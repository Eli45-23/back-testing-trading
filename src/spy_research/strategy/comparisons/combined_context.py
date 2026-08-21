"""Stage 10.8 immutable reconciliation of accepted context annotations."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.interactions import LevelType
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyHorizonStatistics,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    Ema20VwapAlignmentAnnotation,
    Ema20VwapAlignmentState,
)
from spy_research.strategy.comparisons.ema20_vwap_cross_models import (
    Ema20VwapCrossContextAnnotation,
    Ema20VwapCrossContextState,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentAnnotation,
    Ema9VwapAlignmentState,
    Ema9VwapCrossContextAnnotation,
    Ema9VwapCrossContextState,
    EmaAlignmentAnnotation,
    EmaAlignmentState,
    EmaCrossContextAnnotation,
    EmaCrossContextState,
    VwapAlignmentAnnotation,
    VwapAlignmentState,
)
from spy_research.strategy.models import (
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcomeResult,
)


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")
MARGINAL_DIMENSIONS = (
    "EMA9_20_ALIGNMENT",
    "EMA9_20_CROSS_CONTEXT",
    "PRICE_VWAP_ALIGNMENT",
    "EMA9_VWAP_ALIGNMENT",
    "EMA9_VWAP_CROSS_CONTEXT",
    "EMA20_VWAP_ALIGNMENT",
    "EMA20_VWAP_CROSS_CONTEXT",
)


class CombinedContextInputError(ValueError):
    """Accepted annotations cannot form a trustworthy combined matrix."""


class CombinedContextKey(BaseModel):
    """Exact grouping key; no field is interpreted as strategy quality."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    ema9_20_alignment: EmaAlignmentState
    ema9_20_cross_context: EmaCrossContextState
    ema9_20_bars_since_cross: int | None = Field(default=None, ge=0)
    price_vwap_alignment: VwapAlignmentState
    ema9_vwap_alignment: Ema9VwapAlignmentState
    ema9_vwap_cross_context: Ema9VwapCrossContextState
    ema9_vwap_bars_since_cross: int | None = Field(default=None, ge=0)
    ema20_vwap_alignment: Ema20VwapAlignmentState
    ema20_vwap_cross_context: Ema20VwapCrossContextState
    ema20_vwap_bars_since_cross: int | None = Field(default=None, ge=0)


class CombinedContextAnnotation(BaseModel):
    """One setup joined losslessly to all accepted Stage 10.1-10.7 states."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    level_type: LevelType
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    ema9_20_alignment: EmaAlignmentState
    ema9_20_cross_context: EmaCrossContextState
    ema9_20_bars_since_cross: int | None = Field(default=None, ge=0)
    price_vwap_alignment: VwapAlignmentState
    ema9_vwap_alignment: Ema9VwapAlignmentState
    ema9_vwap_cross_context: Ema9VwapCrossContextState
    ema9_vwap_bars_since_cross: int | None = Field(default=None, ge=0)
    ema20_vwap_alignment: Ema20VwapAlignmentState
    ema20_vwap_cross_context: Ema20VwapCrossContextState
    ema20_vwap_bars_since_cross: int | None = Field(default=None, ge=0)
    matrix_version: Literal["combined-stage10-context-v1"] = (
        "combined-stage10-context-v1"
    )

    @model_validator(mode="after")
    def reconcile_timing_and_recency(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("signal-known time must follow confirmation by five minutes")
        recency_specs = (
            (
                self.ema9_20_cross_context is EmaCrossContextState.NO_PRIOR_CROSS,
                self.ema9_20_bars_since_cross,
                "EMA9/20",
            ),
            (
                self.ema9_vwap_cross_context
                is Ema9VwapCrossContextState.NO_PRIOR_EMA9_VWAP_CROSS,
                self.ema9_vwap_bars_since_cross,
                "EMA9/VWAP",
            ),
            (
                self.ema20_vwap_cross_context
                is Ema20VwapCrossContextState.NO_PRIOR_EMA20_VWAP_CROSS,
                self.ema20_vwap_bars_since_cross,
                "EMA20/VWAP",
            ),
        )
        for no_prior, bars, label in recency_specs:
            if no_prior != (bars is None):
                raise ValueError(f"{label} state and exact recency do not reconcile")
        return self

    @property
    def context_key(self) -> CombinedContextKey:
        return CombinedContextKey(
            direction=self.direction,
            ema9_20_alignment=self.ema9_20_alignment,
            ema9_20_cross_context=self.ema9_20_cross_context,
            ema9_20_bars_since_cross=self.ema9_20_bars_since_cross,
            price_vwap_alignment=self.price_vwap_alignment,
            ema9_vwap_alignment=self.ema9_vwap_alignment,
            ema9_vwap_cross_context=self.ema9_vwap_cross_context,
            ema9_vwap_bars_since_cross=self.ema9_vwap_bars_since_cross,
            ema20_vwap_alignment=self.ema20_vwap_alignment,
            ema20_vwap_cross_context=self.ema20_vwap_cross_context,
            ema20_vwap_bars_since_cross=self.ema20_vwap_bars_since_cross,
        )


class CombinedContextLevelCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    annotation_n: int = Field(ge=0)


class CombinedContextGroupStatistics(BaseModel):
    """One naturally observed exact combination and unchanged outcomes."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    context_key: CombinedContextKey
    annotation_n: int = Field(ge=1)
    executable_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    level_composition: tuple[CombinedContextLevelCount, ...]
    session_count: int = Field(ge=1)
    percentage_of_base_all: Decimal = Field(ge=0, le=100)
    singleton: bool
    n_le_5: bool
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("context directions must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("executable count cannot exceed annotations")
        if sum(item.annotation_n for item in self.level_composition) != self.annotation_n:
            raise ValueError("level composition must reconcile")
        observed_levels = {item.level_type for item in self.level_composition}
        if tuple(item.level_type for item in self.level_composition) != tuple(
            level for level in LevelType if level in observed_levels
        ):
            raise ValueError("level composition must be deterministic")
        if self.singleton != (self.annotation_n == 1):
            raise ValueError("singleton flag mismatch")
        if self.n_le_5 != (self.annotation_n <= 5):
            raise ValueError("n<=5 flag mismatch")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("context horizons must use frozen ordering")
        if any(
            item.complete_n + item.incomplete_n != self.executable_n
            for item in self.horizons
        ):
            raise ValueError("horizon populations must match executable count")
        return self


class CombinedContextMarginalCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dimension: Literal[
        "EMA9_20_ALIGNMENT",
        "EMA9_20_CROSS_CONTEXT",
        "PRICE_VWAP_ALIGNMENT",
        "EMA9_VWAP_ALIGNMENT",
        "EMA9_VWAP_CROSS_CONTEXT",
        "EMA20_VWAP_ALIGNMENT",
        "EMA20_VWAP_CROSS_CONTEXT",
    ]
    state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)


class CombinedContextMatrixResult(BaseModel):
    """Complete deterministic Stage 10.8 reconciliation and sparse matrix."""

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
    annotations: tuple[CombinedContextAnnotation, ...]
    base_all_horizons: tuple[BaseStrategyHorizonStatistics, ...]
    marginal_counts: tuple[CombinedContextMarginalCount, ...]
    context_groups: tuple[CombinedContextGroupStatistics, ...]
    singleton_group_count: int = Field(ge=0)
    n_le_5_group_count: int = Field(ge=0)
    matrix_version: Literal["combined-stage10-context-matrix-v1"] = (
        "combined-stage10-context-matrix-v1"
    )
    sample_warning: str = (
        "Exact combinations are descriptive; sparse groups are not evidence of edge."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one combined record")
        if len({item.setup_identity for item in self.annotations}) != len(
            self.annotations
        ):
            raise ValueError("combined setup identities must be unique")
        if tuple(item.horizon for item in self.base_all_horizons) != HORIZON_ORDER:
            raise ValueError("BASE_ALL horizons must use frozen ordering")
        if any(
            item.complete_n + item.incomplete_n != self.executable_count
            for item in self.base_all_horizons
        ):
            raise ValueError("BASE_ALL horizon populations must reconcile")
        if sum(item.annotation_n for item in self.context_groups) != self.confirmed_count:
            raise ValueError("context groups must partition annotations")
        if sum(item.executable_n for item in self.context_groups) != self.executable_count:
            raise ValueError("context groups must partition outcomes")
        if self.singleton_group_count != sum(
            item.singleton for item in self.context_groups
        ):
            raise ValueError("singleton group count mismatch")
        if self.n_le_5_group_count != sum(item.n_le_5 for item in self.context_groups):
            raise ValueError("n<=5 group count mismatch")
        for dimension in MARGINAL_DIMENSIONS:
            rows = tuple(
                item for item in self.marginal_counts if item.dimension == dimension
            )
            if sum(item.annotation_n for item in rows) != self.confirmed_count:
                raise ValueError(f"{dimension} annotations do not reconcile")
            if sum(item.executable_n for item in rows) != self.executable_count:
                raise ValueError(f"{dimension} outcomes do not reconcile")
        return self


def _index_annotations(annotations, confirmed_ids, label):
    indexed = {item.setup_identity: item for item in annotations}
    if len(indexed) != len(annotations) or frozenset(indexed) != confirmed_ids:
        raise CombinedContextInputError(f"{label} identities do not reconcile")
    return indexed


def combine_context_annotations(
    setup_result: BasePriceActionResult,
    ema_annotations: Sequence[EmaAlignmentAnnotation],
    ema_cross_annotations: Sequence[EmaCrossContextAnnotation],
    price_vwap_annotations: Sequence[VwapAlignmentAnnotation],
    ema9_vwap_annotations: Sequence[Ema9VwapAlignmentAnnotation],
    ema9_vwap_cross_annotations: Sequence[Ema9VwapCrossContextAnnotation],
    ema20_vwap_annotations: Sequence[Ema20VwapAlignmentAnnotation],
    ema20_vwap_cross_annotations: Sequence[Ema20VwapCrossContextAnnotation],
) -> tuple[CombinedContextAnnotation, ...]:
    """Join accepted records by setup identity without changing any state."""

    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    confirmed_ids = frozenset(item.setup_identity for item in confirmed)
    sources = (
        _index_annotations(ema_annotations, confirmed_ids, "Stage 10.1"),
        _index_annotations(ema_cross_annotations, confirmed_ids, "Stage 10.2"),
        _index_annotations(price_vwap_annotations, confirmed_ids, "Stage 10.3"),
        _index_annotations(ema9_vwap_annotations, confirmed_ids, "Stage 10.4"),
        _index_annotations(
            ema9_vwap_cross_annotations, confirmed_ids, "Stage 10.5"
        ),
        _index_annotations(ema20_vwap_annotations, confirmed_ids, "Stage 10.6"),
        _index_annotations(
            ema20_vwap_cross_annotations, confirmed_ids, "Stage 10.7"
        ),
    )
    combined = []
    for setup in confirmed:
        rows = tuple(source[setup.setup_identity] for source in sources)
        expected_metadata = (
            setup.session_date,
            setup.direction,
            setup.confirmation_bar_timestamp,
            setup.signal_known_at,
        )
        if any(
            (
                row.session_date,
                row.direction,
                row.confirmation_bar_timestamp,
                row.signal_known_at,
            )
            != expected_metadata
            for row in rows
        ):
            raise CombinedContextInputError("Stage 10 annotation metadata mismatch")
        ema, ema_cross, price, ema9, ema9_cross, ema20, ema20_cross = rows
        combined.append(
            CombinedContextAnnotation(
                setup_identity=setup.setup_identity,
                session_date=setup.session_date,
                direction=setup.direction,
                level_type=setup.level_type,
                confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
                signal_known_at=setup.signal_known_at,
                ema9_20_alignment=ema.alignment_state,
                ema9_20_cross_context=ema_cross.cross_state,
                ema9_20_bars_since_cross=ema_cross.bars_since_cross,
                price_vwap_alignment=price.alignment_state,
                ema9_vwap_alignment=ema9.alignment_state,
                ema9_vwap_cross_context=ema9_cross.cross_state,
                ema9_vwap_bars_since_cross=ema9_cross.bars_since_cross,
                ema20_vwap_alignment=ema20.alignment_state,
                ema20_vwap_cross_context=ema20_cross.cross_state,
                ema20_vwap_bars_since_cross=ema20_cross.bars_since_cross,
            )
        )
    return tuple(combined)


def _marginal_specs():
    return (
        ("EMA9_20_ALIGNMENT", "ema9_20_alignment", EmaAlignmentState),
        ("EMA9_20_CROSS_CONTEXT", "ema9_20_cross_context", EmaCrossContextState),
        ("PRICE_VWAP_ALIGNMENT", "price_vwap_alignment", VwapAlignmentState),
        ("EMA9_VWAP_ALIGNMENT", "ema9_vwap_alignment", Ema9VwapAlignmentState),
        (
            "EMA9_VWAP_CROSS_CONTEXT",
            "ema9_vwap_cross_context",
            Ema9VwapCrossContextState,
        ),
        ("EMA20_VWAP_ALIGNMENT", "ema20_vwap_alignment", Ema20VwapAlignmentState),
        (
            "EMA20_VWAP_CROSS_CONTEXT",
            "ema20_vwap_cross_context",
            Ema20VwapCrossContextState,
        ),
    )


def calculate_combined_context_matrix(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[CombinedContextAnnotation],
) -> CombinedContextMatrixResult:
    """Create deterministic exact combinations and descriptive outcome rows."""

    if not (
        setup_result.start_date == outcome_result.start_date == base_statistics.start_date
        and setup_result.end_date == outcome_result.end_date == base_statistics.end_date
    ):
        raise CombinedContextInputError("Frozen source ranges do not match")
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
        raise CombinedContextInputError("Stage 9 population mismatch")
    current_by_id = {item.setup_identity: item for item in annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    if len(current_by_id) != len(annotations) or frozenset(current_by_id) != frozenset(
        outcome_by_id
    ):
        raise CombinedContextInputError("Combined annotations/outcomes do not reconcile")
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
    reproduced = summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL, "OVERALL", available
    )
    if reproduced != baseline:
        raise CombinedContextInputError("BASE_ALL does not reproduce Stage 9.3")

    marginal_counts = []
    for dimension, field, states in _marginal_specs():
        for state in states:
            identities = {
                item.setup_identity
                for item in annotations
                if getattr(item, field) is state
            }
            marginal_counts.append(
                CombinedContextMarginalCount(
                    dimension=dimension,
                    state=state.value,
                    annotation_n=len(identities),
                    executable_n=sum(
                        item.setup_identity in identities for item in available
                    ),
                )
            )

    grouped: dict[str, list[CombinedContextAnnotation]] = {}
    keys: dict[str, CombinedContextKey] = {}
    for annotation in annotations:
        key = annotation.context_key
        serialized = key.model_dump_json()
        keys[serialized] = key
        grouped.setdefault(serialized, []).append(annotation)
    context_groups = []
    for serialized in sorted(grouped):
        group_annotations = tuple(grouped[serialized])
        identities = {item.setup_identity for item in group_annotations}
        selected = tuple(
            item for item in available if item.setup_identity in identities
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, serialized, selected
        )
        level_composition = tuple(
            CombinedContextLevelCount(
                level_type=level,
                annotation_n=sum(item.level_type is level for item in group_annotations),
            )
            for level in LevelType
            if any(item.level_type is level for item in group_annotations)
        )
        with localcontext() as context:
            context.prec = 50
            percentage = (
                Decimal(len(group_annotations))
                * Decimal(100)
                / Decimal(len(annotations))
            )
        context_groups.append(
            CombinedContextGroupStatistics(
                context_key=keys[serialized],
                annotation_n=len(group_annotations),
                executable_n=len(selected),
                long_annotation_n=sum(
                    item.direction is SetupDirection.LONG
                    for item in group_annotations
                ),
                short_annotation_n=sum(
                    item.direction is SetupDirection.SHORT
                    for item in group_annotations
                ),
                level_composition=level_composition,
                session_count=len({item.session_date for item in group_annotations}),
                percentage_of_base_all=percentage,
                singleton=len(group_annotations) == 1,
                n_le_5=len(group_annotations) <= 5,
                horizons=stats.horizons,
            )
        )
    return CombinedContextMatrixResult(
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
        marginal_counts=tuple(marginal_counts),
        context_groups=tuple(context_groups),
        singleton_group_count=sum(item.singleton for item in context_groups),
        n_le_5_group_count=sum(item.n_le_5 for item in context_groups),
    )
