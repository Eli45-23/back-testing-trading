"""Frozen 21-model event-level exit study, independent of Stage 14 execution."""
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from decimal import Decimal as D, localcontext
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean,median

from spy_research.break_hold.entry_timing_analysis import SessionBootstrap,verify_canonical
from spy_research.break_hold.first_hold_quality_service import CANONICAL_SHA
from spy_research.break_hold.service import BreakHoldReport
from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.market import XNYSCalendar,MarketSessionClassifier
from spy_research.strategy.comparisons.market_structure import detect_confirmed_swings

TARGETS=tuple(map(D,('1','1.5','2','2.5','3')))
VARIANTS=tuple(dict(name=f'{stop}_TARGET_{r}R',stop=stop,target=r,rule='FIXED')
    for stop in ('USD025','USD030','ATR050') for r in TARGETS)+(
    dict(name='USD030_RECLAIM',stop='USD030',target=None,rule='RECLAIM'),
    *(dict(name=f'USD030_TIME_{n}',stop='USD030',target=None,rule='TIME',minutes=n) for n in (15,30,60)),
    dict(name='USD030_STRUCTURE_TRAIL',stop='USD030',target=None,rule='TRAIL'),
    dict(name='USD030_TARGET_2R_BE1R',stop='USD030',target=D(2),rule='BREAKEVEN'),
)
ANCHOR='USD030_TARGET_2R'


def simulate_exit(signal,entry_price,entry_timestamp,atr14,bars,session,variant,*,reclaim_at=None,swings=()):
    # Preserve the full frozen ATR when multiplying by 0.5 and forming prices.
    # R division may repeat; 80 digits exceeds the source's 50-digit precision.
    with localcontext() as context:
        context.prec=80
        return _simulate_exit(signal,entry_price,entry_timestamp,atr14,bars,session,variant,reclaim_at=reclaim_at,swings=swings)


def _simulate_exit(signal,entry_price,entry_timestamp,atr14,bars,session,variant,*,reclaim_at=None,swings=()):
    """No within-minute favorable ordering. Updates use only already-known facts."""
    risk=D('.25') if variant['stop']=='USD025' else D('.30') if variant['stop']=='USD030' else atr14*D('.5') if atr14 else None
    row=dict(event_id=signal.event_id,session_date=signal.session_date,signal_known_at=signal.timestamp,
        direction=signal.direction,variant=variant['name'],entry_price=entry_price,entry_timestamp=entry_timestamp,
        initial_risk=risk,status=None,reason=None,exit_minute=None,exit_price=None,r=None,r_low=None,r_high=None,
        stop_at_exit=None,target=None,updates=[])
    if entry_price is None or entry_timestamp is None:
        return row|dict(status='UNAVAILABLE_ENTRY')
    if risk is None:
        return row|dict(status='UNAVAILABLE_ATR')
    if risk<=0:raise ValueError('risk must be positive')
    sign=D(1) if signal.direction=='LONG' else D(-1)
    chosen=tuple(b for b in bars if entry_timestamp<=b.timestamp<session.market_close)
    expected=tuple(entry_timestamp+timedelta(minutes=i) for i in range(int((session.market_close-entry_timestamp).total_seconds()//60)))
    if tuple(b.timestamp for b in chosen)!=expected or not chosen or chosen[0].open!=entry_price or entry_timestamp<signal.timestamp:
        raise ValueError('invalid executable entry/path continuity')
    if any(b.symbol!='SPY' or b.feed!='sip' or b.timeframe!='1Min' or b.source!='alpaca' or b.adjustment!='raw' for b in chosen):raise ValueError('wrong raw provenance')
    stop=entry_price-sign*risk
    target=entry_price+sign*risk*variant['target'] if variant['target'] is not None else None
    row['target']=target
    def finish(price,stamp,reason):
        value=sign*(price-entry_price)/risk
        return row|dict(status='RESOLVED',reason=reason,exit_minute=stamp,exit_price=price,r=value,r_low=value,r_high=value,stop_at_exit=stop)
    pending_be=None
    used=set()
    for b in chosen:
        if pending_be is not None and b.timestamp>=pending_be and sign*(entry_price-stop)>0:
            stop=entry_price;row['updates'].append(dict(known_at=pending_be,active_at=b.timestamp,price=stop,kind='BREAKEVEN'))
        if variant['rule']=='TRAIL':
            for i,s in enumerate(swings):
                if i in used or not entry_timestamp<s.pivot_known_at<=b.timestamp or s.session_date!=signal.session_date:continue
                used.add(i)
                if s.swing_type.value!=('LOW' if sign==1 else 'HIGH'):continue
                if sign*(s.swing_price-stop)>0:
                    stop=s.swing_price;row['updates'].append(dict(known_at=s.pivot_known_at,active_at=b.timestamp,price=stop,kind='CONFIRMED_SWING'))
        # The observed open resolves gaps before any uncertain intraminute path.
        if sign*(b.open-stop)<=0:return finish(b.open,b.timestamp,'STOP_GAP')
        if target is not None and sign*(b.open-target)>=0:return finish(target,b.timestamp,'TARGET_GAP')
        if variant['rule']=='RECLAIM' and reclaim_at is not None and b.timestamp>=reclaim_at:
            return finish(b.open,b.timestamp,'RECLAIM_OPEN')
        if variant['rule']=='TIME' and b.timestamp>=entry_timestamp+timedelta(minutes=variant['minutes']):
            return finish(b.open,b.timestamp,'TIME_OPEN')
        stopped=b.low<=stop if sign==1 else b.high>=stop
        targeted=target is not None and (b.high>=target if sign==1 else b.low<=target)
        if stopped and targeted:
            return row|dict(status='AMBIGUOUS_STOP_TARGET',reason='SAME_MINUTE_STOP_TARGET',exit_minute=b.timestamp,
                            r_low=sign*(stop-entry_price)/risk,r_high=sign*(target-entry_price)/risk,stop_at_exit=stop)
        if stopped:return finish(stop,b.timestamp,'STOP_TOUCH')
        if targeted:return finish(target,b.timestamp,'TARGET_TOUCH')
        if variant['rule']=='BREAKEVEN' and pending_be is None and (b.high>=entry_price+risk if sign==1 else b.low<=entry_price-risk):
            pending_be=b.timestamp+timedelta(minutes=1)
    return finish(chosen[-1].close,chosen[-1].timestamp,'EOD_CLOSE')


def drawdown(values):
    total=peak=dd=D(0);streak=max_streak=0
    for v in values:
        total+=v;peak=max(peak,total);dd=max(dd,peak-total)
        streak=streak+1 if v<0 else 0;max_streak=max(max_streak,streak)
    return dd,max_streak


def metrics(rows,scenario='r_low',cost=D(0)):
    usable=sorted([r for r in rows if r[scenario] is not None],key=lambda r:(r['signal_known_at'],r['event_id']))
    values=[r[scenario]-cost/r['initial_risk'] for r in usable]
    dollars=[v*r['initial_risk'] for v,r in zip(values,usable)]
    wins=[v for v in values if v>0];losses=[v for v in values if v<0]
    win_d=[v for v in dollars if v>0];loss_d=[v for v in dollars if v<0]
    session_totals=defaultdict(D)
    for row,v in zip(usable,values):session_totals[row['session_date']]+=v
    dd,streak=drawdown(values)
    return dict(n=len(values),wins=len(wins),losses=len(losses),breakeven_n=sum(v==0 for v in values),
        win_rate=D(len(wins))/len(values) if values else None,
        average_winner_r=mean(wins) if wins else None,average_loser_r=mean(losses) if losses else None,
        average_winner_dollars=mean(win_d) if win_d else None,average_loser_dollars=mean(loss_d) if loss_d else None,
        expectancy_r=mean(values) if values else None,median_r=median(values) if values else None,
        profit_factor=sum(wins)/-sum(losses) if losses else None,no_losses=not losses,
        max_drawdown_r=dd,max_losing_streak=streak,session_sum_drawdown_r=drawdown([v for _,v in sorted(session_totals.items())])[0],
        total_r=sum(values,D(0)),session_n=len(session_totals),cost_dollars_per_share=cost)


def summarize(rows,bootstrap=None):
    lower=metrics(rows);upper=metrics(rows,'r_high');resolved=metrics(rows,'r')
    months=sorted({r['session_date'].strftime('%Y-%m') for r in rows})
    monthly={m:metrics([r for r in rows if r['session_date'].strftime('%Y-%m')==m]) for m in months}
    month_means=[m['expectancy_r'] for m in monthly.values() if m['expectancy_r'] is not None]
    lomo=[metrics([r for r in rows if r['session_date'].strftime('%Y-%m')!=m])['expectancy_r'] for m in months]
    result=dict(membership_n=len(rows),statuses=dict(Counter(r['status'] for r in rows)),reasons=dict(Counter(r['reason'] for r in rows if r['reason'])),
        stop_first=lower,target_first=upper,resolved_only=resolved,monthly=monthly,
        positive_months=sum(v>0 for v in month_means),negative_months=sum(v<0 for v in month_means),
        worst_month=min(month_means) if month_means else None,lomo_min=min((v for v in lomo if v is not None),default=None),
        costs={str(c):metrics(rows,cost=c) for c in (D('.01'),D('.02'))})
    if bootstrap:
        result['uncertainty']={k:bootstrap.interval([(r['session_date'],r[k]) for r in rows if r[k] is not None]) for k in ('r_low','r_high')}
        result['win_rate_uncertainty']=bootstrap.interval([(r['session_date'],int(r['r_low']>0)) for r in rows if r['r_low'] is not None])
    return result


def run_exit_study(progress=print):
    content=Path('reports/break_hold_2026_v1.json').read_bytes()
    if sha256(content).hexdigest()!=CANONICAL_SHA:raise ValueError('frozen canonical changed')
    canonical=BreakHoldReport.model_validate_json(content);verify_canonical(canonical)
    quality=json.loads(Path('reports/break_hold_first_hold_quality_analysis.json').read_text())
    if quality['canonical_sha256']!=CANONICAL_SHA:raise ValueError('reference lineage mismatch')
    refs={o['signal']['event_id']:o for o in quality['executable_outcomes'] if o['signal']['entry_style']=='FIRST_HOLD'}
    features={r['event_id']:r for r in quality['rows']}
    if len(refs)!=733 or set(refs)!=set(features):raise ValueError('First Hold population mismatch')
    config=ResearchConfig.model_validate(json.loads(canonical.effective_config_json)['research'])
    store=RawBarStore(config);calendar=XNYSCalendar();classifier=MarketSessionClassifier(calendar)
    lineage={r['session_date']:r for r in quality['lineage']}
    rows=[]
    for i,facts in enumerate(canonical.sessions):
        session=calendar.session_for_date(facts.session_date)
        path=store.partition_path(facts.session_date)
        if sha256(path.read_bytes()).hexdigest()!=lineage[str(facts.session_date)]['sha256']:raise ValueError('raw lineage changed')
        classified=classifier.classify_many(store.load_partition(facts.session_date))
        raw=tuple(b.bar for b in classified if b.session_type=='RTH')
        swings=detect_confirmed_swings(aggregate_rth_1m_to_5m(classified,session))
        for event in facts.events:
            signal=event.first_hold
            if signal is None:continue
            ref=refs[signal.event_id]
            if ref['signal']!=signal.model_dump(mode='json'):raise ValueError('signal reference changed')
            price=D(ref['entry_price']) if ref['entry_price'] is not None else None
            timestamp=datetime.fromisoformat(ref['entry_timestamp']) if ref['entry_timestamp'] else None
            atr=features[signal.event_id]['numeric']['atr14'];atr=D(atr) if atr is not None else None
            for variant in VARIANTS:
                rows.append(simulate_exit(signal,price,timestamp,atr,raw,session,variant,reclaim_at=event.reclaim_timestamp,swings=swings))
        if i%40==0:progress(f'Exit paths completed for {i+1}/170 sessions')
    days=sorted(s.session_date for s in canonical.sessions);bootstrap=SessionBootstrap(days,10000,20260908)
    by_variant={v['name']:[r for r in rows if r['variant']==v['name']] for v in VARIANTS}
    common=set.intersection(*({r['event_id'] for r in rs if r['r_low'] is not None} for rs in by_variant.values()))
    summaries={}
    anchor={r['event_id']:r for r in by_variant[ANCHOR]}
    for name,rs in by_variant.items():
        summaries[name]=dict(all=summarize(rs,bootstrap),
            directions={d:summarize([r for r in rs if r['direction']==d],bootstrap) for d in ('LONG','SHORT')},
            common_sample=summarize([r for r in rs if r['event_id'] in common],bootstrap),
            delta_vs_anchor=bootstrap.interval([(r['session_date'],r['r_low']-anchor[r['event_id']]['r_low']) for r in rs if r['r_low'] is not None and anchor[r['event_id']]['r_low'] is not None]))
    return dict(version='frozen_first_hold_exit_study_v1',canonical_sha256=CANONICAL_SHA,definition_hash=canonical.definition_hash,
        input_manifest_hash=canonical.input_manifest_hash,variant_count=len(VARIANTS),variants=VARIANTS,
        counts=dict(sessions=170,first_holds=733,available_fixed_entries=727,common_sample=len(common)),
        bootstrap=dict(repetitions=10000,seed=20260908),summaries=summaries,rows=rows)
