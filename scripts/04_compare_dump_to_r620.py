#!/usr/bin/env python3
"""
Stage 3, the time dimension: the asset dump set beside R6.20, district by financial year.

    python scripts/04_build_allocation.py --units 10_units/units.gpkg     (first; it writes the dump tables)
    python scripts/04_compare_dump_to_r620.py

THE TWO INSTRUMENTS ARE ON DIFFERENT BASES and this script does not pretend otherwise. The dump is indexed
by the year a work STARTED and puts the work's whole lifetime expenditure in that year. R6.20 is indexed
by the year the money was SPENT. `dump_capture` is the dump's total over R6.20's all-works total; where it
is far below 1 the dump's shares for that year are computed on a sliver of the real denominator and mean
nothing (README section 2). `comparable` marks FY2014-15 to FY2016-17, the only years where both can see,
and the dump's share columns are left blank in every other year. `comparable` is set by year: within those
years a single district's capture still runs well below and above 1, so read dump_capture row by row.
A 0 in a dump column means no work in the dump started in that district-year. From FY2018-19 on that says
more about the dump's coverage than about the district.

NESTED, NOT A PARTITION (README 5.6). R6.20's Water and Plantation are subsets of its NRM, and this script
never adds the three as shares of all expenditure. Inside NRM it takes two shares, for R6.20 only: water /
NRM, and (water + plantation) / NRM. The second is there to show how much of NRM is neither - land
development, drought proofing, flood control - and that the remainder moves from a tenth to a half of NRM
across the panel, which is why NRM cannot be rebuilt from the other two (docs/NRM.md). The dump has no NRM
at all (see 04_build_allocation.py), and its `water` is a construct from CoRE Stack's work categories, not
R6.20's Water. They are put side by side here so that the difference can be seen.

AGREEMENT IS REPORTED TWICE. Districts differ several-fold in size, and two unrelated quantities that both
grow with a district's spending will rank districts alike. So each Spearman correlation is given raw and
again with the district's all-works expenditure (R6.20) partialled out of the ranks. The p-values are not
adjusted for the number of pairs tested.

In : 40_allocation/assets_district_fy.csv, 40_allocation/assets_file_qa.csv   from 04_build_allocation.py (rupees)
     00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv        1,170 rows (lakh rupees)
     00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv                the 39 printed Total rows
     00_raw/mis_reports/odisha_road_plantation_rpt_2016_2017.csv              physical units, no expenditure
Out: 40_allocation/
     district_fy_r620_vs_dump.csv           30 districts x 13 FY = 390 rows, money in lakh
     state_fy_r620_vs_dump.csv              13 rows, R6.20 side taken from its printed totals
     district_instrument_agreement.csv      rank agreement across the 30 districts, by year and pair
     r620_vs_dump.provenance.json           inputs (bytes, sha256), UTC run time, checks, n and missingness

Needs pandas, numpy, scipy.
"""
import datetime, hashlib, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
MIS = ROOT / "00_raw" / "mis_reports"
OUT = ROOT / "40_allocation"
R620 = MIS / "odisha_r620_district_fy_category_2014-2027.csv"
R620_TOTALS = MIS / "odisha_r620_state_totals_2014-2027.csv"
ROAD = MIS / "odisha_road_plantation_rpt_2016_2017.csv"
DUMP = OUT / "assets_district_fy.csv"
DUMP_FILES = OUT / "assets_file_qa.csv"

N_FY, N_DIST = 13, 30
MONEY_TOL = 0.02                    # lakh; the tolerance verify_r620.py uses against the printed totals
COMPARABLE = ("2014-15", "2015-16", "2016-17")
PART_YEAR = "2026-27"
ROAD_YEAR = "2016-17"
# dump total / R6.20 all-works total, per cent, as measured in README section 2. A different answer here
# means the district or year join has gone wrong, not that the README needs changing.
README_CAPTURE = {"2014-15": 82.6, "2015-16": 93.4, "2016-17": 83.4, "2017-18": 36.2, "2018-19": 3.2, "2019-20": 2.3}
ROAD_KM = "Length of Road planted in Km - Total"
ROAD_PLANTS = "Number of Plants planted - Total"
DUMP_MONEY = ["total", "plantation_category", "forestry_worktype", "forest_named_worktype", "water"]
SCALE = "r620_exp_all_lakh"         # what "district size" means when it is partialled out

fails = []


def fail(msg):
    fails.append(msg)


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Nothing was written.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def short_fy(fy):
    """R6.20 writes 2014-2015; the dump tables write 2014-15."""
    a, b = fy.split("-")
    return f"{a}-{b[-2:]}"


def pct(num, den):
    return np.where(den > 0, 100 * num / np.where(den > 0, den, 1), np.nan)


def show(v, width, places=2):
    """A share for the console; a dash where there is nothing to show rather than a nan."""
    return f"{'-':>{width}}" if pd.isna(v) else f"{v:>{width}.{places}f}"


def blank_cells(t):
    return {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}


def rank_agreement(x, y, z):
    """Spearman rho of x and y, raw, and with z partialled out of both sets of ranks; two-sided p-values."""
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    raw = stats.spearmanr(x, y)
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    r = float(np.corrcoef(ex, ey)[0, 1])
    dof = len(rx) - 3
    p = float(2 * stats.t.sf(abs(r) * np.sqrt(dof / (1 - r * r)), dof))
    return float(raw.statistic), float(raw.pvalue), r, p


def load_r620():
    d = pd.read_csv(R620)
    t = pd.read_csv(R620_TOTALS)
    for frame in (d, t):
        frame["fy"] = frame["fy"].map(short_fy)
    if len(d) != N_FY * 3 * N_DIST or set(d["category"]) != {"NRM", "Water", "Plantation"}:
        fail(f"{R620.name}: expected {N_FY * 3 * N_DIST} rows in NRM/Water/Plantation, got {len(d)} in {sorted(set(d['category']))}")
    sums = d.groupby(["fy", "category"])[["works_ongoing", "works_completed", "exp_cat_lakh", "exp_all_lakh"]].sum()
    for (fy, cat), want in t.set_index(["fy", "category"]).iterrows():
        got = sums.loc[(fy, cat)]
        for c in ("works_ongoing", "works_completed"):
            if int(got[c]) != int(want[c]):
                fail(f"R6.20 {fy} {cat}: {c} sums to {int(got[c])}, printed Total {int(want[c])}")
        for c in ("exp_cat_lakh", "exp_all_lakh"):
            if abs(got[c] - want[c]) > MONEY_TOL:
                fail(f"R6.20 {fy} {cat}: {c} sums to {got[c]:,.2f}, printed Total {want[c]:,.2f}")
    stop_if_failed("checking R6.20 against its printed totals")

    d["works"] = d["works_ongoing"] + d["works_completed"]
    wide = d.pivot(index=["district", "fy"], columns="category", values=["exp_cat_lakh", "works", "exp_all_lakh"])
    if (wide["exp_all_lakh"].nunique(axis=1) != 1).any():
        fail("R6.20: exp_all_lakh is one denominator printed three times, but it differs across categories in some cell")
    out = pd.DataFrame({
        "r620_exp_all_lakh": wide[("exp_all_lakh", "NRM")],
        "r620_exp_nrm_lakh": wide[("exp_cat_lakh", "NRM")], "r620_exp_water_lakh": wide[("exp_cat_lakh", "Water")],
        "r620_exp_plantation_lakh": wide[("exp_cat_lakh", "Plantation")],
        "r620_works_nrm": wide[("works", "NRM")], "r620_works_water": wide[("works", "Water")],
        "r620_works_plantation": wide[("works", "Plantation")]}).reset_index()
    for c in ("water", "plantation"):                 # the nesting everything downstream relies on
        if (out[f"r620_exp_{c}_lakh"] > out["r620_exp_nrm_lakh"] + MONEY_TOL).any():
            fail(f"R6.20: {c} expenditure exceeds NRM expenditure in some district-year - the categories are no longer nested")
    stamp = t.groupby("fy")["last_updated"].agg(lambda s: "; ".join(sorted(set(s))))
    out["r620_last_updated"] = out["fy"].map(stamp)
    return out, t


def load_dump():
    for p in (DUMP, DUMP_FILES):
        if not p.exists():
            sys.exit(f"{p.relative_to(ROOT)} is missing - run scripts/04_build_allocation.py first")
    d = pd.read_csv(DUMP, dtype={"fy_work_start": str, "pc11_district_code": str}, keep_default_na=False, na_values=[""])
    files = pd.read_csv(DUMP_FILES, dtype={"pc11_district_code": str})
    if len(files) != N_DIST or int(d["n_works"].sum()) != int(files["n_works"].sum()):
        fail(f"{DUMP.name} holds {int(d['n_works'].sum()):,} works but {DUMP_FILES.name} holds {int(files['n_works'].sum()):,} in {len(files)} files")
    out = d[["district_file", "district_property", "pc11_district_code", "fy_work_start", "n_works"]].rename(
        columns={"fy_work_start": "fy", "district_property": "district", "n_works": "dump_n_works"})
    out["dump_n_works_plantation_category"] = d["n_works_plantation_category"]
    for k in DUMP_MONEY:
        out[f"dump_exp_{k}_lakh"] = d[f"expenditure_{k}"].fillna(0) / 1e5        # the dump is in rupees
    return out, files


def main():
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r620, printed = load_r620()
    dump, files = load_dump()
    stop_if_failed("reading the inputs")

    names_r, names_d = set(r620["district"]), set(files["district_property"])
    if names_r != names_d:
        fail(f"district names differ between R6.20 and the dump's District field: only in R6.20 {sorted(names_r - names_d)}, "
             f"only in the dump {sorted(names_d - names_r)}")
    stop_if_failed("matching districts")
    ids = files.rename(columns={"district_property": "district"})[["district", "district_file", "pc11_district_code"]]

    # ---- district x FY: every R6.20 cell, with the dump's works that STARTED in that year --------------------
    dump_cols = [c for c in dump.columns if c.startswith("dump_")]
    cell = r620.merge(ids, on="district", validate="many_to_one").merge(
        dump[["district", "fy"] + dump_cols], on=["district", "fy"], how="left", validate="one_to_one")
    n_no_dump = int(cell["dump_n_works"].isna().sum())
    cell[dump_cols] = cell[dump_cols].fillna(0)                        # no row = no work in the dump started that year
    cell["dump_n_works"] = cell["dump_n_works"].astype(int)
    cell["dump_n_works_plantation_category"] = cell["dump_n_works_plantation_category"].astype(int)
    cell["dump_capture"] = pct(cell["dump_exp_total_lakh"], cell["r620_exp_all_lakh"]) / 100
    cell["comparable"] = cell["fy"].isin(COMPARABLE).astype(int)
    cell["part_year"] = (cell["fy"] == PART_YEAR).astype(int)
    if len(cell) != N_FY * N_DIST:
        fail(f"expected {N_FY * N_DIST} district-year rows, built {len(cell)}")
    front = ["district", "district_file", "pc11_district_code", "fy", "comparable", "part_year", "r620_last_updated"]
    cell = cell[front + [c for c in cell.columns if c not in front]].sort_values(["district", "fy"]).reset_index(drop=True)
    money = [c for c in cell.columns if c.endswith("_lakh")]

    # ---- state x FY: R6.20 from its own printed Total rows, the dump summed over districts ---------------------
    p = printed.pivot(index="fy", columns="category", values=["exp_cat_lakh", "exp_all_lakh", "works_ongoing", "works_completed"])
    state = pd.DataFrame({
        "r620_exp_all_lakh": p[("exp_all_lakh", "NRM")], "r620_exp_nrm_lakh": p[("exp_cat_lakh", "NRM")],
        "r620_exp_water_lakh": p[("exp_cat_lakh", "Water")], "r620_exp_plantation_lakh": p[("exp_cat_lakh", "Plantation")],
        "r620_works_plantation": p[("works_ongoing", "Plantation")] + p[("works_completed", "Plantation")]})
    state = state.join(cell.groupby("fy")[[c for c in cell.columns if c.startswith("dump_") and c != "dump_capture"]].sum())
    state["dump_capture_pct"] = pct(state["dump_exp_total_lakh"], state["r620_exp_all_lakh"])
    state["r620_nrm_share_pct"] = pct(state["r620_exp_nrm_lakh"], state["r620_exp_all_lakh"])
    state["r620_water_share_pct"] = pct(state["r620_exp_water_lakh"], state["r620_exp_all_lakh"])
    state["r620_plantation_share_pct"] = pct(state["r620_exp_plantation_lakh"], state["r620_exp_all_lakh"])
    state["r620_water_share_of_nrm_pct"] = pct(state["r620_exp_water_lakh"], state["r620_exp_nrm_lakh"])
    # the one place the two are added: to size what else NRM holds, and how far that moves (docs/NRM.md)
    state["r620_water_plus_plantation_share_of_nrm_pct"] = pct(state["r620_exp_water_lakh"] + state["r620_exp_plantation_lakh"],
                                                               state["r620_exp_nrm_lakh"])
    usable = state.index.isin(COMPARABLE)
    for k in DUMP_MONEY[1:]:                          # a dump share outside the comparable years is not a number to keep
        state[f"dump_{k}_share_pct"] = np.where(usable, pct(state[f"dump_exp_{k}_lakh"], state["dump_exp_total_lakh"]), np.nan)
    state = state.reset_index()
    state.insert(1, "comparable", state["fy"].isin(COMPARABLE).astype(int))
    state.insert(2, "part_year", (state["fy"] == PART_YEAR).astype(int))
    state.insert(3, "r620_last_updated", state["fy"].map(printed.groupby("fy")["last_updated"].agg(lambda s: "; ".join(sorted(set(s))))))
    for fy, want in README_CAPTURE.items():
        got = float(state.loc[state["fy"] == fy, "dump_capture_pct"].iloc[0])
        if abs(got - want) > 0.05:
            fail(f"dump capture of R6.20 in {fy} is {got:.2f}%, README section 2 measured {want}%")
    for c in ("exp_all", "exp_nrm", "exp_water", "exp_plantation"):        # districts must add up to the printed totals
        gap = (cell.groupby("fy")[f"r620_{c}_lakh"].sum() - state.set_index("fy")[f"r620_{c}_lakh"]).abs().max()
        if gap > MONEY_TOL:
            fail(f"R6.20 {c}: district rows differ from the printed state total by {gap:.2f} lakh in some year")

    # ---- do the instruments rank the 30 districts alike? ----------------------------------------------------------
    road = pd.read_csv(ROAD)
    total, road = road[road["is_total_row"] == 1], road[road["is_total_row"] == 0]
    for c in (ROAD_KM, ROAD_PLANTS):          # the Total row is printed above and below the data (README 5.3); check each
        if not len(total) or ((total[c] - road[c].sum()).abs() > 0.005).any():
            fail(f"{ROAD.name}: {c!r} sums to {road[c].sum():,.3f}, printed Total {total[c].tolist()}")
    if set(road["fin_year"]) != {"2016-2017"} or set(road["District"]) != names_r:
        fail(f"{ROAD.name}: expected the 30 R6.20 districts for 2016-2017, got {sorted(set(road['fin_year']))} and "
             f"{sorted(set(road['District']) ^ names_r)} unmatched")
    stop_if_failed("building the comparison")
    road = road.rename(columns={"District": "district", ROAD_KM: "road_km_planted", ROAD_PLANTS: "road_plants_planted"})
    pairs = [("r620_exp_plantation_lakh", "dump_exp_plantation_category_lakh"),
             ("r620_exp_plantation_lakh", "dump_exp_forestry_worktype_lakh"),
             ("r620_exp_water_lakh", "dump_exp_water_lakh")]
    road_pairs = [(a, b) for a in ("road_km_planted", "road_plants_planted")
                  for b in ("r620_exp_plantation_lakh", "dump_exp_plantation_category_lakh", "dump_exp_forestry_worktype_lakh")]
    rows = []
    for fy in COMPARABLE:
        y = cell[cell["fy"] == fy].merge(road[["district", "road_km_planted", "road_plants_planted"]], on="district", validate="one_to_one")
        for a, b in pairs + (road_pairs if fy == ROAD_YEAR else []):
            rho, p_raw, partial, p_partial = rank_agreement(y[a], y[b], y[SCALE])
            rows.append({"fy": fy, "a": a, "b": b, "n_districts": len(y), "spearman_rho": round(rho, 3), "p_value": float(f"{p_raw:.3g}"),
                         "rho_given_district_scale": round(partial, 3), "p_value_given_district_scale": float(f"{p_partial:.3g}")})
    agreement = pd.DataFrame(rows)

    OUT.mkdir(exist_ok=True)
    # rounded for the files only; the console below prints from the unrounded figures
    cell.round({**{c: 2 for c in money}, "dump_capture": 4}).to_csv(OUT / "district_fy_r620_vs_dump.csv", index=False)
    state.round({c: (2 if c.endswith("_lakh") else 3) for c in state.columns if c.endswith(("_lakh", "_pct"))}) \
        .to_csv(OUT / "state_fy_r620_vs_dump.csv", index=False)
    agreement.to_csv(OUT / "district_instrument_agreement.csv", index=False)
    inputs = [R620, R620_TOTALS, ROAD, DUMP, DUMP_FILES]
    with open(OUT / "r620_vs_dump.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": str(Path(__file__).resolve().relative_to(ROOT)), "script_sha256": sha256(__file__), "run_utc": started,
            "inputs": [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in inputs],
            "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
            "basis": {"r620": "year the money was spent; lakh rupees; three nested categories, never added as shares of all expenditure. "
                              "(water + plantation) / NRM is taken once, to size what else NRM holds",
                      "dump": "year the work started, whole lifetime expenditure; converted from rupees to lakh; no NRM; water is a construct",
                      "comparable": f"FY in {list(COMPARABLE)} only, set by year; dump share columns are blank in every other year",
                      "part_year": PART_YEAR,
                      "district_scale": f"{SCALE} of the same year, partialled out of the ranks; p-values unadjusted for {len(agreement)} tests"},
            "checks_passed": {"r620_rows_reconcile_to_printed_totals": int(len(printed)), "districts_matched_on_MIS_name": N_DIST,
                              "readme_capture_reproduced_pct": README_CAPTURE, "road_report_reconciles_to_its_total_rows": int(len(total))},
            "tables": {"district_fy_r620_vs_dump.csv": {"rows": int(len(cell)), "districts": N_DIST, "financial_years": N_FY,
                                                       "district_years_with_no_dump_work": n_no_dump, "blank_cells": blank_cells(cell)},
                       "state_fy_r620_vs_dump.csv": {"rows": int(len(state)), "blank_cells": blank_cells(state)},
                       "district_instrument_agreement.csv": {"rows": int(len(agreement)), "n_districts_in_every_row": N_DIST,
                                                            "blank_cells": blank_cells(agreement)}}}, fh, indent=2)

    print(f"district_fy_r620_vs_dump.csv: n = {len(cell)} district-years ({N_DIST} districts x {N_FY} FY); "
          f"{n_no_dump} have no work in the dump starting that year (written as 0); blank cells {blank_cells(cell) or 'none'}")
    comparable_capture = cell.loc[cell["comparable"] == 1, "dump_capture"]
    print(f"  district capture within the comparable years (n = {len(comparable_capture)}): min {comparable_capture.min():.2f}, "
          f"median {comparable_capture.median():.2f}, max {comparable_capture.max():.2f}")
    print(f"\nstate_fy_r620_vs_dump.csv: n = {len(state)} financial years; dump shares blank outside the {len(COMPARABLE)} comparable years "
          f"({int(state['dump_water_share_pct'].isna().sum())} of {len(state)} rows). Shares are per cent of ALL expenditure in that instrument.")
    print("  R6.20 = year spent, from its printed totals.  dump = year started.  NRM contains water and plantation: never add them.")
    print(f"  {'FY':<8}{'capture':>8} |{'R6.20':>7}{'dump':>7}{'dump':>7}{'dump':>7} |{'R6.20':>7}{'dump':>7} |{'R6.20':>7}{'R6.20':>8}{'R6.20':>10}  R6.20 as of")
    print(f"  {'':<8}{'%':>8} |{'plant.':>7}{'pl.cat':>7}{'fwt':>7}{'named':>7} |{'water':>7}{'water*':>7} |{'NRM':>7}{'wat/NRM':>8}{'(w+p)/NRM':>10}")
    for _, r in state.iterrows():
        note = "  <- part-year" if r["part_year"] else ("" if r["comparable"] else "  (dump shares not usable)")
        print(f"  {r['fy']:<8}{show(r['dump_capture_pct'], 8, 1)} |{show(r['r620_plantation_share_pct'], 7)}{show(r['dump_plantation_category_share_pct'], 7)}"
              f"{show(r['dump_forestry_worktype_share_pct'], 7)}{show(r['dump_forest_named_worktype_share_pct'], 7)} |"
              f"{show(r['r620_water_share_pct'], 7)}{show(r['dump_water_share_pct'], 7)} |{show(r['r620_nrm_share_pct'], 7)}{show(r['r620_water_share_of_nrm_pct'], 8)}"
              f"{show(r['r620_water_plus_plantation_share_of_nrm_pct'], 10, 1)}"
              f"  {r['r620_last_updated']}{note}")
    print("  * a construct from CoRE Stack work categories, not R6.20's Water. The dump has no NRM.")
    wp = state["r620_water_plus_plantation_share_of_nrm_pct"]
    print(f"  (w+p)/NRM runs from {wp.min():.1f}% to {wp.max():.1f}%, a swing of {wp.max() - wp.min():.1f} points: NRM cannot be rebuilt from water and plantation")
    print(f"\ndistrict_instrument_agreement.csv: n = {len(agreement)} pairs, {N_DIST} districts in each; blank cells {blank_cells(agreement) or 'none'}")
    print(f"  Spearman rho, raw and with district scale ({SCALE}) partialled out; p-values unadjusted")
    for _, r in agreement.iterrows():
        print(f"  {r['fy']}  {r['a']:<26} ~ {r['b']:<34} rho {r['spearman_rho']:>6.3f} (p {r['p_value']:<8.2g})   "
              f"given scale {r['rho_given_district_scale']:>6.3f} (p {r['p_value_given_district_scale']:<8.2g})")
    print(f"\ndone. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
