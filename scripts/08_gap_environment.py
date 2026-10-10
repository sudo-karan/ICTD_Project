"""Stage 4: the gate on the two Python environments. Writes into `50_gap/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_environment.py

Stage 4 runs in an environment of its own, outside the repository, which holds exactly what
`requirements-stage4.txt` pins (`README.md` section 0). The repository's main environment (`.venv/`) is the one the
earlier stages were built in and is not changed by stage 4: the bootstrap package needs `numba`, and `numba` needs an
older `numpy` than those stages' provenance records show. The project owner ruled this on 10 October 2026, after the
first hours of the run had moved `numpy` down in the main environment; it was put back that day.

This script is run with the stage-4 interpreter. It holds, and stops at the first that fails:

  1. the interpreter running it holds exactly what `requirements-stage4.txt` pins: no package more, none fewer, no
     version different (`pip` itself apart, as in `pip freeze`);
  2. that environment is outside the repository;
  3. the versions the owner named: `wildboottest` 0.3.2, `numba` 0.62.1, `numpy` 2.3.x;
  4. the main environment's `numpy` is the one version shown by the provenance records of the earlier stages that
     stage 4 lists among its inputs: eight records, in `20_degradation/`, `30_need/`, `40_allocation/` and
     `55_decision/` (those folders hold two more records with a `numpy` version, of builds stage 4 does not read; this
     script does not read them);
  5. the main environment's list of packages, in the order `pip freeze` prints it, is line for line the list kept
     before stage 4 installed anything (`50_gap/environment_before_stage4.txt`), where that list is on disk;
  6. in the main environment `verify_r620.py` passes, `verify_layer.py` passes 92 of 92 and `verify_decision.py` passes
     every check: nothing moved.

The main interpreter is `.venv/bin/python` of the repository, or the one named in the variable `ICTD_MAIN_PYTHON`.

Writes `gates_environment.csv` (`gate`, `expected`, `found`, `pass`), `environment_main_now.txt` (the main
environment's `pip freeze` as this script found it, in the order printed) and the section `08_gap_environment` of `gap.provenance.json`,
whose `environment` lists every package of the stage-4 environment with its version.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402

STEP = "08_gap_environment"
MAIN_PYTHON = Path(os.environ.get("ICTD_MAIN_PYTHON", G.ROOT / ".venv" / "bin" / "python"))
EARLIER_RECORDS = [G.rel(p) for k, p in G.IN.items() if k.startswith("provenance_")]   # the provenance records of the earlier stages, from the list of inputs
BEFORE = G.OUT / "environment_before_stage4.txt"
NAMED = {"wildboottest": r"0\.3\.2", "numba": r"0\.62\.1", "numpy": r"2\.3\.\d+"}


def main_run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(MAIN_PYTHON), *args], capture_output=True, text=True, cwd=G.ROOT)


def numpy_in(record: dict):
    """The `numpy` version a provenance record carries, wherever in it the key sits."""
    found = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "numpy" and isinstance(v, str):
                    found.append(v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(record)
    return found


def main() -> None:
    env = G.require_stage4_environment()
    if not MAIN_PYTHON.exists():
        G.stop(f"the main environment's interpreter is not at {MAIN_PYTHON}: set ICTD_MAIN_PYTHON")
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))

    add("the interpreter running stage 4 holds exactly what requirements-stage4.txt pins (no package more, none fewer, no version different; pip itself apart)",
        f"yes: the {env['packages_pinned']} packages the file pins", f"{'yes' if env['holds_exactly_what_the_file_pins'] else 'NO'}: {len(env['packages'])} packages held"
        + ("; " + "; ".join(env["differences"][:5]) if env["differences"] else ""), env["holds_exactly_what_the_file_pins"])
    inside = Path(sys.prefix).resolve().is_relative_to(G.ROOT.resolve())
    add("the stage-4 environment is outside the repository", "yes", "NO: it is inside the repository" if inside else "yes", not inside)
    for name, pattern in NAMED.items():
        v = env["packages"].get(name, "not installed")
        add(f"the stage-4 environment: {name}", {"wildboottest": "0.3.2", "numba": "0.62.1", "numpy": "2.3.x"}[name], v, bool(re.fullmatch(pattern, v)))

    shown = {}
    for rec in EARLIER_RECORDS:
        p = G.ROOT / rec
        if not p.exists():
            G.stop(f"a provenance record of an earlier stage is missing: {rec}")
        for v in numpy_in(json.loads(p.read_text(encoding="utf-8"))):
            shown.setdefault(v, []).append(rec)
    r = main_run("-c", "import numpy; print(numpy.__version__)")
    main_numpy = r.stdout.strip() if r.returncode == 0 else "numpy does not import: " + r.stderr.strip()[-120:]
    add(f"the main environment: numpy is the version the provenance records of the earlier stages show ({len(EARLIER_RECORDS)} records read)",
        "; ".join(sorted(shown)) + (" (one version in every record)" if len(shown) == 1 else " (MORE THAN ONE VERSION)"), main_numpy, len(shown) == 1 and main_numpy in shown)

    freeze = main_run("-m", "pip", "freeze")
    if freeze.returncode != 0:
        G.stop("the main environment's pip freeze failed: " + freeze.stderr.strip()[-200:])
    now = [l.strip() for l in freeze.stdout.splitlines() if l.strip()]            # in the order printed: the kept list is in that order too
    (G.OUT / "environment_main_now.txt").write_text("\n".join(now) + "\n", encoding="utf-8")
    if BEFORE.exists():
        before = [l.strip() for l in BEFORE.read_text(encoding="utf-8").splitlines() if l.strip()]
        changed = sorted(set(before) ^ set(now))
        if not changed and before != now:                                           # the same packages, in another order
            changed = [f"line {i + 1}: {b} then, {n} now" for i, (b, n) in enumerate(zip(before, now)) if b != n]
        add("the main environment's list of packages (pip freeze) against the list kept before stage 4 installed anything (50_gap/environment_before_stage4.txt)",
            f"the same, line for line ({len(before)} packages)", f"{'the same' if before == now else 'DIFFERENT'}: {len(now)} packages" + ("; " + "; ".join(changed[:6]) if changed else ""), before == now)
    else:
        add("the main environment's list of packages against the list kept before stage 4 (50_gap/environment_before_stage4.txt)", "not held: that list is not on disk",
            f"not compared; the main environment holds {len(now)} packages (50_gap/environment_main_now.txt)", True)
    stage4_only = [n for n in ("numba", "llvmlite", "wildboottest", "statsmodels", "tabulate", "matplotlib") if any(l.lower().startswith(n + "==") for l in now)]
    add("packages stage 4 added that the main environment holds (numba, llvmlite, wildboottest, statsmodels, tabulate, matplotlib)", "none", ", ".join(stage4_only) or "none", not stage4_only)

    for script, expected, good in (("verify_r620.py", "it passes (it prints no count of checks: its line of success)", lambda l: l.startswith("OK")),
                                   ("verify_layer.py", "92 of 92 checks passed", lambda l: l.startswith("92 of 92 checks passed")),
                                   ("verify_decision.py", "every check", lambda l: bool(re.match(r"(\d+) of \1 checks passed", l)))):
        v = main_run(str(G.ROOT / "scripts" / script))
        lines = [l.strip() for l in v.stdout.splitlines() if l.strip()]
        line = next((l for l in lines if l.startswith("OK ")), lines[-1] if lines else v.stderr.strip()[-160:])
        add(f"in the main environment, with numpy {main_numpy}: scripts/{script}", expected, line.split(";")[0], v.returncode == 0 and good(line))

    rows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / "gates_environment.csv", rows, ["gate", "expected", "found", "pass"])
    for row in rows:
        print(("ok   " if row["pass"] == "yes" else "FAIL ") + row["gate"] + "  |  expected " + row["expected"] + "  |  found " + row["found"])
    failed = [row for row in rows if row["pass"] != "yes"]
    inputs = {"requirements": G.IN["requirements"], **{k: p for k, p in G.IN.items() if k.startswith("provenance_")}}
    if BEFORE.exists():
        inputs["main_environment_before_stage4"] = BEFORE
    G.record_step(STEP, Path(__file__), inputs, [G.OUT / "gates_environment.csv", G.OUT / "environment_main_now.txt"],
                  {"main_environment": {"numpy": main_numpy, "packages": len(now), "the_version_the_earlier_records_show": sorted(shown)},
                   "gates": len(rows), "gates_passed": len(rows) - len(failed)})
    print(f"\n{len(rows) - len(failed)} of {len(rows)} gates passed; wrote 50_gap/gates_environment.csv")
    if failed:
        G.stop(f"{len(failed)} gate(s) on the environments failed")


if __name__ == "__main__":
    main()
