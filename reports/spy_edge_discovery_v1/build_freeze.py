"""Phase 1 builder: data-integrity checks and design artifacts only."""
import json
from pathlib import Path
from datetime import date
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
sys.dont_write_bytecode=True
from spy_research.edge_discovery_v1.canonical import canonical_bytes, canonical_hash, Envelope
from spy_research.edge_discovery_v1.protocol import protocol, PROTOCOL_SHA256
from spy_research.edge_discovery_v1.inventory import build_inventory, verify_inventory, file_hash, expected_path
from spy_research.edge_discovery_v1.safety import install_audit_guard
from spy_research.edge_discovery_v1.features import FEATURE_REGISTRY
from spy_research.edge_discovery_v1.walk_forward import FOLDS
from spy_research.edge_discovery_v1.reports import REPORT_FIELDS, ALLOWED_LABELS
from spy_research.edge_discovery_v1.freeze import verify_freeze


def save(name,value):
    (OUT/name).write_bytes(canonical_bytes(value))


def prior_checks():
    from spy_research.break_hold.prospective_freeze import verify_freeze as bh
    from spy_research.rejection_entry_v1.manifest import verify_manifest
    from spy_research.rejection_risk_exit_v1.protocol import protocol_hash as risk_hash
    from spy_research.rejection_prospective_v1.protocol import protocol_hash as prospective_hash
    result={'break_hold':len(bh(ROOT)['frozen_files'])}
    assert result['break_hold']==174
    for directory,count in [('key_level_reactions_v1',15),('key_level_reactions_v1_completed_ae8e870',63),('rejection_entry_study_v1_completed_a3909ea',29),('rejection_risk_exit_study_v1_completed_305f56a',27)]:
        folder=ROOT/'reports'/directory
        manifest=json.loads((folder/'run_manifest.json').read_text())
        assert len(manifest['output_hashes'])==count
        for name,h in manifest['output_hashes'].items():assert file_hash(folder/name)==h,(directory,name)
        result[directory]=count
    verify_manifest(ROOT/'reports/rejection_entry_study_v1/freeze_manifest.json',repository_root=ROOT)
    for directory,ph in [('rejection_risk_exit_study_v1',risk_hash()),('rejection_prospective_validation_v1',prospective_hash())]:
        manifest=json.loads((ROOT/'reports'/directory/'freeze_manifest.json').read_text())
        assert manifest['protocol_sha256']==ph
        for section in ('source_files','dependency_files'):
            for name,h in manifest.get(section,{}).items():assert file_hash(ROOT/name)==h,name
        result[directory+'_protocol']=ph
    return result


def main():
    if (OUT/'freeze_manifest.json').exists():raise RuntimeError('Existing freeze cannot be regenerated')
    accessed=install_audit_guard()
    before=prior_checks()
    tracked=subprocess.check_output(['git','ls-files','-z'],text=True).split('\0')
    protected={p:file_hash(ROOT/p) for p in tracked if p and p.startswith(('src/','tests/','reports/','config/'))}
    # Existing untracked audit histories are protected too, without interpreting results.
    for directory in ('break_hold_2023_acquisition_coverage','break_hold_2024_2026_robustness','rejection_prospective_validation_v1_interim_20260908'):
        for path in (ROOT/'reports'/directory).rglob('*'):
            if path.is_file():protected[str(path.relative_to(ROOT))]=file_hash(path)
    save('prior_fingerprints.json',protected)
    print('Prior freezes verified; building permitted input inventory only',flush=True)
    inventory=build_inventory(ROOT)
    verify_inventory(inventory,inventory.digest,ROOT)
    rows=inventory.verify(inventory.digest)['partitions']
    from spy_research.data.raw_store import RawBarStore
    from spy_research.data.coverage import inventory as coverage_inventory, trading_dates
    from spy_research.config import load_research_config
    from spy_research.market import XNYSCalendar
    config=load_research_config();cal=XNYSCalendar()
    day=date(2023,12,29);path=ROOT/expected_path(day)
    coverage=coverage_inventory(config,RawBarStore(config,root=ROOT/'data/oos/raw'),day,day)
    assert len(coverage)==1 and coverage[0].raw_status=='VALID'
    session=cal.session_for_date(day)
    context_row={'path':expected_path(day),'session_date':str(day),'role':'CONTEXT','byte_size':path.stat().st_size,'sha256':file_hash(path),'coverage_status':'VALID','expected_rth_minutes':390,'observed_rth_minutes':coverage[0].observed_minutes,'market_open':session.market_open.isoformat(),'market_close':session.market_close.isoformat(),'early_close':False}
    assert context_row['sha256']=='8b2c0a9bf608d2b57c73960b8a6d34e0b210c582b998567ac814f5ec7a40f49e'
    context=Envelope.seal({'partitions':[context_row]})
    save('input_inventory.json',{'partitions':rows})
    save('context_inventory.json',{'partitions':[context_row]})
    save('protocol.json',protocol())
    save('feature_registry.json',{'families':FEATURE_REGISTRY,'availability':'completed_data_only','unavailable':'explicit_no_fallback','new_families_after_freeze':False})
    folds=[]
    for name,start,end,eval_start,eval_end in FOLDS:
        folds.append({'name':name,'training_start':str(start),'training_end':str(end),'evaluation_start':str(eval_start),'evaluation_end':str(eval_end),'training_sessions':[str(x) for x in trading_dates(start,end,cal)],'evaluation_sessions':[str(x) for x in trading_dates(eval_start,eval_end,cal)],'purge':'exclude_training_labels_extending_past_training_end','reused_fold_status':'development_not_independent_holdout'})
    save('walk_forward_calendar.json',{'folds':folds})
    save('search_ledger_schema.json',{'record_types':{'hypothesis':['predicate','thresholds','direction','cadence','primary_horizon','expected_effect','conditions'],'strategy':['signal','entry','stop','exit','thresholds','direction','conditions'],'result':['specification_id','atomic_comparisons','result','rejection_reason']},'common':['registered_at','parent','previous_hash'],'budgets':protocol()['budgets'],'append_only':True,'changed_specification_consumes_slot':True,'identical_rerun_consumes_slot':False,'every_inspected_contrast_counted':True})
    save('endpoint_report_schema.json',{'required_fields':REPORT_FIELDS,'allowed_labels':sorted(ALLOWED_LABELS),'historical_survivor':'ROBUST_EDGE_CANDIDATE','stronger_deployment_conclusion':False})
    save('phase_state.json',{'phase':'DESIGN_FROZEN','real_validation_batch':None,'historical_edge_outcomes':0,'candidate_2025_evaluations':0,'candidate_2026_evaluations':0})
    package=ROOT/'src/spy_research/edge_discovery_v1'
    source_files={str(p.relative_to(ROOT)):file_hash(p) for p in sorted(package.glob('*.py'))}
    test=ROOT/'tests/unit/test_edge_discovery_v1.py';source_files[str(test.relative_to(ROOT))]=file_hash(test)
    source_files[str(Path(__file__).relative_to(ROOT))]=file_hash(__file__)
    dependencies={p:h for p,h in protected.items() if p.startswith(('src/','config/')) or p.endswith('freeze_manifest.json') or p=='reports/first_hold_prospective_freeze.json'}
    design_files={str(p.relative_to(ROOT)):file_hash(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='build_freeze.py'}
    manifest={'version':'spy-autonomous-edge-discovery-v1-phase1','phase':'DESIGN_FROZEN','historical_outcomes_enabled':False,'protocol_sha256':PROTOCOL_SHA256,'source_files':source_files,'dependency_files':dependencies,'design_files':design_files,'input_partitions':rows,'input_inventory_sha256':inventory.digest,'context_partitions':[context_row],'context_inventory_sha256':context.digest,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'prior_verification':before}
    save('freeze_manifest.json',manifest)
    frozen_hash=canonical_hash(manifest)
    (OUT/'freeze_manifest.sha256').write_text(frozen_hash+'\n')
    verify_freeze(ROOT,'reports/spy_edge_discovery_v1/freeze_manifest.json',frozen_hash)
    assert prior_checks()==before
    assert all(file_hash(ROOT/p)==h for p,h in protected.items())
    save('build_verification.json',{'protocol_hash':PROTOCOL_SHA256,'freeze_manifest_hash':frozen_hash,'input_inventory_hash':inventory.digest,'context_inventory_hash':context.digest,'context_partition_hash':context_row['sha256'],'coverage_counts':{'2024':252,'2025':250,'2026':170,'total':672},'outcome_rth_minutes':261000,'prior_freezes':before,'protected_files_unchanged':len(protected),'historical_edge_outcomes':0,'candidate_2025_evaluations':0,'candidate_2026_evaluations':0,'post_sep4_market_access':0,'network_broker_activity':0,'market_files_accessed':sorted(accessed)})
    print(json.dumps({'protocol_hash':PROTOCOL_SHA256,'freeze_manifest_hash':frozen_hash,'input_inventory_hash':inventory.digest,'context_inventory_hash':context.digest,'coverage':'672/672','prior_freezes':before}),flush=True)

if __name__=='__main__':main()
