"""Explicit Decimal EMA9/EMA20 calculations with daily RTH resets."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext

from spy_research.bars.models import FiveMinuteBar
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.bars.validation import (
    ProcessedFiveMinuteValidator,
    ProcessedValidationReport,
)
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators.models import (
    EmaCalculationResult,
    EmaSessionSummary,
    FiveMinuteIndicatorRow,
)


EMA_DECIMAL_PRECISION = 50
EMA_CONTEXT = Context(prec=EMA_DECIMAL_PRECISION, rounding=ROUND_HALF_EVEN)


class IndicatorSequenceError(ValueError):
    """Five-minute bars do not form a valid indicator input sequence."""


class IndicatorInputValidationError(ValueError):
    """Processed validation failed, blocking indicator calculation."""

    def __init__(self, report: ProcessedValidationReport) -> None:
        self.report = report
        super().__init__(
            "Processed five-minute validation failed; indicator calculation is blocked "
            f"({report.error_count} errors)"
        )


def calculate_ema(
    prices: Sequence[Decimal],
    period: int,
) -> tuple[Decimal | None, ...]:
    """Return SMA-seeded EMA positions without mutating or rounding inputs."""

    if period <= 0:
        raise ValueError("EMA period must be positive")
    if any(not isinstance(price, Decimal) or not price.is_finite() for price in prices):
        raise ValueError("EMA prices must be finite Decimal values")

    output: list[Decimal | None] = [None] * len(prices)
    if len(prices) < period:
        return tuple(output)

    with localcontext(EMA_CONTEXT):
        alpha = Decimal(2) / Decimal(period + 1)
        seed = sum(prices[:period], Decimal(0)) / Decimal(period)
        output[period - 1] = seed
        previous = seed
        for index in range(period, len(prices)):
            current = alpha * prices[index] + (Decimal(1) - alpha) * previous
            output[index] = current
            previous = current
    return tuple(output)


def calculate_session_ema(
    bars: Sequence[FiveMinuteBar],
) -> tuple[FiveMinuteIndicatorRow, ...]:
    """Calculate EMA9/EMA20 for exactly one chronological RTH session."""

    if not bars:
        return ()
    session_date = bars[0].session_date
    previous_timestamp = None
    seen_timestamps = set()
    for bar in bars:
        if bar.session_date != session_date:
            raise IndicatorSequenceError("Single-session EMA input mixes session dates")
        if bar.session_type != "RTH":
            raise IndicatorSequenceError("EMA input must contain only RTH bars")
        if bar.timeframe != "5Min":
            raise IndicatorSequenceError("EMA input timeframe must be 5Min")
        if bar.session_mode != "RTH_ONLY":
            raise IndicatorSequenceError("EMA input session mode must be RTH_ONLY")
        if bar.timestamp in seen_timestamps:
            raise IndicatorSequenceError("EMA input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("EMA input must be strictly chronological")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp

    closes = tuple(bar.close for bar in bars)
    ema9 = calculate_ema(closes, 9)
    ema20 = calculate_ema(closes, 20)
    return tuple(
        FiveMinuteIndicatorRow(
            symbol=bar.symbol,
            timestamp=bar.timestamp,
            session_date=bar.session_date,
            close=bar.close,
            ema9=ema9[index],
            ema20=ema20[index],
        )
        for index, bar in enumerate(bars)
    )


def calculate_ema_sessions(
    bars: Sequence[FiveMinuteBar],
) -> tuple[FiveMinuteIndicatorRow, ...]:
    """Group chronological bars by session and reset EMA state for each group."""

    previous_timestamp = None
    seen_timestamps = set()
    grouped: dict[date, list[FiveMinuteBar]] = defaultdict(list)
    for bar in bars:
        if bar.timestamp in seen_timestamps:
            raise IndicatorSequenceError("EMA input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("EMA input must be strictly chronological")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp
        grouped[bar.session_date].append(bar)

    rows: list[FiveMinuteIndicatorRow] = []
    for session_bars in grouped.values():
        rows.extend(calculate_session_ema(session_bars))
    return tuple(rows)


class EmaIndicatorService:
    """Validate/reconcile processed bars, then calculate session-reset EMAs."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store

    def calculate(self, *, start: date, end: date) -> EmaCalculationResult:
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
        rows = calculate_ema_sessions(bars)
        grouped: dict[date, list[FiveMinuteIndicatorRow]] = defaultdict(list)
        for row in rows:
            grouped[row.session_date].append(row)
        summaries = tuple(
            EmaSessionSummary(
                session_date=session_date,
                bars=len(session_rows),
                ema9_valid_rows=sum(row.ema9 is not None for row in session_rows),
                ema20_valid_rows=sum(row.ema20 is not None for row in session_rows),
                first_ema9_timestamp=next(
                    (row.timestamp for row in session_rows if row.ema9 is not None),
                    None,
                ),
                first_ema20_timestamp=next(
                    (row.timestamp for row in session_rows if row.ema20 is not None),
                    None,
                ),
            )
            for session_date, session_rows in grouped.items()
        )
        return EmaCalculationResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            rows=rows,
            sessions=summaries,
            processed_validation=report,
        )
