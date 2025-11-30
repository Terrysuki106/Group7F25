# Main module
from setup.helpers import Initialize_configuration 
from sensor_pipeline.ingestion import ingest_driving_data
from data_processing.data_processing import rotate_accelerations, estimate_speed, apply_filter, add_accel_braking, calculate_driving_score
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from data_processing.visualize import plot_route_static, plot_columns,SensorPlotter

def run_workflow():
    cfg, sensor_metadata = Initialize_configuration()
    fused_dataframe, metadata = ingest_driving_data("testRide",cfg)
    
    apply_filter(fused_dataframe, 'Location_speed',method="savgol",params = {"window_length": 1001, "polyorder": 3}, overwrite=False)
    
    fused_dataframe = add_accel_braking(fused_dataframe,"Location_speed_smooth")
    
    driving_score = calculate_driving_score(fused_dataframe,
                                            speed_threshold = 40, 
                                            speed_penalty_rate = .5,
                                            accl_col= 'acceleration',
                                            accl_threshold = .5 ,
                                            accl_penalty_rate = 2 ,
                                            brk_col = "braking",
                                            brk_threshold = .5,
                                            brk_penalty_rate = 2) #type: ignore

    for key, value in driving_score.items():
        print(f"{key} = {value}")
    

def run_code():
    repo_root = Path.cwd() / "ingested_data" # current working directory, then go up one
    csv_file = repo_root / "sensors_testRide_fused_20251129_215710.csv"
    # 2. Load CSV
    df = pd.read_csv(csv_file)
    # Generate static route map
    fig, ax = plot_route_static(df,
                    lat_col="Location_latitude",
                    lon_col="Location_longitude",
                    output_file="route_map.png",
                    padding=0.1,
                    figsize=(10,8))
    
    plt.show()

def main_function():
    repo_root = Path.cwd() / "ingested_data" # current working directory, then go up one
    csv_file = repo_root / "sensors_testRide_fused_20251129_215710.csv"
    # 2. Load CSV
    df = pd.read_csv(csv_file)
    
    apply_filter(df, 'Location_speed',method="savgol",params = {"window_length": 1001, "polyorder": 3}, overwrite=False)
    
    df = add_accel_braking(df,"Location_speed_smooth")
    
    driving_score = calculate_driving_score(df,
                                            speed_threshold = 40, 
                                            speed_penalty_rate = .5,
                                            accl_col= 'acceleration',
                                            accl_threshold = .5 ,
                                            accl_penalty_rate = 2 ,
                                            brk_col = "braking",
                                            brk_threshold = .5,
                                            brk_penalty_rate = 2) #type: ignore

    for key, value in driving_score.items():
        print(f"{key} = {value}")

if __name__ == "__main__":
    run_workflow()
