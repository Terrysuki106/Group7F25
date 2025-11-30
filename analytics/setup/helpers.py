from pathlib import Path
from setup.sensor_metadata import SensorMeta
from setup.config import Config

def Initialize_configuration():
    CONFIG_PATH = Path(__file__).resolve().parent.parent / "setup" / "sensors.yaml"
    meta = SensorMeta(str(CONFIG_PATH))
    cfg = Config() #type: ignore
    return cfg, meta
