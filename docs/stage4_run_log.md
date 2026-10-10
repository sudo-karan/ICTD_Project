# Stage 4: the run log

*Written 2026-10-10T20:15:24Z by `scripts/write_stage4_run_log.py`. The gate tables, the lists of files and the package versions are read from the files named beside them; the notes are typed and carry no figure of the analysis. The owner's prompt of 10 October 2026 set nine phases, 0 to 8, each ending in a commit.*

## Where the run stands

Phases written up below: 0, 1, 2, 3, 4, 5. The last is Phase 5, forest rights, at the level the data allow. Every gate of every phase listed passed.

The stage outputs (`50_gap/`, `figures/stage4/`) are not in git. If they are missing, rebuild them: the section "To rebuild" at the end gives the order.

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

## The owner's handoff of 11 October 2026

The run was taken up again on 11 October 2026 under a note from the owner (`.session_scratch_2026-10-05/handoff/2026-10-11_finish_stage4.md`, not in git). It ruled on what was open (one round of review of the verifier's parts and no more; `docs/LAYER.md` to be written again; H9 stays, as a sensitivity; `scripts/layer_overlay.json` stays as it is) and set seven steps. Each ends in a commit.

| step | what | state |
|---|---|---|
| 0 | publish the shared copy to GitHub Pages | done |
| 1 | fix the input listing and rebuild | not yet |
| 2 | Phase 5b: the need read against the Forest Survey's own figures | not yet |
| 3 | finish Phase 6 | not yet |
| 4 | Phase 7 | not yet |
| 5 | Phase 8, with the additions to the account of the stage | not yet |
| 6 | the decision view in WebKit, with the machine awake | not yet |

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

*From `70_share/pages_publication.json` and `70_share/pages_live_check.json`, which are not in git.*

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

### Files written by `scripts/08_gap_inputs.py` (run 2026-10-10T18:08:08Z)

- `50_gap/inputs_listing.json` (18,145 bytes, sha256 `825ed1ac59aea15b`)
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

*Listed 2026-10-10T18:08:06Z by `scripts/08_gap_inputs.py` (`50_gap/inputs_listing.json`, which also has each file's SHA-256).*

- `00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv` (73,503 bytes; 1,170 rows): `fy`, `category`, `district`, `blocks`, `works_ongoing`, `works_completed`, `pct_works`, `exp_cat_lakh`, `exp_all_lakh`, `pct_exp`
- `00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv` (2,958 bytes; 39 rows): `fy`, `category`, `blocks`, `works_ongoing`, `works_completed`, `pct_works`, `exp_cat_lakh`, `exp_all_lakh`, `pct_exp`, `last_updated`
- `00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` (6,289 bytes; 30 rows): `district`, `pc11_district_code`, `frcs_constituted`, `claims_filed_gs_ind_st`, `claims_filed_gs_ind_otfd`, `claims_filed_gs_comm_st`, `claims_filed_gs_comm_otfd`, `claims_filed_gs_total_st`, `claims_filed_gs_total_otfd`, `claims_gs_to_sdlc_ind_st`, `claims_gs_to_sdlc_ind_otfd`, `claims_gs_to_sdlc_comm_st`, `claims_gs_to_sdlc_comm_otfd`, `claims_gs_to_sdlc_total_st`, `claims_gs_to_sdlc_total_otfd`, `claims_sdlc_to_dlc_ind_st`, `claims_sdlc_to_dlc_ind_otfd`, `claims_sdlc_to_dlc_comm_st`, `claims_sdlc_to_dlc_comm_otfd`, `claims_sdlc_to_dlc_total_st`, `claims_sdlc_to_dlc_total_otfd`, `claims_approved_dlc_ind_st`, `claims_approved_dlc_ind_otfd`, `claims_approved_dlc_comm_st`, `claims_approved_dlc_comm_otfd`, `claims_approved_dlc_total_st`, `claims_approved_dlc_total_otfd`, `titles_distributed_ind_st`, `titles_distributed_ind_otfd`, `titles_distributed_comm_st`, `titles_distributed_comm_otfd`, `titles_distributed_total_st`, `titles_distributed_total_otfd`, `extent_ha_ind_st`, `extent_ha_ind_otfd`, `extent_ha_comm_st`, `extent_ha_comm_otfd`, `extent_ha_total_st`, `extent_ha_total_otfd`, `claims_rejected_ind_st`, `claims_rejected_ind_otfd`, `claims_rejected_comm_st`, `claims_rejected_comm_otfd`, `claims_rejected_total_st`, `claims_rejected_total_otfd`
- `00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv` (2,273 bytes; 21 rows): `state`, `claims_received_individual`, `claims_received_community`, `claims_received_total`, `titles_distributed_individual`, `titles_distributed_community`, `titles_distributed_total`, `extent_acres_individual`, `extent_acres_community`, `extent_acres_total`, `extent_ha_individual`, `extent_ha_community`, `extent_ha_total`
- `00_raw/data_manifest.csv` (65,068 bytes; 96 rows): `item_id`, `group`, `priority`, `title`, `kind`, `ref`, `bytes`, `bytes_exact`, `dest`, `licence_or_terms`, `how_verified_2026_10_04`, `notes`
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
- `docs/DATA_NOTES.md` (17,069 bytes)
- `docs/NEED.md` (19,029 bytes)
- `00_raw/docs/Village_level_dataset_schema_31Oct2022.docx` (637,132 bytes)
- `scripts/06_build_layer.py` (69,130 bytes)

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

### Files written by `scripts/08_build_gap_districts.py` (run 2026-10-10T18:10:47Z)

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

### Files written by `scripts/08_build_gap_panel.py` (run 2026-10-10T18:24:03Z)

- `50_gap/district_year_panel.csv` (59,379 bytes, sha256 `49012547ee8ec3f5`)
- `50_gap/panel_models.csv` (5,072 bytes, sha256 `a8c7ef7ef69aa7dd`)
- `50_gap/panel_models.txt` (4,986 bytes, sha256 `7bb227cc3eb69d7a`)
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

### Files written by `scripts/08_build_gap_units.py` (run 2026-10-10T18:25:35Z)

- `50_gap/unit_history.csv` (1,983,358 bytes, sha256 `6fe3a6f4a660f2b2`)
- `50_gap/unit_history_models.csv` (6,920 bytes, sha256 `f2684839d7db5310`)
- `50_gap/unit_history_models.txt` (6,823 bytes, sha256 `d5dbbde193f74211`)
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

### Files written by `scripts/08_build_gap_rights.py` (run 2026-10-10T18:11:24Z)

- `50_gap/fra_by_district.csv` (4,568 bytes, sha256 `37cf178731fafc68`)
- `50_gap/fra_summary.csv` (708 bytes, sha256 `cfbe515474ad9f4b`)
- `50_gap/fra_two_reports.csv` (310 bytes, sha256 `8630d58c44690c10`)
- `50_gap/forest_villages_text_layer_check.csv` (1,599 bytes, sha256 `dd77b52f5809ab48`)
- `50_gap/forest_villages_districts_as_the_layer_reads_them.csv` (1,644 bytes, sha256 `357a86c94d2d2b63`)
- `50_gap/forest_villages_pdf_record.json` (3,474 bytes, sha256 `299cc5135382f597`)
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

## Commits of this run, newest first

*Read from `git log` when this log was written; the commit that carries this very version of the log is the one after the newest listed.*

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
