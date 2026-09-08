"""Offline study composition. Calling is explicit; imports never load data."""
from .historical_inputs import validate_bars
from .levels import generate
from .registry import Registry
from .interactions import build_ledger
from .outcomes import reactions
from .reversals import detect
from .confluence import relationships
from .next_level import snapshot, relative_to_reaction
from .reporting import Report, counts, fingerprint, family_summaries, source_fingerprint, protocol_fingerprint, session_uncertainty
from .indicators import AtrAsOf
from .models import Ledger
from .protocol import NY


def build_report(data, calendar=None):
    data = validate_bars(data.bars, data.context_start, data.outcome_start, data.end, calendar)
    from spy_research.market import XNYSCalendar
    calendar = calendar or XNYSCalendar()
    bars = tuple(b for b in data.bars if calendar.session_for_date(b.timestamp.astimezone(NY).date()).market_open <= b.timestamp < calendar.session_for_date(b.timestamp.astimezone(NY).date()).market_close)
    levels = generate(data, calendar)
    registry = Registry(levels.levels)
    full = build_ledger(bars, registry, calendar)
    ledger = Ledger(touches=tuple(t for t in full.touches if t.start.astimezone(NY).date() >= data.outcome_start),
        episodes=tuple(e for e in full.episodes if e.start.astimezone(NY).date() >= data.outcome_start),
        gap_crosses=tuple(g for g in full.gap_crosses if g.start.astimezone(NY).date() >= data.outcome_start))
    by_id = {x.id: x for x in levels.levels}
    atr = AtrAsOf(bars,calendar)
    by_day = {}
    for bar in bars:
        by_day.setdefault(bar.timestamp.astimezone(NY).date(), []).append(bar)
    outcomes, links, nexts, next_reactions = [], [], [], []
    for ep in ledger.episodes:
        level = by_id[ep.level_id]
        source = by_day[ep.start.astimezone(NY).date()]
        measured = reactions(ep, level, source)
        outcomes.extend(measured)
        links.extend(relationships(ep.id, level.price, ep.start, registry, level.source_ids, atr.at(ep.start),calendar))
        nxt = snapshot(ep, level, registry, source)
        nexts.append(nxt)
        next_reactions.extend(relative_to_reaction(nxt,r,ep) for r in measured)
    for touch in ledger.touches:
        level = by_id[touch.level_id]
        links.extend(relationships(touch.id, level.price, touch.start,registry,level.source_ids,atr.at(touch.start),calendar))
    reversals = detect(tuple(b for b in bars if b.timestamp.astimezone(NY).date() >= data.outcome_start))
    for event in reversals:
        links.extend(relationships(event.id, event.turning_price, event.turning_start, registry, atr=atr.at(event.turning_start),calendar=calendar))
    sessions = tuple(c.session for c in data.coverage if c.session >= data.outcome_start)
    return Report(input_hash=fingerprint(data.bars), context_start=str(data.context_start),
        outcome_start=str(data.outcome_start), outcome_end=str(data.end), coverage=data.coverage,
        levels=levels, ledger=ledger, reactions=tuple(outcomes), reversals=reversals,
        relationships=tuple(links), next_levels=tuple(nexts), denominator_counts=counts(ledger, outcomes),
        next_level_reactions=tuple(next_reactions), family_summaries=family_summaries(levels,ledger,outcomes,sessions),
        source_hash=source_fingerprint(), protocol_hash=protocol_fingerprint(),
        session_uncertainty=session_uncertainty(levels,ledger,outcomes,sessions))
