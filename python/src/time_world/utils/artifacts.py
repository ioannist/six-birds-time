from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Iterable

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[4]


def seed_everything(seed: int) -> None:
    """Seed common RNGs for reproducibility."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


def write_json(path: str | Path, obj: dict) -> Path:
    """Write a JSON file with stable formatting and return its resolved path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return target.resolve()


def write_csv(path: str | Path, rows: Iterable[Iterable[object]]) -> Path:
    """Write rows to a CSV file and return its resolved path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(",".join(str(item) for item in row))
            handle.write("\n")
    return target.resolve()


def artifact_dir(run_name: str) -> Path:
    """Return an artifacts/<run_name> directory, creating it if missing."""
    target = _REPO_ROOT / "artifacts" / run_name
    target.mkdir(parents=True, exist_ok=True)
    return target
