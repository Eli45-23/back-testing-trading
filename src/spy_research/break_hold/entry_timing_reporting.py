"""Tables and exports for the fixed canonical V1 timing analysis."""
from __future__ import annotations

import csv
from decimal import Decimal
from io import StringIO
from typing import Any

from spy_research.break_hold.entry_timing_analysis import THRESHOLD_KEYS, PRIMARY_PAIR, rate


def number(value: Any, digits: int=4) -> str:
    return 'N/A' if value is None else f'{value:.{digits}f}'


def percent(value: Any) -> str:
    return 'N/A' if value is None else f'{100*value:.2f}%'


def table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    return ['','| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']+[
        '| '+' | '.join(str(v) for v in row)+' |' for row in rows]+['']


def cohort_tables(groups: dict[str,dict[str,Any]], *, all_thresholds: bool=True) -> list[str]:
    rows=[]
    for name,s in groups.items():
        rows.append([name+(' [SMALL]' if s['small_sample'] else ''),s['n'],s['sessions'],f"{s['long_n']}/{s['short_n']}",s['eod_available_n'],
            number(s['mfe']['median']),number(s['mfe']['mean']),number(s['mae']['median']),number(s['mae']['mean']),
            number(s['ratio_mean_mfe_mae']),number(s['eod_move']['median']),percent(s['reclaim_rate'])])
    lines=table(['Group','n','contributing sessions','L/S','EOD n','MFE median $','MFE mean $','MAE median $','MAE mean $','mean MFE/MAE','EOD median $','reclaim %'],rows)
    if all_thresholds:
        lines += ['Clean favorable-first percentages; denominator is every signal in the row. Unavailable, ambiguous, and neither remain in that denominator.']
        lines += table(['Group','n']+list(THRESHOLD_KEYS),[[name,s['n']]+[percent(s['thresholds'][k]['favorable_rate']) for k in THRESHOLD_KEYS] for name,s in groups.items()])
    return lines


def paired_tables(groups: dict[str,dict[str,Any]]) -> list[str]:
    rows=[]
    for name,s in groups.items():
        d=s['entry_disadvantage']
        rows.append([name,s['n'],s['sessions'],s['complete_pair_n'],number(d['mean']),number(d['q25']),number(d['median']),number(d['q75']),
            percent(rate(s['better'],s['n'])),percent(rate(s['worse'],s['n'])),percent(rate(s['essentially_unchanged'],s['n'])),s['exactly_unchanged'],number(s['delay']['mean']),number(s['delay']['median'])])
    lines=table(['Group','pairs','sessions','complete EOD pairs','entry disadvantage mean $','Q25 $','median $','Q75 $','better %','worse %','within 1¢ %','exact same n','delay mean min','delay median min'],rows)
    lines += table(['Group','complete EOD pairs','MFE lost mean $','MFE lost median $','MAE improvement mean $','MAE improvement median $','MAE improvement − MFE lost mean $','MAE saving covers positive MFE loss'],[
        [name,s['complete_pair_n'],number(s['mfe_lost']['mean']),number(s['mfe_lost']['median']),number(s['mae_improvement']['mean']),number(s['mae_improvement']['median']),number(s['excursion_compensation']['mean']),f"{s['mae_reduction_covers_lost_mfe_n']}/{s['mfe_lost_positive_n']}"] for name,s in groups.items()])
    lines += ['The last two columns compare dollar excursion magnitudes only, with no risk preference or realized-payoff interpretation. Positive MAE improvement means less adverse excursion; a negative value means waiting worsened MAE.']
    lines += table(['Group','first MFE mean $','strong MFE mean $','first MAE mean $','strong MAE mean $','first EOD move mean $','strong EOD move mean $'],[
        [name]+[number(s[k]['mean']) for k in ('first_mfe','strong_mfe','first_mae','strong_mae','first_eod_move','strong_eod_move')] for name,s in groups.items()])
    lines += table(['Group','first mean MFE/MAE','strong mean MFE/MAE','first reclaims','strong reclaims','first reclaim delay median min','strong reclaim delay median min'],[
        [name,number(s['first_ratio_mean_mfe_mae']),number(s['strong_ratio_mean_mfe_mae']),s['first_reclaims'],s['strong_reclaims'],number(s['first_minutes_to_reclaim']['median']),number(s['strong_minutes_to_reclaim']['median'])] for name,s in groups.items()])
    return lines


def render_analysis(a: dict[str,Any]) -> str:
    p=a['paired']['ALL']
    avoided=a['cohorts']['NEVER_STRONG']
    entry=p['entry_disadvantage']['mean']
    mfe=p['mfe_lost']['mean']
    mae=p['mae_improvement']['mean']
    primary=avoided['thresholds'][PRIMARY_PAIR]
    lines=['# 2026 V1 break-and-hold: entry-timing analysis','',
        'Analysis of the frozen Jan 1–Sep 4, 2026 canonical experiment. All dates/times use New York sessions. No V1 rules, thresholds, levels, raw data, or canonical outcomes were changed.',
        '', '## Executive summary','',
        f"The counts reconcile: **170 sessions, 1,435 breaks, 733 first holds, 524 strong holds**. There are **{p['n']} exact pairs** and **{avoided['n']} first holds that never become strong**. Excursion differences use **{p['complete_pair_n']} pairs with both EOD measurements available**; {p['unavailable_pair_n']} pairs remain unavailable for that comparison.",
        '',f"Waiting costs **${number(entry)} on average** in directional entry price. On complete pairs, it loses **${number(mfe)} mean remaining MFE** and changes mean MAE by **${number(mae)} of improvement** (negative means more adverse excursion). The complete-pair comparison does not support a blanket claim that a reduction in MAE pays for the later entry.",
        '',f"Strong confirmation also avoids a different population: {avoided['reclaims']}/{avoided['n']} never-strong sequences close-reclaim. On the illustrative $0.50/$0.25 pair, {primary['counts'].get('ADVERSE_FIRST',0)} are adverse-first, but {primary['counts'].get('FAVORABLE_FIRST',0)} are clean favorable-first over EOD and {primary['clean_favorable_before_reclaim']} achieve a clean favorable threshold before the reclaim. Calling all avoided events bad would misrepresent the sample.",
        '', 'The supported conclusion is a **selection-versus-delay tradeoff**, not a demonstrated universally superior entry. Whole-cohort hit rates mix different events; matched-event comparisons condition on eventual strong confirmation. Neither alone proves a deployable edge, causation, or realized expectancy.',
        '', '## Definitions and verification','',
        'Verification details and test results: [verification record](break_hold_entry_timing_verification.md). Frozen analysis conventions: [analysis plan](break_hold_entry_timing_analysis_plan.md).',
        f"Canonical JSON SHA-256: `{a['canonical_json_sha256']}`. V1 definition: `{a['definition_hash']}`. V1 input manifest: `{a['input_manifest_hash']}`.",
        '', '- EOD MFE/MAE are remaining excursions from each original reference entry; pre-reclaim windows remain separate. Fixed-horizon records remain in each pair’s canonical outcome export.',
        '- Entry disadvantage = direction sign × (strong price − first price). Better/worse use a fixed ±$0.01 tolerance; exact equality is also counted. Delay is strong-known-at minus first-known-at.',
        '- MFE lost = first MFE − strong MFE. MAE improvement = first MAE − strong MAE. Both are calculated within the same complete pair, not by subtracting means with different availability.',
        '- Reclaim is a completed-candle fact. No reclaim by EOD is censoring, not proof that a trade won. For a matched event, the reclaim close is identical; only the time remaining from each entry differs.',
        '- The frozen strict future-minute-start rule remains unchanged: the minute starting exactly at signal completion is excluded. Consequently this is not an executable close-entry fill simulation.',
        '- Small sample flags mean n<30 or fewer than 10 contributing sessions. These are descriptive subgroups without adjusted significance claims.',
        '', '## 1. Exact paired comparisons','']
    lines += paired_tables(a['paired'])
    lines += ['','### Every frozen threshold on matched events','',
        'Rates use all pairs, including ambiguity/no-data. “Lost clean” means favorable-first at first hold but not strong hold; “gained clean” is the reverse. Full categorical transition matrices and both hit timestamps are preserved in JSON.']
    lines += table(['Direction','pair $ F/A','n','first clean %','strong clean %','strong − first pp','lost clean n','gained clean n'],[
        [name,key,s['n'],percent(rate(t['first_clean'],s['n'])),percent(rate(t['strong_clean'],s['n'])),number(100*rate(t['strong_clean']-t['first_clean'],s['n']),2),t['lost_clean'],t['gained_clean']]
        for name,s in a['paired'].items() for key,t in s['thresholds'].items()])
    lines += ['','## 2. Whole cohorts and the avoided first holds','']
    lines += cohort_tables(a['cohorts'])
    lines += ['','### Never-strong events by direction','']+cohort_tables(a['never_strong_by_direction'])
    lines += table(['Cohort','n','reclaims','no reclaim by EOD','reclaim delay mean min','reclaim delay median min','pre-reclaim MFE mean $','pre-reclaim MAE mean $'],[
        [name,s['n'],s['reclaims'],s['no_reclaim_by_eod'],number(s['minutes_to_reclaim']['mean']),number(s['minutes_to_reclaim']['median']),number(s['pre_reclaim_mfe']['mean']),number(s['pre_reclaim_mae']['mean'])]
        for name,s in a['cohorts'].items()])
    lines += ['','### Were avoided events bad, or were good moves also lost?','',
        '“Adverse-first” is a threshold-specific bad-path proxy, not a universal trade-quality label. “Favorable touched before reclaim” can include an earlier adverse hit; “clean favorable before reclaim” cannot. Failure timing is known only at the reclaim close.']
    lines += table(['Pair $ F/A','never-strong n','clean favorable EOD','adverse first','ambiguous','neither','no future','favorable touched before reclaim','clean favorable before reclaim'],[
        [key,avoided['n'],t['counts'].get('FAVORABLE_FIRST',0),t['counts'].get('ADVERSE_FIRST',0),t['counts'].get('AMBIGUOUS_SAME_BAR',0),t['counts'].get('NEITHER',0),t['counts'].get('NO_FUTURE_DATA',0),t['favorable_hit_before_reclaim'],t['clean_favorable_before_reclaim']]
        for key,t in avoided['thresholds'].items()])
    lines += ['','## 3. Raw breaks that failed before first hold','',
        'Excursion beyond the opening boundary uses the failed break candle’s saved high/low, not an invented raw-break entry price. Delay is from the first crossing minute’s start to the failure-confirming close. The actual elapsed time lies approximately in (reported−1, reported] minutes; intraminute reclaim timing is unavailable. Groups use the raw crossing-minute time bucket.']
    failures={'ALL':a['failures']['all']}|a['failures']['direction']|a['failures']['time_bucket']
    lines += table(['Group','raw breaks','failed','failure %','beyond level mean $','median $','Q25 $','Q75 $','failure delay mean min','median min'],[
        [name,s['raw_break_n'],s['failed_n'],percent(s['failure_rate']),number(s['beyond_boundary']['mean']),number(s['beyond_boundary']['median']),number(s['beyond_boundary']['q25']),number(s['beyond_boundary']['q75']),number(s['minutes_from_crossing_minute_to_failure_close']['mean']),number(s['minutes_from_crossing_minute_to_failure_close']['median'])]
        for name,s in failures.items()])
    lines += ['Waiting for first hold excludes these immediate close-failures by construction. That supports its confirmation role, but does **not** establish raw-break trading as inferior: V1 has no raw-break reference entry, adverse threshold path, costs, or exit policy for a like-for-like payoff comparison.']
    sections=[('time_bucket','4. Time of day'),('distance','5. Distance to next known key level'),('opening_width_quartile','6. Opening-range width'),('break_attempt','7. First versus later break attempts'),('valid_hold_rank','8. First versus later valid hold sequences'),('opposite_break_context','9. Opposite-boundary break context'),('direction','10. Long versus short')]
    for factor,title in sections:
        lines += ['',f'## {title}','']
        if factor=='distance':
            lines += ['Buckets preserve the V1 inclusive upper boundaries: ≤$0.25, ($0.25,$0.50], ($0.50,$1], ($1,$1.50], ($1.50,$2], >$2, unavailable. Unavailable does not mean infinite room. All levels were already known at the respective entry. No filter is selected.']
        if factor=='opening_width_quartile':
            lines += [f"Session-weighted width cutoffs (25th/50th/75th percentile): {', '.join('$'+number(x) for x in a['opening_width']['cutoffs'])}. Session counts: {a['opening_width']['session_counts']}. Equal widths stay together; no outcome is used to set a boundary."]
        if factor=='valid_hold_rank':
            lines += ['Rank refers to the originating first-hold sequence, even for its strong entry. This avoids labeling every strong entry “later” merely because its own first hold already occurred.']
        if factor=='opposite_break_context':
            lines += ['This uses actual strict breaks and their canonical known-at times, not V1’s touch-before-event annotation. A first opposite break observed at the same confirmation close is separate from a previously completed opposite break; future daily both-sides status is never used.']
        for style,groups in a['groups'][factor].items():
            lines += ['',f'### {style}','']+cohort_tables(groups)
    lines += ['','## 11. Monthly robustness','',
        'September contains only September 1–4 and is a partial month. Contributing-session counts in cohort tables can differ from all calendar sessions shown below.']
    lines += table(['Month','dataset sessions','first n','strong n'],[[m,n,a['groups']['month']['FIRST_HOLD'].get(m,{}).get('n',0),a['groups']['month']['STRONG_HOLD'].get(m,{}).get('n',0)] for m,n in sorted(a['month_sessions'].items())])
    for style,groups in a['groups']['month'].items():
        lines += ['',f'### {style}','']+cohort_tables(groups)
    lines += ['','### Paired disadvantage and excursion tradeoff by month','']+paired_tables(a['monthly_pairs'])
    lines += table(['Month','pairs','first clean % .50/.25','strong clean % .50/.25'],[
        [m,s['n'],percent(rate(s['thresholds'][PRIMARY_PAIR]['first_clean'],s['n'])),percent(rate(s['thresholds'][PRIMARY_PAIR]['strong_clean'],s['n']))] for m,s in a['monthly_pairs'].items()])
    lines += ['','## 12. Session-bootstrap uncertainty','',
        '10,000 whole-session resamples with replacement; deterministic seed 20260906; percentile 95% intervals. All 170 session clusters are sampled. Estimates are event-weighted ratios of resampled cluster sums/counts. Pairs are never broken. LONG and SHORT use the same cluster draws. Intervals are pointwise exploratory intervals, not corrected for multiple comparisons, and do not justify selecting the best context.',
        '', 'Price/excursion differences are in dollars. Hit-rate differences are STRONG minus FIRST in percentage points; negative favors the first reference on matched events.']
    rows=[]
    for direction,metrics in a['uncertainty'].items():
        for name,s in metrics.items():
            multiplier=100 if name.startswith('strong_minus') else 1
            rows.append([direction,name,s['n'],s['contributing_sessions'],number(multiplier*s['mean']) if s['mean'] is not None else 'N/A',number(multiplier*s['low']) if s['low'] is not None else 'N/A',number(multiplier*s['high']) if s['high'] is not None else 'N/A',s['valid_repetitions']])
    lines += table(['Group','metric','n','contributing sessions','estimate','CI low','CI high','valid draws'],rows)
    lines += ['','## 13. Same-minute ambiguity sensitivity','',
        'The alternate denominator removes **only** AMBIGUOUS_SAME_BAR. It does not silently drop neither/no-future records. This sensitivity cannot recover the true intraminute order.']
    lines += table(['Cohort','F/A $','all n','ambiguous n','ambiguous %','clean/all %','nonambiguous n','clean/nonambiguous %'],[
        [name,key,s['n'],t['counts'].get('AMBIGUOUS_SAME_BAR',0),percent(t['ambiguous_rate']),percent(t['favorable_rate']),t['nonambiguous_n'],percent(t['favorable_rate_excluding_ambiguity'])]
        for name,s in a['cohorts'].items() for key,t in s['thresholds'].items()])
    lines += ['','## 14. Outlier sensitivity','',
        'Primary observations are never removed. Trimmed means remove 10% from each event-distribution tail only for this diagnostic. Session concentration sums overlapping events’ MFE and is not additive trading profit. The largest-contribution-session omission is a sensitivity comparison only.']
    lines += table(['Cohort','metric','n','mean','median','10% trimmed mean','Q05','Q25','Q75','Q95'],[
        [name,metric,s[metric]['n']]+[number(s[metric][k]) for k in ('mean','median','trimmed_mean_10pct','q05','q25','q75','q95')]
        for name,s in a['cohorts'].items() for metric in ('mfe','mae')])
    for style,s in a['outliers'].items():
        lines += ['',f'### {style}: session contribution','',f"Top five sessions contribute {percent(s['top_five_share'])} of summed event MFE."]
        lines += table(['Session','summed event MFE $','share'],[[x['session_date'],number(x['sum_event_mfe']),percent(x['share'])] for x in s['top_sessions']])
        omitted=s['sensitivity_excluding_largest_contribution_session']
        lines += [f"Sensitivity excluding only {omitted['session_date']}: remaining n={omitted['distribution']['n']}, mean MFE ${number(omitted['distribution']['mean'])}, median ${number(omitted['distribution']['median'])}. Primary full-sample mean remains ${number(s['full']['mean'])}."]
    lines += ['','## 15. Every fixed 20-session rolling window','',
        'All 151 windows are included, stepping one session at a time. Adjacent windows heavily overlap and are not independent tests. The selected .50/.25 pair is the predeclared V1 illustrative metric, not a window-specific selection. All nine pairs are retained in the analysis JSON.']
    lines += table(['Start','End','style','n','EOD n','median MFE $','median MAE $','clean .50/.25 %'],[
        [r['start'],r['end'],style,r[style]['n'],r[style]['eod_available_n'],number(r[style]['mfe']['median']),number(r[style]['mae']['median']),percent(r[style]['thresholds'][PRIMARY_PAIR]['favorable_rate'])]
        for r in a['rolling'] for style in ('FIRST_HOLD','STRONG_HOLD')])
    lines += ['','## 16. Decision report: ten explicit answers','',
        '1. **Is raw break clearly inferior?** Not established as a trading policy. First confirmation excludes 702/1,435 raw breaks (48.92%) that fail their close, supporting a confirmation role. No frozen raw-entry outcome/exit model exists for an apples-to-apples expectancy claim.',
        '2. **Is first hold clearly better?** On the 524 eventual-strong sequences, first hold has better average entry and remaining excursion geometry. Across complete entry policies, superiority is not established: strong also excludes 209 different events. The illustrative clean rate is 37.38% versus 38.36% across whole cohorts, but 50.19% versus 38.36% on matched events. Selection and delay must not be conflated.',
        f'3. **How much entry quality is lost?** Waiting always takes five minutes in this V1 sample. Mean directional disadvantage is ${number(entry)}, median ${number(p["entry_disadvantage"]["median"])}. Strong is worse by more than one cent on {p["worse"]}/{p["n"]} pairs, better on {p["better"]}, and within one cent on {p["essentially_unchanged"]}. Mean remaining MFE lost is ${number(mfe)}.',
        f'4. **How much adverse excursion is avoided?** Within complete pairs, none on average: MAE increases by ${number(-mae)}. LONG and SHORT both show adverse average changes. Across different populations, strong avoids many early failures; that is a separate selection benefit, not within-event MAE improvement.',
        f'5. **Does MAE improvement justify waiting?** Not clearly supported on paired excursion evidence: mean MAE worsens while MFE falls. Only {p["mae_reduction_covers_lost_mfe_n"]}/{p["mfe_lost_positive_n"]} pairs with positive MFE loss have a dollar MAE saving at least as large. This magnitude comparison is not a risk utility or realized-profit model.',
        '6. **Where does strong appear useful?** It avoids 190 adverse-first paths among the 209 never-strong events at $0.50/$0.25, but also excludes 11 clean favorable-first outcomes (eight clean before reclaim). Whole-cohort descriptive clean rates are higher for strong in 10:00–10:30 and 10:30–11:00, but lower in 13:30–15:00. These are different memberships and time-bucket migration, not tested context-specific entry rules. No context is certified superior.',
        '7. **Does more room mean better outcomes?** A monotonic association is not supported. At $0.50/$0.25, first-hold clean rates range non-monotonically across available-room buckets (33.78%–41.75%); strong’s >$2 bucket is 32.61%, versus 47.06% at ($1,$1.50]. Unavailable room remains its own group. Opening width is also non-monotonic; the widest quartile has higher median MAE for both styles. None becomes a filter.',
        '8. **Does time of day matter?** Descriptive behavior varies: the same illustrative first-hold clean rates span 34.33%–41.90%, strong 26.67%–43.64%. Later signals have shorter remaining exposure, which mechanically affects EOD excursions and censoring. These differences do not establish causality or an optimized time restriction.',
        '9. **Are months consistent?** Paired entry disadvantage and MFE loss are positive, and MAE improvement negative, in every displayed month. The illustrative matched clean-rate comparison favors first in eight of nine months; June is the exception. September has just four sessions and seven pairs. Absolute hit rates vary substantially across the 151 rolling windows; do not infer a stable payoff.',
        '10. **What is supported or uncertain?** The selection-versus-delay tradeoff is supported by this sample. Session-bootstrap 95% intervals for aggregate entry disadvantage ($0.2065–$0.3075), MFE loss ($0.2381–$0.3406), and MAE improvement (−$0.2350 to −$0.1478) exclude zero. They are pointwise, not a multiple-testing license to select contexts. Removing ambiguity changes the illustrative whole-cohort rates from 37.38%/38.36% to 37.79%/38.58%, without reversing their ordering. Outliers elevate means, but the five largest-contribution sessions account for only about 11%–12% of summed event MFE. Causation, policy expectancy, transaction-cost resilience, and independent replication remain uncertain.',
        '', 'No signal refinement, parameter search, data exclusion, options conversion, or trading deployment was performed.',
        '', '## Future hypotheses and independent validation','',
        '- Treat Jan 1–Sep 4, 2026 as in-sample discovery for any refinement. No refinement is implemented here.',
        '- Potential hypotheses include whether strength’s avoided-failure benefit differs by direction/time, and whether its extra close is worth the measured delay. Freeze one limited hypothesis set before opening new outcomes.',
        '- Reserve complete unseen sessions after Sep 4, 2026. Freeze the test dates or minimum number of sessions, definitions, threshold family, paired estimands, missing-data rules, and a one-time evaluation schedule before running it. Avoid repeated peeking and stopping on a favorable result.',
        '- Keep unmodified V1 first/strong controls, all failures, and ambiguity categories. Validate calendar coverage and input lineage before interpreting results. Use the same session-clustered uncertainty method and report each month separately.',
        '- Earlier 2024/2025 samples have already been used for other studies in this repository. They are not automatically untouched holdouts. Any earlier-period alternative needs a documented provenance/exposure audit before being labeled independent.',
        '- Before claiming entry-policy expectancy, separately predeclare a realized underlying exit/cost model. Before any options study, validate that underlying result independently. No options layer or trading deployment is authorized by this analysis.',
        '']
    return '\n'.join(lines)


def paired_csv(a: dict[str,Any]) -> str:
    rows=[]
    for p in a['paired_records']:
        row={k:v for k,v in p.items() if k not in ('first_outcome','strong_outcome')}
        for which in ('first_outcome','strong_outcome'):
            outcome=p[which]
            prefix='first' if which=='first_outcome' else 'strong'
            row[prefix+'_timestamp']=outcome['signal']['timestamp']
            row[prefix+'_reclaim_timestamp']=outcome['reclaim_timestamp']
            for t in outcome['thresholds']:
                key=f"{prefix}_{Decimal(t['favorable']):.2f}_{Decimal(t['adverse']):.2f}"
                row[key+'_result']=t['result']
                row[key+'_favorable_hit']=t['favorable_hit']
                row[key+'_adverse_hit']=t['adverse_hit']
        rows.append(row)
    buf=StringIO()
    writer=csv.DictWriter(buf,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
