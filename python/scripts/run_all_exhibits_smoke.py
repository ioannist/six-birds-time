from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> None:
    repo_root = _repo_root()
    python_exe = sys.executable

    scripts = [
        "python/scripts/exhibit_dpi_smoke.py",
        "python/scripts/exhibit_clock_budget_smoke.py",
        "python/scripts/exhibit_enablement_birth_smoke.py",
        "python/scripts/exhibit_constraints_cones_smoke.py",
        "python/scripts/exhibit_no_global_time_smoke.py",
        "python/scripts/exhibit_no_signalling_toy_smoke.py",
        "python/scripts/run_sweep_smoke.py",
    ]

    for script in scripts:
        print(f"START {script}", flush=True)
        subprocess.run([python_exe, script], cwd=repo_root, check=True)
        print(f"OK {script}", flush=True)

    expected_artifacts = [
        "artifacts/exhibit_dpi_smoke/metadata.json",
        "artifacts/exhibit_clock_budget_smoke/metadata.json",
        "artifacts/exhibit_enablement_birth_smoke/metadata.json",
        "artifacts/exhibit_constraints_cones_smoke/metadata.json",
        "artifacts/exhibit_no_global_time_smoke/metadata.json",
        "artifacts/exhibit_no_signalling_toy/metadata.json",
        "artifacts/sweeps/sweep_smoke/results.csv",
        "artifacts/sweeps/sweep_smoke/enablement.csv",
        "artifacts/sweeps/sweep_smoke/summary.json",
    ]

    print("EXPECTED ARTIFACTS")
    for path in expected_artifacts:
        print(path)

    missing = [p for p in expected_artifacts if not (repo_root / p).exists()]
    if missing:
        print("MISSING ARTIFACTS")
        for path in missing:
            print(path)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
