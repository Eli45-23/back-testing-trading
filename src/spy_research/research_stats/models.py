"""Immutable typed results for descriptive cross-theory statistics."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


HorizonName = Literal["5m", "15m", "30m", "60m", "EOD"]
GroupName = Literal[
    "ALL",
    "BULLISH",
    "BEARISH",
    "VWAP_ALIGNED",
    "VWAP_NOT_ALIGNED",
    "EXPANDING",
    "NOT_EXPANDING",
    "VWAP_ALIGNED_AND_EXPANDING",
    "OTHER",
]


class DistributionSummary(BaseModel):
    """Exact Decimal distribution using documented linear percentiles."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    n: int = Field(ge=0)
    mean: Decimal | None
    median: Decimal | None
    minimum: Decimal | None
    maximum: Decimal | None
    p25: Decimal | None
    p75: Decimal | None


class ThresholdSummary(BaseModel):
    """Factual threshold count and percentage with explicit denominator."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: Decimal
    reached_n: int = Field(ge=0)
    eligible_n: int = Field(ge=0)
    percentage: Decimal | None


class FavorableAdverseCounts(BaseModel):
    """Counts comparing raw MFE and MAE magnitudes without interpretation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mfe_greater: int = Field(ge=0)
    equal: int = Field(ge=0)
    mfe_less: int = Field(ge=0)


class HorizonStatistics(BaseModel):
    """One eligible horizon's distributions and frozen threshold summaries."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: HorizonName
    eligible_n: int = Field(ge=0)
    excluded_incomplete_n: int = Field(ge=0)
    mfe: DistributionSummary
    mae: DistributionSummary
    dollar_thresholds: tuple[ThresholdSummary, ...]
    atr_thresholds: tuple[ThresholdSummary, ...]
    atr_eligible_n: int = Field(ge=0)
    atr_excluded_n: int = Field(ge=0)
    favorable_adverse: FavorableAdverseCounts


class GroupStatistics(BaseModel):
    """Descriptive horizon results for one frozen event-time grouping."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: GroupName
    total_n: int = Field(ge=0)
    horizons: tuple[HorizonStatistics, ...]


class OppositeCrossTimingSummary(BaseModel):
    """Availability and elapsed-minute distribution for Stage 5.2 context."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    with_opposite_n: int = Field(ge=0)
    without_opposite_n: int = Field(ge=0)
    minutes: DistributionSummary


class Phase1CrossStatistics(BaseModel):
    """Complete deterministic descriptive report for the requested sample."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    start_date: date
    end_date: date
    total_n: int = Field(ge=0)
    bullish_n: int = Field(ge=0)
    bearish_n: int = Field(ge=0)
    groups: tuple[GroupStatistics, ...]
    absolute_separation: DistributionSummary
    opposite_cross_timing: OppositeCrossTimingSummary
    percentile_method: Literal["linear_rank_n_minus_1_v1"] = (
        "linear_rank_n_minus_1_v1"
    )
    small_sample_warning: str = (
        "This development sample is too small to establish a robust edge."
    )
