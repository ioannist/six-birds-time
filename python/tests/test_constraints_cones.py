import numpy as np

from time_world.audits_ep import entropy_production_step, stationary_distribution
from time_world.clock_audits import clock_metrics_from_run, simulate_with_maintenance
from time_world.constraints_cones import (
    adjacency_from_P,
    constraint_phi_forbid_zero,
    constraint_r_constant,
    reachable_sizes,
)
from time_world.model import build_model


def test_constraints_cones_small():
    params = {
        "n_x": 2,
        "n_phi": 4,
        "n_r": 4,
        "p_x": 0.2,
        "p_phi": 0.7,
        "drive_strength": 0.6,
        "phase_noise": 0.05,
        "record_coupling": 0.5,
        "record_backslide_prob": 0.02,
        "constraint_mask": None,
    }

    states_u, P_u = build_model(params)
    params_r = dict(params)
    params_r["constraint_mask"] = constraint_r_constant()
    states_r, P_r = build_model(params_r)

    pi_u = stationary_distribution(P_u, tol=1e-12)
    pi_r = stationary_distribution(P_r, tol=1e-12)

    ep_u = entropy_production_step(P_u, pi_u, zero_mode="inf")
    ep_r = entropy_production_step(P_r, pi_r, zero_mode="inf")

    assert np.isinf(ep_u)
    assert np.isfinite(ep_r)

    adj_u = adjacency_from_P(P_u)
    adj_r = adjacency_from_P(P_r)
    sizes_u = reachable_sizes(adj_u, start_idx=0, t_max=5)
    sizes_r = reachable_sizes(adj_r, start_idx=0, t_max=5)

    assert sizes_r[-1] <= params["n_x"] * params["n_phi"]
    assert sizes_u[-1] > sizes_r[-1]

    params_phi0 = dict(params)
    params_phi0["constraint_mask"] = constraint_phi_forbid_zero()
    states_0, P_0 = build_model(params_phi0)
    run = simulate_with_maintenance(
        states_0,
        P_0,
        steps=5_000,
        seed=0,
        budget_total=0,
        burn_in=500,
        start_idx=0,
    )
    metrics = clock_metrics_from_run(run)
    assert metrics["tick_rate_per_1k"] < 1e-9
