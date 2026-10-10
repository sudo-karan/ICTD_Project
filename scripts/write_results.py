#!/usr/bin/env python3
"""Writes docs/RESULTS.md: the state of the pipeline and every headline number with its caveat, for a reader who has
followed none of it.

No figure is typed in this file. Each one is read from a file through cell(), key(), count() or agg(), which keep the
file and the place in it; the document's appendix is that record. The run stops if
  1. the text carries a digit of its own - outside code spans, dates, years and a short list of names (ALLOWED);
  2. a figure is printed that was not defined, or defined and not printed;
  3. a conclusion the text draws from figures does not hold in them (hold());
  4. a total that two files both carry differs between them (same());
  5. one of the three verifiers fails.
A figure that cannot be read is not written: a missing file, a missing key or a blank cell stops the run.

The records of the layer's checks in a browser must be of the layer that is on disk, or the run stops - with ONE EXCEPTION,
made on 9 October 2026 by the project owner's choice. Until then the record of the check in the Safari application
(60_layer/exercise_safari.json) had to be of that build like the two others. Now it may be of an earlier build IF the
runner's record of this build (60_layer/decision_runs.json, written by scripts/run_decision_checks.py) is finished, is of
the layer on disk, and names that check as left out of its pass with a reason. The text then says, wherever it speaks of
Safari, that the application was not opened on this build, gives the reason as the record has it, and gives the build the
last Safari run was of. The Chrome and WebKit records must still be of the build on disk: that rule is unchanged.

One group of figures has no stage output to come from: those of the NIRv replication, which are read from the
working files of the session that made them (git-ignored, not rebuilt by any tracked script). The appendix marks them.

Output: docs/RESULTS.md and nothing else; its inputs, their sha256 and the UTC time of the run are in its appendix.
  python scripts/write_results.py              runs the verifiers, writes docs/RESULTS.md
  python scripts/write_results.py --draft p    skips the verifiers and writes to p instead (never into docs/)
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "RESULTS.md"
SCRATCH = ".session_scratch_2026-10-05"          # working files of the sessions that built the pipeline; git-ignored
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
ALLOWED = [                                       # digits the text may carry: none of them is a measurement
    (rf"\b\d{{1,2}} (?:{MONTHS}) (?:19|20)\d\d\b", "a date"),
    (r"\bFY ?(?:19|20)\d\d-\d\d\b", "a financial year"),
    (r"\b(?:19|20)\d\d\b", "a year"),
    (r"(?m)^#{1,4} \d+(?:\.\d+)*\.? ", "the number of a heading"),
    (r"§ ?\d+[a-z]?(?:\.\d+)?", "a reference to a section"),
    (r"\b[Ss]tage \d\b", "the number of a stage of the pipeline"),
    (r"Landsat 8|R6\.20|CC BY-NC-SA 4\.0|CC BY 4\.0|ODbL 1\.0|WGS84", "a name: a satellite, a report, a licence, a datum"),
]

FILES, FIG, TABLES, HELD, SAME = {}, {}, {}, [], []
_csv, _json = {}, {}


def stop(message):
    raise SystemExit("RESULTS not written: " + message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def use(path):
    p = ROOT / path
    if not p.is_file():
        stop(f"{path} is not there")
    if path not in FILES:
        FILES[path] = {"bytes": p.stat().st_size, "sha256": sha256(p), "run_utc": ""}
    return p


def J(path):
    if path not in _json:
        _json[path] = json.loads(use(path).read_text(encoding="utf-8"))
        stamp = _json[path].get("run_utc") or (_json[path].get("summary") or {}).get("run_utc") if isinstance(_json[path], dict) else ""
        FILES[path]["run_utc"] = stamp if isinstance(stamp, str) else ""
    return _json[path]


def C(path):
    if path not in _csv:
        # "NA" is a value in the allocation tables (a work with no usable start date), so only an empty cell is blank
        _csv[path] = pd.read_csv(use(path), dtype={"unit_id": str, "fy_work_start": str, "fy": str}, keep_default_na=False, na_values=[""])
    return _csv[path]


class V:
    """A value with where it was read: the file, the column or key, the row."""
    def __init__(self, v, file, col, row=""):
        self.v, self.file, self.col, self.row = v, file, col, row

    @property
    def where(self):
        return self.col + (f"; row where {self.row}" if self.row else "")


def cell(path, column, blank_ok=False, **where):
    t = C(path)
    m = pd.Series(True, index=t.index)
    for k, x in where.items():
        m &= t[k] == x
    said = " and ".join(f"`{k}` is {x!r}" for k, x in where.items())
    if int(m.sum()) != 1:
        stop(f"{path}: {int(m.sum())} rows where {said}, not one")
    v = t.loc[m, column].iloc[0]
    if pd.isna(v):
        if blank_ok:
            return V(None, path, f"column `{column}`", said)
        stop(f"{path}: `{column}` is blank where {said}")
    return V(v.item() if hasattr(v, "item") else v, path, f"column `{column}`", said)


def key(path, keys):
    v = J(path)
    for k in keys.split("/"):
        try:
            v = v[int(k)] if isinstance(v, list) else v[k]
        except (KeyError, IndexError, ValueError):
            stop(f"{path}: no key {keys}")
    if v is None:
        stop(f"{path}: {keys} is null")
    return V(v, path, "key " + " → ".join(f"`{k}`" for k in keys.split("/")))


def count(path, what, mask):
    return V(int(mask(C(path)).sum()), path, f"rows counted by this script: {what}")


def agg(path, what, fn):
    v = fn(C(path))
    if pd.isna(v):
        stop(f"{path}: {what} is blank")
    return V(float(v), path, f"worked out by this script from its rows: {what}")


def show(name, v, fmt):
    if name in FIG:
        stop(f"the figure {name} is defined twice")
    FIG[name] = {"text": fmt(v.v), "sources": [(v.file, v.where)], "formula": ""}
    return v


def calc(name, value, fmt, formula, parts):
    if name in FIG:
        stop(f"the figure {name} is defined twice")
    FIG[name] = {"text": fmt(value), "sources": [(p.file, p.where) for p in parts], "formula": formula}
    return V(value, "", formula)


def hold(condition, statement):
    """A conclusion the text draws from figures: tested here, listed in the appendix."""
    if not condition:
        stop("the text says something the figures no longer bear out: " + statement)
    HELD.append(statement)


def same(what, a, b, tolerance=0.0):
    """A total that two places both carry."""
    if abs(float(a) - float(b)) > tolerance:
        stop(f"{what}: {a} against {b}")
    SAME.append(what + (f" (to within {tolerance:g})" if tolerance else ""))


def stray_digits(text):
    t = re.sub(r"`[^`]*`", "", text)
    t = re.sub(r"\{[A-Za-z_][A-Za-z0-9_]*\}", "", t)
    for rx, _ in ALLOWED:
        t = re.sub(rx, "", t)
    return re.findall(r".{0,40}\d.{0,40}", t)


# ---- how a figure is printed ----------------------------------------------------------------------------------------------------------
def fix(s):
    return s.replace("-", "−")


def n0(x):
    return fix(f"{int(round(float(x))):,}")


def dec(k):
    return lambda x: fix(f"{float(x):,.{k}f}")


def pc(k):                       # a share, printed as per cent
    return lambda x: fix(f"{100 * float(x):,.{k}f}")


def spc(k):                      # the same, with its sign
    return lambda x: fix(f"{100 * float(x):+,.{k}f}")


def crore(x):                    # rupees, printed as crore
    return f"{float(x) / 1e7:,.1f}"


def lakh_as_crore(x):
    return f"{float(x) / 100:,.0f}"


def mb(x):
    return f"{float(x) / 1e6:.1f}"


def txt(x):
    return str(x)


def c(v, fmt):                   # a table cell
    return ("-" if v.v is None else fmt(v.v), [v])


def span(e, lo, hi, fmt=dec(2)):  # an estimate with its interval, as one table cell
    return (f"{fmt(e.v)} ({fmt(lo.v)} to {fmt(hi.v)})", [e, lo, hi]) if lo.v is not None else ("-", [e, lo, hi])


def table(name, head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    src = {}
    for label in head:
        if stray_digits(label):
            stop(f"table {name}: a heading carries a digit of its own: {label!r}")
    for r in rows:
        line = []
        for x in r:
            if isinstance(x, str):
                if stray_digits(x):
                    stop(f"table {name}: a typed label carries a digit of its own: {x!r}")
                line.append(x)
            else:
                line.append(x[0])
                for v in x[1]:
                    s = src.setdefault(v.file, {"cols": [], "rows": []})
                    if v.col not in s["cols"]:
                        s["cols"].append(v.col)
                    if v.row and v.row not in s["rows"]:
                        s["rows"].append(v.row)
        out.append("| " + " | ".join(line) + " |")
    TABLES[name] = {"md": "\n".join(out), "src": src, "cells": sum(1 for r in rows for x in r if not isinstance(x, str))}


VERIFIER_OUTPUT = {}                           # what each verifier printed, for a writer that holds a figure of its own against a line of it


def verifier(script, draft):
    if draft:
        return V("not run for this draft", f"scripts/{script}", "not run")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], capture_output=True, text=True, cwd=ROOT)
    VERIFIER_OUTPUT[script] = r.stdout
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    last = lines[-1] if lines else ""
    if r.returncode != 0:
        stop(f"scripts/{script} failed (exit {r.returncode}): {last or r.stderr.strip()[-300:]}")
    m = re.search(r"(\d+) of (\d+) checks passed", last)
    if m and m.group(1) != m.group(2):
        stop(f"scripts/{script}: {last}")
    return V(f"{m.group(1)} of {m.group(2)} checks passed" if m else "passed", f"scripts/{script}", "its exit status and last line, run by this script as it wrote the document")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", metavar="PATH", help="skip the verifiers and write here instead of docs/RESULTS.md")
    a = ap.parse_args()
    if a.draft and Path(a.draft).resolve().parent == OUT.parent:
        stop("a draft is never written into docs/")
    written = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    DOC = []

    U = "10_units/units.provenance.json"
    D = "10_units/outside_village_district.provenance.json"
    H = "20_degradation/hansen.provenance.json"
    HL = "20_degradation/hansen_by_unit_level.csv"
    BAND = "20_degradation/hansen_loss_by_canopy_band.csv"
    CSP = "20_degradation/corestack.provenance.json"
    CL = "20_degradation/corestack_by_unit_level.csv"
    CR = "20_degradation/corestack_reconciliation.csv"
    DB = "20_degradation/degradation_by_unit.provenance.json"
    AP = "20_degradation/agreement.provenance.json"
    AS = "20_degradation/agreement_summary.csv"
    AZ = "20_degradation/agreement_by_zone.csv"
    AI = "20_degradation/agreement_intervals.csv"
    AD = "20_degradation/agreement_definitions.csv"
    FF = "20_degradation/forest_floor_options.csv"
    N = "30_need/need.provenance.json"
    NB = "30_need/need_by_unit.csv"
    NC = "30_need/need_source_check.csv"
    NS = "30_need/need_construct_sensitivity.csv"
    A = "40_allocation/allocation.provenance.json"
    ADF = "40_allocation/assets_district_fy.csv"
    R = "40_allocation/state_fy_r620_vs_dump.csv"
    P = "40_allocation/panchayat_of_record_check.csv"
    L = "60_layer/layer.provenance.json"
    RN = SCRATCH + "/replicate_nirv/"
    EXC = "60_layer/exercise_chrome.json"
    EXW = "60_layer/exercise_webkit.json"
    EXS = "60_layer/exercise_safari.json"
    RUNS = "60_layer/decision_runs.json"                    # scripts/run_decision_checks.py: every run of every check on a build, and the checks it was told to leave out

    # ==== 1. what this is ================================================================================================================
    show("written_utc", V(written, "this run", "the UTC time at which this script ran"), txt)
    show("run_units", key(U, "run_utc"), txt)
    show("run_hansen", key(H, "run_utc"), txt)
    show("run_corestack", key(CSP, "run_utc"), txt)
    show("run_agreement", key(AP, "run_utc"), txt)
    show("run_need", key(N, "run_utc"), txt)
    show("run_allocation", key(A, "run_utc"), txt)
    show("run_layer", key(L, "run_utc"), txt)
    show("v_agreement", verifier("verify_agreement.py", a.draft), txt)
    show("v_layer", verifier("verify_layer.py", a.draft), txt)
    show("v_r620", verifier("verify_r620.py", a.draft), txt)
    hold(not [p for p in (ROOT / "50_gap").glob("*") if p.name != ".gitkeep"] if (ROOT / "50_gap").exists() else True, "stage 4 is not built: `50_gap/` holds no output")

    n_units = show("n_units", key(U, "counts/units"), n0)
    n_lgd = show("n_lgd", key(U, "counts/lgd_panchayat_polygons"), n0)
    n_out = show("n_out", key(U, "counts/outside_village_polygons"), n0)
    same("LGD panchayat units and outside-village units add up to the units", n_lgd.v + n_out.v, n_units.v)
    km2_all = show("km2_all", key(U, "counts/km2"), dec(0))
    km2_out = show("km2_out", key(U, "counts/km2_outside_any_revenue_village"), dec(0))
    calc("out_area_pct", 100 * km2_out.v / km2_all.v, dec(1), "outside-village km² ÷ km² of all units × 100", [km2_out, km2_all])

    def hl(col, level):
        return cell(HL, col, unit_level=level)

    out_forest = show("out_forest_pct", hl("share_of_all_forest_pct", "outside_village"), dec(1))
    out_loss = show("out_loss_pct", hl("share_of_all_loss_pct", "outside_village"), dec(1))
    for f, src in (("n_units", HL), ):
        same("units in the Hansen table and in the unit layer", hl("n_units", "all units").v, n_units.v)

    WIN = key(AP, "definitions/headline_window").v
    HP = key(AP, "definitions/headline_population").v
    FLOOR = float(key(AP, "definitions/floor/minimum_reference_ha").v)
    show("floor", key(AP, "definitions/floor/minimum_reference_ha"), n0)
    s_lo = show("floor_s1", key(AP, "definitions/floor/sensitivity_floors_ha/0"), n0)
    s_hi = show("floor_s2", key(AP, "definitions/floor/sensitivity_floors_ha/1"), n0)

    def ag(col, pop, units, floor=None, blank_ok=False):
        return cell(AS, col, blank_ok=blank_ok, population=pop, window=WIN, minimum_reference_ha=FLOOR if floor is None else float(floor), units=units)

    hold(int(ag("delivered", HP, "all units").v) == 1, "the headline rows of `agreement_summary.csv` are the ones marked delivered")
    h_n = show("h_n", ag("n_assessed", HP, "all units"), n0)
    h_both = show("h_both", ag("both", HP, "all units"), n0)
    show("h_exp", ag("both_expected_if_unrelated", HP, "all units"), dec(0))
    h_or = show("h_or", ag("odds_ratio", HP, "all units"), dec(2))
    h_lo = show("h_lo", ag("odds_ratio_lo95", HP, "all units"), dec(2))
    h_hi = show("h_hi", ag("odds_ratio_hi95", HP, "all units"), dec(2))

    DOC.append("""# Results: the state of the pipeline, and every headline number with its caveat

*Written {written_utc} by `scripts/write_results.py`. No figure in this document was typed. Each was read by that script
from the file named for it in the appendix (§13), and each conclusion drawn from figures was tested against them before
it was written. The figures change only when the files do.*

## 1. What this is, and where it stands

The project asks whether work under the rural employment guarantee (MGNREGA) in Odisha goes to the places where forest
is degrading, and to the people who depend on it. To ask that, three things have to be measured on the same pieces of
land: the condition of the forest (stage 1), social need (stage 2), and what the scheme spent (stage 3). Stage 0 builds
the pieces of land, the *units*. A fourth stage would set the three beside one another.

**That fourth stage is not built.** The project owner is respecifying it. So this document reports measurements and the
checks made on them. It holds no finding about whether spending follows need, and none should be read into it.

| stage | main output | state | how it was checked |
|---|---|---|---|
| units | `10_units/units.gpkg` | built, {run_units} | counts and areas recorded by the builder (§2) |
| forest: Hansen tree-cover loss | `20_degradation/hansen_by_unit.csv` | built, {run_hansen} | state totals held against Global Forest Watch's published figures; replicated independently (§3) |
| forest: CoRE Stack tree-change classes | `20_degradation/corestack_by_unit.csv` | built, {run_corestack} | reconciled to the one Odisha figure its producers print (§4) |
| forest: do the two agree | `20_degradation/agreement_summary.csv` and five tables beside it | built, {run_agreement} | arithmetic rebuilt by `scripts/verify_agreement.py`, which imports nothing from the builder: {v_agreement} (§5) |
| forest: NIRv greenness trend | columns of `20_degradation/degradation_by_unit.csv` | **blank: the run was stopped, and it is not a measure** | replicated independently and found unfit (§6) |
| need | `30_need/need_by_unit.csv` | built, {run_need} | census rows re-added to the published state totals (§7) |
| allocation | `40_allocation/allocation_by_unit.csv` | built, {run_allocation} | district-by-year sums equal a separate aggregation to the rupee; `scripts/verify_r620.py`: {v_r620} (§8) |
| the comparison of the three | `50_gap/` | **not built** | - |
| map layer for discussion | `60_layer/index.html`, `60_layer/data.js` | built, {run_layer} | `scripts/verify_layer.py`: {v_layer}; every control exercised in two browser engines, {safari_state} (§10) |

Three statements carry most of what follows.

- **Where the forest is, the planning data are not.** {out_area_pct} per cent of the land lies outside any revenue
  village. It holds {out_forest_pct} per cent of the forest and {out_loss_pct} per cent of the tree-cover loss, and the
  census has no row for it (§9).
- **Two measures of forest change, made independently, point weakly at the same units.** Among the {h_n} units with
  enough forest to compare, {h_both} are in the top fifth on both where two unrelated measures would share about
  {h_exp}: an odds ratio of {h_or} ({h_lo} to {h_hi}). For LGD panchayat units taken alone it is not established, and
  the agreement is about units, not hectares (§5).
- **A third measure failed, and that is a result.** A greenness trend from Landsat 8 was built, replicated, and found
  to move with the correction applied for the date of each image (§6).
""")

    # ==== 2. the unit ====================================================================================================================
    show("n_village_polygons", key(U, "counts/village_polygons"), n0)
    show("n_coded", key(U, "counts/polygons_with_census_2011_code"), n0)
    show("n_unmapped", key(U, "counts/villages_with_no_lgd_panchayat"), n0)
    show("km2_unmapped", key(U, "counts/villages_with_no_lgd_panchayat_km2"), dec(0))
    ids = show("n_ids", count(NC, "every row (one for each LGD panchayat id of the mapping)", lambda t: t.lgd_panchayat_id.notna()), n0)
    ids_poly = count(NC, "`has_unit_polygon` is 1", lambda t: t.has_unit_polygon == 1)
    same("LGD panchayat ids that have a polygon, and LGD panchayat units", ids_poly.v, n_lgd.v)
    nop = show("n_ids_no_polygon", key(N, "ids_with_no_unit_polygon/n"), n0)
    same("ids with no polygon, in the need record and in its check table", nop.v, ids.v - ids_poly.v)
    show("pop_ids_no_polygon", key(N, "ids_with_no_unit_polygon/population"), n0)
    por_all = show("por_all", cell(P, "share_in_modal_polygon", scope="all units"), pc(1))
    show("por_lgd", cell(P, "share_in_modal_polygon", scope="lgd_panchayat units only"), pc(1))
    show("por_cs", cell(P, "share_in_modal_polygon", scope="CoRE Stack panchayat polygons"), pc(1))
    d_name = show("d_by_name", key(D, "counts/assigned_by/label/units"), n0)
    d_moved = show("d_moved", key(D, "counts/assigned_by/two checks against the label/units"), n0)
    d_n1 = key(D, "counts/assigned_by/area majority: the polygon has no district name/units")
    d_n2 = key(D, "counts/assigned_by/neighbours: the polygon has no district name/units")
    calc("d_no_name", d_n1.v + d_n2.v, n0, "the two ways a polygon with no district name was assigned, added", [d_n1, d_n2])
    same("the four ways a district was assigned add up to the outside-village units", d_name.v + d_moved.v + d_n1.v + d_n2.v, n_out.v)
    d_nocheck = show("d_no_check", key(D, "counts/no_check_possible_neither_covered_nor_with_a_coded_neighbour/units"), n0)
    show("d_no_check_km2", key(D, "counts/no_check_possible_neither_covered_nor_with_a_coded_neighbour/km2"), dec(0))
    d_amb = show("d_ambiguous", key(D, "counts/ambiguous_the_one_flag/units"), n0)
    show("d_flagged", key(D, "counts/flagged_not_moved_one_check_contradicts_the_assigned_district/units"), n0)
    show("d_name_right_pct", key(D, "how_good_each_source_is_on_villages_whose_district_is_known/name_gives_it_pct"), dec(2))
    d_nm = key(D, "counts/area_majority/not_measurable/km2")
    calc("d_no_area_check_pct", 100 * d_nm.v / km2_out.v, dec(0), "outside-village km² where the area majority cannot be taken ÷ outside-village km² × 100", [d_nm, km2_out])
    for k, v in (("no_possible_check", d_nocheck), ("moved_off_the_polygons_name", d_moved), ("ambiguous", d_amb)):
        same(f"outside-village districts, {k}: the agreement record and the district record", key(AP, f"counts/outside_village_units_district/{k}").v, v.v)

    DOC.append("""
## 2. The unit: what it is, and what it is not

A unit is a polygon. There are {n_units}, of two kinds.

- **{n_lgd} LGD panchayat units.** Each is the set of village polygons that the Local Government Directory mapping
  assigns to one panchayat id, merged into one shape.
- **{n_out} outside-village units.** Each is a polygon of the village-boundary layer that carries no census code: land
  outside any revenue village. What that land is in law (reserved forest or otherwise) is not in the data used here.
  Each such block is a unit by itself.

Together they cover {km2_all} km², computed on the WGS84 ellipsoid; the outside-village units are {km2_out} km² of it,
{out_area_pct} per cent. They are built from the {n_village_polygons} village polygons of DataMeet's layer, {n_coded}
of which carry a Census 2011 code.

What a unit is **not**:

- **Not a gram panchayat.** The id runs over panchayat names within a sub-district, so a panchayat whose villages lie
  in two sub-districts is two units. The mapping holds {n_ids} ids; {n_ids_no_polygon} of them have no village polygon
  and so no unit ({pop_ids_no_polygon} people live in them). There are more units than Odisha has gram panchayats.
  The state's own count of gram panchayats, and the ratio, are quoted with their source in `docs/UNITS.md`; that count
  is in no file of this pipeline, so it is not repeated here. Anything stated "per panchayat" from these tables is per
  LGD panchayat unit.
- **Not the panchayat that recorded a work.** A work counts toward the unit its recorded location falls in. Only
  {por_all} per cent of works fall in the unit that holds most of the works of their own recorded panchayat
  ({por_lgd} per cent counting LGD panchayat units only). Against CoRE Stack's own panchayat polygons the figure is
  {por_cs} per cent, so this is a property of the recorded locations and not of this layer.
- **Not the whole state.** {n_unmapped} villages ({km2_unmapped} km²) have a census code but no row in the mapping, and
  belong to no unit. The layer's area is not validated against the state's official area and is not meant to be: the
  polygons never claimed to tile the state.
- **Not surveyed for district.** An outside-village unit has no census code and so no district of its own. One was
  assigned: the district named on its polygon for {d_by_name} units; another district for {d_moved}, where two
  independent checks contradicted the name and agreed with each other; and for the {d_no_name} whose polygon names no
  district, the district of the panchayat polygons or the coded villages round it. {d_no_check} units
  ({d_no_check_km2} km²) have a name and nothing to check it against. {d_ambiguous} are ambiguous: two districts within
  five points of each other by the unit's own area. {d_flagged} more are flagged and not moved, because one check
  contradicts the district they carry. On villages whose district is known, the polygon's name is right
  {d_name_right_pct} per cent of the time; but for {d_no_area_check_pct} per cent of the outside-village land no check
  by area is possible, and that is where the forest is.
""")

    # ==== 3. Hansen ======================================================================================================================
    levels = (("outside-village units", "outside_village"), ("LGD panchayat units", "lgd_panchayat"), ("all units", "all units"))
    table("T_hansen", ["", "units", "area on the pixel grid, km²", "forest, km²", "forest, % of area", "share of all forest, %", "loss, km²", "share of all loss, %", "loss, % of forest"],
          [[lab, c(hl("n_units", k), n0), c(hl("area_km2", k), dec(0)), c(hl("forest_km2", k), dec(0)), c(hl("forest_share_of_area_pct", k), dec(1)), c(hl("share_of_all_forest_pct", k), dec(1)),
            c(hl("loss_km2_2001_2025", k), dec(0)), c(hl("share_of_all_loss_pct", k), dec(1)), c(hl("loss_share_of_forest_pct", k), dec(2))] for lab, k in levels])
    show("no_forest", hl("units_with_no_forest", "all units"), n0)
    under1 = show("under1", hl("units_with_under_1_ha_of_forest_including_none", "all units"), n0)
    u1 = calc("under1_pct", 100 * under1.v / n_units.v, dec(1), "units with under a hectare of forest ÷ all units × 100", [under1, n_units])
    hold(u1.v > 50, "more than half the units have under a hectare of forest")
    show("gfw_extent", key(H, "checks_passed/tree_cover_2000_gt_T_against_global_forest_watch_gated/30"), spc(2))
    show("gfw_loss", key(H, "checks_passed/loss_2001_2020_gt_30_against_global_forest_watch_gated"), spc(2))
    show("gfw_tol_extent", key(H, "checks_passed/tolerances/gfw_extent"), pc(0))
    show("gfw_tol_loss", key(H, "checks_passed/tolerances/gfw_loss_2001_2020"), pc(0))

    def bd(col, band, units="all units"):
        return cell(BAND, col, units=units, canopy_band=band)

    bands = (("`treecover2000 > 30`: the forest mask", "gt30"), ("`10 < treecover2000 <= 30`", "gt10le30"), ("`treecover2000 <= 10`", "le10"),
             ("of which `treecover2000 = 0`", "eq0"), ("all land", "any_cover"))
    table("T_bands", ["canopy in the year 2000", "land, km²", "loss, km²", "% of all recorded loss", "loss, % of the band's land", "loss in the first period", "in the second", "in the third"],
          [[lab, c(bd("land_km2", k), dec(0)), c(bd("loss_km2_2001_2025", k), dec(0)), c(bd("share_of_these_units_loss_pct", k), dec(1)), c(bd("loss_pct_of_band_land", k), dec(2)),
            c(bd("loss_km2_2001_2010", k), dec(0)), c(bd("loss_km2_2011_2017", k), dec(0)), c(bd("loss_km2_2018_2025", k), dec(0))] for lab, k in bands])
    om = show("outside_mask_pct", key(H, "checks_passed/loss_outside_the_mask_share"), pc(1))
    same("loss outside the mask, in the Hansen record and in the band table", 100 * om.v, 100 - bd("share_of_these_units_loss_pct", "gt30").v, 0.02)
    same("loss in the mask, in the band table and in the table by unit type", bd("loss_km2_2001_2025", "gt30").v, hl("loss_km2_2001_2025", "all units").v, 0.01)
    l_mid, l_low = bd("loss_km2_2001_2025", "gt10le30"), bd("loss_km2_2001_2025", "le10")
    calc("loss_out_mask", l_mid.v + l_low.v, dec(0), "loss in the two bands below the mask, added", [l_mid, l_low])
    show("loss_any", bd("loss_km2_2001_2025", "any_cover"), dec(0))
    l_eq0 = show("loss_eq0", bd("loss_km2_2001_2025", "eq0"), dec(0))
    calc("eq0_share", 100 * l_eq0.v / l_low.v, dec(0), "loss on land with no canopy in 2000 ÷ loss on the lowest band × 100", [l_eq0, l_low])
    show("units_loss_none_in_mask", hl("units_with_loss_but_none_in_the_mask", "all units"), n0)
    lp = [show(f"low_p{i}", bd(col, "le10"), dec(0)) for i, col in ((1, "loss_km2_2001_2010"), (2, "loss_km2_2011_2017"), (3, "loss_km2_2018_2025"))]
    mp = [show(f"m_p{i}", bd(col, "gt30"), dec(0)) for i, col in ((1, "loss_km2_2001_2010"), (2, "loss_km2_2011_2017"), (3, "loss_km2_2018_2025"))]
    hold(lp[2].v / lp[0].v > 5 * mp[2].v / mp[0].v, "loss on the lowest canopy band rises several times faster across the three periods than loss in the mask")
    show("mid_land", bd("land_km2", "gt10le30"), dec(0))
    show("mid_loss_pct", bd("loss_pct_of_band_land", "gt10le30"), dec(1))

    DOC.append("""
## 3. Forest, first measure: Hansen tree-cover loss

**What it is.** The Global Forest Change dataset of Hansen and others gives, for every Landsat pixel, the canopy cover
in the year 2000 and the year, if any, in which that cover was removed. *Forest* here is a pixel with more than thirty
per cent canopy in 2000 (`treecover2000 > 30`, strictly above); *loss* is the area of such pixels removed in
2001–2025. All {n_units} units are measured.

{T_hansen}

- **More than half the units have almost no forest.** {no_forest} have none, and {under1} ({under1_pct} per cent) have
  under a hectare. A loss *rate* on so little forest is noise, which is why the comparisons below are made only above a
  minimum area (§5.3).
- **Its totals are held against a published source.** Summed over the units, forest in 2000 is {gfw_extent} per cent,
  and loss in 2001–2020 {gfw_loss} per cent, away from the figures Global Forest Watch publishes for Odisha on its own
  outline of the state. The build stops beyond {gfw_tol_extent} and {gfw_tol_loss} per cent. Exact equality is not
  expected: the outlines differ.

**What it cannot see.** Loss is the outright removal of tree cover from any cause, in plantation and natural forest
alike. It is not deforestation; it does not see a forest thinning under a standing canopy; and gain is not netted off.
The producers changed their method from 2011, so a step at that year is partly the method.

### 3.1 The canopy-band finding: what the forest mask leaves out

The mask is a choice, and it is fixed at the year 2000. Every pixel is in exactly one band of year-2000 canopy; the
three periods are 2001–2010, 2011–2017 and 2018–2025.

{T_bands}

- **{outside_mask_pct} per cent of the loss Hansen records inside the units is outside the mask**: {loss_out_mask} of
  {loss_any} km² lie on land that had thirty per cent canopy or less in 2000, and so are not in the loss figure above.
  {units_loss_none_in_mask} units have recorded loss and none of it in the mask.
- **Most of that is not forest that stood in 2000.** {loss_eq0} km², {eq0_share} per cent of the lowest band's loss, is
  on pixels with no canopy at all in 2000: tree cover that grew after 2000 and was then removed, or an artefact of
  detection.
- **Its rise over time is largely the method.** Loss on the lowest band goes {low_p1}, {low_p2}, {low_p3} km² across the
  three periods while loss in the mask goes {m_p1}, {m_p2}, {m_p3}. It should not be read as a trend on the ground.
- **The band that bears on open forest is the middle one**: {mid_land} km² of land, {mid_loss_pct} per cent of it lost.

So the mask hides a large area of recorded loss, but Hansen cannot say that this area is degraded forest. Whether
forest that was already open is getting worse needs a measure of condition. That is the reason for the second measure.
""")

    # ==== 4. CoRE Stack ==================================================================================================================
    def cs(col, units, land):
        return cell(CL, col, units=units, land=land)

    cs_rows = (("all units, all land inside the producers' tree mask", "all units", "all land"), ("all units, land with `treecover2000 > 10`", "all units", "treecover2000 > 10"),
               ("outside-village units, the same land", "outside_village", "treecover2000 > 10"), ("LGD panchayat units, the same land", "lgd_panchayat", "treecover2000 > 10"),
               ("all units, Eastern Plateau and Hills model, all land", "all units", "zone EPAHR, all land"), ("all units, East Coast Plains and Hills model, all land", "all units", "zone ECPHR, all land"))
    table("T_corestack", ["", "tree cover at the start, km²", "degradation, km²", "improvement, km²", "degradation less improvement, km²", "downward share (interval)"],
          [[lab, c(cs("tree_cover_start_km2", u, l), dec(0)), c(cs("degradation_km2", u, l), dec(0)), c(cs("improvement_km2", u, l), dec(0)), c(cs("net_degradation_km2", u, l), dec(0)),
            span(cs("downward_share", u, l), cs("downward_share_lo_95", u, l), cs("downward_share_hi_95", u, l))] for lab, u, l in cs_rows])
    cs_tree = show("cs_tree_all", cs("tree_cover_start_km2", "all units", "all land"), dec(0))
    cs_land = cs("land_km2", "all units", "all land")
    calc("cs_tree_pct", 100 * cs_tree.v / cs_land.v, dec(0), "tree cover at the start ÷ the units' land on the product's grid × 100", [cs_tree, cs_land])
    show("deg_pct_gt10", cs("degradation_pct_of_tree_cover_start", "all units", "treecover2000 > 10"), dec(0))
    show("imp_pct_gt10", cs("improvement_pct_of_tree_cover_start", "all units", "treecover2000 > 10"), dec(0))
    d_ep = show("down_ep", cs("downward_share", "all units", "zone EPAHR, all land"), dec(2))
    d_ec = show("down_ec", cs("downward_share", "all units", "zone ECPHR, all land"), dec(2))
    hold(d_ec.v > d_ep.v and cs("downward_share_lo_95", "all units", "zone ECPHR, all land").v > cs("downward_share_hi_95", "all units", "zone EPAHR, all land").v,
         "the East Coast model's downward share is above the Eastern Plateau model's, and their intervals do not overlap")
    deg_out, deg_all = cs("degradation_km2", "outside_village", "all land"), cs("degradation_km2", "all units", "all land")
    half = calc("cs_out_deg_pct", 100 * deg_out.v / deg_all.v, dec(0), "degradation class in outside-village units ÷ in all units × 100, all land", [deg_out, deg_all])
    hold(45 <= half.v <= 55, "about half of the degradation class is in outside-village units")
    may = lambda col: V(C(CR).loc[C(CR).quantity.str.startswith("class -1, Mayurbhanj"), col].iloc[0].item(), CR, f"column `{col}`", "`quantity` begins 'class -1, Mayurbhanj'")
    hold(int(C(CR).quantity.str.startswith("class -1, Mayurbhanj").sum()) == 1, "the reconciliation table has one row for Mayurbhanj")
    show("may_ours", may("this_pipeline"), dec(1))
    show("may_theirs", may("published"), dec(0))
    show("may_tol", key(CSP, "checks_passed/mayurbhanj_2017_2021_against_the_producers_paper/tolerance"), pc(0))

    DOC.append("""
## 4. Forest, second measure: CoRE Stack tree-change classes

**What it is.** A raster made by the CoRE Stack group at IIT Delhi. It puts each pixel inside its own tree mask into a
class by whether canopy density or tree height moved between two three-year periods, roughly 2016–2019 and 2022–2025.
The product is named for 2017–2023 and exists for that span only. The classes used here are *degradation* (density or
height went from High to Low), *improvement* (the reverse), *lost* and *gained* (tree cover gone, or new), and
*partially degraded*. In the tables' own labels these are class `-1`, class `1`, class `-2`, class `2`, and classes `3`
and `4`.

Three properties decide how far it can be trusted. All three are from the producers' own paper and code;
`docs/DEGRADATION.md` §4a gives the sources.

- **"Degradation" is the crossing of a line, not a measured loss.** A stand that thins without crossing its zone's
  threshold is "no change", and a stand already Low cannot register degradation at all.
- **The classifiers behind it were right about two times in three** on held-out data, and the producers validated only
  the *lost* class.
- **Its "tree cover" is far wider than forest**: {cs_tree_all} km², {cs_tree_pct} per cent of the units' area, taking
  in orchards and trees on farms.

{T_corestack}

- **Read the downward share, never the degradation class alone.** The downward share is degradation over degradation
  plus improvement; one half means no net signal. Improvement is the noise reference for degradation: on land with
  `treecover2000 > 10` the product puts {deg_pct_gt10} per cent of the tree cover in the degradation class and
  {imp_pct_gt10} per cent in improvement, which is more change in six years than a forest undergoes and about what such
  classifiers produce by error.
- **It differs by zone model.** The state is covered by two separately trained models with different thresholds. Their
  downward shares are {down_ep} (Eastern Plateau and Hills) and {down_ec} (East Coast Plains and Hills). Part of that
  difference is the models and not the land. This is the origin of the caveat on the agreement result (§5.2).
- **About half of the degradation class, {cs_out_deg_pct} per cent, is in outside-village units.**
- **Its totals can be held against one published figure only.** The producers print one figure for Odisha: degradation
  in Mayurbhanj district in their earlier product for 2017–2021. Reading that product the way this pipeline reads the
  2017–2023 one gives {may_ours} thousand hectares against their {may_theirs}; the build stops beyond {may_tol} per
  cent. No total exists for 2017–2023 or for the state, so the 2017–2023 tallies themselves are unreconciled.
""")

    # ==== 5. agreement ===================================================================================================================
    pops = (("**Headline: East Coast units left out**", HP), ("Every unit kept", "all_assessed"), ("Eastern Plateau model only", "eastern_plateau_only"))
    utypes = (("all units", "all units"), ("LGD panchayat units", "lgd_panchayat"), ("outside-village units", "outside_village"))
    table("T_agree", ["version", "units", "units compared", "in the top fifth on both", "expected if unrelated", "odds ratio (interval)", "odds ratio within districts (interval)"],
          [[plab, ulab, c(ag("n_assessed", p, u), n0), c(ag("both", p, u), n0), c(ag("both_expected_if_unrelated", p, u), dec(0)),
            span(ag("odds_ratio", p, u), ag("odds_ratio_lo95", p, u), ag("odds_ratio_hi95", p, u)),
            span(ag("odds_ratio_within_districts", p, u), ag("odds_ratio_within_districts_lo95", p, u), ag("odds_ratio_within_districts_hi95", p, u))] for plab, p in pops for ulab, u in utypes])
    show("e_or", ag("odds_ratio", "eastern_plateau_only", "all units"), dec(2))
    e_lo = show("e_lo", ag("odds_ratio_lo95", "eastern_plateau_only", "all units"), dec(2))
    show("e_hi", ag("odds_ratio_hi95", "eastern_plateau_only", "all units"), dec(2))
    hold(e_lo.v > 1, "with the straddling units left out as well, the interval for all units still lies above one")
    excl = show("h_excluded", ag("n_excluded_by_zone_model", HP, "all units"), n0)
    insuf = show("h_insufficient", ag("n_insufficient_forest", HP, "all units"), n0)
    same("units compared, left out by zone model and with too little forest add up to the units", h_n.v + excl.v + insuf.v, n_units.v)
    same("units compared in the headline, in the summary table and in the agreement record", h_n.v, key(AP, "counts/in_the_headline_population").v)
    a_n = show("a_n", ag("n_assessed", "all_assessed", "all units"), n0)
    same("every unit kept: units compared are the headline's plus those left out", a_n.v, h_n.v + excl.v)
    show("a_both", ag("both", "all_assessed", "all units"), n0)
    show("a_exp", ag("both_expected_if_unrelated", "all_assessed", "all units"), dec(0))
    a_or = show("a_or", ag("odds_ratio", "all_assessed", "all units"), dec(2))
    a_lo = show("a_lo", ag("odds_ratio_lo95", "all_assessed", "all units"), dec(2))
    show("a_hi", ag("odds_ratio_hi95", "all_assessed", "all units"), dec(2))
    show("hl_or", ag("odds_ratio", HP, "lgd_panchayat"), dec(2))
    hl_lo = show("hl_lo", ag("odds_ratio_lo95", HP, "lgd_panchayat"), dec(2))
    hl_hi = show("hl_hi", ag("odds_ratio_hi95", HP, "lgd_panchayat"), dec(2))
    show("al_or", ag("odds_ratio", "all_assessed", "lgd_panchayat"), dec(2))
    al_lo = show("al_lo", ag("odds_ratio_lo95", "all_assessed", "lgd_panchayat"), dec(2))
    show("al_hi", ag("odds_ratio_hi95", "all_assessed", "lgd_panchayat"), dec(2))
    show("hlw_or", ag("odds_ratio_within_districts", HP, "lgd_panchayat"), dec(2))
    hlw_lo = show("hlw_lo", ag("odds_ratio_within_districts_lo95", HP, "lgd_panchayat"), dec(2))
    show("hlw_hi", ag("odds_ratio_within_districts_hi95", HP, "lgd_panchayat"), dec(2))
    ho_n = show("ho_n", ag("n_assessed", HP, "outside_village"), n0)
    show("ho_or", ag("odds_ratio", HP, "outside_village"), dec(2))
    ho_lo = show("ho_lo", ag("odds_ratio_lo95", HP, "outside_village"), dec(2))
    show("ho_hi", ag("odds_ratio_hi95", HP, "outside_village"), dec(2))
    h_fh = show("h_flag_h", ag("flagged_by_hansen", HP, "all units"), n0)
    hold(h_lo.v > 1 and a_lo.v > 1, "for all units the interval of the odds ratio lies above one in both versions")
    hold(h_or.v < a_or.v, "the headline odds ratio is the smaller of the two")
    hold(hl_lo.v < 1 < hl_hi.v, "for LGD panchayat units alone the headline interval includes one")
    hold(al_lo.v > 1, "for LGD panchayat units alone, with every unit kept, the interval lies above one")
    hold(hlw_lo.v > 1, "for LGD panchayat units alone, within districts, the headline interval lies above one")
    hold(ho_lo.v > 1, "for outside-village units alone the headline interval lies above one")
    hold(h_both.v < h_fh.v / 2, "fewer than half the units Hansen flags in the headline comparison are flagged by CoRE Stack too")

    def az(col, zone):
        return cell(AZ, col, zone_model_of_the_units_valued_land=zone)

    SPD, SPI = "spearman_hansen_vs_corestack_degradation", "spearman_hansen_vs_corestack_improvement"
    zones = (("Eastern Plateau and Hills model only", "EPAHR only"), ("East Coast Plains and Hills model only", "ECPHR only"), ("land under both models", "both models"))
    table("T_zone", ["units whose valued land is under", "units compared", "districts", "% of the compared land", "odds ratio, degradation", "rank correlation of Hansen's rate with degradation (interval)",
                     "with improvement, the placebo (interval, districts resampled)", "the same interval, units resampled singly"],
          [[lab, c(az("n_assessed", z), n0), c(az("n_districts", z), n0), c(az("reference_land_pct_of_assessed", z), dec(1)), c(az("odds_ratio_degradation", z), dec(2)),
            span(az(SPD, z), az(SPD + "_lo95", z), az(SPD + "_hi95", z)), span(az(SPI, z), az(SPI + "_lo95", z), az(SPI + "_hi95", z)),
            (f"{dec(2)(az(SPI + '_lo95_units_singly', z).v)} to {dec(2)(az(SPI + '_hi95_units_singly', z).v)}", [az(SPI + "_lo95_units_singly", z), az(SPI + "_hi95_units_singly", z)])] for lab, z in zones])
    hold(az("flags_are", "ECPHR only").v == "those of all assessed units" and float(az("minimum_reference_ha", "ECPHR only").v) == FLOOR and az("window", "ECPHR only").v == WIN,
         "the table by zone model is at the ruled floor, in the headline window, with the flags of all assessed units")
    ec_n = show("ec_n", az("n_assessed", "ECPHR only"), n0)
    same("units under the East Coast model only, in the zone table and left out of the headline", ec_n.v, excl.v)
    show("ec_d", az("n_districts", "ECPHR only"), n0)
    ec_or = show("ec_or", az("odds_ratio_degradation", "ECPHR only"), dec(2))
    ep_deg = show("ep_deg", az(SPD, "EPAHR only"), dec(2))
    ep_imp = show("ep_imp", az(SPI, "EPAHR only"), dec(2))
    show("ec_deg", az(SPD, "ECPHR only"), dec(2))
    ec_imp = show("ec_imp", az(SPI, "ECPHR only"), dec(2))
    ec_dl = show("ec_deg_lo", az(SPD + "_lo95", "ECPHR only"), dec(2))
    show("ec_deg_hi", az(SPD + "_hi95", "ECPHR only"), dec(2))
    hold(ec_dl.v < 0, "the East Coast correlation with degradation also has an interval that reaches zero when whole districts are resampled")
    ec_il = show("ec_imp_lo", az(SPI + "_lo95", "ECPHR only"), dec(2))
    show("ec_imp_hi", az(SPI + "_hi95", "ECPHR only"), dec(2))
    ec_ils = show("ec_imp_lo_s", az(SPI + "_lo95_units_singly", "ECPHR only"), dec(2))
    show("ec_imp_hi_s", az(SPI + "_hi95_units_singly", "ECPHR only"), dec(2))
    show("both_n", az("n_assessed", "both models"), n0)
    hold(az(SPI + "_lo95", "EPAHR only").v < 0 < az(SPD + "_lo95", "EPAHR only").v, "under the Eastern Plateau model Hansen's rate is related to degradation and not to improvement")
    hold(ec_imp.v > 3 * abs(ep_imp.v) and ec_imp.v > 0.2, "under the East Coast model Hansen's rate goes with improvement, several times more strongly than under the other model")
    hold(ec_or.v > az("odds_ratio_degradation", "EPAHR only").v and ec_or.v > a_or.v, "the units under the East Coast model are where the two measures agree most")
    hold(ec_il.v < 0 < ec_ils.v, "the East Coast placebo's interval reaches zero when whole districts are resampled, and excludes it when units are resampled singly")

    floors = (s_lo.v, s_hi.v, FLOOR)
    table("T_floor", ["minimum land, ha", "units compared, headline", "odds ratio, headline (interval)", "units compared, every unit kept", "odds ratio, every unit kept (interval)",
                      "smallest class of units admitted, ha", "its repeatability, loss of all years", "its repeatability, loss of the headline window"],
          [[c(ag("minimum_reference_ha", HP, "all units", f), n0), c(ag("n_assessed", HP, "all units", f), n0), span(ag("odds_ratio", HP, "all units", f), ag("odds_ratio_lo95", HP, "all units", f), ag("odds_ratio_hi95", HP, "all units", f)),
            c(ag("n_assessed", "all_assessed", "all units", f), n0), span(ag("odds_ratio", "all_assessed", "all units", f), ag("odds_ratio_lo95", "all_assessed", "all units", f), ag("odds_ratio_hi95", "all_assessed", "all units", f)),
            c(ag("lowest_land_class_admitted_ha", HP, "all units", f), txt), c(ag("repeatability_of_that_class_2001_2025", HP, "all units", f), dec(2)), c(ag("repeatability_of_that_class_2017_2023", HP, "all units", f), dec(2))]
           for f in floors])
    reps = [ag("repeatability_of_that_class_2001_2025", HP, "all units", f) for f in floors]
    ors = [ag("odds_ratio", HP, "all units", f) for f in floors]
    show("rep_s2", reps[1], dec(2))
    show("rep_floor", reps[2], dec(2))
    show("or_s1", ors[0], dec(2))
    show("or_s2", ors[1], dec(2))
    hold(reps[0].v < reps[1].v < reps[2].v, "the repeatability of the smallest units admitted rises with the floor")
    hold(ors[0].v > ors[1].v > ors[2].v, "the stricter the floor, the smaller the odds ratio")
    hold(str(key("20_degradation/forest_floor.provenance.json", "ruled_ha").v) == str(FLOOR), "the floor in the agreement record is the floor the floor table calls ruled")
    ffk = show("ff_kept", cell(FF, "units_kept", floor_ha=FLOOR), n0)
    show("ff_forest", cell(FF, "forest_kept_pct", floor_ha=FLOOR), dec(1))
    show("ff_loss", cell(FF, "loss_kept_pct", floor_ha=FLOOR), dec(1))
    below = calc("ff_below", n_units.v - ffk.v, n0, "all units less the units with at least the floor of forest", [n_units, ffk])
    same("units under the floor of forest, here and in the layer's own count", below.v, key(L, "checks_passed/class_counts_equal_the_stage_tables_own/units_under_100_ha_of_forest").v if FLOOR == 100 else below.v)

    def ai(col, units, stat="odds_ratio", blank_ok=False):
        return cell(AI, col, blank_ok=blank_ok, population=HP, window=WIN, minimum_reference_ha=FLOOR, units=units, statistic=stat)

    cl_rows = [(lab + ", odds ratio", u, "odds_ratio") for lab, u in utypes] + [("all units, odds ratio within districts", "all units", "odds_ratio_within_districts_mantel_haenszel"),
                                                                             ("all units, rank correlation with degradation", "all units", SPD)]
    table("T_cluster", ["", "estimate", "primary: whole districts", "LGD units by district, outside-village units singly", "every unit singly", "width of the first over the second"],
          [[lab, c(ai("estimate", u, s), dec(2)), (f"{dec(2)(ai('lo95_districts', u, s).v)} to {dec(2)(ai('hi95_districts', u, s).v)}", [ai("lo95_districts", u, s), ai("hi95_districts", u, s)]),
            ("-" if ai("lo95_lgd_districts_outside_singly", u, s, True).v is None else f"{dec(2)(ai('lo95_lgd_districts_outside_singly', u, s).v)} to {dec(2)(ai('hi95_lgd_districts_outside_singly', u, s).v)}",
             [ai("lo95_lgd_districts_outside_singly", u, s, True), ai("hi95_lgd_districts_outside_singly", u, s, True)]),
            ("-" if ai("lo95_units_singly", u, s, True).v is None else f"{dec(2)(ai('lo95_units_singly', u, s).v)} to {dec(2)(ai('hi95_units_singly', u, s).v)}", [ai("lo95_units_singly", u, s, True), ai("hi95_units_singly", u, s, True)]),
            c(ai("width_districts_over_lgd_only_design", u, s, True), dec(2))] for lab, u, s in cl_rows])
    same("the primary interval of the headline odds ratio, in the summary table and in the table of intervals", ai("lo95_districts", "all units").v, h_lo.v, 1e-9)
    show("ci_l_lo", ai("lo95_lgd_districts_outside_singly", "all units"), dec(2))
    ci_l_lo = ai("lo95_lgd_districts_outside_singly", "all units")
    show("ci_l_hi", ai("hi95_lgd_districts_outside_singly", "all units"), dec(2))
    ci_s_lo = show("ci_s_lo", ai("lo95_units_singly", "all units"), dec(2))
    ci_s_hi = show("ci_s_hi", ai("hi95_units_singly", "all units"), dec(2))
    w_dl = show("w_dl", ai("width_districts_over_lgd_only_design", "all units"), dec(2))
    w_ds = show("w_ds", ai("width_districts_over_units_singly", "all units"), dec(1))
    hold(0.8 <= w_dl.v <= 1.25 and ci_l_lo.v > 1, "for all units the two clusterings give intervals of nearly the same width, and both lie above one")
    hold(w_ds.v > 1.5 and ci_s_hi.v - ci_s_lo.v < h_hi.v - h_lo.v, "resampling units singly gives a much narrower interval than resampling districts")
    ho_s_lo = show("ho_s_lo", ai("lo95_units_singly", "outside_village"), dec(2))
    show("ho_s_hi", ai("hi95_units_singly", "outside_village"), dec(2))
    ho_ws = show("ho_ws", ai("width_districts_over_units_singly", "outside_village"), dec(2))
    hold(ho_ws.v >= 1.2 and ho_s_lo.v > 1, "for outside-village units alone the district interval is materially wider than the one from resampling units singly, and both lie above one")
    hl_s_lo = show("hl_s_lo", ai("lo95_units_singly", "lgd_panchayat"), dec(2))
    show("hl_s_hi", ai("hi95_units_singly", "lgd_panchayat"), dec(2))
    hold(hl_s_lo.v > 1, "for LGD panchayat units alone, resampling units singly gives an interval above one where resampling districts does not")
    show("ai_nocheck", ai("outside_village_assessed_district_has_no_possible_check", "all units"), n0)
    show("ai_moved", ai("outside_village_assessed_moved_off_the_polygons_name", "all units"), n0)
    show("ai_amb", ai("outside_village_assessed_ambiguous", "all units"), n0)
    show("ai_contra", ai("outside_village_assessed_one_check_contradicts_the_district", "all units"), n0)
    same("outside-village units compared, in the table of intervals and in the summary", ai("n_outside_village", "all units").v, ho_n.v)

    t = C(AD)
    dsel = t[(t.population == HP) & (t.window == WIN) & (t.minimum_reference_ha == FLOOR) & (t.units == "all units")]
    hold(len(dsel) >= 3 and dsel.corestack_flag_is.is_unique, "the table of definitions has one row for each CoRE Stack reading of the headline comparison")

    def ad(col, flag):
        return cell(AD, col, population=HP, window=WIN, minimum_reference_ha=FLOOR, units="all units", corestack_flag_is=flag)

    table("T_defs", ["the CoRE Stack flag is the top fifth on", "in the top fifth on both", "expected if unrelated", "odds ratio (interval)"],
          [[c(ad("corestack_flag_is", f), txt), c(ad("both", f), n0), c(ad("both_expected_if_unrelated", f), dec(0)), span(ad("odds_ratio", f), ad("odds_ratio_lo95", f), ad("odds_ratio_hi95", f))] for f in dsel.corestack_flag_is])

    lost, net, plc = "class -2, tree cover lost", "class -1 minus class 1", "class 1, improvement (the placebo)"
    lost_or = show("lost_or", ad("odds_ratio", lost), dec(2))
    show("lost_lo", ad("odds_ratio_lo95", lost), dec(2))
    show("lost_hi", ad("odds_ratio_hi95", lost), dec(2))
    net_or = show("net_or", ad("odds_ratio", net), dec(2))
    net_lo = show("net_lo", ad("odds_ratio_lo95", net), dec(2))
    net_hi = show("net_hi", ad("odds_ratio_hi95", net), dec(2))
    pl_or = show("pl_or", ad("odds_ratio", plc), dec(2))
    pl_lo = show("pl_lo", ad("odds_ratio_lo95", plc), dec(2))
    show("pl_hi", ad("odds_ratio_hi95", plc), dec(2))
    others = dsel[dsel.corestack_flag_is != plc]
    hold(lost_or.v == others.odds_ratio.max() and net_or.v == others.odds_ratio.min(), "of the readings other than the placebo, the lost class gives the largest odds ratio and degradation net of improvement the smallest")
    hold(net_lo.v < 1 < net_hi.v, "for degradation net of improvement the interval includes one")
    lost_km2 = show("lost_km2_gt10", cs("loss_km2", "all units", "treecover2000 > 10"), dec(0))
    deg_km2 = show("deg_km2_gt10", cs("degradation_km2", "all units", "treecover2000 > 10"), dec(0))
    hold(lost_km2.v < 0.05 * deg_km2.v, "on the compared land the lost class is a small fraction of the degradation class")
    hold(pl_or.v < 1 and pl_lo.v < 1, "in the headline population the improvement flag coincides with Hansen's no more often than chance")

    DOC.append("""
## 5. Do the two measures agree?

The two were made independently, by different groups with different methods, and they do not measure the same thing:
one dates the removal of canopy, the other classes a change in its density or height. If both point at the same places,
each is some evidence for the other.

**The test.** Take the land with more than ten per cent canopy in 2000 (`treecover2000 > 10`), so that both sources are
read on the same land. For each unit with at least {floor} ha of it on both sources' grids, take Hansen's loss rate for 2017–2023 and the share
of the land CoRE Stack puts in its degradation class. Flag a unit on each measure if it is in the top fifth of the units
compared. The *odds ratio* says how much more often the two flags fall on the same unit than they would if the measures
were unrelated; one means no relation. Every interval is the central ninety-five per cent of the estimate recomputed on
resampled data, and unless it says otherwise whole districts were resampled (§5.4). {h_insufficient} units have too
little such land to be compared at all.

### 5.1 The result, two ways, side by side

{T_agree}

The third block also leaves out the {both_n} units whose land straddles the two zone models. It is printed to show that
the headline does not turn on them: for all units it gives {e_or} ({e_lo} to {e_hi}).

### 5.2 Which is the headline, and why

**The headline is the first block: the {h_excluded} units whose land lies wholly under CoRE Stack's East Coast zone
model are left out.**

The reason is a test that was written into the build before any magnitude was looked at. CoRE Stack's improvement class
is the check on its degradation class. Hansen's loss is clearance: it should go with degradation, and it should not go
with improvement. That check, the *placebo*, holds under one zone model and fails under the other.

{T_zone}

- Under the Eastern Plateau model, Hansen's rate is related to degradation ({ep_deg}) and not to improvement
  ({ep_imp}, with an interval that includes zero).
- Under the East Coast model it goes with both: {ec_deg} with degradation and {ec_imp} with improvement. Where loss
  goes with improvement as well, its going with degradation cannot be read as agreement about degradation. Something
  else, the zone's model or how much tree cover a unit has, is moving all three.
- Those {ec_n} units are also where the two measures agree most (an odds ratio of {ec_or}), so leaving them out
  *lowers* the result. The headline is the weaker version. It is the headline because its own test passes, not because
  it survives.
- The {both_n} units whose land straddles the two models stay in.

**What the exclusion changes.**

- **For all units together the conclusion stands, weakened.** With every unit kept, {a_both} of {a_n} units are in the
  top fifth on both where about {a_exp} would be expected: an odds ratio of {a_or} ({a_lo} to {a_hi}). In the headline
  it is {h_both} of {h_n} against about {h_exp}: {h_or} ({h_lo} to {h_hi}). Both intervals lie above one.
- **For LGD panchayat units alone it changes the answer.** With every unit kept their odds ratio is {al_or} ({al_lo} to
  {al_hi}). In the headline it is {hl_or} ({hl_lo} to {hl_hi}), an interval that includes one. So across the state,
  agreement among LGD panchayat units is **not established** once the East Coast units are out. Within districts it
  is: comparing units only with others of their own district gives {hlw_or} ({hlw_lo} to {hlw_hi}).
- **For outside-village units alone it stands**: {ho_or} ({ho_lo} to {ho_hi}).

**A caveat on the caveat.** The East Coast figures rest on {ec_d} districts. When whole districts are resampled, neither
of its two correlations is firmly established: the interval is {ec_deg_lo} to {ec_deg_hi} for degradation and
{ec_imp_lo} to {ec_imp_hi} for improvement, and both reach zero. The improvement correlation excludes zero only when
units are resampled one at a time ({ec_imp_lo_s} to {ec_imp_hi_s}). So the failure of the placebo is a strong pattern
in few districts, and not an established fact. That is a reason to print both versions, as here. It is not a reason to
prefer the larger one.

### 5.3 The floor: {floor} ha

Ruled by the project owner on 7 October 2026; it supersedes the {floor_s2} ha that the pipeline's own rule had proposed.
A unit's loss rate is worth comparing only if it is repeatable. The test of that is the rank correlation, across units
of one size class, between a unit's loss rate in odd years and its loss rate in even years.

{T_floor}

- At {floor_s2} ha the smallest units admitted have a repeatability of {rep_s2}; at {floor} ha, {rep_floor}.
- **The stricter the floor, the weaker the agreement**: the headline odds ratio is {or_s1} at {floor_s1} ha, {or_s2} at
  {floor_s2} ha and {h_or} at {floor} ha. The {floor_s2} ha row is a sensitivity reading and should be quoted only with
  its repeatability beside it.
- On the forest mask proper (`treecover2000 > 30`), {ff_kept} units have at least {floor} ha. They hold {ff_forest} per
  cent of the forest and {ff_loss} per cent of the loss. {ff_below} units fall below it.

### 5.4 The intervals: two ways of clustering

Units of one district share forest type, terrain, forest administration and satellite scenes, so treating them as
independent overstates certainty. The primary interval therefore resamples whole districts, every unit in its district,
which for an outside-village unit is an *assigned* district (§2). Two other designs are printed beside it for the
headline comparison: whole districts for the LGD panchayat units with the outside-village units resampled one at a
time, and every unit resampled one at a time.

{T_cluster}

- **All units are kept in the estimate.** Leaving out the outside-village units would remove {out_forest_pct} per cent
  of the forest and {out_loss_pct} per cent of the loss.
- **What the district labels rest on.** Of the {n_out} outside-village units, {d_no_check} have a district that no
  check can confirm, {d_moved} were moved off their polygon's own name, and {d_ambiguous} are ambiguous. Among the
  {ho_n} of them in the headline comparison the counts are {ai_nocheck}, {ai_moved} and {ai_amb}; {ai_contra} more
  carry a district that one check contradicts.
- **For all units together the two clusterings do not differ materially.** The interval is {h_lo} to {h_hi} with whole
  districts and {ci_l_lo} to {ci_l_hi} with only the LGD panchayat units grouped: the widths are in the ratio {w_dl}, and
  both lie above one. The result for all units does not hinge on the assigned districts.
- **For the outside-village units taken alone they do differ, and that is a finding about that land.** Grouped by
  assigned district their interval is {ho_lo} to {ho_hi}; resampled one at a time it is {ho_s_lo} to {ho_s_hi}. The
  first is {ho_ws} times as wide. Outside-village units of one district move together. They are not independent
  observations, and an analysis that treats them as such overstates what it knows about the forest land. The conclusion
  for them is the same either way: both intervals lie above one.
- **For LGD panchayat units alone the design decides the verdict.** Resampled one at a time their interval is
  {hl_s_lo} to {hl_s_hi}, which lies above one; by district it is {hl_lo} to {hl_hi}, which does not. Their district is
  their own census district and nothing in it is assigned, so the wider interval is the one to believe.
- **Resampling every unit singly would overstate certainty**: for all units {ci_s_lo} to {ci_s_hi}, an interval {w_ds}
  times narrower than the primary one.

### 5.5 What the result depends on, and what it does not show

The comparison can be made with other readings of CoRE Stack's classes. In the headline population:

{T_defs}

- **The reading matters.** The result is largest with the *lost* class ({lost_or}; {lost_lo} to {lost_hi}), the one class
  the producers validated, though on this land it is a small class ({lost_km2_gt10} km² against {deg_km2_gt10} km² of
  degradation). It is smallest with degradation net of improvement ({net_or}; {net_lo} to {net_hi}), whose interval
  includes one.
- **In the headline population the placebo passes.** Units in the top fifth on improvement coincide with Hansen's flags
  no more often than chance ({pl_or}; {pl_lo} to {pl_hi}).
- **Unit-level, not pixel-level.** The two measures agree about *which units* are degrading, not yet about *which
  hectares*. Inside a unit flagged by both, Hansen's loss and CoRE Stack's degradation may lie on different land. The
  pixel-by-pixel overlap has not been run; it needs one more Earth Engine job.
- **One window.** CoRE Stack covers 2017–2023 only, so the agreement is tested for that window and no other.
- **Modest.** Of the {h_flag_h} units Hansen flags in the headline comparison, {h_both} are flagged by CoRE Stack too.
  Most units flagged by one measure are not flagged by the other.
""")

    # ==== 6. NIRv ========================================================================================================================
    C3, C7, LO, RD = RN + "claim3_round2.json", RN + "claim7_round2_pd.json", RN + "leave_one_pass_out.json", RN + "rate_dose.json"
    big = "units with >= 50 ha of treecover2000 > 10"
    r_raw = show("nirv_r_raw", key(C3, f"part2/{big}/raw_/r_median"), dec(2))
    r_std = show("nirv_r_std", key(C3, f"part2/{big}/std_/r_median"), dec(2))
    show("nirv_units_sw", key(C3, f"part2/{big}/n"), n0)
    show("nirv_units_st", key(C3, f"part3/{big}/n"), n0)
    show("nirv_px_sw", key(C7, "part2 treecover2000 > 10, date-standardised/n_pixels"), n0)
    show("nirv_px_st", key(C7, "part3 treecover2000 > 10, date-standardised/n_pixels"), n0)
    rd = [show(f"nirv_dec_{k.replace('.', '')}", key(RD, f"part2/{k}/declining"), pc(1)) for k in ("0.9", "1.0", "1.1")]
    hold(r_raw.v < -0.5 and abs(r_std.v) < 0.3, "the first design's yearly value follows the date of the images, and the redesigned value does not")
    hold(rd[0].v > rd[1].v > rd[2].v, "the declining share falls as the fitted seasonal rate is scaled up")

    def turn(part):
        b, lost, gained = (key(LO, f"{part}/a random pass/date-standardised/{k}") for k in ("declining_before", "declining_lost", "declining_gained"))
        return 100 * (lost.v + gained.v) / b.v, [b, lost, gained]

    for name, part in (("nirv_turn_sw", "part2"), ("nirv_turn_st", "part3")):
        v, parts = turn(part)
        calc(name, v, dec(0), "(declining flags lost + declining flags gained) ÷ declining flags before × 100, one image removed at random", parts)
    null_sw = show("nirv_null_sw", key(C7, "part2 treecover2000 > 10, date-standardised/reorderings_declining_at_or_above_observed"), pc(0))
    null_st = show("nirv_null_st", key(C7, "part3 treecover2000 > 10, date-standardised/reorderings_declining_at_or_above_observed"), pc(0))
    hold(null_sw.v > 0.05 and null_st.v > 0.05, "re-ordered seasons reach the observed declining share more often than one time in twenty in both samples")
    nb = show("nirv_blank", key(DB, "table/blank_cells/nirv_slope"), n0)
    same("units with a blank NIRv cell, and all units", nb.v, n_units.v)
    hold(str(key(DB, "measures/nirv").v).startswith("pending"), "the assembled table records NIRv as pending")

    DOC.append("""
## 6. NIRv from Landsat 8: a measure that failed, which is a result

**What was tried.** A trend, over the seasons 2013–2025, in the near-infrared reflectance of vegetation (NIRv) seen by
Landsat 8 in November and December: for each pixel, a yearly value and a test for decline. It was to be the measure of
thinning that Hansen cannot see.

**What was found.** An independent replication, written from the scripts' descriptions alone, reproduced the pipeline's
values: the design was implemented correctly. It then showed what the yearly value is made of. Greenness falls through
the window as leaves age, and cloud decides which dates are seen, so the value follows the calendar: over the
{nirv_units_sw} larger units of the replication's south-west sample, the median correlation between a unit's yearly
series and the mean date of its images is {nirv_r_raw}. The value was redesigned to move every image to one date, which
removed that dependence (the same correlation becomes {nirv_r_std}). The redesigned trend then has three faults.

| | what was measured | result |
|---|---|---|
| the trend moves with the correction | the fitted seasonal rate scaled to nine tenths, to one, and to eleven tenths of itself | the declining share of the south-west sample is {nirv_dec_09}, {nirv_dec_10} and {nirv_dec_11} per cent |
| one image decides the flag | one image, drawn at random, taken away from every pixel | {nirv_turn_sw} per cent of the declining flags turn over in the south-west sample, {nirv_turn_st} in the state-wide one |
| the decline is not beyond chance | the seasons put in random order and the test run again | re-ordered seasons reach the observed declining share in {nirv_null_sw} per cent of orderings (south-west) and {nirv_null_st} (state-wide) |

The first two are properties of the measure and not of the sample. More units cannot repair them.

**What follows.** By ruling of 7 October 2026, NIRv is not a measure of degradation in this project. It remains as
reported columns of `20_degradation/degradation_by_unit.csv`, and those columns are blank in all {nirv_blank} units:
the state-wide run was stopped partway, when its queued Earth Engine tasks were cancelled from outside the pipeline,
and nothing is queued. The finding does not wait for it: a seasonal greenness trend over deciduous forest needs the
dates of its images controlled, and once they are, the trend is a function of the control.

*These figures are the replication's, on its own samples ({nirv_px_sw} pixels in the south-west and {nirv_px_st}
state-wide; {nirv_units_sw} and {nirv_units_st} larger units). They are read from its working files, which are not
stage outputs (§13). `docs/DEGRADATION.md` §5 has the full account.*
""")

    # ==== 7. need ========================================================================================================================
    NT = "tables/need_by_unit.csv/"
    pop = show("pop_units", key(N, NT + "totals_over_units/population"), n0)
    show("hh_units", key(N, NT + "totals_over_units/households"), n0)
    stp = show("st_units", key(N, NT + "totals_over_units/st_pop"), n0)
    calc("st_pct", 100 * stp.v / pop.v, dec(1), "Scheduled Tribe population of the units ÷ their population × 100", [stp, pop])
    same("population summed over the rows of the need table, and the total in its record", C(NB).population.sum(), pop.v)
    show("census_pop", key(N, "checks_passed/published_census_2011_totals/figures/population"), n0)
    hold(sorted(key(N, "checks_passed/published_census_2011_totals/equal_on").v) == ["population", "rural_population", "sc_pop", "st_pop", "urban_population"],
         "the census rows equal the published state totals on population, rural population, urban population, Scheduled Caste and Scheduled Tribe population")
    hold("households" in str(key(N, "checks_passed/published_census_2011_totals/not_checked").v), "households were not checked against a published total")
    blank_all = show("need_blank_out", key(N, NT + "columns_all_units/population/blank"), n0)
    same("units blank in the need table's population column, and outside-village units", blank_all.v, n_out.v)

    def nk(col, what):
        return key(N, NT + f"columns_lgd_panchayat_units_only/{col}/{what}")

    why = (("`st_share`: Scheduled Tribe share of population", "st_share", "the unit's villages have no resident population in the census rows"),
           ("`adi_2011`: the development index, from Census 2011", "adi_2011", "none of the unit's villages has an index"),
           ("`adi_2019`: the same index as predicted for 2019", "adi_2019", "none of the unit's villages has a prediction"),
           ("`poverty_rate`: a small-area model estimate (SHRUG)", "poverty_rate", "none of the unit's villages has an estimate"),
           ("`forest_dependent_households`: a construct, see below", "forest_dependent_households", "never blank in an LGD panchayat unit"))
    table("T_need", ["column", "LGD panchayat units with a value", "LGD panchayat units blank", "why a cell is blank", "outside-village units blank"],
          [[lab, c(nk(col, "n"), n0), c(nk(col, "blank"), n0), reason, c(key(N, NT + "columns_all_units/population/blank"), n0)] for lab, col, reason in why])
    for col in ("st_share", "adi_2011", "adi_2019", "poverty_rate"):
        same(f"`{col}`: units with a value and units blank add up to the LGD panchayat units", nk(col, "n").v + nk(col, "blank").v, n_lgd.v)
        same(f"`{col}`: blank in every outside-village unit", key(N, NT + f"columns_all_units/{col}/blank").v - nk(col, "blank").v, n_out.v)
    show("st_blank", nk("st_share", "blank"), n0)
    show("adi11_blank", nk("adi_2011", "blank"), n0)
    show("adi19_blank", nk("adi_2019", "blank"), n0)
    show("pov_blank", nk("poverty_rate", "blank"), n0)
    show("undrawn", count(NB, "LGD panchayat units where more than half the population is in villages with no polygon", lambda t: (t.unit_level == "lgd_panchayat") & (t.population_in_villages_without_polygon > 0.5 * t.population)), n0)
    show("census_unmapped", key(N, "checks_passed/census_villages_not_in_the_mapping/n"), n0)
    show("census_unmapped_pop", key(N, "checks_passed/census_villages_not_in_the_mapping/population"), n0)
    show("fdh_villages", key(N, "atree_list/qualifying_villages/n"), n0)
    show("fdh_hh", key(N, "atree_list/qualifying_villages/st_households_estimated"), n0)
    SPC = "spearman_with_the_construct_across_units"
    hold(int((C(NS)[SPC] == 1).sum()) == 1, "the sensitivity table has one row for the construct itself")
    show("fdh_rules", count(NS, "rules other than the construct itself", lambda t: t[SPC] < 1), n0)
    show("fdh_min", agg(NS, f"the smallest `{SPC}` among the other rules", lambda t: t.loc[t[SPC] < 1, SPC].min()), dec(2))
    show("fdh_max", agg(NS, f"the largest `{SPC}` among the other rules", lambda t: t.loc[t[SPC] < 1, SPC].max()), dec(2))

    DOC.append("""
## 7. Need

**What it is.** For each LGD panchayat unit, the Census 2011 counts of the villages mapped to it, and measures built on
them. The units hold {pop_units} people in {hh_units} households, of whom {st_units} ({st_pct} per cent) are of the
Scheduled Tribes.

**How it was checked.** The census rows used here, added up, equal the published Census 2011 totals for Odisha
({census_pop} people) on population, rural population, urban population, Scheduled Caste population and Scheduled Tribe
population. The published figures were taken from a secondary copy. Households are not reconciled: no published total
was found.

**What is blank, and why.**

{T_need}

- **Every column is blank for all {need_blank_out} outside-village units.** They have no census rows. This is not a
  gap that better joining would close: the census does not enumerate that land as villages.
- **Which columns carry the argument.** `st_share` is the axis of marginalisation and `adi_2011` is the control for
  development. `adi_2019` is a prediction, blank for {adi19_blank} units, and is reported only.
- **`poverty_rate` is licensed.** It is a model estimate from SHRUG, under CC BY-NC-SA 4.0. It stays in the analysis
  table. It is left out of the map layer, and no value of it is printed in this document.
- **`forest_dependent_households` is a construct, not a count**: the estimated Scheduled Tribe households of villages
  that ATREE's list of potential community-forest villages classes as having forest inside the boundary
  ({fdh_villages} villages; {fdh_hh} households, estimated). Under {fdh_rules} other reasonable rules its rank
  correlation with itself across units runs from {fdh_min} to {fdh_max}. It is reported, and used as a robustness
  reading, not as the measure of need.
- **Where the units fall short of the census.** {census_unmapped} census villages ({census_unmapped_pop} people) are not
  in the mapping. In {undrawn} units more than half the population lives in villages that have no polygon: the counts
  are right, and the shape drawn is of a minority of the unit.
""")

    # ==== 8. allocation ==================================================================================================================
    works = show("works", key(A, "dump/n_works"), n0)
    exp = show("exp_crore", key(A, "dump/expenditure_total"), crore)
    wa = show("works_assigned", key(A, "join/works_assigned"), n0)
    wu = show("works_unassigned", key(A, "join/works_unassigned"), n0)
    same("works placed in a unit and works in none add up to the works", wa.v + wu.v, works.v)
    same("works summed over the rows of the table by unit, and the works placed", C("40_allocation/allocation_by_unit.csv").n_works.sum(), wa.v)
    same("expenditure summed over the rows of the table by district and year, and the record's total", C(ADF).expenditure_total.sum(), exp.v, 1.0)
    show("exp_unassigned", key(A, "join/expenditure_unassigned_inr"), crore)
    cells = show("cells", key(A, "checks_passed/district_fy_cells_exact"), n0)
    same("district-by-year cells that were exact, and the rows of the table by district and year", cells.v, len(C(ADF)))
    show("cats", key(A, "checks_passed/categories_exact"), n0)
    to1718 = agg(ADF, "`expenditure_total` of rows whose `fy_work_start` is a year up to 2017-18", lambda t: t.loc[(t.fy_work_start != "NA") & (t.fy_work_start <= "2017-18"), "expenditure_total"].sum())
    e1718 = calc("exp_to_1718_pct", 100 * to1718.v / exp.v, dec(1), "expenditure on works started in or before FY2017-18 ÷ all expenditure × 100", [to1718, exp])
    hold(e1718.v > 95, "nearly all of the record's expenditure is on works started in or before FY2017-18")

    def rr(col, fy):
        return cell(R, col, fy=fy)

    show("cap_1617", rr("dump_capture_pct", "2016-17"), dec(0))
    cap19 = show("cap_1819", rr("dump_capture_pct", "2018-19"), dec(0))
    hold(cap19.v < 10, "the record holds a small fraction of the state report's expenditure for FY2018-19")
    show("exp_na", key(A, "dump/n_works_expenditure_na"), n0)
    hold(int(key(A, "dump/n_works_persondays_reported").v) == 0, "no work in the record reports person-days")
    pl, fn, wt = key(A, "dump/expenditure_plantation_category"), key(A, "dump/expenditure_forest_named_worktype"), key(A, "dump/expenditure_water")
    calc("plant_pct", 100 * pl.v / exp.v, dec(1), "expenditure in the plantation category ÷ all expenditure × 100", [pl, exp])
    calc("forest_named_pct", 100 * fn.v / exp.v, dec(1), "expenditure on work types that name forest ÷ all expenditure × 100", [fn, exp])
    calc("water_pct", 100 * wt.v / exp.v, dec(1), "expenditure in the water construct ÷ all expenditure × 100", [wt, exp])
    years = list(C(R).fy)
    table("T_r620", ["financial year", "expenditure, ₹ crore", "natural-resource works, % of it", "plantation, % of it", "water, % of natural-resource works", "the geotagged record holds, % of it", "report last updated"],
          [[c(rr("fy", y), txt), c(rr("r620_exp_all_lakh", y), lakh_as_crore), c(rr("r620_nrm_share_pct", y), dec(1)), c(rr("r620_plantation_share_pct", y), dec(1)), c(rr("r620_water_share_of_nrm_pct", y), dec(1)),
            c(rr("dump_capture_pct", y), dec(1)), c(rr("r620_last_updated", y), txt)] for y in years])
    show("r_years", count(R, "every row (one for each financial year)", lambda t: t.fy.notna()), n0)
    show("r_pl_1617", rr("r620_plantation_share_pct", "2016-17"), dec(1))
    show("r_pl_1819", rr("r620_plantation_share_pct", "2018-19"), dec(1))
    show("r_w_first", rr("r620_water_share_of_nrm_pct", years[0]), dec(1))
    show("r_w_2425", rr("r620_water_share_of_nrm_pct", "2024-25"), dec(1))
    show("r_first", rr("fy", years[0]), txt)
    hold(all(rr("r620_plantation_share_pct", y).v < 1 for y in years if y > "2018-19"), "plantation is under one per cent of expenditure in the state report in every year after FY2018-19")
    stamp = rr("r620_last_updated", years[0])
    show("r_frozen_stamp", stamp, txt)
    show("r_frozen", count(R, f"`r620_last_updated` is {stamp.v}", lambda t: t.r620_last_updated == stamp.v), n0)
    hold(C(R).loc[C(R).r620_last_updated == stamp.v, "r620_plantation_share_pct"].min() > C(R).loc[C(R).r620_last_updated != stamp.v, "r620_plantation_share_pct"].max(),
         "the years of the state report that carry the oldest stamp are its high-plantation years")
    hold(int(C(R).part_year.sum()) == 1 and int(C(R).part_year.iloc[-1]) == 1, "the last year of the state report is a part year, and the only one")
    w_out = show("works_out", key(A, "join/works_in_outside_village_units"), n0)
    e_out = show("exp_out", key(A, "join/expenditure_in_outside_village_units_inr"), crore)
    calc("works_out_pct", 100 * w_out.v / works.v, dec(1), "works in outside-village units ÷ all works × 100", [w_out, works])
    calc("exp_out_pct", 100 * e_out.v / exp.v, dec(1), "expenditure in outside-village units ÷ all expenditure × 100", [e_out, exp])
    show("no_works", key(A, "join/units_with_no_works"), n0)
    show("no_works_out", key(A, "join/units_with_no_works_by_level/outside_village"), n0)

    DOC.append("""
## 8. Allocation

**What it is.** The geotagged record of MGNREGA assets for Odisha: {works} works carrying ₹{exp_crore} crore of
expenditure, each placed in the unit its recorded location falls in. {works_assigned} works fall in a unit;
{works_unassigned} (₹{exp_unassigned} crore) fall in none.

**How it was checked.** Its sums by district and year equal a separate aggregation of the same record, to the rupee, in
{cells} of {cells} cells and in {cats} of {cats} categories.

- **The record effectively ends in FY2017-18.** {exp_to_1718_pct} per cent of all its expenditure is on works started in
  or before that year. Against the scheme's own state report (MIS report R6.20) it holds {cap_1617} per cent of the
  expenditure of FY2016-17 and {cap_1819} per cent of FY2018-19. It is a picture of where works were put up to
  FY2017-18. It is not current allocation.
- **What a work's money means.** A work's whole lifetime expenditure sits in the year the work started. {exp_na} works
  report no expenditure, and no work reports person-days.
- **It is not what a panchayat received.** A work is counted where it lies (§2): {por_all} per cent of works lie in
  the unit that holds most of their own recorded panchayat's works.
- **The categories overlap and must never be added.** The plantation category is {plant_pct} per cent of expenditure,
  work types that name forest {forest_named_pct}, and the water construct {water_pct}.
- **No natural-resource (NRM) figure exists per unit, and none should be built.** The record has no NRM marker, and
  water plus plantation undercounts NRM by a share that is not stable over time. NRM comes only from R6.20, for
  districts and the state:

{T_r620}

- **Plantation's share of expenditure in the state report falls from {r_pl_1617} per cent in FY2016-17 to {r_pl_1819}
  in FY2018-19, and is under one per cent in every later year. Water's share of natural-resource works rises from
  {r_w_first} per cent in FY{r_first} to {r_w_2425} in FY2024-25.**
- **Caveats on the state report.** {r_frozen} of its {r_years} years carry the stamp {r_frozen_stamp}: a snapshot frozen
  years ago, and they are the high-plantation years. Its three categories are nested, water and plantation both
  inside natural-resource works, and not a partition. The last year is a part year. Why plantation fell is not
  something these tables can say.
""")

    # ==== 9. asymmetry ===================================================================================================================
    calc("lgd_forest_pct", hl("share_of_all_forest_pct", "lgd_panchayat").v, dec(1), "read as it stands", [hl("share_of_all_forest_pct", "lgd_panchayat")])
    show("out_forest_share_of_area", hl("forest_share_of_area_pct", "outside_village"), dec(0))
    show("lgd_forest_share_of_area", hl("forest_share_of_area_pct", "lgd_panchayat"), dec(0))

    DOC.append("""
## 9. The outside-village asymmetry

The outside-village units are {out_area_pct} per cent of the land. Set beside one another, the stages say this about
them:

| | outside-village units |
|---|---|
| forest (stage 1, Hansen) | {out_forest_pct} per cent of all forest; {out_forest_share_of_area} per cent of their own area is forest, against {lgd_forest_share_of_area} per cent in LGD panchayat units |
| tree-cover loss (stage 1, Hansen) | {out_loss_pct} per cent of all loss in the mask |
| degradation class (stage 1, CoRE Stack) | {cs_out_deg_pct} per cent of it |
| the agreement comparison | {ho_n} of the {h_n} units compared, and the agreement holds among them (§5.2) |
| need (stage 2) | **nothing: every column blank in all {n_out}** |
| allocation (stage 3) | {works_out} works worth ₹{exp_out} crore lie inside them: {works_out_pct} per cent of works and {exp_out_pct} per cent of expenditure. Of the {no_works} units with no work at all, {no_works_out} are outside-village units |
| district | assigned, not recorded (§2) |

Most of the forest, and most of its loss, is on land for which the planning system has no population figure of any
kind. Work is nonetheless recorded there. Any comparison of need with allocation that requires census data can describe
only the LGD panchayat units, which hold {lgd_forest_pct} per cent of the forest. That is a finding of its own, and it
stands whatever stage 4 turns out to be.
""")

    # ==== 10. the layer ==================================================================================================================
    show("layer_mb", key(L, "outputs/both_bytes"), mb)
    show("layer_zip_mb", key(L, "outputs/both_zipped_bytes"), mb)
    show("layer_fields", key(L, "table/fields_per_unit_in_the_panel"), n0)
    show("layer_tol", key(L, "geometry/tolerance_m"), n0)
    show("layer_small", key(L, "geometry/units_changed_by_more_than_5_pct"), n0)
    hold(float(key(L, "default_floor_ha").v) == FLOOR, "the layer's default minimum of forest is the ruled floor")
    omitted = key(L, "omitted_on_purpose/columns").v
    hold(len(omitted) > 0 and all(x.startswith("poverty_rate") for x in omitted), "the columns the layer leaves out on purpose are the SHRUG-derived ones")
    ex = {}
    for tag, path in (("c", EXC), ("w", EXW)):
        hold(key(path, "summary/layer_run_utc").v == key(L, "run_utc").v, f"the hand check ({'Chrome' if tag == 'c' else 'WebKit'}) was made on the build of the layer that is on disk")
        hold(J(path)["summary"]["files_sha256"] == key(L, "outputs/sha256").v, f"the files the hand check ({'Chrome' if tag == 'c' else 'WebKit'}) opened have the sha256 the layer's record gives")
        hold(J(path)["summary"]["script_errors"] == [], f"the hand check ({'Chrome' if tag == 'c' else 'WebKit'}) met no script error")
        show(f"ex_{tag}_browser", key(path, "summary/browser"), txt)
        ex[tag] = [show(f"ex_{tag}_{k}", key(path, f"summary/{src}"), n0) for k, src in (("ok", "controls_as_expected"), ("n", "controls_exercised"), ("units", "units_clicked"), ("eq", "values_equal"), ("vals", "values_compared"))]
        hold(ex[tag][0].v == ex[tag][1].v and ex[tag][3].v == ex[tag][4].v, "in the hand check every control did what it should and every displayed value equalled the stage tables")

    safari_now = key(EXS, "summary/layer_run_utc").v == key(L, "run_utc").v and J(EXS)["summary"]["files_sha256"] == key(L, "outputs/sha256").v
    if not safari_now:                                      # the one exception (9 October 2026): the runner's record of this build must name the Safari check as left out, with a reason
        left = [x for x in key(RUNS, "checks_not_run_in_this_pass").v if x["check"] == "exercise_layer_safari, as written"]
        hold(key(RUNS, "layer_run_utc").v == key(L, "run_utc").v and "unfinished" not in J(RUNS) and len(left) == 1 and left[0]["why"].strip() != ""
             and all(x["last_run_passed"] for x in key(RUNS, "checks").v) and {"exercise_layer in Chrome", "exercise_layer in WebKit", "verify_layer"} <= {x["check"] for x in key(RUNS, "checks").v},
             "the check in the Safari application was not made on the build of the layer that is on disk, and the runner's record of that build names it as left out with a reason, every check it did run having passed")
        show("ex_s_why", V(left[0]["why"], RUNS, "key `checks_not_run_in_this_pass`: `why` of the check in the Safari application"), txt)
        show("ex_s_build", key(EXS, "summary/layer_run_utc"), txt)
    show("safari_state", V("and the page opened and read in the Safari application" if safari_now else "and the page last opened and read in the Safari application on an earlier build, not on this one",
                           EXS if safari_now else RUNS, "whether the record of the check in the Safari application is of the layer on disk" if safari_now else "key `checks_not_run_in_this_pass`: the check in the Safari application is named there"), txt)
    show("safari_limit", V("" if safari_now else ", and on an earlier build than the one on disk", EXS, "key `summary` → `layer_run_utc`, against the layer's own record"), txt)
    show("ex_s_browser", key(EXS, "summary/browser"), txt)
    sa = [show(f"ex_s_{k}", key(EXS, f"summary/{src}"), n0) for k, src in (("ok", "addresses_as_expected"), ("n", "addresses_tried"), ("units", "units_opened_by_address"), ("eq", "values_found"), ("vals", "values_compared"))]
    hold(sa[0].v == sa[1].v and sa[3].v == sa[4].v, "in the Safari application every address showed what it should and every value a panel should show was in the page's text")
    hold([u["unit"] for u in J(EXS)["units"]] == [u["opened"] for u in J(EXC)["units"]], "the units opened in the Safari application are the units clicked in Chrome")

    if safari_now:
        safari_bullet = """- **Opened in the Safari application itself, from disk**, by `scripts/exercise_layer_safari.py`, in {ex_s_browser}. There
  the page was driven by its address alone and its text read back; nothing was clicked. {ex_s_ok} of {ex_s_n} addresses
  showed what they should (every layer, every minimum of forest, the search, the two text panels), and for the same
  {ex_s_units} units {ex_s_eq} of {ex_s_vals} values the panel should show were in the page's text.
"""
    else:
        safari_bullet = """- **Not opened in the Safari application on this build.** That check was left out of this build's checks, and their
  record gives the reason: "{ex_s_why}". The last run of `scripts/exercise_layer_safari.py`, in {ex_s_browser}, was on
  the layer built {ex_s_build}, not the one on disk: there the page was driven by its address alone and its text read
  back, nothing was clicked, {ex_s_ok} of {ex_s_n} addresses showed what they should (every layer, every minimum of
  forest, the search, the two text panels), and for the same {ex_s_units} units {ex_s_eq} of {ex_s_vals} values the
  panel should show were in the page's text. On the build on disk the layer was exercised in Chrome and in Safari's
  engine only.
"""
    DOC.append("""
## 10. The map layer

**What it is.** Two files, `60_layer/index.html` and `60_layer/data.js` ({layer_mb} MB together, {layer_zip_mb} MB
zipped), that open from disk in a browser and fetch nothing from the network: a map of the {n_units} units with a layer
for each measure above, a panel of {layer_fields} figures for a clicked unit, a search, filters by kind of unit and by
district, and a minimum of forest below which a unit is drawn grey ({floor} ha unless changed). It is a demonstration
for discussion with people who know the places. It is not a verdict on any place.

- **Checked against the stage tables** by `scripts/verify_layer.py`: {v_layer}.
- **Every control exercised on the build that is on disk** ({run_layer}), by `scripts/exercise_layer.py`, which writes
  `60_layer/exercise_chrome.json` and `60_layer/exercise_webkit.json`. In Chrome ({ex_c_browser}), opened from disk
  and driven with real mouse and keyboard events: {ex_c_ok} of {ex_c_n} actions did what they should, and for
  {ex_c_units} units clicked on the map {ex_c_eq} of {ex_c_vals} displayed values equalled the stage tables. In
  {ex_w_browser}, with events made in script: {ex_w_ok} of {ex_w_n}, and for {ex_w_units}
  units {ex_w_eq} of {ex_w_vals}. `docs/LAYER.md` lists each action and what happened.
""" + safari_bullet + """- **Not done.** No click was made in the Safari application, only in its engine: that needs a Safari setting that is
  the owner's to change. And Firefox was not installed on the machine, so the layer has not been opened in it.
- **Left out on purpose**: the SHRUG-derived columns (§7).
- **The shapes are simplified** so that the file can be sent, with a tolerance of {layer_tol} m; {layer_small} very small
  units change by more than five per cent in drawn area. Every area printed in a panel is the unit's true area.
- **Licence of the shapes.** They derive from DataMeet's village boundaries and carry the ODbL 1.0.
""")

    # ==== 11. not built, and blank ========================================================================================================
    DOC.append("""
## 11. Not built, and inputs still blank

- **Stage 4, the comparison of forest condition, need and allocation, is not built.** The project owner is
  respecifying it. `50_gap/` is empty.
- **The pixel-by-pixel overlap of Hansen's loss with CoRE Stack's degradation is not run** (§5.5). It needs an Earth
  Engine job.
- **The state-wide NIRv run is stopped and nothing is queued** (§6). Its columns are blank.
- **The VGPP plantation unit cost (₹ per hectare) is blank.** It is not in `00_raw/`, and no figure has been put in its
  place. Nothing can be costed until it is supplied.
- **The coordinates of the district headquarters are blank**, for the same reason; so no control for remoteness exists.
- **Whether Annexure-A of the order of 22 May 2026 carries a grade for each gram panchayat, or only the formula, is not
  known** (`docs/DATA_NOTES.md`).
- **Forest-rights titles are in no stage.** The two official reports on them disagree with each other
  (`docs/DATA_NOTES.md`), and no title data are joined to the units.
""")

    # ==== 12. limitations ================================================================================================================
    px = C(CR).loc[C(CR).quantity == "area per pixel with a value"]
    hold(len(px) == 1, "the reconciliation table has one row for the area of a pixel")
    show("px_below", V(abs(float(px.difference_pct_of_published.iloc[0])), CR, "column `difference_pct_of_published`", "`quantity` is 'area per pixel with a value'"), dec(1))
    hold(float(px.difference_pct_of_published.iloc[0]) < 0, "this pipeline's area for a CoRE Stack pixel is below the producers' nominal one")
    show("n_clusters", ag("n_districts", HP, "all units"), n0)
    show("pf_more", key(N, "checks_passed/panchayat_file/ids_where_it_holds_more"), n0)
    show("pov_few", key(N, "checks_passed/secc/units/rate_resting_on_fewer_than_100_people"), n0)
    show("pov_shared", key(N, "checks_passed/secc/units/some_of_the_rate_from_a_shrid_shared_with_another_id"), n0)
    DOC.append("""
## 12. Limitations

Collected from `docs/UNITS.md`, `docs/DEGRADATION.md`, `docs/NEED.md`, `docs/NRM.md`, `docs/DATA_NOTES.md` and
`docs/LAYER.md`, which give the detail. The first seven are the ones a reviewer finds first.

**The seven.**

- **The agreement is unit-level, not pixel-level.** The two forest measures agree about which units are degrading, not
  about which hectares. The pixel overlap is unrun (§5.5).
- **CoRE Stack covers 2017–2023 only.** It compares two three-year periods; nothing before them is seen, and the
  agreement with Hansen is tested for that window alone (§4, §5.5).
- **The placebo fails in one zone.** Under CoRE Stack's East Coast model, Hansen's loss goes with improvement
  ({ec_imp}) as well as with degradation. Those {ec_n} units are left out of the headline; leaving them out removes the
  result for LGD panchayat units taken alone (§5.2).
- **{under1_pct} per cent of units have under a hectare of forest** ({under1} of {n_units}). Rates on such units are
  noise; comparisons use a floor of {floor} ha, below which {ff_below} units fall (§3, §5.3).
- **The outside-village land has no census data at all.** {n_out} units, {out_area_pct} per cent of the land and
  {out_forest_pct} per cent of the forest, are blank in every column of need (§7, §9).
- **`poverty_rate` is SHRUG-licensed and omitted from the layer.** CC BY-NC-SA 4.0: any released file that carries it,
  or figures derived from it, may be bound by that licence. It is also a model estimate, blank for {pov_blank} LGD
  panchayat units (§7).
- **Species composition is not measurable from these sources.** Hansen sees canopy and its removal; CoRE Stack sees
  classes of canopy density and height. Neither tells a natural forest from a plantation, or one species from another.
  A plantation replacing a forest is, to both, tree cover.

**The unit.**

- A unit is an LGD panchayat id, not a gram panchayat, and there are more units than gram panchayats (§2).
- A unit is not the panchayat that recorded a work: {por_all} per cent of works lie in their recorded panchayat's
  main unit (§2).
- {n_unmapped} coded villages ({km2_unmapped} km²) are in no unit; {n_ids_no_polygon} ids of the mapping
  ({pop_ids_no_polygon} people) have no polygon.
- The layer's area is on the ellipsoid and is not validated against the state's official area.
- Two other layers are kept for sensitivity, one with the outside-village land dropped and one with it merged into the
  nearest unit. Nothing in this document uses them.
- The district of an outside-village unit is assigned: {d_no_check} with no possible check, {d_moved} moved off the
  polygon's name, {d_ambiguous} ambiguous, {d_flagged} flagged and not moved. The crosswalk of district names inside
  the boundary layer has faults of its own, recorded in `docs/UNITS.md` and not corrected.

**Forest condition.**

- Hansen's loss is stand-replacing removal from any cause. It is not deforestation, cannot see thinning, and does not
  net off gain. Its method changed from 2011.
- The forest mask is a choice fixed at 2000. {outside_mask_pct} per cent of recorded loss is outside it, most of that
  on land with no canopy in 2000, and its rise over time is largely the method (§3.1).
- Earth Engine's area for a pixel cut by a boundary is approximate; the sums over pixels and over polygons are compared
  in the build and held to a tolerance (`20_degradation/hansen.provenance.json`).
- CoRE Stack's degradation is the crossing of a line by classifiers right about two times in three; only its *lost*
  class was validated by its producers; its tree mask takes in {cs_tree_pct} per cent of the units' area; its two zone
  models differ ({down_ep} against {down_ec} in downward share); and only one published figure exists to reconcile it
  to (§4).
- The agreement is modest and depends on choices: the floor (weaker as the floor rises, §5.3), the CoRE Stack class
  used (§5.5), and the zone exclusion (§5.2). The failure of the placebo is itself not firmly established: it rests on
  {ec_d} districts.
- A flag is relative: it marks the top fifth of the units compared, not a stated amount of loss or degradation.
- The intervals rest on resampling districts, and for outside-village units the district is assigned (§5.4).
  {n_clusters} districts is few clusters, so the intervals are themselves rough.
- All areas are on the ellipsoid. The producers of CoRE Stack count a nominal area for every pixel; this pipeline's
  area for the same pixel is {px_below} per cent smaller, so their own tallies of the same raster would be larger.
- NIRv is unfit as a measure, and its columns are blank (§6).

**Need.**

- The census is that of 2011. The development index for 2019 is a prediction, blank for {adi19_blank} units.
- `st_share` is blank for {st_blank} LGD panchayat units and `adi_2011` for {adi11_blank}.
- `forest_dependent_households` is a construct resting on one list and one rule (§7).
- Households are not reconciled to a published total, and the population totals were checked against a secondary copy
  of the census figures.
- In {undrawn} units most of the population lives in villages with no polygon.
- The panchayat-level file supplied with the census data holds more people than the village rows in {pf_more} ids (it
  double counts) and is used only as a cross-check; every figure here is built from village rows.
- The poverty estimate rests on fewer than a hundred people in {pov_few} units, and in {pov_shared} units part of it comes
  from an area shared with another unit.

**Allocation.**

- The geotagged record effectively ends in FY2017-18 ({exp_to_1718_pct} per cent of expenditure up to then). It is not
  current allocation (§8).
- A work's lifetime expenditure sits in its start year; {exp_na} works report none; none reports person-days.
- {works_unassigned} works fall in no unit.
- Categories overlap; no NRM figure exists per unit; the work-type flags for water and for forest have no verified
  reference to be held against.
- The state report's high-plantation years are a frozen snapshot, and its categories are nested (§8).

**Sharing.**

- SHRUG-derived columns must stay out of anything released. The development index for 2011 is kept in the layer on a
  judgement that it is computed from census rows; a stricter reading of SHRUG's terms would remove it
  (`docs/DATA_NOTES.md`).
- The unit shapes are a database derived from DataMeet's under the ODbL 1.0, and may be shared under that licence and
  no narrower one.
- Two inputs carry no stated licence: the Global Forest Watch workbook and ATREE's list of villages. Only figures read
  from them are used, and neither file is redistributed. Whether the Foundation may pass the layer on, and under what
  statement, is not decided.
- The layer shows Scheduled Tribe share and the development index as maps. The paper it takes its vocabulary from
  reports a community that did not favour the mapping of inequity; whether those two layers belong in what is shown is
  the Foundation's call (`docs/LAYER.md` §9).
- The layer's controls were exercised in Chrome and in Safari's engine. In the Safari application it was opened and
  read, not clicked{safari_limit}. It has not been opened in Firefox, on a phone, in print, or on a machine with little memory
  (§10).
""")

    # ==== gates, then the appendix =======================================================================================================
    body = "".join(DOC)
    bad = stray_digits(body)
    if bad:
        stop("the text carries digits of its own:\n  " + "\n  ".join(bad[:25]))
    asked = re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", body)
    known = set(FIG) | set(TABLES)
    if set(asked) - known:
        stop("printed but not defined: " + ", ".join(sorted(set(asked) - known)))
    if known - set(asked):
        stop("defined but not printed: " + ", ".join(sorted(known - set(asked))))
    text = body.format_map({**{k: v["text"] for k, v in FIG.items()}, **{k: v["md"] for k, v in TABLES.items()}})

    def mark(path):
        return f"`{path}`" + (" *(working file)*" if path.startswith(SCRATCH) else "")

    order, seen = [], set()
    for k in asked:
        if k not in seen:
            seen.add(k)
            order.append(k)
    app = ["\n## 13. Where every figure comes from\n",
           "This section is the script's own record of what it read. Paths are relative to the repository. The numbered folders "
           "(`10_units/` to `60_layer/`) are stage outputs: each is rebuilt by the script named in the `.provenance.json` beside it, and none is in git. "
           f"Files under `{SCRATCH}/` are **working files** of the sessions that made the pipeline. They are not stage outputs and no tracked script rebuilds them; "
           "the NIRv replication (§6) has no other record.\n",
           "### 13.1 Figures in the text, in the order they first appear\n", "| as printed | file | where in the file |", "|---|---|---|"]
    for k in order:
        if k in FIG:
            f = FIG[k]
            files = "; ".join(dict.fromkeys(mark(s[0]) if s[0] not in ("this run",) and not s[0].startswith("scripts/") else f"`{s[0]}`" if s[0].startswith("scripts/") else s[0] for s in f["sources"]))
            where = (f"computed here: {f['formula']}. From: " + "; ".join(s[1] for s in f["sources"])) if f["formula"] else f["sources"][0][1]
            app.append(f"| {f['text']} | {files} | {where.replace('|', '/')} |")
    app += ["\n### 13.2 Tables, in the order they appear\n", "Every cell of a table that is not a typed label was read from the file and columns given here.\n", "| table | cells read | file | columns or keys | rows |", "|---|---|---|---|---|"]
    names = {"T_hansen": "§3, forest and loss by kind of unit", "T_bands": "§3.1, loss by band of canopy", "T_corestack": "§4, CoRE Stack classes", "T_agree": "§5.1, the result two ways",
             "T_zone": "§5.2, by zone model", "T_floor": "§5.3, by floor", "T_cluster": "§5.4, three designs of resampling", "T_defs": "§5.5, by CoRE Stack reading", "T_need": "§7, what is blank",
             "T_r620": "§8, the state report by year"}
    for k in order:
        if k in TABLES:
            for i, (file, s) in enumerate(TABLES[k]["src"].items()):
                rows = "; ".join(s["rows"])
                app.append(f"| {names.get(k, k) if i == 0 else ''} | {TABLES[k]['cells'] if i == 0 else ''} | {mark(file)} | {', '.join(x.replace('column ', '').replace('key ', '') for x in s['cols'])} | {(rows if len(rows) < 900 else rows[:900] + ' ...').replace('|', '/')} |")
    app += ["\n### 13.3 Files read\n", "| file | bytes | sha256 | the run stamp it carries |", "|---|---|---|---|"]
    for path in sorted(FILES):
        f = FILES[path]
        app.append(f"| {mark(path)} | {f['bytes']:,} | `{f['sha256'][:16]}` | {f['run_utc'] or '-'} |")
    app += ["\n### 13.4 Statements tested before they were written\n", "Each of these is something the text says in words. The script tested it against the figures and would have stopped had it failed.\n"]
    app += [f"- {s}" for s in HELD]
    app += ["\n### 13.5 Totals that two places both carry, compared\n"] + [f"- {s}" for s in SAME]
    app += ["\n### 13.6 Digits the text was allowed to carry\n", "The text itself may hold no digit except inside a code span (a file, a column, a threshold written as code) and in: "
            + "; ".join(why for _, why in ALLOWED) + ". Everything else that is a number came from a file.\n",
            f"*{len([k for k in order if k in FIG])} figures and {len(TABLES)} tables ({sum(t['cells'] for t in TABLES.values())} cells) from {len(FILES)} files; {len(HELD)} statements tested; {len(SAME)} totals compared. "
            f"Written {written} by `scripts/write_results.py` (sha256 `{sha256(__file__)[:16]}`).*\n"]
    out = Path(a.draft) if a.draft else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n".join(app), encoding="utf-8")
    print(f"{out}: {len(text.splitlines()) + len(app):,} lines; {len([k for k in order if k in FIG])} figures, {len(TABLES)} tables ({sum(t['cells'] for t in TABLES.values())} cells), {len(FILES)} files read; "
          f"{len(HELD)} statements tested, {len(SAME)} totals compared; verifiers {'NOT run (draft)' if a.draft else 'run'}")


if __name__ == "__main__":
    main()
