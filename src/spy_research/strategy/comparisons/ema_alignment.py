"""Pure Stage 10.1 EMA annotation and controlled outcome comparison."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal

from spy_research.indicators import FiveMinuteIndicatorRow
from spy_research.interactions import LevelType
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.models import (
    EmaAlignmentAnnotation,
    EmaAlignmentComparisonResult,
    EmaAlignmentGroupStatistics,
    EmaAlignmentState,
    EmaBaselineDelta,
    EmaComparisonGroupName,
    EmaDirectionGroupStatistics,
    EmaLevelAlignmentStatistics,
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


class EmaComparisonInputError(ValueError):
    """Frozen Stage 3/9 inputs cannot form a trustworthy comparison."""


def annotate_ema_alignment(
    setup: BasePriceActionCandidate,
    indicator_row: FiveMinuteIndicatorRow | None,
) -> EmaAlignmentAnnotation:
    """Label one confirmed setup from only its exact confirmation-bar EMA row."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise EmaComparisonInputError(
            "Only confirmed Stage 9.1 setups may be annotated"
        )
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise EmaComparisonInputError(
            "Confirmed setup lacks frozen confirmation timing"
        )
    if setup.signal_known_at != setup.confirmation_bar_timestamp + timedelta(minutes=5):
        raise EmaComparisonInputError(
            "Signal-known time must follow confirmation by 5 minutes"
        )

    if indicator_row is None:
        return EmaAlignmentAnnotation(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
            signal_known_at=setup.signal_known_at,
            ema9=None,
            ema20=None,
            alignment_state=EmaAlignmentState.EMA_UNAVAILABLE,
            indicator_timestamp=None,
            indicator_available=False,
        )
    if (
        indicator_row.symbol != setup.symbol
        or indicator_row.session_date != setup.session_date
        or indicator_row.timestamp != setup.confirmation_bar_timestamp
        or indicator_row.timeframe != "5Min"
        or indicator_row.session_mode != "RTH_ONLY"
    ):
        raise EmaComparisonInputError(
            "EMA row must match the setup confirmation timestamp and RTH provenance"
        )
    ema9, ema20 = indicator_row.ema9, indicator_row.ema20
    if ema9 is None or ema20 is None:
        state = EmaAlignmentState.EMA_UNAVAILABLE
    elif setup.direction is SetupDirection.LONG and ema9 > ema20:
        state = EmaAlignmentState.EMA_ALIGNED
    elif setup.direction is SetupDirection.SHORT and ema9 < ema20:
        state = EmaAlignmentState.EMA_ALIGNED
    else:
        state = EmaAlignmentState.EMA_NOT_ALIGNED
    return EmaAlignmentAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        ema9=ema9,
        ema20=ema20,
        alignment_state=state,
        indicator_timestamp=indicator_row.timestamp,
        indicator_available=ema9 is not None and ema20 is not None,
    )


def annotate_confirmed_setups(
    setup_result: BasePriceActionResult,
    indicator_rows: Sequence[FiveMinuteIndicatorRow],
) -> tuple[EmaAlignmentAnnotation, ...]:
    """Annotate every confirmed setup by exact timestamp lookup only."""

    previous = None
    rows_by_key = {}
    for row in indicator_rows:
        key = (row.session_date, row.timestamp)
        if key in rows_by_key:
            raise EmaComparisonInputError("Duplicate EMA indicator timestamp")
        if previous is not None and row.timestamp <= previous:
            raise EmaComparisonInputError("EMA rows must be strictly chronological")
        rows_by_key[key] = row
        previous = row.timestamp
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = tuple(
        annotate_ema_alignment(
            item,
            rows_by_key.get((item.session_date, item.confirmation_bar_timestamp)),
        )
        for item in confirmed
    )
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise EmaComparisonInputError("Duplicate EMA annotation setup identity")
    return annotations


def _delta(left: Decimal | None, right: Decimal | None) -> Decimal | None:
    return left - right if left is not None and right is not None else None


def _group_deltas(group, baseline) -> tuple[EmaBaselineDelta, ...]:
    return tuple(
        EmaBaselineDelta(
            horizon=item.horizon,
            median_mfe_delta=_delta(item.mfe.median, base.mfe.median),
            median_mae_delta=_delta(item.mae.median, base.mae.median),
            median_balance_delta=_delta(
                item.net_excursion_balance.median,
                base.net_excursion_balance.median,
            ),
        )
        for item, base in zip(group.horizons, baseline.horizons, strict=True)
    )


def calculate_ema_alignment_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[EmaAlignmentAnnotation],
) -> EmaAlignmentComparisonResult:
    """Compare unchanged Stage 9 outcomes after attaching immutable EMA labels."""

    if not (
        setup_result.start_date
        == outcome_result.start_date
        == base_statistics.start_date
        and setup_result.end_date
        == outcome_result.end_date
        == base_statistics.end_date
    ):
        raise EmaComparisonInputError("Stage 9 source ranges do not match")
    if (
        base_statistics.break_seed_count != setup_result.seed_count
        or base_statistics.confirmed_count != setup_result.confirmed_count
        or base_statistics.non_confirmed_count != setup_result.non_confirmed_count
        or base_statistics.executable_count != outcome_result.available_entry_count
        or base_statistics.session_end_unavailable_count
        != outcome_result.session_end_unavailable_count
        or base_statistics.missing_entry_count != outcome_result.missing_entry_count
    ):
        raise EmaComparisonInputError("Stage 9.3 population does not match sources")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_identity = {item.setup_identity: item for item in confirmed}
    annotation_by_identity = {item.setup_identity: item for item in annotations}
    outcome_by_identity = {
        item.setup_identity: item for item in outcome_result.outcomes
    }
    if len(annotation_by_identity) != len(annotations):
        raise EmaComparisonInputError("Duplicate EMA annotation identity")
    if set(annotation_by_identity) != set(setup_by_identity):
        raise EmaComparisonInputError("Annotations must match confirmed Stage 9 setups")
    if set(outcome_by_identity) != set(setup_by_identity):
        raise EmaComparisonInputError("Outcomes must match confirmed Stage 9 setups")
    for identity, annotation in annotation_by_identity.items():
        setup = setup_by_identity[identity]
        if (
            annotation.session_date != setup.session_date
            or annotation.direction is not setup.direction
            or annotation.confirmation_bar_timestamp
            != setup.confirmation_bar_timestamp
            or annotation.signal_known_at != setup.signal_known_at
        ):
            raise EmaComparisonInputError("EMA annotation does not match frozen setup")

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
        BaseStrategyGroupDimension.OVERALL,
        "OVERALL",
        available,
    )
    if reproduced != baseline:
        raise EmaComparisonInputError("BASE_ALL does not reproduce Stage 9.3 exactly")

    group_specs = (
        (EmaComparisonGroupName.BASE_ALL, None),
        (EmaComparisonGroupName.EMA_ALIGNED, EmaAlignmentState.EMA_ALIGNED),
        (
            EmaComparisonGroupName.EMA_NOT_ALIGNED,
            EmaAlignmentState.EMA_NOT_ALIGNED,
        ),
        (
            EmaComparisonGroupName.EMA_UNAVAILABLE,
            EmaAlignmentState.EMA_UNAVAILABLE,
        ),
    )
    groups = []
    for name, state in group_specs:
        selected_annotations = tuple(
            item
            for item in annotations
            if state is None or item.alignment_state is state
        )
        selected = tuple(
            item
            for item in available
            if state is None
            or annotation_by_identity[item.setup_identity].alignment_state is state
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL,
            name.value,
            selected,
        )
        groups.append(
            EmaAlignmentGroupStatistics(
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
                deltas=_group_deltas(stats, baseline),
            )
        )

    direction_groups = []
    for direction in SetupDirection:
        for state in EmaAlignmentState:
            selected = tuple(
                item
                for item in available
                if item.setup.direction is direction
                and annotation_by_identity[item.setup_identity].alignment_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.DIRECTION,
                f"{direction.value}+{state.value}",
                selected,
            )
            direction_groups.append(
                EmaDirectionGroupStatistics(
                    direction=direction,
                    alignment_state=state,
                    executable_n=len(selected),
                    horizons=stats.horizons,
                )
            )

    level_groups = []
    for level in LevelType:
        for state in EmaAlignmentState:
            level_annotations = tuple(
                item
                for item in annotations
                if setup_by_identity[item.setup_identity].level_type is level
                and item.alignment_state is state
            )
            selected = tuple(
                item
                for item in available
                if item.setup.level_type is level
                and annotation_by_identity[item.setup_identity].alignment_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.LEVEL,
                f"{level.value}+{state.value}",
                selected,
            )
            level_groups.append(
                EmaLevelAlignmentStatistics(
                    level_type=level,
                    alignment_state=state,
                    annotation_n=len(level_annotations),
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )
    return EmaAlignmentComparisonResult(
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
    )
