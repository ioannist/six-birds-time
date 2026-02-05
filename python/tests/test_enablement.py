from time_world.enablement import run_enablement
from time_world.model import build_model


def test_enablement_birth_trigger():
    params = {
        "n_x": 4,
        "n_phi": 8,
        "n_r": 1,
        "p_x": 0.7,
        "p_phi": 0.25,
        "drive_strength": 0.6,
        "phase_noise": 0.02,
        "record_coupling": 0.0,
        "record_backslide_prob": 0.0,
        "x_phi_coupling": 1.0,
        "constraint_mask": None,
    }

    states, P = build_model(params)

    result = run_enablement(
        states,
        P,
        seed=0,
        steps=60_000,
        burn_in=2_000,
        window=10_000,
        threshold=0.05,
        alpha=1.0,
    )

    assert result["birth_step"] is not None
    assert result["gap_pre"] > 0.05
    assert result["gap_post"] < result["gap_pre"] * 0.5
    assert result["gap_f0_max"] >= result["gap_pre"]


def test_enablement_no_birth_control():
    params = {
        "n_x": 4,
        "n_phi": 8,
        "n_r": 1,
        "p_x": 0.7,
        "p_phi": 0.25,
        "drive_strength": 0.6,
        "phase_noise": 0.02,
        "record_coupling": 0.0,
        "record_backslide_prob": 0.0,
        "x_phi_coupling": 0.0,
        "constraint_mask": None,
    }

    states, P = build_model(params)

    result = run_enablement(
        states,
        P,
        seed=0,
        steps=60_000,
        burn_in=2_000,
        window=10_000,
        threshold=0.05,
        alpha=1.0,
    )

    assert result["birth_step"] is None
    assert result["gap_f0_max"] < 0.05
