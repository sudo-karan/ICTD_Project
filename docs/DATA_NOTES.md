# Verification log

What was checked, when, and how. Everything here was done on 4–5 October 2026.

## The four MIS reports supplied 5 Oct 2026

All four are Odisha, FY 2016-2017, confirmed from `state_name=` and `fin_year=` embedded in each row's
hyperlinks. All are HTML tables with a `.xls` extension.

| Report | Rows | Verdict |
|---|---|---|
| `nrm_works_report` | 7 districts, 9 blocks | **partial extract**, not state-wide. NRM 41.09 % of expenditure (₹1,384.35 lakh of ₹3,369.25 lakh); 12.25 % of works. No plantation split. |
| `road_plantation_rpt` | 30 districts | populated: 4,448.35 km, 1,549,272 plants, 2,054,770 beneficiaries. **Physical units only — no expenditure column.** |
| `tree_plantation_rpt` | 30 districts | **every numeric column zero.** |
| `maintenance_block_plantation_rpt` | 30 districts | 3 of 10 numeric columns entirely zero; only Bargarh reports anything (9.085 ha, 684 plants, 6 job-card holders). |

Every column of all four sums to its printed Total row after parsing.

**None of these is R6.20, and none resolves the plantation-expenditure question.** R6.20 carries
expenditure split by NRM / Water Related / All Plantation Works; these carry either NRM in aggregate
(9 blocks) or physical plantation counts with no money attached. R6.20 was scraped the same day — see
below. Note that `nrm_works_report` returning 7 districts / 9 blocks was not a partial export: it is the
MWC-Block default trap, trap 1 below.

## The PDF supplied 5 Oct 2026

`A_MPR_Dec_2025.pdf` is the **Ministry of Tribal Affairs national** FRA monthly progress report as on
31.12.2025 (M/o Tribal Affairs I.D. No.23011/3/2016-FRA dated 29 January 2026, Deputy Secretary
Ganesh Nagarajan). Nine pages, Canon scan, no text layer. It is **not** the Odisha state FRA MPR —
that is a separate two-page document from stsc.odisha.gov.in, already parsed into
`00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv`.

Page 3's state-wise table was transcribed by eye from a 150 dpi rasterisation into
`mota_fra_state_wise_2025-12-31.csv`. Seven of nine column totals reproduce the printed TOTAL exactly;
`extent_acres_individual` and `extent_acres_community` differ by +0.42 and −0.42 acres and cancel, so
the TOTAL column reconciles. That is 0.000002 % and is not in the Odisha row.

The Odisha row is independently confirmed: 808,280.06 acres community ÷ 2.47105 = 327,099 ha, and
Annexure-I on page 4 of the same report prints 327,100 ha.

### The two FRA reports disagree

| | Odisha state report | MoTA national report |
|---|---|---|
| Community titles | 9,432 | 9,352 |
| Community extent | 331,568 ha | 327,099 ha |
| Individual titles | 464,504 | 464,329 |

Same reference date. Differences of 80 titles, 4,469 ha (1.35 %) and 175 titles. Pick one for the paper,
cite it, and note the other.

## R6.20, scraped 5 Oct 2026 — 13 years, resolved

**What R6.20 actually is.** "Comprehensive Report on Plantation Maintenance, Progress and Green
Infrastructure Management", at `MISreport4.aspx` → R6.20. It has four tabs; the fourth,
*NRM / Water / All Plantation Works*, is the only one carrying expenditure. Everything below is that tab.

Scraped for all 13 financial years the portal offers (2014-15 … 2026-27) × 3 categories × 30 districts =
**1,170 district rows**, plus the 39 printed Total rows. `scripts/verify_r620.py` reconciles every one:
integer columns exact, money to 0.02 lakh. Jaskaran cleared the arithmetic CAPTCHA; the scrape ran in the
browser against the validated session.

**The question it was supposed to settle, settled.** There was no contradiction. 15.1 % is the asset
dump's FY2006-18 *pooled* plantation share; 0.63 % is R6.20's FY2024-25 share. Comparing them was the
error. Plantation collapsed after FY2017-18:

| FY | Plantation % of all exp. | FY | Plantation % |
|---|---|---|---|
| 2014-15 | 21.39 | 2020-21 | 0.03 |
| 2015-16 | 17.55 | 2021-22 | 0.01 |
| 2016-17 | 24.17 | 2022-23 | 0.02 |
| 2017-18 | 18.62 | 2023-24 | 0.03 |
| 2018-19 | 3.34 | 2024-25 | 0.63 |
| 2019-20 | 0.33 | 2025-26 | 0.54 |
| | | 2026-27 | 0.13 (part-year) |

**It is a collapse in count, not in unit cost.** 57,135 plantation works in FY2016-17 → 4,532 in
FY2024-25 (12.6×), while expenditure per work fell only ₹82,487 → ₹56,806 (1.45×). An earlier reading of
this file claimed ₹82,000/work → ₹3,700/work and floated accounting reclassification as the explanation;
that was drawn from FY2019-20 alone, the bottom of a five-year trough, and is **withdrawn**. Per-work
expenditure recovers to near its historic level by FY2024-25, so the fall in spending tracks a real fall
in the number of plantation works. The FY2019-20 … FY2023-24 window is its own anomaly (works on the
books at ₹1,586–6,718 each) and should not be read as five ordinary years.

**The result nobody was looking for: NRM became water.** Water as a share of NRM expenditure rises every
single year without exception — 40.1 % (2014-15), 39.8, 44.6, 41.3, 50.5, 50.9, 56.0, 58.0, 60.8, 62.0,
63.7, 77.8, 85.9 % (part-year 2026-27). NRM's share of all expenditure grew 42.8 % → 67.6 %, and the
growth went almost entirely into water works. The new Act's water expenditure floors (65/40/30 % by CGWB
groundwater category) codify a shift that was already nearly complete.

**What the asset dump can and cannot corroborate.** The dump is indexed by the year a work *started*
and attributes each work's whole lifetime expenditure to that year; R6.20 is indexed by the year money
was *spent*. Against R6.20's all-works total the dump captures 82.6 % of FY2014-15, 93.4 % of FY2015-16,
83.4 % of FY2016-17, 36.2 % of FY2017-18, then 3.2 %, 2.3 %, 0.6 %, 0.7 %, 0.6 %, 0.3 %, 0.1 %. So it
corroborates the plantation series only through FY2016-17 — where it does, closely: 18.1 % vs 17.6 %
(FY2015-16), 27.3 % vs 24.2 % (FY2016-17). Its post-FY2017-18 shares are computed on 0.1–3 % of the real
denominator and are not usable; an earlier note here treated the dump's FY2016-17 figure as a clean
validation of R6.20, which overstates it — the start-year/spend-year mismatch alone accounts for the gap.

**The trap that nearly produced a wrong number.** The three categories are nested, not a partition:
Water ≤ NRM in 390/390 district-year cells, Plantation ≤ NRM in 390/390. See README §5.6. Four of the
thirteen years (FY2014-18, the high-plantation ones) carry `last_updated = 10/10/2020` — a frozen
six-year-old snapshot. See README §5.7.

**Two scraper bugs worth recording**, both now encoded in `scripts/scrape_r620_mis.py`:
1. The report defaults to **MWC-Block**, a single block, not the whole state. Left alone it silently
   returns 9 blocks of Odisha. The "ALL" option is `Rbblk` value `0` at radio **index 4**, not index 0.
2. Calling `__doPostBack` on a radio without first setting its `.checked` property makes ASP.NET post the
   *previous* value. The first 13-year run came back with all three categories identical and every table
   stamped `Rbblk=4`, which is how the bug was caught — it looked like success.

## Publication constraints — check before anything is released

Recorded 6 October 2026 on the project owner's ruling. A licence in the manifest is a field; this is the rule
that follows from it.

**SHRUG (`00_raw/03_socioeconomic/shrug/`, two files).** Licence: **CC BY-NC-SA 4.0** — attribution,
**non-commercial**, **and share-alike**. The README inside the download adds a condition of its own: "Any
data that you link to the SHRUG must be posted with SHRUG identifiers at the time that your paper or project
is published. In the spirit of openness, you should post the all-India series if available, rather than just
the analysis sample."

What that touches here: the five SHRUG-derived columns of `30_need/need_by_unit.csv` — `poverty_rate`,
`poverty_rate_ppp2`, `poverty_rate_population_covered_share`, `poverty_rate_population_rated` and
`poverty_rate_shared_shrid_population_share` — and anything computed from them.

- Share-alike can propagate: a dataset that contains or is derived from SHRUG columns may itself have to be
  released under CC BY-NC-SA 4.0, which would bind the other columns travelling in the same file.
- Non-commercial applies to every use of such a dataset, including by whoever receives it.
- The posting condition applies to *other* data linked to SHRUG: releasing unit-level tables joined to these
  columns means posting them with SHRUG identifiers (`shrid2`), and the units here are LGD panchayat ids, not
  shrids.

**Rule: any released dataset, supplementary file or public demo must be checked against these terms before
it ships.** The fallback, if the terms cannot be met or there is any doubt: **keep the SHRUG-derived columns
out of the released artifact and cite them only in the paper.** The pipeline does not depend on them —
`st_share` is the marginalisation axis and `adi_2011` the development control — so dropping them from a
release loses a robustness reading and nothing else.

**The demo layer (`60_layer/`), 7 October 2026 — the fallback applied, and flagged.** The layer built for the Foundation for
Ecological Security is the first artifact of this project meant to leave the machine. On the project owner's
instruction the SHRUG-derived columns are **omitted from it**: `poverty_rate`, `poverty_rate_ppp2`, `poverty_rate_population_covered_share`, `poverty_rate_population_rated`, `poverty_rate_shared_shrid_population_share`.
They stay in `30_need/need_by_unit.csv` and in the analysis. `scripts/06_build_layer.py` stops if one of them, or
the word "poverty" outside the licence note, appears in the layer's files; `scripts/verify_layer.py` checks it again.
The layer's *Sources and licences* panel names SHRUG and its licence and says that no SHRUG-derived figure is
included. Three things follow that the owner should know before the layer is sent:

- **The unit shapes are a derived database under the ODbL.** They are built from DataMeet's village boundaries
  (ODbL 1.0), so `60_layer/data.js` may be shared, with attribution, under that licence and no narrower one. The
  panel says so. This binds the shapes; the figures attached to them are facts from other sources.
- **`adi_2011` is kept, and is the one judgement call.** The index's documentation says SHRUG's keys were used to
  link 2001 and 2011 villages. The 2011 index itself is computed from Census 2011 rows, and it is the project's
  development control, so it is in the layer. If the licence is read more strictly, drop it from the layer.
- **ISFR is cited in the panel but no ISFR figure is on the map**; its terms (non-commercial use with
  acknowledgment) are therefore not engaged by the layer.

**Brought up to date on 9 October 2026, for the decision view** (`docs/DECISION_LAYER.md` is the full account). The layer
now has a second way of reading its measurements, two more sources, and a copy made to be passed on. What the owner
should know before anything is sent:

- **The copy to send is `70_share/odisha_forest_decision_layer/`, not `60_layer/`.** `scripts/07_build_share.py` writes
  the layer's `index.html` and `data.js` there, leaves out `overlay.js`, adds a README, and zips the folder (the zip
  lies beside it in `70_share/`). Until 10 October 2026 the two files were the layer's byte for byte; since then the
  development index of 2011 is taken out of them (next point but three). The page in the copy asks the network for
  nothing: its box "Site-level overlay" says the overlay's file is not beside the page. `scripts/exercise_share.py`
  opens the copy in Chrome and checks that.
- **The tile provider.** In `60_layer/` the decision view can lay Hansen's loss over the map as tiles from Global Forest
  Watch (World Resources Institute). It is off unless ticked, and its code is the one file left out of the copy. Two
  points of the provider's terms are unresolved, and they are the owner's: the terms ask that each request to an API
  carry an account's key, and the tile service's reference declares none; and they bind a user to an attribution page
  written for another of the provider's services. Five of the provider's pages are registered in
  `00_raw/05_forest_reference/` (manifest rows `gfw_dataset_record_umd_tree_cover_loss`,
  `umd_global_forest_change_v1_13_page`, `gfw_terms_of_service_page`,
  `resourcewatch_api_attribution_requirements_page`, `gfw_tile_cache_api_reference_openapi`), and since
  10 October 2026 two more, the two the note on those unresolved points also quotes (`gfw_developer_help_page`,
  `gfw_api_key_guide_page`); they are fetched files and are not in git or in anything sent.
- **The provider's cautions about the data are quoted in the layer** whether or not the overlay is there: short
  quotations from the provider's record of the dataset, kept in `00_raw/05_forest_reference/provider_cautions.json`
  with their source. The data itself is CC BY 4.0. The two pages registered on 10 October 2026 carry the provider's
  help text, and in it cautions the first extract does not have (accuracy lowest in sub-tropical areas; small-holder
  disturbance often missed; the detection method changed in 2015). They are kept, word for word, in a second, dated
  file beside the first, `provider_cautions_2026-10-10.json`; the first is committed and was not edited.
- **The Gazette's list of permissible works.** The decision view names rows of the list notified as S.O. 5448(E) of 5
  October 2026 (`00_raw/06_scheme/`, five manifest rows). It quotes work names and serial numbers. No licence is
  stated for the Gazette; the manifest records what the eGazette site says of it. The PDFs and the Ministry's press
  release are fetched files and are not in git or in anything sent; the table made from the list is.
- **`adi_2011` and the exported list.** By the owner's ruling of 9 October 2026 the development index is no longer a
  column of the list a user can export from the decision view, because that file is the one that gets passed on. It
  is still in the interactive view of `60_layer/`, as a layer and as a column of the list on the page. **Since
  10 October 2026 it is no longer in the copy that is passed on** (`70_share/odisha_forest_decision_layer/`): the
  script that builds the copy takes out the field and everything that displays it, the gate on the copy fails if the
  index's id or name is found in the copy's two files, and the copy's README says the index is not in it. No file
  that is passed on now carries `adi_2011` for a unit. This was a call made with the instruction that opened stage 4
  and can be reversed (`docs/DECISION_LAYER.md` §17.3). The judgement above stands for the view in `60_layer/`: a
  stricter reading of SHRUG's terms would take it out of the layer too. District-level results that stage 4 builds
  from the index (`docs/GAP.md`) are analysis, not the column; wherever they appear they carry the index's source and
  licence as the layer's own list of sources gives them.
- **Scheduled Tribe share in a list that is passed on** is the Foundation's call (`docs/DECISION_LAYER.md` §17). It
  is in the exported list.
- **The copy is published.** On 11 October 2026 the project owner decided to publish it, without a password, at
  https://sudo-karan.github.io/ICTD_Project/. It was first published that day from a branch `gh-pages`, which held the
  copy's three files and no other file of the repository. By his decision of the same day the repository has one
  branch, `main`, and since 12 October 2026 GitHub Pages deploys the site from the folder `site/` of `main`, through
  the workflow `.github/workflows/pages.yml`: `scripts/publish_site.sh` fills `site/` with the copy's three files, and
  nothing else, and pushes `main`; `gh-pages` is deleted. The README inside `70_share/odisha_forest_decision_layer/`
  gives the address and says that each source keeps its own licence; until 11 October 2026 it said that terms for
  passing the copy on were not yet agreed and asked that it not be passed on or published.
  `scripts/check_pages_live.py` checks what the site serves, and what `site/` holds, against the build;
  `70_share/pages_publication.json` records the commits and the check.

Not decided here: whether the layer may be passed on by the Foundation to others, and under what statement.

**Other terms on file** (from `00_raw/data_manifest.csv`; none of these files is redistributed by the
pipeline, only figures read from them):

| source | terms as recorded |
|---|---|
| India State of Forest Report 2023 (Forest Survey of India) | "The contents of the bulletin may be used for non-commercial purposes with due acknowledgment. All rights reserved." |
| Global Forest Watch country workbook | no licence stated in the workbook; asks for citation of Hansen et al. 2013, Harris et al. 2021 and GADM 3.6 |
| ATREE CFR-potential village list | no licence stated at the link or in the workbook |
| MGNREGA MIS reports, asset dump | Government of India; no licence stated, GODL assumed for NIC-hosted data |

The licences of the Earth Engine sources used in stage 1 are in `docs/DEGRADATION.md`.

## Environment notes

- Stage 1 needs `earthengine-api` (1.7.46 is in `.venv`) and an authenticated Earth Engine project; the
  scripts read the project from `~/.config/earthengine/credentials`.
- On 5 October 2026 hostname lookups failed inside one working session (`curl` exit 6, "No DNS configuration
  available") while `dig` still answered. The cause was the session's process sandbox, not macOS: the Mac's
  resolver was healthy throughout and nothing on the machine needs fixing. An earlier note that blamed the
  system resolver was wrong.

## Still outstanding

- VGPP schedule of rates — plantation ₹/ha.
- Whether Annexure-A of the order of 22 May 2026 (No. J-11060/12/2026-RE-III) carries per-GP A/B/C grades
  or only the formula.
- 30 district headquarters coordinates, for the remoteness control.
