"""Exercises the demo layer in a browser, as a person would, and compares what it shows with the stage tables.

    python scripts/exercise_layer.py chrome|webkit [folder for screenshots]

The layer is opened from disk (file://), on the build that is in 60_layer/.
Part A works every interactive element - the layer switcher, the minimum of forest, the kinds of unit, the district
list, the search, the three text panels, the legend, the map's own zoom and drag, the address, two window sizes - and
after each action reads what the page then shows.

Added 13 October 2026, with the owner's handoff of that day (a third button, Guide, and a loader): seven steps, and
nothing taken out. The loader is gone once the page says it is ready, having said its second message. The Guide button
opens the window the other two texts use, with the guide's first heading and a line of its last section, both read
here from docs/GUIDE.md; the window holds the guide's five pictures, each drawn and each as wide as the text; it
scrolls; Close shuts it; in a narrow window a table wider than it scrolls sideways inside itself and the window does
not; and an address that ends in #open=guide opens it. Part B clicks a seeded, stratified sample of units ON THE MAP and
compares every value the panel displays with the stage tables, rebuilt here without any of the layer builder's code.

chrome: a separate, headless Chrome with an empty profile, driven with real mouse and keyboard events through the
        DevTools protocol (_browser_chrome.py).
webkit: a WKWebView off the screen - the engine of Safari, not the Safari application - which takes no mouse, so the
        events are dispatched inside the page (_browser_webkit.py, wkdriver.swift; macOS only).
What neither shows is said in docs/LAYER.md: the district list is set through its change event (a native pop-up
cannot be clicked in a window that is not on a screen), and no other browser is tried.

Output: 60_layer/exercise_<browser>.json - every action with what happened, every unit clicked with its comparison,
the sha256 of the two files opened and of every table read, and the UTC time of the run. It exits 1 unless every
action did what it should, every displayed value equalled the tables, and the page raised no script error.
Screenshots go to the folder given, or to a temporary one; they are not an output."""
import hashlib, json, shutil, subprocess, sys, tempfile, time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from _browser_chrome import Chrome
from _browser_webkit import WebKit

BROWSER = sys.argv[1] if len(sys.argv) > 1 else "chrome"
if BROWSER not in ("chrome", "webkit"):
    sys.exit(__doc__)
SHOTS = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(tempfile.mkdtemp(prefix="ictd_layer_shots_"))
INPUTS = []


def read(path):
    """A file this check reads: recorded with its sha256 in the output."""
    p = ROOT / path
    if not any(i["path"] == path for i in INPUTS):
        INPUTS.append({"path": path, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return p


class InChrome(Chrome):
    """Chrome, with real input events."""
    name, clicked, wheeled = "Chrome", "clicked", "turned the mouse wheel"
    how = "real mouse and keyboard events sent through Chrome's DevTools protocol to a separate, headless Chrome"

    def fresh(self, url):
        Chrome.open(self, "about:blank", ready="true")
        return Chrome.open(self, url)

    def files(self):
        return sorted({u.split("/")[-1].split("#")[0] for u in self.requests})

    def clear_search(self):
        self.click_on("#search")
        self.js("document.getElementById('search').select()")
        self.key("Backspace", "Backspace", 8)

    def arrow_down(self):
        self.key("ArrowDown", "ArrowDown", 40)
        return True

    def dblclick(self, x, y):
        for kind, n in (("mousePressed", 1), ("mouseReleased", 1), ("mousePressed", 2), ("mouseReleased", 2)):
            self.cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left", buttons=1 if kind == "mousePressed" else 0, clickCount=n)
        time.sleep(1.2)

    def resize(self, w, h):
        self.cmd("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        time.sleep(1.0)

    def reset_size(self):
        self.cmd("Emulation.clearDeviceMetricsOverride")


class InWebKit:
    """WebKit in a WKWebView off the screen: events are dispatched in the page."""
    name, clicked, wheeled = "WebKit", "sent a click to", "sent a wheel event"
    how = "events dispatched inside the page (a control's own click(); mouse, wheel and key events built in script), in a WKWebView that lies off the screen"

    def __init__(self):
        self.w = WebKit()
        self.folder = str(ROOT / "60_layer")
        self.version = "WebKit " + subprocess.run(["defaults", "read", "/System/Library/Frameworks/WebKit.framework/Versions/A/Resources/Info", "CFBundleVersion"], capture_output=True, text=True).stdout.strip() + \
                       " (the engine of Safari " + subprocess.run(["defaults", "read", "/Applications/Safari.app/Contents/Info", "CFBundleShortVersionString"], capture_output=True, text=True).stdout.strip() + " on this machine)"

    js = lambda self, expression: self.w.js(expression)
    shot = lambda self, path: self.w.shot(path)
    close = lambda self: self.w.close()

    @property
    def errors(self):
        return self.w.js("window.__errors") or []

    def open(self, url):
        return self.w.open(url, self.folder)

    def fresh(self, url):
        self.w._cmd(op="open", url="about:blank", dir=self.folder)
        return self.w.open(url, self.folder)

    def files(self):
        # WebKit keeps no resource timings for local files: list instead every address the page's own elements point at.
        # Since 13 October 2026 an address that carries its own bytes (data:) is left out of that list: it is not a file, and nothing is loaded for it. The page gained one that day, the line in its head by
        # which it says that it has no icon; the guide's pictures, while its window is open, are five more. Chrome, which reports what it asked for, reports none of them at this step, and passed it unchanged.
        return sorted({u.split("/")[-1].split("#")[0] for u in [self.w.js("location.href")] + self.w.js("Array.from(document.querySelectorAll('[src], link[href]')).map(function(e){return e.src || e.href;})")
                       if not u.startswith("data:")})

    def centre(self, selector, nth=0):
        r = self.w.js(f"(function(){{var e=document.querySelectorAll({json.dumps(selector)})[{nth}]; if(!e) return null; e.scrollIntoView({{block:'nearest'}}); var b=e.getBoundingClientRect(); return [b.left+b.width/2, b.top+b.height/2, b.width, b.height];}})()")
        if not r or r[2] <= 0 or r[3] <= 0:
            raise RuntimeError(f"nothing to click at {selector} [{nth}]")
        return r[0], r[1]

    def click_on(self, selector, nth=0):
        x, y = self.centre(selector, nth)
        self.w.run(f"document.querySelectorAll({json.dumps(selector)})[{nth}].click();")
        time.sleep(0.5)
        return round(x), round(y)

    def _mouse(self, kinds, x, y, target="document.elementFromPoint(X, Y)", detail=1):
        self.w.run("var X=%r, Y=%r, t=%s; %s" % (x, y, target, "".join(
            f"t.dispatchEvent(new MouseEvent('{k}', {{bubbles:true, cancelable:true, view:window, clientX:X, clientY:Y, button:0, buttons:{1 if k in ('mousedown', 'mousemove') else 0}, detail:{detail}}}));" for k in kinds)))

    def click(self, x, y):
        self._mouse(("mousedown", "mouseup", "click"), x, y)
        time.sleep(0.6)

    def dblclick(self, x, y):
        self._mouse(("mousedown", "mouseup", "click", "mousedown", "mouseup", "click", "dblclick"), x, y, detail=2)
        time.sleep(1.5)

    def type(self, text):
        self.w.run(f"var e=document.getElementById('search'); e.focus(); e.value = e.value + {json.dumps(text)}; e.dispatchEvent(new Event('input', {{bubbles:true}}));")

    def clear_search(self):
        self.w.run("var e=document.getElementById('search'); e.focus(); e.value='';")

    def enter(self):
        self.w.run("document.getElementById('search').dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true}));")
        time.sleep(0.4)

    def arrow_down(self):
        return False                                    # a key's built-in action (moving between radio buttons) does not run for an event made in script

    def wheel(self, x, y, dy):
        """Over the map: a wheel event, which the map zooms on. Over a panel: script cannot make WebKit scroll by a wheel event, so the panel is scrolled by its own scrollTop."""
        on_map = self.w.js(f"!!document.elementFromPoint({x},{y}).closest('#map')")
        if on_map:
            self.w.run(f"document.getElementById('map').dispatchEvent(new WheelEvent('wheel', {{bubbles:true, cancelable:true, view:window, clientX:{x}, clientY:{y}, deltaY:{dy}, deltaMode:0}}));")
        else:
            self.w.run(f"var e=document.elementFromPoint({x},{y}); while (e && !(e.scrollHeight > e.clientHeight + 1 && /(auto|scroll)/.test(getComputedStyle(e).overflowY))) e = e.parentElement; if (e) e.scrollTop += {dy};")
        time.sleep(1.2)
        return True

    def drag(self, x0, y0, x1, y1, steps=8):
        self._mouse(("mousedown",), x0, y0)
        for i in range(1, steps + 1):
            self._mouse(("mousemove",), x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, target="document")
            time.sleep(0.05)
        self._mouse(("mouseup",), x1, y1, target="document")
        time.sleep(1.0)

    def resize(self, w, h):
        self.w.size(w, h)

    def reset_size(self):
        self.w.size(1500, 950)


URL = "file://" + str(ROOT / "60_layer" / "index.html")
# the guide (added 13 Oct 2026): what its window must hold is read from its one source, docs/GUIDE.md
GUIDE = read("docs/GUIDE.md").read_text(encoding="utf-8").splitlines()
GUIDE_FIRST = next(l[2:].strip() for l in GUIDE if l.startswith("# "))                              # its first heading
GUIDE_LAST = next(l.strip() for l in GUIDE[max(i for i, l in enumerate(GUIDE) if l.startswith("## ")) + 1:] if l.strip() and l[0] not in "-|!#" and not any(ch in l for ch in "*`["))      # a plain line of its last section
GUIDE_PICTURES = sum(1 for l in GUIDE if l.startswith("!["))                                         # the pictures it names
# the sixteen units of the first hand check (6 October 2026): left out, so that this sample is a fresh one
EARLIER = {"132731", "OUTSIDE_183", "133949", "137247", "OUTSIDE_3185", "137771", "131999", "138534", "132539", "133170", "135472", "OUTSIDE_1855", "131760", "OUTSIDE_1229", "OUTSIDE_3062", "OUTSIDE_3327"}
log, steps = [], []


def say(control, did, happened, ok):
    steps.append({"control": control, "did": did, "happened": happened, "ok": bool(ok)})
    print(("PASS  " if ok else "FAIL  ") + f"[{control}] {did} -> {happened}", flush=True)


# ---- the stage tables, read here ---------------------------------------------------------------------------------------------
R = lambda p: pd.read_csv(read(p), dtype={"unit_id": str, "pc11_district_code": str}).set_index("unit_id")
U, H, B, C, CB, A, N_, AL = (R(p) for p in ("10_units/units_attributes.csv", "20_degradation/hansen_by_unit.csv", "20_degradation/hansen_loss_by_canopy_band_by_unit.csv", "20_degradation/corestack_by_unit.csv",
                                            "20_degradation/corestack_by_unit_bands.csv", "20_degradation/agreement_by_unit.csv", "30_need/need_by_unit.csv", "40_allocation/allocation_by_unit.csv"))
OD = pd.read_csv(read("10_units/outside_village_district.csv"), dtype=str, keep_default_na=False).set_index("unit_id")
DN = pd.read_csv(read("00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"), dtype=str).set_index("pc11_district_code")["district"]
G = gpd.read_file(read("10_units/units.gpkg"), layer="units")
G["unit_id"] = G["unit_id"].astype(str)
G = G.set_index("unit_id")
HOW = {"label": "the name on the DataMeet polygon", "two checks against the label": "the panchayat polygons under it and its neighbours, which both contradict the name on the polygon",
       "area majority: the polygon has no district name": "the panchayat polygons under it (the polygon carries no district name)", "neighbours: the polygon has no district name": "its neighbours (the polygon carries no district name)"}
AGREE = {"both": "Both measures flag this unit", "hansen_only": "Hansen only (clearance)", "corestack_only": "CoRE Stack only (degradation)", "neither": "Neither",
         "zone_model_excluded": "East Coast zone model: left out of the headline comparison", "insufficient_forest": "Insufficient forest to assess"}
ha = lambda x: f"{x:,.2f} ha"
pc = lambda x: f"{x:,.2f} %"
lk = lambda x: "not recorded" if pd.isna(x) else f"Rs {x / 1e5:,.2f} lakh"
ND, NC = "not defined: no such land in this unit", "no census data for this land"


def expected(uid):
    """What the panel should display for one unit, in the order the page lists it: (label of the source, text)."""
    out = uid.startswith("OUTSIDE")
    h, b, c, cb, a, n, al, area = H.loc[uid], B.loc[uid], C.loc[uid], CB.loc[uid], A.loc[uid], N_.loc[uid], AL.loc[uid], float(U.loc[uid, "area_ha"])
    k = {key: sum(cb[f"class_{x}_ha_{band}"] for x in parts for band in ("gt10le30", "gt30")) for key, parts in
         {"lost": ["lost"], "deg": ["degradation"], "par": ["partial3", "partial4"], "noc": ["nochange"], "imp": ["improvement"], "gai": ["gained"]}.items()}
    val = sum(k.values())
    land10 = b.area_ha_gt10le30 + b.area_ha_gt30
    both = lambda x: ha(x) + (f"  ({pc(100 * x / val)})" if val > 0 else "")
    if out:
        o = OD.loc[uid]
        district = DN[o.pc11_district_code] + " (by " + HOW[o.assigned_by] + (", ambiguous: two districts within 5 points of each other" if o.ambiguous == "1" else "") + ")"
    else:
        district = DN[U.loc[uid, "pc11_district_code"]]
    ze, zc = float(cb.value_ha_zone_EPAHR), float(cb.value_ha_zone_ECPHR)
    zone = ("no land with a CoRE Stack class" if val <= 0 else "Eastern Plateau and Hills" if ze > 0 and zc == 0 else
            "East Coast Plains and Hills - the placebo test fails in this model: read its Degradation class with caution" if zc > 0 and ze == 0 else "both models: the unit straddles the two")
    name = U.loc[uid, "unit_name"]
    rows = [("unit name [units]", "(no name on the polygon)" if pd.isna(name) or not str(name).strip() else str(name).strip()),
            ("unit id", uid), ("type", "Outside-village unit: land outside any revenue village" if out else "LGD panchayat unit"), ("district", district), ("area_ha [units]", ha(area)),
            ("forest_ha [hansen_by_unit]", ha(h.forest_ha)), ("forest % of area", pc(100 * h.forest_ha / area)), ("hansen_loss_ha", ha(h.hansen_loss_ha)),
            ("loss % of forest", pc(100 * h.hansen_loss_ha / h.forest_ha) if h.forest_ha > 0 else ND), ("loss 2017-2023 on the mask", ha(sum(h[f"hansen_loss_ha_{y}"] for y in range(2017, 2024)))),
            ("land tc>10 [canopy bands]", ha(land10)), ("land 10-30", ha(b.area_ha_gt10le30)), ("loss on 10-30", ha(b.loss_ha_gt10le30)),
            ("loss % of 10-30", pc(100 * b.loss_ha_gt10le30 / b.area_ha_gt10le30) if b.area_ha_gt10le30 > 0 else ND), ("land <=10", ha(b.area_ha_le10)), ("loss on <=10", ha(b.loss_ha_le10)), ("loss on zero canopy", ha(b.loss_ha_eq0)),
            ("CoRE land with a class [bands]", ha(val)), ("Deforestation", both(k["lost"])), ("Degradation", both(k["deg"])), ("Partially Degraded", both(k["par"])), ("No Change", both(k["noc"])), ("Improvement", both(k["imp"])),
            ("Afforestation", both(k["gai"])), ("Degradation minus Improvement", f"{100 * (k['deg'] - k['imp']) / val:,.2f} points" if val > 0 else ND), ("Degradation, all land [corestack_by_unit]", ha(c.corestack_degradation_ha)),
            ("tree cover at the start, all land", ha(c.corestack_tree_cover_start_ha)), ("agreement_class [agreement_by_unit]", AGREE[a.agreement_class]), ("agreement_class_all_assessed", AGREE[a.agreement_class_all_assessed]),
            ("zone model [corestack bands]", zone), ("Hansen rate 2017-2023 x 100", pc(100 * sum(b[f"loss_ha_{band}_{y}"] for band in ("gt10le30", "gt30") for y in range(2017, 2024)) / land10) if land10 > 0 else ND),
            ("CoRE Degradation rate x 100", pc(100 * k["deg"] / val) if val > 0 else ND), ("reference land", ha(land10)), ("n_works [allocation]", f"{int(al.n_works):,}"), ("expenditure_total", lk(al.expenditure_total)),
            ("expenditure_plantation_category", lk(al.expenditure_plantation_category)), ("expenditure_forest_named_worktype", lk(al.expenditure_forest_named_worktype)), ("expenditure_water", lk(al.expenditure_water))]
    rows += [(x, NC) for x in ("population", "households", "st_share", "sc_share", "adi_2011")] if out else [
        ("population [need]", f"{int(round(n.population)):,}"), ("households", f"{int(round(n.households)):,}"), ("st_share x 100", pc(100 * n.st_share) if not pd.isna(n.st_share) else "not defined: no resident population"),
        ("sc_share x 100", pc(100 * n.sc_share) if not pd.isna(n.sc_share) else "not defined: no resident population"), ("adi_2011", f"{n.adi_2011:,.2f}" if not pd.isna(n.adi_2011) else "no index for this unit's villages")]
    flag = ("Under 1 ha of forest: this unit cannot be assessed for forest loss." if h.forest_ha < 1 else
            "Under 100 ha of forest: below the minimum we use, because a loss rate on this little forest may not repeat from one set of years to the next." if h.forest_ha < 100 else "")
    return rows + [("warning on small forests", flag)]


READ_PANEL = """(function(){
  var i = document.getElementById('info'), h1 = i.querySelector('h1'), flag = i.querySelector('.flag');
  if (!h1) return null;
  var cells = Array.from(i.querySelectorAll('table.kv tr')).map(function(tr){ return tr.cells[1].textContent; });
  // the page lists the Hansen rows as forest, share, loss, share, lost 2017-2023, land above 10 %: put 'land above 10 %' where the tables' order has it
  return {name: h1.textContent, cells: cells, flag: flag ? flag.textContent : '', sections: Array.from(i.querySelectorAll('h3')).map(function(e){return e.textContent;}), bar: i.querySelectorAll('.bar span').length};
})()"""
norm = lambda s: " ".join(str(s).split())


def read_panel(c):
    p = c.js(READ_PANEL)
    if not p:
        return None
    v = p["cells"]
    # DOM order of the Hansen block: forest, share, loss, share, 2017-2023, land>10  ->  expected() order: forest, share, loss, share, 2017-2023, land>10 (the same)
    return {"shown": [p["name"]] + v + [p["flag"]], "sections": p["sections"], "bar": p["bar"]}


def compare(c, uid_target, why):
    p = read_panel(c)
    if p is None:
        return {"why": why, "target": uid_target, "opened": None, "equal": 0, "of": 0, "bad": ["no panel opened"]}
    opened = p["shown"][1]
    want = expected(opened)
    bad = [(want[i][0], p["shown"][i], want[i][1]) for i in range(max(len(want), len(p["shown"]))) if i >= len(want) or i >= len(p["shown"]) or norm(p["shown"][i]) != norm(want[i][1])]
    return {"why": why, "target": uid_target, "opened": opened, "type": "outside_village" if opened.startswith("OUTSIDE") else "lgd_panchayat", "forest_ha": float(H.loc[opened, "forest_ha"]),
            "agreement_class": A.loc[opened, "agreement_class"], "equal": len(want) - len(bad), "of": len(want), "bad": bad, "sections": len(p["sections"]), "bar_segments": p["bar"]}


def point(uid):
    g = G.loc[uid, "geometry"]
    q = g.representative_point()
    w, s, e, n = g.bounds
    return (q.y, q.x), [[s, w], [n, e]]


def to_screen(c, latlng):
    return c.js(f"(function(){{var p=ICTD_MAP.latLngToContainerPoint({json.dumps(list(latlng))}), b=document.getElementById('map').getBoundingClientRect(); return [b.left+p.x, b.top+p.y];}})()")


def pixel(c, x, y):
    return c.js(f"(function(){{var cv=document.querySelector('#map canvas'), b=cv.getBoundingClientRect(), s=cv.width/b.width; var d=cv.getContext('2d').getImageData(Math.round(({x}-b.left)*s), Math.round(({y}-b.top)*s),1,1).data; "
                "return '#'+[d[0],d[1],d[2]].map(function(v){return ('0'+v.toString(16)).slice(-2);}).join('') + (d[3]===0?' (nothing drawn)':'');})()")


def state(c):
    return c.js("""(function(){var q=function(n){var e=document.querySelector('input[name='+n+']:checked'); return e?e.value:null;};
      var drawn=0, lgd=0, out=0; ICTD_MAP.eachLayer(function(l){ if(l._u!==undefined){drawn++; if(window.ICTD_LAYER.out.charAt(l._u)==='1'){out++;}else{lgd++;}} });
      return {layer:q('layer'), floor:q('floor'), lgd:document.getElementById('c_lgd').checked, out:document.getElementById('c_out').checked, drawn_lgd:lgd, drawn_out:out,
              hash:location.hash, zoom:ICTD_MAP.getZoom(), centre:[ICTD_MAP.getCenter().lat, ICTD_MAP.getCenter().lng], legend_title:(document.querySelector('#legend .t')||{}).textContent,
              legend:Array.from(document.querySelectorAll('#legend .lr')).map(function(e){return e.textContent.trim();}), modal:getComputedStyle(document.getElementById('modal')).display,
              district:document.getElementById('district').value, searchmsg:document.getElementById('searchmsg').textContent, search:document.getElementById('search').value,
              unit:(function(){var r=document.querySelector('#info table.kv tr'); return r?r.cells[1].textContent:null;})(), highlighted:(function(){var n=0; ICTD_MAP.eachLayer(function(l){ if(l.options&&l.options.weight===3&&l.options.fill===false){n++;} }); return n;})()};})()""")


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    files = {f: hashlib.sha256((ROOT / "60_layer" / f).read_bytes()).hexdigest() for f in ("index.html", "data.js")}
    prov = json.load(open(read("60_layer/layer.provenance.json")))
    profile = tempfile.mkdtemp(prefix="ictd_chrome_profile_") if BROWSER == "chrome" else None      # an empty profile, made here and removed at the end
    c = InChrome(profile, port=9334) if BROWSER == "chrome" else InWebKit()
    try:
        t = c.open(URL)
        D = c.js("(function(){var D=window.ICTD_LAYER; return {layers:D.layers.map(function(l){return {id:l.id,title:l.title,pending:l.pending||'',legend_title:l.legend_title||'',floored:!!l.floored,counts:l.counts||{},classes:(l.classes||[]).map(function(x){return [x.label,x.color];}),cls:null};}), floors:D.floors, n:D.id.length, default_layer:D.default_layer, default_floor:D.default_floor, districts:D.districts.map(function(d){return {name:d.name,bbox:d.bbox,n:d.n_units};}), codes:D.codes};})()")
        say("page", f"opened {URL} in {c.version}", f"ready in {t} s; files loaded: {c.files()}; script errors: {c.errors or 'none'}", c.files() == ["data.js", "index.html"] and not c.errors)
        s0 = state(c)
        say("page", "read the starting state", f"layer {s0['layer']}, floor {s0['floor']} ha, both kinds of unit shown ({s0['drawn_lgd']:,} + {s0['drawn_out']:,} drawn), no unit selected, legend '{s0['legend_title'][:50]}...'",
            s0["layer"] == D["default_layer"] and s0["floor"] == D["default_floor"] == "100" and s0["drawn_lgd"] + s0["drawn_out"] == D["n"] and s0["unit"] is None)
        c.shot(SHOTS / "A00_start.png")
        # the loader (added 13 Oct 2026): over the map's area while the page opens, gone once the page says it is ready
        lo = c.js("(function(){var l=document.getElementById('loading'), m=document.getElementById('loadmsg'); return {there:!!l, shown:!!l&&getComputedStyle(l).display!=='none', said:m?m.textContent:null, ready:window.ICTD_READY===true};})()")
        own_file = read("60_layer/index.html").read_text(encoding="utf-8")
        first_words = '<p id="loadmsg">Loading the map&hellip;</p>'
        say("loader", "read the loader once the page said it was ready", f"it is no longer shown; the last thing it said was '{lo['said']}'; in the page's own file its first words, 'Loading the map\u2026', are plain markup "
            "that stands before the tag that asks for data.js",
            lo["there"] and not lo["shown"] and lo["ready"] and lo["said"] == "Drawing the units\u2026" and own_file.count(first_words) == 1 and own_file.index(first_words) < own_file.index('<script src="data.js">'))
        selectable = [l for l in D["layers"] if not l["pending"]]

        # a large LGD unit to watch the colour of, and a unit between 50 and 100 ha of forest to watch the floor on
        lgd_ids = [i for i in U.index if not i.startswith("OUTSIDE")]
        watch = max(lgd_ids, key=lambda i: float(U.loc[i, "area_ha"]) if float(H.loc[i, "forest_ha"]) > 200 else 0)
        mid = max([i for i in lgd_ids if 50 <= float(H.loc[i, "forest_ha"]) < 100 and float(H.loc[i, "hansen_loss_ha"]) > 0], key=lambda i: float(U.loc[i, "area_ha"]))
        cls_of = lambda layer, setting, uid: c.js(f"(function(){{var D=window.ICTD_LAYER,l=D.layers.filter(function(x){{return x.id==={json.dumps(layer)};}})[0],k=D.id.indexOf({json.dumps(uid)}); var s=l.floored?l.cls[{json.dumps(setting)}]:l.cls.all; var cl=l.classes[D.codes.indexOf(s.charAt(k))]; return [cl.label, cl.color];}})()")

        # ---- A1. the layer switcher: every layer, by a real click on its radio button ------------------------------------------
        ll, bb = point(watch)
        c.js(f"(function(){{ ICTD_MAP.fitBounds({json.dumps(bb)}, {{animate:false, padding:[80,80]}}); return 0; }})()"); time.sleep(0.8)
        wx, wy = to_screen(c, ll)
        for l in selectable:
            x, y = c.click_on(f"input[name=layer][value={l['id']}]")
            time.sleep(0.9)
            s = state(c)
            label, colour = cls_of(l["id"], s["floor"], watch)
            px = pixel(c, wx, wy)
            want_counts = l["counts"][s["floor"]] if l["floored"] else l["counts"]["all"]
            legend_ok = s["legend_title"] == l["legend_title"] and all(f"{lab} ({want_counts[i]})" == s["legend"][i] for i, (lab, _) in enumerate(l["classes"]))
            say("layer switcher", f"{c.clicked} the radio button '{l['title']}' at ({x}, {y})",
                f"it became the checked layer; the legend's title and its {len(l['classes'])} classes with their counts became this layer's; the address reads '{s['hash']}'; unit {watch} (class '{label}') is drawn {px}, the class colour {colour}",
                s["layer"] == l["id"] and legend_ok and f"layer={l['id']}" in s["hash"] and px.lower() == colour.lower() and not c.errors)
            c.shot(SHOTS / f"A1_layer_{l['id']}.png")
        before = state(c)
        x, y = c.click_on("#layers .pending")
        s = state(c)
        say("layer switcher", f"{c.clicked} the greyed entry 'Greenness trend (NIRv) - tested, not used' at ({x}, {y})", "nothing changed: it is text, not a control", s["layer"] == before["layer"] and s["legend_title"] == before["legend_title"])
        c.click_on("input[name=layer][value=hansen_loss]"); time.sleep(0.6)
        c.js("(function(){document.querySelector('input[name=layer][value=hansen_loss]').focus(); return 0;})()")
        if c.arrow_down():
            s = state(c)
            say("layer switcher", "with the keyboard: Arrow Down on the focused radio button", f"the next layer, '{s['layer']}', became the layer and the legend followed", s["layer"] == "canopy_band_loss" and "10 to 30" in s["legend_title"])
        else:
            say("layer switcher", "did not try the keyboard", "a key's built-in action does not run for an event made in script: not exercised in this browser", True)

        # ---- A2. the minimum-forest setting ------------------------------------------------------------------------------------------
        c.click_on("input[name=layer][value=hansen_loss]"); time.sleep(0.6)
        ll, bb = point(mid)
        c.js(f"(function(){{ ICTD_MAP.fitBounds({json.dumps(bb)}, {{animate:false, padding:[80,80]}}); return 0; }})()"); time.sleep(0.8)
        mx, my = to_screen(c, ll)
        fh = H["forest_ha"].astype(float)
        for f in ("50", "1", "100"):
            x, y = c.click_on(f"input[name=floor][value='{f}']")
            time.sleep(0.9)
            s = state(c)
            grey = [r for r in s["legend"] if r.startswith("Insufficient forest to assess")][0]
            want = int((fh < float(f)).sum())
            label, colour = cls_of("hansen_loss", f, mid)
            px = pixel(c, mx, my)
            say("minimum forest", f"{c.clicked} '{f} ha' at ({x}, {y}) with the Hansen loss layer on",
                f"legend: '{grey}' (hansen_by_unit.csv has {want:,} units under {f} ha of forest); unit {mid}, with {fh[mid]:,.1f} ha of forest, is drawn {px} = '{label}' ({colour}); address '{s['hash']}'",
                s["floor"] == f and f"({want:,} units)" in grey and px.lower() == colour.lower() and (label == "Insufficient forest to assess") == (fh[mid] < float(f)) and f"floor={f}" in s["hash"])
            c.shot(SHOTS / f"A2_floor_{f}.png")
        c.click_on("input[name=layer][value=agreement]"); time.sleep(0.7)
        a100 = state(c)["legend"]
        c.click_on("input[name=floor][value='1']"); time.sleep(0.7)
        say("minimum forest", f"with the agreement layer on, {c.clicked} '1 ha'", "the agreement legend did not change: that layer has its own floor", state(c)["legend"] == a100)
        c.click_on("input[name=floor][value='100']"); time.sleep(0.5)

        # ---- A3. which kinds of unit are shown ----------------------------------------------------------------------------------------
        c.js("(function(){ ICTD_MAP.fitBounds(window.ICTD_LAYER.bounds, {animate:false}); return 0; })()"); time.sleep(0.8)
        n_out, n_lgd = int(U.index.str.startswith("OUTSIDE").sum()), int((~U.index.str.startswith("OUTSIDE")).sum())
        for sel, what, want in (("#c_lgd", "unticked 'Panchayat units'", (0, n_out, "show=out")), ("#c_out", "unticked 'Land outside villages'", (0, 0, "show=none")),
                                ("#c_lgd", "ticked 'Panchayat units' again", (n_lgd, 0, "show=lgd")), ("#c_out", "ticked 'Land outside villages' again", (n_lgd, n_out, ""))):
            x, y = c.click_on(sel)
            time.sleep(1.2)
            s = state(c)
            say("units shown", f"{what} at ({x}, {y})", f"{s['drawn_lgd']:,} LGD panchayat and {s['drawn_out']:,} outside-village units are drawn; address '{s['hash']}'",
                (s["drawn_lgd"], s["drawn_out"]) == want[:2] and (want[2] in s["hash"] if want[2] else "show=" not in s["hash"]))
            c.shot(SHOTS / f"A3_shown_{want[2] or 'both'}.png")

        # ---- A4. go to a district --------------------------------------------------------------------------------------------------------
        inside = lambda s, bbox: c.js(f"ICTD_MAP.getBounds().pad(0.02).contains({json.dumps(bbox)})")
        # The district list is a native pop-up menu. In a headless window the operating system draws it and, once opened by a
        # click, it swallows every later mouse event (measured: after such a click the zoom button stopped answering). So the
        # list is NOT clicked here: each choice is made by setting the list and sending the change event its handler listens for.
        say("go to a district", "did not click the district list", "a native pop-up menu cannot be operated in a headless window (opening it there swallowed all later input); the choices below set the list and send its change event", True)
        moved, late = 0, []
        for k, d in enumerate(D["districts"]):
            c.js(f"(function(){{var e=document.getElementById('district'); e.value='{k}'; e.dispatchEvent(new Event('change', {{bubbles:true}})); return 0;}})()")
            for _ in range(12):                                             # the move is animated: wait until it has ended, at most three seconds
                time.sleep(0.25)
                if inside(None, d["bbox"]):
                    break
            else:
                late.append(d["name"])
            moved += bool(inside(None, d["bbox"]))
        say("go to a district", f"chose each of the {len(D['districts'])} districts in the list in turn", f"the map moved so that the whole district was in view for {moved} of {len(D['districts'])}" + (f" (not within three seconds: {late})" if late else ""),
            moved == len(D["districts"]) == 30)
        c.js("(function(){var e=document.getElementById('district'); e.value=''; e.dispatchEvent(new Event('change', {bubbles:true})); return 0;})()")
        say("go to a district", "chose the first line of the list, 'Jump to a district...'", "nothing moved and nothing broke", not c.errors)

        # ---- A5. the search box -------------------------------------------------------------------------------------------------------------
        def search(text):
            x, y = c.centre("#search")
            c.clear_search()
            if text:
                c.type(text)
            c.enter(); time.sleep(1.3)
            return state(c), (round(x), round(y))
        target = [i for i in U.index if i.startswith("OUTSIDE") and i not in EARLIER and float(H.loc[i, "forest_ha"]) > 3000][3]
        s, (x, y) = search(target)
        say("search", f"put the id '{target}' in the box at ({x}, {y}) and pressed Enter", f"the panel opened unit {s['unit']}, the map flew to it and outlined it ({s['highlighted']} outline), no message; address '{s['hash']}'",
            s["unit"] == target and s["searchmsg"] == "" and s["highlighted"] == 1 and f"unit={target}" in s["hash"])
        c.shot(SHOTS / "A5_search_id.png")
        s, _ = search(target.lower())
        say("search", f"typed the id in lower case, '{target.lower()}'", f"the same unit, {s['unit']}", s["unit"] == target)
        names = U["unit_name"].dropna().astype(str)
        many = names[names.str.lower().str.contains("pur")]
        s, _ = search("PUR")
        say("search", "typed part of a name, 'PUR' (in capitals), pressed Enter", f"message: '{s['searchmsg']}'; the unit opened is {s['unit']} ('{U.loc[s['unit'], 'unit_name']}'); units_attributes.csv has {len(many):,} names containing 'pur'",
            s["searchmsg"] == f"{len(many):,} units match; showing the first. Add more of the name, or use the id." and "pur" in str(U.loc[s["unit"], "unit_name"]).lower())
        one = names[names.str.lower().map(lambda v: (names.str.lower().str.contains(v, regex=False)).sum() == 1)]
        one = one[[i for i in one.index if i not in EARLIER]].iloc[5:6]
        s, _ = search(one.iloc[0])
        say("search", f"typed a name only one unit has, '{one.iloc[0]}'", f"unit {s['unit']} opened, no message", s["unit"] == one.index[0] and s["searchmsg"] == "")
        prev = s["unit"]
        s, _ = search("zzzz no such place")
        say("search", "typed 'zzzz no such place', pressed Enter", f"message: '{s['searchmsg']}'; the unit shown stayed {s['unit']}", s["searchmsg"] == "No unit with that name or id." and s["unit"] == prev)
        s, _ = search("")
        say("search", "emptied the box and pressed Enter", "nothing changed", s["unit"] == prev and not c.errors)

        # ---- A6. the three text panels (the third, the Guide, added 13 Oct 2026) ---------------------------------------------------------------
        for btn, name, must in (("#b_about", "About this map", ["Units, not hectares", "The headline:", "Every unit kept", "Small forests are greyed out"]), ("#b_sources", "Sources", ["ODbL 1.0", "CC BY-NC-SA 4.0", "Leaflet 1.9.4"]),
                                ("#b_guide", "Guide", [GUIDE_FIRST, GUIDE_LAST])):
            x, y = c.click_on(btn); time.sleep(0.5)
            txt = c.js("document.getElementById('modalbody').textContent")
            s = state(c)
            if btn != "#b_guide":
                say("text panels", f"{c.clicked} the button '{name}' at ({x}, {y})", f"the panel opened ({len(txt):,} characters) and holds {must}", s["modal"] == "block" and all(m in txt for m in must))
            else:
                g = c.js("(function(){var b=document.getElementById('modalbody'), h=b.querySelector('h1'); return {h1:h?h.textContent:'', first:b.textContent.trim().slice(0, 60), top:b.parentNode.scrollTop};})()")
                say("text panels", f"{c.clicked} the button '{name}' at ({x}, {y})", f"the same panel opened, at its top ({len(txt):,} characters), under the guide's first heading, '{g['h1']}', and it holds a line of the guide's "
                    f"last section, '{GUIDE_LAST}'", s["modal"] == "block" and all(m in txt for m in must) and g["h1"] == GUIDE_FIRST and g["first"].startswith(GUIDE_FIRST) and g["top"] == 0)
                pics = []
                for _ in range(40):                                  # a picture is decoded a moment after its HTML is put into the window
                    pics = c.js("Array.from(document.querySelectorAll('#modalbody img')).map(function(i){return {done:i.complete, w:i.naturalWidth, h:i.naturalHeight, shown:Math.round(i.getBoundingClientRect().width), "
                                "text:Math.round(document.getElementById('modalbody').getBoundingClientRect().width), here:(i.getAttribute('src')||'').slice(0, 23)};})")
                    if pics and all(q["done"] for q in pics):
                        break
                    time.sleep(0.25)
                say("text panels", "read the pictures in the Guide's panel", f"{len(pics)} pictures, as many as docs/GUIDE.md names ({GUIDE_PICTURES}); each is drawn, at its natural size of "
                    f"{sorted(set((q['w'], q['h']) for q in pics))}, from its own bytes inside the page; each is as wide as the text ({sorted(set(q['shown'] for q in pics))} px of {sorted(set(q['text'] for q in pics))} px)",
                    len(pics) == GUIDE_PICTURES == 5 and all(q["done"] and q["w"] > 0 and q["h"] > 0 and abs(q["shown"] - q["text"]) <= 2 and q["here"] == "data:image/webp;base64," for q in pics))
            c.shot(SHOTS / f"A6_{btn[3:]}.png")
            bx, by = c.centre("#modal .box")
            c.wheel(bx, by, 600)
            top = c.js("document.querySelector('#modal .box').scrollTop")
            say("text panels", f"{c.wheeled} over the panel" if BROWSER == "chrome" else "scrolled the panel by its own scroll position (script cannot scroll WebKit with a wheel event)", f"it scrolled ({top:.0f} px)", top > 0)
            if btn in ("#b_about", "#b_guide"):
                x, y = c.click_on("#b_close"); time.sleep(0.4)
                say("text panels", f"{c.clicked} 'Close' at ({x}, {y})", "the panel closed", state(c)["modal"] == "none")
            else:
                c.click(40, 500); time.sleep(0.4)
                say("text panels", f"{c.clicked} the dimmed page beside the panel, at (40, 500)", "the panel closed", state(c)["modal"] == "none")
        # the Guide's panel in a narrow window (added 13 Oct 2026): a table wider than the panel scrolls sideways inside itself, and the panel does not
        c.resize(380, 700)
        c.js("(function(){document.getElementById('b_guide').click(); return 0;})()"); time.sleep(0.8)
        n = c.js("(function(){var b=document.getElementById('modalbody'), box=b.parentNode; return {open:getComputedStyle(document.getElementById('modal')).display, box:[box.clientWidth, box.scrollWidth], "
                 "tables:Array.from(b.querySelectorAll('.wide')).map(function(w){return [w.clientWidth, w.scrollWidth, getComputedStyle(w).overflowX];}), "
                 "pics:Array.from(b.querySelectorAll('img')).map(function(i){return [Math.round(i.getBoundingClientRect().width), Math.round(b.getBoundingClientRect().width)];})};})()")
        wider = [w for w in n["tables"] if w[1] > w[0] + 1]
        say("text panels", "made the window 380 x 700 and opened the Guide", f"its panel is {n['box'][0]} px wide and does not scroll sideways (its content is {n['box'][1]} px wide); {len(wider)} of its {len(n['tables'])} tables are "
            f"wider than the panel, and each of those scrolls sideways inside itself; each picture is as wide as the text ({sorted(set(q[0] for q in n['pics']))} px)",
            n["open"] == "block" and n["box"][1] <= n["box"][0] + 1 and len(wider) >= 1 and all(w[2] in ("auto", "scroll") for w in n["tables"]) and len(n["pics"]) == GUIDE_PICTURES and all(abs(q[0] - q[1]) <= 2 for q in n["pics"]))
        c.shot(SHOTS / "A6_guide_narrow.png")
        c.js("(function(){document.getElementById('b_close').click(); return 0;})()"); time.sleep(0.3)
        c.reset_size()

        # ---- A6b. the legend's Hide / Show button ---------------------------------------------------------------------------------------------
        size = lambda: c.js("(function(){var b=document.getElementById('legend').getBoundingClientRect(), m=document.getElementById('map').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height), Math.round(m.width), Math.round(m.height), document.querySelectorAll('#legend .lr').length, document.getElementById('legend').scrollWidth - document.getElementById('legend').clientWidth];})()")
        c.click_on("input[name=layer][value=agreement]"); time.sleep(0.6)
        b0 = size()
        say("legend", "read the legend of the agreement layer, the one with the longest class name", f"it is {b0[0]} x {b0[1]} px on a map of {b0[2]} x {b0[3]} px, lists {b0[4]} rows, and nothing in it runs past its edge", b0[4] == 7 and b0[5] <= 0 and b0[1] <= b0[3] - 30)
        x, y = c.click_on("#b_legend"); time.sleep(0.4)
        b1 = size()
        say("legend", f"{c.clicked} its 'Hide' button at ({x}, {y})", f"the legend shrank to its title ({b1[0]} x {b1[1]} px, {b1[4]} rows) and the button now reads '{c.js('document.getElementById(\'b_legend\').textContent')}'",
            b1[4] == 0 and b1[1] < 80 and c.js("document.getElementById('b_legend').textContent") == "Show")
        c.click_on("input[name=layer][value=st_share]"); time.sleep(0.6)
        s = state(c)
        say("legend", "changed the layer while the legend was hidden", f"it stayed hidden and its title became the new layer's ('{s['legend_title'][:40]}...')", size()[4] == 0 and "Scheduled Tribe" in s["legend_title"])
        c.shot(SHOTS / "A6b_legend_hidden.png")
        x, y = c.click_on("#b_legend"); time.sleep(0.4)
        b2 = size()
        say("legend", f"{c.clicked} 'Show' at ({x}, {y})", f"the legend came back with {b2[4]} rows", b2[4] == 7 and c.js("document.getElementById('b_legend').textContent") == "Hide")

        # ---- A7. the map itself: zoom buttons, wheel, drag, double click ----------------------------------------------------------------------------
        c.js("(function(){ ICTD_MAP.fitBounds(window.ICTD_LAYER.bounds, {animate:false}); return 0; })()"); time.sleep(0.8)
        z0 = state(c)["zoom"]
        x, y = c.click_on(".leaflet-control-zoom-in"); time.sleep(1.0)
        z1 = state(c)["zoom"]
        say("map", f"{c.clicked} '+' at ({x}, {y})", f"zoom went from {z0} to {z1}", z1 > z0)
        x, y = c.click_on(".leaflet-control-zoom-out"); time.sleep(1.0)
        z2 = state(c)["zoom"]
        say("map", f"{c.clicked} '-' at ({x}, {y})", f"zoom went back to {z2}", z2 < z1)
        mx, my = c.centre("#map")
        c.wheel(mx, my, -400); time.sleep(1.0)
        z3 = state(c)["zoom"]
        say("map", f"{c.wheeled} (upwards) over the middle of the map", f"zoom went from {z2} to {z3}", z3 > z2)
        c0 = state(c)["centre"]
        c.drag(mx, my, mx - 180, my - 120); time.sleep(0.8)
        c1 = state(c)["centre"]
        say("map", "dragged the map 180 px left and 120 px up" + ("" if BROWSER == "chrome" else " (mouse-down, eight mouse-moves and mouse-up, made in script)"), f"its centre moved from {c0[0]:.3f} N {c0[1]:.3f} E to {c1[0]:.3f} N {c1[1]:.3f} E, and the unit that was open stayed open", c1[1] > c0[1] and c1[0] < c0[0] and state(c)["unit"] == prev)
        c.dblclick(mx, my)
        z4 = state(c)["zoom"]
        say("map", "double-clicked the middle of the map", f"zoom went from {z3} to {z4}", z4 > z3)
        c.shot(SHOTS / "A7_map_zoomed.png")

        # ---- A8. the address: every state by a link, and a link changed while the page is open -------------------------------------------------------
        t = c.fresh(URL + f"#layer=agreement&floor=50&show=out&unit={target}&district=Koraput&open=sources")
        s = state(c)
        say("address", "closed the page, then opened the file afresh with '#layer=agreement&floor=50&show=out&unit=...&district=Koraput&open=sources'",
            f"layer {s['layer']}, floor {s['floor']}, {s['drawn_lgd']} LGD and {s['drawn_out']:,} outside-village units drawn, unit {s['unit']} open, district list on '{D['districts'][int(s['district'])]['name'] if s['district'] else ''}', the Sources panel open",
            s["layer"] == "agreement" and s["floor"] == "50" and s["drawn_lgd"] == 0 and s["drawn_out"] == n_out and s["unit"] == target and s["district"] != "" and D["districts"][int(s["district"])]["name"] == "Koraput" and s["modal"] == "block")
        c.click_on("#b_close")
        c.js("(function(){ location.hash = 'layer=st_share&floor=100&show=both&q=' + encodeURIComponent(" + json.dumps(one.iloc[0]) + "); return 0; })()"); time.sleep(1.8)
        s = state(c)
        say("address", "changed the address in place to '#layer=st_share&floor=100&show=both&q=<a unit's name>'", f"the page followed: layer {s['layer']}, floor {s['floor']}, all {s['drawn_lgd'] + s['drawn_out']:,} units drawn, unit {s['unit']} open",
            s["layer"] == "st_share" and s["floor"] == "100" and s["drawn_lgd"] + s["drawn_out"] == D["n"] and s["unit"] == one.index[0])
        c.js("(function(){ location.hash = 'layer=nirv&floor=7&unit=NO_SUCH_UNIT'; return 0; })()"); time.sleep(1.5)
        s = state(c)
        say("address", "changed the address in place to a layer that is greyed out and cannot be chosen (NIRv), a floor that does not exist and a unit that does not exist", f"layer and floor went to their defaults ({s['layer']}, {s['floor']} ha); the unit already open, {s['unit']}, stayed open; no error",
            s["layer"] == D["default_layer"] and s["floor"] == "100" and s["unit"] == one.index[0] and not c.errors)
        t = c.fresh(URL + "#layer=nirv&floor=7&unit=NO_SUCH_UNIT&show=sideways&district=Atlantis&q=&open=nothing")
        s = state(c)
        say("address", "closed the page, then opened the file afresh with nonsense in every part of the address", f"the page opened on its defaults: layer {s['layer']}, floor {s['floor']} ha, all {s['drawn_lgd'] + s['drawn_out']:,} units drawn, no unit open, no panel, no error",
            s["layer"] == D["default_layer"] and s["floor"] == "100" and s["unit"] is None and s["drawn_lgd"] + s["drawn_out"] == D["n"] and s["modal"] == "none" and not c.errors)
        t = c.fresh(URL + "#open=guide")                           # added 13 Oct 2026: an address that ends in #open=guide opens the Guide
        s = state(c)
        g = c.js("(function(){var b=document.getElementById('modalbody'), h=b.querySelector('h1'); return {h1:h?h.textContent:'', pics:b.querySelectorAll('img').length, top:b.parentNode.scrollTop, "
                 "loader:getComputedStyle(document.getElementById('loading')).display};})()")
        say("address", "closed the page, then opened the file afresh with '#open=guide'", f"the Guide's panel is open, at its top, under the heading '{g['h1']}', with {g['pics']} pictures; the loader is gone; behind it the page is on "
            f"its defaults (layer {s['layer']}, floor {s['floor']} ha, all {s['drawn_lgd'] + s['drawn_out']:,} units drawn, no unit open); no error",
            s["modal"] == "block" and g["h1"] == GUIDE_FIRST and g["pics"] == GUIDE_PICTURES and g["top"] == 0 and g["loader"] == "none" and s["layer"] == D["default_layer"] and s["floor"] == "100" and s["unit"] is None
            and s["drawn_lgd"] + s["drawn_out"] == D["n"] and not c.errors)
        c.click_on("#b_close"); time.sleep(0.3)

        # ---- A9. a smaller window -------------------------------------------------------------------------------------------------------------------------
        for w, h in ((1100, 700), (820, 600)):
            c.resize(w, h)
            r = c.js("(function(){var m=document.getElementById('map').getBoundingClientRect(), s=document.getElementById('side').getBoundingClientRect(), i=document.getElementById('info').getBoundingClientRect(); return [Math.round(s.width), Math.round(m.width), Math.round(i.width), document.documentElement.scrollWidth];})()")
            lg = c.js("(function(){var b=document.getElementById('legend').getBoundingClientRect(), m=document.getElementById('map').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height), Math.round(m.height)];})()")
            say("window size", f"made the window {w} x {h}", f"side panel {r[0]} px, map {r[1]} px, unit panel {r[2]} px wide; the page is {r[3]} px wide, with no sideways scrolling; the legend is {lg[0]} x {lg[1]} px inside a map {lg[2]} px high and can be hidden",
                r[1] >= 350 and r[3] <= w + 2 and lg[1] <= lg[2] - 30 and lg[0] <= r[1] - 10)
            c.shot(SHOTS / f"A9_window_{w}x{h}.png")
        c.reset_size()
        log.append({"part": "A", "steps": list(steps)})

        # ---- B. a fresh sample of units, each clicked on the map ---------------------------------------------------------------------------------------------
        t = c.open(URL)
        rng = np.random.default_rng(20261007)
        forest = H["forest_ha"].astype(float)
        typ = np.where(U.index.str.startswith("OUTSIDE"), "outside_village", "lgd_panchayat")
        pool = pd.DataFrame({"forest": forest.reindex(U.index), "type": typ, "area": U["area_ha"].astype(float)}, index=U.index)
        pool = pool[~pool.index.isin(EARLIER) & (pool.area > 30)]                                  # a unit of a few hectares cannot be hit with a mouse at a zoom where its neighbours show
        wanted = []
        for lo, hi, what in ((-1, 0, "no forest"), (0, 1, "under 1 ha of forest"), (1, 100, "1 to 100 ha"), (100, 1000, "100 to 1,000 ha"), (1000, 1e9, "over 1,000 ha")):
            for kind in ("lgd_panchayat", "outside_village"):
                g = pool[(pool.forest > lo) & (pool.forest <= hi) & (pool.type == kind)] if lo >= 0 else pool[(pool.forest <= 0) & (pool.type == kind)]
                for uid in rng.choice(g.index.to_numpy(), size=min(2, len(g)), replace=False):
                    wanted.append((uid, f"{kind.replace('_', ' ')}, {what}"))
        for k in ("both", "hansen_only", "corestack_only", "neither", "zone_model_excluded"):
            g = A[(A.agreement_class == k) & A.index.isin(pool.index) & ~A.index.isin([w[0] for w in wanted])]
            wanted.append((rng.choice(g.index.to_numpy()), f"agreement class '{k}'"))
        for col, val, what in (("assigned_by", "two checks against the label", "district moved off the polygon's name"), ("assigned_by", "area majority: the polygon has no district name", "polygon with no name"), ("ambiguous", "1", "district ambiguous")):
            g = OD[(OD[col] == val) & ~OD.index.isin(EARLIER)]
            g = g.loc[[i for i in g.index if float(U.loc[i, "area_ha"]) > 3]]
            if len(g):
                wanted.append((g.index[np.argmax([float(U.loc[i, "area_ha"]) for i in g.index])], f"outside village, {what}"))
        g = N_[N_.adi_2011.isna() & ~N_.index.str.startswith("OUTSIDE") & N_.index.isin(pool.index)]
        wanted.append((rng.choice(g.index.to_numpy()), "lgd panchayat, no development index"))
        results = []
        for uid, why in wanted:
            ll, bb = point(uid)
            pad = max(bb[1][0] - bb[0][0], bb[1][1] - bb[0][1]) * 0.6
            c.js(f"(function(){{ ICTD_MAP.fitBounds([[{bb[0][0] - pad},{bb[0][1] - pad}],[{bb[1][0] + pad},{bb[1][1] + pad}]], {{animate:false, maxZoom:14}}); return 0; }})()"); time.sleep(0.7)
            x, y = to_screen(c, ll)
            c.click(x, y); time.sleep(0.5)
            r = compare(c, uid, why)
            r["clicked_at"] = [round(x), round(y)]
            r["outlined"] = state(c)["highlighted"]
            if r["outlined"] != 1:
                r["bad"].append(("outline", f"{r['outlined']} units outlined", "exactly one"))
            results.append(r)
            print(("PASS  " if r["of"] and r["equal"] == r["of"] else "FAIL  ") + f"[unit] {why}: {c.clicked} the map at ({round(x)}, {round(y)}), aiming at {uid}" + ("" if r["opened"] == uid else f"; the click landed on its neighbour {r['opened']}")
                  + f"; {r['equal']} of {r['of']} displayed values equal the stage tables" + ("" if not r["bad"] else "  MISMATCH " + str(r["bad"][:3])), flush=True)
        c.shot(SHOTS / "B_last_unit.png")
        # the panel itself: scroll it, and open a second unit over the first
        ix, iy = c.centre("#info")
        c.wheel(ix, iy, 500)
        top = c.js("document.getElementById('info').scrollTop")
        say("unit panel", f"{c.wheeled} over the unit panel" if BROWSER == "chrome" else "scrolled the unit panel by its own scroll position", f"it scrolled ({top:.0f} px); it has {results[-1]['sections']} headed sections and a bar of {results[-1]['bar_segments']} class segments", top > 0 and results[-1]["sections"] >= 7)
        log.append({"part": "B", "units": results})
        equal, total = sum(r["equal"] for r in results), sum(r["of"] for r in results)
        landed = sum(1 for r in results if r["opened"] != r["target"])
        summary = {"script": "scripts/exercise_layer.py", "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "inputs": INPUTS, "browser": c.version, "events_were": c.how, "opened": URL, "layer_run_utc": prov["run_utc"], "files_sha256": files,
                   "controls_exercised": len(steps), "controls_as_expected": sum(s["ok"] for s in steps), "units_clicked": len(results), "units_where_the_click_landed_on_a_neighbour": landed,
                   "values_compared": total, "values_equal": equal, "script_errors": c.errors, "by_type": pd.Series([r["type"] for r in results]).value_counts().to_dict(),
                   "forest_ha_min_max": [min(r["forest_ha"] for r in results), max(r["forest_ha"] for r in results)], "agreement_classes_seen": sorted({r["agreement_class"] for r in results})}
        print(f"\n{summary['controls_as_expected']} of {summary['controls_exercised']} control actions did what they should; {len(results)} units clicked on the map ({landed} clicks landed on a neighbour, which was then the unit compared); "
              f"{equal} of {total} displayed values equal the stage tables; script errors: {c.errors or 'none'}")
        json.dump({"summary": summary, "steps": steps, "units": results}, open(ROOT / "60_layer" / f"exercise_{BROWSER}.json", "w", encoding="utf-8"), indent=1, default=str)
        return 0 if summary["controls_as_expected"] == summary["controls_exercised"] and equal == total and not c.errors else 1
    finally:
        c.close()
        if profile:
            shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
