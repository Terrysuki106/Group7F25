from models import Driver, Trip, TripMetadata, FileArchive, AnalyticsSummary
from schemas import DriverSchema, TripSchema, TripMetadataSchema, FileArchiveSchema, AnalyticsSummarySchema

def add_entry(session, cfg, fused_dataframe, metadata, driving_score, trip_details):
    """
    Insert driver, trip, metadata, file archive, and analytics summary into DB.
    """

    # --- Step 1: Driver ---
    driver = session.query(Driver).filter_by(email=metadata.get("email")).first()
    if not driver:
        driver = Driver(
            name=metadata.get("name"),
            email=metadata.get("email"),
            overall_score=None  # will be updated later
        )
        session.add(driver)
        session.commit()
        session.refresh(driver)

    # --- Step 2: Trip ---
    trip = Trip(
        driver_id=driver.driver_id,
        start_time=trip_details["start_time"],
        end_time=trip_details["end_time"],
        duration_minutes=trip_details.get("duration_minutes"),
        distance_km=trip_details.get("distance_km"),
        average_speed=trip_details.get("average_speed"),
        max_speed=trip_details.get("max_speed"),
    )
    session.add(trip)
    session.commit()
    session.refresh(trip)

    # --- Step 3: Metadata ---
    trip_meta = TripMetadata(
        trip_id=trip.trip_id,
        platform=metadata["trip"].get("platform"),
        device_id=metadata["trip"].get("device_id"),
        timezone=metadata["trip"].get("timezone"),
        sampling_rate=metadata["trip"].get("sampling_rate"),
    )
    session.add(trip_meta)

    # --- Step 3: FileArchive ---
    for file in metadata["trip"].get("files", []):
        file_entry = FileArchive(
            trip_id=trip.trip_id,
            original_filename=file["filename"],
            file_type=file["file_type"],
            file_path=str(cfg.raw_path / file["filename"])
        )
        session.add(file_entry)

    # --- Step 4: AnalyticsSummary ---
    summary = AnalyticsSummary(
        trip_id=trip.trip_id,
        average_speed=driving_score.get("average_speed"),
        harsh_events=driving_score.get("harsh_events"),
        overspeed_events=driving_score.get("overspeed_events"),
        overspeed_duration_sec=driving_score.get("overspeed_duration_sec"),
        acceleration_events=driving_score.get("acceleration_events"),
        braking_events=driving_score.get("braking_events"),
        total_penalty=driving_score.get("total_penalty"),
        final_score=driving_score.get("final_score"),
        final_score_percent=driving_score.get("final_score_percent"),
    )
    session.add(summary)

    # --- Commit all ---
    session.commit()

    # --- Return schemas for clarity (academic explanation) ---
    return {
        "driver": DriverSchema.from_orm(driver),
        "trip": TripSchema.from_orm(trip),
        "metadata": TripMetadataSchema.from_orm(trip_meta),
        "files": [FileArchiveSchema.from_orm(f) for f in trip.files],
        "summary": AnalyticsSummarySchema.from_orm(summary),
    }
