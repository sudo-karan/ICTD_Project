#!/usr/bin/env python3
"""
Stage 0, an addition - a district for each outside-village unit.

    python scripts/01_assign_outside_district.py --units 10_units/units.gpkg

In : --units                                           the stage-0 layer (--outside keep): its outside_village units
     10_units/odisha_villages_pc11_datameet.gpkg        the DataMeet village polygons the layer was built from
     00_raw/04_boundaries/corestack_gp_odisha.json      panchayat polygons, each with a Census-2011 district code
     00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv   the 30 districts' names beside their Census-2011 codes
     10_units/units.provenance.json                     the layer's own count and area of these units, checked against
Out: 10_units/ and nowhere else
     outside_village_district.csv              one row per outside_village unit
     outside_village_district_summary.csv      per district: how many such units and how much land
     outside_village_district.provenance.json  inputs, UTC run time, method, checks, n and missingness

WHY. The outside-village units are the DataMeet polygons that carry no Census-2011 village code - the land outside
any revenue village, mostly reserved forest. The layer gives them no district, because the layer's district column
is a Census-2011 code and they have none. Descriptive tables and the map need one. THEY STAY OUT OF ANY REGRESSION:
this column is for description, not for a district fixed effect.

WHAT WAS ASKED, AND WHAT 00_raw/ HOLDS. The instruction was a spatial majority against the district boundaries in
00_raw/. There is no file of district boundaries there. There is one file of polygons that carry a district code:
the panchayat polygons of 00_raw/04_boundaries/. They are not wall to wall - they cover about a third of the
outside-village land, because that land is where no panchayat is - so a majority against them can be taken for some
units and not for others. And every DataMeet polygon, the uncoded ones included, carries the NAME of its district
as of the 2001 Census (Odisha has had the same 30 districts since 1993).

So there are three sources of a district for one of these units, and all three are in the table:

1. THE POLYGON'S OWN NAME. An outside-village unit is one DataMeet polygon; its district name is turned into a
   Census-2011 code through the polygons that carry both (each name must go to exactly one code and each code to
   one name, or the run stops).
2. THE AREA MAJORITY - the method asked for, where it can be applied. The share of the UNIT'S OWN AREA that lies on
   panchayat polygons of each district. It is taken as measurable only where at least COVER_MIN of the unit is
   covered. Where it is, the unit is AMBIGUOUS BY AREA if its two largest districts are within AMBIGUOUS_WITHIN of
   each other (5 percentage points of the unit's area): the definition asked for.
3. THE NEIGHBOURS. A collar of COLLAR_M metres is drawn round the unit and the part of it that falls on CODED
   villages is tallied by district - by the villages' 2001 district NAMES, and again by their 2011 CODES. The two
   tallies differ because some coded villages carry a 2011 code that is not their name's; where they differ the
   villages lie where their names say, so the tally by name is the one used and the other is reported beside it.
   A unit whose collar touches no coded village has no neighbours' district. AMBIGUOUS BY THE COLLAR: the two
   largest shares within AMBIGUOUS_WITHIN of each other.

HOW GOOD EACH IS can be measured on the coded villages, whose district is known from their own Census code. The run
does that and records it (measured 7 Oct 2026: the name gives the village's own district for 99.92 per cent of
them; the area majority, among villages at least half covered, for 97.88 per cent). The name is the better of the
two where the truth is known, so:

THE RULE.
  - A unit takes THE DISTRICT ITS POLYGON NAMES.
  - The name is OVERRIDDEN only when both checks contradict it and agree with each other: no coded village of the
    named district lies in the collar by either tally, AND the unit is at least half covered and its area majority
    is another district, AND that district is the neighbours' largest. One check alone does not move a unit: a
    tract on a district boundary can have all its coded neighbours across the line, and the panchayat polygons are
    wrong about one village in fifty. Where one check contradicts the name the unit is flagged, not moved.
  - A polygon with NO district name takes the area majority where it is at least half covered, and otherwise the
    neighbours' largest district by the tally by name.
assigned_by says which happened. An earlier version of this script (6 Oct 2026) said there was no district polygon
file, overrode the name on the collar alone, and took the override from the tally by code; all three were wrong.

COLUMNS of outside_village_district.csv
  unit_id, unit_name                    as in the layer
  district_2001_label, subdistrict_2001_label   the names on the DataMeet polygon (blank on 19 polygons)
  pc11_district_code, district          THE DISTRICT ASSIGNED, code and name
  assigned_by                           "label" | "two checks against the label" | "area majority: the polygon has no
                                        district name" | "neighbours: the polygon has no district name"
  area_cover_share                      the share of the unit's area on panchayat polygons of any district
  area_majority_district_code, area_majority_district, area_majority_share_of_unit,
  area_second_district_code, area_second_share_of_unit
                                        the two districts holding most of the unit's area (blank: no cover at all)
  area_majority_agrees_with_assigned    1 / 0; blank where the unit is less than COVER_MIN covered
  ambiguous_by_area                     1 / 0; blank where the unit is less than COVER_MIN covered
  neighbours_district_code, neighbours_district, neighbours_share, neighbours_second_district_code,
  neighbours_second_share, neighbours_n_districts
                                        the collar, tallied by the coded villages' 2001 names (0 districts: no coded
                                        neighbour)
  neighbours_by_code_district_code      the largest district of the same collar tallied by 2011 codes
  neighbours_agree_with_assigned        1 / 0; blank where there is no coded neighbour
  label_district_share_in_collar        the share of the collar on coded villages of the LABEL's district (the larger
                                        of the two tallies); blank where there is no label or no coded neighbour
  label_absent_from_collar              1 / 0: the named district is in the collar by neither tally; blank likewise
  ambiguous_by_collar                   1 / 0; blank where there is no coded neighbour
  ambiguous, ambiguous_basis            the one flag to use: by area where that is measurable ("area of the unit"),
                                        otherwise by the collar ("collar"), otherwise 0 ("not measurable")
  area_ha                               the unit's area as the layer has it (ellipsoidal)
Shares are of areas measured in UTM zone 45N; no area that is reported is measured in it.

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
PANCHAYATS = ROOT / "00_raw" / "04_boundaries" / "corestack_gp_odisha.json"
DISTRICTS = ROOT / "00_raw" / "cfr_fra" / "odisha_fra_mpr_district_2025-12-31.csv"
LAYER_RECORD = OUT / "units.provenance.json"
WORK_CRS = "EPSG:32645"        # UTM 45N: for shares of area only
COVER_MIN = 0.5                # the area majority is taken as measurable where this share of the unit lies on panchayat polygons
COLLAR_M = 100.0
COLLARS_TRIED = (50.0, 100.0, 250.0)          # the collar's counts are reported at each; COLLAR_M is the one delivered
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
    t = pd.DataFrame({"o": oi, "d": coded_district[ci], "a": area}).dropna(subset=["d"])
    t = t[t["a"] > 0].groupby(["o", "d"], as_index=False)["a"].sum()
    t["share"] = t["a"] / t.groupby("o")["a"].transform("sum")
    return t


def on_district_polygons(geoms, poly_geoms, poly_district):
    """For each polygon of geoms: {district code: share of ITS OWN area on the polygons of that district}. Polygons
    of one district that overlap each other are counted once."""
    tree = shapely.STRtree(poly_geoms)
    oi, ci = tree.query(geoms, predicate="intersects")
    pairs = pd.DataFrame({"o": oi, "c": ci, "d": poly_district[ci]})
    size = pairs.groupby(["o", "d"])["c"].transform("size").to_numpy()
    one = pairs[size == 1]
    rows = [pd.DataFrame({"o": one["o"].to_numpy(), "d": one["d"].to_numpy(), "a": shapely.area(shapely.intersection(geoms[one["o"].to_numpy()], poly_geoms[one["c"].to_numpy()]))})]
    many = pairs[size > 1].groupby(["o", "d"])["c"].apply(list)
    if len(many):
        merged = np.array([shapely.union_all(poly_geoms[c]) for c in many.to_numpy()], dtype=object)
        o = many.index.get_level_values("o").to_numpy()
        rows.append(pd.DataFrame({"o": o, "d": many.index.get_level_values("d").to_numpy(), "a": shapely.area(shapely.intersection(geoms[o], merged))}))
    t = pd.concat(rows, ignore_index=True)
    t = t[t["a"] > 0].copy()
    t["share"] = t["a"].to_numpy() / shapely.area(geoms)[t["o"].to_numpy()]
    return t


def top_two(t, n):
    """Arrays over the n polygons: top district, its share, second district, its share, number of districts."""
    t = t.sort_values(["o", "share", "d"], ascending=[True, False, True])
    first = t.groupby("o").nth(0).set_index("o")
    second = t.groupby("o").nth(1).set_index("o")
    idx = np.arange(n)
    d1 = first["d"].reindex(idx); s1 = first["share"].reindex(idx)
    d2 = second["d"].reindex(idx); s2 = second["share"].reindex(idx).fillna(0.0).where(s1.notna())
    k = t.groupby("o").size().reindex(idx).fillna(0).astype(int)
    return d1.to_numpy(dtype=object), s1.to_numpy(float), d2.to_numpy(dtype=object), s2.to_numpy(float), k.to_numpy()


def flag(values, known):
    """1 / 0 where known, blank elsewhere."""
    out = pd.array(np.where(known, np.asarray(values).astype(int), 0), dtype="Int64")
    out[~np.asarray(known)] = pd.NA
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer built with --outside keep, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    v = gpd.read_file(VILLAGES, layer="villages")
    is_coded = v["pc11_village_code"].notna().to_numpy()
    coded, out = v[is_coded].copy(), v[~is_coded].copy()
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
    rec = json.load(open(LAYER_RECORD))["counts"]
    if int(rec["outside_village_polygons"]) != len(u) or abs(float(rec["outside_village_km2"]) - u["area_ha"].sum() / 100) > 0.01:
        fails.append(f"{LAYER_RECORD.name} records {rec['outside_village_polygons']} outside-village polygons and {rec['outside_village_km2']} km2; the layer read here has {len(u):,} and {u['area_ha'].sum() / 100:,.2f}")
    stop_if_failed("matching the units to the polygons")
    print(f"OK  the {len(out):,} outside_village units are the uncoded polygons, one for one: same number, same name, same geometry; {u['area_ha'].sum() / 100:,.2f} km2, as the layer's record has it")

    # ---- 1. the name: 2001 district name -> 2011 district code, through the polygons that carry both -------------------
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
    own_code = coded["pc11_district_code"].astype(str).to_numpy()
    named_code = coded["district_2001"].map(code_of).to_numpy(dtype=object)                 # the coded villages by their own 2001 district name
    off_name = int((named_code != own_code).sum())
    print(f"OK  the {len(by_name)} district names of 2001 go one to one onto the 30 Census-2011 codes. On the {len(coded):,} coded villages the name gives the village's own code for "
          f"{100 * (1 - off_name / len(coded)):.2f} per cent ({off_name} do not)")
    n = len(out)
    label_code = label.map(code_of).to_numpy(dtype=object)
    label_code[unlabelled] = None

    # ---- 2. the area majority against the panchayat polygons -----------------------------------------------------------
    gp = gpd.read_file(PANCHAYATS)
    if gp["District census code"].isna().any() or set(gp["District census code"].astype(int).astype(str)) != set(names["pc11_district_code"]):
        fails.append(f"{PANCHAYATS.name}: a polygon has no district code, or its codes are not the 30 districts'")
        stop_if_failed("reading the panchayat polygons")
    pg = shapely.make_valid(gp.to_crs(WORK_CRS).geometry.values)
    pd_code = gp["District census code"].astype(int).astype(str).to_numpy()
    og = shapely.make_valid(out.to_crs(WORK_CRS).geometry.values)
    cg = shapely.make_valid(coded.to_crs(WORK_CRS).geometry.values)
    ta = on_district_polygons(og, pg, pd_code)
    cover = ta.groupby("o")["share"].sum().reindex(np.arange(n)).fillna(0.0).to_numpy()
    a1, as1, a2, as2, ak = top_two(ta, n)
    covered = cover >= COVER_MIN
    if cover.max() > 1.02:
        fails.append(f"a unit is {cover.max():.3f} covered by panchayat polygons of different districts: they overlap each other across districts")
    amb_area = covered & ((as1 - as2) < AMBIGUOUS_WITHIN)
    tc = on_district_polygons(cg, pg, pd_code)                                                    # the same on the coded villages, whose district is known
    c_cover = tc.groupby("o")["share"].sum().reindex(np.arange(len(coded))).fillna(0.0).to_numpy()
    c1 = top_two(tc, len(coded))[0]
    c_cov = c_cover >= COVER_MIN
    calib = {"coded_villages": int(len(coded)), "name_gives_the_villages_own_district": int(len(coded) - off_name), "name_gives_it_pct": round(100 * (1 - off_name / len(coded)), 2),
             "coded_villages_at_least_half_covered_by_panchayat_polygons": int(c_cov.sum()), "area_majority_gives_the_villages_own_district": int((c1[c_cov] == own_code[c_cov]).sum()),
             "area_majority_gives_it_pct": round(100 * float((c1[c_cov] == own_code[c_cov]).mean()), 2)}
    ua = shapely.area(og)
    print(f"OK  panchayat polygons: n = {len(gp):,}, {len(set(pd_code))} districts. They cover {100 * float((ua * np.minimum(cover, 1)).sum() / ua.sum()):.1f} per cent of the outside-village land; "
          f"{int(covered.sum()):,} units are at least half covered, {int((cover == 0).sum()):,} not at all")
    print(f"    where the truth is known - coded villages at least half covered, n = {calib['coded_villages_at_least_half_covered_by_panchayat_polygons']:,} - the area majority gives the village's own district for "
          f"{calib['area_majority_gives_it_pct']:.2f} per cent; the name gives it for {calib['name_gives_it_pct']:.2f} per cent of all {len(coded):,}")

    # ---- 3. the neighbours: which district's coded villages lie round each unit -----------------------------------------
    tried, at = {}, {}
    for collar in COLLARS_TRIED:
        by_n, by_c = neighbours(og, cg, named_code, collar), neighbours(og, cg, own_code, collar)
        d1, s1, d2, s2, k = top_two(by_n, n)
        e1, t1, e2, t2, _ = top_two(by_c, n)
        has = k > 0
        both = pd.concat([by_n, by_c])
        own = both[both["d"].to_numpy() == pd.Series(label_code).reindex(both["o"]).to_numpy()].groupby("o")["share"].max().reindex(np.arange(n)).fillna(0.0).to_numpy()
        amb_n, amb_c = has & ((s1 - s2) < AMBIGUOUS_WITHIN), has & ((t1 - t2) < AMBIGUOUS_WITHIN)
        differs = has & ~unlabelled & (d1 != label_code)                                         # always against the LABEL, at every collar
        absent = has & ~unlabelled & (own == 0)
        tried[collar] = {"with_a_coded_neighbour": int(has.sum()), "without": int((~has).sum()), "ambiguous_tally_by_name": int(amb_n.sum()), "ambiguous_tally_by_code": int(amb_c.sum()),
                         "label_differs_from_the_neighbours_largest_district": int(differs.sum()), "label_differs_tally_by_code": int((has & ~unlabelled & (e1 != label_code)).sum()),
                         "label_absent_from_the_collar": int(absent.sum()), "the_two_tallies_name_a_different_largest_district": int((has & (d1 != e1)).sum())}
        if collar == COLLAR_M:
            at = {"d1": d1, "s1": s1, "d2": d2, "s2": s2, "k": k, "e1": e1, "has": has, "own": own, "amb": amb_n, "absent": absent}
    has, d1, absent = at["has"], at["d1"], at["absent"]

    # ---- the rule ----------------------------------------------------------------------------------------------------------
    two = absent & covered & (a1 != label_code) & (a1 == d1)
    assigned = label_code.copy()
    how = np.where(unlabelled, "", "label").astype(object)
    assigned[two] = a1[two]; how[two] = "two checks against the label"
    by_area = unlabelled & covered
    assigned[by_area] = a1[by_area]; how[by_area] = "area majority: the polygon has no district name"
    by_nb = unlabelled & ~covered & has
    assigned[by_nb] = d1[by_nb]; how[by_nb] = "neighbours: the polygon has no district name"
    if (how == "").any():
        fails.append(f"{int((how == '').sum())} polygons carry no district name, are less than half covered by panchayat polygons and touch no coded village: no source gives them a district")
    stop_if_failed("assigning the districts")

    res = pd.DataFrame({"unit_id": out["unit_id"].to_numpy(), "unit_name": out["name_2001"].to_numpy(), "district_2001_label": label.to_numpy(),
                        "subdistrict_2001_label": out["subdistrict_2001"].fillna("").str.strip().to_numpy(), "pc11_district_code": assigned})
    res["district"] = res["pc11_district_code"].map(name_of)
    res["assigned_by"] = how
    res["area_cover_share"] = np.round(np.minimum(cover, 1.0), 4)
    res["area_majority_district_code"] = a1
    res["area_majority_district"] = pd.Series(a1).map(name_of).to_numpy()
    res["area_majority_share_of_unit"] = np.round(as1, 4)
    res["area_second_district_code"] = a2
    res["area_second_share_of_unit"] = np.where(ak > 0, np.round(as2, 4), np.nan)
    res["area_majority_agrees_with_assigned"] = flag(a1 == assigned, covered)
    res["ambiguous_by_area"] = flag(amb_area, covered)
    res["neighbours_district_code"] = d1
    res["neighbours_district"] = pd.Series(d1).map(name_of).to_numpy()
    res["neighbours_share"] = np.round(at["s1"], 4)
    res["neighbours_second_district_code"] = at["d2"]
    res["neighbours_second_share"] = np.where(has, np.round(at["s2"], 4), np.nan)
    res["neighbours_n_districts"] = at["k"]
    res["neighbours_by_code_district_code"] = at["e1"]
    res["neighbours_agree_with_assigned"] = flag(d1 == assigned, has)
    res["label_district_share_in_collar"] = np.where(has & ~unlabelled, np.round(at["own"], 4), np.nan)
    res["label_absent_from_collar"] = flag(absent, has & ~unlabelled)
    res["ambiguous_by_collar"] = flag(at["amb"], has)
    res["ambiguous"] = np.where(covered, amb_area, np.where(has, at["amb"], False)).astype(int)
    res["ambiguous_basis"] = np.where(covered, "area of the unit", np.where(has, "collar", "not measurable"))
    res["area_ha"] = u["area_ha"].to_numpy()
    if res["pc11_district_code"].isna().any() or res["district"].isna().any():
        fails.append(f"{int(res['pc11_district_code'].isna().sum())} outside-village units got no district")
    if len(res) != len(u) or not res["unit_id"].is_unique:
        fails.append("the table does not hold each outside-village unit once")
    stop_if_failed("assigning the districts")

    km2 = lambda sel: round(float(res.loc[sel, "area_ha"].sum()) / 100, 2)
    area_differs = covered & (a1 != assigned)
    one_check = (area_differs | (absent & (how == "label")))
    summary = res.assign(_differs=area_differs.astype(int), _absent=absent.astype(int), _unchecked=(~covered & ~has).astype(int)).groupby(["pc11_district_code", "district"], as_index=False).agg(
        outside_village_units=("unit_id", "size"), outside_village_km2=("area_ha", lambda s: round(s.sum() / 100, 2)), ambiguous_units=("ambiguous", "sum"),
        area_majority_names_another_district=("_differs", "sum"), named_district_absent_from_collar=("_absent", "sum"), no_check_possible=("_unchecked", "sum"),
        not_assigned_by_label=("assigned_by", lambda s: int((s != "label").sum())))
    if int(summary["outside_village_units"].sum()) != int(rec["outside_village_polygons"]) or abs(float(summary["outside_village_km2"].sum()) - float(rec["outside_village_km2"])) > 0.2:
        fails.append(f"the per-district summary holds {int(summary['outside_village_units'].sum()):,} units and {summary['outside_village_km2'].sum():,.2f} km2; {LAYER_RECORD.name} records {rec['outside_village_polygons']} and {rec['outside_village_km2']}")
        stop_if_failed("summarising")
    OUT.mkdir(exist_ok=True)
    res.to_csv(OUT / "outside_village_district.csv", index=False)
    summary.to_csv(OUT / "outside_village_district_summary.csv", index=False)
    back = pd.read_csv(OUT / "outside_village_district.csv", dtype=str, keep_default_na=False)       # blanks are counted in the file as written
    blank = {c: int((back[c] == "").sum()) for c in back.columns if (back[c] == "").any()}
    counts = {"outside_village_units": int(len(res)), "outside_village_km2": km2(np.ones(n, bool)), "districts_with_such_units": int(summary["outside_village_units"].gt(0).sum()),
              "assigned_by": {k_: {"units": int(n_), "km2": km2(res["assigned_by"] == k_)} for k_, n_ in res["assigned_by"].value_counts().items()},
              "area_majority": {"cover_of_the_outside_village_land_pct": round(100 * float((ua * np.minimum(cover, 1)).sum() / ua.sum()), 1), "units_with_some_cover": int((cover > 0).sum()), "units_with_no_cover": int((cover == 0).sum()),
                                "measurable_units_at_least_half_covered": {"units": int(covered.sum()), "km2": km2(covered)}, "not_measurable": {"units": int((~covered).sum()), "km2": km2(~covered)},
                                "agrees_with_the_assigned_district": {"units": int((covered & ~area_differs).sum()), "km2": km2(covered & ~area_differs)},
                                "names_another_district": {"units": int(area_differs.sum()), "km2": km2(area_differs)}, "names_another_district_than_the_label": int((covered & ~unlabelled & (a1 != label_code)).sum()),
                                "ambiguous_by_area_two_districts_within_5_points_of_the_units_area": {"units": int(amb_area.sum()), "km2": km2(amb_area)}},
              f"collar_{COLLAR_M:g}_m": {**tried[COLLAR_M], "label_absent_and_kept_one_check_only": int((absent & (how == "label")).sum()), "label_absent_and_overridden_two_checks": int(two.sum()),
                                           "label_absent_and_the_area_majority_is_measurable": int((absent & covered).sum()), "of_those_the_area_majority_sides_with_the_label": int((absent & covered & (a1 == label_code)).sum())},
              "by_collar_m": {f"{k_:g}": x for k_, x in tried.items()},
              "flagged_not_moved_one_check_contradicts_the_assigned_district": {"units": int(one_check.sum()), "km2": km2(one_check)},
              "no_check_possible_neither_covered_nor_with_a_coded_neighbour": {"units": int((~covered & ~has).sum()), "km2": km2(~covered & ~has)},
              "ambiguous_the_one_flag": {"units": int(res["ambiguous"].sum()), "by_basis": {k_: int(v_) for k_, v_ in res.loc[res["ambiguous"] == 1, "ambiguous_basis"].value_counts().items()},
                                         "units_by_basis": {k_: int(v_) for k_, v_ in res["ambiguous_basis"].value_counts().items()}}}
    entry = lambda p: {"path": str(Path(p).resolve().relative_to(ROOT)), "bytes": Path(p).stat().st_size, "sha256": sha256(p)}
    with open(OUT / "outside_village_district.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/01_assign_outside_district.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)}, entry(VILLAGES), entry(PANCHAYATS), entry(DISTRICTS), entry(LAYER_RECORD)],
                   "method": {"assigned_by": "the district name the DataMeet polygon carries (Census 2001), turned into a Census-2011 code through the coded polygons",
                              "overridden_when": "no coded village of the named district lies in the collar by either tally, AND the unit is at least half covered by panchayat polygons and its area majority is another district, AND that district is the neighbours' largest",
                              "no_name": "the area majority where the unit is at least half covered; otherwise the neighbours' largest district by the tally by 2001 name",
                              "area_majority": f"the share of the unit's own area on the panchayat polygons of each district ({PANCHAYATS.name}); measurable where at least {COVER_MIN} of the unit is covered",
                              "neighbours": f"the share, by district, of a {COLLAR_M:g} m collar round the unit that falls on coded villages, tallied by their 2001 names (used) and by their 2011 codes (reported)",
                              "ambiguous": f"the two largest districts within {AMBIGUOUS_WITHIN} of each other: of the unit's own area where the area majority is measurable, otherwise of the collar", "shares_measured_in": WORK_CRS,
                              "note": "00_raw/ holds no district boundary file. It holds panchayat polygons with a district code, which cover about a third of this land; the method asked for (area majority) is applied where they allow"},
                   "how_good_each_source_is_on_villages_whose_district_is_known": calib,
                   "checks_passed": {"units_are_the_uncoded_polygons_one_for_one": int(len(res)), "count_and_area_equal_the_layers_own_record": True, "names_2001_to_codes_2011_one_to_one": int(len(by_name)),
                                     "share_of_a_names_coded_polygons_with_its_code_min": round(float(purity.min()), 5), "every_unit_has_a_district": True, "largest_cover_of_a_unit_by_panchayat_polygons": round(float(cover.max()), 4)},
                   "counts": counts,
                   "tables": {"outside_village_district.csv": {"rows": int(len(res)), "columns": int(len(res.columns)), "blank_cells": blank},
                              "outside_village_district_summary.csv": {"rows": int(len(summary)), "columns": int(len(summary.columns))}},
                   "versions": {"python": sys.version.split()[0], "geopandas": gpd.__version__, "shapely": shapely.__version__, "pandas": pd.__version__}}, fh, indent=2)
    am, cl = counts["area_majority"], counts[f"collar_{COLLAR_M:g}_m"]
    print(f"\noutside_village_district.csv: n = {len(res):,} units, every one with a district; {counts['districts_with_such_units']} districts have such units. Assigned by:")
    for k_, x in counts["assigned_by"].items():
        print(f"    {k_}: {x['units']:,} units, {x['km2']:,.1f} km2")
    print(f"  AREA MAJORITY (the method asked for) is measurable for {am['measurable_units_at_least_half_covered']['units']:,} units ({am['measurable_units_at_least_half_covered']['km2']:,.0f} km2) and not for "
          f"{am['not_measurable']['units']:,} ({am['not_measurable']['km2']:,.0f} km2). Where measurable it agrees with the assigned district in {am['agrees_with_the_assigned_district']['units']:,} and names another in "
          f"{am['names_another_district']['units']} ({am['names_another_district']['km2']:,.1f} km2). AMBIGUOUS BY AREA (two districts within {100 * AMBIGUOUS_WITHIN:g} points of the unit's area): {am['ambiguous_by_area_two_districts_within_5_points_of_the_units_area']['units']}")
    print(f"  NEIGHBOURS, {COLLAR_M:g} m collar: {cl['with_a_coded_neighbour']:,} units have a coded neighbour, {cl['without']:,} have none; ambiguous by the tally by name {cl['ambiguous_tally_by_name']}, by code {cl['ambiguous_tally_by_code']}; "
          f"the named district is absent from the collar in {cl['label_absent_from_the_collar']}: {cl['label_absent_and_overridden_two_checks']} overridden (the area majority agrees with the neighbours), {cl['label_absent_and_kept_one_check_only']} kept and flagged")
    print(f"  flagged, not moved (one check contradicts the assigned district): {counts['flagged_not_moved_one_check_contradicts_the_assigned_district']['units']} units, {counts['flagged_not_moved_one_check_contradicts_the_assigned_district']['km2']:,.1f} km2; "
          f"no check possible: {counts['no_check_possible_neither_covered_nor_with_a_coded_neighbour']['units']} units, {counts['no_check_possible_neither_covered_nor_with_a_coded_neighbour']['km2']:,.1f} km2")
    print("  the collar at other widths:", json.dumps(counts["by_collar_m"]))
    print(f"  blank cells: {blank}")
    pd.set_option("display.width", 220)
    print(summary.to_string(index=False))
    print(f"run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
