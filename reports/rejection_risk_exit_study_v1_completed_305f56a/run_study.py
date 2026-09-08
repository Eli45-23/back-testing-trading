"""Authorized offline execution companion; frozen kernels are imported unchanged.

This file is a run artifact, not a protocol revision or a new strategy engine.
Run from repository root with .venv/bin/python -B <this path>.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "reports/rejection_entry_study_v1_completed_a3909ea"
COMMIT = "305f56a0ff607de34bafe8f528226192a5086bf6"
START, END = date(2026, 1, 2), date(2026, 9, 4)
NY = ZoneInfo("America/New_York")
getcontext().prec = 80
getcontext().rounding = ROUND_HALF_EVEN
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))


def encode(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal, Path)):
        return str(value)
    raise TypeError(type(value).__name__)


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, default=encode) + "\n")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def frozen_checks():
    from spy_research.break_hold.prospective_freeze import verify_freeze
    from spy_research.rejection_risk_exit_v1.protocol import protocol_hash
    frozen = json.loads((ROOT / "reports/rejection_risk_exit_study_v1/freeze_manifest.json").read_text())
    assert frozen["protocol_sha256"] == protocol_hash()
    result = {"protocol_sha256": protocol_hash()}
    for section in ("source_files", "dependency_files"):
        for name, expected in frozen[section].items():
            assert digest(ROOT / name) == expected, name
        result[section] = len(frozen[section])
    result["break_hold"] = len(verify_freeze(ROOT)["frozen_files"])
    for directory, count in (("key_level_reactions_v1", 15),
                             ("key_level_reactions_v1_completed_ae8e870", 63),
                             ("rejection_entry_study_v1_completed_a3909ea", 29)):
        folder = ROOT / "reports" / directory
        manifest = json.loads((folder / "run_manifest.json").read_text())
        assert len(manifest["output_hashes"]) == count
        for name, expected in manifest["output_hashes"].items():
            assert digest(folder / name) == expected, name
        result[directory] = count
    return result


def stream(path):
    with gzip.open(path, "rt") as handle:
        for line in handle:
            yield json.loads(line)


def context_of(item, confluence_counts):
    def boolean(value):
        return "UNKNOWN" if value is None else str(value)
    close_count, breach_count = item["prior_close_through_count"], item["prior_breach_count"]
    breach = ("UNKNOWN" if close_count is None or breach_count is None else
              "COMPLETED_CLOSE_THROUGH" if close_count else
              "PENETRATED_NO_CLOSE_THROUGH" if breach_count else "NEVER_BREACHED")
    at = datetime.fromisoformat(item["first_touch_at"].replace("Z", "+00:00")).astimezone(NY)
    minute = at.hour * 60 + at.minute
    tod = next(label for end, label in ((600, "09:30-10:00"), (660, "10:00-11:00"),
               (720, "11:00-12:00"), (840, "12:00-14:00"), (900, "14:00-15:00"),
               (960, "15:00-close")) if minute < end)
    n = confluence_counts[item["interaction_id"]]
    assert n >= 1, "Own level identity absent from frozen confluence relationships"
    first_session = item["first_same_session_touch"]
    return {"level_family": item["level_family"],
            "creation_first_touch": boolean(item["first_interaction_since_creation"]),
            "same_session_touch": "UNKNOWN" if first_session is None else "1" if first_session else "REPEATED",
            "breach_history": breach, "time_of_day": tod,
            "approach_side": item["approach_side"],
            "confluence": "ISOLATED" if n == 1 else "TWO_IDENTITIES" if n == 2 else "THREE_PLUS_IDENTITIES"}


def run():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head == COMMIT
    assert not subprocess.check_output(["git", "diff", "HEAD", "--name-only"], cwd=ROOT, text=True).strip()
    assert not (OUT / "outcomes.jsonl.gz").exists(), "Never overwrite a completed row-level export"
    before = frozen_checks()
    save("freeze_checks_before.json", before)
    source_manifest = json.loads((SOURCE / "run_manifest.json").read_text())
    inputs = []
    for item in source_manifest["input_partitions"]:
        day = date.fromisoformat(Path(item["path"]).stem)
        if START <= day <= END:
            inputs.append(dict(item, session_date=day.isoformat()))
    allow = {(ROOT / p["path"]).resolve() for p in inputs}
    assert len(allow) == len(inputs) == 170
    opened, network_attempts = set(), []

    def access_guard(event, args):
        if event in ("socket.connect", "socket.connect_ex", "socket.getaddrinfo", "http.client.connect"):
            network_attempts.append(event)
            raise RuntimeError("Network access prohibited by frozen study")
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if path.name == ".env":
                raise RuntimeError("Credential access prohibited")
            if path.suffix == ".parquet":
                if path not in allow or date.fromisoformat(path.stem) > END:
                    raise RuntimeError("Market partition outside exact development allowlist")
                opened.add(str(path.relative_to(ROOT)))
    sys.addaudithook(access_guard)

    import pyarrow.parquet as pq
    from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
    from spy_research.data.schemas import RAW_BAR_SCHEMA, RawBarRecord
    from spy_research.data.validation import RawDataValidator
    from spy_research.market import MarketSessionClassifier, XNYSCalendar
    from spy_research.rejection_entry_v1.engine import first_executable_minute
    from spy_research.rejection_entry_v1.models import EntrySignal, MinuteBar
    from spy_research.rejection_risk_exit_v1.engine import simulate
    from spy_research.rejection_risk_exit_v1.protocol import ENTRIES, MODELS, PROTOCOL

    calendar = XNYSCalendar()
    expected_days = []
    for i in range((END - START).days + 1):
        day = START + timedelta(days=i)
        if calendar.session_for_date(day).is_trading_day:
            expected_days.append(day.isoformat())
    assert expected_days == sorted(p["session_date"] for p in inputs)
    assert len(ENTRIES) == 2 and len(MODELS) == 16
    interactions = {x["interaction_id"]: x for x in stream(SOURCE / "interactions.jsonl.gz")}
    confluence = Counter()
    for x in stream(SOURCE / "relationships.jsonl.gz"):
        if x["bucket"] in ("0", "0.05", "0.10", "0.25"):
            confluence[x["observation_id"]] += 1
    signals = defaultdict(list)
    source_counts, eligible_counts = Counter(), Counter()
    seen = set()
    for x in stream(SOURCE / "signals.jsonl.gz"):
        variant = x.pop("variant")
        key = (variant, x["interaction_id"], x["session_date"])
        assert key not in seen
        seen.add(key)
        if variant not in ENTRIES:
            source_counts[f"{variant}:OUTSIDE_FROZEN_ENTRY_MATRIX"] += 1
            continue
        if x["status"] != "CONFIRMED" or x["executable_entry_timestamp"] is None:
            source_counts[f"{variant}:NON_EXECUTABLE:{x['status']}"] += 1
            continue
        signal = EntrySignal.model_validate(x)
        assert START <= signal.session_date <= END
        assert signal.approach_side in ("ABOVE", "BELOW")
        assert signal.signal_known_at == signal.confirmation_start_at + timedelta(minutes=signal.confirmation_timeframe_minutes)
        item = interactions[signal.interaction_id]
        assert item["session_date"] == signal.session_date.isoformat()
        assert item["level_id"] == signal.level_id and item["approach_side"] == signal.approach_side
        context = context_of(item, confluence)
        signals[signal.session_date].append((variant, signal, context))
        eligible_counts[variant] += 1
        source_counts[f"{variant}:ELIGIBLE_EXECUTABLE"] += 1
    assert dict(eligible_counts) == {ENTRIES[0]: 3311, ENTRIES[1]: 6024}
    save("source_population_reconciliation.json", {"counts": source_counts, "source_records": len(seen),
         "eligible_entries": eligible_counts, "membership_source": "archived signals only; no archived outcome filtering",
         "reconciled": sum(source_counts.values()) == len(seen)})

    # File handles are opened only after the allowlist gate, and handed directly to
    # Arrow: no C-level filename discovery or directory/partition scanning.
    bars_by_day, fives_by_day = {}, {}
    all_raw, owners, coverage = [], [], []
    classifier = MarketSessionClassifier(calendar)
    for item in sorted(inputs, key=lambda x: x["session_date"]):
        path = (ROOT / item["path"]).resolve()
        day = date.fromisoformat(item["session_date"])
        assert path in allow and START <= day <= END
        assert digest(path) == item["sha256"], "Archived input changed"
        with path.open("rb") as handle:
            table = pq.read_table(handle)
        assert table.schema.equals(RAW_BAR_SCHEMA, check_metadata=False)
        raw = tuple(RawBarRecord.model_validate(x) for x in table.to_pylist())
        assert len({x.timestamp for x in raw}) == len(raw)
        assert tuple(x.timestamp for x in raw) == tuple(sorted(x.timestamp for x in raw))
        assert all(x.timestamp.astimezone(NY).date() == day for x in raw)
        session = calendar.session_for_date(day)
        rth = tuple(x for x in raw if session.market_open <= x.timestamp < session.market_close)
        minutes = int((session.market_close - session.market_open).total_seconds() // 60)
        assert tuple(x.timestamp for x in rth) == tuple(session.market_open + timedelta(minutes=i) for i in range(minutes))
        bars = tuple(MinuteBar(timestamp=x.timestamp, open=x.open, high=x.high,
                              low=x.low, close=x.close, session_date=day) for x in rth)
        five = aggregate_rth_1m_to_5m(classifier.classify_many(raw), session)
        assert len(five) * 5 == len(bars)
        assert five == aggregate_rth_1m_to_5m(classifier.classify_many(raw), session)
        for variant, signal, context in signals[day]:
            at, price, status = first_executable_minute(signal, bars, session_close=session.market_close)
            assert status == "AVAILABLE" and at == signal.executable_entry_timestamp == signal.signal_known_at
            assert price == signal.executable_entry_price
        coverage.append({"session_date": day, "expected_minutes": minutes, "rth_minutes": len(bars),
                         "five_minute_bars": len(five), "raw_rows": len(raw), "complete": True,
                         "market_open": session.market_open, "market_close": session.market_close,
                         "early_close": minutes < 390})
        bars_by_day[day], fives_by_day[day] = bars, five
        all_raw.extend(raw)
        owners.extend([day] * len(raw))
    validation = RawDataValidator(calendar).validate_raw_bars(all_raw, symbol="SPY", start_date=START, end_date=END, partition_dates=owners)
    assert validation.error_count == 0
    save("coverage_raw.json", validation.model_dump(mode="json"))
    save("coverage_sessions.json", coverage)
    save("coverage_summary.json", {"development_sessions": 170, "rth_minutes": sum(x["rth_minutes"] for x in coverage),
         "duplicate_minutes": 0, "missing_rth_minutes": 0, "source_entry_mismatches": 0,
         "early_closes": [x["session_date"] for x in coverage if x["early_close"]],
         "pmh_pml_certified_sessions": 4, "pmh_pml_uncertified_sessions": 166,
         "premarket_policy": "Inherited certified source level identities only; no coverage relaxation or reconstruction",
         "additional_context_partitions_opened": 0, "atr_warmup": "Same-session completed RTH 5m prefix only"})
    print("PRE-OUTCOME GATES PASS: 170 sessions; 66300 RTH minutes; 9335 exact executable references", flush=True)
    manifest = {"status": "OUTCOMES_RUNNING", "git_commit": head, "protocol": PROTOCOL,
                "protocol_sha256": before["protocol_sha256"], "started_at_utc": datetime.now(timezone.utc),
                "outcome_start": START, "outcome_end": END, "input_partitions": inputs,
                "source_archive": str(SOURCE.relative_to(ROOT)), "context_history": "Inherited immutable source level/interaction snapshots; no extra market files",
                "frozen_checks_before": before, "driver_sha256": digest(Path(__file__)),
                "network_policy": "Prohibited; Python socket/DNS/HTTP audit guard installed",
                "market_access_policy": "Exact 170-file allowlist checked before open; Arrow receives guarded file handles only"}
    save("run_manifest.json", manifest)
    rows = []
    status_counts = Counter()
    with (OUT / "outcomes.jsonl.gz").open("wb") as binary:
        with gzip.GzipFile(filename="", mode="wb", fileobj=binary, mtime=0) as archive:
            for i, day in enumerate(sorted(bars_by_day)):
                for variant, signal, context in sorted(signals[day], key=lambda x: (x[0], x[1].executable_entry_timestamp, x[1].interaction_id)):
                    for model in MODELS:
                        outcome = simulate(signal, variant, model, bars_by_day[day], fives_by_day[day])
                        row = json.loads(json.dumps(asdict(outcome), default=encode))
                        row.update(entry_timestamp=signal.executable_entry_timestamp.isoformat(),
                                   signal_known_at=signal.signal_known_at.isoformat(),
                                   entry_price=str(signal.executable_entry_price),
                                   direction="LONG" if signal.approach_side == "ABOVE" else "SHORT", context=context)
                        archive.write((json.dumps(row, sort_keys=True) + "\n").encode())
                        rows.append(row)
                        status_counts[row["status"]] += 1
                if (i + 1) % 10 == 0 or i == 169:
                    print(f"OUTCOMES: {i+1}/170 sessions; {len(rows)} rows", flush=True)
    assert len(rows) == 9335 * 16
    assert len({(r["entry_variant"], r["model"], r["session_date"], r["interaction_id"]) for r in rows}) == len(rows)
    save("outcome_reconciliation.json", {"rows": len(rows), "expected_rows": 9335 * 16,
          "status_counts": status_counts, "entry_counts": eligible_counts, "models_per_entry": 16, "combinations": 32})
    save("session_calendar.json", expected_days)
    manifest.update(status="OUTCOMES_COMPLETE_REPORTING_PENDING", outcome_rows=len(rows),
                    outcome_completed_at_utc=datetime.now(timezone.utc),
                    opened_partitions=sorted(opened), opened_partition_count=len(opened),
                    post_cutoff_partitions_opened=0, network_attempts=network_attempts,
                    frozen_checks_after_outcomes=frozen_checks())
    assert len(opened) == 170 and not network_attempts
    save("run_manifest.json", manifest)
    print("Frozen engine run complete. Reporting helper can consume archived rows without reopening market data.", flush=True)


if __name__ == "__main__":
    run()
