# Stage 4: the run log

*Written 2026-10-11T13:58:43Z by `scripts/write_stage4_run_log.py`. The gate tables, the lists of files and the package versions are read from the files named beside them; the notes are typed and carry no figure of the analysis. The owner's prompt of 10 October 2026 set nine phases, 0 to 8, each ending in a commit.*

## Where the run stands

Phases written up below: 0, 1, 2, 3, 4, 5, 6, 7, 8. The last is Phase 8, docs. Every gate of every phase listed passed.

The stage outputs (`50_gap/`, `figures/stage4/`) are not in git. If they are missing, rebuild them: the section "To rebuild" at the end gives the order.

## The owner's handoff of 11 October 2026

The run was taken up again on 11 October 2026 under a note from the owner (`.session_scratch_2026-10-05/handoff/2026-10-11_finish_stage4.md`, not in git). It ruled on what was open (one round of review of the verifier's parts and no more; `docs/LAYER.md` to be written again; H9 stays, as a sensitivity; `scripts/layer_overlay.json` stays as it is) and set seven steps. Each ends in a commit.

| step | what | state |
|---|---|---|
| 0 | publish the shared copy to GitHub Pages | done |
| 1 | fix the input listing and rebuild | done |
| 2 | Phase 5b: the need read against the Forest Survey's own figures | done |
| 3 | finish Phase 6 | done |
| 4 | Phase 7 | done |
| 5 | Phase 8, with the additions to the account of the stage | done |
| 6 | the decision view in WebKit, with the machine awake | done |

### Step 0: publish the shared copy to GitHub Pages

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

- the site: https://sudo-karan.github.io/ICTD_Project/
- the commit at the head of `gh-pages` when it was checked: `907d0f905b3338c81c4bba00c2be5de0de3082d3`
- the copy: built 2026-10-10T20:05:42Z from the layer built 2026-10-09T04:08:22Z
- the check of the live site (`scripts/check_pages_live.py`, run 2026-10-10T20:09:31Z): 9 of 9 checks passed

| check | expected | found | pass |
|---|---|---|---|
| the copy on disk is the build its provenance record describes (bytes and SHA-256 of its three files) | 3 of 3 | 3 of 3 | yes |
| https://sudo-karan.github.io/ICTD_Project/index.html: the bytes and SHA-256 the site serves are those the provenance record gives for index.html | 205691 bytes, sha256 508144e070577a5e | HTTP 200; 205691 bytes, sha256 508144e070577a5e | yes |
| https://sudo-karan.github.io/ICTD_Project/data.js: the bytes and SHA-256 the site serves are those the provenance record gives for data.js | 22066227 bytes, sha256 4df21a9f2c43845a | HTTP 200; 22066227 bytes, sha256 4df21a9f2c43845a | yes |
| https://sudo-karan.github.io/ICTD_Project/README.txt: the bytes and SHA-256 the site serves are those the provenance record gives for README.txt | 7390 bytes, sha256 8cf3242e8c5978ad | HTTP 200; 7390 bytes, sha256 8cf3242e8c5978ad | yes |
| https://sudo-karan.github.io/ICTD_Project/ opened in headless Chrome and became ready | ready | ready after 9.1 s, in Chrome/154.0.8037.99 | yes |
| units in the page's data, and units drawn on the map | 11468 and 11468 | 11468 and 11468 | yes |
| script errors the page logged (exceptions, console errors and warnings) | 0 | 0 | yes |
| errors in the browser's own log, against the addresses asked for that the site answers with 404 (a browser asks every site for /favicon.ico by itself; the site has none) | none but one 'Failed to load resource' for each favicon.ico the site does not have | 1 line(s): log: Failed to load resource: the server responded with a status of 404 (); answered 404: https://sudo-karan.github.io/favicon.ico | yes |
| requests the page made over http or https, and those of them that did not go to https://sudo-karan.github.io | at least one, and none elsewhere | 3 (/ICTD_Project/, /ICTD_Project/data.js, /favicon.ico); elsewhere: 0 | yes |

*From the two records of that publication, `pages_publication.json` and `pages_live_check.json`, as they were kept in `.session_scratch_2026-10-05/70_share_2026-10-11_before_words/` (working files, not in git) before the copy was built again for the page's words.*

### Step 1: fix the input listing and rebuild

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

**The rebuild against the build before it.**

| gate | expected | found | pass |
|---|---|---|---|
| tables of figures in both builds (50_gap/before_step1/ and 50_gap/) with a cell, a column or a number of rows that differs | none | none (of 20 tables compared) | yes |
| tables of figures of the earlier build that are gone | none | none | yes |
| tables of figures that are byte for byte what they were | 20 of 20 | 20 of 20 | yes |
| files that differ and are not among those expected to (a record with a time or a hash, a listing, a text file with its time) | none | none | yes |
| gates of the build now that did not pass (every gate table of 50_gap/) | none | none | yes |

*5 of 5 gates passed (`50_gap/gates_step1.csv`).*

Files compared or listed: 43; byte for byte the same: 38. Every file that differs, is new or is gone (`50_gap/rebuild_step1_differences.csv`):

| file | kind | what differs | why |
|---|---|---|---|
| `forest_villages_pdf_record.json` | record | keys that differ: checked_utc | the record carries the time of the check |
| `gap.provenance.json` | record | steps that differ, and in which keys - 08_build_gap_deck_tables: run_utc, shared_module_sha256; 08_build_gap_districts: inputs, run_utc, script_sha256, shared_module_sha256; 08_build_gap_panel: outputs, run_utc, shared_module_sha256; 08_build_gap_rights: forest_villages, outputs, run_utc, script_sha256, shared_module_sha256; 08_build_gap_units: outputs, run_utc, shared_module_sha256; 08_gap_environment: inputs, run_utc, script_sha256, shared_module_sha256; 08_gap_inputs: inputs, outputs, run_utc, script_sha256, shared_module_sha256 | every step was run again: the record carries each run's time and the SHA-256 of the script, of the shared module and of every input and output |
| `inputs_listing.json` | record | keys that differ: inputs, run_utc (inputs: 21 then, 34 now) | the listing of inputs, with the time it was written; it holds more inputs wherever the list of inputs grew |
| `panel_models.txt` | text | 1 line(s) of 29: line 1 first | its first line carries the time it was written |
| `unit_history_models.txt` | text | 1 line(s) of 51: line 1 first | its first line carries the time it was written |

### Step 2: Phase 5b: the need read against the Forest Survey's own figures

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

**Gates of Phase 5b.**

| gate | expected | found | pass |
|---|---|---|---|
| district rows read under Table 10.20.3 of the Forest Survey's report | 30 | 30 | yes |
| names of the table that are not a census name of the repository: the owner's five and no others | Angul, Baleswar, Deogarh, Jagatsinghpur, Nabarangpur | Angul, Baleswar, Deogarh, Jagatsinghpur, Nabarangpur | yes |
| the table's rows against the 30 census districts: matched one to one | 30, each code once | 30, each code once: yes | yes |
| the five spelling rules, as the owner gave them: Angul 384, Baleswar 377, Deogarh 373, Jagatsinghpur 380, Nabarangpur 397 | each name on its code | Deogarh 373; Baleswar 377; Jagatsinghpur 380; Angul 384; Nabarangpur 397 | yes |
| fsi_calculated_area_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 155707 | sum 155707; printed 155707 | yes |
| fsi_very_dense_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 7224.42 | sum 7224.42; printed 7224.42 | yes |
| fsi_moderately_dense_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 21065.55 | sum 21065.55; printed 21065.55 | yes |
| fsi_open_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 24143.59 | sum 24143.59; printed 24143.59 | yes |
| fsi_forest_cover_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 52433.56 | sum 52433.56; printed 52433.56 | yes |
| fsi_change_wrt_2021_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 151.89 | sum 151.89; printed 151.89 | yes |
| fsi_scrub_km2: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it | 4632.68 | sum 4632.68; printed 4632.68 | yes |
| districts whose very dense, moderately dense and open forest add to their total forest cover | 30 of 30 | 30 of 30 | yes |
| districts whose printed per cent is 100 x total forest cover / calculated area, to two decimals; and the Grand Total's | 30 of 30; and yes | 30 of 30; yes | yes |
| N1 of the state in this table against the table of districts (hectares) | 89657.2513 | 89657.2513 | yes |
| rank correlations computed (N1 against change and against scrub; and the same two with size taken out of both sides) | 4 | 4 | yes |

*15 of 15 gates passed (`50_gap/gates_phase5b.csv`).*

Files written by `scripts/08_build_gap_fsi.py` (run 2026-10-10T21:47:51Z):

- `50_gap/fsi_district_check.csv` (4,676 bytes, sha256 `bf01bd9e191dcb8c`)
- `50_gap/fsi_summary.csv` (2,210 bytes, sha256 `2f2e621f9e30fc1d`)
- `50_gap/gates_phase5b.csv` (2,270 bytes, sha256 `abacddb86066d298`)

**The four rank correlations** (`50_gap/fsi_summary.csv`; 30 districts in each):

| id | what | Spearman's rho | 95 % bootstrap interval | permutation p (five decimals) | size taken out of both sides |
|---|---|---|---|---|---|
| a | N1 of 2018-2025 (ha) against the Forest Survey's change in forest cover with respect to 2021 (km2) | -0.197325 | -0.539069 to 0.216689 | 0.29484 | no |
| b | N1 of 2018-2025 (ha) against the Forest Survey's scrub (km2) | 0.813247 | 0.59774 to 0.917498 | 0.00001 | no |
| c | N1 per 100 ha of forest at the start of 2018 against the Forest Survey's change as a per cent of its forest cover | -0.212041 | -0.541393 to 0.195843 | 0.25816 | yes |
| d | N1 per 100 ha of forest at the start of 2018 against the Forest Survey's scrub as a per cent of its forest cover | 0.578661 | 0.266942 to 0.789925 | 0.00094 | yes |

### Step 3: finish Phase 6

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

### Step 4: Phase 7

The three deck tables and the six figures were made again, after the verifier had passed, from the tables it checked.
The six images are byte for byte the images that were opened and looked at on 10 October 2026, so none had to be
looked at again, and the record of that look stands. No figure was added. The gates of Phase 7 pass; they are under
Phase 7 below, with the notes on how the figure rules are held and what was changed after the figures were first
looked at.

### Step 5: Phase 8, with the additions to the account of the stage

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

**The rebuild against the build before it.**

| gate | expected | found | pass |
|---|---|---|---|
| tables of figures in both builds (50_gap/before_step5/ and 50_gap/) with a cell, a column or a number of rows that differs | none | none (of 22 tables compared) | yes |
| tables of figures of the earlier build that are gone | none | none | yes |
| tables of figures that are byte for byte what they were | 22 of 22 | 22 of 22 | yes |
| files that differ and are not among those expected to (a record with a time or a hash, a listing, a text file with its time) | none | none | yes |
| gates of the later build that did not pass (every gate table of 50_gap/) | none | none | yes |

*5 of 5 gates passed (`50_gap/gates_step5.csv`).*

Files compared or listed: 53; byte for byte the same: 48. Every file that differs, is new or is gone (`50_gap/rebuild_step5_differences.csv`):

| file | kind | what differs | why |
|---|---|---|---|
| `forest_villages_pdf_record.json` | record | keys that differ: checked_utc | the record carries the time of the check |
| `gap.provenance.json` | record | steps that differ, and in which keys - 08_build_gap_rights: forest_villages, inputs, outputs, run_utc; 08_gap_inputs: inputs, outputs, run_utc | a step that is run again is recorded anew: the record carries each run's time and the SHA-256 of the script, of the shared module and of every input and output |
| `gates_step3.csv` | gate table | 5 cell(s): row 1, gate: 'tables of figures in both buil' then, 'tables of figures in both buil' now; row 1, found: 'none (of 23 tables compared)' then, 'none (of 22 tables compared)' now; row 3, expected: '23 of 23' then, '22 of 22' now | a gate table: see the gate on the gates below |
| `inputs_listing.json` | record | keys that differ: inputs, run_utc (inputs: 34 then, 34 now) | the listing of inputs, with the time it was written; it holds more inputs wherever the list of inputs grew |
| `rebuild_step3_differences.csv` | list of differences | its number of rows: 48 then, 51 now | a list this script writes: it differs when a comparison is made again |

### Step 6: the decision view in WebKit, with the machine awake

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

*`.session_scratch_2026-10-05/60_layer_2026-10-11_before_words/decision_runs.json` (the record of that pass, kept with the session's working files before the layer was built again for the page's words): started 2026-10-10T22:41:56Z, ended 2026-10-10T23:02:56Z; the layer it checked was built 2026-10-09T04:08:22Z; one check at a time.*

| check | run | started | exit status | its last line | lines that failed |
|---|---|---|---|---|---|
| verify_layer | 1 | 2026-10-10T22:41:56Z | 0 | 92 of 92 checks passed; n = 11,468 units, 44 fields a unit, 18 class arrays | none |
| verify_decision | 1 | 2026-10-10T22:42:04Z | 0 | 62 of 62 checks passed; n = 11,468 units, 4 windows, 6 cells, 30 districts | none |
| exercise_layer in Chrome | 1 | 2026-10-10T22:42:13Z | 0 | 53 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | none |
| exercise_layer in WebKit | 1 | 2026-10-10T22:45:59Z | 1 | 52 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | FAIL  [map] dragged the map 180 px left and 120 px up (mouse-down, eight mouse-moves and mouse-up, made in script) -> its centre moved from 20.205 N 84.440 E to 20.205 N 84.440 E, and the unit that was open stayed open |
| exercise_layer in WebKit | 2 | 2026-10-10T22:50:07Z | 0 | 53 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | none |
| exercise_decision in Chrome | 1 | 2026-10-10T22:54:12Z | 0 | 53 of 53 steps did what they should; 46 units opened on the map (46 as aimed, 0 touching the one aimed at; 0 clicks opened nothing); 874 of 874 lines of 'why this tier' are as the tables give them; exports: 6432 of 6432 cells; 14560 of 14560 cells; script errors: none | none |
| exercise_decision in WebKit | 1 | 2026-10-10T22:58:40Z | 0 | 47 of 47 steps did what they should; 46 units opened on the map (46 as aimed, 0 touching the one aimed at; 0 clicks opened nothing); 874 of 874 lines of 'why this tier' are as the tables give them; exports: 6432 of 6432 cells; 14560 of 14560 cells; script errors: none | none |

Not run in this pass: exercise_layer_safari, as written ("the owner's handoff of 11 October 2026: Chrome and WebKit only; the Safari application is not to be started"); exercise_decision_safari, by address ("the owner's handoff of 11 October 2026: Chrome and WebKit only; the Safari application is not to be started").

*Every check passed on its last run: yes; on its first run: no.*

## The owner's second handoff of 11 October 2026: the page's words

The same day the owner had the words of the map page rewritten in his own - a short label, and what it left out in a small "i" beside it - with every untrue line fixed and no figure moved (`.session_scratch_2026-10-05/handoff/2026-10-11_site_copy_and_audit.md` and the deck of words beside it, not in git). Its account is `docs/SITE_COPY.md`, written by `scripts/write_site_copy.py`: every finding, every string before and after, every check whose words changed, the runs, and what was seen. This log keeps what bears on stage 4 and on taking the work up again.

| step | what | state |
|---|---|---|
| 0 | keep what is live | done |
| 1 | the audit | done |
| 2 | the words, in the full layer | done |
| 3 | the copy | done |
| 4 | the checks | done |
| 5 | stage 4 follows the layer | done |
| 6 | look at it | done |
| 7 | the documents | done |
| 8 | publish, on the owner's word | not yet |

### Step 5 of the second handoff: stage 4 follows the layer

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

**The rebuild against the build before it.**

| gate | expected | found | pass |
|---|---|---|---|
| tables of figures in both builds (50_gap/before_site_words/ and 50_gap/) with a cell, a column or a number of rows that differs | none | none (of 22 tables compared) | yes |
| tables of figures of the earlier build that are gone | none | none | yes |
| tables of figures that are byte for byte what they were | 22 of 22 | 22 of 22 | yes |
| files that differ and are not among those expected to (a record with a time or a hash, a listing, a text file with its time) | none | none | yes |
| gates of the later build that did not pass (every gate table of 50_gap/) | none | none | yes |

*5 of 5 gates passed (`50_gap/gates_site_words.csv`).*

Files compared or listed: 57; byte for byte the same: 55. Every file that differs, is new or is gone (`50_gap/rebuild_site_words_differences.csv`):

| file | kind | what differs | why |
|---|---|---|---|
| `gap.provenance.json` | record | steps that differ, and in which keys - 08_build_gap_districts: inputs (60_layer/data.js, scripts/06_build_layer.py), run_utc; 08_gap_inputs: inputs (60_layer/data.js, scripts/06_build_layer.py), outputs (50_gap/inputs_listing.json), run_utc | a step that is run again is recorded anew: the record carries each run's time and the SHA-256 of the script, of the shared module and of every input and output |
| `inputs_listing.json` | record | keys that differ: inputs, run_utc (inputs: 34 then, 34 now; the entries that differ: (60_layer/data.js, scripts/06_build_layer.py)) | the listing of inputs, with the time it was written; it holds more inputs wherever the list of inputs grew |

### The layer's checks on the build with the new words

The layer's checks were run again on the build with the new words, one at a time, with the two checks in the Safari
application left out as before. The table is the runner's record. A browser check that does not pass is run again,
and every run is kept. The two checks in WebKit needed more than one run: in the layer's own exercise the drag of the
map made by script left the map where it was, the step that had failed once on 8 October and once in Step 6 above; and
one run of the decision view's exercise ended on an error raised inside the map library. Nothing was keeping the
display awake during those runs; it was kept awake from then on, and each check then passed. Whether that was the
reason was not established. By the owner's ruling of 9 October the fragility of the WebKit checks is recorded and
not chased.

*`60_layer/decision_runs.json`: started 2026-10-11T11:37:13Z, ended 2026-10-11T12:06:32Z; the layer it checked was built 2026-10-11T11:35:41Z; one check at a time.*

| check | run | started | exit status | its last line | lines that failed |
|---|---|---|---|---|---|
| verify_layer | 1 | 2026-10-11T11:37:13Z | 0 | 92 of 92 checks passed; n = 11,468 units, 44 fields a unit, 18 class arrays | none |
| verify_decision | 1 | 2026-10-11T11:37:21Z | 0 | 62 of 62 checks passed; n = 11,468 units, 4 windows, 6 cells, 30 districts | none |
| exercise_layer in Chrome | 1 | 2026-10-11T11:37:31Z | 0 | 53 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | none |
| exercise_layer in WebKit | 1 | 2026-10-11T11:41:31Z | 1 | 52 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | FAIL  [map] dragged the map 180 px left and 120 px up (mouse-down, eight mouse-moves and mouse-up, made in script) -> its centre moved from 20.205 N 84.440 E to 20.205 N 84.440 E, and the unit that was open stayed open |
| exercise_layer in WebKit | 2 | 2026-10-11T11:45:40Z | 1 | 52 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | FAIL  [map] dragged the map 180 px left and 120 px up (mouse-down, eight mouse-moves and mouse-up, made in script) -> its centre moved from 20.205 N 84.440 E to 20.205 N 84.440 E, and the unit that was open stayed open |
| exercise_layer in WebKit | 3 | 2026-10-11T11:49:48Z | 0 | 53 of 53 control actions did what they should; 29 units clicked on the map (0 clicks landed on a neighbour, which was then the unit compared); 1276 of 1276 displayed values equal the stage tables; script errors: none | none |
| exercise_decision in Chrome | 1 | 2026-10-11T11:53:54Z | 0 | 53 of 53 steps did what they should; 46 units opened on the map (46 as aimed, 0 touching the one aimed at; 0 clicks opened nothing); 874 of 874 lines of 'why this tier' are as the tables give them; exports: 6432 of 6432 cells; 14560 of 14560 cells; script errors: none | none |
| exercise_decision in WebKit | 1 | 2026-10-11T11:58:44Z | 1 | RuntimeError: js: Error Domain=WKErrorDomain Code=4 "A JavaScript exception occurred" UserInfo={WKJavaScriptExceptionLineNumber=789, WKJavaScriptExceptionMessage=TypeError: undefined is not an object (evaluating 'r._code'), WKJavaScriptExceptionColumnNumber=62360, WKJavaScriptExceptionSourceURL=file://<repository>/60_layer/index.html, NSLocalizedDescription=A JavaScript exception occurred} | none |
| exercise_decision in WebKit | 2 | 2026-10-11T12:02:05Z | 0 | 47 of 47 steps did what they should; 46 units opened on the map (46 as aimed, 0 touching the one aimed at; 0 clicks opened nothing); 874 of 874 lines of 'why this tier' are as the tables give them; exports: 6432 of 6432 cells; 14560 of 14560 cells; script errors: none | none |

Not run in this pass: exercise_layer_safari, as written ("the owner's ruling of 9 October 2026: no run in the Safari application in a batch applying his rulings; this batch changes the page's words"); exercise_decision_safari, by address ("the owner's ruling of 9 October 2026: no run in the Safari application in a batch applying his rulings; this batch changes the page's words").

*Every check passed on its last run: yes; on its first run: no.*

### Step 7 of the second handoff: the documents

The documents that describe the page were written again, each by its own script and in this order: `docs/RESULTS.md`
(by `scripts/write_results.py`, which was not changed), `docs/LAYER.md`, `docs/SITE_COPY.md` (new, by
`scripts/write_site_copy.py`), `docs/DECISION_LAYER.md`, this log, and `docs/GAP.md` last. `README.md` and
`docs/DEGRADATION.md` were edited by hand: their lines on NIRv in the owner's words, and in the README the rows of the
copy's builder and its gate, rows for the two new scripts, and the layer section.

**`docs/RESULTS.md`: no sentence was changed.** Of the 272 figures of its text, 4 are printed differently, 0 are gone and 0 are new, against the document of commit `27aea62`; 5 lines of its text differ, each in those figures alone. They are listed, old beside new, in `docs/SITE_COPY.md` (its section on the documents), from `60_layer/site_copy_results_changes.json`. The list under Phase 8 below,
`50_gap/results_md_changes.csv`, was written by `scripts/08_gap_closing_checks.py`, which was not run again: it stays
the record of the stage-4 run, and is of the document as that run left it.

**`docs/GAP.md` is written after this log, and last**, as "To rebuild" at the end of this log says. Its last section
gives the size and SHA-256 of every file it read, and this handoff changed several of them: the layer's two files, the
copy's three and its two records, the two documents on the layer, the layer's builder, two records of `50_gap/` (Step
5 above) and this log. A draft of it, written before this log, differed from the committed document in those lines,
in the time at which the tables of districts were made again and in the time of writing; and, being a draft, in the
lines that give what each verifier printed, which a draft does not run. It differed in no other line.

### Step 8 of the second handoff: the copy on the site

**Not yet published.** The copy with the new words (made 2026-10-11T12:32:18Z) goes to the site on the owner's word. Until then the site serves the copy of Step 0 above, and the two records in `70_share/` are that publication's, put back beside the new copy after it was built.

## Phase 0: inputs, crosswalk, gates

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| 0.1 crosswalk: rows | 30 | 30 | yes |
| 0.1 crosswalk: one R6.20 name to one census code | yes | yes | yes |
| 0.1 crosswalk: each code from 370 to 399 appears once | yes | yes | yes |
| 0.1 crosswalk: the R6.20 names that need a spelling rule | ANGUL, BOLANGIR, BOUDH, DEOGARH, JAJPUR, SONEPUR | ANGUL, BOLANGIR, BOUDH, DEOGARH, JAJPUR, SONEPUR | yes |
| 0.1 crosswalk: same code as the geotagged record's district table, for the 30 R6.20 names it carries (a check added by the build) | 30 | 30 | yes |
| 0.2 units: number of units, each once | 11468 | 11468 | yes |
| 0.2 units: districts | 30 | 30 | yes |
| 0.2 units: units without a district | 0 | 0 | yes |
| 0.2 units: outside-village units, each with a row in outside_village_district.csv (a check added by the build) | 3492 | 3492 | yes |
| 0.2 units: units whose district equals the decision table's (a check added by the build) | 11468 | 11468 | yes |
| R6.20 Plantation expenditure, summed over districts, FY2014-15 to 2017-18, lakh | 151843.18 | 151843.18 | yes |
| R6.20 Plantation expenditure, summed over districts, FY2018-19 to 2025-26, lakh | 13915.72 | 13915.72 | yes |
| R6.20 Plantation expenditure, summed over districts, FY2026-27 (part year), lakh | 110.58 | 110.58 | yes |
| R6.20 NRM expenditure, summed over districts, FY2014-15 to 2017-18, lakh | 327829.94 | 327829.94 | yes |
| R6.20 NRM expenditure, summed over districts, FY2018-19 to 2025-26, lakh | 2334964.06 | 2334964.06 | yes |
| R6.20 all expenditure: one value of exp_all_lakh per district-year, 390 district-years | yes | yes | yes |
| R6.20 all expenditure (exp_all_lakh, one value per district-year), FY2014-15 to 2017-18, lakh | 750836.66 | 750836.66 | yes |
| R6.20 all expenditure (exp_all_lakh, one value per district-year), FY2018-19 to 2025-26, lakh | 3674731.26 | 3674731.26 | yes |
| R6.20: every district-period sum equals the state's printed Total rows (12 sums: 3 categories and all expenditure, 3 periods), largest difference in lakh | at most 0.01 | 0 | yes |
| R6.20 state totals: exp_all_lakh the same on the three category rows of a year (a check added by the build) | yes | yes | yes |
| plantation works, ongoing plus completed, state, FY2016-17 | 57135 | 57135 | yes |
| plantation works, ongoing plus completed, state, FY2025-26 | 4105 | 4105 | yes |
| district-years FY2018-19 to 2025-26 with zero plantation expenditure | 66 of 240 | 66 of 240 | yes |
| post-period share of state plantation expenditure, the three largest, % | Rayagada 29.76 / Mayurbhanj 11.40 / Bolangir 6.77 | Rayagada 29.76 / Mayurbhanj 11.40 / Bolangir 6.77 | yes |
| pre-period share of state plantation expenditure, the three largest, % | Mayurbhanj 20.49 / Rayagada 10.77 / Ganjam 7.64 | Mayurbhanj 20.49 / Rayagada 10.77 / Ganjam 7.64 | yes |
| FRA community titles distributed, ST plus OTFD, state | 9432 | 9432 | yes |
| FRA community extent, ha | 331568.00 | 331568.00 | yes |
| districts that have distributed no community title | 6: Sundargarh, Bhadrak, Kendrapara, Jagatsinghapur, Khordha, Puri | 6: Sundargarh, Bhadrak, Kendrapara, Jagatsinghapur, Khordha, Puri | yes |
| Hansen loss 2001-2025 summed over units and years: dense band / open band, km2 | 1552.64 / 363.84 | 1552.64 / 363.84 | yes |
| forest loss 2018-2025, dense plus open, summed over units from the per-year table, ha (within 1) | 90028 | 90028.4608 | yes |
| the same, over units in the three "loss recorded" cells of the default window, ha (within 2) | 89657 | 89657.2513 | yes |
| forest loss 2018-2025: the decision table's own column summed equals the per-year table's sum (a check added by the build) | 90028.4608 | 90028.4608 | yes |
| standing open-band hectares in the assisted-natural-regeneration cell, default window, ha (within 1) | 293921 | 293921.0503 | yes |
| units per default-window cell: restore / find the cause first / regeneration candidate / protect / verify on the ground / not a forest site | 406 / 1295 / 3055 / 1040 / 33 / 5639 | 406 / 1295 / 3055 / 1040 / 33 / 5639 | yes |
| LGD panchayat units: population / Scheduled Tribe population | 34766888 / 8895006 | 34766888 / 8895006 | yes |
| LGD panchayat units in the need table (a check added by the build) | 7976 | 7976 | yes |

*36 of 36 gates passed (`50_gap/inputs_check.csv`).*

### Files written by `scripts/08_gap_inputs.py` (run 2026-10-11T12:59:47Z)

- `50_gap/inputs_listing.json` (23,556 bytes, sha256 `4acd0f9f22f63b1b`)
- `50_gap/district_crosswalk.csv` (1,392 bytes, sha256 `8a127601ce0254c8`)
- `50_gap/unit_district.csv` (630,249 bytes, sha256 `2a76e6ed9d5977a8`)
- `50_gap/inputs_check.csv` (3,941 bytes, sha256 `524cc7de7a83aa12`)

### The environments

*The gate of `scripts/08_gap_environment.py` (`50_gap/gates_environment.csv`), run with the stage-4 interpreter.*

| gate | expected | found | pass |
|---|---|---|---|
| the interpreter running stage 4 holds exactly what requirements-stage4.txt pins (no package more, none fewer, no version different; pip itself apart) | yes: the 29 packages the file pins | yes: 29 packages held | yes |
| the stage-4 environment is outside the repository | yes | yes | yes |
| the stage-4 environment: wildboottest | 0.3.2 | 0.3.2 | yes |
| the stage-4 environment: numba | 0.62.1 | 0.62.1 | yes |
| the stage-4 environment: numpy | 2.3.x | 2.3.5 | yes |
| the main environment: numpy is the version the provenance records of the earlier stages show (8 records read) | 2.5.3 (one version in every record) | 2.5.3 | yes |
| the main environment's list of packages (pip freeze) against the list kept before stage 4 installed anything (50_gap/environment_before_stage4.txt) | the same, line for line (42 packages) | the same: 42 packages | yes |
| packages stage 4 added that the main environment holds (numba, llvmlite, wildboottest, statsmodels, tabulate, matplotlib) | none | none | yes |
| in the main environment, with numpy 2.5.3: scripts/verify_r620.py | it passes (it prints no count of checks: its line of success) | OK  1170 district rows reconcile to all 39 printed Total rows | yes |
| in the main environment, with numpy 2.5.3: scripts/verify_layer.py | 92 of 92 checks passed | 92 of 92 checks passed | yes |
| in the main environment, with numpy 2.5.3: scripts/verify_decision.py | every check | 62 of 62 checks passed | yes |

*11 of 11 gates passed (`50_gap/gates_environment.csv`).*

The stage-4 environment as that step found it (python 3.12.13; `requirements-stage4.txt`, sha256 `ce2ca3bda40374df`): certifi 2026.7.22, contourpy 1.4.0, cycler 0.12.1, fonttools 4.66.1, formulaic 1.2.2, geopandas 1.2.0, interface-meta 2.0.1, kiwisolver 1.5.1, llvmlite 0.45.1, matplotlib 3.11.2, narwhals 2.26.0, numba 0.62.1, numpy 2.3.5, packaging 26.3, pandas 3.0.6, patsy 1.0.3, pillow 12.3.0, pyogrio 0.13.0, pyparsing 3.3.3, pyproj 3.8.0, python-dateutil 2.9.0.post0, scipy 1.18.1, shapely 2.1.2, six 1.17.0, statsmodels 0.15.0, tabulate 0.10.0, typing-extensions 4.16.0, wildboottest 0.3.2, wrapt 2.5.0.

### Inputs read, with their columns

*Listed 2026-10-11T12:59:45Z by `scripts/08_gap_inputs.py` (`50_gap/inputs_listing.json`, which also has each file's SHA-256).*

- `00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv` (73,503 bytes; 1,170 rows): `fy`, `category`, `district`, `blocks`, `works_ongoing`, `works_completed`, `pct_works`, `exp_cat_lakh`, `exp_all_lakh`, `pct_exp`
- `00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv` (2,958 bytes; 39 rows): `fy`, `category`, `blocks`, `works_ongoing`, `works_completed`, `pct_works`, `exp_cat_lakh`, `exp_all_lakh`, `pct_exp`, `last_updated`
- `00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` (6,289 bytes; 30 rows): `district`, `pc11_district_code`, `frcs_constituted`, `claims_filed_gs_ind_st`, `claims_filed_gs_ind_otfd`, `claims_filed_gs_comm_st`, `claims_filed_gs_comm_otfd`, `claims_filed_gs_total_st`, `claims_filed_gs_total_otfd`, `claims_gs_to_sdlc_ind_st`, `claims_gs_to_sdlc_ind_otfd`, `claims_gs_to_sdlc_comm_st`, `claims_gs_to_sdlc_comm_otfd`, `claims_gs_to_sdlc_total_st`, `claims_gs_to_sdlc_total_otfd`, `claims_sdlc_to_dlc_ind_st`, `claims_sdlc_to_dlc_ind_otfd`, `claims_sdlc_to_dlc_comm_st`, `claims_sdlc_to_dlc_comm_otfd`, `claims_sdlc_to_dlc_total_st`, `claims_sdlc_to_dlc_total_otfd`, `claims_approved_dlc_ind_st`, `claims_approved_dlc_ind_otfd`, `claims_approved_dlc_comm_st`, `claims_approved_dlc_comm_otfd`, `claims_approved_dlc_total_st`, `claims_approved_dlc_total_otfd`, `titles_distributed_ind_st`, `titles_distributed_ind_otfd`, `titles_distributed_comm_st`, `titles_distributed_comm_otfd`, `titles_distributed_total_st`, `titles_distributed_total_otfd`, `extent_ha_ind_st`, `extent_ha_ind_otfd`, `extent_ha_comm_st`, `extent_ha_comm_otfd`, `extent_ha_total_st`, `extent_ha_total_otfd`, `claims_rejected_ind_st`, `claims_rejected_ind_otfd`, `claims_rejected_comm_st`, `claims_rejected_comm_otfd`, `claims_rejected_total_st`, `claims_rejected_total_otfd`
- `00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv` (2,273 bytes; 21 rows): `state`, `claims_received_individual`, `claims_received_community`, `claims_received_total`, `titles_distributed_individual`, `titles_distributed_community`, `titles_distributed_total`, `extent_acres_individual`, `extent_acres_community`, `extent_acres_total`, `extent_ha_individual`, `extent_ha_community`, `extent_ha_total`
- `00_raw/data_manifest.csv` (66,182 bytes; 97 rows): `item_id`, `group`, `priority`, `title`, `kind`, `ref`, `bytes`, `bytes_exact`, `dest`, `licence_or_terms`, `how_verified_2026_10_04`, `notes`
- `10_units/units.gpkg` (48,369,664 bytes; 11,468 rows): `unit_id`, `pc11_district_code`, `pc11_subdistrict_code`, `n_villages`, `unit_name`, `unit_level`, `outside_village`, `area_ha`
- `10_units/outside_village_district.csv` (536,828 bytes; 3,492 rows): `unit_id`, `unit_name`, `district_2001_label`, `subdistrict_2001_label`, `pc11_district_code`, `district`, `assigned_by`, `area_cover_share`, `area_majority_district_code`, `area_majority_district`, `area_majority_share_of_unit`, `area_second_district_code`, `area_second_share_of_unit`, `area_majority_agrees_with_assigned`, `ambiguous_by_area`, `neighbours_district_code`, `neighbours_district`, `neighbours_share`, `neighbours_second_district_code`, `neighbours_second_share`, `neighbours_n_districts`, `neighbours_by_code_district_code`, `neighbours_agree_with_assigned`, `label_district_share_in_collar`, `label_absent_from_collar`, `ambiguous_by_collar`, `ambiguous`, `ambiguous_basis`, `area_ha`
- `20_degradation/hansen_loss_by_canopy_band_by_unit.csv` (4,675,831 bytes; 11,468 rows): `unit_id`, `unit_level`, `outside_village`, `area_ha_le10`, `area_ha_gt10le30`, `area_ha_gt30`, `loss_ha_le10`, `loss_ha_gt10le30`, `loss_ha_gt30`, `loss_ha_any_cover`, `area_ha_eq0`, `loss_ha_eq0`, `loss_ha_le10_2001`, `loss_ha_le10_2002`, `loss_ha_le10_2003`, `loss_ha_le10_2004`, `loss_ha_le10_2005`, `loss_ha_le10_2006`, `loss_ha_le10_2007`, `loss_ha_le10_2008`, `loss_ha_le10_2009`, `loss_ha_le10_2010`, `loss_ha_le10_2011`, `loss_ha_le10_2012`, `loss_ha_le10_2013`, `loss_ha_le10_2014`, `loss_ha_le10_2015`, `loss_ha_le10_2016`, `loss_ha_le10_2017`, `loss_ha_le10_2018`, `loss_ha_le10_2019`, `loss_ha_le10_2020`, `loss_ha_le10_2021`, `loss_ha_le10_2022`, `loss_ha_le10_2023`, `loss_ha_le10_2024`, `loss_ha_le10_2025`, `loss_ha_gt10le30_2001`, `loss_ha_gt10le30_2002`, `loss_ha_gt10le30_2003`, `loss_ha_gt10le30_2004`, `loss_ha_gt10le30_2005`, `loss_ha_gt10le30_2006`, `loss_ha_gt10le30_2007`, `loss_ha_gt10le30_2008`, `loss_ha_gt10le30_2009`, `loss_ha_gt10le30_2010`, `loss_ha_gt10le30_2011`, `loss_ha_gt10le30_2012`, `loss_ha_gt10le30_2013`, `loss_ha_gt10le30_2014`, `loss_ha_gt10le30_2015`, `loss_ha_gt10le30_2016`, `loss_ha_gt10le30_2017`, `loss_ha_gt10le30_2018`, `loss_ha_gt10le30_2019`, `loss_ha_gt10le30_2020`, `loss_ha_gt10le30_2021`, `loss_ha_gt10le30_2022`, `loss_ha_gt10le30_2023`, `loss_ha_gt10le30_2024`, `loss_ha_gt10le30_2025`, `loss_ha_gt30_2001`, `loss_ha_gt30_2002`, `loss_ha_gt30_2003`, `loss_ha_gt30_2004`, `loss_ha_gt30_2005`, `loss_ha_gt30_2006`, `loss_ha_gt30_2007`, `loss_ha_gt30_2008`, `loss_ha_gt30_2009`, `loss_ha_gt30_2010`, `loss_ha_gt30_2011`, `loss_ha_gt30_2012`, `loss_ha_gt30_2013`, `loss_ha_gt30_2014`, `loss_ha_gt30_2015`, `loss_ha_gt30_2016`, `loss_ha_gt30_2017`, `loss_ha_gt30_2018`, `loss_ha_gt30_2019`, `loss_ha_gt30_2020`, `loss_ha_gt30_2021`, `loss_ha_gt30_2022`, `loss_ha_gt30_2023`, `loss_ha_gt30_2024`, `loss_ha_gt30_2025`
- `20_degradation/agreement_by_unit.csv` (2,551,239 bytes; 11,468 rows): `unit_id`, `unit_level`, `outside_village`, `reference_ha`, `corestack_valued_ha`, `assessed`, `corestack_zone_model`, `in_headline_population`, `agreement_class`, `hansen_flag`, `corestack_flag`, `agreement_class_between_2019_2022`, `hansen_flag_between_2019_2022`, `agreement_class_full_span_2001_2025`, `hansen_flag_full_span_2001_2025`, `agreement_class_all_assessed`, `hansen_flag_all_assessed`, `corestack_flag_all_assessed`, `hansen_loss_ha_common_2017_2023`, `hansen_rate_common_2017_2023`, `hansen_loss_ha_between_2019_2022`, `hansen_rate_between_2019_2022`, `hansen_loss_ha_full_span_2001_2025`, `hansen_rate_full_span_2001_2025`, `corestack_degradation_ha`, `corestack_partial_degradation_ha`, `corestack_lost_ha`, `corestack_improvement_ha`, `corestack_rate_degradation`, `corestack_rate_degradation_with_partial`, `corestack_rate_net`, `corestack_rate_lost`, `corestack_rate_improvement`
- `20_degradation/corestack_by_unit.csv` (2,788,494 bytes; 11,468 rows): `unit_id`, `unit_level`, `outside_village`, `area_ha`, `corestack_loss_ha`, `corestack_degradation_ha`, `corestack_partial_degradation_ha`, `corestack_improvement_ha`, `corestack_gain_ha`, `corestack_no_change_ha`, `corestack_missing_ha`, `corestack_no_value_ha`, `corestack_tree_cover_start_ha`, `corestack_tree_cover_end_ha`, `corestack_partial_density_up_height_down_ha`, `corestack_partial_density_down_height_up_ha`, `corestack_missing_share`, `corestack_net_degradation_ha`, `corestack_value_ha_zone_EPAHR`, `corestack_value_ha_zone_ECPHR`, `land_tc_gt10_ha`, `corestack_loss_ha_tc_gt10`, `corestack_degradation_ha_tc_gt10`, `corestack_partial_degradation_ha_tc_gt10`, `corestack_improvement_ha_tc_gt10`, `corestack_gain_ha_tc_gt10`, `corestack_no_change_ha_tc_gt10`, `corestack_tree_cover_start_ha_tc_gt10`, `corestack_net_degradation_ha_tc_gt10`, `lulc_tree_ha_2017`, `lulc_tree_ha_2023`, `lulc_area_ha`, `lulc_tree_both_no_value_ha`
- `30_need/need_by_unit.csv` (1,212,483 bytes; 11,468 rows): `unit_id`, `unit_level`, `outside_village`, `n_villages`, `n_villages_uninhabited`, `n_villages_without_polygon`, `population`, `population_in_villages_without_polygon`, `households`, `st_pop`, `st_share`, `sc_pop`, `sc_share`, `adi_2011`, `adi_2011_population_covered_share`, `adi_2019`, `adi_2019_population_covered_share`, `poverty_rate`, `poverty_rate_ppp2`, `poverty_rate_population_covered_share`, `poverty_rate_population_rated`, `poverty_rate_shared_shrid_population_share`, `forest_dependent_households`, `n_forest_villages`, `households_in_forest_villages`
- `40_allocation/allocation_by_unit.csv` (1,072,899 bytes; 11,468 rows): `unit_id`, `unit_level`, `outside_village`, `n_works`, `n_works_expenditure_na`, `expenditure_total`, `n_works_plantation_category`, `n_works_plantation_category_expenditure_na`, `expenditure_plantation_category`, `n_works_forestry_worktype`, `n_works_forestry_worktype_expenditure_na`, `expenditure_forestry_worktype`, `n_works_forest_named_worktype`, `n_works_forest_named_worktype_expenditure_na`, `expenditure_forest_named_worktype`, `n_works_water`, `n_works_water_expenditure_na`, `expenditure_water`, `n_works_category_unknown`, `persondays`, `n_works_persondays_reported`
- `40_allocation/allocation_by_unit_fy.csv` (7,544,719 bytes; 103,186 rows): `unit_id`, `fy_work_start`, `n_works`, `n_works_expenditure_na`, `expenditure_total`, `n_works_plantation_category`, `n_works_plantation_category_expenditure_na`, `expenditure_plantation_category`, `n_works_forestry_worktype`, `n_works_forestry_worktype_expenditure_na`, `expenditure_forestry_worktype`, `n_works_forest_named_worktype`, `n_works_forest_named_worktype_expenditure_na`, `expenditure_forest_named_worktype`, `n_works_water`, `n_works_water_expenditure_na`, `expenditure_water`, `n_works_category_unknown`, `persondays`, `n_works_persondays_reported`
- `40_allocation/allocation_unassigned.csv` (26,189 bytes; 331 rows): `district_file`, `fy_work_start`, `n_works`, `n_works_expenditure_na`, `expenditure_total`, `n_works_plantation_category`, `n_works_plantation_category_expenditure_na`, `expenditure_plantation_category`, `n_works_forestry_worktype`, `n_works_forestry_worktype_expenditure_na`, `expenditure_forestry_worktype`, `n_works_forest_named_worktype`, `n_works_forest_named_worktype_expenditure_na`, `expenditure_forest_named_worktype`, `n_works_water`, `n_works_water_expenditure_na`, `expenditure_water`, `n_works_category_unknown`, `persondays`, `n_works_persondays_reported`
- `40_allocation/assets_district_fy.csv` (65,174 bytes; 579 rows): `district_file`, `district_property`, `pc11_district_code`, `fy_work_start`, `n_works`, `n_works_expenditure_na`, `expenditure_total`, `n_works_plantation_category`, `n_works_plantation_category_expenditure_na`, `expenditure_plantation_category`, `n_works_forestry_worktype`, `n_works_forestry_worktype_expenditure_na`, `expenditure_forestry_worktype`, `n_works_forest_named_worktype`, `n_works_forest_named_worktype_expenditure_na`, `expenditure_forest_named_worktype`, `n_works_water`, `n_works_water_expenditure_na`, `expenditure_water`, `n_works_category_unknown`, `persondays`, `n_works_persondays_reported`
- `55_decision/condition_by_unit.csv` (7,275,979 bytes; 11,468 rows): `unit_id`, `unit_name`, `unit_level`, `outside_village`, `pc11_district_code`, `district`, `dense_2000_ha`, `open_2000_ha`, `low_2000_ha`, `standing_dense_ha`, `standing_open_ha`, `standing_forest_ha`, `standing_row`, `dense_open_ratio`, `near_dense_open_boundary`, `loss_dense_ha_2018_2025`, `loss_open_ha_2018_2025`, `forest_loss_ha_2018_2025`, `loss_low_ha_2018_2025`, `loss_column_2018_2025`, `cell_2018_2025`, `order_in_district_cell_2018_2025`, `forest_at_window_start_ha_2018_2025`, `forest_loss_share_pct_2018_2025`, `forest_loss_share_blank_because_2018_2025`, `order_in_district_cell_by_share_2018_2025`, `loss_dense_ha_2001_2025`, `loss_open_ha_2001_2025`, `forest_loss_ha_2001_2025`, `loss_low_ha_2001_2025`, `loss_column_2001_2025`, `cell_2001_2025`, `order_in_district_cell_2001_2025`, `forest_at_window_start_ha_2001_2025`, `forest_loss_share_pct_2001_2025`, `forest_loss_share_blank_because_2001_2025`, `order_in_district_cell_by_share_2001_2025`, `loss_dense_ha_2017_2023`, `loss_open_ha_2017_2023`, `forest_loss_ha_2017_2023`, `loss_low_ha_2017_2023`, `loss_column_2017_2023`, `cell_2017_2023`, `order_in_district_cell_2017_2023`, `forest_at_window_start_ha_2017_2023`, `forest_loss_share_pct_2017_2023`, `forest_loss_share_blank_because_2017_2023`, `order_in_district_cell_by_share_2017_2023`, `loss_dense_ha_2021_2025`, `loss_open_ha_2021_2025`, `forest_loss_ha_2021_2025`, `loss_low_ha_2021_2025`, `loss_column_2021_2025`, `cell_2021_2025`, `order_in_district_cell_2021_2025`, `forest_at_window_start_ha_2021_2025`, `forest_loss_share_pct_2021_2025`, `forest_loss_share_blank_because_2021_2025`, `order_in_district_cell_by_share_2021_2025`, `tier_provisional_2018_2025`, `corroboration`, `corroboration_basis`, `corroboration_window`, `agreement_reference_ha`, `agreement_corestack_valued_ha`, `district_check`, `governance_prompt`
- `55_decision/tiers.csv` (3,015 bytes; 6 rows): `tier`, `cell`, `tier_label`, `cell_name`, `standing_row`, `loss_column`, `what_the_name_rests_on`, `why_this_place_in_the_order`, `status`
- `docs/DATA_NOTES.md` (17,554 bytes)
- `docs/NEED.md` (19,029 bytes)
- `00_raw/docs/Village_level_dataset_schema_31Oct2022.docx` (637,132 bytes)
- `scripts/06_build_layer.py` (72,531 bytes)
- `60_layer/layer_by_unit.csv` (10,856,200 bytes; 11,468 rows): `unit_id`, `unit_name`, `unit_level`, `outside_village`, `pc11_district_code`, `district`, `district_assigned_by`, `district_ambiguous`, `area_ha`, `forest_ha`, `hansen_loss_ha`, `land_ha_tc_gt10le30`, `hansen_loss_ha_tc_gt10le30`, `land_ha_tc_le10`, `hansen_loss_ha_tc_le10`, `hansen_loss_ha_tc_eq0`, `nirv_status`, `forest_pct_of_area`, `land_tc_gt10_ha`, `hansen_loss_pct_of_forest`, `hansen_loss_ha_2017_2023`, `hansen_loss_pct_of_land_tc_gt10le30`, `corestack_loss_ha_tc_gt10`, `corestack_degradation_ha_tc_gt10`, `corestack_partial_degradation_ha_tc_gt10`, `corestack_no_change_ha_tc_gt10`, `corestack_improvement_ha_tc_gt10`, `corestack_gain_ha_tc_gt10`, `corestack_valued_ha_tc_gt10`, `corestack_loss_pct`, `corestack_degradation_pct`, `corestack_partial_degradation_pct`, `corestack_no_change_pct`, `corestack_improvement_pct`, `corestack_gain_pct`, `corestack_net_pct`, `corestack_degradation_ha_all_land`, `corestack_tree_cover_start_ha_all_land`, `agreement_class`, `agreement_class_all_assessed`, `corestack_zone_model`, `agreement_reference_ha`, `agreement_hansen_rate_2017_2023_pct`, `agreement_corestack_degradation_rate_pct`, `n_works`, `expenditure_total`, `expenditure_plantation_category`, `expenditure_forest_named_worktype`, `expenditure_water`, `expenditure_total_lakh`, `expenditure_plantation_category_lakh`, `expenditure_forest_named_worktype_lakh`, `expenditure_water_lakh`, `population`, `households`, `st_pop`, `sc_pop`, `adi_2011`, `st_share_pct`, `sc_share_pct`, `class_forest_area`, `class_hansen_loss_floor_100_ha`, `class_hansen_loss_floor_50_ha`, `class_hansen_loss_floor_1_ha`, `class_canopy_band_loss_floor_100_ha`, `class_canopy_band_loss_floor_50_ha`, `class_canopy_band_loss_floor_1_ha`, `class_corestack_degradation_floor_100_ha`, `class_corestack_degradation_floor_50_ha`, `class_corestack_degradation_floor_1_ha`, `class_corestack_net_floor_100_ha`, `class_corestack_net_floor_50_ha`, `class_corestack_net_floor_1_ha`, `class_agreement`, `class_allocation`, `class_forest_named_expenditure`, `class_st_share`, `class_adi_2011`, `shape_area_change_pct`
- `60_layer/data.js` (22,289,078 bytes)
- `00_raw/01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf` (4,506,869 bytes)
- `00_raw/05_forest_reference/isfr2023_vol2_odisha_pdf_pages_260-265.txt` (27,495 bytes)
- `requirements-stage4.txt` (2,110 bytes)
- `20_degradation/hansen.provenance.json` (8,637 bytes)
- `20_degradation/corestack.provenance.json` (12,320 bytes)
- `20_degradation/agreement.provenance.json` (10,756 bytes)
- `20_degradation/forest_floor.provenance.json` (1,891 bytes)
- `30_need/need.provenance.json` (15,023 bytes)
- `40_allocation/allocation.provenance.json` (15,953 bytes)
- `40_allocation/r620_vs_dump.provenance.json` (2,804 bytes)
- `55_decision/decision.provenance.json` (25,625 bytes)

## Phase 1: the five leftovers

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| L1 old value, against standing forest (the version the owner last read): units of the find-the-cause cell that lost under 1 per cent | 349 | 349 | yes |
| L1 old value, against standing forest (the version the owner last read): units of that cell that lost under a tenth of one per cent | 50 | 50 | yes |
| L1 old value, against standing forest (the version the owner last read): forest-site units in a no-loss cell that lost over 2 per cent | 76 | 76 | yes |
| L1 new value, on the column forest_loss_share_pct_2018_2025: forest-site units in a no-loss cell that lost over 2 per cent (the owner's figure against window start) | 74 | 74 | yes |
| L1 old -> new: units of the find-the-cause cell that lost under 1 per cent | the new value is the count on the column | 349 -> 349 | yes |
| L1 old -> new: units of that cell that lost under a tenth of one per cent | the new value is the count on the column | 50 -> 48 | yes |
| L1 old -> new: forest-site units in a no-loss cell that lost over 2 per cent | the new value is the count on the column | 76 -> 74 | yes |
| L1: the three counts docs/DECISION_LAYER.md section 5.1 prints | 349 / 48 / 74 | 349 / 48 / 74 | yes |
| L1: the repeats of those counts in sections 7 and 17 of the document (over 2 per cent; under 1 per cent) | 74; 349 | 74; 349 | yes |
| L1: figures the document's writer still reads from the counts made on standing forest | none | none | yes |
| L2: times the index's id (adi_2011) or its display labels occur in the shared copy's data.js / index.html | 0 / 0 | 0 / 0 | yes |
| L2: 60_layer/data.js still carries adi_2011 and the index's label | yes | yes | yes |
| L2: the shared copy's README says the development index is not in this copy | yes | yes | yes |
| L2: section 17 of docs/DECISION_LAYER.md records the call as reversible | yes | yes | yes |
| L3: figures of 7 October 2026 still typed in the README (19.8 MB; 5.5 MB; 92 of 92; 1,276 of 1,276; 2,447,144; 1,232,815) | none | none | yes |
| L3: the README's layer section points to docs/LAYER.md and docs/DECISION_LAYER.md for them | yes | yes | yes |
| L4: the two provider pages registered - a saved copy with the bytes and SHA-256 its manifest row gives | 2 of 2 | 2 of 2 | yes |
| L4: the manifest against commit 16b1efd - rows then, rows now, and whether every earlier byte is as it was | rows added, none changed | 92 then, 95 now, earlier bytes unchanged: yes | yes |
| L4: a dated file of what the pages say stands beside provider_cautions.json, which is as committed | yes | provider_cautions_2026-10-10.json; provider_cautions.json unchanged: yes | yes |
| L5: documents that mention 70_share and do not give the path 70_share/odisha_forest_decision_layer/ | none | none (of 4: README.md, docs/DATA_NOTES.md, docs/DECISION_LAYER.md, docs/LAYER.md) | yes |
| scripts/verify_layer.py, unchanged | 92 of 92 checks passed | 92 of 92 checks passed | yes |
| scripts/verify_layer.py is as it was at commit 16b1efd | yes | yes | yes |
| scripts/verify_decision.py: every check passes (the count is new: one check was added) | all | 62 of 62 checks passed | yes |
| the gate on the shared copy (scripts/exercise_share.py, in Chrome): steps that did what they should, the new ones included; its record is of the files on disk | all, and yes | 8 of 8; yes | yes |
| deliberate errors tried against the checks added in this phase (the verifier's new check, the writer's hold on the three counts, the gate on the shared copy), and caught | all | 15 of 15 | yes |

*25 of 25 gates passed (`50_gap/gates_phase1.csv`).*

## Phase 2: the headline, district need against district allocation

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| the Scheduled Tribe class rule used here gives, for every LGD unit that has a share, the class the layer shows for it (`class_st_share` of 60_layer/layer_by_unit.csv); units compared | 7853 | 7853 | yes |
| the stamp R6.20 prints on the four pre-period tables | 10/10/2020 | 10/10/2020 | yes |
| districts | 30 | 30 | yes |
| N1, default window, summed over districts, ha (the three loss cells; within 2 of the owner's 89,657) | 89657 | 89657.2513 | yes |
| forest loss 2018-2025 over all units, summed over districts, ha (within 1 of 90,028) | 90028 | 90028.4608 | yes |
| N2, summed over districts, ha (within 1 of 293,921) | 293921 | 293921.0503 | yes |
| N1 of LGD-unit land plus N1 of outside-village land equals N1, every district and window | yes | yes | yes |
| r620_plantation_pre_lakh, summed over districts (the gate of step 0) | 151843.18 | 151843.18 | yes |
| r620_plantation_post_lakh, summed over districts (the gate of step 0) | 13915.72 | 13915.72 | yes |
| r620_plantation_part_year_lakh, summed over districts (the gate of step 0) | 110.58 | 110.58 | yes |
| r620_nrm_pre_lakh, summed over districts (the gate of step 0) | 327829.94 | 327829.94 | yes |
| r620_nrm_post_lakh, summed over districts (the gate of step 0) | 2334964.06 | 2334964.06 | yes |
| r620_all_pre_lakh, summed over districts (the gate of step 0) | 750836.66 | 750836.66 | yes |
| r620_all_post_lakh, summed over districts (the gate of step 0) | 3674731.26 | 3674731.26 | yes |
| FY2018-19 as a per cent of post-period plantation expenditure (the owner's 53 per cent) | 53 | 53.07 | yes |
| FY2018-19 plus FY2019-20 to 2025-26 equals the post period, every district | yes | yes | yes |
| works of the dump that fall in no unit, crore rupees (the owner's 73.8) | 73.8 | 73.8 | yes |
| forest-named expenditure on works started by FY2017-18 as a per cent of all such expenditure in units, a missing start year counted as not started by then (the decision layer's 92.9) | 92.9 | 92.9 | yes |
| the dump's forest-named expenditure: by FY2017-18 + later + start year missing, summed over districts, equals the table's total | 1448602847.76 | 1448602847.76 | yes |
| the pre-period plantation share of all expenditure, per cent (the owner's 20.2232) | 20.2232 | 20.2232 | yes |
| that share applied to the post-period total, lakh (the owner's 743,148.16) | 743148.16 | 743148.16 | yes |
| LGD population / Scheduled Tribe population, summed over districts | 34766888 / 8895006 | 34766888 / 8895006 | yes |
| districts in each tercile of ADI | 10 / 10 / 10 | 10 / 10 / 10 | yes |
| districts in each tercile of Scheduled Caste share | 10 / 10 / 10 | 10 / 10 / 10 | yes |
| C7: districts left out (most of N1 in units wholly under the East Coast model) - listed, not a gate on a value | a list | Nayagarh, Khordha, Puri, Ganjam, Gajapati | yes |
| the other reading of the rule: districts that hold the East Coast units the agreement headline left out - listed | a list | Baleshwar, Cuttack, Jajapur, Nayagarh, Khordha, Puri, Ganjam, Gajapati | yes |
| N1 in units with no zone recorded, ha (so that the rule can be decided for every district) | 0 | 0 | yes |
| units the agreement headline left out (assessed, wholly under the East Coast model), summed over districts | 468 | 468 | yes |
| comparisons computed (the owner's thirteen and the second reading of C7) | 14 | 14 | yes |
| plantation works, state, FY2016-17 / FY2025-26 (the gate of step 0) | 57135 / 4105 | 57135 / 4105 | yes |

*30 of 30 gates passed (`50_gap/gates_phase2.csv`).*

### Files written by `scripts/08_build_gap_districts.py` (run 2026-10-11T13:01:15Z)

- `50_gap/district_need.csv` (15,984 bytes, sha256 `ea978fc16f8500ca`)
- `50_gap/district_allocation.csv` (8,152 bytes, sha256 `a98526993a9de84a`)
- `50_gap/need_vs_allocation.csv` (38,574 bytes, sha256 `4145eb19ecb474d0`)
- `50_gap/need_vs_allocation_summary.csv` (5,000 bytes, sha256 `77831ac32e2c5717`)
- `50_gap/marginalisation_split.csv` (7,305 bytes, sha256 `df523c940c65776f`)
- `50_gap/what_more.csv` (12,125 bytes, sha256 `c70bc6eb0d75b804`)
- `50_gap/gates_phase2.csv` (3,247 bytes, sha256 `984723269ebd05b0`)

## Phase 3: the district-year panel

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| rows of the panel (30 districts x 13 financial years) | 390 | 390 | yes |
| district-years in the models (FY2014-15 to 2025-26) | 360 | 360 | yes |
| the panel's sums by district, category and period against step 2's (district_allocation.csv): largest difference, lakh | 0 | 0 | yes |
| plantation expenditure of the panel, pre, lakh | 151843.18 | 151843.18 | yes |
| plantation expenditure of the panel, post, lakh | 13915.72 | 13915.72 | yes |
| plantation expenditure of the panel, part_year, lakh | 110.58 | 110.58 | yes |
| standard deviation of plantation's share of district expenditure across district-years, pre, percentage points (the owner's figure is reproduced with n in the divisor; with n - 1 it is the figure in brackets) | 11.25 | 11.25 (11.30) | yes |
| standard deviation of plantation's share of district expenditure across district-years, post, percentage points (the owner's figure is reproduced with n in the divisor; with n - 1 it is the figure in brackets) | 1.78 | 1.78 (1.78) | yes |
| forest standing at the start of 2018 (the panel's FY2019-20 rows) equals the decision table's forest at the start of the window 2018-2025, every district | yes | yes | yes |
| forest loss of calendar years 2018 to 2025 in the panel (loss_ha_year_t), ha (within 1 of 90,028) | 90028 | 90028.4608 | yes |
| models fitted, each on 360 district-years and 30 clusters | 7 | 7 | yes |
| reported terms whose wild-bootstrap interval is bounded on both sides (reported, not a gate on a value) | reported | 8 of 8 | yes |
| reported terms for which p fell steadily on both sides: one crossing of 0.05 a side and no climb back of more than 0.01 (reported, not a gate on a value) | reported | 6 of 8 | yes |

*13 of 13 gates passed (`50_gap/gates_phase3.csv`).*

### Files written by `scripts/08_build_gap_panel.py` (run 2026-10-10T20:36:57Z)

- `50_gap/district_year_panel.csv` (59,379 bytes, sha256 `49012547ee8ec3f5`)
- `50_gap/panel_models.csv` (5,072 bytes, sha256 `a8c7ef7ef69aa7dd`)
- `50_gap/panel_models.txt` (4,986 bytes, sha256 `8a9e9fb1e9b2ba06`)
- `50_gap/panel_models_wcb_grids.json` (21,704 bytes, sha256 `9defe9bcfc11abaa`)
- `50_gap/gates_phase3.csv` (1,629 bytes, sha256 `6d12e48b7d993518`)

## Phase 4: the historical companion, units within districts

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| units in the table | 11468 | 11468 | yes |
| units whose dense and open bands at the start of 2018, taken from the yearly columns, do not add to the decision table's forest at the start of the window | 0 | 0 | yes |
| units whose forest at the start of 2018 is within half a hundredth of a hectare below a floor (100 / 50 / 10 ha), where the floor read on the figure as printed to two decimals would differ from the floor read on four | 0 / 0 / 0 | 0 / 0 / 0 | yes |
| forest-named expenditure on works started by FY2017-18, summed over units, against step 2's sum over districts, rupees | 1346269467.11 | 1346269467.11 | yes |
| H1's sample has no unit with a blank outcome: every unit with 100 ha or more at the start has a share | yes | yes | yes |
| models fitted (H9 among them: 20_degradation carries the two classes' hectares for every unit, from which the downward share is formed) | 9 | 9 | yes |
| models whose wild-bootstrap interval is bounded on both sides (reported, not a gate on a value) | reported | 9 of 9 | yes |
| models for which p fell steadily on both sides: one crossing of 0.05 a side and no climb back of more than 0.01 (reported, not a gate on a value) | reported | 9 of 9 | yes |

*8 of 8 gates passed (`50_gap/gates_phase4.csv`).*

### Files written by `scripts/08_build_gap_units.py` (run 2026-10-10T20:38:22Z)

- `50_gap/unit_history.csv` (1,983,358 bytes, sha256 `6fe3a6f4a660f2b2`)
- `50_gap/unit_history_models.csv` (6,920 bytes, sha256 `f2684839d7db5310`)
- `50_gap/unit_history_models.txt` (6,823 bytes, sha256 `1c87824a24eba5c6`)
- `50_gap/unit_history_models_wcb_grids.json` (24,175 bytes, sha256 `a8429977eef4ef10`)
- `50_gap/gates_phase4.csv` (1,167 bytes, sha256 `c71ad60715956d7f`)

## Phase 5: forest rights, at the level the data allow

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| FRA community titles distributed, state (the gate of step 0) | 9432 | 9432 | yes |
| FRA community extent, state, ha (the gate of step 0) | 331568 | 331568 | yes |
| districts with no community title distributed | 6 | 6: Bhadrak, Jagatsinghapur, Kendrapara, Khordha, Puri, Sundargarh | yes |
| the two FRA reports of the same date differ (the README's 80 titles and 4,469 ha, here from the files) | 80 titles; 4469 ha | 80 titles; 4469 ha | yes |
| the forest villages PDF is the registered file: a row of 00_raw/data_manifest.csv names it with its exact size and SHA-256 | one row | 1 row(s) | yes |
| the forest villages PDF: pages, and pages that are one scanned image | every page one image | 64 pages, 64 of them one image | yes |
| the forest villages PDF: district counts taken from its text layer into district_need.csv (the owner's rule: only if checks (a) and (b) both hold) | none unless both hold | none: check (a) fails (a1 holds in 24 of 25; a2 holds in 0 of 1; a3 holds in 23 of 25; a4 holds in 22 of 25; a5 holds in 21 of 25; a6 holds in 18 of 25); check (b) not run | yes |

*7 of 7 gates passed (`50_gap/gates_phase5.csv`).*

### Files written by `scripts/08_build_gap_rights.py` (run 2026-10-10T22:21:36Z)

- `50_gap/fra_by_district.csv` (4,568 bytes, sha256 `37cf178731fafc68`)
- `50_gap/fra_summary.csv` (708 bytes, sha256 `cfbe515474ad9f4b`)
- `50_gap/fra_two_reports.csv` (310 bytes, sha256 `8630d58c44690c10`)
- `50_gap/forest_villages_text_layer_check.csv` (1,599 bytes, sha256 `dd77b52f5809ab48`)
- `50_gap/forest_villages_districts_as_the_layer_reads_them.csv` (1,644 bytes, sha256 `357a86c94d2d2b63`)
- `50_gap/forest_villages_pdf_record.json` (3,474 bytes, sha256 `0c51a34156bfa4ce`)
- `50_gap/gates_phase5.csv` (1,060 bytes, sha256 `6f8c180006589206`)

## The owner's corrections of 10 October 2026, after Phase 5

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

### Each output, built before the corrections and after

*The outputs of the first build are kept in `50_gap/before_the_corrections/` with their provenance record. "The same bytes" compares the SHA-256 the two records give; for a table that is not the same, the last column counts the cells that differ.*

| step | output | the same bytes as before the corrections | cells that differ |
|---|---|---|---|
| `08_build_gap_deck_tables` | `50_gap/deck_tables/districts_by_need.csv` | yes |  |
| `08_build_gap_deck_tables` | `50_gap/deck_tables/districts_by_need.md` | yes |  |
| `08_build_gap_deck_tables` | `50_gap/deck_tables/headline_rows.csv` | yes |  |
| `08_build_gap_deck_tables` | `50_gap/deck_tables/headline_rows.md` | yes |  |
| `08_build_gap_deck_tables` | `50_gap/deck_tables/marginalisation_split_c1.csv` | yes |  |
| `08_build_gap_deck_tables` | `50_gap/deck_tables/marginalisation_split_c1.md` | yes |  |
| `08_build_gap_districts` | `50_gap/district_allocation.csv` | yes |  |
| `08_build_gap_districts` | `50_gap/district_need.csv` | yes |  |
| `08_build_gap_districts` | `50_gap/gates_phase2.csv` | yes |  |
| `08_build_gap_districts` | `50_gap/marginalisation_split.csv` | yes |  |
| `08_build_gap_districts` | `50_gap/need_vs_allocation.csv` | yes |  |
| `08_build_gap_districts` | `50_gap/need_vs_allocation_summary.csv` | **no** | 2 |
| `08_build_gap_districts` | `50_gap/what_more.csv` | yes |  |
| `08_build_gap_fsi` | `50_gap/fsi_district_check.csv` | new: it was not written before |  |
| `08_build_gap_fsi` | `50_gap/fsi_summary.csv` | new: it was not written before |  |
| `08_build_gap_fsi` | `50_gap/gates_phase5b.csv` | new: it was not written before |  |
| `08_build_gap_panel` | `50_gap/district_year_panel.csv` | yes |  |
| `08_build_gap_panel` | `50_gap/gates_phase3.csv` | yes |  |
| `08_build_gap_panel` | `50_gap/panel_models.csv` | **no** | 2 |
| `08_build_gap_panel` | `50_gap/panel_models.txt` | **no** |  |
| `08_build_gap_panel` | `50_gap/panel_models_wcb_grids.json` | **no** |  |
| `08_build_gap_rights` | `50_gap/forest_villages_districts_as_the_layer_reads_them.csv` | new: it was not written before |  |
| `08_build_gap_rights` | `50_gap/forest_villages_pdf_record.json` | **no** |  |
| `08_build_gap_rights` | `50_gap/forest_villages_text_layer_check.csv` | yes |  |
| `08_build_gap_rights` | `50_gap/fra_by_district.csv` | yes |  |
| `08_build_gap_rights` | `50_gap/fra_summary.csv` | yes |  |
| `08_build_gap_rights` | `50_gap/fra_two_reports.csv` | yes |  |
| `08_build_gap_rights` | `50_gap/gates_phase5.csv` | **no** | 9 |
| `08_build_gap_units` | `50_gap/gates_phase4.csv` | yes |  |
| `08_build_gap_units` | `50_gap/unit_history.csv` | yes |  |
| `08_build_gap_units` | `50_gap/unit_history_models.csv` | yes |  |
| `08_build_gap_units` | `50_gap/unit_history_models.txt` | **no** |  |
| `08_build_gap_units` | `50_gap/unit_history_models_wcb_grids.json` | yes |  |
| `08_gap_environment` | `50_gap/environment_main_now.txt` | new: it was not written before |  |
| `08_gap_environment` | `50_gap/gates_environment.csv` | new: it was not written before |  |
| `08_gap_inputs` | `50_gap/district_crosswalk.csv` | yes |  |
| `08_gap_inputs` | `50_gap/inputs_check.csv` | yes |  |
| `08_gap_inputs` | `50_gap/inputs_listing.json` | **no** |  |
| `08_gap_inputs` | `50_gap/unit_district.csv` | yes |  |

## Phase 6: independent verification

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| scripts/verify_r620.py (it prints no count of checks: its line of success) | it passes | OK  1170 district rows reconcile to all 39 printed Total rows | yes |
| scripts/verify_layer.py | 92 of 92 checks passed | 92 of 92 checks passed | yes |
| scripts/verify_decision.py | every check | 62 of 62 checks passed | yes |
| scripts/verify_gap.py | every check | 338 of 338 checks passed | yes |
| the gate on the shared copy (scripts/exercise_share.py, in Chrome): its record, run 2026-10-10T22:16:08Z, and whether it is of the files on disk | every step, and yes | 8 of 8 steps; yes | yes |
| the deliberate errors were tried with the verifier that is on disk | yes | yes | yes |
| the control: the verifier, every part, on an untouched copy of the tables | passes | 338 of 338 checks passed | yes |
| deliberate errors planted in copies of the tables, and caught | at least 15, every one caught | 42 of 42 | yes |
| tables of 50_gap/ in which no error was planted (apart: the gate tables, the list of what changed in docs/RESULTS.md, and the lists of what differs between two builds) | none | none (of 23) | yes |
| the five kinds of error the owner named are among them | a swapped district code; a part-year leak into a sum; a shifted lag; a wrong denominator; a dropped East Coast exclusion | a swapped district code; a part-year leak into a sum; a shifted lag; a wrong denominator; a dropped East Coast exclusion | yes |
| the one round of review: parts of the verifier, and those of them that are in one agent's report and in no other | 10 of 10 | 10 of 10 | yes |
| the review round: every check of every part passed on the real tables as its agent left the part | every one | inputs: 39 of 39; districts: 65 of 65; comparisons: 35 of 35; rights: 42 of 42; panel: 40 of 40; units: 44 of 44; environment+deck+texts: 32 of 32; fsi: 40 of 40 | yes |
| the review round: the reader across all parts reported, and names it found defined in two pieces of the script | reported; none | reported; none | yes |
| the record of the review round is of the verifier that is on disk | yes | yes | yes |
| the rebuild that followed the review (three builders' definitions corrected): its gates, and the tables of figures that are byte for byte what they were | every gate; every table | 5 of 5 gates; 22 of 22 | yes |

*15 of 15 gates passed (`50_gap/gates_phase6.csv`).*

### The review round

*From `50_gap/verify_gap_reviews.json` (written 2026-10-10T22:07:19Z): each agent's own report, as the journal of the round holds it. "Checks" are those of the part as the agent left it, run on the real tables.*

| agent | part | what it did | checks passed | errors planted | caught by the part as left | disagreements | readings assumed | things listed as not covered | weak checks found and mended |
|---|---|---|---|---|---|---|---|---|---|
| review:inputs | inputs | reviewed the part as it stood, tried it with planted errors and fixed what it found | 39 of 39 | 27 | 23 | 0 | 13 | 10 | 3 |
| review:districts | districts | reviewed the part as it stood, tried it with planted errors and fixed what it found | 65 of 65 | 26 | 26 | 0 | 16 | 10 | 3 |
| review:comparisons | comparisons | reviewed the part as it stood, tried it with planted errors and fixed what it found | 35 of 35 | 28 | 28 | 0 | 17 | 9 | 2 |
| review:rights | rights | reviewed the part as it stood, tried it with planted errors and fixed what it found | 42 of 42 | 30 | 30 | 0 | 13 | 10 | 6 |
| review:panel | panel | reviewed the part as it stood, tried it with planted errors and fixed what it found | 40 of 40 | 25 | 25 | 0 | 13 | 9 | 2 |
| review:units | units | reviewed the part as it stood, tried it with planted errors and fixed what it found | 44 of 44 | 25 | 25 | 0 | 15 | 8 | 3 |
| review:small | environment, deck, texts | reviewed the part as it stood, tried it with planted errors and fixed what it found | 32 of 32 | 25 | 25 | 3 | 15 | 12 | 14 |
| write:fsi | fsi | wrote the part from the definitions and tried it with planted errors; no second agent reviewed it | 40 of 40 | 27 | 27 | 0 | 15 | 7 | 6 |

*8 agents reported; 337 of 337 checks passed; 209 of 213 planted errors caught by the parts as the agents left them; 3 disagreements, 117 readings assumed, 75 things listed as not covered, 39 weak checks found and mended. Parts written by agents: inputs, districts, comparisons, panel, units, rights, fsi; by the session: environment, deck, texts.*

**The reader across all parts reported**: 20 columns or keys that no check reads or that a check reads only in part, 6 checks whose name claims more than the code tests, and 0 names defined in two pieces of the script.

**Pieces of the script changed after the round, by the session: 5 of 12.** `scripts/verify_gap.py` (sha256 `85e9a1e9fbbc35c6`) is the pieces below, joined.

| piece | sha256 as the round left it | sha256 as assembled | changed after the round |
|---|---|---|---|
| `vg_head.py` | `07cfb73e6bdfe17e` | `2a53f40c395c9628` | **yes** |
| `part_environment.py` | `a16d996a2c8d0baa` | `ed846e6d69129ef5` | **yes** |
| `part_inputs.py` | `334d2fe3aa9b9460` | `ca61703ac30e1c93` | **yes** |
| `part_districts.py` | `b17f32a06c344d69` | `b17f32a06c344d69` | no |
| `part_comparisons.py` | `27b37057bb3e3388` | `27b37057bb3e3388` | no |
| `part_panel.py` | `b88f989fb7bff18f` | `303b877a44ea7312` | **yes** |
| `part_units.py` | `177555af33431dc8` | `177555af33431dc8` | no |
| `part_rights.py` | `7062ea0e4d447178` | `7062ea0e4d447178` | no |
| `part_fsi.py` | `5949fd6513bf3e1e` | `5949fd6513bf3e1e` | no |
| `part_deck.py` | `6da2f78fdb397929` | `f18df3cee2e4368a` | **yes** |
| `part_texts.py` | `144a5546cd4ba204` | `144a5546cd4ba204` | no |
| `vg_tail.py` | `1eb1d68a4aa45a3c` | `1eb1d68a4aa45a3c` | no |

### The deliberate errors

*Run 2026-10-10T22:07:07Z by `scripts/verify_gap_trials.py` (`50_gap/verify_gap_trials.json`): each error is planted in a copy of 50_gap/ outside the repository, and the copy's provenance record is given the bytes and SHA-256 of the damaged table (except where the part `inputs` is run, which holds the record against the repository's files); the verifier is run on the copy with --tables; caught = exit status 1 and at least one failed check whose words name no SHA-256 (any failed check, where the error is planted in the provenance record itself).*

The control, the verifier, every part, on an untouched copy: 338 of 338 checks passed.

| error planted | kind | table damaged | parts of the verifier run | checks failed, of those run | of them, naming no digest | caught |
|---|---|---|---|---|---|---|
| the census codes of two districts swapped in the crosswalk | a swapped district code | `district_crosswalk.csv` | inputs | 4 of 39 | 4 | yes |
| one unit put in a neighbouring district | a unit in the wrong district | `unit_district.csv` | inputs | 3 of 39 | 3 | yes |
| the found value of a gate altered by a hundredth | a figure altered | `inputs_check.csv` | inputs | 1 of 39 | 1 | yes |
| the need of two districts exchanged (their codes swapped in the table of need) | a swapped district code | `district_need.csv` | districts | 23 of 65 | 23 | yes |
| N1 taken over every unit, the loss under the minimum included | a need without its cell filter | `district_need.csv` | districts | 3 of 65 | 3 | yes |
| FY2026-27 added into post-period plantation money | a part-year leak into a sum | `district_allocation.csv` | districts | 3 of 65 | 3 | yes |
| works with no start year counted as started by FY2017-18 | a missing start year counted as early | `district_allocation.csv` | districts | 3 of 65 | 3 | yes |
| C1's need shares taken over all forest loss, not over N1 | a wrong denominator | `need_vs_allocation.csv` | comparisons | 2 of 35 | 2 | yes |
| C7 computed with every district kept | a dropped East Coast exclusion | `need_vs_allocation.csv`, `need_vs_allocation_summary.csv` | comparisons | 11 of 35 | 11 | yes |
| Pearson's correlation written where C1's rho belongs | another statistic under the same name | `need_vs_allocation_summary.csv` | comparisons | 1 of 35 | 1 | yes |
| the gaps of C1 added without their sign | a sum of the wrong terms | `need_vs_allocation_summary.csv` | comparisons | 1 of 35 | 1 | yes |
| one district counted in another Scheduled Tribe class | a district in the wrong class | `marginalisation_split.csv` | comparisons | 3 of 35 | 3 | yes |
| the size of the fall worked out from the share rounded to two decimals | a rounded ratio used where the exact one belongs | `what_more.csv` | comparisons | 1 of 35 | 1 | yes |
| the panel's loss of the year before replaced by the loss of the same year | a shifted lag | `district_year_panel.csv` | panel | 2 of 40 | 2 | yes |
| the part year flagged as a model year of the post period | a part-year leak into a sum | `district_year_panel.csv` | panel | 1 of 40 | 1 | yes |
| P2's estimate reported as P1 | a model under another's name | `panel_models.csv` | panel | 3 of 40 | 3 | yes |
| P1's interval replaced by the estimate plus and minus 1.96 CR1 standard errors | an interval from another method | `panel_models.csv` | panel | 4 of 40 | 4 | yes |
| the prior loss share taken over forest at the start of the window, not the forest of 2000 | a wrong denominator | `unit_history.csv` | units | 1 of 44 | 1 | yes |
| the exposure set to zero for twenty exposed units of the headline sample | an exposure miscoded | `unit_history.csv` | units | 1 of 44 | 1 | yes |
| H7's estimate and count of exposed units reported as H1 | a model under another's name | `unit_history_models.csv` | units | 4 of 44 | 4 | yes |
| H4 fitted with the East Coast districts kept (H1's figures under H4's name) | a dropped East Coast exclusion | `unit_history_models.csv` | units | 12 of 44 | 12 | yes |
| the community titles and extent of two districts exchanged | a swapped district code | `fra_by_district.csv` | rights | 1 of 42 | 1 | yes |
| R1's figures reported as R2 | another statistic under the same name | `fra_summary.csv` | rights | 6 of 42 | 6 | yes |
| the national report's community extent given in acres | a wrong unit | `fra_two_reports.csv` | rights | 1 of 42 | 1 | yes |
| the deck table's pre-period and post-period shares exchanged | columns exchanged | `deck_tables/districts_by_need.csv` | deck | 2 of 11 | 2 | yes |
| a share of the deck's split rounded down instead of half up | a rounding rule broken | `deck_tables/marginalisation_split_c1.csv` | deck | 2 of 11 | 2 | yes |
| the deck's interval for P1 replaced by the estimate plus and minus 1.96 CR1 standard errors | an interval from another method | `deck_tables/headline_rows.csv` | deck | 2 of 11 | 2 | yes |
| P1's interval in the text file of the panel models replaced by the estimate plus and minus 1.96 CR1 standard errors | an interval from another method | `panel_models.txt` | texts | 1 of 8 | 1 | yes |
| H4's counts of units, exposed units and districts in the text file of the unit models replaced by H1's | a model under another's name | `unit_history_models.txt` | texts | 1 of 8 | 1 | yes |
| the provenance record says the unit models were built with the main environment's numpy | a step run in the wrong environment | `gap.provenance.json` | environment | 1 of 14 | 0 | yes |
| a district's rows read from the forest villages PDF set to the count its page prints, as if the layer had every row | a count altered to pass a check | `forest_villages_districts_as_the_layer_reads_them.csv` | rights | 2 of 42 | 2 | yes |
| the row of the PDF's summary page that does not add up given the total that would make it | a figure altered | `forest_villages_text_layer_check.csv` | rights | 3 of 42 | 3 | yes |
| the record of the forest villages PDF says the owner's check (a) holds | a check reported as passed | `forest_villages_pdf_record.json` | rights | 5 of 42 | 5 | yes |
| the record of the forest villages PDF and its copy in the provenance record both say the owner's check (a) holds | a check reported as passed | `forest_villages_pdf_record.json`, `gap.provenance.json` | rights | 4 of 42 | 4 | yes |
| the Forest Survey's rows of two districts exchanged, as a wrong match of names would put them | a swapped district code | `fsi_district_check.csv` | fsi | 4 of 40 | 4 | yes |
| the Forest Survey's scrub taken as a per cent of the district's area, not of its forest cover | a wrong denominator | `fsi_district_check.csv` | fsi | 1 of 40 | 1 | yes |
| the Forest Survey's change in forest cover with its sign lost | a sign lost | `fsi_district_check.csv` | fsi | 2 of 40 | 2 | yes |
| the correlation of N1 with the Forest Survey's change reported where the size-free one belongs | another statistic under the same name | `fsi_summary.csv` | fsi | 4 of 40 | 4 | yes |
| the main environment's list of packages written sorted as whole lines, not in the order pip freeze prints | an order not kept | `environment_main_now.txt` | environment | 1 of 14 | 1 | yes |
| numba written into the main environment's list of packages | a package stage 4 added, in the main environment | `environment_main_now.txt` | environment | 1 of 14 | 1 | yes |
| the first step recorded with the SHA-256 of another step's script | a step recorded as built by other code | `gap.provenance.json` | environment | 1 of 14 | 0 | yes |
| the deck's intervals for P1 and H1 said to be made with Rademacher weights | a method misnamed | `deck_tables/headline_rows.csv`, `deck_tables/headline_rows.md` | deck | 1 of 11 | 1 | yes |

*42 of 42 errors caught; tables damaged: 29.*

### The rebuild after the review

**The rebuild against the build before it.**

| gate | expected | found | pass |
|---|---|---|---|
| tables of figures in both builds (50_gap/before_step3/ and 50_gap/before_step5/) with a cell, a column or a number of rows that differs | none | none (of 22 tables compared) | yes |
| tables of figures of the earlier build that are gone | none | none | yes |
| tables of figures that are byte for byte what they were | 22 of 22 | 22 of 22 | yes |
| files that differ and are not among those expected to (a record with a time or a hash, a listing, a text file with its time) | none | none | yes |
| gates of the later build that did not pass (every gate table of 50_gap/before_step5/) | none | none | yes |

*5 of 5 gates passed (`50_gap/gates_step3.csv`).*

Files compared or listed: 51; byte for byte the same: 46. Every file that differs, is new or is gone (`50_gap/rebuild_step3_differences.csv`):

| file | kind | what differs | why |
|---|---|---|---|
| `environment_main_now.txt` | text | 2 line(s) of 42: line 10 first | the main environment's list of packages as found at the run |
| `gap.provenance.json` | record | steps that differ, and in which keys - 08_build_gap_deck_tables: run_utc, script_sha256; 08_build_gap_fsi: run_utc, script_sha256; 08_gap_environment: outputs, run_utc, script_sha256 | a step that is run again is recorded anew: the record carries each run's time and the SHA-256 of the script, of the shared module and of every input and output |
| `gates_phase6.csv` | gate table | new: not in the earlier build | written since the earlier build was kept |
| `verify_gap_reviews.json` | record | new: not in the earlier build | written since the earlier build was kept |
| `verify_gap_trials.json` | record | new: not in the earlier build | written since the earlier build was kept |

## Phase 7: figures and tables for the paper and the deck

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| the font of the figures (Calibri if installed, else Carlito, else matplotlib's default) | recorded | Carlito | yes |
| F1_state_report: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; no coloured pixel; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image | all of it | files 4 of 4; 300 dpi; 13 rows plotted; coloured pixels 0.00 %; text on text 0; text end to end 0; labels on another's marker 0; titles inside 0 | yes |
| F2_outside_village_asymmetry: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; no coloured pixel; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image | all of it | files 4 of 4; 300 dpi; 10 rows plotted; coloured pixels 0.00 %; text on text 0; text end to end 0; labels on another's marker 0; titles inside 0 | yes |
| F3_map_of_cells: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; a palette of colours, the one figure allowed them; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image | all of it | files 4 of 4; 300 dpi; 11468 rows plotted; coloured pixels 20.86 %; text on text 0; text end to end 0; labels on another's marker 0; titles inside 0 | yes |
| F4_need_share_against_money_share: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; no coloured pixel; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image | all of it | files 4 of 4; 300 dpi; 60 rows plotted; coloured pixels 0.00 %; text on text 0; text end to end 0; labels on another's marker 0; titles inside 0 | yes |
| F5_need_and_money_by_marginalisation: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; no coloured pixel; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image | all of it | files 4 of 4; 300 dpi; 7 rows plotted; coloured pixels 0.00 %; text on text 0; text end to end 0; labels on another's marker 0; titles inside 0 | yes |
| F6_estimates_with_wild_bootstrap_intervals: its four files; PNG at 300 dpi; a caption with n and the source files; rows of what is plotted; no coloured pixel; no text on text and none set end to end with less than a word's space, by the script's layout check; no title inside the image | all of it | files 4 of 4; 300 dpi; 17 rows plotted; coloured pixels 0.00 %; text on text 0; text end to end 0; labels on another's marker 0; titles inside 0 | yes |
| the six PNGs on disk are the six recorded as looked at (50_gap/figures_looked_at.json, recorded 2026-10-10T18:38:40Z) | 6 of 6 | 6 of 6 | yes |
| the three deck tables, each as .csv and .md | 3 | 3 | yes |
| the deck's table of districts: rows, sorted by N1 from the largest | 30, sorted | 30, sorted | yes |
| files of figures/stage4/ and 50_gap/ that are in git (stage outputs stay out of it) | none | none | yes |

*11 of 11 gates passed (`50_gap/gates_phase7.csv`).*

### Files written by `scripts/08_build_gap_deck_tables.py` (run 2026-10-10T22:19:08Z)

- `50_gap/deck_tables/districts_by_need.csv` (9,590 bytes, sha256 `9beef3660717087a`)
- `50_gap/deck_tables/districts_by_need.md` (10,320 bytes, sha256 `26d300b016511a6c`)
- `50_gap/deck_tables/marginalisation_split_c1.csv` (2,298 bytes, sha256 `c57983821fffe3c5`)
- `50_gap/deck_tables/marginalisation_split_c1.md` (2,472 bytes, sha256 `f7c891f5fbabff6d`)
- `50_gap/deck_tables/headline_rows.csv` (1,564 bytes, sha256 `703c30a3b971de57`)
- `50_gap/deck_tables/headline_rows.md` (1,690 bytes, sha256 `f5d3223efa954e13`)

### Files written by `scripts/make_stage4_figures.py` (run 2026-10-10T22:20:09Z; font Carlito)

- `figures/stage4/F1_state_report.caption.txt` (1,233 bytes, sha256 `1550c7f5692faab2`)
- `figures/stage4/F1_state_report.csv` (612 bytes, sha256 `8632837563937a2f`)
- `figures/stage4/F1_state_report.png` (169,399 bytes, sha256 `c4e238215e532a6b`)
- `figures/stage4/F1_state_report.svg` (82,579 bytes, sha256 `496a6f6efed131ce`)
- `figures/stage4/F2_outside_village_asymmetry.caption.txt` (1,332 bytes, sha256 `37cc16bff1479705`)
- `figures/stage4/F2_outside_village_asymmetry.csv` (1,387 bytes, sha256 `dd1047331884549d`)
- `figures/stage4/F2_outside_village_asymmetry.png` (93,303 bytes, sha256 `f033aeabd3b3efed`)
- `figures/stage4/F2_outside_village_asymmetry.svg` (62,339 bytes, sha256 `86e436cdebeadfa5`)
- `figures/stage4/F3_map_of_cells.caption.txt` (1,953 bytes, sha256 `18b66d3784cc1756`)
- `figures/stage4/F3_map_of_cells.csv` (995,807 bytes, sha256 `059e714041450f21`)
- `figures/stage4/F3_map_of_cells.png` (1,167,578 bytes, sha256 `e4ccf36206922a92`)
- `figures/stage4/F3_map_of_cells.svg` (1,728,920 bytes, sha256 `163f79f62231d248`)
- `figures/stage4/F4_need_share_against_money_share.caption.txt` (1,994 bytes, sha256 `aa6cca89cd821763`)
- `figures/stage4/F4_need_share_against_money_share.csv` (2,097 bytes, sha256 `d59aa3e085bd2abf`)
- `figures/stage4/F4_need_share_against_money_share.png` (210,719 bytes, sha256 `bba9e11543356f59`)
- `figures/stage4/F4_need_share_against_money_share.svg` (110,822 bytes, sha256 `bb0c5738f0c1ef90`)
- `figures/stage4/F5_need_and_money_by_marginalisation.caption.txt` (1,509 bytes, sha256 `3053de72f98c423a`)
- `figures/stage4/F5_need_and_money_by_marginalisation.csv` (373 bytes, sha256 `851c8e61028879ae`)
- `figures/stage4/F5_need_and_money_by_marginalisation.png` (158,318 bytes, sha256 `896b2330113b87c2`)
- `figures/stage4/F5_need_and_money_by_marginalisation.svg` (90,275 bytes, sha256 `d6054fd4c8ef6c27`)
- `figures/stage4/F6_estimates_with_wild_bootstrap_intervals.caption.txt` (2,054 bytes, sha256 `057040ef4cba1200`)
- `figures/stage4/F6_estimates_with_wild_bootstrap_intervals.csv` (3,688 bytes, sha256 `a4d17aa16844fbd5`)
- `figures/stage4/F6_estimates_with_wild_bootstrap_intervals.png` (363,743 bytes, sha256 `55bc528befd1ed74`)
- `figures/stage4/F6_estimates_with_wild_bootstrap_intervals.svg` (173,697 bytes, sha256 `a25a6b053af495fe`)

## Phase 8: docs

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

### Gates

| gate | expected | found | pass |
|---|---|---|---|
| docs/GAP.md: the sections the owner listed (as headings) | all there | all 17 there | yes |
| docs/GAP.md quotes the supervisor's question | yes | yes | yes |
| docs/GAP.md, above its list of where every figure comes from: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| docs/stage4_run_log.md: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| README.md, the stage 4 section as built: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| README.md, why the original specification was superseded: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| README.md, section 9 as far as the corrections: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| docs/RESULTS.md, section 14: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| the six captions of figures/stage4/: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| the three deck tables: uses of "because", "led to", "effect of", "caused", "drove" (or "cause") outside a sentence that says what the analysis cannot show, the cells' own names apart | 0 | 0 | yes |
| docs/GAP.md carries the label: the same money distributed by need; not a requirement | yes | yes | yes |
| docs/GAP.md carries the label: not an overlap: titles are not mapped, and 'community' lumps CR with CFR | yes | yes | yes |
| docs/GAP.md carries the label: VGPP ₹/ha not in 00_raw | yes | yes | yes |
| docs/GAP.md carries the label: the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier years are a frozen 2020 snapshot | yes | yes | yes |
| docs/DECISION_LAYER.md no longer says stage 4 is not built, and points to docs/GAP.md | yes | yes | yes |
| docs/RESULTS.md: the headings it had are all there, in their order and with their numbers, and one section is appended after the last | yes | 26 headings then, 27 now; the first 26 unchanged: yes; added: ## 14. Stage 4: need against allocation | yes |
| docs/RESULTS.md above its section 13, against commit 16b1efd: lines gone or changed; those in the places the owner named (the time of writing, section 1's sentences on stage 4, the stage table's row, section 11's bullet); those that differ only in a figure that refreshed (below); and any other | no other | 8 lines gone or changed: 7 in the places named, 1 with only a refreshed figure, 0 other | yes |
| docs/RESULTS.md, the figures of its section 13.1 against commit 16b1efd (written to 50_gap/results_md_changes.csv): printed differently, and those of them that are neither the time of writing nor read from a record of the browser checks, which the owner expected to refresh; gone; added, and those added that are not read from 50_gap/ or from its verifier | printed differently: none but the time of writing and the browser checks' records; gone: 0; added: stage 4's only | printed differently: 2, of them neither: 0; gone: 0; added: 26, not stage 4's: 0 | yes |
| docs/RESULTS.md no longer says the fourth stage is not built | yes | yes | yes |
| 00_raw/data_manifest.csv against commit 16b1efd: rows then and now, and every earlier byte as it was | rows added, none changed | 92 then, 97 now; earlier bytes unchanged: yes | yes |
| files of 00_raw/ that existed at commit 16b1efd and are changed or gone, the manifest apart | none | none | yes |
| README.md: the stage 4 section is the specification as built, the original is kept under its heading with why it was superseded, and the figures list is F1 to F6 | yes | yes | yes |
| README.md: a path of this machine, an address of a person, or anything that looks like a key or token | 0 | 0 | yes |
| docs/GAP.md: a path of this machine, an address of a person, or anything that looks like a key or token | 0 | 0 | yes |
| docs/RESULTS.md: a path of this machine, an address of a person, or anything that looks like a key or token | 0 | 0 | yes |
| docs/DECISION_LAYER.md: a path of this machine, an address of a person, or anything that looks like a key or token | 0 | 0 | yes |
| docs/LAYER.md: a path of this machine, an address of a person, or anything that looks like a key or token | 0 | 0 | yes |
| docs/stage4_run_log.md: a path of this machine, an address of a person, or anything that looks like a key or token | 0 | 0 | yes |
| scripts/verify_r620.py (it prints no count of checks: its line of success) | it passes | OK  1170 district rows reconcile to all 39 printed Total rows | yes |
| scripts/verify_layer.py | 92 of 92 checks passed | 92 of 92 checks passed | yes |
| scripts/verify_decision.py | every check | 62 of 62 checks passed | yes |
| scripts/verify_gap.py | every check | 338 of 338 checks passed | yes |
| the gate on the shared copy (scripts/exercise_share.py, in Chrome): its record, run 2026-10-10T22:16:08Z, and whether it is of the files on disk | every step, and yes | 8 of 8 steps; yes | yes |

*33 of 33 gates passed (`50_gap/gates_phase8.csv`).*

### Figures of `docs/RESULTS.md` that changed when it was written again

*Its section 13.1 lists every figure in its text with the file it is read from. This is that list set against the same list in the version of the commit before this run (`50_gap/results_md_changes.csv`, written by `scripts/08_gap_closing_checks.py --phase 8`).*

**Printed differently, old → new: 2.**

| before | now | file | where in the file |
|---|---|---|---|
| 2026-10-09T05:37:27Z | 2026-10-10T23:05:39Z | this run | the UTC time at which this script ran |
| the owner's instruction of 9 October 2026 for the batch that applies his rulings: no run in the Safari application, since no unit changes cell | the owner's handoff of 11 October 2026: Chrome and WebKit only; the Safari application is not to be started | `60_layer/decision_runs.json` | key `checks_not_run_in_this_pass`: `why` of the check in the Safari application |

**Gone: 0.**

**Added: 26.**

| as printed | file | where in the file |
|---|---|---|
| 2026-10-10T20:20:22Z | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `run_utc` |
| 338 of 338 checks passed | `scripts/verify_gap.py` | its exit status and last line, run by this script as it wrote the document |
| 67.1 | `50_gap/need_vs_allocation_summary.csv` | column `need_share_pct_where_r_below_0_5`; row where `comparison` is 'C1' |
| 5 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts_r_below_0_5`; row where `comparison` is 'C1' |
| 1.9 | `50_gap/need_vs_allocation_summary.csv` | column `need_share_pct_where_r_above_2`; row where `comparison` is 'C1' |
| 7,207.11 | `50_gap/need_vs_allocation_summary.csv` | column `sum_positive_gaps_lakh`; row where `comparison` is 'C1' |
| 30 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts`; row where `comparison` is 'C1' |
| 0.67 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C1' |
| 0.38 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C1' |
| 0.84 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C1' |
| 0.00012 | `50_gap/need_vs_allocation_summary.csv` | column `p_permutation`; row where `comparison` is 'C1' |
| 0.57 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'B1' |
| 0.37 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C12' |
| 0.01 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C12' |
| 0.63 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C12' |
| 0.226 | `50_gap/panel_models.csv` | column `coefficient`; row where `id` is 'P1' |
| −0.065 | `50_gap/panel_models.csv` | column `wcb_ci95_lo`; row where `id` is 'P1' |
| 0.893 | `50_gap/panel_models.csv` | column `wcb_ci95_hi`; row where `id` is 'P1' |
| 0.383 | `50_gap/panel_models.csv` | column `wcb_p`; row where `id` is 'P1' |
| 360 | `50_gap/panel_models.csv` | column `n`; row where `id` is 'P1' |
| −0.14 | `50_gap/unit_history_models.csv` | column `coefficient`; row where `id` is 'H1' |
| −0.48 | `50_gap/unit_history_models.csv` | column `wcb_ci95_lo`; row where `id` is 'H1' |
| 0.20 | `50_gap/unit_history_models.csv` | column `wcb_ci95_hi`; row where `id` is 'H1' |
| 0.379 | `50_gap/unit_history_models.csv` | column `wcb_p`; row where `id` is 'H1' |
| 2,889 | `50_gap/unit_history_models.csv` | column `n_units`; row where `id` is 'H1' |
| 1,121 | `50_gap/unit_history_models.csv` | column `n_exposed`; row where `id` is 'H1' |

## Commits of this run, newest first

*Read from `git log` when this log was written; the commit that carries this very version of the log is the one after the newest listed.*

- `54ac016` Site words, Step 7: the strings table pairs the README's sections by heading; the writer of docs/SITE_COPY.md after a first reading of what it wrote
- `324351f` Site words, Step 7: the README and DEGRADATION.md brought up to date by hand; the writers of the documents follow the reworded page
- `492dc65` Site words, Step 5: stage 4 follows the layer - two steps run again, no table of figures moved, verify_gap 338 of 338
- `e69680d` Site words, Step 6: the README's sentence on phones says what was seen at a phone's width
- `40ca842` Site words: a bubble no longer closes on the scroll that keyboard focus makes; the check of the words now gives every "i" keyboard focus
- `fc6e583` Site words, Step 4: the check of the words waits for a bubble instead of sleeping, and keeps every run of its browser part
- `5920593` Site words, Step 4: the checks follow the reworded strings; a new check of the words, scripts/check_site_copy.py
- `2e748c9` Site words, Step 1: the blind reader's findings that are in page strings, fixed in the builders
- `00a106a` Site words, Step 3: the published copy - the overlay's box greyed out as ruled on 11 October, the README in the owner's words
- `605a9c4` Site words, Step 2: the full layer's words rewritten to the owner's deck; an "i" beside a label, its words in one new key of data.js
- `27aea62` Handoff of 11 October, Step 6: the layer's checks in Chrome and WebKit on record with the verifier as it stands; the documents written from them
- `ae35f9b` Handoff of 11 October, Step 5: Phase 8 - docs/GAP.md, with the owner's additions and a reading of every sentence against its rows
- `db644c0` Handoff of 11 October, Step 4: Phase 7 - the six figures and the three deck tables, made again from the tables the verifier checked
- `780b81c` Handoff of 11 October, Step 3: Phase 6 - the independent verifier, its one round of review, and 42 planted errors caught
- `22a480a` Handoff of 11 October, Step 2: Phase 5b - the need read against the Forest Survey's own district figures
- `74480bf` Handoff of 11 October, Step 1: the listing of inputs holds every input any step reads; rebuilt, and no table of figures moved
- `db8ddb2` Handoff of 11 October, Step 0: the shared copy published, and the check of the live site
- `825898d` Stage 4: the run log, with where the run stopped (Phase 6 in progress)
- `b80a6c3` Stage 4, the owner's corrections of 10 October: its own environment, requirements-stage4.txt, the forest villages list under his two checks
- `d9c5130` Stage 4, Phase 5: forest rights, at the level the data allow
- `957f3aa` Stage 4, Phase 4: the historical companion - units within districts
- `a0cde28` Stage 4, Phase 3: the district-year panel and its models
- `ef868ae` Stage 4, Phase 2: the headline - need against allocation by district
- `2287f4c` Stage 4, Phase 1: the five leftovers of the batch of 9 October cleared
- `c9bece2` Stage 4, Phase 0: inputs listed, the district crosswalk, a district for every unit, and the gates on what is built

## To rebuild

Each builder writes into `50_gap/` only and stops at the first gate that fails. In order:

```
python3.12 -m venv ~/.venvs/ictd-stage4      # once: stage 4's own environment (README.md section 0)
PY=~/.venvs/ictd-stage4/bin/python
$PY -m pip install --only-binary=:all: -r requirements-stage4.txt
$PY scripts/08_gap_environment.py        # the gate on the two environments
$PY scripts/08_gap_inputs.py             # Phase 0
$PY scripts/08_build_gap_districts.py    # Phase 2
$PY scripts/08_build_gap_panel.py        # Phase 3
$PY scripts/08_build_gap_units.py        # Phase 4
$PY scripts/08_build_gap_rights.py       # Phase 5
$PY scripts/08_build_gap_fsi.py          # Phase 5b
$PY scripts/verify_gap.py                # Phase 6
$PY scripts/verify_gap_trials.py         # Phase 6
$PY scripts/08_build_gap_deck_tables.py  # Phase 7
$PY scripts/make_stage4_figures.py       # Phase 7
$PY scripts/write_gap.py                 # Phase 8
$PY scripts/08_gap_closing_checks.py --phase 6   # and 7, and 8: the gates of the last three phases
$PY scripts/write_stage4_run_log.py
.venv/bin/python scripts/write_results.py            # Phase 8, in the main environment
.venv/bin/python scripts/write_decision_layer.py     # Phase 8, in the main environment
```

A script named above that does not exist yet belongs to a phase that has not been reached.

`scripts/write_gap.py` is run once more after the last of these. The last section of `docs/GAP.md` records the size and SHA-256 of every file it read, and three of them are written after it: `docs/DECISION_LAYER.md`, `docs/LAYER.md` and this log. `docs/LAYER.md` is written by a working script of the sessions that made the layer, `.session_scratch_2026-10-05/make_layer_md.py`, which is not in git.
