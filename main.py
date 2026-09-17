import requests
import datetime
import pandas as pd

from datetime import datetime, timezone
from gtfs_static_data import StaticData as sd
from uta_logger import UTALogger
from config import (
    UTA_GTFS_STATIC_URL
)
from util import (
    get_next_departures, 
    merge_rt_trip_updates, 
    build_departure_string,
    merge_vehicle_updates
)

LOGGER = UTALogger("main", "main").logger
STATIC_DATA = sd.from_url(UTA_GTFS_STATIC_URL)

def main():
    
    if STATIC_DATA is None:
        LOGGER.critical(f"The static GTFS data was unable to be retirieved, aborting.")
        return
    
    today = datetime.now(timezone.utc).astimezone(STATIC_DATA.agency_tzinfo)
    frontrunner_trips = STATIC_DATA.get_trips_from_name("frontrunner")
    
    if frontrunner_trips.empty:
        return
    
    current_times = merge_rt_trip_updates(frontrunner_trips, STATIC_DATA.agency_tzinfo)
    
    #print(current_times[current_times.new_departure_time.notnull()])
    #print(current_times)
    #print(frontrunner_trips)
    
    dirs = get_next_departures(current_times, today, LOGGER, station = "vineyard", num_routes = 3)
    print(dirs)
    for _, departures in dirs.items():
        print(build_departure_string(departures))
        break
        print(build_departure_string(item.get("north")))
        print(build_departure_string(item.get("south")))
    
if __name__ == "__main__":
    main()