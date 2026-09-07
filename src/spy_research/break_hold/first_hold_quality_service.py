"""Offline read-only orchestration; canonical identities are never redetected."""
from datetime import timedelta
from hashlib import sha256
import json
from pathlib import Path

from spy_research.bars.aggregation import aggregate_rth_1m_to_5m
from spy_research.break_hold.service import BreakHoldReport
from spy_research.break_hold.entry_timing_analysis import verify_canonical
from spy_research.break_hold.executable_reference import measure_executable_hold
from spy_research.break_hold.first_hold_features import extract_first_hold_features
from spy_research.break_hold.first_hold_quality_analysis import analyze_features, executable_comparison
from spy_research.config import ResearchConfig
from spy_research.data.raw_store import RawBarStore
from spy_research.market import MarketSessionClassifier, XNYSCalendar

CANONICAL_SHA='6aaf9980ecd7798420151a8b97436311eca6429e9f31fdb33be1ed86c8c47148'


def run_quality_study(path=Path('reports/break_hold_2026_v1.json'),progress=print):
    content=path.read_bytes()
    if sha256(content).hexdigest()!=CANONICAL_SHA:
        raise ValueError('STOP: frozen canonical JSON fingerprint changed')
    canonical=BreakHoldReport.model_validate_json(content)
    verify_canonical(canonical)
    config=ResearchConfig.model_validate(json.loads(canonical.effective_config_json)['research'])
    store=RawBarStore(config)
    calendar=XNYSCalendar();classifier=MarketSessionClassifier(calendar)
    features=[];executable=[];lineage=[]
    for i,facts in enumerate(canonical.sessions):
        session=calendar.session_for_date(facts.session_date)
        raw=store.load_partition(facts.session_date)
        classified=classifier.classify_many(raw)
        rth=tuple(b.bar for b in classified if b.session_type=='RTH')
        expected=tuple(session.market_open+timedelta(minutes=j) for j in range(int((session.market_close-session.market_open).total_seconds()//60)))
        if tuple(b.timestamp for b in rth)!=expected:
            raise ValueError(f'STOP: incomplete/nonunique RTH coverage {facts.session_date}')
        bars=aggregate_rth_1m_to_5m(classified,session)
        # Features first. Outcome labels are not passed into the extractor.
        for event in facts.events:
            if event.first_hold is not None:
                features.append(extract_first_hold_features(event.first_hold,bars,session))
        for event in facts.events:
            for signal in (event.first_hold,event.strong_hold):
                if signal is not None:
                    executable.append(measure_executable_hold(signal,rth,session,reclaim_timestamp=event.reclaim_timestamp))
        raw_path=store.partition_path(facts.session_date)
        lineage.append(dict(session_date=facts.session_date,path=str(raw_path),sha256=sha256(raw_path.read_bytes()).hexdigest(),rth_minutes=len(rth),five_minute_bars=len(bars)))
        if i%25==0:progress(f'Completed session {i+1}/170; feature rows {len(features)}')
    labels={e.event_id:'EVENTUAL_STRONG' if e.strong_hold else 'NEVER_STRONG' for s in canonical.sessions for e in s.events if e.first_hold}
    days=sorted(s.session_date for s in canonical.sessions)
    close_first={o.signal.event_id:o for o in canonical.outcomes if o.signal.entry_style=='FIRST_HOLD'}
    exec_first={o.signal.event_id:o for o in executable if o.signal.entry_style=='FIRST_HOLD'}
    progress('Calculating fixed paired comparisons and whole-session uncertainty')
    references=executable_comparison(executable,canonical.outcomes,days)
    progress('Comparing 70 continuous and 16 categorical feature fields; no model fitting')
    result=analyze_features(features,labels,close_first,exec_first,days)
    result.update(version='first_hold_quality_analysis_v1',canonical_sha256=CANONICAL_SHA,
        definition_hash=canonical.definition_hash,input_manifest_hash=canonical.input_manifest_hash,
        counts=dict(sessions=170,breaks=1435,first_holds=733,eventual_strong=524,never_strong=209),
        settings=dict(bootstrap_repetitions=10000,bootstrap_seed=20260907,relative_volume_lookback=6,
            stage11_1_status='UNAVAILABLE_CALIBRATION_PROVENANCE',thresholds=('0.25/0.25','0.50/0.25','0.50/0.30','1.00/0.30')),
        references=references,lineage=lineage,executable_outcomes=[o.model_dump(mode='json') for o in executable])
    return result
