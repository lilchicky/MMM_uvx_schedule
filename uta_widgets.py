import pandas as pd
import logging

from gtfs_data import GTFSData, GtfsLoadError
from PyQt6.QtCore import Qt, QMimeData
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
        
        self.last_route_search = ""
        self.last_station_search = ""
        
        self.init_ui()
        self.refresh()
        
    def init_ui(self):
        self.setMaximumWidth(300)
        self.setMinimumWidth(150)
        
        self.station_search = QLineEdit()
        self.route_search = QLineEdit()
        
        self.route_search.setPlaceholderText("Search a route...")
        
        self.station_view = QListWidget()
        self.route_view = QListWidget()
        
        self.route_view.itemClicked.connect(lambda: self.pause_widget(self.populate_stations, self.route_view.currentItem().text()))
        
        self.route_search.textChanged.connect(lambda x: self.update_list(self.route_view, self.all_routes, x, self.last_route_search))
        self.station_search.textChanged.connect(lambda x: self.update_list(self.station_view, self.current_stops, x, self.last_station_search))
        
        self.station_view.addItem("Select a route!")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.route_search)
        main_layout.addWidget(self.route_view)
        main_layout.addWidget(self.station_search)
        main_layout.addWidget(self.station_view)
        
        self.setLayout(main_layout)
        
    def refresh(self):
        self.gd.refresh_static_data()
        
        self.static = self.gd.get_trips_from_name("")
        self.all_routes = [format_name(route) for route in self.static["route_long_name"].unique()]
        self.current_stops = []
        
        self.route_view.clear()
        self.update_list(self.route_view, self.all_routes, self.route_search.text(), self.last_route_search)
        
        self.station_view.clear()
        
    def populate_stations(self, route: str):
        static = self.static[self.static.route_long_name.str.contains(route, case = False, regex = False)]
        
        self.station_view.clear()
        self.station_view.addItem("Finding stops...")
        
        try:
            current_times = self.gd.get_current(static, UTA_TRIP_UPDATE_URL, UTA_VEHICLES_URL)
            
        except GtfsLoadError as e:
            self.logger.critical("Failed to retrieve current protobuf data.")
            self.logger.exception(e)
            
        self.current_stops = current_times["stop_name"].unique()
        self.current_stops = [format_name(entry) for entry in self.current_stops]
        
        self.station_view.clear()
        self.station_view.addItems(self.current_stops)
        self.station_view.sortItems(Qt.SortOrder.AscendingOrder)
        
    def pause_widget(self, func: function, *args: any) -> None:
        thread = WorkerThread(func, *args, parent = self)
        thread.result_ready.connect(lambda: self.setEnabled(True))
        thread.finished.connect(thread.deleteLater)
        thread.start()
        self.setEnabled(False)
        
    def update_list(self, current_widget: QListWidget, source_list: list, current_search: str, last_search: str):
        current_widget.clear()
        
        if not current_search:
            current_widget.addItems(source_list)
            return
                
        current_results = [current_widget.item(x).text() for x in range(current_widget.count())] if not current_search.startswith(last_search) else source_list
        last_search = current_search

        new_results = []
        check_search = current_search.lower()
        search_chars = set(check_search)

        for result in current_results:
            check_result = result.lower()
            if not all(char in check_result for char in search_chars):
                print(f"All characters from {search_chars} are not in {result}")
                continue

            score = self.search(check_search, check_result)
            print(f"Search: {check_search}, Result: {check_result}, Score: {score}")

            new_results.append({
                "val": result,
                "score": score
            })

        new_results.sort(key = lambda x: x["score"])
        
        new_results = [entry["val"] for entry in new_results]
            
        current_widget.addItems(new_results)

    def search(self, needle: str, haystack: str):
        score = 0
        search_pos = 0
        last_match = 0

        needle_len = len(needle)
        haystack_len = len(haystack)

        if(needle == haystack):
            return 1000

        for i in range(haystack_len):
            if search_pos >= needle_len:
                break
            
            if needle[search_pos:] in haystack[i:]:
                
                if last_match:
                    score -= (i - last_match - 1) * 2
                    score = max(score, 1)

                if last_match and i == last_match + 1:
                    score += 10
                else:
                    score += 1

                if i == 0:
                    score += 20
                elif i <= 3:
                    score += 5

                last_match = i
                search_pos += 1

        if haystack[search_pos:] == needle:
            score += 100

        return score


        