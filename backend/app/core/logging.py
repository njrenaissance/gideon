"""Application logging configuration.

Configures the ``app`` logger as the root of the application hierarchy.
All modules use ``logging.getLogger(__name__)`` to get a child logger
that inherits this configuration automatically.
"""

import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

_NOISY_LOGGERS = ("uvicorn.access", "httpcore", "httpx", "hpack")


_STREAMS = {"stdout": sys.stdout, "stderr": sys.stderr}


def setup_logging(level: str = "INFO", output: str = "stdout") -> None:
    """Configure application logging.

    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        output: Stream target — "stdout" or "stderr".
    """
    app_logger = logging.getLogger("app")

    # Guard against duplicate handlers on repeated calls.
    if app_logger.handlers:
        return

    app_logger.setLevel(level.upper())

    stream = _STREAMS.get(output.lower(), sys.stdout)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    app_logger.addHandler(handler)

    # Quiet noisy third-party loggers.
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
