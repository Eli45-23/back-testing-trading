"""Pure Stage 10.2 prior-cross annotation and descriptive comparison."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, timedelta
from decimal import Decimal

from spy_research.events import EmaCrossDirection, EmaCrossEvent
from spy_research.research_stats import summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.models import (
    EmaAlignmentAnnotation,
    EmaAlignmentCrossTabCount,
    EmaAlignmentState,
    EmaCrossComparisonGroupName,
    EmaCrossContextAnnotation,
    EmaCrossContextComparisonResult,
    EmaCrossContextGroupStatistics,
    EmaCrossContextState,
    EmaCrossDirectionStatistics,
    EmaCrossRecencyStatistics,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcomeResult,
)


class EmaCrossContextInputError(ValueError):
    """Frozen Stage 4/9 inputs cannot form a trustworthy comparison."""


def ema_cross_identity(event: EmaCrossEvent) -> str:
    """Render the accepted Stage 4 identity tuple without changing the event."""

    return "|".join(
        (
            event.symbol,
            event.timestamp.isoformat(),
            event.direction.value,
            event.event_version,
        )
    )


def select_prior_ema_cross(
    setup: BasePriceActionCandidate,
    same_session_cross_events: Sequence[EmaCrossEvent],
) -> EmaCrossContextAnnotation:
    """Select the latest same-session cross already known at setup signal time."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise EmaCrossContextInputError("Only confirmed Stage 9.1 setups may be annotated")
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise EmaCrossContextInputError("Confirmed setup lacks frozen timing")
    if setup.signal_known_at != setup.confirmation_bar_timestamp + timedelta(minutes=5):
        raise EmaCrossContextInputError("Signal-known time must follow confirmation by 5 minutes")

    previous = None
    seen = set()
    eligible: list[EmaCrossEvent] = []
    for event in same_session_cross_events:
        identity = (event.symbol, event.timestamp, event.direction, event.event_version)
        if identity in seen or (previous is not None and event.timestamp == previous):
            raise EmaCrossContextInputError("Duplicate EMA cross timestamp or identity")
        if previous is not None and event.timestamp < previous:
            raise EmaCrossContextInputError("EMA cross events must be chronological")
        seen.add(identity)
        previous = event.timestamp
        if event.symbol != setup.symbol or event.session_date != setup.session_date:
            raise EmaCrossContextInputError("Selector input must contain only same-session crosses")
        cross_known_at = event.timestamp + timedelta(minutes=5)
        if cross_known_at <= setup.signal_known_at:
            eligible.append(event)

    if not eligible:
        return EmaCrossContextAnnotation(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
            signal_known_at=setup.signal_known_at,
            cross_state=EmaCrossContextState.NO_PRIOR_CROSS,
            most_recent_cross_identity=None,
            cross_direction=None,
            cross_timestamp=None,
            cross_known_at=None,
            bars_since_cross=None,
            minutes_since_cross_completion=None,
        )

    event = eligible[-1]
    cross_known_at = event.timestamp + timedelta(minutes=5)
    interval_seconds = (setup.confirmation_bar_timestamp - event.timestamp).total_seconds()
    if interval_seconds < 0 or interval_seconds % 300:
        raise EmaCrossContextInputError(
            "Cross recency must be a non-negative whole 5-minute interval"
        )
    bars = int(interval_seconds // 300)
    expected = (
        EmaCrossDirection.BULLISH
        if setup.direction is SetupDirection.LONG
        else EmaCrossDirection.BEARISH
    )
    state = (
        EmaCrossContextState.MATCHING_CROSS
        if event.direction is expected
        else EmaCrossContextState.OPPOSING_CROSS
    )
    return EmaCrossContextAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        cross_state=state,
        most_recent_cross_identity=ema_cross_identity(event),
        cross_direction=event.direction,
        cross_timestamp=event.timestamp,
        cross_known_at=cross_known_at,
        bars_since_cross=bars,
        minutes_since_cross_completion=bars * 5,
    )


def annotate_prior_cross_context(
    setup_result: BasePriceActionResult,
    cross_events: Sequence[EmaCrossEvent],
) -> tuple[EmaCrossContextAnnotation, ...]:
    """Annotate every confirmed setup from frozen Stage 4 events only."""

    grouped: dict[date, list[EmaCrossEvent]] = defaultdict(list)
    previous = None
    identities = set()
    timestamps = set()
    for event in cross_events:
        identity = (event.symbol, event.timestamp, event.direction, event.event_version)
        if identity in identities or event.timestamp in timestamps:
            raise EmaCrossContextInputError("Duplicate Stage 4 cross event")
        if previous is not None and event.timestamp <= previous:
            raise EmaCrossContextInputError("Stage 4 cross events must be strictly chronological")
        identities.add(identity)
        timestamps.add(event.timestamp)
        grouped[event.session_date].append(event)
        previous = event.timestamp
    confirmed = tuple(
        item for item in setup_result.candidates if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = tuple(
        select_prior_ema_cross(item, grouped[item.session_date]) for item in confirmed
    )
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise EmaCrossContextInputError("Duplicate cross annotation setup identity")
    return annotations


def calculate_ema_cross_context_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[EmaCrossContextAnnotation],
    alignment_annotations: Sequence[EmaAlignmentAnnotation],
    *,
    stage4_event_count: int,
) -> EmaCrossContextComparisonResult:
    """Describe unchanged Stage 9 outcomes by exact prior-cross context."""

    if not (
        setup_result.start_date == outcome_result.start_date == base_statistics.start_date
        and setup_result.end_date == outcome_result.end_date == base_statistics.end_date
    ):
        raise EmaCrossContextInputError("Frozen source ranges do not match")
    population = (
        setup_result.seed_count,
        setup_result.confirmed_count,
        setup_result.non_confirmed_count,
        outcome_result.available_entry_count,
        outcome_result.session_end_unavailable_count,
        outcome_result.missing_entry_count,
    )
    expected_population = (
        base_statistics.break_seed_count,
        base_statistics.confirmed_count,
        base_statistics.non_confirmed_count,
        base_statistics.executable_count,
        base_statistics.session_end_unavailable_count,
        base_statistics.missing_entry_count,
    )
    if population != expected_population:
        raise EmaCrossContextInputError("Stage 9.3 population does not match sources")
    confirmed = tuple(
        item for item in setup_result.candidates if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_id = {item.setup_identity: item for item in confirmed}
    annotation_by_id = {item.setup_identity: item for item in annotations}
    alignment_by_id = {item.setup_identity: item for item in alignment_annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    identity_maps = (setup_by_id, annotation_by_id, alignment_by_id, outcome_by_id)
    if any(len(mapping) != len(confirmed) for mapping in identity_maps):
        raise EmaCrossContextInputError("Frozen setup identities are duplicate or incomplete")
    if not (
        set(setup_by_id)
        == set(annotation_by_id)
        == set(alignment_by_id)
        == set(outcome_by_id)
    ):
        raise EmaCrossContextInputError("Annotations and outcomes must match confirmed setups")
    for identity, annotation in annotation_by_id.items():
        setup = setup_by_id[identity]
        if (
            annotation.session_date != setup.session_date
            or annotation.direction is not setup.direction
            or annotation.confirmation_bar_timestamp != setup.confirmation_bar_timestamp
            or annotation.signal_known_at != setup.signal_known_at
        ):
            raise EmaCrossContextInputError("Cross annotation does not match frozen setup")

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
        raise EmaCrossContextInputError("BASE_ALL does not reproduce Stage 9.3 exactly")

    group_specs = (
        (EmaCrossComparisonGroupName.BASE_ALL, None),
        (EmaCrossComparisonGroupName.MATCHING_CROSS, EmaCrossContextState.MATCHING_CROSS),
        (EmaCrossComparisonGroupName.OPPOSING_CROSS, EmaCrossContextState.OPPOSING_CROSS),
        (EmaCrossComparisonGroupName.NO_PRIOR_CROSS, EmaCrossContextState.NO_PRIOR_CROSS),
    )
    groups = []
    for name, state in group_specs:
        selected_annotations = tuple(
            item
            for item in annotations
            if state is None or item.cross_state is state
        )
        selected = tuple(
            item
            for item in available
            if state is None
            or annotation_by_id[item.setup_identity].cross_state is state
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, name.value, selected
        )
        groups.append(
            EmaCrossContextGroupStatistics(
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
                long_executable_n=sum(
                    item.setup.direction is SetupDirection.LONG for item in selected
                ),
                short_executable_n=sum(
                    item.setup.direction is SetupDirection.SHORT for item in selected
                ),
                horizons=stats.horizons,
            )
        )

    direction_groups = []
    for direction in SetupDirection:
        for state in EmaCrossContextState:
            selected = tuple(
                item
                for item in available
                if item.setup.direction is direction
                and annotation_by_id[item.setup_identity].cross_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.DIRECTION,
                f"{direction.value}+{state.value}",
                selected,
            )
            direction_groups.append(
                EmaCrossDirectionStatistics(
                    direction=direction,
                    cross_state=state,
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    alignment_cross_tab = tuple(
        EmaAlignmentCrossTabCount(
            alignment_state=alignment,
            cross_state=state,
            annotation_n=sum(
                alignment_by_id[item.setup_identity].alignment_state is alignment
                and item.cross_state is state
                for item in annotations
            ),
        )
        for alignment in EmaAlignmentState
        for state in EmaCrossContextState
    )
    recencies = tuple(
        item.bars_since_cross
        for item in annotations
        if item.bars_since_cross is not None
    )
    observed = tuple(sorted(set(recencies)))
    recency_rows = []
    for bars in observed:
        annotation_n = sum(item.bars_since_cross == bars for item in annotations)
        selected = tuple(
            item
            for item in available
            if annotation_by_id[item.setup_identity].bars_since_cross == bars
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, f"RECENCY_{bars}", selected
        )
        recency_rows.append(
            EmaCrossRecencyStatistics(
                bars_since_cross=bars,
                annotation_n=annotation_n,
                executable_n=len(selected),
                long_executable_n=sum(
                    item.setup.direction is SetupDirection.LONG for item in selected
                ),
                short_executable_n=sum(
                    item.setup.direction is SetupDirection.SHORT for item in selected
                ),
                eod=stats.horizons[-1],
            )
        )
    return EmaCrossContextComparisonResult(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        development_session_count=base_statistics.development_session_count,
        stage4_event_count=stage4_event_count,
        annotations=tuple(annotations),
        groups=tuple(groups),
        direction_groups=tuple(direction_groups),
        alignment_cross_tab=alignment_cross_tab,
        bars_since_cross_distribution=summarize_distribution(
            tuple(Decimal(item) for item in recencies)
        ),
        recency_rows=tuple(recency_rows),
    )
