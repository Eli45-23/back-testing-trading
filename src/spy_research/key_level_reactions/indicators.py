"""Read-only existing ATR semantics, exposed only at five-minute completion."""
from bisect import bisect_right
from datetime import timedelta

from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
from spy_research.indicators.atr import calculate_session_atr
from spy_research.market import MarketSessionClassifier, XNYSCalendar
from .protocol import NY


class AtrAsOf:
    def __init__(self, bars, calendar=None):
        calendar = calendar or XNYSCalendar()
        classifier = MarketSessionClassifier(calendar)
        grouped = {}
        for b in bars:
            grouped.setdefault(b.timestamp.astimezone(NY).date(), []).append(b)
        self.rows = {}
        for day, source in grouped.items():
            five = aggregate_rth_1m_to_5m(classifier.classify_many(source),calendar.session_for_date(day))
            rows = calculate_session_atr(five)
            self.rows[day] = tuple((r.timestamp+timedelta(minutes=5),r.atr14) for r in rows if r.atr14 is not None)

    def at(self, timestamp):
        rows = self.rows.get(timestamp.astimezone(NY).date(), ())
        index = bisect_right(tuple(t for t,_ in rows),timestamp)-1
        if index < 0:
            return None
        known, value = rows[index]
        return value, known
