# The demo layer — `60_layer/`

*Built by `scripts/06_build_layer.py` (run 2026-10-07T08:28:39Z) from the stage tables named below; page in
`scripts/layer_template.html`; checked by `scripts/verify_layer.py`. Every figure in this document is from
`60_layer/layer.provenance.json`, a table it names, or the check record. n = 11,468 units throughout:
3,492 outside-village units and 7,976 LGD panchayat units.*

It is one map of what stages 1, 2 and 3 hold, for every unit, made to be opened by the Foundation for Ecological
Security. It needs no stage 4 and no NIRv, and it argues nothing: it shows what the tables say, unit by unit.

## 1. What is in the folder, and how to open it

| file | bytes | what |
|---|---|---|
| `index.html` | 177,426 | the map. Leaflet 1.9.4 (BSD 2-Clause) is inside it |
| `data.js` | 18,317,780 | the unit shapes and every value and class the map shows. Keep it beside `index.html` |
| `layer_by_unit.csv` | — | the numbers the map shows, one row per unit, 73 columns. Not needed to view the map |
| `layer.provenance.json` | — | inputs with hashes, the UTC run time, the simplification and its error, classes, checks |

**To open: double-click `index.html`.** The two files together are 18,495,206 bytes (18.50 MB; the limit set was
25 MB) and 5.42 MB zipped, so they can be e-mailed as one zip. The page makes **0 network
requests**: no map tiles, no fonts, no library fetched. It will open the same way with no connection, and in two
years. There is consequently no base map under the units — district outlines and names, drawn from the units
themselves, are the only orientation.

An address can point at a view: `index.html#layer=agreement&floor=50&unit=OUTSIDE_183` (layer ids are in §2).

## 2. What it shows

| layer (as titled on the map) | what is drawn | from | land a unit must have to be assessed |
|---|---|---|---|
| Area under forests | `forest_ha` / `area_ha` | `degradation_by_unit.csv`, `units.gpkg` | none: it is the layer that shows who has forest |
| Tree cover loss 2001-2025 (Hansen) | `hansen_loss_ha` / `forest_ha` | `degradation_by_unit.csv` | forest (`treecover2000` > 30) |
| Loss on open canopy, outside the forest mask (Hansen) | `hansen_loss_ha_tc_gt10le30` / `land_ha_tc_gt10le30` | `degradation_by_unit.csv` | land with 10 < `treecover2000` ≤ 30 |
| Forest health and degradation (CoRE Stack tree cover change 2017-2023) | class −1 / land with a class, on `treecover2000` > 10 | `corestack_by_unit_bands.csv` | the smaller of that land on the two grids |
| Degradation net of improvement (CoRE Stack 2017-2023) | (class −1 − class 1) / land with a class, on `treecover2000` > 10 | `corestack_by_unit_bands.csv` | the same |
| Do the two measures agree? (2017-2023) | `agreement_class` (headline window 2017–2023) | `agreement_by_unit.csv` | its own: 50 ha of reference land on both grids, fixed |
| Past allocation: expenditure on all works | `expenditure_total`, in ₹ lakh | `allocation_by_unit.csv` | — |
| Forest-named expenditure | `expenditure_forest_named_worktype`, in ₹ lakh | `allocation_by_unit.csv` | — |
| Scheduled Tribe share of population | `st_share` | `need_by_unit.csv` | — |
| Aggregate Development Index 2011 | `adi_2011` | `need_by_unit.csv` | — |
| NIRv trend | nothing: listed as *pending* | — | — |

Clicking a unit opens a panel with 42 fields: its name, type and district; area; forest and loss; loss by canopy
band; the six CoRE Stack classes as areas and shares; the agreement class and the two rates behind it; works and
expenditure; and the Census 2011 figures. Units can be filtered by type and district and found by name or id.

### Classes, with the number of units in each

The same counts are in the map's legend. Every table adds up to 11,468.

**Area under forests**

| class | units |
|---|---|
| No forest by this measure | 4,310 |
| Up to 1 % | 3,036 |
| 1 to 10 % | 1,663 |
| 10 to 30 % | 1,062 |
| 30 to 60 % | 917 |
| More than 60 % | 480 |
| **all units** | **11,468** |

**Tree cover loss 2001-2025 (Hansen)**

| class | units, floor 50 ha | units, floor 1 ha |
|---|---|---|
| No loss recorded | 263 | 1,632 |
| Up to 1 % | 912 | 1,131 |
| 1 to 2.5 % | 340 | 539 |
| 2.5 to 5 % | 281 | 461 |
| 5 to 10 % | 350 | 544 |
| 10 to 20 % | 342 | 526 |
| More than 20 % | 147 | 370 |
| Insufficient forest to assess | 8,833 | 6,265 |
| **all units** | **11,468** | **11,468** |

**Loss on open canopy, outside the forest mask (Hansen)**

| class | units, floor 50 ha | units, floor 1 ha |
|---|---|---|
| No loss recorded | 728 | 5,176 |
| Up to 1 % | 1,140 | 1,490 |
| 1 to 2.5 % | 351 | 627 |
| 2.5 to 5 % | 257 | 488 |
| 5 to 10 % | 263 | 477 |
| 10 to 20 % | 160 | 316 |
| More than 20 % | 79 | 187 |
| Insufficient forest to assess | 8,490 | 2,707 |
| **all units** | **11,468** | **11,468** |

**Forest health and degradation (CoRE Stack tree cover change 2017-2023)**

| class | units, floor 50 ha | units, floor 1 ha |
|---|---|---|
| Up to 5 % | 881 | 3,970 |
| 5 to 15 % | 1,274 | 2,446 |
| 15 to 25 % | 869 | 1,223 |
| 25 to 35 % | 456 | 565 |
| More than 35 % | 231 | 320 |
| Insufficient forest to assess | 7,757 | 2,944 |
| **all units** | **11,468** | **11,468** |

**Degradation net of improvement (CoRE Stack 2017-2023)**

| class | units, floor 50 ha | units, floor 1 ha |
|---|---|---|
| Net improvement, more than 10 points | 913 | 2,229 |
| Net improvement, 2 to 10 points | 749 | 1,903 |
| Within 2 points: no net change | 518 | 2,000 |
| Net degradation, 2 to 10 points | 740 | 1,300 |
| Net degradation, 10 to 20 points | 416 | 585 |
| Net degradation, more than 20 points | 375 | 507 |
| Insufficient forest to assess | 7,757 | 2,944 |
| **all units** | **11,468** | **11,468** |

**Do the two measures agree? (2017-2023)**

| class | units |
|---|---|
| Both measures flag this unit | 255 |
| Hansen only (clearance) | 487 |
| CoRE Stack only (degradation) | 487 |
| Neither | 2,482 |
| Insufficient forest to assess | 7,757 |
| **all units** | **11,468** |

**Past allocation: expenditure on all works**

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

**Forest-named expenditure**

| class | units |
|---|---|
| Up to Rs 1 lakh | 850 |
| Rs 1 to 5 lakh | 1,042 |
| Rs 5 to 20 lakh | 754 |
| More than Rs 20 lakh | 127 |
| None | 8,667 |
| Works recorded, expenditure not | 28 |
| **all units** | **11,468** |

**Scheduled Tribe share of population**

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

1. **Too little forest is a class, not a colour on the scale.** A loss rate on a few hectares is noise. In
   `20_degradation/forest_floor_repeatability.csv` the rank correlation of a unit's Hansen loss rate between odd and
   even years is 0.34 for units with 1 to 2 ha of forest, 0.77 with 25 to 50 ha, 0.81 with 50 to 100 ha and 0.94
   with 500 to 1,000 ha. So on
   every layer that is a rate on forest land a unit below a minimum of that land is drawn flat grey, **"insufficient
   forest to assess"**. The map offers two minimums: **50 ha, the default** — the floor proposed for stage 4, which
   the project owner has not ruled on — and **1 ha**, every unit with measurable forest. At 50 ha, 8,833 units
   are in that class on the Hansen layer; at 1 ha, 6,265. The agreement layer has its own floor, fixed at 50 ha of
   reference land on both grids (7,757 units insufficient).
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
formatted as text in Python. **The page's script looks text up and draws; it computes nothing** — no sum, no share,
no rounding. Inputs of the run:

| input | bytes | SHA-256 |
|---|---|---|
| `10_units/units.gpkg` | 48,369,664 | `ee86f0c3ac99c0c4…` |
| `00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` | 6,289 | `a2e2cc9c7df1a9b1…` |
| `10_units/outside_village_district.csv` | 536,828 | `763630369d3a544c…` |
| `20_degradation/degradation_by_unit.csv` | 3,628,329 | `072e281b53087823…` |
| `20_degradation/corestack_by_unit_bands.csv` | 2,902,891 | `d59e23e87b62c37b…` |
| `20_degradation/agreement_by_unit.csv` | 2,145,059 | `36f177e75b325055…` |
| `30_need/need_by_unit.csv` | 1,212,483 | `0fc54bd7eb2a6d84…` |
| `40_allocation/allocation_by_unit.csv` | 1,072,899 | `3f81d2d3edefda9f…` |
| `20_degradation/hansen_by_unit_level.csv` | 1,090 | `46d77ed69eac08ca…` |
| `20_degradation/forest_floor_options.csv` | 1,636 | `f7bb4e1859aa7c6a…` |
| `20_degradation/agreement.provenance.json` | 7,039 | `c7557f683c0af31c…` |
| `20_degradation/forest_floor_repeatability.csv` | 991 | `800c61adc7c22132…` |
| `20_degradation/agreement_summary.csv` | 10,725 | `bbd59a6a06261b1e…` |
| `20_degradation/agreement_intervals_by_district.csv` | 2,936 | `361c7ceba1bd5d4f…` |
| `40_allocation/panchayat_of_record_check.csv` | 363 | `f36e1bd24b73ce67…` |
| `10_units/units.provenance.json` | 1,706 | `7a7aa9077c79b68d…` |
| `20_degradation/hansen.provenance.json` | 8,637 | `d6e816740e7dd41a…` |
| `20_degradation/corestack.provenance.json` | 12,320 | `8f03282fa339d4a3…` |

The builder stops unless: the class counts above equal the stage tables' own counts (units with no forest, under
1 ha and under 50 ha; the five agreement classes; the units with no census rows); forest and loss total what the
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
- Plain outlines for administrative units; "Area under forests", "Forest health and degradation" as layer names.

Where it departs, and why:

- **Deforestation and Afforestation will not match CoRE Stack's published block rasters.** Those take the two outer
  classes from a land-use change product; this layer reads all classes from the tree-change asset itself
  (`docs/DEGRADATION.md` §4a). Degradation, Partially Degraded, No Change and Improvement are the same thing.
- The unit is the **LGD panchayat unit or a tract of land outside every village**, not a micro-watershed or a
  tehsil; and a unit polygon is not the panchayat of record for the works inside it (README §5.8).
- Past allocation is the geotagged asset record, 97.8 per cent of which predates FY2017-18 (README, stage 4).
  It is what was built where, not what is being spent now.

## 7. Licences, and what was left out

The map's *Sources and licences* panel lists each of these with its terms:

| what | source | licence or terms |
|---|---|---|
| tree canopy 2000, tree cover loss 2001–2025 | Hansen et al., Global Forest Change v1.13, through Google Earth Engine; totals reconciled to Global Forest Watch | CC BY 4.0 |
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
  dropping `adi_2011` is one line in `06_build_layer.py`.

## 8. How it was verified

A map that renders is not a map that is correct, so this was checked by looking, not by re-running.

**By hand, in a browser.** The built map was opened in Chrome, 16 units were clicked, and every value the panel
displayed was read off the page and compared with the stage tables — 656 of 656 values equal. The units were
chosen to span forest from none to the largest, both kinds of unit, and the awkward cases:

| | chosen as | unit | type | forest, ha | values equal |
|---|---|---|---|---|---|
| A | free click, Mayurbhanj | `132731` | lgd panchayat | 50,768.70 | 41 of 41 |
| B | free click, Kendujhar | `OUTSIDE_183` | outside village | 10,235.40 | 41 of 41 |
| C | free click, Kendrapara | `133949` | lgd panchayat | 0.00 | 41 of 41 |
| D | free click, Kandhamal | `137247` | lgd panchayat | 977.51 | 41 of 41 |
| E | free click, Malkangiri | `OUTSIDE_3185` | outside village | 29,576.74 | 41 of 41 |
| F | lgd, no forest | `137771` | lgd panchayat | 0.00 | 41 of 41 |
| G | lgd, 1 to 50 ha of forest | `131999` | lgd panchayat | 32.95 | 41 of 41 |
| H | lgd, both measures flag | `138534` | lgd panchayat | 1,294.74 | 41 of 41 |
| I | lgd, works but no expenditure, no population | `132539` | lgd panchayat | 0.00 | 41 of 41 |
| J | aimed at 133172, the click landed on its neighbour | `133170` | lgd panchayat | 0.07 | 41 of 41 |
| K | lgd in Anugul with the most forest | `135472` | lgd panchayat | 9,702.92 | 41 of 41 |
| L | outside, large forest | `OUTSIDE_1855` | outside village | 5,985.32 | 41 of 41 |
| M | aimed at OUTSIDE_387, the click landed on its neighbour | `131760` | lgd panchayat | 616.16 | 41 of 41 |
| N | outside, district ambiguous | `OUTSIDE_1229` | outside village | 0.65 | 41 of 41 |
| O | outside, no name, district by neighbours, no forest | `OUTSIDE_3062` | outside village | 0.00 | 41 of 41 |
| P | outside, under 1 ha of forest | `OUTSIDE_3327` | outside village | 0.15 | 41 of 41 |

Two of the clicks landed on a neighbour of the unit aimed at; the unit that opened is the one that was checked.
The legend on the agreement and Scheduled Tribe layers, the 1 ha floor and the two text panels were looked at on screen.

**Then every unit, by script**, because sixteen is not 11,468: `scripts/verify_layer.py` rebuilds every displayed
field of every unit from the stage tables — not from `layer_by_unit.csv` — and every class at both floors, and
compares them with what `data.js` holds: **79 of 79 checks passed; n = 11,468 units, 42 fields a unit, 14 class arrays**. On its first run it failed 6 of 77 checks, and they were real
(CoRE Stack shares built from two tables rounded differently, so six classes summed to 99.97 per cent; units classed
on an unrounded value that printed on the other side of a class boundary). Both were fixed in the builder.

**Opened from disk.** The browser automation used for the clicking cannot open a `file://` address, so the clicking
was done on the same two files served from this machine, and the double-click case was verified separately: headless
Chrome loaded `file://…/60_layer/index.html` with a unit and a layer in the address, and the rendered page held that
unit's panel and that layer's legend, with no script error.

**The build that was clicked, and the builds since.** The sixteen units were clicked on the build of
2026-10-06T20:43:03Z. The layer has been rebuilt three times since, after the review pass of 7 October: when
`degradation_by_unit.csv` gained one empty NIRv column; to replace the interval quoted in the *About* text with the one
from resampling whole districts (`docs/DEGRADATION.md` §4b) and to record every file the builder reads; and when the
district of the outside-village units was redone (`docs/UNITS.md`). The first two touched no per-unit value. **The
third changed one displayed field, the district line, for outside-village units**: 21 of them carry a different
district, and 52 a different line in all (the way the district was assigned, or the ambiguity flag). 2 of the
sixteen clicked units are among those (`OUTSIDE_1229`, `OUTSIDE_3062`); their new district lines, and that of `OUTSIDE_1200`,
the unit the review singled out, were read off the page again, from disk, in headless Chrome, and equal
`outside_village_district.csv` (3 of 3 lines equal: OUTSIDE_1229, OUTSIDE_3062, OUTSIDE_1200). Every other field of every unit rests on
tables that are byte for byte the same, and `verify_layer.py` passed after each rebuild (79 of 79 checks passed on the
build of 2026-10-07T08:28:39Z); it now also checks that each outside-village unit's line says the way *its* district was
assigned. The changed sentence of the *About* text was confirmed in `data.js`; the panel was not opened on screen again.

**Not checked:** the type and district filters and the search box, beyond their loading; any browser other than Chrome; a phone or a small screen; printing; a machine with less memory
(the data file is 18 MB of script); and whether the Foundation's staff read the class names as intended.

## 9. Before it is shown

- It is a map of units. A unit flagged by both measures is a place to look, not a finding about a village.
- The paper this layer borrows its vocabulary from reports that in one of its pilot blocks, Angul, in this state, the
  community did not favour mapping inequity (Commons Connect, ICTD 2024, p. 18). The Scheduled Tribe share and
  development index layers are of that kind. Whether they belong in what is shown is the Foundation's call.
- Nothing here says why a unit lost forest or was passed over for work. Stage 4, not built, is where that is argued.

## 10. To rebuild

```
.venv/bin/python scripts/06_build_layer.py --units 10_units/units.gpkg
.venv/bin/python scripts/verify_layer.py
```

`60_layer/` is git-ignored: it is rebuilt from the stage tables, and `data.js` is 18 MB. When NIRv lands as a
column of `degradation_by_unit.csv` the layer is not changed by it; NIRv is a reported column, not a measure, and
stays listed as it is unless the owner asks for it to be drawn.
