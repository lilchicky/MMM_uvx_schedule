import os
import sys
import osmnx as ox
import matplotlib.pyplot as plt
import contextily as cx

from datetime import datetime, timezone
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal
from geopy.geocoders import Nominatim

from gtfs_data import GTFSData, GtfsLoadError
from uta_logger import UTALogger
from config import (
    UTA_GTFS_STATIC_URL,
    UTA_TRIP_UPDATE_URL,
    UTA_VEHICLES_URL
)
from util import (
    get_next_departures,
    build_departure_string
)

'''
OSMnx paper citation:
Boeing, G. (2025). Modeling and Analyzing Urban Networks and Amenities with OSMnx. Geographical Analysis 57 (4), 567-577. doi:10.1111/gean.70009
'''

load_dotenv()
CARTO_KEY = os.getenv("CARTO_KEY")

class WorkerThread(QThread):
    result_ready = pyqtSignal(str)
    
    def __init__(self, func, *args, parent = None):
        super().__init__(parent)
        self.func = func
        self.args = args
    
    def run(self):
        result = self.func(*self.args)
        self.result_ready.emit(result)

class UTAMapUI(QMainWindow):
    
    LOGGER = UTALogger("ui", "ui").logger
    
    def __init__(self):
        super().__init__()
        self.geocoder = Nominatim(user_agent = "uta_transit_map")
        
        self.count = 0
        self.gd = GTFSData.from_url(UTA_GTFS_STATIC_URL)
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("UTA Transit Map")
        self.setGeometry(100, 100, 1200, 800)
        
        self.main_win = QWidget()
        
        self.refresh = QPushButton("Refresh Static Data")
        self.refresh.clicked.connect(lambda: self.start_input_thread_work(self.refresh, self.gd.refresh_static_data))
        
        self.button = QPushButton("test")
        self.button.clicked.connect(self.push)
        
        self.label = QLabel("Nothing Yet")
        
        main_layout = QGridLayout()
        main_layout.addWidget(self.button, 0, 1)
        main_layout.addWidget(self.label, 1, 0)
        main_layout.addWidget(self.refresh, 0, 2)
        
        self.main_win.setLayout(main_layout)
        
        self.setCentralWidget(self.main_win)
        
    def start_input_thread_work(self, button: QPushButton, func: function, *args: any) -> None:
        thread = WorkerThread(func, *args, parent = self)
        thread.result_ready.connect(lambda: button.setEnabled(True))
        thread.finished.connect(thread.deleteLater)
        thread.start()
        button.setEnabled(False)
        
    def push(self):
        self.count += 1
        self.button.setText(f"{self.count}")
        
        today = datetime.now(timezone.utc).astimezone(self.gd.agency_tzinfo)
        search = self.gd.get_trips_from_name("frontrunner")
        
        if search is not None:
            try:
                current_times = self.gd.get_current(search, UTA_TRIP_UPDATE_URL, UTA_VEHICLES_URL)
            except GtfsLoadError as e:
                UTAMapUI.LOGGER.critical("Failed to retrieve current protobuf data.")
                UTAMapUI.exception(e)
    
            dirs = get_next_departures(
                current_times, today, 
                UTAMapUI.LOGGER, 
                station = "vineyard", 
                num_routes = 3
            )
    
            for _, departures in dirs.items():
                self.label.setText(departures.get("route_name"))
                break

if __name__ == '__main__':
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