#!/usr/bin/env python3
"""The gate on the copy of the layer that is made to be passed on (70_share/): opened from disk in Chrome.

    python scripts/exercise_share.py [folder for screenshots]

The owner's gate of 9 October 2026: "index.html and data.js byte-identical to 60_layer/'s; opened from disk in Chrome, the
overlay control says its file is not beside the page and the page makes no network request."

What it does, in a separate headless Chrome with an empty profile (the adapter of scripts/exercise_layer.py, which is not
changed and of which nothing else is used):
  1. compares the copy's index.html and data.js with 60_layer/'s, byte for byte, and looks for overlay.js in the copy;
  2. opens the copy's index.html from disk (file://) and waits for the page to be ready;
  3. reads which files the page loaded and how many requests went to the network (http or https) while it opened;
  4. chooses the decision view and reads the box "Site-level overlay": it must be on show and unticked;
  5. ticks the box, and reads the box, the message beside it, the map's panes and the requests again: the box must be
     unticked again, the message must be the layer's own words for a file that is not there, no tile may be on the map,
     and no request may have gone to the network;
  6. reads the page's script errors. The browser itself logs that the file overlay.js was not found: that one line is the
     point of the copy and is recorded; any other error fails the run.
It also reads the unit count the page shows, so that "opened" means the map is there.

Output: 70_share/exercise_share_chrome.json and nothing else - every step with what happened, the sha256 of the files
opened, the UTC time. Exits 1 unless every step did what it should. Screenshots go to the folder given, or to a
temporary one; they are not an output.
"""
import hashlib, json, sys, tempfile, time
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


def say(did, happened, ok):
    steps.append({"did": did, "happened": happened, "ok": bool(ok)})
    print(("PASS  " if ok else "FAIL  ") + f"{did} -> {happened}", flush=True)


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for f in ("index.html", "data.js", "README.txt"):
        if not (COPY / f).is_file():
            sys.exit(f"70_share/{NAME}/{f} is not there: run scripts/07_build_share.py")
    rec = json.load(open(ROOT / "70_share" / "share.provenance.json"))
    same = {f: (COPY / f).read_bytes() == (SRC / f).read_bytes() for f in ("index.html", "data.js")}
    held = sorted(p.name for p in COPY.iterdir())
    say("compared the copy's index.html and data.js with 60_layer/'s, byte for byte, and listed the copy's files",
        f"index.html the same: {same['index.html']}; data.js the same: {same['data.js']}; the copy holds {held}; overlay.js in it: {'overlay.js' in held}",
        all(same.values()) and held == ["README.txt", "data.js", "index.html"])
    text = (COPY / "data.js").read_text(encoding="utf-8")
    DV = json.loads(text[text.index("{"):text.rindex("}") + 1])["decision"]
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
        expected = [e for e in errors if e.startswith("log: ") and "ERR_FILE_NOT_FOUND" in e]
        other = [e for e in errors if e not in expected]
        say("read the page's script errors and the browser's log", f"the browser logged that a file was not found {len(expected)} time(s) - overlay.js, the file this copy leaves out; any other error: {other or 'none'}",
            not other and len(expected) <= 1)
        b = box()
        say("looked at the map again after that", f"the decision view is still on and the map is still drawn ({b['drawn']:,} units); the box can be ticked again and gives the same answer", b["view"] and b["drawn"] > 0 and not b["ticked"])
    finally:
        c.close()
    ok = all(s["ok"] for s in steps)
    json.dump({"script": "scripts/exercise_share.py", "run_utc": started, "browser": c.version, "how": X.InChrome.how, "opened": URL,
               "inputs": [{"path": f"70_share/{NAME}/{f}", "bytes": (COPY / f).stat().st_size, "sha256": sha(COPY / f)} for f in ("index.html", "data.js", "README.txt")]
                         + [{"path": f"60_layer/{f}", "bytes": (SRC / f).stat().st_size, "sha256": sha(SRC / f)} for f in ("index.html", "data.js")]
                         + [{"path": "70_share/share.provenance.json", "bytes": (ROOT / "70_share/share.provenance.json").stat().st_size, "sha256": sha(ROOT / "70_share/share.provenance.json")}],
               "copy_run_utc": rec["run_utc"], "layer_run_utc": rec["layer_run_utc"], "steps": steps,
               "summary": {"steps": len(steps), "steps_as_expected": sum(s["ok"] for s in steps), "index_html_and_data_js_byte_for_byte_the_layers": all(same.values()), "overlay_js_in_the_copy": "overlay.js" in held,
                           "what_the_control_said_when_ticked": steps[3]["happened"].split("the control says: '")[1].split("'; the page asked")[0] if len(steps) > 3 and "the control says: '" in steps[3]["happened"] else "",
                           "requests_to_the_network": 0 if ok else None, "errors_other_than_the_file_not_found": [] if ok else "see the steps"}},
              open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{sum(s['ok'] for s in steps)} of {len(steps)} steps did what they should; record: 70_share/exercise_share_chrome.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
