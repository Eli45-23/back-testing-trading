# Phase 1 implementation and freeze verification

Status: DESIGN_FROZEN. No historical discovery or candidate evaluation was performed. No real validation candidate batch exists. The synthetic tests exercise state transitions entirely in memory.

## Tests and isolation

- Focused regressions: **62 passed**.
- Full suite: **1,368 passed**; independently repeated under network/prospective-partition access guards, **1,368 passed in 6.94 seconds**.
- Real network attempts during the guarded suite: **0**.
- Forbidden real prospective-partition attempts during the guarded suite: **0**.
- Historical edge outcomes calculated: **0**.
- Candidate-specific 2025 evaluations: **0**.
- Candidate-specific 2026 evaluations: **0**.
- September 8+ market-data access: **0**.
- Broker activity: **0**.
- No tracked files modified; no staging, commits or pushes.

Tests cover canonical and partition tampering, context/outcome role violations, incomplete inventories, budget exhaustion, immutable batches, premature validation/confirmation, failed-candidate exclusion, forged survivors, gate boundaries, forbidden labels, completed-data timing, training-prefix isolation, fold purging, shared session resampling, Decimal stops, ATR absence, gaps, ambiguity, position conflicts, EOD/early-close handling and blocked network/date access.

## Coverage and hashes

| Role | Valid sessions | RTH minutes |
|---|---:|---:|
| 2024 discovery | 252/252 | 97,740 |
| 2025 validation | 250/250 | 96,960 |
| 2026 through September 4 internal confirmation | 170/170 | 66,300 |
| Outcome inventory total | 672/672 | 261,000 |
| December 29, 2023 context only | 1/1 | 390 |

Protocol canonical SHA-256:
`3e05faefba33778517bfddbc8903ef4dd6b20e1f24c1f8759d19ac7db2c497aa`

Freeze-manifest canonical SHA-256:
`4ef39b64a0681dc7456165314d241026b1faed31d66b1bc6fedecd957ea667dd`

672-partition canonical inventory SHA-256:
`ee09181893cc46edd3a2399b07ca404a3ed6d4b83560c8706f5d17f2bbf7301d`

Context inventory canonical SHA-256:
`4d5ef9665917bfdb062abb38fffeaa8ad7e81af26fcc422ff79c580ad5fe90a4`

December 29, 2023 original partition SHA-256:
`8b2c0a9bf608d2b57c73960b8a6d34e0b210c582b998567ac814f5ec7a40f49e`

All partition records include original byte size and SHA-256, relative path, session date, role, coverage status, expected/observed RTH minutes, UTC boundaries and early-close status. Outcome inventory and context inventory are separately bound into the freeze. Later verification pins the approved freeze digest rather than trusting an edited local digest file.

## Prior research and dependencies

- Break-and-Hold: **174/174** frozen hashes.
- KLR blocked/completed archives: **15/15**, **63/63**.
- Rejection Entry archive: **29/29**.
- Rejection Risk/Exit archive: **27/27**.
- Rejection Entry source fingerprints and protocol: verified.
- Rejection Risk/Exit protocol: `4836afdeb0d4e2db8eafeb16ed4a818b49a85284d43ea9ee0b420fc195f1a15a`.
- Rejection Prospective protocol: `7347b8ca847a9b460fc09cf80bec8d636b1d6a350ddabedb5277fa39458dc066`.
- **493** existing tracked/untracked research/source/config/test artifacts matched their pre-build fingerprints, including Stage 14, prior blocked receipts and the completed robustness study.
- Phase 1 freeze verifies **16 source/test/builder fingerprints**, **205 dependency fingerprints**, and **13 design-artifact fingerprints**.

The post-build verification receipts and this report are deliberately outside the canonical freeze payload to avoid self-reference. The implementation, tests, protocol and complete input inventories are inside its fingerprint scope.

## Exact new files

Package: `src/spy_research/edge_discovery_v1/`

```text
__init__.py
canonical.py
execution.py
features.py
freeze.py
gates.py
inventory.py
ledger.py
phases.py
protocol.py
reports.py
safety.py
statistics.py
walk_forward.py
```

Design/freeze directory: `reports/spy_edge_discovery_v1/`

```text
build_freeze.py
build_verification.json
context_inventory.json
endpoint_report_schema.json
execution_rules.md
feature_registry.json
freeze_manifest.json
freeze_manifest.sha256
gates_and_statistics.md
input_inventory.json
phase_and_freeze_contract.md
phase_state.json
prior_fingerprints.json
protocol.json
protocol.md
search_ledger_schema.json
verification.md
walk_forward_calendar.json
```

Regression file: `tests/unit/test_edge_discovery_v1.py`.

Total: **33 new files**. Existing source and prior research remain unchanged. This is a design/guard/execution-harness freeze, not a historical discovery run or a claim that a trading edge exists.
