"""Deterministic HLC3/volume daily RTH session VWAP calculations."""

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
    FiveMinuteVwapRow,
    VwapCalculationResult,
    VwapSessionSummary,
)


VWAP_DECIMAL_PRECISION = 50
VWAP_CONTEXT = Context(prec=VWAP_DECIMAL_PRECISION, rounding=ROUND_HALF_EVEN)


def calculate_session_vwap(
    bars: Sequence[FiveMinuteBar],
) -> tuple[FiveMinuteVwapRow, ...]:
    """Calculate cumulative HLC3/volume VWAP for exactly one RTH session."""

    if not bars:
        return ()
    session_date = bars[0].session_date
    previous_timestamp = None
    seen_timestamps = set()
    for bar in bars:
        if bar.session_date != session_date:
            raise IndicatorSequenceError("Single-session VWAP input mixes session dates")
        if bar.session_type != "RTH":
            raise IndicatorSequenceError("VWAP input must contain only RTH bars")
        if bar.timeframe != "5Min":
            raise IndicatorSequenceError("VWAP input timeframe must be 5Min")
        if bar.session_mode != "RTH_ONLY":
            raise IndicatorSequenceError("VWAP input session mode must be RTH_ONLY")
        if bar.timestamp in seen_timestamps:
            raise IndicatorSequenceError("VWAP input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("VWAP input must be strictly chronological")
        if bar.volume < 0:
            raise IndicatorSequenceError("VWAP input volume must be non-negative")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp

    rows: list[FiveMinuteVwapRow] = []
    with localcontext(VWAP_CONTEXT):
        cumulative_pv = Decimal(0)
        cumulative_volume = 0
        for bar in bars:
            typical_price = (bar.high + bar.low + bar.close) / Decimal(3)
            cumulative_pv += typical_price * Decimal(bar.volume)
            cumulative_volume += bar.volume
            vwap = (
                cumulative_pv / Decimal(cumulative_volume)
                if cumulative_volume > 0
                else None
            )
            rows.append(
                FiveMinuteVwapRow(
                    symbol=bar.symbol,
                    timestamp=bar.timestamp,
                    session_date=bar.session_date,
                    typical_price=typical_price,
                    vwap=vwap,
                )
            )
    return tuple(rows)


def calculate_vwap_sessions(
    bars: Sequence[FiveMinuteBar],
) -> tuple[FiveMinuteVwapRow, ...]:
    """Group chronological bars by date and reset cumulative state each session."""

    previous_timestamp = None
    seen_timestamps = set()
    grouped: dict[date, list[FiveMinuteBar]] = defaultdict(list)
    for bar in bars:
        if bar.timestamp in seen_timestamps:
            raise IndicatorSequenceError("VWAP input contains a duplicate timestamp")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("VWAP input must be strictly chronological")
        seen_timestamps.add(bar.timestamp)
        previous_timestamp = bar.timestamp
        grouped[bar.session_date].append(bar)

    rows: list[FiveMinuteVwapRow] = []
    for session_bars in grouped.values():
        rows.extend(calculate_session_vwap(session_bars))
    return tuple(rows)


class VwapIndicatorService:
    """Validate/reconcile processed bars, then calculate daily-reset RTH VWAP."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store

    def calculate(self, *, start: date, end: date) -> VwapCalculationResult:
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
        rows = calculate_vwap_sessions(bars)
        grouped: dict[date, list[FiveMinuteVwapRow]] = defaultdict(list)
        for row in rows:
            grouped[row.session_date].append(row)
        summaries = tuple(
            VwapSessionSummary(
                session_date=session_date,
                bars=len(session_rows),
                valid_rows=sum(row.vwap is not None for row in session_rows),
                first_valid_timestamp=next(
                    (row.timestamp for row in session_rows if row.vwap is not None),
                    None,
                ),
                first_vwap=next(
                    (row.vwap for row in session_rows if row.vwap is not None),
                    None,
                ),
                final_vwap=session_rows[-1].vwap if session_rows else None,
            )
            for session_date, session_rows in grouped.items()
        )
        return VwapCalculationResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            rows=rows,
            sessions=summaries,
            processed_validation=report,
        )
