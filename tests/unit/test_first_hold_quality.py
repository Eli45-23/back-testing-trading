from datetime import timedelta,date
from decimal import Decimal as D
import inspect

import pytest

from test_break_hold import fixture
from spy_research.events.break_and_hold import detect_break_holds
from spy_research.outcomes.excursions import measure_hold
from spy_research.break_hold.executable_reference import measure_executable_hold
from spy_research.break_hold.first_hold_features import extract_first_hold_features
from spy_research.break_hold.first_hold_quality_analysis import LabelBootstrap,compare_numeric,compare_category,correlation
from spy_research.break_hold.entry_timing_analysis import window


@pytest.fixture
def sample():
    cal,session,raw,bars=fixture({1:('100','102','100','101.5'),2:('101.5','103','101.4','102')})
    event=detect_break_holds(bars,raw,calendar=cal).events[0]
    return session,raw,bars,event


@pytest.mark.parametrize('completion_minutes',[5,10,15,145])
@pytest.mark.parametrize('direction',['LONG','SHORT'])
def test_executable_exact_completion_open_and_entry_minute_included(sample,completion_minutes,direction):
    session,raw,bars,event=sample
    signal=event.first_hold.model_copy(update={'timestamp':session.market_open+timedelta(minutes=completion_minutes),'direction':direction})
    modified=list(raw)
    modified[completion_minutes]=modified[completion_minutes].model_copy(update={'open':D(100),'high':D(105),'low':D(95),'close':D(100)})
    # An extreme inside the confirming candle must never enter the outcome.
    modified[completion_minutes-1]=modified[completion_minutes-1].model_copy(update={'high':D(1000),'low':D(1)})
    o=measure_executable_hold(signal,modified,session)
    assert o.entry_timestamp==signal.timestamp and o.entry_price==100 and o.entry_delay_minutes==0
    assert window(o,'5m').observed_minutes==5 and window(o,'5m').complete
    assert window(o).mfe==window(o).mae==5
    assert all(t.favorable_hit==signal.timestamp and t.adverse_hit==signal.timestamp and t.result=='AMBIGUOUS_SAME_BAR' for t in o.thresholds)
    assert o.signal==signal  # Original close and signal context remain untouched.


def test_reference_uses_open_not_entry_bar_future_close(sample):
    session,raw,bars,event=sample
    signal=event.first_hold
    a=measure_executable_hold(signal,raw,session)
    changed=tuple(b.model_copy(update={'close':D(999),'high':D(999)}) if b.timestamp==signal.timestamp else b for b in raw)
    b=measure_executable_hold(signal,changed,session)
    assert a.entry_price==b.entry_price and a.entry_timestamp==b.entry_timestamp


def test_session_close_unavailable_no_next_session_fallback(sample):
    session,raw,bars,event=sample
    signal=event.first_hold.model_copy(update={'timestamp':session.market_close})
    o=measure_executable_hold(signal,raw,session)
    assert o.entry_price is None and o.entry_timestamp is None
    assert o.entry_status=='ENTRY_UNAVAILABLE_SESSION_END'
    assert all(t.result=='NO_FUTURE_DATA' for t in o.thresholds)
    assert all(w.mfe is None for w in o.windows)


def test_first_validated_later_minute_when_exact_missing(sample):
    session,raw,bars,event=sample
    filtered=tuple(b for b in raw if b.timestamp!=event.first_hold.timestamp)
    o=measure_executable_hold(event.first_hold,filtered,session)
    assert o.entry_timestamp==event.first_hold.timestamp+timedelta(minutes=1)
    assert o.entry_delay_minutes==1


@pytest.mark.parametrize('fault',['duplicate','wrong_feed','wrong_session'])
def test_invalid_entry_provenance_rejected(sample,fault):
    session,raw,bars,event=sample
    if fault=='duplicate': changed=raw[:2]+raw[1:]
    elif fault=='wrong_feed': changed=(raw[0].model_copy(update={'feed':'iex'}),)+raw[1:]
    else: changed=(raw[0].model_copy(update={'timestamp':raw[0].timestamp+timedelta(days=1)}),)+raw[1:]
    with pytest.raises(ValueError):measure_executable_hold(event.first_hold,changed,session)


def test_close_reference_unmodified_and_distinct(sample):
    session,raw,bars,event=sample
    original=measure_hold(event,event.first_hold,raw,session)
    before=original.model_dump_json()
    new=measure_executable_hold(event.first_hold,raw,session,reclaim_timestamp=event.reclaim_timestamp)
    assert new.reference_mode=='FIRST_EXECUTABLE_MINUTE_OPEN_V1'
    assert original.outcome_version=='break_hold_strict_future_minute_v1'
    assert window(original,'5m').observed_minutes==4 and window(new,'5m').observed_minutes==5
    assert original.model_dump_json()==before


def test_future_strong_and_reclaim_candles_cannot_change_features(sample):
    session,raw,bars,event=sample
    signal=event.first_hold
    expected=extract_first_hold_features(signal,bars,session)
    prefix=tuple(b for b in bars if b.timestamp+timedelta(minutes=5)<=signal.timestamp)
    assert extract_first_hold_features(signal,prefix,session)==expected
    changed=tuple(b.model_copy(update={'high':D(999),'low':D(1),'close':D(500),'volume':9999999}) if b.timestamp>=signal.timestamp else b for b in bars)
    assert extract_first_hold_features(signal,changed,session)==expected
    assert expected['latest_input_known_at']==signal.timestamp
    assert 'label' not in expected and 'reclaim' not in expected
    assert list(inspect.signature(extract_first_hold_features).parameters)==['signal','bars','session']


def test_feature_warmup_not_backfilled_from_later_rows(sample):
    session,raw,bars,event=sample
    f=extract_first_hold_features(event.first_hold,bars,session)
    assert f['numeric']['atr14'] is None
    assert f['numeric']['relative_volume_prior_6'] is None
    assert 'UNAVAILABLE' in f['categorical']['ema9_20_alignment']
    assert f['categorical']['stage11_1.regime']=='UNAVAILABLE_CALIBRATION_PROVENANCE'


def test_exact_row_missing_or_unfinished_fails_closed(sample):
    session,raw,bars,event=sample
    with pytest.raises(ValueError,match='confirmation row'):
        extract_first_hold_features(event.first_hold,bars[:1],session)
    offgrid=event.first_hold.model_copy(update={'timestamp':event.first_hold.timestamp-timedelta(minutes=1)})
    with pytest.raises(ValueError,match='confirmation row'):
        extract_first_hold_features(offgrid,bars,session)


def test_relative_volume_excludes_confirmation_and_future(sample):
    session,raw,bars,event=sample
    index=10
    selected=list(bars)
    for i in range(index-6,index): selected[i]=selected[i].model_copy(update={'volume':100})
    selected[index]=selected[index].model_copy(update={'volume':600})
    signal=event.first_hold.model_copy(update={'timestamp':selected[index].timestamp+timedelta(minutes=5),'price':selected[index].close})
    f=extract_first_hold_features(signal,selected,session)
    assert f['numeric']['relative_volume_prior_6']==6


def test_whole_session_label_difference_bootstrap_and_missingness():
    days=[date(2026,1,2),date(2026,1,5)]
    b=LabelBootstrap(days,repetitions=1000,seed=21)
    obs=[(days[0],'EVENTUAL_STRONG',D(2)),(days[0],'NEVER_STRONG',D(1)),(days[1],'EVENTUAL_STRONG',D(12)),(days[1],'NEVER_STRONG',D(11))]
    s=b.difference(obs)
    assert s['mean']==s['low']==s['high']==1  # Labels share each draw, not independent resampling.
    assert s['valid_repetitions']==1000
    assert b.difference(obs[:1])['mean'] is None


def test_descriptive_availability_and_category_denominators():
    rows=[dict(session_date=date(2026,1,2),label=l,numeric={'x':v},categorical={'c':c}) for l,v,c in
          [('EVENTUAL_STRONG',D(2),'A'),('EVENTUAL_STRONG',None,'UNAVAILABLE'),('NEVER_STRONG',D(1),'A')]]
    s=compare_numeric(rows,'x')
    assert s['groups']['EVENTUAL_STRONG']['population_n']==2
    assert s['groups']['EVENTUAL_STRONG']['unavailable_n']==1
    assert s['mean_difference']==1 and s['standardized_mean_difference'] is None
    c=compare_category(rows,'c')
    assert c['A']['eventual_strong_rate']==D('.5')
    assert c['A']['within_label_percentages']['EVENTUAL_STRONG']==D('.5')
    assert sum(x['n'] for x in c.values())==3


def test_spearman_ties_and_constant_features():
    assert correlation([1,1,2,3],[1,1,2,3],rank=True)==pytest.approx(1)
    assert correlation([1,1,1],[1,2,3],rank=True) is None


def test_late_completed_indicator_row_is_prefix_invariant(sample):
    from spy_research.indicators.atr import calculate_session_atr
    session,raw,bars,event=sample
    index=30
    signal=event.first_hold.model_copy(update={'timestamp':bars[index].timestamp+timedelta(minutes=5),'price':bars[index].close})
    original=extract_first_hold_features(signal,bars,session)
    changed=tuple(b.model_copy(update={'high':D(999),'low':D(1),'close':D(800),'volume':9876543}) if i>index else b for i,b in enumerate(bars))
    assert extract_first_hold_features(signal,changed,session)==original
    assert original['numeric']['atr14']==calculate_session_atr(bars[:index+1])[-1].atr14
    assert original['numeric']['atr14'] is not None
    assert original['categorical']['ema9_20_alignment']!='EMA_UNAVAILABLE'
    assert original['visible_bar_n']==31


def test_future_label_changes_cannot_change_signal_feature_vector(sample):
    session,raw,bars,event=sample
    before=extract_first_hold_features(event.first_hold,bars,session)
    relabeled=event.model_copy(update={'strong_hold':None,'reclaim_timestamp':None,'reclaim_close':None,'state':'FIRST_HOLD_CONFIRMED'})
    assert extract_first_hold_features(relabeled.first_hold,bars,session)==before


def test_executable_pair_rejects_mixed_identity(sample):
    from spy_research.break_hold.first_hold_quality_analysis import reference_pair
    session,raw,bars,event=sample
    first=measure_executable_hold(event.first_hold,raw,session)
    strong=measure_executable_hold(event.strong_hold,raw,session)
    bad=strong.model_copy(update={'signal':strong.signal.model_copy(update={'event_id':'different'})})
    with pytest.raises(ValueError,match='identity'):reference_pair(first,bad)
