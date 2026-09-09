# Frozen admission, validation and confirmation gates

All strategy gates use $0.02 per-share roundtrip net outcomes. Discovery and 2025 require at least 200 executable trades in 80 contributing sessions; 2026 requires 150 in 60. Every scheduled session must validate, including zero-signal sessions. Sample insufficiency does not extend a period.

For every stage: net mean R ≥ 0.05; net PF ≥ 1.10; at least two-thirds of active months positive; maximum net drawdown ≤40R; positive net total R at least as large as maximum drawdown; largest positive month ≤35% of the sum of positive monthly net profits; five largest positive sessions ≤25% of the sum of positive session net profits; leave-one-month-out minimum net mean R strictly positive; expected directional effect unchanged. Zero and inactive months are disclosed separately; active zero-mean months are not positive. A zero-drawdown profitable path passes the recovery ratio without division by zero. Undefined evidence cannot pass.

Whole-session bootstrap: 10,000 draws, seed 20260909; include the complete period calendar and preserve all observations within each resampled session. Share resamples across candidates. Paired comparisons require identical event IDs and session identities; natural populations are also reported explicitly. Outcome arithmetic remains Decimal; numerical bootstrap arrays use floating point, disclosed separately.

Report ordinary two-sided 95% intervals. For validation and confirmation, additionally require a strictly positive lower endpoint of the two-sided Bonferroni interval with alpha=0.05/3, using all three reserved candidate slots even if fewer are submitted. Bounds are the 0.05/6 and 1−0.05/6 quantiles. Undefined intervals are insufficient.

Prediction comparisons use Benjamini–Yekutieli adjustment over every registered atomic contrast. This is nominal evidence in adaptive discovery, not a claim of fully corrected search bias. Report raw search counts and rejected hypotheses. Do not estimate an effective independent search count without a defensible method.
