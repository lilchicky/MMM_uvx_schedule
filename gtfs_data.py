import requests
import zipfile
import io
import pandas as pd
import datetime

from typing import ClassVar
from dataclasses import dataclass
from uta_logger import UTALogger
from zoneinfo import ZoneInfo
from datetime import timezone, datetime
from util import parse_service_time

class GtfsLoadError(Exception):
    '''Exception to be thrown if '''

@dataclass
class GTFSData:
    _LOGGER = UTALogger("static_gtfs", "static_gtfs").logger
    
    agency: pd.DataFrame
    stops: pd.DataFrame
    routes: pd.DataFrame
    trips: pd.DataFrame
    stop_times: pd.DataFrame
    agency_tzinfo: datetime.tzinfo
    
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
                    
        except requests.exceptions.HTTPError as e:
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
            agency_tzinfo = agency_tzinfo
        )
        
    @classmethod
    def _do_files_exist(cls, zip: zipfile.ZipFile) -> None:
        missing_files = set(cls.REQUIRED_FILES) - set(zip.namelist())
        
        if missing_files:
            missing = ", ".join(sorted(missing_files))
            raise(GtfsLoadError(f"GTFS feed zip file from is missing required {"file" if len(missing_files) == 1 else "files"}: {missing}"))
        
    def get_trips_from_name(self, route_name: str) -> pd.DataFrame:
        route_ids = self.routes.loc[
            self.routes.route_long_name.str.contains(route_name, case = False),
            ["route_id", "route_long_name"]
        ]
        
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