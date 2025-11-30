import numpy as np
from scipy.signal import butter, filtfilt, medfilt, savgol_filter
import pandas as pd
import numpy as np
from datetime import datetime
from geopy.distance import geodesic

# --- 1. Quaternion to Rotation Matrix ---
def quaternion_to_rotation_matrix(qx, qy, qz, qw):
    """
    Convert quaternion (qx, qy, qz, qw) to a 3x3 rotation matrix.
    """
    # Normalize quaternion
    norm = np.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm

    # Rotation matrix
    R = np.array([
        [1 - 2*(qy**2 + qz**2),     2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw)],
        [2*(qx*qy + qz*qw),         1 - 2*(qx**2 + qz**2), 2*(qy*qz - qx*qw)],
        [2*(qx*qz - qy*qw),         2*(qy*qz + qx*qw),     1 - 2*(qx**2 + qy**2)]
    ])
    return R

# --- 2. Rotate accelerations into vehicle frame ---
def rotate_accelerations(df):
    rotated = []
    for i in range(len(df)):
        R = quaternion_to_rotation_matrix(df['Orientation_qx'].iloc[i],
                                          df['Orientation_qy'].iloc[i],
                                          df['Orientation_qz'].iloc[i],
                                          df['Orientation_qw'].iloc[i])
        acc = np.array([df['Accelerometer_x'].iloc[i],
                        df['Accelerometer_y'].iloc[i],
                        df['Accelerometer_z'].iloc[i]])
        rotated.append(R @ acc)
    rotated = np.array(rotated)
    df['acc_forward'] = rotated[:,0]   # forward axis
    df['acc_lateral'] = rotated[:,1]   # lateral axis
    df['acc_vertical'] = rotated[:,2]  # vertical axis
    df['acc_brake'] = df['acc_forward'].clip(upper=0)  # braking only
    return df

# --- 3. Speed estimation with fusion ---
def estimate_speed(df, dt=0.1, alpha=0.8):
    """
    Fuse GPS speed with integrated forward acceleration.
    dt: sampling interval (s)
    alpha: blending factor (0=GPS only, 1=Accel only)
    """
    # Integrate forward acceleration
    accel_speed = [df['Location_speed'].iloc[0]]  # start from GPS
    for i in range(1, len(df)):
        v = accel_speed[-1] + df['acc_forward'].iloc[i] * dt
        accel_speed.append(v)
    accel_speed = np.array(accel_speed)

    # Blend GPS and accel-based speed
    gps_speed = df['Location_speed'].to_numpy()
    fused_speed = alpha * accel_speed + (1-alpha) * gps_speed

    df['speed_accel'] = accel_speed
    df['speed_fused'] = fused_speed
    return df

def apply_filter(df, column, method, params=None, overwrite=False):
    """
    Apply a filter to a DataFrame column.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    column : str
        Column name to filter.
    method : str
        Filter method. Options: 'moving_avg', 'rolling_median',
        'zscore', 'minmax', 'clip', 'savgol', 'lowpass'.
    params : dict or None
        Parameters for the filter method.
    overwrite : bool
        If True, overwrite the column (saving raw_<colname>).
        If False, create a new column <colname>_<method>.
    
    Returns
    -------
    df : pandas.DataFrame
        DataFrame with filtered column(s).
    """
    if params is None:
        params = {}
    
    series = df[column].copy()
    result = None
    
    # --- Filters ---
    if method == "moving_avg":
        window = params.get("window", 3)
        result = series.rolling(window, min_periods=1).mean()
    
    elif method == "rolling_median":
        window = params.get("window", 3)
        result = series.rolling(window, min_periods=1).median()
    
    elif method == "zscore":
        threshold = params.get("threshold", 3)
        z = (series - series.mean()) / series.std(ddof=0)
        result = series.where(abs(z) < threshold, np.nan)
    
    elif method == "minmax":
        min_val, max_val = series.min(), series.max()
        result = (series - min_val) / (max_val - min_val)
    
    elif method == "clip":
        lower = params.get("lower", series.min())
        upper = params.get("upper", series.max())
        result = series.clip(lower, upper)
    
    elif method == "savgol":
        # Savitzky–Golay smoothing
        window = params.get("window_length", 5)
        poly = params.get("polyorder", 2)
        # Ensure window length is odd and <= len(series)
        if window % 2 == 0:
            window += 1
        if window > len(series):
            window = len(series) - (len(series) % 2 == 0)
        result = savgol_filter(series, window_length=window, polyorder=poly)
    
    else:
        raise ValueError(f"Unknown filter method: {method}")
    
    # --- Overwrite or add new column ---
    if overwrite:
        df[f"raw_{column}"] = series
        df[column] = result
    else:
        df[f"{column}_smooth"] = result
    
    return df

def add_accel_braking(df, column_name: str):
    # Ensure sorted by time
    df = df.sort_values("t_rel").reset_index(drop=True)
    
    # Compute acceleration: Δv / Δt
    df["acceleration"] = df[column_name].diff() / df["t_rel"].diff()
    
    # Replace NaN in first row with 0
    df["acceleration"] = df["acceleration"].fillna(0)
    
    # Braking = negative acceleration only (else 0)
    df["braking"] = df["acceleration"].apply(lambda x: x if x < 0 else 0)

    df["acceleration"] = df["acceleration"].apply(lambda x: x if x > 0 else 0)
    
    return df

def get_speed_violations(df: pd.DataFrame, threshold: float, penalty_rate: float):
    """
    Calculate speed violations and penalties.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns:
        - 't_rel' (time in seconds, relative or absolute)
        - 'Location_speed_smooth' (speed in m/s)
    threshold : float
        Speed threshold in m/s.
    penalty_rate : float
        Penalty rate per second above threshold.

    Returns
    -------
    dict
        {
            'num_violations': int,   # number of distinct violation events
            'total_penalty': float   # total penalty accrued
        }
    """
    # Boolean mask for speeds above threshold
    above_threshold = df['Location_speed_smooth'] > threshold

    # Count distinct violation events (continuous stretches above threshold)
    # A violation starts when above_threshold changes from False → True
    violation_starts = (above_threshold & ~above_threshold.shift(fill_value=False)).sum()

    # Calculate total penalty: sum of seconds spent above threshold * penalty_rate
    # Assuming t_rel is in seconds and consecutive (1s increments)
    total_seconds_above = above_threshold.sum()
    total_penalty = total_seconds_above * penalty_rate

    return {
        'num_violations': int(violation_starts),
        'total_penalty': float(total_penalty)
    }

def get_harsh_driving_violations(
    df: pd.DataFrame,
    quantity_col: str,
    threshold: float,
    penalty_rate: float
):
    """
    Calculate harsh driving violations and penalties (per event).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a column for the quantity of interest (e.g., acceleration).
    quantity_col : str
        Name of the column in df to check (e.g., 'acceleration').
    threshold : float
        Threshold value for violation (e.g., 0.7 m/s^2).
    penalty_rate : float
        Penalty applied per violation event.

    Returns
    -------
    dict
        {
            'num_violations': int,   # number of distinct violation events
            'total_penalty': float   # total penalty accrued
        }
    """
    # Boolean mask for values above threshold
    above_threshold = df[quantity_col] > threshold

    # Count distinct violation events (continuous stretches above threshold)
    violation_starts = (above_threshold & ~above_threshold.shift(fill_value=False)).sum()

    # Penalty is applied per event, not per second
    total_penalty = violation_starts * penalty_rate

    return {
        'num_violations': int(violation_starts),
        'total_penalty': float(total_penalty)
    }

def calculate_driving_score(
    df: pd.DataFrame,
    speed_threshold: float,
    speed_penalty_rate: float,
    accl_col: str,
    accl_threshold: float,
    accl_penalty_rate: float,
    brk_col: str,
    brk_threshold: float,
    brk_penalty_rate: float
):
    """
    Calculate an overall driving score with time-aware penalties.

    Assumptions:
    - t_rel is in seconds (monotonic, may be irregular).
    - Penalty for speed is per second above threshold (integrates actual time).
    - Acceleration/braking penalties are per event (continuous stretches).

    Returns
    -------
    dict
        {
            'total_seconds': float,
            'speed_violations': int,
            'accel_violations': int,
            'brake_violations': int,
            'speed_seconds_above': float,
            'total_penalty': float,
            'final_score': float,
            'final_score_pct': float
        }
    """
    if df.empty:
        return {
            'total_seconds': 0.0,
            'speed_violations': 0,
            'accel_violations': 0,
            'brake_violations': 0,
            'speed_seconds_above': 0.0,
            'total_penalty': 0.0,
            'final_score': 0.0,
            'final_score_pct': 0.0
        }

    # Ensure t_rel is numeric and sorted
    dfx = df[['t_rel', 'Location_speed_smooth', accl_col, brk_col]].dropna(subset=['t_rel']).copy()
    dfx = dfx.sort_values('t_rel')

    # Time deltas between samples (last sample contributes zero delta)
    dt = dfx['t_rel'].diff().fillna(0).astype(float)
    # Guard against negative or absurd deltas
    dt = dt.clip(lower=0)

    # Total elapsed time (seconds)
    total_seconds = float((dfx['t_rel'].iloc[-1] - dfx['t_rel'].iloc[0]) if len(dfx) > 1 else 0.0)

    # Base score: +1 per second of driving
    base_score = total_seconds

    # Speed mask and time above threshold
    above_speed = dfx['Location_speed_smooth'] > speed_threshold
    speed_seconds_above = float((dt * above_speed.astype(float)).sum())
    speed_violations = int((above_speed & ~above_speed.shift(fill_value=False)).sum())
    speed_penalty = speed_seconds_above * float(speed_penalty_rate)

    # Acceleration events (per-event penalty)
    above_accl = dfx[accl_col] > accl_threshold
    accel_violations = int((above_accl & ~above_accl.shift(fill_value=False)).sum())
    accel_penalty = accel_violations * float(accl_penalty_rate)

    # Braking events (per-event penalty)
    above_brk = abs(dfx[brk_col]) > brk_threshold
    brake_violations = int((above_brk & ~above_brk.shift(fill_value=False)).sum())
    brake_penalty = brake_violations * float(brk_penalty_rate)

    # Totals and final score
    total_penalty = float(speed_penalty + accel_penalty + brake_penalty)
    final_score = float(base_score - total_penalty)

    # Normalize to percentage of theoretical maximum (total_seconds)
    final_score_pct = round(float(0.0 if total_seconds <= 0 else max(0.0, (final_score / total_seconds) * 100)),2)

    return {
        'total_seconds': total_seconds,
        'speed_violations': speed_violations,
        'accel_violations': accel_violations,
        'brake_violations': brake_violations,
        'speed_seconds_above': speed_seconds_above,
        'total_penalty': total_penalty,
        'final_score': final_score,
        'final_score_pct': final_score_pct
    }

def calculate_trip_properties(df: pd.DataFrame) -> dict:
    """
    Parameters:
        df (pd.DataFrame): DataFrame containing sensor data with columns like
                           master_time, t_rel, Location_speed, Location_latitude,
                           Location_longitude, acceleration, braking.
    
    """
    
    # --- Trip Start and End ---
    trip_start = pd.to_datetime(df['master_time'].iloc[0])
    trip_end = pd.to_datetime(df['master_time'].iloc[-1])
    trip_duration = df['t_rel'].iloc[-1] - df['t_rel'].iloc[0]  # seconds
    
    # --- Trip Distance (using haversine via geopy) ---
    coords = list(zip(df['Location_latitude'], df['Location_longitude']))
    distance_km = 0.0
    for i in range(1, len(coords)):
        if not (np.isnan(coords[i][0]) or np.isnan(coords[i][1]) or 
                np.isnan(coords[i-1][0]) or np.isnan(coords[i-1][1])):
            distance_km += geodesic(coords[i-1], coords[i]).km
    
    # --- Speed Metrics ---
    speeds = df['Location_speed'].clip(lower=0)  # remove invalid negatives
    avg_speed = speeds.mean() * 3.6  # convert m/s → km/h
    max_speed = speeds.max() * 3.6   # km/h
    
    # --- Acceleration / Braking ---
    max_acceleration = df['acceleration'].max() if 'acceleration' in df else np.nan
    max_braking = df['braking'].min() if 'braking' in df else np.nan  # braking usually negative
    
    # --- Results ---
    return {
        "start": trip_start,
        "end": trip_end,
        "duration": trip_duration/3600,
        "distance": distance_km,
        "v_avg": avg_speed,
        "v_max": max_speed,
        "a_max": max_acceleration,
        "b_bax": max_braking
    }
