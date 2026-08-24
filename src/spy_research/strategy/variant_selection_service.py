"""Read-only Stage 12.3 composition over accepted local research services."""

from __future__ import annotations

from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.strategy.comparisons import (
    CombinedContextMatrixResult,
    CombinedContextMatrixService,
    MarketConditionFeatureService,
    MarketStructureComparisonResult,
    MarketStructureComparisonService,
    RoomToLevelComparisonResult,
    RoomToLevelComparisonService,
    frozen_boundaries,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService
from spy_research.strategy.stability import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED
from spy_research.strategy.stability_service import (
    DEVELOPMENT_END,
    DEVELOPMENT_START,
    _BoundedProcessedStore,
    _BoundedRawStore,
    build_stability_records,
)
from spy_research.strategy.variant_selection import (
    CandidateContextRecord,
    ControlledVariantSelectionReport,
    VariantSelectionInputError,
    calculate_controlled_variant_selection,
)


def build_candidate_context_records(
    context: CombinedContextMatrixResult,
    structure: MarketStructureComparisonResult,
    room: RoomToLevelComparisonResult,
) -> tuple[CandidateContextRecord, ...]:
    """Join outcome-blind accepted annotations at one setup per identity."""

    context_by_id = {item.setup_identity: item for item in context.annotations}
    structure_by_id = {item.setup_identity: item for item in structure.annotations}
    room_by_id = {item.setup_identity: item for item in room.annotations}
    ids = set(context_by_id)
    if (
        len(ids) != len(context.annotations)
        or ids != set(structure_by_id)
        or ids != set(room_by_id)
    ):
        raise VariantSelectionInputError("Stage 10/11 context identities do not reconcile")
    records = []
    for identity, item in sorted(
        context_by_id.items(), key=lambda pair: (pair[1].session_date, pair[0])
    ):
        structure_item = structure_by_id[identity]
        room_item = room_by_id[identity]
        common = (
            item.session_date,
            item.signal_known_at,
            item.direction,
            item.level_type,
        )
        structure_common = (
            structure_item.session_date,
            structure_item.signal_known_at,
            structure_item.direction,
            structure_item.triggering_level_type,
        )
        room_common = (
            room_item.session_date,
            room_item.signal_known_at,
            room_item.direction,
            room_item.triggering_level_type,
        )
        if common != structure_common or common != room_common:
            raise VariantSelectionInputError(
                f"Frozen candidate annotations disagree for {identity}"
            )
        records.append(
            CandidateContextRecord(
                setup_identity=identity,
                session_date=item.session_date,
                signal_known_at=item.signal_known_at,
                direction=item.direction,
                level_type=item.level_type,
                ema9_20_alignment=item.ema9_20_alignment,
                price_vwap_alignment=item.price_vwap_alignment,
                ema9_vwap_alignment=item.ema9_vwap_alignment,
                ema20_vwap_alignment=item.ema20_vwap_alignment,
                structure_agreement=structure_item.direction_agreement,
                room_in_atr=room_item.room_in_atr,
            )
        )
    return tuple(records)


class ControlledVariantSelectionService:
    """Compose frozen annotations first and join outcomes only afterward."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._config = config
        self._processed_store = processed_store
        self._raw_store = raw_store

    def _sources(self, *, start: date, end: date, processed, raw, boundaries):
        outcomes = SetupOutcomeService(self._config, processed, raw).calculate(
            start=start, end=end
        )
        context = CombinedContextMatrixService(self._config, processed, raw).calculate(
            start=start, end=end
        )
        structure = MarketStructureComparisonService(
            self._config, processed, raw
        ).calculate(start=start, end=end, regime_boundaries=boundaries)
        room = RoomToLevelComparisonService(self._config, processed, raw).calculate(
            start=start, end=end, regime_boundaries=boundaries
        )
        return outcomes, context, structure, room

    def calculate(
        self,
        *,
        start: date,
        end: date,
        bootstrap_seed: int = BOOTSTRAP_SEED,
        bootstrap_resamples: int = BOOTSTRAP_RESAMPLES,
    ) -> ControlledVariantSelectionReport:
        if start != date(2026, 1, 2) or end != DEVELOPMENT_END:
            raise VariantSelectionInputError(
                "Stage 12.3 requires the frozen 2026-01-02 through 2026-08-19 range"
            )
        development_processed = _BoundedProcessedStore(
            self._processed_store, DEVELOPMENT_START, DEVELOPMENT_END
        )
        development_raw = _BoundedRawStore(
            self._raw_store, DEVELOPMENT_START, DEVELOPMENT_END
        )
        development_market = MarketConditionFeatureService(
            self._config, development_processed, development_raw
        ).calculate(start=DEVELOPMENT_START, end=DEVELOPMENT_END)
        boundaries = frozen_boundaries(development_market)
        development = self._sources(
            start=DEVELOPMENT_START,
            end=DEVELOPMENT_END,
            processed=development_processed,
            raw=development_raw,
            boundaries=boundaries,
        )
        expanded = self._sources(
            start=start,
            end=end,
            processed=self._processed_store,
            raw=self._raw_store,
            boundaries=boundaries,
        )
        development_outcomes, development_context, development_structure, development_room = development
        expanded_outcomes, expanded_context, expanded_structure, expanded_room = expanded
        development_contexts = build_candidate_context_records(
            development_context, development_structure, development_room
        )
        expanded_contexts = build_candidate_context_records(
            expanded_context, expanded_structure, expanded_room
        )
        development_records = build_stability_records(
            development_outcomes, development_context, development_structure
        )
        expanded_records = build_stability_records(
            expanded_outcomes, expanded_context, expanded_structure
        )
        return calculate_controlled_variant_selection(
            expanded_contexts,
            development_contexts,
            expanded_records,
            development_records,
            start=start,
            end=end,
            bootstrap_seed=bootstrap_seed,
            bootstrap_resamples=bootstrap_resamples,
        )
