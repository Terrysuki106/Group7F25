from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog,QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings

from frontend.main_window import Ui_MainWindow
from setup.config import Initialize_configuration 
from sensor_pipeline.ingestion import ingest_driving_data
from data_processing.data_processing import apply_filter, add_accel_braking, calculate_driving_score, calculate_trip_properties
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from data_processing.visualize import plot_route_static
from database import Database
from methods import add_entry, get_driver_overall_score, get_session
from drive_frontend import import_trip
from datetime import datetime
from typing import Optional
from data_processing.visualize import generate_trip_map
from PySide6.QtGui import QPixmap

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Internal state
        self._originalPixmap = None
        self._fitToViewport = True  # "fit" mode by default

        # Ensure label is centered (Designer should have set this; we enforce in code too)
        self.ui.routeImageLabel.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        # Do NOT enable scaledContents — we scale manually to preserve aspect ratio
        self.ui.routeImageLabel.setScaledContents(False)
        
        #Set up the table
        self.configure_trip_table()
        self.configure_drive_table()
        self.configure_driver_table()
        
        # Wire the button
        self.ui.pushButton.clicked.connect(self.on_run_clicked)

        self.ui.hyperlinkLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.ui.hyperlinkLabel.setOpenExternalLinks(True)
        self.ui.hyperlinkLabel.setEnabled(False)

    def show_route_image(self, image_path: Path):
        # Load original pixmap and store it
        pix = QPixmap(str(image_path))
        if pix.isNull():
            print(f"Failed to load image: {image_path}")
            return

        self._originalPixmap = pix

        if self._fitToViewport:
            self._update_fit_scaled()
        else:
            # Actual-size mode: show full-res and let scrollbars handle overflow
            self.ui.routeImageLabel.setPixmap(self._originalPixmap)
            self.ui.routeImageLabel.adjustSize()

    def _update_fit_scaled(self):
        if self._originalPixmap is None:
            return

        # Size of the scroll area’s viewport (visible area for the label)
        viewport = self.ui.routeScrollArea.viewport().size()


        # Scale with aspect ratio preserved and smooth filtering
        scaled = self._originalPixmap.scaled(
            viewport,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.routeImageLabel.setPixmap(scaled)
        self.ui.routeImageLabel.adjustSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fitToViewport and self._originalPixmap is not None:
            self._update_fit_scaled()

    def configure_driver_table(self):
        tw = self.ui.tableWidget_driver

        tw.verticalHeader().setVisible(False)
        tw.horizontalHeader().setVisible(False)

        tw.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        tw.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tw.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        header = tw.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.ui.tableWidget_trip.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def configure_drive_table(self):
        tw = self.ui.tableWidget_drive

        tw.verticalHeader().setVisible(False)
        tw.horizontalHeader().setVisible(False)

        tw.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        tw.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tw.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        header = tw.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.ui.tableWidget_trip.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def configure_trip_table(self):
        tw = self.ui.tableWidget_trip

        tw.verticalHeader().setVisible(False)
        tw.horizontalHeader().setVisible(False)

        tw.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        tw.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tw.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        header = tw.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ui.tableWidget_trip.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def check_filepath(self, filepath: Path) -> bool:
        json_path = filepath.with_suffix(".json")
        if json_path.exists():
            return True
        else:
            return False
    
    def pretty_datetime(self, dt: Optional[datetime]) -> str:
        """
        Format a datetime object like '23 Mar 2025 @ 8:30 AM'.
        """
        if dt is None: 
            return "N/A"
        return dt.strftime("%d %b %Y @ %#I:%M %p")

    def populate_driver_table(self, metadata: dict, total_score: float | None):
        self.ui.tableWidget_driver.setRowCount(3)
        self.ui.tableWidget_driver.setColumnCount(2)

        self.ui.tableWidget_driver.setItem(0, 0, QTableWidgetItem("Driver"))
        self.ui.tableWidget_driver.setItem(0, 1, QTableWidgetItem(str(metadata.get("username"))))

        self.ui.tableWidget_driver.setItem(1, 0, QTableWidgetItem("Email"))
        self.ui.tableWidget_driver.setItem(1, 1, QTableWidgetItem(str(metadata.get("email"))))

        self.ui.tableWidget_driver.setItem(2, 0, QTableWidgetItem("Total Score"))
        self.ui.tableWidget_driver.setItem(2, 1, QTableWidgetItem(f"{total_score} %"))

        # After content is in, fit column 0 to text
        self.ui.tableWidget_driver.resizeColumnToContents(0)

    def populate_trip_table(self, trip_details: dict):
        self.ui.tableWidget_trip.setRowCount(len(trip_details))
        self.ui.tableWidget_trip.setColumnCount(2)
        """
        "start": trip_start,
        "end": trip_end,
        "duration": round(trip_duration/60,2),
        "distance": round(distance_km,2),
        "v_avg": round(avg_speed,2),
        "v_max": round(max_speed,2),
        "a_max": round(max_acceleration,2),
        "b_max": round(max_braking,2)
        """
        self.ui.tableWidget_trip.setItem(0, 0, QTableWidgetItem("Start Time"))
        self.ui.tableWidget_trip.setItem(0, 1, QTableWidgetItem(self.pretty_datetime(trip_details.get("start"))))

        self.ui.tableWidget_trip.setItem(1, 0, QTableWidgetItem("End Time"))
        self.ui.tableWidget_trip.setItem(1, 1, QTableWidgetItem(self.pretty_datetime(trip_details.get("end"))))

        self.ui.tableWidget_trip.setItem(2, 0, QTableWidgetItem("Duration"))
        self.ui.tableWidget_trip.setItem(2, 1, QTableWidgetItem(f"{trip_details.get('duration')} min"))

        self.ui.tableWidget_trip.setItem(3, 0, QTableWidgetItem("Total Distance"))
        self.ui.tableWidget_trip.setItem(3, 1, QTableWidgetItem(f"{trip_details.get('distance')} km"))

        self.ui.tableWidget_trip.setItem(4, 0, QTableWidgetItem("Average Speed"))
        self.ui.tableWidget_trip.setItem(4, 1, QTableWidgetItem(f"{trip_details.get('v_avg')} km/h"))

        self.ui.tableWidget_trip.setItem(5, 0, QTableWidgetItem("Top Speed"))
        self.ui.tableWidget_trip.setItem(5, 1, QTableWidgetItem(f"{trip_details.get('v_max')} km/h"))

        self.ui.tableWidget_trip.setItem(6, 0, QTableWidgetItem("Max Acceleration"))
        self.ui.tableWidget_trip.setItem(6, 1, QTableWidgetItem(f"{trip_details.get('a_max')} m/s^2"))

        self.ui.tableWidget_trip.setItem(7, 0, QTableWidgetItem("Max Braking"))
        self.ui.tableWidget_trip.setItem(7, 1, QTableWidgetItem(f"{trip_details.get('b_max')} m/s^2"))

        self.ui.tableWidget_trip.resizeColumnToContents(0)

    def populate_drive_table(self, driving_details: dict):
        self.ui.tableWidget_drive.setRowCount(6)
        self.ui.tableWidget_drive.setColumnCount(2)
        """"    
            'total_seconds': float,
            'speed_violations': int,
            'accel_violations': int,
            'brake_violations': int,
            'speed_seconds_above': float,
            'total_penalty': float,
            'final_score': float,
            'final_score_pct': float
        """
        self.ui.tableWidget_drive.setItem(0, 0, QTableWidgetItem("Speed Violations"))
        self.ui.tableWidget_drive.setItem(0, 1, QTableWidgetItem(str(driving_details.get("speed_violations"))))

        self.ui.tableWidget_drive.setItem(1, 0, QTableWidgetItem("Acceleration Violations"))
        self.ui.tableWidget_drive.setItem(1, 1, QTableWidgetItem(str(driving_details.get("accel_violations"))))

        self.ui.tableWidget_drive.setItem(2, 0, QTableWidgetItem("Brake Violations"))
        self.ui.tableWidget_drive.setItem(2, 1, QTableWidgetItem(str(driving_details.get("brake_violations"))))

        self.ui.tableWidget_drive.setItem(3, 0, QTableWidgetItem("Speeding for"))
        self.ui.tableWidget_drive.setItem(3, 1, QTableWidgetItem(f"{driving_details.get('speed_seconds_above')} s"))

        self.ui.tableWidget_drive.setItem(4, 0, QTableWidgetItem("Total Penalty"))
        self.ui.tableWidget_drive.setItem(4, 1, QTableWidgetItem(str(driving_details.get("total_penalty"))))

        self.ui.tableWidget_drive.setItem(5, 0, QTableWidgetItem("Driving Score"))
        self.ui.tableWidget_drive.setItem(5, 1, QTableWidgetItem(f"{driving_details.get('final_score_pct')} %"))
        self.ui.tableWidget_drive.resizeColumnToContents(0)
        
    def on_run_clicked(self):
        # Step 1: Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sensor Source File",
            "",  # start directory
            "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:  # user cancelled
            self.statusBar().showMessage("File selection cancelled")
            return
        
        if not self.check_filepath(Path(file_path)): #csv exists but the json file does not
            self.statusBar().showMessage("Sensor metadata not found! Can't add trip")
            return
        
        # Show status bar with selected file information
        self.statusBar().showMessage(f"Selected file: {file_path}")

        # Import trip information and assess driving
        (cfg, metadata, driving_details, trip_details, csv_path, jsn_path, fused_dataframe) = import_trip(Path(file_path))

        # Write the trip summary to the database
        with get_session(cfg) as session:
            add_entry(session, cfg, metadata, driving_details, trip_details, csv_path, jsn_path)
            total_score = get_driver_overall_score(session, metadata["username"], metadata.get("email"))

        # Display all information in the tables
        self.populate_trip_table(trip_details)
        self.populate_drive_table(driving_details)
        self.populate_driver_table(metadata,total_score)

        fig, ax = plot_route_static(fused_dataframe)
        # Save to file
        output_file = Path(cfg.output_path) / "route_map.png"
        fig.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print("Static route map saved:", output_file)

        # 2) Display in the UI (fit-to-viewport with preserved aspect ratio)
        self.show_route_image(output_file)
        print("Static route map displayed:", output_file)

        # Run your existing map generation
        html_path = generate_trip_map(fused_dataframe, cfg, csv_path)

        uri = Path(html_path).resolve().as_uri()

        self.ui.hyperlinkLabel.setEnabled(True)
        self.ui.hyperlinkLabel.setText(f'<a href="{uri}">Click here for live route map</a>')


if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec()