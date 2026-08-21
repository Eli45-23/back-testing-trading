"""Local command-line utilities for the research foundation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

import yaml
from pydantic import ValidationError

from spy_research.alpaca import AlpacaDataClient, HistoricalStockDataService
from spy_research.alpaca.errors import AlpacaDataError
from spy_research.bars import (
    AggregationError,
    AggregationResult,
    DEFAULT_PROCESSED_DATA_ROOT,
    FiveMinuteAggregationService,
    FiveMinuteBuildResult,
    FiveMinuteBuildService,
    ProcessedDataError,
    ProcessedFiveMinuteStore,
    ProcessedFiveMinuteValidator,
    ProcessedValidationGateError,
    ProcessedValidationReport,
)
from spy_research.config import DEFAULT_CONFIG_PATH, load_research_config, load_settings
from spy_research.data.errors import RawDataError
from spy_research.data.raw_store import DEFAULT_RAW_DATA_ROOT, RawBarStore
from spy_research.data.validation import DataValidationReport, RawDataValidator
from spy_research.events import (
    EmaCrossCalculationResult,
    EmaCrossDirection,
    EmaCrossEventService,
    EventContextAlignmentError,
)
from spy_research.indicators import (
    AtrCalculationResult,
    AtrIndicatorService,
    EmaCalculationResult,
    EmaIndicatorService,
    EmaSeparationCalculationResult,
    EmaSeparationIndicatorService,
    IndicatorInputValidationError,
    IndicatorSequenceError,
    VwapCalculationResult,
    VwapIndicatorService,
)
from spy_research.interactions import (
    AtrToleranceInputError,
    AtrToleranceResult,
    AtrToleranceService,
    BreakFollowThroughResult,
    BreakFollowThroughService,
    FollowThroughInputError,
    ImmediateState,
    InteractionInputError,
    InteractionType,
    LevelInteractionResult,
    LevelInteractionService,
    LevelType,
    LiquiditySweepResult,
    LiquiditySweepService,
    RetestState,
    SweepInputError,
    SweepType,
)
from spy_research.levels import (
    OpeningFiveMinuteLevelsResult,
    OpeningFiveMinuteLevelsService,
    OpeningRangeLevelError,
    PremarketLevelError,
    PremarketLevelsResult,
    PremarketLevelsService,
    PreviousDayLevelError,
    PreviousDayLevelsResult,
    PreviousDayLevelsService,
)
from spy_research.market import MarketSessionClassifier, SessionSummary, SessionType
from spy_research.outcomes import (
    EmaCrossOutcomeContextResult,
    EmaCrossOutcomeContextService,
    OutcomeInputValidationError,
    OppositeCrossSequenceError,
    OutcomeSequenceError,
)
from spy_research.research_run import ResearchRun
from spy_research.research_stats import (
    Phase1CrossStatistics,
    Phase1CrossStatisticsService,
    StatisticsSequenceError,
)
from spy_research.strategy import (
    BasePriceActionResult,
    BasePriceActionService,
    BaseSetupInputError,
    BaseSetupStatus,
    BaseStatisticsInputError,
    BaseStrategyGroupDimension,
    BaseStrategyStatistics,
    BaseStrategyStatisticsService,
    ConfirmationType,
    EntryStatus,
    SetupOutcomeInputError,
    SetupOutcomeResult,
    SetupOutcomeService,
    SetupDirection,
)
from spy_research.strategy.comparisons import (
    CombinedContextInputError,
    CombinedContextMatrixResult,
    CombinedContextMatrixService,
    EmaAlignmentComparisonResult,
    EmaAlignmentComparisonService,
    Ema9VwapAlignmentComparisonResult,
    Ema9VwapAlignmentComparisonService,
    Ema9VwapComparisonInputError,
    Ema9VwapCrossContextComparisonResult,
    Ema9VwapCrossContextComparisonService,
    Ema9VwapCrossInputError,
    Ema20VwapAlignmentComparisonResult,
    Ema20VwapAlignmentComparisonService,
    Ema20VwapComparisonInputError,
    Ema20VwapCrossContextComparisonResult,
    Ema20VwapCrossContextComparisonService,
    Ema20VwapCrossInputError,
    EmaComparisonInputError,
    EmaCrossContextComparisonResult,
    EmaCrossContextComparisonService,
    EmaCrossContextInputError,
    VwapAlignmentComparisonResult,
    VwapAlignmentComparisonService,
    VwapComparisonInputError,
)


def parse_iso_date(value: str) -> date:
    """Parse a CLI date with a concise validation error."""

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a date in YYYY-MM-DD format") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spy-research",
        description="Local foundation utilities for SPY research.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_check = subparsers.add_parser(
        "config-check",
        help="validate the local non-secret research configuration",
    )
    config_check.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )

    run_manifest = subparsers.add_parser(
        "run-manifest",
        help="create an offline reproducibility manifest without downloading data",
    )
    run_manifest.add_argument("--start", type=parse_iso_date, required=True)
    run_manifest.add_argument("--end", type=parse_iso_date, required=True)
    run_manifest.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )

    fetch_bars = subparsers.add_parser(
        "fetch-bars",
        help="fetch raw SPY 1-minute SIP bars without persisting them",
    )
    fetch_bars.add_argument("--start", type=parse_iso_date, required=True)
    fetch_bars.add_argument("--end", type=parse_iso_date, required=True)
    fetch_bars.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    fetch_bars.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds (default: 10)",
    )

    download_bars = subparsers.add_parser(
        "download-bars",
        help="fetch and persist raw SPY 1-minute SIP bars as Parquet",
    )
    download_bars.add_argument("--start", type=parse_iso_date, required=True)
    download_bars.add_argument("--end", type=parse_iso_date, required=True)
    download_bars.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    download_bars.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root (default: data/raw)",
    )
    download_bars.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds (default: 10)",
    )

    session_summary = subparsers.add_parser(
        "session-summary",
        help="summarize locally stored bars by authoritative XNYS session",
    )
    session_summary.add_argument("--start", type=parse_iso_date, required=True)
    session_summary.add_argument("--end", type=parse_iso_date, required=True)
    session_summary.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    session_summary.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root (default: data/raw)",
    )

    validate_data = subparsers.add_parser(
        "validate-data",
        help="validate locally stored raw bars without modifying them",
    )
    validate_data.add_argument("--start", type=parse_iso_date, required=True)
    validate_data.add_argument("--end", type=parse_iso_date, required=True)
    validate_data.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    validate_data.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root (default: data/raw)",
    )
    validate_data.add_argument(
        "--json",
        action="store_true",
        help="emit the complete machine-readable validation report",
    )

    aggregate_bars = subparsers.add_parser(
        "aggregate-bars",
        help="validate and aggregate local RTH one-minute bars in memory",
    )
    aggregate_bars.add_argument("--start", type=parse_iso_date, required=True)
    aggregate_bars.add_argument("--end", type=parse_iso_date, required=True)
    aggregate_bars.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    aggregate_bars.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root (default: data/raw)",
    )

    build_5m = subparsers.add_parser(
        "build-5m",
        help="build, persist, validate, and reconcile local RTH five-minute bars",
    )
    build_5m.add_argument("--start", type=parse_iso_date, required=True)
    build_5m.add_argument("--end", type=parse_iso_date, required=True)
    build_5m.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    build_5m.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root (default: data/raw)",
    )
    build_5m.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )

    validate_5m = subparsers.add_parser(
        "validate-5m",
        help="validate processed RTH five-minute bars without writing",
    )
    validate_5m.add_argument("--start", type=parse_iso_date, required=True)
    validate_5m.add_argument("--end", type=parse_iso_date, required=True)
    validate_5m.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    validate_5m.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root used for reconciliation (default: data/raw)",
    )
    validate_5m.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )
    validate_5m.add_argument(
        "--no-reconcile",
        action="store_true",
        help="validate processed bars without raw re-aggregation comparison",
    )
    validate_5m.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable processed validation report",
    )

    calculate_ema = subparsers.add_parser(
        "calculate-ema",
        help="calculate session-reset EMA9/EMA20 from local processed bars",
    )
    calculate_ema.add_argument("--start", type=parse_iso_date, required=True)
    calculate_ema.add_argument("--end", type=parse_iso_date, required=True)
    calculate_ema.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    calculate_ema.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root used for reconciliation (default: data/raw)",
    )
    calculate_ema.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )

    calculate_vwap = subparsers.add_parser(
        "calculate-vwap",
        help="calculate daily-reset RTH VWAP from local processed bars",
    )
    calculate_vwap.add_argument("--start", type=parse_iso_date, required=True)
    calculate_vwap.add_argument("--end", type=parse_iso_date, required=True)
    calculate_vwap.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    calculate_vwap.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root used for reconciliation (default: data/raw)",
    )
    calculate_vwap.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )

    calculate_atr = subparsers.add_parser(
        "calculate-atr",
        help="calculate daily-reset Wilder ATR14 from local processed bars",
    )
    calculate_atr.add_argument("--start", type=parse_iso_date, required=True)
    calculate_atr.add_argument("--end", type=parse_iso_date, required=True)
    calculate_atr.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    calculate_atr.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root used for reconciliation (default: data/raw)",
    )
    calculate_atr.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )

    calculate_separation = subparsers.add_parser(
        "calculate-ema-separation",
        help="derive raw EMA9/EMA20 separation metrics from local bars",
    )
    calculate_separation.add_argument("--start", type=parse_iso_date, required=True)
    calculate_separation.add_argument("--end", type=parse_iso_date, required=True)
    calculate_separation.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    calculate_separation.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root used for reconciliation (default: data/raw)",
    )
    calculate_separation.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )

    detect_crosses = subparsers.add_parser(
        "detect-ema-crosses",
        help="detect completed-candle EMA9/EMA20 crosses from local bars",
    )
    detect_crosses.add_argument("--start", type=parse_iso_date, required=True)
    detect_crosses.add_argument("--end", type=parse_iso_date, required=True)
    detect_crosses.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    detect_crosses.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw data root used for reconciliation (default: data/raw)",
    )
    detect_crosses.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed data root (default: data/processed)",
    )

    calculate_outcomes = subparsers.add_parser(
        "calculate-cross-outcomes",
        help="calculate same-session future 1-minute MFE/MAE for EMA crosses",
    )
    calculate_outcomes.add_argument("--start", type=parse_iso_date, required=True)
    calculate_outcomes.add_argument("--end", type=parse_iso_date, required=True)
    calculate_outcomes.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    calculate_outcomes.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    calculate_outcomes.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    cross_stats = subparsers.add_parser(
        "cross-stats",
        help="report descriptive statistics for frozen EMA-cross outcomes",
    )
    cross_stats.add_argument("--start", type=parse_iso_date, required=True)
    cross_stats.add_argument("--end", type=parse_iso_date, required=True)
    cross_stats.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    cross_stats.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    cross_stats.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    previous_day_levels = subparsers.add_parser(
        "previous-day-levels",
        help="calculate look-ahead-safe PDH/PDL/PDC from local raw RTH bars",
    )
    previous_day_levels.add_argument("--start", type=parse_iso_date, required=True)
    previous_day_levels.add_argument("--end", type=parse_iso_date, required=True)
    previous_day_levels.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    previous_day_levels.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )

    premarket_levels = subparsers.add_parser(
        "premarket-levels",
        help="calculate finalized same-day PMH/PML from local raw bars",
    )
    premarket_levels.add_argument("--start", type=parse_iso_date, required=True)
    premarket_levels.add_argument("--end", type=parse_iso_date, required=True)
    premarket_levels.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    premarket_levels.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )

    opening_levels = subparsers.add_parser(
        "opening-5m-levels",
        help="calculate ORH5/ORL5 from validated Stage 2 RTH candles",
    )
    opening_levels.add_argument("--start", type=parse_iso_date, required=True)
    opening_levels.add_argument("--end", type=parse_iso_date, required=True)
    opening_levels.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    opening_levels.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute root used for reconciliation (default: data/raw)",
    )
    opening_levels.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    level_interactions = subparsers.add_parser(
        "level-interactions",
        help="classify completed 5m candle interactions with Stage 7 levels",
    )
    level_interactions.add_argument("--start", type=parse_iso_date, required=True)
    level_interactions.add_argument("--end", type=parse_iso_date, required=True)
    level_interactions.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    level_interactions.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    level_interactions.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    break_follow_through = subparsers.add_parser(
        "break-follow-through",
        help="classify immediate and exact-price retest context after close-throughs",
    )
    break_follow_through.add_argument("--start", type=parse_iso_date, required=True)
    break_follow_through.add_argument("--end", type=parse_iso_date, required=True)
    break_follow_through.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    break_follow_through.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    break_follow_through.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    sweep_patterns = subparsers.add_parser(
        "sweep-patterns",
        help="label strict reclaim patterns from Stage 8.1 wick-throughs",
    )
    sweep_patterns.add_argument("--start", type=parse_iso_date, required=True)
    sweep_patterns.add_argument("--end", type=parse_iso_date, required=True)
    sweep_patterns.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    sweep_patterns.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    sweep_patterns.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    atr_tolerance = subparsers.add_parser(
        "atr-tolerance",
        help="compare exact follow-through with fixed 0.10 event-ATR tolerance",
    )
    atr_tolerance.add_argument("--start", type=parse_iso_date, required=True)
    atr_tolerance.add_argument("--end", type=parse_iso_date, required=True)
    atr_tolerance.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    atr_tolerance.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    atr_tolerance.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    base_setups = subparsers.add_parser(
        "base-setups",
        help="qualify exact-price Stage 9.1 base price-action setup candidates",
    )
    base_setups.add_argument("--start", type=parse_iso_date, required=True)
    base_setups.add_argument("--end", type=parse_iso_date, required=True)
    base_setups.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    base_setups.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    base_setups.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    base_setup_outcomes = subparsers.add_parser(
        "base-setup-outcomes",
        help="calculate offline Stage 9.2 entry references and MFE/MAE",
    )
    base_setup_outcomes.add_argument("--start", type=parse_iso_date, required=True)
    base_setup_outcomes.add_argument("--end", type=parse_iso_date, required=True)
    base_setup_outcomes.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    base_setup_outcomes.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    base_setup_outcomes.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    base_strategy_stats = subparsers.add_parser(
        "base-strategy-stats",
        help="report the offline Stage 9.3 descriptive strategy baseline",
    )
    base_strategy_stats.add_argument("--start", type=parse_iso_date, required=True)
    base_strategy_stats.add_argument("--end", type=parse_iso_date, required=True)
    base_strategy_stats.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    base_strategy_stats.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    base_strategy_stats.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    compare_ema_alignment = subparsers.add_parser(
        "compare-ema-alignment",
        help="compare frozen Stage 9 outcomes by confirmation-bar EMA ordering",
    )
    compare_ema_alignment.add_argument("--start", type=parse_iso_date, required=True)
    compare_ema_alignment.add_argument("--end", type=parse_iso_date, required=True)
    compare_ema_alignment.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    compare_ema_alignment.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    compare_ema_alignment.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    compare_ema_cross_context = subparsers.add_parser(
        "compare-ema-cross-context",
        help="compare frozen Stage 9 outcomes by exact prior EMA-cross context",
    )
    compare_ema_cross_context.add_argument("--start", type=parse_iso_date, required=True)
    compare_ema_cross_context.add_argument("--end", type=parse_iso_date, required=True)
    compare_ema_cross_context.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    compare_ema_cross_context.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    compare_ema_cross_context.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    compare_vwap_alignment = subparsers.add_parser(
        "compare-vwap-alignment",
        help="compare frozen Stage 9 outcomes by confirmation-price/VWAP ordering",
    )
    compare_vwap_alignment.add_argument("--start", type=parse_iso_date, required=True)
    compare_vwap_alignment.add_argument("--end", type=parse_iso_date, required=True)
    compare_vwap_alignment.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="research YAML path (default: config/research.yaml)",
    )
    compare_vwap_alignment.add_argument(
        "--raw-data-root",
        type=Path,
        default=DEFAULT_RAW_DATA_ROOT,
        help="raw one-minute data root (default: data/raw)",
    )
    compare_vwap_alignment.add_argument(
        "--processed-data-root",
        type=Path,
        default=DEFAULT_PROCESSED_DATA_ROOT,
        help="processed five-minute data root (default: data/processed)",
    )

    compare_ema9_vwap = subparsers.add_parser(
        "compare-ema9-vwap-alignment",
        help="compare frozen Stage 9 outcomes by confirmation-row EMA9/VWAP ordering",
    )
    compare_ema9_vwap.add_argument("--start", type=parse_iso_date, required=True)
    compare_ema9_vwap.add_argument("--end", type=parse_iso_date, required=True)
    compare_ema9_vwap.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    compare_ema9_vwap.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    compare_ema9_vwap.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    compare_ema9_vwap_cross = subparsers.add_parser(
        "compare-ema9-vwap-cross-context",
        help="compare frozen outcomes by exact prior EMA9/VWAP cross context",
    )
    compare_ema9_vwap_cross.add_argument("--start", type=parse_iso_date, required=True)
    compare_ema9_vwap_cross.add_argument("--end", type=parse_iso_date, required=True)
    compare_ema9_vwap_cross.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    compare_ema9_vwap_cross.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    compare_ema9_vwap_cross.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    compare_ema20_vwap = subparsers.add_parser(
        "compare-ema20-vwap-alignment",
        help="compare frozen Stage 9 outcomes by confirmation-row EMA20/VWAP ordering",
    )
    compare_ema20_vwap.add_argument("--start", type=parse_iso_date, required=True)
    compare_ema20_vwap.add_argument("--end", type=parse_iso_date, required=True)
    compare_ema20_vwap.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    compare_ema20_vwap.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    compare_ema20_vwap.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    compare_ema20_vwap_cross = subparsers.add_parser(
        "compare-ema20-vwap-cross-context",
        help="compare frozen outcomes by exact prior EMA20/VWAP cross context",
    )
    compare_ema20_vwap_cross.add_argument("--start", type=parse_iso_date, required=True)
    compare_ema20_vwap_cross.add_argument("--end", type=parse_iso_date, required=True)
    compare_ema20_vwap_cross.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    compare_ema20_vwap_cross.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    compare_ema20_vwap_cross.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    combined_context = subparsers.add_parser(
        "compare-combined-context-matrix",
        help="reconcile Stage 10.1-10.7 context and unchanged Stage 9 outcomes",
    )
    combined_context.add_argument("--start", type=parse_iso_date, required=True)
    combined_context.add_argument("--end", type=parse_iso_date, required=True)
    combined_context.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    combined_context.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    combined_context.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run an offline foundation command and return its process exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "config-check":
        try:
            config = load_research_config(args.config)
        except (OSError, ValueError, yaml.YAMLError, ValidationError) as exc:
            print(f"Configuration invalid: {exc}", file=sys.stderr)
            return 1

        print(
            "Configuration valid: "
            f"{config.symbol}, Alpaca {config.data.feed}, "
            f"{config.bars.research_timeframe} research bars"
        )
        return 0

    if args.command == "run-manifest":
        try:
            config = load_research_config(args.config)
            run = ResearchRun.create(
                config,
                start_date=args.start,
                end_date=args.end,
            )
        except (OSError, ValueError, yaml.YAMLError, ValidationError) as exc:
            print(f"Unable to create run manifest: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(run.to_manifest(), indent=2, sort_keys=True))
        return 0
    if args.command == "session-summary":
        try:
            config = load_research_config(args.config)
            store = RawBarStore(config, root=args.data_root)
            bars = store.load_raw_bars(
                symbol=config.symbol,
                start=args.start,
                end=args.end,
                feed=config.data.feed,
                timeframe=config.data.timeframe,
            )
            classifier = MarketSessionClassifier()
            current = args.start
            while current <= args.end:
                _print_session_summary(classifier.summarize(current, bars))
                current += timedelta(days=1)
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to summarize sessions: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "validate-data":
        try:
            config = load_research_config(args.config)
            report = RawDataValidator().validate_raw_store(
                RawBarStore(config, root=args.data_root),
                symbol=config.symbol,
                start_date=args.start,
                end_date=args.end,
            )
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to validate raw data: {exc}", file=sys.stderr)
            return 2

        if args.json:
            print(report.model_dump_json(indent=2))
        else:
            _print_validation_report(report)
        return 0 if report.passed else 1

    if args.command == "aggregate-bars":
        try:
            config = load_research_config(args.config)
            result = FiveMinuteAggregationService(
                config,
                RawBarStore(config, root=args.data_root),
            ).aggregate(start=args.start, end=args.end)
        except AggregationError as exc:
            print(f"Unable to aggregate bars: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to aggregate bars: {exc}", file=sys.stderr)
            return 2

        _print_aggregation_result(result)
        return 0

    if args.command == "build-5m":
        try:
            config = load_research_config(args.config)
            result = FiveMinuteBuildService(
                config,
                RawBarStore(config, root=args.raw_data_root),
                ProcessedFiveMinuteStore(root=args.processed_data_root),
            ).build(start=args.start, end=args.end)
        except (AggregationError, ProcessedDataError, ProcessedValidationGateError) as exc:
            print(f"Unable to build five-minute data: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to build five-minute data: {exc}", file=sys.stderr)
            return 2
        _print_build_result(result)
        return 0

    if args.command == "validate-5m":
        try:
            config = load_research_config(args.config)
            report = ProcessedFiveMinuteValidator().validate_store(
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                start=args.start,
                end=args.end,
                reconcile=not args.no_reconcile,
                config=config,
                raw_store=RawBarStore(config, root=args.raw_data_root),
            )
        except (AggregationError, ProcessedDataError) as exc:
            print(f"Unable to validate five-minute data: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to validate five-minute data: {exc}", file=sys.stderr)
            return 2
        if args.json:
            print(report.model_dump_json(indent=2))
        else:
            _print_processed_validation(report)
        return 0 if report.passed else 1

    if args.command == "calculate-ema":
        try:
            config = load_research_config(args.config)
            result = EmaIndicatorService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            IndicatorInputValidationError,
            IndicatorSequenceError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to calculate EMA: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate EMA: {exc}", file=sys.stderr)
            return 2
        _print_ema_result(result)
        return 0

    if args.command == "calculate-vwap":
        try:
            config = load_research_config(args.config)
            result = VwapIndicatorService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            IndicatorInputValidationError,
            IndicatorSequenceError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to calculate VWAP: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate VWAP: {exc}", file=sys.stderr)
            return 2
        _print_vwap_result(result)
        return 0

    if args.command == "calculate-atr":
        try:
            config = load_research_config(args.config)
            result = AtrIndicatorService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            IndicatorInputValidationError,
            IndicatorSequenceError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to calculate ATR: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate ATR: {exc}", file=sys.stderr)
            return 2
        _print_atr_result(result)
        return 0

    if args.command == "calculate-ema-separation":
        try:
            config = load_research_config(args.config)
            result = EmaSeparationIndicatorService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            IndicatorInputValidationError,
            IndicatorSequenceError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to calculate EMA separation: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate EMA separation: {exc}", file=sys.stderr)
            return 2
        _print_ema_separation_result(result)
        return 0

    if args.command == "detect-ema-crosses":
        try:
            config = load_research_config(args.config)
            result = EmaCrossEventService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to detect EMA crosses: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to detect EMA crosses: {exc}", file=sys.stderr)
            return 2
        _print_ema_cross_result(result)
        return 0

    if args.command == "calculate-cross-outcomes":
        try:
            config = load_research_config(args.config)
            result = EmaCrossOutcomeContextService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            OutcomeInputValidationError,
            OutcomeSequenceError,
            OppositeCrossSequenceError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to calculate cross outcomes: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate cross outcomes: {exc}", file=sys.stderr)
            return 2
        _print_cross_outcomes(result)
        return 0

    if args.command == "cross-stats":
        try:
            config = load_research_config(args.config)
            result = Phase1CrossStatisticsService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            StatisticsSequenceError,
            OutcomeInputValidationError,
            OutcomeSequenceError,
            OppositeCrossSequenceError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            AggregationError,
            ProcessedDataError,
        ) as exc:
            print(f"Unable to calculate cross statistics: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate cross statistics: {exc}", file=sys.stderr)
            return 2
        _print_cross_statistics(result)
        return 0

    if args.command == "previous-day-levels":
        try:
            config = load_research_config(args.config)
            result = PreviousDayLevelsService(
                config,
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except PreviousDayLevelError as exc:
            print(f"Unable to calculate previous-day levels: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate previous-day levels: {exc}", file=sys.stderr)
            return 2
        _print_previous_day_levels(result)
        return 1 if result.missing_sources else 0

    if args.command == "premarket-levels":
        try:
            config = load_research_config(args.config)
            result = PremarketLevelsService(
                config,
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except PremarketLevelError as exc:
            print(f"Unable to calculate premarket levels: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate premarket levels: {exc}", file=sys.stderr)
            return 2
        _print_premarket_levels(result)
        return 1 if any(item.status != "AVAILABLE" for item in result.levels) else 0

    if args.command == "opening-5m-levels":
        try:
            config = load_research_config(args.config)
            result = OpeningFiveMinuteLevelsService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except OpeningRangeLevelError as exc:
            print(f"Unable to calculate opening 5-minute levels: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate opening 5-minute levels: {exc}", file=sys.stderr)
            return 2
        _print_opening_five_minute_levels(result)
        return 0

    if args.command == "level-interactions":
        try:
            config = load_research_config(args.config)
            result = LevelInteractionService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except InteractionInputError as exc:
            print(f"Unable to classify level interactions: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to classify level interactions: {exc}", file=sys.stderr)
            return 2
        _print_level_interactions(result)
        return 0

    if args.command == "break-follow-through":
        try:
            config = load_research_config(args.config)
            result = BreakFollowThroughService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (InteractionInputError, FollowThroughInputError) as exc:
            print(f"Unable to classify break follow-through: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to classify break follow-through: {exc}", file=sys.stderr)
            return 2
        _print_break_follow_through(result)
        return 0

    if args.command == "sweep-patterns":
        try:
            config = load_research_config(args.config)
            result = LiquiditySweepService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except SweepInputError as exc:
            print(f"Unable to classify sweep patterns: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to classify sweep patterns: {exc}", file=sys.stderr)
            return 2
        _print_sweep_patterns(result)
        return 0

    if args.command == "atr-tolerance":
        try:
            config = load_research_config(args.config)
            result = AtrToleranceService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            AtrToleranceInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
        ) as exc:
            print(f"Unable to compare ATR tolerance: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare ATR tolerance: {exc}", file=sys.stderr)
            return 2
        _print_atr_tolerance(result)
        return 0

    if args.command == "base-setups":
        try:
            config = load_research_config(args.config)
            result = BasePriceActionService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except BaseSetupInputError as exc:
            print(f"Unable to qualify base setups: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to qualify base setups: {exc}", file=sys.stderr)
            return 2
        _print_base_setups(result)
        return 0

    if args.command == "base-setup-outcomes":
        try:
            config = load_research_config(args.config)
            result = SetupOutcomeService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except SetupOutcomeInputError as exc:
            print(f"Unable to calculate base setup outcomes: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate base setup outcomes: {exc}", file=sys.stderr)
            return 2
        _print_base_setup_outcomes(result)
        return 0

    if args.command == "base-strategy-stats":
        try:
            config = load_research_config(args.config)
            result = BaseStrategyStatisticsService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (BaseStatisticsInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to calculate base strategy statistics: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to calculate base strategy statistics: {exc}", file=sys.stderr)
            return 2
        _print_base_strategy_statistics(result)
        return 0

    if args.command == "compare-ema-alignment":
        try:
            config = load_research_config(args.config)
            result = EmaAlignmentComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (EmaComparisonInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare EMA alignment: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare EMA alignment: {exc}", file=sys.stderr)
            return 2
        _print_ema_alignment_comparison(result)
        return 0

    if args.command == "compare-ema-cross-context":
        try:
            config = load_research_config(args.config)
            result = EmaCrossContextComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (EmaCrossContextInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare EMA cross context: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare EMA cross context: {exc}", file=sys.stderr)
            return 2
        _print_ema_cross_context_comparison(result)
        return 0

    if args.command == "compare-vwap-alignment":
        try:
            config = load_research_config(args.config)
            result = VwapAlignmentComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (VwapComparisonInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare VWAP alignment: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare VWAP alignment: {exc}", file=sys.stderr)
            return 2
        _print_vwap_alignment_comparison(result)
        return 0

    if args.command == "compare-ema9-vwap-alignment":
        try:
            config = load_research_config(args.config)
            result = Ema9VwapAlignmentComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (Ema9VwapComparisonInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare EMA9/VWAP alignment: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare EMA9/VWAP alignment: {exc}", file=sys.stderr)
            return 2
        _print_ema9_vwap_alignment_comparison(result)
        return 0

    if args.command == "compare-ema9-vwap-cross-context":
        try:
            config = load_research_config(args.config)
            result = Ema9VwapCrossContextComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (Ema9VwapCrossInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare EMA9/VWAP cross context: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare EMA9/VWAP cross context: {exc}", file=sys.stderr)
            return 2
        _print_ema9_vwap_cross_context_comparison(result)
        return 0

    if args.command == "compare-ema20-vwap-alignment":
        try:
            config = load_research_config(args.config)
            result = Ema20VwapAlignmentComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (Ema20VwapComparisonInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare EMA20/VWAP alignment: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare EMA20/VWAP alignment: {exc}", file=sys.stderr)
            return 2
        _print_ema20_vwap_alignment_comparison(result)
        return 0

    if args.command == "compare-ema20-vwap-cross-context":
        try:
            config = load_research_config(args.config)
            result = Ema20VwapCrossContextComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (Ema20VwapCrossInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare EMA20/VWAP cross context: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to compare EMA20/VWAP cross context: {exc}", file=sys.stderr)
            return 2
        _print_ema20_vwap_cross_context_comparison(result)
        return 0

    if args.command == "compare-combined-context-matrix":
        try:
            config = load_research_config(args.config)
            result = CombinedContextMatrixService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (CombinedContextInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to build combined context matrix: {exc}", file=sys.stderr)
            return 1
        except (
            BaseSetupInputError,
            IndicatorInputValidationError,
            IndicatorSequenceError,
            EventContextAlignmentError,
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to build combined context matrix: {exc}", file=sys.stderr)
            return 2
        _print_combined_context_matrix(result)
        return 0

    if args.command in {"fetch-bars", "download-bars"}:
        try:
            settings = load_settings(config_path=args.config)
            with AlpacaDataClient.from_environment(
                settings.alpaca,
                timeout=args.timeout,
            ) as client:
                result = HistoricalStockDataService(
                    client,
                    settings.research,
                ).fetch_stock_bars(start=args.start, end=args.end)
            persistence = None
            if args.command == "download-bars":
                persistence = RawBarStore(
                    settings.research,
                    root=args.data_root,
                ).persist_bars(result.bars)
        except (
            AlpacaDataError,
            RawDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            action = (
                "download and persist bars"
                if args.command == "download-bars"
                else "fetch bars"
            )
            print(f"Unable to {action}: {exc}", file=sys.stderr)
            return 1

        if persistence is not None:
            print(f"Symbol: {settings.research.symbol}")
            print(f"Requested: {args.start.isoformat()} → {args.end.isoformat()}")
            print(f"Downloaded: {len(result.bars)}")
            print(f"New bars stored: {persistence.new_bars}")
            print(f"Existing identical bars: {persistence.existing_identical}")
            print(f"Conflicts: {persistence.conflicts}")
            print(f"Partitions written: {persistence.partitions_written}")
            return 0

        first_timestamp = result.bars[0].timestamp.isoformat() if result.bars else "None"
        last_timestamp = result.bars[-1].timestamp.isoformat() if result.bars else "None"
        print(f"Symbol: {settings.research.symbol}")
        print(f"Feed: {settings.research.data.feed.upper()}")
        print(f"Timeframe: {settings.research.data.timeframe}")
        print(f"Bars received: {len(result.bars)}")
        print(f"First timestamp: {first_timestamp}")
        print(f"Last timestamp: {last_timestamp}")
        print(f"Pages fetched: {result.pages_fetched}")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


def _print_session_summary(summary: SessionSummary) -> None:
    session = summary.session
    print(f"Session: {session.session_date.isoformat()}")
    print(f"Trading day: {'yes' if session.is_trading_day else 'no'}")
    print(f"Open: {_format_timestamp(session.market_open)}")
    print(f"Close: {_format_timestamp(session.market_close)}")
    print(f"Early close: {'yes' if session.is_early_close else 'no'}")
    print(f"Total bars: {summary.total_bars}")
    for session_type in SessionType:
        print(f"{session_type.value} bars: {summary.counts[session_type]}")
    print(f"First RTH: {_format_timestamp(summary.first_rth)}")
    print(f"Last RTH: {_format_timestamp(summary.last_rth)}")
    print(f"First after-hours: {_format_timestamp(summary.first_after_hours)}")


def _format_timestamp(value: datetime | None) -> str:
    return value.isoformat() if value is not None else "None"


def _print_validation_report(report: DataValidationReport) -> None:
    print("SPY Raw Data Validation")
    print(f"{report.start_date.isoformat()} → {report.end_date.isoformat()}")
    print(f"Sessions expected: {report.expected_sessions}")
    print(f"Sessions present: {report.sessions_present}")
    print(f"Total bars: {report.total_bars}")
    print(f"RTH expected: {report.expected_rth_bars}")
    print(f"RTH observed: {report.observed_rth_bars}")
    print(f"RTH missing: {report.missing_rth_bars}")
    print(f"RTH extra: {report.extra_rth_bars}")
    print(f"Duplicate keys: {report.duplicate_keys}")
    print(f"Errors: {report.error_count}")
    print(f"Warnings: {report.warning_count}")
    print(f"Info: {report.info_count}")
    print(f"Status: {'PASS' if report.passed else 'FAIL'}")
    for issue in report.issues:
        print(f"[{issue.severity.value}] {issue.code}: {issue.message}")
        if issue.details:
            print(f"  Details: {json.dumps(issue.details, sort_keys=True)}")


def _print_aggregation_result(result: AggregationResult) -> None:
    print("SPY 5-Minute Aggregation")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    for session in result.sessions:
        print(f"Date: {session.session_date.isoformat()}")
        print(f"Raw RTH bars: {session.raw_rth_bars}")
        print(f"5-minute bars: {session.five_minute_bars}")
        print(f"First candle: {_format_new_york_time(session.first_timestamp)}")
        print(f"Last candle: {_format_new_york_time(session.last_timestamp)}")
    print(f"Total raw RTH bars: {result.raw_rth_bars}")
    print(f"Total 5-minute bars: {len(result.bars)}")
    print("Status: PASS")


def _format_new_york_time(value: datetime | None) -> str:
    if value is None:
        return "None"
    return value.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M %Z")


def _print_build_result(result: FiveMinuteBuildResult) -> None:
    aggregation = result.aggregation
    persistence = result.persistence
    report = result.validation
    print("SPY RTH 5-Minute Build")
    print(f"Sessions: {len(aggregation.sessions)}")
    print(f"Raw RTH bars: {aggregation.raw_rth_bars}")
    print(f"5-minute bars built: {len(aggregation.bars)}")
    print(f"New processed bars: {persistence.new_bars}")
    print(f"Existing identical: {persistence.existing_identical}")
    print(f"Conflicts: {persistence.conflicts}")
    print(f"Partitions written: {persistence.partitions_written}")
    print(f"Reconciliation errors: {report.reconciliation_errors}")
    print(f"Status: {'PASS' if report.passed else 'FAIL'}")


def _print_processed_validation(report: ProcessedValidationReport) -> None:
    print("SPY Processed 5-Minute Validation")
    print(f"Sessions expected: {report.sessions_expected}")
    print(f"Sessions present: {report.sessions_present}")
    print(f"Total bars: {report.total_bars}")
    print(f"Expected bars: {report.expected_bars}")
    print(f"Missing bars: {report.missing_bars}")
    print(f"Duplicate bars: {report.duplicate_bars}")
    print(f"Reconciliation errors: {report.reconciliation_errors}")
    print(f"Errors: {report.error_count}")
    print(f"Warnings: {report.warning_count}")
    print(f"Status: {'PASS' if report.passed else 'FAIL'}")


def _print_ema_result(result: EmaCalculationResult) -> None:
    print("SPY EMA Calculation")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    for session in result.sessions:
        print(f"Session: {session.session_date.isoformat()}")
        print(f"5-minute bars: {session.bars}")
        print(f"EMA9 valid rows: {session.ema9_valid_rows}")
        print(f"EMA20 valid rows: {session.ema20_valid_rows}")
        print(
            "EMA9 first valid: "
            f"{_format_new_york_time(session.first_ema9_timestamp)}"
        )
        print(
            "EMA20 first valid: "
            f"{_format_new_york_time(session.first_ema20_timestamp)}"
        )
    print(f"Total rows: {len(result.rows)}")
    print(f"Total EMA9 valid: {sum(row.ema9 is not None for row in result.rows)}")
    print(f"Total EMA20 valid: {sum(row.ema20 is not None for row in result.rows)}")
    print("Status: PASS")


def _print_vwap_result(result: VwapCalculationResult) -> None:
    print("SPY RTH VWAP")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    for session in result.sessions:
        print(f"Session: {session.session_date.isoformat()}")
        print(f"Bars: {session.bars}")
        print(f"VWAP valid rows: {session.valid_rows}")
        print(f"First VWAP: {session.first_vwap}")
        print(f"Final VWAP: {session.final_vwap}")
    print(f"Total rows: {len(result.rows)}")
    print(f"Total VWAP valid: {sum(row.vwap is not None for row in result.rows)}")
    print("Status: PASS")


def _print_atr_result(result: AtrCalculationResult) -> None:
    print("SPY ATR14")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    for session in result.sessions:
        print(f"Session: {session.session_date.isoformat()}")
        print(f"Bars: {session.bars}")
        print(f"ATR14 valid rows: {session.valid_rows}")
        print(
            "First ATR14: "
            f"{_format_new_york_time(session.first_valid_timestamp)}"
        )
        print(f"First ATR14 value: {session.first_atr14}")
        print(f"Final ATR14: {session.final_atr14}")
    print(f"Total rows: {len(result.rows)}")
    print(f"Total ATR14 valid: {sum(row.atr14 is not None for row in result.rows)}")
    print("Status: PASS")


def _print_ema_separation_result(result: EmaSeparationCalculationResult) -> None:
    print("SPY EMA Separation")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    for session in result.sessions:
        print(f"Session: {session.session_date.isoformat()}")
        print(f"Bars: {session.bars}")
        print(f"Valid separation rows: {session.separation_valid_rows}")
        print(
            "First separation: "
            f"{_format_new_york_time(session.first_separation_timestamp)}"
        )
        print(
            "First delta-1: "
            f"{_format_new_york_time(session.first_delta_1_timestamp)}"
        )
        print(
            "First delta-2: "
            f"{_format_new_york_time(session.first_delta_2_timestamp)}"
        )
        print(
            "First delta-3: "
            f"{_format_new_york_time(session.first_delta_3_timestamp)}"
        )
    print(f"Total rows: {len(result.rows)}")
    print(
        "Total valid separation: "
        f"{sum(row.signed_separation is not None for row in result.rows)}"
    )
    print("Status: PASS")


def _print_ema_cross_result(result: EmaCrossCalculationResult) -> None:
    bullish = sum(
        event.direction == EmaCrossDirection.BULLISH for event in result.events
    )
    bearish = sum(
        event.direction == EmaCrossDirection.BEARISH for event in result.events
    )
    print("SPY EMA Cross Events")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    print(f"Sessions: {len(result.sessions)}")
    print(f"Bullish crosses: {bullish}")
    print(f"Bearish crosses: {bearish}")
    print(f"Total crosses: {len(result.events)}")
    print("Time      Direction  Close  EMA9  EMA20  Signed separation  VWAP  ATR14")
    for event in result.events:
        time = event.timestamp.astimezone(ZoneInfo("America/New_York")).strftime(
            "%Y-%m-%d %H:%M %Z"
        )
        print(
            f"{time}  {event.direction.value}  {event.close}  {event.ema9}  "
            f"{event.ema20}  {event.signed_separation}  {event.vwap}  {event.atr14}"
        )
    print("Status: PASS")


def _print_cross_outcomes(result: EmaCrossOutcomeContextResult) -> None:
    base_result = result.base_result
    print("SPY EMA Cross MFE/MAE Outcomes")
    print(
        f"Range: {base_result.start_date.isoformat()} → "
        f"{base_result.end_date.isoformat()}"
    )
    print(f"Events: {len(result.outcomes)}")
    print(
        "Time  Direction  Ref  MFE5/MAE5  MFE15/MAE15  MFE30/MAE30  "
        "MFE60/MAE60  MFEEOD/MAEEOD  Complete 5/15/30/60/EOD  Next opposite/min"
    )
    for enriched in result.outcomes:
        outcome = enriched.outcome
        event = outcome.event
        time = event.timestamp.astimezone(ZoneInfo("America/New_York")).strftime(
            "%Y-%m-%d %H:%M %Z"
        )
        horizons = (
            outcome.five,
            outcome.fifteen,
            outcome.thirty,
            outcome.sixty,
            outcome.eod,
        )
        pairs = "  ".join(
            f"{item.excursion.mfe}/{item.excursion.mae}" for item in horizons
        )
        complete = "/".join("Y" if item.complete else "N" for item in horizons)
        opposite = enriched.opposite_cross
        next_cross = (
            f"{opposite.opposite_cross_timestamp.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M')}"
            f" {opposite.opposite_cross_direction.value}/{opposite.minutes_to_opposite_cross}"
            if opposite.opposite_cross_timestamp is not None
            and opposite.opposite_cross_direction is not None
            else "None"
        )
        print(
            f"{time}  {event.direction.value}  {outcome.reference_price}  "
            f"{pairs}  {complete}  {next_cross}"
        )
    print("Status: PASS")


def _format_percentage(value: Decimal | None) -> str:
    return f"{value.quantize(Decimal('0.01'))}%" if value is not None else "N/A"


def _print_cross_statistics(result: Phase1CrossStatistics) -> None:
    print("PHASE 1 EMA CROSS STATISTICS")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    print(
        f"Sample: n={result.total_n}  bullish={result.bullish_n}  "
        f"bearish={result.bearish_n}"
    )
    print(f"Percentiles: {result.percentile_method}")
    overall = next(group for group in result.groups if group.name == "ALL")
    print("Overall MFE/MAE")
    for horizon in overall.horizons:
        print(
            f"{horizon.horizon}: eligible={horizon.eligible_n} "
            f"excluded={horizon.excluded_incomplete_n}  "
            f"MFE mean/median/p25/p75={horizon.mfe.mean}/{horizon.mfe.median}/"
            f"{horizon.mfe.p25}/{horizon.mfe.p75}  "
            f"MAE mean/median={horizon.mae.mean}/{horizon.mae.median}"
        )
        print(
            "  Dollar hits: "
            + "  ".join(
                f">={item.threshold}:{item.reached_n}/{item.eligible_n}"
                f" ({_format_percentage(item.percentage)})"
                for item in horizon.dollar_thresholds
            )
        )
        print(
            f"  ATR hits (n={horizon.atr_eligible_n}, "
            f"excluded={horizon.atr_excluded_n}): "
            + "  ".join(
                f">={item.threshold}:{item.reached_n}/{item.eligible_n}"
                f" ({_format_percentage(item.percentage)})"
                for item in horizon.atr_thresholds
            )
        )
        relation = horizon.favorable_adverse
        print(
            f"  MFE>MAE={relation.mfe_greater}  equal={relation.equal}  "
            f"MFE<MAE={relation.mfe_less}"
        )
    print("Frozen context groups")
    print("Group  n  15m n/median MFE/MAE  30m n/median MFE/MAE  EOD n/median MFE/MAE")
    for group in result.groups:
        by_horizon = {item.horizon: item for item in group.horizons}
        fifteen = by_horizon["15m"]
        thirty = by_horizon["30m"]
        eod = by_horizon["EOD"]
        print(
            f"{group.name}  {group.total_n}  "
            f"{fifteen.eligible_n}/{fifteen.mfe.median}/{fifteen.mae.median}  "
            f"{thirty.eligible_n}/{thirty.mfe.median}/{thirty.mae.median}  "
            f"{eod.eligible_n}/{eod.mfe.median}/{eod.mae.median}"
        )
    separation = result.absolute_separation
    print(
        "Absolute separation: "
        f"n={separation.n} mean={separation.mean} median={separation.median} "
        f"p25={separation.p25} p75={separation.p75} "
        f"min={separation.minimum} max={separation.maximum}"
    )
    opposite = result.opposite_cross_timing
    print(
        "Opposite-cross timing: "
        f"with={opposite.with_opposite_n} without={opposite.without_opposite_n} "
        f"mean={opposite.minutes.mean} median={opposite.minutes.median} "
        f"p25={opposite.minutes.p25} p75={opposite.minutes.p75} "
        f"min={opposite.minutes.minimum} max={opposite.minutes.maximum}"
    )
    print(f"Data limitation: {result.small_sample_warning}")
    print("Status: PASS")


def _print_previous_day_levels(result: PreviousDayLevelsResult) -> None:
    print("SPY PREVIOUS-DAY LEVELS")
    print("Session     Source      PDH             PDL             PDC")
    for item in result.levels:
        print(
            f"{item.session_date.isoformat()}  {item.source_session_date.isoformat()}  "
            f"{item.pdh}  {item.pdl}  {item.pdc}"
        )
    if result.missing_sources:
        print("Missing source sessions:")
        for item in result.missing_sources:
            print(
                f"{item.session_date.isoformat()} requires "
                f"{item.source_session_date.isoformat()}: {item.reason}"
            )
        print("Status: INCOMPLETE")
    else:
        print("Status: PASS")


def _print_premarket_levels(result: PremarketLevelsResult) -> None:
    print("SPY PREMARKET LEVELS")
    print("Session     Bars  PMH             PML             Status")
    for item in result.levels:
        pmh = str(item.pmh) if item.pmh is not None else "N/A"
        pml = str(item.pml) if item.pml is not None else "N/A"
        print(
            f"{item.session_date.isoformat()}  {item.source_bar_count:>4}  "
            f"{pmh:<15} {pml:<15} {item.status}"
        )
    unavailable = sum(item.status != "AVAILABLE" for item in result.levels)
    print("Status: PASS" if unavailable == 0 else f"Status: INCOMPLETE ({unavailable})")


def _print_opening_five_minute_levels(
    result: OpeningFiveMinuteLevelsResult,
) -> None:
    print("SPY OPENING 5-MINUTE LEVELS")
    print("Session     ORH5            ORL5            Source  Available")
    timezone = ZoneInfo("America/New_York")
    for item in result.levels:
        source = item.source_timestamp.astimezone(timezone).strftime("%H:%M")
        available = item.available_from_timestamp.astimezone(timezone).strftime("%H:%M")
        print(
            f"{item.session_date.isoformat()}  {str(item.orh5):<15} "
            f"{str(item.orl5):<15} {source}   {available}"
        )
    print("Status: PASS")


def _print_level_interactions(result: LevelInteractionResult) -> None:
    print("SPY LEVEL INTERACTIONS")
    print(
        f"Eligible pairs: {result.eligible_pair_count}  "
        f"emitted: {len(result.interactions)}  "
        f"no interaction: {result.no_interaction_count}"
    )
    by_key = {
        (item.level_type, item.interaction_type): item.count for item in result.counts
    }
    print("Interaction summary")
    event_types = tuple(
        value for value in InteractionType if value is not InteractionType.NO_INTERACTION
    )
    for level_type in LevelType:
        rendered = "  ".join(
            f"{interaction_type.value}={by_key[(level_type, interaction_type)]}"
            for interaction_type in event_types
        )
        print(f"{level_type.value}: {rendered}")

    print("Emitted events")
    print("Date Time  Level Price Type  O/H/L/C  Prev  Above Below")
    timezone = ZoneInfo("America/New_York")
    for item in result.interactions:
        local = item.candle_timestamp.astimezone(timezone)
        previous = str(item.previous_close) if item.previous_close is not None else "N/A"
        print(
            f"{item.session_date.isoformat()} {local:%H:%M}  "
            f"{item.level_type.value} {item.level_price} "
            f"{item.interaction_type.value}  "
            f"{item.open}/{item.high}/{item.low}/{item.close}  "
            f"{previous}  {item.traded_above} {item.traded_below}"
        )
    print("Status: PASS")


def _print_break_follow_through(result: BreakFollowThroughResult) -> None:
    print("SPY BREAK FOLLOW-THROUGH")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"close-through seeds: {result.seed_count}"
    )
    immediate_counts = Counter(item.immediate.state for item in result.follow_through)
    retest_counts = Counter(item.retest.state for item in result.follow_through)
    print(
        "Immediate: "
        + "  ".join(
            f"{state.value}={immediate_counts[state]}" for state in ImmediateState
        )
    )
    print(
        "Retest: "
        + "  ".join(f"{state.value}={retest_counts[state]}" for state in RetestState)
    )
    print("Break rows")
    print(
        "Date Break Level Price Direction Next/Close Immediate "
        "Retest Offset Retest/OHLC Available"
    )
    timezone = ZoneInfo("America/New_York")
    for item in result.follow_through:
        next_time = (
            item.immediate.bar_timestamp.astimezone(timezone).strftime("%H:%M")
            if item.immediate.bar_timestamp is not None
            else "N/A"
        )
        next_close = (
            str(item.immediate.close) if item.immediate.close is not None else "N/A"
        )
        retest_time = (
            item.retest.timestamp.astimezone(timezone).strftime("%H:%M")
            if item.retest.timestamp is not None
            else "N/A"
        )
        retest_ohlc = (
            f"{item.retest.open}/{item.retest.high}/"
            f"{item.retest.low}/{item.retest.close}"
            if item.retest.timestamp is not None
            else "N/A"
        )
        offset = f"+{item.retest.bar_offset}" if item.retest.bar_offset else "N/A"
        break_time = item.break_timestamp.astimezone(timezone).strftime("%H:%M")
        print(
            f"{item.session_date.isoformat()} {break_time} "
            f"{item.level_type.value} {item.level_price} {item.break_direction.value} "
            f"{next_time}/{next_close} {item.immediate.state.value} "
            f"{item.retest.state.value} {offset} {retest_time}/{retest_ohlc} "
            f"{item.retest.available_bars}/3 "
            f"complete={item.retest.window_complete}"
        )
    print("Status: PASS")


def _print_sweep_patterns(result: LiquiditySweepResult) -> None:
    print("SPY LIQUIDITY-SWEEP PATTERNS")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"wick seeds: {result.seed_count}"
    )
    counts = Counter(item.sweep_type for item in result.patterns)
    print(
        "Patterns: "
        + "  ".join(f"{state.value}={counts[state]}" for state in SweepType)
    )
    for state in (SweepType.SWEEP_ABOVE, SweepType.SWEEP_BELOW):
        excursions = sorted(
            item.excursion_amount
            for item in result.patterns
            if item.sweep_type is state
        )
        if excursions:
            print(
                f"{state.value} excursion: count={len(excursions)} "
                f"min={excursions[0]} median={median(excursions)} "
                f"max={excursions[-1]}"
            )
    print("Pattern rows")
    print(
        "Date Time Level Price Source Pattern O/H/L/C "
        "Excursion Reclaim Above Below"
    )
    timezone = ZoneInfo("America/New_York")
    for item in result.patterns:
        local = item.candle_timestamp.astimezone(timezone)
        print(
            f"{item.session_date.isoformat()} {local:%H:%M} "
            f"{item.level_type.value} {item.level_price} "
            f"{item.source_interaction_type.value} {item.sweep_type.value} "
            f"{item.open}/{item.high}/{item.low}/{item.close} "
            f"{item.excursion_amount} {item.reclaim_distance} "
            f"{item.traded_above} {item.traded_below}"
        )
    print("Status: PASS")


def _print_atr_tolerance(result: AtrToleranceResult) -> None:
    print("SPY 0.10 EVENT-ATR FOLLOW-THROUGH COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"seeds: {result.seed_count}  ATR available: {result.atr_available_count}  "
        f"ATR unavailable: {result.atr_unavailable_count}"
    )
    immediate = Counter(
        (item.exact_immediate_state.value, item.tolerant_immediate_state.value)
        for item in result.comparisons
    )
    retest = Counter(
        (item.exact_retest_state.value, item.tolerant_retest_state.value)
        for item in result.comparisons
    )
    print("Immediate transitions")
    for (exact, tolerant), count in sorted(immediate.items()):
        print(f"{exact} -> {tolerant}: {count}")
    print("Retest transitions")
    for (exact, tolerant), count in sorted(retest.items()):
        print(f"{exact} -> {tolerant}: {count}")
    print("Comparison rows")
    print(
        "Date Break Level Direction ATR/Tolerance ExactImmediate/Tolerant "
        "ExactRetest/Tolerant Retest Reclassified(I/R)"
    )
    timezone = ZoneInfo("America/New_York")
    for item in result.comparisons:
        break_time = item.break_timestamp.astimezone(timezone).strftime("%H:%M")
        atr = str(item.event_atr) if item.event_atr is not None else "N/A"
        tolerance = (
            str(item.tolerance_amount) if item.tolerance_amount is not None else "N/A"
        )
        retest_time = (
            item.retest_timestamp.astimezone(timezone).strftime("%H:%M")
            if item.retest_timestamp is not None
            else "N/A"
        )
        offset = f"+{item.retest_bar_offset}" if item.retest_bar_offset else "N/A"
        print(
            f"{item.session_date.isoformat()} {break_time} "
            f"{item.level_type.value}@{item.level_price} {item.break_direction.value} "
            f"{atr}/{tolerance} "
            f"{item.exact_immediate_state.value}/"
            f"{item.tolerant_immediate_state.value} "
            f"{item.exact_retest_state.value}/"
            f"{item.tolerant_retest_state.value} "
            f"{retest_time}/{offset} "
            f"{item.immediate_reclassified}/{item.retest_reclassified}"
        )
    print("Status: PASS")


def _print_base_setups(result: BasePriceActionResult) -> None:
    print("SPY BASE EXACT-PRICE SETUP CANDIDATES")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"seeds: {result.seed_count}  confirmed: {result.confirmed_count}  "
        f"non-confirmed: {result.non_confirmed_count}"
    )
    confirmed = tuple(
        item
        for item in result.candidates
        if item.status is BaseSetupStatus.CONFIRMED
    )
    directions = Counter(item.direction for item in confirmed)
    confirmations = Counter(item.confirmation_type for item in confirmed)
    print(
        "Directions: "
        + "  ".join(
            f"{direction.value}={directions[direction]}"
            for direction in SetupDirection
        )
    )
    print(
        "Confirmations: "
        + "  ".join(
            f"{confirmation.value}={confirmations[confirmation]}"
            for confirmation in ConfirmationType
        )
    )
    print("Candidate rows")
    print(
        "Date Break Level Direction Immediate Retest Status "
        "Confirmation ConfirmBar KnownAt Executable"
    )
    timezone = ZoneInfo("America/New_York")
    for item in result.candidates:
        break_time = item.break_timestamp.astimezone(timezone).strftime("%H:%M")
        confirmation_time = (
            item.confirmation_bar_timestamp.astimezone(timezone).strftime("%H:%M")
            if item.confirmation_bar_timestamp is not None
            else "N/A"
        )
        known_at = (
            item.signal_known_at.astimezone(timezone).strftime("%H:%M")
            if item.signal_known_at is not None
            else "N/A"
        )
        confirmation = (
            item.confirmation_type.value
            if item.confirmation_type is not None
            else "N/A"
        )
        print(
            f"{item.session_date.isoformat()} {break_time} "
            f"{item.level_type.value}@{item.level_price} {item.direction.value} "
            f"{item.exact_immediate_state.value} {item.exact_retest_state.value} "
            f"{item.status.value} {confirmation} {confirmation_time} {known_at} "
            f"{item.same_session_executable}"
        )
    print("Status: PASS")


def _print_base_setup_outcomes(result: SetupOutcomeResult) -> None:
    print("SPY BASE SETUP ENTRY REFERENCES AND EXCURSIONS")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"confirmed: {result.confirmed_setup_count}  "
        f"entries: {result.available_entry_count}  "
        f"session-end unavailable: {result.session_end_unavailable_count}  "
        f"missing: {result.missing_entry_count}"
    )
    print("Completeness")
    for attribute, label in (
        ("five", "5m"),
        ("fifteen", "15m"),
        ("thirty", "30m"),
        ("sixty", "60m"),
        ("eod", "EOD"),
    ):
        values = tuple(
            getattr(item, attribute)
            for item in result.outcomes
            if getattr(item, attribute) is not None
        )
        complete = sum(value.complete for value in values)
        print(f"{label}: complete={complete} incomplete={len(values) - complete}")
    print("Rows")
    print("Date Level Direction KnownAt EntryAt EntryOpen Delay Status 5m 15m 30m 60m EOD")
    timezone = ZoneInfo("America/New_York")
    for item in result.outcomes:
        setup = item.setup
        entry = item.entry_reference
        known_at = entry.signal_known_at.astimezone(timezone).strftime("%H:%M")
        if entry.entry_status is not EntryStatus.AVAILABLE:
            print(
                f"{setup.session_date.isoformat()} {setup.level_type.value} "
                f"{setup.direction.value} {known_at} N/A N/A N/A "
                f"{entry.entry_status.value} N/A N/A N/A N/A N/A"
            )
            continue
        assert entry.entry_reference_timestamp is not None
        entry_at = entry.entry_reference_timestamp.astimezone(timezone).strftime("%H:%M")
        horizon_text = []
        for outcome in (item.five, item.fifteen, item.thirty, item.sixty, item.eod):
            assert outcome is not None
            marker = "C" if outcome.complete else "I"
            horizon_text.append(f"{outcome.mfe}/{outcome.mae}/{marker}")
        print(
            f"{setup.session_date.isoformat()} {setup.level_type.value} "
            f"{setup.direction.value} {known_at} {entry_at} "
            f"{entry.entry_reference_price} {entry.entry_delay_minutes} "
            f"{entry.entry_status.value} {' '.join(horizon_text)}"
        )
    print("Reference: deterministic underlying 1-minute open; not a guaranteed live fill")
    print("MFE/MAE: descriptive excursions, not realized P/L")
    print("Status: PASS")


def _format_base_stat(value: Decimal | None) -> str:
    return f"{value:.4f}" if value is not None else "N/A"


def _print_base_strategy_statistics(result: BaseStrategyStatistics) -> None:
    print("SPY BASE PRICE-ACTION DESCRIPTIVE BASELINE")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"seeds: {result.break_seed_count}  confirmed: {result.confirmed_count}  "
        f"non-confirmed: {result.non_confirmed_count}  "
        f"executable: {result.executable_count}  "
        f"session-end unavailable: {result.session_end_unavailable_count}  "
        f"missing: {result.missing_entry_count}"
    )
    print(
        f"Confirmed types: IMMEDIATE_HOLD={result.immediate_hold_confirmed_count}  "
        f"RETEST_HOLD={result.retest_hold_confirmed_count}"
    )
    print(
        "Dimension Group Horizon Complete Incomplete "
        "MFE(mean/median/min/max) MAE(mean/median/min/max) "
        "Balance(mean/median) Compare(MFE>MAE/=/MFE<MAE) Ratio(n/zero/median)"
    )
    for group in result.groups:
        if group.dimension is not BaseStrategyGroupDimension.OVERALL:
            print(f"[{group.dimension.value}] {group.name} executable={group.executable_n}")
        for horizon in group.horizons:
            mfe = horizon.mfe
            mae = horizon.mae
            balance = horizon.net_excursion_balance
            comparison = horizon.favorable_adverse
            print(
                f"{group.dimension.value} {group.name} {horizon.horizon} "
                f"{horizon.complete_n} {horizon.incomplete_n} "
                f"{_format_base_stat(mfe.mean)}/{_format_base_stat(mfe.median)}/"
                f"{_format_base_stat(mfe.minimum)}/{_format_base_stat(mfe.maximum)} "
                f"{_format_base_stat(mae.mean)}/{_format_base_stat(mae.median)}/"
                f"{_format_base_stat(mae.minimum)}/{_format_base_stat(mae.maximum)} "
                f"{_format_base_stat(balance.mean)}/"
                f"{_format_base_stat(balance.median)} "
                f"{comparison.mfe_greater}/{comparison.equal}/"
                f"{comparison.mfe_less} "
                f"{horizon.valid_ratio_n}/{horizon.zero_mae_n}/"
                f"{_format_base_stat(horizon.median_mfe_mae_ratio)}"
            )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("MFE/MAE and MFE-MAE are descriptive excursions, not realized returns.")
    print("No stops, targets, exits, EMA/VWAP filters, or position sizing are applied.")
    print("Status: PASS")


def _print_ema_alignment_comparison(result: EmaAlignmentComparisonResult) -> None:
    print("SPY CONTROLLED EMA9/EMA20 DIRECTIONAL ALIGNMENT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"seeds: {result.break_seed_count}  confirmed: {result.confirmed_count}  "
        f"non-confirmed: {result.non_confirmed_count}  "
        f"executable: {result.executable_count}  "
        f"session-end: {result.session_end_unavailable_count}"
    )
    print("Annotation composition")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n}"
        )
    print("Horizon comparison")
    print(
        "Group Horizon C/I MedianMFE MedianMAE MedianBalance MedianRatio "
        "DeltaMFE DeltaMAE DeltaBalance"
    )
    for group in result.groups:
        for horizon, delta in zip(group.horizons, group.deltas, strict=True):
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{_format_base_stat(horizon.median_mfe_mae_ratio)} "
                f"{_format_base_stat(delta.median_mfe_delta)} "
                f"{_format_base_stat(delta.median_mae_delta)} "
                f"{_format_base_stat(delta.median_balance_delta)}"
            )
    print("Direction × EMA state (EOD)")
    print("Direction State n MedianMFE MedianMAE MedianBalance Compare(>/=/<)")
    for group in result.direction_groups:
        eod = group.horizons[-1]
        comparison = eod.favorable_adverse
        print(
            f"{group.direction.value} {group.alignment_state.value} "
            f"{group.executable_n} {_format_base_stat(eod.mfe.median)} "
            f"{_format_base_stat(eod.mae.median)} "
            f"{_format_base_stat(eod.net_excursion_balance.median)} "
            f"{comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    print("Level × EMA state (counts and EOD)")
    print("Level State setups executable MedianMFE MedianMAE MedianBalance")
    for group in result.level_groups:
        print(
            f"{group.level_type.value} {group.alignment_state.value} "
            f"{group.annotation_n} {group.executable_n} "
            f"{_format_base_stat(group.eod.mfe.median)} "
            f"{_format_base_stat(group.eod.mae.median)} "
            f"{_format_base_stat(group.eod.net_excursion_balance.median)}"
        )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        "exploratory descriptive research only, not a validated edge."
    )
    print("EMA labels do not modify Stage 9 setups, entries, or MFE/MAE outcomes.")
    print("No VWAP, recent-cross, slope, or separation requirement is applied.")
    print("Status: PASS")


def _print_ema_cross_context_comparison(
    result: EmaCrossContextComparisonResult,
) -> None:
    print("SPY EMA9/EMA20 PRIOR-CROSS CONTEXT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"Stage 4 crosses: {result.stage4_event_count}  "
        f"seeds: {result.break_seed_count}  confirmed: {result.confirmed_count}  "
        f"executable: {result.executable_count}"
    )
    print("Population reconciliation")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n} "
            f"exec-LONG={group.long_executable_n} exec-SHORT={group.short_executable_n}"
        )
    distribution = result.bars_since_cross_distribution
    print(
        "Exact bars-since-cross distribution: "
        f"n={distribution.n} min={_format_base_stat(distribution.minimum)} "
        f"median={_format_base_stat(distribution.median)} "
        f"max={_format_base_stat(distribution.maximum)}"
    )
    print("Bars Setups Executable LONG SHORT EOD-MFE EOD-MAE EOD-Balance")
    for row in result.recency_rows:
        print(
            f"{row.bars_since_cross} {row.annotation_n} {row.executable_n} "
            f"{row.long_executable_n} {row.short_executable_n} "
            f"{_format_base_stat(row.eod.mfe.median)} "
            f"{_format_base_stat(row.eod.mae.median)} "
            f"{_format_base_stat(row.eod.net_excursion_balance.median)}"
        )
    print("Five-horizon comparison")
    print("Group Horizon C/I MedianMFE MedianMAE MedianBalance Compare(>/=/<)")
    for group in result.groups:
        for horizon in group.horizons:
            comparison = horizon.favorable_adverse
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
            )
    print("Direction × cross state (EOD)")
    print("Direction State n MedianMFE MedianMAE MedianBalance Compare(>/=/<)")
    for group in result.direction_groups:
        comparison = group.eod.favorable_adverse
        print(
            f"{group.direction.value} {group.cross_state.value} {group.executable_n} "
            f"{_format_base_stat(group.eod.mfe.median)} "
            f"{_format_base_stat(group.eod.mae.median)} "
            f"{_format_base_stat(group.eod.net_excursion_balance.median)} "
            f"{comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    print("Stage 10.1 EMA alignment × Stage 10.2 cross context")
    for item in result.alignment_cross_tab:
        print(f"{item.alignment_state.value} × {item.cross_state.value}: {item.annotation_n}")
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("Exact recency is reported without any recent-cross cutoff or optimization.")
    print("Stage 9 setups, entries, and MFE/MAE outcomes remain unchanged.")
    print("Status: PASS")


def _print_vwap_alignment_comparison(result: VwapAlignmentComparisonResult) -> None:
    print("SPY CONTROLLED CONFIRMATION-PRICE/VWAP ALIGNMENT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"seeds: {result.break_seed_count}  confirmed: {result.confirmed_count}  "
        f"executable: {result.executable_count}  "
        f"session-end: {result.session_end_unavailable_count}"
    )
    print("Population reconciliation")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n}"
        )
    print("Five-horizon comparison")
    print(
        "Group Horizon C/I MedianMFE MedianMAE MedianBalance MedianRatio "
        "DeltaMFE DeltaMAE DeltaBalance"
    )
    for group in result.groups:
        for horizon, delta in zip(group.horizons, group.deltas, strict=True):
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{_format_base_stat(horizon.median_mfe_mae_ratio)} "
                f"{_format_base_stat(delta.median_mfe_delta)} "
                f"{_format_base_stat(delta.median_mae_delta)} "
                f"{_format_base_stat(delta.median_balance_delta)}"
            )
    print("Direction × VWAP state (EOD)")
    print("Direction State n MedianMFE MedianMAE MedianBalance Compare(>/=/<)")
    for group in result.direction_groups:
        comparison = group.eod.favorable_adverse
        print(
            f"{group.direction.value} {group.alignment_state.value} "
            f"{group.executable_n} {_format_base_stat(group.eod.mfe.median)} "
            f"{_format_base_stat(group.eod.mae.median)} "
            f"{_format_base_stat(group.eod.net_excursion_balance.median)} "
            f"{comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    print("Level × VWAP state (counts and EOD)")
    print("Level State setups executable MedianMFE MedianMAE MedianBalance")
    for group in result.level_groups:
        print(
            f"{group.level_type.value} {group.alignment_state.value} "
            f"{group.annotation_n} {group.executable_n} "
            f"{_format_base_stat(group.eod.mfe.median)} "
            f"{_format_base_stat(group.eod.mae.median)} "
            f"{_format_base_stat(group.eod.net_excursion_balance.median)}"
        )
    print("Stage 10.1 EMA alignment × VWAP")
    for item in result.ema_vwap_cross_tab:
        print(f"{item.ema_state.value} × {item.vwap_state.value}: {item.annotation_n}")
    print("Stage 10.2 cross context × VWAP")
    for item in result.cross_context_vwap_cross_tab:
        print(f"{item.cross_state.value} × {item.vwap_state.value}: {item.annotation_n}")
    print("Directional VWAP-distance summaries")
    print("Direction n Min Median Max Positive/Zero/Negative")
    for item in result.distance_statistics:
        direction = item.direction.value if item.direction is not None else "ALL"
        distribution = item.distribution
        print(
            f"{direction} {distribution.n} "
            f"{_format_base_stat(distribution.minimum)} "
            f"{_format_base_stat(distribution.median)} "
            f"{_format_base_stat(distribution.maximum)} "
            f"{item.positive_n}/{item.zero_n}/{item.negative_n}"
        )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("Price/VWAP distance is descriptive; no threshold or strategy filter is applied.")
    print("Stage 9 setups, entries, and MFE/MAE outcomes remain unchanged.")
    print("Status: PASS")


def _print_ema9_vwap_alignment_comparison(
    result: Ema9VwapAlignmentComparisonResult,
) -> None:
    print("SPY CONTROLLED EMA9/VWAP DIRECTIONAL ALIGNMENT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"seeds: {result.break_seed_count}  confirmed: {result.confirmed_count}  "
        f"executable: {result.executable_count}  "
        f"session-end: {result.session_end_unavailable_count}"
    )
    print("Population reconciliation")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n}"
        )
    print("Directional EMA9/VWAP-distance summaries")
    print("Direction n Min Median Max Positive/Zero/Negative Unavailable")
    for item in result.distance_statistics:
        label = item.direction.value if item.direction is not None else "ALL"
        distribution = item.distribution
        print(
            f"{label} {distribution.n} "
            f"{_format_base_stat(distribution.minimum)} "
            f"{_format_base_stat(distribution.median)} "
            f"{_format_base_stat(distribution.maximum)} "
            f"{item.positive_n}/{item.zero_n}/{item.negative_n} "
            f"{item.unavailable_n}"
        )
    print("Five-horizon comparison")
    print(
        "Group Horizon C/I MedianMFE MedianMAE MedianBalance MedianRatio "
        "DeltaMFE DeltaMAE DeltaBalance"
    )
    for group in result.groups:
        for horizon, delta in zip(group.horizons, group.deltas, strict=True):
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{_format_base_stat(horizon.median_mfe_mae_ratio)} "
                f"{_format_base_stat(delta.median_mfe_delta)} "
                f"{_format_base_stat(delta.median_mae_delta)} "
                f"{_format_base_stat(delta.median_balance_delta)}"
            )
    print("Direction × EMA9/VWAP state (EOD)")
    for group in result.direction_groups:
        comparison = group.eod.favorable_adverse
        print(
            f"{group.direction.value} {group.alignment_state.value} "
            f"n={group.executable_n} MFE={_format_base_stat(group.eod.mfe.median)} "
            f"MAE={_format_base_stat(group.eod.mae.median)} "
            f"balance={_format_base_stat(group.eod.net_excursion_balance.median)} "
            f">/=/<={comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    print("Price/VWAP × EMA9/VWAP")
    for item in result.price_vwap_cross_tab:
        print(
            f"{item.price_vwap_state.value} × {item.ema9_vwap_state.value}: "
            f"{item.annotation_n}"
        )
    print("EMA9/20 × EMA9/VWAP")
    for item in result.ema_alignment_cross_tab:
        print(
            f"{item.ema_alignment_state.value} × {item.ema9_vwap_state.value}: "
            f"{item.annotation_n}"
        )
    print("Prior-cross context × EMA9/VWAP")
    for item in result.cross_context_cross_tab:
        print(
            f"{item.cross_state.value} × {item.ema9_vwap_state.value}: "
            f"{item.annotation_n}"
        )
    print("Price/EMA9 VWAP agreement states (EOD)")
    for item in result.agreement_groups:
        print(
            f"{item.state.value}: setups={item.annotation_n} "
            f"LONG={item.long_annotation_n} SHORT={item.short_annotation_n} "
            f"executable={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print("Level × EMA9/VWAP state (counts and EOD)")
    for item in result.level_groups:
        print(
            f"{item.level_type.value} {item.alignment_state.value} "
            f"setups={item.annotation_n} executable={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("No EMA9/VWAP cross, distance threshold, or combined filter is applied.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_ema20_vwap_alignment_comparison(
    result: Ema20VwapAlignmentComparisonResult,
) -> None:
    print("SPY CONTROLLED EMA20/VWAP DIRECTIONAL ALIGNMENT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"seeds: {result.break_seed_count}  confirmed: {result.confirmed_count}  "
        f"executable: {result.executable_count}  "
        f"session-end: {result.session_end_unavailable_count}"
    )
    print("Population reconciliation")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n}"
        )
    print("Directional EMA20/VWAP-distance summaries")
    print("Direction n Min Median Max Positive/Zero/Negative Unavailable")
    for item in result.distance_statistics:
        label = item.direction.value if item.direction is not None else "ALL"
        distribution = item.distribution
        print(
            f"{label} {distribution.n} "
            f"{_format_base_stat(distribution.minimum)} "
            f"{_format_base_stat(distribution.median)} "
            f"{_format_base_stat(distribution.maximum)} "
            f"{item.positive_n}/{item.zero_n}/{item.negative_n} "
            f"{item.unavailable_n}"
        )
    print("Five-horizon comparison")
    print(
        "Group Horizon C/I MedianMFE MedianMAE MedianBalance MedianRatio "
        "DeltaMFE DeltaMAE DeltaBalance"
    )
    for group in result.groups:
        for horizon, delta in zip(group.horizons, group.deltas, strict=True):
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{_format_base_stat(horizon.median_mfe_mae_ratio)} "
                f"{_format_base_stat(delta.median_mfe_delta)} "
                f"{_format_base_stat(delta.median_mae_delta)} "
                f"{_format_base_stat(delta.median_balance_delta)}"
            )
    print("Direction × EMA20/VWAP state (EOD)")
    for group in result.direction_groups:
        comparison = group.eod.favorable_adverse
        print(
            f"{group.direction.value} {group.alignment_state.value} "
            f"n={group.executable_n} MFE={_format_base_stat(group.eod.mfe.median)} "
            f"MAE={_format_base_stat(group.eod.mae.median)} "
            f"balance={_format_base_stat(group.eod.net_excursion_balance.median)} "
            f">/=/<={comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    for title, table in (
        ("EMA9/VWAP × EMA20/VWAP", result.ema9_vwap_cross_tab),
        ("EMA9/20 × EMA20/VWAP", result.ema_alignment_cross_tab),
        ("Price/VWAP × EMA20/VWAP", result.price_vwap_cross_tab),
        ("EMA9/VWAP cross context × EMA20/VWAP", result.ema9_vwap_cross_context_cross_tab),
    ):
        print(title)
        for item in table:
            print(
                f"{item.source_state} × {item.ema20_vwap_state.value}: "
                f"{item.annotation_n}"
            )
    print("Observed EMA9/EMA20/VWAP stack states (EOD)")
    for item in result.stack_groups:
        print(
            f"{item.stack_state}: setups={item.annotation_n} "
            f"executable={item.executable_n} LONG={item.long_annotation_n} "
            f"SHORT={item.short_annotation_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print("Level × EMA20/VWAP state (counts and EOD)")
    for item in result.level_groups:
        print(
            f"{item.level_type.value} {item.alignment_state.value} "
            f"setups={item.annotation_n} executable={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("No EMA20/VWAP cross, distance threshold, or combined filter is applied.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_combined_context_matrix(result: CombinedContextMatrixResult) -> None:
    print("SPY STAGE 10 COMBINED CONTEXT MATRIX")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions={result.development_session_count} "
        f"confirmed={result.confirmed_count} executable={result.executable_count}"
    )
    print("BASE_ALL exact Stage 9.3 reproduction")
    print("Horizon C/I MedianMFE MedianMAE MedianBalance")
    for item in result.base_all_horizons:
        print(
            f"{item.horizon} {item.complete_n}/{item.incomplete_n} "
            f"{_format_base_stat(item.mfe.median)} "
            f"{_format_base_stat(item.mae.median)} "
            f"{_format_base_stat(item.net_excursion_balance.median)}"
        )
    print("Marginal reconciliation")
    for item in result.marginal_counts:
        print(
            f"{item.dimension} {item.state}: "
            f"setups={item.annotation_n} executable={item.executable_n}"
        )
    print(
        f"Observed exact combinations={len(result.context_groups)} "
        f"singletons={result.singleton_group_count} "
        f"n<=5={result.n_le_5_group_count}"
    )
    print("Exact combined-context rows")
    for index, group in enumerate(result.context_groups, start=1):
        key = group.context_key
        levels = ",".join(
            f"{item.level_type.value}:{item.annotation_n}"
            for item in group.level_composition
        )
        sparse = "singleton" if group.singleton else ("n<=5" if group.n_le_5 else "")
        print(
            f"[{index}] n={group.annotation_n} exec={group.executable_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"sessions={group.session_count} base={_format_percentage(group.percentage_of_base_all)} "
            f"sparse={sparse or 'no'} levels={levels}"
        )
        print(
            f"  direction={key.direction.value} "
            f"EMA9/20={key.ema9_20_alignment.value} "
            f"EMA9/20-cross={key.ema9_20_cross_context.value}@{key.ema9_20_bars_since_cross} "
            f"price/VWAP={key.price_vwap_alignment.value}"
        )
        print(
            f"  EMA9/VWAP={key.ema9_vwap_alignment.value} "
            f"EMA9/VWAP-cross={key.ema9_vwap_cross_context.value}@{key.ema9_vwap_bars_since_cross} "
            f"EMA20/VWAP={key.ema20_vwap_alignment.value} "
            f"EMA20/VWAP-cross={key.ema20_vwap_cross_context.value}@{key.ema20_vwap_bars_since_cross}"
        )
        for item in group.horizons:
            print(
                f"  {item.horizon} C/I={item.complete_n}/{item.incomplete_n} "
                f"MFE={_format_base_stat(item.mfe.median)} "
                f"MAE={_format_base_stat(item.mae.median)} "
                f"balance={_format_base_stat(item.net_excursion_balance.median)}"
            )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("No context combination is ranked, filtered, scored, or qualified.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_ema20_vwap_cross_context_comparison(
    result: Ema20VwapCrossContextComparisonResult,
) -> None:
    print("SPY EMA20/VWAP COMPLETED-CANDLE CROSS CONTEXT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"events: {len(result.events)}  bullish: {result.bullish_event_count}  "
        f"bearish: {result.bearish_event_count}"
    )
    print("Cross-event universe by session")
    for item in result.event_sessions:
        first = (
            item.first_cross_timestamp.isoformat()
            if item.first_cross_timestamp is not None
            else "N/A"
        )
        last = (
            item.last_cross_timestamp.isoformat()
            if item.last_cross_timestamp is not None
            else "N/A"
        )
        print(
            f"{item.session_date.isoformat()} total={item.total_crosses} "
            f"bullish={item.bullish_crosses} bearish={item.bearish_crosses} "
            f"first={first} last={last}"
        )
    print("Setup reconciliation")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n}"
        )
    distribution = result.bars_since_cross_distribution
    print(
        "Exact bars-since-cross distribution: "
        f"n={distribution.n} min={_format_base_stat(distribution.minimum)} "
        f"median={_format_base_stat(distribution.median)} "
        f"max={_format_base_stat(distribution.maximum)}"
    )
    print("Bars Setups Exec LONG SHORT EOD-MFE EOD-MAE EOD-Balance")
    for item in result.recency_rows:
        print(
            f"{item.bars_since_cross} {item.annotation_n} {item.executable_n} "
            f"{item.long_executable_n} {item.short_executable_n} "
            f"{_format_base_stat(item.eod.mfe.median)} "
            f"{_format_base_stat(item.eod.mae.median)} "
            f"{_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print("Five-horizon comparison")
    print("Group Horizon C/I MedianMFE MedianMAE MedianBalance Compare(>/=/<)")
    for group in result.groups:
        for horizon in group.horizons:
            comparison = horizon.favorable_adverse
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
            )
    print("Direction × EMA20/VWAP cross context (EOD)")
    for item in result.direction_groups:
        comparison = item.eod.favorable_adverse
        print(
            f"{item.direction.value} {item.cross_state.value} n={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)} "
            f">/=/<={comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    print("Current EMA20/VWAP state × cross context")
    for item in result.ema20_vwap_state_cross_tab:
        print(
            f"{item.alignment_state.value} × {item.cross_state.value}: "
            f"{item.annotation_n}"
        )
    print("EMA9/VWAP cross context × EMA20/VWAP cross context")
    for item in result.ema9_ema20_vwap_cross_tab:
        print(
            f"{item.ema9_vwap_cross_state.value} × "
            f"{item.ema20_vwap_cross_state.value}: {item.annotation_n}"
        )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("No recency cutoff, optimization, or cross-only strategy is applied.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_ema9_vwap_cross_context_comparison(
    result: Ema9VwapCrossContextComparisonResult,
) -> None:
    print("SPY EMA9/VWAP COMPLETED-CANDLE CROSS CONTEXT COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions: {result.development_session_count}  "
        f"events: {len(result.events)}  bullish: {result.bullish_event_count}  "
        f"bearish: {result.bearish_event_count}"
    )
    print("Cross-event universe by session")
    for item in result.event_sessions:
        first = (
            item.first_cross_timestamp.isoformat()
            if item.first_cross_timestamp is not None
            else "N/A"
        )
        last = (
            item.last_cross_timestamp.isoformat()
            if item.last_cross_timestamp is not None
            else "N/A"
        )
        print(
            f"{item.session_date.isoformat()} total={item.total_crosses} "
            f"bullish={item.bullish_crosses} bearish={item.bearish_crosses} "
            f"first={first} last={last}"
        )
    print("Setup reconciliation")
    for group in result.groups:
        print(
            f"{group.name.value}: setups={group.annotation_n} "
            f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
            f"executable={group.executable_n}"
        )
    distribution = result.bars_since_cross_distribution
    print(
        "Exact bars-since-cross distribution: "
        f"n={distribution.n} min={_format_base_stat(distribution.minimum)} "
        f"median={_format_base_stat(distribution.median)} "
        f"max={_format_base_stat(distribution.maximum)}"
    )
    print("Bars Setups Exec LONG SHORT EOD-MFE EOD-MAE EOD-Balance")
    for item in result.recency_rows:
        print(
            f"{item.bars_since_cross} {item.annotation_n} {item.executable_n} "
            f"{item.long_executable_n} {item.short_executable_n} "
            f"{_format_base_stat(item.eod.mfe.median)} "
            f"{_format_base_stat(item.eod.mae.median)} "
            f"{_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print("Five-horizon comparison")
    print("Group Horizon C/I MedianMFE MedianMAE MedianBalance Compare(>/=/<)")
    for group in result.groups:
        for horizon in group.horizons:
            comparison = horizon.favorable_adverse
            print(
                f"{group.name.value} {horizon.horizon} "
                f"{horizon.complete_n}/{horizon.incomplete_n} "
                f"{_format_base_stat(horizon.mfe.median)} "
                f"{_format_base_stat(horizon.mae.median)} "
                f"{_format_base_stat(horizon.net_excursion_balance.median)} "
                f"{comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
            )
    print("Direction × EMA9/VWAP cross context (EOD)")
    for item in result.direction_groups:
        comparison = item.eod.favorable_adverse
        print(
            f"{item.direction.value} {item.cross_state.value} n={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)} "
            f">/=/<={comparison.mfe_greater}/{comparison.equal}/{comparison.mfe_less}"
        )
    print("Current EMA9/VWAP state × cross context")
    for item in result.ema9_vwap_state_cross_tab:
        print(
            f"{item.alignment_state.value} × {item.cross_state.value}: "
            f"{item.annotation_n}"
        )
    print("Price/VWAP state × EMA9/VWAP cross context")
    for item in result.price_vwap_cross_tab:
        print(
            f"{item.price_vwap_state.value} × {item.cross_state.value}: "
            f"{item.annotation_n}"
        )
    print("EMA9/20 alignment × EMA9/VWAP cross context")
    for item in result.ema_alignment_cross_tab:
        print(
            f"{item.ema_alignment_state.value} × {item.cross_state.value}: "
            f"{item.annotation_n}"
        )
    print("EMA9/20 cross context × EMA9/VWAP cross context")
    for item in result.cross_system_cross_tab:
        print(
            f"{item.ema9_20_cross_state.value} × "
            f"{item.ema9_vwap_cross_state.value}: {item.annotation_n}"
        )
    print(
        f"WARNING: development sample = {result.development_session_count} sessions; "
        f"{result.sample_warning}"
    )
    print("No recency cutoff, optimization, or cross-only strategy is applied.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
