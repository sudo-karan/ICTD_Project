"""Writes `docs/stage4_run_log.md`: what each phase of the stage-4 run did, which gates passed, which files were
written and what comes next, so that a fresh session can resume from it.

    .venv/bin/python scripts/write_stage4_run_log.py

No figure in the log is typed. The gate tables are the gate files of `50_gap/` as the builders wrote them
(`inputs_check.csv` and `gates_*.csv`: `gate`, `expected`, `found`, `pass`); the lists of files are read from
`50_gap/gap.provenance.json`; the list of inputs and their columns from `50_gap/inputs_listing.json`; the package
versions from the two lists of the environment kept in `50_gap/`. What is typed is the notes below: what a phase was
for, what was decided in it, and where to pick up. The notes carry no figure of the analysis.

Writes one file, `docs/stage4_run_log.md`. The stage outputs it reads are not in git: if `50_gap/` is empty, run the
builders in the order the log gives under "To rebuild" and then this script.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "50_gap"
OUT = ROOT / "docs" / "stage4_run_log.md"

# One entry per phase: (number, title, the gate files it wrote, the provenance sections it wrote, the notes).
# A phase appears in the log once its first gate file exists. NOTES is typed prose; it carries no figure.
PHASES = [
    (0, "inputs, crosswalk, gates", ["inputs_check.csv"], ["08_gap_inputs"], """
**What was done.** Every input the stage reads was opened and listed with its columns (below). The district crosswalk
between R6.20's spelling and the census codes was written, with the owner's six spelling rules and no other. Every unit
was given one census district: an LGD panchayat unit its own, an outside-village unit the one assigned to it in stage 0.
Then the gates on what is already built were run, each against the value the owner read from the file or document he
names.

**Which file was used where the prompt did not name one.** "Stage 1's per-unit table of Hansen loss by year and by
canopy band (the one the decision build reads)" is `20_degradation/hansen_loss_by_canopy_band_by_unit.csv`. Each unit's
agro-climatic zone is the column `corestack_zone_model` of `20_degradation/agreement_by_unit.csv`; it is blank for the
units that have no land the CoRE Stack classes on canopy above ten per cent, and the hectares under each zone model are
in `20_degradation/corestack_by_unit.csv` for every unit. The code that classes Scheduled Tribe share in the layer is
not a function of its own: it is one expression inside `main()` of `scripts/06_build_layer.py`, built on that file's
helper `classify`.

**The environment.** The repository had no requirements file; `requirements.txt` was written, pinned. Installing
`numba`, which `wildboottest` needs, moved `numpy` down, because the newest `numba` with a wheel for this machine does
not take the `numpy` that was installed. The verifiers that existed were run again after the install and gave the
counts they gave before (the table under "The environment" below).

**What comes next.** Phase 1: the five leftovers of the last batch.
"""),
    (1, "the five leftovers", ["gates_phase1.csv"], [], """
**What was done.** Each row of the gate table names the leftover it belongs to.

- **L1.** The three counts of `docs/DECISION_LAYER.md` section 5.1 are counted on the share a unit's panel prints
  (the column `forest_loss_share_pct` of the default window, whose denominator is the forest at the start of the
  window), there and where they are repeated (sections 5.4, 7 and 17). The change is in `scripts/write_decision_layer.py`,
  which now counts them on the column itself. `scripts/verify_decision.py` gained one check: it works the three out from
  stage 1's yearly columns and holds them against the column; the writer holds its own counts against the line that check
  prints. The old and the new value of each are in the gate table.
- **L2.** `scripts/07_build_share.py` writes the copy without the development index of 2011: the field and everything
  that displays it. `60_layer/` keeps it. **Which checks of the copy changed, and why:** the builder and the gate
  (`scripts/exercise_share.py`) each held the copy's two files byte for byte against `60_layer/`'s; that cannot hold once
  the index is out, so each now holds them against the layer's files under the rule "the layer's without the index and
  nothing else". The gate gained three checks: the index's id and names are in neither file of the copy; the README says
  the index is not in the copy; and, in the browser, a ranked list, a unit's panel, the list of layers and the two text
  panels show it nowhere. Section 17.3 of `docs/DECISION_LAYER.md` records the call as reversible.
- **L3.** The README's layer section no longer quotes sizes or check counts; it points to `docs/LAYER.md` and
  `docs/DECISION_LAYER.md`. Two counts of the README's layout that had also gone stale (rows of the manifest) were
  reworded so that they carry no count.
- **L4.** The provider's developer page and its guide to API keys are registered from the fetch of 8 October 2026 that
  saved the five pages registered on 9 October: a saved copy each, a manifest row each, kept out of git like the five.
  Both pages carry the provider's whole help text, and in it cautions about the data that the first extract does not
  have; they are kept word for word in a new dated file beside `provider_cautions.json`, made and checked by a script
  beside it. `provider_cautions.json` was not edited.
- **L5.** `README.md`, `docs/DATA_NOTES.md`, `docs/LAYER.md` and `docs/DECISION_LAYER.md` give the copy's real path.
  `docs/RESULTS.md` does not mention the copy.

**A second pass of the browser checks was started and could not be finished.** The layer was not rebuilt, but the
decision verifier changed, so `scripts/run_decision_checks.py --leave-out safari` was started to bring the runner's
record up to the verifier on disk. The Safari application was not started. During the pass the machine went into
standby on a flat battery. After it woke, both verifiers and the checks in Chrome passed and the check of the layer in
WebKit passed on its second run, but the check of the decision view in WebKit stalled twice: the off-screen WebKit
view stopped answering, and it was stopped by hand. The records of the pass of 9 October 2026 were put back as they
were (the layer is the build they were made on), and the unfinished record is kept with the session's working files.
`docs/DECISION_LAYER.md` section 16 says this, with the counts of both passes. **For the owner:** the runner's record
is therefore of the verifier as it stood before it gained its new check; a pass on a machine that is awake and in use
would bring it up to date.

**Not changed, and why.** `scripts/layer_overlay.json` still says that the two pages are only with the session's working
files. It is an input of the layer's build, and rewriting it would call for a rebuild of the layer and a new pass of
every check; `docs/DECISION_LAYER.md` section 14 says where the pages are now. `docs/RESULTS.md` was not regenerated in
this phase: it does not mention the copy, and its writer is changed in Phase 8.

**A note on the session after the standby.** From then on the editor's file tools refused every call, a write to the
session's own scratch folder included, while the shell worked; name lookups on the network failed and the system
would not grant a request to stay awake. That state has been met in this project before. Files were written through
the shell from then on, and nothing that needs the network was attempted; the report to the owner says so.

**What comes next.** Phase 2: district need against district allocation (`scripts/08_build_gap_districts.py`).
"""),
    (2, "the headline, district need against district allocation", ["gates_phase2.csv"], ["08_build_gap_districts"], """
**What was done.** `scripts/08_build_gap_districts.py` built need, allocation and marginalisation for each district,
the comparisons the instruction fixed (C1 the headline), the splits by Scheduled Tribe class and by tercile, and the
table of what more is needed, with the cost at the VGPP rate present and blank. Every column is defined in the
script's docstring. The results are not repeated in this log: they are in `50_gap/need_vs_allocation_summary.csv` and
will be written into `docs/GAP.md` by its writer.

**Calls made in the run, each to be listed in `docs/GAP.md` as a proposal the owner can overrule.**

- **The rule for C7.** The instruction gave two branches: a zone recorded for every unit, or only for the units the
  agreement compared. Neither holds to the letter. The repository records the zone model for every unit that has land
  the CoRE Stack classes on canopy above ten per cent, and the hectares under each model for every unit; the units
  with no zone model carry no N1 at all (a gate). So the first branch can be decided for every district, and it was
  used: a district is left out, need and money together, where units wholly under the East Coast model hold more than
  half of its N1. A district with no N1 stays in. The gate table lists the districts, and those the other reading
  would leave out; that other reading is computed too, as `C7b`, and is not one of the fixed comparisons.
- **The direction of the development index.** `docs/DATA_NOTES.md` does not state it. `docs/NEED.md` says the index is
  the sum of five indicators each ranked from one to three, and the group's data dictionary in `00_raw/docs/` says the
  ranks run from low to advance. The builder reads both sentences and stops if either is gone. The ADI columns and
  splits are therefore in.
- **The index's source and licence line.** `docs/DATA_NOTES.md` gives no single line for `adi_2011`; it gives the
  judgement that the index is computed from census rows although its documentation mentions SHRUG's keys. The line
  carried with every district-level result built from the index is the row of the layer's own list of sources, and
  the builder holds it against that sentence of `docs/DATA_NOTES.md`.
- **Scheduled Tribe classes.** The layer's rule is not a function of its own: the builder calls the layer builder's
  helper `classify` and repeats the one expression around it. A gate holds that this gives, for every LGD unit that
  has a share, the class the layer shows for that unit.
- **Scheduled Caste terciles** are in: `30_need` carries the population.

**What comes next.** Phase 3: the district-year panel (`scripts/08_build_gap_panel.py`).
"""),
    (3, "the district-year panel", ["gates_phase3.csv"], ["08_build_gap_panel"], """
**What comes next.** Phase 4: the historical companion, units within districts (`scripts/08_build_gap_units.py`).
"""),
    (4, "the historical companion, units within districts", ["gates_phase4.csv"], ["08_build_gap_units"], """
**What comes next.** Phase 5: forest rights (`scripts/08_build_gap_rights.py`).
"""),
    (5, "forest rights, at the level the data allow", ["gates_phase5.csv"], ["08_build_gap_rights"], """
**What comes next.** Phase 6: independent verification (`scripts/verify_gap.py`).
"""),
    (6, "independent verification", ["gates_phase6.csv"], [], """
**What comes next.** Phase 7: figures and tables for the paper and the deck.
"""),
    (7, "figures and tables for the paper and the deck", ["gates_phase7.csv"], ["make_stage4_figures", "08_build_gap_deck_tables"], """
**What comes next.** Phase 8: the documents.
"""),
    (8, "docs", ["gates_phase8.csv"], [], """
**What comes next.** Nothing: the run is complete. The report to the owner follows the order he asked for.
"""),
]


def rows(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def esc(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def gate_table(path: Path) -> list[str]:
    r = rows(path)
    out = ["| gate | expected | found | pass |", "|---|---|---|---|"]
    out += [f"| {esc(x['gate'])} | {esc(x['expected'])} | {esc(x['found'])} | {esc(x['pass'])} |" for x in r]
    passed = sum(x["pass"] == "yes" for x in r)
    out.append("")
    out.append(f"*{passed} of {len(r)} gates passed (`50_gap/{path.name}`).*")
    return out


def environment() -> list[str]:
    before, after = GAP / "environment_before_stage4.txt", GAP / "environment_after_install.txt"
    if not (before.exists() and after.exists()):
        return []
    read = lambda p: dict(l.strip().split("==", 1) for l in p.read_text().splitlines() if "==" in l)
    b, a = read(before), read(after)
    out = ["### The environment", "",
           "`pip freeze` before the install of 10 October 2026 and after it (`50_gap/environment_before_stage4.txt`, "
           "`50_gap/environment_after_install.txt`). Packages not listed did not change.", "",
           "| package | before | after |", "|---|---|---|"]
    for name in sorted(set(a) | set(b), key=str.lower):
        if a.get(name) != b.get(name):
            out.append(f"| {name} | {b.get(name, 'not installed')} | {a.get(name, 'removed')} |")
    checks = GAP / "environment_verifiers_after_install.csv"
    if checks.exists():
        out += ["", "The verifiers that existed, run again after the install:", "",
                "| verifier | its last line or its line of success |", "|---|---|"]
        out += [f"| `{esc(x['verifier'])}` | {esc(x['result'])} |" for x in rows(checks)]
    return out + [""]


def inputs() -> list[str]:
    p = GAP / "inputs_listing.json"
    if not p.exists():
        return []
    listing = json.loads(p.read_text(encoding="utf-8"))
    out = ["### Inputs read, with their columns", "",
           f"*Listed {listing['run_utc']} by `scripts/08_gap_inputs.py` (`50_gap/inputs_listing.json`, which also has "
           "each file's SHA-256).*", ""]
    for e in listing["inputs"]:
        head = f"- `{e['path']}` ({e['bytes']:,} bytes"
        head += f"; {e['rows']:,} rows" if e.get("rows") is not None else ""
        head += ")"
        if e.get("columns"):
            head += ": " + ", ".join(f"`{c}`" for c in e["columns"])
        out.append(head)
    return out + [""]


def commits() -> list[str]:
    r = subprocess.run(["git", "log", "--format=%h %s", "16b1efd..HEAD"], capture_output=True, text=True, cwd=ROOT)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    if not lines:
        return []
    return ["## Commits of this run, newest first", "", "*Read from `git log` when this log was written; the commit "
            "that carries this very version of the log is the one after the newest listed.*", ""] + \
           [f"- `{l.split(' ', 1)[0]}` {l.split(' ', 1)[1]}" for l in lines] + [""]


def main() -> None:
    prov = json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8")) if (GAP / "gap.provenance.json").exists() \
        else {"steps": {}}
    written = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    done = [p for p in PHASES if all((GAP / g).exists() for g in p[2])]
    doc = ["# Stage 4: the run log", "",
           f"*Written {written} by `scripts/write_stage4_run_log.py`. The gate tables, the lists of files and the "
           "package versions are read from the files named beside them; the notes are typed and carry no figure of the "
           "analysis. The owner's prompt of 10 October 2026 set nine phases, 0 to 8, each ending in a commit.*", ""]
    if done:
        last = done[-1]
        failed = [g for p in done for g in p[2] if any(x["pass"] != "yes" for x in rows(GAP / g))]
        doc += ["## Where the run stands", "",
                f"Phases written up below: {', '.join(str(p[0]) for p in done)}. The last is Phase {last[0]}, {last[1]}."
                + (f" **A gate failed in: {', '.join('`50_gap/' + g + '`' for g in failed)}. Nothing that depends on it may run.**"
                   if failed else " Every gate of every phase listed passed."), "",
                "The stage outputs (`50_gap/`, `figures/stage4/`) are not in git. If they are missing, rebuild them: "
                "the section \"To rebuild\" at the end gives the order.", ""]
    for number, title, gate_files, steps, notes in done:
        doc += [f"## Phase {number}: {title}", "", notes.strip(), ""]
        for g in gate_files:
            doc += ["### Gates", ""] + gate_table(GAP / g) + [""]
        for s in steps:
            sec = prov["steps"].get(s)
            if not sec:
                continue
            doc += [f"### Files written by `{sec['script']}` (run {sec['run_utc']})", ""]
            doc += [f"- `{name}` ({meta['bytes']:,} bytes, sha256 `{meta['sha256'][:16]}`)" for name, meta in sec["outputs"].items()]
            doc.append("")
        if number == 0:
            doc += environment() + inputs()
    doc += commits()
    doc += ["## To rebuild", "",
            "Each builder writes into `50_gap/` only and stops at the first gate that fails. In order:", "",
            "```",
            ".venv/bin/python scripts/08_gap_inputs.py            # Phase 0",
            ".venv/bin/python scripts/08_build_gap_districts.py   # Phase 2",
            ".venv/bin/python scripts/08_build_gap_panel.py       # Phase 3",
            ".venv/bin/python scripts/08_build_gap_units.py       # Phase 4",
            ".venv/bin/python scripts/08_build_gap_rights.py      # Phase 5",
            ".venv/bin/python scripts/verify_gap.py               # Phase 6",
            ".venv/bin/python scripts/08_build_gap_deck_tables.py # Phase 7",
            ".venv/bin/python scripts/make_stage4_figures.py      # Phase 7",
            ".venv/bin/python scripts/write_gap.py                # Phase 8",
            ".venv/bin/python scripts/write_stage4_run_log.py",
            "```", "",
            "A script named above that does not exist yet belongs to a phase that has not been reached.", ""]
    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(done)} phase(s), {len(doc)} lines")


if __name__ == "__main__":
    sys.exit(main())
