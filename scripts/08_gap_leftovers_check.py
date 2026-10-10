"""Stage 4 run, Phase 1: the gates on the five leftovers of the batch of 9 October 2026. Writes `50_gap/gates_phase1.csv`
(`gate`, `expected`, `found`, `pass`) and nothing else; it changes no file it checks.

    .venv/bin/python scripts/08_gap_leftovers_check.py

What each leftover was, and what is checked of it here:

L1  The three counts of `docs/DECISION_LAYER.md` section 5.1 are put on the share a unit's panel prints
    (`forest_loss_share_pct_2018_2025`, whose denominator is the forest at the start of the window). Checked: the old
    values, counted against standing forest, as the decision build's evidence table still carries them, against the
    values the owner quoted; the new values, counted here on the column; that the document prints exactly those; and
    that its writer no longer reads the three counts made on standing forest.
L2  No file that is passed on carries unit-level `adi_2011` values. Checked: the index's id and names are nowhere in the
    data and view files of `70_share/odisha_forest_decision_layer/`; `60_layer/data.js` still has it; the copy's README
    says it is absent; the document records the call as reversible.
L3  The README's layer section no longer quotes sizes or check counts. Checked: the figures of 7 October 2026 it carried
    are gone from the README, and the section points to the two generated documents.
L4  Two more provider pages are registered. Checked: each saved copy has the bytes and the SHA-256 its manifest row
    gives; the manifest has gained rows and lost or changed none since the commit before this run; a dated file of
    what the pages say stands beside `provider_cautions.json`, which is as committed.
L5  Every document that mentions the shared copy gives its real path. Checked: each of the repository's documents that
    names `70_share` gives `70_share/odisha_forest_decision_layer/`.
And the three gates the owner set for the phase: `verify_layer.py` (92 of 92, unchanged), `verify_decision.py` (every
check, with the new count) and the gate on the shared copy (every step, the new ones included), the last read from the
record that gate wrote, after confirming that the record is of the files on disk. The two verifiers are run here.

The deliberate errors tried against the checks this phase added are counted from `50_gap/mutation_trials_phase1.json`,
which the two trial scripts of the session wrote; the row says how many were caught.
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402

BEFORE_THIS_RUN = "16b1efd"                       # the commit the run started from
SHARE = G.ROOT / "70_share" / "odisha_forest_decision_layer"
STALE_IN_README = ["19.8 MB", "5.5 MB", "92 of 92", "1,276 of 1,276", "2,447,144", "1,232,815"]
REAL_PATH = "70_share/odisha_forest_decision_layer/"


def last_line(script: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(G.ROOT / "scripts" / script)], capture_output=True, text=True, cwd=G.ROOT)
    lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    return r.returncode, (lines[-1] if lines else r.stderr.strip()[-200:])


def main() -> None:
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))

    # ---- L1
    ev = {r["key"]: r for r in G.read_rows(G.ROOT / "55_decision/condition_threshold_evidence.csv")}
    cond = G.read_rows(G.IN["condition_by_unit"])
    col, cell = "forest_loss_share_pct_2018_2025", "cell_2018_2025"
    share = lambda r: None if r[col] == "" else G.D(r[col])
    new = (sum(1 for r in cond if r[cell] == "dense_loss" and share(r) is not None and share(r) < 1),
           sum(1 for r in cond if r[cell] == "dense_loss" and share(r) is not None and share(r) < G.D("0.1")),
           sum(1 for r in cond if r[cell] in ("dense_none", "open_none") and share(r) is not None and share(r) > 2))
    old = tuple(int(float(ev[k]["value"])) for k in ("dense_loss_under_1pct", "dense_loss_under_01pct", "none_cell_over_2pct"))
    names = ("units of the find-the-cause cell that lost under 1 per cent", "units of that cell that lost under a tenth of one per cent",
             "forest-site units in a no-loss cell that lost over 2 per cent")
    for what, quoted, o in zip(names, (349, 50, 76), old):
        add(f"L1 old value, against standing forest (the version the owner last read): {what}", quoted, o, o == quoted)
    add(f"L1 new value, on the column {col}: {names[2]} (the owner's figure against window start)", 74, new[2], new[2] == 74)
    for what, o, n in zip(names, old, new):
        add(f"L1 old -> new: {what}", "the new value is the count on the column", f"{o} -> {n}", True)
    doc = (G.ROOT / "docs/DECISION_LAYER.md").read_text(encoding="utf-8")
    flat = " ".join(doc.split())
    m = re.search(r"rate of loss: ([\d,]+) of the units in \"[^\"]+\" lost under one per cent of the forest they had at the start of the "
                  r"window, and ([\d,]+) lost under a tenth of one per cent of it\..*?And the other way: ([\d,]+) forest-site units lost "
                  r"more than two per cent of the forest they had at the start of the window", flat)
    printed = tuple(int(x.replace(",", "")) for x in m.groups()) if m else None
    add("L1: the three counts docs/DECISION_LAYER.md section 5.1 prints", " / ".join(map(str, new)),
        " / ".join(map(str, printed)) if printed else "the sentence was not found", printed == new)
    again = re.search(r"And ([\d,]+) forest sites that lost over two per cent of the forest they had at the start of the window are in "
                      r"cells without loss", flat)
    seventeen = re.search(r"([\d,]+) units of the cell then called \"under pressure\" lost under one per cent of the forest they had at "
                          r"the start of the window", flat)
    add("L1: the repeats of those counts in sections 7 and 17 of the document (over 2 per cent; under 1 per cent)",
        f"{new[2]}; {new[0]}", f"{again.group(1) if again else 'not found'}; {seventeen.group(1) if seventeen else 'not found'}",
        bool(again and seventeen) and int(again.group(1).replace(",", "")) == new[2] and int(seventeen.group(1).replace(",", "")) == new[0])
    writer = (G.ROOT / "scripts/write_decision_layer.py").read_text(encoding="utf-8")
    left = [k for k in ('ev("dense_loss_under_1pct")', 'ev("dense_loss_under_01pct")', 'ev("none_cell_over_2pct")') if k in writer]
    add("L1: figures the document's writer still reads from the counts made on standing forest", "none", ", ".join(left) or "none", not left)

    # ---- L2
    words = re.compile(r"development index", re.I)
    layer_text = (G.ROOT / "60_layer/data.js").read_text(encoding="utf-8")
    found = {}
    for f in ("data.js", "index.html"):
        body = (SHARE / f).read_text(encoding="utf-8")
        found[f] = body.count("adi_2011") + len(words.findall(body)) + body.count("Aggregate Development Index")
    add("L2: times the index's id (adi_2011) or its display labels occur in the shared copy's data.js / index.html", "0 / 0",
        f"{found['data.js']} / {found['index.html']}", found == {"data.js": 0, "index.html": 0})
    add("L2: 60_layer/data.js still carries adi_2011 and the index's label", "yes",
        "yes" if "adi_2011" in layer_text and "Aggregate Development Index 2011" in layer_text else "no",
        "adi_2011" in layer_text and "Aggregate Development Index 2011" in layer_text)
    readme = (SHARE / "README.txt").read_text(encoding="utf-8").lower()
    add("L2: the shared copy's README says the development index is not in this copy", "yes",
        "yes" if "the development index is not in this copy" in readme else "no", "the development index is not in this copy" in readme)
    rec = "### 17.3" in doc and "**Reversible:**" in doc.split("### 17.3", 1)[1].split("## 18.", 1)[0]
    add("L2: section 17 of docs/DECISION_LAYER.md records the call as reversible", "yes", "yes" if rec else "no", rec)

    # ---- L3
    readme_md = (G.ROOT / "README.md").read_text(encoding="utf-8")
    stale = [s for s in STALE_IN_README if s in readme_md]
    add("L3: figures of 7 October 2026 still typed in the README (" + "; ".join(STALE_IN_README) + ")", "none", "; ".join(stale) or "none", not stale)
    section = readme_md.split("### The demo layer", 1)[1].split("### The decision view", 1)[0]
    points = "docs/LAYER.md" in section and "docs/DECISION_LAYER.md" in section and "not quoted here" in section
    add("L3: the README's layer section points to docs/LAYER.md and docs/DECISION_LAYER.md for them", "yes", "yes" if points else "no", points)

    # ---- L4
    man = list(csv.DictReader(open(G.IN["manifest"], encoding="utf-8", newline="")))
    by = {r["item_id"]: r for r in man}
    ok_pages = []
    for item in ("gfw_developer_help_page", "gfw_api_key_guide_page"):
        r = by.get(item)
        p = G.ROOT / "00_raw" / r["dest"] if r else None
        ok_pages.append(bool(r) and p.is_file() and str(p.stat().st_size) == r["bytes"] and G.sha256(p) in r["how_verified_2026_10_04"]
                        and r["ref"].startswith("https://www.globalforestwatch.org/help/developers"))
    add("L4: the two provider pages registered - a saved copy with the bytes and SHA-256 its manifest row gives", "2 of 2",
        f"{sum(ok_pages)} of 2", all(ok_pages))
    was = subprocess.run(["git", "show", f"{BEFORE_THIS_RUN}:00_raw/data_manifest.csv"], capture_output=True, cwd=G.ROOT).stdout
    now = G.IN["manifest"].read_bytes()
    n_was = len(list(csv.DictReader(io.StringIO(was.decode("utf-8"), newline=""))))
    add(f"L4: the manifest against commit {BEFORE_THIS_RUN} - rows then, rows now, and whether every earlier byte is as it was",
        "rows added, none changed", f"{n_was} then, {len(man)} now, earlier bytes unchanged: {'yes' if now.startswith(was) else 'NO'}",
        now.startswith(was) and len(man) > n_was)
    dated = sorted(p.name for p in (G.ROOT / "00_raw/05_forest_reference").glob("provider_cautions_*.json"))
    same = subprocess.run(["git", "diff", "--quiet", BEFORE_THIS_RUN, "--", "00_raw/05_forest_reference/provider_cautions.json"], cwd=G.ROOT).returncode == 0
    add("L4: a dated file of what the pages say stands beside provider_cautions.json, which is as committed", "yes",
        f"{', '.join(dated) or 'no dated file'}; provider_cautions.json unchanged: {'yes' if same else 'NO'}", bool(dated) and same)

    # ---- L5
    docs = [G.ROOT / "README.md", G.ROOT / "CLAUDE.md"] + sorted((G.ROOT / "docs").glob("*.md"))
    mention = [d for d in docs if "70_share" in d.read_text(encoding="utf-8")]
    without = [G.rel(d) for d in mention if REAL_PATH not in d.read_text(encoding="utf-8")]
    add("L5: documents that mention 70_share and do not give the path " + REAL_PATH, "none",
        ", ".join(without) or f"none (of {len(mention)}: {', '.join(G.rel(d) for d in mention)})", not without and bool(mention))

    # ---- the phase's three gates
    code, line = last_line("verify_layer.py")
    add("scripts/verify_layer.py, unchanged", "92 of 92 checks passed", line.split(";")[0], code == 0 and line.startswith("92 of 92 checks passed"))
    unchanged = subprocess.run(["git", "diff", "--quiet", BEFORE_THIS_RUN, "--", "scripts/verify_layer.py"], cwd=G.ROOT).returncode == 0
    add(f"scripts/verify_layer.py is as it was at commit {BEFORE_THIS_RUN}", "yes", "yes" if unchanged else "no", unchanged)
    code, line = last_line("verify_decision.py")
    m = re.match(r"(\d+) of (\d+) checks passed", line)
    add("scripts/verify_decision.py: every check passes (the count is new: one check was added)", "all", line.split(";")[0],
        code == 0 and bool(m) and m.group(1) == m.group(2))
    ex = json.loads((G.ROOT / "70_share/exercise_share_chrome.json").read_text(encoding="utf-8"))
    of_disk = all(G.sha256(G.ROOT / i["path"]) == i["sha256"] for i in ex["inputs"])
    s = ex["summary"]
    add("the gate on the shared copy (scripts/exercise_share.py, in Chrome): steps that did what they should, the new ones included; "
        "its record is of the files on disk", "all, and yes", f"{s['steps_as_expected']} of {s['steps']}; {'yes' if of_disk else 'NO'}",
        s["steps_as_expected"] == s["steps"] and of_disk and all(x["ok"] for x in ex["steps"]))
    trials = G.OUT / "mutation_trials_phase1.json"
    if trials.exists():
        t = json.loads(trials.read_text(encoding="utf-8"))
        caught = sum(1 for x in t["trials"] if x["caught"])
        add("deliberate errors tried against the checks added in this phase (the verifier's new check, the writer's hold on the three "
            "counts, the gate on the shared copy), and caught", "all", f"{caught} of {len(t['trials'])}", caught == len(t["trials"]))

    rows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / "gates_phase1.csv", rows, ["gate", "expected", "found", "pass"])
    for r in rows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in rows if r["pass"] != "yes"]
    print(f"\n{len(rows) - len(failed)} of {len(rows)} gates passed; wrote 50_gap/gates_phase1.csv")
    if failed:
        G.stop(f"{len(failed)} gate(s) of Phase 1 failed")


if __name__ == "__main__":
    main()
