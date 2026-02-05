# To Notch a Stone with Six Birds

This repository contains the **time instantiation** for the paper:

> **To Notch a Stone with Six Birds: Time as a Closure Artifact of Order, Measure, and Arrow**
>
> Archived at: https://zenodo.org/records/18495363
>
> DOI: https://doi.org/10.5281/zenodo.18495363

This paper instantiates the emergence calculus introduced in *Six Birds: Foundations of Emergence Calculus* as an auditable account of time: a layer has time when it stabilizes order, ticks, and an arrow, and it can fail when any of these components fail. The repository provides a finite-state “micro-laboratory” plus a reproducibility contract that ties figures/tables to generated artifacts.

## What this repository provides

The time instantiation implements:

- **Toy Markov world**: finite-state dynamics on $Z=X\times\Phi\times R$ with drive, noise, and ledger coupling
- **Arrow audits**: stationary EP and path-reversal KL (DPI-safe under coarse-graining)
- **Clock audits**: drift/failure metrics plus anti-stall progress rates under budgeted maintenance
- **Enablement audits**: closure-defect–triggered theory extension with no-birth controls
- **Constraint cones**: feasibility masks, reachability cones, and clock-collapse regimes
- **Protocol holonomy**: measured no-global-time obstruction with a commuting control
- **No-signalling toy**: constraint box vs signalling channel separation
- **Lean anchors**: lightweight mechanized lemmas for holonomy, no-signalling, and closure/ledger structure
- **Artifact contract**: paper tables are generated from snapshot-visible JSON/CSV artifacts

## Scope and limitations

The paper is explicit about what it does and does not claim:

- The micro-laboratory is an audit device, not a model of physical spacetime
- EP and path-KL are used as informational arrow proxies; no thermodynamic claims are made without extra assumptions
- Enablement is modeled as a controlled thresholded rewrite, not as a full theory of open-ended evolution
- The no-signalling toy is a minimal logical separator, not a model of quantum measurement

## Install

```bash
cd python
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Test

```bash
make test
```

## Run experiments

```bash
python python/scripts/run_all_exhibits_smoke.py
```

## Build paper

```bash
python python/scripts/paper/make_paper_tables.py
cd docs/paper && make pdf
```
