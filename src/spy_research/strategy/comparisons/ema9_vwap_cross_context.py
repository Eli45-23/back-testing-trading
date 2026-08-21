"""Stage 10.5 setup annotation and descriptive cross-context comparison."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, timedelta
from decimal import Decimal

from spy_research.research_stats import summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.ema9_vwap_cross import (
    Ema9VwapCrossInputError,
)
from spy_research.strategy.comparisons.models import (
    CrossSystemCrossTabCount,
    Ema9VwapAlignmentAnnotation,
    Ema9VwapAlignmentState,
    Ema9VwapCrossContextAnnotation,
    Ema9VwapCrossContextComparisonResult,
    Ema9VwapCrossContextState,
    Ema9VwapCrossDirection,
    Ema9VwapCrossDirectionStatistics,
    Ema9VwapCrossEvent,
    Ema9VwapCrossGroupName,
    Ema9VwapCrossGroupStatistics,
    Ema9VwapCrossRecencyStatistics,
    Ema9VwapCrossSessionSummary,
    Ema9VwapStateCrossTabCount,
    EmaAlignmentAnnotation,
    EmaAlignmentEma9CrossTabCount,
    EmaAlignmentState,
    EmaCrossContextAnnotation,
    EmaCrossContextState,
    PriceVwapEma9CrossTabCount,
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


def select_prior_ema9_vwap_cross(
    setup: BasePriceActionCandidate,
    same_session_events: Sequence[Ema9VwapCrossEvent],
) -> Ema9VwapCrossContextAnnotation:
    """Select the latest same-session event known when the setup became known."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise Ema9VwapCrossInputError("Only confirmed setups may receive cross context")
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise Ema9VwapCrossInputError("Confirmed setup lacks frozen timing")
    previous = None
    seen = set()
    eligible = []
    for event in same_session_events:
        if event.event_identity in seen or (
            previous is not None and event.cross_timestamp <= previous
        ):
            raise Ema9VwapCrossInputError(
                "EMA9/VWAP context events must be unique and chronological"
            )
        if event.symbol != setup.symbol or event.session_date != setup.session_date:
            raise Ema9VwapCrossInputError(
                "Selector input must contain only same-session events"
            )
        seen.add(event.event_identity)
        previous = event.cross_timestamp
        if event.cross_known_at <= setup.signal_known_at:
            eligible.append(event)
    if not eligible:
        return Ema9VwapCrossContextAnnotation(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
            signal_known_at=setup.signal_known_at,
            cross_state=Ema9VwapCrossContextState.NO_PRIOR_EMA9_VWAP_CROSS,
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
        raise Ema9VwapCrossInputError("Cross recency must use whole five-minute bars")
    bars = int(seconds // 300)
    expected = (
        Ema9VwapCrossDirection.BULLISH
        if setup.direction is SetupDirection.LONG
        else Ema9VwapCrossDirection.BEARISH
    )
    state = (
        Ema9VwapCrossContextState.MATCHING_EMA9_VWAP_CROSS
        if event.direction is expected
        else Ema9VwapCrossContextState.OPPOSING_EMA9_VWAP_CROSS
    )
    return Ema9VwapCrossContextAnnotation(
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


def annotate_ema9_vwap_cross_context(
    setup_result: BasePriceActionResult,
    events: Sequence[Ema9VwapCrossEvent],
) -> tuple[Ema9VwapCrossContextAnnotation, ...]:
    grouped: dict[date, list[Ema9VwapCrossEvent]] = defaultdict(list)
    previous = None
    seen = set()
    for event in events:
        if event.event_identity in seen or (
            previous is not None and event.cross_timestamp <= previous
        ):
            raise Ema9VwapCrossInputError("Cross event universe must be unique and ordered")
        grouped[event.session_date].append(event)
        seen.add(event.event_identity)
        previous = event.cross_timestamp
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = tuple(
        select_prior_ema9_vwap_cross(item, grouped[item.session_date])
        for item in confirmed
    )
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise Ema9VwapCrossInputError("Duplicate setup annotation identity")
    return annotations


def calculate_ema9_vwap_cross_context_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    events: Sequence[Ema9VwapCrossEvent],
    event_sessions: Sequence[Ema9VwapCrossSessionSummary],
    annotations: Sequence[Ema9VwapCrossContextAnnotation],
    ema9_vwap_annotations: Sequence[Ema9VwapAlignmentAnnotation],
    price_annotations: Sequence[VwapAlignmentAnnotation],
    ema_annotations: Sequence[EmaAlignmentAnnotation],
    ema_cross_annotations: Sequence[EmaCrossContextAnnotation],
) -> Ema9VwapCrossContextComparisonResult:
    """Compare frozen outcomes by most recent already-known EMA9/VWAP cross."""

    if not (
        setup_result.start_date
        == outcome_result.start_date
        == base_statistics.start_date
        and setup_result.end_date
        == outcome_result.end_date
        == base_statistics.end_date
    ):
        raise Ema9VwapCrossInputError("Frozen source ranges do not match")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_id = {item.setup_identity: item for item in confirmed}
    current_by_id = {item.setup_identity: item for item in annotations}
    ema9_by_id = {item.setup_identity: item for item in ema9_vwap_annotations}
    price_by_id = {item.setup_identity: item for item in price_annotations}
    ema_by_id = {item.setup_identity: item for item in ema_annotations}
    ema_cross_by_id = {item.setup_identity: item for item in ema_cross_annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    maps = (
        setup_by_id,
        current_by_id,
        ema9_by_id,
        price_by_id,
        ema_by_id,
        ema_cross_by_id,
        outcome_by_id,
    )
    if any(len(item) != len(confirmed) for item in maps) or len(
        {frozenset(item) for item in maps}
    ) != 1:
        raise Ema9VwapCrossInputError("Comparison setup identities do not reconcile")
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
        raise Ema9VwapCrossInputError("Stage 9 population mismatch")
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
        raise Ema9VwapCrossInputError("BASE_ALL does not reproduce Stage 9.3")

    specs = (
        (Ema9VwapCrossGroupName.BASE_ALL, None),
        (
            Ema9VwapCrossGroupName.MATCHING_EMA9_VWAP_CROSS,
            Ema9VwapCrossContextState.MATCHING_EMA9_VWAP_CROSS,
        ),
        (
            Ema9VwapCrossGroupName.OPPOSING_EMA9_VWAP_CROSS,
            Ema9VwapCrossContextState.OPPOSING_EMA9_VWAP_CROSS,
        ),
        (
            Ema9VwapCrossGroupName.NO_PRIOR_EMA9_VWAP_CROSS,
            Ema9VwapCrossContextState.NO_PRIOR_EMA9_VWAP_CROSS,
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
            Ema9VwapCrossGroupStatistics(
                name=name,
                annotation_n=len(selected_annotations),
                long_annotation_n=sum(
                    item.direction is SetupDirection.LONG for item in selected_annotations
                ),
                short_annotation_n=sum(
                    item.direction is SetupDirection.SHORT for item in selected_annotations
                ),
                executable_n=len(selected),
                horizons=stats.horizons,
            )
        )

    direction_groups = []
    for direction in SetupDirection:
        for state in Ema9VwapCrossContextState:
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
                Ema9VwapCrossDirectionStatistics(
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
            Ema9VwapCrossRecencyStatistics(
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
        Ema9VwapStateCrossTabCount(
            alignment_state=alignment,
            cross_state=state,
            annotation_n=sum(
                ema9_by_id[item.setup_identity].alignment_state is alignment
                and item.cross_state is state
                for item in annotations
            ),
        )
        for alignment in Ema9VwapAlignmentState
        for state in Ema9VwapCrossContextState
    )
    price_tab = tuple(
        PriceVwapEma9CrossTabCount(
            price_vwap_state=price_state,
            cross_state=state,
            annotation_n=sum(
                price_by_id[item.setup_identity].alignment_state is price_state
                and item.cross_state is state
                for item in annotations
            ),
        )
        for price_state in VwapAlignmentState
        for state in Ema9VwapCrossContextState
    )
    ema_tab = tuple(
        EmaAlignmentEma9CrossTabCount(
            ema_alignment_state=alignment,
            cross_state=state,
            annotation_n=sum(
                ema_by_id[item.setup_identity].alignment_state is alignment
                and item.cross_state is state
                for item in annotations
            ),
        )
        for alignment in EmaAlignmentState
        for state in Ema9VwapCrossContextState
    )
    system_tab = tuple(
        CrossSystemCrossTabCount(
            ema9_20_cross_state=old_state,
            ema9_vwap_cross_state=new_state,
            annotation_n=sum(
                ema_cross_by_id[item.setup_identity].cross_state is old_state
                and item.cross_state is new_state
                for item in annotations
            ),
        )
        for old_state in EmaCrossContextState
        for new_state in Ema9VwapCrossContextState
    )
    return Ema9VwapCrossContextComparisonResult(
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
            item.direction is Ema9VwapCrossDirection.BULLISH for item in events
        ),
        bearish_event_count=sum(
            item.direction is Ema9VwapCrossDirection.BEARISH for item in events
        ),
        annotations=tuple(annotations),
        groups=tuple(groups),
        direction_groups=tuple(direction_groups),
        bars_since_cross_distribution=summarize_distribution(
            tuple(Decimal(item) for item in recencies)
        ),
        recency_rows=tuple(recency_rows),
        ema9_vwap_state_cross_tab=state_tab,
        price_vwap_cross_tab=price_tab,
        ema_alignment_cross_tab=ema_tab,
        cross_system_cross_tab=system_tab,
    )
