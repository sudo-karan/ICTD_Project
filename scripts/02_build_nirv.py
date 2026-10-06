#!/usr/bin/env python3
"""
Stage 1 - NIRv per analysis unit, from the stored Landsat 8 observations and the stored yearly values made from them.

    python scripts/02_build_nirv.py --units 10_units/units.gpkg

In : --units    the stage-0 layer and its Earth Engine table asset (see 02_upload_units_asset.py)
     projects/<project>/assets/ictd/nirv_obs_<layer stem>    every clear November-December Landsat 8 observation of
                                                   2013-2025, one band per pass (02_export_nirv_observations.py - READ
                                                   ITS DOCSTRING FIRST: what a kept observation is, the grid, the four
                                                   slots, the two path parities, the bands o_<season>_<slot><e|o>,
                                                   path_e, path_o, nirv_<season>, obs_<season>)
     projects/<project>/assets/ictd/nirv_std_<layer stem>    the date-standardised yearly value of every cell, with its
                                                   rate, its passes and their mean day (02_export_nirv_yearly.py - READ
                                                   ITS DOCSTRING TOO: it has the exact arithmetic of the standardisation
                                                   and the bands std_<season>, passes_<season>, day_<season>, g, h, two)
     20_degradation/nirv_scenes.csv                the scenes behind both assets and their times, and the two exports'
     20_degradation/nirv_observations.provenance.json, nirv_yearly.provenance.json    records, which must fit one another
     UMD/hansen/global_forest_change_2025_v1_13    bands treecover2000 and lossyear: the canopy bands and reference forest
Out: 20_degradation/ and nowhere else
     nirv_by_unit.csv            unit_id, nirv_slope, nirv_declining_ha, and what they rest on
     nirv_by_unit_bands.csv      the same by band of year-2000 canopy, with the other measures of the same pixels
     nirv_by_unit_season.csv     unit x season: mean NIRv of the unit's land with tree canopy, and the mean day it was seen
     nirv_by_unit_series.csv     the trend of each unit's own mean series, as it is and relative to reference forest
                                 (S and the flag are blank where a series has fewer than ten seasons)
     nirv_by_unit_level.csv      lgd_panchayat units against outside_village units, and all units
     nirv_null.csv               how much "decline" re-ordered seasons produce: the measured false-alarm rate
     nirv_date_check.csv         does the yearly value still follow the date of the scenes? before and after
     nirv_rates.csv              how much land has a rate and a path step, the rate itself, and how thin the seasons are
     nirv_rate_sensitivity.csv   how much the result hangs on the rate, and on any single pass
     nirv_reference_series.csv   the mean NIRv of all reference forest, season by season
     nirv_pixel_sample.csv       random pixels: everything stored for them (yearly values, rates, passes, mean days) and,
                                 for the first 400, their trends and contrasts as Earth Engine computes them
     nirv_pixel_sample_passes.csv   the same pixels' stored passes, one row per pass
     nirv.provenance.json        inputs, UTC run time, definitions, checks, n and missingness
     Every table carries BOTH yearly values described next: std_ / "date-standardised" and raw_ / "first design".

WHAT NIRv IS. The near-infrared reflectance of vegetation: NIRv = NDVI x NIR, with NDVI = (NIR - red) / (NIR + red)
(Badgley, Field and Berry 2017). It is the part of a pixel's near-infrared reflectance that comes from vegetation,
and it tracks canopy structure. No constant is subtracted from NDVI here.

TWO YEARLY VALUES PER PIXEL AND SEASON.
  FIRST DESIGN (raw_): the median NIRv of the season's kept scenes - the stored band nirv_<season>. It was specified,
    built, and reproduced bit for bit by an independent replication, which then showed what is wrong with it: inside
    the window a forest pixel's NIRv falls by 13 to 18 per cent a month, and the dates of the clear scenes move by
    weeks from season to season, so the median follows the calendar (over nine seasons of five test blocks its
    correlation with the mean day of the clear scenes is -0.90). It is kept so that the two can be compared.
  DATE-STANDARDISED (std_): THE ONE THE DELIVERED COLUMNS USE - the stored band std_<season>. For each cell, NIRv is
    modelled within seasons as a level plus a rate g x (day - 30) plus a step h for the odd path, fitted by least
    squares over all the cell's passes of all thirteen seasons; each pass is moved to day 30 (1 December) by g and to
    the cell's usual mix of paths by h; the yearly value is the median of the season's moved passes, stored as a
    32-bit float. The exact arithmetic, the rule for a cell with too few dates (no value) and the rule for a path
    step are in the docstring of 02_export_nirv_yearly.py, which computes it once per cell.
    What it does NOT do, and what it costs:
      - it uses one straight-line rate per cell for all thirteen seasons, so a year whose leaf fall came early or
        late is not put right (a season's own rate can differ from the pooled one by a fifth to two fifths), and a
        cell cleared inside a season bends its own rate;
      - where the scenes' dates have drifted over the years, THE TREND DEPENDS ON g AT FIRST ORDER: on the
        replication's units a tenth more or less rate moved the declining share by about a tenth. How much the
        result hangs on the rate is tabulated (THE RATE AND THE SINGLE PASS, below);
      - a season resting on a single pass far from 1 December is moved a long way, the pass's own error with it:
        one hazy early-November scene can pull a season down by a fifth.
    On five test boxes of 40 x 40 cells it took the correlation of the season's value with the season's mean day
    from between -0.69 and -0.86 to between -0.45 and +0.12, cut the year-to-year scatter by 9 to 37 per cent, and a
    quadratic or a proportional rate did no better.
  THE STORED VALUES ARE CHECKED AT EVERY RUN: at 4,000 random pixels the script reads every stored pass and redoes the
    whole standardisation in numpy (standardise_local below); the stored std_<season>, g, h, passes and mean day must
    agree, or nothing is written. At the first 400 of them Earth Engine's own slopes, S, n and contrasts, for both
    yearly values, must equal the ones recomputed here from the stored yearly values.

THE FOUR DECISIONS, AND WHY.
1. SENSOR AND YEARS: Landsat 8 alone, the thirteen seasons 2013 to 2025. One instrument, one surface-reflectance
   algorithm and one orbit. That is how the Landsat 7 scan-line gap and the 2013 change of sensor are handled: by
   not crossing them.
     - Landsat 7 has lost 22 per cent of every scene since May 2003, drifted off its orbit from 2017, and its near-
       infrared band is a different width from Landsat 8's; its surface reflectance comes from a different
       algorithm. The published coefficients for bringing the two together were fitted to pre-Collection data over
       the United States. A series that crosses 2013 carries a step exactly where a trend test would see it.
     - Landsat 5 has whole months missing over Odisha in many years.
     - Landsat 9 is left out so that every season is sampled the same way; it would double the observations
       from 2021 on.
   The cost is stated: nothing before 2013 is seen.
2. WINDOW: 1 November to 31 December, a season being named for the year of its November, with every pass
   standardised to 1 December as above. The window starts after the monsoon has withdrawn (normal date 12 October)
   and after October's cloud and cyclones, and ends before most species shed their leaves in January; it lies
   inside the season the Forest Survey of India uses. A fixed window is NOT by itself a consistent point in the
   season - that was the first design's mistake - which is why the date is standardised.
3. WHAT COUNTS AS DECLINING: a significance test, and no slope threshold. A pixel is DECLINING if its Mann-Kendall
   statistic S is at or below minus the exact critical value for a two-sided test at 5 per cent, for the number of
   seasons that pixel has; INCREASING is the mirror image. The same test at the same level defines the "Degrading"
   class of the trend metric in the UN Convention to Combat Desertification's good-practice guidance for SDG
   indicator 15.3.1 - which also says that a trend alone is not sufficient to call land degraded. No magnitude
   threshold is used because none has a precedent that fits; the slope as a share of the land's mean NIRv is reported
   so that size can be read.
4. THE TREND ITSELF: the Theil-Sen slope (ee.Reducer.sensSlope) of the yearly value on the year: the median of the
   slopes between every pair of seasons that have a value (the mean of the two middle ones when their number is
   even). A pixel has a trend only if at least 10 of its 13 seasons have a value.

THE TEST, EXACTLY. S is the number of pairs of seasons in which the later value is higher, minus the number in
which it is lower (equal values count for neither). Under no trend, with n values and no ties, S has a known
exact distribution; the script computes it by counting and reads the critical values from it - 34 for n = 13,
30 for 12, 27 for 11, 23 for 10 at two-sided 5 per cent, each reached with probability 2.0 to 2.3 per cent in one
direction - and checks its distribution against the table the US Environmental Protection Agency prints. No normal
approximation is used.
WHAT THE TEST DOES NOT DO.
  - It treats years as independent and pixels one at a time. A wet or dry year moves a whole region at once, so the
    pixels flagged by chance come in bursts: about 2 per cent each way is the AVERAGE over orderings of the seasons,
    not what any one ordering gives - most orderings flag less, a few flag many times more. The false-alarm rate is
    therefore MEASURED here, by re-ordering the seasons (see THE NULL).
  - It seldom flags a recent clearance: a clean, permanent step after the 2022, 2023 or 2024 season leaves S at
    -30, -22 or -12 against a critical 34 if the values on each side are tied, and is flagged with probability
    0.40, 0.20 or 0.08 if they are not (0.85 for a step in the middle). The same at the start, 2013 to 2015.
  - A declining NIRv is a fall in green canopy as seen around 1 December. It is not by itself degradation: a change
    of crop, a plantation felled on schedule, or a run of dry years does the same.

PER UNIT. Land is split by year-2000 canopy exactly as in 02_build_hansen.py: le10 (treecover2000 <= 10),
gt10le30 (10 < treecover2000 <= 30), gt30 (treecover2000 > 30). From the DATE-STANDARDISED values:
  nirv_declining_ha   area of declining pixels on land with treecover2000 > 10 (gt10le30 and gt30 together):
                      land that had tree canopy in 2000 by the Forest Survey's own floor. Below that floor most
                      land in lgd_panchayat units is cropland; nirv_by_unit_bands.csv carries it separately.
  nirv_increasing_ha  the same for increasing pixels: never read the declining area without it
  nirv_slope          the area-weighted mean Theil-Sen slope over the same land, in NIRv per year. As a share of
                      the land's NIRv (the area-weighted mean of its pixels' thirteen-season medians) it is in
                      nirv_by_unit_bands.csv: a ratio of two means, not a mean of per-pixel ratios, which a few
                      pixels with NIRv near zero (water, sand) would dominate
  nirv_trend_ha       the land the three rest on: treecover2000 > 10 with at least 10 seasons
  missing_data_share  land with treecover2000 > 10 and no trend (fewer than 10 seasons, or no rate), over all land
                      with treecover2000 > 10. In practice it is zero or nearly so and says nothing about how thin
                      a season is: the share of seasons resting on a single pass is in nirv_rates.csv
and the same four from the first design: nirv_slope_unadjusted, nirv_declining_ha_unadjusted,
nirv_increasing_ha_unadjusted, nirv_trend_ha_unadjusted.
Areas are sums of (the grid cell's area on the WGS84 ellipsoid x the fraction of the cell inside the unit), as
for Hansen.

THE BEFORE-AND-AFTER CONTRAST, for setting NIRv beside the CoRE Stack product, which compares a state around
2016-19 with a state around 2022-25. A pixel is LOWER if every one of the seasons 2022, 2023 and 2024 is below
every one of the seasons 2016, 2017 and 2018, and HIGHER in the mirror case; it needs all six seasons. If the six
values were in random order each would happen once in twenty. Its size, for a unit or any other piece of land, is
the change from the earlier period to the later as a share of the earlier: each pixel's period value is the median
of its three seasons, and the land's is the area-weighted mean of its pixels' (pixels with all six seasons).
A trend test over the seven seasons 2017-2023 is carried beside it and is not the measure: a clean, permanent step
in the middle of seven seasons gives S = -12 if the values on each side are tied and reaches the critical 15 with
probability 0.29 if they are not, so over seven seasons the trend test seldom sees an outright clearance.

SEASON BY SEASON. For each unit and season, the mean of the yearly value (weighted as the areas are) over three
classes of land with tree canopy: gt10le30; reference = treecover2000 > 50 and no Hansen loss in any year
2001-2025; and gt30_other = treecover2000 > 30 that is not reference. Each mean is over the pixels that have a
value that season. Beside it, mean_day_gt10: the mean, over the unit's land with treecover2000 > 10 that was seen
that season, of the mean day of each pixel's passes (each pass once; not the day of the median scene).
  - A unit's SERIES is the mean over the three classes together (all its land with treecover2000 > 10), for the
    seasons in which at least half of that land has a value. Its trend is the same Theil-Sen slope and the same
    exact test, applied to the series; at least 10 seasons.
  - The RELATIVE series divides it, season by season, by the mean of ALL reference forest in the layer that
    season. Whatever undisturbed forest shares - a wet year, a late monsoon - cancels. A decline in the relative
    series is canopy falling behind undisturbed forest.

THE NULL: THE FALSE-ALARM RATE, MEASURED. The thirteen seasons are put in a random order, the same order
for every pixel (or unit), and the test is run again; 2,000 times. That keeps everything that makes neighbouring
pixels move together and destroys only the order in time. If the area flagged declining in the real order is
no larger than re-ordered seasons usually give, it cannot be told from chance. Done for the sampled pixels
(as they are and relative) and for the units' series. For the before-and-after contrast the same question has an
exact answer: the six seasons can be split three and three in twenty ways, of which the real one is one; the
contrast is recomputed for all twenty.

THE DATE CHECK. If the standardisation has done its work, a unit's series should no longer follow the mean day
its land was seen on. nirv_date_check.csv gives, for both yearly values: over units (and over sampled pixels), the
correlation across seasons between a series and its mean day; the year-to-year scatter of a series - the standard
deviation, with divisor n, of its distance from its own Theil-Sen line drawn through its median, as a share of that
median (series with a median above zero); across units, the rank correlation between S of the series and S of
its mean day (do the units whose scenes drifted later show more decline?); and, from the sampled pixels, the rates
g and h themselves. A group's own mean series is weighted by the units' land with treecover2000 > 10.

THE RATE AND THE SINGLE PASS. nirv_rate_sensitivity.csv, from the sampled pixels' stored passes, refitted here in
double precision (at a factor of 1 it is the stored value before rounding to 32 bits): every pixel's rate g multiplied by
0, 0.8, 0.9, 1, 1.1 and 1.2 (0 leaves the date as it fell; the path step is kept), with the declining and
increasing shares, the correlation with the day and the scatter at each; and what happens to the flags when one
pass, drawn at random, is taken away from every pixel and everything is fitted again.

HOW A RUN GOES. (1) The records of the two exports are read and must fit the scripts as they now are. (2) Two batch
tasks read the sample pixels - every stored band at 4,000, Earth Engine's trends at the first 400 - and the check
described above is made; a failure stops the run before anything is summed. (3) One batch task per group of units and
yearly value sums the bands. (4) The tables are checked and written, then the record, and only then are the
intermediate tables in Earth Engine deleted. Those tables carry in their names a fingerprint of what they hold (the
image's whole expression, the bands, the grouping, the layer, the scene list, both export recipes), so a run that is
started again takes up its own tables and never another computation's; the record says how many it took up.

Needs earthengine-api, geopandas, shapely, pyproj, pandas, numpy; scripts/_ee_units.py, 02_export_nirv_yearly.py and
through it 02_export_nirv_observations.py.
"""
import argparse, hashlib, importlib.util, json, math, sys, time, warnings
from pathlib import Path

import ee
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ee_units as eu
from _ee_units import OUT, ROOT, fail, now, sha256, stop_if_failed


def load(name):
    """A sibling script as a module: its definitions are used here, not copied."""
    spec = importlib.util.spec_from_file_location(name[:-3].replace("02_", ""), Path(__file__).with_name(name))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


YEARLY = load("02_export_nirv_yearly.py")
OBS = YEARLY.OBS
LANDSAT, HANSEN, GRID = OBS.LANDSAT, OBS.HANSEN, OBS.GRID
SEASONS = {"full": list(OBS.ALL_SEASONS), "common": list(range(2017, 2024))}
MIN_SEASONS = {"full": 10, "common": 6}
ALL_SEASONS = SEASONS["full"]
PASSES = YEARLY.PASSES                         # the eight possible passes of a season, in band order
EPOCH_EARLY, EPOCH_LATE = (2016, 2017, 2018), (2022, 2023, 2024)
STANDARD_DAY, SDD_MIN, SQQ_MIN = YEARLY.STANDARD_DAY, YEARLY.SDD_MIN, YEARLY.SQQ_MIN       # as the stored values were made
SERIES = {"std": "date-standardised", "raw": "first design"}
ALPHA_TWO_SIDED = 0.05                         # declining / increasing
CANOPY = {"le10": "treecover2000 <= 10", "gt10le30": "10 < treecover2000 <= 30", "gt30": "treecover2000 > 30"}
TREE = ("gt10le30", "gt30")                    # land with treecover2000 > 10: what nirv_slope and nirv_declining_ha rest on
CLASSES = {"gt10le30": "10 < treecover2000 <= 30", "gt30_other": "treecover2000 > 30, not reference",
           "reference": "treecover2000 > 50 and no Hansen loss in any year 2001-2025"}
SERIES_MIN_SHARE = 0.5                         # a season counts in a unit's series if this share of its treecover2000 > 10 land has a value
SUMMARY_MIN_HA = 50.0                          # the count of units with a declining series is given for units with at least this much such land
SAMPLE_POINTS = 4000                           # random pixels at which every stored band is read
CHECK_POINTS = 400                             # the first of them, at which Earth Engine's own trends and contrasts are read as well
SAMPLE_SEED = 20261006
PERMUTATIONS = 2000
PERMUTATION_SEED = 20261007
GROUPS = 8
TILE_SCALE = 4
# US EPA (2000), Guidance for Data Quality Assessment, EPA QA/G-9, Table A-11: P(S >= s) with n values, no ties
EPA_TABLE = {(4, 6): 0.042, (5, 8): 0.042, (5, 10): 0.0083, (7, 13): 0.035, (7, 15): 0.015, (8, 16): 0.031, (8, 18): 0.016,
             (9, 18): 0.038, (9, 20): 0.022, (10, 21): 0.036, (10, 23): 0.023}


# ---- the exact Mann-Kendall distribution ---------------------------------------------------------------------------
def inversions(n):
    """c[k] = number of orderings of n distinct values with k inversions; then S = n(n-1)/2 - 2k."""
    c = [1]
    for k in range(2, n + 1):
        new = [0] * (len(c) + k - 1)
        for i, v in enumerate(c):
            for j in range(k):
                new[i + j] += v
        c = new
    return c


def upper_tail(n, s):
    """P(S >= s) under no trend, n values, no ties."""
    c, most = inversions(n), n * (n - 1) // 2
    return sum(v for k, v in enumerate(c) if most - 2 * k >= s) / math.factorial(n)


def critical(n, alpha_one_tail):
    """Smallest s with P(S >= s) <= alpha_one_tail, or None if even a perfect run does not reach it."""
    most = n * (n - 1) // 2
    for s in range(most % 2, most + 1, 2):
        if upper_tail(n, s) <= alpha_one_tail:
            return s
    return None


def critical_table(seasons, need):
    """{n: the critical S for 'declining' (and, mirrored, 'increasing'), and how often it is reached under no trend}."""
    rows = {}
    for n in range(need, len(seasons) + 1):
        two = critical(n, ALPHA_TWO_SIDED / 2)
        rows[n] = {"declining_S": two, "declining_size": None if two is None else upper_tail(n, two)}
    return rows


# ---- Earth Engine images -------------------------------------------------------------------------------------------
def load_records(obs_collection, std_collection):
    """The scene list and the records of the two exports, each checked against the script that wrote it as it now is."""
    scenes, obs_prov = YEARLY.load_scenes(obs_collection)
    record = OUT / "nirv_yearly.provenance.json"
    if not record.exists():
        sys.exit(f"{record.relative_to(ROOT)} is missing: run scripts/02_export_nirv_yearly.py first")
    prov = json.load(open(record))
    stored = prov["outputs_in_earth_engine"]
    if stored["recipe_sha256"] != YEARLY.RECIPE_SHA256 or YEARLY.recipe() != YEARLY.RECIPE_SHA256:
        fail("the stored yearly values were not made by 02_export_nirv_yearly.py as it now is")
    if stored["image_collection"] != std_collection:
        fail(f"the yearly values' record is for {stored['image_collection']}, not {std_collection}")
    if sha256(OUT / "nirv_scenes.csv") not in [i.get("sha256") for i in prov["inputs"]]:
        fail("the stored yearly values were made from a different scene list")
    for record_of, name in ((obs_prov, "nirv_observations.provenance.json"), (prov, "nirv_yearly.provenance.json")):
        record_of["_read_from"] = {"path": f"20_degradation/{name}", "sha256": sha256(OUT / name)}
    return scenes, obs_prov, prov


def fingerprint(*parts):
    """Ten hex digits that change whenever what is computed changes: an image's whole expression, or any text given.
    They go into the names of the intermediate tables in Earth Engine, so that a table left behind by other code, other
    stored values or another layer is never taken for this run's (the helper reuses a table on row count and column names)."""
    return hashlib.sha256("\n".join(x if isinstance(x, str) else x.serialize() for x in parts).encode()).hexdigest()[:10]


def stored_images(obs_collection, std_collection):
    """The two stored assets as images: the observations and the yearly values."""
    return ee.ImageCollection(obs_collection).mosaic(), ee.ImageCollection(std_collection).mosaic()


def first_design(obs):
    """{season: the first design's yearly image}: the stored median of the season's kept scenes."""
    return {y: obs.select(f"nirv_{y}").rename("nirv") for y in ALL_SEASONS}


def stored_standardised(yearly):
    """{season: the stored date-standardised yearly image}, and what the other stored bands say about it."""
    annual = {y: yearly.select(f"std_{y}").rename("nirv") for y in ALL_SEASONS}
    g = yearly.select("g")
    return annual, {"g": g, "h": yearly.select("h"), "has_rate": g.mask().gt(0).unmask(0), "two": yearly.select("two").unmask(0),
                    "passes": {y: yearly.select(f"passes_{y}").unmask(0) for y in ALL_SEASONS}, "mday": {y: yearly.select(f"day_{y}") for y in ALL_SEASONS}}


def pixel_image(annual):
    """Per pixel, from a set of yearly images: slope, S, n and median over 2013-2025; S_c, n_c over 2017-2023; and the
    before-and-after contrast e_valid, e_lower, e_higher (0/1) with e_early, e_late, the medians of the two periods
    (masked unless all six seasons have a value)."""
    bands = trend_bands(annual, SEASONS["full"], "")
    bands.append(ee.ImageCollection([annual[y] for y in SEASONS["full"]]).median().toFloat().rename("median"))
    bands += trend_bands(annual, SEASONS["common"], "_c", with_slope=False)
    early, late = ee.ImageCollection([annual[y] for y in EPOCH_EARLY]), ee.ImageCollection([annual[y] for y in EPOCH_LATE])
    valid = ee.ImageCollection([annual[y] for y in EPOCH_EARLY + EPOCH_LATE]).count().unmask(0).eq(len(EPOCH_EARLY) + len(EPOCH_LATE))
    lower = valid.And(late.max().lt(early.min()).unmask(0))
    higher = valid.And(late.min().gt(early.max()).unmask(0))
    bands += [valid.toInt8().rename("e_valid"), lower.toInt8().rename("e_lower"), higher.toInt8().rename("e_higher"),
              early.median().updateMask(valid).toFloat().rename("e_early"), late.median().updateMask(valid).toFloat().rename("e_late")]
    return ee.Image.cat(bands)


def unit_bands(px, annual, tables, extra=()):
    """Square metres (and area-weighted sums) per unit: the image and its band names in order. `extra` is [(name, image)]
    of further bands, already in square metres or area-weighted."""
    area = ee.Image.pixelArea()
    in_band, in_class, _, _ = canopy_images()
    tier = flags(px, tables)
    slope, median = px.select("slope").unmask(0), px.select("median")
    e_valid, e_lower, e_higher = px.select("e_valid").unmask(0), px.select("e_lower").unmask(0), px.select("e_higher").unmask(0)
    e_early, e_late = px.select("e_early").unmask(0), px.select("e_late").unmask(0)
    named = [("area_m2", area)]
    for b, cond in in_band.items():
        named.append((f"land_{b}_m2", area.multiply(cond)))
    named.append(("land_reference_m2", area.multiply(in_class["reference"])))
    for b, cond in in_band.items():
        for t in ("trend", "declining", "increasing", "negative"):
            named.append((f"full_{b}_{t}_m2", area.multiply(cond.And(tier["full"][t]))))
        named.append((f"full_{b}_slopesum", area.multiply(cond.And(tier["full"]["trend"])).multiply(slope)))
        named.append((f"full_{b}_mediansum", area.multiply(cond.And(tier["full"]["trend"])).multiply(median.unmask(0))))
        for t in ("trend", "declining", "increasing"):
            named.append((f"common_{b}_{t}_m2", area.multiply(cond.And(tier["common"][t]))))
        named.append((f"epoch_{b}_valid_m2", area.multiply(cond.And(e_valid))))
        named.append((f"epoch_{b}_lower_m2", area.multiply(cond.And(e_lower))))
        named.append((f"epoch_{b}_higher_m2", area.multiply(cond.And(e_higher))))
        named.append((f"epoch_{b}_earlysum", area.multiply(cond.And(e_valid)).multiply(e_early)))
        named.append((f"epoch_{b}_latesum", area.multiply(cond.And(e_valid)).multiply(e_late)))
    for c, cond in in_class.items():
        for y in ALL_SEASONS:
            named.append((f"season_{c}_{y}_sum", area.multiply(cond).multiply(annual[y].unmask(0))))
            named.append((f"season_{c}_{y}_m2", area.multiply(cond.And(annual[y].mask().gt(0).unmask(0)))))
    named += list(extra)
    names = [n for n, _ in named]
    return ee.Image.cat([im.rename(n) for n, im in named]), names


def extra_bands_raw(model):
    """With the first design's sums: the mean day the land with treecover2000 > 10 was seen on, season by season, and how
    much of each canopy band rests on a single pass in a season."""
    area = ee.Image.pixelArea()
    in_band, _, _, _ = canopy_images()
    tree = in_band["gt10le30"].Or(in_band["gt30"])
    named = []
    for y in ALL_SEASONS:
        seen = model["passes"][y].gte(1)
        named.append((f"day_{y}_sum", area.multiply(tree.And(seen)).multiply(model["mday"][y].unmask(0))))
        named.append((f"day_{y}_m2", area.multiply(tree.And(seen))))
    single = ee.Image.constant(0)
    for y in ALL_SEASONS:
        single = single.add(model["passes"][y].eq(1))
    for b, cond in in_band.items():
        named.append((f"single_{b}_m2x", area.multiply(cond).multiply(single)))            # square metres x seasons
    return named


def extra_bands_std(model, px, tables):
    """With the standardised sums: how much land has a rate, how much a path step, and the rate itself."""
    area = ee.Image.pixelArea()
    in_band, _, _, _ = canopy_images()
    trend = flags(px, tables)["full"]["trend"]
    named = []
    for b, cond in in_band.items():
        named.append((f"rate_{b}_m2", area.multiply(cond.And(model["has_rate"]))))
        named.append((f"twopath_{b}_m2", area.multiply(cond.And(model["two"]))))
        named.append((f"full_{b}_ratesum", area.multiply(cond.And(trend)).multiply(model["g"].unmask(0))))
    return named


# ---- the pixel sample ------------------------------------------------------------------------------------------------
PIXEL_BANDS = ("slope", "S", "n", "median", "S_c", "n_c", "e_valid", "e_lower", "e_higher", "e_early", "e_late")


def stored_columns():
    return OBS.band_names() + YEARLY.band_names() + ["treecover2000", "lossyear"]


def check_columns():
    return [f"{s}_{b}" for s in SERIES for b in PIXEL_BANDS]


def stored_point_image(obs, yearly):
    """Every stored band, as doubles with a stand-in where a band has no value: -9 for NIRv and days, -9999 for rates, 0 for counts."""
    _, _, cover, lossyear = canopy_images()
    names = OBS.band_names()
    values = [n for n in names if n.startswith(("o_", "nirv_"))]
    return ee.Image.cat([obs.select(values).unmask(-9).toDouble(), obs.select([n for n in names if n not in values]).unmask(0).toDouble(),
                         yearly.select([f"std_{y}" for y in ALL_SEASONS] + [f"day_{y}" for y in ALL_SEASONS]).unmask(-9).toDouble(),
                         yearly.select([f"passes_{y}" for y in ALL_SEASONS] + ["two", "sdd", "sqq", "qbar"]).unmask(0).toDouble(), yearly.select(["g", "h"]).unmask(-9999).toDouble(),
                         cover.rename("treecover2000").toDouble(), lossyear.rename("lossyear").toDouble()]).select(stored_columns())


def check_point_image(px):
    """Earth Engine's own trends and contrasts for both yearly values, -9999 where a band has no value."""
    return ee.Image.cat([px[s].select(list(PIXEL_BANDS)).toDouble().unmask(-9999).rename([f"{s}_{b}" for b in PIXEL_BANDS]) for s in SERIES])


def start_points(pts, image, columns, asset_id, description):
    """Start (or find) a batch task that reads an image at sample points. Returns the task, or None if its table is already there."""
    if eu.exists(asset_id):
        fc = ee.FeatureCollection(asset_id)
        if fc.size().getInfo() == len(pts) and set(columns) <= set(fc.first().propertyNames().getInfo()):
            print(f"  {description}: already read ({len(pts):,} points)")
            return None
        ee.data.deleteAsset(asset_id)
    if eu.unfinished(description):
        sys.exit(f"Earth Engine is still running {description}: wait for it")
    fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([p.x, p.y]), {"i": int(i)}) for i, p in zip(pts.index, pts.geometry)])
    got = image.reduceRegions(collection=fc, reducer=ee.Reducer.first(), crs=GRID["crs"], crsTransform=GRID["transform"], tileScale=16)
    task = ee.batch.Export.table.toAsset(collection=got, description=description, assetId=asset_id)
    task.start()
    print(f"  {description}: task started for {len(pts):,} points", flush=True)
    return task


def read_points(asset_id, columns, at_a_time=60):
    """A point table as a DataFrame, read in slices of columns and joined on the point's number: a page of 2,000 rows by
    180 columns would be several megabytes, near the size of response Earth Engine allows."""
    fc, out = ee.FeatureCollection(asset_id), None
    for k in range(0, len(columns), at_a_time):
        part = eu.table(fc, ["i"] + columns[k:k + at_a_time])
        if part["i"].duplicated().any():
            fail(f"{asset_id.split('/')[-1]}: a point came back twice")
        out = part if out is None else out.merge(part, on="i", validate="one_to_one")
    return out


def trend_bands(annual, seasons, suffix, with_slope=True):
    """S and n over the given seasons, and the Theil-Sen slope if asked. S and n are 0 where there is nothing; the slope is masked where it cannot be fitted."""
    images = [annual[y] for y in seasons]
    n = ee.ImageCollection(images).count().unmask(0)
    s = ee.Image.constant(0)
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            s = s.add(images[j].subtract(images[i]).signum().unmask(0))
    out = [s.toInt8().rename(f"S{suffix}"), n.toInt8().rename(f"n{suffix}")]
    if with_slope:
        stack = ee.ImageCollection([images[i].addBands(ee.Image.constant(y).toFloat().rename("t")).select(["t", "nirv"]) for i, y in enumerate(seasons)])
        out.insert(0, stack.reduce(ee.Reducer.sensSlope()).select("slope").toFloat().rename(f"slope{suffix}"))
    return out


def flags(px, tables):
    """0/1 images from pixel_image(): which pixels have a trend and which are declining, increasing, of negative slope,
    over 2013-2025 ("full") and over 2017-2023 ("common", no slope). `tables` is {window: critical_table(...)}."""
    out = {}
    for window, suffix in (("full", ""), ("common", "_c")):
        table, need = tables[window], MIN_SEASONS[window]
        n, s = px.select(f"n{suffix}").unmask(0), px.select(f"S{suffix}").unmask(0)
        has = n.gte(need)
        if window == "full":
            has = has.And(px.select("slope").mask().gt(0).unmask(0))
        ns = sorted(table)
        crit = n.remap(ns, [table[k]["declining_S"] if table[k]["declining_S"] is not None else 9999 for k in ns], 9999)
        out[window] = {"trend": has, "declining": has.And(s.lte(crit.multiply(-1))), "increasing": has.And(s.gte(crit))}
    out["full"]["negative"] = out["full"]["trend"].And(px.select("slope").unmask(0).lt(0))
    return out


def canopy_images():
    """0/1 images of the canopy bands and of the classes of land with tree canopy."""
    hansen = ee.Image(HANSEN)
    cover, lossyear = hansen.select("treecover2000").unmask(0), hansen.select("lossyear").unmask(0)
    in_band = {"le10": cover.lte(10), "gt10le30": cover.gt(10).And(cover.lte(30)), "gt30": cover.gt(30)}
    reference = cover.gt(50).And(lossyear.eq(0))
    in_class = {"gt10le30": in_band["gt10le30"], "gt30_other": cover.gt(30).And(reference.Not()), "reference": reference}
    return in_band, in_class, cover, lossyear


# ---- the local side: the same arithmetic in numpy ------------------------------------------------------------------
def sample_points(g, n, seed):
    """n points drawn uniformly over the layer's bounding box and kept if inside a unit, with the unit they fall in."""
    rng = np.random.default_rng(seed)
    w, s, e, nn = g.total_bounds
    pts = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in zip(rng.uniform(w, e, n * 4), rng.uniform(s, nn, n * 4))], crs="EPSG:4326")
    j = gpd.sjoin(pts, g[["unit_id", "unit_level", "geometry"]], predicate="within", how="inner")
    j = j[~j.index.duplicated()].sort_index().iloc[:n].reset_index(drop=True)
    if len(j) < n:
        fail(f"only {len(j):,} of the {n:,} sample points wanted fell inside a unit")
    return j


def pairs(k):
    i, j = np.triu_indices(k, 1)
    return i, j


def mk_S(v):
    """S for each row of v (seasons in columns, NaN where a season has no value)."""
    i, j = pairs(v.shape[1])
    return np.nan_to_num(np.sign(v[:, j] - v[:, i])).sum(axis=1).astype(int)


def sen_slope(v, years):
    """Theil-Sen slope for each row: the median of the slopes over every pair of seasons that both have a value."""
    i, j = pairs(v.shape[1])
    t = np.asarray(years, float)
    with np.errstate(invalid="ignore"), __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore", RuntimeWarning)          # rows with no pair at all: all-NaN, median is NaN
        return np.nanmedian((v[:, j] - v[:, i]) / (t[j] - t[i]), axis=1)


def critical_array(table, most):
    """crit[n] for n = 0..most: the declining critical S, or a value no S can reach where there is no test."""
    crit = np.full(most + 1, 10 ** 6)
    for n, r in table.items():
        if r["declining_S"] is not None:
            crit[n] = r["declining_S"]
    return crit


def test_rows(v, table, need):
    """(S, n, declining, increasing) for each row, by the same rule as the image."""
    s, n = mk_S(v), (~np.isnan(v)).sum(axis=1)
    crit = critical_array(table, v.shape[1])[n]
    ok = n >= need
    return s, n, ok & (s <= -crit), ok & (s >= crit)


def contrast(v, early, late):
    """The before-and-after contrast for each row of v (seasons ALL_SEASONS in columns): valid, lower, higher, and the two period medians."""
    import warnings
    e, l = v[:, [ALL_SEASONS.index(y) for y in early]], v[:, [ALL_SEASONS.index(y) for y in late]]
    valid = ~(np.isnan(e).any(axis=1) | np.isnan(l).any(axis=1))
    with np.errstate(invalid="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        lower, higher = valid & (np.nanmax(l, axis=1) < np.nanmin(e, axis=1)), valid & (np.nanmin(l, axis=1) > np.nanmax(e, axis=1))
        return valid, lower, higher, np.where(valid, np.nanmedian(e, axis=1), np.nan), np.where(valid, np.nanmedian(l, axis=1), np.nan)


def contrast_null_rows(what, basis, v, groups):
    """Rows for nirv_null.csv: the share of rows that are lower (higher) in the real split of the six seasons, beside the
    same share under each of the twenty ways of splitting them three and three (the real split is one of the twenty)."""
    import itertools
    six = list(EPOCH_EARLY + EPOCH_LATE)
    splits = [(list(c), [y for y in six if y not in c]) for c in itertools.combinations(six, 3)]
    valid, lower, higher, _, _ = contrast(v, list(EPOCH_EARLY), list(EPOCH_LATE))
    by_split = [contrast(v, a, b)[1] for a, b in splits]                      # "lower" under each split; "higher" under a split is "lower" under its mirror
    rows = []
    for g, sel in groups.items():
        tested = int(valid[sel].sum())
        draws = np.array([int(x[sel].sum()) for x in by_split])
        for direction, flag in (("lower", lower), ("higher", higher)):
            obs = int(flag[sel].sum())
            q = np.percentile(draws, [5, 50, 95])
            rows.append({"what": what, "basis": basis, "group": g, "direction": direction, "n_tested": tested, "observed": obs, "observed_pct": round(100 * obs / tested, 3) if tested else None,
                         "nominal_pct_under_no_trend": 5.0, "reordered_p05_pct": round(100 * q[0] / tested, 3) if tested else None, "reordered_median_pct": round(100 * q[1] / tested, 3) if tested else None,
                         "reordered_p95_pct": round(100 * q[2] / tested, 3) if tested else None, "share_of_reorderings_at_or_above_observed": round(float((draws >= obs).mean()), 4), "reorderings": len(splits)})
    return rows


def permutation_null(v, table, need, groups, k, seed):
    """Re-order the seasons k times, the same order for every row, and count the rows flagged in each group.
    Returns {group: {"declining": counts over the k orders, "increasing": ...}}."""
    rng = np.random.default_rng(seed)
    out = {g: {"declining": np.zeros(k, int), "increasing": np.zeros(k, int)} for g in groups}
    for r in range(k):
        _, _, dec, inc = test_rows(v[:, rng.permutation(v.shape[1])], table, need)
        for g, sel in groups.items():
            out[g]["declining"][r], out[g]["increasing"][r] = int(dec[sel].sum()), int(inc[sel].sum())
    return out


def null_rows(what, basis, v, table, need, groups, k, seed):
    """Rows for nirv_null.csv: observed counts beside what k re-orderings of the seasons give."""
    _, n, dec, inc = test_rows(v, table, need)
    null = permutation_null(v, table, need, groups, k, seed)
    rows = []
    for g, sel in groups.items():
        tested = int((n[sel] >= need).sum())
        for direction, flag in (("declining", dec), ("increasing", inc)):
            obs, draws = int(flag[sel].sum()), null[g][direction]
            q = np.percentile(draws, [5, 50, 95])
            rows.append({"what": what, "basis": basis, "group": g, "direction": direction, "n_tested": tested, "observed": obs,
                         "observed_pct": round(100 * obs / tested, 3) if tested else None,
                         "nominal_pct_under_no_trend": round(100 * float(np.mean([table[int(x)]["declining_size"] for x in n[sel] if x >= need])), 3) if tested else None,
                         "reordered_p05_pct": round(100 * q[0] / tested, 3) if tested else None, "reordered_median_pct": round(100 * q[1] / tested, 3) if tested else None,
                         "reordered_p95_pct": round(100 * q[2] / tested, 3) if tested else None,
                         "share_of_reorderings_at_or_above_observed": round(float((draws >= obs).mean()), 4), "reorderings": k})
    return rows


def sample_arrays(sample):
    """From the sample table: the passes as an array [points, seasons, 8] (NaN where there is none), and the two path bands."""
    obs = np.stack([np.stack([sample[f"o_{y}_{k}{p}"].to_numpy(float) for k, p in PASSES], axis=1) for y in ALL_SEASONS], axis=1)
    return np.where(obs < -8, np.nan, obs), sample["path_e"].to_numpy().astype(int), sample["path_o"].to_numpy().astype(int)


def standardise_local(obs, path_e, path_o, days, rate_scale=1.0):
    """The date standardisation of the docstring, in numpy. obs is [cells, seasons, 8] in PASSES order.
    Returns {"std": [cells, seasons], "g", "h", "sdd", "sqq", "qbar", "two", "mday": [cells, seasons], "passes": [cells, seasons]}.
    rate_scale multiplies every cell's fitted rate before the passes are moved (1 in the pipeline; other values for the sensitivity table)."""
    cells = obs.shape[0]
    D = np.full(obs.shape, np.nan)
    for i, y in enumerate(ALL_SEASONS):
        for j, (k, par) in enumerate(PASSES):
            path = path_o if par == "o" else path_e
            for wp, day in days.get((y, k, par), {}).items():
                D[path == wp, i, j] = day
    V = np.where(np.isnan(D), np.nan, obs.astype(float))                    # a value with no day is not a pass
    D = np.where(np.isnan(V), np.nan, D)
    Q = np.where(np.isnan(V), np.nan, np.array([1.0 if par == "o" else 0.0 for _, par in PASSES])[None, None, :])
    n = (~np.isnan(V)).sum(axis=2)

    def centred(a, b):
        return (np.nansum(a * b, axis=2) - np.nansum(a, axis=2) * np.nansum(b, axis=2) / np.maximum(n, 1)).sum(axis=1)

    sdd, sdq, sdv, sqv = centred(D, D), centred(D, Q), centred(D, V), centred(Q, V)
    # Sqq is compared with a whole number (4), and real pass patterns hit it exactly: it is formed here in the order the
    # export forms it (q - q x q x (1 / n), added season by season), so that both sides round the same way
    odd, inv = np.nansum(Q, axis=2), 1.0 / np.maximum(n, 1)
    sqq = np.zeros(cells)
    for i in range(obs.shape[1]):
        sqq = sqq + (odd[:, i] - odd[:, i] * odd[:, i] * inv[:, i])
    det = sdd * sqq - sdq ** 2
    has, two = sdd >= SDD_MIN, (sqq >= SQQ_MIN) & (det > 1e-6 * sdd * sqq)
    safe = np.maximum(det, 1e-9)
    g = np.where(two, (sdv * sqq - sqv * sdq) / safe, sdv / np.maximum(sdd, 1e-9))
    h = np.where(two, (sqv * sdd - sdv * sdq) / safe, 0.0)
    g, h = np.where(has, g, np.nan), np.where(has, h, np.nan)
    qbar = np.nansum(Q, axis=(1, 2)) / np.maximum(n.sum(axis=1), 1)
    moved = V - rate_scale * g[:, None, None] * (D - STANDARD_DAY) - h[:, None, None] * (Q - qbar[:, None, None])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)                    # a season with no pass: all-NaN, the median is NaN
        std = np.nanmedian(moved, axis=2)
    mday = np.where(n > 0, np.nansum(D, axis=2) / np.maximum(n, 1), np.nan)
    return {"std": std, "g": g, "h": h, "sdd": sdd, "sqq": sqq, "qbar": qbar, "two": two & has, "mday": mday, "passes": n}


def scatter_and_date(series, mday):
    """For each row: the correlation over seasons of its yearly value with the mean day it was seen on, and the scatter
    of the yearly value about its own Theil-Sen line as a share of its median (rows with at least ten seasons)."""
    years = np.asarray(ALL_SEASONS, float)[None, :]
    ok = ~np.isnan(series) & ~np.isnan(mday)
    enough = ok.sum(axis=1) >= MIN_SEASONS["full"]
    a, b = np.where(ok, series, np.nan), np.where(ok, mday, np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        da, db = a - np.nanmean(a, axis=1)[:, None], b - np.nanmean(b, axis=1)[:, None]
        corr = np.nansum(da * db, axis=1) / np.sqrt(np.nansum(da ** 2, axis=1) * np.nansum(db ** 2, axis=1))
        med = np.nanmedian(a, axis=1)
        slope = sen_slope(a, ALL_SEASONS)
        resid = a - (med[:, None] + slope[:, None] * (years - np.nanmedian(np.where(ok, years, np.nan), axis=1)[:, None]))
        scatter = np.nanstd(resid, axis=1) / med
    return np.where(enough, corr, np.nan), np.where(enough & (med > 0), scatter, np.nan)


def date_check_rows(what, groups, series_by, mday, weight=None):
    """Rows for nirv_date_check.csv: for each group and each yearly value, how the rows' values follow the day."""
    rows = []
    for gname, sel in groups.items():
        for s, label in SERIES.items():
            corr, scatter = scatter_and_date(series_by[s][sel], mday[sel])
            tested = ~np.isnan(corr)
            row = {"what": what, "group": gname, "yearly_value": label, "n_tested": int(tested.sum()), "n_in_the_scatter": int((~np.isnan(scatter)).sum())}
            if tested.sum() >= 5:
                s_value, s_day = mk_S(series_by[s][sel][tested]), mk_S(mday[sel][tested])
                if s_value.std() > 0 and s_day.std() > 0:
                    rank = lambda v: pd.Series(v).rank().to_numpy()
                    row["rank_correlation_across_rows_of_S_with_S_of_the_day"] = round(float(np.corrcoef(rank(s_value), rank(s_day))[0, 1]), 3)
            if tested.any():
                row.update({"correlation_with_day_median": round(float(np.nanmedian(corr)), 3), "correlation_with_day_p25": round(float(np.nanpercentile(corr, 25)), 3),
                            "correlation_with_day_p75": round(float(np.nanpercentile(corr, 75)), 3), "share_below_minus_half_pct": round(100 * float((corr[tested] < -0.5).mean()), 1),
                            "scatter_about_own_trend_pct_of_median": round(100 * float(np.nanmedian(scatter)), 2)})
            if weight is not None and sel.any():
                w = np.where(np.isnan(series_by[s][sel]) | np.isnan(mday[sel]), 0.0, weight[sel][:, None])
                with np.errstate(invalid="ignore", divide="ignore"):
                    ms = np.nansum(np.nan_to_num(series_by[s][sel]) * w, axis=0) / w.sum(axis=0)
                    md = np.nansum(np.nan_to_num(mday[sel]) * w, axis=0) / w.sum(axis=0)
                good = ~np.isnan(ms) & ~np.isnan(md)
                row["correlation_of_the_groups_mean_with_its_mean_day"] = round(float(np.corrcoef(ms[good], md[good])[0, 1]), 3) if good.sum() >= 3 else None
            rows.append(row)
    return rows


def rate_sensitivity_rows(obs, path_e, path_o, days, groups, tables, seed):
    """Rows for nirv_rate_sensitivity.csv, from the sampled pixels: the rate scaled, and one pass taken away."""
    table, need = tables["full"], MIN_SEASONS["full"]
    rows, base = [], None
    rank = lambda v: pd.Series(v).rank().to_numpy()
    for k in (0.0, 0.8, 0.9, 1.0, 1.1, 1.2):
        L = standardise_local(obs, path_e, path_o, days, rate_scale=k)
        s, n, dec, inc = test_rows(L["std"], table, need)
        slope = sen_slope(L["std"], ALL_SEASONS)
        corr, scatter = scatter_and_date(L["std"], L["mday"])
        s_day = mk_S(L["mday"])
        if k == 1.0:
            base = (L, s, n, dec, inc)
        for gname, sel in groups.items():
            tested = sel & (n >= need)
            m = int(tested.sum())
            row = {"what": "the rate multiplied by", "value": k, "group": gname, "n_tested": m}
            if m:
                both = tested & (np.std(s[tested]) > 0) & (np.std(s_day[tested]) > 0)
                row.update({"declining_pct": round(100 * float(dec[tested].mean()), 2), "increasing_pct": round(100 * float(inc[tested].mean()), 2),
                            "negative_slope_pct": round(100 * float((slope[tested] < 0).mean()), 2),
                            "correlation_with_day_median": round(float(np.nanmedian(corr[tested])), 3) if (~np.isnan(corr[tested])).any() else None,
                            "scatter_about_own_trend_pct_of_median": round(100 * float(np.nanmedian(scatter[tested])), 2) if (~np.isnan(scatter[tested])).any() else None,
                            "rank_correlation_across_pixels_of_S_with_S_of_the_day": round(float(np.corrcoef(rank(s[both]), rank(s_day[both]))[0, 1]), 3) if both.sum() >= 5 else None})
            rows.append(row)
    L, s, n, dec, inc = base
    rng = np.random.default_rng(seed)
    thinned = obs.copy()
    flat = thinned.reshape(len(obs), -1)
    for i in range(len(flat)):
        have = np.flatnonzero(~np.isnan(flat[i]))
        if len(have) > 1:
            flat[i, rng.choice(have)] = np.nan
    L2 = standardise_local(thinned, path_e, path_o, days)
    s2, n2, dec2, inc2 = test_rows(L2["std"], table, need)
    for gname, sel in groups.items():
        sel = sel & (n >= need)                                           # the pixels tested before the removal: the base of the row at a factor of 1
        m = int(sel.sum())
        row = {"what": "one pass taken away from every pixel", "value": None, "group": gname, "n_tested": m}
        if m:
            row.update({"declining_pct": round(100 * float(dec2[sel].mean()), 2), "increasing_pct": round(100 * float(inc2[sel].mean()), 2),
                        "pixels_whose_S_changed_pct": round(100 * float((s2[sel] != s[sel]).mean()), 2),
                        "declining_flags_before": int(dec[sel].sum()), "declining_flags_kept": int((dec & dec2)[sel].sum()), "declining_flags_new": int((dec2 & ~dec)[sel].sum()),
                        "increasing_flags_before": int(inc[sel].sum()), "increasing_flags_kept": int((inc & inc2)[sel].sum()), "increasing_flags_new": int((inc2 & ~inc)[sel].sum())})
        rows.append(row)
    return rows


# ---- tables from the per-unit sums -----------------------------------------------------------------------------------
def check_sums(m):
    """The arithmetic the sums must obey, whatever the data."""
    tol = 0.01
    if (m[[f"land_{b}_m2" for b in CANOPY]].sum(axis=1) - m["area_m2"]).abs().max() > 1.0:
        fail("the three canopy bands' land does not add up to the unit")
    if (m["land_reference_m2"] > m["land_gt30_m2"] + tol).any():
        fail("reference forest exceeds the land with treecover2000 > 30")
    for b in CANOPY:
        land, t = m[f"land_{b}_m2"], m[f"full_{b}_trend_m2"]
        if (t > land + tol).any() or (m[f"full_{b}_declining_m2"] + m[f"full_{b}_increasing_m2"] > t + tol).any():
            fail(f"full/{b}: land with a trend exceeds the band's land, or declining and increasing together exceed it")
        if (m[f"full_{b}_declining_m2"] > m[f"full_{b}_negative_m2"] + tol).any() or (m[f"full_{b}_negative_m2"] > t + tol).any():
            fail(f"full/{b}: declining pixels that do not have a negative slope, or negative slopes outside the land with a trend")
        c = m[f"common_{b}_trend_m2"]
        if (c > land + tol).any() or (m[f"common_{b}_declining_m2"] + m[f"common_{b}_increasing_m2"] > c + tol).any():
            fail(f"common/{b}: tiers exceed the land with a test, or that exceeds the band's land")
        v = m[f"epoch_{b}_valid_m2"]
        if (v > land + tol).any() or (m[f"epoch_{b}_lower_m2"] + m[f"epoch_{b}_higher_m2"] > v + tol).any():
            fail(f"epoch/{b}: lower and higher together exceed the land with all six seasons, or that exceeds the band's land")
    class_land = {"gt10le30": m["land_gt10le30_m2"], "gt30_other": m["land_gt30_m2"] - m["land_reference_m2"], "reference": m["land_reference_m2"]}
    for c, land in class_land.items():
        worst = max(float((m[f"season_{c}_{y}_m2"] - land).max()) for y in ALL_SEASONS)
        if worst > tol:
            fail(f"season/{c}: in some season more land has a value than the class holds (by {worst:.2f} m2)")
    return class_land


def tabulate(m, tables):
    """Every per-unit table, from the sums. `m` has one row per unit: unit_id, unit_level, outside_village and the bands."""
    ha = lambda c: m[c] / 1e4
    div = lambda a, b: a / b.where(b > 0)
    key = {"unit_id": m["unit_id"], "unit_level": m["unit_level"], "outside_village": m["outside_village"]}
    class_land = check_sums(m)
    land_tree = sum(ha(f"land_{b}_m2") for b in TREE)
    trend_tree = sum(ha(f"full_{b}_trend_m2") for b in TREE)
    by_unit = pd.DataFrame({"unit_id": m["unit_id"],
                            "nirv_slope": div(sum(m[f"full_{b}_slopesum"] for b in TREE), sum(m[f"full_{b}_trend_m2"] for b in TREE)).round(8),
                            "nirv_declining_ha": sum(ha(f"full_{b}_declining_m2") for b in TREE).round(4),
                            "nirv_increasing_ha": sum(ha(f"full_{b}_increasing_m2") for b in TREE).round(4),
                            "nirv_trend_ha": trend_tree.round(4), "land_treecover2000_gt10_ha": land_tree.round(4),
                            "missing_data_share": div((land_tree - trend_tree).clip(lower=0), land_tree).round(6)})

    groups_of_bands = {**{b: [b] for b in CANOPY}, "gt10": list(TREE), "all_land": list(CANOPY)}
    wide = pd.DataFrame(key)
    wide["area_ha"] = ha("area_m2").round(4)
    for b in CANOPY:
        wide[f"land_ha_{b}"] = ha(f"land_{b}_m2").round(4)
    wide["land_ha_reference"] = ha("land_reference_m2").round(4)
    for name, members in groups_of_bands.items():
        tot = lambda stub: sum(m[stub.format(b=b)] for b in members)
        wide[f"full_{name}_trend_ha"] = (tot("full_{b}_trend_m2") / 1e4).round(4)
        for t in ("declining", "increasing", "negative"):
            wide[f"full_{name}_{t}_ha"] = (tot("full_{b}_" + t + "_m2") / 1e4).round(4)
        wide[f"full_{name}_mean_slope"] = div(tot("full_{b}_slopesum"), tot("full_{b}_trend_m2")).round(8)
        wide[f"full_{name}_mean_nirv"] = div(tot("full_{b}_mediansum"), tot("full_{b}_trend_m2")).round(6)
        wide[f"full_{name}_slope_pct_of_mean_nirv_per_year"] = (100 * div(tot("full_{b}_slopesum"), tot("full_{b}_mediansum"))).round(5)
        for t in ("trend", "declining", "increasing"):
            wide[f"common_{name}_{t}_ha"] = (tot("common_{b}_" + t + "_m2") / 1e4).round(4)
        for t in ("valid", "lower", "higher"):
            wide[f"epoch_{name}_{t}_ha"] = (tot("epoch_{b}_" + t + "_m2") / 1e4).round(4)
        wide[f"epoch_{name}_change_pct"] = (100 * div(tot("epoch_{b}_latesum") - tot("epoch_{b}_earlysum"), tot("epoch_{b}_earlysum"))).round(4)

    # season by season
    seasons = np.array(ALL_SEASONS)
    S_sum = {c: m[[f"season_{c}_{y}_sum" for y in ALL_SEASONS]].to_numpy(float) for c in CLASSES}
    S_m2 = {c: m[[f"season_{c}_{y}_m2" for y in ALL_SEASONS]].to_numpy(float) for c in CLASSES}
    tree_sum, tree_m2 = sum(S_sum.values()), sum(S_m2.values())
    land_tree_m2 = sum(m[f"land_{b}_m2"] for b in TREE).to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean_tree = np.where(tree_m2 > 0, tree_sum / tree_m2, np.nan)
        share = np.where(land_tree_m2[:, None] > 0, tree_m2 / land_tree_m2[:, None], np.nan)
        ref_sum, ref_m2 = S_sum["reference"].sum(axis=0), S_m2["reference"].sum(axis=0)
        reference_series = ref_sum / ref_m2
    long = {"unit_id": np.repeat(m["unit_id"].to_numpy(), len(seasons)), "season": np.tile(seasons, len(m))}
    for c in CLASSES:
        with np.errstate(invalid="ignore", divide="ignore"):
            long[f"valid_ha_{c}"] = (S_m2[c] / 1e4).round(4).ravel()
            long[f"nirv_mean_{c}"] = np.where(S_m2[c] > 0, S_sum[c] / S_m2[c], np.nan).round(6).ravel()
    long["valid_ha_gt10"] = (tree_m2 / 1e4).round(4).ravel()
    long["valid_share_gt10"] = share.round(5).ravel()
    long["nirv_mean_gt10"] = mean_tree.round(6).ravel()
    season = pd.DataFrame(long)

    # the trend of each unit's own series, as measured and relative to all reference forest
    series = np.where(share >= SERIES_MIN_SHARE, mean_tree, np.nan)
    relative = series / reference_series[None, :]
    table, need = tables["full"], MIN_SEASONS["full"]
    cols = dict(key)
    cols["land_treecover2000_gt10_ha"] = (land_tree_m2 / 1e4).round(4)
    for tag, v in (("series", series), ("relative", relative)):
        s, n, dec, inc = test_rows(v, table, need)
        slope = sen_slope(v, ALL_SEASONS)
        with __import__("warnings").catch_warnings():
            __import__("warnings").simplefilter("ignore", RuntimeWarning)
            med = np.nanmedian(v, axis=1)
        tested = n >= need
        cols[f"{tag}_seasons"] = n
        cols[f"{tag}_median"] = np.where(tested, med, np.nan).round(6)
        cols[f"{tag}_slope_pct_per_year"] = np.where(tested & (med > 0), 100 * slope / med, np.nan).round(5)
        cols[f"{tag}_S"] = pd.array(np.where(tested, s, 0), dtype="Int64")
        cols[f"{tag}_S"][~tested] = pd.NA                                 # blank, not 0: a series that was not tested has no S
        cols[f"{tag}_flag"] = pd.Series(np.where(dec, "declining", np.where(inc, "increasing", "none")), dtype=object).where(tested, None).to_numpy()
    unit_series = pd.DataFrame(cols)
    return by_unit, wide, season, unit_series, {"series": series, "relative": relative, "reference_series": reference_series,
                                                 "reference_km2_with_a_value": ref_m2 / 1e6, "land_tree_m2": land_tree_m2, "class_land": class_land}


def level_table(m, tables):
    """lgd_panchayat units against outside_village units and all units, by canopy band."""
    level = m["unit_level"].to_numpy()
    groups_of_bands = {**{b: [b] for b in CANOPY}, "gt10": list(TREE), "all_land": list(CANOPY)}
    sizes = [r["declining_size"] for r in tables["full"].values() if r["declining_size"] is not None]
    rows = []
    for gname, sel in [("all units", np.ones(len(m), bool))] + [(k, level == k) for k in sorted(set(level))]:
        for name, members in groups_of_bands.items():
            tot = lambda stub: float(sum(m.loc[sel, stub.format(b=b)].sum() for b in members))
            pct = lambda a, b: round(100 * a / b, 3) if b else None
            land, tr = tot("land_{b}_m2"), tot("full_{b}_trend_m2")
            row = {"units": gname, "n_units": int(sel.sum()), "land": name, "land_km2": round(land / 1e6, 2), "with_a_trend_km2": round(tr / 1e6, 2), "missing_share_pct": pct(land - tr, land)}
            for t in ("declining", "increasing", "negative"):
                v = tot("full_{b}_" + t + "_m2")
                row[f"{t}_km2"], row[f"{t}_pct_of_trend_land"] = round(v / 1e6, 2), pct(v, tr)
            row["nominal_pct_declining_under_no_trend"] = f"{100 * min(sizes):.2f}-{100 * max(sizes):.2f}"
            row["mean_slope_per_year"] = float(f"{tot('full_{b}_slopesum') / tr:.4e}") if tr else None
            ms = tot("full_{b}_mediansum")
            row["mean_nirv"] = round(ms / tr, 5) if tr else None
            row["slope_pct_of_mean_nirv_per_year"] = round(100 * tot("full_{b}_slopesum") / ms, 4) if ms > 0 else None
            ct = tot("common_{b}_trend_m2")
            row["common_2017_2023_tested_km2"] = round(ct / 1e6, 2)
            row["common_declining_pct"], row["common_increasing_pct"] = pct(tot("common_{b}_declining_m2"), ct), pct(tot("common_{b}_increasing_m2"), ct)
            ev = tot("epoch_{b}_valid_m2")
            row["epoch_all_six_seasons_km2"] = round(ev / 1e6, 2)
            row["epoch_lower_km2"], row["epoch_higher_km2"] = round(tot("epoch_{b}_lower_m2") / 1e6, 2), round(tot("epoch_{b}_higher_m2") / 1e6, 2)
            row["epoch_lower_pct"], row["epoch_higher_pct"] = pct(tot("epoch_{b}_lower_m2"), ev), pct(tot("epoch_{b}_higher_m2"), ev)
            row["epoch_pct_each_way_if_seasons_were_in_random_order"] = 5.0
            es = tot("epoch_{b}_earlysum")
            row["epoch_change_pct"] = round(100 * (tot("epoch_{b}_latesum") - es) / es, 3) if es > 0 else None
            rows.append(row)
    return pd.DataFrame(rows)


def check_sample(sample, check, days, tables):
    """(1) At every sample pixel: the STORED standardised values, rates, sums, passes and mean days against the same
    quantities recomputed here from the stored passes. (2) At the check pixels: Earth Engine's trends and contrasts
    against the ones recomputed here from the stored yearly values.
    Returns (the local standardisation, {yearly value: [points, seasons] as stored}, largest gaps)."""
    obs, path_e, path_o = sample_arrays(sample)
    L = standardise_local(obs, path_e, path_o, days)
    first = sample[[f"nirv_{y}" for y in ALL_SEASONS]].to_numpy(float)
    stored = sample[[f"std_{y}" for y in ALL_SEASONS]].to_numpy(float)
    yearly = {"raw": np.where(first < -8, np.nan, first), "std": np.where(stored < -8, np.nan, stored)}
    counts = sample[[f"obs_{y}" for y in ALL_SEASONS]].to_numpy(float)
    passes = sample[[f"passes_{y}" for y in ALL_SEASONS]].to_numpy(float)
    if ((L["passes"] >= 1) != (counts >= 1)).any() or (L["passes"] > counts).any():
        fail("at some sample pixel a season has a kept scene but no pass with a day, or more passes than scenes: the path bands, the slots or the scene list do not fit the stored observations")
    if (passes != L["passes"]).any():
        fail(f"the stored number of passes differs from the passes counted here in {int((passes != L['passes']).sum())} pixel-seasons")
    worst = {}
    local32 = L["std"].astype(np.float32).astype(float)                    # the stored value is a 32-bit float
    if (np.isnan(yearly["std"]) != np.isnan(local32)).any():
        fail(f"the stored standardised value is defined at different pixel-seasons from the one recomputed here ({int((np.isnan(yearly['std']) != np.isnan(local32)).sum())} of {local32.size})")
    worst["standardised_value"] = float(np.nanmax(np.abs(yearly["std"] - local32))) if (~np.isnan(local32)).any() else 0.0
    for b in ("g", "h"):
        theirs = sample[b].where(sample[b] > -9000).to_numpy(float)
        if (np.isnan(theirs) != np.isnan(L[b])).any():
            fail(f"the stored {b} is defined at different pixels from the one recomputed here")
        worst[b] = float(np.nanmax(np.abs(theirs - L[b]) / np.maximum(np.abs(L[b]), 1e-3))) if (~np.isnan(L[b])).any() else 0.0
    if (sample["two"].to_numpy(float) != L["two"]).any():
        fail(f"the stored flag for a path step differs from the rule applied here at {int((sample['two'].to_numpy(float) != L['two']).sum())} pixels")
    for b in ("sdd", "sqq", "qbar"):
        worst[b] = float(np.max(np.abs(sample[b].to_numpy(float) - L[b]) / np.maximum(np.abs(L[b]), 1.0)))
    day = sample[[f"day_{y}" for y in ALL_SEASONS]].to_numpy(float)
    day = np.where(day < -8, np.nan, day)
    if (np.isnan(day) != np.isnan(L["mday"])).any():
        fail("the stored mean day is defined at different pixel-seasons from the one recomputed here")
    worst["mean_day"] = float(np.nanmax(np.abs(day - L["mday"]))) if (~np.isnan(L["mday"])).any() else 0.0
    limits = {"standardised_value": 1e-7, "g": 1e-5, "h": 1e-5, "sdd": 1e-5, "sqq": 1e-5, "qbar": 1e-5, "mean_day": 1e-4}
    if any(worst[k] > v for k, v in limits.items()):
        fail(f"the stored yearly values disagree with the standardisation redone here from the stored passes: largest gaps {worst}, allowed {limits}")
    rows = pd.Index(sample["i"]).get_indexer(check["i"])
    if (rows < 0).any():
        fail("a check pixel is not among the sample pixels")
        return L, yearly, worst
    for s in SERIES:
        V = yearly[s][rows]
        for window, suffix in (("full", ""), ("common", "_c")):
            sub = V[:, [ALL_SEASONS.index(y) for y in SEASONS[window]]]
            worst[f"{s}_S{suffix}"] = int(np.abs(check[f"{s}_S{suffix}"].to_numpy() - mk_S(sub)).max())
            worst[f"{s}_n{suffix}"] = int(np.abs(check[f"{s}_n{suffix}"].to_numpy() - (~np.isnan(sub)).sum(axis=1)).max())
        local_slope = sen_slope(V, ALL_SEASONS)
        ee_slope = check[f"{s}_slope"].where(check[f"{s}_slope"] > -9000).to_numpy(float)
        fitted = ~np.isnan(ee_slope)
        if (fitted != ((~np.isnan(V)).sum(axis=1) >= 2)).any():
            fail(f"{SERIES[s]}: the slope is fitted at pixels with fewer than two seasons, or missing at pixels with two or more")
        worst[f"{s}_slope"] = float(np.nanmax(np.abs(ee_slope[fitted] - local_slope[fitted]))) if fitted.any() else 0.0
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            local_median = np.nanmedian(V, axis=1)
        ee_median = check[f"{s}_median"].where(check[f"{s}_median"] > -9000).to_numpy(float)
        if (np.isnan(ee_median) != np.isnan(local_median)).any():
            fail(f"{SERIES[s]}: the thirteen-season median is defined at different pixels in Earth Engine and here")
        worst[f"{s}_median"] = float(np.nanmax(np.abs(ee_median - local_median))) if (~np.isnan(local_median)).any() else 0.0
        l_valid, l_lower, l_higher, l_early, l_late = contrast(V, list(EPOCH_EARLY), list(EPOCH_LATE))
        worst[f"{s}_contrast_flags"] = int((check[f"{s}_e_valid"].to_numpy() != l_valid).sum() + (check[f"{s}_e_lower"].to_numpy() != l_lower).sum() + (check[f"{s}_e_higher"].to_numpy() != l_higher).sum())
        worst[f"{s}_period_medians"] = 0.0
        for col, local in ((f"{s}_e_early", l_early), (f"{s}_e_late", l_late)):
            theirs = check[col].where(check[col] > -9000).to_numpy(float)
            if (np.isnan(theirs) != np.isnan(local)).any():
                fail(f"{SERIES[s]}: {col} is defined at different pixels in Earth Engine and here")
            elif (~np.isnan(local)).any():
                worst[f"{s}_period_medians"] = max(worst[f"{s}_period_medians"], float(np.nanmax(np.abs(theirs - local))))
    exact = [k for k in worst if k.endswith(("_S", "_n", "_S_c", "_n_c", "_contrast_flags"))]
    if any(worst[k] != 0 for k in exact) or any(worst[f"{s}_{k}"] > 2e-6 for s in SERIES for k in ("slope", "median", "period_medians")):
        fail(f"Earth Engine's trends and contrasts disagree with the ones recomputed here from the stored yearly values at the check pixels: largest gaps {worst}")
    # what the 32-bit rounding of the stored value does to the test: S from the stored values against S from the doubles
    s32, s64 = mk_S(yearly["std"]), mk_S(L["std"])
    worst["pixels_whose_S_differs_from_double_precision"] = int((s32 != s64).sum())
    if (s32 != s64).mean() > 0.01:
        fail(f"S from the stored 32-bit values differs from S in double precision at {int((s32 != s64).sum())} of {len(s32)} sample pixels: rounding cannot explain that")
    return L, yearly, worst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    ap.add_argument("--asset", help="the layer's table asset; default projects/<project>/assets/ictd/<layer stem>")
    a = ap.parse_args()
    started = now()
    project = eu.init(a.project)
    stem = Path(a.units).stem
    asset = a.asset or f"projects/{project}/assets/ictd/{stem}"
    obs_collection, std_collection = f"projects/{project}/assets/ictd/nirv_obs_{stem}", f"projects/{project}/assets/ictd/nirv_std_{stem}"
    units, fc, record = eu.load_units(a.units, asset)
    print(f"{a.units}: n = {len(units):,} units ({dict(units['unit_level'].value_counts())}); asset {asset}")

    # ---- the test's own table, against the published one -------------------------------------------------------------
    for (n, s), printed in EPA_TABLE.items():
        if abs(upper_tail(n, s) - printed) > 0.0006:
            fail(f"exact Mann-Kendall: P(S >= {s}) for n = {n} comes out {upper_tail(n, s):.4f}; the EPA table prints {printed}")
    stop_if_failed("checking the exact Mann-Kendall distribution against the EPA table")
    tables = {w: critical_table(SEASONS[w], MIN_SEASONS[w]) for w in SEASONS}
    print(f"OK  exact Mann-Kendall distribution reproduces all {len(EPA_TABLE)} values of the EPA table. Critical S, two-sided {ALPHA_TWO_SIDED:.0%}: "
          + "; ".join(f"{w} " + ", ".join(f"n={n}: {r['declining_S']}" for n, r in tables[w].items()) for w in tables))

    # ---- the stored observations, the stored yearly values, and the scenes behind them --------------------------------
    scenes, obs_prov, yearly_prov = load_records(obs_collection, std_collection)
    stop_if_failed("reading the records of the two exports")
    n_tiles, n_blocks = len(obs_prov["outputs_in_earth_engine"]["tile_boxes"]), len(yearly_prov["outputs_in_earth_engine"]["block_boxes"])
    for cid, wanted, what in ((obs_collection, set(obs_prov["outputs_in_earth_engine"]["tile_boxes"]), "tiles of observations"),
                              (std_collection, set(yearly_prov["outputs_in_earth_engine"]["block_boxes"]), "blocks of yearly values")):
        have = {x["name"].split("/")[-1] for x in ee.data.listAssets({"parent": cid}).get("assets", [])}
        if wanted - have:
            fail(f"{len(wanted - have)} of {len(wanted)} {what} are missing from {cid}")
    stop_if_failed("finding the stored observations and yearly values")
    days = YEARLY.day_lookup(scenes)
    print(f"OK  {n_tiles} tiles of observations and {n_blocks} blocks of yearly values present; {len(scenes):,} scenes behind them, {len(days)} passes by season, slot and parity")
    obs, yearly = stored_images(obs_collection, std_collection)
    annual = {"raw": first_design(obs)}
    annual["std"], model = stored_standardised(yearly)
    px = {s: pixel_image(annual[s]) for s in SERIES}

    # ---- the pixel sample FIRST: what is stored against the same arithmetic done here ----------------------------------
    # The names of the intermediate tables carry a fingerprint of what they hold (see fingerprint()).
    layer = gpd.read_file(a.units, layer="units")
    pts = sample_points(layer, SAMPLE_POINTS, SAMPLE_SEED)
    stop_if_failed("drawing the pixel sample")
    n_check = min(CHECK_POINTS, len(pts))
    made_from = [sha256(a.units), sha256(OUT / "nirv_scenes.csv"), OBS.RECIPE_SHA256, YEARLY.RECIPE_SHA256, repr(GRID)]     # what the stored values are, not when a record was written
    where = repr([(round(q.x, 9), round(q.y, 9)) for q in pts.geometry])
    stored_image, check_image = stored_point_image(obs, yearly), check_point_image(px)
    stored_asset = f"{asset}_nirv_points_stored_{fingerprint(stored_image, where, *made_from)}"
    check_asset = f"{asset}_nirv_points_check_{fingerprint(check_image, where, str(n_check), *made_from)}"
    point_tasks = [task for task in (start_points(pts, stored_image, stored_columns(), stored_asset, f"ictd_{stem}_nirv_points_stored"),
                                     start_points(pts.iloc[:n_check], check_image, check_columns(), check_asset, f"ictd_{stem}_nirv_points_check")) if task is not None]
    status_sample = eu.wait(point_tasks, "pixel-sample") if point_tasks else {}
    stop_if_failed("the pixel-sample tasks")
    sample = read_points(stored_asset, stored_columns())
    sample = sample.merge(pts[["unit_id", "unit_level"]].assign(lon=pts.geometry.x, lat=pts.geometry.y), left_on="i", right_index=True, validate="one_to_one").sort_values("i").reset_index(drop=True)
    check = read_points(check_asset, check_columns()).sort_values("i").reset_index(drop=True)
    if len(sample) != len(pts) or len(check) != n_check:
        fail(f"the pixel sample came back with {len(sample):,} and {len(check):,} rows for {len(pts):,} points and {n_check:,} check points")
        stop_if_failed("reading the pixel sample")
    L, yearly_px, worst = check_sample(sample, check, days, tables)
    stop_if_failed("checking the stored values and Earth Engine's trends against the stored passes")
    print(f"OK  at {len(sample):,} sample pixels the stored standardised values, rates, passes and mean days equal the standardisation redone here from the stored passes "
          f"(largest gaps: value {worst['standardised_value']:.1e}, rate {worst['g']:.1e} of itself, mean day {worst['mean_day']:.1e}; S differs from double precision at "
          f"{worst['pixels_whose_S_differs_from_double_precision']} pixels); at {len(check):,} of them Earth Engine's slopes, S, n and contrasts equal the ones recomputed here "
          f"(largest slope gap {max(worst['raw_slope'], worst['std_slope']):.1e}; S, n and the flags identical)", flush=True)

    # ---- then the sums per unit, for each of the two yearly values ----------------------------------------------------
    raw, status, cleanups, folders = {}, {}, [], {}
    for s, extra in (("raw", extra_bands_raw(model)), ("std", extra_bands_std(model, px["std"], tables))):
        image, bands = unit_bands(px[s], annual[s], tables, extra)
        if image.bandNames().getInfo() != bands:
            fail(f"{SERIES[s]}: the per-unit image's bands are not the ones named")
            stop_if_failed("building the per-unit image")
        folders[s] = f"{asset}_nirv{s}_parts_{fingerprint(image, repr(bands), str(GROUPS), str(TILE_SCALE), *made_from)}"
        print(f"{SERIES[s]}: {len(bands)} bands per unit; group tables in {folders[s].split('/')[-1]}", flush=True)
        raw[s], status[s], cleanup = eu.zonal(image, bands, fc, units, folders[s], f"{stem}_nirv{s}", GRID, GROUPS, TILE_SCALE)
        cleanups.append(cleanup)

    # ---- per unit ----------------------------------------------------------------------------------------------------
    key = ["unit_id", "unit_level", "outside_village", "polygon_m2"]
    M = {s: units[key].merge(raw[s], on="unit_id", validate="one_to_one") for s in SERIES}
    area = {s: eu.area_check(M[s]) for s in SERIES}
    T = {}
    for s in SERIES:
        by_unit_s, wide_s, season_s, series_s, extra_s = tabulate(M[s], tables)
        T[s] = {"by_unit": by_unit_s, "wide": wide_s, "season": season_s, "series": series_s, "extra": extra_s, "level": level_table(M[s], tables)}
    if (T["std"]["by_unit"]["land_treecover2000_gt10_ha"] - T["raw"]["by_unit"]["land_treecover2000_gt10_ha"]).abs().max() > 1e-3:
        fail("the two sets of sums disagree about the land with treecover2000 > 10")
    for b in CANOPY:
        if (M["std"][f"rate_{b}_m2"] > M["std"][f"land_{b}_m2"] + 0.01).any() or (M["std"][f"twopath_{b}_m2"] > M["std"][f"rate_{b}_m2"] + 0.01).any():
            fail(f"{b}: land with a rate exceeds the band's land, or land with a path step exceeds land with a rate")
        if (M["std"][f"full_{b}_trend_m2"] > M["std"][f"rate_{b}_m2"] + 0.01).any():
            fail(f"{b}: land with a standardised trend exceeds land with a rate")
    stop_if_failed("checking the zonal statistics")
    print(f"OK  {len(units):,} units returned twice; bands add up; tiers nest; area summed over pixels {area['std']['pixels_km2']:,.2f} km2 vs polygons {area['std']['polygons_on_the_ellipsoid_km2']:,.2f} ({area['std']['relative_difference']:+.2e})")

    ha = lambda v: (v / 1e4).round(4)
    by_unit = T["std"]["by_unit"].copy()
    for c in ("nirv_slope", "nirv_declining_ha", "nirv_increasing_ha", "nirv_trend_ha"):
        by_unit[f"{c}_unadjusted"] = T["raw"]["by_unit"][c].to_numpy()
    shared = [c for c in T["std"]["wide"].columns if c in ("unit_id", "unit_level", "outside_village", "area_ha") or c.startswith("land_ha_")]
    wide = pd.concat([T["std"]["wide"][shared]] + [T[s]["wide"].drop(columns=shared).add_prefix(f"{s}_") for s in SERIES], axis=1)
    div = lambda x, y: x / y.where(y > 0)
    more = {}
    for b in CANOPY:
        more[f"std_rate_ha_{b}"], more[f"std_two_paths_ha_{b}"] = ha(M["std"][f"rate_{b}_m2"]), ha(M["std"][f"twopath_{b}_m2"])
        more[f"std_{b}_rate_pct_of_mean_nirv_per_30_days"] = (100 * 30 * div(M["std"][f"full_{b}_ratesum"], M["std"][f"full_{b}_mediansum"])).round(4)
        more[f"raw_single_pass_share_{b}"] = div(M["raw"][f"single_{b}_m2x"], len(ALL_SEASONS) * M["raw"][f"land_{b}_m2"]).round(5)
    more["std_gt10_rate_pct_of_mean_nirv_per_30_days"] = (100 * 30 * div(sum(M["std"][f"full_{b}_ratesum"] for b in TREE), sum(M["std"][f"full_{b}_mediansum"] for b in TREE))).round(4)
    wide = pd.concat([wide, pd.DataFrame(more)], axis=1)
    season = pd.concat([T["std"]["season"][["unit_id", "season"]]] + [T[s]["season"].drop(columns=["unit_id", "season"]).add_prefix(f"{s}_") for s in SERIES], axis=1)
    day_sum = M["raw"][[f"day_{y}_sum" for y in ALL_SEASONS]].to_numpy(float)
    day_m2 = M["raw"][[f"day_{y}_m2" for y in ALL_SEASONS]].to_numpy(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        mday_units = np.where(day_m2 > 0, day_sum / day_m2, np.nan)
    season["mean_day_gt10"] = mday_units.round(3).ravel()
    keys = ["unit_id", "unit_level", "outside_village", "land_treecover2000_gt10_ha"]
    unit_series = pd.concat([T["std"]["series"][keys]] + [T[s]["series"].drop(columns=keys).add_prefix(f"{s}_") for s in SERIES], axis=1)
    by_level = pd.concat([T[s]["level"].assign(yearly_value=SERIES[s]) for s in SERIES], ignore_index=True)
    by_level = by_level[["yearly_value"] + [c for c in by_level.columns if c != "yearly_value"]]
    level = M["std"]["unit_level"].to_numpy()
    rate_rows = []
    for gname, sel in [("all units", np.ones(len(units), bool))] + [(k, level == k) for k in sorted(set(level))]:
        for name, members in {**{b: [b] for b in CANOPY}, "gt10": list(TREE)}.items():
            tot = lambda stub: float(sum(M["std"].loc[sel, stub.format(b=b)].sum() for b in members))
            land = tot("land_{b}_m2")
            rate_rows.append({"units": gname, "land": name, "land_km2": round(land / 1e6, 2), "with_a_rate_pct": round(100 * tot("rate_{b}_m2") / land, 3) if land else None,
                              "with_a_path_step_pct": round(100 * tot("twopath_{b}_m2") / land, 3) if land else None,
                              "rate_pct_of_mean_nirv_per_30_days": round(100 * 30 * tot("full_{b}_ratesum") / tot("full_{b}_mediansum"), 3) if tot("full_{b}_mediansum") > 0 else None,
                              "seasons_resting_on_one_pass_pct": round(100 * float(sum(M["raw"].loc[sel, f"single_{b}_m2x"].sum() for b in members)) / (len(ALL_SEASONS) * land), 3) if land else None})
    rates = pd.DataFrame(rate_rows)

    # ---- the null, and the date check --------------------------------------------------------------------------------
    table, need = tables["full"], MIN_SEASONS["full"]
    cover, lossyear, lvl = sample["treecover2000"].to_numpy(), sample["lossyear"].to_numpy(), sample["unit_level"].to_numpy()
    tree_px = cover > 10
    reference_px = (cover > 50) & (lossyear == 0)
    pixel_groups = {"treecover2000 > 10, all units": tree_px, "treecover2000 > 10, lgd_panchayat": tree_px & (lvl == "lgd_panchayat"), "treecover2000 > 10, outside_village": tree_px & (lvl == "outside_village"),
                    "treecover2000 > 10 and not reference, all units": tree_px & ~reference_px, "treecover2000 > 10 and not reference, lgd_panchayat": tree_px & ~reference_px & (lvl == "lgd_panchayat"),
                    "treecover2000 > 10 and not reference, outside_village": tree_px & ~reference_px & (lvl == "outside_village"),
                    "reference forest": reference_px, "treecover2000 <= 10, lgd_panchayat": ~tree_px & (lvl == "lgd_panchayat"), "treecover2000 <= 10, outside_village": ~tree_px & (lvl == "outside_village")}
    land_tree_m2 = T["std"]["extra"]["land_tree_m2"]
    big = land_tree_m2 >= SUMMARY_MIN_HA * 1e4
    unit_groups = {f"units with >= {SUMMARY_MIN_HA:g} ha of treecover2000 > 10, all": big, f"units with >= {SUMMARY_MIN_HA:g} ha of treecover2000 > 10, lgd_panchayat": big & (level == "lgd_panchayat"),
                   f"units with >= {SUMMARY_MIN_HA:g} ha of treecover2000 > 10, outside_village": big & (level == "outside_village"), "every unit, all": np.ones(len(units), bool)}
    null_rows_all, reference_cols = [], {"season": ALL_SEASONS}
    for s, label in SERIES.items():
        V, R, E = yearly_px[s], T[s]["extra"]["reference_series"], T[s]["extra"]
        rows = (null_rows("sampled pixels", "as it is", V, table, need, pixel_groups, PERMUTATIONS, PERMUTATION_SEED)
                + null_rows("sampled pixels", "relative to reference forest", V / R[None, :], table, need, pixel_groups, PERMUTATIONS, PERMUTATION_SEED)
                + null_rows("unit series", "as it is", E["series"], table, need, unit_groups, PERMUTATIONS, PERMUTATION_SEED)
                + null_rows("unit series", "relative to reference forest", E["relative"], table, need, unit_groups, PERMUTATIONS, PERMUTATION_SEED)
                + contrast_null_rows("sampled pixels, before and after", "as it is", V, pixel_groups)
                + contrast_null_rows("sampled pixels, before and after", "relative to reference forest", V / R[None, :], pixel_groups)
                + contrast_null_rows("unit series, before and after", "as it is", E["series"], unit_groups)
                + contrast_null_rows("unit series, before and after", "relative to reference forest", E["relative"], unit_groups))
        null_rows_all += [{"yearly_value": label, **r} for r in rows]
        reference_cols[f"{s}_reference_forest_mean_nirv"] = np.round(R, 6)
        reference_cols[f"{s}_reference_forest_km2_with_a_value"] = np.round(E["reference_km2_with_a_value"], 2)
    null = pd.DataFrame(null_rows_all)
    reference = pd.DataFrame(reference_cols)
    check_groups = {k: v for k, v in pixel_groups.items() if "not reference" not in k}
    date_check = pd.DataFrame(date_check_rows("unit series", unit_groups, {s: T[s]["extra"]["series"] for s in SERIES}, mday_units, weight=land_tree_m2)
                              + date_check_rows("sampled pixels", check_groups, yearly_px, L["mday"]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        px_level = np.nanmedian(yearly_px["std"], axis=1)
    rate30 = np.where(px_level > 0, 100 * 30 * L["g"] / px_level, np.nan)
    step = np.where(L["two"] & (px_level > 0), 100 * L["h"] / px_level, np.nan)
    sample_rate_rows = []
    for gname, sel in check_groups.items():
        r, st = rate30[sel], step[sel]
        q = (lambda v, p: round(float(np.nanpercentile(v, p)), 2) if (~np.isnan(v)).any() else None)
        sample_rate_rows.append({"what": "sampled pixels: the rates", "group": gname, "n_pixels": int(sel.sum()), "with_a_rate_pct": round(100 * float((~np.isnan(L["g"][sel])).mean()), 2) if sel.any() else None,
                                 "rate_pct_of_level_per_30_days_p25": q(r, 25), "rate_pct_of_level_per_30_days_median": q(r, 50), "rate_pct_of_level_per_30_days_p75": q(r, 75),
                                 "with_a_path_step_pct": round(100 * float(L["two"][sel].mean()), 2) if sel.any() else None, "path_step_pct_of_level_median": q(st, 50),
                                 "passes_per_season_mean": round(float(L["passes"][sel].mean()), 2) if sel.any() else None})
    date_check = pd.concat([date_check, pd.DataFrame(sample_rate_rows)], ignore_index=True)
    sensitivity = pd.DataFrame(rate_sensitivity_rows(*sample_arrays(sample), days, check_groups, tables, PERMUTATION_SEED))

    sample_out = sample.drop(columns=[c for c in sample.columns if c.startswith("o_")]).merge(check, on="i", how="left", validate="one_to_one")
    for c in sample_out.columns:
        if c[-4:].isdigit() and c.startswith(("nirv_", "std_", "day_")):
            sample_out[c] = sample_out[c].where(sample_out[c] > -8)
        elif c in ("g", "h") or (c in check.columns and c != "i"):
            sample_out[c] = sample_out[c].where(sample_out[c] > -9000)
    passes_long = pd.DataFrame({"i": np.repeat(sample["i"].to_numpy(), len(ALL_SEASONS) * len(PASSES)), "season": np.tile(np.repeat(ALL_SEASONS, len(PASSES)), len(sample)),
                                "slot": np.tile([k for k, _ in PASSES], len(sample) * len(ALL_SEASONS)), "parity": np.tile([p for _, p in PASSES], len(sample) * len(ALL_SEASONS)),
                                "nirv": sample_arrays(sample)[0].ravel()}).dropna(subset=["nirv"])

    OUT.mkdir(exist_ok=True)
    out_tables = {"nirv_by_unit.csv": by_unit, "nirv_by_unit_bands.csv": wide, "nirv_by_unit_season.csv": season, "nirv_by_unit_series.csv": unit_series,
                  "nirv_by_unit_level.csv": by_level, "nirv_rates.csv": rates, "nirv_null.csv": null, "nirv_date_check.csv": date_check, "nirv_rate_sensitivity.csv": sensitivity,
                  "nirv_reference_series.csv": reference,
                  "nirv_pixel_sample.csv": sample_out, "nirv_pixel_sample_passes.csv": passes_long}
    for name, t in out_tables.items():
        t.to_csv(OUT / name, index=False)

    blank = lambda t: {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}
    with open(OUT / "nirv.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_build_nirv.py", "script_sha256": sha256(__file__), "helper": "scripts/_ee_units.py",
            "helper_sha256": sha256(Path(__file__).with_name("_ee_units.py")),
            "uses": {f"scripts/{n}": sha256(Path(__file__).with_name(n)) for n in ("02_export_nirv_yearly.py", "02_export_nirv_observations.py")},
            "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                       {"earth_engine_asset": asset, "checked_against_the_layer_by": str(record.relative_to(ROOT))},
                       {"earth_engine_image_collection": obs_collection, "tiles": n_tiles, "recipe_sha256": OBS.RECIPE_SHA256, "exported_by_run": obs_prov["run_utc"], "recorded_in": obs_prov.get("_read_from")},
                       {"earth_engine_image_collection": std_collection, "blocks": n_blocks, "recipe_sha256": YEARLY.RECIPE_SHA256, "exported_by_run": yearly_prov["run_utc"], "recorded_in": yearly_prov.get("_read_from")},
                       {"path": "20_degradation/nirv_scenes.csv", "bytes": (OUT / "nirv_scenes.csv").stat().st_size, "sha256": sha256(OUT / "nirv_scenes.csv"), "scenes": int(len(scenes))},
                       {"earth_engine_dataset": HANSEN, "bands": ["treecover2000", "lossyear"], "grid": GRID}],
            "definitions": {"yearly_values": {"std_ / date-standardised (the delivered columns)": f"the stored std_<season> (02_export_nirv_yearly.py), a 32-bit float: median of the season's passes, each moved to day {STANDARD_DAY:g} (1 December) by the cell's own rate g and to the cell's usual path mix by its path step h",
                                              "raw_ / first design": "median of the season's kept scenes (the stored nirv_<season>)"},
                            "standardisation": {"model": "v = level(season) + g x (day - 30) + h x [odd path], least squares within seasons, all seasons pooled, per cell",
                                                "a_rate_needs_Sdd_of_at_least": SDD_MIN, "a_path_step_needs_Sqq_of_at_least": SQQ_MIN, "standard_day": STANDARD_DAY},
                            "seasons": SEASONS, "min_seasons": MIN_SEASONS,
                            "declining": f"S <= -(exact critical value for two-sided {ALPHA_TWO_SIDED:.0%}) for the pixel's number of seasons", "increasing": "S >= +(the same critical value)",
                            "negative": "Theil-Sen slope < 0", "critical_values": {w: {str(n): r for n, r in t.items()} for w, t in tables.items()},
                            "canopy_bands": CANOPY, "classes_for_the_season_means": CLASSES,
                            "nirv_declining_ha": "declining pixels on land with treecover2000 > 10, seasons 2013-2025, date-standardised values", "nirv_increasing_ha": "increasing pixels on the same land",
                            "nirv_slope": "area-weighted mean Theil-Sen slope on the same land, NIRv per year",
                            "missing_data_share": "land with treecover2000 > 10 and no standardised trend (fewer than 10 seasons, or no rate), over land with treecover2000 > 10",
                            "_unadjusted": "the same four columns from the first design's values",
                            "epoch": {"earlier": EPOCH_EARLY, "later": EPOCH_LATE, "lower": "every later season below every earlier one; all six needed",
                                      "change": "(mean of the later-period values - mean of the earlier-period values) / mean of the earlier, a pixel's period value being the median of its three seasons; pixels with all six"},
                            "unit_series": f"mean yearly value of the unit's land with treecover2000 > 10, for seasons in which at least {SERIES_MIN_SHARE:.0%} of it has a value; relative = divided by the mean of all reference forest that season",
                            "mean_day_gt10": "area-weighted mean, over the unit's land with treecover2000 > 10 that was seen that season, of the mean day of each pixel's passes",
                            "null": f"{PERMUTATIONS} re-orderings of the seasons, the same order for every row, seed {PERMUTATION_SEED}; for the contrast, the twenty splits of the six seasons",
                            "day_of_a_pass": "mean of the day column of nirv_scenes.csv as printed (five decimals) over the scenes of the season, slot and path",
                            "scatter": "standard deviation (divisor n) of a series about its own Theil-Sen line through its median, as a share of the median",
                            "rate_sensitivity": "sampled pixels, in double precision from the stored passes; every pixel's rate multiplied by the value given before its passes are moved; and one pass per pixel removed at random (seed as the null's) and everything refitted"},
            "earth_engine": {"project": project, "zonal_tasks": {s: eu.task_record(status[s]) for s in SERIES}, "zonal_eecu_seconds": {s: round(eu.eecu(status[s]), 1) for s in SERIES},
                             "group_tables_taken_from_an_earlier_attempt_of_the_same_computation": {s: GROUPS - len(status[s]) for s in SERIES}, "group_table_folders": folders,
                             "sample_tasks": eu.task_record(status_sample), "sample_eecu_seconds": round(eu.eecu(status_sample), 1)},
            "checks_passed": {"exact_distribution_matches_epa_table": len(EPA_TABLE), "pixel_sample": {"points": int(len(sample)), "check_points": int(len(check)), "largest_gaps": worst,
                                               "stored_values_equal_the_standardisation_redone_from_the_stored_passes": True, "S_n_and_flags_identical_at_the_check_points": True},
                              "units_returned_each_once": int(len(units)), "bands_add_up": True, "tiers_nest": True, "area_summed_over_pixels_vs_polygons": area},
            "reference_forest_mean_by_season": {s: {str(y): float(v) for y, v in zip(ALL_SEASONS, T[s]["extra"]["reference_series"])} for s in SERIES},
            "tables": {name: {"rows": int(len(t)), "columns": int(len(t.columns)), "blank_cells": blank(t)} for name, t in out_tables.items()},
            "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        }, fh, indent=2)

    try:                                                   # only now that the tables and their record are written; a failed delete loses nothing
        for cleanup in cleanups:
            cleanup()
        for asset_id in (stored_asset, check_asset):
            ee.data.deleteAsset(asset_id)
    except Exception as e:
        print(f"NOTE  the intermediate tables could not all be deleted ({type(e).__name__}: {e}). Left in Earth Engine, to delete by hand: "
              f"{', '.join(x.split('/')[-1] for x in list(folders.values()) + [stored_asset, check_asset])}")

    print(f"\nnirv_by_unit.csv: n = {len(by_unit):,} units; blank cells {blank(by_unit) or 'none'}")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    show = by_level[by_level["land"].isin(["gt10"])]
    print(f"\nnirv_by_unit_level.csv: n = {len(by_level)} rows; shown: land with treecover2000 > 10, both yearly values")
    print(show.drop(columns=["n_units"]).T.to_string(header=False))
    print(f"\nnirv_rates.csv: n = {len(rates)} rows")
    print(rates[rates.land.isin(["gt10", "le10"])].to_string(index=False))
    print(f"\nnirv_date_check.csv: n = {len(date_check)} rows")
    print(date_check.to_string(index=False))
    print(f"\nnirv_rate_sensitivity.csv: n = {len(sensitivity)} rows; shown: treecover2000 > 10, all units")
    print(sensitivity[sensitivity.group == "treecover2000 > 10, all units"].drop(columns=["group"]).to_string(index=False))
    print(f"\nnirv_null.csv: n = {len(null)} rows; shown: sampled pixels and unit series as they are, land with treecover2000 > 10")
    print(null[(null.basis == "as it is") & null.group.isin(["treecover2000 > 10, all units", f"units with >= {SUMMARY_MIN_HA:g} ha of treecover2000 > 10, all"])].drop(columns=["basis", "reorderings"]).to_string(index=False))
    print(f"\nEarth Engine: sums {eu.eecu(status['raw']):,.0f} + {eu.eecu(status['std']):,.0f} EECU-seconds, sample {eu.eecu(status_sample):,.0f}; done. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
