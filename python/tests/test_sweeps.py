import numpy as np

from time_world.sweeps import run_case_metrics


def test_sweep_case_metrics_smoke():
    cases = [
        {
            "case_id": "d0.0_n0.02_rc0.0_cnone",
            "drive_strength": 0.0,
            "phase_noise": 0.02,
            "record_coupling": 0.0,
            "constraint_mode": "none",
        },
        {
            "case_id": "d0.6_n0.12_rc0.5_cr_constant",
            "drive_strength": 0.6,
            "phase_noise": 0.12,
            "record_coupling": 0.5,
            "constraint_mode": "r_constant",
        },
    ]

    for case in cases:
        result = run_case_metrics(
            case,
            seeds=[0],
            steps=5_000,
            burn_in=500,
            stride=10,
            alpha_kl=1.0,
        )
        assert "ep_reg" in result
        assert "tick_failure_rate_mean" in result
        assert "holonomy_H_mean" in result
        assert "expected_step_rate_per_1k_mean" in result
        assert "tick_rate_per_1k_mean" in result
        assert "phi_change_rate_per_1k_mean" in result

    result_r = run_case_metrics(
        cases[1],
        seeds=[0],
        steps=5_000,
        burn_in=500,
        stride=10,
        alpha_kl=1.0,
    )
    assert np.isfinite(result_r["ep_reg"])


def test_sweep_holonomy_control_fast():
    base = {
        "drive_strength": 0.6,
        "phase_noise": 0.12,
        "record_coupling": 0.5,
    }

    case_none = {
        "case_id": "d0.6_n0.12_rc0.5_cnone",
        **base,
        "constraint_mode": "none",
    }
    case_odd = {
        "case_id": "d0.6_n0.12_rc0.5_codd_phi_only",
        **base,
        "constraint_mode": "odd_phi_only",
    }

    result_none = run_case_metrics(
        case_none,
        seeds=[0],
        steps=8_000,
        burn_in=800,
        stride=10,
        alpha_kl=1.0,
    )
    result_odd = run_case_metrics(
        case_odd,
        seeds=[0],
        steps=8_000,
        burn_in=800,
        stride=10,
        alpha_kl=1.0,
    )

    assert abs(result_none["holonomy_H_mean"]) > 0.1
    assert abs(result_odd["holonomy_H_mean"]) < 0.05
