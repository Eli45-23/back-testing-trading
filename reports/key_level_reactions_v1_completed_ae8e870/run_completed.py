"""Run the unchanged KLR V1 study into this isolated completed-run directory."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = ROOT / "reports" / "key_level_reactions_v1" / "run_study.py"
COMMIT = "ae8e87092e53e1ae73e7a6344325f53f39041202"


def load_base():
    spec = importlib.util.spec_from_file_location("klr_base_driver", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load committed KLR audit driver")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.OUT = OUT
    mod.COMMIT = COMMIT
    return mod


def main():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != COMMIT:
        raise RuntimeError(f"Expected repaired engine commit {COMMIT}, found {head}")
    if subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).strip():
        raise RuntimeError("Tracked worktree changes present; refusing study run")
    mod = load_base()
    data, calendar, manifest = mod.coverage()
    manifest.update(
        run_kind="COMPLETED_REPAIRED_RERUN",
        baseline_blocked_run_directory="reports/key_level_reactions_v1",
        historical_outcomes_generated=False,
        source_commit=COMMIT,
        generated_at_utc=str(datetime.now(timezone.utc)),
    )
    mod.run_outcomes(data, calendar, manifest)
    manifest_path = OUT / "run_manifest.json"
    manifest_data = json.loads(manifest_path.read_text())
    manifest_data.update(
        historical_outcomes_generated=True,
        completed_run_directory=str(OUT.relative_to(ROOT)),
        completed_at_utc=str(datetime.now(timezone.utc)),
    )
    manifest_path.write_text(json.dumps(manifest_data, sort_keys=True, indent=2, default=str) + "\n")
    print("COMPLETED_RUN", json.dumps({
        "directory": str(OUT.relative_to(ROOT)),
        "git_commit": COMMIT,
        "frozen_hashes": manifest_data.get("frozen_hashes_after_outcomes"),
        "opened_partitions": len(manifest_data.get("opened_historical_partitions", [])),
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
