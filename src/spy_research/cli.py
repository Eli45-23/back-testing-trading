"""Local command-line utilities for the research foundation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from pathlib import Path
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
from spy_research.market import MarketSessionClassifier, SessionSummary, SessionType
from spy_research.research_run import ResearchRun


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


if __name__ == "__main__":
    raise SystemExit(main())
