"""Logging setup.

Thin, dependency-light wrapper around the standard :mod:`logging` module that
provides a single configuration entry point (:func:`configure_logging`) and a
convenient factory (:func:`get_logger`).

This is infrastructure, not simulation logic: it standardizes how the rest of
the project emits diagnostics.
"""

from __future__ import annotations

import logging
import sys
from typing import Final

_DEFAULT_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DEFAULT_DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"

# Guard so repeated calls don't attach duplicate handlers.
_configured: bool = False


def configure_logging(
    level: str | int = "INFO",
    *,
    to_file: bool = False,
    log_dir: str = "logs",
) -> None:
    """Configure the root logger for the application.

    Idempotent: calling it more than once is a no-op after the first call.

    Args:
        level: Minimum level to emit (name or numeric value).
        to_file: If True, also write logs to a rotating file in ``log_dir``.
        log_dir: Directory for log files when ``to_file`` is enabled.
    """
    global _configured
    if _configured:
        return

    handlers: list[logging.Handler] = [logging.StreamHandler(stream=sys.stdout)]

    # TODO: When to_file is True, create ``log_dir`` and attach a
    #       RotatingFileHandler (kept out of the skeleton to avoid I/O).
    _ = (to_file, log_dir)

    logging.basicConfig(
        level=level,
        format=_DEFAULT_FORMAT,
        datefmt=_DEFAULT_DATEFMT,
        handlers=handlers,
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, configuring logging on first use.

    Args:
        name: Logger name, conventionally ``__name__`` of the caller.

    Returns:
        A configured :class:`logging.Logger`.
    """
    if not _configured:
        configure_logging()
    return logging.getLogger(name)
