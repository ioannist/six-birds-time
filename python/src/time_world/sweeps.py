from __future__ import annotations

from typing import Iterable

import numpy as np

from time_world.audits_ep import entropy_production_step, stationary_distribution
from time_world.clock_audits import clock_metrics_from_run, simulate_with_maintenance
from time_world.constraints_cones import constraint_phi_step_only, constraint_r_constant
from time_world.enablement import run_enablement
from time_world.holonomy import omega_from_samples, protocol_A_identity, protocol_B_even, protocol_C_odd
from time_world.model import build_model, preset_record_drive


def generate_cases() -> list[dict]:
    drive_strength_vals = [0.0, 0.6]
    phase_noise_vals = [0.02, 0.12]
    record_coupling_vals = [0.0, 0.5]
    constraint_modes = ["none", "r_constant", "phi_step_only", "odd_phi_only"]

    cases: list[dict] = []
    for d in drive_strength_vals:
        for n in phase_noise_vals:
            for rc in record_coupling_vals:
                for cm in constraint_modes:
                    case_id = f"d{d}_n{n}_rc{rc}_c{cm}"
                    cases.append(
                        {
                            "case_id": case_id,
                            "drive_strength": d,
                            "phase_noise": n,
                            "record_coupling": rc,
                            "constraint_mode": cm,
                        }
                    )
    return cases


def make_constraint_mask(mode: str, n_x: int, n_phi: int) -> tuple[str, object | None]:
    if mode == "none":
        return "none", None
    if mode == "r_constant":
        return "r_constant", constraint_r_constant()
    if mode == "phi_step_only":
        return "phi_step_only", constraint_phi_step_only(n_phi)
    if mode == "odd_phi_only":
        def _odd_phi_only(_from_state, to_state):
            return (to_state[1] % 2) == 1
        return "odd_phi_only", _odd_phi_only
    raise ValueError(f"Unknown constraint_mode: {mode}")


def _stderr(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(len(values)))


def _summary(values: list[float]) -> dict[str, float]:
    return {"mean": float(np.mean(values)), "stderr": _stderr(values)}


def run_case_metrics(
    case: dict,
    *,
    seeds: list[int],
    steps: int,
    burn_in: int,
    stride: int,
    alpha_kl: float,
) -> dict:
    base_params = preset_record_drive()
    params = dict(base_params)
    params["n_r"] = 8
    params["drive_strength"] = case["drive_strength"]
    params["phase_noise"] = case["phase_noise"]
    params["record_coupling"] = case["record_coupling"]

    constraint_name, constraint_mask = make_constraint_mask(
        case["constraint_mode"], params["n_x"], params["n_phi"]
    )
    params["constraint_mask"] = constraint_mask

    states, P = build_model(params)

    pi = stationary_distribution(P, tol=1e-12)
    ep_raw = entropy_production_step(P, pi, zero_mode="inf")
    ep_reg = entropy_production_step(P, pi, zero_mode="regularize", eps=1e-15)

    tick_failure_rates: list[float] = []
    drift_rates: list[float] = []
    phi_change_rates: list[float] = []
    expected_step_rates: list[float] = []
    tick_rates: list[float] = []
    H_vals: list[float] = []

    proto_a = protocol_A_identity()
    proto_b = protocol_B_even(params["n_phi"])
    proto_c = protocol_C_odd(params["n_phi"])

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
        tick_failure_rates.append(metrics["tick_failure_rate"])
        drift_rates.append(metrics["drift_rate_per_1k"])
        phi_change_rates.append(metrics["phi_change_rate_per_1k"])
        expected_step_rates.append(metrics["expected_step_rate_per_1k"])
        tick_rates.append(metrics["tick_rate_per_1k"])

        traj = run["traj"]
        samples = [states[int(idx)] for idx in traj[::stride]]
        omega_ab = omega_from_samples(proto_a, proto_b, samples)["omega_mean"]
        omega_bc = omega_from_samples(proto_b, proto_c, samples)["omega_mean"]
        omega_ca = omega_from_samples(proto_c, proto_a, samples)["omega_mean"]
        H_vals.append(omega_ab + omega_bc + omega_ca)

    results = {
        "case_id": case["case_id"],
        "drive_strength": case["drive_strength"],
        "phase_noise": case["phase_noise"],
        "record_coupling": case["record_coupling"],
        "constraint_mode": case["constraint_mode"],
        "constraint_name": constraint_name,
        "ep_raw": float(ep_raw),
        "ep_reg": float(ep_reg),
        "tick_failure_rate_mean": _summary(tick_failure_rates)["mean"],
        "tick_failure_rate_stderr": _summary(tick_failure_rates)["stderr"],
        "drift_rate_per_1k_mean": _summary(drift_rates)["mean"],
        "drift_rate_per_1k_stderr": _summary(drift_rates)["stderr"],
        "phi_change_rate_per_1k_mean": _summary(phi_change_rates)["mean"],
        "phi_change_rate_per_1k_stderr": _summary(phi_change_rates)["stderr"],
        "expected_step_rate_per_1k_mean": _summary(expected_step_rates)["mean"],
        "expected_step_rate_per_1k_stderr": _summary(expected_step_rates)["stderr"],
        "tick_rate_per_1k_mean": _summary(tick_rates)["mean"],
        "tick_rate_per_1k_stderr": _summary(tick_rates)["stderr"],
        "holonomy_H_mean": _summary(H_vals)["mean"],
        "holonomy_H_stderr": _summary(H_vals)["stderr"],
        "steps": steps,
        "burn_in": burn_in,
        "stride": stride,
        "seeds": seeds,
        "alpha_kl": alpha_kl,
    }
    return results


def run_enablement_sweep(
    *,
    drive_strength_vals: Iterable[float],
    phase_noise_vals: Iterable[float],
    seeds: Iterable[int],
    steps: int,
    burn_in: int,
    window: int,
    threshold: float,
    alpha: float = 1.0,
) -> list[dict]:
    rows: list[dict] = []
    for drive_strength in drive_strength_vals:
        for phase_noise in phase_noise_vals:
            params = {
                "n_x": 4,
                "n_phi": 8,
                "n_r": 1,
                "p_x": 0.7,
                "p_phi": 0.25,
                "drive_strength": drive_strength,
                "phase_noise": phase_noise,
                "record_coupling": 0.0,
                "record_backslide_prob": 0.0,
                "x_phi_coupling": 1.0,
                "constraint_mask": None,
            }
            states, P = build_model(params)
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
                row = {
                    "drive_strength": drive_strength,
                    "phase_noise": phase_noise,
                    "seed": seed,
                    "birth_step": outcome["birth_step"],
                    "gap_pre": outcome["gap_pre"],
                    "gap_post": outcome["gap_post"],
                    "nll1_pre": outcome["nll1_pre"],
                    "nll2_pre": outcome["nll2_pre"],
                    "nll1_post": outcome["nll1_post"],
                    "nll2_post": outcome["nll2_post"],
                    "steps": steps,
                    "burn_in": burn_in,
                    "window": window,
                    "threshold": threshold,
                    "alpha": alpha,
                }
                rows.append(row)
    return rows
