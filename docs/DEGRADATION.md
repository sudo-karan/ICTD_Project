# Stage 1 — forest condition per unit

*Built by `scripts/02_upload_units_asset.py`, `02_build_hansen.py`, `02_build_corestack.py`, `02_build_nirv.py`,
`02_build_agreement.py`, `02_assemble_degradation.py` and `02_propose_forest_floor.py` (shared code in
`scripts/_ee_units.py`). Every figure below is from `20_degradation/*.provenance.json`, the tables beside
them, or `00_raw/`. All 11,468 units of the base layer are measured, the 3,492 outside-village units included, and
every table gives them separately.*

Three sources, three different things:

| source | what it measures | state |
|---|---|---|
| Hansen Global Forest Change | stand-replacing loss of tree cover, by year 2001–2025, on a year-2000 canopy mask | built, independently replicated twice |
| CoRE Stack tree-change classes | a change of class in canopy density or height between about 2016–19 and 2022–25, inside the producers' tree mask | built (run 2026-10-05T21:40:02Z); reconciled to the producers' one published Odisha figure |
| NIRv trend from Landsat 8 | a decline in November–December greenness, 2013–2025 | redesigned on 6 October after the independent replication; the observations are being exported, the yearly values are queued behind them, and the per-unit scripts are rewritten and tested (§9) |

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
miss them by 0.43 per cent with ≥ 30 (independent replication, §8). The notes and the numbers disagree; this
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
  (§8) dated the steps to 2011, 2013 and 2023 and found the same pattern in Global Forest Watch's own published
  figures. Do not read it as a trend on the ground.
- **The band 10 < `treecover2000` ≤ 30 is the one that bears on open forest**: 10,887 km² of land, 3.3 per cent
  of it lost, half of it in outside-village units. It is small beside the mask (26,630 km², 5.8 per cent lost).
- **In outside-village units nearly half the land had no canopy in 2000** (19,923 of 41,357 km²), and loss on it
  runs at 2.0 per cent against 0.45 in the villages' open land.

So the mask does hide a large area of recorded loss, but Hansen cannot say that this area is degraded forest. What
it shows is tree cover coming and going on land that was open in 2000. Whether forest that was already open is
getting worse is a question for a measure of condition, not of clearance.

## 4. The two measures of condition, and what they can bear

### 4a. CoRE Stack tree-change classes (task C)

`corestack_by_unit.csv`, n = 11,468 units; blank cells: `corestack_missing_share` in 11 units that have no value at all.

**What the product is** (from the producers' own code, metadata and paper; every statement below was opened and
re-opened by a second reader, sources in §10). `overall_change_2017_2023` is a 25 m raster in eleven pieces, one per
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
  panchayat units. It is not forest loss; §4c carries it as a state of its own beside class −1.
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

### 4b. NIRv from Landsat 8 (task B)

**State: redesigned on 6 October after the independent replication; the observations are being exported, the yearly values are queued behind them, and the per-unit scripts are rewritten and tested (§9).** `nirv_by_unit.csv` does not exist yet. 23 of 84 tiles of stored observations had been exported when this was written (2026-10-06T04:41:15Z).

NIRv is the near-infrared reflectance of vegetation, NDVI × NIR (Badgley, Field and Berry 2017): the part of a
pixel's near-infrared reflectance that comes from vegetation. It tracks canopy structure.

#### What the replication found, and what was changed

**The first design measured the calendar.** It stored, for each pixel and season, the median NIRv of the clear
scenes of 1 November – 31 December, and fitted the trend to those thirteen values. An independent replication
(§8) reproduced the stored values bit for bit — and then showed what they are made of. Inside the window a forest
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
   as an image cost 722 EECU-seconds for a pilot block of 1.84 million cells (§9).
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

**What the standardisation does not do, and what it costs** (measured by the replication's second round, §8, on its
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
- *The whole script.* Last, the whole script was run on 7 small units inside the pilot block of stored yearly values (run 2026-10-06T04:45:03Z; the sums and the point reads by small interactive requests instead of batch tasks): every gate passed. At 120 sampled pixels the stored standardised values, rates, passes and mean days equal the ones recomputed from the stored passes (largest gaps 0e+00 in the value, 5e-08 of itself in the rate), and at 40 of them Earth Engine's slopes, S, n and contrasts equal numpy's (largest slope gap 2e-10; S, n and flags identical). On those units the correlation of a unit's series with the mean day it was seen on goes from -0.60 (first design) to +0.20, its year-to-year scatter from 6.0 to 3.9 per cent, and the declining share of their 26 km² of land with `treecover2000` > 10 from 4 to 2 per cent. That is test output on a few square kilometres, not a result.
- *Not yet run when this was written:* the two per-unit scripts' own batch path (the point reads and the group
  tables as real batch tasks). The unattended chain is its first run; the gate comes before the sums, and a
  watchdog bounds what a task may cost.

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

**What this means for the columns.** `nirv_slope` and `nirv_declining_ha` will be produced for every unit from the
date-standardised value, with the first design's beside them as `_unadjusted`, the increasing area, and the
measured false-alarm rate. Which of the two the project uses is the owner's ruling; the delivered pair is the
date-standardised one because the other is known to follow the calendar. Whether NIRv then carries a signal of
degradation is what the state-wide run has to show. Nothing so far shows it.

### 4c. Setting the three beside one another (task D)

**State: `scripts/02_build_agreement.py` is written and tested; it has not run, because it needs the stored NIRv values and the NIRv tables.**

**An interim reading from the two sources that exist, unit by unit — not the table this section is for.** From
`hansen_loss_by_canopy_band_by_unit.csv` and `corestack_by_unit_bands.csv`, on land with `treecover2000` > 10, for units
with at least 50 ha of it under both: the rank correlation of Hansen's loss rate 2019–2022 with CoRE Stack's class −1
rate, with its net rate (−1 minus 1) and with its class −2 rate; and how many units are in the top fifth on Hansen, on
class −1, and on both, beside the number expected if the two were unrelated.

| | units | Hansen vs class −1 | Hansen vs net | Hansen vs class −2 | top fifth, Hansen | top fifth, class −1 | both | both, if unrelated |
|---|---|---|---|---|---|---|---|---|
| all units | 3,711 | +0.37 | +0.26 | +0.18 | 742 | 742 | 251 | 148 |
| outside-village units | 1,207 | +0.31 | +0.24 | +0.31 | 299 | 351 | 124 | 87 |
| LGD panchayat units | 2,504 | +0.38 | +0.26 | +0.15 | 443 | 391 | 127 | 69 |

This compares rates per unit on two different grids and says nothing about whether the two flag the same pixels.

From the random sample (12,813 points; CoRE Stack and Hansen only): on land with `treecover2000` > 10, CoRE Stack class −1 is
16 of 40 valued points that have Hansen loss dated 2019–2023 (40 per cent) and 668 of 2,914 that have no Hansen loss
(23 per cent). None of the 65 Hansen-loss points of those years is CoRE Stack class −2. With one flag on for about
2 per cent of the land and another for about a quarter, raw overlap restates base rates; the table therefore gives,
beside every overlap, the area expected if the flags were unrelated.

**The three do not measure the same thing**, and the table is built so that this shows. Hansen dates the outright
removal of a pixel's tree cover. NIRv is a pixel's November–December greenness, season by season. CoRE Stack is a
class of change between two three-year periods. A cleared pixel should show in all three; a pixel that thinned under
a standing canopy can show only in NIRv and in CoRE Stack's class −1.

**The design, as changed by three independent critiques** (`.session_scratch_2026-10-05/phase2/critique_*.txt`):

- **The common window is the headline: change between the three years to mid-2019 and the three years from
  mid-2022**, which is what CoRE Stack compares (each of its "years" is three agricultural years taken together).
  NIRv: the before-and-after contrast of §4b on the date-standardised value, whose two sets of seasons lie inside
  CoRE Stack's two periods — *lower*, *higher* or neither. Hansen: loss dated 2019, 2020, 2021 or 2022, the calendar years between the periods (a loss
  dated 2023 cannot make NIRv "lower" by that rule, because the 2022 season precedes it; losses of 2016–2018 and of 2023 are
  shown beside it in the control below). CoRE Stack in four states: class −2, class −1, class 1, and the rest (0, 2, 3, 4).
- **One reference for all three:** grid cells with `treecover2000` > 10 where CoRE Stack has a class from −2 to 4 and
  NIRv has all six seasons. What that leaves out, and why, is tallied per unit. Every reference cell falls in exactly
  one of 2 × 3 × 4 = 24 cells, separately for 10 < `treecover2000` ≤ 30 and for `treecover2000` > 30, and every table
  is given for all units, LGD panchayat units and outside-village units.
- **The headline table** is those 24 folded to 2 × 2 × 2: Hansen loss 2019–2022 × NIRv lower × CoRE Stack class −1.
  Class 1 and NIRv *higher* stay in the cross-tabulation as placebos: if NIRv "lower" is as common on CoRE Stack's
  "improvement" as on its "degradation", the two do not agree, whatever their overlap in hectares.
- **What is reported for every pair of flags:** the overlap; the overlap expected by chance (the product of the
  two areas over the reference area) and the ratio of the two; the odds ratio, with a 95 per cent interval from
  resampling units; and the share of one flag that carries the other beside the share of the rest that does.
- **Unit by unit:** each unit's eight areas, so that "all three agree" is an area and not a vote; and, for units
  with at least 50 ha of reference land, the rank correlations of the three rates and the number of units in the
  top fifth on all three, two, one and none, beside the number expected if the three were unrelated.
- **The full span, separately, and not one period:** Hansen loss in any year 2001–2025, NIRv declining or increasing
  over 2013–2025, CoRE Stack as it is. A pixel cleared in 2005 and regrown is "Hansen loss" and "NIRv increasing" in
  that version — disagreement by construction — so it is reported and is not a test of agreement.
- **A positive control:** the share of Hansen-loss pixels each NIRv rule flags, by year of loss. If that is flat near
  the chance rate, NIRv does not see even clearance and cannot be claimed to see thinning.

Everything is on Hansen's grid. CoRE Stack is 25 m, so each grid cell takes the CoRE Stack pixel that contains its
centre; the script measures how far that moves CoRE Stack's margins from the ones summed on its own grid, and stops
unless its Hansen and NIRv margins equal the two sources' own per-unit tables.

**Checked before the state-wide run** (`.session_scratch_2026-10-05/phase2/tests/`): all 151 bands of the per-unit
image, summed by Earth Engine over a box of 4,096 cells, equal the same sums rebuilt in numpy from arrays of the
stored yearly NIRv values, `treecover2000`, `lossyear` and the CoRE Stack class of that box (no difference at all);
and the delivered tables — the eight cells, every pair's overlap, chance expectation, odds ratio and conditional
rates, the per-unit cells and rates — equal a brute-force recomputation straight from the pixels on pretend units cut
from those boxes. Last, the whole script was run on 7 small units inside the pilot block of stored yearly values (run 2026-10-06T04:45:53Z; the sums by small interactive requests): the cells add up to the reference land in every unit, and its Hansen and NIRv margins equal the two sources' own per-unit tables unit by unit (largest gap 0.0000 ha, which is rounding). An earlier run of the same script on 97 units used the first design's NIRv and is superseded. The arithmetic check on the real table is owed when it exists.

### 4d. A minimum forest area for stage 4 (task E) — a recommendation, applied to nothing

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

## 5. Getting 11,468 polygons into and out of Earth Engine

**The limit.** Earth Engine refused a single request of 11.5 MB with "Request payload size exceeds the limit: 10485760 bytes."
The base layer is 94.6 MB as GeoJSON (2,447,144 vertices; the largest unit alone is 1.6 MB), and the project
has no Cloud Storage bucket to stage a file in. So it was sent in 18 parts, each a batch task exporting to
its own table asset with the encoded request held under 9,071,819 bytes; Earth Engine then merged the parts
into one asset and the parts were deleted. The asset is `projects/replicating-paper/assets/ictd/units`; its properties are
`unit_id`, `unit_level`, `outside_village`. It carries no area: the first upload did, a UTM figure that stage 0 has
since replaced (§7), so on 6 October 2026 the asset was re-exported server-side without it and checked again.

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

**The unattended chain.** In restricted mode (§9) the work takes most of a day, so the steps after the export of
the observations are run by a driver in the session folder (`run_phase2_chain.sh`): the yearly values, a check that
every block of them was computed after every tile was finished, `02_build_nirv.py`, `02_build_agreement.py`, the
assembly and the direct arithmetic check — each only if the one before ended with exit 0. A step that ends without
a failed check (a dropped connection) is run again, three times at most; a step that ends at a failed check or a
failed task is not. A watchdog cancels any task that uses far more compute than was measured for its kind and
stops the chain — the stop condition whose absence cost about 106 EECU-hours on 6 October (§9).

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

## 6. Reconciliation of the Hansen totals

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
Forest Watch computes > T is the replication on its own boundary (§8). Year by year the two are in
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

## 7. The area basis

Every area in stage 1 is a sum of pixel areas on the WGS84 ellipsoid. Since 6 October 2026 stage 0's `area_ha` is
on the same basis (`docs/UNITS.md` states the layer's area once: 154,929.33 km², ellipsoidal, WGS84). Before that
it was a UTM zone 45N area, 0.15 per cent too large overall and 0.67 per cent too large west of 82°E. The rebuild
changed `area_ha` and nothing else, and stages 1, 2 and 3 were re-run on the rebuilt layer: every data table came
out byte-identical. `area_ha` in `hansen_by_unit_thresholds.csv` is the unit's area summed over Hansen pixels and
`polygon_area_ha` its polygon's; the first is the right denominator for a share of pixels.

## 8. Verification applied

What was applied, and where:

| part | verification |
|---|---|
| Hansen forest and loss per unit (§1–2) | **full independent replication, twice**, without Earth Engine |
| loss by canopy band (§3, task A) | covered by the second replication, column by column — more than the one careful pass asked for |
| CoRE Stack tallies (§4a, task C) | **one careful pass**: the script's gates, a hand check on three units, and a reconciliation to the producers' one published Odisha figure |
| NIRv (§4b, task B) | **full independent replication, two rounds** — a separate agent, docstring only, no Earth Engine, the same scenes from another archive. Round 1 confirmed the first design's values bit for bit and found that they follow the calendar; the design was changed on that finding. Round 2 confirmed the stored observations, the standardisation's arithmetic and the per-unit figures on test areas, and set out the new measure's limits. Its units are saved for comparison with the state-wide run, which does not exist yet. Before any of it: three independent critics of the design, and every band and table tested against a local recomputation |
| agreement table (§4c, task D) | **not built.** Its arithmetic was checked directly on test areas — every band against numpy, every table against brute force from the pixels, and a 35-check script that re-derives the delivered figures from the per-unit cells. The same check on the real table is owed with it |
| minimum forest area (§4d, task E) | one careful pass; it is arithmetic on the replicated Hansen table |
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

1. The Global Forest Watch gate cannot tell > from ≥: both readings pass it. Said plainly in §6 and in the docstring;
   the evidence for > is the replication on Global Forest Watch's own boundary, not the gate.
2. "The source repeats one row at 20°N" was only partly true: tree cover and the data mask are identical in the two
   tiles' copies of that row, but the loss year differs in 254 of its pixels. Corrected in the docstring.
3. Counts of units with any forest or any loss run a handful below the tiles, because Earth Engine returns zero for
   a sliver; and two count columns were named loosely. Renamed, and said in §1.
4. "Clearance of closed canopy" overstated the mask: a seventh of it has canopy of 31 to 39 per cent. Reworded.
5. The asset stores geodesic edges but the sums behave as straight-edged polygons. Immaterial (at most 0.094 ha for
   a unit); said in §5.
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
   0.8 to about 5. **The export was stopped and the design changed (§4b).**
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
where every cell has one: all 154, 134 and 151 bands of the three per-unit images equal numpy, §4b. The rule for too
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

**The tests of the new scripts** (`.session_scratch_2026-10-05/phase2/tests/`, all re-runnable) are listed in §4b and
§4c: the stored tiles against per-scene pixel values; the standardisation against a second implementation; every
band of the per-unit images against numpy; the tables against brute force from pixels; and both scripts run whole on
a few real units. These are tests of arithmetic on small areas. They are not results and not replication.

**The reviews before the unattended run.** Before the rewritten NIRv and agreement scripts were left to run for most
of a day, four independent reviewers read them, each with one question — will Earth Engine run this at state size;
does the arithmetic do what the docstring says; are the tables and records right; what happens when nobody is
watching — none of them allowed Earth Engine, and each finding was then attacked by a second agent told to refute it.
Nineteen findings came back. What was changed because of them, before the run: the record is written before the
intermediate tables are deleted, and a failed delete no longer fails the run; the gate on the stored values runs
before the per-unit sums, not after; intermediate tables carry a fingerprint of what they hold (§5); a unit series
that was not tested has a blank S and flag, where it had 0 and an empty string that the record's count of blanks
missed; the "one pass taken away" row of the sensitivity table rests on the same pixels as the rows it is read
against; Sqq is formed locally in Earth Engine's order of operations, because real pass patterns land exactly on its
threshold of 4 and the two orders round differently there; the records name the records they read; and the driver
was rewritten (§5). Two things the reviewers raised could only be settled on Earth Engine and were: a cell without a
rate comes back with no slope and no flag, and a cell with fewer than ten seasons has no trend (the "thin" test of
§4b). One reviewer had computed, from the expression graph alone, some 4 × 10⁹ operations per cell for the
standardisation done on the fly against 2 × 10⁴ for the first design — the cost the batch test had by then
shown at 106 EECU-hours (§9). Had the review come before the test, it would have been found for nothing. Not
applied: a retry wrapper inside the shared helper, which was left untouched because the Hansen and CoRE Stack
records carry its hash; the driver retries a whole step instead.

**Not checked:** why Earth Engine's fractions run low; Earth Engine's Hansen asset against the tiles other than
through these sums; the ISFR figures against the PDF itself (only against the registered extract); the claim that
"greater than 30%" is the commoner written form; CoRE Stack's classes against anything on the ground — the producers
say no ground truth exists for them.

The replications' scripts and tables are in `.session_scratch_2026-10-05/replicate_hansen/` and `replicate_hansen_gt30/`.
The Hansen tiles they read were deleted on 6 October 2026 on the project owner's instruction; they are public, and a
note in the first directory says where to fetch them.

## 9. Earth Engine compute, and the quota that slowed the NIRv run to a crawl

The project (`replicating-paper`) is a registered noncommercial Earth Engine project on the free Community tier:
150 EECU-hours a calendar month, reset on the first of the month (Pacific time). **On 5 October 2026 at about
21:35 UTC it exceeded that and went into restricted mode** ("Your project has exceeded its noncommercial compute
quota and is now in restricted mode").

| batch tasks since 1 October (read 2026-10-06T04:41:15Z) | tasks | EECU-seconds |
|---|---|---|
| nirv | 777 | 433,145 |
| agreement | 1 | 622 |
| corestack | 40 | 59,751 |
| hansen | 40 | 61,392 |
| units asset (upload, merge, re-export) | 39 | 0 |
| other | 3 | 3 |
| **all batch tasks** | 900 | **554,913** = 154.1 EECU-hours |

(The task counts include cancelled tasks, which cost nothing.) Batch tasks account for 154.1 of the 150 hours.
The rest went on **interactive requests**, which task records do not show and which could not be measured (Cloud
Monitoring needs billing on the project). The likeliest cause is this stage's own scouting on 5 October —
clear-observation counts, yearly values and class cross-tabs pulled at 4,000 to 12,813 scattered points over Landsat
collections — though earlier use of the project this month cannot be ruled out. A query at scattered points makes
Earth Engine process a whole tile around every point, so each one cost about as much as the whole state. It should
have been piloted and costed like the batch runs were. Everything heavy now goes through batch tasks, each of which
records its cost, and the pixel sample is one batch task on stored images.

**What restricted mode does, measured.** Tasks still run, one at a time, in the order they were submitted, with
several idle minutes between one and the next; a task priority is refused ("Custom priority can only be set on tasks
in registered commercial projects"). Since it began, 48 tasks have started and finished in 6.44 hours
(7.5 an hour): 23 tile of stored observationss, median 7.6 minutes running; 1 block of yearly values, median 11.9 minutes running; 3 nirv per-unit groups, median 1.0 minutes running; 3 nirv point tables, median 1.7 minutes running; 1 agreement, median 1.4 minutes running; 8 corestack lulc groups, median 1.0 minutes running; 8 corestack change groups, median 1.3 minutes running; 1 tile of yearly medians (first design), median 11.8 minutes running.
61 tiles of observations were still to come when this was read, at about nine minutes a tile; the thirteen
blocks of yearly values are queued behind them, and the per-unit sums and the agreement table follow, two to four
hours of queue more. Before the quota ran out the same project ran three or four tile exports at once, each in
four to seven minutes; at that pace the remaining work is two to three hours.

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
are changed: derived per-pixel quantities are stored before they are reduced, and a watchdog cancels a task far
above the measured cost of its kind (§5). The project was already in restricted mode, so the waste was queue time,
not money; it is in the table above under NIRv.

**The ways forward are the project owner's:** let restricted mode work through the queue (about a day, if the
machine that submits the later steps stays awake); wait for the reset on 1 November; or move the project to the
Contributor tier (1,000 EECU-hours a month; it needs a billing account on the project, and noncommercial use is not
charged). Using a second project to get round the limit is against Earth Engine's terms and was not done.

## 10. Sources opened for this stage

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
