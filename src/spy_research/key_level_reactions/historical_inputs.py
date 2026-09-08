"""Local partition reads only; guards execute before any store access."""
from datetime import timedelta

from spy_research.data.validation import RawDataValidator
from spy_research.market import XNYSCalendar

from .models import Coverage, InputData
from .protocol import NY, guard_dates, guard_outcomes, minute_sequence


def validate_bars(bars, context_start, outcome_start, end, calendar=None):
    guard_dates(context_start, end)
    guard_outcomes(outcome_start, end)
    if context_start > outcome_start:
        raise ValueError("Context must precede outcomes")
    bars = minute_sequence(bars)
    if any(not context_start <= b.timestamp.astimezone(NY).date() <= end for b in bars):
        raise ValueError("Out-of-range input")
    if any(a.timestamp >= b.timestamp for a, b in zip(bars, bars[1:])):
        raise ValueError("Duplicate or unordered input")
    calendar = calendar or XNYSCalendar()
    report = RawDataValidator(calendar).validate_raw_bars(
        bars, symbol="SPY", start_date=context_start, end_date=end,
        partition_dates=tuple(b.timestamp.astimezone(NY).date() for b in bars))
    if not report.passed:
        raise ValueError("Local raw validation failed: " + ",".join(sorted({i.code for i in report.issues if i.severity == "ERROR"})))
    coverage = []
    day = context_start
    while day <= end:
        session = calendar.session_for_date(day)
        if session.is_trading_day:
            rth = [b for b in bars if session.market_open <= b.timestamp < session.market_close]
            expected = int((session.market_close - session.market_open).total_seconds() // 60)
            if len(rth) != expected:
                raise ValueError("Incomplete RTH session")
            pm = [b for b in bars if b.timestamp.astimezone(NY).date() == day and 4 <= b.timestamp.astimezone(NY).hour and b.timestamp < session.market_open]
            coverage.append(Coverage(session=day, expected=expected, observed=len(rth), status="VALID",
                premarket_status="OBSERVED_NOT_COMPLETENESS_CERTIFIED" if pm else "UNAVAILABLE",
                warning_codes=tuple(sorted({i.code for i in report.issues if i.severity == "WARNING" and i.session_date in (None,day)}))))
        day += timedelta(days=1)
    return InputData(context_start=context_start, outcome_start=outcome_start, end=end, bars=bars, coverage=tuple(coverage))


def load_local(store, *, context_start, outcome_start, end, calendar=None):
    guard_dates(context_start, end)
    guard_outcomes(outcome_start, end)
    if context_start > outcome_start:
        raise ValueError("Invalid context boundary")
    bars = []
    day = context_start
    while day <= end:
        partition = store.load_partition(day)
        if any(b.timestamp.astimezone(NY).date() != day for b in partition):
            raise ValueError("Raw partition date mismatch")
        bars.extend(partition)
        day += timedelta(days=1)
    return validate_bars(bars, context_start, outcome_start, end, calendar)
