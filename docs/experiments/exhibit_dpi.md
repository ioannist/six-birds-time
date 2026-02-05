# Exhibit: DPI path-KL

Purpose: Estimate DPI-safe path-KL and compare coarse-graining lenses against micro dynamics.

Command:
- `python python/scripts/exhibit_dpi_smoke.py`

Expected outputs:
- `artifacts/exhibit_dpi_smoke/metadata.json`

What to look for:
- identity lens matches micro
- drop_r KL < micro KL
- drop_phi does not exceed micro KL
