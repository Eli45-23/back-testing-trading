"""Offline prospective protocol guards. No outcomes, network or trading actions."""
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path

CANDIDATES=('USD030_TARGET_1.5R','ATR050_TARGET_1R','USD030_TARGET_2R_BE1R')
CONTROL='USD030_TARGET_2R'
MANIFEST=Path('reports/first_hold_prospective_freeze.json')


def verify_freeze(root=Path('.')):
    frozen=json.loads((root/MANIFEST).read_text())
    if tuple(frozen['candidates'])!=CANDIDATES or frozen['control']!=CONTROL:
        raise ValueError('Frozen candidate identity mismatch')
    if (frozen['required_sessions'],frozen['minimum_trades_per_candidate'],frozen['minimum_contributing_sessions'])!=(60,200,40):
        raise ValueError('Frozen sample gates changed')
    for name,expected in frozen['frozen_files'].items():
        if sha256((root/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(f'Frozen baseline changed: {name}')
    return frozen


def readiness(frozen,as_of,validated_sessions,trade_counts,contributing_sessions):
    """Counts must come from validated records; this guard never estimates them.

    Every scheduled session, including zero-signal sessions, must pass coverage.
    Candidate insufficiency never extends the fixed window or changes its rules.
    """
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError('Aware as-of timestamp required')
    days=[s['date'] for s in frozen['sessions']]
    if len(days)!=60 or len(set(days))!=60 or days!=sorted(days):
        raise ValueError('Invalid frozen session inventory')
    completed={s['date'] for s in frozen['sessions'] if datetime.fromisoformat(s['close'])<=as_of}
    validated=list(validated_sessions)
    if len(validated)!=len(set(validated)) or not set(validated)<=completed:
        raise ValueError('Duplicate, outside-window or incomplete session supplied')
    if len(completed)<60:
        return {'status':'INTERIM_NO_SELECTION','completed_sessions':len(completed),'validated_sessions':len(validated),'endpoint':days[-1]}
    if set(validated)!=set(days):
        return {'status':'BLOCKED_DATA_QUALITY','missing_sessions':sorted(set(days)-set(validated))}
    assessments={}
    for candidate in (*CANDIDATES,CONTROL):
        n=trade_counts.get(candidate);s=contributing_sessions.get(candidate)
        if type(n) is not int or type(s) is not int or n<0 or not 0<=s<=60 or s>n:
            raise ValueError('Validated candidate counts required')
        assessments[candidate]='ENDPOINT_REPORT_ELIGIBLE' if n>=200 and s>=40 else 'INSUFFICIENT_PROSPECTIVE_DATA'
    return {'status':'ENDPOINT_REACHED_NO_AUTOMATIC_SELECTION','candidates':assessments}
