import numpy as np

from time_world.holonomy import omega_from_samples, protocol_A_identity, protocol_B_even, protocol_C_odd
from time_world.model import build_model, preset_reversibleish, simulate


def _odd_phi_constraint(_from_state, to_state):
    return (to_state[1] % 2) == 1


def _run_regime(params, seeds, steps, burn_in, stride):
    states, P = build_model(params)
    proto_a = protocol_A_identity()
    proto_b = protocol_B_even(params["n_phi"])
    proto_c = protocol_C_odd(params["n_phi"])

    H_vals = []
    for seed in seeds:
        traj = simulate(P, steps + burn_in, seed)
        traj = traj[burn_in:]
        samples = [states[int(idx)] for idx in traj[::stride]]
        omega_ab = omega_from_samples(proto_a, proto_b, samples)["omega_mean"]
        omega_bc = omega_from_samples(proto_b, proto_c, samples)["omega_mean"]
        omega_ca = omega_from_samples(proto_c, proto_a, samples)["omega_mean"]
        H_vals.append(omega_ab + omega_bc + omega_ca)

    return float(np.mean(H_vals))


def test_holonomy_nonzero_vs_control():
    base = preset_reversibleish()
    base = dict(base)
    base["n_r"] = 1
    base["drive_strength"] = 0.6
    base["phase_noise"] = 0.05

    steps = 50_000
    burn_in = 5_000
    stride = 10
    seeds = [0, 1, 2]

    params_nonzero = dict(base)
    params_nonzero["constraint_mask"] = None

    params_control = dict(base)
    params_control["constraint_mask"] = _odd_phi_constraint

    H_nonzero = _run_regime(params_nonzero, seeds, steps, burn_in, stride)
    H_control = _run_regime(params_control, seeds, steps, burn_in, stride)

    assert abs(H_nonzero) > 0.1
    assert abs(H_control) < 1e-9
