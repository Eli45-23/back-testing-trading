# Key-Level Reactions V1 — offline descriptive implementation

This package is separate from Stage 14 and the frozen break-and-hold project.
It implements the approved design, not a trading strategy. No entry, stop,
take-profit, P&L, ranking, optimization, broker, or live-service code is included.
No historical study was run as part of implementation.

## Scope and data boundary

Outcome sessions must be within January 2–September 4, 2026. The caller must
declare a local historical context start before loading results. Earlier data
is context only, never added to outcome denominators. There is no implicit
20-session lookback or swing expiration. Protected dates are rejected before
partition access; primitive outcome APIs also reject out-of-range records.

`historical_inputs.load_local` only reads local daily partitions. It verifies
partition ownership, chronology, exact Decimal OHLC, source provenance, complete
XNYS RTH minutes and the existing raw-validation gates. Missing/corrupt RTH
history fails closed. Sparse premarket is reported as observed, not certified
complete. Missing premarket/prior-day/prior-week context has explicit issue rows.
No synthetic fill, network fetch or silent counter reset is provided.

## Levels and availability

PDH/PDL use the previous complete XNYS RTH session, active next RTH session.
PMH/PML use observed 04:00–open minutes, finalized at open, active that session.
ORH5/ORL5 use exactly the five opening minutes, active at opening-candle end.
PWH/PWL use every expected RTH session of the previous Monday–Sunday week;
one weekly identity persists throughout the next trading week.

Hourly bars are `1H_RTH_FULL_BARS`, anchored at the exchange open. Normal bars
are 09:30–10:30 through 14:30–15:30. A 13:00 early close produces three full
hours through 12:30. Terminal short intervals are omitted only from pivot
construction, not minute observations. Strict 2-left/2-right pivots require
all four comparisons to be strict; equality is explicitly audited. Pivots
become available at the second right bar's actual completion, including
cross-session confirmation. Missing hours cannot be bridged. No 4H or 5m
swing family exists. The 1H series is not advertised as a chart-equivalent
hourly series with shortened closing bars.

Swing prices/identities persist through development end regardless of age,
touches or breaches. Registry availability is `[available_at, expires_at)`;
swing expiration is null. Development end is administrative censoring.
Source IDs, source extent, logical creation time, availability, original role
and pivot start remain immutable. Logical creation is distinct from the
timestamp printed on a source candle.

## Touches, episodes and histories

Primary membership is exactly `low <= level.price <= high`, never proximity.
One ledger row is one touching minute; consecutive touching minutes form one
touch run. Episodes are nonoverlapping 30-minute windows from first touch,
clipped at the actual exchange close. A new episode requires a non-touch
minute separating contact; uninterrupted contact beyond an episode remains
in the touch ledger with a null episode ID, not a new independent episode.
After separation wholly on the original approach side, a new touching run
is a retest. The first touch never requires a retest.

Session/lifetime touch numbers are one-based including current touch. Prior
counts exclude it. All prior-history snapshots precede current-minute updates.
Lifetime means *observed since availability*, not all SPY history. Unknown
preexisting history is explicitly flagged; first-interaction status is null
when observation coverage since creation is unknown. Unknowable lifetime
counts are null; separately named observed counters retain the visible suffix
without presenting unknown prior history as zero. Level age counts XNYS
session transitions, with zero in its confirmation session. Time-since-touch
and all descriptive delays are seconds between minute starts or known-at
boundaries as named; true intraminute touch time is not claimed.

A resistance breach is a strictly higher observed high; a support breach is
a strictly lower observed low. Equality is not breach. A breach episode ends
after a complete minute is wholly on the original non-breached side (equality
allowed). Both breach-episode and breach-minute counts are recorded. Completed
close-through counts use strict inequality. Gap crossings are separate records
and never primary touches. A newly created level does not synthesize a gap
interaction from a previous minute during which it was unavailable.

## Reaction measurements

Fixed distances are $0.25/$0.50/$1.00 and horizons are 5/15/30 minutes, including
the first touch minute. Each episode appears in all nine panels. First passage
is rejection-first, continuation-first, ambiguous, unresolved, or censored.
Separate censoring flags persist even when an earlier passage is resolved.
Missing tail data is an error, not administrative censoring.

The touch minute's extrema may predate contact. V1 conservatively marks
uncertain first-passage order ambiguous, rather than guessing a path. A final
close sufficiently away without an opposing threshold excursion can establish
an immediate rejection. `mfe`/`mae` are guaranteed post-touch lower bounds:
touch-minute close plus all subsequent full-minute extrema. Envelope upper
bounds additionally include the whole touch minute. Unknown approach gives
null directional excursions. These are distances from a level, not trade R.

Single-candle rejection means the first touch candle closes on the approach
side. Single-touch/one-retest/multiple-test rejection count separated retests
before confirmed rejection recognition; total retests within the horizon are
also recorded. Quick reclaim is a completed close through the level within
five minutes after confirmed recognition; later reclaim is separate. Two
consecutive closes through describe acceptance, not a trading signal.
Retest results explicitly retain held/failed/ambiguous/unresolved/censored.

## Independent discovery, confluence and next levels

Reversal-first discovery is level-blind, session-reset completed-close
directional change at the same three distances. The first leg establishes
direction and is not called a reversal. Unfinished/unestablished legs remain
censored records. Turning-point time and later recognition time are separate.
Level attribution uses availability at turning-minute start, never hindsight
availability at recognition.

Each touch, episode and reversal carries independent relationships to every
eligible level. Distances are preserved even outside descriptive buckets
0/(0,.05]/(.05,.10]/(.10,.25]/>.25. Equal-price levels remain separate;
shared-source flags identify dependent provenance. Existing daily-reset
five-minute ATR14 is joined only at its completion time; unavailable/zero ATR
produces no invented normalized distance.

Next level is the nearest strictly directional price available at episode
start, preserving ties and breached swings. Future levels never replace it.
Reached versus completed-close invalidation ordering is explicit, including
same-minute ambiguity. Per-reaction links distinguish before-recognition,
same-minute ambiguous, after-recognition and unavailable observations.

## Reports and reproducibility

`service.build_report` returns an immutable `Report`; no automatic writes.
Canonical JSON is sorted and uses Decimal strings. It contains input, package
source and protocol hashes, declared history dates, coverage/issues, levels,
pivot audits, touch/gap/episode ledgers, all nine outcome panels, reversal
records, relationships and next-level snapshots. Report validators reconcile
panel denominators and family summaries, including zero-observation families.

Descriptive rate uncertainty uses 2,000 seeded (20260907) whole-session
bootstrap draws, including validated zero-event sessions. Pointwise 95%
outward empirical percentile bounds are not simultaneous confidence bounds
or selection criteria. Zero-denominator draws are counted as undefined, not
silently interpreted as zero rates. One-session/low-session intervals cannot
establish robustness. The seed/draw count are reporting settings, not
thresholds selected from outcome results.

`cli.py` is a separate module, not registered in the shared application CLI.
It requires explicit dates, a local root and `--run`. It reads no credentials,
has no execution switches, and emits JSON to stdout. Do not invoke a full
historical run until separately authorized.

Tests use synthetic minute data only. Implementation verification also runs
the existing full suite and read-only 174-file prospective freeze check.
