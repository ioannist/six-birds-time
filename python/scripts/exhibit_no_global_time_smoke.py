from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.holonomy import (
    omega_from_samples,
    protocol_A_identity,
    protocol_B_even,
    protocol_C_odd,
)
from time_world.model import build_model, preset_reversibleish, simulate
from time_world.utils import artifact_dir, write_json


def _stderr(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(len(values)))


def _summarize(values: list[float]) -> dict[str, float]:
    return {"mean": float(np.mean(values)), "stderr": _stderr(values)}


def _odd_phi_constraint(
    _from_state: tuple[int, int, int], to_state: tuple[int, int, int]
) -> bool:
    return (to_state[1] % 2) == 1


def _run_regime(
    params: dict,
    *,
    constraint_label: str,
    steps: int,
    burn_in: int,
    stride: int,
    seeds: list[int],
) -> dict:
    states, P = build_model(params)

    proto_a = protocol_A_identity()
    proto_b = protocol_B_even(params["n_phi"])
    proto_c = protocol_C_odd(params["n_phi"])

    per_seed = []
    omega_ab_vals = []
    omega_bc_vals = []
    omega_ca_vals = []
    H_vals = []

    for seed in seeds:
        traj = simulate(P, steps + burn_in, seed)
        traj = traj[burn_in:]
        samples = [states[int(idx)] for idx in traj[::stride]]

        omega_ab = omega_from_samples(proto_a, proto_b, samples)["omega_mean"]
        omega_bc = omega_from_samples(proto_b, proto_c, samples)["omega_mean"]
        omega_ca = omega_from_samples(proto_c, proto_a, samples)["omega_mean"]

        H_seed = omega_ab + omega_bc + omega_ca

        omega_ab_vals.append(omega_ab)
        omega_bc_vals.append(omega_bc)
        omega_ca_vals.append(omega_ca)
        H_vals.append(H_seed)

        per_seed.append(
            {
                "seed": seed,
                "omega_ab": omega_ab,
                "omega_bc": omega_bc,
                "omega_ca": omega_ca,
                "H": H_seed,
            }
        )

    summary = {
        "H": _summarize(H_vals),
        "omega_ab": _summarize(omega_ab_vals),
        "omega_bc": _summarize(omega_bc_vals),
        "omega_ca": _summarize(omega_ca_vals),
    }

    params_serialized = dict(params)
    params_serialized["constraint_mask"] = constraint_label

    return {
        "params": params_serialized,
        "per_seed": per_seed,
        "summary": summary,
    }


def main() -> None:
    base = preset_reversibleish()
    base = dict(base)
    base["n_r"] = 1
    base["drive_strength"] = 0.6
    base["phase_noise"] = 0.05

    steps = 200_000
    burn_in = 10_000
    stride = 10
    seeds = list(range(10))

    regime_a_params = dict(base)
    regime_a_params["constraint_mask"] = None

    regime_b_params = dict(base)
    regime_b_params["constraint_mask"] = _odd_phi_constraint

    results = {
        "nonzero": _run_regime(
            regime_a_params,
            constraint_label="none",
            steps=steps,
            burn_in=burn_in,
            stride=stride,
            seeds=seeds,
        ),
        "control": _run_regime(
            regime_b_params,
            constraint_label="odd_phi_only",
            steps=steps,
            burn_in=burn_in,
            stride=stride,
            seeds=seeds,
        ),
    }

    payload = {
        "run_name": "exhibit_no_global_time_smoke",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "protocols": {
            "A": "identity clock: (x,phi,r)->(x,phi,r); clock=phi",
            "B": "coarse phi to b=phi//2, lift even 2b; clock=2b",
            "C": "coarse phi to b=phi//2, lift odd 2b+1; clock=2b+1",
        },
        "run_params": {
            "steps": steps,
            "burn_in": burn_in,
            "stride": stride,
            "seeds": seeds,
        },
        "results": results,
    }

    out_dir = artifact_dir("exhibit_no_global_time_smoke")
    out_path = write_json(out_dir / "metadata.json", payload)

    rel_path = "artifacts/exhibit_no_global_time_smoke/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
