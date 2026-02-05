from __future__ import annotations

from typing import Callable

import numpy as np

from time_world.model import simulate


def lens_f0(state: tuple[int, int, int]) -> tuple[int]:
    x, _phi, _r = state
    return (x,)


def lens_f1(state: tuple[int, int, int]) -> tuple[int, int]:
    x, phi, _r = state
    return (x, phi)


def map_traj(
    states: list[tuple[int, int, int]],
    traj_idx: np.ndarray,
    lens_fn: Callable[[tuple[int, int, int]], tuple[int, ...]],
) -> list[tuple[int, ...]]:
    return [lens_fn(states[int(idx)]) for idx in traj_idx]


def markov_nll_gap(
    y_seq: list[tuple[int, ...]],
    *,
    alpha: float = 1.0,
    train_frac: float = 0.5,
) -> dict:
    if not 0.0 < train_frac < 1.0:
        raise ValueError("train_frac must be in (0, 1)")
    if alpha <= 0:
        raise ValueError("alpha must be > 0")

    n = len(y_seq)
    if n < 4:
        raise ValueError("y_seq must have length >= 4")

    vocab: list[tuple[int, ...]] = []
    index: dict[tuple[int, ...], int] = {}
    for y in y_seq:
        if y not in index:
            index[y] = len(vocab)
            vocab.append(y)

    k = len(vocab)
    y_idx = np.array([index[y] for y in y_seq], dtype=int)

    n_pairs = n - 1
    n_triples = n - 2

    train_pairs = int(n_pairs * train_frac)
    train_pairs = min(max(train_pairs, 1), n_pairs - 1)

    train_triples = int(n_triples * train_frac)
    train_triples = min(max(train_triples, 1), n_triples - 1)

    counts1 = np.zeros((k, k), dtype=int)
    counts1_out = np.zeros(k, dtype=int)

    for t in range(train_pairs):
        curr = y_idx[t]
        nxt = y_idx[t + 1]
        counts1[curr, nxt] += 1
        counts1_out[curr] += 1

    counts2: dict[tuple[int, int, int], int] = {}
    counts2_ctx: dict[tuple[int, int], int] = {}

    for t in range(train_triples):
        prev = y_idx[t]
        curr = y_idx[t + 1]
        nxt = y_idx[t + 2]
        key = (prev, curr, nxt)
        counts2[key] = counts2.get(key, 0) + 1
        ctx = (prev, curr)
        counts2_ctx[ctx] = counts2_ctx.get(ctx, 0) + 1

    nll1 = 0.0
    for t in range(train_pairs, n_pairs):
        curr = y_idx[t]
        nxt = y_idx[t + 1]
        numer = counts1[curr, nxt] + alpha
        denom = counts1_out[curr] + alpha * k
        nll1 += -np.log(numer / denom)

    n_eval_pairs = n_pairs - train_pairs
    nll1 = nll1 / n_eval_pairs if n_eval_pairs > 0 else float("nan")

    nll2 = 0.0
    for t in range(train_triples, n_triples):
        prev = y_idx[t]
        curr = y_idx[t + 1]
        nxt = y_idx[t + 2]
        key = (prev, curr, nxt)
        ctx = (prev, curr)
        numer = counts2.get(key, 0) + alpha
        denom = counts2_ctx.get(ctx, 0) + alpha * k
        nll2 += -np.log(numer / denom)

    n_eval_triples = n_triples - train_triples
    nll2 = nll2 / n_eval_triples if n_eval_triples > 0 else float("nan")

    gap_raw = nll1 - nll2
    gap = max(gap_raw, 0.0)

    return {
        "nll1": float(nll1),
        "nll2": float(nll2),
        "gap_raw": float(gap_raw),
        "gap": float(gap),
        "n_train": int(train_pairs),
        "n_eval": int(n_eval_pairs),
        "k": int(k),
    }


def run_enablement(
    states: list[tuple[int, int, int]],
    P: np.ndarray,
    *,
    seed: int,
    steps: int,
    burn_in: int,
    window: int,
    threshold: float,
    alpha: float = 1.0,
) -> dict:
    traj = simulate(P, steps + burn_in, seed)
    traj = traj[burn_in:]

    total_steps = len(traj) - 1
    if window <= 0 or window > total_steps:
        raise ValueError("window must be in (0, total_steps]")

    n_windows = total_steps // window

    lens_fn = lens_f0
    birth_step = None
    gap_pre = None
    gap_raw_pre = None
    gap_post = None
    gap_raw_post = None
    nll1_pre = None
    nll2_pre = None
    nll1_post = None
    nll2_post = None
    gap_f0_max = None
    gap_raw_f0_max = None
    windows_checked_f0 = 0

    for w in range(n_windows):
        start = w * window
        end = start + window
        y_seq = map_traj(states, traj[start : end + 1], lens_fn)
        stats = markov_nll_gap(y_seq, alpha=alpha, train_frac=0.5)

        if lens_fn is lens_f0:
            windows_checked_f0 += 1
            gap_f0_max = stats["gap"] if gap_f0_max is None else max(gap_f0_max, stats["gap"])
            gap_raw_f0_max = (
                stats["gap_raw"]
                if gap_raw_f0_max is None
                else max(gap_raw_f0_max, stats["gap_raw"])
            )

        if lens_fn is lens_f0 and stats["gap"] > threshold:
            birth_step = end
            gap_pre = stats["gap"]
            gap_raw_pre = stats["gap_raw"]
            nll1_pre = stats["nll1"]
            nll2_pre = stats["nll2"]
            lens_fn = lens_f1
            continue

        if lens_fn is lens_f1 and birth_step is not None and gap_post is None:
            gap_post = stats["gap"]
            gap_raw_post = stats["gap_raw"]
            nll1_post = stats["nll1"]
            nll2_post = stats["nll2"]
            break

    if gap_f0_max is None:
        gap_f0_max = 0.0
    if gap_raw_f0_max is None:
        gap_raw_f0_max = 0.0

    return {
        "birth_step": birth_step,
        "gap_f0_max": gap_f0_max,
        "gap_raw_f0_max": gap_raw_f0_max,
        "windows_checked_f0": windows_checked_f0,
        "gap_pre": gap_pre,
        "gap_raw_pre": gap_raw_pre,
        "gap_post": gap_post,
        "gap_raw_post": gap_raw_post,
        "nll1_pre": nll1_pre,
        "nll2_pre": nll2_pre,
        "nll1_post": nll1_post,
        "nll2_post": nll2_post,
        "steps": steps,
        "burn_in": burn_in,
        "window": window,
        "threshold": threshold,
        "alpha": alpha,
        "seed": seed,
    }
