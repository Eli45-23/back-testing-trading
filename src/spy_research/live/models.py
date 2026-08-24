"""Immutable Stage 14.2 live market-data and signal records."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.data.schemas import RawBarRecord
from spy_research.interactions import LevelType
from spy_research.replay import IncrementalReplayUpdate, ReplaySignalEvent
from spy_research.strategy.models import ConfirmationType, SetupDirection


ALPACA_SIP_STREAM_URL = "wss://stream.data.alpaca.markets/v2/sip"


class LiveDataError(ValueError):
    """A live market-data input cannot preserve Stage 14.1 guarantees."""


class LiveAuthenticationError(LiveDataError):
    """Alpaca rejected data-stream authentication."""


class LiveTransportError(LiveDataError):
    """The bounded Alpaca data-stream reconnect policy was exhausted."""


class LiveBootstrapError(LiveDataError):
    """Historical startup data cannot reconstruct deterministic state."""


class LiveSignalEvent(BaseModel):
    """A Stage 14.1 signal plus values knowable at live emission time."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    signal_identity: str
    setup_identity: str
    direction: SetupDirection
    triggering_level_type: LevelType
    triggering_level_price: Decimal
    break_timestamp: datetime
    confirmation_timestamp: datetime
    signal_known_at: datetime
    confirmation_close: Decimal
    atr14: Decimal | None
    base_short_membership: bool
    stage13_forward_test_candidate_ids: tuple[str, ...]
    live_version: Literal["alpaca-sip-live-signal-v1"] = "alpaca-sip-live-signal-v1"

    @classmethod
    def from_replay_update(
        cls,
        signal: ReplaySignalEvent,
        update: IncrementalReplayUpdate,
    ) -> "LiveSignalEvent":
        candle = update.completed_five_minute_bar
        if candle is None or candle.timestamp != signal.confirmation_candle_timestamp:
            raise LiveDataError("signal lacks its completed confirmation candle")
        atr14 = update.latest_atr.atr14 if update.latest_atr is not None else None
        return cls(
            session_date=signal.session_date,
            signal_identity=signal.event_identity,
            setup_identity=signal.setup_identity,
            direction=signal.direction,
            triggering_level_type=signal.triggering_level_type,
            triggering_level_price=signal.triggering_level_price,
            break_timestamp=signal.break_timestamp,
            confirmation_timestamp=signal.confirmation_candle_timestamp,
            signal_known_at=signal.signal_known_at,
            confirmation_close=candle.close,
            atr14=atr14,
            base_short_membership=signal.base_short_membership,
            stage13_forward_test_candidate_ids=signal.eligible_stage14_candidate_ids,
        )


class LiveAdapterUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    normalized_bar: RawBarRecord | None = None
    replay_update: IncrementalReplayUpdate | None = None
    signal_events: tuple[LiveSignalEvent, ...] = ()
    duplicate_identical: bool = False
    ignored_reason: str | None = None

    @model_validator(mode="after")
    def exactly_one_disposition(self) -> "LiveAdapterUpdate":
        states = (
            self.normalized_bar is not None,
            self.duplicate_identical,
            self.ignored_reason is not None,
        )
        if sum(states) != 1:
            raise ValueError("live update requires exactly one message disposition")
        if self.replay_update is not None and self.normalized_bar is None:
            raise ValueError("only a normalized bar can update replay state")
        return self


class LiveBootstrapResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    as_of: datetime
    prior_session_date: date
    prior_rth_bar_count: int = Field(ge=0)
    current_premarket_bar_count: int = Field(ge=0)
    current_rth_bar_count: int = Field(ge=0)
    seeded_bar_count: int = Field(ge=0)
    last_seeded_timestamp: datetime | None


class LiveSignalRunReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    feed: Literal["sip"] = "sip"
    stream_endpoint: Literal[ALPACA_SIP_STREAM_URL] = ALPACA_SIP_STREAM_URL
    bootstrap: LiveBootstrapResult
    accepted_live_bar_count: int = Field(ge=0)
    duplicate_identical_count: int = Field(ge=0)
    ignored_message_count: int = Field(ge=0)
    signals: tuple[LiveSignalEvent, ...]
    report_version: Literal["stage14-2-alpaca-live-adapter-v1"] = (
        "stage14-2-alpaca-live-adapter-v1"
    )
    caveat: str = (
        "Market-data dry run only; no orders, cancellations, accounts, positions, "
        "buying power, sizing, options, execution, or persistence."
    )


def live_signal_report_hash(report: LiveSignalRunReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
