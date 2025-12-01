from setup.helpers import Initialize_configuration 
from sensor_pipeline.ingestion import ingest_driving_data
from data_processing.data_processing import apply_filter, add_accel_braking, calculate_driving_score, calculate_trip_properties
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from data_processing.visualize import plot_route_static
from database import Database
from methods import add_entry
from setup.config import Config

def add_trip(source_path: Path):
    cfg, sensor_metadata = Initialize_configuration()
    fused_dataframe, metadata, csv_path, jsn_path = ingest_driving_data(source_path,cfg)

    str_datadump_path = csv_path.parent
    str_metadata_path = jsn_path.parents
    str_datadump_file = csv_path.name
    str_metadata_file = jsn_path.name

    apply_filter(fused_dataframe, 'Location_speed',method="savgol",params = {"window_length": 1001, "polyorder": 3}, overwrite=False)

    fused_dataframe = add_accel_braking(fused_dataframe,"Location_speed_smooth")
    
    trip_details = calculate_trip_properties(fused_dataframe)

    driving_details = calculate_driving_score(fused_dataframe,
                                            speed_threshold = 40, 
                                            speed_penalty_rate = .5,
                                            accl_col= 'acceleration',
                                            accl_threshold = .5 ,
                                            accl_penalty_rate = 2 ,
                                            brk_col = "braking",
                                            brk_threshold = .5,
                                            brk_penalty_rate = 2) 
    
    return (cfg, metadata, driving_details, trip_details, csv_path, jsn_path)

def add_entry_to_db(cfg: Config, metadata, driving_score, trip_details, csv_path, jsn_path):
    # Initialize DB and create a session
    db = Database(cfg)
    db.init_db()
    session = db.get_session()
    result = add_entry(session, cfg, metadata, driving_score, trip_details, csv_path, jsn_path)
    return result
