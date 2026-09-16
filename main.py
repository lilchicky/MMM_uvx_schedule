import requests
import datetime
import pandas as pd

from google.transit import gtfs_realtime_pb2
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from gtfs_static_data import StaticData as sd
from uta_logger import UTALogger
from config import (
    UTA_GTFS_STATIC_URL,
    UTA_TRIP_UPDATE_URL
)

LOGGER = UTALogger().logger
STATIC_DATA = sd.from_url(UTA_GTFS_STATIC_URL)

def main():
    
    if STATIC_DATA is None:
        LOGGER.critical(f"The static GTFS data was unable to be retirieved, aborting.")
        return
    
    gtfs_trip_update_pf = requests.get(url = UTA_TRIP_UPDATE_URL)
    gtfs_trip_update_pf.raise_for_status()
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(gtfs_trip_update_pf.content)
    
    uvx_trips = STATIC_DATA.get_trips_from_name("UVX")
    frontrunner_trips = STATIC_DATA.get_trips_from_name("FrontRunner")

    for _, row in frontrunner_trips.iterrows():
        if (datetime.now(timezone.utc).astimezone(STATIC_DATA.agency_tzinfo) > row.arrival_time):
            continue
        
        print(f"Arriving at {row.stop_name} at {row.arrival_time.strftime("%H:%M:%S")} on {row.arrival_time.strftime("%B %d, %Y")}. The trip is heading {"north" if row.direction_id else "south"}.")
        break

    for _, row in uvx_trips.iterrows():
        if (datetime.now(timezone.utc).astimezone(STATIC_DATA.agency_tzinfo) > row.arrival_time):
            continue

        print(f"Arriving at {row.stop_name} at {row.arrival_time.strftime("%H:%M:%S")} on {row.arrival_time.strftime("%B %d, %Y")}. The trip is heading {"north" if row.direction_id else "south"}.")
        break
    
    pf_data = []
    
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
        
        for update in entity.trip_update.stop_time_update:
            pf_data.append({
                "trip_id": int(entity.trip_update.trip.trip_id), 
                "stop_sequence": int(update.stop_sequence), 
                "new_arrival_time": datetime.fromtimestamp(update.arrival.time, ZoneInfo(STATIC_DATA.agency["agency_timezone"].item())), 
                "new_departure_time": datetime.fromtimestamp(update.departure.time, ZoneInfo(STATIC_DATA.agency["agency_timezone"].item()))
            })
                
    current_times = pd.DataFrame(pf_data)
    current_times = pd.merge(
        frontrunner_trips,
        current_times,
        on = ["trip_id", "stop_sequence"],
        how = "left"
    )
    print(current_times[current_times["new_arrival_time"].notnull()])
    
if __name__ == "__main__":
    main()