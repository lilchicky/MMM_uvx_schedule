import requests
import zipfile
import io
import pandas as pd
import datetime

from uta_logger import UTALogger
from zoneinfo import ZoneInfo
from datetime import timezone
from util import parse_service_time

class StaticData:
    _LOGGER = UTALogger("static_gtfs", "static_gtfs").logger
    
    def __init__(self):
        self.agency: pd.DataFrame|None = None
        self.stops: pd.DataFrame|None = None
        self.routes: pd.DataFrame|None = None
        self.trips: pd.DataFrame|None = None
        self.stop_times: pd.DataFrame|None = None
        
        self.agency_tzinfo: datetime.tzinfo|None = None
        
    def _build(self, bytes_: bytes) -> bool:
        try:
            with zipfile.ZipFile(io.BytesIO(bytes_)) as zip:
                self.agency = pd.read_csv(zip.open("agency.txt"))
                self.stops = pd.read_csv(zip.open("stops.txt"))
                self.routes = pd.read_csv(zip.open("routes.txt"))
                self.trips = pd.read_csv(zip.open("trips.txt"))
                self.stop_times = pd.read_csv(zip.open("stop_times.txt"))
                
            self.agency_tzinfo: datetime._TzInfo = ZoneInfo(self.agency["agency_timezone"].item())
                
            return True
                
        except KeyError as e:
            StaticData._LOGGER.critical(f"Unable to retrieve data from zip file: {e}")
                
        except TypeError as e:
            StaticData._LOGGER.critical(f"Initialization failed! object [{StaticData.__name__}] expected {bytes.__name__}, but received [{type(bytes_).__name__}] instead: {e}")
            
        except zipfile.BadZipFile as e:
            StaticData._LOGGER.critical(f"Byte data provided to [{StaticData.__name__}] could not be read as a zip file: {e}")
            
        except Exception as e:
            StaticData._LOGGER.critical(f"Failed to initialize static GTFS data: {e}")
            
        return False
            
    @classmethod
    def from_url(cls, url: str) -> StaticData|None:
        try:
            _gtfs_static = requests.get(url = url)
            _gtfs_static.raise_for_status()
            StaticData.__LOGGER.info(f"Successfully connected to {url}: Response {_gtfs_static.status_code}")
            
            obj = cls()
            
            if not obj.__build(_gtfs_static.content):
                return None
            
            StaticData.__LOGGER.info(f"Successfully retrieved static GTFS data from {url}.")
            return obj
                    
        except requests.exceptions.HTTPError as e:
            StaticData.__LOGGER.critical(f"Failed to connect to {url}: {e}")
            return None
        
    def get_trips_from_name(self, route_name: str) -> pd.DataFrame:
        route_id = self.routes[self.routes.route_long_name.str.contains(route_name)]
        route_id = route_id["route_id"].item()

        trips_from_id = self.trips[self.trips.route_id == route_id].drop("route_id", axis = 1)

        complete_trips = pd.merge(
            self.stop_times.loc[:, ["trip_id", "stop_id", "arrival_time", "departure_time", "stop_sequence"]], 
            trips_from_id.loc[:, ["trip_id", "trip_headsign", "direction_id"]], 
            on = "trip_id"
        )
        complete_trips = pd.merge(
            complete_trips, 
            self.stops.loc[:, ["stop_id", "stop_name"]], 
            on = "stop_id"
        )

        today = datetime.now(timezone.utc).astimezone(self.agency_tzinfo)
        complete_trips["arrival_time"] = complete_trips["arrival_time"].map(lambda x: parse_service_time(x, today))
        complete_trips["departure_time"] = complete_trips["departure_time"].map(lambda x: parse_service_time(x, today))

        complete_trips.sort_values(by = "arrival_time", ascending = True, inplace = True)

        return complete_trips