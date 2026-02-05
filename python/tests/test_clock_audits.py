from time_world.clock_audits import clock_metrics_from_run, simulate_with_maintenance
from time_world.model import build_model, preset_record_drive


def test_budget_reduces_tick_failure():
    params = preset_record_drive()
    params = dict(params)
    params["phase_noise"] = 0.12

    states, P = build_model(params)

    steps = 20_000
    burn_in = 2_000

    budget_low = 0
    budget_high = int(round(300 * steps / 1000.0))

    run_low = simulate_with_maintenance(
        states,
        P,
        steps,
        seed=0,
        budget_total=budget_low,
        burn_in=burn_in,
        start_idx=0,
    )
    run_high = simulate_with_maintenance(
        states,
        P,
        steps,
        seed=0,
        budget_total=budget_high,
        burn_in=burn_in,
        start_idx=0,
    )

    metrics_low = clock_metrics_from_run(run_low)
    metrics_high = clock_metrics_from_run(run_high)

    assert metrics_high["tick_failure_rate"] < metrics_low["tick_failure_rate"]
