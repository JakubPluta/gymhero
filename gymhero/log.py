import logging
import sys
from enum import Enum
from typing import Optional

LOGGING_FORMATTER = (
    "[%(levelname)s] %(name)s %(asctime)s %(funcName)s:%(lineno)d - %(message)s"
)


class DebugLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def get_logger(name: Optional[str] = None, level: DebugLevel = 'DEBUG') -> logging.Logger:
    """Creates and configures a logger object.

    :param name: The name of the logger (optional).
    :type name: Optional[str]
    :param level: The logging level (default: "DEBUG").
    :type level: str
    :return: The configured logger object.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name=name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOGGING_FORMATTER)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if not level or level.upper() not in DebugLevel.__members__:
        logger.warning(
            "invalid logging level: %s, setting logging level to `DEBUG`", level
        )
        level = DebugLevel.DEBUG.value
    logger.setLevel(level=level)
    return logger

