# Stage 1 — forest condition per unit

*Built by `scripts/02_upload_units_asset.py`, `02_build_hansen.py`, `02_build_corestack.py`, `02_build_agreement.py`,
`02_assemble_degradation.py` and `02_propose_forest_floor.py` (shared code in `scripts/_ee_units.py`); NIRv by
`02_export_nirv_observations.py`, `02_export_nirv_yearly.py` and `02_build_nirv.py`. Every figure below is from `20_degradation/*.provenance.json`, the tables beside
them, or `00_raw/`. All 11,468 units of the base layer are measured, the 3,492 outside-village units included, and
every table gives them separately.*

**Stage 1 rests on two measures (ruling of 7 October 2026).** Hansen is the validated floor. What Hansen cannot see —
thinning under a standing canopy, and change on land that was already open in 2000 — is what CoRE Stack's
degradation classes record. `degradation_by_unit.csv` holds the two side by side for every unit, and §4b sets them
against each other. A third source, an NIRv trend from Landsat 8, was built, independently replicated, and found
unfit to be a degradation measure: its trend moves one for one with the correction applied for the date of each
image. That is a result, and it is §5. NIRv stays in the table as a reported column.

| source | what it measures | role | state |
|---|---|---|---|
| Hansen Global Forest Change | stand-replacing loss of tree cover, by year 2001–2025, on a year-2000 canopy mask | measure: the validated floor | built, independently replicated twice |
| CoRE Stack tree-change classes | a change of class in canopy density or height between about 2016–19 and 2022–25, inside the producers' tree mask | measure: thinning, and change outside Hansen's mask | built (run 2026-10-05T21:40:02Z); reconciled to the producers' one published Odisha figure |
| NIRv trend from Landsat 8 | a decline in November–December greenness, 2013–2025 | **a reported column, not a measure** (§5) | pending, and **nothing is queued** — 72 of 84 tiles of stored observations exist (2026-10-07T08:36:08Z); the other 12 and the 13 blocks of yearly values were cancelled from outside this pipeline on 7 October, with every other pending task of the project, and the chain stopped (§6, §10). Queueing them again is the project owner's decision; the columns of `degradation_by_unit.csv` stay blank until then |

## 1. Hansen: forest, and the land the planning system has no population figures for

Forest is **`treecover2000` > 30**: more than 30 per cent canopy in the year 2000 (the inequality is discussed in §2).

| | units | area, km² | forest, km² | forest, % of area | share of all forest, % | loss 2001–2025, km² | share of all loss, % | loss, % of forest |
|---|---|---|---|---|---|---|---|---|
| outside-village units | 3,492 | 41,356 | 15,830 | 38.3 | **59.4** | 887.8 | **57.2** | 5.61 |
| LGD panchayat units | 7,976 | 113,565 | 10,800 | 9.5 | 40.6 | 664.8 | 42.8 | 6.16 |
| all units | 11,468 | 154,922 | 26,630 | 17.2 | 100.0 | 1,552.6 | 100.0 | 5.83 |

The outside-village units are 27 per cent of the area and hold 59 per cent of the forest and 57 per cent of
the tree-cover loss. They have no census rows, so stage 2 is blank for all of them and they cannot enter a
per-capita comparison of need with allocation — yet stage 3 finds 131,687 works worth ₹1,443.5 crore geotagged
inside them. That asymmetry is a result of its own.

2,271 of the 3,492 outside-village units and 4,887 of the 7,976 LGD panchayat units have some forest;
4,310 units have none and 6,265 have under a hectare (those with none included). Counts of this kind run a handful low:
Earth Engine returns 0.0000 for a sliver of a pixel.

Columns of `hansen_by_unit.csv` (n = 11,468; blank cells: none):

| column | meaning |
|---|---|
| `forest_ha` | area of pixels with `treecover2000` > 30 inside the unit |
| `hansen_loss_ha_2001` … `_2025` | area of those pixels whose `lossyear` is that year |
| `hansen_loss_ha` | their sum, 2001–2025 |
| `missing_data_share` | area inside the unit where Hansen's `datamask` is 0, over the unit's area |

`missing_data_share` is zero in every unit and could not be otherwise: Hansen's no-data class is open sea in
this window. It is not a measure of data quality.

| year | loss in the mask, km² |
|---|---|
| 2001 | 29.6 |
| 2002 | 39.4 |
| 2003 | 53.6 |
| 2004 | 44.4 |
| 2005 | 35.9 |
| 2006 | 42.1 |
| 2007 | 58.8 |
| 2008 | 59.1 |
| 2009 | 47.8 |
| 2010 | 23.9 |
| 2011 | 55.7 |
| 2012 | 37.5 |
| 2013 | 53.5 |
| 2014 | 74.7 |
| 2015 | 38.7 |
| 2016 | 83.1 |
| 2017 | 101.0 |
| 2018 | 97.8 |
| 2019 | 77.6 |
| 2020 | 88.9 |
| 2021 | 48.8 |
| 2022 | 79.0 |
| 2023 | 116.4 |
| 2024 | 83.6 |
| 2025 | 81.7 |

Loss is stand-replacing removal of tree cover from any cause, plantation and natural forest alike; it is not
deforestation and it cannot see a forest that thins under a standing canopy. Gain is not netted off. The
producers mapped 2011 onward with an updated method, so the step between 2010 and 2011 is partly the method.

## 2. The mask is a choice, and the inequality matters

**Ruling of 6 October 2026: the mask is `treecover2000` > 30, strictly above.** Two reasons. It is the commoner
written form in the literature, "greater than 30%" (the project owner's reading; not checked here). And it is
what Global Forest Watch, which distributes this dataset, actually computes. Its notes say "The Global Forest Watch website uses a >=30% canopy cover threshold as a default for all statistics" — yet on
its own boundary the public tiles reproduce its published Odisha figures to within about a hectare with > 30 and
miss them by 0.43 per cent with ≥ 30 (independent replication, §9). The notes and the numbers disagree; this
pipeline follows the numbers and writes the inequality out everywhere. There is no bare "at 30" in any output.

| mask | forest, km² | in LGD panchayat units | in outside-village units | outside-village share, % | relative to the mask used | loss 2001–2025, km² |
|---|---|---|---|---|---|---|
| `treecover2000` > 10 | 37,517 | 17,036 | 20,481 | 54.6 | 1.41 | 1,916.5 |
| `treecover2000` > 30 **(used)** | 26,630 | 10,800 | 15,830 | 59.4 | 1.00 | 1,552.6 |
| `treecover2000` > 50 | 15,572 | 5,726 | 9,846 | 63.2 | 0.58 | 1,046.1 |
| `treecover2000` >= 30 | 26,745 | 10,870 | 15,875 | 59.4 | 1.00 | 1,555.8 |

The pixels at exactly 30 per cent are 11,471 ha of forest (0.43 per cent of the ≥ 30 figure) and 314.7 ha of loss.
Every unit's figures at > 10, > 50 and ≥ 30 are in `hansen_by_unit_thresholds.csv`. The mask is fixed at the year
2000: loss is counted in `hansen_loss_ha` only where there was more than 30 per cent canopy then. That is not all
closed forest — about a seventh of the mask has canopy of 31 to 39 per cent.

## 3. What the mask leaves out: loss by year-2000 canopy (task A)

`hansen_loss_ha` counts 54.8 per cent of the Hansen loss inside the units. The rest is on pixels that had 30 per cent
canopy or less in 2000. Every pixel is in exactly one band; `hansen_loss_by_canopy_band.csv` and
`hansen_loss_by_canopy_band_by_unit.csv` carry them (n = 15 rows and 11,468 units).

**All units**

| year-2000 canopy | land, km² | loss 2001–2025, km² | % of these units' loss | loss as % of the band's land | 2001–2010 | 2011–2017 | 2018–2025 | units with loss |
|---|---|---|---|---|---|---|---|---|
| `treecover2000` > 30 (the forest mask) | 26,630 | 1,552.6 | 54.8 | 5.83 | 434.6 | 444.2 | 673.8 | 3,830 |
| 10 < `treecover2000` ≤ 30 | 10,887 | 363.8 | 12.8 | 3.34 | 23.4 | 114.0 | 226.5 | 3,638 |
| `treecover2000` ≤ 10 | 117,404 | 917.4 | 32.4 | 0.78 | 45.1 | 244.8 | 627.5 | 5,291 |
|   of which `treecover2000` = 0 | 114,612 | 825.9 | 29.1 | 0.72 | 37.6 | 217.8 | 570.5 | 5,222 |
| all land | 154,922 | 2,833.9 | 100.0 | 1.83 | 503.1 | 803.0 | 1,527.8 | 5,778 |

**Outside-village units**

| year-2000 canopy | land, km² | loss 2001–2025, km² | % of these units' loss | loss as % of the band's land | 2001–2010 | 2011–2017 | 2018–2025 | units with loss |
|---|---|---|---|---|---|---|---|---|
| `treecover2000` > 30 (the forest mask) | 15,830 | 887.8 | 58.5 | 5.61 | 256.5 | 266.6 | 364.7 | 1,419 |
| 10 < `treecover2000` ≤ 30 | 4,651 | 183.9 | 12.1 | 3.96 | 10.7 | 63.0 | 110.3 | 1,300 |
| `treecover2000` ≤ 10 | 20,876 | 444.6 | 29.3 | 2.13 | 18.6 | 141.7 | 284.3 | 1,619 |
|   of which `treecover2000` = 0 | 19,923 | 398.5 | 26.3 | 2.00 | 15.2 | 126.5 | 256.8 | 1,588 |
| all land | 41,357 | 1,516.3 | 100.0 | 3.67 | 285.7 | 471.3 | 759.3 | 1,825 |

**LGD panchayat units**

| year-2000 canopy | land, km² | loss 2001–2025, km² | % of these units' loss | loss as % of the band's land | 2001–2010 | 2011–2017 | 2018–2025 | units with loss |
|---|---|---|---|---|---|---|---|---|
| `treecover2000` > 30 (the forest mask) | 10,800 | 664.8 | 50.5 | 6.16 | 178.1 | 177.6 | 309.1 | 2,411 |
| 10 < `treecover2000` ≤ 30 | 6,236 | 179.9 | 13.7 | 2.88 | 12.8 | 50.9 | 116.2 | 2,338 |
| `treecover2000` ≤ 10 | 96,529 | 472.8 | 35.9 | 0.49 | 26.5 | 103.1 | 343.2 | 3,672 |
|   of which `treecover2000` = 0 | 94,689 | 427.4 | 32.4 | 0.45 | 22.4 | 91.3 | 313.7 | 3,634 |
| all land | 113,565 | 1,317.5 | 100.0 | 1.16 | 217.4 | 331.7 | 768.5 | 3,953 |

What this does and does not show:

- **1,281 of 2,834 km² of Hansen loss is outside the mask**: 364 km² on 10 < `treecover2000` ≤ 30 and 917 km²
  on `treecover2000` ≤ 10. 1,948 units have Hansen loss and a `hansen_loss_ha` of zero.
- **Most of that is not forest that stood in 2000.** 826 km² — 90 per cent of the lowest band's loss — is on pixels with
  **no canopy at all in 2000**. A pixel with no trees had no forest to lose: loss recorded there is tree cover that
  grew after 2000 and was then removed (a plantation felled, regrowth cleared), or an artefact of detection.
- **Its rise over time is largely the method.** Loss on `treecover2000` ≤ 10 goes 45 → 245 → 627 km² across
  the three periods, a 14-fold rise, while loss in the mask goes 435 → 444 → 674. The independent check
  (§9) dated the steps to 2011, 2013 and 2023 and found the same pattern in Global Forest Watch's own published
  figures. Do not read it as a trend on the ground.
- **The band 10 < `treecover2000` ≤ 30 is the one that bears on open forest**: 10,887 km² of land, 3.3 per cent
  of it lost, half of it in outside-village units. It is small beside the mask (26,630 km², 5.8 per cent lost).
- **In outside-village units nearly half the land had no canopy in 2000** (19,923 of 41,357 km²), and loss on it
  runs at 2.0 per cent against 0.45 in the villages' open land.

So the mask does hide a large area of recorded loss, but Hansen cannot say that this area is degraded forest. What
it shows is tree cover coming and going on land that was open in 2000. Whether forest that was already open is
getting worse is a question for a measure of condition, not of clearance.

## 4. CoRE Stack, and whether it agrees with Hansen

### 4a. CoRE Stack tree-change classes (task C)

`corestack_by_unit.csv`, n = 11,468 units; blank cells: `corestack_missing_share` in 11 units that have no value at all.

**What the product is** (from the producers' own code, metadata and paper; every statement below was opened and
re-opened by a second reader, sources in §11). `overall_change_2017_2023` is a 25 m raster in eleven pieces, one per
agro-climatic zone; two of them cover the units. Its classes: −2 tree cover lost, −1 degradation, 0 no change,
1 improvement, 2 tree cover gained, 3 and 4 partially degraded, 5 missing; no value outside the producers' tree mask.
Three things decide how it can be used:

- **"Degradation" is a class crossing, not a measured loss.** Canopy density and canopy height are each a
  classifier's answer to "above or below this zone's median" — 60 per cent canopy density in the Eastern Plateau
  and Hills zone, 67 in the East Coast Plains and Hills. Class −1 means a pixel went from High to Low. A stand
  that thins from 90 to 70 per cent canopy is "no change"; a stand already Low cannot register degradation at all.
- **The classifiers were right about two times in three** on held-out data (64 to 67 per cent), and the producers
  validated only class −2: "No ground truth is however available for afforestation, improvement, or degradation
  changes in tree cover."
- **Its "tree cover" is far wider than forest.** It is the union of LULC v3 class 6 and Dynamic World's tree class,
  and each "year" is three agricultural years taken together: the product compares roughly 2016–19 with 2022–25.

**The mapping (a decision):** `corestack_loss_ha` = class −2; `corestack_degradation_ha` = class −1 **only**;
`corestack_partial_degradation_ha` = classes 3 + 4, kept out of degradation because in each one of density and
height went up while the other went down; `corestack_improvement_ha` = class 1; `corestack_gain_ha` = class 2;
missing = class 5 over all pixels with a value (0.016 per cent; 18.5 km²). Pixels with no value
(35,615 km²) are their own column, not missing data.

**As the producers define it (all land inside their tree mask)**

| | tree cover at the start, km² | lost (−2) | degradation (−1) | partial (3 + 4) | improvement (1) | gained (2) | net (−1 minus 1) | downward share (95 % interval) |
|---|---|---|---|---|---|---|---|---|
| outside-village units | 35,329 | 1,008 | 6,805 | 357 | 4,231 | 1,121 | +2,574 | 0.62 (0.58–0.65) |
| LGD panchayat units | 74,628 | 5,984 | 6,887 | 343 | 6,336 | 8,229 | +551 | 0.52 (0.50–0.54) |
| all units | 109,957 | 6,991 | 13,692 | 700 | 10,568 | 9,350 | +3,125 | 0.56 (0.55–0.59) |

**On the common reference, land with `treecover2000` > 10** (the columns ending `_tc_gt10`)

| | tree cover at the start, km² | lost (−2) | degradation (−1) | partial (3 + 4) | improvement (1) | gained (2) | net (−1 minus 1) | downward share (95 % interval) |
|---|---|---|---|---|---|---|---|---|
| outside-village units | 20,411 | 57 | 5,527 | 277 | 3,124 | 30 | +2,403 | 0.64 (0.60–0.68) |
| LGD panchayat units | 16,888 | 76 | 3,564 | 204 | 2,401 | 51 | +1,163 | 0.60 (0.56–0.64) |
| all units | 37,299 | 133 | 9,091 | 481 | 5,524 | 81 | +3,566 | 0.62 (0.59–0.65) |

**By band of year-2000 canopy, all units**

| year-2000 canopy | land, km² | tree cover at the start | lost (−2) | degradation (−1) | improvement (1) | gained (2) | downward share (95 % interval) |
|---|---|---|---|---|---|---|---|
| `treecover2000 = 0` | 114,611 | 69,933 | 6,812 | 4,355 | 4,815 | 9,243 | 0.47 (0.47–0.48) |
| `0 < treecover2000 <= 10` | 2,793 | 2,725 | 46 | 246 | 228 | 26 | 0.52 (0.50–0.53) |
| `10 < treecover2000 <= 30` | 10,886 | 10,732 | 81 | 1,367 | 1,178 | 55 | 0.54 (0.52–0.56) |
| `treecover2000 > 30` | 26,632 | 26,568 | 52 | 7,724 | 4,347 | 26 | 0.64 (0.61–0.67) |

**By zone image, all units, all land** — the two zones are separate models with different thresholds

| zone | tree cover at the start, km² | degradation (−1) | improvement (1) | downward share (95 % interval) |
|---|---|---|---|---|
| EPAHR | 87,103 | 11,403 | 9,786 | 0.54 (0.52–0.56) |
| ECPHR | 22,851 | 2,289 | 781 | 0.75 (0.71–0.78) |

What it shows:

- **The product's tree cover is 71 per cent of the units' area** (109,957 km²) — against 24 per cent with Hansen
  canopy above 10 per cent in 2000 and ISFR's 33.7 per cent forest cover. LULC v3 class 6 alone is 87,801 km² in
  2017–18 and 84,925 km² in 2023–24, 67 and 62 per cent above ISFR 2023's 52,433.56 km². It is not expected to agree: a 10 m
  classifier's "trees" takes in orchards, trees on farms and, by the producers' rule, steep cropland.
- **"Lost" and "gained" are mostly farmland changing label.** In the sample, 527 of 539 "lost" points have no Hansen
  canopy at all in 2000, and 0 of them has Hansen loss dated 2018–2023. Class −2 is 86 per cent in LGD
  panchayat units. It is not forest loss; §4b carries it as a state of its own beside class −1.
- **Most of classes −1 and 1 is churn, and what is left over is in the denser forest.** On land with `treecover2000` > 10 the product puts 24 per cent of the
  tree cover in class −1 and 15 per cent in class 1. Two fifths of the forest changing class in six years is more than a forest does; it is what
  classifiers that are right about two times in three produce. The downward share — class −1 over class −1 plus class 1, one half meaning no net signal — is 0.47 (0.47–0.48) on land with no canopy in 2000,
  0.54 (0.52–0.56) on 10 < `treecover2000` ≤ 30 and 0.64 (0.61–0.67) on `treecover2000` > 30. So the net of the two, +3,566 km² on `treecover2000` > 10, is almost all
  (+3,378 km²) on canopy above 30 per cent; on the open forest between 10 and 30, where Hansen's mask is blind, it is +189 km² of 2,544 km² gross.
  Improvement is the noise reference for degradation: read the net and the downward share, never class −1 alone.
- **The net depends on the zone model.** The East Coast Plains and Hills image has a downward share of 0.75 (0.71–0.78), the Eastern Plateau and Hills image 0.54 (0.52–0.56).
  They are separate classifiers with different thresholds (67 and 60 per cent canopy density), so part of the difference is the models and not the land;
  in outside-village units the two are 0.83 (0.78–0.87) and 0.58 (0.55–0.62).
- **By unit type, on `treecover2000` > 10:** outside-village units 5,527 km² in class −1 against 3,124 in class 1 (downward share 0.64 (0.60–0.68));
  LGD panchayat units 3,564 against 2,401 (0.60 (0.56–0.64)). The intervals overlap: on the downward share the product does not separate the two.
- **Half of class −1 is in outside-village units** (6,805 of 13,692 km²), where it is 19 per cent of the product's tree
  cover against 9 per cent in LGD panchayat units.
- **It is weakly related to Hansen.** In the sample, on land with `treecover2000` > 10, class −1 is 16 of 40 valued points
  with Hansen loss dated 2019–2023 (40 per cent) against 668 of 2,914 with no Hansen loss (23 per cent). And class −2 is not Hansen's loss: on `treecover2000` > 10 it is 133 km² in all, while 6,812 of its 6,991 km² lie on land with no canopy in 2000.

**Reconciled to the one Odisha figure the producers print.** Their paper gives Mayurbhanj district 189 thousand hectares degraded between 2017 and 2021. Their own 2017–2021 product, read the way this script reads the 2017–2023 one and counted their way (class −1 pixels × 625 m²) over FAO GAUL's Mayurbhanj, gives **189.2 thousand hectares**. The run stops if that is more than 2% out. The same tally on the 2017–2023 product gives 226.1.

Nothing in the 2017–2023 tallies themselves can be set against a published number: the producers print no total
for 2017–2023 and none for Odisha as a state. Their own area convention counts 625 m² for every pixel; on the
ellipsoid a pixel of this grid is 582.4 m² here, so their convention gives 7.3 per cent more area from the same
pixels. All figures in this document are ellipsoidal. The two zone images lie on one lattice (origins a whole
number of pixels apart), so nothing is resampled; they both have a value on 17.5 km² and differ on 0.00 km² of it.

### 4b. Do Hansen and CoRE Stack point at the same units? (task D)

**State: built for all 11,468 units (run 2026-10-07T08:26:04Z), from the two sources' own per-unit tables; no Earth Engine. Its
arithmetic was then rebuilt by a script that imports nothing from the builder (`scripts/verify_agreement.py`:
55 of 55 checks passed; its docstring lists what it re-derives and what it only checks — the bootstrap intervals are
checked, not rebuilt).** Tables: `agreement_by_unit.csv`, `agreement_summary.csv`, `agreement_definitions.csv`, and three
that say what the first three assume: `agreement_intervals_by_district.csv`, `agreement_by_zone.csv`,
`agreement_floor_repeatability.csv`. NIRv is not in this table (§5).

**What is compared, and at what scale.** Hansen dates the outright removal of tree cover. CoRE Stack classes a 25 m
pixel inside its own tree mask by whether canopy density or height moved a class between two three-year periods. They
do not measure the same thing and are not expected to mark the same pixels: Hansen is blind to thinning, and CoRE
Stack's class −1 is thinning under a canopy that still stands. The question the project needs answered is whether
they point at the same *units*. So this is a table of units, not of pixels.

- **One reference land for both:** land with `treecover2000` > 10 (36,853 km² in the assessed units). A unit's Hansen rate is its loss dated in the
  window on that land, over that land; its CoRE Stack rates are the area of a class on that land over the land there
  that has a class from −2 to 4.
- **A unit is assessed** only if it has at least 50 ha of that land on both sources' grids: 3,711 of 11,468 units
  (2,504 LGD panchayat, 1,207 outside-village). The other 7,757 are *insufficient forest*, a class of their own — not "neither".
- **A unit is flagged** by a measure if its rate is in the top fifth of the assessed units' rates (Hansen: more than
  2.27 per cent of the reference land lost in 2017–2023; CoRE Stack: more than 24.0 per cent of the valued land in class −1). The
  flag is relative. It says "among the worst fifth", not "degraded by some amount": no absolute threshold has a basis.

**The headline window is 2017–2023:** Hansen loss dated 2017 to 2023 beside CoRE Stack's change 2017–2023, the span
the CoRE Stack product itself names. Two other windows are given below in rows of their own and are never pooled or
averaged with it.

**That window is the period of the change in allocation this project sets out to explain — which is a reason to
prefer it, not a limitation.** In the scheme's own district reports (R6.20, `00_raw/mis_reports/`) plantation was
24.2 per cent of Odisha's MGNREGA expenditure in 2016-17 and 18.6 in 2017-18; in 2018-19 it was 3.3, and it has not reached
one per cent in any year since. Over the same years water rose from 40 to 64 per cent of natural-resource
expenditure. The window opens as the plantation money stops:

| financial year | plantation, % of all expenditure | water, % of NRM expenditure |
|---|---|---|
| 2014-2015 | 21.39 | 40.1 |
| 2015-2016 | 17.55 | 39.8 |
| 2016-2017 | 24.17 | 44.6 |
| 2017-2018 | 18.62 | 41.3 |
| 2018-2019 | 3.34 | 50.5 |
| 2019-2020 | 0.33 | 50.9 |
| 2020-2021 | 0.03 | 56.0 |
| 2021-2022 | 0.01 | 58.0 |
| 2022-2023 | 0.02 | 60.8 |
| 2023-2024 | 0.03 | 62.0 |
| 2024-2025 | 0.63 | 63.7 |

So what the two measures record over 2017–2023 is the condition of the forest in exactly the years in which the
scheme stopped paying for it. A measure ending in 2016 could say nothing about that. (This is alignment in time. It
is not, by itself, evidence that one caused the other; stage 4 is where that is argued.)

**The headline.** Units flagged by both, beside the number two unrelated flags of those sizes would share. Intervals
are 95 per cent, from resampling **whole districts** (28 districts hold the assessed units) — see *What the intervals
assume*, below.

| | units | insufficient forest | assessed | flagged by Hansen | flagged by CoRE Stack | **by both** | expected if unrelated | observed / expected | odds ratio | Hansen only | CoRE Stack only | neither |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all units | 11,468 | 7,757 | 3,711 | 742 | 742 | **255** | 148.4 | 1.72 (1.34–2.33) | 2.67 (1.70–4.37) | 487 | 487 | 2,482 |
| LGD panchayat units | 7,976 | 5,472 | 2,504 | 456 | 391 | **129** | 71.2 | 1.81 (1.24–2.76) | 2.69 (1.40–5.48) | 327 | 262 | 1,786 |
| outside-village units | 3,492 | 2,285 | 1,207 | 286 | 351 | **126** | 83.2 | 1.51 (1.29–2.05) | 2.44 (1.78–4.22) | 160 | 225 | 696 |

Rank correlation (Spearman) across assessed units between the Hansen rate 2017–2023 and each CoRE Stack rate, with
the same intervals. Class 1, *improvement*, is the placebo: it comes from the same classifiers as class −1 and should
not go with clearance.

| | class −1 (degradation) | class −1 minus class 1 (net) | classes −1, 3, 4 | class −2 (tree cover lost) | class 1 (improvement, the placebo) |
|---|---|---|---|---|---|
| all units | 0.36 (0.22–0.47) | 0.25 (0.10–0.39) | 0.36 | 0.18 (0.07–0.26) | 0.03 (−0.12 to 0.14) |
| LGD panchayat units | 0.37 (0.18–0.51) | 0.24 (0.08–0.40) | 0.36 | 0.15 (0.03–0.26) | 0.03 (−0.12 to 0.15) |
| outside-village units | 0.32 (0.23–0.42) | 0.23 (0.13–0.36) | 0.32 | 0.32 (0.21–0.41) | −0.00 (−0.15 to 0.11) |

**What the intervals assume.** The intervals in `agreement_summary.csv` resample units one at a time, as if each unit
were an independent draw. They are not — neighbouring units share forest, terrain and administration — and what that
assumption hides shows when whole districts are resampled instead: every interval is 2.7 to 4.8 times wider (all units):

| | estimate | 95 % interval, units resampled singly | **whole districts resampled** | times wider |
|---|---|---|---|---|
| odds ratio | 2.67 | 2.20–3.19 | **1.70–4.37** | 2.7 |
| observed / expected | 1.72 | 1.57–1.87 | **1.34–2.33** | 3.3 |
| rank correlation with class −1 | 0.36 | 0.34–0.39 | **0.22–0.47** | 4.6 |
| with class −1 minus class 1 | 0.25 | 0.21–0.27 | **0.10–0.39** | 4.8 |
| with class −2 | 0.18 | 0.15–0.21 | **0.07–0.26** | 3.0 |
| with class 1 (the placebo) | 0.03 | −0.00 to 0.06 | **−0.12 to 0.14** | 4.1 |

**The district intervals are the ones to quote**, and they are the ones in the two tables above; the single-unit ones
are a lower bound on the uncertainty. With 28 clusters they are rough themselves. The conclusion survives them: the odds ratio's lower
bound stays above 1 in both kinds of unit. In every resample the flags are those of the full sample.

Is the agreement only that both measures are high in the same districts? No. The odds ratio **within districts**
(Mantel–Haenszel, pooled over the districts) is 2.33 for all units, 2.89 in the LGD panchayat units and 2.10 in the
outside-village units, against 2.67 overall: the agreement holds unit by unit inside a district.

**What this shows.**

1. **The two measures agree more than chance, and far from fully.** 255 units are in the top fifth on both, against
   148 expected of unrelated flags: 1.72 times as many, odds ratio 2.67 (1.70–4.37). But 487 units are flagged by
   Hansen alone and 487 by CoRE Stack alone: of the units either measure puts in its worst fifth, 34 per cent are in
   the other's. Where both flag a unit the claim that it degraded is as strong as these two sources can make it. Where
   one does, the table says which, and neither is preferred.
2. **The placebo holds in one of CoRE Stack's two zone models and not in the other.** Pooled, a unit's Hansen rate rises
   with its CoRE Stack degradation rate (Spearman 0.36 (0.22–0.47)) and not with its improvement rate (0.03 (−0.12 to 0.14)),
   and units in Hansen's worst fifth are *less* often in the top fifth for improvement than chance would give (105
   against 148). But the pooled figure mixes two models that differ (§4a). Split by the model covering a unit's land:

   | units whose valued land is under | assessed | flagged by Hansen, % | both, class −1 | expected | odds ratio | Spearman with class −1 | **with class 1, the placebo** | units reaching the pooled class 1 cut | of them flagged by Hansen | expected | median class 1 rate, % |
   |---|---|---|---|---|---|---|---|---|---|---|---|
   | Eastern Plateau and Hills model only | 2,921 | 18.4 | 160 | 99.3 | 2.24 | 0.33 (0.30–0.37) | 0.06 (0.03–0.10) | 698 | 98 | 128.6 | 15.7 |
   | East Coast Plains and Hills model only | 630 | 25.7 | 80 | 36.5 | 6.39 | 0.53 (0.47–0.58) | 0.29 (0.22–0.37) | 13 | 4 | 3.3 | 4.2 |
   | both models | 160 | 26.2 | 15 | 16.0 | 0.87 | 0.05 (−0.14 to 0.21) | 0.02 (−0.13 to 0.17) | 31 | 3 | 8.1 | 11.2 |

   (Intervals here resample units singly.) In the Eastern Plateau and Hills model, which holds 79 per cent of the
   assessed units, the placebo is clean: 0.06 against 0.33 for degradation. **In the East Coast Plains and Hills model it is
   not: there the Hansen rate goes with improvement at 0.29** — less than with degradation (0.53), but far from
   nothing — which is what one would see if the classifier there were busy wherever the forest is changing at all.
   The flag cannot test it there: only 13 of its 630 units reach the pooled improvement cut. And in the 160 units
   that straddle the two models there is no agreement to speak of (odds ratio 0.87; Spearman 0.05, interval
   −0.14 to 0.21). The agreement on class −1 itself holds inside each model taken alone (odds ratios 2.24 and 6.39).
3. **It holds in both kinds of unit** — observed over expected 1.81 (1.24–2.76) in the LGD panchayat units and
   1.51 (1.29–2.05) in the outside-village units. The difference between the two is well inside the intervals.
4. **The class that should match Hansen best matches it worst.** Class −2, "tree cover lost", is the class the producers
   validated and the one that names what Hansen measures; its rank correlation with the Hansen rate is 0.18 over all
   assessed units (0.32 in the outside-village units, 0.15 in the LGD panchayat ones), below that of class −1. On land with
   canopy above 10 per cent in 2000 class −2 is small (0.61 per cent of valued land marks a unit's top fifth), and most of
   the product's class −2 lies on land with no canopy in 2000 (§4a). The two products do not see clearance the same way.
5. **Where the area is.** Units CoRE Stack flags hold 56 per cent of all Hansen loss 2017–2023 on the reference land, and
   45 per cent of the land; units Hansen flags hold 29 per cent of all class −1 area, and 29 per cent of the land. **By
   area, then, the agreement runs one way:** the units CoRE Stack marks hold more than their share of Hansen's loss,
   but the units Hansen marks hold no more than their share of class −1. Clearance is concentrated where thinning is common;
   thinning is not concentrated where clearance is. The
   two also differ by more than an order of magnitude in what they count: 799 km² of Hansen loss in the window against
   9,046 km² of class −1 in the same units.

**The other windows, reported separately** (all units, 50 ha floor). The full-span row sets Hansen's loss in any year
2001–2025 beside a product that starts in 2017; it is not one period and is not a test of agreement. In this table and
the two after it the intervals resample units singly — district intervals were made for the headline only — so read
them as too narrow by the factor above.

| Hansen loss dated | Hansen top-fifth cut, % of reference land | Hansen loss in the window, km² | both | expected | observed / expected | odds ratio | Spearman with class −1 | with class 1 |
|---|---|---|---|---|---|---|---|---|
| **2017–2023 (headline)** | 2.27 | 798.7 | 255 | 148.4 | 1.72 (1.57–1.87) | 2.67 (2.20–3.19) | 0.36 | +0.03 |
| 2019–2022 only (sensitivity) | 0.85 | 380.2 | 251 | 148.4 | 1.69 (1.55–1.84) | 2.58 (2.16–3.11) | 0.37 | +0.02 |
| 2001–2025, Hansen's full span (not one period) | 6.50 | 1,902.0 | 236 | 148.4 | 1.59 (1.45–1.74) | 2.27 (1.89–2.73) | 0.30 | +0.02 |

CoRE Stack's "2017" is the mode of the agricultural years 2016-17 to 2018-19 and its "2023" that of 2022-23 to 2024-25,
so a loss dated 2017 or 2018 falls inside its first period and one dated 2023 inside its second. Keeping only the
years strictly between the two periods (2019–2022) changes little.

**The minimum forest** (headline window, all units). A unit's rate on a few hectares is noise (§4c). 50 ha is the
floor *proposed* for stage 4, which the project owner has not ruled on; it is used here because a floor is needed.
The finding does not depend on where it is set:

| at least | assessed units | both | expected | observed / expected | odds ratio | Spearman with class −1 |
|---|---|---|---|---|---|---|
| 10 ha | 5,693 | 437 | 227.9 | 1.92 (1.80–2.04) | 3.42 (2.96–3.94) | 0.40 |
| 50 ha (delivered) | 3,711 | 255 | 148.4 | 1.72 (1.57–1.87) | 2.67 (2.20–3.19) | 0.36 |
| 100 ha | 2,891 | 184 | 115.6 | 1.59 (1.43–1.76) | 2.27 (1.86–2.79) | 0.33 |

The evidence for 50 ha in §4c was measured on the `treecover2000` > 30 mask, which is not this table's land. The same
test on the reference land used here — the rank correlation of a unit's Hansen loss rate between odd and even years,
by how much of that land the unit has (`agreement_floor_repeatability.csv`):

| reference land in the unit | units | odd against even years, 2001–2025 | within 2017–2023 | the same class of forest on the > 30 mask (§4c) |
|---|---|---|---|---|
| 10 to 25 ha | 1,199 | 0.60 | 0.60 | 0.72 |
| 25 to 50 ha | 874 | 0.70 | 0.65 | 0.77 |
| 50 to 100 ha | 839 | 0.73 | 0.73 | 0.81 |
| 100 to 250 ha | 988 | 0.84 | 0.80 | 0.89 |
| 250 to 500 ha | 622 | 0.91 | 0.83 | 0.91 |
| 500 to 1,000 ha | 542 | 0.93 | 0.87 | 0.94 |

On this land the mark of 0.8 that §4c uses is reached from 100 ha, not from 50: at 50 to 100 ha a unit's rate is repeatable
at 0.73. So the 50 ha floor is weaker here than its own justification says. The 100 ha row above is the
stricter reading: 2,891 units assessed, 184 flagged by both against 116 expected. Which floor stage 4 uses is the owner's
to rule.

**Other readings of "CoRE Stack says degraded"** (headline window, all units, 50 ha floor; `agreement_definitions.csv`).

| CoRE Stack flag on | top-fifth cut, % of valued land | both | expected | observed / expected | odds ratio |
|---|---|---|---|---|---|
| class -1 (delivered) | 23.99 | 255 | 148.4 | 1.72 | 2.67 (2.20–3.19) |
| classes -1, 3 and 4 | 25.82 | 251 | 148.4 | 1.69 | 2.58 (2.14–3.09) |
| class -1 minus class 1 | 10.80 | 234 | 148.4 | 1.58 | 2.23 (1.86–2.68) |
| class -2, tree cover lost | 0.61 | 217 | 148.4 | 1.46 | 1.92 (1.58–2.31) |
| class 1, improvement (the placebo) | 24.29 | 105 | 148.4 | 0.71 | 0.60 (0.48–0.75) |

**What this table is not.**

- **It is not a pixel-by-pixel overlap.** That needs one more Earth Engine job, which was not run: the project's queue
  runs one task at a time in the order submitted (§10), and the job would have waited behind the NIRv exports for
  about two days. A random sample of 12,813 points taken on 5 October gives the direction (a sample, not a table):
  on land with `treecover2000` > 10, of 64 valued points with Hansen loss dated 2017–2023, 18 are CoRE Stack class −1
  (28 per cent) and 0 are class −2; of 2,914 valued points with no Hansen loss in any year, 668 are class −1
  (23 per cent) and 8 are class −2.
- **The flag is relative** to the assessed units of this layer; a different set of units would move the cuts.
- **It is not a clean test in the East Coast Plains and Hills model**, where the placebo fails (point 2).
- **A class −1 rate carries the zone it lies in.** The two agro-climatic zone models differ (§4a: the downward share is
  0.75 in one and 0.54 in the other), so part of what CoRE Stack "flags" follows the zone boundary.
- **The two rates stand on two grids**, Hansen's 30 m and CoRE Stack's 25 m; over all units the reference land differs
  by +0.0037 per cent between them.

### 4c. A minimum forest area for stage 4 (task E) — a recommendation, not ruled on

**Where the proposed floor is used since 7 October 2026.** When this section was written the 50 ha floor was applied to
no table. It is now the floor of the agreement table (§4b), applied there to land with `treecover2000` > 10 — a
different land from the one it was measured on, and weaker on it (§4b, *The minimum forest*) — and the default setting
of the demo layer (`docs/LAYER.md`), which offers 1 ha beside it. No stage-1 column is masked by it, and it is still a
recommendation: the project owner has not ruled.

Stage 1 covers all 11,468 units whatever this section says. `scripts/02_propose_forest_floor.py` writes
`forest_floor_options.csv` and `forest_floor_repeatability.csv` (run 2026-10-05T21:46:29Z).

**The rule used to choose.** A unit's loss rate — `hansen_loss_ha / forest_ha` — is worth entering in a model only if
it is a property of the unit and not of chance. That can be measured from the data alone: compute each unit's rate
from the odd years and from the even years, and see how alike the two halves rank the units, by class of forest area.

| `forest_ha` | units | LGD panchayat | outside-village | with no loss at all | odd years against even years, rank correlation |
|---|---|---|---|---|---|
| 0 – 0.5 | 1,564 | 1,233 | 331 | 1,398 | 0.23 |
| 0.5 – 1 | 391 | 299 | 92 | 306 | 0.31 |
| 1 – 2 | 382 | 281 | 101 | 277 | 0.34 |
| 2 – 5 | 528 | 374 | 154 | 335 | 0.53 |
| 5 – 10 | 438 | 281 | 157 | 237 | 0.61 |
| 10 – 25 | 657 | 385 | 272 | 317 | 0.72 |
| 25 – 50 | 563 | 347 | 216 | 200 | 0.77 |
| 50 – 100 | 568 | 343 | 225 | 120 | 0.81 |
| 100 – 250 | 696 | 437 | 259 | 105 | 0.89 |
| 250 – 500 | 460 | 328 | 132 | 28 | 0.91 |
| 500 – 1000 | 401 | 303 | 98 | 5 | 0.94 |
| 1000 –  | 510 | 276 | 234 | 0 | 0.96 |

Below 10 ha the two halves barely agree; the rate is noise. **The proposal is 50 ha**: the bottom of the smallest
class from which every class reaches 0.8, a conventional mark for a measure being reliable enough to use (the mark
is a convention, and the table lets another be read off).

| floor on `forest_ha` | units kept | LGD panchayat | outside-village | forest kept, % | loss kept, % | odd against even among those kept | units kept if the floor were on `treecover2000` > 10 | pass on > 10 but fail on the mask (of them LGD) |
|---|---|---|---|---|---|---|---|---|
| 1 ha | 5,203 | 3,355 | 1,848 | 99.98 | 99.97 | 0.75 | 8,870 | 3,667 (3,080) |
| 10 ha (alternative) | 3,855 | 2,419 | 1,436 | 99.77 | 99.77 | 0.84 | 5,824 | 1,969 (1,599) |
| **50 ha** (proposed) | 2,635 | 1,687 | 948 | 98.60 | 98.81 | 0.89 | 3,751 | 1,116 (854) |
| 100 ha (alternative) | 2,067 | 1,344 | 723 | 97.03 | 97.49 | 0.92 | 2,912 | 845 (653) |
| 500 ha | 911 | 579 | 332 | 86.52 | 88.83 | 0.95 | 1,302 | 391 (303) |

- At 50 ha, 2,635 of 11,468 units remain (1,687 LGD panchayat, 948 outside-village) and they hold 98.6 per cent of the
  forest and 98.8 per cent of the loss. Three quarters of the units drop out and take about one per cent of the
  forest with them.
- **The floor selects.** 1,116 units have at least 50 ha of land with canopy above 10 per cent but less than
  that above 30 — by construction the units whose tree cover is open — and 854 of them are LGD panchayat units. If
  the measure that enters stage 4 is one defined on canopy above 10 per cent, the floor belongs on that land instead.
- A floor is needed for a *rate*. A model of hectares lost, weighted by forest area, needs none.

## 5. NIRv from Landsat 8: a negative methodological result (task B)

**The finding.** A Theil–Sen NIRv trend over dry-deciduous forest is dominated by the phenology of the acquisition
dates, and correcting for it makes the trend a function of the correction. The measure was specified, built, and
reproduced bit for bit by an independent replication; the replication then showed what the yearly value was made of;
the value was redesigned to remove the date; and a second replication round measured how far the redesigned trend can
be trusted. It cannot carry the weight of a degradation measure. Others who fit a trend to seasonal Landsat composites
over deciduous forest should expect the same.

**What follows (ruling of 7 October 2026).** NIRv is not a measure of degradation in this project and nothing in
stage 1 waits for it. It is a *reported column* of `degradation_by_unit.csv`: `nirv_slope` and `nirv_declining_ha` from
the date-standardised value, with the first design's beside them as `_unadjusted`, and the caveats of §5.4 attached.
**State: pending, and **nothing is queued** — 72 of 84 tiles of stored observations exist (2026-10-07T08:36:08Z); the other 12 and the 13 blocks of yearly values were cancelled from outside this pipeline on 7 October, with every other pending task of the project, and the chain stopped (§6, §10). Queueing them again is the project owner's decision; the columns of `degradation_by_unit.csv` stay blank until then.** `nirv_by_unit.csv` does not exist yet; nothing below is a state-wide figure.

### 5.1 The design

NIRv is the near-infrared reflectance of vegetation, NDVI × NIR (Badgley, Field and Berry 2017): the part of a pixel's
near-infrared reflectance that comes from vegetation. It tracks canopy structure, and a multi-year decline in it was
to be the measure of thinning that Hansen cannot see.

As specified and first built: Landsat 8 alone, the thirteen seasons 2013–2025; for each pixel and season, the median
NIRv of the clear scenes of 1 November – 31 December, after the monsoon and before leaf fall; the Theil–Sen slope of
those thirteen values on the year; and a pixel called *declining* when an exact Mann–Kendall test rejects no-trend at
two-sided 5 per cent. The reasons for each choice are under *The four decisions* below.

An independent replication, written from the scripts' docstrings alone and reading the same scenes from a different
archive, reproduced it: in 2,467,997 of 2,600,000 pixel-seasons the stored value is identical to the last bit of a
32-bit float (the other 132,003 lie under 34 scenes its archive could not serve), and per-unit areas agree to a few
parts in 100,000. **The design was implemented correctly. That is what makes the next finding about the design and
not about the code.**

### 5.2 The calendar problem

The replication then asked what a season's median is a median *of*.

- Inside the window a forest pixel's NIRv falls by **13 to 18 per cent of its mean per 30 days** on land with
  `treecover2000` > 10 (28 to 31 per cent on `treecover2000` ≤ 10): leaves age and dry, and the sun gets lower.
- The mean day of the clear observations **moves by two to three and a half weeks** from one season to the next,
  because cloud decides which scenes are kept.
- So the yearly value follows the calendar: over nine seasons of the replication's test blocks its **correlation
  with the mean day of the clear scenes is −0.90**; unit by unit over 97 units the median is −0.80.
- Three missing scene-dates moved a 97-unit total of declining area by 3 to 35 per cent.

A trend fitted to such medians is in part a trend in scene dates, and the median cannot be put right afterwards,
because it has thrown the dates away. Moving every observation to one date with one rate — as a sensitivity test —
took the declining share of the test blocks from 13.5 to about 6 per cent and the increasing share from 0.8 to about
5. A fixed window is not a fixed point in the season.

### 5.3 The redesign

Every clear pass is now stored with its date (`02_export_nirv_observations.py`). For each pixel, NIRv is modelled
within seasons as a level plus a rate × (day − 30) plus a step for the odd Landsat path, fitted over all the pixel's
passes of all thirteen seasons; each pass is moved to 1 December by the pixel's own rate; and the yearly value is the
median of the season's moved passes (`02_export_nirv_yearly.py`, computed once per grid cell and stored). The trend
and the test are as before.

It does what it was built to do. Given the pipeline's own stored passes, the replicator's code reproduces all 255,748
date-standardised values to within 2 × 10⁻¹⁶. The correlation between a unit's series and the mean day it was seen on
goes from −0.79 to +0.19 (south-west, 61 units) and from −0.71 to +0.04 (state-wide, 21 units); the year-to-year
scatter falls by 41 and 32 per cent; and on no-trend values placed on the real passes, dates and paths the test flags
2.1 to 2.5 per cent each way against a nominal 2.1 — the standardisation does not manufacture a trend.

**The first design's value is kept beside it**, as `raw_` in the detailed tables and `_unadjusted` in the delivered
ones (`nirv_slope_unadjusted`, `nirv_declining_ha_unadjusted`, `nirv_increasing_ha_unadjusted`), so that any reader can
see what the correction changes. It is known to follow the calendar and is there for comparison only.

### 5.4 Three measurements of instability

Measured by the replication's second round on its own 177 units — 97 in the south-west and 80 drawn across the state —
with its own scenes (`.session_scratch_2026-10-05/replicate_nirv/REPORT_round2.md`).

| | what was measured | result |
|---|---|---|
| 1 | **The trend moves with the fitted phenology rate.** Every pixel's rate multiplied by 0.9, 1.0, 1.1 before its passes are moved | the declining share is **6.3, 5.8, 5.3 per cent** (south-west): a tenth more or less rate, about a tenth less or more decline. And the rate is not known that well: a season's own rate differs from the pooled one by a fifth to two fifths |
| 2 | **A single pass decides the flag.** One pass, drawn at random, taken away from every pixel and everything fitted again | **20 to 24 per cent of the declining flags turn over** (32 per cent for a plain median of passes). One hazy scene of 5 November 2023 pulls that season down by 18 per cent where it is the early pass |
| 3 | **The declining share is not beyond chance.** The thirteen seasons put in random order, the same order for every pixel, and the test run again | re-ordered seasons reach the observed declining share in **7 per cent of orderings in the south-west and 22 per cent state-wide**. (The *increasing* share state-wide is beyond chance: 1.6 per cent of orderings) |

Also measured: across regions the trend still goes with the drift of the scene dates (rank correlation −0.38 over 243
blocks state-wide, down from −0.66 for the first design); and on those units the shares themselves — south-west, 5.8
per cent declining and 4.4 increasing (first design 8.7 and 0.7); state-wide sample, 3.3 declining and 10.0 increasing
(first design 5.0 and 5.7).

**How to read the three.** The third could be a matter of power: 177 units is a small sample, and the state-wide run
will have every unit. The first two are not. They are properties of the measure, not of the sample: where scene dates
have drifted over the years the correction is itself trended, so the trend is proportional to a nuisance parameter
that cannot be pinned down to better than a fifth; and a flag that a single observation can reverse is not a
measurement of the canopy. More units will not change either. A measure whose output moves one for one with a nuisance
parameter cannot be defended, whatever the state-wide run returns — which is why the ruling was made before it
returned.

**What the state-wide run will add** when its queue ends (§10): the same three measurements on every unit
(`nirv_rate_sensitivity.csv`, `nirv_null.csv`, `nirv_date_check.csv`). They will give n. They cannot repair 1 and 2.

### 5.5 What is delivered

- In `degradation_by_unit.csv`: `nirv_status` (pending until the run ends), `nirv_slope`, `nirv_declining_ha`,
  `nirv_increasing_ha`, `nirv_trend_ha` from the date-standardised value; the three `_unadjusted` columns from the
  first design; `missing_data_share_nirv`. Never read the declining area without the increasing one.
- Not delivered: NIRv in the agreement table (§4b), or as an input to stage 4.
- The negative result is the deliverable: a seasonal-composite greenness trend over this kind of forest needs its
  acquisition dates controlled, and once they are, it needs the sensitivity to the control reported beside it.

### 5.6 The record

#### The calendar problem and the redesign, in full

**The first design measured the calendar.** It stored, for each pixel and season, the median NIRv of the clear
scenes of 1 November – 31 December, and fitted the trend to those thirteen values. An independent replication
(§9) reproduced the stored values bit for bit — and then showed what they are made of. Inside the window a forest
pixel's NIRv falls by 13 to 18 per cent a month: leaves age and dry, and the sun gets lower. And the dates of the
clear scenes move by two to three and a half weeks from one season to the next. So a season's median is as much a
measure of *when* the clear scenes fell as of the canopy: over nine seasons of the replication's five test blocks its
correlation with the mean day of the clear scenes is −0.90. One box of 40,000 cells, looked at directly, shows the
fall: its forest pixels' mean NIRv in the 2019 season was 0.224 on 10 November, 0.202 on 26 November, 0.184 on 12 December, 0.170 on 28 December
(`.session_scratch_2026-10-05/phase2/date_effect_box.csv`). A trend fitted to such medians can be a trend in dates, and
the median cannot be put right afterwards, because it has thrown the dates away.

**What was done.** The export of yearly medians was stopped at 5 of 84 tiles. Instead:

1. **Every clear observation is stored with its date** (`scripts/02_export_nirv_observations.py`): one band per season,
   per 16-day slot of the window and per parity of the Landsat path — 104 bands, each of which is one pass of one
   path, whose date is known from the scene list. The scene list itself is written to `nirv_scenes.csv`, because the
   figures depend on it. The first design's median and count are stored beside them, made exactly as before.
2. **There are two yearly values, and every table carries both:**
   - *first design* (`raw_`): the median of the season's scenes, as before;
   - ***date-standardised* (`std_`), the one the delivered columns use**: for each pixel, NIRv is modelled within
     seasons as a level plus a rate *g* × (day − 30) plus a step *h* for the odd path, fitted by least squares over
     all the pixel's passes of all thirteen seasons; each pass is moved to day 30 (1 December) by *g* and to the
     pixel's usual mix of paths by *h*; the yearly value is the median of the season's moved passes. A pixel gets a
     rate only if its passes span enough dates (Sdd ≥ 1,000 day²), and a path step only if it is seen from two paths
     often enough (Sqq ≥ 4). The exact arithmetic is in the docstring of `scripts/02_export_nirv_yearly.py`.
3. **The date-standardised value is computed once per grid cell and stored** (`scripts/02_export_nirv_yearly.py`:
   13 blocks, with each cell's rate, path step, passes and mean day beside the thirteen yearly values), and the
   per-unit script (`scripts/02_build_nirv.py`) reads stored bands. This step exists because of what the first
   batch test of the rewritten script cost: with the standardisation computed on the fly inside the per-unit sums,
   Earth Engine recomputed it for every output band — **one group of 1,432 units used 380,962 EECU-seconds (106
   EECU-hours) in ten minutes and was cancelled by hand; it had not finished.** The same arithmetic exported once
   as an image cost 722 EECU-seconds for a pilot block of 1.84 million cells (§10).
4. **What is stored is checked at every run, before anything is summed**: at 4,000 random pixels the per-unit
   script reads every stored pass and every stored yearly band, redoes the whole standardisation in numpy, and stops
   unless the stored values, rates, passes and mean days agree; at 400 of them Earth Engine's slopes, S, n and
   contrasts must equal numpy's.
5. **Whether the standardisation worked is measured, not assumed**: `nirv_date_check.csv` gives, for both values,
   the correlation of a unit's series with the mean day its land was seen on, and the year-to-year scatter;
   `nirv_rate_sensitivity.csv` how much the result hangs on the rate and on any single pass.

**What the standardisation does on test areas.** Five boxes of 40 × 40 cells in the first tiles (per-scene values read
for each; land with `treecover2000` > 10; `phase2/fit_date_model.py`). "Before" is the first design, "after" the
date-standardised value.

| box | pixels | passes per season | rate, % of level per 30 days | correlation with mean day: before | after | year-to-year scatter, %: before | after | declining, %: before | after | increasing, %: before | after | median slope, % a year: before | after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 81.32 E, 17.87 N | 1,551 | 2.7 | -14 | -0.69 | -0.18 | 10.3 | 7.3 | 0.6 | 0.5 | 0.0 | 5.1 | -0.37 | +0.28 |
| 81.42 E, 18.27 N | 1,396 | 2.7 | -13 | -0.78 | -0.45 | 6.1 | 4.1 | 21.1 | 5.0 | 0.3 | 2.1 | -0.95 | -0.17 |
| 81.62 E, 18.22 N | 85 | 2.8 | -21 | -0.72 | +0.12 | 9.8 | 6.2 | 11.8 | 1.2 | 0.0 | 0.0 | -1.46 | +0.02 |
| 81.96 E, 18.12 N | 574 | 2.3 | -21 | -0.86 | -0.04 | 9.4 | 8.6 | 33.6 | 6.6 | 0.7 | 6.4 | -1.50 | -0.31 |
| 82.22 E, 17.87 N | 1,564 | 5.4 | -12 | -0.72 | +0.05 | 6.5 | 4.7 | 6.5 | 1.8 | 1.3 | 15.4 | -0.29 | +0.26 |

In the one box seen from two paths the odd path reads 7.8 per cent of the level above the even one at the same date. A
quadratic rate, a proportional rate and one rate pooled over a box did no better than a straight line per pixel
(`phase2/fit_date_model_variants.py`). **These boxes are in and just outside the state's south-western corner
(Malkangiri) and are tests, not results** — but they show the size of the thing: in four of five, most of what the first design called decline was
dates.

**What the standardisation does not do, and what it costs** (measured by the replication's second round, §9, on its
own 177 units; the state-wide run will measure the same in `nirv_rate_sensitivity.csv` and `nirv_date_check.csv`):

- It uses one straight-line rate per pixel for all thirteen seasons. A season's own rate differs from the pooled
  one by up to a fifth to two fifths, so a year whose leaf fall came early or late is not put right; and a pixel
  cleared inside a season bends its own rate.
- **The trend depends on the rate at first order** wherever the scenes' dates have drifted over the years: a tenth
  more or less rate moves the declining share by about a tenth.
- **A single pass still decides a great deal.** Taking one pass at random from every cell turns over a fifth to a
  quarter of the declining flags, and a pass far from 1 December is moved a long way, its own error with it.
- Across regions the trend still goes with the drift of the dates (rank correlation −0.38 over blocks state-wide,
  down from −0.66): either those regions really declined more or the correction falls short there.
- It does not manufacture a trend: on no-trend values placed on the real passes, dates and paths the test flags
  2.1 to 2.5 per cent each way against a nominal 2.1, including through the rate being fitted on the passes it moves.

#### The four decisions

**1. Sensor and years: Landsat 8 alone, the thirteen seasons 2013–2025.** One instrument and one orbit, so that
nothing in the series changes but the ground. That is how the Landsat 7 scan-line gap and the 2013 change of sensor
are handled: by not crossing them.

- Landsat 7's scan-line corrector failed on 31 May 2003 and about 22 per cent of every scene has been missing
  since; its orbit drifted from 2017 and was lowered in 2022; its surface reflectance comes from a different
  algorithm (LEDAPS) from Landsat 8's (LaSRC); and its near-infrared band is much wider — Landsat 8's lies wholly
  inside it and covers under a quarter of it. NIRv is proportional to NIR, the band in which the two differ most.
  The published coefficients for bringing them together (Roy et al. 2016) were fitted to pre-Collection data over
  the United States. A series that crosses 2013 carries a step exactly where a trend test would see it.
- Landsat 5 has whole months missing over Odisha in many years (no October–December scene in 2002 or 2012; measured
  from the scene list).
- Landsat 9 is left out so that sampling does not step up in 2021. It would roughly double the observations of
  the last five seasons and leave the first eight as they are.
- The cost: nothing before 2013 is seen. The span does match the R6.20 allocation panel (FY2014-15 on).

**2. Window: 1 November to 31 December, every pass standardised to 1 December**, a season being named for the
year of its November. A fixed window is not by itself a fixed point in the season — that was the first design's
mistake — which is why the date is standardised.

- It starts after the monsoon has withdrawn (India Meteorological Department normal for Cuttack and Puri: 12
  October) and after October, which is the cyclone month on this coast and about twice as cloudy as December
  (Bhubaneswar: 3.7 / 4.8 oktas in October against 1.6 / 2.1 in December; state rainfall 112 mm against 7 mm).
- It ends before leaf fall: at Similipal most species begin shedding in January, and in sal forest in Sundargarh
  greenness peaks in mid-October and falls sharply from the start of the year.
- It lies inside the season the Forest Survey of India uses, for the reason it gives ("cloud-free data and full
  vegetation foliage").
- Measured: one sensor gives at least one clear observation in 99.5 per cent of pixel-seasons in this
  window, all thirteen seasons at 93.8 per cent of points and at least ten at 100 per cent (n = 4,000 points).
- Measured against the alternative: running the window to 31 January lowers the year-to-year noise of the yearly
  value only from 7.4 to 7.0 per cent of the median (land with `treecover2000` > 10), at the price of January's leaf fall
  and about four times the compute. The window was kept.

**3. What counts as declining: a significance test, no slope threshold.** A pixel is *declining* if its
Mann–Kendall statistic S is at or below minus the exact critical value of a two-sided 5 per cent test for the
number of seasons that pixel has (34 of a possible 78 at thirteen seasons). This is the threshold the UN Convention
to Combat Desertification's good-practice guidance uses for its degrading-trend class — and the same guidance says
a declining trend alone is not sufficient to call land degraded. The tables carry *increasing* (the mirror image)
and *any negative slope* beside it, never instead of it. No magnitude threshold is used because none has a precedent
that fits; the slope as a share of the land's mean NIRv is reported so that size can be read. The test's own
distribution is computed by counting and checked against the table the US Environmental Protection Agency prints;
no normal approximation is used.

**4. The trend: the Theil–Sen slope** (`ee.Reducer.sensSlope`) of the yearly value on the year, for pixels with at
least ten of their thirteen seasons.

**A kept observation.** For each Landsat 8 scene in the window: red = `SR_B4` × 0.0000275 − 0.2, NIR = `SR_B5` ×
0.0000275 − 0.2; a pixel is kept only if `QA_PIXEL` bits 0–5 are all zero (fill, dilated cloud, cirrus, cloud, cloud
shadow, snow), `QA_RADSAT` bits 3, 4 and 11 are zero (red saturated, NIR saturated, terrain occlusion), and both
reflectances lie strictly between 0 and 1. A season is every scene acquired from 1 November 00:00 UTC up to, not
including, 1 January. Each scene's NIRv is a 32-bit float. Everything is on Hansen's grid, each cell taking the
Landsat pixel that contains its centre. Where two rows of a path overlap, one pass gives two scenes of the same
instant; the stored pass is their mean (the first design's count is of scenes, so it counts both). The script that
makes the yearly values refuses to run if the code that decides what a stored band holds has changed since the
tiles were exported, or if the scene list is not the one the export recorded; the per-unit script refuses in the
same way for both stored layers.

**Beyond the two columns the brief names**, the script also computes, for both yearly values and all from the same
stored observations:

- **A before-and-after contrast**, for setting NIRv beside CoRE Stack, which compares two three-year periods: a
  pixel is *lower* if every one of the seasons 2022, 2023 and 2024 is below every one of 2016, 2017 and 2018, and
  *higher* in the mirror case. Six values in random order do either once in twenty. A trend test over the seven
  seasons 2017–2023 is carried beside it and is not the measure: a clean, permanent step in the middle of seven
  seasons gives S = −12, short of the critical 15, so it cannot see an outright clearance.
- **Season by season**, for each unit, the mean NIRv of its land with `treecover2000` > 10 — the variable a
  district-year panel would use — and of three classes of that land separately: 10 < `treecover2000` ≤ 30;
  *reference forest* (`treecover2000` > 50 and no Hansen loss in any year); and the rest of `treecover2000` > 30.
  Beside it, the mean day on which that land was seen that season.
- **The trend of each unit's own series**, as measured and *relative to reference forest* (the series divided,
  season by season, by the mean of all reference forest in the layer, so that a wet year, a late monsoon or a
  drift in the sensor cancels).
- **The false-alarm rate, measured**: the thirteen seasons are put in a random order, the same for every pixel or
  unit, 2,000 times, and the test is run again. What re-ordered seasons flag is what chance flags.

**What has been checked before the state-wide run** (`.session_scratch_2026-10-05/phase2/tests/`, all re-runnable):

- *The stored tiles.* On a box of 400 cells seen from two paths, all 132 bands of the tile image as Earth Engine
  computes them from Landsat equal the same bands rebuilt in numpy from the per-scene pixel values of that box, cell
  by cell, with no difference at all; and the first design's bands in the new tiles equal the old asset's values —
  the ones the replication confirmed — exactly.
- *The standardisation.* The numpy implementation equals a separate pandas one on five boxes (to 10⁻¹⁶).
- *The stored yearly values.* On a box of 4,096 cells of the pilot block — written by the real export task — the
  stored standardised values equal the standardisation redone in numpy from the stored passes exactly (to the last
  bit of the 32-bit float), the rates to 6 × 10⁻⁸ of themselves; storing 32-bit values changes the test statistic S
  at none of the cells.
- *The per-unit sums.* Every band of both per-unit images — 154 for the first design, 134 for the date-standardised
  value — summed by Earth Engine over that box, equals the same sum rebuilt in numpy from the stored bands (largest
  relative gap 1 × 10⁻⁸); the agreement script's 151 bands likewise, with no difference at all.
- *The path step, and cells with too little.* On a box in which every cell is seen from two paths the same holds
  for all three images. On the same box with seasons deliberately taken away column by column — cells with no
  season, one, two, … thirteen, 60 of them without a rate — the gate still passes and every band still matches:
  a cell without a rate has no yearly value, no slope and no flag, on both sides.
- *The whole script.* Last, the whole script was run on 7 small units inside the pilot block of stored yearly values (run 2026-10-06T19:37:57Z; the sums and the point reads by small interactive requests instead of batch tasks): every gate passed. At 120 sampled pixels the stored standardised values, rates, passes and mean days equal the ones recomputed from the stored passes (largest gaps 0e+00 in the value, 5e-08 of itself in the rate), and at 40 of them Earth Engine's slopes, S, n and contrasts equal numpy's (largest slope gap 2e-10; S, n and flags identical). On those units the correlation of a unit's series with the mean day it was seen on goes from -0.60 (first design) to +0.20, its year-to-year scatter from 6.0 to 3.9 per cent, and the declining share of their 26 km² of land with `treecover2000` > 10 from 4 to 2 per cent. That is test output on a few square kilometres, not a result.
- *Not yet run when this was written:* the two per-unit scripts' own batch path (the point reads and the group
  tables as real batch tasks). The chain (`scripts/run_nirv_chain.py`) is its first run; the gate comes before the
  sums, and the driver bounds what a task may cost.

#### What a sample of the first design showed — superseded, do not quote

**Everything in this subsection was computed with the first design's yearly value**, on a random sample of 4,000 points
inside the units (919 on land with `treecover2000` > 10), before the replication reported
(`.session_scratch_2026-10-05/phase2/window_noise_points.csv`). It is kept because the interim report of 6 October quoted
it. Read with what is now known, points 2, 3 and 4 are what a date effect looks like — a "greening" that appears
in December's scenes and not November's, flags that do not repeat between the two months, year effects shared
across the state — and the rest cannot be relied on until it is redone with the date-standardised value.

Flags on the full thirteen seasons, 1 November – 31 December. Under no change, the exact chance of a flag is
2.11 per cent each way.

| | points with a trend | declining | increasing |
|---|---|---|---|
| `treecover2000` > 10, all units | 919 | 31 (3.4 %) | 89 (9.7 %) |
|   outside-village units | 490 | 12 (2.4 %) | 51 (10.4 %) |
|   LGD panchayat units | 429 | 19 (4.4 %) | 38 (8.9 %) |
| `treecover2000` > 30, all units | 661 | 18 (2.7 %) | 60 (9.1 %) |
|   no Hansen loss in any year | 631 | 16 (2.5 %) | 58 (9.2 %) |
| `treecover2000` ≤ 10, outside-village units | 563 | 12 (2.1 %) | 61 (10.8 %) |
| `treecover2000` ≤ 10, LGD panchayat units | 2,518 | 59 (2.3 %) | 375 (14.9 %) |

1. **The area of significant decline is not distinguishable from chance; the greening is.** On land with canopy
   above 10 per cent, 3.4 per cent of points are declining and 9.7 per cent increasing. The 2.1 per cent floor assumes
   that pixels fail independently; they do not, because a wet or dry season moves the whole state. Re-ordering the
   thirteen seasons the same way at every point, 3,000 times, gives a declining share between 0.1 and 7.1 per
   cent in nine cases out of ten (median 1.3): 21 per cent of re-orderings show at least as much decline as was
   observed, and 1.9 per cent as much increase. Scaled to the 37,517 km² of such land, the declining area would
   be about 1,264 km² — the same order as Hansen's loss on it — and none of it could be told from a null.
2. **The background is greening.** The median slope on that land is +0.25 per cent of NIRv a year, and forest with no
   Hansen loss shows 9.2 per cent increasing against 2.5 declining. A fixed-zero test therefore under-flags decline:
   a stand has to fall against a rising background before it registers.
3. **A pixel's flag is not repeatable within the window.** Computed from November scenes alone and from December
   scenes alone, the slopes of the same 894 points correlate at 0.55 and agree in sign for 66 per cent; 56 are declining in
   November, 21 in December and only 11 in both. November alone shows no greening (median slope -0.08 per cent
   a year) and December alone shows it (+0.29): the trend depends on when in the window the clear dates fall.
4. **Year-to-year noise is about 7 per cent of the value**, with no serial correlation to speak of (lag-1
   -0.08) and 13 per cent of it shared state-wide (the 2019 and 2021 seasons run +7 and +6 per cent high,
   2025 -5). Seasons resting on a single scene (5 per cent of pixel-seasons) are noisier (11 against
   8 per cent with five or more) but not biased low (+1.8 per cent).
5. **The flag does respond to clearance, as far as so few points can say.** Of 18 sampled points with Hansen loss
   dated 2014–2024, 2 are declining and none increasing; of 14 cleared before the series began, 2 are increasing
   and none declining (regrowth). A thirteen-season monotonic test cannot do much better on a one-step loss: by
   exact arithmetic a clean, permanent step is flagged with probability 85 per cent if it falls in 2019–2020 and
   under 10 per cent in the first or last year.
6. **Measured against undisturbed forest instead of against zero, there is a net decline — in the villages.**
   Dividing every season by the mean of the 396 sampled points with canopy above 50 per cent and no Hansen loss
   removes whatever all of that forest shares. On the remaining land with canopy above 10 per cent, 9.9 per cent of
   points then decline and 6.3 increase, against a re-ordered-seasons range of 0.4 to 4.8 per cent: more decline
   than any of 3,000 re-orderings gave. In LGD panchayat units it is 10.5 per cent declining against 6.1 increasing
   (n = 429); in outside-village units 6.3 against 7.6 (n = 490). This is a reading from a few hundred points
   and one choice of reference; the reference forest's own pixels scatter both ways at about 6 to 8 per cent.

**What this means for the columns.** `nirv_slope` and `nirv_declining_ha` will be filled for every unit from the
date-standardised value, with the first design's beside them as `_unadjusted`, the increasing area, and the
measured false-alarm rate. By the ruling of 7 October 2026 they are reported columns, not a measure of degradation,
and no state-wide result can change that: the first two of the three measurements of instability above are
properties of the measure. Nothing so far shows that NIRv carries a signal of degradation in these forests.

## 6. Getting 11,468 polygons into and out of Earth Engine

**The limit.** Earth Engine refused a single request of 11.5 MB with "Request payload size exceeds the limit: 10485760 bytes."
The base layer is 94.6 MB as GeoJSON (2,447,144 vertices; the largest unit alone is 1.6 MB), and the project
has no Cloud Storage bucket to stage a file in. So it was sent in 18 parts, each a batch task exporting to
its own table asset with the encoded request held under 9,071,819 bytes; Earth Engine then merged the parts
into one asset and the parts were deleted. The asset is `projects/replicating-paper/assets/ictd/units`; its properties are
`unit_id`, `unit_level`, `outside_village`. It carries no area: the first upload did, a UTM figure that stage 0 has
since replaced (§8), so on 6 October 2026 the asset was re-exported server-side without it and checked again.

**Nothing was simplified or rounded by the pipeline. Earth Engine does not store a polygon exactly, though,
and that is measured.** Every unit's geometry was read back from the asset and set against the layer's:

| | |
|---|---|
| units read back | 11,468 of 11,468 |
| boundary moved, averaged along a unit's perimeter | median 1.80 mm, 99th percentile 2.23 mm, largest 2.9 mm (unit 136093) |
| area that changed hands, all units | 439,001 m² of 154,929 km² (2.8e-06) |
| **net change in area, all units** | **+98 m² (+6.3e-10)** |
| largest net change for one unit | 47.5 m²; relative to its own area, at most 3.9e-04 |
| vertices | 2,447,144 sent, 2,444,613 stored |

The run stops if any unit's boundary has moved by more than 50 mm on average or the net area by more than
1e-06. That is the area error of the copy Earth Engine holds.

Three things were learned the hard way, and all are now in the scripts:

- **Edges must be sent as geodesics.** The first upload declared them planar in lon/lat, which is how the
  GeoPackage reads them. Earth Engine re-tessellated every polygon on ingestion: four test units sent both ways
  came back with between 0.004 and 0.06 per cent of their area changed hands when sent planar, against 0.00007
  to 0.0014 per cent when sent geodesic (measured on 5 October 2026 on units 135476, 131199, OUTSIDE_998 and
  OUTSIDE_3185; the script does not repeat the planar test). A geodesic edge is not quite the straight lon/lat
  edge between the same two vertices: over all 2,427,049 edges the largest mid-edge gap is 23 cm, on the
  longest edge (5,575 m), and the area lying between the two readings, whichever side it falls, is
  143,710 m² (9.3e-07 of the total). The sums that come out behave as if the edges were straight
  (independent check); either way the difference is at most 0.094 ha for one unit.
- **Earth Engine's own `Geometry.area()` is not a check.** It is computed on a sphere and runs about 0.3 per
  cent above the WGS84 ellipsoid at these latitudes. `ee.Image.pixelArea()`, which the statistics use, is
  ellipsoidal — tested at every run.
- **Requests can hang.** An upload request stalled for half an hour on a dead connection after Earth Engine had
  in fact started its task; the client has no timeout of its own. Every request now has a ten-minute deadline,
  and a part is sent again only if Earth Engine has neither the part nor a task for it.

**Zonal statistics.** The units are split into 8 runs of consecutive ids, each one batch `reduceRegions` task on
the source's own grid; the result tables are read back page by page and deleted. Earth Engine will not export a
table row without a geometry ("Unable to export features with null geometry"), so each row carries a dummy point.
The Hansen run used 17,233 EECU-seconds.

**If a run is interrupted.** The batch tasks belong to Earth Engine, not to the script: they keep running if the
script or the machine dies, and each leaves its table in a folder beside the units asset (`…/units_hansen_parts`,
`…/units_corestack_change_parts`, and so on) until the script has read it. To resume, run the same command again.
The script reuses every group whose table is complete and starts only the missing ones, and it refuses to start
while a task of the same name is still pending or running, because a second task would write the same table. The
two NIRv exports resume the same way (`02_export_nirv_observations.py`, `02_export_nirv_yearly.py`: tiles and blocks
that exist are skipped). Nothing has to be remembered between sessions beyond the command.

**An intermediate table must never be mistaken for another run's.** The helper takes a group table as already
computed if it has the right number of rows and the right column names — nothing ties it to the image that made it.
A table left by an interrupted test did sit under a production name for an hour on 6 October (1,432 rows where the
state-wide group has 1,434; only the row count told them apart). So the NIRv and agreement scripts now put a
fingerprint into the names of their intermediate tables: ten hex digits of a hash over the image's whole expression,
the band list, the grouping, the layer's hash, the scene list's hash and both export recipes
(`…/units_nirvstd_parts_<fingerprint>`, `…/units_nirv_points_stored_<fingerprint>`, and so on). Change anything that
decides what a table holds and the name changes with it. The record says how many group tables were taken from an
earlier attempt of the same computation.

**The unattended chain.** In restricted mode (§10) the work takes days, not hours, so what is left of it is run by one
process, `scripts/run_nirv_chain.py`, which decides from Earth Engine's own record of the tasks and not from anything
it remembers. It waits for the tiles of observations; submits whatever tiles are still missing; waits for the blocks
of yearly values; runs `scripts/check_nirv_blocks.py`; then `02_build_nirv.py` and `02_assemble_degradation.py`, which
fills the NIRv columns of `degradation_by_unit.csv` — each only if the one before ended with exit 0. A step that ends
without a failed check (a dropped connection) is run again, three times at most; a step that ends at a failed check
or a failed task is not, and the chain stops and says why in `logs/nirv_chain.log`. The same process watches cost: a
task that has used far more compute than was measured for its kind is cancelled and the chain stops — the stop
condition whose absence cost about 106 EECU-hours on 6 October (§10). It cancels nothing else and resubmits nothing
that failed. It refuses to start while `logs/STOP_THE_CHAIN` exists.

**What happened to it.** Started on 6 October at 19:39 UTC, it ran for thirteen hours. On 7 October between
08:19:10 and 08:21:30 UTC every pending task of the project was cancelled: 12 tiles and 13 blocks of this pipeline and
8 export tasks of another job (§10). Not by this pipeline: its driver logs every cancellation it makes and made none,
it can cancel only a running task of its own that is over a cost limit, and neither the working session nor any of
its reviewers called Earth Engine in the forty minutes before (their transcripts were searched). At its next poll the driver found 12 tiles neither exported nor queued, said so, and
stopped, as it is written to: a tile that is gone while blocks wait behind it would give a block without that tile.
**Nothing was queued again.** 72 of 84 tiles exist and are untouched; no block had started. Whoever cancelled the tasks may
have meant to, and the queue is shared, so resuming is the project owner's decision. It is one command:
`run_nirv_chain.py --units 10_units/units.gpkg --resubmit-cancelled` queues the missing tiles again, and the blocks
only once every tile exists — which also retires the assumption of the next paragraph, since no block will then
have been queued ahead of a tile. It queues again only what was cancelled, never a task that failed.

**The blocks were queued before the tiles were done, and that is checked, not assumed.** To save a day of queue the
13 blocks of yearly values were submitted behind the tiles on 6 October, on the reasoning that a restricted project
runs one task at a time in the order submitted, so every block starts after every tile under it has finished.
`check_nirv_blocks.py` tests that three ways before anything is built on the blocks: each block's export task
started after the last successful export of every tile it reads; the scene list the blocks were queued with gives
the same day for every scene as the list on disk; and (`--probe`) on a 16 × 16-cell box of one block the cells that
have a stored pass in a season are exactly the cells the tiles hold an observation for. `02_build_nirv.py` then
checks the same thing for every unit and season (the land the blocks cover equals the land the tiles cover, to
1 m²). A block that fails is named, with the tile; nothing is exported again without the owner's word.

**How exact the areas are.** Two boxes are tested at every run:

- A box laid on pixel edges, 1,000 × 1,000 pixels, so that no pixel is cut: Earth Engine sums it to
  722,355,220.16 m²; its area on the WGS84 ellipsoid in closed form is 722,355,220.37 m² (-2.8e-10).
  The pixel areas are ellipsoidal and the grid is Hansen's. The run stops if this differs by more than 1e-08.
- The same box moved half a pixel, so that every boundary pixel is cut exactly in half: -7.8e-06, or
  1.41 m² short per cut pixel. Earth Engine's fraction for a cut pixel is approximate and leans low. On real
  boundaries the replication measured the shortfall at about 0.0009 of a pixel per cut pixel.

So a unit's area summed over pixels falls slightly short of its polygon's:

| | |
|---|---|
| all units, summed over pixels | 154,921.85 km² |
| all units, polygons on the ellipsoid | 154,929.33 km² |
| difference | -7.48 km² (-4.8e-05) |
| per unit, relative | median -6.6e-05; 1st to 99th percentile -6.8e-04 to +1.1e-05; range -5.0e-02 to +1.6e-03 |
| units below / above their polygon | 11,330 / 138 |
| units more than 0.1 % out / more than 1 % out | 56 / 2 |

The run stops if any unit is out by more than 1% of its area and more than 500 m² (under one pixel), or the
total by more than 0.1%. The 2 units more than 1 % out are slivers smaller than one pixel (35 m² and 590 m²); the
56 more than 0.1 % out are all under 23 ha. Every column carries the same small shortfall at each unit's
edge and none in its interior. The CoRE Stack and NIRv tallies use the same machinery and the same gate.

## 7. Reconciliation of the Hansen totals

No expected values were supplied for this stage, so the state totals are set beside the sources' own.

**Global Forest Watch** publishes Odisha's tree cover in 2000 and its yearly loss, by canopy threshold
(`00_raw/05_forest_reference/gfw_IND.xlsx`). Same data. The boundaries differ: theirs is GADM 3.6,
155,638 km²; ours is the units, 154,922 km² on Hansen's grid, 0.46 per cent less.

| | Global Forest Watch, ha | this pipeline, `treecover2000` **>** T, ha | difference | this pipeline, **≥** T, ha | difference |
|---|---|---|---|---|---|
| tree cover 2000, T = 10 | 3,776,619 | 3,751,738 | -0.66 % | 3,771,741 | -0.13 % |
| tree cover 2000, T = 30 | 2,680,194 | 2,663,043 | -0.64 % | 2,674,515 | -0.21 % |
| tree cover 2000, T = 50 | 1,567,786 | 1,557,221 | -0.67 % | 1,559,278 | -0.54 % |
| loss 2001–2020, T = 30 | 114,611 | 114,313 | -0.26 % | | |

The > T columns are like for like and are the ones the script gates: extents at 2%, the 2001–2020 loss at
10%. **That gate cannot tell > from ≥.** Both readings land well inside the tolerance and ≥ even lands nearer,
because the units cover less area than GADM and the pixels at exactly T happen to offset that. The gate catches a
gross error — a wrong band, wrong units, a lost group of polygons — and nothing finer. What shows that Global
Forest Watch computes > T is the replication on its own boundary (§9). Year by year the two are in
`hansen_reconciliation.csv`.

**Forest Survey of India, ISFR 2023** (Vol. II, Table 10.20.2; extracts in `00_raw/05_forest_reference/`). These are
not expected to agree, and they do not.

| | Hansen in 2000, km² | less loss to 2021, km² | ISFR 2023, km² | Hansen 2000 as % of ISFR |
|---|---|---|---|---|
| forest cover — ISFR's wording, canopy ≥ 10 % | 37,717 | 36,287 | 52,433.56 | 72 |
| the same read as canopy > 10 % | 37,517 | | 52,433.56 | 72 |
| moderately + very dense, canopy ≥ 40 % | 22,808 | | 28,289.97 | 81 |
| very dense, canopy ≥ 70 % | 2,100 | | 7,224.42 | 29 |

**On ISFR's inequality.** ISFR 2023 words its floor with "or equal" everywhere it defines forest cover: "tree
canopy density of more than or equal to 10%" (Vol. I, PDF page 14), "tree canopy of more than or equal to 10%"
(glossary, page 26), "canopy density more than or equal to 10% and above" (page 63), "canopy density of 10% and
above" (page 76), "canopy densities exceeding or equal to 10%" (page 81); and its classes are "equal to or more
than" 70, 40 and 10 per cent. The words "exceeding 10%" do not occur in the volume. A reading of the definition
as strictly above 10 per cent was put to this pipeline on 6 October 2026; it is not what the 2023 report says, so
the rows above follow the report, and the > 10 reading is shown beside it. The choice moves the Hansen figure by
200 km² and changes nothing in the comparison.

Why the gap, at the matching canopy line:

- **What counts as a tree.** Hansen counts only vegetation taller than 5 m. ISFR counts all tree canopy on a
  hectare or more "irrespective of ownership, legal status and land use", and "includes orchards, bamboo and palm".
- **When.** Hansen's mask is the year 2000; ISFR 2023 rests on imagery of October to December 2021. Hansen
  records loss since 2000 but its gain is not netted here, so regrowth and new plantation since 2000 are in ISFR
  and not in this figure.
- **How.** ISFR is interpreted from 23.5 m LISS-III imagery with a one-hectare minimum mapping unit and reports
  canopy density classes; Hansen is a per-pixel estimate of canopy closure from 30 m Landsat. The two percentages
  are not the same measurement, which is why the rows fall short by such different amounts.

Nobody should quote this pipeline's forest area as Odisha's forest cover. It is Hansen's year-2000 tree cover at a
stated inequality, used as a mask that is the same for every unit.

## 8. The area basis

Every area in stage 1 is a sum of pixel areas on the WGS84 ellipsoid. Since 6 October 2026 stage 0's `area_ha` is
on the same basis (`docs/UNITS.md` states the layer's area once: 154,929.33 km², ellipsoidal, WGS84). Before that
it was a UTM zone 45N area, 0.15 per cent too large overall and 0.67 per cent too large west of 82°E. The rebuild
changed `area_ha` and nothing else, and stages 1, 2 and 3 were re-run on the rebuilt layer: every data table came
out byte-identical. `area_ha` in `hansen_by_unit_thresholds.csv` is the unit's area summed over Hansen pixels and
`polygon_area_ha` its polygon's; the first is the right denominator for a share of pixels.

## 9. Verification applied

What was applied, and where:

| part | verification |
|---|---|
| Hansen forest and loss per unit (§1–2) | **full independent replication, twice**, without Earth Engine |
| loss by canopy band (§3, task A) | covered by the second replication, column by column — more than the one careful pass asked for |
| CoRE Stack tallies (§4a, task C) | **one careful pass**: the script's gates, a hand check on three units, and a reconciliation to the producers' one published Odisha figure |
| NIRv (§5, task B) | **full independent replication, two rounds** — a separate agent, docstring only, no Earth Engine, the same scenes from another archive. Round 1 confirmed the first design's values bit for bit and found that they follow the calendar; the design was changed on that finding. Round 2 confirmed the stored observations, the standardisation's arithmetic and the per-unit figures on test areas, and set out the new measure's limits. Its units are saved for comparison with the state-wide run, which does not exist yet. Before any of it: three independent critics of the design, and every band and table tested against a local recomputation |
| the assembly, `degradation_by_unit.csv` (task 1 of 7 October) | **one careful pass**: the script's own gates — every unit once, the yearly columns adding to the total, the > 30 band equal to the Hansen table, and 66 sums against the three sources' own summary tables — and an independent reviewer who rebuilt the columns from the sources (*The careful pass of 7 October*, below) |
| agreement table (§4b, task D) | **its arithmetic checked directly**: `scripts/verify_agreement.py` imports nothing from the builder and rebuilds, from the two sources' per-unit tables, each unit's reference land, rates, flags and class and every cut, count, expected count, odds ratio and rank correlation of the six tables — 55 of 55 checks passed; n = 11,468 units, 3,711 assessed. The bootstrap intervals are checked, not rebuilt. Then **one careful pass** by an independent reviewer, which found that the first version of this script claimed more than it checked (below) |
| housekeeping: a district for each outside-village unit, the git repository (task 5) | **one careful pass**: the script's gates and an independent reviewer, who found the district method's premise false; it was redone (below, and `docs/UNITS.md`) |
| the demo layer, `60_layer/` (task 6; `docs/LAYER.md`) | **by hand, in a browser**: the map was opened, 16 units were clicked — forest from none to the largest, both kinds of unit — and all 656 values displayed for them were read off the page and compared with the stage tables. Then, because sixteen is not 11,468, `scripts/verify_layer.py` rebuilt every displayed field of every unit from the stage tables: 79 of 79 checks passed; n = 11,468 units, 42 fields a unit, 14 class arrays. The clicking was on the build of 6 October; what has changed in the builds since, and what was read off the page again, is in `docs/LAYER.md` §9 |
| minimum forest area (§4c, task E) | one careful pass; it is arithmetic on the replicated Hansen table |
| stage 0 rebuild, manifest rows, README and docs edits | one careful pass, with byte-level checks where a check exists |

**The Hansen replications.** Each was a separate agent allowed to read only the script's docstring, rebuilding every
per-unit figure from the six public Hansen GFC-2025-v1.13 tiles with exact pixel-coverage fractions (exactextract)
and a closed-form WGS84 pixel area. Each saved and hashed its own figures before opening the pipeline's.

- **5 October 2026, when the mask was `treecover2000` ≥ 30.** Forest 2,674,514.57 ha against 2,674,624.44 from the
  tiles (−0.0041 %); loss 155,578.37 against 155,586.06 (−0.0049 %); no unit beyond 1 % and 0.5 ha. It is this
  replication that found Global Forest Watch's published figures to be for canopy strictly above the threshold,
  which led to the ruling in §2.
- **6 October 2026, on the mask `treecover2000` > 30 and the new canopy-band table.** All 11,468 units agree in every
  one of the 126 numeric columns of the three per-unit files. No unit differs by more than 1 % and 0.5 ha in any
  column.

| | pipeline, ha | tiles, ha | difference | largest gap for one unit, ha |
|---|---|---|---|---|
| `forest_ha` (`treecover2000` > 30) | 2,663,043.12 | 2,663,152.54 | −0.0041 % | 1.11 |
| `hansen_loss_ha` | 155,263.70 | 155,271.38 | −0.0049 % | 0.28 |
| land with `treecover2000` ≤ 10 | 11,740,446.75 | 11,741,036.07 | −0.0050 % | 1.45 |
| land with 10 < `treecover2000` ≤ 30 | 1,088,694.96 | 1,088,744.53 | −0.0046 % | 0.36 |
| loss on `treecover2000` ≤ 10 | 91,740.24 | 91,744.73 | −0.0049 % | 0.16 |
| loss on 10 < `treecover2000` ≤ 30 | 36,383.70 | 36,385.46 | −0.0049 % | 0.08 |
| loss on any canopy | 283,387.64 | 283,401.58 | −0.0049 % | 0.47 |
| the 25 yearly and 75 band-by-year columns | | | −0.0034 % to −0.0062 % | 0.04 |

- **Every total is 0.004 to 0.005 per cent below the tiles, and that is all.** It is Earth Engine's coverage fraction
  running low on pixels cut by a unit boundary: 0.0009 of a pixel per cut pixel, the same in every column. Where a
  class lies only in whole pixels (5,924 units for forest) the two agree to the fourth decimal of a hectare.
- **The inequalities are where the docstring says.** `forest_ha` sits 109 ha below the tiles' > 30 total and 11,581 ha
  below their ≥ 30 total; pixels at exactly 30 (11,472 ha) are in the band 10 < `treecover2000` ≤ 30 and pixels at exactly 10
  (20,004 ha) in the band `treecover2000` ≤ 10, in every unit where it can be seen.
- **Each claim was confirmed:** the bands' land adds up to the unit and their loss to unmasked loss; the summary and
  level tables follow from the per-unit files; the reconciliation's figures follow from them; and on Global Forest
  Watch's own boundary its published figures are reproduced by > T (within 0.9, 0.8 and 1.4 ha at 10, 30 and 50)
  and missed by ≥ T (by 0.53, 0.43 and 0.13 per cent).
- **After the check, stage 0 was rebuilt with ellipsoidal areas and Hansen was re-run on the rebuilt layer:** all six
  tables came out byte-identical, and the replicator repeated its comparison against the files on disk with the same
  result. One row was added later still — land and loss at `treecover2000` = 0, as an "of which" of the lowest band
  (825.91 km² of loss; the replicator's own figure for it from the tiles is 825.95 km²). The earlier columns were
  again byte-identical.

**What the second replication found wrong, none of it a number, and what was done:**

1. The Global Forest Watch gate cannot tell > from ≥: both readings pass it. Said plainly in §7 and in the docstring;
   the evidence for > is the replication on Global Forest Watch's own boundary, not the gate.
2. "The source repeats one row at 20°N" was only partly true: tree cover and the data mask are identical in the two
   tiles' copies of that row, but the loss year differs in 254 of its pixels. Corrected in the docstring.
3. Counts of units with any forest or any loss run a handful below the tiles, because Earth Engine returns zero for
   a sliver; and two count columns were named loosely. Renamed, and said in §1.
4. "Clearance of closed canopy" overstated the mask: a seventh of it has canopy of 31 to 39 per cent. Reworded.
5. The asset stores geodesic edges but the sums behave as straight-edged polygons. Immaterial (at most 0.094 ha for
   a unit); said in §6.
6. "To the hectare" should be "to within about a hectare". Corrected.
7. The caution about 2010/2011 named one of three steps in the series; in the lower bands the larger steps are at
   2013 and 2023. Said in §3, with the replicator's table of loss by period.

It also answered a question put to it: of the loss on `treecover2000` ≤ 10, 90.0 per cent is on pixels with
no canopy at all in 2000, and 39.9 per cent of it is dated 2023–2025 alone.

**The careful passes.**

- *CoRE Stack.* The script stops unless every pixel is in exactly one class of the legend, the classes and the
  no-value area add up to each unit, the zone images lie on one lattice, and each unit's area summed over pixels is
  within tolerance of its polygon's (−0.004 % in all). Three units were tallied interactively and matched. The
  producers' published Mayurbhanj figure was reproduced from their own earlier product (§4a).
- *Stage 0.* After the rebuild every unit's geometry is byte-identical to the layer before it and every column but
  `area_ha` is unchanged, in all four layers; stage 2's three tables and stage 3's twenty came out byte-identical.
- *Registered references.* The Global Forest Watch workbook's Odisha rows equal the constants in the script, year by
  year; the ISFR figures equal the registered extract; every quoted phrase is checked to be in the extract each time
  this document is generated.
- *Published facts.* Some 245 statements about the sources were gathered by five agents and each re-opened by a
  second; 6 were not confirmed (one wrong, five unsupported) and none of those is used here.

**The NIRv design critique.** Three independent critics (a remote-sensing lens, a statistical one, and the downstream
user's) read the design before the run. All three said the same four things, and all four were adopted: keep the
thirteen yearly values, not just a trend; measure the false-alarm rate instead of quoting it; do not test a
seven-season trend against one-step losses; and put all three measures on one reference before comparing them. Their
reviews are in `.session_scratch_2026-10-05/phase2/critique_*.txt`.

**The NIRv replication.** A separate agent, allowed to read only the scripts' docstrings and forbidden Earth Engine,
rebuilds the computation from the same Landsat 8 scenes read from a different archive (Microsoft's Planetary
Computer), saving and hashing its own figures before it opens the pipeline's.

**Round 1 reported in full (5 October 2026, 22:34 to 23:55 UTC; 655 scenes read, 3.9 GB): the first design's stored
values and per-unit figures hold — and what they measure is partly the calendar.** Its report is
`.session_scratch_2026-10-05/replicate_nirv/REPORT.md`.

*The yearly values, pixel by pixel (five blocks, 2,600,000 pixel-seasons).* In 2,467,997 of them the two archives
hold the same scenes, and in every one the observation count is equal and the stored value identical to the last bit
of a 32-bit float. The other 132,003 (5.1 per cent, all in seasons 2021 to 2024) lie inside the footprints of 34
scenes the replicator could not read — 32 that the Planetary Computer does not hold and 2 whose file there is
corrupt. In those the pipeline always has more observations, never fewer, and its value is attainable by adding that
many observations to the replicator's; for the one scene whose mask and red band could still be read, the pipeline's
extra observation is in exactly the 3,952 cells predicted. They are unverified, not wrong.

- "The Landsat pixel that contains the cell's centre" is the rule that reproduces the values, to well under a metre:
  moving the centre by 1 m would change 3.2 per cent of them.
- The mask reproduces every comparable observation count. But in these blocks `QA_RADSAT`, the "below 1" test and
  snow never decide a pixel, so the comparison does not show that they are applied; "above 0" and "water is not
  masked" are confirmed.
- The season boundary is where the docstring says: scenes one day outside the window are not in the counts.

*Per unit, end to end (the 97 units inside the first five tiles, against the pipeline's own run on them).* Every area
total is 0.0029 to 0.0039 per cent below the replicator's — Earth Engine's low fraction on boundary pixels, 0.00093
of a cell per cut cell, the same as for Hansen and nothing else — with no unit flagged in any of 21 area columns.
Season means agree to a median of 6 × 10⁻⁷ in the 1,025 unit-seasons no missing scene touches. The trend arithmetic,
recomputed from the pipeline's own yearly values, is identical at 300 of 300 sampled pixels (S, n and the contrast
flags exactly; the slope to 3 × 10⁻¹⁰). In the 28 units the missing scenes did not touch, every trend column agrees
to a few parts in 100,000 with no unit flagged. In the other 65 the replicator's figures differ — the pipeline's
declining area is 2.7 per cent below its own, the increasing area 11.7 per cent above — for a reason that is the
replicator's: its 2022–2024 values lack three scene-dates. So three scene-dates move a 97-unit total by 3 to 35 per
cent, which is itself a finding about the first design.

*The exact statements.* The critical values (34, 30, 27, 23; 15 and 13) and their one-direction sizes (2.0 to 2.3
per cent for thirteen seasons) are confirmed, as is the one-in-twenty chance of the before-and-after contrast.

*What it found wrong. None of it is an error in the code; all of it was acted on:*

1. **The yearly value carries the calendar, and the stored images did not keep the date.** Inside the window NIRv
   falls by 13 to 18 per cent of its mean per 30 days on land with `treecover2000` > 10 (28 to 31 per cent on
   `treecover2000` ≤ 10); the mean day of the kept observations moves by two to three and a half weeks between
   seasons; and the yearly value follows it (correlation −0.90 over nine seasons of the blocks; unit by unit over the
   97 units, a median of −0.80). Moving every observation to one date with one rate — a sensitivity test, not a
   correction — took the declining share of the blocks from 13.5 to about 6 per cent and the increasing share from
   0.8 to about 5. **The export was stopped and the design changed (§5).**
2. *"The nominal rate is a floor" was false.* About 2 per cent is the average over orderings of the seasons; most
   orderings flag less and a few flag four to twelve times more. By the script's own criterion the first design's
   declining share was not clearly beyond chance (re-ordered seasons reach it in 5 to 14 per cent of orderings).
   The docstring now says so.
3. *The figures depend on the scene list of the day, which was not recorded.* It now is: `nirv_scenes.csv`, with
   its hash in the provenance record.
4. *"Over seven seasons the trend test cannot see an outright clearance"* holds only for exactly tied values; with
   untied values a mid-window step is flagged with probability 0.29. Reworded.
5. *Unsaid: the thirteen-season test cannot flag a recent clearance* (a step after 2022, 2023 or 2024 leaves S at
   −30, −22, −12 against a critical 34). Now said.
6. *The observation count is of scenes, not dates*: where two rows of a path overlap, one pass counts twice, and
   that is nearly half the pixel-seasons of the test blocks. Now said; the new record is by pass.
7. *`missing_data_share` carries no information* — every cell has at least ten seasons — while 6 to 11 per cent of
   pixel-seasons rest on a single scene. The share of seasons resting on one pass is now reported (`nirv_rates.csv`).
8. *Each scene's NIRv is a 32-bit float before the median* — unsaid and immaterial (at most 3 × 10⁻⁸). Now said.

Eighty units drawn across the state were computed blind and saved, for comparison when the full run exists.

**Round 2 reported (6 October 2026, 00:42 to 01:47 UTC): the stored observations, the standardisation's arithmetic
and the per-unit figures of both yearly values hold; no error was found in the code. It also set out what the new
measure can and cannot bear.** Its report is `.session_scratch_2026-10-05/replicate_nirv/REPORT_round2.md`.

*The stored passes (two blocks of 10,000 cells; 2,080,000 bands).* Every band that does not lie under one of the 34
scenes the replicator cannot read is identical on both sides, value or emptiness (2,028,079 bands). Of the 571,332
passes both sides hold, 570,185 are identical to the last bit, including all 282,211 that are the mean of two rows;
the rest are one pass of which the replicator could read only one of the two rows. The path bands are equal in every
cell. The first design's bands in the new tiles equal the old asset's in 260,000 of 260,000 pixel-seasons. The
pipeline's scene list is the USGS's 1,041 scenes exactly.

*The arithmetic.* Given the pipeline's own stored passes, the replicator's code — written from the docstring — gives
the pipeline's rate to 7 × 10⁻¹⁸ and all 255,748 date-standardised yearly values to within 2 × 10⁻¹⁶.

*Per unit (12 units, against the pipeline's small run).* Land and tested-land totals are 0.003 to 0.011 per cent below
the replicator's, the pipeline lower in every unit (Earth Engine's boundary fraction again, and nothing else).
`nirv_declining_ha` 107.716 against 107.717 ha; `nirv_increasing_ha` 12.0625 against 12.0614; in the 11 units its
missing scenes did not touch, no unit is flagged in any of 37 value columns. The date-check table is reproduced.

*What it could not test against the pipeline:* the path step and the rule for too few dates — no cell of the files it
was given is seen from two paths, and none has few dates. (The path step was then tested inside Earth Engine on a box
where every cell has one: all 154, 134 and 151 bands of the three per-unit images equal numpy, §5. The rule for too
few dates excludes nothing in the replicator's 4.5 million cells.)

*What a user of the new value must know — the replicator's findings on the measure, on its own 97 units of the
south-west and 80 units drawn across the state:*

1. **It does what it was built to do.** The correlation between a unit's series and the mean day it was seen on goes
   from −0.79 to +0.19 (south-west, 61 units) and from −0.71 to +0.04 (state-wide, 21 units); the year-to-year
   scatter falls by 41 and 32 per cent. A simulation that keeps every cell's real passes, dates and paths and puts
   no-trend values on them shows the standardisation does not manufacture flags (2.1 to 2.5 per cent each way against
   a nominal 2.1), including through the rate being fitted on the passes it corrects.
2. **The trend now depends on the fitted rate at first order.** Where the scenes have drifted later over the years
   the correction is itself trended. Multiplying every cell's rate by 0.9 or 1.1 moves the declining share by about a
   tenth (south-west: 6.3, 5.8, 5.3 per cent at 0.9, 1.0, 1.1). And the rate is not known that well: a season's own
   rate differs from the pooled one by up to a fifth to two fifths.
3. **Single passes still decide a quarter of the flags.** Taking one pass at random from each cell turns over 20 to
   24 per cent of the declining flags (32 per cent for a plain median of passes). A pass far from 1 December is
   moved a long way, error and all: one hazy scene of 5 November 2023 pulls that season down by 18 per cent where it
   is the early pass, and changes the flags of the cells under it.
4. **Across regions the trend still goes with the drift of the dates** (rank correlation −0.38 over 243 blocks
   state-wide, down from −0.66; none within blocks). Either the regions whose scenes drifted later really declined
   more, or the correction falls short there. These data cannot tell which.
5. **The declining share is not beyond chance by the script's own null** — re-ordered seasons reach it in 7 per
   cent of orderings in the south-west and 22 per cent state-wide. The *increasing* share state-wide is (1.6 per
   cent of orderings).
6. With its own scenes (34 fewer than the pipeline's) the replicator's units give, on land with `treecover2000` > 10:
   south-west, 5.8 per cent declining and 4.4 increasing (first design 8.7 and 0.7); state-wide sample, 3.3 per cent
   declining and 10.0 increasing (first design 5.0 and 5.7). These are the replication's figures on 177 units, not
   the pipeline's result.

*What was done about it.* The docstring's sentence on recent clearance was corrected (a step in the last three
seasons is seldom flagged, not never), the day of a pass and the scatter are now defined exactly, and three things
were added to the script's output so that points 2 to 4 are measured on the full run instead of taken on trust:
`nirv_rate_sensitivity.csv` (the rate multiplied by 0 to 1.2, and one pass taken away from every pixel), and, in
`nirv_date_check.csv`, the rank correlation across units between the trend of a unit's series and the drift of its
dates. Its per-unit figures for 97 and 80 units under the new definitions are saved and hashed for comparison with the
full run.

**The tests of the NIRv scripts** (`.session_scratch_2026-10-05/phase2/tests/`, all re-runnable) are listed in §5:
the stored tiles against per-scene pixel values; the standardisation against a second implementation; every band of
the per-unit images against numpy; the tables against brute force from pixels; and the script run whole on a few
real units. These are tests of arithmetic on small areas. They are not results and not replication. The same folder
holds the tests of the three-measure agreement script of 6 October; that script was replaced on 7 October by one that
reads tables only (§4b), and its tests are retired with it.

**The careful pass of 7 October.** Three reviewers, one part each, read-only, each rebuilding the figures with code
of its own and none of them allowed Earth Engine; a finding of weight was then to be given to a second agent told to
refute it. The session ended while they were running. The two reviews that had come back were kept; the third was run
again; the findings of the first two were reproduced here instead of by second agents, except one.

- *The assembly.* The reviewer rebuilt every column of `degradation_by_unit.csv` for all 11,468 units from the
  sources' tables: no number in the table or its record failed to reproduce. What it found was in the path not yet
  taken — what the script does when NIRv lands, which the chain runs unattended. NIRv columns were copied and marked
  "built" with no check against NIRv's own summary table, and a NIRv table that was on disk but short of a unit, or
  built for another layer, came out as "pending" with exit 0: the chain would have announced a fill that had not
  happened. A second agent could not refute the first; the second was reproduced here. Both are fixed. NIRv is now
  held to `nirv_by_unit_level.csv` and to the row and blank-cell counts in its own record; a table that is there and
  cannot be used ends the script with exit 1; and the chain passes `--require-nirv`, under which "pending" is an error
  too. Tested in a sandbox copy on made-up NIRv tables — one good, ten bad in different ways, each ending as it
  should. From the same review: every unit is held to a second per-unit table of its source (13 columns, largest gap
  0.0003 ha), because sums by unit type cannot see a row given to the wrong unit; 78 sums are held to the sources' summary tables,
  the periods of the yearly columns among them; the table is read back as text before it replaces the old one; the
  record lists every file read; and `nirv_trend_ha_unadjusted` is carried, so that each pair of NIRv areas has its own
  land (63 columns). The docstring now says that `land_tc_gt10_ha` is measured on CoRE Stack's grid and is not the sum of
  the two Hansen band columns.
- *The agreement table.* The reviewer recomputed the summary and definitions tables with a percentile and a rank
  correlation written by hand, and every unit's class in the three windows (its count: 702 and 180 cells, 0 differing).
  **No number failed to reproduce; four findings changed what §4b says.** (1) The intervals resampled units singly, as
  if independent. Resampling whole districts makes them 2.7 to 4.8 times wider; those are now the intervals quoted, with
  the odds ratio within districts beside them (`agreement_intervals_by_district.csv`). (2) "The placebo behaves" was
  true pooled and in one of CoRE Stack's two zone models and false in the other; §4b says so now, from
  `agreement_by_zone.csv`. (3) The evidence cited for the 50 ha floor was measured on the `treecover2000` > 30 mask,
  not on this table's land, where it is weaker (`agreement_floor_repeatability.csv`); and the README still said the
  floor was applied to nothing. (4) `scripts/verify_agreement.py` claimed to compare cell by cell and did not: run on
  tampered copies, it passed with the cuts, the counts of flagged units, the window labels, most intervals and most of
  the definitions table altered, and a blank cell passed any comparison. It was rewritten (55 checks; its docstring
  lists what it re-derives and what it only checks) and then tried on eighteen tampered copies of the tables: it
  fails on seventeen and passes the one it says it cannot catch, an interval widened without losing its estimate.
  Lesser things: two gates in the builder that could not fail were replaced by a recount from the tables read back
  from disk; the delivered reading had one interval in the summary and another in the definitions table, drawn twice,
  and now has one; the docstring says that the flags are held fixed in every resample and which correlations carry an
  interval. The builder's code for (1) to (3) was written without the reviewer's and reproduces its figures — the zone
  and repeatability tables exactly, the district intervals to within the difference between two random streams.
  `agreement_by_unit.csv` and `agreement_summary.csv` are byte for byte what they were before the pass, so nothing
  downstream of them moved.
- *The housekeeping: a district for each outside-village unit, and the git repository.* The reviewer redid the collar
  for all 3,492 units with code of its own and matched the delivered table in every one; the mapping of names to
  codes, the counts and the summary reproduced. **And it found the premise false.** The script, its record, the README
  and `docs/UNITS.md` all said the DataMeet layer was the only district geometry among the inputs. It is not:
  `00_raw/04_boundaries/` holds panchayat polygons with a district code, which stage 3 already reads. They cover
  35.1 per cent of the outside-village land, so the method that was asked for — the majority of a unit's own area — can be
  applied to 2,170 units and was applied to none. Three of its four findings of weight went to a second agent told to
  refute them, and none was refuted; all four were reproduced here. The other three: a unit placed in Kendrapara, 42 km from the nearest village of
  that district (the reviewer's measurement), because a unit moved off its name took its district from the tally by
  2011 code, which the layer's miscoded villages contaminate; a sensitivity row that compared the 250 m collar with
  the districts already assigned at 100 m instead of with the names (60 where it should have read 92); and an override
  that rested on the claim that a name absent from the collar "cannot be right", which the panchayat polygons
  contradict for 3 of the 16 overridden units they cover. **The script was rewritten** (`docs/UNITS.md`): the name is
  kept, because on villages whose district is known it is right for 99.92 per cent against 97.88 for the area
  majority; the area majority is computed wherever it can be and reported beside it; a name is overridden only where
  both checks contradict it (13 units, not 32); ambiguity is the quantity asked for where that can be measured (3 units).
  21 units changed district. The agreement table's district intervals and the layer were rebuilt on the new table.
  Lesser things, fixed: blank cells are counted in the file as written; the count and area of these units are held to
  the layer's own record, where the old gate compared a table with itself. *Git:* 64 files tracked; the reviewer found
  no credential in the tree or in the history, and nothing tracked under the raw-data folders, the stage folders or the
  scratch folder. Left for the project owner: 1 tracked file over 1 MB (`00_raw/05_forest_reference/gfw_IND.xlsx`), which the `.gitignore`'s own
  comment would keep out; and every commit carries the machine's git identity, a work address, which is worth a look
  before anything is pushed.

The reviewers' own scripts are in `.session_scratch_2026-10-05/careful_pass/`, with the sandbox tests of the assembler
and of the verifier.

**The reviews before the unattended run.** Before the rewritten NIRv and agreement scripts were left to run for most
of a day, four independent reviewers read them, each with one question — will Earth Engine run this at state size;
does the arithmetic do what the docstring says; are the tables and records right; what happens when nobody is
watching — none of them allowed Earth Engine, and each finding was then attacked by a second agent told to refute it.
Nineteen findings came back. What was changed because of them, before the run: the record is written before the
intermediate tables are deleted, and a failed delete no longer fails the run; the gate on the stored values runs
before the per-unit sums, not after; intermediate tables carry a fingerprint of what they hold (§6); a unit series
that was not tested has a blank S and flag, where it had 0 and an empty string that the record's count of blanks
missed; the "one pass taken away" row of the sensitivity table rests on the same pixels as the rows it is read
against; Sqq is formed locally in Earth Engine's order of operations, because real pass patterns land exactly on its
threshold of 4 and the two orders round differently there; the records name the records they read; and the driver
was rewritten (§6). Two things the reviewers raised could only be settled on Earth Engine and were: a cell without a
rate comes back with no slope and no flag, and a cell with fewer than ten seasons has no trend (the "thin" test of
§5). One reviewer had computed, from the expression graph alone, some 4 × 10⁹ operations per cell for the
standardisation done on the fly against 2 × 10⁴ for the first design — the cost the batch test had by then
shown at 106 EECU-hours (§10). Had the review come before the test, it would have been found for nothing. Not
applied: a retry wrapper inside the shared helper, which was left untouched because the Hansen and CoRE Stack
records carry its hash; the driver retries a whole step instead.

**A second review, of the driver, the cost watch and the blocks queued ahead of their tiles** (6 October, three
reviewers asked for; two reported before the session's agent limit ended it, and four of their findings were
attacked by a second agent). What was changed because of it is the driver of §6: one process that reads Earth
Engine's own task records and holds no state of its own, in place of a shell script and a separate watchdog; the
order check done per block against the tiles under that block, not against the newest tile anywhere; the scene
list a block was queued with compared with the list on disk; the probe of one block against its tiles; and the
per-unit check that blocks and tiles cover the same land. The third reviewer's part — the yearly-values script
itself — was not reviewed a second time.

**Not checked:** why Earth Engine's fractions run low; Earth Engine's Hansen asset against the tiles other than
through these sums; the ISFR figures against the PDF itself (only against the registered extract); the claim that
"greater than 30%" is the commoner written form; CoRE Stack's classes against anything on the ground — the producers
say no ground truth exists for them.

The replications' scripts and tables are in `.session_scratch_2026-10-05/replicate_hansen/` and `replicate_hansen_gt30/`.
The Hansen tiles they read were deleted on 6 October 2026 on the project owner's instruction; they are public, and a
note in the first directory says where to fetch them.

## 10. Earth Engine compute, and the quota that slowed the NIRv run to a crawl

The project (`replicating-paper`) is a registered noncommercial Earth Engine project on the free Community tier:
150 EECU-hours a calendar month, reset on the first of the month (Pacific time). **On 5 October 2026 at about
21:35 UTC it exceeded that and went into restricted mode** ("Your project has exceeded its noncommercial compute
quota and is now in restricted mode").

| batch tasks since 1 October (read 2026-10-07T08:36:08Z) | tasks | EECU-seconds |
|---|---|---|
| other | 20 | 3 |
| nirv | 777 | 483,830 |
| agreement | 1 | 622 |
| corestack | 40 | 59,751 |
| hansen | 40 | 61,392 |
| units asset (upload, merge, re-export) | 39 | 0 |
| **all batch tasks** | 917 | **605,598** = 168.2 EECU-hours |

(The task counts include cancelled tasks that never started, which cost nothing.) The quota does not stop tasks, it
slows them, so the total has gone on rising past 150. **Batch tasks that had started before the restriction account
for 88,185 EECU-seconds, 24.5 of the 150 hours**; the other 517,412 were spent after it. What took
the project to its limit was therefore **interactive requests**, which task records do not show and which could not
be measured (Cloud Monitoring needs billing on the project). The likeliest cause is this stage's own scouting on
5 October — clear-observation counts, yearly values and class cross-tabs pulled at 4,000 to 12,813 scattered points
over Landsat collections. Other use of the project this month cannot be ruled out: it carries work that is not this
pipeline's (0 export tasks of another job were waiting in its queue when this was read). A query at scattered points makes
Earth Engine process a whole tile around every point, so each one cost about as much as the whole state. It should
have been piloted and costed like the batch runs were. Everything heavy now goes through batch tasks, each of which
records its cost, and the pixel sample is one batch task on stored images.

**What restricted mode does, measured.** Tasks still run, one at a time, in the order they were submitted, with
several idle minutes between one and the next; a task priority is refused ("Custom priority can only be set on tasks
in registered commercial projects"). Since it began, 97 tasks have started and finished in 34.32 hours
(2.8 an hour): 72 tile of stored observationss, median 9.3 minutes running; 1 block of yearly values, median 11.9 minutes running; 3 nirv per-unit groups, median 1.0 minutes running; 3 nirv point tables, median 1.7 minutes running; 1 agreement, median 1.4 minutes running; 8 corestack lulc groups, median 1.0 minutes running; 8 corestack change groups, median 1.3 minutes running; 1 tile of yearly medians (first design), median 11.8 minutes running.
**The pace fell during the day.** 72 tiles of observations finished between 2026-10-06T00:19:44Z and 2026-10-07T08:17:44Z. From one
finish to the next the median is 23 minutes — 6 over the first ten, 30 over the last ten, and once 5.7 hours — for a
task that runs for 9: most of the time is spent waiting. 12 tiles were still to come when this was read, which at
the pace of the last ten is about 6 hours once they are queued; the thirteen blocks of yearly values and the
per-unit tasks follow. An earlier estimate in this session (nine minutes a tile, the tiles done by early afternoon
of 6 October) was wrong by a factor of three. Before the quota ran out the same project ran three or four tile
exports at once, each in four to seven minutes. Nothing in stage 1 waits for any of this (§5).

**The queue is shared, and on 7 October it was emptied.** The project carries work that is not this pipeline's: on
6 October at 20:29–20:31 UTC eight export tasks of another job (`odisha_v120_3ha_…_clustering_…`) were queued behind
the NIRv tasks, where a queue that runs in the order submitted would have kept them for a day. They were left alone;
the driver counts and may cancel only tasks named `ictd_units_…`. On 7 October between 08:19:10 and 08:21:30 UTC
every task still pending was cancelled before it had started — 8 of the other job's, 13 blocks of yearly values and 12 tiles of stored observations — in
one sweep, newest first. This pipeline did not do it (§6). When this was read (2026-10-07T08:36:08Z) nothing was queued in the project at all.
What it cost this pipeline is queue time: the 72 tiles already exported are stored and are not affected.

**What the redesign cost.** 5 tiles of the first design had been exported when the replication reported; they are superseded
(the first design's values are in the new tiles too) and their collection, `ictd/nirv_yearly_units`, can be deleted.

**One test task cost more than everything else together, and should not have.** On 6 October at 03:20 UTC the
rewritten per-unit script was given its first batch test at the size of one production group (1,432 units,
22,445 km²). Its first-design group cost 13,758 EECU-seconds. Its date-standardised group had used
**380,962 EECU-seconds (106 EECU-hours) when it was cancelled by hand after ten minutes**, unfinished, and the
400-point sample 13,618. The cause: a model fitted per pixel from 104 stored bands, feeding thirteen yearly values
that feed 134 output bands, is recomputed by Earth Engine for every band of a `reduceRegions`; it shares no work
between them. The same arithmetic exported once as an image shares it: the pilot block of
`02_export_nirv_yearly.py` cost 722 EECU-seconds for 1.84 million cells, about 0.0004 a cell against roughly 0.1.
Two things were wrong on this side: the small interactive tests had passed and were taken as evidence about cost,
which they are not; and nothing limited what a task could spend — the script's own wait has no such stop. Both
are changed: derived per-pixel quantities are stored before they are reduced, and the driver cancels a task far
above the measured cost of its kind (§6). The project was already in restricted mode, so the waste was queue time,
not money; it is in the table above under NIRv.

**The ways forward are the project owner's:** let restricted mode work through the queue (a day or two, if the
machine that submits the later steps stays awake; it was happening until the queue was emptied on 7 October); wait for the reset on 1 November; or move the project to the
Contributor tier (1,000 EECU-hours a month; it needs a billing account on the project, and noncommercial use is not
charged). Using a second project to get round the limit is against Earth Engine's terms and was not done.

## 11. Sources opened for this stage

Each was opened on 6 October 2026 by one agent and re-opened by a second, which confirmed the statements this
document relies on (full record, with the words quoted: `.session_scratch_2026-10-05/phase2/research_results.json`).

| for | source | where |
|---|---|---|
| CoRE Stack: the legend of the change raster | core-stack-org/Tree-Health-Monitoring, modal_overall_change.js (GitHub, read 2026-10-06) | <https://github.com/core-stack-org/Tree-Health-Monitoring/blob/main/modal_overall_change.js> |
| CoRE Stack: the classes in the producers' words | core-stack-org/layers_metadata, layer_descriptions.csv, row tree_cover_change_raster (GitHub, read 2026-10-06) | <https://github.com/core-stack-org/layers_metadata/blob/main/layer_descriptions.csv> |
| CoRE Stack: High and Low are relative to a zone's median; accuracy; what was validated; Mayurbhanj | Goyal, Chauhan, Seth, ICTD 2024 paper, section 3.2 | <https://www.cse.iitd.ernet.in/~aseth/forest-health-ictd2024.pdf> |
| CoRE Stack: each year is three years taken together | core-stack-org/Tree-Health-Monitoring README (GitHub, read 2026-10-06) | <https://github.com/core-stack-org/Tree-Health-Monitoring/blob/main/README.md> |
| LULC v3: the legend | core-stack-org/layers_metadata, layer_descriptions.csv, row land_use_land_cover_raster (GitHub, read 2026-10-06); identical text in STAC item land_use | <https://github.com/core-stack-org/layers_metadata/blob/main/layer_descriptions.csv> |
| CoRE Stack: licence of the data (CC-BY-4.0 in its catalogue) | CoRE Stack STAC catalog, PanIndiaCatalogs/collection.json and child collections (read 2026-10-06); core-stack-backend computing/STAC_specs/generate_ST | <https://spatio-temporal-asset-catalog.s3.ap-south-1.amazonaws.com/CorestackCatalogs_merged_collection/PanIndiaCatalogs/collection.json> |
| Landsat 8 Collection 2 Level 2: bands, scale and offset | Google Earth Engine Data Catalog - USGS Landsat 8 Level 2, Collection 2, Tier 1 (page as served 6 Oct 2026) | <https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2> |
| Landsat 8-9: QA_PIXEL bits | USGS - Landsat Collection 2 Quality Assessment Bands (Wayback snapshot 1 Oct 2026) | <https://web.archive.org/web/20261001035258id_/https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands> |
| Landsat: QA_RADSAT bits | Google Earth Engine Data Catalog - USGS Landsat 7 Level 2, Collection 2, Tier 1 (2026); LC08 page lists 'Bit 8: Band 9 data saturated ... Bit 11: Terr | <https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LE07_C02_T1_L2> |
| Landsat 7: scan-line corrector failure | USGS LSDS-1927 Landsat 7 Data Users Handbook v3.0 (May 2024), section 2.2.3.3 | <https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1927_Landsat7-Data-Users-Handbook-v3.pdf> |
| Landsat 7: share of each scene lost | USGS LSDS-1927 Landsat 7 Data Users Handbook v3.0 (May 2024), section 2.2.3.3; corroborated by USGS Landsat 7 page ('78 percent of the scene's pixels  | <https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1927_Landsat7-Data-Users-Handbook-v3.pdf> |
| Landsat 7: orbit drift from 2017 | USGS - Landsat 7 mission page (Wayback snapshot 1 Sep 2026) | <https://web.archive.org/web/20260901083333id_/https://www.usgs.gov/landsat-missions/landsat-7> |
| Landsat 7 and 8: the near-infrared bands differ (Roy et al. 2016) | Roy et al. 2016, Remote Sensing of Environment 185:57-70 (PMC author manuscript PMC6999663), section 2 | <https://pmc.ncbi.nlm.nih.gov/articles/PMC6999663/> |
| Landsat: two surface-reflectance algorithms | USGS - Landsat Collection 2 Surface Reflectance (Wayback snapshot 17 Sep 2026) | <https://web.archive.org/web/20260917130523id_/https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance> |
| Earth Engine: sensSlope | Google Earth Engine API reference - ee.Reducer.sensSlope (page as served 6 Oct 2026); same docstring in github.com/google/earthengine-api python/ee/re | <https://developers.google.com/earth-engine/apidocs/ee-reducer-sensslope> |
| NIRv (Badgley, Field and Berry 2017) | Badgley, Field & Berry 2017, Science Advances 3(3):e1602244 (PMC full text) | <https://pmc.ncbi.nlm.nih.gov/articles/PMC5362170/> |
| UNCCD good-practice guidance: the trend threshold | Sims et al. 2021, UNCCD Good Practice Guidance, SDG Indicator 15.3.1, Version 2.0, section 4.2.4.2 | <https://www.unccd.int/sites/default/files/documents/2021-09/UNCCD_GPG_SDG-Indicator-15.3.1_version2_2021.pdf> |
| UNCCD: a declining trend alone is not enough | Sims et al. 2021, UNCCD Good Practice Guidance, SDG Indicator 15.3.1, Version 2.0 | <https://www.unccd.int/sites/default/files/documents/2021-09/UNCCD_GPG_SDG-Indicator-15.3.1_version2_2021.pdf> |
| US EPA: exact Mann-Kendall probabilities | US EPA 2000, Guidance for Data Quality Assessment: Practical Methods for Data Analysis, EPA QA/G-9 QA00 Update, Box 4-7 and Table A-11 | <https://www.epa.gov/sites/default/files/2015-06/documents/g9-final.pdf> |
| short series (Collaud Coen et al. 2020) | Collaud Coen et al. 2020, Atmospheric Measurement Techniques 13:6945-6964 | <https://amt.copernicus.org/articles/13/6945/2020/> |
| India Meteorological Department: monsoon withdrawal | India Meteorological Department press release, 'New Normal Dates of Onset/Progress and Withdrawal of Southwest Monsoon over India', Table-1 (2020) | <https://mausam.imd.gov.in/backend/assets/press_release_pdf/IMD_Press_release_new_onset_and_withdrawal_dates%28Final%29.pdf> |
| India Meteorological Department: cloud at Bhubaneswar | India Meteorological Department, 'Climatological Tables 1991-2020', station Bhubaneswar (20 deg 15' N, 85 deg 50' E), printed page 65 / PDF page 163 | <https://imdpune.gov.in/library/public/Climatological%20Tables%201991-2020.pdf> |
| India Meteorological Department: rainfall normals | IMD Meteorological Centre Bhubaneswar, 'Districtwise Monthly Normal Rainfall (in mm) of Odisha' (undated table; normal period not stated) | <https://mausam.imd.gov.in/bhubaneswar/mcdata/rfnormal.pdf> |
| Similipal: leaf fall | Mishra et al., 'Phenology of species of moist deciduous forest sites of Similipal biosphere reserve', Lyonia 11(1): 5-17 (2006) | <https://www.lyonia.org/articles/rbussmann/article_465/pdf/articleBody.pdf> |
| Sundargarh sal forest: seasonal greenness | Gupta, U., 'Study of temporal variation of vegetation indices and phenology of tropical deciduous broadleaf forest in Eastern India', ISPRS Archives X | <https://isprs-archives.copernicus.org/articles/XL-8/569/2014/isprsarchives-XL-8-569-2014.pdf> |
| Forest Survey of India: its season | Forest Survey of India, India State of Forest Report 2023, Volume 1, Chapter 2 (section 2.3) and executive summary | <https://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf> |
| Earth Engine: noncommercial tiers | Google Earth Engine Guides - Earth Engine Noncommercial Tiers (page last updated 2026-09-25) | <https://developers.google.com/earth-engine/guides/noncommercial_tiers> |
| Earth Engine: what happens when the quota runs out | Google Earth Engine Guides - Earth Engine Noncommercial Tiers (page last updated 2026-09-25) | <https://developers.google.com/earth-engine/guides/noncommercial_tiers> |

Hansen Global Forest Change is `UMD/hansen/global_forest_change_2025_v1_13`; the Global Forest Watch workbook and the
ISFR 2023 extracts are registered in `00_raw/05_forest_reference/` with manifest rows.
