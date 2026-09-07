"""Persist raw OHLC, validate, aggregate, detect, measure, and export two sessions."""
from datetime import date, timedelta
from decimal import Decimal
import json

from spy_research.alpaca.models import StockBar
from spy_research.config import load_research_config
from spy_research.data.coverage import inventory
from spy_research.data.raw_store import RawBarStore
from spy_research.market import XNYSCalendar
from spy_research.break_hold.service import BreakHoldReport, run_break_hold
from spy_research.break_hold.reporting import export_csv, render_report, summary


def test_two_session_complete_chain(tmp_path,monkeypatch):
    import socket
    monkeypatch.setattr(socket,"create_connection",lambda *a,**k: (_ for _ in ()).throw(AssertionError("network forbidden")))
    config = load_research_config()
    store = RawBarStore(config,root=tmp_path)
    calendar = XNYSCalendar()
    blocks = {
        0:("100","101","99","100"),
        1:("100","102","100","100.5"), # failed upside
        2:("100","100","98","99.5"), # failed downside
        3:("100","102","100","101.5"), # first long
        4:("101.5","103","101","102"), # strong plus same-minute threshold ambiguity
        5:("102","102","100","100"), # reclaim
        6:("100","102","100","101.5"), # re-break
        7:("100","100","98","98.5"), # short
        8:("98.5","98.7","97","97.5"), # strong short
    }
    for day in (date(2026,8,19),date(2026,8,20)):
        session = calendar.session_for_date(day)
        raw = []
        for m in range(390):
            o,h,l,c = map(Decimal,blocks.get(m//5,("100","100.1","99.9","100")))
            raw.append(StockBar(symbol="SPY",timestamp=session.market_open+timedelta(minutes=m),open=o,high=h,low=l,close=c,volume=100,trade_count=10,vwap=c))
        store.persist_bars(raw)
    coverage = inventory(config,store,date(2026,8,19),date(2026,8,20))
    assert all(c.raw_status == "VALID" for c in coverage)
    report = run_break_hold(config,store,date(2026,8,19),date(2026,8,20),coverage=coverage)
    assert len(report.sessions) == 2
    events = [e for s in report.sessions for e in s.events]
    assert sum(e.failed_break for e in events) == 4
    assert sum(e.first_hold is not None for e in events) == 6
    assert sum(e.strong_hold is not None for e in events) == 4
    assert all(s.both_sides_broken for s in report.sessions)
    assert any(t.result == "AMBIGUOUS_SAME_BAR" for o in report.outcomes for t in o.thresholds)
    assert len(report.outcomes) == 10
    first_day = next(o for o in report.outcomes if o.signal.session_date == date(2026,8,19))
    assert "PDH" in first_day.signal.context.unavailable_levels
    second_day = next(o for o in report.outcomes if o.signal.session_date == date(2026,8,20))
    assert "PDH" not in second_day.signal.context.unavailable_levels
    assert BreakHoldReport.model_validate_json(report.model_dump_json()) == report
    assert len(export_csv(report).splitlines()) == 11
    text = render_report(report)
    assert "FIRST_HOLD" in text and "STRONG_HOLD" in text
    s = summary(report.outcomes)
    for counts in s['thresholds'].values():
        assert sum(counts.values()) == 10
    again = run_break_hold(config,store,date(2026,8,19),date(2026,8,20),coverage=coverage)
    assert again == report
