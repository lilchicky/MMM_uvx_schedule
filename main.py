import datetime

from datetime import datetime, timezone
from gtfs_data import GtfsLoadError, GTFSData
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
from ui import (
    test_place
)

LOGGER = UTALogger("main", "main").logger

def main():
    test_place("Vineyard, UT, USA")
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
    
    if frontrunner_trips is not None:
        try:
            current_times = gd.get_current(frontrunner_trips, UTA_TRIP_UPDATE_URL, UTA_VEHICLES_URL)
        except GtfsLoadError as e:
            LOGGER.critical("Failed to retrieve current protobuf data.")
            LOGGER.exception(e)

        #print(current_times[current_times.new_departure_time.notnull()])
        #print(current_times)
        #print(frontrunner_trips)

        dirs = get_next_departures(
            current_times, today, 
            LOGGER, 
            station = "vineyard", 
            num_routes = 3
        )

        for _, departures in dirs.items():
            print(build_departure_string(departures))
    
if __name__ == "__main__":
    main()