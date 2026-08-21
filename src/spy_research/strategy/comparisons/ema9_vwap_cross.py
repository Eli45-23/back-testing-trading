"""Deterministic daily-reset EMA9/VWAP completed-candle cross events."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, timedelta
from decimal import localcontext
from hashlib import sha256

from spy_research.indicators import FiveMinuteIndicatorRow, FiveMinuteVwapRow
from spy_research.indicators.vwap import VWAP_CONTEXT
from spy_research.strategy.comparisons.models import (
    Ema9VwapCrossDirection,
    Ema9VwapCrossEvent,
    Ema9VwapCrossSessionSummary,
)


class Ema9VwapCrossInputError(ValueError):
    """Accepted EMA9/VWAP rows cannot form a trustworthy event universe."""


def ema9_vwap_event_identity(
    symbol: str,
    timestamp,
    direction: Ema9VwapCrossDirection,
) -> str:
    payload = "|".join(
        (
            symbol,
            timestamp.isoformat(),
            direction.value,
            "ema9-vwap-completed-candle-cross-v1",
        )
    )
    return sha256(payload.encode()).hexdigest()


def detect_ema9_vwap_crosses(
    ema_rows: Sequence[FiveMinuteIndicatorRow],
    vwap_rows: Sequence[FiveMinuteVwapRow],
) -> tuple[tuple[Ema9VwapCrossEvent, ...], tuple[Ema9VwapCrossSessionSummary, ...]]:
    """Detect adjacent-row crosses independently within each RTH session."""

    def index(rows, label):
        indexed = {}
        previous = None
        for row in rows:
            key = (row.session_date, row.timestamp)
            if key in indexed:
                raise Ema9VwapCrossInputError(f"Duplicate {label} timestamp")
            if previous is not None and row.timestamp <= previous:
                raise Ema9VwapCrossInputError(f"{label} rows must be chronological")
            if row.timeframe != "5Min" or row.session_mode != "RTH_ONLY":
                raise Ema9VwapCrossInputError(f"{label} rows require RTH 5Min provenance")
            indexed[key] = row
            previous = row.timestamp
        return indexed

    ema_by_key = index(ema_rows, "EMA")
    vwap_by_key = index(vwap_rows, "VWAP")
    if set(ema_by_key) != set(vwap_by_key):
        raise Ema9VwapCrossInputError("EMA9 and VWAP timestamp universes must match")
    grouped: dict[date, list[tuple[FiveMinuteIndicatorRow, FiveMinuteVwapRow]]] = (
        defaultdict(list)
    )
    for key, ema in ema_by_key.items():
        vwap = vwap_by_key[key]
        if ema.symbol != vwap.symbol:
            raise Ema9VwapCrossInputError("EMA9/VWAP symbols must match")
        grouped[ema.session_date].append((ema, vwap))

    events = []
    summaries = []
    for session_date, rows in grouped.items():
        session_events = []
        for (prior_ema, prior_vwap), (current_ema, current_vwap) in zip(
            rows, rows[1:], strict=False
        ):
            if current_ema.timestamp - prior_ema.timestamp != timedelta(minutes=5):
                raise Ema9VwapCrossInputError(
                    "EMA9/VWAP cross rows must be adjacent five-minute buckets"
                )
            values = (
                prior_ema.ema9,
                prior_vwap.vwap,
                current_ema.ema9,
                current_vwap.vwap,
            )
            if any(value is None for value in values):
                continue
            assert prior_ema.ema9 is not None
            assert prior_vwap.vwap is not None
            assert current_ema.ema9 is not None
            assert current_vwap.vwap is not None
            direction = None
            if (
                current_ema.ema9 > current_vwap.vwap
                and prior_ema.ema9 <= prior_vwap.vwap
            ):
                direction = Ema9VwapCrossDirection.BULLISH
            elif (
                current_ema.ema9 < current_vwap.vwap
                and prior_ema.ema9 >= prior_vwap.vwap
            ):
                direction = Ema9VwapCrossDirection.BEARISH
            if direction is None:
                continue
            with localcontext(VWAP_CONTEXT):
                signed = current_ema.ema9 - current_vwap.vwap
            event = Ema9VwapCrossEvent(
                event_identity=ema9_vwap_event_identity(
                    current_ema.symbol, current_ema.timestamp, direction
                ),
                session_date=session_date,
                direction=direction,
                cross_timestamp=current_ema.timestamp,
                cross_known_at=current_ema.timestamp + timedelta(minutes=5),
                ema9=current_ema.ema9,
                vwap=current_vwap.vwap,
                prior_ema9=prior_ema.ema9,
                prior_vwap=prior_vwap.vwap,
                signed_distance=signed,
            )
            events.append(event)
            session_events.append(event)
        summaries.append(
            Ema9VwapCrossSessionSummary(
                session_date=session_date,
                bullish_crosses=sum(
                    item.direction is Ema9VwapCrossDirection.BULLISH
                    for item in session_events
                ),
                bearish_crosses=sum(
                    item.direction is Ema9VwapCrossDirection.BEARISH
                    for item in session_events
                ),
                total_crosses=len(session_events),
                first_cross_timestamp=(
                    session_events[0].cross_timestamp if session_events else None
                ),
                last_cross_timestamp=(
                    session_events[-1].cross_timestamp if session_events else None
                ),
            )
        )
    if len({item.event_identity for item in events}) != len(events):
        raise Ema9VwapCrossInputError("Duplicate EMA9/VWAP event identity")
    return tuple(events), tuple(summaries)
