"""Descriptive research tables; never ranks categories by trading outcome."""
import csv
from io import StringIO
from decimal import Decimal

from spy_research.break_hold.entry_timing_reporting import table,number,percent,paired_tables,cohort_tables
from spy_research.break_hold.first_hold_quality_analysis import LABELS,QUALITY_PAIRS


def numeric_table(features):
    rows=[]
    for name,s in features.items():
        row=[name+(' [SMALL]' if s['small_sample'] else '')]
        for label in LABELS:
            g=s['groups'][label];d=g['distribution']
            row += [f"{g['available_n']}/{g['population_n']} ({g['available_sessions']} sessions)"]+[number(d[k]) for k in ('mean','median','q25','q75')]
        ci=s['bootstrap']
        row += [number(s['mean_difference']),number(s['standardized_mean_difference']),
                f"{number(ci['low'])} to {number(ci['high'])}" if ci else 'not resampled']
        rows.append(row)
    return table(['Feature','eventual available/n','mean','median','Q25','Q75','never available/n','mean','median','Q25','Q75','mean difference E−N','pooled SMD','95% session CI Δmean'],rows)


def category_table(features):
    return table(['Feature','category','n','sessions','eventual n','never n','% of eventual','% of never','eventual/category %'],[
        [name,category+(' [SMALL]' if s['small_sample'] else ''),s['n'],s['sessions'],s['counts'][LABELS[0]],s['counts'][LABELS[1]],
         percent(s['within_label_percentages'][LABELS[0]]),percent(s['within_label_percentages'][LABELS[1]]),percent(s['eventual_strong_rate'])]
        for name,categories in features.items() for category,s in categories.items()])


def render_tables(a):
    lines=['# First Hold quality: complete descriptive tables','',
        'All numeric variables remain continuous. E−N = eventual-strong minus never-strong. SMD uses pooled sample standard deviations; no classifier or profitable-category selection. [SMALL] means fewer than 30 available observations in a label or fewer than 10 contributing sessions (category tables flag their category). Warm-up missingness is not imputed. September is partial.',
        '', '## Reference-mode comparison','']
    for direction,s in a['references'].items():
        lines += [f'### {direction}','',f"Same canonical pairs {s['total_pairs']}; both executable entries available {s['available_entry_pairs']}; unavailable {s['unavailable_entry_pairs']}. All-pair threshold denominators retain the unavailable entries."]
        lines += paired_tables({'REFERENCE_CLOSE_V1_ALL':s['close_all'],'REFERENCE_CLOSE_V1_COMMON':s['close_common'],'FIRST_EXECUTABLE_MINUTE_OPEN_V1':s['executable']})
        lines += table(['metric','n','estimate','95% low','95% high','valid draws'],[[k,v['n'],number(v['mean']),number(v['low']),number(v['high']),v['valid_repetitions']] for k,v in s['uncertainty'].items()])
        lines += table(['F/A $','all pairs','first clean %','strong clean %','first categories','strong categories','95% CI strong−first pp'],[
            [k,v['n'],percent(v['first_clean_rate']),percent(v['strong_clean_rate']),str(v['first_counts']),str(v['strong_counts']),f"{number(100*v['bootstrap']['low'])} to {number(100*v['bootstrap']['high'])}"] for k,v in s['all_pair_thresholds'].items()])
    for direction,s in a['comparisons'].items():
        lines += ['',f'## Signal-time features: {direction}','']+numeric_table(s['numeric'])+category_table(s['categorical'])
    lines += ['','## Continuous feature versus separate outcome-quality evaluations','',
        'Excursion associations are Spearman correlations. Threshold associations are point-biserial correlations with clean favorable-first = 1 and other evaluable outcomes = 0. Ambiguous and no-future observations are excluded from these correlations only, with evaluable n shown; their counts remain in JSON and categorical outcome tables. These descriptive correlations have no independent-significance claim. No continuous variable is bucketed or optimized.']
    for mode,directions in a['outcome_quality'].items():
        for direction,s in directions.items():
            lines += ['',f'### {mode}: {direction} evaluation labels','',
                'Labels are retrospective evaluations, never predictors. Never-strong includes session-close censoring; longer pre-reclaim exposure in eventual-strong sequences is not a causal benefit.']+cohort_tables(s['by_label'])
            lines += ['',f'### {mode}: {direction} continuous','']
            metrics=('pre_reclaim_mfe','pre_reclaim_mae')+QUALITY_PAIRS
            lines += table(['feature']+[f'{k}: r (n)' for k in metrics],[[name]+[f"{number(v[k]['association'])} ({v[k]['n']})" for k in metrics] for name,v in s['numeric'].items()])
            lines += ['',f'### {mode}: {direction} categorical','']
            lines += table(['feature','category','n','sessions','pre-reclaim MFE n/mean/median','pre-reclaim MAE n/mean/median']+list(QUALITY_PAIRS)+['ambiguous n across four pairs','no future n across four pairs'],[
                [name,category+(' [SMALL]' if v['small_sample'] else ''),v['n'],v['sessions']]+[
                    f"{v[k]['n']}/{number(v[k]['mean'])}/{number(v[k]['median'])}" for k in ('pre_reclaim_mfe','pre_reclaim_mae')]+[
                    percent(v['thresholds'][k]['favorable_rate']) for k in QUALITY_PAIRS]+[
                    '/'.join(str(v['thresholds'][k]['counts'].get(status,0)) for k in QUALITY_PAIRS) for status in ('AMBIGUOUS_SAME_BAR','NO_FUTURE_DATA')]
                for name,categories in s['categorical'].items() for category,v in categories.items()])
    for direction,s in a['comparisons'].items():
        lines += ['',f'## Complete monthly stability: {direction}','',
            'Every feature is shown, not only those selected for the decision summary. Monthly intervals are not estimated. Monthly medians, quartiles, mean differences and category denominators remain explicit. September contains only four sessions.']
        for month,m in s['monthly'].items():
            lines += ['',f'### {month}'+(' — PARTIAL / SMALL' if month.endswith('-09') else ''),'']+numeric_table(m['numeric'])+category_table(m['categorical'])
    return '\n'.join(lines)+'\n'


def render_decision(a):
    all_ref=a['references']['ALL']; ex=all_ref['executable']; ci=all_ref['uncertainty']['entry_disadvantage']
    numeric=a['comparisons']['ALL']['numeric']
    strongest=sorted(((name,s) for name,s in numeric.items() if s['standardized_mean_difference'] is not None),key=lambda item:-abs(item[1]['standardized_mean_difference']))[:10]
    lines=['# First Hold quality and executable-entry timing','',
        '## Bottom line','',
        f"The frozen population reconciles: **170 sessions, 1,435 breaks, 733 First Holds, 524 eventual-strong, 209 never-strong**. Using the first eligible minute’s open, waiting for strong confirmation costs **${number(ex['entry_disadvantage']['mean'])} on average**, versus **${number(all_ref['close_all']['entry_disadvantage']['mean'])}** in the original close-reference comparison. The executable cost’s session-bootstrap 95% interval is **${number(ci['low'])}–${number(ci['high'])}**.",
        '',f"Executable paired remaining MFE lost: **${number(ex['mfe_lost']['mean'])}**; MAE improvement: **${number(ex['mae_improvement']['mean'])}** (negative means more adverse excursion). There are {all_ref['available_entry_pairs']} pairs with both executable entries and {all_ref['unavailable_entry_pairs']} unavailable strong entries at session close. Common-sample close comparisons are included in the tables so this denominator change is visible.",
        '', 'This is an entry-reference study, not a fill guarantee or exit strategy. The exact historical minute open omits order latency, spread, slippage, and costs. A feature’s association with surviving one extra candle is not evidence that it improves tradable outcomes.',
        '', '## Signal-time differences','',
        'The following are the largest absolute pooled standardized mean differences, presented descriptively rather than as significance-selected predictors. Overlapping candle geometry and market-condition fields are correlated; they are not independent discoveries. Full availability, medians, quartiles, uncertainty, both directions and every month are in the tables.']
    lines += numeric_table(dict(strongest))
    lines += ['','### Month-by-month mean differences for these fields','']
    months=tuple(a['comparisons']['ALL']['monthly'])
    lines += table(['feature']+list(months),[[name]+[number(a['comparisons']['ALL']['monthly'][m]['numeric'][name]['mean_difference']) for m in months] for name,_ in strongest])
    lines += ['','## Decision: six answers','',
        '1. **Most different:** deeper First Hold closes beyond ORH5/ORL5 and a larger body relative to candle range. Mean directional distance is $0.4432 for eventual-strong versus $0.2041 for never-strong (SMD 0.579). Mean body/range is 0.6685 versus 0.5611 (SMD 0.514). ATR-normalized distance also differs (SMD 0.557), but only 400/733 observations have a warmed-up ATR.',
        '2. **Monthly consistency:** pooled dollar distance and ATR-normalized distance differences are positive in every displayed month. Pooled body/range differences are positive in January–August but reverse in small, partial September. Direction splits reveal exceptions: dollar distance reverses for shorts in January; body/range reverses for shorts in July. These are broad descriptive patterns, not universal rules.',
        '3. **Weak/noisy:** opening width has effectively zero pooled SMD (0.001), volume −0.040, relative volume −0.014, and ATR 0.153 with a mean-difference interval crossing zero. Several EMA/VWAP cross and room measurements appear different in aggregate but reverse by month or direction and have substantial warm-up unavailability. Do not promote them because one interval excludes zero.',
        '4. **Long versus short:** eventual-strong rates are 70.75% (283/400) for longs and 72.37% (241/333) for shorts. Dollar distance effects exist in both directions but are larger standardized effects for longs (0.706 versus 0.488); body/range is likewise stronger for longs (0.598 versus 0.408). Relative-volume differences have opposing signs and uncertainty spanning zero. Executable waiting costs are $0.2284 for longs and $0.2855 for shorts. Do not impose symmetric feature rules.',
        '5. **Promising enough for a future predeclared test:** distance beyond the boundary and body/range merit a limited continuous-variable replication study of survival. They are not ready as entry-quality filters. Deeper distance mechanically gives more room before a close-reclaim, while a later/farther entry can worsen adverse geometry. Separate survival from the four fixed path outcomes in any follow-up.',
        '6. **Do not turn into filters:** no numeric cutoff, favorable time bucket, alignment state, room bucket, or composite score is supported for deployment here. Body/range is associated with survival but has near-zero executable clean-threshold correlations (−0.012 to +0.014 across the four requested pairs). Distance’s executable clean-threshold correlations are only +0.053 to +0.094, whereas its pre-reclaim MAE association is much larger (Spearman +0.498). These are correlations, not predictive accuracy or incremental edge.',
        '', '## Outcome quality is a separate question','',
        'In the executable-reference analysis, distance beyond the level has Spearman correlations of +0.256 with pre-reclaim MFE and +0.498 with pre-reclaim MAE. Body/range has +0.131 and +0.164 respectively. Thus the strongest survival descriptors are not clearly favorable-risk descriptors. Pre-reclaim duration and distance-to-boundary geometry are partly built into the evaluation; no exit performance is inferred.',
        '', 'All 733 observations remain. Six First Holds occurring at session close have no future outcome and cannot be observed progressing to strong that day; they remain in the requested never-strong label, explicitly censored rather than called failed trades. Stage 10.9/11.3 availability also depends on time of day, so available-only comparisons are not full-population effects.',
        '', '## Future Hypotheses — not implemented','',
        '- Freeze an independent post–September 4, 2026 evaluation of continuous boundary distance and body/range, preserving First Hold and Strong Hold controls, direction splits, missingness and the four fixed threshold pairs. Do not choose cutoffs from this sample.',
        '- Predeclare that stronger survival association alone is insufficient: any proposed entry rule must independently improve path quality without an unacceptable adverse-excursion tradeoff. Account for time-of-day, warm-up availability, volatility and session-close censoring in the future design.',
        '- Freeze dates/sample requirements and a single evaluation schedule before inspecting new outcomes. No repeated peeking, arbitrary combinations, model training, score, or new candidate now. Only after entry policy is separately reviewed should an exit-model study begin.',
        '']
    lines += ['','## Timing and leakage safeguards','',
        '- Stored five-minute timestamp = candle start; signal-known time = start + five minutes. The executable selector requires a validated SPY SIP raw RTH minute starting at or after that completion; its open is the separate reference. Its high/low path is included. No confirming-candle constituent minute is eligible.',
        '- Original REFERENCE_CLOSE_V1 signals, prices, paths, definition hash, and files remain unchanged. New outcomes retain original signal records plus separate entry price/time/status fields.',
        '- Feature construction accepts no event outcome or label. Indicators and confirmed swings are recomputed with accepted pure engines using only the completed same-session prefix, ending at the exact First Hold row. Future bars are cut off before indicator computation.',
        '- Session-reset EMA/ATR warm-up is retained. Relative volume excludes confirmation and requires six prior completed bars. Known-level omissions remain flagged; Stage 11.2 uses the original V1 level universe, which does not introduce PDC.',
        '- **Stage 11.1 limitation:** no saved calibration artifact with causal availability was found. Regime labels are UNAVAILABLE_CALIBRATION_PROVENANCE for all 733 observations. Its continuous Stage 10.9 inputs are included. Rebuilding full-period quartiles and calling them signal-time predictors would violate the requested leakage constraint.',
        '- All feature values are computed before the EVENTUAL_STRONG / NEVER_STRONG label join. Outcome quality is evaluated in a separate layer. No labels, reclaim, strong candle, EOD values or threshold results enter a feature.',
        '', '## Interpretation limits','',
        'All comparisons are descriptive in-sample associations. Whole-session bootstrap uses 10,000 shared cluster draws, seed 20260907, with event-weighted estimates. Intervals are pointwise, not adjusted confirmation across 70 correlated numeric fields. Missingness and group composition can confound results. Direction splits and monthly tables are diagnostics, not an unrestricted combination search. September is partial and small.',
        '', '## Artifacts and verification','',
        'Full suite: **1,137 passed**, including **25 new focused tests**. Independent raw-minute audit and frozen-file integrity checks passed. [Verification and limitations](break_hold_first_hold_quality_verification.md).',
        '[Complete tables](break_hold_first_hold_quality_tables.md) · [Machine-readable results](break_hold_first_hold_quality_analysis.json) · [Signal-time feature records](break_hold_first_hold_quality_features.csv) · [Executable pairs](break_hold_first_hold_quality_executable_pairs.csv) · [Frozen analysis plan](break_hold_first_hold_quality_plan.md)',
        '',f"Canonical SHA-256: `{a['canonical_sha256']}`. V1 definition hash: `{a['definition_hash']}`. Original input-manifest hash: `{a['input_manifest_hash']}`.",
        '']
    return '\n'.join(lines)


def feature_csv(a):
    rows=[]
    for r in a['rows']:
        row={k:v for k,v in r.items() if k not in ('numeric','categorical','unavailable_reasons')}
        row.update({'numeric.'+k:v for k,v in r['numeric'].items()})
        row.update({'category.'+k:v for k,v in r['categorical'].items()})
        rows.append(row)
    return csv_rows(rows)


def csv_rows(rows):
    buf=StringIO();writer=csv.DictWriter(buf,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return buf.getvalue()


def executable_csv(a):
    rows=[]
    pairs={p['event_id']:p for p in a['references']['ALL']['pairs']}
    by_id={(o['signal']['event_id'],o['signal']['entry_style']):o for o in a['executable_outcomes']}
    fields=[k for k in next(iter(pairs.values())) if k not in ('first_outcome','strong_outcome')]
    for strong in a['executable_outcomes']:
        if strong['signal']['entry_style']!='STRONG_HOLD':continue
        identity=strong['signal']['event_id'];first=by_id[(identity,'FIRST_HOLD')]
        r=pairs.get(identity,{})
        row={k:r.get(k) for k in fields}
        row.update(event_id=identity,session_date=strong['signal']['session_date'],direction=strong['signal']['direction'],
            first_price=first['entry_price'],strong_price=strong['entry_price'],
            first_entry_timestamp=first['entry_timestamp'],strong_entry_timestamp=strong['entry_timestamp'],
            first_entry_status=first['entry_status'],strong_entry_status=strong['entry_status'],
            first_signal_known_at=first['signal']['timestamp'],strong_signal_known_at=strong['signal']['timestamp'])
        for which,outcome in (('first_outcome',first),('strong_outcome',strong)):
            for t in outcome['thresholds']:
                key=f"{which}.{Decimal(t['favorable']):.2f}/{Decimal(t['adverse']):.2f}"
                row[key]=t['result']
                row[key+'.favorable_hit']=t['favorable_hit']
                row[key+'.adverse_hit']=t['adverse_hit']
        rows.append(row)
    return csv_rows(rows)
