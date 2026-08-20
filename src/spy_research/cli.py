"""Local command-line utilities for the research foundation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml
from pydantic import ValidationError

from spy_research.alpaca import AlpacaDataClient, HistoricalStockDataService
from spy_research.alpaca.errors import AlpacaDataError
from spy_research.config import DEFAULT_CONFIG_PATH, load_research_config, load_settings
from spy_research.data.errors import RawDataError
from spy_research.data.raw_store import DEFAULT_RAW_DATA_ROOT, RawBarStore
from spy_research.data.validation import DataValidationReport, RawDataValidator
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


if __name__ == "__main__":
    raise SystemExit(main())
