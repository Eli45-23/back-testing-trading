"""Composition service for validated aggregate, persist, and reconcile flow."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from spy_research.bars.aggregation import FiveMinuteAggregationService
from spy_research.bars.models import AggregationResult
from spy_research.bars.store import (
    ProcessedFiveMinuteStore,
    ProcessedPersistenceResult,
)
from spy_research.bars.validation import (
    ProcessedFiveMinuteValidator,
    ProcessedValidationReport,
)
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore


class ProcessedValidationGateError(ValueError):
    """Processed output failed validation after persistence."""

    def __init__(self, report: ProcessedValidationReport) -> None:
        self.report = report
        super().__init__(
            "Processed five-minute validation failed "
            f"({report.error_count} errors)"
        )


class FiveMinuteBuildResult(BaseModel):
    """Complete result of one local processed-data build."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    aggregation: AggregationResult
    persistence: ProcessedPersistenceResult
    validation: ProcessedValidationReport


class FiveMinuteBuildService:
    """Compose existing Stage 1 and Stage 2 components without duplication."""

    def __init__(
        self,
        config: ResearchConfig,
        raw_store: RawBarStore,
        processed_store: ProcessedFiveMinuteStore,
    ) -> None:
        self._config = config
        self._raw_store = raw_store
        self._processed_store = processed_store

    def build(self, *, start: date, end: date) -> FiveMinuteBuildResult:
        aggregation = FiveMinuteAggregationService(
            self._config,
            self._raw_store,
        ).aggregate(start=start, end=end)
        persistence = self._processed_store.persist_bars(aggregation.bars)
        validation = ProcessedFiveMinuteValidator().validate_store(
            self._processed_store,
            start=start,
            end=end,
            reconcile=True,
            config=self._config,
            raw_store=self._raw_store,
        )
        if not validation.passed:
            raise ProcessedValidationGateError(validation)
        return FiveMinuteBuildResult(
            aggregation=aggregation,
            persistence=persistence,
            validation=validation,
        )
