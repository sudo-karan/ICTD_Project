#!/usr/bin/env python3
"""
Stage 3 - allocation: what each analysis unit received under MGNREGA, from the geotagged-asset dump.

Every work in the dump is a point. It is assigned to the unit whose polygon contains its lat/lon and to
nothing else: no name matching, and no use of the 10-digit MIS panchayat code in `Work Code`, which has
no documented mapping to the LGD panchayat id (README section 4, stage 3).

    python scripts/04_build_allocation.py --units 10_units/units.gpkg
    python scripts/04_build_allocation.py --units 10_units/units.gpkg 10_units/units_outside_nearest.gpkg 10_units/units_outside_drop.gpkg

In : 00_raw/02_mgnrega/assets_geojson/ODISHA/*.geojson    the 30 district files (rupees)
     00_raw/download_log.csv, 00_raw/data_manifest.csv    sha256 and S3 last-modified of each file
     00_raw/mgnrega_assets/odisha_assets_district_fy_2026-10-04.csv        verified totals to reconcile to
     00_raw/mgnrega_assets/odisha_assets_category_totals_2026-10-04.csv    verified totals to reconcile to
     --units  one or more stage-0 layers. Several are joined in one pass over the dump, which is how the
              sensitivity of the result to the outside-village rule (README 5.1) is measured.
Out: 40_allocation/ and nowhere else. <tag> is the layer's file stem without "units_"; units.gpkg has none.
     allocation_by_unit[__<tag>].csv      one row per unit, INCLUDING units that received nothing
     allocation_by_unit_fy[__<tag>].csv   one row per unit x FY of work start; an absent row means no works
     allocation_unassigned[__<tag>].csv   works that fall inside no unit polygon, by district file x FY
     allocation_join_qa[__<tag>].csv      per district file: where its points landed
     allocation[__<tag>].provenance.json  inputs (bytes, sha256), UTC run time, definitions, checks, n and missingness
     assets_file_qa.csv                   per district file: provenance and missingness; the same for every layer
     assets_district_fy.csv               the dump by district file x FY of work start, before any spatial join
     assets_worktype_flags.csv            every Work Type and the flags it received, for auditing the regexes

READING THE TABLES. pd.read_csv(path, dtype={"unit_id": str, "fy_work_start": str}, keep_default_na=False,
na_values=[""]). The FY label NA is a value, as it is in the verified files, and a default read turns it
into a missing cell and drops those works from any groupby; unit_id mixes numeric ids with OUTSIDE_n.

A UNIT HERE IS A POLYGON. A work counts toward the unit it was geotagged inside, which is not always the
panchayat that recorded it (README 5.8), and an lgd_panchayat unit is the villages stage 0 dissolved under
one LGD panchayat id, which is not always a whole gram panchayat (docs/UNITS.md).

MONEY is in rupees, as in the dump (the MIS reports are in lakh). -1 and null mean "not available" and are
counted, never summed. As in the verified totals, only values above zero enter a sum, so the dump's eleven
negative expenditures are counted as not available too. Every money column has its own count of works
with no expenditure beside it. A money cell is BLANK where the cell has works and none of them reports an
expenditure; it is 0 only where there are no such works at all.

THE FLAGS. A work can carry several. They overlap, so their expenditures must never be added together.
    plantation_category     WorkCategory matches "plant". CoRE Stack's keyword-matched category.
    forestry_worktype       Work Type matches FORESTRY_WORKTYPE_RE from aggregate_nrega_assets.py. Broad in
                            one way: it takes in horticulture, sericulture and nurseries alongside forestry.
    forest_named_worktype   Work Type matches FOREST_NAMED_WORKTYPE_RE: the work type itself names forest or
                            forestry. NOT quite a subset of forestry_worktype: the MIS spells two types
                            "Plntation ... Forstry", which that regex cannot see (5 works, Rs 163,733).
    water                   WorkCategory is one of WATER_CATEGORIES.
NEITHER PLANTATION FLAG IS THE SAFE ONE, so both are reported (README 5.2) and so is where they disagree.
The category puts some roads and buildings under Plantation. The Work Type field is wrong the other way:
in Deogarh's Plantation category the Work Name carries a plantation word (mango, avenue plantation ...) in
323 of the 428 "Maintenance of rural public assets" works and 131 of the 132 "AWC" works, and
forestry_worktype misses every one of the 560. Treat forestry_worktype as a lower bound that is uneven
across districts, not as the stricter measure.
`water` IS A CONSTRUCT, NOT A FIELD, and it is as noisy as the plantation category: by Work Type about a
fifth of its rupees and a quarter of its works are roads, houses and buildings. Audit either flag in
assets_worktype_flags.csv before leaning on it.
THERE IS NO NRM COLUMN, AND NONE MAY BE BUILT PER UNIT. The dump has no NRM marker. Water plus plantation
is not NRM: it is an undercount, because NRM also holds land development, drought proofing and flood
control, and the size of the undercount is not stable. In R6.20 water plus plantation is 90% of NRM in
FY2014-15 and 52% in FY2019-20, so a proxy built on it would carry a time trend that is not in the
spending. NRM comes from R6.20, at district level, and from nowhere else (docs/NRM.md).
Works whose category is NULL or "Un Identified" can carry neither category flag; n_works_category_unknown
counts them.

FINANCIAL YEAR is the year the work STARTED, and each work's whole lifetime expenditure sits in that year.
This is not a spend-by-year panel (README section 2). Coverage effectively ends FY2017-18; works with no
usable start date are kept under fy_work_start = NA so that the yearly rows still add up to the unit total.

PERSONDAYS is written blank wherever no work reports a value above zero. On 2026-10-05 that was every unit:
Total_persondays is -1 for 1,151,852 works and 0 for 150,812, and never positive. Those zeros are not
measured zeros - 1,922 of the same works report Unskilled_Persondays above zero, 370,101 in all.

Needs geopandas, pyogrio, shapely, pandas, numpy.
"""
import argparse, csv, datetime, hashlib, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import pyogrio
import shapely

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from aggregate_nrega_assets import FORESTRY_WORKTYPE_RE, financial_year, year_month   # one definition, shared with the verified totals

RAW = ROOT / "00_raw"
ASSETS = RAW / "02_mgnrega" / "assets_geojson" / "ODISHA"
REF_DISTRICT_FY = RAW / "mgnrega_assets" / "odisha_assets_district_fy_2026-10-04.csv"
REF_CATEGORY = RAW / "mgnrega_assets" / "odisha_assets_category_totals_2026-10-04.csv"
DOWNLOAD_LOG = RAW / "download_log.csv"
MANIFEST = RAW / "data_manifest.csv"
OUT = ROOT / "40_allocation"

N_FILES = 30
MIN_ASSIGNED_SHARE = 0.5          # below this the join has failed (swapped lat/lon, wrong CRS); it is not a result
PLANTATION_CATEGORY_RE = re.compile("plant", re.I)      # the test aggregate_nrega_assets.py applies to WorkCategory
FOREST_NAMED_WORKTYPE_RE = re.compile(r"fore?st", re.I)   # forest, forestry, afforestation, and the dump's "Forstry"
WATER_CATEGORIES = frozenset({"Irrigation - Site level impact", "SWC - Landscape level impact",
                              "Irrigation Site level - Non RWH"})
UNKNOWN_CATEGORIES = frozenset({"NULL", "Un Identified"})   # a missing value, and the description's "undefined work types"
# the 7+1 categories of the data description, as they are spelt in the dump, plus NULL for a missing value
KNOWN_CATEGORIES = WATER_CATEGORIES | UNKNOWN_CATEGORIES | {"Plantation", "Household Livelihood",
                                                            "Agri Impact - HH, Community", "Others - HH, Community"}
READ_WITH = 'pd.read_csv(path, dtype={"unit_id": str, "fy_work_start": str}, keep_default_na=False, na_values=[""])'

FLAGS = ["plantation_category", "forestry_worktype", "forest_named_worktype", "water"]
# (money column, the works it sums over, those of them with no expenditure to sum)
SUMS = [("expenditure_total", "n_works", "n_works_expenditure_na")] \
    + [(f"expenditure_{k}", f"n_works_{k}", f"n_works_{k}_expenditure_na") for k in FLAGS]
MONEY = [m for m, _, _ in SUMS]
COUNTS = [c for _, n, na in SUMS for c in (n, na)] + ["n_works_category_unknown", "n_works_persondays_reported"]
MEASURES = [c for m, n, na in SUMS for c in (n, na, m)] + ["n_works_category_unknown", "persondays", "n_works_persondays_reported"]

fails = []


def fail(msg):
    fails.append(msg)


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Stopped before writing this step's tables.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def amount(v):
    """(value to add, status). In the dump -1 and null mean 'not available', not zero."""
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
        return 0.0, "na"
    if v > 0:
        return float(v), "ok"
    if v == 0:
        return 0.0, "zero"
    return 0.0, ("minus1" if v == -1 else "negative")


def half_up(x):
    """Round to the rupee the way the verified files were rounded: halves go up, not to the even neighbour."""
    return np.floor(x + 0.5)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(path):
    p = Path(path).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def new_worktype():
    return {"n": 0, "exp": 0.0, "n_pl": 0, "exp_pl": 0.0, "n_wa": 0, "exp_wa": 0.0, "categories": Counter()}


def read_district(path):
    """One district file -> per-work columns, a missingness tally and a per-work-type tally."""
    with open(path, encoding="utf-8") as fh:
        obj = json.load(fh)
    feats = obj["features"]
    col = defaultdict(list)
    q = Counter()
    worktypes = defaultdict(new_worktype)
    districts, cat_flags, wt_flags = Counter(), {}, {}
    for f in feats:
        p = f.get("properties") or {}
        cat = re.sub(r"\s+", " ", str(p.get("WorkCategory") or "NULL"))
        wt = str(p.get("Work Type") or "NULL")
        if cat not in cat_flags:
            cat_flags[cat] = (bool(PLANTATION_CATEGORY_RE.search(cat)), cat in WATER_CATEGORIES)
        if wt not in wt_flags:
            wt_flags[wt] = (bool(FORESTRY_WORKTYPE_RE.search(wt)), bool(FOREST_NAMED_WORKTYPE_RE.search(wt)))
        pl, wa = cat_flags[cat]
        fwt, fnw = wt_flags[wt]
        exp, exp_status = amount(p.get("Total_Expenditure"))
        pdy, pdy_status = amount(p.get("Total_persondays"))
        unskilled, unskilled_status = amount(p.get("Unskilled_Persondays"))
        raw_date = p.get("Work_start_date")
        fy = financial_year(raw_date)
        if fy == "NA":
            q["n_start_date_unavailable" if year_month(raw_date) is None else "n_start_year_out_of_range"] += 1
        lat, lon = p.get("lat"), p.get("lon")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and v == v for v in (lat, lon)):
            lat = lon = float("nan"); q["n_latlon_unavailable"] += 1
        else:
            g = f.get("geometry") or {}
            if g.get("type") != "Point" or abs(g["coordinates"][0] - lon) > 1e-9 or abs(g["coordinates"][1] - lat) > 1e-9:
                q["n_latlon_differs_from_geometry"] += 1
        col["lon"].append(lon); col["lat"].append(lat); col["fy"].append(fy); col["category"].append(cat)
        col["category_unknown"].append(cat in UNKNOWN_CATEGORIES)
        col["exp"].append(exp); col["exp_na"].append(exp_status not in ("ok", "zero"))
        col["pdy"].append(pdy); col["pdy_reported"].append(pdy_status == "ok")
        for name, on in zip(FLAGS, (pl, fwt, fnw, wa)):
            col[name].append(on)
        q[f"n_expenditure_{exp_status}"] += 1; q[f"n_persondays_{pdy_status}"] += 1
        if exp_status == "negative":
            q["rupees_negative_excluded"] += p["Total_Expenditure"]
        if unskilled_status == "ok":
            q["n_unskilled_persondays_positive"] += 1; q["unskilled_persondays"] += unskilled
        w = worktypes[wt]; w["n"] += 1; w["exp"] += exp; w["categories"][cat] += 1
        if pl: w["n_pl"] += 1; w["exp_pl"] += exp
        if wa: w["n_wa"] += 1; w["exp_wa"] += exp
        districts[str(p.get("District"))] += 1
    return {"key": Path(path).stem, "name": obj.get("name"), "districts": districts, "n": len(feats),
            "col": col, "q": q, "worktypes": worktypes, "wt_flags": wt_flags}


def load_assets():
    files = sorted(ASSETS.glob("*.geojson"))
    if len(files) != N_FILES:
        fail(f"expected {N_FILES} district files under {rel(ASSETS)}, found {len(files)}")
        stop_if_failed("reading the asset dump")
    log = {r["path"]: r for r in csv.DictReader(open(DOWNLOAD_LOG, encoding="utf-8"))}
    modified = {r["dest"]: r["notes"] for r in csv.DictReader(open(MANIFEST, encoding="utf-8"))}
    ref = pd.read_csv(REF_DISTRICT_FY, dtype={"fy_work_start": str, "pc11_district_code": str}, keep_default_na=False)
    pc11 = dict(zip(ref["s3_key"], ref["pc11_district_code"]))
    if {f.stem for f in files} != set(pc11):
        fail(f"district files and {REF_DISTRICT_FY.name} disagree on the district keys: "
             f"only on disk {sorted({f.stem for f in files} - set(pc11))}, only in the reference {sorted(set(pc11) - {f.stem for f in files})}")
        stop_if_failed("reading the asset dump")

    parts, file_rows, worktypes, wt_flags = [], [], defaultdict(new_worktype), {}
    for i, path in enumerate(files):
        key = path.stem
        logged = log.get(f"02_mgnrega/assets_geojson/ODISHA/{path.name}")
        size, digest = path.stat().st_size, sha256(path)
        if logged is None:
            fail(f"{key}: no row in {DOWNLOAD_LOG.name}, so the file cannot be checked against its download")
        elif (str(size), digest) != (logged["bytes"], logged["sha256"]):
            fail(f"{key}: bytes/sha256 on disk ({size}, {digest[:12]}) differ from {DOWNLOAD_LOG.name} "
                 f"({logged['bytes']}, {logged['sha256'][:12]}) - the file has changed since it was downloaded")
        d = read_district(path)
        if len(d["districts"]) != 1:
            fail(f"{key}: more than one District value in one file: {dict(d['districts'])}")
        df = pd.DataFrame(d["col"])
        df["file"] = i
        parts.append(df)
        m = re.search(r"S3 last-modified ([^.]+)\.", modified.get(f"02_mgnrega/assets_geojson/ODISHA/{path.name}", ""))
        q = d["q"]
        file_rows.append({
            "district_file": key, "geojson_name": d["name"], "district_property": next(iter(d["districts"])),
            "pc11_district_code": pc11[key], "bytes": size, "sha256": digest,
            "s3_last_modified": m.group(1) if m else "",
            "n_works": d["n"], "expenditure_total": df["exp"].sum(),
            "n_expenditure_positive": q["n_expenditure_ok"], "n_expenditure_zero": q["n_expenditure_zero"],
            "n_expenditure_minus1": q["n_expenditure_minus1"], "n_expenditure_null": q["n_expenditure_na"],
            "n_expenditure_negative": q["n_expenditure_negative"], "rupees_negative_excluded": q["rupees_negative_excluded"],
            "n_start_date_unavailable": q["n_start_date_unavailable"], "n_start_year_out_of_range": q["n_start_year_out_of_range"],
            "n_category_unknown": int(df["category_unknown"].sum()),
            "n_persondays_positive": q["n_persondays_ok"], "n_persondays_reported_zero": q["n_persondays_zero"],
            "n_persondays_minus1": q["n_persondays_minus1"], "n_persondays_null": q["n_persondays_na"],
            "n_unskilled_persondays_positive": q["n_unskilled_persondays_positive"], "unskilled_persondays_sum": q["unskilled_persondays"],
            "n_latlon_unavailable": q["n_latlon_unavailable"], "n_latlon_differs_from_geometry": q["n_latlon_differs_from_geometry"],
            **{f"n_works_{f}": int(df[f].sum()) for f in FLAGS},
        })
        for wt, v in d["worktypes"].items():
            t = worktypes[wt]
            for k in ("n", "exp", "n_pl", "exp_pl", "n_wa", "exp_wa"):
                t[k] += v[k]
            t["categories"].update(v["categories"])
        wt_flags.update(d["wt_flags"])
        print(f"  {key:<20} {d['n']:>7} works  Rs {df['exp'].sum():>15,.0f}  expenditure n/a {int(df['exp_na'].sum()):>5}"
              f"  no FY {int((df['fy'] == 'NA').sum()):>5}  S3 last-modified {file_rows[-1]['s3_last_modified'] or '(not in manifest)'}")
    works = pd.concat(parts, ignore_index=True)
    file_qa = pd.DataFrame(file_rows)
    wt_table = pd.DataFrame([{"work_type": wt, "n_works": v["n"], "expenditure_inr": round(v["exp"], 2),
                              "forestry_worktype": int(wt_flags[wt][0]), "forest_named_worktype": int(wt_flags[wt][1]),
                              "n_in_plantation_category": v["n_pl"], "expenditure_in_plantation_category": round(v["exp_pl"], 2),
                              "n_in_water_categories": v["n_wa"], "expenditure_in_water_categories": round(v["exp_wa"], 2),
                              "commonest_category": v["categories"].most_common(1)[0][0]}
                             for wt, v in worktypes.items()]).sort_values("expenditure_inr", ascending=False)
    return files, works, file_qa, wt_table, ref


def reconcile(works, file_qa, ref):
    """Fail loudly unless the parse reproduces the totals already verified in 00_raw/mgnrega_assets/."""
    unknown = sorted(set(works["category"]) - KNOWN_CATEGORIES)
    if unknown:
        fail(f"WorkCategory values outside the 7+1 documented ones: {unknown} - the water flag is defined on that list")
    if (file_qa["n_latlon_differs_from_geometry"] > 0).any():
        fail(f"lat/lon properties differ from the point geometry in {int(file_qa['n_latlon_differs_from_geometry'].sum())} works")

    keys = dict(enumerate(file_qa["district_file"]))
    w = works.assign(district_file=works["file"].map(keys), exp_pl=works["exp"] * works["plantation_category"],
                     exp_fwt=works["exp"] * works["forestry_worktype"])
    mine = w.groupby(["district_file", "fy"]).agg(
        n_works=("exp", "size"), expenditure_inr=("exp", "sum"), plcat_n=("plantation_category", "sum"),
        plcat_exp_inr=("exp_pl", "sum"), fwt_n=("forestry_worktype", "sum"), fwt_exp_inr=("exp_fwt", "sum")).reset_index()
    m = ref.merge(mine, left_on=["s3_key", "fy_work_start"], right_on=["district_file", "fy"], how="outer",
                  suffixes=("_ref", ""), indicator=True)
    for _, r in m[m["_merge"] != "both"].iterrows():
        fail(f"district x FY cell present on one side only ({r['_merge']}): verified {r['s3_key']} {r['fy_work_start']} / parsed {r['district_file']} {r['fy']}")
    both = m[m["_merge"] == "both"]
    # No tolerance. The verified file holds each cell's sum rounded half-up to the rupee, so ours must round to it.
    for c in ("n_works", "plcat_n", "fwt_n"):
        for _, r in both[both[c] != both[c + "_ref"]].iterrows():
            fail(f"{r['s3_key']} {r['fy_work_start']}: {c} {int(r[c])} != verified {int(r[c + '_ref'])}")
    for c in ("expenditure_inr", "plcat_exp_inr", "fwt_exp_inr"):
        for _, r in both[half_up(both[c]) != both[c + "_ref"]].iterrows():
            fail(f"{r['s3_key']} {r['fy_work_start']}: {c} {r[c]:,.2f} != verified {r[c + '_ref']:,} (diff {r[c] - r[c + '_ref']:+,.2f})")

    # The category file was built differently: each district's category sum rounded half-up, then added up.
    cat_ref = pd.read_csv(REF_CATEGORY, keep_default_na=False).set_index("work_category")
    per_file = works.groupby(["file", "category"]).agg(n_works=("exp", "size"), expenditure_inr=("exp", "sum"))
    per_file["expenditure_inr"] = half_up(per_file["expenditure_inr"])
    cat = per_file.groupby("category").sum()
    if set(cat.index) != set(cat_ref.index):
        fail(f"category set differs from {REF_CATEGORY.name}: {sorted(set(cat.index) ^ set(cat_ref.index))}")
    for name in sorted(set(cat.index) & set(cat_ref.index)):
        for c in ("n_works", "expenditure_inr"):
            if int(cat.loc[name, c]) != int(cat_ref.loc[name, c]):
                fail(f"category {name!r}: {c} {int(cat.loc[name, c]):,} != verified {int(cat_ref.loc[name, c]):,}")
    stop_if_failed("reconciling to the verified totals")
    print(f"\nOK  {len(works):,} works reconcile to {REF_DISTRICT_FY.name} in all {len(both)} district x FY cells: works, expenditure,")
    print("    and both plantation flags' works and expenditure - every figure exact to the rupee")
    print(f"OK  all {len(cat)} work categories reconcile to {REF_CATEGORY.name}: works and rupees exact")
    return {"district_fy_cells_exact": int(len(both)), "categories_exact": int(len(cat)),
            "rounding": "verified figures are sums rounded half-up to the rupee; compared after the same rounding, no tolerance",
            "what_this_does_not_test": "the water and forest_named_worktype flags, which have no verified reference"}


def tag_of(path):
    stem = Path(path).stem
    return "" if stem == "units" else (stem[len("units_"):] if stem.startswith("units_") else stem)


def load_units(path):
    if "units" not in {name for name, _ in pyogrio.list_layers(path)}:
        sys.exit(f"{path} has no layer named 'units' - it should be the output of 01_build_units.py")
    u = gpd.read_file(path, layer="units")
    if "unit_id" not in u.columns:
        sys.exit(f"{path} has no unit_id column")
    if u["unit_id"].isna().any() or not u["unit_id"].is_unique:
        sys.exit(f"{path}: unit_id must be present and unique to aggregate on - {int(u['unit_id'].isna().sum())} missing, "
                 f"{int(u['unit_id'].duplicated().sum())} duplicated")
    if u.crs is None:
        sys.exit(f"{path} has no CRS; refusing to guess one for a point-in-polygon join")
    if u.crs.to_epsg() != 4326:
        u = u.to_crs("EPSG:4326")        # the dump's lat/lon are WGS84 degrees
    n_bad = int((~u.geometry.is_valid).sum())
    if n_bad:
        u["geometry"] = u.geometry.make_valid()
        print(f"  repaired {n_bad} invalid unit geometries")
    u["unit_id"] = u["unit_id"].astype(str)
    return u.sort_values("unit_id").reset_index(drop=True)


def point_in_polygon(units, lon, lat):
    """Position of the containing unit for each point, -1 for none, and how many units claimed each point."""
    ok = np.isfinite(lon) & np.isfinite(lat)
    where = np.flatnonzero(ok)
    tree = shapely.STRtree(shapely.points(lon[ok], lat[ok]))
    ui, pi = tree.query(units.geometry.values, predicate="intersects")    # inside, or on the boundary
    order = np.lexsort((ui, pi))        # a point on a shared boundary goes to the unit that sorts first by unit_id
    ui, pi = ui[order], pi[order]
    first = np.r_[True, pi[1:] != pi[:-1]] if len(pi) else np.zeros(0, bool)
    unit_of = np.full(len(lon), -1)
    unit_of[where[pi[first]]] = ui[first]
    claims = np.zeros(len(lon), int)
    claims[where] = np.bincount(pi, minlength=len(where))
    return unit_of, claims


def measure(frame, by):
    """Sum the measures over `by`. Counts are integers, money is unrounded rupees."""
    f = frame.assign(_one=1, **{f"_exp_{k}": frame["exp"] * frame[k] for k in FLAGS},
                     **{f"_na_{k}": frame["exp_na"] & frame[k] for k in FLAGS})
    agg = {"n_works": ("_one", "sum"), "n_works_expenditure_na": ("exp_na", "sum"), "expenditure_total": ("exp", "sum"),
           "n_works_category_unknown": ("category_unknown", "sum"),
           "persondays": ("pdy", "sum"), "n_works_persondays_reported": ("pdy_reported", "sum")}
    for k in FLAGS:
        agg[f"n_works_{k}"] = (k, "sum"); agg[f"n_works_{k}_expenditure_na"] = (f"_na_{k}", "sum")
        agg[f"expenditure_{k}"] = (f"_exp_{k}", "sum")
    return f.groupby(by, observed=True).agg(**agg).reset_index()


def tidy(t):
    """Column order, integer counts, rupees to the paisa, and a blank wherever the dump holds nothing to report."""
    t = t.copy()
    for c in COUNTS:
        t[c] = t[c].fillna(0).astype("int64")
    for money, n, na in SUMS:          # works but no expenditure for any of them: unknown, not zero
        t[money] = t[money].fillna(0.0).round(2).where((t[n] == 0) | (t[na] < t[n])).astype("Float64")
    t["persondays"] = t["persondays"].where(t["n_works_persondays_reported"] > 0).astype("Float64")
    return t[[c for c in t.columns if c not in MEASURES] + MEASURES]


def describe(t):
    """n and missingness for one output table, for the sidecar and the console."""
    d = {"rows": int(len(t)), "blank_cells": {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}}
    for c in ("n_works", "n_works_expenditure_na", "n_works_category_unknown"):
        if c in t.columns:
            d[c] = int(t[c].sum())
    if "expenditure_total" in t.columns:
        d["expenditure_total_inr"] = round(float(t["expenditure_total"].sum()), 2)
    return d


def allocate(units_path, units, works, file_qa, totals, run):
    tag = tag_of(units_path)
    sfx = f"__{tag}" if tag else ""
    label = tag or "units"
    print(f"\n=== {rel(units_path)}" + (f"  (tag {tag})" if tag else ""))
    unit_of, claims = point_in_polygon(units, works["lon"].to_numpy(), works["lat"].to_numpy())
    w = works.assign(unit=unit_of)
    inside, outside_all = w[w["unit"] >= 0], w[w["unit"] < 0]
    if len(inside) < MIN_ASSIGNED_SHARE * len(w):
        fail(f"{label}: only {len(inside):,} of {len(w):,} works fall inside a unit. That is a failed join "
             f"(swapped lat/lon, or a layer in the wrong CRS), not a result")
    stop_if_failed(f"joining to {rel(units_path)}")

    # unrounded sums first, so the conservation checks are not at the mercy of rounding 100,000 rows
    raw_unit = measure(inside, "unit")
    raw_fy = measure(inside, ["unit", "fy"])
    raw_un = measure(outside_all, ["file", "fy"])
    for c in COUNTS + MONEY:
        tol = 0 if c in COUNTS else 0.01
        if abs(raw_unit[c].sum() + raw_un[c].sum() - totals[c]) > tol:
            fail(f"{label}: {c} in units + unassigned = {raw_unit[c].sum() + raw_un[c].sum():,.2f} but the dump holds {totals[c]:,.2f}")
        if abs(raw_fy[c].sum() - raw_unit[c].sum()) > tol:
            fail(f"{label}: {c} is {raw_unit[c].sum():,.2f} by unit but {raw_fy[c].sum():,.2f} by unit and FY")
    for t, name in ((raw_unit, "by-unit"), (raw_fy, "by-unit-by-FY"), (raw_un, "unassigned")):
        for money, n, na in SUMS[1:]:           # a flag is a subset of the works in its cell
            if (t[n] > t["n_works"]).any() or (t[na] > t[n]).any() or (t[money] > t["expenditure_total"] + 0.01).any():
                fail(f"{label}: {money} or its counts exceed the cell total in the {name} table")
    if not raw_unit["unit"].is_unique:
        fail(f"{label}: a unit appears twice in the by-unit table")
    stop_if_failed(f"allocating to {rel(units_path)}")

    ids = units[["unit_id"] + [c for c in ("unit_level", "outside_village") if c in units.columns]]
    by_unit = pd.concat([ids, raw_unit.set_index("unit").reindex(range(len(units))).reset_index(drop=True)], axis=1)
    by_unit = tidy(by_unit)          # units arrive sorted by unit_id; those with no works are zero-filled here

    by_fy = raw_fy.rename(columns={"fy": "fy_work_start"})
    by_fy.insert(0, "unit_id", units["unit_id"].to_numpy()[by_fy["unit"].to_numpy()])
    by_fy = tidy(by_fy.drop(columns="unit")).sort_values(["unit_id", "fy_work_start"]).reset_index(drop=True)

    keys = file_qa["district_file"].to_numpy()
    unassigned = raw_un.rename(columns={"fy": "fy_work_start"})
    unassigned.insert(0, "district_file", keys[unassigned["file"].to_numpy()])
    unassigned = tidy(unassigned.drop(columns="file")).sort_values(["district_file", "fy_work_start"]).reset_index(drop=True)

    # where each district file's points landed
    is_outside = units["outside_village"].to_numpy() == 1 if "outside_village" in units.columns else np.zeros(len(units), bool)
    lands_outside = np.zeros(len(w), bool); lands_outside[unit_of >= 0] = is_outside[unit_of[unit_of >= 0]]
    qa = pd.DataFrame({"file": w["file"], "exp": w["exp"], "assigned": unit_of >= 0, "outside": lands_outside,
                       "boundary": claims > 1})
    if "pc11_district_code" in units.columns:        # 0 = the unit carries no district code (outside-village blocks)
        unit_district = pd.to_numeric(units["pc11_district_code"], errors="coerce").fillna(0).astype(int).to_numpy()
        got = np.zeros(len(w), int); got[unit_of >= 0] = unit_district[unit_of[unit_of >= 0]]
        own = file_qa["pc11_district_code"].astype(int).to_numpy()[w["file"].to_numpy()]
        qa["other_district"] = (got > 0) & (got != own)
        qa["district_unknown"] = (unit_of >= 0) & (got == 0)
    else:
        qa["other_district"] = False; qa["district_unknown"] = unit_of >= 0
    for c in ("assigned", "outside", "other_district"):
        qa[f"exp_{c}"] = qa["exp"] * qa[c]
    join_qa = qa.groupby("file").agg(
        n_works=("exp", "size"), n_assigned=("assigned", "sum"), n_in_outside_village_unit=("outside", "sum"),
        n_on_shared_boundary=("boundary", "sum"), n_in_unit_of_another_district=("other_district", "sum"),
        n_in_unit_with_no_district_code=("district_unknown", "sum"), expenditure_total=("exp", "sum"),
        expenditure_assigned=("exp_assigned", "sum"), expenditure_in_outside_village_unit=("exp_outside", "sum"),
        expenditure_in_unit_of_another_district=("exp_other_district", "sum")).reset_index()
    join_qa.insert(0, "district_file", keys[join_qa["file"].to_numpy()])
    join_qa = join_qa.drop(columns="file")
    join_qa.insert(3, "n_unassigned", join_qa["n_works"] - join_qa["n_assigned"])
    join_qa["expenditure_unassigned"] = join_qa["expenditure_total"] - join_qa["expenditure_assigned"]
    join_qa[[c for c in join_qa.columns if c.startswith("expenditure")]] = join_qa.filter(like="expenditure").round(2)

    if len(by_unit) != len(units) or not by_unit["unit_id"].is_unique or int(by_unit["n_works"].sum()) != len(inside):
        fail(f"{label}: the by-unit table has {len(by_unit)} rows and {int(by_unit['n_works'].sum()):,} works "
             f"for {len(units)} units and {len(inside):,} assigned works")
    stop_if_failed(f"allocating to {rel(units_path)}")

    OUT.mkdir(exist_ok=True)
    names = {"by_unit": f"allocation_by_unit{sfx}.csv", "by_unit_fy": f"allocation_by_unit_fy{sfx}.csv",
             "unassigned": f"allocation_unassigned{sfx}.csv", "join_qa": f"allocation_join_qa{sfx}.csv"}
    by_unit.to_csv(OUT / names["by_unit"], index=False)
    by_fy.to_csv(OUT / names["by_unit_fy"], index=False)
    unassigned.to_csv(OUT / names["unassigned"], index=False)
    join_qa.to_csv(OUT / names["join_qa"], index=False)

    n = len(w)
    with_works = by_unit["n_works"] > 0
    level = by_unit["unit_level"] if "unit_level" in by_unit.columns else pd.Series("unit", index=by_unit.index)
    summary = {
        "units": int(len(units)), "units_by_level": {k: int(v) for k, v in level.value_counts().items()},
        "units_with_no_works": int((~with_works).sum()),
        "units_with_no_works_by_level": {k: int(v) for k, v in level[~with_works].value_counts().items()},
        "units_with_works_but_no_expenditure_reported": int(by_unit["expenditure_total"].isna().sum()),
        "works_total": n, "works_assigned": int(len(inside)), "works_unassigned": int(len(outside_all)),
        "works_with_no_latlon": int((~np.isfinite(w["lon"])).sum()),
        "works_on_a_shared_boundary": int((claims > 1).sum()),
        "works_in_outside_village_units": int(lands_outside.sum()),
        "works_in_unit_of_another_district": int(qa["other_district"].sum()),
        "works_in_unit_with_no_district_code": int(qa["district_unknown"].sum()),
        "expenditure_total_inr": round(float(w["exp"].sum()), 2),
        "expenditure_assigned_inr": round(float(inside["exp"].sum()), 2),
        "expenditure_unassigned_inr": round(float(outside_all["exp"].sum()), 2),
        "expenditure_in_outside_village_units_inr": round(float(w["exp"][lands_outside].sum()), 2),
        "expenditure_in_unit_of_another_district_inr": round(float(w["exp"][qa["other_district"].to_numpy()].sum()), 2),
    }
    tables = {names["by_unit"]: describe(by_unit), names["by_unit_fy"]: describe(by_fy),
              names["unassigned"]: describe(unassigned), names["join_qa"]: describe(join_qa)}
    sidecar = {**run, "units_layer": {"path": rel(units_path), "bytes": Path(units_path).stat().st_size,
                                      "sha256": sha256(units_path), "tag": tag},
               "join": summary, "tables": tables}
    with open(OUT / f"allocation{sfx}.provenance.json", "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, indent=2)

    s = summary
    print(f"  units {s['units']:,} {s['units_by_level']}; with no works at all {s['units_with_no_works']:,} {s['units_with_no_works_by_level']};"
          f" with works but no expenditure reported for any of them {s['units_with_works_but_no_expenditure_reported']:,}")
    print(f"  works assigned   {s['works_assigned']:>9,} of {n:,} ({s['works_assigned'] / n:.2%})   Rs {s['expenditure_assigned_inr'] / 1e7:>9,.1f} cr")
    print(f"  works unassigned {s['works_unassigned']:>9,} ({s['works_unassigned'] / n:.2%})                 Rs {s['expenditure_unassigned_inr'] / 1e7:>9,.1f} cr   inside no unit polygon")
    print(f"  of the assigned: in outside-village units {s['works_in_outside_village_units']:,} (Rs {s['expenditure_in_outside_village_units_inr'] / 1e7:,.1f} cr); "
          f"on a shared boundary {s['works_on_a_shared_boundary']:,}; in a unit of another district than their file "
          f"{s['works_in_unit_of_another_district']:,} (Rs {s['expenditure_in_unit_of_another_district_inr'] / 1e7:,.1f} cr); "
          f"in a unit with no district code {s['works_in_unit_with_no_district_code']:,}")
    for name, d in tables.items():
        print(f"  wrote {name}: n = {d['rows']:,} rows, {d['n_works']:,} works; blank cells {d['blank_cells'] or 'none'}")
    return tag, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", nargs="+", required=True, help="stage-0 unit layer(s), e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    tags = [tag_of(p) for p in a.units]
    if len(set(tags)) != len(tags):
        sys.exit(f"two unit layers would write the same output files (tags {tags}); rename one")
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    layers = [load_units(p) for p in a.units]        # before the long read, so a bad layer stops the run at once

    print(f"reading {rel(ASSETS)}")
    files, works, file_qa, wt_table, ref = load_assets()
    stop_if_failed("reading the asset dump")
    checks = reconcile(works, file_qa, ref)
    works["fy"] = pd.Categorical(works["fy"], categories=sorted(set(works["fy"]) - {"NA"}) + ["NA"], ordered=True)

    whole = measure(works.assign(_all=0), "_all").iloc[0]
    totals = {**{c: int(whole[c]) for c in COUNTS}, **{c: float(whole[c]) for c in MONEY}}
    n = len(works)
    unknown_rupees = float(works["exp"][works["category_unknown"]].sum())
    print(f"\nthe dump: n = {n:,} works, Rs {totals['expenditure_total'] / 1e7:,.1f} crore")
    print(f"  expenditure not available (-1, null or negative): {totals['n_works_expenditure_na']:,} works ({totals['n_works_expenditure_na'] / n:.2%})"
          f" - of which -1: {int(file_qa['n_expenditure_minus1'].sum()):,}, null: {int(file_qa['n_expenditure_null'].sum()):,},"
          f" negative: {int(file_qa['n_expenditure_negative'].sum()):,} (Rs {file_qa['rupees_negative_excluded'].sum():,.0f} left out)")
    print(f"  expenditure reported as zero: {int(file_qa['n_expenditure_zero'].sum()):,} works")
    print(f"  no usable start date, so FY = NA: {int((works['fy'] == 'NA').sum()):,} works"
          f" - {int(file_qa['n_start_date_unavailable'].sum()):,} with no date, {int(file_qa['n_start_year_out_of_range'].sum()):,} with a year outside 2004-2027")
    print(f"  category NULL or Un Identified, so neither category flag can apply: {totals['n_works_category_unknown']:,} works"
          f" ({totals['n_works_category_unknown'] / n:.2%}), Rs {unknown_rupees / 1e7:,.1f} cr")
    print(f"  persondays above zero: {totals['n_works_persondays_reported']:,} works; -1: {int(file_qa['n_persondays_minus1'].sum()):,};"
          f" reported as zero: {int(file_qa['n_persondays_reported_zero'].sum()):,}" + ("  -> persondays is left blank" if not totals["n_works_persondays_reported"] else ""))
    print(f"    (Unskilled_Persondays above zero: {int(file_qa['n_unskilled_persondays_positive'].sum()):,} works, {file_qa['unskilled_persondays_sum'].sum():,.0f} persondays - not used)")
    print("  flags (overlapping - never add them); 'no exp.' = works carrying the flag with no expenditure to sum:")
    for k in FLAGS:
        print(f"    {k:<22} {totals[f'n_works_{k}']:>9,} works  no exp. {totals[f'n_works_{k}_expenditure_na']:>6,}  Rs {totals[f'expenditure_{k}'] / 1e7:>8,.1f} cr  "
              f"{totals[f'expenditure_{k}'] / totals['expenditure_total']:>6.2%} of expenditure")
    print("    (no NRM column: the dump has no NRM marker, and water + plantation undercounts NRM by a share that moves - docs/NRM.md)")
    pl, fwt, fnw = works["plantation_category"], works["forestry_worktype"], works["forest_named_worktype"]
    disagree = {"plantation_category_but_not_forestry_worktype": pl & ~fwt, "forestry_worktype_but_not_plantation_category": fwt & ~pl,
                "forest_named_but_not_forestry_worktype": fnw & ~fwt, "forest_named_but_not_plantation_category": fnw & ~pl}
    disagree = {k: {"n_works": int(v.sum()), "expenditure_inr": round(float(works["exp"][v].sum()), 2)} for k, v in disagree.items()}
    print("  where the plantation flags disagree (README 5.2 - report both):")
    for k, v in disagree.items():
        print(f"    {k.replace('_', ' '):<48} {v['n_works']:>7,} works  Rs {v['expenditure_inr'] / 1e7:>7,.2f} cr")

    OUT.mkdir(exist_ok=True)
    file_qa = file_qa.round({"expenditure_total": 2, "rupees_negative_excluded": 2})
    file_qa.to_csv(OUT / "assets_file_qa.csv", index=False)
    wt_table.to_csv(OUT / "assets_worktype_flags.csv", index=False)
    district_fy = measure(works, ["file", "fy"]).rename(columns={"fy": "fy_work_start"})
    for i, c in enumerate(("district_file", "district_property", "pc11_district_code")):
        district_fy.insert(i, c, file_qa[c].to_numpy()[district_fy["file"].to_numpy()])
    district_fy = tidy(district_fy.drop(columns="file")).sort_values(["district_file", "fy_work_start"]).reset_index(drop=True)
    district_fy.to_csv(OUT / "assets_district_fy.csv", index=False)
    plain = {"assets_file_qa.csv": describe(file_qa), "assets_district_fy.csv": describe(district_fy),
             "assets_worktype_flags.csv": describe(wt_table)}
    print(f"\n  wrote assets_file_qa.csv: n = {len(file_qa)} district files, {plain['assets_file_qa.csv']['n_works']:,} works; "
          f"blank cells {plain['assets_file_qa.csv']['blank_cells'] or 'none'}; S3 last-modified dates "
          f"{dict(Counter(file_qa['s3_last_modified']))} - not one snapshot")
    print(f"  wrote assets_district_fy.csv: n = {len(district_fy)} district x FY rows, {plain['assets_district_fy.csv']['n_works']:,} works;"
          f" blank cells {plain['assets_district_fy.csv']['blank_cells'] or 'none'}")
    print(f"  wrote assets_worktype_flags.csv: n = {len(wt_table)} work types, {plain['assets_worktype_flags.csv']['n_works']:,} works; "
          f"blank cells {plain['assets_worktype_flags.csv']['blank_cells'] or 'none'}; {int(wt_table['forestry_worktype'].sum())} types match the forestry regex,"
          f" {int(wt_table['forest_named_worktype'].sum())} are forest-named")

    run = {
        "script": rel(__file__), "script_sha256": sha256(__file__), "run_utc": started,
        "inputs": [{"path": rel(f), "bytes": int(b), "sha256": s, "s3_last_modified": lm}
                   for f, b, s, lm in zip(files, file_qa["bytes"], file_qa["sha256"], file_qa["s3_last_modified"])]
                  + [{"path": rel(p), "bytes": p.stat().st_size, "sha256": sha256(p)}
                     for p in (REF_DISTRICT_FY, REF_CATEGORY, DOWNLOAD_LOG, MANIFEST, HERE / "aggregate_nrega_assets.py")],
        "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__,
                     "geopandas": gpd.__version__, "shapely": shapely.__version__, "geos": shapely.geos_version_string,
                     "pyogrio": pyogrio.__version__},
        "read_the_tables_with": READ_WITH,
        "definitions": {
            "units_of_money": "rupees",
            "unit": "a polygon. A work counts toward the unit it was geotagged inside, which is not always the panchayat that recorded it. "
                    "unit_level lgd_panchayat is an LGD panchayat id, not a gram panchayat (docs/UNITS.md)",
            "financial_year": "FY of Work_start_date (April-March); the work's whole lifetime expenditure sits in that year. "
                              "The label NA (no usable start date) is a value, not a missing cell",
            "not_available": "-1, null and negative Total_Expenditure are counted in the *_expenditure_na columns and add nothing to any sum",
            "blank_money_cell": "the cell has works and none of them reports an expenditure. 0 means there are no such works",
            "plantation_category": f"WorkCategory matches /{PLANTATION_CATEGORY_RE.pattern}/i",
            "forestry_worktype": f"Work Type matches /{FORESTRY_WORKTYPE_RE.pattern}/i. A lower bound: plantations filed under a generic Work Type are missed",
            "forest_named_worktype": f"Work Type matches /{FOREST_NAMED_WORKTYPE_RE.pattern}/i. Not quite a subset of forestry_worktype (see flag_disagreement)",
            "water": f"CONSTRUCT - WorkCategory in {sorted(WATER_CATEGORIES)}. Noisy: audit it in assets_worktype_flags.csv",
            "nrm": "NOT IN THESE TABLES, and never to be built per unit. The dump has no NRM marker; water + plantation undercounts NRM "
                   "by a share that is not stable over time. NRM comes from R6.20 at district level only (docs/NRM.md)",
            "n_works_category_unknown": f"WorkCategory in {sorted(UNKNOWN_CATEGORIES)}; such works can carry neither category flag",
            "overlap": "the flags overlap. Never add their expenditures",
            "persondays": "sum of Total_persondays above zero; blank where no work in the cell reports one",
            "join": "point-in-polygon on the lat/lon properties (WGS84); a point on a shared boundary goes to the unit that sorts first by unit_id",
        },
        "checks_passed": {**checks, "files_match_download_log_sha256": len(files),
                          "works": n, "expenditure_total_inr": round(totals["expenditure_total"], 2)},
        "dump": {"n_works": n, **{k: (round(v, 2) if isinstance(v, float) else v) for k, v in totals.items()},
                 "expenditure_category_unknown_inr": round(unknown_rupees, 2),
                 "n_works_fy_na": int((works["fy"] == "NA").sum()),
                 "n_expenditure_minus1": int(file_qa["n_expenditure_minus1"].sum()),
                 "n_expenditure_null": int(file_qa["n_expenditure_null"].sum()),
                 "n_expenditure_negative": int(file_qa["n_expenditure_negative"].sum()),
                 "n_expenditure_zero": int(file_qa["n_expenditure_zero"].sum()),
                 "n_persondays_minus1": int(file_qa["n_persondays_minus1"].sum()),
                 "n_persondays_reported_zero": int(file_qa["n_persondays_reported_zero"].sum()),
                 "n_unskilled_persondays_positive": int(file_qa["n_unskilled_persondays_positive"].sum()),
                 "unskilled_persondays_sum": float(file_qa["unskilled_persondays_sum"].sum())},
        "flag_disagreement": disagree,
        "unit_independent_tables": plain,
    }
    results = [allocate(p, u, works, file_qa, totals, run) for p, u in zip(a.units, layers)]

    if len(results) > 1:
        print("\nsensitivity to the unit layer (README 5.1) - n = %s works in every row" % f"{n:,}")
        print(f"  {'layer':<14}{'units':>8}{'no works':>10}{'assigned':>11}{'unassigned':>12}{'Rs cr assigned':>16}{'Rs cr unassigned':>18}{'Rs cr outside-village':>23}")
        for tag, s in results:
            print(f"  {tag or 'units':<14}{s['units']:>8,}{s['units_with_no_works']:>10,}{s['works_assigned']:>11,}{s['works_unassigned']:>12,}"
                  f"{s['expenditure_assigned_inr'] / 1e7:>16,.1f}{s['expenditure_unassigned_inr'] / 1e7:>18,.1f}"
                  f"{s['expenditure_in_outside_village_units_inr'] / 1e7:>23,.1f}")
    print(f"\ndone. run_utc {started}; outputs in {rel(OUT)}/")


if __name__ == "__main__":
    main()
