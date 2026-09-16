import logging
import os
import glob

from pathlib import Path
from config import (
    LOGGING_LEVEL,
    WRITE_LOGS_TO_FILE,
    LOG_FILE_PREFIX,
    LOG_FILE_SUFFIX,
    LOG_FOLDER,
    MAX_SAVED_LOGS
)

class UTALogger():
    """Class to create a logger with consistent formatting across scripts."""
    def __init__(self, logger_name: str, base_log_file_name: str):
        """
        Init UTALogger

        :param str logger_name: The name of the logger to show up in log lines.
        :param str base_log_file_name: The base name to apply to the logging file, in addition to the prefix/suffix defined in config.
        """
        self.base_log_file_name = base_log_file_name
        """Base file name to be applied between ''prefix'' and ''suffix'' when creating log files."""
        self.logger_name = logger_name
        """Name of this logger, used to specify what is being ran when logging."""

        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(LOGGING_LEVEL)

        _handler = logging.StreamHandler()
        _handler.setLevel(LOGGING_LEVEL)
        _handler.setFormatter(self.Formatter())

        self.logger.addHandler(_handler)

        if WRITE_LOGS_TO_FILE:
            log_folder = Path(__file__).parent.resolve() / LOG_FOLDER
            path = f"{log_folder}/{LOG_FILE_PREFIX}{'' if not LOG_FILE_PREFIX else '-'}{self.base_log_file_name}{'' if not LOG_FILE_SUFFIX else '-'}{LOG_FILE_SUFFIX}.log"

            self.logger.info(f"Logging to files has been enabled. Creating log file at {path}")

            self.build_log_file_handler(
                path,
                log_folder
            )

    def clean_old_logs(self, folder_path: str) -> None:
        """
        Remove the oldest logs in the log folder, if number of logs is over [MAX_SAVED_LOGS].
        This will delete any log that contains the base file name at all, not exclusively exact
        matches.
        """
        current_logs = list(filter(os.path.isfile, glob.glob(f"{folder_path}/*{self.base_log_file_name}*.log")))
        current_logs.sort(key = lambda file: os.path.getmtime(file), reverse = True)

        for f in current_logs[MAX_SAVED_LOGS:]:
            os.unlink(f)

    def build_log_file_handler(self, path, log_folder) -> None:
        """Build a handler to create log files."""
        log_folder.mkdir(exist_ok = True)

        file_handler = logging.FileHandler(path,mode = "w")
        file_handler.setLevel(LOGGING_LEVEL)
        file_handler.setFormatter(logging.Formatter("%(asctime)s[%(name)s][%(levelname)s]: %(message)s"))

        self.clean_old_logs(log_folder)

        self.logger.addHandler(file_handler)

    class Formatter(logging.Formatter):
        """Custom formatter class for loggers from UTALogger."""
        grey = "\x1b[38;20m"
        yellow = "\x1b[33m"
        red = "\x1b[31m"
        reset = "\x1b[0m"
        format = "%(asctime)s[%(name)s][%(levelname)s]: %(message)s"

        FORMATS = {
            logging.DEBUG: grey + format + reset,
            logging.INFO: grey + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: red + format + reset
        }

        def format(self, record: logging.LogRecord) -> str:
            log_format = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_format)
            return formatter.format(record)