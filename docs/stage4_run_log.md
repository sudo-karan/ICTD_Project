# Stage 4: the run log

*Written 2026-10-10T11:15:55Z by `scripts/write_stage4_run_log.py`. The gate tables, the lists of files and the package versions are read from the files named beside them; the notes are typed and carry no figure of the analysis. The owner's prompt of 10 October 2026 set nine phases, 0 to 8, each ending in a commit.*

## Where the run stands

Phases written up below: 0. The last is Phase 0, inputs, crosswalk, gates. Every gate of every phase listed passed.

The stage outputs (`50_gap/`, `figures/stage4/`) are not in git. If they are missing, rebuild them: the section "To rebuild" at the end gives the order.

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

**The environment.** The repository had no requirements file; `requirements.txt` was written, pinned. Installing
`numba`, which `wildboottest` needs, moved `numpy` down, because the newest `numba` with a wheel for this machine does
not take the `numpy` that was installed. The verifiers that existed were run again after the install and gave the
counts they gave before (the table under "The environment" below).

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

### Files written by `scripts/08_gap_inputs.py` (run 2026-10-10T11:15:55Z)

- `50_gap/inputs_listing.json` (18,145 bytes, sha256 `2d95552d9feebac5`)
- `50_gap/district_crosswalk.csv` (1,392 bytes, sha256 `8a127601ce0254c8`)
- `50_gap/unit_district.csv` (630,249 bytes, sha256 `2a76e6ed9d5977a8`)
- `50_gap/inputs_check.csv` (3,941 bytes, sha256 `524cc7de7a83aa12`)

### The environment

`pip freeze` before the install of 10 October 2026 and after it (`50_gap/environment_before_stage4.txt`, `50_gap/environment_after_install.txt`). Packages not listed did not change.

| package | before | after |
|---|---|---|
| contourpy | not installed | 1.4.0 |
| cycler | not installed | 0.12.1 |
| fonttools | not installed | 4.66.1 |
| formulaic | not installed | 1.2.2 |
| interface_meta | not installed | 2.0.1 |
| kiwisolver | not installed | 1.5.1 |
| llvmlite | not installed | 0.45.1 |
| matplotlib | not installed | 3.11.2 |
| numba | not installed | 0.62.1 |
| numpy | 2.5.3 | 2.3.5 |
| patsy | not installed | 1.0.3 |
| pillow | not installed | 12.3.0 |
| statsmodels | not installed | 0.15.0 |
| tabulate | not installed | 0.10.0 |
| wildboottest | not installed | 0.3.2 |
| wrapt | not installed | 2.5.0 |

The verifiers that existed, run again after the install:

| verifier | its last line or its line of success |
|---|---|
| `scripts/verify_r620.py` | OK  1170 district rows reconcile to all 39 printed Total rows |
| `scripts/verify_agreement.py` | 41 of 41 checks passed; n = 11,468 units, 2,891 assessed at 100 ha, 2,423 in the headline population |
| `scripts/verify_layer.py` | 92 of 92 checks passed; n = 11,468 units, 44 fields a unit, 18 class arrays |
| `scripts/verify_decision.py` | 61 of 61 checks passed; n = 11,468 units, 4 windows, 6 cells, 30 districts |

### Inputs read, with their columns

*Listed 2026-10-10T11:15:53Z by `scripts/08_gap_inputs.py` (`50_gap/inputs_listing.json`, which also has each file's SHA-256).*

- `00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv` (73,503 bytes; 1,170 rows): `fy`, `category`, `district`, `blocks`, `works_ongoing`, `works_completed`, `pct_works`, `exp_cat_lakh`, `exp_all_lakh`, `pct_exp`
- `00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv` (2,958 bytes; 39 rows): `fy`, `category`, `blocks`, `works_ongoing`, `works_completed`, `pct_works`, `exp_cat_lakh`, `exp_all_lakh`, `pct_exp`, `last_updated`
- `00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` (6,289 bytes; 30 rows): `district`, `pc11_district_code`, `frcs_constituted`, `claims_filed_gs_ind_st`, `claims_filed_gs_ind_otfd`, `claims_filed_gs_comm_st`, `claims_filed_gs_comm_otfd`, `claims_filed_gs_total_st`, `claims_filed_gs_total_otfd`, `claims_gs_to_sdlc_ind_st`, `claims_gs_to_sdlc_ind_otfd`, `claims_gs_to_sdlc_comm_st`, `claims_gs_to_sdlc_comm_otfd`, `claims_gs_to_sdlc_total_st`, `claims_gs_to_sdlc_total_otfd`, `claims_sdlc_to_dlc_ind_st`, `claims_sdlc_to_dlc_ind_otfd`, `claims_sdlc_to_dlc_comm_st`, `claims_sdlc_to_dlc_comm_otfd`, `claims_sdlc_to_dlc_total_st`, `claims_sdlc_to_dlc_total_otfd`, `claims_approved_dlc_ind_st`, `claims_approved_dlc_ind_otfd`, `claims_approved_dlc_comm_st`, `claims_approved_dlc_comm_otfd`, `claims_approved_dlc_total_st`, `claims_approved_dlc_total_otfd`, `titles_distributed_ind_st`, `titles_distributed_ind_otfd`, `titles_distributed_comm_st`, `titles_distributed_comm_otfd`, `titles_distributed_total_st`, `titles_distributed_total_otfd`, `extent_ha_ind_st`, `extent_ha_ind_otfd`, `extent_ha_comm_st`, `extent_ha_comm_otfd`, `extent_ha_total_st`, `extent_ha_total_otfd`, `claims_rejected_ind_st`, `claims_rejected_ind_otfd`, `claims_rejected_comm_st`, `claims_rejected_comm_otfd`, `claims_rejected_total_st`, `claims_rejected_total_otfd`
- `00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv` (2,273 bytes; 21 rows): `state`, `claims_received_individual`, `claims_received_community`, `claims_received_total`, `titles_distributed_individual`, `titles_distributed_community`, `titles_distributed_total`, `extent_acres_individual`, `extent_acres_community`, `extent_acres_total`, `extent_ha_individual`, `extent_ha_community`, `extent_ha_total`
- `00_raw/data_manifest.csv` (59,778 bytes; 92 rows): `item_id`, `group`, `priority`, `title`, `kind`, `ref`, `bytes`, `bytes_exact`, `dest`, `licence_or_terms`, `how_verified_2026_10_04`, `notes`
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
- `docs/DATA_NOTES.md` (15,524 bytes)
- `docs/NEED.md` (19,029 bytes)
- `00_raw/docs/Village_level_dataset_schema_31Oct2022.docx` (637,132 bytes)
- `scripts/06_build_layer.py` (69,130 bytes)

## To rebuild

Each builder writes into `50_gap/` only and stops at the first gate that fails. In order:

```
.venv/bin/python scripts/08_gap_inputs.py            # Phase 0
.venv/bin/python scripts/08_build_gap_districts.py   # Phase 2
.venv/bin/python scripts/08_build_gap_panel.py       # Phase 3
.venv/bin/python scripts/08_build_gap_units.py       # Phase 4
.venv/bin/python scripts/08_build_gap_rights.py      # Phase 5
.venv/bin/python scripts/verify_gap.py               # Phase 6
.venv/bin/python scripts/08_build_gap_deck_tables.py # Phase 7
.venv/bin/python scripts/make_stage4_figures.py      # Phase 7
.venv/bin/python scripts/write_gap.py                # Phase 8
.venv/bin/python scripts/write_stage4_run_log.py
```

A script named above that does not exist yet belongs to a phase that has not been reached.
