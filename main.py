import requests
import datetime
import pandas as pd

from datetime import datetime, timezone
from gtfs_data import GtfsLoadError, GTFSData
from uta_logger import UTALogger
from config import (
    UTA_GTFS_STATIC_URL
)
from util import (
    get_next_departures, 
    merge_rt_trip_updates, 
    build_departure_string
)

LOGGER = UTALogger("main", "main").logger

def main():
    
    try:
        gd = GTFSData.from_url(UTA_GTFS_STATIC_URL)
        
    except GtfsLoadError as e:
        LOGGER.critical("GTFS Data object failed to load.")
        LOGGER.exception(e)
        return
    
    except Exception as e:
        LOGGER.critical("An error has occurred during loading.")
        LOGGER.exception(e)
        return
    
    today = datetime.now(timezone.utc).astimezone(gd.agency_tzinfo)
    frontrunner_trips = gd.get_trips_from_name("frontrunner")
    
    if frontrunner_trips.empty:
        return
    
    current_times = merge_rt_trip_updates(frontrunner_trips, gd.agency_tzinfo)
    
    #print(current_times[current_times.new_departure_time.notnull()])
    #print(current_times)
    #print(frontrunner_trips)
    
    dirs = get_next_departures(current_times, today, LOGGER, station = "vineyard", num_routes = 3)
    
    for _, departures in dirs.items():
        print(build_departure_string(departures))
        break
        print(build_departure_string(item.get("north")))
        print(build_departure_string(item.get("south")))
    
if __name__ == "__main__":
    main()