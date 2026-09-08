"""Stable output schemas and canonical serialization; no file writes."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from decimal import Decimal, localcontext
from typing import Literal, get_args
from pydantic import model_validator

from .models import Frozen, LevelSet, Ledger, Reaction, Reversal, Relationship, NextLevel, NextLevelReaction, Coverage, Family
from .protocol import VERSION, DISTANCES, HORIZONS, CONTEXT, NY, BOOTSTRAP_DRAWS, BOOTSTRAP_SEED


class SessionUncertainty(Frozen):
    family: Family
    distance: Decimal
    horizon: int
    draws: int = BOOTSTRAP_DRAWS
    seed: int = BOOTSTRAP_SEED
    contributing_sessions: int
    resampling_sessions: int
    undefined_draws: int
    # Pointwise 95% percentile bounds, not simultaneous or selection intervals.
    intervals: tuple[tuple[str,Decimal | None,Decimal | None], ...]


class FamilySummary(Frozen):
    family: Family
    distance: Decimal
    horizon: int
    touch_minutes: int
    touch_runs: int
    episodes: int
    levels_touched: int
    sessions_touched: int
    available_level_instances: int
    available_sessions: int
    available_level_minutes: int
    unavailable_sessions: int
    status_counts: tuple[tuple[str,int], ...]
    status_rates: tuple[tuple[str,Decimal | None], ...]
    censored: int


def protocol_fingerprint():
    return sha256(Path(__file__).with_name("protocol.py").read_bytes()).hexdigest()


def source_fingerprint():
    parts = [(p.name,sha256(p.read_bytes()).hexdigest()) for p in sorted(Path(__file__).parent.glob("*.py"))]
    return sha256(json.dumps(parts,separators=(",", ":")).encode()).hexdigest()


class Report(Frozen):
    version: Literal["key-level-reactions-v1"] = VERSION
    protocol_hash: str
    source_hash: str
    input_hash: str
    context_start: str
    outcome_start: str
    outcome_end: str
    coverage: tuple[Coverage, ...]
    levels: LevelSet
    ledger: Ledger
    reactions: tuple[Reaction, ...]
    reversals: tuple[Reversal, ...]
    relationships: tuple[Relationship, ...]
    next_levels: tuple[NextLevel, ...]
    denominator_counts: tuple[tuple[str, int], ...]
    next_level_reactions: tuple[NextLevelReaction, ...]
    family_summaries: tuple[FamilySummary, ...]
    session_uncertainty: tuple[SessionUncertainty, ...]

    @model_validator(mode="after")
    def reconcile(self):
        expected = {(e.id,d,h) for e in self.ledger.episodes for d in DISTANCES for h in HORIZONS}
        actual = [(r.episode_id,r.distance,r.horizon) for r in self.reactions]
        if len(actual) != len(expected) or set(actual) != expected:
            raise ValueError("Missing/duplicate reaction panel")
        if self.denominator_counts != counts(self.ledger,self.reactions):
            raise ValueError("Denominator counts do not reconcile")
        sessions = tuple(c.session for c in self.coverage if self.outcome_start <= c.session.isoformat() <= self.outcome_end)
        if self.family_summaries != family_summaries(self.levels,self.ledger,self.reactions,sessions):
            raise ValueError("Family summaries do not reconcile")
        episodes = {e.id for e in self.ledger.episodes}
        if len(self.next_levels) != len(episodes) or {n.episode_id for n in self.next_levels} != episodes:
            raise ValueError("Missing/duplicate next-level snapshot")
        nextr = [(r.episode_id,r.distance,r.horizon) for r in self.next_level_reactions]
        if len(nextr) != len(expected) or set(nextr) != expected:
            raise ValueError("Missing next-level reaction panel")
        ids = {x.id for x in self.levels.levels}
        if len(ids) != len(self.levels.levels) or any(t.level_id not in ids for t in self.ledger.touches):
            raise ValueError("Level identities do not reconcile")
        return self


def canonical(report):
    return json.dumps(report.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"


def fingerprint(records):
    return sha256("\n".join(b.model_dump_json() for b in records).encode()).hexdigest()


def counts(ledger, reactions):
    result = Counter(touch_minutes=len(ledger.touches), episodes=len(ledger.episodes),
        touch_runs=len({(t.level_id, t.touch_run_number) for t in ledger.touches}),
        levels=len({t.level_id for t in ledger.touches}), sessions=len({t.start.astimezone(NY).date() for t in ledger.touches}),
        gap_crosses=len(ledger.gap_crosses))
    for r in reactions:
        result[f"{r.distance}/{r.horizon}/{r.status}"] += 1
    return tuple(sorted(result.items()))


def family_summaries(levels, ledger, reactions, sessions):
    from spy_research.market import XNYSCalendar
    calendar = XNYSCalendar()
    summaries = []
    for family in get_args(Family):
        ids = {x.id for x in levels.levels if x.family == family}
        active_ids, active_days, exposure = set(), set(), 0
        for x in levels.levels:
            if x.family != family:
                continue
            for day in sessions:
                s = calendar.session_for_date(day)
                start = max(s.market_open,x.available_at)
                end = min(s.market_close,x.expires_at or s.market_close)
                if start < end:
                    active_ids.add(x.id)
                    active_days.add(day)
                    exposure += int((end-start).total_seconds()//60)
        touches = [x for x in ledger.touches if x.level_id in ids]
        eps = {x.id for x in ledger.episodes if x.level_id in ids}
        for d in DISTANCES:
            for h in HORIZONS:
                rows = [r for r in reactions if r.episode_id in eps and r.distance == d and r.horizon == h]
                if len(rows) != len(eps):
                    raise ValueError("Every episode must remain in every panel denominator")
                status = Counter(r.status for r in rows)
                names = ("REJECTION_FIRST","CONTINUATION_FIRST","AMBIGUOUS","UNRESOLVED","CENSORED")
                with localcontext(CONTEXT):
                    rates = tuple((name,Decimal(status[name])/Decimal(len(rows)) if rows else None) for name in names)
                summaries.append(FamilySummary(family=family,distance=d,horizon=h,
                    touch_minutes=len(touches),touch_runs=len({(t.level_id,t.touch_run_number) for t in touches}),
                    episodes=len(eps), levels_touched=len({t.level_id for t in touches}),
                    sessions_touched=len({t.start.astimezone(NY).date() for t in touches}),
                    available_level_instances=len(active_ids),available_sessions=len(active_days),available_level_minutes=exposure,
                    unavailable_sessions=len({i.session for i in levels.issues if i.session in sessions and family in i.families and i.reason != "OBSERVED_PREMARKET_NOT_COMPLETENESS_CERTIFIED"}),
                    status_counts=tuple((name,status[name]) for name in names),status_rates=rates,censored=sum(r.censored for r in rows)))
    return tuple(summaries)


def session_uncertainty(levels, ledger, reactions, sessions):
    """Resample entire sessions, including zero-event sessions; no IID touches."""
    names = ("REJECTION_FIRST","CONTINUATION_FIRST","AMBIGUOUS","UNRESOLVED","CENSORED")
    ep_days = {e.id:e.start.astimezone(NY).date() for e in ledger.episodes}
    ep_levels = {e.id:e.level_id for e in ledger.episodes}
    level_families = {x.id:x.family for x in levels.levels}
    result = []
    sessions = tuple(sessions)
    for family in get_args(Family):
        for d in DISTANCES:
            for h in HORIZONS:
                day_counts = {day:Counter() for day in sessions}
                for r in reactions:
                    if r.distance == d and r.horizon == h and level_families[ep_levels[r.episode_id]] == family:
                        day_counts[ep_days[r.episode_id]][r.status] += 1
                contributing = sum(bool(c) for c in day_counts.values())
                rng = Random(BOOTSTRAP_SEED)
                distributions = {name:[] for name in names}
                undefined = 0
                if contributing:
                    with localcontext(CONTEXT):
                        for _ in range(BOOTSTRAP_DRAWS):
                            sampled = Counter()
                            for _ in sessions:
                                sampled.update(day_counts[sessions[rng.randrange(len(sessions))]])
                            denominator = sum(sampled.values())
                            if not denominator:
                                undefined += 1
                                continue
                            for name in names:
                                distributions[name].append(Decimal(sampled[name])/Decimal(denominator))
                else:
                    undefined = BOOTSTRAP_DRAWS
                bounds = []
                for name in names:
                    ordered = sorted(distributions[name])
                    n = len(ordered)
                    # Fixed nearest-rank outward bounds; integer index arithmetic.
                    lo = ordered[(n-1)*25//1000] if n else None
                    hi = ordered[((n-1)*975+999)//1000] if n else None
                    bounds.append((name,lo,hi))
                result.append(SessionUncertainty(family=family,distance=d,horizon=h,
                    contributing_sessions=contributing,resampling_sessions=len(sessions),
                    undefined_draws=undefined,intervals=tuple(bounds)))
    return tuple(result)
