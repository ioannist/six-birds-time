from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Iterable

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.audits_path_kl import (
    apply_lens,
    estimate_sigma_Ts_for_lenses,
    lens_drop_phi,
    lens_drop_r,
    lens_identity,
)
from time_world.model import build_model, preset_record_drive, preset_reversibleish, simulate
from time_world.utils import artifact_dir, write_json


def _stderr(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(len(values)))


def _summarize(values: list[float]) -> dict[str, float]:
    return {"mean": float(np.mean(values)), "stderr": _stderr(values)}


def _collect_run(
    P: np.ndarray,
    Ts: Iterable[int],
    lens_maps: dict[str, np.ndarray],
    *,
    steps: int,
    burn_in: int,
    seed: int,
    alpha: float,
) -> dict[int, dict[str, object]]:
    traj = simulate(P, steps + burn_in, seed=seed)
    traj = traj[burn_in:]
    return estimate_sigma_Ts_for_lenses(traj, Ts, lens_maps, alpha=alpha)


def _run_preset(name: str, params: dict) -> dict[str, object]:
    states, P = build_model(params)

    lens_maps = {
        "identity": apply_lens(states, lens_identity)[1],
        "drop_r": apply_lens(states, lens_drop_r)[1],
        "drop_phi": apply_lens(states, lens_drop_phi)[1],
    }

    Ts = (1, 3, 5)
    steps = 80_000
    burn_in = 5_000
    seeds = list(range(10))
    alpha = 1.0

    accum: dict[int, dict[str, list[float]]] = {
        T: {"micro": [], "identity": [], "drop_r": [], "drop_phi": []} for T in Ts
    }

    for seed in seeds:
        results = _collect_run(
            P,
            Ts,
            lens_maps,
            steps=steps,
            burn_in=burn_in,
            seed=seed,
            alpha=alpha,
        )
        for T in Ts:
            accum[T]["micro"].append(results[T]["micro"])
            for lens_name, value in results[T]["lenses"].items():
                accum[T][lens_name].append(value)

    summary: dict[int, dict[str, dict[str, float]]] = {}
    for T in Ts:
        summary[T] = {
            key: _summarize(values) for key, values in accum[T].items()
        }

    return {
        "name": name,
        "params": params,
        "steps": steps,
        "burn_in": burn_in,
        "alpha": alpha,
        "seeds": seeds,
        "Ts": list(Ts),
        "results": summary,
    }


def _print_summary(result: dict[str, object]) -> None:
    name = result["name"]
    print(f"Preset: {name}")
    for T in result["Ts"]:
        row = result["results"][T]
        print(
            "T={T} micro={micro:.6g}±{micro_err:.2g} "
            "identity={identity:.6g}±{identity_err:.2g} "
            "drop_r={drop_r:.6g}±{drop_r_err:.2g} "
            "drop_phi={drop_phi:.6g}±{drop_phi_err:.2g}".format(
                T=T,
                micro=row["micro"]["mean"],
                micro_err=row["micro"]["stderr"],
                identity=row["identity"]["mean"],
                identity_err=row["identity"]["stderr"],
                drop_r=row["drop_r"]["mean"],
                drop_r_err=row["drop_r"]["stderr"],
                drop_phi=row["drop_phi"]["mean"],
                drop_phi_err=row["drop_phi"]["stderr"],
            )
        )
    print()


def main() -> None:
    results = [
        _run_preset("record_drive", preset_record_drive()),
        _run_preset("reversibleish", preset_reversibleish()),
    ]

    timestamp_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "run_name": "exhibit_dpi_smoke",
        "timestamp_utc": timestamp_utc,
        "results": results,
    }

    out_dir = artifact_dir("exhibit_dpi_smoke")
    out_path = write_json(out_dir / "metadata.json", payload)

    for result in results:
        _print_summary(result)

    rel_path = "artifacts/exhibit_dpi_smoke/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
