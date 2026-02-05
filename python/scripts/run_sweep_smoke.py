from __future__ import annotations

from pathlib import Path
import sys
import csv

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.sweeps import generate_cases, run_case_metrics, run_enablement_sweep
from time_world.utils import artifact_dir, write_json


def _min_median_max(values: list[float]) -> dict[str, float]:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return {"min": float("nan"), "median": float("nan"), "max": float("nan")}
    return {
        "min": float(np.min(arr)),
        "median": float(np.median(arr)),
        "max": float(np.max(arr)),
    }


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    cases = generate_cases()
    seeds = [0, 1]
    steps = 30_000
    burn_in = 3_000
    stride = 10
    alpha_kl = 1.0

    case_results = []
    for case in cases:
        case_results.append(
            run_case_metrics(
                case,
                seeds=seeds,
                steps=steps,
                burn_in=burn_in,
                stride=stride,
                alpha_kl=alpha_kl,
            )
        )

    enablement_rows = run_enablement_sweep(
        drive_strength_vals=[0.0, 0.6],
        phase_noise_vals=[0.02, 0.12],
        seeds=[0, 1, 2],
        steps=80_000,
        burn_in=5_000,
        window=20_000,
        threshold=0.02,
        alpha=1.0,
    )

    out_dir = artifact_dir("sweeps/sweep_smoke")
    results_path = out_dir / "results.csv"
    enablement_path = out_dir / "enablement.csv"
    summary_path = out_dir / "summary.json"

    results_fields = [
        "case_id",
        "drive_strength",
        "phase_noise",
        "record_coupling",
        "constraint_mode",
        "constraint_name",
        "ep_raw",
        "ep_reg",
        "tick_failure_rate_mean",
        "tick_failure_rate_stderr",
        "drift_rate_per_1k_mean",
        "drift_rate_per_1k_stderr",
        "phi_change_rate_per_1k_mean",
        "phi_change_rate_per_1k_stderr",
        "expected_step_rate_per_1k_mean",
        "expected_step_rate_per_1k_stderr",
        "tick_rate_per_1k_mean",
        "tick_rate_per_1k_stderr",
        "holonomy_H_mean",
        "holonomy_H_stderr",
        "steps",
        "burn_in",
        "stride",
        "seeds",
        "alpha_kl",
    ]
    _write_csv(results_path, case_results, results_fields)

    enablement_fields = [
        "drive_strength",
        "phase_noise",
        "seed",
        "birth_step",
        "gap_pre",
        "gap_post",
        "nll1_pre",
        "nll2_pre",
        "nll1_post",
        "nll2_post",
        "steps",
        "burn_in",
        "window",
        "threshold",
        "alpha",
    ]
    _write_csv(enablement_path, enablement_rows, enablement_fields)

    ep_reg_vals = [row["ep_reg"] for row in case_results if np.isfinite(row["ep_reg"])]
    ep_raw_vals = [row["ep_raw"] for row in case_results if np.isfinite(row["ep_raw"])]
    ep_raw_inf = sum(1 for row in case_results if not np.isfinite(row["ep_raw"]))

    tick_vals = [row["tick_failure_rate_mean"] for row in case_results]
    hol_vals = [row["holonomy_H_mean"] for row in case_results]
    expected_step_vals = [row["expected_step_rate_per_1k_mean"] for row in case_results]

    birth_steps = [row["birth_step"] for row in enablement_rows if row["birth_step"] is not None]

    summary = {
        "parameter_ranges": {
            "drive_strength": [0.0, 0.6],
            "phase_noise": [0.02, 0.12],
            "record_coupling": [0.0, 0.5],
            "constraint_mode": ["none", "r_constant", "phi_step_only", "odd_phi_only"],
        },
        "metrics": {
            "ep_reg": _min_median_max(ep_reg_vals),
            "ep_raw_finite": {**_min_median_max(ep_raw_vals), "count_inf": ep_raw_inf},
            "tick_failure_rate_mean": _min_median_max(tick_vals),
            "holonomy_H_mean": _min_median_max(hol_vals),
            "expected_step_rate_per_1k_mean": _min_median_max(expected_step_vals),
            "enablement_birth_step": _min_median_max(birth_steps),
        },
        "run_params": {
            "cases": len(case_results),
            "seeds": seeds,
            "steps": steps,
            "burn_in": burn_in,
            "stride": stride,
            "alpha_kl": alpha_kl,
        },
        "enablement_params": {
            "drive_strength_vals": [0.0, 0.6],
            "phase_noise_vals": [0.02, 0.12],
            "seeds": [0, 1, 2],
            "steps": 80_000,
            "burn_in": 5_000,
            "window": 20_000,
            "threshold": 0.02,
            "alpha": 1.0,
        },
    }

    write_json(summary_path, summary)

    print("artifacts/sweeps/sweep_smoke/results.csv")
    print("artifacts/sweeps/sweep_smoke/enablement.csv")
    print("artifacts/sweeps/sweep_smoke/summary.json")
    print(
        "expected_step_rate_per_1k_mean: "
        "min={min} median={median} max={max}".format(
            **summary["metrics"]["expected_step_rate_per_1k_mean"]
        )
    )
    print(
        "holonomy_H_mean: min={min} median={median} max={max}".format(
            **summary["metrics"]["holonomy_H_mean"]
        )
    )


if __name__ == "__main__":
    main()
