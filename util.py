import pandas as pd
import logging
import re

from datetime import timedelta, datetime

def parse_service_time(stop_time: str, today: datetime) -> datetime:
    '''
    Normalize a service time (which can be hours over 24 for times after midnight on each "service day") to be
    a datetime formatted in the UTC format.
    
    :param str stop_time: The time, as a string, to be translated (i.e. 25:01:36 becomes 1:01:36AM the next day)
    :param datetime today: Todays date
    
    :returns datetime: The adjusted time in the datetime UTC format
    '''
    if pd.isna(stop_time):
        return pd.NaT
    
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

def get_next_departures(frame: pd.DataFrame, today: datetime, logger: logging.Logger, station: str|int = "", num_routes: int = 1) -> dict: 
    future_trips = frame[frame.departure_time > today]
    
    if station:
        station_restricted = (
            future_trips[future_trips.stop_id == station] if isinstance(station, int)
            else future_trips[future_trips.stop_name.str.contains(station, case = False)]
        )
        
        if not station_restricted.empty:
            future_trips = station_restricted
            
            matched_stations = future_trips.stop_name.unique()
            logger.info(f"{"Stop ID" if isinstance(station, int) else "Stop name"} [{station}] was found and resolved to {format_readable_list(matched_stations, max_len = 5, isolate_char = "\"")}.")
        else:
            logger.warning(f"No stops could be found that match {"stop ID" if isinstance(station, int) else "stop name"} [{station}], so all stations will be included.")
            
    future_trips = future_trips.sort_values(["route_id", "direction_id", "departure_time"])
    grouped_trips = future_trips.groupby(["route_id", "direction_id"]).head(num_routes).reset_index(drop = True)

    times = {}

    for _, row in grouped_trips.iterrows():
        if row.route_id not in times:
            times[row.route_id] = {
                "route_name": row.route_long_name,
                "stop_name": row.stop_name,
                "trip_headsign_north": None,
                "trip_headsign_south": None,
                "departures_north": [],
                "departures_south": []
            }
        
        departure = times.get(row.route_id)
        dir_suffix = "_north" if not row.direction_id else "_south"
        
        if departure[f"trip_headsign{dir_suffix}"] is None:
            departure.update({f"trip_headsign{dir_suffix}": row.trip_headsign})
            
        departure[f"departures{dir_suffix}"].append([
            row.departure_time,
            (None if pd.isna(row.new_departure_time) else row.new_departure_time)
        ])
            
    return times

def build_departure_string(departures: dict) -> str:
    
    def get_plural(to_check: list, is_singlular: str, is_plural: str) -> str:
        if len(to_check) == 1:
            return is_singlular
        return is_plural
        
    def get_formatted_departures(is_north: bool) -> str:
        times = departures.get(f"departures_{"north" if is_north else "south"}")
        
        if not times:
            return ""
        
        heading = departures.get(f"trip_headsign_{"north" if is_north else "south"}").removeprefix("To ").title()
        times_to_list = [i[(0 if i[1] is None else 1)].strftime("%H:%M:%S") for i in times]

        departure_locations = f"{departures.get("route_name").title()}'s next {get_plural(times, "departure", f"{len(times)} departures")} from {departures.get("stop_name")} towards {heading}"
        departure_times = f"{get_plural(times, "is", "are")} at {format_readable_list(times_to_list)}"
        
        return f"{departure_locations} {departure_times}"
        
    north = f"{get_formatted_departures(True)}"
    south = f"{get_formatted_departures(False)}"
    
    north += "." if north else ""
    south += "." if south else ""
    
    return f"{north}{"\n" if north and south else ""}{south}"
    
def format_readable_list(input: list, max_len: int = 0, isolate_char: str = "") -> str:
    original_len = len(input)
    truncated = False
    
    def surround(val: any):
        return f"{isolate_char}{val}{isolate_char}"
    
    if original_len <= 1:
        return surround(input[0])
    
    if original_len == 2:
        return f"{surround(input[0])} and {surround(input[1])}"
    
    if max_len > 0 and original_len > max_len:
        truncated = True
        input = input[:max_len]
        
    input = [surround(to_sur) for to_sur in input]
        
    joined = ", ".join(input[:-1] if not truncated else input)
    after_and = f", and {input[-1] if not truncated else f"{original_len - len(input)} more"}"
        
    return joined + after_and
    
def format_name(name: str) -> str:
    match = re.search(r"\(([A-Z0-9]+)\)\s*$", name)
    
    if match:
        a = match.group(0)
        text = name[:match.start()].strip()
        
        return f"{text.title() if text.isupper() else text} {a}"
        
    return name.title() if name.isupper() else name