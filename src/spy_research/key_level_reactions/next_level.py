"""Touch-time snapshot; future levels never replace it."""
from datetime import timedelta
from .models import NextLevel, NextLevelReaction
from .protocol import outcome_window


def snapshot(ep, level, registry, bars):
    if ep.level_id != level.id or level not in registry.at(ep.start):
        raise ValueError("Snapshot level unavailable or identity mismatch")
    source = outcome_window(ep, bars, 30)
    if ep.approach == "UNKNOWN":
        return NextLevel(episode_id=ep.id, snapshot_at=ep.start, level_ids=(), price=None, status="UNKNOWN_DIRECTION")
    up = ep.approach == "ABOVE"
    eligible = [x for x in registry.at(ep.start) if (x.price > level.price if up else x.price < level.price)]
    if not eligible:
        return NextLevel(episode_id=ep.id, snapshot_at=ep.start, level_ids=(), price=None, status="NO_NEXT_LEVEL")
    price = (min if up else max)(x.price for x in eligible)
    ids = tuple(sorted(x.id for x in eligible if x.price == price))
    reached = invalid = None
    state = "UNRESOLVED"
    for b in source:
        hit = b.low <= price <= b.high
        failed = b.close < level.price if up else b.close > level.price
        known = b.timestamp+timedelta(minutes=1)
        if hit and reached is None:
            reached = known
        if failed and invalid is None:
            invalid = known
        if state == "UNRESOLVED":
            if hit and (failed or b.timestamp == ep.start):
                state = "AMBIGUOUS"
            elif hit:
                state = "REACHED_FIRST"
            elif failed:
                state = "INVALIDATED_FIRST"
    if state == "UNRESOLVED" and ep.end < ep.start+timedelta(minutes=30):
        state = "CENSORED"
    return NextLevel(episode_id=ep.id, snapshot_at=ep.start, level_ids=ids, price=price, status=state,
        reached_known_at=reached, invalidated_known_at=invalid,
        censored=ep.end < ep.start+timedelta(minutes=30))


def relative_to_reaction(next_level, reaction, episode):
    """Never call a pre-recognition hit a subsequent rejection achievement."""
    recognition = reaction.rejection_known_at
    hit = next_level.reached_known_at
    horizon_end = min(episode.end, episode.start+timedelta(minutes=reaction.horizon))
    before = None
    if hit is not None and hit > horizon_end:
        hit = None
    if next_level.price is None:
        result = next_level.status
    elif reaction.rejection_ordering != "CONFIRMED":
        result = "NO_CONFIRMED_REJECTION"
    elif hit is None:
        result = "NOT_REACHED_WITHIN_HORIZON"
    elif hit == recognition:
        result = "SAME_MINUTE_AS_RECOGNITION_AMBIGUOUS"
    elif hit < recognition:
        before, result = True, "REACHED_BEFORE_RECOGNITION"
    else:
        before = False
        invalid = next_level.invalidated_known_at
        result = "REACHED_AFTER_RECOGNITION" if invalid is None or hit < invalid else "AMBIGUOUS" if hit == invalid else "INVALIDATED_BEFORE_REACH"
    return NextLevelReaction(episode_id=episode.id, distance=reaction.distance, horizon=reaction.horizon,
        reached_before_recognition=before, result=result)
