# Key-Level Reactions V1: discovery blocked at episode validation

## Technical summary

**No historical reaction findings are available.** The first authorized discovery
attempt stopped inside the unchanged, committed touch-ledger implementation,
before reaction measurement. It tried to record the first touch of a new episode
as a retest of that same episode. The strict episode validator correctly rejected
this with `Retest outside episode`.

Coverage is sufficient for the RTH-based families. Premarket is defensibly complete
on only 4 of 170 development sessions, so PMH/PML were unavailable on the other
166. No missing minutes were filled and no partial premarket extrema were used.

The existing 59 focused and 1,230 project tests pass, but a separate synthetic
reproducer demonstrates a boundary case those tests do not cover. All 174 frozen
break-and-hold hashes and the committed KLR source/protocol hashes still match.
No source changes, commits, pushes, network requests or prospective-data access
were made. This is a **blocked-run audit**, not a completed discovery report.

## Scope, definitions and provenance

- Engine: `0572548e8ac602bba4f13c7a54ebcbfe22012249`,
  `implement key-level reactions v1 research engine`.
- The implementation was committed and pushed before historical KLR outcomes
  were inspected. This provenance is preserved. Remote state was not contacted
  during this local-only task.
- Development outcomes: January 2–September 4, 2026 inclusive, New York time.
- Context only: December 22–31, 2025, seven XNYS sessions. This includes the full
  preceding holiday week and 39 full RTH hourly bars. Swings before this explicit
  history boundary are not assumed absent. No age-based expiration was applied.
- Input sources: 170 development partitions under `data/raw/` and seven context
  partitions under `data/oos/raw/`. Exact paths and original SHA-256 hashes are in
  [run_manifest.json](run_manifest.json).
- Protocol SHA-256:
  `d39d4a67b22b7c2d775a7f7fbdece6dee1ca513ecf358e89c5d52140a0588592`.
- Package-source fingerprint:
  `b9a560270ea14564912b435bb8822fa9dd90470ff865e6f476a89de8399c9bb8`.
- Primary membership remains exact `minute.low <= level.price <= minute.high`.
  Decimal arithmetic, completed-data availability, fixed distances/horizons and
  all episode invariants were unchanged.
- Reporting groups were declared before outcome execution in
  [reporting_plan.md](reporting_plan.md); none was selected from reaction results.

## Coverage passed, with substantial premarket unavailability

Counts below refer to minute-start timestamps, not inferred/no-trade minutes.

| Coverage item | Development | Context |
|---|---:|---:|
| XNYS sessions | 170 | 7 |
| Expected RTH minutes | 66,300 | 2,550 |
| Observed RTH minutes | 66,300 | 2,550 |
| Missing RTH minutes | 0 | 0 |
| Duplicate timestamps | 0 | 0 |
| Expected premarket minutes | 56,100 | 2,310 |
| Observed premarket minutes | 51,685 | 1,913 |
| Unobserved premarket minutes | 4,415 | 397 |
| Full RTH hourly bars | 1,020 | 39 |

The raw validator reported no errors. An independent set-based check matched
every expected RTH timestamp and independently confirmed premarket minute counts.
All **177/177 input partition hashes** matched after the attempted run.

Premarket minute counts range from 238 to 330 in development. The only sessions
with all 330 required premarket minutes are **March 3, April 8, April 13 and
July 8, 2026**. Sparse rows cannot establish that missing minutes contained no
trades or no more extreme prices. Therefore PMH/PML are unavailable on the other
166 sessions: **332 unavailable family-session slots**, not zero interactions.
Potential touches of unavailable levels are unknowable and cannot be counted.

The committed engine constructs observed-only PM extrema. To implement the
user's explicit coverage requirement without changing it, this run supplied a
documented in-memory input view withholding all uncertified premarket rows.
52,278 such rows were withheld including context; original files were untouched.
Original-record and admitted-view fingerprints are both retained. On certified
days, the engine's generic observed-PM warning remains in its raw issue export;
the independent coverage table supplies the stronger complete-grid certification.

Prior-session and prior-week context are valid for all 170 development sessions.
There are **no missing/invalid development sessions and no development early
closes**. December 24, 2025 is a context early close, with its actual 13:00 close
and three full hourly bars handled explicitly. Context-boundary unavailability
of prior-day/week levels is retained in `level_availability_issues.jsonl.gz`;
it does not remove development sessions.

Hourly initialization has ten confirmed swing identities available before the
development period. Strict two-left/two-right confirmation and the final
right-edge boundary remain unchanged; unconfirmed right-edge pivots cannot be
completed using post-cutoff data.

Evidence: [coverage_summary.json](coverage_summary.json),
[coverage_sessions.json](coverage_sessions.json),
[coverage_raw.json](coverage_raw.json),
[independent_coverage_reconciliation.json](independent_coverage_reconciliation.json).

## Level inventory exists; reaction-population counts do not

There are **1,067 unique constructed identities including context**. Of these,
1,027 have creation dates within development and 1,041 are active at some point
during development. Fourteen earlier-created identities carry into development;
26 context-only identities expire before it. These are construction counts, not
touch, episode or performance denominators.

| Family | Unique identities including context | Active during development |
|---|---:|---:|
| PDH | 176 | 170 |
| PDL | 176 | 170 |
| PMH | 4 | 4 |
| PML | 4 | 4 |
| ORH5 | 177 | 170 |
| ORL5 | 177 | 170 |
| Previous Week High | 36 | 36 |
| Previous Week Low | 36 | 36 |
| 1H swing high | 142 | 142 |
| 1H swing low | 139 | 139 |
| Total | 1,067 | 1,041 |

The 2,110 candidate-side pivot audit rows reconcile as 281 confirmed, 19 tied
extrema and 1,810 non-strict extrema. These are causal level-construction audits,
not reaction outcomes.

Touching-minute, touch-run, reaction-episode and contributing-session counts are
**unavailable because the ledger did not return a valid result**. They must not
be reported as zero. No reaction, reversal, confluence or next-level outcome
export was produced.

## The episode-boundary failure is independently reproducible

The first rejected historical episode is the December 22, 2025 ORL5 episode
starting at **10:06 ET**, ending at **10:36 ET**. Its recorded retest starts include
10:06 ET itself, violating the required strict condition:

`episode.start < retest_start < episode.end`.

Inspection of the committed code identifies the mechanism:

1. Separation during an earlier episode arms a potential retest.
2. Episode expiration clears the episode object but does not clear that state.
3. A later touch creates a new episode.
4. The stale state appends the new episode's initial touch as its own retest.

A 31-minute synthetic sequence reproduces the same error: touch at 09:30,
non-touch approach-side minutes through 09:59, then another touch at 10:00.
The second episode incorrectly contains a retest at its own 10:00 start.
This is not caused by missing coverage or the premarket restriction.

Evidence: [blocker.json](blocker.json) and the executable, synthetic-first
[reproducer](reproduce_blocker.py). The historical diagnostic reread only the
December 22 context partition and confirmed its hash was unchanged.

The validator was not weakened, rows were not discarded, the context boundary
was not shifted to avoid the failure, and no patched engine was substituted.

## Requested reaction analyses remain blocked

| Requested analysis | Status |
|---|---|
| Family × distance × horizon counts and rates | Not calculated |
| First creation/session touch and repeated-touch comparisons | Not calculated |
| Fresh / penetrated / close-through / multiple-breach comparisons | Not calculated |
| Immediate, single-touch, retest, MFE/MAE and reclaim behavior | Not calculated |
| Reversal-first turning-time level associations | Not run |
| Frozen-radius confluence and shared-source comparisons | Not run |
| Causal next-level paths and recognition ordering | Not run |
| Time-of-day and support/resistance-side comparisons | Not calculated |
| Monthly/session robustness and session bootstrap | Not calculated |
| Reaction ambiguity/censoring counts and rates | Unavailable, not zero |

Outcome denominator reconciliation cannot pass without a valid ledger. The
independent **coverage and level-inventory** checks passed; they are not a
substitute for reaction denominator checks. No subgroup findings or family
advantage can be inferred from the inventory.

## Verification and limitations

- Focused committed KLR regressions: **59 passed** (1.56 seconds).
- Full project suite: **1,230 passed** (6.35 seconds).
- Additional diagnostic: boundary defect reproduced on synthetic data and on
  one local context session. This does not count as a repaired regression.
- Frozen break-and-hold hashes: **174/174 before and after**.
- Engine source fingerprint and protocol hash: unchanged.
- Existing tracked files: unchanged, including Stage 14 and prospective files.
- Original input partition hashes: **177/177 matched** independently.
- Network calls: prohibited by the run/test audit guards; none made.
- Post–September 4 historical partitions opened: **0**. The clock advancing to
  September 8 did not alter the fixed data window. Synthetic date-guard tests
  do not access prospective market observations.
- Only this new report directory is untracked; nothing is staged or committed.
- Whitespace and helper-compilation receipts are in `verification.json`.

Passing existing tests does **not** mean this historical milestone passed. The
unexpected episode failure is the principal result of this attempt. Sparse
premarket coverage is a separate important data limitation. There is no evidence
yet about stronger or weaker level families, retest requirements, confluence,
reaction decay, entry quality, trading profitability or strategy selection.

## Review required before another attempt

Stop here for review. A separately approved, narrowly scoped correction to the
episode-state boundary plus a regression would be required before rerunning the
same declared study. No such correction or protocol redesign was made. The
recorded reporting groups and source hashes must be preserved; this failed run
must remain in provenance rather than being presented as a completed study.

The open questions are whether to authorize that implementation correction and,
separately, whether better premarket source coverage can ever be established.
Neither can be answered by inventing or favorably ordering reaction outcomes.
