# Phase and immutable-manifest contract

DESIGN_FROZEN → DISCOVERY → VALIDATION_BATCH_FROZEN → VALIDATION_COMPLETE → INTERNAL_CONFIRMATION → FINAL_REPORT.

Phase 1 permits synthetic state transitions only. All historical execution APIs reject access regardless of the requested year. Synthetic batch examples live only in test memory; there is no real batch manifest or validation/confirmation receipt at handoff.

All candidates must be frozen simultaneously in one immutable candidate-batch manifest, maximum three, before any candidate-specific 2025 evaluation. Bind complete signal, entry, exits, stop, thresholds, direction, conditions, discovery evidence, dependency fingerprints, protocol hash and input-inventory hash. Pin the canonical batch hash externally. No additions, removals, replacements or unused-slot replenishment afterward.

Every candidate in that batch must finish 2025 validation before confirmation becomes accessible. The immutable validation-completion receipt binds the batch hash, protocol hash, every result, mechanical gate decisions and derived survivor IDs. Recompute gates during receipt verification. Incomplete batches, changed receipts or invented survivors fail closed. Only passing candidates may reach 2026. Confirm every survivor unchanged; no failed/insufficient candidate may advance.

Canonical encoding is UTF-8 JSON, sorted object keys, compact separators, deterministic array order, no binary floating-point values. Decimal values serialize as strings; dates use ISO format. A manifest's digest is outside its own payload. Immutable envelopes hold canonical bytes. Use original file-byte SHA-256 for partitions and source artifacts, and canonical payload SHA-256 for inventories/manifests. Never replace a frozen baseline after a mismatch.

The phase-1 freeze embeds all 672 outcome partition records and the separate context record, their canonical inventory hashes, all package/test/design fingerprints and dependency hashes. The verification receipt is produced after the freeze and is not self-referentially embedded. The freeze_manifest.sha256 file records the externally pinnable digest; later callers must use the approved digest rather than trust a newly edited local digest file.
