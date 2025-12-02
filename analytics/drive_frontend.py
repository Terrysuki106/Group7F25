import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Callable
from sensor_pipeline.ingestion import ingest_driving_data
from data_processing.data_processing import apply_filter, add_accel_braking, calculate_driving_score, calculate_trip_properties
from data_processing.visualize import plot_route_static
from database import Database
from methods import add_entry
from setup.config import Config, Initialize_configuration


def import_trip(source_path: Path, logger: Callable[[str],None] | None = None):
    cfg, sensor_info = Initialize_configuration()
    fused_dataframe, metadata, csv_path, jsn_path = ingest_driving_data(source_path,cfg) # type: ignore
    
    str_datadump_path = csv_path.parent
    str_metadata_path = jsn_path.parents
    str_datadump_file = csv_path.name
    str_metadata_file = jsn_path.name

    if logger:
        logger("Data ingested: {str_datadump_file} and {str_metadata_file}")

    apply_filter(fused_dataframe, 'Location_speed',method="savgol",params = {"window_length": 1001, "polyorder": 3}, overwrite=False)

    fused_dataframe = add_accel_braking(fused_dataframe,"Location_speed_smooth")
    
    trip_details = calculate_trip_properties(fused_dataframe)
    
    if logger:
        logger("Trip details calculated")

    driving_details = calculate_driving_score(fused_dataframe,
                                            speed_threshold = 40, 
                                            speed_penalty_rate = .5,
                                            accl_col= 'acceleration',
                                            accl_threshold = .5 ,
                                            accl_penalty_rate = 2 ,
                                            brk_col = "braking",
                                            brk_threshold = .5,
                                            brk_penalty_rate = 2) 
    if logger:
        logger("Driving details calculated")

    
    return (cfg, metadata, driving_details, trip_details, csv_path, jsn_path, fused_dataframe)




