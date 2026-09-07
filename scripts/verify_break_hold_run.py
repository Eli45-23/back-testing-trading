"""Independent raw-price spot/reconciliation checks for a saved break/hold run.

Usage: python scripts/verify_break_hold_run.py reports/break_hold_2026_v1.json
This audit deliberately does not call the production outcome calculators.
"""
import sys
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from spy_research.break_hold.service import BreakHoldReport
from spy_research.config import load_research_config
from spy_research.data.raw_store import RawBarStore
from spy_research.market import XNYSCalendar


def verify(path: Path) -> None:
    report = BreakHoldReport.model_validate_json(path.read_text())
    store = RawBarStore(load_research_config())
    calendar = XNYSCalendar()
    windows_checked = thresholds_checked = 0
    outcomes_by_day = {}
    for outcome in report.outcomes:
        outcomes_by_day.setdefault(outcome.signal.session_date, []).append(outcome)
    for day, outcomes in outcomes_by_day.items():
        session = calendar.session_for_date(day)
        raw = store.load_partition(day)
        for outcome in outcomes:
            signal = outcome.signal
            future = [b for b in raw if signal.timestamp < b.timestamp < session.market_close]
            for window in outcome.windows:
                selected = [b for b in future if b.timestamp+timedelta(minutes=1) <= min(window.requested_end,session.market_close)]
                assert window.observed_minutes == len(selected)
                if not selected:
                    assert window.mfe is None and window.mae is None
                else:
                    hi, lo = max(b.high for b in selected), min(b.low for b in selected)
                    expected = (hi-signal.price,signal.price-lo) if signal.direction == "LONG" else (signal.price-lo,hi-signal.price)
                    assert (window.mfe,window.mae) == tuple(max(Decimal(0),v) for v in expected)
                    expected_return = (selected[-1].close-signal.price)*(1 if signal.direction == "LONG" else -1)
                    assert window.directional_return == expected_return
                windows_checked += 1
            for threshold in outcome.thresholds:
                f, a = [], []
                for b in future:
                    favorable, adverse = ((b.high-signal.price,signal.price-b.low) if signal.direction == "LONG" else (signal.price-b.low,b.high-signal.price))
                    if favorable >= threshold.favorable:
                        f.append(b.timestamp)
                    if adverse >= threshold.adverse:
                        a.append(b.timestamp)
                f_time, a_time = min(f) if f else None, min(a) if a else None
                assert (threshold.favorable_hit,threshold.adverse_hit) == (f_time,a_time)
                expected = "NO_FUTURE_DATA" if not future else "NEITHER"
                if f_time and a_time and f_time == a_time:
                    expected = "AMBIGUOUS_SAME_BAR"
                elif f_time and (a_time is None or f_time < a_time):
                    expected = "FAVORABLE_FIRST"
                elif a_time:
                    expected = "ADVERSE_FIRST"
                assert threshold.result == expected
                thresholds_checked += 1
    assert sum(e.first_hold is not None for s in report.sessions for e in s.events) == sum(o.signal.entry_style == "FIRST_HOLD" for o in report.outcomes)
    assert sum(e.strong_hold is not None for s in report.sessions for e in s.events) == sum(o.signal.entry_style == "STRONG_HOLD" for o in report.outcomes)
    print(f"PASS: {len(report.outcomes)} signals; {windows_checked} windows; {thresholds_checked} threshold results independently reconciled.")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
