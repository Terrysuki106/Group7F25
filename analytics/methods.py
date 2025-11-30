from models import Driver, Trip, TripMetadata, FileArchive, AnalyticsSummary
from schemas import DriverSchema, TripSchema, TripMetadataSchema, FileArchiveSchema, AnalyticsSummarySchema

def add_entry(session, cfg, metadata, driving_score, trip_details, csv_path, jsn_path):
    """
    Insert driver, trip, metadata, file archive, and analytics summary into DB.
    """
    str_datadump_path = csv_path.parent
    str_metadata_path = jsn_path.parents
    str_datadump_file = csv_path.name
    str_metadata_file = jsn_path.name
    
    # --- Step 1: Driver ---
    driver = session.query(Driver).filter_by(email=metadata.get("email")).first()
    if not driver:
        driver = Driver(
            name=metadata.get("username"),
            email=metadata.get("email"),
            overall_score=None  # will be updated later
        )
        session.add(driver)
        session.commit()
        session.refresh(driver)
   
    # --- Step 2: Trip ---
    new_start = trip_details.get("start")
    new_end = trip_details.get("end")
    # Check for overlapping trips for this driver
    overlap = session.query(Trip).filter(
        Trip.driver_id == driver.driver_id,
        Trip.start_time < new_end,
        Trip.end_time > new_start
    ).first()

    if overlap:
        return {
            "status": "failure",
            "driver": None,
            "trip": None,
            "metadata": None,
            "files": None,
            "summary":  f"Driver {driver.email} already has a trip overlapping {new_start} to {new_end} (existing trip_id={overlap.trip_id})"
        }

    # If no trip exists then
    trip = Trip(
        driver_id=driver.driver_id,
        start_time=trip_details.get("start"),
        end_time=trip_details.get("end"),
        duration_minutes=trip_details.get("duration"),
        distance_km=trip_details.get("distance"),
        average_speed=trip_details.get("v_avg"),
        max_speed=trip_details.get("v_max"),
        accl_max = trip_details.get("a_max"),
        brk_max = trip_details.get("b_max")
    )
    session.add(trip)
    session.commit()
    session.refresh(trip)

    # --- Step 3: Metadata ---
    trip_meta = TripMetadata(
        trip_id=trip.trip_id,
        platform=metadata.get("platform"),
        device_id=metadata.get("device_id"),
        timezone=metadata.get("timezone"),
        sampling_rate=metadata.get("sampling_rate"),
    )
    session.add(trip_meta)

    # --- Step 3: FileArchive ---
    file_entry = FileArchive(
        trip_id=trip.trip_id,
        csv_filename = str(str_datadump_file),
        jsn_filename =str(str_metadata_file),
        file_path = str(str_datadump_path)
    )
    session.add(file_entry)

    # --- Step 4: AnalyticsSummary ---
    summary = AnalyticsSummary(
        trip_id=trip.trip_id,
        overspeed_events=driving_score.get("speed_violations"),
        overspeed_duration_sec=driving_score.get("speed_seconds_above"),
        acceleration_events=driving_score.get("accel_violations"),
        braking_events=driving_score.get("brake_violations"),
        total_penalty=driving_score.get("total_penalty"),
        final_score=driving_score.get("final_score"),
        final_score_percent=driving_score.get("final_score_pct"),
    )
    session.add(summary)

    # --- Commit all ---
    session.commit()

    # --- Return schemas ---
    return {
        "status": "success",
        "driver": DriverSchema.from_orm(driver),
        "trip": TripSchema.from_orm(trip),
        "metadata": TripMetadataSchema.from_orm(trip_meta),
        "files": [FileArchiveSchema.from_orm(f) for f in trip.files],
        "summary": AnalyticsSummarySchema.from_orm(summary),
    }
