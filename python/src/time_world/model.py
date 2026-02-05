from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from time_world.utils import seed_everything


@dataclass(frozen=True)
class ModelParams:
    n_x: int
    n_phi: int
    n_r: int
    p_x: float
    p_phi: float
    drive_strength: float
    phase_noise: float
    record_coupling: float
    record_backslide_prob: float
    x_phi_coupling: float
    constraint_mask: object | None = None


def preset_reversibleish() -> dict:
    return {
        "n_x": 3,
        "n_phi": 8,
        "n_r": 1,
        "p_x": 0.2,
        "p_phi": 0.7,
        "drive_strength": 0.0,
        "phase_noise": 0.1,
        "record_coupling": 0.0,
        "record_backslide_prob": 0.0,
        "constraint_mask": None,
    }


def preset_record_drive() -> dict:
    return {
        "n_x": 3,
        "n_phi": 8,
        "n_r": 16,
        "p_x": 0.2,
        "p_phi": 0.7,
        "drive_strength": 0.6,
        "phase_noise": 0.05,
        "record_coupling": 0.5,
        "record_backslide_prob": 0.02,
        "constraint_mask": None,
    }


def _coerce_params(params: dict) -> ModelParams:
    return ModelParams(
        n_x=int(params["n_x"]),
        n_phi=int(params["n_phi"]),
        n_r=int(params["n_r"]),
        p_x=float(params["p_x"]),
        p_phi=float(params["p_phi"]),
        drive_strength=float(params["drive_strength"]),
        phase_noise=float(params["phase_noise"]),
        record_coupling=float(params["record_coupling"]),
        record_backslide_prob=float(params["record_backslide_prob"]),
        x_phi_coupling=float(params.get("x_phi_coupling", 0.0)),
        constraint_mask=params.get("constraint_mask"),
    )


def build_model(params: dict) -> tuple[list[tuple[int, int, int]], np.ndarray]:
    cfg = _coerce_params(params)

    if cfg.n_x < 1 or cfg.n_phi < 1 or cfg.n_r < 1:
        raise ValueError("n_x, n_phi, n_r must be >= 1")
    if cfg.p_x < 0 or cfg.p_phi < 0:
        raise ValueError("p_x and p_phi must be >= 0")
    p_idle = 1.0 - cfg.p_x - cfg.p_phi
    if p_idle < 0:
        raise ValueError("p_idle must be >= 0 (p_x + p_phi <= 1)")
    if not (-1.0 <= cfg.drive_strength <= 1.0):
        raise ValueError("drive_strength must be in [-1, 1]")
    if not (0.0 <= cfg.x_phi_coupling <= 1.0):
        raise ValueError("x_phi_coupling must be in [0, 1]")

    p_fwd = 0.5 * (1.0 + cfg.drive_strength)
    p_bwd = 0.5 * (1.0 - cfg.drive_strength)

    states: list[tuple[int, int, int]] = []
    index: dict[tuple[int, int, int], int] = {}
    for x in range(cfg.n_x):
        for phi in range(cfg.n_phi):
            for r in range(cfg.n_r):
                idx = len(states)
                state = (x, phi, r)
                states.append(state)
                index[state] = idx

    n_states = len(states)
    P = np.zeros((n_states, n_states), dtype=np.float64)

    def add_with_backslide(x: int, phi: int, r: int, prob: float, row: np.ndarray) -> None:
        if prob <= 0:
            return
        r_down = r - 1 if r > 0 else 0
        if r_down == r or cfg.record_backslide_prob <= 0:
            row[index[(x, phi, r)]] += prob
            return
        row[index[(x, phi, r)]] += prob * (1.0 - cfg.record_backslide_prob)
        row[index[(x, phi, r_down)]] += prob * cfg.record_backslide_prob

    for state in states:
        x, phi, r = state
        row = P[index[state]]

        # Idle branch
        add_with_backslide(x, phi, r, p_idle, row)

        # X-update branch
        if cfg.p_x > 0:
            uniform_mass = cfg.p_x * (1.0 - cfg.x_phi_coupling)
            base_prob = uniform_mass / cfg.n_x if uniform_mass > 0 else 0.0
            if base_prob > 0:
                for x_next in range(cfg.n_x):
                    add_with_backslide(x_next, phi, r, base_prob, row)

            if cfg.x_phi_coupling > 0:
                direction = 1 if phi < cfg.n_phi / 2 else -1
                x_next = (x + direction) % cfg.n_x
                add_with_backslide(
                    x_next, phi, r, cfg.p_x * cfg.x_phi_coupling, row
                )

        # Phi-update branch
        if cfg.p_phi > 0:
            # Phase noise branch
            if cfg.phase_noise > 0:
                noise_prob = cfg.p_phi * cfg.phase_noise / cfg.n_phi
                for phi_next in range(cfg.n_phi):
                    add_with_backslide(x, phi_next, r, noise_prob, row)

            # Non-noise branch with drive
            non_noise_prob = cfg.p_phi * (1.0 - cfg.phase_noise)
            if non_noise_prob > 0:
                phi_fwd = (phi + 1) % cfg.n_phi
                phi_bwd = (phi - 1) % cfg.n_phi

                fwd_prob = non_noise_prob * p_fwd
                if fwd_prob > 0:
                    r_inc = r + 1 if r + 1 < cfg.n_r else cfg.n_r - 1
                    if cfg.record_coupling > 0 and r_inc != r:
                        add_with_backslide(
                            x,
                            phi_fwd,
                            r_inc,
                            fwd_prob * cfg.record_coupling,
                            row,
                        )
                        add_with_backslide(
                            x,
                            phi_fwd,
                            r,
                            fwd_prob * (1.0 - cfg.record_coupling),
                            row,
                        )
                    else:
                        add_with_backslide(x, phi_fwd, r, fwd_prob, row)

                bwd_prob = non_noise_prob * p_bwd
                if bwd_prob > 0:
                    add_with_backslide(x, phi_bwd, r, bwd_prob, row)

    _apply_constraints(P, states, cfg.constraint_mask)

    return states, P


def _apply_constraints(
    P: np.ndarray,
    states: list[tuple[int, int, int]],
    constraint_mask: object | None,
) -> None:
    if constraint_mask is None:
        return

    if isinstance(constraint_mask, np.ndarray):
        if constraint_mask.shape != P.shape:
            raise ValueError("constraint_mask has incorrect shape")
        P *= constraint_mask.astype(np.float64, copy=False)
        _renormalize_rows(P)
        return

    if callable(constraint_mask):
        n_states = len(states)
        for i, from_state in enumerate(states):
            weights = np.ones(n_states, dtype=np.float64)
            for j, to_state in enumerate(states):
                raw = constraint_mask(from_state, to_state)
                if isinstance(raw, bool):
                    weights[j] = 1.0 if raw else 0.0
                else:
                    weights[j] = float(raw)
            P[i] *= weights
        _renormalize_rows(P)
        return

    raise ValueError("constraint_mask must be None, numpy array, or callable")


def _renormalize_rows(P: np.ndarray) -> None:
    row_sums = P.sum(axis=1)
    for i, total in enumerate(row_sums):
        if total <= 0:
            raise ValueError("Row has zero mass after applying constraints")
        P[i] /= total


def simulate(P: np.ndarray, steps: int, seed: int, start_idx: int = 0) -> np.ndarray:
    if steps < 0:
        raise ValueError("steps must be >= 0")
    seed_everything(seed)

    n_states = P.shape[0]
    if start_idx < 0 or start_idx >= n_states:
        raise ValueError("start_idx out of range")

    traj = np.empty(steps + 1, dtype=int)
    traj[0] = start_idx
    for t in range(steps):
        current = traj[t]
        traj[t + 1] = np.random.choice(n_states, p=P[current])
    return traj
