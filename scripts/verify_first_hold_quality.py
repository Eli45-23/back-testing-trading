"""Independent raw-minute and canonical-record audit of the saved quality study."""
from collections import Counter
from datetime import datetime,timedelta
from decimal import Decimal as D,localcontext
from hashlib import sha256
import csv
import json
from pathlib import Path
from statistics import mean

from spy_research.break_hold.service import BreakHoldReport
from spy_research.break_hold.first_hold_quality_service import CANONICAL_SHA
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.indicators.ema import EMA_CONTEXT
from spy_research.market import MarketSessionClassifier,XNYSCalendar


def main():
    canonical_path=Path('reports/break_hold_2026_v1.json')
    assert sha256(canonical_path.read_bytes()).hexdigest()==CANONICAL_SHA
    canonical=BreakHoldReport.model_validate_json(canonical_path.read_bytes())
    result=json.loads(Path('reports/break_hold_first_hold_quality_analysis.json').read_text())
    assert result['definition_hash']==canonical.definition_hash
    assert result['input_manifest_hash']==canonical.input_manifest_hash
    signals={(o.signal.event_id,o.signal.entry_style):o.signal for o in canonical.outcomes}
    original_first={o.signal.event_id:o for o in canonical.outcomes if o.signal.entry_style=='FIRST_HOLD'}
    expected_labels={e.event_id:'EVENTUAL_STRONG' if e.strong_hold else 'NEVER_STRONG'
                     for s in canonical.sessions for e in s.events if e.first_hold}
    rows=result['rows']
    assert len(rows)==len({r['event_id'] for r in rows})==733
    assert Counter(r['label'] for r in rows)==Counter(EVENTUAL_STRONG=524,NEVER_STRONG=209)
    assert all(r['label']==expected_labels[r['event_id']] for r in rows)
    assert len(result['lineage'])==170 and sum(r['rth_minutes'] for r in result['lineage'])==66300
    config=ResearchConfig.model_validate(json.loads(canonical.effective_config_json)['research'])
    store=RawBarStore(config); classifier=MarketSessionClassifier(); calendar=XNYSCalendar()
    raw_by_day={}
    for facts in canonical.sessions:
        partition=store.load_partition(facts.session_date)
        raw_by_day[facts.session_date]=tuple(b.bar for b in classifier.classify_many(partition) if b.session_type=='RTH')
    for r in rows:
        signal=original_first[r['event_id']].signal
        assert datetime.fromisoformat(r['signal_known_at'])==signal.timestamp
        assert datetime.fromisoformat(r['confirmation_bar_timestamp'])+timedelta(minutes=5)==signal.timestamp
        assert datetime.fromisoformat(r['latest_input_known_at'])==signal.timestamp
        raw=raw_by_day[signal.session_date]
        confirming=[b for b in raw if signal.timestamp-timedelta(minutes=5)<=b.timestamp<signal.timestamp]
        assert len(confirming)==5
        hi=max(b.high for b in confirming);lo=min(b.low for b in confirming)
        size=hi-lo;body=confirming[-1].close-confirming[0].open
        assert D(r['numeric']['body_size'])==abs(body)
        assert D(r['numeric']['candle_range'])==size
        assert D(r['numeric']['candle_volume'])==sum(b.volume for b in confirming)
        with localcontext(EMA_CONTEXT):
            assert D(r['numeric']['body_range_ratio'])==abs(body)/size
        opening=raw[:5]
        level=max(b.high for b in opening) if signal.direction=='LONG' else min(b.low for b in opening)
        beyond=(1 if signal.direction=='LONG' else -1)*(signal.price-level)
        assert D(r['numeric']['distance_beyond_level'])==beyond
        assert 'label' not in r['numeric'] and 'label' not in r['categorical']
    entry_prices={}; unavailable=Counter(); audit_n=0
    for o in result['executable_outcomes']:
        signal=signals[(o['signal']['event_id'],o['signal']['entry_style'])]
        assert o['signal']==signal.model_dump(mode='json')
        raw=raw_by_day[signal.session_date]
        eligible=[b for b in raw if b.timestamp>=signal.timestamp]
        if not eligible:
            assert o['entry_price'] is None and o['entry_timestamp'] is None
            assert all(t['result']=='NO_FUTURE_DATA' for t in o['thresholds'])
            unavailable[signal.entry_style]+=1
            continue
        start=eligible[0].timestamp;price=eligible[0].open
        assert datetime.fromisoformat(o['entry_timestamp'])==start and D(o['entry_price'])==price
        assert start>=signal.timestamp and o['entry_delay_minutes']==0
        entry_prices[(signal.event_id,signal.entry_style)]=price
        for w in o['windows']:
            end=min(datetime.fromisoformat(w['requested_end']),calendar.session_for_date(signal.session_date).market_close)
            selected=[b for b in eligible if b.timestamp+timedelta(minutes=1)<=end]
            assert len(selected)==w['observed_minutes']
            if not selected:
                assert w['mfe'] is None;continue
            if signal.direction=='LONG':
                mfe=max(D(0),max(b.high for b in selected)-price);mae=max(D(0),price-min(b.low for b in selected))
            else:
                mfe=max(D(0),price-min(b.low for b in selected));mae=max(D(0),max(b.high for b in selected)-price)
            assert D(w['mfe'])==mfe and D(w['mae'])==mae
        for t in o['thresholds']:
            fav=D(t['favorable']);adv=D(t['adverse'])
            fs=[b.timestamp for b in eligible if (b.high-price>=fav if signal.direction=='LONG' else price-b.low>=fav)]
            ads=[b.timestamp for b in eligible if (price-b.low>=adv if signal.direction=='LONG' else b.high-price>=adv)]
            f=fs[0] if fs else None;a=ads[0] if ads else None
            expected='AMBIGUOUS_SAME_BAR' if f is not None and f==a else 'FAVORABLE_FIRST' if f is not None and (a is None or f<a) else 'ADVERSE_FIRST' if a is not None else 'NEITHER'
            assert t['result']==expected
            assert (datetime.fromisoformat(t['favorable_hit']) if t['favorable_hit'] else None)==f
            assert (datetime.fromisoformat(t['adverse_hit']) if t['adverse_hit'] else None)==a
        audit_n+=1
    assert unavailable==Counter(FIRST_HOLD=6,STRONG_HOLD=2)
    costs=[(1 if signals[(identity,'STRONG_HOLD')].direction=='LONG' else -1)*(price-entry_prices[(identity,'FIRST_HOLD')])
           for (identity,style),price in entry_prices.items() if style=='STRONG_HOLD']
    assert len(costs)==522 and mean(costs)==D(result['references']['ALL']['executable']['entry_disadvantage']['mean'])
    for direction,s in result['comparisons'].items():
        for name,stats in s['numeric'].items():
            for g in stats['groups'].values():assert g['available_n']+g['unavailable_n']==g['population_n']
        for name,groups in s['categorical'].items():
            assert sum(g['n'] for g in groups.values())==s['n']
            for label in ('EVENTUAL_STRONG','NEVER_STRONG'):
                assert abs(sum(D(g['within_label_percentages'][label]) for g in groups.values())-1)<D('1e-24')
    for mode,directions in result['outcome_quality'].items():
        for direction,s in directions.items():
            for categories in s['categorical'].values():
                for g in categories.values():
                    assert all(sum(t['counts'].values())==g['n'] for t in g['thresholds'].values())
    for name,n in [('features',733),('executable_pairs',524)]:
        with Path(f'reports/break_hold_first_hold_quality_{name}.csv').open() as f: csv_values=list(csv.DictReader(f))
        assert len(csv_values)==len({r['event_id'] for r in csv_values})==n
    print(f'PASS: 733 independently reconstructed candle features; {audit_n} executable paths and all nine thresholds audited against raw minutes; eight unavailable entries retained; 522 paired price differences; full group denominators; CSV populations 733/524.')


if __name__=='__main__':main()
