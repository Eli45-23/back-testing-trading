# KLR V1 discovery: pre-outcome reporting declaration

Engine baseline: `0572548e8ac602bba4f13c7a54ebcbfe22012249`.
This plan is recorded before calculating or inspecting historical KLR outcomes.
The implementation was committed and pushed before this first discovery study.

## Scope and coverage gate

- Outcomes: January 2 through September 4, 2026, inclusive, New York time.
- Context: December 22–31, 2025. This covers the complete calendar week before
  the first outcome session and more than the five full hourly bars needed for
  strict two-left/two-right swing confirmation. Earlier swings are outside this
  explicitly bounded history, not assumed absent. No age-based expiration.
- Local raw SIP partitions only; no network, credentials, or prospective data.
- No repair, fill, interpolation, or use of later observations to repair gaps.
- Premarket is certified only if all 330 expected minute starts from 04:00 to
  09:30 exist and pass validation. Any uncertified session has PMH/PML unavailable.
  Such premarket rows are withheld from a documented in-memory validated input
  view, because the unchanged engine otherwise constructs observed-only extrema.
  Original raw files remain unchanged; both original and admitted input hashes
  are recorded. After-hours observations are not used for level construction.
- All sessions require complete valid RTH. A failed gate stops outcome execution.

## Fixed descriptive groups

- Observed lifetime touch number: 1; 2; 3–5; 6–10; 11+.
  Complete lifetime history is distinguished from observed lower bounds.
- Same-session touch number: 1; 2; 3+; unavailable. These are the engine's
  touching-minute counters, not silently redefined as retest/run counters.
- Creation first-touch: true; false; unknown.
- Time of day (New York, left-inclusive/right-exclusive): 09:30–10:00;
  10:00–11:00; 11:00–12:00; 12:00–14:00; 14:00–15:00; 15:00–close.
- Prior breach partition: unknown; never breached; penetrated without completed
  close-through; completed close-through. Multiple prior breach episodes (2+)
  is a separate overlapping descriptor, not a fourth disjoint fresh/breach group.
- Confluence: use every frozen radius 0, $0.05, $0.10, $0.25 separately. Count
  eligible identities INCLUDING the original level: 1 (isolated), 2, 3+.
  Report unique families and shared-source relationships separately.
- Reversal association: preserve frozen disjoint distance buckets 0, (0,.05],
  (.05,.10], (.10,.25], >.25. Report each fixed cumulative radius separately;
  no post-result choice of what counts as nearby.
- Primary compact narrative table: $0.50 / 15 minutes, chosen for readability,
  not selection. Complete family tables include all nine panels equally.
- Rejection recognition/retest attributes describe outcomes, not causal filters.
  MFE/MAE use the engine's guaranteed post-touch bounds; envelope upper bounds
  are retained separately. These are excursions from a level, not trading metrics.

## Denominators and uncertainty

Every episode stays in all nine distance/horizon panels. The five exclusive
statuses sum to each panel denominator. The separate horizon-censored flag can
overlap resolved statuses and is never substituted for the exclusive status.
Touch minutes, touch runs, episodes, level identities and sessions are distinct
grains. Unavailable levels have unknowable interaction counts, not zero outcomes.
All descriptive cuts are first-touch snapshots, except explicitly post-event
retest/reclaim attributes. No optimized buckets, filters, scores or rankings.
Use the committed 2,000-draw seeded session bootstrap, including zero-event
sessions, for family panels; intervals are pointwise, not simultaneous.
September is a four-session partial calendar month and must be labeled as such.

## Report shape and reproducibility

User-selected primary artifact: local Markdown findings with JSON/CSV audit
tables, not a hosted report. Audience: technical/audit. Exact tables are used
instead of charts for denominator lookup. Technical summary, findings, scope,
methods, limitations/uncertainty, review-only next steps and open questions are
the required report roles. Local scripts preserve all calculations. No strategy
recommendation, historical trading metrics, commit, push, or live execution.

An external report driver may stream records from the committed public engine
components to bound memory; it must not change those components or their rules.
