"""Causal level construction from validated local history."""
from datetime import timedelta

from spy_research.market import XNYSCalendar
from .historical_inputs import validate_bars
from .higher_timeframes import hours
from .models import AvailabilityIssue, Level, LevelSet, PivotAudit
from .protocol import NY, timestamp_id, guard_dates


def _pair(high_family, low_family, source, available, expires, timeframe="1Min"):
    start = source[0].timestamp
    end = source[-1].timestamp + timedelta(minutes=1)
    ids = tuple(timestamp_id(b.timestamp) for b in source)
    created = available if high_family == "PMH" else end
    return tuple(Level(id=f"{family}:{timestamp_id(available)}", family=family, role=role,
        price=price, source_timeframe=timeframe, source_ids=ids, source_start_at=start,
        source_end_at=end, created_at=created, available_at=available, expires_at=expires)
        for family, role, price in ((high_family, "RESISTANCE", max(b.high for b in source)),
                                   (low_family, "SUPPORT", min(b.low for b in source))))


def swing_levels(hour_bars, calendar=None):
    calendar = calendar or XNYSCalendar()
    hour_bars = tuple(hour_bars)
    for index, bar in enumerate(hour_bars):
        day = bar.start.astimezone(NY).date()
        guard_dates(day, day)
        session = calendar.session_for_date(day)
        if not session.is_trading_day or bar.start < session.market_open or bar.end > session.market_close or (bar.start-session.market_open).total_seconds() % 3600:
            raise ValueError("Not a full RTH aligned hour")
        if index:
            prior = hour_bars[index-1]
            expected = prior.end
            prior_session = calendar.session_for_date(prior.start.astimezone(NY).date())
            if expected+timedelta(hours=1) > prior_session.market_close:
                next_day = prior_session.session_date+timedelta(days=1)
                while not calendar.session_for_date(next_day).is_trading_day:
                    next_day += timedelta(days=1)
                expected = calendar.session_for_date(next_day).market_open
            if bar.start != expected:
                raise ValueError("Missing pivot hour; cannot bridge unobserved history")
    result = []
    if any(a.start >= b.start for a, b in zip(hour_bars, hour_bars[1:])):
        raise ValueError("Unordered pivot bars")
    for i in range(2, len(hour_bars) - 2):
        window = hour_bars[i-2:i+3]
        pivot = hour_bars[i]
        others = (*window[:2], *window[3:])
        for family, role, price, qualifies in (
            ("1H_HIGH", "RESISTANCE", pivot.high, all(pivot.high > b.high for b in others)),
            ("1H_LOW", "SUPPORT", pivot.low, all(pivot.low < b.low for b in others))):
            if qualifies:
                result.append(Level(id=f"{family}:{pivot.id}", family=family, role=role, price=price,
                    source_timeframe="1H_RTH_FULL_BARS", source_ids=tuple(b.id for b in window),
                    source_start_at=window[0].start, source_end_at=window[-1].end,
                    created_at=window[-1].end, available_at=window[-1].end,
                    pivot_bar_start_at=pivot.start))
    return tuple(result)


def generate(data, calendar=None):
    calendar = calendar or XNYSCalendar()
    # Revalidate even manually constructed InputData: completeness is not a flag to trust.
    validate_bars(data.bars, data.context_start, data.outcome_start, data.end, calendar)
    rth = {}
    pm = {}
    for b in data.bars:
        day = b.timestamp.astimezone(NY).date()
        s = calendar.session_for_date(day)
        if s.is_trading_day and s.market_open <= b.timestamp < s.market_close:
            rth.setdefault(day, []).append(b)
        elif s.is_trading_day and b.timestamp < s.market_open and b.timestamp.astimezone(NY).hour >= 4:
            pm.setdefault(day, []).append(b)
    result, issues = [], []
    for day in sorted(rth):
        s = calendar.session_for_date(day)
        previous = day - timedelta(days=1)
        while not calendar.session_for_date(previous).is_trading_day:
            previous -= timedelta(days=1)
        if previous in rth:
            result.extend(_pair("PDH", "PDL", rth[previous], s.market_open, s.market_close))
        else:
            issues.append(AvailabilityIssue(session=day, families=("PDH", "PDL"), reason="MISSING_PRIOR_SESSION_CONTEXT"))
        if day in pm:
            result.extend(_pair("PMH", "PML", pm[day], s.market_open, s.market_close))
            issues.append(AvailabilityIssue(session=day, families=("PMH", "PML"), reason="OBSERVED_PREMARKET_NOT_COMPLETENESS_CERTIFIED"))
        else:
            issues.append(AvailabilityIssue(session=day, families=("PMH", "PML"), reason="NO_PREMARKET_DATA"))
        result.extend(_pair("ORH5", "ORL5", rth[day][:5], s.market_open + timedelta(minutes=5), s.market_close, "5Min"))
        monday = day - timedelta(days=day.weekday())
        # One immutable weekly identity, not a new identity per target day.
        if any(x.family == "PWH" and x.id.endswith(monday.isoformat()) for x in result):
            continue
        prior_days = [monday - timedelta(days=i) for i in range(7, 0, -1)]
        expected = [d for d in prior_days if calendar.session_for_date(d).is_trading_day]
        if expected and all(d in rth for d in expected):
            week_days = [monday + timedelta(days=i) for i in range(7)
                         if calendar.session_for_date(monday + timedelta(days=i)).is_trading_day]
            available = calendar.session_for_date(week_days[0]).market_open
            expires = calendar.session_for_date(week_days[-1]).market_close
            pair = _pair("PWH", "PWL", [b for d in expected for b in rth[d]], available, expires)
            result.extend(x.model_copy(update={"id": f"{x.family}:{monday.isoformat()}"}) for x in pair)
        else:
            issues.append(AvailabilityIssue(session=day, families=("PWH", "PWL"), reason="MISSING_PRIOR_WEEK_CONTEXT"))
    hour_bars = hours(data.bars, calendar)
    result.extend(swing_levels(hour_bars, calendar))
    audits = []
    for i in range(2,len(hour_bars)-2):
        window = hour_bars[i-2:i+3]
        pivot = hour_bars[i]
        for role, attr in (("HIGH","high"),("LOW","low")):
            value = getattr(pivot,attr)
            others = [getattr(b,attr) for b in (*window[:2],*window[3:])]
            strict = all(value > v for v in others) if role == "HIGH" else all(value < v for v in others)
            status = "CONFIRMED" if strict else "EQUAL_EXTREMA" if value in others else "NOT_STRICT_EXTREMUM"
            audits.append(PivotAudit(pivot_start=pivot.start,known_at=window[-1].end,role=role,status=status,
                source_ids=tuple(b.id for b in window)))
    return LevelSet(levels=tuple(sorted(result, key=lambda x: (x.available_at, x.id))), issues=tuple(issues),pivot_audits=tuple(audits))
