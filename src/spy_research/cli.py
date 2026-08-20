"""Local command-line utilities for the research foundation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

import yaml
from pydantic import ValidationError

from spy_research.config import DEFAULT_CONFIG_PATH, load_research_config
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

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
