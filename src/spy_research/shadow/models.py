"""Immutable Stage 14.3 shadow-forward-test records and reports."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.execution import AmbiguityMetadata
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions import LevelType


class ShadowInputError(ValueError):
    """Shadow input cannot preserve frozen timing or execution semantics."""


class ShadowState(StrEnum):
    PENDING_ENTRY = "PENDING_ENTRY"
    ACTIVE = "ACTIVE"
    TARGET_EXIT = "TARGET_EXIT"
    STOP_EXIT = "STOP_EXIT"
    EOD_EXIT = "EOD_EXIT"
    AMBIGUOUS_BOTH_TOUCHED = "AMBIGUOUS_BOTH_TOUCHED"
    UNAVAILABLE_ATR = "UNAVAILABLE_ATR"
    UNAVAILABLE_OBJECTIVE_LEVEL = "UNAVAILABLE_OBJECTIVE_LEVEL"
    ENTRY_UNAVAILABLE_SESSION_END = "ENTRY_UNAVAILABLE_SESSION_END"


TERMINAL_SHADOW_STATES = frozenset(
    {
        ShadowState.TARGET_EXIT,
        ShadowState.STOP_EXIT,
        ShadowState.EOD_EXIT,
        ShadowState.AMBIGUOUS_BOTH_TOUCHED,
        ShadowState.UNAVAILABLE_ATR,
        ShadowState.UNAVAILABLE_OBJECTIVE_LEVEL,
        ShadowState.ENTRY_UNAVAILABLE_SESSION_END,
    }
)


class ShadowEventType(StrEnum):
    CANDIDATE_CREATED = "CANDIDATE_CREATED"
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    UNAVAILABLE = "UNAVAILABLE"


class ShadowPosition(BaseModel):
    """Current or final state for one setup/candidate identity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    setup_identity: str
    candidate_id: str
    signal_known_at: datetime
    confirmation_timestamp: datetime
    confirmation_close: Decimal
    confirmation_atr14: Decimal | None
    stop_multiplier: Decimal
    triggering_level_type: LevelType
    triggering_level_price: Decimal
    target_level_types: tuple[LevelType, ...]
    target_price: Decimal | None
    entry_timestamp: datetime | None = None
    entry_price: Decimal | None = None
    risk_distance: Decimal | None = None
    stop_price: Decimal | None = None
    target_distance: Decimal | None = None
    target_r: Decimal | None = None
    state: ShadowState
    exit_timestamp: datetime | None = None
    exit_price: Decimal | None = None
    realized_price_pnl: Decimal | None = None
    realized_r: Decimal | None = None
    holding_minutes: int | None = Field(default=None, ge=0)
    bars_observed: int = Field(default=0, ge=0)
    ambiguity: AmbiguityMetadata | None = None
    shadow_version: Literal["stage14-3-objective-shadow-v1"] = (
        "stage14-3-objective-shadow-v1"
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        expected_candidates = {
            "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_0_75:NO_FIXED_TARGET": Decimal(
                "0.75"
            ),
            "BASE_SHORT:NEXT_OBJECTIVE_LEVEL:ATR_1_00:NO_FIXED_TARGET": Decimal(
                "1.00"
            ),
        }
        if expected_candidates.get(self.candidate_id) != self.stop_multiplier:
            raise ValueError("unknown or mismatched Stage 14.3 candidate")
        if self.signal_known_at.utcoffset() is None:
            raise ValueError("shadow timestamps must be timezone-aware")
        if tuple(self.target_level_types) != tuple(
            level_type
            for level_type in LevelType
            if level_type in set(self.target_level_types)
        ):
            raise ValueError("shadow target level ties require deterministic ordering")
        if (self.target_price is None) != (not self.target_level_types):
            raise ValueError("shadow target price and level types must agree")
        entry_fields = (self.entry_timestamp, self.entry_price)
        if self.state in (
            ShadowState.PENDING_ENTRY,
            ShadowState.ENTRY_UNAVAILABLE_SESSION_END,
        ):
            if any(item is not None for item in entry_fields):
                raise ValueError("unentered shadow state cannot contain an entry")
            if any(
                item is not None
                for item in (
                    self.risk_distance,
                    self.stop_price,
                    self.target_distance,
                    self.target_r,
                    self.exit_timestamp,
                    self.exit_price,
                    self.realized_price_pnl,
                    self.realized_r,
                    self.holding_minutes,
                    self.ambiguity,
                )
            ) or self.bars_observed:
                raise ValueError("unentered shadow state contains path fields")
            return self
        if any(item is None for item in entry_fields):
            raise ValueError("entered shadow state requires entry timestamp and price")
        assert self.entry_timestamp is not None
        if self.entry_timestamp < self.signal_known_at:
            raise ValueError("shadow entry cannot precede signal-known time")
        unavailable_path_fields = (
            self.exit_timestamp,
            self.exit_price,
            self.realized_price_pnl,
            self.realized_r,
            self.holding_minutes,
            self.ambiguity,
        )
        if self.state is ShadowState.UNAVAILABLE_ATR:
            if self.confirmation_atr14 is not None and self.confirmation_atr14 > 0:
                raise ValueError("ATR-unavailable state cannot contain positive ATR")
            if self.risk_distance is not None or self.stop_price is not None:
                raise ValueError("ATR-unavailable state cannot invent risk")
            if any(item is not None for item in unavailable_path_fields) or self.bars_observed:
                raise ValueError("ATR-unavailable state cannot contain a path")
            return self
        if self.confirmation_atr14 is None or self.confirmation_atr14 <= 0:
            raise ValueError("entered eligible shadow path requires positive ATR")
        assert self.entry_price is not None
        with localcontext(ATR_CONTEXT):
            risk = self.confirmation_atr14 * self.stop_multiplier
            stop = self.entry_price + risk
        if self.risk_distance != risk or self.stop_price != stop:
            raise ValueError("shadow stop must use exact confirmation ATR")
        if self.state is ShadowState.UNAVAILABLE_OBJECTIVE_LEVEL:
            if self.target_price is not None or self.target_level_types:
                raise ValueError("open-ended objective cannot contain a target")
            if any(item is not None for item in unavailable_path_fields) or self.bars_observed:
                raise ValueError("objective-unavailable state cannot contain a path")
            return self
        if self.target_price is None or not self.target_level_types:
            raise ValueError("eligible shadow path requires an objective target")
        with localcontext(ATR_CONTEXT):
            distance = self.entry_price - self.target_price
            target_r = distance / risk
        if self.target_distance != distance or self.target_r != target_r:
            raise ValueError("target distance and R must reconcile exactly")
        if self.state is ShadowState.ACTIVE:
            if any(
                item is not None
                for item in (
                    self.exit_timestamp,
                    self.exit_price,
                    self.realized_price_pnl,
                    self.realized_r,
                    self.holding_minutes,
                    self.ambiguity,
                )
            ):
                raise ValueError("active position cannot contain an exit")
            return self
        if self.state is ShadowState.AMBIGUOUS_BOTH_TOUCHED:
            if self.exit_timestamp is None or self.holding_minutes is None:
                raise ValueError("ambiguous path requires timing")
            if self.ambiguity is None:
                raise ValueError("ambiguous path requires candle metadata")
            if any(
                item is not None
                for item in (self.exit_price, self.realized_price_pnl, self.realized_r)
            ):
                raise ValueError("ambiguous path cannot invent an exit price")
            expected_minutes = int(
                (self.exit_timestamp - self.entry_timestamp).total_seconds() // 60
            )
            if (
                self.exit_timestamp < self.entry_timestamp
                or self.holding_minutes != expected_minutes
            ):
                raise ValueError("ambiguous holding time does not match event timing")
            return self
        if self.state not in (
            ShadowState.TARGET_EXIT,
            ShadowState.STOP_EXIT,
            ShadowState.EOD_EXIT,
        ):
            raise ValueError("unknown shadow terminal state")
        if any(
            item is None
            for item in (
                self.exit_timestamp,
                self.exit_price,
                self.realized_price_pnl,
                self.realized_r,
                self.holding_minutes,
            )
        ):
            raise ValueError("realized shadow exit requires complete fields")
        assert self.exit_price is not None and self.realized_price_pnl is not None
        assert self.realized_r is not None
        assert self.exit_timestamp is not None and self.holding_minutes is not None
        expected_minutes = int(
            (self.exit_timestamp - self.entry_timestamp).total_seconds() // 60
        )
        if self.exit_timestamp < self.entry_timestamp or self.holding_minutes != expected_minutes:
            raise ValueError("shadow holding time does not match exit timing")
        with localcontext(ATR_CONTEXT):
            expected_pnl = self.entry_price - self.exit_price
            expected_r = (
                Decimal("-1")
                if self.state is ShadowState.STOP_EXIT
                else expected_pnl / risk
            )
        if self.realized_price_pnl != expected_pnl or self.realized_r != expected_r:
            raise ValueError("shadow P/L and R do not reconcile")
        return self


class ShadowTransitionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_identity: str
    event_type: ShadowEventType
    event_timestamp: datetime
    setup_identity: str
    candidate_id: str
    resulting_state: ShadowState
    position: ShadowPosition

    @classmethod
    def from_position(
        cls,
        event_type: ShadowEventType,
        timestamp: datetime,
        position: ShadowPosition,
    ) -> "ShadowTransitionEvent":
        identity = sha256(
            (
                f"{position.setup_identity}|{position.candidate_id}|{event_type.value}|"
                f"{timestamp.isoformat()}|{position.state.value}|stage14-3"
            ).encode()
        ).hexdigest()
        return cls(
            event_identity=identity,
            event_type=event_type,
            event_timestamp=timestamp,
            setup_identity=position.setup_identity,
            candidate_id=position.candidate_id,
            resulting_state=position.state,
            position=position,
        )


class ShadowHistoricalEquivalence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    exact_match: bool
    shadow_candidate_count: int = Field(ge=0)
    shadow_executable_path_count: int = Field(ge=0)
    shadow_entry_unavailable_count: int = Field(ge=0)
    stage13_path_count: int = Field(ge=0)
    matched_path_count: int = Field(ge=0)
    mismatched_keys: tuple[str, ...]


class ShadowHistoricalReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    positions: tuple[ShadowPosition, ...]
    equivalence: ShadowHistoricalEquivalence
    report_version: Literal["stage14-3-historical-shadow-equivalence-v1"] = (
        "stage14-3-historical-shadow-equivalence-v1"
    )
    caveat: str = (
        "Shadow forward-test reconstruction only; no orders, accounts, sizing, "
        "options, execution, persistence, or profitability promotion."
    )

    @model_validator(mode="after")
    def exact_equivalence_required(self) -> Self:
        if len(self.positions) != self.equivalence.shadow_candidate_count:
            raise ValueError("shadow candidate count does not reconcile")
        if not self.equivalence.exact_match:
            raise ValueError("Stage 14.3 requires exact Stage 13.2 equivalence")
        return self


class LiveShadowRunReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    accepted_live_bar_count: int = Field(ge=0)
    duplicate_bar_count: int = Field(ge=0)
    transition_events: tuple[ShadowTransitionEvent, ...]
    positions: tuple[ShadowPosition, ...]
    report_version: Literal["stage14-3-live-shadow-dry-run-v1"] = (
        "stage14-3-live-shadow-dry-run-v1"
    )
    caveat: str = "Market-data shadow simulation only; no trading capability."


def shadow_historical_report_hash(report: ShadowHistoricalReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()


def live_shadow_report_hash(report: LiveShadowRunReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
