#!/usr/bin/env python3
"""
Stage 1 - the measures of forest condition side by side: one row per analysis unit.

    python scripts/02_assemble_degradation.py --units 10_units/units.gpkg

In : --units                                                 the stage-0 layer: which units there are, and their type
     20_degradation/hansen_by_unit.csv                       02_build_hansen.py (the mask treecover2000 > 30)
     20_degradation/hansen_loss_by_canopy_band_by_unit.csv   02_build_hansen.py: loss by band of year-2000 canopy
     20_degradation/corestack_by_unit.csv                    02_build_corestack.py
     20_degradation/hansen_by_unit_level.csv, hansen_loss_by_canopy_band.csv, corestack_by_unit_level.csv
                                                             the two sources' own summary tables: what this table must add up to
     20_degradation/nirv_by_unit.csv                         02_build_nirv.py - IF IT EXISTS (see NIRv below)
     and the provenance record beside each source, which must name this layer
Out: 20_degradation/ and nowhere else
     degradation_by_unit.csv                unit_id, unit_level, outside_village, then the columns below
     degradation_by_unit.provenance.json    inputs with their hashes and run times, UTC run time, checks, n and missingness

It computes nothing: every cell is copied from a source table. It refuses to run unless Hansen and CoRE Stack
exist, were each built for this layer, each hold exactly the layer's units once, and add up to their sources' own
summary tables.

STAGE 1 RESTS ON TWO MEASURES (ruling of 7 Oct 2026). Hansen is the validated floor: stand-replacing loss of canopy
that was fairly closed in 2000. CoRE Stack is the measure of what Hansen cannot see - thinning under a standing
canopy, and change on land that was open in 2000. NIRv is a REPORTED COLUMN, not a degradation measure: its trend
moves one for one with the phenology rate fitted to correct it (docs/DEGRADATION.md, the NIRv section).

NIRv. The NIRv columns are always present. Until 02_build_nirv.py has run for this layer they are blank in every
row and nirv_status says "pending"; once nirv_by_unit.csv and its record exist for this layer this script fills
them and nirv_status says "built". A blank NIRv cell under "pending" means not computed yet - it does not mean the
unit has no trend.

COLUMNS, and what each is (full definitions: the source scripts' docstrings and docs/DEGRADATION.md):
  forest_ha                       Hansen: land with treecover2000 > 30
  hansen_loss_ha, _2001 ... _2025 Hansen: tree-cover loss on that land, in all and by year
  land_ha_tc_le10, land_ha_tc_gt10le30, land_ha_tc_gt30
                                  the unit's land by band of year-2000 canopy: treecover2000 <= 10; 10 < treecover2000
                                  <= 30; treecover2000 > 30 (the last is forest_ha again, from the canopy-band table)
  hansen_loss_ha_tc_le10, hansen_loss_ha_tc_gt10le30, hansen_loss_ha_tc_gt30
                                  Hansen loss 2001-2025 in each band. Only the last is inside the mask
  land_ha_tc_eq0, hansen_loss_ha_tc_eq0
                                  the part of the le10 band with no canopy at all in 2000 (not a fourth band): most
                                  loss outside the mask is here, and it is not forest that stood in 2000
  corestack_degradation_ha        CoRE Stack class -1 (density or height fell a class), on all land the product covers
  corestack_partial_degradation_ha  classes 3 and 4 (one of density and height rose, the other fell) - kept apart
                                  from class -1; add it if you read a mixed change as degradation
  corestack_loss_ha               class -2 (tree cover in the first period, none in the second)
  corestack_improvement_ha        class 1 - never read class -1 without it
  corestack_gain_ha               class 2
  corestack_tree_cover_start_ha   the product's tree cover in the first period: what the classes are a share of
  land_tc_gt10_ha, corestack_*_tc_gt10
                                  the same classes on land with treecover2000 > 10 only: the land this product shares
                                  with Hansen, and the reference of 02_build_agreement.py
  nirv_status                     "pending" or "built"
  nirv_slope, nirv_declining_ha, nirv_increasing_ha, nirv_trend_ha
                                  NIRv, date-standardised yearly value, land with treecover2000 > 10 (see NIRv above)
  nirv_slope_unadjusted, nirv_declining_ha_unadjusted, nirv_increasing_ha_unadjusted
                                  the same from the first design's yearly value, which follows the dates of the scenes
  missing_data_share_hansen       Hansen: land with no data over the unit's area (0 everywhere: its no-data is sea)
  missing_data_share_corestack    CoRE Stack: class 5 over all pixels with a class
  missing_data_share_nirv         NIRv: land with treecover2000 > 10 and no trend, over that land (blank while pending)
The brief asks for one missing_data_share. There is one per source, because the sources miss different things on
different land; a single column would have to pick one or average unlike quantities.

THE SOURCES DO NOT REST ON THE SAME LAND. forest_ha and hansen_loss_ha are on treecover2000 > 30; the plain CoRE
Stack columns on the producers' own tree mask, which covers about seven tenths of the state; the _tc_gt10 columns
and the NIRv columns on treecover2000 > 10. Do not difference or ratio columns that rest on different land.
02_build_agreement.py sets Hansen and CoRE Stack beside one another on one reference.

Needs geopandas, pandas, numpy.
"""
import argparse, datetime, hashlib, json, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
REQUIRED = {"hansen": ("hansen_by_unit.csv", "hansen.provenance.json"), "canopy_bands": ("hansen_loss_by_canopy_band_by_unit.csv", "hansen.provenance.json"),
            "corestack": ("corestack_by_unit.csv", "corestack.provenance.json")}
NIRV = ("nirv_by_unit.csv", "nirv.provenance.json")
YEARS = range(2001, 2026)
BANDS = ("le10", "gt10le30", "gt30", "eq0")                  # eq0 is part of le10
CORE = ("degradation", "partial_degradation", "loss", "improvement", "gain")
NIRV_COLUMNS = ("nirv_slope", "nirv_declining_ha", "nirv_increasing_ha", "nirv_trend_ha", "nirv_slope_unadjusted", "nirv_declining_ha_unadjusted", "nirv_increasing_ha_unadjusted")
LEVELS = {"all units": None, "lgd_panchayat": "lgd_panchayat", "outside_village": "outside_village"}
HA_TOLERANCE = 0.003                                         # per unit: a sum of 25 yearly figures each rounded to 0.0001 ha


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

    def load(name, table, record, required):
        """A source's per-unit table, indexed by unit_id, if it exists for this layer; None (with a reason) otherwise."""
        tp, rp = OUT / table, OUT / record
        if not tp.exists() or not rp.exists():
            return None, f"{table} or {record} is missing - that source has not been built"
        prov = json.load(open(rp))
        built_for = [i.get("sha256") for i in prov.get("inputs", []) if i.get("path") == str(a.units)]
        if layer_sha not in built_for:
            return None, f"{record} does not name this layer ({a.units}, sha256 {layer_sha[:12]}...): it was built for another"
        t = pd.read_csv(tp, dtype={"unit_id": str})
        if len(t) != len(units) or not t["unit_id"].is_unique or set(t["unit_id"]) != set(units["unit_id"]):
            return None, f"{table} holds {len(t):,} rows and {t['unit_id'].nunique():,} distinct unit_id; the layer has {len(units):,} units"
        inputs.append({"path": str(tp.relative_to(ROOT)), "bytes": tp.stat().st_size, "sha256": sha256(tp), "built_by": prov.get("script"), "run_utc": prov.get("run_utc"), "required": required})
        return t.set_index("unit_id").loc[units["unit_id"]], None

    for name, (table, record) in REQUIRED.items():
        tables[name], why = load(name, table, record, True)
        if why:
            fails.append(f"{name}: {why}")
    if fails:
        print("NOT ASSEMBLED:", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    nirv, nirv_why = load("nirv", *NIRV, False)
    h, b, c = tables["hansen"], tables["canopy_bands"], tables["corestack"]

    out = units.copy()
    for col in ["forest_ha", "hansen_loss_ha"] + [f"hansen_loss_ha_{y}" for y in YEARS]:
        out[col] = h[col].to_numpy()
    for band in BANDS:
        out[f"land_ha_tc_{band}"] = b[f"area_ha_{band}"].to_numpy()
    for band in BANDS:
        out[f"hansen_loss_ha_tc_{band}"] = b[f"loss_ha_{band}"].to_numpy()
    for k in CORE:
        out[f"corestack_{k}_ha"] = c[f"corestack_{k}_ha"].to_numpy()
    out["corestack_tree_cover_start_ha"] = c["corestack_tree_cover_start_ha"].to_numpy()
    out["land_tc_gt10_ha"] = c["land_tc_gt10_ha"].to_numpy()
    for k in CORE + ("tree_cover_start",):
        out[f"corestack_{k}_ha_tc_gt10"] = c[f"corestack_{k}_ha_tc_gt10"].to_numpy()
    out["nirv_status"] = "built" if nirv is not None else "pending"
    for col in NIRV_COLUMNS:
        out[col] = nirv[col].to_numpy() if nirv is not None else np.nan
    out["missing_data_share_hansen"] = h["missing_data_share"].to_numpy()
    out["missing_data_share_corestack"] = c["corestack_missing_share"].to_numpy()
    out["missing_data_share_nirv"] = nirv["missing_data_share"].to_numpy() if nirv is not None else np.nan

    # ---- checks: within a unit, and against the two sources' own summary tables -------------------------------------
    checks = {}
    yearly = out[[f"hansen_loss_ha_{y}" for y in YEARS]].sum(axis=1)
    gap = float((yearly - out["hansen_loss_ha"]).abs().max())
    checks["yearly_loss_adds_up_to_hansen_loss_ha_largest_gap_ha"] = round(gap, 5)
    if gap > HA_TOLERANCE:
        fails.append(f"the 25 yearly loss columns do not add up to hansen_loss_ha: largest gap {gap:.4f} ha")
    for mine, theirs, what in (("land_ha_tc_gt30", "forest_ha", "the canopy-band table's land with treecover2000 > 30 against forest_ha"),
                               ("hansen_loss_ha_tc_gt30", "hansen_loss_ha", "the canopy-band table's loss on treecover2000 > 30 against hansen_loss_ha")):
        gap = float((out[mine] - out[theirs]).abs().max())
        checks[f"{mine}_equals_{theirs}_largest_gap_ha"] = round(gap, 5)
        if gap > HA_TOLERANCE:
            fails.append(f"{what}: largest gap for a unit {gap:.4f} ha")
    gap = float((out["land_ha_tc_eq0"] - out["land_ha_tc_le10"]).max())
    if gap > HA_TOLERANCE or (out["hansen_loss_ha_tc_eq0"] - out["hansen_loss_ha_tc_le10"]).max() > HA_TOLERANCE:
        fails.append("land or loss with treecover2000 = 0 exceeds the treecover2000 <= 10 band it is part of")
    if (out["hansen_loss_ha"] > out["forest_ha"] + HA_TOLERANCE).any() or (out.select_dtypes("number").drop(columns=[c_ for c_ in out.columns if c_.startswith("nirv_slope")], errors="ignore") < -1e-9).any().any():
        fails.append("a unit has more loss than forest, or a negative area")
    for k in CORE:
        if (out[f"corestack_{k}_ha_tc_gt10"] > out[f"corestack_{k}_ha"] + HA_TOLERANCE).any():
            fails.append(f"corestack_{k}_ha_tc_gt10 exceeds corestack_{k}_ha in some unit")

    def level_sum(col, level):
        sel = out["unit_level"] == level if level else np.ones(len(out), bool)
        return float(out.loc[sel, col].sum()) / 100.0                      # km2

    printed, worst = [], 0.0
    hl = pd.read_csv(OUT / "hansen_by_unit_level.csv").set_index("unit_level")
    cb = pd.read_csv(OUT / "hansen_loss_by_canopy_band.csv").set_index(["units", "canopy_band"])
    cl = pd.read_csv(OUT / "corestack_by_unit_level.csv").set_index(["units", "land"])
    for label, level in LEVELS.items():
        n_here = int((out["unit_level"] == level).sum()) if level else len(out)
        if n_here != int(hl.loc[label, "n_units"]):
            fails.append(f"{label}: {n_here:,} units here, {int(hl.loc[label, 'n_units']):,} in hansen_by_unit_level.csv")
        rows = [("forest_ha", hl.loc[label, "forest_km2"], 0.06, "hansen_by_unit_level.csv forest_km2"),
                ("hansen_loss_ha", hl.loc[label, "loss_km2_2001_2025"], 0.006, "hansen_by_unit_level.csv loss_km2_2001_2025")]
        for band in BANDS:
            rows.append((f"land_ha_tc_{band}", cb.loc[(label, band), "land_km2"], 0.006, f"hansen_loss_by_canopy_band.csv land_km2, {band}"))
            rows.append((f"hansen_loss_ha_tc_{band}", cb.loc[(label, band), "loss_km2_2001_2025"], 0.006, f"hansen_loss_by_canopy_band.csv loss_km2_2001_2025, {band}"))
        for k, theirs in (("degradation", "degradation_km2"), ("partial_degradation", "partial_degradation_km2"), ("loss", "loss_km2"), ("improvement", "improvement_km2"), ("gain", "gain_km2"),
                          ("tree_cover_start", "tree_cover_start_km2")):
            rows.append((f"corestack_{k}_ha", cl.loc[(label, "all land"), theirs], 0.006, f"corestack_by_unit_level.csv {theirs}, all land"))
            rows.append((f"corestack_{k}_ha_tc_gt10", cl.loc[(label, "treecover2000 > 10"), theirs], 0.006, f"corestack_by_unit_level.csv {theirs}, treecover2000 > 10"))
        for col, theirs, tol, where in rows:
            mine = level_sum(col, level)
            worst = max(worst, abs(mine - float(theirs)))
            printed.append({"units": label, "column": col, "sum_km2": round(mine, 3), "source_table_km2": float(theirs), "source": where})
            if abs(mine - float(theirs)) > tol:
                fails.append(f"{label}: {col} sums to {mine:,.3f} km2; {where} prints {float(theirs):,.2f}")
    checks["sums_against_the_sources_own_summary_tables"] = {"figures_compared": len(printed), "largest_gap_km2": round(worst, 4)}
    if nirv is None:
        if not (out[list(NIRV_COLUMNS) + ["missing_data_share_nirv"]].isna().all().all() and (out["nirv_status"] == "pending").all()):
            fails.append("NIRv is pending but an NIRv cell is not blank")
    if fails:
        print("NOT ASSEMBLED:", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)

    out.to_csv(OUT / "degradation_by_unit.csv", index=False)
    blank = {col: int(out[col].isna().sum()) for col in out.columns if out[col].isna().any()}
    by_level = {k: int(v) for k, v in out["unit_level"].value_counts().items()}
    with open(OUT / "degradation_by_unit.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/02_assemble_degradation.py", "script_sha256": sha256(__file__), "run_utc": started, "inputs": inputs
                   + [{"path": f"20_degradation/{n}", "sha256": sha256(OUT / n), "role": "the source's own summary table, checked against"} for n in ("hansen_by_unit_level.csv", "hansen_loss_by_canopy_band.csv", "corestack_by_unit_level.csv")],
                   "table": {"path": "20_degradation/degradation_by_unit.csv", "rows": int(len(out)), "columns": int(len(out.columns)), "units_by_level": by_level, "blank_cells": blank},
                   "measures": {"hansen": "built", "corestack": "built", "nirv": "built" if nirv is not None else f"pending ({nirv_why}); every NIRv cell is blank and nirv_status is 'pending' in every row"},
                   "checks_passed": checks, "sums_km2": printed,
                   "note": "copied column for column from the sources' tables; nothing is computed here. NIRv is a reported column, not a degradation measure (ruling of 7 Oct 2026). "
                           "A blank CoRE Stack share means the unit has no pixel with a CoRE Stack class; a blank NIRv cell under nirv_status 'pending' means not computed yet."}, fh, indent=2)
    print(f"degradation_by_unit.csv: n = {len(out):,} units {by_level}; {len(out.columns)} columns; run_utc {started}")
    print(f"  NIRv: {'built' if nirv is not None else 'PENDING - ' + nirv_why}")
    print(f"  blank cells: {blank or 'none'}")
    print(f"  checks: {len(printed)} sums equal the sources' own summary tables (largest gap {worst:.4f} km2); yearly loss adds up; the canopy-band table's > 30 band equals forest_ha and hansen_loss_ha unit by unit")
    show = pd.DataFrame(printed)
    print(show[show.column.isin(["forest_ha", "hansen_loss_ha", "hansen_loss_ha_tc_gt10le30", "hansen_loss_ha_tc_le10", "corestack_degradation_ha", "corestack_partial_degradation_ha", "corestack_improvement_ha", "corestack_degradation_ha_tc_gt10"])]
          .pivot(index="column", columns="units", values="sum_km2").to_string())


if __name__ == "__main__":
    main()
