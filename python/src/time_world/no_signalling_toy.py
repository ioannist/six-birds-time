from __future__ import annotations

from math import log2


def constraint_box() -> dict[tuple[int, int, int, int], float]:
    P: dict[tuple[int, int, int, int], float] = {}
    for x in (0, 1):
        for y in (0, 1):
            g = x & y
            for a in (0, 1):
                b = a ^ g
                for b_val in (0, 1):
                    P[(x, y, a, b_val)] = 0.5 if b_val == b else 0.0
    return P


def signalling_box() -> dict[tuple[int, int, int, int], float]:
    P: dict[tuple[int, int, int, int], float] = {}
    for x in (0, 1):
        for y in (0, 1):
            for a in (0, 1):
                for b in (0, 1):
                    P[(x, y, a, b)] = 0.5 if b == x else 0.0
    return P


def marginal_B(P: dict[tuple[int, int, int, int], float], x: int, y: int) -> dict[int, float]:
    return {
        0: sum(P[(x, y, a, 0)] for a in (0, 1)),
        1: sum(P[(x, y, a, 1)] for a in (0, 1)),
    }


def marginal_A(P: dict[tuple[int, int, int, int], float], x: int, y: int) -> dict[int, float]:
    return {
        0: sum(P[(x, y, 0, b)] for b in (0, 1)),
        1: sum(P[(x, y, 1, b)] for b in (0, 1)),
    }


def conditional_B_given_A(
    P: dict[tuple[int, int, int, int], float], a: int, x: int, y: int
) -> dict[int, float]:
    denom = sum(P[(x, y, a, b)] for b in (0, 1))
    if denom == 0:
        raise ValueError("Zero-probability conditioning event.")
    return {
        0: P[(x, y, a, 0)] / denom,
        1: P[(x, y, a, 1)] / denom,
    }


def tv_distance(p: dict[int, float], q: dict[int, float]) -> float:
    return 0.5 * (abs(p[0] - q[0]) + abs(p[1] - q[1]))


def no_signalling_violation_A_to_B(P: dict[tuple[int, int, int, int], float]) -> float:
    max_tv = 0.0
    for y in (0, 1):
        m0 = marginal_B(P, x=0, y=y)
        m1 = marginal_B(P, x=1, y=y)
        max_tv = max(max_tv, tv_distance(m0, m1))
    return max_tv


def no_signalling_violation_B_to_A(P: dict[tuple[int, int, int, int], float]) -> float:
    max_tv = 0.0
    for x in (0, 1):
        m0 = marginal_A(P, x=x, y=0)
        m1 = marginal_A(P, x=x, y=1)
        max_tv = max(max_tv, tv_distance(m0, m1))
    return max_tv


def mutual_information_XB(P: dict[tuple[int, int, int, int], float]) -> float:
    px = {0: 0.5, 1: 0.5}
    pxb = {0: {0: 0.0, 1: 0.0}, 1: {0: 0.0, 1: 0.0}}
    for x in (0, 1):
        for y in (0, 1):
            for a in (0, 1):
                for b in (0, 1):
                    pxb[x][b] += 0.25 * P[(x, y, a, b)]
    pb = {
        0: pxb[0][0] + pxb[1][0],
        1: pxb[0][1] + pxb[1][1],
    }

    info = 0.0
    for x in (0, 1):
        for b in (0, 1):
            p = pxb[x][b]
            if p <= 0:
                continue
            info += p * log2(p / (px[x] * pb[b]))
    return info
