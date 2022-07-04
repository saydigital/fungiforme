# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

# pylint: disable=duplicate-code

import logging
import os

from logging.handlers import (
    WatchedFileHandler,
    RotatingFileHandler,
    TimedRotatingFileHandler,
)
from datetime import datetime

DEFAULT_LEVEL = "INFO"
DEFAULT_FORMAT = (
    r"%(asctime)s %(process)d %(levelname)s ? %(name)s: %(message)s"
)
DEFAULT_MAX_BYTES = 100000000
DEFAULT_BACKUP_COUNT = 10
DEFAULT_ROLLOVER_TIME = "00:00:00"
DEFAULT_WHEN = "D"
DEFAULT_INTERVAL = 1


def _set_console_logging():
    logging.basicConfig(
        level=getattr(logging, DEFAULT_LEVEL), format=DEFAULT_FORMAT
    )


def _set_file_logging(log_config):
    log_filepath = log_config.get("filepath", "")
    log_rotate = log_config.get("logRotate", "")
    log_level = log_config.get("level", DEFAULT_LEVEL).upper()
    log_format = log_config.get("format", DEFAULT_FORMAT)
    log_handlers = []

    os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

    if log_rotate == "size":
        max_bytes = log_config.getint("maxBytes", DEFAULT_MAX_BYTES)
        backup_count = log_config.getint("backupCount", DEFAULT_BACKUP_COUNT)
        log_file_handler = RotatingFileHandler(
            log_filepath,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
    elif log_rotate == "time":
        rollover_time = log_config.get("rolloverTime", DEFAULT_ROLLOVER_TIME)
        backup_count = log_config.getint("backupCount", DEFAULT_BACKUP_COUNT)
        when = log_config.get("when", DEFAULT_WHEN)
        interval = log_config.getint("interval", DEFAULT_INTERVAL)
        if when == "midnight":
            at_time = None
        else:
            at_time = datetime.strptime(rollover_time, "%H:%M:%S")
        log_file_handler = TimedRotatingFileHandler(
            log_filepath,
            when=when,
            interval=interval,
            atTime=at_time,
            backupCount=backup_count,
            encoding="utf-8",
        )
    else:
        if os.name == "posix":
            # if fungiforme is running on Unix/Linux OS,
            # we use WatchedFileHandler to allow usage of system tools
            # like 'logrotate' to perform log rotation.
            # WatchedFileHandler is not supported under Windows.
            log_file_handler = WatchedFileHandler(
                log_filepath, encoding="utf-8"
            )
        else:
            log_file_handler = logging.FileHandler(
                log_filepath, encoding="utf-8"
            )

    log_file_handler.setFormatter(logging.Formatter(log_format))
    log_handlers.append(log_file_handler)

    logging.basicConfig(
        level=getattr(logging, log_level), handlers=log_handlers
    )


def setup(config):
    """
    Setup logging.
    """
    if not config.has_section("LOGGING"):
        _set_console_logging()
    else:
        log_config = config["LOGGING"]
        log_filepath = log_config.get("filepath", "")

        if log_filepath:
            _set_file_logging(log_config)
        else:
            log_level = log_config.get("level", DEFAULT_LEVEL).upper()
            log_format = log_config.get("format", DEFAULT_FORMAT)
            logging.basicConfig(
                level=getattr(logging, log_level), format=log_format
            )
