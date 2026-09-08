"""Synthetic-only protocol regressions. Never load historical partitions."""
from datetime import date, datetime, timedelta
from decimal import Decimal as D

import pytest

from spy_research.data.schemas import RawBarRecord
from spy_research.market import XNYSCalendar
from spy_research.key_level_reactions.protocol import NY, DISTANCES, HORIZONS
from spy_research.key_level_reactions.models import Level, Hour
from spy_research.key_level_reactions.registry import Registry
from spy_research.key_level_reactions.historical_inputs import validate_bars, load_local
from spy_research.key_level_reactions.higher_timeframes import hours
from spy_research.key_level_reactions.levels import generate, swing_levels
from spy_research.key_level_reactions.interactions import build_ledger
from spy_research.key_level_reactions.outcomes import reactions
from spy_research.key_level_reactions.reversals import detect
from spy_research.key_level_reactions.confluence import relationships
from spy_research.key_level_reactions.next_level import snapshot
from spy_research.key_level_reactions.service import build_report
from spy_research.key_level_reactions.reporting import canonical


T = datetime(2026, 1, 5, 9, 30, tzinfo=NY)


def bar(t=T, o="99.9", h="100", l="99.8", c="99.9"):
    return RawBarRecord(symbol="SPY", timestamp=t, open=D(o), high=D(h), low=D(l), close=D(c),
        volume=10, trade_count=1, vwap=D(c), source="alpaca", feed="sip", timeframe="1Min", adjustment="raw")


def level(price="100", identity="a", at=T, family="1H_HIGH"):
    return Level(id=identity, family=family, role="RESISTANCE" if family == "1H_HIGH" else "SUPPORT",
        price=D(price), source_timeframe="1H_RTH_FULL_BARS", source_ids=("source",),
        source_start_at=at-timedelta(hours=3), source_end_at=at,
        created_at=at, available_at=at)


def session(day=date(2026, 1, 5)):
    s = XNYSCalendar().session_for_date(day)
    return tuple(bar(s.market_open+timedelta(minutes=i)) for i in range(int((s.market_close-s.market_open).total_seconds()/60)))


def test_immutable_family_and_time_guards():
    x = level()
    with pytest.raises(Exception):
        x.price = D(1)
    for family in ("4H_HIGH", "5M_HIGH", "PDC"):
        with pytest.raises(Exception):
            Level(**{**x.model_dump(), "family": family})
    with pytest.raises(Exception):
        Level(**{**x.model_dump(), "available_at": T-timedelta(minutes=1)})


def test_date_guard_before_store_read():
    class Store:
        def load_partition(self, day):
            pytest.fail("Protected date must fail before IO")
    with pytest.raises(ValueError):
        load_local(Store(), context_start=date(2026,1,2), outcome_start=date(2026,1,2), end=date(2026,9,8))


def test_missing_duplicate_and_outside_minutes_fail():
    bs = session()
    for invalid in (bs[:-1], bs[:20]+bs[21:], bs+(bs[-1],)):
        with pytest.raises(ValueError):
            validate_bars(invalid, date(2026,1,5), date(2026,1,5), date(2026,1,5))


@pytest.mark.parametrize("day,n", [(date(2026,1,5),6),(date(2025,11,28),3)])
def test_full_hours_early_close(day,n):
    hs = hours(session(day))
    assert len(hs) == n
    assert all(h.end-h.start == timedelta(hours=1) for h in hs)
    assert all(len(h.source_ids) == 60 for h in hs)


def test_dst_local_anchor():
    for day in (date(2026,3,6),date(2026,3,9)):
        assert hours(session(day))[0].start.astimezone(NY).hour == 9
        assert hours(session(day))[0].start.astimezone(NY).minute == 30


def test_pivot_confirmation_and_prefix_stability():
    hs = tuple(Hour(id=str(i),start=T+timedelta(hours=i),end=T+timedelta(hours=i+1),
                    high=D(x),low=D("90"),source_ids=(str(i),)) for i,x in enumerate((100,101,105,102,101,100)))
    assert not swing_levels(hs[:4])
    swings = swing_levels(hs)
    assert len(swings) == 1
    x = swings[0]
    assert x.available_at == T+timedelta(hours=5)
    assert Registry(swings).at(x.available_at-timedelta(microseconds=1)) == ()
    assert Registry(swings).at(x.available_at) == swings
    assert swing_levels(hs[:5]) == swings
    tied = list(hs); tied[3] = tied[3].model_copy(update={"high":D(105)})
    assert not swing_levels(tied)


def test_or_cannot_touch_own_source_and_pm_explicit():
    data = validate_bars(session(),date(2026,1,5),date(2026,1,5),date(2026,1,5))
    result = generate(data)
    ors = [x for x in result.levels if x.family.startswith("OR")]
    assert len(ors) == 2
    ledger = build_ledger(data.bars,Registry(ors))
    assert all(t.start >= T+timedelta(minutes=5) for t in ledger.touches)
    assert any(i.reason == "NO_PREMARKET_DATA" for i in result.issues)


def test_pdh_week_holiday_context():
    # Complete preceding holiday week, then Monday; Jan 1 is not expected.
    days = [date(2025,12,29),date(2025,12,30),date(2025,12,31),date(2026,1,2),date(2026,1,5)]
    bs = tuple(b for day in days for b in session(day))
    data = validate_bars(bs,days[0],days[-1],days[-1])
    ls = generate(data).levels
    assert any(x.family == "PDH" and x.available_at == T for x in ls)
    weekly = [x for x in ls if x.family == "PWH"]
    assert len(weekly) == 1 and weekly[0].available_at == T


def test_exact_touch_not_proximity_and_separate_equal_ids():
    bs = (bar(),bar(T+timedelta(minutes=1),h="99.99"))
    ledger = build_ledger(bs,Registry((level(),level(identity="b"))))
    assert len(ledger.touches) == 2
    assert all(t.lifetime_touch_number == 1 for t in ledger.touches)
    links = relationships("x",D(100),T,Registry((level(),level("100.01","c"))))
    assert len(links) == 2


def test_prior_counter_snapshot_and_touch_runs():
    bs = (bar(),bar(T+timedelta(minutes=1)),bar(T+timedelta(minutes=2),h="99.9"),bar(T+timedelta(minutes=3)))
    ledger = build_ledger(bs,Registry((level(),)))
    assert [t.lifetime_touch_number for t in ledger.touches] == [1,2,3]
    assert [t.prior_lifetime_interactions for t in ledger.touches] == [0,1,2]
    assert [t.touch_run_number for t in ledger.touches] == [1,1,2]
    assert ledger.touches[-1].time_since_previous_touch == 120
    assert ledger.episodes[0].retest_starts == (T+timedelta(minutes=3),)


def test_gap_breach_and_completed_close_history():
    bs = (bar(o="101",h="101",l="100.5",c="100.8"),bar(T+timedelta(minutes=1)))
    t = build_ledger(bs,Registry((level(),))).touches[0]
    assert t.lifetime_touch_number == 1
    assert t.prior_breach_count == 1 and t.prior_close_through_count == 1
    assert t.previously_closed_through


def test_current_breach_not_in_own_snapshot():
    bs = (bar(h="100.2",c="100.1"),bar(T+timedelta(minutes=1)))
    ts = build_ledger(bs,Registry((level(),))).touches
    assert ts[0].prior_breach_count == 0
    assert ts[1].prior_breach_count == 1


def test_unknown_history_not_first_and_gap_fails():
    ts = build_ledger((bar(),),Registry((level(at=T-timedelta(days=30)),))).touches
    assert ts[0].first_interaction_since_creation is None
    assert not ts[0].history_complete_since_creation
    assert ts[0].lifetime_touch_number is None and ts[0].prior_breach_count is None
    assert ts[0].observed_lifetime_touch_number == 1
    with pytest.raises(ValueError):
        build_ledger((bar(),bar(T+timedelta(minutes=2))),Registry((level(),)))


def test_persistence_over_twenty_sessions_and_session_reset():
    bs = []
    day = date(2026,1,5)
    calendar = XNYSCalendar()
    for _ in range(32):
        if calendar.session_for_date(day).is_trading_day:
            bs.extend(session(day))
        day += timedelta(days=1)
    ls = level()
    ts = build_ledger(bs,Registry((ls,))).touches
    assert ts[-1].level_age_sessions > 20
    assert ts[390].session_touch_number == 1 and ts[390].lifetime_touch_number == 391
    assert Registry((ls,)).at(bs[-1].timestamp) == (ls,)


def test_continuous_contact_not_duplicate_episodes():
    bs = tuple(bar(T+timedelta(minutes=i)) for i in range(35))
    ledger = build_ledger(bs,Registry((level(),)))
    assert len(ledger.touches) == 35 and len(ledger.episodes) == 1
    assert ledger.touches[-1].episode_id is None


@pytest.mark.parametrize("next_touch_minute", [30, 31, 35])
@pytest.mark.parametrize("family", ["1H_HIGH", "1H_LOW"])
def test_expired_episode_cannot_retest_its_own_first_touch(next_touch_minute, family):
    # Exact blocker: touch, approach-side separation, expiration, then a new touch.
    # Mirror support/resistance; test both the exact endpoint and a later restart.
    resistance = family == "1H_HIGH"
    def source(i):
        touching = i in (0, next_touch_minute)
        return bar(T+timedelta(minutes=i),
            o="99.9" if resistance else "100.1",
            h=("100" if touching else "99.95") if resistance else "100.2",
            l="99.8" if resistance else ("100" if touching else "100.05"),
            c="99.9" if resistance else "100.1")
    ledger = build_ledger(tuple(source(i) for i in range(next_touch_minute+1)),
        Registry((level(family=family),)))
    first, second = ledger.episodes
    assert first.start == T and first.end == T+timedelta(minutes=30)
    assert second.start == T+timedelta(minutes=next_touch_minute)
    assert first.retest_starts == second.retest_starts == ()
    assert first.touch_ids == (ledger.touches[0].id,)
    assert second.touch_ids == (ledger.touches[1].id,)
    assert [t.episode_id for t in ledger.touches] == [first.id, second.id]
    assert [t.session_touch_number for t in ledger.touches] == [1, 2]
    assert [t.lifetime_touch_number for t in ledger.touches] == [1, 2]


def test_retests_and_prior_histories_remain_independent_across_three_episodes():
    touch_minutes = (0, 3, 30, 33, 60, 63)
    breach_minutes = (0, 30, 60)
    bs = tuple(bar(T+timedelta(minutes=i),
        h="100.2" if i in breach_minutes else "100" if i in touch_minutes else "99.95",
        c="100.1" if i in breach_minutes else "99.9") for i in range(64))
    ledger = build_ledger(bs, Registry((level(),)))
    assert len(ledger.episodes) == 3
    assert len({e.id for e in ledger.episodes}) == 3
    for i, ep in enumerate(ledger.episodes):
        assert ep.start == T+timedelta(minutes=i*30)
        assert ep.retest_starts == (T+timedelta(minutes=i*30+3),)
        assert ep.touch_ids == tuple(t.id for t in ledger.touches[i*2:i*2+2])
        assert all(ep.start < t < ep.end for t in ep.retest_starts)
    # Episode-scoped cleanup must not reset level/session history.
    for i, touch in enumerate(ledger.touches):
        assert touch.session_touch_number == touch.lifetime_touch_number == i+1
        assert touch.observed_session_touch_number == touch.observed_lifetime_touch_number == i+1
        assert touch.prior_same_session_interactions == touch.prior_lifetime_interactions == i
        assert touch.touch_run_number == i+1
        assert touch.first_interaction_since_creation == (i == 0)
        assert touch.history_complete_since_creation and touch.session_history_complete
        assert touch.level_age_sessions == 0
        prior_breaches = sum(m < touch_minutes[i] for m in breach_minutes)
        assert touch.prior_breach_count == touch.observed_prior_breach_count == prior_breaches
        assert touch.prior_breach_minute_count == touch.observed_prior_breach_minute_count == prior_breaches
        assert touch.prior_close_through_count == touch.observed_prior_close_through_count == prior_breaches
        assert touch.previously_closed_through == touch.prior_price_breached == bool(prior_breaches)
        assert touch.first_breach_known_at == (T+timedelta(minutes=1) if i else None)
        last_breach = next((m for m in reversed(breach_minutes) if m < touch_minutes[i]), None)
        assert touch.last_breach_known_at == (None if last_breach is None else T+timedelta(minutes=last_breach+1))
        assert touch.time_since_previous_touch == (None if i == 0 else (touch_minutes[i]-touch_minutes[i-1])*60)
        assert touch.last_touch_known_at == (None if i == 0 else T+timedelta(minutes=touch_minutes[i-1]+1))
    # Later episodes cannot change any already-observed history snapshot.
    prefix = build_ledger(bs[:30], Registry((level(),)))
    assert ledger.touches[:2] == prefix.touches
    assert ledger.episodes[0] == prefix.episodes[0]
    assert ledger.gap_crosses[:len(prefix.gap_crosses)] == prefix.gap_crosses


def test_expiration_preserves_continuous_contact_separation_gate():
    # Expiration alone cannot fabricate separation or another episode.
    bs = tuple(bar(T+timedelta(minutes=i), h="99.95" if i == 35 else "100")
        for i in range(37))
    ledger = build_ledger(bs, Registry((level(),)))
    assert [e.start for e in ledger.episodes] == [T, T+timedelta(minutes=36)]
    assert all(not e.retest_starts for e in ledger.episodes)
    assert all(t.episode_id is None for t in ledger.touches if 30 <= int((t.start-T).total_seconds()//60) < 35)
    assert len(ledger.touches) == 36
    assert ledger.touches[-1].lifetime_touch_number == ledger.touches[-1].session_touch_number == 36
    assert ledger.touches[-1].touch_run_number == 2


def test_episode_validator_still_rejects_retests_at_both_window_boundaries():
    from spy_research.key_level_reactions.models import Episode
    end = T+timedelta(minutes=30)
    for invalid_retest in (T, end):
        with pytest.raises(ValueError, match="Retest outside episode"):
            Episode(id="boundary", level_id="a", start=T, end=end, approach="BELOW",
                touch_ids=("first",), retest_starts=(invalid_retest,))


def test_immediate_rejection_and_quick_reclaim():
    bs = [bar(o="99.9",h="100",l="99.7",c="99.7")]
    bs += [bar(T+timedelta(minutes=i),h="100.1",c="100.05") for i in range(1,30)]
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    rs = reactions(ep,level(),bs)
    assert len(rs) == 9
    r = rs[0]
    assert r.status == "REJECTION_FIRST" and r.immediate_rejection
    assert r.single_touch_rejection and r.quick_reclaim


def test_same_minute_ambiguity_and_censoring():
    bs = (bar(t=T.replace(hour=15,minute=59),h="100.5",l="99.5"),)
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    r = reactions(ep,level(),bs)[0]
    assert r.status == "AMBIGUOUS" and r.censored


def test_reversal_prefix_and_future_level_exclusion():
    bs = tuple(bar(T+timedelta(minutes=i),o=str(x),h=str(x),l=str(x),c=str(x)) for i,x in enumerate((100,100.5,100.75,100.4,100.3)))
    events = [x for x in detect(bs) if not x.censored]
    assert events and events[0].turning_start == T+timedelta(minutes=2)
    future = level(at=T+timedelta(minutes=3))
    assert not relationships(events[0].id,events[0].turning_price,events[0].turning_start,Registry((future,)))
    assert [x for x in detect(bs[:4]) if not x.censored] == events


def test_next_level_ties_and_future_not_substituted():
    base = level()
    reg = Registry((base,level("99","b",family="1H_LOW"),level("99","c",family="1H_LOW"),level("99.5","future",at=T+timedelta(minutes=1),family="1H_LOW")))
    bs = tuple(bar(T+timedelta(minutes=i)) for i in range(30))
    ep = build_ledger(bs,reg).episodes[0]
    nxt = snapshot(ep,base,reg,bs)
    assert nxt.price == D(99) and nxt.level_ids == ("b","c")


def test_synthetic_full_service_deterministic_no_data_access():
    data = validate_bars(session(),date(2026,1,5),date(2026,1,5),date(2026,1,5))
    a,b = build_report(data),build_report(data)
    assert canonical(a) == canonical(b)
    assert len(a.reactions) == 9*len(a.ledger.episodes)
    assert {r.distance for r in a.reactions} == set(DISTANCES)
    assert {r.horizon for r in a.reactions} == set(HORIZONS)


def episode_bars(changes=None, start=T):
    changes = changes or {}
    return tuple(bar(start+timedelta(minutes=i),**changes.get(i,{})) for i in range(30))


@pytest.mark.parametrize("retests", [1,2,3])
def test_retest_classification(retests):
    changes = {}
    for i in range(retests):
        changes[1+2*i] = dict(h="99.95",l="99.9",o="99.9",c="99.9")
    recognition_index = 2*retests+1
    changes[recognition_index] = dict(o="99.9",h="99.95",l="99.7",c="99.7")
    for i in range(recognition_index+1,30):
        changes[i] = dict(o="99.7",h="99.75",l="99.6",c="99.7")
    bs = episode_bars(changes)
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    rs = reactions(ep,level(),bs)
    r = next(r for r in rs if r.distance == D("0.25") and r.horizon == 30)
    assert r.retest_count == retests
    assert r.one_retest_rejection == (retests == 1)
    assert r.multiple_test_rejection == (retests >= 2)
    assert r.retest_results == ("HELD",)*retests


def test_retest_failure_and_two_close_acceptance():
    bs = episode_bars({1:dict(h="99.95"),3:dict(h="100.1",c="100.05"),4:dict(h="100.2",c="100.1")})
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    r = reactions(ep,level(),bs)[0]
    assert r.retest_results == ("FAILED",)
    assert r.acceptance_known_at == T+timedelta(minutes=5)


def test_retest_requires_wholly_approach_side_departure():
    bs = episode_bars({1:dict(o="100.1",h="100.2",l="100.05",c="100.1")})
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    assert not ep.retest_starts


@pytest.mark.parametrize("direction", ["UP","DOWN"])
def test_immediate_mirrored_reaction(direction):
    if direction == "UP":
        x = level(family="1H_LOW")
        bs = tuple(bar(T+timedelta(minutes=i),o="100.1",h="100.3",l="100",c="100.3") for i in range(30))
    else:
        x = level()
        bs = tuple(bar(T+timedelta(minutes=i),o="99.9",h="100",l="99.7",c="99.7") for i in range(30))
    ep = build_ledger(bs,Registry((x,))).episodes[0]
    r = reactions(ep,x,bs)[0]
    assert r.immediate_rejection and r.single_touch_rejection
    assert r.mfe == D("0.3") and r.mae == 0


def test_pre_touch_extreme_not_reported_as_certain_mfe():
    bs = episode_bars({0:dict(l="99",h="100",c="99.9")})
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    r = reactions(ep,level(),bs)[0]
    assert r.status == "AMBIGUOUS"
    assert r.mfe == D("0.2") and r.mfe_envelope_upper == D(1)
    assert not r.immediate_rejection


def test_missing_outcome_tail_is_error_not_eod():
    bs = episode_bars()
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    with pytest.raises(ValueError,match="Missing outcome"):
        reactions(ep,level(),bs[:4])
    with pytest.raises(ValueError,match="Missing outcome"):
        snapshot(ep,level(),Registry((level(),)),bs[:4])


def test_unknown_direction_metrics_are_null():
    bs = tuple(bar(T+timedelta(minutes=i),o="100",h="100",l="100",c="100") for i in range(30))
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    rs = reactions(ep,level(),bs)
    assert all(r.status == "AMBIGUOUS" and r.mfe is None and r.mae is None for r in rs)


def test_ledger_causal_prefix_unchanged_by_future():
    bs = episode_bars({10:dict(h="101",c="100.5")})
    reg = Registry((level(),))
    prefix = build_ledger(bs[:10],reg)
    full = build_ledger(bs,reg)
    assert prefix.touches == full.touches[:10]
    # Episode summaries may accrue outcomes, prior snapshots may not.
    assert full.touches[10].prior_breach_count == 0


def test_breach_episodes_count_not_every_through_minute():
    bs = episode_bars({0:dict(h="100.1",c="100.05"),1:dict(h="100.2",c="100.1"),3:dict(h="100.1",c="100.05")})
    ts = build_ledger(bs,Registry((level(),))).touches
    assert ts[2].prior_breach_count == 1
    assert ts[2].prior_breach_minute_count == 2
    assert ts[4].prior_breach_count == 2


def test_support_breach_mirror_and_equality_not_breach():
    bs = tuple(bar(T+timedelta(minutes=i),o="100",h="100.1",l="99.9" if i == 0 else "100",c="99.95" if i == 0 else "100") for i in range(3))
    ts = build_ledger(bs,Registry((level(family="1H_LOW"),))).touches
    assert ts[0].prior_breach_count == 0
    assert ts[1].prior_breach_count == 1 and ts[1].previously_closed_through
    assert ts[2].prior_breach_count == 1 and ts[2].prior_close_through_count == 1


def test_or_and_pivot_available_exact_boundary_no_source_reuse():
    bs = session()
    pivot = level(at=T+timedelta(hours=5))
    ts = build_ledger(bs,Registry((pivot,))).touches
    assert ts[0].start == T+timedelta(hours=5)
    assert ts[0].known_at == T+timedelta(hours=5,minutes=1)
    assert ts[0].prior_lifetime_interactions == 0


def test_pm_levels_final_at_open_not_last_observed_bar():
    pm = bar(T.replace(hour=4,minute=0),h="105",l="95")
    bs = (pm,*session())
    data = validate_bars(bs,date(2026,1,5),date(2026,1,5),date(2026,1,5))
    x = next(x for x in generate(data).levels if x.family == "PMH")
    assert x.price == D(105)
    assert x.created_at == T and x.available_at == T
    assert data.coverage[0].premarket_status == "OBSERVED_NOT_COMPLETENESS_CERTIFIED"


def test_incomplete_prior_week_not_quietly_partial():
    bs = tuple(b for day in (date(2026,1,2),date(2026,1,5)) for b in session(day))
    data = validate_bars(bs,date(2026,1,2),date(2026,1,5),date(2026,1,5))
    ls = generate(data)
    assert not any(x.family == "PWH" for x in ls.levels)
    assert any(i.session == date(2026,1,5) and i.reason == "MISSING_PRIOR_WEEK_CONTEXT" for i in ls.issues)


def test_missing_hour_does_not_confirm_across_gap():
    hs = hours(session())
    with pytest.raises(ValueError,match="Missing pivot hour"):
        swing_levels(hs[:2]+hs[3:])
    with pytest.raises(ValueError,match="Missing hour source"):
        hours(session()[:50]+session()[51:])


def test_pivot_across_session_no_overnight_or_terminal_candle():
    hs = list(hours(session()+session(date(2026,1,6))))
    hs[5] = hs[5].model_copy(update={"high":D(105)})
    x = next(x for x in swing_levels(hs) if x.family == "1H_HIGH")
    assert x.pivot_bar_start_at == T.replace(hour=14,minute=30)
    assert x.available_at == T.replace(day=6,hour=11,minute=30)
    assert len(x.source_ids) == 5


def test_atr_completed_only_and_session_reset():
    from spy_research.key_level_reactions.indicators import AtrAsOf
    atr = AtrAsOf(session()+session(date(2026,1,6)))
    assert atr.at(T+timedelta(minutes=69)) is None
    value, known = atr.at(T+timedelta(minutes=70))
    assert known == T+timedelta(minutes=70) and value == D("0.2")
    assert atr.at(T.replace(day=6)) is None
    with pytest.raises(ValueError,match="Future ATR"):
        relationships("x",D(100),T,Registry((level(),)),atr=(value,known))


def test_zero_atr_and_distance_buckets():
    reg = Registry(tuple(level(str(D(100)+d),identity=str(d)) for d in (D(0),D("0.05"),D("0.10"),D("0.25"),D("0.2501"))))
    links = relationships("x",D(100),T,reg,atr=(D(0),T))
    assert {l.bucket for l in links} == {"0","0.05","0.10","0.25",">0.25"}
    assert all(l.atr_status == "ZERO_ATR" and l.distance_atr is None for l in links)


@pytest.mark.parametrize("when", [0,1,2])
def test_next_level_relative_recognition(when):
    from spy_research.key_level_reactions.next_level import relative_to_reaction
    # Recognition of the $0.50 reversal occurs at minute 1 close; next level
    # at 99.75 can be reached before, in, or after that minute depending on path.
    bs = episode_bars({0:dict(h="100",l="99.9"),1:dict(h="99.9",l="99.4",o="99.9",c="99.4")})
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    r = next(r for r in reactions(ep,level(),bs) if r.distance == D("0.50") and r.horizon == 5)
    from spy_research.key_level_reactions.models import NextLevel
    nxt = NextLevel(episode_id=ep.id,snapshot_at=T,level_ids=("b",),price=D("99.75"),status="REACHED_FIRST",reached_known_at=T+timedelta(minutes=when+1))
    result = relative_to_reaction(nxt,r,ep)
    assert result.result == ("REACHED_BEFORE_RECOGNITION","SAME_MINUTE_AS_RECOGNITION_AMBIGUOUS","REACHED_AFTER_RECOGNITION")[when]


def test_next_level_same_minute_invalidation_ambiguous():
    bs = episode_bars({1:dict(l="99.4",h="100.1",c="100.05")})
    reg = Registry((level(),level("99.5","next",family="1H_LOW")))
    ep = build_ledger(bs,reg).episodes[0]
    nxt = snapshot(ep,level(),reg,bs)
    assert nxt.status == "AMBIGUOUS"
    assert nxt.reached_known_at == nxt.invalidated_known_at


@pytest.mark.parametrize("operation", ["validate","ledger","outcomes","reversal","cli"])
def test_protected_dates_rejected_every_public_lane(operation):
    future = bar(T.replace(month=9,day=8))
    with pytest.raises(ValueError):
        if operation == "validate":
            validate_bars((future,),date(2026,9,8),date(2026,9,8),date(2026,9,8))
        elif operation == "ledger":
            build_ledger((future,),Registry((level(),)))
        elif operation == "outcomes":
            ep = build_ledger(episode_bars(),Registry((level(),))).episodes[0]
            reactions(ep,level(),(*episode_bars(),future))
        elif operation == "reversal":
            detect((future,))
        else:
            from spy_research.key_level_reactions.cli import main
            main(["--raw-root","/does-not-exist","--context-start","2026-01-02","--start","2026-01-02","--end","2026-09-08","--run"])


def test_reversal_unestablished_and_no_session_carry():
    bs = (bar(),bar(T.replace(day=6),o="101",h="101",l="101",c="101"))
    result = detect(bs)
    assert len(result) == 6 and all(x.censored and x.direction == "UNESTABLISHED" for x in result)


def test_decimal_context_independence_and_float_rejected():
    from decimal import localcontext
    bs = episode_bars()
    ep = build_ledger(bs,Registry((level(),))).episodes[0]
    before = reactions(ep,level(),bs)
    with localcontext() as ctx:
        ctx.prec = 4
        after = reactions(ep,level(),bs)
    assert before == after
    with pytest.raises(ValueError,match="float"):
        Level(**{**level().model_dump(),"price":100.0})


def test_no_network_execution_imports_or_shared_file_edits():
    import ast
    from pathlib import Path
    root = Path("src/spy_research/key_level_reactions")
    forbidden = ("spy_research.paper","spy_research.live","spy_research.execution","spy_research.replay","httpx","requests","socket","urllib")
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            modules = [a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ""] if isinstance(node,ast.ImportFrom) else []
            assert not any(m.startswith(forbidden) for m in modules), path


def test_partition_ownership_preserved():
    class Store:
        def load_partition(self,day):
            return (bar(T.replace(day=6)),)
    with pytest.raises(ValueError,match="partition date mismatch"):
        load_local(Store(),context_start=date(2026,1,5),outcome_start=date(2026,1,5),end=date(2026,1,5))


def test_report_denominators_and_undefined_bootstrap():
    data = validate_bars(session(),date(2026,1,5),date(2026,1,5),date(2026,1,5))
    result = build_report(data)
    from spy_research.key_level_reactions.reporting import Report
    for summary in result.family_summaries:
        assert sum(n for _,n in summary.status_counts) == summary.episodes
        if summary.family == "ORH5":
            assert summary.available_level_minutes == 385
    pm = next(x for x in result.session_uncertainty if x.family == "PMH")
    assert pm.undefined_draws == pm.draws
    assert all(lo is None and hi is None for _,lo,hi in pm.intervals)
    with pytest.raises(ValueError,match="reaction panel"):
        Report(**{**result.model_dump(),"reactions":result.reactions[:-1]})


def test_synthetic_service_has_no_network_or_partition_reads(monkeypatch):
    import socket
    from spy_research.data.raw_store import RawBarStore
    def forbidden(*args,**kwargs):
        pytest.fail("Synthetic service must not read partitions or use network")
    monkeypatch.setattr(socket,"create_connection",forbidden)
    monkeypatch.setattr(RawBarStore,"load_partition",forbidden)
    data = validate_bars(session(),date(2026,1,5),date(2026,1,5),date(2026,1,5))
    assert build_report(data).version == "key-level-reactions-v1"


def test_prospective_guard_and_freeze_unchanged():
    from spy_research.break_hold.prospective_freeze import verify_freeze
    assert len(verify_freeze()["frozen_files"]) == 174


def test_two_touch_runs_create_second_episode_only_after_separation():
    bs = tuple(bar(T+timedelta(minutes=i),h="99.95" if i == 30 else "100") for i in range(35))
    ledger = build_ledger(bs,Registry((level(),)))
    assert len(ledger.episodes) == 2
    assert ledger.episodes[1].start == T+timedelta(minutes=31)
    assert ledger.episodes[0].end <= ledger.episodes[1].start


def test_no_retired_swing_on_price_breach():
    bs = episode_bars({0:dict(h="102",c="101"),1:dict(h="102",c="101")})
    x = level()
    reg = Registry((x,))
    ts = build_ledger(bs,reg).touches
    assert ts[-1].prior_price_breached and x in reg.at(bs[-1].timestamp)
