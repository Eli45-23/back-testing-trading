# Rejection Entry Study V1 — protocol and freeze

Status: design freeze only. No Jan 2–Sep 4 entry outcomes have been run or
written by this package.

## Question and population

The study asks which observable, causally knowable confirmation best
distinguishes rejection from continuation while quantifying waiting cost. The
denominator begins with every eligible interaction produced by frozen Key-Level
Reactions V1 level construction and episode logic. It never starts from the
successful-rejection subset. PMH/PML rows are retained but their sparse,
certified premarket coverage is reported separately; no sparse data is inferred.

## Frozen confirmations

1. **Immediate Close-Back (1m and 5m variants).** The first completed confirmation bar
   that contains the initial interaction must have `low <= level <= high` and
   close on the original approach side (`close >= level` for `ABOVE`,
   `close <= level` for `BELOW`). A failure is final for the immediate family.
2. **Momentum-Away.** The first completed confirmation bar at/after the
   interaction whose high/low reaches `$0.25` away in the approach direction is
   the signal. No future turning point or intrabar fill is used.
3. **One-Retest Hold.** A completed 1m initial close-back must exist. A later
   KLR retest start strictly inside the 30-minute episode must touch the level
   and close on the approach side on completion. The first retest is evaluated;
   later success cannot rescue a failed first retest.

The approach side is the original side of the level: `ABOVE` means rejection
back above a level and `BELOW` means rejection back below it. `UNKNOWN` cannot
produce a directional confirmation.

## Timing and execution reference

For every confirmed signal, `signal_known_at = confirmation_start + timeframe`.
The first executable reference is the first same-session RTH 1-minute bar with
`timestamp >= signal_known_at`; its `open` is the reference price. The minute
starting at the completion boundary is eligible and is included in subsequent
path measurements. All minutes inside the confirming bar are strictly before
`signal_known_at` and cannot be used as a pre-signal fill. A signal whose
completion is at/after exchange close is session-close censored/unavailable.

## Measurements (no trading performance)

Each confirmation record stores its interaction and level identity, family,
confirmation start/completion, delay, displacement, and executable-reference
status. Path records store only descriptive MFE away from the level, MAE through
the level, directional close excursion, fixed `$0.25/$0.50/$1.00` first-hit
timestamps, same-minute ambiguity, and session-close censoring. No entry/stop/
target/R/win-rate/profit-factor/P&L/sizing/strategy-ranking field exists.

Wait-cost pairs are exact-identity rows for 1m-vs-5m Immediate, Immediate-vs-
Momentum-Away, and Immediate-vs-One-Retest Hold. They retain both statuses and
only compare delay, executable price disadvantage, remaining MFE, and MAE when
both observations are available. An earlier Immediate observation is never
removed because a later family failed or succeeded.

Context columns (family, support/resistance side, first interaction, same-
session touch number, breach/close-through history, fixed KLR time buckets and
confluence buckets) are descriptive only. No post-result filters or arbitrary
bucket search is allowed.

## Data and ambiguity safeguards

Only local, validated SPY raw SIP RTH minutes are accepted. Context may begin
before January 2, 2026 for prior-day/week and swing warm-up, but outcomes are
hard rejected after September 4. A scope guard runs before a reader callback;
network URLs and network clients are not accepted. Duplicate/unordered minutes
and missing post-entry tails fail closed. If both favorable and adverse fixed
distances occur in one minute their ordering is `AMBIGUOUS_SAME_MINUTE`, never a
favorable assumption. Session-close tails are explicitly censored.

Repeated touches are clustered by the immutable KLR interaction ID. Uncertainty
intervals, when a later reporting layer is authorized, use whole-session
bootstrap only (`2,000` draws, seed `20260908`) and preserve zero-event sessions.

## Freeze/provenance

`protocol_hash()` hashes the canonical JSON payload in `protocol.py`. A design
manifest records that hash, the inherited KLR protocol hash, the declared dates,
families, source-file fingerprint list, and `outcome_run_performed=false`.
Manifest/source hashes must be regenerated only through a reviewed protocol
change. No historical row-level outcomes or prospective files are part of this
design freeze.
