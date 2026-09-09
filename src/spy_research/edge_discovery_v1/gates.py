"""Mechanical gates over declared net evidence; never infer missing evidence."""
from dataclasses import dataclass
from decimal import Decimal as D


@dataclass(frozen=True)
class Evidence:
    trades: int
    sessions: int
    net_mean_r: D
    net_pf: D
    active_months: int
    positive_months: int
    net_drawdown_r: D
    net_total_r: D
    top_month_share: D
    top5_session_share: D
    net_lomo_min: D
    direction_unchanged: bool
    adjusted_ci_low: D
    cost: D = D('0.02')

    def __post_init__(self):
        for name in ('net_mean_r', 'net_pf', 'net_drawdown_r', 'net_total_r', 'top_month_share', 'top5_session_share', 'net_lomo_min', 'adjusted_ci_low', 'cost'):
            value = getattr(self, name)
            if not isinstance(value, D) or not value.is_finite(): raise ValueError('finite Decimal evidence required')
        for value in (self.trades, self.sessions, self.active_months, self.positive_months):
            if type(value) is not int or value < 0: raise ValueError('nonnegative count required')
        if self.sessions > self.trades or self.active_months > self.sessions or self.positive_months > self.active_months: raise ValueError('invalid denominators')
        if self.net_drawdown_r < 0 or self.net_pf < 0 or any(not D(0) <= x <= D(1) for x in (self.top_month_share, self.top5_session_share)): raise ValueError('invalid evidence domain')
        if type(self.direction_unchanged) is not bool: raise ValueError('direction evidence required')


def evaluate(e, phase):
    if phase not in ('DISCOVERY', 'VALIDATION', 'INTERNAL_CONFIRMATION'): raise ValueError('invalid phase')
    if e.cost != D('.02'): raise ValueError('gates require $0.02 net evidence')
    n, s = (150, 60) if phase == 'INTERNAL_CONFIRMATION' else (200, 80)
    failures = []
    if e.trades < n or e.sessions < s: failures.append('INSUFFICIENT_SAMPLE')
    rules = {'NET_MEAN': e.net_mean_r >= D('.05'), 'NET_PF': e.net_pf >= D('1.10'), 'MONTHS': e.active_months > 0 and e.positive_months * 3 >= e.active_months * 2, 'DRAWDOWN': e.net_drawdown_r <= 40, 'RECOVERY': e.net_total_r > 0 and e.net_total_r >= e.net_drawdown_r, 'MONTH_CONCENTRATION': e.top_month_share <= D('.35'), 'SESSION_CONCENTRATION': e.top5_session_share <= D('.25'), 'LOMO': e.net_lomo_min > 0, 'DIRECTION': e.direction_unchanged}
    if phase != 'DISCOVERY': rules['ADJUSTED_UNCERTAINTY'] = e.adjusted_ci_low > 0
    failures += [name for name, passed in rules.items() if not passed]
    return {'passed': not failures, 'status': 'INSUFFICIENT' if 'INSUFFICIENT_SAMPLE' in failures else 'PASS' if not failures else 'FAIL', 'failures': failures}
