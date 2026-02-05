from __future__ import annotations

import numpy as np


def stationary_distribution(
    P: np.ndarray, *, tol: float = 1e-12, max_iter: int = 500_000
) -> np.ndarray:
    P = np.asarray(P, dtype=np.float64)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix")
    if P.shape[0] == 0:
        raise ValueError("P must be non-empty")

    n_states = P.shape[0]
    pi = np.full(n_states, 1.0 / n_states, dtype=np.float64)

    residual = float("inf")
    for _ in range(max_iter):
        pi_next = pi @ P
        pi_next = np.maximum(pi_next, 0.0)
        total = float(pi_next.sum())
        if total <= 0 or not np.isfinite(total):
            raise ValueError("stationary_distribution encountered nonpositive mass")
        pi_next /= total

        residual = float(np.linalg.norm(pi_next - pi, 1))
        if residual < tol:
            pi = pi_next
            break
        pi = pi_next
    else:
        raise ValueError(
            f"stationary_distribution did not converge within {max_iter} iterations "
            f"(residual={residual})"
        )

    pi = np.maximum(pi, 0.0)
    pi /= float(pi.sum())
    return pi


def entropy_production_step(
    P: np.ndarray,
    pi: np.ndarray,
    *,
    zero_mode: str = "inf",
    eps: float = 1e-15,
) -> float:
    P = np.asarray(P, dtype=np.float64)
    pi = np.asarray(pi, dtype=np.float64)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix")
    if pi.ndim != 1 or pi.shape[0] != P.shape[0]:
        raise ValueError("pi must be a vector matching P")
    if zero_mode not in {"inf", "raise", "regularize"}:
        raise ValueError("zero_mode must be 'inf', 'raise', or 'regularize'")

    mask = P > 0
    if zero_mode in {"inf", "raise"}:
        reverse_zero = mask & (P.T == 0)
        if np.any(reverse_zero):
            if zero_mode == "inf":
                return float("inf")
            raise ValueError(
                "absolute irreversibility detected: P_ij>0 and P_ji=0"
            )

        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.divide(P, P.T, out=np.ones_like(P), where=mask)
            log_ratio = np.log(ratio, out=np.zeros_like(P), where=mask)
        contrib = (pi[:, None] * P) * log_ratio
        return float(np.sum(contrib))

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (P + eps) / (P.T + eps)
        log_ratio = np.log(ratio)
    contrib = (pi[:, None] * P) * log_ratio
    return float(np.sum(contrib))
