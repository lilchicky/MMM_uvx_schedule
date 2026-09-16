import requests
import io
import zipfile
import datetime
import pandas as pd

from google.transit import gtfs_realtime_pb2
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo

def parse_service_time(stop_time: str, today: datetime) -> datetime:
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

def timestamp_to_datetime(timestamp: int, tz: datetime._TzInfo = None):
    return datetime.fromtimestamp(timestamp, tz)

def get_trips_from_name(route_name: str, stops: pd.DataFrame, stop_times: pd.DataFrame, routes: pd.DataFrame, trips: pd.DataFrame, agency: pd.DataFrame):
    route_id = routes[routes.route_long_name.str.contains(route_name)]
    route_id = route_id["route_id"].item()

    uta_timezone = agency["agency_timezone"].item()

    trips_from_id = trips[trips.route_id == route_id].drop("route_id", axis = 1)

    complete_trips = pd.merge(
        stop_times.loc[:, ["trip_id", "stop_id", "arrival_time", "departure_time", "stop_sequence"]], 
        trips_from_id.loc[:, ["trip_id", "trip_headsign", "direction_id"]], 
        on = "trip_id"
    )
    complete_trips = pd.merge(
        complete_trips, 
        stops.loc[:, ["stop_id", "stop_name"]], 
        on = "stop_id"
    )

    today = datetime.now(timezone.utc).astimezone(ZoneInfo(uta_timezone))
    complete_trips["arrival_time"] = complete_trips["arrival_time"].map(lambda x: parse_service_time(x, today))
    complete_trips["departure_time"] = complete_trips["departure_time"].map(lambda x: parse_service_time(x, today))

    complete_trips.sort_values(by = "arrival_time", ascending = True, inplace = True)
    
    return complete_trips

def main():
    print("starting...")
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get("https://apps.rideuta.com/tms/gtfs/TripUpdate")
    feed.ParseFromString(response.content)
    
    response = requests.get(url = "https://gtfsfeed.rideuta.com/GTFS_RT.zip", allow_redirects = True)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
        print(zip.namelist())
        agency = pd.DataFrame(pd.read_csv(zip.open("agency.txt")))
        stops = pd.DataFrame(pd.read_csv(zip.open("stops.txt")))
        routes = pd.DataFrame(pd.read_csv(zip.open("routes.txt")))
        trips = pd.DataFrame(pd.read_csv(zip.open("trips.txt")))
        stop_times = pd.DataFrame(pd.read_csv(zip.open("stop_times.txt")))

    uvx_trips = get_trips_from_name("UVX", stops, stop_times, routes, trips, agency)
    frontrunner_trips = get_trips_from_name("FrontRunner", stops, stop_times, routes, trips, agency)

    for _, row in frontrunner_trips.iterrows():
        if (datetime.now(timezone.utc).astimezone(ZoneInfo(agency["agency_timezone"].item())) > row.arrival_time):
            continue
        
        print(f"Arriving at {row.stop_name} at {row.arrival_time.strftime("%H:%M:%S")} on {row.arrival_time.strftime("%B %d, %Y")}. The trip is heading {"north" if row.direction_id else "south"}.")
        break

    for _, row in uvx_trips.iterrows():
        if (datetime.now(timezone.utc).astimezone(ZoneInfo(agency["agency_timezone"].item())) > row.arrival_time):
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
                "new_arrival_time": timestamp_to_datetime(update.arrival.time, ZoneInfo(agency["agency_timezone"].item())), 
                "new_departure_time": timestamp_to_datetime(update.departure.time, ZoneInfo(agency["agency_timezone"].item()))
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