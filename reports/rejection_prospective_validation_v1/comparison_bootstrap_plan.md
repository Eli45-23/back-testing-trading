# Comparison and bootstrap plan

Use 10,000 whole-session draws with fixed seed `20260908`. Each draw samples the
full 60-session calendar with replacement and carries every event in the sampled
session, including sessions with zero signals. Report Decimal 95% percentile
intervals for mean R; do not use individual-trade bootstrap.

Predeclared candidate/control comparisons are:

1. `USD040_TARGET_2R_BE1R` minus `USD040_TARGET_2R`
2. `USD040_TARGET_1.5R` minus `USD040_TARGET_2R`
3. `ATR050_TARGET_1R` minus `USD040_TARGET_2R` on common ATR-available identities

For each comparison show natural means, exact common identities, missing-partner
and ATR attrition, paired mean-R difference, ordinary 95% CI, and Bonferroni-
adjusted 98.333...% CI using alpha `0.05/3`. Shared session resamples are used
for all models and both sides of each pair. Bootstrap results are descriptive and
cannot trigger selection before the fixed endpoint.
