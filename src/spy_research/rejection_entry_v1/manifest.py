"""Freeze-manifest helpers for the design-only Rejection Entry V1 phase."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
import hashlib
import json

from .models import StudyManifest
from .protocol import EntryFamily, LEVEL_FAMILIES, OUTCOME_END, OUTCOME_START, PROSPECTIVE_START, protocol_hash


def build_manifest(*, klr_protocol_hash: str, source_files: Iterable[str]) -> StudyManifest:
    return StudyManifest(
        version="rejection-entry-study-v1",
        protocol_hash=protocol_hash(),
        klr_protocol_hash=klr_protocol_hash,
        outcome_start=OUTCOME_START,
        outcome_end=OUTCOME_END,
        prospective_excluded_from=PROSPECTIVE_START,
        level_families=tuple(LEVEL_FAMILIES),
        entry_families=tuple(EntryFamily),
        source_files=tuple(sorted(source_files)),
        outcome_run_performed=False,
    )


def source_paths(package_root: Path) -> tuple[str, ...]:
    return tuple(sorted(str(path.relative_to(package_root)) for path in package_root.rglob("*.py")))


def verify_manifest(path: Path, *, repository_root: Path) -> dict:
    """Verify a design manifest and source fingerprints without touching data."""
    payload = json.loads(path.read_text())
    if payload.get("version") != "rejection-entry-study-v1" or payload.get("outcome_run_performed"):
        raise ValueError("manifest is not a design-only freeze")
    if payload.get("protocol_hash") != protocol_hash():
        raise ValueError("protocol hash mismatch")
    hashes = payload.get("source_file_hashes", {})
    listed = tuple(payload.get("source_files", ()))
    if set(hashes) != set(listed):
        raise ValueError("source fingerprint list mismatch")
    for relative, expected in hashes.items():
        actual = hashlib.sha256((repository_root / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"source fingerprint mismatch: {relative}")
    return payload
