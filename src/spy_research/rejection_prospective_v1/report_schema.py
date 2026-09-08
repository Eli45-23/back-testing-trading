"""Deterministic endpoint and comparison output schemas for V1."""

from __future__ import annotations

from .protocol import AMBIGUITY_SENSITIVITIES, COST_SCENARIOS

ENDPOINT_FILES = (
    "findings.md",
    "run_manifest.json",
    "coverage_report.json",
    "denominator_reconciliation.json",
    "model_results.csv",
    "cost_sensitivity.csv",
    "atr_availability.csv",
    "common_atr_comparisons.csv",
    "candidate_control_comparisons.csv",
    "monthly_results.csv",
    "session_results.csv",
    "leave_one_month_out.csv",
    "bootstrap_results.csv",
    "context_tables.csv",
    "ambiguity_sensitivity.csv",
    "verification_receipt.json",
    "output_hashes.json",
)

METRIC_FIELDS = (
    "eligible_entries",
    "executable_outcomes",
    "unavailable_outcomes",
    "atr_unavailable",
    "ambiguous_outcomes",
    "contributing_sessions",
    "zero_signal_sessions",
    "wins",
    "losses",
    "zero_r_outcomes",
    "win_rate",
    "average_win_r",
    "average_loss_r",
    "mean_r",
    "median_r",
    "profit_factor",
    "event_order_max_drawdown_r",
    "longest_losing_streak",
    "long_mean_r",
    "short_mean_r",
    "monthly_mean_r",
    "positive_months",
    "negative_months",
    "worst_month",
    "leave_one_month_out_minimum_mean_r",
    "bootstrap_ci_low",
    "bootstrap_ci_high",
)

COMPARISON_FIELDS = (
    "candidate",
    "control",
    "population",
    "cost_per_share_roundtrip",
    "ambiguity_sensitivity",
    "common_usable_identities",
    "paired_mean_r_difference",
    "paired_ci_low",
    "paired_ci_high",
    "bonferroni_adjusted_ci_low",
    "bonferroni_adjusted_ci_high",
)

SCHEMA_CONTRACT = {
    "endpoint_files": ENDPOINT_FILES,
    "metric_fields": METRIC_FIELDS,
    "comparison_fields": COMPARISON_FIELDS,
    "cost_scenarios": tuple(str(value) for value in COST_SCENARIOS),
    "ambiguity_sensitivities": AMBIGUITY_SENSITIVITIES,
    "decimal_policy": "Decimal only; 80-digit HALF_EVEN; null with reason for unavailable/empty metrics",
    "selection_policy": "No ranking or automatic promotion",
}
