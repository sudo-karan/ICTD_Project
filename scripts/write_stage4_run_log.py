"""Writes `docs/stage4_run_log.md`: what each phase of the stage-4 run did, which gates passed, which files were
written and what comes next, so that a fresh session can resume from it.

    ~/.venvs/ictd-stage4/bin/python scripts/write_stage4_run_log.py [--through N]

With `--through N` the log stops after Phase N, so that the commit that closes a phase carries the log as of that
phase even where a later phase's files are already on disk.

No figure in the log is typed. The gate tables are the gate files of `50_gap/` as the builders wrote them
(`inputs_check.csv` and `gates_*.csv`: `gate`, `expected`, `found`, `pass`); the lists of files are read from
`50_gap/gap.provenance.json` (the figures' from `figures/stage4/figures.provenance.json`); the list of inputs and
their columns from `50_gap/inputs_listing.json`; the package versions and the gate on the two environments from `50_gap/gates_environment.csv` and the provenance record; the deliberate errors from `50_gap/verify_gap_trials.json`; the counts of the review of the verifier's parts from `50_gap/verify_gap_reviews.json`; the figures of `docs/RESULTS.md` that changed
from `50_gap/results_md_changes.csv`. What is typed is the notes below: what a phase was
for, what was decided in it, and where to pick up. The notes carry no figure of the analysis.

Since the owner's second handoff of 11 October 2026 (the page's words; `docs/SITE_COPY.md` is its account) the layer and
the copy have been built again, and the records beside them are of the new builds. The two tables of the first handoff
that are printed from such records - the publication of its Step 0 and the runs of its Step 6 - are therefore read from
the copies of `60_layer/` and `70_share/` that were kept before a word was changed (working files, not in git), where
those copies are there, so that each table stays the record of its own step. The second handoff has a section of its
own.

The owner's third handoff of that day (six lines of the page in his words, and publishing) has a section too. The
layer and the copy were built once more for it, so the second handoff's tables - the comparison of its Step 5 and the
runs of its checks - are read in the same way from what was kept before the six lines.

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
KEPT = ROOT / ".session_scratch_2026-10-05"                       # working files of the sessions: not in git
KEPT_SIX_LAYER, KEPT_SIX_SHARE = KEPT / "60_layer_2026-10-11_before_six_fixes", KEPT / "70_share_2026-10-11_before_six_fixes"   # the two builds as they stood before the owner's six lines (his third handoff of 11 October 2026)
KEPT_GAP_WORDS = KEPT / "50_gap_2026-10-11_site_words_step5"       # the comparison of the second handoff's Step 5, as it stood before stage 4 followed the layer once more
KEPT_LAYER, KEPT_SHARE = KEPT / "60_layer_2026-10-11_before_words", KEPT / "70_share_2026-10-11_before_words"      # the two builds as they stood before the page's words were rewritten

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
**What was done.** `scripts/verify_gap.py` recomputes the figures of the tables the stage's steps write into
`50_gap/`, from the inputs, and compares. It imports nothing from the builders and shares no code with them. It is one script made of ten parts, one
for each group of tables; its last line is the count of checks that passed. `scripts/verify_gap_trials.py` plants
deliberate errors, one at a time, in copies of the tables outside the repository and runs the verifier on each copy.
The gate table below holds that every verifier of the project passes, that the verifier passes on an untouched copy,
and that every planted error is caught.

**Who wrote the parts.** Seven parts were each written by an agent that was given the builders' docstrings and was
not allowed to open the builders: the inputs, the districts, the comparisons, the panel, the unit models, forest
rights, and the Forest Survey's figures. Three parts compare a file with the file it is derived from (the two
environments, the deck tables, the text files of the models); they were written by the session that wrote the
builders.

**The review: one round, as the owner ruled.** Two earlier rounds had been cut off, the first when the machine lost
power and the second when the owner asked the run to stop; what those agents had left in the part files was kept, and
was where this round began. In this round one agent reviewed each of the first six parts, one reviewed the three
small parts together, and the agent that wrote the Forest Survey part tried it itself: no second agent reviewed that
part. Each began from the part as it stood, planted errors of the kinds a builder makes, one at a time, in fresh
copies of the tables, mended the checks that let one through, and reported its disagreements with the tables, the
readings it had to assume, what its part does not cover, and the errors it planted. The table under "The review
round" gives each agent's counts. One more agent then read across all ten parts for columns that no check reads.

**No figure disagrees.** Every figure of every table was reproduced from the definitions. The three disagreements in
the table below are all about words in a builder's definition that did not hold of what the builder writes, and the
writer of the Forest Survey part reported three more of the same kind as observations. All were put right in the
builders, which is where the fault lay:

- **The gate on the environments** said that the main environment's list of packages was, line for line, the list
  kept before stage 4 installed anything, and that the file it writes is `pip freeze` as found. The script had
  sorted the list before writing it, so two lines stood in the other order: the same packages at the same versions,
  in another order. It now keeps the order printed and compares line by line.
- **The same gate's definition** said it reads the provenance records of the earlier stages in four folders. It
  reads the records the stage lists among its inputs. Those folders hold two more records that carry a version, of
  builds the stage does not read. The definition now says which records are read; the verifier reads every record,
  those two included, and all show one version.
- **The deck tables' definition** said that each column's name states its rounding. The rounding is stated in the
  definition's list of columns; the names carry none.
- **The Forest Survey step's definition** called one cell "one sentence" where it holds a short text of three; did
  not say that a statistic is written as a number, so that a final zero is not printed; and listed one gate fewer
  than the step writes.

The three steps were run again and every output set against a copy of the build kept from before
(`50_gap/before_step3/`): no table of figures moved. The comparison is under "The rebuild after the review".

*A correction to that comparison, made in Step 5.* As first written it counted one table of figures too many: the
comparison script classed its own earlier list of differences as a table of figures. The script now sets such
lists apart, and the comparison was made again, against a copy of the build kept just before Step 5
(`50_gap/before_step5/`), so that it shows what the rebuild of this step moved and nothing later. The table below
is the corrected one; the message of the commit of Step 3 carries the first count.

**Planted errors that the part concerned did not catch.** The table gives them as the difference between planted
and caught; all are the part on the inputs', and its reviewer left each as it was and said so:

- a number written without its final zeros: the part compares numbers as numbers, and no figure differs;
- the rows of the crosswalk in another order: no definition gives their order;
- a run time moved by an hour, still in the right form: there is nothing to hold a time against;
- one step recorded under the SHA-256 of another step's script: the part on the inputs holds only the form of that
  field. The part on the environments holds every step's script and shared module against the files on disk, so the
  assembled verifier does catch it, and it is one of the trials below.

**What the reader across all parts found.** By reading every part, and not by trial: every column of the tables
the steps write is read by at least one check, and no figure column is unread; the label columns are held by key
words only; no name is defined in two pieces of the script. What no check reads sits in the provenance record: its
top-level description, the sentences of prose a step records about itself, and, for some of the steps, whether the
files a step lists as written or as read are all that its definition names. The reader named six descriptions or
check names that claim more than the code tests:

- the script's own first line said it recomputes every figure of every table in the folder. Files that no step
  writes are read by no part, the deck tables and the text files are held against other outputs, and labels are
  held by key words. The description now says so;
- a check name of the part on the inputs said the hashes of the scripts are held nowhere; the part on the
  environments holds them. The name now says that;
- two check names of the panel part: one credited the part on the inputs with holding fields of which it holds
  only the form, the other named two files of which it reads no cell. Both now say what is done;
- a check name of the deck part said no cell goes unread while the words on each interval were read for a few
  phrases only: closed by the check added to that part (below);
- the checks that hold the owner's expected values and spelling rules say they hold them "as he wrote" them. The
  values are typed into the parts; no file of the repository carries his instruction for a check to read. That
  cannot be mended in the script. The session held them by hand: every number and every name typed for them in the
  parts is found in his prompt of 10 October or in his handoff of 11 October.

**What the session changed after the round**, with no agent to review it. The pieces concerned are named, with
their SHA-256 before and after, under "The review round".

- The head of the script: the description as above; who wrote each part; and that a permutation p and a bootstrap
  interval of a rank correlation are held twice, with the verifier's own draws to a stated tolerance, and drawn
  again with the recorded seeds to the digit. Two reviewers and the writer of the Forest Survey part added that
  second check, each on one stated reading of how the random generator is called, which the definitions do not
  give.
- The words of the three check names above, in the parts on the inputs and the panel. No test was changed in
  either part.
- The deck part gained one check: the words that describe each interval are held as whole cells, with the number of
  clusters and the bootstrap's weights taken from the model's own row. The reviewer of that part had found those
  words unread and left them, having reached its limit of planted errors.
- The environment part's check on the two lists of packages now holds their order too, as the corrected builder
  writes it.

Each of the two changed checks has a planted error of its own among the trials below, and each is caught.

**The planted errors.** A trial counts as caught only if a check of content fails. A builder with the fault would
have recorded the table it wrote, so before the verifier runs, the copy's provenance record is given the size and
SHA-256 of the damaged table; a stale digest then catches nothing. The trials that run the part on the inputs are
the exception: that part holds the record against the repository's own files, which a copy never changes. Five
trials were added in this step to those written earlier: one for each of the two checks the session changed, one
that writes a package of stage 4 into the main environment's list, one that records a step under another step's
script, and one in which the record of the forest villages PDF and its copy in the provenance record both say the
owner's first check holds, so that only the rule itself can tell.

**What the verifier does not hold.** In brief, from the reviewers' lists; each agent's own list, and every reading
it assumed, is in `50_gap/verify_gap_reviews.json` (not in git; a copy is kept beside the working notes).

- **Words.** The free prose of labels, notes and reasons is held by key words, which each check names; a label that
  is wrong in some other way would pass.
- **Order and print.** The order of rows and of columns where no definition gives one; and how many decimals a cell
  prints where cells are compared as numbers.
- **Times.** The time a step records: its form only. There is nothing to hold a time against.
- **Readings the definitions do not give.** How the random generator is called, for the checks that draw again with
  the recorded seeds; which point of the last bracket of the bisection is reported as an end of an interval; what
  the grids' count of tests counts. Each is stated in the name of the check that rests on it.
- **Branches no table reaches.** An interval with an unbounded side, a bracket doubled more than once, a blank
  denominator: the parts carry them, and they were tried on made-up tables only.
- **The package.** The bootstrap package is called at some of the points of each inversion; the rest are held by
  the parts' own arithmetic with the package's weights, which agrees with the package where both are computed.
- **What lies outside the repository.** Whether the registered text of the Forest Survey's pages is a faithful
  extract of the report; the owner's second check of the forest villages PDF, which needs pages read by a reader.
- **The main environment as it is now.** The verifier does not open it; the gate table of this phase runs the three
  earlier verifiers there instead.
- **Derived files.** The parts on the deck tables and the text files hold a derived file against its source; a
  figure wrong in both alike is the source part's to catch.

**For the owner to rule.**

- **One input is in no listing.** The list of packages kept before stage 4 installed anything
  (`50_gap/environment_before_stage4.txt`) is read by the gate on the environments, is written by no step, and is
  not in the listing of inputs, which leaves out the stage's own folder. The verifier lets that one file through by
  name. If the listing should hold it, the shared module's list gains one entry and every step is run again.
- **One gate of Phase 2 cannot tell two readings apart.** It is printed to one decimal, and at that precision a
  work with no start year counted as started early gives the same figure. The district table's own columns do tell
  them apart, and the verifier holds those exactly.
- **The seeded checks** rest on a reading of the generator's calls. If nothing should rest on a reading the
  definitions do not give, those checks can be taken out and the tolerance checks stand alone.

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
- **The deck's headline rows carry more decimals than the documents print**; the script's docstring states the
  rounding of each column.

**What comes next.** Phase 8: the documents.
"""),
    (8, "docs", ["gates_phase8.csv"], [], """
**What was done.**

- `scripts/write_gap.py` wrote `docs/GAP.md` from the tables. No figure in it is typed; each conclusion drawn from
  figures was tested against them before it was written; its last section lists where every figure comes from. It
  has the sections the instruction lists, the owner's decisions of 10 October 2026, and the calls that are proposals.
  What the owner's handoff of 11 October added to it, and the reading of the whole of it, are under Step 5 at the
  head of this log.
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
- **The gate on the five words the owner named was widened** from `docs/GAP.md` to this log, the README's stage 4 text, the new
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


STEP_7_DONE, STEP_8_DONE = True, False                            # the SECOND handoff's last two steps (below): set when each one's commit is made
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
    (1, "fix the input listing and rebuild", True, """
The listing of inputs that step 0 writes (`50_gap/inputs_listing.json`) now holds every input that any step of the
stage reads. It had held only the inputs that several steps share, and left out the files that one step each read on
its own: the forest villages PDF; the two files of the layer that the districts step reads; and the provenance
records of the earlier stages and the requirements file, which the gate on the environments reads. The verifier's
part on the inputs had found that. The list of inputs is kept in one place, the shared module, and the shared module
now stops any step that records an input from outside it, so the listing cannot fall behind again. The Forest
Survey's table, which Step 2 reads, was put on the list at the same time, so that the list would not change twice.

Every builder was then run again in the stage-4 environment, in the order given under "To rebuild", and
`scripts/08_gap_compare_builds.py` (new) set every output beside the copy kept from before the change
(`50_gap/before_step1/`). **No table of figures moved**: each is byte for byte what it was. The files that differ
are records that carry a time or a hash, the listing itself, and the two text files of the models, whose first line
is the time they were written; the table below gives each, with what differs and why. The verifier's part on the
inputs, whose one failing check was this finding, passes every check on the rebuilt listing.
"""),
    (2, "Phase 5b: the need read against the Forest Survey's own figures", True, """
`scripts/08_build_gap_fsi.py` (new, stage-4 environment) reads the table of forest cover by district in the Forest
Survey of India's report of 2023 from the registered text of its pages, which was already in `00_raw/` with a
manifest row and was not changed. It matches the table's thirty rows to the census districts, five of them by the
owner's spelling rule and no other; holds every column that can be added against the table's own printed total and
against the figure the owner gave for it; and sets, beside each district's N1, the Survey's forest cover, its change
with respect to the assessment of 2021, and its scrub. Four rank correlations are computed as in Phase 2, with fixed
seeds that the table and the provenance record carry.

**What the step does not say.** The two sources measure different things: Hansen records gross, stand-replacing loss
year by year; the Survey reports the net change in forest cover between two assessments, and the area of scrub. They
are not the same quantity and neither can be subtracted from the other. The step names no reason for either figure.
The reading of the four correlations is written into `docs/GAP.md` in Step 5, each statement tested against the
table first.

**Calls made in the run.**

- **The table keeps all eight numbers of each row**, not only those the comparison uses, so that each column's sum
  can be held against the printed total and the verifier can check the reading of the whole row.
- **The two per cents are taken on the Survey's own forest cover of 2023**: scrub over forest cover, and the change
  over forest cover.
- **The correlations have a table of their own**, `50_gap/fsi_summary.csv`, with a column that says whether size is
  taken out of both sides.
- **Two checks of the table against itself were added to the owner's**: that the three density classes of every row
  add to its total, and that every printed per cent is the total over the calculated area.

The verifier's part on this step and the deliberate errors against it come with Step 3.
"""),
    (3, "finish Phase 6", True, """
The verifier's parts had their one round of review, and the reader across all parts reported. `scripts/verify_gap.py`
was then assembled from the parts, after holding that no top-level name is defined in two of them. Its last line is
the count of its checks, and every check passes on the tables. `scripts/verify_gap_trials.py` planted its errors,
Step 2's among them, and the verifier caught every one. The gate on the shared copy was run again in Chrome, and the
closing checks of Phase 6 passed. What the reviewers found, what was changed, the trials and the comparison of the
rebuild are written up under Phase 6 below.

**Calls made in this step.**

- **Three builders were changed in their written definitions**, and one of them also in what it writes: the gate on
  the environments now writes the main environment's list of packages in the order `pip freeze` prints it. The
  reviewers had found that the definitions did not hold of the tables. The three steps were run again; no table of
  figures moved.
- **The session changed the verifier after the round**, in the pieces Phase 6 names: its description and three check
  names reworded, one check added, one tightened. The ruling allows one round, so no agent reviewed those changes;
  each changed check has a planted error of its own, and both are caught.
- **A planted error counts as caught only on a check of content.** Before the verifier runs on a damaged copy, the
  copy's provenance record is given the size and SHA-256 of the damaged table, as a builder with the fault would
  have recorded it; a stale digest then catches nothing.
- **The owner's expected values, typed into the parts, were held by hand** against his prompt of 10 October and his
  handoff of 11 October: every number and name typed for them is found there. No file of the repository carries
  them for a check to read.
- **The record of the round is kept outside git**, in `50_gap/verify_gap_reviews.json`, with a copy beside the
  working notes: every agent's report in its own words, with the readings it assumed and what its part does not
  cover. This log gives the counts and a summary.
"""),
    (4, "Phase 7", True, """
The three deck tables and the six figures were made again, after the verifier had passed, from the tables it checked.
The six images are byte for byte the images that were opened and looked at on 10 October 2026, so none had to be
looked at again, and the record of that look stands. No figure was added. The gates of Phase 7 pass; they are under
Phase 7 below, with the notes on how the figure rules are held and what was changed after the figures were first
looked at.
"""),
    (5, "Phase 8, with the additions to the account of the stage", True, """
`docs/GAP.md` was written with the additions the handoff set. Each statement was tested against the tables before
it was written.

- The headline is not read alone. The volumes come first; the rank correlation stands beside the benchmark of
  district size and beside the comparison with size taken out of both sides.
- A section sets the need beside the Forest Survey's own figures. It says what each source measures and that they
  are not the same quantity, gives the four rank correlations, and names shifting cultivation and the harvest of
  plantations only as readings this run cannot test.
- H9 is written as a lead and not a finding, with the four things it is to be read with.
- The two rank correlations on forest rights are read together.
- "What this cannot show" names invasive cover, tree species and costing.
- A section takes the supervisor's comments point by point: what answers each, by section and figure, and what is
  not answered.

**The reading of the whole document.** All of `docs/GAP.md` was then read for sentences that say more than the rows
do. These were changed, and where a statement had no test, one was written:

- two headings said that the window and the East Coast districts "do not matter"; what the rows show is that rho
  moves little, and the headings now say that;
- the three comparisons with earlier money give a higher rho than the headline; the text now adds that each
  interval overlaps the headline's, so that none is shown to differ from it;
- the owner's sentence on the panel's design says that loss rose after 2018; the two yearly means behind it are now
  printed and tested;
- a sentence on forest rights said both figures are larger in larger and more forested districts: forest was
  tested, size was not. It now speaks of forest only, and the rank correlation of N1 with the forest of 2000 is
  printed beside that of community extent;
- two sentences said that gross loss and scrub "move together": they are ranks across districts at one time, and
  the text now says so;
- the paragraph of readings the run cannot test stated what rotational clearing does; it now only names the
  readings;
- outside-village land is reached by no panchayat plan: that sentence is the owner's, from his instruction of
  10 October, and it is kept and marked as his. Beside it the text now says what the tables show of it: the land
  lies in no panchayat unit of the layer;
- what the plantation category takes in is now said as `README.md` has it, with the pointer;
- the count of gates named the steps wrongly;
- the verifier was said to recompute every figure of every table, here and in two places of `docs/RESULTS.md` and
  `README.md`; each now says what it recomputes, and `docs/GAP.md` says what it does not hold.

Three lead-ins that read as claims were kept: they are the owner's own words for what a comparison asks (the land
that panchayat planning can reach; where open forest could regenerate; the old geography).

**Calls made in this step.**

- **The supervisor's comments are registered in a new folder of `00_raw/`**, with a manifest row. A script beside
  the record reads them out of the owner's note, word for word, and stops unless the note is the file that was given
  and every point stands in it. The folder that holds the group's documents is not in git and this record cannot be
  fetched again, so it has a folder that is. The two steps that record the manifest were run again, and no table of
  figures moved: the comparison is below.
- **The fourth stage's headline row in `docs/RESULTS.md` follows the same order**: volumes first, then the rank
  correlation beside the benchmark and the comparison with size taken out. Three figures were added for that, all
  from the stage's own tables. No figure that the document already carried changed.
- **`docs/LAYER.md` was written again**, as ruled; its sentence on stage 4 and the time of one check changed.
- **A count in Step 3's comparison was corrected** (Phase 6 below).
- **One word of the supervisor's question is spelt two ways.** Section 1 of `docs/GAP.md` quotes it as the owner's
  prompt of 10 October gave it, and the new section quotes it as his note of 11 October records it. Each is left as
  its source has it.
"""),
    (6, "the decision view in WebKit, with the machine awake", True, """
`scripts/run_decision_checks.py` was run with the two checks in the Safari application left out, on mains power, the
machine kept awake, and nothing else running beside it. Its record (`60_layer/decision_runs.json`, not in git) is now
of the verifier as it stands. **WebKit did not stall.** Every check passed on its last run. One needed a second run:
the exercise of the layer's first view in WebKit, where one action of the first run did not take. A drag of the map,
made by script, left the map where it was; the second run passed every action. That check had needed a second run
once before, on 8 October. The Safari application was not started: the record names the two checks that were not
run and gives the reason. The table below is the record.

**What followed from it.** The three documents written from those records were written again: `docs/RESULTS.md`,
`docs/LAYER.md` and `docs/DECISION_LAYER.md`. In `docs/RESULTS.md` the figures read from the records refreshed; each
is listed, old beside new, under Phase 8 below. `docs/GAP.md` was written again too, for one sentence (Step 5
above: the owner's sentence on outside-village land), and it was written last. Its last section gives the size and
SHA-256 of every file it read, among them the two documents on the layer and this log. In the commit of Step 5 it
had been written before those three, and so gave the size and SHA-256 of their earlier versions; no figure of its
text was affected. It now gives them as they are, and "To rebuild", at the end of this log, says to write it last.

**A gate was changed after it had passed, and this is that change.** The owner's instruction of 10 October says of
`docs/RESULTS.md` that figures other than those he named may refresh when the script reads the files of the day,
that this is expected, and that each is to be listed. The gate of Phase 8 on that document had allowed no figure to
differ but the time of writing, which held until this step. It now also allows a figure read from a record of the
browser checks, and a line of the text that differs only in such figures. It fails, as before, on any other figure
and on any other line. No other gate, expected value or tolerance was changed.
"""),
]


def mask(s) -> str:
    """A record of a browser check can carry the address a page was opened at, a path of the machine it ran on: the log names it from the repository."""
    return str(s).replace(str(ROOT), "<repository>")


def publication(folder: Path | None = None) -> list[str]:
    """The two records of the published copy: of the copy as it stands (`70_share/`), or, given a folder, the records kept there. A record of the first publication is of
    the branch `gh-pages`, and gives the commit at its head; a record made since the owner's handoff of 11 October 2026 ("One branch: main") is of the folder `site/` of `main`,
    and gives the commit at the head of `main` and the last commit to change `site/`. Either kind is read as it is."""
    pub, chk = (folder or ROOT / "70_share") / "pages_publication.json", (folder or ROOT / "70_share") / "pages_live_check.json"
    if not (pub.exists() and chk.exists()):
        return []
    p, c = json.loads(pub.read_text(encoding="utf-8")), json.loads(chk.read_text(encoding="utf-8"))
    if "site_commit" in p:
        where = [f"- deployed from the folder `{p['folder']}` of the branch `{p['branch']}`, by the workflow `{p['workflow']}`",
                 f"- the commit at the head of `{p['branch']}` when it was checked: `{p['main_commit_when_checked']}`; the last commit to change `{p['folder']}` at that head: `{p['site_commit']}`"]
    else:
        where = [f"- the commit at the head of `{p['branch']}` when it was checked: `{p['gh_pages_commit_when_checked']}`"]
    out = [f"- the site: {p['address']}"] + where + [
           f"- the copy: built {p['copy_built_utc']} from the layer built {p['layer_built_utc']}",
           f"- the check of the live site (`scripts/check_pages_live.py`, run {c['run_utc']}): {c['checks_passed']} of {c['checks_made']} checks passed", "",
           "| check | expected | found | pass |", "|---|---|---|---|"]
    out += [f"| {esc(x['check'])} | {esc(x['expected'])} | {esc(x['found'])} | {'yes' if x['pass'] else 'NO'} |" for x in c["checks"]]
    if folder is not None:
        return out + ["", f"*From the two records of that publication, `pages_publication.json` and `pages_live_check.json`, as they were kept in `{folder.relative_to(ROOT)}/` (working files, not in git) "
                          "before the copy was built again for the page's words.*", ""]
    return out + ["", "*From `70_share/pages_publication.json` and `70_share/pages_live_check.json`, which are not in git.*", ""]


def browser_runs(folder: Path | None = None, before: str = "for the page's words") -> list[str]:
    """The runner's own record of the checks of the layer, every run of each: of the layer as it stands (`60_layer/`), or, given a folder, the record kept there."""
    p = (folder or ROOT / "60_layer") / "decision_runs.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    where = "`60_layer/decision_runs.json`" if folder is None else f"`{folder.relative_to(ROOT)}/decision_runs.json` (the record of that pass, kept with the session's working files before the layer was built again {before})"
    out = [f"*{where}: started {d['started_utc']}, ended {d['ended_utc']}; the layer it checked was built {d['layer_run_utc']}; one check at a time.*", "",
           "| check | run | started | exit status | its last line | lines that failed |", "|---|---|---|---|---|---|"]
    for c in d["checks"]:
        for r in c["runs"]:
            out.append(f"| {esc(c['check'])} | {r['run']} | {r['started_utc']} | {r['exit']} | {esc(mask(r['last_line']))} | {esc(mask('; '.join(r['failed_lines'])) or 'none')} |")
    out += ["", "Not run in this pass: " + "; ".join(f"{x['check']} (\"{x['why']}\")" for x in d["checks_not_run_in_this_pass"]) + ".", "",
            f"*Every check passed on its last run: {'yes' if d['every_check_passed_on_its_last_run'] else 'NO'}; on its first run: "
            f"{'yes' if d['every_check_passed_on_its_first_run'] else 'no'}.*", ""]
    return out


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
                out += publication(KEPT_SHARE if (KEPT_SHARE / "pages_publication.json").exists() else None)
            if n == 1:
                out += rebuild("step1")
            if n == 2:
                out += forest_survey()
            if n == 5:
                out += rebuild("step5")
            if n == 6:
                out += browser_runs(KEPT_LAYER if (KEPT_LAYER / "decision_runs.json").exists() else None)
    return out


# The owner's second handoff of 11 October 2026: nine steps, 0 to 8. Typed, like the list of the first: a step is listed as done once its commit is made.
SECOND_STEPS = [
    (0, "keep what is live", True), (1, "the audit", True), (2, "the words, in the full layer", True), (3, "the copy", True), (4, "the checks", True),
    (5, "stage 4 follows the layer", True), (6, "look at it", True), (7, "the documents", STEP_7_DONE), (8, "publish, on the owner's word", STEP_8_DONE),
]
SECOND_STEP_5 = """
Stage 4 reads two files of the layer: `60_layer/data.js`, for the layer's own row of sources for the development index,
and `60_layer/layer_by_unit.csv`, for the class of Scheduled Tribe share the layer shows for a unit. Its records hold
the bytes and SHA-256 of those two and of `scripts/06_build_layer.py`. The rewording changed the first and the third.
The second, the table of figures, is byte for byte what it was (`docs/SITE_COPY.md`).

The verifier was run on the stage as it stood. It failed two checks and no other: the listing of inputs and the run
record still held the earlier bytes and SHA-256 of those two files. `scripts/08_gap_inputs.py` and
`scripts/08_build_gap_districts.py` were run again in the stage-4 environment, in that order. No other step's section
lists a file that those two runs changed, so no other step was run. **No table of figures moved**: the comparison
below sets every output beside the copy kept from before (`50_gap/before_site_words/`). The verifier then passed every
check. `scripts/08_gap_closing_checks.py` and `scripts/08_gap_leftovers_check.py` were not run again, as instructed:
their tables stay the record of the stage-4 run.

One script of the stage was changed: `scripts/08_gap_compare_builds.py` now names, for a record whose list of inputs
or outputs differs, the files whose entry differs, so that the list below says which input moved a record.
"""
SECOND_RUNS = """
The layer's checks were run again on the build with the new words, one at a time, with the two checks in the Safari
application left out as before. The table is the runner's record. A browser check that does not pass is run again,
and every run is kept. The two checks in WebKit needed more than one run: in the layer's own exercise the drag of the
map made by script left the map where it was, the step that had failed once on 8 October and once in Step 6 above; and
one run of the decision view's exercise ended on an error raised inside the map library. Nothing was keeping the
display awake during those runs; it was kept awake from then on, and each check then passed. Whether that was the
reason was not established. By the owner's ruling of 9 October the fragility of the WebKit checks is recorded and
not chased.
"""


SECOND_STEP_7 = """
The documents that describe the page were written again, each by its own script and in this order: `docs/RESULTS.md`
(by `scripts/write_results.py`, which was not changed), `docs/LAYER.md`, `docs/SITE_COPY.md` (new, by
`scripts/write_site_copy.py`), `docs/DECISION_LAYER.md`, this log, and `docs/GAP.md` last. `README.md` and
`docs/DEGRADATION.md` were edited by hand: their lines on NIRv in the owner's words, and in the README the rows of the
copy's builder and its gate, rows for the two new scripts, and the layer section.

**`docs/RESULTS.md`: no sentence was changed.** {results} The list under Phase 8 below,
`50_gap/results_md_changes.csv`, was written by `scripts/08_gap_closing_checks.py`, which was not run again: it stays
the record of the stage-4 run, and is of the document as that run left it.

**`docs/GAP.md` is written after this log, and last**, as "To rebuild" at the end of this log says. Its last section
gives the size and SHA-256 of every file it read, and this handoff changed several of them: the layer's two files, the
copy's three and its two records, the two documents on the layer, the layer's builder, two records of `50_gap/` (Step
5 above) and this log. A draft of it, written before this log, differed from the committed document in those lines,
in the time at which the tables of districts were made again and in the time of writing; and, being a draft, in the
lines that give what each verifier printed, which a draft does not run. It differed in no other line.
"""


def second_step_7() -> list[str]:
    """Step 7 of the second handoff: the documents. The counts are read from the list of the figures of docs/RESULTS.md that changed."""
    p = ROOT / "60_layer" / "site_copy_results_changes.json"
    if not (STEP_7_DONE and p.exists()):
        return []
    r = json.loads(p.read_text(encoding="utf-8"))
    results = (f"Of the {r['figures_in_the_text_now']} figures of its text, {r['figures_printed_differently']} are printed differently, {r['figures_gone']} are gone and {r['figures_added']} are new, "
               f"against the document of commit `{r['before_is_the_document_of_commit']}`; {r['lines_of_the_text_above_section_13_gone_or_changed']} lines of its text differ, each in those figures alone. "
               "They are listed, old beside new, in `docs/SITE_COPY.md` (its section on the documents), from `60_layer/site_copy_results_changes.json`.")
    if r["no_sentence_was_changed"] is not True:
        raise SystemExit("60_layer/site_copy_results_changes.json does not say that no sentence of docs/RESULTS.md was changed")
    return ["### Step 7 of the second handoff: the documents", "", SECOND_STEP_7.strip().format(results=results), ""]


def second_handoff() -> list[str]:
    """The owner's second handoff of 11 October 2026 (the page's words): its steps, and what of it bears on stage 4. Its account is docs/SITE_COPY.md."""
    if not (GAP / "gates_site_words.csv").exists():
        return []
    out = ["## The owner's second handoff of 11 October 2026: the page's words", "",
           "The same day the owner had the words of the map page rewritten in his own - a short label, and what it left out in a small \"i\" beside it - with every "
           "untrue line fixed and no figure moved (`.session_scratch_2026-10-05/handoff/2026-10-11_site_copy_and_audit.md` and the deck of words beside it, not in "
           "git). Its account is `docs/SITE_COPY.md`, written by `scripts/write_site_copy.py`: every finding, every string before and after, every check whose words "
           "changed, the runs, and what was seen. This log keeps what bears on stage 4 and on taking the work up again.", "",
           "| step | what | state |", "|---|---|---|"]
    third = (KEPT_SIX_LAYER / "decision_runs.json").exists()          # the third handoff has begun: the builds of this one were kept before its six lines
    out += [f"| {n} | {what} | {'done' if done else 'replaced by the third handoff, below' if n == 8 and third else 'not yet'} |" for n, what, done in SECOND_STEPS]
    out += ["", "### Step 5 of the second handoff: stage 4 follows the layer", "", SECOND_STEP_5.strip(), ""] + rebuild("site_words", KEPT_GAP_WORDS if third and (KEPT_GAP_WORDS / "gates_site_words.csv").exists() else None)
    runs = browser_runs(KEPT_SIX_LAYER, "for the owner's six lines") if third else browser_runs()
    if runs:
        out += ["### The layer's checks on the build with the new words", "", SECOND_RUNS.strip(), ""] + runs
    out += second_step_7()
    share = (KEPT_SIX_SHARE if third else ROOT / "70_share") / "share.provenance.json"
    if share.exists():
        made = json.loads(share.read_text(encoding="utf-8"))["run_utc"]
        out += ["### Step 8 of the second handoff: the copy on the site", ""]
        if third:
            out += [f"The work stopped at this step and waited for the owner's word, with the copy of this handoff (made {made}) ready and not published. His word came in his third handoff of the day, which "
                    "replaced the wait: its Step 0 was to publish that copy, and its Step 6 to publish the copy with his six lines. What became of each is in the section below.", ""]
        else:
            out += [f"**Not yet published.** The copy with the new words (made {made}) goes to the site on the owner's word. Until then the site serves the copy of Step 0 "
                    "above, and the two records in `70_share/` are that publication's, put back beside the new copy after it was built.", ""]
    return out


THIRD_STEP_3_DONE, THIRD_STEP_4_DONE, THIRD_STEP_5_DONE = True, True, True       # the THIRD handoff's steps 3, 4 and 5: each set when the step is done
THIRD_STEP_0 = """
**Not done.** The owner's yes to publishing was in this handoff, and its first step was to publish the build that was
waiting, the copy made {waiting}. The publish script (`.session_scratch_2026-10-05/handoff/publish_to_github_pages.sh`)
was not run: the session's permission gate refused the command as a production deploy before the script started, and
so before git was reached. Nothing was done to get round the refusal. As the handoff says of a Step 0 that fails, the
work went on to Step 1, and the site went on serving the copy of the first handoff's Step 0 (above).
"""
THIRD_STEP_1 = """
Six lines of the page that the audit of the second handoff had listed for the owner were untrue or misleading, and he
gave his words for each: the check that fails in the East Coast zone is this project's placebo test and not CoRE
Stack's own; Hansen does record loss on open land, and what it cannot see is thinning; the grid's column without loss
reads "little or no"; the prompt of a unit outside villages keeps its question and drops the claim; the Hansen row of
the sources says what was reconciled; and it is block rasters, not a dashboard, that take two classes from land-use
maps. Every other string is as it was. `docs/DECISION_LAYER.md` (its sections on the outside-village units and on what
changed that day) and `docs/SITE_COPY.md` (its section on the six lines) have each line, old beside new, and his ruling
on the prompt: the decision table keeps its sentence and is not rebuilt, the page shows the new words in its place, and
the builder stops unless the table's sentence is the old one.

**What this means for stage 4.** The decision table was not rebuilt, so no input of stage 4 from `55_decision/`
changed. The layer's two files that stage 4 reads did: `60_layer/data.js` holds the new words, and
`scripts/06_build_layer.py` wrote four of them. `60_layer/layer_by_unit.csv` is byte for byte what it was. Both builds
were kept as they stood before the six lines (`.session_scratch_2026-10-05/60_layer_2026-10-11_before_six_fixes/` and
`70_share_2026-10-11_before_six_fixes/`, working files, not in git).
"""
THIRD_STEP_2 = """
The checks that pin the six lines were changed to follow them, committed, and then run, one at a time. No expected
number, count or tolerance was changed and no check was taken out. `scripts/check_site_copy.py` gained a group that
holds each build against the one kept before the six lines: the strings that differ are the six lines, each by
exactly the owner's replacement, and nothing else differs. `docs/SITE_COPY.md` has the counts, the planted errors and
every changed block of a check. The table below is the runner's record of the layer's checks on the build with the
six lines; the two checks in the Safari application were left out as before.
"""
THIRD_STEP_3 = """
The same step as Step 5 of the second handoff, for the same reason: the records of stage 4 hold the bytes and SHA-256
of `60_layer/data.js` and of `scripts/06_build_layer.py`, and the six lines changed both. The verifier was run on the
stage as it stood; `scripts/08_gap_inputs.py` and `scripts/08_build_gap_districts.py` were run again in the stage-4
environment, in that order, and no other step; the verifier was run again. `scripts/08_gap_closing_checks.py` and
`scripts/08_gap_leftovers_check.py` were not run again. **No table of figures moved.** The comparison below is written
under the names the second handoff's comparison had (`50_gap/gates_site_words.csv` and
`50_gap/rebuild_site_words_differences.csv`), as the owner asked, and sets every output beside the same copy as then,
the one kept before the page's words were first rewritten (`50_gap/before_site_words/`): so it covers both rebuilds.
"""
THIRD_STEP_4 = """
The pictures of both builds were taken again, with four more of each build at the largest size: a ranked list with an
East Coast badge in view, the prompt of a unit outside villages, the comparison section's "i" in the panel of an East
Coast unit, and the grid of "why this tier". Each was compared, byte for byte, with the picture kept from before the
six lines; a picture that differs, or is new, was opened and looked at again. `docs/SITE_COPY.md` has the note on
each.
"""
THIRD_STEP_5 = """
Written again, each by its own script and in this order: `docs/RESULTS.md` (no sentence changed; the figures that are
printed differently are listed in `docs/SITE_COPY.md`), `docs/LAYER.md`, `docs/SITE_COPY.md`, `docs/DECISION_LAYER.md`
(with the owner's ruling on the prompt, dated), this log, and `docs/GAP.md` last.
"""


def third_handoff() -> list[str]:
    """The owner's third handoff of 11 October 2026 (publish what is waiting; six lines of the page in his words; publish again): its steps, and what of it bears on stage 4."""
    if not (KEPT_SIX_LAYER / "decision_runs.json").exists():
        return []
    share, check = ROOT / "70_share" / "share.provenance.json", ROOT / "70_share" / "pages_live_check.json"
    made = json.loads(share.read_text(encoding="utf-8"))["run_utc"] if share.exists() else ""
    live = json.loads(check.read_text(encoding="utf-8")) if check.exists() else {}
    published = bool(made) and live.get("copy_run_utc") == made and live.get("passed") is True
    waiting = json.loads((KEPT_SIX_SHARE / "share.provenance.json").read_text(encoding="utf-8"))["run_utc"]
    stage4 = THIRD_STEP_3_DONE and (GAP / "gates_site_words.csv").exists() and (KEPT_GAP_WORDS / "gates_site_words.csv").exists()
    steps = [(0, "publish the build that is waiting", "not done: the publish script was refused before it ran (below)"), (1, "the six fixes", "done"), (2, "the checks", "done"),
             (3, "stage 4 follows the layer", "done" if stage4 else "not yet"), (4, "look at it", "done" if THIRD_STEP_4_DONE else "not yet"), (5, "the documents", "done" if THIRD_STEP_5_DONE else "not yet"),
             (6, "publish, and write what the site serves", "done" if published else "not yet")]
    out = ["## The owner's third handoff of 11 October 2026: publish what is waiting, six lines, publish again", "",
           "Later the same day the owner gave his yes to publishing, in a third note (`.session_scratch_2026-10-05/handoff/2026-10-11_six_fixes_and_publish.md`, not in git), which replaced the wait at Step 8 of the "
           "second handoff. It set seven steps: publish the build that was waiting; then put six lines of the page right, in his words; then check, look, write the documents and publish again.", "",
           "| step | what | state |", "|---|---|---|"]
    out += [f"| {n} | {what} | {state} |" for n, what, state in steps]
    out += ["", "### Step 0 of the third handoff: publish the build that was waiting", "", THIRD_STEP_0.strip().format(waiting=waiting), "",
            "### Step 1 of the third handoff: the six lines", "", THIRD_STEP_1.strip(), "", "### Step 2 of the third handoff: the checks", "", THIRD_STEP_2.strip(), ""] + browser_runs()
    if stage4:
        out += ["### Step 3 of the third handoff: stage 4 follows the layer", "", THIRD_STEP_3.strip(), ""] + rebuild("site_words")
    if THIRD_STEP_4_DONE:
        out += ["### Step 4 of the third handoff: look at it", "", THIRD_STEP_4.strip(), ""]
    if THIRD_STEP_5_DONE:
        out += ["### Step 5 of the third handoff: the documents", "", THIRD_STEP_5.strip(), ""]
    out += ["### Step 6 of the third handoff: the copy on the site", ""]
    if published:
        out += [f"The copy with the six lines (made {made}) was published by the owner's own script, on his word, and the live site was checked against it:", ""] + publication()
    else:
        out += [f"**Not yet published.** The copy with the six lines (made {made}) is built, checked and ready. The publish script was tried once more at this step, on the owner's word given in this handoff, and "
                "was refused by the session's permission gate before it ran, as at Step 0. Nothing was done to get round the refusal. Until the owner runs the script himself, or allows it, the site serves the copy of "
                "the first handoff's Step 0, and the two records in `70_share/` are that publication's, put back beside the new copy after it was built.", "",
                "What is left once it is published, in this order: `scripts/check_pages_live.py --wait 10`; `scripts/write_decision_layer.py`, which then says that the site serves this copy; this log, with "
                "`STEP_8_DONE` set; and `scripts/write_gap.py` last.", ""]
    return out


def rebuild(name: str, folder: Path | None = None) -> list[str]:
    """A rebuild set against the build kept from before it: the gates of `scripts/08_gap_compare_builds.py`, and every file that differs. Given a folder, the two tables as they were kept there."""
    gates, diff = (folder or GAP) / f"gates_{name}.csv", (folder or GAP) / f"rebuild_{name}_differences.csv"
    if not (gates.exists() and diff.exists()):
        return []
    out = ["**The rebuild against the build before it.**", ""] + gate_table(gates) + [""]
    if folder is not None:
        out += [f"*The two tables are read as they were kept in `{folder.relative_to(ROOT)}/` (working files, not in git) before the same two steps were run once more in the third handoff, which wrote them again under the same names.*", ""]
    r = rows(diff)
    some = [x for x in r if x["same_bytes"] != "yes"]
    out += [f"Files compared or listed: {len(r)}; byte for byte the same: {sum(x['same_bytes'] == 'yes' for x in r)}. Every file that differs, is new or is gone "
            f"(`50_gap/rebuild_{name}_differences.csv`):", "", "| file | kind | what differs | why |", "|---|---|---|---|"]
    out += [f"| `{esc(x['file'])}` | {esc(x['kind'])} | {esc(x['what_differs'])} | {esc(x['why'])} |" for x in some]
    return out + [""]


def forest_survey() -> list[str]:
    """Phase 5b: its gates, and its four rank correlations as the table gives them."""
    gates, summ = GAP / "gates_phase5b.csv", GAP / "fsi_summary.csv"
    if not (gates.exists() and summ.exists()):
        return []
    out = ["**Gates of Phase 5b.**", ""] + gate_table(gates) + [""]
    sec = (json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8"))["steps"]).get("08_build_gap_fsi")
    if sec:
        out += [f"Files written by `{sec['script']}` (run {sec['run_utc']}):", ""]
        out += [f"- `{name}` ({meta['bytes']:,} bytes, sha256 `{meta['sha256'][:16]}`)" for name, meta in sec["outputs"].items()] + [""]
    out += ["**The four rank correlations** (`50_gap/fsi_summary.csv`; 30 districts in each):", "",
           "| id | what | Spearman's rho | 95 % bootstrap interval | permutation p (five decimals) | size taken out of both sides |", "|---|---|---|---|---|---|"]
    out += [f"| {x['id']} | {esc(x['what'])} | {x['rho']} | {x['ci95_lo']} to {x['ci95_hi']} | {float(x['p_permutation']):.5f} | {x['size_free']} |" for x in rows(summ)]
    return out + [""]


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
           "| error planted | kind | table damaged | parts of the verifier run | checks failed, of those run | of them, naming no digest | caught |",
           "|---|---|---|---|---|---|---|"]
    for x in t["trials"]:
        out.append(f"| {esc(x['name'])} | {esc(x['kind'])} | {', '.join('`' + y + '`' for y in x['tables'])} | "
                   f"{', '.join(x['parts_run'])} | {x['checks_failed']} of {x['checks_run']} | {x['checks_failed_that_name_no_digest']} | {'yes' if x['caught'] else 'NO'} |")
    out += ["", f"*{sum(x['caught'] for x in t['trials'])} of {len(t['trials'])} errors caught; tables damaged: "
            f"{len({y for x in t['trials'] for y in x['tables']})}.*", ""]
    return out


def reviews() -> list[str]:
    """The one review round of the verifier's parts, from the record made of the agents' own reports."""
    p = GAP / "verify_gap_reviews.json"
    if not p.exists():
        return []
    v = json.loads(p.read_text(encoding="utf-8"))
    t = v["totals"]
    out = ["### The review round", "",
           f"*From `50_gap/verify_gap_reviews.json` (written {v['written_utc']}): each agent's own report, as the journal of the round holds it. "
           "\"Checks\" are those of the part as the agent left it, run on the real tables.*", "",
           "| agent | part | what it did | checks passed | errors planted | caught by the part as left | disagreements | readings assumed | things listed as not covered | weak checks found and mended |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in v["reports"]:
        out.append(f"| {esc(r['agent'])} | {', '.join(r['parts'])} | {esc(r['role'])} | {r['checks_passed']} of {r['checks']} | {r['errors_planted']} | {r['errors_caught']} | "
                   f"{len(r['disagreements'])} | {len(r['assumptions'])} | {len(r['uncovered'])} | {len(r['weak_checks_found_and_fixed'])} |")
    out += ["", f"*{t['agents_that_reported_on_a_part']} agents reported; {t['checks_passed']} of {t['checks']} checks passed; {t['errors_caught']} of {t['errors_planted']} planted errors "
            f"caught by the parts as the agents left them; {t['disagreements']} disagreements, {t['assumptions']} readings assumed, {t['uncovered']} things listed as not covered, "
            f"{t['weak_checks_found_and_fixed']} weak checks found and mended. Parts written by agents: {', '.join(v['parts_written_by_agents'])}; by the session: "
            f"{', '.join(v['parts_written_by_the_session'])}.*", ""]
    rd = v.get("reader")
    if v["reader_reported"] and rd:
        out += [f"**The reader across all parts reported**: {len(rd['uncovered'])} columns or keys that no check reads or that a check reads only in part, "
                f"{len(rd['names_that_claim_more_than_the_code_tests'])} checks whose name claims more than the code tests, and "
                f"{len(rd['names_defined_in_two_parts'])} names defined in two pieces of the script.", ""]
    else:
        out += ["**The reader across all parts did not report.**", ""]
    changed = v["pieces_changed_after_the_round"]
    out += [f"**Pieces of the script changed after the round, by the session: {len(changed)} of {len(v['pieces'])}.** `{v['verifier']}` (sha256 `{v['verifier_sha256'][:16]}`) is the "
            "pieces below, joined.", "", "| piece | sha256 as the round left it | sha256 as assembled | changed after the round |", "|---|---|---|---|"]
    out += [f"| `{n}` | `{x['sha256_as_the_round_left_it'][:16]}` | `{x['sha256_as_assembled'][:16]}` | {'**yes**' if x['changed_after_the_round'] else 'no'} |" for n, x in v["pieces"].items()]
    return out + [""]


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
    r = subprocess.run(["git", "log", "--first-parent", "--format=%h %s", "16b1efd..HEAD"], capture_output=True, text=True, cwd=ROOT)      # this history's own line: without --first-parent the two commits that main held before the join of 11 October 2026 would be listed too
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
        doc += handoff() + second_handoff() + third_handoff()
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
            doc += reviews() + trials()
            after = rebuild("step3")
            if after:
                doc += ["### The rebuild after the review", ""] + after
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
            "$PY scripts/08_build_gap_fsi.py          # Phase 5b",
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
            "A script named above that does not exist yet belongs to a phase that has not been reached.", "",
            "`scripts/write_gap.py` is run once more after the last of these. The last section of `docs/GAP.md` records the size and "
            "SHA-256 of every file it read, and three of them are written after it: `docs/DECISION_LAYER.md`, `docs/LAYER.md` and this "
            "log. `docs/LAYER.md` is written by a working script of the sessions that made the layer, "
            "`.session_scratch_2026-10-05/make_layer_md.py`, which is not in git.", ""]
    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(done)} phase(s), {len(doc)} lines")


if __name__ == "__main__":
    sys.exit(main())
