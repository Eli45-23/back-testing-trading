# Rejection Risk/Exit Study V1 — design freeze

No historical risk/exit outcomes have been run. Primary entry is IMMEDIATE_CLOSE_BACK_1M;
control is MOMENTUM_AWAY_025. Source design a3909eaa0271a381fd6e05756628c07148bac65c,
archived source 311f4ada80b4739c207cbdf4a8dda4cef703c632. Preserve entry definitions verbatim.

## Population and source contract

Every executable archived signal is eligible: 3,311 primary and 6,024 control
references according to the archived population receipt. Confirm these counts and
unique (variant, interaction_id, session_date) identities before any future run.
Never derive membership from archived paths, MFE, MAE, later confirmations or context.
Read signals and causal interaction metadata only for population construction.
Preserve original signal_known_at, entry timestamp/open and approach direction.
ABOVE means LONG/rejection-up; BELOW means SHORT/rejection-down. Unknown direction
fails reconciliation rather than silently disappearing. Every source record must
reconcile to an eligible executable signal or an explicitly excluded non-executable
source status. Keep non-executable source counts outside the eligible-entry denominator.
PMH/PML remain sparse/insufficient, available only under the source certification.

## Finite matrix and state machine

Four stops: USD025 ($0.25), USD030 ($0.30), USD040 ($0.40), ATR050 (0.5 ATR14).
Each has TARGET_1R, TARGET_1.5R, TARGET_2R, TARGET_2R_BE1R: exactly 16 models per
entry, 32 model-entry combinations. No extra models or filters.

Signal is available at completed confirmation, never its stored start timestamp.
Reuse first_executable_minute from frozen Rejection Entry. First same-session minute
open at or after availability is entry; include that minute. A complete RTH grid
implies entry timestamp equals availability. Reject mismatched archived references.
Do not use any confirming-minute high/low after the entry.

ATR uses calculate_session_atr unchanged: same-session RTH 5-minute bars starting
09:30, consecutive prefix with start+5 minutes <= signal_known_at. First TR is
high-low; 14-TR SMA seed then Wilder recursion, 50-digit HALF_EVEN context;
daily reset. First possible ATR availability is 10:40 ET. No previous-day seed or
fixed fallback. Missing warm-up is UNAVAILABLE_ATR; incomplete prefix fails closed;
nonpositive risk is INVALID_RISK. Freeze ATR at signal availability, never entry's
future minute. Fixed-stop candidates remain eligible when ATR is unavailable.

Let E be entry, d = +1 LONG or -1 SHORT, r initial stop distance. Initial stop
E-d*r; target E+d*r*k. State starts ACTIVE at entry, then EXITED or BE_PENDING,
then BE_ACTIVE on the next minute. Target stays fixed throughout.
For each minute: activate a previously pending BE; evaluate known open first.
Open beyond stop exits at open (gap loss can exceed 1R); open beyond target exits
at target limit, no favorable gap improvement. Then test stop/target inclusively
against high/low. If both touch, emit AMBIGUOUS_STOP_TARGET with stop-first primary
and target-first sensitivity; retain the same event in both denominators. If only
one touches, exit there. Only a surviving minute can arm BE at +1R. Activate at
that minute's completion, for subsequent minutes only. A +1R touch followed by
a return to E within that same minute never retroactively triggers BE. Original
stop remains active during that minute. If the next open gaps beyond E, fill at
open. Touching BE at E gives exactly zero gross R and is not a win.

Require the full consecutive entry-to-session-close minute grid even if a model
exits earlier: shared coverage prerequisite prevents model-dependent coverage
selection. Missing grid returns UNAVAILABLE_PATH. No data filling. If neither
barrier exits, exit at final RTH minute close, known at session close. Honor XNYS
early closes. No 30-minute truncation: risk/exit observations extend to RTH close.

## Accounting, costs and denominators

Gross R = d*(exit-E)/r using original risk, including after BE. Price calculations
retain Decimal; risk/R calculations use 80-digit HALF_EVEN, no float prices/ticks.
Scenario net R = gross R - roundtrip_cost/r; costs exactly 0, .01, .02 dollars
per share. These SPY-equivalent underlying movement costs are not real 0DTE
option execution costs. Classify separately per cost/sensitivity: positive WIN,
negative LOSS, exact zero ZERO. No epsilon. BE gross zero becomes a net loss with cost.

Eligible = executable outcomes + unavailable outcomes. Ambiguous is a subset of
executable outcomes, not an additional disjoint denominator. Executable = wins +
losses + zeros in each sensitivity/cost case. Report UNAVAILABLE_ATR,
UNAVAILABLE_PATH, UNAVAILABLE_ENTRY and INVALID_RISK separately. Data/identity
violations block the run rather than removing observations.

## Reporting and bootstrap plan

For all 32 combinations, both ambiguity sensitivities and all 3 cost scenarios:
eligible, executable, unavailable and ambiguous counts; eligible and contributing
sessions; wins/losses/zeros; win rate over all executable outcomes; average positive
and negative R; mean/median R; profit factor = sum positive R / abs(sum negative R).
No losses and positive gains: null with NO_LOSSES flag (not fabricated finite PF);
all zeros: null UNDEFINED. Empty averages/rates are null with reason, never zero.

Event diagnostic order is (entry_timestamp, interaction_id), independently per
entry/model. Cumulative R starts at zero; drawdown=max(running peak-cumulative R).
Longest losing streak resets on zero or win. Unavailable rows are omitted from
the numeric series but counted explicitly. Overlapping events remain independent
research events; this is not a position-constrained account-equity simulation.

Report LONG/SHORT; calendar-month results (September partial); positive/negative/
zero months by monthly mean R; worst nonempty month; leave-one-month-out minimum
mean R over remaining events. Preserve zero-event sessions and empty-month flags.
Report gross and cost-adjusted metrics and both ambiguity sensitivities throughout.

Whole-session bootstrap: 10,000 draws, seed 20260908. Sample the full 170-session
calendar with replacement, carrying all events in each sampled session (including
zero-event sessions). Compute event-weighted mean R per draw. Percentile 95% CI:
sorted samples, linear interpolation at .025 and .975 using Decimal; report null
draws explicitly. Reset generator to the frozen seed per comparison so draws align.
Pointwise intervals are descriptive, unadjusted for selection among models.

Exactly 16 predeclared primary-minus-control comparisons: identical exit model,
same cost/sensitivity. Show unconditional means with differing populations and
exact common interaction/session identities separately. Common usable identities
must have both entries and valid outcome/risk; report missing partner and ATR
availability attrition. Paired bootstrap samples the same session indices for both
sides and computes mean per-identity R difference, with all common events retained.
Do not use eventual control availability to filter unconditional primary results.
No pairwise search across different models. Report common available-ATR identities
across stop families as an availability sensitivity, never the primary population.

Context is descriptive only: PDH/PDL, ORH5/ORL5, PWH/PWL, 1H_HIGH/1H_LOW,
PMH/PML separately sparse; first since creation/later; first same-session/repeated;
never breached/penetrated without close-through/completed close-through/unknown;
time 09:30-10:00,10:00-11:00,11:00-12:00,12:00-14:00,14:00-15:00,15:00-close
at original first touch; approach direction; existing frozen confluence groups
ISOLATED/TWO_IDENTITIES/THREE_PLUS_IDENTITIES. Preserve causal source snapshots
and unknown values. No retrospective reclassification, filtering or ranking.

## Isolation and freeze plan

Outcomes Jan 2-Sep 4 2026 inclusive. Earlier local data only where already permitted
for causal context; ATR still resets daily. No network or Alpaca. Future runner
must validate paths before opening any partition and install a fail-closed access
guard rejecting post-Sep-4 data, including prospective Sep 8-Dec 1 partitions.
This design phase has no historical loader or batch runner; tests are synthetic.

Freeze manifest hashes this protocol, new source and tests, and records dependency
hashes including existing ATR, entry engine/models, XNYS calendar, archived input
manifests and the 174-file Break-and-Hold freeze. Verify all before a future run;
any mismatch blocks execution. Canonical protocol hash covers constants; artifact
hashes also cover prose and implementation. Manifest excludes itself to avoid
self-reference. Future result manifest must reference this freeze and a separately
approved committed design SHA, exact input hashes, read-access log and output hashes.
No historical result is created in this phase; no commit/push until review.
