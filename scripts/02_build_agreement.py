#!/usr/bin/env python3
"""
Stage 1 - do the two measures of forest condition point at the same units? Hansen beside CoRE Stack.

    python scripts/02_build_agreement.py --units 10_units/units.gpkg

In : --units                                                 the stage-0 layer: which units there are, and their type
     20_degradation/hansen_loss_by_canopy_band_by_unit.csv   02_build_hansen.py: land and yearly loss by band of year-2000 canopy
     20_degradation/corestack_by_unit_bands.csv              02_build_corestack.py: every class by the same bands
     20_degradation/corestack_by_unit.csv                    the same source's own per-unit totals on treecover2000 > 10
     20_degradation/hansen_loss_by_canopy_band.csv, corestack_by_unit_level.csv
                                                             the two sources' own summary tables: what the margins must add up to
     and the two provenance records, which must name this layer
Out: 20_degradation/ and nowhere else
     agreement_by_unit.csv        per unit: the rates of each measure, its flags, and the agreement class
     agreement_summary.csv        by window, unit type and minimum forest: how many units each measure flags, how many
                                  both flag beside the number chance would give, and the rank correlations
     agreement_definitions.csv    the same headline for other readings of "CoRE Stack says degraded"
     agreement.provenance.json    inputs, UTC run time, definitions, checks, n and missingness

It reads tables and calls no Earth Engine. NIRv is not in this table: since 7 Oct 2026 it is a reported column, not
a degradation measure (docs/DEGRADATION.md).

WHAT IS COMPARED, AND WHY UNIT BY UNIT.
  Hansen      a year in which a 30 m pixel's tree cover was removed outright (lossyear).
  CoRE Stack  a class of change between two three-year periods inside its own tree mask: -2 tree cover lost,
              -1 canopy density or height down a class ("degradation"), 1 up a class ("improvement"), 3 and 4 one
              up and one down ("partially degraded").
They do not measure the same thing and are not expected to mark the same pixels: Hansen sees clearance and is
blind to thinning; CoRE Stack's class -1 is thinning under a canopy that still stands. The question this table
answers is the one the project needs: DO THE TWO POINT AT THE SAME UNITS? A pixel-by-pixel overlap needs one more
Earth Engine job and is not in this table.

THE REFERENCE LAND, the same for both: land with treecover2000 > 10 (the two canopy bands 10 < treecover2000 <= 30
and treecover2000 > 30 of both sources' tables). Hansen's loss inside its own mask (treecover2000 > 30) is the
larger part of it; the band 10 < treecover2000 <= 30 is land Hansen's mask leaves out and CoRE Stack covers.
  hansen rate      Hansen loss dated in the window on that land / that land (Hansen's grid)
  corestack rates  the area of a class on that land / the land there that has a CoRE Stack class from -2 to 4
                   (CoRE Stack's own 25 m grid; class 5, "missing", is left out of the denominator)

THE WINDOWS. THE FIRST IS THE HEADLINE. They are never averaged or pooled.
  common_2017_2023      Hansen loss dated 2017 to 2023 beside CoRE Stack's change 2017-2023: the span the CoRE Stack
                        product itself names. THE HEADLINE.
  between_2019_2022     Hansen loss dated 2019 to 2022 only. CoRE Stack's "2017" is the mode of the agricultural
                        years 2016-17 to 2018-19 and its "2023" that of 2022-23 to 2024-25, so a loss dated 2017 or
                        2018 falls inside its first period and one dated 2023 inside its second. This narrower
                        window holds only the years strictly between the two periods. A sensitivity row.
  full_span_2001_2025   Hansen loss in any year 2001 to 2025 beside the same CoRE Stack classes. NOT ONE PERIOD:
                        reported separately and labelled, and not a test of agreement - a unit cleared in 2005
                        counts for Hansen and cannot count for a product that starts in 2017.

A UNIT IS ASSESSED only if it has at least MIN_REFERENCE_HA (50 ha) of reference land by Hansen's grid AND at least
that much land with a CoRE Stack class there. Below that a rate is noise: one 30 m pixel is more than a thousandth
of 50 ha, and the year-to-year repeatability of a unit's Hansen loss rate falls away under it
(forest_floor_repeatability.csv). The summary repeats the headline at 10 and 100 ha. Units below the floor get the
class "insufficient_forest" - they are not "neither".

FLAGS. Among the assessed units of the layer (all unit types together, so that a flag means the same thing in an
lgd_panchayat unit and an outside_village one): a unit is flagged by Hansen if its Hansen rate is above the 80th
percentile of those units' rates (or above zero, if that percentile is zero), and by CoRE Stack if its class -1
rate is above the 80th percentile of theirs. THE FLAG IS RELATIVE: it says "in the top fifth", not "degraded by
some absolute amount" - no absolute threshold has a basis.
  agreement class   both | hansen_only | corestack_only | neither | insufficient_forest
Where both flag a unit the claim that it degraded is as strong as these two sources can make it; where one
flags it the table says which, and neither is preferred.

WHAT "AGREEMENT" IS MEASURED BY.
  expected if unrelated   n x (share flagged by Hansen) x (share flagged by CoRE Stack): what two unrelated flags of
                          these sizes would share. With two flags of a fifth each that is a twenty-fifth of the units.
  observed / expected     1 = no better than chance
  odds ratio              (both)(neither) / (hansen_only)(corestack_only), with a 95 per cent interval from
                          resampling units (percentiles 2.5 and 97.5 of BOOTSTRAP resamples)
  rank correlation        Spearman's, between the Hansen rate and each CoRE Stack rate over the assessed units,
                          with the same kind of interval. Class 1 ("improvement") is there as the placebo: if
                          Hansen's rate goes with improvement as much as with degradation, the two do not agree,
                          whatever the count of units flagged by both.
  where the area is       the share of all Hansen loss in the window that lies in units CoRE Stack flags, and of all
                          class -1 area that lies in units Hansen flags, each beside the share of the reference
                          land in those units (what an unrelated flag would hold)

OTHER READINGS OF "CORE STACK SAYS DEGRADED" (agreement_definitions.csv, headline window): class -1 alone (the
delivered one); class -1 with classes 3 and 4; the net, class -1 minus class 1; class -2 (tree cover lost), which is
the class that should go with Hansen if either product sees what the other sees. Classes -1 and 1 come from
classifiers the producers report as right about two times in three, and the two agro-climatic zone models differ
(the downward share is 0.75 in one and 0.54 in the other), so a class -1 rate carries the zone it lies in.

Needs geopandas, pandas, numpy, scipy.
"""
import argparse, datetime, hashlib, json, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
TREE = ("gt10le30", "gt30")                                  # the two canopy bands that make up treecover2000 > 10
WINDOWS = {"common_2017_2023": (2017, 2023), "between_2019_2022": (2019, 2022), "full_span_2001_2025": (2001, 2025)}
HEADLINE = "common_2017_2023"
WINDOW_IS = {"common_2017_2023": "HEADLINE: Hansen loss 2017-2023 beside CoRE Stack change 2017-2023", "between_2019_2022": "sensitivity: Hansen loss 2019-2022 (the years between CoRE Stack's two periods)",
             "full_span_2001_2025": "NOT ONE PERIOD: Hansen loss 2001-2025 beside CoRE Stack change 2017-2023"}
VALUED = ("lost", "degradation", "nochange", "improvement", "gained", "partial3", "partial4")       # classes -2 to 4; class 5 (missing) is not valued
CORE_RATES = {"degradation": ("degradation",), "degradation_with_partial": ("degradation", "partial3", "partial4"), "lost": ("lost",), "improvement": ("improvement",)}
MIN_REFERENCE_HA = 50.0
FLOORS = (10.0, 50.0, 100.0)
FLAG_PERCENTILE = 80
BOOTSTRAP, BOOTSTRAP_SEED = 2000, 20261008
LEVELS = {"all units": None, "lgd_panchayat": "lgd_panchayat", "outside_village": "outside_village"}
HA_TOLERANCE = 0.003
GRID_TOLERANCE = 0.0005                                      # the reference land summed on Hansen's grid against the same land on CoRE Stack's, all units
fails = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Stopped before writing this step's tables.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def cut_and_flag(rate, assessed):
    """The 80th percentile of the assessed units' rates, and which units lie above it (above zero if it is zero)."""
    cut = float(np.percentile(rate[assessed], FLAG_PERCENTILE))
    return cut, assessed & (rate > cut)


def classes(h_flag, c_flag, assessed):
    out = np.full(len(assessed), "insufficient_forest", dtype=object)
    out[assessed & h_flag & c_flag] = "both"
    out[assessed & h_flag & ~c_flag] = "hansen_only"
    out[assessed & ~h_flag & c_flag] = "corestack_only"
    out[assessed & ~h_flag & ~c_flag] = "neither"
    return out


def odds_ratio(a, b, c, d):
    """(both)(neither) / (hansen_only)(corestack_only); None if a cell of the denominator is empty."""
    return float(a * d / (b * c)) if b > 0 and c > 0 else None


def interval(values):
    v = np.asarray([x for x in values if x is not None and not np.isnan(x)], float)
    return (round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)) if len(v) >= 0.9 * BOOTSTRAP else (None, None)


def agreement_row(sel, h_flag, c_flag, h_rate, c_rate_by, land, h_loss, c_deg, rng):
    """The figures for one set of assessed units: counts, chance, odds ratio, correlations, and where the area lies."""
    n = int(sel.sum())
    row = {"n_assessed": n}
    if n == 0:
        return row
    hf, cf = h_flag[sel], c_flag[sel]
    a, b, c, d = int((hf & cf).sum()), int((hf & ~cf).sum()), int((~hf & cf).sum()), int((~hf & ~cf).sum())
    expected = n * hf.mean() * cf.mean()
    row.update({"flagged_by_hansen": a + b, "flagged_by_corestack": a + c, "both": a, "hansen_only": b, "corestack_only": c, "neither": d,
                "both_expected_if_unrelated": round(float(expected), 2), "both_observed_over_expected": round(a / expected, 3) if expected > 0 else None,
                "odds_ratio": round(odds_ratio(a, b, c, d), 3) if odds_ratio(a, b, c, d) is not None else None})
    idx = np.flatnonzero(sel)
    draws = rng.integers(0, n, size=(BOOTSTRAP, n))
    ors, ratios = [], []
    for k in range(BOOTSTRAP):
        h_, c_ = hf[draws[k]], cf[draws[k]]
        a_, b_, c__, d_ = (h_ & c_).sum(), (h_ & ~c_).sum(), (~h_ & c_).sum(), (~h_ & ~c_).sum()
        ors.append(odds_ratio(a_, b_, c__, d_))
        e_ = n * h_.mean() * c_.mean()
        ratios.append(a_ / e_ if e_ > 0 else None)
    row["odds_ratio_lo95"], row["odds_ratio_hi95"] = interval(ors)
    row["both_observed_over_expected_lo95"], row["both_observed_over_expected_hi95"] = interval(ratios)
    for name, rate in c_rate_by.items():
        x, y = h_rate[idx], rate[idx]
        if np.std(x) == 0 or np.std(y) == 0:
            row[f"spearman_hansen_vs_corestack_{name}"] = None
            continue
        row[f"spearman_hansen_vs_corestack_{name}"] = round(float(spearmanr(x, y)[0]), 4)
        if name in ("degradation", "net", "improvement", "lost"):
            boot = [spearmanr(x[draws[k]], y[draws[k]])[0] for k in range(0, BOOTSTRAP, 4)]          # every fourth resample: 500 are enough for an interval
            v = np.asarray(boot, float); v = v[~np.isnan(v)]
            row[f"spearman_hansen_vs_corestack_{name}_lo95"], row[f"spearman_hansen_vs_corestack_{name}_hi95"] = round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)
    tot_land, tot_loss, tot_deg = land[sel].sum(), h_loss[sel].sum(), c_deg[sel].sum()
    row.update({"reference_km2": round(float(tot_land) / 100, 2), "hansen_loss_km2": round(float(tot_loss) / 100, 2), "corestack_degradation_km2": round(float(tot_deg) / 100, 2),
                "hansen_loss_pct_in_units_corestack_flags": round(100 * float(h_loss[sel & c_flag].sum() / tot_loss), 2) if tot_loss > 0 else None,
                "reference_land_pct_in_units_corestack_flags": round(100 * float(land[sel & c_flag].sum() / tot_land), 2),
                "corestack_degradation_pct_in_units_hansen_flags": round(100 * float(c_deg[sel & h_flag].sum() / tot_deg), 2) if tot_deg > 0 else None,
                "reference_land_pct_in_units_hansen_flags": round(100 * float(land[sel & h_flag].sum() / tot_land), 2)})
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    layer_sha = sha256(a.units)
    units = pd.DataFrame(gpd.read_file(a.units, layer="units", ignore_geometry=True))[["unit_id", "unit_level", "outside_village"]]
    units["unit_id"] = units["unit_id"].astype(str)
    units = units.sort_values("unit_id").reset_index(drop=True)
    inputs = [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": layer_sha}]

    def load(table, record):
        tp, rp = OUT / table, OUT / record
        if not tp.exists() or not rp.exists():
            fails.append(f"{table} or {record} is missing: build that source first")
            return None
        prov = json.load(open(rp))
        if layer_sha not in [i.get("sha256") for i in prov.get("inputs", []) if i.get("path") == str(a.units)]:
            fails.append(f"{record} does not name this layer ({a.units}, sha256 {layer_sha[:12]}...)")
        t = pd.read_csv(tp, dtype={"unit_id": str})
        if len(t) != len(units) or not t["unit_id"].is_unique or set(t["unit_id"]) != set(units["unit_id"]):
            fails.append(f"{table} holds {len(t):,} rows and {t['unit_id'].nunique():,} distinct unit_id; the layer has {len(units):,} units")
            return None
        inputs.append({"path": str(tp.relative_to(ROOT)), "bytes": tp.stat().st_size, "sha256": sha256(tp), "built_by": prov.get("script"), "run_utc": prov.get("run_utc")})
        return t.set_index("unit_id").loc[units["unit_id"]]

    hb = load("hansen_loss_by_canopy_band_by_unit.csv", "hansen.provenance.json")
    cb = load("corestack_by_unit_bands.csv", "corestack.provenance.json")
    cu = load("corestack_by_unit.csv", "corestack.provenance.json")
    stop_if_failed("reading the two sources' tables")
    level = units["unit_level"].to_numpy()
    print(f"{a.units}: n = {len(units):,} units ({dict(units['unit_level'].value_counts())})")

    # ---- the margins, and what they must add up to -----------------------------------------------------------------------
    land = sum(hb[f"area_ha_{b}"].to_numpy(float) for b in TREE)                                   # Hansen's grid
    loss = {w: sum(hb[f"loss_ha_{b}_{y}"].to_numpy(float) for b in TREE for y in range(lo, hi + 1)) for w, (lo, hi) in WINDOWS.items()}
    cls = {k: sum(cb[f"class_{k}_ha_{b}"].to_numpy(float) for b in TREE) for k in VALUED + ("missing",)}
    valued = sum(cls[k] for k in VALUED)                                                           # CoRE Stack's grid
    checks = {}
    for b in TREE + ("le10",):                                                                      # the yearly columns are what the windows are made of
        gap = float(np.abs(sum(hb[f"loss_ha_{b}_{y}"].to_numpy(float) for y in range(2001, 2026)) - hb[f"loss_ha_{b}"].to_numpy(float)).max())
        if gap > HA_TOLERANCE:
            fails.append(f"band {b}: the yearly loss columns do not add up to loss_ha_{b} (largest gap {gap:.4f} ha)")
    hs = pd.read_csv(OUT / "hansen_loss_by_canopy_band.csv").set_index(["units", "canopy_band"])
    cl = pd.read_csv(OUT / "corestack_by_unit_level.csv").set_index(["units", "land"])
    worst = 0.0
    for label, lv in LEVELS.items():
        sel = level == lv if lv else np.ones(len(units), bool)
        for b in TREE:
            for theirs, years in (("loss_km2_2001_2010", range(2001, 2011)), ("loss_km2_2011_2017", range(2011, 2018)), ("loss_km2_2018_2025", range(2018, 2026)), ("loss_km2_2001_2025", range(2001, 2026))):
                mine = float(sum(hb.loc[sel, f"loss_ha_{b}_{y}"].sum() for y in years)) / 100
                worst = max(worst, abs(mine - float(hs.loc[(label, b), theirs])))
                if abs(mine - float(hs.loc[(label, b), theirs])) > 0.006:
                    fails.append(f"{label}, band {b}: yearly loss sums to {mine:,.3f} km2 over {years[0]}-{years[-1]}; hansen_loss_by_canopy_band.csv prints {float(hs.loc[(label, b), theirs]):,.2f}")
            mine = float(hb.loc[sel, f"area_ha_{b}"].sum()) / 100
            if abs(mine - float(hs.loc[(label, b), "land_km2"])) > 0.006:
                fails.append(f"{label}, band {b}: land sums to {mine:,.3f} km2; hansen_loss_by_canopy_band.csv prints {float(hs.loc[(label, b), 'land_km2']):,.2f}")
        for k, theirs in (("degradation", "degradation_km2"), ("lost", "loss_km2"), ("improvement", "improvement_km2"), ("gained", "gain_km2")):
            mine = float(cls[k][sel].sum()) / 100
            worst = max(worst, abs(mine - float(cl.loc[(label, "treecover2000 > 10"), theirs])))
            if abs(mine - float(cl.loc[(label, "treecover2000 > 10"), theirs])) > 0.006:
                fails.append(f"{label}: CoRE Stack class {k} on treecover2000 > 10 sums to {mine:,.3f} km2; corestack_by_unit_level.csv prints {float(cl.loc[(label, 'treecover2000 > 10'), theirs]):,.2f}")
        mine = float((cls["partial3"] + cls["partial4"])[sel].sum()) / 100
        if abs(mine - float(cl.loc[(label, "treecover2000 > 10"), "partial_degradation_km2"])) > 0.006:
            fails.append(f"{label}: classes 3 and 4 on treecover2000 > 10 sum to {mine:,.3f} km2; corestack_by_unit_level.csv prints {float(cl.loc[(label, 'treecover2000 > 10'), 'partial_degradation_km2']):,.2f}")
    checks["margins_against_the_sources_own_summary_tables_largest_gap_km2"] = round(worst, 4)
    gap = float(np.abs(cls["degradation"] - cu["corestack_degradation_ha_tc_gt10"].to_numpy(float)).max())
    checks["corestack_degradation_on_reference_land_two_tables_largest_gap_ha"] = round(gap, 5)
    if gap > HA_TOLERANCE:
        fails.append(f"class -1 on treecover2000 > 10 differs between corestack_by_unit_bands.csv and corestack_by_unit.csv (largest gap {gap:.4f} ha)")
    grid = float(sum(cb[f"land_ha_{b}"].to_numpy(float) for b in TREE).sum() / land.sum() - 1)
    checks["reference_land_on_corestack_grid_vs_hansen_grid_all_units"] = round(grid, 6)
    if abs(grid) > GRID_TOLERANCE:
        fails.append(f"the reference land summed on CoRE Stack's grid differs from Hansen's by {grid:+.4%} over all units")
    stop_if_failed("checking the margins against the two sources' own tables")
    print(f"OK  the windows' yearly columns and the CoRE Stack classes add up to the two sources' own summary tables (largest gap {worst:.4f} km2); "
          f"the reference land is {land.sum() / 100:,.1f} km2 on Hansen's grid and {grid:+.4%} from that on CoRE Stack's")

    # ---- rates, flags and classes, at the delivered floor -----------------------------------------------------------------
    with np.errstate(invalid="ignore", divide="ignore"):
        h_rate = {w: np.where(land > 0, loss[w] / land, np.nan) for w in WINDOWS}
        c_rate = {name: np.where(valued > 0, sum(cls[k] for k in parts) / valued, np.nan) for name, parts in CORE_RATES.items()}
        c_rate["net"] = np.where(valued > 0, (cls["degradation"] - cls["improvement"]) / valued, np.nan)
    assessed_at = {f: (land >= f) & (valued >= f) for f in FLOORS}
    assessed = assessed_at[MIN_REFERENCE_HA]
    by_unit = units.copy()
    by_unit["reference_ha"] = np.round(land, 4)
    by_unit["corestack_valued_ha"] = np.round(valued, 4)
    by_unit["assessed"] = assessed.astype(int)
    cuts, flag = {}, {}
    cuts["corestack_degradation"], flag["corestack"] = cut_and_flag(np.nan_to_num(c_rate["degradation"]), assessed)
    for w in WINDOWS:
        cuts[f"hansen_{w}"], flag[f"hansen_{w}"] = cut_and_flag(np.nan_to_num(h_rate[w]), assessed)
        by_unit[f"hansen_loss_ha_{w}"] = np.round(loss[w], 4)
        by_unit[f"hansen_rate_{w}"] = np.round(h_rate[w], 6)
    for k, parts in (("degradation", ("degradation",)), ("partial_degradation", ("partial3", "partial4")), ("lost", ("lost",)), ("improvement", ("improvement",))):
        by_unit[f"corestack_{k}_ha"] = np.round(sum(cls[p] for p in parts), 4)
    for name in ("degradation", "degradation_with_partial", "net", "lost", "improvement"):
        by_unit[f"corestack_rate_{name}"] = np.round(c_rate[name], 6)
    by_unit["corestack_flag"] = pd.array(np.where(assessed, flag["corestack"].astype(int), 0), dtype="Int64")
    by_unit.loc[~assessed, "corestack_flag"] = pd.NA
    for w in WINDOWS:
        by_unit[f"hansen_flag_{w}"] = pd.array(np.where(assessed, flag[f"hansen_{w}"].astype(int), 0), dtype="Int64")
        by_unit.loc[~assessed, f"hansen_flag_{w}"] = pd.NA
        by_unit[f"agreement_class_{w}"] = classes(flag[f"hansen_{w}"], flag["corestack"], assessed)
    by_unit = by_unit.rename(columns={f"agreement_class_{HEADLINE}": "agreement_class"})
    order = ["unit_id", "unit_level", "outside_village", "reference_ha", "corestack_valued_ha", "assessed", "agreement_class"]
    by_unit = by_unit[order + [c for c in by_unit.columns if c not in order]]
    counted = by_unit["agreement_class"].value_counts()
    if int(counted.drop("insufficient_forest", errors="ignore").sum()) != int(assessed.sum()) or int(counted.get("insufficient_forest", 0)) != int((~assessed).sum()):
        fails.append("the agreement classes do not add up to the assessed and the unassessed units")
    stop_if_failed("classifying the units")

    # ---- the summary: every window, unit type and floor ---------------------------------------------------------------------
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    rows = []
    for w in WINDOWS:
        for floor in FLOORS:
            ok = assessed_at[floor]
            cut_h, hf = cut_and_flag(np.nan_to_num(h_rate[w]), ok)
            cut_c, cf = cut_and_flag(np.nan_to_num(c_rate["degradation"]), ok)
            for label, lv in LEVELS.items():
                in_level = level == lv if lv else np.ones(len(units), bool)
                row = {"window": w, "window_is": WINDOW_IS[w], "minimum_reference_ha": floor, "delivered": int(w == HEADLINE and floor == MIN_REFERENCE_HA), "units": label,
                       "n_units": int(in_level.sum()), "n_insufficient_forest": int((in_level & ~ok).sum()), "hansen_rate_cut": round(cut_h, 6), "corestack_degradation_rate_cut": round(cut_c, 6)}
                row.update(agreement_row(in_level & ok, hf, cf, np.nan_to_num(h_rate[w]), {k: np.nan_to_num(v) for k, v in c_rate.items()}, land, loss[w], cls["degradation"], rng))
                rows.append(row)
    summary = pd.DataFrame(rows)
    head = summary[(summary.window == HEADLINE) & (summary.minimum_reference_ha == MIN_REFERENCE_HA)].set_index("units")
    for label, lv in LEVELS.items():                                       # the summary's counts are the per-unit table's
        sel = by_unit["unit_level"] == lv if lv else np.ones(len(by_unit), bool)
        n_ = by_unit.loc[sel, "agreement_class"].value_counts()
        for k in ("both", "hansen_only", "corestack_only", "neither"):
            if int(n_.get(k, 0)) != int(head.loc[label, k]):
                fails.append(f"{label}: {int(n_.get(k, 0))} units are '{k}' in agreement_by_unit.csv and {int(head.loc[label, k])} in the summary")
    stop_if_failed("checking the summary against the per-unit table")

    drows = []
    ok = assessed
    hf = flag[f"hansen_{HEADLINE}"]
    for name, what in (("degradation", "class -1 (delivered)"), ("degradation_with_partial", "classes -1, 3 and 4"), ("net", "class -1 minus class 1"), ("lost", "class -2, tree cover lost"),
                       ("improvement", "class 1, improvement (the placebo)")):
        cut_c, cf = cut_and_flag(np.nan_to_num(c_rate[name]), ok)
        for label, lv in LEVELS.items():
            in_level = level == lv if lv else np.ones(len(units), bool)
            row = {"window": HEADLINE, "minimum_reference_ha": MIN_REFERENCE_HA, "corestack_flag_is": what, "corestack_rate": name, "units": label, "corestack_rate_cut": round(cut_c, 6)}
            r = agreement_row(in_level & ok, hf, cf, np.nan_to_num(h_rate[HEADLINE]), {name: np.nan_to_num(c_rate[name])}, land, loss[HEADLINE], sum(cls[k] for k in CORE_RATES.get(name, ("degradation",))), rng)
            row.update({k: v for k, v in r.items() if not k.startswith(("hansen_loss_pct", "reference_land_pct", "corestack_degradation_pct", "reference_km2", "hansen_loss_km2", "corestack_degradation_km2"))})
            drows.append(row)
    definitions = pd.DataFrame(drows)

    out_tables = {"agreement_by_unit.csv": by_unit, "agreement_summary.csv": summary, "agreement_definitions.csv": definitions}
    for name, t in out_tables.items():
        t.to_csv(OUT / name, index=False)
    blank = lambda t: {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}
    with open(OUT / "agreement.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/02_build_agreement.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "inputs": inputs + [{"path": f"20_degradation/{n}", "sha256": sha256(OUT / n), "role": "the source's own summary table, checked against"} for n in ("hansen_loss_by_canopy_band.csv", "corestack_by_unit_level.csv")],
                   "definitions": {"measures": ["Hansen tree-cover loss", "CoRE Stack tree-change classes 2017-2023"], "not_in_this_table": "NIRv (a reported column since 7 Oct 2026)",
                                   "reference_land": "treecover2000 > 10 (canopy bands gt10le30 and gt30)", "windows": {w: {"hansen_loss_years": list(v), "is": WINDOW_IS[w]} for w, v in WINDOWS.items()},
                                   "headline_window": HEADLINE, "assessed": f"at least {MIN_REFERENCE_HA:g} ha of reference land on Hansen's grid and at least that much with a CoRE Stack class from -2 to 4",
                                   "flag": f"rate above the {FLAG_PERCENTILE}th percentile of the assessed units' rates (above zero if that is zero); all unit types together",
                                   "cuts_at_the_delivered_floor": {k: round(v, 6) for k, v in cuts.items()}, "corestack_flag_rate": "class -1 over the valued land",
                                   "intervals": f"percentiles 2.5 and 97.5 of {BOOTSTRAP} resamples of units (every fourth for the correlations), seed {BOOTSTRAP_SEED}"},
                   "checks_passed": {**checks, "classes_add_up_to_the_units": True, "summary_counts_equal_the_per_unit_table": True},
                   "counts": {"units": int(len(units)), "assessed": int(assessed.sum()), "by_level": {lab: {k: int(v) for k, v in by_unit.loc[(by_unit['unit_level'] == lv) if lv else slice(None), "agreement_class"].value_counts().items()} for lab, lv in LEVELS.items()}},
                   "tables": {name: {"rows": int(len(t)), "columns": int(len(t.columns)), "blank_cells": blank(t)} for name, t in out_tables.items()},
                   "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__}}, fh, indent=2)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    print(f"\nagreement_by_unit.csv: n = {len(by_unit):,} units; assessed (at least {MIN_REFERENCE_HA:g} ha of reference land on both grids): {int(assessed.sum()):,}; "
          f"insufficient forest: {int((~assessed).sum()):,}. Cuts: Hansen {HEADLINE} rate > {cuts['hansen_' + HEADLINE]:.4%}; CoRE Stack class -1 rate > {cuts['corestack_degradation']:.2%}")
    show = ["window", "units", "n_units", "n_insufficient_forest", "n_assessed", "both", "hansen_only", "corestack_only", "neither", "both_expected_if_unrelated", "both_observed_over_expected",
            "odds_ratio", "odds_ratio_lo95", "odds_ratio_hi95", "spearman_hansen_vs_corestack_degradation", "spearman_hansen_vs_corestack_net", "spearman_hansen_vs_corestack_lost", "spearman_hansen_vs_corestack_improvement"]
    print(f"\nagreement_summary.csv: n = {len(summary)} rows; shown: the delivered floor, every window")
    print(summary[summary.minimum_reference_ha == MIN_REFERENCE_HA][show].T.to_string(header=False))
    print(f"\nagreement_definitions.csv: n = {len(definitions)} rows; all units:")
    print(definitions[definitions.units == "all units"][["corestack_flag_is", "corestack_rate_cut", "both", "both_expected_if_unrelated", "both_observed_over_expected", "odds_ratio", "odds_ratio_lo95", "odds_ratio_hi95"]].to_string(index=False))
    print(f"\ndone. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
