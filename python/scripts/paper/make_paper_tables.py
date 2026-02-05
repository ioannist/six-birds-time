from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


ARTIFACTS = {
    "dpi": "artifacts/exhibit_dpi_smoke/metadata.json",
    "clock_budget": "artifacts/exhibit_clock_budget_smoke/metadata.json",
    "enablement": "artifacts/exhibit_enablement_birth_smoke/metadata.json",
    "holonomy": "artifacts/exhibit_no_global_time_smoke/metadata.json",
    "no_signalling": "artifacts/exhibit_no_signalling_toy/metadata.json",
    "constraints": "artifacts/exhibit_constraints_cones_smoke/metadata.json",
    "sweep_summary": "artifacts/sweeps/sweep_smoke/summary.json",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _fmt_value(value: float | None, stderr: float | None = None) -> str:
    if value is None:
        return "--"
    if stderr is None:
        return f"{value:.6g}"
    return f"{value:.6g}$\\pm${stderr:.2g}"


def _fmt_value_sig(value: float | None, sig: int = 4) -> str:
    if value is None:
        return "--"
    return f"{value:.{sig}g}"


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_table(
    path: Path,
    caption: str,
    label: str,
    header: list[str],
    rows: list[list[str]],
    font_size: str | None = None,
) -> None:
    lines = [
        "% Auto-generated; do not edit.",
        "\\begin{table}[t]",
        "\\centering",
    ]
    if font_size:
        lines.append(font_size)
    lines.extend([
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\begin{tabular}{%s}" % ("l" * len(header)),
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ])
    for row in rows:
        escaped = [_tex_escape(cell) for cell in row]
        lines.append(" & ".join(escaped) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _tex_escape(text: str) -> str:
    return (
        text.replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
    )


def _missing_table(path: Path, caption: str, label: str, artifact: str, reason: str) -> None:
    header = ["Artifact", "Status"]
    rows = [[artifact, reason]]
    _write_table(path, caption, label, header, rows)


def _manifest_table(repo_root: Path, out_dir: Path) -> tuple[Path, dict[str, str]]:
    status = {}
    rows = []
    for key, rel in ARTIFACTS.items():
        found = (repo_root / rel).exists()
        status[key] = "found" if found else "missing"
        label = rel if found else f"{rel} (missing)"
        rows.append([label])

    out_path = out_dir / "table_manifest.tex"
    lines = [
        "% Auto-generated; do not edit.",
        f"% Generated at {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Artifact manifest (auto-generated).}",
        "\\label{tab:artifact-manifest}",
        "\\begin{tabular}{l}",
        "\\toprule",
        "Artifact \\\\",
        "\\midrule",
    ]
    for (rel,) in rows:
        rel_esc = _tex_escape(rel)
        lines.append(f"{rel_esc} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path, status


def _table_dpi(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    artifact = ARTIFACTS["dpi"]
    out_path = out_dir / "table_dpi.tex"
    data = _load_json(repo_root / artifact)
    if not data:
        _missing_table(out_path, "Path-reversal KL (DPI-safe): micro vs coarse lenses.", "tab:dpi", artifact, "missing/parse error")
        return out_path, "missing"

    results = data.get("results", [])
    record_drive = None
    for entry in results:
        if entry.get("name") == "record_drive":
            record_drive = entry
            break
    if record_drive is None and results:
        record_drive = results[0]

    if not record_drive:
        _missing_table(out_path, "Path-reversal KL (DPI-safe): micro vs coarse lenses.", "tab:dpi", artifact, "missing/parse error")
        return out_path, "missing"

    rows = []
    for T in (1, 3, 5):
        row = record_drive.get("results", {}).get(str(T)) or record_drive.get("results", {}).get(T)
        if not row:
            rows.append([str(T), "--", "--", "--"])
            continue
        micro = row.get("micro", {})
        drop_r = row.get("drop_r", {})
        drop_phi = row.get("drop_phi", {})
        rows.append([
            str(T),
            _fmt_value(micro.get("mean"), micro.get("stderr")),
            _fmt_value(drop_r.get("mean"), drop_r.get("stderr")),
            _fmt_value(drop_phi.get("mean"), drop_phi.get("stderr")),
        ])

    _write_table(
        out_path,
        "Path-reversal KL (DPI-safe): micro vs coarse lenses.",
        "tab:dpi",
        ["T", "micro", "drop\_r", "drop\_phi"],
        rows,
    )
    return out_path, "found"


def _table_clock_budget(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    artifact = ARTIFACTS["clock_budget"]
    out_path = out_dir / "table_clock_budget.tex"
    data = _load_json(repo_root / artifact)
    if not data:
        _missing_table(out_path, "Clock viability vs maintenance budget.", "tab:clock-budget", artifact, "missing/parse error")
        return out_path, "missing"

    results = data.get("results", {})
    rows = []
    for budget in ("0", "50", "200"):
        entry = results.get(budget, {})
        rows.append([
            budget,
            _fmt_value(entry.get("tick_failure_rate", {}).get("mean")),
            _fmt_value(entry.get("tick_rate_per_1k", {}).get("mean")),
            _fmt_value(entry.get("expected_step_rate_per_1k", {}).get("mean")),
            _fmt_value(entry.get("maintenance_spend_per_1k", {}).get("mean")),
        ])

    _write_table(
        out_path,
        "Clock viability vs maintenance budget.",
        "tab:clock-budget",
        ["budget (repairs/1k)", "tick\_failure", "tick\_rate/1k", "expected\_step/1k", "maintenance\_spend/1k"],
        rows,
    )
    return out_path, "found"


def _table_enablement(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    artifact = ARTIFACTS["enablement"]
    out_path = out_dir / "table_enablement.tex"
    data = _load_json(repo_root / artifact)
    if not data:
        _missing_table(out_path, "Enablement as theory rewrite (birth) and a no-birth control.", "tab:enablement", artifact, "missing/parse error")
        return out_path, "missing"

    results = data.get("results", {})
    rows = []
    for regime in ("enablement", "control"):
        entry = results.get(regime, {})
        summary = entry.get("summary", {})
        per_seed = entry.get("per_seed", [])
        if summary.get("gap_f0_max") is None and per_seed:
            gap_vals = [r.get("gap_f0_max") for r in per_seed if r.get("gap_f0_max") is not None]
            if gap_vals:
                summary["gap_f0_max"] = {"mean": sum(gap_vals) / len(gap_vals)}
        birth = summary.get("birth_step", {}).get("mean")
        birth_str = "--" if birth is None else _fmt_value(birth)
        rows.append([
            regime,
            birth_str,
            _fmt_value(summary.get("gap_f0_max", {}).get("mean")) if summary.get("gap_f0_max") else "--",
            _fmt_value(summary.get("gap_pre", {}).get("mean")),
            _fmt_value(summary.get("gap_post", {}).get("mean")),
        ])

    _write_table(
        out_path,
        "Enablement as theory rewrite (birth) and a no-birth control.",
        "tab:enablement",
        ["regime", "birth\_step", "gap\_f0\_max", "gap\_pre", "gap\_post"],
        rows,
    )
    return out_path, "found"


def _table_holonomy(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    artifact = ARTIFACTS["holonomy"]
    out_path = out_dir / "table_holonomy.tex"
    data = _load_json(repo_root / artifact)
    if not data:
        _missing_table(out_path, "No global time via protocol holonomy.", "tab:holonomy", artifact, "missing/parse error")
        return out_path, "missing"

    results = data.get("results", {})
    rows = []
    for regime in ("nonzero", "control"):
        summary = results.get(regime, {}).get("summary", {})
        H = summary.get("H", {})
        rows.append([
            regime,
            _fmt_value(H.get("mean")),
            _fmt_value(H.get("stderr")),
        ])

    _write_table(
        out_path,
        "No global time via protocol holonomy.",
        "tab:holonomy",
        ["regime", "H\_mean", "H\_stderr"],
        rows,
    )
    return out_path, "found"


def _table_no_signalling(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    artifact = ARTIFACTS["no_signalling"]
    out_path = out_dir / "table_no_signalling.tex"
    data = _load_json(repo_root / artifact)
    if not data:
        _missing_table(out_path, "Constraint box vs signalling channel (no-signalling metric).", "tab:no-signalling", artifact, "missing/parse error")
        return out_path, "missing"

    results = data.get("results", {})
    rows = []
    for box in ("constraint_box", "signalling_box"):
        entry = results.get(box, {})
        tv = entry.get("max_tv_A_to_B")
        conds = entry.get("conditionals", {})
        if box == "constraint_box":
            ex_key = "a0_x1_y1"
        else:
            ex_key = "a0_x0_y0"
        ex_val = conds.get(ex_key)
        ex_str = "--" if ex_val is None else f"P(b|{ex_key})={ex_val}"
        rows.append([box, _fmt_value(tv), ex_str])

    _write_table(
        out_path,
        "Constraint box vs signalling channel (no-signalling metric).",
        "tab:no-signalling",
        ["box", "max TV($A\\rightarrow B$)", "example conditional"],
        rows,
    )
    return out_path, "found"


def _table_constraints_cones(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    artifact = ARTIFACTS["constraints"]
    out_path = out_dir / "table_constraints_cones.tex"
    data = _load_json(repo_root / artifact)
    if not data:
        _missing_table(
            out_path,
            "Constraints carve reachability cones and can destroy timekeeping.",
            "tab:constraints-cones",
            artifact,
            "missing/parse error",
        )
        return out_path, "missing"

    results = data.get("results", {})
    rows = []
    for regime in ("unconstrained", "r_constant", "phi_forbid_pm1", "phi_no_ticks"):
        entry = results.get(regime, {})
        cone_sizes = entry.get("cone_sizes", [])
        t1 = cone_sizes[1] if len(cone_sizes) > 1 else None
        t10 = cone_sizes[10] if len(cone_sizes) > 10 else None
        ep = entry.get("ep", {})
        clock = entry.get("clock", {})
        tick_failure = clock.get("tick_failure_rate_mean")
        if tick_failure is None or (isinstance(tick_failure, float) and tick_failure != tick_failure):
            tick_failure_str = "--"
        else:
            tick_failure_str = _fmt_value_sig(tick_failure)

        rows.append([
            regime,
            _fmt_value_sig(t1),
            _fmt_value_sig(t10),
            _fmt_value_sig(ep.get("ep_reg")),
            _fmt_value_sig(clock.get("tick_rate_per_1k_mean")),
            _fmt_value_sig(clock.get("expected_step_rate_per_1k_mean")),
            tick_failure_str,
            str(clock.get("tick_failure_rate_nan_count", 0)),
        ])

    _write_table(
        out_path,
        "Constraints carve reachability cones and can destroy timekeeping.",
        "tab:constraints-cones",
        [
            "regime",
            "\\shortstack{cone size\\\\(t=1)}",
            "\\shortstack{cone size\\\\(t=10)}",
            "ep\\_reg",
            "\\shortstack{tick rate\\\\(/1k)}",
            "\\shortstack{expected step\\\\(/1k)}",
            "\\shortstack{tick\\\\ failure}",
            "\\shortstack{tick failure\\\\ nan count}",
        ],
        rows,
        font_size="\\footnotesize",
    )
    return out_path, "found"

def main() -> None:
    repo_root = _repo_root()
    out_dir = repo_root / "docs/paper/tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path, status = _manifest_table(repo_root, out_dir)

    outputs = []
    outputs.append((manifest_path, status.get("constraints", "missing")))

    outputs.append(_table_dpi(repo_root, out_dir))
    outputs.append(_table_clock_budget(repo_root, out_dir))
    outputs.append(_table_enablement(repo_root, out_dir))
    outputs.append(_table_holonomy(repo_root, out_dir))
    outputs.append(_table_no_signalling(repo_root, out_dir))
    outputs.append(_table_constraints_cones(repo_root, out_dir))

    print("Artifacts:")
    for key, rel in ARTIFACTS.items():
        print(f"- {rel}: {status.get(key, 'missing')}")

    print("Tables:")
    for path, _ in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
