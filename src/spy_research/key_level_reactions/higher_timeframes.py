"""Only full, session-open-anchored hours; no overnight aggregation."""
from datetime import timedelta

from spy_research.market import XNYSCalendar
from .models import Hour


def hours(bars, calendar=None):
    calendar = calendar or XNYSCalendar()
    from .protocol import NY, minute_sequence, timestamp_id
    bars = minute_sequence(bars)
    result = []
    by_time = {b.timestamp: b for b in bars}
    if len(by_time) != len(bars):
        raise ValueError("Duplicate minutes")
    for day in sorted({b.timestamp.astimezone(NY).date() for b in bars}):
        s = calendar.session_for_date(day)
        if not s.is_trading_day:
            continue
        start = s.market_open
        while start + timedelta(hours=1) <= s.market_close:
            timestamps = tuple(start + timedelta(minutes=i) for i in range(60))
            if any(t not in by_time for t in timestamps):
                raise ValueError("Missing hour source minute; pivot sequence cannot bridge gap")
            source = [by_time[t] for t in timestamps]
            result.append(Hour(id=timestamp_id(start), start=start, end=start + timedelta(hours=1),
                high=max(b.high for b in source), low=min(b.low for b in source),
                source_ids=tuple(timestamp_id(t) for t in timestamps)))
            start += timedelta(hours=1)
    return tuple(result)
