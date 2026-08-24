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
from spy_research.execution import (
    ExecutionClassificationInputError,
    ExecutionVariantClassificationReport,
    ExecutionVariantClassificationService,
    ExitComparisonInputError,
    ExitModelComparisonReport,
    ExitModelComparisonService,
    ExitModelExitReason,
    ExitModelStatus,
    ExecutionInputError,
    FixedRiskSimulationReport,
    FixedRiskSimulationService,
    TradeExitReason,
    TradeSimulationStatus,
    exit_model_comparison_hash,
    execution_variant_classification_hash,
    fixed_risk_simulation_hash,
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
from spy_research.replay import (
    ReplayInputError,
    SignalReplayReport,
    SignalReplayService,
    signal_replay_hash,
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
    ExpandedStabilityReport,
    ExpandedStabilityService,
    ControlledVariantSelectionReport,
    ControlledVariantSelectionService,
    SetupOutcomeInputError,
    SetupOutcomeResult,
    SetupOutcomeService,
    SetupDirection,
    StabilityInputError,
    VariantSelectionInputError,
    ValidationPartition,
    stability_report_hash,
    controlled_variant_selection_hash,
)
from spy_research.strategy.comparisons import (
    CombinedContextInputError,
    CombinedContextMatrixResult,
    CombinedContextMatrixService,
    MarketConditionFeatureResult,
    MarketConditionFeatureService,
    MarketConditionInputError,
    RegimeHypothesisComparisonResult,
    RegimeHypothesisComparisonService,
    RegimeHypothesisInputError,
    RoomToLevelComparisonResult,
    RoomToLevelComparisonService,
    RoomToLevelInputError,
    MarketStructureComparisonResult,
    MarketStructureComparisonService,
    MarketStructureInputError,
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

    market_condition = subparsers.add_parser(
        "market-condition-features",
        help="measure confirmation-time market conditions without classifying them",
    )
    market_condition.add_argument("--start", type=parse_iso_date, required=True)
    market_condition.add_argument("--end", type=parse_iso_date, required=True)
    market_condition.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    market_condition.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    market_condition.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    regime_hypotheses = subparsers.add_parser(
        "compare-regime-hypotheses",
        help="compare predeclared Stage 11.1 research labels without filtering",
    )
    regime_hypotheses.add_argument("--start", type=parse_iso_date, required=True)
    regime_hypotheses.add_argument("--end", type=parse_iso_date, required=True)
    regime_hypotheses.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    regime_hypotheses.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    regime_hypotheses.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    room_to_level = subparsers.add_parser(
        "compare-room-to-next-level",
        help="measure objective directional room without filtering setups",
    )
    room_to_level.add_argument("--start", type=parse_iso_date, required=True)
    room_to_level.add_argument("--end", type=parse_iso_date, required=True)
    room_to_level.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    room_to_level.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    room_to_level.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    market_structure = subparsers.add_parser(
        "compare-market-structure",
        help="measure confirmed 2x2 five-minute swing structure without filtering",
    )
    market_structure.add_argument("--start", type=parse_iso_date, required=True)
    market_structure.add_argument("--end", type=parse_iso_date, required=True)
    market_structure.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    market_structure.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    market_structure.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    expanded_stability = subparsers.add_parser(
        "validate-expanded-stability",
        help="run offline expanded frozen-rule stability analysis",
    )
    expanded_stability.add_argument("--start", type=parse_iso_date, required=True)
    expanded_stability.add_argument("--end", type=parse_iso_date, required=True)
    expanded_stability.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    expanded_stability.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    expanded_stability.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    variant_selection = subparsers.add_parser(
        "select-stage13-variants",
        help="select only the ten frozen Stage 13 research candidates",
    )
    variant_selection.add_argument("--start", type=parse_iso_date, required=True)
    variant_selection.add_argument("--end", type=parse_iso_date, required=True)
    variant_selection.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    variant_selection.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    variant_selection.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    fixed_risk_simulation = subparsers.add_parser(
        "simulate-fixed-risk-trades",
        help="simulate the frozen Stage 13.1 SPY-share stop/target family",
    )
    fixed_risk_simulation.add_argument("--start", type=parse_iso_date, required=True)
    fixed_risk_simulation.add_argument("--end", type=parse_iso_date, required=True)
    fixed_risk_simulation.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    fixed_risk_simulation.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    fixed_risk_simulation.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    exit_comparison = subparsers.add_parser(
        "compare-exit-models",
        help="compare the frozen Stage 13.1/13.2 exit-model universe",
    )
    exit_comparison.add_argument("--start", type=parse_iso_date, required=True)
    exit_comparison.add_argument("--end", type=parse_iso_date, required=True)
    exit_comparison.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    exit_comparison.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    exit_comparison.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    execution_classification = subparsers.add_parser(
        "classify-execution-variants",
        help="mechanically classify frozen Stage 13.2 execution variants",
    )
    execution_classification.add_argument(
        "--start", type=parse_iso_date, required=True
    )
    execution_classification.add_argument("--end", type=parse_iso_date, required=True)
    execution_classification.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH
    )
    execution_classification.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    execution_classification.add_argument(
        "--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT
    )

    signal_replay = subparsers.add_parser(
        "replay-signal-engine",
        help="replay frozen SPY one-minute bars through incremental signal state",
    )
    signal_replay.add_argument("--start", type=parse_iso_date, required=True)
    signal_replay.add_argument("--end", type=parse_iso_date, required=True)
    signal_replay.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    signal_replay.add_argument(
        "--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT
    )
    signal_replay.add_argument(
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

    if args.command == "market-condition-features":
        try:
            config = load_research_config(args.config)
            result = MarketConditionFeatureService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (MarketConditionInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to measure market conditions: {exc}", file=sys.stderr)
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
            print(f"Unable to measure market conditions: {exc}", file=sys.stderr)
            return 2
        _print_market_condition_features(result)
        return 0

    if args.command == "compare-regime-hypotheses":
        try:
            config = load_research_config(args.config)
            result = RegimeHypothesisComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (RegimeHypothesisInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare regime hypotheses: {exc}", file=sys.stderr)
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
            print(f"Unable to compare regime hypotheses: {exc}", file=sys.stderr)
            return 2
        _print_regime_hypothesis_comparison(result)
        return 0

    if args.command == "compare-room-to-next-level":
        try:
            config = load_research_config(args.config)
            result = RoomToLevelComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (RoomToLevelInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare room to next level: {exc}", file=sys.stderr)
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
            print(f"Unable to compare room to next level: {exc}", file=sys.stderr)
            return 2
        _print_room_to_level_comparison(result)
        return 0

    if args.command == "compare-market-structure":
        try:
            config = load_research_config(args.config)
            result = MarketStructureComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (MarketStructureInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to compare market structure: {exc}", file=sys.stderr)
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
            print(f"Unable to compare market structure: {exc}", file=sys.stderr)
            return 2
        _print_market_structure_comparison(result)
        return 0

    if args.command == "validate-expanded-stability":
        try:
            config = load_research_config(args.config)
            result = ExpandedStabilityService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (StabilityInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to validate expanded stability: {exc}", file=sys.stderr)
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
            print(f"Unable to validate expanded stability: {exc}", file=sys.stderr)
            return 2
        _print_expanded_stability(result)
        return 0

    if args.command == "select-stage13-variants":
        try:
            config = load_research_config(args.config)
            result = ControlledVariantSelectionService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (VariantSelectionInputError, StabilityInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to select Stage 13 variants: {exc}", file=sys.stderr)
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
            print(f"Unable to select Stage 13 variants: {exc}", file=sys.stderr)
            return 2
        _print_controlled_variant_selection(result)
        return 0

    if args.command == "simulate-fixed-risk-trades":
        try:
            config = load_research_config(args.config)
            result = FixedRiskSimulationService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (ExecutionInputError, SetupOutcomeInputError) as exc:
            print(f"Unable to simulate fixed-risk trades: {exc}", file=sys.stderr)
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
            print(f"Unable to simulate fixed-risk trades: {exc}", file=sys.stderr)
            return 2
        _print_fixed_risk_simulation(result)
        return 0

    if args.command == "compare-exit-models":
        try:
            config = load_research_config(args.config)
            result = ExitModelComparisonService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            ExitComparisonInputError,
            ExecutionInputError,
            SetupOutcomeInputError,
        ) as exc:
            print(f"Unable to compare exit models: {exc}", file=sys.stderr)
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
            print(f"Unable to compare exit models: {exc}", file=sys.stderr)
            return 2
        _print_exit_model_comparison(result)
        return 0

    if args.command == "classify-execution-variants":
        try:
            config = load_research_config(args.config)
            result = ExecutionVariantClassificationService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (
            ExecutionClassificationInputError,
            ExitComparisonInputError,
            ExecutionInputError,
            SetupOutcomeInputError,
        ) as exc:
            print(f"Unable to classify execution variants: {exc}", file=sys.stderr)
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
            print(f"Unable to classify execution variants: {exc}", file=sys.stderr)
            return 2
        _print_execution_variant_classification(result)
        return 0

    if args.command == "replay-signal-engine":
        try:
            config = load_research_config(args.config)
            result = SignalReplayService(
                config,
                ProcessedFiveMinuteStore(root=args.processed_data_root),
                RawBarStore(config, root=args.raw_data_root),
            ).calculate(start=args.start, end=args.end)
        except (ReplayInputError, BaseSetupInputError) as exc:
            print(f"Unable to replay signal engine: {exc}", file=sys.stderr)
            return 1
        except (
            RawDataError,
            ProcessedDataError,
            OSError,
            ValueError,
            yaml.YAMLError,
            ValidationError,
        ) as exc:
            print(f"Unable to replay signal engine: {exc}", file=sys.stderr)
            return 2
        _print_signal_replay(result)
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


def _print_market_condition_features(
    result: MarketConditionFeatureResult,
) -> None:
    print("SPY STAGE 10.9 MARKET-CONDITION FEATURE MEASUREMENTS")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions={result.development_session_count} "
        f"confirmed={result.confirmed_count} executable={result.executable_count}"
    )
    print("BASE_ALL exact Stage 9.3 reproduction")
    for item in result.base_all_horizons:
        print(
            f"{item.horizon} C/I={item.complete_n}/{item.incomplete_n} "
            f"MFE={_format_base_stat(item.mfe.median)} "
            f"MAE={_format_base_stat(item.mae.median)} "
            f"balance={_format_base_stat(item.net_excursion_balance.median)}"
        )
    for report in result.feature_reports:
        summary = report.distribution.distribution
        print(f"FEATURE {report.feature_name}")
        print(
            f"n={summary.n} unavailable={report.distribution.unavailable_n} "
            f"min={_format_base_stat(summary.minimum)} "
            f"p25={_format_base_stat(summary.p25)} "
            f"median={_format_base_stat(summary.median)} "
            f"p75={_format_base_stat(summary.p75)} "
            f"max={_format_base_stat(summary.maximum)}"
        )
        for group in report.quartiles:
            print(
                f"  {group.quartile.value} "
                f"({ _format_base_stat(group.lower_exclusive)}, "
                f"{_format_base_stat(group.upper_inclusive)}] "
                f"setups={group.annotation_n} executable={group.executable_n} "
                f"LONG={group.long_annotation_n} SHORT={group.short_annotation_n} "
                f"sessions={group.session_count}"
            )
            for horizon in group.horizons:
                print(
                    f"    {horizon.horizon} C/I={horizon.complete_n}/"
                    f"{horizon.incomplete_n} "
                    f"MFE={_format_base_stat(horizon.mfe.median)} "
                    f"MAE={_format_base_stat(horizon.mae.median)} "
                    f"balance={_format_base_stat(horizon.net_excursion_balance.median)}"
                )
    print(f"WARNING: {result.sample_warning}")
    print("No trend/chop label, score, threshold, filter, or qualification is applied.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_regime_hypothesis_comparison(
    result: RegimeHypothesisComparisonResult,
) -> None:
    print("SPY STAGE 11.1 PREDECLARED MARKET-REGIME HYPOTHESES")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions={result.development_session_count} "
        f"confirmed={result.confirmed_count} executable={result.executable_count}"
    )
    print(f"Frozen Stage 10.9 source hash: {result.source_stage10_9_hash}")
    print("Frozen Stage 10.9 quartile boundaries")
    for item in result.boundaries:
        print(
            f"{item.feature_name}: Q1<={_format_base_stat(item.q1_upper)} "
            f"Q2<={_format_base_stat(item.q2_upper)} "
            f"Q3<={_format_base_stat(item.q3_upper)}"
        )
    print("BASE_ALL exact Stage 9.3 reproduction")
    for item in result.base_all_horizons:
        print(
            f"{item.horizon} C/I={item.complete_n}/{item.incomplete_n} "
            f"MFE={_format_base_stat(item.mfe.median)} "
            f"MAE={_format_base_stat(item.mae.median)} "
            f"balance={_format_base_stat(item.net_excursion_balance.median)} "
            f">/=/<={item.favorable_adverse.mfe_greater}/"
            f"{item.favorable_adverse.equal}/"
            f"{item.favorable_adverse.mfe_less} "
            f"ratio={_format_base_stat(item.median_mfe_mae_ratio)}"
        )
    print("Individual and combined hypothesis states")
    for group in result.groups:
        levels = ",".join(
            f"{item.level_type.value}:{item.annotation_n}"
            for item in group.level_composition
        )
        sessions = ",".join(
            f"{item.session_date.isoformat()}:{item.annotation_n}"
            for item in group.session_composition
        )
        warnings = []
        if group.fewer_than_10_executable:
            warnings.append("exec<10")
        if group.fewer_than_5_sessions:
            warnings.append("sessions<5")
        print(
            f"{group.hypothesis} {group.state}: setups={group.annotation_n} "
            f"executable={group.executable_n} LONG={group.long_annotation_n} "
            f"SHORT={group.short_annotation_n} sessions={group.session_count} "
            f"max-session={group.max_session_annotation_n}/"
            f"{_format_base_stat(group.max_session_percentage)}% "
            f"warnings={','.join(warnings) or 'none'}"
        )
        print(f"  levels={levels or 'none'} sessions={sessions or 'none'}")
        for horizon in group.horizons:
            print(
                f"  {horizon.horizon} C/I={horizon.complete_n}/"
                f"{horizon.incomplete_n} "
                f"MFE={_format_base_stat(horizon.mfe.median)} "
                f"MAE={_format_base_stat(horizon.mae.median)} "
                f"balance={_format_base_stat(horizon.net_excursion_balance.median)} "
                f">/=/<={horizon.favorable_adverse.mfe_greater}/"
                f"{horizon.favorable_adverse.equal}/"
                f"{horizon.favorable_adverse.mfe_less} "
                f"ratio={_format_base_stat(horizon.median_mfe_mae_ratio)}"
            )
    print("Combined-label overlap with accepted Stage 10 context")
    for item in result.context_overlaps:
        print(
            f"{item.combined_state.value} {item.context_dimension} "
            f"{item.context_state}: setups={item.annotation_n} "
            f"executable={item.executable_n}"
        )
    print(f"WARNING: {result.sample_warning}")
    print("Sparse warnings are disclosures, not minimum-sample filters.")
    print("No hypothesis is promoted, scored, optimized, or used to qualify a setup.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_room_to_level_comparison(result: RoomToLevelComparisonResult) -> None:
    print("SPY STAGE 11.2 OBJECTIVE ROOM-TO-NEXT-LEVEL COMPARISON")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions={result.development_session_count} "
        f"confirmed={result.confirmed_count} executable={result.executable_count}"
    )
    print(f"Frozen Stage 11.1 source hash: {result.source_stage11_1_hash}")
    print("BASE_ALL exact Stage 9.3 reproduction")
    for item in result.base_all_horizons:
        print(
            f"{item.horizon} C/I={item.complete_n}/{item.incomplete_n} "
            f"MFE={_format_base_stat(item.mfe.median)} "
            f"MAE={_format_base_stat(item.mae.median)} "
            f"balance={_format_base_stat(item.net_excursion_balance.median)}"
        )
    print("Room distributions")
    for item in result.distributions:
        summary = item.distribution
        print(
            f"{item.metric} {item.direction}: n={summary.n} "
            f"open-ended={item.open_ended_n} unavailable={item.unavailable_n} "
            f"min={_format_base_stat(summary.minimum)} "
            f"Q1={_format_base_stat(summary.p25)} "
            f"median={_format_base_stat(summary.median)} "
            f"Q3={_format_base_stat(summary.p75)} "
            f"max={_format_base_stat(summary.maximum)}"
        )
    print("Fixed room/ATR buckets")
    for group in result.bucket_statistics:
        levels = ",".join(
            f"{item.level_type.value}:{item.annotation_n}"
            for item in group.level_composition
        )
        print(
            f"{group.bucket.value}: setups={group.annotation_n} "
            f"executable={group.executable_n} LONG={group.long_annotation_n} "
            f"SHORT={group.short_annotation_n} sessions={group.session_count} "
            f"levels={levels or 'none'}"
        )
        for horizon in group.horizons:
            print(
                f"  {horizon.horizon} C/I={horizon.complete_n}/"
                f"{horizon.incomplete_n} "
                f"MFE={_format_base_stat(horizon.mfe.median)} "
                f"MAE={_format_base_stat(horizon.mae.median)} "
                f"balance={_format_base_stat(horizon.net_excursion_balance.median)} "
                f">/=/<={horizon.favorable_adverse.mfe_greater}/"
                f"{horizon.favorable_adverse.equal}/"
                f"{horizon.favorable_adverse.mfe_less} "
                f"ratio={_format_base_stat(horizon.median_mfe_mae_ratio)}"
            )
    print("Trigger → nearest-level transitions")
    for item in result.transitions:
        target = (
            "+".join(level.value for level in item.next_level_types)
            if item.next_level_types
            else item.next_level_availability.value
        )
        print(f"{item.triggering_level_type.value} → {target}: {item.count}")
    print("Room-bucket cross-tabs (counts and EOD medians)")
    for item in result.cross_tabs:
        print(
            f"{item.bucket.value} {item.dimension} {item.state}: "
            f"setups={item.annotation_n} executable={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    print(f"WARNING: {result.sample_warning}")
    print("No room bucket, transition, or stacked-level count qualifies a setup.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_market_structure_comparison(
    result: MarketStructureComparisonResult,
) -> None:
    print("SPY STAGE 11.3 CONFIRMED FIVE-MINUTE MARKET STRUCTURE")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions={result.development_session_count} "
        f"confirmed={result.confirmed_count} executable={result.executable_count}"
    )
    print(
        f"Confirmed swings: highs={result.total_confirmed_swing_highs} "
        f"lows={result.total_confirmed_swing_lows}"
    )
    print(f"Frozen Stage 11.1 source hash: {result.source_stage11_1_hash}")
    print(f"Frozen Stage 11.2 source hash: {result.source_stage11_2_hash}")
    print("Swing universe by RTH session")
    for item in result.swing_sessions:
        print(
            f"{item.session_date.isoformat()} highs={item.swing_high_count} "
            f"lows={item.swing_low_count} "
            f"earliest-known={_format_timestamp(item.earliest_pivot_known_at)} "
            f"latest-known={_format_timestamp(item.latest_pivot_known_at)}"
        )
    print("BASE_ALL exact Stage 9.3 reproduction")
    for item in result.base_all_horizons:
        print(
            f"{item.horizon} C/I={item.complete_n}/{item.incomplete_n} "
            f"MFE={_format_base_stat(item.mfe.median)} "
            f"MAE={_format_base_stat(item.mae.median)} "
            f"balance={_format_base_stat(item.net_excursion_balance.median)}"
        )
    print("Structure populations and unchanged outcomes")
    for group in result.groups:
        levels = ",".join(
            f"{item.level_type.value}:{item.annotation_n}"
            for item in group.level_composition
        )
        print(
            f"{group.dimension} {group.state}: setups={group.annotation_n} "
            f"executable={group.executable_n} LONG={group.long_annotation_n} "
            f"SHORT={group.short_annotation_n} sessions={group.session_count} "
            f"levels={levels or 'none'}"
        )
        for horizon in group.horizons:
            print(
                f"  {horizon.horizon} C/I={horizon.complete_n}/"
                f"{horizon.incomplete_n} "
                f"MFE={_format_base_stat(horizon.mfe.median)} "
                f"MAE={_format_base_stat(horizon.mae.median)} "
                f"balance={_format_base_stat(horizon.net_excursion_balance.median)} "
                f">/=/<={horizon.favorable_adverse.mfe_greater}/"
                f"{horizon.favorable_adverse.equal}/"
                f"{horizon.favorable_adverse.mfe_less} "
                f"ratio={_format_base_stat(horizon.median_mfe_mae_ratio)}"
            )
    print("Structure cross-tabs (counts and EOD medians)")
    for item in result.cross_tabs:
        print(
            f"{item.structure_state.value} {item.context_dimension} "
            f"{item.context_state}: setups={item.annotation_n} "
            f"executable={item.executable_n} "
            f"MFE={_format_base_stat(item.eod.mfe.median)} "
            f"MAE={_format_base_stat(item.eod.mae.median)} "
            f"balance={_format_base_stat(item.eod.net_excursion_balance.median)}"
        )
    audit_date = date(2026, 8, 19)
    audits = tuple(
        item for item in result.audit_rows if item.annotation.session_date == audit_date
    )
    if audits:
        print("August 19 setup audit")
    for item in audits:
        annotation = item.annotation
        latest_high = annotation.latest_confirmed_swing_high
        previous_high = annotation.previous_confirmed_swing_high
        latest_low = annotation.latest_confirmed_swing_low
        previous_low = annotation.previous_confirmed_swing_low

        def swing_text(swing):
            if swing is None:
                return "N/A"
            return (
                f"{_format_base_stat(swing.swing_price)}@"
                f"{swing.pivot_timestamp.isoformat()} "
                f"known={swing.pivot_known_at.isoformat()}"
            )

        print(
            f"{annotation.setup_identity} {annotation.direction.value} "
            f"known={annotation.signal_known_at.isoformat()} "
            f"high={swing_text(latest_high)} previous-high={swing_text(previous_high)} "
            f"low={swing_text(latest_low)} previous-low={swing_text(previous_low)} "
            f"states={annotation.high_structure.value}/"
            f"{annotation.low_structure.value}/"
            f"{annotation.combined_structure.value}/"
            f"{annotation.direction_agreement.value} "
            f"close={_format_base_stat(annotation.confirmation_close)} "
            f"dist-high={_format_base_stat(annotation.confirmation_close_to_latest_swing_high)} "
            f"dist-low={_format_base_stat(annotation.confirmation_close_to_latest_swing_low)} "
            f"atr-high={_format_base_stat(annotation.distance_to_swing_high_in_atr)} "
            f"atr-low={_format_base_stat(annotation.distance_to_swing_low_in_atr)} "
            f"room-context={annotation.structural_room_state.value} "
            f"regime={item.regime_hypothesis.value} room={item.room_bucket.value} "
            f"EOD={_format_base_stat(item.eod_mfe)}/{_format_base_stat(item.eod_mae)}"
        )
    print(f"WARNING: {result.sample_warning}")
    print("MIXED_STRUCTURE is not labeled chop.")
    print("No structure state, agreement, or swing distance qualifies a setup.")
    print("Stage 9 setups, entries, and outcomes remain unchanged.")
    print("Status: PASS")


def _print_expanded_stability(result: ExpandedStabilityReport) -> None:
    print("SPY STAGE 12.2 EXPANDED FROZEN-RULE STABILITY ANALYSIS")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"sessions={result.expanded_session_count} setups={result.expanded_setup_n} "
        f"executable={result.expanded_executable_n}"
    )
    print(
        f"Development: {result.development_start.isoformat()} → "
        f"{result.development_end.isoformat()} sessions="
        f"{result.development_session_count} setups={result.development_setup_n} "
        f"executable={result.development_executable_n}"
    )
    print(f"Methodology: {result.methodological_label}")
    print(f"CAVEAT: {result.caveat}")
    base = next(
        item
        for item in result.partition_statistics
        if item.partition is ValidationPartition.EXPANDED_ALL
        and item.dimension == "BASE_ALL"
    )
    print("BASE_ALL full-sample horizons")
    for horizon in base.horizons:
        print(
            f"{horizon.horizon} executable={horizon.executable_n} "
            f"C/I={horizon.complete_n}/{horizon.incomplete_n} "
            f"MFE mean/median={horizon.mfe.mean}/{horizon.mfe.median} "
            f"MAE mean/median={horizon.mae.mean}/{horizon.mae.median} "
            f"balance mean/median={horizon.balance.mean}/{horizon.balance.median} "
            f">/=/<={horizon.favorable_adverse.mfe_greater}/"
            f"{horizon.favorable_adverse.equal}/"
            f"{horizon.favorable_adverse.mfe_less} "
            f"ratio={horizon.median_mfe_mae_ratio} zero-MAE={horizon.zero_mae_n}"
        )
    print("Validation partitions and monthly EOD table")
    for row in result.partition_statistics:
        eod = row.horizons[-1]
        print(
            f"{row.partition.value} {row.dimension} {row.state}: "
            f"setups={row.setup_n} executable={row.executable_n} "
            f"sessions={row.session_count} LONG/SHORT={row.long_n}/{row.short_n} "
            f"parent%={row.percentage_of_parent} "
            f"EOD={eod.mfe.median}/{eod.mae.median}/{eod.balance.median} "
            f">/=/<={eod.favorable_adverse.mfe_greater}/"
            f"{eod.favorable_adverse.equal}/{eod.favorable_adverse.mfe_less}"
        )
    print("Research stability records (descriptive; not trade scores)")
    for item in result.stability_scorecard:
        print(
            f"{item.dimension} {item.state}: n={item.total_executable_n} "
            f"sessions={item.distinct_sessions} months={item.months_represented} "
            f"positive/negative/zero/unavailable={item.positive_months}/"
            f"{item.negative_months}/{item.zero_months}/{item.unavailable_months} "
            f"monthly-balance min/median/max="
            f"{item.minimum_monthly_median_balance}/"
            f"{item.median_of_monthly_median_balances}/"
            f"{item.maximum_monthly_median_balance} "
            f"overall={item.overall_median_eod_balance} "
            f"month>25%={item.one_month_over_25_percent} "
            f"session>10%={item.one_session_over_10_percent}"
        )
    print("Direction-controlled Stage 10 EOD comparisons")
    for row in result.direction_controlled:
        eod = row.horizons[-1]
        print(
            f"{row.direction_scope.value} {row.dimension} {row.state}: "
            f"n={row.executable_n} sessions={row.session_count} "
            f"MFE/MAE/balance={eod.mfe.median}/{eod.mae.median}/"
            f"{eod.balance.median} >/=/<={eod.favorable_adverse.mfe_greater}/"
            f"{eod.favorable_adverse.equal}/{eod.favorable_adverse.mfe_less}"
        )
    print("Level-controlled Stage 10/11 EOD comparisons")
    for row in result.level_controlled:
        eod = row.horizons[-1]
        print(
            f"{row.level_scope.value} {row.dimension} {row.state}: "
            f"n={row.executable_n} sample={row.sample_size.value} "
            f"sessions={row.session_count} MFE/MAE/balance="
            f"{eod.mfe.median}/{eod.mae.median}/{eod.balance.median}"
        )
    print("Session concentration")
    for item in result.session_concentration:
        print(
            f"{item.dimension} {item.state}: setups/executable="
            f"{item.setup_n}/{item.executable_n} sessions={item.distinct_sessions} "
            f"median/max={item.median_setups_per_present_session}/"
            f"{item.maximum_single_session_n} largest1/5%="
            f"{item.largest_session_percentage}/{item.largest_five_sessions_percentage}"
        )
    print("Predeclared Stage 11 two-way relationships")
    for item in result.two_way_relationships:
        print(
            f"{item.left_dimension}={item.left_state} × "
            f"{item.right_dimension}={item.right_state}: setups={item.setup_n} "
            f"executable={item.executable_n} sessions={item.session_count} "
            f"LONG/SHORT={item.long_n}/{item.short_n} "
            f"below30={item.below_30_executable} EOD="
            f"{item.eod.mfe.median}/{item.eod.mae.median}/"
            f"{item.eod.balance.median}"
        )
    print("Leave-one-month-out sensitivity")
    for item in result.leave_one_month_out:
        print(
            f"{item.dimension} {item.state}: n={item.executable_n} "
            f"full={item.full_median_mfe}/{item.full_median_mae}/"
            f"{item.full_median_balance} exclusion-balance min/max="
            f"{item.minimum_exclusion_median_balance}/"
            f"{item.maximum_exclusion_median_balance} "
            f"sign-changes={item.sign_change_exclusions}"
        )
    print(
        f"Session bootstrap: seed={result.bootstrap_seed} "
        f"resamples={result.bootstrap_resamples}"
    )
    for item in result.bootstrap_uncertainty:
        intervals = " ".join(
            f"{value.metric}={value.p2_5}/{value.p50}/{value.p97_5}"
            for value in item.intervals
        )
        print(
            f"{item.dimension} {item.state}: n={item.executable_n} "
            f"sessions={item.session_count} {intervals}"
        )
    print("Development comparisons")
    for item in result.development_comparisons:
        print(
            f"{item.dimension} {item.state} vs {item.comparison_partition}: "
            f"n={item.development_n}/{item.comparison_n} sessions="
            f"{item.development_sessions}/{item.comparison_sessions} balance="
            f"{item.development_median_balance}/{item.comparison_median_balance} "
            f"difference={item.median_balance_difference} "
            f"sign-agrees={item.sign_agrees}"
        )
    print(f"Deterministic Stage 12.2 hash: {stability_report_hash(result)}")
    print("No strategy qualification, ranking, optimization, or trading metric added.")
    print("Status: PASS")


def _print_controlled_variant_selection(
    result: ControlledVariantSelectionReport,
) -> None:
    print("SPY STAGE 12.3 CONTROLLED STRATEGY-VARIANT SELECTION")
    print(
        f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}  "
        f"setups={result.expanded_setup_n} executable={result.expanded_executable_n}"
    )
    print(
        f"Development: {result.development_start.isoformat()} → "
        f"{result.development_end.isoformat()}"
    )
    print(f"CAVEAT: {result.caveat}")
    for evaluation in result.evaluations:
        expanded = evaluation.expanded
        levels = ",".join(
            f"{level.value}:{count}" for level, count in expanded.level_composition
        )
        print(f"VARIANT {evaluation.variant.value}")
        print(
            f"population setups/executable={expanded.setup_n}/{expanded.executable_n} "
            f"sessions/executable-sessions={expanded.session_count}/"
            f"{expanded.executable_session_count} months={expanded.month_coverage} "
            f"LONG/SHORT={expanded.long_n}/{expanded.short_n} "
            f"BASE_ALL%={expanded.percentage_of_base_all} "
            f"largest1/5-session%={evaluation.largest_session_percentage}/"
            f"{evaluation.largest_five_sessions_percentage} levels={levels}"
        )
        for label, partition in (
            ("DEVELOPMENT", evaluation.development),
            ("PRE_DEVELOPMENT", evaluation.pre_development),
            ("EXPANDED", evaluation.expanded),
        ):
            print(
                f"{label} setups/executable={partition.setup_n}/"
                f"{partition.executable_n} sessions={partition.session_count}"
            )
            for horizon in partition.horizons:
                print(
                    f"  {horizon.horizon} C/I={horizon.complete_n}/"
                    f"{horizon.incomplete_n} MFE mean/median={horizon.mfe.mean}/"
                    f"{horizon.mfe.median} MAE mean/median={horizon.mae.mean}/"
                    f"{horizon.mae.median} balance mean/median="
                    f"{horizon.net_excursion_balance.mean}/"
                    f"{horizon.net_excursion_balance.median} >/=/<="
                    f"{horizon.favorable_adverse.mfe_greater}/"
                    f"{horizon.favorable_adverse.equal}/"
                    f"{horizon.favorable_adverse.mfe_less} ratio-valid/zero/median="
                    f"{horizon.valid_ratio_n}/{horizon.zero_mae_n}/"
                    f"{horizon.median_mfe_mae_ratio}"
                )
        print("MONTHLY EOD")
        for partition in evaluation.monthly:
            eod = partition.horizons[-1]
            print(
                f"  {partition.partition.value} executable={partition.executable_n} "
                f"MFE/MAE/balance={eod.mfe.median}/{eod.mae.median}/"
                f"{eod.net_excursion_balance.median}"
            )
        print(
            f"monthly positive/zero/negative/unavailable="
            f"{evaluation.positive_months}/{evaluation.zero_months}/"
            f"{evaluation.negative_months}/{evaluation.unavailable_months}"
        )
        loo = evaluation.leave_one_month_out
        print(
            f"LOO full/min/max/sign-changes={loo.full_median_eod_balance}/"
            f"{loo.minimum_exclusion_median_balance}/"
            f"{loo.maximum_exclusion_median_balance}/{loo.sign_change_count} "
            f"exclusions={','.join(f'{month}:{value}' for month, value in loo.exclusions)}"
        )
        for direction in evaluation.direction_decomposition:
            eod = direction.horizons[-1]
            print(
                f"DIRECTION {direction.direction.value} setups/executable="
                f"{direction.setup_n}/{direction.executable_n} "
                f"sessions={direction.session_count} EOD="
                f"{eod.mfe.median}/{eod.mae.median}/"
                f"{eod.net_excursion_balance.median}"
            )
        if evaluation.bootstrap_uncertainty is not None:
            intervals = " ".join(
                f"{item.metric}={item.p2_5}/{item.p50}/{item.p97_5}"
                for item in evaluation.bootstrap_uncertainty.intervals
            )
            print(
                f"BOOTSTRAP seed={evaluation.bootstrap_uncertainty.seed} "
                f"resamples={evaluation.bootstrap_uncertainty.resamples} {intervals}"
            )
        else:
            print("BOOTSTRAP unavailable: INSUFFICIENT_COVERAGE")
        for criterion in evaluation.criteria:
            print(
                f"CRITERION {criterion.name.value} passed={criterion.passed} "
                f"observed={criterion.observed} required={criterion.required}"
            )
        print(
            f"SELECTION {evaluation.selection_label.value}: "
            f"{evaluation.label_reason}"
        )
    print(
        f"Deterministic Stage 12.3 hash: "
        f"{controlled_variant_selection_hash(result)}"
    )
    print("No stops, targets, exits, realized P/L, optimization, or Stage 13 logic added.")
    print("Status: PASS")


def _print_fixed_risk_simulation(result: FixedRiskSimulationReport) -> None:
    print("SPY STAGE 13.1 DETERMINISTIC FIXED-RISK SHARE SIMULATION")
    print(f"Range: {result.start_date.isoformat()} → {result.end_date.isoformat()}")
    print(f"CAVEAT: {result.caveat}")
    for population in result.populations:
        print(
            f"POPULATION {population.strategy_population.value} "
            f"confirmed-membership={population.confirmed_membership_n} "
            f"eligible-entry={population.eligible_entry_n}"
        )
    print(f"Frozen variants: {len(result.variants)}")
    for item in result.statistics:
        r = item.r_multiple
        pnl = item.price_pnl
        holding = item.holding_minutes
        levels = ",".join(
            f"{level.value}:{count}" for level, count in item.level_composition
        )
        print(
            f"VARIANT {item.strategy_population.value} "
            f"{item.variant.stop_model.value}/{item.variant.target_model.value} "
            f"eligible={item.eligible_setup_n} unavailable-atr={item.unavailable_atr_n} "
            f"simulated={item.executable_simulated_n} realized={item.realized_trade_n} "
            f"target/stop/eod/ambiguous={item.target_exit_n}/{item.stop_exit_n}/"
            f"{item.eod_exit_n}/{item.ambiguous_both_touched_n}"
        )
        print(
            f"  R mean/median={r.mean}/{r.median} "
            f"price-PnL mean/median={pnl.mean}/{pnl.median} "
            f"R +/-/0={item.positive_r_n}/{item.negative_r_n}/{item.zero_r_n} "
            f"win/loss%={item.win_rate_percentage}/{item.loss_rate_percentage} "
            f"holding mean/median={holding.mean}/{holding.median}"
        )
        print(
            "  monthly="
            + ",".join(
                f"{month.month}:{month.trade_n}:{month.median_r}"
                for month in item.monthly
            )
        )
        for direction in item.direction_decomposition:
            print(
                f"  direction={direction.direction.value} n={direction.trade_n} "
                f"R mean/median={direction.r_multiple.mean}/"
                f"{direction.r_multiple.median} PnL mean/median="
                f"{direction.price_pnl.mean}/{direction.price_pnl.median}"
            )
        print(f"  realized-levels={levels}")
    print("REPRESENTATIVE PATH AUDITS")
    audit_keys = (
        (TradeSimulationStatus.SIMULATED, TradeExitReason.STOP),
        (TradeSimulationStatus.SIMULATED, TradeExitReason.TARGET),
        (TradeSimulationStatus.SIMULATED, TradeExitReason.EOD_CLOSE),
        (TradeSimulationStatus.AMBIGUOUS_BOTH_TOUCHED, None),
        (TradeSimulationStatus.TRADE_UNAVAILABLE_ATR, None),
    )
    for status, reason in audit_keys:
        trade = next(
            (
                item
                for item in result.trades
                if item.exit_status is status
                and (reason is None or item.exit_reason is reason)
            ),
            None,
        )
        if trade is None:
            print(f"  {status.value}/{reason.value if reason else '-'}: NONE")
            continue
        ambiguity = (
            f" OHLC={trade.ambiguity.open}/{trade.ambiguity.high}/"
            f"{trade.ambiguity.low}/{trade.ambiguity.close}"
            if trade.ambiguity is not None
            else ""
        )
        print(
            f"  {status.value}/{reason.value if reason else '-'} "
            f"setup={trade.setup_identity} session={trade.session_date} "
            f"entry={trade.entry_timestamp}@{trade.entry_price} "
            f"stop={trade.stop_price} target={trade.target_price} "
            f"exit={trade.exit_timestamp}@{trade.exit_price} "
            f"R={trade.r_multiple} bars={trade.bars_observed}{ambiguity}"
        )
    print(
        f"Deterministic Stage 13.1 hash: {fixed_risk_simulation_hash(result)}"
    )
    print("Ambiguous both-touch trades are excluded from primary statistics.")
    print("No variant ranking, optimization, sizing, costs, options, or recommendation.")
    print("Status: PASS")


def _print_exit_model_comparison(result: ExitModelComparisonReport) -> None:
    print("SPY STAGE 13.2 CONTROLLED EXIT-MODEL COMPARISON")
    print(f"Range: {result.start_date} → {result.end_date}")
    print(f"CAVEAT: {result.caveat}")
    print(
        f"Variants: total={len(result.variants)} control=15 new=21 "
        f"bootstrap={result.bootstrap_resamples} seed={result.bootstrap_seed}"
    )
    for population in result.populations:
        print(
            f"POPULATION {population.strategy_population.value} "
            f"membership={population.confirmed_membership_n} "
            f"eligible-entry={population.eligible_entry_n}"
        )
    bootstrap_by_key = {
        (item.strategy_population, item.variant_id): item
        for item in result.bootstrap_uncertainty
    }
    for item in result.statistics:
        variant = item.variant
        bootstrap = bootstrap_by_key[
            (item.strategy_population, variant.variant_id)
        ]
        controls = ",".join(variant.corresponding_control_variant_ids)
        print(
            f"VARIANT {item.strategy_population.value} {variant.variant_id} "
            f"membership/atr/context={item.membership_n}/{item.atr_eligible_n}/"
            f"{item.target_context_eligible_n} realized/unavailable/ambiguous="
            f"{item.realized_n}/{item.unavailable_n}/{item.ambiguous_n}"
        )
        print(
            f"  exits stop/target/cross/time/eod={item.stop_exit_n}/"
            f"{item.target_exit_n}/{item.cross_exit_n}/{item.time_exit_n}/"
            f"{item.eod_exit_n} R mean/median/std={item.r_multiple.mean}/"
            f"{item.r_multiple.median}/{item.r_standard_deviation} "
            f"R +/-/0={item.positive_r_n}/{item.negative_r_n}/{item.zero_r_n} "
            f"win/loss%={item.win_rate_percentage}/{item.loss_rate_percentage} "
            f"holding mean/median={item.holding_minutes.mean}/"
            f"{item.holding_minutes.median} sessions={item.session_count}"
        )
        print(
            "  monthly="
            + ",".join(
                f"{row.month}:{row.trade_n}:{row.mean_r}:{row.median_r}:"
                f"{row.positive_n}/{row.negative_n}/{row.zero_n}"
                for row in item.monthly
            )
        )
        print(
            "  partitions="
            + ",".join(
                f"{row.partition}:{row.trade_n}:{row.mean_r}:{row.median_r}"
                for row in item.partitions
            )
            + f" positive/negative-months={item.positive_month_n}/"
            f"{item.negative_month_n}"
        )
        print(
            "  leave-one-month-out="
            + ",".join(
                f"{row.excluded_month}:{row.trade_n}:{row.mean_r}:{row.median_r}"
                for row in item.leave_one_month_out
            )
        )
        if item.direction_composition:
            print(
                "  directions="
                + ",".join(
                    f"{row.name}:{row.trade_n}:{row.r_multiple.mean}:"
                    f"{row.r_multiple.median}"
                    for row in item.direction_composition
                )
            )
        print(
            "  levels="
            + ",".join(
                f"{level.value}:{count}" for level, count in item.level_composition
            )
            + f" controls={controls}"
        )
        print(
            "  bootstrap="
            + ",".join(
                f"{row.metric}:{row.p2_5}/{row.p50}/{row.p97_5}"
                for row in bootstrap.intervals
            )
            + f" label={bootstrap.label}"
        )
    print("REPRESENTATIVE NEW PATH AUDITS")
    reasons = (
        ExitModelExitReason.OPPOSITE_EMA9_20_CROSS,
        ExitModelExitReason.OPPOSITE_EMA9_VWAP_CROSS,
        ExitModelExitReason.OPPOSITE_EMA20_VWAP_CROSS,
        ExitModelExitReason.TIME_15M,
        ExitModelExitReason.NEXT_OBJECTIVE_LEVEL,
        ExitModelExitReason.EOD_CLOSE,
        ExitModelExitReason.AMBIGUOUS_BOTH_TOUCHED,
        ExitModelExitReason.UNAVAILABLE_OBJECTIVE,
        ExitModelExitReason.UNAVAILABLE_ATR,
    )
    for reason in reasons:
        trade = next(
            (item for item in result.new_trades if item.exit_reason is reason),
            None,
        )
        if trade is None:
            print(f"  {reason.value}: NONE")
            continue
        ambiguity = (
            f" OHLC={trade.ambiguity.open}/{trade.ambiguity.high}/"
            f"{trade.ambiguity.low}/{trade.ambiguity.close}"
            if trade.ambiguity is not None
            else ""
        )
        print(
            f"  {reason.value} setup={trade.setup_identity} session={trade.session_date} "
            f"variant={trade.variant.variant_id} entry={trade.entry_timestamp}@"
            f"{trade.entry_price} stop={trade.stop_price} objective="
            f"{trade.objective_price} scheduled={trade.scheduled_exit} exit="
            f"{trade.exit_timestamp}@{trade.exit_price} R={trade.r_multiple} "
            f"bars={trade.bars_observed}{ambiguity}"
        )
    print(
        f"Embedded Stage 13.1 hash: "
        f"{fixed_risk_simulation_hash(result.stage13_1_control)}"
    )
    print(f"Deterministic Stage 13.2 hash: {exit_model_comparison_hash(result)}")
    print(
        "Bootstrap intervals are descriptive uncertainty intervals, "
        "not predictive CIs."
    )
    print("No exit ranking, selection, optimization, or recommendation.")
    print("Status: PASS")


def _print_execution_variant_classification(
    result: ExecutionVariantClassificationReport,
) -> None:
    print("SPY STAGE 13.3 CONTROLLED EXECUTION-VARIANT CLASSIFICATION")
    print(f"Range: {result.start_date} → {result.end_date}")
    print(f"CAVEAT: {result.caveat}")
    for row in result.rows:
        gates = row.gates
        warnings = ",".join(item.value for item in row.warnings) or "NONE"
        print(
            f"VARIANT BASE_SHORT {row.variant_id} family={row.family.value} "
            f"stop={row.stop_multiplier} exit={row.exit_definition} "
            f"realized/sessions={row.realized_paths}/{row.session_count}"
        )
        print(
            f"  expanded mean/median={row.expanded_mean_r}/{row.expanded_median_r} "
            f"jan-jul={row.january_july_mean_r}/{row.january_july_median_r} "
            f"august={row.development_mean_r}/{row.development_median_r}"
        )
        print(
            f"  months +/-/0={row.positive_month_count}/"
            f"{row.negative_month_count}/{row.zero_month_count} "
            f"worst-loo-mean={row.worst_loo_mean_r} bootstrap-mean="
            f"{row.bootstrap_mean_p2_5}/{row.bootstrap_mean_p50}/"
            f"{row.bootstrap_mean_p97_5}"
        )
        print(
            "  gates "
            f"realized100={gates.realized_paths_at_least_100} "
            f"sessions50={gates.represented_sessions_at_least_50} "
            f"expanded-mean={gates.expanded_mean_positive} "
            f"expanded-median={gates.expanded_median_positive} "
            f"jan-jul-mean={gates.january_july_mean_positive} "
            f"august-mean={gates.development_mean_positive} "
            f"worst-loo={gates.worst_loo_mean_nonnegative} "
            f"positive-months={gates.at_least_five_positive_monthly_medians} "
            f"bootstrap-lower={gates.bootstrap_mean_lower_bound_positive}"
        )
        print(f"  CLASSIFICATION {row.classification.value} WARNINGS {warnings}")
    print("STAGE 14 HANDOFF")
    print(f"  robust-candidates={len(result.handoff.robust_candidates)}")
    print(
        "  forward-test-candidates="
        + (",".join(result.handoff.forward_test_candidates) or "NONE")
    )
    print(f"  controls={len(result.handoff.controls)}")
    print(f"  rejected={len(result.handoff.rejected_variants)}")
    print(f"  framing={result.handoff.framing}")
    print(
        "Deterministic Stage 13.3 hash: "
        f"{execution_variant_classification_hash(result)}"
    )
    print(f"Source Stage 13.2 hash: {result.source_stage13_2_hash}")
    print(f"Source Stage 13.1 hash: {result.source_stage13_1_hash}")
    print("No ranking, optimization, new execution model, persistence, or Stage 14.")
    print("Status: PASS")


def _print_signal_replay(result: SignalReplayReport) -> None:
    print("SPY STAGE 14.1 DETERMINISTIC INCREMENTAL SIGNAL REPLAY")
    print(f"Range: {result.start_date} → {result.end_date}")
    print(f"CAVEAT: {result.caveat}")
    print(
        f"INPUT raw={result.raw_bar_count} rth-1m={result.rth_one_minute_count} "
        f"self-built-5m={result.five_minute_count} seeds={result.break_seed_count}"
    )
    print(
        f"SETUPS confirmed={result.confirmed_signal_count} "
        f"executable={result.executable_signal_count} "
        f"base-short={result.base_short_confirmed_count} "
        f"base-short-executable={result.base_short_executable_count}"
    )
    for item in result.sessions:
        print(
            f"SESSION {item.session_date} raw/pre/rth/5m="
            f"{item.raw_bar_count}/{item.premarket_bar_count}/"
            f"{item.rth_one_minute_count}/{item.five_minute_count} "
            f"seeds/signals/executable={item.break_seed_count}/"
            f"{item.confirmed_signal_count}/{item.executable_signal_count} "
            f"short/short-executable={item.base_short_confirmed_count}/"
            f"{item.base_short_executable_count} ema9/ema20/atr-valid="
            f"{item.ema9_valid_count}/{item.ema20_valid_count}/"
            f"{item.atr14_valid_count} crosses={item.ema9_ema20_cross_count}/"
            f"{item.ema9_vwap_cross_count}/{item.ema20_vwap_cross_count} "
            f"levels-pd/pm/or={item.previous_day_levels_available}/"
            f"{item.premarket_levels_available}/{item.opening_levels_available}"
        )
    for signal in result.signals:
        print(
            f"SIGNAL {signal.signal_known_at.isoformat()} {signal.setup_identity} "
            f"{signal.direction.value} {signal.triggering_level_type.value}@"
            f"{signal.triggering_level_price} break={signal.break_timestamp.isoformat()} "
            f"confirmation={signal.confirmation_type.value}@"
            f"{signal.confirmation_candle_timestamp.isoformat()} "
            f"executable={signal.same_session_executable} "
            f"base-short={signal.base_short_membership} candidates="
            f"{','.join(signal.eligible_stage14_candidate_ids) or 'NONE'}"
        )
    reconciliation = result.batch_reconciliation
    print(
        f"BATCH-RECONCILIATION exact={reconciliation.exact_match} "
        f"seeds={reconciliation.replay_break_seed_count}/"
        f"{reconciliation.batch_break_seed_count} "
        f"confirmed={reconciliation.replay_confirmed_count}/"
        f"{reconciliation.batch_confirmed_count} executable="
        f"{reconciliation.replay_executable_count}/"
        f"{reconciliation.batch_executable_count} base-short="
        f"{reconciliation.replay_base_short_confirmed_count}/"
        f"{reconciliation.batch_base_short_confirmed_count} "
        f"base-short-executable="
        f"{reconciliation.replay_base_short_executable_count}/"
        f"{reconciliation.batch_base_short_executable_count} mismatches="
        f"{len(reconciliation.mismatched_setup_identities)}"
    )
    print(
        f"Processed five-minute exact match: "
        f"{result.processed_five_minute_exact_match}"
    )
    print(f"Session-chunk replay exact match: {result.session_chunk_replay_exact_match}")
    print(f"Deterministic Stage 14.1 hash: {signal_replay_hash(result)}")
    print("Offline, read-only, non-persistent; no orders, fills, P/L, or Stage 14.2.")
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
