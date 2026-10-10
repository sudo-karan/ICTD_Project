"""Stage 4: the district-year panel and its models. Writes into `50_gap/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_build_gap_panel.py

DEFINITIONS (`scripts/verify_gap.py` is written from this text)

district_year_panel.csv - 30 districts x 13 financial years of R6.20 = 390 rows, sorted by census code and year
  pc11_district_code, district_name, r620_district
  fy                              the financial year as `2014-15`; fy_start_year is its first calendar year, t
  period                          `pre` (FY2014-15 to 2017-18), `post` (FY2018-19 to 2025-26), `part_year` (FY2026-27)
  part_year, in_models            1/0. FY2026-27 is a part year: it is in the panel and in no model. in_models = 1 for the
                                  other twelve years (360 district-years)
  plantation_lakh, nrm_lakh, water_lakh      `exp_cat_lakh` of the three categories (nested: never added)
  all_lakh                        `exp_all_lakh`, one value per district-year
  plantation_pct_of_all           100 x plantation_lakh / all_lakh
  plantation_works_ongoing, plantation_works_completed
  r620_last_updated               the stamp the report prints on that year's tables (the state totals file)
  frozen_2020_snapshot            1 where the stamp is 10/10/2020 (the four pre years)
  loss_ha_year_t_minus_1, loss_ha_year_t
                                  forest loss, dense plus open band, in calendar year t-1 and in calendar year t, summed
                                  over the district's units from `20_degradation/hansen_loss_by_canopy_band_by_unit.csv`.
                                  FY2014-15 takes 2013 and 2014. Hansen's record ends in 2025, so loss_ha_year_t is blank
                                  for FY2026-27
  loss_dense_ha_year_t_minus_1, loss_dense_ha_year_t        the same for the dense band alone
  standing_forest_ha_start_of_year_t_minus_1
                                  for each unit and band, the band's land in 2000 less its loss in 2001 to t-2, not
                                  below zero (the decision table's rule for the forest at the start of a window); the two
                                  bands added, and summed over the district's units
  loss_pct_of_standing_year_t_minus_1                        100 x loss_ha_year_t_minus_1 / that standing forest

MODELS, on the 360 district-years with in_models = 1, complete cases. All are OLS with every dummy written out.
  P1 (the headline)  plantation_pct_of_all on loss_ha_year_t_minus_1 / 100, with a dummy for every district in each period
                     (60) and a dummy for every financial year but the first of each period (10)
  P2                 the same with a dummy per district (30) and per financial year but the first (11): for comparison.
                     Plantation's share varies far more before FY2018-19 than after, so this one is identified largely by
                     how far each district fell in 2018 set against loss that rose after 2018
  P3                 P1 with asinh(plantation_lakh) as the outcome: the coefficient is in asinh(lakh rupees) per 100 ha,
                     not in percentage points
  P4                 P1 with loss in calendar year t
  P5                 P1 with loss_pct_of_standing_year_t_minus_1 as the regressor (percentage points of standing forest)
  P6                 P1 with the dense band's loss in t-1
  P7                 P1 with the regressor and its product with the post period; both terms are reported
A coefficient asks whether, within a district and within a period, years after more forest loss had more plantation
spending than that district's other years, beyond what all districts had in that year. It is not an effect, and
plantation is the scheme's label, not specific to forest.

INFERENCE. 30 clusters, the districts. `se_cr1` is the cluster-robust standard error with the factor
G/(G-1) x (N-1)/(N-K), for reference. The interval that counts is a restricted wild cluster bootstrap (the `wildboottest`
package: Webb weights, the null imposed), inverted by refitting with y - b0 * x: the bracket starts at the estimate
+/- 4 se_cr1 and is doubled as a whole (both ends together, so the two sides of a term always end the same number of
se_cr1 from the estimate), at most ten times, until p is below 0.05 at both ends; p is read on 16 equal steps to each
end and each side is bisected, to 0.001 se_cr1, inside the outermost step where p crosses 0.05. A side that never gets
below 0.05 is reported unbounded. The p of this bootstrap need not fall steadily as b0 moves away from the estimate, so
three things are kept for each side: `wcb_crossings_*` (the steps of the grid in which p crosses 0.05),
`wcb_p_rises_again_*` (yes where, going outward, p climbs more than 0.01 above a value it had already fallen to) and
`wcb_p_at_bracket_end_*` (p at the outer end of the bracket: where p settles when it stops falling). B = 9,999 for P1 and
1,999 for the others. Every p read on the grid is kept in `panel_models_wcb_grids.json`.

panel_models.csv - one row per model and reported term: id, term, headline, spec, outcome, outcome_unit, regressor,
  regressor_unit, coefficient_unit, n, clusters, n_parameters, coefficient, se_cr1, t_cr1, wcb_ci95_lo, wcb_ci95_hi,
  wcb_unbounded_lo, wcb_unbounded_hi, wcb_crossings_lo, wcb_crossings_hi, wcb_p_rises_again_lo, wcb_p_rises_again_hi,
  wcb_p_at_bracket_end_lo, wcb_p_at_bracket_end_hi, wcb_p, wcb_B, wcb_seed, wcb_weights
panel_models.txt - the same, set out to be read
gates_phase3.csv and this step's section of `gap.provenance.json`
"""
from __future__ import annotations

import json
import math
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D, dsum  # noqa: E402

STEP = "08_build_gap_panel"
SEED = 20261010
ZERO = Decimal(0)
B_HEADLINE, B_OTHER = 9999, 1999

MODELS = [  # id, outcome, regressor, fixed effects, B
    ("P1", "plantation_pct_of_all", "loss_t_minus_1_per_100_ha", "district_x_period", B_HEADLINE),
    ("P2", "plantation_pct_of_all", "loss_t_minus_1_per_100_ha", "district", B_OTHER),
    ("P3", "asinh_plantation_lakh", "loss_t_minus_1_per_100_ha", "district_x_period", B_OTHER),
    ("P4", "plantation_pct_of_all", "loss_t_per_100_ha", "district_x_period", B_OTHER),
    ("P5", "plantation_pct_of_all", "loss_pct_of_standing_t_minus_1", "district_x_period", B_OTHER),
    ("P6", "plantation_pct_of_all", "loss_dense_t_minus_1_per_100_ha", "district_x_period", B_OTHER),
    ("P7", "plantation_pct_of_all", "loss_t_minus_1_per_100_ha", "district_x_period", B_OTHER),
]
OUTCOME_UNIT = {"plantation_pct_of_all": "percentage points of the district's expenditure of the year",
                "asinh_plantation_lakh": "asinh of lakh rupees (not a percentage)"}
REGRESSOR_UNIT = {"loss_t_minus_1_per_100_ha": "100 ha of forest loss, dense plus open band, in calendar year t-1",
                  "loss_t_per_100_ha": "100 ha of forest loss, dense plus open band, in calendar year t",
                  "loss_pct_of_standing_t_minus_1": "percentage points of the forest standing at the start of year t-1, lost in year t-1",
                  "loss_dense_t_minus_1_per_100_ha": "100 ha of forest loss, dense band only, in calendar year t-1"}
SPEC = {"district_x_period": "a dummy for every district in each period (pre, post) and for every financial year but the first of each period",
        "district": "a dummy for every district and for every financial year but the first"}


def q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def build_panel(gates) -> list[dict]:
    cw = G.read_rows(G.OUT / "district_crosswalk.csv")
    code_of = {r["r620_district"]: r["pc11_district_code"] for r in cw}
    name = {r["pc11_district_code"]: r["district_name"] for r in cw}
    district = {r["unit_id"]: r["pc11_district_code"] for r in G.read_rows(G.OUT / "unit_district.csv")}
    # loss by district, band and year; and the forest standing at the start of each year
    years = G.YEARS
    loss = {c: {b: {y: ZERO for y in years} for b in ("dense", "open")} for c in name}
    standing = {c: {y: ZERO for y in range(2001, 2027)} for c in name}       # at the start of year y
    for r in G.read_rows(G.IN["hansen_bands"]):
        c = district[r["unit_id"]]
        for b, s in (("dense", "gt30"), ("open", "gt10le30")):
            left = D(r[f"area_ha_{s}"])
            for y in range(2001, 2027):
                standing[c][y] += max(left, ZERO)                             # land of 2000 less loss of 2001..y-1, not below zero
                if y <= 2025:
                    l = D(r[f"loss_ha_{s}_{y}"])
                    loss[c][b][y] += l
                    left -= l
    stamp = {}
    for r in G.read_rows(G.IN["r620_state"]):
        stamp.setdefault(r["fy"], set()).add(r["last_updated"])
    if any(len(v) != 1 for v in stamp.values()) or sorted(stamp) != G.FY_ALL:
        G.stop("the state totals do not carry one stamp for each of the 13 years")
    cells = {}
    for r in G.read_rows(G.IN["r620_district"]):
        cells.setdefault((code_of[r["district"]], r["fy"]), {})[r["category"]] = r
    rows = []
    for c in sorted(name):
        for fy in G.FY_ALL:
            x = cells[(c, fy)]
            if set(x) != set(G.CATEGORIES) or len({x[k]["exp_all_lakh"] for k in x}) != 1:
                G.stop(f"R6.20 does not carry the three categories with one total for {name[c]} {fy}")
            t = G.fy_start_year(fy)
            period = "pre" if fy in G.PRE else ("post" if fy in G.POST else "part_year")
            both = lambda y: loss[c]["dense"][y] + loss[c]["open"][y]
            plantation, all_ = D(x["Plantation"]["exp_cat_lakh"]), D(x["Plantation"]["exp_all_lakh"])
            st = standing[c][t - 1]
            rows.append({
                "pc11_district_code": c, "district_name": name[c], "r620_district": x["Plantation"]["district"],
                "fy": G.fy_short(fy), "fy_start_year": t, "period": period, "part_year": 1 if fy == G.PART else 0,
                "in_models": 0 if fy == G.PART else 1,
                "plantation_lakh": plantation, "nrm_lakh": D(x["NRM"]["exp_cat_lakh"]), "water_lakh": D(x["Water"]["exp_cat_lakh"]), "all_lakh": all_,
                "plantation_pct_of_all": q(100 * plantation / all_, "0.000001"),
                "plantation_works_ongoing": int(x["Plantation"]["works_ongoing"]), "plantation_works_completed": int(x["Plantation"]["works_completed"]),
                "r620_last_updated": next(iter(stamp[fy])), "frozen_2020_snapshot": 1 if next(iter(stamp[fy])) == G.FROZEN_STAMP else 0,
                "loss_ha_year_t_minus_1": both(t - 1), "loss_ha_year_t": both(t) if t <= 2025 else None,
                "loss_dense_ha_year_t_minus_1": loss[c]["dense"][t - 1], "loss_dense_ha_year_t": loss[c]["dense"][t] if t <= 2025 else None,
                "standing_forest_ha_start_of_year_t_minus_1": st,
                "loss_pct_of_standing_year_t_minus_1": q(100 * both(t - 1) / st, "0.000001")})
    # gates on the panel
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    add("rows of the panel (30 districts x 13 financial years)", 390, len(rows), len(rows) == 390)
    add("district-years in the models (FY2014-15 to 2025-26)", 360, sum(r["in_models"] for r in rows), sum(r["in_models"] for r in rows) == 360)
    alloc = {r["pc11_district_code"]: r for r in G.read_rows(G.OUT / "district_allocation.csv")}
    worst = ZERO
    for col, key in (("plantation_lakh", "plantation"), ("nrm_lakh", "nrm"), ("water_lakh", "water"), ("all_lakh", "all")):
        for period in ("pre", "post", "part_year"):
            for c in name:
                mine = dsum(r[col] for r in rows if r["pc11_district_code"] == c and r["period"] == period)
                worst = max(worst, abs(mine - D(alloc[c][f"r620_{key}_{period}_lakh"])))
    add("the panel's sums by district, category and period against step 2's (district_allocation.csv): largest difference, lakh", 0, format(worst, "f"), worst == 0)
    for period, exp in (("pre", "151843.18"), ("post", "13915.72"), ("part_year", "110.58")):
        s = dsum(r["plantation_lakh"] for r in rows if r["period"] == period)
        add(f"plantation expenditure of the panel, {period}, lakh", exp, format(s, "f"), s == Decimal(exp))
    for period, exp in (("pre", "11.25"), ("post", "1.78")):
        v = np.array([float(r["plantation_pct_of_all"]) for r in rows if r["period"] == period])
        sd1, sd0 = float(np.std(v, ddof=1)), float(np.std(v, ddof=0))
        add(f"standard deviation of plantation's share of district expenditure across district-years, {period}, percentage points "
            "(the owner's figure is reproduced with n in the divisor; with n - 1 it is the figure in brackets)", exp, f"{sd0:.2f} ({sd1:.2f})", f"{sd0:.2f}" == exp)
    cond_start = {}
    for r in G.read_rows(G.IN["condition_by_unit"]):
        cond_start[district[r["unit_id"]]] = cond_start.get(district[r["unit_id"]], ZERO) + D(r["forest_at_window_start_ha_2018_2025"])
    same = all(next(r for r in rows if r["pc11_district_code"] == c and r["fy_start_year"] == 2019)["standing_forest_ha_start_of_year_t_minus_1"] == cond_start[c] for c in name)
    add("forest standing at the start of 2018 (the panel's FY2019-20 rows) equals the decision table's forest at the start of the window 2018-2025, every district",
        "yes", "yes" if same else "no", same)
    tot_loss = dsum(r["loss_ha_year_t"] for r in rows if r["loss_ha_year_t"] is not None and 2018 <= r["fy_start_year"] <= 2025)
    add("forest loss of calendar years 2018 to 2025 in the panel (loss_ha_year_t), ha (within 1 of 90,028)", 90028, format(tot_loss, "f"), abs(tot_loss - 90028) <= 1)
    return rows


def design(rows: list[dict], fe: str, regressors: dict) -> tuple[np.ndarray, list[str]]:
    """The regressors first, then the dummies written out. No constant: the district dummies span it."""
    codes = np.array([r["pc11_district_code"] for r in rows])
    fys = np.array([r["fy"] for r in rows])
    periods = np.array([r["period"] for r in rows])
    cols, names = [np.asarray(v, float) for v in regressors.values()], list(regressors)
    if fe == "district_x_period":
        d, dn = G.dummies(np.char.add(np.char.add(codes, ":"), periods), "district_period")
        first = {G.fy_short(G.PRE[0]), G.fy_short(G.POST[0])}
        f, fn = G.dummies(fys, "fy", drop=sorted(first))
    else:
        d, dn = G.dummies(codes, "district")
        f, fn = G.dummies(fys, "fy", drop=[G.fy_short(G.FY_ALL[0])])
    return np.column_stack(cols + [d, f]), names + dn + fn


def main() -> None:
    G.require_stage4_environment()
    gates: list[tuple] = []
    inputs = {"r620_district": G.IN["r620_district"], "r620_state": G.IN["r620_state"], "hansen_bands": G.IN["hansen_bands"],
              "condition_by_unit": G.IN["condition_by_unit"], "district_crosswalk": G.OUT / "district_crosswalk.csv",
              "unit_district": G.OUT / "unit_district.csv", "district_allocation": G.OUT / "district_allocation.csv"}
    for p in inputs.values():
        if not p.exists():
            G.stop(f"an input is missing: {G.rel(p)} (run steps 0 and 2 first)")
    panel = build_panel(gates)
    G.write_rows(G.OUT / "district_year_panel.csv", panel,
                 ["pc11_district_code", "district_name", "r620_district", "fy", "fy_start_year", "period", "part_year", "in_models", "plantation_lakh",
                  "nrm_lakh", "water_lakh", "all_lakh", "plantation_pct_of_all", "plantation_works_ongoing", "plantation_works_completed",
                  "r620_last_updated", "frozen_2020_snapshot", "loss_ha_year_t_minus_1", "loss_ha_year_t", "loss_dense_ha_year_t_minus_1",
                  "loss_dense_ha_year_t", "standing_forest_ha_start_of_year_t_minus_1", "loss_pct_of_standing_year_t_minus_1"])
    grows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    if any(r["pass"] != "yes" for r in grows):
        G.write_rows(G.OUT / "gates_phase3.csv", grows, ["gate", "expected", "found", "pass"])
        for r in grows:
            print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
        G.stop("a gate on the panel failed: no model was fitted. See 50_gap/gates_phase3.csv")

    rows = [r for r in panel if r["in_models"] == 1]
    var = {
        "plantation_pct_of_all": [100.0 * float(r["plantation_lakh"]) / float(r["all_lakh"]) for r in rows],
        "asinh_plantation_lakh": [math.asinh(float(r["plantation_lakh"])) for r in rows],
        "loss_t_minus_1_per_100_ha": [float(r["loss_ha_year_t_minus_1"]) / 100.0 for r in rows],
        "loss_t_per_100_ha": [float(r["loss_ha_year_t"]) / 100.0 for r in rows],
        "loss_pct_of_standing_t_minus_1": [100.0 * float(r["loss_ha_year_t_minus_1"]) / float(r["standing_forest_ha_start_of_year_t_minus_1"]) for r in rows],
        "loss_dense_t_minus_1_per_100_ha": [float(r["loss_dense_ha_year_t_minus_1"]) / 100.0 for r in rows],
    }
    clusters = np.array([r["pc11_district_code"] for r in rows])
    post = np.array([1.0 if r["period"] == "post" else 0.0 for r in rows])
    out, grids, text, seeds = [], {}, [], {}
    for k, (mid, outcome, regressor, fe, B) in enumerate(MODELS):
        y = np.asarray(var[outcome], float)
        x = np.asarray(var[regressor], float)
        regs = {regressor: x}
        if mid == "P7":
            regs[regressor + "_x_post"] = x * post
        X, names = design(rows, fe, regs)
        model, res = G.fit_cluster_model(y, X, names, clusters)
        text.append(f"{mid}  {outcome} on {', '.join(regs)}; {SPEC[fe]}\n    n = {len(y)}, clusters = {len(set(clusters))}, parameters = {X.shape[1]}")
        for j, term in enumerate(regs):
            seed = SEED + 300 + 10 * k + j
            seeds[f"{mid}:{term}"] = seed
            b, se = float(res.params[term]), float(res.bse[term])
            w = G.wcb_interval(y, X, names, clusters, term, B, seed, b, se)
            grids[f"{mid}:{term}"] = {"estimate": b, "se_cr1": se, "B": B, "seed": seed, "grid": w["grid"], "tests_made": w["n_tests"]}
            unit = REGRESSOR_UNIT[regressor] + (", times the post period" if term.endswith("_x_post") else "")
            out.append({"id": mid, "term": term, "headline": "yes" if mid == "P1" else "no", "spec": SPEC[fe], "outcome": outcome,
                        "outcome_unit": OUTCOME_UNIT[outcome], "regressor": term, "regressor_unit": unit,
                        "coefficient_unit": f"{OUTCOME_UNIT[outcome]} per {unit}", "n": len(y), "clusters": len(set(clusters)),
                        "n_parameters": X.shape[1], "coefficient": round(b, 8), "se_cr1": round(se, 8), "t_cr1": round(b / se, 6),
                        "wcb_ci95_lo": None if w["ci95_lo"] is None else round(w["ci95_lo"], 8),
                        "wcb_ci95_hi": None if w["ci95_hi"] is None else round(w["ci95_hi"], 8),
                        "wcb_unbounded_lo": "yes" if w["unbounded_lo"] else "no", "wcb_unbounded_hi": "yes" if w["unbounded_hi"] else "no",
                        "wcb_crossings_lo": w["crossings_lo"], "wcb_crossings_hi": w["crossings_hi"],
                        "wcb_p_rises_again_lo": "yes" if w["p_rises_again_lo"] else "no", "wcb_p_rises_again_hi": "yes" if w["p_rises_again_hi"] else "no",
                        "wcb_p_at_bracket_end_lo": round(w["p_at_end_lo"], 6), "wcb_p_at_bracket_end_hi": round(w["p_at_end_hi"], 6),
                        "wcb_p": w["wcb_p"], "wcb_B": B, "wcb_seed": seed, "wcb_weights": "webb"})
            lo = "unbounded" if w["ci95_lo"] is None else f"{w['ci95_lo']:.6f}"
            hi = "unbounded" if w["ci95_hi"] is None else f"{w['ci95_hi']:.6f}"
            text.append(f"    {term}: coefficient {b:.6f}, CR1 se {se:.6f} (for reference); wild cluster bootstrap 95% interval {lo} to {hi}, p = {w['wcb_p']:.4f} "
                        f"(B = {B}, Webb weights, null imposed, seed {seed}); unit: {out[-1]['coefficient_unit']}")
            print(text[-2] if j == 0 else "", text[-1], sep="\n", flush=True)
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    add("models fitted, each on 360 district-years and 30 clusters", len(MODELS), sum(1 for r in out if r["term"] in REGRESSOR_UNIT and r["n"] == 360 and r["clusters"] == 30),
        sum(1 for r in out if r["term"] in REGRESSOR_UNIT and r["n"] == 360 and r["clusters"] == 30) == len(MODELS))
    bounded = sum(1 for r in out if r["wcb_unbounded_lo"] == "no" and r["wcb_unbounded_hi"] == "no")
    add("reported terms whose wild-bootstrap interval is bounded on both sides (reported, not a gate on a value)", "reported", f"{bounded} of {len(out)}", True)
    mono = sum(1 for r in out if r["wcb_p_rises_again_lo"] == "no" and r["wcb_p_rises_again_hi"] == "no" and r["wcb_crossings_lo"] <= 1 and r["wcb_crossings_hi"] <= 1)
    add("reported terms for which p fell steadily on both sides: one crossing of 0.05 a side and no climb back of more than 0.01 (reported, not a gate on a value)", "reported", f"{mono} of {len(out)}", True)

    G.write_rows(G.OUT / "panel_models.csv", out,
                 ["id", "term", "headline", "spec", "outcome", "outcome_unit", "regressor", "regressor_unit", "coefficient_unit", "n", "clusters",
                  "n_parameters", "coefficient", "se_cr1", "t_cr1", "wcb_ci95_lo", "wcb_ci95_hi", "wcb_unbounded_lo", "wcb_unbounded_hi",
                  "wcb_crossings_lo", "wcb_crossings_hi", "wcb_p_rises_again_lo", "wcb_p_rises_again_hi", "wcb_p_at_bracket_end_lo",
                  "wcb_p_at_bracket_end_hi", "wcb_p", "wcb_B", "wcb_seed", "wcb_weights"])
    (G.OUT / "panel_models_wcb_grids.json").write_text(json.dumps(grids, indent=1) + "\n", encoding="utf-8")
    head = ["Stage 4: the district-year panel models. Written " + G.utc_now() + " by scripts/08_build_gap_panel.py.",
            "360 district-years (30 districts, FY2014-15 to FY2025-26); FY2026-27 is a part year and is in no model.",
            "A coefficient asks whether, within a district and within a period, years after more forest loss had more plantation spending",
            "than that district's other years, beyond what all districts had in that year. It is not an effect. Plantation is the scheme's",
            "label and is not specific to forest. The interval that counts is the wild cluster bootstrap's; the CR1 standard error is for reference.",
            "P1 is the headline. P2 has plain district dummies and is read with its caveat (see the script's docstring).", ""]
    (G.OUT / "panel_models.txt").write_text("\n".join(head + text) + "\n", encoding="utf-8")
    grows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / "gates_phase3.csv", grows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("district_year_panel.csv", "panel_models.csv", "panel_models.txt", "panel_models_wcb_grids.json", "gates_phase3.csv")]
    G.record_step(STEP, Path(__file__), inputs, outputs, {
        "seeds": {"base": SEED, "by_model_and_term": seeds, "bootstrap": "wildboottest, weights_type='webb', impose_null=True"},
        "B": {"P1": B_HEADLINE, "others": B_OTHER},
        "interval": "test inversion: refit with y - b0 * x; bracket estimate +/- 4 CR1 se, doubled as a whole (both ends together) at most 10 times until p is below 0.05 at both ends; 16 steps to each end; bisection to 0.001 CR1 se in the outermost step where p crosses 0.05",
        "gates": len(grows), "gates_passed": sum(r["pass"] == "yes" for r in grows)})
    for r in grows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in grows if r["pass"] != "yes"]
    print(f"\n{len(grows) - len(failed)} of {len(grows)} gates passed; wrote {', '.join(G.rel(p) for p in outputs)}")
    if failed:
        G.stop(f"{len(failed)} gate(s) failed; see 50_gap/gates_phase3.csv")


if __name__ == "__main__":
    main()
