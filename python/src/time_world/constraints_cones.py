from __future__ import annotations

from typing import Callable

import numpy as np


def constraint_r_constant() -> Callable[[tuple[int, int, int], tuple[int, int, int]], bool]:
    def _mask(
        from_state: tuple[int, int, int], to_state: tuple[int, int, int]
    ) -> bool:
        return to_state[2] == from_state[2]

    return _mask


def constraint_phi_forbid_pm1(
    n_phi: int,
) -> Callable[[tuple[int, int, int], tuple[int, int, int]], bool]:
    def _mask(
        from_state: tuple[int, int, int], to_state: tuple[int, int, int]
    ) -> bool:
        phi_from = from_state[1]
        phi_to = to_state[1]
        if phi_to == (phi_from + 1) % n_phi:
            return False
        if phi_to == (phi_from - 1) % n_phi:
            return False
        return True

    return _mask


def constraint_phi_step_only(
    n_phi: int,
) -> Callable[[tuple[int, int, int], tuple[int, int, int]], bool]:
    def _mask(
        from_state: tuple[int, int, int], to_state: tuple[int, int, int]
    ) -> bool:
        phi_from = from_state[1]
        phi_to = to_state[1]
        allowed = {
            phi_from,
            (phi_from + 1) % n_phi,
            (phi_from - 1) % n_phi,
        }
        return phi_to in allowed

    return _mask


def constraint_phi_forbid_value(
    forbidden_phi: int,
) -> Callable[[tuple[int, int, int], tuple[int, int, int]], bool]:
    def _mask(
        _from_state: tuple[int, int, int], to_state: tuple[int, int, int]
    ) -> bool:
        return to_state[1] != forbidden_phi

    return _mask


def constraint_phi_forbid_zero() -> Callable[[tuple[int, int, int], tuple[int, int, int]], bool]:
    return constraint_phi_forbid_value(0)


def constraint_local_x(
    n_x: int, radius: int = 1, *, periodic: bool = True
) -> Callable[[tuple[int, int, int], tuple[int, int, int]], bool]:
    if radius < 0:
        raise ValueError("radius must be >= 0")

    def _dist(a: int, b: int) -> int:
        if not periodic:
            return abs(a - b)
        delta = abs(a - b) % n_x
        return min(delta, n_x - delta)

    def _mask(
        from_state: tuple[int, int, int], to_state: tuple[int, int, int]
    ) -> bool:
        return _dist(from_state[0], to_state[0]) <= radius

    return _mask


def adjacency_from_P(P: np.ndarray, *, tol: float = 0.0) -> list[np.ndarray]:
    P = np.asarray(P)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix")
    if tol < 0:
        raise ValueError("tol must be >= 0")

    adj: list[np.ndarray] = []
    for i in range(P.shape[0]):
        neighbors = np.flatnonzero(P[i] > tol)
        adj.append(neighbors.astype(int, copy=False))
    return adj


def reachable_sizes(
    adj: list[np.ndarray], start_idx: int, t_max: int
) -> list[int]:
    if t_max < 0:
        raise ValueError("t_max must be >= 0")
    if start_idx < 0 or start_idx >= len(adj):
        raise ValueError("start_idx out of range")

    reached = {start_idx}
    sizes = [1]
    frontier = {start_idx}

    for _ in range(t_max):
        next_frontier: set[int] = set()
        for node in frontier:
            for nxt in adj[node]:
                if int(nxt) not in reached:
                    reached.add(int(nxt))
                    next_frontier.add(int(nxt))
        frontier = next_frontier
        sizes.append(len(reached))
        if not frontier:
            sizes.extend([len(reached)] * (t_max - len(sizes) + 1))
            break

    return sizes
