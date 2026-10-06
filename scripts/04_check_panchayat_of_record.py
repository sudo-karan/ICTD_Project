#!/usr/bin/env python3
"""
Stage 3 check: is the unit a work was geotagged inside the unit its own panchayat's works are in?

    python scripts/04_check_panchayat_of_record.py --units 10_units/units.gpkg

THIS SCRIPT READS PANCHAYAT NAMES AND JOINS NOTHING ON THEM. Stage 3 assigns works to units by
point-in-polygon only (04_build_allocation.py). This script asks what that assignment means. Every work
carries the Block and Panchayat that recorded it. Taking each such label in turn, it finds the unit that
holds most of the label's works - the label's modal unit - and reports the share of works that sit in
their label's modal unit. If polygons, mapping and geotags all agreed with the scheme's own records the
share would be near 1. The names pick out groups of works; they never decide where a work goes.

It runs the same test on CoRE Stack's own panchayat polygons (00_raw/04_boundaries), which carry the same
Panchayat_ID as the lgd_panchayat units, and measures how far the two sets of polygons overlap. That shows
whether a low share is this layer's fault or a property of the data.

The share cannot say which of the three is wrong - the polygon, the village -> panchayat mapping, or the
geotag - and an LGD panchayat id is not always a whole gram panchayat (docs/UNITS.md), which alone keeps
the share below 1.

In : 00_raw/02_mgnrega/assets_geojson/ODISHA/*.geojson, --units, 00_raw/04_boundaries/corestack_gp_odisha.json
Out: 40_allocation/panchayat_of_record_check.csv              one row per set of polygons tested
     40_allocation/panchayat_of_record_check.provenance.json  inputs, UTC run time, n, the overlap between the two layers

Needs geopandas, shapely, pandas, numpy.
"""
import argparse, datetime, hashlib, importlib.util, json, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_allocation", Path(__file__).with_name("04_build_allocation.py"))
alloc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alloc)                       # for load_units and point_in_polygon: the join under test, not a copy of it

CORESTACK = ROOT / "00_raw" / "04_boundaries" / "corestack_gp_odisha.json"
OUT = ROOT / "40_allocation"
MIN_WORKS = 30                                       # a label needs this many works before its own share is quoted
WORK_CRS = "EPSG:32645"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_labels():
    """lon, lat and the (district file, Block, Panchayat) label of every work."""
    lon, lat, label, files = [], [], [], sorted(alloc.ASSETS.glob("*.geojson"))
    for path in files:
        with open(path, encoding="utf-8") as fh:
            feats = json.load(fh)["features"]
        for f in feats:
            p = f.get("properties") or {}
            lon.append(p.get("lon")); lat.append(p.get("lat"))
            label.append(f"{path.stem}|{str(p.get('Block') or '').strip().upper()}|{str(p.get('Panchayat') or '').strip().upper()}")
        del feats
    return np.array(lon, float), np.array(lat, float), np.array(label), files


def modal_share(unit_of, label, keep):
    """Of the works inside a kept polygon: the share sitting in the polygon that holds most of their label."""
    t = pd.DataFrame({"unit": unit_of[keep], "label": label[keep]})
    by = t.groupby(["label", "unit"]).size()
    modal, total = by.groupby(level=0).max(), by.groupby(level=0).sum()
    big = total[total >= MIN_WORKS].index
    return {"n_works_inside": int(len(t)), "n_labels": int(len(total)), "share_in_modal_polygon": round(float(modal.sum() / total.sum()), 4),
            "n_labels_with_30_or_more_works": int(len(big)), "median_share_over_those_labels": round(float((modal[big] / total[big]).median()), 4)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 unit layer, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    units = alloc.load_units(a.units)
    cs = gpd.read_file(CORESTACK)
    if cs.crs is None or cs.crs.to_epsg() != 4326 or not cs["Panchayat_ID"].is_unique:
        sys.exit(f"{CORESTACK.name}: expected EPSG:4326 and a unique Panchayat_ID")
    cs["geometry"] = cs.geometry.make_valid()
    cs["unit_id"] = cs["Panchayat_ID"].astype(int).astype(str)
    cs = cs.sort_values("unit_id").reset_index(drop=True)

    lon, lat, label, files = read_labels()
    n = len(lon)
    unit_of, _ = alloc.point_in_polygon(units, lon, lat)
    cs_of, _ = alloc.point_in_polygon(cs, lon, lat)
    is_panchayat = (units["unit_level"] == "lgd_panchayat").to_numpy() if "unit_level" in units.columns else np.ones(len(units), bool)
    in_panchayat = (unit_of >= 0) & is_panchayat[np.clip(unit_of, 0, None)]
    rows = [{"polygons": Path(a.units).name, "scope": "all units", **modal_share(unit_of, label, unit_of >= 0)},
            {"polygons": Path(a.units).name, "scope": "lgd_panchayat units only", **modal_share(unit_of, label, in_panchayat)},
            {"polygons": CORESTACK.name, "scope": "CoRE Stack panchayat polygons", **modal_share(cs_of, label, cs_of >= 0)}]
    out = pd.DataFrame(rows)
    out.insert(2, "n_works", n)

    # the same Panchayat_ID drawn twice: how far do the two polygons overlap?
    mine = units[is_panchayat].set_index("unit_id").to_crs(WORK_CRS)
    theirs = cs.set_index("unit_id").to_crs(WORK_CRS)
    shared = mine.index.intersection(theirs.index)
    ga, gb = mine.loc[shared].geometry.values, theirs.loc[shared].geometry.values
    iou = shapely.area(shapely.intersection(ga, gb)) / shapely.area(shapely.union(ga, gb))
    apart = shapely.distance(shapely.centroid(ga), shapely.centroid(gb))
    overlap = {"panchayat_ids_in_both_layers": int(len(shared)), "of_lgd_panchayat_units": int(len(mine)), "of_corestack_polygons": int(len(theirs)),
               "intersection_over_union": {"median": round(float(np.median(iou)), 3), "share_below_0.1": round(float((iou < 0.1).mean()), 3),
                                           "share_above_0.8": round(float((iou > 0.8).mean()), 3)},
               "centroid_distance_m": {"median": round(float(np.median(apart))), "p90": round(float(np.quantile(apart, 0.9)))}}

    OUT.mkdir(exist_ok=True)
    out.to_csv(OUT / "panchayat_of_record_check.csv", index=False)
    with open(OUT / "panchayat_of_record_check.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/04_check_panchayat_of_record.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "inputs": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files + [CORESTACK]]
                             + [{"path": a.units, "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)}],
                   "label": "district file | Block | Panchayat, upper-cased, as recorded on each work. Used to group works, never to place them",
                   "n_works": n, "min_works_for_a_label_to_be_quoted": MIN_WORKS,
                   "tables": {"panchayat_of_record_check.csv": {"rows": int(len(out)), "blank_cells": int(out.isna().sum().sum())}},
                   "same_panchayat_id_in_both_layers": overlap}, fh, indent=2)

    print(f"panchayat_of_record_check.csv: n = {len(out)} sets of polygons, {n:,} works each; blank cells {int(out.isna().sum().sum())}")
    for _, r in out.iterrows():
        print(f"  {r['polygons']:<26} {r['scope']:<30} works inside {r['n_works_inside']:>9,} ({r['n_works_inside'] / n:.1%})  in their label's modal polygon "
              f"{r['share_in_modal_polygon']:.1%}  (median over {r['n_labels_with_30_or_more_works']:,} labels with {MIN_WORKS}+ works: {r['median_share_over_those_labels']:.1%}; labels {r['n_labels']:,})")
    o = overlap
    print(f"the same Panchayat_ID drawn in both layers: n = {o['panchayat_ids_in_both_layers']:,}; intersection over union median {o['intersection_over_union']['median']}, "
          f"below 0.1 in {o['intersection_over_union']['share_below_0.1']:.1%}, above 0.8 in {o['intersection_over_union']['share_above_0.8']:.1%}; "
          f"centroids {o['centroid_distance_m']['median']:,} m apart at the median")
    print(f"done. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
