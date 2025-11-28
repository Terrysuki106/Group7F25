-- -----------------------------------------------------

CREATE DATABASE IF NOT EXISTS driver_analysis
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE driver_analysis;

-- -----------------------------------------------------
-- DRIVERS TABLE
-- Stores driver information
-- -----------------------------------------------------
CREATE TABLE drivers (
    driver_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- TRIPS TABLE
-- Stores overall trip details (summary per trip)
-- -----------------------------------------------------
CREATE TABLE trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    driver_id INT NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    duration_minutes DECIMAL(10, 2),
    distance_km DECIMAL(10, 2),
    average_speed DECIMAL(10, 2),
    max_speed DECIMAL(10, 2),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- GPS POINTS TABLE
-- Stores all GPS coordinates & driving events for visualization
-- -----------------------------------------------------
CREATE TABLE gps_points (
    point_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    altitude DOUBLE,
    timestamp DATETIME,
    speed DECIMAL(10, 2),
    event_type ENUM('Normal', 'Harsh Brake', 'Harsh Acceleration', 'Overspeed', 'Sharp Turn') DEFAULT 'Normal',
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- FILE ARCHIVE TABLE
-- Stores original uploaded CSV files for auditing
-- -----------------------------------------------------
CREATE TABLE file_archive (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    driver_id INT,
    original_filename VARCHAR(255),
    file_type ENUM('CSV', 'JSON'),
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- ANALYTICS SUMMARY TABLE
-- Stores multi-driver comparison data
-- -----------------------------------------------------
CREATE TABLE analytics_summary (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    driver_id INT,
    total_trips INT,
    total_distance DECIMAL(10, 2),
    average_speed DECIMAL(10, 2),
    harsh_events INT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
