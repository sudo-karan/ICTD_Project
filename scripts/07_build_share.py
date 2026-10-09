#!/usr/bin/env python3
"""A copy of the layer made to be passed on: the two files of 60_layer/, byte for byte, WITHOUT the map overlay's file.

    python scripts/07_build_share.py

Why (the owner's ruling of 9 October 2026). Two points of the tile provider's terms are unresolved, so the copy that goes
to anyone else carries no code that can ask the provider's server for anything. The page is the same page: its box
"Site-level overlay" is still there, and when it is ticked the page finds no overlay.js beside it and says so.

In      60_layer/index.html, 60_layer/data.js      copied byte for byte
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
(the rows of the layer's own "Sources and licences", read from data.js, not typed here), and that terms for passing it on
are not yet agreed. Every figure in it is read from data.js.

What is checked here, and the run stops (nothing left in place) if one fails:
  - the two files in 60_layer/ are the ones the layer's run record describes (sha256);
  - the copy's index.html and data.js are byte for byte those files; the copy holds exactly three files and none is overlay.js;
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


def stop(m):
    print("NOT WRITTEN: " + m, file=sys.stderr)
    sys.exit(1)


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
        "CREDITS AND LICENCES (the rows of the page's own 'Sources and licences')\n" + "\n".join(wrap(f"- {a}: {b}. Licence or terms: {c}") for a, b, c in credits),
        "PASSING IT ON\n" + wrap("Terms for passing this copy on are not yet agreed. Please do not pass it on or publish it until they are. The unit boundaries in data.js are a database derived from "
                                 "DataMeet's and are under the Open Database Licence (ODbL 1.0); the other credits are above."),
        "THIS COPY\n" + f"Made {started} (UTC) by scripts/07_build_share.py from the layer built {L['run_utc']}.\n"
        + "\n".join(f"  {f}  {(SRC / f).stat().st_size:,} bytes  sha256 {sha(SRC / f)}" for f in ("index.html", "data.js")),
    ]) + "\n"
    TMP = OUT / ".being_written"
    OUT.mkdir(exist_ok=True)
    if TMP.exists():
        shutil.rmtree(TMP)
    folder = TMP / NAME
    folder.mkdir(parents=True)
    for f in ("index.html", "data.js"):
        shutil.copyfile(SRC / f, folder / f)
    (folder / "README.txt").write_text(readme, encoding="utf-8")
    wrong = []
    if sorted(p.name for p in folder.iterdir()) != ["README.txt", "data.js", "index.html"]:
        wrong.append("the copy does not hold exactly its three files")
    for f in ("index.html", "data.js"):
        if (folder / f).read_bytes() != (SRC / f).read_bytes():
            wrong.append(f"{f} in the copy is not byte for byte the layer's")
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
              "checks_passed": {"index_html_and_data_js_byte_for_byte_the_layers": True, "files_in_the_copy": 3, "overlay_js_in_the_copy": False, "zip_unpacks_to_the_same_bytes": True,
                                "the_layers_files_are_the_ones_its_record_describes": True, "credits_read_from_the_layers_own_sources": len(credits)},
              "left_out_on_purpose": {"file": "60_layer/overlay.js", "why": "two points of the tile provider's terms of use are unresolved (docs/DECISION_LAYER.md); the copy that is passed on asks the network for nothing"},
              "what_the_page_says_when_the_overlay_is_ticked_in_the_copy": DV["overlay"]["missing"],
              "terms_for_passing_it_on": "not yet agreed; the README says so",
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
    print(f"70_share/{NAME}/: index.html and data.js byte for byte the layer's (built {L['run_utc']}), README.txt of {len(readme.splitlines())} lines, no overlay.js; "
          f"{NAME}.zip {z.stat().st_size if z.exists() else (OUT / (NAME + '.zip')).stat().st_size:,} bytes; {len(credits)} credits read from the layer's own sources")
    print(f"done. run_utc {started}")


if __name__ == "__main__":
    main()
