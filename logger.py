import logging
from logging import StreamHandler
from datetime import datetime


class StatusBarHandler(StreamHandler):
    def __init__(self, main_window):
        StreamHandler.__init__(self)
        self.mw = main_window

    def emit(self, record):
        text = self.format(record)
        self.mw.ui.statusBar().showMessage(text)


class Logger:
    def __init__(self, logger_name, main_window, min_level="warning"):
        self.level_dict = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        self._logger_name = logger_name
        self.mw = main_window
        self._level_int = self.level_dict.get(min_level, "warning")
        self._logger = logging.getLogger(self._logger_name)
        self._logger.setLevel(self._level_int)

        # Stream handler
        ch = logging.StreamHandler()
        ch.setLevel(self._level_int)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

        # Status bar handler
        sb = StatusBarHandler(self.mw)
        sb.setLevel(logging.INFO)
        sb.setFormatter(formatter)
        self._logger.addHandler(sb)

    def debug(self, text):
        self._logger.debug(text)

    def info(self, text):
        self._logger.info(text)

    def warning(self, text):
        self._logger.warning(text)

    def error(self, text):
        self._logger.error(text)

    def critical(self, text):
        self._logger.critical(text)
