from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from time_world.utils import artifact_dir, seed_everything, write_json


def main() -> None:
    run_name = "_smoke"
    seed = 123
    seed_everything(seed)

    out_dir = artifact_dir(run_name)
    timestamp_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "run_name": run_name,
        "seed": seed,
        "params": {
            "note": "smoke",
        },
        "metrics": {
            "ok": True,
        },
        "timestamp_utc": timestamp_utc,
    }
    out_path = write_json(out_dir / "metadata.json", payload)
    rel_path = f"artifacts/{run_name}/metadata.json"
    print(str(out_path.resolve()))
    print(rel_path)


if __name__ == "__main__":
    main()
