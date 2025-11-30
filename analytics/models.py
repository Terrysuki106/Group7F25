from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    overall_score = Column(Float)

    trips = relationship("Trip", back_populates="driver")


class Trip(Base):
    __tablename__ = "trips"
    trip_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    duration_minutes = Column(Integer)
    distance_km = Column(Float)
    average_speed = Column(Float)
    max_speed = Column(Float)

    driver = relationship("Driver", back_populates="trips")
    metadata = relationship("TripMetadata", uselist=False, back_populates="trip")
    files = relationship("FileArchive", back_populates="trip")
    summary = relationship("AnalyticsSummary", uselist=False, back_populates="trip")


class TripMetadata(Base):
    __tablename__ = "trip_metadata"
    metadata_id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), unique=True, nullable=False)
    platform = Column(String)
    device_id = Column(String)
    timezone = Column(String)
    sampling_rate = Column(Integer)

    trip = relationship("Trip", back_populates="metadata")


class FileArchive(Base):
    __tablename__ = "file_archive"
    file_id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), nullable=False)
    original_filename = Column(String)
    file_type = Column(String, CheckConstraint("file_type IN ('CSV','JSON')"))
    file_path = Column(String)

    trip = relationship("Trip", back_populates="files")


class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"
    summary_id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), unique=True, nullable=False)
    average_speed = Column(Float)
    harsh_events = Column(Integer, default=0)
    overspeed_events = Column(Integer, default=0)
    overspeed_duration_sec = Column(Integer, default=0)
    acceleration_events = Column(Integer, default=0)
    braking_events = Column(Integer, default=0)
    total_penalty = Column(Float, default=0)
    final_score = Column(Float)
    final_score_percent = Column(Float)

    trip = relationship("Trip", back_populates="summary")
