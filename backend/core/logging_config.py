import sys

import logging
from logging import Formatter, StreamHandler
from pathlib import Path

from colorlog import ColoredFormatter


def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger("cryptovol_api")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    console_format = (
        "%(log_color)s[%(asctime)s] %(blue)s%(name)s:%(reset)s "
        "%(log_color)s%(levelname)s%(reset)s | "
        "%(cyan)s%(funcName)s:%(reset)s %(log_color)s%(message)s"
    )
    console_formatter = ColoredFormatter(
        console_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "bold_red",
            "CRITICAL": "purple",
        },
    )
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_formatter = Formatter(
        "[%(asctime)s] %(name)s:%(levelname)s | %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logger initialized successfully")
    return logger


logger = setup_logger()