import logging
import sys
import os
from typing import Optional

# Configure default logging parameters
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment variable to control log level
LOG_LEVEL_ENV = os.getenv("LOCAVOX_LOG_LEVEL", "").upper()


def get_log_level() -> int:
    """Get log level from environment or use default"""
    if LOG_LEVEL_ENV == "DEBUG":
        return logging.DEBUG
    elif LOG_LEVEL_ENV == "INFO":
        return logging.INFO
    elif LOG_LEVEL_ENV == "WARNING":
        return logging.WARNING
    elif LOG_LEVEL_ENV == "ERROR":
        return logging.ERROR
    elif LOG_LEVEL_ENV == "CRITICAL":
        return logging.CRITICAL
    else:
        return DEFAULT_LOG_LEVEL


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up and return a logger with the specified name and level.

    Args:
        name: The name of the logger
        level: Optional specific log level, defaults to environment setting or INFO

    Returns:
        Configured logger instance
    """
    if level is None:
        level = get_log_level()

    logger = logging.getLogger(name)

    # Only configure handlers if they haven't been set up already
    if not logger.handlers:
        formatter = logging.Formatter(DEFAULT_FORMAT)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


# Create the default application logger
app_logger = setup_logger("locavox")

# Configure root logger for libraries
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)  # Set higher threshold for external libraries
