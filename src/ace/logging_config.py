from __future__ import annotations

import logging
import os
from logging.config import dictConfig

DEFAULT_LEVEL = os.getenv("ACE_LOG_LEVEL", "INFO").upper()


def configure_logging(level: str = DEFAULT_LEVEL) -> None:
    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": level, "handlers": ["console"]},
    }

    dictConfig(cfg)
    logging.getLogger(__name__).debug("Logging configured (level=%s)", level)
