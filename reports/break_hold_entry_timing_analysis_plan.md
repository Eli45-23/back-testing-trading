# Frozen V1 follow-up analysis conventions

This pass reads the existing canonical 2026 V1 JSON, with mandatory reconciliation
to 170 sessions, 1,435 breaks, 733 first holds, and 524 strong holds. It must stop
on count/identity mismatches. It does not call the detector, recalculate entry
prices, load broker credentials, fetch market data, or alter V1 definitions.

Conventions fixed before computing this follow-up:

- Pair by exact event ID, direction, and session. Entry disadvantage is
  `direction_sign * (strong_price - first_price)`, positive meaning worse.
  Essentially unchanged means absolute difference ≤$0.01; exact equality is
  also reported. This is a descriptive classification, not an entry threshold.
- Primary remaining excursions run to EOD. Pairwise excursion differences use
  only pairs with both measurements available, with missing pairs counted.
  MFE lost = first MFE − strong MFE; MAE improvement = first MAE − strong MAE.
  Positive MAE improvement means less adverse excursion after waiting. These
  differences are not realized P/L or a utility function.
- Preserve every predeclared threshold pair. The +$0.50/−$0.25 pair remains the
  original V1 illustrative subgroup metric; no pair is selected based on results.
  Ambiguous, neither, and no-data categories are retained. A separate sensitivity
  denominator removes only ambiguity and is explicitly labeled.
- Keep V1's existing disjoint distance buckets with inclusive upper bounds:
  ≤$0.25, ($0.25,$0.50], ($0.50,$1], ($1,$1.50], ($1.50,$2], >$2, unavailable.
  No known directional level does not mean unlimited room.
- Opening-width quartiles use all 170 session widths once each and linear
  interpolation (type 7). Ties stay together; groups need not contain exactly
  25% of sessions. These are descriptive dataset-derived bins, not V2 filters.
- Existing time buckets are unchanged. First valid hold refers to the originating
  event's first hold, including when analyzing its strong entry. Actual opposite
  breaks are reconstructed from canonical completed break facts, not the older
  touch-before-event feature: prior completed break, first observed at this
  confirmation close, and no opposite break yet remain distinct.
- Rolling windows are exactly 20 consecutive dataset sessions, step one session;
  every window is shown. Months include September's partial four-session sample.
- Confidence intervals use 10,000 samples of whole sessions with replacement,
  random seed 20260906, percentile 95% intervals. All 170 session clusters,
  including zero observations for a subgroup, are eligible. All events on a
  sampled session receive the same multiplicity. Event-weighted estimands use
  ratios of resampled cluster sums/counts. Paired comparisons always preserve
  the pair. Intervals are pointwise and exploratory, not multiplicity-adjusted.
- Descriptive calculations retain Decimal prices. NumPy float64 is used only
  for bootstrap numerical summaries; it does not affect any trading definition.
- Small groups are flagged at n<30 or fewer than 10 contributing sessions.
  Outlier sensitivity reports full means/medians/quantiles and a symmetric 10%
  trimmed mean, without dropping any event from the primary data. Session MFE
  contribution concentration and removal of the single largest contribution
  session are sensitivity diagnostics only.
- A first hold that never confirms is not automatically a bad trade. For every
  threshold pair, report adverse-first, clean favorable-first, ambiguity, and
  unobserved outcomes. Also distinguish close-reclaimed sequences from
  end-of-session censoring. Raw-break inferiority cannot be inferred from failure
  rate alone because V1 does not define a raw-break entry price or outcome path.

The Jan 1–Sep 4, 2026 period is in-sample for future hypotheses. Earlier
2024/2025 data have already been used elsewhere in this repository and cannot
be called untouched without an explicit provenance audit. No V2 rule is
implemented in this pass.
