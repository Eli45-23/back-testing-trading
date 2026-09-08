"""Descriptive first passage only, never simulated trades."""
from datetime import timedelta
from decimal import Decimal, localcontext

from .models import Reaction
from .protocol import CONTEXT, DISTANCES, HORIZONS, NY, guard_outcomes, outcome_window


def reactions(episode, level, bars):
    guard_outcomes(episode.start.astimezone(NY).date(), episode.start.astimezone(NY).date())
    if episode.level_id != level.id or level.available_at > episode.start or (level.expires_at is not None and episode.start >= level.expires_at):
        raise ValueError("Episode/level identity or availability mismatch")
    with localcontext(CONTEXT):
        return tuple(_reaction(episode, level, bars, d, h) for d in DISTANCES for h in HORIZONS)


def _reaction(ep, level, bars, d, horizon):
    end = min(ep.end, ep.start + timedelta(minutes=horizon))
    source = outcome_window(ep, bars, horizon)
    up = ep.approach == "ABOVE"
    def away(b):
        return b.high-level.price if up else level.price-b.low
    def through(b):
        return level.price-b.low if up else b.high-level.price
    def close_away(b):
        return b.close-level.price if up else level.price-b.close
    rejection = continuation = reclaim = acceptance = None
    status = "UNRESOLVED"
    closes = 0
    for i, b in enumerate(source):
        known = b.timestamp + timedelta(minutes=1)
        a, c = away(b) >= d, through(b) >= d
        # A touch candle's earlier extrema cannot be asserted post-touch.
        # Its final close can prove a move away, but opposing extremes leave ordering unknown.
        if status == "UNRESOLVED" and (a or c):
            if ep.approach == "UNKNOWN" or (a and c) or (i == 0 and not (a and close_away(b) >= d and not c)):
                status = "AMBIGUOUS"
            else:
                status = "REJECTION_FIRST" if a else "CONTINUATION_FIRST"
        if a and rejection is None and (i > 0 or close_away(b) >= d) and ep.approach != "UNKNOWN":
            rejection = known
        if c and continuation is None and (i > 0 or close_away(b) <= -d) and ep.approach != "UNKNOWN":
            continuation = known
        closes = closes + 1 if close_away(b) < 0 else 0
        if closes >= 2 and acceptance is None:
            acceptance = known
        if rejection is not None and known > rejection and close_away(b) < 0 and reclaim is None:
            reclaim = known
    censored = len(source) < horizon
    if ep.approach == "UNKNOWN":
        status = "AMBIGUOUS"
    elif censored and status == "UNRESOLVED":
        status = "CENSORED"
    n = sum(t + timedelta(minutes=1) <= rejection for t in ep.retest_starts) if rejection else 0
    retests = []
    for t in ep.retest_starts:
        if t >= end:
            continue
        result = "CENSORED" if censored else "UNRESOLVED"
        for b in source:
            if b.timestamp < t:
                continue
            if close_away(b) < 0 and away(b) >= d:
                result = "AMBIGUOUS"
                break
            if close_away(b) < 0:
                result = "FAILED"
                break
            if (b.timestamp > t and away(b) >= d) or close_away(b) >= d:
                result = "HELD"
                break
        retests.append(result)
    single = close_away(source[0]) > 0 and ep.approach != "UNKNOWN"
    confirmed = status == "REJECTION_FIRST"
    if not confirmed:
        reclaim = None
    unknown = ep.approach == "UNKNOWN"
    if unknown:
        acceptance = None
    mfe = max((Decimal(0), close_away(source[0]), *(away(b) for b in source[1:])))
    mae = max((Decimal(0), -close_away(source[0]), *(through(b) for b in source[1:])))
    rejection_order = "NOT_OBSERVED" if rejection is None else "CONFIRMED" if confirmed else "AMBIGUOUS"
    return Reaction(episode_id=ep.id, distance=d, horizon=horizon, status=status,
        observed_minutes=len(source), rejection_known_at=rejection, continuation_known_at=continuation,
        mfe=None if unknown else mfe,
        mae=None if unknown else mae,
        touch_minute_penetration=None if unknown else max(Decimal(0), through(source[0])),
        single_candle_rejection=single, immediate_rejection=confirmed and rejection == ep.start+timedelta(minutes=1),
        single_touch_rejection=confirmed and n == 0, one_retest_rejection=confirmed and n == 1,
        multiple_test_rejection=confirmed and n >= 2, retest_results=tuple(retests),
        acceptance_known_at=acceptance, reclaim_known_at=reclaim,
        quick_reclaim=reclaim is not None and reclaim-rejection <= timedelta(minutes=5),
        later_reclaim=reclaim is not None and reclaim-rejection > timedelta(minutes=5), censored=censored,
        mfe_envelope_upper=None if unknown else max(mfe, away(source[0])),
        mae_envelope_upper=None if unknown else max(mae, through(source[0])),
        final_close_away=None if unknown else close_away(source[-1]),
        time_to_rejection_seconds=None if rejection is None else int((rejection-ep.start).total_seconds()),
        time_to_reclaim_seconds=None if reclaim is None else int((reclaim-rejection).total_seconds()),
        first_retest_delay_seconds=next((int((t-ep.start).total_seconds()) for t in ep.retest_starts if t < end), None),
        touch_count=sum(b.low <= level.price <= b.high for b in source),
        retest_count=sum(t < end for t in ep.retest_starts), rejection_ordering=rejection_order)
