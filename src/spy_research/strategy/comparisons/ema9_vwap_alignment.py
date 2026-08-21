"""Pure Stage 10.4 EMA9/VWAP annotation and controlled comparison."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal, localcontext

from spy_research.indicators import FiveMinuteIndicatorRow, FiveMinuteVwapRow
from spy_research.indicators.vwap import VWAP_CONTEXT
from spy_research.interactions import LevelType
from spy_research.research_stats import summarize_distribution
from spy_research.strategy.base_statistics import (
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    summarize_base_outcome_group,
)
from spy_research.strategy.comparisons.models import (
    CrossContextEma9VwapCrossTabCount,
    Ema9VwapAlignmentAnnotation,
    Ema9VwapAlignmentComparisonResult,
    Ema9VwapAlignmentState,
    Ema9VwapBaselineDelta,
    Ema9VwapComparisonGroupName,
    Ema9VwapDirectionStatistics,
    Ema9VwapDistanceStatistics,
    Ema9VwapGroupStatistics,
    Ema9VwapLevelStatistics,
    EmaAlignmentAnnotation,
    EmaAlignmentEma9VwapCrossTabCount,
    EmaAlignmentState,
    EmaCrossContextAnnotation,
    EmaCrossContextState,
    PriceEma9VwapAgreementState,
    PriceEma9VwapAgreementStatistics,
    PriceVwapEma9VwapCrossTabCount,
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


class Ema9VwapComparisonInputError(ValueError):
    """Frozen Stage 3/9 inputs cannot form a trustworthy comparison."""


def annotate_ema9_vwap_alignment(
    setup: BasePriceActionCandidate,
    ema_row: FiveMinuteIndicatorRow | None,
    vwap_row: FiveMinuteVwapRow | None,
) -> Ema9VwapAlignmentAnnotation:
    """Label one setup from exact confirmation-row EMA9 and VWAP only."""

    if setup.status is not BaseSetupStatus.CONFIRMED:
        raise Ema9VwapComparisonInputError(
            "Only confirmed Stage 9.1 setups may be annotated"
        )
    if setup.confirmation_bar_timestamp is None or setup.signal_known_at is None:
        raise Ema9VwapComparisonInputError("Confirmed setup lacks frozen timing")
    if setup.signal_known_at != setup.confirmation_bar_timestamp + timedelta(minutes=5):
        raise Ema9VwapComparisonInputError(
            "Signal-known time must follow confirmation by 5 minutes"
        )
    for row, label in ((ema_row, "EMA9"), (vwap_row, "VWAP")):
        if row is not None and (
            row.symbol != setup.symbol
            or row.session_date != setup.session_date
            or row.timestamp != setup.confirmation_bar_timestamp
            or row.timeframe != "5Min"
            or row.session_mode != "RTH_ONLY"
        ):
            raise Ema9VwapComparisonInputError(
                f"{label} row must match confirmation timestamp and RTH provenance"
            )
    ema9 = ema_row.ema9 if ema_row is not None else None
    vwap = vwap_row.vwap if vwap_row is not None else None
    if ema9 is None or vwap is None:
        return Ema9VwapAlignmentAnnotation(
            setup_identity=setup.setup_identity,
            session_date=setup.session_date,
            direction=setup.direction,
            confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
            signal_known_at=setup.signal_known_at,
            ema9=ema9,
            vwap=vwap,
            indicator_timestamp=None,
            alignment_state=Ema9VwapAlignmentState.EMA9_VWAP_UNAVAILABLE,
            signed_ema9_vwap_distance=None,
            absolute_ema9_vwap_distance=None,
            directional_ema9_vwap_distance=None,
        )
    with localcontext(VWAP_CONTEXT):
        signed = ema9 - vwap
        directional = signed if setup.direction is SetupDirection.LONG else -signed
    state = (
        Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED
        if directional > 0
        else Ema9VwapAlignmentState.EMA9_VWAP_NOT_ALIGNED
    )
    return Ema9VwapAlignmentAnnotation(
        setup_identity=setup.setup_identity,
        session_date=setup.session_date,
        direction=setup.direction,
        confirmation_bar_timestamp=setup.confirmation_bar_timestamp,
        signal_known_at=setup.signal_known_at,
        ema9=ema9,
        vwap=vwap,
        indicator_timestamp=setup.confirmation_bar_timestamp,
        alignment_state=state,
        signed_ema9_vwap_distance=signed,
        absolute_ema9_vwap_distance=abs(signed),
        directional_ema9_vwap_distance=directional,
    )


def annotate_confirmed_ema9_vwap_alignment(
    setup_result: BasePriceActionResult,
    ema_rows: Sequence[FiveMinuteIndicatorRow],
    vwap_rows: Sequence[FiveMinuteVwapRow],
) -> tuple[Ema9VwapAlignmentAnnotation, ...]:
    """Annotate every confirmed setup by exact timestamp lookup only."""

    def index_rows(rows, label):
        indexed = {}
        previous = None
        for row in rows:
            key = (row.session_date, row.timestamp)
            if key in indexed:
                raise Ema9VwapComparisonInputError(f"Duplicate {label} timestamp")
            if previous is not None and row.timestamp <= previous:
                raise Ema9VwapComparisonInputError(f"{label} rows must be chronological")
            indexed[key] = row
            previous = row.timestamp
        return indexed

    ema_by_key = index_rows(ema_rows, "EMA")
    vwap_by_key = index_rows(vwap_rows, "VWAP")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    annotations = tuple(
        annotate_ema9_vwap_alignment(
            item,
            ema_by_key.get((item.session_date, item.confirmation_bar_timestamp)),
            vwap_by_key.get((item.session_date, item.confirmation_bar_timestamp)),
        )
        for item in confirmed
    )
    if len({item.setup_identity for item in annotations}) != len(annotations):
        raise Ema9VwapComparisonInputError("Duplicate EMA9/VWAP annotation identity")
    return annotations


def _delta(left: Decimal | None, right: Decimal | None) -> Decimal | None:
    return left - right if left is not None and right is not None else None


def _deltas(group, baseline) -> tuple[Ema9VwapBaselineDelta, ...]:
    return tuple(
        Ema9VwapBaselineDelta(
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


def _agreement_state(
    price_state: VwapAlignmentState,
    ema9_state: Ema9VwapAlignmentState,
) -> PriceEma9VwapAgreementState:
    if (
        price_state is VwapAlignmentState.VWAP_UNAVAILABLE
        or ema9_state is Ema9VwapAlignmentState.EMA9_VWAP_UNAVAILABLE
    ):
        return PriceEma9VwapAgreementState.UNAVAILABLE
    price_aligned = price_state is VwapAlignmentState.VWAP_ALIGNED
    ema9_aligned = ema9_state is Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED
    if price_aligned and ema9_aligned:
        return PriceEma9VwapAgreementState.BOTH_ALIGNED
    if price_aligned:
        return PriceEma9VwapAgreementState.PRICE_ONLY_ALIGNED
    if ema9_aligned:
        return PriceEma9VwapAgreementState.EMA9_ONLY_ALIGNED
    return PriceEma9VwapAgreementState.NEITHER_ALIGNED


def _distance_summary(
    annotations: Sequence[Ema9VwapAlignmentAnnotation],
    direction: SetupDirection | None,
) -> Ema9VwapDistanceStatistics:
    population = tuple(
        item
        for item in annotations
        if direction is None or item.direction is direction
    )
    values = tuple(
        item.directional_ema9_vwap_distance
        for item in population
        if item.directional_ema9_vwap_distance is not None
    )
    typed = tuple(value for value in values if value is not None)
    return Ema9VwapDistanceStatistics(
        direction=direction,
        distribution=summarize_distribution(typed),
        positive_n=sum(value > 0 for value in typed),
        zero_n=sum(value == 0 for value in typed),
        negative_n=sum(value < 0 for value in typed),
        unavailable_n=len(population) - len(typed),
    )


def calculate_ema9_vwap_alignment_comparison(
    setup_result: BasePriceActionResult,
    outcome_result: SetupOutcomeResult,
    base_statistics: BaseStrategyStatistics,
    annotations: Sequence[Ema9VwapAlignmentAnnotation],
    price_vwap_annotations: Sequence[VwapAlignmentAnnotation],
    ema_annotations: Sequence[EmaAlignmentAnnotation],
    cross_annotations: Sequence[EmaCrossContextAnnotation],
) -> Ema9VwapAlignmentComparisonResult:
    """Describe frozen outcomes by exact confirmation-row EMA9/VWAP state."""

    if not (
        setup_result.start_date
        == outcome_result.start_date
        == base_statistics.start_date
        and setup_result.end_date
        == outcome_result.end_date
        == base_statistics.end_date
    ):
        raise Ema9VwapComparisonInputError("Frozen source ranges do not match")
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
        raise Ema9VwapComparisonInputError("Stage 9.3 population mismatch")
    confirmed = tuple(
        item
        for item in setup_result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    setup_by_id = {item.setup_identity: item for item in confirmed}
    current_by_id = {item.setup_identity: item for item in annotations}
    price_by_id = {item.setup_identity: item for item in price_vwap_annotations}
    ema_by_id = {item.setup_identity: item for item in ema_annotations}
    cross_by_id = {item.setup_identity: item for item in cross_annotations}
    outcome_by_id = {item.setup_identity: item for item in outcome_result.outcomes}
    maps = (
        setup_by_id,
        current_by_id,
        price_by_id,
        ema_by_id,
        cross_by_id,
        outcome_by_id,
    )
    if any(len(item) != len(confirmed) for item in maps):
        raise Ema9VwapComparisonInputError("Comparison identities are incomplete")
    if len({frozenset(item) for item in maps}) != 1:
        raise Ema9VwapComparisonInputError("Comparison identities do not match")
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
        raise Ema9VwapComparisonInputError("BASE_ALL does not reproduce Stage 9.3")

    group_specs = (
        (Ema9VwapComparisonGroupName.BASE_ALL, None),
        (
            Ema9VwapComparisonGroupName.EMA9_VWAP_ALIGNED,
            Ema9VwapAlignmentState.EMA9_VWAP_ALIGNED,
        ),
        (
            Ema9VwapComparisonGroupName.EMA9_VWAP_NOT_ALIGNED,
            Ema9VwapAlignmentState.EMA9_VWAP_NOT_ALIGNED,
        ),
        (
            Ema9VwapComparisonGroupName.EMA9_VWAP_UNAVAILABLE,
            Ema9VwapAlignmentState.EMA9_VWAP_UNAVAILABLE,
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
            if state is None or current_by_id[item.setup_identity].alignment_state is state
        )
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, name.value, selected
        )
        groups.append(
            Ema9VwapGroupStatistics(
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
                deltas=_deltas(stats, baseline),
            )
        )

    direction_groups = []
    for direction in SetupDirection:
        for state in Ema9VwapAlignmentState:
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
                Ema9VwapDirectionStatistics(
                    direction=direction,
                    alignment_state=state,
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    level_groups = []
    for level in LevelType:
        for state in Ema9VwapAlignmentState:
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
                Ema9VwapLevelStatistics(
                    level_type=level,
                    alignment_state=state,
                    annotation_n=len(selected_annotations),
                    executable_n=len(selected),
                    eod=stats.horizons[-1],
                )
            )

    price_tab = tuple(
        PriceVwapEma9VwapCrossTabCount(
            price_vwap_state=price_state,
            ema9_vwap_state=ema9_state,
            annotation_n=sum(
                price_by_id[item.setup_identity].alignment_state is price_state
                and item.alignment_state is ema9_state
                for item in annotations
            ),
        )
        for price_state in VwapAlignmentState
        for ema9_state in Ema9VwapAlignmentState
    )
    ema_tab = tuple(
        EmaAlignmentEma9VwapCrossTabCount(
            ema_alignment_state=ema_state,
            ema9_vwap_state=ema9_state,
            annotation_n=sum(
                ema_by_id[item.setup_identity].alignment_state is ema_state
                and item.alignment_state is ema9_state
                for item in annotations
            ),
        )
        for ema_state in EmaAlignmentState
        for ema9_state in Ema9VwapAlignmentState
    )
    cross_tab = tuple(
        CrossContextEma9VwapCrossTabCount(
            cross_state=cross_state,
            ema9_vwap_state=ema9_state,
            annotation_n=sum(
                cross_by_id[item.setup_identity].cross_state is cross_state
                and item.alignment_state is ema9_state
                for item in annotations
            ),
        )
        for cross_state in EmaCrossContextState
        for ema9_state in Ema9VwapAlignmentState
    )
    agreement_groups = []
    for state in PriceEma9VwapAgreementState:
        selected_annotations = tuple(
            item
            for item in annotations
            if _agreement_state(
                price_by_id[item.setup_identity].alignment_state,
                item.alignment_state,
            )
            is state
        )
        identities = {item.setup_identity for item in selected_annotations}
        selected = tuple(item for item in available if item.setup_identity in identities)
        stats = summarize_base_outcome_group(
            BaseStrategyGroupDimension.OVERALL, state.value, selected
        )
        agreement_groups.append(
            PriceEma9VwapAgreementStatistics(
                state=state,
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
                eod=stats.horizons[-1],
            )
        )
    return Ema9VwapAlignmentComparisonResult(
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
        price_vwap_cross_tab=price_tab,
        ema_alignment_cross_tab=ema_tab,
        cross_context_cross_tab=cross_tab,
        agreement_groups=tuple(agreement_groups),
        distance_statistics=tuple(
            _distance_summary(annotations, direction)
            for direction in (None, SetupDirection.LONG, SetupDirection.SHORT)
        ),
    )
