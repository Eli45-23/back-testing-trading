"""Immutable models for controlled Stage 10 strategy comparisons."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.events import EmaCrossDirection
from spy_research.interactions import LevelType
from spy_research.indicators.vwap import VWAP_CONTEXT
from spy_research.research_stats import DistributionSummary
from spy_research.strategy.base_statistics import BaseStrategyHorizonStatistics
from spy_research.strategy.models import SetupDirection


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")


class EmaAlignmentState(StrEnum):
    EMA_ALIGNED = "EMA_ALIGNED"
    EMA_NOT_ALIGNED = "EMA_NOT_ALIGNED"
    EMA_UNAVAILABLE = "EMA_UNAVAILABLE"


class EmaComparisonGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    EMA_ALIGNED = "EMA_ALIGNED"
    EMA_NOT_ALIGNED = "EMA_NOT_ALIGNED"
    EMA_UNAVAILABLE = "EMA_UNAVAILABLE"


class EmaAlignmentAnnotation(BaseModel):
    """Exact confirmation-bar EMA label for one confirmed Stage 9 setup."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    ema9: Decimal | None
    ema20: Decimal | None
    alignment_state: EmaAlignmentState
    indicator_timestamp: datetime | None
    indicator_available: bool
    comparison_version: Literal["ema-direction-at-confirmation-v1"] = (
        "ema-direction-at-confirmation-v1"
    )

    @model_validator(mode="after")
    def reconcile_availability(self) -> Self:
        values_available = self.ema9 is not None and self.ema20 is not None
        if self.indicator_available != values_available:
            raise ValueError("EMA availability flag does not match values")
        if values_available:
            if self.indicator_timestamp != self.confirmation_bar_timestamp:
                raise ValueError("EMA timestamp must equal confirmation bar timestamp")
            if self.alignment_state is EmaAlignmentState.EMA_UNAVAILABLE:
                raise ValueError("available EMA pair requires a directional label")
        elif self.alignment_state is not EmaAlignmentState.EMA_UNAVAILABLE:
            raise ValueError("missing EMA value requires EMA_UNAVAILABLE")
        return self


class EmaBaselineDelta(BaseModel):
    """Simple median difference from the unchanged BASE_ALL horizon."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    median_mfe_delta: Decimal | None
    median_mae_delta: Decimal | None
    median_balance_delta: Decimal | None


class EmaAlignmentGroupStatistics(BaseModel):
    """Composition, outcomes, and baseline deltas for one EMA state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: EmaComparisonGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]
    deltas: tuple[EmaBaselineDelta, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("direction composition must match annotation count")
        if self.executable_n > self.annotation_n:
            raise ValueError("executable count cannot exceed annotation count")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("EMA comparison horizons must use frozen ordering")
        if tuple(item.horizon for item in self.deltas) != HORIZON_ORDER:
            raise ValueError("EMA comparison deltas must use frozen ordering")
        return self


class EmaDirectionGroupStatistics(BaseModel):
    """Full outcome schema for one direction and EMA state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    alignment_state: EmaAlignmentState
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def validate_horizons(self) -> Self:
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("direction horizons must use frozen ordering")
        return self


class EmaLevelAlignmentStatistics(BaseModel):
    """Per-level annotation composition and concise EOD statistics."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    alignment_state: EmaAlignmentState
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_level(self) -> Self:
        if self.executable_n > self.annotation_n:
            raise ValueError("level executable count cannot exceed annotations")
        if self.eod.horizon != "EOD":
            raise ValueError("level comparison must contain EOD statistics")
        return self


class EmaAlignmentComparisonResult(BaseModel):
    """Complete Stage 10.1 controlled descriptive comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    annotations: tuple[EmaAlignmentAnnotation, ...]
    groups: tuple[EmaAlignmentGroupStatistics, ...]
    direction_groups: tuple[EmaDirectionGroupStatistics, ...]
    level_groups: tuple[EmaLevelAlignmentStatistics, ...]
    comparison_version: Literal["controlled-ema-direction-v1"] = (
        "controlled-ema-direction-v1"
    )
    sample_warning: str = (
        "Exploratory descriptive research; not evidence of stable expectancy."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one EMA annotation")
        if len({item.setup_identity for item in self.annotations}) != len(
            self.annotations
        ):
            raise ValueError("EMA annotations require unique setup identities")
        if tuple(item.name for item in self.groups) != tuple(EmaComparisonGroupName):
            raise ValueError("EMA groups must use frozen ordering")
        if self.groups[0].annotation_n != self.confirmed_count:
            raise ValueError("BASE_ALL annotations must match confirmed count")
        if self.groups[0].executable_n != self.executable_count:
            raise ValueError("BASE_ALL executable count mismatch")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("EMA states must partition confirmed setups")
        if (
            sum(item.executable_n for item in self.groups[1:])
            != self.executable_count
        ):
            raise ValueError("EMA states must partition executable outcomes")
        observed = {
            state: sum(item.alignment_state is state for item in self.annotations)
            for state in EmaAlignmentState
        }
        for group, state in zip(
            self.groups[1:], EmaAlignmentState, strict=True
        ):
            if group.annotation_n != observed[state]:
                raise ValueError("EMA group count does not match annotations")
        expected_directions = tuple(
            (direction, state)
            for direction in SetupDirection
            for state in EmaAlignmentState
        )
        if tuple(
            (item.direction, item.alignment_state)
            for item in self.direction_groups
        ) != expected_directions:
            raise ValueError("direction groups must use frozen ordering")
        expected_levels = tuple(
            (level, state)
            for level in LevelType
            for state in EmaAlignmentState
        )
        if tuple(
            (item.level_type, item.alignment_state) for item in self.level_groups
        ) != expected_levels:
            raise ValueError("level groups must use frozen ordering")
        return self


class EmaCrossContextState(StrEnum):
    MATCHING_CROSS = "MATCHING_CROSS"
    OPPOSING_CROSS = "OPPOSING_CROSS"
    NO_PRIOR_CROSS = "NO_PRIOR_CROSS"


class EmaCrossComparisonGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    MATCHING_CROSS = "MATCHING_CROSS"
    OPPOSING_CROSS = "OPPOSING_CROSS"
    NO_PRIOR_CROSS = "NO_PRIOR_CROSS"


class EmaCrossContextAnnotation(BaseModel):
    """Most recent same-session cross known when one setup became known."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    cross_state: EmaCrossContextState
    most_recent_cross_identity: str | None
    cross_direction: EmaCrossDirection | None
    cross_timestamp: datetime | None
    cross_known_at: datetime | None
    bars_since_cross: int | None = Field(default=None, ge=0)
    minutes_since_cross_completion: int | None = Field(default=None, ge=0)
    comparison_version: Literal["ema-prior-cross-context-v1"] = (
        "ema-prior-cross-context-v1"
    )

    @model_validator(mode="after")
    def reconcile_cross_context(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("setup known-at must follow confirmation by five minutes")
        cross_values = (
            self.most_recent_cross_identity,
            self.cross_direction,
            self.cross_timestamp,
            self.cross_known_at,
            self.bars_since_cross,
            self.minutes_since_cross_completion,
        )
        if self.cross_state is EmaCrossContextState.NO_PRIOR_CROSS:
            if any(value is not None for value in cross_values):
                raise ValueError("NO_PRIOR_CROSS requires null cross fields")
            return self
        if any(value is None for value in cross_values):
            raise ValueError("cross context requires complete cross fields")
        assert self.cross_timestamp is not None
        assert self.cross_known_at is not None
        assert self.bars_since_cross is not None
        assert self.minutes_since_cross_completion is not None
        assert self.cross_direction is not None
        if self.cross_known_at != self.cross_timestamp + timedelta(minutes=5):
            raise ValueError("cross known-at must follow its candle by five minutes")
        if self.cross_known_at > self.signal_known_at:
            raise ValueError("cross context cannot use future information")
        elapsed = self.confirmation_bar_timestamp - self.cross_timestamp
        if elapsed.total_seconds() < 0 or elapsed.total_seconds() % 300:
            raise ValueError("cross recency must use whole non-negative five-minute bars")
        if self.bars_since_cross != elapsed.total_seconds() // 300:
            raise ValueError("bars since cross do not match frozen timestamps")
        if self.minutes_since_cross_completion != self.bars_since_cross * 5:
            raise ValueError("cross recency minutes must equal bars times five")
        expected = (
            EmaCrossDirection.BULLISH
            if self.direction is SetupDirection.LONG
            else EmaCrossDirection.BEARISH
        )
        matching = self.cross_direction is expected
        if matching != (self.cross_state is EmaCrossContextState.MATCHING_CROSS):
            raise ValueError("cross state does not match setup/cross directions")
        return self


class EmaCrossContextGroupStatistics(BaseModel):
    """Composition and unchanged Stage 9 outcomes for one cross state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: EmaCrossComparisonGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_executable_n: int = Field(ge=0)
    short_executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("annotation direction counts must reconcile")
        if self.long_executable_n + self.short_executable_n != self.executable_n:
            raise ValueError("executable direction counts must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("executable count cannot exceed annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("cross-context horizons must use frozen ordering")
        return self


class EmaCrossDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    cross_state: EmaCrossContextState
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_eod(self) -> Self:
        if self.eod.horizon != "EOD":
            raise ValueError("direction cross context must contain EOD statistics")
        return self


class EmaAlignmentCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    alignment_state: EmaAlignmentState
    cross_state: EmaCrossContextState
    annotation_n: int = Field(ge=0)


class EmaCrossRecencyStatistics(BaseModel):
    """One observed exact integer recency and its descriptive EOD outcomes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    bars_since_cross: int = Field(ge=0)
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_executable_n: int = Field(ge=0)
    short_executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def reconcile_recency(self) -> Self:
        if self.long_executable_n + self.short_executable_n != self.executable_n:
            raise ValueError("recency executable directions must reconcile")
        if self.eod.horizon != "EOD":
            raise ValueError("recency row must contain EOD statistics")
        return self


class EmaCrossContextComparisonResult(BaseModel):
    """Complete Stage 10.2 exact prior-cross comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    stage4_event_count: int = Field(ge=0)
    annotations: tuple[EmaCrossContextAnnotation, ...]
    groups: tuple[EmaCrossContextGroupStatistics, ...]
    direction_groups: tuple[EmaCrossDirectionStatistics, ...]
    alignment_cross_tab: tuple[EmaAlignmentCrossTabCount, ...]
    bars_since_cross_distribution: DistributionSummary
    recency_rows: tuple[EmaCrossRecencyStatistics, ...]
    comparison_version: Literal["controlled-ema-prior-cross-v1"] = (
        "controlled-ema-prior-cross-v1"
    )
    sample_warning: str = (
        "Exact recency rows are exploratory; tiny-n rows must not define a cutoff."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one cross annotation")
        if len({item.setup_identity for item in self.annotations}) != len(self.annotations):
            raise ValueError("cross annotations require unique setup identities")
        if tuple(item.name for item in self.groups) != tuple(EmaCrossComparisonGroupName):
            raise ValueError("cross groups must use frozen ordering")
        if self.groups[0].annotation_n != self.confirmed_count:
            raise ValueError("BASE_ALL annotation count mismatch")
        if self.groups[0].executable_n != self.executable_count:
            raise ValueError("BASE_ALL executable count mismatch")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("cross states must partition confirmed setups")
        if sum(item.executable_n for item in self.groups[1:]) != self.executable_count:
            raise ValueError("cross states must partition executable outcomes")
        expected_directions = tuple(
            (direction, state)
            for direction in SetupDirection
            for state in EmaCrossContextState
        )
        observed_directions = tuple(
            (item.direction, item.cross_state) for item in self.direction_groups
        )
        if observed_directions != expected_directions:
            raise ValueError("direction cross groups must use frozen ordering")
        expected_tabs = tuple(
            (alignment, state)
            for alignment in EmaAlignmentState
            for state in EmaCrossContextState
        )
        observed_tabs = tuple(
            (item.alignment_state, item.cross_state)
            for item in self.alignment_cross_tab
        )
        if observed_tabs != expected_tabs:
            raise ValueError("alignment cross-tab must use frozen ordering")
        observed_recencies = tuple(
            sorted(
                {
                    item.bars_since_cross
                    for item in self.annotations
                    if item.bars_since_cross is not None
                }
            )
        )
        if tuple(item.bars_since_cross for item in self.recency_rows) != observed_recencies:
            raise ValueError("recency rows must include each observed value in order")
        return self


class VwapAlignmentState(StrEnum):
    VWAP_ALIGNED = "VWAP_ALIGNED"
    VWAP_NOT_ALIGNED = "VWAP_NOT_ALIGNED"
    VWAP_UNAVAILABLE = "VWAP_UNAVAILABLE"


class VwapComparisonGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    VWAP_ALIGNED = "VWAP_ALIGNED"
    VWAP_NOT_ALIGNED = "VWAP_NOT_ALIGNED"
    VWAP_UNAVAILABLE = "VWAP_UNAVAILABLE"


class VwapAlignmentAnnotation(BaseModel):
    """Exact confirmation-bar price/VWAP state for one frozen setup."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    confirmation_close: Decimal
    vwap: Decimal | None
    indicator_timestamp: datetime | None
    alignment_state: VwapAlignmentState
    signed_price_vwap_distance: Decimal | None
    absolute_price_vwap_distance: Decimal | None
    directional_vwap_distance: Decimal | None
    comparison_version: Literal["price-vwap-at-confirmation-v1"] = (
        "price-vwap-at-confirmation-v1"
    )

    @model_validator(mode="after")
    def reconcile_annotation(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("setup known-at must follow confirmation by five minutes")
        distances = (
            self.signed_price_vwap_distance,
            self.absolute_price_vwap_distance,
            self.directional_vwap_distance,
        )
        if self.vwap is None:
            if self.indicator_timestamp is not None or any(
                value is not None for value in distances
            ):
                raise ValueError("unavailable VWAP requires null indicator fields")
            if self.alignment_state is not VwapAlignmentState.VWAP_UNAVAILABLE:
                raise ValueError("missing VWAP requires VWAP_UNAVAILABLE")
            return self
        if self.indicator_timestamp != self.confirmation_bar_timestamp:
            raise ValueError("VWAP timestamp must equal confirmation bar timestamp")
        if any(value is None for value in distances):
            raise ValueError("available VWAP requires all distance fields")
        with localcontext(VWAP_CONTEXT):
            signed = self.confirmation_close - self.vwap
            directional = signed if self.direction is SetupDirection.LONG else -signed
        if self.signed_price_vwap_distance != signed:
            raise ValueError("signed VWAP distance does not match values")
        if self.absolute_price_vwap_distance != abs(signed):
            raise ValueError("absolute VWAP distance does not match values")
        if self.directional_vwap_distance != directional:
            raise ValueError("directional VWAP distance does not match values")
        expected = (
            VwapAlignmentState.VWAP_ALIGNED
            if directional > 0
            else VwapAlignmentState.VWAP_NOT_ALIGNED
        )
        if self.alignment_state is not expected:
            raise ValueError("VWAP state does not match directional distance")
        return self


class VwapBaselineDelta(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    median_mfe_delta: Decimal | None
    median_mae_delta: Decimal | None
    median_balance_delta: Decimal | None


class VwapAlignmentGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: VwapComparisonGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]
    deltas: tuple[VwapBaselineDelta, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("VWAP direction composition must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("VWAP executable count cannot exceed annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("VWAP horizons must use frozen ordering")
        if tuple(item.horizon for item in self.deltas) != HORIZON_ORDER:
            raise ValueError("VWAP deltas must use frozen ordering")
        return self


class VwapDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    alignment_state: VwapAlignmentState
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_eod(self) -> Self:
        if self.eod.horizon != "EOD":
            raise ValueError("VWAP direction row must contain EOD statistics")
        return self


class VwapLevelStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    alignment_state: VwapAlignmentState
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_level(self) -> Self:
        if self.executable_n > self.annotation_n:
            raise ValueError("VWAP level executable count cannot exceed annotations")
        if self.eod.horizon != "EOD":
            raise ValueError("VWAP level row must contain EOD statistics")
        return self


class EmaVwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ema_state: EmaAlignmentState
    vwap_state: VwapAlignmentState
    annotation_n: int = Field(ge=0)


class EmaCrossVwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    cross_state: EmaCrossContextState
    vwap_state: VwapAlignmentState
    annotation_n: int = Field(ge=0)


class VwapDistanceStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection | None
    distribution: DistributionSummary
    positive_n: int = Field(ge=0)
    zero_n: int = Field(ge=0)
    negative_n: int = Field(ge=0)

    @model_validator(mode="after")
    def reconcile_counts(self) -> Self:
        if self.positive_n + self.zero_n + self.negative_n != self.distribution.n:
            raise ValueError("VWAP distance signs must reconcile")
        return self


class VwapAlignmentComparisonResult(BaseModel):
    """Complete Stage 10.3 price/VWAP controlled comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    annotations: tuple[VwapAlignmentAnnotation, ...]
    groups: tuple[VwapAlignmentGroupStatistics, ...]
    direction_groups: tuple[VwapDirectionStatistics, ...]
    level_groups: tuple[VwapLevelStatistics, ...]
    ema_vwap_cross_tab: tuple[EmaVwapCrossTabCount, ...]
    cross_context_vwap_cross_tab: tuple[EmaCrossVwapCrossTabCount, ...]
    distance_statistics: tuple[VwapDistanceStatistics, ...]
    comparison_version: Literal["controlled-price-vwap-direction-v1"] = (
        "controlled-price-vwap-direction-v1"
    )
    sample_warning: str = (
        "Exploratory descriptive research; not evidence of stable expectancy."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one VWAP annotation")
        if len({item.setup_identity for item in self.annotations}) != len(self.annotations):
            raise ValueError("VWAP annotations require unique setup identities")
        if tuple(item.name for item in self.groups) != tuple(VwapComparisonGroupName):
            raise ValueError("VWAP groups must use frozen ordering")
        if self.groups[0].annotation_n != self.confirmed_count:
            raise ValueError("VWAP BASE_ALL annotation count mismatch")
        if self.groups[0].executable_n != self.executable_count:
            raise ValueError("VWAP BASE_ALL executable count mismatch")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("VWAP states must partition annotations")
        if sum(item.executable_n for item in self.groups[1:]) != self.executable_count:
            raise ValueError("VWAP states must partition executable outcomes")
        expected_direction = tuple(
            (direction, state)
            for direction in SetupDirection
            for state in VwapAlignmentState
        )
        if tuple(
            (item.direction, item.alignment_state) for item in self.direction_groups
        ) != expected_direction:
            raise ValueError("VWAP direction rows must use frozen ordering")
        expected_levels = tuple(
            (level, state) for level in LevelType for state in VwapAlignmentState
        )
        if tuple(
            (item.level_type, item.alignment_state) for item in self.level_groups
        ) != expected_levels:
            raise ValueError("VWAP level rows must use frozen ordering")
        expected_ema_tab = tuple(
            (ema, vwap) for ema in EmaAlignmentState for vwap in VwapAlignmentState
        )
        if tuple(
            (item.ema_state, item.vwap_state) for item in self.ema_vwap_cross_tab
        ) != expected_ema_tab:
            raise ValueError("EMA/VWAP cross-tab must use frozen ordering")
        expected_cross_tab = tuple(
            (cross, vwap)
            for cross in EmaCrossContextState
            for vwap in VwapAlignmentState
        )
        if tuple(
            (item.cross_state, item.vwap_state)
            for item in self.cross_context_vwap_cross_tab
        ) != expected_cross_tab:
            raise ValueError("cross-context/VWAP table must use frozen ordering")
        if tuple(item.direction for item in self.distance_statistics) != (
            None,
            SetupDirection.LONG,
            SetupDirection.SHORT,
        ):
            raise ValueError("VWAP distance rows must be overall, LONG, SHORT")
        return self


class Ema9VwapAlignmentState(StrEnum):
    EMA9_VWAP_ALIGNED = "EMA9_VWAP_ALIGNED"
    EMA9_VWAP_NOT_ALIGNED = "EMA9_VWAP_NOT_ALIGNED"
    EMA9_VWAP_UNAVAILABLE = "EMA9_VWAP_UNAVAILABLE"


class Ema9VwapComparisonGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    EMA9_VWAP_ALIGNED = "EMA9_VWAP_ALIGNED"
    EMA9_VWAP_NOT_ALIGNED = "EMA9_VWAP_NOT_ALIGNED"
    EMA9_VWAP_UNAVAILABLE = "EMA9_VWAP_UNAVAILABLE"


class PriceEma9VwapAgreementState(StrEnum):
    BOTH_ALIGNED = "BOTH_ALIGNED"
    PRICE_ONLY_ALIGNED = "PRICE_ONLY_ALIGNED"
    EMA9_ONLY_ALIGNED = "EMA9_ONLY_ALIGNED"
    NEITHER_ALIGNED = "NEITHER_ALIGNED"
    UNAVAILABLE = "UNAVAILABLE"


class Ema9VwapAlignmentAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    ema9: Decimal | None
    vwap: Decimal | None
    indicator_timestamp: datetime | None
    alignment_state: Ema9VwapAlignmentState
    signed_ema9_vwap_distance: Decimal | None
    absolute_ema9_vwap_distance: Decimal | None
    directional_ema9_vwap_distance: Decimal | None
    comparison_version: Literal["ema9-vwap-at-confirmation-v1"] = (
        "ema9-vwap-at-confirmation-v1"
    )

    @model_validator(mode="after")
    def reconcile_annotation(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("setup known-at must follow confirmation by five minutes")
        distances = (
            self.signed_ema9_vwap_distance,
            self.absolute_ema9_vwap_distance,
            self.directional_ema9_vwap_distance,
        )
        if self.ema9 is None or self.vwap is None:
            if self.indicator_timestamp is not None or any(
                value is not None for value in distances
            ):
                raise ValueError("unavailable EMA9/VWAP requires null derived fields")
            if self.alignment_state is not Ema9VwapAlignmentState.EMA9_VWAP_UNAVAILABLE:
                raise ValueError("missing EMA9 or VWAP requires unavailable state")
            return self
        if self.indicator_timestamp != self.confirmation_bar_timestamp:
            raise ValueError("EMA9/VWAP timestamp must equal confirmation timestamp")
        if any(value is None for value in distances):
            raise ValueError("available EMA9/VWAP requires all distance fields")
        with localcontext(VWAP_CONTEXT):
            signed = self.ema9 - self.vwap
            directional = signed if self.direction is SetupDirection.LONG else -signed
        if self.signed_ema9_vwap_distance != signed:
            raise ValueError("signed EMA9/VWAP distance mismatch")
        if self.absolute_ema9_vwap_distance != abs(signed):
            raise ValueError("absolute EMA9/VWAP distance mismatch")
        if self.directional_ema9_vwap_distance != directional:
            raise ValueError("directional EMA9/VWAP distance mismatch")
        expected = (
            Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED
            if directional > 0
            else Ema9VwapAlignmentState.EMA9_VWAP_NOT_ALIGNED
        )
        if self.alignment_state is not expected:
            raise ValueError("EMA9/VWAP state does not match directional distance")
        return self


class Ema9VwapBaselineDelta(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    median_mfe_delta: Decimal | None
    median_mae_delta: Decimal | None
    median_balance_delta: Decimal | None


class Ema9VwapGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Ema9VwapComparisonGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]
    deltas: tuple[Ema9VwapBaselineDelta, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("EMA9/VWAP direction composition must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("EMA9/VWAP executable count cannot exceed annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("EMA9/VWAP horizons must use frozen ordering")
        if tuple(item.horizon for item in self.deltas) != HORIZON_ORDER:
            raise ValueError("EMA9/VWAP deltas must use frozen ordering")
        return self


class Ema9VwapDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    alignment_state: Ema9VwapAlignmentState
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_eod(self) -> Self:
        if self.eod.horizon != "EOD":
            raise ValueError("EMA9/VWAP direction row must contain EOD")
        return self


class Ema9VwapLevelStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    alignment_state: Ema9VwapAlignmentState
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_level(self) -> Self:
        if self.executable_n > self.annotation_n:
            raise ValueError("EMA9/VWAP level executable count exceeds annotations")
        if self.eod.horizon != "EOD":
            raise ValueError("EMA9/VWAP level row must contain EOD")
        return self


class PriceVwapEma9VwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    price_vwap_state: VwapAlignmentState
    ema9_vwap_state: Ema9VwapAlignmentState
    annotation_n: int = Field(ge=0)


class EmaAlignmentEma9VwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ema_alignment_state: EmaAlignmentState
    ema9_vwap_state: Ema9VwapAlignmentState
    annotation_n: int = Field(ge=0)


class CrossContextEma9VwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    cross_state: EmaCrossContextState
    ema9_vwap_state: Ema9VwapAlignmentState
    annotation_n: int = Field(ge=0)


class PriceEma9VwapAgreementStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    state: PriceEma9VwapAgreementState
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def reconcile_agreement(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("agreement direction composition must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("agreement executable count exceeds annotations")
        if self.eod.horizon != "EOD":
            raise ValueError("agreement row must contain EOD")
        return self


class Ema9VwapDistanceStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection | None
    distribution: DistributionSummary
    positive_n: int = Field(ge=0)
    zero_n: int = Field(ge=0)
    negative_n: int = Field(ge=0)
    unavailable_n: int = Field(ge=0)

    @model_validator(mode="after")
    def reconcile_counts(self) -> Self:
        if self.positive_n + self.zero_n + self.negative_n != self.distribution.n:
            raise ValueError("EMA9/VWAP distance signs must reconcile")
        return self


class Ema9VwapAlignmentComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    annotations: tuple[Ema9VwapAlignmentAnnotation, ...]
    groups: tuple[Ema9VwapGroupStatistics, ...]
    direction_groups: tuple[Ema9VwapDirectionStatistics, ...]
    level_groups: tuple[Ema9VwapLevelStatistics, ...]
    price_vwap_cross_tab: tuple[PriceVwapEma9VwapCrossTabCount, ...]
    ema_alignment_cross_tab: tuple[EmaAlignmentEma9VwapCrossTabCount, ...]
    cross_context_cross_tab: tuple[CrossContextEma9VwapCrossTabCount, ...]
    agreement_groups: tuple[PriceEma9VwapAgreementStatistics, ...]
    distance_statistics: tuple[Ema9VwapDistanceStatistics, ...]
    comparison_version: Literal["controlled-ema9-vwap-direction-v1"] = (
        "controlled-ema9-vwap-direction-v1"
    )
    sample_warning: str = (
        "Exploratory descriptive research; not evidence of stable expectancy."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one EMA9/VWAP annotation")
        if len({item.setup_identity for item in self.annotations}) != len(self.annotations):
            raise ValueError("EMA9/VWAP annotations require unique identities")
        if tuple(item.name for item in self.groups) != tuple(
            Ema9VwapComparisonGroupName
        ):
            raise ValueError("EMA9/VWAP groups must use frozen ordering")
        if self.groups[0].annotation_n != self.confirmed_count:
            raise ValueError("EMA9/VWAP BASE_ALL annotation mismatch")
        if self.groups[0].executable_n != self.executable_count:
            raise ValueError("EMA9/VWAP BASE_ALL executable mismatch")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("EMA9/VWAP states must partition annotations")
        if sum(item.executable_n for item in self.groups[1:]) != self.executable_count:
            raise ValueError("EMA9/VWAP states must partition outcomes")
        if sum(item.annotation_n for item in self.agreement_groups) != self.confirmed_count:
            raise ValueError("agreement states must partition annotations")
        if sum(item.executable_n for item in self.agreement_groups) != self.executable_count:
            raise ValueError("agreement states must partition executable outcomes")
        if tuple(item.state for item in self.agreement_groups) != tuple(
            PriceEma9VwapAgreementState
        ):
            raise ValueError("agreement groups must use frozen ordering")
        expected_directions = tuple(
            (direction, state)
            for direction in SetupDirection
            for state in Ema9VwapAlignmentState
        )
        if tuple(
            (item.direction, item.alignment_state) for item in self.direction_groups
        ) != expected_directions:
            raise ValueError("EMA9/VWAP direction rows must use frozen ordering")
        expected_levels = tuple(
            (level, state)
            for level in LevelType
            for state in Ema9VwapAlignmentState
        )
        if tuple(
            (item.level_type, item.alignment_state) for item in self.level_groups
        ) != expected_levels:
            raise ValueError("EMA9/VWAP level rows must use frozen ordering")
        for table in (
            self.price_vwap_cross_tab,
            self.ema_alignment_cross_tab,
            self.cross_context_cross_tab,
        ):
            if sum(item.annotation_n for item in table) != self.confirmed_count:
                raise ValueError("EMA9/VWAP cross-tab must reconcile annotations")
        if tuple(item.direction for item in self.distance_statistics) != (
            None,
            SetupDirection.LONG,
            SetupDirection.SHORT,
        ):
            raise ValueError("EMA9/VWAP distance rows must be overall, LONG, SHORT")
        direction_counts = (
            self.confirmed_count,
            sum(item.direction is SetupDirection.LONG for item in self.annotations),
            sum(item.direction is SetupDirection.SHORT for item in self.annotations),
        )
        for item, population_n in zip(
            self.distance_statistics, direction_counts, strict=True
        ):
            if item.distribution.n + item.unavailable_n != population_n:
                raise ValueError("EMA9/VWAP distance availability must reconcile")
        return self


class Ema9VwapCrossDirection(StrEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class Ema9VwapCrossEvent(BaseModel):
    """One completed-candle EMA9/VWAP relationship reversal."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: Ema9VwapCrossDirection
    cross_timestamp: datetime
    cross_known_at: datetime
    ema9: Decimal
    vwap: Decimal
    prior_ema9: Decimal
    prior_vwap: Decimal
    signed_distance: Decimal
    event_version: Literal["ema9-vwap-completed-candle-cross-v1"] = (
        "ema9-vwap-completed-candle-cross-v1"
    )

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        if self.cross_timestamp.utcoffset() is None:
            raise ValueError("EMA9/VWAP cross timestamp must be timezone-aware")
        if self.cross_known_at != self.cross_timestamp + timedelta(minutes=5):
            raise ValueError("EMA9/VWAP cross known-at must follow by five minutes")
        with localcontext(VWAP_CONTEXT):
            if self.signed_distance != self.ema9 - self.vwap:
                raise ValueError("EMA9/VWAP signed distance mismatch")
        payload = "|".join(
            (
                self.symbol,
                self.cross_timestamp.isoformat(),
                self.direction.value,
                self.event_version,
            )
        )
        if self.event_identity != sha256(payload.encode()).hexdigest():
            raise ValueError("EMA9/VWAP event identity mismatch")
        return self


class Ema9VwapCrossSessionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    bullish_crosses: int = Field(ge=0)
    bearish_crosses: int = Field(ge=0)
    total_crosses: int = Field(ge=0)
    first_cross_timestamp: datetime | None
    last_cross_timestamp: datetime | None


class Ema9VwapCrossContextState(StrEnum):
    MATCHING_EMA9_VWAP_CROSS = "MATCHING_EMA9_VWAP_CROSS"
    OPPOSING_EMA9_VWAP_CROSS = "OPPOSING_EMA9_VWAP_CROSS"
    NO_PRIOR_EMA9_VWAP_CROSS = "NO_PRIOR_EMA9_VWAP_CROSS"


class Ema9VwapCrossGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    MATCHING_EMA9_VWAP_CROSS = "MATCHING_EMA9_VWAP_CROSS"
    OPPOSING_EMA9_VWAP_CROSS = "OPPOSING_EMA9_VWAP_CROSS"
    NO_PRIOR_EMA9_VWAP_CROSS = "NO_PRIOR_EMA9_VWAP_CROSS"


class Ema9VwapCrossContextAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    cross_state: Ema9VwapCrossContextState
    most_recent_cross_identity: str | None
    cross_direction: Ema9VwapCrossDirection | None
    cross_timestamp: datetime | None
    cross_known_at: datetime | None
    bars_since_cross: int | None = Field(default=None, ge=0)
    minutes_since_cross_completion: int | None = Field(default=None, ge=0)
    comparison_version: Literal["ema9-vwap-prior-cross-context-v1"] = (
        "ema9-vwap-prior-cross-context-v1"
    )

    @model_validator(mode="after")
    def reconcile_context(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("setup known-at must follow confirmation by five minutes")
        cross_fields = (
            self.most_recent_cross_identity,
            self.cross_direction,
            self.cross_timestamp,
            self.cross_known_at,
            self.bars_since_cross,
            self.minutes_since_cross_completion,
        )
        if self.cross_state is Ema9VwapCrossContextState.NO_PRIOR_EMA9_VWAP_CROSS:
            if any(value is not None for value in cross_fields):
                raise ValueError("no-prior EMA9/VWAP cross requires null fields")
            return self
        if any(value is None for value in cross_fields):
            raise ValueError("EMA9/VWAP cross context requires complete fields")
        assert self.cross_timestamp is not None
        assert self.cross_known_at is not None
        assert self.bars_since_cross is not None
        assert self.minutes_since_cross_completion is not None
        assert self.cross_direction is not None
        if self.cross_known_at != self.cross_timestamp + timedelta(minutes=5):
            raise ValueError("cross known-at must follow timestamp by five minutes")
        if self.cross_known_at > self.signal_known_at:
            raise ValueError("future EMA9/VWAP cross cannot annotate setup")
        elapsed = self.confirmation_bar_timestamp - self.cross_timestamp
        if elapsed.total_seconds() < 0 or elapsed.total_seconds() % 300:
            raise ValueError("EMA9/VWAP cross recency must use whole five-minute bars")
        if self.bars_since_cross != elapsed.total_seconds() // 300:
            raise ValueError("EMA9/VWAP bars-since-cross mismatch")
        if self.minutes_since_cross_completion != self.bars_since_cross * 5:
            raise ValueError("EMA9/VWAP minutes-since-cross mismatch")
        expected = (
            Ema9VwapCrossDirection.BULLISH
            if self.direction is SetupDirection.LONG
            else Ema9VwapCrossDirection.BEARISH
        )
        matching = self.cross_direction is expected
        if matching != (
            self.cross_state
            is Ema9VwapCrossContextState.MATCHING_EMA9_VWAP_CROSS
        ):
            raise ValueError("EMA9/VWAP cross direction/context mismatch")
        return self


class Ema9VwapCrossGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Ema9VwapCrossGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("EMA9/VWAP cross group directions must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("EMA9/VWAP executable count exceeds annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("EMA9/VWAP cross horizons must use frozen ordering")
        return self


class Ema9VwapCrossDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    cross_state: Ema9VwapCrossContextState
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics


class Ema9VwapCrossRecencyStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    bars_since_cross: int = Field(ge=0)
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_executable_n: int = Field(ge=0)
    short_executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics


class Ema9VwapStateCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    alignment_state: Ema9VwapAlignmentState
    cross_state: Ema9VwapCrossContextState
    annotation_n: int = Field(ge=0)


class PriceVwapEma9CrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    price_vwap_state: VwapAlignmentState
    cross_state: Ema9VwapCrossContextState
    annotation_n: int = Field(ge=0)


class EmaAlignmentEma9CrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ema_alignment_state: EmaAlignmentState
    cross_state: Ema9VwapCrossContextState
    annotation_n: int = Field(ge=0)


class CrossSystemCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ema9_20_cross_state: EmaCrossContextState
    ema9_vwap_cross_state: Ema9VwapCrossContextState
    annotation_n: int = Field(ge=0)


class Ema9VwapCrossContextComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    symbol: Literal["SPY"] = "SPY"
    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    events: tuple[Ema9VwapCrossEvent, ...]
    event_sessions: tuple[Ema9VwapCrossSessionSummary, ...]
    bullish_event_count: int = Field(ge=0)
    bearish_event_count: int = Field(ge=0)
    annotations: tuple[Ema9VwapCrossContextAnnotation, ...]
    groups: tuple[Ema9VwapCrossGroupStatistics, ...]
    direction_groups: tuple[Ema9VwapCrossDirectionStatistics, ...]
    bars_since_cross_distribution: DistributionSummary
    recency_rows: tuple[Ema9VwapCrossRecencyStatistics, ...]
    ema9_vwap_state_cross_tab: tuple[Ema9VwapStateCrossTabCount, ...]
    price_vwap_cross_tab: tuple[PriceVwapEma9CrossTabCount, ...]
    ema_alignment_cross_tab: tuple[EmaAlignmentEma9CrossTabCount, ...]
    cross_system_cross_tab: tuple[CrossSystemCrossTabCount, ...]
    comparison_version: Literal["controlled-ema9-vwap-cross-context-v1"] = (
        "controlled-ema9-vwap-cross-context-v1"
    )
    sample_warning: str = (
        "Exact recency is exploratory; tiny-n rows must not define a cutoff."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if self.bullish_event_count + self.bearish_event_count != len(self.events):
            raise ValueError("EMA9/VWAP event directions must reconcile")
        if len({item.event_identity for item in self.events}) != len(self.events):
            raise ValueError("EMA9/VWAP event identities must be unique")
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires cross context")
        if tuple(item.name for item in self.groups) != tuple(Ema9VwapCrossGroupName):
            raise ValueError("EMA9/VWAP cross groups must use frozen ordering")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("EMA9/VWAP contexts must partition annotations")
        if sum(item.executable_n for item in self.groups[1:]) != self.executable_count:
            raise ValueError("EMA9/VWAP contexts must partition outcomes")
        for table in (
            self.ema9_vwap_state_cross_tab,
            self.price_vwap_cross_tab,
            self.ema_alignment_cross_tab,
            self.cross_system_cross_tab,
        ):
            if sum(item.annotation_n for item in table) != self.confirmed_count:
                raise ValueError("EMA9/VWAP cross-tab must reconcile annotations")
        observed = tuple(
            sorted(
                {
                    item.bars_since_cross
                    for item in self.annotations
                    if item.bars_since_cross is not None
                }
            )
        )
        if tuple(item.bars_since_cross for item in self.recency_rows) != observed:
            raise ValueError("EMA9/VWAP recency rows must use observed ordering")
        return self
