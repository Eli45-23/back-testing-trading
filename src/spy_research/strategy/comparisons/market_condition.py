"""Stage 10.9 session-bounded market-condition feature measurements."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.bars import FiveMinuteBar
from spy_research.indicators import (
    FiveMinuteAtrRow,
    FiveMinuteIndicatorRow,
    FiveMinuteVwapRow,
)
from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.research_stats import DistributionSummary, summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyHorizonStatistics,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.models import (
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcomeResult,
)


WINDOWS = (6, 12, 24)
SLOPE_LAGS = (1, 2, 3)
HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")
BASE_FEATURE_NAMES = (
    "ema9_ema20_absolute_separation",
    "ema9_ema20_separation_atr14",
)
SLOPE_FEATURE_NAMES = tuple(
    f"{source}_slope_{lag}_bars"
    for source in ("ema9", "ema20", "vwap")
    for lag in SLOPE_LAGS
)
WINDOW_FEATURE_NAMES = tuple(
    f"{name}_{window}_bars"
    for name in (
        "ema9_ema20_cross_count",
        "ema9_vwap_cross_count",
        "ema20_vwap_cross_count",
        "price_vwap_side_change_count",
        "rolling_high_low_range",
        "rolling_range_atr14",
        "directional_efficiency",
        "range_overlap_fraction",
        "close_direction_alternation_fraction",
    )
    for window in WINDOWS
)
DISTANCE_FEATURE_NAMES = (
    "confirmation_close_vwap_distance_atr14",
    "ema9_vwap_distance_atr14",
    "ema20_vwap_distance_atr14",
)
FEATURE_NAMES = (
    BASE_FEATURE_NAMES
    + SLOPE_FEATURE_NAMES
    + WINDOW_FEATURE_NAMES
    + DISTANCE_FEATURE_NAMES
)


class MarketConditionInputError(ValueError):
    """Frozen inputs cannot form trustworthy confirmation-time features."""


class FeatureQuartile(StrEnum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class MarketConditionFeatureValue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    value: Decimal | None


class MarketConditionAnnotation(BaseModel):
    """One frozen setup's complete ordered measurement vector."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    features: tuple[MarketConditionFeatureValue, ...]
    measurement_version: Literal["market-condition-measurement-v1"] = (
        "market-condition-measurement-v1"
    )

    @model_validator(mode="after")
    def reconcile_annotation(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("signal-known time must follow confirmation by five minutes")
        if tuple(item.name for item in self.features) != FEATURE_NAMES:
            raise ValueError("feature vector must use frozen deterministic ordering")
        if any(
            item.value is not None and not item.value.is_finite()
            for item in self.features
        ):
            raise ValueError("feature values must be finite Decimals or unavailable")
        return self

    def value(self, name: str) -> Decimal | None:
        try:
            index = FEATURE_NAMES.index(name)
        except ValueError as exc:
            raise KeyError(name) from exc
        return self.features[index].value


class MarketConditionFeatureDistribution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_name: str
    distribution: DistributionSummary
    unavailable_n: int = Field(ge=0)
    q1_upper: Decimal | None
    q2_upper: Decimal | None
    q3_upper: Decimal | None
    percentile_method: Literal["linear_rank_n_minus_1_v1"] = (
        "linear_rank_n_minus_1_v1"
    )

    @model_validator(mode="after")
    def reconcile_boundaries(self) -> Self:
        expected = (
            self.distribution.p25,
            self.distribution.median,
            self.distribution.p75,
        )
        if (self.q1_upper, self.q2_upper, self.q3_upper) != expected:
            raise ValueError("quartile boundaries must match descriptive distribution")
        return self


class MarketConditionQuartileStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_name: str
    quartile: FeatureQuartile
    lower_exclusive: Decimal | None
    upper_inclusive: Decimal | None
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("quartile direction counts must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("quartile executable count exceeds annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("quartile horizons must use frozen ordering")
        return self


class MarketConditionFeatureReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_name: str
    distribution: MarketConditionFeatureDistribution
    quartiles: tuple[MarketConditionQuartileStatistics, ...]

    @model_validator(mode="after")
    def reconcile_feature(self) -> Self:
        if self.distribution.feature_name != self.feature_name:
            raise ValueError("distribution feature name mismatch")
        if tuple(item.feature_name for item in self.quartiles) != (self.feature_name,) * 4:
            raise ValueError("quartile feature names must reconcile")
        if tuple(item.quartile for item in self.quartiles) != tuple(FeatureQuartile):
            raise ValueError("quartiles must use Q1-Q4 ordering")
        if sum(item.annotation_n for item in self.quartiles) != self.distribution.distribution.n:
            raise ValueError("quartiles must partition available values")
        return self


class MarketConditionFeatureResult(BaseModel):
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
    annotations: tuple[MarketConditionAnnotation, ...]
    base_all_horizons: tuple[BaseStrategyHorizonStatistics, ...]
    feature_reports: tuple[MarketConditionFeatureReport, ...]
    report_version: Literal["market-condition-feature-report-v1"] = (
        "market-condition-feature-report-v1"
    )
    sample_warning: str = (
        "Quartiles are descriptive sample partitions, not strategy thresholds."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one feature annotation")
        if len({item.setup_identity for item in self.annotations}) != len(
            self.annotations
        ):
            raise ValueError("feature annotation identities must be unique")
        if tuple(item.feature_name for item in self.feature_reports) != FEATURE_NAMES:
            raise ValueError("feature reports must use frozen ordering")
        for report in self.feature_reports:
            if (
                report.distribution.distribution.n
                + report.distribution.unavailable_n
                != self.confirmed_count
            ):
                raise ValueError("feature availability must reconcile")
        if tuple(item.horizon for item in self.base_all_horizons) != HORIZON_ORDER:
            raise ValueError("BASE_ALL horizons must use frozen ordering")
        return self


def _validate_rows(rows, label):
    indexed = {}
    previous = None
    for row in rows:
        key = (row.session_date, row.timestamp)
        if key in indexed:
            raise MarketConditionInputError(f"Duplicate {label} timestamp")
        if previous is not None and row.timestamp <= previous:
            raise MarketConditionInputError(f"{label} rows must be chronological")
        if row.timeframe != "5Min" or row.session_mode != "RTH_ONLY":
            raise MarketConditionInputError(f"{label} rows require RTH 5Min provenance")
        indexed[key] = row
        previous = row.timestamp
    return indexed


def _strict_side(left: Decimal, right: Decimal) -> int:
    return 1 if left > right else (-1 if left < right else 0)


def _cross_count(left: Sequence[Decimal], right: Sequence[Decimal]) -> Decimal:
    count = 0
    for prior_left, current_left, prior_right, current_right in zip(
        left, left[1:], right, right[1:], strict=False
    ):
        if current_left > current_right and prior_left <= prior_right:
            count += 1
        elif current_left < current_right and prior_left >= prior_right:
            count += 1
    return Decimal(count)


def _side_change_count(left: Sequence[Decimal], right: Sequence[Decimal]) -> Decimal:
    sides = tuple(_strict_side(a, b) for a, b in zip(left, right, strict=True))
    return Decimal(
        sum(
            prior != 0 and current != 0 and prior != current
            for prior, current in zip(sides, sides[1:], strict=False)
        )
    )


def _window_features(
    bars: Sequence[FiveMinuteBar],
    ema_rows: Sequence[FiveMinuteIndicatorRow],
    vwap_rows: Sequence[FiveMinuteVwapRow],
    atr14: Decimal | None,
) -> dict[str, Decimal | None]:
    values: dict[str, Decimal | None] = {}
    for window in WINDOWS:
        suffix = f"_{window}_bars"
        if len(bars) < window:
            for base in (
                "ema9_ema20_cross_count",
                "ema9_vwap_cross_count",
                "ema20_vwap_cross_count",
                "price_vwap_side_change_count",
                "rolling_high_low_range",
                "rolling_range_atr14",
                "directional_efficiency",
                "range_overlap_fraction",
                "close_direction_alternation_fraction",
            ):
                values[base + suffix] = None
            continue
        selected_bars = tuple(bars[-window:])
        selected_ema = tuple(ema_rows[-window:])
        selected_vwap = tuple(vwap_rows[-window:])
        ema9 = tuple(item.ema9 for item in selected_ema)
        ema20 = tuple(item.ema20 for item in selected_ema)
        vwap = tuple(item.vwap for item in selected_vwap)
        closes = tuple(item.close for item in selected_bars)
        if all(item is not None for item in ema9 + ema20):
            typed_ema9 = tuple(item for item in ema9 if item is not None)
            typed_ema20 = tuple(item for item in ema20 if item is not None)
            values["ema9_ema20_cross_count" + suffix] = _cross_count(
                typed_ema9, typed_ema20
            )
        else:
            values["ema9_ema20_cross_count" + suffix] = None
        if all(item is not None for item in ema9 + vwap):
            typed_ema9 = tuple(item for item in ema9 if item is not None)
            typed_vwap = tuple(item for item in vwap if item is not None)
            values["ema9_vwap_cross_count" + suffix] = _cross_count(
                typed_ema9, typed_vwap
            )
        else:
            values["ema9_vwap_cross_count" + suffix] = None
        if all(item is not None for item in ema20 + vwap):
            typed_ema20 = tuple(item for item in ema20 if item is not None)
            typed_vwap = tuple(item for item in vwap if item is not None)
            values["ema20_vwap_cross_count" + suffix] = _cross_count(
                typed_ema20, typed_vwap
            )
        else:
            values["ema20_vwap_cross_count" + suffix] = None
        if all(item is not None for item in vwap):
            typed_vwap = tuple(item for item in vwap if item is not None)
            values["price_vwap_side_change_count" + suffix] = _side_change_count(
                closes, typed_vwap
            )
        else:
            values["price_vwap_side_change_count" + suffix] = None
        with localcontext(EMA_CONTEXT):
            rolling_range = max(item.high for item in selected_bars) - min(
                item.low for item in selected_bars
            )
            values["rolling_high_low_range" + suffix] = rolling_range
            values["rolling_range_atr14" + suffix] = (
                rolling_range / atr14 if atr14 is not None and atr14 > 0 else None
            )
            path = sum(
                (
                    abs(current - prior)
                    for prior, current in zip(closes, closes[1:], strict=False)
                ),
                Decimal(0),
            )
            values["directional_efficiency" + suffix] = (
                abs(closes[-1] - closes[0]) / path if path > 0 else None
            )
            overlap_n = sum(
                max(prior.low, current.low) <= min(prior.high, current.high)
                for prior, current in zip(
                    selected_bars, selected_bars[1:], strict=False
                )
            )
            values["range_overlap_fraction" + suffix] = Decimal(overlap_n) / Decimal(
                window - 1
            )
            moves = tuple(
                current - prior
                for prior, current in zip(closes, closes[1:], strict=False)
            )
            alternating_n = sum(
                prior != 0 and current != 0 and prior * current < 0
                for prior, current in zip(moves, moves[1:], strict=False)
            )
            values["close_direction_alternation_fraction" + suffix] = Decimal(
                alternating_n
            ) / Decimal(window - 2)
    return values


def calculate_market_condition_annotations(
    setup_result: BasePriceActionResult,
    bars: Sequence[FiveMinuteBar],
    ema_rows: Sequence[FiveMinuteIndicatorRow],
    vwap_rows: Sequence[FiveMinuteVwapRow],
    atr_rows: Sequence[FiveMinuteAtrRow],
) -> tuple[MarketConditionAnnotation, ...]:
    """Measure only same-session rows at or before each confirmation candle."""

    bar_by_key = _validate_rows(bars, "bar")
    ema_by_key = _validate_rows(ema_rows, "EMA")
    vwap_by_key = _validate_rows(vwap_rows, "VWAP")
    atr_by_key = _validate_rows(atr_rows, "ATR")
    universes = tuple(map(set, (bar_by_key, ema_by_key, vwap_by_key, atr_by_key)))
    if len({frozenset(item) for item in universes}) != 1:
        raise MarketConditionInputError("bar and indicator timestamp universes differ")
    grouped_keys: dict[date, list[tuple[date, datetime]]] = defaultdict(list)
    for key in bar_by_key:
        grouped_keys[key[0]].append(key)
    index_by_key = {
        key: index
        for session_keys in grouped_keys.values()
        for index, key in enumerate(session_keys)
    }
    annotations = []
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    for setup in confirmed:
        if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
            raise MarketConditionInputError("Confirmed setup lacks frozen timing")
        key = (setup.session_date, setup.confirmation_bar_timestamp)
        if key not in bar_by_key:
            raise MarketConditionInputError("Confirmation row is unavailable")
        session_keys = grouped_keys[setup.session_date]
        end_index = index_by_key[key]
        cutoff_keys = session_keys[: end_index + 1]
        cutoff_bars = tuple(bar_by_key[item] for item in cutoff_keys)
        cutoff_ema = tuple(ema_by_key[item] for item in cutoff_keys)
        cutoff_vwap = tuple(vwap_by_key[item] for item in cutoff_keys)
        current_bar = cutoff_bars[-1]
        current_ema = cutoff_ema[-1]
        current_vwap = cutoff_vwap[-1].vwap
        current_atr = atr_by_key[key].atr14
        values: dict[str, Decimal | None] = {}
        with localcontext(EMA_CONTEXT):
            separation = (
                abs(current_ema.ema9 - current_ema.ema20)
                if current_ema.ema9 is not None and current_ema.ema20 is not None
                else None
            )
            values["ema9_ema20_absolute_separation"] = separation
            values["ema9_ema20_separation_atr14"] = (
                separation / current_atr
                if separation is not None and current_atr is not None and current_atr > 0
                else None
            )
            for source in ("ema9", "ema20"):
                current = getattr(current_ema, source)
                for lag in SLOPE_LAGS:
                    prior = (
                        getattr(cutoff_ema[-1 - lag], source)
                        if len(cutoff_ema) > lag
                        else None
                    )
                    values[f"{source}_slope_{lag}_bars"] = (
                        (current - prior) / Decimal(lag)
                        if current is not None and prior is not None
                        else None
                    )
            for lag in SLOPE_LAGS:
                prior = cutoff_vwap[-1 - lag].vwap if len(cutoff_vwap) > lag else None
                values[f"vwap_slope_{lag}_bars"] = (
                    (current_vwap - prior) / Decimal(lag)
                    if current_vwap is not None and prior is not None
                    else None
                )
        values.update(
            _window_features(cutoff_bars, cutoff_ema, cutoff_vwap, current_atr)
        )
        with localcontext(EMA_CONTEXT):
            values["confirmation_close_vwap_distance_atr14"] = (
                abs(current_bar.close - current_vwap) / current_atr
                if current_vwap is not None and current_atr is not None and current_atr > 0
                else None
            )
            values["ema9_vwap_distance_atr14"] = (
                abs(current_ema.ema9 - current_vwap) / current_atr
                if current_ema.ema9 is not None
                and current_vwap is not None
                and current_atr is not None
                and current_atr > 0
                else None
            )
            values["ema20_vwap_distance_atr14"] = (
                abs(current_ema.ema20 - current_vwap) / current_atr
                if current_ema.ema20 is not None
                and current_vwap is not None
                and current_atr is not None
                and current_atr > 0
                else None
            )
        annotations.append(
            MarketConditionAnnotation(
                setup_identity=setup.setup_identity,
                session_date=setup.session_date,
                direction=setup.direction,
                confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
                signal_known_at=setup.signal_known_at,
                features=tuple(
                    MarketConditionFeatureValue(name=name, value=values[name])
                    for name in FEATURE_NAMES
                ),
            )
        )
    return tuple(annotations)


def assign_feature_quartile(
    value: Decimal,
    distribution: DistributionSummary,
) -> FeatureQuartile:
    """Assign deterministic inclusive-boundary sample quartiles."""

    if distribution.p25 is None or distribution.median is None or distribution.p75 is None:
        raise ValueError("quartile assignment requires a non-empty distribution")
    if value <= distribution.p25:
        return FeatureQuartile.Q1
    if value <= distribution.median:
        return FeatureQuartile.Q2
    if value <= distribution.p75:
        return FeatureQuartile.Q3
    return FeatureQuartile.Q4


def calculate_market_condition_report(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[MarketConditionAnnotation],
) -> MarketConditionFeatureResult:
    """Summarize features and unchanged outcomes by descriptive quartiles."""

    if not (
        setup_result.start_date == outcome_result.start_date == base_statistics.start_date
        and setup_result.end_date == outcome_result.end_date == base_statistics.end_date
    ):
        raise MarketConditionInputError("Frozen source ranges do not match")
    expected_population = (
        base_statistics.break_seed_count,
        base_statistics.confirmed_count,
        base_statistics.non_confirmed_count,
        base_statistics.executable_count,
        base_statistics.session_end_unavailable_count,
        base_statistics.missing_entry_count,
    )
    source_population = (
        setup_result.seed_count,
        setup_result.confirmed_count,
        setup_result.non_confirmed_count,
        outcome_result.available_entry_count,
        outcome_result.session_end_unavailable_count,
        outcome_result.missing_entry_count,
    )
    if expected_population != source_population:
        raise MarketConditionInputError("Stage 9 population mismatch")
    annotation_by_id = {item.setup_identity: item for item in annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    if len(annotation_by_id) != len(annotations) or frozenset(
        annotation_by_id
    ) != frozenset(outcome_by_id):
        raise MarketConditionInputError("Feature/outcome identities do not reconcile")
    available_outcomes = tuple(
        item
        for item in outcome_result.outcomes
        if item.entry_reference.entry_status is EntryStatus.AVAILABLE
    )
    baseline = next(
        item
        for item in base_statistics.groups
        if item.dimension is BaseStrategyGroupDimension.OVERALL
    )
    if summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL, "OVERALL", available_outcomes
    ) != baseline:
        raise MarketConditionInputError("BASE_ALL does not reproduce Stage 9.3")
    reports = []
    for name in FEATURE_NAMES:
        pairs = tuple(
            (item, item.value(name))
            for item in annotations
            if item.value(name) is not None
        )
        values = tuple(value for _, value in pairs if value is not None)
        distribution = summarize_distribution(values)
        distribution_row = MarketConditionFeatureDistribution(
            feature_name=name,
            distribution=distribution,
            unavailable_n=len(annotations) - len(values),
            q1_upper=distribution.p25,
            q2_upper=distribution.median,
            q3_upper=distribution.p75,
        )
        quartile_rows = []
        boundaries = (
            (None, distribution.p25),
            (distribution.p25, distribution.median),
            (distribution.median, distribution.p75),
            (distribution.p75, None),
        )
        for quartile, (lower, upper) in zip(
            FeatureQuartile, boundaries, strict=True
        ):
            selected_annotations = tuple(
                item
                for item, value in pairs
                if value is not None
                and assign_feature_quartile(value, distribution) is quartile
            )
            identities = {item.setup_identity for item in selected_annotations}
            selected_outcomes = tuple(
                item
                for item in available_outcomes
                if item.setup_identity in identities
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.OVERALL,
                f"{name}_{quartile.value}",
                selected_outcomes,
            )
            quartile_rows.append(
                MarketConditionQuartileStatistics(
                    feature_name=name,
                    quartile=quartile,
                    lower_exclusive=lower,
                    upper_inclusive=upper,
                    annotation_n=len(selected_annotations),
                    executable_n=len(selected_outcomes),
                    long_annotation_n=sum(
                        item.direction is SetupDirection.LONG
                        for item in selected_annotations
                    ),
                    short_annotation_n=sum(
                        item.direction is SetupDirection.SHORT
                        for item in selected_annotations
                    ),
                    session_count=len(
                        {item.session_date for item in selected_annotations}
                    ),
                    horizons=stats.horizons,
                )
            )
        reports.append(
            MarketConditionFeatureReport(
                feature_name=name,
                distribution=distribution_row,
                quartiles=tuple(quartile_rows),
            )
        )
    return MarketConditionFeatureResult(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        development_session_count=base_statistics.development_session_count,
        annotations=tuple(annotations),
        base_all_horizons=baseline.horizons,
        feature_reports=tuple(reports),
    )
