#!/usr/bin/env python3
"""Deliberate errors planted in copies of the stage-4 tables, to show that `scripts/verify_gap.py` catches each one.

    ~/.venvs/ictd-stage4/bin/python scripts/verify_gap_trials.py [name-fragment ...]

For every trial: the tables of `50_gap/` are copied to a temporary folder outside the repository, ONE error is planted in
the copy, and the verifier is run on the copy (`--tables DIR`). The originals are never touched. First the verifier is
run, whole, on an untouched copy (the control): it must pass, or the trials mean nothing.

A trial is CAUGHT when the verifier exits with status 1 and at least one of its checks that fail is a check of content:
one whose words do not name a SHA-256. A builder with the fault would have recorded the table it wrote, so the copy's
provenance record is given the bytes and the SHA-256 of each damaged table before the verifier runs; a stale digest
then catches nothing, and the catch has to come from a figure. (Not so in the trials that run the part `inputs`: that
part holds the record against the repository's own files, which a copy never changes, so there the record is left as
it is.) Where the error is planted in the provenance record itself (a version, a digest), the check that holds that
field is the check of content, whatever its words name, and any failed check counts.

The errors are of the kinds a builder gets wrong, not single flipped digits where a rule can be broken instead: a
district code swapped between two districts, the part year let into a sum, the lag of the panel shifted by a year, a
share taken over the wrong denominator, the East Coast exclusion not applied, a model reported under another's name,
an interval replaced by the one a different method gives, and so on. Every table of `50_gap/` has at least one, and so
have the two text files of the models, the provenance record and the record of the check of the forest villages PDF.

To keep the run to tens of minutes, a trial runs the parts of the verifier that read the table it damaged (`--only`),
which the record names; the control runs every part. With name fragments given, only the trials whose name contains one
are run and the record is not written (for trying one trial).

Writes `50_gap/verify_gap_trials.json` and nothing else: the control, and for each trial its name, its kind, the tables
it damaged, the parts run, whether it was caught, the checks that failed (their first words) and the seconds it took.
"""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAP = ROOT / "50_gap"
PY = sys.executable
VERIFIER = ROOT / "scripts" / "verify_gap.py"


def load(d, name):
    with open(d / name, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def save(d, name, cols, rows):
    with open(d / name, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def D(x):
    return Decimal(str(x))


def q(x, places):
    return format(Decimal(x).quantize(Decimal(places), rounding=ROUND_HALF_UP), "f")


def one(rows, **where):
    found = [r for r in rows if all(r[k] == v for k, v in where.items())]
    assert len(found) == 1, (where, len(found))
    return found[0]


# ---- the errors --------------------------------------------------------------------------------------------------------------------
def crosswalk_swapped(d):
    cols, rows = load(d, "district_crosswalk.csv")
    a, b = one(rows, r620_district="ANGUL"), one(rows, r620_district="BOLANGIR")
    for k in ("pc11_district_code", "district_name"):
        a[k], b[k] = b[k], a[k]
    save(d, "district_crosswalk.csv", cols, rows)


def unit_moved(d):
    cols, rows = load(d, "unit_district.csv")
    u, other = rows[0], next(r for r in rows if r["pc11_district_code"] != rows[0]["pc11_district_code"])
    u["pc11_district_code"], u["district_name"] = other["pc11_district_code"], other["district_name"]
    save(d, "unit_district.csv", cols, rows)


def gate_value_changed(d):
    cols, rows = load(d, "inputs_check.csv")
    r = next(r for r in rows if r["found"] == "151843.18")
    r["found"] = "151843.19"
    save(d, "inputs_check.csv", cols, rows)


def need_on_wrong_district(d):
    cols, rows = load(d, "district_need.csv")
    a, b = one(rows, district_name="Kandhamal"), one(rows, district_name="Rayagada")
    for k in ("pc11_district_code", "district_name", "r620_district"):
        a[k], b[k] = b[k], a[k]
    save(d, "district_need.csv", cols, rows)


def need_without_the_cell_filter(d):
    cols, rows = load(d, "district_need.csv")
    for r in rows:
        r["n1_ha_2018_2025"] = r["forest_loss_ha_2018_2025_all_units"]
        r["loss_below_minimum_ha_2018_2025"] = "0.0000"
    save(d, "district_need.csv", cols, rows)


def part_year_in_the_post_sum(d):
    cols, rows = load(d, "district_allocation.csv")
    for r in rows:
        r["r620_plantation_post_lakh"] = format(D(r["r620_plantation_post_lakh"]) + D(r["r620_plantation_part_year_lakh"]), "f")
    save(d, "district_allocation.csv", cols, rows)


def no_start_year_counted_as_started(d):
    cols, rows = load(d, "district_allocation.csv")
    for r in rows:
        for stem in ("dump_forest_named", "dump_plantation_category"):
            r[f"{stem}_started_by_fy2017_18_inr"] = format(D(r[f"{stem}_started_by_fy2017_18_inr"]) + D(r[f"{stem}_start_year_missing_inr"]), "f")
            r[f"{stem}_start_year_missing_inr"] = "0"
    save(d, "district_allocation.csv", cols, rows)


def need_share_over_all_loss(d):
    _, need = load(d, "district_need.csv")
    total = sum(D(r["forest_loss_ha_2018_2025_all_units"]) for r in need)
    cols, rows = load(d, "need_vs_allocation.csv")
    for r in rows:
        if r["comparison"] == "C1":
            share = 100 * D(r["need"]) / total
            r["need_share_pct"] = q(share, "0.000001")
            if r["r"] != "":
                r["r"] = q(D(r["allocation_share_pct"]) / share, "0.000001")
    save(d, "need_vs_allocation.csv", cols, rows)


def east_coast_not_left_out(d):
    cols, rows = load(d, "need_vs_allocation.csv")
    c1 = {r["pc11_district_code"]: r for r in rows if r["comparison"] == "C1"}
    for r in rows:
        if r["comparison"] == "C7":
            for k in cols:
                if k != "comparison":
                    r[k] = c1[r["pc11_district_code"]][k]
    save(d, "need_vs_allocation.csv", cols, rows)
    cols, rows = load(d, "need_vs_allocation_summary.csv")
    a, b = one(rows, comparison="C7"), one(rows, comparison="C1")
    for k in cols:
        if k not in ("comparison", "kind", "need_is", "allocation_is", "what_it_asks", "seed_permutation", "seed_bootstrap"):
            a[k] = b[k]
    save(d, "need_vs_allocation_summary.csv", cols, rows)


def pearson_reported_as_spearman(d):
    import numpy as np
    _, long = load(d, "need_vs_allocation.csv")
    x = np.array([float(r["need"]) for r in long if r["comparison"] == "C1"])
    y = np.array([float(r["allocation"]) for r in long if r["comparison"] == "C1"])
    cols, rows = load(d, "need_vs_allocation_summary.csv")
    one(rows, comparison="C1")["rho"] = repr(round(float(np.corrcoef(x, y)[0, 1]), 6))
    save(d, "need_vs_allocation_summary.csv", cols, rows)


def gaps_added_without_their_sign(d):
    _, long = load(d, "need_vs_allocation.csv")
    total = sum(abs(D(r["gap_lakh"])) for r in long if r["comparison"] == "C1" and r["gap_lakh"] != "")
    cols, rows = load(d, "need_vs_allocation_summary.csv")
    one(rows, comparison="C1")["sum_positive_gaps_lakh"] = q(total, "0.01")
    save(d, "need_vs_allocation_summary.csv", cols, rows)


def district_in_the_wrong_class(d):
    _, long = load(d, "need_vs_allocation.csv")
    _, need = load(d, "district_need.csv")
    cols, rows = load(d, "marginalisation_split.csv")
    block = [r for r in rows if r["comparison"] == "C1" and r["grouping"] == "st_class"]
    src = next(r for r in block if int(r["n_districts"]) >= 2)
    dst = next(r for r in block if r is not src)
    name = src["districts"].split("; ")[0]
    code = one(need, district_name=name)["pc11_district_code"]
    m = one(long, comparison="C1", pc11_district_code=code)
    for r, sign in ((src, -1), (dst, 1)):
        r["n_districts"] = str(int(r["n_districts"]) + sign)
        r["need"] = format(D(r["need"]) + sign * D(m["need"]), "f")
        r["allocation_lakh"] = format(D(r["allocation_lakh"]) + sign * D(m["allocation"]), "f")
        r["need_share_pct"] = q(D(r["need_share_pct"]) + sign * D(m["need_share_pct"]), "0.000001")
        r["allocation_share_pct"] = q(D(r["allocation_share_pct"]) + sign * D(m["allocation_share_pct"]), "0.000001")
    src["districts"] = "; ".join(src["districts"].split("; ")[1:])
    dst["districts"] = dst["districts"] + "; " + name
    save(d, "marginalisation_split.csv", cols, rows)


def scale_from_the_rounded_share(d):
    _, alloc = load(d, "district_allocation.csv")
    pre, all_pre, all_post = (sum(D(r[k]) for r in alloc) for k in ("r620_plantation_pre_lakh", "r620_all_pre_lakh", "r620_all_post_lakh"))
    share = (100 * pre / all_pre).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) / 100
    cols, rows = load(d, "what_more.csv")
    one(rows, district="state")["scale_of_the_fall_lakh"] = q(share * all_post, "0.01")
    save(d, "what_more.csv", cols, rows)


def lag_shifted(d):
    cols, rows = load(d, "district_year_panel.csv")
    for r in rows:
        if r["loss_ha_year_t"] != "":
            r["loss_ha_year_t_minus_1"], r["loss_dense_ha_year_t_minus_1"] = r["loss_ha_year_t"], r["loss_dense_ha_year_t"]
    save(d, "district_year_panel.csv", cols, rows)


def part_year_in_the_models(d):
    cols, rows = load(d, "district_year_panel.csv")
    for r in rows:
        if r["part_year"] == "1":
            r["in_models"], r["period"] = "1", "post"
    save(d, "district_year_panel.csv", cols, rows)


def plain_district_effects_as_the_headline(d):
    cols, rows = load(d, "panel_models.csv")
    a, b = one(rows, id="P1"), one(rows, id="P2")
    for k in ("coefficient", "se_cr1", "t_cr1", "n_parameters"):
        a[k] = b[k]
    save(d, "panel_models.csv", cols, rows)


def panel_interval_from_the_normal(d):
    cols, rows = load(d, "panel_models.csv")
    a = one(rows, id="P1")
    b, se = float(a["coefficient"]), float(a["se_cr1"])
    a["wcb_ci95_lo"], a["wcb_ci95_hi"] = repr(round(b - 1.96 * se, 8)), repr(round(b + 1.96 * se, 8))
    save(d, "panel_models.csv", cols, rows)


def prior_loss_over_the_wrong_forest(d):
    cols, rows = load(d, "unit_history.csv")
    for r in rows:
        if r["prior_loss_share_pct"] != "" and D(r["forest_at_window_start_ha"]) > 0:
            r["prior_loss_share_pct"] = q(100 * D(r["loss_2001_2017_ha"]) / D(r["forest_at_window_start_ha"]), "0.000001")
    save(d, "unit_history.csv", cols, rows)


def exposure_dropped_for_some_units(d):
    cols, rows = load(d, "unit_history.csv")
    n = 0
    for r in rows:
        if r["e1_any_forest_named"] == "1" and r["in_h1"] == "1" and n < 20:
            r["e1_any_forest_named"] = "0"
            n += 1
    save(d, "unit_history.csv", cols, rows)


def another_exposure_under_the_headlines_name(d):
    cols, rows = load(d, "unit_history_models.csv")
    a, b = one(rows, id="H1"), one(rows, id="H7")
    for k in ("coefficient", "se_cr1", "t_cr1", "n_exposed"):
        a[k] = b[k]
    save(d, "unit_history_models.csv", cols, rows)


def h4_with_every_district(d):
    cols, rows = load(d, "unit_history_models.csv")
    a, b = one(rows, id="H4"), one(rows, id="H1")
    for k in cols:
        if k not in ("id", "headline", "sample", "wcb_seed", "wcb_B"):
            a[k] = b[k]
    save(d, "unit_history_models.csv", cols, rows)


def extent_on_wrong_district(d):
    cols, rows = load(d, "fra_by_district.csv")
    a, b = one(rows, district_name="Mayurbhanj"), one(rows, district_name="Kendujhar")
    for k in ("community_titles_distributed", "community_extent_ha"):
        a[k], b[k] = b[k], a[k]
    save(d, "fra_by_district.csv", cols, rows)


def raw_correlation_under_the_per_hectare_name(d):
    cols, rows = load(d, "fra_summary.csv")
    a, b = one(rows, id="R2"), one(rows, id="R1")
    for k in ("rho", "p_permutation", "ci95_lo", "ci95_hi"):
        a[k] = b[k]
    save(d, "fra_summary.csv", cols, rows)


def national_extent_in_acres(d):
    _, mota = load(ROOT / "00_raw" / "cfr_fra", "mota_fra_state_wise_2025-12-31.csv")
    acres = one(mota, state="Odisha")["extent_acres_community"]
    cols, rows = load(d, "fra_two_reports.csv")
    rows[1]["community_extent_ha"] = acres
    rows[2]["community_extent_ha"] = format(D(rows[0]["community_extent_ha"]) - D(acres), "f")
    save(d, "fra_two_reports.csv", cols, rows)


def deck_pre_and_post_swapped(d):
    cols, rows = load(d / "deck_tables", "districts_by_need.csv")
    for r in rows:
        r["plantation_post_share_pct"], r["plantation_pre_share_pct"] = r["plantation_pre_share_pct"], r["plantation_post_share_pct"]
    save(d / "deck_tables", "districts_by_need.csv", cols, rows)


def deck_share_rounded_down(d):
    cols, rows = load(d / "deck_tables", "marginalisation_split_c1.csv")
    _, split = load(d, "marginalisation_split.csv")
    done = False
    for r in rows:
        src = one(split, comparison="C1", grouping=r["grouping"], **{"class": r["class"]})
        down = format(D(src["need_share_pct"]).quantize(Decimal("0.1"), rounding="ROUND_DOWN"), "f")
        if down != r["need_share_pct"] and not done:
            r["need_share_pct"], done = down, True
    assert done, "no share of the deck table changes when rounded down"
    save(d / "deck_tables", "marginalisation_split_c1.csv", cols, rows)


def deck_interval_from_the_normal(d):
    _, pm = load(d, "panel_models.csv")
    p1 = one(pm, id="P1")
    b, se = float(p1["coefficient"]), float(p1["se_cr1"])
    cols, rows = load(d / "deck_tables", "headline_rows.csv")
    a = one(rows, id="P1")
    a["interval_lo"], a["interval_hi"] = q(b - 1.96 * se, "0.0001"), q(b + 1.96 * se, "0.0001")
    save(d / "deck_tables", "headline_rows.csv", cols, rows)


def text_interval_from_the_normal(d):
    _, pm = load(d, "panel_models.csv")
    p1 = one(pm, id="P1")
    b, se = float(p1["coefficient"]), float(p1["se_cr1"])
    path = d / "panel_models.txt"
    lines = path.read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("P1  ")) + 2
    old = lines[i]
    start, end = old.index("95% interval ") + len("95% interval "), old.index(", p = ")
    lines[i] = old[:start] + f"{b - 1.96 * se:.6f} to {b + 1.96 * se:.6f}" + old[end:]
    assert lines[i] != old
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def text_counts_of_another_model(d):
    _, um = load(d, "unit_history_models.csv")
    h1, h4 = one(um, id="H1"), one(um, id="H4")
    path = d / "unit_history_models.txt"
    text = path.read_text(encoding="utf-8")
    was = f"n = {h4['n_units']} units, {h4['n_exposed']} exposed, {h4['n_districts']} districts (clusters)"
    assert text.count(was) == 1, text.count(was)
    path.write_text(text.replace(was, f"n = {h1['n_units']} units, {h1['n_exposed']} exposed, {h1['n_districts']} districts (clusters)"), encoding="utf-8")


def fv_rows_made_to_fit(d):
    name = "forest_villages_districts_as_the_layer_reads_them.csv"
    cols, rows = load(d, name)
    r = next(r for r in rows if r["rows_equal_the_page_s_zero_area_count"] == "no")
    r["rows_with_a_village_code"], r["rows_equal_the_page_s_zero_area_count"] = r["page_zero_area_villages"], "yes"
    save(d, name, cols, rows)


def fv_summary_row_made_to_add_up(d):
    cols, rows = load(d, "forest_villages_text_layer_check.csv")
    r = one(rows, adds_up="no")
    r["total_inhabited_villages"], r["adds_up"] = str(int(r["revenue_villages"]) + int(r["zero_area_villages"])), "yes"
    save(d, "forest_villages_text_layer_check.csv", cols, rows)


def fv_check_a_said_to_hold(d):
    path = d / "forest_villages_pdf_record.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["check_a"]["holds"] is False
    rec["check_a"]["holds"], rec["which_check_failed"] = True, None
    path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def fsi_rows_on_wrong_districts(d):
    cols, rows = load(d, "fsi_district_check.csv")
    a, b = one(rows, district_name="Kandhamal"), one(rows, district_name="Kalahandi")
    for k in cols:
        if k.startswith("fsi_") or k == "match_rule":            # the Forest Survey's whole row, as a wrong match of names would put it
            a[k], b[k] = b[k], a[k]
    save(d, "fsi_district_check.csv", cols, rows)


def fsi_scrub_over_the_area(d):
    cols, rows = load(d, "fsi_district_check.csv")
    for r in rows:
        r["fsi_scrub_pct_of_forest_cover"] = q(100 * D(r["fsi_scrub_km2"]) / D(r["fsi_calculated_area_km2"]), "0.000001")
    save(d, "fsi_district_check.csv", cols, rows)


def fsi_change_with_its_sign_lost(d):
    cols, rows = load(d, "fsi_district_check.csv")
    for r in rows:
        r["fsi_change_wrt_2021_km2"] = format(abs(D(r["fsi_change_wrt_2021_km2"])), "f")
        r["fsi_change_pct_of_forest_cover"] = format(abs(D(r["fsi_change_pct_of_forest_cover"])), "f")
    save(d, "fsi_district_check.csv", cols, rows)


def fsi_raw_under_the_size_free_name(d):
    cols, rows = load(d, "fsi_summary.csv")
    a, c = one(rows, id="a"), one(rows, id="c")
    for k in ("rho", "p_permutation", "ci95_lo", "ci95_hi"):
        c[k] = a[k]
    save(d, "fsi_summary.csv", cols, rows)


def fv_check_a_said_to_hold_everywhere(d):
    """As `fv_check_a_said_to_hold`, and carried into the copy of the record that the provenance record keeps: the two agree, and only the rule can tell."""
    fv_check_a_said_to_hold(d)
    rec = json.loads((d / "forest_villages_pdf_record.json").read_text(encoding="utf-8"))
    path = d / "gap.provenance.json"
    prov = json.loads(path.read_text(encoding="utf-8"))
    kept = prov["steps"]["08_build_gap_rights"]["forest_villages"]
    assert kept["check_a"]["holds"] is False and kept["which_check_failed"] == "(a)"
    kept["check_a"]["holds"], kept["which_check_failed"] = rec["check_a"]["holds"], rec["which_check_failed"]
    path.write_text(json.dumps(prov, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main_list_sorted_as_whole_lines(d):
    """The fault a reviewer found in the build of 10 October: the list written in another order than `pip freeze` prints."""
    path = d / "environment_main_now.txt"
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert sorted(lines) != lines, "sorting the list as whole lines changes nothing"
    path.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


def main_list_with_a_stage4_package(d):
    path = d / "environment_main_now.txt"
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert not any(l.lower().startswith("numba==") for l in lines)
    at = next(i for i, l in enumerate(lines) if l.lower() > "numba==")
    path.write_text("\n".join(lines[:at] + ["numba==0.62.1"] + lines[at:]) + "\n", encoding="utf-8")


def script_hash_of_another_step(d):
    path = d / "gap.provenance.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    a, b = rec["steps"]["08_gap_inputs"], rec["steps"]["08_build_gap_panel"]
    assert a["script_sha256"] != b["script_sha256"]
    a["script_sha256"] = b["script_sha256"]                       # 64 hexadecimal digits, and not this step's script
    path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def deck_interval_called_by_other_weights(d):
    for name in ("headline_rows.csv", "headline_rows.md"):
        path = d / "deck_tables" / name
        text = path.read_text(encoding="utf-8")
        assert text.count("Webb weights") == 2, (name, text.count("Webb weights"))
        path.write_text(text.replace("Webb weights", "Rademacher weights"), encoding="utf-8")


def step_run_with_another_numpy(d):
    path = d / "gap.provenance.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    env = rec["steps"]["08_build_gap_units"]["environment"]
    main = rec["steps"]["08_gap_environment"]["main_environment"]["numpy"]
    assert env["packages"]["numpy"] != main
    env["packages"]["numpy"] = main                               # as if the unit models had been built in the main environment
    path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


TRIALS = [  # name, kind, tables damaged, parts of the verifier run, the function
    ("the census codes of two districts swapped in the crosswalk", "a swapped district code", ["district_crosswalk.csv"], ["inputs"], crosswalk_swapped),
    ("one unit put in a neighbouring district", "a unit in the wrong district", ["unit_district.csv"], ["inputs"], unit_moved),
    ("the found value of a gate altered by a hundredth", "a figure altered", ["inputs_check.csv"], ["inputs"], gate_value_changed),
    ("the need of two districts exchanged (their codes swapped in the table of need)", "a swapped district code", ["district_need.csv"], ["districts"], need_on_wrong_district),
    ("N1 taken over every unit, the loss under the minimum included", "a need without its cell filter", ["district_need.csv"], ["districts"], need_without_the_cell_filter),
    ("FY2026-27 added into post-period plantation money", "a part-year leak into a sum", ["district_allocation.csv"], ["districts"], part_year_in_the_post_sum),
    ("works with no start year counted as started by FY2017-18", "a missing start year counted as early", ["district_allocation.csv"], ["districts"], no_start_year_counted_as_started),
    ("C1's need shares taken over all forest loss, not over N1", "a wrong denominator", ["need_vs_allocation.csv"], ["comparisons"], need_share_over_all_loss),
    ("C7 computed with every district kept", "a dropped East Coast exclusion", ["need_vs_allocation.csv", "need_vs_allocation_summary.csv"], ["comparisons"], east_coast_not_left_out),
    ("Pearson's correlation written where C1's rho belongs", "another statistic under the same name", ["need_vs_allocation_summary.csv"], ["comparisons"], pearson_reported_as_spearman),
    ("the gaps of C1 added without their sign", "a sum of the wrong terms", ["need_vs_allocation_summary.csv"], ["comparisons"], gaps_added_without_their_sign),
    ("one district counted in another Scheduled Tribe class", "a district in the wrong class", ["marginalisation_split.csv"], ["comparisons"], district_in_the_wrong_class),
    ("the size of the fall worked out from the share rounded to two decimals", "a rounded ratio used where the exact one belongs", ["what_more.csv"], ["comparisons"], scale_from_the_rounded_share),
    ("the panel's loss of the year before replaced by the loss of the same year", "a shifted lag", ["district_year_panel.csv"], ["panel"], lag_shifted),
    ("the part year flagged as a model year of the post period", "a part-year leak into a sum", ["district_year_panel.csv"], ["panel"], part_year_in_the_models),
    ("P2's estimate reported as P1", "a model under another's name", ["panel_models.csv"], ["panel"], plain_district_effects_as_the_headline),
    ("P1's interval replaced by the estimate plus and minus 1.96 CR1 standard errors", "an interval from another method", ["panel_models.csv"], ["panel"], panel_interval_from_the_normal),
    ("the prior loss share taken over forest at the start of the window, not the forest of 2000", "a wrong denominator", ["unit_history.csv"], ["units"], prior_loss_over_the_wrong_forest),
    ("the exposure set to zero for twenty exposed units of the headline sample", "an exposure miscoded", ["unit_history.csv"], ["units"], exposure_dropped_for_some_units),
    ("H7's estimate and count of exposed units reported as H1", "a model under another's name", ["unit_history_models.csv"], ["units"], another_exposure_under_the_headlines_name),
    ("H4 fitted with the East Coast districts kept (H1's figures under H4's name)", "a dropped East Coast exclusion", ["unit_history_models.csv"], ["units"], h4_with_every_district),
    ("the community titles and extent of two districts exchanged", "a swapped district code", ["fra_by_district.csv"], ["rights"], extent_on_wrong_district),
    ("R1's figures reported as R2", "another statistic under the same name", ["fra_summary.csv"], ["rights"], raw_correlation_under_the_per_hectare_name),
    ("the national report's community extent given in acres", "a wrong unit", ["fra_two_reports.csv"], ["rights"], national_extent_in_acres),
    ("the deck table's pre-period and post-period shares exchanged", "columns exchanged", ["deck_tables/districts_by_need.csv"], ["deck"], deck_pre_and_post_swapped),
    ("a share of the deck's split rounded down instead of half up", "a rounding rule broken", ["deck_tables/marginalisation_split_c1.csv"], ["deck"], deck_share_rounded_down),
    ("the deck's interval for P1 replaced by the estimate plus and minus 1.96 CR1 standard errors", "an interval from another method", ["deck_tables/headline_rows.csv"], ["deck"], deck_interval_from_the_normal),
    ("P1's interval in the text file of the panel models replaced by the estimate plus and minus 1.96 CR1 standard errors", "an interval from another method", ["panel_models.txt"], ["texts"], text_interval_from_the_normal),
    ("H4's counts of units, exposed units and districts in the text file of the unit models replaced by H1's", "a model under another's name", ["unit_history_models.txt"], ["texts"], text_counts_of_another_model),
    ("the provenance record says the unit models were built with the main environment's numpy", "a step run in the wrong environment", ["gap.provenance.json"], ["environment"], step_run_with_another_numpy),
    ("a district's rows read from the forest villages PDF set to the count its page prints, as if the layer had every row", "a count altered to pass a check",
     ["forest_villages_districts_as_the_layer_reads_them.csv"], ["rights"], fv_rows_made_to_fit),
    ("the row of the PDF's summary page that does not add up given the total that would make it", "a figure altered", ["forest_villages_text_layer_check.csv"], ["rights"], fv_summary_row_made_to_add_up),
    ("the record of the forest villages PDF says the owner's check (a) holds", "a check reported as passed", ["forest_villages_pdf_record.json"], ["rights"], fv_check_a_said_to_hold),
    ("the record of the forest villages PDF and its copy in the provenance record both say the owner's check (a) holds", "a check reported as passed",
     ["forest_villages_pdf_record.json", "gap.provenance.json"], ["rights"], fv_check_a_said_to_hold_everywhere),
    ("the Forest Survey's rows of two districts exchanged, as a wrong match of names would put them", "a swapped district code", ["fsi_district_check.csv"], ["fsi"], fsi_rows_on_wrong_districts),
    ("the Forest Survey's scrub taken as a per cent of the district's area, not of its forest cover", "a wrong denominator", ["fsi_district_check.csv"], ["fsi"], fsi_scrub_over_the_area),
    ("the Forest Survey's change in forest cover with its sign lost", "a sign lost", ["fsi_district_check.csv"], ["fsi"], fsi_change_with_its_sign_lost),
    ("the correlation of N1 with the Forest Survey's change reported where the size-free one belongs", "another statistic under the same name", ["fsi_summary.csv"], ["fsi"], fsi_raw_under_the_size_free_name),
    ("the main environment's list of packages written sorted as whole lines, not in the order pip freeze prints", "an order not kept", ["environment_main_now.txt"], ["environment"], main_list_sorted_as_whole_lines),
    ("numba written into the main environment's list of packages", "a package stage 4 added, in the main environment", ["environment_main_now.txt"], ["environment"], main_list_with_a_stage4_package),
    ("the first step recorded with the SHA-256 of another step's script", "a step recorded as built by other code", ["gap.provenance.json"], ["environment"], script_hash_of_another_step),
    ("the deck's intervals for P1 and H1 said to be made with Rademacher weights", "a method misnamed", ["deck_tables/headline_rows.csv", "deck_tables/headline_rows.md"], ["deck"],
     deck_interval_called_by_other_weights),
]
RECORD = "gap.provenance.json"


def copy_tables(to):
    shutil.copytree(GAP, to, ignore=shutil.ignore_patterns("verify_gap_trials.json", "before_*"))


def carry_into_record(d, tables):
    """Give the copy's provenance record the bytes and the SHA-256 of each damaged table, wherever a step records it as an output or an input."""
    path = d / RECORD
    rec = json.loads(path.read_text(encoding="utf-8"))
    carried = 0
    for t in tables:
        if t == RECORD:
            continue
        data = (d / t).read_bytes()
        now = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        for sec in rec["steps"].values():
            for name, e in sec.get("outputs", {}).items():
                if name == "50_gap/" + t:
                    e.update(now)
                    carried += 1
            for e in sec.get("inputs", {}).values():
                if e.get("path") == "50_gap/" + t:
                    e.update(now)
                    carried += 1
    path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return carried


def run(tables, only=None):
    cmd = [PY, str(VERIFIER), "--tables", str(tables)] + (["--only", ",".join(only)] if only else [])
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    lines = [l for l in r.stdout.splitlines() if l.startswith(("PASS", "FAIL"))]
    last = (r.stdout.strip().splitlines() or [""])[-1]
    return r.returncode, [l for l in lines if l.startswith("FAIL")], len(lines), last, round(time.time() - t0, 1)


def main():
    wanted = [a.lower() for a in sys.argv[1:]]
    todo = [t for t in TRIALS if not wanted or any(w in t[0].lower() for w in wanted)]
    work = Path(tempfile.mkdtemp(prefix="ictd_gap_trials_"))
    record = {"script": "scripts/verify_gap_trials.py", "verifier": "scripts/verify_gap.py", "verifier_sha256": hashlib.sha256(VERIFIER.read_bytes()).hexdigest(),
              "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "how": "each error is planted in a copy of 50_gap/ outside the repository, and the copy's provenance record is given the bytes and SHA-256 of the damaged table "
                     "(except where the part `inputs` is run, which holds the record against the repository's files); the verifier is run on the copy with --tables; "
                     "caught = exit status 1 and at least one failed check whose words name no SHA-256 (any failed check, where the error is planted in the provenance record itself)"}
    try:
        if not wanted:
            copy_tables(work / "control")
            code, failed, n, last, secs = run(work / "control")
            record["control"] = {"what": "the verifier, every part, on an untouched copy", "passed": code == 0 and not failed and n > 0, "checks": n, "last_line": last, "seconds": secs}
            print(("control passed: " if record["control"]["passed"] else "CONTROL FAILED: ") + last, flush=True)
            if not record["control"]["passed"]:
                sys.exit("the verifier does not pass on the untouched tables: no trial was made")
        out = []
        for k, (name, kind, tables, parts, fn) in enumerate(todo):
            d = work / f"trial_{k:02d}"
            copy_tables(d)
            fn(d)
            changed = [t for t in tables if (d / t).read_bytes() != (GAP / t).read_bytes()]
            assert changed == tables, f"{name}: the tables changed are {changed}, not {tables}"
            carried = carry_into_record(d, tables) if "inputs" not in parts else 0
            code, failed, n, last, secs = run(d, parts)
            on_content = [f for f in failed if "SHA-256" not in f and "sha256" not in f]
            caught = code == 1 and len(failed if RECORD in tables else on_content) > 0
            out.append({"name": name, "kind": kind, "tables": tables, "parts_run": parts, "caught": caught, "checks_run": n, "checks_failed": len(failed),
                        "checks_failed_that_name_no_digest": len(on_content), "entries_of_the_record_given_the_damaged_table_s_digest": carried,
                        "failed_checks": [f[6:186] for f in (on_content or failed)[:4]], "seconds": secs})
            print(("caught      " if caught else "NOT CAUGHT  ") + f"{name} | {len(failed)} of {n} checks failed, {len(on_content)} of them naming no digest | {secs} s", flush=True)
            shutil.rmtree(d)
        record["trials"] = out
        print(f"{sum(t['caught'] for t in out)} of {len(out)} errors caught; tables damaged: {len({x for t in out for x in t['tables']})}")
        if not wanted:
            (GAP / "verify_gap_trials.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
            print("wrote 50_gap/verify_gap_trials.json")
        sys.exit(0 if all(t["caught"] for t in out) else 1)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
