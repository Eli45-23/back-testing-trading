"""Immutable, hash-chained search ledger. Every changed specification costs a slot."""
from dataclasses import dataclass
from .canonical import Envelope, canonical_hash


@dataclass(frozen=True)
class SearchLedger:
    entries: tuple[Envelope, ...] = ()

    def verify(self):
        previous = None
        for item in self.entries:
            data = item.verify(item.digest)
            if data['previous_hash'] != previous: raise ValueError('ledger chain mismatch')
            previous = item.digest

    def register(self, kind, specification, registered_at, parent=None):
        self.verify()
        if kind not in ('hypothesis', 'strategy'): raise ValueError('unknown search kind')
        if registered_at.utcoffset() is None: raise ValueError('aware registration time required')
        required = ('predicate', 'thresholds', 'direction', 'cadence', 'primary_horizon', 'expected_effect', 'conditions') if kind == 'hypothesis' else ('signal', 'entry', 'stop', 'exit', 'thresholds', 'direction', 'conditions')
        if any(k not in specification for k in required) or not 1 <= len(specification['conditions']) <= 3:
            raise ValueError('incomplete specification or condition budget exceeded')
        if kind == 'strategy':
            from .protocol import protocol
            p = protocol()
            if specification['stop'] not in p['stops'] or specification['exit'] not in p['exits']:
                raise ValueError('unapproved risk/exit family')
            if specification['entry'] != p['execution']['entry']: raise ValueError('entry convention changed')
        identity = canonical_hash({'kind': kind, 'specification': specification})
        data = [e.verify(e.digest) for e in self.entries]
        if any(e.get('specification_id') == identity for e in data): return self, identity
        if sum(e['kind'] == kind for e in data) >= (100 if kind == 'hypothesis' else 60): raise ValueError('search budget exhausted')
        if parent is not None and not any(e.get('specification_id') == parent for e in data): raise ValueError('unknown parent')
        item = Envelope.seal({'kind': kind, 'specification': specification, 'specification_id': identity, 'registered_at': registered_at.isoformat(), 'parent': parent, 'previous_hash': self.entries[-1].digest if self.entries else None})
        return SearchLedger(self.entries + (item,)), identity

    def record(self, identity, *, atomic_comparisons, result, rejection_reason=None):
        self.verify()
        if type(atomic_comparisons) is not int or atomic_comparisons < 0: raise ValueError('comparison count required')
        if not any(e.verify(e.digest).get('specification_id') == identity for e in self.entries): raise ValueError('unregistered experiment')
        item = Envelope.seal({'kind': 'result', 'specification_id': identity, 'atomic_comparisons': atomic_comparisons, 'result': result, 'rejection_reason': rejection_reason, 'previous_hash': self.entries[-1].digest})
        return SearchLedger(self.entries + (item,))

    @property
    def atomic_comparisons(self):
        return sum(e.verify(e.digest).get('atomic_comparisons', 0) for e in self.entries)
