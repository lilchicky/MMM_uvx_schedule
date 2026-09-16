import pandas as pd
import requests

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

def get_next_north_south(frame: pd.DataFrame, today: datetime) -> dict:
    times = {}
    
    def get_dir_string(curr_row: pd.DataFrame, dir: str) -> None:
        dir_str = (
            f"{curr_row.route_long_name}'s next departure towards {curr_row.trip_headsign.removeprefix("To ")} "
            f"is at {curr_row.departure_time:%H:%M:%S} and is "
            f"{"on time" if pd.isna(curr_row.new_departure_time) else f" leaving at {curr_row.new_departure_time:%H:%M:%S}"}."
        )
        
        if curr_row.route_id in times:
            times.get(curr_row.route_id).update({dir: dir_str})
            
        else:
            times.update({
                curr_row.route_id: {
                    dir: dir_str
                }
            })
    
    north_routes = []
    south_routes = []
    for _, row in frame.iterrows():
        if row.departure_time > today:
            in_north = row.route_id in north_routes
            in_south = row.route_id in south_routes
            
            if (in_north and not row.direction_id) or (in_south and row.direction_id):
                continue
            
            if not in_north and not row.direction_id:
                get_dir_string(row, "north")
                north_routes.append(row.route_id)
                
            if not in_south and row.direction_id:
                get_dir_string(row, "south")
                south_routes.append(row.route_id)
            
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