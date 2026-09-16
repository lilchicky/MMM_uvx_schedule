import pandas as pd
import requests
import logging

from datetime import timedelta, datetime
from google.transit import gtfs_realtime_pb2

def parse_service_time(stop_time: str, today: datetime) -> datetime:
    '''
    Normalize a service time (which can be hours over 24 for times after midnight on each "service day") to be
    a datetime formatted in the UTC format.
    
    :param str stop_time: The time, as a string, to be translated (i.e. 25:01:36 becomes 1:01:36AM the next day)
    :param datetime today: Todays date
    
    :returns datetime: The adjusted time in the datetime UTC format
    '''
    h, m, s = map(int, stop_time.split(":"))
    
    adjusted_date = datetime(
        today.year,
        today.month,
        today.day,
        h % 24,
        m,
        s,
        tzinfo = today.tzinfo
    )
    
    return adjusted_date + timedelta(days = h // 24)

def get_next_north_south(frame: pd.DataFrame, today: datetime, logger: logging.Logger, station: str|int = None, num_routes: int = 1) -> dict: 
    future_trips = frame[frame.departure_time > today]
    future_trips = future_trips.sort_values(["route_id", "direction_id", "departure_time"])
    
    if station is not None:
        station_restricted = future_trips[future_trips.stop_name.str.contains(station, case = False) if isinstance(station, str) else future_trips.stop_id == station]
        
        if not station_restricted.empty:
            future_trips = station_restricted
            
            matched_stations = future_trips.stop_name.unique()
            ms_len = len(matched_stations)
            matched_stations_f = (", ".join(matched_stations[:-1]) + f"{", " if ms_len > 2 else " "}and {matched_stations[-1]}") if ms_len > 1 else matched_stations[0]
            logger.info(f"{"Stop ID" if isinstance(station, int) else "Stop name"} [{station}] was found and resolved to {matched_stations_f}.")
        else:
            logger.warning(f"No stops could be found that match {"stop ID" if isinstance(station, int) else "stop name"} [{station}], so all stations will be included.")
            
    grouped_trips = future_trips.groupby(["route_id", "direction_id"]).head(num_routes).reset_index(drop = True)
    print(grouped_trips)
    
    times = {}
    
    for _, row in grouped_trips.iterrows():
        dir_str = (
            f"{row.route_long_name.title()}'s next departure {f"from {row.stop_name}"} towards {row.trip_headsign.removeprefix("To ").title()} "
            f"is at {row.departure_time:%H:%M:%S} and is "
            f"{"on time" if pd.isna(row.new_departure_time) else f" leaving at {row.new_departure_time:%H:%M:%S}"}."
        )
        
        if row.route_id not in times:
            times[row.route_id] = {"north": None, "south": None}
            
        times.get(row.route_id)["north" if not row.direction_id else "south"] = dir_str
            
    return {
        key: {
            direction: route.get(direction)
            for direction in ("north", "south")
        }
        for key, route in times.items()
    }

def merge_rt_trip_updates(to_merge: pd.DataFrame, url: str, tz: datetime.tzinfo) -> pd.DataFrame:
    gtfs_trip_update_pf = requests.get(url = url)
    gtfs_trip_update_pf.raise_for_status()
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(gtfs_trip_update_pf.content)
    
    pf_data = []
    
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
        
        for update in entity.trip_update.stop_time_update:
            pf_data.append({
                "trip_id": int(entity.trip_update.trip.trip_id), 
                "stop_sequence": int(update.stop_sequence), 
                "new_arrival_time": datetime.fromtimestamp(update.arrival.time, tz), 
                "new_departure_time": datetime.fromtimestamp(update.departure.time, tz)
            })
    
    updated_trips = pd.DataFrame(pf_data, columns = ["trip_id", "stop_sequence", "new_arrival_time", "new_departure_time"])
    updated_trips = pd.merge(
        to_merge,
        updated_trips,
        on = ["trip_id", "stop_sequence"],
        how = "left"
    )
    updated_trips.sort_values(by = "departure_time", ascending = True, inplace = True)
    
    return updated_trips