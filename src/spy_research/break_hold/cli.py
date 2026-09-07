"""Thin CLI wiring and explicit missing-session historical downloads."""
import json
from argparse import Namespace
from pathlib import Path

from spy_research.bars.store import DEFAULT_PROCESSED_DATA_ROOT, ProcessedFiveMinuteStore
from spy_research.config import DEFAULT_CONFIG_PATH, load_research_config
from spy_research.data.coverage import inventory
from spy_research.data.raw_store import DEFAULT_RAW_DATA_ROOT, RawBarStore
from spy_research.break_hold.reporting import export_csv, render_report
from spy_research.break_hold.service import run_break_hold


def add_commands(subparsers, parse_date):
    for name in ("data-coverage", "fill-missing-data", "break-hold"):
        p = subparsers.add_parser(name, help=f"Historical research: {name}")
        p.add_argument("--start", type=parse_date, required=True)
        p.add_argument("--end", type=parse_date, required=True)
        p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
        p.add_argument("--raw-data-root", type=Path, default=DEFAULT_RAW_DATA_ROOT)
        p.add_argument("--processed-data-root", type=Path, default=DEFAULT_PROCESSED_DATA_ROOT)
        p.add_argument("--json", action="store_true")
        p.add_argument("--output", type=Path)
        if name == "break-hold":
            p.add_argument("--events", action="store_true")
            p.add_argument("--csv", type=Path)


def handle(args: Namespace) -> int:
    config = load_research_config(args.config)
    store = RawBarStore(config, root=args.raw_data_root)
    processed = ProcessedFiveMinuteStore(root=args.processed_data_root) if args.command == "data-coverage" else None
    coverage = inventory(config, store, args.start, args.end, processed)
    if args.command == "fill-missing-data":
        # No credentials are loaded unless a download is actually necessary.
        missing = [x for x in coverage if x.raw_status != "VALID"]
        if missing:
            from spy_research.alpaca import AlpacaDataClient, HistoricalStockDataService
            from spy_research.config import load_settings
            settings = load_settings(args.config)
            with AlpacaDataClient.from_environment(settings.alpaca) as client:
                source = HistoricalStockDataService(client, config)
                for item in missing:
                    bars = source.fetch_stock_bars(start=item.session_date, end=item.session_date)
                    result = store.persist_bars(bars.bars)
                    print(f"{item.session_date}: received={result.bars_received}, new={result.new_bars}, conflicts={result.conflicts}")
            coverage = inventory(config, store, args.start, args.end)
    if args.command == "break-hold":
        report = run_break_hold(config, store, args.start, args.end, coverage=coverage)
        text = report.model_dump_json(indent=2) if args.json else render_report(report)
        if args.events and not args.json:
            text += "\n" + "\n".join(e.model_dump_json() for s in report.sessions for e in s.events)
        if args.csv:
            args.csv.parent.mkdir(parents=True, exist_ok=True)
            args.csv.write_text(export_csv(report), encoding="utf-8")
    else:
        text = json.dumps([x.model_dump(mode="json") for x in coverage], indent=2) if args.json else (
            f"Expected={len(coverage)}; present={sum(x.raw_status!='MISSING' for x in coverage)}; validated={sum(x.raw_status=='VALID' for x in coverage)}; "
            f"missing={sum(x.raw_status=='MISSING' for x in coverage)}; invalid={sum(x.raw_status=='INVALID' for x in coverage)}\n" +
            "\n".join(f"{x.session_date}: raw={x.raw_status}, RTH={x.observed_minutes}/{x.expected_minutes}, processed={x.processed_status}, errors={','.join(x.errors)}" for x in coverage))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text+"\n", encoding="utf-8")
        print(f"Report written: {args.output}")
    else:
        print(text)
    return 0 if all(x.raw_status == "VALID" for x in coverage) else 2
