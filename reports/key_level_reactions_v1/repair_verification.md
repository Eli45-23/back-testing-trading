# Episode/retest boundary repair verification

Status: implementation corrected and verified; **not staged, committed or pushed**.
The full historical discovery study has **not** been rerun. This is a separate
repair note, not a replacement for the failed-run findings or manifest.

## Exact scope

Baseline commit: `0572548e8ac602bba4f13c7a54ebcbfe22012249`.

Changed tracked files:

1. `src/spy_research/key_level_reactions/interactions.py`: one functional
   assignment clears `retest_armed` when its episode expires; two comments
   explain its scope.
2. `tests/unit/test_key_level_reactions.py`: nine additional synthetic test cases.

This separate note is the only new repair artifact. All 16 original blocked-run
audit files were verified byte-for-byte unchanged, including the failed-run
manifest, original reproducer, reporting plan and coverage reports.

## Why the correction is implementation-only

The pending retest flag belongs to an active episode and cannot survive that
episode's expiration. Clearing it before new-episode admission prevents the
initial touch from simultaneously becoming its own retest.

The separate `separated` flag remains unchanged: it tracks actual contact
separation, not a pending retest. Resetting it at expiration would either create
extra episodes during uninterrupted contact or suppress a valid new episode
after real separation. Preserving this gate maintains the existing protocol.

No changes were made to level definitions, reaction logic, distances, horizons,
episode length, valid retest definition, date window, reporting groups, price
arithmetic, counters, breach history, or validators. The invariant remains:

`episode.start < retest_start < episode.end`.

The committed protocol SHA-256 matched before and after:

`d39d4a67b22b7c2d775a7f7fbdece6dee1ca513ecf358e89c5d52140a0588592`.

The package-source fingerprint necessarily changes with the implementation fix;
the uncommitted repaired source fingerprint is:

`5bb6c029218c461882009f0edc7e80d41df3fa1411a63020bc88e6fa12966960`.

The failed-run manifest retains its original engine fingerprint and provenance.

## Regression evidence

Before the fix, the newly selected boundary/history tests produced seven
`Retest outside episode` failures and one passing continuous-contact test.
After the fix, all pass. The final suite includes:

- Support and resistance cases at minute 30, 31 and 35 after the original touch.
- Three independently counted episodes with legitimate internal retests.
- Exact lifetime/session/run counters, prior breach/close counts, first/last
  breach timestamps, time since touch, and prefix snapshot preservation.
- Uninterrupted contact across expiration, followed by genuine separation.
- Direct validator rejection of retests exactly at either episode boundary.

The original 31-minute synthetic sequence was also executed independently:

| Episode | First touch | End | Touches | Retests |
|---|---|---|---:|---:|
| 1 | January 5, 2026, 09:30 ET | 10:00 ET | 1 | 0 |
| 2 | January 5, 2026, 10:00 ET | 10:30 ET | 1 | 0 |

Its lifetime counters remain `[1, 2]`. Only the synthetic sequence was executed;
the archived reproducer, which also contains historical reads and asserts the
old failure, was preserved and was not executed as a whole.

## Verification receipt

- Focused KLR suite: **68 passed**, 1.56 seconds.
- Full project suite: **1,239 passed**, 6.42 seconds.
- Added test cases: **9**; previous totals were 59 and 1,230.
- Frozen break-and-hold hashes: **174/174 before and after**.
- Original blocked-run files: **16/16 unchanged**.
- `git diff --check`: passed.
- Changed Python files: compilation passed.
- Independent read-only code review: no correctness or scope findings.
- Stage 14 and all other existing tracked files: unchanged.
- No historical discovery run, market-data reads, network access or broker access.
  Final focused/full verification enforced network and repository market-data
  read guards; tests used synthetic fixtures.
- No staging, commit or push. HEAD remains the baseline commit above.

Premarket remains **4 certified sessions usable, 166 uncertified sessions
unavailable**. No coverage relaxation or reconstruction was performed.

Await review before a separate repair commit and a separately authorized rerun
of the same declared study. Do not overwrite the failed-run audit during a rerun.
