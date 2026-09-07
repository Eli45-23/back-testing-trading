from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
from spy_research.config import BreakAndHoldConfig
from spy_research.data.schemas import RawBarRecord
from spy_research.events.break_and_hold import detect_break_holds, level_context, time_bucket
from spy_research.events.break_and_hold_models import KnownLevel
from spy_research.market import MarketSessionClassifier, XNYSCalendar
from spy_research.outcomes.excursions import measure_hold, measure_threshold


def fixture(blocks=None, day=date(2026, 8, 19)):
    calendar = XNYSCalendar()
    session = calendar.session_for_date(day)
    raw = []
    for minute in range(int((session.market_close-session.market_open).total_seconds()/60)):
        o, h, l, c = (blocks or {}).get(minute//5, ("100", "100.2", "99.8", "100"))
        if minute < 5:
            o, h, l, c = "100", "101", "99", "100"
        raw.append(RawBarRecord(symbol="SPY", timestamp=session.market_open+timedelta(minutes=minute),
            open=Decimal(o), high=Decimal(h), low=Decimal(l), close=Decimal(c), volume=100, trade_count=5,
            vwap=Decimal(c), source="alpaca", feed="sip", timeframe="1Min", adjustment="raw"))
    bars = aggregate_rth_1m_to_5m(MarketSessionClassifier(calendar).classify_many(raw), session)
    return calendar, session, tuple(raw), bars


@pytest.mark.parametrize("direction,block", [("LONG",("100","102","100","101.5")),("SHORT",("100","100","98","98.5"))])
def test_hold_strong_reclaim_rebreak_and_continuous_sequence(direction, block):
    cal, session, raw, bars = fixture({1:block,2:block,3:block,5:block})
    facts = detect_break_holds(bars,raw,calendar=cal)
    events = [e for e in facts.events if e.direction == direction]
    assert len(events) == 2
    e = events[0]
    assert e.first_break_timestamp == session.market_open+timedelta(minutes=5)
    assert e.first_hold.timestamp == session.market_open+timedelta(minutes=10)
    assert e.strong_hold.timestamp == session.market_open+timedelta(minutes=15)
    assert e.reclaim_timestamp == session.market_open+timedelta(minutes=25)
    assert e.bars_first_to_strong == 1 and e.bars_first_to_reclaim == 3
    assert e.bars_break_to_first_hold == 0


@pytest.mark.parametrize("block,direction", [(("100","102","100","101"),"LONG"),(("100","100","98","99"),"SHORT")])
def test_wick_and_equality_are_preserved_failed_breaks(block,direction):
    cal, _, raw, bars = fixture({1:block})
    e = detect_break_holds(bars,raw,calendar=cal).events[0]
    assert e.direction == direction and e.failed_break
    assert e.first_hold is None and e.failure_timestamp is not None


def test_opening_candle_never_signals():
    cal, _, raw, bars = fixture()
    assert detect_break_holds(bars[:1],raw[:5],calendar=cal).events == ()
    assert detect_break_holds(bars,raw,calendar=cal).events == ()


def test_both_directions_and_unknown_intraminute_order():
    cal, _, raw, bars = fixture({1:("100","102","98","101.5"),3:("100","100","98","98.5")})
    facts = detect_break_holds(bars,raw,calendar=cal)
    assert facts.both_sides_broken and facts.first_boundary == "AMBIGUOUS_SAME_MINUTE"
    assert {e.direction for e in facts.events if e.first_hold} == {"LONG","SHORT"}


def test_prefix_signal_facts_unchanged_by_future_reclaim_or_extreme():
    cal, _, raw, bars = fixture({1:("100","102","100","101.5"),2:("101.5","103","101.3","102"),3:("100","200","1","100")})
    prefix = detect_break_holds(bars[:2],raw[:10],calendar=cal).events[0]
    full = detect_break_holds(bars,raw,calendar=cal).events[0]
    assert prefix.first_hold == full.first_hold
    assert prefix.strong_hold is None and full.strong_hold is not None
    assert prefix.reclaim_timestamp is None and full.reclaim_timestamp is not None


def test_reclaim_prevents_strong_confirmation():
    cal, _, raw, bars = fixture({1:("100","102","100","101.5"),3:("100","102","100","101.5")})
    facts = detect_break_holds(bars,raw,calendar=cal)
    assert facts.events[0].strong_hold is None
    assert facts.events[1].first_hold is not None


def test_mixed_sessions_naive_and_nonconsecutive_rejected():
    cal, _, raw, bars = fixture()
    _, _, raw2, bars2 = fixture(day=date(2026,8,20))
    with pytest.raises(ValueError):
        detect_break_holds(bars[:2]+bars2[:1],raw,calendar=cal)
    with pytest.raises(ValueError):
        detect_break_holds(bars[:2],raw[:10]+raw2[:1],calendar=cal)
    with pytest.raises(ValueError):
        detect_break_holds((bars[0],bars[2]),raw,calendar=cal)
    with pytest.raises(ValidationError):
        RawBarRecord.model_validate(raw[0].model_dump() | {"timestamp":raw[0].timestamp.replace(tzinfo=None)})


def test_early_close_and_eod_unavailable():
    cal, session, raw, bars = fixture({41:("100","102","100","101.5")},date(2026,11,27))
    e = detect_break_holds(bars,raw,calendar=cal).events[0]
    assert session.is_early_close and e.first_hold.timestamp == session.market_close
    result = measure_hold(e,e.first_hold,raw,session)
    assert all(t.result == "NO_FUTURE_DATA" for t in result.thresholds)
    assert all(w.mfe is None for w in result.windows)


@pytest.mark.parametrize("direction,block",[("LONG",("100","102","100","101.5")),("SHORT",("100","100","98","98.5"))])
def test_excursions_long_short_and_presignal_ignored(direction,block):
    cal, session, raw, bars = fixture({1:block})
    e = detect_break_holds(bars,raw,calendar=cal).events[0]
    s = e.first_hold
    result = measure_hold(e,s,raw,session)
    eod = next(w for w in result.windows if w.horizon == "EOD")
    assert eod.mfe == 0
    assert eod.mae == Decimal("1.7")
    assert eod.directional_return == Decimal("-1.5")
    mutated = tuple(b.model_copy(update={"high":Decimal(999),"low":Decimal(1)}) if b.timestamp <= s.timestamp else b for b in raw)
    assert measure_hold(e,s,mutated,session) == result
    assert all(t.favorable_hit is None or t.favorable_hit > s.timestamp for t in result.thresholds)


def test_horizons_and_pre_reclaim_are_distinct():
    cal, session, raw, bars = fixture({1:("100","102","100","101.5"),2:("101.5","103","101.4","102"),3:("102","102","100","100")})
    e = detect_break_holds(bars,raw,calendar=cal).events[0]
    result = measure_hold(e,e.first_hold,raw,session)
    for n in (5,15,30,60):
        w = next(w for w in result.windows if w.horizon == f"{n}m")
        assert w.complete and w.observed_minutes == n-1
        assert w.observed_end == e.first_hold.timestamp+timedelta(minutes=n)
    pre = result.windows[-1]
    assert pre.requested_end == e.reclaim_timestamp and pre.observed_minutes == 9
    assert pre.mfe == Decimal("1.5") and pre.mae == Decimal("1.5")
    assert result.windows[-2].mae == Decimal("1.7")


@pytest.mark.parametrize("direction",["LONG","SHORT"])
@pytest.mark.parametrize("order,expected",[("fav","FAVORABLE_FIRST"),("adv","ADVERSE_FIRST"),("both","AMBIGUOUS_SAME_BAR"),("none","NEITHER")])
def test_threshold_order_and_ambiguity(direction,order,expected):
    cal, _, raw, bars = fixture({1:("100","102","100","101.5")})
    signal = detect_break_holds(bars,raw,calendar=cal).events[0].first_hold.model_copy(update={"direction":direction,"price":Decimal(100)})
    future = []
    for i in range(2):
        fav = order == "both" or (order == "fav" and i == 0) or (order == "adv" and i == 1)
        adv = order == "both" or (order == "adv" and i == 0) or (order == "fav" and i == 1)
        high = Decimal(101) if (fav if direction == "LONG" else adv) else Decimal(100)
        low = Decimal(99) if (adv if direction == "LONG" else fav) else Decimal(100)
        future.append(raw[11+i].model_copy(update={"high":high,"low":low}))
    result = measure_threshold(signal,future,Decimal('.50'),Decimal('.25'))
    assert result.result == expected


def test_level_context_only_known_strict_levels_and_no_fake_values():
    cal, session, _, _ = fixture()
    now = session.market_open+timedelta(minutes=10)
    levels = (KnownLevel(name="PDH",price=Decimal(102),available_at=session.market_open),
              KnownLevel(name="PML",price=Decimal(98),available_at=session.market_open),
              KnownLevel(name="FUTURE",price=Decimal('100.1'),available_at=now+timedelta(minutes=5)))
    long = level_context(levels,Decimal(100),"LONG",now)
    short = level_context(levels,Decimal(100),"SHORT",now)
    assert long['next_level'].name == "PDH" and short['next_level'].name == "PML"
    assert long['distance_above'] == short['distance_below'] == 2
    assert len(long['known_levels']) == 2
    assert level_context((),Decimal(100),"LONG",now)['next_level'] is None
    assert level_context(levels,Decimal(102),"LONG",now)['next_level'] is None


def test_threshold_config_frozen_and_context_bucket_boundaries():
    with pytest.raises(ValidationError):
        BreakAndHoldConfig(strong_hold_confirmation_closes=3)
    _, session, _, _ = fixture()
    assert time_bucket(session.market_open+timedelta(minutes=30)) == "10:00-10:30"


def test_near_close_fixed_windows_incomplete_and_no_afterhours_leak():
    cal, session, raw, bars = fixture({76:("100","102","100","101.5")})
    e = detect_break_holds(bars,raw,calendar=cal).events[0]
    result = measure_hold(e,e.first_hold,raw,session)
    assert result.windows[0].complete
    assert not result.windows[1].complete
    assert result.windows[-2].complete


def test_raw_crossing_evidence_must_reconcile():
    cal, _, raw, bars = fixture({1:("100","102","100","101.5")})
    with pytest.raises(ValueError):
        detect_break_holds(bars[:2],raw[:9],calendar=cal)
    with pytest.raises(ValueError):
        detect_break_holds(bars[:2],tuple(x.model_copy(update={"high":Decimal(500)}) for x in raw),calendar=cal)


def test_opening_timestamp_is_start_levels_available_only_at_completion():
    from spy_research.levels.opening_range import calculate_opening_five_minute_levels
    cal, session, raw, bars = fixture()
    opening = calculate_opening_five_minute_levels(bars[:1],calendar=cal)
    assert bars[0].timestamp == session.market_open
    assert [b.timestamp for b in raw[:5]] == [session.market_open+timedelta(minutes=i) for i in range(5)]
    assert opening.source_timestamp == session.market_open
    assert opening.available_from_timestamp == session.market_open+timedelta(minutes=5)
    level = KnownLevel(name="ORH5",price=opening.orh5,available_at=opening.available_from_timestamp)
    before = level_context((level,),Decimal(100),"LONG",session.market_open+timedelta(minutes=4,seconds=59))
    at_close = level_context((level,),Decimal(100),"LONG",opening.available_from_timestamp)
    assert before['known_levels'] == ()
    assert at_close['known_levels'] == (level,)
    assert detect_break_holds(bars[:1],raw[:5],calendar=cal).events == ()


@pytest.mark.parametrize("confirmation_index",[1,3])
@pytest.mark.parametrize("style",["FIRST_HOLD","STRONG_HOLD"])
def test_completion_not_stored_start_gates_every_outcome_minute(confirmation_index,style):
    from spy_research.outcomes.excursions import measure_window
    block = ("100","102","100","101.5")
    cal, session, raw, bars = fixture({confirmation_index:block,confirmation_index+1:block})
    event = next(e for e in detect_break_holds(bars,raw,calendar=cal).events if e.first_hold is not None)
    signal = event.first_hold if style == "FIRST_HOLD" else event.strong_hold
    index = confirmation_index+(style == "STRONG_HOLD")
    confirming_bar = bars[index]
    expected_close = confirming_bar.timestamp+timedelta(minutes=5)
    assert signal.timestamp == expected_close
    constituents = raw[index*5:index*5+5]
    assert all(confirming_bar.timestamp <= b.timestamp < signal.timestamp for b in constituents)
    # If a consumer accidentally uses the stored start, these extreme inside-bar
    # values become large excursions and false threshold hits.
    original = measure_hold(event,signal,raw,session)
    poisoned = tuple(b.model_copy(update={"high":Decimal(9999),"low":Decimal('.01')})
        if b.timestamp <= signal.timestamp else b for b in raw)
    observed = measure_hold(event,signal,poisoned,session)
    assert observed == original
    inside_only = measure_window(signal,constituents,signal.timestamp+timedelta(minutes=5),"5m",session.market_close)
    assert inside_only.observed_minutes == 0 and inside_only.mfe is None
    for window in observed.windows:
        assert window.mfe_timestamp is None or window.mfe_timestamp > signal.timestamp
        assert window.mae_timestamp is None or window.mae_timestamp > signal.timestamp
    for result in observed.thresholds:
        assert result.favorable_hit is None or result.favorable_hit > signal.timestamp
        assert result.adverse_hit is None or result.adverse_hit > signal.timestamp
