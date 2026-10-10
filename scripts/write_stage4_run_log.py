"""Writes `docs/stage4_run_log.md`: what each phase of the stage-4 run did, which gates passed, which files were
written and what comes next, so that a fresh session can resume from it.

    ~/.venvs/ictd-stage4/bin/python scripts/write_stage4_run_log.py [--through N]

With `--through N` the log stops after Phase N, so that the commit that closes a phase carries the log as of that
phase even where a later phase's files are already on disk.

No figure in the log is typed. The gate tables are the gate files of `50_gap/` as the builders wrote them
(`inputs_check.csv` and `gates_*.csv`: `gate`, `expected`, `found`, `pass`); the lists of files are read from
`50_gap/gap.provenance.json` (the figures' from `figures/stage4/figures.provenance.json`); the list of inputs and
their columns from `50_gap/inputs_listing.json`; the package versions and the gate on the two environments from `50_gap/gates_environment.csv` and the provenance record; the deliberate errors from `50_gap/verify_gap_trials.json`; the figures of `docs/RESULTS.md` that changed
from `50_gap/results_md_changes.csv`. What is typed is the notes below: what a phase was
for, what was decided in it, and where to pick up. The notes carry no figure of the analysis.

Writes one file, `docs/stage4_run_log.md`. The stage outputs it reads are not in git: if `50_gap/` is empty, run the
builders in the order the log gives under "To rebuild" and then this script.
"""
from __future__ import annotations

import argparse
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

**The environment.** Stage 4 runs in an environment of its own, outside the repository, pinned in
`requirements-stage4.txt` to exactly what it holds (`README.md` section 0). Every builder stops unless it is run
there. The repository's main environment is as the earlier stages left it. The gate on both is
`scripts/08_gap_environment.py`; its table is under "The environments" below.

**That is the owner's correction, not how the run began.** In the first hours the bootstrap's packages were installed
into the main environment, which moved its `numpy` down, and a file `requirements.txt` was written and committed with
this phase. The owner ruled both out on the evening of 10 October 2026. The section "The owner's corrections" below
says what was undone and rebuilt.

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
**What was done.** `scripts/08_build_gap_panel.py` wrote the panel of 30 districts by 13 financial years, with the
part year flagged and kept out of every model, and fitted the seven models the instruction fixed, P1 the headline.
The estimates are in `50_gap/panel_models.csv` and `50_gap/panel_models.txt`, and will be written into `docs/GAP.md`
by its writer; they are not repeated here.

**What the run met, each to be said in `docs/GAP.md`.**

- **The two standard deviations the instruction quotes** are reproduced with n in the divisor; the gate row gives the
  figure with n - 1 beside it. No expected value was changed.
- **The bootstrap package cannot take clusters labelled with text**: its compiled loop stopped on the district codes
  as text. The clusters are passed to it as whole numbers in the sorted order of the district codes, which also fixes
  which cluster gets which weight for a given seed.
- **The p of the wild cluster bootstrap does not fall steadily on every side.** In several models it settles at a
  level instead of going on down as the tested value moves away from the estimate, and in one model it climbs back
  before falling again. The instruction's rule is applied as written: the bracket is doubled, as a whole, until p is
  below the level at both ends, and the outermost crossing is reported. **The first build did not do that**: it
  doubled each side of the bracket on its own. The part of the verifier that was written from the definitions alone
  reported the difference, the builder was changed, and the models were built again (the section on the owner's
  corrections lists which files moved). Every grid of p values is saved, not only those of the
  two cases the instruction names, and three columns of the models table say, for each side, how many times p crossed
  the level, whether it climbed back, and where it stood at the end of the bracket.
- **A warning from numpy** ("invalid value encountered in matmul") is printed during the bootstrap on this machine.
  No p value on any grid is missing. The independent verifier of Phase 6 recomputes the p values with its own code.
- **The run takes about nine minutes**: the package compiles its inner loop afresh at every call.

**What comes next.** Phase 4: the historical companion, units within districts (`scripts/08_build_gap_units.py`).
"""),
    (4, "the historical companion, units within districts", ["gates_phase4.csv"], ["08_build_gap_units"], """
**What was done.** `scripts/08_build_gap_units.py` wrote the unit history table, one row for every unit with the
flags of the samples it is in, and fitted the nine models the instruction fixed, H1 the headline, with the inference
of Phase 3. The estimates are in `50_gap/unit_history_models.csv` and `.txt`; they are not repeated here.

**Calls made in the run, each listed in `docs/GAP.md` as a proposal.**

- **H9 was run.** The instruction said to run it only if stage 1 carries the downward share for each unit. No table
  carries the share as a column; `20_degradation/corestack_by_unit.csv` carries, for every unit, the hectares of the
  degradation class and of the improvement class on land with canopy above ten per cent in 2000, and the share is one
  division of the two. It was formed for the units where the two are not both zero. If the owner reads his condition
  to the letter, H9 is the row to drop.
- **The floors are read on the hectares as the table carries them**, to four decimals. A gate holds that no unit lies
  in the last half hundredth below a floor, so the figure as the map prints it would give the same samples.
- **A unit with no row in the allocation table by year** has no works and counts as not exposed.

**The run takes about an hour**: the bootstrap package compiles its inner loop at every call, and each interval takes
about fifty calls.

**What comes next.** Phase 5: forest rights (`scripts/08_build_gap_rights.py`).
"""),
    (5, "forest rights, at the level the data allow", ["gates_phase5.csv"], ["08_build_gap_rights"], """
**What was done.** `scripts/08_build_gap_rights.py` joined the state's forest-rights report to the districts, set the
community extent beside need with the label the instruction gave, computed the two rank correlations, and set the
state's figures beside Odisha's row of the national report, read from the registered table.

**The forest villages list: the owner's rule, and where the step stopped.** The PDF was already on disk in
`00_raw/01_cfr_fra/`, where the fetch of 4 October 2026 put it, so it was not downloaded again. It is registered with
a manifest row that gives its exact size and SHA-256; the row that lists its address is as it was. It is a scan:
every page is one image, and the only text in the file is a layer made by someone else's character recognition. The
owner ruled on the evening of 10 October 2026 that the layer is unverified and is used only if two checks hold: (a)
that the district counts parsed from it equal every total and running serial number the file prints, exactly; (b)
that at least five pages chosen at random, rendered upright and read by a reader, match the parsed rows. The script
reads the layer as `pdftotext` gives it and makes six parts of check (a); the last gate of the table below gives in
how many rows each part holds. **Check (a) fails.** By the rule the step stopped there: check (b) was not run, nothing
was parsed into a table beside the PDF, and no count was added to `district_need.csv`. No character recognition was
run. The file is not matched to units.

**One page was looked at, and that is not check (b).** To see what kind of failure the layer's one bad row of the
summary page is, that page was rendered and read once by the session. The note is in the record
(`50_gap/forest_villages_pdf_record.json`) and in `docs/GAP.md`. A transcription of that page by eye, checked against
the totals it carries, as was done for the national report's table, is the owner's to ask for.

**The first version of this step**, committed with this phase before the owner's rule, tested only the arithmetic of
the summary page. The rule replaced it.

**What comes next.** Phase 6: independent verification (`scripts/verify_gap.py`).
"""),
    (6, "independent verification", ["gates_phase6.csv"], [], """
**What comes next.** Phase 7: figures and tables for the paper and the deck.
"""),
    (7, "figures and tables for the paper and the deck", ["gates_phase7.csv"], ["08_build_gap_deck_tables"], """
**What was done.** `scripts/make_stage4_figures.py` drew the six figures the instruction lists into `figures/stage4/`:
each as a PNG at the resolution asked, an SVG, the CSV of exactly what is plotted, and a caption that gives n and the
source files. `scripts/08_build_gap_deck_tables.py` cut the three tables for the deck from the stage's tables into
`50_gap/deck_tables/`, each as CSV and as markdown. Both were first run while the verifier's parts were being written,
and both were run again after the verifier of Phase 6 had passed, so the figures and the deck tables on disk are of
the tables it checked.

**How the figure rules are held.** The gate table below gives, for each figure, what a script can measure: its four
files; the resolution of the PNG; that no pixel is coloured (the map apart, whose palette is one chosen to be told
apart with colour-blind vision and whose classes are named in its legend); that no title is inside the image; and that
the script's own layout check found no text on text, no two pieces of text set end to end with less than a word's
space between them, no label on another point's marker and no leader line through a label. The font is the first of
Calibri, Carlito and matplotlib's default that the machine has; the gate table says which was found. One claim to a
figure, units in the axis titles and n on every panel are held by how the script draws them and by its captions; no
gate measures them.

**The figures were looked at, after a first round in which they could not be.** When they were first drawn the
session's file tools refused every call (Phase 1) and no image could be opened; the first captions said so. After the
second loss of power the tools worked again, and each of the six PNGs was opened and looked at. Three faults were
seen that the script's layout check had passed, and were put right:

- **F1**: the two axis titles ran end to end up the page and read as one.
- **F4**: two district names stood beside each other's points, each with its line running to its own, so that the
  figure seemed to name the two points the wrong way round; and two names read as one word.
- **F3**: the dissolved district boundaries carried dozens of rings a few millimetres across, pieces of a district
  lying inside its neighbour.

The layout check now also measures text set end to end. The names of F4 are placed by a rule that keeps each beside
its own point, or ties it there with a line that crosses no other, and the script tries many orders of placing them
and keeps the tightest arrangement. The six PNGs were looked at again after the last change;
`50_gap/figures_looked_at.json` holds their SHA-256 and what was seen, and the last-but-three gate of the table holds
that the PNGs on disk are those. A figure drawn again and differently fails that gate until it is looked at again.

**Calls made in the run.**

- **An ignore line for `figures/stage4/` was added to `.gitignore`**, as every other stage folder has one. The
  instruction said not to edit that file to admit outputs; this line keeps them out. It is the owner's to take out.
- **`matplotlib` is in stage 4's environment** to draw the figures, pinned in `requirements-stage4.txt`.
- **F4 has a second panel**, the same comparison in the earlier period (C5), beside the headline's. Districts are
  named where either share reaches a threshold the caption states; the caption lists those not named.
- **F3 leaves the smallest rings of boundary undrawn and carries a scale bar.** The caption gives the threshold, how
  many rings are left out, and the projection the bar is measured on. The units inside those rings keep their colour.
- **F6 gives a panel to each unit of measurement**, so that no two units share an axis.
- **The deck's headline rows carry more decimals than the documents print**; each column's name or the script's
  docstring states its rounding.

**What comes next.** Phase 8: the documents.
"""),
    (8, "docs", ["gates_phase8.csv"], [], """
**What was done.**

- `scripts/write_gap.py` wrote `docs/GAP.md` from the tables. No figure in it is typed; each conclusion drawn from
  figures was tested against them before it was written; its last section lists where every figure comes from. It
  has the sections the instruction lists, the owner's decisions of 10 October 2026, and the calls that are proposals.
- `scripts/write_results.py` wrote `docs/RESULTS.md` again with the four changes the instruction allowed and no
  other: the sentences of its section 1 that said the fourth stage was not built, the stage table's row, section 11's
  bullet, and one section appended after the last, so that no section changed its number. **Every figure that
  changed is listed below, old beside new.**
- `scripts/write_decision_layer.py` wrote `docs/DECISION_LAYER.md` again: the sentence that said stage 4 is not built
  now points to `docs/GAP.md`. The three counts of its section 5.1 were moved to the share a unit's panel prints in
  Phase 1.
- `README.md` has the stage as built, keeps the original specification under its own heading with a paragraph on why
  it was superseded, and lists the six figures. Its section on environments came with the owner's corrections.
- Every verifier was run once more: the last rows of the gate table.

**Calls made in the run.**

- **`docs/LAYER.md` was written again** by its working script: its sentence on stage 4 now points to `docs/GAP.md`.
  The instruction did not list that document; left alone, it would have gone on saying the stage is being built.
- **The new section of `docs/RESULTS.md` says what it changes in the sections above it** that the instruction did not
  open: section 11's bullet on forest-rights titles and section 9's sentence on stage 4 are as they were, and the new
  section says how the fourth stage bears on each.
- **Two sentences of `README.md` outside the stage 4 section were changed**: a pointer to `docs/GAP.md` was added at
  its head, and section 1 no longer says that stage 4 removes the earlier work's second limitation: as built it has
  no control for remoteness.
- **The gate on the words of cause was widened** from `docs/GAP.md` to this log, the README's stage 4 text, the new
  section of `docs/RESULTS.md`, the figures' captions and the deck tables.
- **Each verifier is run with the interpreter of its stage**: the writers of the documents find the other
  environment's interpreter themselves (`README.md`, its section on environments).

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
    gates = GAP / "gates_environment.csv"
    if not gates.exists():
        return []
    out = ["### The environments", "",
           "*The gate of `scripts/08_gap_environment.py` (`50_gap/gates_environment.csv`), run with the stage-4 "
           "interpreter.*", ""] + gate_table(gates) + [""]
    prov = json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8"))["steps"].get("08_gap_environment")
    if prov:
        e = prov["environment"]
        out += [f"The stage-4 environment as that step found it (python {e['python']}; `{e['requirements_file']}`, sha256 "
                f"`{e['requirements_sha256'][:16]}`): " + ", ".join(f"{k} {v}" for k, v in e["packages"].items()) + ".", ""]
    return out


def cells_that_differ(a: Path, b: Path) -> str:
    """Two versions of a CSV, cell by cell: how many cells differ, or what else does (its columns, its number of rows)."""
    ra, rb = rows(a), rows(b)
    if not ra and not rb:
        return "0"
    if (list(ra[0].keys()) if ra else []) != (list(rb[0].keys()) if rb else []):
        return "its columns"
    if len(ra) != len(rb):
        return f"its number of rows ({len(ra)} then, {len(rb)} now)"
    return str(sum(1 for x, y in zip(ra, rb) for k in x if x[k] != y[k]))


# The owner's handoff of 11 October 2026 set seven steps, 0 to 6. A step is listed as done here once its commit is made;
# the list is typed, and is the one place to change when a step closes.
HANDOFF_STEPS = [
    (0, "publish the shared copy to GitHub Pages", True, """
The copy of the layer that is made to be passed on is published, by the owner's decision, at the address below. It was
pushed by his own script to the branch `gh-pages` of the public repository: the copy's three files and an empty
`.nojekyll`, built as a commit in a temporary folder. No branch of this repository was pushed.

**One thing was put to the owner before the push, and changed by his answer.** The copy's README ended by saying that
terms for passing the copy on were not yet agreed, and asked that it not be passed on or published. He chose to have
that paragraph reworded, in words he approved, before publishing: it now gives the site's address and says that each
source keeps its own licence. `scripts/07_build_share.py` was changed in that paragraph and in nothing else the copy
carries; the copy was built again (its `index.html` and `data.js` are byte for byte what they were); the gate on the
copy was run again in Chrome and passed every step; then his script was run.

GitHub had switched Pages on by itself when the branch arrived, with the branch as its source; the source was set
again as instructed. `scripts/check_pages_live.py` (new, main environment) then checked the live site: the table
below. The browser asks every site for an icon by itself and this site has none; that request is refused, the
browser logs it, and the check holds that this is the only line in the browser's log. No script error was logged.

The documents that said the terms were not yet agreed were brought up to date in the same commit:
`docs/DATA_NOTES.md`, `README.md`, and, through their writers, `docs/DECISION_LAYER.md` and `docs/LAYER.md`. Two
sentences of `docs/DECISION_LAYER.md` that the fourth stage had overtaken were corrected with them: how
`scripts/write_results.py` has changed since the decision view was built, and which stage folders that build wrote.
"""),
    (1, "fix the input listing and rebuild", False, ""),
    (2, "Phase 5b: the need read against the Forest Survey's own figures", False, ""),
    (3, "finish Phase 6", False, ""),
    (4, "Phase 7", False, ""),
    (5, "Phase 8, with the additions to the account of the stage", False, ""),
    (6, "the decision view in WebKit, with the machine awake", False, ""),
]


def publication() -> list[str]:
    """Step 0 of the handoff, from the two records of the published copy."""
    pub, chk = ROOT / "70_share" / "pages_publication.json", ROOT / "70_share" / "pages_live_check.json"
    if not (pub.exists() and chk.exists()):
        return []
    p, c = json.loads(pub.read_text(encoding="utf-8")), json.loads(chk.read_text(encoding="utf-8"))
    out = [f"- the site: {p['address']}", f"- the commit at the head of `{p['branch']}` when it was checked: `{p['gh_pages_commit_when_checked']}`",
           f"- the copy: built {p['copy_built_utc']} from the layer built {p['layer_built_utc']}",
           f"- the check of the live site (`scripts/check_pages_live.py`, run {c['run_utc']}): {c['checks_passed']} of {c['checks_made']} checks passed", "",
           "| check | expected | found | pass |", "|---|---|---|---|"]
    out += [f"| {esc(x['check'])} | {esc(x['expected'])} | {esc(x['found'])} | {'yes' if x['pass'] else 'NO'} |" for x in c["checks"]]
    return out + ["", "*From `70_share/pages_publication.json` and `70_share/pages_live_check.json`, which are not in git.*", ""]


def handoff() -> list[str]:
    out = ["## The owner's handoff of 11 October 2026", "",
           "The run was taken up again on 11 October 2026 under a note from the owner "
           "(`.session_scratch_2026-10-05/handoff/2026-10-11_finish_stage4.md`, not in git). It ruled on what was open "
           "(one round of review of the verifier's parts and no more; `docs/LAYER.md` to be written again; H9 stays, as a "
           "sensitivity; `scripts/layer_overlay.json` stays as it is) and set seven steps. Each ends in a commit.", "",
           "| step | what | state |", "|---|---|---|"]
    out += [f"| {n} | {what} | {'done' if done else 'not yet'} |" for n, what, done, _ in HANDOFF_STEPS]
    out.append("")
    for n, what, done, notes in HANDOFF_STEPS:
        if done and notes.strip():
            out += [f"### Step {n}: {what}", "", notes.strip(), ""]
            if n == 0:
                out += publication()
    return out


def corrections(prov: dict) -> list[str]:
    """What the owner corrected on the evening of 10 October 2026, and each output of the stage as it was built before
    the corrections set beside the same output as it is now: by its bytes, from the two provenance records, and, for a
    table, cell by cell against the copy kept from the first build."""
    kept = GAP / "before_the_corrections"
    if not (GAP / "gates_environment.csv").exists():
        return []
    out = ["## The owner's corrections of 10 October 2026, after Phase 5", "", CORRECTIONS.strip(), ""]
    if (kept / "gap.provenance.json").exists():
        was = json.loads((kept / "gap.provenance.json").read_text(encoding="utf-8"))["steps"]
        out += ["### Each output, built before the corrections and after", "",
                "*The outputs of the first build are kept in `50_gap/before_the_corrections/` with their provenance record. "
                "\"The same bytes\" compares the SHA-256 the two records give; for a table that is not the same, the last column "
                "counts the cells that differ.*", "",
                "| step | output | the same bytes as before the corrections | cells that differ |", "|---|---|---|---|"]
        for step in sorted(set(was) | set(prov["steps"])):
            a, b = was.get(step, {}).get("outputs", {}), prov["steps"].get(step, {}).get("outputs", {})
            for name in sorted(set(a) | set(b)):
                cells = ""
                if name in a and name in b:
                    same_bytes = a[name]["sha256"] == b[name]["sha256"]
                    said = "yes" if same_bytes else "**no**"
                    old = kept / Path(name).relative_to("50_gap")
                    if not same_bytes and name.endswith(".csv") and old.exists():
                        cells = cells_that_differ(old, ROOT / name)
                else:
                    said = "new: it was not written before" if name in b else "no longer written"
                out.append(f"| `{step}` | `{name}` | {said} | {cells} |")
        out.append("")
    return out


# Shown at the head of the log for as long as Phase 6 has no gate table. It is typed, and carries no figure of the analysis.
STOPPED_IN_PHASE_6 = """
**The run was stopped in Phase 6, at the owner's request, in the first hour of 11 October 2026**, and taken up again
the same day under his handoff (the next section). Phases 0 to 5 and the owner's corrections are committed. What was
not, at the stop:

- **Phase 6, the verifier, is not finished.** `scripts/verify_gap.py` does not exist yet. Its parts are written and
  every one runs on the tables, but the review of each part by a second agent was stopped part-way, so no reviewer
  has reported; and one check of the part on the inputs fails for a reason that is the builder's: the listing of
  inputs says it holds every input the stage reads and leaves out the files that three of the steps read on their own.
  That is to be put right in the builder, and the tables built again, before the verifier is assembled, run and
  tried against the deliberate errors.
- **Phase 7 is ready and not committed**: the six figures and the three deck tables are made, their gates pass, and
  every image has been looked at.
- **Phase 8 is prepared and not run**: the writers of `docs/GAP.md` and of the new section of `docs/RESULTS.md` pass
  their dry runs; neither document has been written.

The scripts of those three phases are in the working tree, uncommitted. The working detail a fresh session needs
(where the verifier's parts are kept, the state of each at the stop, the order of what is left) is in
`.session_scratch_2026-10-05/IN_FLIGHT.md`, which is not in git.
"""


CORRECTIONS = """
The owner corrected three things after Phase 5 had been committed and before the verifier was assembled. Each was
applied before Phase 6, and the phases above are written up as they now stand.

1. **Stage 4 gets an environment of its own.** The first hours of the run had installed the bootstrap's packages into
   the repository's main environment and moved its `numpy` down. The main environment was put back to the list of
   packages it had before, to the line, and `verify_r620.py`, `verify_layer.py` and `verify_decision.py` were run
   there. Stage 4 now runs in an environment outside the repository; every builder stops unless it is run there; and
   every table of the stage was built again in it.
2. **`requirements-stage4.txt`**, at the root of the repository, pins exactly what that environment holds. The file
   `requirements.txt`, committed with Phase 0, was taken out. `README.md` has a section on the two environments, and
   every step's section of the provenance record lists the packages it ran with.
3. **The forest villages PDF.** Its text layer is someone else's character recognition and is unverified. It is used
   only if two checks hold (Phase 5, above); the first fails, and the step stops there.

Two things were changed with the rebuild that the owner did not ask for, and both are listed in `docs/GAP.md` as
proposals. The bracket of the bootstrap interval is now doubled as a whole (Phase 3, above). And the two totals of
the comparison of intensities are blank in the summary of comparisons: thirty ratios added are a total of nothing.

**What moved.** The table at the end of this section sets every output of the first build beside the same output
now. The tables of figures are byte for byte what they were, with two exceptions the table counts cell by cell: the
summary of comparisons (the two totals now blank) and the table of the panel models (the p at the outer end of the
bracket, on the two sides whose bracket is now wider; no estimate, no interval and no p of a model moved). The other
files that differ are the record and the gate table of the forest villages step, which follow the owner's rule, and
files that carry the time they were written or the grids of the wider brackets.

After the second loss of power the session's file tools and the network worked again. That is how the new
environment could be installed, how one page of the PDF could be looked at, and how the figures could at last be
looked at (Phase 7).

The verifier's parts were being written by four agents when the machine lost power a second time. Each had finished
its part and was running its last trials; none had reported. Their parts and working folders were on disk and were
kept. Each part was then reviewed, attacked and brought up to date by a fresh agent (Phase 6).
"""


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


def trials() -> list[str]:
    p = GAP / "verify_gap_trials.json"
    if not p.exists():
        return []
    t = json.loads(p.read_text(encoding="utf-8"))
    out = ["### The deliberate errors", "",
           f"*Run {t['run_utc']} by `scripts/verify_gap_trials.py` (`50_gap/verify_gap_trials.json`): {t['how']}.*", "",
           f"The control, {t['control']['what']}: {t['control']['last_line']}.", "",
           "| error planted | kind | table damaged | parts of the verifier run | checks failed, of those run | caught |",
           "|---|---|---|---|---|---|"]
    for x in t["trials"]:
        out.append(f"| {esc(x['name'])} | {esc(x['kind'])} | {', '.join('`' + y + '`' for y in x['tables'])} | "
                   f"{', '.join(x['parts_run'])} | {x['checks_failed']} of {x['checks_run']} | {'yes' if x['caught'] else 'NO'} |")
    out += ["", f"*{sum(x['caught'] for x in t['trials'])} of {len(t['trials'])} errors caught; tables damaged: "
            f"{len({y for x in t['trials'] for y in x['tables']})}.*", ""]
    return out


def figures() -> list[str]:
    p = ROOT / "figures" / "stage4" / "figures.provenance.json"
    if not p.exists():
        return []
    f = json.loads(p.read_text(encoding="utf-8"))
    out = [f"### Files written by `{f['script']}` (run {f['run_utc']}; font {f['font']['font']})", ""]
    out += [f"- `{name}` ({meta['bytes']:,} bytes, sha256 `{meta['sha256'][:16]}`)" for name, meta in f["outputs"].items()]
    return out + [""]


def results_changes() -> list[str]:
    p = GAP / "results_md_changes.csv"
    if not p.exists():
        return []
    r = rows(p)
    out = ["### Figures of `docs/RESULTS.md` that changed when it was written again", "",
           "*Its section 13.1 lists every figure in its text with the file it is read from. This is that list set "
           "against the same list in the version of the commit before this run (`50_gap/results_md_changes.csv`, "
           "written by `scripts/08_gap_closing_checks.py --phase 8`).*", ""]
    for kind, title in (("changed", "Printed differently, old → new"), ("gone", "Gone"), ("added", "Added")):
        some = [x for x in r if x["kind"] == kind]
        out += [f"**{title}: {len(some)}.**", ""]
        if not some:
            continue
        if kind == "changed":
            out += ["| before | now | file | where in the file |", "|---|---|---|---|"]
            out += [f"| {esc(x['as_printed_before'])} | {esc(x['as_printed_now'])} | {esc(x['file'])} | {esc(x['where_in_the_file'])} |" for x in some]
        else:
            col = "as_printed_before" if kind == "gone" else "as_printed_now"
            out += ["| as printed | file | where in the file |", "|---|---|---|"]
            out += [f"| {esc(x[col])} | {esc(x['file'])} | {esc(x['where_in_the_file'])} |" for x in some]
        out.append("")
    return out


def commits() -> list[str]:
    r = subprocess.run(["git", "log", "--format=%h %s", "16b1efd..HEAD"], capture_output=True, text=True, cwd=ROOT)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    if not lines:
        return []
    return ["## Commits of this run, newest first", "", "*Read from `git log` when this log was written; the commit "
            "that carries this very version of the log is the one after the newest listed.*", ""] + \
           [f"- `{l.split(' ', 1)[0]}` {l.split(' ', 1)[1]}" for l in lines] + [""]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--through", type=int, metavar="N", help="stop the log after Phase N")
    a = ap.parse_args()
    prov = json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8")) if (GAP / "gap.provenance.json").exists() \
        else {"steps": {}}
    written = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    done = [p for p in PHASES if all((GAP / g).exists() for g in p[2]) and (a.through is None or p[0] <= a.through)]
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
        if not (GAP / "gates_phase6.csv").exists():
            doc += [STOPPED_IN_PHASE_6.strip(), ""]
        doc += handoff()
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
        if number == 5:
            doc += corrections(prov)
        if number == 6:
            doc += trials()
        if number == 7:
            doc += figures()
        if number == 8:
            doc += results_changes()
    doc += commits()
    doc += ["## To rebuild", "",
            "Each builder writes into `50_gap/` only and stops at the first gate that fails. In order:", "",
            "```",
            "python3.12 -m venv ~/.venvs/ictd-stage4      # once: stage 4's own environment (README.md section 0)",
            "PY=~/.venvs/ictd-stage4/bin/python",
            "$PY -m pip install --only-binary=:all: -r requirements-stage4.txt",
            "$PY scripts/08_gap_environment.py        # the gate on the two environments",
            "$PY scripts/08_gap_inputs.py             # Phase 0",
            "$PY scripts/08_build_gap_districts.py    # Phase 2",
            "$PY scripts/08_build_gap_panel.py        # Phase 3",
            "$PY scripts/08_build_gap_units.py        # Phase 4",
            "$PY scripts/08_build_gap_rights.py       # Phase 5",
            "$PY scripts/verify_gap.py                # Phase 6",
            "$PY scripts/verify_gap_trials.py         # Phase 6",
            "$PY scripts/08_build_gap_deck_tables.py  # Phase 7",
            "$PY scripts/make_stage4_figures.py       # Phase 7",
            "$PY scripts/write_gap.py                 # Phase 8",
            "$PY scripts/08_gap_closing_checks.py --phase 6   # and 7, and 8: the gates of the last three phases",
            "$PY scripts/write_stage4_run_log.py",
            ".venv/bin/python scripts/write_results.py            # Phase 8, in the main environment",
            ".venv/bin/python scripts/write_decision_layer.py     # Phase 8, in the main environment",
            "```", "",
            "A script named above that does not exist yet belongs to a phase that has not been reached.", ""]
    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(done)} phase(s), {len(doc)} lines")


if __name__ == "__main__":
    sys.exit(main())
