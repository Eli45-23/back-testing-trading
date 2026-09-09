"""Hash/coverage reads only; candidate outcome access is disabled in Phase 1."""
from datetime import date
from hashlib import sha256
from pathlib import Path
from .canonical import Envelope


def role_for(day):
    if day == date(2023, 12, 29): return 'CONTEXT'
    if date(2024, 1, 2) <= day <= date(2024, 12, 31): return 'DISCOVERY'
    if date(2025, 1, 2) <= day <= date(2025, 12, 31): return 'VALIDATION'
    if date(2026, 1, 2) <= day <= date(2026, 9, 4): return 'INTERNAL_CONFIRMATION'
    raise ValueError('unauthorized market date')


def expected_path(day):
    role_for(day)
    root = 'data/raw' if day.year == 2026 else 'data/oos/raw'
    return f'{root}/alpaca/spy/1min/{day:%Y/%m}/{day.isoformat()}.parquet'


def file_hash(path):
    h = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def verify_inventory(envelope, expected_hash, root, *, require_complete=True):
    data = envelope.verify(expected_hash)
    entries = data['partitions']
    paths, days = set(), set()
    for row in entries:
        day = date.fromisoformat(row['session_date'])
        if row['path'] in paths or day in days: raise ValueError('duplicate inventory entry')
        paths.add(row['path']); days.add(day)
        if row['role'] != role_for(day) or row['path'] != expected_path(day): raise ValueError('partition role/path mismatch')
        if row['coverage_status'] != 'VALID': raise ValueError('invalid coverage')
        candidate = Path(root) / row['path']
        if candidate.is_symlink() or not candidate.resolve().is_relative_to(Path(root).resolve()): raise ValueError('unsafe partition path')
        if not candidate.is_file() or candidate.stat().st_size != row['byte_size'] or file_hash(candidate) != row['sha256']:
            raise ValueError('missing or changed partition')
    if entries != sorted(entries, key=lambda x: x['session_date']): raise ValueError('noncanonical inventory order')
    if require_complete:
        from spy_research.market import XNYSCalendar
        from spy_research.data.coverage import trading_dates
        expected = set(trading_dates(date(2024, 1, 2), date(2026, 9, 4), XNYSCalendar()))
        if days != expected or len(entries) != 672: raise ValueError('complete outcome inventory required')
    return data


def verified_partition(envelope, expected_hash, root, day, requested_role, *, purpose):
    actual_role = role_for(day)
    if actual_role != requested_role: raise ValueError('context/outcome role violation')
    if purpose not in ('HASH_VERIFY', 'COVERAGE_VALIDATE'): raise PermissionError('Phase 1 prohibits historical outcome access')
    data = envelope.verify(expected_hash)
    rows = [row for row in data['partitions'] if row['session_date'] == day.isoformat()]
    if len(rows) != 1: raise ValueError('missing/duplicate inventory identity')
    verify_inventory(Envelope.seal({'partitions': rows}), Envelope.seal({'partitions': rows}).digest, root, require_complete=False)
    return Path(root) / rows[0]['path']


def build_inventory(root):
    from spy_research.config import load_research_config
    from spy_research.data.coverage import inventory
    from spy_research.data.raw_store import RawBarStore
    import pyarrow.parquet as pq
    config = load_research_config(Path(root) / 'config/research.yaml')
    rows = []
    for year, end, count in ((2024, date(2024,12,31),252),(2025,date(2025,12,31),250),(2026,date(2026,9,4),170)):
        store = RawBarStore(config, root=Path(root) / ('data/raw' if year == 2026 else 'data/oos/raw'))
        coverage = inventory(config, store, date(year,1,2), end)
        if len(coverage) != count: raise ValueError('calendar count mismatch')
        for item in coverage:
            if item.raw_status != 'VALID' or item.expected_minutes != item.observed_minutes: raise ValueError('BLOCKED_DATA_QUALITY')
            path = store.partition_path(item.session_date)
            metadata = pq.read_schema(path).metadata or {}
            if any(metadata.get(k.encode()) != v.encode() for k,v in {'symbol':'SPY','source':'alpaca','feed':'sip','timeframe':'1Min','adjustment':'raw'}.items()): raise ValueError('metadata mismatch')
            from spy_research.market import XNYSCalendar
            session = XNYSCalendar().session_for_date(item.session_date)
            rows.append({'path': expected_path(item.session_date), 'session_date': item.session_date.isoformat(), 'role': role_for(item.session_date), 'byte_size': path.stat().st_size, 'sha256': file_hash(path), 'coverage_status': 'VALID', 'expected_rth_minutes': item.expected_minutes, 'observed_rth_minutes': item.observed_minutes, 'market_open': session.market_open.isoformat(), 'market_close': session.market_close.isoformat(), 'early_close': session.is_early_close})
    if sum(x['expected_rth_minutes'] for x in rows) != 261000: raise ValueError('minute totals mismatch')
    return Envelope.seal({'partitions': rows})
