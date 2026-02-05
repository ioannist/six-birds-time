import json

from time_world.utils import write_json


def test_write_json_round_trip(tmp_path):
    payload = {"alpha": 1, "beta": "two"}
    out_path = write_json(tmp_path / "out.json", payload)

    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["beta"] == "two"
