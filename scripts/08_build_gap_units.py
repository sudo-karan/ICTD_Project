"""Stage 4, the historical companion: units within districts. Writes into `50_gap/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_build_gap_units.py

The question: in the same district, did units that had forest-named works by FY2017-18 lose a different share of their
forest in 2018-2025 than units that had none, given their forest and their earlier loss? The exposure comes before the
outcome. Planners sited the works, so this is an association and selection is likely; the control for earlier loss
speaks to part of that, not all. Nothing here is an effect.

DEFINITIONS (`scripts/verify_gap.py` is written from this text)

unit_history.csv - one row for each of the 11,468 units, sorted by district and unit id
  unit_id, unit_level, outside_village (1/0), pc11_district_code, district_name (from `50_gap/unit_district.csv`)
  forest_2000_ha                  `dense_2000_ha` + `open_2000_ha` of `55_decision/condition_by_unit.csv`
  forest_at_window_start_ha       `forest_at_window_start_ha_2018_2025` of that table: forest at the start of 2018
  dense_at_window_start_ha        the dense band's land in 2000 less its loss in 2001 to 2017, not below zero, from the
                                  yearly columns of `20_degradation/hansen_loss_by_canopy_band_by_unit.csv`
  dense_share_of_forest_at_start_pct   100 x dense_at_window_start_ha / forest_at_window_start_ha; blank where that is zero
  loss_2001_2017_ha               dense plus open loss of 2001 to 2017, from the yearly columns
  prior_loss_share_pct            100 x loss_2001_2017_ha / forest_2000_ha; blank where forest_2000_ha is zero
  log_forest_at_start             the natural logarithm of forest_at_window_start_ha; blank where that is zero
  forest_loss_share_pct           `forest_loss_share_pct_2018_2025` of the decision table, as it carries it (two decimals;
                                  blank where the forest at the start prints under 10 ha)
  loss_recorded                   1 where `loss_column_2018_2025` is `some` (1 ha or more of forest loss in the window), else 0
  forest_named_by_fy2017_18_inr   `expenditure_forest_named_worktype` of `40_allocation/allocation_by_unit_fy.csv` summed
                                  over the unit's rows whose `fy_work_start` is 2017-18 or earlier (a work with no start
                                  year, `NA`, counts as not started by then); 0 for a unit with no such row
  e1_any_forest_named             1 where that is above zero, else 0: the headline exposure
  e2_asinh_forest_named_inr_per_ha     asinh(forest_named_by_fy2017_18_inr / forest_at_window_start_ha); blank where the
                                  forest at the start is zero. In asinh(rupees per hectare), not a percentage
  plantation_category_by_fy2017_18_inr, e3_any_plantation_category    the same for `expenditure_plantation_category`
  st_share_pct, adi_2011          100 x `st_share`, and `adi_2011`, of `30_need/need_by_unit.csv`; blank for outside-village
                                  units (no census rows) and where the need table is blank
  corestack_degradation_ha_tc_gt10, corestack_improvement_ha_tc_gt10      of `20_degradation/corestack_by_unit.csv`
  downward_share_pct              100 x degradation / (degradation + improvement), CoRE Stack's classes of 2017-2023 on
                                  land with canopy above 10 per cent in 2000: the downward share of `docs/RESULTS.md`
                                  section 4, formed per unit. Blank where the two classes add to zero
  in_district_left_out_of_c7      1 where the unit's district has `left_out_of_c7` = yes in `50_gap/district_need.csv`
  in_h1 ... in_h9                 1 where the unit is in that model's sample (below), else 0

MODELS. OLS; every model has a dummy for every district present in its sample (no constant) and these controls:
log_forest_at_start, dense_share_of_forest_at_start_pct, prior_loss_share_pct and outside_village.
  H1 (the headline)  forest_loss_share_pct on e1_any_forest_named; units with forest_at_window_start_ha of 100 or more
  H2, H3             the same with a floor of 50 ha, and of 10 ha (the layer's standing minimum)
  H4                 H1 without the units of the districts C7 leaves out
  H5                 H1 on LGD panchayat units only, adding st_share_pct and adi_2011 (units that have both); the
                     outside_village control drops out, being zero for all of them
  H6                 H1 with e2_asinh_forest_named_inr_per_ha in place of e1
  H7                 H1 with e3_any_plantation_category in place of e1
  H8                 loss_recorded on e1, a linear probability model: the coefficient is a difference in probability (0 to 1)
  H9                 downward_share_pct on e1; units of H1's sample whose downward share is defined
The floor is set on forest at the start of the window, not on the land the agreement test compares: a call of the
owner's instruction of 10 October 2026, listed in docs/GAP.md. A sample is always the complete cases of its variables.

INFERENCE as in the panel (`scripts/08_build_gap_panel.py`): clusters are the districts; `se_cr1` for reference; the
interval is a restricted wild cluster bootstrap with Webb weights, inverted by refitting with y - b0 * x. B = 9,999 for
H1 and 1,999 for the others.

unit_history_models.csv - one row per model: id, headline, sample, outcome, outcome_unit, exposure, exposure_unit,
  coefficient_unit, controls, n_units, n_exposed (units with the exposure above zero), n_districts (= clusters),
  n_parameters, coefficient, se_cr1, t_cr1, wcb_ci95_lo, wcb_ci95_hi, wcb_unbounded_lo, wcb_unbounded_hi,
  wcb_crossings_lo, wcb_crossings_hi, wcb_p_rises_again_lo, wcb_p_rises_again_hi, wcb_p_at_bracket_end_lo,
  wcb_p_at_bracket_end_hi (as in the panel's docstring), wcb_p, wcb_B, wcb_seed, wcb_weights
unit_history_models.txt, unit_history_models_wcb_grids.json, gates_phase4.csv, and this step's section of the provenance.
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

STEP = "08_build_gap_units"
SEED = 20261010
ZERO = Decimal(0)
B_HEADLINE, B_OTHER = 9999, 1999
CONTROLS = ["log_forest_at_start", "dense_share_of_forest_at_start_pct", "prior_loss_share_pct", "outside_village"]

MODELS = [  # id, outcome, exposure, floor (ha), extra controls, which units, B
    ("H1", "forest_loss_share_pct", "e1_any_forest_named", 100, [], "all", B_HEADLINE),
    ("H2", "forest_loss_share_pct", "e1_any_forest_named", 50, [], "all", B_OTHER),
    ("H3", "forest_loss_share_pct", "e1_any_forest_named", 10, [], "all", B_OTHER),
    ("H4", "forest_loss_share_pct", "e1_any_forest_named", 100, [], "not_c7", B_OTHER),
    ("H5", "forest_loss_share_pct", "e1_any_forest_named", 100, ["st_share_pct", "adi_2011"], "lgd", B_OTHER),
    ("H6", "forest_loss_share_pct", "e2_asinh_forest_named_inr_per_ha", 100, [], "all", B_OTHER),
    ("H7", "forest_loss_share_pct", "e3_any_plantation_category", 100, [], "all", B_OTHER),
    ("H8", "loss_recorded", "e1_any_forest_named", 100, [], "all", B_OTHER),
    ("H9", "downward_share_pct", "e1_any_forest_named", 100, [], "all", B_OTHER),
]
OUTCOME_UNIT = {"forest_loss_share_pct": "percentage points of the forest at the start of 2018 lost in 2018-2025",
                "loss_recorded": "probability (0 to 1) that 1 ha or more of forest loss is recorded in 2018-2025",
                "downward_share_pct": "percentage points of CoRE Stack's downward share, 2017-2023"}
EXPOSURE_UNIT = {"e1_any_forest_named": "a unit with any forest-named expenditure on works started by FY2017-18, against a unit with none",
                 "e2_asinh_forest_named_inr_per_ha": "one unit of asinh(forest-named rupees, works started by FY2017-18, per hectare of forest at the start of 2018)",
                 "e3_any_plantation_category": "a unit with any plantation-category expenditure on works started by FY2017-18, against a unit with none"}
WHICH = {"all": "every unit", "not_c7": "units outside the districts C7 leaves out", "lgd": "LGD panchayat units only"}


def q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def build_table(gates) -> list[dict]:
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    ud = {r["unit_id"]: r for r in G.read_rows(G.OUT / "unit_district.csv")}
    left_out = {r["pc11_district_code"] for r in G.read_rows(G.OUT / "district_need.csv") if r["left_out_of_c7"] == "yes"}
    bands = {r["unit_id"]: r for r in G.read_rows(G.IN["hansen_bands"])}
    need = {r["unit_id"]: r for r in G.read_rows(G.IN["need_by_unit"])}
    core = {r["unit_id"]: r for r in G.read_rows(G.IN["corestack_by_unit"])}
    spend = {}
    for r in G.read_rows(G.IN["allocation_by_unit_fy"]):
        if G.dump_fy_started_by(r["fy_work_start"]):
            s = spend.setdefault(r["unit_id"], [ZERO, ZERO])
            s[0] += G.money(r["expenditure_forest_named_worktype"])
            s[1] += G.money(r["expenditure_plantation_category"])
    rows, mismatch = [], 0
    for c in G.read_rows(G.IN["condition_by_unit"]):
        u = c["unit_id"]
        b = bands[u]
        start = D(c["forest_at_window_start_ha_2018_2025"])
        dense_start = max(D(b["area_ha_gt30"]) - dsum(D(b[f"loss_ha_gt30_{y}"]) for y in range(2001, 2018)), ZERO)
        open_start = max(D(b["area_ha_gt10le30"]) - dsum(D(b[f"loss_ha_gt10le30_{y}"]) for y in range(2001, 2018)), ZERO)
        mismatch += dense_start + open_start != start
        f2000 = D(c["dense_2000_ha"]) + D(c["open_2000_ha"])
        prior = dsum(D(b[f"loss_ha_gt30_{y}"]) + D(b[f"loss_ha_gt10le30_{y}"]) for y in range(2001, 2018))
        fn, pl = spend.get(u, [ZERO, ZERO])
        lgd = ud[u]["outside_village"] == "0"
        n = need[u]
        deg, imp = D(core[u]["corestack_degradation_ha_tc_gt10"]), D(core[u]["corestack_improvement_ha_tc_gt10"])
        rows.append({
            "unit_id": u, "unit_level": ud[u]["unit_level"], "outside_village": int(ud[u]["outside_village"]),
            "pc11_district_code": ud[u]["pc11_district_code"], "district_name": ud[u]["district_name"],
            "forest_2000_ha": f2000, "forest_at_window_start_ha": start, "dense_at_window_start_ha": dense_start,
            "dense_share_of_forest_at_start_pct": None if start == 0 else q(100 * dense_start / start, "0.000001"),
            "loss_2001_2017_ha": prior, "prior_loss_share_pct": None if f2000 == 0 else q(100 * prior / f2000, "0.000001"),
            "log_forest_at_start": None if start == 0 else round(math.log(float(start)), 10),
            "forest_loss_share_pct": None if c["forest_loss_share_pct_2018_2025"] == "" else D(c["forest_loss_share_pct_2018_2025"]),
            "loss_recorded": 1 if c["loss_column_2018_2025"] == "some" else 0,
            "forest_named_by_fy2017_18_inr": fn, "e1_any_forest_named": 1 if fn > 0 else 0,
            "e2_asinh_forest_named_inr_per_ha": None if start == 0 else round(math.asinh(float(fn) / float(start)), 10),
            "plantation_category_by_fy2017_18_inr": pl, "e3_any_plantation_category": 1 if pl > 0 else 0,
            "st_share_pct": q(100 * D(n["st_share"]), "0.0001") if lgd and n["st_share"] != "" else None,
            "adi_2011": D(n["adi_2011"]) if lgd and n["adi_2011"] != "" else None,
            "corestack_degradation_ha_tc_gt10": deg, "corestack_improvement_ha_tc_gt10": imp,
            "downward_share_pct": None if deg + imp == 0 else q(100 * deg / (deg + imp), "0.000001"),
            "in_district_left_out_of_c7": 1 if ud[u]["pc11_district_code"] in left_out else 0})
    add("units in the table", 11468, len(rows), len(rows) == 11468)
    add("units whose dense and open bands at the start of 2018, taken from the yearly columns, do not add to the decision table's forest at "
        "the start of the window", 0, mismatch, mismatch == 0)
    rows.sort(key=lambda r: (r["pc11_district_code"], r["unit_id"]))
    return rows


def sample(rows, floor, extra, which, outcome, exposure):
    need_cols = [outcome, exposure] + [c for c in CONTROLS if not (which == "lgd" and c == "outside_village")] + extra
    out = []
    for r in rows:
        if r["forest_at_window_start_ha"] < floor:
            continue
        if which == "not_c7" and r["in_district_left_out_of_c7"] == 1:
            continue
        if which == "lgd" and r["outside_village"] == 1:
            continue
        if any(r[c] is None for c in need_cols):
            continue
        out.append(r)
    return out, need_cols[2:]


def main() -> None:
    G.require_stage4_environment()
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    inputs = {k: G.IN[k] for k in ("condition_by_unit", "hansen_bands", "need_by_unit", "corestack_by_unit", "allocation_by_unit_fy")}
    inputs["unit_district"] = G.OUT / "unit_district.csv"
    inputs["district_need"] = G.OUT / "district_need.csv"
    for p in inputs.values():
        if not p.exists():
            G.stop(f"an input is missing: {G.rel(p)} (run steps 0 and 2 first)")
    rows = build_table(gates)
    for mid, outcome, exposure, floor, extra, which, B in MODELS:
        members = {r["unit_id"] for r in sample(rows, floor, extra, which, outcome, exposure)[0]}
        for r in rows:
            r[f"in_{mid.lower()}"] = 1 if r["unit_id"] in members else 0
    near = {f: sum(1 for r in rows if Decimal(f) - Decimal("0.005") <= r["forest_at_window_start_ha"] < f) for f in (100, 50, 10)}
    add("units whose forest at the start of 2018 is within half a hundredth of a hectare below a floor (100 / 50 / 10 ha), where the floor "
        "read on the figure as printed to two decimals would differ from the floor read on four", "0 / 0 / 0",
        " / ".join(str(near[f]) for f in (100, 50, 10)), all(v == 0 for v in near.values()))
    cols = ["unit_id", "unit_level", "outside_village", "pc11_district_code", "district_name", "forest_2000_ha", "forest_at_window_start_ha",
            "dense_at_window_start_ha", "dense_share_of_forest_at_start_pct", "loss_2001_2017_ha", "prior_loss_share_pct", "log_forest_at_start",
            "forest_loss_share_pct", "loss_recorded", "forest_named_by_fy2017_18_inr", "e1_any_forest_named", "e2_asinh_forest_named_inr_per_ha",
            "plantation_category_by_fy2017_18_inr", "e3_any_plantation_category", "st_share_pct", "adi_2011", "corestack_degradation_ha_tc_gt10",
            "corestack_improvement_ha_tc_gt10", "downward_share_pct", "in_district_left_out_of_c7"] + [f"in_{m[0].lower()}" for m in MODELS]
    G.write_rows(G.OUT / "unit_history.csv", rows, cols)
    fn_total = dsum(r["forest_named_by_fy2017_18_inr"] for r in rows)
    alloc = dsum(D(r["dump_forest_named_started_by_fy2017_18_inr"]) for r in G.read_rows(G.OUT / "district_allocation.csv"))
    add("forest-named expenditure on works started by FY2017-18, summed over units, against step 2's sum over districts, rupees", format(alloc, "f"),
        format(fn_total, "f"), fn_total == alloc)
    h1 = [r for r in rows if r["in_h1"] == 1]
    add("H1's sample has no unit with a blank outcome: every unit with 100 ha or more at the start has a share", "yes",
        "yes" if len(h1) == sum(1 for r in rows if r["forest_at_window_start_ha"] >= 100) else "no",
        len(h1) == sum(1 for r in rows if r["forest_at_window_start_ha"] >= 100))

    if any(not ok for *_x, ok in gates):
        grows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
        G.write_rows(G.OUT / "gates_phase4.csv", grows, ["gate", "expected", "found", "pass"])
        for r in grows:
            print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
        G.stop("a gate on the unit table failed: no model was fitted. See 50_gap/gates_phase4.csv")
    out, grids, text, seeds = [], {}, [], {}
    for k, (mid, outcome, exposure, floor, extra, which, B) in enumerate(MODELS):
        s, controls = sample(rows, floor, extra, which, outcome, exposure)
        y = np.array([float(r[outcome]) for r in s])
        x = np.array([float(r[exposure]) for r in s])
        Z = np.column_stack([[float(r[c]) for r in s] for c in controls])
        clusters = np.array([r["pc11_district_code"] for r in s])
        Dm, dn = G.dummies(clusters, "district")
        X, names = np.column_stack([x, Z, Dm]), [exposure] + controls + dn
        model, res = G.fit_cluster_model(y, X, names, clusters)
        b, se = float(res.params[exposure]), float(res.bse[exposure])
        seed = SEED + 500 + k
        seeds[mid] = seed
        w = G.wcb_interval(y, X, names, clusters, exposure, B, seed, b, se)
        grids[mid] = {"estimate": b, "se_cr1": se, "B": B, "seed": seed, "grid": w["grid"], "tests_made": w["n_tests"]}
        words = f"forest at the start of 2018 of {floor} ha or more; {WHICH[which]}" + ("; complete cases" if extra or outcome == "downward_share_pct" else "")
        out.append({"id": mid, "headline": "yes" if mid == "H1" else "no", "sample": words, "outcome": outcome, "outcome_unit": OUTCOME_UNIT[outcome],
                    "exposure": exposure, "exposure_unit": EXPOSURE_UNIT[exposure], "coefficient_unit": f"{OUTCOME_UNIT[outcome]}, per {EXPOSURE_UNIT[exposure]}",
                    "controls": "; ".join(controls) + "; a dummy for every district", "n_units": len(s), "n_exposed": int((x > 0).sum()),
                    "n_districts": len(set(clusters)), "n_parameters": X.shape[1], "coefficient": round(b, 8), "se_cr1": round(se, 8), "t_cr1": round(b / se, 6),
                    "wcb_ci95_lo": None if w["ci95_lo"] is None else round(w["ci95_lo"], 8), "wcb_ci95_hi": None if w["ci95_hi"] is None else round(w["ci95_hi"], 8),
                    "wcb_unbounded_lo": "yes" if w["unbounded_lo"] else "no", "wcb_unbounded_hi": "yes" if w["unbounded_hi"] else "no",
                        "wcb_crossings_lo": w["crossings_lo"], "wcb_crossings_hi": w["crossings_hi"],
                        "wcb_p_rises_again_lo": "yes" if w["p_rises_again_lo"] else "no", "wcb_p_rises_again_hi": "yes" if w["p_rises_again_hi"] else "no",
                        "wcb_p_at_bracket_end_lo": round(w["p_at_end_lo"], 6), "wcb_p_at_bracket_end_hi": round(w["p_at_end_hi"], 6),
                    "wcb_p": w["wcb_p"], "wcb_B": B, "wcb_seed": seed, "wcb_weights": "webb"})
        lo = "unbounded" if w["ci95_lo"] is None else f"{w['ci95_lo']:.6f}"
        hi = "unbounded" if w["ci95_hi"] is None else f"{w['ci95_hi']:.6f}"
        text.append(f"{mid}  {outcome} on {exposure}; {words}\n    controls: {out[-1]['controls']}\n    n = {len(s)} units, {out[-1]['n_exposed']} exposed, "
                    f"{out[-1]['n_districts']} districts (clusters), {X.shape[1]} parameters\n    coefficient {b:.6f}, CR1 se {se:.6f} (for reference); wild cluster "
                    f"bootstrap 95% interval {lo} to {hi}, p = {w['wcb_p']:.4f} (B = {B}, Webb weights, null imposed, seed {seed})\n    unit: {out[-1]['coefficient_unit']}")
        print(text[-1], flush=True)
    add("models fitted (H9 among them: 20_degradation carries the two classes' hectares for every unit, from which the downward share is formed)", len(MODELS), len(out), len(out) == len(MODELS))
    bounded = sum(1 for r in out if r["wcb_unbounded_lo"] == "no" and r["wcb_unbounded_hi"] == "no")
    add("models whose wild-bootstrap interval is bounded on both sides (reported, not a gate on a value)", "reported", f"{bounded} of {len(out)}", True)
    mono = sum(1 for r in out if r["wcb_p_rises_again_lo"] == "no" and r["wcb_p_rises_again_hi"] == "no" and r["wcb_crossings_lo"] <= 1 and r["wcb_crossings_hi"] <= 1)
    add("models for which p fell steadily on both sides: one crossing of 0.05 a side and no climb back of more than 0.01 (reported, not a gate on a value)", "reported", f"{mono} of {len(out)}", True)

    G.write_rows(G.OUT / "unit_history_models.csv", out,
                 ["id", "headline", "sample", "outcome", "outcome_unit", "exposure", "exposure_unit", "coefficient_unit", "controls", "n_units", "n_exposed",
                  "n_districts", "n_parameters", "coefficient", "se_cr1", "t_cr1", "wcb_ci95_lo", "wcb_ci95_hi", "wcb_unbounded_lo", "wcb_unbounded_hi",
                  "wcb_crossings_lo", "wcb_crossings_hi", "wcb_p_rises_again_lo", "wcb_p_rises_again_hi", "wcb_p_at_bracket_end_lo",
                  "wcb_p_at_bracket_end_hi", "wcb_p", "wcb_B", "wcb_seed", "wcb_weights"])
    (G.OUT / "unit_history_models_wcb_grids.json").write_text(json.dumps(grids, indent=1) + "\n", encoding="utf-8")
    head = ["Stage 4: the historical companion, units within districts. Written " + G.utc_now() + " by scripts/08_build_gap_units.py.",
            "In the same district, did units that had forest-named works by FY2017-18 lose a different share of their forest in 2018-2025 than units",
            "that had none, given their forest and their earlier loss? The exposure comes before the outcome. Planners sited the works: this is an",
            "association, and selection is likely. The interval that counts is the wild cluster bootstrap's; the CR1 standard error is for reference.",
            "H1 is the headline.", ""]
    (G.OUT / "unit_history_models.txt").write_text("\n".join(head + text) + "\n", encoding="utf-8")
    grows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / "gates_phase4.csv", grows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("unit_history.csv", "unit_history_models.csv", "unit_history_models.txt", "unit_history_models_wcb_grids.json", "gates_phase4.csv")]
    G.record_step(STEP, Path(__file__), inputs, outputs, {
        "seeds": {"base": SEED, "by_model": seeds, "bootstrap": "wildboottest, weights_type='webb', impose_null=True"},
        "B": {"H1": B_HEADLINE, "others": B_OTHER},
        "h9": "run: 20_degradation/corestack_by_unit.csv carries, for every unit, the hectares of the degradation class and of the improvement class on land "
              "with canopy above 10 per cent in 2000; the downward share (degradation over degradation plus improvement, docs/RESULTS.md section 4) is "
              "formed from them per unit. No table carries the share itself as a column",
        "gates": len(grows), "gates_passed": sum(r["pass"] == "yes" for r in grows)})
    for r in grows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in grows if r["pass"] != "yes"]
    print(f"\n{len(grows) - len(failed)} of {len(grows)} gates passed; wrote {', '.join(G.rel(p) for p in outputs)}")
    if failed:
        G.stop(f"{len(failed)} gate(s) failed; see 50_gap/gates_phase4.csv")


if __name__ == "__main__":
    main()
