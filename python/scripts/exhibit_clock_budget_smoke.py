from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.clock_audits import (
    clock_metrics_from_run,
    idempotence_defect_snap,
    simulate_with_maintenance,
)
from time_world.model import build_model, preset_record_drive
from time_world.utils import artifact_dir, write_json


def _stderr(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(len(values)))


def _summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": float("nan"), "stderr": float("nan")}
    return {"mean": float(np.mean(values)), "stderr": _stderr(values)}


def _summarize_nan_safe(values: list[float]) -> dict[str, float]:
    clean = [v for v in values if np.isfinite(v)]
    return _summarize(clean)


def _run_budget(
    states: list[tuple[int, int, int]],
    P: np.ndarray,
    *,
    steps: int,
    burn_in: int,
    budget_total: int,
    seeds: list[int],
    repair_cost_r_inc: int,
) -> dict[str, object]:
    metrics_accum: dict[str, list[float]] = {
        "tick_failure_rate": [],
        "tick_interval_variance": [],
        "drift_rate_per_1k": [],
        "maintenance_spend_per_1k": [],
        "retention_error": [],
        "phi_change_rate_per_1k": [],
        "expected_step_rate_per_1k": [],
        "tick_rate_per_1k": [],
    }

    for seed in seeds:
        run = simulate_with_maintenance(
            states,
            P,
            steps,
            seed,
            budget_total=budget_total,
            repair_cost_r_inc=repair_cost_r_inc,
            burn_in=burn_in,
            start_idx=0,
        )
        metrics = clock_metrics_from_run(run)
        for key in metrics_accum:
            metrics_accum[key].append(metrics[key])

    summary = {
        key: _summarize_nan_safe(values) for key, values in metrics_accum.items()
    }

    return summary


def _print_summary(budget_label: str, summary: dict[str, dict[str, float]]) -> None:
    print(
        "budget={label} tick_fail={tf:.4g}±{tf_err:.2g} "
        "tick_var={tv:.4g}±{tv_err:.2g} "
        "drift_1k={dr:.4g}±{dr_err:.2g} "
        "maint_1k={mr:.4g}±{mr_err:.2g} "
        "phi_change_1k={pc:.4g}±{pc_err:.2g} "
        "expected_1k={es:.4g}±{es_err:.2g} "
        "tick_1k={tr:.4g}±{tr_err:.2g} "
        "retention={re:.4g}±{re_err:.2g}".format(
            label=budget_label,
            tf=summary["tick_failure_rate"]["mean"],
            tf_err=summary["tick_failure_rate"]["stderr"],
            tv=summary["tick_interval_variance"]["mean"],
            tv_err=summary["tick_interval_variance"]["stderr"],
            dr=summary["drift_rate_per_1k"]["mean"],
            dr_err=summary["drift_rate_per_1k"]["stderr"],
            mr=summary["maintenance_spend_per_1k"]["mean"],
            mr_err=summary["maintenance_spend_per_1k"]["stderr"],
            pc=summary["phi_change_rate_per_1k"]["mean"],
            pc_err=summary["phi_change_rate_per_1k"]["stderr"],
            es=summary["expected_step_rate_per_1k"]["mean"],
            es_err=summary["expected_step_rate_per_1k"]["stderr"],
            tr=summary["tick_rate_per_1k"]["mean"],
            tr_err=summary["tick_rate_per_1k"]["stderr"],
            re=summary["retention_error"]["mean"],
            re_err=summary["retention_error"]["stderr"],
        )
    )


def main() -> None:
    params = preset_record_drive()
    params = dict(params)
    params["phase_noise"] = 0.12

    states, P = build_model(params)

    steps = 60_000
    burn_in = 5_000
    budgets_per_1k = [0, 50, 200]
    seeds = list(range(5))
    repair_cost_r_inc = 1

    budget_totals = {
        b: int(round(b * steps / 1000.0)) for b in budgets_per_1k
    }

    idempotence_defect = idempotence_defect_snap(
        n_phi=params["n_phi"], samples=4000, seed=0
    )

    results = {}
    for b in budgets_per_1k:
        summary = _run_budget(
            states,
            P,
            steps=steps,
            burn_in=burn_in,
            budget_total=budget_totals[b],
            seeds=seeds,
            repair_cost_r_inc=repair_cost_r_inc,
        )
        summary["idempotence_defect"] = {
            "mean": idempotence_defect,
            "stderr": 0.0,
        }
        results[str(b)] = summary

    payload = {
        "run_name": "exhibit_clock_budget_smoke",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "params": {
            "preset": "record_drive",
            "model_params": params,
            "steps": steps,
            "burn_in": burn_in,
            "budgets_per_1k": budgets_per_1k,
            "budget_totals": budget_totals,
            "seeds": seeds,
            "repair_cost_r_inc": repair_cost_r_inc,
            "idempotence_samples": 4000,
        },
        "results": results,
    }

    out_dir = artifact_dir("exhibit_clock_budget_smoke")
    out_path = write_json(out_dir / "metadata.json", payload)

    print("Preset: record_drive (phase_noise=0.12)")
    for b in budgets_per_1k:
        _print_summary(str(b), results[str(b)])
    rel_path = "artifacts/exhibit_clock_budget_smoke/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
