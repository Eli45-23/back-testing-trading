"""Read-only diagnosis of the committed ledger's episode-boundary failure."""
from datetime import date, datetime, timedelta
from decimal import Decimal as D
import gzip
import json

from run_study import OUT, ROOT, audit, digest, write_json
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.data.schemas import RawBarRecord
from spy_research.key_level_reactions.models import Level
from spy_research.key_level_reactions.protocol import NY
from spy_research.key_level_reactions.registry import Registry
from spy_research.key_level_reactions.interactions import build_ledger
from pydantic import ValidationError

T = datetime(2026, 1, 5, 9, 30, tzinfo=NY)


def bar(i, touch):
    return RawBarRecord(symbol="SPY", timestamp=T+timedelta(minutes=i),
        open=D("99.9"), high=D("100" if touch else "99.95"), low=D("99.8"), close=D("99.9"),
        volume=10, trade_count=1, vwap=D("99.9"), source="alpaca", feed="sip", timeframe="1Min", adjustment="raw")


def failure(bars, levels):
    try:
        build_ledger(bars, Registry(levels))
    except ValidationError as exc:
        errors = exc.errors(include_url=False, include_context=False)
        assert any("Retest outside episode" in e["msg"] for e in errors)
        ep = errors[0]["input"]
        return {"message": errors[0]["msg"], "episode_id": ep["id"], "start": ep["start"],
            "end": ep["end"], "retest_starts": ep["retest_starts"],
            "retest_at_episode_start": ep["start"] in ep["retest_starts"]}
    raise AssertionError("Expected committed boundary defect was not reproduced")


level = Level(id="synthetic-resistance", family="1H_HIGH", role="RESISTANCE", price=D("100"),
    source_timeframe="1H_RTH_FULL_BARS", source_ids=("synthetic-source",),
    source_start_at=T-timedelta(hours=3), source_end_at=T, created_at=T, available_at=T)
synthetic = failure(tuple(bar(i, i in (0,30)) for i in range(31)), (level,))
with gzip.open(OUT / "level_inventory.jsonl.gz", "rt") as stream:
    levels = tuple(Level.model_validate_json(line) for line in stream)
store = RawBarStore(load_research_config(), root=ROOT / "data/oos/raw")
path = store.partition_path(date(2025,12,22))
before = digest(path)
source = tuple(b for b in store.load_partition(date(2025,12,22)) if 570 <= b.timestamp.astimezone(NY).hour*60+b.timestamp.astimezone(NY).minute < 960)
historical_context = failure(source, levels)
assert digest(path) == before
result = {"synthetic_reproduction": synthetic, "historical_context_reproduction": historical_context,
    "diagnosis": "retest_armed survives expiration of an earlier episode; the first touch of a new episode is appended as its own retest",
    "source_change_made": False, "reaction_outcomes_calculated": False,
    "expected_behavior": "A new episode's first touch is not its own retest; strict episode validation must remain intact"}
write_json("blocker.json", result)
print(json.dumps(result, default=str, indent=2))
