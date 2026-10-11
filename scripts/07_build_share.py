#!/usr/bin/env python3
"""The copy of the layer that is published: the two files of 60_layer/ WITHOUT the map overlay (its file is left out and
its box is greyed out) and WITHOUT the development index of 2011 (the field adi_2011 and everything that displays it); in
all else the layer's own content.

    python scripts/07_build_share.py

THE OVERLAY IN THE COPY: THE OWNER'S RULING OF 11 OCTOBER 2026. It replaces the words of his gate of 9 October 2026 on the
overlay. Two points of the tile provider's terms of use are unresolved, so:
  - in the copy the overlay's box is greyed out and cannot be ticked;
  - it says that it is not in this copy, in his words (`OVERLAY_UNAVAILABLE` below);
  - the page asks for no overlay.js at all;
  - the copy still carries no code that can ask the provider's server for anything: overlay.js is not in it;
  - in the copy's data, `decision.overlay` holds only `available` (0), `label` and `unavailable`.
The full layer in 60_layer/ is not changed by this: its box works as before.
(Until 11 October the copy's page was the layer's own, box and all: the box could be ticked, the page then asked for an
overlay.js that was not there, unticked the box and said so. On the published site that was a request for a missing
file, and the About text described an overlay the copy did not have.)
What is changed in the copy for the overlay, and nothing else:
  data.js     `decision.overlay` (as above: the layer's own label; its other words go); the paragraph of the About text
              on the overlay, replaced by the owner's paragraph for the copy; the overlay's row of "Sources", whose
              first and last cells get his words for the copy
  index.html  nothing: the page is the layer's page. Its one line that could ask for overlay.js is never reached,
              because a box that is not available is written disabled and the function returns before that line.

Why no development index (10 October 2026; a reversible call, recorded in docs/DECISION_LAYER.md section 17). No file
that is passed on carries unit-level adi_2011 values. The exported list already leaves the index out because it is
passed on; this copy is passed on too. 60_layer/ keeps the index. What is taken out of the copy, and nothing else:
  data.js     the layer whose id is adi_2011 (its legend, its class of every unit, its counts); the index's value in
              every unit's row of fields, and that field's line in the unit panel; the clause of that panel's note that
              names the index's makers; the field's entry in the decision view's list (the column head and the name of
              the field); three places of the About text that speak of it (one of them only a plural: one census layer
              is left); the index's row of "Sources"
  index.html  the one cell of the ranked list's row that printed the index
Each is found exactly once or the run stops, and the run stops if "adi_2011", the layer's title, the list's column
head or the words "development index" in any case are still in either file. The README says the index is not in
this copy.

In      60_layer/index.html, 60_layer/data.js      read, and written again without the development index and with the
                                                   overlay switched off
        60_layer/layer.provenance.json             the build they are of: its time, the two hashes it records, and the
                                                   overlay's provider, credit and terms as that build registered them
Out     70_share/ and nowhere else:
        odisha_forest_decision_layer/index.html, data.js, README.txt      the copy: these three files and no other
        odisha_forest_decision_layer.zip                                  a zip of that folder, beside it
        share.provenance.json                                             this run: inputs with sha256, the UTC time, the checks
        (The owner's words were "new folder 70_share/: index.html and data.js ... plus a short README.txt ... a zip of the
        folder beside it". The three files are one level down, in a folder of their own, so that the zip can lie beside
        the folder it is a zip of and still be inside the one numbered folder this script may write to; and so that this
        run's record is not among the files passed on.)

README.txt, in the owner's words of 11 October 2026: where the copy is online and how to open it, what it shows and what
it isn't, what is left out of this copy (the loss-pixel overlay; "The development index is not in this copy", a sentence
stage 4's gate on the leftovers reads), whose data it draws on (the rows of the page's own "Sources", read from the
copy's data.js, not typed here), and that the owner publishes it at `PUBLISHED_AT`, each source under its own licence.
Every figure in it is read from data.js. Its sentence on phones (`PHONES`) says what was tried and what was seen.

What is checked here, and the run stops (nothing left in place) if one fails:
  - the two files in 60_layer/ are the ones the layer's run record describes (sha256);
  - written again untouched, the layer's data.js gives back its own bytes (so every byte that was not changed is the
    layer's); with the development index taken out, the copy's two files name it nowhere;
  - the overlay's paragraph of the About text and its row of "Sources" are each found exactly once, and the row's
    cells carry the credit and the terms the layer's record registered;
  - in the copy's data the overlay holds exactly `available` 0, `label` and `unavailable`;
  - the copy holds exactly three files and none is overlay.js;
  - the zip holds exactly those three files under the folder's name, and each unpacks to the bytes of the file on disk.
What is NOT checked here: that a browser opens the copy, shows the overlay's box greyed out and unticked with the
owner's words beside it, and asks for no overlay.js and nothing from the network. That is scripts/exercise_share.py,
which opens the copy in Chrome and writes its record into 70_share/.
"""
import datetime, hashlib, html, json, re, shutil, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "60_layer", ROOT / "70_share"
NAME = "odisha_forest_decision_layer"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
wrap = lambda s, width=96: "\n".join(__import__("textwrap").wrap(s, width))
PUBLISHED_AT = "https://sudo-karan.github.io/ICTD_Project/"   # where the owner publishes the copy (his decision of 11 October 2026)
PUBLISHED_ON = "11 October 2026"


def stop(m):
    print("NOT WRITTEN: " + m, file=sys.stderr)
    sys.exit(1)


INDEX_ID = "adi_2011"                                           # the layer, and the unit-level field, left out of the copy
INDEX_WORDS = re.compile(r"development index", re.I)
PAGE_CELL = 'esc(f[F.adi]) + "</td><td>" + '                    # the one cell of the ranked list's row that prints the index
ABOUT_CUTS = ((", the development index and past spending", " and past spending"),
              ("; the development index is shown in the list on this page and is left out of the exported file", ""),
              ("On the census layers the outside-village units are", "On the census layer the outside-village units are"))
NOTE_CUT = "; index by the ICTD group, IIT Delhi"
# The overlay in the copy (the owner's ruling of 11 October 2026): his words, and the places of the layer's texts they go to.
OVERLAY_UNAVAILABLE = "Not in this copy, while we check the tile provider's terms of use."
OVERLAY_ABOUT = re.compile(r"<p><b>The loss-pixel overlay</b> .*?</p>", re.S)                       # the layer's paragraph on its overlay
OVERLAY_ABOUT_COPY = ("<p><b>The loss-pixel overlay isn't in this copy.</b> The full version can lay Hansen's loss pixels over the map as tiles from {provider}. "
                      "We've left it out of the copy we share while two points of the provider's terms of use are unresolved.</p>")
OVERLAY_ROW = "Loss-pixel overlay (optional, online, off unless ticked; its code is in overlay.js)"   # the first cell of the layer's row of Sources
OVERLAY_ROW_COPY = "Loss-pixel overlay (not in this copy)"
OVERLAY_TERMS_COPY = "{attribution}. Terms of use: {terms_url}. Two points of them are unresolved, which is why the overlay is not in this copy."
# The README's sentence on phones: what was tried, and no more. On 11 October 2026 the page was opened in a window of a phone's width (390 x 844) in a desktop
# browser and looked at: the two side panels leave the map no room, the legend covers the list of layers, and the page runs off the right edge. No phone was tried.
PHONES = ("it's laid out for a laptop, and in a window as narrow as a phone's the map gets no room between the two side panels, so it won't work on a phone yet "
          "(we haven't tried one).")


def once(found, what):
    if len(found) != 1:
        stop(f"{what}: found {len(found)} time(s) in the layer, not once. The layer has changed; this script must be read again before a copy is made")
    return found[0]


def overlay_switched_off(D, ov):
    """The copy's data with the overlay switched off, as the owner ruled on 11 October 2026: `decision.overlay` cut to `available` 0, the layer's label and
    his words; the About text's paragraph on the overlay and the overlay's row of Sources replaced by his words for the copy. ov: the layer's record of its
    overlay (provider, attribution, terms_url). Returns what was changed. Each place is found exactly once or the run stops."""
    DV = D["decision"]
    was = DV["overlay"]
    if not was.get("available") or not isinstance(was.get("label"), str):
        stop("the layer's overlay is not registered: there is nothing to switch off, and this script must be read again")
    DV["overlay"] = {"available": 0, "label": was["label"], "unavailable": OVERLAY_UNAVAILABLE}
    para = once(OVERLAY_ABOUT.findall(D["about_html"]), "the paragraph of the About text on the overlay")
    para_copy = OVERLAY_ABOUT_COPY.format(provider=ov["provider"])
    if D["about_html"].count(para) != 1:
        stop("the paragraph of the About text on the overlay stands more than once")
    D["about_html"] = D["about_html"].replace(para, para_copy)
    row = once([r for r in re.findall(r"<tr>.*?</tr>", D["sources_html"], re.S) if r.startswith(f"<tr><td>{OVERLAY_ROW}</td>")], "the overlay's row of Sources")
    cells = re.findall(r"<td>(.*?)</td>", row, re.S)
    if len(cells) != 3 or not cells[1].startswith(ov["provider"] + ":") or not cells[2].startswith(ov["attribution"] + ". ") or f"Terms of use: {ov['terms_url']} " not in cells[2]:
        stop("the overlay's row of Sources does not carry the provider, the credit and the terms the layer's record registered")
    row_copy = f"<tr><td>{OVERLAY_ROW_COPY}</td><td>{cells[1]}</td><td>" + OVERLAY_TERMS_COPY.format(attribution=ov["attribution"], terms_url=ov["terms_url"]) + "</td></tr>"
    D["sources_html"] = D["sources_html"].replace(row, row_copy)
    return {"overlay_in_the_layer": sorted(was), "overlay_in_the_copy": DV["overlay"], "about_paragraph": {"was_characters": len(para), "is": para_copy},
            "sources_row": {"first_cell_was": OVERLAY_ROW, "first_cell_is": OVERLAY_ROW_COPY, "last_cell_was": cells[2], "last_cell_is": OVERLAY_TERMS_COPY.format(attribution=ov["attribution"], terms_url=ov["terms_url"])}}


def without_the_index(text, D, page, ov):
    """The layer's data and page with the development index taken out and the overlay switched off. Returns (data.js text, page text, what was cut, what was changed for the overlay)."""
    dump = lambda d: text[:text.index("{")] + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + text[text.rindex("}") + 1:]
    if dump(D) != text:
        stop("written again untouched, the layer's data.js does not give back its own bytes: the copy would differ from the layer in more than what is taken out")
    D = json.loads(json.dumps(D))
    DV = D["decision"]
    layer = once([l for l in D["layers"] if l["id"] == INDEX_ID], f"a layer whose id is {INDEX_ID}")
    title = layer["title"]
    D["layers"] = [l for l in D["layers"] if l["id"] != INDEX_ID]
    k = DV["fields"].pop("adi", None)                             # the position of the index in a unit's row of fields
    if not isinstance(k, int) or D["default_layer"] == INDEX_ID:
        stop("the decision view names no field for the index, or the index is the layer the page opens on")
    refs = lambda: [r[1] for sec in D["panel"] for r in sec.get("rows", [])] + [sec[key] for sec in D["panel"] for key in ("heading_field", "flag_field") if key in sec] + list(DV["fields"].values())
    sec = once([sec for sec in D["panel"] if any(r[1] == k for r in sec.get("rows", []))], "a section of the unit panel with the index's line")
    line = once([r for r in sec["rows"] if r[1] == k], "the index's line in the unit panel")
    sec["rows"] = [r for r in sec["rows"] if r[1] != k]
    if sec.get("note", "").count(NOTE_CUT) != 1:
        stop("the note under the panel's census section does not name the index's makers exactly once")
    sec["note"] = sec["note"].replace(NOTE_CUT, "")
    if k in refs():
        stop("something else on the page reads the index's field")
    width = {len(row) for row in D["f"]}
    if len(width) != 1 or not k < min(width):
        stop("the units' rows of fields are not all of one length")
    values = len(D["f"])
    for row in D["f"]:
        del row[k]
    for s_ in D["panel"]:                                         # every field after the one taken out moves one place down
        for r in s_.get("rows", []):
            r[1] -= r[1] > k
        for key in ("heading_field", "flag_field"):
            if key in s_:
                s_[key] -= s_[key] > k
    for key in DV["fields"]:
        DV["fields"][key] -= DV["fields"][key] > k
    if max(refs()) >= len(D["f"][0]):
        stop("a field of the page points past the end of a unit's row")
    head = once([c for c in DV["t"]["cols"] if INDEX_WORDS.search(c)], "a column head of the ranked list that names the index")
    place = DV["t"]["cols"].index(head)
    DV["t"]["cols"].remove(head)
    if page.count(PAGE_CELL) != 1 or page.count("F.adi") != 1:
        stop("the page does not print the index in exactly one cell of the ranked list")
    cells_before = page[:page.index(PAGE_CELL)].rsplit("<tr class=", 1)[-1].count("<td")
    if cells_before != place + 1:                                 # the cell cut must be the one under the head cut
        stop(f"the index's cell is not under its head: the head is column {place + 1} and the cell is column {cells_before}")
    page = page.replace(PAGE_CELL, "")
    for old, new in ABOUT_CUTS:
        if D["about_html"].count(old) != 1:
            stop(f"the About text does not hold exactly once: {old!r}")
        D["about_html"] = D["about_html"].replace(old, new)
    row = once([r for r in re.findall(r"<tr>.*?</tr>", D["sources_html"], re.S) if r.startswith(f"<tr><td>{title}</td>")], "the index's row of Sources and licences")
    D["sources_html"] = D["sources_html"].replace(row, "")
    off = overlay_switched_off(D, ov)
    out = dump(D)
    for name, body in (("data.js", out), ("index.html", page)):
        left = [w for w in (INDEX_ID, title, head) if w in body] + INDEX_WORDS.findall(body) + (["F.adi"] if "F.adi" in body else [])
        if left:
            stop(f"{name} of the copy still names the development index: {sorted(set(left))}")
    cut = {"layer": {"id": INDEX_ID, "title": title, "legend_title": layer["legend_title"]}, "unit_rows_from_which_the_value_was_taken": values,
           "field_position_in_a_unit_row": k, "panel_line": line[0], "panel_note_clause": NOTE_CUT, "list_column_head": head, "list_column": place + 1,
           "about_text": [{"was": a, "is": b} for a, b in ABOUT_CUTS], "sources_row_first_cell": title, "page_cell": PAGE_CELL}
    return out, page, cut, off


def main():
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for f in ("index.html", "data.js", "layer.provenance.json"):
        if not (SRC / f).is_file():
            stop(f"60_layer/{f} is not there: build the layer first")
    L = json.load(open(SRC / "layer.provenance.json"))
    if any(sha(SRC / f) != L["outputs"]["sha256"][f] for f in ("index.html", "data.js")):
        stop("the two files in 60_layer/ are not the ones its run record describes: build the layer again")
    text = (SRC / "data.js").read_text(encoding="utf-8")
    D = json.loads(text[text.index("{"):text.rindex("}") + 1])
    DV = D.get("decision")
    ov = (L.get("decision_view") or {}).get("overlay") or {}
    if not DV or not DV["overlay"].get("available") or not ov.get("registered") or any(not ov.get(k) for k in ("provider", "attribution", "terms_url")):
        stop("the layer has no decision view, or its overlay is not registered with a provider, a credit and its terms: the copy's words for the overlay rest on them")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    if page.count('s.src = "overlay.js"') != 1:
        stop("the page does not ask for overlay.js in exactly one place")
    full = {"data.js": text, "index.html": page}
    text, page, cut, off = without_the_index(text, D, page, ov)
    D = json.loads(text[text.index("{"):text.rindex("}") + 1])                    # from here on, the copy's own data
    DV = D["decision"]
    if DV["overlay"] != {"available": 0, "label": off["overlay_in_the_copy"]["label"], "unavailable": OVERLAY_UNAVAILABLE} or OVERLAY_ROW in text or "The loss-pixel overlay</b> is optional" in text:
        stop("in the copy's data the overlay is not switched off as ruled: `available` 0, the label and the owner's words, with his paragraph and his row of Sources")
    made = {"data.js": text.encode("utf-8"), "index.html": page.encode("utf-8")}
    plain = lambda s: " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())
    credits = []
    for r in re.findall(r"<tr>(.*?)</tr>", D["sources_html"], re.S):
        cells = [plain(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(cells) == 3:
            credits.append(cells)
    if len(credits) < 8 or not any("Hansen" in c[1] for c in credits) or not any("ODbL" in c[2] for c in credits):
        stop("the layer's list of sources could not be read from data.js")
    n = len(D["out"])
    cells_now = "\n".join(f"    {c['name']}" for c in DV["cells"])
    order = "; ".join(f"{i + 1} {next(c['name'] for c in DV['cells'] if c['id'] == t)}" for i, t in enumerate(DV["tiers"]))
    bullets = lambda items: "\n".join("\n".join(__import__("textwrap").wrap(x, 96, subsequent_indent="  ")) for x in items)
    readme = "\n\n".join([
        D["title"].upper() + f"\nA working map for discussion. Online at {PUBLISHED_AT}",
        "HOW TO OPEN IT\n" + wrap("Open the address above in a web browser. Or keep index.html and data.js together in one folder and open index.html (double-click it): it needs nothing installed and works without a "
                                  "connection. Once it has loaded, the page asks no other site for anything. We've checked the map in Chrome and in Safari's engine (WebKit) on a laptop, and this copy in Chrome; " + PHONES
                                  + " On the page, \"About this map\" explains how it's made and how to read it, and \"Sources\" says where the data comes from and under what licence."),
        "WHAT IT SHOWS\n" + wrap(f"{n:,} units covering Odisha: panchayat units, and the land outside any revenue village. For each, it shows forest condition, past MGNREGA spending and social need, each as its own layer, "
                                 "built from public data. The decision view reads the forest data a second way: each unit goes in one of six cells, by how much of its forest of 2000 has no loss recorded since "
                                 f"({DV['standing_min']} or more, or less) and by the forest loss recorded in a window of years you choose ({DV['loss_min']} or more, or less). Within one district, units are listed tier by tier.")
        + "\n  The six cells:\n" + cells_now,
        "WHAT IT ISN'T\n" + bullets((
            "- Not a verdict on any place, and not a score. It's a starting point for where to look, to be checked against what people who know the places see.",
            "- Standing forest here is the forest of 2000 with no loss recorded since; not a measure of tree cover today. The page quotes the data provider's own cautions.",
            f"- The order of the tiers is provisional, to be set with the Foundation for Ecological Security: {order}. You can change it on the page.",
            "- Which works from the official list fit which cell is our proposal, not a ruling.",
            "- A unit is a shape on a map, not a jurisdiction; the census figures are from 2011; the geotagged record of works effectively ends in 2017-18.")),
        "LEFT OUT OF THIS COPY\n" + bullets((
            "- The loss-pixel overlay. The full version can lay Hansen's loss over the map as tiles from an outside provider's server. We've left it out while two points of that provider's terms of use are unresolved; "
            "its box on the page is greyed out.",
            f"- The development index is not in this copy. The full version also shows a 2011 village development index ('{cut['layer']['title']}') as a layer, as a line in each unit's panel and as a column of the list. "
            "No file we share carries it.")) + "\nApart from these two, this copy's two files are the full version's own.",
        "CREDITS AND LICENCES (the rows of the page's \"Sources\")\n" + "\n".join(wrap(f"- {a}: {b}. Licence or terms: {c}") for a, b, c in credits),
        "SHARING IT\n" + wrap(f"We publish this copy at {PUBLISHED_AT} (since {PUBLISHED_ON}). Each source keeps its own licence, listed above; the unit boundaries in data.js are a database derived from DataMeet's and are "
                              "under the Open Database Licence (ODbL 1.0)."),
        "THIS COPY\n" + f"Made {started} (UTC) by scripts/07_build_share.py from the layer built {L['run_utc']}: that layer's two files without\nthe development index, and with the overlay switched off.\n"
        + "\n".join(f"  {f}  {len(made[f]):,} bytes  sha256 {hashlib.sha256(made[f]).hexdigest()}" for f in ("index.html", "data.js")),
    ]) + "\n"
    TMP = OUT / ".being_written"
    OUT.mkdir(exist_ok=True)
    if TMP.exists():
        shutil.rmtree(TMP)
    folder = TMP / NAME
    folder.mkdir(parents=True)
    for f in ("index.html", "data.js"):
        (folder / f).write_bytes(made[f])
    (folder / "README.txt").write_text(readme, encoding="utf-8")
    wrong = []
    if sorted(p.name for p in folder.iterdir()) != ["README.txt", "data.js", "index.html"]:
        wrong.append("the copy does not hold exactly its three files")
    for f in ("index.html", "data.js"):
        body = (folder / f).read_text(encoding="utf-8")
        if body.encode("utf-8") != made[f] or len(body) >= len(full[f]):
            wrong.append(f"{f} in the copy is not what was made here: the layer's {f} without the development index")
        if INDEX_ID in body or INDEX_WORDS.search(body) or cut["layer"]["title"] in body or cut["list_column_head"] in body:
            wrong.append(f"{f} in the copy names the development index")
    if "the development index is not in this copy" not in readme.lower():
        wrong.append("the README does not say that the development index is not in this copy")
    stamp = tuple(int(x) for x in re.findall(r"\d+", L["run_utc"])[:6])            # the zip's file times are the layer's build time, so that the same layer gives the same zip but for the README's own time
    z = TMP / (NAME + ".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in ("README.txt", "index.html", "data.js"):
            info = zipfile.ZipInfo(f"{NAME}/{f}", date_time=stamp)
            info.compress_type, info.external_attr = zipfile.ZIP_DEFLATED, 0o644 << 16
            zf.writestr(info, (folder / f).read_bytes())
    with zipfile.ZipFile(z) as zf:
        names = sorted(zf.namelist())
        if names != sorted(f"{NAME}/{f}" for f in ("README.txt", "index.html", "data.js")) or zf.testzip() is not None:
            wrong.append(f"the zip does not hold exactly the three files: {names}")
        elif any(zf.read(f"{NAME}/{f}") != (folder / f).read_bytes() for f in ("README.txt", "index.html", "data.js")):
            wrong.append("a file in the zip does not unpack to the bytes of the file in the folder")
    if "overlay.js" in " ".join(p.name for p in folder.iterdir()) or (folder / "overlay.js").exists():
        wrong.append("overlay.js is in the copy")
    if wrong:
        shutil.rmtree(TMP)
        stop("; ".join(wrong))
    record = {"script": "scripts/07_build_share.py", "run_utc": started,
              "inputs": [{"path": f"60_layer/{f}", "bytes": (SRC / f).stat().st_size, "sha256": sha(SRC / f)} for f in ("index.html", "data.js", "layer.provenance.json")],
              "layer_run_utc": L["run_utc"],
              "the_copy": {"folder": f"70_share/{NAME}", "files": {f: {"bytes": (folder / f).stat().st_size, "sha256": sha(folder / f)} for f in ("index.html", "data.js", "README.txt")},
                           "zip": {"path": f"70_share/{NAME}.zip", "bytes": z.stat().st_size, "sha256": sha(z), "holds": sorted(f"{NAME}/{f}" for f in ("README.txt", "index.html", "data.js"))}},
              "checks_passed": {"written_again_untouched_the_layers_data_js_gives_back_its_own_bytes": True, "index_html_and_data_js_are_the_layers_without_the_development_index": True,
                                "the_overlay_is_switched_off_in_the_copys_data": True,
                                "the_development_index_is_named_in_index_html_or_data_js": False, "the_readme_says_the_development_index_is_not_in_this_copy": True,
                                "files_in_the_copy": 3, "overlay_js_in_the_copy": False, "zip_unpacks_to_the_same_bytes": True,
                                "the_layers_files_are_the_ones_its_record_describes": True, "credits_read_from_the_layers_own_sources": len(credits)},
              "development_index_left_out": dict(cut, why="no file that is passed on carries unit-level adi_2011 values (10 October 2026; reversible: docs/DECISION_LAYER.md section 17). 60_layer/ keeps the index",
                                                 bytes_shorter_than_the_layers={f: len(full[f].encode("utf-8")) - len(made[f]) for f in ("index.html", "data.js")}),
              "left_out_on_purpose": {"file": "60_layer/overlay.js", "why": "two points of the tile provider's terms of use are unresolved (docs/DECISION_LAYER.md); the copy that is published carries no code that can ask the provider's server for anything"},
              "overlay_switched_off": dict(off, ruling="the owner's ruling of 11 October 2026: in the copy the overlay's box is greyed out and cannot be ticked, says it is not in this copy, and the page asks for no overlay.js at all; "
                                                      "60_layer/ is not changed by it"),
              "what_the_page_says_beside_the_greyed_overlay_box_in_the_copy": DV["overlay"]["unavailable"],
              "terms_for_passing_it_on": f"published by the project owner at {PUBLISHED_AT} (his decision of {PUBLISHED_ON}); each source keeps its own licence; the README says so",
              "not_checked_here": "that a browser opens the copy, shows the overlay's box greyed out and unticked with those words, and asks for no overlay.js and nothing from the network: scripts/exercise_share.py"}
    (TMP / "share.provenance.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for old in (OUT / NAME, OUT / (NAME + ".zip"), OUT / "share.provenance.json"):
        if old.is_dir():
            shutil.rmtree(old)
        elif old.exists():
            old.unlink()
    for p in sorted(TMP.iterdir()):
        p.replace(OUT / p.name)
    TMP.rmdir()
    stale = OUT / "exercise_share_chrome.json"
    if stale.exists():                                              # a record of an earlier copy would be read as this one's
        stale.unlink()
    print(f"70_share/{NAME}/: index.html and data.js are the layer's (built {L['run_utc']}) without the development index and with the overlay switched off, README.txt of {len(readme.splitlines())} lines, no overlay.js; "
          f"{NAME}.zip {z.stat().st_size if z.exists() else (OUT / (NAME + '.zip')).stat().st_size:,} bytes; {len(credits)} credits read from the layer's own sources")
    print(f"done. run_utc {started}")


if __name__ == "__main__":
    main()
