"""Deterministic previous-XNYS-session PDH, PDL, and PDC construction."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta

from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.data.validation import RawDataValidator, ValidationSeverity
from spy_research.levels.models import (
    MissingPreviousDaySource,
    PreviousDayLevels,
    PreviousDayLevelsResult,
    PreviousSessionLevelValues,
)
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar


class PreviousDayLevelError(ValueError):
    """Base error for safely rejected previous-day level construction."""


class PreviousDayLevelInputError(PreviousDayLevelError):
    """Raw bars do not describe exactly one valid chronological RTH session."""


class PreviousDayLevelValidationError(PreviousDayLevelError):
    """A locally present source session failed the raw-data validation gate."""


def calculate_previous_session_levels(
    source_rth_bars: Sequence[RawBarRecord],
    *,
    calendar: XNYSCalendar | None = None,
) -> PreviousSessionLevelValues:
    """Calculate PDH/PDL/PDC source values from one chronological RTH session."""

    if not source_rth_bars:
        raise PreviousDayLevelInputError("Previous-session RTH bars cannot be empty")

    active_calendar = calendar or XNYSCalendar()
    classifier = MarketSessionClassifier(active_calendar)
    expected_symbol = source_rth_bars[0].symbol
    source_date: date | None = None
    previous_timestamp = None
    seen_timestamps = set()

    for bar in source_rth_bars:
        if (
            bar.symbol != "SPY"
            or bar.source != "alpaca"
            or bar.feed != "sip"
            or bar.timeframe != "1Min"
            or bar.adjustment != "raw"
        ):
            raise PreviousDayLevelInputError(
                "Previous-day levels require SPY Alpaca SIP raw 1Min bars"
            )
        if bar.timestamp in seen_timestamps:
            raise PreviousDayLevelInputError(
                "Duplicate timestamps are not allowed in a source session"
            )
        if previous_timestamp is not None and bar.timestamp < previous_timestamp:
            raise PreviousDayLevelInputError(
                "Source-session bars must be strictly chronological"
            )
        classified = classifier.classify(bar)
        if classified.session_type is not SessionType.RTH:
            raise PreviousDayLevelInputError(
                "Previous-day levels accept only XNYS RTH bars"
            )
        if source_date is None:
            source_date = classified.session_date
        elif classified.session_date != source_date:
            raise PreviousDayLevelInputError(
                "Previous-day level input cannot mix session dates"
            )
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp

    assert source_date is not None
    high_bar = source_rth_bars[0]
    low_bar = source_rth_bars[0]
    for bar in source_rth_bars[1:]:
        if bar.high > high_bar.high:
            high_bar = bar
        if bar.low < low_bar.low:
            low_bar = bar
    final_bar = source_rth_bars[-1]

    return PreviousSessionLevelValues(
        symbol=expected_symbol,
        source_session_date=source_date,
        pdh=high_bar.high,
        pdl=low_bar.low,
        pdc=final_bar.close,
        pdh_source_timestamp=high_bar.timestamp,
        pdl_source_timestamp=low_bar.timestamp,
        pdc_source_timestamp=final_bar.timestamp,
    )


def next_xnys_session_date(
    source_session_date: date,
    *,
    calendar: XNYSCalendar | None = None,
) -> date:
    """Map one XNYS source session to the next XNYS trading session."""

    active_calendar = calendar or XNYSCalendar()
    if not active_calendar.session_for_date(source_session_date).is_trading_day:
        raise PreviousDayLevelInputError("Source date must be an XNYS trading session")
    candidate = source_session_date + timedelta(days=1)
    while not active_calendar.session_for_date(candidate).is_trading_day:
        candidate += timedelta(days=1)
    return candidate


def map_source_levels_to_next_session(
    source: PreviousSessionLevelValues,
    *,
    calendar: XNYSCalendar | None = None,
) -> PreviousDayLevels:
    """Attach source values to their next XNYS session without recalculation."""

    return PreviousDayLevels(
        **source.model_dump(),
        session_date=next_xnys_session_date(
            source.source_session_date,
            calendar=calendar,
        ),
    )


def _previous_xnys_session_date(
    target_session_date: date,
    calendar: XNYSCalendar,
) -> date:
    if not calendar.session_for_date(target_session_date).is_trading_day:
        raise PreviousDayLevelInputError("Target date must be an XNYS trading session")
    candidate = target_session_date - timedelta(days=1)
    while not calendar.session_for_date(candidate).is_trading_day:
        candidate -= timedelta(days=1)
    return candidate


def _date_range(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


class PreviousDayLevelsService:
    """Build previous-day levels from validated local raw data without writes."""

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

    def calculate(self, *, start: date, end: date) -> PreviousDayLevelsResult:
        if start > end:
            raise ValueError("start date must be on or before end date")

        levels = []
        missing = []
        for target_date in _date_range(start, end):
            if not self._calendar.session_for_date(target_date).is_trading_day:
                continue
            source_date = _previous_xnys_session_date(target_date, self._calendar)
            source_partition = self._raw_store.load_partition(source_date)
            if not source_partition:
                missing.append(
                    MissingPreviousDaySource(
                        session_date=target_date,
                        source_session_date=source_date,
                    )
                )
                continue

            report = self._validator.validate_raw_bars(
                source_partition,
                symbol=self._config.symbol,
                start_date=source_date,
                end_date=source_date,
                partition_dates=(source_date,) * len(source_partition),
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
                raise PreviousDayLevelValidationError(
                    f"Raw source session {source_date.isoformat()} failed validation: "
                    f"{rendered_codes}"
                )

            rth_bars = tuple(
                item.bar
                for item in self._classifier.classify_many(source_partition)
                if item.session_date == source_date
                and item.session_type is SessionType.RTH
            )
            source = calculate_previous_session_levels(
                rth_bars,
                calendar=self._calendar,
            )
            mapped = map_source_levels_to_next_session(
                source,
                calendar=self._calendar,
            )
            if mapped.session_date != target_date:
                raise PreviousDayLevelError(
                    "Previous-session mapping did not resolve to the target session"
                )
            levels.append(mapped)

        return PreviousDayLevelsResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            levels=tuple(levels),
            missing_sources=tuple(missing),
        )
