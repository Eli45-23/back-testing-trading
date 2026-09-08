"""Independent set-based coverage and inventory reconciliation, no reactions."""
from collections import Counter
from datetime import date, datetime, time, timedelta
import gzip
import json

from run_study import ROOT, OUT, START, END, CONTEXT_START, OPENED, write_json, digest
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.key_level_reactions.protocol import NY
from spy_research.market import XNYSCalendar

cal = XNYSCalendar()
manifest = json.loads((OUT / "run_manifest.json").read_text())
sessions = json.loads((OUT / "coverage_sessions.json").read_text())
by_day = {x["session_date"]: x for x in sessions}
raw_stores = [RawBarStore(load_research_config(), root=ROOT / x) for x in ("data/raw","data/oos/raw")]
totals, invalid, missing, part_count = Counter(), [], [], 0
for source in manifest["input_partitions"]:
    path = ROOT / source["path"]
    day = date.fromisoformat(path.stem)
    assert CONTEXT_START <= day <= END
    assert digest(path) == source["sha256"]
    store = raw_stores[0] if day >= START else raw_stores[1]
    assert store.partition_path(day) == path
    bars = store.load_partition(day)
    part_count += 1
    timestamps = [b.timestamp for b in bars]
    assert len(timestamps) == len(set(timestamps))
    assert timestamps == sorted(timestamps)
    assert all(t.astimezone(NY).date() == day for t in timestamps)
    session = cal.session_for_date(day)
    assert session.is_trading_day
    count = int((session.market_close-session.market_open).total_seconds()//60)
    expected = {session.market_open + timedelta(minutes=i) for i in range(count)}
    actual = {t for t in timestamps if session.market_open <= t < session.market_close}
    assert expected == actual
    pm_open = datetime.combine(day,time(4),tzinfo=NY)
    pm_n = int((session.market_open-pm_open).total_seconds()//60)
    expected_pm = {pm_open+timedelta(minutes=i) for i in range(pm_n)}
    actual_pm = {t for t in timestamps if pm_open <= t < session.market_open}
    assert actual_pm <= expected_pm
    lane = "development" if day >= START else "context"
    totals[lane+"_sessions"] += 1
    totals[lane+"_rth_minutes"] += len(actual)
    totals[lane+"_pm_observed"] += len(actual_pm)
    totals[lane+"_pm_missing"] += len(expected_pm-actual_pm)
    if lane == "development":
        assert by_day[str(day)]["premarket_certified"] == (actual_pm == expected_pm)
        assert by_day[str(day)]["premarket_bars"] == len(actual_pm)
        totals["development_pm_certified_sessions"] += int(actual_pm == expected_pm)
with gzip.open(OUT / "level_inventory.jsonl.gz","rt") as stream:
    levels = [json.loads(line) for line in stream]
assert len(levels) == len({x["id"] for x in levels})
assert set(x["family"] for x in levels) == {"PDH","PDL","PMH","PML","ORH5","ORL5","PWH","PWL","1H_HIGH","1H_LOW"}
for level in levels:
    at = datetime.fromisoformat(level["available_at"].replace("Z","+00:00"))
    assert at.astimezone(NY).date() <= END
    if level["family"] in ("PMH","PML"):
        assert by_day[str(at.astimezone(NY).date())]["premarket_certified"]
    if level["family"].startswith("1H"):
        assert level["expires_at"] is None
    assert datetime.fromisoformat(level["source_end_at"].replace("Z","+00:00")) <= at
result = {"status":"PASS", "coverage_totals":dict(totals), "input_partition_hashes_matched":part_count,
    "level_inventory_unique_ids":len(levels), "families":dict(Counter(x["family"] for x in levels)),
    "pm_unavailable_family_session_slots":2*(totals["development_sessions"]-totals["development_pm_certified_sessions"]),
    "missing_rth_minutes":0,"duplicate_timestamps":0,
    "opened_partitions":sorted(OPENED),"post_cutoff_partitions_opened":0,
    "touch_episode_outcome_denominator_validation":"NOT_RUN_ENGINE_BLOCKED"}
write_json("independent_coverage_reconciliation.json",result)
print(json.dumps({k:v for k,v in result.items() if k != 'opened_partitions'},sort_keys=True))
