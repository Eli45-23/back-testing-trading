# Stage 15.1 Verification — August 31, 2026

## Execution safety

- Stage 14 live PAPER processes: `0`
- Alpaca connections made by Stage 15.1: `0`
- PAPER orders submitted: `0`
- Stage 14 candidate/execution changes: none
- Stage 14.5 started: no
- Commit/push performed: no

## Repository and tests

- Local HEAD: `fbbe86c0f9e56be3635aa114a3a848f89cefe537`
- Tracking branch: `fbbe86c0f9e56be3635aa114a3a848f89cefe537`
- Remote `main`: `fbbe86c0f9e56be3635aa114a3a848f89cefe537`
- Full suite: `1,056 passed`
- Combined focused Stage 15/15.1 tests: `16 passed`
- New Stage 15.1 focused tests: `7 passed`
- Compilation/import/CLI parse: pass
- `pip check`: pass
- Isolated wheel installation/import: pass
- `git diff --check`: pass
- Changed-scope credential scan: pass
- Changed-scope endpoint/TLS scan: pass
- Changed-scope one-entry/session guard scan: pass
- Generated wheel build directory removed from the workspace after verification

## Historical equivalence and deterministic hashes

- Historical shadow equivalence: `2,080/2,080 exact`, `0 mismatches`
- Stage 14.4: `3de987672bc6cc73c39c643f6bd656daefdcbe32e0e6ce3c830405ab8eee183b`
- Stage 14.3: `0ffe7b13ac722eff31d7c9d8c0ec615f62099c0b32fba35ec3a947d03bff61c0`
- Stage 14.2: `ee1b0734f7097244a1acad4219b0a8eb52cb3706c3791eddd47f0b0fb5705484`
- Stage 14.1: `50a63cda64e2be8e26b29eee66258fa8bef68d5c462a3a10d59bda9d553561da`
- Stage 13.3: `0b4ee82656230d89d8ca6d3d29ba3b73d7a7281c701e44ae5c4a11373712ef72`
- Stage 13.2: `fd4378d75ca39e56d55b80c68f7e38e24b73f2bd946074fbc0ce525c64a3d0b2`
- Stage 13.1: `b25a8e32756257d785316902259b8f6be7db384eb18f32c82c374a36737ec1ff`
- Stage 15 report: `f6ea0ed5e0166e41defcb92abd03ee70093fffeeb4b941a52bd0ff97fa3bd9df`
- Stage 15.1 report: `082ea45136f0630013ed6aa35acc41b748946f582ab412cbc5fa2cce1e3e09be`

Stage 15.1 rebuilt the Stage 13.2 execution population and reconciled its
accepted source hash before analysis. The full deterministic regression suite
reconfirmed the accepted Stage 13/14 fixtures, no participating Stage 13/14
source changed, and the independent Stage 14.3 minute replay matched every
accepted path exactly.

## Store manifests

- Raw, 158 files: `6ef301e72bb6e2d4ac1616f4bdaf971ab569270b6f81f79bf1c97aec8a06ad05`
- Processed, 158 files: `ae26d7553238e3cf92206e3238ac0bf60f4c59210283f362dfd989eea96bf014`

Both match the accepted manifests.

## Stage 15/15.1 result integrity

- Frozen membership: `1,040`
- Realized primary outcomes: `589`
- Explicit unavailable/ambiguous outcomes: `451`
- Stage 15 single-factor partitions: exact for all `1,040` observations
- Stage 15 predeclared interaction partitions: exact for all `1,040` observations
- Frozen Stage 15 condition counts, exact mean R values, and BH q-values: reconciled
- Stage 15.1 variants evaluated: exactly `10`
- Condition overlap cells: exactly `16`
- Baseline and control-row metric objects: exactly equal
- Additional combinations or learned thresholds searched: none

## Review state

The worktree intentionally contains the uncommitted Stage 15 and Stage 15.1
implementation, tests, and reports for review. No commit or push was performed.
Stage 14 remains paused and unchanged.
