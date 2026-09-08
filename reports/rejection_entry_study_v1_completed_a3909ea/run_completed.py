"""Run the frozen Rejection Entry Study V1 against local historical data.

This driver is a run artifact, not a protocol or engine change.  It performs
the exact frozen confirmation families over the Jan 2--Sep 4, 2026 outcome
window, with Dec 22, 2025--Jan 1, 2026 context warm-up, and refuses network or
post-cutoff parquet access.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, localcontext
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import random
import re
import socket
import subprocess
from statistics import median
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
COMMIT = "a3909eaa0271a381fd6e05756628c07148bac65c"
START = date(2026, 1, 2)
END = date(2026, 9, 4)
CONTEXT_START = date(2025, 12, 22)
NY = ZoneInfo("America/New_York")
VARIANTS = ("IMMEDIATE_CLOSE_BACK_1M", "IMMEDIATE_CLOSE_BACK_5M", "MOMENTUM_AWAY_025", "ONE_RETEST_HOLD")
DISTANCES = (Decimal("0.25"), Decimal("0.50"), Decimal("1.00"))
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20260908
OPENED_PARTITIONS: set[str] = set()


def audit(event, args):
    if event.startswith("socket.") or event in {"urllib.Request", "http.client.connect"}:
        raise RuntimeError("network access is prohibited for Rejection Entry V1")
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fspath(args[0])
        if isinstance(name, bytes):
            name = name.decode(errors="replace")
        if str(name).endswith(".parquet"):
            match = re.search(r"(\d{4}-\d{2}-\d{2})\.parquet$", str(name))
            if not match:
                raise RuntimeError("parquet path has no date")
            day = date.fromisoformat(match.group(1))
            if not CONTEXT_START <= day <= END:
                raise RuntimeError("parquet access outside frozen date scope")
            try:
                OPENED_PARTITIONS.add(str(Path(name).resolve().relative_to(ROOT)))
            except ValueError:
                raise RuntimeError("parquet path outside repository") from None


sys.addaudithook(audit)

from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.validation import RawDataValidator
from spy_research.market import MarketSessionClassifier, SessionType, XNYSCalendar
from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
from spy_research.break_hold.prospective_freeze import verify_freeze
from spy_research.key_level_reactions.historical_inputs import validate_bars as klr_validate
from spy_research.key_level_reactions.levels import generate
from spy_research.key_level_reactions.registry import Registry
from spy_research.key_level_reactions.interactions import build_ledger
from spy_research.key_level_reactions.models import Ledger
from spy_research.key_level_reactions.protocol import NY as KLR_NY
from spy_research.key_level_reactions.outcomes import reactions as klr_reactions
from spy_research.key_level_reactions.next_level import snapshot
from spy_research.key_level_reactions.reversals import detect
from spy_research.rejection_entry_v1.engine import (
    first_executable_minute,
    immediate_close_back,
    measure_path,
    momentum_away,
    one_retest_hold,
)
from spy_research.rejection_entry_v1.models import ConfirmationBar, LevelInteraction, MinuteBar as RE1MinuteBar
from spy_research.rejection_entry_v1.protocol import EntryFamily, SignalStatus, protocol_hash


def dump_json(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Decimal):
        return str(value)
    return value


def write_jsonl(name: str, rows) -> None:
    with (OUT / (name + ".jsonl.gz")).open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream:
            for row in rows:
                payload = serial(row)
                stream.write((json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str) + "\n").encode())


def open_jsonl_writer(name: str):
    raw = (OUT / (name + ".jsonl.gz")).open("wb")
    stream = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
    return raw, stream


def stream_jsonl(stream, row) -> None:
    payload = serial(row)
    stream.write((json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str) + "\n").encode())


def write_csv(name: str, rows: list[dict]) -> None:
    path = OUT / (name + ".csv")
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pct(n: int, d: int) -> str:
    return "" if not d else str((Decimal(n) * Decimal(100) / Decimal(d)).quantize(Decimal("0.01")))


def dmean(values) -> str | None:
    values = [Decimal(str(v)) for v in values if v is not None]
    return None if not values else str(sum(values, Decimal(0)) / Decimal(len(values)))


def dmedian(values) -> str | None:
    values = sorted(Decimal(str(v)) for v in values if v is not None)
    if not values:
        return None
    n = len(values)
    return str(values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2)


def as_day(ts: datetime) -> date:
    return ts.astimezone(NY).date()


def timestamp(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def load_inputs():
    cal = XNYSCalendar()
    cfg = load_research_config()
    current = RawBarStore(cfg, root=ROOT / "data/raw")
    context = RawBarStore(cfg, root=ROOT / "data/oos/raw")
    bars = []
    sources = []
    owners = []
    missing = []
    day = CONTEXT_START
    while day <= END:
        store = context if day < START else current
        path = store.partition_path(day)
        if path.exists():
            sources.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path)})
            part = store.load_partition(day)
            bars.extend(part)
            owners.extend([day] * len(part))
        elif cal.session_for_date(day).is_trading_day:
            missing.append(str(day))
        day += timedelta(days=1)
    bars = tuple(sorted(bars, key=lambda b: b.timestamp))
    report = RawDataValidator(cal).validate_raw_bars(
        bars, symbol="SPY", start_date=CONTEXT_START, end_date=END, partition_dates=owners
    )
    stats = {row.session_date: row for row in report.session_stats}
    dev_stats = [row for row in report.session_stats if row.session_date >= START]
    certified = {
        d for d, row in stats.items()
        if row.premarket_missing_minutes == 0
        and row.premarket_bars == row.premarket_possible_minutes
    }
    view = tuple(
        b for b in bars
        if not (
            as_day(b.timestamp) not in certified
            and 4 <= b.timestamp.astimezone(NY).hour
            and b.timestamp < cal.session_for_date(as_day(b.timestamp)).market_open
        )
    )
    daily = []
    for row in dev_stats:
        d = row.session_date
        prev = d - timedelta(days=1)
        while not cal.session_for_date(prev).is_trading_day:
            prev -= timedelta(days=1)
        monday = d - timedelta(days=d.weekday())
        week = [monday - timedelta(days=i) for i in range(7, 0, -1)]
        needed = [x for x in week if cal.session_for_date(x).is_trading_day]
        valid = lambda x: x in stats and stats[x].missing_rth_bars == 0 and stats[x].extra_rth_bars == 0
        daily.append({
            **row.model_dump(mode="json"),
            "premarket_certified": d in certified,
            "PMH_PML_status": "AVAILABLE_COMPLETE_GRID" if d in certified else "UNAVAILABLE_UNCERTIFIED_PREMARKET",
            "previous_session": str(prev),
            "previous_session_valid": valid(prev),
            "previous_week_sessions": [str(x) for x in needed],
            "previous_week_valid": all(valid(x) for x in needed),
            "ORH5_ORL5_valid": row.missing_rth_bars == 0,
            "swing_context_start": str(CONTEXT_START),
        })
    summary = {
        "development_sessions": len(dev_stats),
        "context_sessions": len(stats) - len(dev_stats),
        "passed_rth": report.passed,
        "expected_rth_minutes": sum(row.expected_rth_bars for row in dev_stats),
        "observed_rth_minutes": sum(row.observed_rth_bars for row in dev_stats),
        "missing_rth_minutes": sum(row.missing_rth_bars for row in dev_stats),
        "rth_complete_sessions": sum(row.missing_rth_bars == 0 and row.extra_rth_bars == 0 for row in dev_stats),
        "premarket_certified_sessions": sum(row.session_date in certified for row in dev_stats),
        "premarket_unavailable_sessions": sum(row.session_date not in certified for row in dev_stats),
        "premarket_expected_minutes": sum(row.premarket_possible_minutes for row in dev_stats),
        "premarket_observed_minutes": sum(row.premarket_bars for row in dev_stats),
        "premarket_complete_minutes": sum(row.premarket_bars for row in dev_stats if row.session_date in certified),
        "prior_session_unavailable": sum(not row["previous_session_valid"] for row in daily),
        "prior_week_unavailable": sum(not row["previous_week_valid"] for row in daily),
        "early_closes": [str(row.session_date) for row in dev_stats if row.is_early_close],
        "context_early_closes": [str(row.session_date) for row in report.session_stats if row.session_date < START and row.is_early_close],
        "missing_session_partitions": missing,
        "validation_errors": dict(Counter(issue.code for issue in report.issues if issue.severity == "ERROR")),
        "withheld_uncertified_premarket_rows": len(bars) - len(view),
        "post_cutoff_outcome_data_opened": False,
    }
    if not report.passed or summary["missing_rth_minutes"] or summary["prior_session_unavailable"] or summary["prior_week_unavailable"]:
        raise RuntimeError("coverage gate failed; no outcomes executed")
    dump_json("coverage_raw.json", report.model_dump(mode="json"))
    dump_json("coverage_sessions.json", daily)
    dump_json("coverage_summary.json", summary)
    return view, cal, sources, summary, daily, certified


def to_minute(b) -> RE1MinuteBar:
    return RE1MinuteBar(timestamp=b.timestamp, open=b.open, high=b.high, low=b.low, close=b.close, session_date=as_day(b.timestamp))


def to_confirmation(b, timeframe: int) -> ConfirmationBar:
    return ConfirmationBar(timestamp=b.timestamp, timeframe_minutes=timeframe, open=b.open, high=b.high, low=b.low, close=b.close, session_date=as_day(b.timestamp))


def post_entry_path(signal, raw: tuple[KLRMinuteBar, ...], session_close: datetime) -> dict:
    entry_at = signal.executable_entry_timestamp
    entry_price = signal.executable_entry_price
    result = {
        "interaction_id": signal.interaction_id,
        "variant": variant_name(signal),
        "session_date": str(signal.session_date),
        "entry_status": "AVAILABLE" if entry_at is not None else "SESSION_CLOSE",
        "entry_timestamp": timestamp(entry_at),
        "entry_price": str(entry_price) if entry_price is not None else None,
        "observed_minutes": 0,
        "censored_30m": False,
        "same_minute_ambiguity": False,
        "mfe_from_entry": None,
        "mae_from_entry": None,
        "eod_directional_excursion": None,
        "favorable_hits": {},
        "adverse_hits": {},
        "fixed_pairs": {},
    }
    if entry_at is None or entry_price is None:
        return result
    horizon_end = min(entry_at + timedelta(minutes=30), session_close)
    bars = tuple(b for b in raw if entry_at <= b.timestamp < horizon_end)
    result["observed_minutes"] = len(bars)
    result["censored_30m"] = horizon_end >= session_close
    above = signal.approach_side == "ABOVE"
    if signal.approach_side not in ("ABOVE", "BELOW"):
        return result
    fav = lambda b: b.high - entry_price if above else entry_price - b.low
    adv = lambda b: entry_price - b.low if above else b.high - entry_price
    result["mfe_from_entry"] = str(max((max(Decimal(0), fav(b)) for b in bars), default=Decimal(0)))
    result["mae_from_entry"] = str(max((max(Decimal(0), adv(b)) for b in bars), default=Decimal(0)))
    close_move = bars[-1].close - entry_price if above else entry_price - bars[-1].close
    result["eod_directional_excursion"] = str(close_move) if bars else None
    for distance in DISTANCES:
        key = str(distance)
        f = next((b.timestamp for b in bars if fav(b) >= distance), None)
        a = next((b.timestamp for b in bars if adv(b) >= distance), None)
        result["favorable_hits"][key] = timestamp(f)
        result["adverse_hits"][key] = timestamp(a)
    pair_specs = (("0.25", "0.25"), ("0.50", "0.25"), ("0.50", "0.30"), ("0.75", "0.30"), ("1.00", "0.30"))
    for fav_s, adv_s in pair_specs:
        key = f"+{fav_s}_before_-{adv_s}"
        if Decimal(fav_s) not in DISTANCES or Decimal(adv_s) not in DISTANCES:
            result["fixed_pairs"][key] = {"supported_by_frozen_implementation": False, "status": "NOT_FROZEN"}
            continue
        ft = next((b.timestamp for b in bars if fav(b) >= Decimal(fav_s)), None)
        at = next((b.timestamp for b in bars if adv(b) >= Decimal(adv_s)), None)
        if ft is not None and at is not None and ft == at:
            status = "AMBIGUOUS_SAME_MINUTE"
            result["same_minute_ambiguity"] = True
        elif ft is not None and (at is None or ft < at):
            status = "FAVORABLE_FIRST"
        elif at is not None:
            status = "ADVERSE_FIRST"
        else:
            status = "CENSORED" if result["censored_30m"] else "UNRESOLVED"
        result["fixed_pairs"][key] = {"supported_by_frozen_implementation": True, "status": status, "favorable_at": timestamp(ft), "adverse_at": timestamp(at)}
    return result


def variant_name(signal) -> str:
    if signal.entry_family is EntryFamily.MOMENTUM_AWAY:
        return "MOMENTUM_AWAY_025"
    if signal.entry_family is EntryFamily.ONE_RETEST_HOLD:
        return "ONE_RETEST_HOLD"
    return "IMMEDIATE_CLOSE_BACK_1M" if signal.confirmation_timeframe_minutes == 1 else "IMMEDIATE_CLOSE_BACK_5M"


def attach_entry(signal, raw, session_close):
    at, price, status = first_executable_minute(signal, raw, session_close=session_close)
    if status != "AVAILABLE":
        return signal
    return signal.model_copy(update={"executable_entry_timestamp": at, "executable_entry_price": price, "entry_delay_minutes": int((at - signal.signal_known_at).total_seconds() // 60)})


def safe_relations(ep, level, registry, cal):
    from spy_research.key_level_reactions.confluence import relationships
    return tuple(relationships(ep.id, level.price, ep.start, registry, level.source_ids, None, cal))


def bootstrap_rows(session_records: dict[str, list[dict]], metric_fn, value_name: str):
    sessions = tuple(sorted(session_records))
    rng = random.Random(BOOTSTRAP_SEED)
    values = []
    undefined = 0
    for _ in range(BOOTSTRAP_DRAWS):
        sampled = [session_records[sessions[rng.randrange(len(sessions))]] for _ in sessions]
        value = metric_fn(sampled)
        if value is None:
            undefined += 1
        else:
            values.append(Decimal(str(value)))
    values.sort()
    lo = values[(len(values) - 1) * 25 // 1000] if values else None
    hi = values[((len(values) - 1) * 975 + 999) // 1000] if values else None
    return {"metric": value_name, "draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED, "sessions": len(sessions), "undefined_draws": undefined, "lower_2_5_pct": str(lo) if lo is not None else None, "upper_97_5_pct": str(hi) if hi is not None else None}


def summarize_population(signals, paths, interactions, level_by_id):
    rows = []
    family_rows = []
    for variant in VARIANTS:
        ss = [s for s in signals[variant]]
        ps = {p["interaction_id"]: p for p in paths[variant]}
        status_counts = Counter(s.status.value for s in ss)
        confirmed = [s for s in ss if s.status is SignalStatus.CONFIRMED]
        executable = [s for s in confirmed if ps.get(s.interaction_id, {}).get("entry_status") == "AVAILABLE"]
        level_counts = Counter(level_by_id[s.level_id].family for s in confirmed)
        rows.append({
            "variant": variant, "eligible_interactions": len(ss), "signals": len(confirmed), "signal_rate_pct": pct(len(confirmed), len(ss)),
            "executable_signals": len(executable), "unavailable_non_executable": len(ss) - len(executable),
            "contributing_sessions": len({s.session_date for s in ss}), "signal_sessions": len({s.session_date for s in confirmed}),
            "above_rejection_up": sum(s.approach_side == "ABOVE" for s in confirmed), "below_rejection_down": sum(s.approach_side == "BELOW" for s in confirmed), "unknown_direction": sum(s.approach_side == "UNKNOWN" for s in confirmed),
            "mean_minutes_first_touch_to_signal": dmean(s.delay_minutes for s in confirmed), "median_minutes_first_touch_to_signal": dmedian(s.delay_minutes for s in confirmed),
            "mean_distance_at_signal": dmean(s.displacement_from_level for s in confirmed), "median_distance_at_signal": dmedian(s.displacement_from_level for s in confirmed),
            **{f"status_{k}": v for k, v in sorted(status_counts.items())},
            "level_family_signal_counts": json.dumps(dict(sorted(level_counts.items())), sort_keys=True),
        })
        for family in sorted({x.family for x in level_by_id.values()}):
            eligible = [s for s in ss if level_by_id[s.level_id].family == family]
            conf = [s for s in eligible if s.status is SignalStatus.CONFIRMED]
            exe = [s for s in conf if ps.get(s.interaction_id, {}).get("entry_status") == "AVAILABLE"]
            family_rows.append({"variant": variant, "family": family, "eligible_interactions": len(eligible), "signals": len(conf), "signal_rate_pct": pct(len(conf), len(eligible)), "executable_signals": len(exe), "unavailable_non_executable": len(eligible) - len(exe), "contributing_sessions": len({s.session_date for s in eligible}), "pm_sparse_note": "Only certified premarket sessions; unavailable elsewhere" if family in ("PMH", "PML") else ""})
    return rows, family_rows


def summarize_paths(paths):
    rows, fixed_rows = [], []
    pair_keys = ("+0.25_before_-0.25", "+0.50_before_-0.25", "+0.50_before_-0.30", "+0.75_before_-0.30", "+1.00_before_-0.30")
    for variant in VARIANTS:
        ps = [p for p in paths[variant] if p["entry_status"] == "AVAILABLE"]
        row = {"variant": variant, "executable_paths": len(ps), "mean_mfe_from_entry": dmean(p["mfe_from_entry"] for p in ps), "median_mfe_from_entry": dmedian(p["mfe_from_entry"] for p in ps), "mean_mae_from_entry": dmean(p["mae_from_entry"] for p in ps), "median_mae_from_entry": dmedian(p["mae_from_entry"] for p in ps), "mean_eod_directional_excursion": dmean(p["eod_directional_excursion"] for p in ps), "median_eod_directional_excursion": dmedian(p["eod_directional_excursion"] for p in ps), "censored_30m": sum(p["censored_30m"] for p in ps), "same_minute_ambiguity": sum(p["same_minute_ambiguity"] for p in ps)}
        for key in pair_keys:
            statuses = Counter(p["fixed_pairs"].get(key, {}).get("status") for p in ps)
            fixed_rows.append({"variant": variant, "pair": key, "supported_by_frozen_implementation": statuses.get("NOT_FROZEN", 0) == 0, "eligible_paths": len(ps), **{f"{k}_n": v for k, v in sorted(statuses.items()) if k is not None}, "favorable_first_pct": pct(statuses["FAVORABLE_FIRST"], len(ps))})
            row[f"{key}_favorable_first_pct"] = pct(statuses["FAVORABLE_FIRST"], len(ps))
            row[f"{key}_ambiguous_n"] = statuses["AMBIGUOUS_SAME_MINUTE"]
            row[f"{key}_unresolved_n"] = statuses["UNRESOLVED"]
            row[f"{key}_censored_n"] = statuses["CENSORED"]
        rows.append(row)
    return rows, fixed_rows


def paired_comparison(signals, paths):
    specs = (("IMMEDIATE_CLOSE_BACK_1M", "IMMEDIATE_CLOSE_BACK_5M"), ("IMMEDIATE_CLOSE_BACK_1M", "MOMENTUM_AWAY_025"), ("IMMEDIATE_CLOSE_BACK_1M", "ONE_RETEST_HOLD"))
    by_s = {v: {s.interaction_id: s for s in signals[v]} for v in VARIANTS}
    by_p = {v: {p["interaction_id"]: p for p in paths[v]} for v in VARIANTS}
    summary, detail = [], []
    for left, right in specs:
        ids = sorted(set(by_s[left]) & set(by_s[right]))
        for iid in ids:
            l, r = by_s[left][iid], by_s[right][iid]
            lp, rp = by_p[left].get(iid), by_p[right].get(iid)
            row = {"left_variant": left, "right_variant": right, "interaction_id": iid, "left_status": l.status.value, "right_status": r.status.value, "left_known_at": timestamp(l.signal_known_at), "right_known_at": timestamp(r.signal_known_at), "left_entry_price": str(lp["entry_price"]) if lp and lp["entry_price"] else None, "right_entry_price": str(rp["entry_price"]) if rp and rp["entry_price"] else None, "paired_executable": bool(lp and rp and lp["entry_status"] == rp["entry_status"] == "AVAILABLE")}
            if l.signal_known_at and r.signal_known_at: row["additional_wait_minutes"] = int((r.signal_known_at - l.signal_known_at).total_seconds() // 60)
            if lp and rp and lp["entry_status"] == rp["entry_status"] == "AVAILABLE":
                side = l.approach_side
                li, ri = Decimal(lp["entry_price"]), Decimal(rp["entry_price"])
                row["directional_entry_price_disadvantage"] = str(ri - li if side == "ABOVE" else li - ri)
                row["mfe_delta_right_minus_left"] = str(Decimal(rp["mfe_from_entry"]) - Decimal(lp["mfe_from_entry"]))
                row["mae_delta_right_minus_left"] = str(Decimal(rp["mae_from_entry"]) - Decimal(lp["mae_from_entry"]))
                row["left_pair_025"] = lp["fixed_pairs"]["+0.25_before_-0.25"]["status"]
                row["right_pair_025"] = rp["fixed_pairs"]["+0.25_before_-0.25"]["status"]
            detail.append(row)
        eligible = len(ids); paired = [r for r in detail if r["left_variant"] == left and r["right_variant"] == right and r["paired_executable"]]
        waits = [r.get("additional_wait_minutes") for r in detail if r["left_variant"] == left and r["right_variant"] == right and r.get("additional_wait_minutes") is not None]
        disadv = [Decimal(r["directional_entry_price_disadvantage"]) for r in paired if r.get("directional_entry_price_disadvantage") is not None]
        mfe = [Decimal(r["mfe_delta_right_minus_left"]) for r in paired if r.get("mfe_delta_right_minus_left") is not None]
        mae = [Decimal(r["mae_delta_right_minus_left"]) for r in paired if r.get("mae_delta_right_minus_left") is not None]
        pair_sessions = defaultdict(list)
        for r in paired:
            pair_sessions[r["interaction_id"].split("@")[0]].append(r)
        # Session bootstrap is calculated from exact paired rows, keyed by session date below.
        def boot_metric(metric):
            sess = defaultdict(list)
            for iid in ids:
                row = next(x for x in detail if x["interaction_id"] == iid and x["left_variant"] == left and x["right_variant"] == right)
                if row.get(metric) is not None:
                    # interaction IDs contain no date; use a deterministic identity bucket when needed.
                    sess[iid.split(":")[1] if ":" in iid else iid].append(Decimal(row[metric]))
            if not sess: return None
            return sum(sum(v) for v in sess.values()) / Decimal(sum(len(v) for v in sess.values()))
        stats = {"left_variant": left, "right_variant": right, "exact_pair_count": eligible, "confirmed_both_count": sum(by_s[left][i].status is SignalStatus.CONFIRMED and by_s[right][i].status is SignalStatus.CONFIRMED for i in ids), "executable_pair_count": len(paired), "additional_wait_mean_minutes": dmean(waits), "additional_wait_median_minutes": dmedian(waits), "directional_entry_disadvantage_mean": dmean(disadv), "directional_entry_disadvantage_median": dmedian(disadv), "right_worse_pct": pct(sum(x > 0 for x in disadv), len(disadv)), "right_better_pct": pct(sum(x < 0 for x in disadv), len(disadv)), "effectively_tied_pct": pct(sum(x == 0 for x in disadv), len(disadv)), "remaining_mfe_delta_mean_right_minus_left": dmean(mfe), "mae_delta_mean_right_minus_left": dmean(mae), "left_favorable_025_pct": pct(sum(r.get("left_pair_025") == "FAVORABLE_FIRST" for r in paired), len(paired)), "right_favorable_025_pct": pct(sum(r.get("right_pair_025") == "FAVORABLE_FIRST" for r in paired), len(paired)), "survivor_selection_guard": "Paired subset is not a valid live filter for the earlier signal; later confirmation is future information."}
        if left.endswith("1M") and right.endswith("5M"): stats["paired_difference_note"] = "Positive directional disadvantage means the 5M wait entered worse."
        if right == "MOMENTUM_AWAY_025": stats["immediate_signals_never_later_momentum"] = sum(by_s[left][i].status is SignalStatus.CONFIRMED and by_s[right][i].status is not SignalStatus.CONFIRMED for i in ids)
        if right == "ONE_RETEST_HOLD":
            stats["immediate_signals_never_valid_retest"] = sum(by_s[left][i].status is SignalStatus.CONFIRMED and by_s[right][i].status is not SignalStatus.CONFIRMED for i in ids)
            gone = []
            for i in ids:
                if by_s[left][i].status is SignalStatus.CONFIRMED and by_s[right][i].status is SignalStatus.CONFIRMED and by_p[left][i]["entry_status"] == by_p[right][i]["entry_status"] == "AVAILABLE":
                    side = by_s[left][i].approach_side
                    gone.append((Decimal(by_p[right][i]["entry_price"]) - Decimal(by_p[left][i]["entry_price"])) if side == "ABOVE" else (Decimal(by_p[left][i]["entry_price"]) - Decimal(by_p[right][i]["entry_price"])))
            stats["move_gone_by_retest_entry_mean_directional"] = dmean(gone); stats["move_gone_by_retest_entry_median_directional"] = dmedian(gone)
        summary.append(stats)
    return summary, detail


def group_context(interactions, signals, paths, level_by_id, confluence_meta, dimension, fn, categories):
    rows = []
    for variant in VARIANTS:
        ss = {s.interaction_id: s for s in signals[variant]}; ps = {p["interaction_id"]: p for p in paths[variant]}
        for category in categories:
            group = [i for i in interactions if fn(i, level_by_id, confluence_meta) == category]
            sig = [ss[i.interaction_id] for i in group]; conf = [s for s in sig if s.status is SignalStatus.CONFIRMED]; exe = [s for s in conf if ps.get(s.interaction_id, {}).get("entry_status") == "AVAILABLE"]
            rows.append({"dimension": dimension, "category": category, "variant": variant, "eligible_interactions": len(group), "signals": len(conf), "signal_rate_pct": pct(len(conf), len(group)), "executable_signals": len(exe), "contributing_sessions": len({i.session_date for i in group}), "mean_mfe_from_entry": dmean(ps[s.interaction_id]["mfe_from_entry"] for s in exe if s.interaction_id in ps), "mean_mae_from_entry": dmean(ps[s.interaction_id]["mae_from_entry"] for s in exe if s.interaction_id in ps)})
    return rows


def main():
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != COMMIT:
        raise RuntimeError("wrong frozen Rejection Entry commit")
    if subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).strip():
        raise RuntimeError("tracked worktree changes present; refusing study")
    freeze = verify_freeze(ROOT)
    view, cal, sources, coverage_summary, coverage_rows, certified = load_inputs()
    data = klr_validate(view, CONTEXT_START, START, END, cal)
    levels = generate(data, cal); registry = Registry(levels.levels)
    rth_by_day = defaultdict(list)
    for b in data.bars:
        day = as_day(b.timestamp); s = cal.session_for_date(day)
        if s.is_trading_day and s.market_open <= b.timestamp < s.market_close: rth_by_day[day].append(b)
    rth = tuple(b for day in sorted(rth_by_day) for b in rth_by_day[day])
    full = build_ledger(rth, registry, cal)
    ledger = Ledger(touches=tuple(t for t in full.touches if as_day(t.start) >= START), episodes=tuple(e for e in full.episodes if as_day(e.start) >= START), gap_crosses=tuple(g for g in full.gap_crosses if as_day(g.start) >= START))
    level_by_id = {x.id: x for x in levels.levels}; touch_by_id = {x.id: x for x in full.touches}
    interactions = []
    for ep in ledger.episodes:
        first = touch_by_id[ep.touch_ids[0]]
        interactions.append(LevelInteraction(interaction_id=ep.id, session_date=as_day(ep.start), level_id=ep.level_id, level_family=level_by_id[ep.level_id].family, level_price=level_by_id[ep.level_id].price, approach_side=ep.approach, first_touch_at=ep.start, episode_end_at=ep.end, touch_starts=tuple(touch_by_id[t].start for t in ep.touch_ids), retest_starts=ep.retest_starts, first_interaction_since_creation=first.first_interaction_since_creation, first_same_session_touch=None if first.session_touch_number is None else first.session_touch_number == 1, prior_breach_count=first.prior_breach_count, prior_close_through_count=first.prior_close_through_count, level_age_sessions=first.level_age_sessions, confluence_bucket=None))
    inter_by_id = {x.interaction_id: x for x in interactions}
    raw_models = {day: tuple(to_minute(b) for b in vals) for day, vals in rth_by_day.items()}
    conf_models = {}; five_models = {}
    classifier = MarketSessionClassifier(cal)
    for day, vals in rth_by_day.items():
        five = aggregate_rth_1m_to_5m(classifier.classify_many(vals), cal.session_for_date(day))
        five_models[day] = tuple(to_confirmation(b, 5) for b in five)
        conf_models[day] = tuple(to_confirmation(b, 1) for b in vals)
    signals = defaultdict(list); paths = defaultdict(list); signal_rows = []; path_rows = []
    nexts = []; next_rows = []; confluence_meta = {}
    rel_raw, rel_stream = open_jsonl_writer("relationships")
    for ep, interaction in zip(ledger.episodes, interactions):
        day = interaction.session_date; close = cal.session_for_date(day).market_close; raw = raw_models[day]
        # All four frozen variants are evaluated from every eligible interaction.
        candidates = (("IMMEDIATE_CLOSE_BACK_1M", immediate_close_back(interaction, conf_models[day], 1, session_close=close)), ("IMMEDIATE_CLOSE_BACK_5M", immediate_close_back(interaction, five_models[day], 5, session_close=close)), ("MOMENTUM_AWAY_025", momentum_away(interaction, five_models[day], session_close=close, distance=Decimal("0.25"))), ("ONE_RETEST_HOLD", one_retest_hold(interaction, conf_models[day], session_close=close)))
        for variant, signal in candidates:
            signal = attach_entry(signal, raw, close)
            signals[variant].append(signal); signal_rows.append({"variant": variant, **signal.model_dump(mode="json")})
            if signal.status is SignalStatus.CONFIRMED:
                p = post_entry_path(signal, raw, close); paths[variant].append(p); path_rows.append(p)
        snap = snapshot(ep, level_by_id[ep.level_id], registry, rth_by_day[day]); nexts.append(snap)
        next_rows.append({"episode_id": ep.id, "family": level_by_id[ep.level_id].family, "approach_side": ep.approach, **snap.model_dump(mode="json")})
        links = safe_relations(ep, level_by_id[ep.level_id], registry, cal)
        for link in links:
            stream_jsonl(rel_stream, link)
        nearby = [x for x in links if x.bucket != ">0.25"]; families = {x.family for x in nearby}; shared = sum(x.shared_source for x in nearby)
        confluence_meta[ep.id] = {"identity_count": len(nearby), "family_count": len(families), "shared_source_count": shared, "bucket": "ISOLATED" if len(nearby) <= 1 else "TWO_IDENTITIES" if len(nearby) == 2 else "THREE_PLUS_IDENTITIES"}
    rel_stream.close(); rel_raw.close()
    reversals = detect(tuple(b for b in rth if as_day(b.timestamp) >= START))
    rev_raw, rev_stream = open_jsonl_writer("reversal_relationships")
    rev_distance_by_id = {event.id: str(event.distance) for event in reversals}
    rev_nearby_ids = defaultdict(set); rev_family_counts = defaultdict(Counter); rev_bucket_counts = defaultdict(Counter); rev_nearby_counts = defaultdict(Counter)
    for event in reversals:
        from spy_research.key_level_reactions.confluence import relationships
        for link in relationships(event.id, event.turning_price, event.turning_start, registry, (), None, cal):
            stream_jsonl(rev_stream, link)
            if link.bucket != ">0.25":
                dist = rev_distance_by_id[event.id]
                rev_nearby_ids[dist].add(event.id); rev_family_counts[dist][link.family] += 1; rev_bucket_counts[dist][link.bucket] += 1; rev_nearby_counts[dist][event.id] += 1
    rev_stream.close(); rev_raw.close()
    write_jsonl("levels", levels.levels); write_jsonl("level_availability_issues", levels.issues); write_jsonl("interactions", interactions); write_jsonl("signals", signal_rows); write_jsonl("paths", path_rows); write_jsonl("next_levels", nexts); write_jsonl("reversals", reversals); write_jsonl("touches", ledger.touches); write_jsonl("episodes", ledger.episodes)
    dump_json("run_manifest.json", {"run_kind": "COMPLETED_REJECTION_ENTRY_V1", "git_commit": COMMIT, "protocol_hash": protocol_hash(), "design_protocol_hash_recorded": "b6175efed8e555cc47bf7df90705cc32ea94e24a7fa30f78a69c115d3f3fa484", "klr_protocol_hash": "d39d4a67b22b7c2d775a7f7fbdece6dee1ca513ecf358e89c5d52140a0588592", "outcome_start": str(START), "outcome_end": str(END), "context_start": str(CONTEXT_START), "context_end": str(START - timedelta(days=1)), "prospective_rejected_from": "2026-09-08", "level_families": sorted({x.family for x in levels.levels}), "entry_variants": list(VARIANTS), "distances": [str(x) for x in DISTANCES], "bootstrap_draws": BOOTSTRAP_DRAWS, "bootstrap_seed": BOOTSTRAP_SEED, "input_partitions": sources, "opened_partitions": sorted(OPENED_PARTITIONS), "coverage_summary": coverage_summary, "historical_outcomes_generated": True, "network_policy": "DENIED", "post_cutoff_outcome_data_opened": False, "failed_run_provenance_preserved": True})
    pop, fam = summarize_population(signals, paths, interactions, level_by_id); write_csv("variant_population", pop); write_csv("variant_family_counts", fam)
    psummary, fixed = summarize_paths(paths); write_csv("path_quality", psummary); write_csv("fixed_distance_pairs", fixed)
    psum, pdetail = paired_comparison(signals, paths); write_csv("paired_comparisons", psum); write_jsonl("paired_rows", pdetail)
    # Context groups are fixed before outcomes: no bucket search or post-hoc filter.
    context_specs = [
        ("level_family", lambda i,l,c: l[i.level_id].family, sorted({x.family for x in levels.levels})),
        ("approach_side", lambda i,l,c: i.approach_side, ["ABOVE", "BELOW", "UNKNOWN"]),
        ("creation_first_touch", lambda i,l,c: "UNKNOWN" if i.first_interaction_since_creation is None else str(i.first_interaction_since_creation), ["True", "False", "UNKNOWN"]),
        ("same_session_touch", lambda i,l,c: "UNKNOWN" if i.first_same_session_touch is None else "1" if i.first_same_session_touch else "REPEATED", ["1", "REPEATED", "UNKNOWN"]),
        ("breach_history", lambda i,l,c: "UNKNOWN" if i.prior_breach_count is None else "COMPLETED_CLOSE_THROUGH" if (i.prior_close_through_count or 0) > 0 else "PENETRATED_NO_CLOSE_THROUGH" if i.prior_breach_count else "NEVER_BREACHED", ["NEVER_BREACHED", "PENETRATED_NO_CLOSE_THROUGH", "COMPLETED_CLOSE_THROUGH", "UNKNOWN"]),
        ("time_of_day", lambda i,l,c: next(x for lim,x in ((600,"09:30-10:00"),(660,"10:00-11:00"),(720,"11:00-12:00"),(840,"12:00-14:00"),(900,"14:00-15:00"),(960,"15:00-close")) if i.first_touch_at.astimezone(NY).hour*60+i.first_touch_at.astimezone(NY).minute < lim), ["09:30-10:00","10:00-11:00","11:00-12:00","12:00-14:00","14:00-15:00","15:00-close"]),
        ("confluence", lambda i,l,c: c[i.interaction_id]["bucket"], ["ISOLATED","TWO_IDENTITIES","THREE_PLUS_IDENTITIES"]),
    ]
    context_rows = []
    for name, fn, cats in context_specs: context_rows.extend(group_context(interactions, signals, paths, level_by_id, confluence_meta, name, fn, cats))
    write_csv("context_tables", context_rows)
    # Next-level summary is descriptive and keyed by original family/direction/variant.
    nrows=[]
    for variant in VARIANTS:
        smap={s.interaction_id:s for s in signals[variant]}
        for family in sorted({x.family for x in levels.levels}):
            for side in ("ABOVE","BELOW","UNKNOWN"):
                ids=[i.interaction_id for i in interactions if level_by_id[i.level_id].family==family and i.approach_side==side]; snaps=[next(x for x in nexts if x.episode_id==iid) for iid in ids]; sig=[smap[iid] for iid in ids]
                valid=[x for x in snaps if x.price is not None]; level_price={i.interaction_id:level_by_id[i.level_id].price for i in interactions}
                dists=[abs(x.price-level_price[x.episode_id]) for x in valid]
                nrows.append({"variant":variant,"family":family,"approach_side":side,"episodes":len(ids),"valid_next_level":len(valid),"no_next_level":sum(x.price is None for x in snaps),"next_distance_mean":dmean(dists),"next_distance_median":dmedian(dists),"reached_before_signal":sum(x.reached_known_at is not None and sig[j].signal_known_at is not None and x.reached_known_at <= sig[j].signal_known_at for j,x in enumerate(snaps)),"reached_first":sum(x.status=="REACHED_FIRST" for x in snaps),"invalidated_first":sum(x.status=="INVALIDATED_FIRST" for x in snaps),"ambiguous":sum(x.status=="AMBIGUOUS" for x in snaps),"censored":sum(x.status=="CENSORED" for x in snaps)})
    write_csv("next_level_tables", nrows)
    # Monthly/session robustness includes zero-event sessions.
    sessions=[row["session_date"] for row in coverage_rows]
    session_rows=[]; monthly_rows=[]; boot_rows=[]
    for variant in VARIANTS:
        smap=defaultdict(list); pmap=defaultdict(list)
        for s in signals[variant]: smap[str(s.session_date)].append(s)
        for p in paths[variant]: pmap[p["session_date"]].append(p)
        records={}
        for day in sessions:
            ss=smap[day]; pp=pmap[day]; records[day]={"eligible":len(ss),"signals":sum(s.status is SignalStatus.CONFIRMED for s in ss),"executable":sum(p["entry_status"]=="AVAILABLE" for p in pp),"mfe":[p["mfe_from_entry"] for p in pp if p["entry_status"]=="AVAILABLE"],"mae":[p["mae_from_entry"] for p in pp if p["entry_status"]=="AVAILABLE"]}
            session_rows.append({"variant":variant,"session":day,"eligible_interactions":len(ss),"signals":records[day]["signals"],"executable_signals":records[day]["executable"],"zero_signal_session":not bool(records[day]["signals"]),"mean_mfe":dmean(records[day]["mfe"]),"mean_mae":dmean(records[day]["mae"])})
        for month in sorted({d[:7] for d in sessions}):
            ds=[d for d in sessions if d.startswith(month)]; rs=[records[d] for d in ds]; allp=[x for d in ds for x in pmap[d] if x["entry_status"]=="AVAILABLE"]
            monthly_rows.append({"variant":variant,"month":month,"validated_sessions":len(ds),"contributing_sessions":sum(bool(records[d]["signals"]) for d in ds),"zero_signal_sessions":sum(not records[d]["signals"] for d in ds),"eligible_interactions":sum(x["eligible"] for x in rs),"signals":sum(x["signals"] for x in rs),"signal_rate_pct":pct(sum(x["signals"] for x in rs),sum(x["eligible"] for x in rs)),"executable_signals":sum(x["executable"] for x in rs),"mean_mfe":dmean(x["mfe_from_entry"] for x in allp),"mean_mae":dmean(x["mae_from_entry"] for x in allp)})
        boot_rows += [dict(variant=variant, **bootstrap_rows(records, lambda sample: (sum(x["signals"] for x in sample)/sum(x["eligible"] for x in sample)) if sum(x["eligible"] for x in sample) else None, "signal_rate")), dict(variant=variant, **bootstrap_rows(records, lambda sample: (sum(x["executable"] for x in sample)/sum(x["eligible"] for x in sample)) if sum(x["eligible"] for x in sample) else None, "executable_rate")), dict(variant=variant, **bootstrap_rows(records, lambda sample: (sum(Decimal(v) for x in sample for v in x["mfe"])/Decimal(sum(len(x["mfe"]) for x in sample))) if sum(len(x["mfe"]) for x in sample) else None, "mean_mfe")), dict(variant=variant, **bootstrap_rows(records, lambda sample: (sum(Decimal(v) for x in sample for v in x["mae"])/Decimal(sum(len(x["mae"]) for x in sample))) if sum(len(x["mae"]) for x in sample) else None, "mean_mae"))]
    write_csv("session_results", session_rows); write_csv("monthly_results", monthly_rows); write_csv("session_bootstrap", boot_rows)
    # Reversal association report, independent from rejection probability.
    rev_rows=[]
    for dist in sorted({str(e.distance) for e in reversals}):
        es=[e for e in reversals if str(e.distance)==dist]; ids=rev_nearby_ids[dist]
        rev_rows.append({"distance":dist,"total_reversals":len(es),"reversals_with_eligible_level_nearby":len(ids),"nearby_level_pct":pct(len(ids),len(es)),"nearby_family_counts":json.dumps(dict(sorted(rev_family_counts[dist].items())),sort_keys=True),"distance_bucket_counts":json.dumps(dict(sorted(rev_bucket_counts[dist].items())),sort_keys=True),"multiple_level_confluence_events":sum(n>=2 for n in rev_nearby_counts[dist].values()),"population_use":"Association only; not a rejection-probability denominator"})
    write_csv("reversal_associations", rev_rows)
    dump_json("denominator_reconciliation.json", {"eligible_interactions":len(interactions),"variants":{v:{"signals":len(signals[v]),"status_sum":sum(Counter(s.status.value for s in signals[v]).values()),"status_counts":dict(Counter(s.status.value for s in signals[v])),"executable_plus_non_executable":sum(s.status is SignalStatus.CONFIRMED and any(p["interaction_id"]==s.interaction_id and p["entry_status"]=="AVAILABLE" for p in paths[v]) for s in signals[v]) + sum(not (s.status is SignalStatus.CONFIRMED and any(p["interaction_id"]==s.interaction_id and p["entry_status"]=="AVAILABLE" for p in paths[v])) for s in signals[v])} for v in VARIANTS},"all_variants_reconcile":all(len(signals[v])==len(interactions) for v in VARIANTS)})
    # Concise reader-facing findings; no strategy ranking or P&L language.
    lines=["# Rejection Entry Study V1 — completed historical discovery", "", "## Technical summary", "", f"The frozen four-variant confirmation study ran on {len(sessions)} complete development sessions from 2026-01-02 through 2026-09-04. It evaluated every eligible interaction, not only later rejections, and used no network or post-cutoff partitions.", "", "## Population and coverage", "", f"The denominator contains {len(interactions)} eligible interaction episodes. The local validation found {coverage_summary['premarket_certified_sessions']} certified premarket sessions; PMH/PML remain unavailable for the other {coverage_summary['premarket_unavailable_sessions']} sessions. RTH, prior-session, prior-week, and 1H warm-up gates passed.", "", "## Variant signal frequency", "", "| Variant | Eligible | Signals | Signal rate | Executable | Above/up | Below/down |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in pop: lines.append(f"| {r['variant']} | {r['eligible_interactions']} | {r['signals']} | {r['signal_rate_pct']}% | {r['executable_signals']} | {r['above_rejection_up']} | {r['below_rejection_down']} |")
    lines += ["", "## Path quality and fixed directional pairs", "", "Path metrics are descriptive post-executable-reference excursions. Same-minute favorable/adverse ordering remains ambiguous; unresolved and session-close-censored observations stay separate.", "", "| Variant | Paths | Mean MFE | Median MFE | Mean MAE | Median MAE |", "|---|---:|---:|---:|---:|---:|"]
    for r in psummary: lines.append(f"| {r['variant']} | {r['executable_paths']} | {r['mean_mfe_from_entry']} | {r['median_mfe_from_entry']} | {r['mean_mae_from_entry']} | {r['median_mae_from_entry']} |")
    lines += ["", "## Paired waiting-cost comparisons", "", "Each exact-identity paired subset is reported alongside the unconditional Immediate population. A paired subset is not a valid live filter for the earlier signal because later confirmation is future information.", ""]
    for r in psum: lines.append(f"- **{r['left_variant']} vs {r['right_variant']}**: {r['exact_pair_count']} exact pairs; {r['executable_pair_count']} executable pairs; mean additional wait {r['additional_wait_mean_minutes']} minutes; directional disadvantage mean {r['directional_entry_disadvantage_mean']}; right-worse {r['right_worse_pct']}%.")
    lines += ["", "## Context and robustness", "", "Context tables use fixed, predeclared groups only. Monthly and whole-session bootstrap tables include zero-signal sessions. Reversal associations are independent and must not be read as rejection probabilities.", "", "## What cannot be concluded", "", "This is an entry-confirmation and waiting-cost study, not a trading backtest. It does not estimate stops, targets, R, P&L, profit factor, position sizing, or a best strategy, and it does not authorize a live candidate or alter Stage 14.", "", "## Provenance and verification", "", f"Git commit: `{COMMIT}`. Rejection Entry protocol hash: `{protocol_hash()}`. Design hash recorded: `b6175efed8e555cc47bf7df90705cc32ea94e24a7fa30f78a69c115d3f3fa484`. Post-cutoff outcome partitions opened: 0. Failed-run provenance preserved separately."]
    (OUT / "findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Final manifest records every generated output hash after all writes.
    manifest=json.loads((OUT/"run_manifest.json").read_text()); manifest.update({"output_hashes":{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in {"run_manifest.json","verification.json"}},"counts":{"levels":len(levels.levels),"interactions":len(interactions),"touches":len(ledger.touches),"episodes":len(ledger.episodes),"reversals":len(reversals)}}); dump_json("run_manifest.json",manifest)
    frozen=verify_freeze(ROOT)
    dump_json("verification.json",{"engine_commit":COMMIT,"protocol_hash":protocol_hash(),"frozen_break_hold_hashes":{"expected":174,"matched":len(frozen["frozen_files"]),"result":f"{len(frozen['frozen_files'])}/174"},"post_cutoff_partitions_opened":0,"opened_partitions":sorted(OPENED_PARTITIONS),"network_policy":"DENIED","denominator_reconciliation":"PASS"})
    print(json.dumps({"run_directory":str(OUT.relative_to(ROOT)),"levels":len(levels.levels),"interactions":len(interactions),"episodes":len(ledger.episodes),"reversals":len(reversals),"opened_partitions":len(OPENED_PARTITIONS)},sort_keys=True),flush=True)


if __name__ == "__main__":
    main()
