from datetime import datetime
import json

import pytest
from spy_research.break_hold.prospective_freeze import CANDIDATES,CONTROL,MANIFEST,verify_freeze,readiness


def data():return json.loads(MANIFEST.read_text())


def test_baseline_and_inventory():
    f=verify_freeze()
    assert f['sessions'][0]['date']=='2026-09-08'
    assert f['sessions'][-1]['date']=='2026-12-01'
    assert len(f['sessions'])==60
    assert tuple(f['candidates'])==CANDIDATES


@pytest.mark.parametrize('time',['2026-09-07T23:59:00-04:00','2026-11-30T23:59:00-05:00','2026-12-01T15:59:59-05:00'])
def test_no_early_decisions(time):
    assert readiness(data(),datetime.fromisoformat(time),[],{}, {})['status']=='INTERIM_NO_SELECTION'


def test_endpoint_not_enough_without_complete_coverage():
    assert readiness(data(),datetime.fromisoformat('2026-12-01T16:00:00-05:00'),[],{}, {})['status']=='BLOCKED_DATA_QUALITY'


def test_atr_insufficiency_not_fallback_or_extension():
    f=data();counts=dict.fromkeys((*CANDIDATES,CONTROL),200);sessions=dict.fromkeys(counts,40)
    counts['ATR050_TARGET_1R']=199
    r=readiness(f,datetime.fromisoformat('2026-12-01T16:00:00-05:00'),[s['date'] for s in f['sessions']],counts,sessions)
    assert r['candidates']['ATR050_TARGET_1R']=='INSUFFICIENT_PROSPECTIVE_DATA'
    assert r['candidates'][CANDIDATES[0]]=='ENDPOINT_REPORT_ELIGIBLE'
    assert 'NO_AUTOMATIC_SELECTION' in r['status']


@pytest.mark.parametrize('days',[['2026-09-04'],['2026-09-08','2026-09-08'],['2026-12-02']])
def test_invalid_session_inventory(days):
    with pytest.raises(ValueError):readiness(data(),datetime.fromisoformat('2026-12-02T23:00:00+00:00'),days,{}, {})


def test_naive_asof_rejected():
    with pytest.raises(ValueError):readiness(data(),datetime(2026,12,1),[],{}, {})
