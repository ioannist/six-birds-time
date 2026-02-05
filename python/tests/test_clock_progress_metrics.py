from time_world.clock_audits import clock_metrics_from_run, simulate_with_maintenance
from time_world.model import build_model, preset_record_drive


def _stall_constraint(from_state, to_state):
    return to_state[1] == from_state[1]


def test_clock_progress_metrics_stall_vs_normal():
    params = preset_record_drive()
    params = dict(params)
    params["n_r"] = 1
    params["phase_noise"] = 0.05
    params["record_coupling"] = 0.0
    params["constraint_mask"] = None

    steps = 20_000
    burn_in = 2_000

    states, P = build_model(params)
    run_normal = simulate_with_maintenance(
        states,
        P,
        steps,
        seed=0,
        budget_total=0,
        burn_in=burn_in,
        start_idx=0,
    )
    metrics_normal = clock_metrics_from_run(run_normal)

    assert metrics_normal["expected_step_rate_per_1k"] > 10
    assert metrics_normal["phi_change_rate_per_1k"] >= metrics_normal[
        "expected_step_rate_per_1k"
    ]
    assert metrics_normal["tick_rate_per_1k"] > 0

    params_stall = dict(params)
    params_stall["constraint_mask"] = _stall_constraint
    states_s, P_s = build_model(params_stall)
    run_stall = simulate_with_maintenance(
        states_s,
        P_s,
        steps,
        seed=0,
        budget_total=0,
        burn_in=burn_in,
        start_idx=0,
    )
    metrics_stall = clock_metrics_from_run(run_stall)

    assert metrics_stall["phi_change_rate_per_1k"] < 1e-9
    assert metrics_stall["expected_step_rate_per_1k"] < 1e-9
