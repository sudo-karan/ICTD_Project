# The demo layer — `60_layer/`

*Built by `scripts/06_build_layer.py` (run 2026-10-12T22:00:54Z) from the stage tables named below; page in
`scripts/layer_template.html`; checked by `scripts/verify_layer.py`. Every figure in this document is from
`60_layer/layer.provenance.json`, a table it names, or the check record. n = 11,468 units throughout:
3,492 outside-village units and 7,976 LGD panchayat units.*

It is one map of what stages 1, 2 and 3 hold, for every unit, made to be opened by the Foundation for Ecological
Security. It needs no stage 4 and no NIRv, and it argues nothing: it shows what the tables say, unit by unit.

## 1. What is in the folder, and how to open it

| file | bytes | what |
|---|---|---|
| `index.html` | 214,465 | the map. Leaflet 1.9.4 (BSD 2-Clause) is inside it |
| `data.js` | 23,213,146 | the unit shapes and every value and class the map shows; since 13 October 2026 also the guide, with its five pictures (§13). Keep it beside `index.html` |
| `layer_by_unit.csv` | — | the numbers the map shows, one row per unit, 79 columns. Not needed to view the map |
| `layer.provenance.json` | — | inputs with hashes, the UTC run time, the simplification and its error, classes, checks |
| `overlay.js` | 1,213 | since 8 October 2026: the code of the decision view's optional online overlay, and nothing else. Not needed to view the map; **left out of the copy that is passed on** (§11) |

**To open: double-click `index.html`.** The two files together are 23,427,611 bytes (23.43 MB; the limit set was
25 MB) and 6.70 MB zipped, so they can be e-mailed as one zip. The page makes **0 network
requests**: no map tiles, no fonts, no library fetched. It will open the same way with no connection, and in two
years. (That is this folder, opened from disk. The copy on the website reaches its reader over the internet, and once
it has loaded asks no other site for anything: §11.) **One exception was added on 8 October 2026, and it is off unless ticked**: in the decision view a box can lay
Hansen's loss over the map as tiles from an outside server; its code is in the third file, `overlay.js`, which the page
asks for only on that tick (§11). There is consequently no base map under the units — district outlines and names, drawn from the units
themselves, are the only orientation.

An address can point at a view, for sending someone to a place: `index.html#layer=agreement&unit=OUTSIDE_183`. The
parts, all optional: `layer=` (ids in §2), `floor=100|50|1`, `unit=` an id, `show=lgd|out|both|none`, `district=` a
district's name, `q=` text for the search box, `open=about|sources|guide`. A part the page does not understand is ignored and
the default is used.

## 2. What it shows

| layer (as titled on the map) | what is drawn | from | land a unit must have to be assessed |
|---|---|---|---|
| Forest in 2000 (Hansen) | `forest_ha` / `area_ha` | `degradation_by_unit.csv`, `units.gpkg` | none: it is the layer that shows who has forest |
| Tree cover loss since 2001 (Hansen) | `hansen_loss_ha` / `forest_ha` | `degradation_by_unit.csv` | forest (`treecover2000` > 30) |
| Loss on open canopy (Hansen) | `hansen_loss_ha_tc_gt10le30` / `land_ha_tc_gt10le30` | `degradation_by_unit.csv` | land with 10 < `treecover2000` ≤ 30 |
| Degradation 2017-2023 (CoRE Stack) | class −1 / land with a class, on `treecover2000` > 10 | `corestack_by_unit_bands.csv` | the smaller of that land on the two grids |
| Degradation minus improvement (CoRE Stack) | (class −1 − class 1) / land with a class, on `treecover2000` > 10 | `corestack_by_unit_bands.csv` | the same |
| Hansen and CoRE Stack compared | `agreement_class` (headline window 2017–2023) | `agreement_by_unit.csv` | its own: 100 ha of reference land on both grids, fixed |
| MGNREGA spending, all works | `expenditure_total`, in ₹ lakh | `allocation_by_unit.csv` | — |
| MGNREGA spending on forest works | `expenditure_forest_named_worktype`, in ₹ lakh | `allocation_by_unit.csv` | — |
| Scheduled Tribe share | `st_share` | `need_by_unit.csv` | — |
| Aggregate Development Index 2011 | `adi_2011` | `need_by_unit.csv` | — |
| Greenness trend (NIRv) | nothing: the entry is greyed and marked "tested, not used", with an "i" that says what was tested and why it is not used. NIRv is not a measure (ruling of 7 October 2026, `docs/RESULTS.md` §6) | — | — |

Clicking a unit opens a panel with 44 fields: its name, type and district; area; forest and loss; loss by canopy
band; the six CoRE Stack classes as areas and shares; the agreement class and the two rates behind it; works and
expenditure; and the Census 2011 figures. Units can be filtered by type and district and found by name or id.

### Classes, with the number of units in each

The same counts are in the map's legend. Every table adds up to 11,468.

**Forest in 2000 (Hansen)**

| class | units |
|---|---|
| No forest by this measure | 4,310 |
| Up to 1 % | 3,036 |
| 1 to 10 % | 1,663 |
| 10 to 30 % | 1,062 |
| 30 to 60 % | 917 |
| More than 60 % | 480 |
| **all units** | **11,468** |

**Tree cover loss since 2001 (Hansen)**

| class | units, floor 100 ha | units, floor 50 ha | units, floor 1 ha |
|---|---|---|---|
| No loss recorded | 142 | 263 | 1,632 |
| Up to 1 % | 755 | 912 | 1,131 |
| 1 to 2.5 % | 269 | 340 | 539 |
| 2.5 to 5 % | 222 | 281 | 461 |
| 5 to 10 % | 284 | 350 | 544 |
| 10 to 20 % | 277 | 342 | 526 |
| More than 20 % | 118 | 147 | 370 |
| Insufficient forest to assess | 9,401 | 8,833 | 6,265 |
| **all units** | **11,468** | **11,468** | **11,468** |

**Loss on open canopy (Hansen)**

| class | units, floor 100 ha | units, floor 50 ha | units, floor 1 ha |
|---|---|---|---|
| No loss recorded | 391 | 728 | 5,176 |
| Up to 1 % | 895 | 1,140 | 1,490 |
| 1 to 2.5 % | 267 | 351 | 627 |
| 2.5 to 5 % | 185 | 257 | 488 |
| 5 to 10 % | 220 | 263 | 477 |
| 10 to 20 % | 120 | 160 | 316 |
| More than 20 % | 54 | 79 | 187 |
| Insufficient forest to assess | 9,336 | 8,490 | 2,707 |
| **all units** | **11,468** | **11,468** | **11,468** |

**Degradation 2017-2023 (CoRE Stack)**

| class | units, floor 100 ha | units, floor 50 ha | units, floor 1 ha |
|---|---|---|---|
| Up to 5 % | 529 | 881 | 3,970 |
| 5 to 15 % | 1,010 | 1,274 | 2,446 |
| 15 to 25 % | 749 | 869 | 1,223 |
| 25 to 35 % | 407 | 456 | 565 |
| More than 35 % | 196 | 231 | 320 |
| Insufficient forest to assess | 8,577 | 7,757 | 2,944 |
| **all units** | **11,468** | **11,468** | **11,468** |

**Degradation minus improvement (CoRE Stack)**

| class | units, floor 100 ha | units, floor 50 ha | units, floor 1 ha |
|---|---|---|---|
| Net improvement, more than 10 points | 650 | 913 | 2,229 |
| Net improvement, 2 to 10 points | 559 | 749 | 1,903 |
| Within 2 points: no net change | 378 | 518 | 2,000 |
| Net degradation, 2 to 10 points | 625 | 740 | 1,300 |
| Net degradation, 10 to 20 points | 358 | 416 | 585 |
| Net degradation, more than 20 points | 321 | 375 | 507 |
| Insufficient forest to assess | 8,577 | 7,757 | 2,944 |
| **all units** | **11,468** | **11,468** | **11,468** |

**Hansen and CoRE Stack compared**

| class | units |
|---|---|
| Both measures flag this unit | 137 |
| Hansen only (clearance) | 348 |
| CoRE Stack only (degradation) | 348 |
| Neither | 1,590 |
| East Coast zone model: left out of the headline comparison | 468 |
| Insufficient forest to assess | 8,577 |
| **all units** | **11,468** |

**MGNREGA spending, all works**

| class | units |
|---|---|
| Up to Rs 10 lakh | 1,522 |
| Rs 10 to 50 lakh | 2,691 |
| Rs 50 to 100 lakh | 1,997 |
| Rs 100 to 200 lakh | 2,142 |
| Rs 200 to 400 lakh | 1,544 |
| More than Rs 400 lakh | 515 |
| No works geotagged here | 1,048 |
| Works recorded, expenditure not | 9 |
| **all units** | **11,468** |

**MGNREGA spending on forest works**

| class | units |
|---|---|
| Up to Rs 1 lakh | 850 |
| Rs 1 to 5 lakh | 1,042 |
| Rs 5 to 20 lakh | 754 |
| More than Rs 20 lakh | 127 |
| None | 8,667 |
| Works recorded, expenditure not | 28 |
| **all units** | **11,468** |

**Scheduled Tribe share**

| class | units |
|---|---|
| Less than 18 % | 4,028 |
| 18 to 33 % | 814 |
| 33 to 50 % | 848 |
| More than 50 % | 2,163 |
| No census data for this land | 3,492 |
| No resident population in the census rows | 123 |
| **all units** | **11,468** |

**Aggregate Development Index 2011**

| class | units |
|---|---|
| Up to 6 | 1,427 |
| 6 to 7 | 2,039 |
| 7 to 8 | 1,279 |
| 8 to 9.5 | 789 |
| More than 9.5 | 1,908 |
| No census data for this land | 3,492 |
| No index for this unit's villages | 534 |
| **all units** | **11,468** |

### Missingness

Blank cells of `layer_by_unit.csv` — a blank is shown on the map in words, never as 0:

| column | units with no value |
|---|---|
| `hansen_loss_pct_of_forest` | 4,310 |
| `hansen_loss_pct_of_land_tc_gt10le30` | 741 |
| `corestack_loss_pct` | 808 |
| `corestack_degradation_pct` | 808 |
| `corestack_partial_degradation_pct` | 808 |
| `corestack_no_change_pct` | 808 |
| `corestack_improvement_pct` | 808 |
| `corestack_gain_pct` | 808 |
| `corestack_net_pct` | 808 |
| `corestack_zone_model` | 808 |
| `agreement_hansen_rate_2017_2023_pct` | 702 |
| `agreement_corestack_degradation_rate_pct` | 808 |
| `expenditure_total` | 9 |
| `expenditure_plantation_category` | 33 |
| `expenditure_forest_named_worktype` | 28 |
| `expenditure_water` | 9 |
| `expenditure_total_lakh` | 9 |
| `expenditure_plantation_category_lakh` | 33 |
| `expenditure_forest_named_worktype_lakh` | 28 |
| `expenditure_water_lakh` | 9 |
| `population` | 3,492 |
| `households` | 3,492 |
| `st_pop` | 3,492 |
| `sc_pop` | 3,492 |
| `adi_2011` | 4,026 |
| `st_share_pct` | 3,615 |
| `sc_share_pct` | 3,615 |

The census columns are blank for the 3,492 outside-village units by construction. A share on forest land is blank where the
unit has none of that land. Expenditure is blank where works are geotagged in the unit but none carries an amount.

## 3. Honest colour

(The page's own names for the first rule are "Minimum forest", over the choice on the side panel, and "Small forests
are greyed out", in *About this map*. Until 11 October 2026 both read "Honest colour".)

1. **Too little forest is a class, not a colour on the scale.** A loss rate on a few hectares is noise. In
   `20_degradation/forest_floor_repeatability.csv` the rank correlation of a unit's Hansen loss rate between odd and
   even years is 0.34 for units with 1 to 2 ha of forest, 0.77 with 25 to 50 ha, 0.81 with 50 to 100 ha, 0.89 with
   100 to 250 ha and 0.94 with 500 to 1,000 ha. So on
   every layer that is a rate on forest land a unit below a minimum of that land is drawn flat grey, **"insufficient
   forest to assess"**. The map offers three minimums: **100 ha, the default — the floor the project owner ruled on
   7 October 2026** — and 50 ha and 1 ha, to see what the stricter floor hides. On the Hansen layer 9,401 units are
   grey at 100 ha, 8,833 at 50 ha and 6,265 at 1 ha. The agreement layer has its own floor, fixed at
   100 ha of reference land on both grids (8,577 units insufficient), and a class of its own for the
   468 units left out of the headline comparison because their land lies wholly under CoRE Stack's East Coast
   zone model (`docs/RESULTS.md` §5.2; `docs/DEGRADATION.md` §4b).
2. **Outside-village units have no census rows.** On the two census layers all 3,492 read **"no census data for this
   land"**, hatched and in a colour that is not on the scale — never blank and never zero.
3. **Outside-village units are hatched on every layer**, so the two kinds of unit can always be told apart.
4. **A class follows the printed figure.** A unit is classed on its value rounded to the two decimals shown, so the
   number in the panel and the class in the legend can never disagree at a boundary.
5. **Flags are relative.** "Both measures flag this unit" means it is in the worst fifth of the assessed units on
   each measure, not that it lost some stated amount (`docs/DEGRADATION.md` §4b).

## 4. The shapes: tolerance, and the area error it introduces

The 11,468 unit polygons tile the layer with no gaps or overlaps. They were simplified **as a coverage** — a shared
boundary is simplified once, so neighbours still meet — with a **tolerance of 30 metres** in EPSG:32645, and stored
to 1e-05 degree (about a metre).

| | |
|---|---|
| vertices before → after | 2,447,144 → 1,232,815 |
| change in total area | -0.00001 % |
| change in one unit's area, absolute: median | 0.022 % |
| 95th percentile | 0.39 % |
| 99th percentile | 5.2 % |
| largest | 18.2 % |
| units whose area changes by more than 5 % | 120 of 11,468; the largest of them is 71.1 ha, the median 3.51 ha |
| units that would have vanished and were kept unsimplified | 0 |

The error falls on small units: the 120 that change by more than 5 per cent are slivers of a few hectares.
**No figure on the map is measured from these shapes.** Every area shown is the stage table's, computed from the
unsimplified polygons on the WGS84 ellipsoid; the simplified shape is only what is drawn. Do not measure from the map.

## 5. Where the numbers come from

Every value in the panel is a cell of `layer_by_unit.csv`, and every cell of that table is either copied from a stage
table or is a share or a conversion to ₹ lakh computed in `06_build_layer.py` from two cells of one. They are
formatted as text in Python. **The page's script looks text up and draws; it works out no figure** — no sum, no share,
no rounding. What it counts, and nothing else: the rows of a ranked list, the units a filter leaves out, the matches
of a search, and a tier's place in the order in use. (Until 11 October 2026 this document, and a note on the page,
said the page computes nothing; the page's *About this map* now says what it counts.) Inputs of the run:

| input | bytes | SHA-256 |
|---|---|---|
| `10_units/units.gpkg` | 48,369,664 | `ee86f0c3ac99c0c4…` |
| `00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` | 6,289 | `a2e2cc9c7df1a9b1…` |
| `10_units/outside_village_district.csv` | 536,828 | `763630369d3a544c…` |
| `20_degradation/degradation_by_unit.csv` | 3,628,329 | `072e281b53087823…` |
| `20_degradation/corestack_by_unit_bands.csv` | 2,902,891 | `d59e23e87b62c37b…` |
| `20_degradation/agreement_by_unit.csv` | 2,551,239 | `c8a7dc67a24b25fa…` |
| `30_need/need_by_unit.csv` | 1,212,483 | `0fc54bd7eb2a6d84…` |
| `40_allocation/allocation_by_unit.csv` | 1,072,899 | `3f81d2d3edefda9f…` |
| `20_degradation/hansen_by_unit_level.csv` | 1,090 | `46d77ed69eac08ca…` |
| `20_degradation/forest_floor_options.csv` | 1,671 | `10fd206612c3c538…` |
| `20_degradation/agreement.provenance.json` | 10,756 | `0c0182e3a357255c…` |
| `20_degradation/forest_floor_repeatability.csv` | 991 | `800c61adc7c22132…` |
| `20_degradation/agreement_summary.csv` | 32,470 | `6e0fb5e26102e318…` |
| `20_degradation/agreement_by_zone.csv` | 1,995 | `df07ed89f94db597…` |
| `20_degradation/agreement_floor_repeatability.csv` | 1,277 | `656d67107fd39010…` |
| `40_allocation/panchayat_of_record_check.csv` | 363 | `f36e1bd24b73ce67…` |
| `10_units/units.provenance.json` | 1,706 | `7a7aa9077c79b68d…` |
| `docs/GUIDE.md` | 36,840 | `90c1b4ec636624be…` |
| `docs/guide/01_page.webp` | 109,134 | `e62e3a92824a84f9…` |
| `docs/guide/05_note.webp` | 111,858 | `885ecbc104aea72f…` |
| `docs/guide/02_unit_panel.webp` | 164,222 | `5f034f257efa9af7…` |
| `docs/guide/03_decision_view.webp` | 127,672 | `171c2b9042385d16…` |
| `docs/guide/04_why_this_tier.webp` | 147,802 | `05d92a8cf6447f1f…` |
| `10_units/outside_village_district.provenance.json` | 7,734 | `e5e02aa04ca51004…` |
| `20_degradation/hansen.provenance.json` | 8,637 | `d6e816740e7dd41a…` |
| `20_degradation/corestack.provenance.json` | 12,320 | `8f03282fa339d4a3…` |
| `20_degradation/forest_floor.provenance.json` | 1,891 | `3691b99a971dda8c…` |
| `30_need/need.provenance.json` | 15,023 | `8024375c3a69546b…` |
| `40_allocation/allocation.provenance.json` | 15,953 | `bf1e7052fa4ba2c7…` |
| `55_decision/decision.provenance.json` | 25,625 | `d62a8eb63f364179…` |
| `55_decision/condition_by_unit.csv` | 7,275,979 | `f5f8a218e86a16b7…` |
| `55_decision/tiers.csv` | 3,015 | `a7a7db34b7bcb90f…` |
| `55_decision/work_types.csv` | 5,133 | `f6d27c0a66b4100a…` |
| `55_decision/condition_cells.csv` | 10,888 | `92687a08c37e4098…` |
| `55_decision/condition_sensitivity.csv` | 9,850 | `a4e2bc786ec2593b…` |
| `55_decision/condition_boundary.csv` | 587 | `0ba2695976dfb3e7…` |
| `55_decision/condition_threshold_evidence.csv` | 15,901 | `6660628f5c963bed…` |
| `55_decision/condition_share.csv` | 3,133 | `dd81a6e4adf06933…` |
| `00_raw/05_forest_reference/provider_cautions.json` | 11,359 | `018923092e50c3d6…` |
| `55_decision/work_rows_naming_forest.csv` | 2,055 | `a1c52ae8265c0c5c…` |
| `scripts/layer_overlay.json` | 8,357 | `61000c5a09259cf5…` |
| `scripts/layer_overlay.js` | 941 | `7d3c8a2a576ac05a…` |

The builder stops unless: the class counts above equal the stage tables' own counts (units with no forest, under
1 ha, under 50 ha and under 100 ha; the six agreement classes; the units with no census rows); forest and loss total what the
Hansen table totals (26,630.4 and 1,552.6 km²); every unit has a shape and a district; the simplified
shapes are still a valid coverage; no SHRUG-derived column is present; nothing in the page or the data refers to
the network; and the two files are under the size limit.

## 6. Vocabulary and conventions

Matched, where it could be, to the layers of Commons Connect and Know Your Landscape (CoRE Stack) that the
Foundation's teams already read:

- CoRE Stack's own class names and colours for tree cover change — Deforestation, Degradation, Partially Degraded,
  No Change, Improvement, Afforestation — and its framing of degradation as a share of tree-covered land.
- Scheduled Tribe share in Know Your Landscape's bins, under 18, 18 to 33 and over 33 per cent, with one more break
  at 50.
- Plain outlines for administrative units. Until 11 October 2026 two layers also carried names of that vocabulary,
  "Area under forests" and "Forest health and degradation"; by the owner's words of that day they are named for what
  they draw, "Forest in 2000 (Hansen)" and "Degradation 2017-2023 (CoRE Stack)". *About this map* still says "forest
  health and degradation (CoRE Stack)" of the second.

Where it departs, and why:

- **Deforestation and Afforestation will not match CoRE Stack's published block rasters.** Those take the two outer
  classes from a land-use change product; this layer reads all classes from the tree-change asset itself
  (`docs/DEGRADATION.md` §4a). Degradation, Partially Degraded, No Change and Improvement are the same thing.
- The unit is the **LGD panchayat unit or a tract of land outside every village**, not a micro-watershed or a
  tehsil; and a unit polygon is not the panchayat of record for the works inside it (README §5.8).
- Past allocation is the geotagged asset record, which effectively ends with works started in FY2017-18
  (`docs/RESULTS.md` §8). It is what was built where, not what is being spent now.

## 7. Licences, and what was left out

The map's *Sources* panel lists each of these with its terms:

| what | source | licence or terms |
|---|---|---|
| tree canopy 2000, tree cover loss 2001–2025 | Hansen et al., Global Forest Change v1.13, through Google Earth Engine; the state's canopy of 2000 and its loss for 2001–2020 reconciled to Global Forest Watch's published figures, which stop at 2020 | CC BY 4.0 |
| forest cover of Odisha, as a comparison only — no figure of it is on the map | Forest Survey of India, India State of Forest Report 2023 | © Forest Survey of India |
| tree cover change 2017–2023 | CoRE Stack | CC BY 4.0 |
| population, households, Scheduled Tribe and Scheduled Caste population | Census of India 2011 | Government of India |
| Aggregate Development Index 2011 | ICTD group, IIT Delhi, from Census 2011 | CC BY 4.0 |
| MGNREGA works and expenditure | Ministry of Rural Development: geotagged assets and MIS report R6.20 | Government of India public data |
| unit boundaries | DataMeet Community, Indian village boundaries | **ODbL 1.0** |
| poverty rate — **not in the layer** | SHRUG 2.2, Development Data Lab | **CC BY-NC-SA 4.0** |

**SHRUG-derived columns are omitted from the layer, on the project owner's instruction of 7 October 2026**:
`poverty_rate`, `poverty_rate_ppp2`, `poverty_rate_population_covered_share`, `poverty_rate_population_rated`, `poverty_rate_shared_shrid_population_share`. SHRUG's licence is non-commercial and share-alike, and a file
handed to another organisation that carried its estimates could become a derived work under it. The columns remain
in `30_need/need_by_unit.csv` and in the analysis. The builder fails if one of them appears in the layer.

**To flag, not decided here:**

- The unit shapes are derived from DataMeet's boundaries, so `data.js` is a derived database under the **ODbL**:
  it may be shared, with attribution, under the same licence. The panel says so.
- The Aggregate Development Index's documentation says SHRUG's keys were used to link 2001 and 2011 villages. The
  2011 index shown is computed from Census 2011 rows, and it is kept; if the owner reads the licence more strictly,
  dropping `adi_2011` is one line in `06_build_layer.py`. Since 10 October 2026 the copy that is passed on (§11) leaves
  the index out; this folder keeps it.

- **Added with the decision view (§11).** The optional overlay draws tiles from Global Forest Watch (World Resources Institute); the data in them is
  Hansen/UMD Global Forest Change v1.13, CC BY 4.0, and two points of the provider's terms of use (https://globalnaturewatch.org/terms/) are unresolved, which
  is why the copy made to be passed on has no overlay. The decision view quotes the provider's cautions about the data
  from its record of the dataset, and names rows of the Gazette's list of permissible works (Ministry of Rural Development notification S.O. 5448(E), 5 October 2026; Gazette of India, Extraordinary, Part II, Section 3(ii), No. 5238; Gazette ID CG-DL-E-05102026-276796); no licence is
  stated for the Gazette. The pages and the Gazette's files are registered in `00_raw/` with manifest rows and are not
  in the layer.

## 8. How it was verified

A map that renders is not a map that is correct. It was checked three ways: every unit by script; every control in two
browser engines; and, in the Safari application itself, every state that can be reached through the address.

**The Safari application was not opened on this build.** The runner's record of this build names that check as left out and gives the reason: "the owner's ruling of 9 October 2026: no run in the Safari application in a batch applying his rulings; this batch adds the Guide button, its pictures and a loader". What §8.3 reports is the last run of it, on the layer built 2026-10-08T22:42:59Z; the two browser engines below were run on this build.


**Every unit, by script.** `scripts/verify_layer.py` rebuilds every displayed field of every unit from the stage tables
— not from `layer_by_unit.csv` — and every class at every floor, and compares them with what `data.js` holds:
**92 of 92 checks passed; n = 11,468 units, 44 fields a unit, 18 class arrays**. It also checks that the layer's run record describes the two files on disk (sizes, sha256, the default
floor).

**Every control, in a browser, on this build.** `scripts/exercise_layer.py` opens `60_layer/index.html` from disk, works
each interactive element, and after each action reads what the page then shows. It then clicks a sample of units on
the map and compares every value the panel displays with the stage tables, rebuilt without any of the builder's code.
Both runs below are on the build of 2026-10-12T22:00:54Z (`index.html` sha256 `24aa94bb69db24f0…`, `data.js` `91d4bb2e68664583…`);
this document is not written unless they are.

| | Chrome | WebKit |
|---|---|---|
| browser | Chrome/154.0.8037.99 | WebKit 21624.5.1.11.3 (the engine of Safari 27.0 on this machine) |
| how the events were made | real mouse and keyboard events sent through Chrome's DevTools protocol to a separate, headless Chrome | events dispatched inside the page (a control's own click(); mouse, wheel and key events built in script), in a WKWebView that lies off the screen |
| run | 2026-10-12T22:06:50Z | 2026-10-12T22:11:09Z |
| actions that did what they should | 60 of 60 | 60 of 60 |
| units clicked on the map | 29 | 29 |
| displayed values equal to the stage tables | 1,276 of 1,276 | 1,276 of 1,276 |
| script errors raised by the page | none | none |
| log | `60_layer/exercise_chrome.json` | `60_layer/exercise_webkit.json` |

### 8.1 What was clicked, and what happened — Chrome

| | control | what was done | what the page then showed |
|---|---|---|---|
| 1 | page | opened file://<repository>/60_layer/index.html in Chrome/154.0.8037.99 | ready in 4.2 s; files loaded: ['data.js', 'index.html']; script errors: none |
| 2 | page | read the starting state | layer hansen_loss, floor 100 ha, both kinds of unit shown (7,976 + 3,492 drawn), no unit selected, legend 'Tree cover loss 2001-2025 as a share of the unit's...' |
| 3 | loader | read the loader once the page said it was ready | it is no longer shown; the last thing it said was 'Drawing the units…'; in the page's own file its first words, 'Loading the map…', are plain markup that stands before the tag that asks for data.js |
| 4 | layer switcher | clicked the radio button 'Forest in 2000 (Hansen)' at (26, 238) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=forest_area&floor=100'; unit 132731 (class 'More than 60 %') is drawn #006d2c, the class colour #006d2c |
| 5 | layer switcher | clicked the radio button 'Tree cover loss since 2001 (Hansen)' at (26, 266) | it became the checked layer; the legend's title and its 8 classes with their counts became this layer's; the address reads '#layer=hansen_loss&floor=100'; unit 132731 (class 'Up to 1 %') is drawn #ffeda0, the class colour #ffeda0 |
| 6 | layer switcher | clicked the radio button 'Loss on open canopy (Hansen)' at (26, 293) | it became the checked layer; the legend's title and its 8 classes with their counts became this layer's; the address reads '#layer=canopy_band_loss&floor=100'; unit 132731 (class 'Up to 1 %') is drawn #ffeda0, the class colour #ffeda0 |
| 7 | layer switcher | clicked the radio button 'Degradation 2017-2023 (CoRE Stack)' at (26, 321) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=corestack_degradation&floor=100'; unit 132731 (class 'More than 35 %') is drawn #a63603, the class colour #a63603 |
| 8 | layer switcher | clicked the radio button 'Degradation minus improvement (CoRE Stack)' at (26, 368) | it became the checked layer; the legend's title and its 7 classes with their counts became this layer's; the address reads '#layer=corestack_net&floor=100'; unit 132731 (class 'Net degradation, more than 20 points') is drawn #7f3b08, the class colour #7f3b08 |
| 9 | layer switcher | clicked the radio button 'Hansen and CoRE Stack compared' at (26, 415) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=agreement&floor=100'; unit 132731 (class 'CoRE Stack only (degradation)') is drawn #ffa500, the class colour #ffa500 |
| 10 | layer switcher | clicked the radio button 'MGNREGA spending, all works' at (26, 517) | it became the checked layer; the legend's title and its 8 classes with their counts became this layer's; the address reads '#layer=allocation&floor=100'; unit 132731 (class 'More than Rs 400 lakh') is drawn #3182bd, the class colour #3182bd |
| 11 | layer switcher | clicked the radio button 'MGNREGA spending on forest works' at (26, 545) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=forest_named_expenditure&floor=100'; unit 132731 (class 'More than Rs 20 lakh') is drawn #1a7f6b, the class colour #1a7f6b |
| 12 | layer switcher | clicked the radio button 'Scheduled Tribe share' at (26, 621) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=st_share&floor=100'; unit 132731 (class 'More than 50 %') is drawn #b9722c, the class colour #b9722c |
| 13 | layer switcher | clicked the radio button 'Aggregate Development Index 2011' at (26, 648) | it became the checked layer; the legend's title and its 7 classes with their counts became this layer's; the address reads '#layer=adi_2011&floor=100'; unit 132731 (class 'Up to 6') is drawn #f2f0f7, the class colour #f2f0f7 |
| 14 | layer switcher | clicked the greyed entry 'Greenness trend (NIRv) - tested, not used' at (142, 453) | nothing changed: it is text, not a control |
| 15 | layer switcher | with the keyboard: Arrow Down on the focused radio button | the next layer, 'canopy_band_loss', became the layer and the legend followed |
| 16 | minimum forest | clicked '50 ha' at (26, 744) with the Hansen loss layer on | legend: 'Insufficient forest to assess (8,833 units)' (hansen_by_unit.csv has 8,833 units under 50 ha of forest); unit 131597, with 81.8 ha of forest, is drawn #fed976 = '1 to 2.5 %' (#fed976); address '#layer=hansen_loss&floor=50' |
| 17 | minimum forest | clicked '1 ha' at (26, 771) with the Hansen loss layer on | legend: 'Insufficient forest to assess (6,265 units)' (hansen_by_unit.csv has 6,265 units under 1 ha of forest); unit 131597, with 81.8 ha of forest, is drawn #fed976 = '1 to 2.5 %' (#fed976); address '#layer=hansen_loss&floor=1' |
| 18 | minimum forest | clicked '100 ha' at (26, 716) with the Hansen loss layer on | legend: 'Insufficient forest to assess (9,401 units)' (hansen_by_unit.csv has 9,401 units under 100 ha of forest); unit 131597, with 81.8 ha of forest, is drawn #cfcfcf = 'Insufficient forest to assess' (#cfcfcf); address '#layer=hansen_loss&floor=100' |
| 19 | minimum forest | with the agreement layer on, clicked '1 ha' | the agreement legend did not change: that layer has its own floor |
| 20 | units shown | unticked 'Panchayat units' at (24, 839) | 0 LGD panchayat and 3,492 outside-village units are drawn; address '#layer=agreement&floor=100&show=out' |
| 21 | units shown | unticked 'Land outside villages' at (24, 856) | 0 LGD panchayat and 0 outside-village units are drawn; address '#layer=agreement&floor=100&show=none' |
| 22 | units shown | ticked 'Panchayat units' again at (24, 829) | 7,976 LGD panchayat and 0 outside-village units are drawn; address '#layer=agreement&floor=100&show=lgd' |
| 23 | units shown | ticked 'Land outside villages' again at (24, 856) | 7,976 LGD panchayat and 3,492 outside-village units are drawn; address '#layer=agreement&floor=100' |
| 24 | go to a district | did not click the district list | a native pop-up menu cannot be operated in a headless window (opening it there swallowed all later input); the choices below set the list and send its change event |
| 25 | go to a district | chose each of the 30 districts in the list in turn | the map moved so that the whole district was in view for 30 of 30 |
| 26 | go to a district | chose the first line of the list, 'Jump to a district...' | nothing moved and nothing broke |
| 27 | search | put the id 'OUTSIDE_1097' in the box at (142, 848) and pressed Enter | the panel opened unit OUTSIDE_1097, the map flew to it and outlined it (1 outline), no message; address '#layer=agreement&floor=100&unit=OUTSIDE_1097' |
| 28 | search | typed the id in lower case, 'outside_1097' | the same unit, OUTSIDE_1097 |
| 29 | search | typed part of a name, 'PUR' (in capitals), pressed Enter | message: '1,659 units match; showing the first. Add more of the name, or use the id.'; the unit opened is 131199 ('bhubaneswarpur'); units_attributes.csv has 1,659 names containing 'pur' |
| 30 | search | typed a name only one unit has, 'bhengrajpur' | unit 131205 opened, no message |
| 31 | search | typed 'zzzz no such place', pressed Enter | message: 'No unit with that name or id.'; the unit shown stayed 131205 |
| 32 | search | emptied the box and pressed Enter | nothing changed |
| 33 | text panels | clicked the button 'About this map' at (71, 14) | the panel opened (20,387 characters) and holds ['Units, not hectares', 'The headline:', 'Every unit kept', 'Small forests are greyed out'] |
| 34 | text panels | turned the mouse wheel over the panel | it scrolled (600 px) |
| 35 | text panels | clicked 'Close' at (1060, 49) | the panel closed |
| 36 | text panels | clicked the button 'Sources' at (165, 14) | the panel opened (3,401 characters) and holds ['ODbL 1.0', 'CC BY-NC-SA 4.0', 'Leaflet 1.9.4'] |
| 37 | text panels | turned the mouse wheel over the panel | it scrolled (600 px) |
| 38 | text panels | clicked the dimmed page beside the panel, at (40, 500) | the panel closed |
| 39 | text panels | clicked the button 'Guide' at (230, 14) | the same panel opened, at its top (33,721 characters), under the guide's first heading, 'A guide to this map', and it holds a line of the guide's last section, 'Figures are those of this build and of the checks run on it.' |
| 40 | text panels | read the pictures in the Guide's panel | 5 pictures, as many as docs/GUIDE.md names (5); each is drawn, at its natural size of [(1280, 800)], from its own bytes inside the page; each is as wide as the text ([701] px of [701] px) |
| 41 | text panels | turned the mouse wheel over the panel | it scrolled (600 px) |
| 42 | text panels | clicked 'Close' at (1060, 49) | the panel closed |
| 43 | text panels | made the window 380 x 700 and opened the Guide | its panel is 342 px wide and does not scroll sideways (its content is 342 px wide); 5 of its 13 tables are wider than the panel, and each of those scrolls sideways inside itself; each picture is as wide as the text ([298] px) |
| 44 | legend | read the legend of the agreement layer, the one with the longest class name | it is 330 x 287 px on a map of 840 x 863 px, lists 7 rows, and nothing in it runs past its edge |
| 45 | legend | clicked its 'Hide' button at (1099, 580) | the legend shrank to its title (330 x 76 px, 0 rows) and the button now reads 'Show' |
| 46 | legend | changed the layer while the legend was hidden | it stayed hidden and its title became the new layer's ('Scheduled Tribe share of population, Cen...') |
| 47 | legend | clicked 'Show' at (1096, 809) | the legend came back with 7 rows |
| 48 | map | clicked '+' at (327, 28) | zoom went from 7.5 to 8.5 |
| 49 | map | clicked '-' at (327, 58) | zoom went back to 7.5 |
| 50 | map | turned the mouse wheel (upwards) over the middle of the map | zoom went from 7.5 to 9 |
| 51 | map | dragged the map 180 px left and 120 px up | its centre moved from 20.211 N 84.440 E to 19.900 N 84.935 E, and the unit that was open stayed open |
| 52 | map | double-clicked the middle of the map | zoom went from 9 to 10 |
| 53 | address | closed the page, then opened the file afresh with '#layer=agreement&floor=50&show=out&unit=...&district=Koraput&open=sources' | layer agreement, floor 50, 0 LGD and 3,492 outside-village units drawn, unit OUTSIDE_1097 open, district list on 'Koraput', the Sources panel open |
| 54 | address | changed the address in place to '#layer=st_share&floor=100&show=both&q=<a unit's name>' | the page followed: layer st_share, floor 100, all 11,468 units drawn, unit 131205 open |
| 55 | address | changed the address in place to a layer that is greyed out and cannot be chosen (NIRv), a floor that does not exist and a unit that does not exist | layer and floor went to their defaults (hansen_loss, 100 ha); the unit already open, 131205, stayed open; no error |
| 56 | address | closed the page, then opened the file afresh with nonsense in every part of the address | the page opened on its defaults: layer hansen_loss, floor 100 ha, all 11,468 units drawn, no unit open, no panel, no error |
| 57 | address | closed the page, then opened the file afresh with '#open=guide' | the Guide's panel is open, at its top, under the heading 'A guide to this map', with 5 pictures; the loader is gone; behind it the page is on its defaults (layer hansen_loss, floor 100 ha, all 11,468 units drawn, no unit open); no error |
| 58 | window size | made the window 1100 x 700 | side panel 250 px, map 550 px, unit panel 300 px wide; the page is 1100 px wide, with no sideways scrolling; the legend is 330 x 307 px inside a map 700 px high and can be hidden |
| 59 | window size | made the window 820 x 600 | side panel 210 px, map 370 px, unit panel 240 px wide; the page is 820 px wide, with no sideways scrolling; the legend is 240 x 340 px inside a map 600 px high and can be hidden |
| 60 | unit panel | turned the mouse wheel over the unit panel | it scrolled (500 px); it has 7 headed sections and a bar of 6 class segments |

### 8.2 The same, in WebKit

| | control | what was done | what the page then showed |
|---|---|---|---|
| 1 | page | opened file://<repository>/60_layer/index.html in WebKit 21624.5.1.11.3 (the engine of Safari 27.0 on this machine) | ready in 2.2 s; files loaded: ['data.js', 'index.html']; script errors: none |
| 2 | page | read the starting state | layer hansen_loss, floor 100 ha, both kinds of unit shown (7,976 + 3,492 drawn), no unit selected, legend 'Tree cover loss 2001-2025 as a share of the unit's...' |
| 3 | loader | read the loader once the page said it was ready | it is no longer shown; the last thing it said was 'Drawing the units…'; in the page's own file its first words, 'Loading the map…', are plain markup that stands before the tag that asks for data.js |
| 4 | layer switcher | sent a click to the radio button 'Forest in 2000 (Hansen)' at (22, 235) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=forest_area&floor=100'; unit 132731 (class 'More than 60 %') is drawn #006d2c, the class colour #006d2c |
| 5 | layer switcher | sent a click to the radio button 'Tree cover loss since 2001 (Hansen)' at (22, 261) | it became the checked layer; the legend's title and its 8 classes with their counts became this layer's; the address reads '#layer=hansen_loss&floor=100'; unit 132731 (class 'Up to 1 %') is drawn #ffeda0, the class colour #ffeda0 |
| 6 | layer switcher | sent a click to the radio button 'Loss on open canopy (Hansen)' at (22, 306) | it became the checked layer; the legend's title and its 8 classes with their counts became this layer's; the address reads '#layer=canopy_band_loss&floor=100'; unit 132731 (class 'Up to 1 %') is drawn #ffeda0, the class colour #ffeda0 |
| 7 | layer switcher | sent a click to the radio button 'Degradation 2017-2023 (CoRE Stack)' at (22, 332) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=corestack_degradation&floor=100'; unit 132731 (class 'More than 35 %') is drawn #a63603, the class colour #a63603 |
| 8 | layer switcher | sent a click to the radio button 'Degradation minus improvement (CoRE Stack)' at (22, 377) | it became the checked layer; the legend's title and its 7 classes with their counts became this layer's; the address reads '#layer=corestack_net&floor=100'; unit 132731 (class 'Net degradation, more than 20 points') is drawn #7f3b08, the class colour #7f3b08 |
| 9 | layer switcher | sent a click to the radio button 'Hansen and CoRE Stack compared' at (22, 422) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=agreement&floor=100'; unit 132731 (class 'CoRE Stack only (degradation)') is drawn #ffa500, the class colour #ffa500 |
| 10 | layer switcher | sent a click to the radio button 'MGNREGA spending, all works' at (22, 522) | it became the checked layer; the legend's title and its 8 classes with their counts became this layer's; the address reads '#layer=allocation&floor=100'; unit 132731 (class 'More than Rs 400 lakh') is drawn #3182bd, the class colour #3182bd |
| 11 | layer switcher | sent a click to the radio button 'MGNREGA spending on forest works' at (22, 548) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=forest_named_expenditure&floor=100'; unit 132731 (class 'More than Rs 20 lakh') is drawn #1a7f6b, the class colour #1a7f6b |
| 12 | layer switcher | sent a click to the radio button 'Scheduled Tribe share' at (22, 621) | it became the checked layer; the legend's title and its 6 classes with their counts became this layer's; the address reads '#layer=st_share&floor=100'; unit 132731 (class 'More than 50 %') is drawn #b9722c, the class colour #b9722c |
| 13 | layer switcher | sent a click to the radio button 'Aggregate Development Index 2011' at (22, 647) | it became the checked layer; the legend's title and its 7 classes with their counts became this layer's; the address reads '#layer=adi_2011&floor=100'; unit 132731 (class 'Up to 6') is drawn #f2f0f7, the class colour #f2f0f7 |
| 14 | layer switcher | sent a click to the greyed entry 'Greenness trend (NIRv) - tested, not used' at (141, 457) | nothing changed: it is text, not a control |
| 15 | layer switcher | did not try the keyboard | a key's built-in action does not run for an event made in script: not exercised in this browser |
| 16 | minimum forest | sent a click to '50 ha' at (22, 739) with the Hansen loss layer on | legend: 'Insufficient forest to assess (8,833 units)' (hansen_by_unit.csv has 8,833 units under 50 ha of forest); unit 131597, with 81.8 ha of forest, is drawn #fed976 = '1 to 2.5 %' (#fed976); address '#layer=hansen_loss&floor=50' |
| 17 | minimum forest | sent a click to '1 ha' at (22, 765) with the Hansen loss layer on | legend: 'Insufficient forest to assess (6,265 units)' (hansen_by_unit.csv has 6,265 units under 1 ha of forest); unit 131597, with 81.8 ha of forest, is drawn #fed976 = '1 to 2.5 %' (#fed976); address '#layer=hansen_loss&floor=1' |
| 18 | minimum forest | sent a click to '100 ha' at (22, 713) with the Hansen loss layer on | legend: 'Insufficient forest to assess (9,401 units)' (hansen_by_unit.csv has 9,401 units under 100 ha of forest); unit 131597, with 81.8 ha of forest, is drawn #cfcfcf = 'Insufficient forest to assess' (#cfcfcf); address '#layer=hansen_loss&floor=100' |
| 19 | minimum forest | with the agreement layer on, sent a click to '1 ha' | the agreement legend did not change: that layer has its own floor |
| 20 | units shown | unticked 'Panchayat units' at (22, 831) | 0 LGD panchayat and 3,492 outside-village units are drawn; address '#layer=agreement&floor=100&show=out' |
| 21 | units shown | unticked 'Land outside villages' at (22, 857) | 0 LGD panchayat and 0 outside-village units are drawn; address '#layer=agreement&floor=100&show=none' |
| 22 | units shown | ticked 'Panchayat units' again at (22, 831) | 7,976 LGD panchayat and 0 outside-village units are drawn; address '#layer=agreement&floor=100&show=lgd' |
| 23 | units shown | ticked 'Land outside villages' again at (22, 857) | 7,976 LGD panchayat and 3,492 outside-village units are drawn; address '#layer=agreement&floor=100' |
| 24 | go to a district | did not click the district list | a native pop-up menu cannot be operated in a headless window (opening it there swallowed all later input); the choices below set the list and send its change event |
| 25 | go to a district | chose each of the 30 districts in the list in turn | the map moved so that the whole district was in view for 30 of 30 |
| 26 | go to a district | chose the first line of the list, 'Jump to a district...' | nothing moved and nothing broke |
| 27 | search | put the id 'OUTSIDE_1097' in the box at (141, 935) and pressed Enter | the panel opened unit OUTSIDE_1097, the map flew to it and outlined it (1 outline), no message; address '#layer=agreement&floor=100&unit=OUTSIDE_1097' |
| 28 | search | typed the id in lower case, 'outside_1097' | the same unit, OUTSIDE_1097 |
| 29 | search | typed part of a name, 'PUR' (in capitals), pressed Enter | message: '1,659 units match; showing the first. Add more of the name, or use the id.'; the unit opened is 131199 ('bhubaneswarpur'); units_attributes.csv has 1,659 names containing 'pur' |
| 30 | search | typed a name only one unit has, 'bhengrajpur' | unit 131205 opened, no message |
| 31 | search | typed 'zzzz no such place', pressed Enter | message: 'No unit with that name or id.'; the unit shown stayed 131205 |
| 32 | search | emptied the box and pressed Enter | nothing changed |
| 33 | text panels | sent a click to the button 'About this map' at (72, 96) | the panel opened (20,387 characters) and holds ['Units, not hectares', 'The headline:', 'Every unit kept', 'Small forests are greyed out'] |
| 34 | text panels | scrolled the panel by its own scroll position (script cannot scroll WebKit with a wheel event) | it scrolled (600 px) |
| 35 | text panels | sent a click to 'Close' at (1058, 52) | the panel closed |
| 36 | text panels | sent a click to the button 'Sources' at (168, 96) | the panel opened (3,401 characters) and holds ['ODbL 1.0', 'CC BY-NC-SA 4.0', 'Leaflet 1.9.4'] |
| 37 | text panels | scrolled the panel by its own scroll position (script cannot scroll WebKit with a wheel event) | it scrolled (600 px) |
| 38 | text panels | sent a click to the dimmed page beside the panel, at (40, 500) | the panel closed |
| 39 | text panels | sent a click to the button 'Guide' at (234, 96) | the same panel opened, at its top (33,721 characters), under the guide's first heading, 'A guide to this map', and it holds a line of the guide's last section, 'Figures are those of this build and of the checks run on it.' |
| 40 | text panels | read the pictures in the Guide's panel | 5 pictures, as many as docs/GUIDE.md names (5); each is drawn, at its natural size of [(1280, 800)], from its own bytes inside the page; each is as wide as the text ([699] px of [699] px) |
| 41 | text panels | scrolled the panel by its own scroll position (script cannot scroll WebKit with a wheel event) | it scrolled (600 px) |
| 42 | text panels | sent a click to 'Close' at (1058, 52) | the panel closed |
| 43 | text panels | made the window 380 x 700 and opened the Guide | its panel is 340 px wide and does not scroll sideways (its content is 340 px wide); 5 of its 13 tables are wider than the panel, and each of those scrolls sideways inside itself; each picture is as wide as the text ([296] px) |
| 44 | legend | read the legend of the agreement layer, the one with the longest class name | it is 330 x 280 px on a map of 840 x 950 px, lists 7 rows, and nothing in it runs past its edge |
| 45 | legend | sent a click to its 'Hide' button at (1098, 674) | the legend shrank to its title (330 x 75 px, 0 rows) and the button now reads 'Show' |
| 46 | legend | changed the layer while the legend was hidden | it stayed hidden and its title became the new layer's ('Scheduled Tribe share of population, Cen...') |
| 47 | legend | sent a click to 'Show' at (1096, 896) | the legend came back with 7 rows |
| 48 | map | sent a click to '+' at (327, 28) | zoom went from 7.5 to 8.5 |
| 49 | map | sent a click to '-' at (327, 58) | zoom went back to 7.5 |
| 50 | map | sent a wheel event (upwards) over the middle of the map | zoom went from 7.5 to 8.25 |
| 51 | map | dragged the map 180 px left and 120 px up (mouse-down, eight mouse-moves and mouse-up, made in script) | its centre moved from 20.205 N 84.440 E to 19.685 N 85.270 E, and the unit that was open stayed open |
| 52 | map | double-clicked the middle of the map | zoom went from 8.25 to 9.25 |
| 53 | address | closed the page, then opened the file afresh with '#layer=agreement&floor=50&show=out&unit=...&district=Koraput&open=sources' | layer agreement, floor 50, 0 LGD and 3,492 outside-village units drawn, unit OUTSIDE_1097 open, district list on 'Koraput', the Sources panel open |
| 54 | address | changed the address in place to '#layer=st_share&floor=100&show=both&q=<a unit's name>' | the page followed: layer st_share, floor 100, all 11,468 units drawn, unit 131205 open |
| 55 | address | changed the address in place to a layer that is greyed out and cannot be chosen (NIRv), a floor that does not exist and a unit that does not exist | layer and floor went to their defaults (hansen_loss, 100 ha); the unit already open, 131205, stayed open; no error |
| 56 | address | closed the page, then opened the file afresh with nonsense in every part of the address | the page opened on its defaults: layer hansen_loss, floor 100 ha, all 11,468 units drawn, no unit open, no panel, no error |
| 57 | address | closed the page, then opened the file afresh with '#open=guide' | the Guide's panel is open, at its top, under the heading 'A guide to this map', with 5 pictures; the loader is gone; behind it the page is on its defaults (layer hansen_loss, floor 100 ha, all 11,468 units drawn, no unit open); no error |
| 58 | window size | made the window 1100 x 700 | side panel 250 px, map 550 px, unit panel 300 px wide; the page is 1100 px wide, with no sideways scrolling; the legend is 330 x 299 px inside a map 700 px high and can be hidden |
| 59 | window size | made the window 820 x 600 | side panel 210 px, map 370 px, unit panel 240 px wide; the page is 820 px wide, with no sideways scrolling; the legend is 240 x 352 px inside a map 600 px high and can be hidden |
| 60 | unit panel | scrolled the unit panel by its own scroll position | it scrolled (500 px); it has 7 headed sections and a bar of 6 class segments |

### 8.3 Safari, the application: opened from disk and driven by its address

`scripts/exercise_layer_safari.py` asks Safari itself (Safari 27.0 (the application)) to open `60_layer/index.html` from disk in a
new window, then changes the window's address — the parts listed in §1 — and after each change reads back the
window's title and the text the page shows. **Nothing is clicked**: running script in a page of Safari from outside
needs a Safari setting that is the owner's to change. So this shows that the page loads, runs and shows the right text
in Safari, for every layer, every minimum, the same 29 units, the search and the two text panels. **Not run on the build this document describes (2026-10-12T22:00:54Z): the owner's ruling of 9 October 2026: no run in the Safari application in a batch applying his rulings; this batch adds the Guide button, its pictures and a loader. What follows is the record of its last run.** Run 2026-10-08T22:53:16Z, on the layer built 2026-10-08T22:42:59Z:
**48 of 48 addresses showed what they should, and 1,265 of 1,265 values the units' panels should show
were in the page's text, in the panel's order** (a value that is blank for a unit is not counted). Log:
`60_layer/exercise_safari.json`.

| | reached | what was done | what the page then showed |
|---|---|---|---|
| 1 | page | opened file://<repository>/60_layer/index.html?exercise=20261008T225206Z in the Safari application, version 27.0, with no layer, floor or unit in the address | after 2 s the window's title is 'Forest condition, MGNREGA allocation and social need - Odisha', the page shows 2,319 characters of text, and the legend is the default layer's (hansen_loss) at 100 ha with its 8 classes and their counts |
| 2 | layer, by address | set the address to '#layer=forest_area&floor=100' | the legend's title and 6 of its 6 class rows, with their counts, are those of the layer's own record |
| 3 | layer, by address | set the address to '#layer=hansen_loss&floor=100' | the legend's title and 8 of its 8 class rows, with their counts, are those of the layer's own record |
| 4 | layer, by address | set the address to '#layer=canopy_band_loss&floor=100' | the legend's title and 8 of its 8 class rows, with their counts, are those of the layer's own record |
| 5 | layer, by address | set the address to '#layer=corestack_degradation&floor=100' | the legend's title and 6 of its 6 class rows, with their counts, are those of the layer's own record |
| 6 | layer, by address | set the address to '#layer=corestack_net&floor=100' | the legend's title and 7 of its 7 class rows, with their counts, are those of the layer's own record |
| 7 | layer, by address | set the address to '#layer=agreement&floor=100' | the legend's title and 6 of its 6 class rows, with their counts, are those of the layer's own record |
| 8 | layer, by address | set the address to '#layer=allocation&floor=100' | the legend's title and 8 of its 8 class rows, with their counts, are those of the layer's own record |
| 9 | layer, by address | set the address to '#layer=forest_named_expenditure&floor=100' | the legend's title and 6 of its 6 class rows, with their counts, are those of the layer's own record |
| 10 | layer, by address | set the address to '#layer=st_share&floor=100' | the legend's title and 6 of its 6 class rows, with their counts, are those of the layer's own record |
| 11 | layer, by address | set the address to '#layer=adi_2011&floor=100' | the legend's title and 7 of its 7 class rows, with their counts, are those of the layer's own record |
| 12 | minimum forest, by address | set the address to '#layer=hansen_loss&floor=100' | the legend reads 'Insufficient forest to assess (9,401 units)' |
| 13 | minimum forest, by address | set the address to '#layer=hansen_loss&floor=50' | the legend reads 'Insufficient forest to assess (8,833 units)' |
| 14 | minimum forest, by address | set the address to '#layer=hansen_loss&floor=1' | the legend reads 'Insufficient forest to assess (6,265 units)' |
| 15 | unit, by address | set the address to '#layer=agreement&floor=100&unit=135949' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 16 | unit, by address | set the address to '#layer=agreement&floor=100&unit=133178' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 17 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_948' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 18 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_2177' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 19 | unit, by address | set the address to '#layer=agreement&floor=100&unit=138213' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 20 | unit, by address | set the address to '#layer=agreement&floor=100&unit=135599' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 21 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_3051' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 22 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1988' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 23 | unit, by address | set the address to '#layer=agreement&floor=100&unit=136359' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 24 | unit, by address | set the address to '#layer=agreement&floor=100&unit=132792' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 25 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_2546' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 26 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_446' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 27 | unit, by address | set the address to '#layer=agreement&floor=100&unit=138925' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 28 | unit, by address | set the address to '#layer=agreement&floor=100&unit=131785' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 29 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1650' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 30 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1523' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 31 | unit, by address | set the address to '#layer=agreement&floor=100&unit=136951' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 32 | unit, by address | set the address to '#layer=agreement&floor=100&unit=137175' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 33 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_232' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 34 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_915' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 35 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1619' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 36 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_2469' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 37 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_413' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 38 | unit, by address | set the address to '#layer=agreement&floor=100&unit=137851' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 39 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_3190' | 43 of 43 values the panel should show are in the page's text, in the panel's order |
| 40 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1704' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 41 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1039' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 42 | unit, by address | set the address to '#layer=agreement&floor=100&unit=OUTSIDE_1034' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 43 | unit, by address | set the address to '#layer=agreement&floor=100&unit=138817' | 44 of 44 values the panel should show are in the page's text, in the panel's order |
| 44 | search, by address | with unit 135949 open, set the address to '#layer=agreement&q=outside_948' (the id in lower case) | the panel shows unit OUTSIDE_948 |
| 45 | search, by address | set the address to a search for 'zzzz no such place' | the message 'No unit with that name or id.' is shown |
| 46 | text panels, by address | set the address to '#layer=agreement&open=about' | the page's text now holds ['Units, not hectares', 'The headline:', 'Every unit kept']; before it was opened it did not hold the first panel's words |
| 47 | text panels, by address | set the address to '#layer=agreement&open=sources' | the page's text now holds ['ODbL 1.0', 'CC BY-NC-SA 4.0'] |
| 48 | address | set the address to a layer, a floor and a unit that do not exist | the page went to its defaults: the legend is that of hansen_loss at 100 ha |

### 8.4 The units clicked on the map

A seeded sample, the same in both engines, drawn to span both kinds of unit, forest from none to the largest, every
agreement class and every way a district was assigned. The sixteen units of the first hand check (6 October) were left
out, so that this is a fresh sample. Every one of the 44 fields of the panel is compared.

| unit that opened | type | chosen as | forest, ha | agreement class | values equal, Chrome | WebKit |
|---|---|---|---|---|---|---|
| `135949` | lgd panchayat | lgd panchayat, no forest | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `133178` | lgd panchayat | lgd panchayat, no forest | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_948` | outside village | outside village, no forest | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_2177` | outside village | outside village, no forest | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `138213` | lgd panchayat | lgd panchayat, under 1 ha of forest | 0.6 | insufficient forest | 44 of 44 | 44 of 44 |
| `135599` | lgd panchayat | lgd panchayat, under 1 ha of forest | 0.1 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_3051` | outside village | outside village, under 1 ha of forest | 0.1 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_1988` | outside village | outside village, under 1 ha of forest | 0.4 | insufficient forest | 44 of 44 | 44 of 44 |
| `136359` | lgd panchayat | lgd panchayat, 1 to 100 ha | 16.1 | insufficient forest | 44 of 44 | 44 of 44 |
| `132792` | lgd panchayat | lgd panchayat, 1 to 100 ha | 1.1 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_2546` | outside village | outside village, 1 to 100 ha | 2.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_446` | outside village | outside village, 1 to 100 ha | 1.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `138925` | lgd panchayat | lgd panchayat, 100 to 1,000 ha | 682.5 | hansen only | 44 of 44 | 44 of 44 |
| `131785` | lgd panchayat | lgd panchayat, 100 to 1,000 ha | 139.4 | neither | 44 of 44 | 44 of 44 |
| `OUTSIDE_1650` | outside village | outside village, 100 to 1,000 ha | 497.4 | zone model excluded | 44 of 44 | 44 of 44 |
| `OUTSIDE_1523` | outside village | outside village, 100 to 1,000 ha | 237.2 | both | 44 of 44 | 44 of 44 |
| `136951` | lgd panchayat | lgd panchayat, over 1,000 ha | 2,648.4 | both | 44 of 44 | 44 of 44 |
| `137175` | lgd panchayat | lgd panchayat, over 1,000 ha | 1,293.2 | neither | 44 of 44 | 44 of 44 |
| `OUTSIDE_232` | outside village | outside village, over 1,000 ha | 1,692.8 | corestack only | 44 of 44 | 44 of 44 |
| `OUTSIDE_915` | outside village | outside village, over 1,000 ha | 1,786.0 | neither | 44 of 44 | 44 of 44 |
| `OUTSIDE_1619` | outside village | agreement class 'both' | 97.5 | both | 44 of 44 | 44 of 44 |
| `OUTSIDE_2469` | outside village | agreement class 'hansen_only' | 132.3 | hansen only | 44 of 44 | 44 of 44 |
| `OUTSIDE_413` | outside village | agreement class 'corestack_only' | 2,313.7 | corestack only | 44 of 44 | 44 of 44 |
| `137851` | lgd panchayat | agreement class 'neither' | 51.5 | neither | 44 of 44 | 44 of 44 |
| `OUTSIDE_3190` | outside village | agreement class 'zone_model_excluded' | 102.4 | zone model excluded | 44 of 44 | 44 of 44 |
| `OUTSIDE_1704` | outside village | outside village, district moved off the polygon's name | 75.8 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_1039` | outside village | outside village, polygon with no name | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `OUTSIDE_1034` | outside village | outside village, district ambiguous | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |
| `138817` | lgd panchayat | lgd panchayat, no development index | 0.0 | insufficient forest | 44 of 44 | 44 of 44 |

### 8.5 What the check found, and what was changed

The first runs of this check, on the builds before this one, found faults that the per-unit script could not have
found, because they were in how the page behaves and not in what it holds. All were fixed, and the runs above are
after the fixes:

- **One quantity, printed two ways.** The land with canopy above 10 per cent, and CoRE Stack's Degradation share, each
  appear on two lines of the panel; in some units the two lines differed in the last digit, because they were taken
  from two tables rounded differently. Each now takes one cell, and `verify_layer.py` requires the two lines to read
  the same.
- **Narrow windows.** In a narrow window the side panels kept their width and squeezed the map to a strip; the rule
  meant to prevent it was placed where it had no effect. The panels now narrow with the window.
- **The legend.** The longest class name ran past the legend's edge, and in a short window the legend covered the map.
  Rows now wrap, the legend scrolls within the map, and it has a Hide / Show button.
- **The district list.** A district chosen while the map was still moving to the previous one was ignored. Moves to a
  district or a unit are no longer animated.
- **Small things.** The count of search matches had no thousands separator; the *About* text printed a change of
  "−0.0000 %".
- **The run record.** It gave a default minimum other than the page's 100 ha, and the "Built" line named an
  older stage date than the newest table read. The builder was corrected and the verifier now compares the record with
  the page.

### 8.6 What this does not show

- **Nothing was clicked in the Safari application.** There the page was opened and taken through its address (§8.3);
  the clicks were made in WebKit, its engine, and in Chrome. Clicking in Safari itself needs its "Allow remote
  automation" or "Allow JavaScript from Apple Events" setting, which is the owner's to change. Not reachable through
  the address, and so not seen in Safari itself: the two kinds-of-unit boxes, the district list, and the drawn map.
  In WebKit the events are made in script, so what a key press does by default (an arrow key moving the choice of
  layer) is exercised in Chrome only.
- **The district list was set through its change event** in both engines: its native pop-up cannot be clicked in a
  window that is not on a screen. Choosing a district, and what the map then does, is exercised; the pop-up itself is
  not.
- **Firefox**: not installed on the machine the check ran on, so the layer has not been opened in it.
- **A phone or a touch screen.** On 11 October 2026 the page was opened in a window of a phone's width, in a desktop
  browser, and looked at. What was seen: The page is laid out for a laptop, and at 390 x 844 it cannot be used. The two side panels keep most of the width between them, so the map, and the ranked list under it, are left a strip a few pixels wide. The legend, which belongs over the map, lies over the side panel and covers the names of the layers and, in the decision view, the windows. The unit's panel runs off the right edge, its figures are cut, and the page scrolls sideways. A bubble still opens wholly inside the window and can be read wherever its 'i' can be reached (the legend's, a section's in the unit's panel, the overlay's); the 'i' of the decision view's switch lies under the legend, and those of the list cannot be reached because the list has no width. Nothing was redesigned. It was not opened on a phone, and nothing was tapped. With the Guide button (13 October 2026): at 390 x 844 the row of the buttons has two lines, as it had, and Guide stands after Sources on the second, under the legend. A click on it there does not reach it; with the legend hidden by its own Hide button, the click opens the guide (measured in both builds). The Guide's window itself was looked at in a window 380 px wide: it can be read, and a table wider than it scrolls sideways inside itself.
  (`docs/SITE_COPY.md` has the notes on each picture.)
- Printing; a machine with little memory (the data file is 23 MB of script); and whether the Foundation's staff read the
  class names as intended.

## 9. Before it is shown

- It is a map of units. A unit flagged by both measures is a place to look, not a finding about a village.
- The paper this layer borrows its vocabulary from reports that in one of its pilot blocks, Angul, in this state, the
  community did not favour mapping inequity (Commons Connect, ICTD 2024, p. 18). The Scheduled Tribe share and
  development index layers are of that kind. Whether they belong in what is shown is the Foundation's call.
- Nothing here says why a unit lost forest or was passed over for work. Stage 4, the comparison of forest condition, need and allocation, is another document, `docs/GAP.md`; it describes where money went relative to where forest was lost and does not argue why either.
- **The copy to send is `70_share/odisha_forest_decision_layer/`, not this folder** (§11): the same two files without
  the development index of 2011 (since 10 October 2026) and with the overlay switched off, its box greyed out (since
  11 October 2026); no `overlay.js`; and a README. Since 11 October 2026 the owner publishes that folder at
  https://sudo-karan.github.io/ICTD_Project/; `docs/DECISION_LAYER.md` §14 says which build of it the site serves.

## 10. To rebuild

```
.venv/bin/python scripts/06_build_layer.py --units 10_units/units.gpkg
.venv/bin/python scripts/verify_layer.py
.venv/bin/python scripts/exercise_layer.py chrome      # needs Google Chrome
.venv/bin/python scripts/exercise_layer.py webkit      # needs macOS and swiftc
.venv/bin/python scripts/exercise_layer_safari.py      # needs macOS, Safari, and leave for the terminal to control it
```

A rebuild makes the three `exercise_*.json` logs stale: they name the build they were made on. This document and
`docs/RESULTS.md` refuse to be written from a Chrome or a WebKit log of another build. For the Safari log both make
one exception since 9 October 2026, by the owner's choice: when `scripts/run_decision_checks.py` was told to leave
the Safari checks out of its pass and wrote the reason into `60_layer/decision_runs.json`, the Safari log may be of an
earlier build, and each document then says so wherever it speaks of Safari.

`60_layer/` is git-ignored: it is rebuilt from the stage tables, and `data.js` is 23 MB. NIRv is not a measure
(ruling of 7 October 2026): its state-wide run was stopped, nothing is queued, and its columns of
`degradation_by_unit.csv` are blank. The layer draws nothing of it and lists it greyed, as §2 says.

## 11. The decision view, the tile provider and the Gazette's list (added 8 and 9 October 2026)

`docs/DECISION_LAYER.md` is the full account and carries the figures; this section says what the addition is to this
folder and to the page described above.

**What was added to the page, and what was not changed.** Above the list of layers stands one switch,
"Decision view", under the heading it shares with them since 11 October 2026, "Show on the map". With it off the page
is the page of §1 to §9: every layer, class and default as before, and the checks of §8 pass on this build
(`scripts/verify_layer.py` is unchanged; `scripts/exercise_layer.py` was changed on 11 October 2026 only where it
pinned reworded words, as listed in `docs/SITE_COPY.md`). Two things show in the existing views: that switch, and a
block "why this tier" at the end of every unit's panel. The owner accepted both on 9 October 2026.

**What the decision view shows.** Each of the 11,468 units in one of six cells, by two questions put to Hansen's
record: how much forest of 2000 has no loss recorded since (10 ha or more, and mostly closed or
mostly open; or less), and whether 1 ha or more of forest loss is recorded in a window of years.
The owner accepted both thresholds on 9 October 2026 and renamed five of the cells then so that each name states its
test; no unit changed cell. In the default window, 2018–2025:

| cell | units |
|---|---|
| Open forest, loss recorded - restore | 406 |
| Closed forest, loss recorded - find the cause first | 1,295 |
| Open forest, little or no loss recorded - assisted natural regeneration candidate | 3,055 |
| Closed forest, little or no loss recorded - protect | 1,040 |
| Little forest left, loss recorded - verify on the ground | 33 |
| Not a forest site | 5,639 |

Within one district the units are listed tier by tier; there is no state-wide ranking and no score. The order of
tiers is provisional, to be set with the Foundation for Ecological Security. Beside the tier, never in it: the loss of
the window as a share of the forest at its start, the corroboration badge of §2's agreement layer, Scheduled Tribe
share, the development index and past forest-named spending. A list can be exported: 32 columns, the
development index not among them.

**The tile provider.** The view's optional overlay asks Global Forest Watch (World Resources Institute) for map tiles of Hansen's loss
(Hansen/UMD Global Forest Change v1.13). It is off unless ticked, can be ticked only in the decision view, and its code is in
`overlay.js` so that `index.html` and `data.js` still ask the network for nothing. While it is ticked, the network
address of whoever is looking, the place viewed and the years of the window leave the machine. Two points of the
provider's terms are unresolved and are the owner's: Two points, both the project owner's to decide; one note to gfw@wri.org could settle both. (1) API keys. The terms read 'each request to an API must include one of Your Account's unique API keys'. The tile service's reference declares no key scheme and the service returns every tile without one. The provider's developer page counts the Tile Cache among the Data API's five core services and says 'Some endpoints require users to include an API key with their request'; the guide it links says 'To make most requests to the GFW Data API using third-party applications (e.g., scripts or websites), you need an API key.' Nothing read says whether tiles drawn in a page like this one are among them. (2) Attribution. The terms bind a user to the Attribution Requirements page, which asks for the words and link 'powered by Resource Watch' on maps made with 'the Resource Watch API'. Whether that page governs the tile service of Global Forest Watch is not said anywhere read, and the page is to be archived. The overlay credits the data's authors, its licence and the tile provider, and does not carry those words

**The Gazette's list.** Each cell's work-type field cites rows of Ministry of Rural Development notification S.O. 5448(E), 5 October 2026; Gazette of India, Extraordinary, Part II, Section 3(ii), No. 5238; Gazette ID CG-DL-E-05102026-276796: 375 works, registered in
`00_raw/06_scheme/`. Which rows bear on which cell is a proposal, for the Foundation.

**The copy made to be passed on, `70_share/odisha_forest_decision_layer/`.** `scripts/07_build_share.py` (run
2026-10-12T22:01:24Z) writes `index.html` and `data.js` of the layer built 2026-10-12T22:00:54Z there without the
development index of 2011 - its layer, its value in the row of each of 11,468 units, its line of the panel, its
column of the ranked list, its row of the sources - and, by the owner's ruling of 11 October 2026, with the overlay
switched off: in the copy its box is greyed out and cannot be ticked, the overlay's part of the data is cut to three
keys, and one paragraph of *About this map* and one row of *Sources* say that the overlay is not in this copy.
Otherwise the two files are as they are here. It leaves `overlay.js` out, adds a README and makes a zip of
6.68 MB beside the folder. This folder, `60_layer/`, keeps the index and a working overlay.
Until 10 October 2026 the copy's two files were this folder's byte for byte. `scripts/exercise_share.py` opened the
copy from disk in Chrome/154.0.8037.99 (2026-10-12T22:20:44Z): 9 of 9 steps did what
they should. It holds the copy's two files against this folder's under that rule and finds the index named in
neither; the page asked the network for nothing and for no `overlay.js`; the overlay's box stayed unticked when it
was clicked; and under it the page says "Not in this copy, while we check the tile provider's terms of use."

**Its checks.** `scripts/verify_decision.py`: 62 of 62 checks passed; n = 11,468 units, 4 windows, 6 cells, 30 districts. `scripts/exercise_decision.py`: in Chrome
53 of 53 steps did what they should, in WebKit
47 of 47, both on this build. The Safari
application: not run on this build (the owner's ruling of 9 October 2026: no run in the Safari application in a batch applying his rulings; this batch adds the Guide button, its pictures and a loader); `docs/DECISION_LAYER.md` §16 says what its last run, on an earlier build, showed.

## 12. The words of the page (11 October 2026)

On 11 October 2026 the page's words were rewritten to the owner's own, with every figure, class, count and colour
left where it was; `docs/SITE_COPY.md` is the account, with every string before and after. What that changed in what
this document describes:

- **A label is short, and what it left out stands in a small "i" beside it.** The "i" opens a bubble on hover and on
  keyboard focus, both checked in a browser; the page's script opens it on a click as well, which is what a tap on a
  touch screen sends, and no touch screen was tried. Its words are in one new key at the top of `data.js`, `tips` (23 texts);
  no other key was added. The side panel has one heading, "Show on the map", over the decision view's switch and the
  list of layers.
- **NIRv is shown for what it is**: tested, not used (§2). The unit panel's NIRv section, which held a heading and a
  note and no figure, is gone; a panel has 7 sections.
- **What the page says of itself is true of the website too**: it no longer calls itself offline, or says that
  nothing is worked out in the browser (§5).
- **No figure moved.** `layer_by_unit.csv` is byte for byte what it was, and `scripts/check_site_copy.py` holds both
  builds against copies saved before a word was changed.
- **Six lines were corrected later the same day, in the owner's words** (his third handoff): the check that fails in
  the East Coast zone is this project's placebo test and not CoRE Stack's own; Hansen does record loss on open land,
  and what it cannot see is thinning; the grid's column without loss reads "little or no"; the prompt of a unit
  outside villages keeps its question and drops the claim that no village plan covers the land; the Hansen row of
  *Sources* says what was reconciled (§7); and it is CoRE Stack's published block rasters, not a dashboard, that take
  two classes from its land-use maps (§6). `docs/DECISION_LAYER.md` §17.5 and `docs/SITE_COPY.md` have each line, old
  beside new; every other string is as it was.

## 13. The Guide button and the loader (13 October 2026)

On 13 October 2026 the owner had two things added to the page. No layer, class, count, colour or figure of §1 to §12
moved: `scripts/check_site_copy.py` holds both builds against the copies kept before, with what was added written out.

**A third button, Guide.** It stands after *About this map* and *Sources* and opens the guide in the window those two
use; *Close*, or a click outside, shuts it, and an address that ends in `#open=guide` opens it. Each of the three texts
now opens at its top. The three buttons stand on one line in a window 1280 px wide; in one 1000 px wide the side panel
has no room for that, and Guide stands on a second line, under the other two.

- **The guide is `docs/GUIDE.md`**, the owner's text (36,840 bytes; sha256 `90c1b4ec636624be…`), and that file is its one source.
  `scripts/_guide.py`, a converter of its own for what the guide uses (headings, paragraphs, bold, italics, inline
  code, links, pictures, lists, pipe tables; everything else is escaped; no package), turns it into HTML when the page
  is built. The page never reads Markdown.
- **It is carried in `data.js`** as one more key, `guide_html`, beside `about_html` and `sources_html`: 923,633 bytes,
  of which 880,924 are its pictures. It holds 13 sections, 13 tables with 91 rows, and 11 links to
  8 addresses; a link opens only when clicked, in a new tab.
- **Its 5 pictures are inside that HTML**, each as its own bytes (a `data:image/webp;base64,` address), so the
  window opens without a connection and the page still asks no other site for anything. They are pictures of the
  published copy at 1280 × 800, taken by Chrome as WebP at quality 80 (`docs/guide/`); the build stops if one the guide names is
  missing:

| picture | bytes | what the guide says it shows |
|---|---|---|
| `docs/guide/01_page.webp` | 109,134 | The page as it opens |
| `docs/guide/02_unit_panel.webp` | 164,222 | A unit clicked, and its panel |
| `docs/guide/03_decision_view.webp` | 127,672 | The decision view with one district ranked |
| `docs/guide/04_why_this_tier.webp` | 147,802 | A unit's panel in the decision view, at Why this tier |
| `docs/guide/05_note.webp` | 111,858 | The note behind the legend's i, open |

- **In the window** a picture is as wide as the text, and a table wider than the window scrolls sideways inside it.
- **The copy carries the same guide**, unchanged (§11): the guide describes the published copy, and the full layer in
  this folder shows that same text.

**A loader.** While the page opens, the map's area says what the page is doing: "Loading the map…" until `data.js` has
arrived, then "Drawing the units…", and the message goes when the map is ready. The first message is plain markup,
placed before the tag that asks for `data.js`, so it shows while that file is still on its way; once the data is in,
the page changes the message, gives the browser a frame to paint it, and only then draws the units. Its bar moves and
counts nothing: `scripts/verify_layer.py` holds that the page's script never uses `fetch` or `XMLHttpRequest`, and
without them a browser reports no progress for `data.js`, so no percentage is shown. If the data never arrives, the
page says so as before.

**The sizes.** The two files were 22,500,277 bytes together before the guide (22.50 MB: `index.html` 210,942,
`data.js` 22,289,335; the layer built 2026-10-11T15:01:22Z) and are 23,427,611 bytes now (23.43 MB: `index.html` 214,465,
`data.js` 23,213,146), against the 25 MB that `scripts/verify_layer.py` allows.

**The checks.** `scripts/exercise_layer.py` gained 7 steps, in each browser (they are among the rows of §8.1 and §8.2;
53 before, 60 now):
the loader is gone once the page says it is ready; the Guide button opens the window with the guide's first heading
and a line of its last section; the window holds the five pictures, each drawn and as wide as the text; it scrolls;
*Close* shuts it; in a narrow window a table wider than it scrolls sideways inside itself; and `#open=guide` opens it.
`scripts/check_site_copy.py` holds the guide in the data to `docs/GUIDE.md`, word for word and picture for picture,
and traces every figure in the guide to a file where it is written the same way; `docs/SITE_COPY.md` is the account.
What a reader sees while the page loads was looked at in pictures of a load (`60_layer/site_copy_looked_at.json`).
