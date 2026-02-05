# Experiments Index

## Scripts

- [_smoke_artifact.py](../../python/scripts/_smoke_artifact.py)
- [exhibit_dpi_smoke.py](../../python/scripts/exhibit_dpi_smoke.py)
- [exhibit_clock_budget_smoke.py](../../python/scripts/exhibit_clock_budget_smoke.py)
- [exhibit_enablement_birth_smoke.py](../../python/scripts/exhibit_enablement_birth_smoke.py)
- [exhibit_constraints_cones_smoke.py](../../python/scripts/exhibit_constraints_cones_smoke.py)
- [exhibit_no_global_time_smoke.py](../../python/scripts/exhibit_no_global_time_smoke.py)
- [exhibit_no_signalling_toy_smoke.py](../../python/scripts/exhibit_no_signalling_toy_smoke.py)
- [run_sweep_smoke.py](../../python/scripts/run_sweep_smoke.py)

## Runbooks

- [exhibit_dpi.md](./exhibit_dpi.md)
- [exhibit_clock_budget.md](./exhibit_clock_budget.md)
- [exhibit_enablement_birth.md](./exhibit_enablement_birth.md)
- [exhibit_constraints_cones.md](./exhibit_constraints_cones.md)
- [exhibit_no_global_time.md](./exhibit_no_global_time.md)
- [exhibit_no_signalling_toy.md](./exhibit_no_signalling_toy.md)
- [sweep_smoke.md](./sweep_smoke.md)

## Expected artifacts

- `artifacts/_smoke/metadata.json`
- `artifacts/exhibit_dpi_smoke/metadata.json`
- `artifacts/exhibit_clock_budget_smoke/metadata.json`
- `artifacts/exhibit_enablement_birth_smoke/metadata.json`
- `artifacts/exhibit_constraints_cones_smoke/metadata.json`
- `artifacts/exhibit_no_global_time_smoke/metadata.json`
- `artifacts/exhibit_no_signalling_toy/metadata.json`
- `artifacts/sweeps/sweep_smoke/results.csv`
- `artifacts/sweeps/sweep_smoke/enablement.csv`
- `artifacts/sweeps/sweep_smoke/summary.json`

## How to run

- `make test`
- `python python/scripts/<script_name>.py`
- optional: `./scripts/package_repo_snapshot.sh`

## Run everything

- `python python/scripts/run_all_exhibits_smoke.py`
- outputs are written under `artifacts/...` (gitignored)

## Paper

- `docs/paper/to_notch_a_stone_with_six_birds.tex`
- `python python/scripts/run_all_exhibits_smoke.py`
- `python python/scripts/paper/make_paper_tables.py`
