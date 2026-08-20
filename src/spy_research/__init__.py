"""SPY strategy research package."""

from spy_research.config import (
    AlpacaEnvironment,
    AppConfig,
    ResearchConfig,
    load_research_config,
    load_settings,
)
from spy_research.research_run import ResearchRun, RunStatus
from spy_research.version import get_version

__all__ = [
    "AlpacaEnvironment",
    "AppConfig",
    "ResearchConfig",
    "ResearchRun",
    "RunStatus",
    "load_research_config",
    "load_settings",
]

__version__ = get_version()
