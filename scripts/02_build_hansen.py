#!/usr/bin/env python3
"""
Stage 1 - forest and tree-cover loss per analysis unit, from Hansen Global Forest Change.

    python scripts/02_upload_units_asset.py --units 10_units/units.gpkg      (first; it puts the layer in Earth Engine)
    python scripts/02_build_hansen.py --units 10_units/units.gpkg

In : --units                    the stage-0 layer; every unit is measured, the outside_village ones included
     the same layer as an Earth Engine table asset (projects/<project>/assets/ictd/<layer stem>), written and
     checked against the layer by 02_upload_units_asset.py. The asset stores its edges as geodesics; the
     layer's are straight lines in lon/lat; that script measures the gap between the two. The sums that come
     out of this script behave as if the edges were straight (independent check, 6 October 2026); either way
     the difference is at most 0.094 ha for one unit and 0.22 ha over all of them.
     UMD/hansen/global_forest_change_2025_v1_13    bands treecover2000, lossyear, datamask
Out: 20_degradation/ and nowhere else
     hansen_by_unit.csv                         unit_id, forest_ha, hansen_loss_ha, hansen_loss_ha_2001 ... _2025, missing_data_share
     hansen_by_unit_thresholds.csv              per unit: the same at other canopy lines, and the areas behind the shares
     hansen_loss_by_canopy_band_by_unit.csv     per unit: land and loss in three bands of year-2000 canopy, by year
     hansen_loss_by_canopy_band.csv             the same summed: all units, lgd_panchayat units, outside_village units
     hansen_by_unit_level.csv                   lgd_panchayat units against outside_village units
     hansen_reconciliation.csv                  state totals beside Global Forest Watch's and the Forest Survey of India's
     hansen.provenance.json                     inputs, UTC run time, definitions, checks, n and missingness

EVERY THRESHOLD IS WRITTEN AS AN INEQUALITY. "gt30" is treecover2000 > 30; "ge30" is treecover2000 >= 30;
"le10" is treecover2000 <= 10. There is no bare "at 30" anywhere in the outputs.

WHAT IS MEASURED, EXACTLY. All of it on Hansen's own grid - EPSG:4326, pixels of 0.00025 degrees, transform
[0.00025, 0, -180, 0, -0.00025, 80] - with nothing resampled.
  forest             a pixel whose treecover2000 > 30. treecover2000 is the per cent canopy closure, in the year
                     2000, of vegetation taller than 5 m, in whole per cent. It is a year-2000 mask and stays fixed.
  forest_ha          the area of forest pixels inside the unit.
  hansen_loss_ha_Y   the area of forest pixels inside the unit whose lossyear is Y - 2000 (lossyear 1..25 = 2001..2025).
                     Loss outside the year-2000 forest mask is NOT in this column; see the canopy bands below.
  hansen_loss_ha     the sum of the 25 years.
  missing_data_share the area inside the unit where datamask is 0 (no data), over the unit's whole area on the grid.
                     datamask 2 is permanent water: it is not missing and, having no tree cover, not forest. In this
                     window datamask 0 is open sea, so the share can only be zero for a land unit. It is no measure
                     of data quality.
  area               each pixel counts for its true area on the ellipsoid (ee.Image.pixelArea), not a nominal 30 m
                     square, and for the FRACTION of it that lies inside the unit's polygon - Earth Engine's weighted
                     sum reducer, run through reduceRegions with Hansen's crs and crsTransform. A unit's figures are
                     therefore sums of (pixel area x fraction inside), in hectares.
The units do not overlap, so no pixel area is counted twice.

THE CANOPY BANDS. Every pixel is in exactly one of three bands of year-2000 canopy:
  le10       treecover2000 <= 10            open land, cropland, water - and land already bare of trees in 2000
  gt10le30   10 < treecover2000 <= 30       open or thinned tree cover
  gt30       treecover2000 > 30             the forest mask
hansen_loss_by_canopy_band_by_unit.csv gives each unit's land (area_ha_<band>) and loss (loss_ha_<band>, and
loss_ha_<band>_<year>) in each. The three bands' land adds up to the unit and their loss to the unit's Hansen
loss with no mask at all (loss_ha_any_cover). loss_ha_gt30 is hansen_loss_ha.
Inside le10 one part is carried separately, as an "of which" and not as a fourth band:
  eq0        treecover2000 = 0              no tree cover at all in 2000
HOW TO READ LOSS IN THE LOWER BANDS. A pixel with no canopy in 2000 had no forest to lose. Loss recorded on it
is the removal of tree cover that grew after 2000 - a plantation felled, regrowth cleared - or an artefact of
detection. And the detection has changed: loss in the two lower bands steps up at 2011, at 2013 and again at
2023, far more sharply than loss in gt30 does. So the lower bands say that tree cover came and went on land
that was open in 2000; they do not say that forest standing in 2000 was degraded, and their rise over time
cannot be read as a trend on the ground. The summary table gives the periods so that this can be seen.

THE THRESHOLD IS A CHOICE (ruling of 6 October 2026: treecover2000 > 30). There is no single correct canopy
threshold for treecover2000. Strictly above 30 is used for two reasons. It is the commoner written form in the
literature, "greater than 30%" (the project owner's reading; not checked here). And it is what Global Forest
Watch's published statistics actually compute: its notes say ">=30%", but on its own boundary the public tiles
reproduce its figures to within about a hectare with > 30 and miss them by 0.43 per cent with >= 30
(independent replication, 5 October 2026, repeated 6 October). The reconciliation table
therefore sets Global Forest Watch's figures beside ours at > T, which is like for like and is gated, and
beside ours at >= T, which is what its notes say and is not. THAT GATE CANNOT TELL > FROM >=. The units
cover 0.46 per cent less area than Global Forest Watch's boundary, so both readings land well inside the
tolerance, and >= T even lands nearer. The gate catches a gross error - wrong band, wrong units, a lost
group of polygons - and nothing finer. What shows that Global Forest Watch computes > T is the replication
on its own boundary, where the public tiles give its figures to within about a hectare with > T (-0.9, -0.8
and +1.4 ha at 10, 30 and 50) and miss them by 0.53, 0.43 and 0.13 per cent with >= T.
hansen_by_unit_thresholds.csv carries every unit at > 10 and > 50 as the sensitivity, and at >= 30 so that
the pixels at exactly 30 can be seen.
The Forest Survey of India writes its own lines with "equal to or more than" (10, 40 and 70 per cent), so its
rows are set beside treecover2000 >= 10, >= 40 and >= 70, and beside > 10 as well.

HOW EXACT THE AREAS ARE. Two things are tested at every run, on boxes drawn for the purpose, and recorded:
  - a box laid on pixel edges, so that no pixel is cut, must sum to its area on the WGS84 ellipsoid computed in
    closed form. That fixes the grid and shows the pixel areas are ellipsoidal. The run stops if it fails.
  - the same box moved half a pixel, so that every boundary pixel is cut exactly in half. Earth Engine's
    fraction for a cut pixel is approximate and leans low; the shortfall on this box is printed. It is a
    property of the engine, not a setting. On real boundaries the replication measured about 0.0009 of a
    pixel short per cut pixel, with a scatter several times that.
So a unit's area summed over pixels is not exactly its polygon's area. Every unit's is compared with the area of
its polygon on the ellipsoid, computed here from the layer: the run stops if any unit is out by more than 1 per
cent of its area (or 500 m2, whichever is larger) or the total by more than 0.1 per cent, and the size and sign
of the difference are reported. forest_ha and the losses carry the same small error at each unit's edge and
none in its interior.

WHAT THIS IS NOT. Hansen "loss" is stand-replacing removal of tree cover from any cause; it is not a measure of
deforestation and it does not see degradation that leaves a canopy. Gain is not netted off. The data's producers
warn that 2011 onward was mapped with an updated method, so a rise across 2010/2011 is partly the method; in
the lower bands the steps at 2012/2013 and 2022/2023 are larger still.
hansen_loss_ha is clearance of what had more than 30 per cent canopy in 2000 and nothing else. That is not
all "closed" forest: a seventh of the mask has canopy of 31 to 39 per cent. Loss in the two lower bands is a
large part of all Hansen loss here and is reported beside it, not inside it. Many units have little or no
forest by this mask, so a loss RATE per unit is undefined or noise for most of them. Counts of "units with
any forest" or "any loss" run a handful low: Earth Engine returns 0.0000 for a sliver of a pixel.
The source tiles overlap by one grid row at 20 N: treecover2000 and datamask are identical in the two copies
of that row; lossyear differs in 254 of its pixels, all dated 2011 or later (found by the replication; it is
in the product, not here, and involves about a hundredth of a per cent of the totals).

Needs earthengine-api, geopandas, pyproj, pandas, numpy; scripts/_ee_units.py.
"""
import argparse, json, sys, time
from pathlib import Path

import ee
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ee_units as eu
from _ee_units import OUT, ROOT, fail, now, sha256, stop_if_failed

HANSEN = "UMD/hansen/global_forest_change_2025_v1_13"
GRID = {"crs": "EPSG:4326", "transform": [0.00025, 0, -180, 0, -0.00025, 80]}      # checked against the asset at run time
THRESHOLD = 30                       # the forest mask is treecover2000 > THRESHOLD
SENSITIVITY = (10, 50)               # treecover2000 > 10 and > 50, per unit
AT_OR_ABOVE = (10, 30, 40, 50, 70)   # treecover2000 >= t: Global Forest Watch's notes (10, 30, 50) and the Forest Survey's classes (10, 40, 70)
BANDS = {"le10": "treecover2000 <= 10", "gt10le30": "10 < treecover2000 <= 30", "gt30": "treecover2000 > 30"}
YEARS = list(range(2001, 2026))
PERIODS = ((2001, 2010), (2011, 2017), (2018, 2025))
ISFR_LAST_LOSS_YEAR = 2021           # ISFR 2023 rests on imagery of October to December 2021
GROUPS = 8
TILE_SCALE = 4
TEST_BOX = (84.0, 20.25, 84.25, 20.5)                # lon/lat, on pixel edges: 1,000 x 1,000 pixels in the middle of the state
BOX_TOLERANCE = 1e-8                 # the uncut box against its closed-form area

# Global Forest Watch, "IND.xlsx" (https://gfw2-data.s3.amazonaws.com/country-pages/country_stats/download/IND.xlsx,
# fetched 2026-10-05, sha256 c79dc6fb...3f35a8), sheet "Subnational 1 tree cover loss", rows for Odisha. Hectares.
# Its boundary is GADM 3.6 (15,563,805 ha) and its loss runs 2001-2020.
GFW_SOURCE = "Global Forest Watch country statistics for India (IND.xlsx), sheet 'Subnational 1 tree cover loss', Odisha; GADM 3.6 boundary; fetched 2026-10-05"
GFW_AREA_HA = 15_563_805
GFW_EXTENT_2000_HA = {10: 3776619, 30: 2680194, 50: 1567786}
GFW_LOSS_HA_30 = {2001: 2977, 2002: 3976, 2003: 5382, 2004: 4462, 2005: 3602, 2006: 4226, 2007: 5886, 2008: 5939, 2009: 4790, 2010: 2394,
                  2011: 5593, 2012: 3779, 2013: 5353, 2014: 7491, 2015: 3867, 2016: 8340, 2017: 10130, 2018: 9792, 2019: 7759, 2020: 8873}
GFW_EXTENT_TOLERANCE = 0.02          # like for like (treecover2000 > T): the two boundaries differ
GFW_LOSS_TOTAL_TOLERANCE = 0.10      # 2001-2020 summed, like for like (treecover2000 > 30)

# Forest Survey of India, India State of Forest Report 2023, Volume II, Table 10.20.2 "Forest Cover of Odisha"
# (https://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-2_2023.pdf, fetched 2026-10-05, sha256 86029d09...dbae344). km2.
# Volume I words every line with "equal to or more than": forest cover "more than or equal to 10%", very dense
# "equal to or more than 70%", moderately dense "equal to or more than 40% but less than 70%".
ISFR_SOURCE = "Forest Survey of India, India State of Forest Report 2023, Vol. II, Table 10.20.2; LISS-III 23.5 m imagery of October-December 2021"
ISFR_2023_KM2 = {"very_dense_forest_canopy_ge70": 7224.42, "moderately_dense_forest_canopy_ge40_lt70": 21065.55,
                 "open_forest_canopy_ge10_lt40": 24143.59, "total_forest_cover_canopy_ge10": 52433.56}


def hansen_areas():
    """One band per quantity, each holding (pixel area in m2) where the condition is true and 0 elsewhere."""
    h = ee.Image(HANSEN)
    cover, lossyear, datamask = (h.select(b).unmask(0) for b in ("treecover2000", "lossyear", "datamask"))
    area = ee.Image.pixelArea()
    in_band = {"le10": cover.lte(10), "gt10le30": cover.gt(10).And(cover.lte(30)), "gt30": cover.gt(30)}
    lost = lossyear.gt(0)
    bands = [area.rename("area_m2"), area.multiply(datamask.eq(0)).rename("nodata_m2"), area.multiply(datamask.eq(2)).rename("water_m2")]
    for t in sorted({THRESHOLD, *SENSITIVITY}):
        bands.append(area.multiply(cover.gt(t)).rename(f"forestgt{t}_m2"))
    for t in AT_OR_ABOVE:
        bands.append(area.multiply(cover.gte(t)).rename(f"forestge{t}_m2"))
    for b, cond in list(in_band.items()) + [("eq0", cover.eq(0))]:                         # eq0 is part of le10, carried as an "of which"
        bands.append(area.multiply(cond).rename(f"area{b}_m2"))
        for y in YEARS:
            bands.append(area.multiply(lossyear.eq(y - 2000).And(cond)).rename(f"loss{y}{b}_m2"))
    bands.append(area.multiply(lost.And(cover.gt(THRESHOLD))).rename("lossanygt30_m2"))     # must equal the 25 years of the gt30 band summed
    bands.append(area.multiply(lost).rename("lossnomask_m2"))                              # must equal all three bands, all years
    bands.append(area.multiply(lost.And(cover.gt(50))).rename("lossanygt50_m2"))
    bands.append(area.multiply(lost.And(cover.gte(THRESHOLD))).rename("lossanyge30_m2"))
    to_isfr = lost.And(lossyear.lte(ISFR_LAST_LOSS_YEAR - 2000))
    for name, cond in (("ge10", cover.gte(10)), ("gt10", cover.gt(10)), ("ge40", cover.gte(40)), ("ge70", cover.gte(70))):
        bands.append(area.multiply(to_isfr.And(cond)).rename(f"lossto{ISFR_LAST_LOSS_YEAR}{name}_m2"))
    image = ee.Image.cat(bands)
    return image, image.bandNames().getInfo(), h.select("treecover2000").projection().getInfo()


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
    units, fc, record = eu.load_units(a.units, asset)
    print(f"{a.units}: n = {len(units):,} units ({dict(units['unit_level'].value_counts())}); asset {asset}")

    image, bands, grid = hansen_areas()
    if grid.get("crs") != GRID["crs"] or [float(v) for v in grid.get("transform", [])] != [float(v) for v in GRID["transform"]]:
        fail(f"{HANSEN}: its grid is {grid}, not {GRID} - the docstring and every area would be wrong")
    boxes = eu.box_tests(GRID, TEST_BOX)
    if abs(boxes["on_pixel_edges"]["relative_difference"]) > BOX_TOLERANCE:
        fail(f"a box on pixel edges sums to {boxes['on_pixel_edges']['earth_engine_m2']:,.2f} m2 in Earth Engine; on the ellipsoid it is "
             f"{boxes['on_pixel_edges']['ellipsoid_m2']:,.2f} m2 - pixel areas or the grid are not what the docstring says")
    stop_if_failed("checking the Hansen grid and the pixel areas")
    print(f"OK  a box on pixel edges: Earth Engine {boxes['on_pixel_edges']['earth_engine_m2']:,.2f} m2, ellipsoid {boxes['on_pixel_edges']['ellipsoid_m2']:,.2f} m2 "
          f"({boxes['on_pixel_edges']['relative_difference']:+.1e}). Moved half a pixel: {boxes['moved_half_a_pixel']['relative_difference']:+.1e}, "
          f"{boxes['moved_half_a_pixel']['shortfall_m2_per_cut_pixel']:.2f} m2 short per cut pixel")
    info = ee.data.getAsset(HANSEN)
    print(f"{HANSEN} (updated {info.get('updateTime', '')[:10]}): {len(bands)} area bands on its own grid, forest = treecover2000 > {THRESHOLD}")

    t0 = time.time()
    raw, status, cleanup = eu.zonal(image, bands, fc, units, f"{asset}_hansen_parts", f"{stem}_hansen", GRID, GROUPS, TILE_SCALE)
    m = units[["unit_id", "unit_level", "outside_village", "polygon_m2"]].merge(raw, on="unit_id", validate="one_to_one")
    ha = pd.DataFrame({c[:-3] + "_ha": m[c] / 1e4 for c in bands})
    ha.insert(0, "unit_id", m["unit_id"])
    tol = 1e-6                                                                    # hectares: 0.01 m2

    # ---- checks that need no outside figure ------------------------------------------------------------------
    by_band_year = {b: ha[[f"loss{y}{b}_ha" for y in YEARS]] for b in BANDS}
    band_loss = {b: by_band_year[b].sum(axis=1) for b in BANDS}
    eq0_year = ha[[f"loss{y}eq0_ha" for y in YEARS]]
    eq0_loss = eq0_year.sum(axis=1)
    if (ha["areaeq0_ha"] > ha["areale10_ha"] + tol).any() or (eq0_loss > band_loss["le10"] + tol).any() or (eq0_loss > ha["areaeq0_ha"] + tol).any():
        fail("land or loss at treecover2000 = 0 exceeds the le10 band it is part of, somewhere")
    year_sum = band_loss["gt30"]
    if (year_sum - ha["lossanygt30_ha"]).abs().max() > tol:
        fail(f"the 25 yearly losses in the gt30 band do not add up to its loss in any year: largest gap {(year_sum - ha['lossanygt30_ha']).abs().max():.6f} ha")
    if (sum(band_loss.values()) - ha["lossnomask_ha"]).abs().max() > tol:
        fail(f"the three bands' losses do not add up to the loss with no mask: largest gap {(sum(band_loss.values()) - ha['lossnomask_ha']).abs().max():.6f} ha")
    if (ha[[f"area{b}_ha" for b in BANDS]].sum(axis=1) - ha["area_ha"]).abs().max() > tol:
        fail("the three bands' land does not add up to the unit")
    if (ha["areagt30_ha"] - ha["forestgt30_ha"]).abs().max() > tol or (ha["areagt10le30_ha"] + ha["areagt30_ha"] - ha["forestgt10_ha"]).abs().max() > tol:
        fail("the band areas disagree with the threshold areas they should equal")
    nest = ["forestge10_ha", "forestgt10_ha", "forestge30_ha", "forestgt30_ha", "forestge40_ha", "forestge50_ha", "forestgt50_ha", "forestge70_ha"]
    for lower, higher in zip(nest, nest[1:]):
        if (ha[higher] > ha[lower] + tol).any():
            fail(f"{higher} exceeds {lower} in {int((ha[higher] > ha[lower] + tol).sum())} units - a stricter line cannot select more")
    if any((band_loss[b] > ha[f"area{b}_ha"] + tol).any() for b in BANDS) or (ha["forestge10_ha"] + ha["nodata_ha"] > ha["area_ha"] + tol).any():
        fail("loss exceeds the land of its band, or tree cover and no-data together exceed the unit, somewhere")
    area = eu.area_check(m)
    stop_if_failed("checking the zonal statistics")
    print(f"OK  {len(m):,} units returned, each once, no blank cell; yearly losses add up; the three bands add up to the unit and to unmasked loss; lines nest")
    print(f"OK  area summed over pixels {area['pixels_km2']:,.2f} km2 vs polygons on the ellipsoid {area['polygons_on_the_ellipsoid_km2']:,.2f} km2 "
          f"({area['relative_difference']:+.2e}). Per unit: median {area['per_unit_relative_difference']['median']:+.2e}, range "
          f"{area['per_unit_relative_difference']['min']:+.2e} to {area['per_unit_relative_difference']['max']:+.2e}; {area['units_more_than_1_per_cent_out']} more than 1% out, "
          f"none of those by more than {eu.UNIT_AREA_FLOOR_M2:g} m2")

    # ---- the per-unit tables -----------------------------------------------------------------------------------
    by_unit = pd.DataFrame({"unit_id": ha["unit_id"], "forest_ha": ha["forestgt30_ha"].round(4), "hansen_loss_ha": year_sum.round(4)})
    for y in YEARS:
        by_unit[f"hansen_loss_ha_{y}"] = ha[f"loss{y}gt30_ha"].round(4)
    by_unit["missing_data_share"] = (ha["nodata_ha"] / ha["area_ha"]).round(6)

    key = {"unit_id": m["unit_id"], "unit_level": m["unit_level"], "outside_village": m["outside_village"]}
    thr = pd.DataFrame({**key, "area_ha": ha["area_ha"].round(4), "polygon_area_ha": (m["polygon_m2"] / 1e4).round(4),
                        "water_ha": ha["water_ha"].round(4), "nodata_ha": ha["nodata_ha"].round(4),
                        "forest_ha_gt10": ha["forestgt10_ha"].round(4), "forest_ha_gt30": ha["forestgt30_ha"].round(4), "forest_ha_gt50": ha["forestgt50_ha"].round(4),
                        "forest_ha_ge10": ha["forestge10_ha"].round(4), "forest_ha_ge30": ha["forestge30_ha"].round(4), "forest_ha_ge50": ha["forestge50_ha"].round(4),
                        "hansen_loss_ha_gt10": (band_loss["gt10le30"] + band_loss["gt30"]).round(4), "hansen_loss_ha_gt30": year_sum.round(4),
                        "hansen_loss_ha_gt50": ha["lossanygt50_ha"].round(4), "hansen_loss_ha_ge30": ha["lossanyge30_ha"].round(4),
                        "hansen_loss_ha_any_cover": ha["lossnomask_ha"].round(4)})

    band_unit = pd.DataFrame(key)
    for b in BANDS:
        band_unit[f"area_ha_{b}"] = ha[f"area{b}_ha"].round(4)
    for b in BANDS:
        band_unit[f"loss_ha_{b}"] = band_loss[b].round(4)
    band_unit["loss_ha_any_cover"] = ha["lossnomask_ha"].round(4)
    band_unit["area_ha_eq0"] = ha["areaeq0_ha"].round(4)                           # of which, inside le10
    band_unit["loss_ha_eq0"] = eq0_loss.round(4)
    for b in BANDS:
        for y in YEARS:
            band_unit[f"loss_ha_{b}_{y}"] = ha[f"loss{y}{b}_ha"].round(4)

    # ---- the summaries -----------------------------------------------------------------------------------------
    level = m["unit_level"].to_numpy()
    groups = [("all units", np.ones(len(m), bool))] + [(k, level == k) for k in sorted(set(level))]
    all_loss_any = float(ha["lossnomask_ha"].sum())
    rows = []
    for name, sel in groups:
        group_loss = float(ha.loc[sel, "lossnomask_ha"].sum())
        for b, text in list(BANDS.items()) + [("any_cover", "all three bands"), ("eq0", "treecover2000 = 0 (part of le10, not a fourth band)")]:
            land = ha.loc[sel, "area_ha"] if b == "any_cover" else ha.loc[sel, f"area{b}_ha"]
            loss = ha.loc[sel, "lossnomask_ha"] if b == "any_cover" else eq0_loss[sel] if b == "eq0" else band_loss[b][sel]
            yearly = pd.concat([by_band_year[x].loc[sel] for x in BANDS], axis=1) if b == "any_cover" else eq0_year.loc[sel] if b == "eq0" else by_band_year[b].loc[sel]
            row = {"units": name, "n_units": int(sel.sum()), "canopy_band": b, "band_is": text, "land_km2": round(land.sum() / 100, 2),
                   "loss_km2_2001_2025": round(loss.sum() / 100, 2),
                   "share_of_these_units_loss_pct": round(100 * loss.sum() / group_loss, 2),
                   "share_of_all_units_loss_in_this_band_pct": round(100 * loss.sum() / (ha["lossnomask_ha"].sum() if b == "any_cover" else eq0_loss.sum() if b == "eq0" else band_loss[b].sum()), 2),
                   "loss_pct_of_band_land": round(100 * loss.sum() / land.sum(), 3), "units_with_land_in_band": int((land > 0).sum()),
                   "units_with_loss_in_band": int((loss > 0).sum())}
            for lo, hi in PERIODS:
                row[f"loss_km2_{lo}_{hi}"] = round(yearly[[c for c in yearly.columns if lo <= int(c[4:8]) <= hi]].sum().sum() / 100, 2)
            rows.append(row)
    band_summary = pd.DataFrame(rows)

    rows = []
    for name, sel in groups[1:] + groups[:1]:
        f, land = ha.loc[sel, "forestgt30_ha"].sum(), ha.loc[sel, "area_ha"].sum()
        row = {"unit_level": name, "n_units": int(sel.sum()), "area_km2": round(land / 100, 1), "forest_km2": round(f / 100, 1),
               "forest_share_of_area_pct": round(100 * f / land, 2), "units_with_any_forest": int((ha.loc[sel, "forestgt30_ha"] > 0).sum()),
               "units_with_no_forest": int((ha.loc[sel, "forestgt30_ha"] == 0).sum()),
               "units_with_under_1_ha_of_forest_including_none": int((ha.loc[sel, "forestgt30_ha"] < 1).sum()),
               "units_with_loss_in_the_mask": int((year_sum[sel] > 0).sum()), "units_with_loss_on_any_cover": int((ha.loc[sel, "lossnomask_ha"] > 0).sum()),
               "loss_km2_2001_2025": round(year_sum[sel].sum() / 100, 2), "loss_share_of_forest_pct": round(100 * year_sum[sel].sum() / f, 3)}
        for lo, hi in PERIODS:
            row[f"loss_km2_{lo}_{hi}"] = round(ha.loc[sel, [f"loss{y}gt30_ha" for y in range(lo, hi + 1)]].sum().sum() / 100, 2)
        for t in SENSITIVITY:
            row[f"forest_km2_gt{t}"] = round(ha.loc[sel, f"forestgt{t}_ha"].sum() / 100, 1)
        row["forest_km2_ge30"] = round(ha.loc[sel, "forestge30_ha"].sum() / 100, 1)
        row["loss_km2_2001_2025_any_cover"] = round(ha.loc[sel, "lossnomask_ha"].sum() / 100, 2)
        row["loss_outside_the_mask_pct_of_any_cover"] = round(100 * (1 - year_sum[sel].sum() / ha.loc[sel, "lossnomask_ha"].sum()), 2)
        row["units_with_loss_but_none_in_the_mask"] = int(((ha.loc[sel, "lossnomask_ha"] > 0) & (year_sum[sel] == 0)).sum())
        row["units_with_missing_data"] = int((ha.loc[sel, "nodata_ha"] > 0).sum())
        rows.append(row)
    by_level = pd.DataFrame(rows)
    everything = by_level.loc[by_level["unit_level"] == "all units"].iloc[0]
    by_level["share_of_all_area_pct"] = (100 * by_level["area_km2"] / everything["area_km2"]).round(2)
    by_level["share_of_all_forest_pct"] = (100 * by_level["forest_km2"] / everything["forest_km2"]).round(2)
    by_level["share_of_all_loss_pct"] = (100 * by_level["loss_km2_2001_2025"] / everything["loss_km2_2001_2025"]).round(2)
    by_level["share_of_all_loss_any_cover_pct"] = (100 * by_level["loss_km2_2001_2025_any_cover"] / everything["loss_km2_2001_2025_any_cover"]).round(2)

    # ---- beside the published totals ---------------------------------------------------------------------------
    total = ha.drop(columns="unit_id").sum()
    rec = []

    def beside(quantity, ours, theirs, source, unit, note=""):
        rec.append({"quantity": quantity, "this_pipeline": round(float(ours), 2), "published": theirs, "unit": unit,
                    "difference_pct_of_published": None if theirs is None else round(100 * (ours - theirs) / theirs, 2), "published_source": source, "note": note})

    like = "like for like: Global Forest Watch's figures count treecover2000 > T; the boundaries differ"
    worded = "as Global Forest Watch's notes word it (>=); its figures leave out pixels at exactly T, and the boundaries differ; not gated"
    beside("area measured", total["area_ha"], GFW_AREA_HA, GFW_SOURCE, "ha", "ours: the units; theirs: GADM 3.6")
    for t, theirs in GFW_EXTENT_2000_HA.items():
        beside(f"tree cover 2000, treecover2000 > {t}", total[f"forestgt{t}_ha"], theirs, GFW_SOURCE, "ha", like)
        beside(f"tree cover 2000, treecover2000 >= {t}", total[f"forestge{t}_ha"], theirs, GFW_SOURCE, "ha", worded)
        if abs(total[f"forestgt{t}_ha"] - theirs) / theirs > GFW_EXTENT_TOLERANCE:
            fail(f"tree cover 2000 above {t} is {total[f'forestgt{t}_ha']:,.0f} ha; Global Forest Watch publishes {theirs:,} ha for Odisha - more than {GFW_EXTENT_TOLERANCE:.0%} apart")
    gfw_loss = sum(GFW_LOSS_HA_30.values())
    ours_2001_2020 = sum(total[f"loss{y}gt30_ha"] for y in GFW_LOSS_HA_30)
    beside("tree cover loss 2001-2020, treecover2000 > 30", ours_2001_2020, gfw_loss, GFW_SOURCE, "ha", like)
    if abs(ours_2001_2020 - gfw_loss) / gfw_loss > GFW_LOSS_TOTAL_TOLERANCE:
        fail(f"tree cover loss 2001-2020 above 30 is {ours_2001_2020:,.0f} ha; Global Forest Watch publishes {gfw_loss:,} ha - more than {GFW_LOSS_TOTAL_TOLERANCE:.0%} apart")
    for y, theirs in GFW_LOSS_HA_30.items():
        beside(f"tree cover loss {y}, treecover2000 > 30", total[f"loss{y}gt30_ha"], theirs, GFW_SOURCE, "ha", "year by year, not gated; " + like)
    isfr = ISFR_2023_KM2
    dense = isfr["moderately_dense_forest_canopy_ge40_lt70"] + isfr["very_dense_forest_canopy_ge70"]
    for label, name, theirs in (("forest cover (ISFR: canopy density >= 10 per cent)", "ge10", isfr["total_forest_cover_canopy_ge10"]),
                                ("forest cover, read as > 10 per cent", "gt10", isfr["total_forest_cover_canopy_ge10"]),
                                ("moderately dense + very dense (ISFR: >= 40 per cent)", "ge40", dense),
                                ("very dense (ISFR: >= 70 per cent)", "ge70", isfr["very_dense_forest_canopy_ge70"])):
        beside(f"{label}: Hansen treecover2000 {name[:2].replace('ge', '>=').replace('gt', '>')} {name[2:]}, in 2000", total[f"forest{name}_ha"] / 100, round(theirs, 2), ISFR_SOURCE, "km2",
               "different sensor, definition and year - not expected to agree")
        beside(f"{label}: the same less loss to {ISFR_LAST_LOSS_YEAR}", (total[f"forest{name}_ha"] - total[f"lossto{ISFR_LAST_LOSS_YEAR}{name}_ha"]) / 100,
               round(theirs, 2), ISFR_SOURCE, "km2", "Hansen has no gain to add back, so this is a floor on its 2021 figure")
    stop_if_failed("setting the state totals beside Global Forest Watch's")
    recon = pd.DataFrame(rec)

    OUT.mkdir(exist_ok=True)
    tables = {"hansen_by_unit.csv": by_unit, "hansen_by_unit_thresholds.csv": thr, "hansen_loss_by_canopy_band_by_unit.csv": band_unit,
              "hansen_loss_by_canopy_band.csv": band_summary, "hansen_by_unit_level.csv": by_level, "hansen_reconciliation.csv": recon}
    for name, t in tables.items():
        t.to_csv(OUT / name, index=False)
    cleanup()                                           # the tables are on disk and checked; the group assets were scaffolding

    blank = lambda t: {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}
    with open(OUT / "hansen.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_build_hansen.py", "script_sha256": sha256(__file__), "helper": "scripts/_ee_units.py",
            "helper_sha256": sha256(Path(__file__).with_name("_ee_units.py")), "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                       {"earth_engine_asset": asset, "checked_against_the_layer_by": str(record.relative_to(ROOT))},
                       {"earth_engine_dataset": HANSEN, "update_time": info.get("updateTime"), "bands": ["treecover2000", "lossyear", "datamask"], "grid": grid}],
            "definitions": {
                "forest": f"treecover2000 > {THRESHOLD} (per cent canopy closure of vegetation taller than 5 m, year 2000); a fixed year-2000 mask",
                "forest_ha": "area of forest pixels inside the unit, hectares",
                "hansen_loss_ha_YYYY": "area of forest pixels inside the unit with lossyear = YYYY - 2000; loss outside the year-2000 forest mask is not counted",
                "hansen_loss_ha": "sum of 2001 to 2025; gross, with no gain netted off",
                "canopy_bands": BANDS | {"eq0": "treecover2000 = 0 (part of le10, carried as an 'of which')"},
                "missing_data_share": "area inside the unit with datamask 0, over the unit's area on the grid; datamask 2 (water) is not missing; open sea only, so zero for land units",
                "area": "ee.Image.pixelArea on Hansen's grid, each pixel weighted by the fraction of it inside the polygon (weighted sum reducer, reduceRegions); "
                        "Earth Engine's fraction for a cut pixel is approximate - see checks_passed.box_tests and area_summed_over_pixels_vs_polygons",
                "threshold": f"treecover2000 > {THRESHOLD} (ruling of 6 October 2026): the commoner written form, and what Global Forest Watch's published figures compute. "
                             f"Sensitivity per unit at > {SENSITIVITY[0]} and > {SENSITIVITY[1]}, and at >= {THRESHOLD}, in hansen_by_unit_thresholds.csv",
                "cautions": "loss is stand-replacing removal from any cause, not deforestation and not degradation under a canopy; 2011 onward was mapped with an updated method"},
            "earth_engine": {"project": project, "tasks": eu.task_record(status), "groups": GROUPS, "tile_scale": TILE_SCALE,
                             "batch_eecu_seconds_this_run": round(eu.eecu(status), 1), "seconds_waited": round(time.time() - t0)},
            "checks_passed": {"units_returned_each_once": int(len(m)), "yearly_losses_add_up": True, "bands_add_up_to_the_unit_and_to_unmasked_loss": True,
                              "lines_nest": True, "loss_within_its_band": True, "box_tests": boxes, "area_summed_over_pixels_vs_polygons": area,
                              "tree_cover_2000_gt_T_against_global_forest_watch_gated": {str(t): round(float((total[f'forestgt{t}_ha'] - v) / v), 5) for t, v in GFW_EXTENT_2000_HA.items()},
                              "tree_cover_2000_ge_T_against_global_forest_watch_not_gated": {str(t): round(float((total[f'forestge{t}_ha'] - v) / v), 5) for t, v in GFW_EXTENT_2000_HA.items()},
                              "loss_2001_2020_gt_30_against_global_forest_watch_gated": round(float((ours_2001_2020 - gfw_loss) / gfw_loss), 5),
                              "pixels_at_exactly_30": {"ha": round(float(total["forestge30_ha"] - total["forestgt30_ha"]), 1),
                                                       "share_of_forest_ge30": round(float(1 - total["forestgt30_ha"] / total["forestge30_ha"]), 5),
                                                       "loss_ha": round(float(total["lossanyge30_ha"] - total["lossanygt30_ha"]), 1)},
                              "loss_on_any_cover_ha": round(all_loss_any, 1), "loss_outside_the_mask_share": round(float(1 - year_sum.sum() / all_loss_any), 4),
                              "tolerances": {"box_on_pixel_edges": BOX_TOLERANCE, "gfw_extent": GFW_EXTENT_TOLERANCE, "gfw_loss_2001_2020": GFW_LOSS_TOTAL_TOLERANCE}},
            "published_figures": {"global_forest_watch": {"source": GFW_SOURCE, "area_ha": GFW_AREA_HA, "extent_2000_ha": GFW_EXTENT_2000_HA, "loss_ha_gt30": GFW_LOSS_HA_30},
                                  "isfr_2023": {"source": ISFR_SOURCE, "km2": ISFR_2023_KM2}},
            "tables": {name: {"rows": int(len(t)), "columns": int(len(t.columns)), "blank_cells": blank(t)} for name, t in tables.items()}
                      | {"hansen_by_unit.csv": {"rows": int(len(by_unit)), "columns": int(len(by_unit.columns)), "blank_cells": blank(by_unit),
                                                "units_with_forest": int((by_unit["forest_ha"] > 0).sum()), "units_with_loss_in_the_mask": int((by_unit["hansen_loss_ha"] > 0).sum()),
                                                "units_with_missing_data": int((by_unit["missing_data_share"] > 0).sum()),
                                                "largest_missing_data_share": float(by_unit["missing_data_share"].max())}},
            "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        }, fh, indent=2)

    print(f"\nhansen_by_unit.csv: n = {len(by_unit):,} units; blank cells {blank(by_unit) or 'none'}; with forest {int((by_unit['forest_ha'] > 0).sum()):,}; "
          f"with loss in the mask {int((by_unit['hansen_loss_ha'] > 0).sum()):,}; with missing data {int((by_unit['missing_data_share'] > 0).sum()):,}")
    print(f"\nhansen_by_unit_level.csv: n = {len(by_level)} rows (forest = treecover2000 > {THRESHOLD})")
    print(by_level.T.to_string(header=False))
    print(f"\nhansen_loss_by_canopy_band.csv: n = {len(band_summary)} rows")
    print(band_summary.drop(columns=["band_is"]).to_string(index=False))
    print(f"\nhansen_reconciliation.csv: n = {len(recon)} rows")
    for _, r in recon[~recon["quantity"].str.match(r"tree cover loss \d{4},")].iterrows():
        print(f"  {r['quantity']:<96} ours {r['this_pipeline']:>14,.1f}  published {r['published']:>14,.1f} {r['unit']:<3} ({r['difference_pct_of_published']:+.2f}%)")
    print(f"\nEarth Engine: {len(status)} batch tasks, {eu.eecu(status):,.0f} EECU-seconds; done. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
