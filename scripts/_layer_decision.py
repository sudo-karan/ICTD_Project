"""The decision view's part of the demo layer (added 8 Oct 2026). Not a step, and it writes nothing: 06_build_layer.py calls
build() and puts what it returns into data.js beside the existing layers, into the About and Sources texts, and - only if a
documented tile endpoint is registered in scripts/layer_overlay.json - into a third, optional file, 60_layer/overlay.js.

It reads 55_decision/ (scripts/05_build_decision.py), for two figures of the About text 20_degradation/agreement_summary.csv, and
for the providers' cautions about the data 00_raw/05_forest_reference/provider_cautions.json - so that those cautions are in
the About text whether or not the overlay is there (the owner's ruling of 9 October 2026).
Every hectare is formatted here, from the table's four-decimal value, to the hundredth it was classed on - by Python's own
two-decimal formatting of the figure, the rule of every other hectare on the map, not "half up"; the page looks strings up
and joins them. Nothing existing is changed by it: no field of the unit panel, no layer, no default.

WHY overlay.js IS A FILE OF ITS OWN. The layer's own checks - which stay as they are - forbid any map-tile or network code in
index.html and data.js. So the one piece of code that can ask the network for something lives in a third file that the page
loads only when its user ticks the overlay. Delete overlay.js and the layer is exactly the offline layer.

THE WORDS (11 Oct 2026, the owner's second handoff of that day). The view's labels were shortened and put in the first and
second person; what a label needs said beside it is the words of a small "i". build() returns those words under "tips" and
06_build_layer.py puts them into the one new key of data.js, `tips`: "decision", "window_head", "tiers", "rank_none",
"filter" and "col_share". Two more "i" reuse words the view already had, under their own keys: a window's `is`, and the
overlay's `note` and `version`. No key of the view itself was added, renamed or taken away. The strings that come from
55_decision/ (the cells' names and what they rest on, the tiers' reasons, the work-type fields, the windows'
descriptions, the governance prompt) and the owner's words for standing forest are as they were.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

WINDOW_LABEL = {"2018_2025": "2018-2025", "2001_2025": "2001-2025", "2017_2023": "2017-2023", "2021_2025": "2021-2025"}
CELL_COLOR = {"dense_none": "#1b7837", "dense_loss": "#d7301f", "open_none": "#a6dba0", "open_loss": "#fd8d3c", "little_loss": "#c994c7", "little_none": "#f0f0f0"}
ROW_WORDS = {"mostly_dense": "mostly dense", "mostly_open": "mostly open", "little_or_none": "little or none"}
# A name too long for the legend may be shortened THERE ONLY (the owner's ruling of 9 October 2026); the panel, the list and the export carry the full name.
LEGEND_NAME = {}
STANDING_IS = "the forest of 2000 with no loss recorded since; not a measure of tree cover today"          # the owner's wording of 9 October 2026, in place of "a lower bound"
CAUTIONS = "00_raw/05_forest_reference/provider_cautions.json"
CORRO = {"both": "Both measures flag this unit", "hansen_only": "Only Hansen flags it (clearance)", "corestack_only": "Only CoRE Stack flags it (degradation)", "neither": "Neither measure flags it"}
EAST = " - East Coast zone: CoRE Stack's own check fails here, so corroboration is unreliable"
NOT_COMPARED = {"below_floor": "Not compared: under {floor:g} ha of land with canopy above 10 % in 2000, the agreement test's floor",
                "below_floor_no_corestack_coverage": "Not compared: under {floor:g} ha of land with canopy above 10 % in 2000, the agreement test's floor; and CoRE Stack gives no class on such land here",
                "corestack_covers_under_floor": "Not compared: CoRE Stack gives a class on under {floor:g} ha of this unit's land with canopy above 10 % in 2000, the agreement test's floor"}
CHECK = {"name_on_the_polygon_not_contradicted": "the name on its boundary polygon; none of the district checks' flags is raised", "moved_off_the_name": "moved off the name on its polygon: two checks contradicted the name and agreed with each other",
         "polygon_has_no_name": "its polygon names no district: taken from the panchayat polygons under it or the villages round it", "ambiguous": "ambiguous: two districts within 5 points of each other",
         "flagged_one_check_contradicts": "flagged: one check contradicts the district it carries", "no_check_possible": "no check possible: a name, and nothing to check it against"}


# The columns of an exported list, in order (the owner's ruling of 9 October 2026: the development index of 2011 is not among them; forest at the start of the window and the share are).
EXPORT_COLS = ["district", "unit_id", "unit_name", "unit_type", "outside_village", "window_of_forest_loss", "standing_forest_is_through", "tier_label", "tier_definition", "tier_order_in_use", "tier_order_is", "order_within_a_tier",
               "standing_dense_ha", "lost_from_dense_in_window_ha", "standing_open_ha", "lost_from_open_in_window_ha", "land_with_10pct_canopy_or_less_in_2000_ha", "lost_on_that_land_in_window_ha_reported_only",
               "standing_forest_ha", "forest_loss_in_window_ha", "forest_at_window_start_ha", "forest_loss_share_pct", "standing_minimum", "loss_minimum", "close_call_dense_or_open", "corroboration", "corroboration_window",
               "scheduled_tribe_share", "forest_named_expenditure_geotagged_record_ends_FY2017_18", "district_assigned_by", "filter_in_use", "layer_built_utc"]


def hundredths(x):
    """A four-decimal hectare figure as the map prints it, by the rule of every other hectare on the map - the figure the unit was classed on."""
    return f"{float(x):,.2f}"


def build(root, ids, outside, district_names, summ, st_classes, fields, also, fails, started):
    """ids, outside: the layer's units in its own order. district_names: its districts in the order of the page's list.
    st_classes: the labels of the Scheduled Tribe layer's classes, in order (the filter names classes, it computes no share).
    fields: where, in a unit's list of displayed strings, its name, id, Scheduled Tribe share, development index and
    forest-named expenditure are."""
    root = Path(root)
    T = pd.read_csv(also("55_decision/condition_by_unit.csv", "the decision view: every hectare, cell and order"), dtype={"unit_id": str, "pc11_district_code": str}, keep_default_na=False, na_values=[""])
    P = json.load(open(also("55_decision/decision.provenance.json", "the decision view: definitions, thresholds, checks")))
    tiers = pd.read_csv(also("55_decision/tiers.csv", "the decision view: the provisional tier order"), keep_default_na=False)
    work = pd.read_csv(also("55_decision/work_types.csv", "the decision view: the work-type field of each cell"), dtype=str, keep_default_na=False).set_index("cell")
    cells_t = pd.read_csv(also("55_decision/condition_cells.csv", "figures in the texts"))
    sens = pd.read_csv(also("55_decision/condition_sensitivity.csv", "figures in the texts"))
    bound = pd.read_csv(also("55_decision/condition_boundary.csv", "figures in the texts"))
    ev = pd.read_csv(also("55_decision/condition_threshold_evidence.csv", "figures in the texts"))
    share_t = pd.read_csv(also("55_decision/condition_share.csv", "figures in the texts: loss as a share"), keep_default_na=False)
    PC = json.load(open(also(CAUTIONS, "the providers' cautions about the data, quoted in the About text")))
    n = len(ids)
    if len(T) != n or list(T["unit_id"]) != list(ids):
        fails.append("55_decision/condition_by_unit.csv does not hold the layer's units in the layer's order: run scripts/05_build_decision.py")
        return None
    windows, cells, defs = list(P["definitions"]["windows"]), list(P["definitions"]["cells"]), P["definitions"]["cells"]
    default_window, th = P["definitions"]["default_window"], P["thresholds"]
    smin, lmin, floor = float(th["standing_min_ha"]), float(th["loss_min_ha"]), 100.0
    order = list(P["tiers"]["order"])
    unranked = P["tiers"]["unranked"]
    if set(windows) != set(WINDOW_LABEL) or set(cells) != set(CELL_COLOR) or set(order) | {unranked} != set(cells) or len(cells) > 10:
        fails.append("the decision table has windows, cells or tiers the page has no words for")
        return None
    if not set(T["district"]) <= set(district_names):
        fails.append("the decision table names a district the layer does not have")
        return None
    code = {c: str(i) for i, c in enumerate(cells)}
    d_index = {d: i for i, d in enumerate(district_names)}
    row_def = {"mostly_dense": f"Forest standing now is mostly dense: {smin:g} ha or more of standing forest, and standing dense at least as large as standing open.",
               "mostly_open": f"Forest standing now is mostly open: {smin:g} ha or more of standing forest, and standing open larger than standing dense.",
               "little_or_none": f"Forest standing now is little or none: under {smin:g} ha of standing forest."}
    col_def = {"some": f"Forest loss in the window is some: {lmin:g} ha or more.", "none": f"Forest loss in the window is none: under {lmin:g} ha."}
    payload_cells = [{"id": c, "name": defs[c]["name"], "color": CELL_COLOR[c], "row": ROW_WORDS[defs[c]["standing_row"]], "loss": defs[c]["loss_column"], "rests": defs[c]["what_the_name_rests_on"],
                      "def": row_def[defs[c]["standing_row"]] + " " + col_def[defs[c]["loss_column"]], "work": work.loc[c, "work_type_field"], "legend": LEGEND_NAME.get(c, defs[c]["name"])} for c in cells]
    loss_cells = [c for c in cells if defs[c]["loss_column"] == "some"]
    work_note = str(work["note"].iloc[0]) if "note" in work.columns else ""
    want = ["Less than 18 %", "18 to 33 %", "33 to 50 %", "More than 50 %"]
    if list(st_classes[:4]) != want:
        fails.append("the Scheduled Tribe layer's classes are not the ones the decision view's filter names")
        return None
    st_codes = {"0": "", "18": "123", "33": "23", "50": "3"}      # the classes of that layer a filter keeps, by their place in its list
    grid = [[ROW_WORDS[r].capitalize()] + [c for col in ("none", "some") for c in cells if defs[c]["standing_row"] == r and defs[c]["loss_column"] == col] for r in ("mostly_dense", "mostly_open", "little_or_none")]
    if any(len(g) != 3 for g in grid):
        fails.append("the six cells do not fill a grid of three rows and two columns")
        return None
    cls, counts, dcounts, rank, loss, rank_share = {}, {}, {}, {}, {}, {}
    for w in windows:
        cell = T[f"cell_{w}"]
        cls[w] = "".join(code[c] for c in cell)
        counts[w] = [f"{int((cell == c).sum()):,} units" for c in cells]
        per = [[[] for _ in cells] for _ in district_names]
        o = T[f"order_in_district_cell_{w}"].to_numpy()
        for k in np.lexsort((o, cell.map(code).astype(int).to_numpy(), T["district"].map(d_index).to_numpy())):
            per[d_index[T["district"].iat[k]]][int(code[cell.iat[k]])].append(int(k))
        rank[w] = per
        # the second order, by share: held only for the cells with loss; a cell without loss has none (the page then keeps the order by standing hectares)
        pers = [[([] if c in loss_cells else None) for c in cells] for _ in district_names]
        os_ = T[f"order_in_district_cell_by_share_{w}"].to_numpy()
        for k in np.lexsort((os_, cell.map(code).astype(int).to_numpy(), T["district"].map(d_index).to_numpy())):
            if cell.iat[k] in loss_cells:
                pers[d_index[T["district"].iat[k]]][int(code[cell.iat[k]])].append(int(k))
        rank_share[w] = pers
        if any(sorted(a_) != sorted(b_) for da, db in zip(per, pers) for a_, b_ in zip(da, db) if b_ is not None):
            fails.append(f"the decision view's order by share for {w} does not hold the same units as the order by hectares, cell by cell")
        dcounts[w] = [[f"{len(x):,}" for x in d] for d in per]
        share_text = T[f"forest_loss_share_pct_{w}"]
        if ((share_text.isna()) != (T[f"forest_loss_share_blank_because_{w}"].fillna("") != "")).any():
            fails.append(f"window {w}: a share is blank without its reason, or given with one")
        loss[w] = {"d": [hundredths(x) for x in T[f"loss_dense_ha_{w}"]], "o": [hundredths(x) for x in T[f"loss_open_ha_{w}"]], "f": [hundredths(x) for x in T[f"forest_loss_ha_{w}"]],
                   "l": [hundredths(x) for x in T[f"loss_low_ha_{w}"]], "s": [hundredths(x) for x in T[f"forest_at_window_start_ha_{w}"]],
                   "p": ["" if pd.isna(x) else f"{float(x):.2f}" for x in share_text]}
        if sum(len(x) for d in per for x in d) != n:
            fails.append(f"the decision view's order for {w} does not hold every unit once")
    labels = [CORRO[k] for k in CORRO] + [CORRO[k] + EAST for k in CORRO] + [NOT_COMPARED[k].format(floor=floor) for k in NOT_COMPARED]
    where = {**{(k, "headline"): i for i, k in enumerate(CORRO)}, **{(k, "east_coast_every_unit_kept"): len(CORRO) + i for i, k in enumerate(CORRO)},
             **{("not_compared", k): 2 * len(CORRO) + i for i, k in enumerate(NOT_COMPARED)}}
    try:
        corro = [where[(a, b)] for a, b in zip(T["corroboration"], T["corroboration_basis"])]
    except KeyError as e:
        fails.append(f"the decision table has a corroboration the page has no words for: {e}")
        return None
    letters = "0123456789ab"
    prompts = sorted(set(T.loc[np.asarray(outside, bool), "governance_prompt"].fillna("")))
    if len(prompts) != 1 or not prompts[0] or (T.loc[~np.asarray(outside, bool), "governance_prompt"].fillna("") != "").any():
        fails.append("the governance prompt is not one sentence carried by the outside_village units and by no other")
        return None
    governance = prompts[0]
    check_labels, check_code = [""], []
    for o_, c in zip(outside, T["district_check"].fillna("")):
        text = "; ".join(CHECK[p] for p in str(c).split("; ")) if o_ else ""
        if text not in check_labels:
            check_labels.append(text)
        check_code.append(check_labels.index(text))
    if len(check_labels) > 36 or len(labels) > len(letters):
        fails.append("too many kinds of district check or of corroboration for the page's codes")
        return None

    # ---- the figures of the texts, each read from a table -----------------------------------------------------------------------
    head = summ[(summ.window == "common_2017_2023") & (summ.minimum_reference_ha == floor) & (summ.delivered == 1)]
    at, al = head[head.units == "lgd_panchayat"], head[head.units == "all units"]
    if len(at) != 1 or len(al) != 1:
        fails.append("agreement_summary.csv has no single headline row for LGD panchayat units, or for all units")
        return None
    at, al = at.iloc[0], al.iloc[0]
    within = f"{at.odds_ratio_within_districts:.2f}, interval {at.odds_ratio_within_districts_lo95:.2f} to {at.odds_ratio_within_districts_hi95:.2f}"
    across = f"{at.odds_ratio:.2f}, {at.odds_ratio_lo95:.2f} to {at.odds_ratio_hi95:.2f}"
    across_all = f"{al.odds_ratio:.2f}, {al.odds_ratio_lo95:.2f} to {al.odds_ratio_hi95:.2f}"
    n_head = int(at.n_assessed)
    if not (at.odds_ratio_within_districts_lo95 > 1 and at.odds_ratio_lo95 < 1 < at.odds_ratio_hi95 and al.odds_ratio_lo95 > 1):
        fails.append("the About text says that among the headline's LGD panchayat units the two measures agree within districts and that agreement across the state is not established, and that for all units "
                     "together the across-state interval lies above 1; agreement_summary.csv no longer says so")
    cw = cells_t[(cells_t.window == default_window) & (cells_t.units == "all units")].set_index("cell")
    co = cells_t[(cells_t.window == default_window) & (cells_t.units == "outside_village")].set_index("cell")
    if "key" not in ev.columns or not ev["key"].is_unique:
        fails.append("55_decision/condition_threshold_evidence.csv has no column of keys: run scripts/05_build_decision.py")
        return None
    evk = ev.set_index("key")
    e = lambda k: evk.loc[k]
    pixel = float(e("pixel_ha")["value"])
    keep = float(e(f"share_standing_{smin:g}")["value"])
    recur, fresh = e(f"recur_{smin:g}_{lmin:g}"), e(f"fresh_{smin:g}")
    one_px = int(e(f"under_mid_pixel_{default_window}")["value"])
    size_lo, size_hi = e("some_loss_share_10"), e("some_loss_share_5000")
    dl_small, pl16, pl18 = e("dense_loss_under_1pct"), float(e("plantation_share_fy2016_17")["value"]), float(e("plantation_share_fy2018_19")["value"])
    sd = sens[sens.window == default_window].drop_duplicates(["standing_min_ha", "loss_min_ha"]).set_index(["standing_min_ha", "loss_min_ha"])["units_whose_cell_differs_from_the_default_all_cells"]
    alt_s, alt_l = [float(x) for x in th["alternatives"]["standing_min_ha"]], [float(x) for x in th["alternatives"]["loss_min_ha"]]
    near = bound[(bound.is_the_flag_in_the_table == 1) & (bound.units == "all units")].iloc[0]
    x = T[T[f"cell_{default_window}"] == "dense_none"]
    intact_cs = int(x["corroboration"].isin(["corestack_only", "both"]).sum())
    intact_compared = int((x["corroboration"] != "not_compared").sum())
    intact_ec = int((x["corroboration"].isin(["corestack_only", "both"]) & (x["corroboration_basis"] == "east_coast_every_unit_kept")).sum())
    intact_lost = int((x["forest_loss_ha_2001_2025"].astype(float).map(lambda v: float(f"{v:.2f}")) >= lmin).sum())      # on the printed figure, as every threshold is
    land = T["dense_2000_ha"].astype(float) + T["open_2000_ha"].astype(float) + T["low_2000_ha"].astype(float)
    small_units = int((land < smin).sum())
    y = T[f"cell_{default_window}"] == unranked
    small_unranked, small_ranked = int(((land < smin) & y).sum()), int(((land < smin) & ~y).sum())
    if set(T.loc[land < smin, "standing_row"]) - {"little_or_none"} or set(T.loc[(land < smin) & ~y, f"cell_{default_window}"]) - {"little_loss"}:
        fails.append("a unit with less land than the standing minimum is not in the row 'little or none': the About text says every one is")
    half_forest = int((y & (2 * T["standing_forest_ha"].astype(float) >= land) & (land > 0)).sum())
    naming_path = root / "55_decision" / "work_rows_naming_forest.csv"
    uncited = []
    if registered_early := bool(P["work_types"]["registered"]):
        wf = pd.read_csv(also("55_decision/work_rows_naming_forest.csv", "the decision view: rows of the list that name forest, and the cells that cite them"), keep_default_na=False)
        uncited = [f"Sl. {int(r_.serial)} {r_.work_name} ({r_.work_type})" for r_ in wf.itertuples() if not r_.cited_by_cells]
    full = T["cell_2001_2025"] == "open_loss"
    full_quiet = int((full & (T[f"forest_loss_ha_{default_window}"].astype(float).map(lambda v: float(f"{v:.2f}")) < lmin)).sum())
    n_site = int(near.n_units_mostly_dense_or_mostly_open)
    out_site = int(sum(int(co.loc[c, "n_units"]) for c in cells if c != unranked))
    registered = bool(P["work_types"]["registered"])
    within_tier = "Within a tier, most hectares lost first; in a cell without loss, most standing hectares of its kind first."
    within_tier_share = "Within a tier, biggest share lost first (units with no share go last, by hectares lost); in a cell without loss, most standing hectares of its kind first."
    sh = share_t[share_t.window == default_window].set_index("cell")
    sc = P["counts"]["loss_as_a_share"][default_window]
    dl_share, none_share = e("dense_loss_share_under_1pct"), e("none_cell_share_over_2pct")
    intact_loss_ha = float(cw.loc["dense_none", "forest_loss_ha_in_window"])
    no_share_reason = sorted(set(T[f"forest_loss_share_blank_because_{default_window}"].dropna()) - {""})
    if len(no_share_reason) != 1 or int(sc["units_with_a_share"]) + int(sc["units_with_no_share"]) != n or int(sh["n_with_a_share"].astype(int).sum()) != int(sc["units_with_a_share"]):
        fails.append("the share's counts in 55_decision do not add up, or its blanks carry more than one reason")
        return None
    pcs, pct = PC["sentences"], PC["percentages_read_from_the_sentences"]
    need_c = ("loss_is", "cover_today_is_not_cover_of_2000_less_loss", "errors", "tree_cover_is", "umd_loss_is")
    if any(k not in pcs for k in need_c) or "clearing of at least half of tree cover" not in pcs["loss_is"]["text"] or "cannot be determined by subtracting" not in pcs["cover_today_is_not_cover_of_2000_less_loss"]["text"]:
        fails.append(CAUTIONS + " does not hold the sentences the About text quotes")
        return None

    # ---- the optional online overlay: only from a registered, documented endpoint ------------------------------------------------
    cfg_path = root / "scripts" / "layer_overlay.json"
    overlay_js, overlay = None, {"available": 0, "label": "Site-level overlay: Hansen tree cover loss as map tiles",
                                 "unavailable": "The site-level overlay is not available in this build: no documented tile endpoint has been registered for it."}
    record = {"registered": False}
    if cfg_path.is_file():
        cfg = json.load(open(also("scripts/layer_overlay.json", "the optional online overlay: its documented endpoint, terms and version")))
        need = ("url_template", "documented_at", "attribution", "data_version", "loss_through_year", "terms_url", "provider", "max_native_zoom", "verified_utc")
        if any(k not in cfg or cfg[k] in ("", None) for k in need) or not str(cfg["url_template"]).startswith("https://") or "{z}" not in cfg["url_template"]:
            fails.append("scripts/layer_overlay.json is incomplete: the overlay may name an endpoint only with where it is documented, its terms, its version and its attribution")
            return None
        tpl = (root / "scripts" / "layer_overlay.js").read_text(encoding="utf-8")
        also("scripts/layer_overlay.js", "the optional online overlay: its code, kept out of the page")
        overlay_js = tpl.replace("__URL__", json.dumps(cfg["url_template"])).replace("__ATTRIBUTION__", json.dumps(cfg["attribution"])).replace("__MAX_NATIVE_ZOOM__", str(int(cfg["max_native_zoom"]))) \
                        .replace("__VERSION__", json.dumps(cfg["data_version"]))
        same = "v1.13" in str(cfg["data_version"]).lower()
        version_note = (f"Tiles: {cfg['data_version']}, loss through {cfg['loss_through_year']} - the version the unit tables are built from." if same else
                        f"Tiles: {cfg['data_version']}, loss through {cfg['loss_through_year']}. The unit tables are built from v1.13 (loss through 2025): the overlay's pixels may disagree with them.")
        overlay = {"available": 1, "label": f"Loss pixels ({str(cfg['provider']).split(' (')[0]})",
                   "note": "Online, optional, off unless ticked. When it is ticked this page asks " + cfg["provider"] + " for map tiles, so your network address, the place you are looking at and the years of the window chosen "
                           "leave this machine. Nothing else on this map asks the network for anything.", "version": version_note, "attribution": cfg["attribution"],
                   "legend": "Overlay on - pink: Hansen tree cover loss in {window} on land with about 10 % canopy or more in 2000. A picture to find places by: do not measure from it. " + str(cfg["attribution"]) + ".",
                   "partial": "Some tiles could not be loaded: where no pink is drawn, that is not a sign of no loss.",
                   "lost": "The connection to the tile service was lost and the overlay took itself off. Everything else on the map works as before.",
                   "offline": "The overlay needs a connection, and this browser reports none. Everything else on the map works as before.",
                   "failed": "The overlay could not be reached: it needs a connection. Everything else on the map works as before.",
                   "missing": "The overlay's file, overlay.js, is not beside this page. Everything else on the map works as before.",
                   "on": "Overlay on: pink marks where Hansen records tree cover loss in {window}, on land with about 10 % tree canopy or more in 2000 - dense and open forest together. Zoom in to see single pixels; zoomed out, it is shaded by "
                         "how dense the loss is. It is a picture to find places by, from the provider's own rendering: do not measure from it, and expect it to differ from the unit tables at the edges."}
        record = {"registered": True, **{k: cfg[k] for k in need}, "same_version_as_the_unit_tables": same, "file": "60_layer/overlay.js", "requested": "only when the user ticks the overlay, and only in the decision view",
                  "network_requests_with_the_overlay_ticked": "tiles from the registered host and no other; index.html and data.js themselves still ask for nothing",
                  "terms_unresolved": cfg.get("terms_unresolved", "")}

    wl = WINDOW_LABEL
    cell_rows = "".join(f"<tr><td><span class='sw' style='background:{CELL_COLOR[c]}'></span>{defs[c]['name']}</td><td>{ROW_WORDS[defs[c]['standing_row']]}</td><td>{defs[c]['loss_column']}</td>"
                        f"<td>{int(cw.loc[c, 'n_units']):,}</td><td>{int(co.loc[c, 'n_units']):,}</td></tr>" for c in order + [unranked])
    tier_list = "; ".join(f"{i + 1} {defs[c]['name']}" for i, c in enumerate(order))
    win_is = {w: P["definitions"]["windows"][w]["is"] for w in windows}
    n_naming = int((work["entries"] != "").sum())                 # the cells whose work-type field cites at least one row of the list
    in_words = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
    cells_naming, cells_not_naming = in_words[n_naming].capitalize(), in_words[len(work) - n_naming]
    loss_def = " - by the definition in Global Forest Watch's record of the data, the clearing of at least half of it"            # quoted from the registered record, whether or not the overlay is there
    quote = lambda k: "<q>" + pcs[k]["text"] + "</q>"
    uncited_text = (" The rows of the list that name forest and are cited by no cell, for the Foundation to rule on: " + "; ".join(uncited) + ".") if uncited else ""
    about = f"""
<h1>The decision view</h1>
<p><b>What it is.</b> A second way to read the same measurements; it changes nothing in the layers above. Each unit is placed in one of six cells by two questions put to Hansen's record: how much forest is standing now, and is it
mostly closed or mostly open; and was forest lost in the window of years you choose. The cells are put in an order of tiers, and within one district the units are listed tier by tier. {within_tier} It's a starting point for where to look, to be checked against
what people who know the places see. It is not a verdict on any place, and it is not a score.</p>
<table>
<tr><th>cell</th><th>forest standing now</th><th>forest loss in the window</th><th>units, window {wl[default_window]}</th><th>of them outside-village units</th></tr>
{cell_rows}
</table>
<p><b>Why a unit and not a pixel.</b> Hansen's loss is the removal of a pixel's tree cover{loss_def}: a pixel is either standing or lost, so no pixel can be shown as both dense and losing. A unit is classed from its hectares, and its panel shows them all.</p>
<p><b>Standing forest</b> is the land under canopy in the year 2000 on which Hansen records no loss through 2025, whatever window is chosen: dense where canopy was above 30 %, open where it was 10 to 30 %. It is {STANDING_IS}.
It can be wrong in either direction: gain is not netted off, so cover that grew back, or grew since 2000, is not in it; and recorded loss is itself uncertain. Global Forest Watch's record of the data says: {quote('cover_today_is_not_cover_of_2000_less_loss')} and
{quote('errors')} The split into dense and open is that of 2000, so thinning since then is not seen; and tree cover here is any vegetation taller than 5 m,
which does not tell a natural forest from a plantation. Loss on land with 10 % canopy or less in 2000 is printed in the panel and decides nothing: most of it is on land with no canopy at all in 2000, and its rise over time is largely the producers'
change of method.</p>
<p><b>Two thresholds, ruled on 9 October 2026 as they were proposed.</b> A unit has <i>little or none</i> under {smin:g} ha of standing forest; it has <i>some</i> loss from {lmin:g} ha of forest loss in the window. Neither is the 100 ha of the agreement test, which is a
floor for comparing rates and is not used here. One pixel is about {pixel:.2f} ha, and in {wl[default_window]} {one_px:,} units have a recorded forest loss above zero and under {pixel:g} ha, the area of one pixel in the middle of the state: slivers cut by a
boundary and, where pixels are smaller than that, whole single pixels. A single pixel must not decide a cell; {lmin:g} ha is the smallest patch the Forest Survey of India counts as forest cover. Units with {smin:g} ha or more standing hold {keep:.1f} % of all standing forest. Among units with {smin:g} ha or more standing,
{float(recur['value']):.0f} % of those that lost {lmin:g} ha or more in 2018-2021 lost that much again in 2022-2025; of those that lost under {pixel:g} ha, or nothing, {float(fresh['value']):.0f} %. The thresholds matter. In the window {wl[default_window]}:
with {lmin:g} ha for loss, moving the standing minimum to {alt_s[0]:g} ha or {alt_s[1]:g} ha moves {int(sd.loc[(alt_s[0], lmin)]):,} or {int(sd.loc[(alt_s[1], lmin)]):,} units to another cell; with {smin:g} ha standing, moving the loss minimum to
{alt_l[0]:g} ha or {alt_l[1]:g} ha moves {int(sd.loc[(smin, alt_l[0])]):,} or {int(sd.loc[(smin, alt_l[1])]):,}. A fixed number of hectares also follows the size of a unit's forest: {float(size_lo['value']):.0f} % of the forest sites with 10 to 25 ha
standing have some loss, and {float(size_hi['value']):.0f} % of those with 5,000 ha or more; {int(dl_share['value']):,} of the {int(dl_share['n']):,} units in <i>{defs['dense_loss']['name']}</i> lost under 1 % of the forest they had at the start of the window, and {int(none_share['value']):,} forest sites in a cell with little or no loss
recorded lost over 2 % of theirs. That is why each unit's loss is also shown as a share (below). And
{small_units:,} units have under {smin:g} ha of land and so have <i>little or none</i> whatever their cover: {small_unranked:,} of them are in <i>{defs[unranked]['name']}</i> and {small_ranked:,}, which lost {lmin:g} ha or more in the window, in
<i>{defs['little_loss']['name']}</i>. In {half_forest:,} units of the cell <i>{defs[unranked]['name']}</i> standing forest covers half or more of the land.</p>
<p><b>Loss as a share</b> stands beside the cell and decides no cell. For each unit and window it is the forest loss of the window as a percentage of the forest the unit had at the start of the window: its dense and open hectares of 2000 less the
forest loss recorded before the window's first year. Where a unit had under {smin:g} ha of forest at the start of the window no share is given, and the page says so in words: too little forest for a share to mean anything. In the window {wl[default_window]},
{int(sc['units_with_a_share']):,} units have a share and {int(sc['units_with_no_share']):,} have none, {int(sc['units_with_no_share_in_a_cell_with_loss']):,} of those in a cell with loss recorded. The ranked list can be ordered within a tier by hectares lost, as it
opens, or by share lost; the cells with little or no loss recorded stay ordered by standing hectares either way, and the head of the list and an exported file say which order is in use.</p>
<p><b>Mostly dense or mostly open</b> is decided by which of the two is larger in standing hectares. Of the {n_site:,} units with {smin:g} ha or more, {int(near.n_near_the_boundary):,} have the smaller within a fifth of the larger: their panels say <i>close call</i>.</p>
<p><b>The window</b> is the span of years over which loss is counted: {wl['2018_2025']} ({win_is['2018_2025']}: plantation is {pl16:.1f} % of expenditure there in FY2016-17 and {pl18:.1f} % in FY2018-19), {wl['2001_2025']} ({win_is['2001_2025']}),
{wl['2017_2023']} ({win_is['2017_2023']}) and {wl['2021_2025']} ({win_is['2021_2025']}). It is named in the legend, in every unit's panel, at the head of the ranked list and in every row of an exported list. A cell's name speaks of loss recorded in the window chosen:
under {wl['2001_2025']} that is at any time since 2001 - {full_quiet:,} of the {int(full.sum()):,} units in <i>{defs['open_loss']['name']}</i> under that window lost under {lmin:g} ha in {wl[default_window]}.</p>
<p><b>The tiers are provisional</b>, to be set with the Foundation for Ecological Security: {tier_list}; <i>{defs[unranked]['name']}</i> is on the map and outside the list. A forester could reasonably put tier 2 above tier 1. You can change the order
on the left; an exported list says which order made it.</p>
<p><b>Why the list is within a district and never across the state.</b> Among the {n_head:,} LGD panchayat units of the agreement test's headline (at least {floor:g} ha of land with canopy above 10 % in 2000, East Coast zone left out, 2017-2023), the two
forest measures agree within districts (odds ratio {within}); across the state their agreement is not established ({across}, an interval that includes 1). For all units of that headline together the across-state figure is {across_all}. So for LGD
panchayat units a state-wide ranking would rest on a comparison we can't establish. There is no state-wide ranking.</p>
<p><b>No score.</b> There is no index, no weight and no number out of a hundred. Loss as a share, Scheduled Tribe share, the development index and past spending on forest-named works stand beside the tier, never inside it. Scheduled Tribe share can filter the
list; it never orders it. The geotagged spending record effectively ends with works started in 2017-18. An exported list has {len(EXPORT_COLS)} columns; the development index is shown in the list on this page and is left out of the exported file.</p>
<p><b>Corroboration.</b> Each unit carries what the existing comparison of Hansen with CoRE Stack already says of it, for 2017-2023 whatever window is chosen: both measures flag it, one does, neither does, or it was not compared and why. In the units under
CoRE Stack's East Coast zone model the comparison's own check failed, and the badge says corroboration is unreliable there. In the window {WINDOW_LABEL[default_window]}, of the {int(cw.loc['dense_none', 'n_units']):,} units in <i>{defs['dense_none']['name']}</i>, {intact_compared:,} were compared, and
{intact_cs:,} of those are flagged by CoRE Stack for degradation ({intact_ec:,} of them under the East Coast model). That cell's name says little or no loss recorded, which means under {lmin:g} ha of forest loss in the window chosen for each unit: its units
together carry {intact_loss_ha:,.1f} ha of forest loss in that window, {intact_lost:,} of them lost {lmin:g} ha or more at some time in 2001-2025, and Hansen cannot see a canopy thinning.</p>
<p><b>Outside-village units</b> have forest, so they are classed and listed like any unit: in the window {WINDOW_LABEL[default_window]}, {out_site:,} of them are in a cell other than <i>{defs[unranked]['name']}</i>. No village plan covers them, their panel asks whose plan does, and it says what their
assigned district rests on. Their census columns read <i>no census data for this land</i>.</p>
<p><b>Work types.</b> {cells_naming + " of the " + in_words[len(work)] + " cells name rows of the official list of permissible works by serial number, and the other " + cells_not_naming + " name none: " + str(work["schedule"].iloc[0]) + ". " + work_note + " The word regeneration is in none of its rows, so assisted natural regeneration - the work that the forest cell with the most units points to - is not a work the list names." + uncited_text if registered else "The work-type field of every cell reads <i>" + work.iloc[0]["work_type_field"] + "</i>: the official schedule of permissible works has not been registered as an input, and no list of works is used in its place."}</p>
<p><b>The loss-pixel overlay</b> {"is optional, online, and off unless ticked: Hansen tree cover loss as map tiles from " + cfg["provider"] + ", for the years of the window chosen, on land with about 10 % canopy or more in 2000. " + overlay["version"] + " It's the one thing on this page that goes online: while it's ticked, the page asks that provider's server for tiles, so your network address, the place you're looking at and the years of the window chosen leave your machine. It can be ticked only in the decision view, and it switches itself off when that view is left or when its tiles stop arriving. Its code is in a third file, overlay.js; without that file, or without a connection, the map works exactly as it does without the overlay. It is a picture to find places by, not something to measure from. Two points of the provider's terms of use are unresolved, and they are ours to decide: the terms ask that each request to an API carry an account's key, while the tile service's reference declares none and it returns tiles without one; and they bind a user to an attribution page written for another of the provider's services. The project's documentation (DECISION_LAYER.md, which comes with the project and not with these files) sets both out." if overlay_js else "is not in this build: no documented tile endpoint has been registered for it."}</p>
"""
    sources_rows = ""
    if overlay_js:
        sources_rows += (f"<tr><td>Loss-pixel overlay (optional, online, off unless ticked; its code is in overlay.js)</td><td>{cfg['provider']}: tree cover loss map tiles, {cfg['data_version']}</td>"
                         f"<td>{cfg['attribution']}. Requested only when the overlay is ticked. Terms of use: {cfg['terms_url']} - two points of them are unresolved (see About this map)</td></tr>\n")
    sources_rows += (f"<tr><td>Cautions about Hansen's data quoted in the decision view</td><td>Global Forest Watch's record of the dataset Tree cover loss ({PC['inputs'][0]['source_url']}) and the University of Maryland's page for "
                     f"Global Forest Change version 1.13 ({PC['inputs'][1]['source_url']}), both as read on 8 October 2026</td><td>Short quotations, each with its source; the data itself is CC BY 4.0</td></tr>\n")
    if registered:
        sources_rows += f"<tr><td>Work types named in the decision view</td><td>{work.iloc[0]['schedule']}; Gazette of India, read from egazette.gov.in</td><td>Government of India; no licence is stated for the Gazette</td></tr>\n"

    payload = {
        "title": "Decision view", "radio": "Decision view", "default_window": default_window,
        "windows": [{"id": w, "label": wl[w], "is": P["definitions"]["windows"][w]["is"], "years": [int(y) for y in P["definitions"]["windows"][w]["years"]]} for w in windows],
        "cells": payload_cells, "tiers": order, "unranked": unranked, "tier_why": {r.cell: r.why_this_place_in_the_order for r in tiers.itertuples()},
        "cls": cls, "counts": counts, "dcounts": dcounts, "rank": rank, "rank_share": rank_share,
        "sd": [hundredths(x) for x in T["standing_dense_ha"]], "so": [hundredths(x) for x in T["standing_open_ha"]], "sf": [hundredths(x) for x in T["standing_forest_ha"]], "low": [hundredths(x) for x in T["low_2000_ha"]],
        "loss": loss, "near": "".join(str(int(x)) for x in T["near_dense_open_boundary"]), "corro": "".join(letters[i] for i in corro), "corro_letters": letters, "corro_labels": labels,
        "check": "".join("0123456789abcdefghijklmnopqrstuvwxyz"[i] for i in check_code), "check_labels": check_labels, "governance": governance,
        "fields": fields, "st_codes": st_codes, "grid": grid, "work_note": work_note,
        "standing_min": f"{smin:g} ha", "loss_min": f"{lmin:g} ha", "built": started, "overlay": overlay,
        "t": {
            "legend_title": "Forest standing through 2025, and forest loss in {window}",
            "legend_note": "Thresholds: {smin} of standing forest; {lmin} of forest loss in the window. Standing forest is " + STANDING_IS + ". Tier order: {order}.",
            "tier": "Tier {k}: {name}", "unranked": "Not ranked: {name}", "order_default": "the provisional order", "order_changed": "your own order",
            "window_head": "Count loss over", "tiers_head": "Provisional tier order", "reset": "Back to the provisional order",
            "why_head": "Why this tier", "why_window": "Window: forest loss counted over {window} ({is}). Standing forest is always through 2025.",
            "grid_cols": ["No forest loss in the window", "Some forest loss in the window"],
            "why_cols": ["Canopy in 2000", "Standing now", "Lost in {window}"], "why_rows": ["Dense: above 30 %", "Open: 10 to 30 %", "10 % or less: not counted as forest (the land itself: nothing is taken off it)"],
            "why_low": "Loss on land with 10 % canopy or less is shown for information; it decides nothing.",
            "why_standing_some": "Standing forest: {sf} ha, at or above the {smin} threshold. It's {row}: standing dense is {cmp} standing open.",
            "why_standing_little": "Standing forest: {sf} ha, under the {smin} threshold, so little or none.",
            "cmp_dense": "at least as large as", "cmp_open": "smaller than",
            "why_loss_some": "Forest loss in the window: {fl} ha (dense and open added), at or above the {lmin} threshold.",
            "why_loss_none": "Forest loss in the window: {fl} ha (dense and open added), under the {lmin} threshold.",
            "why_share": "As a share: {share} % of the {start} ha of forest it had at the start of {window}. It's shown beside the cell and decides nothing.",
            "why_share_none": "No share: it had {start} ha of forest at the start of {window}, under the {smin} a share needs to mean anything.",
            "no_share": "no share: under " + f"{smin:g} ha" + " of forest at the start of the window",
            "why_cell": "So the cell is: {name}. {rests}", "why_order": "Under {order}, it's {tier}.",
            "why_was": "In the provisional order it's {ptier}, because:",
            "why_unranked": "It's on the map, outside the ranked list.",
            "near": "Close call: standing dense and standing open are within a fifth of each other, so mostly dense or mostly open is a fine distinction here.",
            "standing_is": "Standing forest is " + STANDING_IS + ".", "corro_head": "Corroboration, 2017-2023 (whatever window is chosen)", "work_head": "Work types", "district_head": "District assigned by",
            "rank_none": "Choose a district to rank its units. We rank within a district, never across the state.",
            "within_tier": within_tier, "within_tier_share": within_tier_share,
            "within_options": [["ha", "By hectares lost"], ["share", "By share lost"]],
            "rank_head": "{district}, ranked units: {n}, tier by tier. {within} Forest loss counted over {window}; standing forest through 2025. Tier order: {order}.",
            "rank_unranked": "In {name}, on the map but outside the list: {n}.",
            "rank_filter_note": "Filter on: {label}; {m} units left out. Scheduled Tribe share filters the list; it never orders it.",
            "rank_out_kept": "{k} units of land outside villages kept in: they have no census data to filter on.",
            "rank_out_dropped": "{k} units of land outside villages left out: no census data. Tick the box to bring them back.",
            "keep_out_off": "(applies when a filter is on)",
            "district_pick": "Pick a district\u2026", "keep_out": "Keep land outside villages", "export": "Download this list (CSV)",
            "st_options": [["0", "No filter"], ["18", "Scheduled Tribe share 18 % or more"], ["33", "Scheduled Tribe share above 33 %"], ["50", "Scheduled Tribe share more than 50 %"]],
            "cols": ["Tier", "Unit", "Kind", "Standing dense, ha", "Standing open, ha", "Forest loss in {window}, ha", "Loss as a share, %", "Corroboration, 2017-2023", "Scheduled Tribe share", "Development index 2011", "Forest-named spending, record ends FY2017-18"],
            "kind": ["LGD panchayat unit", "Outside-village unit"],
            "export_cols": EXPORT_COLS,
        },
    }
    record_out = {"table": "55_decision/condition_by_unit.csv", "table_run_utc": P["run_utc"], "default_window": default_window, "windows": windows, "cells": cells, "tier_order_provisional": order, "unranked": unranked,
                  "thresholds": {"standing_min_ha": smin, "loss_min_ha": lmin, "status": th["status"]}, "export_columns": len(EXPORT_COLS), "cautions_from": CAUTIONS,
                  "legend_names_shortened": {c: LEGEND_NAME[c] for c in LEGEND_NAME}, "units_per_cell": {w: {c: int((T[f'cell_{w}'] == c).sum()) for c in cells} for w in windows},
                  "work_types_registered": registered, "overlay": record,
                  "module": {"path": "scripts/_layer_decision.py", "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "what": "builds the decision view's data and every sentence it shows"},
                  "figures_in_the_about_text": {"odds_ratio_within_districts_lgd": within, "odds_ratio_across_the_state_lgd": across, "odds_ratio_across_the_state_all_units": across_all, "lgd_units_of_the_headline": n_head,
                                                "pixel_ha": pixel, "units_with_loss_under_the_mid_state_pixel_default_window": one_px,
                                                "share_of_standing_forest_kept_pct": keep, "recurrence_pct": float(recur["value"]), "fresh_loss_pct": float(fresh["value"]), "near_boundary": int(near.n_near_the_boundary),
                                                "sensitivity_units_moved": [int(sd.loc[(alt_s[0], lmin)]), int(sd.loc[(alt_s[1], lmin)]), int(sd.loc[(smin, alt_l[0])]), int(sd.loc[(smin, alt_l[1])])],
                                                "some_loss_share_10_to_25_ha_pct": float(size_lo["value"]), "some_loss_share_5000_ha_or_more_pct": float(size_hi["value"]),
                                                "dense_loss_units_under_1pct_of_the_forest_at_the_window_start": int(dl_share["value"]), "dense_loss_units": int(dl_share["n"]), "forest_sites_without_loss_over_2pct": int(none_share["value"]),
                                                "units_with_a_share_default_window": int(sc["units_with_a_share"]), "units_with_no_share_default_window": int(sc["units_with_no_share"]),
                                                "units_with_no_share_in_a_cell_with_loss_default_window": int(sc["units_with_no_share_in_a_cell_with_loss"]), "forest_loss_ha_in_the_closed_cell_without_loss": intact_loss_ha,
                                                "false_positives_pct_as_the_provider_gives_it": int(pct["false_positives_pct"]), "false_negatives_pct_as_the_provider_gives_it": int(pct["false_negatives_pct"]), "units_with_land_under_the_standing_minimum": small_units, "of_them_outside_the_ranked_list": small_unranked, "of_them_in_the_cell_with_little_forest_and_loss": small_ranked,
                                                "forest_named_rows_cited_by_no_cell": len(uncited),
                                                "unranked_units_with_forest_on_half_their_land": half_forest, "open_loss_units_full_record": int(full.sum()), "of_them_under_the_loss_minimum_in_the_default_window": full_quiet,
                                                "plantation_share_fy2016_17_pct": pl16, "plantation_share_fy2018_19_pct": pl18,
                                                "forest_site_units": n_site, "intact_cell_units": int(cw.loc["dense_none", "n_units"]), "intact_cell_units_compared": intact_compared, "intact_cell_units_flagged_by_corestack": intact_cs,
                                                "of_them_under_the_east_coast_model": intact_ec, "intact_cell_units_that_lost_the_loss_minimum_in_2001_2025": intact_lost,
                                                "outside_village_units_in_a_ranked_cell": out_site}}
    # The words of the view's "i" (11 Oct 2026): 06_build_layer.py puts them into data.js under `tips`, beside the layers' own. `rank_none` is the rest of the
    # sentence the empty list used to carry whole, word for word from "Among": its two odds ratios are the same two strings the About text prints. `col_share`
    # keeps {window}, which the page fills with the window chosen, as it fills the column heads.
    tips = {"decision": "Where is forest work needed, and what kind? This view puts every unit in one of six cells (protect; find the cause first; assisted natural regeneration; restore; verify on the ground; not a forest site) "
                        "and lists a district's units in our provisional order of priority. A starting point to check with people who know the ground, not a verdict.",
            "window_head": "Standing forest always runs to 2025; this only changes which years of loss count.",
            "tiers": "To be set with the Foundation for Ecological Security. Use the arrows to change it: the map, the list and any download follow your order.",
            "rank_none": "Among the LGD panchayat units of the agreement test's headline, the two forest measures agree within districts (odds ratio " + within + ") and their agreement across the state is not established (" + across + ").",
            "filter": "Left out: units with a smaller share, or with no resident population in the 2011 census.",
            "col_share": "Forest loss in {window} as a percentage of the forest the unit had at the start of {window}."}
    return {"payload": payload, "about_html": about, "sources_rows": sources_rows, "overlay_js": overlay_js, "record": record_out, "tips": tips}
