"""Exact Decimal excursions and conservative OHLC threshold ordering."""
from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal
from spy_research.data.schemas import RawBarRecord
from spy_research.events.break_and_hold_models import BreakHoldEvent, HoldSignal
from spy_research.market import TradingSession

from spy_research.outcomes.break_hold_models import HoldOutcome, ThresholdMeasurement, WindowMeasurement

THRESHOLDS = tuple((Decimal(f), Decimal(a)) for f, a in (
    (".25", ".25"), (".50", ".25"), (".75", ".25"), ("1.00", ".25"),
    (".50", ".30"), (".75", ".30"), ("1.00", ".30"), ("1.50", ".30"), ("2.00", ".30")))


def measure_window(signal: HoldSignal, bars: Sequence[RawBarRecord], end: datetime,
                   horizon: str, market_close: datetime) -> WindowMeasurement:
    chosen = [b for b in bars if signal.timestamp < b.timestamp and b.timestamp + timedelta(minutes=1) <= min(end, market_close)]
    sign = Decimal(1) if signal.direction == "LONG" else Decimal(-1)
    if not chosen:
        return WindowMeasurement(horizon=horizon, complete=False, observed_minutes=0,
            requested_end=end, observed_end=None, mfe=None, mae=None, directional_return=None,
            mfe_timestamp=None, mae_timestamp=None, minutes_to_mfe=None, minutes_to_mae=None)
    favorable = lambda b: max(Decimal(0), (b.high-signal.price) if sign == 1 else (signal.price-b.low))
    adverse = lambda b: max(Decimal(0), (signal.price-b.low) if sign == 1 else (b.high-signal.price))
    best, worst = max(chosen, key=favorable), max(chosen, key=adverse)
    expected = max(0, int((end-signal.timestamp).total_seconds()/60)-1)
    complete = end <= market_close and len(chosen) == expected
    return WindowMeasurement(horizon=horizon, complete=complete, observed_minutes=len(chosen),
        requested_end=end, observed_end=chosen[-1].timestamp+timedelta(minutes=1),
        mfe=favorable(best), mae=adverse(worst), directional_return=sign*(chosen[-1].close-signal.price),
        mfe_timestamp=best.timestamp, mae_timestamp=worst.timestamp,
        minutes_to_mfe=int((best.timestamp-signal.timestamp).total_seconds()/60),
        minutes_to_mae=int((worst.timestamp-signal.timestamp).total_seconds()/60))


def measure_threshold(signal: HoldSignal, bars: Sequence[RawBarRecord], favorable: Decimal,
                      adverse: Decimal) -> ThresholdMeasurement:
    future = [b for b in bars if b.timestamp > signal.timestamp]
    fav = next((b.timestamp for b in future if (b.high >= signal.price+favorable if signal.direction == "LONG" else b.low <= signal.price-favorable)), None)
    adv = next((b.timestamp for b in future if (b.low <= signal.price-adverse if signal.direction == "LONG" else b.high >= signal.price+adverse)), None)
    if not future:
        result = "NO_FUTURE_DATA"
    elif fav is not None and fav == adv:
        result = "AMBIGUOUS_SAME_BAR"
    elif fav is not None and (adv is None or fav < adv):
        result = "FAVORABLE_FIRST"
    elif adv is not None:
        result = "ADVERSE_FIRST"
    else:
        result = "NEITHER"
    return ThresholdMeasurement(favorable=favorable, adverse=adverse, favorable_hit=fav, adverse_hit=adv, result=result)


def measure_hold(event: BreakHoldEvent, signal: HoldSignal,
                 raw_minutes: Sequence[RawBarRecord], session: TradingSession) -> HoldOutcome:
    if signal.timestamp.utcoffset() is None or signal.session_date != session.session_date:
        raise ValueError("outcome signal must match the aware XNYS session")
    if not session.market_open <= signal.timestamp <= session.market_close:
        raise ValueError("signal outside RTH")
    stamps = [b.timestamp for b in raw_minutes]
    if stamps != sorted(set(stamps)):
        raise ValueError("outcomes require chronological unique minutes")
    bars = [b for b in raw_minutes if session.market_open <= b.timestamp < session.market_close]
    if any(b.timestamp.date() != session.market_open.date() for b in raw_minutes):
        raise ValueError("outcomes cannot mix sessions")
    windows = [measure_window(signal, bars, signal.timestamp+timedelta(minutes=n), f"{n}m", session.market_close) for n in (5, 15, 30, 60)]
    windows.append(measure_window(signal, bars, session.market_close, "EOD", session.market_close))
    windows.append(measure_window(signal, bars, event.reclaim_timestamp or session.market_close, "PRE_RECLAIM", session.market_close))
    return HoldOutcome(signal=signal, orh5=event.orh5, orl5=event.orl5,
        reclaim_timestamp=event.reclaim_timestamp, windows=tuple(windows),
        thresholds=tuple(measure_threshold(signal, bars, f, a) for f, a in THRESHOLDS))
