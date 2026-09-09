"""Synthetic regressions only: no historical strategy outcomes or network I/O."""
from dataclasses import asdict, replace
from datetime import date, datetime, timedelta, UTC
from decimal import Decimal as D
from hashlib import sha256
import json
import subprocess
import sys

import pytest

from spy_research.edge_discovery_v1.canonical import Envelope, canonical_bytes, canonical_hash
from spy_research.edge_discovery_v1.protocol import protocol, PROTOCOL_SHA256
from spy_research.edge_discovery_v1.inventory import expected_path, role_for, verify_inventory, verified_partition
from spy_research.edge_discovery_v1.phases import ResearchState
from spy_research.edge_discovery_v1.gates import Evidence, evaluate
from spy_research.edge_discovery_v1.ledger import SearchLedger
from spy_research.edge_discovery_v1.features import completed_prefix, baseline_key
from spy_research.edge_discovery_v1.statistics import SessionBootstrap, by_adjusted
from spy_research.edge_discovery_v1.execution import Minute, Signal, simulate_session
from spy_research.edge_discovery_v1.walk_forward import FOLDS, training_rows, validate_threshold_fit
from spy_research.edge_discovery_v1.reports import validate_label

T=datetime(2024,1,2,14,30,tzinfo=UTC)

def evidence(**changes):
    values=dict(trades=300,sessions=100,net_mean_r=D('.10'),net_pf=D('1.20'),active_months=12,positive_months=9,net_drawdown_r=D('10'),net_total_r=D('30'),top_month_share=D('.20'),top5_session_share=D('.15'),net_lomo_min=D('.03'),direction_unchanged=True,adjusted_ci_low=D('.01'))
    return Evidence(**(values|changes))

def candidate(identity='a'):
    return dict(id=identity,signal='synthetic_reference_cross',entry=protocol()['execution']['entry'],exit='TARGET_1R',stop='USD030',thresholds={'reference':'100'},direction='BOTH',conditions=['synthetic'],discovery_evidence_hash='a'*64)

def batch(ids=('a','b')):
    return ResearchState().discovery(synthetic=True).freeze_batch([candidate(i) for i in ids],'b'*64,{'dependency':'c'*64},synthetic=True)

def partition(tmp_path,day=date(2024,1,2)):
    path=tmp_path/expected_path(day);path.parent.mkdir(parents=True);path.write_bytes(b'synthetic partition bytes')
    row=dict(path=expected_path(day),session_date=day.isoformat(),role=role_for(day),byte_size=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest(),coverage_status='VALID')
    return path,Envelope.seal({'partitions':[row]})

def minute(i,o='100',h='100.1',l='99.9',c='100'):
    return Minute(T+timedelta(minutes=i),D(o),D(h),D(l),D(c))

def execute(bars,signals=None,stop='USD030',exit='TARGET_1R'):
    return simulate_session(bars,signals if signals is not None else [Signal('s',T,'LONG')],T,T+timedelta(minutes=len(bars)),stop,exit,synthetic=True)

def test_canonical_stable_and_decimal():
    assert canonical_bytes({'b':D('.3'),'a':1})==b'{"a":1,"b":"0.3"}'
    assert canonical_hash({'a':1,'b':2})==canonical_hash({'b':2,'a':1})
    assert canonical_hash(protocol())==PROTOCOL_SHA256

@pytest.mark.parametrize('bad',[.3,float('nan'),D('NaN'),{1:'x'}])
def test_canonical_invalid(bad):
    with pytest.raises((TypeError,ValueError)):canonical_bytes(bad)

def test_envelope_nested_immutable():
    data={'a':[1]};sealed=Envelope.seal(data);data['a'].append(2)
    assert sealed.verify(sealed.digest)=={'a':[1]}
    with pytest.raises(ValueError):replace(sealed,payload=b'{}').verify(sealed.digest)

@pytest.mark.parametrize('day',[date(2023,6,5),date(2026,9,8),date(2026,12,1),date(2027,1,1)])
def test_dates_rejected(day):
    with pytest.raises(ValueError):role_for(day)

def test_inventory_valid(tmp_path):
    _,e=partition(tmp_path)
    assert verify_inventory(e,e.digest,tmp_path,require_complete=False)
    with pytest.raises(ValueError):verify_inventory(e,e.digest,tmp_path)

@pytest.mark.parametrize('kind',['bytes','missing','hash','duplicate','role','path','coverage'])
def test_inventory_tampering(tmp_path,kind):
    path,e=partition(tmp_path);data=e.verify(e.digest)
    if kind=='bytes':path.write_bytes(b'changed')
    elif kind=='missing':path.unlink()
    elif kind=='hash':
        with pytest.raises(ValueError):verify_inventory(e,'0'*64,tmp_path,require_complete=False)
        return
    elif kind=='duplicate':data['partitions']*=2
    elif kind=='role':data['partitions'][0]['role']='VALIDATION'
    elif kind=='path':data['partitions'][0]['path']='../outside.parquet'
    else:data['partitions'][0]['coverage_status']='INVALID'
    new=Envelope.seal(data)
    with pytest.raises(ValueError):verify_inventory(new,new.digest,tmp_path,require_complete=False)

def test_context_and_outcome_access(tmp_path):
    _,e=partition(tmp_path,date(2023,12,29))
    assert verified_partition(e,e.digest,tmp_path,date(2023,12,29),'CONTEXT',purpose='HASH_VERIFY')
    with pytest.raises(ValueError):verified_partition(e,e.digest,tmp_path,date(2023,12,29),'DISCOVERY',purpose='HASH_VERIFY')
    with pytest.raises(PermissionError):verified_partition(e,e.digest,tmp_path,date(2023,12,29),'CONTEXT',purpose='OUTCOME')

def test_no_real_discovery_or_batch():
    with pytest.raises(PermissionError):ResearchState().discovery()
    with pytest.raises(PermissionError):ResearchState().freeze_batch([],None,None)

def test_validation_before_batch():
    with pytest.raises(ValueError):ResearchState().authorize(2025,'a',synthetic=True)

@pytest.mark.parametrize('count',[0,4])
def test_batch_size(count):
    with pytest.raises(ValueError):batch(tuple(str(i) for i in range(count)))

def test_batch_no_insertion_or_replacement():
    s=batch()
    s.authorize(2025,'a',synthetic=True)
    with pytest.raises(ValueError):s.authorize(2025,'replacement',synthetic=True)
    with pytest.raises(ValueError):s.freeze_batch([candidate('new')],'b',{'d':'h'},synthetic=True)
    with pytest.raises(PermissionError):s.authorize(2025,'a')
    with pytest.raises(ValueError):replace(s,batch_hash='0'*64).authorize(2025,'a',synthetic=True)

def test_batch_partial_and_premature_confirmation():
    s=batch()
    with pytest.raises(ValueError):s.complete_validation({'a':evidence()},synthetic=True)
    with pytest.raises(ValueError):s.authorize(2026,'a',synthetic=True)
    with pytest.raises(ValueError):s.begin_confirmation()

def test_mechanical_survivors_and_labels():
    s=batch().complete_validation({'a':evidence(),'b':evidence(trades=100,sessions=80)},synthetic=True)
    assert s.verified_receipt()['survivors']==['a']
    s=s.begin_confirmation();s.authorize(2026,'a',synthetic=True)
    with pytest.raises(ValueError):s.authorize(2026,'b',synthetic=True)
    assert s.finish({'a':evidence()},synthetic=True).confirmation==( ('a','ROBUST_EDGE_CANDIDATE'), )

def test_forged_survivors_fail_even_with_self_consistent_hash():
    s=batch().complete_validation({'a':evidence(),'b':evidence(net_mean_r=D('-.1'))},synthetic=True)
    data=s.receipt.verify(s.receipt_hash);data['survivors']=['a','b'];forged=Envelope.seal(data)
    with pytest.raises(ValueError):replace(s,receipt=forged,receipt_hash=forged.digest).begin_confirmation()

def test_empty_survivors_final_no_candidate():
    s=batch(('a',)).complete_validation({'a':evidence(net_mean_r=D('-.1'))},synthetic=True).begin_confirmation()
    assert s.finish({},synthetic=True).confirmation==()

@pytest.mark.parametrize('label',['PROVEN_EDGE','LIVE_READY','BEST_STRATEGY'])
def test_forbidden_labels(label):
    with pytest.raises(ValueError):validate_label(label)

@pytest.mark.parametrize('field,value', [('net_mean_r',D('.049')),('net_pf',D('1.09')),('net_drawdown_r',D('41')),('net_total_r',D('9')),('top_month_share',D('.351')),('top5_session_share',D('.251')),('net_lomo_min',D(0)),('adjusted_ci_low',D(0)),('direction_unchanged',False),('positive_months',7)])
def test_each_gate_fails(field,value):
    assert not evaluate(evidence(**{field:value}),'VALIDATION')['passed']

def test_gate_exact_boundaries():
    assert evaluate(evidence(net_mean_r=D('.05'),net_pf=D('1.10'),net_drawdown_r=D(40),net_total_r=D(40),top_month_share=D('.35'),top5_session_share=D('.25'),positive_months=8),'VALIDATION')['passed']
    assert evaluate(evidence(trades=150,sessions=60),'INTERNAL_CONFIRMATION')['passed']
    assert not evaluate(evidence(trades=150,sessions=60),'VALIDATION')['passed']
    with pytest.raises(ValueError):evaluate(evidence(cost=D('.01')),'VALIDATION')

def hypothesis(i=0):
    return dict(predicate=f'feature>{i}',thresholds=[str(i)],direction='LONG',cadence=5,primary_horizon=15,expected_effect='positive',conditions=['x'])

def test_hypothesis_budget_and_result_ledger():
    ledger=SearchLedger()
    for i in range(100):ledger,identity=ledger.register('hypothesis',hypothesis(i),T)
    with pytest.raises(ValueError):ledger.register('hypothesis',hypothesis(100),T)
    same,_=ledger.register('hypothesis',hypothesis(0),T);assert same==ledger
    recorded=ledger.record(identity,atomic_comparisons=5,result={'status':'REJECTED'},rejection_reason='no lift')
    assert recorded.atomic_comparisons==5 and len(ledger.entries)==100
    recorded.verify()

def test_strategy_budget():
    ledger=SearchLedger()
    for i in range(60):ledger,_=ledger.register('strategy',candidate(str(i)),T)
    with pytest.raises(ValueError):ledger.register('strategy',candidate('61'),T)

def test_prefix_and_baseline():
    bars=[minute(i) for i in range(5)]
    assert len(completed_prefix(bars,T+timedelta(minutes=3),1))==3
    assert completed_prefix([minute(0)],T+timedelta(minutes=4),5)==()
    assert len(completed_prefix([minute(0)],T+timedelta(minutes=5),5))==1
    assert baseline_key('2024-01',30,'LONG',['ATR','VWAP'])!=baseline_key('2024-01',30,'LONG',['VWAP'])

def test_training_only_and_purge():
    rows=[dict(observation_date=date(2024,3,28),label_end_date=date(2024,4,1)),dict(observation_date=date(2024,3,28),label_end_date=date(2024,3,28))]
    assert training_rows(rows,FOLDS[0])==(rows[1],)
    with pytest.raises(ValueError):validate_threshold_fit([date(2024,4,1)],FOLDS[0])

def test_session_bootstrap_shared_and_pairing():
    days=[date(2024,1,2),date(2024,1,3)]
    b=SessionBootstrap(days);values=[(days[0],D(1)),(days[1],D(1))]
    a=b.interval(values)
    assert a['valid_draws']==10000 and a['ci95']==['1.0','1.0']
    assert a==SessionBootstrap(days).interval(values)
    assert b.paired({'a':values[0]},{'a':values[0]})['mean']=='0.0'
    with pytest.raises(ValueError):b.paired({'a':values[0]},{'b':values[0]})
    assert by_adjusted([.01,.02,.9])[0]>=.01

def test_entry_timing_no_confirming_bar():
    bars=[minute(0,h='101',l='99'),minute(1),minute(2)]
    records=execute(bars,[Signal('s',T+timedelta(minutes=1),'LONG')])
    assert records[0]['entry_at']==T+timedelta(minutes=1)
    assert records[0]['status']=='EOD_CLOSE' and records[0]['r_low']==0 and not records[0]['win']

@pytest.mark.parametrize('stop,risk',[('USD030',D('.3')),('USD050',D('.5')),('ATR050',D('.4')),('ATR100',D('.8'))])
def test_stop_sizes(stop,risk):
    records=execute([minute(0)],[Signal('s',T,'LONG',D('.8'))],stop=stop)
    assert records[0]['risk']==risk

def test_atr_no_fallback():
    assert execute([minute(0)],stop='ATR050')[0]['status']=='UNAVAILABLE_ATR'

@pytest.mark.parametrize('direction',['LONG','SHORT'])
def test_intraminute_ambiguity(direction):
    x=execute([minute(0,h='101',l='99')],[Signal('s',T,direction)])[0]
    assert x['status']=='AMBIGUOUS_STOP_TARGET' and x['r_low']==-1 and x['r_high']==1

@pytest.mark.parametrize('bar,reason',[ (minute(0,h='100.4'),'TARGET_TOUCH'),(minute(0,l='99.6'),'STOP_TOUCH')])
def test_touch_order(bar,reason):
    assert execute([bar])[0]['status']==reason

def test_gap_stop_and_target():
    assert execute([minute(0),minute(1,o='99',h='99.1',l='98.9',c='99')])[0]['exit_price']==D(99)
    assert execute([minute(0),minute(1,o='101',h='101.1',l='100.9',c='101')])[0]['exit_price']==D('100.3')

def test_conflicts_no_pyramiding_or_exit_minute_reentry():
    bars=[minute(0),minute(1,h='100.4'),minute(2)]
    x=execute(bars,[Signal('a',T,'LONG'),Signal('b',T+timedelta(minutes=1),'SHORT')])
    assert any(z['status']=='IGNORE_AND_RECORD' for z in x)
    assert len([z for z in x if 'entry' in z])==1
    x=execute([minute(0)],[Signal('a',T,'LONG'),Signal('b',T,'SHORT')])
    assert all(z['status']=='NO_ENTRY_CONFLICT' for z in x)

def test_time_exit_and_early_close():
    x=execute([minute(i) for i in range(20)],exit='TIME_15')[0]
    assert x['exit_at']==T+timedelta(minutes=15) and x['status']=='TIME_OPEN'
    x=execute([minute(i) for i in range(210)],exit='TIME_60',signals=[Signal('late',T+timedelta(minutes=205),'LONG')])[0]
    assert x['exit_at']==T+timedelta(minutes=209) and x['status']=='EOD_CLOSE'

def test_invalid_execution_and_eod_signal():
    with pytest.raises(PermissionError):simulate_session([],[],T,T,'USD030','TARGET_1R')
    with pytest.raises(ValueError):execute([minute(0),minute(2)])
    assert execute([minute(0)],[Signal('s',T+timedelta(minutes=1),'LONG')])[0]['status']=='UNAVAILABLE_ENTRY'

def test_network_and_post_date_audit_guard():
    code="""from spy_research.edge_discovery_v1.safety import install_audit_guard
import socket
install_audit_guard()
for action in (lambda: socket.getaddrinfo('example.com',443),lambda: open('/tmp/2026-09-08.parquet','rb')):
    try: action()
    except (PermissionError,ValueError): pass
    else: raise AssertionError('guard bypassed')
"""
    subprocess.run([sys.executable,'-B','-c',code],check=True)
