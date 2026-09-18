import requests
import zipfile
import io
import pandas as pd
import datetime

from google.transit import gtfs_realtime_pb2
from typing import ClassVar
from dataclasses import dataclass
from uta_logger import UTALogger
from zoneinfo import ZoneInfo
from datetime import timezone, datetime
from util import parse_service_time

class GtfsLoadError(Exception):
    '''Exception to be thrown if GTFSData fails to be created for whatever reason.'''

@dataclass
class GTFSData:
    _LOGGER = UTALogger("gtfs_data", "gtfs_data_handler").logger
    
    agency: pd.DataFrame
    stops: pd.DataFrame
    routes: pd.DataFrame
    trips: pd.DataFrame
    stop_times: pd.DataFrame
    
    agency_tzinfo: datetime.tzinfo
    gtfs_static_url: str
    
    REQUIRED_FILES: ClassVar[tuple[str]] = (
        "agency.txt",
        "stops.txt",
        "routes.txt",
        "trips.txt",
        "stop_times.txt"
    )
            
    @classmethod
    def from_url(cls, url: str) -> GTFSData:
        try:
            _gtfs_static = requests.get(url = url)
            _gtfs_static.raise_for_status()
            GTFSData._LOGGER.info(f"Successfully connected to {url}: Response {_gtfs_static.status_code}")
                    
        except requests.exceptions.HTTPError:
            raise(GtfsLoadError(f"Failed to connect to {url}: Response {_gtfs_static.status_code}"))
        
        try:
            with zipfile.ZipFile(io.BytesIO(_gtfs_static.content)) as zip:
                cls._do_files_exist(zip)
                
                agency = pd.read_csv(zip.open("agency.txt"))
                stops = pd.read_csv(zip.open("stops.txt"))
                routes = pd.read_csv(zip.open("routes.txt"))
                trips = pd.read_csv(zip.open("trips.txt"))
                stop_times = pd.read_csv(zip.open("stop_times.txt"))
                
                agency_tzinfo = ZoneInfo(agency["agency_timezone"].item())
            
        except zipfile.BadZipFile:
            raise(GtfsLoadError(f"Object [{cls.__name__}] failed to initialize: Data from [{url}] is not a zip file."))
        
        return cls(
            agency = agency,
            stops = stops,
            routes = routes,
            trips = trips,
            stop_times = stop_times,
            agency_tzinfo = agency_tzinfo,
            gtfs_static_url = url
        )
        
    @classmethod
    def _do_files_exist(cls, zip: zipfile.ZipFile) -> None:
        missing_files = set(cls.REQUIRED_FILES) - set(zip.namelist())
        
        if missing_files:
            missing = ", ".join(sorted(missing_files))
            raise(GtfsLoadError(f"GTFS feed zip file from is missing required {"file" if len(missing_files) == 1 else "files"}: {missing}"))
        
    def refresh_static_data(self):
        try:
            _gtfs_static = requests.get(url = self.gtfs_static_url)
            _gtfs_static.raise_for_status()
            GTFSData._LOGGER.info(f"Successfully connected to {self.gtfs_static_url}: Response {_gtfs_static.status_code}")
                    
        except requests.exceptions.HTTPError:
            raise(GtfsLoadError(f"Failed to connect to {self.gtfs_static_url}: Response {_gtfs_static.status_code}"))
        
        try:
            with zipfile.ZipFile(io.BytesIO(_gtfs_static.content)) as zip:
                self._do_files_exist(zip)
                
                self.agency = pd.read_csv(zip.open("agency.txt"))
                self.stops = pd.read_csv(zip.open("stops.txt"))
                self.routes = pd.read_csv(zip.open("routes.txt"))
                self.trips = pd.read_csv(zip.open("trips.txt"))
                self.stop_times = pd.read_csv(zip.open("stop_times.txt"))
                
                self.agency_tzinfo = ZoneInfo(self.agency["agency_timezone"].item())
            
        except zipfile.BadZipFile:
            raise(GtfsLoadError(f"Object [{GTFSData.__name__}] failed to initialize: Data from [{self.url}] is not a zip file."))
        
    def get_trips_from_name(self, route_name: str) -> pd.DataFrame:
        if route_name:
            route_ids = self.routes.loc[
                self.routes.route_long_name.str.contains(route_name, case = False, regex = False),
                ["route_id", "route_long_name"]
            ]
            
        else:
            route_ids = self.routes[["route_id", "route_long_name"]]
        
        if route_ids.empty:
            self._LOGGER.warning(f"Found no trips that match [{route_name}].")
            return None
        
        self._LOGGER.info(f"Found {len(route_ids)} routes matching \"{route_name}\".")

        trips = self.trips.loc[
            self.trips.route_id.isin(route_ids.route_id),
            ["trip_id", "trip_headsign", "direction_id", "route_id"]
        ]
        
        stop_times = self.stop_times.loc[
            self.stop_times.trip_id.isin(trips.trip_id),
            ["trip_id", "stop_id", "arrival_time", "departure_time", "stop_sequence"]
        ]
        
        stops = self.stops.loc[
            self.stops.stop_id.isin(stop_times.stop_id),
            ["stop_id", "stop_name"]
        ]
        
        complete_trips = (
            trips
                .merge(route_ids, on = "route_id", how = "left")
                .merge(stop_times, on = "trip_id", how = "left")
                .merge(stops, on = "stop_id", how = "left")
        )

        today = datetime.now(timezone.utc).astimezone(self.agency_tzinfo)
        complete_trips.arrival_time = complete_trips.arrival_time.map(lambda x: parse_service_time(x, today))
        complete_trips.departure_time = complete_trips.departure_time.map(lambda x: parse_service_time(x, today))

        return complete_trips.sort_values("departure_time").reset_index(drop = True)
    
    def get_current(self, static_gtfs: pd.DataFrame, trip_update_url: str, vehicles_url: str) -> pd.DataFrame:
        
        if static_gtfs.empty:
            return static_gtfs
    
        def get_protobuf_data(url: str) -> gtfs_realtime_pb2.FeedEntity:
            try:
                pb = requests.get(url = url)
                pb.raise_for_status()
                
            except requests.HTTPError:
                raise(GtfsLoadError(f"Failed to retrieve protobuf data from [{url}]: Response {pb.status_code}"))

            GTFSData._LOGGER.info(f"Successfully connected to {url}: Response {pb.status_code}")
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(pb.content)

            return feed

        update_feed = get_protobuf_data(trip_update_url)
        vehicle_feed = get_protobuf_data(vehicles_url)

        update_data = []
        vehicle_data = []

        for entity in update_feed.entity:
            if not entity.HasField("trip_update"):
                continue
            
            for update in entity.trip_update.stop_time_update:
                update_data.append({
                    "trip_id": int(entity.trip_update.trip.trip_id), 
                    "stop_sequence": int(update.stop_sequence), 
                    "new_arrival_time": datetime.fromtimestamp(update.arrival.time, self.agency_tzinfo), 
                    "new_departure_time": datetime.fromtimestamp(update.departure.time, self.agency_tzinfo)
                })

        for entity in vehicle_feed.entity:
            if not entity.HasField("vehicle"):
                continue

            vehicle_data.append({"trip_id": entity.vehicle.trip.trip_id})

        updated_trips = pd.DataFrame(update_data, columns = ["trip_id", "stop_sequence", "new_arrival_time", "new_departure_time"])
        updated_vehicles = pd.DataFrame(vehicle_data, columns = ["trip_id"])

        updated_trips = updated_trips[updated_trips.trip_id.isin(updated_vehicles.trip_id.unique())]

        all_trips = pd.merge(
            static_gtfs,
            updated_trips,
            on = ["trip_id", "stop_sequence"],
            how = "left"
        )

        return all_trips