# Prospective Rejection Validation V1 — design freeze

This is a design-only freeze. No prospective market data, outcomes, broker, or
paper/live execution is accessed by this package or its tests.

## Scope and provenance

The shortlist is inherited from the completed Rejection Risk/Exit Study V1 at
commit `305f56a0ff607de34bafe8f528226192a5086bf6`. No new development search,
filter, bucket, or outcome inspection is permitted. The sole entry is the frozen
`IMMEDIATE_CLOSE_BACK_1M`; Momentum, five-minute Immediate, and Retest entries
are excluded.

The fixed unseen window begins on the first full XNYS session after the development
cutoff: **2026-09-08**. Exactly **60 XNYS sessions** are predeclared. The endpoint
is the 60th planned session; the window never extends automatically. Zero-signal
sessions remain in the 60-session denominator.

## Frozen model matrix

Exactly four models are evaluated:

1. `USD040_TARGET_2R_BE1R` — primary candidate
2. `USD040_TARGET_1.5R` — secondary candidate
3. `ATR050_TARGET_1R` — exploratory ATR candidate
4. `USD040_TARGET_2R` — control

There are no other stops, targets, management variants, filters, or entry rules.

## Signal and entry semantics

Use the frozen Rejection Entry implementation exactly. A close-back signal is
available only after the completed one-minute confirmation. The executable entry
is the first same-session one-minute bar whose **start** is at or after signal
availability, filled at that bar's OPEN. The entry minute is included in the path;
the confirming bar's high/low cannot be used before its completion. Identity,
session, level, approach, and interaction provenance remain unchanged.

## ATR and ambiguity

ATR uses the existing causal `calculate_session_atr` implementation without any
change, prior-session inheritance, or fallback. ATR-unavailable signals remain
explicitly unavailable. Report availability by session, direction, and month, and
compare fixed-stop models with ATR on exactly the same ATR-available entry IDs.

The existing stop/target state machine is reused unchanged. Same-minute stop and
target contact is `AMBIGUOUS_STOP_TARGET`; stop-first is primary and target-first
is a separate sensitivity. A zero-R break-even exit is not a win. No uncertainty
is resolved in the favorable direction.

## Data validity and causal access

Every one of the 60 planned sessions requires complete Alpaca SIP SPY RTH
one-minute coverage, exact minute ordering, no duplicates, and deterministic
aggregation/indicator initialization. A missing or invalid required session blocks
the endpoint report; the date is not replaced and no minute is filled or inferred.
No later bar may reconstruct an earlier signal, entry, or ATR. The only allowable
market-data partitions are the exact predeclared session dates. Any partition not
matching that allowlist fails closed before it is opened. No network or Alpaca
client is part of the design package.

## Denominators and endpoint metrics

For every model, report eligible entries, executable outcomes, unavailable and
ATR-unavailable outcomes, contributing sessions, zero-signal sessions, wins,
losses, zero-R outcomes, win rate, average win/loss R, mean/median R, profit
factor, event-order maximum drawdown, longest losing streak, long/short results,
monthly results, positive/negative months, worst month, and leave-one-month-out
minimum mean R. Eligible is executable plus unavailable; ambiguity is a subset of
executable; executable is wins plus losses plus zero-R. Null metrics carry an
explicit reason and are never silently reported as zero.

Report gross and the fixed `$0.01` and `$0.02` SPY-equivalent underlying
round-trip cost scenarios. These are research sensitivities, not 0DTE option
execution costs. Event-order drawdown is a diagnostic, not an account-equity path.

## Comparisons and uncertainty

Predeclare three candidate-versus-control comparisons: primary versus control,
secondary versus control, and ATR versus control on the common ATR-available
population. Show natural populations and exact common identities separately;
never filter the natural primary population by eventual control availability.

Use whole-session bootstrap with 10,000 draws, fixed seed `20260908`, shared
resamples across models, and session clustering. Candidate/control comparisons
also use paired session-level resampling on overlapping identities. Report ordinary
95% intervals and Bonferroni-adjusted intervals for the three comparisons
(`alpha = 0.05/3`). No ranking, selection, early stopping, or automatic promotion
is permitted before all 60 sessions pass coverage checks.

## Interim and endpoint states

Before all 60 planned sessions are complete, reports may only be labeled
`INTERIM_NO_SELECTION`. At the endpoint, incomplete coverage yields
`BLOCKED_DATA_QUALITY`; complete coverage yields `ENDPOINT_REACHED_NO_SELECTION`
with per-model `ENDPOINT_REPORT_ELIGIBLE` or `INSUFFICIENT_PROSPECTIVE_DATA`
based on the fixed 200-outcome/40-session gates. These labels do not select or
promote a model. There is no window extension and no live/paper candidate change.
