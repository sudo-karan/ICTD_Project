#!/usr/bin/env python3
"""
A direct check of the agreement tables' arithmetic. Reads, writes nothing, exits 1 if a check fails.

    python scripts/verify_agreement.py

It imports nothing from scripts/02_build_agreement.py. From the two sources' per-unit tables, and the unit type
and district from stage 0, it rebuilds in plain pandas what the six agreement tables hold, and compares.

WHAT IS REBUILT AND COMPARED, CELL BY CELL
  agreement_by_unit.csv                  every column, every unit; the unit type against 10_units/units_attributes.csv
  agreement_summary.csv, all rows        n, the units below the floor, both cuts, the two counts of flagged units, the
                                         four classes, the number chance would give, observed over expected, the odds
                                         ratio, the five rank correlations, the seven area figures, and that each row's
                                         label says which window it is
  agreement_definitions.csv, all rows    the cut, n, the two counts of flagged units, the four classes, chance,
                                         observed over expected, the odds ratio and the row's own rank correlation
  agreement_by_zone.csv                  every count, ratio, median and rank correlation
  agreement_floor_repeatability.csv      every n and rank correlation
  agreement_intervals_by_district.csv    the estimates, the single-unit intervals (they are the summary's), and the
                                         odds ratio within districts
  agreement.provenance.json              its counts and its row, column and blank-cell figures against the files, and
                                         that the two source tables on disk are the ones it was built from

WHAT IS NOT REBUILT. The bootstrap intervals depend on random draws. Every interval in every table is checked to be
present, in order, and to hold its own estimate; the delivered rows of the definitions table are checked to carry
the summary's intervals; and the odds-ratio intervals of the three delivered rows - units resampled singly, and
whole districts resampled - are checked against an independent bootstrap made here (within a quarter of their
width). The other intervals are not re-derived.

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
    v = np.asarray([lo, est, hi], float)
    return bool(not np.isnan(v).any() and v[0] <= v[1] <= v[2] and v[0] < v[2])


def four(sel, hf, cf):
    return int((sel & hf & cf).sum()), int((sel & hf & ~cf).sum()), int((sel & ~hf & cf).sum()), int((sel & ~hf & ~cf).sum())


h = pd.read_csv(D / "hansen_loss_by_canopy_band_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
c = pd.read_csv(D / "corestack_by_unit_bands.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
u = pd.read_csv(D / "agreement_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
s = pd.read_csv(D / "agreement_summary.csv")
d = pd.read_csv(D / "agreement_definitions.csv")
bz = pd.read_csv(D / "agreement_by_zone.csv")
fr = pd.read_csv(D / "agreement_floor_repeatability.csv")
bd = pd.read_csv(D / "agreement_intervals_by_district.csv")
prov = json.load(open(D / "agreement.provenance.json"))
attr = pd.read_csv(R / "10_units" / "units_attributes.csv", dtype=str).set_index("unit_id").sort_index()
outside = pd.read_csv(R / "10_units" / "outside_village_district.csv", dtype=str).set_index("unit_id")["pc11_district_code"]
check("the three per-unit tables and the layer hold the same units, each once", h.index.equals(c.index) and h.index.equals(u.index) and u.index.is_unique and u.index.equals(attr.index), f"n = {len(u):,}")
check("unit_level in agreement_by_unit.csv is the layer's own (10_units/units_attributes.csv)", (u.unit_level == attr.unit_level).all())
level = attr.unit_level
district = attr.pc11_district_code.where(level != "outside_village", outside.reindex(attr.index))
check("every unit has one of 30 districts", district.notna().all() and district.nunique() == 30, f"{district.nunique()} districts")

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
check("the cut recorded for CoRE Stack is that percentile", not off(cut_c, prov["definitions"]["cuts_at_the_delivered_floor"]["corestack_degradation"], 2e-6))
flags = {}
for w in windows:
    r = (loss[w] / ref).where(ref > 0).fillna(0)
    cut = np.percentile(r[ok], 80)
    flags[w] = ok & (r > cut)
    check(f"hansen_flag_{w} is the rate above its 80th percentile among assessed units", (u[f"hansen_flag_{w}"].fillna(-1).astype(int) == np.where(ok, flags[w].astype(int), -1)).all(), f"cut {cut:.6f}; {int(flags[w].sum())} flagged")
    check(f"the cut recorded for Hansen, {w}", not off(cut, prov["definitions"]["cuts_at_the_delivered_floor"][f"hansen_{w}"], 2e-6))
    mine = np.where(~ok, "insufficient_forest", np.where(flags[w] & cflag, "both", np.where(flags[w], "hansen_only", np.where(cflag, "corestack_only", "neither"))))
    col = "agreement_class" if w == "common_2017_2023" else f"agreement_class_{w}"
    check(f"{col} follows from the two flags", (u[col].to_numpy() == mine).all(), str(pd.Series(mine).value_counts().to_dict()))

# ---- the summary, row by row -----------------------------------------------------------------------------------------------
rng = np.random.default_rng(1)
LABEL = {"common_2017_2023": "HEADLINE", "between_2019_2022": "sensitivity", "full_span_2001_2025": "NOT ONE PERIOD"}
FAMILIES = ["odds_ratio", "both_observed_over_expected"] + [f"spearman_hansen_vs_corestack_{k}" for k in ("degradation", "net", "lost", "improvement")]
bad = dict.fromkeys(("counts", "cuts_and_flagged", "label", "chance", "odds", "spearman", "areas", "interval", "interval_far_from_ours"), 0)
n_rows = 0
for row in s.itertuples():
    f = row.minimum_reference_ha
    okf = (ref >= f) & (val >= f)
    r = (loss[row.window] / ref).where(ref > 0).fillna(0)
    cut_h = np.percentile(r[okf], 80)
    hf = okf & (r > cut_h)
    rc = rate["degradation"].fillna(0)
    cut_d = np.percentile(rc[okf], 80)
    cf = okf & (rc > cut_d)
    in_level = (level == row.units) if row.units != "all units" else pd.Series(True, index=level.index)
    sel = okf & in_level
    n = int(sel.sum())
    a, b, c_, dd = four(sel, hf, cf)
    n_rows += 1
    if (n, a, b, c_, dd, int(in_level.sum()), int((in_level & ~okf).sum())) != (row.n_assessed, row.both, row.hansen_only, row.corestack_only, row.neither, row.n_units, row.n_insufficient_forest):
        bad["counts"] += 1
    if off(cut_h, row.hansen_rate_cut, 2e-6) or off(cut_d, row.corestack_degradation_rate_cut, 2e-6) or off(a + b, row.flagged_by_hansen, 0) or off(a + c_, row.flagged_by_corestack, 0):
        bad["cuts_and_flagged"] += 1
    if not str(row.window_is).startswith(LABEL[row.window]) or (row.delivered == 1) != (row.window == "common_2017_2023" and f == 50):
        bad["label"] += 1
    exp = (a + b) * (a + c_) / n
    if off(exp, row.both_expected_if_unrelated, 0.006) or off(a / exp, row.both_observed_over_expected, 6e-4):
        bad["chance"] += 1
    if off(a * dd / (b * c_), row.odds_ratio, 6e-4):
        bad["odds"] += 1
    for k in ("degradation", "degradation_with_partial", "net", "lost", "improvement"):
        if off(spearmanr(r[sel], rate[k].fillna(0)[sel])[0], getattr(row, f"spearman_hansen_vs_corestack_{k}"), 6e-5):
            bad["spearman"] += 1
    tl, th, td = ref[sel].sum(), loss[row.window][sel].sum(), area["degradation"][sel].sum()
    mine = (tl / 100, th / 100, td / 100, 100 * loss[row.window][sel & cf].sum() / th, 100 * ref[sel & cf].sum() / tl, 100 * area["degradation"][sel & hf].sum() / td, 100 * ref[sel & hf].sum() / tl)
    theirs = (row.reference_km2, row.hansen_loss_km2, row.corestack_degradation_km2, row.hansen_loss_pct_in_units_corestack_flags, row.reference_land_pct_in_units_corestack_flags,
              row.corestack_degradation_pct_in_units_hansen_flags, row.reference_land_pct_in_units_hansen_flags)
    if any(off(m_, t_, 0.006) for m_, t_ in zip(mine, theirs)):
        bad["areas"] += 1
    bad["interval"] += sum(not holds(getattr(row, f"{k}_lo95"), getattr(row, k), getattr(row, f"{k}_hi95")) for k in FAMILIES)
    if row.delivered:
        idx = np.flatnonzero(sel.to_numpy())
        hfv, cfv = hf.to_numpy()[idx], cf.to_numpy()[idx]
        ors = []
        for _ in range(1000):
            k = rng.integers(0, n, n)
            x, y = hfv[k], cfv[k]
            ors.append((x & y).sum() * (~x & ~y).sum() / max((x & ~y).sum() * (~x & y).sum(), 1))
        lo, hi = np.percentile(ors, [2.5, 97.5])
        width = row.odds_ratio_hi95 - row.odds_ratio_lo95
        if off(lo, row.odds_ratio_lo95, 0.25 * width) or off(hi, row.odds_ratio_hi95, 0.25 * width):
            bad["interval_far_from_ours"] += 1
check(f"summary: n, the four counts and the units below the floor, all {n_rows} rows", bad["counts"] == 0, f"{bad['counts']} rows differ")
check("summary: both cuts and the two counts of flagged units, all rows", bad["cuts_and_flagged"] == 0, f"{bad['cuts_and_flagged']} rows differ")
check("summary: each row's label names its window, and only the headline window at 50 ha is marked delivered", bad["label"] == 0 and int(s.delivered.sum()) == 3, f"{bad['label']} rows differ")
check("summary: the number expected if unrelated, and observed over expected", bad["chance"] == 0, f"{bad['chance']} rows differ")
check("summary: the odds ratio", bad["odds"] == 0, f"{bad['odds']} rows differ")
check("summary: the five rank correlations", bad["spearman"] == 0, f"{bad['spearman']} cells differ")
check("summary: the areas and where they lie", bad["areas"] == 0, f"{bad['areas']} rows differ")
check(f"summary: all {len(FAMILIES) * n_rows} intervals are there, in order, and hold their estimates", bad["interval"] == 0, f"{bad['interval']} do not")
check("summary: the delivered rows' odds-ratio intervals are close to an independent bootstrap of 1,000", bad["interval_far_from_ours"] == 0, f"{bad['interval_far_from_ours']} rows are not")

# ---- the other readings of the CoRE Stack flag -------------------------------------------------------------------------------
r = (loss["common_2017_2023"] / ref).where(ref > 0).fillna(0)
hf = ok & (r > np.percentile(r[ok], 80))
wrong = wrong_interval = copied = 0
head = s[s.delivered == 1].set_index("units")
for row in d.itertuples():
    rc = rate[row.corestack_rate].fillna(0)
    cut = np.percentile(rc[ok], 80)
    cf = ok & (rc > cut)
    sel = ok & ((level == row.units) if row.units != "all units" else True)
    n = int(sel.sum())
    a, b, c_, dd = four(sel, hf, cf)
    exp = (a + b) * (a + c_) / n
    own = f"spearman_hansen_vs_corestack_{row.corestack_rate}"
    if ((a, b, c_, dd, n) != (row.both, row.hansen_only, row.corestack_only, row.neither, row.n_assessed) or off(cut, row.corestack_rate_cut, 2e-6) or off(a + b, row.flagged_by_hansen, 0)
            or off(a + c_, row.flagged_by_corestack, 0) or off(exp, row.both_expected_if_unrelated, 0.006) or off(a / exp, row.both_observed_over_expected, 6e-4) or off(a * dd / (b * c_), row.odds_ratio, 6e-4)
            or off(spearmanr(r[sel], rc[sel])[0], getattr(row, own), 6e-5)):
        wrong += 1
    fams = ["odds_ratio", "both_observed_over_expected"] + ([own] if row.corestack_rate != "degradation_with_partial" else [])
    wrong_interval += sum(not holds(getattr(row, f"{k}_lo95"), getattr(row, k), getattr(row, f"{k}_hi95")) for k in fams)
    if row.corestack_rate == "degradation":
        copied += sum(off(getattr(row, f"{k}_{e}"), head.loc[row.units, f"{k}_{e}"], 0) for k in fams for e in ("lo95", "hi95"))
check(f"definitions: the cut, n, flagged units, the four counts, chance, observed over expected, the odds ratio and the rate's own rank correlation, all {len(d)} rows", wrong == 0, f"{wrong} rows differ")
check("definitions: every interval is there, in order, and holds its estimate", wrong_interval == 0, f"{wrong_interval} do not")
check("definitions: the delivered reading carries the summary's intervals, not a second draw", copied == 0, f"{copied} bounds differ")

# ---- the headline inside each zone model ------------------------------------------------------------------------------------
ze, zc = c["value_ha_zone_EPAHR"], c["value_ha_zone_ECPHR"]
zone = {"EPAHR only": (ze > 0) & (zc == 0), "ECPHR only": (zc > 0) & (ze == 0), "both models": (ze > 0) & (zc > 0)}
ri = rate["improvement"].fillna(0)
rdeg = rate["degradation"].fillna(0)
pflag = ok & (ri > np.percentile(ri[ok], 80))
wrong = wrong_interval = 0
for row in bz.itertuples():
    sel = ok & zone[row.zone_model_of_the_units_valued_land]
    n = int(sel.sum())
    mine = {"n_assessed": n, "flagged_by_hansen": int((sel & hf).sum()), "flagged_by_hansen_pct": 100 * (sel & hf).sum() / n, "median_corestack_degradation_rate": rdeg[sel].median(), "median_corestack_improvement_rate": ri[sel].median(),
            "spearman_hansen_vs_corestack_degradation": spearmanr(r[sel], rdeg[sel])[0], "spearman_hansen_vs_corestack_improvement": spearmanr(r[sel], ri[sel])[0]}
    tol = {"flagged_by_hansen_pct": 0.06, "median_corestack_degradation_rate": 6e-5, "median_corestack_improvement_rate": 6e-5, "spearman_hansen_vs_corestack_degradation": 6e-5, "spearman_hansen_vs_corestack_improvement": 6e-5}
    for tag, cf in (("degradation", cflag), ("improvement_the_placebo", pflag)):
        a, b, c_, dd = four(sel, hf, cf)
        exp = (a + b) * (a + c_) / n
        mine.update({f"flagged_on_{tag}": a + c_, f"both_{tag}": a, f"both_{tag}_expected_if_unrelated": exp, f"both_{tag}_observed_over_expected": a / exp, f"odds_ratio_{tag}": a * dd / (b * c_)})
        tol.update({f"both_{tag}_expected_if_unrelated": 0.006, f"both_{tag}_observed_over_expected": 6e-4, f"odds_ratio_{tag}": 6e-4})
    wrong += sum(off(v, getattr(row, k), tol.get(k, 0)) for k, v in mine.items())
    wrong_interval += sum(not holds(getattr(row, f"spearman_hansen_vs_corestack_{k}_lo95"), getattr(row, f"spearman_hansen_vs_corestack_{k}"), getattr(row, f"spearman_hansen_vs_corestack_{k}_hi95")) for k in ("degradation", "improvement"))
check(f"by zone model: every count, ratio, median and rank correlation, {len(bz)} rows", wrong == 0 and len(bz) == 3, f"{wrong} cells differ")
check("by zone model: the three groups hold every assessed unit once, and the intervals hold their estimates", int(bz.n_assessed.sum()) == int(ok.sum()) and wrong_interval == 0)

# ---- the minimum forest, on the reference land ---------------------------------------------------------------------------------
wrong = 0
for row in fr.itertuples():
    lo_y, hi_y = (int(x) for x in row.hansen_loss_years.split("-"))
    odd, even = (sum(h[f"loss_ha_{b}_{y}"] for b in ("gt10le30", "gt30") for y in range(lo_y, hi_y + 1) if y % 2 == k) for k in (1, 0))
    sel = (ref >= row.reference_ha_from) & ((ref < row.reference_ha_below) if not np.isnan(row.reference_ha_below) else True)
    wrong += int(sel.sum()) != row.n_units or int(((odd + even)[sel] == 0).sum()) != row.units_with_no_loss_in_those_years or off(spearmanr(odd[sel] / ref[sel], even[sel] / ref[sel])[0], row.odd_years_vs_even_years_spearman, 6e-4)
check(f"repeatability on the reference land: n, units without loss and the odd-against-even rank correlation, {len(fr)} rows", wrong == 0 and len(fr) == 14, f"{wrong} rows differ")

# ---- the intervals again, whole districts resampled -------------------------------------------------------------------------------
wrong = wrong_interval = far = 0
dist = district.to_numpy()
for units_label, part in bd.groupby("units"):
    sel = (ok & ((level == units_label) if units_label != "all units" else True)).to_numpy()
    idx = np.flatnonzero(sel)
    members = [idx[dist[idx] == k] for k in sorted(set(dist[idx]))]
    hv, cv = hf.to_numpy(), cflag.to_numpy()
    num = den = 0.0
    for m_ in members:
        a, b, c_, dd = int((hv[m_] & cv[m_]).sum()), int((hv[m_] & ~cv[m_]).sum()), int((~hv[m_] & cv[m_]).sum()), int((~hv[m_] & ~cv[m_]).sum())
        num += a * dd / len(m_); den += b * c_ / len(m_)
    sizes = [len(m_) for m_ in members]
    for row in part.itertuples():
        wrong += (row.n_assessed, row.n_districts, row.assessed_units_in_a_district_min, row.assessed_units_in_a_district_max) != (len(idx), len(members), min(sizes), max(sizes))
        if row.statistic == "odds_ratio_within_districts_mantel_haenszel":
            wrong += off(num / den, row.estimate, 6e-4)
            continue
        wrong += off(row.estimate, head.loc[units_label, row.statistic], 0) + off(row.lo95_units_resampled_singly, head.loc[units_label, f"{row.statistic}_lo95"], 0) + off(row.hi95_units_resampled_singly, head.loc[units_label, f"{row.statistic}_hi95"], 0)
        wrong_interval += not holds(row.lo95_whole_districts_resampled, row.estimate, row.hi95_whole_districts_resampled)
        if row.statistic == "odds_ratio":
            ors = []
            for _ in range(1000):
                j = np.concatenate([members[i] for i in rng.integers(0, len(members), len(members))])
                x, y = hv[j], cv[j]
                ors.append((x & y).sum() * (~x & ~y).sum() / max((x & ~y).sum() * (~x & y).sum(), 1))
            lo, hi = np.percentile(ors, [2.5, 97.5])
            width = row.hi95_whole_districts_resampled - row.lo95_whole_districts_resampled
            far += off(lo, row.lo95_whole_districts_resampled, 0.25 * width) or off(hi, row.hi95_whole_districts_resampled, 0.25 * width)
check(f"by district: n, the districts, the estimates and single-unit intervals (the summary's), and the odds ratio within districts, {len(bd)} rows", wrong == 0 and len(bd) == 21, f"{wrong} cells differ")
check("by district: every district interval is there, in order, and holds its estimate", wrong_interval == 0, f"{wrong_interval} do not")
check("by district: the odds-ratio intervals are close to an independent bootstrap of whole districts made here", far == 0, f"{far} rows are not")

# ---- the record ----------------------------------------------------------------------------------------------------------------------
tables = {"agreement_by_unit.csv": u.reset_index(), "agreement_summary.csv": s, "agreement_definitions.csv": d, "agreement_intervals_by_district.csv": bd, "agreement_by_zone.csv": bz, "agreement_floor_repeatability.csv": fr}
wrong = sum(prov["tables"].get(name, {}).get("rows") != len(t) or prov["tables"][name].get("columns") != len(t.columns) or prov["tables"][name].get("blank_cells") != {k: int(v) for k, v in t.isna().sum().items() if v}
            for name, t in tables.items())
check("the record's rows, columns and blank cells are the six files'", wrong == 0 and set(prov["tables"]) == set(tables), f"{wrong} tables differ")
counted = {lab: u.loc[(u.unit_level == lab) if lab != "all units" else slice(None), "agreement_class"].value_counts().to_dict() for lab in ("all units", "lgd_panchayat", "outside_village")}
pc = prov.get("counts", {})
check("the record's counts are the per-unit table's", pc.get("units") == len(u) and pc.get("assessed") == int(ok.sum()) and pc.get("by_level") == counted)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
stale = [i["path"] for i in prov["inputs"] if i["path"].endswith(".csv") and sha(R / i["path"]) != i["sha256"]]
check("the source tables on disk are the ones the record says the tables were built from", not stale and prov["definitions"]["headline_window"] == "common_2017_2023", f"changed since: {stale}" if stale else "")

# ---- one cross-check against the assembled table ---------------------------------------------------------------------------------
g = pd.read_csv(D / "degradation_by_unit.csv", dtype={"unit_id": str}).set_index("unit_id").sort_index()
mask_loss = sum(g[f"hansen_loss_ha_{y}"] for y in range(2017, 2024))
band_loss = sum(h[f"loss_ha_gt30_{y}"] for y in range(2017, 2024))
check("the mask's loss 2017-2023 in degradation_by_unit.csv equals the treecover2000 > 30 band's in the canopy-band table, unit by unit", close(mask_loss, band_loss, 2e-3),
      f"{mask_loss.sum() / 100:,.2f} km2 of the {loss['common_2017_2023'].sum() / 100:,.2f} km2 on the reference land")
check("in agreement_by_unit.csv no unit's loss on the reference land is less than the mask's loss in degradation_by_unit.csv", (u.hansen_loss_ha_common_2017_2023 >= mask_loss - 2e-3).all())

print(f"\n{sum(results)} of {len(results)} checks passed; n = {len(u):,} units, {int(ok.sum()):,} assessed")
sys.exit(0 if all(results) else 1)
