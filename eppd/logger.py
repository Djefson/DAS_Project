"""Logging configuration for EPPD.

Provides a single entry point, get_logger(), that returns a logger with a
colored console handler when stdout is a TTY and plain formatting otherwise.
"""

import logging
import sys


class LogColors:
    """ANSI color codes for colored terminal output."""
    RESET = '\033[0m'

    DEBUG = '\033[36m'      # Cyan
    INFO = '\033[32m'       # Green
    WARNING = '\033[33m'    # Yellow
    ERROR = '\033[31m'      # Red
    CRITICAL = '\033[35m'   # Magenta


class ColoredFormatter(logging.Formatter):
    """Logging formatter that adds colors to terminal output."""

    _COLORS = {
        logging.DEBUG: LogColors.DEBUG,
        logging.INFO: LogColors.INFO,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.ERROR,
        logging.CRITICAL: LogColors.CRITICAL,
    }

    def __init__(self):
        super().__init__()
        self._formatters = {
            level: logging.Formatter(
                f'{color}%(levelname)-8s{LogColors.RESET} | %(message)s'
            )
            for level, color in self._COLORS.items()
        }
        self._fallback = logging.Formatter('%(levelname)-8s | %(message)s')

    def format(self, record):
        return self._formatters.get(record.levelno, self._fallback).format(record)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance configured for EPPD.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger with a console handler attached. Subsequent calls with the
        same name return the same instance without adding handlers.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    if sys.stdout.isatty():
        handler.setFormatter(ColoredFormatter())
    else:
        handler.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))

    logger.addHandler(handler)
    return logger
