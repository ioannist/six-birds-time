from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterable

import numpy as np


def apply_lens(
    states: list[tuple[int, int, int]],
    lens_fn: Callable[[tuple[int, int, int]], object],
) -> tuple[list[object], np.ndarray]:
    y_states: list[object] = []
    index: dict[object, int] = {}
    map_z_to_y = np.empty(len(states), dtype=int)

    for i, state in enumerate(states):
        key = lens_fn(state)
        if key not in index:
            index[key] = len(y_states)
            y_states.append(key)
        map_z_to_y[i] = index[key]

    return y_states, map_z_to_y


def project_traj(traj_z: np.ndarray, map_z_to_y: np.ndarray) -> np.ndarray:
    return map_z_to_y[np.asarray(traj_z, dtype=int)]


def reverse_path_tuple(w: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(reversed(w))


def count_paths(traj: np.ndarray, T: int) -> tuple[dict[tuple[int, ...], int], int]:
    if T < 1:
        raise ValueError("T must be >= 1")
    traj = np.asarray(traj, dtype=int)
    if traj.ndim != 1:
        raise ValueError("traj must be a 1D array")
    total = int(traj.shape[0] - T)
    if total <= 0:
        raise ValueError("traj must have length > T")

    counts: dict[tuple[int, ...], int] = defaultdict(int)
    for i in range(total):
        window = tuple(traj[i : i + T + 1].tolist())
        counts[window] += 1
    return dict(counts), total


def estimate_sigma_T_micro(
    counts: dict[tuple[int, ...], int],
    total: int,
    *,
    alpha: float,
) -> float:
    support = _support_with_reverse(counts)
    k = len(support)
    alpha_per = alpha / k if k > 0 else 0.0
    denom = total + alpha
    if denom <= 0:
        raise ValueError("total + alpha must be positive")

    sigma = 0.0
    for w in support:
        c_w = counts.get(w, 0)
        c_rev = counts.get(reverse_path_tuple(w), 0)
        p_w = (c_w + alpha_per) / denom
        q_w = (c_rev + alpha_per) / denom
        if p_w == 0:
            continue
        sigma += p_w * np.log(p_w / q_w)
    return float(sigma)


def estimate_sigma_T_macro_from_micro(
    counts: dict[tuple[int, ...], int],
    total: int,
    map_z_to_y: np.ndarray,
    *,
    alpha: float,
) -> float:
    support = _support_with_reverse(counts)
    k = len(support)
    alpha_per = alpha / k if k > 0 else 0.0
    denom = total + alpha
    if denom <= 0:
        raise ValueError("total + alpha must be positive")

    p_y: dict[tuple[int, ...], float] = defaultdict(float)
    q_y: dict[tuple[int, ...], float] = defaultdict(float)

    for w in support:
        c_w = counts.get(w, 0)
        c_rev = counts.get(reverse_path_tuple(w), 0)
        p_w = (c_w + alpha_per) / denom
        q_w = (c_rev + alpha_per) / denom

        y_path = tuple(map_z_to_y[list(w)].tolist())
        p_y[y_path] += p_w
        q_y[y_path] += q_w

    sigma = 0.0
    for y_path, p_val in p_y.items():
        q_val = q_y.get(y_path, 0.0)
        if p_val == 0:
            continue
        if q_val == 0:
            return float("inf")
        sigma += p_val * np.log(p_val / q_val)
    return float(sigma)


def estimate_sigma_Ts_for_lenses(
    traj_z: np.ndarray,
    Ts: Iterable[int],
    lens_maps: dict[str, np.ndarray],
    *,
    alpha: float,
) -> dict[int, dict[str, object]]:
    results: dict[int, dict[str, object]] = {}
    for T in Ts:
        counts, total = count_paths(traj_z, T)
        micro_sigma = estimate_sigma_T_micro(counts, total, alpha=alpha)
        lens_sigmas = {
            name: estimate_sigma_T_macro_from_micro(
                counts, total, mapping, alpha=alpha
            )
            for name, mapping in lens_maps.items()
        }
        results[int(T)] = {"micro": micro_sigma, "lenses": lens_sigmas}
    return results


def lens_drop_r(state: tuple[int, int, int]) -> tuple[int, int]:
    x, phi, _r = state
    return (x, phi)


def lens_drop_phi(state: tuple[int, int, int]) -> tuple[int, int]:
    x, _phi, r = state
    return (x, r)


def lens_identity(state: tuple[int, int, int]) -> tuple[int, int, int]:
    return state


def _support_with_reverse(
    counts: dict[tuple[int, ...], int]
) -> list[tuple[int, ...]]:
    support: set[tuple[int, ...]] = set()
    for w in counts:
        support.add(w)
        support.add(reverse_path_tuple(w))
    return list(support)
