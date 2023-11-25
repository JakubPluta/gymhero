"""Logging module"""

import logging
import sys
from typing import Optional

LOGGING_FORMATTER = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


DebugLevels = ["DEBUG", "INFO", "WARNING", "ERROR"]
DebugLevelType = str


def get_logger(
    name: Optional[str] = None, level: DebugLevelType = "DEBUG"
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

    if not level or level not in DebugLevels:
        logger.warning(
            "Invalid logging level %s. Setting logging level to DEBUG.", level
        )
        level = "DEBUG"

    logger.setLevel(level=level)
    return logger
