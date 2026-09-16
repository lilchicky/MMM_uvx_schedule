import requests
import datetime
import pandas as pd

from datetime import datetime, timezone
from gtfs_static_data import StaticData as sd
from uta_logger import UTALogger
from config import (
    UTA_GTFS_STATIC_URL,
    UTA_TRIP_UPDATE_URL
)
from util import get_next_north_south, merge_rt_trip_updates

LOGGER = UTALogger("main", "main").logger
STATIC_DATA = sd.from_url(UTA_GTFS_STATIC_URL)

def main():
    
    if STATIC_DATA is None:
        LOGGER.critical(f"The static GTFS data was unable to be retirieved, aborting.")
        return
    
    today = datetime.now(timezone.utc).astimezone(STATIC_DATA.agency_tzinfo)
    frontrunner_trips = STATIC_DATA.get_trips_from_name("8")
    
    current_times = merge_rt_trip_updates(frontrunner_trips, UTA_TRIP_UPDATE_URL, STATIC_DATA.agency_tzinfo)
    
    print(current_times[current_times["new_arrival_time"].notnull()])
    print(current_times)
    
    dirs = get_next_north_south(current_times, today)
    for _, item in dirs.items():
        print(item.get("north"))
        print(item.get("south"))
    
if __name__ == "__main__":
    main()