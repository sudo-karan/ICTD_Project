#!/usr/bin/env python3
"""
Verify the R6.20 district panel against the report's own printed TOTAL rows.

R6.20 is "Comprehensive Report on Plantation Maintenance, Progress and Green Infrastructure
Management" on the MGNREGA MIS (MISreport4.aspx -> R6.20). Its 4th tab, "NRM / Water / All
Plantation Works", prints one district table per (financial year, work category) with a Total row
at top and bottom. We scraped 13 FY x 3 categories x 30 districts = 1170 rows and kept the printed
totals separately; this script reconciles them.

    python scripts/verify_r620.py

Exits non-zero and prints every mismatch. There is no tolerance on the integer columns. Money is
compared at 0.02 lakh (each district is printed to 2 dp, so 30 roundings can accumulate ~0.15,
but in practice the portal's own Total is computed from unrounded values - see WHAT FAILS below).

WHAT THE REPORT WILL NOT RECONCILE, and why that is the portal's arithmetic and not ours:
  pct_works  The "%age of works on X against total works" column is NOT category_works/all_works
             for the row. It has no denominator in the table, and the printed Total is not the sum
             nor the mean of the district values. Treated as opaque; never used downstream.
  exp_all    Identical across the 3 categories within one (fy, district) - this IS checked, since
             it is the same denominator printed three times, and a mismatch would mean the scrape
             crossed years or categories.

THE CATEGORIES ARE NESTED, NOT A PARTITION. Measured over all 390 district-year cells, Water
expenditure <= NRM expenditure in 390/390 and Plantation expenditure <= NRM expenditure in 390/390.
NRM is the parent category; Water and Plantation are subsets of it. So the three shares MUST NOT be
added, and "NRM 67.59%" already contains "Water 43.06%". Water and Plantation are very nearly
disjoint within NRM - Water + Plantation <= NRM in 382 of 390 cells - but not exactly; 8 cells, all
in the 2014-15..2017-18 tables frozen in 2020, exceed it by up to 105.91 lakh (Ganjam 2015-16,
0.6% of that district's total). Those 8 are listed, not failed.
"""
import csv, sys
from collections import defaultdict
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "00_raw" / "mis_reports"
DIST = RAW / "odisha_r620_district_fy_category_2014-2027.csv"
TOT = RAW / "odisha_r620_state_totals_2014-2027.csv"

N_FY, N_CAT, N_DIST = 13, 3, 30
BLOCKS_ODISHA = 314          # the portal's own count; Odisha has 314 CD blocks
MONEY_TOL = 0.02             # lakh
INT_COLS = ["blocks", "works_ongoing", "works_completed"]
MONEY_COLS = ["exp_cat_lakh", "exp_all_lakh"]

fails = []


def fail(msg):
    fails.append(msg)


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def num(row, col):
    return float(row[col])


def main():
    d = read(DIST)
    t = read(TOT)
    print(f"{DIST.name}: {len(d)} rows")
    print(f"{TOT.name}: {len(t)} rows")

    if len(d) != N_FY * N_CAT * N_DIST:
        fail(f"expected {N_FY*N_CAT*N_DIST} district rows, got {len(d)}")
    if len(t) != N_FY * N_CAT:
        fail(f"expected {N_FY*N_CAT} total rows, got {len(t)}")

    # 1. shape: every (fy, category) cell has exactly 30 distinct districts
    cells = defaultdict(list)
    for r in d:
        cells[(r["fy"], r["category"])].append(r)
    for k, rows in sorted(cells.items()):
        if len(rows) != N_DIST:
            fail(f"{k}: {len(rows)} district rows, expected {N_DIST}")
        names = [r["district"] for r in rows]
        if len(set(names)) != len(names):
            dupes = sorted({n for n in names if names.count(n) > 1})
            fail(f"{k}: duplicate districts {dupes}")

    # district name set must be the same in every cell
    sets = {k: frozenset(r["district"] for r in rows) for k, rows in cells.items()}
    ref_k, ref = next(iter(sorted(sets.items())))
    for k, s in sorted(sets.items()):
        if s != ref:
            fail(f"{k}: district set differs from {ref_k}: "
                 f"extra {sorted(s-ref)}, missing {sorted(ref-s)}")

    # 2. exp_all_lakh is one denominator printed three times - must agree across categories
    for fy in sorted({r["fy"] for r in d}):
        for dist in sorted(ref):
            vals = {r["category"]: r["exp_all_lakh"]
                    for r in d if r["fy"] == fy and r["district"] == dist}
            if len(set(vals.values())) > 1:
                fail(f"{fy} {dist}: exp_all_lakh differs across categories {vals}")

    # 3. district rows must sum to the printed Total row
    tot = {(r["fy"], r["category"]): r for r in t}
    for k, rows in sorted(cells.items()):
        if k not in tot:
            fail(f"{k}: no printed Total row to check against")
            continue
        T = tot[k]
        for col in INT_COLS:
            s = sum(int(num(r, col)) for r in rows)
            want = int(num(T, col))
            if col == "blocks":
                # blocks is a per-district constant, so the Total is the state block count
                if s != want:
                    fail(f"{k}: blocks sum {s} != printed {want}")
                if want != BLOCKS_ODISHA:
                    fail(f"{k}: printed blocks {want} != Odisha's {BLOCKS_ODISHA}")
            elif s != want:
                fail(f"{k}: {col} sum {s} != printed {want} (diff {s-want:+d})")
        for col in MONEY_COLS:
            s = round(sum(num(r, col) for r in rows), 2)
            want = num(T, col)
            if abs(s - want) > MONEY_TOL:
                fail(f"{k}: {col} sum {s:,.2f} != printed {want:,.2f} "
                     f"(diff {s-want:+,.2f} lakh)")

    # 4. pct_exp must be exp_cat/exp_all, to the printed precision
    for r in d:
        all_ = num(r, "exp_all_lakh")
        if all_ == 0:
            continue
        calc = num(r, "exp_cat_lakh") / all_ * 100
        if abs(calc - num(r, "pct_exp")) > 0.015:
            fail(f"{r['fy']} {r['category']} {r['district']}: pct_exp printed "
                 f"{r['pct_exp']}, computed {calc:.4f}")

    # 5. nesting: Water and Plantation are subsets of NRM, and each is a subset of all works
    cell = defaultdict(dict)
    for r in d:
        cell[(r["fy"], r["district"])][r["category"]] = r
    overlap = []
    for k, c in sorted(cell.items()):
        if set(c) != {"NRM", "Water", "Plantation"}:
            fail(f"{k}: categories {sorted(c)}, expected NRM/Water/Plantation")
            continue
        nrm, wat, pla = c["NRM"], c["Water"], c["Plantation"]
        parent = num(nrm, "exp_cat_lakh")
        for name, r in (("Water", wat), ("Plantation", pla)):
            if num(r, "exp_cat_lakh") > parent + MONEY_TOL:
                fail(f"{k}: {name} exp {num(r,'exp_cat_lakh'):,.2f} > NRM exp {parent:,.2f} - "
                     f"breaks the nesting the whole panel rests on")
        for name, r in (("NRM", nrm), ("Water", wat), ("Plantation", pla)):
            if num(r, "exp_cat_lakh") > num(r, "exp_all_lakh") + MONEY_TOL:
                fail(f"{k}: {name} exp {num(r,'exp_cat_lakh'):,.2f} > all works "
                     f"{num(r,'exp_all_lakh'):,.2f}")
        # Water and Plantation are near-disjoint inside NRM; record where they are not
        exc = num(wat, "exp_cat_lakh") + num(pla, "exp_cat_lakh") - parent
        if exc > MONEY_TOL:
            overlap.append((k, exc, num(nrm, "exp_all_lakh")))

    # ---- report -------------------------------------------------------------
    if fails:
        print(f"\nFAILED - {len(fails)} check(s):", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)

    print(f"\nOK  {len(d)} district rows reconcile to all {len(t)} printed Total rows")
    print(f"    Water <= NRM and Plantation <= NRM in all {len(cell)} district-year cells: the three")
    print(f"    categories are NESTED, not a partition. Never add them.")
    if overlap:
        print(f"\n    Water + Plantation exceeds NRM in {len(overlap)} of {len(cell)} cells "
              f"(they are near-disjoint inside NRM, not exactly):")
        for k, exc, allw in sorted(overlap, key=lambda x: -x[1]):
            print(f"      {k[0]} {k[1]:<16} by {exc:>8,.2f} lakh "
                  f"({exc/allw*100:.2f}% of the district's total)")
    print(f"    {N_FY} financial years x {N_CAT} categories x {N_DIST} districts, "
          f"{BLOCKS_ODISHA} blocks each")

    # provenance the paper will need: these years are frozen snapshots, not live figures
    print("\nlast_updated as printed by the portal:")
    byd = defaultdict(list)
    for r in t:
        byd[r["last_updated"]].append(r["fy"])
    for when, fys in sorted(byd.items(), key=lambda kv: kv[0][-4:] + kv[0][3:5] + kv[0][:2]):
        print(f"    {when}  {', '.join(sorted(set(fys)))}")
    print("    -> the 2014-15..2017-18 tables have not been rewritten since 10/10/2020.")

    # the headline series
    print("\nPlantation share of all MGNREGA expenditure, Odisha (R6.20, all 314 blocks):")
    for r in sorted(t, key=lambda r: r["fy"]):
        if r["category"] != "Plantation":
            continue
        nrm = next(x for x in t if x["fy"] == r["fy"] and x["category"] == "NRM")
        wat = next(x for x in t if x["fy"] == r["fy"] and x["category"] == "Water")
        works = int(num(r, "works_ongoing")) + int(num(r, "works_completed"))
        per = num(r, "exp_cat_lakh") * 1e5 / works if works else float("nan")
        print(f"    {r['fy']}  plantation {float(r['pct_exp']):6.2f}%   "
              f"NRM {float(nrm['pct_exp']):6.2f}%   water {float(wat['pct_exp']):6.2f}%   "
              f"{works:>7,} plantation works   Rs {per:>9,.0f}/work")
    print("\n    Rs/work is expenditure / (ongoing + completed) and is NOT a unit cost: a work can")
    print("    appear in several years. The ~20x fall after 2017-18 is the number the paper has to")
    print("    explain before it can claim plantation activity itself collapsed.")


if __name__ == "__main__":
    main()
