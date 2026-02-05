import numpy as np

from time_world.model import build_model, preset_record_drive, preset_reversibleish, simulate


def _assert_stochastic(P: np.ndarray) -> None:
    assert P.min() >= -1e-15
    row_sums = P.sum(axis=1)
    assert np.all(np.abs(row_sums - 1.0) < 1e-12)


def test_presets_build_and_simulate():
    for preset in (preset_reversibleish(), preset_record_drive()):
        states, P = build_model(preset)
        assert P.shape == (len(states), len(states))
        _assert_stochastic(P)
        traj = simulate(P, steps=10_000, seed=123)
        assert traj.shape[0] == 10_001
