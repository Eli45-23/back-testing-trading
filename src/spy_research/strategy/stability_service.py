"""Read-only Stage 12.2 orchestration over accepted frozen research objects."""

from __future__ import annotations

from datetime import date
from typing import Any

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.strategy.models import EntryStatus, SetupOutcomeResult
from spy_research.strategy.comparisons import (
    CombinedContextMatrixResult,
    CombinedContextMatrixService,
    MarketConditionFeatureService,
    MarketStructureComparisonResult,
    MarketStructureComparisonService,
    frozen_boundaries,
)
from spy_research.strategy.setup_outcome_service import SetupOutcomeService
from spy_research.strategy.stability import (
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    CONTEXT_DIMENSIONS,
    ExpandedStabilityReport,
    FrozenStabilityHorizon,
    FrozenStabilityRecord,
    FrozenState,
    StabilityInputError,
    calculate_expanded_stability,
)


DEVELOPMENT_START = date(2026, 8, 3)
DEVELOPMENT_END = date(2026, 8, 19)


class _BoundedRawStore:
    """Read-only view preventing context outside the development snapshot."""

    def __init__(self, store: RawBarStore, start: date, end: date) -> None:
        self._store = store
        self._start = start
        self._end = end

    def load_partition(self, partition_date: date):
        if not self._start <= partition_date <= self._end:
            return ()
        return self._store.load_partition(partition_date)

    def load_raw_bars(self, *, start: date, end: date, **kwargs):
        bounded_start = max(start, self._start)
        bounded_end = min(end, self._end)
        if bounded_start > bounded_end:
            return ()
        return self._store.load_raw_bars(
            start=bounded_start,
            end=bounded_end,
            **kwargs,
        )

    def persist_bars(self, *_args, **_kwargs):
        raise StabilityInputError("Stage 12 development view is read-only")


class _BoundedProcessedStore:
    """Read-only processed view with exact chronological range isolation."""

    def __init__(
        self, store: ProcessedFiveMinuteStore, start: date, end: date
    ) -> None:
        self._store = store
        self._start = start
        self._end = end

    def load_partition(self, partition_date: date, **kwargs):
        if not self._start <= partition_date <= self._end:
            return ()
        return self._store.load_partition(partition_date, **kwargs)

    def load_processed_5m_bars(self, *, start: date, end: date, **kwargs):
        bounded_start = max(start, self._start)
        bounded_end = min(end, self._end)
        if bounded_start > bounded_end:
            return ()
        return self._store.load_processed_5m_bars(
            start=bounded_start,
            end=bounded_end,
            **kwargs,
        )

    def persist_bars(self, *_args, **_kwargs):
        raise StabilityInputError("Stage 12 development view is read-only")


def build_stability_records(
    outcomes: SetupOutcomeResult,
    context: CombinedContextMatrixResult,
    structure: MarketStructureComparisonResult,
) -> tuple[FrozenStabilityRecord, ...]:
    """Project accepted objects without recalculating or interpreting states."""

    outcome_by_id = {item.setup_identity: item for item in outcomes.outcomes}
    context_by_id = {item.setup_identity: item for item in context.annotations}
    audit_by_id = {
        item.annotation.setup_identity: item for item in structure.audit_rows
    }
    ids = set(outcome_by_id)
    if (
        len(ids) != len(outcomes.outcomes)
        or ids != set(context_by_id)
        or ids != set(audit_by_id)
    ):
        raise StabilityInputError("Stage 9-11 setup identities do not reconcile")
    context_fields = (
        ("EMA9_20_ALIGNMENT", "ema9_20_alignment"),
        ("EMA9_20_CROSS_CONTEXT", "ema9_20_cross_context"),
        ("PRICE_VWAP_ALIGNMENT", "price_vwap_alignment"),
        ("EMA9_VWAP_ALIGNMENT", "ema9_vwap_alignment"),
        ("EMA9_VWAP_CROSS_CONTEXT", "ema9_vwap_cross_context"),
        ("EMA20_VWAP_ALIGNMENT", "ema20_vwap_alignment"),
        ("EMA20_VWAP_CROSS_CONTEXT", "ema20_vwap_cross_context"),
    )
    rows = []
    for identity, outcome in sorted(
        outcome_by_id.items(), key=lambda item: (item[1].setup.session_date, item[0])
    ):
        context_row = context_by_id[identity]
        audit = audit_by_id[identity]
        states = tuple(
            FrozenState(
                dimension=dimension,
                state=getattr(context_row, field).value,
            )
            for dimension, field in context_fields
        ) + (
            FrozenState(dimension="REGIME", state=audit.regime_hypothesis.value),
            FrozenState(dimension="ROOM_BUCKET", state=audit.room_bucket.value),
            FrozenState(
                dimension="STRUCTURE",
                state=audit.annotation.combined_structure.value,
            ),
            FrozenState(
                dimension="STRUCTURE_AGREEMENT",
                state=audit.annotation.direction_agreement.value,
            ),
        )
        if tuple(item.dimension for item in states[:7]) != CONTEXT_DIMENSIONS:
            raise StabilityInputError("Stage 10 dimension order changed")
        executable = outcome.entry_reference.entry_status is EntryStatus.AVAILABLE
        source_horizons: tuple[tuple[str, Any], ...] = (
            ("5m", outcome.five),
            ("15m", outcome.fifteen),
            ("30m", outcome.thirty),
            ("60m", outcome.sixty),
            ("EOD", outcome.eod),
        )
        horizons = tuple(
            FrozenStabilityHorizon(
                horizon=name,
                complete=value.complete,
                mfe=value.mfe,
                mae=value.mae,
            )
            for name, value in source_horizons
            if value is not None
        )
        rows.append(
            FrozenStabilityRecord(
                setup_identity=identity,
                session_date=outcome.setup.session_date,
                direction=outcome.setup.direction,
                level_type=outcome.setup.level_type,
                executable=executable,
                states=states,
                horizons=horizons,
            )
        )
    return tuple(rows)


class ExpandedStabilityService:
    """Compose accepted local services without network access or persistence."""

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
        outcomes = SetupOutcomeService(
            self._config, processed, raw
        ).calculate(start=start, end=end)
        context = CombinedContextMatrixService(
            self._config, processed, raw
        ).calculate(start=start, end=end)
        structure = MarketStructureComparisonService(
            self._config, processed, raw
        ).calculate(
            start=start,
            end=end,
            regime_boundaries=boundaries,
        )
        return outcomes, context, structure

    def calculate(
        self,
        *,
        start: date,
        end: date,
        bootstrap_seed: int = BOOTSTRAP_SEED,
        bootstrap_resamples: int = BOOTSTRAP_RESAMPLES,
    ) -> ExpandedStabilityReport:
        if start != date(2026, 1, 2) or end != DEVELOPMENT_END:
            raise StabilityInputError(
                "Stage 12.2 requires the frozen 2026-01-02 through 2026-08-19 range"
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
        development_sources = self._sources(
            start=DEVELOPMENT_START,
            end=DEVELOPMENT_END,
            processed=development_processed,
            raw=development_raw,
            boundaries=boundaries,
        )
        expanded_sources = self._sources(
            start=start,
            end=end,
            processed=self._processed_store,
            raw=self._raw_store,
            boundaries=boundaries,
        )
        development_records = build_stability_records(*development_sources)
        expanded_records = build_stability_records(*expanded_sources)
        return calculate_expanded_stability(
            expanded_records,
            development_records,
            start=start,
            end=end,
            development_start=DEVELOPMENT_START,
            development_end=DEVELOPMENT_END,
            bootstrap_seed=bootstrap_seed,
            bootstrap_resamples=bootstrap_resamples,
        )
