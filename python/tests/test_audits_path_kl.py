import numpy as np

from time_world.audits_path_kl import (
    apply_lens,
    count_paths,
    estimate_sigma_T_macro_from_micro,
    estimate_sigma_T_micro,
    lens_drop_phi,
    lens_drop_r,
    lens_identity,
)
from time_world.model import build_model, preset_record_drive, simulate


def test_dpi_for_path_kl():
    preset = preset_record_drive()
    states, P = build_model(preset)

    _, map_drop_r = apply_lens(states, lens_drop_r)
    _, map_drop_phi = apply_lens(states, lens_drop_phi)
    _, map_identity = apply_lens(states, lens_identity)

    steps = 30_000
    burn_in = 2_000
    traj = simulate(P, steps + burn_in, seed=0)
    traj = traj[burn_in:]

    alpha = 1.0

    for T in (1, 3, 5):
        counts, total = count_paths(traj, T)
        sigma_micro = estimate_sigma_T_micro(counts, total, alpha=alpha)
        sigma_identity = estimate_sigma_T_macro_from_micro(
            counts, total, map_identity, alpha=alpha
        )
        sigma_drop_r = estimate_sigma_T_macro_from_micro(
            counts, total, map_drop_r, alpha=alpha
        )
        sigma_drop_phi = estimate_sigma_T_macro_from_micro(
            counts, total, map_drop_phi, alpha=alpha
        )

        assert abs(sigma_identity - sigma_micro) < 1e-10
        assert sigma_drop_r < sigma_micro - 1e-6
        assert sigma_drop_phi <= sigma_micro + 1e-12
