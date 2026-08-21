"""Stage 10.7 setup annotation and EMA20/VWAP cross-context comparison."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from spy_research.research_stats import summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.ema20_vwap_alignment import (
    Ema20VwapAlignmentAnnotation,
    Ema20VwapAlignmentState,
)
from spy_research.strategy.comparisons.ema20_vwap_cross import (
    Ema20VwapCrossInputError,
)
from spy_research.strategy.comparisons.ema20_vwap_cross_models import (
    Ema9Ema20VwapCrossTabCount,
    Ema20VwapCrossContextAnnotation,
    Ema20VwapCrossContextComparisonResult,
    Ema20VwapCrossContextState,
    Ema20VwapCrossDirection,
    Ema20VwapCrossDirectionStatistics,
    Ema20VwapCrossEvent,
    Ema20VwapCrossGroupName,
    Ema20VwapCrossGroupStatistics,
    Ema20VwapCrossRecencyStatistics,
    Ema20VwapCrossSessionSummary,
    Ema20VwapStateCrossTabCount,
)
from spy_research.strategy.comparisons.models import (
    Ema9VwapCrossContextAnnotation,
    Ema9VwapCrossContextState,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcomeResult,
)


def select_prior_ema20_vwap_cross(
    setup: BasePriceActionCandidate,
    same_session_events: Sequence[Ema20VwapCrossEvent],
) -> Ema20VwapCrossContextAnnotation:
    """Select the latest same-session event already known with the setup."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise Ema20VwapCrossInputError("Only confirmed setups may receive context")
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise Ema20VwapCrossInputError("Confirmed setup lacks frozen timing")
    previous = None
    seen = set()
    eligible = []
    for event in same_session_events:
        if event.event_identity in seen or (
            previous is not None and event.cross_timestamp <= previous
        ):
            raise Ema20VwapCrossInputError(
                "EMA20/VWAP context events must be unique and chronological"
            )
        if event.symbol != setup.symbol or event.session_date != setup.session_date:
            raise Ema20VwapCrossInputError(
                "Selector input must contain only same-session events"
            )
        seen.add(event.event_identity)
        previous = event.cross_timestamp
        if event.cross_known_at <= setup.signal_known_at:
            eligible.append(event)
    if not eligible:
        return Ema20VwapCrossContextAnnotation(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
            signal_known_at=setup.signal_known_at,
            cross_state=Ema20VwapCrossContextState.NO_PRIOR_EMA20_VWAP_CROSS,
            most_recent_cross_identity=None,
            cross_direction=None,
            cross_timestamp=None,
            cross_known_at=None,
            bars_since_cross=None,
            minutes_since_cross_completion=None,
        )
    event = eligible[-1]
    seconds = (setup.confirmation_bar_timestamp - event.cross_timestamp).total_seconds()
    if seconds < 0 or seconds % 300:
        raise Ema20VwapCrossInputError("Cross recency requires whole five-minute bars")
    bars = int(seconds // 300)
    expected = (
        Ema20VwapCrossDirection.BULLISH
        if setup.direction is SetupDirection.LONG
        else Ema20VwapCrossDirection.BEARISH
    )
    state = (
        Ema20VwapCrossContextState.MATCHING_EMA20_VWAP_CROSS
        if event.direction is expected
        else Ema20VwapCrossContextState.OPPOSING_EMA20_VWAP_CROSS
    )
    return Ema20VwapCrossContextAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        cross_state=state,
        most_recent_cross_identity=event.event_identity,
        cross_direction=event.direction,
        cross_timestamp=event.cross_timestamp,
        cross_known_at=event.cross_known_at,
        bars_since_cross=bars,
        minutes_since_cross_completion=bars * 5,
    )


def annotate_ema20_vwap_cross_context(
    setup_result: BasePriceActionResult,
    events: Sequence[Ema20VwapCrossEvent],
) -> tuple[Ema20VwapCrossContextAnnotation, ...]:
    grouped: dict[date, list[Ema20VwapCrossEvent]] = defaultdict(list)
    previous = None
    seen = set()
    for event in events:
        if event.event_identity in seen or (
            previous is not None and event.cross_timestamp <= previous
        ):
            raise Ema20VwapCrossInputError("Event universe must be unique and ordered")
        grouped[event.session_date].append(event)
        seen.add(event.event_identity)
        previous = event.cross_timestamp
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = tuple(
        select_prior_ema20_vwap_cross(item, grouped[item.session_date])
        for item in confirmed
    )
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise Ema20VwapCrossInputError("Duplicate setup annotation identity")
    return annotations


def calculate_ema20_vwap_cross_context_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    events: Sequence[Ema20VwapCrossEvent],
    event_sessions: Sequence[Ema20VwapCrossSessionSummary],
    annotations: Sequence[Ema20VwapCrossContextAnnotation],
    alignment_annotations: Sequence[Ema20VwapAlignmentAnnotation],
    ema9_cross_annotations: Sequence[Ema9VwapCrossContextAnnotation],
) -> Ema20VwapCrossContextComparisonResult:
    """Compare unchanged Stage 9 outcomes by latest known EMA20/VWAP cross."""

    if not (
        setup_result.start_date == outcome_result.start_date == base_statistics.start_date
        and setup_result.end_date == outcome_result.end_date == base_statistics.end_date
    ):
        raise Ema20VwapCrossInputError("Frozen source ranges do not match")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_id = {item.setup_identity: item for item in confirmed}
    current_by_id = {item.setup_identity: item for item in annotations}
    alignment_by_id = {item.setup_identity: item for item in alignment_annotations}
    ema9_by_id = {item.setup_identity: item for item in ema9_cross_annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    maps = (setup_by_id, current_by_id, alignment_by_id, ema9_by_id, outcome_by_id)
    if any(len(item) != len(confirmed) for item in maps) or len(
        {frozenset(item) for item in maps}
    ) != 1:
        raise Ema20VwapCrossInputError("Comparison identities do not reconcile")
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
        raise Ema20VwapCrossInputError("Stage 9 population mismatch")
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
        raise Ema20VwapCrossInputError("BASE_ALL does not reproduce Stage 9.3")

    specs = (
        (Ema20VwapCrossGroupName.BASE_ALL, None),
        (
            Ema20VwapCrossGroupName.MATCHING_EMA20_VWAP_CROSS,
            Ema20VwapCrossContextState.MATCHING_EMA20_VWAP_CROSS,
        ),
        (
            Ema20VwapCrossGroupName.OPPOSING_EMA20_VWAP_CROSS,
            Ema20VwapCrossContextState.OPPOSING_EMA20_VWAP_CROSS,
        ),
        (
            Ema20VwapCrossGroupName.NO_PRIOR_EMA20_VWAP_CROSS,
            Ema20VwapCrossContextState.NO_PRIOR_EMA20_VWAP_CROSS,
        ),
    )
    groups = []
    for name, state in specs:
        selected_annotations = tuple(
            item for item in annotations if state is None or item.cross_state is state
        )
        selected = tuple(
            item
            for item in available
            if state is None or current_by_id[item.setup_identity].cross_state is state
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, name.value, selected
        )
        groups.append(
            Ema20VwapCrossGroupStatistics(
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
            )
        )

    direction_groups = []
    for direction in SetupDirection:
        for state in Ema20VwapCrossContextState:
            selected = tuple(
                item
                for item in available
                if item.setup.direction is direction
                and current_by_id[item.setup_identity].cross_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.DIRECTION,
                f"{direction.value}+{state.value}",
                selected,
            )
            direction_groups.append(
                Ema20VwapCrossDirectionStatistics(
                    direction=direction,
                    cross_state=state,
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    recencies = tuple(
        item.bars_since_cross
        for item in annotations
        if item.bars_since_cross is not None
    )
    recency_rows = []
    for bars in sorted(set(recencies)):
        selected_annotations = tuple(
            item for item in annotations if item.bars_since_cross == bars
        )
        selected = tuple(
            item
            for item in available
            if current_by_id[item.setup_identity].bars_since_cross == bars
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, f"RECENCY_{bars}", selected
        )
        recency_rows.append(
            Ema20VwapCrossRecencyStatistics(
                bars_since_cross=bars,
                annotation_n=len(selected_annotations),
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

    state_tab = tuple(
        Ema20VwapStateCrossTabCount(
            alignment_state=alignment,
            cross_state=state,
            annotation_n=sum(
                alignment_by_id[item.setup_identity].alignment_state is alignment
                and item.cross_state is state
                for item in annotations
            ),
        )
        for alignment in Ema20VwapAlignmentState
        for state in Ema20VwapCrossContextState
    )
    system_tab = tuple(
        Ema9Ema20VwapCrossTabCount(
            ema9_vwap_cross_state=ema9_state,
            ema20_vwap_cross_state=ema20_state,
            annotation_n=sum(
                ema9_by_id[item.setup_identity].cross_state is ema9_state
                and item.cross_state is ema20_state
                for item in annotations
            ),
        )
        for ema9_state in Ema9VwapCrossContextState
        for ema20_state in Ema20VwapCrossContextState
    )
    return Ema20VwapCrossContextComparisonResult(
        start_date=setup_result.start_date,
        end_date=setup_result.end_date,
        break_seed_count=setup_result.seed_count,
        confirmed_count=setup_result.confirmed_count,
        non_confirmed_count=setup_result.non_confirmed_count,
        executable_count=outcome_result.available_entry_count,
        session_end_unavailable_count=outcome_result.session_end_unavailable_count,
        missing_entry_count=outcome_result.missing_entry_count,
        development_session_count=base_statistics.development_session_count,
        events=tuple(events),
        event_sessions=tuple(event_sessions),
        bullish_event_count=sum(
            item.direction is Ema20VwapCrossDirection.BULLISH for item in events
        ),
        bearish_event_count=sum(
            item.direction is Ema20VwapCrossDirection.BEARISH for item in events
        ),
        annotations=tuple(annotations),
        groups=tuple(groups),
        direction_groups=tuple(direction_groups),
        bars_since_cross_distribution=summarize_distribution(
            tuple(Decimal(item) for item in recencies)
        ),
        recency_rows=tuple(recency_rows),
        ema20_vwap_state_cross_tab=state_tab,
        ema9_ema20_vwap_cross_tab=system_tab,
    )
