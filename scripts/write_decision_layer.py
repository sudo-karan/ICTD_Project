#!/usr/bin/env python3
"""Writes docs/DECISION_LAYER.md: what the decision view is, every threshold with its reason and its sensitivity, the
provisional order of tiers, and every caveat - for a reader who has followed none of it.

It is written to the standard of docs/RESULTS.md and with the same machinery: the functions of scripts/write_results.py
that read a figure and remember where it was read (cell, key, count, agg), and its gates, are imported and used as they
are. That file is not changed by this one. As there, the run stops if
  1. the text carries a digit of its own - outside code spans, dates, years and a short list of names;
  2. a figure is printed that was not defined, or defined and not printed;
  3. a conclusion the text draws from figures does not hold in them (hold());
  4. a total that two files both carry differs between them (same());
  5. one of the two verifiers fails (verify_layer.py, unchanged; verify_decision.py).
A figure that cannot be read is not written: a missing file, a missing key or a blank cell stops the run.

It does not run the browser checks: it reads their records in 60_layer/ and stops unless each is of the build that is
there. The two records of the checks made in the Safari application are allowed to be of another build when the runner's
record (60_layer/decision_runs.json) names those checks as not run in its pass, with a reason: they are then reported as
not run on this build, with the build they are of (see the section on verification). It also reads the gate on the
renaming of the cells (55_decision/rename_gate.json) and the records of the copy made to be passed on (70_share/), and
stops unless each is of the table and the layer on disk.

One group of figures has no stage output to come from: the independent replication of the decision table, whose record
is a working file of the session that made it (git-ignored). The appendix marks it.

Output: docs/DECISION_LAYER.md and nothing else; its inputs, their sha256 and the UTC time of the run are in its appendix.
  python scripts/write_decision_layer.py              runs the two verifiers, writes docs/DECISION_LAYER.md
  python scripts/write_decision_layer.py --draft p    skips the verifiers and writes to p instead (never into docs/)
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_results as W                      # its reading functions and gates, used as they are; importing it writes nothing

ROOT = W.ROOT
OUT = ROOT / "docs" / "DECISION_LAYER.md"
SCRATCH = W.SCRATCH
V, cell, key, count, agg, show, calc, hold, same, c, table = W.V, W.cell, W.key, W.count, W.agg, W.show, W.calc, W.hold, W.same, W.c, W.table
n0, dec, txt = W.n0, W.dec, W.txt


def stop(message):
    raise SystemExit("DECISION_LAYER not written: " + message)


W.stop = stop                                  # the reading functions say which document was not written


def words(v):                                  # a list of strings read from a file, printed as one
    return "; ".join(str(x) for x in v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", metavar="PATH", help="skip the verifiers and write here instead of docs/DECISION_LAYER.md")
    a = ap.parse_args()
    if a.draft and Path(a.draft).resolve().parent == OUT.parent:
        stop("a draft is never written into docs/")
    written = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    DOC = []

    DP = "55_decision/decision.provenance.json"
    CU = "55_decision/condition_by_unit.csv"
    CC = "55_decision/condition_cells.csv"
    CD = "55_decision/condition_cells_by_district.csv"
    CS = "55_decision/condition_sensitivity.csv"
    CB = "55_decision/condition_boundary.csv"
    CE = "55_decision/condition_threshold_evidence.csv"
    TI = "55_decision/tiers.csv"
    WT = "55_decision/work_types.csv"
    L = "60_layer/layer.provenance.json"
    AS = "20_degradation/agreement_summary.csv"
    AP = "20_degradation/agreement.provenance.json"
    BAND = "20_degradation/hansen_loss_by_canopy_band.csv"
    H = "20_degradation/hansen.provenance.json"
    R = "40_allocation/state_fy_r620_vs_dump.csv"
    ADF = "40_allocation/assets_district_fy.csv"
    AB = "40_allocation/allocation_by_unit.csv"
    A = "40_allocation/allocation.provenance.json"
    N = "30_need/need.provenance.json"
    MAN = "00_raw/data_manifest.csv"
    SP = "00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json"
    ST = "00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv"
    OV = "scripts/layer_overlay.json"
    EXC, EXW, EXS = "60_layer/exercise_chrome.json", "60_layer/exercise_webkit.json", "60_layer/exercise_safari.json"
    EDC, EDW, EDS = "60_layer/exercise_decision_chrome.json", "60_layer/exercise_decision_webkit.json", "60_layer/exercise_decision_safari.json"
    RP = SCRATCH + "/replicate_decision/final_comparison.json"
    RUNS = "60_layer/decision_runs.json"                                  # written by scripts/run_decision_checks.py: every run of every check on this build
    RUNS_FIRST = SCRATCH + "/decision_runs_2026-10-09_pass_with_a_step_by_hand.json"       # an earlier pass of the runner, kept as written with one note added by hand: a working file, of whatever build it says
    RUNS_OLD = SCRATCH + "/decision_runs_2026-10-08.json"                 # the runs on the build before this one, noted by hand: a working file
    TRIALS = SCRATCH + "/schedule_extract_trials_2026-10-09.json"
    PAGES = SCRATCH + "/overlay_pages_2026-10-08/"
    AZ = "20_degradation/agreement_by_zone.csv"
    BASE = "44890a1"                                                      # the commit this batch started from

    WINDOWS = [("2018_2025", "2018–2025"), ("2001_2025", "2001–2025"), ("2017_2023", "2017–2023"), ("2021_2025", "2021–2025")]
    DEFAULT = key(DP, "definitions/default_window").v
    hold(DEFAULT == WINDOWS[0][0] and [w for w, _ in WINDOWS] == list(W.J(DP)["definitions"]["windows"]), "the four windows of the table are the four named here, the first of them the default")
    CELLS = list(W.J(DP)["definitions"]["cells"])
    ORDER = list(W.J(DP)["tiers"]["order"])
    UNRANKED = key(DP, "tiers/unranked").v
    hold(sorted(ORDER + [UNRANKED]) == sorted(CELLS) and len(CELLS) == len(set(CELLS)), "the tier order names every cell but one, and that one is the cell left outside the ranked list")
    name = {x: cell(TI, "cell_name", cell=x) for x in CELLS}
    T = W.C(CU)
    CAUT = "00_raw/05_forest_reference/provider_cautions.json"                 # the providers' cautions about the data, registered on 9 October 2026
    SH = "55_decision/condition_share.csv"
    GATE = "55_decision/rename_gate.json"
    SHARE_REC, SHARE_EX = "70_share/share.provenance.json", "70_share/exercise_share_chrome.json"
    PAGE_DATA = W.use("60_layer/data.js").read_text(encoding="utf-8")
    LAYER_DATA = json.loads(PAGE_DATA[PAGE_DATA.index("{"):PAGE_DATA.rindex("}") + 1])
    ABOUT_PLAIN = " ".join(re.sub(r"<[^>]+>", "", LAYER_DATA["about_html"]).split())
    ABOUT_DV = ABOUT_PLAIN[ABOUT_PLAIN.index("Decision view: where is forest work warranted?"):]            # the decision view's part of the layer's About text
    STANDING_IS = "the forest of 2000 with no loss recorded since; not a measure of tree cover today"          # the owner's wording of 9 October 2026
    hold(key(DP, "definitions/standing").v.endswith(STANDING_IS) and "LOWER BOUND" not in key(DP, "definitions/standing").v and json.dumps(LAYER_DATA["decision"]).count("Standing forest is " + STANDING_IS) >= 2
         and STANDING_IS in ABOUT_DV and "lower bound" not in (json.dumps(LAYER_DATA["decision"]) + ABOUT_DV).lower(),
         "the decision table's record and the layer say of standing forest what the owner ruled, in his words, and the layer's decision view nowhere calls it a lower bound")
    show("standing_is", V(STANDING_IS, DP, "key `definitions` → `standing`: its closing words"), txt)
    show("pc_no_subtraction", key(CAUT, "sentences/cover_today_is_not_cover_of_2000_less_loss/text"), txt)
    show("pc_errors", key(CAUT, "sentences/errors/text"), txt)
    for nm_, k_ in (("pc_loss_is", "loss_is"), ("pc_not_deforestation", "loss_is_not_deforestation"), ("pc_two_halves", "two_halves_of_the_record"), ("pc_year", "year_of_loss"), ("pc_umd_loss", "umd_loss_is")):
        show(nm_, key(CAUT, f"sentences/{k_}/text"), txt)
    pc_fp = show("pc_fp", key(CAUT, "percentages_read_from_the_sentences/false_positives_pct"), n0)
    pc_fn = show("pc_fn", key(CAUT, "percentages_read_from_the_sentences/false_negatives_pct"), n0)
    hold(all(key(CAUT, f"sentences/{k_}/text").v in ABOUT_DV for k_ in ("cover_today_is_not_cover_of_2000_less_loss", "errors")),
         "the layer's About text quotes the provider's two cautions word for word from the registered record")
    # the gate on the renaming: every unit's cell, through the names
    hold(key(GATE, "table_now_sha256").v == W.sha256(W.use(CU)) and key(GATE, "assignments_that_do_not_match").v == 0 and key(GATE, "assignments_compared_units_x_windows").v == 4 * len(T)
         and key(GATE, "of_them_equal_as_text_in_every_row").v == key(GATE, "columns_the_table_had_before").v,
         "the gate on the renaming was run on the decision table that is on disk: every unit's cell in every window matches through the owner's list of names, and every column the table had is unchanged")
    show("gate_n", key(GATE, "assignments_compared_units_x_windows"), n0)
    show("gate_cols", key(GATE, "columns_the_table_had_before"), n0)
    show("gate_cells", key(GATE, "cells_compared_as_text"), n0)
    show("gate_new_cols", V(len(key(GATE, "columns_added_since_not_compared").v), GATE, "key `columns_added_since_not_compared`: their number"), n0)
    show("gate_before_sha", key(GATE, "table_before_is_the_one_ruled_on_sha256"), lambda x: f"`{x[:16]}`")

    # ==== 1. what this is ================================================================================================================
    show("written_utc", V(written, "this run", "the UTC time at which this script ran"), txt)
    run_d = show("run_decision", key(DP, "run_utc"), txt)
    run_l = show("run_layer", key(L, "run_utc"), txt)
    hold(key(L, "decision_view/table_run_utc").v == run_d.v, "the layer in `60_layer/` was built from the decision table that is in `55_decision/`")
    show("v_decision", W.verifier("verify_decision.py", a.draft), txt)
    show("v_layer", W.verifier("verify_layer.py", a.draft), txt)
    hold(not [p for p in (ROOT / "50_gap").glob("*") if p.name != ".gitkeep"] if (ROOT / "50_gap").exists() else True, "stage 4 is not built: `50_gap/` holds no output")
    n_units = show("n_units", key(DP, "counts/units"), n0)
    n_lgd = show("n_lgd", key(DP, "counts/by_level/lgd_panchayat"), n0)
    n_out = show("n_out", key(DP, "counts/by_level/outside_village"), n0)
    same("LGD panchayat units and outside-village units add up to the units", n_lgd.v + n_out.v, n_units.v)
    same("rows of the decision table, and the units", len(T), n_units.v)
    blank_cells = sum(int(T[f"cell_{w}"].isna().sum()) for w, _ in WINDOWS)
    hold(blank_cells == 0, "every unit has a cell in every window: no cell of the four cell columns is blank")
    show("n_tables", V(len(W.J(DP)["tables"]), DP, "key `tables`: the number of tables it lists"), n0)
    show("smin", key(DP, "thresholds/standing_min_ha"), n0)
    show("lmin", key(DP, "thresholds/loss_min_ha"), n0)
    floor = show("floor", key(L, "default_floor_ha"), n0)
    hold(key(DP, "thresholds/standing_min_ha").v != floor.v and key(DP, "thresholds/loss_min_ha").v != floor.v, "neither threshold of the decision view is the floor of the agreement test")

    DOC.append("""# The decision layer: where forest work is warranted

*Written {written_utc} by `scripts/write_decision_layer.py`. No figure in this document was typed: each was read from a
file, and §20 says which. It describes the decision table built {run_decision} and the layer built {run_layer}.*

## 1. What this is

The supervisor asked the project to "determine which areas have seen forest degradation, are also marginalised, and
have they seen good enough resource allocation in the past". Until now that was answered as measurement: two measures
of forest, a measure of need, a record of allocation (`docs/RESULTS.md`). The project owner now reads the request as
one for a **decision layer**: something a planner opens to see where forest work is warranted, comparable in purpose,
in his words, to the recharge-potential layer of CLART in Commons Connect.

This document describes that layer. Four things about it come first.

- **It is added; nothing is replaced.** The measurement stays exactly as it was. No file of `10_units/` to `50_gap/`
  and no existing column was changed. The new tables are in a new folder, `55_decision/` ({n_tables} tables, a run
  record and the record of a gate). The view is a new entry in the layer of `60_layer/`,
  beside the existing ones, which keep their behaviour and their defaults (§16 says how that was checked).
- **It is a way of reading the measurements, not a new measurement.** Each of the {n_units} units
  ({n_lgd} LGD panchayat units and {n_out} outside-village units) is placed in one of six cells by two questions put
  to Hansen's record: how much forest stands now, and is it mostly closed or mostly open; and was forest lost in a
  window of years. No unit is without a cell in any window. The cells are put in an order of tiers. That is all.
- **There is no score.** No index, no weights, no number out of a hundred. Need and past allocation are shown beside
  a unit's tier and are never folded into it (§10).
- **The owner ruled on it on 9 October 2026, and three things are still open.** He accepted the two thresholds as
  proposed ({smin} ha of standing forest; {lmin} ha of forest loss), renamed five of the six cells so that each name
  states its test, had the loss of the window shown also as a share of the forest, struck the words "lower bound",
  took one column out of the exported list, and had a copy of the layer made without the map overlay. Still open, for
  the Foundation for Ecological Security: the order of tiers (§8), which rows of the official list of works bear on
  which cell (§13), and whether Scheduled Tribe share appears in a list they pass on (§10). §17 gives every ruling and
  every open point.

Neither threshold is the {floor} ha floor of the agreement statistics. That floor stays what it was, for the purpose
it was set for, and the decision view does not use it.

Stage 4, the argument about why forest was lost or work withheld, is not built. Nothing here stands in for it.

The two verifiers were run by this script as it wrote the document: `scripts/verify_layer.py`, unchanged, gave
"{v_layer}"; `scripts/verify_decision.py`, new, gave "{v_decision}".
""")

    # ==== 2, 3. unit not pixel; the record ==============================================================================================
    def bd(col, band):
        return cell(BAND, col, units="all units", canopy_band=band)

    le10, eq0 = bd("loss_km2_2001_2025", "le10"), bd("loss_km2_2001_2025", "eq0")
    show("le10_loss", le10, dec(0))
    show("eq0_loss", eq0, dec(0))
    zs = calc("zero_share", 100 * eq0.v / le10.v, dec(0), "loss on land with no canopy in 2000 ÷ loss on land with `treecover2000 <= 10` × 100", [eq0, le10])
    hold(zs.v > 50, "most of the loss on the lowest band is on land with no canopy at all in 2000")
    p = [show(f"le10_p{i}", bd(col, "le10"), dec(0)) for i, col in enumerate(("loss_km2_2001_2010", "loss_km2_2011_2017", "loss_km2_2018_2025"), 1)]
    m = [show(f"gt30_p{i}", bd(col, "gt30"), dec(0)) for i, col in enumerate(("loss_km2_2001_2010", "loss_km2_2011_2017", "loss_km2_2018_2025"), 1)]
    hold(p[2].v / p[0].v > 3 * m[2].v / m[0].v, "loss on the lowest band rises across the three periods several times faster than loss in the forest mask")
    low_w = agg(CC, f"`loss_low_ha_in_window_reported_only` summed over the six cells, all units, window {DEFAULT}", lambda t: t.loc[(t.window == DEFAULT) & (t.units == "all units"), "loss_low_ha_in_window_reported_only"].sum())
    fl_w = agg(CC, f"`forest_loss_ha_in_window` summed over the six cells, all units, window {DEFAULT}", lambda t: t.loc[(t.window == DEFAULT) & (t.units == "all units"), "forest_loss_ha_in_window"].sum())
    show("low_loss_default", low_w, dec(0))
    show("forest_loss_default", fl_w, dec(0))

    # the reconciliation the owner asked for, made here again from the table itself
    HBU = "20_degradation/hansen_loss_by_canopy_band_by_unit.csv"

    def years_differ(band):
        def f(t_):
            cols_ = [c_ for c_ in t_.columns if re.fullmatch(rf"loss_ha_{band}_\d{{4}}", c_)]
            return (t_[cols_] * 10000).round().sum(axis=1) != (t_[f"loss_ha_{band}"] * 10000).round()
        return f
    show("ysum_dense", count(HBU, "rows whose yearly losses on the dense band (`loss_ha_gt30_<year>`) do not add to the table's own total `loss_ha_gt30`, at four decimals", years_differ("gt30")), n0)
    show("ysum_open", count(HBU, "rows whose yearly losses on the open band (`loss_ha_gt10le30_<year>`) do not add to the table's own total `loss_ha_gt10le30`, at four decimals", years_differ("gt10le30")), n0)
    show("ysum_gap", key(DP, "checks_passed/yearly_losses_against_the_tables_own_totals_largest_gap_ha"), dec(4))
    hold("the yearly losses add up to the table's own total (to 0.002 ha)" in W.use("scripts/05_build_decision.py").read_text(encoding="utf-8") and key(DP, "checks_passed/yearly_losses_against_the_tables_own_totals_largest_gap_ha").v <= 0.002,
         "the build's docstring gives the tolerance on the yearly sums, and the largest difference its run record carries is inside it")
    recon = W.J(DP)["checks_passed"]["totals_against_hansen_loss_by_canopy_band"]
    hold(len(recon) == 27 and all(abs(x["this_table_km2"] - x["hansen_loss_by_canopy_band_km2"]) <= 0.0051 for x in recon),
         "every total the decision stage compared with `hansen_loss_by_canopy_band.csv` equals it to the two decimals that table prints")
    show("recon_n", V(len(recon), DP, "key `checks_passed` → `totals_against_hansen_loss_by_canopy_band`: the number of totals compared"), n0)
    rows = []
    for band, col_area, col_stand, code in (("dense: `treecover2000 > 30`", "dense_2000_ha", "standing_dense_ha", "gt30"), ("open: `10 < treecover2000 <= 30`", "open_2000_ha", "standing_open_ha", "gt10le30")):
        area = agg(CU, f"`{col_area}` summed over all units, as km²", lambda t, k=col_area: t[k].sum() / 100)
        stand = agg(CU, f"`{col_stand}` summed over all units, as km²", lambda t, k=col_stand: t[k].sum() / 100)
        lost = agg(CU, f"`{col_area}` less `{col_stand}`, summed over all units, as km²", lambda t, k=col_area, s=col_stand: (t[k] - t[s]).sum() / 100)
        ref_area, ref_loss = bd("land_km2", code), bd("loss_km2_2001_2025", code)
        same(f"land in the {band.split(':')[0]} band in 2000: summed over the decision table, and in `hansen_loss_by_canopy_band.csv`", area.v, ref_area.v, 0.0051)
        same(f"loss on the {band.split(':')[0]} band, all years (land in 2000 less standing, summed over the decision table), and in `hansen_loss_by_canopy_band.csv`", lost.v, ref_loss.v, 0.0051)
        rows.append([band, c(stand, dec(2)), c(lost, dec(2)), c(area, dec(2)), c(ref_area, dec(2)), c(ref_loss, dec(2))])
    table("T_recon", ["band of canopy in the year 2000", "standing now, km²", "lost in all years, km²", "the two added: land in that year, km²", "that land in the band table, km²", "loss in the band table, km²"], rows)
    rx = "checks_passed/standing_plus_all_loss_against_the_band_hectares_per_unit/"
    de, dn, oe, on = (show(nm, key(DP, rx + k), n0) for nm, k in (("recon_dense_exact", "dense/units_exact"), ("recon_dense_not", "dense/units_not_exact"), ("recon_open_exact", "open/units_exact"), ("recon_open_not", "open/units_not_exact")))
    same("units where the dense band adds up exactly and units where it does not, and the units", de.v + dn.v, n_units.v)
    same("units where the open band adds up exactly and units where it does not, and the units", oe.v + on.v, n_units.v)
    gap = show("recon_gap", key(DP, rx + "dense/largest_gap_ha"), dec(4))
    hold(max(gap.v, key(DP, rx + "open/largest_gap_ha").v) <= 0.0001 + 1e-12, "where a band does not add up exactly the gap is one ten-thousandth of a hectare")
    hold("the file as written" in key(DP, "checks_passed/that_identity_was_tested_on").v, "the build tested the identity on the file as written, read back")
    for band_ in ("dense", "open"):                               # and once more here, on the table as this script reads it
        g_ = ((T[f"standing_{band_}_ha"] + T[f"loss_{band_}_ha_2001_2025"] - T[f"{band_}_2000_ha"]) * 10000).round().astype(int)
        same(f"units where standing plus loss 2001-2025 is exactly the year-2000 {band_} band: counted here on the table, and in the run record", int((g_ == 0).sum()), key(DP, rx + f"{band_}/units_exact").v)
        hold(int(g_.abs().max()) <= 1 and bool((g_ >= 0).all()), f"on the table as read here, standing plus loss 2001-2025 never differs from the year-2000 {band_} band by more than one ten-thousandth of a hectare")
    pp = "checks_passed/printed_parts_add_to_a_threshold_the_printed_total_is_under/"
    show("parts_standing", key(DP, pp + "units_standing"), n0)
    show("parts_loss", key(DP, pp + "unit_windows_loss"), n0)
    cz = "checks_passed/standing_set_to_zero_where_the_sources_rounding_put_it_below/"
    same("units whose standing dense was set to zero, and units where the dense band does not add up exactly", key(DP, cz + "dense/units").v, dn.v)
    same("units whose standing open was set to zero, and units where the open band does not add up exactly", key(DP, cz + "open/units").v, on.v)
    pr = "checks_passed/the_printing_rule_against_half_up_on_the_decimal_figure/"
    show("print_cells", key(DP, pr + "hectare_cells_that_would_print_differently"), n0)
    hold(key(DP, pr + "unit_windows_whose_cell_would_differ").v == 0, "no unit's cell, in any window, depends on which of the two rounding rules is used")
    fd = "checks_passed/read_at_four_decimals_and_not_as_printed/"
    show("tie_units", key(DP, fd + "units_mostly_dense_whose_standing_open_is_larger_in_the_fourth_decimal"), n0)
    show("edge_units", key(DP, fd + "unit_windows_with_some_loss_and_under_the_threshold_in_the_fourth_decimal"), n0)
    show("cu_cols", key(DP, "tables/condition_by_unit.csv/columns"), n0)
    bl = W.J(DP)["tables"]["condition_by_unit.csv"]["blank_cells"]
    share_blank = {f"forest_loss_share_pct_{w}" for w, _ in WINDOWS} | {f"forest_loss_share_blank_because_{w}" for w, _ in WINDOWS}
    hold(set(bl) == {"unit_name", "dense_open_ratio", "tier_provisional_2018_2025", "district_check", "governance_prompt"} | share_blank
         and all(bl[f"forest_loss_share_pct_{w}"] + bl[f"forest_loss_share_blank_because_{w}"] == len(T) for w, _ in WINDOWS),
         "the decision table is blank in five columns and, for each window, in the share where none is given and in the share's reason where one is: in every unit and window exactly one of those two is blank")
    show("blank_name", key(DP, "tables/condition_by_unit.csv/blank_cells/unit_name"), n0)
    show("blank_ratio", key(DP, "tables/condition_by_unit.csv/blank_cells/dense_open_ratio"), n0)
    same("units with no tier in the default window, and units in the cell left outside the ranked list", bl["tier_provisional_2018_2025"], cell(CC, "n_units", window=DEFAULT, units="all units", cell=UNRANKED).v)
    same("units with no district check and no governance prompt, and LGD panchayat units", bl["district_check"], n_lgd.v)
    same("units with no governance prompt, and LGD panchayat units", bl["governance_prompt"], n_lgd.v)
    hansen_ds = next(x["earth_engine_dataset"] for x in W.J(H)["inputs"] if "earth_engine_dataset" in x)
    show("hansen_dataset", V(hansen_ds, H, "key `inputs`: the Earth Engine dataset it names"), txt)

    DOC.append("""
## 2. Why a unit and not a pixel

Hansen's loss is stand-replacing: a pixel is recorded as lost when its tree cover is cleared - by the definition in
the provider's record of the data, when at least half of it is (§18). So at the level of a pixel there is "standing"
and there is "lost", and "dense and losing" cannot be shown. The owner put it more strongly, "every lost pixel is bare
by construction"; the source bears out the weaker form, and the conclusion is the same. A place can be both only as an
area: this much closed forest standing, this much lost. Each unit is therefore classed from its hectares, and the
hectares are kept. The cell is a summary of them, and a unit's panel shows them all (§15).

## 3. The record behind every cell

`55_decision/condition_by_unit.csv` has one row for each of the {n_units} units and {cu_cols} columns. Before any
cell, it records, from Hansen ({hansen_dataset}, as tabulated by stage 1, by band of canopy in the year 2000):

- **standing dense** hectares: land with `treecover2000 > 30`, less all loss Hansen records on it through 2025;
- **standing open** hectares: land with `10 < treecover2000 <= 30`, less all loss on it;
- **forest loss** in each window, split by the band the forest was in: lost from dense, lost from open;
- **loss on land with `treecover2000 <= 10`** in each window. It is reported, and it decides nothing.

**"Standing" is always now**, through 2025, whatever window is chosen. **It is {standing_is}.** That is the wording
the owner ruled on 9 October 2026, and it is what the table's run record says and what the layer says in the legend,
in every unit's panel and under the ranked list.

**Until that ruling it was called a lower bound, and it is not strictly one in either direction.** It is too low
where forest grew: Hansen does not net off gain, so land that lost its cover and grew it back, and land that has
gained cover since 2000, is not in it. And recorded loss is itself uncertain both ways. The provider's record of the
data, registered in `00_raw/` (§14), says in its own words: "{pc_no_subtraction}" and "{pc_errors}" With missed loss
at about {pc_fn} per cent the subtraction leaves in forest that was lost; with false loss at about {pc_fp} per cent
it takes out forest that was not. So the words "lower bound" were taken out of the layer, the tables' record and this
document, and the reason is kept here. The split into dense and open is that of 2000: a stand that has thinned since is still
"dense" here. And the provider of the data cautions against reading the subtraction as present cover (§18).

**Why the lowest band decides nothing.** `docs/RESULTS.md` §3.1: of the {le10_loss} km² of loss recorded on land with
`treecover2000 <= 10`, {eq0_loss} km², {zero_share} per cent, is on land with no canopy at all in 2000. That is tree
cover that grew after 2000 and was removed, or an artefact of detection; it is not forest that stood in 2000. And its
rise over time is largely the producers' change of method: it goes {le10_p1}, {le10_p2}, {le10_p3} km² across
2001–2010, 2011–2017 and 2018–2025, while loss on the dense band (canopy above thirty per cent: the "forest mask" of
`docs/RESULTS.md`) goes {gt30_p1}, {gt30_p2}, {gt30_p3}. In the default
window that band carries {low_loss_default} ha of recorded loss against {forest_loss_default} ha of forest loss. Had it
been let into the classification it would have moved many units for a reason that is not about forest.

**The table reconciles with the stage it is built from.** The owner set one condition: standing plus lost hectares in
each band must equal that band's hectares in the year 2000, for each unit and in total, against
`20_degradation/hansen_loss_by_canopy_band.csv`. This script made the comparison again from the table itself:

{T_recon}

*n = {n_units} units; no unit is missing from either band. The band table prints two decimals of a square kilometre,
and the totals agree to that.* The build made {recon_n} such comparisons (three bands, three kinds of unit, land and
two spans of loss) and stops if one fails.

For each unit: the dense band adds up exactly in {recon_dense_exact} units and the open band in {recon_open_exact}.
The build makes this test on the file it has written, read back as text, and this script made it again. In
{recon_dense_not} units for dense and {recon_open_not} for open the band does not add up, by {recon_gap} ha, a square metre:
the source rounds each year's loss and the band's area to four decimals separately, so the years can add to a hair
more than the land. There, standing is set to zero and not left negative. **This is the one place where the identity
the owner asked for holds to a tolerance and not exactly**, and the run record counts the units.

One more thing rests on the same rounding, and it is not the identity. Stage 1's table prints for each unit and band
both the loss of each year and its own total over the whole record. "Lost" in this table is the sum of the years, the
only figure that can be cut into windows. That sum is not the source's own total in {ysum_dense} units for dense and
{ysum_open} for open, by at most {ysum_gap} ha. The build compares the two in every unit and stops beyond a tolerance
that its docstring gives (`0.002 ha`). So against stage 1's own total of all loss, standing is exact to that
tolerance and not to the last digit.

**How figures are compared with a threshold.** Hectares are added and subtracted as whole ten-thousandths, so every
hectare in the table is exact. A threshold is then compared with the figure as the map prints it, to two decimals, by
the rule that prints every other hectare on the map (`format(x, ".2f")`). So a unit's cell never contradicts the
hectares printed beside it. The other common rule, half up, would print {print_cells} of the hectare figures of land, standing forest and loss
(the two hectare columns copied from the agreement test are not in that count) differently in the last digit, and would change the cell of no unit in any window. Read at four decimals and not as
printed, {tie_units} units are mostly dense though their standing open is larger in the fourth decimal, and in
{edge_units} cases a loss counts as some though its fourth decimal is under the threshold. One more oddity of printing:
a total is rounded as a total, so in {parts_standing} unit the two printed parts of standing forest add up to the
threshold while the printed total is a hundredth under it, and in {parts_loss} cases the same happens to a loss. The
cell follows the printed total.

**What is blank in the table, and why.** `unit_name` in {blank_name} units that have no name; `dense_open_ratio` in
{blank_ratio} units with no standing forest in either band; the tier in the units of the cell that is outside the
ranked list; the district check and the governance prompt in the {n_lgd} LGD panchayat units, which they do not
concern; and, in each window, the share of the units that have none, whose reason is then given in words in the
column beside it, which is blank wherever a share is given (§5.4). No hectare and no cell is blank.
""")

    # ==== 4. the windows ================================================================================================================
    def nc(w, x, units="all units", col="n_units"):
        return cell(CC, col, window=w, units=units, cell=x)

    wrows = []
    for w, label in WINDOWS:
        per = [nc(w, x) for x in CELLS]
        same(f"units in the six cells of window {w}, and the units", sum(v.v for v in per), n_units.v)
        other = count(CU, f"rows whose `cell_{w}` differs from `cell_{DEFAULT}`", lambda t, w=w: t[f"cell_{w}"] != t[f"cell_{DEFAULT}"])
        wrows.append([label, c(key(DP, f"definitions/windows/{w}/is"), txt)] + [c(v, n0) for v in per] + [c(other, n0) if w != DEFAULT else "-"])
    table("T_windows", ["window", "what it is"] + [name[x].v for x in CELLS] + ["units in another cell than in the default window"], wrows)

    def rr(col, fy):
        return cell(R, col, fy=fy)

    pl16 = show("pl_1617", rr("r620_plantation_share_pct", "2016-17"), dec(1))
    pl18 = show("pl_1819", rr("r620_plantation_share_pct", "2018-19"), dec(1))
    hold(pl18.v < pl16.v / 2, "plantation's share of expenditure in the state report more than halves between FY2016-17 and FY2018-19")
    later = W.C(R).loc[W.C(R).fy > "2018-19", "r620_plantation_share_pct"]
    hold(bool((later < 1).all()), "plantation's share of expenditure in the state report is under one per cent in every year after FY2018-19")
    show("upd_1617", rr("r620_last_updated", "2016-17"), txt)
    same("plantation's share in FY2016-17: in the state report's table and in the decision stage's evidence table", round(pl16.v, 1), cell(CE, "value", key="plantation_share_fy2016_17").v)
    same("plantation's share in FY2018-19: in the state report's table and in the decision stage's evidence table", round(pl18.v, 1), cell(CE, "value", key="plantation_share_fy2018_19").v)
    hold("state report" in key(DP, f"definitions/windows/{DEFAULT}/is").v, "the default window's reason, as the layer shows it, names the state report it rests on")
    full_ol = show("full_ol", count(CU, "rows whose `cell_2001_2025` is open_loss", lambda t: t.cell_2001_2025 == "open_loss"), n0)
    full_quiet = show("full_quiet", count(CU, f"rows whose `cell_2001_2025` is open_loss and whose `forest_loss_ha_{DEFAULT}`, as printed, is under the loss minimum", lambda t: (t.cell_2001_2025 == "open_loss") & (t[f"forest_loss_ha_{DEFAULT}"].round(2) < key(DP, "thresholds/loss_min_ha").v)), n0)
    same("units of the cell of open forest with loss under the full record that lost under the minimum in the default window: counted here, and in the layer's record of its About text", full_quiet.v, key(L, "decision_view/figures_in_the_about_text/of_them_under_the_loss_minimum_in_the_default_window").v)

    DOC.append("""
## 4. The four windows

Loss is counted over a window of years, and the window is a choice. There are four, each with its own cell for every
unit. The layer opens on the first.

{T_windows}

*n = {n_units} units in every row; each unit is in exactly one cell of each window.*

**Why 2018–2025 is the default.** It is the regime after plantation fell out of the scheme's spending. In the state's
own report (MIS report R6.20, `40_allocation/state_fy_r620_vs_dump.csv`), plantation is {pl_1617} per cent of
expenditure in FY2016-17 and {pl_1819} per cent in FY2018-19, and under one per cent in every later year. The decision
stage reads those two shares and stops if the second is not under half the first. Three
caveats come with that reason; the first and the third are from `docs/RESULTS.md` §8, the second is this document's. The high-plantation years of that report are a snapshot
frozen long ago (the row for FY2016-17 carries the stamp {upd_1617}). A financial year runs from April, and Hansen's
years are calendar years, so the window and the regime do not start on the same day. And why plantation fell is not
something these tables can say. The owner confirmed this window as the default, with these three caveats, on
9 October 2026 (§17).

**A cell's name speaks of loss recorded in the window chosen.** Under the full record that is at any time since 2001:
of the {full_ol} units in "{open_loss_name}" under 2001–2025, {full_quiet} lost under {lmin} ha in 2018–2025. The
layer's About text says so.

**The window is named wherever a cell is shown**: in the legend's title, in every unit's panel, at the head of the
ranked list and in every row of an exported list (§15). The corroboration badge carries its own window, 2017–2023,
whatever window is chosen (§11).
""")

    # ==== 5. the two thresholds ===========================================================================================================
    def ev(k, col="value", blank_ok=False):
        return cell(CE, col, blank_ok=blank_ok, key=k)

    s_alt = [key(DP, "thresholds/alternatives/standing_min_ha/0"), key(DP, "thresholds/standing_min_ha"), key(DP, "thresholds/alternatives/standing_min_ha/1")]
    l_alt = [key(DP, "thresholds/alternatives/loss_min_ha/0"), key(DP, "thresholds/loss_min_ha"), key(DP, "thresholds/alternatives/loss_min_ha/1")]
    hold(s_alt[0].v < s_alt[1].v < s_alt[2].v and l_alt[0].v < l_alt[1].v < l_alt[2].v, "each proposal has one alternative below it and one above")
    g = lambda v: (f"{v.v:g}", [v])              # a threshold as its file writes it
    show("smin_lo", s_alt[0], lambda x: f"{x:g}")
    show("smin_hi", s_alt[2], lambda x: f"{x:g}")
    show("lmin_lo", l_alt[0], lambda x: f"{x:g}")
    show("lmin_hi", l_alt[2], lambda x: f"{x:g}")
    px = show("pixel_ha", ev("pixel_ha"), dec(4))
    same("the area of a pixel in the evidence table and in the run record", px.v, key(DP, "thresholds/pixel_ha").v)
    hold(show("px_in_lmin", ev(f"pixels_in_loss_{l_alt[1].v:g}"), dec(1)).v > 12, "the proposed loss minimum is more than a dozen pixels")
    show("fsi_min", ev("fsi_min_patch_ha"), n0)
    isfr = "00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt"
    hold("more than or equal to one hectare in area" in " ".join(W.use(isfr).read_text(encoding="utf-8").split()), f"the Forest Survey's wording on its smallest patch is in `{isfr}`")
    grid_step = next(x["grid"]["transform"][0] for x in W.J(H)["inputs"] if "earth_engine_dataset" in x)
    hold(grid_step < 1 and next(x["grid"]["crs"] for x in W.J(H)["inputs"] if "earth_engine_dataset" in x) == "EPSG:4326", "Hansen's grid is in degrees, so the ground area of a pixel shrinks towards the north")
    table("T_small", ["window", "units with forest loss above zero and under the area of the pixel in the middle of the state", "units with forest loss from that area to under the loss minimum"],
          [[label, c(ev(f"under_mid_pixel_{w}"), n0), c(ev(f"mid_pixel_to_loss_min_{w}"), n0)] for w, label in WINDOWS])
    one_px = show("one_px", ev(f"under_mid_pixel_{DEFAULT}"), n0)
    hold(all(ev(f"under_mid_pixel_{w}").v > 100 for w, _ in WINDOWS), "in every window more than a hundred units have a forest loss above zero and under the area of the mid-state pixel")
    same("units with a loss above zero and under the area of the pixel in the middle of the state, in the evidence table and counted here in the decision table", one_px.v, int(((T[f"forest_loss_ha_{DEFAULT}"] > 0) & (T[f"forest_loss_ha_{DEFAULT}"] < px.v)).sum()))
    same("that count in the evidence table and in the layer's record of its About text", one_px.v, key(L, "decision_view/figures_in_the_about_text/units_with_loss_under_the_mid_state_pixel_default_window").v)

    def rec(s, l, col="value"):
        return ev(f"recur_{s.v:g}_{l.v:g}", col)

    def fresh(s, col="value"):
        return ev(f"fresh_{s.v:g}", col)

    pn = lambda share, n: (f"{dec(1)(share.v)} (n = {n0(n.v)})", [share, n])
    table("T_recur", ["standing forest of at least, ha", "lost at least the lower alternative, and again", "lost at least the proposal, and again", "lost at least the higher alternative, and again", "lost under the mid-state pixel's area, or nothing, then the proposal or more"],
          [[g(s)] + [pn(rec(s, l), rec(s, l, "n")) for l in l_alt] + [pn(fresh(s), fresh(s, "n"))] for s in s_alt])
    r_all = [rec(s_alt[1], l).v for l in l_alt]
    hold(max(r_all) - min(r_all) < 2, "at the proposed standing minimum, the recurrence of loss is within two points whichever of the three loss minimums is used")
    hold(all(rec(s, l).v > 85 for s in s_alt for l in l_alt) and all(fresh(s).v < 10 for s in s_alt), "loss recurs in more than eighty-five per cent of units at every setting, and starts afresh in under ten per cent")
    show("recur", rec(s_alt[1], l_alt[1]), dec(1))
    show("recur_n", rec(s_alt[1], l_alt[1], "n"), n0)
    show("fresh", fresh(s_alt[1]), dec(1))
    show("fresh_n", fresh(s_alt[1], "n"), n0)

    # an absolute minimum follows the size of the forest
    SIZES = (("ten to twenty-five", "10"), ("twenty-five to fifty", "25"), ("fifty to a hundred", "50"), ("a hundred to two hundred and fifty", "100"), ("two hundred and fifty to five hundred", "250"), ("five hundred to a thousand", "500"),
             ("a thousand to five thousand", "1000"), ("five thousand or more", "5000"))
    table("T_size", ["standing forest in the unit, ha", "forest-site units", "of them with some loss in the default window, %", "of those that lost the loss minimum or more in the first half of the window, the share that did again in the second, %",
                     "of those that lost under the mid-state pixel's area, or nothing, in the first half, the share that lost the loss minimum or more in the second, %"],
          [[lab, c(ev(f"some_loss_share_{k}", "n"), n0), c(ev(f"some_loss_share_{k}"), dec(1)), pn(ev(f"recur_size_{k}"), ev(f"recur_size_{k}", "n")), pn(ev(f"fresh_size_{k}"), ev(f"fresh_size_{k}", "n"))] for lab, k in SIZES])
    rs = [ev(f"recur_size_{k}").v for _, k in SIZES]
    hold(rs[0] < min(rs[4:]) and all(x > 90 for x in rs[4:]), "loss recurs less often among the smallest forest sites than among those with two hundred and fifty hectares or more, where it recurs in more than nine cases in ten")
    show("recur_small", ev("recur_size_10"), dec(0))
    show("recur_small_n", ev("recur_size_10", "n"), n0)
    big_n = show("big_n", ev("some_loss_share_5000", "n"), n0)
    big_loss = show("big_loss_n", count(CU, f"rows whose `standing_forest_ha`, as printed, is five thousand or more and whose `cell_{DEFAULT}` is a cell with loss", lambda t_: (t_.standing_forest_ha.round(2) >= 5000) & t_[f"cell_{DEFAULT}"].isin(["dense_loss", "open_loss"])), n0)
    same("units with five thousand hectares or more: in the evidence table and counted here", big_n.v, int((T.standing_forest_ha.round(2) >= 5000).sum()))
    top = T.loc[T.groupby("district").standing_forest_ha.idxmax()]
    show("dist_top_loss", V(int(top[f"cell_{DEFAULT}"].isin(["dense_loss", "open_loss", "little_loss"]).sum()), CU, f"districts whose row with the largest `standing_forest_ha` has a `cell_{DEFAULT}` with loss"), n0)
    same("forest-site units over the eight size classes, and the forest-site units", sum(ev(f"some_loss_share_{k}", "n").v for _, k in SIZES), ev(f"units_standing_{s_alt[1].v:g}").v)
    sz = [ev(f"some_loss_share_{k}").v for _, k in SIZES]
    hold(all(x < y for x, y in zip(sz, sz[1:])), "the share of units with some loss rises with every step up in the size of their standing forest")
    show("size_lo", ev("some_loss_share_10"), dec(0))
    show("size_hi", ev("some_loss_share_5000"), dec(0))
    dl1 = show("dl_under_1pct", ev("dense_loss_under_1pct"), n0)
    show("dl_under_01pct", ev("dense_loss_under_01pct"), n0)
    same("units in the cell with closed forest and loss: in the evidence table and in the table of cells", ev("dense_loss_under_1pct", "n").v, cell(CC, "n_units", window=DEFAULT, units="all units", cell="dense_loss").v)
    show("none_over_2pct", ev("none_cell_over_2pct"), n0)
    big = T.loc[T[f"cell_{DEFAULT}"] == "dense_loss"].assign(share=lambda d: d[f"forest_loss_ha_{DEFAULT}"] / d["standing_forest_ha"]).sort_values("standing_forest_ha", ascending=False).iloc[0]
    hold(100 * big.share < 1, "the unit with the most standing forest in the cell with closed forest and loss lost under one per cent of it in the window")
    show("big_unit", V(f"{big.unit_name} ({big.unit_id}), {big.district}", CU, f"the row with the largest `standing_forest_ha` among those whose `cell_{DEFAULT}` is dense_loss: its name, id and district"), txt)
    show("big_standing", V(float(big.standing_forest_ha), CU, f"`standing_forest_ha` of that row"), dec(0))
    show("big_loss", V(float(big[f"forest_loss_ha_{DEFAULT}"]), CU, f"`forest_loss_ha_{DEFAULT}` of that row"), dec(2))

    def sv(s, k, col="value"):
        return ev(k.replace("{s}", f"{s.v:g}"), col)

    table("T_stand", ["standing minimum, ha", "pixels in it", "units with at least that much standing forest", "share of all standing forest that is in them, %",
                      "rank correlation of a unit's loss rate between odd and even years, in the class of land that starts there", "units in that class", "share of that class with no loss recorded on that land in any year, %"],
          [[g(s), c(sv(s, "pixels_in_standing_{s}"), dec(0)), c(sv(s, "units_standing_{s}"), n0), c(sv(s, "share_standing_{s}"), dec(2)), c(sv(s, "repeat_rho_{s}"), dec(3)), c(sv(s, "repeat_rho_{s}", "n"), n0), c(sv(s, "repeat_no_loss_{s}"), dec(1))] for s in s_alt])
    kept = [sv(s, "share_standing_{s}").v for s in s_alt]
    hold(min(kept) > 99, "more than ninety-nine per cent of all standing forest is in the units kept, at each of the three standing minimums")
    rho = [sv(s, "repeat_rho_{s}").v for s in s_alt]
    hold(rho[0] < rho[1] < rho[2], "a unit's loss rate repeats better between odd and even years the larger the class of land it is in")
    nol = [sv(s, "repeat_no_loss_{s}").v for s in s_alt]
    hold(min(nol) > 50 and nol[0] > nol[1] > nol[2], "in each of the three classes more than half the units have no loss recorded on that land (canopy above ten per cent in 2000) in any year, and the share falls as the class grows")
    AFR = "20_degradation/agreement_floor_repeatability.csv"
    for s in s_alt[1:]:
        same(f"the rank correlation of the class from {s.v:g} ha in the evidence table and in `agreement_floor_repeatability.csv`", sv(s, "repeat_rho_{s}").v, cell(AFR, "odd_years_vs_even_years_spearman", reference_ha_from=int(s.v), hansen_loss_years="2001-2025").v)
        same(f"the units of the class from {s.v:g} ha in the evidence table and in `agreement_floor_repeatability.csv`", sv(s, "repeat_rho_{s}", "n").v, cell(AFR, "n_units", reference_ha_from=int(s.v), hansen_loss_years="2001-2025").v)
    hold(float(min(W.C(AS).minimum_reference_ha)) == s_alt[1].v and float(min(W.C(AFR).reference_ha_from)) == s_alt[1].v, "the proposed standing minimum is the lowest floor at which the agreement test was run, and the lowest class its repeatability table has")
    site = show("site_units", sv(s_alt[1], "units_standing_{s}"), n0)
    show("site_share", sv(s_alt[1], "share_standing_{s}"), dec(2))
    show("rho_lo", V(rho[0], CE, "column `value`; row where `key` is the rank correlation of the class that starts at the lower alternative"), dec(2))
    show("rho_smin", V(rho[1], CE, "column `value`; row where `key` is the rank correlation of the class that starts at the proposed standing minimum"), dec(2))
    show("rho_hi", V(rho[2], CE, "column `value`; row where `key` is the rank correlation of the class that starts at the higher alternative"), dec(2))
    show("nol_lo", V(nol[0], CE, "column `value`; row where `key` is the share with no loss in the class that starts at the lower alternative"), dec(0))
    show("nol_smin", V(nol[1], CE, "column `value`; row where `key` is the share with no loss in the class that starts at the proposed standing minimum"), dec(0))
    show("nol_hi", V(nol[2], CE, "column `value`; row where `key` is the share with no loss in the class that starts at the higher alternative"), dec(0))
    u_mid, u_hi = sv(s_alt[1], "units_standing_{s}"), sv(s_alt[2], "units_standing_{s}")
    calc("mv_s_hi_units", u_mid.v - u_hi.v, n0, "units with at least the proposed standing minimum less units with at least the higher alternative", [u_mid, u_hi])
    k_mid, k_hi = sv(s_alt[1], "share_standing_{s}"), sv(s_alt[2], "share_standing_{s}")
    calc("set_aside_pct", k_mid.v - k_hi.v, dec(2), "share of standing forest in units with at least the proposed standing minimum less the share in units with at least the higher alternative", [k_mid, k_hi])
    land = T.dense_2000_ha + T.open_2000_ha + T.low_2000_ha
    small_units = show("small_units", count(CU, "rows whose three bands of land in the year 2000 add to less than the standing minimum", lambda t: (t.dense_2000_ha + t.open_2000_ha + t.low_2000_ha) < s_alt[1].v), n0)
    hold(bool((T.loc[land < s_alt[1].v, "standing_row"] == "little_or_none").all()), "every unit with less land than the standing minimum is in the row 'little or none'")
    half = show("half_forest", count(CU, f"rows whose `cell_{DEFAULT}` is the cell outside the ranked list and whose standing forest is half or more of their land", lambda t: (t[f"cell_{DEFAULT}"] == UNRANKED) & (2 * t.standing_forest_ha >= (t.dense_2000_ha + t.open_2000_ha + t.low_2000_ha)) & ((t.dense_2000_ha + t.open_2000_ha + t.low_2000_ha) > 0)), n0)
    same("units with less land than the standing minimum: counted here, and in the layer's record of its About text", small_units.v, key(L, "decision_view/figures_in_the_about_text/units_with_land_under_the_standing_minimum").v)
    same("units outside the ranked list with forest on half their land: counted here, and in the layer's record of its About text", half.v, key(L, "decision_view/figures_in_the_about_text/unranked_units_with_forest_on_half_their_land").v)

    def sens(s, l, w, x, col="n_units"):
        return cell(CS, col, standing_min_ha=s.v, loss_min_ha=l.v, window=w, cell=x)

    moved = lambda s, l, w: sens(s, l, w, CELLS[0], "units_whose_cell_differs_from_the_default_all_cells")
    srows = []
    for s in s_alt:
        for l in l_alt:
            per = [sens(s, l, DEFAULT, x) for x in CELLS]
            same(f"units in the six cells at {s.v:g} ha standing and {l.v:g} ha loss, window {DEFAULT}, and the units", sum(v.v for v in per), n_units.v)
            is_default = s is s_alt[1] and l is l_alt[1]
            if is_default:
                for x, v in zip(CELLS, per):
                    same(f"units in the cell {x} at the proposal: in the sensitivity table and in the table of cells", v.v, nc(DEFAULT, x).v)
                hold(moved(s, l, DEFAULT).v == 0, "at the proposal no unit differs from the default")
            srows.append([g(s), g(l)] + [c(v, n0) for v in per] + [c(moved(s, l, DEFAULT), n0) if not is_default else "the proposal"])
    table("T_sens", ["standing minimum, ha", "loss minimum, ha"] + [name[x].v for x in CELLS] + ["units in another cell than at the proposal"], srows)
    table("T_sens_w", ["window", "standing minimum at the lower alternative", "standing minimum at the higher alternative", "loss minimum at the lower alternative", "loss minimum at the higher alternative"],
          [[label, c(moved(s_alt[0], l_alt[1], w), n0), c(moved(s_alt[2], l_alt[1], w), n0), c(moved(s_alt[1], l_alt[0], w), n0), c(moved(s_alt[1], l_alt[2], w), n0)] for w, label in WINDOWS])
    for nm, s, l in (("mv_s_lo", s_alt[0], l_alt[1]), ("mv_s_hi", s_alt[2], l_alt[1]), ("mv_l_lo", s_alt[1], l_alt[0]), ("mv_l_hi", s_alt[1], l_alt[2])):
        show(nm, moved(s, l, DEFAULT), n0)
    hold(min(moved(s_alt[0], l_alt[1], DEFAULT).v, moved(s_alt[2], l_alt[1], DEFAULT).v) > max(moved(s_alt[1], l_alt[0], DEFAULT).v, moved(s_alt[1], l_alt[2], DEFAULT).v),
         "in the default window, moving the standing minimum to either alternative moves more units than moving the loss minimum to either of its own")

    # ---- 5.4 loss as a share ----
    def shc(col, x, w=DEFAULT):
        return cell(SH, col, window=w, cell=x)
    share_cols = ["n_units", "n_with_a_share", "n_no_share_too_little_forest_at_the_start", "share_under_1pct", "share_1_to_under_5pct", "share_5pct_or_more"]
    table("T_share", ["cell", "units", "with a share", "no share: too little forest at the start", "share under one per cent", "one to under five per cent", "five per cent or more", "median share, %", "largest share, %"],
          [[c(name[x], txt)] + [c(shc(k_, x), n0) for k_ in share_cols] + [c(shc("median_share_pct", x), dec(2)), c(shc("largest_share_pct", x), dec(2))] for x in ORDER + [UNRANKED]])
    for x in CELLS:
        same(f"units of the cell {x} in the share table and in the table of cells", shc("n_units", x).v, nc(DEFAULT, x).v)
        same(f"units of the cell {x} with a share and without one, and its units", shc("n_with_a_share", x).v + shc("n_no_share_too_little_forest_at_the_start", x).v, shc("n_units", x).v)
        same(f"the three classes of the share in the cell {x}, and its units with a share", sum(shc(k_, x).v for k_ in share_cols[3:]), shc("n_with_a_share", x).v)
    table("T_share_w", ["window", "units with a share", "units with none", "of those, in a cell with loss recorded"],
          [[c(V(lab, "this run", "the window's years"), txt), c(key(DP, f"counts/loss_as_a_share/{w}/units_with_a_share"), n0), c(key(DP, f"counts/loss_as_a_share/{w}/units_with_no_share"), n0),
            c(key(DP, f"counts/loss_as_a_share/{w}/units_with_no_share_in_a_cell_with_loss"), n0)] for w, lab in WINDOWS])
    for w, _ in WINDOWS:
        same(f"units with a share and without one in {w}, and the units", key(DP, f"counts/loss_as_a_share/{w}/units_with_a_share").v + key(DP, f"counts/loss_as_a_share/{w}/units_with_no_share").v, n_units.v)
        same(f"units with no share in {w}: in the run record and blank in the table", key(DP, f"counts/loss_as_a_share/{w}/units_with_no_share").v, int(T[f"forest_loss_share_pct_{w}"].isna().sum()))
        hold(bool((T[f"forest_loss_share_pct_{w}"].isna() == T[f"forest_loss_share_blank_because_{w}"].notna()).all()) and T[f"forest_loss_share_blank_because_{w}"].dropna().nunique() <= 1,
             f"in {w} a share is blank exactly where the table gives the reason in words, and the reason is one sentence")
        hold(float(T[f"forest_loss_share_pct_{w}"].max()) <= 100, f"in {w} no share is above a hundred")
    show("sh_with", key(DP, f"counts/loss_as_a_share/{DEFAULT}/units_with_a_share"), n0)
    show("sh_without", key(DP, f"counts/loss_as_a_share/{DEFAULT}/units_with_no_share"), n0)
    show("sh_without_loss", key(DP, f"counts/loss_as_a_share/{DEFAULT}/units_with_no_share_in_a_cell_with_loss"), n0)
    show("sh_reason", V(str(T[f"forest_loss_share_blank_because_{DEFAULT}"].dropna().iloc[0]), CU, f"column `forest_loss_share_blank_because_{DEFAULT}`: the one sentence it holds"), txt)
    dls = show("dl_share_1pct", ev("dense_loss_share_under_1pct"), n0)
    show("none_share_2pct", ev("none_cell_share_over_2pct"), n0)
    same("units of the cell of closed forest with loss whose share prints under one per cent: in the evidence table and in the share table", dls.v, shc("share_under_1pct", "dense_loss").v)
    big_row = T[T[f"cell_{DEFAULT}"] == "dense_loss"].sort_values("standing_forest_ha", ascending=False).iloc[0]
    show("big_share", V(float(big_row[f"forest_loss_share_pct_{DEFAULT}"]), CU, f"column `forest_loss_share_pct_{DEFAULT}` of the row with the largest `standing_forest_ha` among those whose `cell_{DEFAULT}` is dense_loss"), dec(2))
    show("big_start", V(float(big_row[f"forest_at_window_start_ha_{DEFAULT}"]), CU, f"column `forest_at_window_start_ha_{DEFAULT}` of the same row"), n0)
    in_loss = T[f"cell_{DEFAULT}"].isin(["dense_loss", "open_loss", "little_loss"])
    show("order_differs", count(CU, f"rows in a cell with loss whose `order_in_district_cell_by_share_{DEFAULT}` is not their `order_in_district_cell_{DEFAULT}`",
                                lambda t_: t_[f"cell_{DEFAULT}"].isin(["dense_loss", "open_loss", "little_loss"]) & (t_[f"order_in_district_cell_by_share_{DEFAULT}"] != t_[f"order_in_district_cell_{DEFAULT}"])), n0)
    show("order_loss_units", V(int(in_loss.sum()), CU, f"rows whose `cell_{DEFAULT}` is a cell with loss"), n0)
    hold(bool((T.loc[~in_loss, f"order_in_district_cell_by_share_{DEFAULT}"] == T.loc[~in_loss, f"order_in_district_cell_{DEFAULT}"]).all()), "in the cells without loss the order by share is the order by standing hectares, unit for unit")

    DOC.append("""
## 5. The two thresholds: proposed on 8 October 2026, accepted by the owner on 9 October 2026

Two thresholds turn hectares into cells. **Both are decisions. The owner took them on 9 October 2026, as they were
proposed** (§17): the standing minimum, and the loss minimum as the rule of the cells. What follows is what was
proposed, why, and how much the answer moves at two alternatives; none of it changed with the ruling. What the ruling
added is §5.4: because a fixed number of hectares follows the size of a forest, the loss is now also shown as a share.

- **(a) The standing minimum: {smin} ha.** A unit with less standing forest than this, dense and open together, has
  "little or none".
- **(b) The loss minimum: {lmin} ha.** A unit that lost at least this much forest in the window, from dense and open
  together, has "some" loss.

Neither is the {floor} ha of the agreement test. That floor exists so that a rate of loss is a stable number to
compare between two measures; here nothing is a rate.

### 5.1 The loss minimum

**A single pixel must not move a unit.** One Hansen pixel is {pixel_ha} ha in the middle of the state; the grid is in
degrees, so a pixel is a little smaller to the north and a little larger to the south. In the default window {one_px}
units have a recorded forest loss above zero and under {pixel_ha} ha. That count is of a size, not of "one pixel or
less": it takes in slivers of a lost pixel cut off by a unit's boundary and, in the north, units that lost exactly one
whole pixel; and it leaves out units in the south that lost one whole pixel, which is a little more than {pixel_ha} ha
there and so falls in the second column below. The stage tables carry no latitude, so the two were not told apart; the
argument does not need it: there are units, well over a hundred in every window, whose cell one pixel would decide.

{T_small}

*n = {n_units} units in each window; the counts are of units, and a unit with no forest loss is in neither column.*

The proposal, {lmin} ha, is {px_in_lmin} pixels. It is the smallest patch the Forest Survey of India counts as forest
cover: its report gives the minimum as "more than or equal to one hectare in area" (the extract registered in
`00_raw/05_forest_reference/`), {fsi_min} ha. So "some loss" means the loss of at least the least thing the national
inventory would call forest.

**Is a loss of that size a real signal?** What can be asked of this table is whether loss recurs. Among units with at
least {smin} ha standing that lost {lmin} ha or more in 2018–2021, {recur} per cent (n = {recur_n}) lost that much
again in 2022–2025. Among those that lost under {pixel_ha} ha, or nothing, in 2018–2021, {fresh} per cent
(n = {fresh_n}) lost {lmin} ha or more in 2022–2025.

{T_recur}

*Each cell is a share in per cent with the number of units it is a share of. The rows are the three standing
minimums; the first three columns are the three loss minimums.*

**What this does not settle.** Recurrence is within two points whichever of the three loss minimums is used. It shows
that a loss at or above any of them is not noise; it does not pick between them. The choice of {lmin} ha rests on the
Forest Survey's patch and on being more than a dozen pixels, and that is a judgement.

**What a fixed number of hectares does: it follows the size of the forest.** The owner asked for a minimum in
hectares, and this is its consequence. The more forest a unit has, the likelier that some hectare of it was lost:

{T_size}

*n = {site_units} forest-site units, each in one row, classed by standing forest as printed; default window, whose
first half is 2018–2021 and second 2022–2025. The last two columns give a share in per cent with the number of units
it is a share of.*

Of forest sites with ten to twenty-five hectares standing, {size_lo} per cent have "some" loss; of those with five
thousand or more, {size_hi} per cent: {big_loss_n} of {big_n} units in the state. In {dist_top_loss} of the
{n_districts} districts the unit with the most standing forest is in a cell with loss. A cell with loss therefore says
little about a large unit's rate of loss: {dl_under_1pct} of the units in "{dense_loss_name}" lost under one per cent
of their standing forest in the window, and {dl_under_01pct} lost under a tenth of one per cent. The unit of that cell
with the most forest, {big_unit}, has {big_standing} ha standing and lost {big_loss} ha. And the other way:
{none_over_2pct} forest-site units lost more than two per cent of their forest in the window and are in a cell
without loss, because that came to less than {lmin} ha. A unit's panel shows the hectares, so a reader can see which
kind of unit is in front of them; the cell alone does not say. The recurrence that speaks for the loss minimum is
also mostly a matter of large units: among forest sites of ten to twenty-five hectares that lost {lmin} ha or more in
the first half of the window, {recur_small} per cent (n = {recur_small_n}) did so again in the second. The owner's
ruling on this (§17): the minimum stays a number of hectares as the rule of the cells; the names of the cells no
longer claim more than that rule (§7); and the loss is shown as a share beside the cell (§5.4).

### 5.2 The standing minimum

{T_stand}

*n = {n_units} units. The last three columns are the repeatability of stage 1's kind, worked out by the decision
stage on the land this threshold is about (canopy above ten per cent in 2000, dense and open) by the method of
`20_degradation/agreement_floor_repeatability.csv`; for the two classes that table also has, the figures equal its
own, and the build stops if they do not. Classes are of land in the year 2000.*

At {smin} ha, {site_units} units are forest sites and they hold {site_share} per cent of all standing forest. The
share barely changes across the three settings, so it does not pick between them. Nor does the evidence on
repeatability pick one. It rises steadily with the size of the class, with no break at any of the three: the rank
correlation of a unit's loss rate between odd and even years is {rho_lo} in the class that starts at {smin_lo} ha,
{rho_smin} in the class that starts at {smin} ha and {rho_hi} in the class that starts at {smin_hi} ha, and the share
of units with no loss recorded on that land in any year is {nol_lo}, {nol_smin} and {nol_hi} per cent: more than
half in all three. (Loss on land with less canopy is not in that count.)

So the proposal is a judgement, and these are the two things it rests on. {smin} ha is the lowest floor at which this
project's agreement test was itself run, and the lowest class of the repeatability table made on this land, the land
with canopy above ten per cent in 2000: on that land no table of stage 1 goes lower. Another table of stage 1 does go
lower (`20_degradation/forest_floor_repeatability.csv`), but on the forest mask, canopy above thirty per cent, which
is not the land this threshold is about; the proposal does not lean on it. And the higher alternative would set aside {mv_s_hi_units} more units, holding
{set_aside_pct} per cent of all standing forest, as having little or none.

**The minimum is absolute, like the other.** {small_units} units have less than {smin} ha of land altogether and are
in "little or none" whatever their cover. In {half_forest} units of the cell "{unranked_name}" standing forest covers
half or more of the unit's land. Their panels say what the test is.

### 5.3 Sensitivity

Every combination of the proposal and its two alternatives ({smin_lo} and {smin_hi} ha standing; {lmin_lo} and
{lmin_hi} ha of loss), in the default window:

{T_sens}

*n = {n_units} units in every row.*

With the loss minimum at the proposal, moving the standing minimum to {smin_lo} ha or to {smin_hi} ha puts {mv_s_lo}
or {mv_s_hi} units in another cell. With the standing minimum at the proposal, moving the loss minimum to {lmin_lo} ha
or to {lmin_hi} ha moves {mv_l_lo} or {mv_l_hi}. **The standing minimum is the more consequential of the two.** The
same four moves in each window:

{T_sens_w}

*Units whose cell differs from their cell at the proposal, of {n_units}.*

### 5.4 Loss as a share: beside the cell, never in it

Added by the owner's ruling of 9 October 2026. It changes no cell: `scripts/05_check_rename.py` holds every unit's cell
in every window against the table as it stood before (§16).

For each unit and each window the table now carries two more figures:

- **forest at the start of the window**: the unit's dense and open hectares of 2000, less the forest loss recorded in
  the years before the window's first year (`forest_at_window_start_ha`). For the full record that is the forest of 2000;
- **the loss of the window as a share of it**, in per cent (`forest_loss_share_pct`), rounded half up to two decimals
  in whole numbers.

**Where the forest at the start of the window is under the standing minimum, {smin} ha as printed, no share is
given**: a share of almost nothing means nothing. The table then holds the reason in words, "{sh_reason}", and the
layer shows words, not a blank and not a zero. In the default window {sh_with} units have a share and {sh_without}
have none; {sh_without_loss} of those are in a cell with loss recorded, all of them in the cell with little forest
left. By window:

{T_share_w}

*n = {n_units} units in each window.*

How the share falls across the cells, in the default window:

{T_share}

*n = {n_units} units. The share is classed as printed. The median is of the units that have a share.*

Read against §5.1: {dl_share_1pct} of the units in "{dense_loss_name}" lost under one per cent of the forest they had
at the start of the window, and {none_share_2pct} forest sites in a cell with little or no loss recorded lost over two
per cent of theirs. (§5.1 counts the same two things against standing forest, which is the forest at the start less
the loss of the window; the counts differ by the units that sit between the two denominators.) The unit of that cell
with the most forest, {big_unit}, had {big_start} ha at the start of the window and lost {big_share} per cent of it.

**A second order in the ranked list.** Within a tier the list is ordered by hectares lost, as before and as it
opens, or by share lost. It applies to the cells with loss recorded: there the units that have a share come first,
largest share first, and the units with no share after them, by hectares lost. The cells with little or no loss
recorded stay ordered by standing hectares under either choice. In the default window {order_differs} of the
{order_loss_units} units in a cell with loss have another place within their district and cell by share than by
hectares. The order in use is named in the head of the list, carried in the page's address and written in every row
of an exported list (§15). It is an order within a tier; it moves no unit between tiers and it is not a score.

**What was not done for these two columns.** They were not in the table that two independent replicators rebuilt on
8 October 2026. `scripts/verify_decision.py`, which shares no code with the build, rebuilds both from the yearly
columns of stage 1 for every unit and window, with the blanks, their reason and their count, and the order by share
(§16). That is one independent rebuild, not two.
""")
    show("dense_loss_name", name["dense_loss"], txt)
    show("unranked_name", name[UNRANKED], txt)

    # ==== 6. the dense/open boundary =====================================================================================================
    def cb(col, r, u="all units"):
        return cell(CB, col, ratio_at_least=r, units=u)

    ratios = sorted(set(W.C(CB).ratio_at_least))
    flag_r = [r for r in ratios if int(cb("is_the_flag_in_the_table", r).v) == 1]
    hold(len(flag_r) == 1 and abs(flag_r[0] - 0.8) < 1e-9 and abs(key(DP, "counts/near_dense_open_boundary").v - cb("n_near_the_boundary", flag_r[0]).v) == 0, "one ratio, and only one, is the flag carried in the table: the smaller within a fifth of the larger")
    kinds = (("all units", "all units"), ("LGD panchayat units", "lgd_panchayat"), ("outside-village units", "outside_village"))
    table("T_boundary", ["the smaller of standing dense and standing open is at least this share of the larger", "units", "units that are mostly dense or mostly open", "of them near the boundary", "of those, mostly dense", "of those, mostly open"],
          [[(f"{r:g}" + (" (the flag in the table)" if r == flag_r[0] else ""), [cb("ratio_at_least", r)]), lab, c(cb("n_units_mostly_dense_or_mostly_open", r, u), n0), c(cb("n_near_the_boundary", r, u), n0),
            c(cb("of_them_mostly_dense", r, u), n0), c(cb("of_them_mostly_open", r, u), n0)] for r in ratios for lab, u in kinds])
    near = show("near_n", cb("n_near_the_boundary", flag_r[0]), n0)
    same("units near the boundary in the boundary table and in the run record", near.v, key(DP, "counts/near_dense_open_boundary").v)
    same("units near the boundary in the boundary table and counted in the decision table", near.v, int((T.near_dense_open_boundary == 1).sum()))
    same("forest-site units in the boundary table and in the evidence table", cb("n_units_mostly_dense_or_mostly_open", flag_r[0]).v, site.v)
    calc("near_pct", 100 * near.v / site.v, dec(1), "units near the boundary ÷ units that are mostly dense or mostly open × 100", [near, site])
    rd, ro, rl = (show(nm, key(DP, f"counts/standing_row/{k}"), n0) for nm, k in (("row_dense", "mostly_dense"), ("row_open", "mostly_open"), ("row_little", "little_or_none")))
    same("units in the three rows, and the units", rd.v + ro.v + rl.v, n_units.v)
    same("units mostly dense and mostly open, and the forest-site units", rd.v + ro.v, site.v)

    DOC.append("""
## 6. Mostly dense or mostly open, and the units near that line

A unit with at least the standing minimum is **mostly dense** if its standing dense hectares are at least its standing
open hectares, and **mostly open** otherwise. {row_dense} units are mostly dense, {row_open} mostly open, and
{row_little} have little or none.

A unit with a lot of both is the one a single word summarises worst. So the table flags the units where the smaller of
the two is within a fifth of the larger: **{near_n} of the {site_units} forest-site units, {near_pct} per cent**.
Their panels say "close call", and an exported list says so in a column of its own. The count at other margins:

{T_boundary}

*n = {n_units} units; a unit with little or none is in no row of this table.*

A fifth is a round margin and not a finding: the table above is there so that another can be read off. The flag does
not change a unit's cell. It tells the reader that for this unit "mostly dense" and "mostly open" are a
fine distinction, and that the hectares beside the label are the thing to read.
""")

    # ==== 7. the six cells =================================================================================================================
    crow = {"mostly_dense": "mostly dense", "mostly_open": "mostly open", "little_or_none": "little or none"}
    table("T_cells", ["cell", "standing forest now", "forest loss in the window", "units", "LGD panchayat units", "outside-village units", "standing dense, ha", "standing open, ha", "forest loss in the window, ha", "of the units, near the dense and open line"],
          [[c(name[x], txt), crow[cell(TI, "standing_row", cell=x).v], cell(TI, "loss_column", cell=x).v, c(nc(DEFAULT, x), n0), c(nc(DEFAULT, x, "lgd_panchayat"), n0), c(nc(DEFAULT, x, "outside_village"), n0),
            c(nc(DEFAULT, x, col="standing_dense_ha"), dec(0)), c(nc(DEFAULT, x, col="standing_open_ha"), dec(0)), c(nc(DEFAULT, x, col="forest_loss_ha_in_window"), dec(0)), c(nc(DEFAULT, x, col="near_dense_open_boundary"), n0)] for x in ORDER + [UNRANKED]])
    for x in CELLS:
        same(f"LGD panchayat and outside-village units in the cell {x}, and its units", nc(DEFAULT, x, "lgd_panchayat").v + nc(DEFAULT, x, "outside_village").v, nc(DEFAULT, x).v)
    intact = show("intact_n", nc(DEFAULT, "dense_none"), n0)
    intact_cs = show("intact_cs", count(CU, f"rows whose `cell_{DEFAULT}` is dense_none and whose `corroboration` is corestack_only or both", lambda t: (t[f"cell_{DEFAULT}"] == "dense_none") & t.corroboration.isin(["corestack_only", "both"])), n0)
    same("units of the closed-forest cell without loss that CoRE Stack flags: counted here, and in the layer's record of its About text", intact_cs.v, key(L, "decision_view/figures_in_the_about_text/intact_cell_units_flagged_by_corestack").v)
    show("intact_compared", count(CU, f"rows whose `cell_{DEFAULT}` is dense_none and whose `corroboration` is not not_compared", lambda t: (t[f"cell_{DEFAULT}"] == "dense_none") & (t.corroboration != "not_compared")), n0)
    show("intact_loss", nc(DEFAULT, "dense_none", col="forest_loss_ha_in_window"), dec(0))
    intact_ec = show("intact_ec", count(CU, f"rows whose `cell_{DEFAULT}` is dense_none, whose `corroboration` is corestack_only or both, and whose `corroboration_basis` is east_coast_every_unit_kept",
                                         lambda t: (t[f"cell_{DEFAULT}"] == "dense_none") & t.corroboration.isin(["corestack_only", "both"]) & (t.corroboration_basis == "east_coast_every_unit_kept")), n0)
    intact_lost = show("intact_lost", count(CU, f"rows whose `cell_{DEFAULT}` is dense_none and whose `forest_loss_ha_2001_2025`, as printed, is the loss minimum or more",
                                             lambda t: (t[f"cell_{DEFAULT}"] == "dense_none") & (t.forest_loss_ha_2001_2025.round(2) >= key(DP, "thresholds/loss_min_ha").v)), n0)
    show("intact_never", count(CU, f"rows whose `cell_{DEFAULT}` is dense_none and whose `forest_loss_ha_2001_2025` is zero", lambda t: (t[f"cell_{DEFAULT}"] == "dense_none") & (t.forest_loss_ha_2001_2025 == 0)), n0)
    same("units of the closed-forest cell without loss that lost the minimum or more over the full record: counted here, and in the layer's record of its About text", intact_lost.v, key(L, "decision_view/figures_in_the_about_text/intact_cell_units_that_lost_the_loss_minimum_in_2001_2025").v)
    same("units of the closed-forest cell without loss flagged by CoRE Stack under the East Coast model: counted here, and in the layer's record of its About text", intact_ec.v, key(L, "decision_view/figures_in_the_about_text/of_them_under_the_east_coast_model").v)
    show("little_loss_n", nc(DEFAULT, "little_loss"), n0)
    show("anr_n", nc(DEFAULT, "open_none"), n0)
    ol = T[T[f"cell_{DEFAULT}"] == "open_loss"]
    ol_d = agg(CU, f"`loss_dense_ha_{DEFAULT}` summed over the rows whose `cell_{DEFAULT}` is open_loss", lambda t_: t_.loc[t_[f"cell_{DEFAULT}"] == "open_loss", f"loss_dense_ha_{DEFAULT}"].sum())
    ol_f = agg(CU, f"`forest_loss_ha_{DEFAULT}` summed over the rows whose `cell_{DEFAULT}` is open_loss", lambda t_: t_.loc[t_[f"cell_{DEFAULT}"] == "open_loss", f"forest_loss_ha_{DEFAULT}"].sum())
    calc("ol_dense_share", 100 * ol_d.v / ol_f.v, dec(0), "loss from the dense band ÷ forest loss, in the cell with open forest and loss, × 100", [ol_d, ol_f])
    show("ol_dense_more", count(CU, f"rows whose `cell_{DEFAULT}` is open_loss and whose `loss_dense_ha_{DEFAULT}` is larger than their `loss_open_ha_{DEFAULT}`", lambda t_: (t_[f"cell_{DEFAULT}"] == "open_loss") & (t_[f"loss_dense_ha_{DEFAULT}"] > t_[f"loss_open_ha_{DEFAULT}"])), n0)
    show("ol_n", nc(DEFAULT, "open_loss"), n0)
    show("order_rule", key(DP, "definitions/order"), txt)
    # the names before and after the ruling: from the tiers table kept from the build that was ruled on, and the one on disk
    TI_OLD = SCRATCH + "/55_decision_2026-10-08_as_ruled_on/tiers.csv"
    renamed = key(GATE, "the_owners_list_old_name_to_new_name").v
    nrows = []
    for x in ORDER + [UNRANKED]:
        old_ = cell(TI_OLD, "cell_name", cell=x)
        hold(renamed.get(old_.v) == name[x].v, f"the owner's list takes the old name of the cell {x} to the name it has now")
        nrows.append([c(old_, txt), c(name[x], txt) if old_.v != name[x].v else "unchanged"])
    table("T_names", ["name until 9 October 2026", "name as ruled"], nrows)
    hold(sum(1 for r_ in nrows if r_[1] != "unchanged") == 5 and [r_["cell"] for r_ in W.C(TI_OLD).to_dict("records")] == [r_["cell"] for r_ in W.C(TI).to_dict("records")],
         "five of the six cells were renamed, and the order of the tiers table is what it was")
    hold(key(L, "decision_view/legend_names_shortened").v == {}, "the layer's record says no name was shortened for the legend")
    show("dl_n", nc(DEFAULT, "dense_loss"), n0)

    DOC.append("""
## 7. The six cells

Rows: forest standing now is mostly dense, mostly open, or little or none. Columns: forest loss in the window is
none, or some. In the default window, in the provisional order of tiers:

{T_cells}

*n = {n_units} units: every unit is in one row. Hectares are sums over the units of the cell; "standing" is through
2025, and is {standing_is}.*

**Five of the six names were changed on 9 October 2026, by the owner's ruling, and no unit moved.** With a flat
minimum of {lmin} ha of loss, the first names claimed more than the test behind them:

{T_names}

*Six cells. The first column is read from the tiers table of the build of 8 October 2026, kept with the session's
working files; the second from the one on disk.*

Why, in figures read from the files:

- **"Under pressure" mostly meant large.** {dl_share_1pct} of the {dl_n} units of that cell lost under one per cent of
  the forest they had at the start of the window. The one with the most forest, {big_unit}, has {big_standing} ha
  standing and lost {big_loss} ha. And {none_over_2pct} forest sites that lost over two per cent of their standing
  forest are in cells without loss, because that came to less than {lmin} ha (§5.1, §5.4).
- **"Intact" was contradicted.** Of the {intact_compared} units of that cell that the comparison with CoRE Stack
  covers, {intact_cs} are flagged by CoRE Stack for degradation ({intact_ec} of them under the East Coast model, where
  that flag is itself unreliable, §11). The {intact_n} units of the cell carry {intact_loss} ha of forest loss in the
  window between them; {intact_lost} of them lost {lmin} ha or more at some time in 2001–2025, and only {intact_never}
  have no recorded forest loss at all since 2001. And Hansen cannot see a canopy thinning.
- **A name now states the test and no more.** "Loss recorded" is {lmin} ha or more of forest loss in the window
  chosen; "little or no loss recorded" is less than that. The words after the hyphen say what the cell points to, as
  before. The sentence under each name in a unit's panel states the same test in hectares.

**The gate on the renaming.** Every unit's cell as it stood before, in each of the four windows, was taken through
that list of names and compared with the table as it is now: {gate_n} assignments, and every one matches. The
{gate_cols} columns the table had are equal as text in every row ({gate_cells} cells), so the hectares, the orders
within a cell, the tier and the corroboration are what they were; {gate_new_cols} columns were added beside them
(§5.4). `scripts/05_check_rename.py` does this, stops on one mismatch, and writes `55_decision/rename_gate.json`. The
table it compares with, whose `sha256` begins {gate_before_sha}, is the one two independent replicators rebuilt on
8 October 2026 (§16).

More about the names.

- **They are the owner's**, with one change of typography that he accepted: the layer writes the dash in them as a
  hyphen. The governance prompt of §12, which was given as a quotation, keeps its dash. Every name is shown in full
  everywhere, the legend included: none was shortened there.
- **"{anr_name}"** is the largest cell among the forest sites by number of units ({anr_n}). The official list of
  permissible works does not name that work (§13).
- **"{open_loss_name}" is about what stands, not about what was lost.** A unit is in that cell when the forest standing
  in it is mostly open and it lost forest of either band. {ol_dense_share} per cent of the cell's forest loss in the
  window was from the dense band, and in {ol_dense_more} of its {ol_n} units more was lost from dense than from open.
  The panel shows the two losses apart.
- **"{little_name}"** holds {little_loss_n} units. Little forest stands in them and loss is recorded: plantation
  felled, regrowth cleared, or an error. The name says what to do about that.

**The order inside a cell**, as the run record states it: "{order_rule}". The order is kept district by district and
nowhere else (§9). The head of every ranked list, the About text and a column of every exported row say what orders
the units within a tier.

**One column of the table is a number where the layer shows a label.** `tier_provisional_2018_2025` holds the place of
the unit's cell in the provisional order, for the default window only, as a whole number. It is a convenience for
anyone working from the table; the labels are in `55_decision/tiers.csv`, and the layer never shows the bare number.
""")
    show("anr_name", name["open_none"], txt)
    show("little_name", name["little_loss"], txt)
    show("open_loss_name", name["open_loss"], txt)

    # ==== 8. tiers =========================================================================================================================
    table("T_tiers", ["tier, as the layer labels it", "the line recorded for it"], [[c(cell(TI, "tier_label", cell=x), txt), c(cell(TI, "why_this_place_in_the_order", cell=x), txt)] for x in ORDER + [UNRANKED]])
    show("tier_status", key(DP, "tiers/status"), txt)
    hold(ORDER[:2] == ["open_loss", "dense_loss"] and "forester" in key(DP, "tiers/note").v, "the provisional order puts open forest with loss recorded first and closed forest with loss recorded second, and the record notes that a forester could reverse them")
    doc05 = W.use("scripts/05_build_decision.py").read_text(encoding="utf-8").split('"""')[1]
    hold(not any(re.search(r"score|index|weight", col) for col in T.columns) and all(re.search(rf"\b{re.escape(col)}\b", doc05) or re.search(rf"\b{re.escape(re.sub(r'_(2018_2025|2001_2025|2017_2023|2021_2025)$', '_W', col))}\b", doc05) for col in T.columns),
         "no column name of the decision table carries the words score, index or weight, and every column is one the build's docstring names, by its own name or, for the columns of a window, under the letter W")

    DOC.append("""
## 8. The tiers: provisional

The ranked view puts the cells in an order. The status of that order, as the run record carries it: "{tier_status}".

{T_tiers}

*Six cells: five tiers and the one cell left outside the ranked list.*

The lines of the first, second and fifth tiers argue for a place in the order. Those of the third and fourth say what
the tier is for and give no argument for its place: why, of the two cells without recorded forest loss, open forest
comes before closed is argued nowhere yet. It is the owner's provisional order.

**A forester could reasonably put the second tier above the first.** Closed forest that is being removed is arguably
the more urgent thing to understand; open forest with loss recorded is arguably where work has most to gain. That is
a judgement for the Foundation, and the order above is only where the layer starts.

So **the order is a control in the layer, not a constant.** A user can move any tier up or down and go back to the
provisional order. The legend, the ranked list and its head follow, the page's address carries the order, and an
exported list states the order that made it and whether the user changed it; otherwise "the first tier" would mean
different things in different files (§15).

**A rank is shown as a tier label, never as a bare number**, in the legend, in the list and in the export.

**There is no composite score.** No index, no weights, no number out of a hundred, in the table or in the layer.
Within a tier, units are ordered by one physical quantity (§7), and across tiers by the order above.
""")

    # ==== 9. within a district ===============================================================================================================
    HEAD = dict(population="east_coast_excluded", window="common_2017_2023", units="lgd_panchayat")

    def ar(col, fl):
        return cell(AS, col, minimum_reference_ha=fl, **HEAD)

    hold(int(ar("delivered", floor.v).v) == 1 and int(cell(AS, "delivered", population="east_coast_excluded", window="common_2017_2023", units="all units", minimum_reference_ha=floor.v).v) == 1,
         "the row read for the two odds ratios is the agreement test's delivered headline row for LGD panchayat units")
    wi, wl, wh = show("or_within", ar("odds_ratio_within_districts", floor.v), dec(2)), show("or_within_lo", ar("odds_ratio_within_districts_lo95", floor.v), dec(2)), show("or_within_hi", ar("odds_ratio_within_districts_hi95", floor.v), dec(2))
    ac, al, ah = show("or_across", ar("odds_ratio", floor.v), dec(2)), show("or_across_lo", ar("odds_ratio_lo95", floor.v), dec(2)), show("or_across_hi", ar("odds_ratio_hi95", floor.v), dec(2))
    hold(wl.v > 1, "within districts, the interval of the odds ratio for LGD panchayat units lies above one")
    hold(al.v < 1 < ah.v, "across the state, the interval of the odds ratio for LGD panchayat units includes one")
    about = key(L, "decision_view/figures_in_the_about_text/odds_ratio_within_districts_lgd").v + " | " + key(L, "decision_view/figures_in_the_about_text/odds_ratio_across_the_state_lgd").v
    hold(about == f"{wi.v:.2f}, interval {wl.v:.2f} to {wh.v:.2f} | {ac.v:.2f}, {al.v:.2f} to {ah.v:.2f}", "the two odds ratios in the layer's About text are the ones in `agreement_summary.csv`")

    def ar_of(units, col):
        return cell(AS, col, minimum_reference_ha=floor.v, population="east_coast_excluded", window="common_2017_2023", units=units)

    aa, aal, aah = show("or_all", ar_of("all units", "odds_ratio"), dec(2)), show("or_all_lo", ar_of("all units", "odds_ratio_lo95"), dec(2)), show("or_all_hi", ar_of("all units", "odds_ratio_hi95"), dec(2))
    ao, aol, aoh = show("or_out", ar_of("outside_village", "odds_ratio"), dec(2)), show("or_out_lo", ar_of("outside_village", "odds_ratio_lo95"), dec(2)), show("or_out_hi", ar_of("outside_village", "odds_ratio_hi95"), dec(2))
    hold(aal.v > 1 and aol.v > 1, "at the headline, the interval of the across-state odds ratio lies above one for all units together and for outside-village units")
    hold(key(L, "decision_view/figures_in_the_about_text/odds_ratio_across_the_state_all_units").v == f"{aa.v:.2f}, {aal.v:.2f} to {aah.v:.2f}", "the all-units figure in the layer's About text is the one in `agreement_summary.csv`")
    show("or_n", ar("n_assessed", floor.v), n0)
    show("or_districts", ar("n_districts", floor.v), n0)

    def kept(col):
        return cell(AS, col, minimum_reference_ha=floor.v, population="all_assessed", window="common_2017_2023", units="lgd_panchayat")
    ka, kal, kah = show("or_kept", kept("odds_ratio"), dec(2)), show("or_kept_lo", kept("odds_ratio_lo95"), dec(2)), show("or_kept_hi", kept("odds_ratio_hi95"), dec(2))
    hold(kal.v > 1, "with the East Coast units kept, the interval of the across-state odds ratio for LGD panchayat units at the headline floor lies above one")
    headl = T[(T.corroboration_basis == "headline") & (T.unit_level == "lgd_panchayat")]
    by_d = headl.groupby("district").corroboration.agg(h=lambda s_: int(s_.isin(["both", "hansen_only"]).sum()), c=lambda s_: int(s_.isin(["both", "corestack_only"]).sum()))
    same("LGD panchayat units of the headline: counted in the decision table, and in the agreement summary", len(headl), ar("n_assessed", floor.v).v)
    same("districts with an LGD panchayat unit of the headline: counted in the decision table, and in the agreement summary", len(by_d), ar("n_districts", floor.v).v)
    show("or_d_nothing", V(int(((by_d.h == 0) | (by_d.c == 0)).sum()), CU, "districts in which, among the LGD panchayat units whose `corroboration_basis` is headline, no unit is flagged by Hansen or none by CoRE Stack (column `corroboration`)"), n0)
    no_head = sorted(set(T.district) - set(T[T.corroboration_basis == "headline"].district))
    show("or_d_none", V(len(no_head), CU, "districts with no unit of either kind whose `corroboration_basis` is headline"), n0)
    show("or_d_none_names", V(", ".join(no_head), CU, "the districts with no unit whose `corroboration_basis` is headline"), txt)
    show("or_d_none_ranked", V(int((T.district.isin(no_head) & (T[f"cell_{DEFAULT}"] != UNRANKED)).sum()), CU, f"units of those districts whose `cell_{DEFAULT}` is a ranked cell"), n0)
    floors = sorted(set(W.C(AS).minimum_reference_ha))
    table("T_or", ["floor of the agreement test, ha", "LGD panchayat units compared", "odds ratio across the state (interval)", "odds ratio within districts (interval)"],
          [[(f"{fl:g}" + (" (the headline)" if fl == floor.v else ""), [ar("minimum_reference_ha", fl)]), c(ar("n_assessed", fl), n0), W.span(ar("odds_ratio", fl), ar("odds_ratio_lo95", fl), ar("odds_ratio_hi95", fl)),
            W.span(ar("odds_ratio_within_districts", fl), ar("odds_ratio_within_districts_lo95", fl), ar("odds_ratio_within_districts_hi95", fl))] for fl in floors])
    lower = [fl for fl in floors if fl < floor.v]
    hold(len(lower) == 2 and all(ar("odds_ratio_lo95", fl).v > 1 for fl in lower), "at the two lower floors of the same table the interval of the across-state odds ratio for LGD panchayat units lies above one")
    hold(all(ar("odds_ratio_within_districts_lo95", fl).v > 1 for fl in floors), "at every floor of the table the interval of the within-district odds ratio for LGD panchayat units lies above one")
    show("ranked_no_badge", count(CU, f"rows whose `cell_{DEFAULT}` is not the cell outside the ranked list and whose `corroboration` is not_compared", lambda t_: (t_[f"cell_{DEFAULT}"] != UNRANKED) & (t_.corroboration == "not_compared")), n0)
    districts = sorted(set(W.C(CD).district))
    show("n_districts", V(len(districts), CD, "column `district`: the number of distinct districts"), n0)

    def dsum(d, col, ranked):
        what = f"`{col}` summed over the cells " + ("other than the one outside the ranked list" if ranked else "of the cell outside the ranked list") + f", window {DEFAULT}, district {d}"
        return agg(CD, what, lambda t, d=d: t.loc[(t.window == DEFAULT) & (t.district == d) & ((t.cell != UNRANKED) if ranked else (t.cell == UNRANKED)), col].sum())

    drows, tot = [], [0, 0, 0]
    for d in districts:
        rk, ro_, un = dsum(d, "n_units", True), dsum(d, "n_outside_village", True), dsum(d, "n_units", False)
        tot = [tot[0] + rk.v, tot[1] + ro_.v, tot[2] + un.v]
        drows.append([c(V(d, CD, "column `district`"), txt), c(rk, n0), c(ro_, n0), c(un, n0)])
    table("T_districts", ["district", "units in the ranked list", "of them outside-village units", "units outside the list: not a forest site"], drows)
    same("units in the ranked lists of all districts and units outside them, and the units", tot[0] + tot[2], n_units.v)
    out_ranked = show("out_ranked", V(int(tot[1]), CD, f"column `n_outside_village` summed over every district and every cell but the one outside the ranked list, window {DEFAULT}"), n0)
    same("outside-village units in a ranked cell: summed over the districts, and in the layer's record of its About text", out_ranked.v, key(L, "decision_view/figures_in_the_about_text/outside_village_units_in_a_ranked_cell").v)
    show("ranked_all", V(int(tot[0]), CD, f"column `n_units` summed over every district and every cell but the one outside the ranked list, window {DEFAULT}"), n0)
    n_with_out = sum(1 for r in drows if r[2][1][0].v > 0)
    show("districts_with_out", V(n_with_out, CD, f"districts whose ranked cells hold at least one outside-village unit, window {DEFAULT}"), n0)

    DOC.append("""
## 9. Ranked within a district, never across the state

The ranked view is scoped to a district. The user picks one; its units are listed tier by tier. **There is no
state-wide ranking, and none was built**: the page holds an order for each district and no order across them.

**The reason the owner gave is in this project's own analysis, and it is narrower than it sounds.** Among the LGD
panchayat units of the agreement test's headline, from `20_degradation/agreement_summary.csv`: within districts the
odds ratio is {or_within} (interval {or_within_lo} to {or_within_hi}); across the state it is {or_across}
({or_across_lo} to {or_across_hi}), an interval that includes one. So for those units agreement across the state is
not established, and a state-wide leaderboard of them would rest on a comparison the analysis does not establish. The
layer's About text says this, with the units it is true of, and so does the panel under the map while no district is
chosen.

**What that row is, and what it is not.** It is the delivered headline of the agreement test: {or_n} LGD panchayat
units in {or_districts} districts, with the East Coast zone left out, at the {floor} ha floor (`docs/RESULTS.md` §5).
The same file carries the same comparison at two lower floors:

{T_or}

*LGD panchayat units, East Coast zone left out, window 2017–2023. Intervals are from resampling whole districts.*

Four things qualify the reason. The figures of the first, second and fourth are from the same file; the counts of
units and of districts are from the decision table.

- **It is about LGD panchayat units only.** At the same headline, for all units together the across-state odds ratio
  is {or_all} ({or_all_lo} to {or_all_hi}), and for outside-village units {or_out} ({or_out_lo} to {or_out_hi}): both
  intervals lie above one. The ranked lists hold both kinds of unit.
- **It is about one floor.** At the two lower floors the across-state interval for LGD panchayat units lies above one
  as well; the within-district agreement holds at all three.
- **It is about {or_n} units.** The ranked lists of the default window hold {ranked_all}, of which {ranked_no_badge}
  carry no badge at the test's {floor} ha floor (§11); the decision view uses none of these floors (§5).
- **It is about the headline's population, and about districts taken together.** The headline leaves the East Coast
  zone out. With those units kept, the across-state odds ratio for LGD panchayat units at the same floor is {or_kept}
  ({or_kept_lo} to {or_kept_hi}), an interval above one; the ranked lists make no such exclusion. And the
  within-district figure is one figure pooled over {or_districts} districts. In {or_d_nothing} of them one of the two
  measures flags no LGD panchayat unit of the comparison, so the district adds nothing to it. In {or_d_none} districts
  ({or_d_none_names}) no unit of either kind is in the comparison at all; their lists hold {or_d_none_ranked} ranked
  units. So the figure says nothing of any one district's list.

So "the two measures do not agree across the state" is not what the file says; "for LGD panchayat units at the
headline, agreement across the state is not established" is. What the file does bear out for LGD panchayat units is
that agreement within districts holds at all three floors, where agreement across the state does not hold at the
headline. That, and not the absence of agreement across the state, is the case for ranking within a district. The
owner accepted this narrower wording, which is the one the layer uses, on 9 October 2026 (§17). No state-wide ranking
was built.

What a district's list holds, in the default window:

{T_districts}

*n = {n_units} units in {n_districts} districts: {ranked_all} in a ranked cell, {out_ranked} of them outside-village
units. The ranked list of {districts_with_out} of the {n_districts} districts holds outside-village units. A unit is in one district: an LGD panchayat unit in its census district, an
outside-village unit in the district assigned to it (§12).*
""")

    # ==== 10. beside the tier ================================================================================================================
    exp, to1718 = key(A, "dump/expenditure_total"), agg(ADF, "`expenditure_total` of rows whose `fy_work_start` is a year up to 2017-18", lambda t: t.loc[(t.fy_work_start != "NA") & (t.fy_work_start <= "2017-18"), "expenditure_total"].sum())
    e1718 = calc("exp_to_1718_pct", 100 * to1718.v / exp.v, dec(1), "expenditure on works started in or before FY2017-18 ÷ all expenditure × 100", [to1718, exp])
    hold(e1718.v > 95, "nearly all of the geotagged record's expenditure is on works started in or before FY2017-18")
    fn_units = show("fn_units", count(AB, "rows whose `expenditure_forest_named_worktype` is above zero", lambda t: t.expenditure_forest_named_worktype > 0), n0)
    AF = "40_allocation/allocation_by_unit_fy.csv"
    fn_all = agg(AF, "`expenditure_forest_named_worktype` summed over every row", lambda t_: t_.expenditure_forest_named_worktype.sum())
    fn_to = agg(AF, "`expenditure_forest_named_worktype` summed over the rows whose `fy_work_start` is 2017-18 or earlier", lambda t_: t_.expenditure_forest_named_worktype[t_.fy_work_start.astype(str) <= "2017-18"].sum())
    fn_pct = calc("fn_to_1718_pct", 100 * fn_to.v / fn_all.v, dec(1), "expenditure on work types that name forest, on works started in or before FY2017-18 ÷ all such expenditure × 100", [fn_to, fn_all])

    def only_later(t_):
        g_ = t_.assign(early=t_.expenditure_forest_named_worktype.where(~(t_.fy_work_start.astype(str) > "2017-18") | t_.fy_work_start.isna(), 0.0)).groupby("unit_id")[["expenditure_forest_named_worktype", "early"]].sum()
        return float(((g_.expenditure_forest_named_worktype > 0) & (g_.early == 0)).sum())
    fn_later = show("fn_only_later", agg(AF, "units with expenditure on work types that name forest, all of it on works whose `fy_work_start` is after 2017-18", only_later), n0)
    same("units with any expenditure on work types that name forest: in the table by unit and in the table by unit and year", fn_units.v,
         int((W.C(AF).groupby("unit_id").expenditure_forest_named_worktype.sum() > 0).sum()))
    hold(fn_pct.v > 90 and fn_later.v < fn_units.v / 5, "more than nine tenths of the expenditure on work types that name forest is on works started in or before FY2017-18, and fewer than a fifth of the units with any show only later works")
    calc("fn_none", n_units.v - fn_units.v, n0, "units less the units with any expenditure on work types that name forest", [n_units, fn_units])
    NT = "tables/need_by_unit.csv/columns_lgd_panchayat_units_only/"
    show("st_blank", key(N, NT + "st_share/blank"), n0)
    show("adi_blank", key(N, NT + "adi_2011/blank"), n0)

    DOC.append("""
## 10. What stands beside the tier, and what stays out

In the ranked list each unit's row carries, beside its tier label: standing dense and standing open hectares; forest
loss in the window, and that loss as a share of the forest at the window's start (§5.4); the corroboration badge (§11); Scheduled Tribe share (`st_share`); the development index of 2011
(`adi_2011`); past expenditure on work types that name forest; and whether it is an outside-village unit.

- **Need and allocation are beside the tier and never inside it.** They do not move a unit up or down.
- **Past forest-named expenditure is labelled for what it is.** The geotagged record effectively ends in FY2017-18:
  {exp_to_1718_pct} per cent of all its expenditure, and {fn_to_1718_pct} per cent of its expenditure on work types
  that name forest, is on works started in or before that year. The column's heading says so. It is mostly where
  works were put up to then, and it is not current allocation. {fn_units} units have any such expenditure recorded,
  and {fn_only_later} of them show only works started later; the other {fn_none} have none recorded.
- **Scheduled Tribe share can filter the list and never orders it.** The filter has three settings, and they are the
  class breaks of the existing Scheduled Tribe layer (`docs/LAYER.md`), chosen there and not here: eighteen per cent
  or more, above thirty-three per cent, and more than fifty per cent (a share that prints as exactly thirty-three is
  in that layer's class below the break, so the middle setting is labelled "above"). The order within the list does not change. Outside-village units have no census data, so the filter cannot be applied
  to them: a box keeps them in the list or leaves them out, and the page says how many either way.
- **What is blank.** `st_share` is blank for {st_blank} LGD panchayat units (no resident population in the census
  rows) and `adi_2011` for {adi_blank}. The list says which, in words. For the {n_out} outside-village units both
  columns read "no census data for this land", never blank and never zero (§12).
- **Whether Scheduled Tribe share belongs in a shared ranked list is the Foundation's call.** `docs/LAYER.md` §9
  records, with its page reference, that the Commons Connect paper reports that in one of its pilot blocks, Angul, in
  this state, the community did not favour the mapping of inequity. That paper is not among the files registered in
  `00_raw/`, so this document repeats the record and has not read the paper again.
- **SHRUG-derived columns stay out**, as before: no poverty estimate is in the decision table, the view or the export.
  One judgement recorded earlier carries over: the development index of 2011 is kept in the layer on the reading, set
  out in `docs/DATA_NOTES.md`, that it is computed from census rows; a stricter reading of SHRUG's terms would remove
  it. **By the owner's ruling of 9 October 2026 it is no longer a column of the exported list**, which is the file that
  gets passed on; it stays in the interactive view, as a layer of its own and as a column of the list on the page.
  The copy of the layer made to be passed on (§14) is that interactive view, so the index is in it; the exported file
  is not. Whether Scheduled Tribe share belongs in a list that is passed on is still the Foundation's call.
""")

    # ==== 11. corroboration ===================================================================================================================
    BADGE = (("both measures flag it", "both"), ("only Hansen", "hansen_only"), ("only CoRE Stack", "corestack_only"), ("neither", "neither"), ("not compared", "not_compared"))
    BASIS = (("compared, in the headline of the agreement test", "headline"), ("compared, under the East Coast zone model: badge carries the note", "east_coast_every_unit_kept"),
             ("not compared: below the agreement test's floor", "below_floor"), ("not compared: below the floor, and CoRE Stack gives no class on such land", "below_floor_no_corestack_coverage"),
             ("not compared: at or above the floor on Hansen's grid, and CoRE Stack gives a class on less of that land than the floor", "corestack_covers_under_floor"))

    def cb2(basis, badge):
        return count(CU, f"rows whose `corroboration_basis` is {basis} and whose `corroboration` is {badge}", lambda t: (t.corroboration_basis == basis) & (t.corroboration == badge))

    def nb(basis):
        return count(CU, f"rows whose `corroboration_basis` is {basis}", lambda t: t.corroboration_basis == basis)

    table("T_corro", ["what the badge rests on", "units"] + [lab for lab, _ in BADGE], [[lab, c(nb(b), n0)] + [c(cb2(b, k), n0) for _, k in BADGE] for lab, b in BASIS])
    same("units over the five bases of the badge, and the units", sum(nb(b).v for _, b in BASIS), n_units.v)
    for k in ("both", "hansen_only", "corestack_only", "neither"):
        same(f"headline units whose badge is {k}, and the agreement record's own count of that class", cb2("headline", k).v, key(AP, f"counts/by_level/all units/{k}").v)
    ec = show("ec_units", nb("east_coast_every_unit_kept"), n0)
    same("units whose badge carries the East Coast note, and the agreement record's count of units left out by the zone model", ec.v, key(AP, "counts/by_level/all units/zone_model_excluded").v)
    show("ec_districts", cell(AZ, "n_districts", zone_model_of_the_units_valued_land="ECPHR only"), n0)
    same("units under the East Coast zone model: in the decision table and in the table by zone", ec.v, cell(AZ, "n_assessed", zone_model_of_the_units_valued_land="ECPHR only").v)
    notc = show("not_compared", count(CU, "rows whose `corroboration` is not_compared", lambda t: t.corroboration == "not_compared"), n0)
    same("units not compared, and the agreement record's count of units with insufficient forest", notc.v, key(AP, "counts/by_level/all units/insufficient_forest").v)
    hold(set(T.corroboration_window.dropna()) == {"2017-2023"} and T.corroboration_window.notna().all(), "every unit's badge carries the window 2017-2023")
    table("T_cell_corro", ["cell, in the default window", "units"] + [lab for lab, _ in BADGE],
          [[c(name[x], txt), c(nc(DEFAULT, x), n0)] + [c(count(CU, f"rows whose `cell_{DEFAULT}` is {x} and whose `corroboration` is {k}", lambda t, x=x, k=k: (t[f"cell_{DEFAULT}"] == x) & (t.corroboration == k)), n0) for _, k in BADGE] for x in ORDER + [UNRANKED]])
    calc("compared", n_units.v - notc.v, n0, "units less the units not compared", [n_units, notc])
    show("noclass_units", nb("below_floor_no_corestack_coverage"), n0)
    show("noclass_noland", count(CU, "rows whose `corroboration_basis` is below_floor_no_corestack_coverage and whose `agreement_reference_ha` is zero", lambda t: (t.corroboration_basis == "below_floor_no_corestack_coverage") & (t.agreement_reference_ha == 0)), n0)
    hold(bool((T.loc[T.corroboration == "not_compared", "agreement_reference_ha"].lt(floor.v) | T.loc[T.corroboration == "not_compared", "agreement_corestack_valued_ha"].lt(floor.v)).all()),
         "every unit that was not compared is under the agreement test's floor on one of its two grids: no unit is left out for want of CoRE Stack coverage alone")

    DOC.append("""
## 11. Corroboration: what the existing comparison already says

No new agreement statistic was built. Each unit carries what the existing two-measure comparison
(`20_degradation/agreement_by_unit.csv`) already says of it: both measures flag it, only Hansen, only CoRE Stack,
neither, or not compared, with the reason.

{T_corro}

*n = {n_units} units: {compared} compared, {not_compared} not. The first row's four counts equal the agreement
record's own; so do the East Coast count and the count not compared.*

- **The badge has its own window, 2017–2023**, and is labelled with it whatever window the user has chosen. With the
  window set to 2017–2023 the cell and the badge are about the same years; in any other window they are not, and the
  label is there so that nobody reads them as if they were.
- **The {ec_units} units under CoRE Stack's East Coast zone model** carry a note on the badge: the placebo failed
  there, so corroboration is unreliable (`docs/RESULTS.md` §5.2). That failure itself rests on {ec_districts}
  districts. Their class is the one computed with every unit
  kept, since the headline leaves them out.
- **A flag is relative.** It marks the top fifth of the units compared on that measure, not a stated amount of loss
  or degradation (`docs/RESULTS.md` §5).
- **"Not compared" is most units**, and the reason is always the floor of the agreement test, which the decision view
  does not use. So most small forest sites have a cell and no badge.
- **"No CoRE Stack coverage" turned out not to be a reason of its own.** The owner expected two reasons for a unit not
  being compared: below the floor, or no CoRE Stack coverage. Every unit not compared is below the floor on one of the
  two grids. In {noclass_units} of them CoRE Stack assigns no class to the unit's land with canopy above ten per cent
  in 2000 - in {noclass_noland} because the unit has no such land at all. That is what their badge says. It does not
  mean the product fails to reach the unit. (The table's code for this basis, `below_floor_no_corestack_coverage`,
  keeps its first name; the words shown are the ones above.)
- **The counts in the last table but one are by basis; pooled, they would mix two cut-offs.** A flag in the first row
  is cut among the headline's units, a flag in the second among every unit kept. The run record labels the pooled
  counts "do not quote". The table below pools them by cell, and is to be read with that in mind.

How the badge falls across the cells, in the default window:

{T_cell_corro}

*n = {n_units} units. The badge is of 2017–2023 and the cells here are of 2018–2025: the two are not the same years.*
""")

    # ==== 12. outside-village units ===========================================================================================================
    out = T[T.outside_village == 1]
    prompts = sorted(set(out.governance_prompt.dropna()))
    hold(len(prompts) == 1 and out.governance_prompt.notna().all() and T.loc[T.outside_village == 0, "governance_prompt"].isna().all(), "one governance prompt is carried by every outside-village unit and by no other")
    hold(prompts[0] == "No revenue village — this land is in no village plan. Whose plan covers it?", "the governance prompt is the owner's sentence, word for word, with its dash")
    show("gov_prompt", V(prompts[0], CU, "column `governance_prompt`: the one text every outside-village unit carries"), txt)
    sf_all = agg(CU, "`standing_forest_ha` summed over all units", lambda t: t.standing_forest_ha.sum())
    sf_out = agg(CU, "`standing_forest_ha` summed over the outside-village units", lambda t: t.loc[t.outside_village == 1, "standing_forest_ha"].sum())
    calc("out_forest_pct", 100 * sf_out.v / sf_all.v, dec(1), "standing forest in outside-village units ÷ standing forest in all units × 100", [sf_out, sf_all])
    calc("out_unit_pct", 100 * n_out.v / n_units.v, dec(1), "outside-village units ÷ units × 100", [n_out, n_units])
    CHECKS = (("the name on its boundary polygon; none of the district checks' flags is raised", "name_on_the_polygon_not_contradicted"), ("moved off the name on its polygon", "moved_off_the_name"), ("its polygon names no district", "polygon_has_no_name"),
              ("ambiguous between two districts", "ambiguous"), ("flagged: one check contradicts the district it carries", "flagged_one_check_contradicts"), ("no check possible", "no_check_possible"))
    known = {k for _, k in CHECKS}
    hold(set(p for v in out.district_check for p in str(v).split("; ")) <= known and out.district_check.notna().all(), "every outside-village unit carries a district check, and every status is one of the six listed")

    def nchk(k):
        return count(CU, f"outside-village rows whose `district_check` names {k}", lambda t: (t.outside_village == 1) & t.district_check.fillna("").apply(lambda v: k in v.split("; ")))

    table("T_check", ["what the assigned district rests on", "outside-village units"], [[lab, c(nchk(k), n0)] for lab, k in CHECKS])
    for k in ("moved_off_the_name", "polygon_has_no_name", "ambiguous", "flagged_one_check_contradicts", "no_check_possible"):
        same(f"outside-village units whose district check names {k}, and the decision record's count checked against the district record", nchk(k).v, key(DP, f"checks_passed/district_check_counts_equal_the_district_records_own/{k}").v)
    ODC = "10_units/outside_village_district.csv"
    od = W.C(ODC).set_index("unit_id")
    plain_ids = set(out.loc[out.district_check == "name_on_the_polygon_not_contradicted", "unit_id"])
    show("plain_other_code", V(int((od.index.isin(plain_ids) & od.neighbours_by_code_district_code.notna() & (pd.to_numeric(od.neighbours_by_code_district_code, errors="coerce") != pd.to_numeric(od.pc11_district_code, errors="coerce"))).sum()), ODC,
                               "rows whose `neighbours_by_code_district_code` is present and is not their `pc11_district_code`, among the units whose `district_check` in the decision table is name_on_the_polygon_not_contradicted"), n0)
    show("plain_other", V(int(((od.index.isin(plain_ids)) & (od.neighbours_agree_with_assigned.astype(str).isin(["0", "0.0"]))).sum()), ODC,
                          "rows whose `neighbours_agree_with_assigned` is 0, among the units whose `district_check` in the decision table is name_on_the_polygon_not_contradicted"), n0)
    more = int((out.district_check.str.contains("; ")).sum())
    show("check_two", V(more, CU, "outside-village rows whose `district_check` names more than one status"), n0)

    DOC.append("""
## 12. The outside-village units

The {n_out} outside-village units are land outside any revenue village. They have forest: they are {out_unit_pct} per
cent of the units and hold {out_forest_pct} per cent of all standing forest. So they are classed and ranked like any
other unit, and {out_ranked} of them are in a ranked cell in the default window (§9).

Their panel differs in three ways.

- **A governance prompt**, in these words: "{gov_prompt}"
- **What their district rests on.** An outside-village unit has no census district; one was assigned in `10_units/`,
  and the panel shows how that assignment was checked:

{T_check}

*n = {n_out} outside-village units. A unit can carry more than one of these statuses ({check_two} of them do), so the
column can add to more than n. LGD panchayat units carry none: their district is the census's.*

  The first status means that none of the flags of `10_units/` is raised, which is less than "every check agrees":
  in {plain_other} of those units the neighbours' largest district is another one by the tally the rule uses, by
  name ({plain_other_code} by the tally by census code, which the record reports beside it), and the rule of `10_units/` flags
  that only when the unit's own district is absent from its neighbours altogether.

- **Need columns read "no census data for this land"**, never blank and never zero. The census has no rows for this
  land. A zero would be a claim.
""")

    # ==== 13. work types =======================================================================================================================
    WF = "55_decision/work_rows_naming_forest.csv"
    show("so_doc", key(SP, "document"), txt)
    show("so_url", key(SP, "source_url"), txt)
    so_bytes = show("so_bytes", key(SP, "inputs/0/bytes"), n0)
    so_sha = show("so_sha", key(SP, "inputs/0/sha256"), txt)
    mrow = cell(MAN, "bytes", item_id="vbgramg_permissible_works_so5448e_pdf")
    same("bytes of the Gazette file in the manifest row and in the extract's record", mrow.v, so_bytes.v)
    hold(cell(MAN, "ref", item_id="vbgramg_permissible_works_so5448e_pdf").v == key(SP, "source_url").v, "the manifest row carries the address the extract's record names")
    how = cell(MAN, "how_verified_2026_10_04", item_id="vbgramg_permissible_works_so5448e_pdf").v
    hold(so_sha.v in how and "2026-10-08" in how, "the manifest row carries the file's sha256 and the date it was registered")
    pdf = ROOT / key(SP, "inputs/0/path").v
    if pdf.is_file():
        same("bytes of the Gazette file on disk and in the manifest row", pdf.stat().st_size, mrow.v)
        hold(W.sha256(pdf) == so_sha.v, "the Gazette file on disk has the sha256 the manifest row carries")
        show("so_ondisk", V("is on this machine and has that size and hash", "this run", "the file was read and hashed by this script"), txt)
    else:
        show("so_ondisk", V("is not on this machine (it is a fetched file, kept out of git): the size and hash are the manifest's", "this run", "the file was looked for by this script"), txt)
    show("n_manifest_rows", count(MAN, "rows whose `item_id` begins vbgramg_", lambda m_: m_.item_id.astype(str).str.startswith("vbgramg_")), n0)
    so_rows = show("so_rows", key(SP, "checks_passed/rows"), n0)
    sched = W.C(ST)
    same("rows of the table of permissible works, and the rows its record says it has", len(sched), so_rows.v)
    same("rows of the table, and the total the Ministry's release prints", so_rows.v, key(SP, "checks_passed/rows_equal_the_ministrys_published_total").v)
    hold(list(sched.serial) == list(range(1, len(sched) + 1)), "the serial numbers of the table run from one to its number of rows without a gap")
    cats = W.J(SP)["checks_passed"]["rows_by_category_equal_the_ministrys_published_totals"]
    same("rows in the four categories, and the rows", sum(cats.values()), so_rows.v)
    for k, v in cats.items():
        same(f"rows of category {k} counted in the table, and the Ministry's published total for it", int((sched.category == k).sum()), v)
    show("so_cats", V(", ".join(f"{v:,}" for v in cats.values()), SP, "key `checks_passed` → `rows_by_category_equal_the_ministrys_published_totals`"), txt)
    show("so_totals_from", key(SP, "checks_passed/published_totals_from"), txt)
    show("so_totals_url", key(SP, "totals_url"), txt)
    hold(cell(MAN, "ref", item_id="vbgramg_permissible_works_pib_release_2319426").v == key(SP, "totals_url").v and any("pib_" in x["path"] for x in W.J(SP)["inputs"]),
         "the release the totals are read from is registered: the extract's record lists it among its inputs and the manifest has a row for it")
    walked = show("so_walked", key(SP, "checks_passed/rows_walked_in_the_pdfs_own_order_each_work_type_and_name_whole_and_on_its_own_row"), n0)
    same("rows walked in the PDF's own order, and the rows", walked.v, so_rows.v)
    show("so_heads", key(SP, "checks_passed/sub_item_headings_met_on_the_way_and_held_word_for_word"), n0)
    show("so_cat_heads", key(SP, "checks_passed/category_headings_met_on_the_way_and_held_word_for_word"), n0)
    same("rows that begin on their own page and line with both cells at their columns' edges, and the rows", key(SP, "checks_passed/rows_that_begin_on_their_own_page_below_the_row_before_with_both_cells_on_one_line_at_their_columns_left_edges").v, so_rows.v)
    so_cells = show("so_cells", key(SP, "checks_passed/rows_whose_two_cells_read_whole_from_the_positions_of_the_words_are_the_transcriptions"), n0)
    same("rows whose two cells, read whole from the positions of the words, are the transcription's, and the rows", so_cells.v, so_rows.v)
    hold(key(SP, "checks_passed/spaces_inside_headings_are_compared").v is True, "the list's headings were compared with their spaces as printed")
    hold(key(SP, "checks_passed/capitals_are_compared").v is True and key(SP, "checks_passed/dashes_are_compared").v is True and key(SP, "table/blank_cells").v == 0, "the list's table was compared with capitals and dashes kept, and has no blank cell")
    tr_n = show("tr_n", key(TRIALS, "errors_tried"), n0)
    same("deliberate errors tried on the list's check, and those that stopped it", tr_n.v, key(TRIALS, "errors_that_stopped_the_run").v)
    hold(key(TRIALS, "control_was_written").v is True and key(TRIALS, "script_sha256").v == W.sha256(W.use("00_raw/06_scheme/_build_schedule_extract.py")), "the trials of the list's check were made with the script that is on disk, and the unaltered transcription passed")
    show("tr_list", V(words(x["error_put_into_the_transcription"] for x in key(TRIALS, "trials").v if not x["error_put_into_the_transcription"].startswith("control")), TRIALS, "key `trials`: the errors tried"), txt)
    show("so_not_checked", V(words(key(SP, "not_checked").v), SP, "key `not_checked`"), txt)
    hold(bool(key(DP, "work_types/registered").v), "the decision stage found the registered list and built its work-type fields from it")
    pending = key(DP, "work_types/field_when_not_registered").v
    hold(pending == "pending — schedule not yet registered" and not (W.C(WT).work_type_field == pending).any(), "no cell's work-type field reads 'pending': the list is registered")
    show("pending_text", V(pending, DP, "key `work_types` → `field_when_not_registered`"), txt)
    # every serial a cell cites is in the table; the work named beside it is that row's work, under that row's own work type
    cited = set()
    for _, r_ in W.C(WT).iterrows():
        for s_ in ([] if pd.isna(r_.entries) else str(r_.entries).split("; ")):
            row_ = sched[sched.serial == int(s_)]
            hold(len(row_) == 1 and f"Sl. {int(s_)} {row_.work_name.iloc[0]}" in r_.work_type_field, f"the work a cell's field names beside serial number {int(s_)} is that row of the registered table, word for word")
            hold(re.search(re.escape(row_.work_type.iloc[0]) + r" - (?:Sl\. \d+ [^;.]+; )*Sl\. " + str(int(s_)) + " ", r_.work_type_field) is not None, f"serial number {int(s_)} stands under its own work type in a cell's field")
            cited.add(int(s_))
    show("cited_n", V(len(cited), WT, "column `entries`: the number of distinct serial numbers cited"), n0)
    absent = key(DP, "work_types/words_in_no_row_of_the_list").v
    blob = " ".join((sched.work_name + " " + sched.work_type + " " + sched.category_heading + " " + sched.sub_item_heading).str.lower())
    hold(all(w.lower() not in blob for w in absent), "none of the words the record lists as absent is in any row, type or heading of the registered table")
    show("absent_words", V(words(absent), DP, "key `work_types` → `words_in_no_row_of_the_list`"), txt)
    hold(not any(re.search(r"cost|rate|rupee|unit_cost|amount", col.lower()) for col in sched.columns), "the registered table has no column of cost, rate or amount")
    table("T_work", ["cell", "its work-type field, as every unit of the cell shows it"], [[c(name[x], txt), c(cell(WT, "work_type_field", cell=x), txt)] for x in ORDER + [UNRANKED]])
    show("work_note", V(sorted(set(W.C(WT).note))[0], WT, "column `note`: the one note every row carries"), txt)
    hold(len(set(W.C(WT).note)) == 1, "every cell's work-type field carries the same note")
    act = cell(MAN, "title", item_id="vbgramg_act_36_of_2025_pdf")
    show("act_title", act, txt)
    wf = W.C(WF)
    forest_rows = show("forest_rows", V(len(wf), WF, "its rows: every row of the list whose work type or name holds the word forest"), n0)
    same("rows of the list that hold the word forest: in the decision stage's table and counted here in the registered list", forest_rows.v, int((sched.work_name + " " + sched.work_type).str.lower().str.contains("forest").sum()))
    uncited = wf[wf.cited_by_cells.isna()]
    show("forest_uncited", V(len(uncited), WF, "rows whose `cited_by_cells` is blank"), n0)
    hold(set(wf.loc[wf.cited_by_cells.notna(), "serial"]) <= cited and 375 in set(uncited.serial), "every forest-named row marked as cited is cited by a cell, and the last row of the list is among those cited by none")
    table("T_uncited", ["serial number", "work type", "work name"],
          [[c(cell(WF, "serial", serial=int(s_)), lambda x: f"Sl. {int(x)}"), c(cell(WF, "work_type", serial=int(s_)), txt), c(cell(WF, "work_name", serial=int(s_)), txt)] for s_ in uncited.serial])
    last = sched.iloc[-1]
    show("last_row", V(f"Sl. {int(last.serial)}, {last.work_type}: {last.work_name}", ST, "its last row: serial, work type and work name"), txt)
    show("last_sub", V(f"({last.sub_item}) {last.sub_item_heading}", ST, "the sub-item heading of its last row"), txt)

    DOC.append("""
## 13. Work types: the official list of permissible works

**The list was found, verified and registered.** It is: {so_doc}. Source: {so_url}, {so_bytes} bytes, `sha256`
`{so_sha}`. The file {so_ondisk}. `00_raw/data_manifest.csv` has {n_manifest_rows} rows for this: the list with its
address, bytes, hash and date; the transcription; the table made from it; the Act it is issued under ({act_title});
and the Ministry's press release that prints the list's totals. The release was added after the first review and
the check was made stronger after each of the three. So `00_raw/` was written to more than once for this. Against the
last commit it is addition only: nothing that was in `00_raw/` before is changed. Within this batch it is not: the
check script there was rewritten in place after each review, the run record it writes was overwritten each time it
ran, and the notes of the new manifest rows were reworded to match. The table itself came out the same, byte for
byte, every time (its hash is in the manifest), and the
committed manifest's rows are untouched (§16).

**It was checked against the source's own totals.** `00_raw/06_scheme/_build_schedule_extract.py` stops unless the
table has {so_rows} rows numbered without a gap, the total the Ministry's release prints, and unless the rows in the
Act's four categories number {so_cats}, the totals the same release prints ({so_totals_from}; {so_totals_url}). The
release is registered and the totals are read out of its text, not typed. This script counted the categories again.

**And against the Gazette itself, cell by cell.** The script walks the text of the Gazette's English table once, in
the Gazette's own order, with capitals and dashes kept: each of the {so_walked} rows must come next, its work name whole, with
exactly its own work type before it and nothing between rows but the pages' running heads and the {so_heads} sub-item
and {so_cat_heads} category headings, each word for word; straight after the last row must come the notification's
file number. Where a work type ends and its name begins cannot be seen in running text, so that is taken from the
positions of the words on the page: every row must begin on the page the transcription gives it, below the row
before, on a line where the first word of its work type stands at the left edge of the second column and the first
word of its work name at the left edge of the third; and then its two cells, read whole from where the words stand -
every word from that line down to the line the next row begins on, split at the line between the two columns - must
be the transcription's. {so_cells} rows read so. It was tried on {tr_n} deliberate errors put into a copy of the
transcription, and each stopped it: {tr_list}. The record of those trials is a working file of the session (§20).
What the trials show is that these errors stop it, not that no error could pass: two earlier forms of this check
passed their own trials and let through errors a reviewer then found.

**What was not checked**, in the extract's own words: {so_not_checked}.

**Only this list is used.** No count or list of works from anywhere else enters the work-type fields: not the count in
`README.md`, which the manifest's note attributes to an earlier list circulated for comments (that letter is not
registered here), and none from the owner's earlier messages. Had the
list not been found, every field would read "{pending_text}".

Each cell's field, as it appears in "why this tier" on every unit of the cell. Each group of rows stands under the
list's own work type for those rows:

{T_work}

*Six cells; {cited_n} distinct rows of the list are cited, each by its serial number, and this script checked that the
work named beside each number is that row of the table and that it stands under that row's own work type.*

Every field is followed in the panel by this note: "{work_note}"

**The rows that name forest and are cited by no cell.** {forest_rows} rows of the list hold the word forest in their
work type or name. {forest_uncited} of them are cited by no cell. They are listed so that the Foundation can see what
was passed over, and overrule it:

{T_uncited}

*n = {forest_uncited} rows; the rule is the word "forest" in the row's work type or work name, which takes in
"afforestation" and "forestry".*

One of them needs saying aloud. The list's own item for forest work is "{last_sub}", and it has a row that is neither
fire nor planting and that no cell cites: {last_row}. Whether trenches of that kind protect a forest from grazing, or
fields from wild animals, the list does not say, so this project did not assign the row; the Foundation will know.

Four limits on what this mapping is.

- **No row of the list names forest land.** The list names works, and for some of them a kind of place ("wasteland",
  "in fields", "along the coastline"); none says a work may be done on forest land.
- **Assisted natural regeneration is not a work the list names.** These words are in no row, type or heading of the
  table: {absent_words}. The cell with the most units among the forest sites points to that work (§7), so for it the
  field names the rows that could support it and says the work itself is absent.
- **Which rows bear on which cell is this project's proposal**, to be set with the Foundation. The list does not sort
  its works by the condition of a forest.
- **The list carries no unit, rate or cost.** The plantation unit cost under the scheme therefore stays blank, as the
  standing rule requires; nothing here supplies it.

The list was three days old when it was registered and can be amended by a later notification. It should be checked
again before a later use.
""")

    # ==== 14. the overlay ========================================================================================================================
    for nm, k in (("ov_provider", "provider"), ("ov_url", "url_template"), ("ov_doc", "documented_at"), ("ov_doc_is", "documentation_is"), ("ov_version", "data_version"), ("ov_pinned", "version_is_pinned"),
                  ("ov_canopy", "canopy_setting"), ("ov_tiles", "tiles_are"), ("ov_attr", "attribution"), ("ov_licence", "data_licence"), ("ov_terms_url", "terms_url"), ("ov_terms_cover", "terms_cover"), ("ov_terms", "terms_say"),
                  ("ov_attr_page", "attribution_requirements_page"), ("ov_unresolved", "terms_unresolved"), ("ov_verified", "verified_utc"), ("ov_how", "verified_how"), ("ov_years", "year_parameters"), ("ov_zoom_is", "max_native_zoom_is"),
                  ("ov_sent", "what_is_sent")):
        show(nm, key(OV, k), (lambda x_: txt(x_).replace("|", "\\|")) if nm == "ov_terms_cover" else txt)          # a bar inside a table's cell is written so that it does not end the cell
    show("ov_through", key(OV, "loss_through_year"), txt)
    show("ov_zoom", key(OV, "max_native_zoom"), txt)
    ver = re.search(r"v(\d+)\.(\d+)", key(OV, "data_version").v)
    hold(bool(ver) and f"v{ver.group(1)}_{ver.group(2)}" in hansen_ds and f"/v{ver.group(1)}.{ver.group(2)}/" in key(OV, "url_template").v and str(key(OV, "loss_through_year").v) in hansen_ds,
         "the tiles carry the version of Hansen's data that the unit tables are built from, and the address pins that version")
    hold(bool(key(L, "decision_view/overlay/same_version_as_the_unit_tables").v) and key(L, "decision_view/overlay/url_template").v == key(OV, "url_template").v, "the layer's record of its overlay is the registration's")
    hold(int(key(L, "outputs/network_requests").v) == 0, "the layer's own two files ask the network for nothing")
    hold("(1)" in key(OV, "terms_unresolved").v and "(2)" in key(OV, "terms_unresolved").v, "the registration sets out two unresolved points about the provider's terms")
    hold("cannot be determined by subtracting" in key(OV, "provider_cautions").v, "the registration carries the provider's caution against reading present tree cover from the cover of 2000 less loss")
    show("ov_file", key(L, "decision_view/overlay_file/path"), txt)

    def ovstep(record, starts):
        hit = [s for s in W.J(record)["steps"] if s["control"] == "overlay" and s["did"].startswith(starts)]
        if len(hit) != 1:
            stop(f"{record}: {len(hit)} overlay steps whose action starts with {starts!r}, not one")
        return hit[0]

    hold(ovstep(EDC, "opened the page on its ordinary layer")["ok"] and ovstep(EDC, "chose the decision view and read the box")["ok"], "in Chrome the overlay's box is out of reach outside the decision view, and before it is ticked the page has asked the network for nothing")
    on_c = ovstep(EDC, "clicked the box at")
    hold(on_c["ok"] and "tiles came from" in on_c["happened"] and "no other host was asked" in on_c["happened"] and "whole credit" in on_c["happened"], "in Chrome, with a connection, the overlay drew tiles from the registered host, asked no other, and showed the whole credit beside the box and on the map")
    off_c = ovstep(EDC, "set the browser to 'no connection'")
    hold(off_c["ok"] and "nothing was asked of the network (0 requests)" in off_c["happened"] and "needs a connection" in off_c["happened"], "in Chrome, with no connection, the page worked as before, asked the network for nothing, and the control said it needs a connection")
    hold("is not beside this page" in ovstep(EDC, "with the overlay's own file kept from loading")["happened"],
         "in Chrome, with the overlay's own file kept from loading, the control said that the file is not beside the page")
    for rec_, who_ in ((EDC, "Chrome"), (EDW, "WebKit")):
        hid_ = ovstep(rec_, "with the overlay on and the legend hidden")
        hold(hid_["ok"] and "note is still on the map" in hid_["happened"], f"in {who_}, with the legend hidden, the overlay's note - its credit and its window - was still on the map")
    hold(ovstep(EDC, "with a connection but the tile host out of reach")["ok"] and ovstep(EDC, "with the overlay's own file kept from loading")["ok"] and ovstep(EDC, "with the overlay on, clicked the window")["ok"],
         "in Chrome the overlay steps aside when its host cannot be reached or its file is missing, and follows the window when it is on")
    part_c = ovstep(EDC, "ticked the box with a connection")
    hold(part_c["ok"] and "stayed on and SAID so" in part_c["happened"], "in Chrome, when a few tiles failed after others had arrived, the overlay stayed on and said, beside the box and on the map, that pink may be missing")
    lost_c = ovstep(EDC, "with the tile host still cut off")
    hold(lost_c["ok"] and "took itself off" in lost_c["happened"], "in Chrome, when tiles kept failing after some had arrived, the overlay took itself off and said so")
    hold(ovstep(EDC, "the same, zoomed in")["ok"], "in Chrome, zoomed in to where a view asks for only a few tiles and with the host out of reach, the overlay took itself off as unreachable")
    # the pages the registration quotes: copies kept with the session's working files, and each quoted sentence held against them
    import html as _html

    def page_text(name):
        raw_ = W.use(PAGES + name).read_text(encoding="utf-8", errors="replace")
        if name.endswith(".json"):                                   # a record, not a page: its texts as they are (one holds "<" as a sign, which is no tag)
            def texts(x_):
                return [x_] if isinstance(x_, str) else [y_ for v_ in (x_.values() if isinstance(x_, dict) else x_ if isinstance(x_, list) else []) for y_ in texts(v_)]
            raw_ = " ".join(texts(json.loads(raw_)))
        else:
            raw_ = re.sub(r"<[A-Za-z/!][^<>]*>", " ", raw_.replace("\\u003c", "<").replace("\\u003e", ">").replace("\\n", " ").replace('\\"', '"'))
        return " ".join(_html.unescape(raw_).replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u00a0", " ").split())

    quoted = {"terms.html": ["You may not use the Services in any manner that could damage or overburden the Services or interfere with any other party's use of the Services.",
                             "If You use Our APIs in Your own products, please credit Us. You agree to attribute our APIs in line with our Attribution Requirements, available at [https://resourcewatch.org/api-attribution-requirements].",
                             "We may cancel or suspend Your access to the Services at any time and for any reason, without notice.", "each request to an API must include one of Your Account's unique API keys",
                             "resourcewatch.org, globalforestwatch.org, and prepdata.org"],
              "attribution.html": ['Websites that use the Resource Watch API must include the "powered by Resource Watch" logo linking to http://resourcewatch.org on pages that make use of the Resource Watch API.',
                                   "This site is no longer being updated and will be archived in the coming months."],
              "developers.html": ["Some endpoints require users to include an API key with their request"],
              "apikey.html": ["To make most requests to the GFW Data API using third-party applications (e.g., scripts or websites), you need an API key."],
              "dataset.json": ["clearing of at least half of tree cover within a 30-meter pixel", "current (post-2000) tree cover cannot be determined by subtracting figures for annual tree cover loss from year 2000 tree cover",
                               "Comparisons between the original 2001-2010 data and the 2011-2025 update should be performed with caution", "may take the form of natural forests or plantations"]}
    reg_text = " ".join(str(v_) for v_ in W.J(OV).values()).replace("\u2019", "'")
    n_quoted = 0
    for name_, sentences in quoted.items():
        txt_ = page_text(name_)
        for s_ in sentences:
            hold(s_ in txt_, f"the copy of the provider's page kept with the session's working files ({name_}) holds the words the registration quotes: '{s_[:70]}...'")
            if s_.startswith("resourcewatch.org, "):                  # the one the registration gives in its own words: the three sites the terms name
                hold(all(x_ in reg_text for x_ in ("resourcewatch.org", "globalforestwatch.org", "prepdata.org")), f"the registration names the three sites that {name_} says its terms cover")
            else:
                hold(s_.replace('"', "'").split(" [")[0][:60] in reg_text.replace('"', "'"), f"the registration quotes those words of {name_}")
            n_quoted += 1
    show("ov_quoted", V(n_quoted, OV, "the sentences this script looked for in the kept copies of the provider's pages"), n0)
    show("ov_pages", V(len(quoted), "this run", "the kept copies of the provider's pages that this script read"), n0)
    hold(key(PAGES + "openapi.json", "info/title").v == "GFW Tile Cache API" and "/umd_tree_cover_loss/{version}/dynamic/{z}/{x}/{y}.png" in key(PAGES + "openapi.json", "paths").v,
         "the kept copy of the tile service's reference has the path the registration names")
    hold(ovstep(EDC, "with the overlay on, clicked an ordinary layer")["ok"], "in Chrome the overlay goes off when the decision view is left")
    for tag_, rec_, who_ in (("chrome", EDC, "Chrome"), ("webkit", EDW, "WebKit")):
        asked_, drawn_ = key(rec_, "summary/overlay/notes/0/tiles_drawn").v
        show(f"ov_asked_{tag_}", V(asked_, rec_, "key `summary` → `overlay` → `notes` → the first → `tiles_drawn`: its first figure, the tiles asked for"), n0)
        show(f"ov_drawn_{tag_}", V(drawn_, rec_, "key `summary` → `overlay` → `notes` → the first → `tiles_drawn`: its second figure, the tiles drawn"), n0)
        hold(drawn_ == asked_ == key(rec_, "summary/overlay/notes/0/requests_to_the_tile_host").v and asked_ >= 1 and key(rec_, "summary/overlay/notes/0/other_hosts_asked").v == [],
             f"every tile {who_} asked for was drawn - the tiles drawn, the tiles asked for and the requests to the tile host are one number - and no other host was asked")
    show("ov_example", key(EDC, "summary/overlay/notes/0/one_tile_address"), txt)

    DOC.append("""
## 14. The site-level overlay

The units say where to look; they do not show where inside a unit the loss is. For that the layer can lay Hansen's
loss over the map as public map tiles. **It is optional, online, and off unless ticked.**

- **With no network the layer is exactly what it was.** Nothing is asked for until the box is ticked. If the browser
  reports no connection, or the tiles cannot be reached, the box does not stay ticked and the control says the
  overlay needs a connection; if the overlay's file is missing, the box does not stay ticked and the control says the
  file is not beside the page. Everything else works as before.
- **It belongs to the decision view and to nothing else.** Its box is folded away with that view's other controls
  while an ordinary layer is on, and the overlay switches itself off when the view is left. No existing view can show
  it or be changed by it.
- **It does not pretend when tiles fail.** As soon as one tile fails, the control beside the box and the note drawn
  on the map both say that where no pink is drawn, that is not a sign of no loss; by the page's code the warning
  stays until the overlay is drawn again. The note, with the credit, stays on the map when the rest of the legend is
  hidden. What the page has no words for is tiles still on their way: between the tick and the first tile it says
  the overlay is on while no pink is yet drawn, and on a slow connection that can last. When every tile asked for has failed, the overlay takes itself off as unreachable, however few they
  were; when eight in a row fail after some had arrived, it takes itself off as lost. Eight is a round number.
- **It cannot come on behind the user's back.** Its file is asked for on a tick, and if the box has been unticked or
  the view left by the time the file arrives, nothing is drawn.
- **Where its code lives.** The layer's two files, `index.html` and `data.js`, ask the network for nothing, and the
  existing checks that enforce this are unchanged and still pass. The overlay's code is in a third file,
  `{ov_file}`, loaded only when the box is ticked. So the existing statements that the layer is "pre-computed and
  offline" and fetches nothing remain true of the layer with the overlay off, which is how it opens. They are not true
  while the box is ticked, and the layer's About text says so in as many words. One thing about this has to be said
  plainly: the unchanged check `scripts/verify_layer.py` still prints that the page's "own script asks for nothing
  else" than `data.js`. That is true of the page as it opens; the check looks for certain words and cannot see the
  few lines that load the overlay's file on a tick. `scripts/verify_decision.py` pins those lines down instead: one
  script element, one address, reached only from the box's own change.
- **What leaves the machine when it is ticked**, as the registration puts it: {ov_sent}. Nothing about a unit is sent.
  The control says this beside the box.

**The endpoint and its terms, as registered** in `scripts/layer_overlay.json` (as read {ov_verified}):

| | |
|---|---|
| provider | {ov_provider} |
| address | `{ov_url}` |
| where it is documented | {ov_doc} |
| what kind of documentation | {ov_doc_is} |
| data the tiles carry | {ov_version}, loss through {ov_through} |
| the version in the address | {ov_pinned} |
| the years drawn | {ov_years} |
| canopy setting | {ov_canopy} |
| the tiles | {ov_tiles} |
| finest zoom this layer asks for | {ov_zoom}: {ov_zoom_is} |
| licence of the data | {ov_licence} |
| attribution shown, beside the box and on the map | {ov_attr} |
| terms of use | {ov_terms_url} |
| why those terms | {ov_terms_cover} |
| what the terms say | {ov_terms} |
| the attribution page the terms point to | {ov_attr_page} |
| how it was verified | {ov_how} |

**The version.** The tiles carry {ov_version}, the version the unit tables are built from ({hansen_dataset}), and the
address pins it. So no warning about disagreeing versions is needed, and the overlay is labelled with its version all
the same. Two differences remain and are stated on the overlay: its canopy setting takes dense and open forest
together, where the unit tables keep them apart, and it is a picture to find places by, not something to measure from.

**Two points about the terms are unresolved, and they are the owner's to decide** (§17). {ov_unresolved}

**Where the quoted pages are.** By the owner's ruling of 9 October 2026, {reg_pages} of the provider's pages are now
registered in `00_raw/05_forest_reference/`, each with a manifest row giving its address, bytes, `sha256` and date:
the provider's record of the dataset, its terms of service, the attribution page those terms point to, the reference
of the tile service, and the University of Maryland's page for the version of the data used here. They are fetched
files and are not in git.
The registered files are byte for byte the copies read on 8 October 2026. The developer page and the guide to API
keys, which the note on the unresolved terms also quotes, are still only with the session's working files. This
script looked in {ov_pages} of the copies for {ov_quoted} of the sentences the overlay's registration quotes, whole or
by their distinguishing words, and stops if one is missing. It did not look for every quotation.

**The provider's cautions about the data have a home of their own.** `00_raw/05_forest_reference/provider_cautions.json`
holds {caut_n} sentences taken word for word from two of those pages - the provider's record of the dataset and the
University's page - and the four percentages those sentences state. It is made and checked by the script beside it,
and it is in git. The layer's About text quotes the cautions from that file and no longer from the overlay's
registration, so they stay whether or not the overlay is shipped (§18 gives them).

**A copy without the overlay.** `scripts/07_build_share.py` writes `70_share/`: a folder with the layer's `index.html`
and `data.js`, byte for byte, and a README; no `overlay.js`; and a zip of that folder beside it ({share_zip_mb} MB).
The README says how to open the copy, what it is and is not, that the map overlay is not in it, whose data it draws
on ({share_credits} rows, read from the layer's own list of sources) and that terms for passing it on are not yet
agreed. The page in the copy is the same page, so its box "Site-level overlay" is still there. `scripts/exercise_share.py`
opened the copy from disk in Chrome ({share_browser}): {share_steps} of {share_steps} steps did what they should. The
two files are byte for byte the layer's; the page loaded those two files and asked the network for nothing; with the
box ticked the control said "{share_msg}", the box was unticked again and no tile was drawn. The browser logged once
that a file was not found, which is the point of the copy; nothing else was logged. One thing the owner should know:
the copy is the interactive view, so the layer of the development index of 2011 is in it (§10).

**How it behaved under test.** In Chrome, with a connection, ticking the box drew {ov_drawn_chrome} tiles of
{ov_asked_chrome} asked for, from the registered host and no other (one address asked for: `{ov_example}`), with the
whole credit beside the box and on the map; with the browser set to no connection the page opened and worked as
before and asked the network for nothing; with the host cut off after tiles had arrived and the map moved far, the
overlay took itself off;
with a few tiles failing after others had arrived it stayed on and said that pink may be missing; zoomed in, where a
view asks for only a few tiles, it gave up as unreachable just the same; on leaving the decision view it went off. In
WebKit, with a connection, {ov_drawn_webkit} of {ov_asked_webkit} tiles
were drawn. WebKit as driven here cannot be put offline or have an address blocked from outside, so those steps are
Chrome's alone (§16).
""")

    # the provider pages as registered, and the copy without the overlay
    REG = {"gfw_dataset_record_umd_tree_cover_loss": "dataset.json", "gfw_terms_of_service_page": "terms.html", "resourcewatch_api_attribution_requirements_page": "attribution.html",
           "gfw_tile_cache_api_reference_openapi": "openapi.json", "umd_global_forest_change_v1_13_page": "umd_v1_13_download.html"}
    for item_, kept_ in REG.items():
        dest_ = cell(MAN, "dest", item_id=item_).v
        hold(W.sha256(W.use("00_raw/" + dest_)) == W.sha256(W.use(PAGES + kept_)) and int(cell(MAN, "bytes", item_id=item_).v) == W.use("00_raw/" + dest_).stat().st_size and W.sha256(W.use("00_raw/" + dest_)) in cell(MAN, "how_verified_2026_10_04", item_id=item_).v,
             f"the registered page `{dest_}` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256")
    show("reg_pages", V(len(REG), MAN, "the rows of the provider's pages registered on 9 October 2026: their number"), n0)
    show("caut_n", key(CAUT, "checks_passed/sentences_found_word_for_word"), n0)
    hold(W.sha256(W.use(CAUT)) in cell(MAN, "how_verified_2026_10_04", item_id="provider_cautions_extract").v and [i_["sha256"] for i_ in key(CAUT, "inputs").v] == [W.sha256(W.use(i_["path"])) for i_ in key(CAUT, "inputs").v]
         and "provider_cautions" in key(L, "decision_view/cautions_from").v,
         "the extract of the provider's cautions is the file its manifest row describes, it was made from the two registered pages that are on disk, and the layer's record says the About text reads the cautions from it")
    hold(key(SHARE_REC, "layer_run_utc").v == run_l.v and key(SHARE_EX, "copy_run_utc").v == key(SHARE_REC, "run_utc").v and all(s_["ok"] for s_ in key(SHARE_EX, "steps").v)
         and key(SHARE_EX, "summary/index_html_and_data_js_byte_for_byte_the_layers").v is True and key(SHARE_EX, "summary/overlay_js_in_the_copy").v is False and key(SHARE_EX, "summary/requests_to_the_network").v == 0
         and all(key(SHARE_REC, f"the_copy/files/{f_}/sha256").v == W.sha256(W.use(f"60_layer/{f_}")) for f_ in ("index.html", "data.js"))
         and sorted(p_.name for p_ in (ROOT / "70_share" / "odisha_forest_decision_layer").iterdir()) == ["README.txt", "data.js", "index.html"],
         "the copy in `70_share/` is of the layer that is in `60_layer/`, its two files are byte for byte the layer's, it holds a README and no other file, and the check that opened it in Chrome was made on that copy and passed every step")
    show("share_steps", key(SHARE_EX, "summary/steps"), n0)
    show("share_msg", key(SHARE_EX, "summary/what_the_control_said_when_ticked"), txt)
    hold(key(SHARE_EX, "summary/what_the_control_said_when_ticked").v == LAYER_DATA["decision"]["overlay"]["missing"] and "is not beside this page" in key(SHARE_EX, "summary/what_the_control_said_when_ticked").v,
         "what the copy's control said when ticked is the layer's own sentence for a file that is not beside the page")
    show("share_browser", key(SHARE_EX, "browser"), txt)
    show("share_zip_mb", key(SHARE_REC, "the_copy/zip/bytes"), W.mb)
    show("share_credits", key(SHARE_REC, "checks_passed/credits_read_from_the_layers_own_sources"), n0)

    # ==== 15. where the window is named; the export ================================================================================================
    ecols = key(EDC, "summary/export/columns").v
    show("ex_ncols", V(len(ecols), EDC, "key `summary` → `export` → `columns`: their number"), n0)
    show("ex_cols", V(", ".join(f"`{x}`" for x in ecols), EDC, "key `summary` → `export` → `columns`"), txt)
    need = ["district", "unit_id", "unit_type", "window_of_forest_loss", "tier_label", "tier_definition", "tier_order_in_use", "tier_order_is", "order_within_a_tier", "standing_dense_ha", "lost_from_dense_in_window_ha", "standing_open_ha",
            "lost_from_open_in_window_ha", "land_with_10pct_canopy_or_less_in_2000_ha", "lost_on_that_land_in_window_ha_reported_only", "corroboration", "corroboration_window", "outside_village", "layer_built_utc"]
    hold(all(k in ecols for k in need), "an exported row carries district, unit id, unit type, window, tier label, tier definition, the tier order in use and whether it was changed, what orders units within a tier, the six hectare figures, "
                                        "corroboration with its window, the outside-village flag and the build time")
    hold(key(EDW, "summary/export/columns").v == ecols and key(EDC, "summary/export_second/columns").v == ecols, "the export has the same columns in WebKit as in Chrome, and in the second list as in the first")
    for nm, rec_, k_ in (("ex1", EDC, "export"), ("ex2", EDC, "export_second")):
        rws = show(f"{nm}_rows", key(rec_, f"summary/{k_}/rows"), n0)
        same(f"rows in the exported file and rows the tables give for that list ({k_})", rws.v, key(rec_, f"summary/{k_}/rows_expected").v)
        cls_ = show(f"{nm}_cells", key(rec_, f"summary/{k_}/cells_compared"), n0)
        same(f"cells of the exported file compared and cells equal, Chrome ({k_})", cls_.v, key(rec_, f"summary/{k_}/cells_equal").v)
        same(f"rows times columns of the exported file, and the cells compared ({k_})", rws.v * len(ecols), cls_.v)
        hold(key(rec_, f"summary/{k_}/saved_by_the_browser").v is True and key(rec_, f"summary/{k_}/saved_file_equals_the_text_the_page_made").v is True, f"in Chrome the exported file was saved by the browser, read back from disk, and equal to the text the page made ({k_})")
        show(f"{nm}_district", key(rec_, f"summary/{k_}/district"), txt)
        show(f"{nm}_window", key(rec_, f"summary/{k_}/window"), txt)
        show(f"{nm}_filter", key(rec_, f"summary/{k_}/filter"), txt)
        same(f"cells of the exported text compared and cells equal, WebKit ({k_})", key(EDW, f"summary/{k_}/cells_compared").v, key(EDW, f"summary/{k_}/cells_equal").v)
    show("ex1_order", key(EDC, "summary/export/tier_order"), txt)
    show("ex1_no_share", key(EDC, "summary/export/rows_with_no_share"), n0)
    hold(len(ecols) == key(L, "decision_view/export_columns").v and "development_index_2011" not in ecols and key(EDC, "summary/export/development_index_2011_among_the_columns").v is False
         and key(EDC, "summary/export_second/development_index_2011_among_the_columns").v is False and ecols.index("forest_loss_share_pct") == ecols.index("forest_at_window_start_ha") + 1 == ecols.index("forest_loss_in_window_ha") + 2,
         "the exported file has the number of columns the layer's record gives; the development index of 2011 is not among them; the forest at the start of the window and the share follow the forest loss of the window")
    hold("by forest loss in the window where the cell has loss" in key(EDC, "summary/export/order_within_a_tier").v and "as a share of the forest at the start of the window" in key(EDC, "summary/export_second/order_within_a_tier").v
         and key(EDC, "summary/export/rows_with_no_share").v >= 1,
         "of the two lists exported and checked, one was ordered within a tier by hectares lost and one by share lost, and at least one row had no share")
    hold(key(EDC, "summary/export/tier_order_is").v == "an order changed by the user of this page" and key(EDC, "summary/export_second/tier_order_is").v == "the provisional order"
         and key(EDC, "summary/export/window").v != key(EDC, "summary/export_second/window").v, "of the two lists exported and checked, one was made under a changed tier order and one under the provisional order, and they are of different windows")

    DOC.append("""
## 15. Where the window, the thresholds and the order are stated

No screenshot and no exported file should lose which window, which thresholds and which order produced it.

- **The legend**: its title names the window; a note under it gives both thresholds, says what standing forest is in
  the owner's words (§3), and states the tier order in use.
- **Every unit's panel** carries a block, "why this tier", on every unit and not behind any toggle: right under the
  unit's name in the decision view, and after the panel's own sections in every other view, so that the existing
  panels read as they did. In those other views the block is always of the default window and the provisional order,
  whatever was last set in the decision view: its controls are folded away there and the address says nothing of
  them, so the block is what the same address shows on a fresh page. It shows the six hectare figures (standing dense, lost from dense, standing open, lost from
  open, land with ten per cent canopy or less, lost on it), with the window in the table's heading; the sentence that
  puts the unit in its row, with the standing minimum; the sentence that puts it in its column, with the loss minimum;
  the forest at the start of the window and the loss as a share of it, or the words that say why no share is given;
  the grid of six cells with the unit's own outlined; the cell's place under the tier order in use, and the one line
  of reason for that place (when the user has changed the order, it says that the reason is the one given for the
  cell's provisional place); the corroboration badge with its own window; and the work-type field (§13). For an
  outside-village unit it adds the governance prompt and what the district rests on (§12).
- **The head of the ranked list** names the district, the window and the tier order, says which of the two orders
  within a tier is in use (by hectares lost, or by share lost: §5.4), and under a filter says what was left out.
- **Every row of an exported list** carries all of it. **The export has {ex_ncols} columns**: {ex_cols}. By the
  owner's ruling of 9 October 2026 the development index of 2011 is not among them, and the forest at the start of the
  window and the loss as a share of it are. Where a unit has no share the cell says so in words.
- **The address** of a decision view says all of it too: the window, the district, the order of tiers where the user
  changed it, the filter, and the order within a tier where it is by share. A part left out means its default, on a page already open as on a fresh one. The
  address of an ordinary layer carries nothing of the decision view, as before.

Two exports were opened and checked field by field, each value under its own column name and the names held against
a list written out in the check, so that neither the window nor the order in the file could be a constant and no name
could drift from its value. The first: {ex1_district}, window {ex1_window}, under an order the user had changed
("{ex1_order}") and a filter ("{ex1_filter}"): {ex1_rows} rows, as the tables give, and all {ex1_cells} cells equal
to the tables. The
second: {ex2_district}, window {ex2_window}, the provisional order, "{ex2_filter}", ordered by share within a tier:
{ex2_rows} rows and all {ex2_cells} cells equal. Each row said which order of tiers had made it and what ordered the
units within a tier; the first list was ordered by hectares lost and the second by share. {ex1_no_share} row of the
first list had no share and said so in words. An empty list is not offered as a file: with no row
to carry the window, the export button is off.
""")

    # ==== 16. verification =========================================================================================================================
    for rec, nm in ((EXC, "exercise_chrome.json"), (EXW, "exercise_webkit.json"), (EDC, "exercise_decision_chrome.json"), (EDW, "exercise_decision_webkit.json")):
        hold(key(rec, "summary/layer_run_utc").v == run_l.v, f"`60_layer/{nm}` is the record of a run on the layer that is in `60_layer/`")
    for rec in (EDC, EDW):
        hold(key(rec, "summary/decision_table_run_utc").v == run_d.v and key(rec, "summary/script_errors").v == [], "the decision view's exercises ran on the decision table that is in `55_decision/` and the page raised no script error")
    for nm, rec in (("xc", EXC), ("xw", EXW)):
        a_, b_ = show(f"{nm}_actions", key(rec, "summary/controls_exercised"), n0), key(rec, "summary/controls_as_expected")
        same(f"actions exercised and actions as expected, existing views, {rec}", a_.v, b_.v)
        v_, e_ = show(f"{nm}_values", key(rec, "summary/values_compared"), n0), key(rec, "summary/values_equal")
        same(f"values compared and values equal, existing views, {rec}", v_.v, e_.v)
        show(f"{nm}_units", key(rec, "summary/units_clicked"), n0)
        hold(key(rec, "summary/script_errors").v == [], f"the existing views raised no script error in {rec}")
    show("chrome_is", key(EXC, "summary/browser"), txt)
    show("webkit_is", key(EXW, "summary/browser"), txt)
    for nm, rec in (("dc", EDC), ("dw", EDW)):
        a_, b_ = show(f"{nm}_actions", key(rec, "summary/steps"), n0), key(rec, "summary/steps_as_expected")
        same(f"steps and steps as expected, decision view, {rec}", a_.v, b_.v)
        v_, e_ = show(f"{nm}_lines", key(rec, "summary/lines_compared"), n0), key(rec, "summary/lines_equal")
        same(f"lines of 'why this tier' compared and lines equal, {rec}", v_.v, e_.v)
        show(f"{nm}_units", key(rec, "summary/units_opened"), n0)
        hold(key(rec, "summary/clicks_that_opened_nothing").v == 0 and key(rec, "summary/clicks_that_opened_a_unit_elsewhere").v == 0, f"in {rec} no click aimed at a unit opened nothing, and none opened a unit that does not touch the one aimed at")
        same(f"units opened as aimed and units opened that touch the one aimed at, and the units opened, {rec}", key(rec, "summary/units_opened_as_aimed").v + key(rec, "summary/units_opened_that_touch_the_one_aimed_at").v, key(rec, "summary/units_opened").v)
        same(f"kinds of corroboration badge seen and kinds there are, {rec}", len(key(rec, "summary/kinds_of_badge_seen").v), key(rec, "summary/kinds_of_badge_there_are").v)
    show("dc_statements", key(EDC, "summary/steps_that_are_statements_and_not_actions"), n0)
    seen = key(EDC, "summary/cells_and_windows_seen").v
    by_w = {}
    for s_ in seen:
        x, w = s_.split(" / ")
        by_w.setdefault(w, set()).add(x)
    full = [w for w, xs in by_w.items() if xs == set(CELLS)]
    hold(len(full) >= 2, "the units opened in Chrome cover all six cells in at least two windows")
    show("dc_windows_full", V(len(full), EDC, "key `summary` → `cells_and_windows_seen`: windows in which all six cells were opened"), n0)
    show("dc_lgd", key(EDC, "summary/by_type/lgd_panchayat"), n0)
    show("dc_out", key(EDC, "summary/by_type/outside_village"), n0)
    same("units opened in Chrome by kind, and the units opened", key(EDC, "summary/by_type/lgd_panchayat").v + key(EDC, "summary/by_type/outside_village").v, key(EDC, "summary/units_opened").v)
    show("dc_out_districts", V(len(key(EDC, "summary/districts_of_outside_village_units_opened").v), EDC, "key `summary` → `districts_of_outside_village_units_opened`: their number"), n0)
    show("dc_neighbour", key(EDC, "summary/units_opened_that_touch_the_one_aimed_at"), n0)
    show("dc_badges", key(EDC, "summary/kinds_of_badge_there_are"), n0)
    show("arrows_pressed", key(EDC, "summary/tier_arrows_pressed"), n0)
    show("arrows_all", key(EDC, "summary/tier_arrows_there_are"), n0)

    # the replication (a working file of the session): made on 8 October 2026, on the table as it stood then
    show("rp_cells", key(RP, "cells_compared_each"), n0)
    hold(key(RP, "table_sha256").v == key(GATE, "table_before_is_the_one_ruled_on_sha256").v and key(GATE, "table_now_sha256").v == W.sha256(W.use(CU)),
         "the replication's record is of the table the rename gate compares with, and that gate was run on the decision table that is in `55_decision/`: so the columns the replication covered are, cell for cell, today's")
    for who in ("a", "b"):
        hold(key(RP, f"replicator_{who}/cells_that_differ_in_value").v == 0, f"replicator {who}'s table has no cell whose value differs from the decision table's")
    show("rp_cols", key(RP, "columns_compared"), n0)
    show("rp_allcols", key(RP, "columns_of_the_table"), n0)
    same("columns of the table that was replicated, and the columns the rename gate found unchanged", key(RP, "columns_of_the_table").v, key(GATE, "columns_the_table_had_before").v)
    show("rp_form", key(RP, "cells_that_differ_only_in_how_they_are_written"), n0)
    show("rp_a", key(RP, "replicator_a/means"), txt)
    show("rp_b", key(RP, "replicator_b/means"), txt)
    show("rp_amb", key(RP, "ambiguities_reported"), n0)
    show("rp_note", key(RP, "note"), txt)
    hold(key(RP, "unit_windows_where_those_columns_are_not_what_the_cell_implies").v == 0 and len(key(RP, "columns_neither_replicator_wrote").v) == key(RP, "columns_of_the_table").v - key(RP, "columns_compared").v,
         "the columns the replicators did not write are the difference between the table's columns and those compared, and none of them says anything the unit's cell does not")
    show("cols_now", V(len(T.columns), CU, "its columns: their number"), n0)

    # the checks of this build: the runner's record, and what it says was not run
    hold(key(RUNS, "layer_run_utc").v == run_l.v and key(RUNS, "one_at_a_time").v is True and "unfinished" not in W.J(RUNS) and key(RUNS, "script_sha256").v == W.sha256(W.use("scripts/run_decision_checks.py")),
         "`60_layer/decision_runs.json` is the finished record of the checks run, one at a time, on the layer that is in `60_layer/`, by the runner as it is on disk")
    checks_run = {x["check"]: x for x in key(RUNS, "checks").v}
    not_run = {x["check"]: x for x in W.J(RUNS).get("checks_not_run_in_this_pass", [])}
    SAFARI = ("exercise_layer_safari, as written", "exercise_decision_safari, by address")
    safari_run = all(k_ in checks_run for k_ in SAFARI)
    hold(safari_run or all(k_ in not_run and not_run[k_]["why"].strip() for k_ in SAFARI), "the two checks in the Safari application were either run in this pass or are named in its record as not run, with the reason")
    hold(set(checks_run) | set(not_run) == {"verify_layer", "verify_decision", "exercise_layer in Chrome", "exercise_layer in WebKit", "exercise_decision in Chrome", "exercise_decision in WebKit"} | set(SAFARI)
         and not set(checks_run) & set(not_run), "the runner's record accounts for each of its eight checks once: run, or named as not run")

    def runs_of(name, tag):
        e = checks_run.get(name) or stop(f"{RUNS}: no check named {name!r}")
        show(f"{tag}_runs", V(e["runs_made"], RUNS, f"key `checks`: `runs_made` of the check '{name}'"), n0)
        show(f"{tag}_pass", V(e["runs_that_passed"], RUNS, f"key `checks`: `runs_that_passed` of the check '{name}'"), n0)
        return e

    for name_ in ("verify_layer", "exercise_layer in Chrome", "exercise_layer in WebKit") + ((SAFARI[0],) if safari_run else ()):
        hold(checks_run[name_]["file_is_as_committed"] is True, f"the script of the check '{name_}' is byte for byte the one in the last commit")
    for name_ in checks_run:
        hold(checks_run[name_]["last_run_passed"] is True, f"the last run of the check '{name_}' on this build passed")
    e_xc, e_wk, e_dc, e_dw = runs_of("exercise_layer in Chrome", "xc"), runs_of("exercise_layer in WebKit", "wk"), runs_of("exercise_decision in Chrome", "dcr"), runs_of("exercise_decision in WebKit", "dwr")
    show("first_try", V(sum(1 for x in checks_run.values() if x["runs"][0]["exit"] == 0), RUNS, "key `checks`: the checks whose first run passed"), n0)
    show("n_checks", V(len(checks_run), RUNS, "key `checks`: their number"), n0)
    failed_wk = [l for r_ in e_wk["runs"] for l in r_["failed_lines"]]
    show("wk_failed_steps", V("none" if not failed_wk else "; ".join(sorted({l.split("->")[0].replace("FAIL", "").strip() for l in failed_wk})), RUNS, "key `checks`: the `failed_lines` of the runs of 'exercise_layer in WebKit'"), txt)

    # the Safari application: its two records, of whatever build they are
    xs_passed = key(EXS, "summary/addresses_tried").v == key(EXS, "summary/addresses_as_expected").v and key(EXS, "summary/values_compared").v == key(EXS, "summary/values_found").v
    show("xs_run", key(EXS, "summary/run_utc"), txt)
    xs_build = show("xs_build", key(EXS, "summary/layer_run_utc"), txt)
    show("xs_addr", key(EXS, "summary/addresses_tried"), n0)
    show("xs_values", key(EXS, "summary/values_compared"), n0)
    p1, p2 = "summary/part1_the_unchanged_scripts_main/", "summary/part2_the_decision_view/"
    s1 = show("ds1_addr", key(EDS, p1 + "addresses_tried"), n0)
    same("part one in Safari: addresses tried and addresses as expected", s1.v, key(EDS, p1 + "addresses_as_expected").v)
    s1v = show("ds1_values", key(EDS, p1 + "values_compared"), n0)
    same("part one in Safari: values compared and values found", s1v.v, key(EDS, p1 + "values_found").v)
    show("ds1_units", key(EDS, p1 + "units_opened_by_address"), n0)
    s2 = show("ds2_addr", key(EDS, p2 + "addresses_tried"), n0)
    same("part two in Safari: addresses tried and addresses as expected", s2.v, key(EDS, p2 + "addresses_as_expected").v)
    s2l = show("ds2_lines", key(EDS, p2 + "lines_compared"), n0)
    same("part two in Safari: lines compared and lines found", s2l.v, key(EDS, p2 + "lines_found").v)
    show("ds2_units", key(EDS, p2 + "units_opened_by_address"), n0)
    show("safari_is", key(EDS, "summary/browser"), txt)
    show("ds_how", key(EDS, "summary/how_the_window_was_read"), txt)
    eds_build = show("eds_build", key(EDS, "summary/layer_run_utc"), txt)
    if safari_run:
        e_xs = runs_of(SAFARI[0], "xsr")
        e_ds = checks_run[SAFARI[1]]
        hold(xs_build.v == run_l.v and eds_build.v == run_l.v and xs_passed and e_xs["last_run_passed"], "the two records the Safari checks wrote are of the layer that is in `60_layer/`, and the unchanged script passed")
        show("xs_closed", V(sum((r_.get("left_over_safari_windows_of_earlier_runs_closed_first") or 0) for r_ in e_xs["runs"] + e_ds["runs"]), RUNS,
                            "key `checks`: `left_over_safari_windows_of_earlier_runs_closed_first`, summed over the runs of the two Safari checks"), n0)
        safari_text = """- **`scripts/exercise_layer_safari.py`, unchanged and run by itself, in the Safari application: passed.** Run
  {xs_run} on the layer built {xs_build}: {xs_addr} addresses showed what they should and {xs_values} values of the
  units' panels were in the page's text. Nothing is clicked in Safari; the page is driven by its address. Runs made
  of it on this build: {xsr_runs}; runs that passed: {xsr_pass}. Before each Safari run the runner closed any window
  an earlier run of these checks had left open, and no other: {xs_closed} in this pass.
- *Added, and not a substitute for the line above:* `scripts/exercise_decision_safari.py` ran the main routine of that
  unchanged script, every address and every comparison of it, in the Safari application ({safari_is}) with one
  function replaced while it ran, the one that reads the window: {ds_how}. So run, on the layer built {eds_build},
  {ds1_addr} of {ds1_addr} addresses showed what they should and {ds1_values} of {ds1_values} values of {ds1_units}
  units' panels were in the page's text."""
        safari_new = """- In the Safari application, by address and with nothing clicked: {ds2_addr} of {ds2_addr} addresses of the decision
  view showed what they should, and {ds2_lines} of {ds2_lines} lines of "why this tier" for {ds2_units} units were in
  the page's text in order."""
    else:
        hold(xs_build.v != run_l.v and eds_build.v != run_l.v and xs_passed and xs_build.v == eds_build.v, "the two records of the Safari checks in `60_layer/` are of an earlier build, the same one, and on it the unchanged script passed")
        show("xs_why", V(not_run[SAFARI[0]]["why"], RUNS, "key `checks_not_run_in_this_pass`: `why`"), txt)
        hold(not_run[SAFARI[0]]["why"] == not_run[SAFARI[1]]["why"], "the record gives one reason for leaving out both Safari checks")
        safari_text = """- **`scripts/exercise_layer_safari.py`, unchanged, in the Safari application: NOT RUN on this build.** The runner's
  record names it as left out and gives the reason: "{xs_why}". Its last record, still in `60_layer/`, is of the run
  of {xs_run} on the layer built {xs_build}, the build the owner ruled on: {xs_addr} addresses showed what they
  should and {xs_values} values of the units' panels were in the page's text. So **the Safari third of the regression
  gate is not shown for the build described here.** What can be said without it: that script reads the existing
  views only; they are drawn by lines of the page that this batch did not touch (the table below) from stage tables
  that did not change; and the same views passed the unchanged exercise in Chrome and in WebKit on this build. That
  is an argument and not a run.
- *The same holds for `scripts/exercise_decision_safari.py`*, which ran the main routine of that unchanged script in
  the Safari application ({safari_is}) with one function replaced, the one that reads the window ({ds_how}): its last
  record is of the layer built {eds_build}, where {ds1_addr} of {ds1_addr} addresses showed what they should and
  {ds1_values} of {ds1_values} values of {ds1_units} units' panels were in the page's text. Not run on this build."""
        safari_new = """- In the Safari application, by address and with nothing clicked: **not run on this build** (the same reason). On
  the build the owner ruled on, {ds2_addr} of {ds2_addr} addresses of the decision view showed what they should, and
  {ds2_lines} of {ds2_lines} lines of "why this tier" for {ds2_units} units were in the page's text in order. That
  build's block had one line fewer: the share was added since, and has been read in Chrome and WebKit only."""
    # the fragility of the Safari and WebKit checks: recorded, as the owner ruled, from the notes and records kept of the builds of 8 October
    show("old_wk_runs", key(RUNS_OLD, "unchanged_webkit_exercise/runs"), n0)
    show("old_wk_fail", key(RUNS_OLD, "unchanged_webkit_exercise/runs_with_a_failed_step"), n0)
    hold(key(RUNS_OLD, "runs").v[2]["exit"] == 1 and "dragged the map" in key(RUNS_OLD, "unchanged_webkit_exercise/the_step_that_failed_once").v and key(RUNS_OLD, "layer_run_utc").v != run_l.v,
         "on an earlier build, the run of the unchanged WebKit exercise that failed a step was the first made of it, and the step was the map drag")
    show("old_build", key(RUNS_OLD, "layer_run_utc"), txt)
    show("xs_earlier", key(RUNS_OLD, "unchanged_safari_script_as_written/earlier_the_same_day_on_an_earlier_build"), txt)
    show("xs_windows", key(RUNS_OLD, "the_owners_safari_windows_on_8_october"), txt)
    first_xs = next(x for x in key(RUNS_FIRST, "checks").v if x["check"] == SAFARI[0])
    hold("unfinished" not in W.J(RUNS_FIRST) and key(RUNS_FIRST, "started_utc").v < key(RUNS, "started_utc").v and all(x["last_run_passed"] for x in key(RUNS_FIRST, "checks").v),
         "the kept record of the pass with a step made by hand is a finished record, made before the pass reported here, in which every check passed on its last run")
    show("xs1_build", key(RUNS_FIRST, "layer_run_utc"), txt)
    show("xs1_runs", V(first_xs["runs_made"], RUNS_FIRST, f"key `checks`: `runs_made` of the check '{SAFARI[0]}'"), n0)
    show("xs1_pass", V(first_xs["runs_that_passed"], RUNS_FIRST, f"key `checks`: `runs_that_passed` of the check '{SAFARI[0]}'"), n0)
    show("xs1_note", key(RUNS_FIRST, "note_added_by_hand"), txt)
    RULED = SCRATCH + "/60_layer_2026-10-08_as_ruled_on/decision_runs.json"            # the runner's record of the build the owner ruled on: a working file
    hold("unfinished" not in W.J(RULED) and key(RULED, "layer_run_utc").v == xs_build.v if not safari_run else "unfinished" not in W.J(RULED), "the kept record of the checks of the build the owner ruled on is a finished record of that build")
    show("ruled_build", key(RULED, "layer_run_utc"), txt)
    show("ruled_n", V(len(key(RULED, "checks").v), RULED, "key `checks`: their number"), n0)
    show("ruled_first", V(sum(1 for x in key(RULED, "checks").v if x["runs"][0]["exit"] == 0), RULED, "key `checks`: the checks whose first run passed"), n0)
    page_ = W.use("60_layer/index.html").read_text(encoding="utf-8")
    hold('(this._element,"leaflet-zoom-anim")||' in page_[page_.find("_onDown:function"):][:260], "the map library embedded in the page ignores a mouse-down on a map that still marks a zoom as under way")
    share_gate = key(SHARE_EX, "run_utc")
    show("share_run", share_gate, txt)
    show("gate_run", key(GATE, "run_utc"), txt)
    import subprocess
    touched = [".gitignore", "00_raw/data_manifest.csv", "scripts/06_build_layer.py", "scripts/layer_template.html"]
    g_ = subprocess.run(["git", "-C", str(ROOT), "diff", "--numstat", BASE, "--"] + touched, capture_output=True, text=True)
    if g_.returncode != 0:
        stop("git could not compare the working tree with the commit this batch started from: " + g_.stderr.strip()[:200])
    num = {l.split("\t")[2]: (int(l.split("\t")[0]), int(l.split("\t")[1])) for l in g_.stdout.strip().splitlines() if l.count("\t") == 2}
    hold(set(num) == set(touched) and all(v_[1] == 0 for v_ in num.values()), "the four tracked files that existed before and were changed have lines added and none removed")
    names_ = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-status", BASE], capture_output=True, text=True).stdout.split("\n")
    changed = sorted(l.split("\t")[1] for l in names_ if l.startswith("M\t"))
    DOCS_ORDERED = ["CLAUDE.md", "README.md", "docs/DATA_NOTES.md", "docs/LAYER.md", "docs/RESULTS.md"]           # the documents the owner ordered brought up to date on 9 October 2026
    RESULTS_SCRIPT = "scripts/write_results.py"            # changed on 9 October 2026 by the owner's choice: one rule, on the record of the check in the Safari application
    hold(set(changed) <= set(touched) | set(DOCS_ORDERED) | {RESULTS_SCRIPT} and set(touched) <= set(changed) and not any(l.startswith(("D\t", "R")) for l in names_),
         "of the files that existed before the decision view, the only ones modified are the four of code and data that were added to, documents the owner ordered brought up to date, and the script that writes one of those documents; none is deleted or renamed")
    rs_changed = RESULTS_SCRIPT in changed
    rs_num = subprocess.run(["git", "-C", str(ROOT), "diff", "--numstat", BASE, "--", RESULTS_SCRIPT], capture_output=True, text=True).stdout.split()
    show("rs_added", V(int(rs_num[0]) if rs_changed else 0, GIT_RS := "git diff --numstat " + BASE + " -- " + RESULTS_SCRIPT, "lines added"), n0)
    show("rs_removed", V(int(rs_num[1]) if rs_changed else 0, GIT_RS, "lines removed"), n0)
    rs_text = W.use(RESULTS_SCRIPT).read_text(encoding="utf-8")
    hold((not rs_changed) or ("with ONE EXCEPTION" in rs_text and "checks_not_run_in_this_pass" in rs_text and "The Chrome and WebKit records must still be of the build on disk: that rule is unchanged." in rs_text),
         "if the results script is changed, the change is the one exception its own docstring states, on the record of the check in the Safari application, and its rule for the Chrome and WebKit records is unchanged")
    hold(all(checks_run[k_]["file_is_as_committed"] is True for k_ in ("verify_layer", "exercise_layer in Chrome", "exercise_layer in WebKit")), "the three unchanged scripts of the regression gate that were run are as committed")
    docs_changed = [d_ for d_ in DOCS_ORDERED if d_ in changed]
    raw_changed = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-status", "HEAD", "--", "00_raw"], capture_output=True, text=True).stdout.split("\n")
    man_head = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:00_raw/data_manifest.csv"], capture_output=True).stdout
    hold(all(l.split("\t")[1] == "00_raw/data_manifest.csv" for l in raw_changed if l.startswith("M\t")) and not any(l.startswith(("D\t", "R")) for l in raw_changed)
         and W.use(MAN).read_bytes().startswith(man_head[:20000]) and (W.use(MAN).read_bytes().startswith(man_head) or not any(l.startswith("M\t") for l in raw_changed)),
         "no file of `00_raw/` that is in the last commit was edited: the manifest, if it differs from that commit, has rows appended to it and every committed byte in place")
    show("docs_changed", V(", ".join(f"`{d_}`" for d_ in docs_changed) or "none yet", "git diff --name-status " + BASE, "the documents among the files modified"), txt)
    GIT = "git diff --numstat " + BASE
    table("T_git", ["file that existed before", "lines added", "lines removed"], [[c(V(f_, GIT, "the file"), lambda x: f"`{x}`"), c(V(num[f_][0], GIT, "lines added"), n0), c(V(num[f_][1], GIT, "lines removed"), n0)] for f_ in touched])
    show("base_commit", V(BASE, "git", "the commit this batch started from"), lambda x: f"`{x}`")
    show("layer_mb", key(L, "outputs/both_bytes"), W.mb)
    show("layer_zip_mb", key(L, "outputs/both_zipped_bytes"), W.mb)
    show("layer_limit_mb", key(L, "outputs/limit_bytes"), W.mb)
    show("ov_bytes", key(L, "decision_view/overlay_file/bytes"), n0)
    KEPT = SCRATCH + "/60_layer_2026-10-07/layer.provenance.json"
    old_inputs = {i_["path"]: i_["sha256"] for i_ in key(KEPT, "inputs").v if isinstance(i_, dict) and "path" in i_ and "sha256" in i_}
    new_inputs = {i_["path"]: i_["sha256"] for i_ in key(L, "inputs").v if isinstance(i_, dict) and "path" in i_ and "sha256" in i_}
    hold(len(old_inputs) > 0 and all(new_inputs.get(k_) == v_ for k_, v_ in old_inputs.items()), "every stage table the layer of 7 October 2026 was built from goes into today's layer with the same sha256")
    show("kept_inputs", V(len(old_inputs), KEPT, "key `inputs`: the files it lists with a sha256"), n0)
    show("kept_build", key(KEPT, "run_utc"), txt)
    calc("new_inputs", len(new_inputs) - len(old_inputs), n0, "inputs of today's layer less inputs of the layer of 7 October", [V(len(new_inputs), L, "key `inputs`: the files it lists with a sha256"), V(len(old_inputs), KEPT, "key `inputs`")])

    DOC.append("""
## 16. How it was verified: which check was applied where

**This build applies the owner's rulings of 9 October 2026, and it was verified lightly, on purpose.** No unit changes
cell, so, as he instructed, no independent replication was made, no adversarial review, and no run in the Safari
application. What follows says which check was applied to what.

**That no unit changed cell.**

- *The gate on the renaming*, `scripts/05_check_rename.py`, run {gate_run}: {gate_n} assignments - every unit, every
  window - taken through the owner's list of names, and every one matches; the {gate_cols} columns the table had are
  equal as text in every row ({gate_cells} cells); the two thresholds, the order of tiers and the default window are
  what they were (§7). It stops on one mismatch.

**The decision table, `55_decision/condition_by_unit.csv`.**

- *Stop conditions in the build.* `scripts/05_build_decision.py` writes its tables into a holding folder, reads them
  back as text, and moves them into place only if every check holds: each unit once; every hectare column as written
  equal to the figure computed; the reconciliation of §3 made on the file itself, for each unit and in total; its
  yearly sums against stage 1's own totals; its repeatability figures against the existing table's; its
  corroboration counts against the agreement record's own; its district-check counts against the district record's
  own; and, added with the rulings, every share and its blank as written, no share above a hundred, and the forest at
  the start of a window less the loss of the window equal to standing forest where the window runs to the last year.
  Its run record lists what passed.
- *The independent replication of 8 October 2026 still covers what it covered, and no more.* Two agents, each given
  the script's docstring and nothing else of it, rebuilt the table as it stood then, for all four windows, by
  different means ({rp_a}; {rp_b}). Each table was hashed before it was compared. Over {rp_cols} of that table's
  {rp_allcols} columns and {rp_cells} cells each, **no cell differs in value**; {rp_form} differ in how a value is
  written. {rp_note} The replicators reported {rp_amb} places where the docstring left them a choice; none changed a
  value. The gate above holds that each of those {rp_allcols} columns is, cell for cell, in today's table of
  {cols_now} columns. **The {gate_new_cols} columns added on 9 October 2026 were not replicated**: the forest at the
  start of each window, the share, the reason for a blank share and the order by share. They are rebuilt by the
  verifier below, once. The record of the replication is a working file of the session, not a stage output (§20).
- *`scripts/verify_decision.py`*, which shares no code with the builders: "{v_decision}". It re-adds every hectare
  from stage 1's yearly columns, re-derives every cell from the printed hectares, every unit's district from
  `10_units/`, the order of every list from those, and every count and share of the layer's About text with its
  statements of the thresholds, the windows and the tier order; it holds the tier order and the six names against the
  owner's specification written out in it, and the rows the cells cite against the registered list. Extended with the
  rulings: it rebuilds the forest at the start of each window and the share for every unit and window from the yearly
  columns, the blanks with their reason and their count, and the order by share in the table and on the page; it
  holds the five new names as he gave them and that none of the old names, and nowhere the words "lower bound", is
  left in the page or its data; and it holds the export's columns, one for one with the expressions that fill them.

**How the checks were run.** By `scripts/run_decision_checks.py`, one after another and never two at once, on the
build described here; it writes down every run it makes, a failed one included (`60_layer/decision_runs.json`). In
this pass it ran {n_checks} checks, and {first_try} passed on their first run. The runs of each browser check are
given with it below.

**The regression gate: the existing views.**

- `scripts/verify_layer.py`, unchanged: "{v_layer}" (with the one remark of §14 on what its sentence about the page's
  own script can and cannot see).
- `scripts/exercise_layer.py`, unchanged, in Chrome ({chrome_is}): {xc_actions} of {xc_actions} actions did what they
  should; {xc_units} units clicked on the map; {xc_values} of {xc_values} displayed values equal the stage tables.
  Runs made of it on this build: {xc_runs}; runs that passed: {xc_pass}.
- `scripts/exercise_layer.py`, unchanged, in WebKit ({webkit_is}): {xw_actions} of {xw_actions} actions; {xw_units}
  units; {xw_values} of {xw_values} values. Runs made of it on this build: {wk_runs}; runs that passed every step:
  {wk_pass}; steps that failed in any run: {wk_failed_steps}.
""" + safari_text + """
- **That nothing existing changed in code or data** was also checked directly. This script compared the record of the
  layer built {kept_build}, kept with the session's working files, with today's: all {kept_inputs} inputs that layer
  was built from go into today's layer with the same hash, beside {new_inputs} new inputs. It asked git what changed
  since the commit before the decision view ({base_commit}): four files of code and data that existed then have lines
  added and none removed.

{T_git}

  *The lines added to `.gitignore` keep fetched files and stage outputs out of git; those added to the manifest are
  the rows of §13 and §14.* The only other files that existed then and are modified are documents the owner ordered
  brought up to date on 9 October 2026: {docs_changed}; and the script that writes one of them. **`scripts/write_results.py`
  was changed, by the owner's choice of 9 October 2026, in one rule** ({rs_added} lines added, {rs_removed} removed since that
  commit): it refused to write `docs/RESULTS.md` unless the record of the check in the Safari application was of the
  layer on disk; it now allows that record to be of an earlier build when the runner's record of this build names the
  check as left out with a reason, and then says so in the text. Its rule for the Chrome and WebKit records is
  unchanged. The unchanged check scripts that were run are as committed (the runner's record says so of each); and no
  file of `10_units/` to `50_gap/` was written.
- **What did change for an existing view**, and the owner accepted (§17): a heading and one line, the decision view's
  switch, stand above the list of layers; and every unit's panel ends with the block "why this tier". The decision
  view's other controls stay folded away, its radio button is a group of its own so that the keyboard moves through
  the existing layers as before, and an existing view's address is what it was.

**The new view.**

- `scripts/exercise_decision.py` in Chrome: {dc_actions} of {dc_actions} steps did what they should ({dc_statements}
  of them are statements of what was not done, readings of the page's script errors or the summary of the clicks on
  the map, the rest actions on the new controls: the view's switch, the four windows, the district, the order within
  a tier, {arrows_pressed} of the {arrows_all} tier arrows and the way back, the filter and its box, a row of the
  list, two exports, the legend, the address, two window sizes, leaving and returning, the overlay). {dc_units} units
  opened by a click on the map, {dc_lgd} LGD panchayat and {dc_out} outside-village units, the latter in
  {dc_out_districts} districts, covering all six cells in {dc_windows_full} windows and all {dc_badges} kinds of
  corroboration badge; {dc_lines} of {dc_lines} comparisons of the block "why this tier" with the tables held
  (nineteen a unit: lines that must be there, the share among them, lines that must not, and the block's place in the
  panel). A click that opens nothing, or a unit that does not touch the one aimed at, fails the run: there was none.
  {dc_neighbour} clicks opened a touching neighbour. The page's script errors were read at the end of every part and
  before every reload: none. Runs made of it on this build: {dcr_runs}; runs that passed: {dcr_pass}.
- The same in WebKit: {dw_actions} of {dw_actions} steps, {dw_units} units, {dw_lines} of {dw_lines} comparisons.
  There events are made inside the page, the exported text is read from the page and not from a saved file, and the
  browser cannot be put offline or have an address blocked. Runs made of it on this build: {dwr_runs}; runs that
  passed: {dwr_pass}.
- The exports, field by field: §15. The overlay, online in both and offline in Chrome: §14.
""" + safari_new + """

**The copy made to be passed on.** `scripts/exercise_share.py`, run {share_run}, opened `70_share/`'s copy from disk
in Chrome: {share_steps} of {share_steps} steps did what they should (§14).

**The fragility of the Safari and WebKit checks: recorded, and by the owner's ruling not chased.** On the layer built
{old_build}, {old_wk_runs} runs of the unchanged WebKit exercise were made and in {old_wk_fail}, the first, one step
failed: a drag of the map made in script, which did not move the map. No cause was established. One candidate, not
tested: the step before the drag is a zoom by the mouse wheel, and the map library ignores a mouse-down while it
still marks a zoom as under way; the unchanged script waits a fixed time. Of the unchanged Safari script on that
day: {xs_earlier}. On the layer built {xs1_build}, {xs1_runs} runs of it were made and {xs1_pass} passed; the note
added by hand to that pass's record: *{xs1_note}* On the layer the owner ruled on, built {ruled_build}, all
{ruled_n} checks were run and {ruled_first} passed on their first run. And what happened to the owner's Safari
windows on 8 October 2026, from the session's note of that day: *{xs_windows}*

**What three adversarial reviews changed, on 8 October 2026.** Reviewers set against the first version found things
that its own checks had passed: a count of "slivers" that were mostly whole pixels; a sentence shown for every
district that was true of the state and false of many districts; evidence on repeatability measured on the wrong
land; a browser check that compared a stale panel twice and called it a neighbour; an overlay that stayed "on" after
its tiles stopped arriving; and a clause of the provider's terms that had been left out. No cell, hectare or tier was
wrong. A second review, of those corrections, found two new sentences that repeated the fault and several new checks
weaker than their names. A third found one more false sentence in the layer - a badge that had dropped the words
"with canopy above ten per cent" - and again checks weaker than their names: the list's check, the gate on tiles
drawn, the verifier's checks of the view's lists and of the page's handlers. Each was corrected. What that history
shows is that sentences in words are where this work has gone wrong, more than figures, and that each round of
checking found the round before it too generous to itself. **No review was made of this build**, by the owner's
instruction: it changes labels, adds two figures beside the cell and an order within a tier, and moves no unit. The
conclusions this text draws from figures are tested when it is written and listed in §20.4; a sentence that is not
such a conclusion is tested by nothing, and a reader should hold the prose to the tables.

**What was not done.** No run was made in the Safari application on this build, and no control was ever clicked
there. The layer has not been opened in Firefox (not installed on this machine), on a phone, in print, or on a
machine with little memory. The district's list, the filter's list and the list of the order within a tier were set
through their change events in both engines, because a native pop-up cannot be clicked in a window that is not on a
screen. Two behaviours of the overlay were read in the page's code and not exercised in a browser: that nothing is
drawn if its file arrives after the box has been unticked or the view left, and that the warning of a failed tile
stays until the overlay is drawn again. {arrows_pressed} of the {arrows_all} tier arrows were pressed. The digits of
the Gazette's serial numbers were read by eye. The two columns of the share were rebuilt independently once, not
twice. Nobody who knows these places has yet looked at a single tier.
""")

    # ==== 17, 18, 19 =============================================================================================================================
    lo_p = [show(f"gt10_p{i}", bd(col, "gt10le30"), dec(0)) for i, col in enumerate(("loss_km2_2001_2010", "loss_km2_2011_2017", "loss_km2_2018_2025"), 1)]
    hold(lo_p[2].v / lo_p[0].v > 3 * m[2].v / m[0].v, "recorded loss on the open band rises across the three periods several times faster than loss in the forest mask")
    show("dl_open_more", count(CU, f"rows whose `cell_{DEFAULT}` is the cell of closed forest with loss and whose `loss_open_ha_{DEFAULT}` is above their `loss_dense_ha_{DEFAULT}`",
                               lambda t_: (t_[f"cell_{DEFAULT}"] == "dense_loss") & (t_[f"loss_open_ha_{DEFAULT}"] > t_[f"loss_dense_ha_{DEFAULT}"])), n0)
    show("dl_n18", nc(DEFAULT, "dense_loss"), n0)
    DOC.append("""
## 17. The owner's rulings of 9 October 2026, and what is still open

On 9 October 2026 the owner read the list of decisions this section then held and ruled on it. It is split in two as
he asked.

### 17.1 Ruled on 9 October 2026

**Accepted as proposed.**

- **The standing minimum, {smin} ha** (§5.2). The alternatives would move {mv_s_lo} and {mv_s_hi} units.
- **The loss minimum, {lmin} ha, as the rule of the cells** (§5.1). The alternatives would move {mv_l_lo} and
  {mv_l_hi} units.
- **The default window, 2018–2025, with its three caveats** (§4).
- **The narrower wording of the reason for ranking only within a district**, which is the one the layer uses (§9):
  it holds for LGD panchayat units at the headline, not for all units, at every floor, with the East Coast units
  kept, or of any one district.
- **The rounding tolerance** (§3): standing set to zero in {recon_dense_not} units for dense and {recon_open_not} for
  open, where the source's rounding put it a square metre below; and "lost" taken as the sum of the years, which is
  not the source's own total to the last digit in {ysum_dense} units for dense and {ysum_open} for open.
- **The additions to the existing views** (§16): a heading and one line above the list of layers, and a block at the
  end of every unit's panel.
- **Hyphen for dash** in the cells' names (§7).
- **The weaker form of "every lost pixel is bare by construction"** (§2), which is the form the source bears out.
- **The margin of the "close call" flag, a fifth** (§6).
- **The fragility of the Safari and WebKit checks**: to be recorded, and not chased (§16 records it).

**Changed by the rulings, and done in this build.**

- **Five cells renamed, labels only** (§7), because with a flat minimum of {lmin} ha the first names over-claimed:
  {dl_share_1pct} units of the cell then called "under pressure" lost under one per cent of their forest, and
  {intact_cs} units of the cell then called "intact" are flagged by CoRE Stack. No unit changed cell: {gate_n}
  assignments held by the gate.
- **Loss as a share, beside the cell and not in it** (§5.4), with a second order within a tier, by share lost.
  Blank, with the reason in words, where the forest at the start of the window is under the standing minimum:
  {sh_without} units in the default window.
- **"Lower bound" taken out** (§3) of the layer, the tables' record and this document, and replaced by the owner's
  words; the reason is kept in §3 and §18.
- **The export** (§15, §10): the development index of 2011 removed from it and kept in the interactive view; the
  forest at the start of the window and the share added; {ex_ncols} columns.
- **The provider's cautions given a home of their own** (§14): {reg_pages} of the provider's pages registered in
  `00_raw/` with manifest rows, and the cautions quoted in the layer's About text from the dataset record whether or
  not the overlay is shipped.
- **A copy of the layer without the overlay**, `70_share/`, with a README and a zip (§14).
- **The standing rule on `00_raw/`**, reworded in `CLAUDE.md` as he gave it: files in `00_raw/` at a commit are never
  edited; registering a new input adds files and manifest rows. Under it the files this stage put into `00_raw/` on
  8 October 2026, which were rewritten in place before they were committed, were not touched again: this build added
  files and manifest rows there and changed nothing that was committed.
- **The documents** brought up to date as he listed them (§18 says which were). To regenerate `docs/RESULTS.md` with
  no run in the Safari application he chose, the same day, to change one rule of `scripts/write_results.py`: Chrome
  and WebKit on the build on disk are enough, and the text says that Safari was not opened on it (§16).

### 17.2 Still open, for the Foundation for Ecological Security

- **The order of tiers** (§8). Provisional; in particular whether closed forest with loss recorded goes above open
  forest with loss recorded. It is a control in the layer, and an exported list says which order made it.
- **Which rows of the list of permissible works bear on which cell** (§13), and the forest-named rows cited by none,
  above all the last row of the list.
- **Whether Scheduled Tribe share appears in a list they pass on** (§10).

Until these are settled a tier is a starting point for a conversation with the Foundation and not a recommendation.
Two things are open that are not the Foundation's and that the owner knows of: the two points of the tile provider's
terms (§14), which is why the copy made to be passed on has no overlay; and the terms on which that copy may be
passed on, which are not yet agreed and which its README says are not.

## 18. What this does not show

- **It is Hansen's record, read one way.** Standing forest is {standing_is}: it ignores gain, and it inherits
  whatever recorded loss misses or wrongly includes (§3). Loss is the removal of cover; thinning under a canopy is
  invisible to it, and the split into dense and open is that of the year 2000. Tree
  cover is any vegetation taller than five metres: a plantation counts as a natural forest does. The only second
  opinion is the corroboration badge, for the units it covers and for 2017–2023.
- **The provider of the data cautions against part of what is done here.** From Global Forest Watch's record of the
  dataset, registered in `00_raw/` (§14), word for word: "{pc_loss_is}" "{pc_not_deforestation}" "{pc_no_subtraction}"
  "{pc_two_halves}" "{pc_errors}" "{pc_year}" The University of Maryland, whose data it is, defines loss so:
  "{pc_umd_loss}" The decision view's "standing" is exactly the subtraction the record cautions against. It is offered
  as the forest of 2000 with no loss recorded since, and as nothing more: not as tree cover today, and - since the
  owner's ruling of 9 October 2026 - not as a lower bound on it either, because with loss missed at about {pc_fn} per
  cent and loss falsely recorded at about {pc_fp} per cent it can err in either direction. The two halves of the full
  record were made by different methods, which bears on the window 2001–2025; and a loss can be a year off, which
  bears on the edges of every window.
- **Recorded loss on open forest has risen steeply, and these tables cannot say why.** On the open band it goes
  {gt10_p1}, {gt10_p2}, {gt10_p3} km² across 2001–2010, 2011–2017 and 2018–2025, against {gt30_p1}, {gt30_p2},
  {gt30_p3} on the dense band. `docs/RESULTS.md` §3.1 calls the like rise on the lowest band largely the producers'
  change of method. Whether the open band's rise is on the ground or in the method is not established here, and every
  cell with loss counts it.
- **A cell's name says where the forest stands, not where the loss was.** The row is set by standing forest and the
  column by loss from the dense and open bands together (§5). In {ol_dense_more} of the {ol_n} units of
  "{open_loss_name}" more was lost from the dense band than from the open, and in {dl_open_more} of the {dl_n18} units
  of "{dense_loss_name}" more from the open than from the dense. The panel and the export show the two apart.
- **A cell is a summary of hectares in a unit.** It says nothing about where in the unit, why, or by whom. A unit in
  the first tier is a place to look, not a finding about a village. And because the loss minimum is a number of
  hectares, a cell with loss says more about the size of a large unit than about its rate of loss (§5.1).
- **Every limit of the measurements carries over** (`docs/RESULTS.md` §12): the unit is a geometry and not a
  jurisdiction; the canopy bands are fixed at the year 2000; the agreement between the two measures is modest and
  depends on choices; the geotagged record of works ends in FY2017-18; the census is that of 2011.
- **The order of tiers and the mapping to works are still open** (§17). Until the Foundation has set them, a tier is a
  starting point for a conversation and not a recommendation.
- **The other documents.** By the owner's instruction of 9 October 2026 these were brought up to date with the
  decision view, and are modified since the commit before it: {docs_changed}. A document of that instruction that is
  not in this list was not changed and still describes the state before the decision view; §16 says which checks its
  own script asks for. The layer's two files are now {layer_mb} MB together ({layer_zip_mb} MB zipped, against the
  {layer_limit_mb} MB it is held under), and beside them is a third file of {ov_bytes} bytes, the overlay's. One
  sentence of the existing About text, that Hansen "cannot see change on land that was already open in 2000", is
  about change short of clearance; the decision view counts Hansen's clearance on that land.

## 19. To rebuild

```
.venv/bin/python scripts/05_build_decision.py
.venv/bin/python scripts/05_check_rename.py                      # the gate on the renaming: every unit's cell, against the table as ruled on
.venv/bin/python scripts/06_build_layer.py --units 10_units/units.gpkg
.venv/bin/python scripts/run_decision_checks.py                  # both verifiers, then the browser checks, one at a time
.venv/bin/python scripts/07_build_share.py                       # the copy without the overlay, and its zip
.venv/bin/python scripts/exercise_share.py                       # the copy opened from disk in Chrome
.venv/bin/python scripts/write_decision_layer.py
```

The two scripts inside `00_raw/` - the one that checks the list of permissible works and the one that extracts the
provider's cautions - are not in this list: their outputs are registered, and a file in `00_raw/` at a commit is not
written again. `scripts/run_decision_checks.py` runs each check in turn and writes `60_layer/decision_runs.json`,
the record of every run it made, a failed one included; with `--leave-out safari --because "..."` it leaves the two
checks in the Safari application out and writes the reason into the record. This document is written from that
record and stops unless it is of the build in `60_layer/`. The overlay's steps need a connection; the Safari steps
need the terminal's leave to control Safari and no other Safari window showing the layer.

Some things this document reads are working files of the session and are rebuilt by no script: the record of the
independent replication, the decision tables and the layer's records as they stood when the owner ruled on them, the
record of the trials of the list's check, the copies of the provider's pages, the record of the layer built on
7 October 2026, the note of the runs of 8 October 2026 and the record of a pass of the runner with a step made by hand
(§20). It stops if one is missing. The gate on the renaming needs the table as it was ruled on, and stops unless that
copy has the hash written in the gate's script.

Run the browser checks one at a time, on a machine that is otherwise quiet.
""")

    # ==== gates, then the appendix =======================================================================================================
    body = "".join(DOC)
    bad = W.stray_digits(body)
    if bad:
        stop("the text carries digits of its own:\n  " + "\n  ".join(bad[:25]))
    asked = re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", body)
    known = set(W.FIG) | set(W.TABLES)
    if set(asked) - known:
        stop("printed but not defined: " + ", ".join(sorted(set(asked) - known)))
    if known - set(asked):
        stop("defined but not printed: " + ", ".join(sorted(known - set(asked))))
    text = body.format_map({**{k: v["text"] for k, v in W.FIG.items()}, **{k: v["md"] for k, v in W.TABLES.items()}})

    def mark(path):
        return f"`{path}`" + (" *(working file)*" if path.startswith(SCRATCH) else "")

    order, seen_ = [], set()
    for k in asked:
        if k not in seen_:
            seen_.add(k)
            order.append(k)
    app = ["\n## 20. Where every figure comes from\n",
           "This section is the script's own record of what it read. Paths are relative to the repository. The numbered folders "
           "(`10_units/` to `60_layer/`) are stage outputs: each is rebuilt by the script named in the `.provenance.json` beside it, except that the records of the checks in `60_layer/` are written by the checks themselves; none is in git. "
           f"Files under `{SCRATCH}/` are **working files** of the session that made this stage. They are not stage outputs and no tracked script rebuilds them; "
           "the independent replication of the decision table (§16) has no other record.\n",
           "### 20.1 Figures in the text, in the order they first appear\n", "| as printed | file | where in the file |", "|---|---|---|"]
    for k in order:
        if k in W.FIG:
            f = W.FIG[k]
            files = "; ".join(dict.fromkeys(s[0] if s[0] == "this run" else mark(s[0]) for s in f["sources"]))
            where = (f"computed here: {f['formula']}. From: " + "; ".join(s[1] for s in f["sources"])) if f["formula"] else f["sources"][0][1]
            shown = f["text"] if len(f["text"]) <= 160 else f["text"][:157] + "..."
            app.append(f"| {shown.replace('|', '/')} | {files} | {where.replace('|', '/')} |")
    app += ["\n### 20.2 Tables, in the order they appear\n", "Every cell of a table that is not a typed label was read from the file and columns given here.\n", "| table | cells read | file | columns or keys | rows |", "|---|---|---|---|---|"]
    names = {"T_recon": "§3, the reconciliation", "T_windows": "§4, the four windows", "T_small": "§5.1, small losses", "T_recur": "§5.1, recurrence of loss", "T_stand": "§5.2, the standing minimum", "T_sens": "§5.3, sensitivity in the default window",
             "T_sens_w": "§5.3, sensitivity by window", "T_size": "§5.1, the loss column by size of forest", "T_git": "§16, the files that existed before and were added to", "T_uncited": "§13, forest-named rows cited by no cell", "T_boundary": "§6, near the dense and open line", "T_cells": "§7, the six cells", "T_tiers": "§8, the tiers", "T_or": "§9, the odds ratios by floor", "T_districts": "§9, by district",
             "T_corro": "§11, what the badge rests on", "T_cell_corro": "§11, the badge by cell", "T_check": "§12, the district checks", "T_work": "§13, work types"}
    for k in order:
        if k in W.TABLES:
            for i, (file, s) in enumerate(W.TABLES[k]["src"].items()):
                rows_ = "; ".join(s["rows"])
                cols_ = ", ".join(x.replace("column ", "").replace("key ", "") for x in s["cols"])
                app.append(f"| {names.get(k, k) if i == 0 else ''} | {W.TABLES[k]['cells'] if i == 0 else ''} | {mark(file)} | {(cols_ if len(cols_) < 700 else cols_[:700] + ' ...').replace('|', '/')} | {(rows_ if len(rows_) < 700 else rows_[:700] + ' ...').replace('|', '/')} |")
    app += ["\n### 20.3 Files read\n", "| file | bytes | sha256 | the run stamp it carries |", "|---|---|---|---|"]
    for path in sorted(W.FILES):
        f = W.FILES[path]
        app.append(f"| {mark(path)} | {f['bytes']:,} | `{f['sha256'][:16]}` | {f['run_utc'] or '-'} |")
    app += ["\n### 20.4 Statements tested before they were written\n", "Each of these is something the text says in words. The script tested it against the files and would have stopped had it failed.\n"]
    app += [f"- {s}" for s in W.HELD]
    app += ["\n### 20.5 Totals that two places both carry, compared\n"] + [f"- {s}" for s in W.SAME]
    n_fig = len([k for k in order if k in W.FIG])
    app += ["\n### 20.6 Digits the text was allowed to carry\n", "The text itself may hold no digit except inside a code span (a file, a column, a threshold written as code, a command) and in: "
            + "; ".join(dict.fromkeys(why for _, why in W.ALLOWED)) + ". Everything else that is a number came from a file.\n",
            f"*{n_fig} figures and {len(W.TABLES)} tables ({sum(t['cells'] for t in W.TABLES.values())} cells) from {len(W.FILES)} files; {len(W.HELD)} statements tested; {len(W.SAME)} totals compared. "
            f"Written {written} by `scripts/write_decision_layer.py` (sha256 `{W.sha256(__file__)[:16]}`), with the reading functions of `scripts/write_results.py` (sha256 `{W.sha256(W.__file__)[:16]}`).*\n"]
    out = Path(a.draft) if a.draft else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n".join(app), encoding="utf-8")
    print(f"{out}: {len(text.splitlines()) + len(app):,} lines; {n_fig} figures, {len(W.TABLES)} tables ({sum(t['cells'] for t in W.TABLES.values())} cells), {len(W.FILES)} files read; "
          f"{len(W.HELD)} statements tested, {len(W.SAME)} totals compared; verifiers {'NOT run (draft)' if a.draft else 'run'}")


if __name__ == "__main__":
    main()
