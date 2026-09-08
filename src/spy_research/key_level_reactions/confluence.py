"""All eligible identities, never radius-filtered or collapsed."""
from decimal import Decimal, localcontext
from .models import Relationship
from .protocol import CONTEXT
from .interactions import _age
from spy_research.market import XNYSCalendar
from .protocol import NY


def relationships(observation_id, price, at, registry, source_ids=(), atr=None, calendar=None):
    calendar = calendar or XNYSCalendar()
    value, known = atr if atr is not None else (None, None)
    if known is not None and known > at:
        raise ValueError("Future ATR cannot annotate an interaction")
    if value is not None and (not isinstance(value, Decimal) or not value.is_finite() or value < 0):
        raise ValueError("Invalid Decimal ATR")
    if (value is None) != (known is None):
        raise ValueError("ATR requires its availability timestamp")
    result = []
    with localcontext(CONTEXT):
        for level in registry.at(at):
            signed = level.price-price
            distance = abs(signed)
            bucket = "0" if distance == 0 else next((str(x) for x in (Decimal("0.05"), Decimal("0.10"), Decimal("0.25")) if distance <= x), ">0.25")
            result.append(Relationship(observation_id=observation_id, level_id=level.id,
                available_at=level.available_at, signed_distance=signed, absolute_distance=distance,
                bucket=bucket, same_price=distance == 0, shared_source=bool(set(source_ids)&set(level.source_ids)),
                family=level.family, level_age_sessions=_age(level,at.astimezone(NY).date(),calendar),
                atr14=value, atr_known_at=known, distance_atr=None if not value else distance/value,
                atr_status="UNAVAILABLE" if value is None else "ZERO_ATR" if value == 0 else "AVAILABLE"))
    return tuple(result)
