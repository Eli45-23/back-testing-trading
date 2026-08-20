"""Deterministic same-day premarket high and low construction."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta
from typing import Literal

from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.data.validation import RawDataValidator, ValidationSeverity
from spy_research.levels.models import PremarketLevels, PremarketLevelsResult
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar


class PremarketLevelError(ValueError):
    """Base error for safely rejected premarket-level construction."""


class PremarketLevelInputError(PremarketLevelError):
    """Bars do not describe exactly one chronological premarket session."""


class PremarketLevelUnavailableError(PremarketLevelError):
    """A pure calculation received no premarket bars."""


class PremarketLevelValidationError(PremarketLevelError):
    """A locally present target partition failed the raw-data validation gate."""


def calculate_premarket_levels(
    premarket_bars: Sequence[RawBarRecord],
    *,
    calendar: XNYSCalendar | None = None,
) -> PremarketLevels:
    """Calculate PMH/PML from one chronological same-day PREMARKET sequence."""

    if not premarket_bars:
        raise PremarketLevelUnavailableError("No premarket bars were provided")

    active_calendar = calendar or XNYSCalendar()
    classifier = MarketSessionClassifier(active_calendar)
    session_date: date | None = None
    previous_timestamp = None
    seen_timestamps = set()

    for bar in premarket_bars:
        if (
            bar.symbol != "SPY"
            or bar.source != "alpaca"
            or bar.feed != "sip"
            or bar.timeframe != "1Min"
            or bar.adjustment != "raw"
        ):
            raise PremarketLevelInputError(
                "Premarket levels require SPY Alpaca SIP raw 1Min bars"
            )
        if bar.timestamp in seen_timestamps:
            raise PremarketLevelInputError(
                "Duplicate timestamps are not allowed in a premarket session"
            )
        if previous_timestamp is not None and bar.timestamp < previous_timestamp:
            raise PremarketLevelInputError(
                "Premarket bars must be strictly chronological"
            )
        classified = classifier.classify(bar)
        if classified.session_type is not SessionType.PREMARKET:
            raise PremarketLevelInputError(
                "Premarket levels accept only same-day PREMARKET bars"
            )
        if session_date is None:
            session_date = classified.session_date
        elif classified.session_date != session_date:
            raise PremarketLevelInputError("Premarket input cannot mix session dates")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp

    assert session_date is not None
    high_bar = premarket_bars[0]
    low_bar = premarket_bars[0]
    for bar in premarket_bars[1:]:
        if bar.high > high_bar.high:
            high_bar = bar
        if bar.low < low_bar.low:
            low_bar = bar

    return PremarketLevels(
        session_date=session_date,
        pmh=high_bar.high,
        pml=low_bar.low,
        pmh_source_timestamp=high_bar.timestamp,
        pml_source_timestamp=low_bar.timestamp,
        source_bar_count=len(premarket_bars),
        status="AVAILABLE",
    )


def _unavailable(
    session_date: date,
    status: Literal["NO_PREMARKET_DATA", "MISSING_RAW_SESSION"],
) -> PremarketLevels:
    return PremarketLevels(
        session_date=session_date,
        pmh=None,
        pml=None,
        pmh_source_timestamp=None,
        pml_source_timestamp=None,
        source_bar_count=0,
        status=status,
    )


def _date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


class PremarketLevelsService:
    """Build finalized PMH/PML from validated local raw data without writes."""

    def __init__(
        self,
        config: ResearchConfig,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
        validator: RawDataValidator | None = None,
    ) -> None:
        self._config = config
        self._raw_store = raw_store
        self._calendar = calendar or XNYSCalendar()
        self._validator = validator or RawDataValidator(self._calendar)
        self._classifier = MarketSessionClassifier(self._calendar)

    def calculate(self, *, start: date, end: date) -> PremarketLevelsResult:
        if start > end:
            raise ValueError("start date must be on or before end date")

        levels = []
        for session_date in _date_range(start, end):
            if not self._calendar.session_for_date(session_date).is_trading_day:
                continue
            partition = self._raw_store.load_partition(session_date)
            if not partition:
                levels.append(_unavailable(session_date, "MISSING_RAW_SESSION"))
                continue

            report = self._validator.validate_raw_bars(
                partition,
                symbol=self._config.symbol,
                start_date=session_date,
                end_date=session_date,
                partition_dates=(session_date,) * len(partition),
            )
            if not report.passed:
                error_codes = sorted(
                    {
                        issue.code
                        for issue in report.issues
                        if issue.severity == ValidationSeverity.ERROR
                    }
                )
                rendered_codes = ", ".join(error_codes) or "UNKNOWN_VALIDATION_ERROR"
                raise PremarketLevelValidationError(
                    f"Raw target session {session_date.isoformat()} failed validation: "
                    f"{rendered_codes}"
                )

            premarket = tuple(
                item.bar
                for item in self._classifier.classify_many(partition)
                if item.session_date == session_date
                and item.session_type is SessionType.PREMARKET
            )
            if not premarket:
                levels.append(_unavailable(session_date, "NO_PREMARKET_DATA"))
                continue
            levels.append(
                calculate_premarket_levels(premarket, calendar=self._calendar)
            )

        return PremarketLevelsResult(
            start_date=start,
            end_date=end,
            levels=tuple(levels),
        )
