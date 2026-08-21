"""Immutable strategy-candidate models derived from frozen research objects."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.interactions import (
    ImmediateState,
    InteractionType,
    LevelType,
    RetestState,
)


class SetupDirection(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class ConfirmationType(StrEnum):
    IMMEDIATE_HOLD = "IMMEDIATE_HOLD"
    RETEST_HOLD = "RETEST_HOLD"


class BaseSetupStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    REJECTED_IMMEDIATE_FAILURE = "REJECTED_IMMEDIATE_FAILURE"
    REJECTED_RETEST_FAILURE = "REJECTED_RETEST_FAILURE"
    EQUAL_ONLY = "EQUAL_ONLY"
    NO_RETEST = "NO_RETEST"
    INCOMPLETE = "INCOMPLETE"


class BasePriceActionCandidate(BaseModel):
    """One accounted Stage 8.2 break seed and its Stage 9.1 disposition."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    break_interaction_identity: str
    follow_through_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    level_type: LevelType
    level_price: Decimal
    direction: SetupDirection
    break_interaction_type: Literal[
        InteractionType.CLOSE_THROUGH_ABOVE,
        InteractionType.CLOSE_THROUGH_BELOW,
    ]
    break_timestamp: datetime
    break_completed_at: datetime
    exact_immediate_state: ImmediateState
    exact_retest_state: RetestState
    status: BaseSetupStatus
    confirmation_type: ConfirmationType | None = None
    confirmation_bar_timestamp: datetime | None = None
    signal_known_at: datetime | None = None
    earliest_entry_timestamp: datetime | None = None
    retest_bar_offset: int | None = Field(default=None, ge=1, le=3)
    same_session_executable: bool
    strategy_version: Literal["base-exact-price-v1"] = "base-exact-price-v1"

    @model_validator(mode="after")
    def validate_confirmation_fields(self) -> Self:
        confirmation_fields = (
            self.confirmation_type,
            self.confirmation_bar_timestamp,
            self.signal_known_at,
            self.earliest_entry_timestamp,
        )
        if self.status is BaseSetupStatus.CONFIRMED:
            if any(value is None for value in confirmation_fields):
                raise ValueError("confirmed setups require complete timing fields")
            if self.signal_known_at != self.earliest_entry_timestamp:
                raise ValueError("earliest entry timestamp must equal signal-known time")
        elif any(value is not None for value in confirmation_fields):
            raise ValueError("non-confirmed candidates cannot contain confirmation timing")
        if self.confirmation_type is ConfirmationType.RETEST_HOLD:
            if self.retest_bar_offset is None:
                raise ValueError("retest confirmation requires its frozen bar offset")
        elif self.confirmation_type is ConfirmationType.IMMEDIATE_HOLD:
            if self.retest_bar_offset is not None:
                raise ValueError("immediate confirmation cannot use a retest offset")
        elif self.retest_bar_offset is not None:
            raise ValueError("non-confirmed candidates cannot use a retest offset")
        return self


class BasePriceActionResult(BaseModel):
    """Complete Stage 9.1 accounting over the Stage 8.2 break universe."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    candidates: tuple[BasePriceActionCandidate, ...]

    @model_validator(mode="after")
    def reconcile_counts(self) -> Self:
        if self.confirmed_count + self.non_confirmed_count != self.seed_count:
            raise ValueError("confirmed and non-confirmed counts must reconcile")
        if len(self.candidates) != self.seed_count:
            raise ValueError("every Stage 8.2 seed requires one candidate record")
        observed = sum(
            item.status is BaseSetupStatus.CONFIRMED for item in self.candidates
        )
        if observed != self.confirmed_count:
            raise ValueError("confirmed count does not match candidate statuses")
        return self


class EntryStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    ENTRY_UNAVAILABLE_SESSION_END = "ENTRY_UNAVAILABLE_SESSION_END"
    ENTRY_REFERENCE_MISSING = "ENTRY_REFERENCE_MISSING"


class SetupEntryReference(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    signal_known_at: datetime
    earliest_entry_timestamp: datetime
    entry_status: EntryStatus
    entry_reference_timestamp: datetime | None = None
    entry_reference_price: Decimal | None = None
    entry_delay_minutes: int | None = Field(default=None, ge=0)
    source_timeframe: Literal["1Min"] = "1Min"
    source_session: Literal["RTH"] = "RTH"
    entry_reference_version: Literal["first-rth-1m-open-at-or-after-signal-v1"] = (
        "first-rth-1m-open-at-or-after-signal-v1"
    )

    @model_validator(mode="after")
    def validate_status_fields(self) -> Self:
        reference_fields = (
            self.entry_reference_timestamp,
            self.entry_reference_price,
            self.entry_delay_minutes,
        )
        if self.entry_status is EntryStatus.AVAILABLE:
            if any(value is None for value in reference_fields):
                raise ValueError("available entries require complete reference fields")
            assert self.entry_reference_timestamp is not None
            assert self.entry_delay_minutes is not None
            if self.entry_reference_timestamp < self.earliest_entry_timestamp:
                raise ValueError("entry reference cannot precede earliest entry time")
            expected_delay = int(
                (
                    self.entry_reference_timestamp - self.earliest_entry_timestamp
                ).total_seconds()
                // 60
            )
            if self.entry_delay_minutes != expected_delay:
                raise ValueError("entry delay does not match reference timestamp")
        elif any(value is not None for value in reference_fields):
            raise ValueError("unavailable entries cannot contain reference fields")
        if self.signal_known_at != self.earliest_entry_timestamp:
            raise ValueError("frozen Stage 9.1 entry timing must remain unchanged")
        return self


class SetupHorizonOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    requested_minutes: int = Field(ge=0)
    available_minutes: int = Field(ge=0)
    complete: bool
    mfe: Decimal
    mae: Decimal
    mfe_timestamp: datetime
    mae_timestamp: datetime


class SetupOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    setup: BasePriceActionCandidate
    entry_reference: SetupEntryReference
    five: SetupHorizonOutcome | None = None
    fifteen: SetupHorizonOutcome | None = None
    thirty: SetupHorizonOutcome | None = None
    sixty: SetupHorizonOutcome | None = None
    eod: SetupHorizonOutcome | None = None
    outcome_version: Literal["base-setup-entry-rth-1m-mfe-mae-v1"] = (
        "base-setup-entry-rth-1m-mfe-mae-v1"
    )

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.setup.setup_identity != self.setup_identity:
            raise ValueError("embedded setup identity mismatch")
        if self.entry_reference.setup_identity != self.setup_identity:
            raise ValueError("entry-reference setup identity mismatch")
        if self.setup.status is not BaseSetupStatus.CONFIRMED:
            raise ValueError("Stage 9.2 outcomes require confirmed Stage 9.1 setups")
        has_outcomes = any(
            item is not None
            for item in (self.five, self.fifteen, self.thirty, self.sixty, self.eod)
        )
        if self.entry_reference.entry_status is EntryStatus.AVAILABLE:
            if not all(
                item is not None
                for item in (self.five, self.fifteen, self.thirty, self.sixty, self.eod)
            ):
                raise ValueError("available entries require every outcome horizon")
        elif has_outcomes:
            raise ValueError("unavailable entries cannot contain excursion outcomes")
        return self


class SetupOutcomeResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    confirmed_setup_count: int = Field(ge=0)
    available_entry_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    outcomes: tuple[SetupOutcome, ...]

    @model_validator(mode="after")
    def reconcile_counts(self) -> Self:
        if len(self.outcomes) != self.confirmed_setup_count:
            raise ValueError("every confirmed setup requires one outcome record")
        if (
            self.available_entry_count
            + self.session_end_unavailable_count
            + self.missing_entry_count
            != self.confirmed_setup_count
        ):
            raise ValueError("entry statuses must reconcile to confirmed setups")
        observed = {
            status: sum(
                item.entry_reference.entry_status is status for item in self.outcomes
            )
            for status in EntryStatus
        }
        if observed[EntryStatus.AVAILABLE] != self.available_entry_count:
            raise ValueError("available-entry count mismatch")
        if (
            observed[EntryStatus.ENTRY_UNAVAILABLE_SESSION_END]
            != self.session_end_unavailable_count
        ):
            raise ValueError("session-end unavailable count mismatch")
        if observed[EntryStatus.ENTRY_REFERENCE_MISSING] != self.missing_entry_count:
            raise ValueError("missing-entry count mismatch")
        return self
