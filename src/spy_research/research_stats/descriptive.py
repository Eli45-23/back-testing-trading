"""Deterministic descriptive statistics for frozen EMA-cross outcomes."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from decimal import Decimal, localcontext

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events import EmaCrossDirection
from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.outcomes import (
    EmaCrossOutcomeContextService,
    EnrichedEmaCrossOutcome,
)
from spy_research.research_stats.models import (
    DistributionSummary,
    FavorableAdverseCounts,
    GroupStatistics,
    HorizonStatistics,
    OppositeCrossTimingSummary,
    Phase1CrossStatistics,
    ThresholdSummary,
)


DOLLAR_THRESHOLDS = tuple(
    Decimal(value) for value in ("0.25", "0.50", "0.75", "1.00", "1.50", "2.00", "3.00")
)
ATR_THRESHOLDS = tuple(Decimal(value) for value in ("0.5", "1.0", "1.5", "2.0"))
HORIZON_FIELDS = (
    ("5m", "five", True),
    ("15m", "fifteen", True),
    ("30m", "thirty", True),
    ("60m", "sixty", True),
    ("EOD", "eod", False),
)


class StatisticsSequenceError(ValueError):
    """Outcome sequence cannot form a trustworthy descriptive sample."""


def _percentile(sorted_values: Sequence[Decimal], q: Decimal) -> Decimal:
    if not sorted_values:
        raise ValueError("percentile requires at least one value")
    with localcontext(EMA_CONTEXT):
        rank = Decimal(len(sorted_values) - 1) * q
        lower = int(rank)
        upper = min(lower + 1, len(sorted_values) - 1)
        fraction = rank - Decimal(lower)
        return sorted_values[lower] + (
            sorted_values[upper] - sorted_values[lower]
        ) * fraction


def summarize_distribution(values: Sequence[Decimal]) -> DistributionSummary:
    """Summarize without mutation using linear `(n-1)*q` interpolation."""

    if any(not isinstance(value, Decimal) or not value.is_finite() for value in values):
        raise ValueError("distribution values must be finite Decimals")
    if not values:
        return DistributionSummary(
            n=0,
            mean=None,
            median=None,
            minimum=None,
            maximum=None,
            p25=None,
            p75=None,
        )
    ordered = tuple(sorted(values))
    with localcontext(EMA_CONTEXT):
        mean = sum(ordered, Decimal(0)) / Decimal(len(ordered))
        median = _percentile(ordered, Decimal("0.5"))
        p25 = _percentile(ordered, Decimal("0.25"))
        p75 = _percentile(ordered, Decimal("0.75"))
    return DistributionSummary(
        n=len(ordered),
        mean=mean,
        median=median,
        minimum=ordered[0],
        maximum=ordered[-1],
        p25=p25,
        p75=p75,
    )


def _threshold_summaries(
    values: Sequence[Decimal],
    thresholds: Sequence[Decimal],
) -> tuple[ThresholdSummary, ...]:
    denominator = len(values)
    summaries = []
    with localcontext(EMA_CONTEXT):
        for threshold in thresholds:
            reached = sum(value >= threshold for value in values)
            percentage = (
                Decimal(reached) * Decimal(100) / Decimal(denominator)
                if denominator
                else None
            )
            summaries.append(
                ThresholdSummary(
                    threshold=threshold,
                    reached_n=reached,
                    eligible_n=denominator,
                    percentage=percentage,
                )
            )
    return tuple(summaries)


def _is_vwap_aligned(item: EnrichedEmaCrossOutcome) -> bool:
    event = item.outcome.event
    if event.vwap is None:
        return False
    if event.direction == EmaCrossDirection.BULLISH:
        return event.reference_price > event.vwap
    return event.reference_price < event.vwap


def _is_expanding(item: EnrichedEmaCrossOutcome) -> bool:
    event = item.outcome.event
    delta = event.separation_delta_1
    if delta is None:
        return False
    if event.direction == EmaCrossDirection.BULLISH:
        return delta > 0
    return delta < 0


def _eligible_horizon(
    items: Sequence[EnrichedEmaCrossOutcome],
    field: str,
    require_complete: bool,
) -> tuple[EnrichedEmaCrossOutcome, ...]:
    selected = []
    for item in items:
        horizon = getattr(item.outcome, field)
        available = horizon.excursion.mfe is not None
        if available and (horizon.complete or not require_complete):
            selected.append(item)
    return tuple(selected)


def _summarize_horizon(
    items: Sequence[EnrichedEmaCrossOutcome],
    *,
    name: str,
    field: str,
    require_complete: bool,
) -> HorizonStatistics:
    eligible = _eligible_horizon(items, field, require_complete)
    mfe_values = tuple(getattr(item.outcome, field).excursion.mfe for item in eligible)
    mae_values = tuple(getattr(item.outcome, field).excursion.mae for item in eligible)
    assert all(value is not None for value in mfe_values + mae_values)
    mfe = tuple(value for value in mfe_values if value is not None)
    mae = tuple(value for value in mae_values if value is not None)
    normalized = []
    for item, value in zip(eligible, mfe, strict=True):
        atr = item.outcome.event.atr14
        if atr is not None and atr > 0:
            with localcontext(EMA_CONTEXT):
                normalized.append(value / atr)
    comparisons = FavorableAdverseCounts(
        mfe_greater=sum(left > right for left, right in zip(mfe, mae, strict=True)),
        equal=sum(left == right for left, right in zip(mfe, mae, strict=True)),
        mfe_less=sum(left < right for left, right in zip(mfe, mae, strict=True)),
    )
    return HorizonStatistics(
        horizon=name,
        eligible_n=len(eligible),
        excluded_incomplete_n=len(items) - len(eligible),
        mfe=summarize_distribution(mfe),
        mae=summarize_distribution(mae),
        dollar_thresholds=_threshold_summaries(mfe, DOLLAR_THRESHOLDS),
        atr_thresholds=_threshold_summaries(normalized, ATR_THRESHOLDS),
        atr_eligible_n=len(normalized),
        atr_excluded_n=len(eligible) - len(normalized),
        favorable_adverse=comparisons,
    )


def _group(name: str, items: Sequence[EnrichedEmaCrossOutcome]) -> GroupStatistics:
    return GroupStatistics(
        name=name,
        total_n=len(items),
        horizons=tuple(
            _summarize_horizon(
                items,
                name=horizon,
                field=field,
                require_complete=require_complete,
            )
            for horizon, field, require_complete in HORIZON_FIELDS
        ),
    )


def calculate_phase1_cross_statistics(
    outcomes: Sequence[EnrichedEmaCrossOutcome],
    *,
    start: date,
    end: date,
) -> Phase1CrossStatistics:
    """Calculate all frozen descriptive groups without inference or optimization."""

    previous_timestamp = None
    identities = set()
    for item in outcomes:
        event = item.outcome.event
        identity = (event.symbol, event.timestamp, event.direction, event.event_version)
        if identity in identities:
            raise StatisticsSequenceError("Duplicate event identity in statistics input")
        if previous_timestamp is not None and event.timestamp <= previous_timestamp:
            raise StatisticsSequenceError(
                "Statistics outcomes must be strictly chronological"
            )
        identities.add(identity)
        previous_timestamp = event.timestamp

    all_items = tuple(outcomes)
    bullish = tuple(
        item for item in all_items if item.outcome.event.direction == EmaCrossDirection.BULLISH
    )
    bearish = tuple(
        item for item in all_items if item.outcome.event.direction == EmaCrossDirection.BEARISH
    )
    aligned = tuple(item for item in all_items if _is_vwap_aligned(item))
    not_aligned = tuple(item for item in all_items if not _is_vwap_aligned(item))
    expanding = tuple(item for item in all_items if _is_expanding(item))
    not_expanding = tuple(item for item in all_items if not _is_expanding(item))
    combined = tuple(
        item for item in all_items if _is_vwap_aligned(item) and _is_expanding(item)
    )
    other = tuple(
        item
        for item in all_items
        if not (_is_vwap_aligned(item) and _is_expanding(item))
    )
    groups = (
        _group("ALL", all_items),
        _group("BULLISH", bullish),
        _group("BEARISH", bearish),
        _group("VWAP_ALIGNED", aligned),
        _group("VWAP_NOT_ALIGNED", not_aligned),
        _group("EXPANDING", expanding),
        _group("NOT_EXPANDING", not_expanding),
        _group("VWAP_ALIGNED_AND_EXPANDING", combined),
        _group("OTHER", other),
    )
    opposite_minutes = tuple(
        Decimal(item.opposite_cross.minutes_to_opposite_cross)
        for item in all_items
        if item.opposite_cross.minutes_to_opposite_cross is not None
    )
    return Phase1CrossStatistics(
        start_date=start,
        end_date=end,
        total_n=len(all_items),
        bullish_n=len(bullish),
        bearish_n=len(bearish),
        groups=groups,
        absolute_separation=summarize_distribution(
            tuple(item.outcome.event.absolute_separation for item in all_items)
        ),
        opposite_cross_timing=OppositeCrossTimingSummary(
            with_opposite_n=len(opposite_minutes),
            without_opposite_n=len(all_items) - len(opposite_minutes),
            minutes=summarize_distribution(opposite_minutes),
        ),
    )


class Phase1CrossStatisticsService:
    """Reuse Stage 5 outcomes, then calculate descriptive statistics in memory."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._context_service = EmaCrossOutcomeContextService(
            config,
            processed_store,
            raw_store,
        )

    def calculate(self, *, start: date, end: date) -> Phase1CrossStatistics:
        source = self._context_service.calculate(start=start, end=end)
        return calculate_phase1_cross_statistics(
            source.outcomes,
            start=start,
            end=end,
        )
