"""Stage 15 outcome-blind BASE_SHORT attribution research."""

from spy_research.attribution.analysis import analyze_base_short_attribution
from spy_research.attribution.models import (
    AttributionClassification,
    AttributionGroup,
    AttributionObservation,
    AttributionReport,
)
from spy_research.attribution.service import BaseShortAttributionService
from spy_research.attribution.reporting import render_attribution_markdown
from spy_research.attribution.exclusion_models import ExclusionValidationReport
from spy_research.attribution.exclusion_reporting import render_exclusion_markdown
from spy_research.attribution.exclusion_service import NegativeConditionExclusionService
from spy_research.attribution.oos_models import OOSValidationReport, frozen_oos_design
from spy_research.attribution.oos_reporting import render_oos_markdown
from spy_research.attribution.oos_service import (
    DEFAULT_OOS_PROCESSED_DATA_ROOT,
    DEFAULT_OOS_RAW_DATA_ROOT,
    OOSExclusionValidationService,
)

__all__ = [
    "AttributionClassification",
    "AttributionGroup",
    "AttributionObservation",
    "AttributionReport",
    "BaseShortAttributionService",
    "analyze_base_short_attribution",
    "render_attribution_markdown",
    "ExclusionValidationReport",
    "NegativeConditionExclusionService",
    "render_exclusion_markdown",
    "OOSValidationReport",
    "OOSExclusionValidationService",
    "frozen_oos_design",
    "render_oos_markdown",
    "DEFAULT_OOS_RAW_DATA_ROOT",
    "DEFAULT_OOS_PROCESSED_DATA_ROOT",
]
