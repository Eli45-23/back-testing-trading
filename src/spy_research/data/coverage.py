"""Read-only session inventory using the existing strict validation gates."""
from datetime import date, timedelta
from typing import Literal
from collections.abc import Iterator

from spy_research.events.break_and_hold_models import FrozenModel
from spy_research.data.validation import RawDataValidator
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.market import XNYSCalendar


class SessionCoverage(FrozenModel):
    session_date: date
    raw_status: Literal["VALID", "MISSING", "INVALID"]
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    expected_minutes: int
    observed_minutes: int
    processed_status: str = "NOT_CHECKED"


def trading_dates(start: date, end: date, calendar: XNYSCalendar) -> Iterator[date]:
    if start > end:
        raise ValueError("start must not exceed end")
    current = start
    while current <= end:
        if calendar.session_for_date(current).is_trading_day:
            yield current
        current += timedelta(days=1)


def inventory(config: ResearchConfig, raw_store: RawBarStore, start: date, end: date,
              processed_store: ProcessedFiveMinuteStore | None = None,
              calendar: XNYSCalendar | None = None) -> tuple[SessionCoverage, ...]:
    calendar = calendar or XNYSCalendar()
    validator = RawDataValidator(calendar)
    result = []
    for day in trading_dates(start, end, calendar):
        report = validator.validate_raw_store(raw_store, symbol=config.symbol, start_date=day, end_date=day)
        errors = tuple(sorted({i.code for i in report.issues if i.severity == "ERROR"}))
        status = "VALID" if report.passed else ("MISSING" if report.total_bars == 0 and "CORRUPTED_PARTITION" not in errors else "INVALID")
        processed = "NOT_CHECKED"
        if processed_store is not None and status == "VALID":
            from spy_research.bars.validation import ProcessedFiveMinuteValidator
            validation = ProcessedFiveMinuteValidator(calendar).validate_store(
                processed_store, start=day, end=day, reconcile=True, config=config, raw_store=raw_store)
            processed = "VALID" if validation.passed else "MISSING_OR_INVALID"
        elif processed_store is not None:
            processed = "UNVERIFIABLE_RAW_INVALID"
        result.append(SessionCoverage(session_date=day, raw_status=status, errors=errors,
            warnings=tuple(sorted({i.code for i in report.issues if i.severity == "WARNING"})),
            expected_minutes=report.expected_rth_bars, observed_minutes=report.observed_rth_bars, processed_status=processed))
    return tuple(result)
