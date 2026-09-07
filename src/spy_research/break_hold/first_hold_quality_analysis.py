"""Predeclared descriptive label comparisons; no fitting or feature selection."""
from collections import Counter
from decimal import Decimal
from statistics import mean

import numpy as np

from spy_research.break_hold.entry_timing_analysis import (
    SessionBootstrap, distribution, cohort_summary, paired_summary, paired_uncertainty,
    THRESHOLD_KEYS, key_threshold, window, rate,
)

LABELS=('EVENTUAL_STRONG','NEVER_STRONG')
QUALITY_PAIRS=('0.25/0.25','0.50/0.25','0.50/0.30','1.00/0.30')


class LabelBootstrap(SessionBootstrap):
    def difference(self, observations):
        sums=np.zeros((2,len(self.sessions))); counts=np.zeros_like(sums)
        for day,label,value in observations:
            i=LABELS.index(label); j=self.lookup[day]
            sums[i,j]+=float(value); counts[i,j]+=1
        nums=self.weights@sums.T; dens=self.weights@counts.T
        valid=(dens>0).all(axis=1)
        if not valid.any() or not (counts.sum(axis=1)>0).all():
            return dict(mean=None,low=None,high=None,valid_repetitions=0)
        draws=nums[valid,0]/dens[valid,0]-nums[valid,1]/dens[valid,1]
        lo,hi=np.quantile(draws,[.025,.975])
        return dict(mean=float(sums[0].sum()/counts[0].sum()-sums[1].sum()/counts[1].sum()),
                    low=float(lo),high=float(hi),valid_repetitions=int(valid.sum()))


def compare_numeric(rows,name,bootstrap=None):
    groups={label:[r for r in rows if r['label']==label] for label in LABELS}
    available={label:[r['numeric'][name] for r in group if r['numeric'][name] is not None] for label,group in groups.items()}
    summaries={label:dict(population_n=len(groups[label]),available_n=len(xs),unavailable_n=len(groups[label])-len(xs),
                sessions=len({r['session_date'] for r in groups[label]}),
                available_sessions=len({r['session_date'] for r in groups[label] if r['numeric'][name] is not None}),distribution=distribution(xs)) for label,xs in available.items()}
    x,y=available.values()
    delta=mean(x)-mean(y) if x and y else None
    sd=None
    if len(x)>1 and len(y)>1:
        sx,sy=np.asarray(x,dtype=float),np.asarray(y,dtype=float)
        pooled=np.sqrt(((len(x)-1)*sx.var(ddof=1)+(len(y)-1)*sy.var(ddof=1))/(len(x)+len(y)-2))
        sd=float(delta)/pooled if pooled else None
    return dict(groups=summaries,mean_difference=delta,standardized_mean_difference=sd,
        small_sample=any(s['available_n']<30 or s['available_sessions']<10 for s in summaries.values()),
        bootstrap=bootstrap.difference([(r['session_date'],r['label'],r['numeric'][name]) for r in rows if r['numeric'][name] is not None]) if bootstrap else None)


def compare_category(rows,name):
    totals=Counter(r['label'] for r in rows)
    result={}
    for category in sorted({r['categorical'][name] for r in rows}):
        selected=[r for r in rows if r['categorical'][name]==category]
        counts=Counter(r['label'] for r in selected)
        result[category]=dict(n=len(selected),sessions=len({r['session_date'] for r in selected}),
            counts={l:counts[l] for l in LABELS},within_label_percentages={l:rate(counts[l],totals[l]) for l in LABELS},
            eventual_strong_rate=rate(counts[LABELS[0]],len(selected)),
            small_sample=len(selected)<30 or len({r['session_date'] for r in selected})<10,
            availability='UNAVAILABLE_OR_PARTIAL' if 'UNAVAILABLE' in category else 'AVAILABLE')
    return result


def correlation(xs,ys,rank=False):
    if len(xs)<3:
        return None
    def ranks(values):
        arr=np.asarray(values,dtype=float)
        ordered=np.argsort(arr,kind='stable'); out=np.empty(len(arr))
        i=0
        while i<len(arr):
            j=i+1
            while j<len(arr) and arr[ordered[j]]==arr[ordered[i]]: j+=1
            out[ordered[i:j]]=(i+j-1)/2+1; i=j
        return out
    x,y=(ranks(xs),ranks(ys)) if rank else (np.asarray(xs,dtype=float),np.asarray(ys,dtype=float))
    if np.ptp(x)==0 or np.ptp(y)==0: return None
    return float(np.corrcoef(x,y)[0,1])


def numeric_quality(rows,outcomes,name):
    # Future evaluations live here, never in the feature module.
    result={}
    for metric in ('pre_reclaim_mfe','pre_reclaim_mae')+QUALITY_PAIRS:
        xs=[];ys=[];status=Counter()
        for row in rows:
            value=row['numeric'][name]
            if value is None:
                status['FEATURE_UNAVAILABLE']+=1; continue
            o=outcomes[row['event_id']]
            if metric.startswith('pre_'):
                target=getattr(window(o,'PRE_RECLAIM'),metric.rsplit('_',1)[1])
                if target is None:
                    status['OUTCOME_UNAVAILABLE']+=1;continue
            else:
                t=next(t for t in o.thresholds if key_threshold(t)==metric)
                status[t.result]+=1
                if t.result in ('AMBIGUOUS_SAME_BAR','NO_FUTURE_DATA'):continue
                target=int(t.result=='FAVORABLE_FIRST')
            xs.append(value);ys.append(target)
        result[metric]=dict(n=len(xs),excluded_n=len(rows)-len(xs),status_counts=dict(status),
            association=correlation(xs,ys,rank=metric.startswith('pre_')),
            method='SPEARMAN' if metric.startswith('pre_') else 'POINT_BISERIAL_CLEAN_VS_OTHER_EVALUABLE')
    return result


def reference_pair(first,strong):
    if (first.signal.event_id,first.signal.session_date,first.signal.direction)!=(strong.signal.event_id,strong.signal.session_date,strong.signal.direction):
        raise ValueError('executable pair identity mismatch')
    if first.entry_price is None or strong.entry_price is None or strong.entry_timestamp<=first.entry_timestamp:
        raise ValueError('executable pair requires chronological available entries')
    if first.reclaim_timestamp!=strong.reclaim_timestamp:
        raise ValueError('executable pair reclaim mismatch')
    f,s=window(first),window(strong)
    cost=(1 if first.signal.direction=='LONG' else -1)*(strong.entry_price-first.entry_price)
    available=all(v is not None for v in (f.mfe,s.mfe,f.mae,s.mae))
    return dict(event_id=first.signal.event_id,session_date=first.signal.session_date,direction=first.signal.direction,
        first_price=first.entry_price,strong_price=strong.entry_price,entry_disadvantage=cost,
        first_entry_timestamp=first.entry_timestamp,strong_entry_timestamp=strong.entry_timestamp,
        delay_minutes=int((strong.entry_timestamp-first.entry_timestamp).total_seconds()//60),
        entry_comparison='UNCHANGED_WITHIN_ONE_CENT' if abs(cost)<=Decimal('.01') else 'BETTER' if cost<0 else 'WORSE',
        first_mfe=f.mfe,strong_mfe=s.mfe,first_mae=f.mae,strong_mae=s.mae,
        first_eod_move=f.directional_return,strong_eod_move=s.directional_return,
        mfe_lost=f.mfe-s.mfe if available else None,mae_improvement=f.mae-s.mae if available else None,
        same_pair_excursions_available=available,
        first_minutes_to_reclaim=int((first.reclaim_timestamp-first.entry_timestamp).total_seconds()//60) if first.reclaim_timestamp else None,
        strong_minutes_to_reclaim=int((strong.reclaim_timestamp-strong.entry_timestamp).total_seconds()//60) if strong.reclaim_timestamp else None,
        first_outcome=first.model_dump(mode='json'),strong_outcome=strong.model_dump(mode='json'))


def executable_comparison(executable,canonical,days):
    originals={(o.signal.event_id,o.signal.entry_style):o for o in canonical}
    from spy_research.break_hold.entry_timing_analysis import pair_record
    by_id={(o.signal.event_id,o.signal.entry_style):o for o in executable}
    strong=[o for o in executable if o.signal.entry_style=='STRONG_HOLD']
    b=SessionBootstrap(days,repetitions=10000,seed=20260907)
    output={}
    for direction in ('ALL','LONG','SHORT'):
        selected=[o for o in strong if direction=='ALL' or o.signal.direction==direction]
        usable=[o for o in selected if o.entry_price is not None and by_id[(o.signal.event_id,'FIRST_HOLD')].entry_price is not None]
        pairs=[reference_pair(by_id[(s.signal.event_id,'FIRST_HOLD')],s) for s in usable]
        close_pairs=[pair_record(originals[(s.signal.event_id,'FIRST_HOLD')],originals[(s.signal.event_id,'STRONG_HOLD')]) for s in selected]
        common_close=[p for p in close_pairs if p['event_id'] in {s.signal.event_id for s in usable}]
        thresholds={}
        for key in THRESHOLD_KEYS:
            fs=[];ss=[]; observations=[]
            for s in selected:
                f=by_id[(s.signal.event_id,'FIRST_HOLD')]
                ft=next(t for t in f.thresholds if key_threshold(t)==key);st=next(t for t in s.thresholds if key_threshold(t)==key)
                fs.append(ft.result);ss.append(st.result)
                observations.append((s.signal.session_date,int(st.result=='FAVORABLE_FIRST')-int(ft.result=='FAVORABLE_FIRST')))
            thresholds[key]=dict(n=len(selected),first_counts=dict(Counter(fs)),strong_counts=dict(Counter(ss)),
                first_clean_rate=rate(fs.count('FAVORABLE_FIRST'),len(selected)),strong_clean_rate=rate(ss.count('FAVORABLE_FIRST'),len(selected)),
                bootstrap=b.interval(observations))
        output[direction]=dict(total_pairs=len(selected),available_entry_pairs=len(pairs),unavailable_entry_pairs=len(selected)-len(pairs),
            executable=paired_summary(pairs),close_all=paired_summary(close_pairs),close_common=paired_summary(common_close),
            uncertainty=paired_uncertainty(pairs,b),all_pair_thresholds=thresholds,pairs=pairs)
    return output


def analyze_features(features,labels,close_first,executable_first,days):
    if len(features)!=733 or len({f['event_id'] for f in features})!=733 or set(labels)!={f['event_id'] for f in features}:
        raise ValueError('STOP: frozen First Hold feature/label population mismatch')
    if Counter(labels.values())!=Counter(EVENTUAL_STRONG=524,NEVER_STRONG=209):
        raise ValueError('STOP: label counts mismatch')
    rows=[f|{'label':labels[f['event_id']]} for f in features]
    numeric=tuple(rows[0]['numeric']);categorical=tuple(rows[0]['categorical'])
    if any(tuple(r['numeric'])!=numeric or tuple(r['categorical'])!=categorical for r in rows):
        raise ValueError('inconsistent feature universes')
    b=LabelBootstrap(days,repetitions=10000,seed=20260907)
    result={}
    for direction in ('ALL','LONG','SHORT'):
        selected=[r for r in rows if direction=='ALL' or r['direction']==direction]
        months=sorted({str(r['session_date'])[:7] for r in selected})
        result[direction]=dict(n=len(selected),numeric={name:compare_numeric(selected,name,b) for name in numeric},
            categorical={name:compare_category(selected,name) for name in categorical},
            monthly={m:dict(numeric={name:compare_numeric([r for r in selected if str(r['session_date'])[:7]==m],name) for name in numeric},
                categorical={name:compare_category([r for r in selected if str(r['session_date'])[:7]==m],name) for name in categorical}) for m in months})
    quality={}
    for mode,outcomes in (('REFERENCE_CLOSE_V1',close_first),('FIRST_EXECUTABLE_MINUTE_OPEN_V1',executable_first)):
        quality[mode]={}
        for direction in ('ALL','LONG','SHORT'):
            selected=[r for r in rows if direction=='ALL' or r['direction']==direction]
            quality[mode][direction]=dict(numeric={name:numeric_quality(selected,outcomes,name) for name in numeric},
                by_label={label:cohort_summary([outcomes[r['event_id']] for r in selected if r['label']==label]) for label in LABELS},
                categorical={name:{category:cohort_summary([outcomes[r['event_id']] for r in selected if r['categorical'][name]==category])
                    for category in sorted({r['categorical'][name] for r in selected})} for name in categorical})
    return dict(rows=rows,comparisons=result,outcome_quality=quality)
