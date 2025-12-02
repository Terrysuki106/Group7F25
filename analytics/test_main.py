# Main module
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from setup.config import Initialize_configuration 
from sensor_pipeline.ingestion import ingest_driving_data
from data_processing.data_processing import apply_filter, add_accel_braking, calculate_driving_score, calculate_trip_properties
from data_processing.visualize import plot_route_static
from database import Database
from methods import add_entry

def run_workflow():
    cfg, sensor_metadata = Initialize_configuration()

    SourcePath = Path("C:\\Work\\Moutushi Sarkar\\codes\\Group7F25\\data")

    fused_dataframe, metadata, csv_path, jsn_path = ingest_driving_data(SourcePath / "sensors_testRide.csv" ,cfg)

    str_datadump_path = csv_path.parent
    str_metadata_path = jsn_path.parents
    str_datadump_file = csv_path.name
    str_metadata_file = jsn_path.name
    
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
                                            brk_penalty_rate = 2) 
    
    trip_details = calculate_trip_properties(fused_dataframe)


    # trip_details: contains information about the trip itself
    # driving_score: contains assessment results of the trip
    # fused_dataframe: contains all the sensor log with unified timestamp
    # metadata: contains the information from the sensors
    # str_datadump_path: contains the path string where the ingested data is stored
    # str_metadata_path: contains the path string where the metadata JSON is stored
    # str_datadump_file: contains the filename of the data dump
    # str_metadata_file: contain the filename of the metadata JSON

    print('Metadata content')
    for key, value in metadata.items():
        print(f"{key} = {value}")

    print('Driving score content')
    for key, value in driving_score.items():
        print(f"{key} = {value}")

    print('Driving trip details')
    for key, value in trip_details.items():
        print(f"{key} = {value}")

    print('Initializing DB connection')
    # Initialize DB and create a session
    db = Database(cfg) 
    db.init_db()
    session = db.get_session()

    # Insert everything into the DB
    print('Starting to Insert')

    result = add_entry(session, cfg, metadata, driving_score, trip_details, csv_path, jsn_path)

    # Print schemas returned for clarity
    print("\nInserted records:")
    for key, schema in result.items():
        print(f"{key}: {schema}")
   

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
