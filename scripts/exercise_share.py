#!/usr/bin/env python3
"""The gate on the copy of the layer that is made to be passed on (70_share/odisha_forest_decision_layer/): opened from
disk in Chrome.

    python scripts/exercise_share.py [folder for screenshots]

The owner's gate of 9 October 2026 was: "index.html and data.js byte-identical to 60_layer/'s; opened from disk in Chrome,
the overlay control says its file is not beside the page and the page makes no network request." Since 10 October 2026
the copy also leaves out the development index of 2011 (adi_2011), so its two files are no longer the layer's byte for
byte, and the first step is no longer a comparison of bytes. Two things changed in this gate, and why:
  - step 1 held the copy's two files byte for byte against 60_layer/'s. It now holds them against 60_layer/'s under the
    rule written out in `expected()` below: the layer's files with the index taken out and nothing else. A copy that
    differed from the layer in anything but the index would fail it, as before.
  - the record's key `index_html_and_data_js_byte_for_byte_the_layers` is gone; in its place is
    `index_html_and_data_js_are_the_layers_without_the_development_index`.
Three checks were added: that neither "adi_2011" nor the index's names on the page are in the copy's data.js or
index.html (the README is exempt: it names the index to say that it is absent, and must); and, in the browser, that the
ranked list, a unit's panel, the list of layers and the two text panels show the index nowhere and show no empty or
shifted cell where it was.

What it does, in a separate headless Chrome with an empty profile (the adapter of scripts/exercise_layer.py, which is not
changed and of which nothing else is used):
  1. compares the copy's index.html and data.js with 60_layer/'s under the rule, and looks for overlay.js in the copy;
  2. looks in the copy's data.js and index.html for the index's id and names, and in the README for the sentence that
     says the index is not in the copy;
  3. opens the copy's index.html from disk (file://) and waits for the page to be ready; reads which files the page
     loaded and how many requests went to the network (http or https) while it opened;
  4. chooses the decision view and reads the box "Site-level overlay": it must be on show and unticked;
  5. ticks the box, and reads the box, the message beside it, the map's panes and the requests again: the box must be
     unticked again, the message must be the layer's own words for a file that is not there, no tile may be on the map,
     and no request may have gone to the network;
  6. reads the page's script errors. The browser itself logs that the file overlay.js was not found: that one line is the
     point of the copy and is recorded; any other error fails the run;
  7. looks at the map again;
  8. ranks a district and opens one of its units by the page's address, and reads the ranked list (as many cells in
     every row as heads, the last cell the one the layer's own list ends with, no cell reading "undefined"), the unit's
     panel (every line the layer's panel has for that unit but the index's, the same note in the box above the forest
     figures), the list of layers, and the texts "What this is" and "Sources and licences": the index is in none.
It also reads the unit count the page shows, so that "opened" means the map is there.

Output: 70_share/exercise_share_chrome.json and nothing else - every step with what happened, the sha256 of the files
opened, the UTC time. Exits 1 unless every step did what it should. Screenshots go to the folder given, or to a
temporary one; they are not an output.
"""
import hashlib, json, re, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="ictd_share_shots_"))
sys.argv = [sys.argv[0], "chrome", str(SHOTS)]                  # exercise_layer reads these when imported; importing it opens no browser
sys.path.insert(0, str(ROOT / "scripts"))
import exercise_layer as X                                      # noqa: E402  (its Chrome adapter only)

NAME = "odisha_forest_decision_layer"
COPY, SRC, OUT = ROOT / "70_share" / NAME, ROOT / "60_layer", ROOT / "70_share" / "exercise_share_chrome.json"
URL = "file://" + str(COPY / "index.html")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
steps = []
INDEX = "adi_2011"
INDEX_WORDS = re.compile(r"development index", re.I)
CELL = 'esc(f[F.adi]) + "</td><td>" + '
README_SAYS = "the development index is not in this copy"


def say(did, happened, ok):
    steps.append({"did": did, "happened": happened, "ok": bool(ok)})
    print(("PASS  " if ok else "FAIL  ") + f"{did} -> {happened}", flush=True)


def data_of(path):
    text = Path(path).read_text(encoding="utf-8")
    return text, json.loads(text[text.index("{"):text.rindex("}") + 1])


def expected(S):
    """The rule, written out: what the layer's data must be once the development index is taken out, and nothing else."""
    E = json.loads(json.dumps(S))
    k = E["decision"]["fields"].pop("adi")
    down = lambda i: i - (i > k)
    title = next(l["title"] for l in E["layers"] if l["id"] == INDEX)
    E["layers"] = [l for l in E["layers"] if l["id"] != INDEX]
    E["f"] = [row[:k] + row[k + 1:] for row in E["f"]]
    for sec in E["panel"]:
        if any(r[1] == k for r in sec.get("rows", [])):
            sec["note"] = sec["note"].replace("; index by the ICTD group, IIT Delhi", "")
        if "rows" in sec:
            sec["rows"] = [[r[0], down(r[1])] for r in sec["rows"] if r[1] != k]
        for key in ("heading_field", "flag_field"):
            if key in sec:
                sec[key] = down(sec[key])
    E["decision"]["fields"] = {a: down(b) for a, b in E["decision"]["fields"].items()}
    head = [c for c in E["decision"]["t"]["cols"] if INDEX_WORDS.search(c)]
    E["decision"]["t"]["cols"] = [c for c in E["decision"]["t"]["cols"] if not INDEX_WORDS.search(c)]
    for was, now in ((", the development index and past spending", " and past spending"),
                     ("; the development index is shown in the list on this page and is left out of the exported file", ""),
                     ("On the census layers the outside-village units are", "On the census layer the outside-village units are")):
        E["about_html"] = E["about_html"].replace(was, now)
    E["sources_html"] = re.sub(r"<tr><td>" + re.escape(title) + r"</td>.*?</tr>", "", E["sources_html"], count=1, flags=re.S)
    return E, k, title, head


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for f in ("index.html", "data.js", "README.txt"):
        if not (COPY / f).is_file():
            sys.exit(f"70_share/{NAME}/{f} is not there: run scripts/07_build_share.py")
    rec = json.load(open(ROOT / "70_share" / "share.provenance.json"))
    s_text, S = data_of(SRC / "data.js")
    c_text, C = data_of(COPY / "data.js")
    s_page, c_page = (SRC / "index.html").read_text(encoding="utf-8"), (COPY / "index.html").read_text(encoding="utf-8")
    E, k, title, head = expected(S)
    differ = sorted(key for key in set(E) | set(C) if E.get(key) != C.get(key))
    whole = c_text == s_text[:s_text.index("{")] + json.dumps(C, ensure_ascii=False, separators=(",", ":")) + s_text[s_text.rindex("}") + 1:]
    same = {"data.js": not differ and whole and len(head) == 1 and len(C["f"][0]) == len(S["f"][0]) - 1 and len(C["layers"]) == len(S["layers"]) - 1,
            "index.html": s_page.count(CELL) == 1 and c_page == s_page.replace(CELL, "")}
    held = sorted(p.name for p in COPY.iterdir())
    say("compared the copy's index.html and data.js with 60_layer/'s under the rule (the layer's files with the development index taken out and nothing else), and listed the copy's files",
        f"index.html is the layer's without the one cell that printed the index: {same['index.html']}; data.js is the layer's without the index: {same['data.js']}"
        + (f" (parts that differ from the rule: {differ})" if differ else "") + f"; the copy holds {held}; overlay.js in it: {'overlay.js' in held}",
        all(same.values()) and held == ["README.txt", "data.js", "index.html"])
    names = [INDEX, title] + head
    found = {f: sorted({w for w in names if w in body} | set(INDEX_WORDS.findall(body)) | ({"F.adi"} if "F.adi" in body else set())) for f, body in (("data.js", c_text), ("index.html", c_page))}
    readme = (COPY / "README.txt").read_text(encoding="utf-8")
    in_layer = all(w in s_text for w in names)                    # so that not finding them in the copy means something
    say(f"looked in the copy's data.js and index.html for the index's id and its names on the page ({', '.join(repr(w) for w in names)}, and the words 'development index' in any case), and in README.txt for the sentence that says it is absent",
        f"found in data.js: {found['data.js'] or 'none'}; in index.html: {found['index.html'] or 'none'}; all of them are in 60_layer/data.js: {in_layer}; the README says '{README_SAYS}': {README_SAYS in readme.lower()}",
        not found["data.js"] and not found["index.html"] and in_layer and README_SAYS in readme.lower())
    DV = C["decision"]
    missing = DV["overlay"]["missing"]
    c = X.InChrome(tempfile.mkdtemp(prefix="ictd_chrome_profile_"), port=9337)
    net = lambda: [u for u in c.requests if u.startswith("http")]
    box = lambda: c.js("(function(){var e=document.getElementById('c_overlay'), m=document.getElementById('overlaymsg'), p=document.querySelector('.leaflet-sitelevel-pane');"
                       " return {shown: !!(e && e.offsetParent !== null), ticked: !!(e && e.checked), disabled: !!(e && e.disabled), msg: m ? m.textContent : '', tiles: p ? p.querySelectorAll('img').length : 0,"
                       " overlay_object: typeof window.ICTD_OVERLAY, view: document.getElementById('r_decision').checked, units: (window.ICTD_LAYER.id || []).length,"
                       " drawn: (function(){var n=0; ICTD_MAP.eachLayer(function(l){ if(l._u!==undefined){n++;} }); return n;})()};})()")
    try:
        t = c.open(URL)
        b = box()
        say(f"opened {URL} in {c.version}", f"ready in {t} s; files loaded: {c.files()}; requests to the network while it opened: {len(net())}; the map is there ({b['units']:,} units in the data, {b['drawn']:,} drawn)",
            c.files() == ["data.js", "index.html"] and len(net()) == 0 and b["units"] > 0 and b["drawn"] > 0)
        c.click_on("#r_decision"); time.sleep(0.8)
        b = box()
        say("chose the decision view and read the box 'Site-level overlay' before touching it", f"it is on show and unticked ('{b['msg'][:90]}...'); requests to the network so far: {len(net())}",
            b["view"] and b["shown"] and not b["ticked"] and not b["disabled"] and len(net()) == 0)
        x, y = c.click_on("#c_overlay")
        for _ in range(20):
            time.sleep(0.5)
            b = box()
            if not b["ticked"] and b["msg"] == missing:
                break
        c.shot(SHOTS / "share_overlay_ticked.png")
        asked = [u.split("/")[-1].split("#")[0] for u in c.requests if u.endswith("overlay.js")]
        say(f"ticked the box at ({x}, {y})",
            f"the box is unticked again and the control says: '{b['msg']}'; the page asked for the file {asked or 'nothing'} beside it, which is not there; no tile is on the map ({b['tiles']}); "
            f"requests to the network since the page opened: {len(net())}",
            not b["ticked"] and b["msg"] == missing and "is not beside this page" in b["msg"] and b["tiles"] == 0 and b["overlay_object"] == "undefined" and len(net()) == 0 and asked == ["overlay.js"])
        errors = list(c.errors or [])
        expected_log = [e for e in errors if e.startswith("log: ") and "ERR_FILE_NOT_FOUND" in e]
        other = [e for e in errors if e not in expected_log]
        say("read the page's script errors and the browser's log", f"the browser logged that a file was not found {len(expected_log)} time(s) - overlay.js, the file this copy leaves out; any other error: {other or 'none'}",
            not other and len(expected_log) <= 1)
        b = box()
        say("looked at the map again after that", f"the decision view is still on and the map is still drawn ({b['drawn']:,} units); the box can be ticked again and gives the same answer", b["view"] and b["drawn"] > 0 and not b["ticked"])
        # A district ranked and one of its units opened, by the page's address: the list, the panel, the layers, the texts.
        flag_at = next(sec["flag_field"] for sec in S["panel"] if "flag_field" in sec)
        u = next(i for i in range(len(S["f"])) if S["f"][i][flag_at] and S["f"][i][k][:1].isdigit() and S["out"][i] == "0")   # an LGD unit with a note above its forest figures and an index in the layer
        district = next(d["name"] for d in S["districts"] if d["name"] == S["f"][u][3])
        c.js(f"location.hash = 'layer=decision&rank=' + encodeURIComponent({json.dumps(district)}) + '&unit=' + encodeURIComponent({json.dumps(S['id'][u])})")
        r = {}
        for _ in range(40):
            time.sleep(0.5)
            r = c.js("(function(){var rows=[].slice.call(document.querySelectorAll('table.rk tr.r')), heads=[].slice.call(document.querySelectorAll('table.rk th')).map(function(e){return e.textContent;}),"
                     " info=document.getElementById('info'), flag=info.querySelector('.flag');"
                     " return {heads: heads, rows: rows.length, cells: rows.map(function(t){return t.children.length;}), last: rows.length ? rows[0].lastElementChild.textContent : '',"
                     " first_unit: rows.length ? +rows[0].getAttribute('data-u') : -1, undefined_cells: rows.filter(function(t){return /undefined/.test(t.textContent);}).length,"
                     " list_text: document.querySelector('table.rk') ? document.querySelector('table.rk').textContent : '', panel: [].slice.call(info.querySelectorAll('table.kv tr')).map(function(t){return [t.children[0].textContent, t.children[1].textContent];}),"
                     " panel_text: info.textContent, flag: flag ? flag.textContent : '', layers: [].slice.call(document.querySelectorAll('input[name=layer]')).map(function(e){return e.value;})};})()")
            if r["rows"] and r["panel"]:
                break
        c.shot(SHOTS / "share_ranked_list_and_panel.png")
        want_panel = [[row[0], S["f"][u][row[1]]] for sec in S["panel"] for row in sec.get("rows", []) if row[1] != k]
        fn = S["decision"]["fields"]["fn"]
        list_ok = (r["rows"] > 0 and r["heads"] and set(r["cells"]) == {len(r["heads"])} and len(r["heads"]) == len(S["decision"]["t"]["cols"]) - 1 and r["undefined_cells"] == 0
                   and not INDEX_WORDS.search(r["list_text"]) and r["first_unit"] >= 0 and r["last"] == S["f"][r["first_unit"]][fn])
        panel_ok = r["panel"] == want_panel and r["flag"] == S["f"][u][flag_at] and not INDEX_WORDS.search(r["panel_text"]) and "undefined" not in r["panel_text"]
        layers_ok = INDEX not in r["layers"] and sorted(r["layers"]) == sorted(l["id"] for l in S["layers"] if l["id"] != INDEX and not l.get("pending"))
        texts = {}
        for which in ("about", "sources"):
            c.js(f"document.getElementById('b_{which}').click()"); time.sleep(0.5)
            texts[which] = c.js("document.getElementById('modalbody').textContent")
            c.js("document.getElementById('b_close').click()"); time.sleep(0.3)
        texts_ok = all(len(v) > 500 and not INDEX_WORDS.search(v) and title not in v for v in texts.values())
        say(f"ranked the district {district} and opened its unit {S['id'][u]} by the page's address, and read the ranked list, the unit's panel, the list of layers and the two text panels",
            f"the list has {len(r.get('heads', []))} heads and {r.get('rows', 0)} rows, each of {sorted(set(r.get('cells', [])))} cells, against {len(S['decision']['t']['cols'])} heads in 60_layer/; cells reading 'undefined': {r.get('undefined_cells')}; "
            f"the last cell of the first row is that unit's forest-named spending as 60_layer/ gives it: {r.get('last') == (S['f'][r['first_unit']][fn] if r.get('first_unit', -1) >= 0 else None)}; "
            f"the panel has {len(r.get('panel', []))} lines, the layer's {len(want_panel) + 1} less the index's, each with the layer's value: {r.get('panel') == want_panel}; the note above the forest figures is the layer's: {r.get('flag') == S['f'][u][flag_at]}; "
            f"layers offered: {len(r.get('layers', []))}, the index among them: {INDEX in r.get('layers', [])}; the index named in the list, the panel, 'What this is' or 'Sources and licences': "
            f"{bool(INDEX_WORDS.search(r.get('list_text', '') + r.get('panel_text', '') + ''.join(texts.values())))}; requests to the network since the page opened: {len(net())}",
            list_ok and panel_ok and layers_ok and texts_ok and len(net()) == 0)
        other = [e for e in (c.errors or []) if not (e.startswith("log: ") and "ERR_FILE_NOT_FOUND" in e)]
        if other:
            say("read the page's script errors once more, after the list and the panel", f"errors: {other}", False)
    finally:
        c.close()
    ok = all(s["ok"] for s in steps)
    ticked = [s for s in steps if s["did"].startswith("ticked the box") and "the control says: '" in s["happened"]]
    json.dump({"script": "scripts/exercise_share.py", "run_utc": started, "browser": c.version, "how": X.InChrome.how, "opened": URL,
               "inputs": [{"path": f"70_share/{NAME}/{f}", "bytes": (COPY / f).stat().st_size, "sha256": sha(COPY / f)} for f in ("index.html", "data.js", "README.txt")]
                         + [{"path": f"60_layer/{f}", "bytes": (SRC / f).stat().st_size, "sha256": sha(SRC / f)} for f in ("index.html", "data.js")]
                         + [{"path": "70_share/share.provenance.json", "bytes": (ROOT / "70_share/share.provenance.json").stat().st_size, "sha256": sha(ROOT / "70_share/share.provenance.json")}],
               "copy_run_utc": rec["run_utc"], "layer_run_utc": rec["layer_run_utc"], "steps": steps,
               "summary": {"steps": len(steps), "steps_as_expected": sum(s["ok"] for s in steps), "index_html_and_data_js_are_the_layers_without_the_development_index": all(same.values()),
                           "the_development_index_is_named_in_index_html_or_data_js": bool(found["data.js"] or found["index.html"]), "the_readme_says_the_development_index_is_not_in_this_copy": README_SAYS in readme.lower(),
                           "overlay_js_in_the_copy": "overlay.js" in held,
                           "what_the_control_said_when_ticked": ticked[0]["happened"].split("the control says: '")[1].split("'; the page asked")[0] if ticked else "",
                           "requests_to_the_network": 0 if ok else None, "errors_other_than_the_file_not_found": [] if ok else "see the steps"}},
              open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{sum(s['ok'] for s in steps)} of {len(steps)} steps did what they should; record: 70_share/exercise_share_chrome.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
