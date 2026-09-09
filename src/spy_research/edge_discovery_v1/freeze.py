"""Externally pinned design/dependency/input verification, without outcomes."""
from pathlib import Path
from .canonical import Envelope, canonical_hash
from .inventory import file_hash, verify_inventory
from .protocol import PROTOCOL_SHA256


def verify_freeze(root, manifest_path, expected_hash):
    root=Path(root)
    envelope=Envelope((root/manifest_path).read_bytes(),expected_hash)
    data=envelope.verify(expected_hash)
    if data['protocol_sha256']!=PROTOCOL_SHA256 or data['phase']!='DESIGN_FROZEN' or data['historical_outcomes_enabled'] is not False:
        raise ValueError('invalid design freeze')
    for section in ('source_files','dependency_files','design_files'):
        for name,h in data[section].items():
            target=(root/name).resolve()
            if not target.is_relative_to(root.resolve()) or file_hash(target)!=h: raise ValueError('frozen dependency changed')
    inventory=Envelope.seal({'partitions':data['input_partitions']})
    if inventory.digest!=data['input_inventory_sha256']:raise ValueError('input inventory canonical hash mismatch')
    verify_inventory(inventory,inventory.digest,root)
    context=Envelope.seal({'partitions':data['context_partitions']})
    if context.digest!=data['context_inventory_sha256']:raise ValueError('context inventory hash mismatch')
    verify_inventory(context,context.digest,root,require_complete=False)
    if len(data['context_partitions'])!=1 or data['context_partitions'][0]['role']!='CONTEXT':raise ValueError('context scope changed')
    return data
