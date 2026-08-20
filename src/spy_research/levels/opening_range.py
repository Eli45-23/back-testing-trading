"""Opening five-minute high and low from validated Stage 2 RTH candles."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta

from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.bars.validation import ProcessedFiveMinuteValidator
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.data.validation import ValidationSeverity
from spy_research.levels.models import (
    OpeningFiveMinuteLevels,
    OpeningFiveMinuteLevelsResult,
)
from spy_research.market import XNYSCalendar


class OpeningRangeLevelError(ValueError):
    """Base error for safely rejected opening-range construction."""


class OpeningRangeLevelInputError(OpeningRangeLevelError):
    """Processed bars do not describe a valid chronological RTH session."""


class OpeningRangeLevelValidationError(OpeningRangeLevelError):
    """Persisted Stage 2 bars failed validation or raw reconciliation."""


def calculate_opening_five_minute_levels(
    session_5m_bars: Sequence[FiveMinuteBar],
    *,
    calendar: XNYSCalendar | None = None,
) -> OpeningFiveMinuteLevels:
    """Select the calendar-aligned first completed RTH five-minute candle."""

    if not session_5m_bars:
        raise OpeningRangeLevelInputError("Opening-range input cannot be empty")

    active_calendar = calendar or XNYSCalendar()
    session_date: date | None = None
    previous_timestamp = None
    seen_timestamps = set()

    for bar in session_5m_bars:
        if (
            bar.symbol != "SPY"
            or bar.source != "alpaca"
            or bar.feed != "sip"
            or bar.source_timeframe != "1Min"
            or bar.timeframe != "5Min"
            or bar.adjustment != "raw"
            or bar.source_bar_count != 5
            or bar.session_type != "RTH"
            or bar.session_mode != "RTH_ONLY"
            or bar.aggregation_method != "rth_1m_to_5m_v1"
        ):
            raise OpeningRangeLevelInputError(
                "Opening-range levels require self-built SPY RTH_ONLY 5Min bars"
            )
        if bar.timestamp in seen_timestamps:
            raise OpeningRangeLevelInputError(
                "Duplicate timestamps are not allowed in an RTH session"
            )
        if previous_timestamp is not None and bar.timestamp < previous_timestamp:
            raise OpeningRangeLevelInputError(
                "Opening-range bars must be strictly chronological"
            )
        if session_date is None:
            session_date = bar.session_date
        elif bar.session_date != session_date:
            raise OpeningRangeLevelInputError(
                "Opening-range input cannot mix session dates"
            )
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp

    assert session_date is not None
    session = active_calendar.session_for_date(session_date)
    if not session.is_trading_day or session.market_open is None:
        raise OpeningRangeLevelInputError(
            "Opening-range session date must be an XNYS trading session"
        )
    first = session_5m_bars[0]
    if first.timestamp != session.market_open:
        raise OpeningRangeLevelInputError(
            "First five-minute bar must start at the XNYS session open"
        )

    return OpeningFiveMinuteLevels(
        session_date=session_date,
        orh5=first.high,
        orl5=first.low,
        source_timestamp=first.timestamp,
        available_from_timestamp=first.timestamp + timedelta(minutes=5),
    )


class OpeningFiveMinuteLevelsService:
    """Validate/reconcile Stage 2 data, then derive opening ranges in memory."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
        validator: ProcessedFiveMinuteValidator | None = None,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store
        self._calendar = calendar or XNYSCalendar()
        self._validator = validator or ProcessedFiveMinuteValidator(self._calendar)

    def calculate(self, *, start: date, end: date) -> OpeningFiveMinuteLevelsResult:
        if start > end:
            raise ValueError("start date must be on or before end date")

        validation = self._validator.validate_store(
            self._processed_store,
            start=start,
            end=end,
            reconcile=True,
            config=self._config,
            raw_store=self._raw_store,
        )
        if not validation.passed:
            error_codes = sorted(
                {
                    issue.code
                    for issue in validation.issues
                    if issue.severity == ValidationSeverity.ERROR
                }
            )
            rendered_codes = ", ".join(error_codes) or "UNKNOWN_VALIDATION_ERROR"
            raise OpeningRangeLevelValidationError(
                "Processed five-minute validation/reconciliation failed: "
                f"{rendered_codes}"
            )

        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        by_session: dict[date, list[FiveMinuteBar]] = {}
        for bar in bars:
            by_session.setdefault(bar.session_date, []).append(bar)

        levels = []
        for session_date in sorted(by_session):
            levels.append(
                calculate_opening_five_minute_levels(
                    tuple(by_session[session_date]),
                    calendar=self._calendar,
                )
            )
        return OpeningFiveMinuteLevelsResult(
            start_date=start,
            end_date=end,
            levels=tuple(levels),
        )
