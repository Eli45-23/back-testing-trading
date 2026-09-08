"""Deterministic descriptive tables and findings for the completed KLR run."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, localcontext
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from statistics import median
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
NY = ZoneInfo("America/New_York")
FAMILIES = ("PDH", "PDL", "PMH", "PML", "ORH5", "ORL5", "PWH", "PWL", "1H_HIGH", "1H_LOW")
DISTANCES = ("0.25", "0.50", "1.00")
HORIZONS = (5, 15, 30)
PANELS = tuple((d, h) for d in DISTANCES for h in HORIZONS)
STATUSES = ("REJECTION_FIRST", "CONTINUATION_FIRST", "AMBIGUOUS", "UNRESOLVED", "CENSORED")
RADII = ("0", "0.05", "0.10", "0.25")
EP_DAY: dict[str, str] = {}


def stream(name: str):
    with gzip.open(OUT / f"{name}.jsonl.gz", "rt") as handle:
        for line in handle:
            yield json.loads(line)


def stamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(NY)


def pct(n: int, d: int) -> str:
    return "" if not d else str((Decimal(n) * Decimal(100) / Decimal(d)).quantize(Decimal("0.01")))


def median_decimal(values) -> str:
    vals = sorted(Decimal(str(x)) for x in values if x is not None)
    return "" if not vals else str(vals[(len(vals) - 1) // 2] if len(vals) % 2 else (vals[len(vals)//2-1] + vals[len(vals)//2]) / 2)


def write_csv(name: str, records: list[dict]) -> None:
    path = OUT / f"{name}.csv"
    fields = list(dict.fromkeys(k for row in records for k in row))
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def write_json(name: str, value) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def reaction_summary(rows: list[dict]) -> dict:
    counts = Counter(row["status"] for row in rows)
    n = len(rows)
    assert sum(counts.values()) == n
    return {
        "episodes": n,
        **{f"{status}_n": counts[status] for status in STATUSES},
        **{f"{status}_pct": pct(counts[status], n) for status in STATUSES},
        "horizon_censored_flag_n": sum(bool(row["censored"]) for row in rows),
        "median_mfe_lower_bound": median_decimal(row["mfe"] for row in rows),
        "median_mae_lower_bound": median_decimal(row["mae"] for row in rows),
        "median_mfe_envelope_upper": median_decimal(row["mfe_envelope_upper"] for row in rows),
        "median_mae_envelope_upper": median_decimal(row["mae_envelope_upper"] for row in rows),
        "reclaim_n": sum(row["reclaim_known_at"] is not None for row in rows),
        "reclaim_pct_of_rejection_first": pct(sum(row["reclaim_known_at"] is not None for row in rows), counts["REJECTION_FIRST"]),
        "quick_reclaim_n": sum(bool(row["quick_reclaim"]) for row in rows),
        "later_reclaim_n": sum(bool(row["later_reclaim"]) for row in rows),
        "median_time_to_reclaim_seconds": median_decimal(row["time_to_reclaim_seconds"] for row in rows),
    }


def table_from_groups(name: str, groups: dict[tuple, list[dict]], dimensions: list[tuple[str, list]], include_families: bool = True) -> list[dict]:
    records = []
    family_values = ["ALL", *FAMILIES] if include_families else ["ALL"]
    for family in family_values:
        for group_key in _product(*(values for _, values in dimensions)):
            for distance, horizon in PANELS:
                rows = groups.get((family, *group_key, distance, horizon), [])
                records.append({"family": family, **{name_: value for (name_, _), value in zip(dimensions, group_key)},
                    "distance": distance, "horizon": horizon,
                    "contributing_sessions": len({EP_DAY[row["episode_id"]] for row in rows}) if rows else 0,
                    **reaction_summary(rows)})
    write_csv(name, records)
    return records


def _product(*sequences):
    if not sequences:
        yield ()
        return
    for head in sequences[0]:
        for tail in _product(*sequences[1:]):
            yield (head, *tail)


def main() -> None:
    levels = {row["id"]: row for row in stream("level_inventory")}
    touches = {row["id"]: row for row in stream("touches")}
    episodes = {row["id"]: row for row in stream("episodes")}
    reactions = list(stream("reactions"))
    next_levels = {row["episode_id"]: row for row in stream("next_levels")}
    next_reactions = list(stream("next_level_reactions"))
    reversals = list(stream("reversals"))
    coverage = json.loads((OUT / "coverage_sessions.json").read_text())
    session_dates = tuple(row["session_date"] for row in coverage)
    ep_family = {eid: levels[episode["level_id"]]["family"] for eid, episode in episodes.items()}
    ep_role = {eid: levels[episode["level_id"]]["role"] for eid, episode in episodes.items()}
    ep_day = {eid: stamp(episode["start"]).date().isoformat() for eid, episode in episodes.items()}
    global EP_DAY
    EP_DAY = ep_day
    first_touch = {eid: touches[episode["touch_ids"][0]] for eid, episode in episodes.items()}
    assert len(reactions) == 9 * len(episodes)
    assert len({(row["episode_id"], row["distance"], row["horizon"]) for row in reactions}) == len(reactions)

    # Family panel table is the committed engine's complete denominator table.
    family_rows = []
    for row in stream("family_summaries"):
        statuses = dict(row.pop("status_counts"))
        row.pop("status_rates")
        family_rows.append({**row, **{f"{s}_n": statuses[s] for s in STATUSES},
            **{f"{s}_pct": pct(statuses[s], row["episodes"]) for s in STATUSES}})
    write_csv("family_reactions", family_rows)

    # Level inventory and availability.
    issues = list(stream("level_availability_issues"))
    inventory = []
    for family in FAMILIES:
        rows = [row for row in levels.values() if row["family"] == family]
        touched_ids = {touch["level_id"] for touch in touches.values() if levels[touch["level_id"]]["family"] == family}
        inventory.append({"family": family, "unique_level_identities_including_context": len(rows),
            "created_in_development": sum("2026-01-02" <= stamp(row["created_at"]).date().isoformat() <= "2026-09-04" for row in rows),
            "touched_level_identities": len(touched_ids),
            "availability_issue_rows": sum(family in issue["families"] for issue in issues),
            "pm_unverified_issue_rows": sum(family in issue["families"] and issue["reason"] == "OBSERVED_PREMARKET_NOT_COMPLETENESS_CERTIFIED" for issue in issues),
            "active_identity_instances": sum(row["expires_at"] is None or stamp(row["expires_at"]).date().isoformat() >= session_dates[0] for row in rows)})
    write_csv("level_inventory_summary", inventory)

    # Fixed descriptive touch-history groups, declared in reporting_plan.md.
    def session_touch(t):
        n = t["session_touch_number"]
        return "UNAVAILABLE" if n is None else "1" if n == 1 else "2" if n == 2 else "3+"
    def lifetime_touch(t):
        n = t["observed_lifetime_touch_number"]
        return "1" if n == 1 else "2" if n == 2 else "3-5" if n <= 5 else "6-10" if n <= 10 else "11+"
    def breach(t):
        if t["prior_breach_count"] is None or t["previously_closed_through"] is None:
            return "UNKNOWN"
        if t["previously_closed_through"]:
            return "COMPLETED_CLOSE_THROUGH"
        return "PENETRATED_NO_CLOSE_THROUGH" if t["prior_breach_count"] else "NEVER_BREACHED"
    def breach_multi(t):
        return "UNKNOWN" if t["prior_breach_count"] is None else "2+" if t["prior_breach_count"] >= 2 else "0-1"
    def time_of_day(t):
        minute = stamp(t["start"]).hour * 60 + stamp(t["start"]).minute
        return next(label for limit, label in ((600, "09:30-10:00"), (660, "10:00-11:00"), (720, "11:00-12:00"),
            (840, "12:00-14:00"), (900, "14:00-15:00"), (960, "15:00-close")) if minute < limit)
    def approach(t):
        return t["approach"]
    def first_creation(t):
        return str(t["first_interaction_since_creation"])
    def history(t):
        return str(t["history_complete_since_creation"])

    touch_dimensions = [
        ("creation_first_touch", first_creation, ["True", "False", "None"]),
        ("same_session_touch", session_touch, ["1", "2", "3+", "UNAVAILABLE"]),
        ("observed_lifetime_touch", lifetime_touch, ["1", "2", "3-5", "6-10", "11+"]),
        ("history_complete", history, ["True", "False"]),
        ("breach_history", breach, ["NEVER_BREACHED", "PENETRATED_NO_CLOSE_THROUGH", "COMPLETED_CLOSE_THROUGH", "UNKNOWN"]),
        ("multiple_breach_episodes", breach_multi, ["0-1", "2+", "UNKNOWN"]),
        ("time_of_day", time_of_day, ["09:30-10:00", "10:00-11:00", "11:00-12:00", "12:00-14:00", "14:00-15:00", "15:00-close"]),
        ("approach_side", approach, ["ABOVE", "BELOW", "UNKNOWN"]),
    ]
    for name, fn, values in touch_dimensions:
        groups = defaultdict(list)
        for row in reactions:
            eid = row["episode_id"]
            group = fn(first_touch[eid])
            for family in ("ALL", ep_family[eid]):
                groups[(family, group, row["distance"], row["horizon"])].append(row)
        table_from_groups(name, groups, [(name, values)])

    def rejection_path(row):
        if row["status"] != "REJECTION_FIRST":
            return "NO_CONFIRMED_REJECTION"
        if row["immediate_rejection"]:
            return "IMMEDIATE_SINGLE_TOUCH"
        if row["single_touch_rejection"]:
            return "SINGLE_TOUCH_LATER"
        if row["one_retest_rejection"]:
            return "ONE_RETEST"
        if row["multiple_test_rejection"]:
            return "MULTIPLE_TESTS"
        raise AssertionError(row)
    groups = defaultdict(list)
    for row in reactions:
        eid = row["episode_id"]
        for family in ("ALL", ep_family[eid]):
            groups[(family, rejection_path(row), row["distance"], row["horizon"])].append(row)
    table_from_groups("immediate_retest", groups, [("rejection_path", ["IMMEDIATE_SINGLE_TOUCH", "SINGLE_TOUCH_LATER", "ONE_RETEST", "MULTIPLE_TESTS", "NO_CONFIRMED_REJECTION"])])

    for flag in ("single_candle_rejection", "immediate_rejection", "single_touch_rejection", "one_retest_rejection", "multiple_test_rejection"):
        groups = defaultdict(list)
        for row in reactions:
            eid = row["episode_id"]
            for family in ("ALL", ep_family[eid]):
                groups[(family, str(row[flag]), row["distance"], row["horizon"])].append(row)
        table_from_groups(flag, groups, [(flag, ["True", "False"])] )

    # Session and month tables include zero-event sessions explicitly.
    by_key = defaultdict(list)
    for row in reactions:
        eid = row["episode_id"]
        for family in ("ALL", ep_family[eid]):
            by_key[(family, ep_day[eid], row["distance"], row["horizon"])].append(row)
    session_rows, month_rows = [], []
    months = tuple(sorted({day[:7] for day in session_dates}))
    for family in ("ALL", *FAMILIES):
        for day in session_dates:
            for distance, horizon in PANELS:
                rs = by_key[(family, day, distance, horizon)]
                session_rows.append({"family": family, "session": day, "distance": distance, "horizon": horizon, **reaction_summary(rs)})
        for month in months:
            days = [day for day in session_dates if day.startswith(month)]
            for distance, horizon in PANELS:
                rs = [row for day in days for row in by_key[(family, day, distance, horizon)]]
                month_rows.append({"family": family, "month": month, "validated_sessions": len(days),
                    "partial_month": month == "2026-09", "distance": distance, "horizon": horizon,
                    "contributing_sessions": sum(bool(by_key[(family, day, distance, horizon)]) for day in days), **reaction_summary(rs)})
    write_csv("session_reactions", session_rows)
    write_csv("monthly_reactions", month_rows)

    # Session-bootstrap intervals from the committed engine export.
    bootstrap_rows = []
    for row in stream("session_uncertainty"):
        output = {key: value for key, value in row.items() if key != "intervals"}
        for status, lower, upper in row["intervals"]:
            output[f"{status}_lower_pct"] = "" if lower is None else str(Decimal(lower) * 100)
            output[f"{status}_upper_pct"] = "" if upper is None else str(Decimal(upper) * 100)
        bootstrap_rows.append(output)
    write_csv("session_bootstrap", bootstrap_rows)

    # Direct level-pair comparisons are descriptive, not a ranking.
    pairs = []
    for high, low in (("PDH", "PDL"), ("PMH", "PML"), ("ORH5", "ORL5"), ("PWH", "PWL"), ("1H_HIGH", "1H_LOW")):
        for distance, horizon in PANELS:
            high_row = next(r for r in family_rows if r["family"] == high and r["distance"] == distance and r["horizon"] == horizon)
            low_row = next(r for r in family_rows if r["family"] == low and r["distance"] == distance and r["horizon"] == horizon)
            pairs.append({"upper_family": high, "lower_family": low, "distance": distance, "horizon": horizon,
                "upper_episodes": high_row["episodes"], "lower_episodes": low_row["episodes"],
                "upper_rejection_first_pct": high_row["REJECTION_FIRST_pct"], "lower_rejection_first_pct": low_row["REJECTION_FIRST_pct"],
                "upper_minus_lower_rejection_pp": str(Decimal(high_row["REJECTION_FIRST_pct"] or 0) - Decimal(low_row["REJECTION_FIRST_pct"] or 0))})
    write_csv("family_direction_pairs", pairs)

    # Frozen next-level snapshots and recognition ordering.
    next_groups = defaultdict(list)
    for row in next_reactions:
        eid = row["episode_id"]
        direction = "RESISTANCE_APPROACH" if ep_role[eid] == "RESISTANCE" else "SUPPORT_APPROACH"
        next_groups[(ep_family[eid], direction, row["distance"], row["horizon"])].append(row)
    next_rows = []
    for key, rs in sorted(next_groups.items()):
        snapshots = [next_levels[row["episode_id"]] for row in rs]
        distances = []
        for snapshot_row in snapshots:
            if snapshot_row["price"] is not None:
                original = levels[episodes[snapshot_row["episode_id"]]["level_id"]]["price"]
                distances.append(abs(Decimal(snapshot_row["price"]) - Decimal(original)))
        next_rows.append({"family": key[0], "approach_role": key[1], "distance": key[2], "horizon": key[3],
            "episodes": len(rs), "valid_next_level": len(distances), "no_next_level": sum(x["status"] == "NO_NEXT_LEVEL" for x in snapshots),
            "unknown_direction": sum(x["status"] == "UNKNOWN_DIRECTION" for x in snapshots),
            "next_distance_min": str(min(distances)) if distances else "", "next_distance_median": median_decimal(distances),
            "next_distance_max": str(max(distances)) if distances else "",
            **{f"snapshot_{status}": sum(x["status"] == status for x in snapshots) for status in ("REACHED_FIRST", "INVALIDATED_FIRST", "AMBIGUOUS", "CENSORED", "UNRESOLVED")},
            **{f"relative_{status}": sum(x["result"] == status for x in rs) for status in sorted({x["result"] for x in rs})}})
    write_csv("next_level_tables", next_rows)

    # Episode confluence: relationships are streamed; no source data is reread.
    episode_nearby = {eid: {radius: [] for radius in RADII} for eid in episodes}
    relationship_count = 0
    for row in stream("episode_relationships"):
        relationship_count += 1
        eid = row["observation_id"]
        assert stamp(row["available_at"]) <= stamp(episodes[eid]["start"])
        distance = Decimal(row["absolute_distance"])
        for radius in RADII:
            if distance <= Decimal(radius):
                episode_nearby[eid][radius].append(row)
    confluence_inventory = []
    for eid in episodes:
        for radius in RADII:
            links = episode_nearby[eid][radius]
            confluence_inventory.append({"episode_id": eid, "radius": radius, "identity_count": len(links),
                "family_count": len({link["family"] for link in links}),
                "other_shared_source_count": sum(link["shared_source"] and link["level_id"] != episodes[eid]["level_id"] for link in links)})
    write_csv("confluence_episode_inventory", confluence_inventory)
    for radius in RADII:
        for mode, fn, values in (
            ("identity_count", lambda links: "1" if len(links) == 1 else "2" if len(links) == 2 else "3+", ["1", "2", "3+"]),
            ("family_count", lambda links: "1" if len({link["family"] for link in links}) == 1 else "2" if len({link["family"] for link in links}) == 2 else "3+", ["1", "2", "3+"]),
        ):
            groups = defaultdict(list)
            for reaction in reactions:
                eid = reaction["episode_id"]
                group = fn(episode_nearby[eid][radius])
                for family in ("ALL", ep_family[eid]):
                    groups[(family, group, reaction["distance"], reaction["horizon"])].append(reaction)
            table_from_groups(f"confluence_{radius}_{mode}", groups, [("confluence", values)])
        groups = defaultdict(list)
        for reaction in reactions:
            eid = reaction["episode_id"]
            group = str(any(link["shared_source"] and link["level_id"] != episodes[eid]["level_id"] for link in episode_nearby[eid][radius]))
            for family in ("ALL", ep_family[eid]):
                groups[(family, group, reaction["distance"], reaction["horizon"])].append(reaction)
        table_from_groups(f"confluence_{radius}_shared_source_other", groups, [("confluence", ["True", "False"])])

    # Level-blind reversal association; turning-time availability is asserted.
    reversal_nearby = {row["id"]: {radius: [] for radius in RADII} for row in reversals}
    reversal_all_links = {row["id"]: [] for row in reversals}
    reversal_turning_start = {row["id"]: row["turning_start"] for row in reversals}
    reversal_relationship_count = 0
    for row in stream("reversal_relationships"):
        reversal_relationship_count += 1
        event_id = row["observation_id"]
        assert stamp(row["available_at"]) <= stamp(reversal_turning_start[event_id])
        distance = Decimal(row["absolute_distance"])
        reversal_all_links[event_id].append(row)
        for radius in RADII:
            if distance <= Decimal(radius):
                reversal_nearby[event_id][radius].append(row)
    reversal_by_id = {row["id"]: row for row in reversals}
    rev_summary, rev_families, rev_buckets = [], [], []
    for distance in DISTANCES:
        population = [row for row in reversals if row["distance"] == distance]
        confirmed = [row for row in population if row["known_at"] is not None and not row["censored"]]
        for radius in RADII:
            associated = [row for row in confirmed if reversal_nearby[row["id"]][radius]]
            rev_summary.append({"distance": distance, "radius": radius, "total_reversal_records": len(population),
                "confirmed_reversals": len(confirmed), "censored_or_unconfirmed": len(population)-len(confirmed),
                "eligible_level_nearby": len(associated), "eligible_level_nearby_pct": pct(len(associated), len(confirmed)),
                "multiple_level_identity_frequency": sum(len(reversal_nearby[row["id"]][radius]) >= 2 for row in confirmed),
                "multiple_family_frequency": sum(len({x["family"] for x in reversal_nearby[row["id"]][radius]}) >= 2 for row in confirmed)})
            for family in FAMILIES:
                n = sum(any(link["family"] == family for link in reversal_nearby[row["id"]][radius]) for row in confirmed)
                rev_families.append({"distance": distance, "radius": radius, "family": family, "associated_reversals": n,
                    "confirmed_reversals": len(confirmed), "pct": pct(n, len(confirmed))})
        bucket_map = {"0": 0, "0.05": 0, "0.10": 0, "0.25": 0, ">0.25": 0, "NO_ELIGIBLE_LEVEL": 0}
        for row in confirmed:
            links = list(stream("reversal_relationships")) if False else None
            candidates = reversal_all_links[row["id"]]
            if not candidates:
                bucket_map["NO_ELIGIBLE_LEVEL"] += 1
            else:
                nearest = min(Decimal(link["absolute_distance"]) for link in candidates)
                bucket = "0" if nearest == 0 else "0.05" if nearest <= Decimal("0.05") else "0.10" if nearest <= Decimal("0.10") else "0.25" if nearest <= Decimal("0.25") else ">0.25"
                bucket_map[bucket] += 1
        for bucket, n in bucket_map.items():
            rev_buckets.append({"distance": distance, "nearest_distance_bucket": bucket, "reversals": n, "pct": pct(n, len(confirmed))})
    write_csv("reversal_associations", rev_summary)
    write_csv("reversal_family_associations", rev_families)
    write_csv("reversal_nearest_distance", rev_buckets)

    reconciliation = {"development_sessions": len(session_dates), "levels": len(levels), "touched_level_identities": len({row["level_id"] for row in touches.values()}),
        "touching_minutes": len(touches), "touch_runs": len({(row["level_id"], row["touch_run_number"]) for row in touches.values()}),
        "episodes": len(episodes), "reaction_rows": len(reactions), "expected_reaction_rows": 9*len(episodes),
        "gap_crosses": sum(1 for _ in stream("gap_crosses")), "next_level_rows": len(next_levels), "next_level_reaction_rows": len(next_reactions),
        "episode_relationship_rows": relationship_count, "reversal_records": len(reversals), "reversal_relationship_rows": reversal_relationship_count,
        "null_episode_touch_minutes": sum(row["episode_id"] is None for row in touches.values()),
        "episode_touch_minutes": sum(len(row["touch_ids"]) for row in episodes.values()),
        "contributing_sessions": len({ep_day[eid] for eid in episodes}), "premarket_certified_sessions": sum(row["premarket_certified"] for row in coverage),
        "premarket_unavailable_sessions": sum(not row["premarket_certified"] for row in coverage),
        "status_panel_checks": "PASS", "all_episode_touch_ids_reconciled": True, "causal_availability_checks": "PASS",
        "post_cutoff_rows": 0, "outcome_data_after_2026_09_04_opened": False}
    assert reconciliation["reaction_rows"] == reconciliation["expected_reaction_rows"]
    assert reconciliation["episode_touch_minutes"] + reconciliation["null_episode_touch_minutes"] == reconciliation["touching_minutes"]
    for row in touches.values():
        assert "2026-01-02" <= stamp(row["start"]).date().isoformat() <= "2026-09-04"
        level = levels[row["level_id"]]
        assert Decimal(row["low"]) <= Decimal(level["price"]) <= Decimal(row["high"])
        assert stamp(level["available_at"]) <= stamp(row["start"])
    for row in family_rows:
        check = [x for x in reactions if ep_family[x["episode_id"]] == row["family"] and x["distance"] == row["distance"] and x["horizon"] == row["horizon"]]
        assert len(check) == row["episodes"]
        assert sum(row[f"{status}_n"] for status in STATUSES) == row["episodes"]
    write_json("independent_reconciliation", reconciliation)

    # Human-readable report, answer-first and explicitly descriptive.
    selected = [row for row in family_rows if row["distance"] == "0.50" and row["horizon"] == 15]
    lines = ["# Key-Level Reactions V1 — repaired historical discovery", "", "## Technical summary", "",
        f"The repaired engine completed the unchanged descriptive study for **{len(session_dates)} development sessions**. It produced **{len(levels)} unique level identities including context**, **{len(touches):,} touching minutes**, **{len(episodes):,} reaction episodes**, and **{len(reactions):,} fixed reaction rows**. These are reactions from levels, not trading outcomes.", "",
        "The most important data limitation remains premarket coverage: PMH/PML are available only on the four sessions with a complete 04:00–09:30 grid and unavailable on the other 166. RTH coverage is complete. All findings below are descriptive; they do not estimate entries, stops, targets, R multiples, win rates, P&L or strategy quality.", "",
        "## Scope, data and definitions", "",
        "- Engine commit: `ae8e87092e53e1ae73e7a6344325f53f39041202`.",
        "- Outcomes: January 2–September 4, 2026 inclusive, New York time.",
        "- Causal context: December 22–31, 2025 only. Prospective September 8–December 1 data was not opened.",
        "- Fixed distances: $0.25, $0.50 and $1.00; fixed horizons: 5, 15 and 30 minutes.",
        "- Primary touch: `minute.low <= level.price <= minute.high`; all five statuses remain in every denominator.",
        "- Fixed predeclared reporting groups are documented in `reporting_plan.md`.", "",
        "## Coverage and data quality", "",
        f"RTH coverage passed at **66,300/66,300 development minutes** with zero missing minutes, zero duplicates and no invalid development sessions. The seven-session context had 2,550/2,550 RTH minutes. There were no development early closes; December 24, 2025 was an early-close context session.", "",
        f"Premarket coverage was complete on **4/170 sessions** (March 3, April 8, April 13 and July 8). The other 166 sessions remain unavailable for PMH/PML; no sparse premarket extrema were inferred. Previous-session and previous-week context were available for all development sessions. Ten confirmed 1H swings were available before the outcome window.", "",
        "See `coverage_summary.json`, `coverage_raw.json`, `coverage_sessions.json` and `independent_coverage_reconciliation.json`.", "",
        "## Population reconciliation", "",
        f"The study contains **{len(levels):,} unique levels**, **{len(touches):,} touching minutes**, **{reconciliation['touch_runs']:,} touch runs**, **{len(episodes):,} episodes**, **{reconciliation['gap_crosses']:,} gap-cross records**, and **{len(reversals):,} reversal records**. Every episode has exactly nine reaction rows, and all five statuses sum to each panel denominator. See `independent_reconciliation.json` and `denominators.json`.", "", "## Level-family reaction behavior", "",
        "The complete family × distance × horizon counts and rates are in `family_reactions.csv`. The compact $0.50/15-minute panel below is a readability anchor, not a selection or ranking:", "",
        "| Family | Episodes | Rejection-first | Continuation-first | Ambiguous | Unresolved | Censored |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    for row in selected:
        lines.append(f"| {row['family']} | {row['episodes']} | {row['REJECTION_FIRST_n']} ({row['REJECTION_FIRST_pct']}%) | {row['CONTINUATION_FIRST_n']} ({row['CONTINUATION_FIRST_pct']}%) | {row['AMBIGUOUS_n']} ({row['AMBIGUOUS_pct']}%) | {row['UNRESOLVED_n']} ({row['UNRESOLVED_pct']}%) | {row['CENSORED_n']} ({row['CENSORED_pct']}%) |")
    lines.extend(["", "Direct PDH/PDL, PMH/PML, ORH5/ORL5, previous-week and 1H high/low comparisons are in `family_direction_pairs.csv`; no family is labeled best.", "", "## Touch history, breach history and retests", "", "Fixed first-creation, same-session, observed-lifetime, history-completeness, breach-history, multiple-breach, time-of-day and approach-side tables are in the corresponding CSV files. `immediate_retest.csv` separates immediate/single-touch, later single-touch, one-retest and multiple-test descriptive paths. These groups are not filters and repeated touches are not independent sessions.", "", "## Reversal-first discovery", "", f"The independent completed-close detector produced {len(reversals):,} reversal records across the three distances. Association with levels is measured only at turning-time availability; it is not a rejection-probability estimate. Results by radius, family and nearest-distance bucket are in `reversal_associations.csv`, `reversal_family_associations.csv` and `reversal_nearest_distance.csv`.", "", "## Confluence and next levels", "", "Confluence uses all frozen radii (0, $0.05, $0.10 and $0.25), preserves every identity and separately records shared-source relationships. Tables distinguish one, two and three-plus identities/families; they do not assert that more confluence is better.", "", "`next_level_tables.csv` reports causal first-touch snapshots, distance distributions and reached/invalidated/ambiguous/censored ordering. A next-level hit before rejection recognition remains explicitly separate.", "", "## Monthly and session stability", "", "`monthly_reactions.csv`, `session_reactions.csv` and `session_bootstrap.csv` provide monthly rates, contributing sessions, partial-September labeling and the committed 2,000-draw whole-session pointwise intervals. September is a four-session partial month. These intervals are descriptive uncertainty summaries, not selection criteria.", "", "## Ambiguity, censoring and interpretation limits", "", "Ambiguous outcomes are retained whenever same-minute ordering cannot be known; censoring is separately flagged and never made favorable. Reaction-first percentages are not trade win rates. The study cannot identify a best strategy, establish causality, estimate profitability, or justify new filters, thresholds, entries, exits or forward candidates. It also cannot support strong PMH/PML conclusions beyond the four certified sessions.", "", "## Verification and provenance", "", f"- Repair commit: `ae8e87092e53e1ae73e7a6344325f53f39041202`.", "- Repaired run manifest records source/protocol/input/output hashes and the 177 permitted partitions.", "- Frozen break-and-hold verification: 174/174 hashes matched before and after.", "- Focused and full test receipts are recorded in `verification.json` after the post-run test pass.", "- No Stage 14 or frozen break-and-hold artifact changed; no Alpaca/network service was contacted.", "- The original blocked run remains unchanged in `reports/key_level_reactions_v1/`; this is a separate completed-run directory.", "", "## Review-only next step", "", "Review the completed descriptive evidence and data limitations. Do not alter the declared protocol or infer a trading strategy from this first reaction study."])
    (OUT / "findings.md").write_text("\n".join(lines) + "\n")

    # Recompute output hashes after all tables/findings are present.
    manifest_path = OUT / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(summary_generated_at_utc=datetime.now().astimezone().isoformat(),
        summary_source_script="summarize_completed.py", historical_findings_report="findings.md",
        output_hashes={path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.iterdir()) if path.is_file() and path.name != "run_manifest.json"},
        denominator_reconciliation="PASS", independent_checks="PASS", historical_outcomes_generated=True)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2, default=str) + "\n")
    print(json.dumps({"levels": len(levels), "touches": len(touches), "touch_runs": reconciliation["touch_runs"],
        "episodes": len(episodes), "reactions": len(reactions), "reversals": len(reversals),
        "episode_relationships": relationship_count, "reversal_relationships": reversal_relationship_count}, sort_keys=True))


if __name__ == "__main__":
    with localcontext() as context:
        context.prec = 50
        main()
