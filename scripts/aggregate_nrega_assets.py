#!/usr/bin/env python3
"""
Aggregate the CoRE Stack MGNREGA geotagged-asset dump (district GeoJSON files) to
Gram Panchayat x financial year x work category.

Input : <dest>/02_mgnrega/assets_geojson/ODISHA/*.geojson   (downloaded by collect_data.py)
Output: <dest>/02_mgnrega/derived/
          odisha_assets_gp_fy_category.csv   one row per GP x FY x WorkCategory
          odisha_assets_gp_summary.csv       one row per GP (all years pooled)
          odisha_assets_district_fy.csv      one row per district x FY
          odisha_assets_worktype_totals.csv  one row per Work Type (to audit the two forestry flags)

Two forestry flags are produced, because the dump's own category is noisy:
  plcat : WorkCategory contains "plant"  (CoRE Stack's keyword-matched category; in Deogarh it also
          catches 'Maintenance of rural public assets' and 'AWC' works)
  fwt   : the Work Type field itself matches FORESTRY_WORKTYPE_RE (stricter; edit the regex to taste)

Standard library only.  Usage:  python aggregate_nrega_assets.py --dest ./ictd_data
"""
import argparse, csv, glob, json, os, re, sys
from collections import defaultdict

FORESTRY_WORKTYPE_RE = re.compile(r"plantation|afforestation|nursery|forest|horticulture|sericulture|bamboo|shelter ?belt", re.I)
PANCHAYAT_CODE_RE = re.compile(r"^(\d{10})/")          # MIS work code = <10-digit panchayat code>/<type>/<serial>
MONTHS = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}

def year_month(s):
    """The dump mixes three date formats: '2017-08-09 00:00:00', '01/01/2007' (d/m/Y), '01-APR-17 11:54:32'."""
    if s is None:
        return None
    s = str(s).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return int(m.group(3)), int(m.group(2))
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{2,4})", s)
    if m:
        y = int(m.group(3)); y = y + 2000 if y < 100 else y
        return y, MONTHS.get(m.group(2).upper(), 1)
    return None

def financial_year(s):
    ym = year_month(s)
    if not ym or not (2004 <= ym[0] <= 2027):
        return "NA"
    y = ym[0] if ym[1] >= 4 else ym[0] - 1
    return f"{y}-{(y + 1) % 100:02d}"

def num(v):
    return float(v) if isinstance(v, (int, float)) and v > 0 else 0.0     # -1 and null are 'not available' in the dump

def aggregate_file(path):
    with open(path, encoding="utf-8") as fh:
        feats = json.load(fh)["features"]
    district = os.path.splitext(os.path.basename(path))[0]
    cell = defaultdict(lambda: [0, 0.0, 0.0])        # (code, fy, category) -> [n, exp, persondays]
    gp = {}                                          # code -> dict
    dfy = defaultdict(lambda: [0, 0.0, 0, 0.0, 0, 0.0])
    wt_tot = defaultdict(lambda: [0, 0.0, 0, 0])     # work type -> [n, exp, n_plcat, n_fwt]
    for f in feats:
        p = f.get("properties") or {}
        cat = re.sub(r"\s+", " ", str(p.get("WorkCategory") or "NULL"))
        wt = str(p.get("Work Type") or "NULL")
        exp = num(p.get("Total_Expenditure")); pd_ = num(p.get("Total_persondays"))
        fy = financial_year(p.get("Work_start_date"))
        m = PANCHAYAT_CODE_RE.match(str(p.get("Work Code") or ""))
        code = m.group(1) if m else "NA"
        plcat = bool(re.search("plant", cat, re.I)); fwt = bool(FORESTRY_WORKTYPE_RE.search(wt))
        c = cell[(code, fy, cat)]; c[0] += 1; c[1] += exp; c[2] += pd_
        g = gp.setdefault(code, {"district": district, "block": str(p.get("Block") or "").upper(),
                                 "panchayat": str(p.get("Panchayat") or p.get("Gram_panchayat") or "").upper(),
                                 "n": 0, "exp": 0.0, "plcat_n": 0, "plcat_exp": 0.0, "fwt_n": 0, "fwt_exp": 0.0,
                                 "lat_sum": 0.0, "lon_sum": 0.0, "n_geo": 0})
        g["n"] += 1; g["exp"] += exp
        if plcat: g["plcat_n"] += 1; g["plcat_exp"] += exp
        if fwt: g["fwt_n"] += 1; g["fwt_exp"] += exp
        geom = f.get("geometry")
        if geom and geom.get("type") == "Point":
            g["lon_sum"] += geom["coordinates"][0]; g["lat_sum"] += geom["coordinates"][1]; g["n_geo"] += 1
        d = dfy[fy]; d[0] += 1; d[1] += exp
        if plcat: d[2] += 1; d[3] += exp
        if fwt: d[4] += 1; d[5] += exp
        w = wt_tot[wt]; w[0] += 1; w[1] += exp; w[2] += plcat; w[3] += fwt
    return district, len(feats), cell, gp, dfy, wt_tot

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", default="./ictd_data")
    ap.add_argument("--state", default="ODISHA")
    a = ap.parse_args()
    src = os.path.join(a.dest, "02_mgnrega", "assets_geojson", a.state)
    out = os.path.join(a.dest, "02_mgnrega", "derived"); os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "*.geojson")))
    if not files:
        sys.exit(f"no GeoJSON files under {src} - run collect_data.py --only nrega_s3 first")
    pre = a.state.lower()
    all_wt = defaultdict(lambda: [0, 0.0, 0, 0]); totals = []
    with open(os.path.join(out, f"{pre}_assets_gp_fy_category.csv"), "w", newline="", encoding="utf-8") as f1, \
         open(os.path.join(out, f"{pre}_assets_gp_summary.csv"), "w", newline="", encoding="utf-8") as f2, \
         open(os.path.join(out, f"{pre}_assets_district_fy.csv"), "w", newline="", encoding="utf-8") as f3:
        w1 = csv.writer(f1); w2 = csv.writer(f2); w3 = csv.writer(f3)
        w1.writerow(["district_file", "mis_panchayat_code", "block", "panchayat", "fy_work_start", "work_category", "n_works", "expenditure_inr", "persondays"])
        w2.writerow(["district_file", "mis_panchayat_code", "block", "panchayat", "n_works", "expenditure_inr", "plcat_n", "plcat_exp_inr",
                     "fwt_n", "fwt_exp_inr", "plcat_share_of_exp", "fwt_share_of_exp", "centroid_lat", "centroid_lon"])
        w3.writerow(["district_file", "fy_work_start", "n_works", "expenditure_inr", "plcat_n", "plcat_exp_inr", "fwt_n", "fwt_exp_inr"])
        for path in files:
            district, n, cell, gp, dfy, wt_tot = aggregate_file(path)
            for (code, fy, cat), (cn, ce, cp) in sorted(cell.items()):
                g = gp[code]; w1.writerow([district, code, g["block"], g["panchayat"], fy, cat, cn, round(ce), round(cp)])
            for code, g in sorted(gp.items()):
                e = g["exp"]
                w2.writerow([district, code, g["block"], g["panchayat"], g["n"], round(e), g["plcat_n"], round(g["plcat_exp"]), g["fwt_n"], round(g["fwt_exp"]),
                             round(g["plcat_exp"] / e, 5) if e else "", round(g["fwt_exp"] / e, 5) if e else "",
                             round(g["lat_sum"] / g["n_geo"], 6) if g["n_geo"] else "", round(g["lon_sum"] / g["n_geo"], 6) if g["n_geo"] else ""])
            for fy, d in sorted(dfy.items()):
                w3.writerow([district, fy] + [round(v) for v in d])
            for k, v in wt_tot.items():
                t = all_wt[k]; t[0] += v[0]; t[1] += v[1]; t[2] += v[2]; t[3] += v[3]
            tot = sum(g["exp"] for g in gp.values())
            totals.append((district, n, round(tot), len([c for c in gp if c != "NA"])))
            print(f"{district:<24} assets={n:>7}  expenditure={round(tot):>14}  panchayat codes={totals[-1][3]:>4}")
    with open(os.path.join(out, f"{pre}_assets_worktype_totals.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["work_type", "n_works", "expenditure_inr", "n_in_plantation_category", "n_matching_forestry_regex"])
        for k, v in sorted(all_wt.items(), key=lambda kv: -kv[1][1]):
            w.writerow([k, v[0], round(v[1]), v[2], v[3]])
    # Self-check against what was observed on 2026-10-04 (browser read of the same S3 objects).
    expected = {"DEOGARH": (16068, 1512896912), "RAYAGARHA": (44599, 5289139554)}
    for d, n, e, _ in totals:
        if d in expected:
            ok = (n, e) == expected[d]
            print(f"self-check {d}: {'matches' if ok else 'DIFFERS from'} the 2026-10-04 reading {expected[d]}" + ("" if ok else f" (now {(n, e)}) - the bucket has been updated since"))
    print("wrote 4 CSVs to", out)

if __name__ == "__main__":
    main()
