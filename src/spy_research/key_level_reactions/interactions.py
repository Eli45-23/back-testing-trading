"""Exact touch ledger. Prior snapshots precede all current-minute updates."""
from datetime import timedelta

from spy_research.market import XNYSCalendar
from .models import Episode, GapCross, Ledger, Touch
from .protocol import NY, guard_dates, minute_sequence, timestamp_id


def _side(price, level):
    return "ABOVE" if price > level else "BELOW" if price < level else "UNKNOWN"


def _age(level, day, calendar):
    current = level.available_at.astimezone(NY).date()
    age = 0
    while current < day:
        current += timedelta(days=1)
        age += int(calendar.session_for_date(current).is_trading_day)
    return age


def _first_eligible_rth(available, calendar):
    day = available.astimezone(NY).date()
    while True:
        session = calendar.session_for_date(day)
        if session.is_trading_day and available < session.market_close:
            return max(available,session.market_open)
        day += timedelta(days=1)


def build_ledger(bars, registry, calendar=None):
    calendar = calendar or XNYSCalendar()
    bars = minute_sequence(bars)
    if not bars:
        return Ledger(touches=(), episodes=())
    guard_dates(bars[0].timestamp.astimezone(NY).date(), bars[-1].timestamp.astimezone(NY).date())
    if any(a.timestamp >= b.timestamp for a, b in zip(bars, bars[1:])):
        raise ValueError("Duplicate/unordered ledger minutes")
    states, touches, episodes, gaps = {}, [], [], []
    previous = None
    first_rth = None
    for b in bars:
        day = b.timestamp.astimezone(NY).date()
        session = calendar.session_for_date(day)
        if not session.is_trading_day or not session.market_open <= b.timestamp < session.market_close:
            continue
        if first_rth is None:
            first_rth = b.timestamp
        # Gaps within or across sessions are fatal, not counter resets.
        if previous is not None:
            prior_session = calendar.session_for_date(previous.timestamp.astimezone(NY).date())
            expected = previous.timestamp + timedelta(minutes=1)
            if expected == prior_session.market_close:
                next_day = prior_session.session_date + timedelta(days=1)
                while not calendar.session_for_date(next_day).is_trading_day:
                    next_day += timedelta(days=1)
                expected = calendar.session_for_date(next_day).market_open
            if expected != b.timestamp:
                raise ValueError("Missing RTH history; cannot invent counters")
        for level in registry.at(b.timestamp):
            st = states.setdefault(level.id, dict(total=0, session=0, day=day, last=None, runs=0,
                touching=False, breach=False, breaches=0, breach_minutes=0, closes=0,
                first_breach=None, last_breach=None, episode=None, separated=True,
                retest_armed=False, history_start=b.timestamp,
                complete=_first_eligible_rth(level.available_at,calendar) >= first_rth,
                session_complete=max(level.available_at,session.market_open) >= first_rth))
            if st["day"] != day:
                st.update(day=day, session=0, touching=False, episode=None, separated=True, retest_armed=False, session_complete=True)
            touching = b.low <= level.price <= b.high
            if previous is not None and level.available_at <= previous.timestamp and not touching and (
                (previous.close < level.price < b.low) or
                (previous.close > level.price > b.high)):
                gaps.append(GapCross(level_id=level.id, start=b.timestamp,
                    known_at=b.timestamp+timedelta(minutes=1), previous_close=previous.close,
                    open=b.open, through_original_role=(b.open > level.price if level.role == "RESISTANCE" else b.open < level.price)))
            old = st["episode"]
            if old is not None and b.timestamp >= old["end"]:
                st["episode"] = None
                # Retest arming belongs to the expired episode, not its successor.
                # Keep the contact-separation gate and level histories intact.
                st["retest_armed"] = False
            approach = _side(previous.close, level.price) if previous is not None and previous.timestamp.astimezone(NY).date() == day else _side(b.open, level.price)
            if touching:
                if not st["touching"]:
                    st["runs"] += 1
                if st["episode"] is None and st["separated"]:
                    ep = dict(id=f"{level.id}@{timestamp_id(b.timestamp)}", level_id=level.id,
                        start=b.timestamp, end=min(b.timestamp + timedelta(minutes=30), session.market_close),
                        approach=approach, touch_ids=[], retest_starts=[])
                    episodes.append(ep)
                    st["episode"] = ep
                ep = st["episode"]
                if ep is not None and st["retest_armed"]:
                    ep["retest_starts"].append(b.timestamp)
                st["retest_armed"] = False
                identity = f"{level.id}/{timestamp_id(b.timestamp)}"
                touches.append(Touch(id=identity, level_id=level.id, start=b.timestamp,
                    known_at=b.timestamp + timedelta(minutes=1), approach=approach,
                    session_touch_number=st["session"] + 1 if st["session_complete"] else None,
                    lifetime_touch_number=st["total"] + 1 if st["complete"] else None,
                    time_since_previous_touch=None if st["last"] is None else int((b.timestamp-st["last"]).total_seconds()),
                    prior_lifetime_interactions=st["total"] if st["complete"] else None,
                    prior_same_session_interactions=st["session"] if st["session_complete"] else None,
                    first_interaction_since_creation=(st["total"] == 0) if st["complete"] else None,
                    prior_breach_count=st["breaches"] if st["complete"] else None,
                    prior_breach_minute_count=st["breach_minutes"] if st["complete"] else None,
                    prior_close_through_count=st["closes"] if st["complete"] else None,
                    previously_closed_through=True if st["closes"] > 0 else False if st["complete"] else None,
                    first_breach_known_at=st["first_breach"], last_breach_known_at=st["last_breach"],
                    last_touch_known_at=None if st["last"] is None else st["last"]+timedelta(minutes=1),
                    level_age_sessions=_age(level, day, calendar), history_start_at=st["history_start"],
                    history_complete_since_creation=st["complete"], touch_run_number=st["runs"],
                    episode_id=None if ep is None else ep["id"], continuous_contact=st["touching"],
                    open=b.open, high=b.high, low=b.low, close=b.close,
                    prior_price_breached=True if st["breaches"] > 0 else False if st["complete"] else None,
                    observed_lifetime_touch_number=st["total"]+1,
                    observed_session_touch_number=st["session"]+1,
                    observed_prior_breach_count=st["breaches"],
                    observed_prior_breach_minute_count=st["breach_minutes"],
                    observed_prior_close_through_count=st["closes"],session_history_complete=st["session_complete"]))
                if ep is not None:
                    ep["touch_ids"].append(identity)
                st["total"] += 1
                st["session"] += 1
                st["last"] = b.timestamp
                st["separated"] = False
            else:
                st["separated"] = True
                ep = st["episode"]
                if ep is not None and ((ep["approach"] == "ABOVE" and b.low > level.price) or
                                       (ep["approach"] == "BELOW" and b.high < level.price)):
                    st["retest_armed"] = True
            breached = b.high > level.price if level.role == "RESISTANCE" else b.low < level.price
            closed = b.close > level.price if level.role == "RESISTANCE" else b.close < level.price
            reset = b.high <= level.price if level.role == "RESISTANCE" else b.low >= level.price
            if breached:
                st["breach_minutes"] += 1
                if not st["breach"]:
                    st["breaches"] += 1
                st["breach"] = True
                st["last_breach"] = b.timestamp + timedelta(minutes=1)
                if st["first_breach"] is None:
                    st["first_breach"] = st["last_breach"]
            elif reset:
                st["breach"] = False
            st["closes"] += int(closed)
            st["touching"] = touching
        previous = b
    return Ledger(touches=tuple(touches), episodes=tuple(Episode(**e) for e in episodes), gap_crosses=tuple(gaps))
