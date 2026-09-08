"""Standalone local-only entry point, intentionally not in the shared CLI.

Importing or requesting --help never reads market partitions. A study requires
an explicit --run flag; this implementation phase does not invoke that flag.
"""
import argparse
from datetime import date

from .protocol import guard_dates, guard_outcomes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline descriptive Key-Level Reactions V1")
    parser.add_argument("--raw-root", required=True)
    parser.add_argument("--context-start", type=date.fromisoformat, required=True)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--run", action="store_true", help="Explicitly build descriptive report to stdout")
    args = parser.parse_args(argv)
    guard_dates(args.context_start,args.end)
    guard_outcomes(args.start,args.end)
    if not args.run:
        parser.error("No study started: --run is required")
    from spy_research.config import load_research_config
    from spy_research.data.raw_store import RawBarStore
    from .historical_inputs import load_local
    from .service import build_report
    from .reporting import canonical
    data = load_local(RawBarStore(load_research_config(),root=args.raw_root),
        context_start=args.context_start,outcome_start=args.start,end=args.end)
    print(canonical(build_report(data)),end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
