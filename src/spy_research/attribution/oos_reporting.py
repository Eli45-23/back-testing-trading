"""Review-ready Stage 15.2 report rendering."""

from __future__ import annotations

from decimal import Decimal

from spy_research.attribution.oos_models import OOSValidationReport


def _n(value, places=4):
    return "NA" if value is None else f"{value:.{places}f}"


def _pct(value):
    return "NA" if value is None else f"{value * Decimal(100):.1f}%"


def render_oos_markdown(report: OOSValidationReport) -> str:
    periods = report.years + (report.combined,)
    lines = [
        "# Stage 15.2 — BASE_SHORT Out-of-Sample Exclusion Validation",
        "",
        "The candidate universe, NEG definitions, gates, and classifications were frozen before unseen outcomes were loaded. Stage 14 remained paused; Alpaca PAPER was not used.",
        "",
        "## Baselines",
        "",
        "| Period | Membership | Realized | Unavailable/ambiguous | Sessions | Win | Mean R | Median R | PF | +/− months | LOMO | Mean 95% CI |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *(f"| {p.period} | {p.baseline.retained_membership} | {p.baseline.realized_retained} | {p.baseline.unavailable_or_ambiguous_retained} | {p.baseline.sessions} | {_pct(p.baseline.win_rate)} | {_n(p.baseline.mean_r)} | {_n(p.baseline.median_r)} | {_n(p.baseline.profit_factor)} | {p.baseline.positive_months}/{p.baseline.negative_months} | {_n(p.baseline.leave_one_month_out_min_mean_r)} | [{_n(p.baseline.bootstrap_mean_r_low)}, {_n(p.baseline.bootstrap_mean_r_high)}] |" for p in periods),
        "",
        "## Overall replication decision",
        "",
        "| Candidate | 2025 Δ mean R | 2024 Δ mean R | Combined Δ mean R | Both years agree | Overall classification |",
        "|---|---:|---:|---:|---|---|",
        *(f"| {item.candidate.value} | {_n(dict(item.year_mean_r_deltas).get('2025'))} | {_n(dict(item.year_mean_r_deltas).get('2024'))} | {_n(item.combined_mean_r_delta)} | {item.all_unseen_years_directionally_agree} | {item.classification.value} |" for item in report.overall),
        "",
        "## Frozen candidate comparison",
        "",
        "| Period | Candidate | Retained M/R/U | Retained | Mean R | Δ mean | Stage15.1 Δ | PF | Δ PF | LOMO | Δ LOMO | Paired Δ 95% CI | Room diagnosis | Classification |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        *(f"| {p.period} | {r.candidate.value} | {r.metrics.retained_membership}/{r.metrics.realized_retained}/{r.metrics.unavailable_or_ambiguous_retained} | {_pct(r.metrics.retained_percentage)} | {_n(r.metrics.mean_r)} | {_n(r.mean_r_delta)} | {_n(r.stage15_1_mean_r_delta)} | {_n(r.metrics.profit_factor)} | {_n(r.profit_factor_delta)} | {_n(r.metrics.leave_one_month_out_min_mean_r)} | {_n(r.lomo_delta)} | [{_n(r.bootstrap_delta_low)}, {_n(r.bootstrap_delta_high)}] | {r.room_diagnostic.classification.value if r.room_diagnostic else 'NA'} | {r.classification.value} |" for p in periods for r in p.candidates),
        "",
        "## Outcome details",
        "",
        "| Period | Candidate | Std R | Target | Stop | EOD | Median MFE | Median MAE | 5th pct R | Worst month | Worst mean |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|",
        *(f"| {p.period} | {r.candidate.value} | {_n(r.metrics.standard_deviation_r)} | {_pct(r.metrics.target_hit_rate)} | {_pct(r.metrics.stop_hit_rate)} | {_pct(r.metrics.eod_exit_rate)} | {_n(r.metrics.median_mfe)} | {_n(r.metrics.median_mae)} | {_n(r.metrics.fifth_percentile_r)} | {r.metrics.worst_month or 'NA'} | {_n(r.metrics.worst_month_mean_r)} |" for p in periods for r in p.candidates),
        "",
        "## Monthly performance",
        "",
        "| Period | Candidate | Month | Trades | Retained | Mean R | Median R | Total R |",
        "|---|---|---|---:|---:|---:|---:|---:|",
        *(f"| {p.period} | {r.candidate.value} | {m.month} | {m.trades} | {_pct(m.retained_percentage)} | {_n(m.mean_r)} | {_n(m.median_r)} | {_n(m.total_r)} |" for p in periods for r in p.candidates for m in r.metrics.monthly),
        "",
        "## Excursion replication",
        "",
        "| Period | Candidate | Stage15.1 diagnosis | OOS diagnosis | Replicated | Entry claim supported | Removed/retained 5m MFE ATR | Removed/retained 5m MAE ATR |",
        "|---|---|---|---|---|---|---:|---:|",
        *(f"| {p.period} | {r.candidate.value} | {r.stage15_1_room_classification or 'NA'} | {r.room_diagnostic.classification.value if r.room_diagnostic else 'NA'} | {r.room_diagnosis_replicated if r.room_diagnosis_replicated is not None else 'NA'} | {r.claimed_entry_quality_supported} | {_n(r.room_diagnostic.removed_median_five_mfe_atr) if r.room_diagnostic else 'NA'}/{_n(r.room_diagnostic.retained_median_five_mfe_atr) if r.room_diagnostic else 'NA'} | {_n(r.room_diagnostic.removed_median_five_mae_atr) if r.room_diagnostic else 'NA'}/{_n(r.room_diagnostic.retained_median_five_mae_atr) if r.room_diagnostic else 'NA'} |" for p in periods for r in p.candidates if r.condition_ids),
        "",
        "## Hard stop",
        "",
        "Exactly six frozen candidates were evaluated. No new exclusions, thresholds, combinations, or buckets were searched. No result changes Stage 14 or authorizes a live candidate.",
        "",
        "## Conclusion",
        "",
        "No exclusion qualifies as an `OOS_REPLICATED_RESEARCH_CANDIDATE` across both unseen years. Every exclusion has a negative mean-R delta in 2025, so the positive 2024 effects do not directionally replicate. The combined sample therefore cannot override the year disagreement.",
        "",
        "`EXCLUDE_NEG_1_4`, the Stage 15.1 entry-behavior focus, fails its special validation: its delta is negative in 2025, and its fixed five-minute excursion diagnosis is `EXIT_GEOMETRY_DEPENDENT` in both 2024 and 2025 rather than `ENTRY_BEHAVIOR_SUPPORTED`.",
        "",
        "The Stage 15.1 exclusions should not advance. BASE_SHORT itself is also regime-unstable across the unseen years: positive in 2025 and negative in 2024. This report stops without creating a live candidate or changing Stage 14.",
    ]
    return "\n".join(lines) + "\n"
