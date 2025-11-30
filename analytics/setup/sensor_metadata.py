import yaml
from dataclasses import dataclass
import matplotlib.pyplot as plt

@dataclass
class SensorField:
    plot_title: str
    unit: str
    description: str

class SensorMeta:
    def __init__(self, yaml_file: str):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)['sensors']

        # Dynamically create attributes for each sensor
        for key, val in data.items():
            setattr(self, key, SensorField(**val))

    def list_sensors(self):
        """Return all sensor names available."""
        return [attr for attr in self.__dict__ if isinstance(getattr(self, attr), SensorField)]

    def get_info(self, sensor_name: str):
        """Lookup sensor metadata by name."""
        return getattr(self, sensor_name, None)
    
    def plot_multi(self, df, sensor_names, time_col='master_time'):
        plt.figure(figsize=(10, 5))
        for name in sensor_names:
            info = self.get_info(name)
            if info and name in df.columns:
                plt.plot(df[time_col], df[name], label=info.plot_title)
        plt.xlabel(time_col)
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.show()
