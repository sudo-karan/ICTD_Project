#!/usr/bin/env python3
"""
Stage 2 - social need per analysis unit: Census 2011 counts, the development index, a poverty estimate,
and one reported construct.

    python scripts/03_build_need.py --units 10_units/units.gpkg

In : 10_units/units.gpkg                                               unit ids and levels (attributes only)
     10_units/odisha_villages_pc11_datameet.gpkg                       which villages have a polygon (attributes only)
     00_raw/02_mgnrega/mis_panel/LGD_village_panchayat_mapping.csv     Census-2011 village code -> LGD panchayat id
     00_raw/03_socioeconomic/village_census_data.csv                   Census 2011 Primary Census Abstract, village / town / ward rows
     00_raw/03_socioeconomic/Village_Level_Predictions_14_States.csv   village development index (ADI), 2011 and 2019
     00_raw/03_socioeconomic/panchayat_census_adi_data.csv             CROSS-CHECK ONLY, see below
     00_raw/03_socioeconomic/shrug/shrug-secc-cons-rural-csv.zip       SHRUG 2.2 SECC rural consumption and poverty, per shrid
     00_raw/03_socioeconomic/shrug/shrug-pc-keys-csv.zip               SHRUG 2.2 key: Census-2011 village -> shrid
     00_raw/01_cfr_fra/OD_CFR_Potential_Villages_22_April_2025.xlsx    ATREE's CFR-potential village list (--atree overrides)
Out: 30_need/ and nowhere else
     need_by_unit.csv                 one row per unit of the layer, including the outside-village units (blank)
     need_source_check.csv            one row per Odisha LGD panchayat id: these figures beside panchayat_census_adi_data.csv
     need_construct_sensitivity.csv   what other forest thresholds would have selected, statewide, and how alike
                                      they rank the units
     need.provenance.json             inputs (bytes, sha256), UTC run time, definitions, checks, n and missingness per column

THE UNIT IS AN LGD PANCHAYAT ID, not a gram panchayat (docs/UNITS.md). A unit's figures are the sum over
every village the mapping gives that id, whether or not the village has a polygon in the unit layer;
population_in_villages_without_polygon says how much of it lies outside the unit's drawn area.
Outside-village units have no census rows at all and every column is blank for them.

WHICH COLUMNS CARRY THE ARGUMENT (rulings of 5 October 2026).
  st_share   is the marginalisation axis.
  adi_2011   is the development control. adi_2019 is reported and is not to be used as a regressor: it is
             blank for 2,866 of the 7,976 units against 534, and would quietly drop a third of the sample.
  forest_dependent_households is a REPORTED COLUMN AND A ROBUSTNESS CHECK, not the need measure. Across units
             it ranks 0.81 alike with ST households counted regardless of forest, and it is zero for 3,619
             units, 2,459 of which have Scheduled Tribe residents. Forest comes from stage 1. The brief's
             three axes are degraded, marginalised and under-allocated; a column that folds forest into
             marginalisation collapses two of them and repeats stage 1's job.

WHY THE COUNTS ARE NOT TAKEN FROM panchayat_census_adi_data.csv. That file is keyed on the same id and
joins to every unit, but on 2026-10-05 its contents did not reconcile to the census rows it was built from:
  - 83 of Odisha's 8,152 ids hold more people than their villages do, 192,336 in all: the 15 census towns
    the mapping places under panchayats are counted twice, and so are individual villages in other ids;
  - its ADI divides sum(ADI x population) by the population of ALL the id's villages, including those with
    no ADI, which are thereby averaged in as zeros. A fifth of Odisha's mapped population has no 2011 ADI
    and nearly half has no 2019 ADI, so the file's figure is pulled toward zero in most ids.
So each village is counted once from the census rows, and ADI is averaged over the villages that have one.
The panchayat file is still read: the run fails if these figures ever exceed it, or if the ADI numerator
stops matching it where the two agree on population, and need_source_check.csv lists every difference.

TWO SOURCE FILES HAVE SHIFTED ROWS. An unquoted comma in a village name moves every later field one place
to the right. The census file has two such rows in Odisha and the village ADI file three; both are repaired
on reading. In the ADI file the last field, ADI_2019, falls off the end of a shifted row and is treated as
missing, not rebuilt. One village's ADI changes (382945: 2011 reads 3 at face value and is 7).

RECONCILIATION. The census file prints no state or district rows, so its Odisha rows are summed and set
against the published Census 2011 totals for population (total, rural, urban), SC and ST - taken from a
secondary copy, named at CENSUS_2011_ODISHA, because the census site could not be reached. Households has
no published figure beside it. The SECC module does print totals of its own, one row per district: each
shrid's rate weighted by the census population of its villages must reproduce all 30, or the run stops.
(A shrid is SHRUG's own location unit: usually one village, sometimes several merged. The module has no
village rows, so every village of a shrid takes the shrid's rate, and this check cannot tell the two apart.)
WHICH POVERTY LINE EACH RATE COLUMN USES is read off the module's own numbers, not its column names: where a
shrid's rate is 1 its mean consumption per head lies below the line, and where it is 0, at or above it, so
the largest mean among the first and the smallest among the second bracket the line. The run stops unless
the brackets round to the Rs 27 and Rs 31 a day the module's documentation gives, in that order.

COLUMNS
  population, households, st_pop, sc_pop     Census 2011, summed over the id's villages.
  st_share, sc_share                         of population; blank where the id has no population.
  adi_2011, adi_2019                         population-weighted mean of the village ADI (sum of five 1-3
                                             ranks, so 5-15; 2019 is a satellite-based prediction) over the
                                             villages that have one. *_population_covered_share is the share
                                             of the id's population in those villages. Blank where none has.
  poverty_rate                               population-weighted mean, over the villages whose shrid has one, of
                                             SHRUG's SECC small-area poverty rate: the share of people below the
                                             Tendulkar rural line (documented as Rs 27 a day; the data put it
                                             between Rs 27.18 and 27.22). A MODEL ESTIMATE - IHDS-II consumption
                                             imputed onto SECC assets - and rural only.
  poverty_rate_ppp2                          the same at the module's higher line ($2 a day PPP, documented as
                                             Rs 31). The run checks it is never below the Tendulkar rate.
  poverty_rate_population_covered_share      share of the id's population in villages that have a rate.
  poverty_rate_population_rated              the people in those villages: how much the rate rests on. Small
                                             counts give rates of exactly 0 or 1.
  poverty_rate_shared_shrid_population_share of those people, the share whose shrid also holds villages of
                                             another LGD panchayat id - where the rate is not this id's alone.
  forest_dependent_households                A CONSTRUCT, NOT A MEASUREMENT - see below.

forest_dependent_households, IN WORDS. The estimated number of Scheduled Tribe households living in villages
that have forest inside their revenue boundary.
  - "Forest inside the revenue boundary" is ATREE's classification, not a threshold chosen here: a village
    counts when ATREE's list gives it CFR Type "Forest within village" or "Both". In ATREE's file those two
    classes begin at 9.90 ha of forest inside the boundary and the third class, "Forest adjacent to village",
    ends at 9.88 ha, so the rule amounts to "about 10 ha or more". It was adopted because it is the source's
    own line; need_construct_sensitivity.csv shows what other lines would select.
  - "Scheduled Tribe households" is not counted by the census at village level. It is estimated as the
    village's households times the ST share of its population, which assumes ST and other households are
    the same size.
  - Households and population come from the census rows by village code. ATREE's own columns are the same
    census figures where it gives them, and blank elsewhere.
  - A village that is not on ATREE's list contributes nothing. Nor do ATREE's 676 rows with no Census-2011
    code: they cannot be placed in a unit without matching names, and ATREE itself gives them no forest area,
    no households and the class "adjacent". So forest settlements, which have no census row, are not in the
    construct at all - a gap in the sources, not a choice made here. The run counts those rows.
  - Qualifying villages in the 176 ids that have no polygon are in no unit, so the units' total is a little
    below the statewide one printed in need_construct_sensitivity.csv.
  - It measures where ST households live beside forest. It does not measure use of, or income from, forest.
    Across units it ranks much as ST households in general do, and a unit can score zero while holding
    Scheduled Tribe population. docs/NEED.md has the figures.

Needs pandas, numpy, pyogrio.
"""
import argparse, csv, datetime, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import pyogrio

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "00_raw"
LGD = RAW / "02_mgnrega" / "mis_panel" / "LGD_village_panchayat_mapping.csv"
PCA = RAW / "03_socioeconomic" / "village_census_data.csv"
VILLAGE_ADI = RAW / "03_socioeconomic" / "Village_Level_Predictions_14_States.csv"
PANCHAYAT = RAW / "03_socioeconomic" / "panchayat_census_adi_data.csv"
SECC = RAW / "03_socioeconomic" / "shrug" / "shrug-secc-cons-rural-csv.zip"
PC_KEYS = RAW / "03_socioeconomic" / "shrug" / "shrug-pc-keys-csv.zip"
ATREE = RAW / "01_cfr_fra" / "OD_CFR_Potential_Villages_22_April_2025.xlsx"
VILLAGE_POLYGONS = ROOT / "10_units" / "odisha_villages_pc11_datameet.gpkg"
OUT = ROOT / "30_need"

STATE = "21"                                             # Odisha in the Census 2011 codes
COUNTS = ["households", "population", "sc_pop", "st_pop"]
ADI_YEARS = ("2011", "2019")
ADI_PARTS = ["BF", "FC", "MSW", "ASSET", "LIT"]          # the five ranked indicators the village ADI adds up
# Census of India 2011 totals for Odisha AS REPRODUCED BY citypopulation.de/en/india/admin/21__odisha/, which
# credits the Registrar General; fetched 2026-10-05. A secondary copy: censusindia.gov.in and two Government of
# Odisha pages could not be reached that day. No published household total was found, so households has none.
CENSUS_2011_ODISHA = {"population": 41_974_218, "rural_population": 34_970_562, "urban_population": 7_003_656,
                      "sc_pop": 7_188_463, "st_pop": 9_590_756}
CENSUS_2011_ODISHA_SOURCE = ("https://www.citypopulation.de/en/india/admin/21__odisha/ (secondary; credits the Office of the "
                             "Registrar General and Census Commissioner), fetched 2026-10-05")
POVERTY = {"poverty_rate": "secc_pov_rate_tend_rural", "poverty_rate_ppp2": "secc_pov_rate_rural"}     # ours: the module's
SECC_DISTRICT_TOLERANCE = 1e-9                           # on a rate between 0 and 1: the district rows are this arithmetic exactly
SECC_LINES_RS_A_DAY = {"poverty_rate": 27, "poverty_rate_ppp2": 31}      # as SHRUG's documentation gives them, whole rupees
SECC_CONSUMPTION = "secc_cons_pc_rural"                  # mean consumption per head, rupees a year
SECC_FLAGS = ["_mean_p_miss", "_core_p_miss"]            # the module's own missing-input shares; its files do not define them
SECC_MIN_CENSUS_AGREEMENT = 0.99                         # below this the key's village codes are not the census's
FOREST_WITHIN = ("Forest within village", "Both")        # ATREE's classes for forest inside the revenue boundary
FOREST_ADJACENT = "Forest adjacent to village"
ATREE_MIN_CENSUS_AGREEMENT = 0.99                        # below this the village codes are not the census's codes
SHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

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


def rel(path):
    p = Path(path).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def code(series):
    """A Census-2011 village code as the mapping, the census and ATREE each write it -> one spelling."""
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.lstrip("0")


def read_census():
    """Odisha's rows of the Primary Census Abstract: one row per village, per town and per ward."""
    rows, repaired = [], []
    with open(PCA, encoding="latin-1", newline="") as fh:
        r = csv.reader(fh)
        head = next(r)
        ix = {c: i for i, c in enumerate(head)}
        for row in r:
            if row[ix["State"]] != STATE:
                continue
            if row[ix["TRU"]] not in ("Rural", "Urban"):       # an unquoted comma inside Name: later fields sit one to the right
                if row[ix["TRU"] + 1] not in ("Rural", "Urban"):
                    fail(f"{PCA.name}: cannot read the row for village code {row[ix['Town/Village']]}: {row[:11]}")
                    continue
                repaired.append(row[ix["Town/Village"]])
                row = row[:ix["Name"]] + [row[ix["Name"]] + "," + row[ix["Name"] + 1]] + row[ix["Name"] + 2:] + [""]
            rows.append([row[ix[c]] for c in ("Town/Village", "Level", "TRU", "No_HH", "TOT_P", "P_SC", "P_ST")])
    c = pd.DataFrame(rows, columns=["code", "level", "tru", "households", "population", "sc_pop", "st_pop"])
    c["code"] = code(c["code"])
    for k in COUNTS:
        c[k] = c[k].astype("int64")
    if set(c["level"]) != {"VILLAGE", "TOWN", "WARD"}:
        fail(f"{PCA.name}: unexpected Level values {sorted(set(c['level']))}")
    return c, repaired


def read_village_adi(codes):
    """Village ADI for the given codes, read twice: at face value, and with shifted rows put right.

    A village name holding an unquoted comma pushes every later field one place to the right, and the last
    field, ADI_2019, off the end of the row. The panchayat file was built from the face-value reading, so
    ADI_*_file keeps that for the cross-check. The figures use the repaired reading, in which a lost
    ADI_2019 is missing rather than rebuilt from its parts."""
    wanted = [f"{p}_{y}" for y in ADI_YEARS for p in ADI_PARTS + ["ADI"]]
    rows, repaired = [], []
    with open(VILLAGE_ADI, encoding="utf-8", newline="") as fh:
        r = csv.reader(fh)
        head = next(r)
        ix = {c: i for i, c in enumerate(head)}
        name = ix["Village_Name"]
        for row in r:
            c = re.sub(r"\.0$", "", row[ix["Village_2011_ID"]]).strip().lstrip("0")
            if c not in codes:
                continue
            face = [row[ix[f"ADI_{y}"]] for y in ADI_YEARS]
            if row[name + 1] and not re.fullmatch(r"\d+(\.\d+)?", row[name + 1]):     # the field after the name is not a rank
                repaired.append(c)
                row = row[:name] + [row[name] + "," + row[name + 1]] + row[name + 2:] + [""]
            rows.append([c] + [row[ix[k]] for k in wanted] + face)
    a = pd.DataFrame(rows, columns=["code"] + wanted + [f"ADI_{y}_file" for y in ADI_YEARS])
    for k in a.columns[1:]:
        a[k] = pd.to_numeric(a[k], errors="coerce")
    for y in ADI_YEARS:                               # the index is the sum of five ranks, each 1-3
        has = a[f"ADI_{y}"].notna()
        parts = a.loc[has, [f"{p}_{y}" for p in ADI_PARTS]]
        bad = has.sum() - int((parts.isin([1, 2, 3]).all(axis=1) & (parts.sum(axis=1) == a.loc[has, f"ADI_{y}"])).sum())
        if bad:
            fail(f"{VILLAGE_ADI.name}: ADI_{y} is not the sum of five 1-3 ranks in {bad} of the mapped villages - a row is misread")
    n_rows = len(a)
    conflicting = int(a.groupby("code")[[f"ADI_{y}" for y in ADI_YEARS]].nunique(dropna=False).gt(1).any(axis=1).sum())
    keep = [f"ADI_{y}" for y in ADI_YEARS] + [f"ADI_{y}_file" for y in ADI_YEARS]
    return a.drop_duplicates("code").set_index("code")[keep], n_rows, conflicting, repaired    # first row, as the panchayat file took it


def read_secc(census):
    """Census-2011 village code -> shrid, its two SECC poverty rates and its flag; checked against the module's own rows."""
    tend, ppp = POVERTY["poverty_rate"], POVERTY["poverty_rate_ppp2"]
    with zipfile.ZipFile(PC_KEYS) as z:
        key = pd.read_csv(z.open("pc11r_shrid_key.csv"), dtype=str)
    key = key[key["pc11_state_id"] == STATE].copy()
    key["code"] = code(key["pc11_village_id"])
    key["key_population"] = pd.to_numeric(key["pc11_pca_tot_p"])
    with zipfile.ZipFile(SECC) as z:
        rates = pd.read_csv(z.open("secc_cons_rural_shrid.csv"), dtype={"shrid2": str}, usecols=["shrid2", tend, ppp, SECC_CONSUMPTION] + SECC_FLAGS)
        printed = pd.read_csv(z.open("secc_cons_rural_pc11dist.csv"), dtype={"pc11_district_id": str, "pc11_state_id": str})
    printed = printed[printed["pc11_state_id"] == STATE].set_index("pc11_district_id")
    if not key["code"].is_unique or key["shrid2"].isna().any() or not rates["shrid2"].is_unique:
        fail(f"{PC_KEYS.name} / {SECC.name}: a village code or a shrid repeats, or a village has no shrid")

    # which line is which, from every shrid row in the country: all poor -> mean below the line; none poor -> mean at or above it
    lines = {}
    for k, c in POVERTY.items():
        all_poor, none_poor = rates.loc[rates[c] == 1, SECC_CONSUMPTION], rates.loc[rates[c] == 0, SECC_CONSUMPTION]
        lines[k] = {"column": c, "shrids_all_poor": int(len(all_poor)), "shrids_none_poor": int(len(none_poor)),
                    "above_rs_a_day": round(float(all_poor.max()) / 365, 4), "at_most_rs_a_day": round(float(none_poor.min()) / 365, 4),
                    "documented_rs_a_day": SECC_LINES_RS_A_DAY[k]}
        low, high = lines[k]["above_rs_a_day"], lines[k]["at_most_rs_a_day"]
        if not (low < high and round(low) == round(high) == SECC_LINES_RS_A_DAY[k]):
            fail(f"{SECC.name}: {c} behaves like a line between Rs {low:.2f} and Rs {high:.2f} a day, not the Rs {SECC_LINES_RS_A_DAY[k]} "
                 f"its documentation gives - the column is not what it is taken to be")
    if lines["poverty_rate"]["at_most_rs_a_day"] >= lines["poverty_rate_ppp2"]["above_rs_a_day"]:
        fail(f"{SECC.name}: the two poverty lines are not in order: {lines}")

    m = key.merge(rates, on="shrid2", how="left")
    has = m[tend].notna()
    if (has != m[ppp].notna()).any() or (m.loc[has, ppp] < m.loc[has, tend] - 1e-9).any():
        fail(f"{SECC.name}: the two poverty rates are not present together, or {ppp} falls below {tend} - the columns are not what they are taken to be")
    # the module's own district rows: every shrid once, weighted by the census population of its villages
    sh = m[has].groupby(["pc11_district_id", "shrid2"]).agg(w=("key_population", "sum"), **{c: (c, "first") for c in (tend, ppp)})
    worst = 0.0
    for c in (tend, ppp):
        mine = (sh[c] * sh["w"]).groupby(level=0).sum() / sh["w"].groupby(level=0).sum()
        gap = (mine - printed[c].reindex(mine.index)).abs()
        if len(mine) != len(printed) or gap.isna().any() or gap.max() > SECC_DISTRICT_TOLERANCE:
            fail(f"{SECC.name}: {c} rebuilt from the shrid rows differs from the module's own district rows by up to {gap.max():.6f} "
                 f"({len(mine)} districts rebuilt, {len(printed)} printed)")
        else:
            worst = max(worst, float(gap.max()))
    known = m["code"].isin(census.index)
    same = float((m.loc[known, "key_population"] == census.loc[m.loc[known, "code"], "population"].to_numpy()).mean())
    if same < SECC_MIN_CENSUS_AGREEMENT:
        fail(f"{PC_KEYS.name}: its village population equals the census in only {same:.1%} of villages found by code - the codes are not the census's")
    m["secc_flagged"] = has & (m[SECC_FLAGS].fillna(0) > 0).any(axis=1)
    meta = {"odisha_villages_in_the_key": int(len(m)), "of_them_in_the_census_file": int(known.sum()), "key_population_equal_to_the_census_share": round(same, 6),
            "villages_with_a_rate": int(has.sum()), "shrids_with_a_rate": int(m.loc[has, "shrid2"].nunique()),
            "shrids_with_a_rate_holding_more_than_one_village": int((m[has].groupby("shrid2").size() > 1).sum()),
            "key_population_in_villages_with_a_rate_share": round(float(m.loc[has, "key_population"].sum() / m["key_population"].sum()), 6),
            "districts_reconciled_to_the_module's_own_rows": int(len(printed)), "max_abs_difference_in_a_district_rate": worst,
            "tolerance": SECC_DISTRICT_TOLERANCE, "poverty_lines_bracketed_from_the_module's_shrid_rows": lines,
            "state_rate_population_weighted_over_the_key's_rated_villages": {
                k: round(float((m.loc[has, c] * m.loc[has, "key_population"]).sum() / m.loc[has, "key_population"].sum()), 6) for k, c in POVERTY.items()},
            "rated_shrids_the_module_flags": {"columns": SECC_FLAGS, "shrids": int(m.loc[m["secc_flagged"], "shrid2"].nunique()),
                                              "note": "a share above zero in either column; the module's files do not say what they measure; the rate is used as given"}}
    return m.set_index("code")[["shrid2", tend, ppp, "secc_flagged"]].rename(columns={c: k for k, c in POVERTY.items()}), meta


def read_atree(path):
    """The one sheet of ATREE's workbook, by the standard library (openpyxl is not a project dependency)."""
    z = zipfile.ZipFile(path)
    strings = ["".join(t.text or "" for t in si.iter(SHEET_NS + "t"))
               for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(SHEET_NS + "si")]
    sheets = sorted(n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
    if len(sheets) != 1:
        sys.exit(f"{path}: expected one worksheet, found {len(sheets)}")

    def column(ref):
        n = 0
        for ch in re.match(r"[A-Z]+", ref).group(0):
            n = n * 26 + ord(ch) - 64
        return n - 1

    table = []
    for r in ET.fromstring(z.read(sheets[0])).find(SHEET_NS + "sheetData").findall(SHEET_NS + "row"):
        cells = {}
        for c in r.findall(SHEET_NS + "c"):
            v = c.find(SHEET_NS + "v")
            if v is not None:
                cells[column(c.attrib["r"])] = strings[int(v.text)] if c.attrib.get("t") == "s" else v.text
        table.append(cells)
    head = [table[0].get(i, "") for i in range(max(table[0]) + 1)]
    numeric = {"forest_ha": "Forest inside revenue boundary (ha)", "area_ha": "Total Geographical Area (ha)", "gis_ha": "Calculated GIS Area (ha)",
               "atree_population": "Total Population", "atree_households": "Total Households"}
    need = {"Village Code 2011", "CFR Type", "Level", *numeric.values()}
    if need - set(head):
        sys.exit(f"{path}: missing column(s) {sorted(need - set(head))}; saw {head}")
    a = pd.DataFrame([[row.get(i, "") for i in range(len(head))] for row in table[1:]], columns=head)
    a["code"] = code(a["Village Code 2011"])
    a["has_code"] = a["code"].str.fullmatch(r"\d+")
    for k, name in numeric.items():
        a[k] = pd.to_numeric(a[name], errors="coerce")
    return a


def missingness(t, columns):
    """n and blank cells for each column of an output table."""
    return {c: {"n": int(t[c].notna().sum()), "blank": int(t[c].isna().sum())} for c in columns}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 unit layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--atree", default=str(ATREE) if ATREE.exists() else None,
                    help="ATREE's Odisha CFR-potential village list (.xlsx); default is the copy registered in 00_raw")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    checks = {}

    units = pyogrio.read_dataframe(a.units, layer="units", read_geometry=False)
    units["unit_id"] = units["unit_id"].astype(str)
    if not units["unit_id"].is_unique or "unit_level" not in units.columns:
        sys.exit(f"{a.units}: needs a unique unit_id and a unit_level column")
    is_panchayat = units["unit_level"] == "lgd_panchayat"
    print(f"units: n = {len(units):,} ({dict(units['unit_level'].value_counts())})")

    # ---- the mapping -------------------------------------------------------------------------------------------
    lgd = pd.read_csv(LGD, dtype=str, keep_default_na=False)
    lgd = lgd[lgd["State_2011_ID"] == STATE].copy()
    lgd["code"] = code(lgd["Village_2011_ID"])
    if set(lgd["State_2022_name"].str.lower().str.strip()) != {"odisha"} or not lgd["code"].is_unique:
        fail(f"{LGD.name}: state code {STATE} is not only Odisha, or a village code appears twice")
    ids = sorted(set(lgd["Panchayat_ID"]))
    no_row = sorted(set(units.loc[is_panchayat, "unit_id"]) - set(ids))
    no_polygon = sorted(set(ids) - set(units.loc[is_panchayat, "unit_id"]))
    if no_row:
        fail(f"{len(no_row)} lgd_panchayat units have no village in {LGD.name}, e.g. {no_row[:5]}")
    print(f"mapping: {len(lgd):,} Odisha villages under {len(ids):,} LGD panchayat ids; units with no row in the mapping {len(no_row)}; "
          f"ids with no unit polygon {len(no_polygon)}")

    # ---- the census --------------------------------------------------------------------------------------------
    census, repaired = read_census()
    stop_if_failed("reading the census file")
    village, town, ward = (census[census["level"] == k] for k in ("VILLAGE", "TOWN", "WARD"))
    rural, urban = village[COUNTS].sum(), ward[COUNTS].sum()
    print(f"census file, Odisha: {len(village):,} village rows, {len(town):,} town rows, {len(ward):,} ward rows; {len(repaired)} rows repaired (codes {repaired})")
    print(f"  village rows: population {rural['population']:,}, households {rural['households']:,}, SC {rural['sc_pop']:,}, ST {rural['st_pop']:,}")
    print(f"  village + ward rows (the state): population {rural['population'] + urban['population']:,}, households {rural['households'] + urban['households']:,}, "
          f"SC {rural['sc_pop'] + urban['sc_pop']:,}, ST {rural['st_pop'] + urban['st_pop']:,}")
    published = {"rural_population": int(rural["population"]), "urban_population": int(urban["population"]),
                 **{k: int(rural[k] + urban[k]) for k in ("population", "sc_pop", "st_pop")}}
    for k, want in CENSUS_2011_ODISHA.items():       # the file prints no state or district rows of its own
        if published[k] != want:
            fail(f"{PCA.name}: Odisha {k} sums to {published[k]:,}, the published Census 2011 figure is {want:,} ({CENSUS_2011_ODISHA_SOURCE})")
    print(f"  OK  population (total, rural, urban), SC and ST equal the published Census 2011 totals - from a secondary copy, see CENSUS_2011_ODISHA;")
    print("      households has no published figure to set beside it")
    by_code = pd.concat([village, town]).groupby("code")[COUNTS].sum()            # a place is a village or a town, never both
    if set(village["code"]) & set(town["code"]):
        fail(f"{PCA.name}: a code is both a village and a town")
    lgd["is_town"] = lgd["code"].isin(set(town["code"]))
    missing_codes = lgd.loc[~lgd["code"].isin(by_code.index), "code"]
    if len(missing_codes):
        fail(f"{len(missing_codes)} mapped villages are not in {PCA.name}, e.g. {missing_codes.head(5).tolist()}")
    towns_used = sorted(lgd.loc[lgd["is_town"], "code"])
    town_rows, ward_sum = town[town["code"].isin(towns_used)].groupby("code"), ward[ward["code"].isin(towns_used)].groupby("code")[COUNTS].sum()
    if (town_rows.size() != 1).any() or not town_rows[COUNTS].sum().equals(ward_sum.reindex(town_rows.size().index)):
        fail(f"{PCA.name}: for a census town the mapping uses, the town row is not the sum of its ward rows")   # the source's own total
    stop_if_failed("checking the census file")
    unmapped = village[~village["code"].isin(set(lgd["code"]))]
    checks.update(census_rows_repaired=repaired, census_towns_under_panchayats=len(towns_used),
                  census_town_row_equals_sum_of_its_wards=len(towns_used),
                  census_villages_not_in_the_mapping={"n": int(len(unmapped)), "population": int(unmapped["population"].sum())},
                  census_odisha_totals_from_rows={"rural_village_rows": {k: int(rural[k]) for k in COUNTS}, "urban_ward_rows": {k: int(urban[k]) for k in COUNTS}},
                  published_census_2011_totals={"equal_on": sorted(CENSUS_2011_ODISHA), "figures": CENSUS_2011_ODISHA, "source": CENSUS_2011_ODISHA_SOURCE,
                                                "not_checked": "households - no published total was found; the file prints no state or district rows"})
    print(f"  every mapped village is in the census file ({int((~lgd['is_town']).sum()):,} village codes, {len(towns_used)} census towns, each town row equal to "
          f"the sum of its wards); {len(unmapped)} census villages are not in the mapping (population {int(unmapped['population'].sum()):,})")

    v = lgd[["Panchayat_ID", "code", "is_town"]].join(by_code, on="code")
    polygons = pyogrio.read_dataframe(VILLAGE_POLYGONS, layer="villages", read_geometry=False, columns=["pc11_village_code"])
    v["no_polygon"] = ~v["code"].isin(set(code(polygons["pc11_village_code"].dropna())))
    adi, adi_rows, adi_conflicts, adi_repaired = read_village_adi(set(v["code"]))
    stop_if_failed("reading the village ADI file")
    v = v.join(adi, on="code")
    changed = v[v["code"].isin(adi_repaired) & ((v["ADI_2011"].fillna(-1) != v["ADI_2011_file"].fillna(-1)) | (v["ADI_2019"].fillna(-1) != v["ADI_2019_file"].fillna(-1)))]
    checks["village_adi_rows_repaired"] = {"codes": adi_repaired, "rows_whose_adi_changed": [
        {"code": r.code, "lgd_panchayat_id": r.Panchayat_ID, "adi_2011": [r.ADI_2011_file, r.ADI_2011], "adi_2019": [r.ADI_2019_file, None if pd.isna(r.ADI_2019) else r.ADI_2019]}
        for r in changed.itertuples()], "note": "[as the file reads at face value, as used]; an ADI_2019 pushed off the end of a shifted row is missing"}
    print(f"village ADI file: {len(adi):,} of {len(v):,} mapped villages have a row ({adi_rows - len(adi)} repeated rows dropped, {adi_conflicts} of them disagreeing); "
          f"ADI_2011 present for {int(v['ADI_2011'].notna().sum()):,}, ADI_2019 for {int(v['ADI_2019'].notna().sum()):,}")
    print(f"  {len(adi_repaired)} rows repaired (codes {adi_repaired}): a comma in the village name shifts the row. ADI changed in {len(changed)} of them: "
          + "; ".join(f"{r.code} 2011 {r.ADI_2011_file:g} -> {r.ADI_2011:g}, 2019 {r.ADI_2019_file:g} -> {'missing' if pd.isna(r.ADI_2019) else format(r.ADI_2019, 'g')}" for r in changed.itertuples()))

    secc, secc_meta = read_secc(by_code)
    stop_if_failed("reading the SECC module")
    v = v.join(secc, on="code")
    rated = v["poverty_rate"].notna()
    ids_per_shrid = v[rated].groupby("shrid2")["Panchayat_ID"].nunique()
    shared = rated & (v["shrid2"].map(ids_per_shrid) > 1)                # the shrid also holds villages of another id
    state = secc_meta["state_rate_population_weighted_over_the_key's_rated_villages"]
    mapped_rate = {k: round(float((v.loc[rated, k] * v.loc[rated, "population"]).sum() / v.loc[rated, "population"].sum()), 6) for k in POVERTY}
    checks["secc"] = {**secc_meta, "mapped_villages_with_a_rate": int(rated.sum()), "mapped_villages": int(len(v)),
                      "mapped_population_in_villages_with_a_rate_share": round(float(v.loc[rated, "population"].sum() / v["population"].sum()), 6),
                      "rate_population_weighted_over_the_mapped_rated_villages": mapped_rate,
                      "shrids_spanning_more_than_one_id": int((ids_per_shrid > 1).sum()), "mapped_villages_in_them": int(shared.sum())}
    lines = secc_meta["poverty_lines_bracketed_from_the_module's_shrid_rows"]
    print(f"SECC module (SHRUG 2.2): {secc_meta['villages_with_a_rate']:,} of {secc_meta['odisha_villages_in_the_key']:,} Odisha villages in its key have a rate "
          f"({state['poverty_rate']:.1%} of their people below the Tendulkar line, {state['poverty_rate_ppp2']:.1%} below the higher one); "
          f"the key's population equals the census in {secc_meta['key_population_equal_to_the_census_share']:.2%}")
    print("  OK  the lines, bracketed from the module's own shrid rows: " + "; ".join(
        f"{d['column']} above Rs {d['above_rs_a_day']:.2f} and at most Rs {d['at_most_rs_a_day']:.2f} a day (documented: Rs {d['documented_rs_a_day']})" for d in lines.values()))
    print(f"  OK  all {secc_meta[chr(100) + 'istricts_reconciled_to_the_module' + chr(39) + 's_own_rows']} district rows the module prints are reproduced from its shrid rows "
          f"(largest difference {secc_meta['max_abs_difference_in_a_district_rate']:.1e}, both rates; tolerance {SECC_DISTRICT_TOLERANCE:g})")
    print(f"  of the {len(v):,} mapped villages {int(rated.sum()):,} have a rate, holding {checks['secc']['mapped_population_in_villages_with_a_rate_share']:.2%} of the mapped population "
          f"({mapped_rate['poverty_rate']:.1%} of them below the Tendulkar line, {mapped_rate['poverty_rate_ppp2']:.1%} below the higher one)")

    # ---- per LGD panchayat id --------------------------------------------------------------------------------
    g = v.groupby("Panchayat_ID")
    t = g[COUNTS].sum()
    t.insert(0, "n_villages", g.size())
    t.insert(1, "n_villages_uninhabited", (v["population"] == 0).groupby(v["Panchayat_ID"]).sum())
    t.insert(2, "n_villages_without_polygon", v["no_polygon"].groupby(v["Panchayat_ID"]).sum())
    t["population_in_villages_without_polygon"] = (v["population"] * v["no_polygon"]).groupby(v["Panchayat_ID"]).sum()
    populated = t["population"] > 0
    t["st_share"] = (t["st_pop"] / t["population"].where(populated)).round(6)
    t["sc_share"] = (t["sc_pop"] / t["population"].where(populated)).round(6)
    numerator, file_numerator = {}, {}
    for year in ADI_YEARS:
        has = v[f"ADI_{year}"].notna()
        numerator[year] = (v[f"ADI_{year}"].fillna(0) * v["population"]).groupby(v["Panchayat_ID"]).sum()
        file_numerator[year] = (v[f"ADI_{year}_file"].fillna(0) * v["population"]).groupby(v["Panchayat_ID"]).sum()
        covered = (v["population"] * has).groupby(v["Panchayat_ID"]).sum()
        t[f"adi_{year}"] = (numerator[year] / covered.where(covered > 0)).round(4)
        t[f"adi_{year}_population_covered_share"] = (covered / t["population"].where(populated)).round(6)
    covered = (v["population"] * rated).groupby(v["Panchayat_ID"]).sum()
    for k in POVERTY:
        t[k] = ((v[k].fillna(0) * v["population"]).groupby(v["Panchayat_ID"]).sum() / covered.where(covered > 0)).round(6)
    t["poverty_rate_population_covered_share"] = (covered / t["population"].where(populated)).round(6)
    t["poverty_rate_population_rated"] = covered
    t["poverty_rate_shared_shrid_population_share"] = ((v["population"] * shared).groupby(v["Panchayat_ID"]).sum() / covered.where(covered > 0)).round(6)
    flagged_ids = set(v.loc[rated & v["secc_flagged"].fillna(False).astype(bool), "Panchayat_ID"])

    # ---- cross-check against the panchayat file ----------------------------------------------------------------
    pf = pd.read_csv(PANCHAYAT, dtype={"Panchayat_ID": str}).set_index("Panchayat_ID")
    if not pf.index.is_unique or set(ids) - set(pf.index):
        fail(f"{PANCHAYAT.name}: Panchayat_ID repeats, or {len(set(ids) - set(pf.index))} Odisha ids have no row")
        stop_if_failed("reading the panchayat file")
    pf = pf.loc[t.index]
    file_cols = {"households": "no_hh", "population": "tot_p", "sc_pop": "p_sc", "st_pop": "p_st"}
    excess = pd.DataFrame({k: pf[f] - t[k] for k, f in file_cols.items()})
    if (excess < 0).any().any():
        fail(f"{PANCHAYAT.name} holds FEWER people or households than the census rows in {int((excess < 0).any(axis=1).sum())} ids - these sums would be double counting")
    agrees = (excess == 0).all(axis=1)
    for year in ADI_YEARS:                          # where the two agree on people, the face-value ADI numerator must be the file's
        off = agrees & ~np.isclose(file_numerator[year], pf[f"pop_adi_{year}"], atol=0.5)
        if off.any():
            fail(f"sum(ADI_{year} x population) differs from {PANCHAYAT.name} in {int(off.sum())} ids whose population agrees - the ADI source or the weights are not the file's")
    stop_if_failed("cross-checking against the panchayat file")
    diluted = {year: int((populated & (t[f"adi_{year}_population_covered_share"] > 0) & (t[f"adi_{year}_population_covered_share"] < 1)).sum()) for year in ("2011", "2019")}
    zeroed = {year: int((populated & (t[f"adi_{year}_population_covered_share"] == 0)).sum()) for year in ("2011", "2019")}
    checks["panchayat_file"] = {
        "ids": int(len(t)), "ids_where_its_counts_equal_the_census_rows": int(agrees.sum()), "ids_where_it_holds_more": int((~agrees).sum()),
        "its_excess": {k: int(excess[k].sum()) for k in COUNTS}, "ids_where_it_holds_less": 0,
        "adi_numerator_equal_where_population_agrees": int(agrees.sum()),
        "ids_where_its_adi_is_diluted_by_villages_with_no_adi": diluted, "populated_ids_where_its_adi_is_zero_because_no_village_has_one": zeroed}
    print(f"panchayat file, {len(t):,} ids: counts equal the census rows in {int(agrees.sum()):,}; it holds MORE in {int((~agrees).sum())} "
          f"(+{int(excess['population'].sum()):,} people, +{int(excess['households'].sum()):,} households); it never holds less")
    print(f"  its ADI numerator equals sum(ADI x population) in all {int(agrees.sum()):,} ids that agree on people; its ADI is diluted by villages with no ADI in "
          f"{diluted['2011']:,} populated ids for 2011 and {diluted['2019']:,} for 2019, and is zero for want of any in {zeroed['2011']:,} and {zeroed['2019']:,}")

    # ---- the construct -----------------------------------------------------------------------------------------
    atree_meta, sensitivity = None, None
    t["forest_dependent_households"] = np.nan
    t["n_forest_villages"] = np.nan
    t["households_in_forest_villages"] = np.nan
    if a.atree:
        at = read_atree(a.atree)
        coded = at[at["has_code"]]
        if not coded["code"].is_unique:
            fail(f"ATREE list: {int(coded['code'].duplicated().sum())} village codes repeat")
        if set(at["CFR Type"]) - set(FOREST_WITHIN) - {FOREST_ADJACENT}:
            fail(f"ATREE list: CFR Type values this script does not know: {sorted(set(at['CFR Type']) - set(FOREST_WITHIN) - {FOREST_ADJACENT})}")
        within = at["CFR Type"].isin(FOREST_WITHIN)
        lowest_within, highest_adjacent = at.loc[within, "forest_ha"].min(), at.loc[~within, "forest_ha"].max()
        if not highest_adjacent < lowest_within:
            fail(f"ATREE list: the classes no longer split on forest area (adjacent reaches {highest_adjacent} ha, within starts at {lowest_within} ha), "
                 "so the construct's threshold is not what the docstring says")
        m = coded.join(by_code, on="code")
        in_census = m["population"].notna()
        same = float((m.loc[in_census, "atree_population"] == m.loc[in_census, "population"]).mean())
        if same < ATREE_MIN_CENSUS_AGREEMENT:
            fail(f"ATREE list: its population equals the census in only {same:.1%} of villages found by code - the codes are not the census's")
        stop_if_failed("checking the ATREE list")
        m = m[in_census].join(lgd.set_index("code")["Panchayat_ID"], on="code")
        m["st_households"] = m["households"] * m["st_pop"] / m["population"].where(m["population"] > 0)
        m["st_households"] = m["st_households"].fillna(0.0)                       # an uninhabited village has none
        m["within"] = m["CFR Type"].isin(FOREST_WITHIN)
        placed = m["Panchayat_ID"].notna()
        q = m[placed & m["within"]]
        t["forest_dependent_households"] = q.groupby("Panchayat_ID")["st_households"].sum().reindex(t.index, fill_value=0.0).round(1)
        t["n_forest_villages"] = q.groupby("Panchayat_ID").size().reindex(t.index, fill_value=0)
        t["households_in_forest_villages"] = q.groupby("Panchayat_ID")["households"].sum().reindex(t.index, fill_value=0)
        # Share of the village's area, on "Total Geographical Area": forest never exceeds that column, whereas it
        # exceeds "Calculated GIS Area" in hundreds of villages, by up to dozens of times. No usable area, no share.
        share = m["forest_ha"] / m["area_ha"].where(m["area_ha"] > 0)
        if (share > 1 + 1e-9).any():
            fail(f"ATREE list: forest inside the boundary exceeds the village's geographical area in {int((share > 1 + 1e-9).sum())} villages - the area column is not what it was")
            stop_if_failed("checking the ATREE list")
        rules = [("on ATREE's list at all", pd.Series(True, index=m.index)), ("forest inside the boundary > 0 ha", m["forest_ha"] > 0),
                 ("ATREE class 'Forest within village' or 'Both'  <- THE CONSTRUCT", m["within"]),
                 ("forest inside the boundary >= 25 ha", m["forest_ha"] >= 25), ("forest inside the boundary >= 50 ha", m["forest_ha"] >= 50),
                 ("forest inside the boundary >= 100 ha", m["forest_ha"] >= 100),
                 ("forest >= 10% of the village's geographical area", share >= 0.10), ("forest >= 25% of the village's geographical area", share >= 0.25),
                 ("forest >= 50% of the village's geographical area", share >= 0.50)]
        unit_ids = t.index[t.index.isin(set(units.loc[is_panchayat, "unit_id"]))]
        construct = q.groupby("Panchayat_ID")["st_households"].sum().reindex(unit_ids, fill_value=0.0)

        def rank_agreement(per_id):
            """Spearman correlation, across the LGD panchayat units, between the construct and what another rule would give."""
            return round(float(construct.rank().corr(per_id.reindex(unit_ids, fill_value=0.0).rank())), 4)

        sensitivity = pd.DataFrame([{"rule": name, "n_villages": int((sel & placed).sum()), "households": int(m.loc[sel & placed, "households"].sum()),
                                     "st_households_estimated": round(float(m.loc[sel & placed, "st_households"].sum()), 1),
                                     "lgd_panchayat_ids_with_any": int(m.loc[sel & placed, "Panchayat_ID"].nunique()),
                                     "spearman_with_the_construct_across_units": rank_agreement(m.loc[sel & placed].groupby("Panchayat_ID")["st_households"].sum())}
                                    for name, sel in rules])
        everyone = (v["households"] * v["st_pop"] / v["population"].where(v["population"] > 0)).fillna(0.0)     # no forest condition at all
        sensitivity.loc[len(sensitivity)] = {
            "rule": "every village of the id, on ATREE's list or not (ST households, forest or no forest)", "n_villages": int(len(v)),
            "households": int(v["households"].sum()), "st_households_estimated": round(float(everyone.sum()), 1),
            "lgd_panchayat_ids_with_any": int(v["Panchayat_ID"].nunique()),
            "spearman_with_the_construct_across_units": rank_agreement(everyone.groupby(v["Panchayat_ID"]).sum())}
        no_code = at[~at["has_code"]]
        atree_meta = {
            "path": rel(a.atree), "bytes": Path(a.atree).stat().st_size, "sha256": sha256(a.atree),
            "registered_in_00_raw": Path(a.atree).resolve().is_relative_to(RAW),
            "rows": int(len(at)), "cfr_type": {k: int(n) for k, n in at["CFR Type"].value_counts().items()},
            "class_boundary_ha": {"highest_forest_in_adjacent_class": float(highest_adjacent), "lowest_forest_in_within_classes": float(lowest_within)},
            "rows_with_no_census_2011_code": {"n": int(len(no_code)), "level": {k: int(n) for k, n in no_code["Level"].value_counts().items()},
                                              "in_the_within_classes": int(no_code["CFR Type"].isin(FOREST_WITHIN).sum()),
                                              "with_a_forest_area": int(no_code["forest_ha"].notna().sum()),
                                              "with_a_household_count": int(no_code["atree_households"].notna().sum())},
            "its_own_household_column": {"blank_among_found_rows": int(m["atree_households"].isna().sum()),
                                         "equal_to_the_census_where_given": int((m["atree_households"] == m["households"]).sum()),
                                         "given": int(m["atree_households"].notna().sum())},
            "area_columns": {"placed_villages_with_no_geographical_area": int((placed & ~(m["area_ha"] > 0)).sum()),
                             "placed_villages_where_forest_exceeds_calculated_gis_area": int((placed & (m["forest_ha"] > m["gis_ha"])).sum()),
                             "placed_villages_where_forest_exceeds_geographical_area": int((placed & (share > 1 + 1e-9)).sum())},
            "qualifying_villages_in_ids_with_no_unit_polygon": {"n": int((~q["Panchayat_ID"].isin(set(units.loc[is_panchayat, "unit_id"]))).sum()),
                                                                "st_households_estimated": round(float(q.loc[~q["Panchayat_ID"].isin(set(units.loc[is_panchayat, "unit_id"])), "st_households"].sum()), 1)},
            "coded_rows": int(len(coded)), "coded_rows_found_in_the_census": int(in_census.sum()),
            "population_equal_to_the_census_share": round(same, 6),
            "found_rows_with_an_lgd_panchayat_id": int(placed.sum()),
            "qualifying_villages": {"n": int(len(q)), "households": int(q["households"].sum()), "st_households_estimated": round(float(q["st_households"].sum()), 1),
                                    "uninhabited": int((q["population"] == 0).sum())},
        }
        checks["atree"] = {"class_boundary_separates": True, "population_agreement_with_census": round(same, 6)}
        print(f"ATREE list: {len(at):,} rows ({dict(at['CFR Type'].value_counts())}); 'adjacent' reaches {highest_adjacent} ha, the 'within' classes start at {lowest_within} ha")
        print(f"  {len(no_code)} rows carry no Census-2011 code ({dict(no_code['Level'].value_counts())}) and cannot be placed; of the {len(coded):,} coded rows "
              f"{int(in_census.sum()):,} are in the census file (population equal in {same:.2%}) and {int(placed.sum()):,} have an LGD panchayat id")
        print(f"  qualifying villages: n = {len(q):,}, {int(q['households'].sum()):,} households, {q['st_households'].sum():,.0f} estimated ST households")
        if not atree_meta["registered_in_00_raw"]:
            print(f"  NOTE the ATREE list was read from {a.atree}, which is NOT in 00_raw - forest_dependent_households rests on an unregistered input")
    else:
        print("no --atree given: forest_dependent_households is left blank")

    # ---- per unit ----------------------------------------------------------------------------------------------
    carried = [c for c in t.columns]
    out = units[["unit_id", "unit_level"] + (["outside_village"] if "outside_village" in units.columns else [])].join(t, on="unit_id")
    for c in ("n_villages", "n_villages_uninhabited", "n_villages_without_polygon", "population_in_villages_without_polygon", "n_forest_villages",
              "households_in_forest_villages", "poverty_rate_population_rated", *COUNTS):
        out[c] = out[c].astype("Int64")
    order = ["unit_id", "unit_level"] + (["outside_village"] if "outside_village" in units.columns else []) + [
        "n_villages", "n_villages_uninhabited", "n_villages_without_polygon", "population", "population_in_villages_without_polygon", "households",
        "st_pop", "st_share", "sc_pop", "sc_share", "adi_2011", "adi_2011_population_covered_share", "adi_2019", "adi_2019_population_covered_share",
        "poverty_rate", "poverty_rate_ppp2", "poverty_rate_population_covered_share", "poverty_rate_population_rated",
        "poverty_rate_shared_shrid_population_share",
        "forest_dependent_households", "n_forest_villages", "households_in_forest_villages"]
    out = out[order].sort_values("unit_id").reset_index(drop=True)

    in_units, off_map = t.loc[t.index.isin(set(out["unit_id"]))], t.loc[no_polygon]
    for k in COUNTS:                                 # every mapped village is in a unit or in an id with no polygon
        if int(out[k].sum()) != int(in_units[k].sum()) or int(in_units[k].sum()) + int(off_map[k].sum()) != int(by_code.loc[lgd["code"], k].sum()):
            fail(f"{k}: units {int(out[k].sum()):,} + ids with no polygon {int(off_map[k].sum()):,} != all mapped villages {int(by_code.loc[lgd['code'], k].sum()):,}")
    if out.loc[out["unit_level"] != "lgd_panchayat", order[3:]].notna().any().any():
        fail("a unit that is not an LGD panchayat carries census figures")
    if (out["st_pop"] > out["population"]).any() or (out["sc_pop"] > out["population"]).any() or (out["forest_dependent_households"] > out["households_in_forest_villages"] + 0.05).any():
        fail("a part exceeds its whole in need_by_unit")
    if (out["poverty_rate"] > out["poverty_rate_ppp2"] + 1e-6).any() or not out["poverty_rate_ppp2"].dropna().between(0, 1).all():
        fail("a poverty rate lies outside 0-1, or the Tendulkar-line rate exceeds the higher-line rate, in need_by_unit")
    if (out["poverty_rate"].notna() != (out["poverty_rate_population_rated"] > 0).fillna(False)).any():
        fail("a unit has a poverty rate and no rated population, or the reverse")
    stop_if_failed("building need_by_unit")
    has_rate = out["poverty_rate"].notna()
    checks["secc"]["units"] = {
        "with_a_rate": int(has_rate.sum()),
        "rate_resting_on_fewer_than_100_people": int((out.loc[has_rate, "poverty_rate_population_rated"] < 100).sum()),
        "rate_exactly_0_or_1": int(out.loc[has_rate, "poverty_rate"].isin([0, 1]).sum()),
        "some_of_the_rate_from_a_shrid_shared_with_another_id": int((out["poverty_rate_shared_shrid_population_share"] > 0).sum()),
        "all_of_the_rate_from_such_shrids": int((out["poverty_rate_shared_shrid_population_share"] == 1).sum()),
        "touched_by_a_shrid_the_module_flags": int(out["unit_id"].isin(flagged_ids).sum())}

    check = pd.DataFrame({"has_unit_polygon": t.index.isin(set(out["unit_id"])).astype(int), "n_villages": t["n_villages"]})
    for k, f in file_cols.items():
        check[k] = t[k]; check[f"panchayat_file_{k}"] = pf[f]
    for year in ("2011", "2019"):
        check[f"adi_{year}"] = t[f"adi_{year}"]; check[f"panchayat_file_adi_{year}"] = pf[f"adi_{year}"]
        check[f"adi_{year}_population_covered_share"] = t[f"adi_{year}_population_covered_share"]
    check = check.reset_index().rename(columns={"Panchayat_ID": "lgd_panchayat_id"})

    OUT.mkdir(exist_ok=True)
    out.to_csv(OUT / "need_by_unit.csv", index=False)
    check.to_csv(OUT / "need_source_check.csv", index=False)
    if sensitivity is not None:
        sensitivity.to_csv(OUT / "need_construct_sensitivity.csv", index=False)
    value_columns = order[3:]
    lp = out[out["unit_level"] == "lgd_panchayat"]
    tables = {"need_by_unit.csv": {"rows": int(len(out)), "units_by_level": {k: int(n) for k, n in out["unit_level"].value_counts().items()},
                                   "columns_all_units": missingness(out, value_columns), "columns_lgd_panchayat_units_only": missingness(lp, value_columns),
                                   "totals_over_units": {k: int(out[k].sum()) for k in COUNTS}},
              "need_source_check.csv": {"rows": int(len(check)), "blank_cells": {c: int(check[c].isna().sum()) for c in check.columns if check[c].isna().any()}}}
    if sensitivity is not None:
        tables["need_construct_sensitivity.csv"] = {"rows": int(len(sensitivity)), "blank_cells": {}}
    inputs = [Path(a.units), VILLAGE_POLYGONS, LGD, PCA, VILLAGE_ADI, PANCHAYAT, SECC, PC_KEYS]
    with open(OUT / "need.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": rel(__file__), "script_sha256": sha256(__file__), "run_utc": started,
            "inputs": [{"path": rel(p), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in inputs],
            "atree_list": atree_meta or "NOT GIVEN - forest_dependent_households is blank",
            "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__, "pyogrio": pyogrio.__version__},
            "definitions": {
                "unit": "an LGD panchayat id (docs/UNITS.md); outside_village units have no census rows and are blank in every column",
                "counts": "Census 2011 Primary Census Abstract, each mapped village or census town once, whether or not it has a polygon",
                "st_share, sc_share": "share of population; blank where the id has no population",
                "adi_2011, adi_2019": "population-weighted mean of the village ADI (5-15) over the villages that have one; blank where none has; "
                                      "*_population_covered_share is the share of the id's population in those villages. 2019 is a prediction",
                "which_columns_carry_the_argument": "st_share is the marginalisation axis; adi_2011 is the development control (adi_2019 is reported only: "
                                                    "it is blank for a third of units); forest_dependent_households is reported and used as a robustness "
                                                    "check, not as the need measure; forest comes from stage 1 (rulings of 5 October 2026)",
                "poverty_rate": "population-weighted mean, over villages whose shrid has one, of SHRUG 2.2's SECC small-area poverty rate at the Tendulkar "
                                "rural line (documented as Rs 27 a day; bracketed from the data in checks_passed.secc). A model estimate, rural only, a share "
                                "of people. poverty_rate_ppp2 is the same at the module's higher line ($2 a day PPP, documented as Rs 31); "
                                "*_population_covered_share is the share of the id's population in villages with a rate; *_population_rated is that "
                                "population; *_shared_shrid_population_share is the part of it whose shrid also holds villages of another id",
                "forest_dependent_households": "REPORTED COLUMN AND ROBUSTNESS CHECK, not the need measure. CONSTRUCT. Estimated ST households (households x ST share of population) in villages ATREE classes "
                                               "'Forest within village' or 'Both' - about 10 ha or more of forest inside the revenue boundary. "
                                               "Villages off ATREE's list add nothing; ATREE rows with no village code are left out. Not a measure of forest use",
                "panchayat_census_adi_data.csv": "cross-check only: it double counts in some ids and dilutes ADI (need_source_check.csv)"},
            "checks_passed": checks,
            "ids_with_no_unit_polygon": {"n": len(no_polygon), **{k: int(off_map[k].sum()) for k in COUNTS}},
            "tables": tables}, fh, indent=2)

    print(f"\nneed_by_unit.csv: n = {len(out):,} units ({len(lp):,} lgd_panchayat with figures, {len(out) - len(lp):,} outside_village blank by design)")
    print(f"  over the lgd_panchayat units: population {int(lp['population'].sum()):,}, households {int(lp['households'].sum()):,}, SC {int(lp['sc_pop'].sum()):,}, ST {int(lp['st_pop'].sum()):,}")
    print(f"  not in any unit: {len(no_polygon)} ids with no polygon (population {int(off_map['population'].sum()):,}); inside units but in villages with no polygon: "
          f"population {int(lp['population_in_villages_without_polygon'].sum()):,} in {int(lp['n_villages_without_polygon'].sum()):,} villages")
    print(f"  {'column':<42}{'n':>7}{'blank':>7}   among the {len(lp):,} lgd_panchayat units")
    for c in value_columns:
        print(f"  {c:<42}{int(lp[c].notna().sum()):>7,}{int(lp[c].isna().sum()):>7,}")
    if sensitivity is not None:
        print(f"\nneed_construct_sensitivity.csv: n = {len(sensitivity)} rules, statewide, villages placed in an LGD panchayat id; "
              f"rank agreement with the construct is across the {len(lp):,} lgd_panchayat units")
        for _, r in sensitivity.iterrows():
            print(f"  {r['rule']:<84}{r['n_villages']:>8,} villages{r['households']:>11,} households{r['st_households_estimated']:>12,.0f} ST households (est.)"
                  f"   Spearman {r['spearman_with_the_construct_across_units']:.4f}")
    print(f"need_source_check.csv: n = {len(check):,} LGD panchayat ids")
    print(f"\ndone. run_utc {started}; outputs in {rel(OUT)}/")


if __name__ == "__main__":
    main()
