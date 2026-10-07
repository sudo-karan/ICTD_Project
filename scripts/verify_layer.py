#!/usr/bin/env python3
"""
A direct check of the demo layer against the stage tables. Reads, writes nothing, exits 1 if a check fails.

    python scripts/verify_layer.py

It shares no code with scripts/06_build_layer.py and does not read 60_layer/layer_by_unit.csv. It opens
60_layer/data.js - the file the map reads - and, for EVERY unit and EVERY figure the map can show, rebuilds what
should be on the screen from the tables the figures come from:
    10_units/units.gpkg (attributes and shapes), outside_village_district.csv
    20_degradation/hansen_by_unit.csv, hansen_loss_by_canopy_band_by_unit.csv, corestack_by_unit.csv,
                   corestack_by_unit_bands.csv, agreement_by_unit.csv
    30_need/need_by_unit.csv        40_allocation/allocation_by_unit.csv
It goes behind degradation_by_unit.csv to the tables that was assembled from. It also rebuilds every class of
every layer at both minimum-forest settings, recounts the legend, checks that each unit's drawn shape lies where
the unit is, and that the two files ask for nothing from the network and carry no SHRUG-derived figure.
This is the machine's half of the layer's verification; the other half is opening the map and clicking.
"""
import json, re, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
results = []


def check(what, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {what}" + (f"   {detail}" if detail else ""))


raw = (ROOT / "60_layer/data.js").read_text(encoding="utf-8")
assert raw.startswith("window.ICTD_LAYER = ") and raw.rstrip().endswith(";")
D = json.loads(raw[len("window.ICTD_LAYER = "):].rstrip()[:-1])
page = (ROOT / "60_layer/index.html").read_text(encoding="utf-8")
ids = D["id"]
n = len(ids)
read = lambda p: pd.read_csv(ROOT / p, dtype={"unit_id": str, "pc11_district_code": str}).set_index("unit_id")
g = gpd.read_file(ROOT / "10_units/units.gpkg", layer="units")
g["unit_id"] = g["unit_id"].astype(str)
g = g.set_index("unit_id")
check("the map holds each unit of the layer once", n == len(g) and len(set(ids)) == n and set(ids) == set(g.index), f"n = {n:,}")
g = g.loc[ids]
h, hb, c, cb, ag, nd, al = (read(p).loc[ids] for p in ("20_degradation/hansen_by_unit.csv", "20_degradation/hansen_loss_by_canopy_band_by_unit.csv", "20_degradation/corestack_by_unit.csv",
                                                       "20_degradation/corestack_by_unit_bands.csv", "20_degradation/agreement_by_unit.csv", "30_need/need_by_unit.csv", "40_allocation/allocation_by_unit.csv"))
od = read("10_units/outside_village_district.csv")
dn = pd.read_csv(ROOT / "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv", dtype=str).set_index("pc11_district_code")["district"]
out = (g["outside_village"] == 1).to_numpy()
F = np.array(D["f"], dtype=object)
check("the hatching marks exactly the outside_village units", D["out"] == "".join("1" if o else "0" for o in out), f"{int(out.sum()):,} hatched")

# ---- every figure of every unit --------------------------------------------------------------------------------------------
fmt = lambda v, unit, d=2: np.array(["" if pd.isna(x) else f"{x:,.{d}f}{unit}" for x in np.asarray(v, float)], dtype=object)
number = lambda s: np.array([float(re.sub(r"[^0-9.\-]", "", str(x).split("(")[0])) if re.search(r"\d", str(x).split("(")[0]) else np.nan for x in s])
bad = {}


def same(field, expected, what):
    wrong = np.flatnonzero(F[:, field] != np.asarray(expected, dtype=object))
    bad[what] = len(wrong)
    check(f"{what}: all {n:,} units", len(wrong) == 0, "" if len(wrong) == 0 else f"{len(wrong):,} differ, e.g. unit {ids[wrong[0]]}: shown '{F[wrong[0], field]}', table gives '{expected[wrong[0]]}'")


def near(field, expected, tol, what, undefined):
    shown = number(F[:, field])
    exp = np.asarray(expected, float)
    ok = (np.isnan(exp) & np.array([undefined in str(x) or str(x) == "" for x in F[:, field]])) | (np.abs(shown - exp) <= tol)
    check(f"{what}: all {n:,} units (to {tol:g})", ok.all(), "" if ok.all() else f"{int((~ok).sum()):,} differ, e.g. unit {ids[np.flatnonzero(~ok)[0]]}: shown '{F[np.flatnonzero(~ok)[0], field]}', table gives {exp[np.flatnonzero(~ok)[0]]}")


name = g["unit_name"].fillna("").astype(str).str.strip().to_numpy()
same(0, np.where(name == "", "(no name on the polygon)", name), "unit name")
same(1, np.array(ids, dtype=object), "unit id")
same(2, np.where(out, "Outside-village unit: land outside any revenue village", "LGD panchayat unit"), "unit type")
code = g["pc11_district_code"].astype("string").to_numpy(dtype=object)
code[out] = od["pc11_district_code"].reindex(np.array(ids)[out]).to_numpy()
district = pd.Series(code).map(dn).to_numpy()
check("district: the name shown begins with the district of the unit's Census code, or of outside_village_district.csv", all(str(F[i, 3]).split(" (")[0] == district[i] for i in range(n)),
      f"{len(set(district))} districts; {int(sum('(by ' in str(x) for x in F[:, 3])):,} carry how they were assigned")
check("district: an outside-village unit, and only one, says how its district was assigned", all(("(by " in str(F[i, 3])) == bool(out[i]) for i in range(n)))
words = {"label": "name on the DataMeet polygon)", "two checks against the label": "which both contradict the name on the polygon",
         "area majority: the polygon has no district name": "panchayat polygons under it (the polygon carries no district name",
         "neighbours: the polygon has no district name": "its neighbours (the polygon carries no district name"}
by = od["assigned_by"].reindex(ids)
check("district: each outside-village unit says the way ITS district was assigned, as outside_village_district.csv has it",
      set(by[out].dropna()) <= set(words) and all(sum(w in str(F[i, 3]) or (k == "label" and str(F[i, 3]).split(",")[0].endswith("name on the DataMeet polygon")) for k, w in words.items() if k == by.iloc[i]) == 1
                                                 and sum(w.rstrip(")") in str(F[i, 3]) for w in words.values()) == 1 for i in range(n) if out[i]), str(by[out].value_counts().to_dict()))
amb = od["ambiguous"].reindex(ids).fillna(0).to_numpy()
check("district: the units flagged ambiguous are those of outside_village_district.csv", all(("ambiguous" in str(F[i, 3])) == bool(amb[i]) for i in range(n)), f"{int(amb.sum())} ambiguous")
same(4, fmt(g["area_ha"], " ha"), "area")
same(5, fmt(h["forest_ha"], " ha"), "forest in 2000")
near(6, 100 * h["forest_ha"] / g["area_ha"], 0.0051, "forest as a share of the unit", "zzz")
land10 = hb["area_ha_gt10le30"] + hb["area_ha_gt30"]
near(7, land10, 0.0051, "land with canopy above 10 %", "zzz")
same(8, fmt(h["hansen_loss_ha"], " ha"), "loss 2001-2025")
near(9, (100 * h["hansen_loss_ha"] / h["forest_ha"]).where(h["forest_ha"] > 0), 0.0051, "loss as a share of the forest", "not defined")
near(10, sum(h[f"hansen_loss_ha_{y}"] for y in range(2017, 2024)), 0.0051, "loss 2017-2023", "zzz")
same(11, fmt(hb["area_ha_gt10le30"], " ha"), "land with 10 to 30 % canopy")
same(12, fmt(hb["loss_ha_gt10le30"], " ha"), "loss on it")
near(13, (100 * hb["loss_ha_gt10le30"] / hb["area_ha_gt10le30"]).where(hb["area_ha_gt10le30"] > 0), 0.0051, "that loss as a share of that land", "not defined")
same(14, fmt(hb["area_ha_le10"], " ha"), "land with 10 % canopy or less")
same(15, fmt(hb["loss_ha_le10"], " ha"), "loss on it")
same(16, fmt(hb["loss_ha_eq0"], " ha"), "loss on land with no canopy in 2000")
klass = {"loss": ["lost"], "degradation": ["degradation"], "partial_degradation": ["partial3", "partial4"], "no_change": ["nochange"], "improvement": ["improvement"], "gain": ["gained"]}
area = {k: sum(cb[f"class_{p}_ha_{b}"] for p in parts for b in ("gt10le30", "gt30")) for k, parts in klass.items()}
valued = sum(area.values())
near(17, valued, 0.0051, "land with a CoRE Stack class", "zzz")
for j, k in enumerate(klass):
    shown_ha = number(F[:, 18 + j])
    check(f"CoRE Stack {k}: hectares, all {n:,} units (to the printed digit)", (np.abs(shown_ha - area[k].to_numpy()) <= 0.00501).all(), f"largest difference {np.abs(shown_ha - area[k].to_numpy()).max():.5f} ha")
    shown_pct = np.array([float(re.search(r"\(([\-0-9.,]+) %\)", str(x)).group(1).replace(",", "")) if "(" in str(x) else np.nan for x in F[:, 18 + j]])
    exp = (100 * area[k] / valued).where(valued > 0).to_numpy()
    ok = (np.isnan(exp) & np.isnan(shown_pct)) | (np.abs(shown_pct - exp) <= 0.00501)
    check(f"CoRE Stack {k}: share of the land with a class, all units (to the printed digit)", ok.all(), "" if ok.all() else f"{int((~ok).sum())} differ, e.g. {ids[np.flatnonzero(~ok)[0]]}: shown {shown_pct[np.flatnonzero(~ok)[0]]}, tables give {exp[np.flatnonzero(~ok)[0]]}")
near(24, (100 * (area["degradation"] - area["improvement"]) / valued).where(valued > 0), 0.0101, "Degradation minus Improvement", "not defined")
same(25, fmt(c["corestack_degradation_ha"], " ha"), "Degradation on all land the product covers")
same(26, fmt(c["corestack_tree_cover_start_ha"], " ha"), "the product's tree cover at the start")
label = {"both": "Both measures flag this unit", "hansen_only": "Hansen only (clearance)", "corestack_only": "CoRE Stack only (degradation)", "neither": "Neither", "insufficient_forest": "Insufficient forest to assess"}
same(27, ag["agreement_class"].map(label).to_numpy(), "agreement class")
loss1723 = sum(hb[f"loss_ha_{b}_{y}"] for b in ("gt10le30", "gt30") for y in range(2017, 2024))
near(28, (100 * loss1723 / land10).where(land10 > 0), 0.0051, "Hansen loss 2017-2023 as a share of the reference land", "not defined")
near(29, (100 * area["degradation"] / valued).where(valued > 0), 0.0101, "CoRE Stack Degradation rate in the agreement panel", "not defined")
near(30, land10, 0.0051, "reference land", "zzz")
same(31, np.array([f"{int(x):,}" for x in al["n_works"]], dtype=object), "MGNREGA works")
for j, col in ((32, "expenditure_total"), (33, "expenditure_plantation_category"), (34, "expenditure_forest_named_worktype"), (35, "expenditure_water")):
    same(j, np.array(["not recorded" if pd.isna(x) else f"Rs {x / 1e5:,.2f} lakh" for x in al[col]], dtype=object), col)
nc = "no census data for this land"
same(36, np.where(out, nc, [("" if pd.isna(x) else f"{int(round(x)):,}") for x in nd["population"]]), "population")
same(37, np.where(out, nc, [("" if pd.isna(x) else f"{int(round(x)):,}") for x in nd["households"]]), "households")
same(38, np.where(out, nc, ["not defined: no resident population" if pd.isna(x) else f"{100 * x:,.2f} %" for x in nd["st_share"]]), "Scheduled Tribe share")
same(39, np.where(out, nc, ["not defined: no resident population" if pd.isna(x) else f"{100 * x:,.2f} %" for x in nd["sc_share"]]), "Scheduled Caste share")
same(40, np.where(out, nc, ["no index for this unit's villages" if pd.isna(x) else f"{x:,.2f}" for x in nd["adi_2011"]]), "Aggregate Development Index 2011")
check("every outside_village unit says 'no census data for this land' in all five census lines, and no other unit does", all(((F[:, j] == nc) == out).all() for j in range(36, 41)), f"{int(out.sum()):,} units")
check("no blank cell is shown to the reader", not (F[:, :41] == "").any(), f"{int((F[:, :41] == '').sum())} blank among {F[:, :41].size:,} cells")
fh = h["forest_ha"].to_numpy()
check("the warning on small forests is on the units under 1 ha and under 50 ha of forest, and no other", all(("Under 1 ha" in F[i, 41]) == (fh[i] < 1) and ("Under 50 ha" in F[i, 41]) == (1 <= fh[i] < 50) for i in range(n)),
      f"{int((fh < 1).sum()):,} under 1 ha, {int(((fh >= 1) & (fh < 50)).sum()):,} from 1 to 50 ha")

# ---- every class of every layer, both minimum-forest settings -----------------------------------------------------------------
L = {x["id"]: x for x in D["layers"]}
codes = D["codes"]


def shown(layer, setting):
    return np.array([L[layer]["classes"][codes.index(ch)]["label"] for ch in L[layer]["cls"][setting]], dtype=object)


def bins(v, edges, labels):
    """The class of each value as the reader sees the value: rounded to the two decimals it is printed with."""
    return np.array([labels[int(np.searchsorted(edges, round(float(x), 2), side="left"))] for x in v], dtype=object)


r2 = lambda v: np.round(np.asarray(v, float), 2)


GREY = "Insufficient forest to assess"
loss_labels = ["Up to 1 %", "1 to 2.5 %", "2.5 to 5 %", "5 to 10 %", "10 to 20 %", "More than 20 %"]
fp = (100 * h["forest_ha"] / g["area_ha"]).to_numpy()
exp = np.where(fh <= 0, "No forest by this measure", bins(fp, [1, 10, 30, 60], ["Up to 1 %", "1 to 10 %", "10 to 30 %", "30 to 60 %", "More than 60 %"]))
check("classes of 'Area under forests'", (shown("forest_area", "all") == exp).all(), str(pd.Series(exp).value_counts().to_dict()))
for floor in ("50", "1"):
    f = float(floor)
    lp = np.nan_to_num((100 * h["hansen_loss_ha"] / h["forest_ha"]).to_numpy())
    exp = np.where(fh < f, GREY, np.where(r2(lp) <= 0, "No loss recorded", bins(lp, [1, 2.5, 5, 10, 20], loss_labels)))
    check(f"classes of 'Tree cover loss', minimum {floor} ha", (shown("hansen_loss", floor) == exp).all(), f"grey {int((exp == GREY).sum()):,}")
    band = hb["area_ha_gt10le30"].to_numpy()
    bp = np.nan_to_num((100 * hb["loss_ha_gt10le30"] / hb["area_ha_gt10le30"]).to_numpy())
    exp = np.where(band < f, GREY, np.where(r2(bp) <= 0, "No loss recorded", bins(bp, [1, 2.5, 5, 10, 20], loss_labels)))
    check(f"classes of 'Loss on open canopy', minimum {floor} ha", (shown("canopy_band_loss", floor) == exp).all(), f"grey {int((exp == GREY).sum()):,}")
    ref = np.minimum(land10.to_numpy(), valued.to_numpy())
    dp = np.nan_to_num((100 * area["degradation"] / valued).where(valued > 0).to_numpy())
    exp = np.where(ref < f, GREY, bins(dp, [5, 15, 25, 35], ["Up to 5 %", "5 to 15 %", "15 to 25 %", "25 to 35 %", "More than 35 %"]))
    check(f"classes of 'Forest health and degradation', minimum {floor} ha", (shown("corestack_degradation", floor) == exp).all(), f"grey {int((exp == GREY).sum()):,}")
    npct = np.nan_to_num((100 * (area["degradation"] - area["improvement"]) / valued).where(valued > 0).to_numpy())
    exp = np.where(ref < f, GREY, bins(npct, [-10, -2, 2, 10, 20], ["Net improvement, more than 10 points", "Net improvement, 2 to 10 points", "Within 2 points: no net change", "Net degradation, 2 to 10 points",
                                                                    "Net degradation, 10 to 20 points", "Net degradation, more than 20 points"]))
    check(f"classes of 'Degradation net of improvement', minimum {floor} ha", (shown("corestack_net", floor) == exp).all(), f"grey {int((exp == GREY).sum()):,}")
check("classes of 'Do the two measures agree?'", (shown("agreement", "all") == ag["agreement_class"].map(label).to_numpy()).all(), str(ag["agreement_class"].value_counts().to_dict()))
works, spent = al["n_works"].to_numpy(float), (al["expenditure_total"] / 1e5).to_numpy(float)
exp = np.where(works <= 0, "No works geotagged here", np.where(np.isnan(spent), "Works recorded, expenditure not",
               bins(np.nan_to_num(spent), [10, 50, 100, 200, 400], ["Up to Rs 10 lakh", "Rs 10 to 50 lakh", "Rs 50 to 100 lakh", "Rs 100 to 200 lakh", "Rs 200 to 400 lakh", "More than Rs 400 lakh"])))
check("classes of 'Past allocation'", (shown("allocation", "all") == exp).all(), f"no works {int((works <= 0).sum()):,}; expenditure not recorded {int((np.isnan(spent) & (works > 0)).sum())}")
fn = (al["expenditure_forest_named_worktype"] / 1e5).to_numpy(float)
exp = np.where(np.isnan(fn), np.where(works <= 0, "None", "Works recorded, expenditure not"), np.where(r2(np.nan_to_num(fn)) <= 0, "None", bins(np.nan_to_num(fn), [1, 5, 20], ["Up to Rs 1 lakh", "Rs 1 to 5 lakh", "Rs 5 to 20 lakh", "More than Rs 20 lakh"])))
check("classes of 'Forest-named expenditure'", (shown("forest_named_expenditure", "all") == exp).all(), f"some {int((fn > 0).sum()):,}")
st = (100 * nd["st_share"]).to_numpy(float)
exp = np.where(out, "No census data for this land", np.where(np.isnan(st), "No resident population in the census rows",
               np.where(r2(np.nan_to_num(st)) < 18, "Less than 18 %", bins(np.nan_to_num(st), [33, 50], ["18 to 33 %", "33 to 50 %", "More than 50 %"]))))
check("classes of 'Scheduled Tribe share'", (shown("st_share", "all") == exp).all(), f"no census data {int(out.sum()):,}; no population {int((np.isnan(st) & ~out).sum())}")
adi = nd["adi_2011"].to_numpy(float)
exp = np.where(out, "No census data for this land", np.where(np.isnan(adi), "No index for this unit's villages", bins(np.nan_to_num(adi), [6, 7, 8, 9.5], ["Up to 6", "6 to 7", "7 to 8", "8 to 9.5", "More than 9.5"])))
check("classes of 'Aggregate Development Index 2011'", (shown("adi_2011", "all") == exp).all(), f"no census data {int(out.sum()):,}; no index {int((np.isnan(adi) & ~out).sum())}")
wrong = 0
for lid, lay in L.items():
    if lay.get("pending"):
        continue
    for setting, s in lay["cls"].items():
        for k in range(len(lay["classes"])):
            wrong += lay["counts"][setting][k] != f"{s.count(codes[k]):,} units"
check("the number of units printed beside every legend class is the number of units drawn in it", wrong == 0, f"{wrong} differ")
check("no unit on a census layer is drawn as a value when it is an outside_village unit", not any(lab in ("Less than 18 %", "Up to 6") for lab in shown("st_share", "all")[out]) and not any(lab == "Up to 6" for lab in shown("adi_2011", "all")[out]))
check("NIRv is listed and marked pending", any(x["id"] == "nirv" and x.get("pending") for x in D["layers"]))

# ---- shapes: each unit's drawn shape lies where the unit is ---------------------------------------------------------------------
def bbox(shape):
    xs, ys = [], []
    for poly in shape:
        for ring in poly:
            a = np.asarray(ring, float).reshape(-1, 2).cumsum(axis=0) / 1e5
            xs += [a[:, 0].min(), a[:, 0].max()]
            ys += [a[:, 1].min(), a[:, 1].max()]
    return min(xs), min(ys), max(xs), max(ys)


# A simplified boundary only drops points, so a unit's drawn shape must lie inside the unit's own bounding box (to the 0.00001
# degree it is stored at) - which another unit's shape would not - and must still span most of it.
drawn = np.array([bbox(s) for s in D["g"]])
true = g.geometry.bounds.to_numpy()
inside = (drawn[:, 0] >= true[:, 0] - 2e-5) & (drawn[:, 1] >= true[:, 1] - 2e-5) & (drawn[:, 2] <= true[:, 2] + 2e-5) & (drawn[:, 3] <= true[:, 3] + 2e-5)
check("every unit has a shape, and it lies inside the unit's own bounding box", inside.all(), f"{int((~inside).sum())} do not")
span = np.minimum((drawn[:, 2] - drawn[:, 0]) / np.maximum(true[:, 2] - true[:, 0], 1e-9), (drawn[:, 3] - drawn[:, 1]) / np.maximum(true[:, 3] - true[:, 1], 1e-9))
off = np.abs(drawn - true).max(axis=1)
check("every unit's shape still spans at least half of its bounding box each way", (span >= 0.5).all(),
      f"smallest span {span.min():.2f}; the box moved by more than 0.003 degrees (about 300 m) in {int((off > 0.003).sum())} units - thin spurs dropped by the simplification; largest {off.max():.5f} degrees")
check("30 districts are outlined and named", len(D["districts"]) == 30 and len({d["name"] for d in D["districts"]}) == 30 and sum(d["n_units"] for d in D["districts"]) == n)

# ---- the two files ask for nothing, and carry nothing they should not -------------------------------------------------------------
own = page.split("<script>")[-1]
check("the page loads one file, data.js, and its own script asks for nothing else", page.count("<script src=") == 1 and '<script src="data.js">' in page and not re.search(r"\b(fetch|XMLHttpRequest|tileLayer|importScripts)\b", own))
check("no stylesheet, image or script is taken from the network", not re.search(r"<(?:link|img|iframe|script)[^>]*(?:src|href)\s*=\s*[\"'](?:https?:)?//", page) and not re.search(r"url\(\s*[\"']?(?:https?:|//|images/)", page) and "@import" not in page)
lower = raw.lower()
check("no SHRUG-derived figure is in the data: 'poverty' occurs only in the licence note", lower.count("poverty") == lower.count("poverty rate (not in this file)") + lower.count("small-area poverty estimates") and "shrid" not in lower,
      f"'poverty' occurs {lower.count('poverty')} times")
size = (ROOT / "60_layer/index.html").stat().st_size + (ROOT / "60_layer/data.js").stat().st_size
check("the two files together are under 25 MB", size < 25_000_000, f"{size / 1e6:.2f} MB")
print(f"\n{sum(results)} of {len(results)} checks passed; n = {n:,} units, {F.shape[1]} fields a unit, {sum(len(x['cls']) for x in L.values() if not x.get('pending'))} class arrays")
sys.exit(0 if all(results) else 1)
