"""Stage 4, the headline: need and allocation by district, set beside one another. Writes into `50_gap/` only.

    .venv/bin/python scripts/08_build_gap_districts.py

The owner's question, in the supervisor's words: "determine which areas have seen forest degradation, are also
marginalised, and have they seen good enough resource allocation in the past". Current allocation exists only by
district (MIS report R6.20), so the district is the unit here: 30 districts. Nothing here is about cause: the tables
describe where money went relative to where forest was lost.

DEFINITIONS (every column of every table is defined here; `scripts/verify_gap.py` is written from this text)

"Forest" is Hansen canopy above 10 per cent in 2000, in the two bands the decision table carries: dense (above 30) and
open (10 to 30). The band at or below 10 decides nothing. Hectares are those of `55_decision/condition_by_unit.csv`
(four decimals) and are added exactly. A unit's district is the one `50_gap/unit_district.csv` gives it (step 0).
A window is a span of calendar years, ends included: 2018_2025 (the default), 2001_2025, 2017_2023, 2021_2025.

district_need.csv - one row per district (30 rows, sorted by census code)
  pc11_district_code, district_name, r620_district      from `50_gap/district_crosswalk.csv`
  n_units, n_units_lgd, n_units_outside                  units of the district; LGD panchayat units; outside-village units
  forest_2000_ha (+ _lgd, _outside)                      sum over units of `dense_2000_ha` + `open_2000_ha`
  for each window W:
    n1_ha_W (+ _lgd, _outside)                           N1: sum of `forest_loss_ha_W` over the units whose `cell_W` is
                                                         one of the three "loss recorded" cells (open_loss, dense_loss,
                                                         little_loss)
    n_units_loss_cells_W                                 how many units that is
    forest_loss_ha_W_all_units                           sum of `forest_loss_ha_W` over every unit
    loss_below_minimum_ha_W                              the difference: loss in units whose loss is under the 1 ha minimum
    forest_at_window_start_ha_W                          sum over every unit of `forest_at_window_start_ha_W`
  n2_ha (+ _lgd, _outside), n_units_anr                  N2: sum of `standing_open_ha` over the units whose default-window
                                                         cell is open_none (the assisted-natural-regeneration cell).
                                                         A stock; N1 is a flow; they are never added
  loss_2001_2013_ha                                      sum over every unit of the yearly dense and open loss of 2001 to
                                                         2013 in `20_degradation/hansen_loss_by_canopy_band_by_unit.csv`
  n1_ha_2018_2025_in_east_coast_only_units, _in_eastern_plateau_only_units, _in_units_under_both_models,
  _in_units_with_no_zone                                 N1 of the default window split by the unit's `corestack_zone_model`
                                                         in `20_degradation/agreement_by_unit.csv` (`ECPHR only`,
                                                         `EPAHR only`, `both models`, blank)
  east_coast_share_of_n1_pct                             the first of those as a per cent of the district's N1; blank
                                                         where N1 is zero
  n_assessed_units_east_coast_only                       units the agreement headline left out: `assessed` = 1 and zone
                                                         `ECPHR only`
  left_out_of_c7                                         yes where east_coast_share_of_n1_pct is above 50 (the rule used
                                                         for C7 and H4), else no. A district with no N1 stays in
  left_out_under_the_other_rule                          yes where n_assessed_units_east_coast_only is above 0
  population_lgd, st_pop_lgd, sc_pop_lgd                 sums over the district's LGD panchayat units of `population`,
                                                         `st_pop`, `sc_pop` in `30_need/need_by_unit.csv`. Outside-village
                                                         land has no census rows and is in none of these
  st_share_pct, st_class                                 100 x st_pop_lgd / population_lgd; its class by the layer's rule
                                                         (the per cent rounded to two decimals; under 18; 18 to 33, the
                                                         value 33 included; above 33 to 50, the value 50 included; above 50),
                                                         with the layer's own labels
  sc_share_pct, sc_tercile                               the same share for Scheduled Castes; terciles of 10, 10 and 10
                                                         districts by ascending share (ties by census code)
  adi_2011, adi_2011_population_covered_pct, n_units_lgd_with_adi
                                                         the mean of `adi_2011` over the district's LGD units that have a
                                                         value, weighted by unit population; the population of those units
                                                         as a per cent of population_lgd; their number
  adi_tercile                                            terciles of 10, 10 and 10 districts by ascending adi_2011 (ties
                                                         by census code): `lowest third of the index`, `middle third`,
                                                         `highest third of the index`. Higher is more developed: the
                                                         index is a sum of five indicators each ranked 1 (low) to 3
                                                         (`docs/NEED.md`; the group's data dictionary in `00_raw/docs/`)

district_allocation.csv - one row per district. Money from R6.20 is in lakh rupees, from the dump in rupees
  r620_plantation_pre_lakh, _post_lakh, _part_year_lakh  sums of `exp_cat_lakh`, category Plantation, over FY2014-15 to
                                                         2017-18 (pre), FY2018-19 to 2025-26 (post), FY2026-27 (a part
                                                         year, reported alone and in no sum, share or model)
  r620_plantation_post_without_fy2018_19_lakh            FY2019-20 to 2025-26
  r620_nrm_*, r620_water_*, r620_all_*                   the same three periods for NRM, Water and all expenditure
                                                         (`exp_all_lakh`, one value per district-year). NRM, water and
                                                         plantation are nested: never added or subtracted
  plantation_pct_of_all_pre, _post                       100 x plantation / all expenditure of the same period
  plantation_works_fy2016_17, _fy2025_26                 `works_ongoing` + `works_completed`, category Plantation
  r620_pre_years_last_updated                            the stamp R6.20 prints on the four pre tables (10/10/2020: a
                                                         snapshot frozen in 2020)
  dump_forest_named_started_by_fy2017_18_inr             `expenditure_forest_named_worktype` of
                                                         `40_allocation/allocation_by_unit_fy.csv` summed over the
                                                         district's units and over rows whose `fy_work_start` is 2017-18
                                                         or earlier. Lifetime cost indexed by the year a work started:
                                                         never in a sum with R6.20
  dump_forest_named_started_later_inr, dump_forest_named_start_year_missing_inr
                                                         the same for later years and for `fy_work_start` = NA (a work
                                                         with no start year counts as not started by FY2017-18)
  dump_plantation_category_*                             the same three for `expenditure_plantation_category`
  n_units_with_forest_named_by_fy2017_18                 units of the district with such expenditure above zero
  dump_no_unit_total_inr, dump_no_unit_forest_named_inr, dump_no_unit_plantation_category_inr
                                                         works that fall in no unit (`allocation_unassigned.csv`), by the
                                                         district of the file they came in: LEFT OUT of every dump column
                                                         above

need_vs_allocation.csv - long: one row per comparison and district
  comparison, pc11_district_code, district_name, in_comparison (no for a district C7 leaves out), need, need_unit,
  allocation, allocation_unit, need_share_pct, allocation_share_pct (shares of the districts in the comparison),
  r (allocation share / need share; blank with r_blank_because where need is zero), gap_lakh (need share x the
  comparison's total allocation - the district's allocation, in lakh rupees: "the same money distributed by need; not a
  requirement"). Shares, r and gap are blank for C12 (intensities) and B1 (a benchmark).

need_vs_allocation_summary.csv - one row per comparison
  n_districts, need_total, allocation_total, rho (Spearman, average ranks for ties), p_permutation (two-sided,
  99,999 shuffles of allocation against need), ci95_lo, ci95_hi (percentile bootstrap over districts, 9,999 draws),
  the seeds, need_share_pct_where_r_below_0_5, need_share_pct_where_r_above_2, n_districts_r_below_0_5,
  n_districts_r_above_2, n_districts_need_zero, sum_positive_gaps_lakh, and the comparison's definition in words.

The comparisons (fixed before any result was seen; C1 is the headline):
  C1  N1 2018_2025, all land                      v R6.20 plantation, post
  C2  N1 2018_2025, LGD-unit land only            v R6.20 plantation, post
  C3  N2                                           v R6.20 plantation, post
  C4  loss 2001-2013, all units                    v R6.20 plantation, pre
  C5  N1 2018_2025                                 v R6.20 plantation, pre
  C6  N1 2018_2025                                 v dump, forest-named, works started by FY2017-18
  C7  N1 2018_2025, districts with left_out_of_c7 = yes left out (need and money together) v plantation, post
  C7b the same under the other rule (left_out_under_the_other_rule): NOT one of the fixed comparisons; computed
      because the condition of the owner's rule was met neither way (docs/GAP.md lists it as a call he can overrule)
  C8  N1 2001_2025   C9  N1 2017_2023   C10  N1 2021_2025        each v R6.20 plantation, post
  C11 N1 2018_2025                                 v R6.20 plantation, FY2019-20 to 2025-26
  C12 N1 per 100 ha of the district's forest at window start v plantation as % of the district's own expenditure, post
  B1  N1 2018_2025                                 v R6.20 all expenditure, post (a benchmark: what size alone gives)

marginalisation_split.csv - for C1 and C4: within each st_class, adi_tercile and sc_tercile, the number of districts
  and the sums of need share and allocation share (and of need and allocation). LGD population only.

what_more.csv - for C1: one row per district and a row `state`
  n1_ha, r, r_below_1, r_below_0_5; n1_ha_where_r_below_1, n1_ha_where_r_below_0_5 (the district's N1 if its r is below
  the bound, else 0; summed in the state row); works_per_1000_ha_n1_fy2016_17, _fy2025_26 (an intensity, not a
  requirement: works have no standard size; blank where N1 is zero); cost_at_vgpp_rate_inr (blank) with
  cost_blank_because; scale_of_the_fall_lakh = the pre-period plantation share of all expenditure applied to the
  post-period total ("the size of the fall, measured by the scheme's own earlier share; not a measure of need; the
  earlier years are a frozen 2020 snapshot"), for the state from the state's unrounded ratio, for a district from its
  own (district rows do not add to the state row), beside plantation_post_actual_lakh.

Also written: `gates_phase2.csv` (the gates of this step) and this step's section of `gap.provenance.json` (inputs with
SHA-256, seeds, package versions, run time). The run stops after writing the gate table if a gate fails.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D, dsum  # noqa: E402

STEP = "08_build_gap_districts"
SEED = 20261010                                   # every seed of this step is SEED + a number fixed below
ZERO = Decimal(0)
GAP_LABEL = "the same money distributed by need; not a requirement"
SCALE_LABEL = ("the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier "
               "years are a frozen 2020 snapshot")
VGPP_BLANK = "VGPP ₹/ha not in 00_raw"
ZONES = {"ECPHR only": "east_coast_only_units", "EPAHR only": "eastern_plateau_only_units", "both models": "units_under_both_models",
         "": "units_with_no_zone"}
TERCILES_ADI = ["lowest third of the index", "middle third", "highest third of the index"]
TERCILES_SC = ["lowest third of Scheduled Caste share", "middle third", "highest third of Scheduled Caste share"]

# id, what the need is, what the allocation is, what it asks (the owner's table of 10 October 2026), kind
COMPARISONS = [
    ("C1", "N1, window 2018-2025, all land", "R6.20 plantation, post (FY2018-19 to 2025-26)",
     "In the years plantation fell out of the scheme, did what was left go where forest was being lost?", "comparison"),
    ("C2", "N1, 2018-2025, LGD-unit land only", "R6.20 plantation, post", "The same, for the land that panchayat planning can reach.", "comparison"),
    ("C3", "N2", "R6.20 plantation, post", "Did it go where open forest could regenerate?", "comparison"),
    ("C4", "total loss 2001-2013", "R6.20 plantation, pre (FY2014-15 to 2017-18; a frozen 2020 snapshot)", "Before the fall, did money go where loss had been?", "comparison"),
    ("C5", "N1, 2018-2025", "R6.20 plantation, pre (a frozen 2020 snapshot)", "Did the old geography of plantation money match where loss came next?", "comparison"),
    ("C6", "N1, 2018-2025", "dump, forest-named, works started by FY2017-18", "The same as C5, with the narrow forest-named measure.", "comparison"),
    ("C7", "N1, 2018-2025, East Coast districts left out", "R6.20 plantation, post, the same districts left out",
     "C1 without the zone the agreement headline leaves out.", "comparison"),
    ("C7b", "N1, 2018-2025, districts left out under the other reading of the rule", "R6.20 plantation, post, the same districts left out",
     "C7 under the other reading of its rule; not one of the fixed comparisons.", "comparison"),
    ("C8", "N1, window 2001-2025", "R6.20 plantation, post", "C1 under another window.", "comparison"),
    ("C9", "N1, window 2017-2023", "R6.20 plantation, post", "C1 under another window.", "comparison"),
    ("C10", "N1, window 2021-2025", "R6.20 plantation, post", "C1 under another window.", "comparison"),
    ("C11", "N1, 2018-2025", "R6.20 plantation, FY2019-20 to 2025-26", "C1 without FY2018-19, which alone is more than half of the post-period total.", "comparison"),
    ("C12", "N1 per 100 ha of the district's forest at window start", "plantation as a share of the district's own expenditure, post",
     "C1 with district size taken out of both sides.", "intensity"),
    ("B1", "N1, 2018-2025", "R6.20 all expenditure, post", "How much rank correlation district size alone produces. Read C1 against it.", "benchmark"),
]


def q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def pct(a: Decimal, b: Decimal, places: str = "0.000001"):
    return None if b == 0 else q(Decimal(100) * a / b, places)


def layer_classify():
    """`classify` of scripts/06_build_layer.py: the helper the layer's Scheduled Tribe classes are built on."""
    spec = importlib.util.spec_from_file_location("build_layer", G.IN["layer_builder"])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.classify


def st_class_index(share_pct: float, classify) -> int:
    """The layer's rule for a Scheduled Tribe share in per cent: the expression of `main()` of 06_build_layer.py.

    `np.where(np.round(st, 2) < 18, 0, 1 + classify(st, [33, 50]))`: under 18 is class 0; `classify` rounds to two
    decimals and gives 0 up to and including 33, 1 above 33 up to and including 50, 2 above 50."""
    if float(np.round(share_pct, 2)) < 18:
        return 0
    return 1 + int(classify([share_pct], [33, 50])[0])


def adi_direction() -> dict:
    """The sentences of the repository's documents that state which way the index runs. Stops if either is gone."""
    need_md = " ".join(G.IN["need_md"].read_text(encoding="utf-8").split())
    m = re.search(r"ADI is the sum of five indicators each ranked 1–3, so it runs 5–15", need_md)
    with zipfile.ZipFile(G.IN["adi_schema_docx"]) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    text = " ".join(re.sub(r"<[^>]+>", "", xml).split())
    d = re.search(r"rank each village at level-1 \(low\), level-2 \(medium\), or level-3 \(advance\) against these indicators", text)
    if not (m and d):
        G.stop("no document in the repository states the direction of the development index any longer: the ADI columns must be left out")
    return {"docs/NEED.md": m.group(0), "00_raw/docs/Village_level_dataset_schema_31Oct2022.docx": d.group(0),
            "reading": "each of five indicators is ranked 1 (low) to 3 (advance) and the index is their sum: higher is more developed"}


def adi_source_line() -> str:
    """The index's source and licence as the layer's own list of sources gives them, held against docs/DATA_NOTES.md."""
    text = (G.ROOT / "60_layer/data.js").read_text(encoding="utf-8")
    src = json.loads(text[text.index("{"):text.rindex("}") + 1])["sources_html"]
    row = re.search(r"<tr><td>(Aggregate Development Index 2011)</td><td>(.*?)</td><td>(.*?)</td></tr>", src, re.S)
    notes = " ".join(G.IN["data_notes"].read_text(encoding="utf-8").split())
    if not row or "The index's documentation says SHRUG's keys were used to link 2001 and 2011 villages" not in notes:
        G.stop("the development index's source and licence could not be read from the layer's sources and docs/DATA_NOTES.md")
    return f"{row.group(1)}: {row.group(2)}. Licence or terms: {row.group(3)}."


def terciles(codes: list[str], value: dict, labels: list[str]) -> dict:
    order = sorted(codes, key=lambda c: (value[c], c))
    if len(order) != 30:
        G.stop("terciles need 30 districts")
    return {c: labels[i // 10] for i, c in enumerate(order)}


def main() -> None:
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    inputs = {k: G.IN[k] for k in ("r620_district", "r620_state", "condition_by_unit", "hansen_bands", "agreement_by_unit",
                                    "need_by_unit", "allocation_by_unit_fy", "allocation_unassigned", "assets_district_fy",
                                    "tiers", "need_md", "adi_schema_docx", "data_notes", "layer_builder")}
    inputs["district_crosswalk"] = G.OUT / "district_crosswalk.csv"
    inputs["unit_district"] = G.OUT / "unit_district.csv"
    inputs["layer_by_unit"] = G.ROOT / "60_layer/layer_by_unit.csv"
    inputs["layer_data_js"] = G.ROOT / "60_layer/data.js"
    for p in inputs.values():
        if not p.exists():
            G.stop(f"an input is missing: {G.rel(p)} (run scripts/08_gap_inputs.py first)")

    cw = G.read_rows(inputs["district_crosswalk"])
    codes = [r["pc11_district_code"] for r in cw]
    name = {r["pc11_district_code"]: r["district_name"] for r in cw}
    r620_name = {r["pc11_district_code"]: r["r620_district"] for r in cw}
    code_of_r620 = {v: k for k, v in r620_name.items()}
    district = {r["unit_id"]: r["pc11_district_code"] for r in G.read_rows(inputs["unit_district"])}
    cond = G.read_rows(inputs["condition_by_unit"])
    if {r["unit_id"] for r in cond} != set(district):
        G.stop("the decision table and the unit-district table do not hold the same units")
    cell_names = {r["cell"]: r["cell_name"] for r in G.read_rows(inputs["tiers"])}
    zone = {r["unit_id"]: r["corestack_zone_model"] for r in G.read_rows(inputs["agreement_by_unit"])}
    assessed = {r["unit_id"]: r["assessed"] for r in G.read_rows(inputs["agreement_by_unit"])}
    if set(zone.values()) != set(ZONES):
        G.stop(f"the zone models are not the four expected: {sorted(set(zone.values()))}")

    # ------------------------------------------------------------------------------------------------ need by district
    N = {c: {} for c in codes}

    def acc(c, key, v):
        N[c][key] = N[c].get(key, ZERO if isinstance(v, Decimal) else 0) + v

    for r in cond:
        c, lgd = district[r["unit_id"]], r["outside_village"] == "0"
        kind = "_lgd" if lgd else "_outside"
        acc(c, "n_units", 1); acc(c, "n_units" + kind, 1)
        f2000 = D(r["dense_2000_ha"]) + D(r["open_2000_ha"])
        acc(c, "forest_2000_ha", f2000); acc(c, "forest_2000_ha" + kind, f2000)
        for w in G.WINDOWS:
            loss = D(r[f"forest_loss_ha_{w}"])
            acc(c, f"forest_loss_ha_{w}_all_units", loss)
            acc(c, f"forest_at_window_start_ha_{w}", D(r[f"forest_at_window_start_ha_{w}"]))
            in_loss_cell = r[f"cell_{w}"] in G.LOSS_CELLS
            acc(c, f"n1_ha_{w}", loss if in_loss_cell else ZERO)
            acc(c, f"n1_ha_{w}{kind}", loss if in_loss_cell else ZERO)
            acc(c, f"n_units_loss_cells_{w}", 1 if in_loss_cell else 0)
        anr = r[f"cell_{G.DEFAULT_WINDOW}"] == G.ANR_CELL
        so = D(r["standing_open_ha"]) if anr else ZERO
        acc(c, "n2_ha", so); acc(c, "n2_ha" + kind, so); acc(c, "n_units_anr", 1 if anr else 0)
        in_loss = r[f"cell_{G.DEFAULT_WINDOW}"] in G.LOSS_CELLS
        n1u = D(r[f"forest_loss_ha_{G.DEFAULT_WINDOW}"]) if in_loss else ZERO
        for z, label in ZONES.items():
            acc(c, f"n1_ha_2018_2025_in_{label}", n1u if zone[r["unit_id"]] == z else ZERO)
        acc(c, "n_assessed_units_east_coast_only", 1 if assessed[r["unit_id"]] == "1" and zone[r["unit_id"]] == "ECPHR only" else 0)
    for c in codes:
        for k in ("n_units_lgd", "n_units_outside"):
            N[c].setdefault(k, 0)
        for stem in ["forest_2000_ha", "n2_ha"] + [f"n1_ha_{w}" for w in G.WINDOWS]:
            for kind in ("_lgd", "_outside"):
                N[c].setdefault(stem + kind, ZERO)
        for w in G.WINDOWS:
            N[c][f"loss_below_minimum_ha_{w}"] = N[c][f"forest_loss_ha_{w}_all_units"] - N[c][f"n1_ha_{w}"]
    for r in G.read_rows(inputs["hansen_bands"]):
        acc(district[r["unit_id"]], "loss_2001_2013_ha",
            dsum(D(r[f"loss_ha_gt30_{y}"]) + D(r[f"loss_ha_gt10le30_{y}"]) for y in range(2001, 2014)))
    for c in codes:
        n1 = N[c]["n1_ha_2018_2025"]
        ec = N[c]["n1_ha_2018_2025_in_east_coast_only_units"]
        N[c]["east_coast_share_of_n1_pct"] = pct(ec, n1)
        N[c]["left_out_of_c7"] = "yes" if n1 > 0 and ec * 2 > n1 else "no"
        N[c]["left_out_under_the_other_rule"] = "yes" if N[c]["n_assessed_units_east_coast_only"] > 0 else "no"

    # marginalisation: LGD units only
    classify = layer_classify()
    need_rows = [r for r in G.read_rows(inputs["need_by_unit"]) if r["unit_level"] == "lgd_panchayat"]
    layer_class = {r["unit_id"]: r["class_st_share"] for r in G.read_rows(inputs["layer_by_unit"])}
    label_of, agree, with_share = {}, 0, 0
    for r in need_rows:
        if r["st_share"] == "":
            continue
        with_share += 1
        k = st_class_index(100.0 * float(r["st_share"]), classify)
        label_of.setdefault(k, set()).add(layer_class[r["unit_id"]])
    one_label = all(len(v) == 1 for v in label_of.values()) and sorted(label_of) == [0, 1, 2, 3]
    if one_label:
        st_label = {k: next(iter(v)) for k, v in label_of.items()}
        agree = sum(1 for r in need_rows if r["st_share"] != "" and
                    st_label[st_class_index(100.0 * float(r["st_share"]), classify)] == layer_class[r["unit_id"]])
    add("the Scheduled Tribe class rule used here gives, for every LGD unit that has a share, the class the layer shows for it "
        "(`class_st_share` of 60_layer/layer_by_unit.csv); units compared", with_share, agree, one_label and agree == with_share and with_share > 0)
    if not one_label:
        G.stop("the Scheduled Tribe class rule does not reproduce the layer's classes")
    for r in need_rows:
        c = district[r["unit_id"]]
        pop = int(r["population"])
        acc(c, "population_lgd", pop); acc(c, "st_pop_lgd", int(r["st_pop"])); acc(c, "sc_pop_lgd", int(r["sc_pop"]))
        if r["adi_2011"] != "":
            acc(c, "_adi_num", D(r["adi_2011"]) * pop); acc(c, "_adi_pop", pop); acc(c, "n_units_lgd_with_adi", 1)
    direction = adi_direction()
    source_line = adi_source_line()
    for c in codes:
        P = Decimal(N[c]["population_lgd"])
        N[c]["st_share_pct"] = pct(Decimal(N[c]["st_pop_lgd"]), P)
        N[c]["st_class"] = st_label[st_class_index(100.0 * N[c]["st_pop_lgd"] / N[c]["population_lgd"], classify)]
        N[c]["sc_share_pct"] = pct(Decimal(N[c]["sc_pop_lgd"]), P)
        N[c]["adi_2011"] = q(N[c]["_adi_num"] / Decimal(N[c]["_adi_pop"]), "0.000001")
        N[c]["adi_2011_population_covered_pct"] = pct(Decimal(N[c]["_adi_pop"]), P)
    adi_t = terciles(codes, {c: N[c]["_adi_num"] / Decimal(N[c]["_adi_pop"]) for c in codes}, TERCILES_ADI)
    sc_t = terciles(codes, {c: Decimal(N[c]["sc_pop_lgd"]) / Decimal(N[c]["population_lgd"]) for c in codes}, TERCILES_SC)
    for c in codes:
        N[c]["adi_tercile"], N[c]["sc_tercile"] = adi_t[c], sc_t[c]

    # ------------------------------------------------------------------------------------------ allocation by district
    A = {c: {} for c in codes}
    r620 = G.read_rows(inputs["r620_district"])
    state = G.read_rows(inputs["r620_state"])
    periods = {"pre": G.PRE, "post": G.POST, "part_year": [G.PART], "post_without_fy2018_19": G.POST_WITHOUT_FIRST}
    cat_key = {"Plantation": "plantation", "NRM": "nrm", "Water": "water"}
    seen_all = set()
    for r in r620:
        c = code_of_r620[r["district"]]
        for pname, fys in periods.items():
            if r["fy"] in fys:
                k = f"r620_{cat_key[r['category']]}_{pname}_lakh"
                A[c][k] = A[c].get(k, ZERO) + D(r["exp_cat_lakh"])
                if (r["fy"], r["district"], pname) not in seen_all:
                    seen_all.add((r["fy"], r["district"], pname))
                    k = f"r620_all_{pname}_lakh"
                    A[c][k] = A[c].get(k, ZERO) + D(r["exp_all_lakh"])
        if r["category"] == "Plantation" and r["fy"] in ("2016-2017", "2025-2026"):
            A[c][f"plantation_works_fy{G.fy_short(r['fy']).replace('-', '_')}"] = int(r["works_ongoing"]) + int(r["works_completed"])
    stamps = sorted({r["last_updated"] for r in state if r["fy"] in G.PRE})
    add("the stamp R6.20 prints on the four pre-period tables", G.FROZEN_STAMP, " / ".join(stamps), stamps == [G.FROZEN_STAMP])
    for c in codes:
        A[c]["plantation_pct_of_all_pre"] = pct(A[c]["r620_plantation_pre_lakh"], A[c]["r620_all_pre_lakh"])
        A[c]["plantation_pct_of_all_post"] = pct(A[c]["r620_plantation_post_lakh"], A[c]["r620_all_post_lakh"])
        A[c]["r620_pre_years_last_updated"] = stamps[0] if len(stamps) == 1 else ""
    dump_cols = {"forest_named": "expenditure_forest_named_worktype", "plantation_category": "expenditure_plantation_category"}
    units_with = {c: set() for c in codes}
    fn_all = fn_by = ZERO
    for r in G.read_rows(inputs["allocation_by_unit_fy"]):
        c = district[r["unit_id"]]
        fy = r["fy_work_start"]
        when = "start_year_missing" if fy == G.DUMP_NO_START else ("started_by_fy2017_18" if G.dump_fy_started_by(fy) else "started_later")
        for short, col in dump_cols.items():
            k = f"dump_{short}_{when}_inr"
            A[c][k] = A[c].get(k, ZERO) + G.money(r[col])
        v = G.money(r["expenditure_forest_named_worktype"])
        fn_all += v
        if when == "started_by_fy2017_18":
            fn_by += v
            if v > 0:
                units_with[c].add(r["unit_id"])
    file_code = {}
    for r in G.read_rows(inputs["assets_district_fy"]):
        file_code.setdefault(r["district_file"], set()).add(r["pc11_district_code"])
    if any(len(v) != 1 for v in file_code.values()) or len(file_code) != 30:
        G.stop("the dump's district files do not each name one census district")
    for r in G.read_rows(inputs["allocation_unassigned"]):
        c = next(iter(file_code[r["district_file"]]))
        for k, col in (("dump_no_unit_total_inr", "expenditure_total"), ("dump_no_unit_forest_named_inr", "expenditure_forest_named_worktype"),
                       ("dump_no_unit_plantation_category_inr", "expenditure_plantation_category")):
            A[c][k] = A[c].get(k, ZERO) + G.money(r[col])
    for c in codes:
        for short in dump_cols:
            for when in ("started_by_fy2017_18", "started_later", "start_year_missing"):
                A[c].setdefault(f"dump_{short}_{when}_inr", ZERO)
        for k in ("dump_no_unit_total_inr", "dump_no_unit_forest_named_inr", "dump_no_unit_plantation_category_inr"):
            A[c].setdefault(k, ZERO)
        A[c]["n_units_with_forest_named_by_fy2017_18"] = len(units_with[c])

    # ---------------------------------------------------------------------------------------------------------- gates
    tot = lambda table, k: dsum(table[c][k] for c in codes)
    add("districts", 30, len(codes), len(codes) == 30)
    add("N1, default window, summed over districts, ha (the three loss cells; within 2 of the owner's 89,657)", 89657,
        format(tot(N, "n1_ha_2018_2025"), "f"), abs(tot(N, "n1_ha_2018_2025") - 89657) <= 2)
    add("forest loss 2018-2025 over all units, summed over districts, ha (within 1 of 90,028)", 90028,
        format(tot(N, "forest_loss_ha_2018_2025_all_units"), "f"), abs(tot(N, "forest_loss_ha_2018_2025_all_units") - 90028) <= 1)
    add("N2, summed over districts, ha (within 1 of 293,921)", 293921, format(tot(N, "n2_ha"), "f"), abs(tot(N, "n2_ha") - 293921) <= 1)
    add("N1 of LGD-unit land plus N1 of outside-village land equals N1, every district and window", "yes",
        "yes" if all(N[c][f"n1_ha_{w}_lgd"] + N[c][f"n1_ha_{w}_outside"] == N[c][f"n1_ha_{w}"] for c in codes for w in G.WINDOWS) else "no",
        all(N[c][f"n1_ha_{w}_lgd"] + N[c][f"n1_ha_{w}_outside"] == N[c][f"n1_ha_{w}"] for c in codes for w in G.WINDOWS))
    for k, exp in (("r620_plantation_pre_lakh", "151843.18"), ("r620_plantation_post_lakh", "13915.72"), ("r620_plantation_part_year_lakh", "110.58"),
                   ("r620_nrm_pre_lakh", "327829.94"), ("r620_nrm_post_lakh", "2334964.06"), ("r620_all_pre_lakh", "750836.66"), ("r620_all_post_lakh", "3674731.26")):
        add(f"{k}, summed over districts (the gate of step 0)", exp, format(tot(A, k), "f"), tot(A, k) == Decimal(exp))
    first = dsum(D(r["exp_cat_lakh"]) for r in r620 if r["category"] == "Plantation" and r["fy"] == G.POST[0])
    share_first = Decimal(100) * first / tot(A, "r620_plantation_post_lakh")
    add("FY2018-19 as a per cent of post-period plantation expenditure (the owner's 53 per cent)", 53, format(q(share_first, "0.01"), "f"), q(share_first, "1") == 53)
    splits = all(A[c]["r620_plantation_post_lakh"] - A[c]["r620_plantation_post_without_fy2018_19_lakh"] ==
                 dsum(D(r["exp_cat_lakh"]) for r in r620 if r["category"] == "Plantation" and r["fy"] == G.POST[0] and code_of_r620[r["district"]] == c) for c in codes)
    add("FY2018-19 plus FY2019-20 to 2025-26 equals the post period, every district", "yes", "yes" if splits else "no", splits)
    no_unit = tot(A, "dump_no_unit_total_inr")
    add("works of the dump that fall in no unit, crore rupees (the owner's 73.8)", "73.8", format(q(no_unit / Decimal(10 ** 7), "0.1"), "f"),
        q(no_unit / Decimal(10 ** 7), "0.1") == Decimal("73.8"))
    share_by = Decimal(100) * fn_by / fn_all
    add("forest-named expenditure on works started by FY2017-18 as a per cent of all such expenditure in units, a missing start year counted "
        "as not started by then (the decision layer's 92.9)", "92.9", format(q(share_by, "0.1"), "f"), q(share_by, "0.1") == Decimal("92.9"))
    add("the dump's forest-named expenditure: by FY2017-18 + later + start year missing, summed over districts, equals the table's total", format(fn_all, "f"),
        format(tot(A, "dump_forest_named_started_by_fy2017_18_inr") + tot(A, "dump_forest_named_started_later_inr") + tot(A, "dump_forest_named_start_year_missing_inr"), "f"),
        tot(A, "dump_forest_named_started_by_fy2017_18_inr") + tot(A, "dump_forest_named_started_later_inr") + tot(A, "dump_forest_named_start_year_missing_inr") == fn_all)
    ratio = tot(A, "r620_plantation_pre_lakh") / tot(A, "r620_all_pre_lakh")
    scale = q(ratio * tot(A, "r620_all_post_lakh"), "0.01")
    add("the pre-period plantation share of all expenditure, per cent (the owner's 20.2232)", "20.2232", format(q(100 * ratio, "0.0001"), "f"), q(100 * ratio, "0.0001") == Decimal("20.2232"))
    add("that share applied to the post-period total, lakh (the owner's 743,148.16)", "743148.16", format(scale, "f"), scale == Decimal("743148.16"))
    pops = (sum(N[c]["population_lgd"] for c in codes), sum(N[c]["st_pop_lgd"] for c in codes))
    add("LGD population / Scheduled Tribe population, summed over districts", "34766888 / 8895006", f"{pops[0]} / {pops[1]}", pops == (34766888, 8895006))
    for label, t_ in (("ADI", adi_t), ("Scheduled Caste share", sc_t)):
        sizes = sorted(list(t_.values()).count(v) for v in set(t_.values()))
        add(f"districts in each tercile of {label}", "10 / 10 / 10", " / ".join(map(str, sizes)), sizes == [10, 10, 10])
    c7 = [name[c] for c in codes if N[c]["left_out_of_c7"] == "yes"]
    c7b = [name[c] for c in codes if N[c]["left_out_under_the_other_rule"] == "yes"]
    add("C7: districts left out (most of N1 in units wholly under the East Coast model) - listed, not a gate on a value", "a list", ", ".join(c7), len(c7) > 0)
    add("the other reading of the rule: districts that hold the East Coast units the agreement headline left out - listed", "a list", ", ".join(c7b), set(c7) <= set(c7b))
    add("N1 in units with no zone recorded, ha (so that the rule can be decided for every district)", "0", format(tot(N, "n1_ha_2018_2025_in_units_with_no_zone"), "f"),
        tot(N, "n1_ha_2018_2025_in_units_with_no_zone") == 0)
    excluded = sum(N[c]["n_assessed_units_east_coast_only"] for c in codes)
    add("units the agreement headline left out (assessed, wholly under the East Coast model), summed over districts", 468, excluded, excluded == 468)

    # ---------------------------------------------------------------------------------------------- comparisons
    def spec(cid):
        """(need by district, need unit, allocation by district, allocation unit, districts in the comparison)."""
        inn = list(codes)
        post = {c: A[c]["r620_plantation_post_lakh"] for c in codes}
        pre = {c: A[c]["r620_plantation_pre_lakh"] for c in codes}
        n1 = {c: N[c]["n1_ha_2018_2025"] for c in codes}
        if cid == "C1": return n1, "ha", post, "lakh", inn
        if cid == "C2": return {c: N[c]["n1_ha_2018_2025_lgd"] for c in codes}, "ha", post, "lakh", inn
        if cid == "C3": return {c: N[c]["n2_ha"] for c in codes}, "ha", post, "lakh", inn
        if cid == "C4": return {c: N[c]["loss_2001_2013_ha"] for c in codes}, "ha", pre, "lakh", inn
        if cid == "C5": return n1, "ha", pre, "lakh", inn
        if cid == "C6": return n1, "ha", {c: A[c]["dump_forest_named_started_by_fy2017_18_inr"] for c in codes}, "rupees", inn
        if cid == "C7": return n1, "ha", post, "lakh", [c for c in codes if N[c]["left_out_of_c7"] == "no"]
        if cid == "C7b": return n1, "ha", post, "lakh", [c for c in codes if N[c]["left_out_under_the_other_rule"] == "no"]
        if cid in ("C8", "C9", "C10"):
            w = {"C8": "2001_2025", "C9": "2017_2023", "C10": "2021_2025"}[cid]
            return {c: N[c][f"n1_ha_{w}"] for c in codes}, "ha", post, "lakh", inn
        if cid == "C11": return n1, "ha", {c: A[c]["r620_plantation_post_without_fy2018_19_lakh"] for c in codes}, "lakh", inn
        if cid == "C12":
            return ({c: Decimal(100) * N[c]["n1_ha_2018_2025"] / N[c]["forest_at_window_start_ha_2018_2025"] for c in codes}, "ha per 100 ha of forest at window start",
                    {c: Decimal(100) * A[c]["r620_plantation_post_lakh"] / A[c]["r620_all_post_lakh"] for c in codes}, "per cent of the district's own expenditure", inn)
        if cid == "B1": return n1, "ha", {c: A[c]["r620_all_post_lakh"] for c in codes}, "lakh", inn
        raise KeyError(cid)

    long_rows, summary_rows, seeds = [], [], {}
    C = {}
    for k, (cid, need_words, alloc_words, asks, kind) in enumerate(COMPARISONS):
        need, need_unit, alloc, alloc_unit, inn = spec(cid)
        tn, ta = dsum(need[c] for c in inn), dsum(alloc[c] for c in inn)
        to_lakh = G.LAKH if alloc_unit == "rupees" else Decimal(1)
        per = {}
        for c in codes:
            row = {"comparison": cid, "pc11_district_code": c, "district_name": name[c], "in_comparison": "yes" if c in inn else "no",
                   "need": q(need[c], "0.000001") if kind == "intensity" else need[c], "need_unit": need_unit,
                   "allocation": q(alloc[c], "0.000001") if kind == "intensity" else alloc[c], "allocation_unit": alloc_unit,
                   "need_share_pct": None, "allocation_share_pct": None, "r": None, "r_blank_because": "", "gap_lakh": None}
            if c not in inn:
                row["r_blank_because"] = "the district is left out of this comparison, need and money together"
            elif kind != "comparison":
                row["r_blank_because"] = "shares, r and gaps do not apply: " + ("the comparison is of intensities" if kind == "intensity" else "a benchmark")
            else:
                ns, as_ = need[c] / tn, alloc[c] / ta
                row["need_share_pct"], row["allocation_share_pct"] = q(100 * ns, "0.000001"), q(100 * as_, "0.000001")
                row["gap_lakh"] = q((ns * ta - alloc[c]) / to_lakh, "0.01")
                if need[c] == 0:
                    row["r_blank_because"] = "need is zero"
                else:
                    row["r"] = q(as_ / ns, "0.000001")
                per[c] = (ns, as_, None if need[c] == 0 else as_ / ns, (ns * ta - alloc[c]) / to_lakh)
            long_rows.append(row)
        s_perm, s_boot = SEED + 100 + k, SEED + 200 + k
        seeds[cid] = {"permutation": s_perm, "bootstrap": s_boot}
        st = G.spearman_with_inference([float(need[c]) for c in inn], [float(alloc[c]) for c in inn], s_perm, s_boot)
        srow = {"comparison": cid, "kind": kind, "need_is": need_words, "allocation_is": alloc_words, "what_it_asks": asks,
                "n_districts": len(inn), "districts_left_out": "; ".join(name[c] for c in codes if c not in inn),
                "need_total": q(tn, "0.000001") if kind == "intensity" else tn, "need_unit": need_unit,
                "allocation_total": q(ta, "0.000001") if kind == "intensity" else ta, "allocation_unit": alloc_unit,
                "rho": round(st["rho"], 6), "p_permutation": st["p_permutation"], "ci95_lo": round(st["ci95_lo"], 6), "ci95_hi": round(st["ci95_hi"], 6),
                "n_permutations": st["n_permutations"], "n_bootstrap": st["n_bootstrap"], "n_bootstrap_undefined": st["n_bootstrap_undefined"],
                "seed_permutation": s_perm, "seed_bootstrap": s_boot,
                "need_share_pct_where_r_below_0_5": None, "need_share_pct_where_r_above_2": None, "n_districts_r_below_0_5": None,
                "n_districts_r_above_2": None, "n_districts_need_zero": None, "sum_positive_gaps_lakh": None, "gap_is": ""}
        if kind == "comparison":
            lo = [c for c in per if per[c][2] is not None and per[c][2] < Decimal("0.5")]
            hi = [c for c in per if per[c][2] is not None and per[c][2] > 2]
            srow.update({"need_share_pct_where_r_below_0_5": q(100 * dsum(per[c][0] for c in lo), "0.000001"),
                         "need_share_pct_where_r_above_2": q(100 * dsum(per[c][0] for c in hi), "0.000001"),
                         "n_districts_r_below_0_5": len(lo), "n_districts_r_above_2": len(hi),
                         "n_districts_need_zero": sum(1 for c in per if per[c][2] is None),
                         "sum_positive_gaps_lakh": q(dsum(per[c][3] for c in per if per[c][3] > 0), "0.01"), "gap_is": GAP_LABEL})
            if tn == 0 or ta == 0 or abs(dsum(per[c][3] for c in per)) > Decimal("0.000001"):
                G.stop(f"{cid}: the gaps do not add to zero, or a total is zero")
        else:
            srow["sum_positive_gaps_lakh"] = None
        summary_rows.append(srow)
        C[cid] = (need, alloc, inn, per, tn, ta)
    if summary_rows[0]["need_unit"] != "ha":
        G.stop("C1 is not first")
    add("comparisons computed (the owner's thirteen and the second reading of C7)", len(COMPARISONS), len(summary_rows), len(summary_rows) == 14)

    # -------------------------------------------------------------------------------------- marginalisation splits
    split_rows = []
    groupings = (("st_class", [st_label[k] for k in sorted(st_label)]), ("adi_tercile", TERCILES_ADI), ("sc_tercile", TERCILES_SC))
    for cid in ("C1", "C4"):
        need, alloc, inn, per, tn, ta = C[cid]
        for gname, labels in groupings:
            for lab in labels:
                members = [c for c in inn if N[c][gname] == lab]
                split_rows.append({"comparison": cid, "grouping": gname, "class": lab, "n_districts": len(members),
                                   "districts": "; ".join(name[c] for c in members),
                                   "need": dsum(need[c] for c in members), "need_unit": "ha",
                                   "allocation_lakh": dsum(alloc[c] for c in members),
                                   "need_share_pct": q(100 * dsum(per[c][0] for c in members), "0.000001"),
                                   "allocation_share_pct": q(100 * dsum(per[c][1] for c in members), "0.000001"),
                                   "population_lgd": sum(N[c]["population_lgd"] for c in members),
                                   "note": "classes rest on the census population of LGD panchayat units only: outside-village land has no census rows"
                                           + ("; " + source_line if gname == "adi_tercile" else "")})
            n_in = sum(r["n_districts"] for r in split_rows if r["comparison"] == cid and r["grouping"] == gname)
            if n_in != 30:
                G.stop(f"{cid}, {gname}: the classes do not hold the 30 districts once each")

    # ------------------------------------------------------------------------------------------------ what more
    need, alloc, inn, per, tn, ta = C["C1"]
    what = []
    for c in codes:
        r_ = per[c][2]
        n1 = N[c]["n1_ha_2018_2025"]
        row = {"district": name[c], "pc11_district_code": c, "n1_ha": n1, "r": None if r_ is None else q(r_, "0.000001"),
               "r_below_1": "" if r_ is None else ("yes" if r_ < 1 else "no"), "r_below_0_5": "" if r_ is None else ("yes" if r_ < Decimal("0.5") else "no"),
               "n1_ha_where_r_below_1": n1 if r_ is not None and r_ < 1 else ZERO, "n1_ha_where_r_below_0_5": n1 if r_ is not None and r_ < Decimal("0.5") else ZERO,
               "plantation_works_fy2016_17": A[c]["plantation_works_fy2016_17"], "plantation_works_fy2025_26": A[c]["plantation_works_fy2025_26"],
               "works_per_1000_ha_n1_fy2016_17": None if n1 == 0 else q(Decimal(A[c]["plantation_works_fy2016_17"]) * 1000 / n1, "0.000001"),
               "works_per_1000_ha_n1_fy2025_26": None if n1 == 0 else q(Decimal(A[c]["plantation_works_fy2025_26"]) * 1000 / n1, "0.000001"),
               "works_intensity_is": "an intensity, not a requirement: works have no standard size" + ("" if n1 else "; blank: N1 is zero"),
               "cost_at_vgpp_rate_inr": None, "cost_blank_because": VGPP_BLANK,
               "scale_of_the_fall_lakh": q(A[c]["r620_plantation_pre_lakh"] / A[c]["r620_all_pre_lakh"] * A[c]["r620_all_post_lakh"], "0.01"),
               "plantation_post_actual_lakh": A[c]["r620_plantation_post_lakh"], "scale_is": SCALE_LABEL + "; a district's own shares: district rows do not add to the state row"}
        what.append(row)
    w16, w25 = sum(A[c]["plantation_works_fy2016_17"] for c in codes), sum(A[c]["plantation_works_fy2025_26"] for c in codes)
    what.append({"district": "state", "pc11_district_code": "", "n1_ha": tn, "r": None, "r_below_1": "", "r_below_0_5": "",
                 "n1_ha_where_r_below_1": dsum(r["n1_ha_where_r_below_1"] for r in what), "n1_ha_where_r_below_0_5": dsum(r["n1_ha_where_r_below_0_5"] for r in what),
                 "plantation_works_fy2016_17": w16, "plantation_works_fy2025_26": w25,
                 "works_per_1000_ha_n1_fy2016_17": q(Decimal(w16) * 1000 / tn, "0.000001"), "works_per_1000_ha_n1_fy2025_26": q(Decimal(w25) * 1000 / tn, "0.000001"),
                 "works_intensity_is": "an intensity, not a requirement: works have no standard size",
                 "cost_at_vgpp_rate_inr": None, "cost_blank_because": VGPP_BLANK, "scale_of_the_fall_lakh": scale,
                 "plantation_post_actual_lakh": tot(A, "r620_plantation_post_lakh"), "scale_is": SCALE_LABEL})
    add("plantation works, state, FY2016-17 / FY2025-26 (the gate of step 0)", "57135 / 4105", f"{w16} / {w25}", (w16, w25) == (57135, 4105))

    # ----------------------------------------------------------------------------------------------------- write
    need_cols = ["pc11_district_code", "district_name", "r620_district", "n_units", "n_units_lgd", "n_units_outside",
                 "forest_2000_ha", "forest_2000_ha_lgd", "forest_2000_ha_outside"]
    for w in G.WINDOWS:
        need_cols += [f"n1_ha_{w}", f"n1_ha_{w}_lgd", f"n1_ha_{w}_outside", f"n_units_loss_cells_{w}", f"forest_loss_ha_{w}_all_units",
                      f"loss_below_minimum_ha_{w}", f"forest_at_window_start_ha_{w}"]
    need_cols += ["n2_ha", "n2_ha_lgd", "n2_ha_outside", "n_units_anr", "loss_2001_2013_ha"]
    need_cols += [f"n1_ha_2018_2025_in_{v}" for v in ZONES.values()]
    need_cols += ["east_coast_share_of_n1_pct", "n_assessed_units_east_coast_only", "left_out_of_c7", "left_out_under_the_other_rule",
                  "population_lgd", "st_pop_lgd", "sc_pop_lgd", "st_share_pct", "st_class", "sc_share_pct", "sc_tercile",
                  "adi_2011", "adi_2011_population_covered_pct", "n_units_lgd_with_adi", "adi_tercile"]
    G.write_rows(G.OUT / "district_need.csv",
                 [dict(N[c], pc11_district_code=c, district_name=name[c], r620_district=r620_name[c]) for c in codes], need_cols)
    alloc_cols = ["pc11_district_code", "district_name", "r620_district"]
    for cat in ("plantation", "nrm", "water", "all"):
        alloc_cols += [f"r620_{cat}_pre_lakh", f"r620_{cat}_post_lakh", f"r620_{cat}_part_year_lakh"]
    alloc_cols += ["r620_plantation_post_without_fy2018_19_lakh", "plantation_pct_of_all_pre", "plantation_pct_of_all_post",
                   "plantation_works_fy2016_17", "plantation_works_fy2025_26", "r620_pre_years_last_updated"]
    for short in dump_cols:
        alloc_cols += [f"dump_{short}_started_by_fy2017_18_inr", f"dump_{short}_started_later_inr", f"dump_{short}_start_year_missing_inr"]
    alloc_cols += ["n_units_with_forest_named_by_fy2017_18", "dump_no_unit_total_inr", "dump_no_unit_forest_named_inr", "dump_no_unit_plantation_category_inr"]
    G.write_rows(G.OUT / "district_allocation.csv",
                 [dict(A[c], pc11_district_code=c, district_name=name[c], r620_district=r620_name[c]) for c in codes], alloc_cols)
    G.write_rows(G.OUT / "need_vs_allocation.csv", long_rows,
                 ["comparison", "pc11_district_code", "district_name", "in_comparison", "need", "need_unit", "allocation", "allocation_unit",
                  "need_share_pct", "allocation_share_pct", "r", "r_blank_because", "gap_lakh"])
    G.write_rows(G.OUT / "need_vs_allocation_summary.csv", summary_rows,
                 ["comparison", "kind", "need_is", "allocation_is", "what_it_asks", "n_districts", "districts_left_out", "need_total", "need_unit",
                  "allocation_total", "allocation_unit", "rho", "p_permutation", "ci95_lo", "ci95_hi", "n_permutations", "n_bootstrap",
                  "n_bootstrap_undefined", "seed_permutation", "seed_bootstrap", "need_share_pct_where_r_below_0_5", "need_share_pct_where_r_above_2",
                  "n_districts_r_below_0_5", "n_districts_r_above_2", "n_districts_need_zero", "sum_positive_gaps_lakh", "gap_is"])
    G.write_rows(G.OUT / "marginalisation_split.csv", split_rows,
                 ["comparison", "grouping", "class", "n_districts", "districts", "need", "need_unit", "allocation_lakh", "need_share_pct",
                  "allocation_share_pct", "population_lgd", "note"])
    G.write_rows(G.OUT / "what_more.csv", what,
                 ["district", "pc11_district_code", "n1_ha", "r", "r_below_1", "r_below_0_5", "n1_ha_where_r_below_1", "n1_ha_where_r_below_0_5",
                  "plantation_works_fy2016_17", "plantation_works_fy2025_26", "works_per_1000_ha_n1_fy2016_17", "works_per_1000_ha_n1_fy2025_26",
                  "works_intensity_is", "cost_at_vgpp_rate_inr", "cost_blank_because", "scale_of_the_fall_lakh", "plantation_post_actual_lakh", "scale_is"])
    rows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / "gates_phase2.csv", rows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("district_need.csv", "district_allocation.csv", "need_vs_allocation.csv", "need_vs_allocation_summary.csv",
                                   "marginalisation_split.csv", "what_more.csv", "gates_phase2.csv")]
    G.record_step(STEP, Path(__file__), inputs, outputs, {
        "seeds": {"base": SEED, "by_comparison": seeds, "generator": "numpy.random.default_rng"},
        "permutations": 99999, "bootstrap_resamples": 9999,
        "cell_names": {c: cell_names[c] for c in list(G.LOSS_CELLS) + [G.ANR_CELL]},
        "c7_rule": {"used": "a district is left out, need and money together, where units wholly under CoRE Stack's East Coast zone model "
                            "(`corestack_zone_model` = ECPHR only) hold more than half of its N1 of the default window; a district with no N1 stays in",
                    "districts_left_out": c7,
                    "why_this_reading": "the owner's rule had two branches: a zone recorded for every unit, or only for the units the agreement compared. "
                                        "The repository records the zone model for the units that have land the CoRE Stack classes on canopy above ten "
                                        "per cent, and the hectares under each model for every unit; the units with no zone model carry no N1, so the "
                                        "first branch can be decided for every district",
                    "other_reading": "the districts that hold the East Coast units the agreement headline left out", "districts_left_out_under_it": c7b},
        "st_classes": {"labels": [st_label[k] for k in sorted(st_label)], "rule_from": "scripts/06_build_layer.py: classify() and the expression of main()"},
        "adi": {"direction": direction, "source_and_licence": source_line},
        "gates": len(rows), "gates_passed": sum(r["pass"] == "yes" for r in rows)})
    for r in rows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in rows if r["pass"] != "yes"]
    print(f"\n{len(rows) - len(failed)} of {len(rows)} gates passed; wrote {', '.join(G.rel(p) for p in outputs)}")
    if failed:
        G.stop(f"{len(failed)} gate(s) failed; see 50_gap/gates_phase2.csv. Nothing downstream may run.")
    c1 = summary_rows[0]
    print(f"C1: rho {c1['rho']} ({c1['ci95_lo']} to {c1['ci95_hi']}), permutation p {c1['p_permutation']:.5f}; need in districts with r below 0.5: "
          f"{c1['need_share_pct_where_r_below_0_5']} %, above 2: {c1['need_share_pct_where_r_above_2']} %; sum of positive gaps {c1['sum_positive_gaps_lakh']} lakh")


if __name__ == "__main__":
    main()
