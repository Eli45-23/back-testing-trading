"""Offline attribution estimands: pairing, missingness and session clustering."""
from datetime import date, timedelta
from decimal import Decimal as D
from types import SimpleNamespace

import numpy as np
import pytest

from spy_research.break_hold.entry_timing_analysis import (
    SessionBootstrap, cohort_summary, distribution, pair_record, paired_summary,
    verify_canonical,
)
from spy_research.events.break_and_hold import detect_break_holds
from spy_research.outcomes.excursions import measure_hold
from test_break_hold import fixture


@pytest.fixture
def outcomes():
    cal, session, raw, bars = fixture({
        1: ('100', '102', '100', '101.5'),
        2: ('101.5', '103', '101.4', '102'),
        3: ('102', '102', '100', '100'),
    })
    event = detect_break_holds(bars, raw, calendar=cal).events[0]
    return tuple(measure_hold(event, signal, raw, session)
                 for signal in (event.first_hold, event.strong_hold))


def test_count_gate_stops_before_any_interpretation():
    with pytest.raises(ValueError, match='STOP: canonical counts'):
        verify_canonical(SimpleNamespace(sessions=[], outcomes=[]))


@pytest.mark.parametrize('direction,expected', [('LONG', D('.5')), ('SHORT', D('-.5'))])
def test_directional_price_cost_and_exact_pair(outcomes, direction, expected):
    first, strong = [o.model_copy(update={'signal': o.signal.model_copy(update={'direction': direction})}) for o in outcomes]
    p = pair_record(first, strong)
    assert p['entry_disadvantage'] == expected
    assert p['raw_price_difference'] == D('.5')
    assert p['delay_minutes'] == 5
    assert p['first_minutes_to_reclaim'] - p['strong_minutes_to_reclaim'] == 5
    assert p['mfe_lost'] == p['first_mfe'] - p['strong_mfe']
    assert p['mae_improvement'] == p['first_mae'] - p['strong_mae']


@pytest.mark.parametrize('change,result', [('.01','UNCHANGED_WITHIN_ONE_CENT'), ('-.01','UNCHANGED_WITHIN_ONE_CENT'), ('.010001','WORSE'), ('-.010001','BETTER'), ('0','UNCHANGED_WITHIN_ONE_CENT')])
def test_predeclared_one_cent_tolerance(outcomes, change, result):
    first, strong = outcomes
    strong = strong.model_copy(update={'signal': strong.signal.model_copy(update={'price': first.signal.price + D(change)})})
    assert pair_record(first, strong)['entry_comparison'] == result


@pytest.mark.parametrize('field,value', [('event_id','wrong'), ('direction','SHORT'), ('session_date',date(2026,8,20))])
def test_identity_mismatch_rejected(outcomes, field, value):
    first, strong = outcomes
    strong = strong.model_copy(update={'signal': strong.signal.model_copy(update={field:value})})
    with pytest.raises(ValueError, match='identities'):
        pair_record(first, strong)


def test_reclaim_identity_and_chronology_fail_closed(outcomes):
    first, strong = outcomes
    with pytest.raises(ValueError, match='reclaim'):
        pair_record(first, strong.model_copy(update={'reclaim_timestamp':None}))
    with pytest.raises(ValueError, match='chronology'):
        pair_record(first, strong.model_copy(update={'signal':strong.signal.model_copy(update={'timestamp':first.signal.timestamp})}))


def test_missing_excursion_keeps_entry_pair_and_threshold_denominator(outcomes):
    first, strong = outcomes
    windows = tuple(w.model_copy(update={'mae':None}) if w.horizon=='EOD' else w for w in strong.windows)
    p = pair_record(first, strong.model_copy(update={'windows':windows}))
    s = paired_summary([p])
    assert s['n'] == s['unavailable_pair_n'] == s['entry_disadvantage']['n'] == 1
    assert s['complete_pair_n'] == s['mfe_lost']['n'] == 0
    assert p['mfe_lost'] is None and p['mae_improvement'] is None
    assert all(sum(t['transitions'].values()) == 1 for t in s['thresholds'].values())


def test_ambiguity_removed_only_from_alternate_denominator(outcomes):
    first, _ = outcomes
    variants=[]
    for result in ('FAVORABLE_FIRST','ADVERSE_FIRST','AMBIGUOUS_SAME_BAR','NEITHER','NO_FUTURE_DATA'):
        thresholds=tuple(t.model_copy(update={'result':result,'favorable_hit':first.signal.timestamp+timedelta(minutes=1)}) for t in first.thresholds)
        variants.append(first.model_copy(update={'thresholds':thresholds}))
    s=cohort_summary(variants)
    for t in s['thresholds'].values():
        assert sum(t['counts'].values()) == 5
        assert t['favorable_rate'] == D('.2')
        assert t['nonambiguous_n'] == 4
        assert t['favorable_rate_excluding_ambiguity'] == D('.25')
        assert t['favorable_hit_before_reclaim'] == 5
        assert t['clean_favorable_before_reclaim'] == 1


def test_favorable_after_reclaim_not_counted_as_pre_reclaim(outcomes):
    first, _ = outcomes
    ts=tuple(t.model_copy(update={'result':'FAVORABLE_FIRST','favorable_hit':first.reclaim_timestamp}) for t in first.thresholds)
    s=cohort_summary([first.model_copy(update={'thresholds':ts})])
    assert all(t['counts']['FAVORABLE_FIRST']==1 and t['clean_favorable_before_reclaim']==0 for t in s['thresholds'].values())


def test_session_bootstrap_shared_clusters_and_event_weighting():
    days=[date(2026,1,2), date(2026,1,5)]
    b=SessionBootstrap(days, repetitions=1000, seed=17)
    c=SessionBootstrap(days, repetitions=1000, seed=17)
    assert np.array_equal(b.weights,c.weights)
    assert np.all(b.weights.sum(axis=1)==2)
    obs=[(days[0],D(0)),(days[0],D(0)),(days[1],D(9))]
    result=b.interval(obs)
    assert result['mean']==3  # Not the equal-session mean, 4.5.
    assert result['low']==0 and result['high']==9
    doubled=b.interval(obs+obs)
    assert [result[k] for k in ('mean','low','high')] == [doubled[k] for k in ('mean','low','high')]
    assert result['contributing_sessions']==2 and result['valid_repetitions']==1000


def test_session_bootstrap_missing_clusters_and_empty_measurements():
    days=[date(2026,1,2),date(2026,1,5)]
    b=SessionBootstrap(days,repetitions=1000,seed=17)
    s=b.interval([(days[0],D(2))])
    assert s['mean']==s['low']==s['high']==2
    assert 0<s['valid_repetitions']<1000
    assert b.interval([])['valid_repetitions']==0


def test_distributions_do_not_delete_or_mutate_observations():
    xs=[D(x) for x in reversed(range(20))]
    before=xs.copy()
    s=distribution(xs)
    assert xs==before and s['n']==20
    assert s['mean']==s['median']==s['trimmed_mean_10pct']==D('9.5')
    assert s['q25']==D('4.75') and s['q75']==D('14.25')
    assert distribution([])['mean'] is None
