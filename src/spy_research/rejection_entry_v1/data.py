"""Local-only study boundary and input validation.

The loader hook is intentionally dependency-injected.  This package never
constructs an HTTP client and cannot silently fetch missing historical data.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from .models import MinuteBar
from .protocol import OUTCOME_END, OUTCOME_START, guard_outcome_range


def validate_local_root(root: str | Path) -> Path:
    value = str(root)
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        raise ValueError("Rejection Entry V1 accepts local paths only")
    path = Path(root).expanduser()
    if not path.is_absolute():
        raise ValueError("local data root must be an absolute path")
    return path


def validate_scope(context_start: date, outcome_start: date, outcome_end: date) -> None:
    if context_start > outcome_start:
        raise ValueError("context must begin on or before outcome window")
    guard_outcome_range(outcome_start, outcome_end)
    if outcome_end > OUTCOME_END:
        raise ValueError("post-September-4 outcomes are prohibited")


def load_after_scope_guard(
    reader: Callable[[date, date, date], Iterable[MinuteBar]],
    *,
    context_start: date,
    outcome_start: date,
    outcome_end: date,
) -> tuple[MinuteBar, ...]:
    """Call a local reader only after all date checks have passed."""
    validate_scope(context_start, outcome_start, outcome_end)
    values = tuple(reader(context_start, outcome_start, outcome_end))
    validate_bars(values, outcome_start=outcome_start, outcome_end=outcome_end)
    return values


def validate_bars(
    bars: Iterable[MinuteBar], *, outcome_start: date, outcome_end: date
) -> tuple[MinuteBar, ...]:
    """Reject duplicates, future outcomes, and non-chronological inputs."""
    guard_outcome_range(outcome_start, outcome_end)
    values = tuple(bars)
    previous: datetime | None = None
    for bar in values:
        if bar.session_date > outcome_end:
            raise ValueError("outcome bar after September 4, 2026")
        if previous is not None and bar.timestamp <= previous:
            raise ValueError("duplicate or unordered local bars")
        previous = bar.timestamp
    return values
