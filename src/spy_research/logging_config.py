"""Reusable console logging configuration with credential redaction."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterable


_SENSITIVE_ENVIRONMENT_VARIABLES = ("ALPACA_API_KEY", "ALPACA_SECRET_KEY")
_REGISTERED_SENSITIVE_VALUES: set[str] = set()


def register_sensitive_values(values: Iterable[str]) -> None:
    """Register secrets loaded from sources that do not modify ``os.environ``."""

    _REGISTERED_SENSITIVE_VALUES.update(value for value in values if value)


def redact_sensitive_text(value: str) -> str:
    """Mask registered and environment-provided credentials in text."""

    environment_values = {
        secret
        for variable in _SENSITIVE_ENVIRONMENT_VARIABLES
        if (secret := os.getenv(variable))
    }
    for sensitive_value in _REGISTERED_SENSITIVE_VALUES | environment_values:
        value = value.replace(sensitive_value, "**********")
    return value


class RedactingFormatter(logging.Formatter):
    """Format log records while masking known credential values."""

    def __init__(self, fmt: str, datefmt: str | None = None) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        return redact_sensitive_text(super().format(record))


def configure_logging(level: str | int = "INFO") -> None:
    """Configure concise timestamped console logs for the application."""

    handler = logging.StreamHandler()
    handler.setFormatter(
        RedactingFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
