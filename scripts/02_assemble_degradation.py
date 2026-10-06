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
unit has no trend. "Pending" is only for a source that has not been built. A NIRv table that IS on disk with its
record but was built for another layer, or does not hold exactly the layer's units, is an error: nothing is
written and the script ends with exit 1. --require-nirv (the chain passes it) makes "pending" an error too, so
that a run that was meant to fill the columns cannot end quietly without them. When NIRv is filled it is held to
its own summary table (nirv_by_unit_level.csv) and to the blank-cell counts in its record, as the other two are.

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
                                  with Hansen, and the reference of 02_build_agreement.py. land_tc_gt10_ha is that
                                  land ON THE CoRE STACK GRID (25 m, treecover2000 taken nearest-neighbour) and is the
                                  only valid denominator for the corestack_*_tc_gt10 columns. It is not
                                  land_ha_tc_gt10le30 + land_ha_tc_gt30, the same land on Hansen's 30 m grid: the two
                                  differ unit by unit (by 1.39 km2 over all units, up to 28 ha in one)
  nirv_status                     "pending" or "built"
  nirv_slope, nirv_declining_ha, nirv_increasing_ha, nirv_trend_ha
                                  NIRv, date-standardised yearly value, land with treecover2000 > 10 (see NIRv above)
  nirv_slope_unadjusted, nirv_declining_ha_unadjusted, nirv_increasing_ha_unadjusted, nirv_trend_ha_unadjusted
                                  the same four from the first design's yearly value, which follows the dates of the
                                  scenes. Each pair of areas has its own land with a trend: take a share of an
                                  _unadjusted area over nirv_trend_ha_unadjusted, not over nirv_trend_ha
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
import argparse, datetime, hashlib, json, os, sys
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
NIRV_COLUMNS = ("nirv_slope", "nirv_declining_ha", "nirv_increasing_ha", "nirv_trend_ha",
                "nirv_slope_unadjusted", "nirv_declining_ha_unadjusted", "nirv_increasing_ha_unadjusted", "nirv_trend_ha_unadjusted")
NIRV_LEVEL = "nirv_by_unit_level.csv"                       # NIRv's own summary table; its rows for land "gt10" are what the per-unit columns rest on
NIRV_SERIES = (("date-standardised", ""), ("first design", "_unadjusted"))
CORE_BANDS = {"degradation": ("degradation",), "partial_degradation": ("partial3", "partial4"), "loss": ("lost",), "improvement": ("improvement",), "gain": ("gained",)}
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
    ap.add_argument("--require-nirv", action="store_true", help="end with exit 1, writing nothing, unless the NIRv columns can be filled")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    layer_sha = sha256(a.units)
    units = pd.DataFrame(gpd.read_file(a.units, layer="units", ignore_geometry=True))[["unit_id", "unit_level", "outside_village"]]
    units["unit_id"] = units["unit_id"].astype(str)
    units = units.sort_values("unit_id").reset_index(drop=True)
    fails, tables, inputs = [], {}, [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": layer_sha}]

    def entry(path, **more):
        return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path), **more}

    def load(name, table, record, required):
        """A source's per-unit table, indexed by unit_id, if it exists for this layer: (table, None, its record, 'ok').
        Otherwise (None, why, None, 'absent') if it has not been built, or (..., 'rejected') if it is there and cannot be used."""
        tp, rp = OUT / table, OUT / record
        if not tp.exists() and not rp.exists():
            return None, f"{table} and {record} do not exist - that source has not been built", None, "absent"
        if not tp.exists() or not rp.exists():
            return None, f"only {table if tp.exists() else record} exists, without {record if tp.exists() else table} - that source is half written or its build was cut off", None, "absent"
        prov = json.load(open(rp))
        built_for = [i.get("sha256") for i in prov.get("inputs", []) if i.get("path") == str(a.units)]
        if layer_sha not in built_for:
            return None, f"{record} does not name this layer ({a.units}, sha256 {layer_sha[:12]}...): it was built for another", None, "rejected"
        t = pd.read_csv(tp, dtype={"unit_id": str})
        if len(t) != len(units) or not t["unit_id"].is_unique or set(t["unit_id"]) != set(units["unit_id"]):
            return None, f"{table} holds {len(t):,} rows and {t['unit_id'].nunique():,} distinct unit_id; the layer has {len(units):,} units", None, "rejected"
        inputs.append(entry(tp, built_by=prov.get("script"), run_utc=prov.get("run_utc"), required=required))
        if not any(i["path"] == str(rp.relative_to(ROOT)) for i in inputs):
            inputs.append(entry(rp, role="the source's record: says which layer the table was built for"))
        return t.set_index("unit_id").loc[units["unit_id"]], None, prov, "ok"

    for name, (table, record) in REQUIRED.items():
        tables[name], why, _, _ = load(name, table, record, True)
        if why:
            fails.append(f"{name}: {why}")
    if fails:
        print("NOT ASSEMBLED:", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    nirv, nirv_why, nirv_prov, nirv_state = load("nirv", *NIRV, False)
    if nirv_state == "rejected":
        fails.append(f"NIRv: a table is on disk and cannot be used - {nirv_why}. 'Pending' is only for a source that has not been built: rebuild it or remove it")
    elif nirv is None and a.require_nirv:
        fails.append(f"NIRv was required (--require-nirv) and is not built: {nirv_why}")
    if fails:
        print("NOT ASSEMBLED:", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
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

    for col in ("missing_data_share_hansen", "missing_data_share_corestack") + (("missing_data_share_nirv",) if nirv is not None else ()):
        v = out[col].dropna()
        if ((v < -1e-9) | (v > 1 + 1e-9)).any():
            fails.append(f"{col} is outside 0 to 1 in {int(((v < -1e-9) | (v > 1 + 1e-9)).sum()):,} units")
    # each unit against a SECOND per-unit table of the same source: sums by unit type cannot see a row given to the wrong unit
    th = pd.read_csv(OUT / "hansen_by_unit_thresholds.csv", dtype={"unit_id": str}).set_index("unit_id").reindex(units["unit_id"])
    cbu = pd.read_csv(OUT / "corestack_by_unit_bands.csv", dtype={"unit_id": str}).set_index("unit_id").reindex(units["unit_id"])
    second = [("forest_ha", th["forest_ha_gt30"], "hansen_by_unit_thresholds.csv forest_ha_gt30"), ("hansen_loss_ha", th["hansen_loss_ha_gt30"], "hansen_by_unit_thresholds.csv hansen_loss_ha_gt30")]
    for k, classes in CORE_BANDS.items():
        every = sum(cbu[f"class_{c_}_ha_{b_}"] for c_ in classes for b_ in ("eq0", "gt0le10", "gt10le30", "gt30"))
        tree = sum(cbu[f"class_{c_}_ha_{b_}"] for c_ in classes for b_ in ("gt10le30", "gt30"))
        second += [(f"corestack_{k}_ha", every, f"corestack_by_unit_bands.csv, class {k} over the four bands"), (f"corestack_{k}_ha_tc_gt10", tree, f"corestack_by_unit_bands.csv, class {k} on treecover2000 > 10")]
    second.append(("land_tc_gt10_ha", cbu["land_ha_gt10le30"] + cbu["land_ha_gt30"], "corestack_by_unit_bands.csv land on treecover2000 > 10"))
    worst_unit = 0.0
    for col, theirs, where in second:
        if theirs.isna().any():
            fails.append(f"{where}: {int(theirs.isna().sum()):,} of the layer's units are not in that table")
            continue
        gap = float(np.abs(out[col].to_numpy() - theirs.to_numpy()).max())
        worst_unit = max(worst_unit, gap)
        if gap > 2 * HA_TOLERANCE:
            fails.append(f"{col} differs from {where} by up to {gap:.4f} ha in a unit")
    checks["each_unit_against_a_second_per_unit_table_of_its_source"] = {"columns_compared": len(second), "largest_gap_ha": round(worst_unit, 5)}

    def level_sum(col, level):
        sel = out["unit_level"] == level if level else np.ones(len(out), bool)
        return float(out.loc[sel, col].sum()) / 100.0                      # km2

    printed, worst = [], 0.0
    hl = pd.read_csv(OUT / "hansen_by_unit_level.csv").set_index("unit_level")
    cb = pd.read_csv(OUT / "hansen_loss_by_canopy_band.csv").set_index(["units", "canopy_band"])
    cl = pd.read_csv(OUT / "corestack_by_unit_level.csv").set_index(["units", "land"])
    nl = None
    if nirv is not None:
        if not (OUT / NIRV_LEVEL).exists():
            fails.append(f"{NIRV_LEVEL} does not exist: the NIRv columns cannot be held to their source's own summary")
        else:
            nl = pd.read_csv(OUT / NIRV_LEVEL)
            nl = nl[nl["land"] == "gt10"].set_index(["yearly_value", "units"])
        cells = out[list(NIRV_COLUMNS) + ["missing_data_share_nirv"]]
        if cells.isna().all().all():
            fails.append("every NIRv cell is blank although nirv_by_unit.csv exists")
        for series, sfx in NIRV_SERIES:
            d, i_, tr = (out[f"nirv_{k}_ha{sfx}"].fillna(0) for k in ("declining", "increasing", "trend"))
            if ((d + i_) > tr + HA_TOLERANCE).any():
                fails.append(f"NIRv, {series}: declining plus increasing area exceeds the land with a trend in {int(((d + i_) > tr + HA_TOLERANCE).sum()):,} units")
        rec = (nirv_prov.get("tables") or {}).get(NIRV[0])
        if rec is None:
            fails.append(f"{NIRV[1]} has no 'tables' entry for {NIRV[0]}: the table cannot be held to its record")
        else:
            if int(rec.get("rows", -1)) != len(nirv):
                fails.append(f"{NIRV[0]} holds {len(nirv):,} rows; its record says {rec.get('rows')}")
            for col in list(NIRV_COLUMNS) + ["missing_data_share"]:
                want, have = int((rec.get("blank_cells") or {}).get(col, 0)), int(nirv[col].isna().sum())
                if want != have:
                    fails.append(f"{NIRV[0]} {col}: {have:,} blank cells; its record says {want:,} - the table is not the one the record describes")
            checks["nirv_table_has_the_rows_and_blank_cells_its_record_states"] = True
    for label, level in LEVELS.items():
        n_here = int((out["unit_level"] == level).sum()) if level else len(out)
        if n_here != int(hl.loc[label, "n_units"]):
            fails.append(f"{label}: {n_here:,} units here, {int(hl.loc[label, 'n_units']):,} in hansen_by_unit_level.csv")
        rows = [("forest_ha", hl.loc[label, "forest_km2"], 0.06, "hansen_by_unit_level.csv forest_km2"),
                ("hansen_loss_ha", hl.loc[label, "loss_km2_2001_2025"], 0.006, "hansen_by_unit_level.csv loss_km2_2001_2025"),
                ("land_tc_gt10_ha", cl.loc[(label, "treecover2000 > 10"), "land_km2"], 0.006, "corestack_by_unit_level.csv land_km2, treecover2000 > 10")]
        for first, last in ((2001, 2010), (2011, 2017), (2018, 2025)):          # the yearly columns, by the periods the source's table prints
            sel = out["unit_level"] == level if level else np.ones(len(out), bool)
            mine = float(out.loc[sel, [f"hansen_loss_ha_{y}" for y in range(first, last + 1)]].sum().sum()) / 100.0
            theirs = float(hl.loc[label, f"loss_km2_{first}_{last}"])
            worst = max(worst, abs(mine - theirs))
            printed.append({"units": label, "column": f"hansen_loss_ha_{first} ... _{last}", "sum_km2": round(mine, 3), "source_table_km2": theirs, "source": f"hansen_by_unit_level.csv loss_km2_{first}_{last}"})
            if abs(mine - theirs) > 0.006:
                fails.append(f"{label}: loss {first}-{last} sums to {mine:,.3f} km2; hansen_by_unit_level.csv prints {theirs:,.2f}")
        n_missing = int((out.loc[out["unit_level"] == level if level else np.ones(len(out), bool), "missing_data_share_hansen"] > 0).sum())
        if n_missing != int(hl.loc[label, "units_with_missing_data"]):
            fails.append(f"{label}: {n_missing:,} units with missing Hansen data here, {int(hl.loc[label, 'units_with_missing_data']):,} in hansen_by_unit_level.csv")
        if nirv is not None and nl is not None:
            for series, sfx in NIRV_SERIES:
                for col, theirs in ((f"nirv_declining_ha{sfx}", "declining_km2"), (f"nirv_increasing_ha{sfx}", "increasing_km2"), (f"nirv_trend_ha{sfx}", "with_a_trend_km2")):
                    if (series, label) not in nl.index:
                        fails.append(f"{NIRV_LEVEL} has no row for {series}, {label}, land gt10")
                    else:
                        rows.append((col, nl.loc[(series, label), theirs], 0.006, f"{NIRV_LEVEL} {theirs}, {series}, treecover2000 > 10"))
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
    tmp = OUT / "degradation_by_unit.csv.part"                 # written, read back as text, and only then put in place
    out.to_csv(tmp, index=False)
    back = pd.read_csv(tmp, dtype=str, keep_default_na=False)
    if list(back["unit_id"]) != list(units["unit_id"]) or list(back.columns) != list(out.columns):
        fails.append("the table read back from disk does not hold the layer's units in order, or its columns")
    else:
        nirv_text = back[list(NIRV_COLUMNS) + ["missing_data_share_nirv"]]
        if nirv is None and not ((nirv_text == "").all().all() and (back["nirv_status"] == "pending").all()):
            fails.append("NIRv is pending but, in the table as written, an NIRv cell is not empty or nirv_status is not 'pending'")
        if nirv is not None and not (back["nirv_status"] == "built").all():
            fails.append("NIRv is built but nirv_status is not 'built' in every row of the table as written")
        checks["table_read_back_as_text_units_in_order_and_nirv_cells_as_stated"] = True
    if fails:
        tmp.unlink(missing_ok=True)
        print("NOT ASSEMBLED:", file=sys.stderr)
        for f in fails:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)

    os.replace(tmp, OUT / "degradation_by_unit.csv")
    blank = {col: int(out[col].isna().sum()) for col in out.columns if out[col].isna().any()}
    by_level = {k: int(v) for k, v in out["unit_level"].value_counts().items()}
    with open(OUT / "degradation_by_unit.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/02_assemble_degradation.py", "script_sha256": sha256(__file__), "run_utc": started, "inputs": inputs
                   + [entry(OUT / n, role="the source's own summary table, checked against") for n in ("hansen_by_unit_level.csv", "hansen_loss_by_canopy_band.csv", "corestack_by_unit_level.csv") + ((NIRV_LEVEL,) if nirv is not None else ())]
                   + [entry(OUT / n, role="a second per-unit table of the same source, checked against unit by unit") for n in ("hansen_by_unit_thresholds.csv", "corestack_by_unit_bands.csv")],
                   "table": {"path": "20_degradation/degradation_by_unit.csv", "rows": int(len(out)), "columns": int(len(out.columns)), "units_by_level": by_level, "blank_cells": blank},
                   "measures": {"hansen": "built", "corestack": "built", "nirv": "built" if nirv is not None else f"pending ({nirv_why}); every NIRv cell is blank and nirv_status is 'pending' in every row"},
                   "checks_passed": checks, "sums_km2": printed,
                   "note": "copied column for column from the sources' tables; nothing is computed here. NIRv is a reported column, not a degradation measure (ruling of 7 Oct 2026). "
                           "A blank CoRE Stack share means the unit has no pixel with a CoRE Stack class; a blank NIRv cell under nirv_status 'pending' means not computed yet."}, fh, indent=2)
    print(f"degradation_by_unit.csv: n = {len(out):,} units {by_level}; {len(out.columns)} columns; run_utc {started}")
    print(f"  NIRv: {'built' if nirv is not None else 'PENDING - ' + nirv_why}")
    print(f"  blank cells: {blank or 'none'}")
    print(f"  checks: {len(printed)} sums equal the sources' own summary tables (largest gap {worst:.4f} km2); {len(second)} columns equal a second per-unit table unit by unit (largest gap {worst_unit:.4f} ha); "
          f"yearly loss adds up; the canopy-band table's > 30 band equals forest_ha and hansen_loss_ha unit by unit; the table was read back as text")
    show = pd.DataFrame(printed)
    print(show[show.column.isin(["forest_ha", "hansen_loss_ha", "hansen_loss_ha_tc_gt10le30", "hansen_loss_ha_tc_le10", "corestack_degradation_ha", "corestack_partial_degradation_ha", "corestack_improvement_ha", "corestack_degradation_ha_tc_gt10"])]
          .pivot(index="column", columns="units", values="sum_km2").to_string())


if __name__ == "__main__":
    main()
