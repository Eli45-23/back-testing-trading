# Rejection Entry Study V1 (design freeze)

This isolated package defines the causal confirmation study built on the
completed Key-Level Reactions V1 interaction population.  It is a research
engine, not a trading strategy: it has no stops, targets, P&L, sizing, broker,
network, live service, or historical outcome runner.

## Frozen scope

The denominator is every eligible KLR interaction, not only episodes that later
look like rejections.  The inherited level families are PDH/PDL, ORH5/ORL5,
previous-week high/low, confirmed 1H RTH full-bar swing high/low, with PMH/PML
retained but separately reported as sparse (only certified premarket sessions).
No 4H or 5-minute swing levels are added.  The outcome window is January 2
through September 4, 2026 inclusive.  Earlier partitions are warm-up only;
September 8–December 1 prospective data is rejected before a reader is called.

Exactly three confirmation families are frozen (Immediate Close-Back has two
predeclared timeframe variants):

* `IMMEDIATE_CLOSE_BACK` (completed 1-minute and 5-minute variants): the first
  completed bar containing the interaction must close on the original approach
  side. A failed first close-back is not rescued by a later close-back.
* `MOMENTUM_AWAY`: the first completed bar whose range reaches a fixed $0.25
  from the level in the rejection direction.  The distance is descriptive and
  predeclared, not optimized.
* `ONE_RETEST_HOLD`: the initial completed 1-minute close-back must be followed
  by one of the frozen KLR causal retest starts; the retest bar must touch and
  close back on the approach side on completion.

Signal availability is always the confirming bar completion.  A confirmation
bar's stored timestamp is its start, never its completion.  Its constituent
minutes are therefore unavailable to the executable reference.  The first
same-session RTH one-minute bar whose **start** is at or after
`signal_known_at` supplies the executable minute open.  That minute is included
in path measurements.  No close-entry, intrabar, or future turning-point fill is
simulated.

All timestamps are timezone-aware and all prices are exact `Decimal` values.
Unavailable, ambiguous, missing-tail, and session-close-censored records remain
explicit.  Repeated touches are linked by session/interaction identity and are
not treated as independent bootstrap observations.  Pairwise wait-cost rows are
formed by exact interaction identity and never use later confirmation to filter
an earlier immediate signal.
