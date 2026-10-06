#!/usr/bin/env python3
"""
Stage 1 - the three sources side by side: one row per analysis unit.

    python scripts/02_assemble_degradation.py --units 10_units/units.gpkg

In : --units                                the stage-0 layer: which units there are, and their type
     20_degradation/hansen_by_unit.csv      02_build_hansen.py
     20_degradation/nirv_by_unit.csv        02_build_nirv.py
     20_degradation/corestack_by_unit.csv   02_build_corestack.py
     and the provenance record beside each, which must name this layer
Out: 20_degradation/ and nowhere else
     degradation_by_unit.csv                unit_id, unit_level, outside_village, then the columns below
     degradation_by_unit.provenance.json    inputs with their hashes and run times, UTC run time, n and missingness

It computes nothing. It refuses to run unless all three sources exist, were each built for this layer, and each
hold exactly the layer's units once: a table with one source left blank would be read as if that source had
found nothing.

COLUMNS, and what each is (the full definitions are in the three scripts' docstrings and docs/DEGRADATION.md):
  forest_ha                       Hansen: land with treecover2000 > 30
  hansen_loss_ha, _2001 ... _2025 Hansen: tree-cover loss on that land, in all and by year
  nirv_slope                      NIRv: mean Theil-Sen slope, seasons 2013-2025, on land with treecover2000 > 10,
                                  from the DATE-STANDARDISED yearly value (every pass moved to 1 December)
  nirv_declining_ha               NIRv: land with treecover2000 > 10 whose trend is significantly downward
  nirv_increasing_ha              the same, upward - never read the declining area without it
  nirv_trend_ha                   the land the three NIRv columns rest on
  nirv_slope_unadjusted, nirv_declining_ha_unadjusted, nirv_increasing_ha_unadjusted
                                  the same from the first design's yearly value (the median of a season's scenes),
                                  which follows the dates of the clear scenes; carried so that the two can be compared
  corestack_degradation_ha        CoRE Stack class -1, on all land the product covers
  corestack_loss_ha               class -2
  corestack_improvement_ha        class 1 - never read class -1 without it
  corestack_gain_ha               class 2
  missing_data_share_hansen       Hansen: land with no data over the unit's area (0 everywhere: its no-data is sea)
  missing_data_share_nirv         NIRv: land with treecover2000 > 10 and no trend (fewer than ten seasons, or no rate), over that land
  missing_data_share_corestack    CoRE Stack: class 5 over all pixels with a class
The brief asks for one missing_data_share. There are three, because the three sources miss different things on
different land; a single column would have to pick one or average unlike quantities.

THE THREE DO NOT REST ON THE SAME LAND. forest_ha and hansen_loss_ha are on treecover2000 > 30; the NIRv columns on
treecover2000 > 10; the CoRE Stack columns on the producers' own tree mask, which covers about seven tenths of
the state. Do not difference or ratio columns of different sources. 02_build_agreement.py sets the three beside
one another on one reference.

Needs geopandas, pandas.
"""
import argparse, datetime, hashlib, json, sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
SOURCES = {"hansen": ("hansen_by_unit.csv", "hansen.provenance.json"), "nirv": ("nirv_by_unit.csv", "nirv.provenance.json"),
           "corestack": ("corestack_by_unit.csv", "corestack.provenance.json")}
YEARS = range(2001, 2026)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    layer_sha = sha256(a.units)
    units = pd.DataFrame(gpd.read_file(a.units, layer="units", ignore_geometry=True))[["unit_id", "unit_level", "outside_village"]]
    units["unit_id"] = units["unit_id"].astype(str)
    units = units.sort_values("unit_id").reset_index(drop=True)
    fails, tables, inputs = [], {}, [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": layer_sha}]
    for name, (table, record) in SOURCES.items():
        tp, rp = OUT / table, OUT / record
        if not tp.exists() or not rp.exists():
            fails.append(f"{name}: {table} or {record} is missing - that source has not been built")
            continue
        prov = json.load(open(rp))
        built_for = [i.get("sha256") for i in prov.get("inputs", []) if i.get("path") == str(a.units)]
        if layer_sha not in built_for:
            fails.append(f"{name}: {record} does not name this layer ({a.units}, sha256 {layer_sha[:12]}...): it was built for another")
        t = pd.read_csv(tp, dtype={"unit_id": str})
        if len(t) != len(units) or not t["unit_id"].is_unique or set(t["unit_id"]) != set(units["unit_id"]):
            fails.append(f"{name}: {table} holds {len(t):,} rows and {t['unit_id'].nunique():,} distinct unit_id; the layer has {len(units):,} units")
        tables[name] = t.set_index("unit_id")
        inputs.append({"path": str(tp.relative_to(ROOT)), "bytes": tp.stat().st_size, "sha256": sha256(tp), "built_by": prov.get("script"), "run_utc": prov.get("run_utc")})
    if fails:
        print("NOT ASSEMBLED:", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    h, n, c = (tables[k].loc[units["unit_id"]] for k in ("hansen", "nirv", "corestack"))
    out = units.copy()
    for col in ["forest_ha", "hansen_loss_ha"] + [f"hansen_loss_ha_{y}" for y in YEARS]:
        out[col] = h[col].to_numpy()
    for col in ("nirv_slope", "nirv_declining_ha", "nirv_increasing_ha", "nirv_trend_ha", "nirv_slope_unadjusted", "nirv_declining_ha_unadjusted", "nirv_increasing_ha_unadjusted"):
        out[col] = n[col].to_numpy()
    for col in ("corestack_degradation_ha", "corestack_loss_ha", "corestack_improvement_ha", "corestack_gain_ha"):
        out[col] = c[col].to_numpy()
    out["missing_data_share_hansen"] = h["missing_data_share"].to_numpy()
    out["missing_data_share_nirv"] = n["missing_data_share"].to_numpy()
    out["missing_data_share_corestack"] = c["corestack_missing_share"].to_numpy()
    out.to_csv(OUT / "degradation_by_unit.csv", index=False)
    blank = {col: int(out[col].isna().sum()) for col in out.columns if out[col].isna().any()}
    by_level = {k: int(v) for k, v in out["unit_level"].value_counts().items()}
    with open(OUT / "degradation_by_unit.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/02_assemble_degradation.py", "script_sha256": sha256(__file__), "run_utc": started, "inputs": inputs,
                   "table": {"path": "20_degradation/degradation_by_unit.csv", "rows": int(len(out)), "columns": int(len(out.columns)), "units_by_level": by_level, "blank_cells": blank},
                   "note": "copied column for column from the three sources' tables; nothing is computed here. A blank NIRv or CoRE Stack cell means the unit has no land of the kind "
                           "that column rests on (no treecover2000 > 10 land; no pixel with a CoRE Stack class), not that the source failed."}, fh, indent=2)
    print(f"degradation_by_unit.csv: n = {len(out):,} units {by_level}; {len(out.columns)} columns; blank cells {blank or 'none'}; run_utc {started}")


if __name__ == "__main__":
    main()
