import logging
import os

from core.config import settings


def setup_error_logger() -> logging.Logger:
    logger = logging.getLogger("weather_errors")
    logger.setLevel(logging.INFO)

    log_path = os.path.abspath(settings.ERROR_LOG_FILE)
    has_handler = any(
        isinstance(handler, logging.FileHandler)
        and getattr(handler, "baseFilename", None) == log_path
        for handler in logger.handlers
    )

    if not has_handler:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger
