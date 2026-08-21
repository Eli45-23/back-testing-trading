"""Pure Stage 10.6 EMA20/VWAP annotation and controlled comparison."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.indicators import FiveMinuteIndicatorRow, FiveMinuteVwapRow
from spy_research.indicators.vwap import VWAP_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import DistributionSummary, summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyHorizonStatistics,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentAnnotation,
    Ema9VwapAlignmentState,
    Ema9VwapCrossContextAnnotation,
    Ema9VwapCrossContextState,
    EmaAlignmentAnnotation,
    EmaAlignmentState,
    VwapAlignmentAnnotation,
    VwapAlignmentState,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcomeResult,
)


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")


class Ema20VwapComparisonInputError(ValueError):
    """Frozen Stage 3/9/10 inputs cannot form a trustworthy comparison."""


class Ema20VwapAlignmentState(StrEnum):
    EMA20_VWAP_ALIGNED = "EMA20_VWAP_ALIGNED"
    EMA20_VWAP_NOT_ALIGNED = "EMA20_VWAP_NOT_ALIGNED"
    EMA20_VWAP_UNAVAILABLE = "EMA20_VWAP_UNAVAILABLE"


class Ema20VwapComparisonGroupName(StrEnum):
    BASE_ALL = "BASE_ALL"
    EMA20_VWAP_ALIGNED = "EMA20_VWAP_ALIGNED"
    EMA20_VWAP_NOT_ALIGNED = "EMA20_VWAP_NOT_ALIGNED"
    EMA20_VWAP_UNAVAILABLE = "EMA20_VWAP_UNAVAILABLE"


class Ema20VwapAlignmentAnnotation(BaseModel):
    """Exact confirmation-row EMA20/VWAP label for one Stage 9 setup."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    ema9: Decimal | None
    ema20: Decimal | None
    vwap: Decimal | None
    indicator_timestamp: datetime | None
    alignment_state: Ema20VwapAlignmentState
    signed_ema20_vwap_distance: Decimal | None
    absolute_ema20_vwap_distance: Decimal | None
    directional_ema20_vwap_distance: Decimal | None
    stack_state: str
    comparison_version: Literal["ema20-vwap-at-confirmation-v1"] = (
        "ema20-vwap-at-confirmation-v1"
    )

    @model_validator(mode="after")
    def reconcile_annotation(self) -> Self:
        if self.signal_known_at != self.confirmation_bar_timestamp + timedelta(minutes=5):
            raise ValueError("setup known-at must follow confirmation by five minutes")
        distances = (
            self.signed_ema20_vwap_distance,
            self.absolute_ema20_vwap_distance,
            self.directional_ema20_vwap_distance,
        )
        if self.ema20 is None or self.vwap is None:
            if self.indicator_timestamp is not None or any(
                value is not None for value in distances
            ):
                raise ValueError("unavailable EMA20/VWAP requires null derived fields")
            if self.alignment_state is not Ema20VwapAlignmentState.EMA20_VWAP_UNAVAILABLE:
                raise ValueError("missing EMA20 or VWAP requires unavailable state")
        else:
            if self.indicator_timestamp != self.confirmation_bar_timestamp:
                raise ValueError("EMA20/VWAP timestamp must equal confirmation timestamp")
            if any(value is None for value in distances):
                raise ValueError("available EMA20/VWAP requires all distance fields")
            with localcontext(VWAP_CONTEXT):
                signed = self.ema20 - self.vwap
                directional = signed if self.direction is SetupDirection.LONG else -signed
            if self.signed_ema20_vwap_distance != signed:
                raise ValueError("signed EMA20/VWAP distance mismatch")
            if self.absolute_ema20_vwap_distance != abs(signed):
                raise ValueError("absolute EMA20/VWAP distance mismatch")
            if self.directional_ema20_vwap_distance != directional:
                raise ValueError("directional EMA20/VWAP distance mismatch")
            expected = (
                Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED
                if directional > 0
                else Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED
            )
            if self.alignment_state is not expected:
                raise ValueError("EMA20/VWAP state does not match directional distance")
        if self.stack_state != indicator_stack_state(self.ema9, self.ema20, self.vwap):
            raise ValueError("indicator stack state is not deterministic")
        return self


class Ema20VwapBaselineDelta(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    horizon: Literal["5m", "15m", "30m", "60m", "EOD"]
    median_mfe_delta: Decimal | None
    median_mae_delta: Decimal | None
    median_balance_delta: Decimal | None


class Ema20VwapGroupStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Ema20VwapComparisonGroupName
    annotation_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    horizons: tuple[BaseStrategyHorizonStatistics, ...]
    deltas: tuple[Ema20VwapBaselineDelta, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("direction composition must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("executable count cannot exceed annotations")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("horizons must use frozen ordering")
        if tuple(item.horizon for item in self.deltas) != HORIZON_ORDER:
            raise ValueError("deltas must use frozen ordering")
        return self


class Ema20VwapDirectionStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    direction: SetupDirection
    alignment_state: Ema20VwapAlignmentState
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_eod(self) -> Self:
        if self.eod.horizon != "EOD":
            raise ValueError("direction row must contain EOD statistics")
        return self


class Ema20VwapLevelStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    level_type: LevelType
    alignment_state: Ema20VwapAlignmentState
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def validate_level(self) -> Self:
        if self.executable_n > self.annotation_n:
            raise ValueError("level executable count cannot exceed annotations")
        if self.eod.horizon != "EOD":
            raise ValueError("level row must contain EOD statistics")
        return self


class Ema20VwapDistanceStatistics(BaseModel):
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
            raise ValueError("distance signs must reconcile")
        return self


class Ema20VwapCrossTabCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_dimension: Literal[
        "EMA9_VWAP", "EMA9_EMA20", "PRICE_VWAP", "EMA9_VWAP_CROSS"
    ]
    source_state: str
    ema20_vwap_state: Ema20VwapAlignmentState
    annotation_n: int = Field(ge=0)


class IndicatorStackStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    stack_state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def reconcile_stack(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("stack directions must reconcile")
        if self.executable_n > self.annotation_n:
            raise ValueError("stack executable count cannot exceed annotations")
        if self.eod.horizon != "EOD":
            raise ValueError("stack row must contain EOD statistics")
        return self


class Ema20VwapAlignmentComparisonResult(BaseModel):
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
    annotations: tuple[Ema20VwapAlignmentAnnotation, ...]
    groups: tuple[Ema20VwapGroupStatistics, ...]
    direction_groups: tuple[Ema20VwapDirectionStatistics, ...]
    level_groups: tuple[Ema20VwapLevelStatistics, ...]
    distance_statistics: tuple[Ema20VwapDistanceStatistics, ...]
    ema9_vwap_cross_tab: tuple[Ema20VwapCrossTabCount, ...]
    ema_alignment_cross_tab: tuple[Ema20VwapCrossTabCount, ...]
    price_vwap_cross_tab: tuple[Ema20VwapCrossTabCount, ...]
    ema9_vwap_cross_context_cross_tab: tuple[Ema20VwapCrossTabCount, ...]
    stack_groups: tuple[IndicatorStackStatistics, ...]
    comparison_version: Literal["controlled-ema20-vwap-direction-v1"] = (
        "controlled-ema20-vwap-direction-v1"
    )
    sample_warning: str = (
        "Exploratory descriptive research; not evidence of stable expectancy."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one EMA20/VWAP annotation")
        if len({item.setup_identity for item in self.annotations}) != len(self.annotations):
            raise ValueError("EMA20/VWAP annotations require unique identities")
        if tuple(item.name for item in self.groups) != tuple(
            Ema20VwapComparisonGroupName
        ):
            raise ValueError("groups must use frozen ordering")
        if self.groups[0].annotation_n != self.confirmed_count:
            raise ValueError("BASE_ALL annotation mismatch")
        if self.groups[0].executable_n != self.executable_count:
            raise ValueError("BASE_ALL executable mismatch")
        if sum(item.annotation_n for item in self.groups[1:]) != self.confirmed_count:
            raise ValueError("states must partition annotations")
        if sum(item.executable_n for item in self.groups[1:]) != self.executable_count:
            raise ValueError("states must partition outcomes")
        expected_directions = tuple(
            (direction, state)
            for direction in SetupDirection
            for state in Ema20VwapAlignmentState
        )
        if tuple(
            (item.direction, item.alignment_state) for item in self.direction_groups
        ) != expected_directions:
            raise ValueError("direction rows must use frozen ordering")
        expected_levels = tuple(
            (level, state)
            for level in LevelType
            for state in Ema20VwapAlignmentState
        )
        if tuple(
            (item.level_type, item.alignment_state) for item in self.level_groups
        ) != expected_levels:
            raise ValueError("level rows must use frozen ordering")
        if sum(item.annotation_n for item in self.stack_groups) != self.confirmed_count:
            raise ValueError("stack states must partition annotations")
        for table in (
            self.ema9_vwap_cross_tab,
            self.ema_alignment_cross_tab,
            self.price_vwap_cross_tab,
            self.ema9_vwap_cross_context_cross_tab,
        ):
            if sum(item.annotation_n for item in table) != self.confirmed_count:
                raise ValueError("cross-tab must reconcile annotations")
        if tuple(item.direction for item in self.distance_statistics) != (
            None,
            SetupDirection.LONG,
            SetupDirection.SHORT,
        ):
            raise ValueError("distance rows must be overall, LONG, SHORT")
        direction_counts = (
            self.confirmed_count,
            sum(item.direction is SetupDirection.LONG for item in self.annotations),
            sum(item.direction is SetupDirection.SHORT for item in self.annotations),
        )
        for item, population_n in zip(
            self.distance_statistics, direction_counts, strict=True
        ):
            if item.distribution.n + item.unavailable_n != population_n:
                raise ValueError("distance availability must reconcile")
        return self


def indicator_stack_state(
    ema9: Decimal | None, ema20: Decimal | None, vwap: Decimal | None
) -> str:
    """Return exact, deterministic descending indicator ordering."""

    values = {"EMA9": ema9, "EMA20": ema20, "VWAP": vwap}
    available = [(label, value) for label, value in values.items() if value is not None]
    unavailable = sorted(label for label, value in values.items() if value is None)
    groups: list[str] = []
    for value in sorted({value for _, value in available}, reverse=True):
        labels = sorted(label for label, item_value in available if item_value == value)
        groups.append(" = ".join(labels))
    ordering = " > ".join(groups)
    if unavailable:
        suffix = ", ".join(f"{label}=UNAVAILABLE" for label in unavailable)
        return f"{ordering} | {suffix}" if ordering else suffix
    return ordering


def annotate_ema20_vwap_alignment(
    setup: BasePriceActionCandidate,
    ema_row: FiveMinuteIndicatorRow | None,
    vwap_row: FiveMinuteVwapRow | None,
) -> Ema20VwapAlignmentAnnotation:
    """Label one setup from exact confirmation-row EMA20 and VWAP only."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise Ema20VwapComparisonInputError("Only confirmed setups may be annotated")
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise Ema20VwapComparisonInputError("Confirmed setup lacks frozen timing")
    if setup.signal_known_at != setup.confirmation_bar_timestamp + timedelta(minutes=5):
        raise Ema20VwapComparisonInputError(
            "Signal-known time must follow confirmation by 5 minutes"
        )
    for row, label in ((ema_row, "EMA20"), (vwap_row, "VWAP")):
        if row is not None and (
            row.symbol != setup.symbol
            or row.session_date != setup.session_date
            or row.timestamp != setup.confirmation_bar_timestamp
            or row.timeframe != "5Min"
            or row.session_mode != "RTH_ONLY"
        ):
            raise Ema20VwapComparisonInputError(
                f"{label} row must match confirmation timestamp and RTH provenance"
            )
    ema9 = ema_row.ema9 if ema_row is not None else None
    ema20 = ema_row.ema20 if ema_row is not None else None
    vwap = vwap_row.vwap if vwap_row is not None else None
    common = dict(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        ema9=ema9,
        ema20=ema20,
        vwap=vwap,
        stack_state=indicator_stack_state(ema9, ema20, vwap),
    )
    if ema20 is None or vwap is None:
        return Ema20VwapAlignmentAnnotation(
            **common,
            indicator_timestamp=None,
            alignment_state=Ema20VwapAlignmentState.EMA20_VWAP_UNAVAILABLE,
            signed_ema20_vwap_distance=None,
            absolute_ema20_vwap_distance=None,
            directional_ema20_vwap_distance=None,
        )
    with localcontext(VWAP_CONTEXT):
        signed = ema20 - vwap
        directional = signed if setup.direction is SetupDirection.LONG else -signed
    state = (
        Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED
        if directional > 0
        else Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED
    )
    return Ema20VwapAlignmentAnnotation(
        **common,
        indicator_timestamp=setup.confirmation_bar_timestamp,
        alignment_state=state,
        signed_ema20_vwap_distance=signed,
        absolute_ema20_vwap_distance=abs(signed),
        directional_ema20_vwap_distance=directional,
    )


def annotate_confirmed_ema20_vwap_alignment(
    setup_result: BasePriceActionResult,
    ema_rows: Sequence[FiveMinuteIndicatorRow],
    vwap_rows: Sequence[FiveMinuteVwapRow],
) -> tuple[Ema20VwapAlignmentAnnotation, ...]:
    """Annotate every confirmed setup by exact timestamp lookup only."""

    def index_rows(rows, label):
        indexed = {}
        previous = None
        for row in rows:
            key = (row.session_date, row.timestamp)
            if key in indexed:
                raise Ema20VwapComparisonInputError(f"Duplicate {label} timestamp")
            if previous is not None and row.timestamp <= previous:
                raise Ema20VwapComparisonInputError(f"{label} rows must be chronological")
            indexed[key] = row
            previous = row.timestamp
        return indexed

    ema_by_key = index_rows(ema_rows, "EMA")
    vwap_by_key = index_rows(vwap_rows, "VWAP")
    confirmed = tuple(
        item for item in setup_result.candidates if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = tuple(
        annotate_ema20_vwap_alignment(
            item,
            ema_by_key.get((item.session_date, item.confirmation_bar_timestamp)),
            vwap_by_key.get((item.session_date, item.confirmation_bar_timestamp)),
        )
        for item in confirmed
    )
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise Ema20VwapComparisonInputError("Duplicate EMA20/VWAP annotation identity")
    return annotations


def _delta(left: Decimal | None, right: Decimal | None) -> Decimal | None:
    return left - right if left is not None and right is not None else None


def _distance_summary(annotations, direction):
    population = tuple(
        item for item in annotations if direction is None or item.direction is direction
    )
    values = tuple(
        item.directional_ema20_vwap_distance
        for item in population
        if item.directional_ema20_vwap_distance is not None
    )
    return Ema20VwapDistanceStatistics(
        direction=direction,
        distribution=summarize_distribution(values),
        positive_n=sum(value > 0 for value in values),
        zero_n=sum(value == 0 for value in values),
        negative_n=sum(value < 0 for value in values),
        unavailable_n=len(population) - len(values),
    )


def calculate_ema20_vwap_alignment_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[Ema20VwapAlignmentAnnotation],
    ema9_vwap_annotations: Sequence[Ema9VwapAlignmentAnnotation],
    ema_annotations: Sequence[EmaAlignmentAnnotation],
    price_vwap_annotations: Sequence[VwapAlignmentAnnotation],
    ema9_cross_annotations: Sequence[Ema9VwapCrossContextAnnotation],
) -> Ema20VwapAlignmentComparisonResult:
    """Describe unchanged Stage 9 outcomes by EMA20/VWAP state."""

    if not (
        setup_result.start_date == outcome_result.start_date == base_statistics.start_date
        and setup_result.end_date == outcome_result.end_date == base_statistics.end_date
    ):
        raise Ema20VwapComparisonInputError("Frozen source ranges do not match")
    confirmed = tuple(
        item for item in setup_result.candidates if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_id = {item.setup_identity: item for item in confirmed}
    current_by_id = {item.setup_identity: item for item in annotations}
    ema9_by_id = {item.setup_identity: item for item in ema9_vwap_annotations}
    ema_by_id = {item.setup_identity: item for item in ema_annotations}
    price_by_id = {item.setup_identity: item for item in price_vwap_annotations}
    cross_by_id = {item.setup_identity: item for item in ema9_cross_annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    maps = (
        setup_by_id,
        current_by_id,
        ema9_by_id,
        ema_by_id,
        price_by_id,
        cross_by_id,
        outcome_by_id,
    )
    if any(len(item) != len(confirmed) for item in maps):
        raise Ema20VwapComparisonInputError("Comparison identities are incomplete")
    if len({frozenset(item) for item in maps}) != 1:
        raise Ema20VwapComparisonInputError("Comparison identities do not match")
    source_population = (
        setup_result.seed_count,
        setup_result.confirmed_count,
        setup_result.non_confirmed_count,
        outcome_result.available_entry_count,
        outcome_result.session_end_unavailable_count,
        outcome_result.missing_entry_count,
    )
    baseline_population = (
        base_statistics.break_seed_count,
        base_statistics.confirmed_count,
        base_statistics.non_confirmed_count,
        base_statistics.executable_count,
        base_statistics.session_end_unavailable_count,
        base_statistics.missing_entry_count,
    )
    if source_population != baseline_population:
        raise Ema20VwapComparisonInputError("Stage 9.3 population mismatch")
    available = tuple(
        item for item in outcome_result.outcomes
        if item.entry_reference.entry_status is EntryStatus.AVAILABLE
    )
    baseline = next(
        item for item in base_statistics.groups
        if item.dimension is BaseStrategyGroupDimension.OVERALL
    )
    reproduced = summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL, "OVERALL", available
    )
    if reproduced != baseline:
        raise Ema20VwapComparisonInputError("BASE_ALL does not reproduce Stage 9.3")

    group_specs = (
        (Ema20VwapComparisonGroupName.BASE_ALL, None),
        (
            Ema20VwapComparisonGroupName.EMA20_VWAP_ALIGNED,
            Ema20VwapAlignmentState.EMA20_VWAP_ALIGNED,
        ),
        (
            Ema20VwapComparisonGroupName.EMA20_VWAP_NOT_ALIGNED,
            Ema20VwapAlignmentState.EMA20_VWAP_NOT_ALIGNED,
        ),
        (
            Ema20VwapComparisonGroupName.EMA20_VWAP_UNAVAILABLE,
            Ema20VwapAlignmentState.EMA20_VWAP_UNAVAILABLE,
        ),
    )
    groups = []
    for name, state in group_specs:
        selected_annotations = tuple(
            item for item in annotations if state is None or item.alignment_state is state
        )
        selected = tuple(
            item for item in available
            if state is None or current_by_id[item.setup_identity].alignment_state is state
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, name.value, selected
        )
        groups.append(
            Ema20VwapGroupStatistics(
                name=name,
                annotation_n=len(selected_annotations),
                long_annotation_n=sum(
                    item.direction is SetupDirection.LONG
                    for item in selected_annotations
                ),
                short_annotation_n=sum(
                    item.direction is SetupDirection.SHORT
                    for item in selected_annotations
                ),
                executable_n=len(selected),
                horizons=stats.horizons,
                deltas=tuple(
                    Ema20VwapBaselineDelta(
                        horizon=item.horizon,
                        median_mfe_delta=_delta(item.mfe.median, base.mfe.median),
                        median_mae_delta=_delta(item.mae.median, base.mae.median),
                        median_balance_delta=_delta(
                            item.net_excursion_balance.median,
                            base.net_excursion_balance.median,
                        ),
                    )
                    for item, base in zip(
                        stats.horizons, baseline.horizons, strict=True
                    )
                ),
            )
        )

    direction_groups = []
    for direction in SetupDirection:
        for state in Ema20VwapAlignmentState:
            selected = tuple(
                item
                for item in available
                if item.setup.direction is direction
                and current_by_id[item.setup_identity].alignment_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.DIRECTION,
                f"{direction.value}+{state.value}",
                selected,
            )
            direction_groups.append(
                Ema20VwapDirectionStatistics(
                    direction=direction,
                    alignment_state=state,
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    level_groups = []
    for level in LevelType:
        for state in Ema20VwapAlignmentState:
            selected_annotations = tuple(
                item
                for item in annotations
                if setup_by_id[item.setup_identity].level_type is level
                and item.alignment_state is state
            )
            selected = tuple(
                item
                for item in available
                if item.setup.level_type is level
                and current_by_id[item.setup_identity].alignment_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.LEVEL,
                f"{level.value}+{state.value}",
                selected,
            )
            level_groups.append(
                Ema20VwapLevelStatistics(
                    level_type=level,
                    alignment_state=state,
                    annotation_n=len(selected_annotations),
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    def cross_tab(dimension, source_states, state_getter):
        return tuple(
            Ema20VwapCrossTabCount(
                source_dimension=dimension,
                source_state=source_state.value,
                ema20_vwap_state=current_state,
                annotation_n=sum(
                    state_getter(item.setup_identity) is source_state
                    and item.alignment_state is current_state
                    for item in annotations
                ),
            )
            for source_state in source_states
            for current_state in Ema20VwapAlignmentState
        )

    observed_stacks = sorted({item.stack_state for item in annotations})
    stack_groups = []
    for stack_state in observed_stacks:
        stack_annotations = tuple(item for item in annotations if item.stack_state == stack_state)
        identities = {item.setup_identity for item in stack_annotations}
        selected = tuple(item for item in available if item.setup_identity in identities)
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, stack_state, selected
        )
        stack_groups.append(IndicatorStackStatistics(
            stack_state=stack_state,
            annotation_n=len(stack_annotations),
            executable_n=len(selected),
            long_annotation_n=sum(
                item.direction is SetupDirection.LONG for item in stack_annotations
            ),
            short_annotation_n=sum(
                item.direction is SetupDirection.SHORT for item in stack_annotations
            ),
            eod=stats.horizons[-1],
        ))

    return Ema20VwapAlignmentComparisonResult(
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
        groups=tuple(groups),
        direction_groups=tuple(direction_groups),
        level_groups=tuple(level_groups),
        distance_statistics=tuple(
            _distance_summary(annotations, direction)
            for direction in (None, SetupDirection.LONG, SetupDirection.SHORT)
        ),
        ema9_vwap_cross_tab=cross_tab(
            "EMA9_VWAP",
            Ema9VwapAlignmentState,
            lambda identity: ema9_by_id[identity].alignment_state,
        ),
        ema_alignment_cross_tab=cross_tab(
            "EMA9_EMA20",
            EmaAlignmentState,
            lambda identity: ema_by_id[identity].alignment_state,
        ),
        price_vwap_cross_tab=cross_tab(
            "PRICE_VWAP",
            VwapAlignmentState,
            lambda identity: price_by_id[identity].alignment_state,
        ),
        ema9_vwap_cross_context_cross_tab=cross_tab(
            "EMA9_VWAP_CROSS",
            Ema9VwapCrossContextState,
            lambda identity: cross_by_id[identity].cross_state,
        ),
        stack_groups=tuple(stack_groups),
    )
