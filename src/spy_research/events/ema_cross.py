"""Completed-candle EMA9/EMA20 cross detection and context composition."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import localcontext

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.bars.validation import ProcessedFiveMinuteValidator
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events.models import (
    DetectedEmaCross,
    EmaCrossCalculationResult,
    EmaCrossDirection,
    EmaCrossEvent,
    EmaCrossSessionSummary,
)
from spy_research.indicators.atr import calculate_atr_sessions
from spy_research.indicators.ema import (
    EMA_CONTEXT,
    IndicatorInputValidationError,
    IndicatorSequenceError,
    calculate_ema_sessions,
)
from spy_research.indicators.models import FiveMinuteIndicatorRow
from spy_research.indicators.separation import calculate_ema_separation_sessions
from spy_research.indicators.vwap import calculate_vwap_sessions


class EventContextAlignmentError(ValueError):
    """Verified indicator rows cannot be aligned at a detected event timestamp."""


def detect_session_ema_crosses(
    ema_rows: Sequence[FiveMinuteIndicatorRow],
) -> tuple[DetectedEmaCross, ...]:
    """Detect crosses from adjacent valid EMA rows in exactly one session."""

    if not ema_rows:
        return ()
    session_date = ema_rows[0].session_date
    previous_timestamp = None
    seen_timestamps = set()
    for row in ema_rows:
        if row.session_date != session_date:
            raise IndicatorSequenceError(
                "Single-session EMA cross input mixes session dates"
            )
        if row.timeframe != "5Min":
            raise IndicatorSequenceError("EMA cross input timeframe must be 5Min")
        if row.session_mode != "RTH_ONLY":
            raise IndicatorSequenceError(
                "EMA cross input session mode must be RTH_ONLY"
            )
        if row.timestamp in seen_timestamps:
            raise IndicatorSequenceError("EMA cross input contains a duplicate timestamp")
        if previous_timestamp is not None and row.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("EMA cross input must be strictly chronological")
        for value in (row.ema9, row.ema20):
            if value is not None and not value.is_finite():
                raise IndicatorSequenceError(
                    "EMA cross input values must be finite Decimals"
                )
        seen_timestamps.add(row.timestamp)
        previous_timestamp = row.timestamp

    events: list[DetectedEmaCross] = []
    for previous, current in zip(ema_rows, ema_rows[1:], strict=False):
        if (
            previous.ema9 is None
            or previous.ema20 is None
            or current.ema9 is None
            or current.ema20 is None
        ):
            continue
        direction = None
        if current.ema9 > current.ema20 and previous.ema9 <= previous.ema20:
            direction = EmaCrossDirection.BULLISH
        elif current.ema9 < current.ema20 and previous.ema9 >= previous.ema20:
            direction = EmaCrossDirection.BEARISH
        if direction is not None:
            events.append(
                DetectedEmaCross(
                    symbol=current.symbol,
                    timestamp=current.timestamp,
                    session_date=current.session_date,
                    direction=direction,
                    close=current.close,
                    ema9=current.ema9,
                    ema20=current.ema20,
                    previous_ema9=previous.ema9,
                    previous_ema20=previous.ema20,
                )
            )
    return tuple(events)


def detect_ema_crosses(
    ema_rows: Sequence[FiveMinuteIndicatorRow],
) -> tuple[DetectedEmaCross, ...]:
    """Group chronological EMA rows and reset detection at each RTH session."""

    previous_timestamp = None
    seen_timestamps = set()
    grouped: dict[date, list[FiveMinuteIndicatorRow]] = defaultdict(list)
    for row in ema_rows:
        if row.timestamp in seen_timestamps:
            raise IndicatorSequenceError("EMA cross input contains a duplicate timestamp")
        if previous_timestamp is not None and row.timestamp <= previous_timestamp:
            raise IndicatorSequenceError("EMA cross input must be strictly chronological")
        seen_timestamps.add(row.timestamp)
        previous_timestamp = row.timestamp
        grouped[row.session_date].append(row)

    events: list[DetectedEmaCross] = []
    for session_rows in grouped.values():
        events.extend(detect_session_ema_crosses(session_rows))
    return tuple(events)


class EmaCrossEventService:
    """Validate bars, reuse Stage 3 indicators, detect crosses, and attach context."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store

    def calculate(self, *, start: date, end: date) -> EmaCrossCalculationResult:
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
        ema_rows = calculate_ema_sessions(bars)
        separation_rows = calculate_ema_separation_sessions(ema_rows)
        vwap_rows = calculate_vwap_sessions(bars)
        atr_rows = calculate_atr_sessions(bars)
        detected = detect_ema_crosses(ema_rows)

        ema_by_timestamp = {row.timestamp: row for row in ema_rows}
        separation_by_timestamp = {row.timestamp: row for row in separation_rows}
        vwap_by_timestamp = {row.timestamp: row for row in vwap_rows}
        atr_by_timestamp = {row.timestamp: row for row in atr_rows}
        events: list[EmaCrossEvent] = []
        with localcontext(EMA_CONTEXT):
            for cross in detected:
                ema = ema_by_timestamp.get(cross.timestamp)
                separation = separation_by_timestamp.get(cross.timestamp)
                vwap = vwap_by_timestamp.get(cross.timestamp)
                atr = atr_by_timestamp.get(cross.timestamp)
                if ema is None or separation is None or vwap is None or atr is None:
                    raise EventContextAlignmentError(
                        f"Missing indicator context at {cross.timestamp.isoformat()}"
                    )
                previous_signed = cross.previous_ema9 - cross.previous_ema20
                events.append(
                    EmaCrossEvent(
                        symbol=cross.symbol,
                        timestamp=cross.timestamp,
                        session_date=cross.session_date,
                        direction=cross.direction,
                        reference_price=cross.close,
                        close=cross.close,
                        ema9=cross.ema9,
                        ema20=cross.ema20,
                        previous_ema9=cross.previous_ema9,
                        previous_ema20=cross.previous_ema20,
                        signed_separation=separation.signed_separation,
                        absolute_separation=separation.absolute_separation,
                        previous_signed_separation=previous_signed,
                        separation_delta_1=separation.separation_delta_1,
                        separation_delta_2=separation.separation_delta_2,
                        separation_delta_3=separation.separation_delta_3,
                        vwap=vwap.vwap,
                        close_minus_vwap=(
                            cross.close - vwap.vwap if vwap.vwap is not None else None
                        ),
                        ema9_minus_vwap=(
                            cross.ema9 - vwap.vwap if vwap.vwap is not None else None
                        ),
                        ema20_minus_vwap=(
                            cross.ema20 - vwap.vwap if vwap.vwap is not None else None
                        ),
                        atr14=atr.atr14,
                    )
                )

        identities = {
            (event.symbol, event.timestamp, event.direction, event.event_version)
            for event in events
        }
        if len(identities) != len(events):
            raise EventContextAlignmentError("Duplicate EMA cross event identity")

        grouped_events: dict[date, list[EmaCrossEvent]] = defaultdict(list)
        for event in events:
            grouped_events[event.session_date].append(event)
        session_dates = tuple(dict.fromkeys(row.session_date for row in ema_rows))
        summaries = tuple(
            EmaCrossSessionSummary(
                session_date=session_date,
                bullish_crosses=sum(
                    event.direction == EmaCrossDirection.BULLISH
                    for event in session_events
                ),
                bearish_crosses=sum(
                    event.direction == EmaCrossDirection.BEARISH
                    for event in session_events
                ),
                total_crosses=len(session_events),
                first_event_timestamp=(
                    session_events[0].timestamp if session_events else None
                ),
                last_event_timestamp=(
                    session_events[-1].timestamp if session_events else None
                ),
            )
            for session_date in session_dates
            for session_events in (grouped_events[session_date],)
        )
        return EmaCrossCalculationResult(
            symbol=self._config.symbol,
            start_date=start,
            end_date=end,
            events=tuple(events),
            sessions=summaries,
            processed_validation=report,
        )
