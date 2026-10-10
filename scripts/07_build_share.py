#!/usr/bin/env python3
"""A copy of the layer made to be passed on: the two files of 60_layer/ WITHOUT the map overlay's file and WITHOUT the
development index of 2011 (the field adi_2011 and everything that displays it); in all else the layer's own content.

    python scripts/07_build_share.py

Why (the owner's ruling of 9 October 2026). Two points of the tile provider's terms are unresolved, so the copy that goes
to anyone else carries no code that can ask the provider's server for anything. The page is the same page: its box
"Site-level overlay" is still there, and when it is ticked the page finds no overlay.js beside it and says so.

Why no development index (10 October 2026; a reversible call, recorded in docs/DECISION_LAYER.md section 17). No file
that is passed on carries unit-level adi_2011 values. The exported list already leaves the index out because it is
passed on; this copy is passed on too. 60_layer/ keeps the index. What is taken out of the copy, and nothing else:
  data.js     the layer whose id is adi_2011 (its legend, its class of every unit, its counts); the index's value in
              every unit's row of fields, and that field's line in the unit panel; the clause of that panel's note that
              names the index's makers; the field's entry in the decision view's list (the column head and the name of
              the field); three places of the About text that speak of it (one of them only a plural: one census layer
              is left); the index's row of "Sources and licences"
  index.html  the one cell of the ranked list's row that printed the index
Each is found exactly once or the run stops, and the run stops if "adi_2011", the layer's title, the list's column
head or the words "development index" in any case are still in either file. The README says the index is not in
this copy.

In      60_layer/index.html, 60_layer/data.js      read, and written again without the development index
        60_layer/layer.provenance.json             the build they are of: its time and the two hashes it records
Out     70_share/ and nowhere else:
        odisha_forest_decision_layer/index.html, data.js, README.txt      the copy: these three files and no other
        odisha_forest_decision_layer.zip                                  a zip of that folder, beside it
        share.provenance.json                                             this run: inputs with sha256, the UTC time, the checks
        (The owner's words were "new folder 70_share/: index.html and data.js ... plus a short README.txt ... a zip of the
        folder beside it". The three files are one level down, in a folder of their own, so that the zip can lie beside
        the folder it is a zip of and still be inside the one numbered folder this script may write to; and so that this
        run's record is not among the files passed on.)

README.txt says how to open the copy, what it is and is not, that the map overlay is not in it, whose data it draws on
(the rows of the layer's own "Sources and licences", read from data.js, not typed here), and how it is passed on: since
11 October 2026 the copy is published by the project owner at `PUBLISHED_AT`, each source under its own licence. (Until
that day the README said that terms for passing the copy on were not yet agreed and asked that it not be passed on or
published; the owner decided to publish it, and that paragraph was reworded in the words he approved.) Every figure in it
is read from data.js.

What is checked here, and the run stops (nothing left in place) if one fails:
  - the two files in 60_layer/ are the ones the layer's run record describes (sha256);
  - written again untouched, the layer's data.js gives back its own bytes (so every byte that was not taken out is the
    layer's); with the development index taken out, the copy's two files name it nowhere;
  - the copy holds exactly three files and none is overlay.js;
  - the zip holds exactly those three files under the folder's name, and each unpacks to the bytes of the file on disk;
  - index.html and data.js, as the layer's own check already holds, name no address on the network outside their texts'
    words: the copy's page still has the one line that asks for overlay.js, a file that is not there.
What is NOT checked here: that a browser opens the copy, shows the overlay's box saying its file is not beside the page,
and asks the network for nothing. That is scripts/exercise_share.py, which opens the copy in Chrome and writes its record
into 70_share/.
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


def once(found, what):
    if len(found) != 1:
        stop(f"{what}: found {len(found)} time(s) in the layer, not once. The layer has changed; this script must be read again before a copy is made")
    return found[0]


def without_the_index(text, D, page):
    """The layer's data and page with the development index taken out. Returns (data.js text, page text, what was cut)."""
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
    out = dump(D)
    for name, body in (("data.js", out), ("index.html", page)):
        left = [w for w in (INDEX_ID, title, head) if w in body] + INDEX_WORDS.findall(body) + (["F.adi"] if "F.adi" in body else [])
        if left:
            stop(f"{name} of the copy still names the development index: {sorted(set(left))}")
    cut = {"layer": {"id": INDEX_ID, "title": title, "legend_title": layer["legend_title"]}, "unit_rows_from_which_the_value_was_taken": values,
           "field_position_in_a_unit_row": k, "panel_line": line[0], "panel_note_clause": NOTE_CUT, "list_column_head": head, "list_column": place + 1,
           "about_text": [{"was": a, "is": b} for a, b in ABOUT_CUTS], "sources_row_first_cell": title, "page_cell": PAGE_CELL}
    return out, page, cut


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
    if not DV or not DV["overlay"].get("available") or "missing" not in DV["overlay"]:
        stop("the layer has no decision view, or its overlay has no words for a file that is not there")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    if page.count('s.src = "overlay.js"') != 1:
        stop("the page does not ask for overlay.js in exactly one place")
    full = {"data.js": text, "index.html": page}
    text, page, cut = without_the_index(text, D, page)
    D = json.loads(text[text.index("{"):text.rindex("}") + 1])                    # from here on, the copy's own data
    DV = D["decision"]
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
    readme = "\n\n".join([
        D["title"].upper() + "\nA map layer for discussion. This copy was made to be passed on.",
        "HOW TO OPEN IT\n" + wrap("Keep index.html and data.js together in one folder and open index.html in a web browser (double-click it). Nothing is installed, nothing is fetched from the internet, "
                                  "and it works with no connection. It was checked in Chrome and in Safari's engine on a laptop; it has not been tried on a phone. The button 'What this is, and how to read it' on the page is the full account, "
                                  "and 'Sources and licences' lists every source."),
        "WHAT IT IS\n" + wrap(f"{n:,} units of Odisha: gram panchayat units, and the land that lies in no revenue village. For each it shows measurements of forest condition, of past MGNREGA allocation and of "
                              "social need, each as a layer of its own, as they were built from public data. The 'Decision view' on the page reads the forest measurements a second way: each unit is "
                              f"placed in one of six cells by how much forest of 2000 has no loss recorded since ({DV['standing_min']} or more, or less) and by the forest loss recorded in a window of years you "
                              f"choose ({DV['loss_min']} or more, or less), and within one district the units are listed tier by tier.")
        + "\n  The six cells:\n" + cells_now,
        "WHAT IT IS NOT\n" + "\n".join(wrap(s) for s in (
            "- It is not a verdict on any place and it is not a score. It is a prompt for where to look, to be set against what people who know the places see.",
            "- Standing forest in it is the forest of 2000 with no loss recorded since; not a measure of tree cover today. The page's own text gives the data provider's cautions.",
            f"- The order of the tiers is provisional, to be set with the Foundation for Ecological Security: {order}. The page lets you change it.",
            "- Which works of the official list bear on which cell is a proposal, not a ruling.",
            "- A unit is a shape on a map, not a jurisdiction; the census figures are of 2011; the geotagged record of works effectively ends in 2017-18.")),
        "THE MAP OVERLAY IS NOT IN THIS COPY\n" + wrap("The page has a box 'Site-level overlay'. In the full layer it can lay Hansen's loss over the map as tiles from an outside provider's server. The file that does "
                                                     "that, overlay.js, is left out of this copy on purpose: two points of that provider's terms of use are unresolved. If the box is ticked here the page "
                                                     f"says: \"{DV['overlay']['missing']}\" The page asks the network for nothing."),
        "THE DEVELOPMENT INDEX IS NOT IN THIS COPY\n" + wrap(f"The full layer also shows a village development index of 2011 ('{cut['layer']['title']}'): as a layer of its own, as a line in each unit's panel "
                                                           "and as a column of the ranked list. The index is left out of this copy on purpose, with its value for every unit: no file that is passed on "
                                                           "carries it. Apart from that, and from the map overlay's file, the copy's two files are the layer's own."),
        "CREDITS AND LICENCES (the rows of the page's own 'Sources and licences')\n" + "\n".join(wrap(f"- {a}: {b}. Licence or terms: {c}") for a, b, c in credits),
        "PASSING IT ON\n" + wrap(f"This copy is published by the project owner at {PUBLISHED_AT} ({PUBLISHED_ON}). Each source keeps its own licence, listed above; the unit boundaries in data.js are a "
                                 "database derived from DataMeet's and are under the Open Database Licence (ODbL 1.0)."),
        "THIS COPY\n" + f"Made {started} (UTC) by scripts/07_build_share.py from the layer built {L['run_utc']}: that layer's two files without the development index.\n"
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
                                "the_development_index_is_named_in_index_html_or_data_js": False, "the_readme_says_the_development_index_is_not_in_this_copy": True,
                                "files_in_the_copy": 3, "overlay_js_in_the_copy": False, "zip_unpacks_to_the_same_bytes": True,
                                "the_layers_files_are_the_ones_its_record_describes": True, "credits_read_from_the_layers_own_sources": len(credits)},
              "development_index_left_out": dict(cut, why="no file that is passed on carries unit-level adi_2011 values (10 October 2026; reversible: docs/DECISION_LAYER.md section 17). 60_layer/ keeps the index",
                                                 bytes_shorter_than_the_layers={f: len(full[f].encode("utf-8")) - len(made[f]) for f in ("index.html", "data.js")}),
              "left_out_on_purpose": {"file": "60_layer/overlay.js", "why": "two points of the tile provider's terms of use are unresolved (docs/DECISION_LAYER.md); the copy that is passed on asks the network for nothing"},
              "what_the_page_says_when_the_overlay_is_ticked_in_the_copy": DV["overlay"]["missing"],
              "terms_for_passing_it_on": f"published by the project owner at {PUBLISHED_AT} (his decision of {PUBLISHED_ON}); each source keeps its own licence; the README says so",
              "not_checked_here": "that a browser opens the copy, shows that message and asks the network for nothing: scripts/exercise_share.py"}
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
    print(f"70_share/{NAME}/: index.html and data.js are the layer's (built {L['run_utc']}) without the development index, README.txt of {len(readme.splitlines())} lines, no overlay.js; "
          f"{NAME}.zip {z.stat().st_size if z.exists() else (OUT / (NAME + '.zip')).stat().st_size:,} bytes; {len(credits)} credits read from the layer's own sources")
    print(f"done. run_utc {started}")


if __name__ == "__main__":
    main()
