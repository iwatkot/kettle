import logging
import os

from datetime import datetime

absolute_path = os.path.dirname(__file__)

LOG_FORMATTER = "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
LOG_FILE = os.path.join(absolute_path, 'logs/{date}.txt').format(
    date=datetime.date(datetime.now()))


class Logger(logging.getLoggerClass()):
    """Handles logging to the file with timestamps."""
    def __init__(self, name: str):
        super().__init__(name)
        os.makedirs(os.path.join(absolute_path, 'logs'), exist_ok=True)
        self.setLevel(logging.DEBUG)
        self.file_handler = logging.FileHandler(
            filename=LOG_FILE, mode='a', encoding='utf-8')
        self.fmt = LOG_FORMATTER
        self.file_handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        self.addHandler(self.file_handler)
