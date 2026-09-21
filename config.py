import logging
import datetime

from uta_logger import UTALogger

UTA_GTFS_STATIC_URL = "https://gtfsfeed.rideuta.com/GTFS_RT.zip"
UTA_TRIP_UPDATE_URL = "https://apps.rideuta.com/tms/gtfs/TripUpdate"
UTA_VEHICLES_URL = "https://apps.rideuta.com/tms/gtfs/Vehicle"

LOGGING_LEVEL = logging.DEBUG
WRITE_LOGS_TO_FILE = True
LOG_FOLDER = "logs"
LOG_FILE_PREFIX = f"{datetime.datetime.now():%Y-%m-%d_%H%M%S}"
LOG_FILE_SUFFIX = ""
MAX_SAVED_LOGS = 5

LOGGER = UTALogger(
    "main",
    "uta_tracker",
    LOGGING_LEVEL,
    WRITE_LOGS_TO_FILE,
    LOG_FILE_PREFIX,
    LOG_FILE_SUFFIX,
    LOG_FOLDER,
    MAX_SAVED_LOGS
).logger
