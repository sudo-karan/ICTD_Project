#!/usr/bin/env python3
"""
Stage 1 - the date-standardised yearly NIRv of every grid cell, made once from the stored observations and stored in turn.

    python scripts/02_export_nirv_yearly.py --units 10_units/units.gpkg

In : --units    the stage-0 layer (which land to cover)
     projects/<project>/assets/ictd/nirv_obs_<layer stem>    every clear November-December Landsat 8 observation of
                                                   2013-2025, one band per pass (02_export_nirv_observations.py - READ
                                                   ITS DOCSTRING FIRST: what a kept observation is, the grid, the four
                                                   slots, the two path parities, the bands o_<season>_<slot><e|o>,
                                                   path_e, path_o)
     20_degradation/nirv_scenes.csv                the scenes behind that asset and their times; its hash must be the one
     20_degradation/nirv_observations.provenance.json   the export of the observations recorded
Out: an Earth Engine image collection projects/<project>/assets/ictd/nirv_std_<layer stem>, in blocks, on Hansen's grid
     20_degradation/ and nowhere else
     nirv_yearly.provenance.json    inputs, UTC run time, definitions, the blocks, the cost

WHY THIS IS A STEP OF ITS OWN. The standardisation reads every one of a cell's 104 possible passes to fit two numbers,
and each season's value then depends on those two numbers. Computed on the fly inside the per-unit sums it is
recomputed for every band of every sum: one group of units used more than a hundred EECU-hours before it was
stopped. Computed once per cell and stored, it costs a few thousandths of that, and everything downstream
(02_build_nirv.py, 02_build_agreement.py) reads stored bands.

WHAT IS COMPUTED, per grid cell.
  A PASS is one stored band o_<season>_<slot><e|o> at the cell: its value v; its day d, the days from
  1 November 00:00 UTC of its season to the pass (the mean of the `day` column of nirv_scenes.csv, as printed there
  to five decimals, over the scenes of that season, slot and path - the path being path_e or path_o at the cell);
  and q = 1 for an odd path, 0 for even.
  For each cell, v = (a level for the season) + g x (d - 30) + h x q, fitted by least squares WITHIN seasons, all
  seasons pooled: from v, d and q subtract their means over that season's passes at the cell, and over all passes
  of all seasons form Sdd = sum d'd', Sqq = sum q'q', Sdq = sum d'q', Sdv = sum d'v', Sqv = sum q'v'.
    If Sqq >= 4 (the cell is seen from two paths often enough) and Sdd x Sqq - Sdq^2 > 0.000001 x Sdd x Sqq:
        g = (Sdv Sqq - Sqv Sdq) / (Sdd Sqq - Sdq^2),   h = (Sqv Sdd - Sdv Sdq) / (Sdd Sqq - Sdq^2).
    Otherwise g = Sdv / Sdd and h = 0.
    A cell has a rate only if Sdd >= 1,000 day^2; a cell without one has no standardised value in any season.
  The standardised pass is v - g x (d - 30) - h x (q - qbar), qbar being the share of the cell's passes (all
  seasons) that are from an odd path. The yearly value is the MEDIAN of the season's standardised passes (the mean
  of the two middle ones for an even number); one pass is enough. Day 30 is 1 December.
  g is the cell's own fall per day inside the window (leaves ageing and drying, and the sun getting lower); h is the
  step between its two paths, which look at it from opposite sides. All of this is done in double precision.

WHAT IS STORED, per grid cell.
  std_<season>      the date-standardised yearly value, rounded to a 32-bit float; no value where the season has no
                    pass or the cell has no rate
  passes_<season>   the number of passes the season has at the cell (0 to 8)
  day_<season>      the mean day of those passes (no value where there is none)
  g, h              the cell's rate (NIRv per day) and path step, as 32-bit floats; no value where the cell has no rate
  two               1 where a path step was fitted (the two-path rule held), else 0
  sdd, sqq, qbar    Sdd, Sqq and qbar, as 32-bit floats

WHAT THIS DOES NOT DO, AND WHAT IT COSTS. See the docstring of 02_build_nirv.py, which tabulates it: one straight-line
rate per cell for all thirteen seasons; a trend that depends on g at first order where the scenes' dates have
drifted; a single pass far from 1 December moved a long way, its own error with it.

BLOCKS. Two-degree blocks with edges on whole grid cells, each cut down to the bounding box of the units that touch
it. One batch task per block, resumable: blocks that exist are skipped. The run stops unless every tile of
observations is present and the scene list is the one their export recorded.

Needs earthengine-api, geopandas, shapely, pandas, numpy; scripts/_ee_units.py, 02_export_nirv_observations.py.
"""
import argparse, hashlib, importlib.util, inspect, json, math, sys, time
from pathlib import Path

import ee
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ee_units as eu
from _ee_units import OUT, ROOT, fail, now, sha256, stop_if_failed


def load(name):
    """A sibling script as a module: its definitions are used here, not copied."""
    spec = importlib.util.spec_from_file_location(name[:-3].replace("02_", ""), Path(__file__).with_name(name))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OBS = load("02_export_nirv_observations.py")
GRID, ALL_SEASONS = OBS.GRID, list(OBS.ALL_SEASONS)
PASSES = [(k, p) for k in range(OBS.SLOTS) for p in OBS.PATHS]          # the eight possible passes of a season, in band order
STANDARD_DAY = 30.0                            # 1 December: day 30 counted from 1 November 00:00 UTC
SDD_MIN = 1000.0                               # day^2: below this a cell's passes do not span enough dates to give it a rate
SQQ_MIN = 4.0                                  # below this a cell is not seen from two paths often enough to give it a path step
BLOCK_DEG = 2.0
# The stored blocks were exported by the code of this hash (standardise, band_names and the constants they use, and the
# recipe of the observations they were made from). If that code changes, delete the collection and export again.
RECIPE_SHA256 = "d9ff43dbc3fd3b2504b1422a8aa3984d73581e8ae55eb7b918bfea691976f64d"


def day_lookup(scenes):
    """{(season, slot, parity): {path: day}} from the scene list: the day of each pass."""
    days = {}
    for (y, k, par, wp), g in scenes.groupby(["season", "slot", "parity", "wrs_path"]):
        days.setdefault((int(y), int(k), str(par)), {})[int(wp)] = float(g["day"].mean())
    return days


def load_scenes(obs_collection):
    """nirv_scenes.csv and the record of the export of the observations, checked against each other and against that script as it now is."""
    record, table = OUT / "nirv_observations.provenance.json", OUT / "nirv_scenes.csv"
    if not record.exists() or not table.exists():
        sys.exit(f"{record.relative_to(ROOT)} or {table.relative_to(ROOT)} is missing: run scripts/02_export_nirv_observations.py first")
    prov = json.load(open(record))
    if sha256(table) != prov["inputs"][1]["scene_list_sha256"]:
        fail(f"{table.relative_to(ROOT)} is not the scene list the export recorded")
    if prov["outputs_in_earth_engine"]["recipe_sha256"] != OBS.RECIPE_SHA256 or OBS.recipe() != OBS.RECIPE_SHA256:
        fail("the stored tiles of observations were not exported by 02_export_nirv_observations.py as it now is")
    if prov["outputs_in_earth_engine"]["image_collection"] != obs_collection:
        fail(f"the export's record is for {prov['outputs_in_earth_engine']['image_collection']}, not {obs_collection}")
    return pd.read_csv(table), prov


def standardise(stored, days):
    """The date-standardised yearly images, and what they rest on, from the stored observations (a mosaic of the tiles).
    Returns ({season: image 'nirv', double}, {"g", "h", "sdd", "sqq", "qbar", "has_rate", "two", "passes": {season: n}, "mday": {season: mean day}})."""
    zero = ee.Image.constant(0).toDouble()
    acc = {k: zero for k in ("sdd", "sdq", "sqq", "sdv", "sqv", "n", "q")}
    seasons = {}
    for y in ALL_SEASONS:
        items = []
        for k, par in PASSES:
            table = days.get((y, k, par))
            if not table:
                continue                                                   # no scene made that pass anywhere
            paths = sorted(table)
            d = stored.select(f"path_{par}").remap(paths, [table[x] for x in paths]).toDouble()
            v = stored.select(f"o_{y}_{k}{par}").toDouble().updateMask(d.mask())
            items.append((v, d.updateMask(v.mask()), 1.0 if par == "o" else 0.0))
        tot = {k: zero for k in ("n", "d", "q", "v", "dd", "dq", "dv", "qv")}
        for v, d, q in items:
            w, v0, d0 = v.mask().gt(0).unmask(0), v.unmask(0), d.unmask(0)
            tot["n"] = tot["n"].add(w)
            tot["d"], tot["q"], tot["v"] = tot["d"].add(d0), tot["q"].add(w.multiply(q)), tot["v"].add(v0)
            tot["dd"], tot["dq"] = tot["dd"].add(d0.multiply(d0)), tot["dq"].add(d0.multiply(q))
            tot["dv"], tot["qv"] = tot["dv"].add(d0.multiply(v0)), tot["qv"].add(v0.multiply(q))
        inv = ee.Image.constant(1).divide(tot["n"].max(1))
        centred = lambda ab, a, b: tot[ab].subtract(tot[a].multiply(tot[b]).multiply(inv))
        acc["sdd"] = acc["sdd"].add(centred("dd", "d", "d"))
        acc["sdq"] = acc["sdq"].add(centred("dq", "d", "q"))
        acc["sqq"] = acc["sqq"].add(tot["q"].subtract(tot["q"].multiply(tot["q"]).multiply(inv)))          # q x q = q
        acc["sdv"] = acc["sdv"].add(centred("dv", "d", "v"))
        acc["sqv"] = acc["sqv"].add(centred("qv", "q", "v"))
        acc["n"], acc["q"] = acc["n"].add(tot["n"]), acc["q"].add(tot["q"])
        seasons[y] = (items, tot["n"], tot["d"])
    sdd, sdq, sqq, sdv, sqv = (acc[k] for k in ("sdd", "sdq", "sqq", "sdv", "sqv"))
    det = sdd.multiply(sqq).subtract(sdq.multiply(sdq))
    has_rate = sdd.gte(SDD_MIN)
    two = sqq.gte(SQQ_MIN).And(det.gt(sdd.multiply(sqq).multiply(1e-6)))
    safe = det.max(1e-9)
    g = sdv.divide(sdd.max(1e-9)).where(two, sdv.multiply(sqq).subtract(sqv.multiply(sdq)).divide(safe)).updateMask(has_rate)
    h = zero.where(two, sqv.multiply(sdd).subtract(sdv.multiply(sdq)).divide(safe)).updateMask(has_rate)
    qbar = acc["q"].divide(acc["n"].max(1))
    nothing = ee.Image.constant(0).toDouble().rename("nirv").updateMask(0)
    annual, passes, mday = {}, {}, {}
    for y, (items, n, sum_d) in seasons.items():
        moved = [v.subtract(g.multiply(d.subtract(STANDARD_DAY))).subtract(h.multiply(ee.Image.constant(q).subtract(qbar))).rename("nirv") for v, d, q in items]
        annual[y] = ee.ImageCollection([nothing] + moved).median().rename("nirv")
        passes[y] = n
        mday[y] = sum_d.divide(n.max(1)).updateMask(n.gte(1))
    return annual, {"g": g, "h": h, "sdd": sdd, "sqq": sqq, "qbar": qbar, "has_rate": has_rate, "two": two.And(has_rate), "passes": passes, "mday": mday}


def band_names():
    return ([f"std_{y}" for y in ALL_SEASONS] + [f"passes_{y}" for y in ALL_SEASONS] + [f"day_{y}" for y in ALL_SEASONS] + ["g", "h", "two", "sdd", "sqq", "qbar"])


def yearly_image(stored, days):
    """The image that is stored: the bands of band_names(), in that order."""
    annual, m = standardise(stored, days)
    bands = [annual[y].toFloat().rename(f"std_{y}") for y in ALL_SEASONS]
    bands += [m["passes"][y].toInt8().rename(f"passes_{y}") for y in ALL_SEASONS]
    bands += [m["mday"][y].toFloat().rename(f"day_{y}") for y in ALL_SEASONS]
    bands += [m["g"].toFloat().rename("g"), m["h"].toFloat().rename("h"), m["two"].toInt8().rename("two"),
              m["sdd"].toFloat().rename("sdd"), m["sqq"].toFloat().rename("sqq"), m["qbar"].toFloat().rename("qbar")]
    return ee.Image.cat(bands)


def recipe():
    """A hash of everything that decides what a stored band holds."""
    parts = [OBS.RECIPE_SHA256, repr(ALL_SEASONS), repr(PASSES), repr(STANDARD_DAY), repr(SDD_MIN), repr(SQQ_MIN), repr(GRID),
             inspect.getsource(day_lookup), inspect.getsource(standardise), inspect.getsource(band_names), inspect.getsource(yearly_image)]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def blocks_over(units_path):
    """Two-degree blocks that touch any unit, each cut down to the bounding box of the units touching it, edges on whole
    grid cells: [(id, west, south, east, north)]. Also returns the layer."""
    g = gpd.read_file(units_path, layer="units")
    step = GRID["transform"][0]
    w, s, e, n = g.total_bounds
    tree = shapely.STRtree(g.geometry.values)
    bounds = shapely.bounds(g.geometry.values)
    out = []
    for i in range(int(math.floor(w / BLOCK_DEG)), int(math.ceil(e / BLOCK_DEG))):
        for j in range(int(math.floor(s / BLOCK_DEG)), int(math.ceil(n / BLOCK_DEG))):
            west, south = i * BLOCK_DEG, j * BLOCK_DEG
            hit = tree.query(box(west, south, west + BLOCK_DEG, south + BLOCK_DEG), predicate="intersects")
            if not len(hit):
                continue
            b = bounds[hit]
            x0, y0 = max(west, b[:, 0].min()), max(south, b[:, 1].min())
            x1, y1 = min(west + BLOCK_DEG, b[:, 2].max()), min(south + BLOCK_DEG, b[:, 3].max())
            snap_down = lambda v, origin: origin + math.floor(round((v - origin) / step, 6)) * step
            snap_up = lambda v, origin: origin + math.ceil(round((v - origin) / step, 6)) * step
            x0, y0, x1, y1 = snap_down(x0, west), snap_down(y0, south), snap_up(x1, west), snap_up(y1, south)
            x1, y1 = max(x1, x0 + step), max(y1, y0 + step)
            out.append((f"b_{int(round(west * 10)):04d}_{int(round(south * 10)):04d}", x0, y0, x1, y1))
    return sorted(out), g


def export_blocks(collection_id, blocks, stem, stored, days):
    """One batch export per block that is not there yet. Returns {task description: status} for the ones run now."""
    if not eu.exists(collection_id):
        ee.data.createAsset({"type": "IMAGE_COLLECTION"}, collection_id)
    running = eu.unfinished(f"ictd_{stem}_nirvstd_block_")
    if running:
        sys.exit(f"Earth Engine is still running {len(running)} block exports ({running[:3]} ...): wait for them, or two tasks would write the same block")
    have = {a["name"].split("/")[-1] for a in ee.data.listAssets({"parent": collection_id}).get("assets", [])}
    step = GRID["transform"][0]
    image = yearly_image(stored, days).select(band_names())
    tasks = []
    for bid, west, south, east, north in blocks:
        if bid in have:
            continue
        nx, ny = int(round((east - west) / step)), int(round((north - south) / step))
        task = ee.batch.Export.image.toAsset(image=image.set({"recipe_sha256": RECIPE_SHA256, "block": bid}), description=f"ictd_{stem}_nirvstd_block_{bid}", assetId=f"{collection_id}/{bid}",
                                             crs=GRID["crs"], crsTransform=[step, 0, west, 0, -step, north], dimensions=f"{nx}x{ny}", maxPixels=int(1e9))
        task.start()
        tasks.append(task)
    print(f"  {len(blocks)} blocks touch the units; {len(have & {b[0] for b in blocks})} were already exported, {len(tasks)} started now", flush=True)
    return eu.wait(tasks, "block-export") if tasks else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    a = ap.parse_args()
    started = now()
    if recipe() != RECIPE_SHA256:
        sys.exit("the code that decides what a stored band holds is not the code the blocks were exported with.\n"
                 "Restore it; or delete the image collection, export every block again, and set RECIPE_SHA256 to " + recipe())
    project = eu.init(a.project)
    stem = Path(a.units).stem
    obs_collection = f"projects/{project}/assets/ictd/nirv_obs_{stem}"
    collection_id = f"projects/{project}/assets/ictd/nirv_std_{stem}"
    scenes, obs_prov = load_scenes(obs_collection)
    have_tiles = {x["name"].split("/")[-1] for x in ee.data.listAssets({"parent": obs_collection}).get("assets", [])}
    wanted = set(obs_prov["outputs_in_earth_engine"]["tile_boxes"])
    if wanted - have_tiles:
        fail(f"{len(wanted - have_tiles)} of {len(wanted)} tiles of observations are missing from {obs_collection}")
    stop_if_failed("finding the stored observations")
    days = day_lookup(scenes)
    blocks, layer = blocks_over(a.units)
    cells = sum(round((b[3] - b[1]) / GRID["transform"][0]) * round((b[4] - b[2]) / GRID["transform"][0]) for b in blocks)
    print(f"{a.units}: n = {len(layer):,} units; {len(blocks)} blocks of {BLOCK_DEG:g} degrees cut to the units' bounding boxes, {cells / 1e6:,.1f} million grid cells; "
          f"{len(scenes):,} scenes, {len(days)} passes by season, slot and parity")
    stored = ee.ImageCollection(obs_collection).mosaic()
    t0 = time.time()
    status = export_blocks(collection_id, blocks, stem, stored, days)
    stop_if_failed("exporting the blocks")
    have = {x["name"].split("/")[-1] for x in ee.data.listAssets({"parent": collection_id}).get("assets", [])}
    if {b[0] for b in blocks} - have:
        fail(f"{len({b[0] for b in blocks} - have)} blocks are missing from {collection_id}")
        stop_if_failed("counting the blocks")
    print(f"OK  {collection_id}: {len(blocks)} blocks; {eu.eecu(status):,.0f} EECU-seconds in this run ({time.time() - t0:,.0f} s)")
    sizes = {b[0]: int(ee.data.getAsset(f"{collection_id}/{b[0]}").get("sizeBytes", 0)) for b in blocks}
    OUT.mkdir(exist_ok=True)
    with open(OUT / "nirv_yearly.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_export_nirv_yearly.py", "script_sha256": sha256(__file__), "helper": "scripts/_ee_units.py",
            "helper_sha256": sha256(Path(__file__).with_name("_ee_units.py")), "uses": {"scripts/02_export_nirv_observations.py": sha256(Path(__file__).with_name("02_export_nirv_observations.py"))},
            "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                       {"earth_engine_image_collection": obs_collection, "tiles": len(wanted), "recipe_sha256": OBS.RECIPE_SHA256, "exported_by_run": obs_prov["run_utc"]},
                       {"path": "20_degradation/nirv_scenes.csv", "bytes": (OUT / "nirv_scenes.csv").stat().st_size, "sha256": sha256(OUT / "nirv_scenes.csv"), "scenes": int(len(scenes))}],
            "outputs_in_earth_engine": {"image_collection": collection_id, "blocks": len(blocks), "block_degrees": BLOCK_DEG, "recipe_sha256": RECIPE_SHA256, "bands": band_names(),
                                        "grid_cells": int(cells), "bytes": int(sum(sizes.values())), "block_boxes": {b[0]: [round(v, 5) for v in b[1:]] for b in blocks}},
            "definitions": {"model": "v = level(season) + g x (day - 30) + h x [odd path], least squares within seasons, all seasons pooled, per cell",
                            "a_rate_needs_Sdd_of_at_least": SDD_MIN, "a_path_step_needs_Sqq_of_at_least": SQQ_MIN, "standard_day": STANDARD_DAY,
                            "std_<season>": "median of the season's passes, each moved to day 30 by g and to the cell's usual path mix by h; 32-bit float",
                            "day_of_a_pass": "mean of the day column of nirv_scenes.csv as printed (five decimals) over the scenes of the season, slot and path",
                            "passes_<season>, day_<season>": "the number of passes of the season at the cell and their mean day"},
            "earth_engine": {"project": project, "block_tasks_this_run": len(status), "block_eecu_seconds_this_run": round(eu.eecu(status), 1), "tasks": eu.task_record(status)},
            "checks_passed": {"every_tile_of_observations_present": len(wanted), "scene_list_is_the_one_recorded": True, "blocks_present": len(blocks)},
            "tables": {}, "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        }, fh, indent=2)
    print(f"done. run_utc {started}; record in {OUT.relative_to(ROOT)}/nirv_yearly.provenance.json")


if __name__ == "__main__":
    main()
