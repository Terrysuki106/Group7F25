# Group7F25

# Driving Analytics Workflow 🚗📊

## Overview
This project implements a **driving data ingestion and analytics pipeline**.  
It processes raw sensor logs, applies filters, calculates driving scores, extracts trip properties, and persists results into a relational database using SQLAlchemy ORM.

The workflow is designed to be **modular, reproducible, and academically annotated**, making it suitable for both technical demonstration and teaching purposes.

---

## Workflow Steps

1. **Configuration & Ingestion**
   - Initialize system configuration (`Initialize_configuration`)
   - Ingest driving data (`ingest_driving_data`) → returns fused dataframe, metadata, and file paths

2. **Preprocessing**
   - Apply Savitzky–Golay filter to smooth speed data (`apply_filter`)
   - Add acceleration & braking signals (`add_accel_braking`)

3. **Analytics**
   - Calculate driving score (`calculate_driving_score`)
     - Speed violations
     - Acceleration/braking violations
     - Penalty scoring
   - Calculate trip properties (`calculate_trip_properties`)
     - Start/end time
     - Duration
     - Distance
     - Average/max speed
     - Max acceleration/braking

4. **Database Persistence**
   - Initialize database connection (`Database`)
   - Insert records via `add_entry`:
     - **Driver** (unique by email)
     - **Trip** (with overlap detection logic)
     - **TripMetadata**
     - **FileArchive**
     - **AnalyticsSummary**

5. **Validation**
   - Return Pydantic schemas (`DriverSchema`, `TripSchema`, etc.) for inserted records
   - Print results for clarity

---

## Example Run

```bash
python main.py
