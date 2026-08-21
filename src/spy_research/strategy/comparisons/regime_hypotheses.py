"""Stage 11.1 predeclared labels over frozen Stage 10.9 measurements."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence
from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.interactions import LevelType
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyHorizonStatistics,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.combined_context import (
    CombinedContextAnnotation,
    CombinedContextMatrixResult,
)
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    Ema20VwapAlignmentState,
)
from spy_research.strategy.comparisons.ema20_vwap_cross_models import (
    Ema20VwapCrossContextState,
)
from spy_research.strategy.comparisons.market_condition import (
    FeatureQuartile,
    MarketConditionAnnotation,
    MarketConditionFeatureResult,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentState,
    Ema9VwapCrossContextState,
    EmaAlignmentState,
    VwapAlignmentState,
)
from spy_research.strategy.models import (
    BasePriceActionResult,
    EntryStatus,
    SetupDirection,
    SetupOutcome,
    SetupOutcomeResult,
)


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")
EFFICIENCY_FEATURE = "directional_efficiency_24_bars"
SEPARATION_FEATURE = "ema9_ema20_separation_atr14"
ALTERNATION_FEATURE = "close_direction_alternation_fraction_24_bars"
VWAP_DISTANCE_FEATURE = "confirmation_close_vwap_distance_atr14"
CROSS_FEATURES = (
    ("EMA9_20", "ema9_ema20_cross_count_24_bars"),
    ("EMA9_VWAP", "ema9_vwap_cross_count_24_bars"),
    ("EMA20_VWAP", "ema20_vwap_cross_count_24_bars"),
    ("PRICE_VWAP", "price_vwap_side_change_count_24_bars"),
)
BOUNDARY_FEATURES = (
    EFFICIENCY_FEATURE,
    SEPARATION_FEATURE,
    ALTERNATION_FEATURE,
    VWAP_DISTANCE_FEATURE,
) + tuple(feature for _, feature in CROSS_FEATURES)
CONTEXT_SPECS = (
    ("EMA9_20_ALIGNMENT", "ema9_20_alignment", EmaAlignmentState),
    ("PRICE_VWAP_ALIGNMENT", "price_vwap_alignment", VwapAlignmentState),
    ("EMA9_VWAP_ALIGNMENT", "ema9_vwap_alignment", Ema9VwapAlignmentState),
    ("EMA20_VWAP_ALIGNMENT", "ema20_vwap_alignment", Ema20VwapAlignmentState),
    (
        "EMA9_VWAP_CROSS_CONTEXT",
        "ema9_vwap_cross_context",
        Ema9VwapCrossContextState,
    ),
    (
        "EMA20_VWAP_CROSS_CONTEXT",
        "ema20_vwap_cross_context",
        Ema20VwapCrossContextState,
    ),
)


class RegimeHypothesisInputError(ValueError):
    """Frozen Stage 9/10 sources cannot form a trustworthy comparison."""


class EfficiencyState(StrEnum):
    HIGH = "HIGH_EFFICIENCY"
    MID = "MID_EFFICIENCY"
    LOW = "LOW_EFFICIENCY"
    UNAVAILABLE = "UNAVAILABLE"


class SeparationState(StrEnum):
    WIDE = "WIDE_SEPARATION"
    MID = "MID_SEPARATION"
    TIGHT = "TIGHT_SEPARATION"
    UNAVAILABLE = "UNAVAILABLE"


class AlternationState(StrEnum):
    HIGH = "HIGH_ALTERNATION"
    MID = "MID_ALTERNATION"
    LOW = "LOW_ALTERNATION"
    UNAVAILABLE = "UNAVAILABLE"


class VwapDistanceState(StrEnum):
    FAR = "FAR_FROM_VWAP"
    MID = "MID_DISTANCE"
    NEAR = "NEAR_VWAP"
    UNAVAILABLE = "UNAVAILABLE"


class CrossQuartileState(StrEnum):
    TOP = "TOP_QUARTILE"
    MIDDLE = "MIDDLE_QUARTILES"
    BOTTOM = "BOTTOM_QUARTILE"
    UNAVAILABLE = "UNAVAILABLE"


class CombinedRegimeState(StrEnum):
    TREND_LIKE_A = "TREND_LIKE_A"
    CHOP_LIKE_A = "CHOP_LIKE_A"
    OTHER = "OTHER"
    UNAVAILABLE = "UNAVAILABLE"


class FrozenQuartileBoundary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_name: str
    q1_upper: Decimal | None
    q2_upper: Decimal | None
    q3_upper: Decimal | None
    percentile_method: Literal["linear_rank_n_minus_1_v1"] = (
        "linear_rank_n_minus_1_v1"
    )

    @model_validator(mode="after")
    def ordered_when_available(self) -> Self:
        values = (self.q1_upper, self.q2_upper, self.q3_upper)
        if any(item is None for item in values):
            if any(item is not None for item in values):
                raise ValueError("quartile boundaries must be wholly available or absent")
        elif not self.q1_upper <= self.q2_upper <= self.q3_upper:
            raise ValueError("quartile boundaries must be ordered")
        return self


class CrossActivityAnnotation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Literal["EMA9_20", "EMA9_VWAP", "EMA20_VWAP", "PRICE_VWAP"]
    feature_name: str
    frozen_value: Decimal | None
    exact_count: int | None = Field(default=None, ge=0)
    quartile: FeatureQuartile | None
    quartile_state: CrossQuartileState

    @model_validator(mode="after")
    def reconcile_value(self) -> Self:
        unavailable = self.frozen_value is None
        if unavailable != (self.exact_count is None):
            raise ValueError("cross count availability mismatch")
        if unavailable != (self.quartile is None):
            raise ValueError("cross quartile availability mismatch")
        if unavailable != (self.quartile_state is CrossQuartileState.UNAVAILABLE):
            raise ValueError("cross state availability mismatch")
        if self.frozen_value is not None:
            if self.frozen_value != self.frozen_value.to_integral_value():
                raise ValueError("cross feature must be an exact integer count")
            if self.exact_count != int(self.frozen_value):
                raise ValueError("exact count must reuse frozen feature value")
        return self


class RegimeHypothesisAnnotation(BaseModel):
    """One outcome-blind label projection of a frozen Stage 10.9 annotation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    directional_efficiency_24: Decimal | None
    ema_separation_atr14: Decimal | None
    close_alternation_24: Decimal | None
    confirmation_close_vwap_distance_atr14: Decimal | None
    efficiency_state: EfficiencyState
    separation_state: SeparationState
    alternation_state: AlternationState
    vwap_distance_state: VwapDistanceState
    cross_activity: tuple[CrossActivityAnnotation, ...]
    combined_state: CombinedRegimeState
    hypothesis_version: Literal["predeclared-regime-hypotheses-v1"] = (
        "predeclared-regime-hypotheses-v1"
    )

    @model_validator(mode="after")
    def reconcile_cross_order(self) -> Self:
        if tuple(item.name for item in self.cross_activity) != tuple(
            name for name, _ in CROSS_FEATURES
        ):
            raise ValueError("cross annotations must use frozen ordering")
        return self

    def cross(self, name: str) -> CrossActivityAnnotation:
        return next(item for item in self.cross_activity if item.name == name)


class RegimeLevelCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    annotation_n: int = Field(ge=0)


class RegimeSessionCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    session_date: date
    annotation_n: int = Field(ge=0)


class RegimeHypothesisGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    hypothesis: str
    state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    session_composition: tuple[RegimeSessionCount, ...]
    level_composition: tuple[RegimeLevelCount, ...]
    max_session_annotation_n: int = Field(ge=0)
    max_session_percentage: Decimal = Field(ge=0, le=100)
    fewer_than_10_executable: bool
    fewer_than_5_sessions: bool
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("direction composition must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("executable count exceeds annotation count")
        if sum(item.annotation_n for item in self.session_composition) != self.annotation_n:
            raise ValueError("session composition must reconcile")
        if sum(item.annotation_n for item in self.level_composition) != self.annotation_n:
            raise ValueError("level composition must reconcile")
        if self.session_count != len(self.session_composition):
            raise ValueError("session count must match composition")
        if self.fewer_than_10_executable != (self.executable_n < 10):
            raise ValueError("executable sparsity warning mismatch")
        if self.fewer_than_5_sessions != (self.session_count < 5):
            raise ValueError("session sparsity warning mismatch")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("horizons must use frozen ordering")
        return self


class RegimeContextOverlap(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    combined_state: CombinedRegimeState
    context_dimension: str
    context_state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)


class RegimeHypothesisComparisonResult(BaseModel):
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
    source_stage10_9_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    boundaries: tuple[FrozenQuartileBoundary, ...]
    annotations: tuple[RegimeHypothesisAnnotation, ...]
    base_all_horizons: tuple[BaseStrategyHorizonStatistics, ...]
    groups: tuple[RegimeHypothesisGroupStatistics, ...]
    context_overlaps: tuple[RegimeContextOverlap, ...]
    report_version: Literal["predeclared-regime-comparison-v1"] = (
        "predeclared-regime-comparison-v1"
    )
    sample_warning: str = (
        "Thirteen-session development sample; labels are hypotheses, not filters."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one hypothesis annotation")
        if tuple(item.feature_name for item in self.boundaries) != BOUNDARY_FEATURES:
            raise ValueError("boundaries must use frozen feature ordering")
        if tuple(item.horizon for item in self.base_all_horizons) != HORIZON_ORDER:
            raise ValueError("BASE_ALL horizons must use frozen ordering")
        combined = tuple(item for item in self.groups if item.hypothesis == "COMBINED")
        if sum(item.annotation_n for item in combined) != self.confirmed_count:
            raise ValueError("combined states must partition annotations")
        if sum(item.executable_n for item in combined) != self.executable_count:
            raise ValueError("combined states must partition executable outcomes")
        for hypothesis in {item.hypothesis for item in self.groups}:
            rows = tuple(item for item in self.groups if item.hypothesis == hypothesis)
            if sum(item.annotation_n for item in rows) != self.confirmed_count:
                raise ValueError(f"{hypothesis} states must partition annotations")
            if sum(item.executable_n for item in rows) != self.executable_count:
                raise ValueError(f"{hypothesis} states must partition outcomes")
        for combined_state in CombinedRegimeState:
            expected_group = next(
                item
                for item in combined
                if item.state == combined_state.value
            )
            for dimension, _, _ in CONTEXT_SPECS:
                rows = tuple(
                    item
                    for item in self.context_overlaps
                    if item.combined_state is combined_state
                    and item.context_dimension == dimension
                )
                if sum(item.annotation_n for item in rows) != expected_group.annotation_n:
                    raise ValueError("context overlap annotations must reconcile")
                if sum(item.executable_n for item in rows) != expected_group.executable_n:
                    raise ValueError("context overlap outcomes must reconcile")
        return self


def frozen_boundaries(
    result: MarketConditionFeatureResult,
) -> tuple[FrozenQuartileBoundary, ...]:
    """Copy—not recalculate—the accepted Stage 10.9 report boundaries."""

    reports = {item.feature_name: item for item in result.feature_reports}
    if any(name not in reports for name in BOUNDARY_FEATURES):
        raise RegimeHypothesisInputError("Stage 10.9 boundary feature is missing")
    return tuple(
        FrozenQuartileBoundary(
            feature_name=name,
            q1_upper=reports[name].distribution.q1_upper,
            q2_upper=reports[name].distribution.q2_upper,
            q3_upper=reports[name].distribution.q3_upper,
        )
        for name in BOUNDARY_FEATURES
    )


def _quartile(
    value: Decimal | None,
    boundary: FrozenQuartileBoundary,
) -> FeatureQuartile | None:
    if value is None:
        return None
    if boundary.q1_upper is None:
        raise RegimeHypothesisInputError("Available value lacks frozen boundaries")
    if value <= boundary.q1_upper:
        return FeatureQuartile.Q1
    if value <= boundary.q2_upper:
        return FeatureQuartile.Q2
    if value <= boundary.q3_upper:
        return FeatureQuartile.Q3
    return FeatureQuartile.Q4


def _three_band(quartile: FeatureQuartile | None, states):
    if quartile is None:
        return states[3]
    if quartile is FeatureQuartile.Q4:
        return states[0]
    if quartile in (FeatureQuartile.Q2, FeatureQuartile.Q3):
        return states[1]
    return states[2]


def classify_regime_hypothesis(
    annotation: MarketConditionAnnotation,
    boundaries: Sequence[FrozenQuartileBoundary],
) -> RegimeHypothesisAnnotation:
    """Assign predeclared labels without accepting outcomes or future data."""

    boundary_by_name = {item.feature_name: item for item in boundaries}
    if frozenset(boundary_by_name) != frozenset(BOUNDARY_FEATURES):
        raise RegimeHypothesisInputError("Frozen boundary universe mismatch")
    efficiency = annotation.value(EFFICIENCY_FEATURE)
    separation = annotation.value(SEPARATION_FEATURE)
    alternation = annotation.value(ALTERNATION_FEATURE)
    distance = annotation.value(VWAP_DISTANCE_FEATURE)
    efficiency_state = _three_band(
        _quartile(efficiency, boundary_by_name[EFFICIENCY_FEATURE]),
        (
            EfficiencyState.HIGH,
            EfficiencyState.MID,
            EfficiencyState.LOW,
            EfficiencyState.UNAVAILABLE,
        ),
    )
    separation_state = _three_band(
        _quartile(separation, boundary_by_name[SEPARATION_FEATURE]),
        (
            SeparationState.WIDE,
            SeparationState.MID,
            SeparationState.TIGHT,
            SeparationState.UNAVAILABLE,
        ),
    )
    alternation_state = _three_band(
        _quartile(alternation, boundary_by_name[ALTERNATION_FEATURE]),
        (
            AlternationState.HIGH,
            AlternationState.MID,
            AlternationState.LOW,
            AlternationState.UNAVAILABLE,
        ),
    )
    distance_state = _three_band(
        _quartile(distance, boundary_by_name[VWAP_DISTANCE_FEATURE]),
        (
            VwapDistanceState.FAR,
            VwapDistanceState.MID,
            VwapDistanceState.NEAR,
            VwapDistanceState.UNAVAILABLE,
        ),
    )
    crosses = []
    for name, feature in CROSS_FEATURES:
        value = annotation.value(feature)
        quartile = _quartile(value, boundary_by_name[feature])
        crosses.append(
            CrossActivityAnnotation(
                name=name,
                feature_name=feature,
                frozen_value=value,
                exact_count=int(value) if value is not None else None,
                quartile=quartile,
                quartile_state=_three_band(
                    quartile,
                    (
                        CrossQuartileState.TOP,
                        CrossQuartileState.MIDDLE,
                        CrossQuartileState.BOTTOM,
                        CrossQuartileState.UNAVAILABLE,
                    ),
                ),
            )
        )
    if (
        efficiency_state is EfficiencyState.UNAVAILABLE
        or separation_state is SeparationState.UNAVAILABLE
        or alternation_state is AlternationState.UNAVAILABLE
    ):
        combined = CombinedRegimeState.UNAVAILABLE
    elif (
        efficiency_state is EfficiencyState.HIGH
        and separation_state is SeparationState.WIDE
    ):
        combined = CombinedRegimeState.TREND_LIKE_A
    elif (
        efficiency_state is EfficiencyState.LOW
        and alternation_state is AlternationState.HIGH
    ):
        combined = CombinedRegimeState.CHOP_LIKE_A
    else:
        combined = CombinedRegimeState.OTHER
    return RegimeHypothesisAnnotation(
        setup_identity=annotation.setup_identity,
        session_date=annotation.session_date,
        direction=annotation.direction,
        confirmation_bar_timestamp=annotation.confirmation_bar_timestamp,
        signal_known_at=annotation.signal_known_at,
        directional_efficiency_24=efficiency,
        ema_separation_atr14=separation,
        close_alternation_24=alternation,
        confirmation_close_vwap_distance_atr14=distance,
        efficiency_state=efficiency_state,
        separation_state=separation_state,
        alternation_state=alternation_state,
        vwap_distance_state=distance_state,
        cross_activity=tuple(crosses),
        combined_state=combined,
    )


def build_regime_hypothesis_annotations(
    result: MarketConditionFeatureResult,
) -> tuple[RegimeHypothesisAnnotation, ...]:
    boundaries = frozen_boundaries(result)
    return tuple(
        classify_regime_hypothesis(annotation, boundaries)
        for annotation in result.annotations
    )


def _group_statistics(
    hypothesis: str,
    state: str,
    annotations: Sequence[RegimeHypothesisAnnotation],
    context_by_id: dict[str, CombinedContextAnnotation],
    available_outcomes: Sequence[SetupOutcome],
) -> RegimeHypothesisGroupStatistics:
    identities = {item.setup_identity for item in annotations}
    outcomes = tuple(
        item for item in available_outcomes if item.setup_identity in identities
    )
    contexts = tuple(context_by_id[item.setup_identity] for item in annotations)
    session_counts = Counter(item.session_date for item in annotations)
    level_counts = Counter(item.level_type for item in contexts)
    sessions = tuple(
        RegimeSessionCount(session_date=session, annotation_n=session_counts[session])
        for session in sorted(session_counts)
    )
    levels = tuple(
        RegimeLevelCount(level_type=level, annotation_n=level_counts[level])
        for level in LevelType
        if level_counts[level]
    )
    max_session = max(session_counts.values(), default=0)
    with localcontext() as context:
        context.prec = 50
        concentration = (
            Decimal(max_session) * Decimal(100) / Decimal(len(annotations))
            if annotations
            else Decimal(0)
        )
    stats = summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL,
        f"{hypothesis}:{state}",
        outcomes,
    )
    return RegimeHypothesisGroupStatistics(
        hypothesis=hypothesis,
        state=state,
        annotation_n=len(annotations),
        executable_n=len(outcomes),
        long_annotation_n=sum(
            item.direction is SetupDirection.LONG for item in annotations
        ),
        short_annotation_n=sum(
            item.direction is SetupDirection.SHORT for item in annotations
        ),
        session_count=len(sessions),
        session_composition=sessions,
        level_composition=levels,
        max_session_annotation_n=max_session,
        max_session_percentage=concentration,
        fewer_than_10_executable=len(outcomes) < 10,
        fewer_than_5_sessions=len(sessions) < 5,
        horizons=stats.horizons,
    )


def _group_specs(annotations: Sequence[RegimeHypothesisAnnotation]):
    specs: list[
        tuple[str, str, Callable[[RegimeHypothesisAnnotation], bool]]
    ] = []
    individual = (
        ("DIRECTIONAL_EFFICIENCY", "efficiency_state", EfficiencyState),
        ("EMA_SEPARATION", "separation_state", SeparationState),
        ("CLOSE_ALTERNATION", "alternation_state", AlternationState),
        ("VWAP_DISTANCE", "vwap_distance_state", VwapDistanceState),
    )
    for hypothesis, field, states in individual:
        for state in states:
            specs.append(
                (
                    hypothesis,
                    state.value,
                    lambda item, field=field, state=state: getattr(item, field)
                    is state,
                )
            )
    for name, _ in CROSS_FEATURES:
        observed = sorted(
            {
                item.cross(name).exact_count
                for item in annotations
                if item.cross(name).exact_count is not None
            }
        )
        for count in observed:
            specs.append(
                (
                    f"{name}_CROSS_ACTIVITY_EXACT",
                    f"COUNT_{count}",
                    lambda item, name=name, count=count: item.cross(name).exact_count
                    == count,
                )
            )
        specs.append(
            (
                f"{name}_CROSS_ACTIVITY_EXACT",
                "UNAVAILABLE",
                lambda item, name=name: item.cross(name).exact_count is None,
            )
        )
        for state in CrossQuartileState:
            specs.append(
                (
                    f"{name}_CROSS_ACTIVITY_QUARTILE",
                    state.value,
                    lambda item, name=name, state=state: item.cross(
                        name
                    ).quartile_state
                    is state,
                )
            )
    for state in CombinedRegimeState:
        specs.append(
            (
                "COMBINED",
                state.value,
                lambda item, state=state: item.combined_state is state,
            )
        )
    return tuple(specs)


def calculate_regime_hypothesis_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    market_result: MarketConditionFeatureResult,
    context_result: CombinedContextMatrixResult,
    annotations: Sequence[RegimeHypothesisAnnotation],
) -> RegimeHypothesisComparisonResult:
    """Join frozen outcomes only after all hypothesis labels are assigned."""

    ranges = {
        (item.start_date, item.end_date)
        for item in (
            setup_result,
            outcome_result,
            base_statistics,
            market_result,
            context_result,
        )
    }
    if len(ranges) != 1:
        raise RegimeHypothesisInputError("Frozen source ranges do not match")
    population = (
        setup_result.seed_count,
        setup_result.confirmed_count,
        setup_result.non_confirmed_count,
        outcome_result.available_entry_count,
        outcome_result.session_end_unavailable_count,
        outcome_result.missing_entry_count,
    )
    expected = (
        base_statistics.break_seed_count,
        base_statistics.confirmed_count,
        base_statistics.non_confirmed_count,
        base_statistics.executable_count,
        base_statistics.session_end_unavailable_count,
        base_statistics.missing_entry_count,
    )
    if population != expected:
        raise RegimeHypothesisInputError("Stage 9 population mismatch")
    ids = {item.setup_identity for item in annotations}
    context_by_id = {item.setup_identity: item for item in context_result.annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    if len(ids) != len(annotations) or ids != set(context_by_id) or ids != set(
        outcome_by_id
    ):
        raise RegimeHypothesisInputError("Stage 10.9/context/outcome identities differ")
    source_annotations = {
        item.setup_identity: item for item in market_result.annotations
    }
    for annotation in annotations:
        source = source_annotations[annotation.setup_identity]
        if (
            annotation.directional_efficiency_24
            != source.value(EFFICIENCY_FEATURE)
            or annotation.ema_separation_atr14
            != source.value(SEPARATION_FEATURE)
            or annotation.close_alternation_24
            != source.value(ALTERNATION_FEATURE)
            or annotation.confirmation_close_vwap_distance_atr14
            != source.value(VWAP_DISTANCE_FEATURE)
        ):
            raise RegimeHypothesisInputError("Stage 10.9 feature value changed")
        for name, feature in CROSS_FEATURES:
            if annotation.cross(name).frozen_value != source.value(feature):
                raise RegimeHypothesisInputError("Stage 10.9 cross value changed")
        context = context_by_id[annotation.setup_identity]
        if (
            annotation.session_date,
            annotation.direction,
            annotation.confirmation_bar_timestamp,
            annotation.signal_known_at,
        ) != (
            context.session_date,
            context.direction,
            context.confirmation_bar_timestamp,
            context.signal_known_at,
        ):
            raise RegimeHypothesisInputError("Stage 10 annotation metadata mismatch")
    available = tuple(
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
        BaseStrategyGroupDimension.OVERALL, "OVERALL", available
    ) != baseline:
        raise RegimeHypothesisInputError("BASE_ALL does not reproduce Stage 9.3")
    groups = []
    for hypothesis, state, predicate in _group_specs(annotations):
        selected = tuple(item for item in annotations if predicate(item))
        groups.append(
            _group_statistics(
                hypothesis,
                state,
                selected,
                context_by_id,
                available,
            )
        )
    group_by_combined = {
        CombinedRegimeState(item.state): item
        for item in groups
        if item.hypothesis == "COMBINED"
    }
    overlaps = []
    for combined_state in CombinedRegimeState:
        selected_annotations = tuple(
            item for item in annotations if item.combined_state is combined_state
        )
        selected_ids = {item.setup_identity for item in selected_annotations}
        selected_contexts = tuple(
            context_by_id[item.setup_identity] for item in selected_annotations
        )
        for dimension, field, states in CONTEXT_SPECS:
            for state in states:
                state_ids = {
                    item.setup_identity
                    for item in selected_contexts
                    if getattr(item, field) is state
                }
                overlaps.append(
                    RegimeContextOverlap(
                        combined_state=combined_state,
                        context_dimension=dimension,
                        context_state=state.value,
                        annotation_n=len(state_ids),
                        executable_n=sum(
                            item.setup_identity in state_ids for item in available
                        ),
                    )
                )
        expected_group = group_by_combined[combined_state]
        if len(selected_ids) != expected_group.annotation_n:
            raise RegimeHypothesisInputError("Combined overlap population mismatch")
    return RegimeHypothesisComparisonResult(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        development_session_count=base_statistics.development_session_count,
        source_stage10_9_hash=sha256(
            market_result.model_dump_json().encode()
        ).hexdigest(),
        boundaries=frozen_boundaries(market_result),
        annotations=tuple(annotations),
        base_all_horizons=baseline.horizons,
        groups=tuple(groups),
        context_overlaps=tuple(overlaps),
    )
