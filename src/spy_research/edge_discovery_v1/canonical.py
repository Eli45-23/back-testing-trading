"""Canonical, immutable JSON envelopes with externally pinned SHA-256."""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json


def canonical_bytes(value):
    def clean(x):
        if isinstance(x, float):
            raise TypeError('binary floats are forbidden in canonical manifests')
        if isinstance(x, Decimal):
            if not x.is_finite(): raise ValueError('nonfinite decimal')
            return str(x)
        if isinstance(x, dict):
            if any(not isinstance(k, str) for k in x): raise TypeError('string keys required')
            return {k: clean(v) for k, v in x.items()}
        if isinstance(x, (tuple, list)): return [clean(v) for v in x]
        if x is None or type(x) in (str, int, bool): return x
        raise TypeError(type(x).__name__)
    return json.dumps(clean(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def canonical_hash(value):
    return sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class Envelope:
    """Payload is bytes, so nested caller-owned dictionaries cannot mutate it."""
    payload: bytes
    digest: str

    @classmethod
    def seal(cls, value):
        payload = canonical_bytes(value)
        return cls(payload, sha256(payload).hexdigest())

    def verify(self, expected):
        if self.digest != expected or sha256(self.payload).hexdigest() != expected:
            raise ValueError('canonical manifest hash mismatch')
        value = json.loads(self.payload)
        if canonical_bytes(value) != self.payload: raise ValueError('noncanonical payload')
        return value
