"""Stage 4 run: the gates of the last three phases. Writes one gate table into `50_gap/` and nothing else.

    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_closing_checks.py --phase 6      # the verifiers and the deliberate errors
    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_closing_checks.py --phase 7      # the figures and the deck tables
    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_closing_checks.py --phase 8      # the documents, and every verifier once more

    ~/.venvs/ictd-stage4/bin/python scripts/08_gap_closing_checks.py --figures-looked-at "what was seen"

The last form is not a gate. It records, on the word of whoever runs it, that the six PNGs now in `figures/stage4/`
were opened and looked at, with the SHA-256 of each and the words given (`50_gap/figures_looked_at.json`). The gate of
Phase 7 then holds that the PNGs on disk are those the record names: a figure drawn again after it was looked at, and
drawn differently, fails it until it is looked at again.

Each writes `50_gap/gates_phase<N>.csv` (`gate`, `expected`, `found`, `pass`) for the run log. Phase 8 also writes
`50_gap/results_md_changes.csv`: every figure of `docs/RESULTS.md` that is printed differently from the version of the
commit before this run, old beside new, every figure added and every figure gone (`kind`, `as_printed_before`,
`as_printed_now`, `file`, `where_in_the_file`), for the run log and the report to the owner. It changes no file it
checks. The verifiers are run here (`verify_r620.py`, `verify_layer.py`, `verify_decision.py`, `verify_gap.py`); the gate
on the shared copy needs a browser and is not started from here: its record (`70_share/exercise_share_chrome.json`) is
read, after confirming that it is of the files on disk.

Phase 6  every verifier passes, with its count; the control and every deliberate error of
         `50_gap/verify_gap_trials.json` (at least fifteen, every table, the five kinds the owner named); the record of
         the one round of review of the verifier's parts (`50_gap/verify_gap_reviews.json`): a report for every part,
         the reader's report, and that it is of the verifier on disk; and the rebuild that followed the review moved
         no table of figures (`50_gap/gates_step3.csv`).
Phase 7  for each of F1 to F6: the PNG (300 dpi), the SVG, the CSV of what is plotted and the caption are there; the
         caption gives n and its source files; the image holds no colour (F3 excepted); the script's own layout check
         found no text on text; no title is inside the image; the font is recorded. And the three deck tables are there.
         And the six PNGs on disk are the six recorded as looked at.
Phase 8  `docs/GAP.md` has the sections the owner listed; the words of cause appear only where it says what cannot be
         shown; `docs/RESULTS.md` changed only where he said it might; the manifest only gained rows; the README has the
         specification as built and keeps the original; and every verifier passes once more.

         What the owner said might change in `docs/RESULTS.md`: the four places he named, and figures that refresh
         when the script reads today's files ("§10 and the appendix at least ... That is expected. List every figure
         that changed, old → new"). The gate holds that a figure printed differently is the time of writing or is read
         from a record of the browser checks (`60_layer/decision_runs.json`, `60_layer/exercise_*.json`), and that a
         line of the text outside the four places differs only in such figures; every one is listed in
         `50_gap/results_md_changes.csv`.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402

BEFORE_THIS_RUN = "16b1efd"
LOOKED = G.OUT / "figures_looked_at.json"
FIGS = ["F1_state_report", "F2_outside_village_asymmetry", "F3_map_of_cells", "F4_need_share_against_money_share",
        "F5_need_and_money_by_marginalisation", "F6_estimates_with_wild_bootstrap_intervals"]
KINDS = ["a swapped district code", "a part-year leak into a sum", "a shifted lag", "a wrong denominator", "a dropped East Coast exclusion"]
GAP_SECTIONS = ["What this is", "The owner's decisions of 10 October 2026", "Calls that are proposals", "Definitions", "The headline", "Why districts may be compared across the state",
                "The comparison split by marginalisation", "What more is needed", "The district-year panel", "The historical companion", "Forest rights",
                "The need read against the Forest Survey's own figures", "What this cannot show", "What this answers of the supervisor's comments",
                "How it was verified", "To rebuild", "Where every figure comes from"]


MAIN_PYTHON = Path(os.environ.get("ICTD_MAIN_PYTHON", G.ROOT / ".venv" / "bin" / "python"))
STAGE4_VERIFIERS = ("verify_gap.py",)


def run(script: str) -> tuple[int, str]:
    """A verifier's exit status and its last line. `verify_gap.py` runs with the interpreter running this script (the
    stage-4 one); the verifiers of the earlier stages run in the repository's main environment, where they belong."""
    py = sys.executable if script in STAGE4_VERIFIERS else str(MAIN_PYTHON)
    if not Path(py).exists():
        G.stop(f"scripts/{script} needs the interpreter {py}, which is not there (README.md section 0)")
    r = subprocess.run([py, str(G.ROOT / "scripts" / script)], capture_output=True, text=True, cwd=G.ROOT)
    lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    return r.returncode, next((l for l in lines if l.startswith("OK ")), lines[-1] if lines else r.stderr.strip()[-200:])


CAUSAL = re.compile(r"\b(because|led to|effect of|effects of|caused|drove|causes?|driven by)\b", re.I)
SAYS_WHAT_IT_CANNOT = re.compile(r"cannot show|nothing here shows|No figure here is an effect|only where it says so|only to say what|says nothing about (cause|why)|does not say why", re.I)


def causal_uses(text: str, cell_names: list[str]) -> list[str]:
    """The tails of the sentences of `text` that use a word of cause and do not say what the analysis cannot show. The
    decision table's own cell names ("... find the cause first") are taken out first: they are names, not claims."""
    flat = " ".join(text.split())
    for n in list(cell_names) + ["find the cause first", "find-the-cause"]:
        flat = flat.replace(n, "")
    bad = []
    for m in CAUSAL.finditer(flat):
        s0 = max(flat.rfind(". ", 0, m.start()), flat.rfind("** ", 0, m.start()))
        s1 = flat.find(". ", m.end())
        sentence = flat[s0 + 1:s1 + 1 if s1 > 0 else len(flat)]
        if not SAYS_WHAT_IT_CANNOT.search(sentence):
            bad.append(sentence[-120:])
    return bad


# The lines of the body of docs/RESULTS.md (above its section 13) that the owner said might change: the first words of each,
# as they stood at the commit before this run. A line of the old body that is gone or changed and is not one of these fails the gate.
RESULTS_LINES_THAT_MAY_CHANGE = [
    "*Written ",                                                             # the time the document was written
    "the pieces of land, the *units*. A fourth stage would set the three",   # section 1: the sentences that said stage 4 was not built
    "**That fourth stage is not built.**",
    "checks made on them. It holds no finding about whether spending follows need",
    "| the comparison of the three | `50_gap/` | **not built** | - |",       # the stage table's row
    "- **Stage 4, the comparison of forest condition, need and allocation, is not built.**",   # section 11's bullet
    "  respecifying it. `50_gap/` is empty.",
]


def figure_rows(doc: str) -> list[tuple[str, str, str]]:
    """The rows of section 13.1 of a version of docs/RESULTS.md: (as printed, file, where in the file), in order."""
    part = doc.split("### 13.1 ", 1)[1].split("\n### 13.2 ", 1)[0]
    out = []
    for line in part.splitlines():
        if line.startswith("| ") and not line.startswith("| as printed") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if len(cells) >= 3:
                out.append((cells[0], cells[1], " | ".join(cells[2:])))
    return out


def results_changes(was: str, now: str) -> tuple[list[dict], list[str], list[str]]:
    """What changed in docs/RESULTS.md: the figure rows (changed, added, gone), the lines of the old body that are
    gone or changed, and the lines of the old appendix, section 13.1 and the tally apart, that are gone or changed."""
    import difflib
    from collections import defaultdict
    a, b = defaultdict(list), defaultdict(list)
    for printed, file, where in figure_rows(was):
        a[(file, where)].append(printed)
    for printed, file, where in figure_rows(now):
        b[(file, where)].append(printed)
    rows = []
    for k in a:
        if k in b and a[k] != b[k]:
            rows.append({"kind": "changed", "as_printed_before": "; ".join(a[k]), "as_printed_now": "; ".join(b[k]), "file": k[0], "where_in_the_file": k[1]})
        elif k not in b:
            rows.append({"kind": "gone", "as_printed_before": "; ".join(a[k]), "as_printed_now": "", "file": k[0], "where_in_the_file": k[1]})
    for k in b:
        if k not in a:
            rows.append({"kind": "added", "as_printed_before": "", "as_printed_now": "; ".join(b[k]), "file": k[0], "where_in_the_file": k[1]})
    body_was, body_now = was.split("\n## 13. ", 1)[0].splitlines(), now.split("\n## 13. ", 1)[0].splitlines()
    ops = difflib.SequenceMatcher(None, body_was, body_now, autojunk=False).get_opcodes()
    gone_body = [l for tag, i1, i2, _, _ in ops if tag in ("replace", "delete") for l in body_was[i1:i2]]
    return rows, gone_body, [l for l in body_now if l not in set(body_was)]


REFRESH = ("this run", "`60_layer/decision_runs.json`", "`60_layer/exercise_")      # figures that refresh when the script reads today's files


def only_refreshed(line: str, pairs: list[tuple[str, str]], body_now: set[str]) -> bool:
    """Whether a line of the old text, with every figure that is printed differently now put in its new form, is a line
    of the text now: the line then differs in those figures and in nothing else."""
    new = line
    for old_v, new_v in sorted(pairs, key=lambda x: -len(x[0])):
        if old_v and old_v in new:
            new = new.replace(old_v, new_v)
    return new != line and new in body_now


def verifiers(add) -> None:
    code, line = run("verify_r620.py")
    add("scripts/verify_r620.py (it prints no count of checks: its line of success)", "it passes", line, code == 0 and line.startswith("OK"))
    for script, expected in (("verify_layer.py", "92 of 92 checks passed"), ("verify_decision.py", "every check"), ("verify_gap.py", "every check")):
        code, line = run(script)
        m = re.match(r"(\d+) of (\d+) checks passed", line)
        ok = code == 0 and bool(m) and m.group(1) == m.group(2) and (expected == "every check" or line.startswith(expected))
        add(f"scripts/{script}", expected, line.split(";")[0], ok)
    ex = json.loads((G.ROOT / "70_share/exercise_share_chrome.json").read_text(encoding="utf-8"))
    of_disk = all(G.sha256(G.ROOT / i["path"]) == i["sha256"] for i in ex["inputs"])
    s = ex["summary"]
    add("the gate on the shared copy (scripts/exercise_share.py, in Chrome): its record, run " + ex["run_utc"] + ", and whether it is of the files on disk",
        "every step, and yes", f"{s['steps_as_expected']} of {s['steps']} steps; {'yes' if of_disk else 'NO'}", s["steps_as_expected"] == s["steps"] and of_disk and all(x["ok"] for x in ex["steps"]))


def phase6(add) -> None:
    verifiers(add)
    t = json.loads((G.OUT / "verify_gap_trials.json").read_text(encoding="utf-8"))
    same = t["verifier_sha256"] == G.sha256(G.ROOT / "scripts/verify_gap.py")
    add("the deliberate errors were tried with the verifier that is on disk", "yes", "yes" if same else "no", same)
    add("the control: the verifier, every part, on an untouched copy of the tables", "passes", t["control"]["last_line"], t["control"]["passed"] is True)
    tr = t["trials"]
    add("deliberate errors planted in copies of the tables, and caught", "at least 15, every one caught", f"{sum(x['caught'] for x in tr)} of {len(tr)}", len(tr) >= 15 and all(x["caught"] for x in tr))
    tables = sorted({x for r in tr for x in r["tables"]})
    here = sorted([p.name for p in G.OUT.glob("*.csv") if not p.name.startswith(("gates_", "environment_", "results_md_", "rebuild_"))] + ["deck_tables/" + p.name for p in (G.OUT / "deck_tables").glob("*.csv")])
    missing = [x for x in here if x not in tables]
    add("tables of 50_gap/ in which no error was planted (apart: the gate tables, the list of what changed in docs/RESULTS.md, and the lists of what differs between two builds)", "none", ", ".join(missing) or f"none (of {len(here)})", not missing)
    kinds = {r["kind"] for r in tr}
    add("the five kinds of error the owner named are among them", "; ".join(KINDS), "; ".join(k for k in KINDS if k in kinds), all(k in kinds for k in KINDS))
    # the one round of review of the verifier's parts, from the record made of the agents' own reports
    rv = json.loads((G.OUT / "verify_gap_reviews.json").read_text(encoding="utf-8"))
    script = (G.ROOT / "scripts/verify_gap.py").read_text(encoding="utf-8")
    parts = re.findall(r"part_([a-z_]+)", re.search(r"^PARTS = \[(.*?)\]", script, re.M).group(1))
    reported = [x for r in rv["reports"] for x in r["parts"]]
    add("the one round of review: parts of the verifier, and those of them that are in one agent's report and in no other", f"{len(parts)} of {len(parts)}",
        f"{sum(reported.count(x) == 1 for x in parts)} of {len(parts)}", bool(parts) and sorted(parts) == sorted(reported))
    left = [f"{'+'.join(r['parts'])}: {r['checks_passed']} of {r['checks']}" for r in rv["reports"]]
    add("the review round: every check of every part passed on the real tables as its agent left the part", "every one", "; ".join(left), all(r["checks_passed"] == r["checks"] > 0 for r in rv["reports"]))
    reader = rv.get("reader") or {}
    add("the review round: the reader across all parts reported, and names it found defined in two pieces of the script", "reported; none",
        f"{'reported' if rv['reader_reported'] else 'NOT reported'}; {len(reader.get('names_defined_in_two_parts', ['?'])) or 'none'}",
        rv["reader_reported"] is True and reader.get("names_defined_in_two_parts") == [])
    add("the record of the review round is of the verifier that is on disk", "yes", "yes" if rv["verifier_sha256"] == G.sha256(G.ROOT / "scripts/verify_gap.py") else "no",
        rv["verifier_sha256"] == G.sha256(G.ROOT / "scripts/verify_gap.py"))
    s3 = G.read_rows(G.OUT / "gates_step3.csv")
    same = next((r["found"] for r in s3 if r["gate"].startswith("tables of figures that are byte for byte")), "not found")
    add("the rebuild that followed the review (three builders' definitions corrected): its gates, and the tables of figures that are byte for byte what they were",
        "every gate; every table", f"{sum(r['pass'] == 'yes' for r in s3)} of {len(s3)} gates; {same}", bool(s3) and all(r["pass"] == "yes" for r in s3) and bool(re.fullmatch(r"(\d+) of \1", same)))


def phase7(add) -> None:
    from PIL import Image
    import numpy as np
    prov = json.loads((G.ROOT / "figures/stage4/figures.provenance.json").read_text(encoding="utf-8"))
    add("the font of the figures (Calibri if installed, else Carlito, else matplotlib's default)", "recorded", prov["font"]["font"], bool(prov["font"]["font"]))
    for f in FIGS:
        d = G.ROOT / "figures/stage4"
        have = [e for e in ("png", "svg", "csv", "caption.txt") if (d / f"{f}.{e}").is_file() and (d / f"{f}.{e}").stat().st_size > 0]
        im = Image.open(d / f"{f}.png")
        dpi = round(float(im.info.get("dpi", (0, 0))[0]))
        a = np.asarray(im.convert("RGB")).astype(int)
        coloured = float(((abs(a[:, :, 0] - a[:, :, 1]) + abs(a[:, :, 1] - a[:, :, 2])) > 12).mean())
        cap = (d / f"{f}.caption.txt").read_text(encoding="utf-8")
        with open(d / f"{f}.csv", encoding="utf-8") as fh:
            n_rows = sum(1 for _ in fh) - 1
        lay = prov["layout_checked_by_the_script"][f]
        grey_ok = coloured == 0 if not f.startswith("F3") else coloured > 0
        ok = len(have) == 4 and dpi == 300 and "n = " in cap and "Source files:" in cap and n_rows > 0 and grey_ok and not lay["text_on_text"] \
            and not lay["text_abutting_text"] and not lay["text_on_another_marker"] and not lay["leader_line_through_another_text"] and lay.get("titles_inside_the_image", 0) == 0
        add(f"{f}: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; "
            + ("a palette of colours, the one figure allowed them" if f.startswith("F3") else "no coloured pixel") + "; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image",
            "all of it", f"files {len(have)} of 4; {dpi} dpi; {n_rows} rows plotted; coloured pixels {100 * coloured:.2f} %; text on text {len(lay['text_on_text'])}; text end to end {len(lay['text_abutting_text'])}; "
            f"labels on another's marker {len(lay['text_on_another_marker'])}; titles inside {lay.get('titles_inside_the_image', 'not recorded')}", ok)
    looked = json.loads(LOOKED.read_text(encoding="utf-8")) if LOOKED.exists() else {"files": {}, "recorded_utc": "never"}
    same_png = [f for f in FIGS if looked["files"].get(f"{f}.png") == G.sha256(G.ROOT / "figures/stage4" / f"{f}.png")]
    add(f"the six PNGs on disk are the six recorded as looked at (50_gap/figures_looked_at.json, recorded {looked['recorded_utc']})", "6 of 6",
        f"{len(same_png)} of {len(FIGS)}" + ("" if len(same_png) == len(FIGS) else "; drawn again since, or never looked at: " + ", ".join(f for f in FIGS if f not in same_png)),
        len(same_png) == len(FIGS))
    deck = [n for n in ("districts_by_need", "marginalisation_split_c1", "headline_rows") if (G.OUT / "deck_tables" / f"{n}.csv").is_file() and (G.OUT / "deck_tables" / f"{n}.md").is_file()]
    add("the three deck tables, each as .csv and .md", 3, len(deck), len(deck) == 3)
    rows = G.read_rows(G.OUT / "deck_tables/districts_by_need.csv")
    add("the deck's table of districts: rows, sorted by N1 from the largest", "30, sorted", f"{len(rows)}, {'sorted' if [float(r['n1_ha']) for r in rows] == sorted((float(r['n1_ha']) for r in rows), reverse=True) else 'NOT sorted'}",
        len(rows) == 30 and [float(r["n1_ha"]) for r in rows] == sorted((float(r["n1_ha"]) for r in rows), reverse=True))
    untracked = subprocess.run(["git", "ls-files", "figures/stage4", "50_gap"], capture_output=True, text=True, cwd=G.ROOT).stdout.split()
    add("files of figures/stage4/ and 50_gap/ that are in git (stage outputs stay out of it)", "none", ", ".join(untracked) or "none", not untracked)


def phase8(add) -> None:
    gap = (G.ROOT / "docs/GAP.md").read_text(encoding="utf-8")
    heads = [l for l in gap.splitlines() if l.startswith("#")]
    missing = [s for s in GAP_SECTIONS if not any(s in h for h in heads)]
    add("docs/GAP.md: the sections the owner listed (as headings)", "all there", "missing: " + "; ".join(missing) if missing else f"all {len(GAP_SECTIONS)} there", not missing)
    add("docs/GAP.md quotes the supervisor's question", "yes", "yes" if "determine which areas have seen forest degradation, are also marginalised, and have they seen good enough resource allocation in the past" in " ".join(gap.split()) else "no",
        "determine which areas have seen forest degradation, are also marginalised, and have they seen good enough resource allocation in the past" in " ".join(gap.split()))
    body = gap.split("## 16. Where every figure comes from")[0]
    flat = " ".join(body.split())
    names = list(json.loads((G.OUT / "gap.provenance.json").read_text(encoding="utf-8"))["steps"]["08_build_gap_districts"]["cell_names"].values())
    readme_all = (G.ROOT / "README.md").read_text(encoding="utf-8")
    results_all = (G.ROOT / "docs/RESULTS.md").read_text(encoding="utf-8")
    between = lambda text, a, b: text[text.index(a):text.index(b, text.index(a))]
    texts = [("docs/GAP.md, above its list of where every figure comes from", body),
             ("docs/stage4_run_log.md", (G.ROOT / "docs/stage4_run_log.md").read_text(encoding="utf-8")),
             ("README.md, the stage 4 section as built", between(readme_all, "### Stage 4 — need against allocation", "#### Original specification (superseded 10 October 2026)")),
             ("README.md, why the original specification was superseded", between(readme_all, "**Why it was superseded.**", "\n---\n")),
             ("README.md, section 9 as far as the corrections", between(readme_all, "## 9. What the paper and deck need out of this", "### Corrections the draft paper and deck still carry")),
             ("docs/RESULTS.md, section 14", results_all[results_all.index("## 14. Stage 4: need against allocation"):]),
             ("the six captions of figures/stage4/", "\n".join((G.ROOT / "figures/stage4" / f"{f}.caption.txt").read_text(encoding="utf-8") for f in FIGS)),
             ("the three deck tables", "\n".join(p.read_text(encoding="utf-8") for p in sorted((G.OUT / "deck_tables").glob("*.md"))))]
    for where, text in texts:
        bad = causal_uses(text, names)
        add(f"{where}: uses of \"because\", \"led to\", \"effect of\", \"caused\", \"drove\" (or \"cause\") outside a sentence that says what the analysis cannot show, the cells' own names apart", 0,
            f"{len(bad)}" + (": " + " | ".join(bad[:3]) if bad else ""), not bad)
    for phrase in ("the same money distributed by need; not a requirement", "not an overlap: titles are not mapped, and 'community' lumps CR with CFR", "VGPP ₹/ha not in 00_raw",
                   "the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier years are a frozen 2020 snapshot"):
        add(f"docs/GAP.md carries the label: {phrase}", "yes", "yes" if phrase in flat else "no", phrase in flat)
    dl = " ".join((G.ROOT / "docs/DECISION_LAYER.md").read_text(encoding="utf-8").split())
    add("docs/DECISION_LAYER.md no longer says stage 4 is not built, and points to docs/GAP.md", "yes",
        "yes" if "is not built. Nothing here stands in for it" not in dl and "Stage 4 is built, and it is another document: `docs/GAP.md`" in dl else "no",
        "is not built. Nothing here stands in for it" not in dl and "Stage 4 is built, and it is another document: `docs/GAP.md`" in dl)
    res = (G.ROOT / "docs/RESULTS.md").read_text(encoding="utf-8")
    was = subprocess.run(["git", "show", f"{BEFORE_THIS_RUN}:docs/RESULTS.md"], capture_output=True, text=True, cwd=G.ROOT).stdout
    heads_was = [l for l in was.splitlines() if l.startswith("#")]
    heads_now = [l for l in res.splitlines() if l.startswith("#")]
    add("docs/RESULTS.md: the headings it had are all there, in their order and with their numbers, and one section is appended after the last", "yes",
        f"{len(heads_was)} headings then, {len(heads_now)} now; the first {len(heads_was)} unchanged: {'yes' if heads_now[:len(heads_was)] == heads_was else 'NO'}; added: {'; '.join(heads_now[len(heads_was):])}",
        heads_now[:len(heads_was)] == heads_was and len(heads_now) == len(heads_was) + 1 and heads_now[-1].startswith("## 14."))
    changes, gone_body, new_body = results_changes(was, res)
    G.write_rows(G.OUT / "results_md_changes.csv", changes, ["kind", "as_printed_before", "as_printed_now", "file", "where_in_the_file"])
    changed = [c for c in changes if c["kind"] == "changed"]
    gone = [c for c in changes if c["kind"] == "gone"]
    pairs = [(c["as_printed_before"], c["as_printed_now"]) for c in changed if c["file"].startswith(REFRESH)]
    named = [l for l in gone_body if any(l.startswith(s) for s in RESULTS_LINES_THAT_MAY_CHANGE)]
    refreshed = [l for l in gone_body if l not in named and only_refreshed(l, pairs, set(res.split("\n## 13. ", 1)[0].splitlines()))]
    stray = [l for l in gone_body if l not in named and l not in refreshed]
    add(f"docs/RESULTS.md above its section 13, against commit {BEFORE_THIS_RUN}: lines gone or changed; those in the places the owner named (the time of writing, section 1's sentences on stage 4, "
        "the stage table's row, section 11's bullet); those that differ only in a figure that refreshed (below); and any other", "no other",
        f"{len(gone_body)} lines gone or changed: {len(named)} in the places named, {len(refreshed)} with only a refreshed figure, {len(stray)} other" + (": " + " | ".join(s[:80] for s in stray[:3]) if stray else ""),
        not stray)
    not_stage4 = [c for c in changes if c["kind"] == "added" and not (c["file"].startswith("`50_gap/") or c["file"] == "`scripts/verify_gap.py`")]
    not_refresh = [c for c in changed if not c["file"].startswith(REFRESH)]
    add(f"docs/RESULTS.md, the figures of its section 13.1 against commit {BEFORE_THIS_RUN} (written to 50_gap/results_md_changes.csv): printed differently, and those of them that are neither the time of "
        "writing nor read from a record of the browser checks, which the owner expected to refresh; gone; added, and those added that are not read from 50_gap/ or from its verifier",
        "printed differently: none but the time of writing and the browser checks' records; gone: 0; added: stage 4's only",
        f"printed differently: {len(changed)}, of them neither: {len(not_refresh)}" + (" (" + "; ".join(f"{c['as_printed_before']} -> {c['as_printed_now']}" for c in not_refresh[:3]) + ")" if not_refresh else "")
        + f"; gone: {len(gone)}; added: {len([c for c in changes if c['kind'] == 'added'])}, not stage 4's: {len(not_stage4)}",
        not not_refresh and not gone and not not_stage4)
    add("docs/RESULTS.md no longer says the fourth stage is not built", "yes", "yes" if "That fourth stage is not built" not in res and "**not built**" not in res.split("## 2.")[0] else "no",
        "That fourth stage is not built" not in res and "**not built**" not in res.split("## 2.")[0])
    now_m = G.IN["manifest"].read_bytes()
    was_m = subprocess.run(["git", "show", f"{BEFORE_THIS_RUN}:00_raw/data_manifest.csv"], capture_output=True, cwd=G.ROOT).stdout
    n_was = len(list(csv.DictReader(io.StringIO(was_m.decode("utf-8"), newline=""))))
    n_now = len(list(csv.DictReader(io.StringIO(now_m.decode("utf-8"), newline=""))))
    add(f"00_raw/data_manifest.csv against commit {BEFORE_THIS_RUN}: rows then and now, and every earlier byte as it was", "rows added, none changed",
        f"{n_was} then, {n_now} now; earlier bytes unchanged: {'yes' if now_m.startswith(was_m) else 'NO'}", now_m.startswith(was_m) and n_now > n_was)
    changed = subprocess.run(["git", "diff", "--name-status", BEFORE_THIS_RUN, "--", "00_raw"], capture_output=True, text=True, cwd=G.ROOT).stdout.split("\n")
    other = [l for l in changed if l.strip() and not l.startswith("A") and "data_manifest.csv" not in l]
    add(f"files of 00_raw/ that existed at commit {BEFORE_THIS_RUN} and are changed or gone, the manifest apart", "none", "; ".join(other) or "none", not other)
    readme = (G.ROOT / "README.md").read_text(encoding="utf-8")
    ok = "#### Original specification (superseded 10 October 2026)" in readme and "**Why it was superseded.**" in readme and "### Stage 4 — need against allocation" in readme \
        and all(f"**F{i}**" in readme for i in range(1, 7))
    add("README.md: the stage 4 section is the specification as built, the original is kept under its heading with why it was superseded, and the figures list is F1 to F6", "yes", "yes" if ok else "no", ok)
    for doc in ("README.md", "docs/GAP.md", "docs/RESULTS.md", "docs/DECISION_LAYER.md", "docs/LAYER.md", "docs/stage4_run_log.md"):
        text = (G.ROOT / doc).read_text(encoding="utf-8")
        leak = len(re.findall(r"/Users/|itsfake|api[_-]?key\s*[=:]\s*\S{12,}|token\s*[=:]\s*\S{12,}", text, re.I))
        add(f"{doc}: a path of this machine, an address of a person, or anything that looks like a key or token", 0, leak, leak == 0)
    verifiers(add)


def record_looked_at(words: str) -> None:
    files = {}
    for f in FIGS:
        png = G.ROOT / "figures/stage4" / f"{f}.png"
        if not png.is_file():
            G.stop(f"figures/stage4/{f}.png is not there: nothing was recorded")
        files[f"{f}.png"] = G.sha256(png)
    LOOKED.write_text(json.dumps({"what": "The six PNGs of figures/stage4/ as they were when someone opened and looked at each. This is that person's word, not a measurement.",
                                  "recorded_utc": G.utc_now(), "words_of_whoever_looked": words, "files": files}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"recorded the six PNGs as looked at: {G.rel(LOOKED)}")


def main() -> None:
    G.require_stage4_environment()
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, choices=[6, 7, 8])
    ap.add_argument("--figures-looked-at", metavar="WORDS", help="record that the six PNGs on disk were looked at, with these words; no gate is run")
    a = ap.parse_args()
    if a.figures_looked_at:
        return record_looked_at(a.figures_looked_at)
    if a.phase is None:
        ap.error("--phase is required")
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    {6: phase6, 7: phase7, 8: phase8}[a.phase](add)
    rows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / f"gates_phase{a.phase}.csv", rows, ["gate", "expected", "found", "pass"])
    for r in rows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in rows if r["pass"] != "yes"]
    print(f"\n{len(rows) - len(failed)} of {len(rows)} gates passed; wrote 50_gap/gates_phase{a.phase}.csv")
    if failed:
        G.stop(f"{len(failed)} gate(s) of Phase {a.phase} failed")


if __name__ == "__main__":
    main()
