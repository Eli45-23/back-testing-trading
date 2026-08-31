# Stage 15 Verification — August 31, 2026

## Execution safety

- Stage 14 live PAPER processes: `0`
- Alpaca/network calls made by Stage 15: `0`
- PAPER orders submitted: `0`
- Stage 14 source diff: none
- Stage 14.5 started: no
- Commit/push performed: no

## Repository and tests

- Local HEAD: `fbbe86c0f9e56be3635aa114a3a848f89cefe537`
- Tracking branch: `fbbe86c0f9e56be3635aa114a3a848f89cefe537`
- Remote `main`: `fbbe86c0f9e56be3635aa114a3a848f89cefe537`
- Full suite: `1,049 passed`
- New focused Stage 15 tests: `9 passed`
- Focused Stage 14 replay/live/shadow/paper hash regression tests: `33 passed`
- Compilation/import/CLI parse: pass
- `pip check`: pass
- `git diff --check`: pass
- Changed-diff credential/endpoint scan: pass
- Stage 15 network/PAPER/session-cap scan: pass

## Historical equivalence and deterministic hashes

- Historical shadow equivalence: `2,080/2,080 exact`, `0 mismatches`
- Stage 14.4: `3de987672bc6cc73c39c643f6bd656daefdcbe32e0e6ce3c830405ab8eee183b`
- Stage 14.3: `0ffe7b13ac722eff31d7c9d8c0ec615f62099c0b32fba35ec3a947d03bff61c0`
- Stage 14.2: `ee1b0734f7097244a1acad4219b0a8eb52cb3706c3791eddd47f0b0fb5705484`
- Stage 14.1: `50a63cda64e2be8e26b29eee66258fa8bef68d5c462a3a10d59bda9d553561da`
- Stage 13.3: `0b4ee82656230d89d8ca6d3d29ba3b73d7a7281c701e44ae5c4a11373712ef72`
- Stage 13.2: `fd4378d75ca39e56d55b80c68f7e38e24b73f2bd946074fbc0ce525c64a3d0b2`
- Stage 13.1: `b25a8e32756257d785316902259b8f6be7db384eb18f32c82c374a36737ec1ff`

Stage 13.1, 13.2, 13.3, 14.1, and 14.3 were freshly reconstructed from the accepted stores. Stage 14.2 and 14.4 are live/PAPER report fixtures and were reconfirmed by their deterministic regression tests. No source file participating in any accepted Stage 13/14 hash was modified.

## Store manifests

- Raw, 158 files: `6ef301e72bb6e2d4ac1616f4bdaf971ab569270b6f81f79bf1c97aec8a06ad05`
- Processed, 158 files: `ae26d7553238e3cf92206e3238ac0bf60f4c59210283f362dfd989eea96bf014`

Both match the accepted manifests.

## Stage 15 result integrity

- Frozen membership: `1,040`
- Realized primary outcomes: `589`
- Explicit unavailable/ambiguous outcomes: `451`
- Every single factor partitions all `1,040` observations exactly.
- Every predeclared interaction partitions all `1,040` observations exactly.
- No unrestricted interactions or learned bucket boundaries are present.
- All four `RESEARCH_CANDIDATE` rows pass trade/session/month-concentration gates, BH FDR `q <= 0.10`, and a session-clustered 95% bootstrap interval excluding zero.
