# Time_utils module
from typing import Dict
import pandas as pd
from setup.config import Config 

def split_sensors(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Split a wide-form dataframe into per-sensor dataframes.
    Keys are sensor names (prefix before first underscore).
    """
    grouped_cols: Dict[str, list[str]] = {}

    # group columns by prefix
    for col in df.columns:
        sensor, _, field = col.partition("_")
        grouped_cols.setdefault(sensor, []).append(col)

    sensor_frames: Dict[str, pd.DataFrame] = {}

    # build per-sensor dataframes
    for sensor, cols in grouped_cols.items():
        sdf = df[cols].copy()
        # normalize column names (drop sensor prefix)
        sdf.columns = [c.split("_", 1)[1] for c in cols]
        sensor_frames[sensor] = sdf

    return sensor_frames


def prepare_time(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """
    Convert nanosecond epoch timestamps to human-readable and relative seconds.
    Expects a 'time' column in the dataframe.
    """
    if "time" not in df.columns:
        raise ValueError("Expected a 'time' column in dataframe")

    # absolute timestamp
    df["timestamp"] = (
        pd.to_datetime(df["time"], unit="ns")
        .dt.tz_localize("UTC")
        .dt.tz_convert(cfg.timezone)
        .dt.round("ms")
    )

    # relative seconds since start
    df["t_rel"] = ((df["time"] - df["time"].iloc[0]) / 1e9).round(3)

    return df


def split_full_data(df: pd.DataFrame, cfg: Config) -> Dict[str, pd.DataFrame]:
    """
    Full ingestion pipeline:
    - split into per-sensor frames
    - add timestamp and relative time
    """
    sensor_frames = split_sensors(df)
    for sensor, sdf in sensor_frames.items():
        sensor_frames[sensor] = prepare_time(sdf, cfg)
    return sensor_frames

def build_master_timeline(streams: Dict[str, pd.DataFrame], cfg: Config) -> pd.DataFrame:
    """
    Build a master timeline across all sensor streams.
    Returns only two columns: master_time and t_rel.
    """
    starts, ends = [], []
    for sensor, df in streams.items():
        if "timestamp" not in df.columns:
            raise ValueError(f"Stream {sensor} missing 'timestamp' column")
        ts = df["timestamp"].dropna().sort_values()
        if ts.empty:
            print(f"Skipping sensor {sensor}: No valid timestamp")
            continue
        starts.append(ts.iloc[0])
        ends.append(ts.iloc[-1])

    t_start = max(starts)
    t_end = min(ends)
    if t_start >= t_end:
        raise ValueError(f"No overlap between streams: start={t_start}, end={t_end}")

    freq_hz = cfg.sampling_rate
    step_ns = int(1e9 / freq_hz)

    master_index = pd.date_range(start=t_start, end=t_end, freq=pd.to_timedelta(step_ns, unit="ns"))

    master_df = pd.DataFrame({
        "master_time": master_index,
        "t_rel": (master_index - master_index[0]).total_seconds()
    })

    return master_df

def fuse_sensors(streams: Dict[str, pd.DataFrame], master_df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """
    Fuse all sensor streams onto the master timeline.
    For each sensor and each quantity column, interpolate values
    onto master_time and append as new columns.
    """
    fused = master_df.copy()

    def get_round_digits(sensor: str) -> int:
        """Return rounding precision based on sensor type."""
        return cfg.location_digits if sensor == "Location" else cfg.normal_digits

    for sensor, df in streams.items():
        # Ensure sorted and unique timestamps
        df = df.sort_values("timestamp")
        df = df[~df["timestamp"].duplicated(keep="first")]

        # Select only meaningful columns (exclude metadata and elapsed time)
        sensor_cols = [
            col for col in df.columns
            if col not in ("time", "timestamp", "t_rel") and not col.endswith("seconds_elapsed")
        ]

        for col in sensor_cols:
            round_digits = get_round_digits(sensor)

            # Align sensor values to master timeline
            aligned = (
                df.set_index("timestamp")[col]
                .reindex(fused["master_time"])
                .interpolate(method="time")
                .round(round_digits)
            )
            aligned = aligned.ffill().bfill()

            # Add to fused dataframe with sensor prefix
            fused[f"{sensor}_{col}"] = aligned.to_numpy()

    return fused

