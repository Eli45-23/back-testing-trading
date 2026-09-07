"""Analysis of saved V1 records only. No detection, data download, or optimization."""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean, median
from typing import Any

import numpy as np

from spy_research.break_hold.service import BreakHoldReport
from spy_research.break_hold.reporting import quantile
from spy_research.events.break_and_hold import time_bucket
from spy_research.events.break_and_hold_models import BreakHoldEvent
from spy_research.outcomes.break_hold_models import HoldOutcome

EXPECTED_COUNTS = (170, 1435, 733, 524)
REPETITIONS = 10_000
SEED = 20260906
UNCHANGED_TOLERANCE = Decimal("0.01")
STYLES = ("FIRST_HOLD", "STRONG_HOLD")
PRIMARY_PAIR = "0.50/0.25"
THRESHOLD_KEYS = ("0.25/0.25", "0.50/0.25", "0.75/0.25", "1.00/0.25", "0.50/0.30", "0.75/0.30", "1.00/0.30", "1.50/0.30", "2.00/0.30")


def key_threshold(threshold: Any) -> str:
    return f"{threshold.favorable:.2f}/{threshold.adverse:.2f}"


def distribution(values: Sequence[Decimal | int]) -> dict[str, Any]:
    xs = sorted(Decimal(x) for x in values)
    if not xs:
        return dict(n=0, mean=None, median=None, q05=None, q25=None, q75=None, q95=None, trimmed_mean_10pct=None)
    trim = len(xs) // 10
    kept = xs[trim:len(xs)-trim] if trim else xs
    return dict(n=len(xs), mean=mean(xs), median=median(xs), q05=quantile(xs,.05),
        q25=quantile(xs,.25), q75=quantile(xs,.75), q95=quantile(xs,.95), trimmed_mean_10pct=mean(kept))


def rate(numerator: int, denominator: int) -> Decimal | None:
    return Decimal(numerator)/Decimal(denominator) if denominator else None


def window(outcome: HoldOutcome, name: str = "EOD") -> Any:
    return next(w for w in outcome.windows if w.horizon == name)


def verify_canonical(report: BreakHoldReport) -> tuple[dict[str, BreakHoldEvent], dict[tuple[str,str], HoldOutcome]]:
    events = [e for s in report.sessions for e in s.events]
    counts = (len(report.sessions),len(events),sum(o.signal.entry_style == STYLES[0] for o in report.outcomes),sum(o.signal.entry_style == STYLES[1] for o in report.outcomes))
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"STOP: canonical counts {counts} differ from {EXPECTED_COUNTS}")
    if len(report.coverage) != 170 or any(c.raw_status != "VALID" for c in report.coverage):
        raise ValueError("STOP: canonical coverage is incomplete")
    event_map = {e.event_id:e for e in events}
    outcome_map = {(o.signal.event_id,o.signal.entry_style):o for o in report.outcomes}
    if len(event_map) != len(events) or len(outcome_map) != len(report.outcomes):
        raise ValueError("STOP: duplicate canonical identities")
    expected_ids = set()
    for event in events:
        for signal in (event.first_hold,event.strong_hold):
            if signal:
                key = (event.event_id,signal.entry_style)
                expected_ids.add(key)
                if key not in outcome_map or outcome_map[key].signal != signal:
                    raise ValueError("STOP: event/outcome signal mismatch")
        if event.strong_hold and event.first_hold is None:
            raise ValueError("STOP: strong hold lacks paired first hold")
    if set(outcome_map) != expected_ids:
        raise ValueError("STOP: unexpected outcome identity")
    for o in report.outcomes:
        if tuple(key_threshold(t) for t in o.thresholds) != THRESHOLD_KEYS:
            raise ValueError("STOP: threshold definitions differ from V1")
        if any(l.available_at > o.signal.timestamp for l in o.signal.context.known_levels):
            raise ValueError("STOP: future level in context")
    return event_map,outcome_map


def cohort_summary(outcomes: Sequence[HoldOutcome]) -> dict[str, Any]:
    eod = [window(o) for o in outcomes]
    complete = [w for w in eod if w.mfe is not None and w.mae is not None]
    mfe,mae = distribution([w.mfe for w in complete]),distribution([w.mae for w in complete])
    reclaimed = [o for o in outcomes if o.reclaim_timestamp is not None]
    n = len(outcomes)
    thresholds = {}
    for key in THRESHOLD_KEYS:
        measurements = [(o,next(t for t in o.thresholds if key_threshold(t)==key)) for o in outcomes]
        counts = Counter(t.result for _,t in measurements)
        ambiguous = counts["AMBIGUOUS_SAME_BAR"]
        favorable = counts["FAVORABLE_FIRST"]
        thresholds[key] = dict(counts=dict(counts), favorable_rate=rate(favorable,n),
            adverse_rate=rate(counts['ADVERSE_FIRST'],n), ambiguous_rate=rate(ambiguous,n),
            nonambiguous_n=n-ambiguous, favorable_rate_excluding_ambiguity=rate(favorable,n-ambiguous),
            favorable_hit_before_reclaim=sum(o.reclaim_timestamp is not None and t.favorable_hit is not None and t.favorable_hit < o.reclaim_timestamp for o,t in measurements),
            clean_favorable_before_reclaim=sum(t.result == 'FAVORABLE_FIRST' and o.reclaim_timestamp is not None and t.favorable_hit < o.reclaim_timestamp for o,t in measurements))
    contributing_sessions=len({o.signal.session_date for o in outcomes})
    return dict(n=n,sessions=contributing_sessions,small_sample=n<30 or contributing_sessions<10,
        long_n=sum(o.signal.direction=='LONG' for o in outcomes),short_n=sum(o.signal.direction=='SHORT' for o in outcomes),
        eod_available_n=len(complete),eod_unavailable_n=n-len(complete),mfe=mfe,mae=mae,
        ratio_mean_mfe_mae=mfe['mean']/mae['mean'] if mae['mean'] else None,
        ratio_median_mfe_mae=mfe['median']/mae['median'] if mae['median'] else None,
        eod_move=distribution([w.directional_return for w in complete]),
        reclaims=len(reclaimed),reclaim_rate=rate(len(reclaimed),n),
        no_reclaim_by_eod=n-len(reclaimed),
        minutes_to_reclaim=distribution([int((o.reclaim_timestamp-o.signal.timestamp).total_seconds()/60) for o in reclaimed]),
        pre_reclaim_mfe=distribution([window(o,'PRE_RECLAIM').mfe for o in outcomes if window(o,'PRE_RECLAIM').mfe is not None]),
        pre_reclaim_mae=distribution([window(o,'PRE_RECLAIM').mae for o in outcomes if window(o,'PRE_RECLAIM').mae is not None]),
        thresholds=thresholds)


def pair_record(first: HoldOutcome, strong: HoldOutcome) -> dict[str, Any]:
    if (first.signal.event_id,first.signal.direction,first.signal.session_date) != (strong.signal.event_id,strong.signal.direction,strong.signal.session_date):
        raise ValueError("cannot pair different event identities")
    if first.signal.entry_style != 'FIRST_HOLD' or strong.signal.entry_style != 'STRONG_HOLD' or strong.signal.timestamp <= first.signal.timestamp:
        raise ValueError("invalid pair styles or chronology")
    sign=Decimal(1) if first.signal.direction=='LONG' else Decimal(-1)
    f,s=window(first),window(strong)
    available=all(v is not None for v in (f.mfe,s.mfe,f.mae,s.mae,f.directional_return,s.directional_return))
    if first.reclaim_timestamp != strong.reclaim_timestamp:
        raise ValueError("paired sequence reclaim identities differ")
    disadvantage=sign*(strong.signal.price-first.signal.price)
    return dict(event_id=first.signal.event_id,session_date=first.signal.session_date,direction=first.signal.direction,
        first_price=first.signal.price,strong_price=strong.signal.price,raw_price_difference=strong.signal.price-first.signal.price,
        entry_disadvantage=disadvantage,delay_minutes=int((strong.signal.timestamp-first.signal.timestamp).total_seconds()/60),
        entry_comparison='UNCHANGED_WITHIN_ONE_CENT' if abs(disadvantage)<=UNCHANGED_TOLERANCE else ('BETTER' if disadvantage<0 else 'WORSE'),
        first_mfe=f.mfe,strong_mfe=s.mfe,first_mae=f.mae,strong_mae=s.mae,
        first_eod_move=f.directional_return,strong_eod_move=s.directional_return,
        mfe_lost=f.mfe-s.mfe if available else None,mae_improvement=f.mae-s.mae if available else None,
        same_pair_excursions_available=available,
        first_minutes_to_reclaim=int((first.reclaim_timestamp-first.signal.timestamp).total_seconds()/60) if first.reclaim_timestamp else None,
        strong_minutes_to_reclaim=int((strong.reclaim_timestamp-strong.signal.timestamp).total_seconds()/60) if strong.reclaim_timestamp else None,
        first_outcome=first.model_dump(mode='json'),strong_outcome=strong.model_dump(mode='json'))


def paired_summary(pairs: Sequence[dict[str, Any]]) -> dict[str, Any]:
    measured=[p for p in pairs if p['same_pair_excursions_available']]
    n=len(pairs)
    lost=[p for p in measured if p['mfe_lost']>0]
    result=dict(n=n,sessions=len({p['session_date'] for p in pairs}),complete_pair_n=len(measured),unavailable_pair_n=n-len(measured),
        entry_disadvantage=distribution([p['entry_disadvantage'] for p in pairs]),
        delay=distribution([p['delay_minutes'] for p in pairs]),
        better=sum(p['entry_comparison']=='BETTER' for p in pairs),worse=sum(p['entry_comparison']=='WORSE' for p in pairs),
        essentially_unchanged=sum(p['entry_comparison']=='UNCHANGED_WITHIN_ONE_CENT' for p in pairs),exactly_unchanged=sum(p['entry_disadvantage']==0 for p in pairs),
        mfe_lost=distribution([p['mfe_lost'] for p in measured]),mae_improvement=distribution([p['mae_improvement'] for p in measured]),
        excursion_compensation=distribution([p['mae_improvement']-p['mfe_lost'] for p in measured]),
        mfe_lost_positive_n=len(lost),mae_reduction_covers_lost_mfe_n=sum(p['mae_improvement']>=p['mfe_lost'] for p in lost))
    for key in ('first_mfe','strong_mfe','first_mae','strong_mae','first_eod_move','strong_eod_move'):
        result[key]=distribution([p[key] for p in measured])
    for style in ('first','strong'):
        delays=[p[style+'_minutes_to_reclaim'] for p in pairs if p[style+'_minutes_to_reclaim'] is not None]
        result[style+'_reclaims']=len(delays)
        result[style+'_minutes_to_reclaim']=distribution(delays)
        denominator=result[style+'_mae']['mean']
        result[style+'_ratio_mean_mfe_mae']=result[style+'_mfe']['mean']/denominator if denominator else None
    result['thresholds']={}
    for key in THRESHOLD_KEYS:
        transitions=Counter()
        for p in pairs:
            f=next(t for t in p['first_outcome']['thresholds'] if f"{Decimal(t['favorable']):.2f}/{Decimal(t['adverse']):.2f}"==key)
            s=next(t for t in p['strong_outcome']['thresholds'] if f"{Decimal(t['favorable']):.2f}/{Decimal(t['adverse']):.2f}"==key)
            transitions[(f['result'],s['result'])]+=1
        result['thresholds'][key]=dict(first_clean=sum(v for (f,s),v in transitions.items() if f=='FAVORABLE_FIRST'),
            strong_clean=sum(v for (f,s),v in transitions.items() if s=='FAVORABLE_FIRST'),
            lost_clean=sum(v for (f,s),v in transitions.items() if f=='FAVORABLE_FIRST' and s!='FAVORABLE_FIRST'),
            gained_clean=sum(v for (f,s),v in transitions.items() if f!='FAVORABLE_FIRST' and s=='FAVORABLE_FIRST'),
            transitions={f'{f} -> {s}':v for (f,s),v in sorted(transitions.items())})
    return result


class SessionBootstrap:
    """Shared cluster multiplicities for paired event-weighted mean estimates."""
    def __init__(self,sessions: Sequence[date],repetitions: int=REPETITIONS,seed: int=SEED):
        self.sessions=tuple(sessions)
        self.lookup={day:i for i,day in enumerate(sessions)}
        self.weights=np.random.default_rng(seed).multinomial(len(sessions),np.full(len(sessions),1/len(sessions)),size=repetitions)

    def interval(self,observations: Sequence[tuple[date,Decimal|int]]) -> dict[str,Any]:
        sums=np.zeros(len(self.sessions))
        counts=np.zeros(len(self.sessions))
        for day,value in observations:
            sums[self.lookup[day]]+=float(value)
            counts[self.lookup[day]]+=1
        denominators=self.weights@counts
        numerators=self.weights@sums
        estimates=numerators[denominators>0]/denominators[denominators>0]
        if not len(estimates):
            return dict(n=0,mean=None,low=None,high=None,valid_repetitions=0,contributing_sessions=0)
        low,high=np.quantile(estimates,[.025,.975])
        return dict(n=len(observations),mean=float(sums.sum()/counts.sum()),low=float(low),high=float(high),
            valid_repetitions=len(estimates),contributing_sessions=int(np.count_nonzero(counts)))


def paired_uncertainty(pairs: Sequence[dict[str,Any]], bootstrap: SessionBootstrap) -> dict[str,Any]:
    results={}
    for metric in ('entry_disadvantage','mfe_lost','mae_improvement'):
        results[metric]=bootstrap.interval([(p['session_date'],p[metric]) for p in pairs if p[metric] is not None])
    for key in THRESHOLD_KEYS:
        observations=[]
        for p in pairs:
            def clean(which: str) -> int:
                t=next(t for t in p[which]['thresholds'] if f"{Decimal(t['favorable']):.2f}/{Decimal(t['adverse']):.2f}"==key)
                return int(t['result']=='FAVORABLE_FIRST')
            observations.append((p['session_date'],clean('strong_outcome')-clean('first_outcome')))
        results['strong_minus_first_clean_'+key]=bootstrap.interval(observations)
    return results


def failure_summary(events: Sequence[BreakHoldEvent]) -> dict[str,Any]:
    failed=[e for e in events if e.failed_break]
    excess=[e.break_ohlc[1]-e.level_price if e.direction=='LONG' else e.level_price-e.break_ohlc[2] for e in failed]
    return dict(raw_break_n=len(events),failed_n=len(failed),failure_rate=rate(len(failed),len(events)),
        beyond_boundary=distribution(excess),minutes_from_crossing_minute_to_failure_close=distribution([
            int((e.failure_timestamp-e.first_break_timestamp).total_seconds()/60) for e in failed]),
        sessions=len({e.session_date for e in events}))


def outlier_sensitivity(outcomes: Sequence[HoldOutcome]) -> dict[str,Any]:
    totals=defaultdict(Decimal)
    values=[]
    for o in outcomes:
        value=window(o).mfe
        if value is not None:
            totals[o.signal.session_date]+=value
            values.append((o.signal.session_date,value))
    ranked=sorted(totals.items(),key=lambda item:(-item[1],item[0]))
    total=sum(totals.values(),Decimal(0))
    largest=ranked[0][0] if ranked else None
    without=[v for d,v in values if d!=largest]
    return dict(full=distribution([v for _,v in values]),top_sessions=[dict(session_date=d,sum_event_mfe=v,share=v/total if total else None) for d,v in ranked[:5]],
        top_five_share=sum(v for _,v in ranked[:5])/total if total else None,
        sensitivity_excluding_largest_contribution_session=dict(session_date=largest,distribution=distribution(without)))


def analyze(report: BreakHoldReport) -> dict[str,Any]:
    event_map,outcome_map=verify_canonical(report)
    days=sorted(s.session_date for s in report.sessions)
    first=[o for o in report.outcomes if o.signal.entry_style=='FIRST_HOLD']
    strong=[o for o in report.outcomes if o.signal.entry_style=='STRONG_HOLD']
    strong_ids={o.signal.event_id for o in strong}
    never=[o for o in first if o.signal.event_id not in strong_ids]
    paired_first=[o for o in first if o.signal.event_id in strong_ids]
    pairs=[pair_record(outcome_map[(s.signal.event_id,'FIRST_HOLD')],s) for s in strong]
    widths={s.session_date:s.events[0].orh5-s.events[0].orl5 for s in report.sessions if s.events}
    if len(widths)!=len(days):
        raise ValueError('STOP: opening width unavailable for a session; do not silently omit')
    cuts=[quantile(list(widths.values()),p) for p in (.25,.50,.75)]
    width_bucket={d:next((f'Q{i+1}' for i,c in enumerate(cuts) if v<=c),'Q4') for d,v in widths.items()}
    events_by_day={s.session_date:s.events for s in report.sessions}
    def break_rank(o: HoldOutcome) -> str:
        events=events_by_day[o.signal.session_date]
        earliest=min(e.first_break_timestamp for e in events)
        current=event_map[o.signal.event_id]
        if current.first_break_timestamp>earliest:
            return 'LATER_BREAK_ATTEMPT'
        return 'TIED_FIRST_BREAK_MINUTE' if sum(e.first_break_timestamp==earliest for e in events)>1 else 'FIRST_BREAK_ATTEMPT'
    def hold_rank(o: HoldOutcome) -> str:
        events=events_by_day[o.signal.session_date]
        earliest=min(e.first_hold.timestamp for e in events if e.first_hold)
        return 'FIRST_VALID_HOLD_SEQUENCE' if event_map[o.signal.event_id].first_hold.timestamp==earliest else 'LATER_VALID_HOLD_SEQUENCE'
    def opposite(o: HoldOutcome) -> str:
        known=[e.break_known_at for e in events_by_day[o.signal.session_date] if e.direction!=o.signal.direction and e.break_known_at<=o.signal.timestamp]
        if not known:
            return 'NO_OPPOSITE_BREAK_BY_SIGNAL'
        return 'BOTH_BROKEN_BEFORE_SIGNAL_CLOSE' if min(known)<o.signal.timestamp else 'OPPOSITE_FIRST_OBSERVED_THIS_CLOSE'
    factors={
        'direction':lambda o:o.signal.direction,'time_bucket':lambda o:o.signal.context.time_bucket,
        'distance':lambda o:o.signal.context.distance_bucket,'opening_width_quartile':lambda o:width_bucket[o.signal.session_date],
        'break_attempt':break_rank,'valid_hold_rank':hold_rank,'opposite_break_context':opposite,
        'month':lambda o:o.signal.session_date.strftime('%Y-%m'),
    }
    grouped={}
    for name,fn in factors.items():
        grouped[name]={}
        for style,cohort in zip(STYLES,(first,strong)):
            buckets=defaultdict(list)
            for o in cohort:
                buckets[fn(o)].append(o)
            grouped[name][style]={k:cohort_summary(v) for k,v in sorted(buckets.items())}
    monthly_pairs={m:paired_summary([p for p in pairs if p['session_date'].strftime('%Y-%m')==m]) for m in sorted({d.strftime('%Y-%m') for d in days})}
    rolling=[]
    for end_index in range(19,len(days)):
        window_days=set(days[end_index-19:end_index+1])
        rolling.append(dict(start=days[end_index-19],end=days[end_index],sessions=20,
            **{style:cohort_summary([o for o in cohort if o.signal.session_date in window_days]) for style,cohort in zip(STYLES,(first,strong))}))
    bootstrap=SessionBootstrap(days)
    groups_pairs={'ALL':pairs,'LONG':[p for p in pairs if p['direction']=='LONG'],'SHORT':[p for p in pairs if p['direction']=='SHORT']}
    failures={
        'all':failure_summary(list(event_map.values())),
        'direction':{d:failure_summary([e for e in event_map.values() if e.direction==d]) for d in ('LONG','SHORT')},
        'time_bucket':{b:failure_summary([e for e in event_map.values() if time_bucket(e.first_break_timestamp)==b]) for b in sorted({time_bucket(e.first_break_timestamp) for e in event_map.values()})}}
    return dict(version='canonical_v1_entry_timing_analysis_v1',counts=EXPECTED_COUNTS,
        definition_hash=report.definition_hash,input_manifest_hash=report.input_manifest_hash,
        analysis_settings=dict(bootstrap_repetitions=REPETITIONS,seed=SEED,cluster='session',rolling_sessions=20,
            unchanged_entry_tolerance=str(UNCHANGED_TOLERANCE),selected_threshold=PRIMARY_PAIR),
        cohorts={name:cohort_summary(rows) for name,rows in (('ALL_FIRST',first),('ALL_STRONG',strong),('PAIRED_FIRST',paired_first),('NEVER_STRONG',never))},
        never_strong_by_direction={d:cohort_summary([o for o in never if o.signal.direction==d]) for d in ('LONG','SHORT')},
        never_strong_records=[o.model_dump(mode='json') for o in never],
        paired={name:paired_summary(rows) for name,rows in groups_pairs.items()},
        paired_records=pairs,uncertainty={name:paired_uncertainty(rows,bootstrap) for name,rows in groups_pairs.items()},
        groups=grouped,opening_width=dict(cutoffs=cuts,session_n=170,session_counts=dict(Counter(width_bucket.values()))),
        month_sessions=dict(Counter(d.strftime('%Y-%m') for d in days)),monthly_pairs=monthly_pairs,
        failures=failures,rolling=rolling,
        outliers={style:outlier_sensitivity(rows) for style,rows in zip(STYLES,(first,strong))})


def run_saved_analysis(input_path: Path) -> dict[str,Any]:
    content=input_path.read_bytes()
    report=BreakHoldReport.model_validate_json(content)
    result=analyze(report)
    result['canonical_json_sha256']=sha256(content).hexdigest()
    return result


def json_default(value: Any) -> str:
    if isinstance(value,(Decimal,date)):
        return str(value)
    raise TypeError(type(value).__name__)
