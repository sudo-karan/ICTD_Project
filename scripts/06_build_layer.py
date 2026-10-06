#!/usr/bin/env python3
"""
The demo layer - one offline map of what stages 1, 2 and 3 hold, for every unit.

    python scripts/06_build_layer.py --units 10_units/units.gpkg

In : --units                                       the stage-0 layer: geometry, names, unit type, district of the lgd_panchayat units
     10_units/outside_village_district.csv         the district of each outside_village unit (01_assign_outside_district.py)
     10_units/units.provenance.json                the layer's own counts (the villages that belong to no unit)
     00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv   district names beside their Census-2011 codes
     20_degradation/degradation_by_unit.csv        stage 1: Hansen, the canopy bands, CoRE Stack (NIRv pending)
     20_degradation/corestack_by_unit_bands.csv    stage 1: every CoRE Stack class by band of year-2000 canopy - the six classes
                                                   on land with treecover2000 > 10, and their shares, all from this one table
     20_degradation/agreement_by_unit.csv          stage 1: the two-measure agreement class and its two rates
     20_degradation/hansen_by_unit_level.csv, forest_floor_options.csv, agreement.provenance.json   their own counts, checked against
     30_need/need_by_unit.csv                      stage 2: Census 2011 counts, st_share, sc_share, adi_2011
     40_allocation/allocation_by_unit.csv          stage 3: MGNREGA works geotagged inside each unit, and their expenditure
     scripts/vendor/leaflet-1.9.4/, scripts/layer_template.html   the map library (embedded) and the page
Out: 60_layer/ and nowhere else
     index.html              the map: open it from disk. Self-contained - it makes no network request
     data.js                 its data: the simplified unit shapes, every displayed figure, every class. Keep it beside index.html
     layer_by_unit.csv       THE FIGURES THE MAP SHOWS, one row per unit, as numbers: each popup figure is a cell of this table
     layer.provenance.json   inputs, UTC run time, the simplification and its area error, classes, checks, n and missingness

WHO IT IS FOR. The Foundation for Ecological Security, who will open it and look. It needs no stage 4 and no NIRv.

EVERY FIGURE IN A POPUP IS A CELL OF A STAGE OUTPUT. Areas, counts and rupees are copied from the stage tables.
Shares and rupees in lakh are computed HERE, written to layer_by_unit.csv, and the page shows that cell as text:
the page's JavaScript looks values up and computes nothing. scripts/verify_layer.py rebuilds every displayed
string from the stage tables independently.

HONEST COLOUR.
  - A rate on a few hectares of forest is noise (forest_floor_repeatability.csv gives, by forest area, the rank
    correlation of a unit's Hansen loss rate between odd and even years; the page quotes it from that table).
    So on every layer that is a rate on forest land, a unit below a minimum of that land is drawn in one flat
    colour, "insufficient forest to assess" - never on the colour scale. The page offers two minimums: 50 ha (the
    floor proposed for stage 4; the default) and 1 ha (every unit with measurable forest). The agreement class has
    its own floor, fixed where 02_build_agreement.py set it.
  - The outside_village units have no census rows. On the two census layers they are "no census data for this
    land" - a class of its own, never blank and never zero.
  - Every class is listed in the legend with the number of units in it.
  - No SHRUG-derived column is in the layer (poverty_rate and its companions): SHRUG is CC BY-NC-SA 4.0, and a
    shared file that carried its estimates could become a derived work under that licence. They stay in
    30_need/need_by_unit.csv for the analysis.

THE LAYERS (id: what is drawn; the land it must have to be assessed)
  forest_area               forest (treecover2000 > 30) as a share of the unit's area
  hansen_loss               Hansen loss 2001-2025 as a share of that forest; needs forest
  canopy_band_loss          Hansen loss 2001-2025 on land with 10 < treecover2000 <= 30, as a share of that land - the
                            band Hansen's mask leaves out; needs land in that band
  corestack_degradation     CoRE Stack class -1 as a share of the land with a class, on treecover2000 > 10; needs that land
  corestack_net             class -1 minus class 1, the same share; needs that land
  agreement                 the two-measure agreement class of agreement_by_unit.csv (its own floor)
  allocation                expenditure on all MGNREGA works geotagged inside the unit, rupees lakh
  forest_named_expenditure  the same for works whose work type names forest or forestry
  st_share, adi_2011        Census 2011
  nirv                      listed, not built: pending

GEOMETRY. The 11,468 unit polygons are a valid coverage (no gaps or overlaps between neighbours). They are
simplified as a coverage - shared edges stay shared - with a tolerance of SIMPLIFY_M metres in UTM zone 45N, and
stored to 0.00001 degree. The record gives what that does to each unit's area; the areas the map PRINTS are the
layer's own, not the simplified shapes'. District outlines are the dissolved simplified units.

Needs geopandas, shapely (2.1 or later, with GEOS 3.12 or later, for coverage_simplify), pyproj, pandas, numpy.
"""
import argparse, datetime, hashlib, json, re, sys, zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from pyproj import Geod

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "60_layer"
VENDOR = Path(__file__).resolve().parent / "vendor" / "leaflet-1.9.4"
TEMPLATE = Path(__file__).resolve().parent / "layer_template.html"
LEAFLET_SHA256 = "db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a"      # leaflet.js 1.9.4 as published (the same bytes from unpkg, cdnjs and jsDelivr on 7 Oct 2026)
WORK_CRS = "EPSG:32645"
SIMPLIFY_M = 30.0
MAX_BYTES = 25_000_000
FLOORS = {"50": 50.0, "1": 1.0}                    # hectares; the first is the default
CODES = "0123456789abcdefghij"
GREY, NO_CENSUS, NO_FIGURE = "#cfcfcf", "#9fa8b3", "#e6e0d4"
CORE_CLASSES = [("Deforestation (tree cover lost)", "#ff0000", "loss"), ("Degradation", "#ffa500", "degradation"), ("Partially Degraded", "#dee64c", "partial_degradation"),
                ("No Change", "#ffffff", "no_change"), ("Improvement", "#8aff8a", "improvement"), ("Afforestation (tree cover gained)", "#007500", "gain")]
AGREEMENT = {"both": ("Both measures flag this unit", "#6a1b7a"), "hansen_only": ("Hansen only (clearance)", "#e31a1c"), "corestack_only": ("CoRE Stack only (degradation)", "#ffa500"),
             "neither": ("Neither", "#f3efe0"), "insufficient_forest": ("Insufficient forest to assess", GREY)}
SHRUG_COLUMNS = ("poverty_rate", "poverty_rate_ppp2", "poverty_rate_population_covered_share", "poverty_rate_population_rated", "poverty_rate_shared_shrid_population_share")
fails = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Stopped.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


# ---- how a figure is written on the page -----------------------------------------------------------------------------------
def num(v, decimals=2, unit=""):
    return "" if pd.isna(v) else f"{v:,.{decimals}f}{unit}"


def ha(v):
    return num(v, 2, " ha")


def pct(v):
    return num(v, 2, " %")


def lakh(v):
    return "" if pd.isna(v) else f"Rs {v:,.2f} lakh"


def whole(v):
    return "" if pd.isna(v) else f"{int(round(v)):,}"


def classify(values, breaks):
    """Class index of each value: i for the first break the value does not exceed; len(breaks) above them all.
    The value is first rounded to the two decimals it is PRINTED with, so that a unit's class never contradicts the figure in
    its panel (a share that prints as 5.00 % is in "up to 5 %", whatever the sixteenth digit of the division says)."""
    return np.searchsorted(np.asarray(breaks, float), np.round(np.asarray(values, float), 2), side="left")


def encode(geom):
    """A polygon or multipolygon as [[ring, ...], ...]; a ring is whole numbers in 0.00001 degree: first point, then steps."""
    out = []
    for p in ([geom] if geom.geom_type == "Polygon" else list(geom.geoms)):
        rings = []
        for r in [p.exterior] + list(p.interiors):
            xy = np.round(np.asarray(r.coords)[:, :2] * 1e5).astype(np.int64)
            keep = np.ones(len(xy), bool)
            keep[1:] = np.any(np.diff(xy, axis=0) != 0, axis=1)
            xy = xy[keep]
            if len(xy) < 4:
                if not rings:
                    break                                              # the outer ring is gone: the part is
                continue
            rings.append(np.concatenate([xy[0], np.diff(xy, axis=0).ravel()]).tolist())
        if rings:
            out.append(rings)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    inputs = []

    def table(path, **kw):
        p = ROOT / path
        inputs.append({"path": path, "bytes": p.stat().st_size, "sha256": sha256(p)})
        return pd.read_csv(p, dtype={"unit_id": str, "pc11_district_code": str}, **kw)

    g = gpd.read_file(a.units, layer="units")
    inputs.append({"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)})
    g["unit_id"] = g["unit_id"].astype(str)
    g = g.sort_values("unit_id").reset_index(drop=True)
    n = len(g)
    ids = g["unit_id"]
    names = table("00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv")[["district", "pc11_district_code"]]
    od = table("10_units/outside_village_district.csv")
    deg = table("20_degradation/degradation_by_unit.csv")
    core = table("20_degradation/corestack_by_unit_bands.csv")
    agr = table("20_degradation/agreement_by_unit.csv")
    need = table("30_need/need_by_unit.csv")
    alloc = table("40_allocation/allocation_by_unit.csv")
    for name, t in (("degradation_by_unit", deg), ("corestack_by_unit_bands", core), ("agreement_by_unit", agr), ("need_by_unit", need), ("allocation_by_unit", alloc)):
        if len(t) != n or not t["unit_id"].is_unique or set(t["unit_id"]) != set(ids):
            fails.append(f"{name}.csv does not hold each of the layer's {n:,} units once")
    stop_if_failed("reading the stage tables")
    deg, core, agr, need, alloc = (t.set_index("unit_id").loc[ids].reset_index() for t in (deg, core, agr, need, alloc))
    outside = (g["outside_village"] == 1).to_numpy()
    print(f"{a.units}: n = {n:,} units ({int((~outside).sum()):,} lgd_panchayat, {int(outside.sum()):,} outside_village)")

    # ---- the table of what the map shows: copied cells, and the shares computed here ---------------------------------------
    T = pd.DataFrame({"unit_id": ids, "unit_name": g["unit_name"].fillna("").astype(str).str.strip(), "unit_level": g["unit_level"], "outside_village": g["outside_village"].astype(int)})
    code = g["pc11_district_code"].astype("string")
    od_i = od.set_index("unit_id")
    code[outside] = od_i["pc11_district_code"].reindex(ids[outside]).to_numpy()
    T["pc11_district_code"] = code.to_numpy()
    T["district"] = T["pc11_district_code"].map(names.set_index("pc11_district_code")["district"])
    T["district_assigned_by"] = np.where(outside, od_i["assigned_by"].reindex(ids).to_numpy(), "the unit's Census-2011 villages")
    T["district_ambiguous"] = np.where(outside, od_i["ambiguous"].reindex(ids).fillna(0).to_numpy(), 0).astype(int)
    if T["district"].isna().any():
        fails.append(f"{int(T['district'].isna().sum())} units have no district")
    T["area_ha"] = g["area_ha"].to_numpy()
    div = lambda x, y: np.where(np.asarray(y, float) > 0, 100.0 * np.asarray(x, float) / np.where(np.asarray(y, float) > 0, y, 1), np.nan)
    for c in ("forest_ha", "hansen_loss_ha", "land_ha_tc_gt10le30", "hansen_loss_ha_tc_gt10le30", "land_ha_tc_le10", "hansen_loss_ha_tc_le10", "hansen_loss_ha_tc_eq0", "nirv_status"):
        T[c] = deg[c].to_numpy()
    T["forest_pct_of_area"] = div(T["forest_ha"], T["area_ha"])
    T["land_tc_gt10_ha"] = (deg["land_ha_tc_gt10le30"] + deg["land_ha_tc_gt30"]).to_numpy()
    T["hansen_loss_pct_of_forest"] = div(T["hansen_loss_ha"], T["forest_ha"])
    T["hansen_loss_ha_2017_2023"] = sum(deg[f"hansen_loss_ha_{y}"] for y in range(2017, 2024)).to_numpy()
    T["hansen_loss_pct_of_land_tc_gt10le30"] = div(T["hansen_loss_ha_tc_gt10le30"], T["land_ha_tc_gt10le30"])
    # CoRE Stack on land with treecover2000 > 10: the six classes and the land with a class, ALL from corestack_by_unit_bands.csv
    # (the two canopy bands above 10 added), exactly as 02_build_agreement.py reads them - so that the classes add up to the
    # land, and the shares shown are those of the agreement table to its last printed digit
    in_bands = {"loss": ("lost",), "degradation": ("degradation",), "partial_degradation": ("partial3", "partial4"), "no_change": ("nochange",), "improvement": ("improvement",), "gain": ("gained",)}
    for k, parts in in_bands.items():
        T[f"corestack_{k}_ha_tc_gt10"] = sum(core[f"class_{p}_ha_{b}"] for p in parts for b in ("gt10le30", "gt30")).to_numpy()
    T["corestack_valued_ha_tc_gt10"] = sum(T[f"corestack_{k}_ha_tc_gt10"] for k in in_bands).to_numpy()
    if np.abs(T["corestack_valued_ha_tc_gt10"] - agr["corestack_valued_ha"].to_numpy()).max() > 2e-4 or np.abs(T["corestack_degradation_ha_tc_gt10"] - agr["corestack_degradation_ha"].to_numpy()).max() > 2e-4:
        fails.append("the CoRE Stack land with a class, or its class -1, differs from agreement_by_unit.csv")
    for k in in_bands:
        T[f"corestack_{k}_pct"] = div(T[f"corestack_{k}_ha_tc_gt10"], T["corestack_valued_ha_tc_gt10"])
    T["corestack_net_pct"] = T["corestack_degradation_pct"] - T["corestack_improvement_pct"]
    for mine, theirs in (("corestack_degradation_pct", "corestack_rate_degradation"), ("corestack_loss_pct", "corestack_rate_lost"), ("corestack_improvement_pct", "corestack_rate_improvement"), ("corestack_net_pct", "corestack_rate_net")):
        gap = float(np.nanmax(np.abs(T[mine].to_numpy(float) - 100.0 * agr[theirs].to_numpy(float))))
        if gap > 1e-4:                                                   # the agreement table prints its rates to six decimals
            fails.append(f"{mine} differs from agreement_by_unit.csv's {theirs} by up to {gap:.5f} points")
    T["corestack_degradation_ha_all_land"] = deg["corestack_degradation_ha"].to_numpy()
    T["corestack_tree_cover_start_ha_all_land"] = deg["corestack_tree_cover_start_ha"].to_numpy()
    T["agreement_class"] = agr["agreement_class"].to_numpy()
    T["agreement_reference_ha"] = agr["reference_ha"].to_numpy()
    T["agreement_hansen_rate_2017_2023_pct"] = 100.0 * agr["hansen_rate_common_2017_2023"].to_numpy()
    T["agreement_corestack_degradation_rate_pct"] = 100.0 * agr["corestack_rate_degradation"].to_numpy()
    for c in ("n_works", "expenditure_total", "expenditure_plantation_category", "expenditure_forest_named_worktype", "expenditure_water"):
        T[c] = alloc[c].to_numpy()
    for c in ("expenditure_total", "expenditure_plantation_category", "expenditure_forest_named_worktype", "expenditure_water"):
        T[c + "_lakh"] = T[c] / 1e5
    for c in ("population", "households", "st_pop", "sc_pop", "adi_2011"):
        T[c] = need[c].to_numpy()
    T["st_share_pct"] = 100.0 * need["st_share"].to_numpy()
    T["sc_share_pct"] = 100.0 * need["sc_share"].to_numpy()
    if any(c.startswith("poverty") or "shrid" in c for c in T.columns):
        fails.append("a SHRUG-derived column has found its way into the layer")
    whole_ = sum(np.nan_to_num(T[f"corestack_{k}_pct"].to_numpy(float)) for _, _, k in CORE_CLASSES)
    with_land = (T["corestack_valued_ha_tc_gt10"] > 0).to_numpy()
    if np.abs(whole_[with_land] - 100).max() > 1e-6:
        fails.append(f"the six CoRE Stack class shares do not add up to 100 (largest gap {np.abs(whole_[with_land] - 100).max():.6f} points)")
    if (T.loc[outside, ["population", "st_share_pct", "adi_2011"]].notna().any().any()):
        fails.append("an outside_village unit has a census figure")
    stop_if_failed("building the table of displayed figures")

    # ---- classes ---------------------------------------------------------------------------------------------------------------
    def scale(colors, labels):
        return [{"label": lab, "color": col} for lab, col in zip(labels, colors)]

    def flat(label, color):
        return {"label": label, "color": color, "flat": 1}

    base = {"forest": T["forest_ha"].to_numpy(float), "band": T["land_ha_tc_gt10le30"].to_numpy(float),
            "reference": np.minimum(T["land_tc_gt10_ha"].to_numpy(float), T["corestack_valued_ha_tc_gt10"].to_numpy(float))}
    base_words = {"forest": "forest (tree canopy above 30 % in 2000)", "band": "land with 10 to 30 % tree canopy in 2000",
                  "reference": "land with tree canopy above 10 % in 2000 that has a CoRE Stack class"}
    layers = []

    def add(layer, cls, floored_on=None):
        """cls: class index per unit ignoring any floor. With floored_on, units under each floor move to the last class."""
        k = len(layer["classes"])
        if floored_on is None:
            arrays = {"all": cls}
        else:
            layer["classes"] = layer["classes"] + [flat("Insufficient forest to assess", GREY)]
            arrays = {f: np.where(base[floored_on] >= v, cls, k) for f, v in FLOORS.items()}
            layer["floored"] = 1
            layer["floor_note"] = {f: f"Grey: under {v:g} ha of {base_words[floored_on]} - {int((base[floored_on] < v).sum()):,} units." for f, v in FLOORS.items()}
        if max(int(x.max()) for x in arrays.values()) >= len(layer["classes"]) or len(layer["classes"]) > len(CODES):
            fails.append(f"layer {layer['id']}: a class index has no class")
        layer["cls"] = {f: "".join(CODES[i] for i in x) for f, x in arrays.items()}
        layer["counts"] = {f: [f"{int((x == i).sum()):,} units" for i in range(len(layer["classes"]))] for f, x in arrays.items()}
        layer["_arrays"] = arrays
        layers.append(layer)

    greens = ["#ffffff", "#e5f5e0", "#a1d99b", "#74c476", "#31a354", "#006d2c"]
    v = T["forest_pct_of_area"].to_numpy(float)
    add({"id": "forest_area", "group": "Forests", "title": "Area under forests", "legend_title": "Forest (tree canopy above 30 % in 2000) as a share of the unit's area",
         "this_shows": "This shows how much of each unit was forest in 2000 by Hansen's tree-canopy map. It is the land the next layer's loss is counted on. It is not Odisha's recorded forest area, and not the Forest Survey's forest cover.",
         "classes": scale(greens, ["No forest by this measure", "Up to 1 %", "1 to 10 %", "10 to 30 %", "30 to 60 %", "More than 60 %"])},
        np.where(T["forest_ha"].to_numpy(float) <= 0, 0, 1 + classify(v, [1, 10, 30, 60])))
    reds = ["#ffffcc", "#ffeda0", "#fed976", "#fd8d3c", "#f03b20", "#bd0026", "#67000d"]
    loss_labels = ["No loss recorded", "Up to 1 %", "1 to 2.5 %", "2.5 to 5 %", "5 to 10 %", "10 to 20 %", "More than 20 %"]
    v = T["hansen_loss_pct_of_forest"].to_numpy(float)
    add({"id": "hansen_loss", "group": "Forests", "title": "Tree cover loss 2001-2025 (Hansen)", "legend_title": "Tree cover loss 2001-2025 as a share of the unit's forest (Hansen)",
         "this_shows": "This shows forest that was cleared outright, as a share of the forest each unit had in 2000. Hansen sees clearance of fairly closed canopy; it is blind to thinning under a canopy that still stands, and to change on land that was open in 2000.",
         "classes": scale(reds, loss_labels)}, np.where(np.round(np.nan_to_num(v), 2) <= 0, 0, 1 + classify(np.nan_to_num(v), [1, 2.5, 5, 10, 20])), "forest")
    v = T["hansen_loss_pct_of_land_tc_gt10le30"].to_numpy(float)
    add({"id": "canopy_band_loss", "group": "Forests", "title": "Loss on open canopy, outside the forest mask (Hansen)", "legend_title": "Tree cover loss 2001-2025 on land with 10 to 30 % canopy in 2000, as a share of that land",
         "this_shows": "This shows loss on land that had some tree canopy in 2000 but too little to count as forest above. Of all Hansen loss in the units, {outside_mask:.0f} % lies outside the forest mask; this band is the part of it that stood as trees in 2000.",
         "classes": scale(reds, loss_labels)}, np.where(np.round(np.nan_to_num(v), 2) <= 0, 0, 1 + classify(np.nan_to_num(v), [1, 2.5, 5, 10, 20])), "band")
    oranges = ["#fff5e0", "#fdd49e", "#fdae6b", "#f16913", "#a63603"]
    v = T["corestack_degradation_pct"].to_numpy(float)
    add({"id": "corestack_degradation", "group": "Forests", "title": "Forest health and degradation (CoRE Stack tree cover change 2017-2023)",
         "legend_title": "CoRE Stack class Degradation (canopy density or tree height down a class), 2017-2023, as a share of the land with a class, on land with canopy above 10 % in 2000",
         "this_shows": "This shows thinning under a canopy that still stands - what Hansen cannot see. A pixel is 'Degradation' when a classifier that is right about two times in three says it crossed its zone's threshold; read it beside Improvement, which is the same noise the other way (next layer).",
         "classes": scale(oranges, ["Up to 5 %", "5 to 15 %", "15 to 25 %", "25 to 35 %", "More than 35 %"])}, classify(np.nan_to_num(v), [5, 15, 25, 35]), "reference")
    div_colors = ["#1a7837", "#7fbf7b", "#f7f7f7", "#fdb863", "#e66101", "#7f3b08"]
    v = T["corestack_net_pct"].to_numpy(float)
    add({"id": "corestack_net", "group": "Forests", "title": "Degradation net of improvement (CoRE Stack 2017-2023)",
         "legend_title": "CoRE Stack class Degradation minus class Improvement, 2017-2023, as a share of the land with a class, on land with canopy above 10 % in 2000",
         "this_shows": "This shows where degradation outweighs improvement. Because both classes carry the same classifier noise, the net is the safer reading: near zero means no net signal.",
         "classes": scale(div_colors, ["Net improvement, more than 10 points", "Net improvement, 2 to 10 points", "Within 2 points: no net change", "Net degradation, 2 to 10 points", "Net degradation, 10 to 20 points", "Net degradation, more than 20 points"])},
        classify(np.nan_to_num(v), [-10, -2, 2, 10, 20]), "reference")
    order = ["both", "hansen_only", "corestack_only", "neither", "insufficient_forest"]
    add({"id": "agreement", "group": "Forests", "title": "Do the two measures agree? (2017-2023)", "legend_title": "Hansen loss 2017-2023 beside CoRE Stack Degradation 2017-2023: which measure puts the unit in its top fifth",
         "this_shows": "This shows, for units with at least 50 ha of land with canopy above 10 % in 2000, whether each measure ranks the unit in the top fifth of such units. Where both do, the claim that the unit degraded is as strong as these two sources can make it. Where one does, neither is preferred. This layer has its own floor: the control on the left does not change it.",
         "classes": [({"label": AGREEMENT[k][0], "color": AGREEMENT[k][1], "flat": 1} if k == "insufficient_forest" else {"label": AGREEMENT[k][0], "color": AGREEMENT[k][1]}) for k in order]},
        T["agreement_class"].map({k: i for i, k in enumerate(order)}).to_numpy())
    blues = ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"]
    works, spent = T["n_works"].to_numpy(float), T["expenditure_total_lakh"].to_numpy(float)
    add({"id": "allocation", "group": "MGNREGA (works geotagged inside the unit)", "title": "Past allocation: expenditure on all works", "legend_title": "Expenditure on all MGNREGA works geotagged inside the unit, rupees lakh (works started 2006-07 to 2017-18 in the main)",
         "this_shows": "This shows what was spent on works whose recorded location falls inside the unit - not what the panchayat of record received: only {in_own_unit:.0f} works in 100 lie in the unit that holds most of their own panchayat's works. It is a total, not per person. The record effectively ends with works started in 2017-18.",
         "classes": scale(blues, ["Up to Rs 10 lakh", "Rs 10 to 50 lakh", "Rs 50 to 100 lakh", "Rs 100 to 200 lakh", "Rs 200 to 400 lakh", "More than Rs 400 lakh"])
                    + [flat("No works geotagged here", "#ffffff"), flat("Works recorded, expenditure not", NO_FIGURE)]},
        np.where(works <= 0, 6, np.where(np.isnan(spent), 7, classify(np.nan_to_num(spent), [10, 50, 100, 200, 400]))))
    teals = ["#e0f3ee", "#a8ddb5", "#52b69a", "#1a7f6b"]
    fn = T["expenditure_forest_named_worktype_lakh"].to_numpy(float)
    add({"id": "forest_named_expenditure", "group": "MGNREGA (works geotagged inside the unit)", "title": "Forest-named expenditure", "legend_title": "Expenditure on works whose work type names forest or forestry, rupees lakh",
         "this_shows": "This shows spending on works typed as afforestation, forest protection, eco-restoration of forest or forestry plantation: {forest_named:.1f} % of all expenditure on the works in these units. The wider 'Plantation' category ({plantation:.0f} %) includes orchards and is given in the panel for each unit.",
         "classes": scale(teals, ["Up to Rs 1 lakh", "Rs 1 to 5 lakh", "Rs 5 to 20 lakh", "More than Rs 20 lakh"]) + [flat("None", "#ffffff"), flat("Works recorded, expenditure not", NO_FIGURE)]},
        np.where(np.isnan(fn), np.where(works <= 0, 4, 5), np.where(np.round(np.nan_to_num(fn), 2) <= 0, 4, classify(np.nan_to_num(fn), [1, 5, 20]))))
    tans = ["#eeeac5", "#f7dba5", "#ecb573", "#b9722c"]
    st = T["st_share_pct"].to_numpy(float)
    add({"id": "st_share", "group": "Social (Census 2011)", "title": "Scheduled Tribe share of population", "legend_title": "Scheduled Tribe share of population, Census 2011",
         "this_shows": "This shows the share of each unit's 2011 population that is Scheduled Tribe. The first two breaks, 18 % and 33 %, are the ones CoRE Stack's Know Your Landscape dashboard uses.",
         "classes": scale(tans, ["Less than 18 %", "18 to 33 %", "33 to 50 %", "More than 50 %"]) + [flat("No census data for this land", NO_CENSUS), flat("No resident population in the census rows", NO_FIGURE)]},
        np.where(outside, 4, np.where(np.isnan(st), 5, np.where(np.round(np.nan_to_num(st), 2) < 18, 0, 1 + classify(np.nan_to_num(st), [33, 50])))))
    purples = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"]
    adi = T["adi_2011"].to_numpy(float)
    add({"id": "adi_2011", "group": "Social (Census 2011)", "title": "Aggregate Development Index 2011", "legend_title": "Aggregate Development Index 2011 (5 to 15; higher is more developed)",
         "this_shows": "This shows a village development index from Census 2011 - the sum of five ranks from 1 (low) to 3 (advanced): bathroom facility, cooking fuel, source of drinking water, assets, literacy - averaged over each unit's villages by population.",
         "classes": scale(purples, ["Up to 6", "6 to 7", "7 to 8", "8 to 9.5", "More than 9.5"]) + [flat("No census data for this land", NO_CENSUS), flat("No index for this unit's villages", NO_FIGURE)]},
        np.where(outside, 5, np.where(np.isnan(adi), 6, classify(np.nan_to_num(adi), [6, 7, 8, 9.5]))))
    stop_if_failed("classifying")
    for L in layers:
        for f, x in L["_arrays"].items():
            T[f"class_{L['id']}" + ("" if f == "all" else f"_floor_{f}_ha")] = [L["classes"][i]["label"] for i in x]

    # ---- the classes against the stage tables' own counts -----------------------------------------------------------------------
    hl = pd.read_csv(ROOT / "20_degradation/hansen_by_unit_level.csv").set_index("unit_level")
    ff = pd.read_csv(ROOT / "20_degradation/forest_floor_options.csv").set_index("floor_ha")
    ap_ = json.load(open(ROOT / "20_degradation/agreement.provenance.json"))
    by = {L["id"]: L for L in layers}
    grey = lambda lid, f: int((by[lid]["_arrays"][f] == len(by[lid]["classes"]) - 1).sum())
    checks = {"units_under_1_ha_of_forest": [grey("hansen_loss", "1"), int(hl.loc["all units", "units_with_under_1_ha_of_forest_including_none"])],
              "units_under_50_ha_of_forest": [grey("hansen_loss", "50"), n - int(ff.loc[50.0, "units_kept"])],
              "units_with_no_forest": [int((by["forest_area"]["_arrays"]["all"] == 0).sum()), int(hl.loc["all units", "units_with_no_forest"])]}
    for k, i in {k: i for i, k in enumerate(order)}.items():
        checks[f"agreement_{k}"] = [int((by["agreement"]["_arrays"]["all"] == i).sum()), int(ap_["counts"]["by_level"]["all units"].get(k, 0))]
    checks["no_census_data_units_st_share"] = [int((by["st_share"]["_arrays"]["all"] == 4).sum()), int(outside.sum())]
    checks["no_census_data_units_adi"] = [int((by["adi_2011"]["_arrays"]["all"] == 5).sum()), int(outside.sum())]
    for k, (mine, theirs) in checks.items():
        if mine != theirs:
            fails.append(f"{k}: {mine:,} units on the map, {theirs:,} in the stage's own table")
    totals = {"forest_km2": [float(T["forest_ha"].sum()) / 100, float(hl.loc["all units", "forest_km2"]), 0.06], "hansen_loss_km2": [float(T["hansen_loss_ha"].sum()) / 100, float(hl.loc["all units", "loss_km2_2001_2025"]), 0.006]}
    for k, (mine, theirs, tol) in totals.items():
        if abs(mine - theirs) > tol:
            fails.append(f"{k}: {mine:,.3f} in the layer's table, {theirs:,.2f} in hansen_by_unit_level.csv")
    if abs(float(T["expenditure_total"].sum()) - float(alloc["expenditure_total"].sum())) > 0.5:
        fails.append("expenditure_total does not add up to the allocation table's")
    stop_if_failed("checking the classes against the stage tables' own counts")
    print("OK  classes: " + "; ".join(f"{k} {v[0]:,}" for k, v in checks.items()) + " - each equal to the stage tables' own counts")

    # ---- geometry: simplified as a coverage ---------------------------------------------------------------------------------------
    geod = Geod(ellps="WGS84")
    # area on the ellipsoid; the rings are put in a fixed order first, because the sum of a polygon's signed ring areas is only its
    # area if its holes run the other way round from its shell, and a simplified coverage does not promise that
    ell = lambda geoms: np.array([abs(geod.geometry_area_perimeter(x)[0]) / 1e4 for x in shapely.orient_polygons(geoms)])
    src = shapely.make_valid(g.geometry.values)
    if not bool(shapely.coverage_is_valid(src)):
        fails.append("the unit polygons are not a valid coverage: they cannot be simplified with shared edges kept")
        stop_if_failed("checking the geometry")
    simple = gpd.GeoSeries(shapely.coverage_simplify(shapely.make_valid(g.to_crs(WORK_CRS).geometry.values), SIMPLIFY_M), crs=WORK_CRS).to_crs("EPSG:4326").values
    shapes = [encode(x) for x in simple]
    lost = [i for i, s in enumerate(shapes) if not s]
    for i in lost:                                                       # a unit so small that it vanished: keep its own shape
        shapes[i] = encode(src[i])
    if any(not s for s in shapes):
        fails.append("a unit has no shape on the map")
    a0, a1 = ell(src), ell(simple)
    rel = (a1 - a0) / a0
    area_error = {"tolerance_m": SIMPLIFY_M, "in": WORK_CRS, "stored_to_degrees": 1e-5, "vertices_before": int(shapely.get_num_coordinates(src).sum()), "vertices_after": int(sum(len(r) // 2 for s in shapes for p in s for r in p)),
                  "total_area_change_pct": round(100 * float(a1.sum() / a0.sum() - 1), 5), "per_unit_abs_change_pct": {"median": round(100 * float(np.median(np.abs(rel))), 3), "p95": round(100 * float(np.percentile(np.abs(rel), 95)), 2),
                                                                                                                 "p99": round(100 * float(np.percentile(np.abs(rel), 99)), 2), "max": round(100 * float(np.abs(rel).max()), 1)},
                  "units_changed_by_more_than_5_pct": int((np.abs(rel) > 0.05).sum()), "largest_such_unit_ha": round(float(a0[np.abs(rel) > 0.05].max()), 1) if (np.abs(rel) > 0.05).any() else None,
                  "median_such_unit_ha": round(float(np.median(a0[np.abs(rel) > 0.05])), 2) if (np.abs(rel) > 0.05).any() else None, "units_kept_unsimplified_because_they_vanished": len(lost)}
    T["shape_area_change_pct"] = np.round(100 * rel, 3)
    print(f"OK  geometry: {area_error['vertices_before']:,} vertices -> {area_error['vertices_after']:,} at {SIMPLIFY_M:g} m; total area {area_error['total_area_change_pct']:+.5f} %; "
          f"per unit: median {area_error['per_unit_abs_change_pct']['median']} %, 95th percentile {area_error['per_unit_abs_change_pct']['p95']} %, largest {area_error['per_unit_abs_change_pct']['max']} %; "
          f"{area_error['units_changed_by_more_than_5_pct']} units change by more than 5 % (the largest of them {area_error['largest_such_unit_ha']} ha)")
    districts = []
    for code_, grp in T.groupby("pc11_district_code"):
        u = shapely.coverage_union_all(simple[grp.index.to_numpy()])
        parts = [u] if u.geom_type == "Polygon" else sorted(u.geoms, key=lambda p: p.area, reverse=True)
        outline = [encode(shapely.Polygon(p.exterior))[0][0] for p in parts if p.area > 2e-5]            # islands under about 20 ha are not outlined
        pt = parts[0].representative_point()
        w, s, e, nn = u.bounds
        districts.append({"name": grp["district"].iloc[0], "code": code_, "outline": outline, "label": [round(pt.y, 5), round(pt.x, 5)], "bbox": [[round(s, 4), round(w, 4)], [round(nn, 4), round(e, 4)]], "n_units": int(len(grp))})
    districts.sort(key=lambda d: d["name"])
    if len(districts) != 30:
        fails.append(f"{len(districts)} districts, not 30")

    # ---- what the panel says for a unit: every string made here ---------------------------------------------------------------------
    nd, nc = "not defined: no such land in this unit", "no census data for this land"
    type_label = np.where(outside, "Outside-village unit: land outside any revenue village", "LGD panchayat unit")
    how = {"label": "the name on the DataMeet polygon", "neighbours: the polygon has no district name": "its neighbours (the polygon carries no district name)",
           "neighbours: the label's district is nowhere round the unit": "its neighbours (the polygon's own label names a district that is nowhere round it)"}
    flag = np.where(T["forest_ha"] < 1, "Under 1 ha of forest: this unit cannot be assessed for forest loss.",
                    np.where(T["forest_ha"] < 50, "Under 50 ha of forest: a loss rate on this little forest is mostly noise.", ""))
    F = []
    for i, r in enumerate(T.itertuples(index=False)):
        o = bool(r.outside_village)
        F.append([
            r.unit_name or "(no name on the polygon)", r.unit_id, type_label[i],
            r.district + (" (by " + how[r.district_assigned_by] + (", ambiguous: two districts lie round it almost equally" if r.district_ambiguous else "") + ")" if o else ""),
            ha(r.area_ha), ha(r.forest_ha), pct(r.forest_pct_of_area), ha(r.land_tc_gt10_ha),
            ha(r.hansen_loss_ha), pct(r.hansen_loss_pct_of_forest) or nd, ha(r.hansen_loss_ha_2017_2023),
            ha(r.land_ha_tc_gt10le30), ha(r.hansen_loss_ha_tc_gt10le30), pct(r.hansen_loss_pct_of_land_tc_gt10le30) or nd, ha(r.land_ha_tc_le10), ha(r.hansen_loss_ha_tc_le10), ha(r.hansen_loss_ha_tc_eq0),
            ha(r.corestack_valued_ha_tc_gt10),
            *[(ha(getattr(r, f"corestack_{k}_ha_tc_gt10")) + ("  (" + pct(getattr(r, f"corestack_{k}_pct")) + ")" if pct(getattr(r, f"corestack_{k}_pct")) else "")) for _, _, k in CORE_CLASSES],
            (num(r.corestack_net_pct, 2, " points") if not pd.isna(r.corestack_net_pct) else nd), ha(r.corestack_degradation_ha_all_land), ha(r.corestack_tree_cover_start_ha_all_land),
            AGREEMENT[r.agreement_class][0], pct(r.agreement_hansen_rate_2017_2023_pct) or nd, pct(r.agreement_corestack_degradation_rate_pct) or nd, ha(r.agreement_reference_ha),
            whole(r.n_works), lakh(r.expenditure_total_lakh) or "not recorded", lakh(r.expenditure_plantation_category_lakh) or "not recorded", lakh(r.expenditure_forest_named_worktype_lakh) or "not recorded",
            lakh(r.expenditure_water_lakh) or "not recorded",
            nc if o else whole(r.population), nc if o else whole(r.households), nc if o else (pct(r.st_share_pct) or "not defined: no resident population"),
            nc if o else (pct(r.sc_share_pct) or "not defined: no resident population"), nc if o else (num(r.adi_2011, 2) or "no index for this unit's villages"),
            flag[i]])
    FIELD_COUNT = len(F[0])
    c0 = 18                                                              # the first of the six CoRE Stack class rows
    panel = [
        {"heading": "x", "heading_field": 0, "top": 1, "rows": [["Unit id", 1], ["Type", 2], ["District", 3], ["Area", 4]]},
        {"heading": "Forests: Hansen tree canopy and loss", "flag_field": FIELD_COUNT - 1,
         "rows": [["Forest in 2000 (canopy above 30 %)", 5], ["... as a share of the unit", 6], ["Tree cover loss 2001-2025 on that forest", 8], ["... as a share of the forest", 9], ["... of which lost 2017-2023", 10],
                  ["Land with canopy above 10 % in 2000", 7]],
         "note": "Source: Hansen Global Forest Change v1.13 (30 m). Areas are sums of pixel areas inside the unit. Pre-computed; nothing on this page is calculated in the browser."},
        {"heading": "Loss by canopy in 2000 (what the forest mask leaves out)",
         "rows": [["Land with 10 to 30 % canopy", 11], ["Loss 2001-2025 on it", 12], ["... as a share of that land", 13], ["Land with 10 % canopy or less", 14], ["Loss 2001-2025 on it", 15], ["... of which on land with no canopy in 2000", 16]],
         "note": "Loss on land with no canopy at all in 2000 is tree cover that grew after 2000 and was removed, or an artefact of detection: not forest that stood in 2000."},
        {"heading": "Forest health and degradation: CoRE Stack tree cover change 2017-2023", "bar": 1,
         "rows": [["Land with a class, on canopy above 10 % in 2000", 17]] + [[name, c0 + k] for k, (name, _, _) in enumerate(CORE_CLASSES)]
                 + [["Degradation minus Improvement", c0 + 6], ["Degradation on ALL land the product covers", c0 + 7], ["Its tree cover at the start, all land", c0 + 8]],
         "note": "Source: CoRE Stack, overall_change_2017_2023 (25 m), read from the raw Earth Engine asset: classes named and coloured as CoRE Stack does. CoRE Stack's own dashboard takes Deforestation and Afforestation from its land-use maps "
                 "instead, so its figures for those two classes will differ. Only Deforestation was validated by its producers."},
        {"heading": "Do the two measures agree? (2017-2023)",
         "rows": [["Agreement class", c0 + 9], ["Hansen loss 2017-2023, share of the land below", c0 + 10], ["CoRE Stack Degradation, share of the land with a class", c0 + 11], ["Land with canopy above 10 % in 2000", c0 + 12]],
         "note": "A unit is assessed if it has at least 50 ha of this land by both sources' grids, and flagged by a measure if its rate is in the top fifth of assessed units. The flag is relative, not an absolute amount of damage."},
        {"heading": "MGNREGA works geotagged inside this unit",
         "rows": [["Works", c0 + 13], ["Expenditure, all works", c0 + 14], ["... Plantation category (includes orchards)", c0 + 15], ["... work type names forest or forestry", c0 + 16], ["... water works", c0 + 17]],
         "note": "Source: MGNREGA geotagged assets (Bhuvan, as published by CoRE Stack), works started 2006-07 to 2017-18 in the main. What was geotagged inside this polygon - not what the panchayat of record received. "
                 "The three lines below the total are flags that overlap: do not add them."},
        {"heading": "Social: Census 2011",
         "rows": [["Population", c0 + 18], ["Households", c0 + 19], ["Scheduled Tribe share", c0 + 20], ["Scheduled Caste share", c0 + 21], ["Aggregate Development Index 2011 (5 to 15)", c0 + 22]],
         "note": "Source: Census 2011 village rows summed over the unit's villages; index by the ICTD group, IIT Delhi. Outside-village units are land outside any revenue village: the census has no rows for them."},
        {"heading": "NIRv trend (Landsat 8, 2013-2025)", "note": "Pending: not yet computed for the state. It will be a reported column, not a measure of degradation - its trend moves with the correction applied for the date of each image."},
    ]
    if any(max(r[1] for r in s.get("rows", [["", 0]])) >= FIELD_COUNT for s in panel) or c0 + 23 != FIELD_COUNT - 1:
        fails.append("the panel points at a field that is not there")
    widths = np.nan_to_num(np.column_stack([T[f"corestack_{k}_pct"].to_numpy(float) for _, _, k in CORE_CLASSES]))
    bars = [[round(float(x), 2) for x in row] if row.sum() > 0 else 0 for row in widths]
    stop_if_failed("building the panel")

    # ---- the texts: every figure in them is read from a stage table here -----------------------------------------------------------
    n_out, n_lgd = int(outside.sum()), int((~outside).sum())
    ae = area_error
    ov = hl.loc["outside_village"]
    rep = pd.read_csv(ROOT / "20_degradation/forest_floor_repeatability.csv").set_index("forest_ha_from")["odd_years_vs_even_years_spearman"]
    summ = pd.read_csv(ROOT / "20_degradation/agreement_summary.csv")
    head = summ[(summ.delivered == 1) & (summ.units == "all units")].iloc[0]
    por = pd.read_csv(ROOT / "40_allocation/panchayat_of_record_check.csv").set_index("scope").loc["all units"]
    uc = json.load(open(ROOT / "10_units/units.provenance.json"))["counts"]
    spent_all = float(alloc["expenditure_total"].sum())
    fig = {"out_area": float(ov["share_of_all_area_pct"]), "out_forest": float(ov["share_of_all_forest_pct"]), "out_loss": float(ov["share_of_all_loss_pct"]),
           "rep_1": float(rep.loc[1.0]), "rep_5": float(rep.loc[5.0]), "rep_50": float(rep.loc[50.0]), "kept_50": float(ff.loc[50.0, "forest_kept_pct"]),
           "outside_mask": float(hl.loc["all units", "loss_outside_the_mask_pct_of_any_cover"]), "expected_both": float(head["both_expected_if_unrelated"]),
           "odds": float(head["odds_ratio"]), "odds_lo": float(head["odds_ratio_lo95"]), "odds_hi": float(head["odds_ratio_hi95"]),
           "in_own_unit": 100 * float(por["share_in_modal_polygon"]), "forest_named": 100 * float(alloc["expenditure_forest_named_worktype"].sum()) / spent_all,
           "plantation": 100 * float(alloc["expenditure_plantation_category"].sum()) / spent_all}
    for L in layers:
        L["this_shows"] = L["this_shows"].format(**fig)
    about = f"""
<h1>Forest condition beside MGNREGA allocation and social need - Odisha</h1>
<p><b>What this is.</b> A pre-computed, offline map of {n:,} units covering Odisha: {n_lgd:,} LGD panchayat units and {n_out:,} outside-village units. For each unit it shows forest and its loss (Hansen), forest health and degradation (CoRE Stack),
whether those two agree, MGNREGA expenditure on the works geotagged inside the unit, and Census 2011 measures. Click a unit to read its figures; choose a layer on the left.</p>
<p><b>Why it exists.</b> The paper on Commons Connect (Mehta et al., ICTD 2024) describes a tool for water security built on the CoRE Stack and says: &ldquo;We envision that similarly other tools can be built, for example, for agroforestry planning,
forest conservation and restoration, tracking of carbon credits, etc. by suitably bringing together new datasets and methods for these new domains of ecological sustainability.&rdquo; This is a first step toward such a tool for forest:
datasets (tree canopy, its loss, tree-cover change), indicators per unit, and one view of them. It is a demonstration for discussion, to be checked against what people who know these places observe - not a verdict on any place.</p>
<p><b>The unit.</b> Commons Connect computes its landscape-level indicators per micro-watershed, and the consultation catalogue lists its forest variables per forest beat. This map uses administrative polygons instead, because MGNREGA funds and the census are
administrative: an LGD panchayat unit is the villages mapped to one LGD panchayat id (not always a whole gram panchayat). <b>Outside-village units</b> (hatched) are the land outside any revenue village - mostly reserved forest. They are {fig['out_area']:.0f} % of the area and hold {fig['out_forest']:.0f} % of
the forest and {fig['out_loss']:.0f} % of its loss, and they have no census rows. The few blank patches inside the state are {uc['villages_with_no_lgd_panchayat']} villages
({uc['villages_with_no_lgd_panchayat_km2']:,.0f} km<sup>2</sup>) that have a census code but no row in the village-to-panchayat mapping: they belong to no unit. The district of an outside-village unit is the district named on its boundary polygon,
checked against the villages round it; the panel says so where it was assigned another way or is ambiguous.</p>
<p><b>Honest colour.</b> More than half of the units ({checks['units_under_1_ha_of_forest'][0]:,} of {n:,}) have under one hectare of forest, and a rate on a few hectares is noise: between odd and even years the rank correlation of a unit's loss rate is {fig['rep_1']:.2f} for units
with 1 to 2 ha of forest, {fig['rep_5']:.2f} at 5 to 10 ha and {fig['rep_50']:.2f} at 50 to 100 ha. So on the forest layers a unit with too little of the land a layer rests on is grey - <i>insufficient forest to assess</i> - and never on the colour scale. You can set the minimum to 50 ha (the default; {checks['units_under_50_ha_of_forest'][0]:,} units grey on the
Hansen layer, and the coloured units still hold {fig['kept_50']:.1f} % of the forest) or to 1 ha. On the census layers the outside-village units are <i>no census data for this land</i>, never zero.</p>
<p><b>What each forest measure can and cannot see.</b></p>
<ul>
<li><b>Hansen tree cover loss</b> dates the outright removal of canopy that was fairly closed in 2000. It is validated and it is a floor: it cannot see thinning, and it cannot see change on land that was already open in 2000.</li>
<li><b>CoRE Stack tree cover change 2017-2023</b> classes each 25 m pixel inside its own tree mask by whether canopy density or tree height moved a class between two three-year periods. Its Degradation and Improvement classes come from classifiers
its producers report as right about two times in three, and only Deforestation was validated by them: read Degradation beside Improvement. The two agro-climatic zone models differ, so part of what the map shows follows the zone boundary.</li>
<li><b>Agreement.</b> Among the {int(ap_['counts']['assessed']):,} units with at least 50 ha of land with canopy above 10 % in 2000, {checks['agreement_both'][0]:,} are in the top fifth on both measures; two unrelated measures would share about {fig['expected_both']:.0f}
(odds ratio {fig['odds']:.2f}, 95 % interval {fig['odds_lo']:.2f} to {fig['odds_hi']:.2f}). The two do not measure
the same thing and are not expected to mark the same pixels; the question is whether they point at the same units.</li>
<li><b>NIRv</b> (a greenness trend from Landsat 8) is pending and will be a reported column only.</li>
</ul>
<p><b>MGNREGA.</b> Expenditure is that of the works whose recorded location falls inside a unit, from the geotagged asset record, which effectively ends with works started in 2017-18. It is not what a panchayat received: only {fig['in_own_unit']:.0f} works in 100 fall in the unit
that holds most of their own panchayat's works. Works typed as forest or forestry are {fig['forest_named']:.1f} % of all expenditure on the works in these units. What happened to plantation spending after 2017-18 is in the scheme's district reports (MIS report R6.20), not in this unit-level record.</p>
<p><b>The shapes are simplified</b> so that the file can be e-mailed: {ae['vertices_before']:,} boundary points to {ae['vertices_after']:,}, with a tolerance of {ae['tolerance_m']:g} m and shared boundaries kept shared. The whole area changes by {ae['total_area_change_pct']:+.4f} %;
a unit's drawn area by {ae['per_unit_abs_change_pct']['median']} % at the median and under {ae['per_unit_abs_change_pct']['p95']} % for 95 units in 100; {ae['units_changed_by_more_than_5_pct']} very small units (none larger than {ae['largest_such_unit_ha']} ha) change by more than 5 %.
Every area printed in a panel is the unit's true area, not that of the simplified shape. There is no background map: nothing is fetched from the internet.</p>
<p><b>To check a figure.</b> Every number shown is a cell of <code>layer_by_unit.csv</code>, which is built from the stage tables <code>degradation_by_unit.csv</code>, <code>agreement_by_unit.csv</code>, <code>need_by_unit.csv</code> and <code>allocation_by_unit.csv</code>.</p>
"""
    sources = """
<h1>Sources and licences</h1>
<table>
<tr><th>What</th><th>Source</th><th>Licence or terms</th></tr>
<tr><td>Tree canopy in 2000 and tree cover loss 2001-2025</td><td>Hansen, Potapov, Moore, Hancher et al., Global Forest Change v1.13 (University of Maryland), through Google Earth Engine; state totals reconciled to Global Forest Watch's published figures</td><td>CC BY 4.0</td></tr>
<tr><td>Forest cover of Odisha, as a comparison only (no figure of it is on the map)</td><td>Forest Survey of India, India State of Forest Report 2023</td><td>&copy; Forest Survey of India; non-commercial use with acknowledgment</td></tr>
<tr><td>Tree cover change 2017-2023 (Deforestation, Degradation, No Change, Improvement, Afforestation, Partially Degraded)</td><td>CoRE Stack (Commoning for Resilience and Equality), ACT4D group, IIT Delhi - core-stack.org</td><td>CC BY 4.0</td></tr>
<tr><td>Population, households, Scheduled Tribe and Scheduled Caste population</td><td>Census of India 2011, village rows as compiled by the ICTD group, IIT Delhi</td><td>Government of India; compilation CC BY 4.0</td></tr>
<tr><td>Aggregate Development Index 2011</td><td>ICTD group, IIT Delhi, from Census 2011</td><td>CC BY 4.0. Its documentation says SHRUG's keys were used to link 2001 and 2011 villages; the 2011 index itself is computed from Census 2011 rows</td></tr>
<tr><td>MGNREGA works and expenditure</td><td>Ministry of Rural Development: geotagged assets (Bhuvan GeoMGNREGA), as published by CoRE Stack; MGNREGA MIS report R6.20 for the state-level statements</td><td>Government of India public data; compilation CC BY 4.0</td></tr>
<tr><td>Unit boundaries, and district names of the land outside villages</td><td>DataMeet Community, Indian village boundaries (Odisha), joined to LGD panchayat ids</td><td><b>ODbL 1.0.</b> The shapes in this file are a database derived from DataMeet's and are offered under the same licence</td></tr>
<tr><td>Poverty rate (NOT in this file)</td><td>SHRUG 2.2, Development Data Lab</td><td><b>CC BY-NC-SA 4.0.</b> The analysis behind this map uses SHRUG's small-area poverty estimates; no SHRUG-derived figure is included here, so that this file does not become a derived work under that licence</td></tr>
<tr><td>The map library</td><td>Leaflet 1.9.4</td><td>BSD 2-Clause, &copy; Volodymyr Agafonkin and CloudMade; embedded unmodified</td></tr>
</table>
<p class="sub">Reference: Mehta et al., &ldquo;Initial Observations from Field Testing of a Digital Participatory Tool to Improve Water Security in Rural India&rdquo;, ICTD 2024.</p>
"""
    payload = {
        "title": "Forest condition, MGNREGA allocation and social need - Odisha", "subtitle": f"{n:,} units. Pre-computed and offline: a demonstration for discussion.",
        "built": f"Built {started[:10]} from stage outputs of {max(json.load(open(ROOT / '20_degradation' / p))['run_utc'] for p in ('hansen.provenance.json', 'corestack.provenance.json'))[:10]} and earlier.",
        "unit_types": {"lgd": f"LGD panchayat units ({n_lgd:,})", "out": f"Outside-village units ({n_out:,})", "out_legend": "Hatched: outside-village unit (land outside any revenue village)"},
        "codes": CODES, "default_layer": "hansen_loss", "default_floor": "50",
        "floors": [{"id": f, "label": f"{v:g} ha" + (" (default: the floor proposed for the analysis)" if f == "50" else " (every unit with measurable forest)")} for f, v in FLOORS.items()],
        "layers": [x for L in layers for x in ([{k: v for k, v in L.items() if not k.startswith("_")}]
                                               + ([{"id": "nirv", "group": "Forests", "title": "NIRv trend (Landsat 8, 2013-2025)", "pending": "pending, not yet computed"}] if L["id"] == "agreement" else []))],
        "core_classes": [{"name": name, "color": color} for name, color, _ in CORE_CLASSES],
        "panel": panel, "info_empty": "<h3>Click a unit</h3><p class='sub'>Its figures appear here. Hatched units are land outside any revenue village.</p>",
        "search_none": "No unit with that name or id.", "search_many": "{n} units match; showing the first. Add more of the name, or use the id.",
        "about_html": about, "sources_html": sources,
        "bounds": [[float(g.total_bounds[1]), float(g.total_bounds[0])], [float(g.total_bounds[3]), float(g.total_bounds[2])]],
        "districts": districts, "id": ids.tolist(), "out": "".join("1" if o else "0" for o in outside), "f": F, "bar": bars, "g": shapes,
    }

    # ---- write: the table, the data file, the page ------------------------------------------------------------------------------------
    js, css = (VENDOR / "leaflet.js").read_text(encoding="utf-8"), (VENDOR / "leaflet.css").read_text(encoding="utf-8")
    if sha256(VENDOR / "leaflet.js") != LEAFLET_SHA256:
        fails.append("scripts/vendor/leaflet-1.9.4/leaflet.js is not Leaflet 1.9.4 as published")
    css = re.sub(r"background-image:\s*url\(images/[^)]*\);?", "", css)                       # the two images it names are for controls this page does not use
    css = css.replace("behavior: url(#default#VML);", "")
    page = TEMPLATE.read_text(encoding="utf-8").replace("__TITLE__", payload["title"]).replace("__LEAFLET_VERSION__", "1.9.4").replace("/*LEAFLET_CSS*/", css).replace("/*LEAFLET_JS*/", js)
    data = "window.ICTD_LAYER = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    # nothing may be fetched: the page's own markup and script (Leaflet apart, which asks for nothing unless given a tile layer) and the data
    own = TEMPLATE.read_text(encoding="utf-8")
    for what, text in (("the page", own), ("data.js", data), ("the embedded stylesheet", css)):
        if re.search(r"<(?:script|link|img|iframe|source)[^>]*(?:src|href)\s*=\s*[\"'](?:https?:)?//", text) or re.search(r"url\(\s*[\"']?(?:https?:|//|images/)", text) or "@import" in text \
                or re.search(r"\b(?:fetch|XMLHttpRequest|importScripts|tileLayer|EventSource|WebSocket)\b", text if what != "data.js" else ""):
            fails.append(f"{what} would fetch something from the network")
    if own.count("<script src=") != 1 or '<script src="data.js">' not in own:
        fails.append("the page must load exactly one file, data.js")
    if "poverty" in data.lower() and "poverty rate (not in this file)" not in data.lower():
        fails.append("the data file mentions poverty outside the licence note")
    if len(page.encode()) + len(data.encode()) > MAX_BYTES:
        fails.append(f"index.html and data.js come to {(len(page.encode()) + len(data.encode())) / 1e6:.1f} MB, over the {MAX_BYTES / 1e6:g} MB that can be e-mailed")
    stop_if_failed("checking the page and the data file")
    OUT.mkdir(exist_ok=True)
    T.to_csv(OUT / "layer_by_unit.csv", index=False)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "data.js").write_text(data, encoding="utf-8")
    with zipfile.ZipFile(OUT / "_size_check.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(OUT / "index.html", "index.html")
        z.write(OUT / "data.js", "data.js")
    zipped = (OUT / "_size_check.zip").stat().st_size
    (OUT / "_size_check.zip").unlink()
    sizes = {"index.html": (OUT / "index.html").stat().st_size, "data.js": (OUT / "data.js").stat().st_size}
    blank = {c: int(T[c].isna().sum()) for c in T.columns if T[c].isna().any()}
    with open(OUT / "layer.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/06_build_layer.py", "script_sha256": sha256(__file__), "template_sha256": sha256(TEMPLATE), "run_utc": started, "inputs": inputs,
                   "embedded": {"leaflet": "1.9.4", "leaflet_js_sha256": LEAFLET_SHA256, "licence": "BSD 2-Clause"},
                   "outputs": {"index.html": sizes["index.html"], "data.js": sizes["data.js"], "both_bytes": sum(sizes.values()), "both_zipped_bytes": zipped, "limit_bytes": MAX_BYTES, "network_requests": 0},
                   "geometry": area_error, "floors_ha": FLOORS, "default_floor_ha": 50,
                   "layers": [{"id": L["id"], "title": L["title"], "classes": [c["label"] for c in L["classes"]], "units_per_class": {f: [int((x == i).sum()) for i in range(len(L["classes"]))] for f, x in L["_arrays"].items()}} for L in layers],
                   "omitted_on_purpose": {"columns": list(SHRUG_COLUMNS), "why": "SHRUG is CC BY-NC-SA 4.0; a shared file carrying its estimates could become a derived work under that licence. They remain in 30_need/need_by_unit.csv"},
                   "checks_passed": {"class_counts_equal_the_stage_tables_own": {k: v[0] for k, v in checks.items()}, "totals_equal_the_stage_tables_own": {k: round(v[0], 3) for k, v in totals.items()},
                                     "every_unit_has_a_shape_and_a_district": True, "no_shrug_derived_column": True, "no_network_reference": True, "districts": 30},
                   "table": {"path": "60_layer/layer_by_unit.csv", "rows": int(len(T)), "columns": int(len(T.columns)), "blank_cells": blank, "fields_per_unit_in_the_panel": FIELD_COUNT},
                   "versions": {"python": sys.version.split()[0], "geopandas": gpd.__version__, "shapely": shapely.__version__, "geos": ".".join(map(str, shapely.geos_version)), "pandas": pd.__version__}}, fh, indent=2)
    print(f"60_layer/: index.html {sizes['index.html'] / 1e6:.2f} MB + data.js {sizes['data.js'] / 1e6:.2f} MB = {sum(sizes.values()) / 1e6:.2f} MB ({zipped / 1e6:.2f} MB zipped; limit {MAX_BYTES / 1e6:g} MB); "
          f"layer_by_unit.csv n = {len(T):,} units, {len(T.columns)} columns; blank cells in {len(blank)} columns (census figures of the {n_out:,} outside-village units; shares where the land is absent)")
    for L in layers:
        f = "50" if "50" in L["_arrays"] else "all"
        print(f"  {L['id']:26s} " + "; ".join(f"{c['label']}: {int((L['_arrays'][f] == i).sum()):,}" for i, c in enumerate(L["classes"])))
    print(f"done. run_utc {started}")


if __name__ == "__main__":
    main()
