"""Descriptive aggregation and exports; no signal decisions live here."""
import csv
from collections import Counter, defaultdict
from decimal import Decimal
from io import StringIO
from statistics import mean, median


def quantile(values, p):
    if not values:
        return None
    xs = sorted(values)
    rank = Decimal(len(xs)-1)*Decimal(str(p))
    lo = int(rank)
    return xs[lo] + (xs[min(lo+1, len(xs)-1)]-xs[lo])*(rank-lo)


def summary(outcomes):
    eod = [next(w for w in o.windows if w.horizon == "EOD") for o in outcomes]
    measured = [w for w in eod if w.mfe is not None]
    mfes, maes = [w.mfe for w in measured], [w.mae for w in measured]
    thresholds = {}
    for outcome in outcomes:
        for t in outcome.thresholds:
            key = f"+{t.favorable}/-{t.adverse}"
            thresholds.setdefault(key, Counter())[t.result] += 1
    return dict(n=len(outcomes), measured_n=len(measured), long_n=sum(o.signal.direction == "LONG" for o in outcomes),
        short_n=sum(o.signal.direction == "SHORT" for o in outcomes),
        mean_mfe=mean(mfes) if mfes else None, median_mfe=median(mfes) if mfes else None,
        mean_mae=mean(maes) if maes else None, median_mae=median(maes) if maes else None,
        mfe_q25=quantile(mfes, .25), mfe_q75=quantile(mfes, .75), mae_q25=quantile(maes, .25), mae_q75=quantile(maes, .75),
        ratio_mean_mfe_mae=mean(mfes)/mean(maes) if maes and mean(maes) else None,
        median_eod=median(w.directional_return for w in measured) if measured else None,
        thresholds=thresholds)


def fmt(value):
    return "N/A" if value is None else f"{value:.4f}"


def render_report(report):
    events = [e for s in report.sessions for e in s.events]
    first = [o for o in report.outcomes if o.signal.entry_style == "FIRST_HOLD"]
    strong = [o for o in report.outcomes if o.signal.entry_style == "STRONG_HOLD"]
    failed = sum(e.failed_break for e in events)
    percent = lambda n, d: f"{100*n/d:.2f}%" if d else "N/A"
    lines = ["# SPY break-and-hold V1 research", "", f"Requested: {report.start} through {report.end} (America/New_York).",
        f"Sessions: expected {len(report.coverage)}, analyzed {len(report.sessions)}, missing {sum(x.raw_status == 'MISSING' for x in report.coverage)}, invalid {sum(x.raw_status == 'INVALID' for x in report.coverage)}.",
        f"Definition hash: `{report.definition_hash}`. Input manifest: `{report.input_manifest_hash}`.",
        f"Git base: `{report.git_commit}`; this report may include uncommitted research code.", "",
        "## Event population", "", "| Measure | Count/rate |", "|---|---:|",
        f"| Upside breaks | {sum(e.direction == 'LONG' for e in events)} |",
        f"| Downside breaks | {sum(e.direction == 'SHORT' for e in events)} |",
        f"| Failed upside breaks | {sum(e.failed_break and e.direction == 'LONG' for e in events)} |",
        f"| Failed downside breaks | {sum(e.failed_break and e.direction == 'SHORT' for e in events)} |",
        f"| Failed-break rate, all breaks | {failed}/{len(events)} = {percent(failed,len(events))} |",
        f"| First holds / all breaks | {len(first)}/{len(events)} = {percent(len(first),len(events))} |",
        f"| Strong holds / first holds | {len(strong)}/{len(first)} = {percent(len(strong),len(first))} |",
        f"| Reclaims | {sum(e.reclaim_timestamp is not None for e in events)} |", ""]
    for direction in ("LONG", "SHORT"):
        count = sum(any(e.direction == direction for e in s.events) for s in report.sessions)
        lines.append(f"Sessions with {direction} break: {count}/{len(report.sessions)} ({percent(count,len(report.sessions))}).")
    lines += [f"Sessions with both boundaries broken: {sum(s.both_sides_broken for s in report.sessions)}/{len(report.sessions)}.", ""]
    for style, cohort in (("FIRST_HOLD", first), ("STRONG_HOLD", strong)):
        s = summary(cohort)
        lines += [f"## {style}", "", f"n={s['n']}; measurable EOD n={s['measured_n']}; long n={s['long_n']}; short n={s['short_n']}.",
            "", "| EOD metric ($) | Value |", "|---|---:|"]
        for key in ("mean_mfe", "median_mfe", "mean_mae", "median_mae", "mfe_q25", "mfe_q75", "mae_q25", "mae_q75", "median_eod", "ratio_mean_mfe_mae"):
            lines.append(f"| {key} | {fmt(s[key])} |")
        lines += ["", "| Horizon | complete n | mean directional return $ | median return $ | median MFE $ | median MAE $ |", "|---|---:|---:|---:|---:|---:|"]
        for horizon in ("5m", "15m", "30m", "60m", "EOD", "PRE_RECLAIM"):
            windows = [w for o in cohort for w in o.windows if w.horizon == horizon and w.complete and w.directional_return is not None]
            lines.append(f"| {horizon} | {len(windows)} | {fmt(mean(w.directional_return for w in windows) if windows else None)} | {fmt(median(w.directional_return for w in windows) if windows else None)} | {fmt(median(w.mfe for w in windows) if windows else None)} | {fmt(median(w.mae for w in windows) if windows else None)} |")
        lines += ["", "Threshold percentages use all signals as denominator; ambiguous, neither, and no-data cases are retained.", "",
            "| Favorable/adverse $ | n | favorable first | adverse first | ambiguous same bar | neither | no future |", "|---|---:|---:|---:|---:|---:|---:|"]
        for key, counts in s["thresholds"].items():
            values = [f"{counts[k]} ({percent(counts[k],s['n'])})" for k in ("FAVORABLE_FIRST", "ADVERSE_FIRST", "AMBIGUOUS_SAME_BAR", "NEITHER", "NO_FUTURE_DATA")]
            lines.append(f"| {key} | {s['n']} | " + " | ".join(values) + " |")
        factors = {
            "direction": lambda o: o.signal.direction, "time bucket": lambda o: o.signal.context.time_bucket,
            "weekday": lambda o: o.signal.context.day_of_week, "next-level distance": lambda o: o.signal.context.distance_bucket,
            "first/later break": lambda o: "FIRST_BREAK" if o.signal.context.prior_break_attempts == 0 else "LATER_BREAK",
            "opposite previously tested": lambda o: str(o.signal.context.opposite_boundary_tested_earlier),
        }
        for name, key in factors.items():
            groups = defaultdict(list)
            for o in cohort:
                groups[key(o)].append(o)
            lines += ["", f"### {style}: {name}", "", "| Subgroup | n | sessions | median MFE $ | mean MFE $ | median MAE $ | mean MAE $ | median EOD $ | +.50/-.25 clean % |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
            for label, group in sorted(groups.items()):
                row = summary(group)
                clean = sum(t.result == "FAVORABLE_FIRST" for o in group for t in o.thresholds if t.favorable == Decimal('.50') and t.adverse == Decimal('.25'))
                lines.append(f"| {label}{' [small n]' if len(group)<30 else ''} | {len(group)} | {len({o.signal.session_date for o in group})} | " + " | ".join(fmt(row[k]) for k in ("median_mfe", "mean_mfe", "median_mae", "mean_mae", "median_eod")) + f" | {percent(clean,len(group))} |")
    paired_ids = {o.signal.event_id for o in strong}
    paired_first = [o for o in first if o.signal.event_id in paired_ids]
    lines += ["", "## Matched-event comparison", "", "These pairs are restricted to events that eventually achieved strong hold. This is survivor selection, not an executable first-hold filter.", "",
        "| Cohort | n | mean MFE $ | mean MAE $ | +.50/-.25 clean % |", "|---|---:|---:|---:|---:|"]
    for label, group in (("All first holds",first), ("First holds on eventual strong events",paired_first), ("Strong entries on same events",strong)):
        s = summary(group)
        clean = sum(t.result == "FAVORABLE_FIRST" for o in group for t in o.thresholds if t.favorable == Decimal('.50') and t.adverse == Decimal('.25'))
        lines.append(f"| {label} | {len(group)} | {fmt(s['mean_mfe'])} | {fmt(s['mean_mae'])} | {percent(clean,len(group))} |")
    by_id = {o.signal.event_id:o for o in paired_first}
    entry_costs = [(o.signal.price-by_id[o.signal.event_id].signal.price)*(1 if o.signal.direction == "LONG" else -1) for o in strong]
    lines += ["", f"Mean directional entry-price deterioration from waiting: ${fmt(mean(entry_costs) if entry_costs else None)}; positive means a less favorable entry.",
        "", "## Missing/invalid sessions", ""]
    lines += [f"- {c.session_date}: {c.raw_status}; {', '.join(c.errors)}" for c in report.coverage if c.raw_status != "VALID"] or ["None."]
    lines += ["", "## Interpretation and limits", ""] + [f"- {s}" for s in report.annotations]
    lines += ["- MFE/MAE ratios are descriptive excursions, not realized payoff ratios or expectancy.",
        "- Thresholds are nine predeclared comparisons, not optimized exits. No selection or edge claim follows from the best subgroup.",
        "- Backtest evidence does not guarantee future profitability; this does not estimate options profitability.", ""]
    return "\n".join(lines)


def export_csv(report):
    rows = []
    for o in report.outcomes:
        s, c = o.signal, o.signal.context
        row = dict(event_id=s.event_id, session_date=s.session_date, direction=s.direction, entry_style=s.entry_style,
            entry_timestamp=s.timestamp.isoformat(), entry_price=s.price, ORH5=o.orh5, ORL5=o.orl5,
            next_level_type=c.next_level.name if c.next_level else None, next_level_price=c.next_level.price if c.next_level else None,
            distance_to_next_level=c.next_distance, time_bucket=c.time_bucket, weekday=c.day_of_week,
            reclaim_timestamp=o.reclaim_timestamp.isoformat() if o.reclaim_timestamp else None)
        for w in o.windows:
            row.update({f"{w.horizon}_{k}": getattr(w,k) for k in ("mfe", "mae", "directional_return", "complete")})
        for t in o.thresholds:
            prefix = f"plus{t.favorable}_minus{t.adverse}"
            row[prefix] = t.result
            row[prefix+"_favorable_time"] = t.favorable_hit
            row[prefix+"_adverse_time"] = t.adverse_hit
        rows.append(row)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]) if rows else ["event_id", "entry_style"])
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
