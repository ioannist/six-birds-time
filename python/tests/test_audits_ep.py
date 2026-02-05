import numpy as np

from time_world.audits_ep import entropy_production_step, stationary_distribution
from time_world.model import build_model, preset_record_drive, preset_reversibleish


def test_stationary_distribution_and_ep():
    presets = {
        "reversibleish": preset_reversibleish(),
        "record_drive": preset_record_drive(),
    }

    results = {}
    for name, preset in presets.items():
        states, P = build_model(preset)
        pi = stationary_distribution(P)

        assert abs(pi.sum() - 1.0) < 1e-10
        assert pi.min() >= -1e-15
        assert np.linalg.norm(pi @ P - pi, 1) < 1e-8

        ep = entropy_production_step(P, pi)
        results[name] = ep

    ep_rev = results["reversibleish"]
    ep_rec = results["record_drive"]

    assert abs(ep_rev) < 1e-10
    assert np.isinf(ep_rec) or ep_rec > ep_rev + 1e-8
