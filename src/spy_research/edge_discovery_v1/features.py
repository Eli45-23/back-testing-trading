"""Frozen feature vocabulary and outcome-blind prefix/baseline contracts."""
from datetime import timedelta

FEATURE_REGISTRY = (
    ('completed_return', (1, 5, 15, 30, 60)),
    ('completed_5m_EMA', (9, 20)),
    ('completed_5m_Wilder_ATR', (14,)),
    ('daily_RTH_VWAP', ()),
    ('distance_to_reference', ('VWAP', 'PRIOR_CLOSE', 'PDH', 'PDL', 'ORH5', 'ORL5')),
    ('prior_session_gap', ()), ('opening_range_width', (5,)),
    ('completed_rolling_high_low', (5, 15, 30, 60)),
    ('realized_volatility', (15, 30, 60)),
    ('relative_volume_prior_completed_minutes', (20,)),
    ('candle_structure', ('range', 'body_range', 'close_location', 'wick_proportions', 'consecutive_close_direction')),
    ('calendar_time', ('month', 'minute_of_session', 'day_of_week', 'early_close')),
    ('causal_reference_event', ('crossing', 'failed_crossing')),
)


def completed_prefix(bars, known_at, minutes):
    if known_at.utcoffset() is None or minutes not in (1, 5): raise ValueError('aware timestamp and native bar duration required')
    stamps = [b.timestamp for b in bars]
    if any(t.utcoffset() is None for t in stamps) or any(a >= b for a, b in zip(stamps, stamps[1:])):
        raise ValueError('bar timestamps must be aware, unique and ordered')
    return tuple(b for b in bars if b.timestamp + timedelta(minutes=minutes) <= known_at)


def baseline_key(month, minute_of_session, direction, availability):
    if direction not in ('LONG', 'SHORT') or minute_of_session < 0: raise ValueError('invalid baseline identity')
    return month, minute_of_session, direction, tuple(sorted(availability))
