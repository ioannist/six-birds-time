# Exhibit: Enablement birth

Purpose: Demonstrate theory rewrite when coarse lens fails, plus a control regime with no birth.

Command:
- `python python/scripts/exhibit_enablement_birth_smoke.py`

Expected outputs:
- `artifacts/exhibit_enablement_birth_smoke/metadata.json`

What to look for:
- birth_step present for all seeds
- gap_post < gap_pre
- control regime has birth_step = None
