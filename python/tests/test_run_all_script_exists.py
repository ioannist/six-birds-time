from pathlib import Path
import py_compile


def test_run_all_script_exists_and_compiles():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "python/scripts/run_all_exhibits_smoke.py"
    assert script_path.exists()
    py_compile.compile(script_path, doraise=True)
