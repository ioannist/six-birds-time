from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.no_signalling_toy import (
    conditional_B_given_A,
    constraint_box,
    marginal_B,
    mutual_information_XB,
    no_signalling_violation_A_to_B,
    signalling_box,
)
from time_world.utils import artifact_dir, write_json


def _box_payload(name: str, P: dict[tuple[int, int, int, int], float]) -> dict:
    marginals = {}
    for x in (0, 1):
        for y in (0, 1):
            marginals[f"{x},{y}"] = marginal_B(P, x=x, y=y)

    payload = {
        "marginals_B": marginals,
        "max_tv_A_to_B": no_signalling_violation_A_to_B(P),
        "mutual_information_XB_bits": mutual_information_XB(P),
    }

    if name == "constraint_box":
        payload["conditionals"] = {
            "a0_x1_y1": conditional_B_given_A(P, a=0, x=1, y=1),
            "a1_x1_y1": conditional_B_given_A(P, a=1, x=1, y=1),
        }
    else:
        payload["conditionals"] = {
            "a0_x0_y0": conditional_B_given_A(P, a=0, x=0, y=0),
            "a0_x1_y0": conditional_B_given_A(P, a=0, x=1, y=0),
        }

    return payload


def main() -> None:
    results = {
        "constraint_box": _box_payload("constraint_box", constraint_box()),
        "signalling_box": _box_payload("signalling_box", signalling_box()),
    }

    payload = {
        "run_name": "exhibit_no_signalling_toy",
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "results": results,
    }

    out_dir = artifact_dir("exhibit_no_signalling_toy")
    out_path = write_json(out_dir / "metadata.json", payload)

    rel_path = "artifacts/exhibit_no_signalling_toy/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
