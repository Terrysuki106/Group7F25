import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib.pyplot as plt

import geopandas as gpd
from shapely.geometry import LineString
import contextily as ctx

def plot_route_static(df, lat_col="Location_latitude", lon_col="Location_longitude",
                      output_file="route_map.png", padding=0.05, figsize=(8,6)):
    # Build LineString from lat/lon
    route = LineString(zip(df[lon_col], df[lat_col]))
    gdf = gpd.GeoDataFrame(geometry=[route], crs="EPSG:4326").to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=figsize)
    gdf.plot(ax=ax, color="blue", linewidth=2)

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik) # type: ignore

    # Add padding around bounds
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    x_pad = (bounds[2] - bounds[0]) * padding
    y_pad = (bounds[3] - bounds[1]) * padding
    ax.set_xlim(bounds[0] - x_pad, bounds[2] + x_pad)
    ax.set_ylim(bounds[1] - y_pad, bounds[3] + y_pad)

    ax.set_title("")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])

    return  fig, ax 

def plot_columns(
    df,
    columns,
    kind="line",
    color="blue",
    xlabel="t_rel (s)",
    ylabel=None,
    title=None
):
    """
    Plot one or more columns from a DataFrame against 't_rel' (in seconds).

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    columns : str or list of str
        Column name(s) to plot.
    kind : str, optional
        Type of plot ('line', 'hist', 'bar', etc.), default is 'line'.
    color : str, optional
        Plot color (matplotlib color string), default is 'blue'.
    xlabel : str, optional
        Label for the x-axis. Defaults to 't_rel (s)'.
    ylabel : str, optional
        Label for the y-axis. Defaults to column name.
    title : str, optional
        Title for the plot. Defaults to column name.
    """
    # Normalize input to list
    if isinstance(columns, str):
        columns = [columns]

    # Ensure t_rel exists
    if "t_rel" not in df.columns:
        raise ValueError("DataFrame must contain a 't_rel' column for x-axis.")

    for col in columns:
        if col not in df.columns:
            print(f"Column '{col}' not found in DataFrame.")
            continue

        plt.figure(figsize=(6,4))
        if kind == "line":
            plt.plot(df["t_rel"], df[col], color=color)
        elif kind == "hist":
            plt.hist(df[col], bins=30, color=color)
        elif kind == "bar":
            plt.bar(df["t_rel"], df[col], color=color)
        else:
            # fallback: generic plot
            plt.plot(df["t_rel"], df[col], color=color)

        plt.xlabel(xlabel if xlabel else "t_rel (s)")
        plt.ylabel(ylabel if ylabel else col)
        plt.title(title if title else col)
        plt.tight_layout()
        plt.show()

class SensorPlotter:
    def __init__(self, df, meta):
        """
        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe containing sensor data.
        meta : SensorMeta
            Metadata object with sensor definitions.
        """
        self.df = df
        self.meta = meta

        # Default labels for derived signals (not in YAML)
        self.derived_labels = {
            "acc_forward": ("Forward Acceleration", "m/s²"),
            "acc_brake": ("Braking Acceleration", "m/s²"),
            "acc_lateral": ("Lateral Acceleration", "m/s²"),
            "acc_vertical": ("Vertical Acceleration", "m/s²"),
            "speed_fused": ("Fused Speed", "m/s"),
            "speed_accel": ("Accel-Integrated Speed", "m/s")
        }

    def plot(self, sensor_name: str, time_col: str = 'master_time', **kwargs):
        """
        Plot a single sensor or derived quantity.
        """
        # First check metadata
        info = self.meta.get_info(sensor_name)
        if info:
            title, unit = info.plot_title, info.unit
        elif sensor_name in self.derived_labels:
            title, unit = self.derived_labels[sensor_name]
        else:
            raise ValueError(f"No metadata or derived label found for '{sensor_name}'.")

        if sensor_name not in self.df.columns:
            raise ValueError(f"Column '{sensor_name}' not found in dataframe.")

        plt.figure(figsize=(10, 4))
        plt.plot(self.df[time_col], self.df[sensor_name], **kwargs)
        plt.title(title)
        plt.xlabel(time_col)
        plt.ylabel(unit)
        plt.grid(True)
        plt.show()

    def plot_multi(self, sensor_names, time_col: str = 'master_time'):
        """
        Plot multiple sensors/derived signals together.
        """
        plt.figure(figsize=(10, 5))
        for name in sensor_names:
            info = self.meta.get_info(name)
            if info and name in self.df.columns:
                label = info.plot_title
            elif name in self.derived_labels and name in self.df.columns:
                label = self.derived_labels[name][0]
            else:
                continue
            plt.plot(self.df[time_col], self.df[name], label=label)
        plt.xlabel(time_col)
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.show()

    def describe_sensor(self, sensor_name: str):
        """
        Print metadata or derived description for a sensor.
        """
        info = self.meta.get_info(sensor_name)
        if info:
            print(f"{sensor_name}: {info.description} [{info.unit}]")
        elif sensor_name in self.derived_labels:
            title, unit = self.derived_labels[sensor_name]
            print(f"{sensor_name}: Derived quantity ({title}) [{unit}]")
        else:
            print(f"No metadata or derived info found for {sensor_name}")
