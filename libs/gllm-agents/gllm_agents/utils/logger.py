"""Defines a logger for logging.

Example of Displayed Logs using default format:
    [2023-10-24 09:23:15 +0700] [24600] [INFO] Processing the message into the use case flow...

Example of Displayed Logs using json format:
    {"level": "INFO", "time": "2025-03-19T03:54:08.782202Z", "pid": 32565, "hostname": "GDPL-LTP-279.local",
    "name": "GDPLabsGenAILogger", "message": "Total config loading time: 19.16 seconds"}

Authors:
    Pray Somaldo (pray.somaldo@gdplabs.id)
    Anggara Setiawan (anggara.t.setiawan@gdplabs.id)
    Hermes Vincentius Gani (hermes.v.gani@gdplabs.id)

References:
    [1] https://github.com/GDP-ADMIN/gsdp
"""

import logging

from colorama import Fore, Style

LOG_FORMAT = "default"
LOGGER_NAME = "GDPLabsGenAILogger"
COLORED_LOG_FORMAT = f"{Fore.LIGHTBLACK_EX}[%(asctime)s.%(msecs)03d %(levelname).1s]{Style.RESET_ALL} %(message)s"
COLORED_LOG_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""

    def format(self, record: logging.LogRecord):
        """Format the log record with colors based on log level.

        Args:
            record (logging.LogRecord): The log record to be formatted.
        """
        log_colors = {
            logging.DEBUG: Style.RESET_ALL,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA,
        }
        color = log_colors.get(record.levelno, Fore.WHITE)
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


colored_log_formatter = ColoredFormatter(COLORED_LOG_FORMAT, datefmt=COLORED_LOG_DATE_FORMAT)

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
logger.propagate = False

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(colored_log_formatter)
logger.addHandler(stream_handler)
