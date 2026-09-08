"""In-memory synthetic-test kernel. No store, network, or historical runner."""
from dataclasses import dataclass
from datetime import timedelta, date
from decimal import Decimal as D, localcontext
from spy_research.indicators.atr import calculate_session_atr
from spy_research.market import XNYSCalendar
from spy_research.rejection_entry_v1.engine import first_executable_minute, validate_bars
from spy_research.rejection_entry_v1.protocol import SignalStatus, NY
from .protocol import MODELS, ENTRIES

@dataclass(frozen=True)
class Outcome:
    interaction_id: str
    session_date: date
    entry_variant: str
    model: str
    status: str
    risk: D | None = None
    low_r: D | None = None
    high_r: D | None = None
    exit_at: object = None
    exit_price_low: D | None = None
    exit_price_high: D | None = None
    be_active_at: object = None

def visible_atr(signal, five_bars):
    """Use the existing daily-reset ATR without recalculation conventions."""
    if signal.signal_known_at is None:
        raise ValueError('signal availability required')
    if any(b.session_date > date(2026,9,4) for b in five_bars):
        raise ValueError('post-cutoff input')
    session = XNYSCalendar().session_for_date(signal.session_date)
    visible = tuple(b for b in five_bars if b.session_date == signal.session_date
                    and b.timestamp + timedelta(minutes=5) <= signal.signal_known_at)
    expected = tuple(session.market_open + timedelta(minutes=5*i) for i in range(len(visible)))
    if tuple(b.timestamp for b in visible) != expected:
        raise ValueError('ATR prefix gap/order')
    last_completed = int((signal.signal_known_at-session.market_open).total_seconds()//300)
    if len(visible) != last_completed:
        raise ValueError('incomplete ATR prefix')
    rows = calculate_session_atr(visible)
    return rows[-1].atr14 if rows else None

def simulate(signal, entry_variant, model, bars, five_bars=()):
    if model not in MODELS or entry_variant not in ENTRIES:
        raise ValueError('unfrozen candidate')
    expected_family = 'IMMEDIATE_CLOSE_BACK' if entry_variant == ENTRIES[0] else 'MOMENTUM_AWAY'
    if signal.entry_family.value != expected_family or (entry_variant == ENTRIES[0] and signal.confirmation_timeframe_minutes != 1):
        raise ValueError('entry identity mismatch')
    if signal.status != SignalStatus.CONFIRMED or signal.approach_side not in ('ABOVE','BELOW'):
        raise ValueError('executable confirmed source required')
    if not date(2026,1,2) <= signal.session_date <= date(2026,9,4):
        raise ValueError('outcome date outside freeze')
    validate_bars(bars)
    if any(b.session_date != signal.session_date for b in bars):
        raise ValueError('mixed-session path')
    session = XNYSCalendar().session_for_date(signal.session_date)
    at, price, status = first_executable_minute(signal, bars, session_close=session.market_close)
    base = dict(interaction_id=signal.interaction_id, session_date=signal.session_date,
                entry_variant=entry_variant, model=model)
    if status != 'AVAILABLE':
        return Outcome(**base, status='UNAVAILABLE_ENTRY')
    if at != signal.executable_entry_timestamp or price != signal.executable_entry_price or at != signal.signal_known_at:
        raise ValueError('frozen executable reference mismatch')
    path = tuple(b for b in bars if at <= b.timestamp < session.market_close)
    expected = tuple(at+timedelta(minutes=i) for i in range(int((session.market_close-at).total_seconds()//60)))
    if not path or tuple(b.timestamp for b in path) != expected:
        return Outcome(**base, status='UNAVAILABLE_PATH')
    with localcontext() as ctx:
        ctx.prec = 80
        stop_name = model.split('_')[0]
        if stop_name == 'ATR050':
            atr = visible_atr(signal, five_bars)
            if atr is None:
                return Outcome(**base, status='UNAVAILABLE_ATR')
            risk = atr * D('.5')
        else:
            risk = {'USD025':D('.25'),'USD030':D('.30'),'USD040':D('.40')}[stop_name]
        if risk <= 0:
            return Outcome(**base, status='INVALID_RISK')
        sign = D(1) if signal.approach_side == 'ABOVE' else D(-1)
        multiple = D(model.split('TARGET_')[1].split('R')[0])
        target = price + sign*risk*multiple
        stop = price-sign*risk
        pending = None
        active = None
        def finish(lo, hi, bar, reason):
            return Outcome(**base, status=reason, risk=risk, low_r=sign*(lo-price)/risk,
                           high_r=sign*(hi-price)/risk, exit_at=bar.timestamp,
                           exit_price_low=lo, exit_price_high=hi, be_active_at=active)
        for bar in path:
            if pending is not None and bar.timestamp >= pending:
                stop=price; active=pending
            if sign*(bar.open-stop) <= 0:
                return finish(bar.open,bar.open,bar,'STOP_OPEN')
            if sign*(bar.open-target) >= 0:
                return finish(target,target,bar,'TARGET_OPEN')
            stopped = bar.low <= stop if sign == 1 else bar.high >= stop
            targeted = bar.high >= target if sign == 1 else bar.low <= target
            if stopped and targeted:
                return finish(stop,target,bar,'AMBIGUOUS_STOP_TARGET')
            if stopped:
                return finish(stop,stop,bar,'BREAKEVEN' if active else 'STOP')
            if targeted:
                return finish(target,target,bar,'TARGET')
            if model.endswith('BE1R') and pending is None and (bar.high >= price+risk if sign == 1 else bar.low <= price-risk):
                pending=bar.timestamp+timedelta(minutes=1)
        return finish(path[-1].close,path[-1].close,path[-1],'EOD')

def net_r(outcome, cost=D('0'), sensitivity='stop_first'):
    if not isinstance(cost,D) or cost not in (D('0'),D('.01'),D('.02')):
        raise ValueError('unfrozen/non-Decimal cost')
    if sensitivity not in ('stop_first','target_first'):
        raise ValueError('unknown sensitivity')
    r=outcome.low_r if sensitivity == 'stop_first' else outcome.high_r
    with localcontext() as ctx:
        ctx.prec=80
        return None if r is None else r-cost/outcome.risk

def classification(value):
    return 'UNAVAILABLE' if value is None else 'WIN' if value>0 else 'LOSS' if value<0 else 'ZERO'
