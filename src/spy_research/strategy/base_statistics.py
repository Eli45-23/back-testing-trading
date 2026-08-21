"""Pure descriptive statistics over frozen Stage 9.1 and 9.2 records."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, time
from decimal import Decimal, localcontext
from enum import StrEnum
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import (
    DistributionSummary,
    FavorableAdverseCounts,
    summarize_distribution,
)
from spy_research.strategy.models import (
    BasePriceActionResult,
    BaseSetupStatus,
    ConfirmationType,
    EntryStatus,
    SetupDirection,
    SetupHorizonOutcome,
    SetupOutcome,
    SetupOutcomeResult,
)


NEW_YORK = ZoneInfo("America/New_York")
HORIZON_FIELDS = (
    ("5m", "five"),
    ("15m", "fifteen"),
    ("30m", "thirty"),
    ("60m", "sixty"),
    ("EOD", "eod"),
)
TIME_BUCKETS = (
    ("09:30-09:59", time(9, 30), time(10, 0)),
    ("10:00-10:59", time(10, 0), time(11, 0)),
    ("11:00-11:59", time(11, 0), time(12, 0)),
    ("12:00-12:59", time(12, 0), time(13, 0)),
    ("13:00-13:59", time(13, 0), time(14, 0)),
    ("14:00-14:59", time(14, 0), time(15, 0)),
    ("15:00-16:00", time(15, 0), time(16, 0)),
)


class BaseStatisticsInputError(ValueError):
    """Frozen setup and outcome inputs cannot form a trustworthy baseline."""


class BaseStrategyGroupDimension(StrEnum):
    OVERALL = "OVERALL"
    DIRECTION = "DIRECTION"
    LEVEL = "LEVEL"
    CONFIRMATION = "CONFIRMATION"
    ENTRY_TIME_BUCKET = "ENTRY_TIME_BUCKET"


class BaseStrategyHorizonStatistics(BaseModel):
    """Exact descriptive statistics for one group's horizon."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    complete_n: int = Field(ge=0)
    incomplete_n: int = Field(ge=0)
    mfe: DistributionSummary
    mae: DistributionSummary
    net_excursion_balance: DistributionSummary
    favorable_adverse: FavorableAdverseCounts
    valid_ratio_n: int = Field(ge=0)
    zero_mae_n: int = Field(ge=0)
    median_mfe_mae_ratio: Decimal | None

    @model_validator(mode="after")
    def reconcile_counts(self):
        if self.mfe.n != self.complete_n or self.mae.n != self.complete_n:
            raise ValueError("MFE/MAE distributions must match complete count")
        if self.net_excursion_balance.n != self.complete_n:
            raise ValueError("balance distribution must match complete count")
        comparison_n = (
            self.favorable_adverse.mfe_greater
            + self.favorable_adverse.equal
            + self.favorable_adverse.mfe_less
        )
        if comparison_n != self.complete_n:
            raise ValueError("paired comparison counts must match complete count")
        if self.valid_ratio_n + self.zero_mae_n != self.complete_n:
            raise ValueError("ratio counts must match complete count")
        if (self.valid_ratio_n == 0) != (self.median_mfe_mae_ratio is None):
            raise ValueError("ratio median availability mismatch")
        return self


class BaseStrategyGroupStatistics(BaseModel):
    """One deterministically ordered baseline group."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: BaseStrategyGroupDimension
    name: str
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def validate_horizons(self):
        if tuple(item.horizon for item in self.horizons) != tuple(
            item[0] for item in HORIZON_FIELDS
        ):
            raise ValueError("baseline horizons must use frozen ordering")
        for item in self.horizons:
            if item.complete_n + item.incomplete_n != self.executable_n:
                raise ValueError("horizon population must match executable group")
        return self


class BaseStrategyStatistics(BaseModel):
    """Frozen Stage 9 control-group report for later filtered comparisons."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    break_seed_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    non_confirmed_count: int = Field(ge=0)
    executable_count: int = Field(ge=0)
    session_end_unavailable_count: int = Field(ge=0)
    missing_entry_count: int = Field(ge=0)
    immediate_hold_confirmed_count: int = Field(ge=0)
    retest_hold_confirmed_count: int = Field(ge=0)
    development_session_count: int = Field(ge=0)
    groups: tuple[BaseStrategyGroupStatistics, ...]
    statistics_version: Literal["base-strategy-descriptive-v1"] = (
        "base-strategy-descriptive-v1"
    )
    precision_policy: Literal["decimal-ema-context-v1"] = "decimal-ema-context-v1"
    sample_warning: str = (
        "Descriptive baseline research; not evidence of stable expectancy."
    )

    @model_validator(mode="after")
    def reconcile_confirmation_counts(self):
        if (
            self.immediate_hold_confirmed_count
            + self.retest_hold_confirmed_count
            != self.confirmed_count
        ):
            raise ValueError("confirmation populations must match confirmed count")
        return self


def entry_time_bucket(item: SetupOutcome) -> str:
    """Return the frozen ET bucket for an available entry reference."""

    timestamp = item.entry_reference.entry_reference_timestamp
    if timestamp is None:
        raise BaseStatisticsInputError("Time buckets require an available entry")
    local_time = timestamp.astimezone(NEW_YORK).time().replace(tzinfo=None)
    for label, start, end in TIME_BUCKETS:
        if start <= local_time < end:
            return label
    raise BaseStatisticsInputError("Executable entry is outside frozen RTH buckets")


def _summarize_horizon(
    items: Sequence[SetupOutcome],
    *,
    name: str,
    field: str,
) -> BaseStrategyHorizonStatistics:
    horizons = tuple(getattr(item, field) for item in items)
    if any(value is None for value in horizons):
        raise BaseStatisticsInputError("Available entry is missing a required horizon")
    typed = tuple(value for value in horizons if value is not None)
    complete = tuple(value for value in typed if value.complete)
    mfe = tuple(value.mfe for value in complete)
    mae = tuple(value.mae for value in complete)
    ratios = []
    with localcontext(EMA_CONTEXT):
        balances = tuple(
            left - right for left, right in zip(mfe, mae, strict=True)
        )
        for left, right in zip(mfe, mae, strict=True):
            if right > 0:
                ratios.append(left / right)
    ratio_summary = summarize_distribution(tuple(ratios))
    return BaseStrategyHorizonStatistics(
        horizon=name,
        complete_n=len(complete),
        incomplete_n=len(typed) - len(complete),
        mfe=summarize_distribution(mfe),
        mae=summarize_distribution(mae),
        net_excursion_balance=summarize_distribution(balances),
        favorable_adverse=FavorableAdverseCounts(
            mfe_greater=sum(left > right for left, right in zip(mfe, mae, strict=True)),
            equal=sum(left == right for left, right in zip(mfe, mae, strict=True)),
            mfe_less=sum(left < right for left, right in zip(mfe, mae, strict=True)),
        ),
        valid_ratio_n=len(ratios),
        zero_mae_n=sum(value == 0 for value in mae),
        median_mfe_mae_ratio=ratio_summary.median,
    )


def summarize_base_outcome_group(
    dimension: BaseStrategyGroupDimension,
    name: str,
    items: Sequence[SetupOutcome],
) -> BaseStrategyGroupStatistics:
    return BaseStrategyGroupStatistics(
        dimension=dimension,
        name=name,
        executable_n=len(items),
        horizons=tuple(
            _summarize_horizon(items, name=horizon, field=field)
            for horizon, field in HORIZON_FIELDS
        ),
    )


def _validate_inputs(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
) -> tuple[SetupOutcome, ...]:
    if (
        setup_result.start_date != outcome_result.start_date
        or setup_result.end_date != outcome_result.end_date
    ):
        raise BaseStatisticsInputError("Setup and outcome ranges do not match")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_identity = {item.setup_identity: item for item in confirmed}
    if len(setup_by_identity) != len(confirmed):
        raise BaseStatisticsInputError("Duplicate confirmed setup identity")
    outcome_by_identity = {
        item.setup_identity: item for item in outcome_result.outcomes
    }
    if len(outcome_by_identity) != len(outcome_result.outcomes):
        raise BaseStatisticsInputError("Duplicate setup outcome identity")
    if len(confirmed) != outcome_result.confirmed_setup_count:
        raise BaseStatisticsInputError("Confirmed setup populations do not reconcile")
    if set(setup_by_identity) != set(outcome_by_identity):
        raise BaseStatisticsInputError("Setup and outcome identities do not match")
    for identity, item in outcome_by_identity.items():
        if item.setup != setup_by_identity[identity]:
            raise BaseStatisticsInputError(
                "Embedded outcome setup does not match Stage 9.1"
            )
    available = tuple(
        item
        for item in outcome_result.outcomes
        if item.entry_reference.entry_status is EntryStatus.AVAILABLE
    )
    for item in available:
        if any(getattr(item, field) is None for _, field in HORIZON_FIELDS):
            raise BaseStatisticsInputError(
                "Available entry is missing a required horizon"
            )
    return available


def calculate_base_strategy_statistics(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    *,
    development_session_count: int,
) -> BaseStrategyStatistics:
    """Aggregate immutable Stage 9 records without reclassification or mutation."""

    available = _validate_inputs(setup_result, outcome_result)
    group_specs: list[
        tuple[
            BaseStrategyGroupDimension,
            str,
            Callable[[SetupOutcome], bool],
        ]
    ] = [
        (BaseStrategyGroupDimension.OVERALL, "OVERALL", lambda item: True),
    ]
    group_specs.extend(
        (
            BaseStrategyGroupDimension.DIRECTION,
            direction.value,
            lambda item, direction=direction: item.setup.direction is direction,
        )
        for direction in SetupDirection
    )
    group_specs.extend(
        (
            BaseStrategyGroupDimension.LEVEL,
            level.value,
            lambda item, level=level: item.setup.level_type is level,
        )
        for level in LevelType
    )
    group_specs.extend(
        (
            BaseStrategyGroupDimension.CONFIRMATION,
            confirmation.value,
            lambda item, confirmation=confirmation: (
                item.setup.confirmation_type is confirmation
            ),
        )
        for confirmation in ConfirmationType
    )
    group_specs.extend(
        (
            BaseStrategyGroupDimension.ENTRY_TIME_BUCKET,
            label,
            lambda item, label=label: entry_time_bucket(item) == label,
        )
        for label, _, _ in TIME_BUCKETS
    )
    groups = tuple(
        summarize_base_outcome_group(
            dimension,
            name,
            tuple(item for item in available if predicate(item)),
        )
        for dimension, name, predicate in group_specs
    )
    return BaseStrategyStatistics(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        immediate_hold_confirmed_count=sum(
            item.confirmation_type is ConfirmationType.IMMEDIATE_HOLD
            for item in setup_result.candidates
            if item.status is BaseSetupStatus.CONFIRMED
        ),
        retest_hold_confirmed_count=sum(
            item.confirmation_type is ConfirmationType.RETEST_HOLD
            for item in setup_result.candidates
            if item.status is BaseSetupStatus.CONFIRMED
        ),
        development_session_count=development_session_count,
        groups=groups,
    )
