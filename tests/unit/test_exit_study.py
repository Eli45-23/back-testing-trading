from datetime import timedelta
from decimal import Decimal as D
from types import SimpleNamespace as NS

import pytest
from test_break_hold import fixture
from spy_research.break_hold.exit_study import VARIANTS, simulate_exit, drawdown, metrics


def setup(direction='LONG', count=20):
    _, session, raw, _ = fixture()
    raw = tuple(b.model_copy(update=dict(open=D(100), high=D('100.1'), low=D('99.9'), close=D(100))) for b in raw[-count:])
    signal = NS(event_id='test', session_date=session.session_date, timestamp=raw[0].timestamp, direction=direction)
    return signal, session, list(raw)


def run(signal, session, raw, name='USD030_TARGET_2R', **kwargs):
    return simulate_exit(signal, D(100), raw[0].timestamp, D('.8'), raw, session,
                         next(v for v in VARIANTS if v['name']==name), **kwargs)


def change(raw, i, **prices):
    raw[i] = raw[i].model_copy(update={k:D(v) for k,v in prices.items()})


def test_inventory_frozen():
    assert len(VARIANTS)==len({v['name'] for v in VARIANTS})==21
    assert sum(v['rule']=='FIXED' for v in VARIANTS)==15


@pytest.mark.parametrize('direction,field,value', [('LONG','high','100.6'),('SHORT','low','99.4')])
def test_entry_minute_included(direction,field,value):
    s,se,raw=setup(direction);change(raw,0,**{field:value})
    r=run(s,se,raw)
    assert r['r']==2 and r['exit_minute']==s.timestamp


@pytest.mark.parametrize('direction,field,value', [('LONG','low','99.7'),('SHORT','high','100.3')])
def test_stop(direction,field,value):
    s,se,raw=setup(direction);change(raw,0,**{field:value})
    assert run(s,se,raw)['r']==-1


def test_ambiguity_not_guessed():
    s,se,raw=setup();change(raw,0,high='100.6',low='99.7')
    r=run(s,se,raw)
    assert r['r'] is None and r['exit_price'] is None
    assert (r['r_low'],r['r_high'])==(-1,2)


@pytest.mark.parametrize('opening,expected,reason', [('99.4',-2,'STOP_GAP'),('101',2,'TARGET_GAP')])
def test_open_resolves_gap_even_when_both_levels_touched(opening,expected,reason):
    s,se,raw=setup();change(raw,1,open=opening,high='101',low='99.4')
    r=run(s,se,raw)
    assert r['r']==expected and r['reason']==reason


def test_reclaim_only_after_completion():
    s,se,raw=setup();known=raw[5].timestamp
    change(raw,4,close='100.1');change(raw,5,open='100.05',high='102',low='98')
    r=run(s,se,raw,'USD030_RECLAIM',reclaim_at=known)
    assert r['exit_minute']==known and r['exit_price']==D('100.05') and r['reason']=='RECLAIM_OPEN'


def test_time_exit_open_precedes_intraminute():
    s,se,raw=setup();change(raw,15,high='102',low='98')
    r=run(s,se,raw,'USD030_TIME_15')
    assert r['exit_minute']==raw[15].timestamp and r['r']==0


def test_eod_fallback():
    s,se,raw=setup(count=3);change(raw,2,close='100.1')
    r=run(s,se,raw,'USD030_TIME_60')
    assert r['reason']=='EOD_CLOSE' and r['exit_price']==D('100.1')


def test_breakeven_not_retroactive():
    s,se,raw=setup();change(raw,0,high='100.3',low='99.9')
    r=run(s,se,raw,'USD030_TARGET_2R_BE1R')
    assert r['r']==0 and r['exit_minute']==raw[1].timestamp
    assert r['updates'][0]['known_at']==raw[1].timestamp


def test_current_stop_before_be_activation():
    s,se,raw=setup();change(raw,0,high='100.3',low='99.7')
    r=run(s,se,raw,'USD030_TARGET_2R_BE1R')
    assert r['r']==-1 and not r['updates']


@pytest.mark.parametrize('direction,kind,price', [('LONG','LOW','99.95'),('SHORT','HIGH','100.05')])
def test_trail_waits_for_known_at(direction,kind,price):
    s,se,raw=setup(direction)
    swing=NS(session_date=s.session_date,pivot_known_at=raw[3].timestamp,swing_type=NS(value=kind),swing_price=D(price))
    r=run(s,se,raw,'USD030_STRUCTURE_TRAIL',swings=(swing,))
    assert r['exit_minute']==raw[3].timestamp and len(r['updates'])==1
    assert r['stop_at_exit']==D(price)


def test_trail_never_loosens_or_uses_preentry_pivot():
    s,se,raw=setup()
    swings=tuple(NS(session_date=s.session_date,pivot_known_at=t,swing_type=NS(value='LOW'),swing_price=D(p))
                 for t,p in [(s.timestamp,'100.05'),(raw[2].timestamp,'99')])
    r=run(s,se,raw,'USD030_STRUCTURE_TRAIL',swings=swings)
    assert r['reason']=='EOD_CLOSE' and not r['updates']


def test_missing_atr_and_entry_explicit():
    s,se,raw=setup();v=next(v for v in VARIANTS if v['stop']=='ATR050')
    assert simulate_exit(s,D(100),s.timestamp,None,raw,se,v)['status']=='UNAVAILABLE_ATR'
    assert simulate_exit(s,None,None,None,raw,se,v)['status']=='UNAVAILABLE_ENTRY'
    assert simulate_exit(s,D(100),s.timestamp,D('.711331033999984192678'),raw,se,v)['initial_risk']==D('.3556655169999920963390')


@pytest.mark.parametrize('bad', ['missing','duplicate','before_signal'])
def test_path_fails_closed(bad):
    s,se,raw=setup()
    if bad=='missing': del raw[1]
    if bad=='duplicate':raw.insert(1,raw[0])
    if bad=='before_signal':s.timestamp+=timedelta(minutes=1)
    with pytest.raises(ValueError):run(s,se,raw)


def test_future_after_exit_irrelevant():
    s,se,raw=setup();change(raw,0,high='100.6');before=run(s,se,raw)
    change(raw,5,high='999',low='1')
    assert before==run(s,se,raw)


def test_drawdown_zero_resets_losing_streak():
    assert drawdown(list(map(D,['1','-1','-1','0','-1','4'])))==(D(3),2)


def test_metrics_cost_and_no_loss_pf():
    s,se,raw=setup();change(raw,0,high='100.6');r=run(s,se,raw)
    assert metrics([r])['profit_factor'] is None
    assert metrics([r],cost=D('.03'))['expectancy_r']==D('1.9')


def test_full_precision_atr_stop_and_target():
    s,se,raw=setup();v=next(v for v in VARIANTS if v['stop']=='ATR050')
    atr=D('0.71133103399998419267812723114832339521925529165537')
    r=simulate_exit(s,D(100),s.timestamp,atr,raw,se,v)
    assert r['initial_risk']==D('0.355665516999992096339063615574161697609627645827685')
    assert r['target']==D('100.355665516999992096339063615574161697609627645827685')
    assert r['stop_at_exit']==D('99.644334483000007903660936384425838302390372354172315')
