"""Immutable Stage 14.1 sequential replay state and signal records."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.bars.models import FiveMinuteBar
from spy_research.indicators.models import (
    FiveMinuteAtrRow,
    FiveMinuteIndicatorRow,
    FiveMinuteVwapRow,
)
from spy_research.interactions import InteractionType, LevelType
from spy_research.interactions.models import LevelInteraction
from spy_research.market import SessionType
from spy_research.strategy.models import (
    BaseSetupStatus,
    ConfirmationType,
    SetupDirection,
)


class ReplayInputError(ValueError):
    """A sequential input violates frozen Stage 14.1 timing or ordering."""


class ReplayCrossType(StrEnum):
    EMA9_EMA20 = "EMA9_EMA20"
    EMA9_VWAP = "EMA9_VWAP"
    EMA20_VWAP = "EMA20_VWAP"


class ReplayCrossEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    session_date: date
    cross_type: ReplayCrossType
    direction: Literal["BULLISH", "BEARISH"]
    event_timestamp: datetime
    known_at: datetime
    event_identity: str
    replay_version: Literal["incremental-rth-signal-state-v1"] = (
        "incremental-rth-signal-state-v1"
    )

    @model_validator(mode="after")
    def completed_candle_timing(self) -> Self:
        from datetime import timedelta

        if self.known_at != self.event_timestamp + timedelta(minutes=5):
            raise ValueError("cross known-at must follow candle completion by five minutes")
        return self


class ReplaySignalEvent(BaseModel):
    """One immutable Stage 9 confirmed setup emitted at its knowable time."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    event_type: Literal["STAGE9_CONFIRMED_SETUP"] = "STAGE9_CONFIRMED_SETUP"
    event_timestamp: datetime
    known_at: datetime
    direction: SetupDirection
    triggering_level_type: LevelType
    triggering_level_price: Decimal
    break_timestamp: datetime
    break_completed_at: datetime
    break_interaction_type: Literal[
        InteractionType.CLOSE_THROUGH_ABOVE,
        InteractionType.CLOSE_THROUGH_BELOW,
    ]
    confirmation_type: ConfirmationType
    confirmation_candle_timestamp: datetime
    signal_known_at: datetime
    setup_identity: str
    stage9_qualification_status: Literal[BaseSetupStatus.CONFIRMED]
    same_session_executable: bool
    base_short_membership: bool
    eligible_stage14_candidate_ids: tuple[str, ...]
    interaction_version: Literal["level-interaction-v1"] = "level-interaction-v1"
    follow_through_version: Literal["break-follow-through-v1"] = (
        "break-follow-through-v1"
    )
    strategy_version: Literal["base-exact-price-v1"] = "base-exact-price-v1"
    replay_version: Literal["incremental-rth-signal-state-v1"] = (
        "incremental-rth-signal-state-v1"
    )

    @model_validator(mode="after")
    def reconcile_signal(self) -> Self:
        from datetime import timedelta

        if self.event_timestamp != self.confirmation_candle_timestamp:
            raise ValueError("signal event timestamp must be its confirmation candle")
        if self.known_at != self.signal_known_at:
            raise ValueError("signal known-at aliases must match")
        if self.signal_known_at != self.confirmation_candle_timestamp + timedelta(
            minutes=5
        ):
            raise ValueError("signal cannot be known before confirmation completion")
        if self.base_short_membership != (self.direction is SetupDirection.SHORT):
            raise ValueError("BASE_SHORT membership must remain direction-only")
        if self.base_short_membership != bool(self.eligible_stage14_candidate_ids):
            raise ValueError("only BASE_SHORT signals receive Stage 14 candidate IDs")
        return self


class IncrementalReplayUpdate(BaseModel):
    """Zero-or-more derived facts from one newly completed one-minute bar."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    input_bar_timestamp: datetime
    input_bar_completed_at: datetime
    session_date: date
    session_type: SessionType
    completed_five_minute_bar: FiveMinuteBar | None = None
    latest_ema: FiveMinuteIndicatorRow | None = None
    latest_vwap: FiveMinuteVwapRow | None = None
    latest_atr: FiveMinuteAtrRow | None = None
    level_interactions: tuple[LevelInteraction, ...] = ()
    cross_events: tuple[ReplayCrossEvent, ...] = ()
    signal_events: tuple[ReplaySignalEvent, ...] = ()


class ReplaySessionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    raw_bar_count: int = Field(ge=0)
    premarket_bar_count: int = Field(ge=0)
    rth_one_minute_count: int = Field(ge=0)
    five_minute_count: int = Field(ge=0)
    break_seed_count: int = Field(ge=0)
    confirmed_signal_count: int = Field(ge=0)
    executable_signal_count: int = Field(ge=0)
    base_short_confirmed_count: int = Field(ge=0)
    base_short_executable_count: int = Field(ge=0)
    ema9_valid_count: int = Field(ge=0)
    ema20_valid_count: int = Field(ge=0)
    atr14_valid_count: int = Field(ge=0)
    ema9_ema20_cross_count: int = Field(ge=0)
    ema9_vwap_cross_count: int = Field(ge=0)
    ema20_vwap_cross_count: int = Field(ge=0)
    previous_day_levels_available: bool
    premarket_levels_available: bool
    opening_levels_available: bool


class ReplayBatchReconciliation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    exact_match: bool
    replay_break_seed_count: int = Field(ge=0)
    batch_break_seed_count: int = Field(ge=0)
    replay_confirmed_count: int = Field(ge=0)
    batch_confirmed_count: int = Field(ge=0)
    replay_executable_count: int = Field(ge=0)
    batch_executable_count: int = Field(ge=0)
    replay_base_short_confirmed_count: int = Field(ge=0)
    batch_base_short_confirmed_count: int = Field(ge=0)
    replay_base_short_executable_count: int = Field(ge=0)
    batch_base_short_executable_count: int = Field(ge=0)
    mismatched_setup_identities: tuple[str, ...]


class SignalReplayReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    raw_bar_count: int = Field(ge=0)
    rth_one_minute_count: int = Field(ge=0)
    five_minute_count: int = Field(ge=0)
    break_seed_count: int = Field(ge=0)
    confirmed_signal_count: int = Field(ge=0)
    executable_signal_count: int = Field(ge=0)
    base_short_confirmed_count: int = Field(ge=0)
    base_short_executable_count: int = Field(ge=0)
    signals: tuple[ReplaySignalEvent, ...]
    sessions: tuple[ReplaySessionSummary, ...]
    batch_reconciliation: ReplayBatchReconciliation
    processed_five_minute_exact_match: bool
    session_chunk_replay_exact_match: bool
    report_version: Literal["stage14-1-deterministic-signal-replay-v1"] = (
        "stage14-1-deterministic-signal-replay-v1"
    )
    caveat: str = (
        "Prospective signal-state infrastructure only; no fills, orders, sizing, "
        "options, execution, persistence, or historical-profitability claim."
    )

    @model_validator(mode="after")
    def reconcile_counts(self) -> Self:
        if len(self.signals) != self.confirmed_signal_count:
            raise ValueError("signal stream/count mismatch")
        totals = {
            "raw_bar_count": sum(item.raw_bar_count for item in self.sessions),
            "rth_one_minute_count": sum(
                item.rth_one_minute_count for item in self.sessions
            ),
            "five_minute_count": sum(item.five_minute_count for item in self.sessions),
            "break_seed_count": sum(item.break_seed_count for item in self.sessions),
            "confirmed_signal_count": sum(
                item.confirmed_signal_count for item in self.sessions
            ),
            "executable_signal_count": sum(
                item.executable_signal_count for item in self.sessions
            ),
            "base_short_confirmed_count": sum(
                item.base_short_confirmed_count for item in self.sessions
            ),
            "base_short_executable_count": sum(
                item.base_short_executable_count for item in self.sessions
            ),
        }
        if any(getattr(self, name) != value for name, value in totals.items()):
            raise ValueError("session summaries do not reproduce replay totals")
        if not self.batch_reconciliation.exact_match:
            raise ValueError("Stage 14.1 requires exact batch/replay setup equality")
        if not self.processed_five_minute_exact_match:
            raise ValueError("incremental candles must equal accepted Stage 2 bars")
        if not self.session_chunk_replay_exact_match:
            raise ValueError("session-chunk replay must equal continuous replay")
        return self


def signal_replay_hash(report: SignalReplayReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
