"""Read-only Stage 15.1 orchestration over the completed Stage 15 population."""

from __future__ import annotations

from datetime import date
from hashlib import sha256

from spy_research.attribution.exclusion_analysis import analyze_exclusions
from spy_research.attribution.exclusion_models import ExclusionValidationReport
from spy_research.attribution.service import BaseShortAttributionService
from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.market import XNYSCalendar


class NegativeConditionExclusionService:
    """Reconcile Stage 15, then evaluate only the frozen exclusion universe."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
        *,
        calendar: XNYSCalendar | None = None,
    ) -> None:
        self._stage15 = BaseShortAttributionService(
            config, processed_store, raw_store, calendar=calendar
        )

    def calculate(self, *, start: date, end: date) -> ExclusionValidationReport:
        stage15, observations = self._stage15.calculate_with_observations(
            start=start, end=end
        )
        stage15_hash = sha256(
            stage15.model_dump_json().encode("utf-8")
        ).hexdigest()
        return analyze_exclusions(
            observations,
            stage15,
            source_stage15_report_hash=stage15_hash,
        )
