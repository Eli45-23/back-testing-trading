"""Synthetic-only state transitions; no Phase 1 historical evaluation route."""
from dataclasses import asdict, dataclass, replace
from .canonical import Envelope
from .gates import Evidence, evaluate
from .protocol import PROTOCOL_SHA256


@dataclass(frozen=True)
class ResearchState:
    phase: str = 'DESIGN_FROZEN'
    batch: Envelope | None = None
    batch_hash: str | None = None
    receipt: Envelope | None = None
    receipt_hash: str | None = None
    confirmation: tuple = ()

    def discovery(self, *, synthetic=False):
        if not synthetic: raise PermissionError('historical discovery disabled in Phase 1')
        if self.phase != 'DESIGN_FROZEN': raise ValueError('invalid transition')
        return replace(self, phase='DISCOVERY')

    def freeze_batch(self, candidates, inventory_hash, dependencies, *, synthetic=False):
        if not synthetic: raise PermissionError('real candidate batches prohibited in Phase 1')
        if self.phase != 'DISCOVERY' or self.batch is not None: raise ValueError('batch already frozen or invalid phase')
        if not 1 <= len(candidates) <= 3: raise ValueError('one to three candidates required; no placeholder batch')
        ids = [x['id'] for x in candidates]
        if len(ids) != len(set(ids)): raise ValueError('duplicate candidate')
        for c in candidates:
            required = ('id','signal','entry','exit','stop','thresholds','direction','conditions','discovery_evidence_hash')
            if any(k not in c for k in required): raise ValueError('incomplete candidate specification')
            from .protocol import protocol
            p = protocol()
            if c['stop'] not in p['stops'] or c['exit'] not in p['exits'] or c['entry'] != p['execution']['entry'] or not 1 <= len(c['conditions']) <= 3: raise ValueError('candidate violates frozen execution universe')
        if not inventory_hash or not dependencies: raise ValueError('inventory/dependencies required')
        batch = Envelope.seal({'synthetic': True, 'candidates': sorted(candidates, key=lambda x:x['id']), 'inventory_hash': inventory_hash, 'dependencies': dependencies, 'protocol_hash': PROTOCOL_SHA256, 'reserved_slots': 3})
        return replace(self, phase='VALIDATION_BATCH_FROZEN', batch=batch, batch_hash=batch.digest)

    def verified_batch(self):
        if self.batch is None or self.batch_hash is None: raise ValueError('batch hash required before validation')
        batch = self.batch.verify(self.batch_hash)
        if batch['protocol_hash'] != PROTOCOL_SHA256 or batch['synthetic'] is not True: raise ValueError('wrong batch protocol/domain')
        return batch

    def authorize(self, year, candidate, *, synthetic=False):
        if not synthetic: raise PermissionError('historical candidate evaluation disabled in Phase 1')
        if year not in (2025, 2026): raise ValueError('unsupported candidate year')
        batch = self.verified_batch()
        if candidate not in {c['id'] for c in batch['candidates']}: raise ValueError('candidate not in frozen batch')
        if year == 2025:
            if self.phase != 'VALIDATION_BATCH_FROZEN': raise ValueError('validation phase closed')
        else:
            if self.phase != 'INTERNAL_CONFIRMATION': raise ValueError('premature confirmation')
            receipt = self.verified_receipt()
            if candidate not in receipt['survivors']: raise ValueError('failed/insufficient candidate cannot advance')

    def complete_validation(self, results, *, synthetic=False):
        if not synthetic: raise PermissionError('historical validation disabled')
        if self.phase != 'VALIDATION_BATCH_FROZEN': raise ValueError('wrong phase')
        batch = self.verified_batch()
        if set(results) != {c['id'] for c in batch['candidates']}: raise ValueError('entire validation batch must complete')
        decisions = {k:evaluate(v,'VALIDATION') for k,v in sorted(results.items())}
        receipt = Envelope.seal({'batch_hash': self.batch_hash, 'protocol_hash': PROTOCOL_SHA256, 'results': {k:asdict(v) for k,v in sorted(results.items())}, 'decisions': decisions, 'survivors': [k for k,v in decisions.items() if v['passed']]})
        return replace(self, phase='VALIDATION_COMPLETE', receipt=receipt, receipt_hash=receipt.digest)

    def verified_receipt(self):
        from decimal import Decimal
        if self.receipt is None: raise ValueError('validation receipt required')
        data = self.receipt.verify(self.receipt_hash)
        batch = self.verified_batch()
        if data['batch_hash'] != self.batch_hash or data['protocol_hash'] != PROTOCOL_SHA256: raise ValueError('receipt binding mismatch')
        if set(data['results']) != {c['id'] for c in batch['candidates']}: raise ValueError('incomplete receipt')
        decisions = {}
        for key, value in data['results'].items():
            typed = {k:Decimal(v) if isinstance(v,str) else v for k,v in value.items()}
            decisions[key] = evaluate(Evidence(**typed),'VALIDATION')
        survivors = sorted(k for k,v in decisions.items() if v['passed'])
        if data['decisions'] != decisions or data['survivors'] != survivors: raise ValueError('nonmechanical survivor advancement')
        return data

    def begin_confirmation(self):
        if self.phase != 'VALIDATION_COMPLETE': raise ValueError('entire batch not complete')
        self.verified_receipt()
        return replace(self, phase='INTERNAL_CONFIRMATION')

    def finish(self, results, *, synthetic=False):
        if not synthetic: raise PermissionError('historical confirmation disabled')
        if self.phase != 'INTERNAL_CONFIRMATION': raise ValueError('wrong phase')
        receipt = self.verified_receipt()
        if set(results) != set(receipt['survivors']): raise ValueError('exact survivor confirmation set required')
        labels = tuple((key, 'ROBUST_EDGE_CANDIDATE' if evaluate(e,'INTERNAL_CONFIRMATION')['passed'] else 'INTERNAL_CONFIRMATION_FAIL') for key,e in sorted(results.items()))
        return replace(self, phase='FINAL_REPORT', confirmation=labels)
