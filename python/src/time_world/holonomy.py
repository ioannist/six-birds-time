from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class Protocol:
    name: str
    proj: Callable[[tuple[int, int, int]], tuple[int, ...]]
    lift: Callable[[tuple[int, ...]], tuple[int, int, int]]
    clock: Callable[[tuple[int, ...]], float]


def protocol_A_identity() -> Protocol:
    def proj(state: tuple[int, int, int]) -> tuple[int, int, int]:
        return state

    def lift(y: tuple[int, int, int]) -> tuple[int, int, int]:
        return y

    def clock(y: tuple[int, int, int]) -> float:
        return float(y[1])

    return Protocol(name="A_identity", proj=proj, lift=lift, clock=clock)


def protocol_B_even(n_phi: int) -> Protocol:
    if n_phi % 2 != 0:
        raise ValueError("n_phi must be even for protocol_B_even")

    def proj(state: tuple[int, int, int]) -> tuple[int, int, int]:
        x, phi, r = state
        return (x, phi // 2, r)

    def lift(y: tuple[int, int, int]) -> tuple[int, int, int]:
        x, b, r = y
        return (x, 2 * b, r)

    def clock(y: tuple[int, int, int]) -> float:
        _x, b, _r = y
        return float(2 * b)

    return Protocol(name="B_even", proj=proj, lift=lift, clock=clock)


def protocol_C_odd(n_phi: int) -> Protocol:
    if n_phi % 2 != 0:
        raise ValueError("n_phi must be even for protocol_C_odd")

    def proj(state: tuple[int, int, int]) -> tuple[int, int, int]:
        x, phi, r = state
        return (x, phi // 2, r)

    def lift(y: tuple[int, int, int]) -> tuple[int, int, int]:
        x, b, r = y
        return (x, 2 * b + 1, r)

    def clock(y: tuple[int, int, int]) -> float:
        _x, b, _r = y
        return float(2 * b + 1)

    return Protocol(name="C_odd", proj=proj, lift=lift, clock=clock)


def edge_delta(
    protocol_u: Protocol,
    protocol_v: Protocol,
    z_state: tuple[int, int, int],
) -> float:
    y_u = protocol_u.proj(z_state)
    z_lift = protocol_u.lift(y_u)
    y_v = protocol_v.proj(z_lift)
    return float(protocol_v.clock(y_v) - protocol_u.clock(y_u))


def omega_from_samples(
    protocol_u: Protocol,
    protocol_v: Protocol,
    samples: list[tuple[int, int, int]],
) -> dict:
    if not samples:
        raise ValueError("samples must be non-empty")
    deltas = np.array(
        [edge_delta(protocol_u, protocol_v, z) for z in samples], dtype=float
    )
    return {
        "omega_mean": float(np.mean(deltas)),
        "omega_std": float(np.std(deltas, ddof=1)) if deltas.size > 1 else 0.0,
        "n": int(deltas.size),
    }


def holonomy_cycle_from_samples(
    protocols_cycle: list[Protocol],
    samples: list[tuple[int, int, int]],
) -> dict:
    if len(protocols_cycle) < 2:
        raise ValueError("protocols_cycle must have length >= 2")
    if not samples:
        raise ValueError("samples must be non-empty")

    edges = []
    for i in range(len(protocols_cycle) - 1):
        u = protocols_cycle[i]
        v = protocols_cycle[i + 1]
        stats = omega_from_samples(u, v, samples)
        edges.append({"from": u.name, "to": v.name, **stats})

    H_mean = float(sum(edge["omega_mean"] for edge in edges))
    H_std_proxy = float(
        np.sqrt(sum(edge["omega_std"] ** 2 for edge in edges))
    )

    return {
        "edges": edges,
        "H_mean": H_mean,
        "H_std_proxy": H_std_proxy,
    }
