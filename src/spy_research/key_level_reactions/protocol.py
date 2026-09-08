"""Predeclared V1 constants. Changes require a new reviewed protocol."""
from datetime import UTC, date, timedelta
from decimal import Context, Decimal, ROUND_HALF_EVEN
from zoneinfo import ZoneInfo

VERSION = "key-level-reactions-v1"
OUTCOME_START = date(2026, 1, 2)
OUTCOME_END = date(2026, 9, 4)
DISTANCES = (Decimal("0.25"), Decimal("0.50"), Decimal("1.00"))
HORIZONS = (5, 15, 30)
EPISODE_MINUTES = 30
# Reporting-only reproducibility settings, never selection criteria.
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20260907
CONTEXT = Context(prec=50, rounding=ROUND_HALF_EVEN)
NY = ZoneInfo("America/New_York")


def timestamp_id(timestamp):
    return timestamp.astimezone(UTC).isoformat()


def minute_sequence(bars):
    """Validate primitive inputs, even when a caller bypasses the study facade."""
    bars = tuple(bars)
    for b in bars:
        day = b.timestamp.astimezone(NY).date()
        guard_dates(day, day)
        if b.timestamp.second or b.timestamp.microsecond:
            raise ValueError("Minute-start timestamps required")
        if any(not isinstance(v, Decimal) or not v.is_finite() or v <= 0
               for v in (b.open, b.high, b.low, b.close)):
            raise ValueError("Invalid exact prices")
        if b.high < max(b.open, b.close, b.low) or b.low > min(b.open, b.close, b.high):
            raise ValueError("Invalid OHLC")
    if any(a.timestamp >= b.timestamp for a,b in zip(bars,bars[1:])):
        raise ValueError("Duplicate/unordered minutes")
    return bars


def outcome_window(ep, bars, horizon):
    """Missing data is an error; only a declared session-close boundary censors."""
    guard_outcomes(ep.start.astimezone(NY).date(), ep.start.astimezone(NY).date())
    bars = minute_sequence(bars)
    end = min(ep.end, ep.start + timedelta(minutes=horizon))
    selected = tuple(b for b in bars if ep.start <= b.timestamp < end)
    expected = int((end-ep.start).total_seconds() // 60)
    if len(selected) != expected or any(b.timestamp != ep.start+timedelta(minutes=i)
                                       for i,b in enumerate(selected)):
        raise ValueError("Missing outcome minutes; not administrative censoring")
    return selected


def guard_dates(start, end):
    if start > end or end > OUTCOME_END:
        raise ValueError("Invalid range or protected prospective date")


def guard_outcomes(start, end):
    guard_dates(start, end)
    if start < OUTCOME_START:
        raise ValueError("Context is not an outcome population")
