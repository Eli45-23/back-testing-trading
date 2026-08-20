"""Deterministic true range and daily-reset Wilder ATR calculations."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext

from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.bars.validation import ProcessedFiveMinuteValidator
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators.ema import (
    IndicatorInputValidationError,
    IndicatorSequenceError,
)
from spy_research.indicators.models import (
    AtrCalculationResult,
    AtrSessionSummary,
    FiveMinuteAtrRow,
)


ATR_PERIOD = 14
ATR_DECIMAL_PRECISION = 50
ATR_CONTEXT = Context(prec=ATR_DECIMAL_PRECISION, rounding=ROUND_HALF_EVEN)


def _validate_single_session(bars: Sequence[FiveMinuteBar]) -> None:
    if not bars:
        return
    session_date = bars[0].session_date
    previous_timestamp = None
    seen_timestamps = set()
    for bar in bars:
        if bar.session_date != session_date:
            raise IndicatorSequenceError("Single-session ATR input mixes session dates")
        if bar.session_type != "RTH":
            raise IndicatorSequenceError("ATR input must contain only RTH bars")
        if bar.timeframe != "5Min":
            raise IndicatorSequenceError("ATR input timeframe must be 5Min")
        if bar.session_mode != "RTH_ONLY":
            raise IndicatorSequenceError("ATR input session mode must be RTH_ONLY")
        if bar.timestamp in seen_timestamps:
            raise IndicatorSequenceError("ATR input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("ATR input must be strictly chronological")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp


def calculate_true_ranges(
    bars: Sequence[FiveMinuteBar],
) -> tuple[Decimal, ...]:
    """Return one true range per bar using only the same-session previous close."""

    _validate_single_session(bars)
    if not bars:
        return ()

    ranges: list[Decimal] = []
    with localcontext(ATR_CONTEXT):
        previous_close: Decimal | None = None
        for bar in bars:
            intrabar_range = bar.high - bar.low
            if previous_close is None:
                true_range = intrabar_range
            else:
                true_range = max(
                    intrabar_range,
                    abs(bar.high - previous_close),
                    abs(bar.low - previous_close),
                )
            ranges.append(true_range)
            previous_close = bar.close
    return tuple(ranges)


def calculate_wilder_atr(
    true_ranges: Sequence[Decimal],
    period: int = ATR_PERIOD,
) -> tuple[Decimal | None, ...]:
    """SMA-seed a Wilder ATR, then apply the recursive Wilder recurrence."""

    if period <= 0:
        raise ValueError("ATR period must be positive")
    if any(
        not isinstance(value, Decimal) or not value.is_finite() or value < 0
        for value in true_ranges
    ):
        raise ValueError("True ranges must be finite non-negative Decimal values")

    output: list[Decimal | None] = [None] * len(true_ranges)
    if len(true_ranges) < period:
        return tuple(output)

    with localcontext(ATR_CONTEXT):
        divisor = Decimal(period)
        multiplier = Decimal(period - 1)
        seed = sum(true_ranges[:period], Decimal(0)) / divisor
        output[period - 1] = seed
        previous = seed
        for index in range(period, len(true_ranges)):
            current = (previous * multiplier + true_ranges[index]) / divisor
            output[index] = current
            previous = current
    return tuple(output)


def calculate_session_atr(
    bars: Sequence[FiveMinuteBar],
) -> tuple[FiveMinuteAtrRow, ...]:
    """Calculate true range and Wilder ATR for exactly one RTH session."""

    true_ranges = calculate_true_ranges(bars)
    values = calculate_wilder_atr(true_ranges)
    return tuple(
        FiveMinuteAtrRow(
            symbol=bar.symbol,
            timestamp=bar.timestamp,
            session_date=bar.session_date,
            true_range=true_ranges[index],
            atr14=values[index],
        )
        for index, bar in enumerate(bars)
    )


def calculate_atr_sessions(
    bars: Sequence[FiveMinuteBar],
) -> tuple[FiveMinuteAtrRow, ...]:
    """Group chronological bars by date and reset TR/ATR state every session."""

    previous_timestamp = None
    seen_timestamps = set()
    grouped: dict[date, list[FiveMinuteBar]] = defaultdict(list)
    for bar in bars:
        if bar.timestamp in seen_timestamps:
            raise IndicatorSequenceError("ATR input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("ATR input must be strictly chronological")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp
        grouped[bar.session_date].append(bar)

    rows: list[FiveMinuteAtrRow] = []
    for session_bars in grouped.values():
        rows.extend(calculate_session_atr(session_bars))
    return tuple(rows)


class AtrIndicatorService:
    """Validate/reconcile processed bars, then calculate daily-reset ATR14."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store

    def calculate(self, *, start: date, end: date) -> AtrCalculationResult:
        report = ProcessedFiveMinuteValidator().validate_store(
            self._processed_store,
            start=start,
            end=end,
            reconcile=True,
            config=self._config,
            raw_store=self._raw_store,
        )
        if not report.passed:
            raise IndicatorInputValidationError(report)
        bars = self._processed_store.load_processed_5m_bars(
            symbol=self._config.symbol,
            start=start,
            end=end,
            session_mode="RTH_ONLY",
        )
        rows = calculate_atr_sessions(bars)
        grouped: dict[date, list[FiveMinuteAtrRow]] = defaultdict(list)
        for row in rows:
            grouped[row.session_date].append(row)
        summaries = tuple(
            AtrSessionSummary(
                session_date=session_date,
                bars=len(session_rows),
                valid_rows=sum(row.atr14 is not None for row in session_rows),
                first_valid_timestamp=next(
                    (row.timestamp for row in session_rows if row.atr14 is not None),
                    None,
                ),
                first_atr14=next(
                    (row.atr14 for row in session_rows if row.atr14 is not None),
                    None,
                ),
                final_atr14=session_rows[-1].atr14 if session_rows else None,
            )
            for session_date, session_rows in grouped.items()
        )
        return AtrCalculationResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            rows=rows,
            sessions=summaries,
            processed_validation=report,
        )
