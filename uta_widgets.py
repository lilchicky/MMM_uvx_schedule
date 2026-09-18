import pandas as pd
import logging

from gtfs_data import GTFSData, GtfsLoadError
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget
)
from config import UTA_TRIP_UPDATE_URL, UTA_VEHICLES_URL
from util import format_name, WorkerThread

class StationInfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setMaximumHeight(200)
        self.setMinimumHeight(200)

        self.route_name = QLabel()
        self.stop_name = QLabel()
        self.headsign_north = QLabel()
        self.headsign_south = QLabel()
        
        self.update_label({})

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.route_name)
        main_layout.addWidget(self.stop_name)
        main_layout.addWidget(self.headsign_north)
        main_layout.addWidget(self.headsign_south)

        self.setLayout(main_layout)

    def update_label(self, new_data: dict):
        self.route_name.setText(f"Route: {new_data.get("route_name")}")
        self.stop_name.setText(f"Stop: {new_data.get("stop_name")}")
        self.headsign_north.setText(f"North Final Stop: {new_data.get("trip_headsign_north")}")
        self.headsign_south.setText(f"South Final Stop: {new_data.get("trip_headsign_south")}")
        
class SearchTripsWidget(QWidget):
    def __init__(self, gd: GTFSData, logger: logging.Logger):
        super().__init__()
        self.gd = gd
        self.logger = logger
        
        self.reload_static_data()
        self.init_ui()
        
    def init_ui(self):
        self.setMaximumWidth(300)
        self.setMinimumWidth(150)
        
        self.station_search = QLineEdit()
        self.route_search = QLineEdit()
        
        self.station_view = QListWidget()
        self.route_view = QListWidget()
        
        self.route_view.addItems(self.all_routes)
        self.route_view.sortItems(Qt.SortOrder.AscendingOrder)
        self.route_view.currentTextChanged.connect(lambda: self.pause_widget(self.populate_stations, self.route_view.currentItem().text()))
        
        self.station_view.addItem("Select a route!")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.route_search)
        main_layout.addWidget(self.route_view)
        main_layout.addWidget(self.station_search)
        main_layout.addWidget(self.station_view)
        
        self.setLayout(main_layout)
        
    def reload_static_data(self):
        self.gd.refresh_static_data()
        
        self.static = self.gd.get_trips_from_name("")
        self.all_routes = [format_name(route) for route in self.static["route_long_name"].unique()]
        self.all_stations = [format_name(station) for station in self.static["stop_name"].unique()]
        
    def populate_stations(self, route: str):
        static = self.static[self.static.route_long_name.str.contains(route, case = False, regex = False)]
        
        self.station_view.clear()
        self.station_view.addItem("Finding stops...")
        
        try:
            current_times = self.gd.get_current(static, UTA_TRIP_UPDATE_URL, UTA_VEHICLES_URL)
            
        except GtfsLoadError as e:
            self.logger.critical("Failed to retrieve current protobuf data.")
            self.logger.exception(e)
            
        current_stops = current_times["stop_name"].unique()
        self.station_view.clear()
        self.station_view.addItems(current_stops)
        self.station_view.sortItems(Qt.SortOrder.AscendingOrder)
        
    def pause_widget(self, func: function, *args: any) -> None:
        thread = WorkerThread(func, *args, parent = self)
        thread.result_ready.connect(lambda: self.setEnabled(True))
        thread.finished.connect(thread.deleteLater)
        thread.start()
        self.setEnabled(False)
            
        