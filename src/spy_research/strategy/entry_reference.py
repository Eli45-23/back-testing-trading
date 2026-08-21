"""Pure executable underlying entry-reference selection for Stage 9.2."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from spy_research.data.schemas import RawBarRecord
from spy_research.market import MarketSessionClassifier, SessionType
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BaseSetupStatus,
    EntryStatus,
    SetupEntryReference,
)


class SetupOutcomeInputError(ValueError):
    """Setup or raw bars violate frozen Stage 9.2 provenance/timing."""


def validate_rth_minutes(
    setup: BasePriceActionCandidate,
    bars: Sequence[RawBarRecord],
) -> None:
    classifier = MarketSessionClassifier()
    previous = None
    seen = set()
    for bar in bars:
        if (
            bar.symbol != "SPY"
            or bar.source != "alpaca"
            or bar.feed != "sip"
            or bar.timeframe != "1Min"
            or bar.adjustment != "raw"
        ):
            raise SetupOutcomeInputError(
                "Entry outcomes require SPY Alpaca SIP raw 1Min bars"
            )
        classified = classifier.classify(bar)
        if classified.session_date != setup.session_date:
            raise SetupOutcomeInputError(
                "One-minute bar belongs to the wrong setup session"
            )
        if classified.session_type is not SessionType.RTH:
            raise SetupOutcomeInputError("Entry outcomes require RTH one-minute bars")
        if bar.timestamp in seen:
            raise SetupOutcomeInputError("Duplicate one-minute timestamp")
        if previous is not None and bar.timestamp <= previous:
            raise SetupOutcomeInputError(
                "One-minute bars must be strictly chronological"
            )
        seen.add(bar.timestamp)
        previous = bar.timestamp


def select_entry_reference(
    setup: BasePriceActionCandidate,
    chronological_same_session_rth_1m_bars: Sequence[RawBarRecord],
) -> SetupEntryReference:
    """Select the first same-session RTH minute at/after signal-known time."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise SetupOutcomeInputError("Only confirmed Stage 9.1 setups may be processed")
    if setup.signal_known_at is None or setup.earliest_entry_timestamp is None:
        raise SetupOutcomeInputError("Confirmed setup lacks frozen entry timing")
    validate_rth_minutes(setup, chronological_same_session_rth_1m_bars)
    if not setup.same_session_executable:
        return SetupEntryReference(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            signal_known_at=setup.signal_known_at,
            earliest_entry_timestamp=setup.earliest_entry_timestamp,
            entry_status=EntryStatus.ENTRY_UNAVAILABLE_SESSION_END,
        )
    selected = next(
        (
            bar
            for bar in chronological_same_session_rth_1m_bars
            if bar.timestamp >= setup.earliest_entry_timestamp
        ),
        None,
    )
    if selected is None:
        return SetupEntryReference(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            signal_known_at=setup.signal_known_at,
            earliest_entry_timestamp=setup.earliest_entry_timestamp,
            entry_status=EntryStatus.ENTRY_REFERENCE_MISSING,
        )
    delay_seconds = (
        selected.timestamp - setup.earliest_entry_timestamp
    ).total_seconds()
    if delay_seconds < 0 or delay_seconds % 60:
        raise SetupOutcomeInputError("Entry delay must be a whole nonnegative minute")
    delay = int(delay_seconds // 60)
    return SetupEntryReference(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        signal_known_at=setup.signal_known_at,
        earliest_entry_timestamp=setup.earliest_entry_timestamp,
        entry_status=EntryStatus.AVAILABLE,
        entry_reference_timestamp=selected.timestamp,
        entry_reference_price=selected.open,
        entry_delay_minutes=delay,
    )
