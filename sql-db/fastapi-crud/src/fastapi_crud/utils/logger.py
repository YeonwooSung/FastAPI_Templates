"""Provides logging functionality"""

import logging
import os

# custom module
from fastapi_crud.utils.singleton import Singleton

_DEFAULT_LOG_NAME = "example_app"
_DEFAULT_LOG_LEVEL = "DEBUG"
_DEFAULT_MAX_BYTES = 10485760
_DEFAULT_BACKUP_COUNT = 10

class Logger(metaclass=Singleton):
    """Logger class."""

    def __init__(
        self,
        use_file_handler:bool=True,
        use_rotate_file_handler=True,
        rotate_max_byte:int=_DEFAULT_MAX_BYTES,
        rotate_backup_count:int=_DEFAULT_BACKUP_COUNT
    ) -> None:
        """
        Initialize the logger.

        Use the proxy pattern to create a singleton logger when it is actually required.
        """
        self.log_name = os.getenv("LOG_NAME", _DEFAULT_LOG_NAME)
        self.log_level = os.getenv("LOG_LEVEL", _DEFAULT_LOG_LEVEL) # [DEBUG, INFO, WARNING, ERROR, CRITICAL]
        self.logger = None
        self.use_file_handler = use_file_handler
        self.use_rotate_file_handler = use_rotate_file_handler
        self.rotate_max_byte = rotate_max_byte
        self.rotate_backup_count = rotate_backup_count

    def get_logger(self) -> logging.Logger:
        """
        Get a logger instance

        Returns:
            logging.Logger: Logger instance
        """
        if not self.logger:
            logger = logging.getLogger(self.log_name)
            logger.setLevel(self.log_level)

            fmt_str = "%(asctime)s | %(levelname)s | %(thread)d | %(module)s | %(funcName)s | %(message)s"
            formatter = logging.Formatter(fmt_str)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)

            # check whether to use file handler
            if self.use_file_handler:
                # check whether to use rotate file handler
                if self.use_rotate_file_handler:
                    from logging.handlers import RotatingFileHandler
                    file_handler = RotatingFileHandler(
                        f"{self.log_name}.log",
                        maxBytes=self.rotate_max_byte,
                        backupCount=self.rotate_backup_count
                    )
                    file_handler.setLevel(self.log_level)
                    file_handler.setFormatter(formatter)
                else:
                    file_handler = logging.FileHandler(f"{self.log_name}.log")
                    file_handler.setLevel(self.log_level)
                    file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            self.logger = logger
            return logger
        return self.logger
