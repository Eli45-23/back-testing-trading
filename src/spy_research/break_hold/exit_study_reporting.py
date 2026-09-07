"""Complete, explicitly scenario-labeled exit-study tables and trade audit export."""
import csv
from io import StringIO
import json
from spy_research.break_hold.entry_timing_analysis import json_default
from spy_research.break_hold.entry_timing_reporting import table, number, percent


def ci(c):
    return f"[{number(c['low'])}, {number(c['high'])}]"


def render_tables(result):
    lines=['# Frozen First Hold exit study — complete tables','',
           'All primary metrics below use the **stop-first sensitivity scenario**, not reconstructed realized ordering. See the adjacent target-first and resolved-only diagnostics. Initial R is fixed. Event drawdown and streak are signal/event-ID ordered, include overlapping events, and are not account or mark-to-market measures.', '',
           'Session bootstrap: 10,000 draws; seed 20260908; pointwise 95% intervals, not adjusted for selecting among 21 models. September is partial. Costs are round-trip dollars per share. Missing ATR is not imputed.']
    lines+=['','## All available entries','']
    lines+=table(['Variant','n','Ambiguous','Mean R stop-first','Mean R target-first','Win %','PF','Event DD R','Losing streak','Mean R 95% CI','Mean R less $0.02'],[
        [name,s['all']['stop_first']['n'],s['all']['statuses'].get('AMBIGUOUS_STOP_TARGET',0),number(s['all']['stop_first']['expectancy_r']),number(s['all']['target_first']['expectancy_r']),percent(s['all']['stop_first']['win_rate']),number(s['all']['stop_first']['profit_factor']),number(s['all']['stop_first']['max_drawdown_r']),s['all']['stop_first']['max_losing_streak'],ci(s['all']['uncertainty']['r_low']),number(s['all']['costs']['0.02']['expectancy_r'])]
        for name,s in result['summaries'].items()])
    lines+=['## Common available-ATR identities — all 21 models','',f"Same {result['counts']['common_sample']} entries, so warm-up availability cannot drive comparisons."]
    lines+=table(['Variant','Mean R','Median R','Win %','PF','Event DD R','LOMO min R','Mean R 95% CI'],[
        [name,number(s['common_sample']['stop_first']['expectancy_r']),number(s['common_sample']['stop_first']['median_r']),percent(s['common_sample']['stop_first']['win_rate']),number(s['common_sample']['stop_first']['profit_factor']),number(s['common_sample']['stop_first']['max_drawdown_r']),number(s['common_sample']['lomo_min']),ci(s['common_sample']['uncertainty']['r_low'])] for name,s in result['summaries'].items()])
    for name,v in result['summaries'].items():
        lines+=['## '+name,'',f"Membership/status counts: `{v['all']['statuses']}`. Exit reasons: `{v['all']['reasons']}`."]
        rows=[]
        for label,s in [('ALL',v['all']),*v['directions'].items()]:
            m=s['stop_first']
            rows.append([label,m['n'],m['session_n'],percent(m['win_rate']),number(m['average_winner_r']),number(m['average_loser_r']),number(m['average_winner_dollars']),number(m['average_loser_dollars']),number(m['expectancy_r']),number(m['median_r']),number(m['profit_factor']),number(m['max_drawdown_r']),m['max_losing_streak'],ci(s['uncertainty']['r_low'])])
        lines+=table(['Direction','n','sessions','Win %','Avg win R','Avg loss R','Avg win $','Avg loss $','Mean R','Median R','PF','Event DD R','Losing streak','Mean R 95% CI'],rows)
        s=v['all']
        lines+=[f"Win-rate 95% CI (fractions): {ci(s['win_rate_uncertainty'])}; target-first mean-R CI: {ci(s['uncertainty']['r_high'])}. Positive/negative months: {s['positive_months']}/{s['negative_months']}; worst month mean R: {number(s['worst_month'])}; LOMO minimum mean R: {number(s['lomo_min'])}. Session-sum drawdown R: {number(s['stop_first']['session_sum_drawdown_r'])}.", '',
                f"Paired stop-first delta versus $0.30/2R on this model's available identities: {number(v['delta_vs_anchor']['mean'])} R, 95% CI {ci(v['delta_vs_anchor'])}, n={v['delta_vs_anchor']['n']}. This is a within-sample comparison, not OOS evidence."]
        lines+=table(['Scenario','n','Mean R','Median R','Win %','PF','DD R','Losing streak'],[
            [label,m['n'],number(m['expectancy_r']),number(m['median_r']),percent(m['win_rate']),number(m['profit_factor']),number(m['max_drawdown_r']),m['max_losing_streak']]
            for label,m in [('Stop-first',s['stop_first']),('Target-first',s['target_first']),('Resolved only (selection diagnostic)',s['resolved_only']),('$0.01 RT cost / stop-first',s['costs']['0.01']),('$0.02 RT cost / stop-first',s['costs']['0.02'])]])
        lines+=table(['Month','n','Mean R','Median R','Win %','PF','Avg winner R','Avg loser R'],[
            [month,m['n'],number(m['expectancy_r']),number(m['median_r']),percent(m['win_rate']),number(m['profit_factor']),number(m['average_winner_r']),number(m['average_loser_r'])] for month,m in s['monthly'].items()])
    return '\n'.join(lines)


def trade_csv(result):
    stream=StringIO();fields=list(result['rows'][0]);writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for r in result['rows']:
        writer.writerow(r|{'updates':json.dumps(r['updates'],default=json_default)})
    return stream.getvalue()
