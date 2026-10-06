#!/usr/bin/env python3
"""
A direct check of the agreement table's arithmetic. Reads, writes nothing, exits 1 if a check fails.

    python scripts/verify_agreement.py

It shares no code with scripts/02_build_agreement.py. From the two sources' per-unit tables it rebuilds, in plain
pandas, everything the three agreement tables hold - the reference land, the loss in each window, the rates, which
units are assessed, the cuts, the flags, the classes, the counts, the number chance would give, the odds ratios,
the rank correlations and the area shares - and compares cell by cell. The bootstrap intervals depend on the
random draws and are not rebuilt: each is checked to contain its own estimate and against an independent
bootstrap made here.

In : 20_degradation/hansen_loss_by_canopy_band_by_unit.csv, corestack_by_unit_bands.csv   (the sources)
     20_degradation/agreement_by_unit.csv, agreement_summary.csv, agreement_definitions.csv, agreement.provenance.json
     20_degradation/degradation_by_unit.csv   (one cross-check: the mask's loss in the window, from the other table)
"""
import json, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

D = Path(__file__).resolve().parent.parent / "20_degradation"
results = []


def check(what, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {what}" + (f"   {detail}" if detail else ""))


def close(a, b, tol):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(((np.isnan(a) & np.isnan(b)) | (np.abs(a - b) <= tol)).all())


h = pd.read_csv(D / "hansen_loss_by_canopy_band_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
c = pd.read_csv(D / "corestack_by_unit_bands.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
u = pd.read_csv(D / "agreement_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
s = pd.read_csv(D / "agreement_summary.csv")
d = pd.read_csv(D / "agreement_definitions.csv")
prov = json.load(open(D / "agreement.provenance.json"))
check("the three tables hold the same units, each once", h.index.equals(c.index) and h.index.equals(u.index) and u.index.is_unique, f"n = {len(u):,}")

# ---- the per-unit table, column by column ---------------------------------------------------------------------------------
ref = h["area_ha_gt10le30"] + h["area_ha_gt30"]
val = sum(c[f"class_{k}_ha_{b}"] for k in ("lost", "degradation", "nochange", "improvement", "gained", "partial3", "partial4") for b in ("gt10le30", "gt30"))
check("reference_ha is the land with treecover2000 > 10 of Hansen's canopy-band table", close(u.reference_ha, ref, 1e-3))
check("corestack_valued_ha is classes -2 to 4 on that land", close(u.corestack_valued_ha, val, 1e-3))
windows = {"common_2017_2023": range(2017, 2024), "between_2019_2022": range(2019, 2023), "full_span_2001_2025": range(2001, 2026)}
loss = {w: sum(h[f"loss_ha_{b}_{y}"] for b in ("gt10le30", "gt30") for y in years) for w, years in windows.items()}
klass = {"degradation": ["degradation"], "partial_degradation": ["partial3", "partial4"], "lost": ["lost"], "improvement": ["improvement"]}
area = {k: sum(c[f"class_{p}_ha_{b}"] for p in parts for b in ("gt10le30", "gt30")) for k, parts in klass.items()}
for w in windows:
    check(f"hansen_loss_ha_{w} is the yearly loss of those years on that land", close(u[f"hansen_loss_ha_{w}"], loss[w], 1e-3))
    check(f"hansen_rate_{w} is that loss over reference_ha", close(u[f"hansen_rate_{w}"], (loss[w] / ref).where(ref > 0), 2e-6))
for k in klass:
    check(f"corestack_{k}_ha is that class on the reference land", close(u[f"corestack_{k}_ha"], area[k], 1e-3))
rate = {"degradation": area["degradation"] / val, "degradation_with_partial": (area["degradation"] + area["partial_degradation"]) / val, "net": (area["degradation"] - area["improvement"]) / val,
        "lost": area["lost"] / val, "improvement": area["improvement"] / val}
for k, r in rate.items():
    check(f"corestack_rate_{k} is over corestack_valued_ha", close(u[f"corestack_rate_{k}"], r.where(val > 0), 2e-6))
floor = 50.0
ok = (ref >= floor) & (val >= floor)
check(f"assessed is at least {floor:g} ha on both grids", (u.assessed == ok.astype(int)).all(), f"{int(ok.sum()):,} assessed, {int((~ok).sum()):,} not")
cut_c = np.percentile(rate["degradation"][ok], 80)
cflag = ok & (rate["degradation"] > cut_c)
check("corestack_flag is the class -1 rate above its 80th percentile among assessed units", (u.corestack_flag.fillna(-1).astype(int) == np.where(ok, cflag.astype(int), -1)).all(), f"cut {cut_c:.6f}; {int(cflag.sum())} flagged")
check("the cut recorded for CoRE Stack is that percentile", abs(prov["definitions"]["cuts_at_the_delivered_floor"]["corestack_degradation"] - cut_c) < 2e-6)
flags = {}
for w in windows:
    r = (loss[w] / ref).where(ref > 0).fillna(0)
    cut = np.percentile(r[ok], 80)
    flags[w] = ok & (r > cut)
    check(f"hansen_flag_{w} is the rate above its 80th percentile among assessed units", (u[f"hansen_flag_{w}"].fillna(-1).astype(int) == np.where(ok, flags[w].astype(int), -1)).all(), f"cut {cut:.6f}; {int(flags[w].sum())} flagged")
    check(f"the cut recorded for Hansen, {w}", abs(prov["definitions"]["cuts_at_the_delivered_floor"][f"hansen_{w}"] - cut) < 2e-6)
    mine = np.where(~ok, "insufficient_forest", np.where(flags[w] & cflag, "both", np.where(flags[w], "hansen_only", np.where(cflag, "corestack_only", "neither"))))
    col = "agreement_class" if w == "common_2017_2023" else f"agreement_class_{w}"
    check(f"{col} follows from the two flags", (u[col].to_numpy() == mine).all(), str(pd.Series(mine).value_counts().to_dict()))
check("every unit below the floor is 'insufficient_forest', and none above it", ((u.agreement_class == "insufficient_forest") == ~ok.to_numpy()).all())

# ---- the summary, row by row -----------------------------------------------------------------------------------------------
rng = np.random.default_rng(1)
level = u.unit_level
bad = {"counts": 0, "chance": 0, "odds": 0, "spearman": 0, "areas": 0, "interval_holds_estimate": 0, "interval_far_from_ours": 0}
n_rows = 0
for row in s.itertuples():
    f = row.minimum_reference_ha
    okf = (ref >= f) & (val >= f)
    r = (loss[row.window] / ref).where(ref > 0).fillna(0)
    hf = okf & (r > np.percentile(r[okf], 80))
    rc = rate["degradation"].fillna(0)
    cf = okf & (rc > np.percentile(rc[okf], 80))
    sel = okf & ((level == row.units) if row.units != "all units" else True)
    n = int(sel.sum())
    a, b, c_, dd = int((sel & hf & cf).sum()), int((sel & hf & ~cf).sum()), int((sel & ~hf & cf).sum()), int((sel & ~hf & ~cf).sum())
    n_rows += 1
    in_level = (level == row.units) if row.units != "all units" else pd.Series(True, index=level.index)
    if (n, a, b, c_, dd, int(in_level.sum()), int((in_level & ~okf).sum())) != (row.n_assessed, row.both, row.hansen_only, row.corestack_only, row.neither, row.n_units, row.n_insufficient_forest):
        bad["counts"] += 1
    exp = n * (a + b) / n * (a + c_) / n
    if abs(exp - row.both_expected_if_unrelated) > 0.006 or abs(a / exp - row.both_observed_over_expected) > 6e-4:
        bad["chance"] += 1
    if abs(a * dd / (b * c_) - row.odds_ratio) > 6e-4:
        bad["odds"] += 1
    for k in ("degradation", "degradation_with_partial", "net", "lost", "improvement"):
        if abs(spearmanr(r[sel], rate[k].fillna(0)[sel])[0] - getattr(row, f"spearman_hansen_vs_corestack_{k}")) > 6e-5:
            bad["spearman"] += 1
    tl, th, td = ref[sel].sum(), loss[row.window][sel].sum(), area["degradation"][sel].sum()
    mine = (tl / 100, th / 100, td / 100, 100 * loss[row.window][sel & cf].sum() / th, 100 * ref[sel & cf].sum() / tl, 100 * area["degradation"][sel & hf].sum() / td, 100 * ref[sel & hf].sum() / tl)
    theirs = (row.reference_km2, row.hansen_loss_km2, row.corestack_degradation_km2, row.hansen_loss_pct_in_units_corestack_flags, row.reference_land_pct_in_units_corestack_flags,
              row.corestack_degradation_pct_in_units_hansen_flags, row.reference_land_pct_in_units_hansen_flags)
    if not close(mine, theirs, 0.006):
        bad["areas"] += 1
    if not (row.odds_ratio_lo95 <= row.odds_ratio <= row.odds_ratio_hi95 and row.both_observed_over_expected_lo95 <= row.both_observed_over_expected <= row.both_observed_over_expected_hi95
            and row.spearman_hansen_vs_corestack_degradation_lo95 <= row.spearman_hansen_vs_corestack_degradation <= row.spearman_hansen_vs_corestack_degradation_hi95):
        bad["interval_holds_estimate"] += 1
    if row.delivered or (row.window == "common_2017_2023" and row.minimum_reference_ha == 50):
        idx = np.flatnonzero(sel.to_numpy())
        hfv, cfv = hf.to_numpy()[idx], cf.to_numpy()[idx]
        ors = []
        for _ in range(1000):
            k = rng.integers(0, n, n)
            x, y = hfv[k], cfv[k]
            ors.append((x & y).sum() * (~x & ~y).sum() / max((x & ~y).sum() * (~x & y).sum(), 1))
        lo, hi = np.percentile(ors, [2.5, 97.5])
        width = row.odds_ratio_hi95 - row.odds_ratio_lo95
        if abs(lo - row.odds_ratio_lo95) > 0.25 * width or abs(hi - row.odds_ratio_hi95) > 0.25 * width:
            bad["interval_far_from_ours"] += 1
check(f"summary: n, the four counts and the units below the floor, all {n_rows} rows", bad["counts"] == 0, f"{bad['counts']} rows differ")
check("summary: the number expected if unrelated, and observed over expected", bad["chance"] == 0, f"{bad['chance']} rows differ")
check("summary: the odds ratio", bad["odds"] == 0, f"{bad['odds']} rows differ")
check("summary: the five rank correlations", bad["spearman"] == 0, f"{bad['spearman']} cells differ")
check("summary: the areas and where they lie", bad["areas"] == 0, f"{bad['areas']} rows differ")
check("summary: every interval holds its own estimate", bad["interval_holds_estimate"] == 0, f"{bad['interval_holds_estimate']} rows do not")
check("summary: the delivered rows' odds-ratio intervals are close to an independent bootstrap of 1,000", bad["interval_far_from_ours"] == 0, f"{bad['interval_far_from_ours']} rows are not")
check("summary: exactly three rows are marked delivered (the headline window at the delivered floor, by unit type)", int(s.delivered.sum()) == 3 and set(s[s.delivered == 1].window) == {"common_2017_2023"})

# ---- the other readings of the CoRE Stack flag -------------------------------------------------------------------------------
r = (loss["common_2017_2023"] / ref).where(ref > 0).fillna(0)
hf = ok & (r > np.percentile(r[ok], 80))
wrong = 0
for row in d.itertuples():
    rc = rate[row.corestack_rate].fillna(0)
    cf = ok & (rc > np.percentile(rc[ok], 80))
    sel = ok & ((level == row.units) if row.units != "all units" else True)
    a, b, c_, dd = int((sel & hf & cf).sum()), int((sel & hf & ~cf).sum()), int((sel & ~hf & cf).sum()), int((sel & ~hf & ~cf).sum())
    exp = (a + b) * (a + c_) / int(sel.sum())
    if (a, b, c_, dd) != (row.both, row.hansen_only, row.corestack_only, row.neither) or abs(exp - row.both_expected_if_unrelated) > 0.006 or abs(a * dd / (b * c_) - row.odds_ratio) > 6e-4:
        wrong += 1
check(f"definitions: counts, chance and odds ratio for every reading of the CoRE Stack flag, all {len(d)} rows", wrong == 0, f"{wrong} rows differ")

# ---- one cross-check against the assembled table ---------------------------------------------------------------------------------
g = pd.read_csv(D / "degradation_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
mask_loss = sum(g[f"hansen_loss_ha_{y}"] for y in range(2017, 2024))
band_loss = sum(h[f"loss_ha_gt30_{y}"] for y in range(2017, 2024))
check("the mask's loss 2017-2023 in degradation_by_unit.csv equals the treecover2000 > 30 band's in the canopy-band table, unit by unit", close(mask_loss, band_loss, 2e-3),
      f"{mask_loss.sum() / 100:,.2f} km2 of the {loss['common_2017_2023'].sum() / 100:,.2f} km2 on the reference land")
check("the reference land never holds less loss than the mask inside it", (loss["common_2017_2023"] >= band_loss - 2e-3).all())

print(f"\n{sum(results)} of {len(results)} checks passed; n = {len(u):,} units, {int(ok.sum()):,} assessed")
sys.exit(0 if all(results) else 1)
