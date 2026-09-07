"""Session-at-a-time orchestration over validated local raw partitions."""
from datetime import date
from hashlib import sha256
import json
import subprocess

from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
from spy_research.data.coverage import SessionCoverage, inventory
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.events.break_and_hold import detect_break_holds
from spy_research.events.break_and_hold_models import FrozenModel, KnownLevel, SessionBreakFacts
from spy_research.levels.premarket import calculate_premarket_levels
from spy_research.levels.previous_day import PreviousDayLevelsService
from spy_research.market import MarketSessionClassifier, XNYSCalendar
from spy_research.outcomes.break_hold_models import HoldOutcome
from spy_research.outcomes.excursions import THRESHOLDS, measure_hold


class BreakHoldReport(FrozenModel):
    start: date
    end: date
    coverage: tuple[SessionCoverage, ...]
    sessions: tuple[SessionBreakFacts, ...]
    outcomes: tuple[HoldOutcome, ...]
    strategy_version: str = "opening_break_hold_v1"
    effective_config_json: str
    definition_hash: str
    input_manifest_hash: str
    git_commit: str | None
    annotations: tuple[str, ...] = (
        "Raw timestamps are minute starts. Outcomes exclude the minute starting exactly at signal close.",
        "First crossing timestamps identify a minute interval, never an exact trade timestamp.",
        "Both-sides-broken is a post-session annotation. Features use only signal-time knowledge.",
        "Fixed horizons past EOD are incomplete and omitted from complete-horizon return summaries.",
        "EOD excursions and pre-reclaim excursions are separate. No-reclaim windows run to EOD.",
        "Close reference prices assume no spread/slippage. No execution/P&L or options model.",
        "Overlapping events are dependent. Strong-hold cohorts are selected survivors.",
        "ATR/VWAP omitted from V1; no filters. Missing previous/premarket context remains unavailable.",
    )


def run_break_hold(config: ResearchConfig, raw_store: RawBarStore, start: date, end: date,
                   *, coverage: tuple[SessionCoverage, ...] | None = None) -> BreakHoldReport:
    if not config.break_and_hold.enabled:
        raise ValueError("break_and_hold is disabled")
    calendar = XNYSCalendar()
    coverage = coverage if coverage is not None else inventory(config, raw_store, start, end, calendar=calendar)
    classifier = MarketSessionClassifier(calendar)
    sessions, outcomes, manifests = [], [], []
    for item in coverage:
        if item.raw_status != "VALID":
            continue
        day = item.session_date
        partition = raw_store.load_partition(day)
        classified = classifier.classify_many(partition)
        session = calendar.session_for_date(day)
        bars = aggregate_rth_1m_to_5m(classified, session)
        rth = tuple(x.bar for x in classified if x.session_type == "RTH")
        pre = tuple(x.bar for x in classified if x.session_type == "PREMARKET")
        levels, unavailable = [], []
        if pre:
            pm = calculate_premarket_levels(pre, calendar=calendar)
            levels.extend(KnownLevel(name=n, price=p, available_at=session.market_open) for n, p in (("PMH", pm.pmh), ("PML", pm.pml)))
        else:
            unavailable.extend(("PMH", "PML"))
        # Existing level service validates prior-session context and does not impute.
        previous = PreviousDayLevelsService(config, raw_store, calendar=calendar).calculate(start=day, end=day)
        if previous.levels:
            pd = previous.levels[0]
            levels.extend(KnownLevel(name=n, price=p, available_at=session.market_open) for n, p in (("PDH", pd.pdh), ("PDL", pd.pdl)))
            path = raw_store.partition_path(pd.source_session_date)
            manifests.append((str(path.relative_to(path.parents[5])), sha256(path.read_bytes()).hexdigest()))
        else:
            unavailable.extend(("PDH", "PDL"))
        facts = detect_break_holds(bars, rth, known_levels=levels, unavailable_levels=tuple(unavailable), calendar=calendar)
        sessions.append(facts)
        for event in facts.events:
            for signal in (event.first_hold, event.strong_hold):
                if signal is not None:
                    outcomes.append(measure_hold(event, signal, rth, session))
        path = raw_store.partition_path(day)
        manifests.append((day.isoformat(), sha256(path.read_bytes()).hexdigest()))
    effective = dict(research=config.model_dump(mode="json"), break_and_hold=config.break_and_hold.model_dump(mode="json"),
        thresholds=[(str(f), str(a)) for f, a in THRESHOLDS], outcome_start="minute_start_strictly_after_signal_close", version="opening_break_hold_v1")
    snapshot = json.dumps(effective, sort_keys=True, separators=(",", ":"))
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return BreakHoldReport(start=start, end=end, coverage=coverage, sessions=tuple(sessions), outcomes=tuple(outcomes),
        effective_config_json=snapshot, definition_hash=sha256(snapshot.encode()).hexdigest(),
        input_manifest_hash=sha256(json.dumps(sorted(set(manifests))).encode()).hexdigest(), git_commit=commit)
