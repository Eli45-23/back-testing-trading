"""Stage 11.2 objective room-to-next-level measurements and comparisons."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from hashlib import sha256
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from spy_research.bars import FiveMinuteBar
from spy_research.indicators import FiveMinuteAtrRow
from spy_research.indicators.atr import ATR_CONTEXT
from spy_research.interactions import AvailableLevel, LevelType
from spy_research.research_stats import DistributionSummary, summarize_distribution
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
from spy_research.strategy.comparisons.models import (
    Ema9VwapAlignmentState,
    EmaAlignmentState,
    VwapAlignmentState,
)
from spy_research.strategy.comparisons.regime_hypotheses import (
    CombinedRegimeState,
    RegimeHypothesisComparisonResult,
    RegimeLevelCount,
    RegimeSessionCount,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcome,
    SetupOutcomeResult,
)


HORIZON_ORDER = ("5m", "15m", "30m", "60m", "EOD")
CONTEXT_SPECS = (
    ("REGIME_HYPOTHESIS", "combined_state", CombinedRegimeState),
    ("EMA9_20_ALIGNMENT", "ema9_20_alignment", EmaAlignmentState),
    ("PRICE_VWAP_ALIGNMENT", "price_vwap_alignment", VwapAlignmentState),
    ("EMA9_VWAP_ALIGNMENT", "ema9_vwap_alignment", Ema9VwapAlignmentState),
    ("EMA20_VWAP_ALIGNMENT", "ema20_vwap_alignment", Ema20VwapAlignmentState),
)


class RoomToLevelInputError(ValueError):
    """Frozen setup, level, indicator, and outcome inputs do not reconcile."""


class NextLevelAvailability(StrEnum):
    AVAILABLE = "AVAILABLE"
    OPEN_ENDED = "OPEN_ENDED"


class RoomBucket(StrEnum):
    LT_0_5_ATR = "LT_0_5_ATR"
    ATR_0_5_TO_1_0 = "ATR_0_5_TO_1_0"
    ATR_1_0_TO_1_5 = "ATR_1_0_TO_1_5"
    ATR_1_5_TO_2_0 = "ATR_1_5_TO_2_0"
    ATR_2_0_TO_3_0 = "ATR_2_0_TO_3_0"
    GT_3_0_ATR = "GT_3_0_ATR"
    OPEN_ENDED = "OPEN_ENDED"
    UNAVAILABLE_ATR = "UNAVAILABLE_ATR"


class RoomToLevelAnnotation(BaseModel):
    """One immutable confirmation-time room measurement."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    setup_identity: str
    symbol: Literal["SPY"] = "SPY"
    session_date: date
    direction: SetupDirection
    triggering_level_type: LevelType
    triggering_level_price: Decimal
    confirmation_bar_timestamp: datetime
    signal_known_at: datetime
    reference_confirmation_price: Decimal
    reference_entry_price: Decimal | None
    next_level_price: Decimal | None
    next_level_types: tuple[LevelType, ...]
    next_level_availability: NextLevelAvailability
    room_from_confirmation: Decimal | None = Field(default=None, ge=0)
    room_from_entry_reference: Decimal | None
    atr14: Decimal | None = Field(default=None, ge=0)
    room_in_atr: Decimal | None = Field(default=None, ge=0)
    room_bucket: RoomBucket
    number_of_known_levels_above: int = Field(ge=0)
    number_of_known_levels_below: int = Field(ge=0)
    nearest_level_distance_above: Decimal | None = Field(default=None, ge=0)
    nearest_level_distance_below: Decimal | None = Field(default=None, ge=0)
    directional_level_count_within_0_5_atr: int | None = Field(default=None, ge=0)
    directional_level_count_within_1_0_atr: int | None = Field(default=None, ge=0)
    known_level_count: int = Field(ge=0)
    measurement_version: Literal["objective-room-to-level-v1"] = (
        "objective-room-to-level-v1"
    )

    @model_validator(mode="after")
    def reconcile_room(self) -> Self:
        available = self.next_level_availability is NextLevelAvailability.AVAILABLE
        if available != (self.next_level_price is not None):
            raise ValueError("next-level availability and price mismatch")
        if available != bool(self.next_level_types):
            raise ValueError("available next level requires tied level types")
        if available != (self.room_from_confirmation is not None):
            raise ValueError("available next level requires confirmation room")
        if self.reference_entry_price is None or not available:
            if self.room_from_entry_reference is not None:
                raise ValueError("entry room requires entry and next-level prices")
        if self.room_in_atr is None:
            expected_special = (
                RoomBucket.OPEN_ENDED
                if not available
                else RoomBucket.UNAVAILABLE_ATR
            )
            if self.room_bucket is not expected_special:
                raise ValueError("missing ATR room requires a special bucket")
        elif self.room_bucket in (
            RoomBucket.OPEN_ENDED,
            RoomBucket.UNAVAILABLE_ATR,
        ):
            raise ValueError("available normalized room requires a numeric bucket")
        stacked = (
            self.directional_level_count_within_0_5_atr,
            self.directional_level_count_within_1_0_atr,
        )
        if self.atr14 is None:
            if any(item is not None for item in stacked):
                raise ValueError("stacked counts require confirmation-time ATR")
        elif any(item is None for item in stacked):
            raise ValueError("available ATR requires stacked counts")
        if tuple(self.next_level_types) != tuple(
            level for level in LevelType if level in set(self.next_level_types)
        ):
            raise ValueError("tied level types must use deterministic ordering")
        return self


class RoomDistributionRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: Literal[
        "ROOM_FROM_CONFIRMATION",
        "ROOM_FROM_ENTRY_REFERENCE",
        "ROOM_IN_ATR",
    ]
    direction: Literal["ALL", "LONG", "SHORT"]
    distribution: DistributionSummary
    open_ended_n: int = Field(ge=0)
    unavailable_n: int = Field(ge=0)
    population_n: int = Field(ge=0)

    @model_validator(mode="after")
    def reconcile_population(self) -> Self:
        if (
            self.distribution.n + self.open_ended_n + self.unavailable_n
            != self.population_n
        ):
            raise ValueError("room distribution population mismatch")
        return self


class RoomBucketStatistics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    bucket: RoomBucket
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    long_annotation_n: int = Field(ge=0)
    short_annotation_n: int = Field(ge=0)
    session_count: int = Field(ge=0)
    session_composition: tuple[RegimeSessionCount, ...]
    level_composition: tuple[RegimeLevelCount, ...]
    horizons: tuple[BaseStrategyHorizonStatistics, ...]

    @model_validator(mode="after")
    def reconcile_group(self) -> Self:
        if self.long_annotation_n + self.short_annotation_n != self.annotation_n:
            raise ValueError("room-bucket directions must reconcile")
        if sum(item.annotation_n for item in self.session_composition) != self.annotation_n:
            raise ValueError("room-bucket sessions must reconcile")
        if sum(item.annotation_n for item in self.level_composition) != self.annotation_n:
            raise ValueError("room-bucket levels must reconcile")
        if self.session_count != len(self.session_composition):
            raise ValueError("room-bucket session count mismatch")
        if tuple(item.horizon for item in self.horizons) != HORIZON_ORDER:
            raise ValueError("room-bucket horizons must use frozen ordering")
        return self


class LevelTransitionCount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    triggering_level_type: LevelType
    next_level_availability: NextLevelAvailability
    next_level_types: tuple[LevelType, ...]
    count: int = Field(ge=0)


class RoomContextCrossTab(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    bucket: RoomBucket
    dimension: str
    state: str
    annotation_n: int = Field(ge=0)
    executable_n: int = Field(ge=0)
    eod: BaseStrategyHorizonStatistics

    @model_validator(mode="after")
    def eod_only(self) -> Self:
        if self.eod.horizon != "EOD":
            raise ValueError("room cross-tabs report EOD only")
        return self


class RoomToLevelComparisonResult(BaseModel):
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
    source_stage11_1_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    annotations: tuple[RoomToLevelAnnotation, ...]
    distributions: tuple[RoomDistributionRow, ...]
    bucket_statistics: tuple[RoomBucketStatistics, ...]
    transitions: tuple[LevelTransitionCount, ...]
    cross_tabs: tuple[RoomContextCrossTab, ...]
    base_all_horizons: tuple[BaseStrategyHorizonStatistics, ...]
    report_version: Literal["objective-room-comparison-v1"] = (
        "objective-room-comparison-v1"
    )
    sample_warning: str = (
        "Thirteen-session development sample; room buckets are descriptive, not filters."
    )

    @model_validator(mode="after")
    def reconcile_result(self) -> Self:
        if len(self.annotations) != self.confirmed_count:
            raise ValueError("every confirmed setup requires one room annotation")
        if len({item.setup_identity for item in self.annotations}) != len(
            self.annotations
        ):
            raise ValueError("room annotations require unique setup identities")
        expected_distributions = tuple(
            (metric, direction)
            for metric in (
                "ROOM_FROM_CONFIRMATION",
                "ROOM_FROM_ENTRY_REFERENCE",
                "ROOM_IN_ATR",
            )
            for direction in ("ALL", "LONG", "SHORT")
        )
        if tuple(
            (item.metric, item.direction) for item in self.distributions
        ) != expected_distributions:
            raise ValueError("room distributions must use frozen ordering")
        if tuple(item.bucket for item in self.bucket_statistics) != tuple(RoomBucket):
            raise ValueError("room buckets must use frozen ordering")
        if sum(item.annotation_n for item in self.bucket_statistics) != self.confirmed_count:
            raise ValueError("room buckets must partition annotations")
        if sum(item.executable_n for item in self.bucket_statistics) != self.executable_count:
            raise ValueError("room buckets must partition outcomes")
        if sum(item.count for item in self.transitions) != self.confirmed_count:
            raise ValueError("level transitions must partition annotations")
        expected_tabs = tuple(
            (bucket, dimension, state.value)
            for bucket in RoomBucket
            for dimension, _field, states in CONTEXT_SPECS
            for state in states
        )
        if tuple(
            (item.bucket, item.dimension, item.state) for item in self.cross_tabs
        ) != expected_tabs:
            raise ValueError("room cross-tabs must use frozen ordering")
        bucket_by_name = {item.bucket: item for item in self.bucket_statistics}
        for bucket in RoomBucket:
            for dimension, _field, _states in CONTEXT_SPECS:
                partition = tuple(
                    item
                    for item in self.cross_tabs
                    if item.bucket is bucket and item.dimension == dimension
                )
                if sum(item.annotation_n for item in partition) != bucket_by_name[
                    bucket
                ].annotation_n:
                    raise ValueError("room cross-tab annotations must reconcile")
                if sum(item.executable_n for item in partition) != bucket_by_name[
                    bucket
                ].executable_n:
                    raise ValueError("room cross-tab outcomes must reconcile")
        if tuple(item.horizon for item in self.base_all_horizons) != HORIZON_ORDER:
            raise ValueError("BASE_ALL horizons must use frozen ordering")
        return self


def room_bucket(
    room_in_atr: Decimal | None,
    availability: NextLevelAvailability,
) -> RoomBucket:
    """Apply the fixed half-open buckets; 3.0 belongs to the 2.0-3.0 bucket."""

    if availability is NextLevelAvailability.OPEN_ENDED:
        return RoomBucket.OPEN_ENDED
    if room_in_atr is None:
        return RoomBucket.UNAVAILABLE_ATR
    if room_in_atr < Decimal("0.5"):
        return RoomBucket.LT_0_5_ATR
    if room_in_atr < Decimal("1.0"):
        return RoomBucket.ATR_0_5_TO_1_0
    if room_in_atr < Decimal("1.5"):
        return RoomBucket.ATR_1_0_TO_1_5
    if room_in_atr < Decimal("2.0"):
        return RoomBucket.ATR_1_5_TO_2_0
    if room_in_atr <= Decimal("3.0"):
        return RoomBucket.ATR_2_0_TO_3_0
    return RoomBucket.GT_3_0_ATR


def select_room_to_next_level(
    setup: BasePriceActionCandidate,
    *,
    confirmation_price: Decimal,
    entry_price: Decimal | None,
    atr14: Decimal | None,
    levels: Sequence[AvailableLevel],
) -> RoomToLevelAnnotation:
    """Select from levels known at signal time before considering entry price."""

    if setup.status is not BaseSetupStatus.CONFIRMED or setup.signal_known_at is None:
        raise RoomToLevelInputError("Room measurement requires a confirmed setup")
    known = tuple(
        item
        for item in levels
        if item.session_date == setup.session_date
        and item.available_from_timestamp <= setup.signal_known_at
    )
    above = tuple(item for item in known if item.level_price > confirmation_price)
    below = tuple(item for item in known if item.level_price < confirmation_price)
    directional = above if setup.direction is SetupDirection.LONG else below
    directional = tuple(
        item
        for item in directional
        if item.level_type is not setup.level_type
        and item.level_price != setup.level_price
    )
    effective_atr = atr14 if atr14 is not None and atr14 > 0 else None
    if directional:
        next_price = (
            min(item.level_price for item in directional)
            if setup.direction is SetupDirection.LONG
            else max(item.level_price for item in directional)
        )
        next_types = tuple(
            level
            for level in LevelType
            if any(
                item.level_type is level and item.level_price == next_price
                for item in directional
            )
        )
        availability = NextLevelAvailability.AVAILABLE
        with localcontext(ATR_CONTEXT):
            confirmation_room = (
                next_price - confirmation_price
                if setup.direction is SetupDirection.LONG
                else confirmation_price - next_price
            )
            entry_room = (
                (
                    next_price - entry_price
                    if setup.direction is SetupDirection.LONG
                    else entry_price - next_price
                )
                if entry_price is not None
                else None
            )
            normalized = (
                confirmation_room / effective_atr
                if effective_atr is not None
                else None
            )
    else:
        next_price = None
        next_types = ()
        availability = NextLevelAvailability.OPEN_ENDED
        confirmation_room = None
        entry_room = None
        normalized = None
    with localcontext(ATR_CONTEXT):
        above_distance = (
            min(item.level_price for item in above) - confirmation_price
            if above
            else None
        )
        below_distance = (
            confirmation_price - max(item.level_price for item in below)
            if below
            else None
        )
        if effective_atr is not None:
            directional_distances = tuple(
                (
                    item.level_price - confirmation_price
                    if setup.direction is SetupDirection.LONG
                    else confirmation_price - item.level_price
                )
                for item in directional
            )
            within_half = sum(
                distance <= Decimal("0.5") * effective_atr
                for distance in directional_distances
            )
            within_one = sum(
                distance <= effective_atr for distance in directional_distances
            )
        else:
            within_half = None
            within_one = None
    return RoomToLevelAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        triggering_level_type=setup.level_type,
        triggering_level_price=setup.level_price,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        reference_confirmation_price=confirmation_price,
        reference_entry_price=entry_price,
        next_level_price=next_price,
        next_level_types=next_types,
        next_level_availability=availability,
        room_from_confirmation=confirmation_room,
        room_from_entry_reference=entry_room,
        atr14=effective_atr,
        room_in_atr=normalized,
        room_bucket=room_bucket(normalized, availability),
        number_of_known_levels_above=len(above),
        number_of_known_levels_below=len(below),
        nearest_level_distance_above=above_distance,
        nearest_level_distance_below=below_distance,
        directional_level_count_within_0_5_atr=within_half,
        directional_level_count_within_1_0_atr=within_one,
        known_level_count=len(known),
    )


def build_room_annotations(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    bars: Sequence[FiveMinuteBar],
    atr_rows: Sequence[FiveMinuteAtrRow],
    levels_by_session: dict[date, tuple[AvailableLevel, ...]],
) -> tuple[RoomToLevelAnnotation, ...]:
    bar_by_key = {(item.session_date, item.timestamp): item for item in bars}
    atr_by_key = {(item.session_date, item.timestamp): item for item in atr_rows}
    if len(bar_by_key) != len(bars) or len(atr_by_key) != len(atr_rows):
        raise RoomToLevelInputError("Duplicate bar or ATR timestamp")
    if frozenset(bar_by_key) != frozenset(atr_by_key):
        raise RoomToLevelInputError("Bar and ATR timestamp universes differ")
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    if {item.setup_identity for item in confirmed} != set(outcome_by_id):
        raise RoomToLevelInputError("Setup and outcome identities differ")
    annotations = []
    for setup in confirmed:
        key = (setup.session_date, setup.confirmation_bar_timestamp)
        if key not in bar_by_key:
            raise RoomToLevelInputError("Confirmation candle is unavailable")
        outcome = outcome_by_id[setup.setup_identity]
        entry = outcome.entry_reference.entry_reference_price
        annotations.append(
            select_room_to_next_level(
                setup,
                confirmation_price=bar_by_key[key].close,
                entry_price=entry,
                atr14=atr_by_key[key].atr14,
                levels=levels_by_session.get(setup.session_date, ()),
            )
        )
    return tuple(annotations)


def _distribution_rows(
    annotations: Sequence[RoomToLevelAnnotation],
) -> tuple[RoomDistributionRow, ...]:
    specs = (
        ("ROOM_FROM_CONFIRMATION", "room_from_confirmation"),
        ("ROOM_FROM_ENTRY_REFERENCE", "room_from_entry_reference"),
        ("ROOM_IN_ATR", "room_in_atr"),
    )
    rows = []
    for metric, field in specs:
        for direction in ("ALL", "LONG", "SHORT"):
            population = tuple(
                item
                for item in annotations
                if direction == "ALL" or item.direction.value == direction
            )
            values = tuple(
                getattr(item, field)
                for item in population
                if getattr(item, field) is not None
            )
            open_n = sum(
                item.next_level_availability is NextLevelAvailability.OPEN_ENDED
                for item in population
            )
            rows.append(
                RoomDistributionRow(
                    metric=metric,
                    direction=direction,
                    distribution=summarize_distribution(values),
                    open_ended_n=open_n,
                    unavailable_n=len(population) - len(values) - open_n,
                    population_n=len(population),
                )
            )
    return tuple(rows)


def _room_group(
    bucket: RoomBucket,
    annotations: Sequence[RoomToLevelAnnotation],
    available_outcomes: Sequence[SetupOutcome],
) -> RoomBucketStatistics:
    selected = tuple(item for item in annotations if item.room_bucket is bucket)
    identities = {item.setup_identity for item in selected}
    outcomes = tuple(
        item for item in available_outcomes if item.setup_identity in identities
    )
    session_counts = Counter(item.session_date for item in selected)
    level_counts = Counter(item.triggering_level_type for item in selected)
    stats = summarize_base_outcome_group(
        BaseStrategyGroupDimension.OVERALL,
        bucket.value,
        outcomes,
    )
    return RoomBucketStatistics(
        bucket=bucket,
        annotation_n=len(selected),
        executable_n=len(outcomes),
        long_annotation_n=sum(
            item.direction is SetupDirection.LONG for item in selected
        ),
        short_annotation_n=sum(
            item.direction is SetupDirection.SHORT for item in selected
        ),
        session_count=len(session_counts),
        session_composition=tuple(
            RegimeSessionCount(session_date=session, annotation_n=count)
            for session, count in sorted(session_counts.items())
        ),
        level_composition=tuple(
            RegimeLevelCount(level_type=level, annotation_n=level_counts[level])
            for level in LevelType
            if level_counts[level]
        ),
        horizons=stats.horizons,
    )


def calculate_room_to_level_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    context_result: CombinedContextMatrixResult,
    regime_result: RegimeHypothesisComparisonResult,
    annotations: Sequence[RoomToLevelAnnotation],
) -> RoomToLevelComparisonResult:
    """Attach unchanged outcomes and accepted context after room selection."""

    ranges = {
        (item.start_date, item.end_date)
        for item in (
            setup_result,
            outcome_result,
            base_statistics,
            context_result,
            regime_result,
        )
    }
    if len(ranges) != 1:
        raise RoomToLevelInputError("Frozen source ranges differ")
    annotation_by_id = {item.setup_identity: item for item in annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    context_by_id = {item.setup_identity: item for item in context_result.annotations}
    regime_by_id = {item.setup_identity: item for item in regime_result.annotations}
    ids = set(annotation_by_id)
    if (
        len(ids) != len(annotations)
        or ids != set(outcome_by_id)
        or ids != set(context_by_id)
        or ids != set(regime_by_id)
    ):
        raise RoomToLevelInputError("Room/source identities do not reconcile")
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
        raise RoomToLevelInputError("BASE_ALL does not reproduce Stage 9.3")
    bucket_rows = tuple(
        _room_group(bucket, annotations, available) for bucket in RoomBucket
    )
    transitions_counter = Counter(
        (
            item.triggering_level_type,
            item.next_level_availability,
            item.next_level_types,
        )
        for item in annotations
    )
    transitions = tuple(
        LevelTransitionCount(
            triggering_level_type=trigger,
            next_level_availability=availability,
            next_level_types=types,
            count=count,
        )
        for (trigger, availability, types), count in sorted(
            transitions_counter.items(),
            key=lambda row: (
                tuple(LevelType).index(row[0][0]),
                row[0][1].value,
                tuple(item.value for item in row[0][2]),
            ),
        )
    )
    tabs = []
    for bucket in RoomBucket:
        bucket_ids = {
            item.setup_identity for item in annotations if item.room_bucket is bucket
        }
        for dimension, field, states in CONTEXT_SPECS:
            source = regime_by_id if dimension == "REGIME_HYPOTHESIS" else context_by_id
            for state in states:
                selected_ids = {
                    identity
                    for identity in bucket_ids
                    if getattr(source[identity], field) is state
                }
                selected_outcomes = tuple(
                    item for item in available if item.setup_identity in selected_ids
                )
                stats = summarize_base_outcome_group(
                    BaseStrategyGroupDimension.OVERALL,
                    f"{bucket.value}:{dimension}:{state.value}",
                    selected_outcomes,
                )
                tabs.append(
                    RoomContextCrossTab(
                        bucket=bucket,
                        dimension=dimension,
                        state=state.value,
                        annotation_n=len(selected_ids),
                        executable_n=len(selected_outcomes),
                        eod=stats.horizons[-1],
                    )
                )
    return RoomToLevelComparisonResult(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        development_session_count=base_statistics.development_session_count,
        source_stage11_1_hash=sha256(
            regime_result.model_dump_json().encode()
        ).hexdigest(),
        annotations=tuple(annotations),
        distributions=_distribution_rows(annotations),
        bucket_statistics=bucket_rows,
        transitions=transitions,
        cross_tabs=tuple(tabs),
        base_all_horizons=baseline.horizons,
    )
