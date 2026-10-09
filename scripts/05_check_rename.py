#!/usr/bin/env python3
"""The gate on the renaming of the cells (the owner's ruling of 9 October 2026): no unit changes cell.

    python scripts/05_check_rename.py [--before FOLDER]

Five of the six cells were renamed so that each name states its test. A name is a label: the ids of the cells, the two
thresholds, the tier order and every unit's cell must be what they were. This script holds that, unit by unit.

BEFORE   the decision tables as they stood when they were ruled on: condition_by_unit.csv, tiers.csv and
         decision.provenance.json of the build of 8 October 2026. They are a stage output of that day and are not in git, so
         a copy is kept with the session's working files (default: .session_scratch_2026-10-05/55_decision_2026-10-08_as_ruled_on/).
         The run stops unless that condition_by_unit.csv has the sha256 written below - the hash of the table that was
         independently replicated and that docs/DECISION_LAYER.md of 8 October described.
AFTER    55_decision/condition_by_unit.csv, tiers.csv and decision.provenance.json as they are now.

What is held, and the run stops (exit 1, nothing written) on one mismatch:
  1. THE OWNER'S GATE. Every unit's cell BEFORE, in each of the four windows, is taken to its old name by the old
     tiers.csv, through the owner's list old name -> new name (written out below, from his message), and compared with
     the name the new tiers.csv gives the unit's cell AFTER. 11,468 units x 4 windows = 45,872 assignments; all must match.
  2. The old names are exactly the six of his list, and the new names exactly the six it maps to.
  3. Every one of the 51 columns the table had BEFORE is in the table AFTER, and equal as text in every row: so the
     hectares, the rows, the cells, the orders, the tier, the corroboration and the district checks are what they were,
     and the independent replication of 8 October still covers them. The columns added since are listed, not compared.
  4. The two thresholds and the order of the tiers are what they were.

Output: 55_decision/rename_gate.json and nothing else: the inputs with their sha256, the UTC time, the list of names, and
the counts. It is of the table whose hash it records: run it again after any rebuild of 55_decision/.
"""
import argparse, csv, datetime, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "55_decision" / "rename_gate.json"
RULED_ON_SHA256 = "f129962e816e4da3eb656e8d10c185543d6116b208c52c445560ce881c6fcb0e"      # condition_by_unit.csv as replicated and as ruled on
WINDOWS = ("2018_2025", "2001_2025", "2017_2023", "2021_2025")
RENAMED = {  # the owner's list of 9 October 2026, old name -> new name, as he wrote it
    "Open forest still losing - restore": "Open forest, loss recorded - restore",
    "Closed forest under pressure - find the cause first": "Closed forest, loss recorded - find the cause first",
    "Open forest - assisted natural regeneration candidate": "Open forest, little or no loss recorded - assisted natural regeneration candidate",
    "Protect - intact closed forest": "Closed forest, little or no loss recorded - protect",
    "Little forest left, recent loss - verify on the ground": "Little forest left, loss recorded - verify on the ground",
    "Not a forest site": "Not a forest site",
}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stop(m):
    print("RENAME GATE FAILED: " + m, file=sys.stderr)
    sys.exit(1)


def table(p):
    with open(p, encoding="utf-8", newline="") as fh:
        r = csv.reader(fh)
        head = next(r)
        return head, list(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", default=str(ROOT / ".session_scratch_2026-10-05" / "55_decision_2026-10-08_as_ruled_on"))
    a = ap.parse_args()
    before, after = Path(a.before), ROOT / "55_decision"
    files = [before / "condition_by_unit.csv", before / "tiers.csv", before / "decision.provenance.json", after / "condition_by_unit.csv", after / "tiers.csv", after / "decision.provenance.json"]
    for f in files:
        if not f.is_file():
            stop(f"{f} is not there")
    if sha(files[0]) != RULED_ON_SHA256:
        stop(f"{files[0]} is not the table that was ruled on (sha256 {sha(files[0])}, expected {RULED_ON_SHA256})")
    (h0, r0), (h1, r1) = table(files[0]), table(files[3])
    name0 = {r["cell"]: r["cell_name"] for r in csv.DictReader(open(files[1], encoding="utf-8"))}
    name1 = {r["cell"]: r["cell_name"] for r in csv.DictReader(open(files[4], encoding="utf-8"))}
    if set(name0.values()) != set(RENAMED) or len(name0) != 6:
        stop(f"the names before are not the six of the owner's list: {sorted(name0.values())}")
    if set(name1.values()) != set(RENAMED.values()) or len(name1) != 6:
        stop(f"the names now are not the six the owner's list maps to: {sorted(name1.values())}")
    if len(r0) != len(r1) or [r[0] for r in r0] != [r[0] for r in r1] or h0[0] != "unit_id" or h1[0] != "unit_id":
        stop(f"the two tables do not hold the same units in the same order ({len(r0):,} before, {len(r1):,} now)")
    # 1. the owner's gate: every assignment, through the names
    i0, i1 = {c: k for k, c in enumerate(h0)}, {c: k for k, c in enumerate(h1)}
    compared, mismatches, by_cell = 0, [], {}
    for w in WINDOWS:
        for a_, b_ in zip(r0, r1):
            old_cell, new_cell = a_[i0[f"cell_{w}"]], b_[i1[f"cell_{w}"]]
            compared += 1
            if old_cell not in name0 or new_cell not in name1 or RENAMED[name0[old_cell]] != name1[new_cell]:
                mismatches.append((a_[0], w, old_cell, new_cell))
            by_cell[(w, new_cell)] = by_cell.get((w, new_cell), 0) + 1
    if mismatches:
        stop(f"{len(mismatches):,} of {compared:,} assignments do not match after the names are mapped, e.g. {mismatches[:5]}")
    if compared != len(r0) * len(WINDOWS):
        stop(f"{compared:,} assignments compared, not units x windows")
    # 3. every column the table had is there and equal as text
    missing = [c for c in h0 if c not in i1]
    if missing:
        stop(f"columns the table had before are no longer in it: {missing}")
    differ = {c: sum(1 for a_, b_ in zip(r0, r1) if a_[i0[c]] != b_[i1[c]]) for c in h0}
    if any(differ.values()):
        stop(f"cells of columns the table had before have changed: { {c: v for c, v in differ.items() if v} }")
    # 4. the thresholds and the order of the tiers
    p0, p1 = (json.load(open(f, encoding="utf-8")) for f in (files[2], files[5]))
    th = lambda p: (p["thresholds"]["standing_min_ha"], p["thresholds"]["loss_min_ha"], p["thresholds"]["alternatives"])
    if th(p0) != th(p1) or p0["tiers"]["order"] != p1["tiers"]["order"] or p0["tiers"]["unranked"] != p1["tiers"]["unranked"] or p0["definitions"]["default_window"] != p1["definitions"]["default_window"]:
        stop("a threshold, the order of the tiers or the default window is not what it was")
    record = {"script": "scripts/05_check_rename.py", "run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "inputs": [{"path": str(f.relative_to(ROOT)), "bytes": f.stat().st_size, "sha256": sha(f), "role": "before the ruling" if before in f.parents else "now"} for f in files],
              "the_owners_list_old_name_to_new_name": RENAMED,
              "assignments_compared_units_x_windows": compared, "assignments_that_do_not_match": 0, "units": len(r0), "windows": list(WINDOWS),
              "units_by_window_and_cell_now": {w: {c: by_cell.get((w, c), 0) for c in name1} for w in WINDOWS},
              "columns_the_table_had_before": len(h0), "of_them_equal_as_text_in_every_row": len(h0), "cells_compared_as_text": len(h0) * len(r0),
              "columns_added_since_not_compared": [c for c in h1 if c not in i0],
              "thresholds_and_tier_order_unchanged": {"standing_min_ha": p1["thresholds"]["standing_min_ha"], "loss_min_ha": p1["thresholds"]["loss_min_ha"], "tier_order": p1["tiers"]["order"]},
              "table_before_is_the_one_ruled_on_sha256": RULED_ON_SHA256, "table_now_sha256": sha(files[3]), "table_now_run_utc": p1["run_utc"]}
    OUT.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"rename gate: {compared:,} of {compared:,} assignments match (n = {len(r0):,} units x {len(WINDOWS)} windows); the {len(h0)} columns the table had are equal as text in every row "
          f"({len(h0) * len(r0):,} cells); {len(record['columns_added_since_not_compared'])} columns added since; thresholds and tier order unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
