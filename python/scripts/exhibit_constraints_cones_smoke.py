from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.audits_ep import entropy_production_step, stationary_distribution
from time_world.clock_audits import clock_metrics_from_run, simulate_with_maintenance
from time_world.constraints_cones import (
    adjacency_from_P,
    constraint_phi_forbid_pm1,
    constraint_phi_forbid_zero,
    constraint_r_constant,
    reachable_sizes,
)
from time_world.model import build_model, preset_record_drive
from time_world.utils import artifact_dir, write_json


def _mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else float("nan")


def _run_clock_metrics(
    states: list[tuple[int, int, int]],
    P: np.ndarray,
    *,
    steps: int,
    burn_in: int,
    seeds: list[int],
) -> dict[str, float]:
    tick_failure_rates = []
    drift_rates = []
    phi_change_rates = []
    expected_step_rates = []
    tick_rates = []
    tick_failure_rate_nan_count = 0

    for seed in seeds:
        run = simulate_with_maintenance(
            states,
            P,
            steps,
            seed,
            budget_total=0,
            burn_in=burn_in,
            start_idx=0,
        )
        metrics = clock_metrics_from_run(run)
        tick_failure_rate = metrics["tick_failure_rate"]
        tick_failure_rates.append(tick_failure_rate)
        if np.isnan(tick_failure_rate):
            tick_failure_rate_nan_count += 1
        drift_rates.append(metrics["drift_rate_per_1k"])
        phi_change_rates.append(metrics["phi_change_rate_per_1k"])
        expected_step_rates.append(metrics["expected_step_rate_per_1k"])
        tick_rates.append(metrics["tick_rate_per_1k"])

    return {
        "tick_failure_rate_mean": float(np.nanmean(tick_failure_rates))
        if tick_failure_rates
        else float("nan"),
        "tick_failure_rate_nan_count": tick_failure_rate_nan_count,
        "drift_rate_per_1k_mean": _mean(drift_rates),
        "phi_change_rate_per_1k_mean": _mean(phi_change_rates),
        "expected_step_rate_per_1k_mean": _mean(expected_step_rates),
        "tick_rate_per_1k_mean": _mean(tick_rates),
    }


def _ep_stats(P: np.ndarray) -> dict[str, float]:
    pi = stationary_distribution(P, tol=1e-12)
    ep_raw = entropy_production_step(P, pi, zero_mode="inf")
    ep_reg = entropy_production_step(P, pi, zero_mode="regularize", eps=1e-15)
    return {
        "ep_raw": float(ep_raw),
        "ep_reg": float(ep_reg),
    }


def main() -> None:
    base_params = preset_record_drive()

    regimes = {
        "unconstrained": {
            "params": {**base_params, "constraint_mask": None},
            "constraint_name": "none",
        },
        "r_constant": {
            "params": {**base_params, "constraint_mask": constraint_r_constant()},
            "constraint_name": "constraint_r_constant",
        },
        "phi_forbid_pm1": {
            "params": {
                **base_params,
                "constraint_mask": constraint_phi_forbid_pm1(base_params["n_phi"]),
            },
            "constraint_name": "constraint_phi_forbid_pm1",
        },
        "phi_no_ticks": {
            "params": {
                **base_params,
                "constraint_mask": constraint_phi_forbid_zero(),
            },
            "constraint_name": "constraint_phi_forbid_zero",
        },
    }

    t_max = 10
    steps = 60_000
    burn_in = 5_000
    seeds = [0, 1, 2]

    results = {}
    for name, regime in regimes.items():
        params = regime["params"]
        states, P = build_model(params)
        adj = adjacency_from_P(P, tol=0.0)
        sizes = reachable_sizes(adj, start_idx=0, t_max=t_max)

        ep_stats = _ep_stats(P)
        clock_stats = _run_clock_metrics(
            states, P, steps=steps, burn_in=burn_in, seeds=seeds
        )

        params_serialized = dict(params)
        params_serialized["constraint_mask"] = regime["constraint_name"]

        results[name] = {
            "params": params_serialized,
            "cone_sizes": sizes,
            "ep": ep_stats,
            "clock": clock_stats,
        }

    payload = {
        "run_name": "exhibit_constraints_cones_smoke",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "run_params": {
            "steps": steps,
            "burn_in": burn_in,
            "seeds": seeds,
            "t_max": t_max,
            "ep_tol": 1e-12,
            "ep_eps": 1e-15,
        },
        "results": results,
    }

    out_dir = artifact_dir("exhibit_constraints_cones_smoke")
    out_path = write_json(out_dir / "metadata.json", payload)

    rel_path = "artifacts/exhibit_constraints_cones_smoke/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
