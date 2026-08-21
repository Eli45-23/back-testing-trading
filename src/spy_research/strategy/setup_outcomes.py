"""Pure same-session post-entry one-minute excursion outcomes."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal

from spy_research.data.schemas import RawBarRecord
from spy_research.strategy.entry_reference import (
    SetupOutcomeInputError,
    validate_rth_minutes,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    EntryStatus,
    SetupEntryReference,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupDirection,
)


FIXED_SETUP_HORIZONS = (5, 15, 30, 60)


def _one_horizon(
    setup: BasePriceActionCandidate,
    entry: SetupEntryReference,
    bars: tuple[RawBarRecord, ...],
    name: str,
    requested: int,
) -> SetupHorizonOutcome:
    highest = max(bars, key=lambda bar: bar.high)
    lowest = min(bars, key=lambda bar: bar.low)
    price = entry.entry_reference_price
    assert price is not None
    if setup.direction is SetupDirection.LONG:
        mfe = max(Decimal(0), highest.high - price)
        mae = max(Decimal(0), price - lowest.low)
        mfe_time, mae_time = highest.timestamp, lowest.timestamp
    else:
        mfe = max(Decimal(0), price - lowest.low)
        mae = max(Decimal(0), highest.high - price)
        mfe_time, mae_time = lowest.timestamp, highest.timestamp
    return SetupHorizonOutcome(
        horizon=name,
        requested_minutes=requested,
        available_minutes=len(bars),
        complete=len(bars) == requested,
        mfe=mfe,
        mae=mae,
        mfe_timestamp=mfe_time,
        mae_timestamp=mae_time,
    )


def calculate_setup_outcomes(
    setup: BasePriceActionCandidate,
    entry: SetupEntryReference,
    same_session_rth_1m_bars: Sequence[RawBarRecord],
    session_close: datetime,
) -> SetupOutcome:
    """Calculate entry-inclusive exact fixed and EOD windows."""

    if entry.setup_identity != setup.setup_identity:
        raise SetupOutcomeInputError("Entry reference setup identity mismatch")
    if entry.entry_status is not EntryStatus.AVAILABLE:
        return SetupOutcome(
            setup_identity=setup.setup_identity,
            setup=setup,
            entry_reference=entry,
        )
    validate_rth_minutes(setup, same_session_rth_1m_bars)
    start = entry.entry_reference_timestamp
    assert start is not None
    if entry.entry_reference_price is None:
        raise SetupOutcomeInputError("Available entry lacks its reference price")
    by_time = {
        bar.timestamp: bar
        for bar in same_session_rth_1m_bars
        if start <= bar.timestamp < session_close
    }
    entry_bar = by_time.get(start)
    if entry_bar is None:
        raise SetupOutcomeInputError(
            "Entry-reference minute is absent from outcome bars"
        )
    if entry_bar.open != entry.entry_reference_price:
        raise SetupOutcomeInputError(
            "Entry-reference price does not match raw minute open"
        )
    results = {}
    for minutes in FIXED_SETUP_HORIZONS:
        selected = tuple(
            by_time[t]
            for t in (start + timedelta(minutes=i) for i in range(minutes))
            if t in by_time
        )
        results[minutes] = _one_horizon(
            setup, entry, selected, f"{minutes}m", minutes
        )
    eod_requested = int((session_close - start).total_seconds() // 60)
    eod_bars = tuple(
        by_time[t]
        for t in (start + timedelta(minutes=i) for i in range(eod_requested))
        if t in by_time
    )
    return SetupOutcome(
        setup_identity=setup.setup_identity,
        setup=setup,
        entry_reference=entry,
        five=results[5],
        fifteen=results[15],
        thirty=results[30],
        sixty=results[60],
        eod=_one_horizon(setup, entry, eod_bars, "EOD", eod_requested),
    )
