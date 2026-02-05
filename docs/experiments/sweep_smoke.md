# Exhibit: Sweep smoke

Purpose: Run a small parameter sweep and aggregate EP/clock/holonomy metrics plus enablement outcomes.

Command:
- `python python/scripts/run_sweep_smoke.py`

Expected outputs:
- `artifacts/sweeps/sweep_smoke/results.csv`
- `artifacts/sweeps/sweep_smoke/enablement.csv`
- `artifacts/sweeps/sweep_smoke/summary.json`

What to look for:
- results.csv has 24 rows
- summary.json reports min/median/max for key metrics
