"""Read-only Stage 13.3 composition over the accepted Stage 13.2 report."""

from __future__ import annotations

from datetime import date

from spy_research.bars.store import ProcessedFiveMinuteStore
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.execution.classification import classify_execution_variants
from spy_research.execution.classification_models import (
    ExecutionClassificationInputError,
    ExecutionVariantClassificationReport,
)
from spy_research.execution.exit_models import exit_model_comparison_hash
from spy_research.execution.exit_service import ExitModelComparisonService
from spy_research.execution.models import fixed_risk_simulation_hash


ACCEPTED_STAGE13_2_HASH = (
    "fd4378d75ca39e56d55b80c68f7e38e24b73f2bd946074fbc0ce525c64a3d0b2"
)
ACCEPTED_STAGE13_1_HASH = (
    "b25a8e32756257d785316902259b8f6be7db384eb18f32c82c374a36737ec1ff"
)


class ExecutionVariantClassificationService:
    """Project statistical records, then apply only frozen mechanical gates."""

    def __init__(
        self,
        config: ResearchConfig,
        processed_store: ProcessedFiveMinuteStore,
        raw_store: RawBarStore,
    ) -> None:
        self._source = ExitModelComparisonService(config, processed_store, raw_store)

    def calculate(
        self, *, start: date, end: date
    ) -> ExecutionVariantClassificationReport:
        source = self._source.calculate(start=start, end=end)
        source_hash = exit_model_comparison_hash(source)
        control_hash = fixed_risk_simulation_hash(source.stage13_1_control)
        if source_hash != ACCEPTED_STAGE13_2_HASH:
            raise ExecutionClassificationInputError(
                "accepted Stage 13.2 deterministic hash changed"
            )
        if control_hash != ACCEPTED_STAGE13_1_HASH:
            raise ExecutionClassificationInputError(
                "accepted Stage 13.1 deterministic hash changed"
            )
        report = classify_execution_variants(
            start_date=start,
            end_date=end,
            statistics=source.statistics,
            bootstrap_uncertainty=source.bootstrap_uncertainty,
            source_stage13_2_hash=source_hash,
            source_stage13_1_hash=control_hash,
        )
        if report.handoff.robust_candidates:
            raise ExecutionClassificationInputError(
                "unexpected robust candidate in the accepted Stage 13.2 sample"
            )
        return report
