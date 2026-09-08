"""Independent completed-close directional change, with session-local state."""
from datetime import timedelta
from decimal import localcontext

from .models import Reversal
from .protocol import CONTEXT, DISTANCES, NY, guard_outcomes, minute_sequence, timestamp_id


def detect(bars):
    bars = minute_sequence(bars)
    if not bars:
        return ()
    guard_outcomes(bars[0].timestamp.astimezone(NY).date(), bars[-1].timestamp.astimezone(NY).date())
    from spy_research.market import XNYSCalendar
    calendar = XNYSCalendar()
    for bar in bars:
        session = calendar.session_for_date(bar.timestamp.astimezone(NY).date())
        if not session.is_trading_day or not session.market_open <= bar.timestamp < session.market_close:
            raise ValueError("Reversals require RTH observations")
    if any(a.timestamp >= b.timestamp for a, b in zip(bars, bars[1:])):
        raise ValueError("Unordered reversal input")
    result = []
    with localcontext(CONTEXT):
        for day in sorted({b.timestamp.astimezone(NY).date() for b in bars}):
            source = [b for b in bars if b.timestamp.astimezone(NY).date() == day]
            if any(b.timestamp-a.timestamp != timedelta(minutes=1) for a,b in zip(source,source[1:])):
                raise ValueError("Missing reversal minute")
            for d in DISTANCES:
                high = low = source[0]
                leg = None
                for b in source[1:]:
                    if leg is None:
                        high = b if b.close > high.close else high
                        low = b if b.close < low.close else low
                        if b.close-low.close >= d:
                            leg, high = "UP", b
                        elif high.close-b.close >= d:
                            leg, low = "DOWN", b
                    elif leg == "UP":
                        high = b if b.close > high.close else high
                        if high.close-b.close >= d:
                            result.append(_event(d, "DOWN", high, b.timestamp+timedelta(minutes=1), b.timestamp+timedelta(minutes=1)))
                            leg, low = "DOWN", b
                    else:
                        low = b if b.close < low.close else low
                        if b.close-low.close >= d:
                            result.append(_event(d, "UP", low, b.timestamp+timedelta(minutes=1), b.timestamp+timedelta(minutes=1)))
                            leg, high = "UP", b
                if leg:
                    result.append(_event(d, "DOWN" if leg == "UP" else "UP", high if leg == "UP" else low, None, source[-1].timestamp+timedelta(minutes=1)))
                else:
                    result.append(_event(d, "UNESTABLISHED", source[0], None, source[-1].timestamp+timedelta(minutes=1)))
    return tuple(result)


def _event(distance, direction, turning, known, end):
    return Reversal(id=f"{distance}:{direction}:{timestamp_id(turning.timestamp)}", distance=distance,
        direction=direction, turning_start=turning.timestamp, turning_price=turning.close,
        known_at=known, censored=known is None, observation_end_at=end)
