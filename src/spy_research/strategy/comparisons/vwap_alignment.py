"""Pure Stage 10.3 confirmation-price/VWAP annotation and comparison."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal, localcontext

from spy_research.bars import FiveMinuteBar
from spy_research.indicators import FiveMinuteVwapRow
from spy_research.indicators.vwap import VWAP_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.models import (
    EmaAlignmentAnnotation,
    EmaAlignmentState,
    EmaCrossContextAnnotation,
    EmaCrossContextState,
    EmaCrossVwapCrossTabCount,
    EmaVwapCrossTabCount,
    VwapAlignmentAnnotation,
    VwapAlignmentComparisonResult,
    VwapAlignmentGroupStatistics,
    VwapAlignmentState,
    VwapBaselineDelta,
    VwapComparisonGroupName,
    VwapDirectionStatistics,
    VwapDistanceStatistics,
    VwapLevelStatistics,
)
from spy_research.strategy.models import (
    BasePriceActionCandidate,
    BasePriceActionResult,
    BaseSetupStatus,
    EntryStatus,
    SetupDirection,
    SetupOutcomeResult,
)


class VwapComparisonInputError(ValueError):
    """Frozen Stage 3/9 inputs cannot form a trustworthy VWAP comparison."""


def annotate_vwap_alignment(
    setup: BasePriceActionCandidate,
    confirmation_bar: FiveMinuteBar,
    vwap_row: FiveMinuteVwapRow | None,
) -> VwapAlignmentAnnotation:
    """Label one setup from only its exact completed confirmation candle."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise VwapComparisonInputError("Only confirmed Stage 9.1 setups may be annotated")
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise VwapComparisonInputError("Confirmed setup lacks frozen timing")
    if setup.signal_known_at != setup.confirmation_bar_timestamp + timedelta(minutes=5):
        raise VwapComparisonInputError(
            "Signal-known time must follow confirmation by 5 minutes"
        )
    if (
        confirmation_bar.symbol != setup.symbol
        or confirmation_bar.session_date != setup.session_date
        or confirmation_bar.timestamp != setup.confirmation_bar_timestamp
        or confirmation_bar.timeframe != "5Min"
        or confirmation_bar.session_mode != "RTH_ONLY"
        or confirmation_bar.session_type != "RTH"
    ):
        raise VwapComparisonInputError(
            "Price bar must match the setup confirmation timestamp and RTH provenance"
        )
    if vwap_row is None or vwap_row.vwap is None:
        if vwap_row is not None and (
            vwap_row.symbol != setup.symbol
            or vwap_row.session_date != setup.session_date
            or vwap_row.timestamp != setup.confirmation_bar_timestamp
        ):
            raise VwapComparisonInputError(
                "VWAP row must match the setup confirmation timestamp"
            )
        return VwapAlignmentAnnotation(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
            signal_known_at=setup.signal_known_at,
            confirmation_close=confirmation_bar.close,
            vwap=None,
            indicator_timestamp=None,
            alignment_state=VwapAlignmentState.VWAP_UNAVAILABLE,
            signed_price_vwap_distance=None,
            absolute_price_vwap_distance=None,
            directional_vwap_distance=None,
        )
    if (
        vwap_row.symbol != setup.symbol
        or vwap_row.session_date != setup.session_date
        or vwap_row.timestamp != setup.confirmation_bar_timestamp
        or vwap_row.timeframe != "5Min"
        or vwap_row.session_mode != "RTH_ONLY"
    ):
        raise VwapComparisonInputError(
            "VWAP row must match the setup confirmation timestamp and RTH provenance"
        )
    with localcontext(VWAP_CONTEXT):
        signed = confirmation_bar.close - vwap_row.vwap
        directional = signed if setup.direction is SetupDirection.LONG else -signed
    state = (
        VwapAlignmentState.VWAP_ALIGNED
        if directional > 0
        else VwapAlignmentState.VWAP_NOT_ALIGNED
    )
    return VwapAlignmentAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        confirmation_close=confirmation_bar.close,
        vwap=vwap_row.vwap,
        indicator_timestamp=vwap_row.timestamp,
        alignment_state=state,
        signed_price_vwap_distance=signed,
        absolute_price_vwap_distance=abs(signed),
        directional_vwap_distance=directional,
    )


def annotate_confirmed_vwap_alignment(
    setup_result: BasePriceActionResult,
    bars: Sequence[FiveMinuteBar],
    vwap_rows: Sequence[FiveMinuteVwapRow],
) -> tuple[VwapAlignmentAnnotation, ...]:
    """Annotate every confirmed setup by exact session/timestamp lookup."""

    def index_rows(rows, label):
        indexed = {}
        previous = None
        for row in rows:
            key = (row.session_date, row.timestamp)
            if key in indexed:
                raise VwapComparisonInputError(f"Duplicate {label} timestamp")
            if previous is not None and row.timestamp <= previous:
                raise VwapComparisonInputError(f"{label} rows must be chronological")
            indexed[key] = row
            previous = row.timestamp
        return indexed

    bars_by_key = index_rows(bars, "confirmation bar")
    vwap_by_key = index_rows(vwap_rows, "VWAP")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = []
    for item in confirmed:
        key = (item.session_date, item.confirmation_bar_timestamp)
        bar = bars_by_key.get(key)
        if bar is None:
            raise VwapComparisonInputError(
                "Confirmed setup is missing its authoritative five-minute bar"
            )
        annotations.append(annotate_vwap_alignment(item, bar, vwap_by_key.get(key)))
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise VwapComparisonInputError("Duplicate VWAP annotation setup identity")
    return tuple(annotations)


def _delta(left: Decimal | None, right: Decimal | None) -> Decimal | None:
    return left - right if left is not None and right is not None else None


def _group_deltas(group, baseline) -> tuple[VwapBaselineDelta, ...]:
    return tuple(
        VwapBaselineDelta(
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


def _distance_statistics(
    annotations: Sequence[VwapAlignmentAnnotation],
    direction: SetupDirection | None,
) -> VwapDistanceStatistics:
    values = tuple(
        item.directional_vwap_distance
        for item in annotations
        if item.directional_vwap_distance is not None
        and (direction is None or item.direction is direction)
    )
    typed = tuple(value for value in values if value is not None)
    return VwapDistanceStatistics(
        direction=direction,
        distribution=summarize_distribution(typed),
        positive_n=sum(value > 0 for value in typed),
        zero_n=sum(value == 0 for value in typed),
        negative_n=sum(value < 0 for value in typed),
    )


def calculate_vwap_alignment_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[VwapAlignmentAnnotation],
    ema_annotations: Sequence[EmaAlignmentAnnotation],
    cross_annotations: Sequence[EmaCrossContextAnnotation],
) -> VwapAlignmentComparisonResult:
    """Compare unchanged Stage 9 outcomes after immutable VWAP annotation."""

    if not (
        setup_result.start_date
        == outcome_result.start_date
        == base_statistics.start_date
        and setup_result.end_date
        == outcome_result.end_date
        == base_statistics.end_date
    ):
        raise VwapComparisonInputError("Frozen Stage 9 source ranges do not match")
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
        raise VwapComparisonInputError("Stage 9.3 population does not match sources")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_id = {item.setup_identity: item for item in confirmed}
    annotation_by_id = {item.setup_identity: item for item in annotations}
    ema_by_id = {item.setup_identity: item for item in ema_annotations}
    cross_by_id = {item.setup_identity: item for item in cross_annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    maps = (setup_by_id, annotation_by_id, ema_by_id, cross_by_id, outcome_by_id)
    if any(len(item) != len(confirmed) for item in maps):
        raise VwapComparisonInputError("Comparison identities are duplicate or incomplete")
    if len({frozenset(item) for item in maps}) != 1:
        raise VwapComparisonInputError("Comparison identities do not match")
    for identity, annotation in annotation_by_id.items():
        setup = setup_by_id[identity]
        if (
            annotation.session_date != setup.session_date
            or annotation.direction is not setup.direction
            or annotation.confirmation_bar_timestamp != setup.confirmation_bar_timestamp
            or annotation.signal_known_at != setup.signal_known_at
        ):
            raise VwapComparisonInputError("VWAP annotation does not match frozen setup")

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
        raise VwapComparisonInputError("BASE_ALL does not reproduce Stage 9.3 exactly")

    group_specs = (
        (VwapComparisonGroupName.BASE_ALL, None),
        (VwapComparisonGroupName.VWAP_ALIGNED, VwapAlignmentState.VWAP_ALIGNED),
        (
            VwapComparisonGroupName.VWAP_NOT_ALIGNED,
            VwapAlignmentState.VWAP_NOT_ALIGNED,
        ),
        (
            VwapComparisonGroupName.VWAP_UNAVAILABLE,
            VwapAlignmentState.VWAP_UNAVAILABLE,
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
            or annotation_by_id[item.setup_identity].alignment_state is state
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, name.value, selected
        )
        groups.append(
            VwapAlignmentGroupStatistics(
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
        for state in VwapAlignmentState:
            selected = tuple(
                item
                for item in available
                if item.setup.direction is direction
                and annotation_by_id[item.setup_identity].alignment_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.DIRECTION,
                f"{direction.value}+{state.value}",
                selected,
            )
            direction_groups.append(
                VwapDirectionStatistics(
                    direction=direction,
                    alignment_state=state,
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    level_groups = []
    for level in LevelType:
        for state in VwapAlignmentState:
            level_annotations = tuple(
                item
                for item in annotations
                if setup_by_id[item.setup_identity].level_type is level
                and item.alignment_state is state
            )
            selected = tuple(
                item
                for item in available
                if item.setup.level_type is level
                and annotation_by_id[item.setup_identity].alignment_state is state
            )
            stats = summarize_base_outcome_group(
                BaseStrategyGroupDimension.LEVEL,
                f"{level.value}+{state.value}",
                selected,
            )
            level_groups.append(
                VwapLevelStatistics(
                    level_type=level,
                    alignment_state=state,
                    annotation_n=len(level_annotations),
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    ema_tab = tuple(
        EmaVwapCrossTabCount(
            ema_state=ema_state,
            vwap_state=vwap_state,
            annotation_n=sum(
                ema_by_id[item.setup_identity].alignment_state is ema_state
                and item.alignment_state is vwap_state
                for item in annotations
            ),
        )
        for ema_state in EmaAlignmentState
        for vwap_state in VwapAlignmentState
    )
    cross_tab = tuple(
        EmaCrossVwapCrossTabCount(
            cross_state=cross_state,
            vwap_state=vwap_state,
            annotation_n=sum(
                cross_by_id[item.setup_identity].cross_state is cross_state
                and item.alignment_state is vwap_state
                for item in annotations
            ),
        )
        for cross_state in EmaCrossContextState
        for vwap_state in VwapAlignmentState
    )
    return VwapAlignmentComparisonResult(
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
        ema_vwap_cross_tab=ema_tab,
        cross_context_vwap_cross_tab=cross_tab,
        distance_statistics=tuple(
            _distance_statistics(annotations, direction)
            for direction in (None, SetupDirection.LONG, SetupDirection.SHORT)
        ),
    )
