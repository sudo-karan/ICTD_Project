#!/usr/bin/env python3
"""
A direct check of the agreement tables' arithmetic. Reads, writes nothing, exits 1 if a check fails.

    python scripts/verify_agreement.py

It imports nothing from scripts/02_build_agreement.py. From the two sources' per-unit tables, and the unit type
and district from stage 0, it rebuilds in plain pandas what the six agreement tables hold, and compares.

WHAT IS REBUILT AND COMPARED, CELL BY CELL
  agreement_by_unit.csv              every column, every unit: land, loss, rates, the zone model, who is assessed (the
                                     floor must be the 100 ha ruled on 7 Oct 2026), who is in the headline population,
                                     the flags and classes of the headline population in three windows and of all
                                     assessed units in the headline window; unit type against 10_units/
  agreement_summary.csv, all rows    for each population, window, floor and unit type: n, the units below the floor,
                                     the units shut out by their zone model, both cuts, the two counts of flagged
                                     units, the four classes, chance, observed over expected, the odds ratio, the odds
                                     ratio within districts, the five rank correlations, the seven area figures, the
                                     districts resampled, the repeatability attached to the floor, and that each row's
                                     label says which window it is; exactly the headline rows marked delivered
  agreement_definitions.csv          the cut, n, flagged units, the four classes, chance, observed over expected, the
                                     odds ratio, the odds ratio within districts and the row's own rank correlation
  agreement_by_zone.csv              every count, share, ratio, median and rank correlation
  agreement_floor_repeatability.csv  every n and rank correlation
  agreement_intervals.csv            the estimates and district intervals (they are the summary's), the numbers of
                                     districts and of units resampled singly, and how many assessed outside-village
                                     units have a district that no check can confirm, was moved, or is ambiguous
  agreement.provenance.json          its counts, its row, column and blank-cell figures, the floor and the headline
                                     population it names, and that the source tables on disk are the ones it used

WHAT IS NOT REBUILT. The bootstrap intervals depend on random draws. Every interval in every table is checked to be
present, in order, and to hold its own estimate; the delivered reading of the definitions table is checked to carry
the summary's intervals; and for the delivered rows the odds-ratio interval of each of the three ways of resampling
(whole districts; districts for the lgd_panchayat units with outside_village units singly; every unit singly) is
checked against an independent bootstrap made here, to within a quarter of its width. An interval moved by less
than that, or widened without losing its estimate, would pass.

WHAT THIS SHARES WITH THE BUILDER. numpy's percentile and scipy's spearmanr, and the design of the bootstrap. A
fault in either library, or in the design, would pass here. A blank cell where a figure belongs fails.

In : 20_degradation/hansen_loss_by_canopy_band_by_unit.csv, corestack_by_unit_bands.csv   (the sources)
     10_units/units_attributes.csv, outside_village_district.csv                           (unit type, district)
     20_degradation/agreement_*.csv, agreement.provenance.json                             (what is checked)
     20_degradation/degradation_by_unit.csv   (one cross-check: the mask's loss in the window, from the other table)
"""
import hashlib, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

R = Path(__file__).resolve().parent.parent
D = R / "20_degradation"
RULED_FLOOR_HA = 100.0                     # the project owner's ruling of 7 Oct 2026; the tables must be built on it
HEADLINE_POPULATION = "east_coast_excluded"
SP = "spearman_hansen_vs_corestack_"
results = []


def check(what, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {what}" + (f"   {detail}" if detail else ""))


def close(a, b, tol):
    """Arrays: equal within tol, and blank in the same places."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(((np.isnan(a) & np.isnan(b)) | (np.abs(a - b) <= tol)).all())


def off(mine, theirs, tol):
    """One figure against the table's: True if they differ, or if either is blank."""
    try:
        mine, theirs = float(mine), float(theirs)
    except (TypeError, ValueError):
        return True
    return bool(np.isnan(mine) or np.isnan(theirs) or abs(mine - theirs) > tol)


def holds(lo, est, hi):
    """An interval that is there, in order, and holds its estimate."""
    try:
        v = np.asarray([lo, est, hi], float)
    except (TypeError, ValueError):
        return False
    return bool(not np.isnan(v).any() and v[0] <= v[1] <= v[2] and v[0] < v[2])


def four(sel, hf, cf):
    return int((sel & hf & cf).sum()), int((sel & hf & ~cf).sum()), int((sel & ~hf & cf).sum()), int((sel & ~hf & ~cf).sum())


def within_districts(idx, hv, cv, dist):
    num = den = 0.0
    for k in set(dist[idx]):
        m = idx[dist[idx] == k]
        a, b, c_, dd = int((hv[m] & cv[m]).sum()), int((hv[m] & ~cv[m]).sum()), int((~hv[m] & cv[m]).sum()), int((~hv[m] & ~cv[m]).sum())
        num += a * dd / len(m); den += b * c_ / len(m)
    return num / den if den else np.nan


def or_interval(idx, hv, cv, dist, out, design, rng, n=1000):
    """An independent bootstrap of the odds ratio under one of the three ways of resampling."""
    grouped = idx if design == "districts" else idx[~out[idx]] if design == "lgd_districts" else idx[:0]
    single = idx[:0] if design == "districts" else idx[out[idx]] if design == "lgd_districts" else idx
    members = [grouped[dist[grouped] == k] for k in sorted(set(dist[grouped]))]
    ors = []
    for _ in range(n):
        parts = [members[i] for i in rng.integers(0, len(members), len(members))] if members else []
        if len(single):
            parts.append(single[rng.integers(0, len(single), len(single))])
        j = np.concatenate(parts)
        x, y = hv[j], cv[j]
        ors.append((x & y).sum() * (~x & ~y).sum() / max((x & ~y).sum() * (~x & y).sum(), 1))
    return np.percentile(ors, [2.5, 97.5])


h = pd.read_csv(D / "hansen_loss_by_canopy_band_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
c = pd.read_csv(D / "corestack_by_unit_bands.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
u = pd.read_csv(D / "agreement_by_unit.csv", dtype={"unit_id": str}, keep_default_na=True).set_index("unit_id").sort_index()
s = pd.read_csv(D / "agreement_summary.csv")
d = pd.read_csv(D / "agreement_definitions.csv")
bz = pd.read_csv(D / "agreement_by_zone.csv")
fr = pd.read_csv(D / "agreement_floor_repeatability.csv")
iv = pd.read_csv(D / "agreement_intervals.csv")
prov = json.load(open(D / "agreement.provenance.json"))
attr = pd.read_csv(R / "10_units" / "units_attributes.csv", dtype=str).set_index("unit_id").sort_index()
odt = pd.read_csv(R / "10_units" / "outside_village_district.csv", dtype=str, keep_default_na=False).set_index("unit_id")
check("the three per-unit tables and the layer hold the same units, each once", h.index.equals(c.index) and h.index.equals(u.index) and u.index.is_unique and u.index.equals(attr.index), f"n = {len(u):,}")
check("unit_level in agreement_by_unit.csv is the layer's own (10_units/units_attributes.csv)", (u.unit_level == attr.unit_level).all())
level = attr.unit_level
out = (level == "outside_village").to_numpy()
district = attr.pc11_district_code.where(level != "outside_village", odt["pc11_district_code"].reindex(attr.index))
check("every unit has one of 30 districts", district.notna().all() and district.nunique() == 30, f"{district.nunique()} districts")
dist = district.to_numpy()
N = len(u)

# ---- the per-unit table: land, loss, rates ---------------------------------------------------------------------------------
ref = h["area_ha_gt10le30"] + h["area_ha_gt30"]
val = sum(c[f"class_{k}_ha_{b}"] for k in ("lost", "degradation", "nochange", "improvement", "gained", "partial3", "partial4") for b in ("gt10le30", "gt30"))
check("reference_ha is the land with treecover2000 > 10 of Hansen's canopy-band table", close(u.reference_ha, ref, 1e-3))
check("corestack_valued_ha is classes -2 to 4 on that land", close(u.corestack_valued_ha, val, 1e-3))
windows = {"common_2017_2023": range(2017, 2024), "between_2019_2022": range(2019, 2023), "full_span_2001_2025": range(2001, 2026)}
HW = "common_2017_2023"
loss = {w: sum(h[f"loss_ha_{b}_{y}"] for b in ("gt10le30", "gt30") for y in years) for w, years in windows.items()}
klass = {"degradation": ["degradation"], "partial_degradation": ["partial3", "partial4"], "lost": ["lost"], "improvement": ["improvement"]}
area = {k: sum(c[f"class_{p}_ha_{b}"] for p in parts for b in ("gt10le30", "gt30")) for k, parts in klass.items()}
bad = sum(not close(u[f"hansen_loss_ha_{w}"], loss[w], 1e-3) or not close(u[f"hansen_rate_{w}"], (loss[w] / ref).where(ref > 0), 2e-6) for w in windows)
check("hansen_loss_ha and hansen_rate, three windows: the yearly loss of those years on that land, over that land", bad == 0, f"{bad} windows differ")
rate = {"degradation": area["degradation"] / val, "degradation_with_partial": (area["degradation"] + area["partial_degradation"]) / val, "net": (area["degradation"] - area["improvement"]) / val,
        "lost": area["lost"] / val, "improvement": area["improvement"] / val}
bad = sum(not close(u[f"corestack_{k}_ha"], area[k], 1e-3) for k in klass) + sum(not close(u[f"corestack_rate_{k}"], r.where(val > 0), 2e-6) for k, r in rate.items())
check("the four CoRE Stack areas and the five rates over corestack_valued_ha", bad == 0, f"{bad} columns differ")
hr = {w: (loss[w] / ref).where(ref > 0).fillna(0) for w in windows}
cr = {k: r.fillna(0) for k, r in rate.items()}

# ---- the floor, the zone models, the populations -------------------------------------------------------------------------------
floor = float(prov["definitions"]["floor"]["minimum_reference_ha"])
check("the floor the tables were built on is the 100 ha ruled on 7 Oct 2026", floor == RULED_FLOOR_HA and prov["definitions"]["headline_population"] == HEADLINE_POPULATION, f"floor {floor:g} ha; headline population {prov['definitions']['headline_population']}")
at = {f: (ref >= f) & (val >= f) for f in (10.0, 50.0, 100.0)}
ok = at[RULED_FLOOR_HA]
check("assessed is at least 100 ha on both grids", (u.assessed == ok.astype(int)).all(), f"{int(ok.sum()):,} assessed, {int((~ok).sum()):,} not")
ze, zc = c["value_ha_zone_EPAHR"], c["value_ha_zone_ECPHR"]
zone = pd.Series(np.where((ze > 0) & (zc == 0), "EPAHR only", np.where((zc > 0) & (ze == 0), "ECPHR only", np.where((ze > 0) & (zc > 0), "both models", "neither"))), index=c.index)
check("corestack_zone_model is the model, or models, a unit's valued land lies under", (u.corestack_zone_model.fillna("") == zone.where(val > 0, "")).all(), str(zone[ok].value_counts().to_dict()))
keep = {"all_assessed": pd.Series(True, index=ref.index), "east_coast_excluded": zone != "ECPHR only", "eastern_plateau_only": zone == "EPAHR only"}
check("in_headline_population is assessed and not wholly under the East Coast model", (u.in_headline_population == (ok & keep[HEADLINE_POPULATION]).astype(int)).all(), f"{int((ok & keep[HEADLINE_POPULATION]).sum()):,} units")


def flagged(pop, w, f, name="degradation"):
    """The population's assessed units, both cuts and both flags."""
    okp = at[f] & keep[pop]
    ch, cc = np.percentile(hr[w][okp], 80), np.percentile(cr[name][okp], 80)
    return okp, ch, cc, okp & (hr[w] > ch), okp & (cr[name] > cc)


def klasses(okp, hf, cf):
    return np.where(~ok, "insufficient_forest", np.where(~okp, "zone_model_excluded", np.where(hf & cf, "both", np.where(hf, "hansen_only", np.where(cf, "corestack_only", "neither")))))


wrong = []
for w in windows:
    okp, ch, cc, hf, cf = flagged(HEADLINE_POPULATION, w, RULED_FLOOR_HA)
    cls_col, flag_col = ("agreement_class", "hansen_flag") if w == HW else (f"agreement_class_{w}", f"hansen_flag_{w}")
    if not (u[cls_col].to_numpy() == klasses(okp, hf, cf)).all():
        wrong.append(cls_col)
    if not (u[flag_col].fillna(-1).astype(int) == np.where(okp, hf.astype(int), -1)).all():
        wrong.append(flag_col)
    if w == HW and not (u["corestack_flag"].fillna(-1).astype(int) == np.where(okp, cf.astype(int), -1)).all():
        wrong.append("corestack_flag")
    rec = prov["definitions"]["cuts_at_the_delivered_floor"][f"{HEADLINE_POPULATION}__{w}"]
    if off(ch, rec["hansen"], 2e-6) or off(cc, rec["corestack_degradation"], 2e-6):
        wrong.append(f"recorded cuts, {w}")
check("the headline population's flags and classes in three windows follow from its own 80th-percentile cuts, and the record holds those cuts", not wrong, f"differ: {wrong}" if wrong else str(pd.Series(u.agreement_class).value_counts().to_dict()))
okp, ch, cc, hf, cf = flagged("all_assessed", HW, RULED_FLOOR_HA)
check("agreement_class_all_assessed and its two flags follow from the cuts over every assessed unit",
      (u.agreement_class_all_assessed.to_numpy() == klasses(okp, hf, cf)).all() and (u.hansen_flag_all_assessed.fillna(-1).astype(int) == np.where(okp, hf.astype(int), -1)).all()
      and (u.corestack_flag_all_assessed.fillna(-1).astype(int) == np.where(okp, cf.astype(int), -1)).all(), str(pd.Series(u.agreement_class_all_assessed).value_counts().to_dict()))

# ---- the minimum forest, on the reference land -----------------------------------------------------------------------------------
wrong = 0
for row in fr.itertuples():
    lo_y, hi_y = (int(x) for x in row.hansen_loss_years.split("-"))
    odd, even = (sum(h[f"loss_ha_{b}_{y}"] for b in ("gt10le30", "gt30") for y in range(lo_y, hi_y + 1) if y % 2 == k) for k in (1, 0))
    sel = (ref >= row.reference_ha_from) & ((ref < row.reference_ha_below) if not np.isnan(row.reference_ha_below) else True)
    wrong += int(sel.sum()) != row.n_units or int(((odd + even)[sel] == 0).sum()) != row.units_with_no_loss_in_those_years or off(spearmanr(odd[sel] / ref[sel], even[sel] / ref[sel])[0], row.odd_years_vs_even_years_spearman, 6e-4)
check(f"repeatability on the reference land: n, units without loss and the odd-against-even rank correlation, {len(fr)} rows", wrong == 0 and len(fr) == 14, f"{wrong} rows differ")
rep = fr.set_index(["reference_ha_from", "hansen_loss_years"])["odd_years_vs_even_years_spearman"]

# ---- the summary, row by row -----------------------------------------------------------------------------------------------------
rng = np.random.default_rng(1)
LABEL = {"common_2017_2023": "HEADLINE", "between_2019_2022": "sensitivity", "full_span_2001_2025": "NOT ONE PERIOD"}
RATED = ("degradation", "net", "lost", "improvement")
FAMILIES = ["odds_ratio", "both_observed_over_expected", "odds_ratio_within_districts"] + [SP + k for k in RATED]
bad = dict.fromkeys(("counts", "cuts_and_flagged", "label", "chance", "odds", "within", "spearman", "areas", "repeatability", "interval", "interval_far_from_ours"), 0)
n_rows = 0
for row in s.itertuples():
    f, w, pop = row.minimum_reference_ha, row.window, row.population
    okf, cut_h, cut_d, hf, cf = flagged(pop, w, f)
    in_level = (level == row.units) if row.units != "all units" else pd.Series(True, index=level.index)
    sel = okf & in_level
    n = int(sel.sum())
    a, b, c_, dd = four(sel, hf, cf)
    n_rows += 1
    if (n, a, b, c_, dd, int(in_level.sum()), int((in_level & ~at[f]).sum()), int((in_level & at[f] & ~keep[pop]).sum())) != (row.n_assessed, row.both, row.hansen_only, row.corestack_only, row.neither, row.n_units, row.n_insufficient_forest,
                                                                                                                                  row.n_excluded_by_zone_model):
        bad["counts"] += 1
    if off(cut_h, row.hansen_rate_cut, 2e-6) or off(cut_d, row.corestack_degradation_rate_cut, 2e-6) or off(a + b, row.flagged_by_hansen, 0) or off(a + c_, row.flagged_by_corestack, 0):
        bad["cuts_and_flagged"] += 1
    if not str(row.window_is).startswith(LABEL[w]) or (row.delivered == 1) != (pop == HEADLINE_POPULATION and w == HW and f == RULED_FLOOR_HA):
        bad["label"] += 1
    exp = (a + b) * (a + c_) / n
    if off(exp, row.both_expected_if_unrelated, 0.006) or off(a / exp, row.both_observed_over_expected, 6e-4):
        bad["chance"] += 1
    if off(a * dd / (b * c_), row.odds_ratio, 6e-4):
        bad["odds"] += 1
    idx = np.flatnonzero(sel.to_numpy())
    hv, cv = hf.to_numpy(), cf.to_numpy()
    if off(within_districts(idx, hv, cv, dist), row.odds_ratio_within_districts, 6e-4) or len(set(dist[idx])) != row.n_districts:
        bad["within"] += 1
    for k in ("degradation", "degradation_with_partial", "net", "lost", "improvement"):
        if off(spearmanr(hr[w][sel], cr[k][sel])[0], getattr(row, SP + k), 6e-5):
            bad["spearman"] += 1
    tl, th, td = ref[sel].sum(), loss[w][sel].sum(), area["degradation"][sel].sum()
    mine = (tl / 100, th / 100, td / 100, 100 * loss[w][sel & cf].sum() / th, 100 * ref[sel & cf].sum() / tl, 100 * area["degradation"][sel & hf].sum() / td, 100 * ref[sel & hf].sum() / tl)
    theirs = (row.reference_km2, row.hansen_loss_km2, row.corestack_degradation_km2, row.hansen_loss_pct_in_units_corestack_flags, row.reference_land_pct_in_units_corestack_flags,
              row.corestack_degradation_pct_in_units_hansen_flags, row.reference_land_pct_in_units_hansen_flags)
    if any(off(m_, t_, 0.006) for m_, t_ in zip(mine, theirs)):
        bad["areas"] += 1
    if off(rep[(f, "2001-2025")], row.repeatability_of_that_class_2001_2025, 0) or off(rep[(f, "2017-2023")], row.repeatability_of_that_class_2017_2023, 0) or not str(row.lowest_land_class_admitted_ha).startswith(f"{f:g} to "):
        bad["repeatability"] += 1
    bad["interval"] += sum(not holds(getattr(row, f"{k}_lo95"), getattr(row, k), getattr(row, f"{k}_hi95")) for k in FAMILIES)
    if w == HW and f == RULED_FLOOR_HA and pop != "eastern_plateau_only":
        lo, hi = or_interval(idx, hv, cv, dist, out, "districts", rng)
        width = row.odds_ratio_hi95 - row.odds_ratio_lo95
        if off(lo, row.odds_ratio_lo95, 0.25 * width) or off(hi, row.odds_ratio_hi95, 0.25 * width):
            bad["interval_far_from_ours"] += 1
check(f"summary: n, the four counts, the units below the floor and those shut out by their zone model, all {n_rows} rows", bad["counts"] == 0, f"{bad['counts']} rows differ")
check("summary: both cuts and the two counts of flagged units, all rows", bad["cuts_and_flagged"] == 0, f"{bad['cuts_and_flagged']} rows differ")
check("summary: each row's label names its window; only the headline population, window and floor are marked delivered", bad["label"] == 0 and int(s.delivered.sum()) == 3, f"{bad['label']} rows differ")
check("summary: the number expected if unrelated, and observed over expected", bad["chance"] == 0, f"{bad['chance']} rows differ")
check("summary: the odds ratio", bad["odds"] == 0, f"{bad['odds']} rows differ")
check("summary: the odds ratio within districts, and the number of districts resampled", bad["within"] == 0, f"{bad['within']} rows differ")
check("summary: the five rank correlations", bad["spearman"] == 0, f"{bad['spearman']} cells differ")
check("summary: the areas and where they lie", bad["areas"] == 0, f"{bad['areas']} rows differ")
check("summary: each floor carries the repeatability of the lowest class of land it lets in, as the repeatability table has it", bad["repeatability"] == 0, f"{bad['repeatability']} rows differ")
check(f"summary: all {len(FAMILIES) * n_rows} intervals are there, in order, and hold their estimates", bad["interval"] == 0, f"{bad['interval']} do not")
check("summary: the odds-ratio intervals of the six rows at the headline window and floor are close to an independent bootstrap of whole districts", bad["interval_far_from_ours"] == 0, f"{bad['interval_far_from_ours']} rows are not")
check("summary: the populations add up - assessed units of all, less those shut out, are the headline population's", all(
    int(s[(s.population == "all_assessed") & (s.window == w) & (s.minimum_reference_ha == f) & (s.units == "all units")].n_assessed.iloc[0])
    == int(x.n_assessed) + int(x.n_excluded_by_zone_model) for (w, f), g in s[(s.population == HEADLINE_POPULATION) & (s.units == "all units")].groupby(["window", "minimum_reference_ha"]) for x in g.itertuples()))
head = {pop: s[(s.population == pop) & (s.window == HW) & (s.minimum_reference_ha == RULED_FLOOR_HA)].set_index("units") for pop in keep}

# ---- the other readings of the CoRE Stack flag -----------------------------------------------------------------------------------
wrong = wrong_interval = copied = 0
for row in d.itertuples():
    okp, _, cut, hf, cf = flagged(row.population, HW, RULED_FLOOR_HA, row.corestack_rate)
    sel = okp & ((level == row.units) if row.units != "all units" else True)
    n = int(sel.sum())
    a, b, c_, dd = four(sel, hf, cf)
    exp = (a + b) * (a + c_) / n
    own = SP + row.corestack_rate
    idx = np.flatnonzero(sel.to_numpy())
    if ((a, b, c_, dd, n) != (row.both, row.hansen_only, row.corestack_only, row.neither, row.n_assessed) or off(cut, row.corestack_rate_cut, 2e-6) or off(a + b, row.flagged_by_hansen, 0)
            or off(a + c_, row.flagged_by_corestack, 0) or off(exp, row.both_expected_if_unrelated, 0.006) or off(a / exp, row.both_observed_over_expected, 6e-4) or off(a * dd / (b * c_), row.odds_ratio, 6e-4)
            or off(within_districts(idx, hf.to_numpy(), cf.to_numpy(), dist), row.odds_ratio_within_districts, 6e-4) or off(spearmanr(hr[HW][sel], cr[row.corestack_rate][sel])[0], getattr(row, own), 6e-5)):
        wrong += 1
    fams = ["odds_ratio", "both_observed_over_expected", "odds_ratio_within_districts"] + ([own] if row.corestack_rate != "degradation_with_partial" else [])
    wrong_interval += sum(not holds(getattr(row, f"{k}_lo95"), getattr(row, k), getattr(row, f"{k}_hi95")) for k in fams)
    if row.corestack_rate == "degradation":
        copied += sum(off(getattr(row, f"{k}_{e}"), head[row.population].loc[row.units, f"{k}_{e}"], 0) for k in ("odds_ratio", "both_observed_over_expected", own) for e in ("lo95", "hi95"))
check(f"definitions: the cut, n, flagged units, the four counts, chance, the two odds ratios and the rate's own rank correlation, all {len(d)} rows", wrong == 0 and len(d) == 30, f"{wrong} rows differ")
check("definitions: every interval is there, in order, and holds its estimate", wrong_interval == 0, f"{wrong_interval} do not")
check("definitions: the delivered reading carries the summary's intervals, not a second draw", copied == 0, f"{copied} bounds differ")

# ---- the zone models one at a time ----------------------------------------------------------------------------------------------------
oka, _, _, hfa, cfa = flagged("all_assessed", HW, RULED_FLOOR_HA)
pflag = oka & (cr["improvement"] > np.percentile(cr["improvement"][oka], 80))
wrong = wrong_interval = 0
for row in bz.itertuples():
    sel = oka & (zone == row.zone_model_of_the_units_valued_land)
    n = int(sel.sum())
    mine = {"n_assessed": n, "n_lgd_panchayat": int((sel & ~out).sum()), "n_outside_village": int((sel & out).sum()), "n_districts": len(set(dist[sel.to_numpy()])),
            "in_the_headline_population": int(row.zone_model_of_the_units_valued_land != "ECPHR only"), "assessed_units_pct": 100 * n / int(oka.sum()),
            "reference_land_pct_of_assessed": 100 * ref[sel].sum() / ref[oka].sum(), "hansen_loss_pct_of_assessed": 100 * loss[HW][sel].sum() / loss[HW][oka].sum(),
            "corestack_degradation_pct_of_assessed": 100 * area["degradation"][sel].sum() / area["degradation"][oka].sum(),
            "flagged_by_hansen": int((sel & hfa).sum()), "flagged_by_hansen_pct": 100 * (sel & hfa).sum() / n, "median_corestack_degradation_rate": cr["degradation"][sel].median(),
            "median_corestack_improvement_rate": cr["improvement"][sel].median(), SP + "degradation": spearmanr(hr[HW][sel], cr["degradation"][sel])[0], SP + "improvement": spearmanr(hr[HW][sel], cr["improvement"][sel])[0]}
    tol = {"assessed_units_pct": 0.006, "reference_land_pct_of_assessed": 0.006, "hansen_loss_pct_of_assessed": 0.006, "corestack_degradation_pct_of_assessed": 0.006, "flagged_by_hansen_pct": 0.06,
           "median_corestack_degradation_rate": 6e-5, "median_corestack_improvement_rate": 6e-5, SP + "degradation": 6e-5, SP + "improvement": 6e-5}
    for tag, cf in (("degradation", cfa), ("improvement_the_placebo", pflag)):
        a, b, c_, dd = four(sel, hfa, cf)
        exp = (a + b) * (a + c_) / n
        mine.update({f"flagged_on_{tag}": a + c_, f"both_{tag}": a, f"both_{tag}_expected_if_unrelated": exp, f"both_{tag}_observed_over_expected": a / exp, f"odds_ratio_{tag}": a * dd / (b * c_)})
        tol.update({f"both_{tag}_expected_if_unrelated": 0.006, f"both_{tag}_observed_over_expected": 6e-4, f"odds_ratio_{tag}": 6e-4})
    wrong += sum(off(v, getattr(row, k), tol.get(k, 0)) for k, v in mine.items())
    wrong_interval += sum(not holds(getattr(row, f"{SP}{k}_lo95{e}"), getattr(row, SP + k), getattr(row, f"{SP}{k}_hi95{e}")) for k in ("degradation", "improvement") for e in ("", "_units_singly"))
check(f"by zone model: every count, share, ratio, median and rank correlation, {len(bz)} rows", wrong == 0 and len(bz) == 3, f"{wrong} cells differ")
check("by zone model: the three groups hold every assessed unit once, and both kinds of interval hold their estimates", int(bz.n_assessed.sum()) == int(oka.sum()) and wrong_interval == 0, f"{wrong_interval} intervals do not")

# ---- the intervals three ways -------------------------------------------------------------------------------------------------------------
cover, nbrs = pd.to_numeric(odt["area_cover_share"], errors="coerce").reindex(attr.index).to_numpy(float), pd.to_numeric(odt["neighbours_n_districts"], errors="coerce").reindex(attr.index).to_numpy(float)
o = odt.reindex(attr.index).fillna("")
quality = {"outside_village_assessed_district_has_no_possible_check": out & ~(cover >= 0.5) & ~(nbrs > 0), "outside_village_assessed_moved_off_the_polygons_name": out & (o["assigned_by"] == "two checks against the label").to_numpy(),
           "outside_village_assessed_polygon_has_no_name": out & o["assigned_by"].str.endswith("has no district name").to_numpy(), "outside_village_assessed_ambiguous": out & (o["ambiguous"] == "1").to_numpy(),
           "outside_village_assessed_one_check_contradicts_the_district": out & ((o["area_majority_agrees_with_assigned"] == "0") | ((o["label_absent_from_collar"] == "1") & (o["assigned_by"] == "label"))).to_numpy()}
check("the outside-village districts that no check can confirm, were moved or are ambiguous, in all: as the record has them",
      {k: int(v.sum()) for k, v in quality.items()} == {"outside_village_assessed_" + k: v for k, v in {"district_has_no_possible_check": prov["counts"]["outside_village_units_district"]["no_possible_check"],
       "moved_off_the_polygons_name": prov["counts"]["outside_village_units_district"]["moved_off_the_polygons_name"], "polygon_has_no_name": prov["counts"]["outside_village_units_district"]["polygon_has_no_name"],
       "ambiguous": prov["counts"]["outside_village_units_district"]["ambiguous"], "one_check_contradicts_the_district": prov["counts"]["outside_village_units_district"]["one_check_contradicts_the_district"]}.items()},
      str({k.replace("outside_village_assessed_", ""): int(v.sum()) for k, v in quality.items()}))
wrong = wrong_interval = far = 0
for (pop, units_label), part in iv.groupby(["population", "units"]):
    okp, _, _, hf, cf = flagged(pop, HW, RULED_FLOOR_HA)
    sel = (okp & ((level == units_label) if units_label != "all units" else True)).to_numpy()
    idx = np.flatnonzero(sel)
    hv, cv = hf.to_numpy(), cf.to_numpy()
    lgd_districts = len(set(dist[idx[~out[idx]]]))
    for row in part.itertuples():
        wrong += (row.n_assessed, row.n_lgd_panchayat, row.n_outside_village, row.districts_resampled_primary, row.districts_resampled_lgd_only_design, row.units_resampled_singly_lgd_only_design, row.delivered) != (
            len(idx), int((sel & ~out).sum()), int((sel & out).sum()), len(set(dist[idx])), lgd_districts, int((sel & out).sum()), int(pop == HEADLINE_POPULATION))
        wrong += sum(off(int((sel & q).sum()), getattr(row, k), 0) for k, q in quality.items())
        if row.statistic == "odds_ratio_within_districts_mantel_haenszel":
            sr = head[pop].loc[units_label]
            wrong += off(row.estimate, sr.odds_ratio_within_districts, 0) + off(row.lo95_districts, sr.odds_ratio_within_districts_lo95, 0) + off(row.hi95_districts, sr.odds_ratio_within_districts_hi95, 0)
            continue
        sr = head[pop].loc[units_label]
        wrong += off(row.estimate, sr[row.statistic], 0) + off(row.lo95_districts, sr[f"{row.statistic}_lo95"], 0) + off(row.hi95_districts, sr[f"{row.statistic}_hi95"], 0)
        wrong_interval += (not holds(row.lo95_lgd_districts_outside_singly, row.estimate, row.hi95_lgd_districts_outside_singly)) + (not holds(row.lo95_units_singly, row.estimate, row.hi95_units_singly))
        if row.statistic == "odds_ratio":
            for design, lo_t, hi_t in (("lgd_districts", row.lo95_lgd_districts_outside_singly, row.hi95_lgd_districts_outside_singly), ("units_singly", row.lo95_units_singly, row.hi95_units_singly)):
                lo, hi = or_interval(idx, hv, cv, dist, out, design, rng)
                far += off(lo, lo_t, 0.25 * (hi_t - lo_t)) or off(hi, hi_t, 0.25 * (hi_t - lo_t))
check(f"three ways: n, the districts and single units resampled, the outside-village district counts, the estimates and district intervals (the summary's), {len(iv)} rows", wrong == 0 and len(iv) == 42, f"{wrong} cells differ")
check("three ways: every interval of the other two designs is there, in order, and holds its estimate", wrong_interval == 0, f"{wrong_interval} do not")
check("three ways: the odds-ratio intervals of the other two designs are close to independent bootstraps made here", far == 0, f"{far} are not")

# ---- the record -------------------------------------------------------------------------------------------------------------------------------
tables = {"agreement_by_unit.csv": u.reset_index(), "agreement_summary.csv": s, "agreement_definitions.csv": d, "agreement_intervals.csv": iv, "agreement_by_zone.csv": bz, "agreement_floor_repeatability.csv": fr}
wrong = sum(prov["tables"].get(name, {}).get("rows") != len(t) or prov["tables"][name].get("columns") != len(t.columns) or prov["tables"][name].get("blank_cells") != {k: int(v) for k, v in t.isna().sum().items() if v}
            for name, t in tables.items())
check("the record's rows, columns and blank cells are the six files'", wrong == 0 and set(prov["tables"]) == set(tables), f"{wrong} tables differ")
count = lambda col: {lab: u.loc[(u.unit_level == lab) if lab != "all units" else slice(None), col].value_counts().to_dict() for lab in ("all units", "lgd_panchayat", "outside_village")}
pc = prov.get("counts", {})
check("the record's counts are the per-unit table's", pc.get("units") == N and pc.get("assessed") == int(ok.sum()) and pc.get("in_the_headline_population") == int((ok & keep[HEADLINE_POPULATION]).sum())
      and pc.get("by_level") == count("agreement_class") and pc.get("by_level_all_assessed") == count("agreement_class_all_assessed"))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
stale = [i["path"] for i in prov["inputs"] if i["path"].endswith(".csv") and sha(R / i["path"]) != i["sha256"]]
check("the source tables on disk are the ones the record says the tables were built from", not stale and prov["definitions"]["headline_window"] == HW, f"changed since: {stale}" if stale else "")
check("the table this one replaced is gone", not (D / "agreement_intervals_by_district.csv").exists())

# ---- one cross-check against the assembled table ---------------------------------------------------------------------------------
g = pd.read_csv(D / "degradation_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
mask_loss = sum(g[f"hansen_loss_ha_{y}"] for y in range(2017, 2024))
band_loss = sum(h[f"loss_ha_gt30_{y}"] for y in range(2017, 2024))
check("the mask's loss 2017-2023 in degradation_by_unit.csv equals the treecover2000 > 30 band's in the canopy-band table, unit by unit", close(mask_loss, band_loss, 2e-3),
      f"{mask_loss.sum() / 100:,.2f} km2 of the {loss[HW].sum() / 100:,.2f} km2 on the reference land")
check("in agreement_by_unit.csv no unit's loss on the reference land is less than the mask's loss in degradation_by_unit.csv", (u.hansen_loss_ha_common_2017_2023 >= mask_loss - 2e-3).all())

H = head[HEADLINE_POPULATION].loc["all units"]
print(f"\n{sum(results)} of {len(results)} checks passed; n = {N:,} units, {int(ok.sum()):,} assessed at {RULED_FLOOR_HA:g} ha, {int(H.n_assessed):,} in the headline population")
sys.exit(0 if all(results) else 1)
