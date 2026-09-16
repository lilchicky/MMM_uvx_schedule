import logging
import datetime

UTA_GTFS_STATIC_URL = "https://gtfsfeed.rideuta.com/GTFS_RT.zip"
UTA_TRIP_UPDATE_URL = "https://apps.rideuta.com/tms/gtfs/TripUpdate"

LOGGING_LEVEL = logging.DEBUG
WRITE_LOGS_TO_FILE = True
LOG_FOLDER = "logs"
LOG_FILE_PREFIX = f"{datetime.datetime.now():%Y-%m-%d_%H%M%S}"
LOG_FILE_SUFFIX = ""
MAX_SAVED_LOGS = 5