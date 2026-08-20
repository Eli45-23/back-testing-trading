"""Deterministic in-memory research-bar transformations."""

from spy_research.bars.aggregation import (
    AggregationError,
    BucketIntegrityError,
    FiveMinuteAggregationService,
    RawDataValidationGateError,
    aggregate_rth_1m_to_5m,
)
from spy_research.bars.build import (
    FiveMinuteBuildResult,
    FiveMinuteBuildService,
    ProcessedValidationGateError,
)
from spy_research.bars.errors import (
    ProcessedDataConflictError,
    ProcessedDataCorruptionError,
    ProcessedDataError,
    ProcessedDataScopeError,
    ProcessedDataWriteError,
)
from spy_research.bars.models import (
    AggregationResult,
    FiveMinuteBar,
    SessionAggregationSummary,
)
from spy_research.bars.store import (
    DEFAULT_PROCESSED_DATA_ROOT,
    PROCESSED_FIVE_MINUTE_SCHEMA,
    ProcessedFiveMinuteStore,
    ProcessedPersistenceResult,
)
from spy_research.bars.validation import (
    ProcessedFiveMinuteValidator,
    ProcessedSessionStats,
    ProcessedValidationIssue,
    ProcessedValidationReport,
)

__all__ = [
    "AggregationError",
    "AggregationResult",
    "BucketIntegrityError",
    "DEFAULT_PROCESSED_DATA_ROOT",
    "FiveMinuteAggregationService",
    "FiveMinuteBar",
    "FiveMinuteBuildResult",
    "FiveMinuteBuildService",
    "PROCESSED_FIVE_MINUTE_SCHEMA",
    "ProcessedDataConflictError",
    "ProcessedDataCorruptionError",
    "ProcessedDataError",
    "ProcessedDataScopeError",
    "ProcessedDataWriteError",
    "ProcessedFiveMinuteStore",
    "ProcessedFiveMinuteValidator",
    "ProcessedPersistenceResult",
    "ProcessedSessionStats",
    "ProcessedValidationGateError",
    "ProcessedValidationIssue",
    "ProcessedValidationReport",
    "RawDataValidationGateError",
    "SessionAggregationSummary",
    "aggregate_rth_1m_to_5m",
]
