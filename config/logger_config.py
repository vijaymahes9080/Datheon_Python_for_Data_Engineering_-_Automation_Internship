"""Logging configuration with rotating file handlers and standard console formatting."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import settings


def configure_logging(log_level: str | None = None) -> logging.Logger:
    """Configure root logger with console and rotating file handlers."""
    level = getattr(logging, (log_level or settings.LOG_LEVEL).upper(), logging.INFO)
    logger = logging.getLogger("streamforge")
    logger.setLevel(level)

    # Avoid duplicate handlers on re-entry
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler (5 MB per file, 3 backups)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = settings.LOGS_DIR / "streamforge.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
