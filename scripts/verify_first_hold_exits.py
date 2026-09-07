"""Independent raw-bar audit of fixed, time and reclaim exits plus all record arithmetic.

Does not call the exit simulator or its metric helpers. No broker/data retrieval.
"""
import json
from collections import Counter,defaultdict
from datetime import datetime
from decimal import Decimal as D, localcontext
from pathlib import Path
from statistics import mean

from spy_research.break_hold.service import BreakHoldReport
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.market import XNYSCalendar


def main():
    with localcontext() as ctx:
        ctx.prec=80
        audit()


def audit():
    report=json.loads(Path('reports/break_hold_exit_study.json').read_text())
    canonical=BreakHoldReport.model_validate_json(Path('reports/break_hold_2026_v1.json').read_text())
    store=RawBarStore(ResearchConfig.model_validate(json.loads(canonical.effective_config_json)['research']))
    events={e.event_id:e for s in canonical.sessions for e in s.events if e.first_hold}
    calendar=XNYSCalendar()
    raw={str(s.session_date):store.load_partition(s.session_date) for s in canonical.sessions}
    assert len(report['rows'])==733*21
    assert len({(r['event_id'],r['variant']) for r in report['rows']})==733*21
    verified=0;available=0;by_variant=defaultdict(list)
    variants={v['name']:v for v in report['variants']}
    for r in report['rows']:
        e=events[r['event_id']];signal=e.first_hold
        assert datetime.fromisoformat(r['signal_known_at'])==signal.timestamp
        assert r['direction']==signal.direction
        by_variant[r['variant']].append(r)
        if r['status']=='UNAVAILABLE_ENTRY':
            assert r['entry_timestamp'] is None and r['r'] is None
            continue
        stamp=datetime.fromisoformat(r['entry_timestamp']);entry=D(r['entry_price'])
        close=calendar.session_for_date(signal.session_date).market_close
        path=[b for b in raw[r['session_date']] if stamp<=b.timestamp<close]
        assert path and path[0].timestamp==stamp==signal.timestamp and path[0].open==entry
        if r['status']=='UNAVAILABLE_ATR':
            assert variants[r['variant']]['stop']=='ATR050' and r['initial_risk'] is None
            continue
        available+=1
        risk=D(r['initial_risk']);sign=D(1 if r['direction']=='LONG' else -1)
        assert risk>0 and datetime.fromisoformat(r['exit_minute'])>=stamp
        if r['r'] is not None:
            assert abs(D(r['r'])-sign*(D(r['exit_price'])-entry)/risk)<D('1e-60')
            assert r['r']==r['r_low']==r['r_high']
        else:
            assert r['status']=='AMBIGUOUS_STOP_TARGET' and r['exit_price'] is None
            assert abs(D(r['r_low'])-sign*(D(r['stop_at_exit'])-entry)/risk)<D('1e-60')
            assert abs(D(r['r_high'])-sign*(D(r['target'])-entry)/risk)<D('1e-60')
        previous=entry-sign*risk
        for u in r['updates']:
            assert stamp<datetime.fromisoformat(u['known_at'])<=datetime.fromisoformat(u['active_at'])<=datetime.fromisoformat(r['exit_minute'])
            assert sign*(D(u['price'])-previous)>0
            previous=D(u['price'])
        variant=variants[r['variant']]
        if variant['rule'] in ('TRAIL','BREAKEVEN'):continue
        stop=entry-sign*risk;target=entry+sign*risk*D(variant['target']) if variant['target'] is not None else None
        expected=None
        for b in path:
            # Directional coordinates give an independent symmetric implementation.
            o=sign*(b.open-entry);adverse=sign*((b.low if sign==1 else b.high)-entry)
            favorable=sign*((b.high if sign==1 else b.low)-entry)
            if o<=-risk:expected=('RESOLVED',b.timestamp,b.open);break
            if target is not None and o>=risk*D(variant['target']):expected=('RESOLVED',b.timestamp,target);break
            scheduled=(variant['rule']=='RECLAIM' and e.reclaim_timestamp is not None and b.timestamp>=e.reclaim_timestamp) or (variant['rule']=='TIME' and (b.timestamp-stamp).total_seconds()>=60*variant['minutes'])
            if scheduled:expected=('RESOLVED',b.timestamp,b.open);break
            hit_stop=adverse<=-risk;hit_target=target is not None and favorable>=risk*D(variant['target'])
            if hit_stop and hit_target:expected=('AMBIGUOUS_STOP_TARGET',b.timestamp,None);break
            if hit_stop or hit_target:expected=('RESOLVED',b.timestamp,stop if hit_stop else target);break
        if expected is None:expected=('RESOLVED',path[-1].timestamp,path[-1].close)
        assert expected==(r['status'],datetime.fromisoformat(r['exit_minute']),D(r['exit_price']) if r['exit_price'] is not None else None),(r['event_id'],r['variant'])
        verified+=1
    for name,rows in by_variant.items():
        m=report['summaries'][name]['all']['stop_first']
        xs=[D(r['r_low']) for r in sorted(rows,key=lambda r:(r['signal_known_at'],r['event_id'])) if r['r_low'] is not None]
        assert len(xs)==m['n']
        assert abs(mean(xs)-D(m['expectancy_r']))<D('1e-24')
        total=peak=dd=D(0);streak=longest=0
        for x in xs:
            total+=x;peak=max(peak,total);dd=max(dd,peak-total)
            streak=streak+1 if x<0 else 0;longest=max(streak,longest)
        assert abs(dd-D(m['max_drawdown_r']))<D('1e-22') and longest==m['max_losing_streak']
        assert sum(x>0 for x in xs)==m['wins']
    print({'records':len(report['rows']),'available_outcome_arithmetic':available,'independent_raw_exit_checks':verified,'metric_groups':len(by_variant),'status':'PASS'})


if __name__=='__main__':main()
