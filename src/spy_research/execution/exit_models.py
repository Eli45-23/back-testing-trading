"""Immutable models for the controlled Stage 13.2 exit comparison."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.execution.models import (
    AmbiguityMetadata,
    AtrStopModel,
    FixedRiskSimulationReport,
    PopulationReconciliation,
    RiskTargetModel,
    StrategyPopulation,
)
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import DistributionSummary
from spy_research.strategy.models import SetupDirection


class ExitComparisonInputError(ValueError):
    """Frozen Stage 13.2 inputs cannot form a trustworthy comparison."""


class ExitFamily(StrEnum):
    FIXED_R_CONTROL = "FIXED_R_CONTROL"
    OPPOSITE_EMA9_20_CROSS = "OPPOSITE_EMA9_20_CROSS"
    OPPOSITE_EMA9_VWAP_CROSS = "OPPOSITE_EMA9_VWAP_CROSS"
    OPPOSITE_EMA20_VWAP_CROSS = "OPPOSITE_EMA20_VWAP_CROSS"
    TIME_EXIT = "TIME_EXIT"
    NEXT_OBJECTIVE_LEVEL = "NEXT_OBJECTIVE_LEVEL"


class ExitModelStatus(StrEnum):
    REALIZED = "REALIZED"
    AMBIGUOUS_BOTH_TOUCHED = "AMBIGUOUS_BOTH_TOUCHED"
    UNAVAILABLE_ATR = "UNAVAILABLE_ATR"
    UNAVAILABLE_OBJECTIVE = "UNAVAILABLE_OBJECTIVE"


class ExitModelExitReason(StrEnum):
    STOP = "STOP"
    FIXED_R_TARGET = "FIXED_R_TARGET"
    OPPOSITE_EMA9_20_CROSS = "OPPOSITE_EMA9_20_CROSS"
    OPPOSITE_EMA9_VWAP_CROSS = "OPPOSITE_EMA9_VWAP_CROSS"
    OPPOSITE_EMA20_VWAP_CROSS = "OPPOSITE_EMA20_VWAP_CROSS"
    TIME_15M = "TIME_15M"
    TIME_30M = "TIME_30M"
    TIME_60M = "TIME_60M"
    NEXT_OBJECTIVE_LEVEL = "NEXT_OBJECTIVE_LEVEL"
    EOD_CLOSE = "EOD_CLOSE"
    AMBIGUOUS_BOTH_TOUCHED = "AMBIGUOUS_BOTH_TOUCHED"
    UNAVAILABLE_ATR = "UNAVAILABLE_ATR"
    UNAVAILABLE_OBJECTIVE = "UNAVAILABLE_OBJECTIVE"


class ExitModelVariant(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    variant_id: str
    family: ExitFamily
    stop_model: AtrStopModel
    stop_multiplier: Decimal = Field(gt=0)
    fixed_target_model: RiskTargetModel | None = None
    fixed_target_r: Decimal | None = Field(default=None, gt=0)
    time_minutes: Literal[15, 30, 60] | None = None
    corresponding_control_variant_ids: tuple[str, ...]

    @model_validator(mode="after")
    def reconcile_variant(self) -> Self:
        if self.stop_multiplier != self.stop_model.multiplier:
            raise ValueError("exit-model stop multiplier mismatch")
        control = self.family is ExitFamily.FIXED_R_CONTROL
        if control != (self.fixed_target_model is not None):
            raise ValueError("only control variants may contain a fixed target")
        if control:
            assert self.fixed_target_model is not None
            if self.fixed_target_r != self.fixed_target_model.multiple:
                raise ValueError("control target R mismatch")
            if self.time_minutes is not None:
                raise ValueError("control variant cannot contain a time exit")
            if self.corresponding_control_variant_ids != (self.variant_id,):
                raise ValueError("control variant must correspond to itself")
        else:
            if self.fixed_target_r is not None:
                raise ValueError("new exit variant cannot contain fixed target R")
            is_time = self.family is ExitFamily.TIME_EXIT
            if is_time != (self.time_minutes is not None):
                raise ValueError("only time variants require a frozen minute value")
            if len(self.corresponding_control_variant_ids) != 5:
                raise ValueError("new variants require all five same-stop controls")
        expected = exit_variant_identity(
            self.family,
            self.stop_model,
            fixed_target=self.fixed_target_model,
            time_minutes=self.time_minutes,
        )
        if self.variant_id != expected:
            raise ValueError("exit-model variant identity mismatch")
        return self


def exit_variant_identity(
    family: ExitFamily,
    stop_model: AtrStopModel,
    *,
    fixed_target: RiskTargetModel | None = None,
    time_minutes: int | None = None,
) -> str:
    suffix = (
        fixed_target.value
        if fixed_target is not None
        else f"{time_minutes}M"
        if time_minutes is not None
        else "NO_FIXED_TARGET"
    )
    return f"{family.value}:{stop_model.value}:{suffix}"


class NormalizedCrossExitEvent(BaseModel):
    """Lossless timing projection of an accepted completed-candle cross."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_identity: str
    family: Literal[
        ExitFamily.OPPOSITE_EMA9_20_CROSS,
        ExitFamily.OPPOSITE_EMA9_VWAP_CROSS,
        ExitFamily.OPPOSITE_EMA20_VWAP_CROSS,
    ]
    session_date: date
    direction: Literal["BULLISH", "BEARISH"]
    cross_timestamp: datetime
    cross_known_at: datetime

    @model_validator(mode="after")
    def known_after_completion(self) -> Self:
        from datetime import timedelta

        if self.cross_timestamp.utcoffset() is None:
            raise ValueError("cross timestamps must be timezone-aware")
        if self.cross_known_at != self.cross_timestamp + timedelta(minutes=5):
            raise ValueError("cross-known time must be five minutes after completion")
        return self


class ScheduledExit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    executable_at: datetime
    reason: Literal[
        ExitModelExitReason.OPPOSITE_EMA9_20_CROSS,
        ExitModelExitReason.OPPOSITE_EMA9_VWAP_CROSS,
        ExitModelExitReason.OPPOSITE_EMA20_VWAP_CROSS,
        ExitModelExitReason.TIME_15M,
        ExitModelExitReason.TIME_30M,
        ExitModelExitReason.TIME_60M,
    ]
    source_event_identity: str | None = None
    source_cross_timestamp: datetime | None = None


class ExitModelTradePath(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    session_date: date
    direction: SetupDirection
    level_type: LevelType
    strategy_population: StrategyPopulation
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    entry_timestamp: datetime
    entry_price: Decimal
    confirmation_atr: Decimal | None
    variant: ExitModelVariant
    stop_price: Decimal | None
    initial_risk: Decimal | None
    objective_price: Decimal | None
    objective_level_types: tuple[LevelType, ...] = ()
    scheduled_exit: ScheduledExit | None = None
    atr_eligible: bool
    target_context_eligible: bool
    status: ExitModelStatus
    exit_timestamp: datetime | None
    exit_price: Decimal | None
    exit_reason: ExitModelExitReason
    price_pnl: Decimal | None
    r_multiple: Decimal | None
    minutes_in_trade: int | None = Field(default=None, ge=0)
    bars_observed: int = Field(ge=0)
    ambiguity: AmbiguityMetadata | None = None
    execution_version: Literal["controlled-exit-rth-1m-v1"] = (
        "controlled-exit-rth-1m-v1"
    )

    @model_validator(mode="after")
    def reconcile(self) -> Self:
        if self.variant.family is ExitFamily.FIXED_R_CONTROL:
            raise ValueError("Stage 13.1 controls remain in their accepted report")
        if self.atr_eligible != (
            self.confirmation_atr is not None and self.confirmation_atr > 0
        ):
            raise ValueError("ATR eligibility mismatch")
        unavailable = self.status in (
            ExitModelStatus.UNAVAILABLE_ATR,
            ExitModelStatus.UNAVAILABLE_OBJECTIVE,
        )
        if unavailable:
            if any(
                item is not None
                for item in (
                    self.exit_timestamp,
                    self.exit_price,
                    self.price_pnl,
                    self.r_multiple,
                    self.minutes_in_trade,
                    self.ambiguity,
                )
            ) or self.bars_observed:
                raise ValueError("unavailable variant cannot contain a trade path")
            expected = (
                ExitModelExitReason.UNAVAILABLE_ATR
                if self.status is ExitModelStatus.UNAVAILABLE_ATR
                else ExitModelExitReason.UNAVAILABLE_OBJECTIVE
            )
            if self.exit_reason is not expected:
                raise ValueError("unavailable status/reason mismatch")
            return self
        if not self.atr_eligible or not self.target_context_eligible:
            raise ValueError("simulated exit requires ATR and context eligibility")
        if self.stop_price is None or self.initial_risk is None:
            raise ValueError("simulated exit requires initial stop risk")
        assert self.confirmation_atr is not None
        with localcontext(ATR_CONTEXT):
            expected_risk = self.confirmation_atr * self.variant.stop_multiplier
            expected_stop = (
                self.entry_price - expected_risk
                if self.direction is SetupDirection.LONG
                else self.entry_price + expected_risk
            )
        if self.initial_risk != expected_risk or self.stop_price != expected_stop:
            raise ValueError("initial stop risk must use confirmation ATR exactly")
        if self.status is ExitModelStatus.AMBIGUOUS_BOTH_TOUCHED:
            if self.exit_reason is not ExitModelExitReason.AMBIGUOUS_BOTH_TOUCHED:
                raise ValueError("ambiguity reason mismatch")
            if self.ambiguity is None or self.exit_timestamp is None:
                raise ValueError("ambiguity requires timestamp and OHLC")
            if any(
                item is not None
                for item in (self.exit_price, self.price_pnl, self.r_multiple)
            ):
                raise ValueError("ambiguous path cannot invent a realized exit")
            return self
        if self.status is not ExitModelStatus.REALIZED:
            raise ValueError("unknown exit-model status")
        if any(
            item is None
            for item in (
                self.exit_timestamp,
                self.exit_price,
                self.price_pnl,
                self.r_multiple,
                self.minutes_in_trade,
            )
        ):
            raise ValueError("realized exit requires complete outcome fields")
        if self.ambiguity is not None:
            raise ValueError("realized exit cannot contain ambiguity")
        assert self.exit_timestamp is not None
        assert self.exit_price is not None
        assert self.price_pnl is not None
        assert self.r_multiple is not None
        if self.exit_timestamp < self.entry_timestamp:
            raise ValueError("exit cannot precede entry")
        with localcontext(ATR_CONTEXT):
            expected_pnl = (
                self.exit_price - self.entry_price
                if self.direction is SetupDirection.LONG
                else self.entry_price - self.exit_price
            )
            expected_r = (
                Decimal("-1")
                if self.exit_reason is ExitModelExitReason.STOP
                else expected_pnl / self.initial_risk
            )
        if self.price_pnl != expected_pnl or self.r_multiple != expected_r:
            raise ValueError("realized P/L and R must reconcile exactly")
        return self


class ExitMonthlyStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    month: str
    trade_n: int = Field(ge=0)
    mean_r: Decimal | None
    median_r: Decimal | None
    positive_n: int = Field(ge=0)
    negative_n: int = Field(ge=0)
    zero_n: int = Field(ge=0)


class ExitSliceStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    trade_n: int = Field(ge=0)
    r_multiple: DistributionSummary


class ExitPartitionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    partition: Literal["EXPANDED", "JANUARY_JULY", "AUGUST_DEVELOPMENT"]
    trade_n: int = Field(ge=0)
    mean_r: Decimal | None
    median_r: Decimal | None


class LeaveOneMonthOutR(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    excluded_month: str
    trade_n: int = Field(ge=0)
    mean_r: Decimal | None
    median_r: Decimal | None


class ExitVariantStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_population: StrategyPopulation
    variant: ExitModelVariant
    membership_n: int = Field(ge=0)
    atr_eligible_n: int = Field(ge=0)
    target_context_eligible_n: int = Field(ge=0)
    realized_n: int = Field(ge=0)
    unavailable_n: int = Field(ge=0)
    ambiguous_n: int = Field(ge=0)
    stop_exit_n: int = Field(ge=0)
    target_exit_n: int = Field(ge=0)
    cross_exit_n: int = Field(ge=0)
    time_exit_n: int = Field(ge=0)
    eod_exit_n: int = Field(ge=0)
    r_multiple: DistributionSummary
    r_standard_deviation: Decimal | None
    positive_r_n: int = Field(ge=0)
    zero_r_n: int = Field(ge=0)
    negative_r_n: int = Field(ge=0)
    win_rate_percentage: Decimal | None
    loss_rate_percentage: Decimal | None
    holding_minutes: DistributionSummary
    monthly: tuple[ExitMonthlyStatistics, ...]
    positive_month_n: int = Field(ge=0)
    negative_month_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    direction_composition: tuple[ExitSliceStatistics, ...]
    level_composition: tuple[tuple[LevelType, int], ...]
    partitions: tuple[ExitPartitionStatistics, ...]
    leave_one_month_out: tuple[LeaveOneMonthOutR, ...]

    @model_validator(mode="after")
    def reconcile_statistics(self) -> Self:
        if self.realized_n + self.unavailable_n + self.ambiguous_n != self.membership_n:
            raise ValueError("exit status counts must partition membership")
        exits = (
            self.stop_exit_n
            + self.target_exit_n
            + self.cross_exit_n
            + self.time_exit_n
            + self.eod_exit_n
        )
        if exits != self.realized_n:
            raise ValueError("exit-reason counts must partition realized trades")
        if self.positive_r_n + self.zero_r_n + self.negative_r_n != self.realized_n:
            raise ValueError("R signs must partition realized trades")
        if sum(item.trade_n for item in self.monthly) != self.realized_n:
            raise ValueError("monthly rows must partition realized trades")
        if not self.partitions or self.partitions[0].trade_n != self.realized_n:
            raise ValueError("expanded partition must reproduce realized trades")
        if sum(count for _level, count in self.level_composition) != self.realized_n:
            raise ValueError("level composition must partition realized trades")
        return self


class ExitBootstrapInterval(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: Literal["MEAN_R", "MEDIAN_R"]
    p2_5: Decimal
    p50: Decimal
    p97_5: Decimal


class ExitBootstrapUncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_population: StrategyPopulation
    variant_id: str
    realized_n: int = Field(gt=0)
    session_cluster_count: int = Field(gt=0)
    seed: int
    resamples: Literal[10000]
    intervals: tuple[ExitBootstrapInterval, ExitBootstrapInterval]
    label: Literal["BOOTSTRAP_UNCERTAINTY_INTERVAL"] = (
        "BOOTSTRAP_UNCERTAINTY_INTERVAL"
    )


class ExitModelComparisonReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    populations: tuple[PopulationReconciliation, ...]
    variants: tuple[ExitModelVariant, ...]
    stage13_1_control: FixedRiskSimulationReport
    new_trades: tuple[ExitModelTradePath, ...]
    statistics: tuple[ExitVariantStatistics, ...]
    bootstrap_uncertainty: tuple[ExitBootstrapUncertainty, ...]
    bootstrap_seed: int
    bootstrap_resamples: Literal[10000]
    report_version: Literal["stage13-2-controlled-exit-comparison-v1"] = (
        "stage13-2-controlled-exit-comparison-v1"
    )
    caveat: str = (
        "Descriptive controlled exit comparison; no ranking, selection, optimization, "
        "sizing, costs, or recommendation."
    )

    @model_validator(mode="after")
    def reconcile_report(self) -> Self:
        if len(self.variants) != 36 or len(
            set(item.variant_id for item in self.variants)
        ) != 36:
            raise ValueError("Stage 13.2 requires exactly 36 unique variants")
        if sum(
            item.family is not ExitFamily.FIXED_R_CONTROL for item in self.variants
        ) != 21:
            raise ValueError("Stage 13.2 requires exactly 21 new variants")
        expected = tuple(
            (population, variant.variant_id)
            for population in StrategyPopulation
            for variant in self.variants
        )
        observed = tuple(
            (item.strategy_population, item.variant.variant_id)
            for item in self.statistics
        )
        if observed != expected:
            raise ValueError("exit statistics ordering mismatch")
        if len(self.bootstrap_uncertainty) != len(expected):
            raise ValueError("every population/variant requires bootstrap uncertainty")
        if tuple(item.strategy_population for item in self.populations) != tuple(
            StrategyPopulation
        ):
            raise ValueError("Stage 13.2 requires the two frozen populations")
        eligible_by_population = {
            item.strategy_population: item.eligible_entry_n for item in self.populations
        }
        if any(
            item.membership_n != eligible_by_population[item.strategy_population]
            for item in self.statistics
        ):
            raise ValueError("variant membership must preserve accepted entries")
        new_keys = tuple(
            (
                item.strategy_population,
                item.setup_identity,
                item.variant.variant_id,
            )
            for item in self.new_trades
        )
        if len(new_keys) != len(set(new_keys)):
            raise ValueError("new exit paths require unique population/setup/variant keys")
        expected_new_n = sum(eligible_by_population.values()) * 21
        if len(self.new_trades) != expected_new_n:
            raise ValueError("every accepted entry requires all 21 new exit paths")
        bootstrap_keys = tuple(
            (item.strategy_population, item.variant_id)
            for item in self.bootstrap_uncertainty
        )
        if bootstrap_keys != expected:
            raise ValueError("bootstrap ordering must match exit statistics")
        return self


def exit_model_comparison_hash(report: ExitModelComparisonReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
