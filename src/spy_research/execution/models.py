"""Immutable models for deterministic Stage 13.1 SPY-share simulations."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.interactions import LevelType
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.research_stats import DistributionSummary
from spy_research.strategy.models import SetupDirection


class ExecutionInputError(ValueError):
    """Frozen execution inputs cannot form a trustworthy trade path."""


class StrategyPopulation(StrEnum):
    BASE_ALL = "BASE_ALL"
    BASE_SHORT = "BASE_SHORT"


class AtrStopModel(StrEnum):
    ATR_0_50 = "ATR_0_50"
    ATR_0_75 = "ATR_0_75"
    ATR_1_00 = "ATR_1_00"

    @property
    def multiplier(self) -> Decimal:
        return {
            AtrStopModel.ATR_0_50: Decimal("0.50"),
            AtrStopModel.ATR_0_75: Decimal("0.75"),
            AtrStopModel.ATR_1_00: Decimal("1.00"),
        }[self]


class RiskTargetModel(StrEnum):
    R_1 = "1R"
    R_1_5 = "1.5R"
    R_2 = "2R"
    R_2_5 = "2.5R"
    R_3 = "3R"

    @property
    def multiple(self) -> Decimal:
        return {
            RiskTargetModel.R_1: Decimal("1"),
            RiskTargetModel.R_1_5: Decimal("1.5"),
            RiskTargetModel.R_2: Decimal("2"),
            RiskTargetModel.R_2_5: Decimal("2.5"),
            RiskTargetModel.R_3: Decimal("3"),
        }[self]


class TradeSimulationStatus(StrEnum):
    SIMULATED = "SIMULATED"
    TRADE_UNAVAILABLE_ATR = "TRADE_UNAVAILABLE_ATR"
    AMBIGUOUS_BOTH_TOUCHED = "AMBIGUOUS_BOTH_TOUCHED"


class TradeExitReason(StrEnum):
    STOP = "STOP"
    TARGET = "TARGET"
    EOD_CLOSE = "EOD_CLOSE"


class FixedRiskVariant(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    stop_model: AtrStopModel
    stop_multiplier: Decimal = Field(gt=0)
    target_model: RiskTargetModel
    target_r: Decimal = Field(gt=0)

    @model_validator(mode="after")
    def frozen_values(self) -> Self:
        if self.stop_multiplier != self.stop_model.multiplier:
            raise ValueError("stop multiplier must match its frozen ATR model")
        if self.target_r != self.target_model.multiple:
            raise ValueError("target multiple must match its frozen R model")
        return self


class ExecutableTradeSetup(BaseModel):
    """Outcome-blind Stage 9 setup and its accepted executable entry reference."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    session_date: date
    direction: SetupDirection
    level_type: LevelType
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    entry_timestamp: datetime
    entry_price: Decimal = Field(gt=0)

    @model_validator(mode="after")
    def validate_timing(self) -> Self:
        timestamps = (
            self.confirmation_bar_timestamp,
            self.signal_known_at,
            self.entry_timestamp,
        )
        if any(item.utcoffset() is None for item in timestamps):
            raise ValueError("execution timestamps must be timezone-aware")
        if self.entry_timestamp < self.signal_known_at:
            raise ValueError("entry cannot precede signal-known time")
        return self


class AmbiguityMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    stop_touched: Literal[True] = True
    target_touched: Literal[True] = True
    both_touch: Literal[True] = True


class RealizedTradePath(BaseModel):
    """One fixed stop/target path for one accepted executable setup."""

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
    stop_model: AtrStopModel
    stop_multiplier: Decimal
    stop_price: Decimal | None
    initial_risk: Decimal | None
    target_model: RiskTargetModel
    target_r: Decimal
    target_price: Decimal | None
    exit_status: TradeSimulationStatus
    exit_timestamp: datetime | None
    exit_price: Decimal | None
    exit_reason: TradeExitReason | None
    price_pnl: Decimal | None
    r_multiple: Decimal | None
    minutes_in_trade: int | None = Field(default=None, ge=0)
    bars_observed: int = Field(ge=0)
    minutes_observed: int = Field(ge=0)
    ambiguity: AmbiguityMetadata | None = None
    execution_version: Literal["fixed-risk-rth-1m-first-hit-v1"] = (
        "fixed-risk-rth-1m-first-hit-v1"
    )

    @model_validator(mode="after")
    def reconcile_status(self) -> Self:
        if self.bars_observed != self.minutes_observed:
            raise ValueError("one-minute bars and observed minutes must reconcile")
        risk_fields = (self.stop_price, self.initial_risk, self.target_price)
        exit_fields = (
            self.exit_timestamp,
            self.exit_price,
            self.exit_reason,
            self.price_pnl,
            self.r_multiple,
            self.minutes_in_trade,
        )
        if self.exit_status is TradeSimulationStatus.TRADE_UNAVAILABLE_ATR:
            if self.confirmation_atr is not None and self.confirmation_atr > 0:
                raise ValueError("ATR-unavailable trade cannot contain positive ATR")
            if any(item is not None for item in risk_fields + exit_fields):
                raise ValueError("ATR-unavailable trade cannot contain risk or exit values")
            if self.ambiguity is not None or self.bars_observed:
                raise ValueError("ATR-unavailable trade cannot observe a trade path")
            return self
        if self.confirmation_atr is None or self.confirmation_atr <= 0:
            raise ValueError("simulated trade requires positive confirmation ATR")
        if any(item is None for item in risk_fields):
            raise ValueError("simulated trade requires stop, risk, and target")
        assert self.initial_risk is not None
        assert self.stop_price is not None
        assert self.target_price is not None
        if self.initial_risk <= 0:
            raise ValueError("initial risk must be positive")
        with localcontext(ATR_CONTEXT):
            expected_risk = self.confirmation_atr * self.stop_multiplier
            expected_stop = (
                self.entry_price - expected_risk
                if self.direction is SetupDirection.LONG
                else self.entry_price + expected_risk
            )
            expected_target = (
                self.entry_price + self.target_r * expected_risk
                if self.direction is SetupDirection.LONG
                else self.entry_price - self.target_r * expected_risk
            )
        if (
            self.initial_risk != expected_risk
            or self.stop_price != expected_stop
            or self.target_price != expected_target
        ):
            raise ValueError("risk, stop, and target must match frozen formulas")
        if self.exit_status is TradeSimulationStatus.AMBIGUOUS_BOTH_TOUCHED:
            if self.exit_timestamp is None or self.minutes_in_trade is None:
                raise ValueError("ambiguous trade requires event timing")
            if any(
                item is not None
                for item in (
                    self.exit_price,
                    self.exit_reason,
                    self.price_pnl,
                    self.r_multiple,
                )
            ):
                raise ValueError("ambiguous trade cannot invent a realized exit")
            if self.ambiguity is None:
                raise ValueError("ambiguous trade requires bar metadata")
            if self.ambiguity.timestamp != self.exit_timestamp:
                raise ValueError("ambiguity timestamp must match exit event")
            return self
        if self.exit_status is not TradeSimulationStatus.SIMULATED:
            raise ValueError("unknown trade simulation status")
        if any(item is None for item in exit_fields):
            raise ValueError("realized trade requires complete exit fields")
        if self.ambiguity is not None:
            raise ValueError("realized trade cannot carry ambiguity metadata")
        assert self.exit_price is not None
        assert self.price_pnl is not None
        assert self.r_multiple is not None
        with localcontext(ATR_CONTEXT):
            expected_pnl = (
                self.exit_price - self.entry_price
                if self.direction is SetupDirection.LONG
                else self.entry_price - self.exit_price
            )
        if self.price_pnl != expected_pnl:
            raise ValueError("price P/L must match direction and exact exit")
        if self.exit_reason is TradeExitReason.STOP and self.r_multiple != Decimal("-1"):
            raise ValueError("exact stop exit must equal -1R")
        if self.exit_reason is TradeExitReason.TARGET and self.r_multiple != self.target_r:
            raise ValueError("exact target exit must equal requested target R")
        return self


class PopulationReconciliation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_population: StrategyPopulation
    confirmed_membership_n: int = Field(ge=0)
    eligible_entry_n: int = Field(ge=0)


class MonthlyTradeStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    month: str
    trade_n: int = Field(ge=0)
    median_r: Decimal | None


class DirectionTradeStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    trade_n: int = Field(ge=0)
    r_multiple: DistributionSummary
    price_pnl: DistributionSummary


class FixedRiskTradeStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_population: StrategyPopulation
    variant: FixedRiskVariant
    eligible_setup_n: int = Field(ge=0)
    unavailable_atr_n: int = Field(ge=0)
    executable_simulated_n: int = Field(ge=0)
    realized_trade_n: int = Field(ge=0)
    target_exit_n: int = Field(ge=0)
    stop_exit_n: int = Field(ge=0)
    eod_exit_n: int = Field(ge=0)
    ambiguous_both_touched_n: int = Field(ge=0)
    r_multiple: DistributionSummary
    price_pnl: DistributionSummary
    positive_r_n: int = Field(ge=0)
    zero_r_n: int = Field(ge=0)
    negative_r_n: int = Field(ge=0)
    win_rate_percentage: Decimal | None
    loss_rate_percentage: Decimal | None
    holding_minutes: DistributionSummary
    monthly: tuple[MonthlyTradeStatistics, ...]
    direction_decomposition: tuple[DirectionTradeStatistics, ...]
    level_composition: tuple[tuple[LevelType, int], ...]

    @model_validator(mode="after")
    def reconcile_counts(self) -> Self:
        if self.unavailable_atr_n + self.executable_simulated_n != self.eligible_setup_n:
            raise ValueError("ATR availability must reconcile to eligible setups")
        if (
            self.realized_trade_n + self.ambiguous_both_touched_n
            != self.executable_simulated_n
        ):
            raise ValueError("realized and ambiguous trades must reconcile")
        if self.target_exit_n + self.stop_exit_n + self.eod_exit_n != self.realized_trade_n:
            raise ValueError("realized exit reasons must reconcile")
        if self.positive_r_n + self.zero_r_n + self.negative_r_n != self.realized_trade_n:
            raise ValueError("realized R signs must reconcile")
        summaries = (self.r_multiple, self.price_pnl, self.holding_minutes)
        if any(item.n != self.realized_trade_n for item in summaries):
            raise ValueError("primary statistics must exclude unavailable and ambiguous trades")
        return self


class FixedRiskSimulationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    populations: tuple[PopulationReconciliation, ...]
    variants: tuple[FixedRiskVariant, ...]
    trades: tuple[RealizedTradePath, ...]
    statistics: tuple[FixedRiskTradeStatistics, ...]
    report_version: Literal["stage13-1-fixed-risk-share-simulation-v1"] = (
        "stage13-1-fixed-risk-share-simulation-v1"
    )
    caveat: str = (
        "Descriptive SPY-share simulation over frozen variants; no ranking, "
        "optimization, sizing, costs, or recommendation."
    )

    @model_validator(mode="after")
    def reconcile_structure(self) -> Self:
        if tuple(item.strategy_population for item in self.populations) != tuple(
            StrategyPopulation
        ):
            raise ValueError("Stage 13.1 requires exactly BASE_ALL and BASE_SHORT")
        expected_variants = tuple(
            (stop, target) for stop in AtrStopModel for target in RiskTargetModel
        )
        if tuple(
            (item.stop_model, item.target_model) for item in self.variants
        ) != expected_variants:
            raise ValueError("Stage 13.1 requires exactly fifteen trade variants")
        if any(
            item.strategy_population is StrategyPopulation.BASE_SHORT
            and item.direction is not SetupDirection.SHORT
            for item in self.trades
        ):
            raise ValueError("BASE_SHORT can contain only frozen SHORT membership")
        expected = tuple(
            (population, variant.stop_model, variant.target_model)
            for population in StrategyPopulation
            for variant in self.variants
        )
        observed = tuple(
            (
                item.strategy_population,
                item.variant.stop_model,
                item.variant.target_model,
            )
            for item in self.statistics
        )
        if observed != expected:
            raise ValueError("statistics must use frozen population/variant ordering")
        return self


def fixed_risk_simulation_hash(report: FixedRiskSimulationReport) -> str:
    return sha256(report.model_dump_json().encode()).hexdigest()
