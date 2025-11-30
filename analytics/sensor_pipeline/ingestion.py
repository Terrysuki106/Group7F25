# Ingestion module
import pandas as pd
import datetime
import json
from pathlib import Path
from setup.config import Config
from sensor_pipeline.time_utils import split_full_data, build_master_timeline, fuse_sensors

def ingest_driving_data(base_filename: str, cfg: Config):  
    print("[Starting] Data Ingestion")
    df, metadata = load_data(base_filename, cfg)
    sensor_streams = split_full_data(df, cfg)
    master_timeline = build_master_timeline(sensor_streams, cfg)
    fused_dataframe = fuse_sensors(sensor_streams, master_timeline,cfg)
    save_output(base_filename, fused_dataframe,metadata, cfg)
    print("[Done] Data Ingestion")

    return (fused_dataframe, metadata)

def load_data(base_filename: str, cfg: Config): # -> Tuple[pd.DataFrame, Dict]:
    """
    Load sensor CSV and metadata JSON based on config paths.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent
    source_path = repo_root / cfg.raw_path
    csv_filename = "sensors_"+ base_filename
    info_filename = "metadata_"+base_filename
    csv_file = (source_path / csv_filename).with_suffix(".csv")
    jsn_file = (source_path /info_filename).with_suffix(".json")
  
    df = pd.read_csv(csv_file)
    with open(jsn_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return df, metadata

def save_output(base_filename:str, df: pd.DataFrame, metadata, cfg: Config):
    """
    Save fused dataset to CSV and metadata to JSON.
    Creates a folder under repo_root named after cfg.output_path.
    """
    # repo root (two levels up from this file)
    repo_root = Path(__file__).resolve().parent.parent

    # Locating target folder
    target_folder = repo_root / cfg.output_path
    target_folder.mkdir(parents=True, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Filenames for the sensor data and the json data
    csv_filename = "sensors_"+ base_filename + "_fused_"+ ts
    info_filename = "metadata_"+ base_filename + "_" + ts    

    # fixed CSV filename inside that folder
    csv_path = (target_folder / csv_filename).with_suffix(".csv")
    jsn_path = (target_folder / info_filename).with_suffix(".json")
    df.to_csv(csv_path, index=False)

    with open(jsn_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    
