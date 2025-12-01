from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog
from frontend.main_window import Ui_MainWindow
from setup.helpers import Initialize_configuration 
from sensor_pipeline.ingestion import ingest_driving_data
from data_processing.data_processing import apply_filter, add_accel_braking, calculate_driving_score, calculate_trip_properties
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from data_processing.visualize import plot_route_static
from database import Database
from methods import add_entry
from drive_frontend import add_trip, add_entry_to_db

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Wire the button
        self.ui.pushButton.clicked.connect(self.on_run_clicked)

    def check_filepath(self, filepath: str) -> bool:
        selected_path = Path(filepath)
        json_path = selected_path.with_suffix(".json")
        if json_path.exists():
            return True
        else:
            return False
        
    def populate_table_from_dicts(self, trip_details: dict, driving_details: dict):
        # Combine both dictionaries into one sequence of items
        all_items = list(trip_details.items()) + list(driving_details.items())

        # Configure table: 2 columns (Key, Value), rows = number of items
        self.ui.tableWidget_trip.setRowCount(len(all_items))
        self.ui.tableWidget_trip.setColumnCount(2)
        self.ui.tableWidget_trip.setHorizontalHeaderLabels(["Key", "Value"])

        # Loop through items and populate
        for row, (key, value) in enumerate(all_items):
            self.ui.tableWidget_trip.setItem(row, 0, QTableWidgetItem(str(key)))
            self.ui.tableWidget_trip.setItem(row, 1, QTableWidgetItem(str(value)))


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
        
        if not self.check_filepath(file_path): #csv exists but the json file does not
            self.statusBar().showMessage("Sensor metadata not found! Can't add trip")
            return
        
        (cfg, metadata, driving_details, trip_details, csv_path, jsn_path) = add_trip(file_path)

        self.populate_table_from_dicts(trip_details, driving_details)
        
        self.statusBar().showMessage(f"Selected file: {file_path}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec()
