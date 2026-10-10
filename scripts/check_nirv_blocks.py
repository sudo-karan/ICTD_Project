#!/usr/bin/env python3
"""
Stage 1, NIRv - were the stored yearly values made from the whole of the stored observations?

    python scripts/check_nirv_blocks.py --units 10_units/units.gpkg
    python scripts/check_nirv_blocks.py --units 10_units/units.gpkg --probe b_0820_0180

Reads Earth Engine's task records and, for --probe, one small box of two stored assets. Writes nothing.
Exit 0 = passed; 1 = a check failed; 3 = cannot be decided yet (tasks still queued, or nothing to probe yet).

WHY THIS EXISTS. scripts/02_export_nirv_yearly.py makes each block of yearly values from the tiles of observations
(scripts/02_export_nirv_observations.py) that lie under it. Run as written it starts only when every tile exists.
On 6 October 2026 the 13 block exports were instead QUEUED BEHIND 61 tile exports that had not run yet, so that
Earth Engine could work through all of them unattended. That is sound only if (a) Earth Engine evaluates a queued
task when it starts, not when it is queued, and (b) every block started after the tiles under it had finished.
This script checks both, from what Earth Engine itself records.

THE ORDER CHECK (no argument). For every block: the latest successful export task of the block, and of each tile
whose box overlaps the block's. The block passes if it STARTED after every one of those tiles ENDED. A block that
started earlier is named with the tile it missed: delete that block and run 02_export_nirv_yearly.py again - but
ask the project owner first. Also checked: no tile or block export is still pending or running, and the scene list
the blocks were queued with gives every pass the same day as the scene list now recorded
(20_degradation/nirv_scenes.csv): a block bakes the day of each pass into its values.

THE PROBE (--probe <block id>), for (a), to be run as soon as that block exists: it finds a tile under the block
whose export ended AFTER the blocks were queued, reads a box of 16 x 16 grid cells in it from both assets, and
compares, cell by cell and season by season, "the block counted at least one pass" (passes_<season> >= 1) with
"the tile holds at least one kept scene" (obs_<season> >= 1). They must be the same everywhere. If the block
counted nothing where the tile has scenes, the block was computed without that tile: assumption (a) is wrong, and
every block still queued will be wrong in the same way.

Needs earthengine-api, geopandas, pandas, numpy; scripts/_ee_units.py, 02_export_nirv_yearly.py.
"""
import argparse, datetime as dt, importlib.util, sys
from pathlib import Path

import ee
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ee_units as eu
from _ee_units import OUT, ROOT

spec = importlib.util.spec_from_file_location("yearly", Path(__file__).with_name("02_export_nirv_yearly.py"))
Y = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Y)
X = Y.OBS
QUEUED_WITH = OUT / "nirv_yearly_blocks_queued_with_scenes.csv"       # the scene list of the one-off queueing of 6 Oct 2026, if there was one
PROBE_CELLS = 16


def when(m, key):
    return dt.datetime.fromisoformat((m.get(key) or m["updateTime"]).replace("Z", "+00:00"))


def task_records(stem):
    """{tile id: latest successful export task}, {block id: the same}, [descriptions still pending or running], from the project's task list."""
    tiles, blocks, live = {}, {}, []
    for o in ee.data.listOperations():
        m = o.get("metadata", {})
        d, state = str(m.get("description", "")), m.get("state")
        for prefix, into in ((f"ictd_{stem}_nirvobs_", tiles), (f"ictd_{stem}_nirvstd_block_", blocks)):
            if d.startswith(prefix):
                if state in ("PENDING", "RUNNING"):
                    live.append(d)
                elif state == "SUCCEEDED" and (d[len(prefix):] not in into or when(m, "endTime") > when(into[d[len(prefix):]], "endTime")):
                    into[d[len(prefix):]] = m
    return tiles, blocks, live


def overlap(a, b):
    """The box two boxes (west, south, east, north) share, or None if they share no area."""
    w, s, e, n = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    return (w, s, e, n) if e - w > 1e-9 and n - s > 1e-9 else None


def order_check(stem, tiles, blocks):
    t_rec, b_rec, live = task_records(stem)
    bad, undecided = [], []
    if live:
        undecided.append(f"{len(live)} tile or block exports are still pending or running")
    no_t = [t[0] for t in tiles if t[0] not in t_rec]
    no_b = [b[0] for b in blocks if b[0] not in b_rec]
    if no_t or no_b:
        (undecided if live else bad).append(f"no successful export task is recorded for {len(no_t)} tiles {no_t[:4]} and {len(no_b)} blocks {no_b[:4]}")
    late = []
    for b in blocks:
        if b[0] not in b_rec:
            continue
        started = when(b_rec[b[0]], "startTime")
        for t in tiles:
            if t[0] in t_rec and overlap(b[1:], t[1:]) and when(t_rec[t[0]], "endTime") >= started:
                late.append((b[0], t[0], started, when(t_rec[t[0]], "endTime")))
    for bid, tid, started, ended in late:
        bad.append(f"block {bid} started {started:%Y-%m-%dT%H:%M:%SZ}, before tile {tid} under it was finished ({ended:%Y-%m-%dT%H:%M:%SZ}): the block does not hold that tile")
    if b_rec and t_rec:
        first_block = min(when(m, "createTime") for m in b_rec.values())
        print(f"tasks: {len(t_rec)} of {len(tiles)} tiles and {len(b_rec)} of {len(blocks)} blocks have a successful export; the blocks' tasks were created from {first_block:%Y-%m-%dT%H:%M:%SZ}; "
              f"{sum(1 for m in t_rec.values() if when(m, 'endTime') > first_block)} tiles finished after that")
    if QUEUED_WITH.exists() and (OUT / "nirv_scenes.csv").exists():
        used, recorded = pd.read_csv(QUEUED_WITH), pd.read_csv(OUT / "nirv_scenes.csv")
        if Y.day_lookup(used) != Y.day_lookup(recorded):
            bad.append(f"the scene list the blocks were queued with ({QUEUED_WITH.name}) gives some pass a different day from 20_degradation/nirv_scenes.csv: the blocks' values were moved by other days than the build would use")
        else:
            same_text = QUEUED_WITH.read_text() == (OUT / "nirv_scenes.csv").read_text()
            print(f"scene lists: every pass has the same day in the list the blocks were queued with and in the list now recorded ({len(recorded):,} scenes"
                  + ("; the two files are identical)" if same_text else "; the files differ in other columns, which does not touch the blocks)"))
    elif QUEUED_WITH.exists():
        undecided.append("20_degradation/nirv_scenes.csv does not exist yet: the scene lists cannot be compared")
    return bad, undecided


def probe(stem, project, tiles, blocks, block_id):
    block = next((b for b in blocks if b[0] == block_id), None)
    if block is None:
        return [f"{block_id} is not a block of this layer"], []
    obs_c, std_c = f"projects/{project}/assets/ictd/nirv_obs_{stem}", f"projects/{project}/assets/ictd/nirv_std_{stem}"
    if not eu.exists(f"{std_c}/{block_id}"):
        return [], [f"block {block_id} does not exist yet"]
    t_rec, b_rec, _ = task_records(stem)
    if block_id not in b_rec:
        return [], [f"no successful export task is recorded for block {block_id}"]
    queued = when(b_rec[block_id], "createTime")
    under = [(t, when(t_rec[t[0]], "endTime")) for t in tiles if t[0] in t_rec and overlap(block[1:], t[1:])]
    after = sorted([x for x in under if x[1] > queued], key=lambda x: x[1], reverse=True)
    if not after:
        return [], [f"no tile under block {block_id} finished after the block was queued ({queued:%Y-%m-%dT%H:%M:%SZ}): this block cannot show whether a queued task reads the tiles when it starts"]
    step = Y.GRID["transform"][0]
    seasons = Y.ALL_SEASONS
    for tile, ended in after[:4]:
        box = overlap(block[1:], tile[1:])
        for fx, fy in ((0.5, 0.5), (0.25, 0.25), (0.75, 0.75), (0.25, 0.75), (0.75, 0.25)):
            west = box[0] + round((box[2] - box[0]) * fx / step) * step
            south = box[1] + round((box[3] - box[1]) * fy / step) * step
            geom = ee.Geometry.Rectangle([west, south, west + PROBE_CELLS * step, south + PROBE_CELLS * step], None, False)
            image = ee.Image.cat([ee.Image(f"{std_c}/{block_id}").select([f"passes_{y}" for y in seasons]).unmask(0).toDouble(),
                                  ee.Image(f"{obs_c}/{tile[0]}").select([f"obs_{y}" for y in seasons]).unmask(0).toDouble()])
            got = image.reproject(Y.GRID["crs"], Y.GRID["transform"]).sampleRectangle(geom).getInfo()["properties"]
            passes = np.stack([np.array(got[f"passes_{y}"], float).ravel() for y in seasons], axis=1)
            scenes = np.stack([np.array(got[f"obs_{y}"], float).ravel() for y in seasons], axis=1)
            seen = int((scenes >= 1).sum())
            if seen == 0:
                continue                                               # sea or no data here: try another place
            differ = int(((passes >= 1) != (scenes >= 1)).sum())
            print(f"probe: block {block_id} (queued {queued:%Y-%m-%dT%H:%M:%SZ}, started {when(b_rec[block_id], 'startTime'):%Y-%m-%dT%H:%M:%SZ}) against tile {tile[0]} (finished {ended:%Y-%m-%dT%H:%M:%SZ}); "
                  f"{PROBE_CELLS} x {PROBE_CELLS} cells at {west:.5f}, {south:.5f}: the tile holds scenes in {seen:,} of {scenes.size:,} cell-seasons, the block counts a pass in {int((passes >= 1).sum()):,}; they differ in {differ:,}")
            if differ:
                return [f"block {block_id} does not hold what tile {tile[0]} holds ({differ:,} of {scenes.size:,} cell-seasons differ; the block counts passes in {int((passes >= 1).sum()):,}, the tile has scenes in {seen:,}). "
                        "A task queued before its inputs existed did not read them: the blocks still queued will be wrong in the same way. Tell the project owner before exporting anything again."], []
            return [], []
    return [], [f"no cell with a kept scene was found in the places tried under block {block_id}"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    ap.add_argument("--probe", metavar="BLOCK", help="read one small box of this block and of a tile under it, and compare")
    a = ap.parse_args()
    project = eu.init(a.project)
    stem = Path(a.units).stem
    tiles, _ = X.tiles_over(a.units)
    blocks, _ = Y.blocks_over(a.units)
    bad, undecided = probe(stem, project, tiles, blocks, a.probe) if a.probe else order_check(stem, tiles, blocks)
    what = f"probing block {a.probe}" if a.probe else "checking that every block was computed after the tiles under it"
    if bad:
        print(f"\nFAILED at {what} - {len(bad)} check(s).", file=sys.stderr)
        for m in bad:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)
    if undecided:
        print(f"NOT DECIDED YET ({what}): " + "; ".join(undecided))
        sys.exit(3)
    print(f"OK  {what}: " + ("the block holds what the tile holds, cell by cell and season by season" if a.probe else f"all {len(blocks)} blocks started after the tiles under them had finished"))


if __name__ == "__main__":
    main()
