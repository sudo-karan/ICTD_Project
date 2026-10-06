#!/usr/bin/env python3
"""
Stage 1, task E - a minimum forest area for a unit to enter stage 4: a RECOMMENDATION, applied to nothing.

    python scripts/02_propose_forest_floor.py

In : 20_degradation/hansen_by_unit.csv, hansen_by_unit_thresholds.csv     (02_build_hansen.py)
Out: 20_degradation/ and nowhere else
     forest_floor_options.csv          for each candidate floor: units kept, by unit type, and the share of forest
                                       and of loss they hold
     forest_floor_repeatability.csv    by class of forest area: how repeatable a unit's loss rate is
     forest_floor.provenance.json      inputs, UTC run time, the rule, the proposal

Stage 1 covers all 11,468 units whatever this says. Nothing here removes a row from any table.

THE PROBLEM. Thousands of units have no forest by the mask (treecover2000 > 30) and thousands more have under
a hectare. A loss RATE for such a unit - hansen_loss_ha / forest_ha - is a ratio of a few pixels, and one pixel
of a 30 m grid is about 0.07 ha.

THE RULE USED TO CHOOSE. A unit's loss rate is worth entering in a model only if it is a property of the unit
and not of chance. That can be measured without any outside data: split the 25 years into the odd ones and the
even ones, compute each unit's loss rate from each half, and see how alike the two halves rank the units
(Spearman rank correlation), separately for units of each size. Where the halves disagree, the rate is noise.
The floor proposed is the bottom of the SMALLEST class of forest area in which that correlation reaches
REPEATABILITY (0.8), a conventional mark for a measure being reliable enough to use. The mark is a convention
and is stated as one; forest_floor_repeatability.csv gives every class so that another can be read off.

WHAT IT IS A FLOOR ON. forest_ha, the Hansen mask, because that is the denominator of the Hansen loss rate.
The same floors are also counted on land with treecover2000 > 10 (forest_ha_gt10), the wider land on which the
NIRv and CoRE Stack measures are set beside Hansen, and the options table says how many units pass one and
fail the other: a floor on the mask drops, by construction, the units whose tree cover is open.

Needs pandas, numpy, scipy.
"""
import datetime, hashlib, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
BY_UNIT, THRESHOLDS = OUT / "hansen_by_unit.csv", OUT / "hansen_by_unit_thresholds.csv"
YEARS = list(range(2001, 2026))
CLASS_EDGES = [0, 0.5, 1, 2, 5, 10, 25, 50, 100, 250, 500, 1000, float("inf")]     # hectares of forest; a class is [lower, upper)
FLOORS = [0.5, 1, 5, 10, 25, 50, 100, 250, 500, 1000]                                # candidate floors, hectares
REPEATABILITY = 0.8
PIXEL_HA = 0.0725                                                                    # one Hansen pixel in the middle of the state (722 m2)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    h = pd.read_csv(BY_UNIT, dtype={"unit_id": str})
    t = pd.read_csv(THRESHOLDS, dtype={"unit_id": str})
    d = h.merge(t[["unit_id", "unit_level", "forest_ha_gt10", "hansen_loss_ha_gt10"]], on="unit_id", validate="one_to_one")
    if len(d) != len(h) or not np.allclose(d[[f"hansen_loss_ha_{y}" for y in YEARS]].sum(axis=1), d["hansen_loss_ha"], atol=0.002):
        sys.exit("the Hansen tables do not line up, or the yearly losses do not add up to the total")
    odd = d[[f"hansen_loss_ha_{y}" for y in YEARS if y % 2 == 1]].sum(axis=1)
    even = d[[f"hansen_loss_ha_{y}" for y in YEARS if y % 2 == 0]].sum(axis=1)
    has = d["forest_ha"] > 0
    d["rate"] = (d["hansen_loss_ha"] / d["forest_ha"]).where(has)
    d["rate_odd"], d["rate_even"] = (odd / d["forest_ha"]).where(has), (even / d["forest_ha"]).where(has)
    lgd = d["unit_level"] == "lgd_panchayat"
    pooled = float(d["hansen_loss_ha"].sum() / d["forest_ha"].sum())
    print(f"hansen_by_unit.csv: n = {len(d):,} units ({int(lgd.sum()):,} lgd_panchayat, {int((~lgd).sum()):,} outside_village); with any forest {int(has.sum()):,}; "
          f"forest {d['forest_ha'].sum() / 100:,.1f} km2, loss {d['hansen_loss_ha'].sum() / 100:,.2f} km2, pooled 25-year loss rate {pooled:.4f}")

    rows = []
    for lo, hi in zip(CLASS_EDGES, CLASS_EDGES[1:]):
        g = d[has & (d["forest_ha"] >= lo) & (d["forest_ha"] < hi)] if lo > 0 else d[has & (d["forest_ha"] < hi)]
        rho = float(spearmanr(g["rate_odd"], g["rate_even"])[0]) if len(g) > 2 and g["rate_odd"].nunique() > 1 and g["rate_even"].nunique() > 1 else None
        rows.append({"forest_ha_from": lo, "forest_ha_below": hi if np.isfinite(hi) else None, "n_units": int(len(g)), "n_lgd_panchayat": int((g["unit_level"] == "lgd_panchayat").sum()),
                     "n_outside_village": int((g["unit_level"] != "lgd_panchayat").sum()), "forest_km2": round(g["forest_ha"].sum() / 100, 2), "loss_km2": round(g["hansen_loss_ha"].sum() / 100, 2),
                     "units_with_no_loss": int((g["hansen_loss_ha"] == 0).sum()), "median_loss_rate": round(float(g["rate"].median()), 5) if len(g) else None,
                     "pixels_of_forest_at_the_bottom_of_the_class": round(lo / PIXEL_HA, 1), "one_pixel_as_share_of_forest_at_the_bottom": round(PIXEL_HA / lo, 4) if lo else None,
                     "odd_years_vs_even_years_spearman": None if rho is None else round(rho, 3)})
    rep = pd.DataFrame(rows)
    good = rep[(rep["forest_ha_from"] > 0) & (rep["odd_years_vs_even_years_spearman"] >= REPEATABILITY)]
    # the proposal: the bottom of the smallest class from which EVERY larger class is repeatable too
    ok = (rep["odd_years_vs_even_years_spearman"] >= REPEATABILITY).to_numpy()
    first = next((i for i in range(1, len(rep)) if ok[i:].all()), None)
    if first is None:
        sys.exit(f"no class of forest area reaches a repeatability of {REPEATABILITY}: there is nothing to propose")
    proposal = float(rep["forest_ha_from"].iloc[first])
    alternatives = [f for f in (10.0, 100.0) if f != proposal][:2]

    rows = []
    tot = {"forest": d["forest_ha"].sum(), "loss": d["hansen_loss_ha"].sum(), "forest_gt10": d["forest_ha_gt10"].sum(), "loss_gt10": d["hansen_loss_ha_gt10"].sum()}
    for f in FLOORS:
        keep, keep10 = d["forest_ha"] >= f, d["forest_ha_gt10"] >= f
        g = d[keep]
        rho = float(spearmanr(g["rate_odd"], g["rate_even"])[0])
        row = {"floor_ha": f, "role": "PROPOSED" if f == proposal else "alternative" if f in alternatives else "",
               "units_kept": int(keep.sum()), "units_kept_pct": round(100 * keep.mean(), 2),
               "lgd_panchayat_kept": int((keep & lgd).sum()), "lgd_panchayat_kept_pct": round(100 * (keep & lgd).sum() / lgd.sum(), 2),
               "outside_village_kept": int((keep & ~lgd).sum()), "outside_village_kept_pct": round(100 * (keep & ~lgd).sum() / (~lgd).sum(), 2),
               "forest_kept_pct": round(100 * g["forest_ha"].sum() / tot["forest"], 3), "loss_kept_pct": round(100 * g["hansen_loss_ha"].sum() / tot["loss"], 3),
               "forest_kept_pct_lgd_panchayat": round(100 * d.loc[keep & lgd, "forest_ha"].sum() / d.loc[lgd, "forest_ha"].sum(), 3),
               "forest_kept_pct_outside_village": round(100 * d.loc[keep & ~lgd, "forest_ha"].sum() / d.loc[~lgd, "forest_ha"].sum(), 3),
               "kept_units_with_no_loss": int((g["hansen_loss_ha"] == 0).sum()), "odd_vs_even_spearman_among_kept": round(rho, 3),
               "one_pixel_as_pct_of_forest_at_the_floor": round(100 * PIXEL_HA / f, 2),
               "units_kept_if_the_floor_were_on_treecover2000_gt10": int(keep10.sum()), "lgd_panchayat_kept_gt10": int((keep10 & lgd).sum()), "outside_village_kept_gt10": int((keep10 & ~lgd).sum()),
               "units_passing_gt10_but_failing_the_mask": int((keep10 & ~keep).sum()), "of_them_lgd_panchayat": int((keep10 & ~keep & lgd).sum()),
               "land_gt10_kept_pct_if_on_gt10": round(100 * d.loc[keep10, "forest_ha_gt10"].sum() / tot["forest_gt10"], 3)}
        rows.append(row)
    options = pd.DataFrame(rows)

    OUT.mkdir(exist_ok=True)
    options.to_csv(OUT / "forest_floor_options.csv", index=False)
    rep.to_csv(OUT / "forest_floor_repeatability.csv", index=False)
    with open(OUT / "forest_floor.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/02_propose_forest_floor.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "inputs": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in (BY_UNIT, THRESHOLDS)],
                   "status": "A RECOMMENDATION FOR STAGE 4, for the project owner to rule on. Applied to no table.",
                   "rule": f"the bottom of the smallest class of forest_ha from which every larger class has a rank correlation of at least {REPEATABILITY} "
                           "between a unit's loss rate in odd years and in even years",
                   "proposal_ha": proposal, "alternatives_ha": alternatives, "repeatability_mark": REPEATABILITY, "pooled_25_year_loss_rate": pooled,
                   "n": {"units": int(len(d)), "with_any_forest": int(has.sum()), "lgd_panchayat": int(lgd.sum()), "outside_village": int((~lgd).sum())},
                   "tables": {"forest_floor_options.csv": {"rows": int(len(options)), "blank_cells": {}},
                              "forest_floor_repeatability.csv": {"rows": int(len(rep)), "blank_cells": {c: int(rep[c].isna().sum()) for c in rep.columns if rep[c].isna().any()}}},
                   "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__}}, fh, indent=2)

    pd.set_option("display.width", 250)
    print(f"\nforest_floor_repeatability.csv: n = {len(rep)} classes of forest_ha (units with no forest are in none)")
    print(rep[["forest_ha_from", "forest_ha_below", "n_units", "n_lgd_panchayat", "n_outside_village", "units_with_no_loss", "median_loss_rate", "odd_years_vs_even_years_spearman"]].to_string(index=False))
    print(f"\nPROPOSAL: forest_ha >= {proposal:g} ha - the smallest class from which every class reaches {REPEATABILITY}. Alternatives shown: {alternatives}")
    print(f"\nforest_floor_options.csv: n = {len(options)} candidate floors")
    print(options[["floor_ha", "role", "units_kept", "lgd_panchayat_kept", "outside_village_kept", "forest_kept_pct", "loss_kept_pct", "odd_vs_even_spearman_among_kept",
                   "units_kept_if_the_floor_were_on_treecover2000_gt10", "units_passing_gt10_but_failing_the_mask", "of_them_lgd_panchayat"]].to_string(index=False))
    print(f"\ndone. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
