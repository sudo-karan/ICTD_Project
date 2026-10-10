#!/usr/bin/env python3
"""Stage 4, the independent check: recomputes the figures of the tables the stage's steps write into `50_gap/`, from the inputs, and compares.

    ~/.venvs/ictd-stage4/bin/python scripts/verify_gap.py [--tables DIR] [--only PART,PART]

It runs in stage 4's own environment (`README.md` section 0), and its first part holds that it does. Reads, writes
nothing. It imports nothing from the builders (`scripts/08_*.py`, `scripts/_gap_common.py`) and shares no code with
them. `--tables DIR` checks the tables in another folder (a copy with a deliberate error, for instance) against the
same inputs; the default is `50_gap/`. The last line is `N of N checks passed`; the exit status is 0 only if every
check passed.

Who wrote what. The parts `inputs`, `districts`, `comparisons`, `panel`, `units`, `rights` and `fsi` were each written
by an agent that was given the definitions in the builders' docstrings and was not allowed to open the builders; each
of the first six was then reviewed, tried with planted errors and corrected by another such agent, and the `fsi` part
was tried with planted errors by the agent that wrote it. The parts `environment`, `deck` and `texts` compare a file
with the file it is derived from; they were written by the session that wrote the builders, and reviewed, tried and
corrected by an agent that did not open the builders. After that one round the session reworded this description and
three check names, added one check to the `deck` part and tightened one of the `environment` part.
`docs/stage4_run_log.md` gives the counts of the round and names what was changed after it.

What it reads, and what it does not. The reader of the review round found, by reading every part and not by trial,
that each column of the 23 tables the steps write (20 in `50_gap/`, 3 in `50_gap/deck_tables/`) is read by at least
one check. A figure is recomputed from the inputs; a label, a note or a reason is held by the key words its check
names, not word for word. The three deck tables and the two text files of the models are held against the tables
they are cut from, which the other parts recompute. The owner's expected values and spelling rules are typed into the
parts from his instructions of 10 and 11 October 2026: no file of the repository carries them for a check to read.
Not read at all: the gate tables of the phases that have no step (`gates_phase1.csv`, `gates_phase6.csv` to
`gates_phase8.csv`, `gates_step*.csv`), the lists of what differs between two builds (`rebuild_*_differences.csv`),
`figures_looked_at.json`, `mutation_trials_phase1.json`, `verify_gap_trials.json`, `verify_gap_reviews.json`,
`environment_main_while_stage4_packages_were_in_it.txt`, the kept copies of earlier builds, and, in
`gap.provenance.json`, the top-level `what` and the sentences of prose a step records about itself.

What is recomputed exactly, and what only to a tolerance:
  - sums of hectares and of money: exactly (decimal arithmetic), from the stage tables and the registered inputs;
  - shares, ratios and coefficients: to the last digit the table prints;
  - a permutation p and a bootstrap interval of a rank correlation: twice. With this script's own draws, so to the
    tolerance that the number of draws allows, stated in the check's name; and drawn again with the seeds the
    definitions give, to the digit. The second rests on one reading of how the generator is called, which the
    definitions do not give; each such check states the reading in its name;
  - a wild-cluster-bootstrap p and interval: the coefficient and its CR1 standard error are recomputed here in numpy;
    the p is recomputed with this script's own implementation of the restricted wild cluster bootstrap (Webb weights)
    and its own draws, to a stated tolerance; and the interval's two ends are tested with the `wildboottest` package
    and the seed the table records: just inside each end p must be at least 0.05, just outside it below.
"""
import argparse
import csv
import json
import math
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
_ap = argparse.ArgumentParser()
_ap.add_argument("--tables", default=str(ROOT / "50_gap"), help="the folder that holds the stage-4 tables to check (default: 50_gap/)")
_ap.add_argument("--only", default="", help="run only these parts, comma-separated (environment, inputs, districts, comparisons, panel, units, rights, fsi, deck, texts); default: all")
_args = _ap.parse_args()
GAP = Path(_args.tables).resolve()
ONLY = [x.strip() for x in _args.only.split(",") if x.strip()]
results = []


def check(what, ok, detail=""):
    """One check: what it tests, in words that say no more than it tests; whether it held; and, if not, what was found."""
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {what}" + (f"   {detail}" if detail else ""), flush=True)


def rows(path):
    """A CSV as a list of dicts, every cell as text, a blank cell as ''. `path` is absolute, or relative to the repository."""
    p = Path(path)
    with open(p if p.is_absolute() else ROOT / p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def table(name):
    """A table of the folder being checked (`--tables`)."""
    return rows(GAP / name)


def D(x):
    return Decimal(str(x).strip())


def q(x, places):
    return x.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def close(a, b, tol):
    """Two numbers given as text or numbers, equal to within tol; a blank equals only a blank."""
    if a in ("", None) or b in ("", None):
        return a in ("", None) and b in ("", None)
    return abs(float(a) - float(b)) <= tol


def mismatches(pairs, limit=3):
    """A short account of the first few (key, in the table, recomputed) that differ, for a check's detail."""
    bad = [p for p in pairs if not p[3]]
    return "" if not bad else f"{len(bad)} differ, e.g. " + "; ".join(f"{k}: table {a!r}, recomputed {b!r}" for k, a, b, _ in bad[:limit])

# ---- part: environment ------------------------------------------------------------------------------------------------------------------
# Stage 4 runs in an environment of its own, outside the repository, which holds exactly what requirements-stage4.txt pins. This part
# holds that the interpreter running the check is that environment, and that every step of the provenance record says it ran in it.
# The gates table and the record are derived files: where a cell of theirs can be made again from a file on disk (the earlier stages'
# records, the two lists of the main environment) it is; the main environment itself is never opened here.
def _env_canonical(name):
    return name.strip().lower().replace("_", "-").replace(".", "-")


def _env_pins():
    pins = {}
    for line in (ROOT / "requirements-stage4.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            name, _, version = line.partition("==")
            pins[_env_canonical(name)] = version.strip()
    return pins


def _env_held():
    import importlib.metadata as md
    held = {}
    for d in md.distributions():
        name = _env_canonical(d.metadata["Name"])
        if name != "pip":
            held[name] = d.version
    return held


def _env_sha256(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _env_numpy_in(record):
    """Every text found under a key `numpy`, wherever in a provenance record the key sits."""
    found = []
    if isinstance(record, dict):
        for k, v in record.items():
            if k == "numpy" and isinstance(v, str):
                found.append(v)
            else:
                found += _env_numpy_in(v)
    elif isinstance(record, list):
        for v in record:
            found += _env_numpy_in(v)
    return found


def _env_lines(path):
    """The lines of a list of packages that are not blank; None if the file is not there."""
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.is_file() else None


_env_GATES = {                                                      # what the definition says the script holds: the words that find its gate
    "the interpreter holds exactly what the file pins": "holds exactly what requirements-stage4.txt pins",
    "the stage-4 environment is outside the repository": "outside the repository",
    "wildboottest": "the stage-4 environment: wildboottest", "numba": "the stage-4 environment: numba", "numpy of stage 4": "the stage-4 environment: numpy",
    "numpy of the main environment": "the main environment: numpy",
    "the main environment's list of packages": "environment_before_stage4.txt",
    "verify_r620.py": "scripts/verify_r620.py", "verify_layer.py": "scripts/verify_layer.py", "verify_decision.py": "scripts/verify_decision.py"}


def part_environment():
    import re
    pins, held = _env_pins(), _env_held()
    differ = sorted(n for n in set(pins) | set(held) if pins.get(n) != held.get(n))
    check(f"the interpreter running this check holds exactly what requirements-stage4.txt pins: the {len(pins)} packages of the file, each at its version, and no other (pip itself apart)",
          not differ and len(pins) > 0, "" if not differ else "; ".join(f"{n}: pinned {pins.get(n, 'not pinned')}, held {held.get(n, 'not installed')}" for n in differ[:6]))
    check("that interpreter is outside the repository", not Path(sys.prefix).resolve().is_relative_to(ROOT.resolve()), sys.prefix)
    named = {"wildboottest": held.get("wildboottest") == "0.3.2", "numba": held.get("numba") == "0.62.1", "numpy": str(held.get("numpy", "")).startswith("2.3.")}
    check("it holds the versions the owner named: wildboottest 0.3.2, numba 0.62.1, numpy 2.3.x", all(named.values()),
          "; ".join(f"{n} {held.get(n, 'not installed')}" for n in named))

    prov = json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8"))["steps"]
    wanted = ["08_gap_environment", "08_gap_inputs", "08_build_gap_districts", "08_build_gap_panel", "08_build_gap_units", "08_build_gap_rights", "08_build_gap_fsi", "08_build_gap_deck_tables"]
    missing = [s for s in wanted if s not in prov]
    other = [s for s in prov if s not in wanted]
    check(f"gap.provenance.json has a section for each of the {len(wanted)} steps that write the tables, and no other section", not missing and not other,
          ("missing: " + ", ".join(missing) + "; " if missing else "") + ("not one of the steps: " + ", ".join(other) if other else ""))
    every = wanted + other                                          # a section that is not one of the steps is held to the same record
    req_sha = _env_sha256(ROOT / "requirements-stage4.txt")
    bad = []
    for s in every:
        e = prov.get(s, {}).get("environment") or {}
        if not (e.get("holds_exactly_what_the_file_pins") is True and e.get("requirements_sha256") == req_sha and e.get("requirements_file") == "requirements-stage4.txt"
                and e.get("packages") == held and e.get("differences") == [] and e.get("packages_pinned") == len(pins) and e.get("python") == sys.version.split()[0]):
            bad.append(s)
    check(f"every section of the record ({len(every)}: those steps', and any other it has) records an environment that held exactly what the file pins: the file's SHA-256 as it is on disk, "
          "and, package for package and for the interpreter's own version, what the interpreter running this check holds", not bad, "" if not bad else "not so: " + ", ".join(bad))
    stale = []
    for s in every:
        sec = prov.get(s, {})
        for key in ("script", "shared_module"):
            path = ROOT / sec.get(key, "?")
            if not path.is_file() or _env_sha256(path) != sec.get(key + "_sha256"):
                stale.append(f"{s}: {key}")
    check("every section of the record names a script and a shared module whose SHA-256 is that of the file on disk: no step is recorded as built by code that has since changed "
          "(the files are hashed, not read)", not stale, "; ".join(stale))

    g = table("gates_environment.csv")
    check("gates_environment.csv: every gate on the two environments passed, and there is at least one", len(g) > 0 and all(r["pass"] == "yes" for r in g),
          "; ".join(r["gate"][:60] for r in g if r["pass"] != "yes"))
    rows_of = {k: [r for r in g if words in r["gate"]] for k, words in _env_GATES.items()}
    columns = list(g[0].keys()) if g else []
    check(f"gates_environment.csv has the four columns the definition gives it (gate, expected, found, pass) and one gate, and one only, for each of the {len(_env_GATES)} things the definition says "
          "the script holds (the interpreter against the file; outside the repository; wildboottest, numba and numpy of stage 4; numpy of the main environment; its list of packages against the "
          "list kept; verify_r620.py, verify_layer.py and verify_decision.py), each found by the words of its gate",
          columns == ["gate", "expected", "found", "pass"] and all(len(v) == 1 for v in rows_of.values()),
          ("" if columns == ["gate", "expected", "found", "pass"] else f"columns {columns}; ") + "; ".join(f"{k}: {len(v)} gates" for k, v in rows_of.items() if len(v) != 1))
    gate = {k: (v[0] if len(v) == 1 else {"gate": "", "expected": "", "found": "", "pass": ""}) for k, v in rows_of.items()}
    sec = prov.get("08_gap_environment", {})
    n_yes = sum(1 for r in g if r["pass"] == "yes")
    check("the record's section 08_gap_environment: `gates` is the number of rows of gates_environment.csv and `gates_passed` the number of them with pass = yes",
          type(sec.get("gates")) is int and type(sec.get("gates_passed")) is int and (sec.get("gates"), sec.get("gates_passed")) == (len(g), n_yes),
          f"record {sec.get('gates')!r} and {sec.get('gates_passed')!r}; the table has {len(g)} rows, {n_yes} with yes")
    found = {r["gate"]: r["found"] for r in g}
    said = {n: found.get(f"the stage-4 environment: {n}") for n in ("wildboottest", "numba", "numpy")}
    check("gates_environment.csv: the versions it found for wildboottest, numba and numpy in the stage-4 environment are those the interpreter running this check holds",
          all(said[n] == held.get(n) for n in said), "; ".join(f"{n}: table {said[n]}, held {held.get(n)}" for n in said))
    first, layer, decision = gate["the interpreter holds exactly what the file pins"], gate["verify_layer.py"], gate["verify_decision.py"]
    passed = re.fullmatch(r"(\d+) of (\d+) checks passed", decision["found"])
    check("gates_environment.csv: the number of packages its first gate expected is the number the file pins, and the number it found is the number the interpreter running this check holds; "
          "verify_layer.py's line is '92 of 92 checks passed' (the count the definition gives); verify_decision.py's is 'N of N checks passed' with one N (the definition gives no count)",
          re.findall(r"\d+", first["expected"]) == [str(len(pins))] and re.findall(r"\d+", first["found"]) == [str(len(held))] and first["found"].startswith("yes")
          and layer["found"] == "92 of 92 checks passed" and bool(passed) and passed.group(1) == passed.group(2),
          f"first gate: expected {first['expected']!r}, found {first['found']!r}; verify_layer.py {layer['found']!r}; verify_decision.py {decision['found']!r}")

    # the main environment: what the gates and the record say of it, made again from the files on disk
    main = sec.get("main_environment", {})
    shown = {}
    for folder in ("20_degradation", "30_need", "40_allocation", "55_decision"):
        for path in sorted((ROOT / folder).glob("*.provenance.json")):
            versions = _env_numpy_in(json.loads(path.read_text(encoding="utf-8")))
            if versions:
                shown[path.relative_to(ROOT).as_posix()] = sorted(set(versions))
    one = sorted({v for versions in shown.values() for v in versions})
    now = _env_lines(GAP / "environment_main_now.txt")
    numpy_now = [l.split("==", 1)[1] for l in (now or []) if l.split("==", 1)[0].strip().lower() == "numpy" and "==" in l]
    of_main = gate["numpy of the main environment"]
    check(f"the main environment's numpy: the provenance records of the earlier stages (every *.provenance.json of 20_degradation/, 30_need/, 40_allocation/ and 55_decision/ that carries a numpy "
          f"version: {len(shown)} of them, read here) show one version, and it is the version the record gives the main environment (`numpy`, and the one entry of "
          "`the_version_the_earlier_records_show`), the version the gate found and expected, and the version of the numpy line of environment_main_now.txt (the main environment is not opened here)",
          len(one) == 1 and main.get("numpy") == one[0] and main.get("the_version_the_earlier_records_show") == one and of_main["found"] == one[0]
          and of_main["expected"].split(" ")[0] == one[0] and numpy_now == one,
          f"the earlier records show {one}; the record {main.get('numpy')!r} and {main.get('the_version_the_earlier_records_show')!r}; the gate found {of_main['found']!r}, expected {of_main['expected']!r}; the list {numpy_now}")
    read = [v.get("path") for k, v in (sec.get("inputs") or {}).items() if k.startswith("provenance_") and isinstance(v, dict)]
    counted = re.search(r"\((\d+) records read\)", of_main["gate"])
    check("the number of records that gate says it read is the number of earlier stages' records the section lists among its inputs, and each of those is one of the records read here "
          "(so each carries that one version)", bool(counted) and int(counted.group(1)) == len(read) > 0 and all(p in shown for p in read),
          f"the gate: {of_main['gate'][-20:]!r}; inputs of the section: {len(read)}; not among the records read here: {[p for p in read if p not in shown]}")
    kept = _env_lines(GAP / "environment_before_stage4.txt")
    lists = gate["the main environment's list of packages"]
    same = now is not None and kept is not None and sorted(now) == sorted(kept) and len(set(now)) == len(now)
    in_order = same and now == kept
    order = "" if not same or in_order else "the two files have the same lines and not in the same order: " + "; ".join(
        f"line {i}: {a} / {b}" for i, (a, b) in enumerate(zip(now, kept), 1) if a != b)[:200]
    check("the main environment's list as the gate found it (environment_main_now.txt) is, line for line and in the same order, the list kept before stage 4 installed anything "
          "(environment_before_stage4.txt): the same packages at the same versions, each once, none more and none fewer, each on the line it has in the kept list (the definition: `pip freeze` "
          "as found, in the order printed, line for line the kept list); and their number is the number the gate expected and found and the number the record gives the main environment (`packages`)",
          in_order and re.findall(r"\d+", lists["expected"]) == [str(len(now))] and re.findall(r"\d+", lists["found"]) == [str(len(now))] and main.get("packages") == len(now) and type(main.get("packages")) is int,
          ("a list is not on disk" if now is None or kept is None else
           (order if same else "lines in one list only: " + ", ".join(sorted(set(now) ^ set(kept))[:6])) + f" [{len(now)} lines; the gate expected {lists['expected']!r}, found {lists['found']!r}; the record {main.get('packages')!r}]"))

# ---- part: inputs ---- step 0: inputs_check.csv, district_crosswalk.csv, unit_district.csv and inputs_listing.json, each recomputed from the inputs; and gap.provenance.json held against the files it names ----
_inputs_R620 = "00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv"
_inputs_R620_STATE = "00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv"
_inputs_FRA = "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"
_inputs_UNITS = "10_units/units.gpkg"
_inputs_OUTSIDE = "10_units/outside_village_district.csv"
_inputs_HANSEN = "20_degradation/hansen_loss_by_canopy_band_by_unit.csv"
_inputs_NEED = "30_need/need_by_unit.csv"
_inputs_ASSETS = "40_allocation/assets_district_fy.csv"
_inputs_DECISION = "55_decision/condition_by_unit.csv"
_inputs_TIERS = "55_decision/tiers.csv"
_inputs_REQUIREMENTS = "requirements-stage4.txt"
_inputs_FY = [f"{y}-{y + 1}" for y in range(2014, 2027)]            # R6.20 writes a financial year as 2014-2015
_inputs_PRE, _inputs_POST, _inputs_PART = _inputs_FY[:4], _inputs_FY[4:12], _inputs_FY[12:]
_inputs_RULE = {"ANGUL": "384", "BOLANGIR": "393", "BOUDH": "391", "DEOGARH": "373", "JAJPUR": "382", "SONEPUR": "392"}
_inputs_LOSS_CELLS = ("open_loss", "dense_loss", "little_loss")
_inputs_ANR_CELL = "open_none"
_inputs_LGD, _inputs_OUT = "lgd_panchayat", "outside_village"
_inputs_CODES = [str(c) for c in range(370, 400)]
_inputs_STEP0 = "08_gap_inputs"
_inputs_STEP0_WRITES = ("inputs_listing.json", "district_crosswalk.csv", "unit_district.csv", "inputs_check.csv")
_inputs_DECK, _inputs_ENVIRONMENT_STEP = "08_build_gap_deck_tables", "08_gap_environment"
_inputs_STEPS = (_inputs_STEP0, "08_build_gap_districts", "08_build_gap_panel", "08_build_gap_units", "08_build_gap_rights", "08_build_gap_fsi",
                 _inputs_DECK, _inputs_ENVIRONMENT_STEP)             # the eight builders whose docstrings are the definitions (08_build_gap_fsi, Phase 5b, was added on 11 October 2026)
_inputs_KEPT_LIST = "50_gap/environment_before_stage4.txt"        # the main environment's list kept before stage 4 installed anything: the definition of 08_gap_environment names it, and no step writes it
# The census names the owner wrote beside the six codes of his spelling rule (his instruction of 10 October 2026, Phase 0.1), as he typed them.
_inputs_RULE_NAME = {"ANGUL": "Anugul", "BOLANGIR": "Balangir", "BOUDH": "Baudh", "DEOGARH": "Debagarh", "JAJPUR": "Jajapur", "SONEPUR": "Subarnapur"}
_inputs_SECTION_KEYS = ("script", "script_sha256", "shared_module", "shared_module_sha256", "run_utc", "inputs", "outputs", "package_versions", "environment")
_inputs_ENVIRONMENT_KEYS = ("python", "requirements_file", "requirements_sha256", "packages", "packages_pinned", "differences", "holds_exactly_what_the_file_pins")
_inputs_NAMED_VERSIONS = {"wildboottest": "0.3.2", "numba": "0.62.1", "numpy": "2.3."}     # the owner, 10 October 2026: wildboottest==0.3.2, numba==0.62.1, numpy 2.3.x
# The inputs the owner's instruction of 10 October 2026 names for Phase 0 ("Read these and list each ... with its columns"), by the path each has in the repository.
_inputs_NAMED = (_inputs_R620, _inputs_R620_STATE, _inputs_FRA, "00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv", "00_raw/data_manifest.csv",
                 _inputs_UNITS, _inputs_OUTSIDE, _inputs_HANSEN, "20_degradation/agreement_by_unit.csv", "20_degradation/corestack_by_unit.csv", _inputs_NEED,
                 "40_allocation/allocation_by_unit.csv", "40_allocation/allocation_by_unit_fy.csv", _inputs_DECISION, "docs/DATA_NOTES.md", "scripts/06_build_layer.py")
# The expected value of every gate the owner set, as his instruction of 10 October 2026 gives it (Phase 0: the gate of 0.1, the gate of 0.2, the table of 0.3),
# thousands separators and units apart. The words of a gate are the table's; the value is his. Nothing here is read from the table.
_inputs_OWNER = {
    "0.1 crosswalk: rows": "30",
    "0.1 crosswalk: one R6.20 name to one census code": "yes",
    "0.1 crosswalk: each code from 370 to 399 appears once": "yes",
    "0.1 crosswalk: the R6.20 names that need a spelling rule": ", ".join(sorted(_inputs_RULE)),
    "0.2 units: number of units, each once": "11468",
    "0.2 units: districts": "30",
    "0.2 units: units without a district": "0",
    "R6.20 Plantation expenditure, summed over districts, FY2014-15 to 2017-18, lakh": "151843.18",
    "R6.20 Plantation expenditure, summed over districts, FY2018-19 to 2025-26, lakh": "13915.72",
    "R6.20 Plantation expenditure, summed over districts, FY2026-27 (part year), lakh": "110.58",
    "R6.20 NRM expenditure, summed over districts, FY2014-15 to 2017-18, lakh": "327829.94",
    "R6.20 NRM expenditure, summed over districts, FY2018-19 to 2025-26, lakh": "2334964.06",
    "R6.20 all expenditure: one value of exp_all_lakh per district-year, 390 district-years": "yes",
    "R6.20 all expenditure (exp_all_lakh, one value per district-year), FY2014-15 to 2017-18, lakh": "750836.66",
    "R6.20 all expenditure (exp_all_lakh, one value per district-year), FY2018-19 to 2025-26, lakh": "3674731.26",
    "R6.20: every district-period sum equals the state's printed Total rows (12 sums: 3 categories and all expenditure, 3 periods), largest difference in lakh": "at most 0.01",
    "plantation works, ongoing plus completed, state, FY2016-17": "57135",
    "plantation works, ongoing plus completed, state, FY2025-26": "4105",
    "district-years FY2018-19 to 2025-26 with zero plantation expenditure": "66 of 240",
    "post-period share of state plantation expenditure, the three largest, %": "Rayagada 29.76 / Mayurbhanj 11.40 / Bolangir 6.77",
    "pre-period share of state plantation expenditure, the three largest, %": "Mayurbhanj 20.49 / Rayagada 10.77 / Ganjam 7.64",
    "FRA community titles distributed, ST plus OTFD, state": "9432",
    "FRA community extent, ha": "331568.00",
    "districts that have distributed no community title": "6: Sundargarh, Bhadrak, Kendrapara, Jagatsinghapur, Khordha, Puri",
    "Hansen loss 2001-2025 summed over units and years: dense band / open band, km2": "1552.64 / 363.84",
    "forest loss 2018-2025, dense plus open, summed over units from the per-year table, ha (within 1)": "90028",
    'the same, over units in the three "loss recorded" cells of the default window, ha (within 2)': "89657",
    "standing open-band hectares in the assisted-natural-regeneration cell, default window, ha (within 1)": "293921",
    "units per default-window cell: restore / find the cause first / regeneration candidate / protect / verify on the ground / not a forest site": "406 / 1295 / 3055 / 1040 / 33 / 5639",
    "LGD panchayat units: population / Scheduled Tribe population": "34766888 / 8895006",
}
_inputs_BUILD_MARK = "(a check added by the build)"


def _inputs_header(name):
    """The column names of a table of the folder being checked, as its first line writes them (a name written twice stays twice)."""
    with open(GAP / name, encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def _inputs_present(x):
    """A value read from the GeoPackage as text; a missing one (None, NaN, NA) as the empty text."""
    text = "" if x is None else str(x).strip()
    return "" if text in ("nan", "NaN", "<NA>", "None") else text


def _inputs_twice(values):
    """The values a list holds more than once, sorted."""
    from collections import Counter
    return sorted(v for v, n in Counter(values).items() if n > 1)


def _inputs_whole(t):
    """Every row of a table has a cell for every column and no cell beyond the last column."""
    return all(None not in r and None not in r.values() for r in t)


def _inputs_cell(r, col):
    """A cell as text; a cell or a column that is not there is the empty text."""
    v = r.get(col)
    return "" if v is None else v


def _inputs_text(x):
    """An exact sum as text, never in exponent notation."""
    return format(x, "f")


def _inputs_same(a, b):
    """Two cells are the same: the numbers in them equal as numbers, in the same places (12.5 equals 12.50), and the words between
    the numbers equal as text (the white space at a word's two ends apart)."""
    import re
    pat = re.compile(r"\d+(?:\.\d+)?")
    a, b = str(a).strip(), str(b).strip()
    return ([w.strip() for w in pat.split(a)] == [w.strip() for w in pat.split(b)]
            and [D(x) for x in pat.findall(a)] == [D(x) for x in pat.findall(b)])


def _inputs_met(gate, expected, value):
    """Whether a recomputed value meets a gate's expected value, by the rule the gate itself states."""
    import re
    try:
        within = re.search(r"\(within (\d+(?:\.\d+)?)\)", gate)
        if within:
            return abs(D(value) - D(expected)) <= D(within.group(1))
        if expected.strip().startswith("at most "):
            return D(value) <= D(expected.strip()[len("at most "):])
    except Exception:
        return False
    return _inputs_same(expected, value)


def _inputs_census_names():
    """The names each census district code carries in the Odisha FRA table and in the decision table: two dicts of sets."""
    fra, dec = {}, {}
    for r in rows(_inputs_FRA):
        fra.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"].strip())
    for r in rows(_inputs_DECISION):
        dec.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"].strip())
    return fra, dec


def _inputs_crosswalk(r620_names, name_of):
    """The crosswalk from its definition: {R6.20 name: (census code, census name, match rule)}, and the names that need the rule.
    A name takes the code whose census name equals it once both are upper-cased; failing that, the code of the spelling rule."""
    by_upper = {}
    for code, name in name_of.items():
        by_upper.setdefault(name.upper(), []).append(code)
    out, need_rule = {}, []
    for n in r620_names:
        hit = by_upper.get(n.upper(), [])
        if len(hit) == 1:
            out[n] = (hit[0], name_of[hit[0]], "case-folded census name")
        else:
            need_rule.append(n)
            code = _inputs_RULE.get(n, "")
            out[n] = (code, name_of.get(code, ""), "spelling rule" if code else "")
    return out, sorted(need_rule)


def _inputs_units():
    """Every unit of 10_units/units.gpkg with the district its definition gives it: {unit_id: (level, outside flag, code, from)}.
    An LGD panchayat unit takes the code it carries in the GeoPackage; an outside-village unit the code of its one row in
    outside_village_district.csv. Also returned: the unit ids in the file's order, and the codes that CSV holds for each id."""
    import pyogrio
    df = pyogrio.read_dataframe(ROOT / _inputs_UNITS, read_geometry=False)
    assigned = {}
    for r in rows(_inputs_OUTSIDE):
        assigned.setdefault(r["unit_id"].strip(), []).append(r["pc11_district_code"].strip())
    units, order = {}, []
    for uid, level, flag, code in zip(df["unit_id"], df["unit_level"], df["outside_village"], df["pc11_district_code"]):
        uid, level, flag, code = str(uid).strip(), str(level).strip(), str(int(flag)), _inputs_present(code)
        order.append(uid)
        if level == _inputs_LGD:
            units[uid] = (level, flag, code, "units.gpkg")
        elif level == _inputs_OUT:
            got = assigned.get(uid, [])
            units[uid] = (level, flag, got[0] if len(got) == 1 else "", "outside_village_district.csv")
        else:
            units[uid] = (level, flag, "", "")
    return units, order, assigned


def _inputs_gates(cw, need_rule, units, order, assigned):
    """The `found` value of every gate of inputs_check.csv, recomputed from the inputs and written as the table writes it.
    A gate is keyed by its own words, which are its definition. Returned in six groups, each (what it is about, how its
    values are compared, {gate: found}); and, for the six gates the build added to the owner's, the value each is held
    against, recomputed from the inputs too: {gate: expected}."""
    text = _inputs_text
    build = {}
    # -- 0.1 the crosswalk ------------------------------------------------------------------------------------------------------
    g = {}
    groups = [("0.1 crosswalk", "counts as whole numbers; yes or no, and the list of names, as text", g)]
    codes = [v[0] for v in cw.values()]
    g["0.1 crosswalk: rows"] = str(len(cw))
    g["0.1 crosswalk: one R6.20 name to one census code"] = "yes" if all(codes) and len(set(codes)) == len(cw) else "no"
    g["0.1 crosswalk: each code from 370 to 399 appears once"] = "yes" if sorted(codes) == _inputs_CODES else "no"
    g["0.1 crosswalk: the R6.20 names that need a spelling rule"] = ", ".join(need_rule)
    dump = {}
    for r in rows(_inputs_ASSETS):
        dump.setdefault(r["district_property"].strip(), set()).add(r["pc11_district_code"].strip())
    k = "0.1 crosswalk: same code as the geotagged record's district table, for the 30 R6.20 names it carries (a check added by the build)"
    g[k] = str(sum(1 for n, v in cw.items() if dump.get(n) == {v[0]}))
    build[k] = str(sum(1 for n in cw if n in dump))                 # held against: the R6.20 names that table carries
    # -- 0.2 the units ------------------------------------------------------------------------------------------------------------
    g = {}
    groups.append(("0.2 units", "counts as whole numbers", g))
    dec = {}
    for r in rows(_inputs_DECISION):
        dec.setdefault(r["unit_id"].strip(), []).append(r)
    g["0.2 units: number of units, each once"] = str(len(units)) if len(units) == len(order) else f"{len(order)} rows, {len(units)} distinct"
    g["0.2 units: districts"] = str(len({v[2] for v in units.values() if v[2]}))
    g["0.2 units: units without a district"] = str(sum(1 for v in units.values() if not v[2]))
    k = "0.2 units: outside-village units, each with a row in outside_village_district.csv (a check added by the build)"
    g[k] = str(sum(1 for u, v in units.items() if v[0] == _inputs_OUT and len(assigned.get(u, [])) == 1))
    build[k] = str(sum(1 for v in units.values() if v[0] == _inputs_OUT))             # held against: the outside-village units of units.gpkg
    k = "0.2 units: units whose district equals the decision table's (a check added by the build)"
    g[k] = str(sum(1 for u, v in units.items() if v[2] and len(dec.get(u, [])) == 1 and dec[u][0]["pc11_district_code"].strip() == v[2]))
    build[k] = str(len(units))                                      # held against: the units of units.gpkg
    # -- R6.20: lakh rupees, two decimals, added exactly ------------------------------------------------------------------------------
    g = {}
    groups.append(("R6.20", "sums of lakh rupees exactly, as numbers; counts; yes or no as text; the three largest shares rounded half up to 2 decimals, beside the R6.20 names in title case", g))
    r620 = rows(_inputs_R620)
    districts = sorted({r["district"] for r in r620})
    periods = {"FY2014-15 to 2017-18": _inputs_PRE, "FY2018-19 to 2025-26": _inputs_POST, "FY2026-27 (part year)": _inputs_PART}
    cat_sum, all_cells, works = {}, {}, {}                          # by (category, district, year); exp_all_lakh by (district, year)
    for r in r620:
        k = (r["category"], r["district"], r["fy"])
        cat_sum[k] = cat_sum.get(k, D(0)) + D(r["exp_cat_lakh"])
        all_cells.setdefault((r["district"], r["fy"]), []).append(D(r["exp_all_lakh"]))
        works[k] = works.get(k, 0) + int(r["works_ongoing"]) + int(r["works_completed"])
    one_value = len(all_cells) == 390 and all(len(v) == 3 and len(set(v)) == 1 for v in all_cells.values())

    def dsum(cat, fys, district=None):
        ds = districts if district is None else [district]
        if cat == "all":
            return sum((all_cells[(d, f)][0] for d in ds for f in fys), D(0))
        return sum((cat_sum.get((cat, d, f), D(0)) for d in ds for f in fys), D(0))

    for label, fys in periods.items():
        g[f"R6.20 Plantation expenditure, summed over districts, {label}, lakh"] = text(dsum("Plantation", fys))
    for label, fys in list(periods.items())[:2]:
        g[f"R6.20 NRM expenditure, summed over districts, {label}, lakh"] = text(dsum("NRM", fys))
        g[f"R6.20 all expenditure (exp_all_lakh, one value per district-year), {label}, lakh"] = text(dsum("all", fys))
    g["R6.20 all expenditure: one value of exp_all_lakh per district-year, 390 district-years"] = "yes" if one_value else "no"
    st_cat, st_all = {}, {}
    for r in rows(_inputs_R620_STATE):
        st_cat[(r["category"], r["fy"])] = st_cat.get((r["category"], r["fy"]), D(0)) + D(r["exp_cat_lakh"])
        st_all.setdefault(r["fy"], []).append(D(r["exp_all_lakh"]))
    st_one = sorted(st_all) == _inputs_FY and all(len(v) == 3 and len(set(v)) == 1 for v in st_all.values())
    diffs = []
    for fys in periods.values():
        for cat in ("Plantation", "NRM", "Water"):
            diffs.append(abs(dsum(cat, fys) - sum((st_cat[(cat, f)] for f in fys), D(0))))
        diffs.append(abs(dsum("all", fys) - sum((st_all[f][0] for f in fys), D(0))))
    g["R6.20: every district-period sum equals the state's printed Total rows (12 sums: 3 categories and all expenditure, 3 periods), largest difference in lakh"] = text(max(diffs))
    k = "R6.20 state totals: exp_all_lakh the same on the three category rows of a year (a check added by the build)"
    g[k] = "yes" if st_one else "no"
    build[k] = "yes"
    for label, fy in (("FY2016-17", "2016-2017"), ("FY2025-26", "2025-2026")):
        g[f"plantation works, ongoing plus completed, state, {label}"] = str(sum(works[("Plantation", d, fy)] for d in districts))
    zero = sum(1 for d in districts for f in _inputs_POST if cat_sum[("Plantation", d, f)] == 0)
    g["district-years FY2018-19 to 2025-26 with zero plantation expenditure"] = f"{zero} of {len(districts) * len(_inputs_POST)}"
    for word, fys in (("post", _inputs_POST), ("pre", _inputs_PRE)):
        total = dsum("Plantation", fys)
        share = sorted(((D(100) * dsum("Plantation", fys, d) / total, d) for d in districts), key=lambda s: (-s[0], s[1]))
        g[f"{word}-period share of state plantation expenditure, the three largest, %"] = " / ".join(f"{d.title()} {q(s, '0.01')}" for s, d in share[:3])
    # -- forest rights ---------------------------------------------------------------------------------------------------------------
    g = {}
    groups.append(("forest rights", "the titles as a whole number; the extent as an exact sum; the districts with no title as text, in the file's order", g))
    fra = rows(_inputs_FRA)
    titles = [(r["district"].strip(), int(r["titles_distributed_comm_st"]) + int(r["titles_distributed_comm_otfd"])) for r in fra]
    none = [n for n, k in titles if k == 0]
    g["FRA community titles distributed, ST plus OTFD, state"] = str(sum(k for _, k in titles))
    g["FRA community extent, ha"] = text(sum((D(r["extent_ha_comm_st"]) + D(r["extent_ha_comm_otfd"]) for r in fra), D(0)))
    g["districts that have distributed no community title"] = f"{len(none)}: " + ", ".join(none)
    # -- Hansen's yearly loss and the decision table: hectares, four decimals, added exactly ------------------------------------------
    g = {}
    groups.append(("Hansen's yearly loss and the decision table", "sums of hectares exactly, as numbers; km2 = hectares / 100 rounded half up to 2 decimals; the six counts of units", g))
    cell = {u: v[0]["cell_2018_2025"].strip() for u, v in dec.items()}
    dense = opn = loss_all = loss_cells = D(0)
    for r in rows(_inputs_HANSEN):
        dense += sum((D(r[f"loss_ha_gt30_{y}"]) for y in range(2001, 2026)), D(0))
        opn += sum((D(r[f"loss_ha_gt10le30_{y}"]) for y in range(2001, 2026)), D(0))
        w = sum((D(r[f"loss_ha_gt30_{y}"]) + D(r[f"loss_ha_gt10le30_{y}"]) for y in range(2018, 2026)), D(0))
        loss_all += w
        if cell.get(r["unit_id"].strip()) in _inputs_LOSS_CELLS:
            loss_cells += w
    g["Hansen loss 2001-2025 summed over units and years: dense band / open band, km2"] = f"{q(dense / 100, '0.01')} / {q(opn / 100, '0.01')}"
    g["forest loss 2018-2025, dense plus open, summed over units from the per-year table, ha (within 1)"] = text(loss_all)
    g['the same, over units in the three "loss recorded" cells of the default window, ha (within 2)'] = text(loss_cells)
    k = "forest loss 2018-2025: the decision table's own column summed equals the per-year table's sum (a check added by the build)"
    g[k] = text(sum((D(v[0]["forest_loss_ha_2018_2025"]) for v in dec.values()), D(0)))
    build[k] = text(loss_all)                                       # held against: the per-year table's sum
    g["standing open-band hectares in the assisted-natural-regeneration cell, default window, ha (within 1)"] = text(
        sum((D(v[0]["standing_open_ha"]) for v in dec.values() if v[0]["cell_2018_2025"].strip() == _inputs_ANR_CELL), D(0)))
    words = ["restore", "find the cause first", "regeneration candidate", "protect", "verify on the ground", "not a forest site"]
    tiers = rows(_inputs_TIERS)
    counts = []
    for w in words:                                                  # each word of the gate names one cell: the one whose full name ends in it
        hit = [k["cell"].strip() for k in tiers if k["cell_name"].strip().lower().endswith(w)]
        counts.append(str(sum(1 for c in cell.values() if c == hit[0])) if len(hit) == 1 else "?")
    g["units per default-window cell: " + " / ".join(words)] = " / ".join(counts)
    # -- the need table -----------------------------------------------------------------------------------------------------------------
    g = {}
    groups.append(("the need table", "two sums and a count of whole numbers", g))
    lgd = [r for r in rows(_inputs_NEED) if r["unit_level"].strip() == _inputs_LGD]
    g["LGD panchayat units: population / Scheduled Tribe population"] = f"{sum(int(r['population']) for r in lgd)} / {sum(int(r['st_pop']) for r in lgd)}"
    k = "LGD panchayat units in the need table (a check added by the build)"
    g[k] = str(len(lgd))
    build[k] = str(sum(1 for v in units.values() if v[0] == _inputs_LGD))             # held against: the LGD panchayat units of units.gpkg
    return groups, build


def _inputs_norm(name):
    """A package name as the index normalises it: lower case, a run of hyphens, underscores and dots as one hyphen."""
    import re
    return re.sub(r"[-_.]+", "-", str(name)).lower()


def _inputs_pins():
    """requirements-stage4.txt: its lines `name==version` as {normalised name: version}, comments apart; the other lines it has
    (one that is neither, or a name pinned twice); and the SHA-256 of the file."""
    import hashlib
    import re
    raw = (ROOT / _inputs_REQUIREMENTS).read_bytes()
    pins, other = {}, []
    for line in raw.decode("utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s=;,]+)", line)
        if not m or _inputs_norm(m.group(1)) in pins:
            other.append(line)
            continue
        pins[_inputs_norm(m.group(1))] = m.group(2)
    return pins, other, hashlib.sha256(raw).hexdigest()


def _inputs_held():
    """What the interpreter running this script holds, pip apart: {normalised name: version}."""
    import importlib.metadata
    held = {}
    for d in importlib.metadata.distributions():
        name = d.metadata["Name"]
        if name and _inputs_norm(name) != "pip":
            held[_inputs_norm(name)] = d.version
    return held


def _inputs_file(path):
    """The size in bytes and the SHA-256 of a file named by its path in the repository; (None, None) where the path leaves the
    repository or there is no such file."""
    import hashlib
    p = Path(str(path))
    if p.is_absolute() or ".." in p.parts or not (ROOT / p).is_file():
        return None, None
    h, n = hashlib.sha256(), 0
    with open(ROOT / p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
            n += len(block)
    return n, h.hexdigest()


def _inputs_shape(path):
    """What a listing can say of an input's rows and columns. A CSV: its column names as its first line writes them and the number
    of its rows, the header and empty lines apart. The GeoPackage: the attribute fields of its layer, its features, its geometry
    type and its reference system. Any other file is not a table: no columns and no rows."""
    if str(path).endswith(".csv"):
        with open(ROOT / path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            return {"columns": header, "rows": sum(1 for row in reader if row)}
    if str(path).endswith(".gpkg"):
        import pyogrio
        info = pyogrio.read_info(ROOT / path)
        return {"columns": [str(x) for x in info["fields"]], "rows": int(info["features"]), "geometry": info["geometry_type"], "crs": info["crs"]}
    return {"columns": None, "rows": None}


def _inputs_utc(text):
    """True for a time written YYYY-MM-DDTHH:MM:SSZ that is a date and a time of day."""
    import datetime
    try:
        datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
        return len(text) == 20
    except Exception:
        return False


def _inputs_json(name):
    """A JSON file of the folder being checked; None if it is not there or cannot be read as JSON."""
    try:
        return json.loads((GAP / name).read_text(encoding="utf-8"))
    except Exception:
        return None


def _inputs_environment(sec, pins, pins_sha):
    """What is wrong with one section's `environment` and `package_versions`, held against requirements-stage4.txt: a list of
    words, empty if nothing is."""
    import platform
    env, versions, wrong = sec.get("environment"), sec.get("package_versions"), []
    if not isinstance(env, dict):
        return ["no `environment`"]
    if sorted(env) != sorted(_inputs_ENVIRONMENT_KEYS):
        wrong.append(f"its keys are {sorted(env)}")
    if env.get("python") != platform.python_version():
        wrong.append(f"python {env.get('python')!r}, this interpreter is {platform.python_version()}")
    if env.get("requirements_file") != _inputs_REQUIREMENTS:
        wrong.append(f"requirements_file {env.get('requirements_file')!r}")
    if env.get("requirements_sha256") != pins_sha:
        wrong.append(f"requirements_sha256 {str(env.get('requirements_sha256'))[:12]}..., the file's is {pins_sha[:12]}...")
    packages = env.get("packages") if isinstance(env.get("packages"), dict) else {}
    recorded = {_inputs_norm(k): v for k, v in packages.items()}
    if len(recorded) != len(packages) or recorded != pins:
        odd = sorted(k for k in set(recorded) | set(pins) if recorded.get(k) != pins.get(k))
        wrong.append("packages differ from the pins: " + ", ".join(f"{k} {recorded.get(k)} (pinned {pins.get(k)})" for k in odd[:4]))
    if env.get("packages_pinned") != len(pins) or isinstance(env.get("packages_pinned"), bool):
        wrong.append(f"packages_pinned {env.get('packages_pinned')!r}, the file pins {len(pins)}")
    if env.get("differences") != []:
        wrong.append(f"differences {env.get('differences')!r}")
    if env.get("holds_exactly_what_the_file_pins") is not True:
        wrong.append(f"holds_exactly_what_the_file_pins {env.get('holds_exactly_what_the_file_pins')!r}")
    if not isinstance(versions, dict) or not versions:
        wrong.append("no `package_versions`")
    else:
        for k, v in versions.items():
            want = env.get("python") if k == "python" else recorded.get(_inputs_norm(k))
            if want is None or v != want:
                wrong.append(f"package_versions {k} {v!r}, its `environment` says {want!r}")
    return wrong


def part_inputs():
    cell = _inputs_cell
    # ---- the district crosswalk ----------------------------------------------------------------------------------------------------
    T = "district_crosswalk.csv"
    r620_names = sorted({r["district"] for r in rows(_inputs_R620)})
    fra_names, dec_names = _inputs_census_names()
    ok = (sorted(fra_names) == _inputs_CODES and sorted(dec_names) == _inputs_CODES
          and all(len(fra_names[c]) == 1 and fra_names[c] == dec_names[c] for c in _inputs_CODES))
    check("inputs: the Odisha FRA table and the decision table each carry the census codes 370 to 399 and no other, and one and the same district name for each",
          ok, "" if ok else "; ".join(f"{c}: FRA {sorted(fra_names.get(c, []))}, decision {sorted(dec_names.get(c, []))}"
                                      for c in sorted(set(_inputs_CODES) | set(fra_names) | set(dec_names))
                                      if len(fra_names.get(c, [])) != 1 or fra_names.get(c) != dec_names.get(c))[:400])
    name_of = {c: sorted(v)[0] for c, v in fra_names.items() if v}
    cw, need_rule = _inputs_crosswalk(r620_names, name_of)
    ok = need_rule == sorted(_inputs_RULE) and len(cw) == 30 and sorted(v[0] for v in cw.values()) == _inputs_CODES
    check("recomputed crosswalk: of the 30 district names of R6.20, those that fail the case-folded match with a census name are exactly the six of the owner's spelling rule (ANGUL, BOLANGIR, BOUDH, DEOGARH, JAJPUR, SONEPUR); the 30 names take the codes 370 to 399, each once",
          ok, "" if ok else f"names needing the rule: {need_rule}; names: {len(cw)}; distinct codes: {len({v[0] for v in cw.values()})}")
    t, cols = table(T), _inputs_header(T)
    keys = [cell(r, "r620_district") for r in t]
    tcodes = [cell(r, "pc11_district_code") for r in t]
    ok = (len(t) == 30 and cols == ["r620_district", "pc11_district_code", "district_name", "match_rule"] and _inputs_whole(t)
          and sorted(keys) == r620_names and sorted(tcodes) == _inputs_CODES)
    check(f"{T}: 30 rows; columns r620_district, pc11_district_code, district_name, match_rule, a cell for each on every row; its R6.20 names are the 30 distinct `district` values of the R6.20 district file, none twice; each census code 370 to 399 once",
          ok, "" if ok else f"rows {len(t)}; columns {cols}; names not in R6.20 {sorted(set(keys) - set(r620_names))}; R6.20 names missing {sorted(set(r620_names) - set(keys))}; "
          f"names twice {_inputs_twice(keys)}; codes missing {sorted(set(_inputs_CODES) - set(tcodes))}; codes twice {_inputs_twice(tcodes)}")
    none = ("", "", "")
    for j, (col, what) in enumerate((("pc11_district_code", "the code of the census name that equals the R6.20 name once both are upper-cased, else the code the owner's spelling rule gives the name"),
                                     ("district_name", "the name the Odisha FRA table and the decision table carry for the recomputed code"),
                                     ("match_rule", "`case-folded census name` where the upper-cased names are equal, `spelling rule` for the six that are not"))):
        pairs = [(cell(r, "r620_district"), cell(r, col), cw.get(cell(r, "r620_district"), none)[j], cell(r, col) == cw.get(cell(r, "r620_district"), none)[j]) for r in t]
        check(f"{T}: {col} = {what}; every row, as text", bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    by_name = {cell(r, "r620_district"): r for r in t}
    pairs = []
    for n in sorted(_inputs_RULE):                                  # the rule as the owner typed it, code and census name: held against the table, not against another table
        mine = tuple(cell(by_name.get(n, {}), c) for c in ("pc11_district_code", "district_name", "match_rule"))
        his = (_inputs_RULE[n], _inputs_RULE_NAME[n], "spelling rule")
        pairs.append((n, "/".join(mine), "/".join(his), n in by_name and mine == his))
    check(f"{T}: the owner's spelling rule of 10 October 2026 as he wrote it, code and census name: the rows of ANGUL, BOLANGIR, BOUDH, DEOGARH, JAJPUR and SONEPUR carry 384 Anugul, 393 Balangir, 391 Baudh, 373 Debagarh, "
          "382 Jajapur and 392 Subarnapur, each with match_rule `spelling rule`; as text (the six codes and names are held here as he typed them, not read from a table)",
          len(pairs) == 6 and all(p[3] for p in pairs), mismatches(pairs))
    dump = {}
    for r in rows(_inputs_ASSETS):
        dump.setdefault(r["district_property"].strip(), set()).add(r["pc11_district_code"].strip())
    pairs = [(cell(r, "r620_district"), cell(r, "pc11_district_code"), "/".join(sorted(dump.get(cell(r, "r620_district"), []))), dump.get(cell(r, "r620_district")) == {cell(r, "pc11_district_code")}) for r in t]
    check(f"{T}: pc11_district_code = the one code the geotagged record's own table of districts (40_allocation/assets_district_fy.csv) carries for the R6.20 name as its district_property; every row, as text "
          "(a second source for the code, not the rule: that table carries all 30 names)", bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))

    # ---- a district for every unit ----------------------------------------------------------------------------------------------------
    T = "unit_district.csv"
    units, order, assigned = _inputs_units()
    ok = all((v[0] == _inputs_OUT) == (v[1] == "1") and v[0] in (_inputs_LGD, _inputs_OUT) and v[1] in ("0", "1") for v in units.values())
    check("inputs: every unit of 10_units/units.gpkg is `lgd_panchayat` with outside_village 0 or `outside_village` with outside_village 1", ok,
          "" if ok else str([(u, v[0], v[1]) for u, v in units.items() if (v[0] == _inputs_OUT) != (v[1] == "1") or v[0] not in (_inputs_LGD, _inputs_OUT)][:3]))
    t, cols = table(T), _inputs_header(T)
    ids = [cell(r, "unit_id") for r in t]
    ok = (len(t) == 11468 and cols == ["unit_id", "unit_level", "outside_village", "pc11_district_code", "district_name", "district_from"] and _inputs_whole(t)
          and len(set(ids)) == len(ids) and len(order) == len(units) == 11468 and set(ids) == set(units))
    check(f"{T}: 11,468 rows; columns unit_id, unit_level, outside_village, pc11_district_code, district_name, district_from, a cell for each on every row; no unit_id twice; its unit ids are those of 10_units/units.gpkg, which holds each once",
          ok, "" if ok else f"rows {len(t)}; columns {cols}; ids twice {len(ids) - len(set(ids))}, e.g. {_inputs_twice(ids)[:3]}; "
          f"in the table and not in units.gpkg {len(set(ids) - set(units))}, e.g. {sorted(set(ids) - set(units))[:3]}; "
          f"in units.gpkg and not in the table {len(set(units) - set(ids))}, e.g. {sorted(set(units) - set(ids))[:3]}; units.gpkg rows {len(order)}, distinct {len(units)}")
    none = ("", "", "", "")
    for col, j, what in (("unit_level", 0, "unit_level of units.gpkg"), ("outside_village", 1, "outside_village of units.gpkg"),
                         ("pc11_district_code", 2, "the code the unit carries in units.gpkg (an LGD panchayat unit) or the code of its row in outside_village_district.csv (an outside-village unit)"),
                         ("district_from", 3, "`units.gpkg` for an LGD panchayat unit, `outside_village_district.csv` for an outside-village unit")):
        pairs = [(cell(r, "unit_id"), cell(r, col), units.get(cell(r, "unit_id"), none)[j], cell(r, col) == units.get(cell(r, "unit_id"), none)[j]) for r in t]
        check(f"{T}: {col} = {what}; every row, as text", bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    pairs = [(cell(r, "unit_id"), cell(r, "district_name"), name_of.get(units.get(cell(r, "unit_id"), none)[2], ""),
              cell(r, "district_name") == name_of.get(units.get(cell(r, "unit_id"), none)[2], "")) for r in t]
    check(f"{T}: district_name = the name the Odisha FRA table and the decision table carry for the unit's recomputed code; every row, as text",
          bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    second = {}                                                     # the decision table's own columns for each unit: a second source
    for r in rows(_inputs_DECISION):
        second.setdefault(r["unit_id"].strip(), []).append((r["unit_level"].strip(), r["outside_village"].strip(), r["pc11_district_code"].strip(), r["district"].strip()))
    pairs = []
    for r in t:
        mine = (cell(r, "unit_level"), cell(r, "outside_village"), cell(r, "pc11_district_code"), cell(r, "district_name"))
        theirs = second.get(cell(r, "unit_id"), [])
        pairs.append((cell(r, "unit_id"), "/".join(mine), " or ".join("/".join(x) for x in theirs), theirs == [mine]))
    n_d = len({cell(r, "pc11_district_code") for r in t})
    n_blank = sum(1 for r in t if not cell(r, "pc11_district_code").strip())
    ok = bool(pairs) and all(p[3] for p in pairs) and n_d == 30 and n_blank == 0
    check(f"{T}: no unit without a district code; 30 distinct codes; from a second source, the decision table (55_decision/condition_by_unit.csv, which has one row for the unit): "
          "every unit's unit_level, outside_village, pc11_district_code and district_name = its unit_level, outside_village, pc11_district_code and district there, as text",
          ok, "" if ok else f"distinct codes {n_d}; units without a code {n_blank}; " + mismatches(pairs))

    # ---- the gates on what is already built -------------------------------------------------------------------------------------------
    T = "inputs_check.csv"
    groups, build = _inputs_gates(cw, need_rule, units, order, assigned)
    found = {gate: value for _, _, g in groups for gate, value in g.items()}
    t, cols = table(T), _inputs_header(T)
    gates = [cell(r, "gate") for r in t]
    row_of = {cell(r, "gate"): r for r in t}
    ok = cols == ["gate", "expected", "found", "pass"] and _inputs_whole(t) and len(set(gates)) == len(gates) and set(gates) == set(found)
    check(f"{T}: {len(found)} rows; columns gate, expected, found, pass, a cell for each on every row; no gate twice; its gates are exactly the {len(found)} this part recomputes (a gate it has no recomputation for fails here)",
          ok, "" if ok else f"rows {len(t)}; columns {cols}; gates twice: {_inputs_twice(gates)[:3]}; "
          f"gates not recomputed here: {sorted(set(gates) - set(found))[:3]}; gates missing from the table: {sorted(set(found) - set(gates))[:3]}")
    for label, how, g in groups:
        pairs = [(gate, cell(row_of[gate], "found") if gate in row_of else None, value, gate in row_of and _inputs_same(cell(row_of[gate], "found"), value)) for gate, value in g.items()]
        check(f"{T}: `found` of the {len(g)} gates on {label} = the value recomputed from the inputs ({how}); a gate that is not in the table fails", all(p[3] for p in pairs), mismatches(pairs))
    bad = [(cell(r, "gate"), cell(r, "pass")) for r in t if cell(r, "pass") != "yes"]
    check(f"{T}: pass = yes on every row of the table", bool(t) and not bad, "" if not bad else f"{len(bad)} of {len(t)} not yes, e.g. {bad[:3]}")
    owner = _inputs_OWNER
    split = not (set(owner) & set(build)) and set(owner) | set(build) == set(found) and set(build) == {g for g in found if _inputs_BUILD_MARK in g}
    pairs = [(gate, cell(row_of[gate], "expected") if gate in row_of else None, value, gate in row_of and _inputs_same(cell(row_of[gate], "expected"), value)) for gate, value in owner.items()]
    check(f"{T}: `expected` of the {len(owner)} gates the owner set = the value his instruction of 10 October 2026 gives (Phase 0: the gate of 0.1, the gate of 0.2 and the table of 0.3), which this script holds as he wrote it, "
          "thousands separators and units apart; numbers as numbers, words as text; no tolerance applies to this column; the gates he set are those not marked `a check added by the build`",
          split and all(p[3] for p in pairs), ("" if split else "the gates held here as the owner's and as the build's are not, together, the gates recomputed; ") + mismatches(pairs))
    pairs = [(gate, cell(row_of[gate], "expected") if gate in row_of else None, value, gate in row_of and _inputs_same(cell(row_of[gate], "expected"), value)) for gate, value in build.items()]
    check(f"{T}: `expected` of the {len(build)} gates marked `a check added by the build` = what each holds its count or sum against, recomputed from the inputs: the R6.20 names the geotagged record's district table carries; "
          "the outside-village units, all the units and the LGD panchayat units of units.gpkg; `yes`; the forest loss of 2018 to 2025 summed from the per-year Hansen table; numbers as numbers",
          split and bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    pairs = [(gate, cell(row_of[gate], "expected") if gate in row_of else None, value, gate in row_of and _inputs_met(gate, cell(row_of[gate], "expected"), value)) for gate, value in found.items()]
    check(f"{T}: `expected` of each of the {len(found)} gates is met by the value recomputed from the inputs, by the gate's own rule (within the number the gate's name gives, where it says `(within 1)` or `(within 2)`; "
          "no more than the number, where the expected value reads `at most` a number; otherwise equal: numbers as numbers, words as text)", all(p[3] for p in pairs), mismatches(pairs))
    k = "forest loss 2018-2025: the decision table's own column summed equals the per-year table's sum (a check added by the build)"
    ok = D(found[k]) == D(build[k])
    check("inputs: forest_loss_ha_2018_2025 of the decision table summed over units = the dense plus open loss of 2018 to 2025 summed over units from the per-year Hansen table, exactly",
          ok, "" if ok else f"decision table {found[k]}, per-year table {build[k]}")

    # ---- the listing of the inputs ------------------------------------------------------------------------------------------------------
    T = "inputs_listing.json"
    listing = _inputs_json(T)
    entries = listing.get("inputs") if isinstance(listing, dict) else None
    entries = [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else []
    paths = [e.get("path") for e in entries]
    names = [e.get("key") for e in entries]
    ok = (isinstance(listing, dict) and sorted(listing) == ["inputs", "run_utc"] and _inputs_utc(listing.get("run_utc")) and isinstance(listing.get("inputs"), list)
          and len(entries) == len(listing["inputs"]) > 0 and all(isinstance(x, str) and x for x in paths + names) and len(set(paths)) == len(paths) and len(set(names)) == len(names))
    check(f"{T}: a `run_utc` written YYYY-MM-DDTHH:MM:SSZ and a list `inputs` of entries, each with a `key` and a `path`, no key and no path twice", ok,
          "" if ok else f"keys {sorted(listing) if isinstance(listing, dict) else None}; run_utc {listing.get('run_utc') if isinstance(listing, dict) else None!r}; entries {len(entries)}; "
          f"keys twice {_inputs_twice([str(x) for x in names])}; paths twice {_inputs_twice([str(x) for x in paths])}")
    pairs = []
    for e in entries:
        path = str(e.get("path"))
        size, sha = _inputs_file(path)
        if size is None:
            pairs.append((path, "listed", "no such file in the repository", False))
            continue
        shape = _inputs_shape(path)
        mine = dict(key=e.get("key"), path=path, bytes=size, sha256=sha, **shape)
        odd = sorted(k for k in set(e) | set(mine) if k not in e or k not in mine or type(e[k]) is not type(mine[k]) or e[k] != mine[k])
        pairs.append((path, {k: e.get(k) for k in odd}, {k: mine.get(k) for k in odd}, not odd))
    check(f"{T}: every entry names a file of the repository and gives its `bytes` and `sha256` as they are now, and of a table its `rows` and `columns`: for a CSV the names of its first line, in order, and the number of rows "
          "after it (empty lines apart); for the GeoPackage the attribute fields of its layer, its features, and its `geometry` type and `crs`; for a file that is not a table, null for both; no other field; exactly",
          bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    missing = [p for p in _inputs_NAMED if p not in paths]
    check(f"{T}: lists each of the {len(_inputs_NAMED)} inputs the owner's instruction of 10 October 2026 names for Phase 0 (the two R6.20 files, the two FRA tables, the manifest, units.gpkg, outside_village_district.csv, "
          "the per-year Hansen table by canopy band, the agreement and CoRE Stack tables by unit, the need table, the two allocation tables by unit, the decision table, docs/DATA_NOTES.md and the layer's builder)",
          not missing, "" if not missing else f"not listed: {missing}")
    record = _inputs_json("gap.provenance.json")
    steps = record.get("steps") if isinstance(record, dict) else None
    steps = {k: v for k, v in steps.items() if isinstance(v, dict)} if isinstance(steps, dict) else {}
    read = {}                                                       # every file a step records as an input: {path: the steps that read it}
    for name, sec in steps.items():
        for v in (sec.get("inputs") if isinstance(sec.get("inputs"), dict) else {}).values():
            if isinstance(v, dict) and isinstance(v.get("path"), str):
                read.setdefault(v["path"], []).append(name)
    unlisted = sorted(p for p in read if not p.startswith("50_gap/") and p not in paths)
    check(f"{T}: \"every input this stage reads\": every file that a step of the stage records as an input in gap.provenance.json is listed, the files of 50_gap/ apart (the stage's own folder: "
          "what a step reads from it is held further down, against what the steps record writing)",
          bool(read) and not unlisted, "" if read and not unlisted else f"{len(unlisted)} of the {len([p for p in read if not p.startswith('50_gap/')])} files the steps record are not listed: "
          + "; ".join(f"{p} (read by {', '.join(sorted(set(read[p])))})" for p in unlisted) if read else "no step records an input")

    # ---- the record of provenance: every section against the files it names, and step 0's against what step 0 wrote ------------------------
    T = "gap.provenance.json"
    wrong = [] if steps else ["no `steps`"]
    wrong += [f"no section {name}" for name in _inputs_STEPS if name not in steps]
    for name, sec in steps.items():
        gone = [k for k in _inputs_SECTION_KEYS if k not in sec]
        if gone:
            wrong.append(f"{name}: no {', '.join(gone)}")
        if sec.get("script") != f"scripts/{name}.py" or sec.get("shared_module") != "scripts/_gap_common.py":
            wrong.append(f"{name}: script {sec.get('script')!r}, shared_module {sec.get('shared_module')!r}")
        if not _inputs_utc(sec.get("run_utc")):
            wrong.append(f"{name}: run_utc {sec.get('run_utc')!r}")
        for k in ("script_sha256", "shared_module_sha256"):
            if not (isinstance(sec.get(k), str) and len(sec[k]) == 64 and set(sec[k]) <= set("0123456789abcdef")):
                wrong.append(f"{name}: {k} is not 64 hexadecimal digits")
        ins, outs = sec.get("inputs"), sec.get("outputs")
        if not isinstance(ins, dict) or not ins or any(not isinstance(v, dict) or sorted(v) != ["bytes", "path", "sha256"] for v in ins.values()):
            wrong.append(f"{name}: `inputs` is not a set of entries with path, bytes and sha256")
        if not isinstance(outs, dict) or not outs or any(not isinstance(v, dict) or sorted(v) != ["bytes", "sha256"] for v in outs.values()):
            wrong.append(f"{name}: `outputs` is not a set of paths with bytes and sha256")
    check(f"{T}: a section for each of the eight builders ({', '.join(_inputs_STEPS)}); every section names its script scripts/<section>.py and the shared module scripts/_gap_common.py, and gives each 64 hexadecimal digits as its SHA-256 "
          "(this check holds their form only; the part on the environments holds the digits against the two files, which it hashes and does not read), a `run_utc` written YYYY-MM-DDTHH:MM:SSZ, `inputs` (each with path, bytes, sha256), `outputs` (each a path with bytes, sha256), `package_versions` and `environment`", not wrong, "; ".join(wrong[:4]))
    for kind in ("inputs", "outputs"):
        pairs = []
        for name, sec in steps.items():
            for k, v in (sec.get(kind) if isinstance(sec.get(kind), dict) else {}).items():
                path = v.get("path") if kind == "inputs" and isinstance(v, dict) else k
                size, sha = _inputs_file(path)
                said = (v.get("bytes"), v.get("sha256")) if isinstance(v, dict) else (None, None)
                pairs.append((f"{name}: {path}", f"{said[0]} bytes, {str(said[1])[:12]}...", "no such file in the repository" if size is None else f"{size} bytes, {sha[:12]}...",
                              size is not None and said == (size, sha) and not isinstance(said[0], bool)))
        check(f"{T}: in every section, each of the `{kind}` is recorded by its path in the repository, and the file at that path now has the recorded `bytes` and `sha256`, exactly "
              + ("(an input changed since a step ran fails here)" if kind == "inputs" else "(a table changed since its step wrote it fails here; with --tables, the record of that folder is held against the repository's files, by the paths it gives)"),
              bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    written = {}                                                    # every file a section records as an output: {path: the sections that record it}
    for name, sec in steps.items():
        for k in (sec.get("outputs") if isinstance(sec.get("outputs"), dict) else {}):
            written.setdefault(str(k), []).append(name)
    wrong, own = [], 0
    for path, names in sorted(written.items()):
        if len(names) > 1:
            wrong.append(f"{path} is recorded as an output by {', '.join(names)}")
        for name in names:
            folder = "50_gap/deck_tables/" if name == _inputs_DECK else "50_gap/"
            if not path.startswith(folder) or not path[len(folder):] or "/" in path[len(folder):]:
                wrong.append(f"{name}: its output {path} is not recorded by a path directly in {folder}")
    for name, sec in steps.items():
        for v in (sec.get("inputs") if isinstance(sec.get("inputs"), dict) else {}).values():
            path = v.get("path") if isinstance(v, dict) else None
            if not isinstance(path, str) or not path.startswith("50_gap/"):
                continue
            own += 1
            if [w for w in written.get(path, []) if w != name]:
                continue
            if not (path == _inputs_KEPT_LIST and name == _inputs_ENVIRONMENT_STEP):
                wrong.append(f"{name}: its input {path} is not a file another section records as its output")
    if not own:
        wrong.append("no section records an input from 50_gap/")
    check(f"{T}: what the stage reads of its own. Each of the `outputs` of a section is recorded by a path directly in 50_gap/ (of {_inputs_DECK}: directly in 50_gap/deck_tables/), and none is recorded by two sections; "
          "and each of the `inputs` of a section that lies in 50_gap/ is, by the same path, a file another section records as its output. One input alone is let through without a section that wrote it: "
          f"{_inputs_KEPT_LIST}, as an input of {_inputs_ENVIRONMENT_STEP} and of no other step - the list of the main environment kept before stage 4 installed anything, which that step's definition names "
          "(a step that read an older copy of a table, kept in a sub-folder of 50_gap/, fails here)", bool(written) and not wrong, "; ".join(wrong[:4]))
    pins, other, pins_sha = _inputs_pins()
    held = _inputs_held()
    named = [f"{k} {pins.get(k)}" for k, v in _inputs_NAMED_VERSIONS.items() if not (pins.get(k) == v or (v.endswith(".") and str(pins.get(k)).startswith(v)))]
    odd = sorted(k for k in set(held) | set(pins) if held.get(k) != pins.get(k))
    ok = bool(pins) and not other and not named and not odd
    check(f"{_inputs_REQUIREMENTS}: every line that is not a comment is `name==version`, no name twice; it pins wildboottest 0.3.2, numba 0.62.1 and a numpy 2.3.x, the versions the owner named; "
          "and the interpreter running this script holds exactly what it pins, pip apart: no package more, none fewer, no version different (the script is to be run with the stage-4 interpreter)",
          ok, "" if ok else f"lines that are not a pin: {other[:3]}; named versions not pinned: {named}; "
          + "held and pinned differ: " + ", ".join(f"{k} held {held.get(k)}, pinned {pins.get(k)}" for k in odd[:5]))
    wrong = [f"{name}: {w}" for name, sec in steps.items() for w in _inputs_environment(sec, pins, pins_sha)]
    check(f"{T}: in every section, `environment` has the fields {', '.join(_inputs_ENVIRONMENT_KEYS)} and says what {_inputs_REQUIREMENTS} is: its SHA-256, its {len(pins)} pins as `packages` "
          "(name for name, version for version) and their number as `packages_pinned`, no `differences`, `holds_exactly_what_the_file_pins` true, and the Python version of the interpreter running this script; "
          "and every entry of `package_versions` is the version its `environment` gives that package", bool(steps) and not wrong, "; ".join(wrong[:4]))
    sec = steps.get(_inputs_STEP0, {})
    wrong = []
    outs = sorted(sec.get("outputs")) if isinstance(sec.get("outputs"), dict) else []
    if outs != sorted("50_gap/" + n for n in _inputs_STEP0_WRITES):
        wrong.append(f"its outputs are {outs}")
    ins = sec.get("inputs") if isinstance(sec.get("inputs"), dict) else {}
    listed = {e.get("key"): {"path": e.get("path"), "bytes": e.get("bytes"), "sha256": e.get("sha256")} for e in entries}
    if not listed or ins != listed:
        odd = sorted(str(k) for k in set(ins) | set(listed) if ins.get(k) != listed.get(k))
        wrong.append(f"its inputs are not the listing's, key for key with path, bytes and sha256: {odd[:4]}")
    t = table("inputs_check.csv")
    n_yes = sum(1 for r in t if cell(r, "pass") == "yes")
    if (sec.get("gates"), sec.get("gates_passed")) != (len(t), n_yes) or isinstance(sec.get("gates"), bool) or isinstance(sec.get("gates_passed"), bool):
        wrong.append(f"gates {sec.get('gates')!r} and gates_passed {sec.get('gates_passed')!r}; inputs_check.csv has {len(t)} rows, {n_yes} with pass = yes")
    check(f"{T}, the section of step 0 ({_inputs_STEP0}): its `outputs` are the four files the step writes (50_gap/ " + ", ".join(_inputs_STEP0_WRITES) + "); its `inputs` are the entries of inputs_listing.json, key for key, "
          "with the same path, bytes and sha256; `gates` = the number of rows of inputs_check.csv and `gates_passed` = the number of them with pass = yes", not wrong, "; ".join(wrong))

# ---- part: districts ---- district_need.csv and district_allocation.csv, every column recomputed from the inputs, and again from a second source where the inputs offer one ----
_districts_R620 = "00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv"
_districts_R620_STATE = "00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv"
_districts_FRA = "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"
_districts_UNITS = "10_units/units.gpkg"
_districts_OUTSIDE = "10_units/outside_village_district.csv"
_districts_HANSEN = "20_degradation/hansen_loss_by_canopy_band_by_unit.csv"
_districts_AGREEMENT = "20_degradation/agreement_by_unit.csv"
_districts_CORESTACK = "20_degradation/corestack_by_unit.csv"
_districts_NEED = "30_need/need_by_unit.csv"
_districts_DUMP_UNIT_FY = "40_allocation/allocation_by_unit_fy.csv"
_districts_DUMP_UNIT = "40_allocation/allocation_by_unit.csv"
_districts_DUMP_NO_UNIT = "40_allocation/allocation_unassigned.csv"
_districts_DUMP_DISTRICTS = "40_allocation/assets_district_fy.csv"
_districts_DUMP_JOIN = "40_allocation/allocation_join_qa.csv"
_districts_DUMP_FILES = "40_allocation/assets_file_qa.csv"
_districts_R620_STAGE3 = "40_allocation/district_fy_r620_vs_dump.csv"
_districts_DECISION = "55_decision/condition_by_unit.csv"
_districts_CELLS = "55_decision/condition_cells.csv"
_districts_CELLS_BY_DISTRICT = "55_decision/condition_cells_by_district.csv"
_districts_TIERS = "55_decision/tiers.csv"
_districts_LAYER = "60_layer/layer_by_unit.csv"
_districts_CODES = [str(c) for c in range(370, 400)]
_districts_FY = [f"{y}-{y + 1}" for y in range(2014, 2027)]          # R6.20 writes a financial year as 2014-2015
_districts_PERIODS = {"pre": _districts_FY[:4], "post": _districts_FY[4:12], "part_year": _districts_FY[12:]}
_districts_POST_WITHOUT_FIRST = _districts_FY[5:12]
_districts_STAMP = "10/10/2020"                                     # the stamp the definitions give for the four pre tables
_districts_RULE = {"ANGUL": "384", "BOLANGIR": "393", "BOUDH": "391", "DEOGARH": "373", "JAJPUR": "382", "SONEPUR": "392"}
_districts_WINDOWS = ("2018_2025", "2001_2025", "2017_2023", "2021_2025")
_districts_DEFAULT = "2018_2025"
_districts_LOSS_CELLS = ("open_loss", "dense_loss", "little_loss")
_districts_ANR_CELL = "open_none"
_districts_ZONES = {"ECPHR only": "in_east_coast_only_units", "EPAHR only": "in_eastern_plateau_only_units",
                    "both models": "in_units_under_both_models", "": "in_units_with_no_zone"}
_districts_ST_LABELS = ("Less than 18 %", "18 to 33 %", "33 to 50 %", "More than 50 %")       # the layer's own labels: held against 60_layer/layer_by_unit.csv below
_districts_ST_TIES = ("17.995", "33.005", "50.005")                 # a per cent exactly here is classed one way rounded half up and another way rounded to even or as a float
_districts_ADI_THIRDS = ("lowest third of the index", "middle third", "highest third of the index")
_districts_SC_THIRDS = ("lowest third of Scheduled Caste share", "middle third", "highest third of Scheduled Caste share")     # not in the definitions: see the check
_districts_PLACES = 6                                               # the decimals these two tables print a per cent or a mean with (not in the definitions)
_districts_WHENS = ("started_by_fy2017_18", "started_later", "start_year_missing")
_districts_KINDS = (("forest_named", "expenditure_forest_named_worktype"), ("plantation_category", "expenditure_plantation_category"))
_districts_WORKS = {"forest_named": "n_works_forest_named_worktype", "plantation_category": "n_works_plantation_category", "total": "n_works"}     # the count of works that stands beside each money column in the dump's tables
_districts_STEP = "08_build_gap_districts"
_districts_STEP_WRITES = ("district_need.csv", "district_allocation.csv", "need_vs_allocation.csv", "need_vs_allocation_summary.csv", "marginalisation_split.csv", "what_more.csv", "gates_phase2.csv")
_districts_COMPARISONS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C7b", "C8", "C9", "C10", "C11", "C12", "B1")
_districts_SEED = 20261010                                          # permutation seed of comparison k: base + 100 + k; bootstrap seed: base + 200 + k
_districts_GATES = "gates_phase2.csv"
# The value each gate of this step is held against where the owner's instruction of 10 October 2026 gives one (Phase 0: the table of 0.3; Phase 2: the definitions, the
# comparisons and "what more is needed"), as he wrote it, thousands separators and units apart. The words of a gate are the table's; the value is his.
_districts_OWNER = {
    "the stamp R6.20 prints on the four pre-period tables": "10/10/2020",
    "districts": "30",
    "N1, default window, summed over districts, ha (the three loss cells; within 2 of the owner's 89,657)": "89657",
    "forest loss 2018-2025 over all units, summed over districts, ha (within 1 of 90,028)": "90028",
    "N2, summed over districts, ha (within 1 of 293,921)": "293921",
    "r620_plantation_pre_lakh, summed over districts (the gate of step 0)": "151843.18",
    "r620_plantation_post_lakh, summed over districts (the gate of step 0)": "13915.72",
    "r620_plantation_part_year_lakh, summed over districts (the gate of step 0)": "110.58",
    "r620_nrm_pre_lakh, summed over districts (the gate of step 0)": "327829.94",
    "r620_nrm_post_lakh, summed over districts (the gate of step 0)": "2334964.06",
    "r620_all_pre_lakh, summed over districts (the gate of step 0)": "750836.66",
    "r620_all_post_lakh, summed over districts (the gate of step 0)": "3674731.26",
    "FY2018-19 as a per cent of post-period plantation expenditure (the owner's 53 per cent)": "53",
    "works of the dump that fall in no unit, crore rupees (the owner's 73.8)": "73.8",
    "forest-named expenditure on works started by FY2017-18 as a per cent of all such expenditure in units, a missing start year counted as not started by then (the decision layer's 92.9)": "92.9",
    "the pre-period plantation share of all expenditure, per cent (the owner's 20.2232)": "20.2232",
    "that share applied to the post-period total, lakh (the owner's 743,148.16)": "743148.16",
    "LGD population / Scheduled Tribe population, summed over districts": "34766888 / 8895006",
    "districts in each tercile of ADI": "10 / 10 / 10",
    "districts in each tercile of Scheduled Caste share": "10 / 10 / 10",
    "comparisons computed (the owner's thirteen and the second reading of C7)": "14",
    "plantation works, state, FY2016-17 / FY2025-26 (the gate of step 0)": "57135 / 4105",
}


def _districts_header(name):
    """The column names of a table of the folder being checked, as its first line writes them (a name written twice stays twice)."""
    with open(GAP / name, encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def _districts_round(x, places):
    """A fraction rounded half up (a tie goes away from zero) to `places` decimals, as the text a table prints."""
    from fractions import Fraction
    scale = 10 ** places
    n = (abs(Fraction(x)) * scale + Fraction(1, 2)).__floor__()
    text = f"{n // scale}.{n % scale:0{places}d}" if places else str(n)
    return ("-" if x < 0 and n else "") + text


def _districts_st_class(pct):
    """The layer's rule on a per cent given exactly: rounded to two decimals; under 18; 18 to 33, 33 included; above 33 to 50,
    50 included; above 50."""
    from fractions import Fraction
    r = Fraction(_districts_round(pct, 2))
    return _districts_ST_LABELS[0 if r < 18 else 1 if r <= 33 else 2 if r <= 50 else 3]


def _districts_st_tie(pct):
    """True where the class of a per cent depends on how a tie at the third decimal is rounded: exactly 17.995, 33.005 or 50.005."""
    from fractions import Fraction
    return any(Fraction(pct) == Fraction(D(x)) for x in _districts_ST_TIES)


def _districts_thirds(value, labels):
    """Terciles of 10, 10 and 10 districts by ascending value, ties by census code: {code: label}."""
    order = sorted(value, key=lambda c: (value[c], int(c)))
    return {c: labels[0 if i < 10 else 1 if i < 20 else 2] for i, c in enumerate(order)}


def _districts_when(fy):
    """Where a start year of the geotagged record falls: 0 for 2017-18 or earlier, 1 for later, 2 for NA (no usable start
    date: not started by FY2017-18, and not later either); None for anything else."""
    fy = fy.strip()
    if fy == "NA":
        return 2
    if len(fy) == 7 and fy[:4].isdigit() and fy[4] == "-" and fy[5:].isdigit():
        return 0 if int(fy[:4]) <= 2017 else 1
    return None


def _districts_money(cell):
    """A money cell of the geotagged record's tables: a blank cell adds nothing."""
    return D(cell) if cell.strip() else D(0)


def _districts_crosswalk():
    """From the inputs: {census code: (district name, R6.20 name)} and what went wrong, if anything.
    The name is the one the Odisha FRA table and the decision table carry for the code; an R6.20 name takes the code whose
    census name equals it once both are upper-cased, else the code the owner's spelling rule gives it."""
    wrong = []
    fra, dec = {}, {}
    for r in rows(_districts_FRA):
        fra.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"].strip())
    for r in rows(_districts_DECISION):
        dec.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"].strip())
    for c in sorted(set(fra) | set(dec)):
        if len(fra.get(c, ())) != 1 or fra.get(c) != dec.get(c):
            wrong.append(f"code {c}: FRA table {sorted(fra.get(c, ()))}, decision table {sorted(dec.get(c, ()))}")
    name_of = {c: sorted(v)[0] for c, v in fra.items() if v}
    upper = {}
    for c, n in name_of.items():
        upper.setdefault(n.upper(), []).append(c)
    out = {}
    for n in sorted({r["district"].strip() for r in rows(_districts_R620)}):
        hit = upper.get(n.upper(), [])
        code = hit[0] if len(hit) == 1 else _districts_RULE.get(n, "")
        if not code or code in out:
            wrong.append(f"R6.20 name {n}: no census code, or a code already taken ({code!r})")
            continue
        out[code] = (name_of.get(code, ""), n)
    if sorted(out) != _districts_CODES:
        wrong.append(f"the codes are not 370 to 399 each once: {sorted(out)}")
    return out, wrong


def _districts_units(cw):
    """From the inputs: {unit_id: (True for an LGD panchayat unit, census district code)} and what went wrong, if anything.
    An LGD panchayat unit takes the code it carries in units.gpkg, an outside-village unit the code of its row in
    outside_village_district.csv. A unit that cannot be given one of the crosswalk's districts is left out and reported."""
    import pyogrio
    df = pyogrio.read_dataframe(ROOT / _districts_UNITS, read_geometry=False)
    assigned, wrong, units = {}, [], {}
    for r in rows(_districts_OUTSIDE):
        assigned.setdefault(r["unit_id"].strip(), []).append(r["pc11_district_code"].strip())
    for uid, level, code in zip(df["unit_id"], df["unit_level"], df["pc11_district_code"]):
        uid, level = str(uid).strip(), str(level).strip()
        if level == "lgd_panchayat":
            code = "" if code is None else str(code).strip()         # a missing code (NaN, NA) is no code of the crosswalk: reported below
        elif level == "outside_village":
            code = assigned[uid][0] if len(assigned.get(uid, [])) == 1 else ""
        else:
            code = ""
        if uid in units or code not in cw:
            wrong.append(f"unit {uid} ({level}): twice in units.gpkg, or no district of the crosswalk ({code!r})")
            continue
        units[uid] = (level == "lgd_panchayat", code)
    return units, wrong


def _districts_by_unit(path, units, wrong):
    """A per-unit table as {unit_id: row}, kept to the units of units.gpkg; a unit twice, unknown or absent is reported."""
    got = {}
    for r in rows(path):
        u = r["unit_id"].strip()
        if u in got or u not in units:
            wrong.append(f"{path}: unit {u} twice, or not a unit of units.gpkg")
            continue
        got[u] = r
    if len(got) != len(units):
        wrong.append(f"{path}: holds {len(got)} of the {len(units)} units")
    return got


def _districts_need(units, cw):
    """district_need.csv from its definition: {code: {column: value}}; a Decimal for hectares, an int for a count, text otherwise
    (a per cent or a mean already rounded half up to the six decimals the table prints). Also returned: the forest and loss
    hectares made a second way, from the per-year Hansen table instead of the decision table's own hectares (the cells still the
    decision table's); what went wrong, if anything; and the default-window loss of each unit that is in a loss cell."""
    from fractions import Fraction
    Z, wrong = D(0), []
    W, DEF = _districts_WINDOWS, _districts_DEFAULT
    out = {}
    for c in cw:
        o = out[c] = {"pc11_district_code": c, "district_name": cw[c][0], "r620_district": cw[c][1]}
        for k in ("n_units", "n_units_lgd", "n_units_outside", "n_units_anr", "n_assessed_units_east_coast_only",
                  "population_lgd", "st_pop_lgd", "sc_pop_lgd", "n_units_lgd_with_adi"):
            o[k] = 0
        for k in ("forest_2000_ha", "n2_ha"):
            o[k] = o[k + "_lgd"] = o[k + "_outside"] = Z
        for w in W:
            o[f"n1_ha_{w}"] = o[f"n1_ha_{w}_lgd"] = o[f"n1_ha_{w}_outside"] = Z
            o[f"forest_loss_ha_{w}_all_units"] = o[f"forest_at_window_start_ha_{w}"] = Z
            o[f"n_units_loss_cells_{w}"] = 0
        o["loss_2001_2013_ha"] = Z
        for z in _districts_ZONES.values():
            o[f"n1_ha_{DEF}_{z}"] = Z
        o["_adi_x_pop"], o["_adi_pop"] = Fraction(0), 0
    n1_of_unit = {}                                                  # default window: the loss of each unit in a loss cell
    dec = _districts_by_unit(_districts_DECISION, units, wrong)
    for u, r in dec.items():
        lgd, c = units[u]
        o, part = out[c], "_lgd" if lgd else "_outside"
        o["n_units"] += 1
        o["n_units" + part] += 1
        forest = D(r["dense_2000_ha"]) + D(r["open_2000_ha"])
        o["forest_2000_ha"] += forest
        o["forest_2000_ha" + part] += forest
        for w in W:
            loss = D(r[f"forest_loss_ha_{w}"])
            o[f"forest_loss_ha_{w}_all_units"] += loss
            o[f"forest_at_window_start_ha_{w}"] += D(r[f"forest_at_window_start_ha_{w}"])
            if r[f"cell_{w}"].strip() in _districts_LOSS_CELLS:
                o[f"n1_ha_{w}"] += loss
                o[f"n1_ha_{w}{part}"] += loss
                o[f"n_units_loss_cells_{w}"] += 1
                if w == DEF:
                    n1_of_unit[u] = loss
        if r[f"cell_{DEF}"].strip() == _districts_ANR_CELL:
            o["n2_ha"] += D(r["standing_open_ha"])
            o["n2_ha" + part] += D(r["standing_open_ha"])
            o["n_units_anr"] += 1
    alt = {c: {} for c in cw}                                        # the same hectares from a second source: the per-year Hansen table
    for a in alt.values():
        for k in ["forest_2000_ha", "n2_ha"] + [f"n1_ha_{w}" for w in W]:
            a[k] = a[k + "_lgd"] = a[k + "_outside"] = Z
        for w in W:
            a[f"forest_loss_ha_{w}_all_units"] = a[f"loss_below_minimum_ha_{w}"] = a[f"forest_at_window_start_ha_{w}"] = Z
    for u, r in _districts_by_unit(_districts_HANSEN, units, wrong).items():
        lgd, c = units[u]
        out[c]["loss_2001_2013_ha"] += sum((D(r[f"loss_ha_gt30_{y}"]) + D(r[f"loss_ha_gt10le30_{y}"]) for y in range(2001, 2014)), Z)
        a, part, cells = alt[c], "_lgd" if lgd else "_outside", dec.get(u, {})
        land = {b: D(r[f"area_ha_{b}"]) for b in ("gt30", "gt10le30")}                              # the dense band and the open band in 2000
        lost = {b: [Z] + [D(r[f"loss_ha_{b}_{y}"]) for y in range(2001, 2026)] for b in land}       # lost[b][k]: the band's loss in the year 2000 + k
        a["forest_2000_ha"] += land["gt30"] + land["gt10le30"]
        a["forest_2000_ha" + part] += land["gt30"] + land["gt10le30"]
        for w in W:
            first, last = int(w[:4]), int(w[5:])                     # a window is a span of calendar years, ends included
            loss = sum((sum(lost[b][first - 2000:last - 2000 + 1], Z) for b in land), Z)
            a[f"forest_loss_ha_{w}_all_units"] += loss
            a[f"forest_at_window_start_ha_{w}"] += sum((max(Z, land[b] - sum(lost[b][:first - 2000], Z)) for b in land), Z)
            if cells.get(f"cell_{w}", "").strip() in _districts_LOSS_CELLS:
                a[f"n1_ha_{w}"] += loss
                a[f"n1_ha_{w}{part}"] += loss
            else:
                a[f"loss_below_minimum_ha_{w}"] += loss
        if cells.get(f"cell_{DEF}", "").strip() == _districts_ANR_CELL:
            standing = max(Z, land["gt10le30"] - sum(lost["gt10le30"], Z))
            a["n2_ha"] += standing
            a["n2_ha" + part] += standing
    for u, r in _districts_by_unit(_districts_AGREEMENT, units, wrong).items():
        zone, o = r["corestack_zone_model"].strip(), out[units[u][1]]
        if zone not in _districts_ZONES:
            wrong.append(f"{_districts_AGREEMENT}: unit {u} has the zone model {zone!r}, which the definition does not name")
            continue
        o[f"n1_ha_{DEF}_{_districts_ZONES[zone]}"] += n1_of_unit.get(u, Z)
        if r["assessed"].strip() == "1" and zone == "ECPHR only":
            o["n_assessed_units_east_coast_only"] += 1
    for u, r in _districts_by_unit(_districts_NEED, units, wrong).items():
        if not units[u][0]:                                          # outside-village land has no census rows
            continue
        o, pop = out[units[u][1]], int(r["population"])
        o["population_lgd"] += pop
        o["st_pop_lgd"] += int(r["st_pop"])
        o["sc_pop_lgd"] += int(r["sc_pop"])
        if r["adi_2011"].strip():
            o["_adi_x_pop"] += Fraction(D(r["adi_2011"])) * pop
            o["_adi_pop"] += pop
            o["n_units_lgd_with_adi"] += 1
    sc, adi, P = {}, {}, _districts_PLACES
    for c, o in out.items():
        for w in W:
            o[f"loss_below_minimum_ha_{w}"] = o[f"forest_loss_ha_{w}_all_units"] - o[f"n1_ha_{w}"]
        n1 = o[f"n1_ha_{DEF}"]
        east = Fraction(100) * Fraction(o[f"n1_ha_{DEF}_in_east_coast_only_units"]) / Fraction(n1) if n1 else None
        o["east_coast_share_of_n1_pct"] = "" if east is None else _districts_round(east, P)
        o["left_out_of_c7"] = "yes" if east is not None and east > 50 else "no"
        if east is not None and (east > 50) != (Fraction(D(o["east_coast_share_of_n1_pct"])) > 50):
            wrong.append(f"district {c}: its East Coast share of N1 is above 50 exactly and not as printed, or the reverse: the rule for C7 is not decided")
        o["left_out_under_the_other_rule"] = "yes" if o["n_assessed_units_east_coast_only"] > 0 else "no"
        pop, with_adi = o["population_lgd"], o.pop("_adi_pop")
        weighted = o.pop("_adi_x_pop")
        if not pop or not with_adi:
            wrong.append(f"district {c}: no LGD population, or no LGD unit with an adi_2011")
            continue
        st, sc[c], adi[c] = Fraction(100 * o["st_pop_lgd"], pop), Fraction(100 * o["sc_pop_lgd"], pop), weighted / with_adi
        if _districts_st_tie(st):
            wrong.append(f"district {c}: its Scheduled Tribe per cent is exactly {float(st)}, where the class depends on how the tie is rounded")
        o["st_share_pct"], o["st_class"] = _districts_round(st, P), _districts_st_class(st)
        o["sc_share_pct"] = _districts_round(sc[c], P)
        o["adi_2011"] = _districts_round(adi[c], P)
        o["adi_2011_population_covered_pct"] = _districts_round(Fraction(100 * with_adi, pop), P)
    for col, value, labels, printed in (("sc_tercile", sc, _districts_SC_THIRDS, "sc_share_pct"), ("adi_tercile", adi, _districts_ADI_THIRDS, "adi_2011")):
        thirds = _districts_thirds(value, labels)
        for c, label in thirds.items():
            out[c][col] = label
        if thirds != _districts_thirds({c: Fraction(D(out[c][printed])) for c in value}, labels):
            wrong.append(f"{col}: the thirds are not the same by the exact {printed} and by the {printed} as printed: the ranking is not decided")
    return out, alt, wrong, n1_of_unit


def _districts_second_cells(cw):
    """From a second source, the decision stage's own count of units by window, district and cell
    (55_decision/condition_cells_by_district.csv, by district name): {code: {column: count}} for n_units, n_units_lgd,
    n_units_outside, n_units_loss_cells of each window and n_units_anr. Also what went wrong, if anything."""
    code_of = {v[0]: c for c, v in cw.items()}
    got, wrong = {}, []
    for r in rows(_districts_CELLS_BY_DISTRICT):
        k = (r["window"].strip(), r["district"].strip(), r["cell"].strip())
        if k in got or k[0] not in _districts_WINDOWS or k[1] not in code_of:
            wrong.append(f"{_districts_CELLS_BY_DISTRICT}: a second row, or a window or a district that is not one of the stage's: {k}")
            continue
        got[k] = (int(r["n_units"]), int(r["n_outside_village"]))
    cells = sorted({k[2] for k in got})
    if len(got) != len(_districts_WINDOWS) * len(code_of) * 6 or len(cells) != 6 or not set(_districts_LOSS_CELLS) | {_districts_ANR_CELL} <= set(cells):
        wrong.append(f"{_districts_CELLS_BY_DISTRICT}: {len(got)} rows and the cells {cells}, not 4 windows x 30 districts x 6 cells")
    out = {}
    for name, c in code_of.items():
        o, totals = {}, set()
        for w in _districts_WINDOWS:
            mine = {x: got.get((w, name, x), (0, 0)) for x in cells}
            totals.add((sum(v[0] for v in mine.values()), sum(v[1] for v in mine.values())))
            o[f"n_units_loss_cells_{w}"] = sum(mine.get(x, (0, 0))[0] for x in _districts_LOSS_CELLS)
            if w == _districts_DEFAULT:
                o["n_units_anr"] = mine.get(_districts_ANR_CELL, (0, 0))[0]
        if len(totals) != 1:
            wrong.append(f"{_districts_CELLS_BY_DISTRICT}: {name} has not the same units in each window: {sorted(totals)}")
        o["n_units"], o["n_units_outside"] = sorted(totals)[0]
        o["n_units_lgd"] = o["n_units"] - o["n_units_outside"]
        out[c] = o
    return out, wrong


def _districts_second_state():
    """What the decision stage's own table of cells (55_decision/condition_cells.csv) prints for the state, as far as it totals a
    column of district_need.csv: {column: (the total, how far a sum of exact hectares may lie from it)}. Its hectares are
    printed to 0.01 ha, so each figure added may be 0.005 ha off; its counts are exact. Also what went wrong, if anything."""
    half, by, wrong, out = D("0.005"), {}, [], {}
    for r in rows(_districts_CELLS):
        by[(r["window"].strip(), r["units"].strip(), r["cell"].strip())] = r
    kinds = (("", "all units"), ("_lgd", "lgd_panchayat"), ("_outside", "outside_village"))
    cells = sorted({k[2] for k in by})
    if len(by) != len(_districts_WINDOWS) * 3 * 6 or len(cells) != 6 or any((w, kind, x) not in by for w in _districts_WINDOWS for _, kind in kinds for x in cells):
        return out, [f"{_districts_CELLS}: not one row for each of 4 windows x 3 kinds of unit x 6 cells"]
    for w in _districts_WINDOWS:
        for suffix, kind in kinds:
            out[f"n1_ha_{w}{suffix}"] = (sum((D(by[(w, kind, x)]["forest_loss_ha_in_window"]) for x in _districts_LOSS_CELLS), D(0)), half * 3)
        out[f"forest_loss_ha_{w}_all_units"] = (sum((D(by[(w, "all units", x)]["forest_loss_ha_in_window"]) for x in cells), D(0)), half * 6)
        out[f"loss_below_minimum_ha_{w}"] = (sum((D(by[(w, "all units", x)]["forest_loss_ha_in_window"]) for x in cells if x not in _districts_LOSS_CELLS), D(0)), half * 3)
        out[f"n_units_loss_cells_{w}"] = (D(sum(int(by[(w, "all units", x)]["n_units"]) for x in _districts_LOSS_CELLS)), D(0))
    for suffix, kind in kinds:
        out[f"n2_ha{suffix}"] = (D(by[(_districts_DEFAULT, kind, _districts_ANR_CELL)]["standing_open_ha"]), half)
        out[f"n_units{suffix}"] = (D(int(by[(_districts_DEFAULT, kind, _districts_ANR_CELL)]["n_units_of_this_kind"])), D(0))
    out["n_units_anr"] = (D(int(by[(_districts_DEFAULT, "all units", _districts_ANR_CELL)]["n_units"])), D(0))
    return out, wrong


def _districts_second_zone(units, n1_of_unit):
    """From a second source: N1 of the default window split by which zone model's hectares 20_degradation/corestack_by_unit.csv
    gives a unit (East Coast only, Eastern Plateau only, both, neither), and the units the agreement table's own flag leaves out
    of its headline (assessed = 1, in_headline_population = 0): {code: {column: value}}. The two splits must be equal if the
    two tables agree on the model of every unit that has one and the units without one hold no N1; what fails of that is
    returned too."""
    Z, wrong = D(0), []
    out = {}
    for _, c in units.values():
        if c not in out:
            out[c] = dict({f"n1_ha_{_districts_DEFAULT}_{z}": Z for z in _districts_ZONES.values()}, n_assessed_units_east_coast_only=0)
    model = {}
    for u, r in _districts_by_unit(_districts_AGREEMENT, units, wrong).items():
        model[u] = r["corestack_zone_model"].strip()
        if r["assessed"].strip() == "1" and r["in_headline_population"].strip() == "0":
            out[units[u][1]]["n_assessed_units_east_coast_only"] += 1
    n_differ = n_blank_with_n1 = 0
    for u, r in _districts_by_unit(_districts_CORESTACK, units, wrong).items():
        east, plateau = D(r["corestack_value_ha_zone_ECPHR"]) > 0, D(r["corestack_value_ha_zone_EPAHR"]) > 0
        zone = "both models" if east and plateau else "ECPHR only" if east else "EPAHR only" if plateau else ""
        if model.get(u, ""):
            n_differ += model[u] != zone
        elif n1_of_unit.get(u, Z) != 0:
            n_blank_with_n1 += 1
        out[units[u][1]][f"n1_ha_{_districts_DEFAULT}_{_districts_ZONES[zone]}"] += n1_of_unit.get(u, Z)
    if n_differ or n_blank_with_n1:
        wrong.append(f"{n_differ} units whose zone model in the agreement table is not the one their zone hectares in {_districts_CORESTACK} give; "
                     f"{n_blank_with_n1} units with N1 and no zone model")
    from fractions import Fraction
    for o in out.values():                                           # the share and the two rules for C7, made of this source's own split and count
        east, n1 = o[f"n1_ha_{_districts_DEFAULT}_in_east_coast_only_units"], sum((o[f"n1_ha_{_districts_DEFAULT}_{z}"] for z in _districts_ZONES.values()), Z)
        share = Fraction(100) * Fraction(east) / Fraction(n1) if n1 else None
        o["east_coast_share_of_n1_pct"] = "" if share is None else _districts_round(share, _districts_PLACES)
        o["left_out_of_c7"] = "yes" if share is not None and share > 50 else "no"
        o["left_out_under_the_other_rule"] = "yes" if o["n_assessed_units_east_coast_only"] > 0 else "no"
    return out, wrong


def _districts_second_people(cw):
    """From a second source, the layer's own per-unit table (60_layer/layer_by_unit.csv), by the district code and the unit level
    it carries itself: the people columns of district_need.csv, made by the same definitions. {code: {column: value}}, and what
    went wrong, if anything."""
    from fractions import Fraction
    P, wrong, out = _districts_PLACES, [], {c: {"population_lgd": 0, "st_pop_lgd": 0, "sc_pop_lgd": 0, "n_units_lgd_with_adi": 0, "_x": Fraction(0), "_pop": 0} for c in cw}
    for r in rows(_districts_LAYER):
        if r["unit_level"].strip() != "lgd_panchayat":
            continue
        c = r["pc11_district_code"].strip()
        people = [D(r[k]) for k in ("population", "st_pop", "sc_pop")]
        if c not in out or any(x != x.to_integral_value() for x in people):
            wrong.append(f"{_districts_LAYER}: unit {r['unit_id']} has no district of the stage, or people that are not whole numbers")
            continue
        o, pop = out[c], int(people[0])
        o["population_lgd"] += pop
        o["st_pop_lgd"] += int(people[1])
        o["sc_pop_lgd"] += int(people[2])
        if r["adi_2011"].strip():
            o["_x"] += Fraction(D(r["adi_2011"])) * pop
            o["_pop"] += pop
            o["n_units_lgd_with_adi"] += 1
    sc, adi = {}, {}
    for c, o in out.items():
        x, with_adi, pop = o.pop("_x"), o.pop("_pop"), o["population_lgd"]
        if not pop or not with_adi:
            wrong.append(f"{_districts_LAYER}: district {c} has no LGD population, or no LGD unit with an adi_2011")
            continue
        st, sc[c], adi[c] = Fraction(100 * o["st_pop_lgd"], pop), Fraction(100 * o["sc_pop_lgd"], pop), x / with_adi
        o["st_share_pct"], o["st_class"] = _districts_round(st, P), _districts_st_class(st)
        o["sc_share_pct"] = _districts_round(sc[c], P)
        o["adi_2011"] = _districts_round(adi[c], P)
        o["adi_2011_population_covered_pct"] = _districts_round(Fraction(100 * with_adi, pop), P)
    if len(sc) == len(out):                                          # the thirds are of all the districts or of none
        for col, value, labels in (("sc_tercile", sc, _districts_SC_THIRDS), ("adi_tercile", adi, _districts_ADI_THIRDS)):
            for c, label in _districts_thirds(value, labels).items():
                out[c][col] = label
    return out, wrong


def _districts_allocation(units, cw):
    """district_allocation.csv from its definition: {code: {column: value}}; a Decimal for money, an int for a count, text otherwise.
    Also what went wrong, if anything."""
    from fractions import Fraction
    Z, wrong, P = D(0), [], _districts_PLACES
    code_of = {v[1]: c for c, v in cw.items()}
    out = {c: {"pc11_district_code": c, "district_name": cw[c][0], "r620_district": cw[c][1]} for c in cw}
    # ---- R6.20: lakh rupees, two decimals, added exactly -----------------------------------------------------------------------------
    cat, every, works = {}, {}, {}
    for r in rows(_districts_R620):
        k = (code_of.get(r["district"].strip()), r["category"].strip(), r["fy"].strip())
        if k[0] is None or k in cat or k[1] not in ("Plantation", "NRM", "Water") or k[2] not in _districts_FY:
            wrong.append(f"{_districts_R620}: a row with no district, category or year of the definition, or a second row for one: {k}")
            continue
        cat[k] = D(r["exp_cat_lakh"])
        every.setdefault((k[0], k[2]), set()).add(D(r["exp_all_lakh"]))
        works[k] = int(r["works_ongoing"]) + int(r["works_completed"])
    if len(cat) != 30 * 3 * 13 or any(len(v) != 1 for v in every.values()):
        wrong.append(f"{_districts_R620}: {len(cat)} district-category-years, not 1,170; or exp_all_lakh differs within a district-year")
        return out, wrong
    state = rows(_districts_R620_STATE)
    stamps = {r["last_updated"].strip() for r in state if r["fy"].strip() in _districts_PERIODS["pre"]}
    later = {r["last_updated"].strip() for r in state if r["fy"].strip() not in _districts_PERIODS["pre"]}
    if stamps != {_districts_STAMP} or _districts_STAMP in later or len(state) != 39 or len({(r["category"].strip(), r["fy"].strip()) for r in state}) != 39:
        wrong.append(f"{_districts_R620_STATE}: the four pre years carry the stamps {sorted(stamps)}, not {_districts_STAMP} alone; or a later year carries it; or the file has not one row for each of 3 categories x 13 years")
    for c, o in out.items():
        for name, key in (("plantation", "Plantation"), ("nrm", "NRM"), ("water", "Water"), ("all", None)):
            for period, fys in _districts_PERIODS.items():
                o[f"r620_{name}_{period}_lakh"] = sum((cat[(c, key, f)] if key else sorted(every[(c, f)])[0] for f in fys), Z)
        o["r620_plantation_post_without_fy2018_19_lakh"] = sum((cat[(c, "Plantation", f)] for f in _districts_POST_WITHOUT_FIRST), Z)
        for period in ("pre", "post"):
            whole = o[f"r620_all_{period}_lakh"]
            o[f"plantation_pct_of_all_{period}"] = _districts_round(Fraction(100) * Fraction(o[f"r620_plantation_{period}_lakh"]) / Fraction(whole), P) if whole else ""
        o["plantation_works_fy2016_17"] = works[(c, "Plantation", "2016-2017")]
        o["plantation_works_fy2025_26"] = works[(c, "Plantation", "2025-2026")]
        o["r620_pre_years_last_updated"] = sorted(stamps)[0] if len(stamps) == 1 else ""
    # ---- the geotagged record: rupees, by the district of the unit ---------------------------------------------------------------------
    whens = _districts_WHENS
    for o in out.values():
        for name, _ in _districts_KINDS:
            for when in whens:
                o[f"dump_{name}_{when}_inr"] = Z
        o["n_units_with_forest_named_by_fy2017_18"] = 0
        for k in ("total", "forest_named", "plantation_category"):
            o[f"dump_no_unit_{k}_inr"] = Z
    by_then = {}
    for r in rows(_districts_DUMP_UNIT_FY):
        u, when = r["unit_id"].strip(), _districts_when(r["fy_work_start"])
        if u not in units:
            wrong.append(f"{_districts_DUMP_UNIT_FY}: unit {u} is not a unit of units.gpkg")
            continue
        if when is None:
            wrong.append(f"{_districts_DUMP_UNIT_FY}: fy_work_start {r['fy_work_start']!r} is neither a year written like 2017-18 nor NA")
            continue
        o = out[units[u][1]]
        for name, col in _districts_KINDS:
            o[f"dump_{name}_{whens[when]}_inr"] += _districts_money(r[col])
        if when == 0:
            by_then[u] = by_then.get(u, Z) + _districts_money(r[_districts_KINDS[0][1]])
    for u, v in by_then.items():
        if v > 0:
            out[units[u][1]]["n_units_with_forest_named_by_fy2017_18"] += 1
    # ---- works in no unit, by the district of the file they came in ---------------------------------------------------------------------
    file_code = {}
    for r in rows(_districts_DUMP_DISTRICTS):
        file_code.setdefault(r["district_file"].strip(), set()).add(r["pc11_district_code"].strip())
    for r in rows(_districts_DUMP_NO_UNIT):
        codes = file_code.get(r["district_file"].strip(), set())
        if len(codes) != 1 or sorted(codes)[0] not in out:
            wrong.append(f"{_districts_DUMP_NO_UNIT}: the file {r['district_file']!r} has no one district in {_districts_DUMP_DISTRICTS}")
            continue
        o = out[sorted(codes)[0]]
        for k, col in (("total", "expenditure_total"), ("forest_named", "expenditure_forest_named_worktype"), ("plantation_category", "expenditure_plantation_category")):
            o[f"dump_no_unit_{k}_inr"] += _districts_money(r[col])
    return out, wrong


def _districts_second_r620(cw):
    """From a second source, stage 3's own table of the report by district and year (40_allocation/district_fy_r620_vs_dump.csv),
    by the census code that table carries itself: every R6.20 column of district_allocation.csv, made by the same definitions.
    {code: {column: value}}, and what went wrong, if anything."""
    from fractions import Fraction
    Z, wrong, P, got = D(0), [], _districts_PLACES, {}
    short = {f: f[:5] + f[7:] for f in _districts_FY}                # 2014-2015 -> 2014-15, as that table writes a year
    for r in rows(_districts_R620_STAGE3):
        k = (r["pc11_district_code"].strip(), r["fy"].strip())
        if k in got or k[0] not in cw or k[1] not in short.values() or r["district"].strip() != cw[k[0]][1]:
            wrong.append(f"{_districts_R620_STAGE3}: a second row, or a code, a year or an R6.20 name that is not the stage's: {k} {r['district']!r}")
            continue
        got[k] = r
    if len(got) != 30 * 13:
        return {}, wrong + [f"{_districts_R620_STAGE3}: {len(got)} district-years, not 390"]
    out = {}
    for c in cw:
        o = out[c] = {}
        for name in ("plantation", "nrm", "water", "all"):
            for period, fys in _districts_PERIODS.items():
                o[f"r620_{name}_{period}_lakh"] = sum((D(got[(c, short[f])][f"r620_exp_{name}_lakh"]) for f in fys), Z)
        o["r620_plantation_post_without_fy2018_19_lakh"] = sum((D(got[(c, short[f])]["r620_exp_plantation_lakh"]) for f in _districts_POST_WITHOUT_FIRST), Z)
        for period in ("pre", "post"):
            whole = o[f"r620_all_{period}_lakh"]
            o[f"plantation_pct_of_all_{period}"] = _districts_round(Fraction(100) * Fraction(o[f"r620_plantation_{period}_lakh"]) / Fraction(whole), P) if whole else ""
        for col, fy in (("plantation_works_fy2016_17", "2016-17"), ("plantation_works_fy2025_26", "2025-26")):
            n = D(got[(c, fy)]["r620_works_plantation"])
            o[col] = int(n) if n == n.to_integral_value() else None
        stamps = {got[(c, short[f])]["r620_last_updated"].strip() for f in _districts_PERIODS["pre"]}
        o["r620_pre_years_last_updated"] = sorted(stamps)[0] if len(stamps) == 1 else None
    return out, wrong


def _districts_second_dump(units, cw):
    """Second sources for the geotagged record's columns. Each money cell of the dump's tables is rounded to the paisa, so a sum of
    k cells may lie 0.005 x k rupees from the same sum made of other cells. k counts only the cells that hold a work of the kind
    (the count of works beside the money column is above zero): a cell with no work of the kind must add nothing, which is held
    here, and a figure of nothing is not rounded. Returned:
      per_unit   {code: {kind: (the kind's expenditure summed over the district's units in allocation_by_unit.csv, tolerance)}}
      no_unit    {code: (expenditure_unassigned of allocation_join_qa.csv for the district's file, by the code assets_file_qa.csv
                 gives the file; tolerance)}
      state      {(kind, when): (that expenditure of assets_district_fy.csv, every work of the record, less that of
                 allocation_unassigned.csv, the works in no unit; tolerance)}
      outside    {kind or `total`: (that expenditure of assets_district_fy.csv, every work of the record, less that of
                 allocation_by_unit.csv, the works in a unit: the works in no unit; tolerance)}
    and what went wrong, if anything."""
    Z, half, wrong = D(0), D("0.005"), []
    kinds3 = _districts_KINDS + (("total", "expenditure_total"),)

    def figures(r, path):
        """{kind: 1 where the row holds a work of the kind, else 0}; a row with no work of the kind and money of it is reported."""
        f = {}
        for name, col in kinds3:
            f[name] = 1 if int(r[_districts_WORKS[name]]) > 0 else 0
            if not f[name] and _districts_money(r[col]) != 0:
                wrong.append(f"{path}: a row with no work of the kind `{name}` and money in {col}")
        return f

    n_rows = {c: {name: 0 for name, _ in _districts_KINDS} for c in cw}     # the cells of the per-unit, per-year table that fall in each district and hold a work of the kind
    n_when = {(name, w): 0 for name, _ in _districts_KINDS for w in range(3)}
    for r in rows(_districts_DUMP_UNIT_FY):
        u, when = r["unit_id"].strip(), _districts_when(r["fy_work_start"])
        if u in units and when is not None:
            f = figures(r, _districts_DUMP_UNIT_FY)
            for name, _ in _districts_KINDS:
                n_rows[units[u][1]][name] += f[name]
                n_when[(name, when)] += f[name]
    per_unit = {c: {name: [Z, 0] for name, _ in _districts_KINDS} for c in cw}
    in_units = {name: [Z, 0] for name, _ in kinds3}                 # the works that fall in a unit, the whole state
    for u, r in _districts_by_unit(_districts_DUMP_UNIT, units, wrong).items():
        f = figures(r, _districts_DUMP_UNIT)
        for name, col in _districts_KINDS:
            per_unit[units[u][1]][name][0] += _districts_money(r[col])
            per_unit[units[u][1]][name][1] += f[name]
        for name, col in kinds3:
            in_units[name][0] += _districts_money(r[col])
            in_units[name][1] += f[name]
    per_unit = {c: {name: (v[0], half * (v[1] + n_rows[c][name])) for name, v in kinds.items()} for c, kinds in per_unit.items()}
    file_code = {}
    for r in rows(_districts_DUMP_FILES):
        file_code.setdefault(r["district_file"].strip(), set()).add(r["pc11_district_code"].strip())
    n_file, apart = {}, {(name, w): [Z, 0] for name, _ in _districts_KINDS for w in range(3)}
    n_apart = {name: 0 for name, _ in kinds3}
    for r in rows(_districts_DUMP_NO_UNIT):
        n_file[r["district_file"].strip()] = n_file.get(r["district_file"].strip(), 0) + 1
        when = _districts_when(r["fy_work_start"])
        if when is None:
            wrong.append(f"{_districts_DUMP_NO_UNIT}: fy_work_start {r['fy_work_start']!r} is neither a year nor NA")
            continue
        f = figures(r, _districts_DUMP_NO_UNIT)
        for name, col in _districts_KINDS:
            apart[(name, when)][0] += _districts_money(r[col])
            apart[(name, when)][1] += f[name]
        for name, _ in kinds3:
            n_apart[name] += f[name]
    no_unit = {c: [Z, half] for c in cw}
    seen = set()
    for r in rows(_districts_DUMP_JOIN):
        f = r["district_file"].strip()
        codes = file_code.get(f, set())
        if f in seen or len(codes) != 1 or sorted(codes)[0] not in no_unit:
            wrong.append(f"{_districts_DUMP_JOIN}: the file {f!r} twice, or with no one district in {_districts_DUMP_FILES}")
            continue
        seen.add(f)
        no_unit[sorted(codes)[0]][0] += D(r["expenditure_unassigned"])
        no_unit[sorted(codes)[0]][1] += half * n_file.get(f, 0)
    if len(seen) != 30 or not set(n_file) <= seen:
        wrong.append(f"{_districts_DUMP_JOIN}: {len(seen)} files, not 30; or a file of {_districts_DUMP_NO_UNIT} that it does not have")
    whole = {(name, w): [Z, 0] for name, _ in _districts_KINDS for w in range(3)}
    every = {name: [Z, 0] for name, _ in kinds3}                    # every work of the record, the whole state
    for r in rows(_districts_DUMP_DISTRICTS):
        when = _districts_when(r["fy_work_start"])
        if when is None:
            wrong.append(f"{_districts_DUMP_DISTRICTS}: fy_work_start {r['fy_work_start']!r} is neither a year nor NA")
            continue
        f = figures(r, _districts_DUMP_DISTRICTS)
        for name, col in _districts_KINDS:
            whole[(name, when)][0] += _districts_money(r[col])
            whole[(name, when)][1] += f[name]
        for name, col in kinds3:
            every[name][0] += _districts_money(r[col])
            every[name][1] += f[name]
    state = {k: (whole[k][0] - apart[k][0], half * (whole[k][1] + apart[k][1] + n_when[k])) for k in whole}
    outside = {name: (every[name][0] - in_units[name][0], half * (every[name][1] + in_units[name][1] + n_apart[name])) for name, _ in kinds3}
    return per_unit, {c: tuple(v) for c, v in no_unit.items()}, state, outside, wrong


def _districts_same(a, b):
    """Two cells are the same: the numbers in them equal as numbers, in the same places (12.5 equals 12.50), and the words between
    the numbers equal as text (the white space at a word's two ends apart)."""
    import re
    pat = re.compile(r"\d+(?:\.\d+)?")
    a, b = str(a).strip(), str(b).strip()
    return ([w.strip() for w in pat.split(a)] == [w.strip() for w in pat.split(b)]
            and [D(x) for x in pat.findall(a)] == [D(x) for x in pat.findall(b)])


def _districts_places(text):
    """The decimals a plain number is printed with; None for anything else."""
    import re
    m = re.fullmatch(r"-?\d+(?:\.(\d+))?", str(text).strip())
    return None if not m else len(m.group(1) or "")


def _districts_found(cell, value, expected):
    """Whether a gate's `found` cell states a recomputed value. Text and exact sums (given as text) must be the same, numbers as
    numbers. A ratio (given as a fraction) must be the fraction rounded half up to the decimals the cell prints, and the cell
    must print at least as many decimals as the expected value has."""
    from fractions import Fraction
    if not isinstance(value, Fraction):
        return _districts_same(cell, value)
    shown, least = _districts_places(cell), _districts_places(expected)
    return shown is not None and least is not None and shown >= least and D(cell) == D(_districts_round(value, shown))


def _districts_met(gate, expected, value):
    """Whether a recomputed value meets a gate's expected value, by the rule the gate's own words state: within the number, where it
    says `within N of`; nothing to meet, where the gate lists and the expected value reads `a list`; a ratio rounded half up to the
    decimals the expected value has; otherwise equal, numbers as numbers and words as text."""
    import re
    from fractions import Fraction
    try:
        within = re.search(r"within (\d+(?:\.\d+)?) of", gate)
        if within:
            return abs(D(value) - D(expected)) <= D(within.group(1))
        if expected.strip() == "a list" and "listed" in gate:
            return True
        if isinstance(value, Fraction):
            return _districts_places(expected) is not None and D(_districts_round(value, _districts_places(expected))) == D(expected)
    except Exception:
        return False
    return _districts_same(expected, value)


def _districts_gates(need, alloc, units, cw, n_classed):
    """Every gate of gates_phase2.csv from the inputs: {gate: (found, held against)}. `found` is text (a count, an exact sum, yes
    or no, a list) or, for a ratio, the exact fraction; `held against` is the value recomputed here for the gates the build set
    itself, and None for the gates held against a value of the owner's (which _districts_OWNER carries). `need` and `alloc` are
    the two tables as this part recomputes them; `n_classed` the LGD units with a Scheduled Tribe share whose class by this
    part's rule is the layer's, and the number of such units."""
    from fractions import Fraction
    Z, DEF, codes = D(0), _districts_DEFAULT, sorted(cw, key=int)
    text = lambda x: format(x, "f")
    total = lambda table, col: sum((table[c][col] for c in codes), Z)
    g = {}
    g["the Scheduled Tribe class rule used here gives, for every LGD unit that has a share, the class the layer shows for it (`class_st_share` of 60_layer/layer_by_unit.csv); units compared"] = (str(n_classed[0]), str(n_classed[1]))
    stamps = sorted({alloc[c]["r620_pre_years_last_updated"] for c in codes})
    g["the stamp R6.20 prints on the four pre-period tables"] = (" / ".join(stamps), None)
    g["districts"] = (str(len(need)), None)
    g["N1, default window, summed over districts, ha (the three loss cells; within 2 of the owner's 89,657)"] = (text(total(need, f"n1_ha_{DEF}")), None)
    g["forest loss 2018-2025 over all units, summed over districts, ha (within 1 of 90,028)"] = (text(total(need, f"forest_loss_ha_{DEF}_all_units")), None)
    g["N2, summed over districts, ha (within 1 of 293,921)"] = (text(total(need, "n2_ha")), None)
    parts = all(need[c][f"n1_ha_{w}_lgd"] + need[c][f"n1_ha_{w}_outside"] == need[c][f"n1_ha_{w}"] for c in codes for w in _districts_WINDOWS)
    g["N1 of LGD-unit land plus N1 of outside-village land equals N1, every district and window"] = ("yes" if parts else "no", "yes")
    for name in ("plantation_pre", "plantation_post", "plantation_part_year", "nrm_pre", "nrm_post", "all_pre", "all_post"):
        g[f"r620_{name}_lakh, summed over districts (the gate of step 0)"] = (text(total(alloc, f"r620_{name}_lakh")), None)
    code_of = {v[1]: c for c, v in cw.items()}
    first = {c: Z for c in codes}                                    # plantation expenditure of FY2018-19, by district
    for r in rows(_districts_R620):
        if r["category"].strip() == "Plantation" and r["fy"].strip() == _districts_PERIODS["post"][0]:
            first[code_of[r["district"].strip()]] += D(r["exp_cat_lakh"])
    post = total(alloc, "r620_plantation_post_lakh")
    g["FY2018-19 as a per cent of post-period plantation expenditure (the owner's 53 per cent)"] = (Fraction(100) * Fraction(sum(first.values(), Z)) / Fraction(post), None)
    adds = all(first[c] + alloc[c]["r620_plantation_post_without_fy2018_19_lakh"] == alloc[c]["r620_plantation_post_lakh"] for c in codes)
    g["FY2018-19 plus FY2019-20 to 2025-26 equals the post period, every district"] = ("yes" if adds else "no", "yes")
    g["works of the dump that fall in no unit, crore rupees (the owner's 73.8)"] = (Fraction(total(alloc, "dump_no_unit_total_inr")) / 10 ** 7, None)
    by, later, missing = (total(alloc, f"dump_forest_named_{when}_inr") for when in _districts_WHENS)
    g["forest-named expenditure on works started by FY2017-18 as a per cent of all such expenditure in units, a missing start year counted as not started by then (the decision layer's 92.9)"] = (
        Fraction(100) * Fraction(by) / Fraction(by + later + missing), None)
    g["the dump's forest-named expenditure: by FY2017-18 + later + start year missing, summed over districts, equals the table's total"] = (
        text(by + later + missing), text(sum((_districts_money(r["expenditure_forest_named_worktype"]) for r in rows(_districts_DUMP_UNIT_FY)), Z)))
    share = Fraction(total(alloc, "r620_plantation_pre_lakh")) / Fraction(total(alloc, "r620_all_pre_lakh"))
    g["the pre-period plantation share of all expenditure, per cent (the owner's 20.2232)"] = (100 * share, None)
    g["that share applied to the post-period total, lakh (the owner's 743,148.16)"] = (share * Fraction(total(alloc, "r620_all_post_lakh")), None)
    g["LGD population / Scheduled Tribe population, summed over districts"] = (f"{sum(need[c]['population_lgd'] for c in codes)} / {sum(need[c]['st_pop_lgd'] for c in codes)}", None)
    for label, col, thirds in (("ADI", "adi_tercile", _districts_ADI_THIRDS), ("Scheduled Caste share", "sc_tercile", _districts_SC_THIRDS)):
        g[f"districts in each tercile of {label}"] = (" / ".join(str(sum(1 for c in codes if need[c].get(col) == x)) for x in thirds), None)
    g["C7: districts left out (most of N1 in units wholly under the East Coast model) - listed, not a gate on a value"] = (
        ", ".join(need[c]["district_name"] for c in codes if need[c]["left_out_of_c7"] == "yes"), "a list")
    g["the other reading of the rule: districts that hold the East Coast units the agreement headline left out - listed"] = (
        ", ".join(need[c]["district_name"] for c in codes if need[c]["left_out_under_the_other_rule"] == "yes"), "a list")
    g["N1 in units with no zone recorded, ha (so that the rule can be decided for every district)"] = (text(total(need, f"n1_ha_{DEF}_in_units_with_no_zone")), "0")
    left_out = sum(1 for r in rows(_districts_AGREEMENT) if r["unit_id"].strip() in units and r["assessed"].strip() == "1" and r["in_headline_population"].strip() == "0")
    g["units the agreement headline left out (assessed, wholly under the East Coast model), summed over districts"] = (str(sum(need[c]["n_assessed_units_east_coast_only"] for c in codes)), str(left_out))
    ids = [r.get("comparison") or "" for r in table("need_vs_allocation_summary.csv")]
    g["comparisons computed (the owner's thirteen and the second reading of C7)"] = (str(len(ids)) if sorted(ids) == sorted(_districts_COMPARISONS) else f"{len(ids)}: {sorted(ids)}", None)
    g["plantation works, state, FY2016-17 / FY2025-26 (the gate of step 0)"] = (
        f"{sum(alloc[c]['plantation_works_fy2016_17'] for c in codes)} / {sum(alloc[c]['plantation_works_fy2025_26'] for c in codes)}", None)
    return g


def _districts_pairs(t, want, cols):
    """For a check's detail: (district and column, the table's cell, the recomputed value, whether they are the same).
    A recomputed Decimal is compared as a number, an int as the text of the whole number, text as text. A district of the
    recomputation that has no row in the table is a difference too, so that a comparison cannot hold on a table that lacks a row."""
    pairs = []
    for r in t:
        code = r.get("pc11_district_code") or ""
        for col in cols:
            cell, w = r.get(col), want.get(code, {}).get(col)
            cell = "" if cell is None else cell
            if isinstance(w, Decimal):
                try:
                    same = D(cell) == w
                except Exception:
                    same = False
            else:
                same = w is not None and cell == str(w)
            pairs.append((f"{code} {r.get('district_name') or ''} {col}", cell, None if w is None else str(w), same))
    have = {(r.get("pc11_district_code") or "") for r in t}
    pairs += [(f"{code}: the table has no row for this district", None, "a row", False) for code in want if code not in have]
    return pairs


def _districts_number(cell):
    """A cell as an exact number; None if it is not one."""
    try:
        x = D(cell)
        return x if x.is_finite() else None
    except Exception:
        return None


def _districts_column_sum(t, col):
    """A column of a table added exactly; None if a cell of it is not a number."""
    cells = [_districts_number(r.get(col) or "") for r in t]
    return None if not cells or any(x is None for x in cells) else sum(cells, D(0))


def _districts_within(t, want, cols_of):
    """Pairs for a comparison to a tolerance: `want` is {code: {label: (value, tolerance)}} and `cols_of(label)` the columns of the
    table whose sum on the district's row is compared with the value."""
    pairs = []
    for r in t:
        code = r.get("pc11_district_code") or ""
        for label, (value, tol) in want.get(code, {}).items():
            cells = [_districts_number(r.get(col) or "") for col in cols_of(label)]
            mine = None if any(x is None for x in cells) else sum(cells, D(0))
            pairs.append((f"{code} {r.get('district_name') or ''} {label}", None if mine is None else str(mine), f"{value} (within {tol})", mine is not None and abs(mine - value) <= tol))
    have = {(r.get("pc11_district_code") or "") for r in t}
    pairs += [(f"{code}: the table has no row for this district", None, "a row", False) for code in want if code not in have]
    return pairs


def part_districts():
    import html
    import re
    import zipfile
    from fractions import Fraction
    _F = Fraction
    cw, wrong_cw = _districts_crosswalk()
    units, wrong_units = _districts_units(cw)
    ok = not wrong_cw and not wrong_units and len(cw) == 30 and len(units) == 11468
    check("inputs, recomputed for this part: the Odisha FRA table and the decision table carry one name for each census code; each of the 30 R6.20 names takes one code "
          "(case-folded census name, else the owner's spelling rule), the codes 370 to 399 each once; units.gpkg holds 11,468 units, each once and each with one of those codes "
          "(its own for an LGD panchayat unit, that of outside_village_district.csv for an outside-village unit)",
          ok, "" if ok else "; ".join((wrong_cw + wrong_units)[:3]) + f" (districts {len(cw)}, units {len(units)})")
    codes = sorted(cw, key=int)
    compared = {}                                                   # table -> the columns a check has compared, as the checks are made

    def compare(name, what, t, want, cols):
        compared.setdefault(name, set()).update(cols)
        pairs = _districts_pairs(t, want, cols)
        check(f"{name}: {what}", bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))

    def shape(name, t, want, in_order):
        cols, mine = _districts_header(name), list(want[codes[0]].keys())
        tcodes = [r.get("pc11_district_code") or "" for r in t]
        whole = all(None not in r and None not in r.values() for r in t)
        ok = len(t) == 30 and whole and len(cols) == len(set(cols)) and set(cols) == set(mine) and (tcodes == codes if in_order else sorted(tcodes) == sorted(codes))
        out_of_order = [f"row {i + 1} is {a!r}, not {b!r}" for i, (a, b) in enumerate(zip(tcodes, codes)) if a != b][:2] if in_order else []
        compared.setdefault(name, set()).add("pc11_district_code")
        check(f"{name}: 30 rows, one for each census code 370 to 399{', in ascending order of the code' if in_order else ''}; a cell for every column on every row; "
              f"its columns are the {len(mine)} this part recomputes, each once (a column it does not recompute fails here)",
              ok, "" if ok else f"rows {len(t)}; codes that are not one of 370 to 399: {sorted(set(tcodes) - set(codes))}; codes missing: {sorted(set(codes) - set(tcodes))}; "
              f"codes twice: {sorted({c for c in tcodes if tcodes.count(c) > 1})}; order: {out_of_order}; columns twice: {sorted({c for c in cols if cols.count(c) > 1})}; "
              f"columns not recomputed here: {sorted(set(cols) - set(mine))}; columns missing: {sorted(set(mine) - set(cols))}; a row with too few or too many cells: {not whole}")
        return cols

    def covered(name, cols):
        left = sorted(set(cols) - compared.get(name, set()))
        check(f"{name}: every column of the table was compared with a value recomputed from the inputs by one of the checks above (the columns are counted as the checks compare them, not from a list)",
              bool(cols) and not left, "" if not left else f"not compared: {left}")

    # ---- the Scheduled Tribe class: this part's own statement of the layer's rule, held against the layer's units -----------------------
    need_rows = {r["unit_id"].strip(): r for r in rows(_districts_NEED)}
    with_share = {u for u, r in need_rows.items() if units.get(u, (False, ""))[0] and r["st_share"].strip()}
    pairs, ties = [], []
    for r in rows(_districts_LAYER):
        u = r["unit_id"].strip()
        if u in with_share:
            pct = 100 * Fraction(D(need_rows[u]["st_share"]))
            mine = _districts_st_class(pct)
            pairs.append((u, r["class_st_share"], mine, r["class_st_share"] == mine))
            if _districts_st_tie(pct):
                ties.append(u)
    n_classed = (sum(1 for p in pairs if p[3]), len(with_share))
    ok = len(pairs) == len(with_share) > 0 and len({p[0] for p in pairs}) == len(pairs) and all(p[3] for p in pairs) and {p[2] for p in pairs} == set(_districts_ST_LABELS) and not ties
    check("inputs: this part's statement of the layer's Scheduled Tribe class rule (100 x st_share of the need table, rounded half up to two decimals; under 18; 18 to 33; above 33 to 50; above 50) "
          f"gives class_st_share of 60_layer/layer_by_unit.csv, label for label, for every LGD unit that has a share in the need table ({len(with_share)} units, each found once in the layer's table); "
          "all four labels occur among them; and no unit's per cent is exactly 17.995, 33.005 or 50.005, where the class would depend on how the tie is rounded",
          ok, "" if ok else f"units compared {len(pairs)} of {len(with_share)}; labels met: {sorted({p[2] for p in pairs})}; units on a tie: {ties[:3]}; " + mismatches(pairs))

    tiers = rows(_districts_TIERS)
    with_loss = sorted(r["cell"].strip() for r in tiers if r["loss_column"].strip() == "some")
    anr = [r["cell"].strip() for r in tiers if "assisted natural regeneration" in r["cell_name"].lower()]
    ok = with_loss == sorted(_districts_LOSS_CELLS) and anr == [_districts_ANR_CELL]
    check("inputs: in 55_decision/tiers.csv the cells whose loss_column is `some` are open_loss, dense_loss and little_loss (the three this part sums N1 over), "
          "and the one cell whose name speaks of assisted natural regeneration is open_none (the one it sums N2 over)", ok, "" if ok else f"loss recorded: {with_loss}; assisted natural regeneration: {anr}")

    # ---- district_need.csv --------------------------------------------------------------------------------------------------------
    T = "district_need.csv"
    want, second, wrong, n1_of_unit = _districts_need(units, cw)
    need = want
    check(f"inputs for {T}: each per-unit table (decision, Hansen by band, agreement, need) holds every unit of units.gpkg once; the agreement table has no zone model but the four the definition names; "
          "every district has LGD population and an LGD unit with an adi_2011; no district's Scheduled Tribe per cent is on a rounding tie of the class rule; the rule for C7 reads the same on the exact share and on the share as printed; "
          "the thirds are the same ranked by the exact values and by the printed ones", not wrong, "; ".join(wrong[:3]))
    t = table(T)
    cols = shape(T, t, want, True)
    num, text = "as numbers, exactly (decimal sums over the district's units)", "as text"
    compare(T, f"district_name and r620_district = the crosswalk recomputed from the inputs, {text}", t, want, ["district_name", "r620_district"])
    compare(T, "n_units, n_units_lgd, n_units_outside = the district's units in units.gpkg: all, LGD panchayat, outside-village; as whole numbers", t, want, ["n_units", "n_units_lgd", "n_units_outside"])
    compare(T, f"forest_2000_ha, _lgd, _outside = dense_2000_ha + open_2000_ha of the decision table, {num}", t, want, ["forest_2000_ha", "forest_2000_ha_lgd", "forest_2000_ha_outside"])
    for w in _districts_WINDOWS:
        compare(T, f"window {w}: n1_ha_{w}, _lgd, _outside (forest_loss_ha_{w} over the units whose cell_{w} is open_loss, dense_loss or little_loss), forest_loss_ha_{w}_all_units, "
                   f"loss_below_minimum_ha_{w} (all units less N1), forest_at_window_start_ha_{w} = the decision table summed, {num}",
                t, want, [f"n1_ha_{w}", f"n1_ha_{w}_lgd", f"n1_ha_{w}_outside", f"forest_loss_ha_{w}_all_units", f"loss_below_minimum_ha_{w}", f"forest_at_window_start_ha_{w}"])
        compare(T, f"window {w}: n_units_loss_cells_{w} = the number of the district's units whose cell_{w} is one of the three loss cells, as a whole number", t, want, [f"n_units_loss_cells_{w}"])
    compare(T, f"n2_ha, _lgd, _outside = standing_open_ha over the units whose cell_2018_2025 is open_none, {num}", t, want, ["n2_ha", "n2_ha_lgd", "n2_ha_outside"])
    compare(T, "n_units_anr = the number of the district's units whose cell_2018_2025 is open_none, as a whole number", t, want, ["n_units_anr"])
    compare(T, f"loss_2001_2013_ha = the yearly loss of 2001 to 2013, dense band plus open band, of the per-year Hansen table, {num}", t, want, ["loss_2001_2013_ha"])
    zone_cols = [f"n1_ha_2018_2025_{z}" for z in _districts_ZONES.values()]
    compare(T, f"the four columns that split n1_ha_2018_2025 by corestack_zone_model of the agreement table (`ECPHR only`, `EPAHR only`, `both models`, blank), {num}", t, want, zone_cols)
    compare(T, "east_coast_share_of_n1_pct = 100 x the East-Coast-only part / n1_ha_2018_2025, rounded half up to six decimals and printed with six; blank where N1 is zero; as text", t, want, ["east_coast_share_of_n1_pct"])
    compare(T, "n_assessed_units_east_coast_only = the district's units with assessed = 1 and zone model `ECPHR only`, as a whole number", t, want, ["n_assessed_units_east_coast_only"])
    compare(T, "left_out_of_c7 = yes where the East Coast share of N1 is above 50, else no (no where N1 is zero); left_out_under_the_other_rule = yes where n_assessed_units_east_coast_only is above 0, else no; as text",
            t, want, ["left_out_of_c7", "left_out_under_the_other_rule"])
    compare(T, "population_lgd, st_pop_lgd, sc_pop_lgd = population, st_pop, sc_pop of the need table summed over the district's LGD panchayat units, as whole numbers", t, want, ["population_lgd", "st_pop_lgd", "sc_pop_lgd"])
    compare(T, "st_share_pct = 100 x st_pop_lgd / population_lgd and sc_share_pct = 100 x sc_pop_lgd / population_lgd, rounded half up to six decimals and printed with six, as text", t, want, ["st_share_pct", "sc_share_pct"])
    compare(T, "st_class = the layer's class of the exact Scheduled Tribe per cent (rounded half up to two decimals; under 18; 18 to 33; above 33 to 50; above 50), with the layer's labels, as text", t, want, ["st_class"])
    compare(T, "sc_tercile = 10, 10 and 10 districts by ascending exact Scheduled Caste share, ties by census code, as text; the three labels are the table's own (`lowest third of Scheduled Caste share`, `middle third`, "
               "`highest third of Scheduled Caste share`): the definitions give none for this column", t, want, ["sc_tercile"])
    compare(T, "adi_2011 = the mean of adi_2011 of the need table over the district's LGD units that have a value, weighted by the unit's population; adi_2011_population_covered_pct = 100 x the population of those units / population_lgd; "
               "both rounded half up to six decimals and printed with six, as text", t, want, ["adi_2011", "adi_2011_population_covered_pct"])
    compare(T, "n_units_lgd_with_adi = the number of the district's LGD units that have an adi_2011, as a whole number", t, want, ["n_units_lgd_with_adi"])
    compare(T, "adi_tercile = 10, 10 and 10 districts by ascending exact adi_2011, ties by census code, labelled `lowest third of the index`, `middle third`, `highest third of the index`, as text", t, want, ["adi_tercile"])
    covered(T, cols)
    compare(T, "from a second source, the per-year Hansen table in place of the decision table's hectares (the cells still the decision table's): forest_2000_ha = the land of the bands above 30 and 10 to 30; "
               "for each of the four windows, forest_loss_ha_all_units = the two bands' loss of the window's years, n1_ha and loss_below_minimum_ha = that loss in and out of the three loss cells, "
               "forest_at_window_start_ha = each band's land in 2000 less its loss before the window, not below zero; n2_ha = the open band's land less its loss of 2001 to 2025, not below zero, in the open_none cell; "
               f"with the _lgd and _outside parts; {num}", t, second, sorted(second[codes[0]]))
    by_cells, wrong = _districts_second_cells(cw)
    pairs = _districts_pairs(t, by_cells, sorted(by_cells[codes[0]]))
    check(f"{T}, from a second source, the decision stage's own count of units by window, district name and cell (55_decision/condition_cells_by_district.csv, 4 windows x 30 districts x 6 cells): "
          "n_units_loss_cells of each of the four windows = its units in the three loss cells; n_units_anr = its units in open_none, window 2018_2025; n_units = its units in the six cells, the same in each window; "
          "n_units_outside = its outside-village units; n_units_lgd = the rest; as whole numbers", not wrong and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    state, wrong = _districts_second_state()
    pairs = []
    for col, (value, tol) in state.items():
        mine = _districts_column_sum(t, col)
        pairs.append((col + ", summed over the districts", None if mine is None else str(mine), f"{value} (within {tol})", mine is not None and abs(mine - value) <= tol))
    check(f"{T}, against the totals the decision stage prints for the state (55_decision/condition_cells.csv, hectares to 0.01 ha), each column summed over the 30 districts: n1_ha of each window with its _lgd and _outside parts "
          "= the window's forest loss in the three loss cells, for all units, LGD panchayat units and outside-village units (within 0.015 ha: three figures of 0.005); forest_loss_ha_all_units = that loss in the six cells (within 0.03 ha) "
          "and loss_below_minimum_ha = that in the three other cells (within 0.015 ha); n2_ha, _lgd, _outside = standing_open_ha of open_none, window 2018_2025 (within 0.005 ha); "
          "n_units_loss_cells of each window, n_units_anr, n_units, n_units_lgd and n_units_outside = its counts of units, exactly",
          not wrong and len(t) == 30 and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    by_zone, wrong = _districts_second_zone(units, n1_of_unit)
    pairs = _districts_pairs(t, by_zone, sorted(by_zone[codes[0]]))
    check(f"{T}, from a second source: the four columns that split n1_ha_2018_2025 = N1 split by which zone model's hectares 20_degradation/corestack_by_unit.csv gives the unit (corestack_value_ha_zone_ECPHR alone above zero, "
          "corestack_value_ha_zone_EPAHR alone, both, neither), which is the same split because that table gives every unit with a zone model in the agreement table the same model and the units without one hold no N1 (both held here); "
          "n_assessed_units_east_coast_only = the units the agreement table's own flag leaves out of its headline (assessed = 1, in_headline_population = 0); and, made of that split and that count, east_coast_share_of_n1_pct "
          "(100 x the East-Coast-only part / the four parts added, rounded half up to six decimals; blank where they add to zero), left_out_of_c7 (yes where that share is above 50) and left_out_under_the_other_rule (yes where that count is above 0); "
          "hectares as numbers, exactly; the count as a whole number; the share and the two rules as text",
          not wrong and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    people, wrong = _districts_second_people(cw)
    pairs = _districts_pairs(t, people, sorted(people[codes[0]]))
    check(f"{T}, from a second source, the layer's own per-unit table (60_layer/layer_by_unit.csv) with the district code and unit level it carries itself: population_lgd, st_pop_lgd, sc_pop_lgd, n_units_lgd_with_adi as whole numbers; "
          "st_share_pct, sc_share_pct, adi_2011 and adi_2011_population_covered_pct made of its population, st_pop, sc_pop and adi_2011 by the same definitions, rounded half up to six decimals, as text; "
          "and, made of those exact values, st_class (the layer's rule), sc_tercile and adi_tercile (10, 10 and 10 districts by ascending value, ties by census code), as text",
          not wrong and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))

    # ---- district_allocation.csv ------------------------------------------------------------------------------------------------------
    T = "district_allocation.csv"
    want, wrong = _districts_allocation(units, cw)
    alloc = want
    check(f"inputs for {T}: R6.20 has one row for each of 30 districts x 3 categories x 13 years and one exp_all_lakh per district-year; its state file has one row for each of 3 categories x 13 years, the stamp {_districts_STAMP} "
          "on the four pre years and on no later year; every unit and start year of the dump's per-unit table, and every file of its no-unit table, could be placed", not wrong, "; ".join(wrong[:3]))
    t = table(T)
    cols = shape(T, t, want, False)
    exact = "as numbers, exactly (decimal sums)"
    compare(T, f"district_name and r620_district = the crosswalk recomputed from the inputs, {text}", t, want, ["district_name", "r620_district"])
    compare(T, "r620_plantation_pre_lakh (FY2014-15 to 2017-18), _post_lakh (FY2018-19 to 2025-26), _part_year_lakh (FY2026-27) and r620_plantation_post_without_fy2018_19_lakh (FY2019-20 to 2025-26) "
               f"= exp_cat_lakh of R6.20, category Plantation, summed, {exact}",
            t, want, ["r620_plantation_pre_lakh", "r620_plantation_post_lakh", "r620_plantation_part_year_lakh", "r620_plantation_post_without_fy2018_19_lakh"])
    compare(T, f"r620_nrm_ and r620_water_ pre, post and part_year lakh = exp_cat_lakh of R6.20, categories NRM and Water, summed over the same three periods, {exact}",
            t, want, [f"r620_{n}_{p}_lakh" for n in ("nrm", "water") for p in _districts_PERIODS])
    compare(T, f"r620_all_ pre, post and part_year lakh = exp_all_lakh of R6.20, one value per district-year, summed over the same three periods, {exact}", t, want, [f"r620_all_{p}_lakh" for p in _districts_PERIODS])
    compare(T, "plantation_pct_of_all_pre and _post = 100 x plantation / all expenditure of the period, rounded half up to six decimals and printed with six, as text", t, want, ["plantation_pct_of_all_pre", "plantation_pct_of_all_post"])
    compare(T, "plantation_works_fy2016_17 and _fy2025_26 = works_ongoing + works_completed of R6.20, category Plantation, in that year, as whole numbers", t, want, ["plantation_works_fy2016_17", "plantation_works_fy2025_26"])
    compare(T, f"r620_pre_years_last_updated = the one stamp (last_updated) the R6.20 state totals file carries on the four years FY2014-15 to 2017-18, which is {_districts_STAMP}, as text", t, want, ["r620_pre_years_last_updated"])
    for name, col in _districts_KINDS:
        compare(T, f"dump_{name}_started_by_fy2017_18_inr, _started_later_inr and _start_year_missing_inr = {col} of allocation_by_unit_fy.csv summed over the units of the district (the unit's district as recomputed here) "
                   f"and over the rows whose fy_work_start is 2017-18 or earlier, later, and NA; {exact}; a blank cell adds nothing", t, want, [f"dump_{name}_{when}_inr" for when in _districts_WHENS])
    compare(T, "n_units_with_forest_named_by_fy2017_18 = the number of the district's units whose expenditure_forest_named_worktype, summed over start years to 2017-18, is above zero; as a whole number", t, want, ["n_units_with_forest_named_by_fy2017_18"])
    compare(T, "dump_no_unit_total_inr, _forest_named_inr, _plantation_category_inr = expenditure_total, _forest_named_worktype, _plantation_category of allocation_unassigned.csv summed over every start year, "
               f"by the district that assets_district_fy.csv gives the file the works came in; {exact}", t, want, ["dump_no_unit_total_inr", "dump_no_unit_forest_named_inr", "dump_no_unit_plantation_category_inr"])
    covered(T, cols)
    printed, pairs = {}, []                                         # what R6.20 prints for the state, by category and year
    for r in rows(_districts_R620_STATE):
        printed[(r["category"].strip(), r["fy"].strip())] = (D(r["exp_cat_lakh"]), D(r["exp_all_lakh"]), int(r["works_ongoing"]) + int(r["works_completed"]))
    spans = dict(_districts_PERIODS, post_without_fy2018_19=_districts_POST_WITHOUT_FIRST)
    for col, key, span in ([(f"r620_{n}_{p}_lakh", k, p) for n, k in (("plantation", "Plantation"), ("nrm", "NRM"), ("water", "Water"), ("all", None)) for p in _districts_PERIODS]
                           + [("r620_plantation_post_without_fy2018_19_lakh", "Plantation", "post_without_fy2018_19")]):
        total = sum((printed[(key or "Plantation", f)][0 if key else 1] for f in spans[span]), D(0))
        mine = _districts_column_sum(t, col)
        pairs.append((col + ", summed over the districts", None if mine is None else str(mine), str(total), mine == total))
    for col, fy in (("plantation_works_fy2016_17", "2016-2017"), ("plantation_works_fy2025_26", "2025-2026")):
        cells = [r.get(col) or "" for r in t]
        mine = sum(int(x) for x in cells) if cells and all(x.isdigit() for x in cells) else None
        pairs.append((col + ", summed over the districts", mine, printed[("Plantation", fy)][2], mine == printed[("Plantation", fy)][2]))
    check(f"{T}, against the totals R6.20 prints for the state (the state totals file): each of the 13 R6.20 money columns summed over the districts = the state's exp_cat_lakh (exp_all_lakh, one value a year, for the `all` columns) "
          "summed over the same years, as numbers, exactly; plantation_works of FY2016-17 and of FY2025-26 summed = the state's works_ongoing + works_completed, as whole numbers",
          len(t) == 30 and all(p[3] for p in pairs), mismatches(pairs))
    stage3, wrong = _districts_second_r620(cw)
    pairs = _districts_pairs(t, stage3, sorted(stage3[codes[0]])) if stage3 else []
    check(f"{T}, from a second source, stage 3's own table of the report by district and year (40_allocation/district_fy_r620_vs_dump.csv, 390 district-years, by the census code and the R6.20 name it carries itself): "
          "the 13 R6.20 money columns = its r620_exp_plantation_lakh, _nrm_lakh, _water_lakh and _all_lakh summed over the same years, as numbers, exactly; plantation_pct_of_all_pre and _post made of those sums, as text; "
          "plantation_works of FY2016-17 and FY2025-26 = its r620_works_plantation of that year, as whole numbers; r620_pre_years_last_updated = the one r620_last_updated of the district's four pre years, as text",
          not wrong and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    per_unit, no_unit, state, outside, wrong = _districts_second_dump(units, cw)
    span = lambda tols: (lambda v: f"{min(v)} to {max(v)}")(sorted(tols)) if tols else "none"
    rule = ("half a paisa for each cell added, on either side, that holds a work of the kind (each money cell of the dump's tables is rounded to the paisa; a cell with no work of the kind adds nothing, "
            "which is held here for every table read)")
    pairs = _districts_within(t, per_unit, lambda name: [f"dump_{name}_{when}_inr" for when in _districts_WHENS])
    check(f"{T}, from a second source, the dump's per-unit table without start years (40_allocation/allocation_by_unit.csv): for forest-named work types and for the plantation category, the three columns "
          f"(started by FY2017-18, later, start year missing) added = that expenditure summed over the district's units, to within {rule}: "
          f"{span([v[1] for kinds in per_unit.values() for v in kinds.values()])} rupees for a district and a kind", not wrong and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    pairs = _districts_within(t, {c: {"dump_no_unit_total_inr": v} for c, v in no_unit.items()}, lambda label: [label])
    check(f"{T}, from a second source, the join's own account of each district file (40_allocation/allocation_join_qa.csv, column expenditure_unassigned; the file's district from 40_allocation/assets_file_qa.csv): "
          "dump_no_unit_total_inr = the expenditure of the file's works that fell in no unit, to within half a paisa for that figure and for each row of allocation_unassigned.csv added",
          not wrong and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    pairs = []
    for (name, when), (value, tol) in state.items():
        col = f"dump_{name}_{_districts_WHENS[when]}_inr"
        mine = _districts_column_sum(t, col)
        pairs.append((col + ", summed over the districts", None if mine is None else str(mine), f"{value} (within {tol})", mine is not None and abs(mine - value) <= tol))
    check(f"{T}, against the dump's own table of every work by district file and start year (40_allocation/assets_district_fy.csv): each of the six dump columns by start year, summed over the districts, "
          f"= that expenditure of every work with such a start year, less that of the works in no unit (allocation_unassigned.csv), to within {rule}: {span([v[1] for v in state.values()])} rupees for a column "
          "(the works in no unit are left out of these columns, and no other work is)", not wrong and len(t) == 30 and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))
    pairs = []
    for name, (value, tol) in outside.items():
        col = f"dump_no_unit_{name}_inr"
        mine = _districts_column_sum(t, col)
        pairs.append((col + ", summed over the districts", None if mine is None else str(mine), f"{value} (within {tol})", mine is not None and abs(mine - value) <= tol))
    check(f"{T}, from a second source for the works in no unit, the dump's table of every work (40_allocation/assets_district_fy.csv) and its per-unit table (40_allocation/allocation_by_unit.csv), neither of which the three columns are made of: "
          "dump_no_unit_total_inr, _forest_named_inr and _plantation_category_inr, each summed over the districts, = expenditure_total, _forest_named_worktype and _plantation_category of every work less that of the works that fall in a unit, "
          f"to within {rule}: {span([v[1] for v in outside.values()])} rupees for a column (the state only: the inputs do not give the works in no unit by district and kind a second time)",
          not wrong and len(t) == 30 and bool(pairs) and all(p[3] for p in pairs), "; ".join(wrong[:2]) or mismatches(pairs))

    # ---- the step's own gates -----------------------------------------------------------------------------------------------------------
    T = _districts_GATES
    g = _districts_gates(need, alloc, units, cw, n_classed)
    t, cols = table(T), _districts_header(T)
    gates = [r.get("gate") or "" for r in t]
    row_of = {(r.get("gate") or ""): r for r in t}
    cell = lambda gate, col: (row_of[gate].get(col) or "") if gate in row_of else None
    ok = cols == ["gate", "expected", "found", "pass"] and all(None not in r and None not in r.values() for r in t) and len(set(gates)) == len(gates) and set(gates) == set(g)
    check(f"{T}: {len(g)} rows; columns gate, expected, found, pass, a cell for each on every row; no gate twice; its gates are exactly the {len(g)} this part recomputes (a gate it has no recomputation for fails here)",
          ok, "" if ok else f"rows {len(t)}; columns {cols}; gates twice: {sorted({x for x in gates if gates.count(x) > 1})[:3]}; gates not recomputed here: {sorted(set(gates) - set(g))[:3]}; "
          f"gates missing from the table: {sorted(set(g) - set(gates))[:3]}")
    plain = {gate: v for gate, v in g.items() if not isinstance(v[0], _F)}
    ratio = {gate: v for gate, v in g.items() if isinstance(v[0], _F)}
    pairs = [(gate, cell(gate, "found"), v[0], gate in row_of and _districts_found(cell(gate, "found"), v[0], cell(gate, "expected"))) for gate, v in plain.items()]
    check(f"{T}: `found` of the {len(plain)} gates that state a count, an exact sum, yes or no, a stamp or a list of districts = the value recomputed from the inputs (through district_need.csv and district_allocation.csv "
          "as this part recomputes them; the comparisons counted in need_vs_allocation_summary.csv and held against the fourteen the definitions name); numbers as numbers, words as text; a gate that is not in the table fails",
          bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    pairs = [(gate, cell(gate, "found"), _districts_round(v[0], _districts_places(cell(gate, "found")) or 0) if gate in row_of else None,
              gate in row_of and _districts_found(cell(gate, "found"), v[0], cell(gate, "expected"))) for gate, v in ratio.items()]
    check(f"{T}: `found` of the {len(ratio)} gates that state a ratio (FY2018-19 as a per cent of the post period's plantation expenditure; the works in no unit in crore rupees; forest-named expenditure on works started by FY2017-18 "
          "as a per cent of all of it in units; the pre-period plantation share of all expenditure in per cent; that share, unrounded, applied to the post-period total) = the exact value recomputed from the inputs, "
          "rounded half up to the decimals the cell prints, which are no fewer than the expected value has", bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    bad = [(r.get("gate"), r.get("pass")) for r in t if r.get("pass") != "yes"]
    check(f"{T}: pass = yes on every row of the table", bool(t) and not bad, "" if not bad else f"{len(bad)} of {len(t)} not yes, e.g. {bad[:3]}")
    owner = _districts_OWNER
    build = {gate: v[1] for gate, v in g.items() if v[1] is not None}
    split = not (set(owner) & set(build)) and set(owner) | set(build) == set(g)
    pairs = [(gate, cell(gate, "expected"), value, gate in row_of and _districts_same(cell(gate, "expected"), value)) for gate, value in owner.items()]
    check(f"{T}: `expected` of the {len(owner)} gates held against a value of the owner's = the value his instruction of 10 October 2026 gives (the table of Phase 0.3 for the gates of step 0 and the hectares; Phase 2 for the stamp, "
          "the 53 per cent, the 73.8 crore, the 92.9 per cent, the 20.2232 per cent and the 743,148.16 lakh, the terciles of 10, 10 and 10, the 30 districts and the thirteen comparisons, to which the second reading of C7 adds one), "
          "which this script holds as he wrote it, thousands separators and units apart; numbers as numbers, words as text; no tolerance applies to this column",
          split and all(p[3] for p in pairs), ("" if split else "the gates held here as the owner's and as the build's are not, together, the gates recomputed; ") + mismatches(pairs))
    pairs = [(gate, cell(gate, "expected"), value, gate in row_of and _districts_same(cell(gate, "expected"), value)) for gate, value in build.items()]
    check(f"{T}: `expected` of the other {len(build)} gates = what each holds its value against, recomputed from the inputs: the LGD units that have a Scheduled Tribe share in the need table; `yes` for the two identities; "
          "expenditure_forest_named_worktype of allocation_by_unit_fy.csv summed over all its rows; `a list` for the two gates that list districts; 0 hectares of N1 in units with no zone; "
          "the units the agreement table's own flag leaves out of its headline (assessed = 1, in_headline_population = 0); numbers as numbers, words as text",
          split and bool(pairs) and all(p[3] for p in pairs), mismatches(pairs))
    pairs = [(gate, cell(gate, "expected"), str(v[0]) if not isinstance(v[0], _F) else _districts_round(v[0], 6), gate in row_of and _districts_met(gate, cell(gate, "expected"), v[0])) for gate, v in g.items()]
    check(f"{T}: `expected` of each of the {len(g)} gates is met by the value recomputed from the inputs, by the rule the gate's words state (within the number, where it says `within 1 of` or `within 2 of`; "
          "nothing to meet, where the gate lists districts and the expected value reads `a list`; a ratio rounded half up to the decimals the expected value has; otherwise equal: numbers as numbers, words as text)",
          all(p[3] for p in pairs), mismatches(pairs))

    # ---- the step's section of the record of provenance ------------------------------------------------------------------------------------
    T = "gap.provenance.json"
    try:
        record = json.loads((GAP / T).read_text(encoding="utf-8"))
    except Exception:
        record = {}
    sec = record.get("steps", {}).get(_districts_STEP, {}) if isinstance(record, dict) and isinstance(record.get("steps"), dict) else {}
    sec = sec if isinstance(sec, dict) else {}
    wrong = [] if sec else [f"no section {_districts_STEP}"]
    outs = sorted(sec.get("outputs")) if isinstance(sec.get("outputs"), dict) else []
    if outs != sorted("50_gap/" + n for n in _districts_STEP_WRITES):
        wrong.append(f"its outputs are {outs}")
    gate_rows = table(_districts_GATES)
    n_yes = sum(1 for r in gate_rows if r.get("pass") == "yes")
    if (sec.get("gates"), sec.get("gates_passed")) != (len(gate_rows), n_yes) or isinstance(sec.get("gates"), bool) or isinstance(sec.get("gates_passed"), bool):
        wrong.append(f"gates {sec.get('gates')!r} and gates_passed {sec.get('gates_passed')!r}; gates_phase2.csv has {len(gate_rows)} rows, {n_yes} with pass = yes")
    seeds = {"base": _districts_SEED, "generator": "numpy.random.default_rng",
             "by_comparison": {c: {"permutation": _districts_SEED + 100 + k, "bootstrap": _districts_SEED + 200 + k} for k, c in enumerate(_districts_COMPARISONS)}}
    if sec.get("seeds") != seeds or (sec.get("permutations"), sec.get("bootstrap_resamples")) != (99999, 9999):
        wrong.append(f"seeds, permutations or bootstrap_resamples: {str(sec.get('seeds'))[:160]}, {sec.get('permutations')!r}, {sec.get('bootstrap_resamples')!r}")
    names = {r["cell"].strip(): r["cell_name"] for r in tiers}
    if sec.get("cell_names") != {c: names.get(c) for c in _districts_LOSS_CELLS + (_districts_ANR_CELL,)}:
        wrong.append(f"cell_names {sec.get('cell_names')!r}")
    rule = sec.get("c7_rule") if isinstance(sec.get("c7_rule"), dict) else {}
    for key, col in (("districts_left_out", "left_out_of_c7"), ("districts_left_out_under_it", "left_out_under_the_other_rule")):
        mine = [need[c]["district_name"] for c in codes if need[c].get(col) == "yes"]
        if rule.get(key) != mine:
            wrong.append(f"c7_rule.{key} {rule.get(key)!r}, recomputed {mine}")
    if (sec.get("st_classes") if isinstance(sec.get("st_classes"), dict) else {}).get("labels") != list(_districts_ST_LABELS):
        wrong.append(f"st_classes.labels {sec.get('st_classes')!r}")
    check(f"{T}, the section of this step ({_districts_STEP}): its `outputs` are the seven files the step writes (50_gap/ " + ", ".join(_districts_STEP_WRITES) + "); `gates` = the number of rows of gates_phase2.csv and "
          "`gates_passed` = the number of them with pass = yes; `seeds` = base 20261010, numpy.random.default_rng, and for the k-th of the 14 comparisons (C1 ... C12 with C7b after C7, then B1; k from 0) permutation base + 100 + k, "
          "bootstrap base + 200 + k; `permutations` 99999 and `bootstrap_resamples` 9999; `cell_names` = cell_name of 55_decision/tiers.csv for open_loss, dense_loss, little_loss and open_none; "
          "`c7_rule.districts_left_out` and `.districts_left_out_under_it` = the districts whose recomputed left_out_of_c7 and left_out_under_the_other_rule is yes, by name in the order of the census code; "
          "`st_classes.labels` = the layer's four labels", not wrong, "; ".join(wrong[:4]))
    said = (sec.get("adi") if isinstance(sec.get("adi"), dict) else {}).get("direction")
    said = said if isinstance(said, dict) else {}
    wrong = []
    for path in ("docs/NEED.md", "00_raw/docs/Village_level_dataset_schema_31Oct2022.docx"):
        sentence = said.get(path)
        try:
            if path.endswith(".docx"):
                with zipfile.ZipFile(ROOT / path) as z:
                    body = html.unescape(re.sub(r"<[^>]+>", "", z.read("word/document.xml").decode("utf-8")))
            else:
                body = (ROOT / path).read_text(encoding="utf-8")
        except Exception as e:
            body = ""
            wrong.append(f"{path}: cannot be read ({type(e).__name__})")
        if not isinstance(sentence, str) or len(sentence.split()) < 5 or " ".join(sentence.split()) not in " ".join(body.split()):
            wrong.append(f"{path}: the words quoted from it are not in it, or are fewer than five: {sentence!r}")
    check(f"{T}, the section of this step: under `adi.direction`, the words quoted from docs/NEED.md and from the group's data dictionary (00_raw/docs/Village_level_dataset_schema_31Oct2022.docx) for the way the index runs "
          "are in those two documents, word for word (white space apart; the dictionary's text as its word/document.xml gives it, tags removed)", bool(said) and not wrong, "; ".join(wrong) if said else "no adi.direction")

# ---------------------------------------------------------------------------------------------------------------------
# part_comparisons: need_vs_allocation.csv, need_vs_allocation_summary.csv, marginalisation_split.csv, what_more.csv
# Taken as given (another part checks them against the inputs): district_need.csv, district_allocation.csv.
# Written from the definitions in the builders' docstrings; no builder was read.
# ---------------------------------------------------------------------------------------------------------------------
_comparisons_LIST = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C7b", "C8", "C9", "C10", "C11", "C12", "B1"]
_comparisons_SEED_BASE = 20261010          # the builders' base seed: comparison k has base + 100 + k and base + 200 + k
_comparisons_N_PERMUTATIONS = 99999
_comparisons_N_BOOTSTRAP = 9999
_comparisons_OWN_SEED = 771000000          # this script's own draws start here; nothing to do with the builders' seeds
_comparisons_OWN_BOOTSTRAPS = 20           # own bootstraps of 9,999 draws each: the first is "this script's interval",
                                           # all of them measure how far such an interval's end moves from one bootstrap to the next
_comparisons_GAP_IS = "the same money distributed by need; not a requirement"
_comparisons_INTENSITY_IS = "an intensity, not a requirement: works have no standard size"
_comparisons_SCALE_IS = "the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier years are a frozen 2020 snapshot"
_comparisons_ADI_TITLE = "Aggregate Development Index 2011"     # the index's name in the layer's list of sources


def _comparisons_fr(cell):
    """A cell as an exact fraction."""
    from fractions import Fraction
    return Fraction(D(cell))


def _comparisons_round(x, places):
    """A fraction rounded half up to `places` decimals, exactly; a tie goes away from zero, as decimal.ROUND_HALF_UP. A Decimal."""
    n = x * 10 ** places
    a = abs(n)
    k = a.numerator // a.denominator
    if 2 * (a - k) >= 1:
        k += 1
    return Decimal(-k if n < 0 else k).scaleb(-places)


def _comparisons_number(cell, exact):
    """True where a cell is a number equal to the exact value ('12.5' equals '12.50'); False for a blank, for text, and for a number with white space around it."""
    try:
        return cell not in ("", None) and cell == cell.strip() and _comparisons_fr(cell) == exact
    except Exception:
        return False


def _comparisons_printed(cell, exact, places):
    """True where a cell prints `places` decimals and is the exact value rounded half up to them; where exact is None, where the cell is blank."""
    if exact is None:
        return cell == ""
    try:
        d = D(cell)
    except Exception:
        return False
    return cell == cell.strip() and d.is_finite() and -d.as_tuple().exponent == places and d == _comparisons_round(exact, places)


def _comparisons_show(exact, places=None):
    """An expected value as text for a check's detail."""
    if exact is None:
        return ""
    if places is not None:
        return str(_comparisons_round(exact, places))
    return str(exact.numerator) if exact.denominator == 1 else str(float(exact))


def _comparisons_header(name):
    """The header of a table of the folder being checked: its column names as written, a name written twice staying twice."""
    with open(GAP / name, encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def _comparisons_ragged(rws):
    """How many rows of a table do not have exactly the header's cells."""
    return sum(1 for r in rws if None in r or any(v is None for v in r.values()))


def _comparisons_whole(rws):
    """The rows with a missing cell, or a column the header lacks, read as blank, and cells beyond the header dropped: a ragged row or a lost column then fails its checks instead of stopping the part."""
    from collections import defaultdict
    return [defaultdict(str, {k: ("" if v is None else v) for k, v in r.items() if k is not None}) for r in rws]


def _comparisons_codes(values):
    """Each exact value's place among the sorted distinct values, and how many distinct values there are: equal values share a place, so a tie is exact."""
    place = {v: i for i, v in enumerate(sorted(set(values)))}
    return np.array([place[v] for v in values], dtype=np.int64), len(place)


def _comparisons_twice_ranks(codes, m):
    """Twice the average rank of every entry within its row: 2 x (entries of the row below it) + (entries equal to it) + 1. Whole numbers.

    `codes` holds whole numbers from 0 to m - 1, one row per sample."""
    rws = codes.reshape(-1, codes.shape[-1])
    counts = np.bincount((rws + m * np.arange(len(rws))[:, None]).ravel(), minlength=len(rws) * m).reshape(len(rws), m)
    below = np.cumsum(counts, axis=1) - counts
    return (2 * np.take_along_axis(below, rws, 1) + np.take_along_axis(counts, rws, 1) + 1).reshape(codes.shape)


def _comparisons_spearman(xs, ys, seed, n_permutations, n_bootstrap, n_bootstraps):
    """Spearman's rho with average ranks for ties, and this script's own permutation p and bootstrap intervals.

    Ranks are made from exact values. With A and B twice the average ranks, sum(A) = sum(B) = n(n + 1), so the centred
    cross product is T = sum(A * B) - n(n + 1)^2, a whole number, and rho = T / sqrt(SA * SB) with SA, SB the centred
    sums of squares. A shuffle of y against x keeps SA and SB, so its |rho| is at least the observed |rho| exactly
    when its |T| is at least the observed |T|: that comparison is made in whole numbers.
      p         (1 + shuffles with |rho| at least the observed) / (1 + n_permutations), two-sided
      intervals n_bootstraps of them; each from n_bootstrap draws of the pairs with replacement, ranks made afresh in
                every draw; the 2.5th and 97.5th percentiles of the rho of the draws in which rho is defined
    Returns rho, p and the intervals (one row each: lower end, upper end).
    """
    cx, mx = _comparisons_codes(xs)
    cy, my = _comparisons_codes(ys)
    n = len(xs)
    c = n * (n + 1) ** 2
    A, B = _comparisons_twice_ranks(cx, mx), _comparisons_twice_ranks(cy, my)
    T, SA, SB = int((A * B).sum()) - c, int((A * A).sum()) - c, int((B * B).sum()) - c
    rho = T / math.sqrt(SA * SB) if SA > 0 and SB > 0 else float("nan")
    rng = np.random.default_rng(seed)
    shuffled = rng.permuted(np.tile(B, (n_permutations, 1)), axis=1)
    p = (1 + int((np.abs(shuffled @ A - c) >= abs(T)).sum())) / (1 + n_permutations)
    intervals = []
    for _ in range(n_bootstraps):
        draw = rng.integers(0, n, size=(n_bootstrap, n))
        Ab, Bb = _comparisons_twice_ranks(cx[draw], mx), _comparisons_twice_ranks(cy[draw], my)
        Tb, SAb, SBb = (Ab * Bb).sum(1) - c, (Ab * Ab).sum(1) - c, (Bb * Bb).sum(1) - c
        ok = (SAb > 0) & (SBb > 0)
        intervals.append(np.percentile(Tb[ok] / np.sqrt(SAb[ok].astype(float) * SBb[ok].astype(float)), [2.5, 97.5]))
    return rho, p, np.array(intervals)


def _comparisons_seeded(xs, ys, seed_permutation, seed_bootstrap, n_permutations, n_bootstrap):
    """The permutation p and the bootstrap interval drawn with the seeds the definition gives, under one plain reading of it.

    The definition names the generator (`numpy.random.default_rng(seed)`), the two seeds and the two counts; it does not
    give the calls. The reading here was fixed before any table was held against it, and no other was tried:
      permutation  one generator from seed_permutation; y is shuffled n_permutations times, each shuffle the next of the
                   generator (`permuted` over the rows of a table of copies: in the numpy the stage pins, the same stream as
                   one `permutation` per shuffle); a shuffle counts when its |rho| is at least the observed |rho|, decided
                   in whole numbers
      bootstrap    one generator from seed_bootstrap; each draw is n whole numbers from 0 to n - 1, the next of the
                   generator (`integers`: one call for all draws is the same stream as one call per draw); ranks made
                   afresh in every draw; the ends are `numpy.percentile` (its default, linear between the ordered values)
                   at 2.5 and 97.5 over the draws in which rho is defined
    Returns p, the lower end, the upper end, and the number of draws in which rho is not defined."""
    cx, mx = _comparisons_codes(xs)
    cy, my = _comparisons_codes(ys)
    n = len(xs)
    c = n * (n + 1) ** 2
    A, B = _comparisons_twice_ranks(cx, mx), _comparisons_twice_ranks(cy, my)
    T = int((A * B).sum()) - c
    rng = np.random.default_rng(seed_permutation)
    shuffled = rng.permuted(np.tile(B, (n_permutations, 1)), axis=1)
    p = (1 + int((np.abs(shuffled @ A - c) >= abs(T)).sum())) / (1 + n_permutations)
    rng = np.random.default_rng(seed_bootstrap)
    draw = rng.integers(0, n, size=(n_bootstrap, n))
    Ab, Bb = _comparisons_twice_ranks(cx[draw], mx), _comparisons_twice_ranks(cy[draw], my)
    Tb, SAb, SBb = (Ab * Bb).sum(1) - c, (Ab * Ab).sum(1) - c, (Bb * Bb).sum(1) - c
    ok = (SAb > 0) & (SBb > 0)
    lo, hi = np.percentile(Tb[ok] / np.sqrt(SAb[ok].astype(float) * SBb[ok].astype(float)), [2.5, 97.5])
    return p, float(lo), float(hi), int((~ok).sum())


def _comparisons_chance_constant(values):
    """The exact chance that a sample of len(values) of the values, drawn with replacement, is constant: rho is then not defined."""
    from collections import Counter
    from fractions import Fraction
    n = len(values)
    return sum(Fraction(k, n) ** n for k in Counter(values).values())


def _comparisons_words(text):
    """A label in lower case with every kind of dash and the underscore as '-', for a search of key words."""
    dashes = "_" + "".join(chr(code) for code in range(0x2010, 0x2016))          # the underscore, and U+2010 to U+2015: hyphens and dashes
    return "".join("-" if ch in dashes else ch for ch in str(text).lower())


def part_comparisons():
    import html
    import re
    from fractions import Fraction

    LIST, fr = _comparisons_LIST, _comparisons_fr
    number, printed, show = _comparisons_number, _comparisons_printed, _comparisons_show
    half = Fraction(1, 2)

    def held(what, ok, detail):
        """A check whose account of what was found is printed only when it fails."""
        check(what, ok, "" if ok else detail)

    # ------------------------------------------------------------------ the two tables taken as given
    need_rows, alloc_rows = table("district_need.csv"), table("district_allocation.csv")
    need = {r["pc11_district_code"]: r for r in need_rows}
    alloc = {r["pc11_district_code"]: r for r in alloc_rows}
    held("comparisons, what is taken as given: district_need.csv and district_allocation.csv each hold the same 30 census district codes, once each (another part checks their figures against the inputs)",
          len(need_rows) == len(need) == 30 and len(alloc_rows) == len(alloc) == 30 and set(need) == set(alloc),
          f"district_need.csv {len(need_rows)} rows and {len(need)} codes; district_allocation.csv {len(alloc_rows)} rows and {len(alloc)} codes; codes in one and not the other: {sorted(set(need) ^ set(alloc))}")
    codes = sorted(need, key=int)
    name = {k: need[k]["district_name"] for k in codes}

    # ------------------------------------------------------------------ every comparison, from its definition
    N1, POST, PRE = "n1_ha_2018_2025", "r620_plantation_post_lakh", "r620_plantation_pre_lakh"
    spec = {   # comparison: need (column of district_need.csv), allocation (column of district_allocation.csv), its unit, the column that leaves a district out
        "C1": (N1, POST, "lakh", None),
        "C2": (N1 + "_lgd", POST, "lakh", None),
        "C3": ("n2_ha", POST, "lakh", None),
        "C4": ("loss_2001_2013_ha", PRE, "lakh", None),
        "C5": (N1, PRE, "lakh", None),
        "C6": (N1, "dump_forest_named_started_by_fy2017_18_inr", "rupees", None),
        "C7": (N1, POST, "lakh", "left_out_of_c7"),
        "C7b": (N1, POST, "lakh", "left_out_under_the_other_rule"),
        "C8": ("n1_ha_2001_2025", POST, "lakh", None),
        "C9": ("n1_ha_2017_2023", POST, "lakh", None),
        "C10": ("n1_ha_2021_2025", POST, "lakh", None),
        "C11": (N1, "r620_plantation_post_without_fy2018_19_lakh", "lakh", None),
        "C12": (None, None, None, None),      # two intensities, formed below
        "B1": (N1, "r620_all_post_lakh", "lakh", None)}
    E, S = {}, {}                                                  # expected: by (comparison, district), and by comparison
    for c in LIST:
        ncol, acol, aunit, out = spec[c]
        if c == "C12":
            nv = {k: 100 * fr(need[k][N1]) / fr(need[k]["forest_at_window_start_ha_2018_2025"]) for k in codes}
            av = {k: 100 * fr(alloc[k][POST]) / fr(alloc[k]["r620_all_post_lakh"]) for k in codes}
        else:
            nv = {k: fr(need[k][ncol]) for k in codes}
            av = {k: fr(alloc[k][acol]) for k in codes}
        kept = [k for k in codes if not (out and need[k][out] == "yes")]
        tn, ta = sum(nv[k] for k in kept), sum(av[k] for k in kept)
        plain = c not in ("C12", "B1")                              # shares, r and gaps apply
        in_lakh = 100000 if aunit == "rupees" else 1                # one lakh is 100,000 rupees
        s = dict(kept=kept, out=[k for k in codes if k not in kept], tn=tn, ta=ta, plain=plain, aunit=aunit, below=Fraction(0), above=Fraction(0),
                 n_below=0, n_above=0, n_zero=0, positive=Fraction(0), xs=[nv[k] for k in kept], ys=[av[k] for k in kept])
        for k in codes:
            e = dict(inc="yes" if k in kept else "no", need=nv[k], alloc=av[k], ns=None, as_=None, r=None, gap=None)
            if not plain:
                e["why"] = "intensity" if c == "C12" else "benchmark"
            elif k not in kept:
                e["why"] = "out"
            else:
                e["ns"], e["as_"] = 100 * nv[k] / tn, 100 * av[k] / ta
                e["gap"] = (nv[k] / tn * ta - av[k]) / in_lakh
                if e["gap"] > 0:
                    s["positive"] += e["gap"]
                if nv[k] == 0:
                    e["why"] = "zero"
                    s["n_zero"] += 1
                else:
                    e["why"], e["r"] = "", e["as_"] / e["ns"]
                    if e["r"] < half:
                        s["below"] += e["ns"]
                        s["n_below"] += 1
                    if e["r"] > 2:
                        s["above"] += e["ns"]
                        s["n_above"] += 1
            E[(c, k)] = e
        S[c] = s

    # ================================================================== need_vs_allocation.csv
    nva_raw = table("need_vs_allocation.csv")
    nva = _comparisons_whole(nva_raw)
    cols = ["comparison", "pc11_district_code", "district_name", "in_comparison", "need", "need_unit", "allocation", "allocation_unit",
            "need_share_pct", "allocation_share_pct", "r", "r_blank_because", "gap_lakh"]
    keys = [(r.get("comparison"), r.get("pc11_district_code")) for r in nva]
    want = [(c, k) for c in LIST for k in codes]
    head = _comparisons_header("need_vs_allocation.csv")
    held("need_vs_allocation.csv: the 13 columns this part checks, each once, and no other; 420 rows, one for each of the 14 comparisons (C1 to C12, C7b, B1) and each of the 30 districts, none twice and none ragged, in the order of the list of comparisons and, within a comparison, of the census codes",
          sorted(head) == sorted(cols) and keys == want and not _comparisons_ragged(nva_raw),
          f"{len(nva)} rows, {len(set(keys))} distinct keys, {len(set(want) - set(keys))} missing, {len(set(keys) - set(want))} not expected, {_comparisons_ragged(nva_raw)} ragged; "
          f"same keys in another order: {sorted(map(str, keys)) == sorted(map(str, want)) and keys != want}; columns {head}")
    tab = {}
    for r in nva:
        tab.setdefault((r.get("comparison"), r.get("pc11_district_code")), r)
    blank = {c: "" for c in cols}
    absent = set(want) - set(tab)

    def cell(key, col):
        return "(no row)" if key in absent else tab[key][col]

    pairs = [(f"{c} {k}", (cell((c, k), "district_name"), cell((c, k), "in_comparison")), (name[k], E[(c, k)]["inc"]),
              (cell((c, k), "district_name"), cell((c, k), "in_comparison")) == (name[k], E[(c, k)]["inc"])) for c, k in want]
    check("need_vs_allocation.csv: district_name is the district's name in district_need.csv; in_comparison is 'no' for the districts C7 and C7b leave out (left_out_of_c7, left_out_under_the_other_rule = yes in district_need.csv) and 'yes' on every other row",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for c, k in want:
        e, t = E[(c, k)], tab.get((c, k), blank)
        if c == "C12":
            ok = (printed(t["need"], e["need"], 6) and printed(t["allocation"], e["alloc"], 6) and all(w in t["need_unit"] for w in ("per 100 ha", "forest", "window start"))
                  and all(w in t["allocation_unit"] for w in ("per cent", "own expenditure")))
            exp = (show(e["need"], 6), "(names 'per 100 ha', 'forest', 'window start')", show(e["alloc"], 6), "(names 'per cent', 'own expenditure')")
        else:
            ok = number(t["need"], e["need"]) and number(t["allocation"], e["alloc"]) and t["need_unit"] == "ha" and t["allocation_unit"] == S[c]["aunit"]
            exp = (show(e["need"]), "ha", show(e["alloc"]), S[c]["aunit"])
        pairs.append((f"{c} {k}", tuple(cell((c, k), x) for x in ("need", "need_unit", "allocation", "allocation_unit")), exp, ok))
    check("need_vs_allocation.csv: need and allocation equal, as numbers, the columns of district_need.csv and district_allocation.csv that the specification gives each comparison (the left-out districts of C7 and C7b keep theirs), with need_unit 'ha' and allocation_unit 'lakh' ('rupees' for C6); "
          "for C12 they are 100 x n1_ha_2018_2025 / forest_at_window_start_ha_2018_2025 and 100 x r620_plantation_post_lakh / r620_all_post_lakh, exact, rounded half up to the 6 decimals printed, and the units name 'per 100 ha', 'forest' and 'window start', and 'per cent' and 'own expenditure' (key words)",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for c, k in want:
        e, t = E[(c, k)], tab.get((c, k), blank)
        pairs.append((f"{c} {k}", (cell((c, k), "need_share_pct"), cell((c, k), "allocation_share_pct")), (show(e["ns"], 6), show(e["as_"], 6)),
                      printed(t["need_share_pct"], e["ns"], 6) and printed(t["allocation_share_pct"], e["as_"], 6)))
    check("need_vs_allocation.csv: need_share_pct and allocation_share_pct are 100 x the district's need (allocation) / the sum over the districts in the comparison, exact, rounded half up to the 6 decimals printed; blank for a district left out and on every row of C12 and B1",
          all(p[3] for p in pairs), mismatches(pairs))

    says = {"zero": "need is zero", "out": "left out", "intensity": "intensit", "benchmark": "benchmark"}
    pairs, wording = [], {}
    for c, k in want:
        e, t = E[(c, k)], tab.get((c, k), blank)
        why = t["r_blank_because"]
        ok = printed(t["r"], e["r"], 6) and (why == "" if e["why"] == "" else says[e["why"]] in why.lower())
        pairs.append((f"{c} {k}", (cell((c, k), "r"), cell((c, k), "r_blank_because")), (show(e["r"], 6), "" if e["why"] == "" else f"(says '{says[e['why']]}')"), ok))
        if e["why"]:
            wording.setdefault(e["why"], set()).add(why)
    several = {kind: sorted(w) for kind, w in wording.items() if len(w) != 1}
    check("need_vs_allocation.csv: r is the exact allocation share / need share (unrounded shares), rounded half up to the 6 decimals printed, and blank where the need is zero, for a district left out and on every row of C12 and B1; "
          "r_blank_because is blank exactly where r is given and otherwise says which of the four it is ('need is zero', 'left out', 'intensit[ies]', 'benchmark'), in one wording for each of the four",
          all(p[3] for p in pairs) and not several, mismatches(pairs) + (f" more than one wording for a kind of blank: {several}" if several else ""))

    pairs = [(f"{c} {k}", cell((c, k), "gap_lakh"), show(E[(c, k)]["gap"], 2), printed(tab.get((c, k), blank)["gap_lakh"], E[(c, k)]["gap"], 2)) for c, k in want]
    check("need_vs_allocation.csv: gap_lakh is the district's need share x the comparison's total allocation - the district's allocation, exact, in lakh rupees (C6's rupees divided by 100,000), rounded half up to the 2 decimals printed; blank for a district left out and on every row of C12 and B1",
          all(p[3] for p in pairs), mismatches(pairs))

    # ================================================================== need_vs_allocation_summary.csv
    summ_raw = table("need_vs_allocation_summary.csv")
    summ = _comparisons_whole(summ_raw)
    scols = ["comparison", "kind", "need_is", "allocation_is", "what_it_asks", "n_districts", "districts_left_out", "need_total", "need_unit", "allocation_total",
             "allocation_unit", "rho", "p_permutation", "ci95_lo", "ci95_hi", "n_permutations", "n_bootstrap", "n_bootstrap_undefined", "seed_permutation",
             "seed_bootstrap", "need_share_pct_where_r_below_0_5", "need_share_pct_where_r_above_2", "n_districts_r_below_0_5", "n_districts_r_above_2",
             "n_districts_need_zero", "sum_positive_gaps_lakh", "gap_is"]
    kind = {c: "intensity" if c == "C12" else "benchmark" if c == "B1" else "comparison" for c in LIST}
    head = _comparisons_header("need_vs_allocation_summary.csv")
    held("need_vs_allocation_summary.csv: the 27 columns this part checks, each once, and no other; 14 rows, one per comparison, none ragged, in the order of the list C1, C2, C3, C4, C5, C6, C7, C7b, C8, C9, C10, C11, C12, B1",
          sorted(head) == sorted(scols) and [r.get("comparison") for r in summ] == LIST and not _comparisons_ragged(summ_raw),
          f"{len(summ)} rows, {_comparisons_ragged(summ_raw)} ragged: {[r.get('comparison') for r in summ]}; columns {head}")
    sblank = {c: "" for c in scols}
    st = {}
    for r in summ:
        st.setdefault(r.get("comparison"), r)
    sabsent = [c for c in LIST if c not in st]

    def scell(c, col):
        return "(no row)" if c in sabsent else st[c][col]

    def not_fixed(text):
        """True where a comparison's what_it_asks says that it is not one of those fixed beforehand."""
        return re.search(r"\bnot one of\b.*\bfixed\b", " ".join(text.lower().split())) is not None

    pairs = [(c, (scell(c, "kind"), scell(c, "what_it_asks")[:80]), (kind[c], "says 'not one of' ... 'fixed'" if c == "C7b" else "not blank; does not say 'not one of' ... 'fixed'"),
              st.get(c, sblank)["kind"] == kind[c] and st.get(c, sblank)["what_it_asks"].strip() != "" and not_fixed(st.get(c, sblank)["what_it_asks"]) == (c == "C7b")) for c in LIST]
    check("need_vs_allocation_summary.csv: kind is 'comparison' for C1 to C11 and for C7b (a comparison in kind), 'intensity' for C12 and 'benchmark' for B1; what_it_asks is not blank, and says of C7b, and of no other comparison, that it is 'not one of' those 'fixed' (key words: the rest of its wording is not in the specification and is not tested)",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for c in LIST:
        t, exp = st.get(c, sblank), (str(len(S[c]["kept"])), [name[k] for k in S[c]["out"]])
        got = (scell(c, "n_districts"), [x.strip() for x in t["districts_left_out"].split(";") if x.strip()])
        pairs.append((c, got, exp, got == exp and (t["districts_left_out"] == "; ".join(exp[1]))))
    check("need_vs_allocation_summary.csv: n_districts is the number of districts in the comparison, and districts_left_out names those C7 and C7b leave out, in census-code order, joined by '; ' (blank for every other comparison)",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for c in LIST:
        t, s = st.get(c, sblank), S[c]
        units = (sorted({r.get("need_unit", "") for r in nva if r.get("comparison") == c}), sorted({r.get("allocation_unit", "") for r in nva if r.get("comparison") == c}))
        if c == "C12":                                              # two ratios: thirty ratios added are a total of nothing
            ok, exp = c not in sabsent and (t["need_total"], t["allocation_total"]) == ("", ""), ("", "")
        else:
            ok, exp = number(t["need_total"], s["tn"]) and number(t["allocation_total"], s["ta"]), (show(s["tn"]), show(s["ta"]))
        pairs.append((c, (scell(c, "need_total"), scell(c, "need_unit"), scell(c, "allocation_total"), scell(c, "allocation_unit")), (exp[0], units[0], exp[1], units[1]),
                      ok and units == ([t["need_unit"]], [t["allocation_unit"]])))
    check("need_vs_allocation_summary.csv: need_total and allocation_total are the exact sums of need and allocation over the districts in the comparison, as numbers, and both are blank for C12, whose need and allocation are ratios; need_unit and allocation_unit are the one unit that the comparison's rows of need_vs_allocation.csv carry",
          all(p[3] for p in pairs), mismatches(pairs))

    own = {c: _comparisons_spearman(S[c]["xs"], S[c]["ys"], _comparisons_OWN_SEED + i, _comparisons_N_PERMUTATIONS, _comparisons_N_BOOTSTRAP, _comparisons_OWN_BOOTSTRAPS)
           for i, c in enumerate(LIST)}

    def number_or_none(text):
        try:
            return float(text) if math.isfinite(float(text)) else None
        except Exception:
            return None

    pairs = [(c, scell(c, "rho"), f"{own[c][0]:.9f}", number_or_none(st.get(c, sblank)["rho"]) is not None and abs(number_or_none(st.get(c, sblank)["rho"]) - own[c][0]) <= 5.0e-7 + 1e-12) for c in LIST]
    check("need_vs_allocation_summary.csv: rho is Spearman's rho of need against allocation over the districts in the comparison (the Pearson correlation of average ranks; ranks made from the exact values, ties sharing the average rank), to the 6 decimals printed: |table - recomputed| <= 0.0000005",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs, sharp, whole, far = [], [], [], 0.0
    for c in LIST:
        pt, po = number_or_none(st.get(c, sblank)["p_permutation"]), own[c][1]
        pairs.append((c, scell(c, "p_permutation"), f"{po:.5f}", pt is not None and abs(pt - po) <= 0.01))
        se = 0.0 if pt is None or not 0 <= pt <= 1 else math.sqrt((pt * (1 - pt) + po * (1 - po)) / (1 + _comparisons_N_PERMUTATIONS))
        sharp.append((c, scell(c, "p_permutation"), f"{po:.5f} (allowed difference {6 * se + 0.00002:.5f})", pt is not None and abs(pt - po) <= 6 * se + 0.00002))
        count = None if pt is None else pt * (1 + _comparisons_N_PERMUTATIONS)
        whole.append((c, scell(c, "p_permutation"), "(1 + a count) / 100000", count is not None and abs(count - round(count)) < 1e-6 and 1 <= round(count) <= 1 + _comparisons_N_PERMUTATIONS))
        far = max(far, abs(pt - po)) if pt is not None else far
    check("need_vs_allocation_summary.csv: p_permutation is within 0.01 of this script's own two-sided permutation p (99,999 shuffles of allocation against need with this script's own seeds; p = (1 + shuffles whose |rho| is at least the observed |rho|) / (1 + shuffles))",
          all(p[3] for p in pairs), mismatches(pairs) or f"largest |difference| {far:.5f}")
    check("need_vs_allocation_summary.csv: p_permutation is also within six Monte Carlo standard errors of that own p: |difference| <= 6 x sqrt((p(1 - p) + p'(1 - p')) / 100000) + 0.00002, p and p' the table's value and this script's",
          all(p[3] for p in sharp), mismatches(sharp))
    check("need_vs_allocation_summary.csv: p_permutation x 100,000 is a whole number from 1 to 100,000, as (1 + a count of shuffles) / (1 + 99,999) must be",
          all(p[3] for p in whole), mismatches(whole))

    pairs, sharp, far, z = [], [], 0.0, 0.0
    for c in LIST:
        t, ivs = st.get(c, sblank), own[c][2]
        lo, hi = number_or_none(t["ci95_lo"]), number_or_none(t["ci95_hi"])
        ok = lo is not None and hi is not None and abs(lo - ivs[0, 0]) <= 0.04 and abs(hi - ivs[0, 1]) <= 0.04 and lo <= hi
        pairs.append((c, (scell(c, "ci95_lo"), scell(c, "ci95_hi")), (f"{ivs[0, 0]:.6f}", f"{ivs[0, 1]:.6f}"), ok))
        mean, sd = ivs.mean(0), ivs.std(0, ddof=1)
        sharp.append((c, (scell(c, "ci95_lo"), scell(c, "ci95_hi")), (f"{mean[0]:.6f} +/- {6 * sd[0] + 0.000001:.6f}", f"{mean[1]:.6f} +/- {6 * sd[1] + 0.000001:.6f}"),
                      lo is not None and hi is not None and abs(lo - mean[0]) <= 6 * sd[0] + 0.000001 and abs(hi - mean[1]) <= 6 * sd[1] + 0.000001))
        z = max(z, abs(lo - mean[0]) / sd[0] if lo is not None and sd[0] > 0 else 0.0, abs(hi - mean[1]) / sd[1] if hi is not None and sd[1] > 0 else 0.0)
        if lo is not None and hi is not None:
            far = max(far, abs(lo - ivs[0, 0]), abs(hi - ivs[0, 1]))
    check("need_vs_allocation_summary.csv: ci95_lo and ci95_hi are each within 0.04 of this script's own percentile bootstrap interval (9,999 draws of the districts with replacement, as pairs, with this script's own seed; ranks made afresh in every draw; the 2.5th and 97.5th percentiles of the rho of the draws), and ci95_lo <= ci95_hi",
          all(p[3] for p in pairs), mismatches(pairs) or f"largest |difference| {far:.4f}")
    check(f"need_vs_allocation_summary.csv: ci95_lo and ci95_hi are also each within six standard deviations of the mean of that end over {_comparisons_OWN_BOOTSTRAPS} own bootstraps of 9,999 draws, the standard deviation being that of the end across those {_comparisons_OWN_BOOTSTRAPS} (how far an honest interval's end moves from one bootstrap to the next), plus 0.000001 for the decimals printed",
          all(p[3] for p in sharp), mismatches(sharp) or f"the end furthest from its mean is {z:.2f} standard deviations away")

    pairs = []
    for i, c in enumerate(LIST):
        t, s = st.get(c, sblank), S[c]
        expected_undefined = _comparisons_N_BOOTSTRAP * (_comparisons_chance_constant(s["xs"]) + _comparisons_chance_constant(s["ys"]))
        und = t["n_bootstrap_undefined"]
        ok_und = und.isascii() and und.isdigit() and int(und) <= _comparisons_N_BOOTSTRAP and (int(und) == 0 or expected_undefined >= Fraction(1, 10 ** 6))
        exp = (str(_comparisons_N_PERMUTATIONS), str(_comparisons_N_BOOTSTRAP), str(_comparisons_SEED_BASE + 100 + i), str(_comparisons_SEED_BASE + 200 + i),
               "0" if expected_undefined < Fraction(1, 10 ** 6) else f"a whole number from 0 to {_comparisons_N_BOOTSTRAP}")
        got = tuple(scell(c, x) for x in ("n_permutations", "n_bootstrap", "seed_permutation", "seed_bootstrap", "n_bootstrap_undefined"))
        pairs.append((c, got, exp, got[:4] == exp[:4] and ok_und))
    check("need_vs_allocation_summary.csv: n_permutations is 99999 and n_bootstrap 9999; seed_permutation and seed_bootstrap are 20261010 + 100 + k and 20261010 + 200 + k, k the comparison's place (from 0) in the list; "
          "n_bootstrap_undefined is a whole number from 0 to n_bootstrap, and 0 wherever the exact chance of a constant resample of either side puts the expected number of undefined draws below one in a million",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for i, c in enumerate(LIST):
        t, s = st.get(c, sblank), S[c]
        p, lo, hi, und = _comparisons_seeded(s["xs"], s["ys"], _comparisons_SEED_BASE + 100 + i, _comparisons_SEED_BASE + 200 + i, _comparisons_N_PERMUTATIONS, _comparisons_N_BOOTSTRAP)
        pt, lt, ht = number_or_none(t["p_permutation"]), number_or_none(t["ci95_lo"]), number_or_none(t["ci95_hi"])
        ok = (pt is not None and abs(pt - p) <= 1e-9 and lt is not None and abs(lt - lo) <= 5.0e-7 + 1e-12 and ht is not None and abs(ht - hi) <= 5.0e-7 + 1e-12
              and t["n_bootstrap_undefined"] == str(und))
        pairs.append((c, tuple(scell(c, x) for x in ("p_permutation", "ci95_lo", "ci95_hi", "n_bootstrap_undefined")), (f"{p:.5f}", f"{lo:.9f}", f"{hi:.9f}", str(und)), ok))
    check("need_vs_allocation_summary.csv: drawn again with the seeds the definition gives (20261010 + 100 + k for the permutation, 20261010 + 200 + k for the bootstrap), p_permutation, ci95_lo, ci95_hi and n_bootstrap_undefined are the table's to the digit - "
          "p as (1 + a count) / 100,000 (|difference| <= 0.000000001), each end to the 6 decimals printed (|table - recomputed| <= 0.0000005), the number of undefined draws the same - "
          "under this script's one reading of how the generator is called, which the definition does not give: numpy.random.default_rng(seed) once for each of the two; allocation shuffled 99,999 times in turn, a shuffle counted when its |rho| is at least the observed |rho| (decided in whole numbers); "
          "9,999 draws in turn of n whole numbers from 0 to n - 1, ranks made afresh, numpy's default percentiles at 2.5 and 97.5 of the rho of the draws in which it is defined",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for c in LIST:
        t, s = st.get(c, sblank), S[c]
        got = tuple(scell(c, x) for x in ("need_share_pct_where_r_below_0_5", "need_share_pct_where_r_above_2", "n_districts_r_below_0_5", "n_districts_r_above_2", "n_districts_need_zero"))
        if s["plain"]:
            exp = (show(s["below"], 6), show(s["above"], 6), str(s["n_below"]), str(s["n_above"]), str(s["n_zero"]))
            ok = printed(t["need_share_pct_where_r_below_0_5"], s["below"], 6) and printed(t["need_share_pct_where_r_above_2"], s["above"], 6) and got[2:] == exp[2:]
        else:
            exp, ok = ("", "", "", "", ""), got == ("", "", "", "", "")
        pairs.append((c, got, exp, ok))
    check("need_vs_allocation_summary.csv: need_share_pct_where_r_below_0_5 and need_share_pct_where_r_above_2 are the exact sums of the need shares of the districts whose exact r is below 0.5, and above 2, rounded half up to the 6 decimals printed; "
          "n_districts_r_below_0_5 and n_districts_r_above_2 count those districts, and n_districts_need_zero the districts in the comparison whose need is zero (they have no r and are in neither count); all five blank for C12 and B1",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for c in LIST:
        t, s = st.get(c, sblank), S[c]
        exp = (show(s["positive"], 2), _comparisons_GAP_IS) if s["plain"] else ("", "")
        pairs.append((c, (scell(c, "sum_positive_gaps_lakh"), scell(c, "gap_is")), exp, printed(t["sum_positive_gaps_lakh"], s["positive"] if s["plain"] else None, 2) and t["gap_is"] == exp[1]))
    check("need_vs_allocation_summary.csv: sum_positive_gaps_lakh is the exact sum of the districts' unrounded gaps that are above zero, in lakh rupees, rounded half up to the 2 decimals printed, and gap_is is the specification's sentence 'the same money distributed by need; not a requirement'; both blank for C12 and B1",
          all(p[3] for p in pairs), mismatches(pairs))

    post, pre = r"\bpost\b", r"\bpre\b"
    words = {   # comparison: what need_is must name, what allocation_is must name (patterns, searched in lower case with every dash as '-')
        "C1": (["n1", "2018", "2025", "all land"], ["r6.20", "plantation", post]),
        "C2": (["n1", "2018", "2025", "lgd"], ["r6.20", "plantation", post]),
        "C3": (["n2"], ["r6.20", "plantation", post]),
        "C4": (["loss", "2001", "2013"], ["r6.20", "plantation", pre]),
        "C5": (["n1", "2018", "2025"], ["r6.20", "plantation", pre]),
        "C6": (["n1", "2018", "2025"], ["dump", "forest-named", "2017-18"]),
        "C7": (["n1", "2018", "2025", "left out"], ["r6.20", "plantation", post, "left out"]),
        "C7b": (["n1", "2018", "2025", "left out", "other"], ["r6.20", "plantation", post, "left out"]),
        "C8": (["n1", "2001", "2025"], ["r6.20", "plantation", post]),
        "C9": (["n1", "2017", "2023"], ["r6.20", "plantation", post]),
        "C10": (["n1", "2021", "2025"], ["r6.20", "plantation", post]),
        "C11": (["n1", "2018", "2025"], ["r6.20", "plantation", "2019-20", "2025-26"]),
        "C12": (["n1", "per 100 ha", "window start"], ["plantation", "own expenditure", post]),
        "B1": (["n1", "2018", "2025"], ["r6.20", "all expenditure", post])}
    but = lambda *those: [c for c in LIST if c not in those]
    never = {   # what belongs to one comparison, or to a few, and must not stand in another's label: (pattern, the comparisons whose label must not have it)
        "need_is": [(r"\blgd\b", but("C2")), (r"\bn2\b", but("C3")), ("left out", but("C7", "C7b")), ("per 100 ha", but("C12"))],
        "allocation_is": [("dump", but("C6")), ("all expenditure", but("B1")), ("own expenditure", but("C12")), ("left out", but("C7", "C7b")), (pre, but("C4", "C5")), (post, ["C4", "C5"])]}
    found_in = lambda w, text: re.search(w if w.startswith("\\") else re.escape(w), _comparisons_words(text)) is not None
    pairs = []
    for c in LIST:
        t = st.get(c, sblank)
        lacking = [w for w in words[c][0] if not found_in(w, t["need_is"])] + [w for w in words[c][1] if not found_in(w, t["allocation_is"])]
        wrongly = [f"{col}: {w}" for col in ("need_is", "allocation_is") for w, those in never[col] if c in those and found_in(w, t[col])]
        pairs.append((c, (scell(c, "need_is"), scell(c, "allocation_is")), f"lacks {lacking}; names what belongs to another comparison {wrongly}", not lacking and not wrongly))
    check("need_vs_allocation_summary.csv: need_is and allocation_is name what the specification gives the comparison - key words only (N1, N2 or loss; the window's two years; 'all land', 'LGD', 'left out'; R6.20 plantation with 'pre' or 'post' or the years of C11; the dump's forest-named works by 2017-18; 'all expenditure'; C12's 'per 100 ha' and 'own expenditure') - "
          "and name none of these that belongs to another comparison and not to this one ('LGD', 'N2', 'left out', 'per 100 ha'; 'dump', 'all expenditure', 'own expenditure', 'pre' for an allocation of the post period, 'post' for one of the pre period); their full wording is not in the specification and is not tested",
          all(p[3] for p in pairs), mismatches(pairs))

    # ================================================================== marginalisation_split.csv
    ms_raw = table("marginalisation_split.csv")
    ms = _comparisons_whole(ms_raw)
    mcols = ["comparison", "grouping", "class", "n_districts", "districts", "need", "need_unit", "allocation_lakh", "need_share_pct", "allocation_share_pct", "population_lgd", "note"]
    groupings = ["st_class", "adi_tercile", "sc_tercile"]
    msplit = {"C1": (N1, POST), "C4": ("loss_2001_2013_ha", PRE)}
    M = {}
    for c, (ncol, acol) in msplit.items():
        tn, ta = sum(fr(need[k][ncol]) for k in codes), sum(fr(alloc[k][acol]) for k in codes)
        for g in groupings:
            for cl in sorted({need[k][g] for k in codes}):
                members = [k for k in codes if need[k][g] == cl]
                n, a = sum(fr(need[k][ncol]) for k in members), sum(fr(alloc[k][acol]) for k in members)
                M[(c, g, cl)] = dict(members=members, need=n, alloc=a, ns=100 * n / tn, as_=100 * a / ta, pop=sum(fr(need[k]["population_lgd"]) for k in members))
    mkeys = [(r.get("comparison"), r.get("grouping"), r.get("class")) for r in ms]
    head = _comparisons_header("marginalisation_split.csv")
    held("marginalisation_split.csv: the 12 columns this part checks, each once, and no other; one row for each of C1 and C4, each grouping (st_class, adi_tercile, sc_tercile) and each class that district_need.csv has in that grouping; none twice, none ragged and no other row",
          sorted(head) == sorted(mcols) and sorted(map(str, mkeys)) == sorted(map(str, M)) and len(set(mkeys)) == len(mkeys) and not _comparisons_ragged(ms_raw),
          f"{len(ms)} rows, {_comparisons_ragged(ms_raw)} ragged, {len(set(mkeys))} distinct keys, expected {len(M)}; missing {sorted(map(str, set(M) - set(mkeys)))}; not expected {sorted(map(str, set(mkeys) - set(M)))}; columns {head}")
    mt = {}
    for r in ms:
        mt.setdefault((r.get("comparison"), r.get("grouping"), r.get("class")), r)
    mblank = {c: "" for c in mcols}

    def mcell(key, col):
        return mt[key][col] if key in mt else "(no row)"

    def listed(text):
        return [x.strip() for x in text.split(";") if x.strip()]

    pairs = []
    for c in msplit:
        for g in groupings:
            named = [d for key, r in mt.items() if key[:2] == (c, g) for d in listed(r["districts"])]
            counts = [r["n_districts"] for key, r in mt.items() if key[:2] == (c, g)]
            total = sum(int(x) for x in counts if x.isascii() and x.isdigit())
            pairs.append((f"{c} {g}", (f"{len(named)} names, {len(set(named))} distinct", f"n_districts add to {total}"), ("30 names, 30 distinct: the 30 districts", "n_districts add to 30"),
                          sorted(named) == sorted(name.values()) and total == 30))
    check("marginalisation_split.csv: within each comparison and grouping the rows' lists of districts hold the 30 districts of district_need.csv once each, and their n_districts add to 30",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for key, m in M.items():
        t, exp = mt.get(key, mblank), (str(len(m["members"])), "; ".join(name[k] for k in m["members"]))
        pairs.append((" / ".join(key), (mcell(key, "n_districts"), mcell(key, "districts")), exp, (t["n_districts"], t["districts"]) == exp))
    check("marginalisation_split.csv: n_districts and districts are the number and the names, in census-code order and joined by '; ', of the districts whose st_class, adi_tercile or sc_tercile in district_need.csv is the row's class",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for key, m in M.items():
        t = mt.get(key, mblank)
        pairs.append((" / ".join(key), tuple(mcell(key, x) for x in ("need", "need_unit", "allocation_lakh", "population_lgd")), (show(m["need"]), "ha", show(m["alloc"]), show(m["pop"])),
                      number(t["need"], m["need"]) and t["need_unit"] == "ha" and number(t["allocation_lakh"], m["alloc"]) and t["population_lgd"] == show(m["pop"])))
    check("marginalisation_split.csv: need, allocation_lakh and population_lgd are the exact sums over the class's districts of the comparison's need (C1: n1_ha_2018_2025; C4: loss_2001_2013_ha), of its allocation (C1: r620_plantation_post_lakh; C4: r620_plantation_pre_lakh) and of population_lgd - hectares and money as numbers, the population as the whole number it is; need_unit is 'ha'",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = [(" / ".join(key), (mcell(key, "need_share_pct"), mcell(key, "allocation_share_pct")), (show(m["ns"], 6), show(m["as_"], 6)),
              printed(mt.get(key, mblank)["need_share_pct"], m["ns"], 6) and printed(mt.get(key, mblank)["allocation_share_pct"], m["as_"], 6)) for key, m in M.items()]
    check("marginalisation_split.csv: need_share_pct and allocation_share_pct are the sums of the class's districts' need shares and allocation shares in the comparison, unrounded - that is, 100 x the class's sum / the sum over the 30 districts - rounded half up to the 6 decimals printed (not a sum of the rounded shares that need_vs_allocation.csv prints)",
          all(p[3] for p in pairs), mismatches(pairs))

    source = ROOT / "60_layer" / "data.js"
    found = re.search(r"<tr><td>" + re.escape(_comparisons_ADI_TITLE) + r"</td><td>(.*?)</td><td>(.*?)</td></tr>", source.read_text(encoding="utf-8")) if source.exists() else None
    line = [] if not found else [_comparisons_ADI_TITLE] + [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in found.groups()]
    pairs = []
    for key in M:
        note = mt.get(key, mblank)["note"]
        carries = bool(line) and all(x in note for x in line)
        if key[1] == "adi_tercile":
            ok, exp = "LGD" in note and carries, "names LGD population and carries the index's name, source and licence"
        else:
            ok, exp = "LGD" in note and not carries and _comparisons_ADI_TITLE not in note, "names LGD population and does not carry the index's line"
        pairs.append((" / ".join(key), note[:60] + (" ..." if len(note) > 60 else "") + note[-50:] * (len(note) > 110), exp, ok))
    one = {g: sorted({r["note"] for key, r in mt.items() if key[1] == g}) for g in groupings}
    check("marginalisation_split.csv: note says on every row that the classes rest on LGD population (it names 'LGD') and is one text within a grouping; on the adi_tercile rows, and only there, it carries the three cells (name, source, licence or terms) of the row 'Aggregate Development Index 2011' in the layer's list of sources (60_layer/data.js)",
          bool(line) and all(p[3] for p in pairs) and all(len(v) == 1 for v in one.values()),
          ("the row of the index was not found in 60_layer/data.js; " if not line else "") + mismatches(pairs) + "".join(f" {g}: {len(v)} different notes;" for g, v in one.items() if len(v) != 1))

    # ================================================================== what_more.csv
    wm_raw = table("what_more.csv")
    wm = _comparisons_whole(wm_raw)
    wcols = ["district", "pc11_district_code", "n1_ha", "r", "r_below_1", "r_below_0_5", "n1_ha_where_r_below_1", "n1_ha_where_r_below_0_5", "plantation_works_fy2016_17",
             "plantation_works_fy2025_26", "works_per_1000_ha_n1_fy2016_17", "works_per_1000_ha_n1_fy2025_26", "works_intensity_is", "cost_at_vgpp_rate_inr", "cost_blank_because",
             "scale_of_the_fall_lakh", "plantation_post_actual_lakh", "scale_is"]
    wkeys = [(r.get("district"), r.get("pc11_district_code")) for r in wm]
    wwant = [(name[k], k) for k in codes] + [("state", "")]
    head = _comparisons_header("what_more.csv")
    held("what_more.csv: the 18 columns this part checks, each once, and no other; 31 rows, none ragged - the 30 districts in census-code order, under the names district_need.csv gives them, then one row 'state' with no code",
          sorted(head) == sorted(wcols) and wkeys == wwant and not _comparisons_ragged(wm_raw),
          f"{len(wm)} rows, {_comparisons_ragged(wm_raw)} ragged, {len(set(wwant) - set(wkeys))} missing, {len(set(wkeys) - set(wwant))} not expected, in order: {wkeys == wwant}; columns {head}")
    wt = {}
    for r in wm:
        wt.setdefault(r.get("pc11_district_code"), r)
    wblank = {c: "" for c in wcols}
    W, tot = {}, dict(n1=Fraction(0), w16=Fraction(0), w25=Fraction(0), post=Fraction(0), pre=Fraction(0), all_pre=Fraction(0), all_post=Fraction(0), b1=Fraction(0), b05=Fraction(0))
    for k in codes:
        e = E[("C1", k)]
        w = dict(n1=fr(need[k][N1]), w16=fr(alloc[k]["plantation_works_fy2016_17"]), w25=fr(alloc[k]["plantation_works_fy2025_26"]), post=fr(alloc[k][POST]),
                 pre=fr(alloc[k][PRE]), all_pre=fr(alloc[k]["r620_all_pre_lakh"]), all_post=fr(alloc[k]["r620_all_post_lakh"]), r=e["r"])
        w["b1"] = w["n1"] if w["r"] is not None and w["r"] < 1 else Fraction(0)
        w["b05"] = w["n1"] if w["r"] is not None and w["r"] < half else Fraction(0)
        for x in tot:
            tot[x] += w[x]
        W[k] = w
    W[""] = dict(tot, r=None)                                      # the state row: sums; it has no r
    rows_of = [(k, name[k]) for k in codes] + [("", "state")]

    def wcell(k, col):
        return wt[k][col] if k in wt else "(no row)"

    pairs = []
    for k, label in rows_of:
        t, w = wt.get(k, wblank), W[k]
        pairs.append((label, tuple(wcell(k, x) for x in ("n1_ha", "plantation_works_fy2016_17", "plantation_works_fy2025_26", "plantation_post_actual_lakh")), (show(w["n1"]), show(w["w16"]), show(w["w25"]), show(w["post"])),
                      number(t["n1_ha"], w["n1"]) and t["plantation_works_fy2016_17"] == show(w["w16"]) and t["plantation_works_fy2025_26"] == show(w["w25"]) and number(t["plantation_post_actual_lakh"], w["post"])))
    check("what_more.csv: n1_ha, plantation_works_fy2016_17, plantation_works_fy2025_26 and plantation_post_actual_lakh are the district's n1_ha_2018_2025 (district_need.csv), its two counts of plantation works and its r620_plantation_post_lakh (district_allocation.csv) - hectares and money as numbers, the counts as the whole numbers they are; the state row holds the exact sums over the 30 districts",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for k, label in rows_of:
        t, r = wt.get(k, wblank), W[k]["r"]
        exp = (show(r, 6), "" if r is None else "yes" if r < 1 else "no", "" if r is None else "yes" if r < half else "no")
        pairs.append((label, (wcell(k, "r"), wcell(k, "r_below_1"), wcell(k, "r_below_0_5")), exp, printed(t["r"], r, 6) and (t["r_below_1"], t["r_below_0_5"]) == exp[1:]))
    check("what_more.csv: r is C1's r (the exact allocation share / need share from the two given tables, rounded half up to the 6 decimals printed), blank where N1 is zero and in the state row; r_below_1 and r_below_0_5 are 'yes' where the exact r is below 1, and below 0.5, else 'no', and blank where r is blank",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = [(label, (wcell(k, "n1_ha_where_r_below_1"), wcell(k, "n1_ha_where_r_below_0_5")), (show(W[k]["b1"]), show(W[k]["b05"])),
              number(wt.get(k, wblank)["n1_ha_where_r_below_1"], W[k]["b1"]) and number(wt.get(k, wblank)["n1_ha_where_r_below_0_5"], W[k]["b05"])) for k, label in rows_of]
    check("what_more.csv: n1_ha_where_r_below_1 and n1_ha_where_r_below_0_5 are the district's N1 where its exact r is below the bound and 0 otherwise (0 too where N1 is zero), as numbers; the state row holds the exact sums over the 30 districts",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for k, label in rows_of:
        t, w = wt.get(k, wblank), W[k]
        i16, i25 = (None, None) if w["n1"] == 0 else (1000 * w["w16"] / w["n1"], 1000 * w["w25"] / w["n1"])
        text = t["works_intensity_is"]
        ok_text = text.startswith(_comparisons_INTENSITY_IS) and (("N1 is zero" in text) == (i16 is None))
        pairs.append((label, (wcell(k, "works_per_1000_ha_n1_fy2016_17"), wcell(k, "works_per_1000_ha_n1_fy2025_26"), wcell(k, "works_intensity_is")),
                      (show(i16, 6), show(i25, 6), _comparisons_INTENSITY_IS + (" ... N1 is zero" if i16 is None else "")),
                      printed(t["works_per_1000_ha_n1_fy2016_17"], i16, 6) and printed(t["works_per_1000_ha_n1_fy2025_26"], i25, 6) and ok_text))
    check("what_more.csv: works_per_1000_ha_n1_fy2016_17 and works_per_1000_ha_n1_fy2025_26 are 1000 x the works / N1, exact, rounded half up to the 6 decimals printed - for a district from its own figures, for the state from the sums - and blank where N1 is zero; "
          "works_intensity_is begins with the specification's words 'an intensity, not a requirement: works have no standard size' and says 'N1 is zero' on exactly the rows where the two are blank",
          all(p[3] for p in pairs), mismatches(pairs))

    reasons = sorted({r.get("cost_blank_because", "") for r in wm})
    filled = [r.get("district") for r in wm if r.get("cost_at_vgpp_rate_inr", "") != ""]
    held("what_more.csv: cost_at_vgpp_rate_inr is a column of the table and is blank on every row, and cost_blank_because gives one reason, the same on all 31 rows, which names VGPP and 00_raw (that the rate is in no file of 00_raw/ is not tested here)",
          bool(wm) and "cost_at_vgpp_rate_inr" in head and not filled and len(reasons) == 1 and "VGPP" in reasons[0] and "00_raw" in reasons[0],
          f"the column is in the table: {'cost_at_vgpp_rate_inr' in head}; rows with a cost: {filled}; reasons given: {reasons}")

    pairs = []
    for k, label in rows_of:
        t, w = wt.get(k, wblank), W[k]
        scale = w["pre"] / w["all_pre"] * w["all_post"]
        text = t["scale_is"]
        ok_text = text == _comparisons_SCALE_IS if k == "" else text.startswith(_comparisons_SCALE_IS) and "do not add to the state row" in text
        pairs.append((label, (wcell(k, "scale_of_the_fall_lakh"), wcell(k, "scale_is")[-60:]), (show(scale, 2), "the specification's sentence" + ("" if k == "" else " ... district rows do not add to the state row")),
                      printed(t["scale_of_the_fall_lakh"], scale, 2) and ok_text))
    check("what_more.csv: scale_of_the_fall_lakh is r620_plantation_pre_lakh / r620_all_pre_lakh x r620_all_post_lakh, exact and unrounded until the end, rounded half up to the 2 decimals printed - for a district from its own three figures, for the state from the three sums over the 30 districts; "
          "scale_is is the specification's sentence ('the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier years are a frozen 2020 snapshot') in the state row, and on a district row begins with it and says that district rows 'do not add to the state row'",
          all(p[3] for p in pairs), mismatches(pairs))

# ---------------------------------------------------------------------------------------------------------------------
# part_panel: district_year_panel.csv, panel_models.csv and panel_models_wcb_grids.json, from the inputs; and what the
# step that writes them says of itself (gates_phase3.csv, its section of gap.provenance.json).
# Written from the definitions in the docstring of the panel builder and of the shared module, not from their code.
# Nothing here is read from the tables under test to rebuild them: the district of a unit comes from 10_units/, the
# crosswalk from the rule, the panel from R6.20 and the Hansen band table, every design matrix from that recomputed
# panel (the exact ratios, not the six decimals the table prints), and the whole inversion of the bootstrap test (the
# bracket, the grid, the bisection) from this part's own arithmetic. The kept grids are then held to that inversion.
# ---------------------------------------------------------------------------------------------------------------------
_panel_T = "district_year_panel.csv"
_panel_M = "panel_models.csv"
_panel_GRIDS = "panel_models_wcb_grids.json"
_panel_GATES = "gates_phase3.csv"
_panel_RECORD = "gap.provenance.json"
_panel_STEP = "08_build_gap_panel"
_panel_STEP_WRITES = (_panel_T, _panel_M, "panel_models.txt", _panel_GRIDS, _panel_GATES)
_panel_UNITS = "10_units/units.gpkg"
_panel_OUTSIDE = "10_units/outside_village_district.csv"
_panel_R620 = "00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv"
_panel_R620_STATE = "00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv"
_panel_FRA = "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"
_panel_DECISION = "55_decision/condition_by_unit.csv"
_panel_HANSEN = "20_degradation/hansen_loss_by_canopy_band_by_unit.csv"

# the owner's spelling rule of 10 October 2026, as the definition gives it
_panel_RULE = {"ANGUL": "384", "BOLANGIR": "393", "BOUDH": "391", "DEOGARH": "373", "JAJPUR": "382", "SONEPUR": "392"}
_panel_CODES = tuple(str(c) for c in range(370, 400))
_panel_YEARS = tuple(range(2014, 2027))          # the 13 financial years of R6.20, by their first calendar year t
_panel_PRE = (2014, 2017)                        # FY2014-15 to FY2017-18
_panel_POST = (2018, 2025)                       # FY2018-19 to FY2025-26
_panel_PART = 2026                               # FY2026-27, a part year: in the panel, in no model
_panel_HANSEN_YEARS = (2001, 2025)               # Hansen's record of loss
_panel_BANDS = (("gt30", "dense"), ("gt10le30", "open"))
_panel_FROZEN = "10/10/2020"
_panel_PCT = "0.000001"                          # the six decimals the tables print for a per cent and for a p at a bracket's end
_panel_COLUMNS = (
    "pc11_district_code", "district_name", "r620_district", "fy", "fy_start_year", "period", "part_year", "in_models",
    "plantation_lakh", "nrm_lakh", "water_lakh", "all_lakh", "plantation_pct_of_all", "plantation_works_ongoing",
    "plantation_works_completed", "r620_last_updated", "frozen_2020_snapshot", "loss_ha_year_t_minus_1", "loss_ha_year_t",
    "loss_dense_ha_year_t_minus_1", "loss_dense_ha_year_t", "standing_forest_ha_start_of_year_t_minus_1",
    "loss_pct_of_standing_year_t_minus_1")
_panel_MODEL_COLUMNS = (
    "id", "term", "headline", "spec", "outcome", "outcome_unit", "regressor", "regressor_unit", "coefficient_unit", "n",
    "clusters", "n_parameters", "coefficient", "se_cr1", "t_cr1", "wcb_ci95_lo", "wcb_ci95_hi", "wcb_unbounded_lo",
    "wcb_unbounded_hi", "wcb_crossings_lo", "wcb_crossings_hi", "wcb_p_rises_again_lo", "wcb_p_rises_again_hi",
    "wcb_p_at_bracket_end_lo", "wcb_p_at_bracket_end_hi", "wcb_p", "wcb_B", "wcb_seed", "wcb_weights")
_panel_GRID_KEYS = ("B", "estimate", "grid", "se_cr1", "seed", "tests_made")
# the models: id, outcome, regressors (the reported terms, in the definition's order), dummies
_panel_SPECS = (
    ("P1", "share", ("loss_t1",), "by period"),
    ("P2", "share", ("loss_t1",), "plain"),
    ("P3", "asinh_plantation", ("loss_t1",), "by period"),
    ("P4", "share", ("loss_t",), "by period"),
    ("P5", "share", ("loss_pct_t1",), "by period"),
    ("P6", "share", ("dense_t1",), "by period"),
    ("P7", "share", ("loss_t1", "loss_t1_x_post"), "by period"),
)
# Which rows must carry the same words and which must not, by the definitions ("P2: the same with ...", "P3: P1 with asinh(
# plantation_lakh) as the outcome", "P4: P1 with loss in calendar year t", ...). A row is (model, place of the term).
_panel_SAME_WORDS = {
    "term": ((("P1", 0), ("P2", 0), ("P3", 0), ("P7", 0)), (("P4", 0),), (("P5", 0),), (("P6", 0),), (("P7", 1),)),
    "regressor": ((("P1", 0), ("P2", 0), ("P3", 0), ("P7", 0)), (("P4", 0),), (("P5", 0),), (("P6", 0),), (("P7", 1),)),
    "regressor_unit": ((("P1", 0), ("P2", 0), ("P3", 0), ("P7", 0)), (("P4", 0),), (("P5", 0),), (("P6", 0),), (("P7", 1),)),
    "outcome": ((("P1", 0), ("P2", 0), ("P4", 0), ("P5", 0), ("P6", 0), ("P7", 0), ("P7", 1)), (("P3", 0),)),
    "outcome_unit": ((("P1", 0), ("P2", 0), ("P4", 0), ("P5", 0), ("P6", 0), ("P7", 0), ("P7", 1)), (("P3", 0),)),
    "spec": ((("P1", 0), ("P3", 0), ("P4", 0), ("P5", 0), ("P6", 0), ("P7", 0), ("P7", 1)), (("P2", 0),)),
    "coefficient_unit": ((("P1", 0), ("P2", 0), ("P7", 0)), (("P3", 0),), (("P4", 0),), (("P5", 0),), (("P6", 0),), (("P7", 1),)),
}
_panel_HEADLINE = "P1"
# The words that tell one model's regressor from another's, held to the rows the definitions give them to (and to no other) in
# each of these columns: the classes above hold only WHICH rows carry the same words, and two rows that exchanged theirs keep them.
_panel_NAMING = ("term", "regressor", "regressor_unit", "coefficient_unit")
_panel_RECORD_KEYS = ("script", "script_sha256", "shared_module", "shared_module_sha256", "run_utc", "inputs", "outputs", "package_versions",
                      "environment", "seeds", "B", "interval", "gates", "gates_passed")
_panel_BASE_SEED = 20261010                      # the builders' base; panel model k, term j: base + 300 + 10k + j
_panel_B = {"P1": 9999}                          # 1,999 for the others
_panel_B_OTHERS = 1999
_panel_LEVEL = 0.05
_panel_CLIMB = 0.01
_panel_FIRST_REACH = 4                           # the bracket starts at the estimate -/+ 4 CR1 standard errors
_panel_MAX_DOUBLINGS = 10                        # and is doubled as a whole, one width for both sides, at most ten times
_panel_STEPS = 16                                # p is read on 16 equal steps from the estimate to each end
_panel_BISECT_TO = 0.001                         # of a CR1 standard error
_panel_OWN_SEED = 20261910                       # this part's own draws: not a seed of any builder
_panel_OWN_DRAWS = 9999
_panel_SDS = 3.5                                 # two bootstrap p's from different draws: at most this many standard errors apart,
_panel_P_TOL = 0.04                              # and never more than this
_panel_NUDGE = 0.002                             # of a CR1 standard error: the builder bisects to 0.001
_panel_SAME = 1e-9                               # two p's from the same draws; a point of a grid, in CR1 standard errors
_panel_FLOAT = 1e-10                             # a coefficient or a standard error kept in full, computed twice
# The package compiles its loop over the draws at every call, threaded by default. Not threaded it gives the same p (the
# 56 values the first version of this part asked for were compared, bit for bit) and compiles in a third of the time.
_panel_PKG_PARALLEL = False
_panel_COEF_TOL = 0.5e-8 + 1e-10                 # the table prints eight decimals: half a unit of the last, and floating point
_panel_T_TOL = 0.5e-6 + 1e-10                    # and six for t


def _panel_dec(cell):
    """A cell as a Decimal; None where it is blank or not a finite number."""
    try:
        s = str(cell).strip()
        if s == "":
            return None
        v = Decimal(s)
        return v if v.is_finite() else None
    except Exception:
        return None


def _panel_float(cell):
    v = _panel_dec(cell)
    return None if v is None else float(v)


def _panel_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _panel_exact(key, cell, value):
    """(key, in the table, recomputed, equal as numbers); `value` None means the cell must be blank."""
    if value is None:
        return (key, cell, "", cell == "")
    d = _panel_dec(cell)
    return (key, cell, str(value), d is not None and d == value)


def _panel_fy_label(t):
    return f"{t}-{(t + 1) % 100:02d}"


def _panel_period(t):
    if _panel_PRE[0] <= t <= _panel_PRE[1]:
        return "pre"
    if _panel_POST[0] <= t <= _panel_POST[1]:
        return "post"
    return "part_year" if t == _panel_PART else ""


def _panel_table(name):
    """A table of the folder being checked, as rows; no rows if it cannot be read (the check of its shape then says why)."""
    try:
        return table(name)
    except Exception:
        return []


def _panel_header(name):
    """The first line of a table of the folder being checked, cell by cell as written, and how many of its other lines have
    a number of cells other than that line's. (None, the reason) if the file cannot be read."""
    try:
        with open(GAP / name, encoding="utf-8", newline="") as f:
            lines = list(csv.reader(f))
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    if not lines:
        return [], 0
    return lines[0], sum(1 for line in lines[1:] if len(line) != len(lines[0]))


def _panel_rebuild():
    """The panel recomputed from the inputs, and what was found about the inputs on the way.

    Returns (panel, found, frozen_years): panel is {(census code, fy): {column: value}} with money, hectares and ratios as
    exact Decimals (unrounded; None where the cell is to be blank) and text as text; found is a list of (what, ok, detail)
    about the inputs themselves; frozen_years are the first calendar years of the financial years the state totals file
    stamps 10/10/2020.
    """
    import collections
    import pyogrio

    found = []
    zero = Decimal(0)

    # a district for every unit: an LGD panchayat unit from units.gpkg, an outside-village unit from the outside table
    gp = pyogrio.read_dataframe(ROOT / _panel_UNITS, read_geometry=False, columns=["unit_id", "pc11_district_code", "outside_village"])
    outside = {}
    for r in rows(_panel_OUTSIDE):
        outside.setdefault(r["unit_id"], []).append(r["pc11_district_code"].strip())
    unit_code, bad_units = {}, []
    for uid, code, flag in zip(gp["unit_id"].tolist(), gp["pc11_district_code"].tolist(), gp["outside_village"].tolist()):
        uid = str(uid)
        if int(flag) == 1:
            got = outside.get(uid, [])
            code = got[0] if len(got) == 1 else ""
        else:
            code = "" if code is None or code != code else str(code).strip()
        if uid in unit_code or code not in _panel_CODES:
            bad_units.append(uid)
        unit_code[uid] = code
    hansen = rows(_panel_HANSEN)
    hansen_ids = [r["unit_id"] for r in hansen]
    ok = (len(unit_code) == 11468 and len(gp) == 11468 and not bad_units and len(set(unit_code.values())) == 30
          and len(hansen_ids) == 11468 and set(hansen_ids) == set(unit_code))
    found.append((f"panel, inputs: each of the 11,468 units of {_panel_UNITS} gets one census district code from 370 to 399 (an LGD "
                  f"panchayat unit the one it carries there, an outside-village unit the one {_panel_OUTSIDE} gives it), 30 districts in "
                  f"all, and the Hansen band table has the same 11,468 units, once each", ok,
                  "" if ok else f"units {len(unit_code)}, without one code {len(bad_units)} (e.g. {bad_units[:3]}), districts "
                  f"{len(set(unit_code.values()))}, Hansen rows {len(hansen_ids)}, Hansen units not in units.gpkg {len(set(hansen_ids) - set(unit_code))}"))

    # the census name of each code, as the FRA table and the decision table carry it
    name_fra = {}
    for r in rows(_panel_FRA):
        name_fra.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"])
    decision = rows(_panel_DECISION)
    name_dec = {}
    for r in decision:
        name_dec.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"])
    names_ok = (set(name_fra) == set(_panel_CODES) == set(name_dec)
                and all(len(name_fra[c]) == 1 and name_fra[c] == name_dec[c] for c in _panel_CODES))
    name = {c: sorted(name_fra.get(c) or name_dec.get(c) or {""})[0] for c in _panel_CODES}

    # R6.20's names to census codes: the case-folded census name, or the spelling rule
    r620 = rows(_panel_R620)
    r620_names = sorted({r["district"] for r in r620})
    by_upper = collections.defaultdict(list)
    for c in _panel_CODES:
        by_upper[name[c].upper()].append(c)
    cross, failed = {}, []
    for n in r620_names:
        hit = by_upper.get(n.upper(), [])
        if len(hit) == 1:
            cross[n] = hit[0]
        else:
            failed.append(n)
            cross[n] = _panel_RULE.get(n, "")
    r620_of = {}
    for n, c in cross.items():
        r620_of.setdefault(c, []).append(n)
    ok = (names_ok and len(r620_names) == 30 and sorted(failed) == sorted(_panel_RULE)
          and sorted(cross.values()) == list(_panel_CODES) and all(len(v) == 1 for v in r620_of.values()))
    found.append((f"panel, inputs: the crosswalk rebuilt from the rule: R6.20 has 30 district names, 24 equal a census name once both are "
                  f"upper-cased, exactly the six of the spelling rule do not, and the 30 map one to one onto the codes 370 to 399; "
                  f"the FRA table and the decision table give one and the same name for every code", ok,
                  "" if ok else f"names {len(r620_names)}, failing the case-folded match {failed}, codes reached {len(set(cross.values()))}, "
                  f"FRA and decision names agree: {names_ok}"))

    # R6.20: one row per financial year, category and district; one stamp per year in the state totals file
    r6 = {}
    dup = 0
    for r in r620:
        k = (r["fy"], r["category"], r["district"])
        dup += k in r6
        r6[k] = r
    fy_r620 = {t: f"{t}-{t + 1}" for t in _panel_YEARS}
    want = {(fy_r620[t], cat, n) for t in _panel_YEARS for cat in ("NRM", "Water", "Plantation") for n in r620_names}
    all_differs = [(fy_r620[t], n) for t in _panel_YEARS for n in r620_names
                   if len({_panel_dec(r6[(fy_r620[t], cat, n)]["exp_all_lakh"]) for cat in ("NRM", "Water", "Plantation") if (fy_r620[t], cat, n) in r6}) != 1]
    stamps = {}
    for r in rows(_panel_R620_STATE):
        stamps.setdefault(r["fy"], set()).add(r["last_updated"])
    stamp_ok = set(stamps) == set(fy_r620.values()) and all(len(v) == 1 for v in stamps.values())
    frozen_years = sorted(int(f[:4]) for f, v in stamps.items() if v == {_panel_FROZEN})
    ok = dup == 0 and set(r6) == want and len(r620) == 1170 and not all_differs and stamp_ok
    found.append((f"panel, inputs: R6.20's district file has one row for each of 13 financial years (2014-2015 to 2026-2027) x 3 categories "
                  f"x 30 districts and nothing else, with one exp_all_lakh per district-year; the state totals file prints one stamp for "
                  f"each of the 13 years", ok,
                  "" if ok else f"rows {len(r620)}, keys twice {dup}, keys missing {len(want - set(r6))}, keys not expected {len(set(r6) - want)}, "
                  f"district-years with more than one exp_all_lakh {len(all_differs)}, one stamp a year: {stamp_ok}"))

    # the land of 2000 by band: the Hansen band table, which must be the decision table's
    dec_land = {r["unit_id"]: (_panel_dec(r["dense_2000_ha"]), _panel_dec(r["open_2000_ha"])) for r in decision}
    differs = [r["unit_id"] for r in hansen
               if dec_land.get(r["unit_id"]) != (_panel_dec(r["area_ha_gt30"]), _panel_dec(r["area_ha_gt10le30"]))]
    ok = len(decision) == 11468 and not differs
    found.append((f"panel, inputs: the land of 2000 in the dense and the open band is the same number in the Hansen band table "
                  f"(area_ha_gt30, area_ha_gt10le30) and in the decision table (dense_2000_ha, open_2000_ha), every unit, so 'the band's "
                  f"land in 2000' has one reading", ok, "" if ok else f"{len(differs)} units differ, e.g. {differs[:3]}"))

    # forest loss by district, band and calendar year; forest standing at the start of each calendar year
    loss = collections.defaultdict(lambda: zero)           # (code, band, year)
    standing = collections.defaultdict(lambda: zero)       # (code, year): at the start of that year
    for r in hansen:
        code = unit_code.get(r["unit_id"], "")
        for band, _ in _panel_BANDS:
            left = D(r[f"area_ha_{band}"])                 # the band's land in 2000
            for y in range(_panel_HANSEN_YEARS[0], _panel_HANSEN_YEARS[1] + 1):
                standing[(code, y)] += left if left > zero else zero     # land of 2000 less loss of 2001..y-1, not below zero
                lost = D(r[f"loss_ha_{band}_{y}"])
                loss[(code, band, y)] += lost
                left -= lost
    # the decision table's own forest at the start of three of its windows, by district (a second route to the same column)
    window_start = collections.defaultdict(lambda: zero)   # (code, first year of the window)
    for r in decision:
        code = unit_code.get(r["unit_id"], "")
        for w in ("2017_2023", "2018_2025", "2021_2025"):
            window_start[(code, int(w[:4]))] += D(r[f"forest_at_window_start_ha_{w}"])

    panel = {}
    for code in _panel_CODES:
        dn = (r620_of.get(code) or [""])[0]
        for t in _panel_YEARS:
            fy = fy_r620[t]
            cell = lambda cat, col: _panel_dec(r6[(fy, cat, dn)][col]) if (fy, cat, dn) in r6 else None
            text = lambda cat, col: r6[(fy, cat, dn)][col] if (fy, cat, dn) in r6 else ""
            stamp = sorted(stamps.get(fy, {""}))[0]
            both = lambda y: loss[(code, "gt30", y)] + loss[(code, "gt10le30", y)]
            has_t = t <= _panel_HANSEN_YEARS[1]            # Hansen's record ends in 2025
            row = {
                "pc11_district_code": code, "district_name": name[code], "r620_district": dn,
                "fy": _panel_fy_label(t), "fy_start_year": str(t), "period": _panel_period(t),
                "part_year": "1" if t == _panel_PART else "0", "in_models": "0" if t == _panel_PART else "1",
                "plantation_lakh": cell("Plantation", "exp_cat_lakh"), "nrm_lakh": cell("NRM", "exp_cat_lakh"),
                "water_lakh": cell("Water", "exp_cat_lakh"), "all_lakh": cell("Plantation", "exp_all_lakh"),
                "plantation_works_ongoing": text("Plantation", "works_ongoing"),
                "plantation_works_completed": text("Plantation", "works_completed"),
                "r620_last_updated": stamp, "frozen_2020_snapshot": "1" if stamp == _panel_FROZEN else "0",
                "loss_ha_year_t_minus_1": both(t - 1), "loss_ha_year_t": both(t) if has_t else None,
                "loss_dense_ha_year_t_minus_1": loss[(code, "gt30", t - 1)],
                "loss_dense_ha_year_t": loss[(code, "gt30", t)] if has_t else None,
                "standing_forest_ha_start_of_year_t_minus_1": standing[(code, t - 1)],
                "_t": t, "_window_start": window_start.get((code, t - 1)),
            }
            pl, al, st = row["plantation_lakh"], row["all_lakh"], row["standing_forest_ha_start_of_year_t_minus_1"]
            row["plantation_pct_of_all"] = 100 * pl / al if pl is not None and al else None
            row["loss_pct_of_standing_year_t_minus_1"] = 100 * row["loss_ha_year_t_minus_1"] / st if st else None
            panel[(code, row["fy"])] = row
    return panel, found, frozen_years


def _panel_design(panel, spec):
    """One model's design from the recomputed panel: the regressor(s) first, then every dummy written out, no constant.

    Floats are made here from the exact values (the unrounded ratios). Returns (y, X, column names, cluster index 0..G-1 in
    the sorted order of the district codes, G).
    """
    _, outcome, regressors, dummies = spec
    sample = []
    for (code, fy), r in sorted(panel.items(), key=lambda kv: (kv[0][0], kv[1]["_t"])):
        if r["in_models"] != "1":
            continue
        f = lambda v: None if v is None else float(v)
        loss_t1 = f(r["loss_ha_year_t_minus_1"])
        v = {
            "share": f(r["plantation_pct_of_all"]),
            "asinh_plantation": None if r["plantation_lakh"] is None else math.asinh(float(r["plantation_lakh"])),
            "loss_t1": None if loss_t1 is None else loss_t1 / 100,
            "loss_t": None if r["loss_ha_year_t"] is None else float(r["loss_ha_year_t"]) / 100,
            "dense_t1": None if r["loss_dense_ha_year_t_minus_1"] is None else float(r["loss_dense_ha_year_t_minus_1"]) / 100,
            "loss_pct_t1": f(r["loss_pct_of_standing_year_t_minus_1"]),
        }
        v["loss_t1_x_post"] = None if v["loss_t1"] is None else v["loss_t1"] * (1.0 if r["period"] == "post" else 0.0)
        if v[outcome] is None or any(v[x] is None for x in regressors):
            continue                                        # complete cases of the model's own variables
        sample.append((code, r["period"], r["_t"], v))
    cols = [[s[3][x] for s in sample] for x in regressors]
    names = list(regressors)
    if dummies == "by period":                              # every district in each period; every year but the first of each period
        for lab in sorted({(s[0], s[1]) for s in sample}):
            cols.append([1.0 if (s[0], s[1]) == lab else 0.0 for s in sample])
            names.append(f"district {lab[0]} in {lab[1]}")
        for per in sorted({s[1] for s in sample}):
            for t in sorted({s[2] for s in sample if s[1] == per})[1:]:
                cols.append([1.0 if s[2] == t else 0.0 for s in sample])
                names.append(f"year {t}")
    else:                                                   # every district; every year but the first
        for code in sorted({s[0] for s in sample}):
            cols.append([1.0 if s[0] == code else 0.0 for s in sample])
            names.append(f"district {code}")
        for t in sorted({s[2] for s in sample})[1:]:
            cols.append([1.0 if s[2] == t else 0.0 for s in sample])
            names.append(f"year {t}")
    codes = sorted({s[0] for s in sample})
    y = np.array([s[3][outcome] for s in sample], dtype=float)
    X = np.array(cols, dtype=float).T
    cl = np.array([codes.index(s[0]) for s in sample], dtype=int)
    return y, X, names, cl, len(codes)


def _panel_ols_cr1(y, X, cl, G):
    """OLS by least squares and the CR1 standard errors: the cluster sandwich times G/(G-1) x (N-1)/(N-K)."""
    n, k = X.shape
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta
    bread = np.linalg.inv(X.T @ X)
    meat = np.zeros((k, k))
    for g in range(G):
        s = X[cl == g].T @ u[cl == g]
        meat += np.outer(s, s)
    V = bread @ meat @ bread * (G / (G - 1)) * ((n - 1) / (n - k))
    return beta, np.sqrt(np.diag(V)), int(rank)


def _panel_own_p(y, X, cl, G, j, b0, W):
    """This part's own restricted (null-imposed) wild cluster bootstrap-t of H0: beta_j = b0. W is G x draws.

    The model is fitted with beta_j held at b0; y* = that fit + its residual x the weight of the row's cluster; the full
    model is fitted again to every y*; t* = (beta*_j - b0) / its CR1 standard error. p = the share of draws with
    |t*| >= |t|, t being the same statistic of the data.
    """
    n, k = X.shape
    c = (G / (G - 1)) * ((n - 1) / (n - k))
    A = np.linalg.inv(X.T @ X) @ X.T                        # beta = A y
    a = A[j]
    of_cluster = np.zeros((G, n))
    of_cluster[cl, np.arange(n)] = 1.0
    beta = A @ y
    s = of_cluster @ (a * (y - X @ beta))                   # each cluster's part of beta_j's score
    t = (beta[j] - b0) / math.sqrt(c * float(s @ s))
    X0 = np.delete(X, j, axis=1)                            # the restricted model: y - b0 x on the other columns
    gamma, _, _, _ = np.linalg.lstsq(X0, y - b0 * X[:, j], rcond=None)
    u0 = y - b0 * X[:, j] - X0 @ gamma
    Ystar = (y - u0)[:, None] + u0[:, None] * W[cl, :]      # n x draws
    Bstar = A @ Ystar
    S = (of_cluster * a) @ (Ystar - X @ Bstar)              # G x draws
    tstar = (Bstar[j] - b0) / np.sqrt(c * (S * S).sum(axis=0))
    return float(np.mean(np.abs(tstar) >= abs(t)))


def _panel_pkg_p(y, X, names, cl, j, b0, B, seed):
    """The `wildboottest` package's p of H0: beta_j = b0, the way the tables' intervals were found: y - b0 x, the recorded seed."""
    import warnings
    import pandas as pd
    import statsmodels.api as sm
    from wildboottest.wildboottest import wildboottest

    model = sm.OLS(pd.Series(y - b0 * X[:, j], name="y"), pd.DataFrame(X, columns=names))
    with warnings.catch_warnings():                         # numpy's "invalid value encountered in matmul" on this machine
        warnings.simplefilter("ignore")
        with np.errstate(all="ignore"):
            res = wildboottest(model, param=names[j], cluster=pd.Series(cl), B=B, weights_type="webb", impose_null=True,
                               seed=seed, show=False, parallel=_panel_PKG_PARALLEL)
    p = float(res["p-value"].iloc[0])
    return p if math.isfinite(p) else None


def _panel_pkg_weights(G, B, seed):
    """The Webb weights the package draws from a seed (its own generator): G x B, rows in the sorted order of the clusters."""
    from wildboottest.weights import draw_weights

    v, _ = draw_weights(t="webb", full_enumeration=False, N_G_bootcluster=G, boot_iter=B, rng=np.random.default_rng(seed))
    return v


def _panel_sd(p, B):
    """The standard error of the difference between two bootstrap p's of a test whose p is `p`: one from B draws, one from this part's own."""
    return math.sqrt(p * (1 - p) * (1 / B + 1 / _panel_OWN_DRAWS))


def _panel_invert(P, b, s):
    """This part's own inversion of the bootstrap test of one term, by the definition as it stands. `P(b0)` is the p of H0: beta = b0.

    The bracket is the coefficient -/+ 4 x 2^d se_cr1 with ONE d for both sides: the smallest d, 0 to 10, at which p is below
    0.05 at both ends, or 10 (doubled as a whole, at most ten times). p is then read on 16 equal steps from the coefficient to
    each end. A side whose p at the end is not below 0.05 is unbounded. On any other side the outermost step in which p
    crosses 0.05 is halved until it is no wider than 0.001 se_cr1.

    Returns (d, sides, asked, ends): sides[side] has the 17 values of b0 and of p, `unbounded`, `crossings` (the steps in which p
    crosses 0.05), `rises` (going outward, p climbs more than 0.01 above a value it had already fallen to) and `bracket`
    (the two ends of the halved step, the inner first; None on an unbounded side). `asked` is every null at which a p was
    read, in order, repeats and all. `ends` is the p at the lower and at the upper end of each bracket tried, d = 0 first.
    """
    asked, ends = [], []

    def ask(b0):
        asked.append(b0)
        return P(b0)

    far = lambda sign, k: b + sign * _panel_FIRST_REACH * 2 ** k * s
    d = 0
    while True:
        ends.append((ask(far(-1.0, d)), ask(far(1.0, d))))
        if (ends[-1][0] < _panel_LEVEL and ends[-1][1] < _panel_LEVEL) or d == _panel_MAX_DOUBLINGS:
            break
        d += 1
    sides = {}
    for side, sign in (("lo", -1.0), ("hi", 1.0)):
        end = far(sign, d)
        b0s = [b] + [b + (end - b) * i / _panel_STEPS for i in range(1, _panel_STEPS)] + [end]
        ps = [ask(x) for x in b0s]
        crossing = [i for i in range(_panel_STEPS) if (ps[i] < _panel_LEVEL) != (ps[i + 1] < _panel_LEVEL)]
        rises, lowest = False, ps[0]
        for v in ps[1:]:
            rises = rises or v > lowest + _panel_CLIMB      # climbs more than 0.01 above a value it had already fallen to
            lowest = min(lowest, v)
        bracket = None
        if ps[-1] < _panel_LEVEL and crossing:              # p is 1 at the coefficient, so a side that ends below 0.05 has a crossing
            inner, outer = b0s[crossing[-1]], b0s[crossing[-1] + 1]
            while abs(outer - inner) > _panel_BISECT_TO * s:
                middle = (inner + outer) / 2
                if ask(middle) < _panel_LEVEL:
                    outer = middle
                else:
                    inner = middle
            bracket = (inner, outer)
        sides[side] = {"b0": b0s, "p": ps, "unbounded": bracket is None, "crossings": len(crossing), "rises": rises, "bracket": bracket}
    return d, sides, asked, ends


def _panel_says(text):
    """Which of the things that tell one model's regressor from another's a label names, in the definitions' own words."""
    t = text.lower()
    return {"the lag t-1": any(x in t for x in ("t-1", "t - 1", "t_minus_1", "t minus 1")),
            "the dense band alone": "dense" in t and "open" not in t,
            "the standing forest": "standing" in t,
            "the post period": "post" in t}


def _panel_classes(keys, word_of):
    """The rows named by `keys` gathered by the words they carry: a sorted list of sorted groups."""
    groups = {}
    for k in keys:
        groups.setdefault(word_of(k), []).append(k)
    return sorted(sorted(v) for v in groups.values())


def _panel_step_checks(panel, fits, terms, seeds_wanted):
    """What the step says of itself: gates_phase3.csv, row by row, and its section of the record of provenance.

    `fits` is (n, clusters, rank is full) for each model fitted here; `terms` is (bounded on both sides, p fell steadily on both
    sides) for each reported term, from this part's own inversion; `seeds_wanted` is {id:term: seed}. The definitions name the
    gate table and do not list its rows: each row's own label is taken as its definition, and found by a phrase of it.
    """
    import collections
    import re

    zero = Decimal(0)
    sums = collections.defaultdict(lambda: zero)            # (code, column, period)
    whole = True
    for (code, _), r in panel.items():
        for col in ("plantation_lakh", "nrm_lakh", "water_lakh", "all_lakh"):
            whole = whole and r[col] is not None
            sums[(code, col, r["period"])] += r[col] if r[col] is not None else zero
    alloc = {(r.get("pc11_district_code") or ""): r for r in _panel_table("district_allocation.csv")}
    gaps = []
    for code in _panel_CODES:
        for cat in ("plantation", "nrm", "water", "all"):
            for per in ("pre", "post", "part_year"):
                there = _panel_dec((alloc.get(code) or {}).get(f"r620_{cat}_{per}_lakh"))
                gaps.append(None if there is None else abs(there - sums[(code, f"{cat}_lakh", per)]))
    worst = max(gaps) if whole and all(g is not None for g in gaps) else None
    total = {per: sum((sums[(code, "plantation_lakh", per)] for code in _panel_CODES), zero) for per in ("pre", "post", "part_year")}
    sd = {}
    for per in ("pre", "post"):
        v = [float(r["plantation_pct_of_all"]) for r in panel.values() if r["period"] == per and r["plantation_pct_of_all"] is not None]
        sd[per] = (float(np.std(v)), float(np.std(v, ddof=1))) if len(v) > 1 else None
    at_2018 = [r for r in panel.values() if r["_t"] == 2019]
    standing_same = len(at_2018) == 30 and all(r["_window_start"] is not None and r["standing_forest_ha_start_of_year_t_minus_1"] == r["_window_start"] for r in at_2018)
    loss_window = sum((r["loss_ha_year_t"] for r in panel.values() if 2018 <= r["_t"] <= 2025 and r["loss_ha_year_t"] is not None), zero)
    n_in = sum(1 for r in panel.values() if r["in_models"] == "1")
    fitted = sum(1 for n, G, full in fits if n == 360 and G == 30 and full)
    n_bounded, n_steady = sum(1 for bounded, _ in terms if bounded), sum(1 for _, steady in terms if steady)

    # a phrase of the label; what `found` must be; how `expected` stands to it
    number = lambda v: ("number", v)
    wanted = (
        ("rows of the panel", number(Decimal(len(panel))), "the same number"),
        ("district-years in the models", number(Decimal(n_in)), "the same number"),
        ("against step 2's", number(worst), "the same number"),
        ("plantation expenditure of the panel, pre,", number(total["pre"]), "the same number"),
        ("plantation expenditure of the panel, post,", number(total["post"]), "the same number"),
        ("plantation expenditure of the panel, part_year,", number(total["part_year"]), "the same number"),
        ("across district-years, pre,", ("two standard deviations", sd["pre"]), "the first of the two"),
        ("across district-years, post,", ("two standard deviations", sd["post"]), "the first of the two"),
        ("forest standing at the start of 2018", ("words", "yes" if standing_same else "no"), "the same words"),
        ("forest loss of calendar years 2018 to 2025", number(loss_window), "within 1"),
        ("models fitted", number(Decimal(fitted)), "the same number"),
        ("bounded on both sides", ("words", f"{n_bounded} of {len(terms)}"), "the word reported"),
        ("fell steadily on both sides", ("words", f"{n_steady} of {len(terms)}"), "the word reported"),
    )
    gates = _panel_table(_panel_GATES)
    header, ragged = _panel_header(_panel_GATES)
    found_pairs, expected_pairs = [], []
    for phrase, (kind, value), rule in wanted:
        hits = [r for r in gates if phrase in (r.get("gate") or "")]
        if len(hits) != 1:
            for pairs in (found_pairs, expected_pairs):
                pairs.append((phrase, f"{len(hits)} rows with this phrase in the label", "one row", False))
            continue
        said, expected, passed = (hits[0].get(c) or "" for c in ("found", "expected", "pass"))
        if value is None:
            found_pairs.append((phrase, said, "could not be recomputed", False))
            first = None
        elif kind == "number":
            found_pairs.append(_panel_exact(phrase, said, value))
            first = _panel_dec(said)
        elif kind == "words":
            found_pairs.append((phrase, said, value, said == value))
            first = None
        else:                                               # "11.25 (11.30)": n in the divisor, then n - 1, each to the two decimals printed
            m = re.fullmatch(r"\s*(\d+\.\d\d)\s*\(\s*(\d+\.\d\d)\s*\)\s*", said)
            ok = m is not None and all(abs(float(m.group(i + 1)) - value[i]) <= 0.005 + 1e-9 for i in (0, 1))
            found_pairs.append((phrase, said, f"{value[0]:.4f} ({value[1]:.4f}), to two decimals", ok))
            first = _panel_dec(m.group(1)) if m else None
        want = _panel_dec(expected)
        if rule == "the same number":
            ok = first is not None and want is not None and first == want
        elif rule == "the first of the two":
            ok = first is not None and want is not None and first == want
        elif rule == "within 1":
            ok = first is not None and want is not None and abs(first - want) <= 1
        elif rule == "the same words":
            ok = expected == said
        else:
            ok = expected == "reported"
        expected_pairs.append((phrase, f"expected {expected!r}, found {said!r}, pass {passed!r}", f"pass yes, and expected is {rule}", ok and passed == "yes"))
    shape = header == ["gate", "expected", "found", "pass"] and ragged == 0 and len(gates) == len(wanted)
    check(f"{_panel_GATES}: {len(wanted)} rows with the columns gate, expected, found, pass, and `found` in each is what this part recomputes for what the row's "
          f"label names (the definitions do not list the rows; a row is known by a phrase of its label): the rows of the panel and those in the models; the "
          f"largest difference between the recomputed panel's sums by district, category and period and district_allocation.csv's r620_*_lakh columns; "
          f"plantation expenditure by period, exactly; the standard deviation of plantation's share across the district-years of pre and of post, with n "
          f"and with n - 1 in the divisor, each to the 2 decimals printed (|difference| <= 0.005); whether the forest standing at the start of 2018 is "
          f"the decision table's in every district; the loss of 2018 to 2025 (loss_ha_year_t), exactly; the models fitted on 360 district-years and 30 "
          f"clusters; the terms bounded on both sides and those whose p fell steadily (one crossing a side, no climb back), by this part's own inversion",
          shape and all(p[3] for p in found_pairs),
          mismatches(found_pairs) or ("" if shape else f"header {header}; rows {len(gates)}; rows with another number of cells {ragged}"))
    check(f"{_panel_GATES}: every row has pass = yes, and its `expected` stands to its `found` as its label says: the same number; for the two standard "
          f"deviations the figure with n in the divisor; for the loss of 2018 to 2025 within 1; yes for the row that asks a question; the word reported for "
          f"the two rows that are not gates on a value", len(expected_pairs) == len(wanted) and all(p[3] for p in expected_pairs) and all((r.get("pass") or "") == "yes" for r in gates),
          mismatches(expected_pairs))

    try:
        record = json.loads((GAP / _panel_RECORD).read_text(encoding="utf-8"))
    except Exception:
        record = {}
    steps = record.get("steps") if isinstance(record, dict) else None
    sec = steps.get(_panel_STEP) if isinstance(steps, dict) else None
    sec = sec if isinstance(sec, dict) else {}
    wrong = [] if sec else [f"no section {_panel_STEP}"]
    outs = sorted(sec.get("outputs")) if isinstance(sec.get("outputs"), dict) else []
    if outs != sorted("50_gap/" + n for n in _panel_STEP_WRITES):
        wrong.append(f"its outputs are {outs}")
    n_yes = sum(1 for r in gates if (r.get("pass") or "") == "yes")
    if (sec.get("gates"), sec.get("gates_passed")) != (len(gates), n_yes) or isinstance(sec.get("gates"), bool) or isinstance(sec.get("gates_passed"), bool) or not gates:
        wrong.append(f"gates {sec.get('gates')!r} and gates_passed {sec.get('gates_passed')!r}; {_panel_GATES} has {len(gates)} rows, {n_yes} with pass = yes")
    said = sec.get("seeds") if isinstance(sec.get("seeds"), dict) else {}
    if said.get("base") != _panel_BASE_SEED or isinstance(said.get("base"), bool) or said.get("by_model_and_term") != seeds_wanted or len(seeds_wanted) != 8:
        wrong.append(f"seeds {str(said)[:200]}")
    how = str(said.get("bootstrap", "")).lower().replace(" ", "")
    if "webb" not in how or "impose_null=true" not in how:
        wrong.append(f"seeds.bootstrap {said.get('bootstrap')!r}")
    if sec.get("B") != {_panel_HEADLINE: _panel_B[_panel_HEADLINE], "others": _panel_B_OTHERS}:
        wrong.append(f"B {sec.get('B')!r}")
    if sorted(sec) != sorted(_panel_RECORD_KEYS) or sorted(said) != ["base", "bootstrap", "by_model_and_term"]:
        wrong.append(f"its keys are {sorted(sec)}, those of `seeds` {sorted(said)}")
    rule = str(sec.get("interval", "")).lower()             # the sentence that states the inversion: the definition's numbers and its three words
    figures = set(re.findall(r"\d+(?:\.\d+)?", rule))
    if not {"4", "10", "0.05", "16", "0.001"} <= figures or any(w not in rule for w in ("as a whole", "both ends", "outermost")):
        wrong.append(f"interval {sec.get('interval')!r}")
    check(f"{_panel_RECORD}, the section of this step ({_panel_STEP}): its `outputs` are the five files the step writes (50_gap/ " + ", ".join(_panel_STEP_WRITES)
          + f"); `gates` = the number of rows of {_panel_GATES} and `gates_passed` = the number of them with pass = yes; `seeds.base` = {_panel_BASE_SEED} and "
          f"`seeds.by_model_and_term` = for each of the 8 rows of {_panel_M}, under id:term, base + 300 + 10 x (the model's place, P1 = 0) + (the term's place); "
          f"`seeds.bootstrap` names webb weights and impose_null=True; `B` = 9999 for P1 and 1999 for the others; the section has the keys "
          + ", ".join(_panel_RECORD_KEYS) + f" and no other, and `seeds` the keys base, bootstrap and by_model_and_term (the first nine keys are read by the part 'inputs' - `run_utc` for its form only - and the two SHA-256 among them are held against the files by the part "
          f"'environment'; the last five are held here); and `interval`, a sentence of which only this is tested, gives the definition's numbers 4, 10, 0.05, 16 "
          f"and 0.001 and says 'as a whole', 'both ends' and 'outermost'", not wrong, "; ".join(wrong[:4]))


def part_panel():
    import collections

    # ------------------------------------------------------------------------------------------ the panel, recomputed
    panel, found, frozen_years = _panel_rebuild()
    for what, ok, detail in found:
        check(what, ok, detail)

    tab = _panel_table(_panel_T)
    header, ragged = _panel_header(_panel_T)
    keys = [((r.get("pc11_district_code") or ""), (r.get("fy") or "")) for r in tab]
    twice = [k for k, v in collections.Counter(keys).items() if v > 1]
    order = [(int(k[0]) if k[0].isdigit() else -1, k[1]) for k in keys]
    ok = (header == list(_panel_COLUMNS) and ragged == 0 and len(tab) == 390 and not twice and set(keys) == set(panel)
          and order == sorted(order))
    check(f"{_panel_T}: its first line is exactly the 23 columns the definition names, in the definition's order, none twice; 390 rows, each with "
          f"23 cells; one row for each of the census codes 370 to 399 and each of the 13 financial years written 2014-15 to 2026-27, none "
          f"twice; sorted by census code, then year", ok,
          "" if ok else (ragged if header is None else f"rows {len(tab)}, {ragged} of them with another number of cells than the first line; columns missing "
                         f"{sorted(set(_panel_COLUMNS) - set(header))}, not in the definition {sorted(set(header) - set(_panel_COLUMNS))}, in the definition's "
                         f"order and none twice: {header == list(_panel_COLUMNS)}; keys twice {twice[:3]}; keys missing {sorted(set(panel) - set(keys))[:3]}; "
                         f"keys not expected {sorted(set(keys) - set(panel))[:3]}; sorted: {order == sorted(order)}"))
    got = {}
    for r in tab:
        got.setdefault(((r.get("pc11_district_code") or ""), (r.get("fy") or "")), r)
    every = sorted(set(panel) | set(got))

    def compare(columns, how):
        """(key, in the table, recomputed, equal) for each column named and each district-year of either side."""
        out = []
        for k in every:
            for c in columns:
                label = f"{k[0]} {k[1]} {c}"
                if k not in panel:
                    out.append((label, got[k].get(c), "(no such district-year)", False))
                elif k not in got or got[k].get(c) is None:
                    out.append(how(label, "(no such cell)", panel[k][c])[:3] + (False,))
                else:
                    out.append(how(label, got[k][c], panel[k][c]))
        return out

    as_text = lambda label, cell, value: (label, cell, value, cell == value)

    def rounded(label, cell, value):
        if value is None:
            return (label, cell, "", cell == "")
        d, want = _panel_dec(cell), q(value, _panel_PCT)
        return (label, cell, str(want), d is not None and d == want)

    pairs = compare(("district_name", "r620_district"), as_text)
    check(f"{_panel_T}: district_name is the census name the FRA table and the decision table carry for the row's code, and r620_district "
          f"the R6.20 name the rebuilt crosswalk gives that code (text)", all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("fy_start_year", "period", "part_year", "in_models"), as_text)
    n_in = sum(1 for r in tab if r.get("in_models") == "1")
    check(f"{_panel_T}: fy_start_year is the first calendar year of fy; period is pre for FY2014-15 to 2017-18, post for FY2018-19 to "
          f"2025-26, part_year for FY2026-27; part_year is 1 for FY2026-27 alone; in_models is 1 for the other twelve years, 360 rows "
          f"(text)", all(p[3] for p in pairs) and n_in == 360,
          mismatches(pairs) or ("" if n_in == 360 else f"rows with in_models = 1: {n_in}"))

    pairs = compare(("plantation_lakh", "nrm_lakh", "water_lakh", "all_lakh"), _panel_exact)
    check(f"{_panel_T}: plantation_lakh, nrm_lakh and water_lakh equal exp_cat_lakh of the category, and all_lakh equals exp_all_lakh, "
          f"of the district-year in R6.20's district file, as numbers, exactly", all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("plantation_pct_of_all",), rounded)
    check(f"{_panel_T}: plantation_pct_of_all equals 100 x exp_cat_lakh (Plantation) / exp_all_lakh of R6.20, rounded half up to the "
          f"6 decimals the table prints", all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("plantation_works_ongoing", "plantation_works_completed"), as_text)
    check(f"{_panel_T}: plantation_works_ongoing and plantation_works_completed equal works_ongoing and works_completed of the "
          f"district-year's Plantation row in R6.20's district file (text)", all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("r620_last_updated", "frozen_2020_snapshot"), as_text)
    ok = all(p[3] for p in pairs) and frozen_years == list(range(_panel_PRE[0], _panel_PRE[1] + 1))
    check(f"{_panel_T}: r620_last_updated equals the stamp the state totals file prints for the year, and frozen_2020_snapshot is 1 "
          f"exactly where that stamp is {_panel_FROZEN}; in the state totals file those are the four pre years and no other (text)", ok,
          mismatches(pairs) or ("" if ok else f"years stamped {_panel_FROZEN} in the state totals file: {frozen_years}"))

    pairs = compare(("loss_ha_year_t_minus_1", "loss_ha_year_t"), _panel_exact)
    check(f"{_panel_T}: loss_ha_year_t_minus_1 and loss_ha_year_t equal the dense plus open loss (loss_ha_gt30_Y + loss_ha_gt10le30_Y of "
          f"the Hansen band table) of calendar years t-1 and t, t the first calendar year of the financial year, summed over the "
          f"district's units, exactly; loss_ha_year_t is blank for FY2026-27 and nowhere else", all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("loss_dense_ha_year_t_minus_1", "loss_dense_ha_year_t"), _panel_exact)
    check(f"{_panel_T}: loss_dense_ha_year_t_minus_1 and loss_dense_ha_year_t equal the dense band's loss (loss_ha_gt30_Y) of calendar "
          f"years t-1 and t summed over the district's units, exactly; the second is blank for FY2026-27 and nowhere else",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("standing_forest_ha_start_of_year_t_minus_1",), _panel_exact)
    check(f"{_panel_T}: standing_forest_ha_start_of_year_t_minus_1 equals, summed over the district's units and the two bands, the "
          f"band's land of 2000 less its loss of 2001 to t-2, not below zero for any unit and band (Hansen band table), exactly",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = [_panel_exact(f"{k[0]} {k[1]}", got[k].get("standing_forest_ha_start_of_year_t_minus_1", "") if k in got else "(no such row)",
                          panel[k]["_window_start"]) for k in sorted(panel) if panel[k]["_window_start"] is not None]
    check(f"{_panel_T}: standing_forest_ha_start_of_year_t_minus_1 of the FY2018-19, FY2019-20 and FY2022-23 rows equals the decision "
          f"table's forest_at_window_start_ha of the windows 2017_2023, 2018_2025 and 2021_2025 summed over the district's units, "
          f"exactly ({len(pairs)} district-years)", len(pairs) == 90 and all(p[3] for p in pairs), mismatches(pairs))

    pairs = compare(("loss_pct_of_standing_year_t_minus_1",), rounded)
    check(f"{_panel_T}: loss_pct_of_standing_year_t_minus_1 equals 100 x loss of year t-1 / forest standing at the start of year t-1 "
          f"(both recomputed from the Hansen band table), rounded half up to the 6 decimals the table prints",
          all(p[3] for p in pairs), mismatches(pairs))

    # ------------------------------------------------------------------------------------------ the models
    mt = _panel_table(_panel_M)
    mheader, mragged = _panel_header(_panel_M)
    want_keys = [(spec[0], j) for spec in _panel_SPECS for j in range(len(spec[2]))]
    row_of = {}
    for r in mt:
        spec = next((s for s in _panel_SPECS if s[0] == (r.get("id") or "")), None)
        if spec is not None:                                # P7's second term is the one named ..._x_post
            j = 1 if len(spec[2]) == 2 and (r.get("term") or "").endswith("_x_post") else 0
            row_of.setdefault((spec[0], j), r)
    key_text = [((r.get("id") or ""), (r.get("term") or "")) for r in mt]
    per_id = dict(collections.Counter(k[0] for k in key_text))
    ok = (mheader == list(_panel_MODEL_COLUMNS) and mragged == 0 and len(mt) == 8 and len(set(key_text)) == len(key_text)
          and all(k in row_of for k in want_keys) and per_id == {s[0]: len(s[2]) for s in _panel_SPECS})
    check(f"{_panel_M}: its first line is exactly the 29 columns the definition names, in the definition's order, none twice; 8 rows, each "
          f"with 29 cells; one row for each of P1 to P6 and two for P7 (its regressor, and the term whose name ends in _x_post: the "
          f"product with the post period); no (id, term) twice", ok,
          "" if ok else (mragged if mheader is None else f"rows {len(mt)}, {mragged} of them with another number of cells than the first line; columns "
                         f"missing {sorted(set(_panel_MODEL_COLUMNS) - set(mheader))}, not in the definition {sorted(set(mheader) - set(_panel_MODEL_COLUMNS))}, "
                         f"in the definition's order and none twice: {mheader == list(_panel_MODEL_COLUMNS)}; rows by id {per_id}; terms not found "
                         f"{[k for k in want_keys if k not in row_of]}"))

    cell = lambda r, c: "(no row)" if r is None else ("(no such cell)" if r.get(c) is None else r[c])
    near = lambda text, value, tol: _panel_float(text) is not None and value is not None and abs(_panel_float(text) - value) <= tol

    pairs = []
    for k in want_keys:
        r, label = row_of.get(k), f"{k[0]} term {k[1] + 1}"
        want = "yes" if k[0] == _panel_HEADLINE else "no"
        pairs.append((f"{label} headline", cell(r, "headline"), want, cell(r, "headline") == want))
        for c in _panel_SAME_WORDS:
            pairs.append((f"{label} {c}", cell(r, c), "(words)", r is not None and bool((r.get(c) or "").strip())))
        named = cell(r, "outcome") == "plantation_pct_of_all"
        pairs.append((f"{label} outcome", cell(r, "outcome"), "plantation_pct_of_all" if k[0] != "P3" else "another outcome: asinh(plantation_lakh)",
                      named if k[0] != "P3" else r is not None and not named))
        for c in ("outcome_unit", "coefficient_unit"):      # "P3: the coefficient is in asinh(lakh rupees) per 100 ha, not in percentage points"
            has = "asinh" in cell(r, c).lower()
            pairs.append((f"{label} {c}", cell(r, c), "names asinh" if k[0] == "P3" else "does not name asinh", has == (k[0] == "P3") and r is not None))
        unit = cell(r, "regressor_unit").lower()            # "loss / 100" for every regressor but P5's, "percentage points of standing forest"
        per_100, in_points = "100 ha" in unit, "percentage point" in unit
        pairs.append((f"{label} regressor_unit", cell(r, "regressor_unit"), "in percentage points, not per 100 ha" if k[0] == "P5" else "per 100 ha, not in percentage points",
                      r is not None and (in_points and not per_100 if k[0] == "P5" else per_100 and not in_points)))
        pairs.append((f"{label} wcb_weights", cell(r, "wcb_weights"), "webb", cell(r, "wcb_weights").strip().lower() == "webb"))
        by_period = "period" in cell(r, "spec").lower()     # "a dummy for every district in each period" for all but P2, "a dummy per district"
        pairs.append((f"{label} spec", cell(r, "spec"), "does not name a period" if k[0] == "P2" else "names the period", r is not None and by_period == (k[0] != "P2")))
        wanted_words = {"the lag t-1": k[0] != "P4", "the dense band alone": k[0] == "P6", "the standing forest": k[0] == "P5", "the post period": k == ("P7", 1)}
        for c in _panel_NAMING:
            said_words = _panel_says(cell(r, c))
            for what, yes in wanted_words.items():
                pairs.append((f"{label} {c}", cell(r, c), ("names " if yes else "does not name ") + what, r is not None and said_words[what] == yes))
    for c, wanted in _panel_SAME_WORDS.items():
        classes = _panel_classes([k for k in want_keys if k in row_of], lambda k: (row_of[k].get(c) or "").strip())
        wanted = sorted(sorted(g) for g in wanted)
        pairs.append((f"{c}: the rows that carry the same words", str(classes), str(wanted), classes == wanted))
    check(f"{_panel_M}: headline is yes for P1 and no for every other row; wcb_weights is webb; term, spec, outcome, outcome_unit, regressor, "
          f"regressor_unit and coefficient_unit are not blank. Their wording is not checked, but for this, which the definitions give: "
          f"outcome is plantation_pct_of_all for every model but P3 and is not that for P3; outcome_unit and coefficient_unit name asinh "
          f"for P3 and for no other; regressor_unit is per '100 ha' for every regressor but P5's, which is in percentage points; and "
          f"rows carry the same words exactly where the definitions make them the same: term, regressor and regressor_unit for P1, P2, "
          f"P3 and P7's first term, each of P4, P5, P6 and P7's product apart; outcome and outcome_unit for all but P3; spec for all "
          f"but P2; coefficient_unit for P1, P2 and P7's first term, each of the others apart. And, so that two rows cannot exchange "
          f"their words unseen, the words that tell one model from another are in the rows the definitions give them to and in no "
          f"other: spec names a 'period' for every model but P2 and not for P2; each of term, regressor, regressor_unit and coefficient_unit "
          f"names the lag (written t-1, t - 1, t_minus_1 or t minus 1) in every row but P4's, the dense band without the open one ('dense', no 'open') in P6's "
          f"alone, the standing forest ('standing') in P5's alone, and the post period ('post') in the row of P7's product alone",
          all(p[3] for p in pairs), mismatches(pairs))

    grids, grids_error = {}, ""
    try:
        with open(GAP / _panel_GRIDS, encoding="utf-8") as f:
            grids = json.load(f)
        if not isinstance(grids, dict):
            raise ValueError("not a set of grids by model and term")
    except Exception as e:
        grids, grids_error = {}, f"{type(e).__name__}: {e}"
    grid_names = [f"{k[0]}:{row_of[k].get('term') or ''}" for k in want_keys if k in row_of]
    odd = []
    for name in sorted(set(grids) | set(grid_names)):
        g = grids.get(name)
        if name not in grid_names:
            odd.append(f"{name}: not a row of {_panel_M}")
        elif not isinstance(g, dict) or sorted(g) != sorted(_panel_GRID_KEYS):
            odd.append(f"{name}: " + (f"its keys are {sorted(g)}" if isinstance(g, dict) else "no such entry"))
        elif not isinstance(g["grid"], dict) or sorted(g["grid"]) != ["hi", "lo"]:
            odd.append(f"{name}: the sides of its grid are {sorted(g['grid']) if isinstance(g['grid'], dict) else g['grid']!r}")
        else:
            for side in ("lo", "hi"):
                pts = g["grid"][side]
                if not isinstance(pts, list) or len(pts) != _panel_STEPS + 1 or any(
                        not isinstance(pt, dict) or sorted(pt) != ["b0", "p"] or not _panel_number(pt["b0"]) or not _panel_number(pt["p"]) for pt in pts):
                    odd.append(f"{name} {side}: not {_panel_STEPS + 1} points of b0 and p, numbers")
    check(f"{_panel_GRIDS}: can be read; it has one entry for each of the 8 rows of {_panel_M}, named id:term, and no other; every entry has "
          f"the keys {', '.join(_panel_GRID_KEYS)} and no other (so that none goes unread here); every grid has the sides lo and hi, each "
          f"of 17 points, each point a b0 and a p, numbers", not grids_error and len(grid_names) == 8 and not odd, grids_error or "; ".join(odd[:4]))

    webb = np.array([-math.sqrt(1.5), -1.0, -math.sqrt(0.5), math.sqrt(0.5), 1.0, math.sqrt(1.5)])
    level = _panel_LEVEL
    counts, coefs, ses, seeds, own_zero, own_ends, own_mids, arith_zero = [], [], [], [], [], [], [], []
    pkg_zero, pkg_ends, pkg_brackets, described, kept_points, kept_heads, made, bisected, middles, doubling = [], [], [], [], [], [], [], [], [], []
    seen = {"zero": [], "ends": [], "mids": [], "in": [], "out": [], "middle": []}
    fits, terms, seeds_wanted, doublings = [], [], {}, []
    for k, spec in enumerate(_panel_SPECS):
        mid = spec[0]
        y, X, names, cl, G = _panel_design(panel, spec)
        n, K = X.shape
        beta, se, rank = _panel_ols_cr1(y, X, cl, G)
        fits.append((n, G, rank == K))
        W = webb[np.random.default_rng(_panel_OWN_SEED).integers(0, 6, size=(G, _panel_OWN_DRAWS))]    # this part's own draws
        B = _panel_B.get(mid, _panel_B_OTHERS)             # the definition's B and seed: the table must carry them
        for j in range(len(spec[2])):
            r = row_of.get((mid, j))
            label = f"{mid} {r.get('term') or ''}" if r is not None else f"{mid} term {j + 1}"
            seed = _panel_BASE_SEED + 300 + 10 * k + j
            if r is not None:
                seeds_wanted[f"{mid}:{r.get('term') or ''}"] = seed
            b, s = float(beta[j]), float(se[j])

            # the sample, the coefficient, its CR1 standard error; B and the seed
            for c, value in (("n", n), ("clusters", G), ("n_parameters", K)):
                counts.append((f"{label} {c}", cell(r, c), str(value), cell(r, c) == str(value)))
            counts.append((f"{label} rank of the design", str(rank), str(K), rank == K))
            coefs.append((label, cell(r, "coefficient"), f"{b:.10f}", near(cell(r, "coefficient"), b, _panel_COEF_TOL)))
            ses.append((f"{label} se_cr1", cell(r, "se_cr1"), f"{s:.10f}", near(cell(r, "se_cr1"), s, _panel_COEF_TOL)))
            ses.append((f"{label} t_cr1", cell(r, "t_cr1"), f"{b / s:.8f}", near(cell(r, "t_cr1"), b / s, _panel_T_TOL)))
            seeds.append((f"{label} wcb_B", cell(r, "wcb_B"), str(B), cell(r, "wcb_B") == str(B)))
            seeds.append((f"{label} wcb_seed", cell(r, "wcb_seed"), str(seed), cell(r, "wcb_seed") == str(seed)))

            # this part's own bootstrap arithmetic, given the weights the package draws from the seed: the builder's p at any b0
            V = _panel_pkg_weights(G, B, seed)
            known = {}

            def P(b0, y=y, X=X, cl=cl, G=G, j=j, V=V, known=known):
                if b0 not in known:
                    known[b0] = _panel_own_p(y, X, cl, G, j, b0, V)
                return known[b0]

            # the whole inversion by that arithmetic: the bracket (one d for both sides), the grid, the bisection
            d, sides, asked, tried = _panel_invert(P, b, s)
            doublings.append(d)
            terms.append((not sides["lo"]["unbounded"] and not sides["hi"]["unbounded"],
                          all(sides[x]["crossings"] == 1 and not sides[x]["rises"] for x in ("lo", "hi"))))
            g = grids.get(f"{mid}:{r.get('term') or ''}") if r is not None else None
            g = g if isinstance(g, dict) else {}

            # H0: beta = 0, by this part's own draws; by its own arithmetic with the package's weights; and by the package
            p_own = _panel_own_p(y, X, cl, G, j, 0.0, W)
            tol_zero = min(_panel_P_TOL, _panel_SDS * _panel_sd((p_own * _panel_OWN_DRAWS + 1) / (_panel_OWN_DRAWS + 2), B))
            seen["zero"].append(abs(p_own - (_panel_float(cell(r, "wcb_p")) or 0.0)) / tol_zero)
            own_zero.append((label, cell(r, "wcb_p"), f"{p_own:.4f}, to within {tol_zero:.4f}", near(cell(r, "wcb_p"), p_own, tol_zero)))
            arith_zero.append((label, cell(r, "wcb_p"), repr(P(0.0)), near(cell(r, "wcb_p"), P(0.0), _panel_SAME)))
            p_pkg = _panel_pkg_p(y, X, names, cl, j, 0.0, B, seed)
            pkg_zero.append((label, cell(r, "wcb_p"), repr(p_pkg), near(cell(r, "wcb_p"), p_pkg, _panel_SAME)))

            # the entry of the kept grids for this term: what it says of the run, and how many tests it counts
            for c, value in (("B", B), ("seed", seed)):
                kept_heads.append((f"{label} {c}", repr(g.get(c)), str(value), _panel_number(g.get(c)) and g.get(c) == value))
            for c, value in (("estimate", b), ("se_cr1", s)):
                kept_heads.append((f"{label} {c}", repr(g.get(c)), repr(value), _panel_number(g.get(c)) and abs(g.get(c) - value) <= _panel_FLOAT))
            nulls = len({round((x - b) / s, 9) for x in asked + [0.0]})
            made.append((label, repr(g.get("tests_made")), str(nulls), _panel_number(g.get("tests_made")) and g.get("tests_made") == nulls))

            far = lambda sign, kk: b + sign * _panel_FIRST_REACH * 2 ** kk * s
            for side, sign in (("lo", -1.0), ("hi", 1.0)):
                tag = f"{label} {side}"
                own = sides[side]
                end_text = cell(r, f"wcb_ci95_{side}")
                end = _panel_float(end_text)

                # the columns that say how p behaved along the bracket, from this part's own grid
                for c, value in (("wcb_unbounded", "yes" if own["unbounded"] else "no"), ("wcb_crossings", str(own["crossings"])),
                                 ("wcb_p_rises_again", "yes" if own["rises"] else "no")):
                    described.append((f"{tag} {c}", cell(r, f"{c}_{side}"), value, cell(r, f"{c}_{side}") == value))
                described.append(_panel_exact(f"{tag} wcb_p_at_bracket_end", cell(r, f"wcb_p_at_bracket_end_{side}"), q(D(repr(own["p"][-1])), _panel_PCT)))

                # the end of the interval
                if own["unbounded"]:                        # no end to give: the cell is to be blank
                    for held in (own_ends, pkg_ends, bisected, middles):
                        held.append((tag, end_text, "blank: this part's own inversion finds the side unbounded", end_text == ""))
                elif end is None:
                    for held in (own_ends, own_mids, pkg_ends, bisected, middles):
                        held.append((tag, end_text, "an end of the interval", False))
                else:
                    p_end = _panel_own_p(y, X, cl, G, j, end, W)
                    tol_end = _panel_SDS * _panel_sd(level, B)
                    seen["ends"].append((p_end - level) / tol_end)
                    own_ends.append((tag, end_text, f"own p there {p_end:.4f}, to be within {tol_end:.4f} of {level}; coefficient {b:.6f}",
                                     (end - b) * sign > 0 and abs(p_end - level) <= tol_end))
                    p_mid = _panel_own_p(y, X, cl, G, j, (b + end) / 2, W)
                    seen["mids"].append(p_mid)
                    own_mids.append((tag, end_text, f"own p at the midpoint {p_mid:.4f}", p_mid > level))
                    p_in = _panel_pkg_p(y, X, names, cl, j, end - sign * _panel_NUDGE * s, B, seed)
                    p_out = _panel_pkg_p(y, X, names, cl, j, end + sign * _panel_NUDGE * s, B, seed)
                    seen["in"].append(p_in)
                    seen["out"].append(p_out)
                    pkg_ends.append((tag, end_text, f"package p inside {p_in!r}, outside {p_out!r}",
                                     p_in is not None and p_out is not None and p_in >= level and p_out < level))
                    inner, outer = own["bracket"]
                    seen["middle"].append(abs(end - (inner + outer) / 2) / s)
                    bisected.append((tag, end_text, f"between {inner:.8f} and {outer:.8f}", min(inner, outer) <= end <= max(inner, outer)))
                    middles.append((tag, end_text, f"{(inner + outer) / 2:.10f}", near(end_text, (inner + outer) / 2, _panel_COEF_TOL)))

                # the grid the builder kept for this side, against this part's own: where it ends, and every point of it
                try:
                    pts = [(float(pt["b0"]), float(pt["p"])) for pt in g["grid"][side]]
                except Exception:
                    pts = []
                reach = (pts[-1][0] - b) * sign / (_panel_FIRST_REACH * s) if pts else 0.0     # in first brackets of 4 se_cr1
                kd = round(math.log2(reach)) if reach > 0 else None
                on_a_doubling = kd is not None and abs(reach - 2 ** kd) <= _panel_SAME * 2 ** kd
                doubling.append((tag, "no such grid" if not pts else (f"the kept grid ends at 4 x 2^{kd} se_cr1" if on_a_doubling else
                                                                     f"the kept grid ends {reach * _panel_FIRST_REACH:.6f} se_cr1 from the coefficient"),
                                 f"4 x 2^{d} se_cr1; own p at the lower and the upper end of each bracket tried: "
                                 + "; ".join(f"4 x 2^{i}: {lo_p:.6f} and {hi_p:.6f}" for i, (lo_p, hi_p) in enumerate(tried)), on_a_doubling and kd == d))
                if len(pts) != _panel_STEPS + 1:
                    kept_points.append((tag, f"{len(pts)} points", f"{_panel_STEPS + 1} points", False))
                else:
                    for i, (b0, p_kept) in enumerate(pts):
                        kept_points.append((f"{tag} point {i}", f"b0 {b0!r}, p {p_kept!r}", f"b0 {own['b0'][i]!r}, p {own['p'][i]!r}",
                                            abs(b0 - own["b0"][i]) <= _panel_SAME * s and abs(p_kept - own["p"][i]) <= _panel_SAME))

                # the package's p at the end of the bracket; and, where the bracket was doubled, at the end it had before
                for kk in ([d - 1] if d >= 1 else []) + [d]:
                    p_far = _panel_pkg_p(y, X, names, cl, j, far(sign, kk), B, seed)
                    pkg_brackets.append((f"{tag}, coefficient -/+ 4 x 2^{kk} se_cr1", f"package {p_far!r}", f"own {P(far(sign, kk))!r}",
                                         p_far is not None and abs(p_far - P(far(sign, kk))) <= _panel_SAME))

    span = lambda v: f"{min(v):.4f} to {max(v):.4f}" if v else "none"
    check(f"{_panel_M}: n, clusters and n_parameters equal the district-years, districts and columns of the design rebuilt from the "
          f"recomputed panel (the regressor(s), then every dummy, no constant; complete cases of the rows with in_models = 1, so "
          f"FY2026-27 is in none), and that design has full column rank", all(p[3] for p in counts), mismatches(counts))
    check(f"{_panel_M}: coefficient equals the least-squares coefficient (numpy lstsq) on the rebuilt design, to the eight decimals "
          f"the table prints (|difference| <= 5.1e-9)", all(p[3] for p in coefs), mismatches(coefs))
    check(f"{_panel_M}: se_cr1 equals the cluster sandwich by district times G/(G-1) x (N-1)/(N-K), computed here in numpy, to the "
          f"eight decimals the table prints (|difference| <= 5.1e-9); t_cr1 equals the recomputed coefficient over that standard "
          f"error, to the six decimals it prints (|difference| <= 5.001e-7)", all(p[3] for p in ses), mismatches(ses))
    check(f"{_panel_M}: wcb_B is 9999 for P1 and 1999 for the others; wcb_seed is 20261010 + 300 + 10 x (the model's place, P1 = 0) + "
          f"(the term's place, 0 or 1)", all(p[3] for p in seeds), mismatches(seeds))
    check(f"{_panel_M}: wcb_p against this part's own restricted wild cluster bootstrap-t of H0: beta = 0 (Webb weights, the null "
          f"imposed, {_panel_OWN_DRAWS} draws of its own): |difference| <= {_panel_SDS} standard errors of the difference between two such p's "
          f"from different draws, sqrt(p(1-p)(1/wcb_B + 1/{_panel_OWN_DRAWS})) with p this part's own, and never more than {_panel_P_TOL}",
          all(p[3] for p in own_zero), mismatches(own_zero) or f"largest |difference|, as a share of what is allowed: {max(seen['zero']):.2f}")
    check(f"{_panel_M}: wcb_p equals the p of this part's own bootstrap arithmetic at H0: beta = 0 when it is given the Webb weights "
          f"the package draws from the definition's seed (wcb_B draws), to 1e-9", all(p[3] for p in arith_zero), mismatches(arith_zero))
    check(f"{_panel_M}: wcb_p equals the wildboottest package's p of H0: beta = 0 on the rebuilt design with the definition's B and "
          f"seed (Webb weights, the null imposed), to 1e-9", all(p[3] for p in pkg_zero), mismatches(pkg_zero))
    check(f"{_panel_M}: wcb_ci95_lo is below and wcb_ci95_hi above the recomputed coefficient, and with this part's own draws the "
          f"bootstrap p of H0: beta = that end is within {_panel_SDS} standard errors of 0.05, sqrt(0.05 x 0.95 x (1/wcb_B + 1/{_panel_OWN_DRAWS})): "
          f"within {_panel_SDS * _panel_sd(level, _panel_B[_panel_HEADLINE]):.4f} for P1 and {_panel_SDS * _panel_sd(level, _panel_B_OTHERS):.4f} for the others "
          f"(different draws); an end is blank only on a side this part's own inversion finds unbounded", len(own_ends) == 16 and all(p[3] for p in own_ends),
          mismatches(own_ends) or f"own p at the {len(seen['ends'])} ends, less 0.05, as a share of what is allowed: {span(seen['ends'])}")
    check(f"{_panel_M}: with this part's own draws the bootstrap p is above 0.05 at the midpoint between the recomputed coefficient "
          f"and each end of the interval", all(p[3] for p in own_mids),
          mismatches(own_mids) or f"own p at the {len(seen['mids'])} midpoints: {span(seen['mids'])}")
    check(f"{_panel_M}: with the package and the same B and seed, refitting with y - b0 x: p is at least 0.05 at {_panel_NUDGE} se_cr1 "
          f"inside each end of the interval (towards the coefficient) and below 0.05 at {_panel_NUDGE} se_cr1 outside it",
          len(pkg_ends) == 16 and all(p[3] for p in pkg_ends), mismatches(pkg_ends) or f"p inside: {span(seen['in'])}; p outside: {span(seen['out'])}")
    check(f"{_panel_M}: wcb_ci95_lo and wcb_ci95_hi lie inside the bracket this part's own inversion reaches from the inputs: p by its "
          f"own bootstrap arithmetic with the package's weights for the seed; the bracket of 4 x 2^d se_cr1 found as the definition "
          f"says; the outermost of its 16 steps in which p crosses 0.05 halved until no wider than {_panel_BISECT_TO} se_cr1",
          len(bisected) == 16 and all(p[3] for p in bisected),
          mismatches(bisected) or f"{len(bisected)} ends; the farthest from the middle of its bracket: {max(seen['middle'] or [0]):.6f} se_cr1")
    check(f"{_panel_M}: wcb_ci95_lo and wcb_ci95_hi equal the middle of that bracket, to the eight decimals the table prints "
          f"(|difference| <= 5.1e-9). The definition does not say which point of the last bracket is given, nor whether 'to 0.001' is "
          f"its width or half of it: the middle of a bracket no wider than 0.001 se_cr1 is read here, and held so that a changed digit "
          f"of an end shows", len(middles) == 16 and all(p[3] for p in middles), mismatches(middles))
    check(f"{_panel_M}: wcb_unbounded_*, wcb_crossings_*, wcb_p_rises_again_* and wcb_p_at_bracket_end_* (6 decimals, exactly) equal what "
          f"the definition gives on the grid of this part's own inversion: unbounded where p at the end of the bracket is not below "
          f"0.05, the number of the 16 steps in which p crosses 0.05, whether p, going outward, climbs more than 0.01 above a value it "
          f"had fallen to, and p at the end of the bracket", len(described) == 64 and all(p[3] for p in described), mismatches(described))
    check(f"{_panel_GRIDS}: the bracket is doubled as a whole: for every term, both sides of the kept grid end at the coefficient -/+ "
          f"4 x 2^d se_cr1 (to 1e-9 of that reach) for ONE d, the smallest of 0 to 10 at which p is below 0.05 at BOTH ends, or 10; p by "
          f"this part's own bootstrap arithmetic with the package's weights for the seed",
          len(doubling) == 16 and all(p[3] for p in doubling), mismatches(doubling) or "d of the 8 terms: " + ", ".join(str(x) for x in doublings))
    check(f"{_panel_GRIDS}: every point of every kept grid (8 terms x 2 sides x 17 points) is the point of this part's own grid: b0 is "
          f"the coefficient plus the same sixteenth of the way to the end of the bracket (to 1e-9 se_cr1) and p is the p of this part's "
          f"own bootstrap arithmetic there with the Webb weights the package draws from the seed (to 1e-9)",
          len(kept_points) == 272 and all(p[3] for p in kept_points), mismatches(kept_points))
    check(f"{_panel_GRIDS}: each entry carries the definition's B and seed for its term, and its estimate and se_cr1 are the recomputed "
          f"coefficient and CR1 standard error (|difference| <= 1e-10)", len(kept_heads) == 32 and all(p[3] for p in kept_heads), mismatches(kept_heads))
    check(f"{_panel_GRIDS}: tests_made. The definitions do not say what it counts; it is read here as the number of different nulls at "
          f"which the definition's procedure reads a p (H0: beta = 0; the two ends of every bracket tried; the 17 points of each side, "
          f"the coefficient once; the points of the two bisections), counted on this part's own inversion",
          len(made) == 8 and all(p[3] for p in made), mismatches(made))
    check(f"the ground under the checks of {_panel_GRIDS} (this check reads no cell of a table and cannot fail on an error in one): the package's p, with the same B and seed, at the two ends of each term's bracket (the "
          f"coefficient -/+ 4 x 2^d se_cr1, d this part's own) equals this part's own p there, to 1e-9: the p the grids and "
          f"wcb_p_at_bracket_end_* are held to; and so does the package's p at the two ends of the bracket before the last doubling, where "
          f"there was one, at one of which it is therefore not below 0.05",
          len(pkg_brackets) == 16 + 2 * sum(1 for x in doublings if x >= 1) and all(p[3] for p in pkg_brackets),
          mismatches(pkg_brackets) or f"{len(pkg_brackets)} values of p compared")

    # ------------------------------------------------------------------------------------------ what the step says of itself
    _panel_step_checks(panel, fits, terms, seeds_wanted)

# ---- part: units ---- unit_history.csv, unit_history_models.csv, unit_history_models_wcb_grids.json and gates_phase4.csv, each recomputed from the inputs ----
# Written from the definitions in the docstring of the builder of these tables and of the shared routines, not from
# their code. Nothing here reads unit_district.csv: the district of a unit is rebuilt from 10_units/. Nothing of 50_gap/
# is taken as given: the districts C7 leaves out are rebuilt from the decision table and the agreement table by the rule
# the definitions give, and district_need.csv is read only to hold the sentence that the unit table's flag is that
# table's column. The inversion of the bootstrap test (the bracket, the grid of p values, the bisection) is redone from
# the rule as it stands - one bracket for both sides of a model, doubled as a whole - with this part's own bootstrap
# arithmetic and the weights the recorded seed draws; the table and the saved grid are then held to that.
# A regression here reads each variable as the unit table prints it (a share to six decimals, the logarithm and the
# asinh to ten). The definition does not say whether a model reads its columns as printed or before they are rounded;
# the two fits differ by up to 2.3e-8 in a coefficient. The fit on the values before rounding is held to the table as
# well, to 1e-6.
# The step's own account of itself is held too: gates_phase4.csv row by row (each gate recomputed from its own label, the
# definitions naming the table and not its rows) and, of its section of gap.provenance.json, the seeds, the draws and the
# count of gates. Two things the definitions leave open are read as follows, and the checks say so: which point of the
# last bracket of a bisection is reported as the interval's end (none is preferred: all ends must sit at the same one of
# its inner end, its middle and its outer end), and what tests_made counts (the different b0 at which the rule reads a p).
_units_UNITS = "10_units/units.gpkg"
_units_OUTSIDE = "10_units/outside_village_district.csv"
_units_FRA = "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"
_units_DECISION = "55_decision/condition_by_unit.csv"
_units_TIERS = "55_decision/tiers.csv"
_units_HANSEN = "20_degradation/hansen_loss_by_canopy_band_by_unit.csv"
_units_AGREEMENT = "20_degradation/agreement_by_unit.csv"
_units_NEED = "30_need/need_by_unit.csv"
_units_CORESTACK = "20_degradation/corestack_by_unit.csv"
_units_ALLOCATION = "40_allocation/allocation_by_unit_fy.csv"
_units_GRIDS = "unit_history_models_wcb_grids.json"
_units_GATES, _units_PROVENANCE, _units_STEP = "gates_phase4.csv", "gap.provenance.json", "08_build_gap_units"
_units_STEP2_SUM = ("district_allocation.csv", "dump_forest_named_started_by_fy2017_18_inr")     # "step 2's sum over districts" of a gate
_units_LGD, _units_OUT = "lgd_panchayat", "outside_village"
_units_PRIOR_YEARS = range(2001, 2018)                      # the calendar years before the default window, 2018 to 2025
_units_LAST_START = 2017                                    # "started by FY2017-18": fy_work_start of 2017-18 or earlier
_units_LOSS_CELLS = ("open_loss", "dense_loss", "little_loss")       # the three "loss recorded" cells: N1 is the loss in their units
_units_ZONES = ("ECPHR only", "EPAHR only", "both models", "")       # corestack_zone_model as the agreement table writes it
_units_EAST_COAST = "ECPHR only"                            # the units C7's rule counts: the east-coast model alone
_units_KEY = ("unit_id", "unit_level", "outside_village", "pc11_district_code", "district_name")
_units_SAMPLE_FLAGS = tuple(f"in_h{k}" for k in range(1, 10))
_units_COLUMNS = _units_KEY + (
    "forest_2000_ha", "forest_at_window_start_ha", "dense_at_window_start_ha", "dense_share_of_forest_at_start_pct",
    "loss_2001_2017_ha", "prior_loss_share_pct", "log_forest_at_start", "forest_loss_share_pct", "loss_recorded",
    "forest_named_by_fy2017_18_inr", "e1_any_forest_named", "e2_asinh_forest_named_inr_per_ha",
    "plantation_category_by_fy2017_18_inr", "e3_any_plantation_category", "st_share_pct", "adi_2011",
    "corestack_degradation_ha_tc_gt10", "corestack_improvement_ha_tc_gt10", "downward_share_pct",
    "in_district_left_out_of_c7") + _units_SAMPLE_FLAGS
_units_MODEL_COLUMNS = (
    "id", "headline", "sample", "outcome", "outcome_unit", "exposure", "exposure_unit", "coefficient_unit", "controls",
    "n_units", "n_exposed", "n_districts", "n_parameters", "coefficient", "se_cr1", "t_cr1", "wcb_ci95_lo", "wcb_ci95_hi",
    "wcb_unbounded_lo", "wcb_unbounded_hi", "wcb_crossings_lo", "wcb_crossings_hi", "wcb_p_rises_again_lo",
    "wcb_p_rises_again_hi", "wcb_p_at_bracket_end_lo", "wcb_p_at_bracket_end_hi", "wcb_p", "wcb_B", "wcb_seed", "wcb_weights")
_units_CONTROLS = ("log_forest_at_start", "dense_share_of_forest_at_start_pct", "prior_loss_share_pct", "outside_village")
_units_CONTROLS_H5 = _units_CONTROLS[:3] + ("st_share_pct", "adi_2011")
_units_NOT_C7, _units_LGD_ONLY, _units_OF_H1 = "outside the districts C7 leaves out", "LGD panchayat units only", "units of H1's sample"
# id: outcome, exposure, floor in hectares of forest at the start of 2018, restriction, controls. The order is the table's.
_units_MODELS = {
    "H1": ("forest_loss_share_pct", "e1_any_forest_named", "100", "", _units_CONTROLS),
    "H2": ("forest_loss_share_pct", "e1_any_forest_named", "50", "", _units_CONTROLS),
    "H3": ("forest_loss_share_pct", "e1_any_forest_named", "10", "", _units_CONTROLS),
    "H4": ("forest_loss_share_pct", "e1_any_forest_named", "100", _units_NOT_C7, _units_CONTROLS),
    "H5": ("forest_loss_share_pct", "e1_any_forest_named", "100", _units_LGD_ONLY, _units_CONTROLS_H5),
    "H6": ("forest_loss_share_pct", "e2_asinh_forest_named_inr_per_ha", "100", "", _units_CONTROLS),
    "H7": ("forest_loss_share_pct", "e3_any_plantation_category", "100", "", _units_CONTROLS),
    "H8": ("loss_recorded", "e1_any_forest_named", "100", "", _units_CONTROLS),
    "H9": ("downward_share_pct", "e1_any_forest_named", "100", _units_OF_H1, _units_CONTROLS),
}
_units_VARIABLES = tuple(dict.fromkeys(v for m in _units_MODELS.values() for v in (m[0], m[1]) + m[4]))   # every variable a model reads
# variable: (the definitions' word for it, one of which its unit must use; the words of the other outcomes or exposures, which it must not)
_units_WORDS = {"forest_loss_share_pct": (("percentage", "per cent"), ("probability", "downward")),
                "loss_recorded": (("probability",), ("downward",)),
                "downward_share_pct": (("downward",), ("probability",)),
                "e1_any_forest_named": (("forest-named",), ("asinh", "plantation")),
                "e2_asinh_forest_named_inr_per_ha": (("asinh",), ("plantation",)),
                "e3_any_plantation_category": (("plantation",), ("forest-named", "asinh"))}
_units_SEED_BASE = 20261010                                 # unit model k (H1..H9 -> 0..8) takes the seed base + 500 + k
_units_B_HEADLINE, _units_B_OTHERS = 9999, 1999             # draws of the builder's bootstrap: H1, and the other eight
_units_LEVEL = 0.05
_units_BRACKET_SE, _units_GRID_STEPS, _units_MAX_DOUBLINGS, _units_BISECT_SE = 4, 16, 10, 0.001      # the owner's rule of the interval
_units_OWN_DRAWS, _units_OWN_SEED = 99999, 7410             # this part's own bootstrap: its own draws, not the builder's
_units_NEAR_END = 0.002                                     # "just inside" and "just outside" an end, in CR1 standard errors
_units_POINTS = ("the inner end", "the middle", "the outer end")     # the points of its last bracket that a bisection can report
_units_TOL10, _units_TOL8, _units_TOL6 = 5.1e-11, 5.1e-9, 5.1e-7     # half a unit of the 10th, 8th and 6th decimal, and a little


def _units_dec(text):
    """A cell as an exact number; None where it is blank or is not a number."""
    try:
        return D(text) if str(text).strip() != "" else None
    except Exception:
        return None


def _units_float(text):
    """A cell as a float; None where it is blank or is not a finite number."""
    try:
        v = float(text)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def _units_same_number(cell, value):
    """A cell of the table equals a recomputed exact number (12.5 equals 12.50); a blank equals only a blank (None)."""
    if value is None:
        return cell == ""
    got = _units_dec(cell)
    return got is not None and got == value


def _units_near(cell, value, tol):
    """A cell of the table is within tol of a recomputed float; a blank equals only a blank (None)."""
    if value is None:
        return cell == ""
    got = _units_float(cell)
    return got is not None and math.isfinite(value) and abs(got - value) <= tol


def _units_pct(num, den):
    """100 x num / den rounded half up to six decimals; None (a blank) where den is zero."""
    return None if den == 0 else q(D(100) * num / den, "0.000001")


def _units_show(v):
    """A recomputed value as it is set beside the table's cell in a check's detail."""
    return "" if v is None else format(v, "f") if isinstance(v, Decimal) else repr(v) if isinstance(v, float) else str(v)


def _units_header(name):
    """The column names of a table of the folder being checked, as its first line writes them."""
    with open(GAP / name, encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def _units_settle(what, pairs, limit=3):
    """One check from (key, the table's cell, recomputed, whether they agree): it holds if there is a pair and every pair
    agrees. Its detail shows the first `limit` that do not."""
    pairs = [(k, a, _units_show(b), ok) for k, a, b, ok in pairs]
    check(what, bool(pairs) and all(p[3] for p in pairs), mismatches(pairs, limit) if pairs else "nothing to compare")


def _units_hold(what, claims, limit=9):
    """One check from (key, what was found, whether it is as it should be): it holds if there is a claim and every claim
    does. Its detail shows the first `limit` that do not."""
    bad = [f"{k}: {found}" for k, found, ok in claims if not ok]
    check(what, bool(claims) and not bad, "nothing to test" if not claims else "" if not bad else f"{len(bad)} fail, e.g. " + "; ".join(bad[:limit]))


def _units_recompute():
    """Every column of unit_history.csv for every unit, from the inputs: ({unit id: record}, the ids in the table's order,
    what is wrong with the inputs, {district code: what C7's rule makes of it}). A record holds, under each column's name,
    what the table should print: text for the words and the 1/0 flags, an exact Decimal for hectares, rupees and shares
    (the shares rounded half up to six decimals), a float for the logarithm and the asinh, None for a blank. Under `x` it
    holds the float a regression reads for each variable, which is the column as the table prints it (the logarithm and
    the asinh to ten decimals; nan for a blank); under `raw` the same before any rounding. For a district the last holds
    `n1` (its N1 of 2018_2025), `east` (the part of it in units under the east-coast model alone), `share` (the second
    as a per cent of the first, None where N1 is zero) and `left_out` (yes where that share is above 50, else no)."""
    import pyogrio
    wrong, nan = [], float("nan")
    name_of = {}
    for r in rows(_units_FRA):
        name_of.setdefault(r["pc11_district_code"].strip(), set()).add(r["district"].strip())
    assigned = {}
    for r in rows(_units_OUTSIDE):
        assigned.setdefault(r["unit_id"].strip(), []).append(r["pc11_district_code"].strip())
    layer = pyogrio.read_dataframe(ROOT / _units_UNITS, read_geometry=False)
    units = {}
    for uid, level, flag, code in zip(layer["unit_id"], layer["unit_level"], layer["outside_village"], layer["pc11_district_code"]):
        uid, level, flag = str(uid).strip(), str(level).strip(), str(int(flag))
        code = "" if code is None or code != code else str(code).strip()
        if uid in units:
            wrong.append(f"{uid} is twice in units.gpkg")
        if (level, flag) not in ((_units_LGD, "0"), (_units_OUT, "1")):
            wrong.append(f"{uid}: unit_level {level!r} with outside_village {flag!r}")
        if level == _units_OUT:                             # the code assigned to it in outside_village_district.csv
            got = assigned.get(uid, [])
            code = got[0] if len(got) == 1 else ""
        if len(name_of.get(code, ())) != 1:
            wrong.append(f"{uid}: not one district with one name (code {code!r})")
        units[uid] = {"unit_id": uid, "unit_level": level, "outside_village": flag, "pc11_district_code": code,
                      "district_name": "; ".join(sorted(name_of.get(code, ())))}
    if len(units) != 11468 or len(name_of) != 30 or any(len(v) != 1 for v in name_of.values()):
        wrong.append(f"units.gpkg has {len(units)} units; the FRA table has {len(name_of)} district codes, "
                     f"{sum(len(v) != 1 for v in name_of.values())} of them with more than one name")
    extra = sorted(set(assigned) - {uid for uid, u in units.items() if u["unit_level"] == _units_OUT})
    if extra:
        wrong.append(f"{len(extra)} units of outside_village_district.csv are not outside-village units of units.gpkg, e.g. {extra[:3]}")

    def by_unit(path):
        out = {}
        for r in rows(path):
            if r["unit_id"].strip() in out:
                wrong.append(f"{r['unit_id']} is twice in {path}")
            out[r["unit_id"].strip()] = r
        if set(out) != set(units):
            wrong.append(f"{path} does not carry the units of units.gpkg: {len(set(out) ^ set(units))} ids differ")
        return out

    decision, hansen, need, corestack = by_unit(_units_DECISION), by_unit(_units_HANSEN), by_unit(_units_NEED), by_unit(_units_CORESTACK)
    agreement = by_unit(_units_AGREEMENT)
    started = {}                                            # unit: [forest-named rupees, plantation-category rupees] of works started by FY2017-18
    for r in rows(_units_ALLOCATION):
        uid, fy = r["unit_id"].strip(), r["fy_work_start"].strip()
        if uid not in units:
            wrong.append(f"allocation_by_unit_fy.csv has a unit that units.gpkg has not: {uid}")
            continue
        if fy == "NA":                                      # no usable start date: counts as not started by FY2017-18
            continue
        if not (len(fy) == 7 and fy[:4].isdigit() and fy[4] == "-" and fy[5:].isdigit() and int(fy[5:]) == (int(fy[:4]) + 1) % 100):
            wrong.append(f"allocation_by_unit_fy.csv: fy_work_start {fy!r} is neither NA nor a financial year written like 2017-18")
            continue
        if int(fy[:4]) <= _units_LAST_START:
            both = started.setdefault(uid, [D(0), D(0)])
            for k, col in enumerate(("expenditure_forest_named_worktype", "expenditure_plantation_category")):
                if r[col].strip() != "":                    # a blank money cell (works, none with expenditure reported) adds nothing
                    both[k] += D(r[col])

    # the districts C7 leaves out, by its rule: more than half of the district's N1 lies in units under the east-coast model alone
    with_loss = sorted(r["cell"].strip() for r in rows(_units_TIERS) if r["loss_column"].strip() == "some")
    if with_loss != sorted(_units_LOSS_CELLS):
        wrong.append(f"the cells of tiers.csv whose loss_column is 'some' are {with_loss}, not the three loss cells of the definitions")
    cells = {r["cell"].strip() for r in rows(_units_TIERS)}
    c7 = {code: {"n1": D(0), "east": D(0)} for code in name_of}
    for uid, u in units.items():
        if uid not in decision or uid not in agreement or u["pc11_district_code"] not in c7:
            continue
        cell, zone = decision[uid]["cell_2018_2025"].strip(), agreement[uid]["corestack_zone_model"].strip()
        if cell not in cells or zone not in _units_ZONES:
            wrong.append(f"{uid}: cell_2018_2025 {cell!r} is not a cell of tiers.csv, or corestack_zone_model {zone!r} is not one of {_units_ZONES}")
        if cell in _units_LOSS_CELLS:
            lost = D(decision[uid]["forest_loss_ha_2018_2025"])
            c7[u["pc11_district_code"]]["n1"] += lost
            if zone == _units_EAST_COAST:
                c7[u["pc11_district_code"]]["east"] += lost
    for code, v in c7.items():
        v["share"] = None if v["n1"] == 0 else D(100) * v["east"] / v["n1"]
        v["left_out"] = "yes" if v["share"] is not None and v["share"] > 50 else "no"      # a district with no N1 stays in
        if v["share"] is not None and abs(v["share"] - 50) <= D("0.000001"):
            wrong.append(f"district {code}: the east-coast share of N1 is {v['share']}: whether it is above 50 turns on its rounding, which the definitions do not settle")

    for uid, u in units.items():
        if uid not in decision or uid not in hansen or uid not in need or uid not in corestack:
            continue
        d, h = decision[uid], hansen[uid]
        if D(d["dense_2000_ha"]) != D(h["area_ha_gt30"]) or D(d["open_2000_ha"]) != D(h["area_ha_gt10le30"]):
            wrong.append(f"{uid}: a band's land in 2000 differs between the decision table and the Hansen table")
        if d["pc11_district_code"].strip() != u["pc11_district_code"]:
            wrong.append(f"{uid}: the district rebuilt from 10_units/ ({u['pc11_district_code']}) is not the decision table's ({d['pc11_district_code']})")
        u["forest_2000_ha"] = forest_2000 = D(d["dense_2000_ha"]) + D(d["open_2000_ha"])
        u["forest_at_window_start_ha"] = start = D(d["forest_at_window_start_ha_2018_2025"])
        dense_lost = sum((D(h[f"loss_ha_gt30_{y}"]) for y in _units_PRIOR_YEARS), D(0))
        open_lost = sum((D(h[f"loss_ha_gt10le30_{y}"]) for y in _units_PRIOR_YEARS), D(0))
        u["dense_at_window_start_ha"] = dense = max(D(h["area_ha_gt30"]) - dense_lost, D(0))
        u["bands_add_up"] = dense + max(D(h["area_ha_gt10le30"]) - open_lost, D(0)) == start      # a gate of the step counts where they do not
        u["loss_2001_2017_ha"] = lost = dense_lost + open_lost
        u["dense_share_of_forest_at_start_pct"] = _units_pct(dense, start)
        u["prior_loss_share_pct"] = _units_pct(lost, forest_2000)
        u["log_forest_at_start"] = math.log(float(start)) if start > 0 else None
        u["forest_loss_share_pct"] = d["forest_loss_share_pct_2018_2025"]
        u["loss_recorded"] = "1" if d["loss_column_2018_2025"].strip() == "some" else "0"
        named, plantation = started.get(uid, (D(0), D(0)))
        u["forest_named_by_fy2017_18_inr"], u["plantation_category_by_fy2017_18_inr"] = named, plantation
        u["e1_any_forest_named"] = "1" if named > 0 else "0"
        u["e3_any_plantation_category"] = "1" if plantation > 0 else "0"
        u["e2_asinh_forest_named_inr_per_ha"] = math.asinh(float(named) / float(start)) if start > 0 else None
        census = u["unit_level"] == _units_LGD              # outside-village land has no census rows
        st, adi = _units_dec(need[uid]["st_share"]), _units_dec(need[uid]["adi_2011"])
        u["st_share_pct"] = D(100) * st if census and st is not None else None
        u["adi_2011"] = adi if census else None
        down, up = D(corestack[uid]["corestack_degradation_ha_tc_gt10"]), D(corestack[uid]["corestack_improvement_ha_tc_gt10"])
        u["corestack_degradation_ha_tc_gt10"], u["corestack_improvement_ha_tc_gt10"] = down, up
        u["downward_share_pct"] = _units_pct(down, down + up)
        u["in_district_left_out_of_c7"] = "1" if c7.get(u["pc11_district_code"], {}).get("left_out") == "yes" else "0"
        x, raw = {}, {}
        for v in _units_VARIABLES:
            raw[v] = nan if u[v] is None or str(u[v]).strip() == "" else float(u[v])
            x[v] = round(raw[v], 10) if isinstance(u[v], float) else raw[v]      # the logarithm and the asinh: ten decimals
        if start > 0:
            raw["dense_share_of_forest_at_start_pct"] = float(D(100) * dense / start)
        if forest_2000 > 0:
            raw["prior_loss_share_pct"] = float(D(100) * lost / forest_2000)
        if down + up > 0:
            raw["downward_share_pct"] = float(D(100) * down / (down + up))
        u["x"], u["raw"] = x, raw
    for mid, (outcome, exposure, floor, restriction, controls) in _units_MODELS.items():
        for u in units.values():                            # a sample: at or above the floor, the restriction, no blank among the variables
            if "x" not in u:
                continue
            inside = u["forest_at_window_start_ha"] >= D(floor) and all(u["x"][v] == u["x"][v] for v in (outcome, exposure) + controls)
            if restriction == _units_NOT_C7:
                inside = inside and u["in_district_left_out_of_c7"] == "0"
            elif restriction == _units_LGD_ONLY:
                inside = inside and u["unit_level"] == _units_LGD
            elif restriction == _units_OF_H1:
                inside = inside and u["in_h1"] == "1"
            u["in_" + mid.lower()] = "1" if inside else "0"
    order = sorted(units, key=lambda uid: (units[uid]["pc11_district_code"], uid))
    return units, order, wrong, c7


def _units_check_table(units, order, c7):
    """unit_history.csv against the recomputed records: its shape, its order, then every column, a group of columns a check."""
    t = table("unit_history.csv")
    header = _units_header("unit_history.csv")
    ids = [r.get("unit_id") for r in t]
    ragged = sum(None in r or None in r.values() for r in t)
    shape = (len(t) == 11468 and len(units) == 11468 and len(set(ids)) == len(ids) and set(ids) == set(units)
             and header == list(_units_COLUMNS) and not ragged)
    check("unit_history.csv: 11,468 rows, one for each unit of 10_units/units.gpkg and no unit twice, with the 34 columns the "
          "definition names, in its order, and in every row a cell for each column and none beyond", shape, "" if shape else
          f"{len(t)} rows, {len(set(ids))} distinct unit ids, {len(set(ids) ^ set(units))} ids not shared with units.gpkg ({len(units)} units); "
          f"{ragged} rows with a cell missing or one too many; "
          f"columns missing {[c for c in _units_COLUMNS if c not in header]}, not in the definition {[c for c in header if c not in _units_COLUMNS]}, "
          f"in the definition's order: {header == list(_units_COLUMNS)}")
    first = next((i for i, (a, b) in enumerate(zip(ids, order)) if a != b), min(len(ids), len(order)))
    check("unit_history.csv: the rows are in the order of the census district code rebuilt from the inputs, then of the unit id read as text",
          ids == order, "" if ids == order else f"first at line {first + 2} of the file: table {(ids + ['(no row)'])[first]!r}, "
          f"recomputed {(order + ['(no row)'])[first]!r}")
    t = [r for r in t if r.get("unit_id") in units and "x" in units[r["unit_id"]]]
    n = f"{len(t):,} rows"                                   # the rows whose unit is a unit of the inputs: those compared below

    def cells(columns, same):
        return [(f"{r['unit_id']} {c}", r.get(c), units[r["unit_id"]][c], same(r.get(c), units[r["unit_id"]][c])) for r in t for c in columns]

    def text(a, b):
        return a == b

    _units_settle(f"unit_history.csv: unit_level and outside_village equal those of units.gpkg, pc11_district_code equals the code the unit "
                  f"carries in units.gpkg (an LGD panchayat unit) or is assigned in outside_village_district.csv (an outside-village unit), and "
                  f"district_name equals the name the Odisha FRA table carries for that code, as text ({n})", cells(_units_KEY[1:], text))
    _units_settle(f"unit_history.csv: forest_2000_ha equals dense_2000_ha + open_2000_ha and forest_at_window_start_ha equals "
                  f"forest_at_window_start_ha_2018_2025 of the decision table, exactly, as numbers ({n})",
                  cells(("forest_2000_ha", "forest_at_window_start_ha"), _units_same_number))
    _units_settle(f"unit_history.csv: dense_at_window_start_ha equals the dense band's land in 2000 less its loss of 2001 to 2017, not below zero, "
                  f"and loss_2001_2017_ha equals the dense plus open loss of 2001 to 2017, both as exact sums of the Hansen table's yearly "
                  f"columns, as numbers ({n})", cells(("dense_at_window_start_ha", "loss_2001_2017_ha"), _units_same_number))
    _units_settle(f"unit_history.csv: dense_share_of_forest_at_start_pct equals 100 x dense_at_window_start_ha / forest_at_window_start_ha and "
                  f"prior_loss_share_pct equals 100 x loss_2001_2017_ha / forest_2000_ha, each rounded half up to the 6 decimals the table "
                  f"prints, and each is blank exactly where its denominator is zero ({n})",
                  cells(("dense_share_of_forest_at_start_pct", "prior_loss_share_pct"), _units_same_number))
    _units_settle(f"unit_history.csv: log_forest_at_start equals the natural logarithm of forest_at_window_start_ha to the 10 decimals the "
                  f"table prints (within 5.1e-11), and is blank exactly where that forest is zero ({n})",
                  cells(("log_forest_at_start",), lambda a, b: _units_near(a, b, _units_TOL10)))
    _units_settle(f"unit_history.csv: forest_loss_share_pct equals forest_loss_share_pct_2018_2025 of the decision table as text (its two "
                  f"decimals, its blanks), and loss_recorded is 1 exactly where loss_column_2018_2025 is 'some', else 0 ({n})",
                  cells(("forest_loss_share_pct", "loss_recorded"), text))
    _units_settle(f"unit_history.csv: forest_named_by_fy2017_18_inr and plantation_category_by_fy2017_18_inr equal the exact sums of "
                  f"expenditure_forest_named_worktype and expenditure_plantation_category over the unit's rows of allocation_by_unit_fy.csv "
                  f"whose fy_work_start is 2017-18 or earlier (NA not among them; 0 for a unit with no such row), as numbers ({n})",
                  cells(("forest_named_by_fy2017_18_inr", "plantation_category_by_fy2017_18_inr"), _units_same_number))
    _units_settle(f"unit_history.csv: e1_any_forest_named and e3_any_plantation_category are 1 exactly where the recomputed sum of rupees is "
                  f"above zero, else 0 ({n})", cells(("e1_any_forest_named", "e3_any_plantation_category"), text))
    _units_settle(f"unit_history.csv: e2_asinh_forest_named_inr_per_ha equals asinh(forest_named_by_fy2017_18_inr / forest_at_window_start_ha) "
                  f"to the 10 decimals the table prints (within 5.1e-11), and is blank exactly where that forest is zero ({n})",
                  cells(("e2_asinh_forest_named_inr_per_ha",), lambda a, b: _units_near(a, b, _units_TOL10)))
    _units_settle(f"unit_history.csv: st_share_pct equals 100 x st_share and adi_2011 equals adi_2011 of the need table, exactly, as numbers; "
                  f"both blank for every outside-village unit and where the need table is blank ({n})",
                  cells(("st_share_pct", "adi_2011"), _units_same_number))
    _units_settle(f"unit_history.csv: corestack_degradation_ha_tc_gt10 and corestack_improvement_ha_tc_gt10 equal those of corestack_by_unit.csv "
                  f"exactly, as numbers, and downward_share_pct equals 100 x degradation / (degradation + improvement) rounded half up to the "
                  f"6 decimals the table prints, blank exactly where the two add to zero ({n})",
                  cells(("corestack_degradation_ha_tc_gt10", "corestack_improvement_ha_tc_gt10", "downward_share_pct"), _units_same_number))
    _units_settle(f"unit_history.csv: in_district_left_out_of_c7 is 1 exactly for the units of the districts C7's rule leaves out, the list "
                  f"rebuilt from the inputs (a district is left out where more than half of its N1 of 2018_2025 - forest_loss_ha_2018_2025 "
                  f"of the decision table summed over its units in the three loss cells - lies in units whose corestack_zone_model in "
                  f"agreement_by_unit.csv is 'ECPHR only'; a district with no N1 stays in), else 0 ({n})", cells(("in_district_left_out_of_c7",), text))
    try:
        said = [((r.get("pc11_district_code") or "").strip(), (r.get("left_out_of_c7") or "").strip()) for r in table("district_need.csv")]
    except Exception as e:
        said = [("", f"district_need.csv could not be read: {type(e).__name__}")]
    link = [(f"district {code}", dict(said).get(code, "(no row)"), v["left_out"], dict(said).get(code) == v["left_out"]) for code, v in sorted(c7.items())]
    link += [(f"district_need.csv row {i + 2}", f"code {code!r}", "one row for each of the 30 districts", False)
             for i, (code, _) in enumerate(said) if code not in c7 or [k for k, _ in said].count(code) != 1]
    _units_settle("district_need.csv of the folder being checked: left_out_of_c7 is yes for exactly the districts that rule leaves out and no "
                  "for each other of the 30, one row a district (the definition takes the unit table's flag from this column)", link, 9)
    _units_settle(f"unit_history.csv: in_h1 to in_h9 are 1 exactly for the units of each model's sample rebuilt from the recomputed columns "
                  f"(forest at the start of 2018 at or above the model's floor; for H4 outside the districts that rule leaves out, for H5 an "
                  f"LGD panchayat unit, for H9 a unit of H1's sample; no blank among the model's variables), else 0 ({n})",
                  cells(_units_SAMPLE_FLAGS, text))


def _units_design(units, order, mid, form):
    """One model's sample as arrays: the outcome; the design, which is the exposure, then the controls in the definition's
    order, then a 0/1 column for every district present in the sample, and no constant; the columns' names; each unit's
    cluster as a whole number, 0..G-1 in the sorted order of the district codes; and the 0/1 columns alone. `form` is
    `x` (each variable as the unit table prints it) or `raw` (before it is rounded for the table)."""
    outcome, exposure, _, _, controls = _units_MODELS[mid]
    ids = [uid for uid in order if units[uid].get("in_" + mid.lower()) == "1"]
    codes = sorted({units[uid]["pc11_district_code"] for uid in ids})
    cl = np.array([codes.index(units[uid]["pc11_district_code"]) for uid in ids], dtype=np.int64)
    Z = (cl[:, None] == np.arange(len(codes))[None, :]).astype(float)
    y = np.array([units[uid][form][outcome] for uid in ids], dtype=float)
    X = np.column_stack([np.array([units[uid][form][v] for uid in ids], dtype=float) for v in (exposure,) + controls] + [Z])
    return y, X, [exposure] + list(controls) + ["district_" + c for c in codes], cl, Z


def _units_fit(y, X, Z):
    """OLS by numpy's least squares, and the CR1 standard error of the first coefficient: the cluster sandwich
    (X'X)^-1 [sum over clusters of X_g' u_g u_g' X_g] (X'X)^-1 times G/(G-1) x (N-1)/(N-K), the clusters being the columns
    of Z. Returns (the first coefficient, the rank of the design, its standard error)."""
    n, K = X.shape
    G = Z.shape[1]
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    bread = np.linalg.inv(X.T @ X)
    score = Z.T @ (X * (y - X @ beta)[:, None])              # clusters x columns: a row is X_g' u_g
    V = bread @ (score.T @ score) @ bread * (G / (G - 1)) * ((n - 1) / (n - K))
    return float(beta[0]), int(rank), math.sqrt(float(V[0, 0]))


def _units_boot(y, X, Z, A, W, b0, cl=None):
    """This part's own restricted wild cluster bootstrap-t of H0: the first coefficient equals b0, tested as the definition
    says: as H0: it is zero, after y is replaced by y - b0 * x. `A` is (X'X)^-1 X'; `W` holds a weight for each cluster
    (row) and draw (column). The model with the first coefficient held at zero is fitted; a draw's outcome is that fit
    plus its residuals, each times the weight of its unit's cluster; the full model is fitted to the draw's outcome and
    the same cluster-robust t is formed. Returns (the share of draws whose |t| is above the |t| of the data - the
    package counts so; "at least" would differ only where a draw's |t| equals the data's to the last bit - and the t of
    every draw). The draws' t come from sums by cluster, a draw's outcome being linear in its weights; with `cl` (each
    unit's cluster) given they come instead from the n outcomes of each draw, one regression a draw: the plain way."""
    n, K = X.shape
    G = Z.shape[1]
    c = G / (G - 1) * (n - 1) / (n - K)
    a = A[0]                                                 # the row of (X'X)^-1 X' that gives the first coefficient
    yy = y - b0 * X[:, 0]
    t = float(a @ yy) / math.sqrt(c * float(((Z.T @ (a * (yy - X @ (A @ yy)))) ** 2).sum()))
    fit = X[:, 1:] @ np.linalg.lstsq(X[:, 1:], yy, rcond=None)[0]      # the first coefficient held at zero
    res = yy - fit
    if cl is not None:
        Y = fit[:, None] + res[:, None] * W[cl, :]           # units x draws: the outcome of every draw
        coef = A @ Y
        S = Z.T @ (a[:, None] * (Y - X @ coef))              # clusters x draws: the sum over a cluster of a_i times the draw's residual
        ts = coef[0] / np.sqrt(c * (S ** 2).sum(axis=0))
    else:
        E = Z * res[:, None]                                 # units x clusters: one cluster's restricted residuals, zero elsewhere
        Q = Z.T @ (a[:, None] * (E - X @ (A @ E)))           # what cluster h's residuals, weighted by one, add to cluster g's sum
        base = Z.T @ (a * (fit - X @ (A @ fit)))             # what the fit adds to it: zero but for rounding
        ts = (float(a @ fit) + (Z.T @ (a * res)) @ W) / np.sqrt(c * ((base[:, None] + Q @ W) ** 2).sum(axis=0))
    return float(np.mean(np.abs(ts) > abs(t))), ts


def _units_webb(G, B, seed):
    """Webb's six-point weights (+-sqrt(3/2), +-1, +-sqrt(1/2), a sixth each), one for each of G clusters (rows) and B draws."""
    six = np.array([-math.sqrt(1.5), -1.0, -math.sqrt(0.5), math.sqrt(0.5), 1.0, math.sqrt(1.5)])
    return six[np.random.default_rng(seed).integers(0, 6, size=(G, B))]


def _units_package_weights(G, B, seed):
    """The weights the `wildboottest` package (0.3.2) draws for a seed: one call of numpy's default_rng(seed).choice over
    the six Webb values in ascending order, G x B of them, laid out a row a cluster (its clusters in the sorted order
    of their labels). Its p is the share of draws whose |t| exceeds the |t| of the data."""
    six = np.concatenate([-np.sqrt(np.array([3, 2, 1]) / 2), np.sqrt(np.array([1, 2, 3]) / 2)])
    return np.random.default_rng(seed).choice(a=six, replace=True, size=G * B).reshape(G, B)


def _units_package_p(y, X, names, cl, b0, B, seed):
    """The p the `wildboottest` package gives H0: the first coefficient equals b0, by refitting with y - b0 * x: Webb
    weights, the null imposed, the clusters passed as whole numbers 0..G-1 in the sorted order of the district codes.
    `parallel=False` asks the package to run its loop over the draws on one thread: the draws and the arithmetic of
    each are the same, and the call compiles in a third of the time. Not a number where the package gives none: every
    check that reads it then fails."""
    import pandas as pd
    import statsmodels.api as sm
    from wildboottest.wildboottest import wildboottest
    try:
        got = wildboottest(sm.OLS(y - b0 * X[:, 0], pd.DataFrame(X, columns=names)), param=names[0], cluster=pd.Series(cl), B=B,
                           weights_type="webb", impose_null=True, seed=seed, parallel=False, show=False)
        return float(got["p-value"].iloc[0])
    except Exception:
        return float("nan")


def _units_mc(p, B):
    """How far two bootstrap p values of one hypothesis may lie apart when one comes from B draws and the other from this
    part's own draws: four standard errors of their difference at p, sqrt(p(1-p)(1/B + 1/own draws)), and one draw of B."""
    return 4 * math.sqrt(max(p * (1 - p), 0.0) * (1 / B + 1 / _units_OWN_DRAWS)) + 1 / B


def _units_grid(grids, mid):
    """One model's saved grid as {"lo": [(b0, p), ...], "hi": [...]} from the estimate outward, and what the file says of the
    model; (None, {}) where the file does not hold such a grid."""
    g = grids.get(mid) if isinstance(grids, dict) else None
    try:
        sides = {s: [(float(e["b0"]), float(e["p"])) for e in g["grid"][s]] for s in ("lo", "hi")}
    except Exception:
        return None, {}
    if any(len(v) < 2 or not all(math.isfinite(b0) and math.isfinite(p) for b0, p in v) for v in sides.values()):
        return None, {}
    return sides, g


def _units_grid_side(points):
    """What the definition keeps of one side of a grid, from the estimate outward: how many steps cross the level (p below
    it at one end of the step and not at the other), whether p climbs more than 0.01 above a value it had already fallen
    to, p at the outer end, and the outermost step that crosses (its position, None if none does)."""
    p = [v for _, v in points]
    cross = [i for i in range(len(p) - 1) if (p[i] < _units_LEVEL) != (p[i + 1] < _units_LEVEL)]
    rises = any(p[j] > min(p[:j]) + 0.01 for j in range(1, len(p)))
    return len(cross), "yes" if rises else "no", p[-1], cross[-1] if cross else None


def _units_placed(sides, rule):
    """Whether each side of a saved grid holds the points of the rule: as many, each within 1e-9 of where the rule puts it."""
    return all(len(sides[s]) == len(rule[s]["points"]) and all(abs(b0 - want) <= 1e-9 for (b0, _), (want, _) in zip(sides[s], rule[s]["points"]))
               for s in ("lo", "hi"))


def _units_invert(f):
    """The owner's rule of the interval for one model, redone from the fit alone with this part's bootstrap arithmetic and
    the weights the recorded seed draws. The bracket is the estimate -/+ 4 se_cr1 x 2^d, ONE d for both sides: the
    smallest of 0 to 10 at which p is below the level at both ends, 10 if there is none. Each side is then read on 16
    equal steps from the estimate to its end and, where p at that end is below the level, bisected inside the outermost
    step that crosses the level until the step is no wider than 0.001 se_cr1. Returns d, the p at the two ends of every
    bracket tried, and for each side: `points` (the 17 (b0, p) from the estimate outward), `crossings`, `rises`,
    `p_end` (what the definition keeps of them), `unbounded` (yes where p at the outer end is not below the level, else
    no), `settled` (False where the other reading of "never gets below" - no point of the grid below the level - would say
    otherwise) and `last` (the last bracket of the bisection: the b0 at which p is at least the level, the b0 at which
    it is below; None for a side with no end). Under `asked` it returns every b0 at which it read a p, in the order read."""
    b, se = f["b"], f["se"]

    asked = []

    def p(b0):
        asked.append(b0)
        return _units_boot(f["y"], f["X"], f["Z"], f["A"], f["Wp"], b0)[0]

    out = {"d": 0, "ends": [], "asked": asked}
    while True:
        width = _units_BRACKET_SE * se * 2 ** out["d"]
        out["ends"].append((p(b - width), p(b + width)))
        if max(out["ends"][-1]) < _units_LEVEL or out["d"] == _units_MAX_DOUBLINGS:
            break
        out["d"] += 1
    for side, sign in (("lo", -1), ("hi", 1)):
        points = [(b0, p(b0)) for b0 in (b + sign * i * width / _units_GRID_STEPS for i in range(_units_GRID_STEPS + 1))]
        crossings, rises, p_end, outermost = _units_grid_side(points)
        bounded = p_end < _units_LEVEL
        last = None
        if bounded:                                          # p is 1 at the estimate and below the level at the end: a step crosses, downward
            inner, outer = points[outermost][0], points[outermost + 1][0]
            for _ in range(200):
                if not abs(outer - inner) > _units_BISECT_SE * se:
                    break
                half = (inner + outer) / 2
                if p(half) < _units_LEVEL:
                    outer = half
                else:
                    inner = half
            last = (inner, outer)
        out[side] = {"points": points, "crossings": crossings, "rises": rises, "p_end": p_end, "unbounded": "no" if bounded else "yes",
                     "settled": bounded == any(v < _units_LEVEL for _, v in points), "last": last}
    return out


def _units_check_models(units, order, kept=None):
    """unit_history_models.csv against the nine models refitted on the recomputed unit table, the bootstrap redone twice
    (this part's own code and draws; the package with the recorded seed), the interval's rule redone from the fit, and
    the saved grids of p values against that. `kept`, if given, receives for each model whether its design has full column
    rank (`full`) and what the rule gives it (`rule`): the gates of the step are held to them."""
    m = table("unit_history_models.csv")
    header = _units_header("unit_history_models.csv")
    ids = [r.get("id") for r in m]
    ragged = sum(None in r or None in r.values() for r in m)
    shape = ids == list(_units_MODELS) and header == list(_units_MODEL_COLUMNS) and not ragged
    check("unit_history_models.csv: 9 rows, H1 to H9 in that order and none twice, with the 30 columns the definition names, in its order, "
          "and in every row a cell for each column and none beyond",
          shape, "" if shape else f"ids {ids}; {ragged} rows with a cell missing or one too many; columns missing "
          f"{[c for c in _units_MODEL_COLUMNS if c not in header]}, not in the definition "
          f"{[c for c in header if c not in _units_MODEL_COLUMNS]}, in the definition's order: {header == list(_units_MODEL_COLUMNS)}")
    row = {}
    for r in m:
        row.setdefault(r.get("id"), r)

    def cell(mid, col):
        v = row.get(mid, {}).get(col)
        return "" if v is None else v

    words, named = [], []
    for mid, (outcome, exposure, floor, restriction, controls) in _units_MODELS.items():
        words.append((f"{mid} headline", cell(mid, "headline"), "yes" if mid == "H1" else "no", cell(mid, "headline") == ("yes" if mid == "H1" else "no")))
        words += [(f"{mid} {c}", cell(mid, c), "words, not a blank", cell(mid, c).strip() != "")
                  for c in ("sample", "outcome_unit", "exposure_unit", "coefficient_unit", "controls")]
        for col, variable in (("outcome_unit", outcome), ("exposure_unit", exposure), ("coefficient_unit", outcome), ("coefficient_unit", exposure)):
            uses, avoids = _units_WORDS[variable]
            words.append((f"{mid} {col}", cell(mid, col), f"one of {uses} and none of {avoids}, for {variable}",
                          any(w in cell(mid, col) for w in uses) and not any(w in cell(mid, col) for w in avoids)))
        for word, wanted in (("C7", restriction == _units_NOT_C7), ("LGD", restriction == _units_LGD_ONLY)):
            words.append((f"{mid} sample", cell(mid, "sample"), f"{'names' if wanted else 'does not name'} {word}", (word in cell(mid, "sample")) == wanted))
        named.append((f"{mid} outcome", cell(mid, "outcome"), outcome, cell(mid, "outcome") == outcome))
        named.append((f"{mid} exposure", cell(mid, "exposure"), exposure, cell(mid, "exposure") == exposure))
        listed = [w.strip() for w in cell(mid, "controls").split(";") if w.strip() in _units_COLUMNS]
        named.append((f"{mid} controls", cell(mid, "controls"), "; ".join(controls), listed == list(controls)))
        named.append((f"{mid} sample", cell(mid, "sample"), f"... {floor} ha ...", f" {floor} ha" in cell(mid, "sample")))
    _units_settle("unit_history_models.csv: headline is yes for H1 and no for the other eight; sample, outcome_unit, exposure_unit, "
                  "coefficient_unit and controls are not blank; outcome_unit uses the definitions' word for the model's own outcome "
                  "('percentage' or 'per cent' for the share of forest lost, 'probability' for H8, 'downward' for H9) and not the word of "
                  "another outcome, exposure_unit likewise for the exposure ('forest-named', 'asinh' for H6, 'plantation' for H7), and "
                  "coefficient_unit both; sample names C7 for H4 alone and LGD for H5 alone (the rest of the wording is not checked)", words, 9)
    _units_settle("unit_history_models.csv: outcome and exposure name the definition's variables for each model, the columns of "
                  "unit_history.csv that controls lists between its semicolons are the definition's controls for that model, in its order, "
                  "and sample gives the model's floor as so many ha (100, 50 or 10)", named, 9)

    fits, counts, coefs, errors, unrounded, recorded = {}, [], [], [], [], []
    for k, mid in enumerate(_units_MODELS):
        y, X, names, cl, Z = _units_design(units, order, mid, "x")
        b, rank, se = _units_fit(y, X, Z)
        (n, K), G = X.shape, Z.shape[1]
        B, seed = _units_B_HEADLINE if mid == "H1" else _units_B_OTHERS, _units_SEED_BASE + 500 + k
        fits[mid] = {"y": y, "X": X, "names": names, "cl": cl, "Z": Z, "b": b, "se": se, "B": B, "seed": seed, "full": rank == K,
                     "A": np.linalg.solve(X.T @ X, X.T)}
        for col, value in (("n_units", n), ("n_exposed", int((X[:, 0] > 0).sum())), ("n_districts", G)):
            counts.append((f"{mid} {col}", cell(mid, col), str(value), cell(mid, col) == str(value)))
        counts.append((f"{mid} n_parameters", cell(mid, "n_parameters"), str(K) if rank == K else f"{K} columns of rank {rank}",
                       cell(mid, "n_parameters") == str(K) and rank == K))
        coefs.append((f"{mid} coefficient", cell(mid, "coefficient"), b, _units_near(cell(mid, "coefficient"), b, _units_TOL8)))
        errors.append((f"{mid} se_cr1", cell(mid, "se_cr1"), se, _units_near(cell(mid, "se_cr1"), se, _units_TOL8)))
        errors.append((f"{mid} t_cr1", cell(mid, "t_cr1"), b / se, _units_near(cell(mid, "t_cr1"), b / se, _units_TOL6)))
        y0, X0, _, _, Z0 = _units_design(units, order, mid, "raw")
        b0, _, se0 = _units_fit(y0, X0, Z0)
        unrounded.append((f"{mid} coefficient", cell(mid, "coefficient"), b0, _units_near(cell(mid, "coefficient"), b0, 1e-6)))
        unrounded.append((f"{mid} se_cr1", cell(mid, "se_cr1"), se0, _units_near(cell(mid, "se_cr1"), se0, 1e-6)))
        recorded += [(f"{mid} {col}", cell(mid, col), value, cell(mid, col) == value)
                     for col, value in (("wcb_B", str(B)), ("wcb_seed", str(seed)), ("wcb_weights", "webb"))]
    _units_settle("unit_history_models.csv: n_units, n_exposed (units of the sample with the exposure above zero), n_districts and n_parameters "
                  "equal the rows, the exposed rows, the districts and the columns of the design rebuilt from the recomputed unit table (the "
                  "exposure, the controls, a 0/1 column for every district present, no constant), which has full column rank", counts, 9)
    _units_settle("unit_history_models.csv: coefficient equals the exposure's coefficient by OLS (numpy lstsq) on that design, each variable "
                  "taken as the unit table prints it, to the 8 decimals the table prints (within 5.1e-9)", coefs, 9)
    _units_settle("unit_history_models.csv: se_cr1 equals the CR1 standard error recomputed in numpy (the cluster sandwich times G/(G-1) x "
                  "(N-1)/(N-K), clusters the districts) to the 8 decimals the table prints (within 5.1e-9), and t_cr1 equals coefficient / "
                  "se_cr1 to its 6 decimals (within 5.1e-7)", errors, 9)
    _units_settle("unit_history_models.csv: coefficient and se_cr1 are also within 1e-6 of the fit in which each variable is taken before it "
                  "is rounded for the unit table (the definition does not say which of the two the regression reads)", unrounded, 9)
    _units_settle("unit_history_models.csv: wcb_B is 9999 for H1 and 1999 for the others, wcb_seed is 20261010 + 500 + the model's place "
                  "(H1 0 ... H9 8) and wcb_weights is webb, as the definition fixes them", recorded, 9)

    # the owner's rule of the interval, redone for each model with this part's arithmetic and the weights of the recorded seed
    for mid, f in fits.items():
        rB, rseed = cell(mid, "wcb_B"), cell(mid, "wcb_seed")     # the recorded draws and seed, if they are whole numbers; the definition's if not
        f["rB"] = int(rB) if rB.isascii() and rB.isdigit() and 0 < int(rB) <= 100000 else f["B"]
        f["rseed"] = int(rseed) if rseed.isascii() and rseed.isdigit() and len(rseed) < 19 else f["seed"]
        f["Wp"] = _units_package_weights(f["Z"].shape[1], f["rB"], f["rseed"])
        f["rule"] = _units_invert(f)
    if kept is not None:
        kept.update({mid: {"full": f["full"], "rule": f["rule"]} for mid, f in fits.items()})

    # the bootstrap with this part's own code and its own draws
    two_ways, own_p, own_ends = [], [], []
    for k, (mid, f) in enumerate(fits.items()):
        y, X, Z, A, b = f["y"], f["X"], f["Z"], f["A"], f["b"]
        W = _units_webb(Z.shape[1], _units_OWN_DRAWS, _units_OWN_SEED + k)
        p, ts = _units_boot(y, X, Z, A, W, 0.0)
        for label, b0 in (("beta = 0", 0.0), ("beta = the coefficient less 2 se_cr1", b - 2 * f["se"])):
            sums, plain = _units_boot(y, X, Z, A, W[:, :200], b0)[1], _units_boot(y, X, Z, A, W[:, :200], b0, f["cl"])[1]
            gap = float(np.max(np.abs(plain - sums) / np.maximum(np.abs(plain), 1e-300)))
            two_ways.append((f"{mid}, H0: {label}", f"the two differ by up to {gap:.1e} of the t", gap <= 1e-9))
        own_p.append((f"{mid} wcb_p", cell(mid, "wcb_p"), f"{p!r} (within {_units_mc(p, f['B']):.4f})", _units_near(cell(mid, "wcb_p"), p, _units_mc(p, f["B"]))))
        for side, sign in (("lo", -1), ("hi", 1)):
            text, end, within = cell(mid, f"wcb_ci95_{side}"), _units_float(cell(mid, f"wcb_ci95_{side}")), _units_mc(_units_LEVEL, f["B"])
            if f["rule"][side]["last"] is None:
                own_ends.append((f"{mid} {side}", "the rule gives this side no end: nothing is tested", True))
            elif end is None or not sign * (end - b) > 0:
                own_ends.append((f"{mid} wcb_ci95_{side}", f"{text!r} is not a number {'below' if sign < 0 else 'above'} the coefficient {b:.8f}", False))
            else:
                at_end, half_way = _units_boot(y, X, Z, A, W, end)[0], _units_boot(y, X, Z, A, W, (b + end) / 2)[0]
                own_ends.append((f"{mid} wcb_ci95_{side} {text}", f"own p {at_end:.4f} at the end (0.05 +/- {within:.4f}), {half_way:.4f} half way to it",
                                 abs(at_end - _units_LEVEL) <= within and half_way > _units_LEVEL))
    _units_hold("the unit models: this part's own bootstrap gives each of its first 200 draws the same t, to 1e-9 of the t, whether the t is "
                "formed from sums by cluster or from that draw's own regression on the n outcomes (9 models; H0: beta = 0, and H0: beta = "
                "the coefficient less 2 se_cr1)", two_ways)
    _units_settle("unit_history_models.csv: wcb_p is within 4 standard errors of the difference, and one draw (1 / wcb_B), of the p of this "
                  "part's own restricted wild cluster bootstrap-t of H0: beta = 0 (Webb weights, the null imposed, 99,999 draws of its own; "
                  "the standard error is sqrt(p(1-p)(1/B + 1/99,999)) at this part's p, B being 9,999 for H1 and 1,999 for the others: "
                  "the two use different draws, hence the tolerance, which is at most 0.046)", own_p, 9)
    _units_hold("unit_history_models.csv: wcb_ci95_lo is below and wcb_ci95_hi above the coefficient; at each of the two the p of this part's own "
                "bootstrap of H0: beta = that end (its own 99,999 draws) is within 4 standard errors of the difference, and one draw, of "
                "0.05 (sqrt(0.05 x 0.95 x (1/B + 1/99,999)): within 0.0093 for H1 and 0.0202 for the others), and half way from the "
                "coefficient to it the p is above 0.05 (a side the rule leaves without an end is not tested)", own_ends)

    # the grid of p values saved beside the result, held to the rule; and the columns of the table that the rule fixes
    try:
        grids = json.loads((GAP / _units_GRIDS).read_text(encoding="utf-8"))
    except Exception:
        grids = None
    held = sorted(grids) if isinstance(grids, dict) else None
    check("unit_history_models_wcb_grids.json: the file holds one record for each of H1 to H9 and for nothing else",
          held == sorted(_units_MODELS), "" if held == sorted(_units_MODELS) else f"found {held if held is not None else 'no such file, or not a record of records'}")
    bracket, grid_p, described, unbounded, in_last, at_point, made = [], [], [], [], [], [], []
    for mid, f in fits.items():
        b, se, Z, rule = f["b"], f["se"], f["Z"], f["rule"]
        sides, meta = _units_grid(grids, mid)
        f["sides"] = sides
        tried = "; ".join(f"d = {d}: p {lo:.6f} and {hi:.6f}" for d, (lo, hi) in enumerate(rule["ends"]))
        if sides is None:
            for found in (bracket, grid_p):
                found.append((mid, "the file holds no grid of numbers for this model", False))
        else:
            same_meta = (_units_near(meta.get("estimate"), b, 1e-9) and _units_near(meta.get("se_cr1"), se, 1e-9)
                         and meta.get("B") == f["B"] and meta.get("seed") == f["seed"])
            placed = _units_placed(sides, rule)
            far = [abs(sides[s][-1][0] - b) / se if se > 0 else float("nan") for s in ("lo", "hi")]
            bracket.append((mid, f"saved estimate {meta.get('estimate')!r}, se_cr1 {meta.get('se_cr1')!r}, B {meta.get('B')!r}, seed {meta.get('seed')!r} "
                            f"against {b!r}, {se!r}, {f['B']}, {f['seed']}; the rule gives d = {rule['d']} ({tried}), so each side ends "
                            f"{_units_BRACKET_SE * 2 ** rule['d']} se_cr1 from the estimate; the saved sides hold {len(sides['lo'])} and {len(sides['hi'])} points "
                            f"and end {far[0]:.6f} and {far[1]:.6f} se_cr1 from it; every saved b0 where the rule puts it: {placed}", same_meta and placed))
            differ = [(b0, p, mine) for s in ("lo", "hi") for b0, p in sides[s]
                      for mine in [_units_boot(f["y"], f["X"], Z, f["A"], f["Wp"], b0)[0]] if not abs(mine - p) <= 1e-9]
            grid_p.append((mid, f"{len(differ)} of {len(sides['lo']) + len(sides['hi'])} differ, e.g. at b0 {differ[0][0]!r}: saved {differ[0][1]!r}, "
                           f"recomputed {differ[0][2]!r}" if differ else "", not differ))
        nulls = len({round((b0 - b) / se, 9) for b0 in rule["asked"] + [0.0]})
        made.append((f"{mid} tests_made", repr(meta.get("tests_made")), str(nulls), type(meta.get("tests_made")) is int and meta.get("tests_made") == nulls))
        for side, sign in (("lo", -1), ("hi", 1)):
            r = rule[side]
            described.append((f"{mid} wcb_crossings_{side}", cell(mid, f"wcb_crossings_{side}"), str(r["crossings"]), cell(mid, f"wcb_crossings_{side}") == str(r["crossings"])))
            described.append((f"{mid} wcb_p_rises_again_{side}", cell(mid, f"wcb_p_rises_again_{side}"), r["rises"], cell(mid, f"wcb_p_rises_again_{side}") == r["rises"]))
            described.append((f"{mid} wcb_p_at_bracket_end_{side}", cell(mid, f"wcb_p_at_bracket_end_{side}"), r["p_end"],
                              _units_near(cell(mid, f"wcb_p_at_bracket_end_{side}"), r["p_end"], _units_TOL6)))
            unbounded.append((f"{mid} wcb_unbounded_{side}", cell(mid, f"wcb_unbounded_{side}"),
                              r["unbounded"] if r["settled"] else "the definitions do not settle it: p at the outer end is not below 0.05, yet p is below it elsewhere on the grid",
                              r["settled"] and cell(mid, f"wcb_unbounded_{side}") == r["unbounded"]))
            end = _units_float(cell(mid, f"wcb_ci95_{side}"))
            if r["last"] is None:
                in_last.append((f"{mid} {side}", "the rule gives this side no end: nothing is tested", True))
            elif end is None:
                in_last.append((f"{mid} wcb_ci95_{side}", f"{cell(mid, f'wcb_ci95_{side}')!r} is not a number", False))
                at_point.append((f"{mid} wcb_ci95_{side} {cell(mid, f'wcb_ci95_{side}')!r}", None, (False, False, False)))
            else:
                near, far = sorted(r["last"])
                in_last.append((f"{mid} wcb_ci95_{side}", f"{end!r} is not between {near!r} and {far!r} (a bracket {(far - near) / se:.6f} se_cr1 wide): it is "
                                f"{max(near - end, end - far) / se:.6f} se_cr1 outside it", near - _units_TOL8 <= end <= far + _units_TOL8))
                three = (r["last"][0], (r["last"][0] + r["last"][1]) / 2, r["last"][1])      # the inner end, the middle, the outer end
                at_point.append((f"{mid} wcb_ci95_{side} {cell(mid, f'wcb_ci95_{side}')}", three, tuple(abs(end - v) <= _units_TOL8 for v in three)))
    _units_hold("unit_history_models_wcb_grids.json: for each model the saved estimate and se_cr1 equal the recomputed ones to 1e-9 and B and seed "
                "are the definition's; each side holds 17 points, each (to 1e-9) where the rule puts it: the estimate, then 16 equal steps "
                "to the estimate less / plus 4 se_cr1 x 2^d, with one d for both sides of the model: the smallest of 0 to 10 at which p is "
                "below 0.05 at both ends of the bracket, 10 if there is none (p by this part's bootstrap arithmetic with the weights of the "
                "recorded seed)", bracket)
    _units_hold("unit_history_models_wcb_grids.json: every p of the saved grids (34 a model) equals, to 1e-9, the p this part's own bootstrap code "
                "gives at the b0 saved with it, with the weights the recorded seed draws for the package (numpy default_rng(seed).choice over "
                "the six Webb values, a row a cluster in the sorted order of the district codes)", grid_p)
    _units_settle("unit_history_models_wcb_grids.json: tests_made. The definitions do not say what it counts; it is read here, as the part on "
                  "the panel reads it, as the number of different b0 at which the rule reads a p (H0: beta = 0; the two ends of every "
                  "bracket tried; the 17 points of each side, the estimate once; the points of the two bisections), counted on this "
                  "part's own redoing of the rule (a b0 is counted by its distance from the estimate in se_cr1, rounded to nine decimals)", made, 9)
    _units_settle("unit_history_models.csv: wcb_crossings_lo/hi (the steps with p below 0.05 at one end and not at the other), "
                  "wcb_p_rises_again_lo/hi (yes where, going outward, a p is more than 0.01 above an earlier one, else no) and "
                  "wcb_p_at_bracket_end_lo/hi (the last p, to the 6 decimals the table prints: within 5.1e-7) equal those of the grid this "
                  "part recomputes from the rule (the bracket as above, 17 points a side, p by this part's bootstrap arithmetic with the "
                  "weights of the recorded seed), not those of the saved file", described, 9)
    _units_settle("unit_history_models.csv: wcb_unbounded_lo/hi is yes exactly where, on that recomputed grid, p at the outer end of the side is "
                  "not below 0.05, else no", unbounded, 9)
    _units_hold("unit_history_models.csv: wcb_ci95_lo and wcb_ci95_hi each lie in the last bracket of the bisection this part redoes inside the "
                "outermost step of that recomputed grid in which p crosses 0.05, halved until it is no wider than 0.001 se_cr1 (it ends "
                "0.00098 se_cr1 wide; its two ends included, and 5.1e-9 allowed for the 8 decimals printed; the definitions do not say "
                "which point of it is reported; a side the rule leaves without an end is not tested)", in_last)
    # the same ends to the precision printed: which point of that bracket is reported the definitions do not say, so none is
    # preferred; but a bisection reports one of three, and a builder reports the same one every time
    most = max(range(3), key=lambda k: sum(hit[k] for _, _, hit in at_point)) if at_point else 0
    astray = [f"{key}: the three points are " + (", ".join(f"{v:.8f}" for v in three) if three else "not formed")
              for key, three, hit in at_point if not hit[most]]
    check("unit_history_models.csv: wcb_ci95_lo and wcb_ci95_hi are, each to the 8 decimals the table prints (within 5.1e-9), all at the same "
          "one of the three points of that last bracket that a bisection can report: its inner end (p at least 0.05 there), its middle, "
          "or its outer end (p below 0.05 there). The definitions do not say which is reported, so none of the three is preferred (a "
          "side the rule leaves without an end is not tested)", not astray,
          ("" if at_point else "the rule gives no side an end: nothing is tested") if not astray else
          f"{len(astray)} of the {len(at_point)} ends tested are not at {_units_POINTS[most]} of the bracket, where most are, e.g. " + "; ".join(astray[:6]))

    # the same with the package and the recorded seed: seven calls a model
    at_zero, at_ends, at_bracket_end, same_p = [], [], [], []
    for mid, f in fits.items():
        b, se, rule = f["b"], f["se"], f["rule"]
        points = [("b0 = 0", 0.0)]
        for side, sign in (("lo", -1), ("hi", 1)):
            end = _units_float(cell(mid, f"wcb_ci95_{side}"))
            if rule[side]["last"] is not None and end is not None:
                points += [(f"{side} inside", end - sign * _units_NEAR_END * se), (f"{side} outside", end + sign * _units_NEAR_END * se)]
            points.append((f"{side} bracket end", rule[side]["points"][-1][0]))
        p = {}
        for label, b0 in points:
            p[label] = _units_package_p(f["y"], f["X"], f["names"], f["cl"], b0, f["rB"], f["rseed"])
            mine = _units_boot(f["y"], f["X"], f["Z"], f["A"], f["Wp"], b0)[0]
            same_p.append((f"{mid} {label} (b0 {b0!r})", f"package {p[label]!r}, this part's code {mine!r}", abs(p[label] - mine) <= 1e-9))
        at_zero.append((f"{mid} wcb_p", cell(mid, "wcb_p"), p["b0 = 0"], _units_near(cell(mid, "wcb_p"), p["b0 = 0"], 1e-9)))
        for side in ("lo", "hi"):
            if rule[side]["last"] is None:
                at_ends.append((f"{mid} {side}", "the rule gives this side no end: nothing is tested", True))
            elif f"{side} inside" not in p:
                at_ends.append((f"{mid} wcb_ci95_{side}", f"{cell(mid, f'wcb_ci95_{side}')!r} is not a number", False))
            else:
                at_ends.append((f"{mid} wcb_ci95_{side} {cell(mid, f'wcb_ci95_{side}')}", f"p {p[f'{side} inside']:.6f} just inside, "
                                f"{p[f'{side} outside']:.6f} just outside", p[f"{side} inside"] >= _units_LEVEL and p[f"{side} outside"] < _units_LEVEL))
            got, saved = p[f"{side} bracket end"], None if f["sides"] is None else f["sides"][side][-1]
            at_bracket_end.append((f"{mid} wcb_p_at_bracket_end_{side}", cell(mid, f"wcb_p_at_bracket_end_{side}"), got,
                                   _units_near(cell(mid, f"wcb_p_at_bracket_end_{side}"), got, _units_TOL6)))
            at_bracket_end.append((f"{mid} {side}, the last point of the saved grid", "(no saved grid)" if saved is None else f"b0 {saved[0]!r}, p {saved[1]!r}",
                                   f"b0 {rule[side]['points'][-1][0]!r}, p {got!r}",
                                   saved is not None and abs(saved[0] - rule[side]["points"][-1][0]) <= 1e-9 and abs(saved[1] - got) <= 1e-9))
    _units_settle("unit_history_models.csv: wcb_p equals, to 1e-9, the p the wildboottest package gives H0: beta = 0 on the rebuilt design with the "
                  "recorded wcb_B and wcb_seed (Webb weights, the null imposed, clusters as whole numbers in the sorted order of the district "
                  "codes)", at_zero, 9)
    _units_hold("unit_history_models.csv: with the wildboottest package and the recorded seed, refitting with y - b0 * x, p is at least 0.05 at "
                "b0 0.002 se_cr1 inside wcb_ci95_lo and inside wcb_ci95_hi (towards the coefficient) and below 0.05 at b0 0.002 se_cr1 "
                "outside each (a side the rule leaves without an end is not tested)", at_ends)
    _units_settle("unit_history_models.csv and the saved grids: the p the wildboottest package gives, with the recorded seed, at the two outer ends "
                  "of the bracket the rule gives (the estimate less / plus 4 se_cr1 x 2^d) equals wcb_p_at_bracket_end_lo/hi to the 6 decimals "
                  "the table prints (within 5.1e-7), and the last point of each side of the saved grid is at that b0 with that p (both to 1e-9)",
                  at_bracket_end, 9)
    _units_hold("the unit models: at every b0 at which the package was run (7 a model: 0, just inside and just outside each end, the two outer "
                "ends of the bracket), the p of this part's own bootstrap code with the weights the recorded seed draws equals the package's "
                "p to 1e-9", same_p)


def _units_check_step(units, fits):
    """What the step says of itself: gates_phase4.csv, row by row, and the seeds, the draws and the count of gates in its
    section of gap.provenance.json. The definitions name the gate table and do not list its rows: each row's own label is
    taken as its definition, and the row is found by a phrase of it. `fits` holds, for each model fitted here, whether its
    design has full column rank and what this part's redoing of the interval's rule gives each side."""
    done = [u for u in units.values() if "x" in u]
    odd = sum(1 for u in done if not u["bands_add_up"])
    below = " / ".join(str(sum(1 for u in done if D(floor) - D("0.005") <= u["forest_at_window_start_ha"] < D(floor))) for floor in ("100", "50", "10"))
    rupees = sum((u["forest_named_by_fy2017_18_inr"] for u in done), D(0))
    no_blank = "yes" if all(str(u["forest_loss_share_pct"]).strip() != "" for u in done if u["forest_at_window_start_ha"] >= 100) else "no"
    fitted = sum(1 for f in fits.values() if f["full"])
    bounded = sum(1 for f in fits.values() if all(f["rule"][s]["unbounded"] == "no" for s in ("lo", "hi")))
    steady = sum(1 for f in fits.values() if all(f["rule"][s]["crossings"] == 1 and f["rule"][s]["rises"] == "no" for s in ("lo", "hi")))
    try:
        by_district = sum((D(r[_units_STEP2_SUM[1]]) for r in table(_units_STEP2_SUM[0])), D(0))
    except Exception:
        by_district = None
    # a phrase of the label; what `found` must be; what `expected` must be (None: it could not be formed)
    wanted = (("units in the table", D(len(done)), D(11468)),
              ("do not add to the decision table's forest", D(odd), D(0)),
              ("below a floor", below, "0 / 0 / 0"),
              ("against step 2's sum over districts", rupees, by_district),
              ("no unit with a blank outcome", no_blank, "yes"),
              ("models fitted", D(fitted), D(len(_units_MODELS))),
              ("bounded on both sides", f"{bounded} of {len(_units_MODELS)}", "reported"),
              ("fell steadily on both sides", f"{steady} of {len(_units_MODELS)}", "reported"))
    try:
        gates, header = table(_units_GATES), _units_header(_units_GATES)
    except Exception:
        gates, header = [], []

    def same(cell, value):
        return value is not None and (_units_same_number(cell, value) if isinstance(value, Decimal) else cell == value)

    found, expected, hit = [], [], []
    for phrase, value, hoped in wanted:
        rows_ = [r for r in gates if phrase in (r.get("gate") or "")]
        if len(rows_) != 1:
            for pairs in (found, expected):
                pairs.append((phrase, f"{len(rows_)} rows with this phrase in the label", "one row", False))
            continue
        hit.append(rows_[0].get("gate"))
        said, hope, passed = ((rows_[0].get(c) or "") for c in ("found", "expected", "pass"))
        found.append((phrase, said, value, same(said, value)))
        expected.append((f"{phrase}: expected", hope, hoped, same(hope, hoped)))
        holds = "yes" if hoped == "reported" or same(said, hoped) else "no"
        expected.append((f"{phrase}: pass", passed, holds, passed == holds))
    shape = header == ["gate", "expected", "found", "pass"] and len(gates) == len(wanted) and len(set(hit)) == len(wanted)
    check("gates_phase4.csv: the columns gate, expected, found and pass; 8 rows, and each of the eight gates this part knows by a phrase of "
          "its label is one of them, once", shape, "" if shape else f"columns {header}; {len(gates)} rows; {len(set(hit))} of the {len(wanted)} phrases found once")
    _units_settle("gates_phase4.csv: found equals what this part recomputes for each gate from the inputs, read from the gate's own label (the "
                  "units; the units whose dense and open bands at the start of 2018, each its land in 2000 less its loss of 2001 to 2017 and "
                  "not below zero, do not add to the decision table's forest at the start of the window; the units whose forest at the "
                  "start is below a floor of 100 / 50 / 10 ha by no more than 0.005 ha; the forest-named rupees of works started by "
                  "FY2017-18 summed over units, exactly; whether no unit of 100 ha or more has a blank outcome; the models whose design has "
                  "full column rank; the models both of whose sides the redone rule bounds; the models with one crossing and no climb of "
                  "more than 0.01 on both sides), numbers as numbers and words as text", found, 9)
    _units_settle("gates_phase4.csv: expected is 11468 units, 0, '0 / 0 / 0', the sum of dump_forest_named_started_by_fy2017_18_inr over "
                  "the rows of district_allocation.csv of the folder being checked, yes, 9 models, and "
                  "the word reported for the two gates that report; pass is yes exactly where found equals expected or the gate reports", expected, 9)
    try:
        sec = json.loads((GAP / _units_PROVENANCE).read_text(encoding="utf-8"))["steps"][_units_STEP]
    except Exception:
        sec = None
    said = []
    if isinstance(sec, dict):
        seeds, draws = (sec.get(k) if isinstance(sec.get(k), dict) else {} for k in ("seeds", "B"))
        others = [v for k, v in draws.items() if k != "H1"]
        said = [("seeds.base", seeds.get("base"), _units_SEED_BASE),
                ("seeds.by_model", seeds.get("by_model"), {mid: _units_SEED_BASE + 500 + k for k, mid in enumerate(_units_MODELS)}),
                ("B of H1", draws.get("H1"), _units_B_HEADLINE), ("B of the others", others, [_units_B_OTHERS] * max(len(others), 1)),
                ("gates", sec.get("gates"), len(gates)), ("gates_passed", sec.get("gates_passed"), sum(1 for r in gates if r.get("pass") == "yes"))]
    _units_hold("gap.provenance.json, the section of this step (08_build_gap_units): seeds.base is 20261010 and seeds.by_model gives each of H1 "
                "to H9, and no other, the definition's seed (the base + 500 + its place); B gives 9999 for H1 and 1999 for every other "
                "entry, of which there is at least one; gates is the number of rows of gates_phase4.csv and gates_passed the number of "
                "them whose pass is yes (the rest of the section is not read here)",
                [(k, f"{got!r}, not {want!r}", type(got) is type(want) and got == want) for k, got, want in said])


def part_units():
    """unit_history.csv, unit_history_models.csv, the saved grids and the step's gates: every figure recomputed from the inputs and compared."""
    units, order, wrong, c7 = _units_recompute()
    check("inputs of the unit tables: units.gpkg has 11,468 units, none twice, each an LGD panchayat unit (outside_village 0) with a district "
          "code of its own or an outside-village unit (1) with one row in outside_village_district.csv, which holds no other unit; the "
          "Odisha FRA table gives each of 30 codes one name; the rebuilt district equals the decision table's for every unit; the "
          "decision, Hansen, agreement, need and CoRE Stack tables each carry those units once; a band's land in 2000 is the same in the "
          "decision table and the Hansen table; every fy_work_start of allocation_by_unit_fy.csv is a financial year or NA and every "
          "unit of it is a unit; the cells of tiers.csv with loss_column 'some' are the three loss cells, every cell_2018_2025 is a cell "
          "of tiers.csv and every corestack_zone_model one of the four the agreement table uses; no district's east-coast share of N1 is "
          "within 0.000001 of 50",
          not wrong, "" if not wrong else f"{len(wrong)} things wrong, e.g. " + "; ".join(wrong[:3]))
    fits = {}                                               # filled by the check of the models, read by the check of the gates
    for name, checks, given in (("unit_history.csv", _units_check_table, (units, order, c7)),
                                ("unit_history_models.csv and unit_history_models_wcb_grids.json", _units_check_models, (units, order, fits)),
                                ("gates_phase4.csv and the step's section of gap.provenance.json", _units_check_step, (units, fits))):
        try:
            checks(*given)
        except Exception as e:                               # a table that cannot be checked to the end is a failed check, and the other is still checked
            check(f"the checks of {name} ran to their end", False, f"{type(e).__name__}: {e}")

# ---------------------------------------------------------------------------------------------------------------------
# part_rights: fra_by_district.csv, fra_summary.csv, fra_two_reports.csv, and the three files on the forest villages PDF
# (forest_villages_pdf_record.json, forest_villages_text_layer_check.csv,
# forest_villages_districts_as_the_layer_reads_them.csv); and what the step says of itself: gates_phase5.csv and its
# section of gap.provenance.json (its inputs, outputs, seeds and counts of gates; the copy of the record).
# Taken as given (another part checks it against the inputs): district_need.csv.
# Written from the definitions in the builders' docstrings; no builder was read.
# The PDF is read with the poppler tools only (pdfinfo, pdfimages -list, pdffonts, pdftotext): no page is rendered and
# no character is recognised here.
# ---------------------------------------------------------------------------------------------------------------------
_rights_SEED_BASE = 20261010               # the builders' base seed: R1 has base + 700 and base + 800, R2 base + 701 and base + 801
_rights_N_PERMUTATIONS = 99999
_rights_N_BOOTSTRAP = 9999
_rights_OWN_SEED = 773000000               # this script's own draws start here; nothing to do with the builders' seeds
_rights_OWN_BOOTSTRAPS = 20                # own bootstraps of 9,999 draws each: the first is "this script's interval",
                                           # all of them measure how far such an interval's end moves from one bootstrap to the next
_rights_FRA_DISTRICT = "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"
_rights_FRA_NATIONAL = "00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv"
_rights_PDF = "00_raw/01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf"
_rights_MANIFEST = "00_raw/data_manifest.csv"
_rights_MANIFEST_ITEM = "forest_villages_pdf_as_fetched"
_rights_HEADING = "List of Forest / Un-Surveyed Villages in the Districts"
_rights_PAGE_PHRASES = ("Total Number of Villages", "Revenue Villages (Surveyed")                       # either makes a page a district page
_rights_NUMBER_PHRASES = ("Total Number of Villages", "Revenue Villages (Surveyed villages)", "Settlements etc.)")   # total inhabited, revenue, "ZERO" area
_rights_RECORD_FIELDS = ["path", "bytes", "sha256", "examined", "pages", "creator", "producer", "pages_that_are_one_image", "image_pixels_per_inch", "pages_rotated",
                         "fonts_named_in_the_file", "characters_of_text_in_the_file", "poppler", "summary_page", "summary_rows_read", "summary_rows_that_add_up",
                         "summary_rows_that_do_not", "printed_total_row_read", "zero_area_villages_summed_over_the_rows_read", "districts_in_the_file", "rule", "check_a",
                         "check_b", "which_check_failed", "text_usable_for_counts", "note_from_one_page_read_by_eye", "conclusion", "checked_utc"]
_rights_LAYER_COLUMNS = ["page", "line_as_read", "label_as_read", "revenue_villages", "zero_area_villages", "total_inhabited_villages", "adds_up", "is_a_total_row"]
_rights_DISTRICT_COLUMNS = ["order_in_file", "district_page", "list_pages", "page_total_inhabited", "page_revenue_villages", "page_zero_area_villages", "page_adds_up",
                            "page_equals_a_summary_row", "rows_with_a_village_code", "rows_equal_the_page_s_zero_area_count", "serial_numbers_read", "last_serial_number_read",
                            "serial_numbers_not_read", "serial_number_1_read_more_than_once", "serial_numbers_are_1_to_the_count"]
_rights_ASKS = {   # the six parts of check (a), in the definition's words
    "a1": "every row of the summary page adds up",
    "a2": "a total row of the summary page is read, and each of its three numbers is the sum of its column",
    "a3": "every district page gives its three numbers, and they add up",
    "a4": "every district page's three numbers are those of a row of the summary page",
    "a5": "every district's rows with a village code number what its page prints for the \"ZERO\" area",
    "a6": "every district's serial numbers are exactly 1 to that count"}
_rights_RULE_A = "the district counts parsed from it equal every total and running serial number the PDF prints, exactly"     # clause (a) of the owner's rule, as the definition gives it


def _rights_fr(cell):
    """A cell as an exact fraction."""
    from fractions import Fraction
    return Fraction(D(cell))


def _rights_round(x, places):
    """A fraction rounded half up to `places` decimals, exactly; a tie goes away from zero, as decimal.ROUND_HALF_UP. A Decimal."""
    n = x * 10 ** places
    a = abs(n)
    k = a.numerator // a.denominator
    if 2 * (a - k) >= 1:
        k += 1
    return Decimal(-k if n < 0 else k).scaleb(-places)


def _rights_number(cell, exact):
    """True where a cell is a number equal to the exact value ('12.5' equals '12.50'); False for a blank, for text, and for a number with white space around it."""
    try:
        return cell not in ("", None) and cell == cell.strip() and _rights_fr(cell) == exact
    except Exception:
        return False


def _rights_printed(cell, exact, places):
    """True where a cell prints `places` decimals and is the exact value rounded half up to them; where exact is None, where the cell is blank."""
    if exact is None:
        return cell == ""
    try:
        d = D(cell)
    except Exception:
        return False
    return cell == cell.strip() and d.is_finite() and -d.as_tuple().exponent == places and d == _rights_round(exact, places)


def _rights_show(exact, places=None):
    """An expected value as text for a check's detail."""
    if exact is None:
        return ""
    if places is not None:
        return str(_rights_round(exact, places))
    return str(exact.numerator) if exact.denominator == 1 else str(float(exact))


def _rights_header(name):
    """The header of a table of the folder being checked: its column names as written, a name written twice staying twice."""
    with open(GAP / name, encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def _rights_ragged(rws):
    """How many rows of a table do not have exactly the header's cells."""
    return sum(1 for r in rws if None in r or any(v is None for v in r.values()))


def _rights_whole(rws):
    """The rows with a missing cell, or a column the header lacks, read as blank, and cells beyond the header dropped: a ragged row or a lost column then fails its checks instead of stopping the part."""
    from collections import defaultdict
    return [defaultdict(str, {k: ("" if v is None else v) for k, v in r.items() if k is not None}) for r in rws]


def _rights_codes(values):
    """Each exact value's place among the sorted distinct values, and how many distinct values there are: equal values share a place, so a tie is exact."""
    place = {v: i for i, v in enumerate(sorted(set(values)))}
    return np.array([place[v] for v in values], dtype=np.int64), len(place)


def _rights_twice_ranks(codes, m):
    """Twice the average rank of every entry within its row: 2 x (entries of the row below it) + (entries equal to it) + 1. Whole numbers.

    `codes` holds whole numbers from 0 to m - 1, one row per sample."""
    rws = codes.reshape(-1, codes.shape[-1])
    counts = np.bincount((rws + m * np.arange(len(rws))[:, None]).ravel(), minlength=len(rws) * m).reshape(len(rws), m)
    below = np.cumsum(counts, axis=1) - counts
    return (2 * np.take_along_axis(below, rws, 1) + np.take_along_axis(counts, rws, 1) + 1).reshape(codes.shape)


def _rights_spearman(xs, ys, seed, n_permutations, n_bootstrap, n_bootstraps):
    """Spearman's rho with average ranks for ties, and this script's own permutation p and bootstrap intervals.

    Ranks are made from exact values. With A and B twice the average ranks, sum(A) = sum(B) = n(n + 1), so the centred
    cross product is T = sum(A * B) - n(n + 1)^2, a whole number, and rho = T / sqrt(SA * SB) with SA, SB the centred
    sums of squares. A shuffle of y against x keeps SA and SB, so its |rho| is at least the observed |rho| exactly
    when its |T| is at least the observed |T|: that comparison is made in whole numbers.
      p         (1 + shuffles with |rho| at least the observed) / (1 + n_permutations), two-sided
      intervals n_bootstraps of them; each from n_bootstrap draws of the pairs with replacement, ranks made afresh in
                every draw; the 2.5th and 97.5th percentiles of the rho of the draws in which rho is defined
    Returns rho, p and the intervals (one row each: lower end, upper end).
    """
    cx, mx = _rights_codes(xs)
    cy, my = _rights_codes(ys)
    n = len(xs)
    c = n * (n + 1) ** 2
    A, B = _rights_twice_ranks(cx, mx), _rights_twice_ranks(cy, my)
    T, SA, SB = int((A * B).sum()) - c, int((A * A).sum()) - c, int((B * B).sum()) - c
    rho = T / math.sqrt(SA * SB) if SA > 0 and SB > 0 else float("nan")
    rng = np.random.default_rng(seed)
    shuffled = rng.permuted(np.tile(B, (n_permutations, 1)), axis=1)
    p = (1 + int((np.abs(shuffled @ A - c) >= abs(T)).sum())) / (1 + n_permutations)
    intervals = []
    for _ in range(n_bootstraps):
        draw = rng.integers(0, n, size=(n_bootstrap, n))
        Ab, Bb = _rights_twice_ranks(cx[draw], mx), _rights_twice_ranks(cy[draw], my)
        Tb, SAb, SBb = (Ab * Bb).sum(1) - c, (Ab * Ab).sum(1) - c, (Bb * Bb).sum(1) - c
        ok = (SAb > 0) & (SBb > 0)
        intervals.append(np.percentile(Tb[ok] / np.sqrt(SAb[ok].astype(float) * SBb[ok].astype(float)), [2.5, 97.5]))
    return rho, p, np.array(intervals)


def _rights_chance_constant(values):
    """The exact chance that a sample of len(values) of the values, drawn with replacement, is constant: rho is then not defined."""
    from collections import Counter
    from fractions import Fraction
    n = len(values)
    return sum(Fraction(k, n) ** n for k in Counter(values).values())


def _rights_seeded(xs, ys, seed_permutation, seed_bootstrap, n_permutations, n_bootstrap):
    """The permutation count, the interval's two ends and the number of undefined draws, drawn with given seeds in the plainest way the definition's sentence allows.

    The definition: both use numpy.random.default_rng(seed); y is shuffled against x n_permutations times; districts are
    drawn with replacement, as pairs, n_bootstrap times; the interval is the 2.5th and 97.5th percentiles of the rho of
    the draws in which rho is defined. It does not name the generator's calls. Here: one Generator.permutation of y's
    ranks per shuffle (a shuffle of y moves its ranks with it), one Generator.integers(0, n, n) per draw, and numpy's
    default percentiles. That these are the builder's calls is an assumption of this part. The arithmetic is this
    script's own, in whole numbers, as in _rights_spearman.
    Returns (shuffles whose |rho| is at least the observed |rho|, lower end, upper end, draws in which rho is not defined)."""
    cx, mx = _rights_codes(xs)
    cy, my = _rights_codes(ys)
    n = len(xs)
    c = n * (n + 1) ** 2
    A, B = _rights_twice_ranks(cx, mx), _rights_twice_ranks(cy, my)
    T = int((A * B).sum()) - c
    rng = np.random.default_rng(seed_permutation)
    shuffled = np.array([rng.permutation(B) for _ in range(n_permutations)])
    count = int((np.abs(shuffled @ A - c) >= abs(T)).sum())
    rng = np.random.default_rng(seed_bootstrap)
    draw = np.array([rng.integers(0, n, n) for _ in range(n_bootstrap)])
    Ab, Bb = _rights_twice_ranks(cx[draw], mx), _rights_twice_ranks(cy[draw], my)
    Tb, SAb, SBb = (Ab * Bb).sum(1) - c, (Ab * Ab).sum(1) - c, (Bb * Bb).sum(1) - c
    ok = (SAb > 0) & (SBb > 0)
    if not ok.any():
        return count, None, None, int((~ok).sum())
    lo, hi = np.percentile(Tb[ok] / np.sqrt(SAb[ok].astype(float) * SBb[ok].astype(float)), [2.5, 97.5])
    return count, float(lo), float(hi), int((~ok).sum())


def _rights_tool(*args):
    """What a poppler tool prints, as text. Nothing is written: pdftotext is given '-' and pdfimages only lists."""
    import subprocess
    done = subprocess.run([str(a) for a in args], capture_output=True, timeout=300)
    if done.returncode != 0:
        raise RuntimeError(f"{args[0]} ended with status {done.returncode}: {done.stderr.decode('utf-8', 'replace')[:200]}")
    return done.stdout.decode("utf-8", errors="replace")


def _rights_registered(manifest, dest, size, digest):
    """The rows of the manifest that name a file (dest) with its exact size (bytes, marked exact by bytes_exact Y) and carry its SHA-256 in one of their cells."""
    return [r for r in manifest if r.get("dest") == dest and r.get("bytes") == str(size) and r.get("bytes_exact") == "Y" and any(digest in (v or "") for v in r.values() if isinstance(v, str))]


def _rights_summary_row(line):
    """A line of the summary page as a row of its table, or None. `line` has its white space collapsed to single spaces.

    The definition: a row is a line that ends in three whole numbers, with nothing but white space and marks between them.
    Here: the line's last character is a digit, and no letter stands between its last three runs of digits.
    Returns (label, first, second, third): the label is what stands before the first of the three numbers."""
    import re
    found = list(re.finditer(r"[0-9]+", line))
    if len(found) < 3 or found[-1].end() != len(line):
        return None
    a, b, c = found[-3:]
    if any(ch.isalnum() for ch in line[a.end():b.start()] + line[b.end():c.start()]):
        return None
    return line[:a.start()].strip(), int(a.group()), int(b.group()), int(c.group())


def _rights_is_total(label):
    """True where a row's label has the word 'total', in capitals or not."""
    return "total" in label.lower()


def _rights_figures(read):
    """The record's five figures of the summary page from rows read: `read` is a list of (line, (label, first, second, third)) in the page's order.

    Rows read; rows whose first two numbers add to the third; the lines of those that do not; total rows read; the
    middle column summed over the rows read that are not total rows (the sum of the column, as part a2 of check (a)
    means it: a total row is what that sum is held against, and is not in it)."""
    return (len(read), sum(1 for x in read if x[1][1] + x[1][2] == x[1][3]), [x[0] for x in read if x[1][1] + x[1][2] != x[1][3]],
            sum(1 for x in read if _rights_is_total(x[1][0])), sum(x[1][2] for x in read if not _rights_is_total(x[1][0])))


def _rights_total_part(read):
    """Part a2 of check (a) from rows read, as (holds in, of): a total row is read, and each of its three numbers is the sum of its column.

    Asked of each total row read; the sum of a column is taken over the rows that are not total rows. Where no total
    row is read it is asked once, of the page, and does not hold: (0, 1)."""
    totals = [x[1] for x in read if _rights_is_total(x[1][0])]
    sums = tuple(sum(x[1][i] for x in read if not _rights_is_total(x[1][0])) for i in (1, 2, 3))
    return (sum(1 for t in totals if t[1:] == sums), len(totals)) if totals else (0, 1)


def _rights_number_after(text, phrase):
    """The whole number that follows `phrase` in a page's text, marks between; None where the phrase or the number cannot be found.

    From the first place the phrase stands, everything that is neither a letter nor a digit is passed over (marks, and
    white space of any kind: the layer can put the number on the next line); the run of digits met there is the number.
    If a letter is met first, or the text ends, there is none."""
    at = text.find(phrase)
    if at < 0:
        return None
    start = at + len(phrase)
    while start < len(text) and not text[start].isalnum():
        start += 1
    end = start
    while end < len(text) and text[end] in "0123456789":
        end += 1
    return int(text[start:end]) if end > start else None


def _rights_serial(line):
    """The serial number a line of a list begins with, or None.

    The definition: a whole number from 1 to 999 that begins a line (marks before it apart) and is followed by nothing,
    by a village code, or by a word with a letter in it, on a line without the word "Total". Here: the number is the
    first run of digits of the line, with nothing but white space and marks before it; what follows it is the rest of
    the line cut at white space, so the word that follows may be joined to the number ('4-B4iipada' gives 4, the word
    being '-B4iipada'; '3_' gives none, the word '_' having no letter)."""
    import re
    if "Total" in line:
        return None
    start = 0
    while start < len(line) and not line[start].isalnum():
        start += 1
    end = start
    while end < len(line) and line[end] in "0123456789":
        end += 1
    if end == start or not 1 <= int(line[start:end]) <= 999:
        return None
    words = line[end:].split()
    if not words or re.fullmatch(r"[0-9]{8}", words[0]) or any(ch.isalpha() for ch in words[0]):
        return int(line[start:end])
    return None


def _rights_read_layer(pages):
    """The forest villages file as its text layer reads, by the definition's rules. `pages` holds the text of each page (pdftotext -layout, one page at a time).

    Returns a dict:
      summary_page   the first of the first six pages whose text, white space collapsed, has the heading; None if none has
      rows           the rows of that page, in its order: (line with its white space collapsed, (label, first, second, third))
      districts      one dict per district, in the file's order, with the 15 cells of the districts table as text
      parts          the six parts of check (a): {"a1": (holds in, of), ...}
    A district is a district page and the pages after it up to the next district page; its list pages are those of its
    pages that hold a village code (a run of exactly eight digits); a row of its list is a line of its pages that holds
    one; serial numbers are read on the lines of its list pages."""
    import re
    code = re.compile(r"(?<![0-9])[0-9]{8}(?![0-9])")
    summary_page = next((j + 1 for j, text in enumerate(pages[:6]) if _rights_HEADING in " ".join(text.split())), None)
    rows_read = []
    if summary_page is not None:
        for ln in pages[summary_page - 1].split("\n"):
            line = " ".join(ln.split())
            parsed = _rights_summary_row(line)
            if parsed is not None:
                rows_read.append((line, parsed))
    triples = {(r[1][1], r[1][2], r[1][3]) for r in rows_read}                    # (revenue, "ZERO" area, total inhabited) of every row read
    district_pages = [j + 1 for j, text in enumerate(pages) if any(ph in text for ph in _rights_PAGE_PHRASES)]
    districts, held_in = [], {"a3": 0, "a4": 0, "a5": 0, "a6": 0}
    for k, first in enumerate(district_pages):
        last = district_pages[k + 1] - 1 if k + 1 < len(district_pages) else len(pages)
        own = list(range(first, last + 1))
        total, revenue, zero = (_rights_number_after(pages[first - 1], ph) for ph in _rights_NUMBER_PHRASES)
        list_pages = [p for p in own if code.search(pages[p - 1])]
        n_rows = sum(1 for p in own for ln in pages[p - 1].split("\n") if code.search(ln))
        serials = [s for s in (_rights_serial(ln) for p in list_pages for ln in pages[p - 1].split("\n")) if s is not None]
        distinct = sorted(set(serials))
        full = None not in (total, revenue, zero)
        adds_up = full and revenue + zero == total
        in_summary = full and (revenue, zero, total) in triples
        rows_equal = zero is not None and n_rows == zero
        one_to_count = zero is not None and distinct == list(range(1, zero + 1))
        for part, holds in (("a3", adds_up), ("a4", in_summary), ("a5", rows_equal), ("a6", one_to_count)):
            held_in[part] += 1 if holds else 0
        yes_no = lambda known, value: "" if not known else "yes" if value else "no"
        districts.append({
            "order_in_file": str(k + 1), "district_page": str(first), "list_pages": " ".join(str(p) for p in list_pages),
            "page_total_inhabited": "" if total is None else str(total), "page_revenue_villages": "" if revenue is None else str(revenue),
            "page_zero_area_villages": "" if zero is None else str(zero),
            "page_adds_up": yes_no(full, adds_up), "page_equals_a_summary_row": yes_no(full, in_summary),
            "rows_with_a_village_code": str(n_rows), "rows_equal_the_page_s_zero_area_count": yes_no(zero is not None, rows_equal),
            "serial_numbers_read": str(len(distinct)), "last_serial_number_read": str(distinct[-1]) if distinct else "",
            "serial_numbers_not_read": "" if zero is None else " ".join(str(n) for n in range(1, zero + 1) if n not in distinct),
            "serial_number_1_read_more_than_once": "yes" if serials.count(1) > 1 else "no",
            "serial_numbers_are_1_to_the_count": "yes" if one_to_count else "no"})
    figures = _rights_figures(rows_read)
    parts = {"a1": (figures[1], figures[0]), "a2": _rights_total_part(rows_read)}
    parts.update({part: (held_in[part], len(districts)) for part in ("a3", "a4", "a5", "a6")})
    return {"summary_page": summary_page, "rows": rows_read, "districts": districts, "parts": parts}


def part_rights():
    import datetime
    import hashlib
    import re
    import shutil
    import subprocess
    from collections import Counter
    from fractions import Fraction

    fr, number, printed, show = _rights_fr, _rights_number, _rights_printed, _rights_show

    def held(what, ok, detail):
        """A check whose account of what was found is printed only when it fails."""
        check(what, ok, "" if ok else detail)

    # ------------------------------------------------------------------ what is taken as given, and the inputs
    need_rows = table("district_need.csv")
    need = {r["pc11_district_code"]: r for r in need_rows}
    held("rights, what is taken as given: district_need.csv holds 30 census district codes, once each (another part checks its figures against the inputs)",
         len(need_rows) == len(need) == 30, f"{len(need_rows)} rows, {len(need)} codes")
    codes = sorted(need, key=int)
    name = {k: need[k]["district_name"] for k in codes}
    fra = rows(_rights_FRA_DISTRICT)
    fk = {r["pc11_district_code"]: r for r in fra}
    held("the Odisha FRA report by district (00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv): 30 rows, one for each census district code of district_need.csv, each under the name district_need.csv gives that code",
         len(fra) == len(fk) == 30 and set(fk) == set(need) and all(fk[k]["district"] == name[k] for k in codes),
         f"{len(fra)} rows, {len(fk)} codes; codes in one and not the other: {sorted(set(fk) ^ set(need))}; names that differ: {[(k, fk[k]['district'], name[k]) for k in codes if k in fk and fk[k]['district'] != name[k]][:5]}")
    X = {}
    for k in codes:
        a = fk[k]
        x = dict(titles=fr(a["titles_distributed_comm_st"]) + fr(a["titles_distributed_comm_otfd"]), extent=fr(a["extent_ha_comm_st"]) + fr(a["extent_ha_comm_otfd"]),
                 f2000=fr(need[k]["forest_2000_ha"]), n1=fr(need[k]["n1_ha_2018_2025"]), start=fr(need[k]["forest_at_window_start_ha_2018_2025"]))
        x["pct"], x["per100"] = 100 * x["extent"] / x["f2000"], 100 * x["n1"] / x["start"]
        X[k] = x

    # ================================================================== fra_by_district.csv
    fb_raw = table("fra_by_district.csv")
    fb = _rights_whole(fb_raw)
    cols = ["pc11_district_code", "district_name", "community_titles_distributed", "community_extent_ha", "forest_2000_ha", "community_extent_pct_of_forest_2000", "extent_is",
            "n1_ha_2018_2025", "forest_at_window_start_ha_2018_2025", "n1_per_100_ha_of_forest_at_window_start"]
    keys = [r.get("pc11_district_code") for r in fb]
    head = _rights_header("fra_by_district.csv")
    held("fra_by_district.csv: the 10 columns this part checks, each once, and no other; 30 rows, one for each census district code of district_need.csv, none twice and none ragged, in the order of the codes",
         sorted(head) == sorted(cols) and keys == codes and not _rights_ragged(fb_raw),
         f"{len(fb)} rows, {_rights_ragged(fb_raw)} ragged, {len(set(keys))} distinct codes, {len(set(codes) - set(keys))} missing, {len(set(keys) - set(codes))} not expected, in order: {keys == codes}; columns {head}")
    ft = {}
    for r in fb:
        ft.setdefault(r.get("pc11_district_code"), r)
    blank = {c: "" for c in cols}

    def cell(k, col):
        return ft[k][col] if k in ft else "(no row)"

    pairs = [(k, tuple(cell(k, x) for x in ("district_name", "community_titles_distributed", "community_extent_ha")), (name[k], show(X[k]["titles"]), show(X[k]["extent"])),
              ft.get(k, blank)["district_name"] == name[k] and ft.get(k, blank)["community_titles_distributed"] == show(X[k]["titles"]) and number(ft.get(k, blank)["community_extent_ha"], X[k]["extent"])) for k in codes]
    check("fra_by_district.csv: district_name is the district's name in district_need.csv; community_titles_distributed is titles_distributed_comm_st + titles_distributed_comm_otfd, a whole number, and community_extent_ha is extent_ha_comm_st + extent_ha_comm_otfd, as a number, of the district's row in the Odisha FRA report",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = [(k, tuple(cell(k, x) for x in ("forest_2000_ha", "n1_ha_2018_2025", "forest_at_window_start_ha_2018_2025")), (show(X[k]["f2000"]), show(X[k]["n1"]), show(X[k]["start"])),
              number(ft.get(k, blank)["forest_2000_ha"], X[k]["f2000"]) and number(ft.get(k, blank)["n1_ha_2018_2025"], X[k]["n1"]) and number(ft.get(k, blank)["forest_at_window_start_ha_2018_2025"], X[k]["start"])) for k in codes]
    check("fra_by_district.csv: forest_2000_ha, n1_ha_2018_2025 and forest_at_window_start_ha_2018_2025 equal, as numbers, the columns of those names in district_need.csv",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = [(k, (cell(k, "community_extent_pct_of_forest_2000"), cell(k, "n1_per_100_ha_of_forest_at_window_start")), (show(X[k]["pct"], 6), show(X[k]["per100"], 6)),
              printed(ft.get(k, blank)["community_extent_pct_of_forest_2000"], X[k]["pct"], 6) and printed(ft.get(k, blank)["n1_per_100_ha_of_forest_at_window_start"], X[k]["per100"], 6)) for k in codes]
    check("fra_by_district.csv: community_extent_pct_of_forest_2000 is 100 x community_extent_ha / forest_2000_ha and n1_per_100_ha_of_forest_at_window_start is 100 x n1_ha_2018_2025 / forest_at_window_start_ha_2018_2025, exact, rounded half up to the 6 decimals printed",
          all(p[3] for p in pairs), mismatches(pairs))

    fs_raw = table("fra_summary.csv")
    fs = _rights_whole(fs_raw)
    labels = sorted({r.get("extent_is", "") for r in fb} | {r.get("extent_is", "") for r in fs})
    held("fra_by_district.csv and fra_summary.csv: extent_is is one label, the same on every row of both tables; it says the extent is 'not an overlap', that 'titles are not mapped', and that 'community' takes in both CR and CFR (key words of the definition's sentence; its full wording is not tested)",
         bool(fb) and bool(fs) and len(labels) == 1 and "not an overlap" in labels[0].lower() and "titles are not mapped" in labels[0].lower()
         and re.search(r"\bCR\b", labels[0]) is not None and re.search(r"\bCFR\b", labels[0]) is not None,
         f"labels found: {labels}")

    # ================================================================== fra_summary.csv
    scols = ["id", "what", "x", "y", "n_districts", "rho", "p_permutation", "ci95_lo", "ci95_hi", "n_permutations", "n_bootstrap", "n_bootstrap_undefined", "seed_permutation",
             "seed_bootstrap", "extent_is"]
    defs = {"R1": ("community_extent_ha", "n1_ha_2018_2025", [X[k]["extent"] for k in codes], [X[k]["n1"] for k in codes]),
            "R2": ("community_extent_pct_of_forest_2000", "n1_per_100_ha_of_forest_at_window_start", [X[k]["pct"] for k in codes], [X[k]["per100"] for k in codes])}
    ids = list(defs)
    st = {}
    for r in fs:
        st.setdefault(r.get("id"), r)
    sblank = {c: "" for c in scols}

    def scell(i, col):
        return st[i][col] if i in st else "(no row)"

    head = _rights_header("fra_summary.csv")
    held("fra_summary.csv: the 15 columns this part checks, each once, and no other; 2 rows, R1 then R2, none ragged; x and y name the two columns of fra_by_district.csv that the specification gives each (R1: community_extent_ha, n1_ha_2018_2025; R2: community_extent_pct_of_forest_2000, n1_per_100_ha_of_forest_at_window_start); n_districts is 30; what is not blank and speaks of 'per 100 ha' in R2 and not in R1 (its full wording is not in the specification)",
         sorted(head) == sorted(scols) and [r.get("id") for r in fs] == ids and not _rights_ragged(fs_raw)
         and all((st[i]["x"], st[i]["y"], st[i]["n_districts"]) == (defs[i][0], defs[i][1], str(len(codes))) and st[i]["what"].strip() != "" and ("per 100 ha" in st[i]["what"]) == (i == "R2") for i in ids),
         f"{len(fs)} rows, {_rights_ragged(fs_raw)} ragged: {[(r.get('id'), r.get('x'), r.get('y'), r.get('n_districts'), r.get('what')) for r in fs]}; columns {head}")

    own = {i: _rights_spearman(defs[i][2], defs[i][3], _rights_OWN_SEED + j, _rights_N_PERMUTATIONS, _rights_N_BOOTSTRAP, _rights_OWN_BOOTSTRAPS) for j, i in enumerate(ids)}

    def number_or_none(text):
        try:
            return float(text) if math.isfinite(float(text)) else None
        except Exception:
            return None

    pairs = [(i, scell(i, "rho"), f"{own[i][0]:.9f}", number_or_none(st.get(i, sblank)["rho"]) is not None and abs(number_or_none(st.get(i, sblank)["rho"]) - own[i][0]) <= 5.0e-7 + 1e-12) for i in ids]
    check("fra_summary.csv: rho is Spearman's rho over the 30 districts (the Pearson correlation of average ranks; ranks made from the exact values, ties sharing the average rank) - R1: community extent in hectares against N1 of 2018-2025; R2: that extent per 100 ha of the forest of 2000 against N1 per 100 ha of forest at the start of the window, both unrounded - to the 6 decimals printed: |table - recomputed| <= 0.0000005",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs, sharp, whole, far = [], [], [], 0.0
    for i in ids:
        pt, po = number_or_none(st.get(i, sblank)["p_permutation"]), own[i][1]
        pairs.append((i, scell(i, "p_permutation"), f"{po:.5f}", pt is not None and abs(pt - po) <= 0.01))
        se = 0.0 if pt is None or not 0 <= pt <= 1 else math.sqrt((pt * (1 - pt) + po * (1 - po)) / (1 + _rights_N_PERMUTATIONS))
        sharp.append((i, scell(i, "p_permutation"), f"{po:.5f} (allowed difference {6 * se + 0.00002:.5f})", pt is not None and abs(pt - po) <= 6 * se + 0.00002))
        count = None if pt is None else pt * (1 + _rights_N_PERMUTATIONS)
        whole.append((i, scell(i, "p_permutation"), "(1 + a count) / 100000", count is not None and abs(count - round(count)) < 1e-6 and 1 <= round(count) <= 1 + _rights_N_PERMUTATIONS))
        far = max(far, abs(pt - po)) if pt is not None else far
    check("fra_summary.csv: p_permutation is within 0.01 of this script's own two-sided permutation p (99,999 shuffles of y against x with this script's own seeds; p = (1 + shuffles whose |rho| is at least the observed |rho|) / (1 + shuffles))",
          all(p[3] for p in pairs), mismatches(pairs) or f"largest |difference| {far:.5f}")
    check("fra_summary.csv: p_permutation is also within six Monte Carlo standard errors of that own p: |difference| <= 6 x sqrt((p(1 - p) + p'(1 - p')) / 100000) + 0.00002, p and p' the table's value and this script's",
          all(p[3] for p in sharp), mismatches(sharp))
    check("fra_summary.csv: p_permutation x 100,000 is a whole number from 1 to 100,000, as (1 + a count of shuffles) / (1 + 99,999) must be",
          all(p[3] for p in whole), mismatches(whole))

    pairs, sharp, far, z = [], [], 0.0, 0.0
    for i in ids:
        t, ivs = st.get(i, sblank), own[i][2]
        lo, hi = number_or_none(t["ci95_lo"]), number_or_none(t["ci95_hi"])
        pairs.append((i, (scell(i, "ci95_lo"), scell(i, "ci95_hi")), (f"{ivs[0, 0]:.6f}", f"{ivs[0, 1]:.6f}"),
                      lo is not None and hi is not None and abs(lo - ivs[0, 0]) <= 0.04 and abs(hi - ivs[0, 1]) <= 0.04 and lo <= hi))
        mean, sd = ivs.mean(0), ivs.std(0, ddof=1)
        sharp.append((i, (scell(i, "ci95_lo"), scell(i, "ci95_hi")), (f"{mean[0]:.6f} +/- {6 * sd[0] + 0.000001:.6f}", f"{mean[1]:.6f} +/- {6 * sd[1] + 0.000001:.6f}"),
                      lo is not None and hi is not None and abs(lo - mean[0]) <= 6 * sd[0] + 0.000001 and abs(hi - mean[1]) <= 6 * sd[1] + 0.000001))
        z = max(z, abs(lo - mean[0]) / sd[0] if lo is not None and sd[0] > 0 else 0.0, abs(hi - mean[1]) / sd[1] if hi is not None and sd[1] > 0 else 0.0)
        if lo is not None and hi is not None:
            far = max(far, abs(lo - ivs[0, 0]), abs(hi - ivs[0, 1]))
    check("fra_summary.csv: ci95_lo and ci95_hi are each within 0.04 of this script's own percentile bootstrap interval (9,999 draws of the districts with replacement, as pairs, with this script's own seed; ranks made afresh in every draw; the 2.5th and 97.5th percentiles of the rho of the draws), and ci95_lo <= ci95_hi",
          all(p[3] for p in pairs), mismatches(pairs) or f"largest |difference| {far:.4f}")
    check(f"fra_summary.csv: ci95_lo and ci95_hi are also each within six standard deviations of the mean of that end over {_rights_OWN_BOOTSTRAPS} own bootstraps of 9,999 draws, the standard deviation being that of the end across those {_rights_OWN_BOOTSTRAPS} (how far an honest interval's end moves from one bootstrap to the next), plus 0.000001 for the decimals printed",
          all(p[3] for p in sharp), mismatches(sharp) or f"the end furthest from its mean is {z:.2f} standard deviations away")

    pairs = []
    for j, i in enumerate(ids):
        t = st.get(i, sblank)
        count, s_lo, s_hi, s_undefined = _rights_seeded(defs[i][2], defs[i][3], _rights_SEED_BASE + 700 + j, _rights_SEED_BASE + 800 + j, _rights_N_PERMUTATIONS, _rights_N_BOOTSTRAP)
        try:
            p_exact = D(t["p_permutation"]) * (1 + _rights_N_PERMUTATIONS) == 1 + count
        except Exception:
            p_exact = False
        e_lo, e_hi = number_or_none(t["ci95_lo"]), number_or_none(t["ci95_hi"])
        pairs.append((i, tuple(scell(i, x) for x in ("p_permutation", "ci95_lo", "ci95_hi", "n_bootstrap_undefined")),
                      (f"{(1 + count) / (1 + _rights_N_PERMUTATIONS):.5f}", "" if s_lo is None else f"{s_lo:.6f}", "" if s_hi is None else f"{s_hi:.6f}", str(s_undefined)),
                      p_exact and None not in (e_lo, e_hi, s_lo, s_hi) and abs(e_lo - s_lo) <= 5.0e-7 + 1e-12 and abs(e_hi - s_hi) <= 5.0e-7 + 1e-12 and t["n_bootstrap_undefined"] == str(s_undefined)))
    check("fra_summary.csv, drawn again with the seeds the definition gives (20261010 + 700 and + 800 for R1, + 701 and + 801 for R2) and numpy.random.default_rng, in the plainest way its sentence allows - one Generator.permutation of y per shuffle, one Generator.integers(0, 30, 30) per draw of the districts, numpy's default percentiles; the arithmetic this script's own: "
          "p_permutation is (1 + the number of those 99,999 shuffles whose |rho| is at least the observed |rho|) / 100,000, exactly; ci95_lo and ci95_hi are the 2.5th and 97.5th percentiles of the rho of those 9,999 draws to the 6 decimals printed (|table - recomputed| <= 0.0000005); "
          "n_bootstrap_undefined is the number of those draws in which rho is not defined. The definition does not name the generator's calls: that these are the builder's is this part's assumption, and the checks above, with this script's own draws, do not rest on it",
          all(p[3] for p in pairs), mismatches(pairs))

    pairs = []
    for j, i in enumerate(ids):
        t = st.get(i, sblank)
        expected_undefined = _rights_N_BOOTSTRAP * (_rights_chance_constant(defs[i][2]) + _rights_chance_constant(defs[i][3]))
        und = t["n_bootstrap_undefined"]
        ok_und = und.isascii() and und.isdigit() and int(und) <= _rights_N_BOOTSTRAP and (int(und) == 0 or expected_undefined >= Fraction(1, 10 ** 6))
        exp = (str(_rights_N_PERMUTATIONS), str(_rights_N_BOOTSTRAP), str(_rights_SEED_BASE + 700 + j), str(_rights_SEED_BASE + 800 + j),
               "0" if expected_undefined < Fraction(1, 10 ** 6) else f"a whole number from 0 to {_rights_N_BOOTSTRAP}")
        got = tuple(scell(i, x) for x in ("n_permutations", "n_bootstrap", "seed_permutation", "seed_bootstrap", "n_bootstrap_undefined"))
        pairs.append((i, got, exp, got[:4] == exp[:4] and ok_und))
    check("fra_summary.csv: n_permutations is 99999 and n_bootstrap 9999; seed_permutation and seed_bootstrap are 20261010 + 700 and 20261010 + 800 for R1, 20261010 + 701 and 20261010 + 801 for R2; "
          "n_bootstrap_undefined is a whole number from 0 to n_bootstrap, and 0 wherever the exact chance of a constant resample of either side puts the expected number of undefined draws below one in a million",
          all(p[3] for p in pairs), mismatches(pairs))

    # ================================================================== fra_two_reports.csv
    two_raw = table("fra_two_reports.csv")
    two = _rights_whole(two_raw)
    tcols = ["report", "community_titles_distributed", "community_extent_ha", "extent_difference_pct_of_state"]
    national = [r for r in rows(_rights_FRA_NATIONAL) if r["state"].strip() == "Odisha"]
    iso = re.search(r"\d{4}-\d\d-\d\d", _rights_FRA_DISTRICT).group()                 # the date in the district file's name ...
    day = "-".join(reversed(iso.split("-")))                                         # ... as the reports write it: 31-12-2025
    said = [(r.get("report") or "") for r in two] + ["", "", ""]
    head = _rights_header("fra_two_reports.csv")
    held(f"fra_two_reports.csv: the 4 columns this part checks, each once, and no other; 3 rows, none ragged - the first names the state's report and says the district table is summed, the second names the Ministry of Tribal Affairs and Odisha's row, both give the date {day} (the date in the two files' names), and the third is the difference, 'state less national' (key words; the full wording is not in the specification)",
         sorted(head) == sorted(tcols) and len(two) == 3 and not _rights_ragged(two_raw)
         and "state" in said[0].lower() and "summed" in said[0].lower() and "ministry" not in said[0].lower()
         and "ministry of tribal affairs" in said[1].lower() and "odisha" in said[1].lower()
         and day in said[0] and day in said[1] and iso in _rights_FRA_NATIONAL
         and "difference" in said[2].lower() and "state less national" in said[2].lower(),
         f"{len(two)} rows, {_rights_ragged(two_raw)} ragged: {said[:3]}; columns {head}")
    state_titles, state_extent = sum(X[k]["titles"] for k in codes), sum(X[k]["extent"] for k in codes)
    if len(national) != 1 or len(two) != 3:
        check("fra_two_reports.csv: the three rows' figures against the two FRA files", False,
              f"NOT COMPARED: the national file has {len(national)} rows for Odisha (one is needed) and the table has {len(two)} rows (three are needed)")
    else:
        nat_titles, nat_extent = fr(national[0]["titles_distributed_community"]), fr(national[0]["extent_ha_community"])
        expected = [(state_titles, state_extent, None), (nat_titles, nat_extent, None), (state_titles - nat_titles, state_extent - nat_extent, 100 * (state_extent - nat_extent) / state_extent)]
        pairs = [(said[j][:40], (two[j]["community_titles_distributed"], two[j]["community_extent_ha"], two[j]["extent_difference_pct_of_state"]), (show(e[0]), show(e[1]), show(e[2], 2)),
                  two[j]["community_titles_distributed"] == show(e[0]) and number(two[j]["community_extent_ha"], e[1]) and printed(two[j]["extent_difference_pct_of_state"], e[2], 2)) for j, e in enumerate(expected)]
        check("fra_two_reports.csv: the state row holds the exact sums over the 30 districts of the Odisha FRA report of community titles (comm_st + comm_otfd) and of community extent; the national row holds titles_distributed_community and extent_ha_community of Odisha's one row in 00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv; "
              "the third row is state less national; titles are compared as the whole numbers they are and extents as numbers; extent_difference_pct_of_state is 100 x the difference in extent / the state's extent, exact, rounded half up to the 2 decimals printed, and blank in the first two rows",
              all(p[3] for p in pairs), mismatches(pairs))

    # ================================================================== the forest villages PDF: the record and its two tables
    rec = json.loads((GAP / "forest_villages_pdf_record.json").read_text(encoding="utf-8"))
    rec = rec if isinstance(rec, dict) else {}
    pdf = ROOT / _rights_PDF
    data = pdf.read_bytes() if pdf.exists() else None
    digest = None if data is None else hashlib.sha256(data).hexdigest()
    held("forest_villages_pdf_record.json: the 28 fields this part checks and no other; path is 00_raw/01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf, and bytes and sha256 are those of that file on disk",
         data is not None and sorted(rec.keys()) == sorted(_rights_RECORD_FIELDS) and rec.get("path") == _rights_PDF and type(rec.get("bytes")) is int and rec.get("bytes") == len(data) and rec.get("sha256") == digest,
         "the PDF is not on disk" if data is None else f"fields lacking {sorted(set(_rights_RECORD_FIELDS) - set(rec))}, not expected {sorted(set(rec) - set(_rights_RECORD_FIELDS))}; path {rec.get('path')!r}; bytes: record {rec.get('bytes')!r}, file {len(data)}; sha256: record {rec.get('sha256')!r}, file {digest}")

    manifest = rows(_rights_MANIFEST)
    dest = _rights_PDF.split("/", 1)[1]                                               # the manifest writes a file's place within 00_raw/
    naming = [r for r in manifest if r.get("dest") == dest]
    exact = [] if data is None else _rights_registered(manifest, dest, len(data), digest)
    held("00_raw/data_manifest.csv: one row, and only one, names the PDF (dest 01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf) with the size of the file on disk, marked exact (bytes_exact Y), and carries the file's SHA-256 in one of its cells; that row is the item forest_villages_pdf_as_fetched, which the definition names",
         len(exact) == 1 and exact[0].get("item_id") == _rights_MANIFEST_ITEM,
         f"rows naming the file: {[(r.get('item_id'), r.get('bytes'), r.get('bytes_exact')) for r in naming]}; of them with the exact size {None if data is None else len(data)} and the SHA-256 {digest}: {[r.get('item_id') for r in exact]}")

    tl_raw = table("forest_villages_text_layer_check.csv")
    tl = _rights_whole(tl_raw)
    lcols = _rights_LAYER_COLUMNS
    head = _rights_header("forest_villages_text_layer_check.csv")
    held("forest_villages_text_layer_check.csv: the 8 columns this part checks, each once, and no other; no row ragged; and every row on the record's summary_page",
         sorted(head) == sorted(lcols) and not _rights_ragged(tl_raw) and all(r.get("page") == str(rec.get("summary_page")) for r in tl),
         f"columns {head}; ragged rows {_rights_ragged(tl_raw)}; pages {sorted({r.get('page') for r in tl})}; summary_page {rec.get('summary_page')!r}")

    dt_raw = table("forest_villages_districts_as_the_layer_reads_them.csv")
    dt = _rights_whole(dt_raw)
    dcols = _rights_DISTRICT_COLUMNS
    head = _rights_header("forest_villages_districts_as_the_layer_reads_them.csv")
    held("forest_villages_districts_as_the_layer_reads_them.csv: the 15 columns this part checks, each once, and no other; no row ragged; order_in_file runs 1, 2, 3 ... down the rows; and the record's districts_in_the_file is the number of rows",
         sorted(head) == sorted(dcols) and not _rights_ragged(dt_raw) and [r.get("order_in_file") for r in dt] == [str(j + 1) for j in range(len(dt))]
         and type(rec.get("districts_in_the_file")) is int and rec.get("districts_in_the_file") == len(dt),
         f"columns {head}; ragged rows {_rights_ragged(dt_raw)}; order_in_file {[r.get('order_in_file') for r in dt]}; {len(dt)} rows; districts_in_the_file {rec.get('districts_in_the_file')!r}")

    def as_int(text):
        return int(text) if isinstance(text, str) and text.isascii() and text.isdigit() else None

    in_table = [(r.get("line_as_read", ""), (r.get("label_as_read", ""), as_int(r.get("revenue_villages")), as_int(r.get("zero_area_villages")), as_int(r.get("total_inhabited_villages")))) for r in tl]
    numbered = all(None not in x[1] for x in in_table)
    figures = (rec.get("summary_rows_read"), rec.get("summary_rows_that_add_up"), rec.get("summary_rows_that_do_not"), rec.get("printed_total_row_read"), rec.get("zero_area_villages_summed_over_the_rows_read"))
    whole_numbers = all(type(x) is int for x in (figures[0], figures[1], figures[3], figures[4])) and isinstance(figures[2], list)
    held("forest_villages_pdf_record.json against forest_villages_text_layer_check.csv: summary_rows_read is the table's number of rows, summary_rows_that_add_up the number whose first two numbers add to the third, summary_rows_that_do_not the lines of the others in the table's order, "
         "printed_total_row_read the number of rows whose label has the word 'total', and zero_area_villages_summed_over_the_rows_read the middle column summed over the rows that are not total rows; the four counts are whole numbers, not text",
         numbered and whole_numbers and figures == _rights_figures(in_table), f"record {figures}; from the table's rows {_rights_figures(in_table) if numbered else 'a cell that is not a whole number'}")

    # ---- check (a) as the record gives it: its form, and its six counts against the two tables
    ca = rec.get("check_a") if isinstance(rec.get("check_a"), dict) else {}
    ca_parts = [p for p in ca.get("parts", [])] if isinstance(ca.get("parts"), list) else []
    well_formed = (sorted(ca.keys()) == ["holds", "parts", "parts_that_fail"] and len(ca_parts) == 6
                   and all(isinstance(p, dict) and sorted(p.keys()) == ["asks", "holds_in", "of", "part"] and isinstance(p["part"], str)
                           and type(p["holds_in"]) is int and type(p["of"]) is int and 0 <= p["holds_in"] <= p["of"] for p in ca_parts))
    rec_parts = {p["part"]: (p["holds_in"], p["of"]) for p in ca_parts} if well_formed else {}
    rec_failing = [p["part"] for p in ca_parts if p["holds_in"] != p["of"]] if well_formed else None
    held("forest_villages_pdf_record.json, check_a, its form: the keys holds, parts and parts_that_fail and no other; parts holds a1 to a6 in that order, each with the keys part, asks, holds_in and of and no other; asks is the definition's sentence for the part, word for word; holds_in and of are whole numbers with 0 <= holds_in <= of; "
         "parts_that_fail lists, in order, the parts that do not hold in every row they are asked of, and holds is true where that list is empty and false otherwise",
         well_formed and [p["part"] for p in ca_parts] == list(_rights_ASKS) and all(" ".join(str(p["asks"]).split()) == _rights_ASKS.get(p["part"]) for p in ca_parts)
         and ca.get("parts_that_fail") == rec_failing and ca.get("holds") is (not rec_failing),
         f"check_a: {json.dumps(rec.get('check_a'), ensure_ascii=False)[:700]}")

    yes = lambda col: sum(1 for r in dt if r.get(col) == "yes")
    from_tables = {"a1": (_rights_figures(in_table)[1], len(in_table)) if numbered else None, "a2": _rights_total_part(in_table) if numbered else None,
                   "a3": (yes("page_adds_up"), len(dt)), "a4": (yes("page_equals_a_summary_row"), len(dt)),
                   "a5": (yes("rows_equal_the_page_s_zero_area_count"), len(dt)), "a6": (yes("serial_numbers_are_1_to_the_count"), len(dt))}
    held("forest_villages_pdf_record.json, check_a against the two tables: a1 holds in as many rows of forest_villages_text_layer_check.csv as add up, of all its rows; a2 holds in as many of its total rows as have each of their three numbers equal to the sum of the column over the other rows, of its total rows (0 of 1 where it has none); "
         "a3, a4, a5 and a6 hold in as many rows of forest_villages_districts_as_the_layer_reads_them.csv as say 'yes' in page_adds_up, page_equals_a_summary_row, rows_equal_the_page_s_zero_area_count and serial_numbers_are_1_to_the_count, of all its rows",
         bool(rec_parts) and rec_parts == from_tables, f"record {rec_parts}; from the tables {from_tables}")

    # ---- the owner's rule, applied to check (a) as the record gives it
    cb = rec.get("check_b") if isinstance(rec.get("check_b"), dict) else {}
    village_columns = [c for c in need_rows[0] if any(w in c.lower() for w in ("village", "habitation", "settlement"))] if need_rows else []
    rule_text = " ".join(str(rec.get("rule") or "").split())
    held("forest_villages_pdf_record.json, the owner's rule applied to the record's own check_a, which does not hold: which_check_failed is '(a)', check_b has the keys run and why and no other, with run false and why not blank, text_usable_for_counts is false, and district_need.csv has no column with 'village', 'habitation' or 'settlement' in its name "
         "(the only trace this part looks for of a count taken from the file into that table). "
         "A record in which check_a holds is failed here: by the definition the step stops then, for a reader to make check (b)",
         well_formed and ca.get("holds") is False and rec.get("which_check_failed") == "(a)" and sorted(cb.keys()) == ["run", "why"] and cb.get("run") is False and str(cb.get("why") or "").strip() != ""
         and rec.get("text_usable_for_counts") is False and not village_columns,
         f"check_a.holds {ca.get('holds')!r}; which_check_failed {rec.get('which_check_failed')!r}; check_b {rec.get('check_b')!r}; text_usable_for_counts {rec.get('text_usable_for_counts')!r}; columns of district_need.csv named for villages {village_columns}")
    note = " ".join(str(rec.get("note_from_one_page_read_by_eye") or "").split())
    held("forest_villages_pdf_record.json, its words: examined is true; rule quotes clause (a) of the definition ('the district counts parsed from it equal every total and running serial number the PDF prints, exactly') and, for clause (b), names 'five pages', 'at random', 'upright' and 'a reader'; "
         "note_from_one_page_read_by_eye is text, not blank, and says it is 'not check (b)' (key words only: what the reader saw on the page is not tested, and no page is rendered here)",
         rec.get("examined") is True and isinstance(rec.get("rule"), str) and _rights_RULE_A in rule_text and all(w in rule_text for w in ("(a)", "(b)", "five pages", "at random", "upright", "a reader"))
         and isinstance(rec.get("note_from_one_page_read_by_eye"), str) and "not check (b)" in note,
         f"examined {rec.get('examined')!r}; rule {rule_text[:160]!r}; note {note[:100]!r} ... {note[-60:]!r}")

    prov = json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8")) if (GAP / "gap.provenance.json").exists() else {}
    copy = prov.get("steps", {}).get("08_build_gap_rights", {}).get("forest_villages") if isinstance(prov, dict) else None
    try:
        a_time = isinstance(rec.get("checked_utc"), str) and datetime.datetime.strptime(rec["checked_utc"], "%Y-%m-%dT%H:%M:%SZ") is not None and len(rec["checked_utc"]) == 20
    except ValueError:
        a_time = False
    held("forest_villages_pdf_record.json: checked_utc is a date and time that exist, written as YYYY-MM-DDTHH:MM:SSZ (UTC), and the record is, field for field, the copy of it that gap.provenance.json keeps (steps > 08_build_gap_rights > forest_villages)",
         a_time and isinstance(copy, dict) and copy == rec,
         f"checked_utc {rec.get('checked_utc')!r}; fields that differ from the copy: {sorted(k for k in set(rec) | set(copy if isinstance(copy, dict) else {}) if rec.get(k) != (copy if isinstance(copy, dict) else {}).get(k))}")

    # ---- from here on the file itself is asked, with the poppler tools; without them nothing below is claimed
    tools = ["pdfinfo", "pdfimages", "pdffonts", "pdftotext"]
    lacking = [t for t in tools if shutil.which(t) is None]
    asked = ("forest villages PDF: the poppler tools (pdfinfo, pdfimages, pdffonts, pdftotext) are on the PATH, the PDF is on disk, and pdftotext here is the version the record names in poppler - so that what follows is recomputed from the file itself, with the tool the record was made with")
    if lacking or data is None:
        check(asked, False, f"NOT RECOMPUTED - tools not on the PATH: {lacking}; the PDF is on disk: {data is not None}. The checks of the record and of its two tables against the file itself were NOT made, nor those of gates_phase5.csv and of the step's section of gap.provenance.json")
        return
    version = (subprocess.run(["pdftotext", "-v"], capture_output=True).stderr.decode("utf-8", "replace").splitlines() or ["?"])[0].strip()
    check(asked, version == rec.get("poppler"),
          "" if version == rec.get("poppler") else f"pdftotext here is {version!r}; the record names {rec.get('poppler')!r}. The checks below were made with the tool here: a count of characters or a line of text can differ between versions")

    info = {}
    for ln in _rights_tool("pdfinfo", pdf).splitlines():
        if ":" in ln:
            info.setdefault(ln.split(":", 1)[0].strip(), ln.split(":", 1)[1].strip())
    n_pages = as_int(info.get("Pages", ""))
    held("forest_villages_pdf_record.json: pages, creator and producer are the Pages, Creator and Producer that pdfinfo reports for the file",
         type(rec.get("pages")) is int and (rec.get("pages"), rec.get("creator"), rec.get("producer")) == (n_pages, info.get("Creator"), info.get("Producer")),
         f"record {(rec.get('pages'), rec.get('creator'), rec.get('producer'))}; pdfinfo {(n_pages, info.get('Creator'), info.get('Producer'))}")
    if not n_pages:
        check("forest villages PDF: the pages of the file, to be read one at a time", False, f"NOT RECOMPUTED: pdfinfo reports no number of pages ({info.get('Pages')!r}). The checks of the record and of its two tables against the file's text were NOT made, nor those of gates_phase5.csv and of the step's section of gap.provenance.json")
        return

    rotation = {}
    for ln in _rights_tool("pdfinfo", "-f", 1, "-l", n_pages, pdf).splitlines():
        found = re.fullmatch(r"Page\s+(\d+)\s+rot:\s+(-?\d+)", ln.strip())
        if found:
            rotation[found.group(1)] = int(found.group(2))
    rotated = {p: d for p, d in rotation.items() if d != 0}
    held("forest_villages_pdf_record.json: pages_rotated gives, page by page, the degrees of every page whose rotation pdfinfo reports as other than 0, and no other page (pdfinfo reports a rotation for every page of the file)",
         sorted(rotation, key=int) == [str(p) for p in range(1, n_pages + 1)] and isinstance(rec.get("pages_rotated"), dict) and rec.get("pages_rotated") == rotated
         and all(type(v) is int for v in rec.get("pages_rotated").values()),
         f"record {rec.get('pages_rotated')!r}; pdfinfo {rotated!r}, with a rotation reported for {len(rotation)} of {n_pages} pages")

    listing = _rights_tool("pdfimages", "-list", pdf).splitlines()
    head = listing[0].split() if listing else []
    images = [ln.split() for ln in listing[2:] if ln.strip()]
    lined_up = bool(images) and all(len(r) == len(head) for r in images) and {"page", "x-ppi", "y-ppi"} <= set(head)
    per_page = Counter(as_int(r[head.index("page")]) for r in images) if lined_up else Counter()
    one_image = sum(1 for p in range(1, n_pages + 1) if per_page.get(p, 0) == 1)
    ppi = sorted({r[head.index("x-ppi")] for r in images} | {r[head.index("y-ppi")] for r in images}) if lined_up else []
    fonts = len([ln for ln in _rights_tool("pdffonts", pdf).splitlines()[2:] if ln.strip()])
    held("forest_villages_pdf_record.json: pages_that_are_one_image is the number of pages for which pdfimages -list shows exactly one image, image_pixels_per_inch the distinct x-ppi and y-ppi values it shows, and fonts_named_in_the_file the number of fonts pdffonts lists",
         lined_up and type(rec.get("pages_that_are_one_image")) is int and rec.get("pages_that_are_one_image") == one_image
         and isinstance(rec.get("image_pixels_per_inch"), list) and sorted(map(str, rec.get("image_pixels_per_inch"))) == ppi and type(rec.get("fonts_named_in_the_file")) is int and rec.get("fonts_named_in_the_file") == fonts,
         f"record {(rec.get('pages_that_are_one_image'), rec.get('image_pixels_per_inch'), rec.get('fonts_named_in_the_file'))}; recounted {(one_image, ppi, fonts)}; the listing of images could be read: {lined_up}")

    characters = len(_rights_tool("pdftotext", pdf, "-").strip())
    held("forest_villages_pdf_record.json: characters_of_text_in_the_file is the length of pdftotext's default output for the whole file with the white space at its two ends removed, and is above zero: the file carries text",
         type(rec.get("characters_of_text_in_the_file")) is int and rec.get("characters_of_text_in_the_file") == characters and characters > 0, f"record {rec.get('characters_of_text_in_the_file')!r}; recounted {characters}")

    # ---- the text layer, one page at a time, read by the definition's rules
    pages = []
    for p in range(1, n_pages + 1):
        text = _rights_tool("pdftotext", "-layout", "-f", p, "-l", p, pdf, "-")
        pages.append(text[:-1] if text.endswith("\f") else text)                      # pdftotext ends a page with a form feed
    layer = _rights_read_layer(pages)
    page = layer["summary_page"]
    held("forest_villages_pdf_record.json: summary_page is the first of the first six pages whose text (pdftotext -layout, white space collapsed) has the heading 'List of Forest / Un-Surveyed Villages in the Districts'",
         page is not None and type(rec.get("summary_page")) is int and rec.get("summary_page") == page, f"record {rec.get('summary_page')!r}; the first such page here: {page!r}")

    expected = [(str(page), line, parsed[0], str(parsed[1]), str(parsed[2]), str(parsed[3]), "yes" if parsed[1] + parsed[2] == parsed[3] else "no", "yes" if _rights_is_total(parsed[0]) else "no")
                for line, parsed in layer["rows"]]
    got = [tuple(r.get(c, "") for c in lcols) for r in tl]
    pairs = [(f"row {j + 1}", got[j] if j < len(got) else "(no such row in the table)", expected[j] if j < len(expected) else "(no such row on the page)", j < len(got) and j < len(expected) and got[j] == expected[j])
             for j in range(max(len(got), len(expected)))]
    check("forest_villages_text_layer_check.csv: its rows are, one for one and in the page's order, the lines of the summary page (pdftotext -layout, white space collapsed) that end in three whole numbers with nothing but white space and marks between them, and no other line; "
          "line_as_read is that line, revenue_villages, zero_area_villages and total_inhabited_villages are the three numbers, label_as_read is what stands before them, adds_up is 'yes' where the first two add to the third and 'no' otherwise, is_a_total_row is 'yes' where the label has the word 'total' and 'no' otherwise, and page is the summary page",
          page is not None and bool(expected) and all(p[3] for p in pairs), ("no summary page was found; " if page is None else "") + mismatches(pairs))
    held("forest_villages_pdf_record.json: summary_rows_read, summary_rows_that_add_up, summary_rows_that_do_not (the lines, in the page's order), printed_total_row_read and zero_area_villages_summed_over_the_rows_read (the middle column, total rows apart) are those of this script's own reading of the summary page from the file's text layer",
         page is not None and whole_numbers and figures == _rights_figures(layer["rows"]), f"record {figures}; this script's reading {_rights_figures(layer['rows'])}")

    mine = layer["districts"]
    pairs = []
    for j in range(max(len(dt), len(mine))):
        for c in dcols:
            a, b = (dt[j].get(c, "") if j < len(dt) else "(no such row in the table)"), (mine[j][c] if j < len(mine) else "(no such district in the file)")
            pairs.append((f"district {j + 1}, {c}", a, b, j < len(dt) and j < len(mine) and a == b))
    check("forest_villages_districts_as_the_layer_reads_them.csv: every cell of its 15 columns, row for row, is what this script reads from the file's text layer (pdftotext -layout, one page at a time) by the definition's rules - one row for each district page, in the file's order; the district's pages; its list pages; the three numbers of its page; "
          "whether they add up and are those of a row of the summary page; its rows with a village code; its serial numbers, read on the lines of its list pages (how many distinct, the highest, those from 1 to the page's count that are missing, whether 1 is read more than once, whether they are exactly 1 to the count) - "
          "and the record's districts_in_the_file is the number of district pages",
          bool(mine) and all(p[3] for p in pairs) and rec.get("districts_in_the_file") == len(mine),
          "" if bool(mine) and all(p[3] for p in pairs) and rec.get("districts_in_the_file") == len(mine) else
          (mismatches(pairs, 6) + f"; districts_in_the_file: record {rec.get('districts_in_the_file')!r}, district pages here {len(mine)}").lstrip("; "))

    my_parts = layer["parts"]
    my_failing = [part for part in _rights_ASKS if my_parts[part][0] != my_parts[part][1]]
    held("forest_villages_pdf_record.json, check_a recomputed from the file's text layer: for each of a1 to a6 the record's holds_in and of are this script's own counts (a1 and a2 on its reading of the summary page, a3 to a6 on its reading of every district), parts_that_fail lists the parts that do not hold in every row on that reading, and holds is true only if none fails",
         rec_parts == my_parts and ca.get("parts_that_fail") == my_failing and ca.get("holds") is (not my_failing),
         f"record {rec_parts}, parts_that_fail {ca.get('parts_that_fail')!r}, holds {ca.get('holds')!r}; this script's reading {my_parts}, failing {my_failing}")

    if not my_failing:
        check("forest_villages_pdf_record.json, the owner's rule applied to this script's own check (a)", False,
              "NOT COMPARED: on this script's reading of the text layer check (a) holds. By the definition the step then stops for a reader to make check (b), which no script can make; this part does not know what the record should say in that case")
    else:
        conclusion = " ".join(str(rec.get("conclusion") or "").split())
        named = sorted(set(re.findall(r"\ba[1-6]\b", conclusion)))
        said_pages = set(re.findall(r"\b(\d+) pages\b", conclusion))
        said_ppi = set(re.findall(r"\b(\d+) pixels per inch\b", conclusion))
        held("forest_villages_pdf_record.json, the owner's rule applied to this script's own check (a), which fails: which_check_failed is '(a)', check_b.run is false and text_usable_for_counts is false; and the conclusion, which the rule requires to record the page count, the layer and which check failed, "
             "is not blank, says 'check (a)', names as failing exactly the parts that fail on this script's reading and no other part, gives the page count pdfinfo reports wherever it writes 'N pages' (and writes it), gives the images' pixels per inch wherever it writes 'N pixels per inch', "
             "names the file's producer (the software that made the layer), and says that check (b) was 'not run' (its other words are not tested)",
             rec.get("which_check_failed") == "(a)" and cb.get("run") is False and rec.get("text_usable_for_counts") is False
             and conclusion != "" and "check (a)" in conclusion and named == sorted(my_failing) and said_pages == {str(n_pages)} and said_ppi <= set(ppi)
             and bool(info.get("Producer")) and info.get("Producer") in conclusion and re.search(r"check \(b\) was not run", conclusion, re.IGNORECASE) is not None,
             f"which_check_failed {rec.get('which_check_failed')!r}; check_b.run {cb.get('run')!r}; text_usable_for_counts {rec.get('text_usable_for_counts')!r}; parts the conclusion names {named}, parts that fail here {sorted(my_failing)}; "
             f"'N pages' in the conclusion {sorted(said_pages)}, pages {n_pages}; 'N pixels per inch' {sorted(said_ppi)}, images {ppi}; producer {info.get('Producer')!r}; conclusion {conclusion[:200]!r}")

    # ================================================================== gates_phase5.csv, and what the step's section of the provenance says of the step
    g_raw = table("gates_phase5.csv")
    g = _rights_whole(g_raw)
    head = _rights_header("gates_phase5.csv")
    sec = prov.get("steps", {}).get("08_build_gap_rights") if isinstance(prov, dict) and isinstance(prov.get("steps"), dict) else None
    sec = sec if isinstance(sec, dict) else {}
    n_yes = sum(1 for r in g if r["pass"] == "yes")
    held("gates_phase5.csv: the columns gate, expected, found and pass, each once, and no other; at least one row, none ragged, no gate named twice, no cell blank; every row's pass is 'yes'; "
         "and the step's section of gap.provenance.json (steps > 08_build_gap_rights) gives gates as the number of rows and gates_passed as the number that pass, as whole numbers",
         sorted(head) == ["expected", "found", "gate", "pass"] and bool(g) and not _rights_ragged(g_raw) and len({r["gate"] for r in g}) == len(g) and all(r[c].strip() != "" for r in g for c in ("gate", "expected", "found", "pass"))
         and n_yes == len(g) and type(sec.get("gates")) is int and type(sec.get("gates_passed")) is int and (sec.get("gates"), sec.get("gates_passed")) == (len(g), n_yes),
         f"columns {head}; {len(g)} rows, {_rights_ragged(g_raw)} ragged; pass: {[r['pass'] for r in g]}; the section: gates {sec.get('gates')!r}, gates_passed {sec.get('gates_passed')!r}")

    numbers = lambda text: [int(x) for x in re.findall(r"[0-9]+", text)]
    no_titles = sorted(name[k] for k in codes if X[k]["titles"] == 0)
    differ = None if len(national) != 1 else f"{show(state_titles - fr(national[0]['titles_distributed_community']))} {show(state_extent - fr(national[0]['extent_ha_community']), 0)}"
    wanted = [(("community titles distributed", "state"), show(state_titles), True),            # (key words of the gate's name, the figures `found` must give, whether `expected` must give them too)
              (("community extent", "state"), show(state_extent), True),
              (("no community title",), str(len(no_titles)), True),
              (("two fra reports",), differ, True),
              (("registered file",), str(len(exact)), False),
              (("one scanned image",), f"{n_pages} {one_image}", False),
              (("district counts",), " ".join(f"{part[1:]} {my_parts[part][0]} {my_parts[part][1]}" for part in _rights_ASKS), False)]
    pairs = []
    for words, figures, in_expected in wanted:
        hit = [r for r in g if all(w in r["gate"].lower() for w in words)]
        if len(hit) != 1 or figures is None:
            pairs.append((" + ".join(words), f"{len(hit)} gates with these words in their names", "one gate, and figures to hold it to", False))
            continue
        ok = numbers(hit[0]["found"]) == numbers(figures) and (not in_expected or numbers(hit[0]["expected"]) == numbers(figures))
        if words == ("no community title",):
            ok = ok and {nm for nm in name.values() if nm in hit[0]["found"]} == set(no_titles)
            figures += ": " + ", ".join(no_titles)
        pairs.append((hit[0]["gate"][:60], (hit[0]["expected"], hit[0]["found"]), figures, ok))
    check("gates_phase5.csv, the figures of its gates (the definition does not list this step's gates: the seven held here are known by key words of their names, each must be there once and there must be no other gate; of a cell only its whole numbers are compared, in their order, not its words): "
          "found gives the state's community titles and community extent, summed over the 30 districts of the Odisha FRA report; the number of districts with no community title distributed, and names those districts and no other; the difference of the two FRA reports in titles and in hectares rounded half up to a whole hectare; "
          "the number of rows of the manifest that name the PDF with its exact size and SHA-256; the PDF's pages and its pages that are one image; and for each of a1 to a6 in how many rows it holds and of how many, on this script's reading of the text layer - and expected gives the same numbers in the first four",
          all(p[3] for p in pairs) and len(g) == len(wanted), mismatches(pairs, 7) or f"{len(g)} gates in the table, {len(wanted)} known here")

    outs = sec.get("outputs") if isinstance(sec.get("outputs"), dict) else {}
    written = ["fra_by_district.csv", "fra_summary.csv", "fra_two_reports.csv", "forest_villages_pdf_record.json", "forest_villages_text_layer_check.csv", "forest_villages_districts_as_the_layer_reads_them.csv", "gates_phase5.csv"]
    wrong = []
    for nm in written:
        f, e = GAP / nm, outs.get("50_gap/" + nm)
        if not f.exists() or not isinstance(e, dict) or type(e.get("bytes")) is not int or e.get("bytes") != f.stat().st_size or e.get("sha256") != hashlib.sha256(f.read_bytes()).hexdigest():
            wrong.append(nm)
    seeds = sec.get("seeds") if isinstance(sec.get("seeds"), dict) else {}
    ins = sec.get("inputs") if isinstance(sec.get("inputs"), dict) else {}
    reads = [_rights_FRA_DISTRICT, _rights_FRA_NATIONAL, "50_gap/district_need.csv", _rights_PDF, _rights_MANIFEST]
    stale = []
    for e in ins.values():
        if not isinstance(e, dict) or not isinstance(e.get("path"), str):
            stale.append(repr(e)[:60])
            continue
        f = GAP / e["path"].split("/", 1)[1] if e["path"].startswith("50_gap/") else ROOT / e["path"]
        if not f.is_file() or type(e.get("bytes")) is not int or e.get("bytes") != f.stat().st_size or e.get("sha256") != hashlib.sha256(f.read_bytes()).hexdigest():
            stale.append(e["path"])
    held("gap.provenance.json, the section of this step (steps > 08_build_gap_rights): its inputs are the five files the definition names (the two FRA files, district_need.csv, the PDF and the manifest), each once and no other, each with the bytes and the SHA-256 of the file on disk (district_need.csv: of the one in the folder being checked); "
         "its outputs are the seven files the definition says the step writes (the three FRA tables, the record and the two tables on the forest villages PDF, gates_phase5.csv) and no other, each with the bytes and the SHA-256 of the file of that name in the folder being checked; "
         "its seeds give base 20261010, R1 [base + 700, base + 800] and R2 [base + 701, base + 801] (what else it holds under seeds is not tested); permutations is 99999 and bootstrap_resamples 9999, as whole numbers",
         sorted(str(e.get("path")) if isinstance(e, dict) else "" for e in ins.values()) == sorted(reads) and not stale
         and sorted(outs) == sorted("50_gap/" + nm for nm in written) and not wrong and type(seeds.get("base")) is int and seeds.get("base") == _rights_SEED_BASE
         and seeds.get("R1") == [_rights_SEED_BASE + 700, _rights_SEED_BASE + 800] and seeds.get("R2") == [_rights_SEED_BASE + 701, _rights_SEED_BASE + 801]
         and type(sec.get("permutations")) is int and sec.get("permutations") == _rights_N_PERMUTATIONS and type(sec.get("bootstrap_resamples")) is int and sec.get("bootstrap_resamples") == _rights_N_BOOTSTRAP,
         f"inputs listed {sorted(str(e.get('path')) if isinstance(e, dict) else '' for e in ins.values())}, of them missing or with other bytes or SHA-256 than the section gives: {stale}; "
         f"outputs listed {sorted(outs)}; files that are missing or whose bytes or SHA-256 are not the section's: {wrong}; seeds {sec.get('seeds')!r}; permutations {sec.get('permutations')!r}; bootstrap_resamples {sec.get('bootstrap_resamples')!r}")

# ---------------------------------------------------------------------------------------------------------------------
# part_fsi: Phase 5b, the need read against the Forest Survey of India's own district figures -
# fsi_district_check.csv and fsi_summary.csv, each cell recomputed; and what the step says of itself: gates_phase5b.csv
# and the section 08_build_gap_fsi of gap.provenance.json.
# Table 10.20.3 is read here from the registered text of the report's pages, by the rule the definition states.
# Taken as given (another part recomputes it): district_need.csv of the folder being checked.
# Written from the definition in the builder's docstring; the builder was not read.
# ---------------------------------------------------------------------------------------------------------------------
_fsi_TEXT = "00_raw/05_forest_reference/isfr2023_vol2_odisha_pdf_pages_260-265.txt"
_fsi_MANIFEST, _fsi_MANIFEST_ROW = "00_raw/data_manifest.csv", "isfr2023_vol2_odisha_extract"
_fsi_STEP = "08_build_gap_fsi"
_fsi_EIGHT = ["fsi_calculated_area_km2", "fsi_very_dense_km2", "fsi_moderately_dense_km2", "fsi_open_km2", "fsi_forest_cover_km2", "fsi_forest_cover_pct_of_area",
              "fsi_change_wrt_2021_km2", "fsi_scrub_km2"]                      # the table's eight numbers, in the table's order
_fsi_COLUMNS = (["pc11_district_code", "district_name", "fsi_district_name", "match_rule", "n1_ha_2018_2025", "n1_km2_2018_2025", "forest_at_window_start_ha_2018_2025",
                 "n1_per_100_ha_of_forest_at_window_start"] + _fsi_EIGHT + ["fsi_scrub_pct_of_forest_cover", "fsi_change_pct_of_forest_cover"])
_fsi_OWNER_TOTALS = {"fsi_calculated_area_km2": "155707", "fsi_very_dense_km2": "7224.42", "fsi_moderately_dense_km2": "21065.55", "fsi_open_km2": "24143.59",
                     "fsi_forest_cover_km2": "52433.56", "fsi_change_wrt_2021_km2": "151.89", "fsi_scrub_km2": "4632.68"}       # the seven columns that can be added
_fsi_SPELLING = {"Angul": "384", "Baleswar": "377", "Deogarh": "373", "Jagatsinghpur": "380", "Nabarangpur": "397"}          # the owner's rule of 11 October 2026
_fsi_SUMMARY_COLUMNS = ["id", "what", "x", "y", "size_free", "n_districts", "rho", "p_permutation", "ci95_lo", "ci95_hi", "n_permutations", "n_bootstrap",
                        "n_bootstrap_undefined", "seed_permutation", "seed_bootstrap", "the_two_sources"]
_fsi_ROWS = [("a", "n1_ha_2018_2025", "fsi_change_wrt_2021_km2", "no"), ("b", "n1_ha_2018_2025", "fsi_scrub_km2", "no"),
             ("c", "n1_per_100_ha_of_forest_at_window_start", "fsi_change_pct_of_forest_cover", "yes"),
             ("d", "n1_per_100_ha_of_forest_at_window_start", "fsi_scrub_pct_of_forest_cover", "yes")]
_fsi_SEED_BASE = 20261010                  # the builders' base seed: row k (from 0) has base + 900 + k and base + 950 + k
_fsi_N_PERMUTATIONS = 99999
_fsi_N_BOOTSTRAP = 9999
_fsi_OWN_SEED = 915500000                  # this part's own draws start here; nothing to do with the builders' seeds
_fsi_OWN_BOOTSTRAPS = 20                   # own bootstraps of 9,999 draws each: the first is "this part's interval", all of them
                                           # measure how far such an interval's end moves from one bootstrap to the next


def _fsi_number(token):
    """True where a word is a number as the table prints one: digits, plain or with commas in the Indian grouping (1,55,707), an optional minus sign, an optional decimal part."""
    import re
    return re.fullmatch(r"-?(?:\d+|\d{1,2}(?:,\d{2})*,\d{3})(?:\.\d+)?", token) is not None


def _fsi_read_table(lines):
    """Table 10.20.3 by the definition's rule. Returns (lines that hold 'Table 10.20.3', district rows, Grand Total rows).

    From a line that holds "Table 10.20.3" on, every line that is a name followed by exactly eight numbers is a row,
    until the row named "Grand Total", which ends the table. A line is such a row when its last eight words are numbers,
    the word before them is not a number, and the words before them (the name) hold a letter. A row is
    (name, [the eight numbers as printed]).
    """
    headings, found, grand, reading = 0, [], [], False
    for line in lines:
        if "Table 10.20.3" in line:
            headings += 1
            reading = True
        if not reading:
            continue
        words = line.split()
        k = 0
        while k < len(words) and _fsi_number(words[len(words) - 1 - k]):
            k += 1
        name = " ".join(words[:len(words) - 8]) if k == 8 else ""
        if k != 8 or not any(ch.isalpha() for ch in name):
            continue
        if name == "Grand Total":
            grand.append(words[-8:])
            reading = False
        else:
            found.append((name, words[-8:]))
    return headings, found, grand


def _fsi_plain(printed):
    """A printed number without its commas: the digits, the sign and the decimals as printed."""
    return printed.replace(",", "")


def _fsi_fr(cell):
    """A cell as an exact fraction."""
    from fractions import Fraction
    return Fraction(Decimal(str(cell).strip()))


def _fsi_half_up(x, places):
    """A fraction rounded half up to `places` decimals, exactly (a tie goes away from zero, as decimal.ROUND_HALF_UP), as text with `places` decimals."""
    scaled = abs(x) * 10 ** places
    whole = scaled.numerator // scaled.denominator
    if 2 * (scaled - whole) >= 1:
        whole += 1
    return format(Decimal(-whole if x < 0 else whole).scaleb(-places), "f")


def _fsi_is_tie(x, places):
    """True where a fraction lies exactly half way between two numbers of `places` decimals."""
    scaled = abs(x) * 10 ** places
    return 2 * (scaled - scaled.numerator // scaled.denominator) == 1


def _fsi_whole(rws):
    """Rows with a missing cell, or a column the header lacks, read as blank, and cells beyond the header dropped: a ragged row or a lost column then fails its checks instead of stopping the part."""
    from collections import defaultdict
    return [defaultdict(str, {k: ("" if v is None else v) for k, v in r.items() if k is not None}) for r in rws]


def _fsi_ragged(rws):
    """How many rows of a table do not have exactly the header's cells."""
    return sum(1 for r in rws if None in r or any(v is None for v in r.values()))


def _fsi_header(name):
    """The header of a table of the folder being checked, as written; [] where the file is not there."""
    try:
        with open(GAP / name, encoding="utf-8", newline="") as f:
            return next(csv.reader(f), [])
    except OSError:
        return []


def _fsi_table(name):
    """A table of the folder being checked; [] where the file is not there (its checks then fail)."""
    try:
        return table(name)
    except OSError:
        return []


def _fsi_float(text):
    """A cell as a finite number, or None."""
    try:
        v = float(text)
    except (TypeError, ValueError):
        return None
    return v if text == text.strip() and math.isfinite(v) else None


def _fsi_places(values):
    """Each exact value's place among the sorted distinct values: equal values share a place, so a tie is exact."""
    place = {v: i for i, v in enumerate(sorted(set(values)))}
    return np.array([place[v] for v in values], dtype=np.int64)


def _fsi_twice_ranks(places):
    """Twice the average rank of every entry within its own row (one row per sample): (entries of the row below it) + (entries of the row not above it) + 1. Whole numbers."""
    c = np.atleast_2d(np.asarray(places, dtype=np.int64))
    r, n = c.shape
    keyed = c + (int(c.max()) + 1) * np.arange(r, dtype=np.int64)[:, None]          # every row in a range of its own, so one sorted list serves all rows
    ordered = np.sort(keyed, axis=1).ravel()
    first = (n * np.arange(r, dtype=np.int64))[:, None]
    below = np.searchsorted(ordered, keyed.ravel(), side="left").reshape(r, n) - first
    not_above = np.searchsorted(ordered, keyed.ravel(), side="right").reshape(r, n) - first
    return below + not_above + 1


def _fsi_sums(A, B):
    """For twice-ranks A and B (one row per sample of n): the centred cross product T and the centred sums of squares SA, SB. Their sums are n(n + 1), so T = sum(A * B) - n(n + 1)^2: whole numbers."""
    n = A.shape[-1]
    c = n * (n + 1) ** 2
    return (A * B).sum(-1) - c, (A * A).sum(-1) - c, (B * B).sum(-1) - c


def _fsi_rho_exact(xs, ys, places=6):
    """Spearman's rho of exact values with average ranks for ties, rounded half up to `places` decimals from 60 significant digits; None where a side is constant. Also its float."""
    import decimal
    A, B = _fsi_twice_ranks(_fsi_places(xs))[0], _fsi_twice_ranks(_fsi_places(ys))[0]
    T, SA, SB = (int(v) for v in _fsi_sums(A, B))
    if SA <= 0 or SB <= 0:
        return None, float("nan")
    with decimal.localcontext() as ctx:
        ctx.prec = 60
        rho = Decimal(T) / (Decimal(SA) * Decimal(SB)).sqrt()
        return rho.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP), float(rho)


def _fsi_interval(A_places, B_places, draws):
    """The percentile interval of one bootstrap: `draws` holds one row of n places (0 to n - 1) per draw; ranks are made afresh in every draw; the 2.5th and 97.5th percentiles
    (numpy's default, linear between the ordered values) of the rho of the draws in which rho is defined. Returns (lower end, upper end, draws in which rho is not defined)."""
    T, SA, SB = _fsi_sums(_fsi_twice_ranks(A_places[draws]), _fsi_twice_ranks(B_places[draws]))
    ok = (SA > 0) & (SB > 0)
    lo, hi = np.percentile(T[ok] / np.sqrt(SA[ok].astype(float) * SB[ok].astype(float)), [2.5, 97.5])
    return float(lo), float(hi), int((~ok).sum())


def _fsi_own(xs, ys, seed):
    """This part's own permutation p and bootstrap intervals, with its own seed.

      p          (1 + shuffles of y against x whose |rho| is at least the observed |rho|) / (1 + shuffles), two-sided. A shuffle keeps both sums of squares, so its |rho| is at least
                 the observed exactly when its |T| is at least the observed |T|: decided in whole numbers.
      intervals  _fsi_OWN_BOOTSTRAPS of them, each from 9,999 draws of the districts with replacement, as pairs.
    Returns p and the intervals (one row each: lower end, upper end)."""
    px, py = _fsi_places(xs), _fsi_places(ys)
    n = len(xs)
    A, B = _fsi_twice_ranks(px)[0], _fsi_twice_ranks(py)[0]
    T = int(_fsi_sums(A, B)[0])
    rng = np.random.default_rng(seed)
    shuffled = rng.permuted(np.tile(B, (_fsi_N_PERMUTATIONS, 1)), axis=1)
    p = (1 + int((np.abs(shuffled @ A - n * (n + 1) ** 2) >= abs(T)).sum())) / (1 + _fsi_N_PERMUTATIONS)
    intervals = [_fsi_interval(px, py, rng.integers(0, n, size=(_fsi_N_BOOTSTRAP, n)))[:2] for _ in range(_fsi_OWN_BOOTSTRAPS)]
    return p, np.array(intervals)


def _fsi_seeded(xs, ys, seed_permutation, seed_bootstrap):
    """The permutation p and the bootstrap interval drawn with the seeds the definition gives, under one plain reading of it.

    The definition names the generator (`numpy.random.default_rng(seed)`), the two seeds and the two counts; it does not give the calls. The reading here was fixed before
    the table was held against it, and no other was tried:
      permutation  one generator from seed_permutation; y is shuffled 99,999 times, each shuffle one `permutation` of y, the next of the generator; a shuffle counts when
                   its |rho| is at least the observed |rho|, decided in whole numbers
      bootstrap    one generator from seed_bootstrap; each of the 9,999 draws is one call of `integers` for n whole numbers from 0 to n - 1, the next of the generator;
                   ranks made afresh in every draw; the ends are `numpy.percentile` (its default) at 2.5 and 97.5 over the draws in which rho is defined
    Returns p, the lower end, the upper end, and the number of draws in which rho is not defined."""
    px, py = _fsi_places(xs), _fsi_places(ys)
    n = len(xs)
    A, B = _fsi_twice_ranks(px)[0], _fsi_twice_ranks(py)[0]
    T = int(_fsi_sums(A, B)[0])
    rng = np.random.default_rng(seed_permutation)
    shuffled = np.array([rng.permutation(B) for _ in range(_fsi_N_PERMUTATIONS)])
    p = (1 + int((np.abs(shuffled @ A - n * (n + 1) ** 2) >= abs(T)).sum())) / (1 + _fsi_N_PERMUTATIONS)
    rng = np.random.default_rng(seed_bootstrap)
    lo, hi, undefined = _fsi_interval(px, py, np.array([rng.integers(0, n, size=n) for _ in range(_fsi_N_BOOTSTRAP)]))
    return p, lo, hi, undefined


def _fsi_chance_constant(values):
    """The exact chance that a sample of len(values) of the values, drawn with replacement, is constant: rho is then not defined."""
    from collections import Counter
    from fractions import Fraction
    n = len(values)
    return sum(Fraction(k, n) ** n for k in Counter(values).values())


def part_fsi():
    import hashlib
    import re
    from fractions import Fraction

    DC, SM, GT, PV = "fsi_district_check.csv", "fsi_summary.csv", "gates_phase5b.csv", "gap.provenance.json"

    # ================================================================== the Forest Survey's table, read from the registered text
    try:
        data = (ROOT / _fsi_TEXT).read_bytes()
        text = data.decode("utf-8")
    except (OSError, ValueError) as e:
        check(f"the registered text of the report's pages is on disk ({_fsi_TEXT})", False, f"NOT RECOMPUTED: {type(e).__name__}; no check of this part was made")
        return
    try:
        registered = [r for r in rows(_fsi_MANIFEST) if r.get("item_id") == _fsi_MANIFEST_ROW]
    except OSError:
        registered = []
    reg = registered[0] if len(registered) == 1 else {}
    digest = hashlib.sha256(data).hexdigest()
    check(f"the text of the report's pages is the registered one: the manifest ({_fsi_MANIFEST}) has one row {_fsi_MANIFEST_ROW}; its dest is the text's path under 00_raw/; its bytes, marked exact, are the size of the file on disk; "
          "and the SHA-256 of the file on disk is written in that row",
          len(registered) == 1 and "00_raw/" + (reg.get("dest") or "") == _fsi_TEXT and reg.get("bytes") == str(len(data)) and reg.get("bytes_exact") == "Y" and any(digest in v for v in reg.values() if isinstance(v, str)),
          f"rows of that name {len(registered)}; dest {reg.get('dest')!r}; bytes in the manifest {reg.get('bytes')!r} (exact: {reg.get('bytes_exact')!r}), on disk {len(data)}; SHA-256 on disk {digest}")
    headings, printed, grand = _fsi_read_table(text.splitlines())
    names = [nm for nm, _ in printed]
    check("Table 10.20.3 as read from the registered text by the definition's rule: two lines hold 'Table 10.20.3'; 30 district rows, no name twice; and one row named 'Grand Total', which ends the table",
          headings == 2 and len(printed) == 30 and len(set(names)) == 30 and len(grand) == 1,
          f"lines that hold the table's number {headings}; district rows {len(printed)}, distinct names {len(set(names))}; Grand Total rows {len(grand)}")
    if len(grand) != 1 or not printed:
        check("Table 10.20.3: its rows and its Grand Total row, to be held against the tables", False, "NOT RECOMPUTED: the table could not be read; no further check of this part was made")
        return
    grand = dict(zip(_fsi_EIGHT, grand[0]))
    fsi = {nm: dict(zip(_fsi_EIGHT, cells)) for nm, cells in printed}               # name as printed -> the eight numbers as printed

    pairs = []
    for col, owner in _fsi_OWNER_TOTALS.items():
        total = sum(D(_fsi_plain(cells[col])) for cells in fsi.values())
        pairs.append((col, f"printed Grand Total {grand[col]}; the owner's figure {owner}", str(total), total == D(_fsi_plain(grand[col])) and total == D(owner)))
    check("Table 10.20.3: each of the seven columns that can be added (calculated area, very dense, moderately dense, open, total forest cover, change with respect to 2021, scrub), "
          "summed over the 30 districts in decimal arithmetic, equals the printed Grand Total exactly and the figure the owner gave for it (155,707; 7,224.42; 21,065.55; 24,143.59; 52,433.56; 151.89; 4,632.68)",
          all(p[3] for p in pairs), mismatches(pairs))
    pairs = [(nm, c["fsi_forest_cover_km2"], str(sum(D(_fsi_plain(c[k])) for k in ("fsi_very_dense_km2", "fsi_moderately_dense_km2", "fsi_open_km2"))),
              sum(D(_fsi_plain(c[k])) for k in ("fsi_very_dense_km2", "fsi_moderately_dense_km2", "fsi_open_km2")) == D(_fsi_plain(c["fsi_forest_cover_km2"]))) for nm, c in fsi.items()]
    check("Table 10.20.3: in each of the 30 district rows the very dense, moderately dense and open forest add to the total forest cover exactly (the Grand Total row's add too, by the sums above)",
          all(p[3] for p in pairs), mismatches(pairs))
    pairs = []
    for nm, c in list(fsi.items()) + [("Grand Total", grand)]:
        area, cover = _fsi_fr(_fsi_plain(c["fsi_calculated_area_km2"])), _fsi_fr(_fsi_plain(c["fsi_forest_cover_km2"]))
        exp = _fsi_half_up(100 * cover / area, 2) if area > 0 else "(no area)"
        pairs.append((nm, c["fsi_forest_cover_pct_of_area"], exp, area > 0 and c["fsi_forest_cover_pct_of_area"] == exp and not _fsi_is_tie(100 * cover / area, 2)))
    check("Table 10.20.3: every printed per cent, the Grand Total's too (31 rows), is 100 x total forest cover / calculated area rounded to the two decimals printed, "
          "and none of the 31 lies exactly half way between two such numbers (so no rule for ties is in question)", all(p[3] for p in pairs), mismatches(pairs))

    # ================================================================== the census districts, and the match of names
    need_raw = _fsi_table("district_need.csv")
    need = {r["pc11_district_code"]: r for r in _fsi_whole(need_raw)}
    census = {}                                                                       # census name -> its codes
    for code, r in need.items():
        census.setdefault(r["district_name"], []).append(code)
    codes = sorted(need, key=lambda c: (len(c), c))
    check("district_need.csv (taken as given; of the folder being checked): 30 rows, 30 census codes written as whole numbers, 30 district names, none twice",
          len(need_raw) == 30 and len(need) == 30 and all(c.isascii() and c.isdigit() for c in need) and len(census) == 30 and "" not in census,
          f"rows {len(need_raw)}, distinct codes {len(need)}, distinct names {len(census)}")
    match, by_rule = {}, []                                                           # census code -> (name as printed, rule)
    unmatched, twice = [], []
    for nm in names:
        if len(census.get(nm, [])) == 1:
            code, rule = census[nm][0], "census name"
        elif nm in _fsi_SPELLING and nm not in census:
            code, rule = _fsi_SPELLING[nm], "spelling rule"
            by_rule.append(nm)
        else:
            unmatched.append(nm)
            continue
        if code in match or code not in need:
            twice.append(f"{nm} -> {code}")
            continue
        match[code] = (nm, rule)
    check("Table 10.20.3 against the census districts: the names that are not a census name of district_need.csv are exactly the owner's five (Angul, Baleswar, Deogarh, Jagatsinghpur, Nabarangpur) and no other; "
          "with his rule (Angul 384, Baleswar 377, Deogarh 373, Jagatsinghpur 380, Nabarangpur 397) for those five and the census name for the other 25, the match is one to one over the 30 census codes",
          sorted(by_rule) == sorted(_fsi_SPELLING) and not unmatched and not twice and sorted(match) == sorted(need) and len(match) == 30,
          f"names that need a rule {sorted(by_rule)}; names with no match {unmatched}; a code met twice or not a census code {twice}; codes matched {len(match)}")

    def exact(code):
        """A district's exact quantities: what the tables print is rounded from these."""
        r, c = need[code], fsi[match[code][0]]
        n1, forest = _fsi_fr(r["n1_ha_2018_2025"]), _fsi_fr(r["forest_at_window_start_ha_2018_2025"])
        cover, change, scrub = (_fsi_fr(_fsi_plain(c[k])) for k in ("fsi_forest_cover_km2", "fsi_change_wrt_2021_km2", "fsi_scrub_km2"))
        return {"n1_ha_2018_2025": n1, "n1_km2": n1 / 100, "n1_per_100_ha_of_forest_at_window_start": 100 * n1 / forest if forest > 0 else None,
                "fsi_change_wrt_2021_km2": change, "fsi_scrub_km2": scrub,
                "fsi_scrub_pct_of_forest_cover": 100 * scrub / cover if cover > 0 else None, "fsi_change_pct_of_forest_cover": 100 * change / cover if cover > 0 else None}

    usable = sorted(match) == sorted(need) and len(match) == 30
    try:
        E = {code: exact(code) for code in codes} if usable else {}
    except Exception as e:                                                            # a cell of district_need.csv that is not a number
        E, usable = {}, False
        check("district_need.csv: N1 and the forest at the window's start of 2018-2025 are numbers in every row", False, f"{type(e).__name__}: {e}")
    if not usable:
        check("the 30 districts matched one to one, so that fsi_district_check.csv and fsi_summary.csv can be recomputed", False, "NOT RECOMPUTED: the cells and the correlations were not checked")
    derived = ("n1_per_100_ha_of_forest_at_window_start", "fsi_scrub_pct_of_forest_cover", "fsi_change_pct_of_forest_cover")
    if usable:
        none = [f"{code} {k}" for code in codes for k in derived if E[code][k] is None]
        check("the forest at the window's start (district_need.csv) and the Forest Survey's total forest cover are above zero in all 30 districts, so that each of the three derived columns is defined",
              not none, "" if not none else f"not defined: {none[:5]}")
        usable = not none

    # ================================================================== fsi_district_check.csv, cell by cell
    dc_raw = _fsi_table(DC)
    dc = _fsi_whole(dc_raw)
    head = _fsi_header(DC)
    check(f"{DC}: the 18 columns of the definition, in its order, each once, and no other; no row with a cell more or a cell fewer than the header",
          head == _fsi_COLUMNS and _fsi_ragged(dc_raw) == 0, f"header {head}; ragged rows {_fsi_ragged(dc_raw)}")
    got_codes = [r["pc11_district_code"] for r in dc]
    check(f"{DC}: 30 rows, one for each census code of district_need.csv and no other, in increasing order of the census code",
          got_codes == codes and len(got_codes) == 30, f"{len(got_codes)} rows; codes not in district_need.csv {sorted(set(got_codes) - set(codes))}; lacking {sorted(set(codes) - set(got_codes))}; "
          f"in order: {got_codes == sorted(got_codes, key=lambda c: (len(c), c))}")
    row = {}
    for r in dc:
        row.setdefault(r["pc11_district_code"], r)
    blank = _fsi_whole([{}])[0]

    def cell(code, col):
        return row[code][col] if code in row else "(no row)"

    def held(what, columns, expected):
        """One check of `columns` in every row: the cell is, as text, what `expected(code, column)` gives."""
        if not usable:
            check(what, False, "NOT RECOMPUTED (see above)")
            return
        pairs = [(f"{code} {col}", cell(code, col), expected(code, col), row.get(code, blank)[col] == expected(code, col)) for code in codes for col in columns]
        check(what, all(p[3] for p in pairs), mismatches(pairs))

    held(f"{DC}: district_name is the census name that district_need.csv gives for the row's code (30 rows)", ["district_name"], lambda code, col: need[code]["district_name"])
    held(f"{DC}: fsi_district_name is the name as Table 10.20.3 prints it, and match_rule is 'spelling rule' for the owner's five and 'census name' for the other 25 (30 rows)",
         ["fsi_district_name", "match_rule"], lambda code, col: match[code][0 if col == "fsi_district_name" else 1])
    held(f"{DC}: n1_ha_2018_2025 and forest_at_window_start_ha_2018_2025 are the cells of those names in district_need.csv for the row's code, as text (30 rows)",
         ["n1_ha_2018_2025", "forest_at_window_start_ha_2018_2025"], lambda code, col: need[code][col])
    held(f"{DC}: n1_km2_2018_2025 is N1 of 2018-2025 (district_need.csv) in hectares / 100, rounded half up to six decimals and printed with six (30 rows)",
         ["n1_km2_2018_2025"], lambda code, col: _fsi_half_up(E[code]["n1_km2"], 6))
    held(f"{DC}: n1_per_100_ha_of_forest_at_window_start is 100 x N1 / forest at the window's start, both of 2018-2025 from district_need.csv, rounded half up to six decimals from the exact fraction and printed with six (30 rows)",
         ["n1_per_100_ha_of_forest_at_window_start"], lambda code, col: _fsi_half_up(E[code][col], 6))
    held(f"{DC}: the eight numbers of the district's row of Table 10.20.3 (calculated area, very dense, moderately dense, open, total forest cover, per cent of the calculated area, change with respect to 2021, scrub), "
         "each in its own column and as printed - the digits, the sign and the decimals of the registered text, without the commas (30 rows x 8 columns)",
         _fsi_EIGHT, lambda code, col: _fsi_plain(fsi[match[code][0]][col]))
    held(f"{DC}: fsi_scrub_pct_of_forest_cover is 100 x scrub / total forest cover of the district's row, rounded half up to six decimals from the exact fraction and printed with six (30 rows)",
         ["fsi_scrub_pct_of_forest_cover"], lambda code, col: _fsi_half_up(E[code][col], 6))
    held(f"{DC}: fsi_change_pct_of_forest_cover is 100 x change with respect to 2021 / total forest cover (of 2023) of the district's row, with the sign of the change, rounded half up to six decimals from the exact fraction and printed with six (30 rows)",
         ["fsi_change_pct_of_forest_cover"], lambda code, col: _fsi_half_up(E[code][col], 6))

    # ================================================================== fsi_summary.csv: the four rank correlations
    sm_raw = _fsi_table(SM)
    sm = _fsi_whole(sm_raw)
    head = _fsi_header(SM)
    ids = [r["id"] for r in sm]
    check(f"{SM}: the 16 columns of the definition, in its order, each once, and no other; four rows, a, b, c and d in that order, none ragged",
          head == _fsi_SUMMARY_COLUMNS and ids == [r[0] for r in _fsi_ROWS] and _fsi_ragged(sm_raw) == 0, f"header {head}; ids {ids}; ragged rows {_fsi_ragged(sm_raw)}")
    st = {}
    for r in sm:
        st.setdefault(r["id"], r)

    def scell(i, col):
        return st[i][col] if i in st else "(no row)"

    pairs = [(i, (scell(i, "x"), scell(i, "y"), scell(i, "size_free"), scell(i, "n_districts")), (x, y, free, "30"),
              (st.get(i, blank)["x"], st.get(i, blank)["y"], st.get(i, blank)["size_free"], st.get(i, blank)["n_districts"]) == (x, y, free, "30")) for i, x, y, free in _fsi_ROWS]
    check(f"{SM}: x and y are the two columns of {DC} that the definition names for the row (a: N1 against the change; b: N1 against scrub; c and d: N1 per 100 ha of forest against the change and against scrub, "
          "each as a per cent of the forest cover); size_free is 'no' for a and b and 'yes' for c and d; n_districts is 30", all(p[3] for p in pairs), mismatches(pairs))
    pairs = []
    for i, x, y, free in _fsi_ROWS:
        what = " ".join(st.get(i, blank)["what"].lower().split())
        said = ("change" in what, "scrub" in what, "per cent" in what or "per 100" in what)
        pairs.append((i, scell(i, "what")[:90], "says 'change'" if "change" in y else "says 'scrub'", bool(what) and said[:2] == ("change" in y, "scrub" in y) and said[2] == (free == "yes")))
    check(f"{SM}: what is not blank; it says 'change' and not 'scrub' on rows a and c, 'scrub' and not 'change' on rows b and d, and 'per cent' or 'per 100' on the size-free rows c and d only "
          "(key words chosen by this part: the wording of `what` is not in the definition and the rest of it is not tested)", all(p[3] for p in pairs), mismatches(pairs))
    sentences = [st.get(i, blank)["the_two_sources"] for i, *_ in _fsi_ROWS]
    said = " ".join(sentences[0].lower().split())
    check(f"{SM}: the_two_sources is on every one of the four rows, the same text on each, not blank; it names both sources ('Hansen', 'Forest Survey') and says 'not the same quantity' "
          "(key words: the rest of its wording is not in the definition and is not tested)",
          len(set(sentences)) == 1 and bool(said) and "hansen" in said and "forest survey" in said and "not the same quantity" in said, f"distinct texts {len(set(sentences))}; the first: {sentences[0][:120]!r}")

    def six(text):
        try:
            d = D(text)
        except Exception:
            return False
        return text == text.strip() and d.is_finite() and abs(d) <= 1 and d.as_tuple().exponent >= -6

    pairs = [(f"{i} {c}", scell(i, c), "a number from -1 to 1 with at most six decimals", six(st.get(i, blank)[c])) for i, *_ in _fsi_ROWS for c in ("rho", "ci95_lo", "ci95_hi")]
    check(f"{SM}: rho, ci95_lo and ci95_hi are each a number from -1 to 1 written with at most six decimals (a final zero may be left off)", all(p[3] for p in pairs), mismatches(pairs))

    if not usable:
        check(f"{SM}: rho, p_permutation, ci95_lo, ci95_hi, the counts of draws and the seeds", False, "NOT RECOMPUTED (see above)")
    else:
        exact_of = {"n1_ha_2018_2025": "n1_ha_2018_2025", "fsi_change_wrt_2021_km2": "fsi_change_wrt_2021_km2", "fsi_scrub_km2": "fsi_scrub_km2"}
        V = {i: ([E[code][exact_of.get(x, x)] for code in codes], [E[code][exact_of.get(y, y)] for code in codes]) for i, x, y, _ in _fsi_ROWS}
        same = all(np.array_equal(_fsi_twice_ranks(_fsi_places([E[code][k] for code in codes])), _fsi_twice_ranks(_fsi_places([Fraction(_fsi_half_up(E[code][k], 6)) for code in codes]))) for k in derived)
        check("the three derived columns give the same ranks over the 30 districts whether the exact fractions are ranked or the six decimals printed "
              "(the definition does not say which the correlations rank; with the same ranks either way, the choice changes no figure of the summary)", same)
        pairs = []
        for i, *_ in _fsi_ROWS:
            exp, _f = _fsi_rho_exact(*V[i])
            try:
                ok = exp is not None and st.get(i, blank)["rho"] == st.get(i, blank)["rho"].strip() and D(st.get(i, blank)["rho"]) == exp
            except Exception:
                ok = False
            pairs.append((i, scell(i, "rho"), str(exp), ok))
        check(f"{SM}: rho is Spearman's rho of x against y over the 30 districts (the Pearson correlation of average ranks; ranks made from the exact values, ties sharing the average rank), "
              "equal to the recomputed rho rounded to six decimals", all(p[3] for p in pairs), mismatches(pairs))

        own = {i: _fsi_own(V[i][0], V[i][1], _fsi_OWN_SEED + k) for k, (i, *_) in enumerate(_fsi_ROWS)}
        pairs, sharp, whole, far = [], [], [], 0.0
        for i, *_ in _fsi_ROWS:
            pt, po = _fsi_float(st.get(i, blank)["p_permutation"]), own[i][0]
            pairs.append((i, scell(i, "p_permutation"), f"{po:.5f}", pt is not None and abs(pt - po) <= 0.01))
            se = 0.0 if pt is None or not 0 <= pt <= 1 else math.sqrt((pt * (1 - pt) + po * (1 - po)) / (1 + _fsi_N_PERMUTATIONS))
            sharp.append((i, scell(i, "p_permutation"), f"{po:.5f} (allowed difference {6 * se:.5f})", pt is not None and abs(pt - po) <= 6 * se + 1e-12))
            count = None if pt is None else pt * (1 + _fsi_N_PERMUTATIONS)
            whole.append((i, scell(i, "p_permutation"), "(1 + a count) / 100000", count is not None and abs(count - round(count)) < 1e-6 and 1 <= round(count) <= 1 + _fsi_N_PERMUTATIONS))
            far = max(far, abs(pt - po)) if pt is not None else far
        check(f"{SM}: p_permutation is within 0.01 of this part's own two-sided permutation p (99,999 shuffles of y against x with this part's own seeds; p = (1 + shuffles whose |rho| is at least the observed |rho|) / (1 + shuffles))",
              all(p[3] for p in pairs), mismatches(pairs) or f"largest |difference| {far:.5f}")
        check(f"{SM}: p_permutation is also within six Monte Carlo standard errors of that own p: |difference| <= 6 x sqrt((p(1 - p) + p'(1 - p')) / 100000), p and p' the table's value and this part's",
              all(p[3] for p in sharp), mismatches(sharp))
        check(f"{SM}: p_permutation x 100,000 is a whole number from 1 to 100,000, as (1 + a count of shuffles) / (1 + 99,999) must be", all(p[3] for p in whole), mismatches(whole))

        pairs, sharp, far, z = [], [], 0.0, 0.0
        for i, *_ in _fsi_ROWS:
            t, ivs = st.get(i, blank), own[i][1]
            lo, hi = _fsi_float(t["ci95_lo"]), _fsi_float(t["ci95_hi"])
            ok = lo is not None and hi is not None and abs(lo - ivs[0, 0]) <= 0.04 and abs(hi - ivs[0, 1]) <= 0.04 and lo <= hi
            pairs.append((i, (scell(i, "ci95_lo"), scell(i, "ci95_hi")), (f"{ivs[0, 0]:.6f}", f"{ivs[0, 1]:.6f}"), ok))
            mean, sd = ivs.mean(0), ivs.std(0, ddof=1)
            sharp.append((i, (scell(i, "ci95_lo"), scell(i, "ci95_hi")), (f"{mean[0]:.6f} +/- {6 * sd[0] + 0.000001:.6f}", f"{mean[1]:.6f} +/- {6 * sd[1] + 0.000001:.6f}"),
                          lo is not None and hi is not None and abs(lo - mean[0]) <= 6 * sd[0] + 0.000001 and abs(hi - mean[1]) <= 6 * sd[1] + 0.000001))
            z = max(z, abs(lo - mean[0]) / sd[0] if lo is not None and sd[0] > 0 else 0.0, abs(hi - mean[1]) / sd[1] if hi is not None and sd[1] > 0 else 0.0)
            if lo is not None and hi is not None:
                far = max(far, abs(lo - ivs[0, 0]), abs(hi - ivs[0, 1]))
        check(f"{SM}: ci95_lo and ci95_hi are each within 0.04 of this part's own percentile bootstrap interval (9,999 draws of the 30 districts with replacement, as pairs, with this part's own seed; "
              "ranks made afresh in every draw; the 2.5th and 97.5th percentiles of the rho of the draws), and ci95_lo <= ci95_hi", all(p[3] for p in pairs), mismatches(pairs) or f"largest |difference| {far:.4f}")
        check(f"{SM}: ci95_lo and ci95_hi are also each within six standard deviations of the mean of that end over {_fsi_OWN_BOOTSTRAPS} own bootstraps of 9,999 draws, the standard deviation being that of the end "
              f"across those {_fsi_OWN_BOOTSTRAPS} (how far an honest interval's end moves from one bootstrap to the next), plus 0.000001 for the decimals printed",
              all(p[3] for p in sharp), mismatches(sharp) or f"the end furthest from its mean is {z:.2f} standard deviations away")

        pairs = []
        for k, (i, *_) in enumerate(_fsi_ROWS):
            t = st.get(i, blank)
            expected_undefined = _fsi_N_BOOTSTRAP * (_fsi_chance_constant(V[i][0]) + _fsi_chance_constant(V[i][1]))
            und = t["n_bootstrap_undefined"]
            ok_und = und.isascii() and und.isdigit() and int(und) <= _fsi_N_BOOTSTRAP and (int(und) == 0 or expected_undefined >= Fraction(1, 10 ** 6))
            exp = (str(_fsi_N_PERMUTATIONS), str(_fsi_N_BOOTSTRAP), str(_fsi_SEED_BASE + 900 + k), str(_fsi_SEED_BASE + 950 + k),
                   "0" if expected_undefined < Fraction(1, 10 ** 6) else f"a whole number from 0 to {_fsi_N_BOOTSTRAP}")
            got = tuple(scell(i, x) for x in ("n_permutations", "n_bootstrap", "seed_permutation", "seed_bootstrap", "n_bootstrap_undefined"))
            pairs.append((i, got, exp, got[:4] == exp[:4] and ok_und))
        check(f"{SM}: n_permutations is 99999 and n_bootstrap 9999; seed_permutation and seed_bootstrap are 20261010 + 900 + k and 20261010 + 950 + k, k the row's place from 0 (a, b, c, d); "
              "n_bootstrap_undefined is a whole number from 0 to n_bootstrap, and 0 wherever the exact chance of a constant resample of either side puts the expected number of undefined draws below one in a million",
              all(p[3] for p in pairs), mismatches(pairs))

        pairs = []
        for k, (i, *_) in enumerate(_fsi_ROWS):
            t = st.get(i, blank)
            p, lo, hi, und = _fsi_seeded(V[i][0], V[i][1], _fsi_SEED_BASE + 900 + k, _fsi_SEED_BASE + 950 + k)
            pt, lt, ht = _fsi_float(t["p_permutation"]), _fsi_float(t["ci95_lo"]), _fsi_float(t["ci95_hi"])
            ok = (pt is not None and abs(pt - p) <= 1e-9 and lt is not None and abs(lt - lo) <= 5.0e-7 + 1e-12 and ht is not None and abs(ht - hi) <= 5.0e-7 + 1e-12 and t["n_bootstrap_undefined"] == str(und))
            pairs.append((i, tuple(scell(i, x) for x in ("p_permutation", "ci95_lo", "ci95_hi", "n_bootstrap_undefined")), (f"{p:.5f}", f"{lo:.9f}", f"{hi:.9f}", str(und)), ok))
        check(f"{SM}: drawn again with the seeds the definition gives (20261010 + 900 + k for the permutation, 20261010 + 950 + k for the bootstrap), p_permutation, ci95_lo, ci95_hi and n_bootstrap_undefined are the table's to the digit - "
              "p as (1 + a count) / 100,000 (|difference| <= 0.000000001), each end to the 6 decimals printed (|table - recomputed| <= 0.0000005), the number of undefined draws the same - "
              "under this part's one reading of how the generator is called, which the definition does not give: numpy.random.default_rng(seed) once for each of the two; y shuffled 99,999 times in turn (one `permutation` each), "
              "a shuffle counted when its |rho| is at least the observed |rho| (decided in whole numbers); 9,999 draws in turn of 30 whole numbers from 0 to 29 (one `integers` each), ranks made afresh, numpy's default percentiles "
              "at 2.5 and 97.5 of the rho of the draws in which it is defined", all(p[3] for p in pairs), mismatches(pairs))

    # ================================================================== gates_phase5b.csv
    g_raw = _fsi_table(GT)
    gates = _fsi_whole(g_raw)
    head = _fsi_header(GT)
    labels = [g["gate"] for g in gates]
    n_yes = sum(1 for g in gates if g["pass"] == "yes")
    check(f"{GT}: the columns gate, expected, found and pass, each once, and no other; at least one row, none ragged, no gate named twice, no cell blank; every row's pass is 'yes'",
          head == ["gate", "expected", "found", "pass"] and bool(gates) and _fsi_ragged(g_raw) == 0 and len(set(labels)) == len(labels) and all(g[c].strip() for g in gates for c in head) and n_yes == len(gates),
          f"header {head}; rows {len(gates)}, ragged {_fsi_ragged(g_raw)}, distinct gates {len(set(labels))}, pass = yes on {n_yes}")
    def numbers(text):
        """The numbers a cell names, in its order, as exact numbers."""
        return [D(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text)]

    wrong = []
    for col, owner in _fsi_OWNER_TOTALS.items():
        mine = [g for g in gates if g["gate"].startswith(col + ":")]
        total = sum(D(_fsi_plain(cells[col])) for cells in fsi.values())
        if len(mine) != 1 or numbers(mine[0]["expected"]) != [D(owner)] or numbers(mine[0]["found"]) != [total, D(_fsi_plain(grand[col]))]:
            wrong.append(f"{col}: {[(g['expected'], g['found']) for g in mine]} against the owner's {owner}, the sum {total} and the printed {_fsi_plain(grand[col])}")
    try:
        state = sum(D(need[code]["n1_ha_2018_2025"]) for code in codes)
    except Exception:
        state = None
    for words, exp in (("district rows read", [D(30)]), ("N1 of the state", [state]), ("rank correlations computed", [D(4)])):
        mine = [g for g in gates if words in g["gate"]]
        if len(mine) != 1 or numbers(mine[0]["expected"]) != exp or numbers(mine[0]["found"]) != exp:
            wrong.append(f"'{words}': {[(g['expected'], g['found']) for g in mine]} against {exp}")
    for words in ("not a census name", "one to one", "spelling rule", "add to", "per cent"):
        if sum(1 for g in gates if words in g["gate"]) != 1:
            wrong.append(f"'{words}': in the name of {sum(1 for g in gates if words in g['gate'])} gates, not of one")
    check(f"{GT}: the gates the definition lists are each there once, known by words of their own names, and ten of them carry this part's figures - for each of the seven columns that can be added, the gate whose name begins "
          "with the column's name gives as expected the owner's figure and as found two numbers, this part's sum over the 30 districts and the Grand Total as printed; 'district rows read' gives 30 and 30; 'N1 of the state' gives, "
          "as expected and as found, the sum of n1_ha_2018_2025 over district_need.csv; 'rank correlations computed' gives 4 and 4. The gates named 'not a census name', 'one to one', 'spelling rule', 'add to' and 'per cent' "
          "are held as there once, with pass = yes; their expected and found are words and are not recomputed", not wrong, "; ".join(wrong[:3]))

    # ================================================================== the step's section of the provenance record
    try:
        record = json.loads((GAP / PV).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        record = {}
        check(f"{PV}: on disk in the folder being checked, and JSON", False, f"{type(e).__name__}: {e}")
    steps = record.get("steps") if isinstance(record, dict) and isinstance(record.get("steps"), dict) else {}
    sec = steps.get(_fsi_STEP) if isinstance(steps.get(_fsi_STEP), dict) else {}
    check(f"{PV}: a section for this step (steps > {_fsi_STEP})", bool(sec), "" if sec else f"sections: {sorted(steps)}")

    def on_disk(f, e):
        return f.is_file() and isinstance(e, dict) and type(e.get("bytes")) is int and e.get("bytes") == f.stat().st_size and e.get("sha256") == hashlib.sha256(f.read_bytes()).hexdigest()

    ins = sec.get("inputs") if isinstance(sec.get("inputs"), dict) else {}
    stale = []
    for e in ins.values():
        if not isinstance(e, dict) or not isinstance(e.get("path"), str):
            stale.append(repr(e)[:60])
        elif not on_disk(GAP / e["path"].split("/", 1)[1] if e["path"].startswith("50_gap/") else ROOT / e["path"], e):
            stale.append(e["path"])
    listed = sorted(str(e.get("path")) if isinstance(e, dict) else "" for e in ins.values())
    check(f"{PV}, steps > {_fsi_STEP}: its inputs are the two files the definition names (the registered text of the report's pages, and 50_gap/district_need.csv), each once and no other, "
          "each with the bytes and the SHA-256 of the file on disk (district_need.csv: of the one in the folder being checked)",
          listed == sorted([_fsi_TEXT, "50_gap/district_need.csv"]) and not stale, f"inputs listed {listed}; missing, or with other bytes or SHA-256 than the section gives: {stale}")
    outs = sec.get("outputs") if isinstance(sec.get("outputs"), dict) else {}
    written = [DC, SM, GT]
    stale = [nm for nm in written if not on_disk(GAP / nm, outs.get("50_gap/" + nm))]
    check(f"{PV}, steps > {_fsi_STEP}: its outputs are the three files the definition says the step writes (50_gap/{DC}, 50_gap/{SM}, 50_gap/{GT}) and no other, "
          "each with the bytes and the SHA-256 of the file of that name in the folder being checked",
          sorted(outs) == sorted("50_gap/" + nm for nm in written) and not stale, f"outputs listed {sorted(outs)}; missing, or with other bytes or SHA-256 than the section gives: {stale}")
    seeds = sec.get("seeds") if isinstance(sec.get("seeds"), dict) else {}
    exp_seeds = {"base": _fsi_SEED_BASE, "generator": "numpy.random.default_rng"}
    exp_seeds.update({i: [_fsi_SEED_BASE + 900 + k, _fsi_SEED_BASE + 950 + k] for k, (i, *_) in enumerate(_fsi_ROWS)})
    whole_numbers = type(seeds.get("base")) is int and all(isinstance(seeds.get(i), list) and all(type(v) is int for v in seeds[i]) for i, *_ in _fsi_ROWS)
    check(f"{PV}, steps > {_fsi_STEP}: its seeds give base 20261010, for each row a, b, c, d the pair [base + 900 + k, base + 950 + k] (k from 0), the generator numpy.random.default_rng, and nothing else, as whole numbers; "
          "permutations is 99999 and bootstrap_resamples 9999, as whole numbers",
          seeds == exp_seeds and whole_numbers and type(sec.get("permutations")) is int and sec.get("permutations") == _fsi_N_PERMUTATIONS
          and type(sec.get("bootstrap_resamples")) is int and sec.get("bootstrap_resamples") == _fsi_N_BOOTSTRAP,
          f"seeds {seeds}; permutations {sec.get('permutations')!r}; bootstrap_resamples {sec.get('bootstrap_resamples')!r}")
    tab = sec.get("the_table") if isinstance(sec.get("the_table"), dict) else {}
    exp_grand = {col: _fsi_plain(grand[col]) for col in _fsi_EIGHT}
    check(f"{PV}, steps > {_fsi_STEP} > the_table: grand_total_as_printed holds the eight numbers of the Grand Total row of Table 10.20.3 as the registered text prints them (without the commas), each under its column's name, "
          "and no other; spelling_rule is the owner's five names, each on its code (Angul 384, Baleswar 377, Deogarh 373, Jagatsinghpur 380, Nabarangpur 397), and no other; the name it gives holds 'Table 10.20.3' and the unit is km2",
          tab.get("grand_total_as_printed") == exp_grand and tab.get("spelling_rule") == _fsi_SPELLING and "Table 10.20.3" in str(tab.get("name")) and tab.get("unit") == "km2",
          f"grand_total_as_printed {tab.get('grand_total_as_printed')}; spelling_rule {tab.get('spelling_rule')}; name {tab.get('name')!r}; unit {tab.get('unit')!r}")
    check(f"{PV}, steps > {_fsi_STEP}: gates is the number of rows of {GT} and gates_passed the number of them whose pass is 'yes', as whole numbers",
          bool(gates) and type(sec.get("gates")) is int and sec.get("gates") == len(gates) and type(sec.get("gates_passed")) is int and sec.get("gates_passed") == n_yes,
          f"gates {sec.get('gates')!r}, gates_passed {sec.get('gates_passed')!r}; {GT} has {len(gates)} rows, {n_yes} with pass = yes")

# ---- part: deck ---------------------------------------------------------------------------------------------------------------------
# The three tables of 50_gap/deck_tables/ are cut from the stage's own tables: each cell must be a cell of one of them, rounded half up
# as the definition says. Those source tables are verified from the inputs by the other parts; here every deck cell is held against them.
# So this part compares one file with another, by design: it says nothing of a figure that is wrong in the source table too.
_deck_COLUMNS = {                                                   # the columns the definition lists, in its order
    "districts_by_need": ["rank_by_n1", "district_name", "pc11_district_code", "n1_ha", "need_share_pct", "plantation_post_share_pct", "plantation_pre_share_pct",
                          "r_post_share_over_need_share", "st_class", "adi_tercile", "adi_source"],
    "marginalisation_split_c1": ["grouping", "class", "n_districts", "need_share_pct", "allocation_share_pct", "note"],
    "headline_rows": ["id", "what_it_is", "estimate", "interval_lo", "interval_hi", "interval_is", "p", "p_is", "n", "unit", "read_from"]}


def _deck_r(x, places):
    return "" if x in ("", None) else format(q(D(x), places), "f")


def _deck_md(name):
    lines = [l for l in (GAP / "deck_tables" / name).read_text(encoding="utf-8").splitlines() if l.strip()]
    head = [c_.strip() for c_ in lines[0].strip().strip("|").split("|")]
    body = [[c_.strip() for c_ in l.strip()[1:-1].split(" | ")] for l in lines[2:]]
    return head, body


def part_deck():
    need = table("district_need.csv")
    long = {(r["comparison"], r["pc11_district_code"]): r for r in table("need_vs_allocation.csv")}
    split = table("marginalisation_split.csv")
    adi_note = next(r["note"] for r in split if r["grouping"] == "adi_tercile")
    adi_source = adi_note.split("; ", 1)[1]

    heads = {name: list(table(f"deck_tables/{name}.csv")[0].keys()) for name in _deck_COLUMNS}
    check("each of the three deck tables has the columns the definition lists, in its order, and no other (so no cell of a deck table goes unread below)",
          heads == _deck_COLUMNS, "; ".join(f"{n}: {heads[n]}" for n in heads if heads[n] != _deck_COLUMNS[n]))

    # districts_by_need.csv
    t = table("deck_tables/districts_by_need.csv")
    order = sorted(need, key=lambda r: (-D(r["n1_ha_2018_2025"]), r["pc11_district_code"]))
    check("deck_tables/districts_by_need.csv has one row for each of the 30 districts of district_need.csv, in the order of N1 (2018-2025) from the largest, ties by census code, numbered 1 to 30",
          [(r["pc11_district_code"], r["district_name"], r["rank_by_n1"]) for r in t] == [(r["pc11_district_code"], r["district_name"], str(i)) for i, r in enumerate(order, 1)] and len(t) == 30)
    pairs = []
    for row, src in zip(t, order):
        c1, c5 = long[("C1", src["pc11_district_code"])], long[("C5", src["pc11_district_code"])]
        want = {"n1_ha": _deck_r(src["n1_ha_2018_2025"], "1"), "need_share_pct": _deck_r(c1["need_share_pct"], "0.1"),
                "plantation_post_share_pct": _deck_r(c1["allocation_share_pct"], "0.1"), "plantation_pre_share_pct": _deck_r(c5["allocation_share_pct"], "0.1"),
                "r_post_share_over_need_share": _deck_r(c1["r"], "0.01"), "st_class": src["st_class"], "adi_tercile": src["adi_tercile"], "adi_source": adi_source}
        for k, v in want.items():
            pairs.append((f"{src['district_name']}.{k}", row[k], v, row[k] == v))
    check("deck_tables/districts_by_need.csv: every cell (N1 to whole hectares; C1's need share and allocation share and C5's allocation share to one decimal; C1's r to two decimals, blank "
          "where it is blank; the Scheduled Tribe class; the tercile of the index; the index's source line) equals the cell of district_need.csv, need_vs_allocation.csv or "
          "marginalisation_split.csv it is cut from, rounded half up", all(p[3] for p in pairs) and len(pairs) == 240, mismatches(pairs))
    zero = sorted(r["pc11_district_code"] for r in need if D(r["n1_ha_2018_2025"]) == 0)
    blank = sorted(r["pc11_district_code"] for r in t if r["r_post_share_over_need_share"] == "")
    check(f"deck_tables/districts_by_need.csv: r is blank for the districts whose N1 (2018-2025) is zero in district_need.csv ({len(zero)} of them) and for no other",
          blank == zero, f"blank: {blank}; N1 zero: {zero}" if blank != zero else "")
    check("deck_tables/districts_by_need.csv: the need share column and the post-period and pre-period allocation share columns each add to 100 within the rounding of 30 one-decimal cells (0.05 a cell, 1.5 in all)",
          all(abs(sum(float(r[k]) for r in t) - 100) <= 30 * 0.05 for k in ("plantation_post_share_pct", "plantation_pre_share_pct", "need_share_pct")))

    # marginalisation_split_c1.csv
    t2 = table("deck_tables/marginalisation_split_c1.csv")
    src2 = [r for r in split if r["comparison"] == "C1"]
    pairs = []
    for row, src in zip(t2, src2):
        want = {"grouping": src["grouping"], "class": src["class"], "n_districts": src["n_districts"], "need_share_pct": _deck_r(src["need_share_pct"], "0.1"),
                "allocation_share_pct": _deck_r(src["allocation_share_pct"], "0.1"), "note": src["note"]}
        for k, v in want.items():
            pairs.append((f"{src['grouping']}/{src['class']}.{k}", row[k], v, row[k] == v))
    check("deck_tables/marginalisation_split_c1.csv: the rows are those of marginalisation_split.csv for C1, in its order, and every cell (shares to one decimal, half up; the number of districts; the note) equals its source",
          len(t2) == len(src2) == 10 and all(p[3] for p in pairs), mismatches(pairs))

    # headline_rows.csv
    t3_rows = table("deck_tables/headline_rows.csv")
    t3 = {r["id"]: r for r in t3_rows}
    c1 = next(r for r in table("need_vs_allocation_summary.csv") if r["comparison"] == "C1")
    p1 = next(r for r in table("panel_models.csv") if r["id"] == "P1" and not r["term"].endswith("_x_post"))
    h1 = next(r for r in table("unit_history_models.csv") if r["id"] == "H1")
    want = {"C1": {"estimate": _deck_r(c1["rho"], "0.001"), "interval_lo": _deck_r(c1["ci95_lo"], "0.001"), "interval_hi": _deck_r(c1["ci95_hi"], "0.001"), "p": _deck_r(c1["p_permutation"], "0.00001"),
                   "n": f"{c1['n_districts']} districts", "read_from": "50_gap/need_vs_allocation_summary.csv"},
            "P1": {"estimate": _deck_r(p1["coefficient"], "0.0001"), "interval_lo": _deck_r(p1["wcb_ci95_lo"], "0.0001"), "interval_hi": _deck_r(p1["wcb_ci95_hi"], "0.0001"), "p": _deck_r(p1["wcb_p"], "0.0001"),
                   "n": f"{p1['n']} district-years, {p1['clusters']} districts", "unit": p1["coefficient_unit"], "read_from": "50_gap/panel_models.csv"},
            "H1": {"estimate": _deck_r(h1["coefficient"], "0.0001"), "interval_lo": _deck_r(h1["wcb_ci95_lo"], "0.0001"), "interval_hi": _deck_r(h1["wcb_ci95_hi"], "0.0001"), "p": _deck_r(h1["wcb_p"], "0.0001"),
                   "n": f"{h1['n_units']} units ({h1['n_exposed']} exposed), {h1['n_districts']} districts", "unit": h1["coefficient_unit"], "read_from": "50_gap/unit_history_models.csv"}}
    pairs = [(f"{i}.{k}", t3.get(i, {}).get(k), v, t3.get(i, {}).get(k) == v) for i, w in want.items() for k, v in w.items()]
    check("deck_tables/headline_rows.csv has three rows and no more, C1, P1 and H1, each once, and each estimate, interval end, p, n and unit equals the cell of need_vs_allocation_summary.csv, panel_models.csv or "
          "unit_history_models.csv it is cut from (C1 to three decimals and its p to five; P1 and H1 to four), rounded half up",
          sorted(r["id"] for r in t3_rows) == ["C1", "H1", "P1"] and all(p[3] for p in pairs), (f"rows: {[r['id'] for r in t3_rows]}; " if len(t3_rows) != 3 else "") + mismatches(pairs))
    is_ = {"C1": f"Spearman's rho between need ({c1['need_is']}) and allocation ({c1['allocation_is']}) over the districts",
           "P1": f"{p1['outcome']} on {p1['regressor']}; {p1['spec']}",
           "H1": f"{h1['outcome']} on {h1['exposure']}; {h1['sample']}; controls: {h1['controls']}"}
    pairs = [(f"{i}.what_it_is", t3.get(i, {}).get("what_it_is"), v, t3.get(i, {}).get("what_it_is") == v) for i, v in is_.items()]
    pairs.append(("C1.unit", t3.get("C1", {}).get("unit"), "rank correlation", t3.get("C1", {}).get("unit") == "rank correlation"))
    check("deck_tables/headline_rows.csv: what_it_is is made of the cells of the row it is cut from and of no other model's - C1: the summary's need_is and allocation_is; P1: the model's outcome, "
          "regressor and spec; H1: the model's outcome, exposure, sample and controls - set in the table's own words ('Spearman's rho between need (..) and allocation (..) over the districts', "
          "'.. on ..; ..', '.. on ..; ..; controls: ..': no definition gives that wording); and C1's unit says 'rank correlation'", all(p[3] for p in pairs), mismatches(pairs))
    said = {"P1": f"({p1['clusters']} district clusters", "H1": f"({h1['n_districts']} district clusters"}
    check("deck_tables/headline_rows.csv: the words on each interval name the method and, for P1 and H1, the number of clusters of that model; C1's say a percentile bootstrap over districts and a permutation p",
          all(said[i] in t3[i]["interval_is"] and "wild cluster bootstrap" in t3[i]["interval_is"] and t3[i]["p_is"] == "wild cluster bootstrap" for i in said)
          and "percentile bootstrap over districts" in t3["C1"]["interval_is"] and t3["C1"]["p_is"] == "two-sided permutation")
    whole = {"C1": "95 % percentile bootstrap over districts",
             "P1": f"95 % interval of a restricted wild cluster bootstrap ({p1['clusters']} district clusters, {p1['wcb_weights'].capitalize()} weights), by test inversion",
             "H1": f"95 % interval of a restricted wild cluster bootstrap ({h1['n_districts']} district clusters, {h1['wcb_weights'].capitalize()} weights), by test inversion"}
    pairs = [(f"{i}.interval_is", t3.get(i, {}).get("interval_is"), v, t3.get(i, {}).get("interval_is") == v) for i, v in whole.items()]
    check("deck_tables/headline_rows.csv: interval_is, the whole cell - for P1 and H1 '95 % interval of a restricted wild cluster bootstrap (N district clusters, W weights), by test inversion' with N the "
          "model's own number of clusters and W its own cell wcb_weights, first letter in capitals; for C1 '95 % percentile bootstrap over districts' (the frame is the table's own wording: no definition "
          "gives it; the weights and the number of clusters are the source row's cells)", all(p[3] for p in pairs), mismatches(pairs))

    # the markdown twins
    bad = []
    for name in ("districts_by_need", "marginalisation_split_c1", "headline_rows"):
        rows_ = table(f"deck_tables/{name}.csv")
        head, body = _deck_md(f"{name}.md")
        same_ = head == list(rows_[0].keys()) and len(body) == len(rows_) and all([r[k].replace("|", "/") for k in head] == b for r, b in zip(rows_, body))
        if not same_:
            bad.append(name)
    check("each deck table's markdown twin (.md) has the same columns and, row by row, the same cells as its .csv", not bad, "differ: " + ", ".join(bad) if bad else "")

# ---- the two text files of the models: every figure they print is the figure of the table beside them ---------------------------------
# The text files restate their tables, so this part compares one file with another, by design: a model missing from the table AND from
# the text passes here (the parts on the panel and on the units hold the tables' own rows against the definitions).
_TX_LINE = r"coefficient (-?\d+\.\d+), CR1 se (\d+\.\d+) \(for reference\); wild cluster bootstrap 95% interval (-?\d+\.\d+|unbounded) to (-?\d+\.\d+|unbounded), p = (\d+\.\d+) \(B = (\d+), Webb weights, null imposed, seed (\d+)\)"


def _tx_same(printed, cell):
    """A figure as a text file prints it against the table's cell. The two were each rounded from the same number, the
    text to fewer decimals than the table, so they may differ by half a unit of the text's last decimal plus half a unit
    of the table's; where the table prints no more decimals than the text, the two must be the same number."""
    if printed == "unbounded" or cell == "":
        return printed == "unbounded" and cell == ""
    places = lambda s: len(s.split(".")[1]) if "." in s else 0
    pt, pc = places(printed), places(cell)
    if pc <= pt:
        return D(printed) == D(cell)
    return abs(D(printed) - D(cell)) <= (Decimal(10) ** -pt + Decimal(10) ** -pc) / 2


def _tx_cut(name):
    """The text file cut into its preamble (the lines before the first model) and its blocks, one for each line that begins
    with an id: [(id, the lines from that line to the next such line, blank lines left out)], a block for every such line,
    so that an id that comes twice gives two blocks."""
    import re
    preamble, cut = [], []
    for line in (GAP / name).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Za-z]+\d+[a-z]?)  ", line)
        if m:
            cut.append((m.group(1), [line]))
        elif not cut:
            preamble.append(line)
        elif line.strip():
            cut[-1][1].append(line)
    return preamble, cut


def _tx_preamble(preamble, table_rows, step):
    """What is wrong with a text file's preamble, held against the table and the record of the step: a list of words."""
    import re
    text, wrong = " ".join(preamble), []
    said = re.findall(r"\b([A-Za-z]+\d+[a-z]?) is the headline\b", text)
    marked = list(dict.fromkeys(r["id"] for r in table_rows if r["headline"] == "yes"))
    if said != marked or len(marked) != 1:
        wrong.append(f"the text says the headline is {said}, the table marks {marked}")
    script = json.loads((GAP / "gap.provenance.json").read_text(encoding="utf-8"))["steps"].get(step, {}).get("script")
    by = re.findall(r"\bby (scripts/\S+\.py)\.", text)
    if by != [script]:
        wrong.append(f"the text says it was written by {by}, the record's section {step} names {script!r}")
    return wrong, marked


def part_texts():
    import re
    # panel_models.txt: one block for each model; inside it one line for each term of the table
    pm = table("panel_models.csv")
    preamble, cut = _tx_cut("panel_models.txt")
    blocks = dict(cut)
    ids = list(dict.fromkeys(r["id"] for r in pm))
    check("panel_models.txt has one block for each model of panel_models.csv, each once, in the table's order, and no other", [i for i, _ in cut] == ids, "" if [i for i, _ in cut] == ids else f"text {[i for i, _ in cut]}; table {ids}")
    terms = {i: [r["regressor"] for r in pm if r["id"] == i] for i in ids}
    odd = [i for i, lines in cut if len(lines) != 2 + len(terms.get(i, [])) or not re.match(r"^\s+n = ", lines[1])
           or [l.strip().split(": coefficient ", 1)[0] for l in lines[2:]] != terms.get(i, [])]
    check("panel_models.txt: every block is its first line, the line of n, and one line for each term the table gives the model, in the table's order, and no other line (blank lines apart)",
          not odd and bool(cut), "not so: " + ", ".join(odd) if odd else "")
    pairs = []
    for r in pm:
        text = "\n".join(blocks.get(r["id"], []))
        m = re.search(r"^\s+" + re.escape(r["regressor"]) + ": " + _TX_LINE + r"; unit: (.*)$", text, re.M)
        head = re.search(r"n = (\d+), clusters = (\d+), parameters = (\d+)", text)
        ok = bool(m) and bool(head) and _tx_same(m.group(1), r["coefficient"]) and _tx_same(m.group(2), r["se_cr1"]) and _tx_same(m.group(3), r["wcb_ci95_lo"]) \
            and _tx_same(m.group(4), r["wcb_ci95_hi"]) and _tx_same(m.group(5), r["wcb_p"]) and m.group(6) == r["wcb_B"] and m.group(7) == r["wcb_seed"] \
            and m.group(8) == r["coefficient_unit"] \
            and (head.group(1), head.group(2), head.group(3)) == (r["n"], r["clusters"], r["n_parameters"]) \
            and blocks[r["id"]][0] == f"{r['id']}  {r['outcome']} on {', '.join(terms[r['id']])}; {r['spec']}"
        pairs.append((f"{r['id']} {r['regressor']}", m.groups() if m else None, (r["coefficient"], r["se_cr1"], r["wcb_ci95_lo"], r["wcb_ci95_hi"], r["wcb_p"], r["wcb_B"], r["wcb_seed"], r["coefficient_unit"]), ok))
    check(f"panel_models.txt: for each of the {len(pm)} rows of panel_models.csv, the line of its term prints the table's coefficient, CR1 standard error, interval, p, number of draws and seed "
          "(each to the decimals the text prints: no further from the table's figure than half a unit of the text's last decimal plus half a unit of the table's) and, word for word, its coefficient_unit; "
          "the block's n, clusters and parameters are the table's; and the block's first line is the model's id, its outcome, its regressors in the table's order and its spec", all(p[3] for p in pairs), mismatches(pairs))
    wrong, marked = _tx_preamble(preamble, pm, "08_build_gap_panel")
    counts = re.findall(r"(\d+) district-years \((\d+) districts", " ".join(preamble))
    of_headline = [(r["n"], r["clusters"]) for r in pm if r["id"] in marked][:1]
    if counts != of_headline:
        wrong.append(f"the text counts {counts} district-years and districts, the headline model's n and clusters are {of_headline}")
    check("panel_models.txt, the lines before the first model: the model they call the headline is the one model the table marks `headline` = yes; the script they name is the one the record of "
          "provenance names for the step; and the district-years and districts they count are the n and the clusters of that headline model (the time on the first line is not held)", not wrong, "; ".join(wrong))
    # unit_history_models.txt: one block for each model
    um = table("unit_history_models.csv")
    preamble, cut = _tx_cut("unit_history_models.txt")
    blocks = dict(cut)
    check("unit_history_models.txt has one block for each model of unit_history_models.csv, each once, in the table's order, and no other", [i for i, _ in cut] == [r["id"] for r in um],
          "" if [i for i, _ in cut] == [r["id"] for r in um] else f"text {[i for i, _ in cut]}; table {[r['id'] for r in um]}")
    odd = [i for i, lines in cut if len(lines) != 5 or [bool(re.match(p, l)) for p, l in zip((r"^\s+controls: ", r"^\s+n = ", r"^\s+coefficient ", r"^\s+unit: "), lines[1:])] != [True] * 4]
    check("unit_history_models.txt: every block is five lines and no other (blank lines apart): its first line, then the lines of the controls, of n, of the coefficient and of the unit, in that order",
          not odd and bool(cut), "not so: " + ", ".join(odd) if odd else "")
    pairs = []
    for r in um:
        text = "\n".join(blocks.get(r["id"], []))
        m = re.search(r"^\s+" + _TX_LINE, text, re.M)
        head = re.search(r"n = (\d+) units, (\d+) exposed, (\d+) districts \(clusters\), (\d+) parameters", text)
        ok = bool(m) and bool(head) and _tx_same(m.group(1), r["coefficient"]) and _tx_same(m.group(2), r["se_cr1"]) and _tx_same(m.group(3), r["wcb_ci95_lo"]) \
            and _tx_same(m.group(4), r["wcb_ci95_hi"]) and _tx_same(m.group(5), r["wcb_p"]) and m.group(6) == r["wcb_B"] and m.group(7) == r["wcb_seed"] \
            and head.groups() == (r["n_units"], r["n_exposed"], r["n_districts"], r["n_parameters"]) \
            and blocks[r["id"]][0] == f"{r['id']}  {r['outcome']} on {r['exposure']}; {r['sample']}" and f"    unit: {r['coefficient_unit']}" in blocks[r["id"]] \
            and f"    controls: {r['controls']}" in blocks[r["id"]]
        pairs.append((r["id"], (m.groups() if m else None, head.groups() if head else None), (r["coefficient"], r["se_cr1"], r["wcb_ci95_lo"], r["wcb_ci95_hi"], r["wcb_p"], r["n_units"], r["n_exposed"]), ok))
    check(f"unit_history_models.txt: for each of the {len(um)} models of unit_history_models.csv, its block prints the table's outcome, exposure, sample, controls and unit, its counts of units, "
          "exposed units, districts and parameters, and its coefficient, CR1 standard error, interval, p, number of draws and seed (each to the decimals the text prints: no further from the table's figure than half a unit of the text's last decimal plus half a unit of the table's)",
          all(p[3] for p in pairs), mismatches(pairs))
    wrong, marked = _tx_preamble(preamble, um, "08_build_gap_units")
    check("unit_history_models.txt, the lines before the first model: the model they call the headline is the one model the table marks `headline` = yes; and the script they name is the one the "
          "record of provenance names for the step (the time on the first line is not held)", not wrong, "; ".join(wrong))



PARTS = [part_environment, part_inputs, part_districts, part_comparisons, part_panel, part_units, part_rights, part_fsi, part_deck, part_texts]

if __name__ == "__main__":
    _names = [p.__name__[5:] for p in PARTS]
    if any(o not in _names for o in ONLY):
        sys.exit(f"--only names a part that does not exist: {ONLY}; the parts are {_names}")
    _run = [p for p in PARTS if not ONLY or p.__name__[5:] in ONLY]
    for _part in _run:
        try:
            _part()
        except Exception as _e:                                    # a part that cannot run is a failed check, not a silent pass
            check(f"the part '{_part.__name__[5:]}' ran to its end", False, f"{type(_e).__name__}: {_e}")
    _which = "" if not ONLY else f" (parts run: {', '.join(p.__name__[5:] for p in _run)}; the others were not run)"
    print(f"\n{sum(results)} of {len(results)} checks passed{_which}")
    sys.exit(0 if results and all(results) else 1)
