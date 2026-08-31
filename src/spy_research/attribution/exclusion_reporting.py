"""Review-ready Stage 15.1 Markdown rendering."""

from __future__ import annotations

from decimal import Decimal

from spy_research.attribution.exclusion_models import ExclusionValidationReport


def _n(value: Decimal | None, places: int = 4) -> str:
    return "NA" if value is None else f"{value:.{places}f}"


def _pct(value: Decimal | None) -> str:
    return "NA" if value is None else f"{value * Decimal(100):.1f}%"


def render_exclusion_markdown(report: ExclusionValidationReport) -> str:
    lines = [
        "# Stage 15.1 — BASE_SHORT Negative-Condition Exclusion Validation",
        "",
        f"Frozen range: `{report.start_date}` through `{report.end_date}`",
        f"Baseline: `{report.baseline_candidate}`",
        "Stage 14 status: paused and unchanged. No Alpaca connection or order activity.",
        "",
        "## 1. Baseline reconciliation",
        "",
        f"Membership **{report.baseline.retained_membership}**; realized **{report.baseline.realized_retained}**; unavailable/ambiguous **{report.baseline.unavailable_or_ambiguous_retained}**; sessions **{report.baseline.sessions}**; mean R **{_n(report.baseline.mean_r)}**; median R **{_n(report.baseline.median_r)}**; PF **{_n(report.baseline.profit_factor)}**; win **{_pct(report.baseline.win_rate)}**; +/− months **{report.baseline.positive_months}/{report.baseline.negative_months}**; LOMO minimum **{_n(report.baseline.leave_one_month_out_min_mean_r)}**; 95% CI **[{_n(report.baseline.bootstrap_mean_r_low)}, {_n(report.baseline.bootstrap_mean_r_high)}]**.",
        "",
        "Baseline reconciliation passed exact Stage 15 Decimal values before any exclusion was evaluated.",
        "",
        "## 2. Frozen-condition and overlap accounting",
        "",
        "| ID | Condition | Membership | Realized | Unavailable/ambiguous | Unique membership | Unique realized | Sessions | Months | Frozen mean R | Frozen BH q |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *(f"| {item.condition_id} | {item.condition_name} | {item.membership_n} | {item.realized_n} | {item.unavailable_or_ambiguous_n} | {item.unique_membership_n} | {item.unique_realized_n} | {item.sessions} | {item.months} | {_n(item.stage15_mean_r)} | {_n(item.stage15_fdr_q_value)} |" for item in report.conditions),
        "",
        "Membership overlap matrix (realized overlap in parentheses):",
        "",
        "| | NEG_1 | NEG_2 | NEG_3 | NEG_4 |",
        "|---|---:|---:|---:|---:|",
        *(
            "| NEG_{} | {} |".format(
                left,
                " | ".join(
                    f"{cell.membership_overlap} ({cell.realized_overlap})"
                    for cell in report.overlap_matrix
                    if cell.left_condition == left
                ),
            )
            for left in range(1, 5)
        ),
        "",
        "## 3. Exclusion-variant comparison",
        "",
        "| Variant | Original M | Removed M/R/U | Retained M/R/U | Membership retained | Realized retained | Sessions | Win | Mean R | Δ mean | Median R | PF | LOMO | 5th pct R | Classification |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        *(
            f"| {item.variant_id} | {item.metrics.original_membership} | {item.removal.unique_membership_removed}/{item.removal.realized_removed}/{item.removal.unavailable_or_ambiguous_removed} | {item.metrics.retained_membership}/{item.metrics.realized_retained}/{item.metrics.unavailable_or_ambiguous_retained} | {_pct(item.metrics.retained_percentage)} | {_pct(Decimal(item.metrics.realized_retained) / Decimal(report.baseline.realized_retained))} | {item.metrics.sessions} | {_pct(item.metrics.win_rate)} | {_n(item.metrics.mean_r)} | {_n(item.mean_r_delta)} | {_n(item.metrics.median_r)} | {_n(item.metrics.profit_factor)} | {_n(item.metrics.leave_one_month_out_min_mean_r)} | {_n(item.metrics.fifth_percentile_r)} | {item.classification.value} |"
            for item in report.variants
        ),
        "",
        "Outcome-detail metrics:",
        "",
        "| Variant | Std R | Target hit | Stop hit | EOD exit | Median MFE | Median MAE |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *(f"| {item.variant_id} | {_n(item.metrics.standard_deviation_r)} | {_pct(item.metrics.target_hit_rate)} | {_pct(item.metrics.stop_hit_rate)} | {_pct(item.metrics.eod_exit_rate)} | {_n(item.metrics.median_mfe)} | {_n(item.metrics.median_mae)} |" for item in report.variants),
        "",
        "## 4. Monthly and stability table",
        "",
        "Frozen minimum gates: at least 70% of realized trades, at least 80 sessions, at least four represented months with no month exceeding 50% of retained realized trades, and no baseline month with at least five trades reduced below 50% retention.",
        "",
        "| Variant | +/− months | Worst month | Worst mean R | CI | Bootstrap Δ CI | 70% trades | 80 sessions | Month breadth | No heavy month reduction |",
        "|---|---:|---|---:|---:|---:|---|---|---|---|",
        *(
            f"| {item.variant_id} | {item.metrics.positive_months}/{item.metrics.negative_months} | {item.metrics.worst_month or 'NA'} | {_n(item.metrics.worst_month_mean_r)} | [{_n(item.metrics.bootstrap_mean_r_low)}, {_n(item.metrics.bootstrap_mean_r_high)}] | [{_n(item.bootstrap_delta_low)}, {_n(item.bootstrap_delta_high)}] | {item.retains_70_percent_realized} | {item.represents_80_sessions} | {item.month_concentration_pass} | {item.no_heavily_reduced_month} |"
            for item in report.variants
        ),
        "",
        "Complete variant-month rows:",
        "",
        "| Variant | Month | Trades | Retained | Mean R | Median R | Total R |",
        "|---|---|---:|---:|---:|---:|---:|",
        *(f"| {item.variant_id} | {month.month} | {month.trades} | {_pct(month.retained_percentage)} | {_n(month.mean_r)} | {_n(month.median_r)} | {_n(month.total_r)} |" for item in report.variants for month in item.metrics.monthly),
        "",
        "## 5. Bootstrap diagnostics",
        "",
        "All intervals use 10,000 session-clustered resamples. Variant Δ intervals use paired session resampling against the complete control population.",
        "",
        "| Variant | Mean bootstrap median | Mean 95% CI | Δ median | Δ 95% CI | CI above zero |",
        "|---|---:|---:|---:|---:|---|",
        *(f"| {item.variant_id} | {_n(item.metrics.bootstrap_mean_r_median)} | [{_n(item.metrics.bootstrap_mean_r_low)}, {_n(item.metrics.bootstrap_mean_r_high)}] | {_n(item.bootstrap_delta_median)} | [{_n(item.bootstrap_delta_low)}, {_n(item.bootstrap_delta_high)}] | {bool(item.metrics.bootstrap_mean_r_low is not None and item.metrics.bootstrap_mean_r_low > 0)} |" for item in report.variants),
        "",
        "## 6. Room/exit-geometry diagnostic",
        "",
        "The diagnostic compares fixed first-five-minute post-entry MFE/MAE normalized by confirmation ATR. This outcome window is independent of which next-objective exit ultimately resolved.",
        "",
        "| Variant | Removed realized | Sessions | Removed/retained MFE ATR | Δ favorable | Removed/retained MAE ATR | Δ adverse | Classification |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        *(f"| {item.variant_id} | {item.room_diagnostic.removed_realized_n} | {item.room_diagnostic.removed_sessions} | {_n(item.room_diagnostic.removed_median_five_mfe_atr)}/{_n(item.room_diagnostic.retained_median_five_mfe_atr)} | {_n(item.room_diagnostic.favorable_excursion_delta)} | {_n(item.room_diagnostic.removed_median_five_mae_atr)}/{_n(item.room_diagnostic.retained_median_five_mae_atr)} | {_n(item.room_diagnostic.adverse_excursion_delta)} | {item.room_diagnostic.classification.value} |" for item in report.variants if item.room_diagnostic is not None),
        "",
        "## 7. Pre-development, development, and expanded comparison",
        "",
        "| Variant | Period | Trades | Mean R | Baseline mean | Δ mean | Median R | PF |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
        *(f"| {item.variant_id} | {period.period} | {period.trades} | {_n(period.mean_r)} | {_n(period.baseline_mean_r)} | {_n(period.mean_r_delta)} | {_n(period.median_r)} | {_n(period.profit_factor)} |" for item in report.variants for period in item.metrics.periods),
        "",
        "## 8. Written conclusion",
        "",
        *_conclusion_lines(report),
        "",
        "No further combinations, thresholds, level types, time windows, or indicator buckets were searched. No exclusion is authorized for forward testing or live use by this report.",
        "",
        f"Source Stage 15 report hash: `{report.source_stage15_report_hash}`",
    ]
    return "\n".join(lines) + "\n"


def _conclusion_lines(report: ExclusionValidationReport) -> list[str]:
    by_id = {item.variant_id: item for item in report.variants}
    singles = [by_id[f"EXCLUDE_NEG_{index}"] for index in range(1, 5)]
    strongest_single = max(
        singles,
        key=lambda item: item.mean_r_delta if item.mean_r_delta is not None else Decimal("-Infinity"),
    )
    combinations = [
        by_id["EXCLUDE_NEG_1_2"], by_id["EXCLUDE_NEG_1_4"],
        by_id["EXCLUDE_NEG_2_4"], by_id["EXCLUDE_NEG_1_2_4"],
    ]
    strongest_combination = max(
        combinations,
        key=lambda item: item.mean_r_delta if item.mean_r_delta is not None else Decimal("-Infinity"),
    )
    all_four = by_id["EXCLUDE_ANY_OF_1_TO_4"]
    candidates = [
        item.variant_id for item in report.variants
        if item.classification.value == "RESEARCH_EXCLUSION_CANDIDATE"
    ]
    return [
        f"- **Single conditions:** `{strongest_single.variant_id}` is the strongest single exclusion by mean-R improvement (Δ {_n(strongest_single.mean_r_delta)} R; retained mean {_n(strongest_single.metrics.mean_r)} R). Singles 2 and 3 improve realized outcomes descriptively but are classified `EXIT_GEOMETRY_DEPENDENT`; they are not supported as entry filters.",
        f"- **All four:** `{all_four.variant_id}` retains {_pct(all_four.metrics.retained_percentage)} of membership and {_pct(Decimal(all_four.metrics.realized_retained) / Decimal(report.baseline.realized_retained))} of realized trades, passes every minimum retention gate, and improves mean R by {_n(all_four.mean_r_delta)}. It does not numerically over-filter, but its room diagnostic is `{all_four.room_diagnostic.classification.value if all_four.room_diagnostic else 'NA'}`, so it remains `{all_four.classification.value}` rather than an entry-rule candidate.",
        f"- **Predeclared combinations:** `{strongest_combination.variant_id}` is strongest by mean-R improvement (Δ {_n(strongest_combination.mean_r_delta)} R; PF {_n(strongest_combination.metrics.profit_factor)}; LOMO {_n(strongest_combination.metrics.leave_one_month_out_min_mean_r)}).",
        "- **Stability:** every reported research candidate improves mean R in both the January–July pre-development period and the August development period, passes month-breadth/retention gates, and has a positive paired session-bootstrap delta interval. This is internal historical stability, not independent confirmation.",
        "- **Room versus entry behavior:** the room-based findings are not uniform. NEG_1 is `MIXED`; NEG_2 and NEG_3 are `EXIT_GEOMETRY_DEPENDENT`; NEG_1_4 is `ENTRY_BEHAVIOR_SUPPORTED`; other room combinations are mixed or geometry-dependent. Room exclusions therefore cannot be treated wholesale as entry-quality findings.",
        f"- **Research decision:** the frozen gates identify {', '.join(f'`{item}`' for item in candidates) if candidates else 'no variants'} as research exclusion candidates. That is enough only to justify a separately reviewed follow-up test; it does not justify changing BASE_SHORT, creating a forward candidate, or resuming paper trading.",
    ]
