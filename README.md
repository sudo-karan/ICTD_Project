# Forest condition as a missing input to rural employment guarantee planning — Odisha

A pipeline that measures **forest degradation**, **social marginalisation** and **scheme allocation**
on the same administrative units, and asks whether allocation tracks need.

This file is the brief. Read it fully before writing code.

**For the current state of the pipeline and every headline number with its caveat, read `docs/RESULTS.md`.** It is
written by `scripts/write_results.py` from the stage outputs, with the file each figure came from listed in its
appendix; where this brief and that document differ on a figure, that document is the later one.

**For the decision view - where forest work is warranted, read as six cells ranked within a district - read
`docs/DECISION_LAYER.md`**, written by `scripts/write_decision_layer.py` to the same standard. Its section 17 lists the
owner's rulings of 9 October 2026 and what is still open for the Foundation for Ecological Security.

---

## 0. Environments

Two Python environments, both Python 3.12. Neither is in git.

**The main environment, `.venv/` in the repository.** Stages 0 to 3, the decision tables, the layer and its copy, and
their verifiers and document writers run here. `CLAUDE.md` lists what it is expected to hold; the versions each stage
was built with are in the provenance record beside that stage's output. Stage 4 changes nothing in it.

**Stage 4's own environment, outside the repository.** Stage 4 only reads files the earlier stages wrote. Its
bootstrap package (`wildboottest`) needs `numba`, and `numba` needs an older `numpy` than the earlier stages were
built with, so stage 4 has an environment of its own. `requirements-stage4.txt` pins exactly what that environment
holds. To make it:

```
python3.12 -m venv ~/.venvs/ictd-stage4
~/.venvs/ictd-stage4/bin/python -m pip install --only-binary=:all: -r requirements-stage4.txt
~/.venvs/ictd-stage4/bin/python scripts/08_gap_environment.py     # the gate on both environments
```

Run with that interpreter: `scripts/08_gap_environment.py`, `08_gap_inputs.py`, every `08_build_gap_*.py`,
`08_gap_closing_checks.py`, `verify_gap.py`, `verify_gap_trials.py`, `make_stage4_figures.py` and `write_gap.py`.
Each builder stops unless the interpreter running it holds exactly what the file pins, no package more and none
fewer, and writes the list into `50_gap/gap.provenance.json`. `08_gap_environment.py` holds, besides, that the main
environment's `numpy` is the version the earlier stages' provenance records show, and that `verify_r620.py`,
`verify_layer.py` and `verify_decision.py` pass there.

A writer that needs a verifier of the other environment finds the other interpreter by itself: `write_results.py`
(main) runs `verify_gap.py` with `~/.venvs/ictd-stage4/bin/python`, and `write_gap.py` (stage 4) runs the earlier
verifiers with `.venv/bin/python`. Set `ICTD_STAGE4_ENV` or `ICTD_MAIN_PYTHON` if either is somewhere else.

---

## 1. The question

Under VB–G RAM G (in force 1 July 2026), every village plan is drawn on the Yuktdhara portal from a
fixed list of 375 permissible works: the list notified as S.O. 5448(E) on 5 October 2026, registered in
`00_raw/06_scheme/` (375 rows). The figure of 318 that stood here until 9 October 2026 came from a draft of the
list circulated for comments. Of 155 portal layers, 46 across five categories concern water;
forest has four static layers describing legal boundaries and a land-degradation product from 2015–16.
Water carries a minimum expenditure floor (65 / 40 / 30 % by groundwater category); no other domain does.

**Does a gram panchayat whose principal landscape need is degrading forest receive work that addresses
it — and if not, who is affected?**

Two findings are already established by earlier work in this project and are *not* to be re-derived:

- Forest area and Scheduled Tribe population coincide. Across 25,034 gram panchayats in five states,
  ST share rises monotonically from 21.5 % in the least-forested quintile to 51.8 % in the most. Pooled
  correlation of log forest area with ST share is 0.292; in Odisha 0.324; at district level 0.508.
- The join works: 93,567 of 94,243 villages carry a unique Census-2011 code.

Two limitations were stated and are what this pipeline exists to remove:

- the forest measure was Census-2011 land use — administrative, fifteen years old, and about where
  forest *is*, not its condition;
- remoteness, population and administrative capacity were not controlled for.

Stage 1 replaces the first. Stage 4 removes the second. Nothing else about the earlier framing changes.

---

## 2. What is already verified — do not re-derive

Everything in `00_raw/` was checked on 4–5 October 2026. Each file's provenance is in
`00_raw/data_manifest.csv`. Treat these as inputs, not as things to recompute.

| File | What it is | How it was checked |
|---|---|---|
| `cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` | Odisha FRA progress, 30 districts × 45 columns, Census-2011 district codes | every count column sums to the source PDF's own TOTAL row |
| `cfr_fra/mota_fra_state_wise_2025-12-31.csv` | National MoTA FRA status, 21 states, same reference date | 7 of 9 column totals match the printed TOTAL exactly; the two extent columns differ by ±0.42 acres and cancel. Odisha's row is independently confirmed against the hectare table in Annexure-I |
| `mis_reports/odisha_r620_district_fy_category_2014-2027.csv` | **R6.20 panel: 13 FY × 3 work categories × 30 districts = 1,170 rows.** Works ongoing/completed and expenditure, per district | `scripts/verify_r620.py` — all 1,170 rows reconcile to the report's own 39 printed Total rows; integers exact, money to 0.02 lakh |
| `mis_reports/odisha_r620_state_totals_2014-2027.csv` | The 39 printed state Total rows, with the portal's own `last_updated` per table | transcribed from the Total row printed above and below each district table |
| `mis_reports/*_2016_2017.csv` | Four Odisha FY 2016-17 MIS reports | all four parse to 30 districts (7 for NRM) with every column summing to its printed Total |
| `mgnrega_assets/odisha_assets_district_fy_2026-10-04.csv` | 30 districts × financial year: works, expenditure, plantation | computed from all 1,302,664 geotagged works; checksummed per district |
| `mgnrega_assets/odisha_assets_category_totals_2026-10-04.csv` | Statewide totals by the dump's own work category | 1,302,664 works, ₹12,817 crore |
| `mgnrega_assets/odisha_assets_forestry_worktypes_LOWER_BOUNDS_2026-10-04.csv` | 25 forestry-like work types | **lower bounds** — each district's top 12 summed, capturing ₹1,799 cr of ₹1,808 cr |
| `10_units/units.gpkg`, `units_outside_nearest.gpkg`, `units_outside_drop.gpkg` (derived, not in `00_raw/`) | Stage-0 unit layers. `--outside keep`, the base: **11,468** units (7,976 LGD panchayat + 3,492 outside-village). `nearest`: **7,976** units. `drop`: 7,976 units. The layer's area is stated once, in §4 stage 0 | measured 5 Oct 2026 against the real LGD mapping; areas recomputed on the ellipsoid 6 Oct 2026. Earlier GP-mode figures (13,438 / 9,946 units; 154,046 / 112,609 km²) were never measured — the mapping had not been downloaded — and are withdrawn, as are the UTM-based areas (155,161 / 113,724 km²) |

### Headline numbers already computed

- 1,302,664 works, ₹12,817 crore. Work-start years actually run FY2003-04 → FY2024-25, but **97.9 % of
  the expenditure sits in FY2006-07 → FY2017-18**; the post-2018 tail is 29,479 works and ₹271 cr
  (2.1 %), and a further 27,759 works carry `fy_work_start = NA`. Earlier drafts of this file said the
  dump "covers FY2006-07 to 2017-18" — near enough for the totals, wrong if you slice by year.
- `WorkCategory = Plantation`: 116,309 works, ₹1,941 crore, **15.1 %** of expenditure. Rising by year of
  work start: 2.4 % (2010-11) → 17.5 % (2013-14) → 27.3 % (2016-17) → 32.9 % (2017-18).
- **The dump is not a spend-by-year panel, and must not be used as one.** It is indexed by the year a
  work *started*, and each work's whole lifetime expenditure is attributed to that year; R6.20 is
  indexed by the year money was *spent*. Measured against R6.20's all-works total, the dump captures
  82.6 % of FY2014-15, 93.4 % of FY2015-16, 83.4 % of FY2016-17, 36.2 % of FY2017-18 — and then
  3.2 %, 2.3 %, 0.6 %, 0.7 %, 0.6 %, 0.3 %, 0.1 %. **Any share computed from the dump for FY2018-19
  onward has a denominator that is 0.1–3 % of the real one and is meaningless.** The dump's apparent
  "19.5 % plantation in FY2020-21" is ₹7.5 cr out of ₹38 cr, in a year Odisha actually spent ₹5,961 cr.
- **Plantation collapsed after FY2017-18, and R6.20 is the instrument that shows it.** Plantation's
  share of all Odisha MGNREGA expenditure: 21.4 % (2014-15), 17.6 %, **24.2 % (2016-17)**, 18.6 %
  (2017-18) — then 3.3 % (2018-19), 0.33 %, 0.03 %, 0.01 %, 0.02 %, 0.03 %, **0.63 % (2024-25)**,
  0.54 %, 0.13 % (part-year 2026-27). R6.20 is complete for all 13 years (all 314 blocks, the report's
  own state totals), so this series stands on its own.
- **The dump corroborates it only up to FY2016-17, and that is enough.** Over the three years where the
  dump is a near-census, the two independent instruments track each other: FY2015-16 18.1 % vs 17.6 %
  (gap 0.6), FY2016-17 27.3 % vs 24.2 % (gap 3.1), FY2014-15 27.5 % vs 21.4 % (gap 6.1). The residual
  is what the start-year-vs-spend-year attribution predicts, not measurement error, so do not present
  these as a validation of R6.20 — present them as two instruments that do not contradict each other
  where both can see.
- There was never a contradiction between 15.1 % and 0.63 %. The first is a FY2006-18 pooled average
  from one instrument, the second a single late year from another. Comparing them was the error.
- **The collapse is in the count of works, not the unit cost.** 57,135 plantation works (2016-17) →
  4,532 (2024-25), a 12.6× fall; expenditure per work over the same span went ₹82,487 → ₹56,806, only
  1.45×. So plantation activity itself fell away; this is not an artefact of cheaper works. The
  FY2019-20 to FY2023-24 window is a separate anomaly — works still on the books at ₹1,600–6,700 each
  — and the paper should not read those five years as ordinary.
- **Meanwhile NRM became water.** Water as a share of NRM expenditure rises monotonically every single
  year: 40.1 % (2014-15) → 50.5 % (2018-19) → 60.8 % (2022-23) → 63.7 % (2024-25) → 77.8 % (2025-26) →
  85.9 % (part-year 2026-27). NRM's own share of all expenditure grew 42.8 % → 67.6 %, but the growth
  went almost entirely to water. This is the strongest result in the raw data so far, and it is what
  the new Act's water expenditure floors (65/40/30 % by CGWB groundwater category) now codify.
- By `Work Type` instead: generic "Plantation" ₹1,463 cr (11.4 %); explicitly forest-named types
  (Afforestation, Forest Protection, Eco Restoration of Forest, the "…of Forestry…" plantations)
  at least ₹143 cr (**1.1 %**); explicitly horticulture-named at least ₹53 cr.
- FRA: 9,432 community titles over 331,568 ha. Six districts have distributed none — Sundargarh
  (486 approved by DLC, 0 distributed), Bhadrak, Kendrapara, Jagatsinghapur, Khordha, Puri.

---

## 3. Layout

```
.
├── README.md                  this brief
├── 00_raw/                    downloaded or verified inputs — a file here at a commit is never edited; a new input adds files and manifest rows
│   ├── data_manifest.csv      one row for every input: id/url, exact bytes, licence, how verified (rows are added, never changed)
│   ├── 05_forest_reference/   Global Forest Watch workbook and ISFR 2023 extracts that stage 1 reconciles to; since 9 and 10 Oct 2026 also
│   │                          pages of the providers of Hansen's data and two dated extracts of what they say (each with its manifest row)
│   ├── 06_scheme/             the notified list of permissible works, S.O. 5448(E) of 5 Oct 2026: PDFs, transcription, table, check (5 manifest rows)
│   ├── cfr_fra/
│   ├── mis_reports/           the four .xls originals plus their parsed CSVs
│   └── mgnrega_assets/        district-level summaries (the 2 GB of raw assets is NOT here)
├── 10_units/                  stage 0 output   → input to 1, 2, 3
├── 20_degradation/            stage 1 output
├── 30_need/                   stage 2 output
├── 40_allocation/             stage 3 output
├── 50_gap/                    stage 4 output
├── 55_decision/               the decision tables: every unit in one of six cells, for four windows of years (git-ignored; rebuilt by a script)
├── 60_layer/                  the demo layer: one offline HTML map and its data file (git-ignored; rebuilt by a script)
├── 70_share/                  the copy of the layer made to be passed on, in `70_share/odisha_forest_decision_layer/`: the layer's two files
│                              without the map overlay and without the development index of 2011, a README; a zip beside it (git-ignored)
├── logs/                      run logs of the NIRv chain (git-ignored)
├── scripts/                   one script per step; vendor/ holds the one library the layer embeds
├── figures/
└── docs/
```

Files in `00_raw/` at a commit are never edited; registering a new input adds files and manifest rows. Every
transformation writes into a numbered folder. That is what makes the methods section of the paper writable.

### Scripts already present

| Script | State |
|---|---|
| `collect_data.py` | downloads the 52 fetchable files by Drive id / S3 key, size-checks, logs SHA-256. **Tested against a mock server only, never against live Drive or S3.** |
| `parse_mis_html_reports.py` | parses MIS `.xls` exports. Run and verified on all four supplied reports. |
| `aggregate_nrega_assets.py` | district GeoJSON → MIS panchayat code × FY × category (the 10-digit code in `Work Code`; **not** the analysis unit). Run 5 Oct 2026: reproduces the verified totals; self-checks two districts. |
| `build_odisha_villages_datameet.py` | rebuilds the village polygon layer. Run; reproduces the delivered file exactly. |
| `01_build_units.py` | stage 0. Run in all four modes against the real 52,531-polygon layer and the real LGD mapping, 5 Oct 2026; writes a provenance record beside each layer. |
| `01_assign_outside_district.py` | stage 0, an addition. A district for each of the 3,492 outside-village units: the district its DataMeet polygon names, checked two ways — against the area majority on the panchayat polygons of `00_raw/04_boundaries/` (the method asked for; they cover 35.1 per cent of this land) and against the coded villages within 100 m — and overridden only where both contradict it. Run 2026-10-07T08:21:28Z. For descriptive tables and the layer (`docs/UNITS.md`). |
| `02_upload_units_asset.py` | stage 1, step a. Puts a unit layer into Earth Engine as one table asset, unsimplified, in parts under Earth Engine's 10,485,760-byte request limit, with edges sent as geodesics; then reads every unit's geometry back and measures it against the layer. Run 5 Oct 2026; the asset was re-exported without its area column and re-checked on 6 Oct 2026. |
| `_ee_units.py` | not a step and writes nothing: the zonal-statistics machinery the stage-1 builders share, so that all of them sum pixel areas over the units, and gate them, in the same way. |
| `02_build_hansen.py` | stage 1. Forest (`treecover2000` > 30) and Hansen tree-cover loss per unit and year, with the same at > 10, > 50 and ≥ 30, and loss split by year-2000 canopy band; reconciles state totals to Global Forest Watch's published figures. Run 5 Oct 2026 (UTC) on the rebuilt layer; all gates passed. Independently replicated twice without Earth Engine (`docs/DEGRADATION.md` §8). It replaces `02_build_degradation.py`, which built the mask as ≥ 30. |
| `02_build_corestack.py` | stage 1. CoRE Stack tree-change classes 2017–2023 per unit, every class also by band of year-2000 canopy, and LULC v3 tree cover. Last run 2026-10-05T21:40:02Z; all gates passed, one of them the producers' one published Odisha figure, reproduced from their own earlier product. |
| `02_export_nirv_observations.py` | stage 1, the NIRv column. Stores every clear November–December Landsat 8 observation of NIRv, 2013–2025, in Earth Engine — one band per pass, with the scene list (`nirv_scenes.csv`) — so that nothing downstream reads Landsat again. It replaces a first design that stored one median per season, which an independent replication showed to follow the dates of the clear scenes. **72 of 84 tiles exported; the other 12 are not queued** — they were cancelled from outside this pipeline on 7 Oct 2026 with every other pending task of the project; the project's Earth Engine quota has run out (`docs/DEGRADATION.md` §10). Tested cell by cell against per-scene pixel values. |
| `02_export_nirv_yearly.py` | stage 1, the NIRv column. Computes the date-standardised yearly NIRv of every grid cell once — every pass moved to 1 December by the cell's own within-season rate — and stores it in Earth Engine with the rate, the passes and their mean day, so that the per-unit sums read stored bands. Added on 6 Oct after a batch test showed what the alternative costs: computed on the fly inside the sums, one group of units used 106 EECU-hours before it was cancelled (`docs/DEGRADATION.md` §10). **Not queued**: its 13 blocks were cancelled with the tiles on 7 Oct 2026, before any had started; a pilot block equals a numpy recomputation from the stored passes to the last bit. |
| `02_build_nirv.py` | stage 1, the NIRv column. NIRv per unit from the two stored layers, with two yearly values side by side: date-standardised (the reported columns) and the first design's median (`_unadjusted`). Before anything is summed it re-derives the stored values at 4,000 random pixels and stops if they disagree; it also stops unless the blocks and the tiles cover the same land in every unit and season. Then trend and exact test per pixel, a measured false-alarm rate, a check that the value no longer follows the date, and how much the result hangs on the fitted rate. **Not run for the state.** Tested band by band against a local recomputation and run whole on a few real units. |
| `check_nirv_blocks.py` | stage 1, the NIRv column; writes nothing but a log. The 13 blocks of yearly values were queued before the tiles they read were finished. This checks, per block, that its export started after the last successful export of every tile under it; that the scene list it was queued with gives every scene the same day as the list on disk; and (`--probe`) that on a box of one block the cells with a stored pass are exactly the cells the tiles hold an observation for. Exit 0 pass, 1 fail, 3 not decidable yet. |
| `run_nirv_chain.py` | stage 1, the NIRv column: the driver. One process that reads Earth Engine's own task records, waits for the tiles and the blocks, runs the check, `02_build_nirv.py` and `02_assemble_degradation.py` in order, each only if the one before passed, and cancels a task that uses far more compute than was measured for its kind. It resubmits nothing that failed and stops, saying why, in `logs/nirv_chain.log`. `--self-test` runs its decisions on made-up queues. **Stopped** on 7 Oct 2026 at 08:25 UTC, as it is written to, when it found 12 tiles neither exported nor queued. `--resubmit-cancelled` queues again what was cancelled (never what failed), the blocks only after every tile exists; that is the project owner's decision and has not been run. |
| `02_build_agreement.py` | stage 1. Hansen beside CoRE Stack, unit by unit, from the two sources' own tables (no Earth Engine): each unit's rate on one reference land (`treecover2000` > 10), a flag for the worst fifth on each measure, and the class *both / Hansen only / CoRE Stack only / neither / zone model excluded / insufficient forest*. Floor 100 ha (ruled 7 Oct 2026; 50 and 10 ha as sensitivity). Every figure for the headline population — units wholly under CoRE Stack's East Coast zone model left out, because the placebo fails there — and for every assessed unit, side by side. Intervals from resampling whole districts, with two other ways beside them. Headline window 2017–2023; 2019–2022 and Hansen's full span in rows of their own, never pooled. Run 2026-10-07T10:08:15Z. The three-measure version of 6 Oct is in the repository's first commit only. |
| `verify_agreement.py` | stage 1 check; writes nothing. Rebuilds the agreement tables' arithmetic from the sources, importing nothing from the builder: 41 of 41 checks passed; n = 11,468 units, 2,891 assessed at 100 ha, 2,423 in the headline population. Its docstring lists what it re-derives and what it only checks (the bootstrap intervals). |
| `02_assemble_degradation.py` | stage 1, last. Copies the sources' columns into `degradation_by_unit.csv`, one row per unit, and gates 66 sums against the sources' own summary tables. Hansen and CoRE Stack are required; NIRv is optional — while it is not built its columns are blank and `nirv_status` is `pending`. Run 2026-10-06T21:26:10Z: 11,468 rows × 63 columns, NIRv pending. |
| `02_propose_forest_floor.py` | stage 1: how many units, and how much forest and loss, survive a minimum forest area, and how repeatable a unit's loss rate is by forest area. **The floor is 100 ha, by ruling (7 Oct 2026)**; the 50 ha its own rule proposed is kept as a sensitivity. Changes no stage-1 output. Run 2026-10-07T09:59:25Z. |
| `03_build_need.py` | stage 2. Census counts, ADI and the SECC poverty rate per unit from village-level rows, and the reported `forest_dependent_households` construct. Independently replicated. |
| `04_build_allocation.py` | stage 3. Point-in-polygon allocation; reconciles to the verified totals to the rupee before writing. |
| `04_compare_dump_to_r620.py` | stage 3, the time dimension: the dump beside R6.20 by district × FY. |
| `04_check_panchayat_of_record.py` | stage 3 check behind §5.8. Reads panchayat names to describe the join; assigns nothing by them. |
| `06_build_layer.py` | the demo layer. Reads the stage tables and the unit shapes and writes `60_layer/`: one HTML file with Leaflet inside it and one data file. Formats every displayed value in Python; stops unless its class counts and totals equal the stage tables' own, no SHRUG-derived column is present, nothing refers to the network and the two files are under 25 MB. |
| `layer_template.html` | the layer's page: markup, style and the script that draws. It computes no number. |
| `verify_layer.py` | check; writes nothing. Rebuilds every field the layer displays, for every unit, from the stage tables. |
| `vendor/leaflet-1.9.4/` | Leaflet 1.9.4 (BSD 2-Clause), the one third-party library, embedded in the layer so that it needs no network. Its SHA-256 is checked at build. |
| `06_build_layer.py` | the demo layer. Reads the stage tables and the unit shapes and writes `60_layer/`: one HTML file with Leaflet inside it and one data file. Formats every displayed value in Python; stops unless its class counts and totals equal the stage tables' own, no SHRUG-derived column is present, nothing refers to the network and the two files are under 25 MB. |
| `layer_template.html` | the layer's page: markup, style and the script that draws. It computes no number. |
| `verify_layer.py` | check; writes nothing. Rebuilds every field the layer displays, for every unit, from the stage tables. |
| `exercise_layer.py` | the layer's check in a browser. Opens `60_layer/index.html` from disk, works every control and reads what the page then shows, clicks a seeded sample of units on the map and compares every displayed value with the stage tables. `chrome`: real mouse and keyboard events in a separate headless Chrome. `webkit`: Safari's engine in a view off the screen, with events made in script (macOS). Writes `60_layer/exercise_<browser>.json`. |
| `exercise_layer_safari.py` | the same layer in the Safari application itself, opened from disk: driven by the page's address alone and read back through AppleScript, nothing clicked (clicking in Safari from outside needs a Safari setting that is the owner's to change). Every layer, every minimum of forest, the units the Chrome check clicked, the search, the two text panels. Writes `60_layer/exercise_safari.json`. |
| `_browser_chrome.py`, `_browser_webkit.py`, `wkdriver.swift` | not steps and write nothing: the two small drivers `exercise_layer.py` uses, standard library only; the Swift source is compiled into the temporary folder when first needed. |
| `write_results.py` | writes `docs/RESULTS.md`. No figure is typed in it: each is read from a stage output and listed with its file in the document's appendix. Stops if the text carries a digit of its own, if a figure is blank, if a conclusion in words does not hold in the figures, if a total two files both carry differs, or if a verifier fails. |
| `vendor/leaflet-1.9.4/` | Leaflet 1.9.4 (BSD 2-Clause), the one third-party library, embedded in the layer so that it needs no network. Its SHA-256 is checked at build. |
| `00_raw/06_scheme/_build_schedule_extract.py` | inside `00_raw/`, like `cfr_fra/_build_mota.py`: makes the table of the 375 permissible works from the transcription of the Gazette's list and stops unless the Ministry's own totals, the order of the rows and every cell, read whole from the positions of the words in the PDF, agree. Its output is registered: it is not run again. |
| `00_raw/05_forest_reference/_build_provider_cautions.py` | inside `00_raw/`: takes the cautions the providers attach to Hansen's data, word for word, from two registered pages into `provider_cautions.json`, and stops unless every sentence stands in its page. Its output is registered: it is not run again. |
| `05_build_decision.py` | the decision tables, `55_decision/`. Every unit in one of six cells for four windows, from stage 1's hectares alone: the forest of 2000 with no loss recorded since (dense, open), and the forest loss of the window. Two thresholds, accepted by the owner on 9 Oct 2026 (10 ha, 1 ha). Beside the cell, never in it: the forest at the start of the window and the loss as a share of it. Stops unless standing plus lost equals the year-2000 band on the file as written. No Earth Engine. |
| `05_check_rename.py` | the gate on the renaming of five cells (9 Oct 2026): every unit's cell in every window, through the owner's list of names, against the table as it stood when he ruled on it; and every column that table had, cell for cell. Stops on one mismatch. |
| `_layer_decision.py` | not a step and writes nothing: the decision view's data and every sentence it shows, built for `06_build_layer.py`. |
| `layer_overlay.js`, `layer_overlay.json` | the optional online overlay of the decision view (Hansen loss tiles from Global Forest Watch) and the registration of its endpoint, its terms and the two points of them that are unresolved. Its code goes into a third file, `60_layer/overlay.js`, so that the layer's two files still ask the network for nothing. |
| `verify_decision.py` | check; writes nothing. Shares no code with the builders: re-adds every hectare of the decision view from stage 1's yearly columns, re-derives every cell, order, share and count, and holds the names, the export's columns and the page's handlers against what is written out in it. |
| `exercise_decision.py` | the decision view's check in a browser (`chrome`, `webkit`): every new control, units of all six cells opened on the map, two exported lists checked field by field, the overlay online, offline and failing. |
| `exercise_decision_safari.py` | the decision view in the Safari application, by address, with the unchanged Safari script's routine and one function replaced. Not part of the regression gate. |
| `run_decision_checks.py` | runs both verifiers and the browser checks one at a time and writes down every run, a failed one included (`60_layer/decision_runs.json`). |
| `07_build_share.py` | the copy made to be passed on, `70_share/odisha_forest_decision_layer/`: the layer's two files without `overlay.js` and, since 10 October 2026, without the development index of 2011 (`adi_2011` and everything that displays it; `60_layer/` keeps it), a README (how to open it, what it is and is not, what is left out, credits, that terms for passing it on are not yet agreed) and a zip beside the folder. |
| `exercise_share.py` | the gate on that copy: its two files held against `60_layer/`'s under the rule "the layer's without the development index and nothing else", the index's id and names looked for in both, and the copy opened from disk in Chrome - its overlay control says its file is not beside the page, the page asks the network for nothing, and the ranked list, a unit's panel, the list of layers and the two text panels show the index nowhere. |
| `check_pages_live.py` | check; publishes nothing. The copy as the owner publishes it (https://sudo-karan.github.io/ICTD_Project/, since 11 October 2026): the three files the site serves against the build's bytes and SHA-256, and the page opened in headless Chrome (every unit drawn, no script error, every request to the site's own host). Writes `70_share/pages_live_check.json` and `70_share/pages_publication.json` |
| `write_decision_layer.py` | writes `docs/DECISION_LAYER.md` with the reading functions and the gates of `write_results.py`: no figure is typed. |

---

## 4. The pipeline to build

Stages 1, 2 and 3 depend only on stage 0, so they can be built and run in any order. **Build stage 3
first** — see §7.

### Stage 0 — units *(script exists; you may need to extend it)*

| | |
|---|---|
| In | village polygons (`odisha_villages_pc11_datameet*.gpkg`); `LGD_village_panchayat_mapping.csv` |
| Out | `10_units/units.gpkg` — `unit_id`, `unit_name`, `unit_level`, `pc11_district_code`, `area_ha`, `outside_village` |

Use `--unit lgd_panchayat --outside keep`: that is the base layer (ruling of 5 Oct 2026). `nearest` and `drop`
are kept as sensitivity layers; see §5.1. The unit is an **LGD panchayat id, not a gram panchayat** — the
mapping has 8,152 ids for Odisha against 6,645 distinct name-and-district pairs — and is called
`lgd_panchayat` everywhere. `docs/UNITS.md` has the counts.

**A district for the outside-village units** (`10_units/outside_village_district.csv`, 7 Oct 2026). They have no
census code, so `pc11_district_code` is blank for them in `units.gpkg`. `00_raw/` has no file of district boundaries;
it has panchayat polygons with a district code (`00_raw/04_boundaries/`), which cover 35.1 per cent of this land. So each
unit takes the district its DataMeet polygon names (3,460 units), which is right for 99.92 per cent of the villages it
can be scored on, and the area majority against the panchayat polygons — the method asked for — is the check where
it can be taken: 2,170 units, 21 per cent of the land. It names another district in 63 of them (flagged, not
moved); 3 are ambiguous by area (two districts within 5 points). 13 units are moved off their name because that check
and their neighbours both contradict it; 19 polygons carry no name. **For descriptive tables and the layer:
these units stay out of any regression.**

**The base layer covers 154,929.33 km², ellipsoidal, WGS84** (ruling of 6 Oct 2026). That is the area of the
polygons on the WGS84 ellipsoid, it is what `area_ha` holds, and the figure is frozen: quote it from here or
from `docs/UNITS.md`. Of it, 41,358.31 km² (26.7 %) is the outside-village units and 113,571.01 km² the LGD
panchayat units. It is **not** to be validated against Odisha's official 155,707 km²: that is a surveyed
total, not an ellipsoidal computation of these shapes, and the polygons never claimed to tile the state. (The
earlier 155,161 km² was a UTM zone 45N area, 0.15 % too large overall and 0.67 % too large west of 82°E, where
the forest is — a longitude-correlated bias in the denominator of every per-hectare measure.)

### Stage 1 — forest condition (Google Earth Engine)

| | |
|---|---|
| In | `units.gpkg` uploaded as an Earth Engine table asset (`scripts/02_upload_units_asset.py`; the asset is `projects/replicating-paper/assets/ictd/units`) |
| Out | one table per source in `20_degradation/`, each with a row for every one of the 11,468 units, the outside-village units included; **`degradation_by_unit.csv`**, the sources side by side (11,468 rows × 63 columns, assembled 2026-10-06T21:26:10Z); and `agreement_by_unit.csv`, which sets Hansen against CoRE Stack |

Columns of `degradation_by_unit.csv`: `unit_id`, `unit_level`, `outside_village`, `forest_ha`, `hansen_loss_ha` (total and by
year 2001–2025), land and loss by band of year-2000 canopy (`land_ha_tc_*`, `hansen_loss_ha_tc_*`),
`corestack_degradation_ha`, `corestack_partial_degradation_ha`, `corestack_loss_ha`, `corestack_improvement_ha`,
`corestack_gain_ha`, the same on land with `treecover2000` > 10 (`*_tc_gt10`), `nirv_status`, `nirv_slope`,
`nirv_declining_ha` and five more NIRv columns, and `missing_data_share_hansen`, `_corestack`, `_nirv`.

**Stage 1 rests on two measures (ruling of 7 Oct 2026).** Hansen on the mask `treecover2000` > 30 measures
stand-replacing clearance of canopy that was already fairly closed in 2000; it is the validated floor. It is blind
by construction to thinning, and to change on land that was open or degraded in 2000 — the land this project is
about. That is what CoRE Stack's degradation classes record. The third source, an NIRv trend, was built,
independently replicated and found unfit to be a degradation measure: its trend moves one for one with the
correction for the date of each image. **NIRv is a reported column, not a measure, and nothing waits for it.**
`docs/DEGRADATION.md` has the full account; read it before using any column.

| source | tables in `20_degradation/` | state, 7 Oct 2026 |
|---|---|---|
| Hansen Global Forest Change v1.13 | `hansen_by_unit.csv`, `hansen_by_unit_thresholds.csv`, `hansen_loss_by_canopy_band.csv`, `hansen_loss_by_canopy_band_by_unit.csv` | built; independently replicated twice |
| CoRE Stack tree-change classes 2017–2023 | `corestack_by_unit.csv`, `corestack_by_unit_bands.csv` | built, every class by canopy band |
| Hansen beside CoRE Stack | `agreement_by_unit.csv`, `agreement_summary.csv`, `agreement_definitions.csv`; and what they assume: `agreement_intervals.csv`, `agreement_by_zone.csv`, `agreement_floor_repeatability.csv` | built; arithmetic rebuilt by a second script (41 of 41 checks passed) |
| the sources side by side | `degradation_by_unit.csv` | built; NIRv columns blank, `nirv_status` = pending |
| NIRv, Landsat 8, 2013–2025 — a reported column | — | **pending, nothing queued**: 72 of 84 tiles of observations exist; the other 12 and the 13 blocks were cancelled from outside this pipeline on 7 Oct 2026 and the chain stopped. `scripts/run_nirv_chain.py --resubmit-cancelled` resumes it, on the project owner's word |
| minimum forest area for stage 4 | `forest_floor_options.csv`, `forest_floor_repeatability.csv` | a recommendation, applied to nothing |

- **The forest mask is `treecover2000` > 30 — strictly above (ruling of 6 Oct 2026).** Every threshold in
  stage 1 is written as an inequality and there is no bare "at 30" anywhere. `treecover2000` > 30 gives
  26,630 km² of forest over the units; `treecover2000` > 10 gives 37,517 km², `treecover2000` > 50
  gives 15,572 km², and `treecover2000` ≥ 30 gives 26,745 km². All four are carried per unit
  in `hansen_by_unit_thresholds.csv`.
- **Most of the forest is outside the revenue villages.** The 3,492 outside-village units are 27 % of the
  area and hold 59 % of the forest (15,830 km²) and 57 % of the tree-cover loss 2001–2025 (888 of 1,553 km²).
  They have no census rows and so no figures in stage 2. This is a result, not a footnote, and every stage-1
  table gives them separately.
- **What the mask leaves out** (`hansen_loss_by_canopy_band.csv`). Of 2,834 km² of Hansen loss inside the units,
  1,553 km² (55 %) is on `treecover2000` > 30, 364 km² (13 %) on 10 < `treecover2000` ≤ 30 and 917 km² (32 %) on
  `treecover2000` ≤ 10. But 826 km² of that last figure is on pixels with **no canopy at all in 2000**: tree
  cover that grew after 2000 and was removed, or an artefact of detection, not forest that stood in 2000 — and
  its rise over time follows the producers' changes of method. Hansen cannot say that the land outside the mask
  is degrading forest.
- **CoRE Stack** (`corestack_by_unit.csv`). Inside the producers' tree mask, which covers 71 % of the units'
  area: class −1 (degradation) 13,692 km², 50 % of it in outside-village units; class 1
  (improvement) 10,568 km²; class −2 (lost) 6,991 km² and class 2 (gained) 9,350 km², 86 % and 88 % of
  them in LGD panchayat units. On land with `treecover2000` > 10 — the reference it shares with Hansen and NIRv — class −1 is 9,091 km² and class 1 5,524 km²: a net of +3,566 km² and a downward share (class −1 over the two) of 0.62 (95 % interval 0.59–0.65; one half means no net signal). In outside-village units the downward share is 0.64 (0.60–0.68), in LGD panchayat units 0.60 (0.56–0.64). Almost all of that net is on `treecover2000` > 30 (+3,378 km²); on 10 < `treecover2000` ≤ 30, where Hansen's mask is blind, it is +189 km². The two zone models differ: the downward share is 0.75 in the East Coast Plains and Hills image and 0.54 in the Eastern Plateau and Hills one. `corestack_degradation_ha` is class −1 alone; classes 3 and 4 are carried
  separately. Degradation and improvement are crossings of a zone-specific threshold by a classifier the
  producers report as right about two times in three; only class −2 was validated by them. Read the net of −1
  and 1, never −1 alone.
- **Do the two measures point at the same units?** (`agreement_by_unit.csv`, `agreement_summary.csv`; `docs/DEGRADATION.md`
  §4b; `docs/RESULTS.md`.) On one reference land (`treecover2000` > 10), a unit with at least **100 ha** of it on both
  grids is *assessed* — the floor the project owner ruled on 7 Oct 2026: 2,891 of 11,468 units; the other
  8,577 are *insufficient forest*. A unit is flagged by a measure when its rate is in the worst fifth of the units
  compared. Headline window 2017–2023, the years in which plantation went from 24.2 per cent of Odisha's scheme
  expenditure (2016-17) to 3.3 (2018-19). **Every figure is given two ways, side by side:**

  | | units compared | flagged by both | expected if unrelated | odds ratio (95 %) | within districts |
  |---|---|---|---|---|---|
  | **headline:** units wholly under CoRE Stack's East Coast zone model left out | 2,423 | 137 | 97 | 1.80 (1.10–2.91) | 2.30 (1.71–3.45) |
  | every assessed unit | 2,891 | 184 | 116 | 2.27 (1.42–3.65) | 2.38 (1.85–3.55) |

  **Why the first is the headline:** the table's own test of what agreement means is the placebo — Hansen's rate
  should not go with CoRE Stack's *improvement* class. It is +0.07 under the Eastern Plateau model and
  **+0.35 in the 468 units under the East Coast model** (`agreement_by_zone.csv`), which are also where the two
  measures agree most; leaving them out lowers every figure. Carry four things with it. **(1)** In the LGD panchayat
  units alone the headline odds ratio is 1.55 (0.80–3.61), an interval that includes 1: across the state, agreement is not established for them; in the
  outside-village units 2.06 (1.34–3.33). **(2)** Intervals resample whole districts (the columns `_lo95`, `_hi95`);
  `agreement_intervals.csv` gives two other ways beside them. The district of an outside-village unit is assigned,
  not surveyed, and resampling them singly instead changes the headline interval little (1.17–2.99).
  **(3)** The stricter the floor the weaker the agreement: 2.20 at 50 ha, where a unit's rate repeats at only
  0.73 (`agreement_floor_repeatability.csv`). **(4) It is about units, not hectares:** a pixel-by-pixel overlap
  was not run (it needs an Earth Engine job). Hansen's full span 2001–2025 beside the same CoRE Stack classes is
  reported separately (126 by both, odds ratio 1.54) and is not one period: **never average or pool the
  windows.**
- **NIRv is a negative methodological result** (`docs/DEGRADATION.md` §5). Landsat 8, seasons 2013–2025, median NIRv
  of the clear scenes of 1 November – 31 December, Theil–Sen slope, exact Mann–Kendall test. An independent
  replication reproduced it bit for bit and then showed that inside the window a forest pixel's NIRv falls by 13 to
  18 per cent a month while the dates of the clear scenes move by weeks between seasons, so the yearly value follows
  the calendar (correlation −0.90 with the mean scene date on its test blocks). The value was redesigned — every
  pass stored with its date and moved to 1 December by the pixel's own rate — and the replication's second round
  then measured three things on its own 177 units: (1) multiply the fitted rate by 0.9, 1.0, 1.1 and the declining
  share is 6.3, 5.8, 5.3 per cent — the trend is proportional to a nuisance parameter; (2) take one pass away from
  every pixel and 20 to 24 per cent of the declining flags turn over; (3) re-ordered seasons reach the observed
  declining share in 7 per cent of orderings in the south-west and 22 per cent state-wide. The first two are
  properties of the measure and no state-wide run can change them. `nirv_slope` and `nirv_declining_ha` (date-
  standardised) and their `_unadjusted` twins (the first design) are reported for the record. **Do not use them as
  a measure of degradation, and never quote the declining area without the increasing one.**
- **`missing_data_share` is per source.** For Hansen it is 0 in every unit and could not be otherwise: its
  no-data class is open sea here. It is not a data-quality measure for that source.
- **`hansen_loss_ha` counts loss only inside the mask**, and 4,310 units have no forest by it and 6,265 have
  under a hectare, so a loss *rate* per unit is undefined or noise for most units. **The floor for a rate is
  100 ha, by ruling of the project owner (7 Oct 2026)**: on the mask, 2,067 units keep 97.0 % of the forest and
  97.5 % of the loss. It supersedes the 50 ha first proposed (2,635 units), whose evidence was measured on
  the mask and not on the land the two measures are compared on. No stage-1 column is masked by it; the agreement
  table and the demo layer apply it, and keep 50 ha as a sensitivity.
- **Reconciliation.** Against Global Forest Watch's published Odisha totals, like for like
  (`treecover2000` > T): tree cover in 2000 is 0.66 %, 0.64 % and 0.67 % lower at T = 10, 30 and 50, and loss
  2001–2020 0.26 % lower — the units cover 0.46 % less area than Global Forest Watch's boundary. Against the
  Forest Survey of India (ISFR 2023, Vol. II, Table 10.20.2: 52,433.56 km² of forest cover, canopy density
  "more than or equal to 10%" in the report's own words), Hansen's year-2000 tree cover is 37,717 km² at
  `treecover2000` ≥ 10 and 37,517 km² at > 10, 28 % lower either way: Hansen counts only vegetation over 5 m in
  2000; ISFR counts all tree canopy of a hectare or more in late 2021, orchards, bamboo and young plantations
  included. Do not quote `forest_ha` as Odisha's forest cover.
- **Areas.** Every area in stage 1 is a sum of pixel areas on the WGS84 ellipsoid, the same basis as stage 0's
  `area_ha` since 6 Oct 2026.
- **Earth Engine quota.** The project is on the free Community tier, 150 EECU-hours a month. It ran out on
  5 Oct 2026 (UTC) and the project is in restricted mode — tasks still run, one at a time and slowly — until
  1 November unless it is moved to the Contributor tier. Batch tasks started before the limit account for only
  24 of the 150 hours; the rest went on interactive requests, which cannot be itemised without Cloud
  billing. The likeliest cause is this pipeline's own scouting: a query at a few thousand scattered points over a
  Landsat collection makes Earth Engine process a whole tile around every point. Run everything as batch tasks and
  read their cost (`docs/DEGRADATION.md` §10).

Sources, with status:

- `UMD/hansen/global_forest_change_2025_v1_13` — **verified**, CC-BY. `lossyear` 1–25 = 2001–2025, 30 m.
- `LANDSAT/LC08/C02/T1_L2` — Landsat 8 Collection-2 Level-2 surface reflectance, red `SR_B4`, NIR `SR_B5`,
  scaled `×0.0000275 − 0.2`, cloud and shadow masked from `QA_PIXEL`. Landsat 5, 7 and 9 are not used; why is
  in `docs/DEGRADATION.md` §5. Trend by Theil–Sen (`ee.Reducer.sensSlope()`), not OLS. **A fixed window is not a
  fixed point in the season**: standardise the date, or the trend is partly a trend in scene dates.
- `projects/corestack-trees/assets/tree_characteristics/overall_change_2017_2023` — **read and verified
  5 Oct 2026**, CC-BY-4.0. Eleven agro-climatic-zone images on one 25 m lattice; two have values in Odisha.
  Classes −2 lost, −1 degradation, 0 no change, 1 improvement, 2 gained, 3 and 4 partly degraded, 5 missing.
- `projects/corestack-datasets/assets/datasets/LULC_v3_river_basin/pan_india_lulc_v3_<y>_<y+1>` — **read
  5 Oct 2026**, band `predicted_label`, class 6 = trees and forest, 10 m, y = 2017 … 2024.

Two measures because one is a single point of failure. Report their agreement explicitly: where both put a unit
in the worst fifth, the claim is as strong as these sources can make it; where they disagree, say so rather than
picking one.

### Stage 2 — social need

| | |
|---|---|
| In | village-level Census 2011 rows (`village_census_data.csv`), joined to units through `LGD_village_panchayat_mapping.csv`; village ADI (`Village_Level_Predictions_14_States.csv`), averaged only over the villages that have one; SHRUG 2.2 SECC rural consumption (`shrug-secc-cons-rural-csv.zip`, linked by `shrug-pc-keys-csv.zip`); ATREE's CFR-potential village list |
| Out | `30_need/need_by_unit.csv` |

**Not `panchayat_census_adi_data.csv`**, which an earlier version of this brief named: it double counts 83
of 8,152 ids by 192,336 people and dilutes ADI by averaging in villages that have none. It is read as a
cross-check only. `docs/NEED.md` has the full account, with n and missingness for every column.

Columns: `unit_id`, `population`, `households`, `st_pop`, `st_share`, `sc_pop`, `sc_share`,
`adi_2011`, `adi_2019`, `poverty_rate`, and one reported construct, `forest_dependent_households`.
What each is for (rulings of 5 Oct 2026):

- **`st_share` is the marginalisation axis.**
- **`adi_2011` is the development regressor.** It is blank for 534 of the 7,976 LGD panchayat units
  (6.7 %). `adi_2019` is blank for 2,866 (36 %) and would silently drop more than a third of the sample;
  it stays as a reported column and is not to be used as a regressor.
- **`poverty_rate`** is SHRUG 2.2's SECC small-area poverty rate at the Tendulkar rural line,
  population-weighted over the villages that have one: n = 7,812 of 7,976 units. It is a model estimate
  (IHDS-II consumption imputed onto SECC assets) and rural only. The module was fetched on 5 Oct 2026 —
  the download needs no login and no form. Its rows are per shrid (SHRUG's location unit, usually one
  village); weighted by the census population of their villages they reproduce all 30 of its own district
  rows. Which line the column uses is read from the data, not the column name: between Rs 27.18 and
  Rs 27.22 a day, against the Rs 27 SHRUG documents. `poverty_rate_ppp2` is the same at the module's
  higher line (Rs 31). `poverty_rate_population_rated` says how many people a unit's rate rests on — 101
  units rest on fewer than 100. No proxy is to be substituted for either.
- **`forest_dependent_households` is not the need measure.** It is a reported column and a robustness
  check. Across units it ranks 0.81 alike with ST households counted regardless of forest, and it is zero
  for 3,619 of 7,976 units, 2,459 of which have Scheduled Tribe residents. The brief's three axes are
  degraded, marginalised and under-allocated; this composite collapsed two of them and duplicated stage 1's
  job. Forest comes from stage 1. It remains a **construct, not a measurement**: estimated ST households in
  villages ATREE classes as having forest inside the revenue boundary (about 10 ha or more), defined in
  words in `docs/NEED.md`, which is how it must appear in the paper.

### Stage 3 — allocation

| | |
|---|---|
| In | 30 district asset GeoJSONs (1.99 GB, not in this repo); `units.gpkg` |
| Out | `40_allocation/allocation_by_unit.csv`, and `allocation_by_unit_fy.csv` |

Columns: `unit_id`, `n_works`, `expenditure_total`, `expenditure_plantation_category`,
`expenditure_forestry_worktype`, `expenditure_forest_named_worktype`, `expenditure_water`, `persondays`, by
financial year. Each money column has its own count of works with no expenditure beside it. `persondays` is
blank: the dump reports none.

Join **spatially**, point-in-polygon on `lat`/`lon`. Do not name-match: the 10-digit MIS panchayat code
in `Work Code` has no documented mapping to the LGD panchayat id.

**There is no `expenditure_nrm`, and none may be constructed per unit.** The dump has no NRM marker, and
water plus plantation is an undercount of NRM by a share that moves from a tenth to a half across the panel
(`docs/NRM.md`). NRM comes from R6.20 at district level only. `expenditure_water` and
`expenditure_plantation_category` are flags that can overlap with the work-type flags; never add flag
columns together. Use the R6.20 panel for the district-year time dimension the asset dump does not have:
the dump stops at FY2017-18, R6.20 runs to FY2026-27.

### Stage 4 — gap model

> **Obsolete as written (5 Oct 2026). Do not build from this section.** The unit-level allocation data is
> 97.8 % pre-FY2017-18 and cannot speak to the post-2018 collapse R6.20 records. Stage 4 is to be
> respecified as a district-year panel before any code is written.

| | |
|---|---|
| In | the three CSVs above, plus confounders |
| Out | `50_gap/expected_vs_actual.csv`, `gap_ranked.csv`, `model_summary.txt` |

Regress forest-work expenditure per unit on population, remoteness (distance to district HQ), total
scheme expenditure (to control for overall scale), block groundwater category, and district fixed
effects. Report robust standard errors. The **residual is the allocation gap**: negative residual plus
high need is the finding.

Then cost the shortfall at the scheme's own plantation rate from the VGPP schedule of rates.
**That rate is not in this repo. Do not invent it.** Leave the costing unfilled and say so if it is
absent.

This is what converts "0.08 % is small" into "this LGD panchayat has *N* ha degrading, *M* forest-dependent
households, received ₹*X* against an expected ₹*Y*, shortfall ₹*Z*".

---

### The demo layer — `60_layer/` (built for the Foundation for Ecological Security)

| | |
|---|---|
| In | `10_units/units.gpkg`, `outside_village_district.csv`; `20_degradation/degradation_by_unit.csv`, `corestack_by_unit_bands.csv`, `agreement_by_unit.csv`; `30_need/need_by_unit.csv`; `40_allocation/allocation_by_unit.csv`; `scripts/layer_template.html`; `scripts/vendor/leaflet-1.9.4/` |
| Out | `60_layer/index.html` and `60_layer/data.js` — the map; `layer_by_unit.csv` — every value the map shows, one row per unit; `layer.provenance.json` |

One HTML file and one data file. **It opens from disk by double-click, makes no network request, and has no map tiles
behind it**: Leaflet 1.9.4 is inside the HTML file. All 11,468 units are drawn; outside-village units are hatched.
`docs/LAYER.md` is the full account. **The layer's sizes and the counts of its checks are not quoted here**: this
section once carried those of 7 October 2026 after the layer had been rebuilt. They are in `docs/LAYER.md` (§1 the
files and their sizes, §4 the shapes, §8 the checks) and, for the decision view, in `docs/DECISION_LAYER.md` (§16),
both written from the build that is on disk. What must not be lost:

- **Every number shown is a cell of a stage table**, formatted in Python. The page computes nothing. `scripts/verify_layer.py`
  rebuilds every displayed field of every unit from the stage tables, and `scripts/exercise_layer.py` works every
  control of the page in Chrome and in WebKit and compares units clicked on the map, field by field, with the stage
  tables. How many checks, units and values, and that all passed: `docs/LAYER.md` §8.
- **Honest colour.** A unit with too little forest for a rate to mean anything is drawn in a flat grey class,
  *insufficient forest to assess*, not on the colour scale; the floor is 100 ha by default (the ruled floor), with 50 ha and 1 ha as the other
  setting. Outside-village units on a need measure read *no census data for this land*, never blank or zero.
- **Geometry is simplified at 30 m** (shared boundaries kept shared). How many vertices that leaves, and the error in
  area it introduces overall and unit by unit, are in `docs/LAYER.md` §4. **Areas shown are the stage tables', not
  the drawn shapes'.**
- **SHRUG-derived columns are left out** (the poverty rate): SHRUG is CC BY-NC-SA 4.0. They stay in `30_need/`.
  The unit shapes derive from DataMeet's village boundaries and carry the ODbL.
- **Not run by any other stage.** Rebuild with `.venv/bin/python scripts/06_build_layer.py`, then `scripts/verify_layer.py`.

### The decision view — `55_decision/`, a view in `60_layer/`, and the copy in `70_share/odisha_forest_decision_layer/` (8 to 10 October 2026)

The owner reads the supervisor's request as one for a decision layer: something a planner opens to see where forest
work is warranted. It is added beside the measurements and replaces none of them. `docs/DECISION_LAYER.md` is the full
account; the figures are there and are not repeated here. What must not be lost:

- **Six cells, from Hansen's hectares alone**: forest standing (the forest of 2000 with no loss recorded since; not a
  measure of tree cover today) is mostly closed, mostly open, or little; forest loss in a window of years is recorded
  or not. The names state the test (renamed on 9 October 2026; no unit moved, and `scripts/05_check_rename.py` holds it).
- **No score and no state-wide ranking.** Units are listed tier by tier within one district. The order of tiers is
  provisional, to be set with the Foundation for Ecological Security. Need and allocation stand beside the tier.
- **Loss is also shown as a share** of the forest at the start of the window, beside the cell and never in it.
- **The work-type field of a cell cites rows of the notified list of permissible works** by serial number. Which rows
  bear on which cell is a proposal, for the Foundation.
- **The map overlay is the one thing that can ask the network for anything**, it is off unless ticked, and its code is
  a third file. **The copy to pass on is `70_share/odisha_forest_decision_layer/`** (a zip of it lies beside it),
  **which leaves that file out** and, since 10 October 2026, the development index of 2011 as well: no file that is
  passed on carries `adi_2011` for a unit, while `60_layer/` keeps it. Since 11 October 2026 the owner publishes that
  copy at https://sudo-karan.github.io/ICTD_Project/ (`scripts/check_pages_live.py` checks the live site against the build).
- **Rebuild** with `scripts/05_build_decision.py`, `scripts/05_check_rename.py`, `scripts/06_build_layer.py`,
  `scripts/run_decision_checks.py`, `scripts/07_build_share.py`, `scripts/exercise_share.py`, then
  `scripts/write_decision_layer.py`.

---

## 5. Things that will silently corrupt results

### 5.1 A quarter of Odisha is outside any revenue village

3,492 of 52,531 village polygons carry no Census-2011 code. They are named after their sub-district and
cover **41,358 km², 27 % of the unit layer** — the land outside any revenue village, overwhelmingly reserved
forest. LGD panchayat polygons built by unioning villages exclude it, so "degraded forest per panchayat"
silently drops a quarter of the state's forest.

Worse: **2,453 of those 3,492 blocks touch two or more LGD panchayat polygons at distance zero** — 70 % of
the blocks, and 95 % of that land by area — so "assign to the nearest panchayat" is arbitrary for almost
all of it.

Measured consequences (areas ellipsoidal, WGS84; §4 stage 0): drop it and the unit layer covers 113,571 km²;
keep it and it covers 154,929 km². The village polygons themselves cover 155,682 km²; the 753 km² between
that and the keep layer is 161 coded villages with no row in the LGD mapping. None of these is checked
against Odisha's official 155,707 km², and none should be. Pick a rule, state it on every slide and in the
paper, and report the sensitivity of the headline result to the choice.

### 5.2 The asset dump's quirks

- `Work_start_date` comes in three formats: `2017-08-09 00:00:00`, `01/01/2007` (d/m/Y), `01-APR-17 …`.
- `-1` and `null` mean "not available", not zero. Treating `-1` as a value corrupts every total.
- **Coverage effectively ends FY 2017-18.** Works starting later are 2.26 % of records, unevenly spread
  (Balangir 8,457; Ganjam 3,996; most districts a few hundred). 2.13 % have no usable start date, of
  which 22,021 are in Mayurbhanj alone.
- Neither plantation flag is clean, and the mislabelled field is **`Work Type`, not the category**. In
  Deogarh the `Plantation` category holds 428 works typed "Maintenance of rural public assets" and 132
  typed "AWC" — and by Work Name they are plantations: a plantation word in 323 of the 428 and 131 of the
  132 ("1st Year Mango Plantation of …", "Avenue Plantation at …"). A `Work Type` regex therefore misses
  real plantation work, unevenly by district: statewide 16,945 Plantation-category works, ₹242.9 cr, fall
  outside it. Always compute both the category flag and the `Work Type` regex, report both, and treat the
  regex as a lower bound, not as the stricter measure.
- **The `Plantation` category is not a forest-restoration measure.** It contains horticulture — the
  Deogarh works above are mango orchards — alongside forestry. The honest forest figure is the forest-named
  work type (the Work Type itself names forest or forestry): 8,523 works, ₹146.6 cr, **1.14 %** of
  expenditure.
- The 30 files are **not one snapshot**: 25 were last modified 15 May 2025, four on 24–28 September
  2025, one on 14 October 2025. Record per-file last-modified; do not cite them as a single dataset.
- District file names are irregular: `RAYAGARHA`, `KEONJHAR_KENDUJHAR`, `BOUDH`, `SONEPUR`,
  `JAGATSINGHAPUR`, `JAJPUR`, `KENDRAPARA`, `NUAPADA`, `BALESHWAR`. The working keys are in the manifest.

### 5.3 The MIS `.xls` files are HTML

Not Excel. `pandas.read_excel` and `openpyxl` both fail. Use `parse_mis_html_reports.py`. Three traps it
handles: the Total row is printed **both above and below** the data with its serial cell blank (so the
label sits in column 1); a row of column numbers sits under the header and looks like data; and
`state_name` is URL-encoded in some reports (`ODISHA+`) and not others (`ODISHA `).

Two more, specific to R6.20 and the reason `nrm_works_report.xls` looked like a partial export: the
block selector defaults to **MWC-Block** — one block — so the report silently returns 9 blocks of Odisha
unless you select ALL (`Rbblk` value `0`, radio **index 4**; the value and index disagree, trust the
value). And `__doPostBack` on a radio posts the *previous* value unless you set `.checked = true` first,
which fails silently and looks like success. Both are encoded in `scripts/scrape_r620_mis.js`.

### 5.4 The two FRA reports disagree

At the same reference date, 31 December 2025:

| | Odisha state report | MoTA national report |
|---|---|---|
| Community titles | 9,432 | 9,352 |
| Community extent | 331,568 ha | 327,099 ha |

A difference of 80 titles and 4,469 ha (1.35 %). Cite one, note the other, state the discrepancy.
Also: the Odisha district table lumps **CR and CFR together as "community"**. District-wise CFR alone is
not published. CFR-only figures exist at state level only (Mo Jungle Jami portal, as of 31 December 2024:
15,179 claims, 3,992 titles, 458,734.83 acres).

### 5.5 Units

MoTA's state-wise table is in **acres**; its Annexure-I and the Odisha state report are in **hectares**.
1 acre = 0.40468564224 ha. Expenditure in the MIS reports is in **lakh rupees**; in the asset dump it is
in **rupees**.

---

### 5.6 R6.20's three work categories are nested, not a partition

This is the one that will produce a wrong number quietly. NRM, Water and Plantation are **not** mutually
exclusive. Measured over all 390 district-year cells in the panel:

- Water expenditure ≤ NRM expenditure in **390 of 390**
- Plantation expenditure ≤ NRM expenditure in **390 of 390**
- Water + Plantation ≤ NRM in **382 of 390**

So NRM is the parent category and the other two are subsets of it. **Never sum the three shares.**
"NRM 67.59 %" in FY2024-25 already contains "Water 43.06 %"; adding them gives 111 % of a quantity that
cannot exceed 100 %. The eight exceptions where Water + Plantation slightly exceeds NRM are all in the
four tables frozen in 2020, worst case Ganjam FY2015-16 by ₹105.91 lakh (0.6 % of that district's
total); `verify_r620.py` lists them rather than failing on them.

Two more columns in that report to leave alone:

- `pct_works` — the "%age of works on X against total works" column has no denominator anywhere in the
  table, and the printed Total is neither the sum nor the mean of the district values. Opaque. Unused.
- `blocks` — the district's block count (sums to Odisha's 314), **not** a count of blocks that reported.

### 5.7 Four of the thirteen years are a frozen 2020 snapshot

R6.20 prints its own `last_updated` per table, and it is not uniform:

| `last_updated` | Financial years |
|---|---|
| 10/10/2020 | 2014-15, 2015-16, 2016-17, 2017-18 |
| 27/12/2024 | 2018-19 |
| 27/12/2025 | 2019-20 |
| 03/10/2026 | 2020-21 … 2024-25 |
| 04/10/2026 | 2025-26, 2026-27 |

The four high-plantation years have not been rewritten in six years. They are the *2020 state* of the
FY2014-18 record, which is the right thing to cite for a claim about the record, but the paper must say
so rather than implying a live figure. FY2026-27 is a part-year and must never be compared like-for-like
with a complete year — it is only ~19 % of FY2025-26's expenditure.

This also kills the earlier plan to settle the plantation question from the FY2016-17 R6.20 tab alone:
that single tab covers 9 blocks, is six years stale, and two of its four plantation sub-reports are
entirely zero for Odisha. The 13-year panel is what the argument now rests on.

### 5.8 A unit polygon is not the panchayat of record

Stage 3 assigns a work to the unit it was geotagged inside. That is not always the panchayat that recorded
it. Every work carries the Block and Panchayat of record; group the works by that label and find the unit
holding most of each group. Of the 1,294,160 works that fall inside a unit, only **65.2 %** sit in their
own panchayat's modal unit — 70.4 % counting LGD panchayat units alone (n = 1,162,473 works).

This is not peculiar to our polygons. CoRE Stack's own panchayat polygons, which carry the same
`Panchayat_ID`, score 67.2 %. And the two layers barely agree with each other: for the 7,779 ids drawn in
both, the median intersection-over-union is **0.25**, with centroids 1.4 km apart at the median. Which is
wrong — the polygons, the village-to-panchayat mapping, or the geotags — is not established, and an LGD
panchayat id is in any case not always a whole gram panchayat (§4, stage 0).

So `allocation_by_unit` measures what was geotagged inside a polygon, not what a panchayat received, and
any unit-level comparison of need with allocation carries large, spatially structured measurement error.
Say so wherever a unit-level number is shown. `scripts/04_check_panchayat_of_record.py` reproduces these
figures; it reads panchayat names to describe the join and assigns nothing by them.

## 6. Rules

1. **Never invent a number.** If a quantity is not in `00_raw/`, leave it unfilled and say so. This
   applies especially to the plantation unit cost and to district HQ coordinates.
2. **Every derived file records its inputs** — source filenames and a run timestamp in a header comment
   or sidecar.
3. **Check against printed totals wherever a source has one**, as the existing parsers do, and fail
   loudly on mismatch.
4. **State sample sizes and missingness** on every table. A share computed over an unstated denominator
   is not usable in a paper.
5. Prefer standard library and already-installed packages. `geopandas`, `pyogrio`, `shapely`, `pandas`,
   `numpy`, `scipy`, `scikit-learn` are expected. `statsmodels` is not — if you want it, add it
   explicitly, or write OLS with robust standard errors in numpy. Stage 1 also needs `earthengine-api` and an
   authenticated Earth Engine project (`docs/DATA_NOTES.md`, environment notes).
6. **Do not commit the 2 GB of raw assets.** Keep them in `00_raw/` and gitignore it.

---

## 7. Build order, and the risk

**Build and run stage 3 first.**

The asset dump says plantation is 15.1 % of Odisha's scheme expenditure, and 27.3 % for works started in
FY 2016-17. An earlier reading of MIS report R6.20 gave 0.63 % for FY 2024-25. These are different
instruments over different years with different definitions of "plantation", so neither refutes the
other — but a 25-fold gap sits underneath the project's premise that forest work is starved.

The four MIS reports supplied do **not** resolve it. None of them is R6.20:

- `nrm_works_report` — only 7 districts and 9 blocks, and reports NRM in aggregate, not plantation.
  It does say NRM was 41.09 % of expenditure in those blocks, which broadly agrees with the dump on NRM.
  The disagreement is specifically about *plantation*.
- `road_plantation_rpt` — all 30 districts, populated, but **physical units only**: 4,448 km planted,
  1,549,272 plants, 2,054,770 beneficiaries. No expenditure column.
- `tree_plantation_rpt` — all 30 districts, **every numeric column zero**.
- `maintenance_block_plantation_rpt` — all 30 districts, **three of ten numeric columns entirely zero**;
  only Bargarh reports anything (9.085 ha, 684 plants, 6 job-card holders).

So: still pull R6.20 for FY 2016-17 and compare it against the dump's 27.3 % for the same year.
If R6.20 also shows under 1 % for 2016-17, the two instruments measure different things and the paper
must say which it uses and why. If it shows roughly 25 %, plantation spending collapsed after 2018,
which is itself the finding.

**A second finding is already sitting in those four reports**, and it supports the thesis independently
of any satellite work: two of the four plantation reports are empty for Odisha FY 2016-17 and a third has
one district. The scheme's own MIS cannot see its own plantation activity. That is the administrative
twin of "the planning stack cannot see forest condition", and it needs no remote sensing to state.

A third, cheap and worth doing: `road_plantation_rpt` gives district-level *physical* plantation output
for FY 2016-17. The asset dump gives district-level plantation *expenditure* for the same year. They have
different scope — roadside only versus all plantation — but if their district rankings are uncorrelated,
one of the two is unreliable and you need to know which before building on it.

---

## 8. Out of scope

**Species-level or invasive-species mapping.** It needs reference labels that do not exist for Odisha.
The only labels available are 32 community forest resource management plans from Melghat, Maharashtra,
which record species at *village* level; the pipeline emits *stand* polygons. There is no correspondence
to validate against, so no accuracy figure can be computed. Do not build a species classifier and do not
describe any output as identifying invasives.

The consultation finding that prompted this — that canopy cover alone cannot represent forest condition,
because Lantana and Prosopis register as closed canopy over degraded land — is nonetheless respected by
this design. That objection is to cover measured *at a single date*. An invaded stand reached that state
through a trajectory: canopy opens, then invasion fills the gap. A multi-year trend sees that history
where a single-date classification cannot. **This is why stage 1 is a time series and not a cover map,
and it should be said in those words in the paper.**

*7 Oct 2026 — what is left of that argument.* The multi-year trend built to see that history, NIRv, was found unfit
(stage 1). Stage 1 now rests on two measures of *change between dates*: Hansen's yearly loss and CoRE Stack's change
of canopy-density or height class between about 2016–19 and 2022–25. Neither is single-date cover, so the objection
is still answered in kind. But neither follows a stand year by year, and a stand whose canopy opened and then closed
again under Lantana inside CoRE Stack's two periods would read as *no change* or *improvement*. The paper should
say so in those words, and not claim a trajectory it no longer measures.

---

## 9. What the paper and deck need out of this

1. A map of forest degradation per unit, with the two measures' agreement shown. `60_layer/` is a first version:
   interactive, offline, every unit, built for the Foundation for Ecological Security.
2. The need-versus-allocation scatter, residuals marked, confounders listed.
3. A ranked table of LGD panchayat units: degradation, ST share, expected allocation, actual, shortfall.
4. The costed shortfall — **only if the VGPP rate is supplied.**
5. A sensitivity table for the outside-village rule (§5.1).
6. A methods appendix listing every input with access date, size and checksum.

Figures: one chart per claim, readable in greyscale, axis units stated, *n* on every panel.

### Corrections the draft paper and deck still carry

- The paper says the MIS covers **"2010-11 through 2025-26"**. The portal offers **2014-15 to 2026-27**,
  and FY2026-27 is a part-year. Fix the range.
- Anywhere the draft contrasts 15.1 % against 0.63 % as a discrepancy to be explained, delete it. The
  two figures come from different instruments on different bases and were never in conflict; the real
  finding is the FY2017-18 break in the R6.20 series.
- Anywhere NRM, water and plantation shares are added or shown as a stacked composition, that chart is
  wrong — the categories are nested (§5.6). The defensible version of that chart is water as a share of
  *NRM*, which is the monotonic 40 % → 86 % series.
