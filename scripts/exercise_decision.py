"""Exercises the DECISION VIEW of the demo layer in a browser, as a person would, and compares what it shows with the
decision table (55_decision/condition_by_unit.csv) and the stage tables behind it.

    python scripts/exercise_decision.py chrome|webkit [folder for screenshots]

These are the NEW checks that came with the decision view (8 Oct 2026). scripts/exercise_layer.py is left exactly as it
was and still has to pass by itself; this script only borrows its two browser adapters and adds nothing to it.

The layer is opened from disk (file://), on the build that is in 60_layer/.
Part A works every new control - the decision view's switch, the four windows, the district the units are ranked in, the
order within a tier (by hectares lost, or by share lost: added with the owner's rulings of 9 October 2026), the order of
tiers (three of its arrows, and the way back), the Scheduled Tribe filter and its box for the outside-village units, a
row of the list, the legend, the address, two window sizes, and going back to an ordinary layer - and after each action
reads what the page then shows and holds it against the tables.
Part B opens a sample of units by clicking them ON THE MAP - every one of the six cells in at least two windows, both
kinds of unit, units near the dense/open boundary, every one of the eleven kinds of corroboration badge and every kind of
district check - and compares every line of the block "why this tier" with the tables. A click that opens nothing, or
opens a unit that is neither the one aimed at nor one touching it, FAILS; a click that opens a touching neighbour is
counted apart and the neighbour is the unit compared. What the lines are compared with: the hectares, the cell, the order
and the badge are read from 55_decision/condition_by_unit.csv (itself rebuilt independently, and re-added from stage 1 by
verify_decision.py) and printed here by the map's own rule; Scheduled Tribe share, the index and spending from stages 2 and 3.
Part C is the export: two lists downloaded - one under a changed tier order and a filter, ordered by hectares lost; one
under another window with the provisional order and no filter, ordered by share lost - and every field of every row
checked under the name of its column: thirty-two columns, the forest at the start of the window and the share among
them, the development index of 2011 not.
Part D is the optional online overlay: it must be out of reach outside the decision view, off unless ticked, ask for
nothing until then, draw tiles when there is a connection, follow the window, switch itself off when the view is left,
say so beside the box and on the map as soon as one tile fails, and step aside cleanly when there is no connection, when
none of its tiles can be had, when they stop arriving, and when its file is missing.
Script errors of the page are read and must be none at the end of every part and before every reload, the steps in
which the browser is made to fail requests included.

chrome: a separate, headless Chrome with an empty profile, driven with real mouse and keyboard events; the exported file
        is saved by the browser and read back from disk; "no connection" is the browser's own offline mode.
webkit: a WKWebView off the screen - the engine of Safari - where events are dispatched inside the page. There the
        exported text is read from the page (the view has nowhere to save a file) and "no connection" cannot be set, so
        that half of part D is Chrome's alone.
In both, a native list (the district to rank in, the filter) is set through its change event: a native pop-up cannot be
clicked in a window that is not on a screen.

Output: 60_layer/exercise_decision_<browser>.json - every action with what happened, every unit with its comparison, the
export's check, the sha256 of the files opened and of every table read, and the UTC time. It exits 1 unless everything held.
"""
import csv, hashlib, io, json, shutil, sys, tempfile, time
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BROWSER = sys.argv[1] if len(sys.argv) > 1 else "chrome"
if BROWSER not in ("chrome", "webkit"):
    sys.exit(__doc__)
SHOTS = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(tempfile.mkdtemp(prefix="ictd_decision_shots_"))
sys.path.insert(0, str(HERE))
sys.argv = [sys.argv[0], BROWSER, str(SHOTS)]                 # exercise_layer reads these when imported; importing it opens no browser
import exercise_layer as X                                     # its two adapters, its way of finding a unit on the map, its tables

import numpy as np
import pandas as pd

URL = "file://" + str(ROOT / "60_layer" / "index.html")
WIN = {"2018_2025": "2018-2025", "2001_2025": "2001-2025", "2017_2023": "2017-2023", "2021_2025": "2021-2025"}
steps = []


def say(control, did, happened, ok):
    steps.append({"control": control, "did": did, "happened": happened, "ok": bool(ok)})
    print(("PASS  " if ok else "FAIL  ") + f"[{control}] {did} -> {happened}", flush=True)


def shown(x):
    return f"{float(Decimal(str(x))):,.2f}"                    # the rule of every other hectare on the map


# ---- the tables, read here ----------------------------------------------------------------------------------------------------------
with open(X.read("55_decision/condition_by_unit.csv"), newline="", encoding="utf-8") as fh:
    T = {r["unit_id"]: r for r in csv.DictReader(fh)}
with open(X.read("55_decision/tiers.csv"), newline="", encoding="utf-8") as fh:
    TIERS = [r for r in csv.DictReader(fh)]
with open(X.read("55_decision/work_types.csv"), newline="", encoding="utf-8") as fh:
    WORK = {r["cell"]: r["work_type_field"] for r in csv.DictReader(fh)}
PROV = json.load(open(X.read("55_decision/decision.provenance.json")))
NAME = {c: v["name"] for c, v in PROV["definitions"]["cells"].items()}
STANDING_IS = "the forest of 2000 with no loss recorded since; not a measure of tree cover today"       # the owner's wording of 9 October 2026, in place of "a lower bound"
RESTS = {c: v["what_the_name_rests_on"] for c, v in PROV["definitions"]["cells"].items()}
ROW = {c: v["standing_row"] for c, v in PROV["definitions"]["cells"].items()}
COL = {c: v["loss_column"] for c, v in PROV["definitions"]["cells"].items()}
ORDER0 = [r["cell"] for r in TIERS if r["tier"] != ""]
WHY = {r["cell"]: r["why_this_place_in_the_order"] for r in TIERS}
UNRANKED = "little_none"
SMIN, LMIN = f"{PROV['thresholds']['standing_min_ha']:g} ha", f"{PROV['thresholds']['loss_min_ha']:g} ha"
IDS = sorted(T)
OUT = {u: T[u]["outside_village"] == "1" for u in IDS}
ROWW = {"mostly_dense": "mostly dense", "mostly_open": "mostly open", "little_or_none": "little or none"}
CORRO = {"both": "Both measures flag this unit", "hansen_only": "Only Hansen flags it (clearance)", "corestack_only": "Only CoRE Stack flags it (degradation)", "neither": "Neither measure flags it"}
CHECK = {"name_on_the_polygon_not_contradicted": "the name on its boundary polygon; none of the district checks' flags is raised", "moved_off_the_name": "moved off the name on its polygon: two checks contradicted the name and agreed with each other",
         "polygon_has_no_name": "its polygon names no district: taken from the panchayat polygons under it or the villages round it", "ambiguous": "ambiguous: two districts within 5 points of each other",
         "flagged_one_check_contradicts": "flagged: one check contradicts the district it carries", "no_check_possible": "no check possible: a name, and nothing to check it against"}
WITHIN = {"ha": "Within a tier, largest first: by forest loss in the window where the cell has loss, by standing hectares of the cell's band where it has none.",
          "share": "Within a tier, largest first: by forest loss in the window as a share of the forest at the start of the window where the cell has loss (units with no share after the others, by hectares lost), "
                   "by standing hectares of the cell's band where it has none."}       # the two orders within a tier, as the head of the list and the export name them
errors_seen = []                                                # script errors of the page, with where they were read: there must be none


def no_errors(c, where):
    """The page's script errors so far: read, kept if any, and reported. Called at the end of every part and before every reload."""
    e = list(c.errors or [])
    if e:
        errors_seen.append({"read": where, "errors": e})
        print(f"SCRIPT ERROR(S) read {where}: {e}", flush=True)
    return not e


def corro(u):
    r = T[u]
    if r["corroboration_basis"] == "headline":
        return CORRO[r["corroboration"]]
    if r["corroboration_basis"] == "east_coast_every_unit_kept":
        return CORRO[r["corroboration"]] + " - East Coast zone model: the placebo failed there, so corroboration is unreliable"
    return {"below_floor": "Not compared: under 100 ha of land with canopy above 10 % in 2000, the agreement test's floor",
            "below_floor_no_corestack_coverage": "Not compared: under 100 ha of land with canopy above 10 % in 2000, the agreement test's floor; and CoRE Stack gives no class on such land here",
            "corestack_covers_under_floor": "Not compared: CoRE Stack gives a class on under 100 ha of this unit's land with canopy above 10 % in 2000, the agreement test's floor"}[r["corroboration_basis"]]


def share_text(u, w):
    """The share as the list and the export show it: the table's figure, or the words for a unit that has none."""
    return T[u][f"forest_loss_share_pct_{w}"] or f"no share: under {SMIN} of forest at the start of the window"


def tier_label(cell, order):
    return f"Tier {order.index(cell) + 1}: {NAME[cell]}" if cell in order else f"Not ranked: {NAME[cell]}"


def order_words(order):
    return "the provisional order" if order == ORDER0 else "an order changed by the user of this page (" + "; ".join(f"{i + 1} {NAME[c]}" for i, c in enumerate(order)) + ")"


def ranked(district, w, order, st="0", keep_out=True, within="ha"):
    """The units the list should hold, in order, and what the filter left out - from the decision table and the census table. within: the order inside a tier, by hectares lost or by share lost."""
    col = f"order_in_district_cell_{w}" if within == "ha" else f"order_in_district_cell_by_share_{w}"
    keep = {"0": None, "18": 18.0, "33": 33.0, "50": 50.0}[st]
    rows, dropped, out_kept, out_dropped = [], 0, 0, 0
    for cell in order:
        mine = sorted((u for u in IDS if T[u]["district"] == district and T[u][f"cell_{w}"] == cell), key=lambda u: int(T[u][col]))
        for u in mine:
            if keep is not None:
                if OUT[u]:
                    if keep_out:
                        out_kept += 1
                    else:
                        out_dropped += 1
                        continue
                else:
                    s = X.N_.loc[u, "st_share"]
                    pct = None if pd.isna(s) else round(100 * float(s), 2)
                    if pct is None or (pct < keep if st != "50" else pct <= keep):
                        dropped += 1
                        continue
            rows.append(u)
    return rows, dropped, out_kept, out_dropped


def why_expected(u, w, order):
    """Every line the block 'why this tier' should carry for one unit, from the tables."""
    r = T[u]
    cell = r[f"cell_{w}"]
    little = ROW[cell] == "little_or_none"
    e = {"chip": tier_label(cell, order),
         "window": f"Window: forest loss counted over {WIN[w]} ({PROV['definitions']['windows'][w]['is']}). Standing forest is always through 2025.",
         "hectares": [shown(r["standing_dense_ha"]) + " ha", shown(r[f"loss_dense_ha_{w}"]) + " ha", shown(r["standing_open_ha"]) + " ha", shown(r[f"loss_open_ha_{w}"]) + " ha", shown(r["low_2000_ha"]) + " ha", shown(r[f"loss_low_ha_{w}"]) + " ha"],
         "standing": (f"Standing forest {shown(r['standing_forest_ha'])} ha, under the {SMIN} below which a unit has little or none." if little else
                      f"Standing forest {shown(r['standing_forest_ha'])} ha, at least the {SMIN} below which a unit has little or none; {ROWW[ROW[cell]]}, because standing dense is "
                      + ("at least as large as" if ROW[cell] == "mostly_dense" else "smaller than") + " standing open."),
         "loss": f"Forest loss in the window {shown(r[f'forest_loss_ha_{w}'])} ha (dense and open added), " + (f"at least the {LMIN} that counts as some loss." if COL[cell] == "some" else f"under the {LMIN} that counts as some loss."),
         "share": (f"As a share: the unit had {shown(r[f'forest_at_window_start_ha_{w}'])} ha of forest at the start of {WIN[w]}, and the forest loss of the window is {r[f'forest_loss_share_pct_{w}']} % of it. "
                   "The share stands beside the cell and decides nothing." if r[f"forest_loss_share_pct_{w}"] else
                   f"As a share: none is given. The unit had {shown(r[f'forest_at_window_start_ha_{w}'])} ha of forest at the start of {WIN[w]}, under the {SMIN} below which a share means nothing."),
         "near": r["near_dense_open_boundary"] == "1", "grid": NAME[cell],
         "cell": f"So the cell is: {NAME[cell]}. {RESTS[cell]} " + ("It is on the map and outside the ranked list." if cell not in order else
                 f"Its place under the tier order in use ({order_words(order)}): {tier_label(cell, order)}. "
                 + (f"In the provisional order this cell is {tier_label(cell, ORDER0)}; the line recorded for it there: " if order != ORDER0 else "") + WHY[cell]),
         "corro": "Corroboration, 2017-2023 (whatever window is chosen): " + corro(u), "work": "Work types: " + WORK[cell],
         "gov": T[u]["governance_prompt"] if OUT[u] else None,
         "district": ("District assigned by: " + "; ".join(CHECK[p] for p in r["district_check"].split("; "))) if OUT[u] else None}
    return e


READ_WHY = """(function(){
  var b = document.getElementById('dvwhy'); if (!b) return null;
  var p = function(k){ var e = b.querySelector('[data-w=' + k + ']'); return e ? e.textContent : null; };
  var t = b.querySelector('table.why:not(.grid6)'), g = b.querySelector('table.grid6 td.in'), gov = b.querySelector('.gov');
  return {chip: b.querySelector('.tierchip').textContent, window: p('window'), hectares: Array.from(t.querySelectorAll('tr')).slice(1).reduce(function(a, tr){ a.push(tr.cells[1].textContent); a.push(tr.cells[2].textContent); return a; }, []),
          head: Array.from(t.querySelectorAll('th')).map(function(e){return e.textContent;}), rowlabels: Array.from(t.querySelectorAll('tr')).slice(1).map(function(tr){return tr.cells[0].textContent;}), standing: p('standing'), loss: p('loss'), share: p('share'), near: !!b.querySelector('[data-w=near]'), grid: g ? g.textContent : null,
          highlighted: b.querySelectorAll('table.grid6 td.in').length, cell: p('cell'), corro: p('corro'), work: p('work'), gov: gov ? gov.textContent : null, district: p('district'),
          last: document.getElementById('info').lastElementChild === b, gridcol: (function(){var c=b.querySelector('table.grid6 td.in'); return c ? b.querySelectorAll('table.grid6 th')[c.cellIndex].textContent : null;})(),
          unit: (function(){var r=document.querySelector('#info table.kv tr'); return r?r.cells[1].textContent:null;})()};
})()"""


def why_compare(c, u, w, order):
    got = c.js(READ_WHY)
    if not got:
        return {"unit": u, "aimed_at": u, "window": w, "cell": T[u][f"cell_{w}"], "type": "outside_village" if OUT[u] else "lgd_panchayat", "equal": 0, "of": 19, "bad": ["no block 'why this tier' in the panel"], "badge": "", "block_is_last_in_the_panel": None}
    want = why_expected(got["unit"], w, order)
    bad = []
    for k in ("chip", "window", "standing", "loss", "share", "near", "grid", "cell", "corro", "work", "gov", "district"):
        a, b = got[k], want[k]
        if (X.norm(a) if isinstance(a, str) else a) != (X.norm(b) if isinstance(b, str) else b):
            bad.append((k, a, b))
    for j, (a, b) in enumerate(zip(got["hectares"], want["hectares"])):
        if X.norm(a) != b:
            bad.append((f"hectares[{j}]", a, b))
    col_head = "Some forest loss in the window" if COL[T[got["unit"]][f"cell_{w}"]] == "some" else "No forest loss in the window"
    labels_ok = got["head"] == ["Canopy in 2000", "Standing now", f"Lost in {WIN[w]}"] and len(got["rowlabels"]) == 3 and got["rowlabels"][0] == "Dense: above 30 %" and got["rowlabels"][1] == "Open: 10 to 30 %" \
        and got["rowlabels"][2].startswith("10 % or less: not counted as forest")
    if len(got["hectares"]) != 6 or got["highlighted"] != 1 or not labels_ok or got["gridcol"] != col_head:
        bad.append(("table", f"{len(got['hectares'])} figures, {got['highlighted']} cell outlined under '{got['gridcol']}', heads {got['head']}, rows {got['rowlabels']}",
                    f"6 figures, 1 cell outlined under '{col_head}', the heads 'Canopy in 2000', 'Standing now', 'Lost in {WIN[w]}' and the rows dense, open, 10 % or less in that order"))
    of = 12 + 6 + 1
    return {"unit": got["unit"], "aimed_at": u, "window": w, "cell": T[got["unit"]][f"cell_{w}"], "type": "outside_village" if OUT[got["unit"]] else "lgd_panchayat", "equal": of - len(bad), "of": of, "bad": bad,
            "badge": T[got["unit"]]["corroboration"] + " / " + T[got["unit"]]["corroboration_basis"], "block_is_last_in_the_panel": got["last"]}


def dstate(c):
    return c.js("""(function(){var q=function(n){var e=document.querySelector('input[name='+n+']:checked'); return e?e.value:null;};
      var rk=document.getElementById('ranked'), rows=Array.from(document.querySelectorAll('table.rk tr.r'));
      return {layer:(document.getElementById('r_decision').checked ? 'decision' : q('layer')), both_checked: !!(document.getElementById('r_decision').checked && q('layer')), more: getComputedStyle(document.getElementById('dv_more')).display,
              keep_disabled: (document.getElementById('c_keep_out')||{}).disabled, keep_label: ((document.getElementById('c_keep_out')||{}).parentElement||{}).textContent||'', layer_radios: document.querySelectorAll('input[name=layer]').length, window:q('dwindow'), wrap:document.getElementById('mapwrap').className, hash:location.hash, legend_title:(document.querySelector('#legend .t')||{}).textContent,
              legend:Array.from(document.querySelectorAll('#legend .lr')).map(function(e){return e.textContent.trim();}), legend_note:Array.from(document.querySelectorAll('#legend p.note')).map(function(e){return e.textContent;}).join(' | '),
              ranked_shown: getComputedStyle(rk).display !== 'none', ranked_len: rk.innerHTML.length, msg:(document.getElementById('rank_msg')||{}).textContent||'', head:(document.getElementById('rank_head')||{}).textContent||'',
              filter:(document.getElementById('rank_filter')||{}).textContent||'', unranked:(document.getElementById('rank_unranked')||{}).textContent||'',
              rows: rows.map(function(tr){return window.ICTD_LAYER.id[+tr.getAttribute('data-u')];}), first: rows.length ? Array.from(rows[0].cells).map(function(td){return td.textContent;}) : [],
              cols: Array.from(document.querySelectorAll('table.rk th')).map(function(e){return e.textContent;}), export_disabled: (document.getElementById('b_export')||{}).disabled,
              rank: (document.getElementById('rank_district')||{}).value, st:(document.getElementById('rank_st')||{}).value, within:(document.getElementById('rank_within')||{}).value, keep:(document.getElementById('c_keep_out')||{}).checked,
              tiers: Array.from(document.querySelectorAll('#dv_tiers div')).map(function(e){return e.textContent.trim();}), overlay: document.getElementById('c_overlay').checked, overlay_disabled: document.getElementById('c_overlay').disabled,
              overlay_msg: document.getElementById('overlaymsg').textContent, unit:(function(){var r=document.querySelector('#info table.kv tr'); return r?r.cells[1].textContent:null;})(),
              drawn:(function(){var n=0; ICTD_MAP.eachLayer(function(l){ if(l._u!==undefined){n++;} }); return n;})(), page_w: document.documentElement.scrollWidth,
              map_w: Math.round(document.getElementById('map').getBoundingClientRect().width), map_h: Math.round(document.getElementById('map').getBoundingClientRect().height),
              ranked_h: Math.round(rk.getBoundingClientRect().height), legend_h: Math.round(document.getElementById('legend').getBoundingClientRect().height)};})()""")


def choose(c, selector, value):
    """A native list cannot be opened in a window that is not on a screen: set it and send the change event its handler listens for."""
    c.js(f"(function(){{var e=document.querySelector({json.dumps(selector)}); e.value={json.dumps(value)}; e.dispatchEvent(new Event('change', {{bubbles:true}})); return 0;}})()")
    time.sleep(1.0)


def legend_expected(w, order, district=None):
    out = []
    for cell in order + [UNRANKED]:
        n_all = sum(1 for u in IDS if T[u][f"cell_{w}"] == cell)
        n_d = sum(1 for u in IDS if T[u][f"cell_{w}"] == cell and T[u]["district"] == district) if district else None
        out.append(f"{tier_label(cell, order)} ({n_all:,} units" + (f"; {n_d:,} in {district}" if district else "") + ")")
    return out


def export_expected(d, w, order, st, keep, built, within="ha"):
    """Every field of every row the exported list should hold, from the tables."""
    rows, _, _, _ = ranked(d, w, order, st, keep, within)
    order_text = "; ".join(f"{i + 1} {NAME[c_]}" for i, c_ in enumerate(order)) + f"; not ranked: {NAME[UNRANKED]}"
    rowdef = {"mostly_dense": f"Forest standing now is mostly dense: {SMIN} or more of standing forest, and standing dense at least as large as standing open.",
              "mostly_open": f"Forest standing now is mostly open: {SMIN} or more of standing forest, and standing open larger than standing dense.", "little_or_none": f"Forest standing now is little or none: under {SMIN} of standing forest."}
    coldef = {"some": f"Forest loss in the window is some: {LMIN} or more.", "none": f"Forest loss in the window is none: under {LMIN}."}
    filt = {"0": "No filter", "18": "Scheduled Tribe share 18 % or more", "33": "Scheduled Tribe share above 33 %", "50": "Scheduled Tribe share more than 50 %"}[st] + ("" if st == "0" else "; outside-village units kept" if keep else "; outside-village units left out")
    plain = lambda v: shown(v).replace(",", "")
    out = []
    for u in rows:
        r_, cell, f = T[u], T[u][f"cell_{w}"], X.expected(u)
        fnv = "not recorded" if pd.isna(X.AL.loc[u, "expenditure_forest_named_worktype"]) else f"Rs {X.AL.loc[u, 'expenditure_forest_named_worktype'] / 1e5:,.2f} lakh"
        stv = X.NC if OUT[u] else ("not defined: no resident population" if pd.isna(X.N_.loc[u, "st_share"]) else f"{100 * X.N_.loc[u, 'st_share']:,.2f} %")
        out.append([d, u, f[0][1], "Outside-village unit" if OUT[u] else "LGD panchayat unit", "1" if OUT[u] else "0", WIN[w], "2025", tier_label(cell, order), rowdef[ROW[cell]] + " " + coldef[COL[cell]], order_text,
                    "the provisional order" if order == ORDER0 else "an order changed by the user of this page", WITHIN[within], plain(r_["standing_dense_ha"]), plain(r_[f"loss_dense_ha_{w}"]), plain(r_["standing_open_ha"]), plain(r_[f"loss_open_ha_{w}"]),
                    plain(r_["low_2000_ha"]), plain(r_[f"loss_low_ha_{w}"]), plain(r_["standing_forest_ha"]), plain(r_[f"forest_loss_ha_{w}"]), plain(r_[f"forest_at_window_start_ha_{w}"]), share_text(u, w), SMIN, LMIN, "yes" if r_["near_dense_open_boundary"] == "1" else "no", corro(u), "2017-2023", stv, fnv,
                    "; ".join(CHECK[p] for p in r_["district_check"].split("; ")) if OUT[u] else "", filt, built])
    return rows, out, order_text, filt


EXPORT = ["district", "unit_id", "unit_name", "unit_type", "outside_village", "window_of_forest_loss", "standing_forest_is_through", "tier_label", "tier_definition", "tier_order_in_use", "tier_order_is", "order_within_a_tier",
          "standing_dense_ha", "lost_from_dense_in_window_ha", "standing_open_ha", "lost_from_open_in_window_ha", "land_with_10pct_canopy_or_less_in_2000_ha", "lost_on_that_land_in_window_ha_reported_only", "standing_forest_ha",
          "forest_loss_in_window_ha", "forest_at_window_start_ha", "forest_loss_share_pct", "standing_minimum", "loss_minimum", "close_call_dense_or_open", "corroboration", "corroboration_window", "scheduled_tribe_share",
          "forest_named_expenditure_geotagged_record_ends_FY2017_18", "district_assigned_by", "filter_in_use", "layer_built_utc"]       # the columns, in order, as export_expected() fills them: each value is compared under its own name


def export_and_check(c, downloads, cols, d, w, order, st, keep, built, what, within="ha"):
    """Press the export button, take the file the browser saved (Chrome) or the text the page made (WebKit), and compare every field of every row."""
    before = {p.name for p in downloads.iterdir()} if BROWSER == "chrome" else set()
    c.js("window.ICTD_EXPORT = null")
    x, y = c.click_on("#b_export"); time.sleep(1.5)
    ex = c.js("window.ICTD_EXPORT")
    on_disk = None
    if BROWSER == "chrome":
        for _ in range(40):
            got = [p for p in downloads.iterdir() if p.suffix == ".csv" and p.name not in before]
            if got:
                on_disk = got[0].read_bytes().decode("utf-8")
                break
            time.sleep(0.25)
    text = on_disk if on_disk is not None else ex["text"]
    table = list(csv.reader(io.StringIO(text)))
    head, body = table[0], table[1:]
    rows, want, order_text, filt = export_expected(d, w, order, st, keep, built, within)
    bad, n_cells = [], 0
    for u, got_, want_ in zip(rows, body, want):
        named = dict(zip(head, got_))                                    # the file's own header names each value
        for col, b in zip(EXPORT, want_):
            n_cells += 1
            if X.norm(named.get(col, "<no such column>")) != X.norm(b):
                bad.append((u, col, named.get(col), b))
    record = {"file": ex["name"], "saved_by_the_browser": on_disk is not None, "saved_file_equals_the_text_the_page_made": (on_disk == ex["text"]) if on_disk is not None else None, "columns": head, "rows": len(body), "rows_expected": len(rows),
              "cells_compared": n_cells, "cells_equal": n_cells - len(bad), "bad": bad[:10], "district": d, "window": WIN[w], "tier_order": order_text, "tier_order_is": "the provisional order" if order == ORDER0 else "an order changed by the user of this page", "filter": filt,
              "order_within_a_tier": WITHIN[within], "development_index_2011_among_the_columns": "development_index_2011" in head, "rows_with_no_share": sum(1 for u in rows if not T[u][f"forest_loss_share_pct_{w}"])}
    changed = order != ORDER0
    say("export", f"{c.clicked} 'Download this list (CSV)' at ({x}, {y}): {what}",
        (f"the browser saved '{ex['name']}' ({len(text):,} characters), the same text the page made; " if on_disk is not None else f"the page made '{ex['name']}' ({len(text):,} characters; read from the page - this view has nowhere to save a file); ")
        + f"{len(body):,} rows x {len(head)} columns; every row carries its district, unit, kind, the window {WIN[w]}, tier label and definition, THE ORDER OF TIERS IN USE and that it was {'changed' if changed else 'the provisional one'}, what orders units within a tier, "
          f"the six hectare figures, the forest at the start of the window and the loss as a share of it, corroboration with its own window, the outside-village flag, the filter and the build time; the development index is not in the file; "
          f"{n_cells - len(bad):,} of {n_cells:,} cells equal the tables" + (f"; WRONG: {bad[:2]}" if bad else ""),
        head == EXPORT == cols and all(len(g) == len(EXPORT) for g in body) and [g[1] for g in body] == rows and len(body) > 0 and not bad and n_cells == len(rows) * len(head) and (on_disk is None or on_disk == ex["text"])
        and WIN[w].replace("-", "_") in ex["name"] and d.replace(" ", "_") in ex["name"] and len(head) == 32 and "development_index_2011" not in head
        and all(g[head.index("order_within_a_tier")] == WITHIN[within] for g in body)
        and all(g[head.index("window_of_forest_loss")] == WIN[w] and g[head.index("tier_order_is")] == record["tier_order_is"] and g[head.index("layer_built_utc")] == built for g in body))
    return record


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    files = {f: hashlib.sha256((ROOT / "60_layer" / f).read_bytes()).hexdigest() for f in ("index.html", "data.js") + (("overlay.js",) if (ROOT / "60_layer/overlay.js").is_file() else ())}
    prov = json.load(open(X.read("60_layer/layer.provenance.json")))
    overlay_cfg = json.load(open(X.read("scripts/layer_overlay.json"))) if (ROOT / "scripts/layer_overlay.json").is_file() else None
    profile = tempfile.mkdtemp(prefix="ictd_chrome_profile_") if BROWSER == "chrome" else None
    downloads = Path(tempfile.mkdtemp(prefix="ictd_decision_export_"))
    c = X.InChrome(profile, port=9335) if BROWSER == "chrome" else X.InWebKit()
    results, exports, overlay_notes, not_actions = [], [], [], 0
    try:
        t = c.open(URL)
        D = c.js("(function(){var D=window.ICTD_LAYER, V=D.decision; return {districts:D.districts.map(function(d){return {name:d.name,bbox:d.bbox};}), cells:V.cells.map(function(x){return [x.id,x.name,x.color];}), tiers:V.tiers, built:V.built, overlay:V.overlay, cols:V.t.export_cols, default_layer:D.default_layer};})()")
        names = [d["name"] for d in D["districts"]]
        color = {cid: col for cid, _, col in D["cells"]}
        s = dstate(c)
        say("page", f"opened {URL} in {c.version}", f"ready in {t} s; files loaded: {c.files()}; the ordinary layer '{s['layer']}' is on, and its {s['layer_radios']} layer buttons are the ones it had; of the decision view only its one switch shows: its windows, "
            f"tiers and overlay box are folded away (display '{s['more']}') until it is chosen; no list is shown; script errors: {c.errors or 'none'}",
            c.files() == ["data.js", "index.html"] and s["layer"] == D["default_layer"] and s["layer_radios"] == 10 and s["more"] == "none" and s["window"] == "2018_2025" and len(s["tiers"]) == 5 and s["wrap"] == "" and not s["ranked_shown"] and not s["overlay"] and not c.errors)

        # ---- A1. the switch ------------------------------------------------------------------------------------------------------------------
        lgd = [u for u in IDS if not OUT[u]]
        watch = max((u for u in lgd if T[u]["cell_2018_2025"] != T[u]["cell_2001_2025"] and float(X.U.loc[u, "area_ha"]) > 3000), key=lambda u: float(X.U.loc[u, "area_ha"]))
        ll, bb = X.point(watch)
        x, y = c.click_on("#r_decision"); time.sleep(1.2)
        c.js(f"(function(){{ ICTD_MAP.fitBounds({json.dumps(bb)}, {{animate:false, padding:[60,60]}}); return 0; }})()"); time.sleep(0.9)
        wx, wy = X.to_screen(c, ll)
        s, px = dstate(c), X.pixel(c, wx, wy)
        want = legend_expected("2018_2025", ORDER0)
        say("decision view", f"{c.clicked} the radio button 'Where is forest work warranted?' at ({x}, {y})",
            f"it became the checked view and no ordinary layer stayed checked beside it; its windows, tiers and overlay box unfolded; the legend reads '{s['legend_title']}' with {len(want)} rows - five tiers and 'Not ranked' - each with the decision table's count; "
            f"the address reads '{s['hash']}'; unit {watch} (cell {T[watch]['cell_2018_2025']}) is drawn {px}, that cell's colour {color[T[watch]['cell_2018_2025']]}; a panel opened under the map saying '{s['msg'][:70]}...'; the export button is off until a district is chosen",
            s["layer"] == "decision" and not s["both_checked"] and s["more"] != "none" and s["wrap"] == "dv" and "2018-2025" in s["legend_title"] and s["legend"][:6] == want and "layer=decision" in s["hash"] and px.lower() == color[T[watch]["cell_2018_2025"]].lower()
            and s["ranked_shown"] and "never across the state" in s["msg"] and "not established" in s["msg"] and s["export_disabled"] and s["drawn"] == len(IDS) and not c.errors)
        c.shot(SHOTS / "A1_decision_on.png")

        # ---- A2. the four windows ---------------------------------------------------------------------------------------------------------------
        for w in ("2001_2025", "2017_2023", "2021_2025", "2018_2025"):
            x, y = c.click_on(f"input[name=dwindow][value='{w}']"); time.sleep(1.0)
            s, px = dstate(c), X.pixel(c, wx, wy)
            want = legend_expected(w, ORDER0)
            say("window", f"{c.clicked} the window '{WIN[w]}' at ({x}, {y})", f"the legend's title names it ('{s['legend_title']}'); its six counts are the decision table's for that window ({want[0]} ...); unit {watch} is now in cell {T[watch][f'cell_{w}']} and is drawn {px} "
                f"({color[T[watch][f'cell_{w}']]}); address '{s['hash']}'",
                s["window"] == w and WIN[w] in s["legend_title"] and s["legend"][:6] == want and px.lower() == color[T[watch][f"cell_{w}"]].lower() and (("window=" + w in s["hash"]) == (w != "2018_2025")))
            c.shot(SHOTS / f"A2_window_{w}.png")

        # ---- A3. the district the units are ranked in -----------------------------------------------------------------------------------------
        n_out_by = {d: sum(1 for u in IDS if OUT[u] and T[u]["district"] == d and T[u]["cell_2018_2025"] != UNRANKED) for d in names}
        chosen = [max(n_out_by, key=n_out_by.get), "Ganjam", min((d for d in names), key=lambda d: sum(1 for u in IDS if T[u]["district"] == d and T[u]["cell_2018_2025"] != UNRANKED))]
        say("ranked list", "did not click the two lists (the district, the filter)", "a native pop-up menu cannot be operated in a window that is not on a screen; each choice below sets the list and sends its change event", True)
        not_actions += 1
        for d in chosen:
            choose(c, "#rank_district", str(names.index(d)))
            s = dstate(c)
            rows, _, _, _ = ranked(d, "2018_2025", ORDER0)
            n_un = sum(1 for u in IDS if T[u]["district"] == d and T[u]["cell_2018_2025"] == UNRANKED)
            inside = c.js(f"ICTD_MAP.getBounds().pad(0.05).contains({json.dumps(D['districts'][names.index(d)]['bbox'])})")
            say("ranked list", f"chose '{d}' in the list 'Rank the units of...'",
                f"the head reads '{s['head'][:150]}...'; {len(s['rows']):,} rows, the same units in the same order as the decision table gives ({len(rows):,}: tier by tier, then by loss or by standing hectares), of which "
                f"{sum(1 for u in rows if OUT[u]):,} outside-village units; the foot says {n_un:,} are 'Not a forest site'; the legend adds each cell's count in {d}; the map moved to the district; address '{s['hash']}'",
                s["rows"] == rows and s["head"].startswith(f"{d}, ranked units: {len(rows)}, tier by tier. {WITHIN['ha']} Forest loss counted over 2018-2025; standing forest through 2025. Tier order: the provisional order.")
                and f"outside the list: {n_un:,}." in s["unranked"] and s["legend"][:6] == legend_expected("2018_2025", ORDER0, d) and inside and "rank=" in s["hash"] and not s["export_disabled"] and len(s["cols"]) == 11
                and "2018-2025" in " ".join(s["cols"]) and "2017-2023" in " ".join(s["cols"]) and "ends FY2017-18" in s["cols"][10] and "share" in s["cols"][6] and s["within"] == "ha" and "within=" not in s["hash"]
                and STANDING_IS in s["unranked"] and "lower bound" not in (s["unranked"] + s["legend_note"]).lower() and STANDING_IS in s["legend_note"] and s["keep_disabled"] and "applies when a filter is on" in s["keep_label"])
        c.shot(SHOTS / "A3_ranked.png")
        # ---- A3b. the second order within a tier: by share lost (added with the rulings of 9 October 2026) ----------------------------------------
        differ = {d_: sum(1 for a_, b_ in zip(ranked(d_, "2018_2025", ORDER0)[0], ranked(d_, "2018_2025", ORDER0, within="share")[0]) if a_ != b_) for d_ in names}
        d_share = max(differ, key=differ.get)                     # the district whose list changes in the most places when it is ordered by share
        choose(c, "#rank_district", str(names.index(d_share)))
        by_ha, by_share = ranked(d_share, "2018_2025", ORDER0)[0], ranked(d_share, "2018_2025", ORDER0, within="share")[0]
        choose(c, "#rank_within", "share")
        s = dstate(c)
        no_loss = [u for u in by_ha if not T[u]["cell_2018_2025"].endswith("_loss")]
        say("order within a tier", f"with {d_share} ranked, set the list 'Within a tier' to 'by share lost'",
            f"the {len(s['rows']):,} rows are in the order the decision table gives by share ({differ[d_share]:,} of them in another place than by hectares lost); the units of the cells with little or no loss recorded "
            f"({len(no_loss):,}) are where they were, ordered by standing hectares; the head now says '{s['head'][s['head'].index('Within a tier'):][:118]}...'; address '{s['hash']}'",
            s["rows"] == by_share and by_share != by_ha and sorted(by_share) == sorted(by_ha) and differ[d_share] > 0 and [u for u in s["rows"] if u in set(no_loss)] == no_loss
            and WITHIN["share"] in s["head"] and WITHIN["ha"] not in s["head"] and "within=share" in s["hash"] and s["within"] == "share"
            and [X.norm(v) for v in s["first"]][6] == X.norm(share_text(s["rows"][0], "2018_2025")))
        c.shot(SHOTS / "A3b_by_share.png")
        choose(c, "#rank_within", "ha")
        s = dstate(c)
        say("order within a tier", "set the list 'Within a tier' back to 'by hectares lost'", f"the rows are in the first order again, the head says so, and the address carries nothing of the order ('{s['hash']}')",
            s["rows"] == by_ha and WITHIN["ha"] in s["head"] and WITHIN["share"] not in s["head"] and "within=" not in s["hash"] and s["within"] == "ha")
        d = chosen[0]                                             # the district with the most outside-village units in a ranked cell: the rest of part A works in it
        choose(c, "#rank_district", str(names.index(d)))
        # the first row, cell by cell
        s = dstate(c)
        u0 = s["rows"][0]
        f0 = X.expected(u0)
        fn = "not recorded" if pd.isna(X.AL.loc[u0, "expenditure_forest_named_worktype"]) else f"Rs {X.AL.loc[u0, 'expenditure_forest_named_worktype'] / 1e5:,.2f} lakh"
        st0 = X.NC if OUT[u0] else ("not defined: no resident population" if pd.isna(X.N_.loc[u0, "st_share"]) else f"{100 * X.N_.loc[u0, 'st_share']:,.2f} %")
        adi0 = X.NC if OUT[u0] else ("no index for this unit's villages" if pd.isna(X.N_.loc[u0, "adi_2011"]) else f"{X.N_.loc[u0, 'adi_2011']:,.2f}")
        want_row = [tier_label(T[u0]["cell_2018_2025"], ORDER0), f"{f0[0][1]} ({u0})", "Outside-village unit" if OUT[u0] else "LGD panchayat unit", shown(T[u0]["standing_dense_ha"]), shown(T[u0]["standing_open_ha"]),
                    shown(T[u0]["forest_loss_ha_2018_2025"]), share_text(u0, "2018_2025"), corro(u0), st0, adi0, fn]
        say("ranked list", f"read the first row of the list for {d}", f"its eleven cells are {s['first']}: the tier as a label and never a bare number, the unit, its kind, standing dense and open, forest loss in the window and that loss as a share of the forest "
            "at the window's start, the corroboration badge with its own window in the column head, "
            "and beside them - not in them - Scheduled Tribe share, the development index and forest-named spending, as the stage tables have them", [X.norm(v) for v in s["first"]] == [X.norm(v) for v in want_row])

        # ---- A4. the order of tiers ------------------------------------------------------------------------------------------------------------
        order = list(ORDER0)
        for k, move in ((0, 1), (3, -1), (4, -1)):
            x, y = c.click_on(f"#dv_tiers button[data-tier='{k}'][data-move='{move}']"); time.sleep(1.0)
            order[k], order[k + move] = order[k + move], order[k]
            s = dstate(c)
            rows, _, _, _ = ranked(d, "2018_2025", order)
            say("tier order", f"{c.clicked} the '{'down' if move > 0 else 'up'}' arrow of tier {k + 1} at ({x}, {y})",
                f"the order became {' > '.join(order)}; the legend, the list ({len(s['rows']):,} rows, re-ordered) and the list's head all follow, and the head now says '{s['head'][s['head'].index('Tier order'):][:60]}...'; address '{s['hash']}'",
                s["rows"] == rows and s["legend"][:6] == legend_expected("2018_2025", order, d) and f"Tier order: {order_words(order)}." in s["head"] and "tiers=" + ".".join(order) in s["hash"]
                and [x_.split(" ", 1)[1] for x_ in s["tiers"]] == [NAME[c_] for c_ in order])
        changed = list(order)
        c.shot(SHOTS / "A4_tiers_changed.png")

        # ---- A5. the Scheduled Tribe filter, and its box for the outside-village units ---------------------------------------------------------
        for st, keep in (("33", True), ("33", False), ("50", False), ("18", True)):
            choose(c, "#rank_st", st)
            if dstate(c)["keep"] != keep:
                c.click_on("#c_keep_out"); time.sleep(0.8)
            s = dstate(c)
            rows, dropped, ok_, od_ = ranked(d, "2018_2025", order, st, keep)
            say("filter", f"set the filter to Scheduled Tribe share '{st} %' with the box 'Keep outside-village units' {'ticked' if keep else 'unticked'}",
                f"{len(s['rows']):,} rows remain, the ones need_by_unit.csv gives ({len(rows):,}); the note reads '{s['filter'][:190]}...'; the order within the list did not change; the box can be used now that a filter is on; address '{s['hash']}'",
                s["rows"] == rows and f"Units left out for a smaller or undefined share: {dropped}." in s["filter"] and not s["keep_disabled"]
                and (f"Outside-village units kept in the list though the filter cannot be applied to them (no census data): {ok_}." in s["filter"] if keep else f"Outside-village units left out with the filter on, for want of census data: {od_}. Tick the box to bring them back." in s["filter"])
                and "it never orders it" in s["filter"] and "most of the forest" not in s["filter"] and f"st={st}" in s["hash"] and (("keepout=0" in s["hash"]) == (not keep)))
        c.shot(SHOTS / "A5_filter.png")

        # ---- A6. a row of the list ----------------------------------------------------------------------------------------------------------------
        s = dstate(c)
        target = s["rows"][min(3, len(s["rows"]) - 1)]
        x, y = c.click_on("table.rk tr.r", min(3, len(s["rows"]) - 1)); time.sleep(1.2)
        s2 = dstate(c)
        r = why_compare(c, target, "2018_2025", order)
        say("ranked list", f"{c.clicked} the row of unit {target} at ({x}, {y})", f"the unit's panel opened ({s2['unit']}), the map went to it, and its block 'why this tier' - right under the unit's name in this view - shows the tier under the changed order and says "
            f"that the reason given is the one for the cell's provisional place ({r['equal']} of {r['of']} lines as the tables give them)",
            s2["unit"] == target and r["equal"] == r["of"] == 19 and not r["block_is_last_in_the_panel"] and f"unit={target}" in s2["hash"])
        ok_a = no_errors(c, "after part A, steps 1 to 6")

        # ---- C. the export: two lists, every field of every row ---------------------------------------------------------------------------------------
        if BROWSER == "chrome":
            c.cmd("Browser.setDownloadBehavior", behavior="allow", downloadPath=str(downloads))
        else:
            c.js("(function(){ var p = HTMLAnchorElement.prototype; if (!p.__kept) { p.__kept = p.click; p.click = function(){ if (this.hasAttribute('download')) { window.__saved = this.download; return; } return p.__kept.call(this); }; } return 0; })()")
        c.click_on("#c_keep_out"); time.sleep(0.8)                      # the first list is made with the outside-village units left out, so that the filter's second half is in a file too
        exports.append(export_and_check(c, downloads, D["cols"], d, "2018_2025", order, "18", False, prov["run_utc"], f"{d}, window 2018-2025, the changed tier order, the 18 % filter on and the outside-village units left out"))
        c.click_on("#c_keep_out"); time.sleep(0.8)
        # the second list: another window, the provisional order, no filter - so that the window in the file is not the default one, and the order in it is the provisional one
        x, y = c.click_on("#b_tier_reset"); time.sleep(1.0)
        choose(c, "#rank_st", "0")
        c.click_on("input[name=dwindow][value='2017_2023']"); time.sleep(1.0)
        d_second = "Ganjam"
        choose(c, "#rank_district", str(names.index(d_second)))
        choose(c, "#rank_within", "share")                         # and ordered by share within a tier, so that the file's column for that order is checked in both its states
        exports.append(export_and_check(c, downloads, D["cols"], d_second, "2017_2023", ORDER0, "0", True, prov["run_utc"], f"{d_second}, window 2017-2023, the provisional tier order, no filter, ordered by share within a tier", within="share"))
        choose(c, "#rank_within", "ha")
        choose(c, "#rank_st", "50")
        c.click_on("#c_keep_out"); time.sleep(0.8)
        empty = "Bhadrak"
        choose(c, "#rank_district", str(names.index(empty)))
        s = dstate(c)
        rows, _, _, _ = ranked(empty, "2017_2023", ORDER0, "50", False)
        say("export", f"chose {empty} with the 50 % filter on and the outside-village units left out", f"the list holds {len(s['rows'])} rows, as the tables give ({len(rows)})" + (", and the export button is off: an empty list is not offered as a file that would carry no window" if not rows else ""),
            s["rows"] == rows and (s["export_disabled"] if not rows else not s["export_disabled"]))
        c.click_on("#c_keep_out"); time.sleep(0.6)
        choose(c, "#rank_st", "0")
        c.click_on("input[name=dwindow][value='2018_2025']"); time.sleep(1.0)
        choose(c, "#rank_district", str(names.index(d)))

        # ---- A7. the provisional order again; the legend's own button; leaving and coming back --------------------------------------------------------------
        s = dstate(c)
        rows, _, _, _ = ranked(d, "2018_2025", ORDER0)
        say("tier order", "after 'Back to the provisional order', with the filter off and the first window chosen again", f"the order is the provisional one again, the list is the first list again ({len(s['rows']):,} rows), and the address no longer carries an order, a window or a filter ('{s['hash']}')",
            s["rows"] == rows and "the provisional order" in s["head"] and "tiers=" not in s["hash"] and "st=" not in s["hash"] and "window=" not in s["hash"] and "keepout" not in s["hash"])
        x, y = c.click_on("#b_legend"); time.sleep(0.4)
        s1 = dstate(c)
        c.click_on("#b_legend"); time.sleep(0.4)
        s2 = dstate(c)
        say("legend", f"{c.clicked} the legend's 'Hide' and then 'Show' at ({x}, {y})", f"it shrank to its title ({len(s1['legend'])} rows), still naming the window ('{s1['legend_title']}'), and came back with {len(s2['legend'])} rows",
            len(s1["legend"]) == 0 and "2018-2025" in s1["legend_title"] and len(s2["legend"]) == 7)
        x, y = c.click_on("input[name=layer][value=hansen_loss]"); time.sleep(1.0)
        s = dstate(c)
        r = why_compare(c, target, "2018_2025", ORDER0)
        say("decision view", f"{c.clicked} an ordinary layer, 'Tree cover loss 2001-2025 (Hansen)', at ({x}, {y})", f"the decision view stepped aside: its switch is unticked and its controls are folded away again, the list under the map is gone, the map has its full height again "
            f"({s['map_h']} px), the legend is that layer's ('{s['legend_title'][:40]}...'), and the address is an ordinary layer's, with nothing of the decision view in it ('{s['hash']}'). The unit's panel still carries 'why this tier', now AFTER the "
            f"panel's own sections and not before them ({r['equal']} of {r['of']} lines as the tables give them)",
            s["layer"] == "hansen_loss" and s["more"] == "none" and s["wrap"] == "" and not s["ranked_shown"] and s["ranked_len"] == 0 and "Tree cover loss" in s["legend_title"] and "layer=hansen_loss" in s["hash"]
            and not any(k in s["hash"] for k in ("rank=", "window=", "tiers=", "st=", "keepout")) and r["equal"] == r["of"] == 19 and r["block_is_last_in_the_panel"])
        x, y = c.click_on("#r_decision"); time.sleep(1.0)
        s = dstate(c)
        say("decision view", f"{c.clicked} the decision view again", f"it came back as it was left: {d} still chosen, {len(s['rows']):,} rows", s["layer"] == "decision" and s["rows"] == rows and s["head"].startswith(d + ","))
        ok_a &= no_errors(c, "after part C and part A, step 7")

        # ---- A8. the address ------------------------------------------------------------------------------------------------------------------------------
        d2 = "Koraput"
        o2 = ["dense_loss", "open_loss", "dense_none", "open_none", "little_loss"]
        u2 = ranked(d2, "2017_2023", o2, "18", False)[0][0]
        t = c.fresh(URL + f"#layer=decision&window=2017_2023&rank={d2}&tiers={'.'.join(o2)}&st=18&keepout=0&within=share&unit={u2}")
        s = dstate(c)
        rows, dropped, _, od_ = ranked(d2, "2017_2023", o2, "18", False, "share")
        r = why_compare(c, u2, "2017_2023", o2)
        say("address", "closed the page, then opened the file afresh with '#layer=decision&window=2017_2023&rank=Koraput&tiers=<another order>&st=18&keepout=0&within=share&unit=...'",
            f"the decision view is on with window {WIN[s['window']]}, {d2} ranked ({len(s['rows']):,} rows, as the tables give), the other order of tiers in the legend and in the head, the filter on with the outside-village units left out, the list ordered by share within a tier, and unit {s['unit']} open "
            f"with its tier under that order ({r['equal']} of {r['of']} lines)",
            s["layer"] == "decision" and s["window"] == "2017_2023" and s["rows"] == rows and s["legend"][:6] == legend_expected("2017_2023", o2, d2) and "2017-2023" in s["head"] and s["st"] == "18" and s["keep"] is False and s["within"] == "share" and WITHIN["share"] in s["head"] and s["unit"] == u2 and r["equal"] == r["of"] == 19)
        x, y = c.click_on("input[name=layer][value=agreement]"); time.sleep(1.0)
        s = dstate(c)
        r = why_compare(c, u2, "2018_2025", ORDER0)
        say("decision view", f"with that window and that order still set, {c.clicked} an ordinary layer at ({x}, {y})", f"the block 'why this tier' at the end of the unit's panel is the one of the default window and the provisional order - what the ordinary layer's "
            f"address ('{s['hash']}') gives on a fresh page - and not of the window and order last set in the decision view, whose controls are folded away ({r['equal']} of {r['of']} lines)",
            s["layer"] == "agreement" and r["equal"] == r["of"] == 19 and r["block_is_last_in_the_panel"] and "window=" not in s["hash"] and "tiers=" not in s["hash"])
        c.js("(function(){ location.hash = 'layer=decision&window=2021_2025&rank=Kandhamal'; return 0; })()"); time.sleep(1.8)
        s = dstate(c)
        rows, _, _, _ = ranked("Kandhamal", "2021_2025", ORDER0)
        say("address", "changed the address in place to '#layer=decision&window=2021_2025&rank=Kandhamal'", f"the page shows what that address says and nothing left over from before: window {WIN[s['window']]}, Kandhamal ranked ({len(s['rows']):,} rows), and - the address "
            f"naming no order of tiers, no filter and no order within a tier - the provisional order, no filter and the order by hectares lost, as the same address gives on a fresh page",
            s["window"] == "2021_2025" and s["head"].startswith("Kandhamal,") and s["rows"] == rows and "the provisional order" in s["head"] and s["st"] == "0" and s["keep"] is True and s["within"] == "ha" and WITHIN["ha"] in s["head"] and s["legend"][:6] == legend_expected("2021_2025", ORDER0, "Kandhamal"))
        ok_a &= no_errors(c, "after the two addresses of part A, step 8")
        t = c.fresh(URL + "#layer=decision&window=constructor&rank=Atlantis&tiers=a.b.c&st=toString&keepout=9")
        s = dstate(c)
        say("address", "closed the page, then opened the file afresh with the decision view and nonsense in every other part - among it names every script object answers to ('constructor', 'toString')",
            f"the decision view opened on its own defaults: window {WIN[s['window']]}, no district ranked ('{s['msg'][:40]}...'), the provisional order, no filter; script errors: {c.errors or 'none'}",
            s["layer"] == "decision" and s["window"] == "2018_2025" and s["rank"] == "" and s["msg"] != "" and s["st"] == "0" and s["keep"] is True and s["legend"][:6] == legend_expected("2018_2025", ORDER0) and not c.errors)
        t = c.fresh(URL + f"#layer=agreement&floor=100&window=constructor&st=toString&unit={u2}&open=sources")
        s = dstate(c)
        say("address", "closed the page, then opened an ORDINARY layer's address with the same nonsense in it and a unit to open", f"the ordinary layer opened as it always did (layer '{s['layer']}', unit {s['unit']} in the panel, the sources shown); the nonsense was ignored; "
            f"script errors: {c.errors or 'none'}", s["layer"] == "agreement" and s["unit"] == u2 and s["more"] == "none" and c.js("document.getElementById('modal').style.display") == "block" and not c.errors)
        ok_a &= no_errors(c, "after the nonsense addresses of part A, step 8")
        t = c.fresh(URL + "#layer=decision")

        # ---- A9. a smaller window -------------------------------------------------------------------------------------------------------------------------
        choose(c, "#rank_district", str(names.index(d)))
        for w_, h_ in ((1100, 700), (820, 600)):
            c.resize(w_, h_)
            s = dstate(c)
            say("window size", f"made the window {w_} x {h_} with the decision view and its list on", f"map {s['map_w']} x {s['map_h']} px, the list {s['ranked_h']} px high below it and scrolling inside itself, the legend {s['legend_h']} px high; the page is {s['page_w']} px wide, with no sideways scrolling",
                s["map_w"] >= 350 and s["page_w"] <= w_ + 2 and s["map_h"] >= 200 and s["ranked_h"] >= 150 and s["legend_h"] <= s["map_h"] - 20)
            time.sleep(0.6)
            c.shot(SHOTS / f"A9_window_{w_}x{h_}.png")
        c.reset_size()
        ok_a &= no_errors(c, "at the end of part A")
        say("script errors", "read the page's script errors at the end of each stretch of parts A and C, before every reload", f"none in any of them" if ok_a else f"ERRORS: {errors_seen}", ok_a)
        not_actions += 1

        # ---- B. units opened by a click on the map: all six cells in two windows and more, both kinds, every badge ---------------------------------------
        t = c.open(URL)
        c.click_on("#r_decision"); time.sleep(1.0)
        c.click_on("#b_legend"); time.sleep(0.4)                         # the legend lies over the map's lower left: put away for the whole of this part, so that no click can fall on it
        rng = np.random.default_rng(20261008)
        big = {u for u in IDS if float(X.U.loc[u, "area_ha"]) > 30}
        wanted = []
        for w in ("2018_2025", "2001_2025", "2017_2023"):
            for cell in NAME:
                for kind in (False, True):
                    pool = sorted(u for u in big if T[u][f"cell_{w}"] == cell and OUT[u] == kind and u not in {x_[0] for x_ in wanted})
                    if pool and (w != "2017_2023" or cell in ("dense_loss", "open_loss")):
                        wanted.append((str(rng.choice(pool)), w, f"{'outside village' if kind else 'lgd panchayat'}, cell {cell}, window {WIN[w]}"))
        kinds = sorted({(T[u]["corroboration"], T[u]["corroboration_basis"]) for u in IDS})
        special = [("near the dense/open boundary", lambda u: T[u]["near_dense_open_boundary"] == "1"), ("only CoRE Stack flags it, in the cell 'Protect'", lambda u: T[u]["corroboration"] == "corestack_only" and T[u]["cell_2018_2025"] == "dense_none"),
                   ("district moved off the polygon's name", lambda u: "moved_off_the_name" in T[u]["district_check"]), ("district: no check possible", lambda u: "no_check_possible" in T[u]["district_check"]),
                   ("district ambiguous", lambda u: "ambiguous" in T[u]["district_check"]), ("district flagged", lambda u: "flagged" in T[u]["district_check"]), ("polygon names no district", lambda u: "polygon_has_no_name" in T[u]["district_check"])]
        special += [(f"badge '{a_}' on the basis '{b_}'", (lambda u, a_=a_, b_=b_: T[u]["corroboration"] == a_ and T[u]["corroboration_basis"] == b_)) for a_, b_ in kinds]
        for what, test in special:
            pool = sorted((u for u in IDS if test(u) and float(X.U.loc[u, "area_ha"]) > 3 and u not in {x_[0] for x_ in wanted}), key=lambda u: -float(X.U.loc[u, "area_ha"]))
            if pool:
                wanted.append((pool[0], "2018_2025", what))
        panel_unit = "(function(){var r=document.querySelector('#info table.kv tr'); return r?r.cells[1].textContent:null;})()"
        current, opened_exact, opened_neighbour, opened_nothing, opened_elsewhere = "2018_2025", 0, 0, 0, 0
        for u, w, why in wanted:
            if w != current:
                c.click_on(f"input[name=dwindow][value='{w}']"); time.sleep(0.8)
                current = w
            ll, bb = X.point(u)
            got_unit, before, x, y = None, c.js(panel_unit), 0, 0
            for pad_share in (0.6, 0.15):                                # a second try, closer in, if the first click opened nothing
                pad = max(bb[1][0] - bb[0][0], bb[1][1] - bb[0][1]) * pad_share
                c.js(f"(function(){{ ICTD_MAP.fitBounds([[{bb[0][0] - pad},{bb[0][1] - pad}],[{bb[1][0] + pad},{bb[1][1] + pad}]], {{animate:false, maxZoom:14}}); return 0; }})()"); time.sleep(0.7)
                x, y = X.to_screen(c, ll)
                on_map = c.js(f"(function(){{var e=document.elementFromPoint({x},{y}); return !!(e && e.closest('#map') && !e.closest('#legend'));}})()")
                if not on_map:
                    continue
                c.click(x, y); time.sleep(0.5)
                got_unit = c.js(panel_unit)
                if got_unit != before:
                    break
            r = {"aimed_at": u, "window": w, "why": why, "clicked_at": [round(x), round(y)]}
            if got_unit is None or got_unit == before:                   # the panel is the one that was there before the click: the click opened nothing, and nothing is compared
                opened_nothing += 1
                r.update({"unit": None, "equal": 0, "of": 18, "bad": ["the click opened no unit: the panel did not change"], "cell": T[u][f"cell_{w}"], "type": "outside_village" if OUT[u] else "lgd_panchayat", "badge": ""})
            else:
                touching = got_unit == u or X.G.loc[got_unit].geometry.distance(X.G.loc[u].geometry) < 1e-9
                r.update(why_compare(c, u, w, ORDER0))
                r["why"], r["clicked_at"], r["drawn"] = why, [round(x), round(y)], X.pixel(c, x, y)
                if got_unit == u:
                    opened_exact += 1
                elif touching:
                    opened_neighbour += 1
                else:
                    opened_elsewhere += 1
                    r["bad"] = list(r["bad"]) + [f"the unit opened, {got_unit}, is neither the unit aimed at nor one that touches it"]
                    r["equal"] = 0
            results.append(r)
            print(("PASS  " if r["of"] and r["equal"] == r["of"] else "FAIL  ") + f"[unit] {why}: {c.clicked} the map at ({round(x)}, {round(y)}), aiming at {u}"
                  + ("; NOTHING OPENED" if r["unit"] is None else "" if r["unit"] == u else f"; the click landed on {r['unit']}, a unit that touches it" if r["equal"] else f"; the click opened {r['unit']}, which does not touch it")
                  + f"; {r['equal']} of {r['of']} lines of 'why this tier' are as the tables give them" + ("" if not r["bad"] else "  MISMATCH " + str(r["bad"][:2])), flush=True)
        c.shot(SHOTS / "B_last_unit.png")
        opened = [r for r in results if r["unit"] is not None]
        seen = {(r["cell"], r["window"]) for r in opened}
        badges = sorted({r["badge"] for r in opened})
        say("units", f"aimed {len(results)} clicks at units on the map, in three windows, with the legend put away",
            f"{opened_exact} opened the unit aimed at; {opened_neighbour} opened a unit touching it, which was then the unit compared; {opened_nothing} opened nothing; {opened_elsewhere} opened a unit elsewhere. Every one of the six cells was seen in "
            f"{min(sum(1 for (c_, w_) in seen if c_ == cell) for cell in NAME)} windows or more; {sum(1 for r in opened if r['type'] == 'outside_village')} outside-village and {sum(1 for r in opened if r['type'] == 'lgd_panchayat')} LGD panchayat units; "
            f"outside-village units in {len({T[r['unit']]['district'] for r in opened if r['type'] == 'outside_village'})} districts; {len(badges)} of the {len(kinds)} kinds of badge",
            opened_nothing == 0 and opened_elsewhere == 0 and all(sum(1 for (c_, w_) in seen if c_ == cell) >= 2 for cell in NAME) and {r["type"] for r in opened} == {"outside_village", "lgd_panchayat"} and len(badges) == len(kinds)
            and {p_ for r in opened if r["type"] == "outside_village" for p_ in T[r["unit"]]["district_check"].split("; ")} == set(CHECK) and any(T[r["unit"]]["near_dense_open_boundary"] == "1" for r in opened))
        not_actions += 1
        ok_b = no_errors(c, "at the end of part B")
        say("script errors", "read the page's script errors after the clicks of part B", "none" if ok_b else f"ERRORS: {errors_seen[-1]}", ok_b)
        not_actions += 1

        # ---- D. the optional online overlay ---------------------------------------------------------------------------------------------------------------------
        t = c.open(URL)
        s = dstate(c)
        tiles = lambda: c.js("(function(){var p=document.querySelector('.leaflet-sitelevel-pane'); if(!p) return [0,0]; return [p.querySelectorAll('img').length, p.querySelectorAll('img.leaflet-tile-loaded').length];})()")
        box_shown = lambda: c.js("(function(){var e=document.getElementById('c_overlay'); return !!(e && e.offsetParent !== null);})()")
        if not D["overlay"]["available"]:
            c.click_on("#r_decision"); time.sleep(0.8)
            s = dstate(c)
            say("overlay", "looked at the box 'Site-level overlay'", f"it is there, unticked and disabled, and says: '{s['overlay_msg']}'", s["overlay_disabled"] and not s["overlay"] and "not available" in s["overlay_msg"] and overlay_cfg is None and not (ROOT / "60_layer/overlay.js").exists())
        else:
            host = overlay_cfg["url_template"].split("/")[2]
            reqs = (lambda: [u_ for u_ in c.requests if u_.startswith("http")]) if BROWSER == "chrome" else (lambda: c.js("performance.getEntriesByType('resource').map(function(e){return e.name;}).filter(function(n){return n.indexOf('http')===0;})"))
            say("overlay", "opened the page on its ordinary layer and looked for the box 'Site-level overlay'", f"it is not on show: it belongs to the decision view and is folded away with it; requests to the network since the page opened: {len(reqs())}",
                not box_shown() and not s["overlay"] and len(reqs()) == 0)
            c.click_on("#r_decision"); time.sleep(0.8)
            s, before = dstate(c), reqs()
            say("overlay", "chose the decision view and read the box before touching it", f"it is on show and unticked; it says '{s['overlay_msg'][:120]}...'; requests to the network since the page opened: {len(before)}; no tile is on the map; overlay.js has not been asked for",
                box_shown() and not s["overlay"] and not s["overlay_disabled"] and len(before) == 0 and tiles() == [0, 0] and c.js("typeof window.ICTD_OVERLAY") == "undefined" and overlay_cfg["data_version"] in s["overlay_msg"] and "years of the window" in s["overlay_msg"])
            c.js("(function(){ ICTD_MAP.setView([20.2, 84.3], 9, {animate:false}); return 0; })()"); time.sleep(0.6)
            x, y = c.click_on("#c_overlay")
            for _ in range(80):                                          # until every tile asked for has been drawn (or the overlay has taken itself off)
                time.sleep(0.5)
                tl = tiles()
                if (tl[0] > 0 and tl[1] == tl[0]) or (_ > 4 and not dstate(c)["overlay"]):
                    break
            time.sleep(0.5)
            s, tl, after = dstate(c), tiles(), reqs()
            tile_reqs = [u_ for u_ in after if host in u_]
            c.shot(SHOTS / "D_overlay_on.png")
            overlay_notes.append({"tiles_drawn": tl, "requests_to_the_tile_host": len(tile_reqs), "one_tile_address": tile_reqs[0] if tile_reqs else None, "other_hosts_asked": sorted({u_.split('/')[2] for u_ in after if host not in u_})})
            say("overlay", f"{c.clicked} the box at ({x}, {y}), with a connection", f"overlay.js was loaded and tiles came from {host}: {tl[1]} drawn of {tl[0]} asked for; the box stayed ticked; the message beside the box and the note drawn on the map both carry the whole credit "
                f"('{overlay_cfg['attribution'][:40]}...') and name the window; no other host was asked ({overlay_notes[-1]['other_hosts_asked'] or 'none'})",
                s["overlay"] and tl[1] == tl[0] >= 1 and len(tile_reqs) == tl[0] and not overlay_notes[-1]["other_hosts_asked"] and overlay_cfg["data_version"] in s["overlay_msg"] and overlay_cfg["attribution"] in s["overlay_msg"] and overlay_cfg["attribution"] in s["legend_note"]
                and "2018-2025" in s["legend_note"] and "2018-2025" in s["overlay_msg"] and all("start_year=2018&end_year=2025" in u_ for u_ in tile_reqs))
            c.click_on("input[name=dwindow][value='2021_2025']")
            for _ in range(40):
                time.sleep(0.5)
                if tiles()[1] >= 4:
                    break
            s, new_reqs = dstate(c), [u_ for u_ in reqs() if host in u_ and u_ not in tile_reqs]
            say("overlay", f"with the overlay on, {c.clicked} the window '2021-2025'", f"the overlay was drawn again for those years: {len(new_reqs)} new tiles asked for, each with the years 2021 to 2025 in its address; the message and the legend now name 2021-2025",
                s["overlay"] and len(new_reqs) >= 1 and all("start_year=2021&end_year=2025" in u_ for u_ in new_reqs) and "2021-2025" in s["legend_note"] and "2021-2025" in s["overlay_msg"])
            c.click_on("input[name=dwindow][value='2018_2025']"); time.sleep(1.0)
            c.click_on("#b_legend"); time.sleep(0.4)                     # the legend is longer with the overlay's line in it: put it away so that the unit under it can be clicked
            ll, bb = X.point(watch)
            c.js(f"(function(){{ ICTD_MAP.fitBounds({json.dumps(bb)}, {{animate:false, padding:[60,60]}}); return 0; }})()"); time.sleep(1.0)
            px_, py_ = X.to_screen(c, ll)
            c.click(px_, py_); time.sleep(0.6)
            hidden = c.js("(function(){var e=document.getElementById('legend_overlay'); return {note: e ? e.textContent : '', rows: document.querySelectorAll('#legend .lr').length};})()")
            say("overlay", f"with the overlay on and the legend hidden, {c.clicked} unit {watch} on the map", f"its panel opened ({dstate(c)['unit']}): the overlay does not take the click; and with the legend's {hidden['rows']} rows put away the overlay's "
                f"note is still on the map, with the whole credit and the window ('{hidden['note'][:60]}...')", dstate(c)["unit"] == watch and hidden["rows"] == 0 and overlay_cfg["attribution"] in hidden["note"] and "2018-2025" in hidden["note"])
            c.click_on("#b_legend"); time.sleep(0.4)
            x, y = c.click_on("input[name=layer][value=hansen_loss]"); time.sleep(1.0)
            s, tl = dstate(c), tiles()
            say("overlay", f"with the overlay on, {c.clicked} an ordinary layer", f"the overlay went with the view it belongs to: no tile is left ({tl[0]}), its box is folded away, and the ordinary layer's legend carries no line of it ('{s['legend_note'][:50]}')",
                not s["overlay"] and tl[0] == 0 and not box_shown() and "Overlay on" not in s["legend_note"] and s["layer"] == "hansen_loss")
            c.click_on("#r_decision"); time.sleep(0.8)
            s = dstate(c)
            x, y = c.click_on("#c_overlay")
            for _ in range(40):
                time.sleep(0.5)
                if tiles()[1] >= 4 or not dstate(c)["overlay"]:
                    break
            on_again = dstate(c)["overlay"] and tiles()[1] >= 1
            x, y = c.click_on("#c_overlay"); time.sleep(0.8)
            s2, tl = dstate(c), tiles()
            say("overlay", f"came back to the decision view (the box was unticked: {not s['overlay']}), ticked it, and {c.clicked} the box again at ({x}, {y})", f"it came on again ({on_again}) and then off: its tiles are gone ({tl[0]} left) and the message is the idle one again",
                not s["overlay"] and on_again and not s2["overlay"] and tl[0] == 0 and "off unless ticked" in s2["overlay_msg"])
            ok_d = no_errors(c, "after the overlay's steps with a connection")
            say("script errors", "read the page's script errors after the overlay's steps with a connection", "none" if ok_d else f"ERRORS: {errors_seen[-1]}", ok_d)
            not_actions += 1
            if BROWSER == "chrome":
                c.cmd("Network.emulateNetworkConditions", offline=True, latency=0, downloadThroughput=-1, uploadThroughput=-1)
                t = c.open(URL)
                n0 = len(reqs())
                c.click_on("#r_decision"); time.sleep(0.8)
                x, y = c.click_on("#c_overlay"); time.sleep(1.5)
                s = dstate(c)
                say("overlay", f"set the browser to 'no connection', opened the file afresh and {c.clicked} the box at ({x}, {y})", f"the page opened and works exactly as before (decision view on, {s['drawn']:,} units drawn); the box did not stay ticked and says: '{s['overlay_msg']}'; "
                    f"nothing was asked of the network ({len(reqs()) - n0} requests); script errors: {c.errors or 'none'}",
                    not s["overlay"] and "needs a connection" in s["overlay_msg"] and s["layer"] == "decision" and s["drawn"] == len(IDS) and len(reqs()) == n0 and tiles() == [0, 0] and not c.errors)
                c.cmd("Network.emulateNetworkConditions", offline=False, latency=0, downloadThroughput=-1, uploadThroughput=-1)
                c.cmd("Network.setBlockedURLs", urls=[f"*{host}*"])              # from here the browser is MADE to fail requests to the tile host
                t = c.open(URL)
                c.click_on("#r_decision"); time.sleep(0.8)
                c.js("(function(){ ICTD_MAP.setView([20.2, 84.3], 9, {animate:false}); return 0; })()"); time.sleep(0.5)
                x, y = c.click_on("#c_overlay")
                for _ in range(30):
                    time.sleep(0.5)
                    if not dstate(c)["overlay"]:
                        break
                s = dstate(c)
                say("overlay", f"with a connection but the tile host out of reach (its address blocked in the browser), {c.clicked} the box", f"when every tile asked for had failed the overlay took itself off: the box is unticked, no tile is left, and it says: '{s['overlay_msg']}'",
                    not s["overlay"] and "could not be reached" in s["overlay_msg"] and tiles()[0] == 0)
                c.js("(function(){ ICTD_MAP.setView([20.2, 84.3], 14, {animate:false}); return 0; })()"); time.sleep(0.6)
                x, y = c.click_on("#c_overlay")
                for _ in range(30):
                    time.sleep(0.5)
                    if not dstate(c)["overlay"]:
                        break
                s = dstate(c)
                say("overlay", f"the same, zoomed in to where one view asks for only a few tiles (zoom 14): {c.clicked} the box", f"the few tiles asked for all failed and the overlay took itself off just the same: the box is unticked and it says: '{s['overlay_msg']}'",
                    not s["overlay"] and "could not be reached" in s["overlay_msg"] and tiles()[0] == 0)
                ok_blocked = no_errors(c, "after the tile host was out of reach")
                # the connection goes AFTER tiles have arrived: a few failures must be SAID, beside the box and on the map; many in a row must take the overlay off
                c.cmd("Network.setBlockedURLs", urls=[])
                t = c.open(URL)
                c.click_on("#r_decision"); time.sleep(0.8)
                c.js("(function(){ ICTD_MAP.setView([20.2, 84.3], 9, {animate:false}); return 0; })()"); time.sleep(0.5)
                x, y = c.click_on("#c_overlay")
                for _ in range(60):
                    time.sleep(0.5)
                    if tiles()[1] >= 4:
                        break
                time.sleep(2.0)                                              # let every tile of this view arrive, so that the next ones are the only ones to fail
                had = tiles()[1]
                c.cmd("Network.setBlockedURLs", urls=[f"*{host}*"])
                c.js("(function(){ ICTD_MAP.panBy([256, 0], {animate:false}); return 0; })()")      # one tile's width: one new column of tiles is asked for, and fails
                s = dstate(c)
                for _ in range(20):
                    time.sleep(0.5)
                    s = dstate(c)
                    if "not a sign of no loss" in s["overlay_msg"] or not s["overlay"]:
                        break
                partial_ok = s["overlay"] and s["overlay_msg"].startswith("Some tiles could not be loaded") and "not a sign of no loss" in s["legend_note"] and tiles()[1] >= 1
                say("overlay", f"ticked the box with a connection ({had} tiles arrived), then cut the tile host off and moved the map by one tile's width", f"the new column of tiles failed, and the overlay stayed on and SAID so, beside the box ('{s['overlay_msg'][:60]}...') "
                    f"and in the note drawn on the map ('{s['legend_note'][-200:][:70]}...'): missing pink is not shown as no loss", had >= 4 and partial_ok)
                c.js("(function(){ ICTD_MAP.setView([21.6, 85.6], 11, {animate:false}); return 0; })()")
                for _ in range(60):
                    time.sleep(0.5)
                    s = dstate(c)
                    if not s["overlay"]:
                        break
                c.cmd("Network.setBlockedURLs", urls=[])
                say("overlay", "with the tile host still cut off, moved the map to a place none of whose tiles were loaded", f"after eight tiles in a row had failed the overlay took itself off: the box is unticked, no tile is left, and it says: '{s['overlay_msg']}'",
                    not s["overlay"] and "took itself off" in s["overlay_msg"] and tiles()[0] == 0)
                ok_blocked &= no_errors(c, "after the tile host was cut off with the overlay on")
                c.cmd("Network.setBlockedURLs", urls=["*overlay.js*"])
                t = c.open(URL)
                c.click_on("#r_decision"); time.sleep(0.8)
                x, y = c.click_on("#c_overlay"); time.sleep(1.5)
                s = dstate(c)
                c.cmd("Network.setBlockedURLs", urls=[])
                say("overlay", f"with the overlay's own file kept from loading, {c.clicked} the box", f"the box is unticked and says: '{s['overlay_msg']}'; the map is the offline map", not s["overlay"] and "overlay.js, is not beside this page" in s["overlay_msg"])
                ok_blocked &= no_errors(c, "after overlay.js was kept from loading")
                say("script errors", "read the page's script errors after each of the steps in which the browser was made to fail requests", "none: a request the browser is made to fail is not an error of the page's script" if ok_blocked else f"ERRORS: {errors_seen}", ok_blocked)
                not_actions += 1
            else:
                say("overlay", "did not try 'no connection', a tile host out of reach or a missing overlay.js here", "this view cannot be put offline, nor have an address blocked, from outside; those steps are in the Chrome run", True)
                not_actions += 1
        ok_end = no_errors(c, "at the end of the run")
        steps_ok = sum(s_["ok"] for s_ in steps)
        equal, total = sum(r["equal"] for r in results), sum(r["of"] for r in results)
        summary = {"script": "scripts/exercise_decision.py", "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "inputs": X.INPUTS, "browser": c.version, "events_were": c.how, "opened": URL, "layer_run_utc": prov["run_utc"], "files_sha256": files,
                   "decision_table_run_utc": PROV["run_utc"], "steps": len(steps), "steps_as_expected": steps_ok, "steps_that_are_statements_and_not_actions": not_actions,
                   "controls_exercised": len(steps), "controls_as_expected": steps_ok,
                   "clicks_aimed_at_units": len(results), "units_opened_as_aimed": opened_exact, "units_opened_that_touch_the_one_aimed_at": opened_neighbour, "clicks_that_opened_nothing": opened_nothing, "clicks_that_opened_a_unit_elsewhere": opened_elsewhere,
                   "units_opened": len(opened), "lines_compared": total, "lines_equal": equal, "cells_and_windows_seen": sorted(f"{c_} / {w_}" for c_, w_ in seen), "kinds_of_badge_seen": badges, "kinds_of_badge_there_are": len(kinds),
                   "by_type": pd.Series([r["type"] for r in opened]).value_counts().to_dict(), "districts_of_outside_village_units_opened": sorted({T[r["unit"]]["district"] for r in opened if r["type"] == "outside_village"}),
                   "export": exports[0] if exports else {}, "export_second": exports[1] if len(exports) > 1 else {}, "overlay": {"registered": overlay_cfg is not None, "notes": overlay_notes},
                   "script_errors": errors_seen, "script_errors_were_read": "at the end of every part and before every reload" + ("" if BROWSER == "chrome" else "; in this view a page's errors are lost when it is reloaded, which is why they are read before each one"),
                   "tier_arrows_pressed": sum(1 for s_ in steps if s_["control"] == "tier order" and "arrow of tier" in s_["did"]), "tier_arrows_there_are": 2 * len(ORDER0) - 2}
        print(f"\n{steps_ok} of {len(steps)} steps did what they should; {len(opened)} units opened on the map ({opened_exact} as aimed, {opened_neighbour} touching the one aimed at; {opened_nothing} clicks opened nothing); {equal} of {total} lines of 'why this tier' are as the tables give them; "
              f"exports: " + "; ".join(f"{e.get('cells_equal')} of {e.get('cells_compared')} cells" for e in exports) + f"; script errors: {errors_seen or 'none'}")
        json.dump({"summary": summary, "steps": steps, "units": results}, open(ROOT / "60_layer" / f"exercise_decision_{BROWSER}.json", "w", encoding="utf-8"), indent=1, default=str)
        return 0 if steps_ok == len(steps) and equal == total and total > 0 and not errors_seen and ok_end else 1
    finally:
        c.close()
        if profile:
            shutil.rmtree(profile, ignore_errors=True)
        shutil.rmtree(downloads, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
