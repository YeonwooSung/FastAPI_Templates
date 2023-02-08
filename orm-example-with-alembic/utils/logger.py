"""Provides logging functionality"""

import logging
import os

from .singleton import Singleton


class Logger(metaclass=Singleton):
    """Logger class."""

    def __init__(self) -> None:
        """Initialize"""
        self.log_name = os.getenv("LOG_NAME", "example_app")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.logger = None

    def get_logger(self) -> logging.Logger:
        """Get a logger instance"""
        if not self.logger:
            logger = logging.getLogger(self.log_name)
            logger.setLevel(self.log_level)

            fmt_str = "%(asctime)s | %(levelname)s | %(thread)d | %(module)s | %(funcName)s | %(message)s"
            formatter = logging.Formatter(fmt_str)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            self.logger = logger
            return logger
        return self.logger
