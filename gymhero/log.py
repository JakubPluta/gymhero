"""Logging module"""

import logging
import sys
from enum import Enum
from typing import Optional

LOGGING_FORMATTER = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DebugLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def get_logger(
    name: Optional[str] = None, level: DebugLevel = DebugLevel.DEBUG
) -> logging.Logger:
    """
    Creates and configures a logger for logging messages.

    Parameters:
        name (Optional[str]): The name of the logger. Defaults to None.
        level (DebugLevel): The logging level. Defaults to DebugLevel.DEBUG.

    Returns:
        logging.Logger: The configured logger object.
    """
    logger = logging.getLogger(name=name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOGGING_FORMATTER)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not level or level not in DebugLevel:
        logger.warning(
            f"invalid logging level: {level}, setting logging level to `DEBUG`"
        )
        level = DebugLevel.DEBUG

    logger.setLevel(level=level)
    return logger
