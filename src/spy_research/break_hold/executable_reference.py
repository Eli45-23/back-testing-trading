"""Separate entry-inclusive minute-open reference; frozen close V1 is untouched."""
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Literal

from pydantic import AwareDatetime

from spy_research.events.break_and_hold_models import FrozenModel, HoldSignal
from spy_research.outcomes.break_hold_models import ThresholdMeasurement, WindowMeasurement
from spy_research.outcomes.excursions import THRESHOLDS
from spy_research.strategy.entry_reference import select_entry_reference
from spy_research.strategy.models import BaseSetupStatus, SetupDirection, EntryStatus
from spy_research.interactions import LevelType


def signal_adapter(signal: HoldSignal, market_close, level_price=None):
    """Metadata adapter for pure accepted engines, not a new BASE setup."""
    return SimpleNamespace(
        symbol='SPY', setup_identity=signal.event_id, session_date=signal.session_date,
        direction=SetupDirection(signal.direction), status=BaseSetupStatus.CONFIRMED,
        confirmation_bar_timestamp=signal.timestamp-timedelta(minutes=5),
        signal_known_at=signal.timestamp, earliest_entry_timestamp=signal.timestamp,
        same_session_executable=signal.timestamp<market_close,
        level_type=LevelType.ORH5 if signal.direction=='LONG' else LevelType.ORL5,
        level_price=level_price,
    )


class ExecutableHoldOutcome(FrozenModel):
    signal: HoldSignal  # Original signal time/close/context, never overwritten.
    reference_mode: Literal['FIRST_EXECUTABLE_MINUTE_OPEN_V1']='FIRST_EXECUTABLE_MINUTE_OPEN_V1'
    entry_status: str
    entry_timestamp: AwareDatetime | None
    entry_price: Decimal | None
    entry_delay_minutes: int | None
    reclaim_timestamp: AwareDatetime | None
    windows: tuple[WindowMeasurement,...]
    thresholds: tuple[ThresholdMeasurement,...]


def executable_window(signal, entry, bars, end, horizon, market_close):
    start=entry.entry_reference_timestamp
    price=entry.entry_reference_price
    chosen=[b for b in bars if start is not None and start<=b.timestamp and b.timestamp+timedelta(minutes=1)<=min(end,market_close)]
    if not chosen:
        return WindowMeasurement(horizon=horizon,complete=False,observed_minutes=0,
            requested_end=end,observed_end=None,mfe=None,mae=None,directional_return=None,
            mfe_timestamp=None,mae_timestamp=None,minutes_to_mfe=None,minutes_to_mae=None)
    sign=1 if signal.direction=='LONG' else -1
    favorable=lambda b:max(Decimal(0),b.high-price if sign==1 else price-b.low)
    adverse=lambda b:max(Decimal(0),price-b.low if sign==1 else b.high-price)
    best,worst=max(chosen,key=favorable),max(chosen,key=adverse)
    expected=int((end-start).total_seconds()//60)
    return WindowMeasurement(horizon=horizon,complete=end<=market_close and len(chosen)==expected,
        observed_minutes=len(chosen),requested_end=end,observed_end=chosen[-1].timestamp+timedelta(minutes=1),
        mfe=favorable(best),mae=adverse(worst),directional_return=sign*(chosen[-1].close-price),
        mfe_timestamp=best.timestamp,mae_timestamp=worst.timestamp,
        minutes_to_mfe=int((best.timestamp-start).total_seconds()//60),
        minutes_to_mae=int((worst.timestamp-start).total_seconds()//60))


def measure_executable_hold(signal, raw_minutes, session, *, reclaim_timestamp=None):
    if signal.session_date!=session.session_date or not session.market_open<=signal.timestamp<=session.market_close:
        raise ValueError('signal outside its RTH session')
    entry=select_entry_reference(signal_adapter(signal,session.market_close),raw_minutes)
    start=entry.entry_reference_timestamp
    future=[b for b in raw_minutes if start is not None and start<=b.timestamp<session.market_close]
    price=entry.entry_reference_price
    thresholds=[]
    for f,a in THRESHOLDS:
        fav=next((b.timestamp for b in future if (b.high>=price+f if signal.direction=='LONG' else b.low<=price-f)),None)
        adv=next((b.timestamp for b in future if (b.low<=price-a if signal.direction=='LONG' else b.high>=price+a)),None)
        result=('NO_FUTURE_DATA' if not future else 'AMBIGUOUS_SAME_BAR' if fav is not None and fav==adv
                else 'FAVORABLE_FIRST' if fav is not None and (adv is None or fav<adv)
                else 'ADVERSE_FIRST' if adv is not None else 'NEITHER')
        thresholds.append(ThresholdMeasurement(favorable=f,adverse=a,favorable_hit=fav,adverse_hit=adv,result=result))
    anchor=start or signal.timestamp
    ends=[(f'{n}m',anchor+timedelta(minutes=n)) for n in (5,15,30,60)]
    ends += [('EOD',session.market_close),('PRE_RECLAIM',reclaim_timestamp or session.market_close)]
    windows=tuple(executable_window(signal,entry,raw_minutes,end,name,session.market_close) for name,end in ends)
    if entry.entry_status is EntryStatus.AVAILABLE and (start<signal.timestamp or price!=future[0].open):
        raise ValueError('entry reference timing/price mismatch')
    return ExecutableHoldOutcome(signal=signal,entry_status=entry.entry_status.value,
        entry_timestamp=start,entry_price=price,entry_delay_minutes=entry.entry_delay_minutes,
        reclaim_timestamp=reclaim_timestamp,windows=windows,thresholds=tuple(thresholds))
