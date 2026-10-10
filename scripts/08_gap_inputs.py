"""Stage 4, step 0: the inputs read and listed, the district crosswalk, a district for every unit, and the gates.

Writes into `50_gap/` only:

* `inputs_listing.json` - every input this stage reads: path, bytes, SHA-256, number of rows and the column names.
* `district_crosswalk.csv` - 30 rows: `r620_district` (as R6.20 spells it), `pc11_district_code`, `district_name`
  (as the repository spells it: the name the Odisha FRA table and the decision table carry for that code) and
  `match_rule`. Twenty-four R6.20 names equal the census name once both are upper-cased
  (`match_rule` = `case-folded census name`); six need the owner's spelling rule of 10 October 2026
  (`match_rule` = `spelling rule`): ANGUL 384, BOLANGIR 393, BOUDH 391, DEOGARH 373, JAJPUR 382, SONEPUR 392.
  The build stops unless exactly those six, and no others, fail the case-folded match; unless the table is 30 rows, one
  to one; and unless each code from 370 to 399 appears once. As a check that is not the rule, the geotagged record's
  own table of districts (`40_allocation/assets_district_fy.csv`, columns `district_property` and
  `pc11_district_code`) must give the same code for every R6.20 name it carries.
* `unit_district.csv` - 11,468 rows: `unit_id`, `unit_level`, `outside_village`, `pc11_district_code`, `district_name`,
  `district_from`. An LGD panchayat unit takes the census district code it carries in `10_units/units.gpkg`
  (`district_from` = `units.gpkg`); an outside-village unit takes the code assigned to it in
  `10_units/outside_village_district.csv` (`district_from` = `outside_village_district.csv`). The build stops unless
  there are 11,468 units, 30 districts and no unit without one, and unless every unit's code equals the one the
  decision table (`55_decision/condition_by_unit.csv`) carries.
* `inputs_check.csv` - the gates on what is already built: `gate`, `expected`, `found`, `pass`. The expected values are
  the owner's, read by him from the files and documents he names; none is changed here, and a gate that fails stops the
  run after the whole table has been written, so that what was found can be read.
* its section of `gap.provenance.json`.

Run with the stage-4 interpreter (`README.md` section 0): `~/.venvs/ictd-stage4/bin/python scripts/08_gap_inputs.py`. The gate on the
environments themselves is `scripts/08_gap_environment.py`.

Sums of money and hectares are exact (`decimal.Decimal`). A share in per cent is compared after rounding to the two
decimals the expected value has. No Earth Engine, no network.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D, dsum  # noqa: E402

STEP = "08_gap_inputs"
EXPECTED_ZERO_TITLE_DISTRICTS = ["Sundargarh", "Bhadrak", "Kendrapara", "Jagatsinghapur", "Khordha", "Puri"]
CELL_ORDER = ["open_loss", "dense_loss", "open_none", "dense_none", "little_loss", "little_none"]


def q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def listing() -> list[dict]:
    import pyogrio
    out = []
    for key, path in G.IN.items():
        if not path.exists():
            G.stop(f"an input is missing: {G.rel(path)}")
        entry = {"key": key, "path": G.rel(path), "bytes": path.stat().st_size, "sha256": G.sha256(path)}
        if path.suffix == ".csv":
            entry["columns"] = G.read_header(path)
            with open(path, encoding="utf-8") as f:
                entry["rows"] = sum(1 for _ in f) - 1
        elif path.suffix == ".gpkg":
            info = pyogrio.read_info(path)
            entry["columns"] = [str(c) for c in info["fields"]]
            entry["rows"] = int(info["features"])
            entry["geometry"] = str(info["geometry_type"])
            entry["crs"] = str(info["crs"])
        else:
            entry["columns"] = None
            entry["rows"] = None
        out.append(entry)
    return out


def crosswalk(r620: list[dict], fra: list[dict], assets: list[dict], gates: list) -> list[dict]:
    names = {r["pc11_district_code"]: r["district"] for r in fra}
    if len(names) != 30:
        G.stop("the FRA district table does not carry 30 district codes")
    by_upper = {}
    for code, name in names.items():
        if name.upper() in by_upper:
            G.stop(f"two census district names fold to the same text: {name}")
        by_upper[name.upper()] = code
    r_names = sorted({r["district"] for r in r620})
    rows, needing_rule = [], []
    for rn in r_names:
        if rn.upper() in by_upper:
            code, rule = by_upper[rn.upper()], "case-folded census name"
        else:
            needing_rule.append(rn)
            if rn not in G.R620_SPELLING_RULE:
                G.stop(f"R6.20 district {rn!r} matches no census name and is not in the spelling rule")
            code, rule = G.R620_SPELLING_RULE[rn], "spelling rule"
        rows.append({"r620_district": rn, "pc11_district_code": code, "district_name": names[code], "match_rule": rule})
    rows.sort(key=lambda r: r["pc11_district_code"])
    codes = [r["pc11_district_code"] for r in rows]
    gates.append(("0.1 crosswalk: rows", "30", str(len(rows)), len(rows) == 30))
    one_to_one = len(set(codes)) == 30 and len({r["r620_district"] for r in rows}) == 30
    gates.append(("0.1 crosswalk: one R6.20 name to one census code", "yes", "yes" if one_to_one else "no", one_to_one))
    each_once = sorted(codes) == [str(c) for c in range(370, 400)]
    gates.append(("0.1 crosswalk: each code from 370 to 399 appears once", "yes", "yes" if each_once else "no",
                  each_once))
    six = sorted(needing_rule) == sorted(G.R620_SPELLING_RULE)
    gates.append(("0.1 crosswalk: the R6.20 names that need a spelling rule",
                  ", ".join(sorted(G.R620_SPELLING_RULE)), ", ".join(sorted(needing_rule)), six))
    # A check that is not the rule: the geotagged record's own district table names a code for each district property.
    prop = {}
    for r in assets:
        prop.setdefault(r["district_property"].strip().upper(), set()).add(r["pc11_district_code"])
    seen, agree = 0, 0
    for r in rows:
        if r["r620_district"] in prop:
            seen += 1
            agree += prop[r["r620_district"]] == {r["pc11_district_code"]}
    gates.append((f"0.1 crosswalk: same code as the geotagged record's district table, for the {seen} R6.20 names "
                  "it carries (a check added by the build)", str(seen), str(agree), seen == agree and seen > 0))
    return rows


def unit_districts(names: dict, cond: list[dict], gates: list) -> list[dict]:
    import pyogrio
    units = pyogrio.read_dataframe(G.IN["units_gpkg"], read_geometry=False)
    outside = {r["unit_id"]: r["pc11_district_code"].strip() for r in G.read_rows(G.IN["outside_district"])}
    rows = []
    for u in units.itertuples(index=False):
        uid = str(u.unit_id)
        is_outside = str(u.outside_village).strip() in ("1", "1.0", "True", "true")
        if is_outside:
            code, source = outside.get(uid, ""), "outside_village_district.csv"
        else:
            raw = u.pc11_district_code
            code = "" if raw is None or str(raw).strip() in ("", "nan", "None") else str(int(float(raw)))
            source = "units.gpkg"
        rows.append({"unit_id": uid, "unit_level": str(u.unit_level), "outside_village": "1" if is_outside else "0",
                     "pc11_district_code": code, "district_name": names.get(code, ""), "district_from": source})
    n = len(rows)
    n_ids = len({r["unit_id"] for r in rows})
    without = sum(1 for r in rows if r["pc11_district_code"] == "" or r["district_name"] == "")
    districts = len({r["pc11_district_code"] for r in rows if r["pc11_district_code"]})
    gates.append(("0.2 units: number of units, each once", "11468", str(n if n == n_ids else f"{n} rows, {n_ids} ids"),
                  n == 11468 and n_ids == 11468))
    gates.append(("0.2 units: districts", "30", str(districts), districts == 30))
    gates.append(("0.2 units: units without a district", "0", str(without), without == 0))
    n_out = sum(1 for r in rows if r["outside_village"] == "1")
    used = sum(1 for r in rows if r["outside_village"] == "1" and r["unit_id"] in outside)
    gates.append(("0.2 units: outside-village units, each with a row in outside_village_district.csv "
                  "(a check added by the build)", str(len(outside)), str(used), used == n_out == len(outside)))
    decision = {r["unit_id"]: r["pc11_district_code"] for r in cond}
    same = sum(1 for r in rows if decision.get(r["unit_id"]) == r["pc11_district_code"])
    gates.append(("0.2 units: units whose district equals the decision table's (a check added by the build)",
                  "11468", str(same), same == 11468 and len(decision) == 11468))
    rows.sort(key=lambda r: (r["pc11_district_code"], r["outside_village"], r["unit_id"]))
    return rows


def r620_gates(r620: list[dict], state: list[dict], gates: list) -> None:
    def district_sum(cat: str, fys, col: str = "exp_cat_lakh") -> Decimal:
        return dsum(D(r[col]) for r in r620 if r["category"] == cat and r["fy"] in fys)

    def state_sum(cat: str, fys, col: str = "exp_cat_lakh") -> Decimal:
        return dsum(D(r[col]) for r in state if r["category"] == cat and r["fy"] in fys)

    if sorted({r["fy"] for r in r620}) != G.FY_ALL or sorted({r["category"] for r in r620}) != sorted(G.CATEGORIES):
        G.stop("R6.20's financial years or categories are not the 13 and the 3 expected")
    if len(r620) != 13 * 3 * 30:
        G.stop(f"R6.20 district file has {len(r620)} rows, not 1,170")
    periods = (("FY2014-15 to 2017-18", G.PRE), ("FY2018-19 to 2025-26", G.POST), ("FY2026-27 (part year)", [G.PART]))
    expected = {("Plantation", 0): "151843.18", ("Plantation", 1): "13915.72", ("Plantation", 2): "110.58",
                ("NRM", 0): "327829.94", ("NRM", 1): "2334964.06"}
    for (cat, k), exp in expected.items():
        found = district_sum(cat, periods[k][1])
        gates.append((f"R6.20 {cat} expenditure, summed over districts, {periods[k][0]}, lakh", exp, format(found, "f"),
                      found == Decimal(exp)))
    # exp_all_lakh: one value per district-year, printed on each of the three category rows.
    per_cell = {}
    for r in r620:
        per_cell.setdefault((r["fy"], r["district"]), set()).add(r["exp_all_lakh"])
    one_value = all(len(v) == 1 for v in per_cell.values()) and len(per_cell) == 390
    gates.append(("R6.20 all expenditure: one value of exp_all_lakh per district-year, 390 district-years", "yes",
                  "yes" if one_value else "no", one_value))
    all_by = {k: D(next(iter(v))) for k, v in per_cell.items()}
    for k, exp in ((0, "750836.66"), (1, "3674731.26")):
        found = dsum(v for (fy, _), v in all_by.items() if fy in periods[k][1])
        gates.append((f"R6.20 all expenditure (exp_all_lakh, one value per district-year), {periods[k][0]}, lakh", exp,
                      format(found, "f"), found == Decimal(exp)))
    # Every district-period sum against the state's printed Total rows.
    worst, worst_what, n_compared = Decimal(0), "", 0
    for label, fys in periods:
        for cat in G.CATEGORIES:
            diff = abs(district_sum(cat, fys) - state_sum(cat, fys))
            n_compared += 1
            if diff > worst:
                worst, worst_what = diff, f"{cat}, {label}"
        st_all = dsum(D(r["exp_all_lakh"]) for r in state if r["category"] == "NRM" and r["fy"] in fys)
        diff = abs(dsum(v for (fy, _), v in all_by.items() if fy in fys) - st_all)
        n_compared += 1
        if diff > worst:
            worst, worst_what = diff, f"all expenditure, {label}"
    gates.append((f"R6.20: every district-period sum equals the state's printed Total rows ({n_compared} sums: "
                  "3 categories and all expenditure, 3 periods), largest difference in lakh",
                  "at most 0.01", format(worst, "f") + (f" ({worst_what})" if worst else ""), worst <= Decimal("0.01")))
    state_all_same = all(len({r["exp_all_lakh"] for r in state if r["fy"] == fy}) == 1 for fy in G.FY_ALL)
    gates.append(("R6.20 state totals: exp_all_lakh the same on the three category rows of a year (a check added by "
                  "the build)", "yes", "yes" if state_all_same else "no", state_all_same))
    for fy, exp in (("2016-2017", "57135"), ("2025-2026", "4105")):
        found = dsum(D(r["works_ongoing"]) + D(r["works_completed"]) for r in r620
                     if r["category"] == "Plantation" and r["fy"] == fy)
        gates.append((f"plantation works, ongoing plus completed, state, FY{G.fy_short(fy)}", exp, format(found, "f"),
                      found == Decimal(exp)))
    zero = sum(1 for r in r620 if r["category"] == "Plantation" and r["fy"] in G.POST and D(r["exp_cat_lakh"]) == 0)
    n_post = sum(1 for r in r620 if r["category"] == "Plantation" and r["fy"] in G.POST)
    gates.append(("district-years FY2018-19 to 2025-26 with zero plantation expenditure", "66 of 240",
                  f"{zero} of {n_post}", zero == 66 and n_post == 240))
    for label, fys, wanted in (("post-period", G.POST, (("RAYAGADA", "29.76"), ("MAYURBHANJ", "11.40"),
                                                         ("BOLANGIR", "6.77"))),
                               ("pre-period", G.PRE, (("MAYURBHANJ", "20.49"), ("RAYAGADA", "10.77"),
                                                       ("GANJAM", "7.64")))):
        total = district_sum("Plantation", fys)
        shares = {}
        for r in r620:
            if r["category"] == "Plantation" and r["fy"] in fys:
                shares[r["district"]] = shares.get(r["district"], Decimal(0)) + D(r["exp_cat_lakh"])
        ranked = sorted(shares, key=lambda d: shares[d], reverse=True)[:3]
        found = [(d, format(q2(shares[d] / total * 100), "f")) for d in ranked]
        gates.append((f"{label} share of state plantation expenditure, the three largest, %",
                      " / ".join(f"{d.title()} {s}" for d, s in wanted),
                      " / ".join(f"{d.title()} {s}" for d, s in found), found == list(wanted)))


def other_gates(fra, bands, cond, need, gates) -> None:
    titles = {r["district"]: int(r["titles_distributed_comm_st"]) + int(r["titles_distributed_comm_otfd"]) for r in fra}
    found = sum(titles.values())
    gates.append(("FRA community titles distributed, ST plus OTFD, state", "9432", str(found), found == 9432))
    extent = dsum(D(r["extent_ha_comm_st"]) + D(r["extent_ha_comm_otfd"]) for r in fra)
    gates.append(("FRA community extent, ha", "331568.00", format(q2(extent), "f"), extent == Decimal("331568")))
    none = [r["district"] for r in fra if titles[r["district"]] == 0]
    gates.append(("districts that have distributed no community title",
                  "6: " + ", ".join(EXPECTED_ZERO_TITLE_DISTRICTS), f"{len(none)}: " + ", ".join(none),
                  sorted(none) == sorted(EXPECTED_ZERO_TITLE_DISTRICTS)))
    dense = dsum(D(r[f"loss_ha_gt30_{y}"]) for r in bands for y in G.YEARS)
    open_ = dsum(D(r[f"loss_ha_gt10le30_{y}"]) for r in bands for y in G.YEARS)
    found = f"{format(q2(dense / 100), 'f')} / {format(q2(open_ / 100), 'f')}"
    gates.append(("Hansen loss 2001-2025 summed over units and years: dense band / open band, km2", "1552.64 / 363.84",
                  found, found == "1552.64 / 363.84"))
    w = range(2018, 2026)
    loss_by_unit = {r["unit_id"]: dsum(D(r[f"loss_ha_gt30_{y}"]) + D(r[f"loss_ha_gt10le30_{y}"]) for y in w)
                    for r in bands}
    total = dsum(loss_by_unit.values())
    gates.append(("forest loss 2018-2025, dense plus open, summed over units from the per-year table, ha (within 1)",
                  "90028", format(total, "f"), abs(total - Decimal(90028)) <= 1))
    cell = {r["unit_id"]: r["cell_2018_2025"] for r in cond}
    in_loss = dsum(v for u, v in loss_by_unit.items() if cell[u] in G.LOSS_CELLS)
    gates.append(("the same, over units in the three \"loss recorded\" cells of the default window, ha (within 2)",
                  "89657", format(in_loss, "f"), abs(in_loss - Decimal(89657)) <= 2))
    table_total = dsum(D(r["forest_loss_ha_2018_2025"]) for r in cond)
    gates.append(("forest loss 2018-2025: the decision table's own column summed equals the per-year table's sum "
                  "(a check added by the build)", format(total, "f"), format(table_total, "f"), table_total == total))
    anr = dsum(D(r["standing_open_ha"]) for r in cond if r["cell_2018_2025"] == G.ANR_CELL)
    gates.append(("standing open-band hectares in the assisted-natural-regeneration cell, default window, ha "
                  "(within 1)", "293921", format(anr, "f"), abs(anr - Decimal(293921)) <= 1))
    counts = {}
    for r in cond:
        counts[r["cell_2018_2025"]] = counts.get(r["cell_2018_2025"], 0) + 1
    found = " / ".join(str(counts.get(c, 0)) for c in CELL_ORDER)
    gates.append(("units per default-window cell: restore / find the cause first / regeneration candidate / protect / "
                  "verify on the ground / not a forest site", "406 / 1295 / 3055 / 1040 / 33 / 5639", found,
                  found == "406 / 1295 / 3055 / 1040 / 33 / 5639" and sum(counts.values()) == 11468))
    lgd = [r for r in need if r["unit_level"] == "lgd_panchayat"]
    pop = sum(int(r["population"]) for r in lgd)
    st = sum(int(r["st_pop"]) for r in lgd)
    gates.append(("LGD panchayat units: population / Scheduled Tribe population", "34766888 / 8895006", f"{pop} / {st}",
                  pop == 34766888 and st == 8895006))
    gates.append(("LGD panchayat units in the need table (a check added by the build)", "7976", str(len(lgd)),
                  len(lgd) == 7976))


def main() -> None:
    G.require_stage4_environment()
    G.OUT.mkdir(parents=True, exist_ok=True)
    files = listing()
    (G.OUT / "inputs_listing.json").write_text(json.dumps({"run_utc": G.utc_now(), "inputs": files}, indent=1) + "\n",
                                               encoding="utf-8")
    r620 = G.read_rows(G.IN["r620_district"])
    state = G.read_rows(G.IN["r620_state"])
    fra = G.read_rows(G.IN["fra_district"])
    assets = G.read_rows(G.IN["assets_district_fy"])
    cond = G.read_rows(G.IN["condition_by_unit"])
    bands = G.read_rows(G.IN["hansen_bands"])
    need = G.read_rows(G.IN["need_by_unit"])
    gates: list[tuple] = []

    cw = crosswalk(r620, fra, assets, gates)
    G.write_rows(G.OUT / "district_crosswalk.csv", cw,
                 ["r620_district", "pc11_district_code", "district_name", "match_rule"])
    names = {r["pc11_district_code"]: r["district_name"] for r in cw}
    ud = unit_districts(names, cond, gates)
    G.write_rows(G.OUT / "unit_district.csv", ud,
                 ["unit_id", "unit_level", "outside_village", "pc11_district_code", "district_name", "district_from"])
    r620_gates(r620, state, gates)
    other_gates(fra, bands, cond, need, gates)

    rows = [{"gate": g, "expected": e, "found": f, "pass": "yes" if ok else "NO"} for g, e, f, ok in gates]
    G.write_rows(G.OUT / "inputs_check.csv", rows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("inputs_listing.json", "district_crosswalk.csv", "unit_district.csv",
                                   "inputs_check.csv")]
    G.record_step(STEP, Path(__file__), G.IN, outputs,
                  {"gates": len(rows), "gates_passed": sum(r["pass"] == "yes" for r in rows)})
    failed = [r for r in rows if r["pass"] != "yes"]
    for r in rows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] +
              "  |  found " + r["found"])
    print(f"\n{len(rows) - len(failed)} of {len(rows)} gates passed; wrote {', '.join(G.rel(p) for p in outputs)}")
    if failed:
        G.stop(f"{len(failed)} gate(s) failed; see 50_gap/inputs_check.csv. Nothing downstream may run.")


if __name__ == "__main__":
    main()
