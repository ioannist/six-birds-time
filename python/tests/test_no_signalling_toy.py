import math

from time_world.no_signalling_toy import (
    conditional_B_given_A,
    constraint_box,
    marginal_B,
    no_signalling_violation_A_to_B,
    signalling_box,
)


def test_box_normalization_and_bounds():
    for box in (constraint_box(), signalling_box()):
        for x in (0, 1):
            for y in (0, 1):
                total = 0.0
                for a in (0, 1):
                    for b in (0, 1):
                        p = box[(x, y, a, b)]
                        assert p >= -1e-15
                        assert p <= 1.0 + 1e-15
                        total += p
                assert abs(total - 1.0) < 1e-12


def test_no_signalling_violation():
    v_constraint = no_signalling_violation_A_to_B(constraint_box())
    v_signal = no_signalling_violation_A_to_B(signalling_box())
    assert v_constraint < 1e-12
    assert v_signal > 0.9


def test_constraint_box_conditionals_sharp():
    P = constraint_box()
    c0 = conditional_B_given_A(P, a=0, x=1, y=1)
    c1 = conditional_B_given_A(P, a=1, x=1, y=1)
    assert max(c0.values()) > 0.999999
    assert max(c1.values()) > 0.999999


def test_constraint_box_marginal_uniform():
    P = constraint_box()
    for x in (0, 1):
        for y in (0, 1):
            m = marginal_B(P, x=x, y=y)
            assert math.isclose(m[0], 0.5, abs_tol=1e-12)
            assert math.isclose(m[1], 0.5, abs_tol=1e-12)
