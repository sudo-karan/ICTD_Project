"""
Shared machinery for the stage-1 scripts: zonal statistics of an Earth Engine image over the unit layer.

Not a pipeline step and it writes no file. 02_build_hansen.py, 02_build_nirv.py and 02_build_corestack.py
import it so that all three sum pixel areas over the units in the same way and gate them in the same way.

What it does, for any image whose bands hold square metres (pixel area where a condition is true, else 0):
  - splits the units into runs of consecutive unit_id and starts one batch reduceRegions task per run, on
    the grid it is given (crs + crsTransform), with a weighted sum reducer: each pixel counts for the
    FRACTION of it inside the unit's polygon, as Earth Engine computes that fraction;
  - exports each run's table to a table asset (a row needs a geometry to be exported, so each carries a
    dummy point), reads the tables back page by page, and deletes them once the caller has its rows;
  - checks that every unit came back exactly once with no blank cell;
  - checks each unit's area summed over pixels against the area of its polygon on the WGS84 ellipsoid.

Every request carries a deadline: on 2026-10-05 one hung for half an hour on a dead connection.
"""
import datetime, hashlib, json, sys, time
from pathlib import Path

import ee
import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
CREDENTIALS = Path("~/.config/earthengine/credentials").expanduser()
REQUEST_DEADLINE_MS = 600_000
AREA_TOLERANCE = 1e-3                # all units: area summed over pixels against area of the polygons on the ellipsoid
UNIT_AREA_TOLERANCE = 0.01           # one unit: the same, as a share of its area ...
UNIT_AREA_FLOOR_M2 = 500.0           # ... or this, whichever is larger: under one 30 m pixel

fails = []


def fail(msg):
    fails.append(msg)


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Stopped before writing this step's tables.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init(project=None):
    project = project or json.load(open(CREDENTIALS)).get("project")
    if not project:
        sys.exit(f"no Cloud project: pass --project, or run `earthengine set_project <id>` so that {CREDENTIALS} names one")
    for attempt in (1, 2, 3, 4):                           # this machine's network drops for a minute or two at a time
        try:
            ee.Initialize(project=project)
            break
        except Exception as e:
            if attempt == 4:
                raise
            print(f"  could not reach Earth Engine ({type(e).__name__}); trying again in 60 s", flush=True)
            time.sleep(60)
    ee.data.setDeadline(REQUEST_DEADLINE_MS)
    return project


def exists(asset):
    try:
        return ee.data.getAsset(asset)
    except ee.EEException:
        return None


def load_units(path, asset):
    """The layer's attributes with each polygon's area on the WGS84 ellipsoid, and the asset holding the same units."""
    units = gpd.read_file(path, layer="units")
    units["unit_id"] = units["unit_id"].astype(str)
    geod = pyproj.Geod(ellps="WGS84")
    units["polygon_m2"] = [abs(geod.geometry_area_perimeter(g)[0]) for g in units.geometry.values]
    units = pd.DataFrame(units.drop(columns="geometry")).sort_values("unit_id").reset_index(drop=True)
    record = OUT / f"{Path(path).stem}_asset.provenance.json"
    if not record.exists() or json.load(open(record))["inputs"][0]["sha256"] != sha256(path):
        sys.exit(f"{record.relative_to(ROOT)} is missing or was written for a different {path}: run scripts/02_upload_units_asset.py first")
    fc = ee.FeatureCollection(asset)
    if fc.size().getInfo() != len(units):
        sys.exit(f"{asset} does not hold the layer's {len(units):,} units")
    return units, fc, record


def quadrangle_m2(west, south, east, north):
    """Area on the WGS84 ellipsoid of a box bounded by two meridians and two parallels, in closed form."""
    a, f = 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    e = np.sqrt(e2)
    q = lambda lat: a * a * (1 - e2) / 2 * (np.sin(lat) / (1 - e2 * np.sin(lat) ** 2) + np.arctanh(e * np.sin(lat)) / e)
    return float(np.deg2rad(east - west) * (q(np.deg2rad(north)) - q(np.deg2rad(south))))


def box_tests(grid, box):
    """Earth Engine's pixel-area sum over a lon/lat box on pixel edges, and over the same box moved half a pixel."""
    out, step = {}, grid["transform"][0]
    for name, shift in (("on_pixel_edges", 0.0), ("moved_half_a_pixel", step / 2)):
        w, s, e, n = (v + shift for v in box)
        geom = ee.Geometry({"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]], "geodesic": False})
        got = ee.Image.pixelArea().reduceRegion(ee.Reducer.sum(), geom, crs=grid["crs"], crsTransform=grid["transform"], maxPixels=1e9).get("area").getInfo()
        exact = quadrangle_m2(w, s, e, n)
        out[name] = {"earth_engine_m2": got, "ellipsoid_m2": exact, "relative_difference": (got - exact) / exact}
    cut = 2 * round((box[2] - box[0]) / step) + 2 * round((box[3] - box[1]) / step)
    half = out["moved_half_a_pixel"]
    half["pixels_cut"] = int(cut)
    half["shortfall_m2_per_cut_pixel"] = (half["ellipsoid_m2"] - half["earth_engine_m2"]) / cut
    return out


def wait(tasks, what="zonal-statistics"):
    """Poll batch tasks until none is pending. Returns {description: final status}."""
    done, t0 = {}, time.time()
    while len(done) < len(tasks):
        for t in tasks:
            name = t.config["description"]
            if name not in done:
                try:
                    s = t.status()
                except Exception as e:                   # one failed poll is not a failed task
                    print(f"  could not poll {name} ({type(e).__name__}); will ask again", flush=True)
                    continue
                if s["state"] in ("COMPLETED", "FAILED", "CANCELLED"):
                    done[name] = s
                    if s["state"] != "COMPLETED":
                        fail(f"task {name} ended {s['state']}: {s.get('error_message', '')}")
        print(f"  {len(done)} of {len(tasks)} {what} tasks finished after {time.time() - t0:,.0f} s", flush=True)
        if len(done) < len(tasks):
            time.sleep(60)
    return done


def unfinished(prefix):
    """Descriptions of this project's batch tasks, pending or running, that start with `prefix`."""
    return [o["metadata"].get("description") for o in ee.data.listOperations()
            if o.get("metadata", {}).get("state") in ("PENDING", "RUNNING") and str(o["metadata"].get("description", "")).startswith(prefix)]


def table(fc, columns):
    """The properties of a FeatureCollection as a DataFrame, read page by page."""
    rows, token = [], None
    while True:
        params = {"expression": fc.select(columns, retainGeometry=False), "pageSize": 2000}
        if token:
            params["pageToken"] = token
        page = ee.data.computeFeatures(params)
        rows += [f["properties"] for f in page.get("features", [])]
        token = page.get("nextPageToken")
        if not token:
            return pd.DataFrame(rows)


def zonal(image, bands, fc, units, folder, tag, grid, groups=8, tile_scale=4):
    """Sum every band of `image` over every unit. Returns (rows as a DataFrame, {task: status}, cleanup function).

    The group tables stay in `folder` until the caller runs the cleanup, so a rerun after a failure downstream
    reuses them instead of computing again. `bands` is fixed by the caller; a group table computed for a different
    band list is not reused."""
    if not exists(folder):
        ee.data.createAsset({"type": "FOLDER"}, folder)
    running = unfinished(f"ictd_{tag}_group_")
    if running:
        sys.exit(f"Earth Engine is still running {running}: wait for them before starting again, or two tasks would write the same table")
    ids = units["unit_id"].to_numpy()
    tasks, parts = [], []
    for k, idx in enumerate(np.array_split(np.arange(len(ids)), groups)):
        part = f"{folder}/group_{k}"
        parts.append(part)
        have = exists(part)
        if have:
            head = ee.FeatureCollection(part).first().propertyNames().getInfo()
            if ee.FeatureCollection(part).size().getInfo() == len(idx) and set(bands) <= set(head):
                print(f"  group {k}: already computed ({len(idx)} units)")
                continue
            ee.data.deleteAsset(part)
        group = fc.filter(ee.Filter.And(ee.Filter.gte("unit_id", str(ids[idx[0]])), ee.Filter.lte("unit_id", str(ids[idx[-1]]))))
        if group.size().getInfo() != len(idx):
            fail(f"group {k}: Earth Engine finds {group.size().getInfo()} units between {ids[idx[0]]} and {ids[idx[-1]]}, the layer has {len(idx)}")
            continue
        stats = image.reduceRegions(collection=group.select(["unit_id"]), reducer=ee.Reducer.sum(), crs=grid["crs"],
                                    crsTransform=grid["transform"], tileScale=tile_scale)
        rows = stats.map(lambda f: ee.Feature(ee.Geometry.Point([0, 0]), f.toDictionary(["unit_id"] + bands)))    # no export without a geometry
        task = ee.batch.Export.table.toAsset(collection=rows, description=f"ictd_{tag}_group_{k}", assetId=part)
        task.start()
        tasks.append(task)
        print(f"  group {k}: {len(idx)} units, {ids[idx[0]]} .. {ids[idx[-1]]}, task started", flush=True)
    stop_if_failed("starting the zonal-statistics tasks")
    status = wait(tasks)
    stop_if_failed("the zonal-statistics tasks")
    raw = pd.concat([table(ee.FeatureCollection(p), ["unit_id"] + bands) for p in parts], ignore_index=True)
    raw["unit_id"] = raw["unit_id"].astype(str)
    if len(raw) != len(units) or not raw["unit_id"].is_unique or set(raw["unit_id"]) != set(units["unit_id"]):
        fail(f"Earth Engine returned {len(raw):,} rows and {raw['unit_id'].nunique():,} distinct unit_id for {len(units):,} units")
    if raw[bands].isna().any().any():
        fail(f"blank cells came back from Earth Engine in {int(raw[bands].isna().any(axis=1).sum())} units")
    stop_if_failed("reading the zonal statistics back")

    def cleanup():
        for p in parts:
            ee.data.deleteAsset(p)
        ee.data.deleteAsset(folder)

    return raw, status, cleanup


def area_check(m, area_column="area_m2"):
    """Gate each unit's area summed over pixels against its polygon's on the ellipsoid; return the measured gap."""
    pixel_total, polygon_total = float(m[area_column].sum()), float(m["polygon_m2"].sum())
    gap = m[area_column] - m["polygon_m2"]
    rel = gap / m["polygon_m2"]
    out_of_line = gap.abs() > np.maximum(UNIT_AREA_TOLERANCE * m["polygon_m2"], UNIT_AREA_FLOOR_M2)
    if abs(pixel_total - polygon_total) / polygon_total > AREA_TOLERANCE:
        fail(f"area summed over pixels ({pixel_total / 1e6:,.1f} km2) differs from the polygons' area ({polygon_total / 1e6:,.1f} km2) by more than {AREA_TOLERANCE:.1%}")
    if out_of_line.any():
        worst = m.loc[out_of_line].assign(gap=gap[out_of_line]).reindex(gap[out_of_line].abs().sort_values(ascending=False).index).head(10)
        fail(f"{int(out_of_line.sum())} units' area summed over pixels is more than {UNIT_AREA_TOLERANCE:.0%} and {UNIT_AREA_FLOOR_M2:g} m2 from their polygon's: "
             + "; ".join(f"{r.unit_id} {r.gap:+,.0f} m2 of {r.polygon_m2:,.0f}" for r in worst.itertuples()))
    return {"pixels_km2": pixel_total / 1e6, "polygons_on_the_ellipsoid_km2": polygon_total / 1e6, "relative_difference": (pixel_total - polygon_total) / polygon_total,
            "per_unit_relative_difference": {"median": float(rel.median()), "p01": float(rel.quantile(0.01)), "p99": float(rel.quantile(0.99)),
                                             "min": float(rel.min()), "max": float(rel.max())},
            "per_unit_difference_m2": {"median": float(gap.median()), "min": float(gap.min()), "max": float(gap.max())},
            "units_below_their_polygon": int((gap < 0).sum()), "units_above_their_polygon": int((gap > 0).sum()),
            "units_more_than_1_per_cent_out": int((rel.abs() > 0.01).sum()), "units_more_than_0.1_per_cent_out": int((rel.abs() > 0.001).sum()),
            "tolerances": {"all_units": AREA_TOLERANCE, "one_unit": UNIT_AREA_TOLERANCE, "one_unit_floor_m2": UNIT_AREA_FLOOR_M2}}


def task_record(status):
    return {k: {"id": v.get("id"), "state": v["state"], "batch_eecu_usage_seconds": v.get("batch_eecu_usage_seconds")} for k, v in status.items()}


def eecu(status):
    return sum(float(s.get("batch_eecu_usage_seconds") or 0) for s in status.values())
