"""Stage 4: one build of `50_gap/` set against a copy kept from the build before it. Writes into `50_gap/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_compare_builds.py before_step1 --name step1
    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_compare_builds.py before_step3 --name step3 --now before_step5

When a builder or the shared module is changed and every step is run again, the question is whether any figure moved.
Before such a rebuild the outputs are copied to a folder inside `50_gap/` (here `50_gap/before_step1/`); afterwards
this script compares, file by file, what is there with what is in `50_gap/` now:

  - every file: whether its bytes are the same;
  - a table (`.csv`): whether its columns and its number of rows are the same, and how many cells differ;
  - a record (`.json`): which of its top-level keys differ (for the provenance record, which steps, and in which keys);
  - a text file: how many lines differ.

A file is a *table of figures* if it is a `.csv` and neither a gate table (`gates_*.csv`, `inputs_check.csv`) nor a
list this script or the closing checks write about a comparison (`rebuild_*_differences.csv`, `results_md_changes.csv`).
The gate: no table of figures has a cell, a column or a row that differs, and no table of figures is gone. A table
that is new is listed and is not a failure. Gate tables are compared too and reported; a gate whose `pass` is not
`yes` in the build now is a failure.

With `--now FOLDER` the later build is a kept copy too (a folder inside `50_gap/`), not `50_gap/` as it stands: a
rebuild can then be set against the build before it after later steps have run. Until 11 October 2026 the lists of
differences were classed as tables of figures, so the count of tables in the comparison written for Step 3 of the
owner's handoff was one too high; that comparison was made again with this version.

Since the owner's second handoff of 11 October 2026 a record's list of inputs or outputs that differs is given with the
files whose entry differs, so that the list says which input moved a record and not only that one did.

Writes `rebuild_<name>_differences.csv` (`file`, `kind`, `same_bytes`, `what_differs`, `why`: one row for every file
of either build; `why` is filled for the files that are expected to differ, from the short list of reasons in this
script, and says "NOT EXPECTED" for any other file that differs) and `gates_<name>.csv` (`gate`, `expected`, `found`,
`pass`). The exit status is 0 only if every gate passed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402

GATE_TABLES = ("gates_", "inputs_check.csv")
LISTS = ("rebuild_", "results_md_")                # lists of what differs between two versions of something: not tables of figures
# Why a file may differ between two builds that give the same figures. A key is the start of a file's name.
WHY = {
    "gap.provenance.json": "a step that is run again is recorded anew: the record carries each run's time and the SHA-256 of the script, of the shared module and of every input and output",
    "inputs_listing.json": "the listing of inputs, with the time it was written; it holds more inputs wherever the list of inputs grew",
    "panel_models.txt": "its first line carries the time it was written",
    "unit_history_models.txt": "its first line carries the time it was written",
    "forest_villages_pdf_record.json": "the record carries the time of the check",
    "environment_main_now.txt": "the main environment's list of packages as found at the run",
    "rebuild_": "a list this script writes: it differs when a comparison is made again",
    "results_md_changes.csv": "a list the closing checks write: it differs when docs/RESULTS.md is written again",
    "verify_gap_reviews.json": "not written by a builder",
    "figures_looked_at.json": "not written by a builder",
    "verify_gap_trials.json": "not written by a builder",
}


def kind_of(name: str) -> str:
    base = name.rsplit("/", 1)[-1]
    if base.endswith(".csv"):
        return "gate table" if base.startswith(GATE_TABLES) else "list of differences" if base.startswith(LISTS) else "table of figures"
    return {"json": "record", "txt": "text", "md": "table as markdown"}.get(base.rsplit(".", 1)[-1], "other")


def files_of(folder: Path) -> dict[str, Path]:
    out = {}
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix in (".csv", ".json", ".txt"):
            out[p.name] = p
    deck = folder / "deck_tables"
    if deck.is_dir():
        out.update({"deck_tables/" + p.name: p for p in sorted(deck.iterdir()) if p.is_file()})
    return out


def which(x, y) -> str:
    """Of two versions of a record's list of files (a dict by name or path, or a list of entries with a `path`): the files whose entry differs, in brackets; nothing for anything else."""
    def by_path(v):
        if isinstance(v, dict) and all(isinstance(e, dict) for e in v.values()):
            return {e.get("path", k): e for k, e in v.items()}
        if isinstance(v, list) and all(isinstance(e, dict) and "path" in e for e in v):
            return {e["path"]: e for e in v}
        return None
    px, py = by_path(x), by_path(y)
    if px is None or py is None:
        return ""
    names = sorted(k for k in set(px) | set(py) if px.get(k) != py.get(k))
    return " (" + ", ".join(names) + ")" if names else ""


def compare(name: str, a: Path, b: Path) -> tuple[str, bool]:
    """What differs between two versions of a file, in words, and whether a figure does (for a table: any cell, column or row)."""
    if a.read_bytes() == b.read_bytes():
        return "", False
    if name.endswith(".csv"):
        ra, rb = G.read_rows(a), G.read_rows(b)
        ca, cb = G.read_header(a), G.read_header(b)
        if ca != cb:
            return f"its columns: {len(ca)} then, {len(cb)} now", True
        if len(ra) != len(rb):
            return f"its number of rows: {len(ra)} then, {len(rb)} now", True
        cells = [(i, c) for i, (x, y) in enumerate(zip(ra, rb)) for c in ca if x[c] != y[c]]
        first = "; ".join(f"row {i + 1}, {c}: {ra[i][c][:30]!r} then, {rb[i][c][:30]!r} now" for i, c in cells[:3])
        return (f"{len(cells)} cell(s): {first}" if cells else "bytes only (the cells are the same)"), bool(cells)
    if name.endswith(".json"):
        ja, jb = json.loads(a.read_text(encoding="utf-8")), json.loads(b.read_text(encoding="utf-8"))
        if isinstance(ja, dict) and isinstance(jb, dict):
            if "steps" in ja and "steps" in jb:
                parts = []
                for s in sorted(set(ja["steps"]) | set(jb["steps"])):
                    x, y = ja["steps"].get(s), jb["steps"].get(s)
                    if x is None or y is None:
                        parts.append(f"{s}: {'new' if x is None else 'gone'}")
                    elif x != y:
                        parts.append(f"{s}: " + ", ".join(k + which(x.get(k), y.get(k)) for k in sorted(set(x) | set(y)) if x.get(k) != y.get(k)))
                return "steps that differ, and in which keys - " + "; ".join(parts), False
            keys = [k for k in sorted(set(ja) | set(jb)) if ja.get(k) != jb.get(k)]
            extra = ""
            if "inputs" in keys and isinstance(ja.get("inputs"), list) and isinstance(jb.get("inputs"), list):
                extra = f" (inputs: {len(ja['inputs'])} then, {len(jb['inputs'])} now" + (f"; the entries that differ:{which(ja['inputs'], jb['inputs'])}" if which(ja["inputs"], jb["inputs"]) else "") + ")"
            return "keys that differ: " + ", ".join(keys) + extra, False
        return "its contents", False
    la, lb = a.read_text(encoding="utf-8", errors="replace").splitlines(), b.read_text(encoding="utf-8", errors="replace").splitlines()
    n = sum(1 for x, y in zip(la, lb) if x != y) + abs(len(la) - len(lb))
    return f"{n} line(s) of {max(len(la), len(lb))}" + (f": line {next(i + 1 for i, (x, y) in enumerate(zip(la, lb)) if x != y)} first" if any(x != y for x, y in zip(la, lb)) else ""), False


def main() -> None:
    G.require_stage4_environment()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before", help="the folder inside 50_gap/ that holds the earlier build")
    ap.add_argument("--name", required=True, help="the name the two output tables carry")
    ap.add_argument("--now", help="a folder inside 50_gap/ that holds the later build; default: 50_gap/ as it stands")
    a = ap.parse_args()
    kept = G.OUT / a.before
    later = G.OUT / a.now if a.now else G.OUT
    if not kept.is_dir() or not later.is_dir():
        G.stop(f"{G.rel(kept if not kept.is_dir() else later)} is not there: no build to compare")
    was, now = files_of(kept), files_of(later)
    own = {f"rebuild_{a.name}_differences.csv", f"gates_{a.name}.csv"}
    rows, moved, gone, new = [], [], [], []
    for name in sorted((set(was) | set(now)) - own):
        kind = kind_of(name)
        if name not in now:
            rows.append({"file": name, "kind": kind, "same_bytes": "", "what_differs": "in the earlier build and not in this one", "why": "NOT EXPECTED" if kind == "table of figures" else ""})
            if kind == "table of figures":
                gone.append(name)
            continue
        if name not in was:
            rows.append({"file": name, "kind": kind, "same_bytes": "", "what_differs": "new: not in the earlier build", "why": "written since the earlier build was kept"})
            if kind == "table of figures":
                new.append(name)
            continue
        what, figure = compare(name, was[name], now[name])
        why = "" if not what else next((v for k, v in WHY.items() if name.rsplit("/", 1)[-1].startswith(k)), "NOT EXPECTED")
        if kind == "gate table" and what and why == "NOT EXPECTED":
            why = "a gate table: see the gate on the gates below"
        rows.append({"file": name, "kind": kind, "same_bytes": "no" if what else "yes", "what_differs": what, "why": why})
        if kind == "table of figures" and figure:
            moved.append(name)
    G.write_rows(G.OUT / f"rebuild_{a.name}_differences.csv", rows, ["file", "kind", "same_bytes", "what_differs", "why"])

    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    tables = [r for r in rows if r["kind"] == "table of figures" and r["same_bytes"] in ("yes", "no")]
    add(f"tables of figures in both builds ({G.rel(kept)}/ and {G.rel(later)}/) with a cell, a column or a number of rows that differs", "none",
        ", ".join(moved) or f"none (of {len(tables)} tables compared)", not moved)
    add("tables of figures of the earlier build that are gone", "none", ", ".join(gone) or "none", not gone)
    same = sum(1 for r in tables if r["same_bytes"] == "yes")
    add("tables of figures that are byte for byte what they were", f"{len(tables)} of {len(tables)}", f"{same} of {len(tables)}", same == len(tables))
    unexpected = [r["file"] for r in rows if r["why"] == "NOT EXPECTED"]
    add("files that differ and are not among those expected to (a record with a time or a hash, a listing, a text file with its time)", "none", ", ".join(unexpected) or "none", not unexpected)
    failing = []
    for name, p in now.items():
        if kind_of(name) == "gate table" and name not in own:
            failing += [f"{name}: {r['gate'][:60]}" for r in G.read_rows(p) if r.get("pass") != "yes"]
    add(f"gates of the later build that did not pass (every gate table of {G.rel(later)}/)", "none", "; ".join(failing[:4]) or "none", not failing)
    grows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / f"gates_{a.name}.csv", grows, ["gate", "expected", "found", "pass"])
    for r in rows:
        if r["same_bytes"] != "yes":
            print(f"differs  {r['file']} [{r['kind']}]: {r['what_differs'][:150]}  |  {r['why'][:90]}")
    print(f"new tables of figures: {', '.join(new) or 'none'}")
    for r in grows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in grows if r["pass"] != "yes"]
    print(f"\n{len(grows) - len(failed)} of {len(grows)} gates passed; wrote 50_gap/rebuild_{a.name}_differences.csv and 50_gap/gates_{a.name}.csv")
    if failed:
        G.stop(f"{len(failed)} gate(s) failed: a figure moved in the rebuild, or a file differs that should not")


if __name__ == "__main__":
    main()
