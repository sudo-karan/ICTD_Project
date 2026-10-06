#!/usr/bin/env python3
"""
Stage 1, step a - put a stage-0 unit layer into Earth Engine as ONE table asset, unchanged.

    python scripts/02_upload_units_asset.py --units 10_units/units.gpkg

In : --units   a stage-0 layer (layer "units": unit_id, unit_level, outside_village, geometry)
     ~/.config/earthengine/credentials   written by `earthengine authenticate`; names the Cloud project
Out: an Earth Engine table asset, by default projects/<project>/assets/ictd/<layer stem>
     20_degradation/<layer stem>_asset.provenance.json   what went up, how, and the checks it passed

WHY IT GOES UP IN PARTS. Earth Engine refuses any single request above 10,485,760 bytes ("Request payload
size exceeds the limit"). The base layer is 94.6 MB as GeoJSON and its largest unit alone is 1.6 MB, so
without a Cloud Storage bucket it cannot be sent in one piece. The script packs units, in unit_id order,
into parts whose ENCODED request stays under --max-request-bytes (the client's encoding is about 1.6 times
the GeoJSON), exports each part to its own table asset with a batch task, then has Earth Engine merge the
parts into one asset server-side and deletes the parts. A rerun skips parts that are already there.
No request is allowed to hang: on 2026-10-05 one stalled for half an hour after Earth Engine had in fact
started its task, so every request carries a deadline, and a part whose request fails is sent again only
if Earth Engine has neither the part nor a task for it.

NOTHING IS SIMPLIFIED OR ROUNDED BY THIS SCRIPT - BUT EARTH ENGINE DOES NOT STORE A POLYGON EXACTLY, and what
it does to one is measured here rather than assumed. Coordinates are sent as the doubles the GeoPackage
holds. Two things then happen on Earth Engine's side, both found by reading assets back on 2026-10-05:
  - A table asset keeps no vertex bit-for-bit. Sent with geodesic edges, Earth Engine's native form, the
    stored polygon is within millimetres of the one sent. Sent with planar lon/lat edges (geodesic = false),
    it is re-tessellated on ingestion and its boundary moves by about 0.13 m on average. So edges are sent
    as geodesics.
  - A geodesic edge is not quite the straight lon/lat edge GEOS sees between the same two vertices. The run
    measures, over every edge of the layer, the largest gap between the two and the area lying between them.
After ingestion EVERY unit's geometry is read back and set against the layer's:
  - the asset has exactly the layer's units, each once, with the same unit_level and outside_village;
  - per unit, the symmetric difference between stored and local polygon, divided by the perimeter - the mean
    distance the boundary has moved - is at most BOUNDARY_TOLERANCE_M;
  - over all units, the net change in area is at most NET_AREA_TOLERANCE of the total.
If any of these fails the run stops, the merged asset is left in place for inspection, and nothing is
recorded as passed. The measured figures go into the provenance record: that is the area error of the copy
Earth Engine holds.

Earth Engine's own Geometry.area() is NOT used as a check: it is computed on a sphere and runs about 0.3 per
cent above the WGS84 ellipsoid at these latitudes. (ee.Image.pixelArea(), which stage 1 uses, is ellipsoidal.)

THE ASSET CARRIES NO AREA. Its properties are unit_id, unit_level and outside_village. An area column in
Earth Engine would be a second copy of a number that belongs to stage 0, and the first copy that went up (5
October 2026) was a UTM area that stage 0 has since replaced. --drop-properties re-exports the existing asset
server-side without the named properties, so the geometry does not have to be sent again; the asset is then
checked against the layer exactly as after an upload.

Needs earthengine-api, geopandas, shapely, pyproj, pandas, numpy.
"""
import argparse, datetime, hashlib, json, os, sys, time
from pathlib import Path

import ee
import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import shapely
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
CREDENTIALS = Path("~/.config/earthengine/credentials").expanduser()
PAYLOAD_LIMIT = 10_485_760           # bytes; Earth Engine's own figure, from its refusal of an 11.5 MB request
REQUEST_DEADLINE_MS = 600_000        # a part takes about 70 s to send on this connection
BOUNDARY_TOLERANCE_M = 0.05          # per unit: symmetric difference / perimeter, i.e. the mean shift of its boundary
NET_AREA_TOLERANCE = 1e-6            # all units: |stored area - local area| / local area
READ_BACK_BYTES = 3_000_000          # GeoJSON per request when the asset's geometry is fetched for checking
EQUAL_AREA = "+proj=aea +lat_1=18 +lat_2=22 +lat_0=20 +lon_0=84.5 +datum=WGS84 +units=m"      # Albers, centred on Odisha
PROPERTIES = ["unit_id", "unit_level", "outside_village"]

fails = []


def fail(msg):
    fails.append(msg)


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). No provenance record was written.", file=sys.stderr)
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


def exists(asset):
    try:
        return ee.data.getAsset(asset)
    except ee.EEException:
        return None


def make_folder(path):
    if not exists(path):
        ee.data.createAsset({"type": "FOLDER"}, path)


def collection(units, geojson, index):
    """An inline FeatureCollection for these rows: exact coordinates, geodesic edges, the four properties."""
    feats = []
    for i in index:
        g = json.loads(geojson[i])
        g["geodesic"] = True
        r = units.iloc[i]
        feats.append(ee.Feature(ee.Geometry(g), {"unit_id": str(r["unit_id"]), "unit_level": str(r["unit_level"]),
                                                 "outside_village": int(r["outside_village"])}))
    return ee.FeatureCollection(feats)


def request_bytes(fc):
    return len(json.dumps(ee.serializer.encode(fc, for_cloud_api=True)))


def pack(units, geojson, limit):
    """Consecutive runs of units whose encoded request fits under `limit`. Returns [(first, last_exclusive, bytes)]."""
    size = np.array([len(s) for s in geojson])
    guess = limit / 1.75                     # GeoJSON bytes that usually encode to about `limit`; then measured
    parts, start = [], 0
    while start < len(units):
        end = start + max(1, int(np.searchsorted(np.cumsum(size[start:]), guess)))
        while True:
            n = request_bytes(collection(units, geojson, range(start, end)))
            if n <= limit or end - start == 1:
                break
            end = start + max(1, (end - start) * 3 // 4)
        if n > limit:
            sys.exit(f"unit {units.iloc[start]['unit_id']} alone encodes to {n:,} bytes, over the {limit:,} limit - it cannot be sent whole")
        parts.append((start, end, n))
        start = end
    return parts


def unfinished(prefix):
    """Descriptions of this project's batch tasks, pending or running, that start with `prefix`."""
    return [o["metadata"].get("description") for o in ee.data.listOperations()
            if o.get("metadata", {}).get("state") in ("PENDING", "RUNNING") and str(o["metadata"].get("description", "")).startswith(prefix)]


def start_export(make_collection, description, asset_id):
    """Start a table export. Returns the task, or None if a request failed but Earth Engine has the task or the asset anyway."""
    for attempt in (1, 2, 3):
        try:
            task = ee.batch.Export.table.toAsset(collection=make_collection(), description=description, assetId=asset_id)
            task.start()
            return task
        except Exception as e:                           # a deadline, a dropped connection: the request may still have arrived
            print(f"    {description}, attempt {attempt}: {type(e).__name__}: {str(e)[:160]}", flush=True)
            time.sleep(90)
            if exists(asset_id) or description in unfinished(description):
                print(f"    {description}: Earth Engine has it; not sent again", flush=True)
                return None
    sys.exit(f"{description}: could not be sent in three attempts")


def wait(tasks, what):
    """Poll batch tasks until none is pending. Returns {description: final status}."""
    done, t0 = {}, time.time()
    while len(done) < len(tasks):
        for t in tasks:
            name = t.config["description"]
            if name in done:
                continue
            try:
                s = t.status()
            except Exception as e:                       # one failed poll is not a failed task
                print(f"  {what}: could not poll {name} ({type(e).__name__}); will ask again", flush=True)
                continue
            if s["state"] in ("COMPLETED", "FAILED", "CANCELLED"):
                done[name] = s
                if s["state"] != "COMPLETED":
                    fail(f"{what} task {name} ended {s['state']}: {s.get('error_message', '')}")
        print(f"  {what}: {len(done)} of {len(tasks)} tasks finished after {time.time() - t0:,.0f} s", flush=True)
        if len(done) < len(tasks):
            time.sleep(30)
    return done


def stored_geometry(fc, units, geojson):
    """{unit_id: the polygon as Earth Engine holds it}, for every unit, fetched a few megabytes at a time."""
    size, out, start = np.array([len(s) for s in geojson]), {}, 0
    while start < len(units):
        end = start + min(4000, max(1, int(np.searchsorted(np.cumsum(size[start:]), READ_BACK_BYTES))))      # getInfo returns at most 5,000
        ids = units["unit_id"].iloc[start:end].tolist()
        for f in fc.filter(ee.Filter.inList("unit_id", ids)).getInfo()["features"]:
            out[f["properties"]["unit_id"]] = shape(f["geometry"])
        print(f"  read back {len(out):,} of {len(units):,} units", flush=True)
        start = end
    return out


def edge_gap(geom):
    """How far a geodesic edge strays from the straight lon/lat edge on the same two vertices, over every edge.

    Returns the largest perpendicular gap at mid-edge (m), the longest edge (m), the number of edges, and the sum over
    edges of two thirds x gap x length: the area of the sliver between the two readings, whichever side it falls."""
    c, ring = shapely.get_coordinates(shapely.get_rings(shapely.get_parts(geom)), return_index=True)
    same = ring[1:] == ring[:-1]
    a, b = c[:-1][same], c[1:][same]
    geod = pyproj.Geod(ellps="WGS84")
    azimuth, _, length = geod.inv(a[:, 0], a[:, 1], b[:, 0], b[:, 1])
    mid_lon, mid_lat, _ = geod.fwd(a[:, 0], a[:, 1], azimuth, length / 2)                 # the geodesic's midpoint
    run = b[:, 0] - a[:, 0]
    along = np.divide(mid_lon - a[:, 0], run, out=np.zeros_like(run), where=run != 0)
    _, _, north_south = geod.inv(mid_lon, mid_lat, mid_lon, a[:, 1] + along * (b[:, 1] - a[:, 1]))     # to the straight edge, along the meridian
    slope = np.arctan2(np.deg2rad(b[:, 1] - a[:, 1]), np.deg2rad(run) * np.cos(np.deg2rad((a[:, 1] + b[:, 1]) / 2)))
    gap = np.where(run != 0, np.abs(north_south * np.cos(slope)), 0.0)                    # an edge along a meridian is the same either way
    return float(gap.max()), float(length.max()), int(len(length)), float((2 / 3 * gap * length).sum())


def table(fc, columns):
    """The properties of a FeatureCollection as a DataFrame, read page by page."""
    rows, token = [], None
    while True:
        params = {"expression": fc.select(columns, retainGeometry=False), "pageSize": 5000}
        if token:
            params["pageToken"] = token
        page = ee.data.computeFeatures(params)
        rows += [f["properties"] for f in page.get("features", [])]
        token = page.get("nextPageToken")
        if not token:
            return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    ap.add_argument("--asset", help="asset id; default projects/<project>/assets/ictd/<layer stem>")
    ap.add_argument("--max-request-bytes", type=int, default=9_400_000, help=f"per part; Earth Engine's limit is {PAYLOAD_LIMIT:,}")
    ap.add_argument("--drop-properties", nargs="+", metavar="NAME", help="re-export the existing asset without these properties, then check it")
    a = ap.parse_args()
    started = now()
    project = a.project or json.load(open(CREDENTIALS)).get("project")
    if not project:
        sys.exit(f"no Cloud project: pass --project, or run `earthengine set_project <id>` so that {CREDENTIALS} names one")
    if a.max_request_bytes >= PAYLOAD_LIMIT:
        sys.exit(f"--max-request-bytes must be below Earth Engine's limit of {PAYLOAD_LIMIT:,}")
    ee.Initialize(project=project)
    ee.data.setDeadline(REQUEST_DEADLINE_MS)
    stem = Path(a.units).stem
    asset = a.asset or f"projects/{project}/assets/ictd/{stem}"
    parts_folder = f"{asset}_parts"

    units = gpd.read_file(a.units, layer="units")
    if units.crs is None or units.crs.to_epsg() != 4326:
        sys.exit(f"{a.units}: expected EPSG:4326, got {units.crs}")
    if not units["unit_id"].is_unique or set(PROPERTIES + ["area_ha"]) - set(units.columns):
        sys.exit(f"{a.units}: needs a unique unit_id and the columns {PROPERTIES + ['area_ha']}")
    units = units.sort_values("unit_id").reset_index(drop=True)
    units["unit_id"] = units["unit_id"].astype(str)
    geom = units.geometry.values
    geojson = shapely.to_geojson(geom)
    geod = pyproj.Geod(ellps="WGS84")
    units["local_area_m2"] = [abs(geod.geometry_area_perimeter(g)[0]) for g in geom]
    n_vertices = shapely.get_num_coordinates(geom)
    print(f"{a.units}: n = {len(units):,} units, {int(n_vertices.sum()):,} vertices, {sum(len(s) for s in geojson) / 1e6:.1f} MB as GeoJSON; "
          f"geodesic area {units['local_area_m2'].sum() / 1e6:,.1f} km2")
    print(f"target asset {asset}")

    record = {"asset": asset, "merged_by_this_run": False}
    earlier = OUT / f"{stem}_asset.provenance.json"
    if earlier.exists():                                   # what an earlier run recorded about how the asset came to be
        old = json.load(open(earlier))
        record["earlier_record"] = {"run_utc": old.get("run_utc"), "layer_sha256": old["inputs"][0]["sha256"], "layer_bytes": old["inputs"][0]["bytes"],
                                    "upload": {k: v for k, v in old.get("upload", {}).items() if k not in ("earlier_record", "part_tasks", "units_per_part")},
                                    "note": "this run checks the asset against the layer named in inputs; the earlier record is how the geometry got there"}
    if a.drop_properties:
        if not exists(asset):
            sys.exit(f"--drop-properties needs the asset to exist: {asset}")
        have = ee.FeatureCollection(asset).first().propertyNames().getInfo()
        dropped = [p for p in a.drop_properties if p in have]
        if dropped:
            tmp = f"{asset}_reexport"
            if exists(tmp):
                ee.data.deleteAsset(tmp)
            task = start_export(lambda: ee.FeatureCollection(asset).select(PROPERTIES), f"ictd_{stem}_reexport", tmp)
            status = wait([task], "re-exporting") if task else {}
            while unfinished(f"ictd_{stem}_reexport"):
                time.sleep(30)
            stop_if_failed("re-exporting the asset")
            if ee.FeatureCollection(tmp).size().getInfo() != len(units):
                sys.exit(f"{tmp} does not hold {len(units):,} units; {asset} is left as it was")
            ee.data.deleteAsset(asset)
            ee.data.renameAsset(tmp, asset)
            record["reexported"] = {"without_properties": dropped, "task": {k: {"id": v.get("id"), "state": v["state"]} for k, v in status.items()},
                                    "note": "server-side copy of the asset with these properties left out; no geometry was sent again"}
            print(f"  re-exported {asset} without {dropped}")
        else:
            print(f"  {asset} has none of {a.drop_properties}; nothing to drop")
    if exists(asset):
        print("  the asset already exists; nothing is sent, it is only checked")
        if exists(parts_folder):                       # an earlier run merged the parts and stopped before recording it
            parts = pack(units, geojson, a.max_request_bytes)
            counts = [ee.FeatureCollection(p["name"]).size().getInfo() for p in sorted(ee.data.listAssets({"parent": parts_folder}).get("assets", []), key=lambda p: p["name"])]
            if counts != [last - first for first, last, _ in parts]:
                fail(f"{parts_folder} holds parts of {counts} units; packing the layer again gives {[last - first for first, last, _ in parts]}")
                stop_if_failed("matching the part assets an earlier run left")
            record.update(parts=len(parts), max_request_bytes_sent=int(max(n for _, _, n in parts)), units_per_part=counts,
                          note="merged by an earlier run that stopped before writing this record; the parts are packed again here and match the part assets it left")
            print(f"  an earlier run left its {len(parts)} parts (largest request {record['max_request_bytes_sent']:,} bytes); they match and are deleted once the asset passes")
    else:
        make_folder(asset.rsplit("/", 1)[0])
        make_folder(parts_folder)
        t0 = time.time()
        parts = pack(units, geojson, a.max_request_bytes)
        print(f"  {len(parts)} parts, largest request {max(n for _, _, n in parts):,} bytes (limit {PAYLOAD_LIMIT:,}); packed in {time.time() - t0:,.0f} s")
        tasks, part_ids = [], []
        for k, (first, last, nbytes) in enumerate(parts):
            pid = f"{parts_folder}/part_{k:03d}"
            part_ids.append(pid)
            have = exists(pid)
            if have and ee.FeatureCollection(pid).size().getInfo() == last - first:
                print(f"  part {k:03d}: already ingested ({last - first} units)", flush=True)
                continue
            if have:
                ee.data.deleteAsset(pid)
            t1 = time.time()
            task = start_export(lambda: collection(units, geojson, range(first, last)), f"ictd_{stem}_part_{k:03d}", pid)
            if task:
                tasks.append(task)
            print(f"  part {k:03d}: units {first}-{last - 1} ({last - first}), request {nbytes:,} bytes, sent in {time.time() - t1:,.0f} s", flush=True)
        part_status = wait(tasks, "ingesting parts")
        while unfinished(f"ictd_{stem}_part_"):          # a part whose request failed after Earth Engine had taken it
            time.sleep(30)
        stop_if_failed("ingesting the parts")
        counts = [ee.FeatureCollection(p).size().getInfo() for p in part_ids]
        if sum(counts) != len(units) or counts != [last - first for first, last, _ in parts]:
            fail(f"the parts hold {sum(counts):,} units, the layer {len(units):,}")
            stop_if_failed("counting the parts")

        merged = ee.FeatureCollection([ee.FeatureCollection(p) for p in part_ids]).flatten()
        task = start_export(lambda: merged, f"ictd_{stem}_merge", asset)
        merge_status = wait([task], "merging") if task else {}
        while unfinished(f"ictd_{stem}_merge"):
            time.sleep(30)
        stop_if_failed("merging the parts")
        record.update(merged_by_this_run=True, parts=len(parts), max_request_bytes_sent=int(max(n for _, _, n in parts)),
                      units_per_part=counts, part_tasks={k: {"id": v.get("id"), "state": v["state"]} for k, v in part_status.items()},
                      merge_task={k: {"id": v.get("id"), "state": v["state"], "batch_eecu_usage_seconds": v.get("batch_eecu_usage_seconds")}
                                  for k, v in merge_status.items()},
                      seconds_to_send_and_ingest=round(time.time() - t0))

    # ---- what Earth Engine now holds, against the layer --------------------------------------------------------
    fc = ee.FeatureCollection(asset)
    got = table(fc, ["unit_id", "unit_level", "outside_village"])
    if len(got) != len(units) or not got["unit_id"].is_unique or set(got["unit_id"]) != set(units["unit_id"]):
        fail(f"the asset holds {len(got):,} rows and {got['unit_id'].nunique():,} distinct unit_id; the layer has {len(units):,}")
        stop_if_failed("checking the asset's units")
    m = units.merge(got, on="unit_id", suffixes=("", "_gee"), validate="one_to_one")
    if (m["unit_level"] != m["unit_level_gee"]).any() or (m["outside_village"].astype(int) != m["outside_village_gee"].astype(int)).any():
        fail("unit_level or outside_village differs between the asset and the layer")
    print(f"OK  asset holds the layer's {len(m):,} units, each once; unit_level and outside_village agree")

    back = stored_geometry(fc, units, geojson)
    if set(back) != set(units["unit_id"]):
        fail(f"geometry came back for {len(back):,} of {len(units):,} units")
        stop_if_failed("reading the asset's geometry back")
    stored = shapely.make_valid(np.array([back[i] for i in units["unit_id"]], dtype=object))
    local_ea = gpd.GeoSeries(geom, crs="EPSG:4326").to_crs(EQUAL_AREA)
    stored_ea = gpd.GeoSeries(stored, crs="EPSG:4326").to_crs(EQUAL_AREA)
    area, perimeter = local_ea.area.to_numpy(), local_ea.length.to_numpy()
    moved = local_ea.symmetric_difference(stored_ea).area.to_numpy()          # m2 that changed hands, either way
    shift = moved / perimeter                                                 # mean distance the boundary moved, m
    net = stored_ea.area.to_numpy() - area
    n_stored = shapely.get_num_coordinates(stored)
    worst = int(np.argmax(shift))
    if shift.max() > BOUNDARY_TOLERANCE_M:
        fail(f"the stored boundary of {int((shift > BOUNDARY_TOLERANCE_M).sum())} units has moved by more than {BOUNDARY_TOLERANCE_M} m on average; "
             f"worst {units['unit_id'].iloc[worst]} at {shift.max():.3f} m")
    if abs(net.sum()) / area.sum() > NET_AREA_TOLERANCE:
        fail(f"stored area differs from the layer's by {net.sum():+,.1f} m2 in all, {abs(net.sum()) / area.sum():.2e} of the total; tolerance {NET_AREA_TOLERANCE:g}")
    stop_if_failed("checking the asset's geometry against the layer")
    gap, longest, n_edges, sliver = edge_gap(geom)
    print(f"OK  every unit's geometry read back. Boundary moved, on average along a unit's perimeter: median {np.median(shift) * 1000:.3f} mm, "
          f"largest {shift.max() * 1000:.2f} mm (unit {units['unit_id'].iloc[worst]}); tolerance {BOUNDARY_TOLERANCE_M * 1000:.0f} mm")
    print(f"    area that changed hands {moved.sum():,.1f} m2 ({moved.sum() / area.sum():.2e} of {area.sum() / 1e6:,.1f} km2); net change {net.sum():+,.1f} m2 "
          f"({abs(net.sum()) / area.sum():.2e}); largest for one unit {np.abs(net).max():,.1f} m2; vertices {int(n_vertices.sum()):,} sent, {int(n_stored.sum()):,} stored")
    print(f"    geodesic against planar edges: largest mid-edge gap {gap * 1000:.0f} mm over {n_edges:,} edges, the longest {longest:,.0f} m; "
          f"area between the two readings, whichever side, {sliver:,.0f} m2 ({sliver / area.sum():.1e})")

    if exists(parts_folder):
        for p in ee.data.listAssets({"parent": parts_folder}).get("assets", []):
            ee.data.deleteAsset(p["name"])
        ee.data.deleteAsset(parts_folder)
        print(f"    the {record.get('parts', '')} part assets are deleted; only {asset} remains")

    info = ee.data.getAsset(asset)
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"{stem}_asset.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_upload_units_asset.py", "script_sha256": sha256(__file__), "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)}],
            "earth_engine": {"project": project, "asset": asset, "asset_type": info.get("type"), "asset_bytes": info.get("sizeBytes"),
                             "asset_update_time": info.get("updateTime"), "properties": PROPERTIES},
            "limit_met": {"request_payload_limit_bytes": PAYLOAD_LIMIT,
                          "message": "Request payload size exceeds the limit: 10485760 bytes.",
                          "what_was_done": "sent in parts under the limit, merged into one asset by Earth Engine, parts deleted"},
            "geometry": "sent unsimplified and unrounded, with geodesic edges; Earth Engine's stored copy is measured against the layer below",
            "upload": record,
            "checks_passed": {"units": int(len(m)), "unit_ids_identical": True, "geometry_read_back_for_units": int(len(back)),
                              "tolerances": {"boundary_shift_m_per_unit": BOUNDARY_TOLERANCE_M, "net_area_relative": NET_AREA_TOLERANCE}},
            "stored_against_local": {
                "what": "each unit's polygon as Earth Engine stores it against the layer's, both in an Albers equal-area projection",
                "boundary_shift_m": {"median": float(np.median(shift)), "p99": float(np.quantile(shift, 0.99)), "max": float(shift.max()),
                                     "unit_with_max": str(units["unit_id"].iloc[worst]), "meaning": "symmetric difference / perimeter"},
                "area_that_changed_hands_m2": float(moved.sum()), "area_that_changed_hands_share": float(moved.sum() / area.sum()),
                "net_area_change_m2": float(net.sum()), "net_area_change_share": float(net.sum() / area.sum()),
                "largest_net_change_for_one_unit_m2": float(np.abs(net).max()),
                "largest_relative_net_change_for_one_unit": float((np.abs(net) / area).max()),
                "vertices_sent": int(n_vertices.sum()), "vertices_stored": int(n_stored.sum()),
                "geodesic_vs_planar_edge": {"largest_mid_edge_gap_m": gap, "longest_edge_m": longest, "edges": n_edges,
                                            "area_between_the_two_readings_m2": sliver, "area_between_the_two_readings_share": sliver / float(area.sum()),
                                            "meaning": "Earth Engine joins the vertices by geodesics, the layer by straight lon/lat lines; the area is summed "
                                                       "whichever side it falls, so it bounds what any set of units can gain or lose by it"}},
            "area_km2": {"layer_geodesic_wgs84": round(float(units["local_area_m2"].sum() / 1e6), 3), "layer_equal_area": round(float(area.sum() / 1e6), 3),
                         "layer_area_ha_column_as_stage_0_wrote_it": round(float(units["area_ha"].sum() / 100), 3)},
            "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "geopandas": gpd.__version__,
                         "shapely": shapely.__version__, "pyproj": pyproj.__version__},
        }, fh, indent=2)
    print(f"\ndone. {asset}: n = {len(m):,} units. Record in {(OUT / f'{stem}_asset.provenance.json').relative_to(ROOT)}; run_utc {started}")


if __name__ == "__main__":
    main()
