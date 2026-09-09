"""One-position synthetic execution harness. No historical data loader."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal as D, localcontext
from .protocol import protocol


@dataclass(frozen=True)
class Minute:
    timestamp: datetime
    open: D
    high: D
    low: D
    close: D

    def __post_init__(self):
        if self.timestamp.utcoffset() is None: raise ValueError('aware minute start required')
        if any(not isinstance(x,D) or not x.is_finite() or x<=0 for x in (self.open,self.high,self.low,self.close)): raise ValueError('positive Decimal OHLC required')
        if self.high < max(self.open,self.close,self.low) or self.low > min(self.open,self.close,self.high): raise ValueError('invalid OHLC')


@dataclass(frozen=True)
class Signal:
    identity: str
    known_at: datetime
    direction: str
    atr: D | None = None

    def __post_init__(self):
        if self.known_at.utcoffset() is None or self.direction not in ('LONG','SHORT'): raise ValueError('invalid signal')
        if self.atr is not None and (not isinstance(self.atr,D) or not self.atr.is_finite() or self.atr<=0): raise ValueError('invalid ATR')


def simulate_session(minutes, signals, market_open, market_close, stop_model, exit_model, *, synthetic=False):
    if not synthetic: raise PermissionError('historical execution prohibited in Phase 1')
    with localcontext() as context:
        context.prec=80
        return _simulate(minutes,signals,market_open,market_close,stop_model,exit_model)


def _simulate(minutes,signals,market_open,market_close,stop_model,exit_model):
    p=protocol()
    if stop_model not in p['stops'] or exit_model not in p['exits']: raise ValueError('unapproved model')
    if market_open.utcoffset() is None or market_close.utcoffset() is None or market_close<=market_open: raise ValueError('invalid session')
    expected=tuple(market_open+timedelta(minutes=i) for i in range(int((market_close-market_open).total_seconds()/60)))
    if tuple(m.timestamp for m in minutes)!=expected or not minutes: raise ValueError('complete chronological session required')
    if len({s.identity for s in signals})!=len(signals): raise ValueError('duplicate signal identity')
    if any(not market_open<=s.known_at<=market_close for s in signals): raise ValueError('outside-session signal')
    scheduled={}
    records=[]
    for s in signals:
        stamp=next((m.timestamp for m in minutes if m.timestamp>=s.known_at),None)
        if stamp is None: records.append({'id':s.identity,'status':'UNAVAILABLE_ENTRY'});continue
        scheduled.setdefault(stamp,[]).append(s)
    active=None
    for m in minutes:
        candidates=sorted(scheduled.get(m.timestamp,()),key=lambda x:x.identity)
        if active is not None:
            records.extend({'id':s.identity,'status':'IGNORE_AND_RECORD'} for s in candidates)
        elif len({s.direction for s in candidates})>1:
            records.extend({'id':s.identity,'status':'NO_ENTRY_CONFLICT'} for s in candidates)
        elif candidates:
            s=candidates[0]
            records.extend({'id':x.identity,'status':'SIMULTANEOUS_SAME_DIRECTION_DUPLICATE'} for x in candidates[1:])
            risk=D('.30') if stop_model=='USD030' else D('.50') if stop_model=='USD050' else None if s.atr is None else s.atr*(D('.5') if stop_model=='ATR050' else D(1))
            if risk is None:records.append({'id':s.identity,'status':'UNAVAILABLE_ATR'})
            else:
                sign=D(1) if s.direction=='LONG' else D(-1)
                target_r=D(exit_model.removeprefix('TARGET_').removesuffix('R')) if exit_model.startswith('TARGET_') else None
                active={'id':s.identity,'sign':sign,'entry':m.open,'entry_at':m.timestamp,'known_at':s.known_at,'risk':risk,'stop':m.open-sign*risk,'target':m.open+sign*risk*target_r if target_r is not None else None}
        if active is None:continue
        a=active;sign=a['sign'];price=None;reason=None;upper=None
        if sign*(m.open-a['stop'])<=0:price=m.open;reason='STOP_GAP'
        elif a['target'] is not None and sign*(m.open-a['target'])>=0:price=a['target'];reason='TARGET_GAP'
        elif exit_model.startswith('TIME_') and m.timestamp>=a['entry_at']+timedelta(minutes=int(exit_model.split('_')[1])):price=m.open;reason='TIME_OPEN'
        else:
            stopped=m.low<=a['stop'] if sign==1 else m.high>=a['stop']
            targeted=a['target'] is not None and (m.high>=a['target'] if sign==1 else m.low<=a['target'])
            if stopped and targeted:price=a['stop'];upper=a['target'];reason='AMBIGUOUS_STOP_TARGET'
            elif stopped:price=a['stop'];reason='STOP_TOUCH'
            elif targeted:price=a['target'];reason='TARGET_TOUCH'
        if price is None and m.timestamp==minutes[-1].timestamp:price=m.close;reason='EOD_CLOSE'
        if price is not None:
            low=sign*(price-a['entry'])/a['risk'];high=sign*((upper if upper is not None else price)-a['entry'])/a['risk']
            records.append({**a,'status':reason,'exit_at':m.timestamp,'exit_price':price,'r_low':low,'r_high':high,'win':low>0,'costs':{c:str(low-D(c)/a['risk']) for c in p['costs']}})
            active=None
    return tuple(records)
