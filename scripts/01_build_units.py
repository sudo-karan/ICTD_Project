#!/usr/bin/env python3
"""
Stage 0 - build the analysis unit layer for Odisha.

The unit is the LGD PANCHAYAT ID of the village -> panchayat mapping: every village polygon carrying the
same Panchayat_ID is dissolved into one polygon.

    python scripts/01_build_units.py --villages 10_units/odisha_villages_pc11_datameet.gpkg \
        --lgd-map 00_raw/02_mgnrega/mis_panel/LGD_village_panchayat_mapping.csv \
        --unit lgd_panchayat --outside keep --out 10_units/units.gpkg

AN LGD PANCHAYAT ID IS NOT A GRAM PANCHAYAT. In the mapping file Panchayat_ID is a running index over
(panchayat name, Census-2011 sub-district): Odisha has 8,152 ids, exactly one per name-and-sub-district
pair, but only 6,645 distinct name-and-district pairs. A gram panchayat that straddles a sub-district line
is therefore two or more units, and 162 ids are nameless catch-alls for villages with no named panchayat.
Call the unit an LGD panchayat, never a GP. docs/UNITS.md has the counts.

Without --lgd-map it builds village-level units instead (--unit village), which is useful for testing
the rest of the pipeline without the mapping. Village units are NOT safe to aggregate on as they stand:
a multi-part village is several polygons sharing one Census-2011 code, so unit_id repeats.

AREA. Every area this script reports or writes - area_ha per unit, and the totals it prints - is the area of
the polygon on the WGS84 ellipsoid (geodesic polygon area, pyproj), in hectares. Until 6 October 2026 it was
a UTM zone 45N area, which runs 0.15 per cent high over the layer and 0.67 per cent high west of 82 E, where
the forest is: a longitude-correlated bias in the denominator of every per-hectare measure. The village
layer's own area_ha column is a UTM figure and is not used. The layer's total is not checked against any
official area of Odisha: the polygons never claimed to tile the state.

THE LAND OUTSIDE VILLAGES. 3,492 of the 52,531 DataMeet polygons carry no Census-2011 village code;
they are named after their sub-district and cover 27% of the layer. That is the land outside
any revenue village, much of it reserved forest. LGD panchayat polygons built by unioning villages
exclude it, so a "degraded forest per panchayat" measure silently drops a quarter of the state.
It is not empty: stage 3 finds a tenth of all geotagged MGNREGA works inside it. --outside sets the rule,
and whichever you pick must be stated on the slide:
    keep    (default, and the project's base layer) each block becomes its own unit with
            outside_village=1. These units have no census denominators, so they cannot enter a
            per-capita comparison; they show what the planning system reaches without a panchayat.
    nearest each block is merged into the LGD panchayat polygon nearest to it. Most blocks touch several
            panchayats at distance zero, and then the one with the lowest id is taken - an arbitrary
            choice, made only so that reruns agree.
    drop    excluded. Simplest, and it discards the works and the forest inside that land.

Writes <out>, <out stem>_attributes.csv and <out stem>.provenance.json (inputs with bytes and sha256, the
UTC run time, the arguments and the counts), all in the folder of --out.

Needs geopandas + pyogrio + pyproj.
"""
import argparse, datetime, hashlib, json, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj

WORK_CRS = "EPSG:32645"   # UTM 45N: used only to find the nearest panchayat and to dissolve in --outside nearest. No area is measured in it
AREA_BASIS = "ellipsoidal, WGS84 (geodesic polygon area, pyproj Geod)"


def ellipsoid_ha(geometries):
    """Area of each lon/lat polygon on the WGS84 ellipsoid, in hectares."""
    geod = pyproj.Geod(ellps="WGS84")
    return np.array([abs(geod.geometry_area_perimeter(g)[0]) for g in geometries]) / 1e4


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_villages(path):
    g = gpd.read_file(path)
    need = {"pc11_village_code", "geometry"}
    missing = need - set(g.columns)
    if missing:
        sys.exit(f"{path} is missing column(s) {sorted(missing)}")
    if g.crs is None:
        g = g.set_crs("EPSG:4326")
    g["_valid"] = g.geometry.is_valid
    if (~g["_valid"]).any():
        n = int((~g["_valid"]).sum())
        g.loc[~g["_valid"], "geometry"] = g.loc[~g["_valid"], "geometry"].buffer(0)
        print(f"  repaired {n} invalid geometries with buffer(0)")
    return g.drop(columns="_valid")


def attach_lgd_panchayat(vill, lgd_path):
    """Attach the LGD panchayat id to each village by Census-2011 village code."""
    lgd = pd.read_csv(lgd_path, dtype=str)
    cols = {c.lower().strip(): c for c in lgd.columns}
    vcol = next((cols[k] for k in ("village_2011_id", "village_code_2011", "pc11_village_code") if k in cols), None)
    pcol = next((cols[k] for k in ("panchayat_id", "lgd_panchayat_id", "panchayat") if k in cols), None)
    ncol = next((cols[k] for k in ("gram_panchayat_name", "panchayat_name") if k in cols), None)
    if not vcol or not pcol:
        sys.exit(f"could not find village-code and panchayat-id columns in {lgd_path}; saw {list(lgd.columns)[:12]}")
    print(f"  LGD map: village column {vcol!r}, panchayat column {pcol!r}, {len(lgd)} rows")
    lgd = lgd[[c for c in (vcol, pcol, ncol) if c]].dropna(subset=[vcol, pcol]).drop_duplicates(vcol)
    lgd[vcol] = lgd[vcol].str.strip().str.lstrip("0")
    out = vill.copy()
    out["_key"] = out["pc11_village_code"].astype("string").str.strip().str.lstrip("0")
    out = out.merge(lgd.rename(columns={vcol: "_key", pcol: "lgd_panchayat_id", **({ncol: "lgd_panchayat_name"} if ncol else {})}),
                    on="_key", how="left").drop(columns="_key")
    hit = out["lgd_panchayat_id"].notna()
    print(f"  villages matched to an LGD panchayat id: {int(hit.sum())} of {len(out)} ({hit.mean():.1%})")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--villages", required=True)
    ap.add_argument("--lgd-map")
    ap.add_argument("--unit", choices=["lgd_panchayat", "village"], default="lgd_panchayat")
    ap.add_argument("--outside", choices=["keep", "nearest", "drop"], default="keep")
    ap.add_argument("--out", default="units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    counts = {}

    print(f"reading {a.villages}")
    v = load_villages(a.villages)
    if v.crs.to_epsg() != 4326:
        sys.exit(f"{a.villages}: expected EPSG:4326, got {v.crs} - the ellipsoidal areas need lon/lat")
    v["area_ha"] = ellipsoid_ha(v.geometry.values)          # replaces the file's own UTM column, in memory only
    print(f"  {len(v)} polygons, {v['pc11_village_code'].notna().sum()} with a Census-2011 code; "
          f"{v['area_ha'].sum() / 100:,.2f} km2 ({AREA_BASIS})")

    inside = v[v["pc11_village_code"].notna()].copy()
    outside = v[v["pc11_village_code"].isna()].copy()
    counts.update(village_polygons=int(len(v)), village_polygons_km2=round(float(v["area_ha"].sum() / 100), 2),
                  polygons_with_census_2011_code=int(len(inside)),
                  outside_village_polygons=int(len(outside)), outside_village_km2=round(float(outside["area_ha"].sum() / 100), 2))

    if a.unit == "village":
        units = inside.rename(columns={"pc11_village_code": "unit_id", "pc11_village_name": "unit_name"})
        units["unit_level"] = "village"
        units = units[["unit_id", "unit_name", "unit_level", "pc11_district_code", "pc11_subdistrict_code", "geometry"]]
        repeats = int(units["unit_id"].duplicated().sum())
        counts["village_rows_repeating_an_earlier_unit_id"] = repeats
        if repeats:
            print(f"  NOTE {repeats} village polygons repeat an earlier unit_id (multi-part villages); do not aggregate on unit_id")
    else:
        if not a.lgd_map:
            sys.exit("--unit lgd_panchayat needs --lgd-map (LGD_village_panchayat_mapping.csv). Use --unit village to test without it.")
        inside = attach_lgd_panchayat(inside, a.lgd_map)
        unmapped = inside[inside["lgd_panchayat_id"].isna()]
        inside = inside[inside["lgd_panchayat_id"].notna()]
        agg = {"geometry": "union_all", "pc11_district_code": "first", "pc11_subdistrict_code": "first",
               "pc11_village_code": "count"}
        if "lgd_panchayat_name" in inside.columns:
            agg["lgd_panchayat_name"] = "first"
        units = inside.dissolve(by="lgd_panchayat_id", aggfunc={k: val for k, val in agg.items() if k != "geometry"}).reset_index()
        units = units.rename(columns={"lgd_panchayat_id": "unit_id", "pc11_village_code": "n_villages",
                                      **({"lgd_panchayat_name": "unit_name"} if "lgd_panchayat_name" in inside.columns else {})})
        units["unit_level"] = "lgd_panchayat"
        if len(unmapped):
            print(f"  NOTE {len(unmapped)} villages had no LGD panchayat id in the mapping and are excluded from the units "
                  f"({unmapped['area_ha'].sum()/100:,.0f} km2)")
        print(f"  built {len(units)} LGD panchayat polygons")
        counts.update(villages_with_no_lgd_panchayat=int(len(unmapped)),
                      villages_with_no_lgd_panchayat_km2=round(float(unmapped["area_ha"].sum() / 100), 2),
                      lgd_panchayat_polygons=int(len(units)))

    units["outside_village"] = 0
    if a.outside == "keep" and len(outside):
        o = outside.rename(columns={"name_2001": "unit_name"}).copy()
        o["unit_id"] = ["OUTSIDE_" + str(i) for i in range(1, len(o) + 1)]
        o["unit_level"] = "outside_village"
        o["outside_village"] = 1
        keep = ["unit_id", "unit_name", "unit_level", "pc11_district_code", "pc11_subdistrict_code", "outside_village", "geometry"]
        units = gpd.GeoDataFrame(pd.concat([units, o[[c for c in keep if c in o.columns]]], ignore_index=True),
                                 crs=units.crs)
        print(f"  kept {len(o)} outside-village polygons as their own units")
    elif a.outside == "nearest" and len(outside):
        if a.unit != "lgd_panchayat":
            sys.exit("--outside nearest only makes sense with --unit lgd_panchayat")
        tgt = units.to_crs(WORK_CRS)
        src = outside.to_crs(WORK_CRS).reset_index(drop=True)
        joined = gpd.sjoin_nearest(src[["geometry"]], tgt[["unit_id", "geometry"]], how="left", distance_col="_d")
        # a block that touches several panchayats is at distance 0 from each, and sjoin_nearest returns a row per tie:
        # count the ties first, then keep one, chosen by unit_id so that reruns agree
        touching = joined[joined["_d"] == 0].groupby(level=0)["unit_id"].nunique().reindex(src.index, fill_value=0)
        joined = joined.sort_values(["_d", "unit_id"]).groupby(level=0).first()
        src["unit_id"] = joined.reindex(src.index)["unit_id"].to_numpy()
        tied = (touching >= 2).to_numpy()
        block_km2 = outside["area_ha"].to_numpy() / 100                     # same order as src
        tied_km2 = float(block_km2[tied].sum())
        merged = pd.concat([units.to_crs(WORK_CRS)[["unit_id", "geometry"]], src[["unit_id", "geometry"]]])
        diss = merged.dissolve(by="unit_id").reset_index().to_crs(units.crs)
        units = units.drop(columns="geometry").merge(diss, on="unit_id", how="right")
        units = gpd.GeoDataFrame(units, geometry="geometry", crs=diss.crs)
        print(f"  merged {len(src)} outside-village polygons into the nearest LGD panchayat: {int(tied.sum())} of them "
              f"({tied.mean():.0%}, holding {tied_km2 / block_km2.sum():.0%} of that land) touch two or more "
              f"panchayats and were assigned arbitrarily; {int((touching == 1).sum())} touch exactly one, {int((touching == 0).sum())} touch none")
        counts.update(outside_blocks_touching_two_or_more_units=int(tied.sum()), outside_blocks_touching_exactly_one_unit=int((touching == 1).sum()),
                      outside_blocks_touching_no_unit=int((touching == 0).sum()), km2_in_blocks_touching_two_or_more_units=round(tied_km2, 2))
    elif a.outside == "drop":
        print(f"  dropped {len(outside)} outside-village polygons ({outside['area_ha'].sum()/100:,.0f} km2)")

    units["area_ha"] = ellipsoid_ha(units.geometry.values).round(4)
    units = units.sort_values("unit_id").reset_index(drop=True)
    out = Path(a.out)
    attributes = out.with_name(out.stem + "_attributes.csv")
    units.to_file(out, layer="units", driver="GPKG")
    units.drop(columns="geometry").to_csv(attributes, index=False)

    tot = units["area_ha"].sum() / 100
    out_ha = units.loc[units["outside_village"] == 1, "area_ha"].sum() / 100
    counts.update(units=int(len(units)), units_by_level={k: int(n) for k, n in units["unit_level"].value_counts().items()},
                  km2=round(float(tot), 2), km2_outside_any_revenue_village=round(float(out_ha), 2),
                  unit_id_is_unique=bool(units["unit_id"].is_unique))
    inputs = [a.villages] + ([a.lgd_map] if a.unit == "lgd_panchayat" else [])
    with open(out.with_name(out.stem + ".provenance.json"), "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/01_build_units.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "arguments": {"villages": a.villages, "lgd_map": a.lgd_map if a.unit == "lgd_panchayat" else None,
                                 "unit": a.unit, "outside": a.outside, "out": a.out},
                   "inputs": [{"path": p, "bytes": Path(p).stat().st_size, "sha256": sha256(p)} for p in inputs],
                   "outputs": [str(out), str(attributes)],
                   "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "geopandas": gpd.__version__},
                   "unit": "an LGD panchayat id (name x Census-2011 sub-district), not a gram panchayat" if a.unit == "lgd_panchayat" else "a village polygon",
                   "area_basis": AREA_BASIS,
                   "counts": counts}, fh, indent=2)

    print(f"\nwrote {a.out}: {len(units)} units, {tot:,.2f} km2 total ({AREA_BASIS})"
          + (f", of which {out_ha:,.2f} km2 ({out_ha/tot:.1%}) is outside any revenue village" if out_ha else ""))


if __name__ == "__main__":
    main()
