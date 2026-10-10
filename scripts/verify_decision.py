#!/usr/bin/env python3
"""
A direct check of the decision view of the demo layer. Reads, writes nothing, exits 1 if a check fails.

    python scripts/verify_decision.py

These are the NEW assertions that came with the decision view (8 Oct 2026). scripts/verify_layer.py is left exactly as
it was and still has to pass by itself: nothing here replaces a check of it.

It shares no code with scripts/06_build_layer.py, scripts/_layer_decision.py or scripts/05_build_decision.py. It opens
60_layer/data.js - the file the map reads - and for EVERY unit and EVERY window rebuilds what the decision view should
show, from
    55_decision/condition_by_unit.csv, tiers.csv, work_types.csv, decision.provenance.json
and goes behind that table for what it copies:
    20_degradation/hansen_loss_by_canopy_band_by_unit.csv   the hectares, re-added here from the yearly columns; the keys
                                                            of the order within a district; the figures of the About text
    20_degradation/agreement_by_unit.csv                    the corroboration badge
    20_degradation/agreement_summary.csv                    the odds ratios the texts quote
    20_degradation/forest_floor_repeatability.csv           the area of one pixel in the middle of the state
    40_allocation/state_fy_r620_vs_dump.csv                 plantation's share in the two years the default window's reason names
    10_units/units_attributes.csv, outside_village_district.csv, 00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv
                                                            each unit's district, and what an outside-village unit's rests on
The provisional order of tiers and the six names are held against the project owner's specification, written out here.
Hectares are added as decimals; a figure is turned into the text the map prints by the map's own rule (two decimals of
the figure as a double), because that rule is what is being checked.

What it takes from the decision stage's own outputs and does not rebuild: the two thresholds (proposed by that stage and
accepted by the project owner on 9 October 2026), the wording of each cell's work-type field, and the columns it never
reads (dense_open_ratio, the order by hectares in the table, tier_provisional_2018_2025, agreement_reference_ha,
agreement_corestack_valued_ha): those were rebuilt by the independent replication of the table on 8 October 2026.
ADDED 9 OCTOBER 2026, with the owner's rulings, and NOT covered by that replication - so rebuilt here: the forest at the
start of each window and the loss of the window as a share of it, from the yearly columns of stage 1, for every unit and
window; where the share is blank, its reason and the count; the order by share in the cells with loss, in the table and
in the page; the five new names of the cells, written out here as he gave them; and the export's columns. Several of its checks are of words that must be there or must not be: each says so in its name.
"""
import csv, hashlib, json, re, sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
results = []


def check(what, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'}  {what}" + (f"   {detail}" if detail else ""))


def rows(path):
    with open(ROOT / path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def shown(x):
    """A hectare figure as the page must print it: by the rule of every other hectare on the map (two decimals of the figure as a double)."""
    return f"{float(Decimal(x)):,.2f}"


raw = (ROOT / "60_layer/data.js").read_text(encoding="utf-8")
D = json.loads(raw[len("window.ICTD_LAYER = "):].rstrip()[:-1])
page = (ROOT / "60_layer/index.html").read_text(encoding="utf-8")
REC = json.loads((ROOT / "60_layer/layer.provenance.json").read_text(encoding="utf-8"))
DV = D.get("decision")
check("the map's data holds a decision view", isinstance(DV, dict))
if not isinstance(DV, dict):
    sys.exit(1)
ids, n = D["id"], len(D["id"])
T_rows = rows("55_decision/condition_by_unit.csv")
T = {r["unit_id"]: r for r in T_rows}
P = json.loads((ROOT / "55_decision/decision.provenance.json").read_text(encoding="utf-8"))
check("the decision table holds each unit of the map once, and the map was built from the table that is on disk", len(T_rows) == n and len(T) == n and set(T) == set(ids) and REC["decision_view"]["table_run_utc"] == P["run_utc"]
      and any(i["path"] == "55_decision/condition_by_unit.csv" and i["sha256"] == hashlib.sha256((ROOT / "55_decision/condition_by_unit.csv").read_bytes()).hexdigest() for i in REC["inputs"]), f"n = {n:,}; table run {P['run_utc']}")
KEYS = {"title", "radio", "default_window", "windows", "cells", "tiers", "unranked", "tier_why", "cls", "counts", "dcounts", "rank", "rank_share", "sd", "so", "sf", "low", "loss", "near", "corro", "corro_letters", "corro_labels",
        "check", "check_labels", "governance", "fields", "st_codes", "grid", "work_note", "standing_min", "loss_min", "built", "overlay", "t"}
TOP = {"title", "subtitle", "built", "bounds", "id", "f", "g", "out", "bar", "codes", "layers", "floors", "default_layer", "default_floor", "districts", "panel", "core_classes", "unit_types", "info_empty", "search_none",
       "search_many", "about_html", "sources_html", "decision"}
SUB = {"t": {"legend_title", "legend_note", "tier", "unranked", "order_default", "order_changed", "window_head", "tiers_head", "reset", "why_head", "why_window", "grid_cols", "why_cols", "why_rows", "why_low", "why_standing_some",
             "why_standing_little", "cmp_dense", "cmp_open", "why_loss_some", "why_loss_none", "why_cell", "why_order", "why_was", "why_unranked", "near", "standing_is", "why_share", "why_share_none", "no_share", "within_tier_share", "within_options", "corro_head", "work_head", "district_head", "rank_none", "within_tier",
             "rank_head", "rank_unranked", "rank_filter_note", "rank_out_kept", "rank_out_dropped", "keep_out_off", "district_pick", "keep_out", "export", "st_options", "cols", "kind", "export_cols"},
       "overlay": {"available", "label", "note", "version", "attribution", "legend", "partial", "lost", "offline", "failed", "missing", "on"} if DV["overlay"].get("available") else {"available", "label", "unavailable"},
       "fields": {"name", "id", "st", "adi", "fn"}, "st_codes": {"0", "18", "33", "50"}, "tier_why": set(c["id"] for c in DV["cells"]), "cls": None, "counts": None, "dcounts": None, "rank": None, "rank_share": None, "loss": None}
unknown = sorted(set(DV) - KEYS) + [f"{k}.{x}" for k, want_ in SUB.items() if want_ is not None for x in sorted(set(DV[k]) - want_)] \
    + [f"cells[].{x}" for c in DV["cells"] for x in sorted(set(c) - {"id", "name", "color", "row", "loss", "rests", "def", "work", "legend"})] + [f"windows[].{x}" for w in DV["windows"] for x in sorted(set(w) - {"id", "label", "is", "years"})] \
    + [f"{k}.{w}" for k in ("cls", "counts", "dcounts", "rank", "rank_share", "loss") for w in sorted(set(DV[k]) - {"2018_2025", "2001_2025", "2017_2023", "2021_2025"})] + [f"loss.{w}.{x}" for w in DV["loss"] for x in sorted(set(DV["loss"][w]) - set("doflsp"))]
PER_UNIT = {"sd", "so", "sf", "low", "near", "corro", "check"} | {f"cls.{w}" for w in DV["cls"]} | {f"loss.{w}.{x}" for w in DV["loss"] for x in "doflsp"}       # the only places where the view may hold one value for every unit
def walk(x, path):
    """Every place in the decision view, outside the per-unit places and the district lists, that holds a list of more than 31 items or a text of more than 1,000 characters; and every per-unit place that is not exactly as long as the units are many."""
    out = []
    if isinstance(x, dict):
        for k, v in x.items():
            out += walk(v, f"{path}.{k}" if path else k)
    elif isinstance(x, (list, str)):
        if path in PER_UNIT:
            if len(x) != n:
                out.append(f"{path} ({len(x):,} items)")
        elif len(x) > (32 if isinstance(x, list) else 1000) and not path.startswith(("rank.", "rank_share.")):
            out.append(f"{path} ({len(x):,} {'items' if isinstance(x, list) else 'characters'})")
        if isinstance(x, list) and path not in PER_UNIT:
            for v in x:
                out += walk(v, path + "[]")
    return out
extra = walk(DV, "")
check("the decision view holds exactly the keys this check knows - at its top, in its texts, its overlay's words, its fields, its filter's codes, each cell, each window and each window's hectares; the places that hold one value for "
      "every unit (the hectares, the cells, the close-call flag and the two badges) are each exactly as long as the units are many; and outside them and the district lists no list in it has more than 32 items and no text more than "
      "1,000 characters. (What this tests is names and sizes: it does not read what a text says.)",
      set(DV) == KEYS and not unknown and not extra, f"unknown: {unknown}; missing: {sorted(KEYS - set(DV))}; out of size: {extra}")
LAYERS = ["forest_area", "hansen_loss", "canopy_band_loss", "corestack_degradation", "corestack_net", "agreement", "nirv", "allocation", "forest_named_expenditure", "st_share", "adi_2011"]       # the eleven layers of the build of 7 October
nd, nc_ = len(D["districts"]), len(DV["cells"])
strs = lambda xs, k: isinstance(xs, list) and len(xs) == k and all(isinstance(x, str) for x in xs)
shapes = {"six cells, five of them in the tier order and one outside it": nc_ == 6 and strs(DV["tiers"], 5) and isinstance(DV["unranked"], str),
          "four windows": len(DV["windows"]) == 4,
          "a count for each cell in each window": all(strs(DV["counts"][w], nc_) for w in DV["counts"]),
          "a count for each cell of each district in each window": all(isinstance(DV["dcounts"][w], list) and len(DV["dcounts"][w]) == nd and all(strs(x, nc_) for x in DV["dcounts"][w]) for w in DV["dcounts"]),
          "a list for each cell of each district in each window, of whole numbers":
              all(isinstance(DV["rank"][w], list) and len(DV["rank"][w]) == nd and all(isinstance(x, list) and len(x) == nc_ and all(isinstance(y, list) and all(isinstance(z, int) for z in y) for y in x) for x in DV["rank"][w]) for w in DV["rank"]),
          "the order by share: in each window, for each district, a list of whole numbers for each of the three cells with loss and nothing for the three without":
              set(DV["rank_share"]) == set(DV["rank"]) and all(isinstance(DV["rank_share"][w], list) and len(DV["rank_share"][w]) == nd and all(isinstance(x, list) and len(x) == nc_ and all(
                  (y is None) == (DV["cells"][k]["loss"] != "some") and (y is None or all(isinstance(z, int) for z in y)) for k, y in enumerate(x)) for x in DV["rank_share"][w]) for w in DV["rank_share"]),
          "eleven labels of the corroboration badge and eight of the district check, all text": strs(DV["corro_labels"], 11) and strs(DV["check_labels"], 8) and isinstance(DV["corro_letters"], str) and len(DV["corro_letters"]) == 12,
          "a grid of three rows of three": isinstance(DV["grid"], list) and len(DV["grid"]) == 3 and all(strs(x, 3) for x in DV["grid"]),
          "every one of the view's texts a text, a list of texts, or for the options of the filter and of the order a list of pairs of texts": all(isinstance(v, str) or strs(v, len(v)) or (k in ("st_options", "within_options") and all(strs(x, 2) for x in v)) for k, v in DV["t"].items()),
          "three rows in a unit's table of hectares and two kinds of unit, as written here": len(DV["t"]["why_rows"]) == 3 and DV["t"]["kind"] == ["LGD panchayat unit", "Outside-village unit"],
          "every word of the overlay, every line of a tier, every field's place and every part of a cell a text or a whole number": all(isinstance(v, (str, int)) and not isinstance(v, bool) for part_ in [DV["overlay"], DV["tier_why"], DV["fields"]] + DV["cells"] for v in part_.values()),
          "the class letters the filter reads begin 0123, the four classes of Scheduled Tribe share in their order": D["codes"][:4] == "0123"}
check("the lists inside the view have the lengths and kinds expected: " + "; ".join(shapes), all(shapes.values()), "not so: " + "; ".join(k for k, v in shapes.items() if not v))
check("the map's data has, at its top, the keys it had before the decision view and one more, 'decision', and its layers are the eleven it had: no layer and no key was added beside the view",
      set(D) == TOP and [l.get("id") for l in D["layers"]] == LAYERS, f"unknown: {sorted(set(D) - TOP)}; missing: {sorted(TOP - set(D))}; layers: {len(D['layers'])}")
check("the view's title, its switch's label and the note under every work-type field are the ones expected", DV["title"] == "Decision view" and DV["radio"].startswith("Where is forest work warranted?") and "ranked within a district" in DV["radio"]
      and DV["work_note"] == (W_NOTE if (W_NOTE := next(iter({r["note"] for r in rows("55_decision/work_types.csv")}))) else ""))
check("the layer's run record names the module that wrote every sentence of the view, with the hash of the file that is on disk",
      REC["decision_view"].get("module", {}).get("sha256") == hashlib.sha256((ROOT / "scripts/_layer_decision.py").read_bytes()).hexdigest())
WIN = {"2018_2025": (2018, 2025), "2001_2025": (2001, 2025), "2017_2023": (2017, 2023), "2021_2025": (2021, 2025)}
SPEC_ORDER = ["open_loss", "dense_loss", "open_none", "dense_none", "little_loss"]                       # the project owner's provisional order, written out
SPEC_NAMES = {"dense_none": "Closed forest, little or no loss recorded - protect", "dense_loss": "Closed forest, loss recorded - find the cause first",
              "open_none": "Open forest, little or no loss recorded - assisted natural regeneration candidate", "open_loss": "Open forest, loss recorded - restore",
              "little_loss": "Little forest left, loss recorded - verify on the ground", "little_none": "Not a forest site"}   # the project owner's names as ruled on 9 October 2026, written out: each states its test
NAMES_BEFORE = ("Protect - intact closed forest", "Closed forest under pressure - find the cause first", "Open forest - assisted natural regeneration candidate", "Open forest still losing - restore",
                "Little forest left, recent loss - verify on the ground")                                       # the five names that were replaced: none may be left anywhere in the view
LEGEND_SHORT = {}                                                # a cell whose name the legend alone shows in a shorter form, written out; every other cell's legend name is its full name
CELL = {("mostly_dense", "none"): "dense_none", ("mostly_dense", "some"): "dense_loss", ("mostly_open", "none"): "open_none", ("mostly_open", "some"): "open_loss",
        ("little_or_none", "some"): "little_loss", ("little_or_none", "none"): "little_none"}
cells = [c["id"] for c in DV["cells"]]
check("four windows, the default 2018-2025; six cells; and each window is named with its years", [w["id"] for w in DV["windows"]] == list(WIN) and DV["default_window"] == "2018_2025" and sorted(cells) == sorted(CELL.values())
      and all(w["label"] == w["id"].replace("_", "-") for w in DV["windows"]), str([w["label"] for w in DV["windows"]]))
smin, lmin = Decimal(str(P["thresholds"]["standing_min_ha"])), Decimal(str(P["thresholds"]["loss_min_ha"]))
check("the two thresholds the page states are the table's, and neither is the agreement test's 100 ha", DV["standing_min"] == f"{smin.normalize():f} ha" and DV["loss_min"] == f"{lmin.normalize():f} ha" and smin != 100 and lmin != 100,
      f"standing {DV['standing_min']}, loss {DV['loss_min']}")

# ---- the hectares: from the stage-1 table itself, year by year ---------------------------------------------------------------------
B = {r["unit_id"]: r for r in rows("20_degradation/hansen_loss_by_canopy_band_by_unit.csv")}
BAND = {"d": "gt30", "o": "gt10le30", "l": "le10"}
bad = {k: 0 for k in ("standing dense", "standing open", "standing forest", "land with 10 % canopy or less", "loss by band and window", "forest loss in the window", "cell", "cell against the printed figures", "close call",
                      "forest at the start of the window", "the share", "the share's blank and its reason", "a share above 100")}
NO_SHARE = f"under {smin.normalize():f} ha of forest at the start of the window: too little for a share to mean anything"       # the reason a blank share carries, as the build's docstring gives it
no_share = {w: 0 for w in WIN}
example = {}
S1 = {}                                                         # per unit, from stage 1 alone: standing dense and open, land, loss by window, loss in two halves of the default window, the cell
for i, u in enumerate(ids):
    b = B[u]
    lost = {k: {y: Decimal(b[f"loss_ha_{s}_{y}"]) for y in range(2001, 2026)} for k, s in BAND.items()}
    sd = max(Decimal(b["area_ha_gt30"]) - sum(lost["d"].values()), Decimal(0))
    so = max(Decimal(b["area_ha_gt10le30"]) - sum(lost["o"].values()), Decimal(0))
    for what, mine, theirs in (("standing dense", shown(sd), DV["sd"][i]), ("standing open", shown(so), DV["so"][i]), ("standing forest", shown(sd + so), DV["sf"][i]), ("land with 10 % canopy or less", shown(b["area_ha_le10"]), DV["low"][i])):
        if mine != theirs:
            bad[what] += 1
            example.setdefault(what, f"unit {u}: shown '{theirs}', the stage table gives '{mine}'")
    S1[u] = {"sd": sd, "so": so, "land": Decimal(b["area_ha_gt30"]) + Decimal(b["area_ha_gt10le30"]) + Decimal(b["area_ha_le10"]), "fl": {}, "cell": {}, "start": {}, "share": {}, "frac": {},
             "first": sum(lost[k][y] for k in "do" for y in range(2018, 2022)), "second": sum(lost[k][y] for k in "do" for y in range(2022, 2026))}
    row = "little_or_none" if Decimal(shown(sd + so).replace(",", "")) < smin else "mostly_dense" if Decimal(shown(sd).replace(",", "")) >= Decimal(shown(so).replace(",", "")) else "mostly_open"
    near = row != "little_or_none" and 10 * min(sd, so) >= 8 * max(sd, so)
    if (DV["near"][i] == "1") != near:
        bad["close call"] += 1
        example.setdefault("close call", f"unit {u}")
    for w, (a, z) in WIN.items():
        part = {k: sum(lost[k][y] for y in range(a, z + 1)) for k in BAND}
        for k in BAND:
            if shown(part[k]) != DV["loss"][w][k][i]:
                bad["loss by band and window"] += 1
                example.setdefault("loss by band and window", f"unit {u}, {w}, {k}: shown '{DV['loss'][w][k][i]}', the stage table gives '{shown(part[k])}'")
        fl = shown(part["d"] + part["o"])
        if fl != DV["loss"][w]["f"][i]:
            bad["forest loss in the window"] += 1
            example.setdefault("forest loss in the window", f"unit {u}, {w}: shown '{DV['loss'][w]['f'][i]}', the stage table gives '{fl}'")
        cell = CELL[(row, "some" if Decimal(fl.replace(",", "")) >= lmin else "none")]
        S1[u]["fl"][w], S1[u]["cell"][w], S1[u]["row"] = part["d"] + part["o"], cell, row
        # the forest at the start of the window, and the loss of the window as a share of it: the dense and the open hectares of 2000, each less its loss in the years before the window, never below nothing
        start = sum(max(Decimal(b[f"area_ha_{BAND[k]}"]) - sum(lost[k][y] for y in range(2001, a)), Decimal(0)) for k in "do")
        given = Decimal(shown(start).replace(",", "")) >= smin                 # on the figure as printed, like every threshold
        share = (100 * (part["d"] + part["o"]) / start).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if given else None
        S1[u]["start"][w], S1[u]["share"][w], S1[u]["frac"][w] = start, share, (Fraction(int((part["d"] + part["o"]) * 10000), int(start * 10000)) if given else None)
        no_share[w] += not given
        if shown(start) != DV["loss"][w]["s"][i] or T[u][f"forest_at_window_start_ha_{w}"] != f"{start:.4f}":
            bad["forest at the start of the window"] += 1
            example.setdefault("forest at the start of the window", f"unit {u}, {w}: shown '{DV['loss'][w]['s'][i]}', table '{T[u][f'forest_at_window_start_ha_{w}']}', the yearly columns give {start:.4f}")
        text = f"{share:.2f}" if given else ""
        if DV["loss"][w]["p"][i] != text or T[u][f"forest_loss_share_pct_{w}"] != text:
            bad["the share"] += 1
            example.setdefault("the share", f"unit {u}, {w}: shown '{DV['loss'][w]['p'][i]}', table '{T[u][f'forest_loss_share_pct_{w}']}', the yearly columns give '{text}'")
        if T[u][f"forest_loss_share_blank_because_{w}"] != ("" if given else NO_SHARE):
            bad["the share's blank and its reason"] += 1
            example.setdefault("the share's blank and its reason", f"unit {u}, {w}: '{T[u][f'forest_loss_share_blank_because_{w}']}'")
        if given and share > 100:
            bad["a share above 100"] += 1
        drawn = cells[D["codes"].index(DV["cls"][w][i])]
        if drawn != T[u][f"cell_{w}"]:
            bad["cell"] += 1
            example.setdefault("cell", f"unit {u}, {w}: drawn '{drawn}', the decision table has '{T[u][f'cell_{w}']}'")
        if drawn != cell:
            bad["cell against the printed figures"] += 1
            example.setdefault("cell against the printed figures", f"unit {u}, {w}: drawn '{drawn}', the printed hectares give '{cell}'")
check(f"standing dense, standing open, standing forest and the land with 10 % canopy or less: all {n:,} units, re-added from the yearly columns of the stage-1 table",
      not any(bad[k] for k in ("standing dense", "standing open", "standing forest", "land with 10 % canopy or less")), "; ".join(example.get(k, "") for k in ("standing dense", "standing open", "standing forest", "land with 10 % canopy or less") if k in example))
check(f"loss from the dense band, the open band and the land below them, in each of the four windows: all {n:,} units x 4 windows x 3", bad["loss by band and window"] == 0, example.get("loss by band and window", f"{12 * n:,} figures"))
check(f"forest loss in the window (dense and open added, then printed): all {n:,} units x 4 windows", bad["forest loss in the window"] == 0, example.get("forest loss in the window", ""))
check(f"the cell each unit is drawn in is the decision table's, in every window: {4 * n:,} cells", bad["cell"] == 0, example.get("cell", ""))
check("the cell follows from the PRINTED hectares and the two thresholds, in every unit and window: a cell never contradicts the figures beside it", bad["cell against the printed figures"] == 0, example.get("cell against the printed figures", ""))
check(f"the forest at the start of each window - the dense and open hectares of 2000 less the forest loss recorded before the window's first year - is, in the table and on the page, what the yearly columns of the stage-1 table give: "
      f"all {n:,} units x 4 windows", bad["forest at the start of the window"] == 0, example.get("forest at the start of the window", f"{4 * n:,} figures"))
check(f"the loss of the window as a share of that forest, half up to two decimals, is in the table and on the page what the yearly columns give, in every unit and window; none is above 100", bad["the share"] == 0 and bad["a share above 100"] == 0,
      example.get("the share", f"{sum(n - no_share[w] for w in WIN):,} shares"))
check("a share is blank exactly where the forest at the start of the window prints under the standing minimum, the table then gives that reason in words and gives none otherwise; and the number of units without a share in each window is the "
      "one the build's run record carries", bad["the share's blank and its reason"] == 0 and all(no_share[w] == P["counts"]["loss_as_a_share"][w]["units_with_no_share"] and n - no_share[w] == P["counts"]["loss_as_a_share"][w]["units_with_a_share"] for w in WIN)
      and all(sum(1 for u in ids if S1[u]["share"][w] is None and S1[u]["cell"][w].endswith("_loss")) == P["counts"]["loss_as_a_share"][w]["units_with_no_share_in_a_cell_with_loss"] for w in WIN)
      and DV["t"]["no_share"] == f"no share: under {smin.normalize():f} ha of forest at the start of the window",
      example.get("the share's blank and its reason", "; ".join(f"{w}: {no_share[w]:,} units without a share" for w in WIN)))
check("no unit of the two forest rows is without a share in any window: what stands now cannot be more than what stood at the window's start", not any(S1[u]["share"][w] is None and S1[u]["row"] != "little_or_none" for u in ids for w in WIN))
check("'close call' is on the units of a forest row whose smaller of standing dense and open is at least four fifths of the larger, and on no other", bad["close call"] == 0, example.get("close call", f"{DV['near'].count('1'):,} units"))

# ---- counts, the order within a district, the tiers ---------------------------------------------------------------------------------
names = [d["name"] for d in D["districts"]]
UA = {r["unit_id"]: r for r in rows("10_units/units_attributes.csv")}
OD = {r["unit_id"]: r for r in rows("10_units/outside_village_district.csv")}
DN = {r["pc11_district_code"]: r["district"] for r in rows("00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv")}
DIST = {u: DN.get((OD[u] if UA[u]["outside_village"] == "1" else UA[u])["pc11_district_code"]) for u in ids}
check("every unit's district is the one 10_units gives it - its census district, or for an outside-village unit the one assigned there - under the name the list of districts uses",
      all(T[u]["district"] == DIST[u] for u in ids) and set(DIST.values()) == set(names), f"{sum(T[u]['district'] != DIST[u] for u in ids)} differ")
ok_counts = all(DV["counts"][w][k] == f"{sum(1 for u in ids if S1[u]['cell'][w] == c):,} units" for w in WIN for k, c in enumerate(cells))
check("the number of units printed beside every cell of the legend is the number that stage 1's hectares put in it, in each window", ok_counts, str({w: DV["counts"][w] for w in list(WIN)[:1]}))
wrong, seen_all, wrong_s, lists_s, differ_s = 0, True, 0, 0, 0
for w in WIN:
    seen = 0
    for di, dname in enumerate(names):
        for k, c in enumerate(cells):
            mine = [u for u in ids if DIST[u] == dname and S1[u]["cell"][w] == c]
            # the rule itself, on stage 1's own hectares and 10_units' own district: loss cells by forest loss, the others by standing hectares of the row's band; ties by unit id
            keyf = (lambda u: S1[u]["fl"][w]) if c.endswith("_loss") else (lambda u: S1[u]["sd"]) if c == "dense_none" else (lambda u: S1[u]["so"]) if c == "open_none" else (lambda u: S1[u]["sd"] + S1[u]["so"])
            mine.sort(key=lambda u: (-keyf(u), u))
            listed = [ids[j] for j in DV["rank"][w][di][k]]
            wrong += listed != mine
            seen += len(listed)
            wrong += DV["dcounts"][w][di][k] != f"{len(mine):,}"
            # the second order: by share in a cell with loss (units without a share after the others, by hectares lost); a cell without loss has none on the page, and in the table it is the first order
            by = DV["rank_share"][w][di][k]
            if c.endswith("_loss"):
                mine_s = sorted(mine, key=lambda u: (0, -S1[u]["frac"][w], -S1[u]["fl"][w], u) if S1[u]["frac"][w] is not None else (1, Fraction(0), -S1[u]["fl"][w], u))
                wrong_s += by is None or [ids[j] for j in by] != mine_s or any(T[u][f"order_in_district_cell_by_share_{w}"] != str(pos) for pos, u in enumerate(mine_s, 1))
                lists_s += 1
                differ_s += mine_s != mine
            else:
                wrong_s += by is not None or any(T[u][f"order_in_district_cell_by_share_{w}"] != T[u][f"order_in_district_cell_{w}"] for u in mine)
    seen_all &= seen == n
check("within each district and cell the units are in the stated order - loss cells by forest loss in the window, the others by standing hectares of the row's band, ties by unit id - in every window, on stage 1's hectares and 10_units' districts; every unit is listed once",
      wrong == 0 and seen_all, f"{wrong} of {4 * len(names) * len(cells)} lists differ")
check("the second order, by share, is what the yearly columns give: in every district and every cell with loss, units with a share by loss over the forest at the window's start as an exact fraction, largest first, ties by "
      "hectares lost then unit id, and the units without a share after them by hectares lost - on the page and in the table's own column; a cell without loss has no such list on the page and keeps the first order in the table",
      wrong_s == 0 and lists_s == 4 * len(names) * 3, f"{wrong_s} lists differ; of the {lists_s} lists by share, {differ_s} are in another order than by hectares")
check("the order is held district by district - thirty lists of six cells in each window; the two checks above look for an unknown key and for a list or a text too long for its place",
      set(DV["rank"]) == set(WIN) and all(len(DV["rank"][w]) == len(names) == 30 and all(len(d) == 6 for d in DV["rank"][w]) for w in WIN))
tiers = rows("55_decision/tiers.csv")
order = [r["cell"] for r in tiers if r["tier"] != ""]
check("the tier order the page starts with is the project owner's provisional order, written out in this check, with 'Not a forest site' outside it; and the six cells carry his names",
      DV["tiers"] == order == P["tiers"]["order"] == SPEC_ORDER and DV["unranked"] == "little_none" and {c["id"]: c["name"] for c in DV["cells"]} == SPEC_NAMES, " > ".join(order))
everything = json.dumps(D, ensure_ascii=False) + page
check("the five names that were replaced on 9 October 2026 are nowhere in the page or its data, nor are the words they over-claimed with ('under pressure', 'intact', 'still losing', 'recent loss'); the tiers table carries the new names; "
      "and the legend shows each cell under its full name, or under the shorter form written out in this check",
      not any(x in everything for x in NAMES_BEFORE) and not re.search(r"under pressure|\bintact\b|still losing|recent loss", json.dumps(DV, ensure_ascii=False) + D["about_html"][D["about_html"].index("Decision view: where is forest work warranted?"):])
      and {r["cell"]: r["cell_name"] for r in tiers} == SPEC_NAMES and all(r["tier_label"] == (f"Tier {r['tier']}: " if r["tier"] else "Not ranked: ") + SPEC_NAMES[r["cell"]] for r in tiers)
      and {c["id"]: c["legend"] for c in DV["cells"]} == {**SPEC_NAMES, **LEGEND_SHORT} and "dvTierLabel(cell, cell.legend)" in page and page.count("cell.legend") == 1,
      f"shortened in the legend: {LEGEND_SHORT or 'none'}")
check("each cell's row and column are the ones its hectares are tested for, and the grid of six in every panel puts each cell under its own row and column",
      all(CELL[({"mostly dense": "mostly_dense", "mostly open": "mostly_open", "little or none": "little_or_none"}[c["row"]], c["loss"])] == c["id"] for c in DV["cells"])
      and DV["grid"] == [["Mostly dense", "dense_none", "dense_loss"], ["Mostly open", "open_none", "open_loss"], ["Little or none", "little_none", "little_loss"]]
      and DV["t"]["grid_cols"] == ["No forest loss in the window", "Some forest loss in the window"])
check("every tier has its one line of reason, and the text says the order is provisional and the user's to change", all(DV["tier_why"].get(c) for c in order) and "provisional" in DV["t"]["tiers_head"].lower()
      and "a forester could reasonably put" in DV["tier_why"]["dense_loss"].lower())
check("a rank is shown as a tier label with its cell's name, never a bare number", DV["t"]["tier"] == "Tier {k}: {name}" and "{name}" in DV["t"]["unranked"])

# ---- corroboration: straight from the agreement table ---------------------------------------------------------------------------------
A = {r["unit_id"]: r for r in rows("20_degradation/agreement_by_unit.csv")}
words = {"both": "Both measures flag this unit", "hansen_only": "Only Hansen flags it", "corestack_only": "Only CoRE Stack flags it", "neither": "Neither measure flags it"}
wrong, east, notc = 0, 0, 0
for i, u in enumerate(ids):
    a, text = A[u], DV["corro_labels"][DV["corro_letters"].index(DV["corro"][i])]
    if a["agreement_class"] in words:
        ok = text.startswith(words[a["agreement_class"]]) and "East Coast" not in text
    elif a["agreement_class"] == "zone_model_excluded":
        east += 1
        ok = text.startswith(words[a["agreement_class_all_assessed"]]) and "East Coast zone model: the placebo failed there" in text and "unreliable" in text
    else:
        notc += 1
        ok = text.startswith("Not compared") and (("under 100 ha of land with canopy above 10 %" in text) == (Decimal(a["reference_ha"]) < 100)) and \
             (("CoRE Stack gives no class on such land" in text) == (Decimal(a["reference_ha"]) < 100 and Decimal(a["corestack_valued_ha"]) == 0)) and "coverage" not in text and \
             (("CoRE Stack gives a class on under 100 ha of this unit's land with canopy above 10 % in 2000" in text) == (Decimal(a["corestack_valued_ha"]) < 100 <= Decimal(a["reference_ha"]))) and \
             (Decimal(a["reference_ha"]) < 100 or Decimal(a["corestack_valued_ha"]) < 100)
    wrong += not ok
check(f"the corroboration badge of every unit says what agreement_by_unit.csv says of it; the East Coast note is on its {east:,} units and no other; {notc:,} units are 'not compared', each with its reason", wrong == 0, f"{wrong} differ")
check("the badge names its own window, 2017-2023, whatever window is selected", "2017-2023" in DV["t"]["corro_head"] and "whatever window" in DV["t"]["corro_head"] and any("2017-2023" in c for c in DV["t"]["cols"]))

# ---- the outside-village units ------------------------------------------------------------------------------------------------------------
say = {"moved": "moved off the name", "noname": "names no district", "ambiguous": "ambiguous", "flagged": "flagged", "nocheck": "no check possible"}
wrong, n_out = 0, 0
for i, u in enumerate(ids):
    text = DV["check_labels"][int(DV["check"][i], 36)]
    if D["out"][i] != "1":
        wrong += text != ""
        continue
    n_out += 1
    o = OD[u]
    want = {"moved": o["assigned_by"] == "two checks against the label", "noname": o["assigned_by"].endswith("has no district name"), "ambiguous": o["ambiguous"] == "1",
            "flagged": o["area_majority_agrees_with_assigned"] == "0" or (o["label_absent_from_collar"] == "1" and o["assigned_by"] == "label"), "nocheck": o["ambiguous_basis"] == "not measurable"}
    wrong += any((say[k] in text) != v for k, v in want.items()) or (not any(want.values()) and "none of the district checks' flags is raised" not in text) or "no check contradicts" in text
check(f"each of the {n_out:,} outside-village units says what its assigned district rests on, as outside_village_district.csv has it, and no other unit says anything", wrong == 0 and n_out == D["out"].count("1"), f"{wrong} differ")
check("their governance prompt is the one asked for, word for word", DV["governance"] == "No revenue village — this land is in no village plan. Whose plan covers it?", DV["governance"])
F = DV["fields"]
nc = "no census data for this land"
check("beside the tier, an outside-village unit's census columns read 'no census data for this land', never blank or zero; the columns are the panel's own cells",
      all((D["f"][i][F["st"]] == nc and D["f"][i][F["adi"]] == nc) == (D["out"][i] == "1") for i in range(n)) and not any(D["f"][i][F["st"]] in ("", "0", "0.00 %") and D["out"][i] == "1" for i in range(n)))
dv_js = page.split("<script>")[-1]
dv_js = dv_js[dv_js.index("the decision view (added 8 Oct 2026) ---"):dv_js.index("// ---- start:")]
bare = lambda s: " ".join(re.sub(r"(?m)\s+//.*$", "", s).split())            # a piece of the page's script without its comments, its spacing made single
dv_bare = bare(dv_js)
rows_fn = dv_js[dv_js.index("function dvRows()"):dv_js.index("function dvFilterLabel()")]
ROWS_FN = ('function dvRows() { var per = DV.rank[state.window][state.rank], bys = state.within === "share" ? DV.rank_share[state.window][state.rank] : null, st = layerById.st_share.cls.all, need = DV.st_codes[state.st] || "", '
           'out = { rows: [], dropped: 0, outKept: 0, outDropped: 0 }, t, cell, idx, j, i, list; for (t = 0; t < state.tiers.length; t++) { cell = dvCellById(state.tiers[t]); idx = DV.cells.indexOf(cell); '
           'list = (bys && bys[idx]) ? bys[idx] : per[idx]; for (j = 0; j < list.length; j++) { i = list[j]; if (need) { '
           'if (D.out.charAt(i) === "1") { if (state.keepOut) { out.outKept++; } else { out.outDropped++; continue; } } else if (need.indexOf(st.charAt(i)) < 0) { out.dropped++; continue; } } '
           'out.rows.push([i, cell]); } } return out; }')            # the whole of the function, as it must read
check("Scheduled Tribe share is a filter and nothing else, in the page's own script: the view reads the classes of that layer in one place, the function that lists a district's rows; there the one use of a unit's class is to "
      "leave its row out; that function takes the rows in one of the two orders the builder gave - by hectares lost, or by share lost - and sorts nothing; and the view's only sort anywhere is of tier names read from an address. (That the rows a browser shows are in the "
      "order expected under each setting of the filter is the browser exercise's to show.)",
      set(DV["st_codes"]) == {"0", "18", "33", "50"} and DV["st_codes"]["0"] == "" and "it never orders it" in DV["t"]["rank_filter_note"]
      and dv_js.count("layerById.st_share") == 1 and "st = layerById.st_share.cls.all" in rows_fn and re.findall(r"(?<![.\w])st\b[^\n]{0,12}", rows_fn) == ["st = layerById", "st.charAt(i)) "]
      and "else if (need.indexOf(st.charAt(i)) < 0) { out.dropped++; continue; }" in rows_fn and ".sort(" not in rows_fn and "out.rows.push([i, cell]);" in rows_fn and rows_fn.count(".push(") == 1
      and re.findall(r"[^\n]*\.sort\([^\n]*", dv_js) == ["    if (!t || t.slice().sort().join() !== DV.tiers.slice().sort().join()) { t = DV.tiers.slice(); }"] and ".reverse(" not in dv_bare and ".splice(" not in dv_bare
      and ROWS_FN in dv_bare,
      f"sorts in the view's script: {len(re.findall(r'[.]sort[(]', dv_js))}; places that read the classes: {dv_js.count('layerById.st_share')}")

# ---- the work-type field, the texts, the export --------------------------------------------------------------------------------------------
W = {r["cell"]: r for r in rows("55_decision/work_types.csv")}
SCHED = ROOT / "00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv"
registered = SCHED.is_file()
pending = ("pending — schedule not yet registered",)
check("the work-type field of each cell is the decision table's" + (", from the registered schedule" if registered else ": 'pending', because no schedule of permissible works is registered"),
      all(c["work"] == W[c["id"]]["work_type_field"] for c in DV["cells"]) and (registered or all(c["work"] in pending for c in DV["cells"])) and P["work_types"]["registered"] == registered, DV["cells"][0]["work"][:90])
if registered:
    LIST = {int(r["serial"]): r for r in rows("00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv")}
    cited_ok, n_cited = True, 0
    for c in DV["cells"]:
        for m in re.finditer(r"(?:([A-Z][A-Za-z ]+?) - )?Sl\. (\d+) ([^;.]+)", c["work"]):
            n_cited += 1
            cited_ok &= int(m.group(2)) in LIST and LIST[int(m.group(2))]["work_name"] == m.group(3).strip()
        for m in re.finditer(r"(?:^|\. |: )([A-Z][A-Za-z ]+?) - ((?:Sl\. \d+ [^;.]+(?:; )?)+)", c["work"]):       # a heading, then the rows under it: the heading is the list's own work type of each of them
            cited_ok &= all(LIST[int(s)]["work_type"] == m.group(1) for s in re.findall(r"Sl\. (\d+)", m.group(2)))
        cited_ok &= sorted(set(int(s) for s in re.findall(r"Sl\. (\d+)", c["work"]))) == sorted(int(s) for s in W[c["id"]]["entries"].split("; ") if s)
        ent, groups = [int(s) for s in W[c["id"]]["entries"].split("; ") if s], []
        for s in ent:                                                  # the rows in the order cited, gathered under the list's own work type of each
            if groups and groups[-1][0] == LIST[s]["work_type"]:
                groups[-1][1].append(s)
            else:
                groups.append((LIST[s]["work_type"], [s]))
        listing = " ".join(f"{ty} - " + "; ".join(f"Sl. {s} {LIST[s]['work_name']}" for s in ss) + "." for ty, ss in groups)
        cited_ok &= c["work"].endswith(listing) if ent else "Sl." not in c["work"]
    check("every row of the list that a cell cites carries, beside its serial number, the work name the registered list gives that number; the cell's list of entries is the rows its field cites; and the field ends with exactly those rows, "
          "each group under the list's own work type written out as the list has it, so a heading cannot be dropped or reworded", cited_ok and n_cited > 0, f"{n_cited} citations")
SUMM = [r for r in rows("20_degradation/agreement_summary.csv") if r["window"] == "common_2017_2023" and float(r["minimum_reference_ha"]) == 100 and r["delivered"] == "1"]
S, SA = [r for r in SUMM if r["units"] == "lgd_panchayat"], [r for r in SUMM if r["units"] == "all units"]
about = D["about_html"]
dv_about = about[about.index("Decision view: where is forest work warranted?"):] if "Decision view: where is forest work warranted?" in about else ""
plain = " ".join(re.sub(r"<[^>]+>", "", dv_about).split())
if len(S) == 1 and len(SA) == 1:
    s, sa = S[0], SA[0]
    within = f"{float(s['odds_ratio_within_districts']):.2f}, interval {float(s['odds_ratio_within_districts_lo95']):.2f} to {float(s['odds_ratio_within_districts_hi95']):.2f}"
    across = f"{float(s['odds_ratio']):.2f}, {float(s['odds_ratio_lo95']):.2f} to {float(s['odds_ratio_hi95']):.2f}"
    across_all = f"{float(sa['odds_ratio']):.2f}, {float(sa['odds_ratio_lo95']):.2f} to {float(sa['odds_ratio_hi95']):.2f}"
    check("the reason for ranking only within a district is in the About text and in the empty list, with the odds ratios as agreement_summary.csv has them, the units they are of, and the words 'not established'",
          within in plain and across in plain and within in DV["t"]["rank_none"] and across in DV["t"]["rank_none"] and "never across the state" in DV["t"]["rank_none"] and "not established" in DV["t"]["rank_none"]
          and f"Among the {int(s['n_assessed']):,} LGD panchayat units of the agreement test's headline" in plain and "East Coast zone left out" in plain and "not established" in plain
          and f"For all units of that headline together the across-state figure is {across_all}" in plain and float(s["odds_ratio_lo95"]) < 1 < float(s["odds_ratio_hi95"]) and float(s["odds_ratio_within_districts_lo95"]) > 1,
          f"within districts {within}; across the state {across}; all units {across_all}")
else:
    check("agreement_summary.csv has one headline row for LGD panchayat units and one for all units", False)

# every other figure of the About text, worked out here from stage 1 and held against the sentence that carries it
pixel = Decimal(next(r for r in rows("20_degradation/forest_floor_repeatability.csv") if float(r["forest_ha_from"]) == 1.0)["one_pixel_as_share_of_forest_at_the_bottom"])
p2 = lambda x: Decimal(shown(x).replace(",", ""))                # a figure as printed, for a threshold
dw = "2018_2025"
dense_name, open_loss_name, intact_name, unranked_name = SPEC_NAMES["dense_loss"], SPEC_NAMES["open_loss"], SPEC_NAMES["dense_none"], SPEC_NAMES["little_none"]
def cells_at(s_, l_):
    out = {}
    for u in ids:
        v = S1[u]
        row = "little_or_none" if p2(v["sd"] + v["so"]) < s_ else "mostly_dense" if p2(v["sd"]) >= p2(v["so"]) else "mostly_open"
        out[u] = CELL[(row, "some" if p2(v["fl"][dw]) >= l_ else "none")]
    return out
base = cells_at(smin, lmin)
alt_s, alt_l = [Decimal(str(x)) for x in P["thresholds"]["alternatives"]["standing_min_ha"]], [Decimal(str(x)) for x in P["thresholds"]["alternatives"]["loss_min_ha"]]
moved = []
for a_, b_ in ((alt_s[0], lmin), (alt_s[1], lmin), (smin, alt_l[0]), (smin, alt_l[1])):
    other = cells_at(a_, b_)
    moved.append(sum(1 for u in ids if other[u] != base[u]))
g = lambda x: f"{x.normalize():f}"
site = [u for u in ids if p2(S1[u]["sd"] + S1[u]["so"]) >= smin]
total = sum(S1[u]["sd"] + S1[u]["so"] for u in ids)
pct = lambda a, b: round(100 * float(a) / float(b), 1)
had = [u for u in site if p2(S1[u]["first"]) >= lmin]
none_ = [u for u in site if S1[u]["first"] < pixel]
size = lambda lo, hi: [u for u in site if S1[u]["sd"] + S1[u]["so"] >= lo and (hi is None or S1[u]["sd"] + S1[u]["so"] < hi)]
some = lambda us: sum(1 for u in us if base[u].endswith("_loss"))
dl = [u for u in ids if base[u] == "dense_loss"]
out_units = [u for i, u in enumerate(ids) if D["out"][i] == "1"]
intact = [u for u in ids if base[u] == "dense_none"]
A_ = {r["unit_id"]: r for r in rows("20_degradation/agreement_by_unit.csv")}
badge = lambda u: A_[u]["agreement_class"] if A_[u]["agreement_class"] in ("both", "hansen_only", "corestack_only", "neither") else A_[u]["agreement_class_all_assessed"] if A_[u]["agreement_class"] == "zone_model_excluded" else "not_compared"
intact_flagged = [u for u in intact if badge(u) in ("corestack_only", "both")]
R620 = {r["fy"]: r for r in rows("40_allocation/state_fy_r620_vs_dump.csv")}
full_open_loss = [u for u in ids if S1[u]["cell"]["2001_2025"] == "open_loss"]
near_n = sum(1 for u in site if 10 * min(S1[u]["sd"], S1[u]["so"]) >= 8 * max(S1[u]["sd"], S1[u]["so"]))
row_words = {"mostly_dense": "mostly dense", "mostly_open": "mostly open", "little_or_none": "little or none"}
CAUT = json.loads((ROOT / "00_raw/05_forest_reference/provider_cautions.json").read_text(encoding="utf-8"))          # the providers' cautions about the data, registered on 9 October 2026
NUM = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
ov_cfg = json.loads((ROOT / "scripts/layer_overlay.json").read_text(encoding="utf-8")) if (ROOT / "60_layer/overlay.js").is_file() else None
want = {
    "the table of the six cells: units, and outside-village units among them": all(
        f"{SPEC_NAMES[c]}</td><td>{row_words[r]}</td><td>{col}</td><td>{sum(1 for u in ids if base[u] == c):,}</td><td>{sum(1 for u in out_units if base[u] == c):,}</td>" in dv_about for (r, col), c in CELL.items()),
    "units with a loss under the area of the pixel in the middle of the state": f"in 2018-2025 {sum(1 for u in ids if 0 < S1[u]['fl'][dw] < pixel):,} units have a recorded forest loss above zero and under {g(pixel)} ha, the area of one pixel in the middle of the state" in plain
                                                    and "one pixel or less" not in plain and f"One pixel is about {pixel:.2f} ha" in plain,
    "the number of works in the registered list": (not registered) or f"({len(LIST)} works)" in plain,
    "the version the overlay's tiles carry": (not ov_cfg) or f"Tiles: {ov_cfg['data_version']}" in plain,
    "the share of standing forest in the forest sites": f"Units with {g(smin)} ha or more standing hold {pct(sum(S1[u]['sd'] + S1[u]['so'] for u in site), total):.1f} % of all standing forest" in plain,
    "recurrence of loss, and loss starting afresh": f"Among units with {g(smin)} ha or more standing, {pct(sum(1 for u in had if p2(S1[u]['second']) >= lmin), len(had)):.0f} % of those that lost {g(lmin)} ha or more in 2018-2021 lost that much again in 2022-2025; "
                                                    f"of those that lost under {g(pixel)} ha, or nothing, {pct(sum(1 for u in none_ if p2(S1[u]['second']) >= lmin), len(none_)):.0f} %" in plain,
    "units moved by each alternative threshold, with the window named": f"In the window 2018-2025: with {g(lmin)} ha for loss, moving the standing minimum to {g(alt_s[0])} ha or {g(alt_s[1])} ha moves {moved[0]:,} or {moved[1]:,} units to another cell; "
                                                    f"with {g(smin)} ha standing, moving the loss minimum to {g(alt_l[0])} ha or {g(alt_l[1])} ha moves {moved[2]:,} or {moved[3]:,}." in plain,
    "how the loss column follows the size of the forest": f"{pct(some(size(10, 25)), len(size(10, 25))):.0f} % of the forest sites with 10 to 25 ha standing have some loss, and {pct(some(size(5000, None)), len(size(5000, None))):.0f} % of those with 5,000 ha or more; "
                                                    f"{sum(1 for u in dl if S1[u]['share'][dw] is not None and S1[u]['share'][dw] < 1):,} of the {len(dl):,} units in {dense_name} lost under 1 % of the forest they had at the start of the window, and "
                                                    f"{sum(1 for u in site if base[u].endswith('_none') and S1[u]['share'][dw] is not None and S1[u]['share'][dw] > 2):,} forest sites in a cell with little or no loss recorded lost over 2 % of theirs" in plain,
    "units with a share and without one": f"In the window 2018-2025, {n - no_share[dw]:,} units have a share and {no_share[dw]:,} have none, {sum(1 for u in ids if S1[u]['share'][dw] is None and base[u].endswith('_loss')):,} of those in a cell with loss recorded" in plain
                                                    and f"Where a unit had under {g(smin)} ha of forest at the start of the window no share is given" in plain,
    "small units, the two cells they are in, and forest on half the land of a unit that is not a forest site": (lambda small: all(base[u] in ("little_none", "little_loss") for u in small) and
        f"{len(small):,} units have under {g(smin)} ha of land and so have little or none whatever their cover: {sum(1 for u in small if base[u] == 'little_none'):,} of them are in {unranked_name} and "
        f"{sum(1 for u in small if base[u] == 'little_loss'):,}, which lost {g(lmin)} ha or more in the window, in {SPEC_NAMES['little_loss']}. "
        f"In {sum(1 for u in ids if base[u] == 'little_none' and S1[u]['land'] > 0 and 2 * (S1[u]['sd'] + S1[u]['so']) >= S1[u]['land']):,} units of the cell {unranked_name} standing forest covers half or more of the land" in plain)(
        [u for u in ids if S1[u]["land"] < smin]),
    "units near the dense and open line": f"Of the {len(site):,} units with {g(smin)} ha or more, {near_n:,} have the smaller within a fifth of the larger" in plain,
    "plantation's share in the two years the default window's reason names": f"plantation is {float(R620['2016-17']['r620_plantation_share_pct']):.1f} % of expenditure there in FY2016-17 and {float(R620['2018-19']['r620_plantation_share_pct']):.1f} % in FY2018-19" in plain
                                                    and float(R620["2018-19"]["r620_plantation_share_pct"]) < float(R620["2016-17"]["r620_plantation_share_pct"]) / 2,
    "what 'still losing' means under the full record": f"{sum(1 for u in full_open_loss if p2(S1[u]['fl'][dw]) < lmin):,} of the {len(full_open_loss):,} units in {open_loss_name} under that window lost under {g(lmin)} ha in 2018-2025" in plain,
    "what 'intact' means, and how many of that cell CoRE Stack flags": f"In the window 2018-2025, of the {len(intact):,} units in {intact_name}, {sum(1 for u in intact if badge(u) != 'not_compared'):,} were compared, and {len(intact_flagged):,} of those are flagged by CoRE Stack for degradation "
                                                    f"({sum(1 for u in intact_flagged if A_[u]['agreement_class'] == 'zone_model_excluded'):,} of them under the East Coast model). That cell's name says little or no loss recorded, which means under {g(lmin)} ha of forest loss in the window chosen "
                                                    f"for each unit: its units together carry {round(float(sum(S1[u]['fl'][dw] for u in intact)), 2):,.1f} ha of forest loss in that window, "
                                                    f"{sum(1 for u in intact if p2(S1[u]['fl']['2001_2025']) >= lmin):,} of them lost {g(lmin)} ha or more at some time in 2001-2025" in plain,
    "outside-village units in a ranked cell": f"in the window 2018-2025, {sum(1 for u in out_units if base[u] != 'little_none'):,} of them are in a cell other than {unranked_name}" in plain and dw == "2018_2025",
    "how many cells name rows of the list": (not registered) or (f"{NUM[sum(1 for c in DV['cells'] if 'Sl. ' in c['work'])].capitalize()} of the {NUM[len(DV['cells'])]} cells name rows of the official list of permissible works by serial number, "
                                                              f"and the other {NUM[sum(1 for c in DV['cells'] if 'Sl. ' not in c['work'])]} name none" in plain and "Each cell names rows" not in plain),
    "nothing is said of what a single district's list rests on": "a district's list rests on" not in plain,
    "the number of columns of an exported list": f"An exported list has {len(DV['t']['export_cols'])} columns; the development index is shown in the list on this page and is left out of the exported file" in plain,
    "the provider's two cautions, word for word from the registered record, and the two rates in them": all(CAUT["sentences"][k]["text"] in plain for k in ("cover_today_is_not_cover_of_2000_less_loss", "errors"))
        and f"false positives (commission errors) in this data at {CAUT['percentages_read_from_the_sentences']['false_positives_pct']}%" in plain and f"false negatives (omission errors) at {CAUT['percentages_read_from_the_sentences']['false_negatives_pct']}%" in plain
        and "the clearing of at least half of it" in plain and "clearing of at least half of tree cover" in CAUT["sentences"]["loss_is"]["text"],
    "what is said of keys is what the registration says": (not ov_cfg) or ("the tile service's reference declares none and it returns tiles without one" in plain and "no way to send one" not in plain
                                                                           and "declares no key scheme and the service returns every tile without one" in ov_cfg["terms_unresolved"]),
}
check(f"each of the {len(want)} sentences of the About text that carries a count or a share says the figure worked out here from stage 1's tables", all(want.values()), "NOT AS WORKED OUT HERE: " + "; ".join(k for k, v in want.items() if not v) if not all(want.values()) else "")
# The three counts that section 5.1 of docs/DECISION_LAYER.md gives (since 10 October 2026 on the share the panel prints, whose denominator is the forest at the
# start of the window): units of the cell of closed forest with loss that lost under 1 % and under 0.1 % of it, and forest sites in a cell without loss that lost
# over 2 %. Worked out here from stage 1's yearly columns (S1), and counted again on the decision table's own column. The document's writer reads the line this prints.
share_col = {u: (Decimal(T[u][f"forest_loss_share_pct_{dw}"]) if T[u][f"forest_loss_share_pct_{dw}"] != "" else None) for u in ids}
three = lambda sh: (sum(1 for u in dl if sh(u) is not None and sh(u) < 1), sum(1 for u in dl if sh(u) is not None and sh(u) < Decimal("0.1")),
                    sum(1 for u in site if base[u].endswith("_none") and sh(u) is not None and sh(u) > 2))
worked, on_column = three(lambda u: S1[u]["share"][dw]), three(lambda u: share_col[u])
check(f"three counts on the loss share - units of {dense_name} that lost under 1 % and under 0.1 % of the forest they had at the start of the window, and forest sites in a cell with little or "
      f"no loss recorded that lost over 2 % of it - are the same worked out here from stage 1's yearly columns and counted on the column forest_loss_share_pct_{dw} of the decision table "
      "(docs/DECISION_LAYER.md is not read here: its writer holds the counts of its section 5.1 against the figures this line prints)",
      worked == on_column and worked[1] <= worked[0] <= len(dl),
      f"counts on the share: under 1 %: {worked[0]:,}; under 0.1 %: {worked[1]:,}; over 2 % in a cell without loss: {worked[2]:,}" + ("" if worked == on_column else f"; ON THE COLUMN: {on_column}"))
STANDING_IS = "the forest of 2000 with no loss recorded since; not a measure of tree cover today"                # the owner's wording of 9 October 2026
check("the About text says the thresholds were ruled on by the owner on 9 October 2026 as proposed, the tiers are provisional, standing forest is 'the forest of 2000 with no loss recorded since; not a measure of tree cover today', "
      "that there is no score, and what orders the units within a tier; the build's record gives the thresholds the same standing",
      all(x in plain for x in ("Two thresholds, ruled on by the project owner on 9 October 2026 as they were proposed.", "provisional", STANDING_IS, "No score", "not a verdict", DV["t"]["within_tier"]))
      and "await a ruling" not in plain and "(proposed)" not in json.dumps(DV) and P["thresholds"]["status"].startswith("RULED by the project owner on 9 October 2026"))
check("the About text states the two thresholds, the four windows and the provisional order of tiers as the table and the specification have them",
      f"A unit has little or none under {g(smin)} ha of standing forest; it has some loss from {g(lmin)} ha of forest loss in the window." in plain
      and all(f"{a}-{z} (" in plain for a, z in WIN.values()) and "; ".join(f"{i + 1} {SPEC_NAMES[c]}" for i, c in enumerate(SPEC_ORDER)) + f"; {unranked_name} is on the map and outside the list" in plain)
if registered:
    NF = rows("55_decision/work_rows_naming_forest.csv")
    forest_rows = [r for r in LIST.values() if "forest" in (r["work_type"] + " " + r["work_name"]).lower()]
    cited_all = {int(s) for c in DV["cells"] for s in re.findall(r"Sl\. (\d+)", c["work"])}
    check("the rows of the registered list that name forest and are cited by no cell are all named in the About text, each with its serial number, its name and its work type; the layer sends its reader to no file that does not travel with it",
          len(NF) == len(forest_rows) and all(f"Sl. {int(r['serial'])} {r['work_name']} ({r['work_type']})" in plain for r in forest_rows if int(r["serial"]) not in cited_all)
          and sum(1 for r in forest_rows if int(r["serial"]) not in cited_all) > 0 and "docs/DECISION_LAYER.md" not in json.dumps(DV) and "docs/DECISION_LAYER.md" not in D["sources_html"],
          f"{sum(1 for r in forest_rows if int(r['serial']) not in cited_all)} of {len(forest_rows)} rows")
check("standing forest is nowhere called a lower bound - not in the view's data, its About text, the page's script, the decision table's run record or the layer's - and the sentence that replaced it is in the legend's note, "
      "in every unit's block and under the ranked list",
      "Standing forest is " + STANDING_IS + "." in DV["t"]["legend_note"] and DV["t"]["standing_is"] == "Standing forest is " + STANDING_IS + "." and page.split("<script>")[-1].count("t.standing_is") >= 2
      and not any("lower bound" in x.lower() or "lower_bound" in x for x in (json.dumps(DV), dv_about, page.split("<script>")[-1], json.dumps(REC["decision_view"])))
      and STANDING_IS in P["definitions"]["standing"] and "LOWER BOUND" not in json.dumps(P["definitions"]["standing"]))
check("the window is named in the legend, in the unit's panel, at the head of the ranked list and in the export's columns", "{window}" in DV["t"]["legend_title"] and "{window}" in DV["t"]["why_window"] and "{window}" in DV["t"]["rank_head"]
      and "{window}" in DV["t"]["why_cols"][2] and "window_of_forest_loss" in DV["t"]["export_cols"])
check("the list's eleven column heads are the ones asked for - the share beside the hectares lost, the development index still in the list on the page, the spending column labelled with where the geotagged record ends; the head "
      "of the list says which of the two orders within a tier is in use, by hectares lost as the page opens or by share lost, and that the cells without loss stay ordered by standing hectares; and the address carries the order",
      DV["t"]["cols"] == ["Tier", "Unit", "Kind", "Standing dense, ha", "Standing open, ha", "Forest loss in {window}, ha", "Loss as a share of the forest at the start of {window}, %", "Corroboration, 2017-2023", "Scheduled Tribe share",
                          "Development index 2011", "Forest-named spending (geotagged record; ends FY2017-18)"]
      and "{within}" in DV["t"]["rank_head"] and "largest first" in DV["t"]["within_tier"] and "by forest loss in the window where the cell has loss" in DV["t"]["within_tier"]
      and "as a share of the forest at the start of the window where the cell has loss" in DV["t"]["within_tier_share"] and all("by standing hectares of the cell's band where it has none" in DV["t"][k] for k in ("within_tier", "within_tier_share"))
      and DV["t"]["within_options"] == [["ha", "Within a tier: by hectares lost"], ["share", "Within a tier: by share lost"]]
      and 'function dvWithin() { return state.within === "share" ? DV.t.within_tier_share : DV.t.within_tier; }' in dv_bare and 'state.within = "ha";' in page and 'if (state.within !== "ha") { h += "&within=" + state.within; }' in dv_bare
      and 'wi = h0.within === "share" ? "share" : "ha";' in dv_bare and "within: dvWithin()" in dv_bare)
st_classes = [c["label"] for c in next(l for l in D["layers"] if l["id"] == "st_share")["classes"]]
check("each choice of the Scheduled Tribe filter keeps the classes its label names",
      DV["t"]["st_options"] == [["0", "No filter"], ["18", "Scheduled Tribe share 18 % or more"], ["33", "Scheduled Tribe share above 33 %"], ["50", "Scheduled Tribe share more than 50 %"]]
      and DV["st_codes"] == {"0": "", "18": "123", "33": "23", "50": "3"} and st_classes[:4] == ["Less than 18 %", "18 to 33 %", "33 to 50 %", "More than 50 %"])
EXPORT = ["district", "unit_id", "unit_name", "unit_type", "outside_village", "window_of_forest_loss", "standing_forest_is_through", "tier_label", "tier_definition", "tier_order_in_use", "tier_order_is", "order_within_a_tier",
          "standing_dense_ha", "lost_from_dense_in_window_ha", "standing_open_ha", "lost_from_open_in_window_ha", "land_with_10pct_canopy_or_less_in_2000_ha", "lost_on_that_land_in_window_ha_reported_only", "standing_forest_ha",
          "forest_loss_in_window_ha", "forest_at_window_start_ha", "forest_loss_share_pct", "standing_minimum", "loss_minimum", "close_call_dense_or_open", "corroboration", "corroboration_window", "scheduled_tribe_share",
          "forest_named_expenditure_geotagged_record_ends_FY2017_18", "district_assigned_by", "filter_in_use", "layer_built_utc"]
exp_line = re.search(r"lines\.push\(\[(.*?)\]\.map\(q\)", page.split("<script>")[-1], re.S)
exp_vals = [x.strip() for x in re.sub(r"\s+", " ", exp_line.group(1)).split(", ")] if exp_line else []
EXP_SRC = ["d", "f[F.id]", "f[F.name]", "DV.t.kind[+D.out.charAt(i)]", "D.out.charAt(i)", "w.label", '"2025"', "dvTierLabel(cell)", "cell.def", "order", "dvOrderChanged() ? DV.t.order_changed : DV.t.order_default", "dvWithin()",
           "plain(DV.sd[i])", "plain(L.d[i])", "plain(DV.so[i])", "plain(L.o[i])", "plain(DV.low[i])", "plain(L.l[i])", "plain(DV.sf[i])", "plain(L.f[i])", "plain(L.s[i])", "dvShare(i)", "DV.standing_min", "DV.loss_min",
           'DV.near.charAt(i) === "1" ? "yes" : "no"', "dvCorro(i)", '"2017-2023"', "f[F.st]", "f[F.fn]", "dvCheck(i)",
           'dvFilterLabel() + (state.st !== "0" ? (state.keepOut ? "; outside-village units kept" : "; outside-village units left out") : "")', "DV.built"]
check("the export has thirty-two columns, these names in this order, and the page's script fills them with these thirty-two expressions in this order, one for one. The development index of 2011 is not among them, by name or by the "
      "field that holds it, though the list on the page still shows it; the forest at the start of the window and the share are, after the forest loss of the window; and the column that says what orders the units within a tier is "
      "filled with the order in use. (This reads the page's text; that the file a browser writes has each value under its name is the browser exercise's to show.)",
      DV["t"]["export_cols"] == EXPORT and len(EXPORT) == len(EXP_SRC) == 32 and exp_vals == EXP_SRC and DV["built"] == REC["run_utc"] and "development_index_2011" not in EXPORT and not any("adi" in x.lower() for x in exp_vals)
      and "Development index 2011" in DV["t"]["cols"] and EXPORT.index("forest_at_window_start_ha") == EXPORT.index("forest_loss_in_window_ha") + 1 and EXPORT.index("forest_loss_share_pct") == EXPORT.index("forest_at_window_start_ha") + 1
      and REC["decision_view"]["export_columns"] == len(EXPORT)
      and 'function dvShare(i) { var p = DV.loss[state.window].p[i]; return p === "" ? DV.t.no_share : p; }' in dv_bare,
      f"{len(DV['t']['export_cols'])} columns, {len(exp_vals)} expressions; built {DV['built']}" + ("" if exp_vals == EXP_SRC else f"; the page fills them with {exp_vals}"))
why_rows_src = re.search(r"rows = \[\[t\.why_rows\[0\], DV\.sd\[i\], L\.d\[i\]\], \[t\.why_rows\[1\], DV\.so\[i\], L\.o\[i\]\], \[t\.why_rows\[2\], DV\.low\[i\], L\.l\[i\]\]\];", page)
check("in every unit's block the three rows are labelled dense, open and 10 % or less in that order and filled with standing dense, standing open and the land of the lowest band; the heads read canopy in 2000, standing now, lost in the window",
      DV["t"]["why_rows"][0] == "Dense: above 30 %" and DV["t"]["why_rows"][1] == "Open: 10 to 30 %" and DV["t"]["why_rows"][2].startswith("10 % or less") and "nothing is taken off it" in DV["t"]["why_rows"][2]
      and DV["t"]["why_cols"] == ["Canopy in 2000", "Standing now", "Lost in {window}"] and why_rows_src is not None)

# ---- the optional online overlay, and what the two core files still do not do ---------------------------------------------------------------
cfg = ROOT / "scripts/layer_overlay.json"
ov = ROOT / "60_layer/overlay.js"
own = page.split("<script>")[-1]
part = own[own.index("the decision view (added 8 Oct 2026) ---"):own.index("// ---- start:")]
if cfg.is_file():
    c = json.loads(cfg.read_text(encoding="utf-8"))
    js = ov.read_text(encoding="utf-8") if ov.is_file() else ""
    check("the overlay's file names the registered endpoint and no other address, and the registration says where it is documented, its terms and both points of them that are unresolved, its version and its attribution",
          ov.is_file() and json.dumps(c["url_template"]) in js and len(re.findall(r"https?://", js)) == len(re.findall(r"https?://", json.dumps(c["url_template"]) + json.dumps(c["attribution"])))
          and all(c.get(k) for k in ("documented_at", "terms_url", "terms_say", "terms_unresolved", "attribution_requirements_page", "provider_cautions", "data_version", "attribution", "verified_utc"))
          and "(1)" in c["terms_unresolved"] and "(2)" in c["terms_unresolved"], c["url_template"])
    check("the overlay is labelled with the version its tiles carry" + ("" if "v1.13" in str(c["data_version"]) else ", and says its pixels may disagree with the unit tables, which are built from v1.13"),
          str(c["data_version"]) in DV["overlay"]["version"] and ("v1.13" in str(c["data_version"]).lower() or "may disagree" in DV["overlay"]["version"]), DV["overlay"]["version"])
    check("the overlay's tiles are asked for with the years of the chosen window, and its label names that window; the version is pinned in the address, never 'latest'; the whole credit is in the note drawn on the map",
          "start_year=" in js and "end_year=" in js and "{window}" in DV["overlay"]["on"] and "{window}" in DV["overlay"]["legend"] and c["attribution"] in DV["overlay"]["legend"] and DV["overlay"]["attribution"] == c["attribution"]
          and all(len(w.get("years", [])) == 2 and f"{w['years'][0]}-{w['years'][1]}" == w["label"] for w in DV["windows"]) and "/latest/" not in c["url_template"] and "/v1.13/" in c["url_template"])
    check("beside its switch the overlay says that ticking it sends the network address, the place viewed and the years of the window to the provider, and that nothing else on the map asks the network for anything",
          "network address" in DV["overlay"]["note"] and "years of the window" in DV["overlay"]["note"] and "leave this machine" in DV["overlay"]["note"] and "Nothing else on this map asks the network" in DV["overlay"]["note"])
    check("the overlay has words for tiles that stop arriving - some missing, and the connection lost - and the page uses both", "not a sign of no loss" in DV["overlay"]["partial"] and "took itself off" in DV["overlay"]["lost"]
          and "DV.overlay.partial" in part and "DV.overlay.lost" in part)
else:
    check("no endpoint is registered, so there is no overlay file and the control says the overlay is not available", not ov.exists() and DV["overlay"]["available"] == 0 and "not available" in DV["overlay"]["unavailable"])
tag = own[own.rindex("<input", 0, own.index('id="c_overlay"')):]
tag = tag[:tag.index('"> "')]
code = re.sub(r"(?m)^\s*//.*$", "", own)                         # the script without its whole-line comments, one of which names the function
calls = re.findall(r"dvOverlay\s*\(([^)]*)\)", code.replace("function dvOverlay(on)", ""))
aliases = re.findall(r"\bdvOverlay\b(?!\s*\()", code)
check("the overlay is off unless ticked: its box is written without 'checked', the page only ever unticks it, and - in the whole of the page's script - the function that turns it on is called from the box's own change, from a change of "
      "window while it is on, and to turn it off, is given no other name, and draws nothing unless the box is ticked and the decision view is on",
      "checked" not in tag and set(re.findall(r'\$\("c_overlay"\)\.checked\s*=\s*(\w+)', own)) <= {"false"} and sorted(calls) == sorted(["t.checked", '"again"', "false"]) and not aliases
      and 'if (state.layer !== "decision" || !$("c_overlay").checked)' in own, f"calls: {calls}; other mentions: {len(aliases)}")
check("the page makes one script element and gives it one address, overlay.js, in the handler of that tick; no other file is named anywhere in the page",
      len(re.findall(r"createElement\(\s*['\"]script['\"]\s*\)", own)) == 1 and len(re.findall(r"\.src\s*=", own)) == 1 and not re.search(r"setAttribute\(\s*['\"]src['\"]", own) and own.count('s.src = "overlay.js"') == 1
      and "overlay.js" not in page.replace(own, "").replace("overlay.js, loaded only on that tick", "").replace("overlay.js beside it", ""))
HANDLERS = ('ovLayer.on("tileload", function () { ovSeen.ok++; ovSeen.run = 0; }); '
            'ovLayer.on("tileerror", function () { ovSeen.bad++; ovSeen.run++; if (ovSeen.ok && ovSeen.run >= 8) { dvOverlayOff(DV.overlay.lost); } else if (state.overlay) { dvOverlayMsg(dvOverlayOn()); showLegend(); } }); '
            'ovLayer.on("load", function () { var mine = this; setTimeout(function () { if (state.overlay && ovLayer === mine && !ovSeen.ok && ovSeen.bad) { dvOverlayOff(DV.overlay.failed); } }, 0); });')
check("the overlay's three handlers read, whole and with their comments left out, exactly as written in this check: a tile that arrives is counted and ends a run of failures; a failed tile is said at once, beside the box and on the map, "
      "and after eight in a row with some arrived the overlay takes itself off as lost; when every tile asked for has arrived or failed and none arrived, it takes itself off as unreachable - on a timer, after the map library has "
      "finished with its own event. Nothing else listens to the overlay's tiles, and its note is in the legend whether the legend is shown or hidden. (This reads the page's text; that the page behaves so is the browser exercise's to show.)",
      HANDLERS in bare(own) and bare(own).count("ovLayer.on(") == 3 and 'if (!state.legend) { $("legend").innerHTML = h + (state.overlay ? dvOverlayNote() : ""); return; }' in bare(own) and "if (state.overlay) { h += dvOverlayNote(); }" in bare(own) and
      "(ovSeen.bad ? DV.overlay.partial" in own and own.count("(ovSeen.bad ? DV.overlay.partial") == 2 and 'ovLayer.on("load"' in own and "ovSeen.ok && ovSeen.run >= 8" in own
      and "setTimeout(function () { if (state.overlay && ovLayer === mine && !ovSeen.ok && ovSeen.bad) { dvOverlayOff(DV.overlay.failed); } }, 0);" in own
      and not re.search(r'ovLayer\.on\("load", function \(\) \{[^\n]*\n\s*if \(', own))
check("index.html and data.js themselves still hold no address on the network in the decision view's part: every word of it is local", "http://" not in json.dumps(DV) and "https://" not in json.dumps(DV) and "http" not in part)
strings = all(isinstance(x, str) for k in ("sd", "so", "sf", "low") for x in DV[k]) and all(isinstance(x, str) for w in WIN for k in "doflsp" for x in DV["loss"][w][k])
check("every hectare and every share of the decision view reaches the page as text, and the page's part for the view has none of parseFloat, Number(, toFixed or Math., and puts no sign or operator on a hectare: it looks figures up and joins them",
      strings and not re.search(r"parseFloat|Number\(|toFixed|Math\.", part) and not re.search(r"[-+*/]\s*(?:DV\.(?:sd|so|sf|low)|L\.[doflsp])\[", part) and not re.search(r"(?:DV\.(?:sd|so|sf|low)|L\.[doflsp])\[[^\]]+\]\s*[-*/]", part))
check("the words poverty and shrid are nowhere in the decision view: no SHRUG-derived column is named in it", "poverty" not in json.dumps(DV).lower() and "shrid" not in json.dumps(DV).lower())
check("the words composite, weighted and 'score out of' are nowhere in the decision view", not re.search(r"composite|weighted|score out of", json.dumps(DV).lower()))
check("the layer's run record describes the decision view that is in the data", REC["decision_view"]["units_per_cell"] == {w: {c: sum(1 for u in ids if T[u][f"cell_{w}"] == c) for c in cells} for w in WIN}
      and REC["decision_view"]["thresholds"] == {"standing_min_ha": float(smin), "loss_min_ha": float(lmin), "status": P["thresholds"]["status"]})
print(f"\n{sum(results)} of {len(results)} checks passed; n = {n:,} units, 4 windows, 6 cells, {len(names)} districts")
sys.exit(0 if all(results) else 1)
