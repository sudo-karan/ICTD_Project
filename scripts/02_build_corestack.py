#!/usr/bin/env python3
"""
Stage 1 - the CoRE Stack tree-change classes per analysis unit, and its tree mask.

    python scripts/02_build_corestack.py --units 10_units/units.gpkg

In : --units    the stage-0 layer and its Earth Engine table asset (see 02_upload_units_asset.py)
     projects/corestack-trees/assets/tree_characteristics/overall_change_2017_2023      image collection, band "constant"
     projects/corestack-datasets/assets/datasets/LULC_v3_river_basin/pan_india_lulc_v3_<Y>_<Y+1>   band "predicted_label"
     projects/corestack-datasets/assets/datasets/tree_health/overall_change_2017_2021   the producers' earlier product, for
                                                                                        one check against their own paper
     UMD/hansen/global_forest_change_2025_v1_13    band treecover2000, to split every class by year-2000 canopy
     FAO/GAUL/2015/level2                          the boundary of Mayurbhanj district, for that one check
Out: 20_degradation/ and nowhere else
     corestack_by_unit.csv           one row per unit, every unit, the outside_village ones included
     corestack_by_unit_bands.csv     per unit, every class by band of year-2000 canopy
     corestack_by_unit_level.csv     by unit type, by canopy band and by zone: the classes, their net, and intervals
     corestack_reconciliation.csv    what could be set beside a published figure, and what could not
     corestack.provenance.json       inputs, UTC run time, definitions, checks, n and missingness

WHAT THE SOURCE IS (from the producers' own code and paper; docs/DEGRADATION.md cites them).
overall_change_2017_2023 is a 25 m raster in eleven pieces, one per agro-climatic zone. Its values:
    -2  tree cover lost        there was tree cover in the first period and none in the second
    -1  degradation            tree cover in both; canopy cover density or canopy height fell a class
     0  no change              tree cover in both; neither changed class
     1  improvement            tree cover in both; density or height rose a class
     2  tree cover gained      none in the first period, tree cover in the second
     3  partially degraded     density rose a class, height fell
     4  partially degraded     density fell a class, height rose
     5  missing                the model produced no output in one of the periods
  (no value)                   outside the producers' tree mask in both periods - or a combination of changes
                               that their code sends to no value rather than to class 5
"Tree cover" is the producers' mask: LULC v3 class 6 ("trees and forest") together with Dynamic World's tree
class. Density and height are each a classifier's answer to "above or below this zone's median" (60 per cent
canopy density in the Eastern Plateau and Hills zone, 67 in the East Coast Plains and Hills), so "degradation"
means a pixel CROSSED A THRESHOLD, not that it lost a measured amount. Each "year" is the mode of three
agricultural years (July to June) around it: the product compares roughly 2016-2019 with 2022-2025. The
producers validated tree cover lost and nothing else; they state that no ground truth exists for the other
classes. Their classifiers were right about two times in three on held-out data.

WHICH CLASSES COUNT AS WHAT (a decision, stated):
  corestack_loss_ha                  class -2
  corestack_degradation_ha           class -1 ONLY
  corestack_partial_degradation_ha   classes 3 and 4 together, as the producers merge them. Kept OUT of
                                     corestack_degradation_ha: in each, one of density and height went up
                                     while the other went down, which is a mixed signal and not a decline.
                                     The column is there to be added by a reader who thinks otherwise.
  corestack_improvement_ha           class 1
  corestack_gain_ha                  class 2
  corestack_no_change_ha             class 0
  corestack_missing_ha               class 5
  corestack_no_value_ha              no value. Mostly land outside the tree mask in both periods; not missing data,
                                     and not proof of no trees (lulc_tree_both_no_value_ha is the part of it
                                     that LULC v3 calls trees in both of its years)
  corestack_net_degradation_ha       class -1 minus class 1 (see GROSS AND NET below)
  corestack_value_ha_zone_<zone>     the area with a value that comes from each zone's image
  corestack_tree_cover_start_ha      classes -2, -1, 0, 1, 3, 4, 5: tree cover in the first period
  corestack_tree_cover_end_ha        classes -1, 0, 1, 2, 3, 4, 5: tree cover in the second period
  corestack_missing_share            class 5 over all pixels that have a value
  lulc_tree_ha_<Y>                   area of LULC v3 class 6 in the agricultural year July <Y> to June <Y+1>
  ..._tc_gt10                        the same class on land with treecover2000 > 10 only (see below)

THE PRODUCT'S "TREE COVER" IS MUCH WIDER THAN FOREST. It covers about seven tenths of the units' area, and most
of class -2 and class 2 lies on land that had no Hansen canopy at all in 2000 - farmland whose label flips
between trees and crops. So every class is ALSO tallied by band of year-2000 canopy, exactly as in
02_build_hansen.py: eq0 (treecover2000 = 0), gt0le10, gt10le30, gt30. The columns ending _tc_gt10 are the
classes on land with treecover2000 > 10; that is the common reference on which this product is set beside
NIRv and Hansen. The plain columns are the product as its producers define it.

GROSS AND NET. Classes -1 and 1 come from classifiers that are right about two times in three, so some of
each is the same noise pointing in opposite directions. The summary therefore gives, beside the gross areas,
the net (class -1 minus class 1) and the downward share, class -1 / (class -1 + class 1), with an interval from
resampling units. A downward share of one half means no net signal. Improvement is the noise reference for
degradation.

HOW IT IS MEASURED. The change classes are summed on ONE 25 m grid - that of the Eastern Plateau and Hills
image, which covers most of the state. The other zones' images have the same pixel size and their origins sit
a whole number of pixels from it (checked at every run), so all of them lie on one lattice and nothing is
resampled. Where two zones' images both have a value the Eastern Plateau and Hills one is used, and the area
where that happens, and where the two disagree, is recorded. (The two zones use different thresholds, so a
class does not mean quite the same thing on either side of the line between them.) LULC v3 is summed on its own 10 m grid. As for Hansen, each
pixel counts for its area on the WGS84 ellipsoid and for the fraction of it inside the unit's polygon, and
every unit's area summed over pixels is gated against its polygon's. The producers count 625 m2 for every
25 m pixel; a pixel of this grid is smaller than that at Odisha's latitude, and the ratio is reported.

RECONCILIATION. The producers publish no total for 2017-2023 and none for Odisha as a state. They do print one
Odisha figure: Mayurbhanj district, 189 thousand hectares degraded between 2017 and 2021 (Goyal, Chauhan and
Seth, ICTD 2024). So the way this script reads their rasters - the legend, the mosaic of zones, the grid - is
tested on THEIR EARLIER PRODUCT, by THEIR OWN CONVENTION (a count of class -1 pixels times 625 m2), over
Mayurbhanj: the run stops unless that comes within MAYURBHANJ_TOLERANCE of 189 thousand hectares. The district
boundary is FAO GAUL's, since theirs is not published; that is what the tolerance is for. Nothing in the
2017-2023 tallies themselves can be gated against a published number. Also checked: every pixel is in exactly
one class; classes and the no-value area add up to the unit; the canopy bands add up to each class. LULC
class 6 is set beside the Forest Survey of India's forest cover, with which it is not expected to agree.

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

CHANGE = "projects/corestack-trees/assets/tree_characteristics/overall_change_2017_2023"
CHANGE_2017_2021 = "projects/corestack-datasets/assets/datasets/tree_health/overall_change_2017_2021"
HANSEN = "UMD/hansen/global_forest_change_2025_v1_13"
GAUL = "FAO/GAUL/2015/level2"
CANOPY = {"eq0": "treecover2000 = 0", "gt0le10": "0 < treecover2000 <= 10", "gt10le30": "10 < treecover2000 <= 30", "gt30": "treecover2000 > 30"}
REFERENCE = ("gt10le30", "gt30")                           # treecover2000 > 10: the land this product shares with the NIRv and Hansen columns
MAYURBHANJ_PUBLISHED_KHA = 189.0                           # Goyal, Chauhan & Seth (ICTD 2024): Mayurbhanj, degraded, AY2017 to AY2021, thousand hectares
MAYURBHANJ_TOLERANCE = 0.02                                # their district boundary is not published; FAO GAUL's is used
BOOTSTRAP = 2000
BOOTSTRAP_SEED = 20261006
LULC = "projects/corestack-datasets/assets/datasets/LULC_v3_river_basin/pan_india_lulc_v3_{y}_{y1}"
ZONES = ["CPAHR", "LGPR", "SPAHR", "ECPHR", "EPAHR"]      # the five whose footprints reach Odisha; the last is used first where two overlap
GRID_ZONE = "EPAHR"
MAIN_ZONES = ("EPAHR", "ECPHR")                            # Eastern Plateau and Hills; East Coast Plains and Hills
CLASSES = {-2: "lost", -1: "degradation", 0: "nochange", 1: "improvement", 2: "gained", 3: "partial3", 4: "partial4", 5: "missing"}
TREE_START = (-2, -1, 0, 1, 3, 4, 5)
TREE_END = (-1, 0, 1, 2, 3, 4, 5)
LULC_TREES = 6
LULC_YEARS = (2017, 2023)                                  # the two years the change product is named for
NOMINAL_PIXEL_M2 = 625.0                                   # the producers' own area per 25 m pixel
GROUPS = 8
TILE_SCALE = 4
ISFR_FOREST_COVER_KM2 = 52433.56                           # ISFR 2023, Vol. II, Table 10.20.2 (00_raw/05_forest_reference); imagery of October-December 2021


def change_image():
    """The mosaic of the zone images and one band of square metres per class, plus bookkeeping bands."""
    first = ee.Image(f"{CHANGE}/{GRID_ZONE}")
    proj = first.projection().getInfo()
    grid = {"crs": proj["crs"], "transform": proj["transform"]}
    zone_images = {z: ee.Image(f"{CHANGE}/{z}").select(0) for z in ZONES}
    sizes = {z: zone_images[z].projection().getInfo()["transform"] for z in ZONES}
    value = ee.ImageCollection([zone_images[z] for z in ZONES]).mosaic()        # later in the list wins: GRID_ZONE is last
    area = ee.Image.pixelArea()
    full = lambda image: image.unmask(0, False)                 # 0 wherever the image has nothing, footprint or no footprint
    cover = ee.Image(HANSEN).select("treecover2000").unmask(0)   # taken nearest-neighbour onto this grid
    in_band = {"eq0": cover.eq(0), "gt0le10": cover.gt(0).And(cover.lte(10)), "gt10le30": cover.gt(10).And(cover.lte(30)), "gt30": cover.gt(30)}
    has = full(value.mask().gt(0))
    bands = [area.rename("area_m2"), area.multiply(has.Not()).rename("novalue_m2")]
    known = ee.Image.constant(0)
    for code, name in CLASSES.items():
        is_class = full(value.eq(code))
        bands.append(area.multiply(is_class).rename(f"{name}_m2"))
        known = known.add(is_class)
        for b, cond in in_band.items():
            bands.append(area.multiply(is_class.And(cond)).rename(f"{name}_{b}_m2"))
    for b, cond in in_band.items():
        bands.append(area.multiply(cond).rename(f"land_{b}_m2"))
    for z in MAIN_ZONES:                                                                       # class by zone, where that zone's image is the one used
        used = full(zone_images[z].mask().gt(0)) if z == GRID_ZONE else full(zone_images[z].mask().gt(0)).And(full(zone_images[GRID_ZONE].mask().gt(0)).Not())
        for code, name in CLASSES.items():
            bands.append(area.multiply(used.And(full(value.eq(code)))).rename(f"{name}_zone{z}_m2"))
    bands.append(area.multiply(has.And(known.eq(0))).rename("othervalue_m2"))                  # a value outside the legend: must be nothing
    n_zones = ee.Image.constant(0)
    for z in ZONES:
        present = full(zone_images[z].mask().gt(0))
        bands.append(area.multiply(present).rename(f"zone{z}_m2"))
        n_zones = n_zones.add(present)
    a, b = zone_images["ECPHR"], zone_images[GRID_ZONE]
    both = full(a.mask().gt(0)).And(full(b.mask().gt(0)))
    bands.append(area.multiply(n_zones.gte(2)).rename("twozones_m2"))
    bands.append(area.multiply(both.And(full(a.neq(b)))).rename("twozonesdiffer_m2"))
    bands.append(has.rename("pixels"))                                                         # the producers' unit: a count of pixels
    image = ee.Image.cat(bands)
    return image, image.bandNames().getInfo(), grid, sizes


def mayurbhanj_check(grid):
    """Class -1 of the producers' 2017-2021 product over Mayurbhanj, counted their way: whole pixels x 625 m2."""
    district = ee.FeatureCollection(GAUL).filter(ee.Filter.And(ee.Filter.eq("ADM1_NAME", "Orissa"), ee.Filter.eq("ADM2_NAME", "Mayurbhanj")))
    if district.size().getInfo() != 1:
        fail(f"{GAUL}: expected exactly one district named Mayurbhanj in Orissa")
        return {"class_minus1_thousand_ha_at_625_m2": float("nan")}
    out = {"boundary": f"{GAUL}, ADM1_NAME Orissa, ADM2_NAME Mayurbhanj", "published": "Goyal, Chauhan and Seth (ICTD 2024): Mayurbhanj 189 kha degraded, AY2017 to AY2021"}
    for key_, cid in (("class_minus1_thousand_ha_at_625_m2", CHANGE_2017_2021), ("class_minus1_thousand_ha_2017_2023", CHANGE)):
        value = ee.ImageCollection(cid).mosaic()
        hist = value.reduceRegion(ee.Reducer.frequencyHistogram().unweighted(), district.geometry(), crs=grid["crs"], crsTransform=grid["transform"], maxPixels=int(1e9), tileScale=8).getInfo()
        counts = {int(float(k)): v for k, v in list(hist.values())[0].items() if k != "null"}
        out[key_] = counts.get(-1, 0) * NOMINAL_PIXEL_M2 / 1e7
        out[key_.replace("class_minus1_thousand_ha", "pixels_by_class")] = {str(k): int(v) for k, v in sorted(counts.items())}
    return out


def lulc_image():
    first = ee.Image(LULC.format(y=LULC_YEARS[0], y1=LULC_YEARS[0] + 1)).select("predicted_label")
    proj = first.projection().getInfo()
    grid = {"crs": proj["crs"], "transform": proj["transform"]}
    area = ee.Image.pixelArea()
    bands = [area.rename("area_m2")]
    for y in LULC_YEARS:
        label = ee.Image(LULC.format(y=y, y1=y + 1)).select("predicted_label")
        this = label.projection().getInfo()
        if this["crs"] != grid["crs"] or [float(v) for v in this["transform"]] != [float(v) for v in grid["transform"]]:
            fail(f"LULC v3 {y}: its grid {this} differs from {LULC_YEARS[0]}'s {grid}")
        bands.append(area.multiply(label.round().eq(LULC_TREES).unmask(0, False)).rename(f"tree{y}_m2"))
        bands.append(area.multiply(label.mask().gt(0).unmask(0, False)).rename(f"label{y}_m2"))
    both = ee.Image.constant(1)
    for y in LULC_YEARS:
        both = both.And(ee.Image(LULC.format(y=y, y1=y + 1)).select("predicted_label").round().eq(LULC_TREES).unmask(0, False))
    change_has_value = ee.ImageCollection([ee.Image(f"{CHANGE}/{z}").select(0) for z in ZONES]).mosaic().mask().gt(0).unmask(0, False)   # taken nearest-neighbour onto the 10 m grid
    bands.append(area.multiply(both.And(change_has_value.Not())).rename("treeboth_novalue_m2"))
    image = ee.Image.cat(bands)
    return image, image.bandNames().getInfo(), grid


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
    key = ["unit_id", "unit_level", "outside_village", "polygon_m2"]

    # ---- the change classes, on the 25 m grid --------------------------------------------------------------------
    image, bands, grid, sizes = change_image()
    step = float(grid["transform"][0])
    if any(abs(float(t[0]) - step) > 1e-15 or abs(float(t[4]) + step) > 1e-15 for t in sizes.values()):
        fail(f"the zone images do not share one pixel size: {sizes}")
    stop_if_failed("reading the change product's grids")
    off = lambda v: abs(v - round(v))                                       # how far an origin sits from a whole number of pixels
    offsets = {z: {"x_pixels": float(f"{off((float(t[2]) - float(grid['transform'][2])) / step):.2e}"), "y_pixels": float(f"{off((float(t[5]) - float(grid['transform'][5])) / step):.2e}")}
               for z, t in sizes.items()}
    if max(max(o_.values()) for o_ in offsets.values()) > 1e-3:
        fail(f"the zone images are not on one lattice: origins sit {offsets} of a pixel from whole pixels of the {GRID_ZONE} grid - they would have to be resampled")
    n_images = ee.ImageCollection(CHANGE).size().getInfo()
    stop_if_failed("checking that the zone images share one lattice")
    print(f"{CHANGE}: {n_images} zone images; summed on the {GRID_ZONE} grid, pixel {step:.14f} deg; the other zones' origins sit a whole number of pixels from it "
          f"(to within {max(max(o_.values()) for o_ in offsets.values()):.0e} of a pixel), so nothing is resampled")
    mayurbhanj = mayurbhanj_check(grid)
    if abs(mayurbhanj["class_minus1_thousand_ha_at_625_m2"] - MAYURBHANJ_PUBLISHED_KHA) / MAYURBHANJ_PUBLISHED_KHA > MAYURBHANJ_TOLERANCE:
        fail(f"the producers' 2017-2021 product, read as this script reads it, gives {mayurbhanj['class_minus1_thousand_ha_at_625_m2']:,.1f} thousand ha of class -1 in Mayurbhanj; "
             f"their paper prints {MAYURBHANJ_PUBLISHED_KHA:g} - the legend, the mosaic or the grid is being misread")
    stop_if_failed("reconciling to the producers' published Mayurbhanj figure")
    print(f"OK  the producers' 2017-2021 product, read the same way, their convention, Mayurbhanj (GAUL boundary): class -1 = {mayurbhanj['class_minus1_thousand_ha_at_625_m2']:,.1f} thousand ha; "
          f"they publish {MAYURBHANJ_PUBLISHED_KHA:g} (tolerance {MAYURBHANJ_TOLERANCE:.0%}). The same tally on 2017-2023: {mayurbhanj['class_minus1_thousand_ha_2017_2023']:,.1f}")
    t0 = time.time()
    raw, status_change, cleanup_change = eu.zonal(image, bands, fc, units, f"{asset}_corestack_change_parts", f"{stem}_corestack_change", grid, GROUPS, TILE_SCALE)
    m = units[key].merge(raw, on="unit_id", validate="one_to_one")
    tol = 0.01                                                              # m2
    names = list(CLASSES.values())
    if m["othervalue_m2"].max() > tol:
        fail(f"{CHANGE}: {m['othervalue_m2'].sum() / 1e4:,.2f} ha carries a value outside the legend {sorted(CLASSES)}")
    if (m[[f"{n}_m2" for n in names]].sum(axis=1) + m["novalue_m2"] + m["othervalue_m2"] - m["area_m2"]).abs().max() > 1.0:
        fail("the classes and the no-value area do not add up to the unit, somewhere")
    area_change = eu.area_check(m)
    stop_if_failed("checking the change classes")
    valued = m[[f"{n}_m2" for n in names]].sum(axis=1)
    pixel_m2 = float(valued.sum() / m["pixels"].sum())
    print(f"OK  every unit returned; no value outside the legend; classes + no value = unit; area summed over pixels {area_change['pixels_km2']:,.2f} km2 vs polygons "
          f"{area_change['polygons_on_the_ellipsoid_km2']:,.2f} ({area_change['relative_difference']:+.2e})")
    print(f"    a pixel with a value is {pixel_m2:,.2f} m2 on average here; the producers count {NOMINAL_PIXEL_M2:g} m2, {NOMINAL_PIXEL_M2 / pixel_m2 - 1:+.1%}")
    print("    area by zone image, km2: " + ", ".join(f"{z} {m[f'zone{z}_m2'].sum() / 1e6:,.1f}" for z in ZONES)
          + f"; two zones both have a value on {m['twozones_m2'].sum() / 1e6:,.2f} km2, and ECPHR and {GRID_ZONE} differ on {m['twozonesdiffer_m2'].sum() / 1e6:,.2f} km2 of it")

    # ---- the tree mask, on LULC v3's own 10 m grid ---------------------------------------------------------------
    limage, lbands, lgrid = lulc_image()
    stop_if_failed("reading the LULC v3 grids")
    print(f"LULC v3: years {list(LULC_YEARS)}, class {LULC_TREES}, on its own grid, pixel {float(lgrid['transform'][0]):.14f} deg")
    lraw, status_lulc, cleanup_lulc = eu.zonal(limage, lbands, fc, units, f"{asset}_corestack_lulc_parts", f"{stem}_corestack_lulc", lgrid, GROUPS, TILE_SCALE)
    lm = units[key].merge(lraw, on="unit_id", validate="one_to_one")
    area_lulc = eu.area_check(lm)
    for y in LULC_YEARS:
        if (lm[f"tree{y}_m2"] > lm[f"label{y}_m2"] + tol).any() or (lm[f"label{y}_m2"] > lm["area_m2"] + tol).any():
            fail(f"LULC v3 {y}: trees exceed labelled land, or labelled land exceeds the unit, somewhere")
    stop_if_failed("checking the LULC tallies")
    print(f"OK  LULC: area summed over pixels {area_lulc['pixels_km2']:,.2f} km2 vs polygons {area_lulc['polygons_on_the_ellipsoid_km2']:,.2f} ({area_lulc['relative_difference']:+.2e})")

    # ---- the per-unit tables -------------------------------------------------------------------------------------
    names_by_code = dict(CLASSES)
    for name in names:                                  # each class must be the sum of its four canopy bands
        if (m[[f"{name}_{b}_m2" for b in CANOPY]].sum(axis=1) - m[f"{name}_m2"]).abs().max() > 1.0:
            fail(f"class {name}: its canopy bands do not add up to it")
    if (m[[f"land_{b}_m2" for b in CANOPY]].sum(axis=1) - m["area_m2"]).abs().max() > 1.0:
        fail("the canopy bands' land does not add up to the unit")
    stop_if_failed("checking the canopy bands")
    ha = lambda col: m[col] / 1e4
    cls = {code: ha(f"{name}_m2") for code, name in CLASSES.items()}
    ref = {code: sum(ha(f"{name}_{b}_m2") for b in REFERENCE) for code, name in CLASSES.items()}       # on treecover2000 > 10
    out = pd.DataFrame({"unit_id": m["unit_id"], "unit_level": m["unit_level"], "outside_village": m["outside_village"],
                        "area_ha": ha("area_m2").round(4),
                        "corestack_loss_ha": cls[-2].round(4), "corestack_degradation_ha": cls[-1].round(4),
                        "corestack_partial_degradation_ha": (cls[3] + cls[4]).round(4),
                        "corestack_improvement_ha": cls[1].round(4), "corestack_gain_ha": cls[2].round(4),
                        "corestack_no_change_ha": cls[0].round(4), "corestack_missing_ha": cls[5].round(4),
                        "corestack_no_value_ha": ha("novalue_m2").round(4),
                        "corestack_tree_cover_start_ha": sum(cls[c] for c in TREE_START).round(4),
                        "corestack_tree_cover_end_ha": sum(cls[c] for c in TREE_END).round(4),
                        "corestack_partial_density_up_height_down_ha": cls[3].round(4), "corestack_partial_density_down_height_up_ha": cls[4].round(4)})
    with_value = sum(cls.values())
    out["corestack_missing_share"] = (cls[5] / with_value.where(with_value > 0)).round(6)
    out["corestack_net_degradation_ha"] = (cls[-1] - cls[1]).round(4)
    for z in MAIN_ZONES:
        out[f"corestack_value_ha_zone_{z}"] = sum(ha(f"{name}_zone{z}_m2") for name in names).round(4)
    out["land_tc_gt10_ha"] = sum(ha(f"land_{b}_m2") for b in REFERENCE).round(4)
    out["corestack_loss_ha_tc_gt10"] = ref[-2].round(4)
    out["corestack_degradation_ha_tc_gt10"] = ref[-1].round(4)
    out["corestack_partial_degradation_ha_tc_gt10"] = (ref[3] + ref[4]).round(4)
    out["corestack_improvement_ha_tc_gt10"] = ref[1].round(4)
    out["corestack_gain_ha_tc_gt10"] = ref[2].round(4)
    out["corestack_no_change_ha_tc_gt10"] = ref[0].round(4)
    out["corestack_tree_cover_start_ha_tc_gt10"] = sum(ref[c] for c in TREE_START).round(4)
    out["corestack_net_degradation_ha_tc_gt10"] = (ref[-1] - ref[1]).round(4)
    for y in LULC_YEARS:
        out[f"lulc_tree_ha_{y}"] = (lm[f"tree{y}_m2"] / 1e4).round(4).to_numpy()
    out["lulc_area_ha"] = (lm["area_m2"] / 1e4).round(4).to_numpy()
    out["lulc_tree_both_no_value_ha"] = (lm["treeboth_novalue_m2"] / 1e4).round(4).to_numpy()

    wide = pd.DataFrame({"unit_id": m["unit_id"], "unit_level": m["unit_level"], "outside_village": m["outside_village"]})
    for b in CANOPY:
        wide[f"land_ha_{b}"] = ha(f"land_{b}_m2").round(4)
    for code, name in CLASSES.items():
        for b in CANOPY:
            wide[f"class_{name}_ha_{b}"] = ha(f"{name}_{b}_m2").round(4)
    for z in MAIN_ZONES:
        wide[f"value_ha_zone_{z}"] = sum(ha(f"{name}_zone{z}_m2") for name in names).round(4)

    # ---- the summary: by unit type, by canopy band, by zone; gross, net, and the downward share with an interval ----
    level = m["unit_level"].to_numpy()
    groups = [("all units", np.ones(len(m), bool))] + [(k, level == k) for k in sorted(set(level))]
    strata = {"all land": list(CANOPY), "treecover2000 > 10": list(REFERENCE), **{CANOPY[b]: [b] for b in CANOPY}}
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    def summary(label_units, sel, label_land, cols_of):
        """cols_of(name) -> the m2 columns of class `name` in this stratum."""
        idx = np.flatnonzero(sel)
        a = {code: m.loc[sel, cols_of(name)].sum(axis=1).to_numpy() for code, name in CLASSES.items()}
        tot = {code: float(v.sum()) / 1e6 for code, v in a.items()}
        start = sum(tot[c] for c in TREE_START)
        row = {"units": label_units, "n_units": int(len(idx)), "land": label_land,
               "tree_cover_start_km2": round(start, 2), "loss_km2": round(tot[-2], 2), "degradation_km2": round(tot[-1], 2), "partial_degradation_km2": round(tot[3] + tot[4], 2),
               "improvement_km2": round(tot[1], 2), "gain_km2": round(tot[2], 2), "no_change_km2": round(tot[0], 2), "missing_km2": round(tot[5], 3)}
        for label, c in (("loss", -2), ("degradation", -1), ("improvement", 1)):
            row[f"{label}_pct_of_tree_cover_start"] = round(100 * tot[c] / start, 2) if start else None
        row["net_degradation_km2"] = round(tot[-1] - tot[1], 2)                       # class -1 minus class 1
        both = tot[-1] + tot[1]
        row["downward_share"] = round(tot[-1] / both, 4) if both else None            # 0.5 = no net signal
        if both and len(idx) > 1:
            draws = rng.integers(0, len(idx), size=(BOOTSTRAP, len(idx)))
            d, u = a[-1][draws].sum(axis=1), a[1][draws].sum(axis=1)
            share = d / np.where(d + u > 0, d + u, np.nan)
            row["downward_share_lo_95"], row["downward_share_hi_95"] = (round(float(v), 4) for v in np.nanpercentile(share, [2.5, 97.5]))
        else:
            row["downward_share_lo_95"] = row["downward_share_hi_95"] = None
        row["units_with_degradation"] = int((a[-1] > 0).sum())
        return row

    rows = []
    for gname, sel in groups:
        for lname, members in strata.items():
            r = summary(gname, sel, lname, lambda name, members=members: [f"{name}_{b}_m2" for b in members])
            r["land_km2"] = round(sum(m.loc[sel, f"land_{b}_m2"].sum() for b in members) / 1e6, 2)
            rows.append(r)
        for z in MAIN_ZONES:
            r = summary(gname, sel, f"zone {z}, all land", lambda name, z=z: [f"{name}_zone{z}_m2"])
            r["land_km2"] = None
            rows.append(r)
    by_level = pd.DataFrame(rows)
    first = ["units", "n_units", "land", "land_km2"]
    by_level = by_level[first + [c for c in by_level.columns if c not in first]]
    lulc_rows = {g: {y: float(lm.loc[sel, f"tree{y}_m2"].sum() / 1e6) for y in LULC_YEARS} | {"area": float(lm.loc[sel, "area_m2"].sum() / 1e6)} for g, sel in groups}

    total = out.drop(columns=["unit_id", "unit_level", "outside_village"]).sum()
    rec = [
        {"quantity": "class -1, Mayurbhanj district, the producers' 2017-2021 product, counted their way (pixels x 625 m2)",
         "this_pipeline": round(mayurbhanj["class_minus1_thousand_ha_at_625_m2"], 1), "published": MAYURBHANJ_PUBLISHED_KHA, "unit": "thousand ha",
         "note": f"GATED at {MAYURBHANJ_TOLERANCE:.0%}. Published in Goyal, Chauhan and Seth (ICTD 2024). It tests how this script reads the producers' rasters; the boundary is FAO GAUL's, theirs is not published"},
        {"quantity": "any class of overall_change_2017_2023, Odisha", "this_pipeline": None, "published": None, "unit": "",
         "note": "NOT RECONCILED: the producers publish no total for 2017-2023 and none for Odisha; their Table 5 is per agro-climatic zone for 2017-2021"},
        {"quantity": "area per pixel with a value", "this_pipeline": round(pixel_m2, 2), "published": NOMINAL_PIXEL_M2, "unit": "m2",
         "note": "the producers multiply a pixel count by 625 m2; on the ellipsoid a pixel of this grid is smaller at Odisha's latitude, so their convention would give "
                 f"{NOMINAL_PIXEL_M2 / pixel_m2 - 1:+.1%} more area from the same pixels"},
    ]
    for y in LULC_YEARS:
        rec.append({"quantity": f"LULC v3 class 6 (trees and forest), July {y} - June {y + 1}, over the units", "this_pipeline": round(float(total[f'lulc_tree_ha_{y}']) / 100, 1),
                    "published": ISFR_FOREST_COVER_KM2, "unit": "km2",
                    "note": "beside the Forest Survey of India's forest cover (ISFR 2023; canopy density of 10 per cent and more on a hectare and more, imagery of October-December 2021). "
                            "NOT expected to agree: LULC class 6 is any pixel a 10 m classifier calls trees, orchards and trees on farms included"})
    recon = pd.DataFrame(rec)
    recon["difference_pct_of_published"] = [None if pd.isna(a_) or pd.isna(b_) else round(100 * (a_ - b_) / b_, 1) for a_, b_ in zip(recon["this_pipeline"], recon["published"])]

    OUT.mkdir(exist_ok=True)
    tables = {"corestack_by_unit.csv": out, "corestack_by_unit_bands.csv": wide, "corestack_by_unit_level.csv": by_level, "corestack_reconciliation.csv": recon}
    for name, t in tables.items():
        t.to_csv(OUT / name, index=False)
    cleanup_change()
    cleanup_lulc()

    blank = lambda t: {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}
    info = ee.data.getAsset(CHANGE)
    with open(OUT / "corestack.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_build_corestack.py", "script_sha256": sha256(__file__), "helper": "scripts/_ee_units.py",
            "helper_sha256": sha256(Path(__file__).with_name("_ee_units.py")), "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                       {"earth_engine_asset": asset, "checked_against_the_layer_by": str(record.relative_to(ROOT))},
                       {"earth_engine_dataset": CHANGE, "update_time": info.get("updateTime"), "zone_images_in_the_collection": n_images, "zone_images_used": ZONES,
                        "grid": grid, "other_zones_origin_distance_from_a_whole_pixel": offsets},
                       {"earth_engine_dataset": [LULC.format(y=y, y1=y + 1) for y in LULC_YEARS], "band": "predicted_label", "class": LULC_TREES, "grid": lgrid},
                       {"earth_engine_dataset": HANSEN, "band": "treecover2000", "use": "the canopy bands, taken nearest-neighbour onto the 25 m grid"},
                       {"earth_engine_dataset": CHANGE_2017_2021, "use": "the Mayurbhanj check only"}, {"earth_engine_dataset": GAUL, "use": "the Mayurbhanj boundary only"}],
            "definitions": {
                "classes": {str(k): v for k, v in CLASSES.items()},
                "corestack_loss_ha": "class -2", "corestack_degradation_ha": "class -1 only", "corestack_partial_degradation_ha": "classes 3 + 4, not in corestack_degradation_ha",
                "corestack_improvement_ha": "class 1", "corestack_gain_ha": "class 2", "corestack_no_change_ha": "class 0", "corestack_missing_ha": "class 5",
                "corestack_no_value_ha": "no value in any zone image: mostly outside the producers' tree mask in both periods; not missing data and not proof of no trees",
                "lulc_tree_both_no_value_ha": "land with no value in the change product that LULC v3 calls class 6 in both of its years here",
                "corestack_tree_cover_start_ha": f"classes {list(TREE_START)}", "corestack_tree_cover_end_ha": f"classes {list(TREE_END)}",
                "corestack_missing_share": "class 5 over all pixels with a value; blank where the unit has none",
                "lulc_tree_ha_Y": f"LULC v3 predicted_label = {LULC_TREES}, July Y to June Y+1, on its own 10 m grid",
                "canopy_bands": CANOPY, "_tc_gt10": "the class on land with treecover2000 > 10 (bands gt10le30 and gt30)",
                "net_degradation": "class -1 minus class 1", "downward_share": f"class -1 / (class -1 + class 1); 0.5 means no net signal; interval from {BOOTSTRAP} resamples of units",
                "area": "ee.Image.pixelArea on the grid named above, each pixel weighted by the fraction of it inside the polygon",
                "cautions": "degradation and improvement are crossings of a zone-specific threshold by a classifier that is right about two times in three; only class -2 was "
                            "validated by the producers; each 'year' is a three-year mode; the two zones have different thresholds"},
            "earth_engine": {"project": project, "tasks": eu.task_record(status_change) | eu.task_record(status_lulc), "groups": GROUPS, "tile_scale": TILE_SCALE,
                             "batch_eecu_seconds_change": round(eu.eecu(status_change), 1), "batch_eecu_seconds_lulc": round(eu.eecu(status_lulc), 1), "seconds_waited": round(time.time() - t0)},
            "checks_passed": {"units_returned_each_once": int(len(m)), "no_value_outside_the_legend": True, "classes_and_no_value_add_up_to_the_unit": True,
                              "area_summed_over_pixels_vs_polygons_change_grid": area_change, "area_summed_over_pixels_vs_polygons_lulc_grid": area_lulc,
                              "mean_m2_per_pixel_with_a_value": pixel_m2, "producers_nominal_m2_per_pixel": NOMINAL_PIXEL_M2,
                              "km2_by_zone_image": {z: round(float(m[f"zone{z}_m2"].sum() / 1e6), 2) for z in ZONES},
                              "km2_where_two_zone_images_have_a_value": round(float(m["twozones_m2"].sum() / 1e6), 3),
                              "km2_where_ECPHR_and_EPAHR_differ": round(float(m["twozonesdiffer_m2"].sum() / 1e6), 3),
                              "mayurbhanj_2017_2021_against_the_producers_paper": mayurbhanj | {"published_thousand_ha": MAYURBHANJ_PUBLISHED_KHA, "tolerance": MAYURBHANJ_TOLERANCE},
                              "canopy_bands_add_up_to_each_class": True,
                              "lulc_class_6_km2": {g: {str(k): round(v, 1) for k, v in r.items()} for g, r in lulc_rows.items()},
                              "not_reconciled": "no producer total exists for 2017-2023 or for Odisha as a state"},
            "tables": {name: {"rows": int(len(t)), "columns": int(len(t.columns)), "blank_cells": blank(t)} for name, t in tables.items()},
            "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        }, fh, indent=2)

    print(f"\ncorestack_by_unit.csv: n = {len(out):,} units; blank cells {blank(out) or 'none'}")
    pd.set_option("display.width", 260)
    print(f"\ncorestack_by_unit_level.csv: n = {len(by_level)} rows")
    print(by_level.drop(columns=["n_units", "missing_km2", "no_change_km2", "units_with_degradation"]).to_string(index=False))
    print("\nLULC v3 class 6, km2: " + "; ".join(f"{g}: " + ", ".join(f"{y} {r[y]:,.0f} ({100 * r[y] / r['area']:.1f} % of area)" for y in LULC_YEARS) for g, r in lulc_rows.items()))
    print(f"\ncorestack_reconciliation.csv: n = {len(recon)} rows")
    print(recon.drop(columns=["note"]).to_string(index=False))
    print(f"\nEarth Engine: change {eu.eecu(status_change):,.0f} EECU-seconds, LULC {eu.eecu(status_lulc):,.0f}; done. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
