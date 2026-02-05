from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.enablement import run_enablement
from time_world.model import build_model
from time_world.utils import artifact_dir, write_json


def _summary(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": None, "std": None}
    arr = np.array(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
    }


def main() -> None:
    base_params = {
        "n_x": 4,
        "n_phi": 8,
        "n_r": 1,
        "p_x": 0.7,
        "p_phi": 0.25,
        "drive_strength": 0.6,
        "phase_noise": 0.02,
        "record_coupling": 0.0,
        "record_backslide_prob": 0.0,
        "constraint_mask": None,
    }

    steps = 120_000
    burn_in = 5_000
    window = 20_000
    threshold = 0.10
    alpha = 1.0
    seeds = [0, 1, 2]

    regimes = {
        "enablement": {**base_params, "x_phi_coupling": 1.0},
        "control": {**base_params, "x_phi_coupling": 0.0},
    }

    results = {}
    for name, params in regimes.items():
        states, P = build_model(params)
        per_seed = []
        for seed in seeds:
            outcome = run_enablement(
                states,
                P,
                seed=seed,
                steps=steps,
                burn_in=burn_in,
                window=window,
                threshold=threshold,
                alpha=alpha,
            )
            per_seed.append(outcome)

        gap_pre_vals = [r["gap_pre"] for r in per_seed if r["gap_pre"] is not None]
        gap_post_vals = [r["gap_post"] for r in per_seed if r["gap_post"] is not None]
        birth_steps = [r["birth_step"] for r in per_seed if r["birth_step"] is not None]

        summary = {
            "gap_pre": _summary(gap_pre_vals),
            "gap_post": _summary(gap_post_vals),
            "birth_step": _summary(birth_steps),
        }

        results[name] = {
            "params": params,
            "per_seed": per_seed,
            "summary": summary,
        }

    payload = {
        "run_name": "exhibit_enablement_birth_smoke",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "run_params": {
            "steps": steps,
            "burn_in": burn_in,
            "window": window,
            "threshold": threshold,
            "alpha": alpha,
            "seeds": seeds,
        },
        "results": results,
    }

    out_dir = artifact_dir("exhibit_enablement_birth_smoke")
    out_path = write_json(out_dir / "metadata.json", payload)

    rel_path = "artifacts/exhibit_enablement_birth_smoke/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
