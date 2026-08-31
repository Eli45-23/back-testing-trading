"""Deterministic Markdown rendering for the Stage 15 review artifact."""

from __future__ import annotations

from decimal import Decimal

from spy_research.attribution.models import AttributionGroup, AttributionReport


def _number(value: Decimal | None, places: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{value:.{places}f}"


def _percent(value: Decimal | None) -> str:
    return "NA" if value is None else f"{value * Decimal(100):.1f}%"


def _group_row(item: AttributionGroup) -> str:
    flags = ",".join(
        label
        for label, active in (
            ("<30T", item.fewer_than_30_trades),
            ("<10S", item.fewer_than_10_sessions),
            ("MONTH_CONC", item.month_concentration),
        )
        if active
    ) or "—"
    return "| " + " | ".join((
        item.factor,
        item.state,
        str(item.population_n),
        str(item.trades),
        str(item.sessions),
        _percent(item.win_rate),
        _number(item.mean_r),
        _number(item.median_r),
        _number(item.profit_factor),
        _number(item.standard_deviation_r),
        _percent(item.target_hit_rate),
        _percent(item.stop_hit_rate),
        _percent(item.eod_exit_rate),
        _number(item.median_mfe),
        _number(item.median_mae),
        f"{item.positive_months}/{item.negative_months}",
        _number(item.leave_one_month_out_min_mean_r),
        f"[{_number(item.bootstrap_mean_r_low)}, {_number(item.bootstrap_mean_r_high)}]",
        _number(item.raw_p_value),
        _number(item.fdr_q_value),
        flags,
        item.classification.value,
    )) + " |"


HEADER = (
    "| Factor | State | Population | Realized | Sessions | Win | Mean R | Median R | PF | SD R | "
    "Target | Stop | EOD | Median MFE | Median MAE | +/− months | LOMO min | 95% bootstrap CI | p | BH q | Flags | Classification |\n"
    "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|"
)


def render_attribution_markdown(report: AttributionReport) -> str:
    baseline = report.baseline
    candidates = sorted(
        (
            item for item in report.single_factor_groups + report.interaction_groups
            if item.classification.value == "RESEARCH_CANDIDATE"
        ),
        key=lambda item: (item.mean_r if item.mean_r is not None else Decimal(0)),
    )
    strongest = sorted(
        (item for item in report.single_factor_groups if not item.fewer_than_30_trades and not item.fewer_than_10_sessions and not item.month_concentration and item.mean_r is not None),
        key=lambda item: item.mean_r,
        reverse=True,
    )[:5]
    weakest = sorted(
        (item for item in report.single_factor_groups + report.interaction_groups if not item.fewer_than_30_trades and not item.fewer_than_10_sessions and not item.month_concentration and item.mean_r is not None),
        key=lambda item: item.mean_r,
    )[:8]
    lines = [
        "# Stage 15 — BASE_SHORT Attribution Backtest",
        "",
        f"Frozen range: `{report.start_date}` through `{report.end_date}`",
        f"Candidate: `{report.candidate_identity}`",
        "Status: exploratory historical research only; Stage 14 remains paused and unchanged.",
        "",
        "## 1. Baseline BASE_SHORT counts",
        "",
        f"Membership: **{baseline.population_n}**; realized: **{baseline.trades}**; explicitly unavailable/ambiguous: **{baseline.unavailable_or_ambiguous}**; sessions: **{baseline.sessions}**.",
        "",
        HEADER,
        _group_row(baseline),
        "",
        "Baseline monthly performance:",
        "",
        "| Month | Trades | Mean R | Total R |",
        "|---|---:|---:|---:|",
        *(
            f"| {item.month} | {item.trades} | {_number(item.mean_r)} | {_number(item.total_r)} |"
            for item in baseline.monthly_performance
        ),
        "",
        "## 2. Complete single-factor attribution table",
        "",
        HEADER,
        *(_group_row(item) for item in report.single_factor_groups),
        "",
        "## 3. Complete predeclared interaction table",
        "",
        HEADER,
        *(_group_row(item) for item in report.interaction_groups),
        "",
        "## 4. Stability analysis",
        "",
        f"Baseline positive/negative months: **{baseline.positive_months}/{baseline.negative_months}**. Baseline leave-one-month-out minimum mean R: **{_number(baseline.leave_one_month_out_min_mean_r)}**. Session-clustered 10,000-resample 95% CI for baseline mean R: **[{_number(baseline.bootstrap_mean_r_low)}, {_number(baseline.bootstrap_mean_r_high)}]**.",
        "",
        "Every row reports the same stability fields. `<30T`, `<10S`, and `MONTH_CONC` force `INSUFFICIENT_EVIDENCE` even when an unadjusted or adjusted p-value is small.",
        "",
        "## 5. Multiple-testing diagnostics",
        "",
        "| Family | Tested hypotheses | Raw p ≤ 0.10 | BH q ≤ 0.10 | FDR level |",
        "|---|---:|---:|---:|---:|",
        *(
            f"| {item.family} | {item.hypotheses} | {item.raw_p_le_0_10} | {item.fdr_q_le_0_10} | {_number(item.fdr_level, 2)} |"
            for item in report.multiple_testing
        ),
        "",
        "Tests compare each subgroup with its complement using a two-sided unequal-variance normal approximation. Benjamini-Hochberg correction is applied separately to single factors and predeclared interactions. Sparse rows remain in the correction family but cannot be research candidates.",
        "A `RESEARCH_CANDIDATE` must also have a session-clustered 95% bootstrap interval for its own mean R that excludes zero.",
        "",
        "## 6. Strongest and weakest findings",
        "",
        "Highest adequate-coverage single-factor means (descriptive, not rankings for deployment):",
        "",
        *(
            f"- `{item.factor}:{item.state}` — n={item.trades}, mean R={_number(item.mean_r)}, delta={_number(item.mean_r_delta_from_baseline)}, q={_number(item.fdr_q_value)}, {item.classification.value}."
            for item in strongest
        ),
        "",
        "Lowest adequate-coverage findings:",
        "",
        *(
            f"- `{item.factor}:{item.state}` — n={item.trades}, mean R={_number(item.mean_r)}, delta={_number(item.mean_r_delta_from_baseline)}, q={_number(item.fdr_q_value)}, CI=[{_number(item.bootstrap_mean_r_low)}, {_number(item.bootstrap_mean_r_high)}], {item.classification.value}."
            for item in weakest
        ),
        "",
        "Unavailable EMA/regime states coincide with early-session indicator warm-up and must not be interpreted as a favorable tradable condition. Room-to-objective groups partly describe exit geometry as well as setup quality, so follow-up tests must preserve that distinction.",
        "",
        "## 7. Findings deserving a follow-up research test",
        "",
        *(f"- `{item.factor}:{item.state}` — n={item.trades}, sessions={item.sessions}, mean R={_number(item.mean_r)}, q={_number(item.fdr_q_value)}, +/− months={item.positive_months}/{item.negative_months}." for item in candidates),
        "" if candidates else "- None passed the predeclared evidence gates.",
        "",
        "These are candidates for a separately predeclared historical/forward research test only. They do not alter Stage 14 and are not authorization to deploy a filter.",
        "",
        "## 8. Source integrity",
        "",
        f"- Source Stage 13.2 exit-model hash: `{report.source_exit_hash}`",
        f"- Accepted Stage 14.4 hash: `{report.source_stage14_hash}`",
        "- Stage 14 candidate/execution source was not modified by the study.",
        "- Raw and processed stores are read-only inputs; manifest/hash verification is recorded in the final verification section after the automated checks.",
        "",
        "## Method contract",
        "",
        "Feature states and interactions are frozen in source. All feature values are known at `signal_known_at`; MFE, MAE, and realized R are outcomes only. No missing or ambiguous membership is silently dropped. No arbitrary cut-point search or unrestricted interaction search is performed.",
        "",
        "## Appendix A — Complete subgroup monthly performance",
        "",
        "The compact attribution tables report positive/negative month counts and leave-one-month-out minima. This appendix retains every subgroup-month result, including zero-trade months.",
        "",
        "| Family | Factor | State | Month | Trades | Mean R | Total R |",
        "|---|---|---|---|---:|---:|---:|",
        *(
            f"| {family} | {item.factor} | {item.state} | {month.month} | {month.trades} | {_number(month.mean_r)} | {_number(month.total_r)} |"
            for family, groups in (
                ("SINGLE_FACTOR", report.single_factor_groups),
                ("INTERACTION", report.interaction_groups),
            )
            for item in groups
            for month in item.monthly_performance
        ),
    ]
    return "\n".join(lines) + "\n"
