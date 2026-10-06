#!/usr/bin/env python3
"""
Rebuild odisha_villages_pc11_datameet.gpkg from DataMeet's village boundaries (ODbL).

  git clone --depth 1 https://github.com/datameet/indian_village_boundaries
  python build_odisha_villages_datameet.py --src indian_village_boundaries/or --out odisha_villages_pc11_datameet.gpkg

Needs geopandas + pyogrio.  Geometry is Census-2001 vintage; the repo's own crosswalk attaches Census-2011 codes.
On 2026-10-04 this gave 52,531 polygons, 49,039 (93.4%) with a 2011 village code, total area 155,917 km2.
"""
import argparse, os
import geopandas as gpd, pandas as pd

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--src", required=True, help="the 'or' folder of the DataMeet repo")
ap.add_argument("--out", default="odisha_villages_pc11_datameet.gpkg")
a = ap.parse_args()

g = pd.concat([gpd.read_file(os.path.join(a.src, f)) for f in ("or1.geojson", "or2.geojson")], ignore_index=True)
g = g.set_crs("EPSG:4326", allow_override=True)
x = pd.read_csv(os.path.join(a.src, "or.csv.csv"), dtype=str).drop_duplicates("CEN_2001")
m = g.merge(x, on="CEN_2001", how="left").rename(columns={
    "NAME": "name_2001", "DISTRICT": "district_2001", "SUB_DIST": "subdistrict_2001", "TYPE": "type",
    "village_code_2011": "pc11_village_code", "village_name_2011": "pc11_village_name",
    "district_code_2011": "pc11_district_code", "sub_district_code_2011": "pc11_subdistrict_code", "state_code_2011": "pc11_state_code"})
m = m[["pc11_village_code", "pc11_village_name", "pc11_state_code", "pc11_district_code", "pc11_subdistrict_code",
       "CEN_2001", "name_2001", "subdistrict_2001", "district_2001", "type", "geometry"]]
m["area_ha"] = (m.to_crs("EPSG:32645").area / 1e4).round(2)
has = m["pc11_village_code"].notna()
print(f"{len(m)} polygons; {int(has.sum())} ({has.mean():.1%}) carry a Census-2011 village code; total area {m['area_ha'].sum() / 100:,.0f} km2")
print("2011 codes attached to more than one polygon:", int(m.loc[has, "pc11_village_code"].duplicated().sum()))
m.to_file(a.out, layer="villages", driver="GPKG")
print("wrote", a.out)
