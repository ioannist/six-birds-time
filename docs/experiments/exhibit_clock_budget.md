# Exhibit: Clock budget

Purpose: Show maintenance budget improves clock stability under noise.

Command:
- `python python/scripts/exhibit_clock_budget_smoke.py`

Expected outputs:
- `artifacts/exhibit_clock_budget_smoke/metadata.json`

What to look for:
- higher budget lowers tick failure rate
- drift rate per 1k drops with budget
