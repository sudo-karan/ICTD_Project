"""Stage 4: the six figures for the paper and the deck. Writes into `figures/stage4/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/make_stage4_figures.py [F1 F2 ...]

For each figure: `<name>.png` (300 dpi), `<name>.svg`, `<name>.csv` - exactly what is plotted, one row per mark - and
`<name>.caption.txt`, which gives the claim, n and the source files. The rules every figure keeps: one claim; axis titles
with units; n on every panel; readable in greyscale (F3, the map, is the one exception: a colour-blind-safe palette, with
its classes labelled by name); no title inside the image; the font is Calibri if installed, else Carlito, else
matplotlib's default, and which was used is written into every caption and into `figures.provenance.json`.

No figure computes a statistic of its own: each mark is a cell of a stage table, or a share formed from two cells of one
row (F1: plantation over all expenditure, water over NRM, from the state's printed totals; F2: a kind of unit's share of a
state sum). Nothing is stacked in F1: NRM, water and plantation are nested categories.

F1  the state report: plantation as a share of all expenditure, and water as a share of NRM, FY2014-15 to FY2026-27
F2  the outside-village asymmetry: LGD units' and outside-village units' shares of land, forest, loss, people and money
F3  a map of the default-window cells of all 11,468 units, district boundaries made by dissolving the units
F4  C1: each district's share of need against its share of post-period plantation money; a second panel shows C5
F5  C1 by Scheduled Tribe class and by tercile of the development index: need share beside allocation share
F6  the estimates of the panel and unit models with their wild-bootstrap intervals, one panel per unit of measurement
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D  # noqa: E402

OUT = G.ROOT / "figures" / "stage4"
STEP = "make_stage4_figures"
FONT_DIRS = ["/Library/Fonts", str(Path.home() / "Library/Fonts"), "/System/Library/Fonts", "/Library/Application Support/SoftMaker/fonts",
             "/Applications/LibreOffice.app/Contents/Resources/fonts/truetype", "/usr/share/fonts", "/usr/local/share/fonts"]
BLACK, DARK, MID, LIGHT = "#000000", "#404040", "#8c8c8c", "#d9d9d9"
# Okabe and Ito's palette, made to be told apart with the common forms of colour blindness; the last is a neutral grey.
MAP_COLOURS = {"open_loss": "#D55E00", "dense_loss": "#CC79A7", "open_none": "#F0E442", "dense_none": "#009E73", "little_loss": "#0072B2", "little_none": "#E6E6E6"}
USED = {"files": {}, "font": None}


def choose_font() -> dict:
    """Calibri if installed, else Carlito, else matplotlib's default. Returns what was used and where it was found."""
    for family in ("Calibri", "Carlito"):
        found = [f for f in font_manager.findSystemFonts(fontpaths=None) if Path(f).stem.lower().startswith(family.lower())]
        for d in FONT_DIRS:
            if Path(d).is_dir():
                found += [str(p) for p in Path(d).glob(f"{family}*.ttf")] + [str(p) for p in Path(d).glob(f"{family.lower()}*.ttf")]
        found = sorted(set(found))
        if found:
            for f in found:
                font_manager.fontManager.addfont(f)
            plt.rcParams["font.family"] = family
            return {"font": family, "found_in": sorted({str(Path(f).parent) for f in found}), "files": sorted({Path(f).name for f in found})}
    return {"font": plt.rcParams["font.family"][0] + " (matplotlib's default: neither Calibri nor Carlito was found)", "found_in": [], "files": []}


def style() -> None:
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6, "savefig.dpi": 300, "figure.dpi": 100,
                         "svg.hashsalt": "ictd-stage4", "axes.unicode_minus": False, "hatch.linewidth": 0.5})


def layout_check(fig, points=None) -> dict:
    """What a script can tell about a drawing without looking at it: do two pieces of text sit on one another, are two
    set end to end with less than a word's space between them (so that they read as one), does a label sit on a marker
    that is not its own, does any text lie outside the figure. Boxes are the upright rectangles
    around each piece of text as drawn; tick labels written at an angle are left out of the comparison with one another,
    because their rectangles overlap where the words do not. `points` are (x, y, label) in display units for the markers
    of a scatter, with the label that belongs to each."""
    from matplotlib.text import Text
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    boxes = []
    undrawn = set()
    for ax in fig.axes:                                           # a tick label beyond the axis' limits exists but is not drawn
        for axis, (lo, hi) in ((ax.xaxis, sorted(ax.get_xlim())), (ax.yaxis, sorted(ax.get_ylim()))):
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if not ax.axison or not (lo - 1e-9 <= tick.get_loc() <= hi + 1e-9):
                    undrawn.update({id(tick.label1), id(tick.label2)})
            if not ax.axison:                                     # an axis that is switched off draws neither its ticks nor its title
                undrawn.update({id(axis.label), id(axis.offsetText)})
    for t in fig.findobj(Text):
        s_ = t.get_text().strip()
        if not s_ or not t.get_visible() or id(t) in undrawn:
            continue
        bb = Text.get_window_extent(t, r)                         # the words alone: an annotation's own box takes in its line
        if bb.width > 0 and bb.height > 0:
            boxes.append((s_.replace("\n", " / "), bb, abs(t.get_rotation()) % 180 not in (0, 90), abs(t.get_rotation()) % 180 == 90,
                          t.get_fontsize() * fig.dpi / 72.0))
    hit = lambda a, b: a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1
    pairs = [(boxes[i][0][:48], boxes[j][0][:48]) for i in range(len(boxes)) for j in range(i + 1, len(boxes))
             if not (boxes[i][2] and boxes[j][2]) and hit(boxes[i][1], boxes[j][1])]
    abutting = []                                                 # two texts on one line of reading, less than 0.6 of a letter's height apart
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (s1, b1, ang1, up1, em1), (s2, b2, ang2, up2, em2) = boxes[i], boxes[j]
            if ang1 or ang2 or up1 != up2 or hit(b1, b2):
                continue
            if up1:                                               # both written up the page: they follow one another along y
                along = max(b1.y0, b2.y0) - min(b1.y1, b2.y1)
                across = min(b1.x1, b2.x1) - max(b1.x0, b2.x0) >= 0.5 * min(b1.width, b2.width)
            else:
                along = max(b1.x0, b2.x0) - min(b1.x1, b2.x1)
                across = min(b1.y1, b2.y1) - max(b1.y0, b2.y0) >= 0.5 * min(b1.height, b2.height)
            if across and 0 <= along < 0.6 * min(em1, em2):
                abutting.append((s1[:48], s2[:48]))
    fb = fig.bbox
    outside = [b[0][:48] for b in boxes if b[1].x0 < fb.x0 - 1 or b[1].y0 < fb.y0 - 1 or b[1].x1 > fb.x1 + 1 or b[1].y1 > fb.y1 + 1]
    on_marker = []
    for x, y, own in points or []:
        for s_, bb, *_ in boxes:
            if s_ != own and bb.x0 - 2 <= x <= bb.x1 + 2 and bb.y0 - 2 <= y <= bb.y1 + 2:
                on_marker.append((s_[:48], own))
    through = []
    for t in fig.findobj(Text):
        own = t.get_text().strip()
        for px, py in (getattr(t, "_leader", None) or [])[:-2]:
            for s_, bb, *_ in boxes:
                if s_ != own and bb.x0 <= px <= bb.x1 and bb.y0 <= py <= bb.y1 and (own, s_[:48]) not in through:
                    through.append((own, s_[:48]))
    titles = sum(1 for ax in fig.axes if ax.get_title().strip()) + (1 if fig._suptitle is not None and fig._suptitle.get_text().strip() else 0)
    return {"pieces_of_text": len(boxes), "text_on_text": pairs, "text_abutting_text": abutting, "text_on_another_marker": on_marker, "leader_line_through_another_text": through,
            "titles_inside_the_image": titles, "text_outside_the_figure_before_trimming": outside}


def save(fig, name: str, rows: list[dict], cols: list[str], caption: str, sources: list[Path], points=None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lay = layout_check(fig, points)
    USED.setdefault("layout", {})[name] = lay
    print(f"layout {name}: {lay['pieces_of_text']} pieces of text; text on text: {lay['text_on_text']}; text end to end: {lay['text_abutting_text']}; text on another's marker: {lay['text_on_another_marker']}; "
          f"line through another text: {lay['leader_line_through_another_text']}; outside: {lay['text_outside_the_figure_before_trimming']}", flush=True)
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white", metadata={"Software": None})
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", facecolor="white", metadata={"Date": None, "Creator": None})
    plt.close(fig)
    G.write_rows(OUT / f"{name}.csv", rows, cols)
    text = caption.strip() + "\n\nSource files: " + "; ".join(f"`{G.rel(p)}`" for p in sources) + f".\nFont: {USED['font']['font']}." \
        + f"\nWhat is plotted, mark by mark: `figures/stage4/{name}.csv` ({len(rows)} rows)." \
        + f"\nLayout, as the script measures it: {lay['pieces_of_text']} pieces of text; pairs of text whose boxes overlap: {len(lay['text_on_text'])}; " \
        + f"pairs set end to end with less than a word's space between them: {len(lay['text_abutting_text'])}; " \
        + f"labels lying on another point's marker: {len(lay['text_on_another_marker'])}; leader lines running through another text: {len(lay['leader_line_through_another_text'])}. " \
        + "A script cannot judge whether a figure reads well: look at it before it is used." \
        + f"\nMade {G.utc_now()} by `scripts/make_stage4_figures.py`.\n"
    (OUT / f"{name}.caption.txt").write_text(text, encoding="utf-8")
    for ext in ("png", "svg", "csv", "caption.txt"):
        USED["files"][f"{name}.{ext}"] = sources
    print(f"wrote figures/stage4/{name}.png, .svg, .csv, .caption.txt", flush=True)


def pct(a: Decimal, b: Decimal) -> float:
    return float(Decimal(100) * a / b)


# ------------------------------------------------------------------------------------------------------------------ F1
def f1() -> None:
    src = G.IN["r620_state"]
    st = {}
    for r in G.read_rows(src):
        st.setdefault(r["fy"], {})[r["category"]] = r
    rows = []
    for fy in G.FY_ALL:
        x = st[fy]
        rows.append({"fy": G.fy_short(fy), "plantation_pct_of_all_expenditure": round(pct(D(x["Plantation"]["exp_cat_lakh"]), D(x["Plantation"]["exp_all_lakh"])), 4),
                     "water_pct_of_nrm_expenditure": round(pct(D(x["Water"]["exp_cat_lakh"]), D(x["NRM"]["exp_cat_lakh"])), 4),
                     "table_last_updated": x["Plantation"]["last_updated"], "frozen_2020_snapshot": 1 if x["Plantation"]["last_updated"] == G.FROZEN_STAMP else 0,
                     "part_year": 1 if fy == G.PART else 0})
    xs = list(range(len(rows)))
    fig, axes = plt.subplots(2, 1, figsize=(6.3, 5.0), sharex=True)
    for ax, key, label in ((axes[0], "plantation_pct_of_all_expenditure", "Plantation expenditure,\n% of all expenditure"),
                           (axes[1], "water_pct_of_nrm_expenditure", "Water expenditure,\n% of NRM expenditure")):
        ys = [r[key] for r in rows]
        frozen = [i for i, r in enumerate(rows) if r["frozen_2020_snapshot"]]
        ax.axvspan(min(frozen) - 0.5, max(frozen) + 0.5, color=LIGHT, lw=0, zorder=0)
        full = [i for i, r in enumerate(rows) if not r["part_year"]]
        ax.plot([xs[i] for i in full], [ys[i] for i in full], color=BLACK, lw=1.2, marker="o", ms=4, zorder=3)
        part = [i for i, r in enumerate(rows) if r["part_year"]]
        ax.plot([xs[full[-1]], xs[part[0]]], [ys[full[-1]], ys[part[0]]], color=BLACK, lw=1.0, ls=":", zorder=2)
        ax.plot([xs[i] for i in part], [ys[i] for i in part], ls="none", marker="o", ms=5, mfc="white", mec=BLACK, zorder=4)
        top = max(ys) * 1.22
        ax.set_ylim(0, top)
        ax.set_ylabel(label)
        ax.text((min(frozen) + max(frozen)) / 2, top * 0.98, f"tables frozen on {G.FROZEN_STAMP}", ha="center", va="top", fontsize=8, color=DARK)
        ax.annotate("part year", (xs[part[0]], ys[part[0]]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8, color=DARK)
        ax.text(0.995, 0.55 if key.startswith("plantation") else 0.08, f"n = {len(rows)} financial years; state totals as the report prints them",
                transform=ax.transAxes, ha="right", va="center", fontsize=8, color=DARK)
    axes[1].set_xticks(xs)
    axes[1].set_xticklabels([r["fy"] for r in rows], rotation=45, ha="right")
    axes[1].set_xlabel("Financial year (MIS report R6.20, Odisha)")
    fig.align_ylabels(axes)
    save(fig, "F1_state_report", rows, list(rows[0].keys()),
         "F1. The state report. Upper panel: plantation expenditure as a share of all MGNREGA expenditure in Odisha. Lower panel: water expenditure as a "
         "share of natural-resource (NRM) expenditure. The three categories of the report are nested (water and plantation both lie inside NRM), so they are "
         "drawn in separate panels and never stacked. The shaded years are the four whose tables carry the stamp 10/10/2020: a snapshot frozen in 2020. The "
         f"open marker is FY2026-27, a part year, not comparable with a full year. n = {len(rows)} financial years; each point is a state total as the report "
         "prints it (30 districts). The figure describes the record; it does not say why plantation fell.", [src])


# ------------------------------------------------------------------------------------------------------------------ F2
def f2() -> None:
    import pyogrio
    units = pyogrio.read_dataframe(G.IN["units_gpkg"], read_geometry=False)
    area = {str(u.unit_id): Decimal(str(u.area_ha)) for u in units.itertuples(index=False)}
    kind = {r["unit_id"]: ("outside-village units" if r["outside_village"] == "1" else "LGD panchayat units") for r in G.read_rows(G.OUT / "unit_district.csv")}
    cond = G.read_rows(G.IN["condition_by_unit"])
    need = {r["unit_id"]: r for r in G.read_rows(G.IN["need_by_unit"])}
    alloc = {r["unit_id"]: r for r in G.read_rows(G.IN["allocation_by_unit"])}
    measures = [("Land", "area, ha", lambda u, c: area[u], "10_units/units.gpkg: area_ha"),
                ("Forest in 2000\n(canopy above 10 %)", "ha", lambda u, c: D(c["dense_2000_ha"]) + D(c["open_2000_ha"]), "55_decision/condition_by_unit.csv: dense_2000_ha + open_2000_ha"),
                ("Forest loss\n2001-2025", "ha", lambda u, c: D(c["forest_loss_ha_2001_2025"]), "55_decision/condition_by_unit.csv: forest_loss_ha_2001_2025"),
                ("Census population\n(2011)", "people", lambda u, c: Decimal(need[u]["population"] or 0), "30_need/need_by_unit.csv: population (no row for outside-village land)"),
                ("Expenditure in the\ngeotagged record", "rupees", lambda u, c: G.money(alloc[u]["expenditure_total"]), "40_allocation/allocation_by_unit.csv: expenditure_total")]
    kinds = ["LGD panchayat units", "outside-village units"]
    n_units = {k: sum(1 for v in kind.values() if v == k) for k in kinds}
    rows = []
    for label, unit, fn, source in measures:
        tot = {k: Decimal(0) for k in kinds}
        for c in cond:
            tot[kind[c["unit_id"]]] += fn(c["unit_id"], c)
        for k in kinds:
            rows.append({"measure": label.replace("\n", " "), "unit_of_the_sum": unit, "kind_of_unit": k, "n_units": n_units[k], "sum": tot[k],
                         "share_pct": round(pct(tot[k], tot[kinds[0]] + tot[kinds[1]]), 4), "read_from": source})
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    h = 0.36
    for j, (label, *_rest) in enumerate(measures):
        for i, k in enumerate(kinds):
            r = next(x for x in rows if x["measure"] == label.replace("\n", " ") and x["kind_of_unit"] == k)
            y = j + (h / 2 if i else -h / 2)
            ax.barh(y, r["share_pct"], height=h, color=DARK if i == 0 else "white", edgecolor=BLACK, linewidth=0.6, hatch=None if i == 0 else "////")
            note = f"{r['share_pct']:.1f}"
            if label.startswith("Census") and i == 1:
                note = "no census rows for this land"
            ax.text(r["share_pct"] + 1.2, y, note, va="center", ha="left", fontsize=8)
    ax.set_yticks(range(len(measures)))
    ax.set_yticklabels([m[0] for m in measures])
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("Share of the total over all units, %")
    ax.legend(handles=[Patch(facecolor=DARK, edgecolor=BLACK, label=f"LGD panchayat units (n = {n_units[kinds[0]]:,})"),
                       Patch(facecolor="white", edgecolor=BLACK, hatch="////", label=f"outside-village units (n = {n_units[kinds[1]]:,})")],
              loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False, ncol=2)
    save(fig, "F2_outside_village_asymmetry", rows, list(rows[0].keys()),
         "F2. The outside-village asymmetry. For each of five totals over the units, the share held by LGD panchayat units and by outside-village units (land "
         f"in no revenue village). n = {n_units[kinds[0]]:,} LGD panchayat units and {n_units[kinds[1]]:,} outside-village units; the two shares of a row add to "
         "100. The census has no row for outside-village land, so its population share is not a measured zero. Expenditure is that of the geotagged record of "
         "works, placed where a work lies; the works that fall in no unit are in neither bar. Forest is Hansen canopy above 10 per cent in 2000 (dense and open "
         "band); loss is Hansen tree-cover loss on it, which is not degradation and does not see thinning.",
         [G.IN["units_gpkg"], G.OUT / "unit_district.csv", G.IN["condition_by_unit"], G.IN["need_by_unit"], G.IN["allocation_by_unit"]])


# ------------------------------------------------------------------------------------------------------------------ F3
LABEL_ORDERS_TRIED = 400                                       # F4: how many orders of placing the names are tried; the tightest arrangement is kept
CLEAR_OF_MARKER = 9                                            # F4: display units a name at the end of a line keeps from every marker that is not its own
MIN_RING_KM2 = 25                                              # a drawing choice of F3: smaller rings of a district's boundary are not drawn
SCALE_BAR_KM = 100


def f3() -> None:
    import geopandas as gpd
    gdf = gpd.read_file(G.IN["units_gpkg"])
    gdf["unit_id"] = gdf["unit_id"].astype(str)
    cond = {r["unit_id"]: r for r in G.read_rows(G.IN["condition_by_unit"])}
    tiers = G.read_rows(G.IN["tiers"])
    names = {r["cell"]: r["cell_name"] for r in tiers}
    order = [r["cell"] for r in sorted(tiers, key=lambda r: (r["tier"] == "", r["tier"]))]
    if set(gdf["unit_id"]) != set(cond) or set(order) != set(MAP_COLOURS):
        G.stop("the unit shapes and the decision table do not hold the same units, or the cells are not the six expected")
    gdf["cell"] = [cond[u]["cell_2018_2025"] for u in gdf["unit_id"]]
    gdf["district"] = [cond[u]["district"] for u in gdf["unit_id"]]
    proj = gdf.to_crs(32645)                                    # UTM 45N, for drawing only: no area is reported from it
    districts = proj[["district", "geometry"]].dissolve(by="district")
    proj["geometry"] = proj.geometry.simplify(60, preserve_topology=True)
    districts["geometry"] = districts.geometry.simplify(60, preserve_topology=True)
    # A dissolved district is one large piece and, often, small ones: a few units of the district lying inside another
    # (most of them outside-village units, whose district is assigned), and small gaps between units. Drawn, each is a
    # ring a few millimetres across. Rings that enclose less than MIN_RING_KM2 are left out of the boundary lines; the
    # units inside them keep their colour.
    from shapely.geometry import Polygon
    rings, small_rings = [], 0
    for geom in districts.geometry:
        for part in (list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]):
            for ring in [part.exterior] + list(part.interiors):
                if Polygon(ring).area / 1e6 >= MIN_RING_KM2:
                    rings.append(ring)
                else:
                    small_rings += 1
    fig, ax = plt.subplots(figsize=(6.3, 6.6))
    for cell in order:
        sub = proj[proj["cell"] == cell]
        sub.plot(ax=ax, color=MAP_COLOURS[cell], edgecolor="none", linewidth=0, rasterized=True)
    gpd.GeoSeries(rings, crs=districts.crs).plot(ax=ax, color=BLACK, linewidth=0.45)
    ax.set_axis_off()
    ax.set_aspect("equal")
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bx, by = x1 - 0.04 * (x1 - x0) - SCALE_BAR_KM * 1000, y0 + 0.06 * (y1 - y0)
    ax.plot([bx, bx + SCALE_BAR_KM * 1000], [by, by], color=BLACK, lw=1.2, solid_capstyle="butt")
    for e in (bx, bx + SCALE_BAR_KM * 1000):
        ax.plot([e, e], [by, by + 0.008 * (y1 - y0)], color=BLACK, lw=1.0)
    ax.text(bx + SCALE_BAR_KM * 500, by + 0.014 * (y1 - y0), f"{SCALE_BAR_KM} km", ha="center", va="bottom", fontsize=8, color=DARK)
    counts = {c: int((gdf["cell"] == c).sum()) for c in order}
    ax.legend(handles=[Patch(facecolor=MAP_COLOURS[c], edgecolor=DARK, linewidth=0.4, label=f"{names[c]} (n = {counts[c]:,})") for c in order] +
                      [Line2D([0], [0], color=BLACK, lw=0.6, label=f"district boundary, made by dissolving the units (n = {len(districts)} districts)")],
              loc="upper center", bbox_to_anchor=(0.5, 0.02), frameon=False, ncol=1, handlelength=1.4)
    ax.text(0.0, 1.0, f"n = {len(gdf):,} units", transform=ax.transAxes, ha="left", va="top", fontsize=8, color=DARK)
    rows = [{"unit_id": u, "pc11_district_code": cond[u]["pc11_district_code"], "district": cond[u]["district"], "outside_village": cond[u]["outside_village"],
             "cell_2018_2025": cond[u]["cell_2018_2025"], "cell_name": names[cond[u]["cell_2018_2025"]], "colour": MAP_COLOURS[cond[u]["cell_2018_2025"]]}
            for u in sorted(cond)]
    save(fig, "F3_map_of_cells", rows, list(rows[0].keys()),
         f"F3. The six cells of the decision table, window 2018-2025, for every unit of Odisha (n = {len(gdf):,} units). A cell is set by the forest of 2000 with no loss "
         "recorded since (mostly closed, mostly open, or under 10 ha) and by whether 1 ha or more of forest loss is recorded in the window. The names are the "
         "layer's own. Units per cell: " + "; ".join(f"{names[c]}: {counts[c]:,}" for c in order) + f". District boundaries ({len(districts)}) are made by "
         "dissolving the units; the district of an outside-village unit is assigned, not surveyed. A dissolved district has small pieces lying inside its "
         f"neighbours and small gaps; the {small_rings} rings of boundary that enclose less than {MIN_RING_KM2} square kilometres are not drawn (the units inside them keep "
         f"their colour). The bar is {SCALE_BAR_KM} km on the map's projection (UTM zone 45N). The palette is Okabe and Ito's, chosen to be told apart with "
         "colour-blind vision; this is the one figure not made for greyscale. Shapes are simplified for drawing (60 m) and no area is read from them. A cell is "
         "a summary of Hansen's hectares in a unit: it is not a ranking of units across the state.",
         [G.IN["units_gpkg"], G.IN["condition_by_unit"], G.IN["tiers"]])


def place_labels_among(fig, ax, pts, n_named, keep_clear):
    """Name the first `n_named` of the points `pts` [(x, y, name)] on `ax`.

    The rules a place must keep: the name sits on no other name, on no text of `keep_clear` and on no marker but its
    own (named or not); it keeps most of a letter's height from the next text on its line; it lies inside the axes. A
    name set away from its point gets a thin line back to it, which may not run through another name or marker nor
    cross another line; such a name keeps a line's height clear of every marker that is not its own. A name
    beside its point gets no line, and is allowed there only where every other marker is clearly farther from it than
    its own, so that it cannot be taken for a neighbour's.

    Each name has a ring of candidate places round its point. Names are placed one after another, each taking the
    nearest place the rules allow; the result depends on the order, so many orders are tried (the most hemmed-in
    points first, then shuffles from a fixed seed) and the arrangement kept is the one with no name unplaced and the
    shortest lines. The boxes are worked out from each name's measured width and height, and the annotations are drawn
    once, at the end. Returns the names for which no place was found."""
    import math
    import random
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    px = fig.dpi / 72.0
    marks = [tuple(m) for m in ax.transData.transform([(x, y) for x, y, _ in pts])] if pts else []
    pts = pts[:n_named]
    fixed = [t.get_window_extent(r) for t in keep_clear]
    fixed = [(b.x0, b.y0, b.x1, b.y1) for b in fixed]
    ins = ax.get_window_extent(r)
    size = {}
    for _, _, name in pts:                                        # the width and height of each name as drawn
        probe = ax.text(0, 0, name, fontsize=7)
        bb = probe.get_window_extent(r)
        size[name] = (bb.width, bb.height)
        probe.remove()
    gap_x, gap_y = 0.8 * 7 * px, 0.15 * 7 * px                    # a name keeps this far from another text: most of a letter's height along the line
    ring = [(5, 3, "left", "bottom"), (5, -3, "left", "top"), (-5, 3, "right", "bottom"), (-5, -3, "right", "top"), (0, 6, "center", "bottom"), (0, -6, "center", "top")]
    for d in (10, 13, 16, 20, 24, 29, 35, 42, 50, 59, 69, 80, 92, 105, 119, 134):      # rings of growing radius, forty-eight directions each
        for k in range(48):
            ang = math.radians(7.5 * k + 3.75)
            dx, dy = d * math.cos(ang), d * math.sin(ang)
            ring.append((dx, dy, "left" if dx > 0 else "right", "bottom" if dy > 0 else "top"))

    def box(k, c):                                                # the name's box at candidate place c, in display units
        dx, dy, ha, va = c
        w, h = size[pts[k][2]]
        ax_, ay_ = marks[k][0] + dx * px, marks[k][1] + dy * px
        x0 = ax_ if ha == "left" else (ax_ - w if ha == "right" else ax_ - w / 2)
        y0 = ay_ if va == "bottom" else ay_ - h
        return (x0, y0, x0 + w, y0 + h)

    def leader(m, b, n=24):                                       # points along the line from a marker to the nearest edge of its name
        ex, ey = min(max(m[0], b[0]), b[2]), min(max(m[1], b[1]), b[3])
        return [(m[0] + (ex - m[0]) * i / n, m[1] + (ey - m[1]) * i / n) for i in range(n + 1)]

    away = lambda m, b: math.hypot(max(b[0] - m[0], 0, m[0] - b[2]), max(b[1] - m[1], 0, m[1] - b[3]))
    turn = lambda a_, b_, c_: (b_[0] - a_[0]) * (c_[1] - a_[1]) - (b_[1] - a_[1]) * (c_[0] - a_[0])
    crosses = lambda p1, p2, p3, p4: turn(p1, p2, p3) * turn(p1, p2, p4) < 0 and turn(p3, p4, p1) * turn(p3, p4, p2) < 0
    near_text = lambda a, b: a[0] - gap_x < b[2] and b[0] < a[2] + gap_x and a[1] - gap_y < b[3] and b[1] < a[3] + gap_y

    # what does not depend on the other names is settled once for every candidate
    allowed = {}
    for k in range(len(pts)):
        ok = []
        for c in ring:
            b = box(k, c)
            far = max(abs(c[0]), abs(c[1])) > 8
            if not (b[0] >= ins.x0 and b[2] <= ins.x1 and b[1] >= ins.y0 and b[3] <= ins.y1):
                continue
            if any(near_text(b, f) for f in fixed) or any(j != k and away(m, b) <= (CLEAR_OF_MARKER if far else 3) for j, m in enumerate(marks)):
                continue                                          # a name at the end of a line keeps a line's height clear of every other marker
            line = leader(marks[k], b) if far else []
            if any(f[0] <= x_ <= f[2] and f[1] <= y_ <= f[3] for x_, y_ in line for f in fixed):
                continue
            if any(j != k and math.hypot(x_ - m[0], y_ - m[1]) < 5 for x_, y_ in line[2:] for j, m in enumerate(marks)):
                continue
            if not far:
                own = away(marks[k], b)
                if any(j != k and away(m, b) < max(1.6 * own, own + 5) for j, m in enumerate(marks)):
                    continue
            ok.append((c, b, line, math.hypot(c[0], c[1]) if far else 0.0))
        allowed[k] = ok

    def arrange(order):
        placed, cost, failed = {}, 0.0, []
        for k in order:
            for c, b, line, length in allowed[k]:
                if any(near_text(b, pb) for _, pb, _ in placed.values()):
                    continue
                if any(pb[0] <= x_ <= pb[2] and pb[1] <= y_ <= pb[3] for x_, y_ in line for _, pb, _ in placed.values()):
                    continue                                      # this name's line would run through a name already placed
                if any(b[0] <= x_ <= b[2] and b[1] <= y_ <= b[3] for _, _, pl in placed.values() for x_, y_ in pl):
                    continue                                      # this name would sit on a line already drawn
                if line and any(pl and crosses(line[0], line[-1], pl[0], pl[-1]) for _, _, pl in placed.values()):
                    continue                                      # two lines would cross
                placed[k] = (c, b, line)
                cost += length ** 2
                break
            else:
                failed.append(k)
        return failed, cost, placed

    crowd = lambda k: sum(1 for j, m in enumerate(marks) if j != k and abs(m[0] - marks[k][0]) < 30 and abs(m[1] - marks[k][1]) < 30)
    orders = [sorted(range(len(pts)), key=lambda k: (-crowd(k), -(pts[k][0] + pts[k][1])))]
    rng = random.Random(20261010)
    for _ in range(LABEL_ORDERS_TRIED - 1):
        o = list(range(len(pts)))
        rng.shuffle(o)
        orders.append(o)
    best = min((arrange(o) for o in orders), key=lambda res: (len(res[0]), res[1]))
    failed, _, placed = best
    for k, (x, y, name) in enumerate(pts):
        if k in placed:
            (dx, dy, ha, va), _, line = placed[k]
            far = max(abs(dx), abs(dy)) > 8
            a = ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx, dy), ha=ha, va=va, fontsize=7, color=BLACK,
                            arrowprops=dict(arrowstyle="-", lw=0.4, color=MID, shrinkA=0, shrinkB=2) if far else None)
            a._leader = line
        else:
            ax.annotate(name, (x, y), textcoords="offset points", xytext=(5, 3), fontsize=7, color=BLACK)
    return [pts[k][2] for k in failed]


# ------------------------------------------------------------------------------------------------------------------ F4
def f4() -> None:
    long = G.read_rows(G.OUT / "need_vs_allocation.csv")
    summ = {r["comparison"]: r for r in G.read_rows(G.OUT / "need_vs_allocation_summary.csv")}
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.9))
    panels = (("C1", "Share of post-period plantation money\n(R6.20, FY2018-19 to 2025-26), %"),
              ("C5", "Share of pre-period plantation money\n(R6.20, FY2014-15 to 2017-18; frozen 2020 snapshot), %"))
    unlabelled, to_name, clear, marks, not_placed = {}, {}, {}, [], []
    for ax, (cid, ylabel) in zip(axes, panels):
        pts = [r for r in long if r["comparison"] == cid]
        xs, ys = [float(r["need_share_pct"]) for r in pts], [float(r["allocation_share_pct"]) for r in pts]
        top = max(xs + ys) * 1.12
        ax.plot([0, top], [0, top], color=MID, lw=0.8, ls="--", zorder=1)
        eq = ax.text(top * 0.99, top * 0.955, "equal shares", rotation=45, ha="right", va="top", fontsize=8, color=DARK)
        ax.scatter(xs, ys, s=16, facecolor="white", edgecolor=BLACK, linewidth=0.8, zorder=3)
        unlabelled[cid], to_name[cid] = [], []
        for r, x, y in zip(pts, xs, ys):
            lab = x >= 3 or y >= 3
            (to_name[cid] if lab else unlabelled[cid]).append((x, y, r["district_name"]))
            rows.append({"panel": cid, "pc11_district_code": r["pc11_district_code"], "district_name": r["district_name"], "need_share_pct": round(x, 4),
                         "allocation_share_pct": round(y, 4), "labelled_on_the_figure": "yes" if lab else "no"})
        unlabelled[cid] = [n for _, _, n in unlabelled[cid]]
        ax.set_xlim(-0.8, top)
        ax.set_ylim(-0.8, top)
        ax.set_aspect("equal")
        ax.set_xlabel("Share of need: forest loss 2018-2025 in units\nwith loss recorded (N1), %")
        ax.set_ylabel(ylabel)
        s = summ[cid]
        note = ax.text(0.03, 0.97, f"{cid}   n = {len(pts)} districts\nSpearman's rho = {float(s['rho']):.2f}", transform=ax.transAxes, ha="left", va="top", fontsize=8)
        clear[cid] = [eq, note]
    fig.tight_layout(w_pad=2.0)
    for ax, (cid, _) in zip(axes, panels):                       # names are placed once the panels have their final size
        all_pts = [(float(r["need_share_pct"]), float(r["allocation_share_pct"]), r["district_name"]) for r in long if r["comparison"] == cid]
        names = {n for _, _, n in to_name[cid]}
        ordered = [p for p in all_pts if p[2] in names] + [p for p in all_pts if p[2] not in names]
        not_placed += [f"{cid}: {n}" for n in place_labels_among(fig, ax, ordered, len(names), clear[cid])]
        marks += [(*ax.transData.transform((x, y)), n) for x, y, n in ordered[:len(names)]]
    if not_placed:
        print("F4: no clear place was found for " + ", ".join(not_placed), flush=True)
    c1, c5 = summ["C1"], summ["C5"]
    save(fig, "F4_need_share_against_money_share", rows, list(rows[0].keys()),
         "F4. Each district's share of need against its share of plantation money. Need (N1) is forest loss in 2018-2025 summed over the units in which 1 ha or "
         "more of loss is recorded. Left (C1): the share of R6.20 plantation expenditure of FY2018-19 to 2025-26. Right (C5): the share of FY2014-15 to 2017-18, "
         "four years whose tables are a snapshot frozen on 10/10/2020. The dashed line is equal shares: a district below it has a smaller share of the money "
         f"than of the need. n = 30 districts in each panel. Spearman's rho, C1: {float(c1['rho']):.2f} (95 % bootstrap interval {float(c1['ci95_lo']):.2f} to "
         f"{float(c1['ci95_hi']):.2f}; permutation p = {float(c1['p_permutation']):.5f}); C5: {float(c5['rho']):.2f} ({float(c5['ci95_lo']):.2f} to "
         f"{float(c5['ci95_hi']):.2f}; p = {float(c5['p_permutation']):.5f}). Districts are named where either share is 3 per cent or more. Not named, left panel: "
         + ", ".join(sorted(unlabelled["C1"])) + ". Not named, right panel: " + ", ".join(sorted(unlabelled["C5"])) + ". Hectares of Hansen loss by district are a "
         "measured quantity, not a ranking of units; they do not tell plantation harvest from the loss of natural forest. Plantation is the scheme's label and is "
         "not specific to forest. The figure shows where money went relative to where loss was recorded, not why.",
         [G.OUT / "need_vs_allocation.csv", G.OUT / "need_vs_allocation_summary.csv"], points=marks)


# ------------------------------------------------------------------------------------------------------------------ F5
def f5() -> None:
    split = [r for r in G.read_rows(G.OUT / "marginalisation_split.csv") if r["comparison"] == "C1" and r["grouping"] in ("st_class", "adi_tercile")]
    adi_source = next(r["note"] for r in split if r["grouping"] == "adi_tercile").split("; ", 1)[1]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7), sharey=True, gridspec_kw={"width_ratios": [4, 3]})
    rows = []
    for ax, (grouping, xlabel) in zip(axes, (("st_class", "Scheduled Tribe share of the district's population\n(LGD panchayat units, Census 2011)"),
                                             ("adi_tercile", "Tercile of the development index of 2011\n(higher is more developed)"))):
        g = [r for r in split if r["grouping"] == grouping]
        w = 0.38
        for i, r in enumerate(g):
            ns, as_ = float(r["need_share_pct"]), float(r["allocation_share_pct"])
            ax.bar(i - w / 2, ns, width=w, color=DARK, edgecolor=BLACK, linewidth=0.6)
            ax.bar(i + w / 2, as_, width=w, color="white", edgecolor=BLACK, linewidth=0.6, hatch="////")
            ax.text(i - w / 2, ns + 1, f"{ns:.1f}", ha="center", va="bottom", fontsize=8)
            ax.text(i + w / 2, as_ + 1, f"{as_:.1f}", ha="center", va="bottom", fontsize=8)
            rows.append({"panel": grouping, "class": r["class"], "n_districts": int(r["n_districts"]), "need_share_pct": round(ns, 4), "allocation_share_pct": round(as_, 4)})
        ax.set_xticks(range(len(g)))
        ax.set_xticklabels([f"{r['class']}\n(n = {r['n_districts']})" for r in g], fontsize=7.5)
        ax.set_xlabel(xlabel)
        ax.text(0.02, 0.98, f"n = {sum(int(r['n_districts']) for r in g)} districts", transform=ax.transAxes, ha="left", va="top", fontsize=8, color=DARK)
    top = max(max(r["need_share_pct"], r["allocation_share_pct"]) for r in rows)
    axes[0].set_ylim(0, top * 1.22)
    axes[0].set_ylabel("Share of the state total, %")
    fig.legend(handles=[Patch(facecolor=DARK, edgecolor=BLACK, label="need: forest loss 2018-2025 in units with loss recorded (N1)"),
                        Patch(facecolor="white", edgecolor=BLACK, hatch="////", label="allocation: R6.20 plantation expenditure, FY2018-19 to 2025-26")],
               loc="lower center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=1)
    fig.tight_layout()
    save(fig, "F5_need_and_money_by_marginalisation", rows, list(rows[0].keys()),
         "F5. Need share beside allocation share (comparison C1), with the 30 districts grouped by Scheduled Tribe share of population (left) and by tercile of "
         "the development index of 2011 (right; ten districts in each tercile; higher is more developed). A bar is the sum, over the districts of the class, of "
         "their shares of the state's need and of the state's post-period plantation money; the bars of a kind add to 100 across a panel. The classes rest on "
         "the Census 2011 population of LGD panchayat units only: outside-village land has no census rows, although much of the need lies on it. The classes "
         "split the comparison; they do not weight it. n = 30 districts in each panel, with the number in each class under it. " + adi_source,
         [G.OUT / "marginalisation_split.csv"])


# ------------------------------------------------------------------------------------------------------------------ F6
def f6() -> None:
    pm = G.read_rows(G.OUT / "panel_models.csv")
    um = G.read_rows(G.OUT / "unit_history_models.csv")
    U = {r["id"]: r for r in um}

    def urow(i):
        r = U[i]
        return {"id": i, "label": f"{i}  (n = {int(r['n_units']):,} units, {int(r['n_exposed']):,} exposed)", "b": r["coefficient"], "lo": r["wcb_ci95_lo"],
                "hi": r["wcb_ci95_hi"], "headline": r["headline"], "p": r["wcb_p"]}

    def prow(r):
        tag = r["id"] + (" x post" if r["term"].endswith("_x_post") else "")
        return {"id": tag, "label": f"{tag}  (n = {r['n']} district-years)", "b": r["coefficient"], "lo": r["wcb_ci95_lo"], "hi": r["wcb_ci95_hi"],
                "headline": r["headline"] if not r["term"].endswith("_x_post") else "no", "p": r["wcb_p"]}

    P = lambda ids: [prow(r) for r in pm if r["id"] in ids]
    panels = [
        ("Units within districts: forest lost 2018-2025, percentage points of the forest\nat the start of 2018, exposed unit against unexposed", [urow(i) for i in ("H1", "H2", "H3", "H4", "H5", "H7")]),
        ("The same outcome, per unit of asinh(forest-named rupees per ha)", [urow("H6")]),
        ("Probability that loss is recorded (0 to 1), exposed unit against unexposed", [urow("H8")]),
        ("CoRE Stack downward share 2017-2023, percentage points,\nexposed unit against unexposed", [urow("H9")]),
        ("District-years: plantation's share of the district's expenditure,\npercentage points per 100 ha of forest loss", P(("P1", "P2", "P4", "P6", "P7"))),
        ("asinh(plantation, lakh rupees) per 100 ha of forest loss in the year before", P(("P3",))),
        ("Plantation's share, percentage points, per percentage point of standing forest\nlost in the year before", P(("P5",))),
    ]
    heights = [max(len(rows), 1) + 1.8 for _, rows in panels]
    fig, axes = plt.subplots(len(panels), 1, figsize=(6.6, 0.25 * sum(heights) + 1.7), gridspec_kw={"height_ratios": heights})
    out = []
    for k, (ax, (title, rows)) in enumerate(zip(axes, panels)):
        vals = []
        for j, r in enumerate(rows):
            b = float(r["b"])
            lo = None if r["lo"] == "" else float(r["lo"])
            hi = None if r["hi"] == "" else float(r["hi"])
            vals += [v for v in (b, lo, hi) if v is not None]
            head = r["headline"] == "yes"
            if lo is not None and hi is not None:
                ax.plot([lo, hi], [j, j], color=BLACK, lw=1.6 if head else 1.0, solid_capstyle="butt", zorder=2)
                for e in (lo, hi):
                    ax.plot([e, e], [j - 0.16, j + 0.16], color=BLACK, lw=1.0, zorder=2)
            ax.plot([b], [j], marker="D" if head else "o", ms=6 if head else 4.5, mfc=BLACK if head else "white", mec=BLACK, mew=1.0, ls="none", zorder=3)
            out.append({"panel": k + 1, "panel_unit": title.replace("\n", " "), "id": r["id"], "headline": "yes" if head else "no", "coefficient": b,
                        "wcb_ci95_lo": lo, "wcb_ci95_hi": hi, "wcb_p": float(r["p"]), "label": r["label"],
                        "interval_unbounded": "yes" if lo is None or hi is None else "no"})
        ax.axvline(0, color=MID, lw=0.8, ls="--", zorder=1)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([r["label"] + ("  - headline" if r["headline"] == "yes" else "") for r in rows])
        ax.set_ylim(len(rows) - 0.4, -0.6)
        span = max(abs(v) for v in vals) or 1.0
        ax.set_xlim(-1.15 * span if min(vals) < 0 else -0.15 * span, 1.15 * span if max(vals) > 0 else 0.15 * span)
        ax.set_xlabel(title)
        ax.tick_params(axis="y", length=0)
    fig.tight_layout(h_pad=0.8)
    unb = [r["id"] for r in out if r["interval_unbounded"] == "yes"]
    save(fig, "F6_estimates_with_wild_bootstrap_intervals", out, list(out[0].keys()),
         "F6. The estimates of the unit models (H1 to H9) and of the district-year models (P1 to P7), each with its 95 % interval from a restricted wild "
         "cluster bootstrap (districts as clusters, Webb weights), found by test inversion. One panel for each unit of measurement, so that no two units share "
         "an axis; the axis title of a panel gives its unit. The filled diamonds are the headline rows, H1 and P1; the dashed line is zero. n is given beside "
         "each row, in units (with the number exposed) or in district-years: " + "; ".join(r["label"].replace("  (n = ", ": n = ").rstrip(")") for r in out) + ". "
         "P7 has two terms, the loss and its product with the post period. "
         + ("An interval with no bar was unbounded on a side: " + ", ".join(unb) + ". " if unb else "") +
         "H rows compare, within a district, units that had forest-named works by FY2017-18 with units that had none (H7: plantation-category works), given "
         "their forest and earlier loss: an association, and selection is likely. P rows ask whether, within a district and a period, years after more loss "
         "had more plantation spending. None is an effect.", [G.OUT / "panel_models.csv", G.OUT / "unit_history_models.csv"])


def main() -> None:
    G.require_stage4_environment()
    style()
    USED["font"] = choose_font()
    which = [a.upper() for a in sys.argv[1:]] or ["F1", "F2", "F3", "F4", "F5", "F6"]
    todo = {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5, "F6": f6}
    for w in which:
        todo[w]()
    outputs = sorted(p for p in OUT.glob("F*.*"))
    record = {"script": "scripts/make_stage4_figures.py", "script_sha256": G.sha256(Path(__file__)), "run_utc": G.utc_now(), "figures_made_in_this_run": which,
              "font": USED["font"], "matplotlib": matplotlib.__version__, "dpi_of_png": 300, "layout_checked_by_the_script": USED.get("layout", {}),
              "inputs": {G.rel(p): {"bytes": p.stat().st_size, "sha256": G.sha256(p)} for p in sorted({s for v in USED["files"].values() for s in v})},
              "outputs": {G.rel(p): {"bytes": p.stat().st_size, "sha256": G.sha256(p)} for p in outputs}}
    (OUT / "figures.provenance.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(f"font: {USED['font']['font']}; {len(outputs)} files in figures/stage4/")


if __name__ == "__main__":
    main()
