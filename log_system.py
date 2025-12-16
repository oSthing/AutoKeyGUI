import time
import threading
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


LEVEL_TEXT = {
    LogLevel.DEBUG: "DEBUG",
    LogLevel.INFO: "INFO",
    LogLevel.WARN: "WARN",
    LogLevel.ERROR: "ERROR",
}


class Logger:

    def __init__(self):
        self._lock = threading.Lock()
        self._handlers = []

    def add_handler(self, handler):
        """
        handler(level: LogLevel, text: str)
        """
        self._handlers.append(handler)

    def log(self, level: LogLevel, msg: str):
        timestamp = time.strftime("%H:%M:%S")
        text = f"[{timestamp}] [{LEVEL_TEXT[level]}] {msg}"

        with self._lock:
            for h in self._handlers:
                try:
                    h(level, text)
                except Exception:
                    pass

    def debug(self, msg): self.log(LogLevel.DEBUG, msg)
    def info(self, msg): self.log(LogLevel.INFO, msg)
    def warn(self, msg): self.log(LogLevel.WARN, msg)
    def error(self, msg): self.log(LogLevel.ERROR, msg)
