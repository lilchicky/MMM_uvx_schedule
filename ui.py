import os
import sys
import osmnx as ox
import matplotlib.pyplot as plt
import contextily as cx

from dotenv import load_dotenv
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from geopy.geocoders import Nominatim

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
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("UTA Transit Map")
        
        self.main_win = QWidget()
        
        self.button = QPushButton("test")
        self.button.clicked.connect(self.push)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.button)
        
        self.main_win.setLayout(main_layout)
        
        self.setCentralWidget(self.main_win)
        
    def push(self):
        self.count += 1
        self.button.setText(f"{self.count}")

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