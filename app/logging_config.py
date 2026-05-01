import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOG_LEVEL = os.getenv("LOG_LEVEL")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s:     [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        # "uvicorn": {"handlers": ["default"], "level": LOG_LEVEL},
        # "uvicorn.error": {"handlers": ["default"], "level": LOG_LEVEL},
        # "uvicorn.access": {"handlers": ["default"], "level": LOG_LEVEL},
        "": {"handlers": ["default"], "level": LOG_LEVEL},  # root logger
    },
}
