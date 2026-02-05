from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from time_world.utils import seed_everything


@dataclass(frozen=True)
class MaintenanceRun:
    traj: np.ndarray
    repairs_used: int
    drift_detected_pre: int
    drift_unrepaired_post: int
    tick_times: list[int]
    n_phi: int
    n_r: int
    drift_flags: np.ndarray


def simulate_with_maintenance(
    states: list[tuple[int, int, int]],
    P: np.ndarray,
    steps: int,
    seed: int,
    *,
    budget_total: int,
    repair_cost_r_inc: int = 1,
    burn_in: int = 0,
    start_idx: int = 0,
) -> dict:
    if steps < 0:
        raise ValueError("steps must be >= 0")
    if burn_in < 0:
        raise ValueError("burn_in must be >= 0")
    if budget_total < 0:
        raise ValueError("budget_total must be >= 0")

    seed_everything(seed)

    n_states = len(states)
    if n_states == 0:
        raise ValueError("states must be non-empty")
    if P.shape != (n_states, n_states):
        raise ValueError("P has incorrect shape")
    if start_idx < 0 or start_idx >= n_states:
        raise ValueError("start_idx out of range")

    phis = np.array([state[1] for state in states], dtype=int)
    rs = np.array([state[2] for state in states], dtype=int)
    n_phi = int(phis.max()) + 1
    n_r = int(rs.max()) + 1

    index = {state: i for i, state in enumerate(states)}

    total_steps = steps + burn_in
    traj_full = np.empty(total_steps + 1, dtype=int)
    traj_full[0] = start_idx

    repairs_used_total = 0
    repairs_used = 0
    drift_detected_pre = 0
    drift_unrepaired_post = 0
    phi_change_count = 0
    expected_step_count = 0
    backward_step_count = 0
    slip_step_count = 0
    drift_flags: list[bool] = []

    for t in range(total_steps):
        current_idx = traj_full[t]
        next_idx = int(np.random.choice(n_states, p=P[current_idx]))

        x_prev, phi_prev, _r_prev = states[current_idx]
        x_prop, phi_prop, r_prop = states[next_idx]

        expected = (phi_prev + 1) % n_phi
        drift_pre = (phi_prop != phi_prev) and (phi_prop != expected)

        repaired = False
        phi_next = phi_prop
        r_next = r_prop
        x_next = x_prop

        if drift_pre and repairs_used_total < budget_total:
            phi_next = expected
            r_next = min(n_r - 1, r_prop + repair_cost_r_inc)
            next_idx = index[(x_next, phi_next, r_next)]
            repairs_used_total += 1
            repaired = True

        drift_post = (phi_next != phi_prev) and (phi_next != expected)

        traj_full[t + 1] = next_idx

        if t >= burn_in:
            if drift_pre:
                drift_detected_pre += 1
            if drift_post:
                drift_unrepaired_post += 1
            if repaired:
                repairs_used += 1
            phi_changed = phi_next != phi_prev
            if phi_changed:
                phi_change_count += 1
            if phi_next == expected:
                expected_step_count += 1
            if phi_next == (phi_prev - 1) % n_phi:
                backward_step_count += 1
            if phi_changed and phi_next not in {expected, (phi_prev - 1) % n_phi}:
                slip_step_count += 1
            drift_flags.append(drift_post)

    traj = traj_full[burn_in:]
    phi_traj = np.array([states[idx][1] for idx in traj], dtype=int)
    tick_times = np.where(phi_traj == 0)[0].tolist()

    return {
        "traj": traj,
        "repairs_used": repairs_used,
        "drift_detected_pre": drift_detected_pre,
        "drift_unrepaired_post": drift_unrepaired_post,
        "phi_change_count": phi_change_count,
        "expected_step_count": expected_step_count,
        "backward_step_count": backward_step_count,
        "slip_step_count": slip_step_count,
        "tick_times": tick_times,
        "n_phi": n_phi,
        "n_r": n_r,
        "drift_flags": np.array(drift_flags, dtype=bool),
    }


def clock_metrics_from_run(run_dict: dict) -> dict:
    traj = run_dict["traj"]
    tick_times = run_dict["tick_times"]
    drift_flags = run_dict["drift_flags"]

    steps = int(traj.shape[0] - 1)
    tick_count = len(tick_times)

    tick_interval_variance = float("nan")
    if len(tick_times) >= 3:
        intervals = np.diff(np.array(tick_times, dtype=int))
        if intervals.size >= 2:
            tick_interval_variance = float(np.var(intervals, ddof=1))

    tick_failure_rate = float("nan")
    if len(tick_times) >= 2:
        cycle_count = len(tick_times) - 1
        drift_prefix = np.zeros(steps + 1, dtype=int)
        drift_prefix[1:] = np.cumsum(drift_flags.astype(int))
        failed = 0
        for i in range(cycle_count):
            start = tick_times[i]
            end = tick_times[i + 1]
            drift_in_cycle = drift_prefix[end] - drift_prefix[start]
            if drift_in_cycle > 0:
                failed += 1
        tick_failure_rate = failed / cycle_count if cycle_count > 0 else float("nan")

    drift_rate_per_1k = float("nan")
    maintenance_spend_per_1k = float("nan")
    phi_change_rate_per_1k = float("nan")
    expected_step_rate_per_1k = float("nan")
    tick_rate_per_1k = float("nan")
    backward_rate_per_1k = float("nan")
    slip_rate_per_1k = float("nan")
    if steps > 0:
        drift_rate_per_1k = 1000.0 * run_dict["drift_unrepaired_post"] / steps
        maintenance_spend_per_1k = 1000.0 * run_dict["repairs_used"] / steps
        phi_change_rate_per_1k = 1000.0 * run_dict["phi_change_count"] / steps
        expected_step_rate_per_1k = 1000.0 * run_dict["expected_step_count"] / steps
        tick_rate_per_1k = 1000.0 * tick_count / steps
        backward_rate_per_1k = 1000.0 * run_dict["backward_step_count"] / steps
        slip_rate_per_1k = 1000.0 * run_dict["slip_step_count"] / steps

    retention_error = run_dict["drift_unrepaired_post"] / max(
        run_dict["drift_detected_pre"], 1
    )

    return {
        "tick_interval_variance": tick_interval_variance,
        "tick_failure_rate": tick_failure_rate,
        "drift_rate_per_1k": drift_rate_per_1k,
        "maintenance_spend_per_1k": maintenance_spend_per_1k,
        "phi_change_rate_per_1k": phi_change_rate_per_1k,
        "expected_step_rate_per_1k": expected_step_rate_per_1k,
        "tick_rate_per_1k": tick_rate_per_1k,
        "backward_rate_per_1k": backward_rate_per_1k,
        "slip_rate_per_1k": slip_rate_per_1k,
        "retention_error": retention_error,
    }


def idempotence_defect_snap(n_phi: int, samples: int, seed: int) -> float:
    if n_phi < 2 or samples <= 0:
        return 0.0

    rng = np.random.default_rng(seed)
    phi_prev = rng.integers(0, n_phi, size=samples)
    phi_prop = rng.integers(0, n_phi, size=samples)
    mask = phi_prop == phi_prev
    while np.any(mask):
        phi_prop[mask] = rng.integers(0, n_phi, size=int(mask.sum()))
        mask = phi_prop == phi_prev

    expected = (phi_prev + 1) % n_phi

    phi_repaired = np.where(phi_prop == expected, phi_prop, expected)
    phi_repaired_again = np.where(phi_repaired == expected, phi_repaired, expected)

    defect = np.mean(phi_repaired_again != phi_repaired)
    return float(defect)
