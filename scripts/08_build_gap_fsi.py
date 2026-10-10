"""Stage 4, Phase 5b: the need read against the Forest Survey of India's own district figures. Writes into `50_gap/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_build_gap_fsi.py

Added on 11 October 2026 by the project owner's instruction. Most of N1 lies in five southern districts. This step
sets, beside each district's N1, what the Forest Survey reports for the same district, and computes four rank
correlations. It names no reason for anything: the two sources measure different things, and nothing here says why
either figure is what it is.

WHAT THE TWO SOURCES MEASURE
  Hansen (N1)        gross, stand-replacing loss of tree cover, year by year, on land with canopy above 10 per cent in
                     2000; here summed over 2018 to 2025 in the units where loss is recorded (`50_gap/district_need.csv`).
  The Forest Survey  India State of Forest Report 2023, Volume II, Table 10.20.3, "District-wise Forest Cover in
                     Odisha": for each district the forest cover of its 2023 assessment in three density classes and
                     in total, the change in that total with respect to its 2021 assessment, and the area of scrub.
                     All in square kilometres. The change is a net figure between two assessments.
They are not the same quantity, and neither can be subtracted from the other.

THE INPUT is the registered text of the report's pages, `00_raw/05_forest_reference/isfr2023_vol2_odisha_pdf_pages_260-265.txt`
(manifest row `isfr2023_vol2_odisha_extract`). It is read and not changed.

HOW THE TABLE IS READ. The table runs over two pages, each under a line that holds "Table 10.20.3". From such a line
on, every line that is a name followed by exactly eight numbers is a row, until the row named "Grand Total", which
ends the table. A number may carry commas in the Indian grouping (`1,55,707`) and a minus sign. The eight numbers, in
the table's order: calculated area (by the Survey of India), very dense forest, moderately dense forest, open forest,
total forest cover, total as a per cent of the calculated area, change with respect to 2021 (the table's footnote:
"*Area figure calculated without normalization factor."), scrub.

DISTRICT NAMES. A row's name is matched to the census district of the same name in `50_gap/district_need.csv`. Five
names of the table are spelt otherwise than the census name and take the owner's rule of 11 October 2026, and no
other name may need one: Angul 384, Baleswar 377, Deogarh 373, Jagatsinghpur 380, Nabarangpur 397. The match must be
one to one over the 30 districts.

fsi_district_check.csv - one row per district (30), in the order of the census code
  pc11_district_code, district_name            the census code and name, as `district_need.csv` gives them
  fsi_district_name                            the name as the table prints it
  match_rule                                   `census name` or `spelling rule`
  n1_ha_2018_2025                              N1 of the window 2018-2025, hectares (`district_need.csv`)
  n1_km2_2018_2025                             the same in square kilometres: hectares / 100, to 6 decimals
  forest_at_window_start_ha_2018_2025          from `district_need.csv`
  n1_per_100_ha_of_forest_at_window_start      100 x N1 / forest at window start, rounded half up to 6 decimals
  fsi_calculated_area_km2, fsi_very_dense_km2, fsi_moderately_dense_km2, fsi_open_km2, fsi_forest_cover_km2,
  fsi_forest_cover_pct_of_area, fsi_change_wrt_2021_km2, fsi_scrub_km2
                                               the row's eight numbers, as printed
  fsi_scrub_pct_of_forest_cover                100 x scrub / total forest cover, rounded half up to 6 decimals
  fsi_change_pct_of_forest_cover               100 x change with respect to 2021 / total forest cover (of 2023), rounded
                                               half up to 6 decimals; it carries the sign of the change

fsi_summary.csv - four rank correlations over the 30 districts, each computed as in Phase 2: Spearman's rho with
average ranks for ties, a two-sided permutation p from 99,999 shuffles, a percentile bootstrap 95 % interval from
9,999 draws of districts, the seeds recorded (base 20261010; for the k-th row, k from 0, permutation seed base + 900 + k
and bootstrap seed base + 950 + k)
  a   n1_ha_2018_2025                           against  fsi_change_wrt_2021_km2
  b   n1_ha_2018_2025                           against  fsi_scrub_km2
  c   n1_per_100_ha_of_forest_at_window_start   against  fsi_change_pct_of_forest_cover
  d   n1_per_100_ha_of_forest_at_window_start   against  fsi_scrub_pct_of_forest_cover
  columns: id, what, x, y, size_free (no for a and b; yes for c and d, in which both sides are divided by the district's
  own forest), n_districts, rho (6 decimals), p_permutation, ci95_lo, ci95_hi (6 decimals), n_permutations,
  n_bootstrap, n_bootstrap_undefined, seed_permutation, seed_bootstrap, and `the_two_sources`: the same short text on
  every row, which says what each source measures and that they are not the same quantity. rho, p and the interval's
  ends are written as numbers rounded to those decimals (p to 5), as Phase 2 writes them: a final zero is not printed
  (`0.59774` is 0.597740) and the smallest p there can be, one in a hundred thousand, is written `1e-05`.

gates_phase5b.csv (`gate`, `expected`, `found`, `pass`), and this step's section of `gap.provenance.json`. The gates:
30 rows, matched one to one; the five spelling rules and no others; each of the seven columns that can be added, summed
over the 30 districts, equals the table's printed Grand Total row and the figure the owner gave for it, exactly; every
row's three density classes add to its total; every printed per cent is 100 x total / calculated area to two
decimals, the Grand Total's too; the state's N1 here is the one `district_need.csv` gives; and all four rank
correlations were computed.
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D, dsum  # noqa: E402

STEP = "08_build_gap_fsi"
SEED = 20261010
TABLE = "Table 10.20.3"
SPELLING_RULE = {"Angul": "384", "Baleswar": "377", "Deogarh": "373", "Jagatsinghpur": "380", "Nabarangpur": "397"}   # the owner's, 11 October 2026
COLUMNS = ["fsi_calculated_area_km2", "fsi_very_dense_km2", "fsi_moderately_dense_km2", "fsi_open_km2", "fsi_forest_cover_km2",
           "fsi_forest_cover_pct_of_area", "fsi_change_wrt_2021_km2", "fsi_scrub_km2"]
# The owner's figures for the printed Grand Total row (his instruction of 11 October 2026). The per cent is not a sum and has none.
GRAND_TOTAL_EXPECTED = {"fsi_calculated_area_km2": "155707", "fsi_very_dense_km2": "7224.42", "fsi_moderately_dense_km2": "21065.55", "fsi_open_km2": "24143.59",
                        "fsi_forest_cover_km2": "52433.56", "fsi_change_wrt_2021_km2": "151.89", "fsi_scrub_km2": "4632.68"}
THE_TWO_SOURCES = ("Hansen: gross, stand-replacing loss by year on land with canopy above 10 per cent in 2000. Forest Survey of India: forest cover of its 2023 "
                   "assessment, the net change in it with respect to its 2021 assessment, and scrub. Not the same quantity; neither can be subtracted from the other")
ROW = re.compile(r"^\s*([A-Za-z][A-Za-z ]*?)\s+((?:-?[\d,]+(?:\.\d+)?\s+){7}-?[\d,]+(?:\.\d+)?)\s*$")


def q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def read_table(path: Path) -> tuple[list[tuple[str, list[Decimal]]], list[Decimal]]:
    """The district rows of Table 10.20.3 and its Grand Total row, by the rule of the docstring."""
    rows, total, inside = [], None, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if TABLE in line:
            inside = total is None                                # a heading after the Grand Total row opens nothing
            continue
        if not inside:
            continue
        m = ROW.match(line)
        if not m:
            continue
        numbers = [D(x.replace(",", "")) for x in m.group(2).split()]
        if m.group(1).strip() == "Grand Total":
            total, inside = numbers, False
        else:
            rows.append((m.group(1).strip(), numbers))
    if total is None:
        G.stop(f"{G.rel(path)}: no Grand Total row was read under {TABLE}")
    return rows, total


def main() -> None:
    G.require_stage4_environment()
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    inputs = {"isfr_vol2_odisha": G.IN["isfr_vol2_odisha"], "district_need": G.OUT / "district_need.csv"}
    for p in inputs.values():
        if not p.exists():
            G.stop(f"an input is missing: {G.rel(p)}")
    need = G.read_rows(inputs["district_need"])
    code_of = {r["district_name"]: r["pc11_district_code"] for r in need}
    by_code = {r["pc11_district_code"]: r for r in need}
    table, total = read_table(inputs["isfr_vol2_odisha"])
    add("district rows read under Table 10.20.3 of the Forest Survey's report", 30, len(table), len(table) == 30)

    needs_rule = sorted(name for name, _ in table if name not in code_of)
    add("names of the table that are not a census name of the repository: the owner's five and no others",
        ", ".join(sorted(SPELLING_RULE)), ", ".join(needs_rule), needs_rule == sorted(SPELLING_RULE))
    matched = {}
    for name, numbers in table:
        code = code_of.get(name) or SPELLING_RULE.get(name)
        if code is None:
            G.stop(f"a district of the Forest Survey's table has no census code: {name}")
        if code in matched:
            G.stop(f"two rows of the Forest Survey's table take the census code {code}")
        matched[code] = (name, numbers, "census name" if name in code_of else "spelling rule")
    add("the table's rows against the 30 census districts: matched one to one", "30, each code once",
        f"{len(matched)}, each code once: {'yes' if set(matched) == set(by_code) else 'NO'}", set(matched) == set(by_code) and len(matched) == 30)
    rule_ok = all(matched.get(code, ("",))[0] == name for name, code in SPELLING_RULE.items())
    add("the five spelling rules, as the owner gave them: Angul 384, Baleswar 377, Deogarh 373, Jagatsinghpur 380, Nabarangpur 397", "each name on its code",
        "; ".join(f"{name} {code}" for code, (name, _, how) in sorted(matched.items()) if how == "spelling rule"), rule_ok)

    for k, col in enumerate(COLUMNS):
        if col not in GRAND_TOTAL_EXPECTED:
            continue
        s = dsum(numbers[k] for _, numbers, _ in matched.values())
        add(f"{col}: the 30 districts summed, the table's printed Grand Total, and the figure the owner gave for it", GRAND_TOTAL_EXPECTED[col],
            f"sum {format(s, 'f')}; printed {format(total[k], 'f')}", s == total[k] == D(GRAND_TOTAL_EXPECTED[col]))
    adds = sum(1 for _, n, _ in matched.values() if n[1] + n[2] + n[3] == n[4])
    add("districts whose very dense, moderately dense and open forest add to their total forest cover", "30 of 30", f"{adds} of {len(matched)}", adds == len(matched) == 30)
    pct = sum(1 for _, n, _ in matched.values() if q(100 * n[4] / n[0], "0.01") == n[5])
    add("districts whose printed per cent is 100 x total forest cover / calculated area, to two decimals; and the Grand Total's", "30 of 30; and yes",
        f"{pct} of {len(matched)}; {'yes' if q(100 * total[4] / total[0], '0.01') == total[5] else 'NO'}", pct == len(matched) == 30 and q(100 * total[4] / total[0], "0.01") == total[5])

    rows = []
    for code in sorted(matched):
        name, n, how = matched[code]
        d = by_code[code]
        n1, start = D(d["n1_ha_2018_2025"]), D(d["forest_at_window_start_ha_2018_2025"])
        row = {"pc11_district_code": code, "district_name": d["district_name"], "fsi_district_name": name, "match_rule": how,
               "n1_ha_2018_2025": n1, "n1_km2_2018_2025": q(n1 / 100, "0.000001"), "forest_at_window_start_ha_2018_2025": start,
               "n1_per_100_ha_of_forest_at_window_start": q(100 * n1 / start, "0.000001")}
        row.update({col: n[k] for k, col in enumerate(COLUMNS)})
        row["fsi_scrub_pct_of_forest_cover"] = q(100 * n[7] / n[4], "0.000001")
        row["fsi_change_pct_of_forest_cover"] = q(100 * n[6] / n[4], "0.000001")
        rows.append(row)
    state_n1 = dsum(r["n1_ha_2018_2025"] for r in rows)
    add("N1 of the state in this table against the table of districts (hectares)", format(dsum(D(r["n1_ha_2018_2025"]) for r in need), "f"), format(state_n1, "f"),
        state_n1 == dsum(D(r["n1_ha_2018_2025"]) for r in need))

    f = lambda key: [float(r[key]) for r in rows]
    summary, seeds = [], {}
    for k, (rid, x, y, free, words) in enumerate((
            ("a", "n1_ha_2018_2025", "fsi_change_wrt_2021_km2", "no", "N1 of 2018-2025 (ha) against the Forest Survey's change in forest cover with respect to 2021 (km2)"),
            ("b", "n1_ha_2018_2025", "fsi_scrub_km2", "no", "N1 of 2018-2025 (ha) against the Forest Survey's scrub (km2)"),
            ("c", "n1_per_100_ha_of_forest_at_window_start", "fsi_change_pct_of_forest_cover", "yes",
             "N1 per 100 ha of forest at the start of 2018 against the Forest Survey's change as a per cent of its forest cover"),
            ("d", "n1_per_100_ha_of_forest_at_window_start", "fsi_scrub_pct_of_forest_cover", "yes",
             "N1 per 100 ha of forest at the start of 2018 against the Forest Survey's scrub as a per cent of its forest cover"))):
        st = G.spearman_with_inference(f(x), f(y), SEED + 900 + k, SEED + 950 + k)
        seeds[rid] = [SEED + 900 + k, SEED + 950 + k]
        summary.append({"id": rid, "what": words, "x": x, "y": y, "size_free": free, "n_districts": st["n"], "rho": round(st["rho"], 6), "p_permutation": st["p_permutation"],
                        "ci95_lo": round(st["ci95_lo"], 6), "ci95_hi": round(st["ci95_hi"], 6), "n_permutations": st["n_permutations"], "n_bootstrap": st["n_bootstrap"],
                        "n_bootstrap_undefined": st["n_bootstrap_undefined"], "seed_permutation": st["seed_permutation"], "seed_bootstrap": st["seed_bootstrap"],
                        "the_two_sources": THE_TWO_SOURCES})
    add("rank correlations computed (N1 against change and against scrub; and the same two with size taken out of both sides)", 4, len(summary), len(summary) == 4)

    G.write_rows(G.OUT / "fsi_district_check.csv", rows,
                 ["pc11_district_code", "district_name", "fsi_district_name", "match_rule", "n1_ha_2018_2025", "n1_km2_2018_2025", "forest_at_window_start_ha_2018_2025",
                  "n1_per_100_ha_of_forest_at_window_start"] + COLUMNS + ["fsi_scrub_pct_of_forest_cover", "fsi_change_pct_of_forest_cover"])
    G.write_rows(G.OUT / "fsi_summary.csv", summary,
                 ["id", "what", "x", "y", "size_free", "n_districts", "rho", "p_permutation", "ci95_lo", "ci95_hi", "n_permutations", "n_bootstrap", "n_bootstrap_undefined",
                  "seed_permutation", "seed_bootstrap", "the_two_sources"])
    grows = [{"gate": g, "expected": e, "found": f_, "pass": "yes" if ok else "NO"} for g, e, f_, ok in gates]
    G.write_rows(G.OUT / "gates_phase5b.csv", grows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("fsi_district_check.csv", "fsi_summary.csv", "gates_phase5b.csv")]
    G.record_step(STEP, Path(__file__), inputs, outputs, {
        "seeds": {"base": SEED, **seeds, "generator": "numpy.random.default_rng"}, "permutations": 99999, "bootstrap_resamples": 9999,
        "the_table": {"name": TABLE + ", District-wise Forest Cover in Odisha (India State of Forest Report 2023, Volume II)", "unit": "km2",
                      "grand_total_as_printed": {col: format(total[k], "f") for k, col in enumerate(COLUMNS)}, "spelling_rule": SPELLING_RULE},
        "gates": len(grows), "gates_passed": sum(r["pass"] == "yes" for r in grows)})
    for r in grows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in grows if r["pass"] != "yes"]
    print(f"\n{len(grows) - len(failed)} of {len(grows)} gates passed; wrote {', '.join(G.rel(p) for p in outputs)}")
    for s in summary:
        print(f"{s['id']}: rho {s['rho']} ({s['ci95_lo']} to {s['ci95_hi']}), permutation p {s['p_permutation']:.5f}  [{s['what']}]")
    if failed:
        G.stop(f"{len(failed)} gate(s) failed; see 50_gap/gates_phase5b.csv")


if __name__ == "__main__":
    main()
