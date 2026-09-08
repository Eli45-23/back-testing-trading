from datetime import datetime, timedelta
from decimal import Decimal as D
from zoneinfo import ZoneInfo
import pytest
from spy_research.rejection_entry_v1.models import EntrySignal, MinuteBar
from spy_research.rejection_entry_v1.protocol import EntryFamily, SignalStatus
from spy_research.rejection_risk_exit_v1.engine import simulate, net_r, classification
from spy_research.rejection_risk_exit_v1.protocol import MODELS

T = datetime(2026,1,2,15,57,tzinfo=ZoneInfo('America/New_York'))

def signal(side='ABOVE'):
    return EntrySignal(interaction_id='synthetic', session_date=T.date(), level_id='x',
        level_family='PDH', level_price=D('100'), approach_side=side,
        entry_family=EntryFamily.IMMEDIATE_CLOSE_BACK, status=SignalStatus.CONFIRMED,
        first_touch_at=T-timedelta(minutes=1), confirmation_start_at=T-timedelta(minutes=1),
        signal_known_at=T, confirmation_timeframe_minutes=1,
        executable_entry_timestamp=T, executable_entry_price=D('100'))

def bar(i, high='100.1', low='99.9', close='100', open='100'):
    return MinuteBar(timestamp=T+timedelta(minutes=i), session_date=T.date(),
        open=D(open),high=D(high),low=D(low),close=D(close))

def run(model='USD025_TARGET_2R', bars=None, side='ABOVE'):
    return simulate(signal(side),'IMMEDIATE_CLOSE_BACK_1M',model,
                    tuple(bars or [bar(i) for i in range(3)]))

@pytest.mark.parametrize('stop,risk',[('USD025','.25'),('USD030','.30'),('USD040','.40')])
def test_fixed_stops(stop,risk):
    x=run(stop+'_TARGET_2R'); assert x.risk==D(risk) and x.status=='EOD'

def test_atr_unavailable():
    # Missing required prefix fails closed, not an invented fixed fallback.
    with pytest.raises(ValueError,match='prefix'):
        run('ATR050_TARGET_1R')

@pytest.mark.parametrize('side,high,low',[('ABOVE','100.5','99.9'),('BELOW','100.1','99.5')])
def test_target_first(side,high,low):
    x=run(bars=[bar(0,high,low),bar(1,low='99'),bar(2)],side=side)
    assert x.status=='TARGET' and x.low_r==2

def test_stop_first():
    x=run(bars=[bar(0,low='99.75'),bar(1,high='101'),bar(2)])
    assert x.status=='STOP' and x.low_r==-1

def test_ambiguity():
    x=run(bars=[bar(0,high='100.5',low='99.75'),bar(1),bar(2)])
    assert x.status=='AMBIGUOUS_STOP_TARGET' and (x.low_r,x.high_r)==(D('-1'),D('2'))

def test_be_subsequent_minute_only():
    x=run('USD025_TARGET_2R_BE1R',[bar(0,high='100.25',low='99.9'),bar(1),bar(2)])
    assert x.exit_at==T+timedelta(minutes=1) and x.low_r==0
    assert x.be_active_at==x.exit_at and classification(x.low_r)=='ZERO'
    assert net_r(x,D('.01'))==D('-.04')

def test_original_stop_during_be_activation_minute():
    x=run('USD025_TARGET_2R_BE1R',[bar(0,high='100.25',low='99.75'),bar(1),bar(2)])
    assert x.low_r==-1 and x.be_active_at is None

def test_gap_and_limit():
    x=run(bars=[bar(0),bar(1,high='99.6',low='99.4',open='99.5',close='99.5'),bar(2)])
    assert x.low_r==-2
    y=run(bars=[bar(0),bar(1,high='101.1',low='100.9',open='101',close='101'),bar(2)])
    assert y.low_r==2

def test_eod_exact_decimal():
    x=run(bars=[bar(0),bar(1),bar(2,close='100.01')])
    assert x.status=='EOD' and x.low_r==D('.04')

def test_missing_path():
    assert run(bars=[bar(0),bar(2)]).status=='UNAVAILABLE_PATH'

def test_entry_timing_unchanged():
    s=signal().model_copy(update={'executable_entry_timestamp':T-timedelta(minutes=1)})
    with pytest.raises(ValueError,match='reference'):
        simulate(s,'IMMEDIATE_CLOSE_BACK_1M',MODELS[0],tuple(bar(i) for i in range(3)))

def test_no_post_cutoff():
    with pytest.raises(ValueError):
        bar(0).model_validate(dict(timestamp=datetime(2026,9,8,10,tzinfo=T.tzinfo),
            session_date=datetime(2026,9,8).date(),open=D(100),high=D(101),low=D(99),close=D(100)))

def test_no_float():
    with pytest.raises(ValueError):
        MinuteBar(timestamp=T,session_date=T.date(),open=100.0,high=D(101),low=D(99),close=D(100))
    with pytest.raises(ValueError): net_r(run(),.01)

def test_matrix():
    assert len(MODELS)==16 and len(set(MODELS))==16

def five_prefix(n):
    from spy_research.bars.models import FiveMinuteBar
    start=T.replace(hour=9,minute=30)
    return tuple(FiveMinuteBar(symbol='SPY',timestamp=start+timedelta(minutes=5*i),
        session_date=T.date(),open=D(100),high=D('100.5'),low=D('99.5'),close=D(100),
        volume=1,trade_count=1,source='alpaca',feed='sip',timeframe='5Min',
        adjustment='raw',source_bar_count=5) for i in range(n))

def test_atr_completion_and_warmup():
    from spy_research.rejection_risk_exit_v1.engine import visible_atr
    s=signal().model_copy(update={'signal_known_at':T.replace(hour=10,minute=39)})
    assert visible_atr(s,five_prefix(14)) is None
    s=s.model_copy(update={'signal_known_at':T.replace(hour=10,minute=40)})
    assert visible_atr(s,five_prefix(15))==D(1)

def test_atr_unavailable_outcome_and_no_fallback():
    start=T.replace(hour=9,minute=31)
    s=signal().model_copy(update={'signal_known_at':start,'confirmation_start_at':start-timedelta(minutes=1),
        'executable_entry_timestamp':start})
    bars=tuple(bar(0).model_copy(update={'timestamp':start+timedelta(minutes=i)}) for i in range(389))
    assert simulate(s,'IMMEDIATE_CLOSE_BACK_1M','ATR050_TARGET_1R',bars).status=='UNAVAILABLE_ATR'
    assert simulate(s,'IMMEDIATE_CLOSE_BACK_1M','USD030_TARGET_1R',bars).risk==D('.30')

def test_atr_exact_risk():
    x=simulate(signal(),'IMMEDIATE_CLOSE_BACK_1M','ATR050_TARGET_1R',
               tuple(bar(i) for i in range(3)),five_prefix(77))
    assert x.risk==D('.5')

def test_confirming_bar_excluded():
    confirming=bar(-1,high='102',low='98')
    x=run(bars=[confirming,bar(0),bar(1),bar(2)])
    assert x.status=='EOD' and x.low_r==0
