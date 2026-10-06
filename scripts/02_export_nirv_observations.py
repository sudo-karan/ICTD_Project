#!/usr/bin/env python3
"""
Stage 1 - every clear November-December Landsat 8 observation of NIRv, stored once, so that nothing downstream has to
read Landsat again.

    python scripts/02_export_nirv_observations.py --units 10_units/units.gpkg

In : --units    the stage-0 layer (which land to cover)
     LANDSAT/LC08/C02/T1_L2    Landsat 8 OLI, Collection 2 Level 2 surface reflectance, Tier 1:
                               bands SR_B4 (red), SR_B5 (near infrared), QA_PIXEL, QA_RADSAT; properties WRS_PATH, WRS_ROW
Out: an Earth Engine image collection projects/<project>/assets/ictd/nirv_obs_<layer stem>, in tiles, on Hansen's grid
     20_degradation/ and nowhere else
     nirv_scenes.csv                     every scene the collection held for the window when this ran: id, time, path, row,
                                         season, slot, day - the figures depend on that list, so it is kept
     nirv_observations.provenance.json   inputs, UTC run time, definitions, the tiles, the list's hash, the cost

WHY OBSERVATIONS AND NOT A YEARLY VALUE. The first design stored one value per pixel and season: the median NIRv of
the clear scenes of 1 November - 31 December. An independent replication (docs/DEGRADATION.md, section 8) reproduced
those values bit for bit and then showed what they are made of: inside the window a forest pixel's NIRv falls by
13 to 18 per cent a month (leaves ageing and drying, and the sun getting lower), while the dates of the clear scenes
move by two to three and a half weeks from one season to the next. So a season's median is as much a measure of WHEN
the clear scenes fell as of the canopy, and a trend fitted to it can be a trend in dates. The median cannot be put
right afterwards, because it has thrown the dates away. This script therefore keeps every observation with its date,
and the yearly value is made downstream (02_build_nirv.py), where it can be made in more than one way and compared.

WHAT A KEPT OBSERVATION IS (unchanged). For each Landsat 8 scene: red = SR_B4 x 0.0000275 - 0.2 and
NIR = SR_B5 x 0.0000275 - 0.2. A pixel of a scene is kept only if QA_PIXEL bits 0 to 5 are all zero (fill, dilated
cloud, cirrus, cloud, cloud shadow, snow), QA_RADSAT bits 3, 4 and 11 are zero (red saturated, near-infrared
saturated, terrain occlusion), and both reflectances are above 0 and below 1. Its value is
NIRv = (NIR - red) / (NIR + red) x NIR, rounded to a 32-bit float. Everything is on Hansen's grid (EPSG:4326, cells
of 0.00025 degrees, cell (i, j) having its west edge at -180 + 0.00025 i and its north edge at 80 - 0.00025 j), each
grid cell taking the Landsat pixel that contains its centre.

WHAT IS STORED, per grid cell.
  o_<season>_<slot><e|o>   one band for each season 2013-2025 (a season is named for the year of its November), each
                           of four SLOTS of the window, and each PARITY of the WRS-2 path: the NIRv of the kept
                           observation made then. 13 x 4 x 2 = 104 bands; most are empty at any one cell.
                             slot 0 = 1-16 November, 1 = 17 November - 2 December, 2 = 3-18 December,
                             3 = 19-31 December (days 0-15, 16-31, 32-47, 48-60 counted from 1 November 00:00 UTC;
                             a scene belongs to the slot its acquisition time falls in).
                             e = paths 138, 140, 142; o = paths 139, 141, 143.
                           Landsat 8 passes a path once every 16 days, so a slot holds at most one pass of a path;
                           and two paths that both see a cell are neighbours, one even and one odd. So each band is
                           ONE pass of ONE path, and its date is known from nirv_scenes.csv: (season, slot, path).
                           Where two rows of a path overlap, one pass gives two scenes of the same instant: the band
                           holds their mean.
  path_e, path_o           which path the even and the odd observations of this cell come from (0 where none).
  nirv_<season>, obs_<season>   the first design's yearly value and count, made exactly as before - the median over
                           the scenes kept in the season (the mean of the two middle ones for an even number), and
                           the number of scenes - so that the earlier figures, and their replication, stand as they
                           are and can be set beside whatever replaces them.

TILES. 0.5-degree tiles with edges on whole grid cells, each cut down to the bounding box of the units that touch
it (land outside the units is not computed). One batch task per tile, resumable: tiles that exist are skipped.

THE SCENE LIST IS PART OF THE RESULT. Which scenes the archive holds for a window changes (scenes are reprocessed,
added, withdrawn), and one cloudy pass more or less moves a season's value. The list as it stood at this run is
written to nirv_scenes.csv and its hash to the provenance record; the run stops unless every (season, path, slot)
holds one pass and every path is in one of the two parity lists.

Needs earthengine-api, geopandas, shapely, pandas, numpy; scripts/_ee_units.py.
"""
import argparse, hashlib, inspect, json, math, sys, time
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

LANDSAT = "LANDSAT/LC08/C02/T1_L2"
HANSEN = "UMD/hansen/global_forest_change_2025_v1_13"
GRID = {"crs": "EPSG:4326", "transform": [0.00025, 0, -180, 0, -0.00025, 80]}
WINDOW = ("11-01", "01-01")                    # from 1 November up to, not including, 1 January of the next year
WINDOW_DAYS = 61
ALL_SEASONS = list(range(2013, 2026))
SLOT_DAYS = 16                                 # one Landsat 8 repeat cycle
SLOTS = 4
PATHS = {"e": [138, 140, 142], "o": [139, 141, 143]}
TILE_DEG = 0.5
FIRST_TILES = ("t_0810_0175", "t_0810_0180", "t_0815_0175", "t_0815_0180", "t_0820_0175")     # exported first: the earlier design's tiles, for the comparison with it
# The stored tiles were exported by the code of this hash (the functions that decide what a band holds, and the constants
# they use). If that code changes, the tiles no longer match it: delete the collection and export again.
RECIPE_SHA256 = "e3e92d6bd381e1c2ef12654a7357b99ab8631e632f480c8aa8f69901558af3d6"


def nirv(im):
    qa, sat = im.select("QA_PIXEL"), im.select("QA_RADSAT")
    red = im.select("SR_B4").multiply(0.0000275).add(-0.2)
    nir = im.select("SR_B5").multiply(0.0000275).add(-0.2)
    keep = (qa.bitwiseAnd(0b111111).eq(0).And(sat.bitwiseAnd((1 << 3) | (1 << 4) | (1 << 11)).eq(0))
            .And(red.gt(0)).And(red.lt(1)).And(nir.gt(0)).And(nir.lt(1)))
    return nir.subtract(red).divide(nir.add(red)).multiply(nir).updateMask(keep).rename("nirv").toFloat()


def yearly_from_landsat(region=None):
    """One image: nirv_<season> = the median NIRv of that season's kept observations, obs_<season> = how many there were."""
    col = ee.ImageCollection(LANDSAT)
    if region is not None:
        col = col.filterBounds(region)
    bands = []
    for y in ALL_SEASONS:
        kept = col.filterDate(f"{y}-{WINDOW[0]}", f"{y + 1}-{WINDOW[1]}").map(nirv)
        bands.append(kept.median().toFloat().rename(f"nirv_{y}"))
        bands.append(kept.count().unmask(0).toInt8().rename(f"obs_{y}"))
    return ee.Image.cat(bands)


def observations_from_landsat(region=None):
    """One image: o_<season>_<slot><parity> for every season, slot and parity, and path_e, path_o."""
    col = ee.ImageCollection(LANDSAT)
    if region is not None:
        col = col.filterBounds(region)
    nothing = ee.ImageCollection([ee.Image.constant(0).toFloat().rename("nirv").updateMask(0)])        # so that a pass no scene made still gives a (masked) band
    bands = []
    for y in ALL_SEASONS:
        start = ee.Date.fromYMD(y, 11, 1)
        for k in range(SLOTS):
            a, b = start.advance(k * SLOT_DAYS, "day"), start.advance(min((k + 1) * SLOT_DAYS, WINDOW_DAYS), "day")
            for parity, paths in PATHS.items():
                scenes = col.filterDate(a, b).filter(ee.Filter.inList("WRS_PATH", paths)).map(nirv)
                bands.append(nothing.merge(scenes).mean().toFloat().rename(f"o_{y}_{k}{parity}"))
    window = col.filterDate(f"{ALL_SEASONS[0]}-{WINDOW[0]}", f"{ALL_SEASONS[-1] + 1}-{WINDOW[1]}").filter(ee.Filter.calendarRange(11, 12, "month"))
    no_path = ee.ImageCollection([ee.Image.constant(0).toUint8().rename("path").updateMask(0)])
    for parity, paths in PATHS.items():
        seen = window.filter(ee.Filter.inList("WRS_PATH", paths)).map(lambda im: nirv(im).multiply(0).add(ee.Number(im.get("WRS_PATH"))).toUint8().rename("path"))
        bands.append(no_path.merge(seen).max().unmask(0).toUint8().rename(f"path_{parity}"))
    return ee.Image.cat(bands)


def band_names():
    return ([f"o_{y}_{k}{p}" for y in ALL_SEASONS for k in range(SLOTS) for p in PATHS] + [f"path_{p}" for p in PATHS]
            + [n for y in ALL_SEASONS for n in (f"nirv_{y}", f"obs_{y}")])


def tile_image(region=None):
    return ee.Image.cat([observations_from_landsat(region), yearly_from_landsat(region)])


def recipe():
    """A hash of everything that decides what a stored band holds."""
    parts = [LANDSAT, repr(WINDOW), repr(WINDOW_DAYS), repr(ALL_SEASONS), repr(SLOT_DAYS), repr(SLOTS), repr(PATHS), repr(GRID),
             inspect.getsource(nirv), inspect.getsource(yearly_from_landsat), inspect.getsource(observations_from_landsat), inspect.getsource(tile_image)]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def tiles_over(units_path):
    """0.5-degree tiles that touch any unit, each cut down to the bounding box of the units touching it, edges on whole
    grid cells: [(id, west, south, east, north)], the FIRST_TILES first. Also returns the layer."""
    g = gpd.read_file(units_path, layer="units")
    step = GRID["transform"][0]
    w, s, e, n = g.total_bounds
    tree = shapely.STRtree(g.geometry.values)
    bounds = shapely.bounds(g.geometry.values)
    out = []
    for i in range(int(math.floor(w / TILE_DEG)), int(math.ceil(e / TILE_DEG))):
        for j in range(int(math.floor(s / TILE_DEG)), int(math.ceil(n / TILE_DEG))):
            west, south = i * TILE_DEG, j * TILE_DEG
            hit = tree.query(box(west, south, west + TILE_DEG, south + TILE_DEG), predicate="intersects")
            if not len(hit):
                continue
            b = bounds[hit]
            x0, y0 = max(west, b[:, 0].min()), max(south, b[:, 1].min())
            x1, y1 = min(west + TILE_DEG, b[:, 2].max()), min(south + TILE_DEG, b[:, 3].max())
            snap_down = lambda v, origin: origin + math.floor(round((v - origin) / step, 6)) * step
            snap_up = lambda v, origin: origin + math.ceil(round((v - origin) / step, 6)) * step
            x0, y0, x1, y1 = snap_down(x0, west), snap_down(y0, south), snap_up(x1, west), snap_up(y1, south)
            x1, y1 = max(x1, x0 + step), max(y1, y0 + step)                       # a unit that only touches the tile's edge still gets one row or column of cells
            out.append((f"t_{int(round(west * 10)):04d}_{int(round(south * 10)):04d}", x0, y0, x1, y1))
    out.sort(key=lambda t: (t[0] not in FIRST_TILES, t[0]))
    return out, g


def scene_list(region):
    """Every scene of the window that the collection holds over the region, now: a DataFrame, checked."""
    col = (ee.ImageCollection(LANDSAT).filterBounds(region).filterDate(f"{ALL_SEASONS[0]}-{WINDOW[0]}", f"{ALL_SEASONS[-1] + 1}-{WINDOW[1]}")
           .filter(ee.Filter.calendarRange(11, 12, "month")))
    got = col.reduceColumns(ee.Reducer.toList(5), ["system:index", "system:time_start", "WRS_PATH", "WRS_ROW", "CLOUD_COVER"]).get("list").getInfo()
    d = pd.DataFrame(got, columns=["scene_id", "time_start_ms", "wrs_path", "wrs_row", "cloud_cover"]).sort_values(["time_start_ms", "scene_id"]).reset_index(drop=True)
    if len(d) != col.size().getInfo() or not d["scene_id"].is_unique:
        fail(f"the scene list has {len(d):,} rows for a collection of {col.size().getInfo():,} scenes (a scene with a property missing is dropped from the list)")
    t = pd.to_datetime(d["time_start_ms"], unit="ms", utc=True)
    d["time_utc"] = t.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    d["season"] = t.dt.year
    start = pd.to_datetime(d["season"].astype(str) + "-11-01", utc=True)
    d["day"] = ((t - start).dt.total_seconds() / 86400).round(5)
    d["slot"] = np.floor(d["day"] / SLOT_DAYS).astype(int)
    d["parity"] = d["wrs_path"].map({p: k for k, ps in PATHS.items() for p in ps})
    if d["parity"].isna().any():
        fail(f"scenes on a path outside the two parity lists {PATHS}: {sorted(d.loc[d['parity'].isna(), 'wrs_path'].unique())}")
    if not d["season"].isin(ALL_SEASONS).all() or (d["day"] < 0).any() or (d["day"] >= WINDOW_DAYS).any() or not d["slot"].between(0, SLOTS - 1).all():
        fail("a scene of the window falls outside the seasons or the slots")
    spread = d.groupby(["season", "wrs_path", "slot"])["day"].agg(lambda v: v.max() - v.min())
    if (spread > 0.01).any():
        fail(f"{int((spread > 0.01).sum())} (season, path, slot) hold more than one pass - a slot would mix two dates")
    return d


def export_tiles(collection_id, tiles, stem):
    """One batch export per tile that is not there yet. Returns {task description: status} for the ones run now."""
    if not eu.exists(collection_id):
        ee.data.createAsset({"type": "IMAGE_COLLECTION"}, collection_id)
    running = eu.unfinished(f"ictd_{stem}_nirvobs_")
    if running:
        sys.exit(f"Earth Engine is still running {len(running)} tile exports ({running[:3]} ...): wait for them, or two tasks would write the same tile")
    have = {a["name"].split("/")[-1] for a in ee.data.listAssets({"parent": collection_id}).get("assets", [])}
    step = GRID["transform"][0]
    names = band_names()
    tasks = []
    for tid, west, south, east, north in tiles:
        if tid in have:
            continue
        region = ee.Geometry.Rectangle([west, south, east, north], None, False)
        image = tile_image(region).select(names).set({"recipe_sha256": RECIPE_SHA256, "tile": tid})
        nx, ny = int(round((east - west) / step)), int(round((north - south) / step))
        task = ee.batch.Export.image.toAsset(image=image, description=f"ictd_{stem}_nirvobs_{tid}", assetId=f"{collection_id}/{tid}", crs=GRID["crs"],
                                             crsTransform=[step, 0, west, 0, -step, north], dimensions=f"{nx}x{ny}", maxPixels=int(1e9))
        task.start()
        tasks.append(task)
    print(f"  {len(tiles)} tiles touch the units; {len(have & {t[0] for t in tiles})} were already exported, {len(tasks)} started now", flush=True)
    return eu.wait(tasks, "tile-export") if tasks else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    ap.add_argument("--only", nargs="*", help="export only these tiles (ids) and write nothing to 20_degradation/: for a pilot")
    a = ap.parse_args()
    started = now()
    if recipe() != RECIPE_SHA256:
        sys.exit("the code that decides what a stored band holds is not the code the tiles were exported with.\n"
                 "Restore it; or delete the image collection, export every tile again, and set RECIPE_SHA256 to " + recipe())
    project = eu.init(a.project)
    stem = Path(a.units).stem
    collection_id = f"projects/{project}/assets/ictd/nirv_obs_{stem}"
    grid = ee.Image(HANSEN).select("treecover2000").projection().getInfo()
    if grid.get("crs") != GRID["crs"] or [float(v) for v in grid.get("transform", [])] != [float(v) for v in GRID["transform"]]:
        fail(f"{HANSEN}: its grid is {grid}, not {GRID}")
    tiles, layer = tiles_over(a.units)
    w, s, e, n = layer.total_bounds
    scenes = scene_list(ee.Geometry.Rectangle([float(w), float(s), float(e), float(n)], None, False))
    stop_if_failed("checking the grid and the scene list")
    full = sum(1 for t in tiles if round((t[3] - t[1]) / TILE_DEG, 6) == 1 and round((t[4] - t[2]) / TILE_DEG, 6) == 1)
    cells = sum(round((t[3] - t[1]) / GRID["transform"][0]) * round((t[4] - t[2]) / GRID["transform"][0]) for t in tiles)
    print(f"{a.units}: n = {len(layer):,} units; {len(tiles)} tiles ({full} whole, the rest cut to the units' bounding box; {cells / 1e6:,.1f} million grid cells, "
          f"{100 * cells / (len(tiles) * (TILE_DEG / GRID['transform'][0]) ** 2):.0f} per cent of whole tiles)")
    print(f"{LANDSAT}: {len(scenes):,} scenes in the window over the units' bounding box, seasons {scenes.season.min()}-{scenes.season.max()}; "
          f"by season {scenes.groupby('season').size().to_dict()}")
    if a.only is not None:
        tiles = [t for t in tiles if t[0] in set(a.only)]
        print(f"--only: {len(tiles)} tile(s); nothing is written to {OUT.relative_to(ROOT)}/")
    t0 = time.time()
    status = export_tiles(collection_id, tiles, stem)
    stop_if_failed("exporting the tiles")
    have = {x["name"].split("/")[-1] for x in ee.data.listAssets({"parent": collection_id}).get("assets", [])}
    print(f"OK  {collection_id}: {len(have & {t[0] for t in tiles})} of {len(tiles)} tiles; {eu.eecu(status):,.0f} EECU-seconds in this run ({time.time() - t0:,.0f} s)")
    if a.only is not None:
        for k, v in status.items():
            print(f"  {k}: {v['state']}, {float(v.get('batch_eecu_usage_seconds') or 0):,.0f} EECU-seconds")
        return
    if {t[0] for t in tiles} - have:
        fail(f"{len({t[0] for t in tiles} - have)} tiles are missing from {collection_id}")
        stop_if_failed("counting the tiles")
    OUT.mkdir(exist_ok=True)
    scenes.to_csv(OUT / "nirv_scenes.csv", index=False)
    sizes = {t[0]: int(ee.data.getAsset(f"{collection_id}/{t[0]}").get("sizeBytes", 0)) for t in tiles}
    with open(OUT / "nirv_observations.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_export_nirv_observations.py", "script_sha256": sha256(__file__), "helper": "scripts/_ee_units.py",
            "helper_sha256": sha256(Path(__file__).with_name("_ee_units.py")), "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                       {"earth_engine_dataset": LANDSAT, "bands": ["SR_B4", "SR_B5", "QA_PIXEL", "QA_RADSAT"], "window": f"{WINDOW[0]} to the day before {WINDOW[1]} of the next year, UTC",
                        "scenes": int(len(scenes)), "scenes_by_season": {str(k): int(v) for k, v in scenes.groupby("season").size().items()},
                        "scene_list": "20_degradation/nirv_scenes.csv", "scene_list_sha256": sha256(OUT / "nirv_scenes.csv")},
                       {"earth_engine_dataset": HANSEN, "use": "the grid only", "grid": grid}],
            "outputs_in_earth_engine": {"image_collection": collection_id, "tiles": len(tiles), "tile_degrees": TILE_DEG, "recipe_sha256": RECIPE_SHA256, "bands": len(band_names()),
                                        "grid_cells": int(cells), "bytes": int(sum(sizes.values())), "tile_boxes": {t[0]: [round(v, 5) for v in t[1:]] for t in tiles}},
            "definitions": {"kept": "QA_PIXEL bits 0-5 zero, QA_RADSAT bits 3, 4, 11 zero, red and NIR reflectance in (0, 1)", "nirv": "NDVI x NIR, a 32-bit float per scene",
                            "o_<season>_<slot><parity>": "mean NIRv of the kept scenes of that season, slot and path parity at the cell: one pass of one path (two scenes where rows overlap)",
                            "slots": {str(k): f"days {k * SLOT_DAYS}-{min((k + 1) * SLOT_DAYS, WINDOW_DAYS) - 1} from 1 November 00:00 UTC" for k in range(SLOTS)}, "paths": PATHS,
                            "path_e, path_o": "the WRS-2 path of the cell's even / odd observations, 0 where none",
                            "nirv_<season>, obs_<season>": "the first design's value: median over the season's kept scenes, and their number"},
            "earth_engine": {"project": project, "tile_tasks_this_run": len(status), "tile_eecu_seconds_this_run": round(eu.eecu(status), 1)},
            "checks_passed": {"grid_is_hansens": True, "one_pass_per_season_path_slot": True, "every_path_in_a_parity_list": True, "tiles_present": len(tiles)},
            "tables": {"nirv_scenes.csv": {"rows": int(len(scenes)), "columns": int(len(scenes.columns)), "blank_cells": {}}},
            "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        }, fh, indent=2)
    print(f"nirv_scenes.csv: n = {len(scenes):,} scenes; done. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
