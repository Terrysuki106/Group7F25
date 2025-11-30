from pydantic import BaseModel
from datetime import datetime

class DriverSchema(BaseModel):
    driver_id: int | None
    name: str
    email: str | None
    overall_score: float | None

    class Config:
        orm_mode = True


class TripSchema(BaseModel):
    trip_id: int | None
    driver_id: int
    start_time: datetime
    end_time: datetime | None
    duration_minutes: int | None
    distance_km: float | None
    average_speed: float | None
    max_speed: float | None

    class Config:
        orm_mode = True


class TripMetadataSchema(BaseModel):
    metadata_id: int | None
    trip_id: int
    platform: str | None
    device_id: str | None
    timezone: str | None
    sampling_rate: int | None

    class Config:
        orm_mode = True


class FileArchiveSchema(BaseModel):
    file_id: int | None
    trip_id: int
    original_filename: str | None
    file_type: str | None
    upload_time: datetime | None
    file_path: str | None

    class Config:
        orm_mode = True


class AnalyticsSummarySchema(BaseModel):
    summary_id: int | None
    trip_id: int
    average_speed: float | None
    harsh_events: int | None
    overspeed_events: int | None
    overspeed_duration_sec: int | None
    acceleration_events: int | None
    braking_events: int | None
    total_penalty: float | None
    final_score: float | None
    final_score_percent: float | None

    class Config:
        orm_mode = True