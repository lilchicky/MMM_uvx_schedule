import os
import sys
import osmnx as ox
import matplotlib.pyplot as plt
import contextily as cx
import pandas as pd

from datetime import datetime, timezone
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QCompleter
)
from PyQt6.QtCore import Qt
from geopy.geocoders import Nominatim

from gtfs_data import GTFSData, GtfsLoadError
from uta_widgets import StationInfoWidget, SearchTripsWidget
from config import (
    UTA_GTFS_STATIC_URL,
    UTA_TRIP_UPDATE_URL,
    UTA_VEHICLES_URL,
    LOGGER
)
from util import (
    get_next_departures,
    format_name,
    WorkerThread
)

'''
OSMnx paper citation:
Boeing, G. (2025). Modeling and Analyzing Urban Networks and Amenities with OSMnx. Geographical Analysis 57 (4), 567-577. doi:10.1111/gean.70009
'''

load_dotenv()
CARTO_KEY = os.getenv("CARTO_KEY")

class UTAMapUI(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.geocoder = Nominatim(user_agent = "uta_transit_map")
        
        self.count = 0
        self.gd = GTFSData.from_url(UTA_GTFS_STATIC_URL)
        
        self.search_routes = self.gd.routes["route_long_name"].apply(lambda x: format_name(x)).unique()
        self.search_stops = self.gd.stops["stop_name"].apply(lambda x: format_name(x)).unique()
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("UTA Transit Map")
        self.setGeometry(100, 100, 1200, 800)
        
        self.main_pane = QWidget()
        
        self.search_pane = QWidget()
        self.search_pane.setFixedHeight(40)
        
        self.info_pane = QWidget()
        
        self.search_pane.setLayout(self.build_search_bar())
        self.info_pane.setLayout(self.build_info_pane())
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.search_pane)
        main_layout.addWidget(self.info_pane)
        
        self.main_pane.setLayout(main_layout)
        
        self.setCentralWidget(self.main_pane)
        
    def build_search_bar(self):
        
        def get_completer(database: list):
            completer = QCompleter(database, self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            return completer
            
        self.route_search = QLineEdit()
        self.station_search = QLineEdit()
        
        self.submit_search = QPushButton("Search")
        self.submit_search.setMaximumSize(100, 25)
        self.submit_search.setMinimumSize(80, 25)
        
        self.route_search.setCompleter(get_completer(self.search_routes))
        self.station_search.setCompleter(get_completer(self.search_stops))

        # Interaction connections
        self.route_search.returnPressed.connect(lambda: self.push(self.route_search.text()))
        self.station_search.returnPressed.connect(lambda: self.push(self.station_search.text()))
        self.submit_search.clicked.connect(lambda: self.search(self.route_search.text(), self.station_search.text()))
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.route_search)
        search_layout.addWidget(self.station_search)
        search_layout.addWidget(self.submit_search)
        
        return search_layout
    
    def build_info_pane(self):
        self.route_data = StationInfoWidget()
        self.test_search = SearchTripsWidget(self.gd)
        
        self.refresh = QPushButton("Refresh Static Data")
        self.refresh.clicked.connect(lambda: self.start_input_thread_work(self.refresh, self.test_search.refresh))
        
        self.button = QPushButton("test")
        self.button.clicked.connect(lambda: self.start_input_thread_work(self.button, self.push))
        
        info_layout = QGridLayout()
        info_layout.addWidget(self.button, 0, 1)
        info_layout.addWidget(self.route_data, 1, 0)
        info_layout.addWidget(self.refresh, 0, 2)
        info_layout.addWidget(self.test_search, 1, 1)
        
        return info_layout
        
    def start_input_thread_work(self, button: QPushButton, func: function, *args: any) -> None:
        thread = WorkerThread(func, *args, parent = self)
        thread.result_ready.connect(lambda: button.setEnabled(True))
        thread.finished.connect(thread.deleteLater)
        thread.start()
        button.setEnabled(False)
        
    def refresh_static_data(self):
        self.gd.refresh_static_data()
        self.search_routes = self.gd.routes["route_long_name"].apply(lambda x: format_name(x)).unique()
        self.search_stops = self.gd.stops["stop_name"].apply(lambda x: format_name(x)).unique()
        
    def push(self):
        self.count += 1
        self.button.setText(f"{self.count}")
            
    def search(self, route, station):
        search = self.gd.get_trips_from_name(route)
                
        if search is not None:
            today = datetime.now(timezone.utc).astimezone(self.gd.agency_tzinfo)
            
            try:
                current_times = self.gd.get_current(search, UTA_TRIP_UPDATE_URL, UTA_VEHICLES_URL)
            except GtfsLoadError as e:
                LOGGER.critical("Failed to retrieve current protobuf data.")
                LOGGER.exception(e)
    
            dirs = get_next_departures(
                current_times, today,
                station = station, 
                num_routes = 3
            )
    
            for _, departures in dirs.items():
                self.route_data.update_label(departures)
                break

def ui():
    app = QApplication(sys.argv)
    window = UTAMapUI()
    window.show()
    sys.exit(app.exec())

def test_place(place: str):
    area = ox.geocode_to_gdf(place)
    area = area.to_crs(epsg = 3857)
    fig, ax = plt.subplots(figsize = (12, 12))
    
    area.plot(
        ax = ax,
        facecolor = "none",
        edgecolor = "red",
        linewidth = 2
    )
    
    cx.add_basemap(
        ax,
        source = "https://basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png?key=" + CARTO_KEY,
        attribution = "© OpenStreetMap contributors, © CartoDB"
    )
    
    ax.set_axis_off()
    plt.show()