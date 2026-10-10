"""The demo layer in the Safari application itself, opened from disk.

    python scripts/exercise_layer_safari.py

Safari is driven by the page's address alone and read back through AppleScript: its title, its address, and the text it
shows. NOTHING IS CLICKED. Running script in a page of Safari from outside, or driving Safari remotely, needs settings
of Safari that are its owner's to change, and this script changes none. So what it shows is that the page loads from
disk in Safari, runs, and shows the right text - for every layer, every minimum of forest, a sample of units, the
search and the two text panels - reached through the parts of the address the page understands (layer, floor, unit, q,
open). The controls themselves are exercised by exercise_layer.py in Chrome and in WebKit, the engine of Safari.
Not reachable this way, and so not looked at here: the two kinds-of-unit boxes and the district list (what they do is
drawn on the map, not written in the text), and the map itself.

It opens one new window in Safari, uses only that window (it marks the address so as to find it again), and closes it
at the end. macOS asks, once, whether the
terminal may control Safari.

A unit's panel is compared with the stage tables through exercise_layer.expected(), the same function the other two
checks use, and the units are the ones exercise_layer.py clicked in Chrome - so run that first.

Output: 60_layer/exercise_safari.json - every address opened with what the page then showed, every unit with its
comparison, the sha256 of the two files opened and of every table read, and the UTC time. Exits 1 unless all held."""
import hashlib, json, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.argv = [sys.argv[0], "chrome", tempfile.gettempdir()]      # exercise_layer reads these when imported; importing it starts no browser
import exercise_layer as X                                      # the stage tables, and expected(): what a unit's panel should show

# The file's address, with a mark after it that the page ignores: it lets this script find its own window again and
# never touch another window that happens to show the same file.
BASE = "file://" + str(ROOT / "60_layer" / "index.html") + "?exercise=" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
DOC = f'(first document whose URL starts with "{BASE}")'
SEP = "\n<<<ictd>>>\n"
steps = []


def osa(script, limit=90):
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=limit)
    except subprocess.TimeoutExpired:
        raise SystemExit("Safari did not answer. Has this terminal been allowed to control Safari (System Settings, Privacy & Security, Automation)?")
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:400])
    return r.stdout.rstrip("\n")


def read():
    out = osa(f'tell application "Safari"\nset d to {DOC}\nreturn (name of d) & "{SEP}" & (URL of d) & "{SEP}" & (text of d)\nend tell'.replace("\n<<<ictd>>>\n", "\\n<<<ictd>>>\\n"))
    name, url, text = out.split(SEP, 2)
    return {"name": name, "url": url, "text": X.norm(text)}


def goto(part, until, wait_s=40):
    """Change the address of the window in place, then wait until the page shows what `until` asks for."""
    osa(f'tell application "Safari" to set URL of {DOC} to "{BASE}#{part}"')
    t0 = time.time()
    while True:
        time.sleep(0.6)
        s = read()
        if until(s) or time.time() - t0 > wait_s:
            return s


def say(control, did, happened, ok):
    steps.append({"control": control, "did": did, "happened": happened, "ok": bool(ok)})
    print(("PASS  " if ok else "FAIL  ") + f"[{control}] {did} -> {happened}", flush=True)


def sq(s):
    """Text with every space and line break taken out: Safari's text of a page breaks lines where a table cell does."""
    return "".join(str(s).split())


def in_order(text, wanted, after=""):
    """The ones of `wanted` that do not occur in `text` one after another, starting after the last `after`."""
    text = sq(text)
    pos, missing = max(text.rfind(sq(after)), 0) if after else 0, []
    for label, w in wanted:
        if not sq(w):
            continue
        i = text.find(sq(w), pos)
        if i < 0:
            missing.append((label, X.norm(w)))
        else:
            pos = i + len(sq(w))
    return missing


def main():
    files = {f: hashlib.sha256((ROOT / "60_layer" / f).read_bytes()).hexdigest() for f in ("index.html", "data.js")}
    prov = json.load(open(X.read("60_layer/layer.provenance.json")))
    raw = (ROOT / "60_layer" / "data.js").read_text(encoding="utf-8")
    D = json.loads(raw[len("window.ICTD_LAYER = "):].rstrip()[:-1])
    chrome = json.load(open(X.read("60_layer/exercise_chrome.json")))
    if chrome["summary"]["layer_run_utc"] != prov["run_utc"]:
        raise SystemExit("60_layer/exercise_chrome.json is of another build of the layer: run exercise_layer.py chrome first")
    sample = [u["opened"] for u in chrome["units"]]
    layers = [l for l in D["layers"] if not l.get("pending")]
    floors = [f["id"] for f in D["floors"]]

    def legend(layer, floor):
        counts = layer["counts"][floor] if layer.get("floored") else layer["counts"]["all"]
        return [X.norm(layer["legend_title"])] + [X.norm(f"{c['label']} ({counts[k]})") for k, c in enumerate(layer["classes"])]

    def shows(layer, floor):
        return lambda s: all(row in s["text"] for row in legend(layer, floor))

    version = osa('tell application "Safari" to get version')
    default = next(l for l in layers if l["id"] == D["default_layer"])
    osa(f'tell application "Safari" to make new document with properties {{URL:"{BASE}"}}')
    results = []
    try:
        t0 = time.time()
        while True:
            time.sleep(1.0)
            s = read()
            if (s["name"] == D["title"] and shows(default, D["default_floor"])(s)) or time.time() - t0 > 120:
                break
        say("page", f"opened {BASE} in the Safari application, version {version}, with no layer, floor or unit in the address",
            f"after {time.time() - t0:.0f} s the window's title is '{s['name']}', the page shows {len(s['text']):,} characters of text, and the legend is the default layer's ({default['id']}) at {D['default_floor']} ha with its {len(default['classes'])} classes and their counts",
            s["name"] == D["title"] and shows(default, D["default_floor"])(s) and X.norm(D["subtitle"]) in s["text"])
        # every layer, by its address
        for l in layers:
            floor = D["default_floor"]
            s = goto(f"layer={l['id']}&floor={floor}", shows(l, floor))
            rows = legend(l, floor)
            say("layer, by address", f"set the address to '#layer={l['id']}&floor={floor}'", f"the legend's title and {sum(r in s['text'] for r in rows[1:])} of its {len(rows) - 1} class rows, with their counts, are those of the layer's own record",
                shows(l, floor)(s))
        # every minimum of forest, on the Hansen layer
        hansen = next(l for l in layers if l["id"] == "hansen_loss")
        for f in floors:
            s = goto(f"layer=hansen_loss&floor={f}", shows(hansen, f))
            grey = legend(hansen, f)[-1]
            say("minimum forest, by address", f"set the address to '#layer=hansen_loss&floor={f}'", f"the legend reads '{grey}'" if grey in s["text"] else f"the legend does not read '{grey}'", shows(hansen, f)(s))
        # the sample of units, each opened by its id in the address
        agreement = next(l for l in layers if l["id"] == "agreement")
        last_legend_row = legend(agreement, D["default_floor"])[-1]
        for uid in sample:
            want = X.expected(uid)
            first = X.norm(want[0][1])
            s = goto(f"layer=agreement&floor={D['default_floor']}&unit={uid}", lambda s: uid in s["text"] and sq(first) in sq(s["text"]))
            panel, flag = want[:-1], want[-1]
            missing = in_order(s["text"], panel, after=last_legend_row)       # the panel comes after the legend in the page
            if sq(flag[1]) and sq(flag[1]) not in sq(s["text"]):
                missing.append((flag[0], X.norm(flag[1])))
            n = sum(1 for _, w in want if sq(w))
            results.append({"unit": uid, "type": "outside_village" if uid.startswith("OUTSIDE") else "lgd_panchayat", "found": n - len(missing), "of": n, "missing": missing})
            say("unit, by address", f"set the address to '#layer=agreement&floor={D['default_floor']}&unit={uid}'", f"{n - len(missing)} of {n} values the panel should show are in the page's text, in the panel's order" + (f"; missing: {missing[:3]}" if missing else ""), not missing)
        # the search, through the address
        uid = next(u for u in sample if u.startswith("OUTSIDE"))
        other = next(u for u in sample if u != uid)
        goto(f"layer=agreement&floor={D['default_floor']}&unit={other}", lambda s: other in s["text"])
        s = goto(f"layer=agreement&q={uid.lower()}", lambda s: sq(X.expected(uid)[0][1]) in sq(s["text"]) and uid in s["text"])
        say("search, by address", f"with unit {other} open, set the address to '#layer=agreement&q={uid.lower()}' (the id in lower case)", f"the panel shows unit {uid}" if uid in s["text"] else "the panel does not show it", uid in s["text"] and not in_order(s["text"], X.expected(uid)[:3], after=last_legend_row))
        s = goto("layer=agreement&q=zzzz%20no%20such%20place", lambda s: X.norm(D["search_none"]) in s["text"])
        say("search, by address", "set the address to a search for 'zzzz no such place'", f"the message '{D['search_none']}' is shown" if X.norm(D["search_none"]) in s["text"] else "no message", X.norm(D["search_none"]) in s["text"])
        # the two text panels
        marks = {"about": ["Units, not hectares", "The headline:", "Every unit kept"], "sources": ["ODbL 1.0", "CC BY-NC-SA 4.0"]}
        s = goto("layer=agreement", shows(agreement, D["default_floor"]))
        closed = not any(m in s["text"] for m in marks["about"])
        for which, words in marks.items():
            s = goto(f"layer=agreement&open={which}", lambda s: all(w in s["text"] for w in words))
            say("text panels, by address", f"set the address to '#layer=agreement&open={which}'", f"the page's text now holds {[w for w in words if w in s['text']]}" + ("; before it was opened it did not hold the first panel's words" if which == "about" else ""),
                all(w in s["text"] for w in words) and (closed or which != "about"))
        # an address the page cannot understand
        s = goto("layer=nosuchlayer&floor=7&unit=NOPE", shows(default, D["default_floor"]))
        say("address", "set the address to a layer, a floor and a unit that do not exist", f"the page went to its defaults: the legend is that of {default['id']} at {D['default_floor']} ha", shows(default, D["default_floor"])(s))
    finally:
        try:
            osa(f'tell application "Safari" to close {DOC}', limit=20)
        except Exception:
            pass
    found, of = sum(r["found"] for r in results), sum(r["of"] for r in results)
    summary = {"script": "scripts/exercise_layer_safari.py", "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "inputs": X.INPUTS, "browser": f"Safari {version} (the application)",
               "events_were": "none: the page was driven by its address alone and read back through AppleScript (title, address, the text shown); nothing was clicked",
               "opened": BASE, "layer_run_utc": prov["run_utc"], "files_sha256": files, "addresses_tried": len(steps), "addresses_as_expected": sum(s["ok"] for s in steps),
               "units_opened_by_address": len(results), "values_compared": of, "values_found": found,
               "not_looked_at": "the two kinds-of-unit boxes, the district list and the map itself: what they do is not written in the page's text"}
    print(f"\n{summary['addresses_as_expected']} of {summary['addresses_tried']} addresses showed what they should; {len(results)} units opened by address; {found} of {of} values the panels should show were in the page's text")
    json.dump({"summary": summary, "steps": steps, "units": results}, open(ROOT / "60_layer" / "exercise_safari.json", "w", encoding="utf-8"), indent=1, default=str)
    return 0 if summary["addresses_as_expected"] == summary["addresses_tried"] and found == of else 1


if __name__ == "__main__":
    sys.exit(main())
