"""Local audit driver; outcome execution requires an explicit --outcomes flag."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
START, END, CONTEXT_START = date(2026, 1, 2), date(2026, 9, 4), date(2025, 12, 22)
COMMIT = "0572548e8ac602bba4f13c7a54ebcbfe22012249"
OPENED = set()


def audit(event, args):
    if event in ("socket.connect", "socket.getaddrinfo", "socket.bind"):
        raise RuntimeError("Network prohibited in KLR discovery")
    if event == "open" and isinstance(args[0], (str, bytes)):
        name = str(args[0])
        if name.endswith(".parquet"):
            match = re.search(r"(\d{4}-\d{2}-\d{2})\.parquet$", name)
            if not match or not CONTEXT_START <= date.fromisoformat(match[1]) <= END:
                raise RuntimeError("Historical partition outside fixed permitted range")
            OPENED.add(str(Path(name).resolve().relative_to(ROOT)))


sys.addaudithook(audit)
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.validation import RawDataValidator
from spy_research.market import XNYSCalendar
from spy_research.break_hold.prospective_freeze import verify_freeze
from spy_research.key_level_reactions.protocol import NY, minute_sequence
from spy_research.key_level_reactions.reporting import fingerprint, source_fingerprint, protocol_fingerprint


def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, sort_keys=True, indent=2, default=str) + "\n")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def coverage():
    import subprocess
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == COMMIT
    assert not subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).strip()
    frozen = verify_freeze()
    print("Frozen baseline verified:", len(frozen["frozen_files"]), flush=True)
    cal = XNYSCalendar()
    cfg = load_research_config()
    current = RawBarStore(cfg, root=ROOT / "data/raw")
    context = RawBarStore(cfg, root=ROOT / "data/oos/raw")
    bars, owners, sources = [], [], []
    day = CONTEXT_START
    while day <= END:
        store = context if day < START else current
        path = store.partition_path(day)
        if path.exists():
            # Date checks precede every file read, including its hash.
            assert CONTEXT_START <= day <= END
            sources.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path)})
            part = store.load_partition(day)
            bars.extend(part)
            owners.extend([day] * len(part))
        day += timedelta(days=1)
    minute_sequence(bars)
    report = RawDataValidator(cal).validate_raw_bars(
        bars, symbol="SPY", start_date=CONTEXT_START, end_date=END, partition_dates=owners)
    write_json("coverage_raw.json", report.model_dump(mode="json"))
    stats = {s.session_date: s for s in report.session_stats}
    certified = {d for d, s in stats.items() if s.premarket_missing_minutes == 0 and s.premarket_bars == s.premarket_possible_minutes}
    sessions = [s for s in report.session_stats if s.session_date >= START]
    view = tuple(b for b in bars if not (
        b.timestamp.astimezone(NY).date() not in certified
        and 4 <= b.timestamp.astimezone(NY).hour
        and b.timestamp < cal.session_for_date(b.timestamp.astimezone(NY).date()).market_open))
    daily = []
    for s in sessions:
        d = s.session_date
        prev = d - timedelta(days=1)
        while not cal.session_for_date(prev).is_trading_day:
            prev -= timedelta(days=1)
        monday = d - timedelta(days=d.weekday())
        week = [monday - timedelta(days=7-i) for i in range(7)]
        needed = [x for x in week if cal.session_for_date(x).is_trading_day]
        valid = lambda x: x in stats and stats[x].missing_rth_bars == 0 and stats[x].extra_rth_bars == 0
        daily.append({**s.model_dump(mode="json"),
            "premarket_certified": d in certified,
            "PMH_PML_status": "AVAILABLE_COMPLETE_GRID" if d in certified else "UNAVAILABLE_UNCERTIFIED_PREMARKET",
            "previous_session": str(prev), "previous_session_valid": valid(prev),
            "previous_week_sessions": [str(x) for x in needed],
            "previous_week_valid": all(valid(x) for x in needed),
            "ORH5_ORL5_valid": s.missing_rth_bars == 0,
            "swing_context_start": str(CONTEXT_START)})
    summary = {"passed_rth": report.passed,
        "development_sessions": len(sessions), "context_sessions": len(stats)-len(sessions),
        "expected_rth_minutes": sum(s.expected_rth_bars for s in sessions),
        "observed_rth_minutes": sum(s.observed_rth_bars for s in sessions),
        "missing_rth_minutes": sum(s.missing_rth_bars for s in sessions),
        "duplicates": report.duplicate_keys,
        "premarket_certified_sessions": sum(s.session_date in certified for s in sessions),
        "premarket_unavailable_sessions": sum(s.session_date not in certified for s in sessions),
        "premarket_expected_minutes": sum(s.premarket_possible_minutes for s in sessions),
        "premarket_observed_minutes": sum(s.premarket_bars for s in sessions),
        "prior_session_unavailable": sum(not d["previous_session_valid"] for d in daily),
        "prior_week_unavailable": sum(not d["previous_week_valid"] for d in daily),
        "early_closes": [str(s.session_date) for s in sessions if s.is_early_close],
        "context_early_closes": [str(s.session_date) for s in report.session_stats if s.session_date < START and s.is_early_close],
        "error_codes": dict(Counter(i.code for i in report.issues if i.severity == "ERROR")),
        "withheld_uncertified_premarket_rows_including_context": len(bars)-len(view)}
    write_json("coverage_sessions.json", daily)
    write_json("coverage_summary.json", summary)
    provenance = {"git_commit": COMMIT, "engine_source_hash": source_fingerprint(),
        "protocol_hash": protocol_fingerprint(), "reporting_plan_hash": digest(OUT / "reporting_plan.md"),
        "raw_record_hash": fingerprint(bars), "validated_input_view_hash": fingerprint(view),
        "input_partitions": sources, "outcome_start": START, "outcome_end": END,
        "context_start": CONTEXT_START, "context_end": START-timedelta(days=1),
        "coverage_checked_at_utc": datetime.now(timezone.utc),
        "freeze_hashes_before": len(frozen["frozen_files"]),
        "historical_outcomes_previously_inspected": False,
        "network_policy": "DENIED", "prospective_data_policy": "DENIED",
        "opened_historical_partitions": sorted(OPENED)}
    write_json("run_manifest.json", provenance)
    print(json.dumps(summary, sort_keys=True), flush=True)
    if not report.passed or summary["prior_session_unavailable"] or summary["prior_week_unavailable"]:
        raise RuntimeError("Coverage gate failed; no outcome execution")
    return view, cal, provenance


def export_rows(name, rows):
    import gzip
    with (OUT / (name + ".jsonl.gz")).open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream:
            for row in rows:
                line = row.model_dump_json() if hasattr(row, "model_dump_json") else json.dumps(row, sort_keys=True, default=str)
                stream.write((line + "\n").encode())


def run_outcomes(view, cal, manifest):
    from spy_research.key_level_reactions.historical_inputs import validate_bars
    from spy_research.key_level_reactions.levels import generate
    from spy_research.key_level_reactions.higher_timeframes import hours
    from spy_research.key_level_reactions.registry import Registry
    from spy_research.key_level_reactions.interactions import build_ledger
    from spy_research.key_level_reactions.models import Ledger
    from spy_research.key_level_reactions.outcomes import reactions
    from spy_research.key_level_reactions.reversals import detect
    from spy_research.key_level_reactions.confluence import relationships
    from spy_research.key_level_reactions.next_level import snapshot, relative_to_reaction
    from spy_research.key_level_reactions.indicators import AtrAsOf
    from spy_research.key_level_reactions.reporting import counts, family_summaries, session_uncertainty
    print("Coverage gate accepted; generating causal levels", flush=True)
    data = validate_bars(view, CONTEXT_START, START, END, cal)
    levels = generate(data, cal)
    export_rows("level_inventory", levels.levels)
    export_rows("level_availability_issues", levels.issues)
    export_rows("pivot_audits", levels.pivot_audits)
    hour_rows = hours(data.bars, cal)
    export_rows("hour_context_inventory", hour_rows)
    registry = Registry(levels.levels)
    by_day = {}
    for bar in data.bars:
        d = bar.timestamp.astimezone(NY).date()
        s = cal.session_for_date(d)
        if s.market_open <= bar.timestamp < s.market_close:
            by_day.setdefault(d, []).append(bar)
    rth = tuple(b for day in by_day.values() for b in day)
    print("Level inventory", len(levels.levels), dict(Counter(x.family for x in levels.levels)), flush=True)
    full = build_ledger(rth, registry, cal)
    ledger = Ledger(touches=tuple(t for t in full.touches if t.start.astimezone(NY).date() >= START),
        episodes=tuple(e for e in full.episodes if e.start.astimezone(NY).date() >= START),
        gap_crosses=tuple(g for g in full.gap_crosses if g.start.astimezone(NY).date() >= START))
    del full
    export_rows("touches", ledger.touches)
    export_rows("episodes", ledger.episodes)
    export_rows("gap_crosses", ledger.gap_crosses)
    print("Ledger complete", dict(counts(ledger, ())), flush=True)
    by_id = {x.id: x for x in levels.levels}
    outcomes, nexts, nextr = [], [], []
    for i, ep in enumerate(ledger.episodes):
        source = by_day[ep.start.astimezone(NY).date()]
        measured = reactions(ep, by_id[ep.level_id], source)
        outcomes.extend(measured)
        nxt = snapshot(ep, by_id[ep.level_id], registry, source)
        nexts.append(nxt)
        nextr.extend(relative_to_reaction(nxt, r, ep) for r in measured)
        if (i+1) % 1000 == 0:
            print("Reaction episodes measured", i+1, flush=True)
    export_rows("reactions", outcomes)
    export_rows("next_levels", nexts)
    export_rows("next_level_reactions", nextr)
    reversals = detect(tuple(b for b in rth if b.timestamp.astimezone(NY).date() >= START))
    export_rows("reversals", reversals)
    sessions = tuple(c.session for c in data.coverage if c.session >= START)
    export_rows("family_summaries", family_summaries(levels, ledger, outcomes, sessions))
    print("Calculating committed session bootstrap", flush=True)
    export_rows("session_uncertainty", session_uncertainty(levels, ledger, outcomes, sessions))
    write_json("denominators.json", dict(counts(ledger, outcomes)))
    print("Streaming independent confluence identities", flush=True)
    atr = AtrAsOf(rth, cal)
    relation_counts = Counter()
    def links(kind, observations):
        for i, obs in enumerate(observations):
            if kind == "reversal":
                price, at, source_ids = obs.turning_price, obs.turning_start, ()
            else:
                level = by_id[obs.level_id]
                price, at, source_ids = level.price, obs.start, level.source_ids
            for link in relationships(obs.id, price, at, registry, source_ids, atr.at(at), cal):
                assert link.available_at <= at
                relation_counts[kind] += 1
                yield link
            if (i+1) % 1000 == 0:
                print("Relationships", kind, i+1, "/", len(observations), flush=True)
    export_rows("episode_relationships", links("episode", ledger.episodes))
    export_rows("touch_relationships", links("touch", ledger.touches))
    export_rows("reversal_relationships", links("reversal", reversals))
    manifest.update(outcome_execution_complete=True, outcome_completed_at_utc=datetime.now(timezone.utc),
        relationship_counts=dict(relation_counts), frozen_hashes_after_outcomes=len(verify_freeze()["frozen_files"]),
        driver_hash=digest(Path(__file__)), opened_historical_partitions=sorted(OPENED),
        context_full_hours=sum(h.start.astimezone(NY).date() < START for h in hour_rows),
        development_full_hours=sum(h.start.astimezone(NY).date() >= START for h in hour_rows),
        pre_outcome_confirmed_swings=sum(x.family.startswith("1H") and x.available_at.astimezone(NY).date() < START for x in levels.levels))
    assert source_fingerprint() == manifest["engine_source_hash"]
    manifest["output_hashes"] = {p.name: digest(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "run_manifest.json"}
    write_json("run_manifest.json", manifest)
    print("Outcome run complete; frozen hashes", manifest["frozen_hashes_after_outcomes"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outcomes", action="store_true")
    args = parser.parse_args()
    if (OUT / "blocker.json").exists():
        raise RuntimeError("Known committed-engine blocker: review required before another study run")
    data, calendar, manifest = coverage()
    if args.outcomes:
        run_outcomes(data, calendar, manifest)
