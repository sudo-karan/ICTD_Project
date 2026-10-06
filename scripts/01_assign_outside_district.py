#!/usr/bin/env python3
"""
Stage 0, an addition - a district for each outside-village unit.

    python scripts/01_assign_outside_district.py --units 10_units/units.gpkg

In : --units                                           the stage-0 layer (--outside keep): its outside_village units
     10_units/odisha_villages_pc11_datameet.gpkg        the DataMeet village polygons the layer was built from
     00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv   the 30 districts' names beside their Census-2011 codes
Out: 10_units/ and nowhere else
     outside_village_district.csv              one row per outside_village unit
     outside_village_district_summary.csv      per district: how many such units and how much land
     outside_village_district.provenance.json  inputs, UTC run time, method, checks, n

WHY. The outside-village units are the DataMeet polygons that carry no Census-2011 village code - the land outside
any revenue village, mostly reserved forest. The layer gives them no district, because the layer's district column
is a Census-2011 code and they have none. Descriptive tables and the map need one. THEY STAY OUT OF ANY REGRESSION:
this column is for description, not for a district fixed effect.

THERE IS NO DISTRICT BOUNDARY FILE IN 00_raw/. The only district geometry among the inputs is the DataMeet layer
itself, in which EVERY polygon - the uncoded ones included - carries the name of its district as of the 2001
Census (Odisha has had the same 30 districts since 1993). So the district is assigned in two ways, and both are
reported:

1. BY THE SOURCE'S OWN LABEL (the column that is delivered). An outside-village unit is one DataMeet polygon; its
   district is the district name on that polygon, turned into a Census-2011 code through the polygons that carry
   both (each 2001 name must go to exactly one 2011 code, and each code to one name, or the run stops). This is
   also what "spatial majority against district polygons" gives if the district polygons are made by dissolving
   the DataMeet layer on its district name: every such unit lies wholly inside its own district, by construction.
2. BY ITS NEIGHBOURS (an independent check, and the measure of ambiguity). For each outside-village unit, a collar
   of COLLAR_M metres is drawn round it and the area of the collar that falls on CODED villages is tallied by
   those villages' Census-2011 district. The district with the largest share is the neighbours' district. A unit
   is AMBIGUOUS when the two largest shares are within AMBIGUOUS_WITHIN of each other (5 percentage points of the
   collar on coded land) - a block on a district boundary, with as much of one district round it as of the other.
   A unit whose collar touches no coded village (it is surrounded by other outside-village units, or by sea or
   the state boundary) has no neighbours' district. Collar areas are measured in UTM zone 45N; only their shares
   are used.
THE RULE, where the two differ (measured 7 Oct 2026: 89 of the 3,138 units that have a coded neighbour):
  - Neither side is always right. Some coded villages carry a 2011 district code that differs from their own 2001
    name (the crosswalk's doing), so the neighbours can be wrong; and some labels name a district that is nowhere
    near (polygons labelled Rayagada in the middle of Nayagarh), so the label can be wrong.
  - So the collar is tallied twice, by the coded villages' 2011 codes and by their 2001 names. The LABEL IS KEPT
    whenever its district is present in the collar by either tally - the unit is then a block on or near that
    district's boundary, or its neighbours' codes are the odd ones. The label is OVERRIDDEN by the neighbours'
    district only when the unit touches coded villages and none of them belongs to the label's district by
    either tally: districts are contiguous, so such a label cannot be right. assigned_by says which happened.
  - A FEW POLYGONS CARRY NO DISTRICT NAME AT ALL (19, 4.8 km2 between them): those take the neighbours' district.

COLUMNS of outside_village_district.csv
  unit_id, unit_name                    as in the layer
  district_2001_label, subdistrict_2001_label   the names on the DataMeet polygon
  pc11_district_code, district          the district assigned, code and name
  assigned_by                           "label"; "neighbours: the polygon has no district name"; or "neighbours: the
                                        label's district is nowhere round the unit"
  label_district_share_in_collar        the share of the collar on coded villages of the LABEL's district (the larger
                                        of the two tallies); blank where there is no label or no coded neighbour
  neighbours_district_code, neighbours_district   the district with the largest share of the collar
  neighbours_share, neighbours_second_district_code, neighbours_second_share
  neighbours_n_districts                how many districts the collar touches (0: no coded neighbour)
  ambiguous                             1 if the two largest shares are within AMBIGUOUS_WITHIN of each other
  label_agrees_with_neighbours          1 / 0; blank where there is no coded neighbour or no label
  area_ha                               the unit's area as the layer has it (ellipsoidal)

Needs geopandas, shapely, pandas, numpy.
"""
import argparse, datetime, hashlib, json, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "10_units"
VILLAGES = OUT / "odisha_villages_pc11_datameet.gpkg"
DISTRICTS = ROOT / "00_raw" / "cfr_fra" / "odisha_fra_mpr_district_2025-12-31.csv"
WORK_CRS = "EPSG:32645"        # UTM 45N: for the collar only; no area that is reported is measured in it
COLLAR_M = 100.0
COLLARS_TRIED = (50.0, 100.0, 250.0)          # the count of ambiguous units is reported at each; COLLAR_M is the one delivered
AMBIGUOUS_WITHIN = 0.05
fails = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Nothing written.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def neighbours(out_geoms, coded_geoms, coded_district, collar_m):
    """For each outside polygon: {district code: share of its collar's area on coded villages}."""
    tree = shapely.STRtree(coded_geoms)
    collars = shapely.buffer(out_geoms, collar_m)
    oi, ci = tree.query(collars, predicate="intersects")
    area = shapely.area(shapely.intersection(collars[oi], coded_geoms[ci]))
    t = pd.DataFrame({"o": oi, "d": coded_district[ci], "a": area})
    t = t[t["a"] > 0].groupby(["o", "d"], as_index=False)["a"].sum()
    t["share"] = t["a"] / t.groupby("o")["a"].transform("sum")
    return t


def top_two(t, n):
    """Arrays over the n outside polygons: top district, its share, second district, its share, number of districts."""
    t = t.sort_values(["o", "share", "d"], ascending=[True, False, True])
    first = t.groupby("o").nth(0).set_index("o")
    second = t.groupby("o").nth(1).set_index("o")
    idx = np.arange(n)
    d1 = first["d"].reindex(idx); s1 = first["share"].reindex(idx)
    d2 = second["d"].reindex(idx); s2 = second["share"].reindex(idx).fillna(0.0).where(s1.notna())
    k = t.groupby("o").size().reindex(idx).fillna(0).astype(int)
    return d1.to_numpy(), s1.to_numpy(float), d2.to_numpy(), s2.to_numpy(float), k.to_numpy()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer built with --outside keep, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    v = gpd.read_file(VILLAGES, layer="villages")
    coded, out = v[v["pc11_village_code"].notna()].copy(), v[v["pc11_village_code"].isna()].copy()
    out["unit_id"] = ["OUTSIDE_" + str(i) for i in range(1, len(out) + 1)]          # as 01_build_units.py numbers them
    units = gpd.read_file(a.units, layer="units")
    u = units[units["outside_village"] == 1].set_index("unit_id")
    print(f"{VILLAGES.name}: n = {len(v):,} polygons, {len(coded):,} with a Census-2011 village code, {len(out):,} without; {a.units}: n = {len(units):,} units, {len(u):,} outside_village")

    # ---- the outside-village units are those polygons, one for one --------------------------------------------------
    if len(u) != len(out) or set(u.index) != set(out["unit_id"]):
        fails.append(f"the layer has {len(u):,} outside_village units and the village layer {len(out):,} uncoded polygons, or their ids differ")
        stop_if_failed("matching the units to the polygons")
    u = u.loc[out["unit_id"]]
    if (u["unit_name"].to_numpy() != out["name_2001"].to_numpy()).any():
        fails.append(f"{int((u['unit_name'].to_numpy() != out['name_2001'].to_numpy()).sum())} units do not carry the name of the polygon with their number")
    moved = shapely.hausdorff_distance(shapely.make_valid(u.geometry.values), shapely.make_valid(out.geometry.values))
    if np.nanmax(moved) > 1e-7:
        fails.append(f"{int((moved > 1e-7).sum())} units do not have the geometry of the polygon with their number (largest distance {np.nanmax(moved):.2e} degrees)")
    stop_if_failed("matching the units to the polygons")
    print(f"OK  the {len(out):,} outside_village units are the uncoded polygons, one for one: same number, same name, same geometry")

    # ---- 1. the label: 2001 district name -> 2011 district code, through the polygons that carry both -----------------
    names = pd.read_csv(DISTRICTS, dtype=str)[["district", "pc11_district_code"]]
    if len(names) != 30 or names["pc11_district_code"].nunique() != 30:
        fails.append(f"{DISTRICTS.name} does not list 30 districts with distinct codes")
    cross = coded.groupby(["district_2001", "pc11_district_code"]).size().rename("n").reset_index()
    by_name = cross.sort_values("n", ascending=False).groupby("district_2001").head(1).set_index("district_2001")
    purity = (by_name["n"] / cross.groupby("district_2001")["n"].sum()).rename("share_of_the_names_polygons_with_this_code")
    if by_name["pc11_district_code"].nunique() != len(by_name) or set(by_name["pc11_district_code"]) != set(names["pc11_district_code"]):
        fails.append("the 2001 district names of the coded polygons do not go one to one onto the 30 Census-2011 district codes")
    label = out["district_2001"].fillna("").str.strip()
    unlabelled = (label == "").to_numpy()
    if not set(label[~unlabelled]) <= set(by_name.index):
        fails.append(f"outside-village polygons carry district names that no coded polygon has: {sorted(set(label[~unlabelled]) - set(by_name.index))}")
    stop_if_failed("building the 2001-name to 2011-code crosswalk")
    code_of = by_name["pc11_district_code"].to_dict()
    name_of = names.set_index("pc11_district_code")["district"].to_dict()
    print(f"OK  the {len(by_name)} district names of 2001 go one to one onto the {names['pc11_district_code'].nunique()} Census-2011 codes; of the coded polygons under a name, "
          f"between {100 * purity.min():.2f} and {100 * purity.max():.2f} per cent carry that name's code (the rest: {int(cross['n'].sum() - by_name['n'].sum()):,} polygons whose 2011 district differs from their 2001 one)")
    res = pd.DataFrame({"unit_id": out["unit_id"].to_numpy(), "unit_name": out["name_2001"].to_numpy(), "district_2001_label": label.to_numpy(),
                        "subdistrict_2001_label": out["subdistrict_2001"].fillna("").str.strip().to_numpy()})
    res["pc11_district_code"] = res["district_2001_label"].map(code_of)
    res["assigned_by"] = np.where(unlabelled, "neighbours: the polygon has no district name", "label")
    print(f"    {int(unlabelled.sum())} outside-village polygons carry no district name ({out.loc[unlabelled, 'area_ha'].sum() / 100:,.1f} km2): they take their neighbours' district")

    # ---- 2. the neighbours: which district's coded villages lie round each unit ----------------------------------------
    og = shapely.make_valid(out.to_crs(WORK_CRS).geometry.values)
    cg = shapely.make_valid(coded.to_crs(WORK_CRS).geometry.values)
    cd = coded["pc11_district_code"].to_numpy()
    cd_2001 = coded["district_2001"].map(code_of).to_numpy()                       # the same villages by their own 2001 district name
    label_code = res["pc11_district_code"].to_numpy()
    both = pd.concat([neighbours(og, cg, cd, COLLAR_M), neighbours(og, cg, cd_2001, COLLAR_M)])
    own = both[both["d"].to_numpy() == pd.Series(label_code).reindex(both["o"]).to_numpy()].groupby("o")["share"].max()
    tried = {}
    for collar in COLLARS_TRIED:
        d1, s1, d2, s2, k = top_two(neighbours(og, cg, cd, collar), len(out))
        has = k > 0
        amb = has & ((s1 - s2) < AMBIGUOUS_WITHIN)
        agree = has & ~unlabelled & (d1 == res["pc11_district_code"].to_numpy())
        differs = has & ~unlabelled & ~agree
        tried[collar] = {"with_a_coded_neighbour": int(has.sum()), "without": int((~has).sum()), "ambiguous": int(amb.sum()),
                         "label_differs_from_neighbours": int(differs.sum()), "label_differs_and_not_ambiguous": int((differs & ~amb).sum()),
                         "unlabelled": int(unlabelled.sum()), "unlabelled_and_ambiguous": int((unlabelled & amb).sum()), "unlabelled_without_a_coded_neighbour": int((unlabelled & ~has).sum())}
        if collar == COLLAR_M:
            res["neighbours_district_code"] = d1
            res["neighbours_district"] = pd.Series(d1).map(name_of).to_numpy()
            res["neighbours_share"] = np.round(s1, 4)
            res["neighbours_second_district_code"] = d2
            res["neighbours_second_share"] = np.where(has, np.round(s2, 4), np.nan)
            res["neighbours_n_districts"] = k
            res["ambiguous"] = amb.astype(int)
            res["label_agrees_with_neighbours"] = pd.array(np.where(has, agree.astype(int), 0), dtype="Int64")
            res.loc[~has | unlabelled, "label_agrees_with_neighbours"] = pd.NA
            label_share = own.reindex(np.arange(len(out))).fillna(0.0).to_numpy()
            res["label_district_share_in_collar"] = np.where(has & ~unlabelled, np.round(label_share, 4), np.nan)
            nowhere = has & ~unlabelled & (label_share == 0)
            res.loc[nowhere, "assigned_by"] = "neighbours: the label's district is nowhere round the unit"
            res.loc[unlabelled | nowhere, "pc11_district_code"] = pd.Series(d1)[unlabelled | nowhere].to_numpy()
            kept_though_differing = int((differs & ~nowhere).sum())
    res["district"] = res["pc11_district_code"].map(name_of)
    res["area_ha"] = u["area_ha"].to_numpy()
    if res["pc11_district_code"].isna().any() or res["district"].isna().any():
        fails.append(f"{int(res['pc11_district_code'].isna().sum())} outside-village units got no district")
    if len(res) != len(u) or not res["unit_id"].is_unique:
        fails.append("the table does not hold each outside-village unit once")
    stop_if_failed("assigning the districts")

    summary = res.groupby(["pc11_district_code", "district"], as_index=False).agg(
        outside_village_units=("unit_id", "size"), outside_village_km2=("area_ha", lambda s: round(s.sum() / 100, 2)), ambiguous_units=("ambiguous", "sum"),
        label_differs_from_neighbours=("label_agrees_with_neighbours", lambda s: int((s == 0).sum())), no_coded_neighbour=("neighbours_n_districts", lambda s: int((s == 0).sum())),
        assigned_by_neighbours=("assigned_by", lambda s: int((s != "label").sum())))
    if int(summary["outside_village_units"].sum()) != len(res) or abs(summary["outside_village_km2"].sum() - res["area_ha"].sum() / 100) > 0.2:
        fails.append("the per-district summary does not add up to the table")
        stop_if_failed("summarising")
    OUT.mkdir(exist_ok=True)
    res.to_csv(OUT / "outside_village_district.csv", index=False)
    summary.to_csv(OUT / "outside_village_district_summary.csv", index=False)
    d = tried[COLLAR_M]
    with open(OUT / "outside_village_district.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/01_assign_outside_district.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                              {"path": str(VILLAGES.relative_to(ROOT)), "bytes": VILLAGES.stat().st_size, "sha256": sha256(VILLAGES)},
                              {"path": str(DISTRICTS.relative_to(ROOT)), "bytes": DISTRICTS.stat().st_size, "sha256": sha256(DISTRICTS)}],
                   "method": {"assigned_by": "the district name the DataMeet polygon carries (Census 2001), turned into a Census-2011 code through the coded polygons",
                              "checked_by": f"the share, by Census-2011 district, of a {COLLAR_M:g} m collar round the unit that falls on coded villages",
                              "ambiguous": f"the two largest shares within {AMBIGUOUS_WITHIN} of each other", "collar_crs": WORK_CRS,
                              "note": "there is no district boundary file in 00_raw/; the DataMeet layer's own district names are the only district geometry among the inputs"},
                   "checks_passed": {"units_are_the_uncoded_polygons_one_for_one": int(len(res)), "assigned_by": {k: int(n_) for k, n_ in res["assigned_by"].value_counts().items()}, "names_2001_to_codes_2011_one_to_one": int(len(by_name)),
                                     "share_of_a_names_coded_polygons_with_its_code_min": round(float(purity.min()), 5), "every_unit_has_a_district": True},
                   "counts": {"outside_village_units": int(len(res)), "label_kept_though_it_differs_from_the_neighbours": kept_though_differing, "districts_with_such_units": int(summary["outside_village_units"].gt(0).sum()), **{f"at_{COLLAR_M:g}_m": d},
                              "by_collar_m": {f"{k:g}": x for k, x in tried.items()}},
                   "tables": {"outside_village_district.csv": {"rows": int(len(res)), "columns": int(len(res.columns)), "blank_cells": {c: int(res[c].isna().sum()) for c in res.columns if res[c].isna().any()}},
                              "outside_village_district_summary.csv": {"rows": int(len(summary)), "columns": int(len(summary.columns))}},
                   "versions": {"python": sys.version.split()[0], "geopandas": gpd.__version__, "shapely": shapely.__version__, "pandas": pd.__version__}}, fh, indent=2)
    how = {k: int(n_) for k, n_ in res["assigned_by"].value_counts().items()}
    print(f"\noutside_village_district.csv: n = {len(res):,} units, every one with a district; assigned by: {how}; {int(summary['outside_village_units'].gt(0).sum())} districts have such units")
    print(f"  of the {d['label_differs_from_neighbours']} units whose label differs from the neighbours' district, the label is kept in {kept_though_differing} (its district is present round the unit) and overridden in {how.get(chr(110) + 'eighbours: the label' + chr(39) + 's district is nowhere round the unit', 0)}")
    print(f"  check by neighbours, {COLLAR_M:g} m collar: {d['with_a_coded_neighbour']:,} units have a coded neighbour, {d['without']:,} have none; "
          f"AMBIGUOUS (two districts within {100 * AMBIGUOUS_WITHIN:g} points): {d['ambiguous']:,}; the label differs from the neighbours' district in {d['label_differs_from_neighbours']:,}, "
          f"of which {d['label_differs_and_not_ambiguous']:,} are not ambiguous")
    print("  the same at other collars:", {f"{k:g} m": x for k, x in tried.items()})
    pd.set_option("display.width", 200)
    print(summary.to_string(index=False))
    print(f"run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
