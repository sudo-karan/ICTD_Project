#!/usr/bin/env python3
"""The words of the map page, checked after they were rewritten on 11 October 2026. Changes nothing it reads.

    .venv/bin/python scripts/check_site_copy.py            the check
    .venv/bin/python scripts/check_site_copy.py --trials   plant errors on copies and see that the check catches each

On 11 October 2026 the owner had the page's words rewritten (a short label; what it left out in a small "i" beside it;
every untrue line fixed) with one rule above the others: changing words must not change a figure, a class, a count or a
colour. Before a word was changed the two builds were copied, with a list of their sha256, to
    .session_scratch_2026-10-05/60_layer_2026-10-11_before_words/      the full layer, 60_layer/
    .session_scratch_2026-10-05/70_share_2026-10-11_before_words/      the published copy, 70_share/
Both folders are outside git, so those copies are the only "before". This script holds the builds that are on disk
now against them, and against the owner's two files of that day (his handoff and his deck of words).

WHAT IT CHECKS
 a. THE NUMBERS. The saved copies still have the sha256 listed when they were made. `layer_by_unit.csv` is byte for
    byte the saved one. In both data.js files every part is the saved copy's but three kinds: parts that hold words
    (written out below, one by one), the two build times, and in the copy the overlay's part. The unit panel points at
    the same fields in the same order. Every field of every unit's row is the saved one but the small-forest warning,
    whose figures are the same and whose units are the same. Every figure and every {placeholder} of the old words
    stands in the new words of the same place or in the "i" of that place, or is listed here with why it went; the
    figures of the About text are in the saved order but for the listed changes.
 b. THE TRUTH. None of the phrases the owner's deck lists (its section 11) is in either build's words, in an "i" or
    in the README, outside what the deck exempts. No finding of the audit that is marked fixed is still there, and
    every finding marked as listed for the owner, with nothing changed, still is. In the copy the overlay's part is
    `available` 0 with `label` and `unavailable`, in his words, and nothing else.
 c. THE CAUTIONS. Each of the twenty-two cautions of the deck's section 8 is reachable where the deck says: on the
    page, in an "i" or in About this map, in both builds (the overlay's in the full layer only; the last in the
    copy's README).
 d. THE VOICE. Each label of the deck's section 1 has at most six words and no "?" or ";". No legend note opens
    "This shows". Every "i" has words, does not merely repeat its label, and its label does not hold its words. And in
    a browser (a separate, headless Chrome with an empty profile, driven by scripts/_browser_chrome.py), for each
    build: every "i" element's own text is empty; the one floating box is empty and hidden while no "i" is open and
    again after each one closes; the pointer on an "i" shows exactly that "i"'s words, wholly inside the window, and
    so does keyboard focus, also on an "i" that the browser has first to scroll into view;
    every "i" the data has words for is drawn somewhere and no other; a click on an "i" that stands inside a label
    does not work the label's control; the page raises no script error and asks the network for nothing. A run of
    this part that finds something wrong is made again, up to three runs in all, and every run is kept in the
    record with what it found (the rule of scripts/run_decision_checks.py for a browser check).
 e. THE CHECKS' OWN CHANGES (an addition to the owner's list, so that "no check is removed or loosened" can be read
    off a table). scripts/verify_layer.py is byte for byte the file of commit 16b1efd. For every other check and
    document writer that this task changed, every block of lines that differs from the commit before the task
    (`CHECKS_BEFORE`) has a row in 60_layer/site_copy_check_changes.csv, and every row of that table is a change that
    is really in the file.
 t. THE PLANTED ERRORS. The record of the trials (below) is of this script as it is and of the builds on disk, the
    builds as they are passed every check in it, and every planted error was caught by a check meant to catch it.

--trials plants each error on a COPY - a copy of a build's data held in memory, or a copy of its index.html written to
a temporary folder beside a link to its data.js - never on the real files, runs the checks on the copy, and counts the
error as caught only if a check that is MEANT to catch it fails. The eight errors the owner named are the first eight.

Reads   60_layer/: index.html, data.js, layer_by_unit.csv, layer.provenance.json, site_copy_audit.csv,
                   site_copy_check_changes.csv, and (the check only) site_copy_trials.json
        70_share/odisha_forest_decision_layer/: index.html, data.js, README.txt; 70_share/share.provenance.json
        the two saved copies named above, with their lists of sha256
        20_degradation/agreement_summary.csv (the interval one caution quotes),
        00_raw/05_forest_reference/provider_cautions.json (the provider's sentences the About text quotes)
        git: the check scripts as they were at `CHECKS_BEFORE`, and scripts/verify_layer.py at 16b1efd
Writes  the check:   60_layer/site_copy_check.json and 60_layer/site_copy_strings.csv, and nothing else. The second
                     holds every visible string and every "i" of both builds, before and after, with where each
                     one is; and one row for each figure that left or joined a place, with why.
        --trials:    60_layer/site_copy_trials.json, and nothing else.
        With --out FOLDER the same files go to that folder instead (a dry run).
Exit status 0 only if every check passed (the check), or every planted error was caught (--trials).
"""
from __future__ import annotations

import argparse
import copy
import csv
import difflib
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
NAME = "odisha_forest_decision_layer"
SCRATCH = ROOT / ".session_scratch_2026-10-05"
SAVED = {"layer": SCRATCH / "60_layer_2026-10-11_before_words", "copy": SCRATCH / "70_share_2026-10-11_before_words" / NAME}
SAVED_LISTS = {"layer": SCRATCH / "60_layer_2026-10-11_before_words" / "sha256.txt", "copy": SCRATCH / "70_share_2026-10-11_before_words" / "sha256.txt"}
NOW = {"layer": ROOT / "60_layer", "copy": ROOT / "70_share" / NAME}
CALLED = {"layer": "the full layer", "copy": "the published copy"}
AUDIT, CHANGES, TRIALS = "60_layer/site_copy_audit.csv", "60_layer/site_copy_check_changes.csv", "site_copy_trials.json"
CHECKS_BEFORE = "2e748c9"            # the last commit before this task changed a check
VERIFY_LAYER_AT = "16b1efd"          # the commit the stage-4 checks hold scripts/verify_layer.py to
CHECK_FILES = ["scripts/verify_decision.py", "scripts/exercise_layer.py", "scripts/exercise_decision.py", "scripts/exercise_share.py", "scripts/exercise_layer_safari.py", "scripts/exercise_decision_safari.py",
               "scripts/run_decision_checks.py", "scripts/check_pages_live.py", "scripts/write_decision_layer.py", "scripts/write_results.py"]
OUTSIDE_GIT = {".session_scratch_2026-10-05/make_layer_md.py": ".session_scratch_2026-10-05/site_copy/make_layer_md.before_site_words.py"}    # a writer git does not hold: the file as it was, saved beside the audit's working files
STANDING_IS = "the forest of 2000 with no loss recorded since; not a measure of tree cover today"       # the owner's wording of 9 October 2026
OVERLAY_SAYS = "Not in this copy, while we check the tile provider's terms of use."                      # his words for the copy's greyed box, 11 October 2026
INPUTS = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


def read(p):
    """A file this check reads: recorded with its size and sha256 in the output."""
    p = Path(p)
    r = rel(p)
    if not any(i["path"] == r for i in INPUTS):
        INPUTS.append({"path": r, "bytes": p.stat().st_size, "sha256": sha(p)})
    return p


def plain(s):
    """A piece of the page's HTML as the words a reader sees: an inline tag (bold, italic, code, a raised figure) goes without a trace, any other tag leaves a space."""
    s = re.sub(r"</?(?:b|i|code|sup|sub|em|strong|span|a)(?:\s[^>]*)?>", "", s)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def norm(s):
    """A text for comparing: one space between words, straight quotes, lower case."""
    return " ".join(str(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').split()).lower()


def load(folder):
    text = read(folder / "data.js").read_text(encoding="utf-8")
    return {"D": json.loads(text[text.index("{"):text.rindex("}") + 1]), "page": read(folder / "index.html").read_text(encoding="utf-8"),
            "readme": read(folder / "README.txt").read_text(encoding="utf-8") if (folder / "README.txt").is_file() else None, "folder": folder}


# ---- every string a reader can see, with where it is --------------------------------------------------------------------------------------------
FROM_55 = "a string from 55_decision/"
LABEL = "label: "                                               # the kinds that the deck's section 1 calls a label begin with this


def blocks(text):
    """The About text cut into its blocks (a heading, a paragraph, a list item, a row of a table), each as plain text."""
    parts = re.split(r"</?(?:p|li|h1|h2|h3|ul|ol|table|tr)(?:\s[^>]*)?>", text)
    return [t for t in (plain(p) for p in parts) if t]


def source_rows(text):
    return [[plain(c) for c in re.findall(r"<t[dh]>(.*?)</t[dh]>", r, re.S)] for r in re.findall(r"<tr>(.*?)</tr>", text, re.S)]


def tip_part(k):
    return "legend" if k.startswith("layer:") else "a unit's panel" if k.startswith("panel:") else "side panel" if k in ("floors", "units") else \
        "decision view: the list" if k in ("rank_none", "filter", "col_share") else "decision view: controls"


def strings(b):
    """Every visible string of one build: (part, key, where, kind, text, exempt). `key` groups the strings that are paired before and after;
    `exempt` says why a string is outside the deck's list of phrases, where it is."""
    D, V, new = b["D"], b["D"]["decision"], "tips" in b["D"]
    rows = []

    def add(part, where, kind, text, exempt="", key=None):
        if isinstance(text, str) and text.strip():
            rows.append({"part": part, "key": key or where, "where": where, "kind": kind, "text": text, "exempt": exempt})
    add("side panel", "title", "the page's title", D["title"])
    add("side panel", "subtitle", "text", D["subtitle"])
    add("side panel", "built", "text (the build's date)", D["built"])
    for k, v in D["unit_types"].items():
        add("side panel", f"unit_types.{k}", "text beside a box" if k != "out_legend" else "legend row", v)
    for f in D["floors"]:
        add("side panel", f"floors[{f['id']}].label", LABEL + "an option of the minimum-forest choice", f["label"])
    add("search", "search_none", "message", D["search_none"])
    add("search", "search_many", "message", D["search_many"])
    for l in D["layers"]:
        i = l["id"]
        add("side panel", f"layers[{i}].group", LABEL + "a group's name", l.get("group"))
        add("side panel", f"layers[{i}].title", LABEL + "a layer's name", l.get("title"))
        add("side panel", f"layers[{i}].pending", "text beside a greyed layer", l.get("pending"))
        add("legend", f"layers[{i}].legend_title", "legend title", l.get("legend_title"))
        add("legend", f"layers[{i}].this_shows", "legend note", l.get("this_shows"))
        for s_, v in (l.get("floor_note") or {}).items():
            add("legend", f"layers[{i}].floor_note[{s_}]", "legend note (the grey class)", v)
        for k, c in enumerate(l.get("classes") or []):
            add("legend", f"layers[{i}].classes[{k}].label", "legend class label", c["label"], "a legend class label")
    for k, c in enumerate(D.get("core_classes") or []):
        add("a unit's panel", f"core_classes[{k}].name", "legend class label", c["name"], "a legend class label")
    add("a unit's panel", "info_empty", "text (before a unit is chosen)", plain(D["info_empty"]))
    for k, sec in enumerate(D["panel"]):
        if not sec.get("top"):
            add("a unit's panel", f"panel[{k}].heading", LABEL + "a section heading in a unit's panel", sec.get("heading"))
        for j, r in enumerate(sec.get("rows", [])):
            add("a unit's panel", f"panel[{k}].rows[{j}]", "row label", r[0])
        add("a unit's panel", f"panel[{k}].note", "note", sec.get("note"))
    flag = next(sec["flag_field"] for sec in D["panel"] if "flag_field" in sec)
    seen = {}
    for row in D["f"]:
        for k, v in enumerate(row):
            if k in (0, 1):
                continue                                         # a unit's name and its id
            w = re.sub(r"[0-9][0-9,.]*", "N", v) if k != flag else v
            if k == 3:
                w = re.sub(r"^[^(]*", "DISTRICT ", w) if "(" in v else ""      # field 3 is the district's name, with how it was assigned for an outside-village unit
            if re.search(r"[A-Za-z]{3}", w):
                seen.setdefault((k, w), v)
    for (k, w), v in sorted(seen.items()):
        add("a unit's panel", f"f[][{k}]" + ("" if k == flag else f": {w}"), "the small-forest warning" if k == flag else "a value of a unit's panel (figures written N)", w,
            "" if k == flag else "a value of a unit's panel", key=f"f[][{k}]")
    for n_, t in enumerate(blocks(D["about_html"])):
        add("About this map", f"about_html, block {n_ + 1}", "text", t, key="about_html")
    for n_, cells in enumerate(source_rows(D["sources_html"])):
        overlay = bool(cells) and bool(re.match(r"(Loss-pixel|Site-level) overlay", cells[0]))
        for c_, cell in enumerate(cells):
            add("Sources", f"sources_html, row {n_ + 1}, cell {c_ + 1}", "text", cell, "" if overlay else "a cell of Sources other than the overlay row's", key="sources_html")
    for t in blocks(re.sub(r"<table>.*?</table>", " ", D["sources_html"], flags=re.S)):
        add("Sources", "sources_html, outside its table", "text", t, key="sources_html, outside its table")
    add("decision view: controls", "decision.title", "text held in the data (the page draws it nowhere since 11 October 2026)" if new else LABEL + "a heading on the side panel", V.get("title"))
    add("decision view: controls", "decision.radio", LABEL + "the decision view's switch", V["radio"])
    for w in V["windows"]:
        add("decision view: controls", f"decision.windows[{w['id']}].label", "text beside a button (a window's years)", w["label"])
        add("decision view: controls", f"decision.windows[{w['id']}].is", "i (the window's description)" if new else "text under a window's years", w["is"], FROM_55 + ": a window's description")
    for c in V["cells"]:
        for k, what in (("name", "a cell's name"), ("legend", "a cell's name"), ("def", "a cell's definition"), ("rests", "a cell's reason"), ("work", "a work-type field"), ("row", "a cell's row"), ("loss", "a cell's column")):
            add("decision view: legend and why this tier", f"decision.cells[{c['id']}].{k}", "text", c.get(k), FROM_55 + ": " + what)
    for k, v in V["tier_why"].items():
        add("decision view: legend and why this tier", f"decision.tier_why[{k}]", "text", v, FROM_55 + ": a tier's reason")
    add("decision view: legend and why this tier", "decision.governance", "text", V["governance"], FROM_55 + ": the governance prompt")
    add("decision view: legend and why this tier", "decision.work_note", "note", V["work_note"], FROM_55 + ": the note under a work-type field")
    for k, v in enumerate(V["corro_labels"]):
        add("decision view: legend and why this tier", f"decision.corro_labels[{k}]", "text (a corroboration badge)", v)
    for k, v in enumerate(V["check_labels"]):
        add("decision view: legend and why this tier", f"decision.check_labels[{k}]", "text (what a district rests on)", v)
    for k, g in enumerate(V["grid"]):
        add("decision view: legend and why this tier", f"decision.grid[{k}][0]", "text (a row of the grid of six)", g[0])
    add("decision view: legend and why this tier", "decision.standing_min", "text (a threshold)", V["standing_min"])
    add("decision view: legend and why this tier", "decision.loss_min", "text (a threshold)", V["loss_min"])
    for k, v in V["overlay"].items():
        if k != "available":
            add("overlay", f"decision.overlay.{k}", LABEL + "the overlay box's label" if k == "label" else "i (the overlay's note and version)" if new and k in ("note", "version") else "message", v)
    kinds = {"cols": LABEL + "a column head of the list", "window_head": LABEL + "a heading of the decision view's controls", "tiers_head": LABEL + "a heading of the decision view's controls", "reset": LABEL + "a button",
             "export": LABEL + "a button", "legend_title": "legend title", "legend_note": "legend note"}
    exempt = {"export_cols": "an export column name", "kind": "t.kind"}
    for k, v in V["t"].items():
        part = "decision view: controls" if k in ("window_head", "tiers_head", "reset") else "decision view: the list" if k.startswith(("rank_", "within", "keep_out", "district_pick")) or k in ("cols", "export", "st_options") \
            else "decision view: legend and why this tier"
        if isinstance(v, str):
            add(part, f"decision.t.{k}", kinds.get(k, "text"), v, exempt.get(k, ""))
        else:
            for j, x in enumerate(v):
                add(part, f"decision.t.{k}[{j}]", kinds.get(k, "text"), x if isinstance(x, str) else x[1], exempt.get(k, ""))
    for k, v in (D.get("tips") or {}).items():
        add(tip_part(k), f"tips.{k}", "i", v)
    # the page's own words
    page = b["page"]
    body, own = page[page.index("<body>"):page.index("<script>")], page[page.rindex("<script>"):]
    add("side panel", "index.html, <title>", "the tab's name until the data loads", plain(re.search(r"<title>(.*?)</title>", page, re.S).group(1)), key="index.html")
    marked = set()
    for tag, kind in (("h2", LABEL + "a heading on the side panel"), ("button", LABEL + "a button")):
        for m in re.finditer(rf"<{tag}\b[^>]*>(.*?)</{tag}>", body, re.S):
            marked.add(plain(m.group(1)))
            add("side panel", f"index.html, <{tag}>", kind, plain(m.group(1)), key="index.html")
    for m in re.finditer(r">([^<>]+)<", re.sub(r"</?(?:b|i|span)(?:\s[^>]*)?>", "", body)):
        t = " ".join(html.unescape(m.group(1)).split())
        if re.search(r"[A-Za-z]{2}", t) and t not in marked:
            add("side panel", "index.html, markup", "text", t, key="index.html")
    for m in re.finditer(r'(placeholder|title)="([^"]+)"', body):
        add("side panel", f"index.html, {m.group(1)}=", "the search box's hint" if m.group(1) == "placeholder" else "a button's hover text", html.unescape(m.group(2)), key="index.html")
    for m in sorted(set(re.findall(r"""(title|aria-label)="([^"'+]+)\"""", own))):           # the hover texts and names for a screen reader that the page's script writes as they stand
        add("page messages", f"index.html, {m[0]}= in its script", "a hover text" if m[0] == "title" else "an i's name for a screen reader", html.unescape(m[1]), key="index.html")
    for m in re.finditer(r"""(?<![\w\\])(?:'((?:[^'\\\n]|\\.)*)'|"((?:[^"\\\n]|\\.)*)")""", own):
        lit = m.group(1) if m.group(1) is not None else m.group(2)
        t = plain(lit.replace("\\'", "'").replace('\\"', '"'))
        if re.search(r"[A-Za-z]{3,}\s+[A-Za-z]{2,}|^(Hide|Show|Close|Move up|Move down)$|^[A-Z][a-z]+\u2026$", t) and not re.search(r"^[a-z_ .#=\[\]-]+$", t) and not re.search(r'[<>{};]|="|\bfunction\b', t):
            add("page messages", "index.html, a string of its script", LABEL + "a button" if t in ("Hide", "Show", "Close") else "a string of the page's script", t, key="index.html")
    if b["readme"] is not None:
        for head, text in readme_sections(b["readme"]):
            add("README.txt", f"README.txt: {head}", "text", text, key="README.txt")
    out, had = [], set()
    for r in rows:                                               # the same string in the same place once
        if (r["where"], r["text"]) not in had:
            had.add((r["where"], r["text"]))
            out.append(r)
    return out


def readme_sections(text):
    """The README cut at its headings (a line in capitals): (heading, the text under it)."""
    out, head, lines = [], "(the top)", []
    for line in text.splitlines():
        if line.strip() and not line.startswith(" ") and line.split("(")[0] == line.split("(")[0].upper() and re.search(r"[A-Z]{3}", line.split("(")[0]):
            if lines:
                out.append((head, " ".join(" ".join(lines).split())))
            head, lines = line.split("(")[0].strip(), []
            if not out:                                          # the first line is the title, in capitals too: it is its own section
                out.append(("(the title)", line.strip()))
                head = "(the top)"
        else:
            lines.append(line)
    if lines:
        out.append((head, " ".join(" ".join(lines).split())))
    return [(h, t) for h, t in out if t]


# The page's own words (index.html), old beside new: which string became which. The deck's section 3 gives each of these; a string named in neither column pairs with itself.
PAGE_PAIRS = [("Forest condition, MGNREGA allocation and social need - Odisha", "Odisha forest decision layer"), ("Decision view", "Show on the map"), ("Layer", "Show on the map"), ("Honest colour", "Minimum forest"),
              ("Units shown", "Show units"), ("Go to", "Find"), ("What this is, and how to read it", "About this map"), ("Sources and licences", "Sources"), ("Unit name or id, then Enter", "Name or unit id, then Enter"),
              ("District\u2026", "Jump to a district\u2026"),
              ("The map's data file was not found. Keep data.js in the same folder as this file and open it again.", "The map's data didn't load. If you downloaded the map, keep data.js in the same folder as index.html and open it again.")]


def paired(before, after):
    """The strings of one build before and after, side by side: by key where a key holds one string, in order where it holds several; the page's own words by the list written out above."""
    out = []
    keys = list(dict.fromkeys([r["key"] for r in before] + [r["key"] for r in after]))
    for k in keys:
        a, b = [r for r in before if r["key"] == k], [r for r in after if r["key"] == k]
        if k == "index.html":
            new_, used = {r["text"]: r for r in b}, set()
            for r in a:
                to = [n for o, n in PAGE_PAIRS if o == r["text"]] or [r["text"]]
                if all(n in new_ for n in to):
                    out += [(r, new_[n]) for n in to]
                    used.update(to)
                else:
                    out.append((r, None))
            out += [(None, r) for r in b if r["text"] not in used]
            continue
        if len(a) <= 1 and len(b) <= 1:
            out.append((a[0] if a else None, b[0] if b else None))
            continue
        sm = difflib.SequenceMatcher(None, [r["text"] for r in a], [r["text"] for r in b], autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                out += list(zip(a[i1:i2], b[j1:j2]))
            else:
                n = max(i2 - i1, j2 - j1)
                out += [(a[i1 + x] if i1 + x < i2 else None, b[j1 + x] if j1 + x < j2 else None) for x in range(n)]
    return out


GONE = {"A rate on a few hectares of forest is noise.": "the paragraph went with its heading: the 'i' beside 'Minimum forest' says it (tips.floors)",
        "Pending: not computed for the state.": "the unit panel's NIRv section is gone: NIRv is not a measure (ruling of 7 October 2026); About and the layer entry's 'i' say what was tested",
        "NIRv trend (Landsat 8, 2013-2025)": "the unit panel's NIRv section is gone: NIRv is not a measure (ruling of 7 October 2026)"}      # why a string that is gone went: by how it begins
CAME_FROM = {"tips.decision": "the switch's own label, which was a question", "tips.window_head": "new", "tips.tiers": "the heading over the order of tiers, which said 'provisional; yours to change'",
             "tips.rank_none": "the prompt of the empty list, which carried the whole sentence", "tips.filter": "the filter's note, which said 'for a smaller or undefined share'",
             "tips.col_share": "the head of the share's column, which said what the share is a share of", "tips.floors": "the paragraph under the heading 'Honest colour'", "tips.units": "new",
             "tips.layer:nirv": "the unit panel's NIRv section and the About text"}


def came_from(where):
    if where in CAME_FROM:
        return CAME_FROM[where]
    if where.startswith("tips.layer:"):
        return "the note under this layer's legend"
    if where.startswith("tips.panel:"):
        return "the note under this section of a unit's panel"
    return ""


# ---- a. the numbers ---------------------------------------------------------------------------------------------------------------------------------
NUM = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")
HOLE = re.compile(r"\{(\w+)\}")
WORDS = [r"\.title", r"\.subtitle", r"\.info_empty", r"\.about_html", r"\.sources_html", r"\.unit_types\.(lgd|out|out_legend)", r"\.floors\[\d+\]\.label", r"\.layers\[\d+\]\.(group|title|legend_title|this_shows|pending)",
         r"\.layers\[\d+\]\.floor_note\.(1|50|100)", r"\.decision\.radio", r"\.decision\.corro_labels\[\d+\]", r"\.decision\.overlay\.label", r"\.decision\.t\.cols\[\d+\]", r"\.decision\.t\.within_options\[\d+\]\[1\]",
         r"\.decision\.t\.(legend_title|legend_note|order_changed|window_head|tiers_head|why_head|why_standing_some|why_standing_little|why_loss_some|why_loss_none|why_share|why_share_none|why_order|why_was|why_unranked|why_low"
         r"|rank_none|within_tier|within_tier_share|rank_unranked|rank_filter_note|rank_out_kept|rank_out_dropped|keep_out|district_pick)"]        # the parts of data.js that hold words this task reworded: each written out
TIMES = [r"\.built", r"\.decision\.built"]
IN_THE_COPY = [r"\.decision\.overlay(\.\w+)?"]


def differ(a, b, path, out):
    """Every place where two readings of data.js differ: (path, how)."""
    if a == b:
        return
    if type(a) is not type(b):
        out.append((path, "another kind of value"))
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((f"{path}.{k}", "added"))
            elif k not in b:
                out.append((f"{path}.{k}", "taken out"))
            else:
                differ(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path, f"{len(a)} items, now {len(b)}"))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                differ(x, y, f"{path}[{i}]", out)
    else:
        out.append((path, "changed"))


def place(where, was_before):
    """The place a string belongs to, for comparing figures: a label and its "i" are one place."""
    m = re.match(r"(?:layers\[(\w+)\]\.(?:title|pending|legend_title|this_shows|floor_note\[\w+\])|tips\.layer:(\w+))$", where)
    if m:
        return "layer " + (m.group(1) or m.group(2))
    m = re.match(r"(?:panel\[(\d+)\]\.|tips\.panel:(\d+)$)", where)
    if m:
        k = m.group(1) or m.group(2)
        return "layer nirv" if was_before and k == "7" else "a unit's panel, section " + k      # the eighth section was NIRv's: a heading and a note, no figure of any unit
    for name, keys in (("the decision view's switch", ("decision.radio", "tips.decision", "decision.title")), ("the prompt of the empty list", ("decision.t.rank_none", "tips.rank_none")),
                       ("the filter's note", ("decision.t.rank_filter_note", "tips.filter")), ("the head of the share's column", ("decision.t.cols[6]", "tips.col_share")),
                       ("the heading over the order of tiers", ("decision.t.tiers_head", "tips.tiers")), ("the heading over the windows", ("decision.t.window_head", "tips.window_head")),
                       ("the minimum-forest choice", ("tips.floors",)), ("the kinds of unit", ("tips.units",))):
        if where in keys:
            return name
    if where.startswith("floors["):
        return "the minimum-forest choice"
    if where.startswith("unit_types."):
        return "the kinds of unit"
    if where.startswith("decision.overlay."):
        return "the overlay"
    if where.startswith(("about_html", "sources_html", "README.txt", "f[][")):
        return where.split(",")[0].split(":")[0]
    if where.startswith("index.html"):
        return "the page's own words (index.html)"
    return where


# Every figure that is not where it was, with why. (build, place) -> {figure or {placeholder}: why}. A figure not listed here that left or joined a place fails the check.
WENT = {
    ("both", "layer forest_area"): {"2000": "the deck's name for the layer, 'Forest in 2000 (Hansen)', names the year, as its legend title and its note do; the old name was 'Area under forests'"},
    ("both", "layer hansen_loss"): {"2001": "the deck's note says 'cleared outright since 2001'; the year also stands in the layer's name and in its legend title",
                                    "2025": "the deck's name is 'Tree cover loss since 2001 (Hansen)': the end year left the name and still stands in the legend title, 'Tree cover loss 2001-2025 ...'"},
    ("both", "layer corestack_net"): {"2017": "the deck's name is 'Degradation minus improvement (CoRE Stack)': the years left the name and still stand in the legend title",
                                      "2023": "as for 2017: the years left the layer's name and still stand in its legend title"},
    ("both", "layer agreement"): {"2017": "the deck's name is 'Hansen and CoRE Stack compared': the years left the name and still stand, twice, in the legend title",
                                  "2023": "as for 2017: the years left the layer's name and still stand in its legend title"},
    ("both", "layer nirv"): {"8": "'Landsat 8' stood in the layer's name and in the heading of the unit panel's NIRv section; the section is gone and the name is 'Greenness trend (NIRv)', so it stands once, in the entry's 'i' (and in About)",
                             "2013": "as for 8: the years of the test, 2013-2025, now stand once, in the entry's 'i' (and in About)", "2025": "as for 8: the years of the test, 2013-2025"},
    ("both", "a unit's panel, section 2"): {"2000": "the section's heading no longer names the year: 'Loss by canopy in 2000 (what the forest mask leaves out)' became 'Loss outside the forest mask'; its rows and its 'i' still say 2000"},
    ("both", "about_html"): {"2013": "the deck's item on NIRv gives the years of the test, 2013-2025", "2025": "the deck's item on NIRv gives the years of the test, 2013-2025",
                             "7": "the deck's item on NIRv gives the date of the decision, 7 October 2026 (docs/RESULTS.md section 6)", "2026": "the deck's item on NIRv gives the date of the decision, 7 October 2026"},
    ("copy", "about_html"): {"10": "the copy's About no longer has the full layer's paragraph on the overlay (tiles of loss on land with about 10 % canopy in 2000, version v1.13, loss through 2025): the owner's paragraph for the copy has no figure",
                             "2000": "as for 10: the overlay's paragraph is the owner's for the copy", "1.13": "as for 10: the overlay's paragraph is the owner's for the copy"},
    ("both", "the filter's note"): {"2011": "the deck's 'i' beside the note names the census by its year ('no resident population in the 2011 census'), where the note said 'undefined share'; a year, not a figure of the map"},
    ("both", "the head of the share's column"): {"{window}": "the deck's 'i' in the head names the window twice: the loss of the window, and the forest at the window's start; the page fills both in"},
    ("both", "the heading over the windows"): {"2025": "the deck's 'i' beside the heading says standing forest always runs to 2025, as the line in a unit's panel does ('Standing forest is always through 2025')"},
    ("both", "the minimum-forest choice"): {"100": "the deck's 'i' says 'We use 100 ha in the analysis', which the old label of the 100 ha option said in words ('the floor ruled for the analysis')",
                                            "50": "the deck's 'i' says '50 ha was our earlier proposal', which the old label of the 50 ha option said in words ('the earlier proposal')"},
    ("copy", "the overlay"): {t: "by the owner's ruling of 11 October 2026 the copy's overlay part holds only its label and his sentence: the note, the version and the messages of the full layer, with their figures, are not in the copy"
                              for t in ("1.13", "10", "2000", "2025", "4.0", "{window}")},
}
BUILD_SPECIFIC = ("built", "README.txt: THIS COPY")             # the build's own date, times, sizes and hashes: different in every build, and not figures of the map


def figures(text):
    return Counter(NUM.findall(text)) + Counter("{" + h + "}" for h in HOLE.findall(text))


def tokens_in_order(text):
    return NUM.findall(text)


# ---- b. the truth -------------------------------------------------------------------------------------------------------------------------------------
PHRASES = ["pending", "not yet computed", "will be a reported column", "pre-computed and offline", "offline map", "nothing is fetched from the internet", "asks the network for nothing", "project owner", "user of this page",
           "warranted", "honest colour", "what this is, and how to read it", "site-level overlay", "ruled for the analysis", "shown as a sensitivity", "gram panchayat units", "consultation catalogue", "the placebo failed"]
PHRASES_COPY_ONLY = ["is not beside this page"]                 # the full layer keeps it, for an overlay.js that is missing


def has_phrase(phrase, text):
    return re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", norm(text)) is not None


def unquoted(text, sentences):
    """A text without what it quotes: what stands between curly quotation marks, and the provider's registered sentences."""
    t = re.sub(r"“[^”]*”", " ", text)
    for s in sentences:
        t = t.replace(s, " ")
    return t


# ---- c. the cautions --------------------------------------------------------------------------------------------------------------------------------
def cautions(across):
    """The twenty-two cautions of the deck's section 8: (number, what it is, the words that must be reachable - every one of them; a tuple means any one of its members -, where)."""
    page, full, readme = ("layer", "copy"), ("layer",), "readme"
    return [
        (1, "not a verdict on any place; not a score", ["not a verdict", "no score"], page),
        (2, "ranked within a district, never across the state; across-state agreement not established, with its interval", ["never across the state", "not established", across], page),
        (3, "what standing forest is, in the owner's words", [STANDING_IS], page),
        (4, "Hansen can't see thinning, or change on land open in 2000; it's a floor", ["can't see thinning", "already open in 2000", "a floor"], page),
        (5, "CoRE Stack's classifiers are right about two times in three; read Degradation with Improvement", ["two times in three", ("read it next to improvement", "read degradation beside improvement")], page),
        (6, "CoRE Stack's own check fails in the East Coast zone", ["own check fails", "east coast zone"], page),
        (7, "units, not hectares: not overlaid pixel by pixel", ["units, not hectares", "pixel by pixel"], page),
        (8, "a flag is relative, not an amount of damage", ["a flag is relative, not an absolute amount of damage"], page),
        (9, "geotagged spending isn't what the panchayat received", [("not what the panchayat of record received", "not what a panchayat received")], page),
        (10, "the works record effectively ends with works started in 2017-18", ["effectively ends with works started in 2017-18"], page),
        (11, "the Plantation category includes orchards", ["includes orchards"], page),
        (12, "the three spending lines overlap: don't add them", ["overlap: don't add them"], page),
        (13, "small forests are greyed out (insufficient forest to assess)", ["insufficient forest to assess", "greyed out"], page),
        (14, "land outside villages has no census data; never zero", ["no census data for this land", "never zero"], page),
        (15, "Scheduled Tribe share filters the list; it never orders it", ["scheduled tribe share filters the list; it never orders it"], page),
        (16, "the tiers are provisional, to be set with the Foundation for Ecological Security", ["provisional tier order", "to be set with the foundation for ecological security"], page),
        (17, "which works fit which cell is a proposal", ["which rows bear on a cell is this project's proposal"], page),
        (18, "loss on land with 10 % canopy or less decides nothing", ["loss on land with 10 % canopy or less is shown for information; it decides nothing"], page),
        (19, "close call", ["close call"], page),
        (20, "NIRv was tested, not used, and why", ["tested, not used", "a single image could flip"], page),
        (21, "the overlay: for finding places, not for measuring; what it sends; missing pink is not a sign of no loss", ["do not measure from it", "network address", "years of the window", "not a sign of no loss"], full),
        (22, "in the copy's README: the development index is not in this copy", ["the development index is not in this copy"], readme),
    ]


# ---- d. the voice, in a browser ----------------------------------------------------------------------------------------------------------------------
LIST_TIPS = """(function(){var b=document.getElementById('tipbox'), d=document.documentElement;
  return {box:{there:!!b, text:b?b.textContent:null, shown:b?getComputedStyle(b).display!=='none':null, in_info:!!(b&&b.closest('#info'))}, w:d.clientWidth, h:d.clientHeight,
    tips:Array.from(document.querySelectorAll('.tip')).map(function(e,i){var r=e.getBoundingClientRect();
      return {i:i, own:e.textContent, kids:e.childElementCount, words:e.getAttribute('data-tip'), visible:!!(e.offsetParent!==null&&r.width>0&&r.height>0), beside:(e.parentElement.textContent||'').trim().slice(0,70)};})};})()"""
BOX = "(function(){var b=document.getElementById('tipbox'), r=b.getBoundingClientRect(), d=document.documentElement; return {text:b.textContent, shown:getComputedStyle(b).display!=='none'&&r.width>0&&r.height>0, inside:r.left>=0&&r.top>=0&&r.right<=d.clientWidth&&r.bottom<=d.clientHeight};})()"


def in_a_browser(folder, D, port=9341):
    """Open one build from disk and read every "i" in five states of the page. Returns what was seen, and what is wrong (a list, empty when nothing is)."""
    from _browser_chrome import Chrome
    V, tips = D["decision"], D.get("tips") or {}
    expected = {v for k, v in tips.items() if k != "col_share"} | {w["is"] for w in V["windows"]}
    default = next(w["label"] for w in V["windows"] if w["id"] == V["default_window"])
    if "col_share" in tips:
        expected.add(tips["col_share"].replace("{window}", default))
    if V["overlay"].get("available"):
        expected.add(V["overlay"]["note"] + " " + V["overlay"]["version"])
    profile = tempfile.mkdtemp(prefix="ictd_chrome_profile_")
    c = Chrome(profile, port=port)
    url = "file://" + str(Path(folder) / "index.html")
    seen, wrong, states, hovered, focused, focused_after_a_scroll, slowest = Counter(), [], [], 0, 0, 0, 0.0
    net = lambda: [u for u in c.requests if u.startswith("http")]

    def until(want, limit=2.0):
        """Read the floating box until it is as wanted, for at most two seconds: a bubble that opens or closes within that time is one a reader sees open or close."""
        nonlocal slowest
        t0 = time.time()
        while True:
            box = c.js(BOX)
            if want(box) or time.time() - t0 > limit:
                slowest = max(slowest, time.time() - t0)
                return box
            time.sleep(0.05)

    def state(name):
        nonlocal hovered, focused, focused_after_a_scroll
        time.sleep(0.5)
        s = c.js(LIST_TIPS)
        if not s["box"]["there"] or s["box"]["text"] != "" or s["box"]["shown"] or s["box"]["in_info"]:
            wrong.append(f"{name}: with no 'i' open the floating box holds {s['box']['text']!r}, shown {s['box']['shown']}, inside the unit panel {s['box']['in_info']}")
        opened = 0
        for t in s["tips"]:
            if t["visible"]:
                seen[t["words"]] += 1
            if t["own"] != "" or t["kids"]:
                wrong.append(f"{name}: the 'i' beside '{t['beside']}' holds text of its own: {t['own']!r}")
            if not t["words"]:
                wrong.append(f"{name}: an 'i' beside '{t['beside']}' has no words")
            if not t["visible"]:
                continue
            xy = c.js(f"(function(){{var e=document.querySelectorAll('.tip')[{t['i']}]; e.scrollIntoView({{block:'nearest'}}); var r=e.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}})()")
            c.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=xy[0], y=xy[1], button="none")
            box = until(lambda b_: b_["text"] == t["words"] and b_["shown"])
            if box["text"] != t["words"] or not box["shown"] or not box["inside"]:
                wrong.append(f"{name}: with the pointer on the 'i' beside '{t['beside']}' the box shows {box['text'][:60]!r} (shown {box['shown']}, inside the window {box['inside']}), not its words")
            c.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=2, y=2, button="none")
            box = until(lambda b_: b_["text"] == "" and not b_["shown"])
            if box["text"] != "" or box["shown"]:
                wrong.append(f"{name}: after the pointer left the 'i' beside '{t['beside']}' the box still holds {box['text'][:60]!r}")
            opened += 1
        hovered += opened
        # keyboard focus. Each "i" on show is given focus, as a Tab would give it, after its panel has been scrolled so that the "i" is out of sight wherever the panel can scroll:
        # the browser then scrolls it back into view, and its bubble must open and stay open (found on 11 October 2026: that scroll used to close it).
        by_focus = after_scroll = 0
        for t in s["tips"]:
            if not t["visible"]:
                continue
            out_of_sight = c.js(f"""(function(){{var e=document.querySelectorAll('.tip')[{t['i']}], p=e.parentElement;
              while (p && !(p.scrollHeight > p.clientHeight + 1 && /(auto|scroll)/.test(getComputedStyle(p).overflowY))) p = p.parentElement;
              if (p) {{ var r=e.getBoundingClientRect(), q=p.getBoundingClientRect(); p.scrollTop = (r.top - q.top + p.scrollTop > p.clientHeight) ? 0 : p.scrollHeight; }}
              var r2=e.getBoundingClientRect(); return document.elementFromPoint(r2.left+r2.width/2, r2.top+r2.height/2) !== e;}})()""")
            time.sleep(0.15)                                     # the scroll just made has passed before focus is given
            c.js(f"(function(){{document.querySelectorAll('.tip')[{t['i']}].focus(); return 0;}})()")
            box = until(lambda b_: b_["text"] == t["words"] and b_["shown"])
            if box["text"] == t["words"] and box["shown"]:
                time.sleep(0.3)                                  # and it is still open a moment later, when the scroll that focus made has passed
                box = c.js(BOX)
            if box["text"] != t["words"] or not box["shown"] or not box["inside"]:
                wrong.append(f"{name}: with keyboard focus on the 'i' beside '{t['beside']}'" + (", which had first to scroll into view," if out_of_sight else "") + f" the box shows {box['text'][:60]!r} (shown {box['shown']}, inside the window {box['inside']}), not its words")
            c.js("(function(){ if (document.activeElement) { document.activeElement.blur(); } return 0; })()")
            box = until(lambda b_: b_["text"] == "" and not b_["shown"])
            if box["text"] != "" or box["shown"]:
                wrong.append(f"{name}: after the 'i' beside '{t['beside']}' lost keyboard focus the box still holds {box['text'][:60]!r}")
            by_focus += 1
            after_scroll += bool(out_of_sight)
        focused += by_focus
        focused_after_a_scroll += after_scroll
        states.append({"state": name, "i_elements": len(s["tips"]), "on_show_and_opened_by_the_pointer": opened, "opened_by_keyboard_focus": by_focus, "of_them_after_scrolling_into_view": after_scroll, "window": [s["w"], s["h"]]})

    try:
        c.cmd("Emulation.setFocusEmulationEnabled", enabled=True)      # a window off the screen has no focus of its own: without this no element in it is told that it took focus
        c.open(url)
        state("the page as it opens")
        # a click on an "i" inside a label must not work the label's control
        x, y = c.click_on("#dv label .tip")
        if c.js("document.getElementById('r_decision').checked"):
            wrong.append("a click on the 'i' inside the decision view's switch turned the view on")
        c.click(2, 2)
        for l in D["layers"]:
            if l.get("pending"):
                continue
            c.js(f"(function(){{document.querySelector('input[name=layer][value={l['id']}]').click(); return 0;}})()")
            state(f"the layer '{l['title']}'")
        c.js(f"(function(){{location.hash = 'layer=agreement&unit=' + encodeURIComponent({json.dumps(D['id'][0])}); return 0;}})()")
        for _ in range(40):
            time.sleep(0.25)
            if c.js("!!document.querySelector('#info table.kv')"):
                break
        state("a unit's panel")
        c.js("(function(){location.hash = 'layer=decision'; return 0;})()")
        time.sleep(1.2)
        state("the decision view, no district chosen")
        w0 = c.js("(document.querySelector('input[name=dwindow]:checked')||{}).value")
        other = next(w["id"] for w in V["windows"] if w["id"] != w0)
        c.click_on(f"input[name=dwindow][value='{other}'] ~ .tip")
        if c.js("(document.querySelector('input[name=dwindow]:checked')||{}).value") != w0:
            wrong.append("a click on the 'i' inside a window's label chose that window")
        c.click(2, 2)
        if V["overlay"].get("available"):
            c.click_on("#c_overlay ~ .tip")
            time.sleep(0.8)
            if c.js("document.getElementById('c_overlay').checked") or c.js("typeof window.ICTD_OVERLAY") != "undefined" or net():
                wrong.append("a click on the 'i' inside the overlay's label ticked the box, or asked for overlay.js, or went to the network")
            c.click(2, 2)
        elif c.js("!!document.querySelector('#c_overlay ~ .tip')"):
            wrong.append("the overlay's box is not available and has an 'i' beside it")
        c.js(f"(function(){{location.hash = 'layer=decision&rank=' + encodeURIComponent({json.dumps(D['districts'][0]['name'])}) + '&st=33'; return 0;}})()")
        for _ in range(40):
            time.sleep(0.25)
            if c.js("!!document.querySelector('table.rk')"):
                break
        state("the decision view, a district ranked and a filter on")
        errors = list(c.errors or [])
        if errors:
            wrong.append(f"script errors or lines in the browser's log: {errors[:3]}")
        if net():
            wrong.append(f"requests to the network: {net()[:3]}")
        version = c.version
    finally:
        c.close()
        shutil.rmtree(profile, ignore_errors=True)
    drawn = {w for w in seen if w}
    if expected - drawn:
        wrong.append("words of an 'i' that the data holds and no state of the page draws: " + "; ".join(sorted(x[:50] for x in expected - drawn)))
    if drawn - expected:
        wrong.append("an 'i' drawn with words the data does not hold for it: " + "; ".join(sorted(x[:50] for x in drawn - expected)))
    if not focused_after_a_scroll:
        wrong.append("no 'i' was out of sight when it was given keyboard focus: the scroll that focus makes was not exercised")
    return {"browser": version, "opened": "file://" + rel(Path(folder) / "index.html") if Path(folder).resolve().is_relative_to(ROOT) else "a copy in a temporary folder", "states": states,
            "i_with_distinct_words_drawn": len(drawn), "i_with_distinct_words_expected": len(expected), "bubbles_opened_by_the_pointer": hovered,
            "bubbles_opened_by_keyboard_focus": focused, "of_them_on_an_i_that_had_first_to_scroll_into_view": focused_after_a_scroll, "the_slowest_bubble_to_open_or_close_s": round(slowest, 2), "wrong": wrong}


def in_a_browser_with_runs(folder, D):
    """The browser check of one build, run again - up to three runs in all - if a run finds something wrong; every run is kept. This is the rule of scripts/run_decision_checks.py for a browser
    check: how many runs it needed is part of the result, and what an earlier run found wrong is written down."""
    runs = []
    for _ in range(3):
        runs.append(in_a_browser(folder, D))
        if not runs[-1]["wrong"]:
            break
        time.sleep(3)
    last = dict(runs[-1])
    last.update({"runs_made": len(runs), "runs_that_found_nothing_wrong": sum(1 for r in runs if not r["wrong"]), "what_each_earlier_run_found_wrong": [r["wrong"] for r in runs[:-1]]})
    return last


# ---- e. the checks' own changes ---------------------------------------------------------------------------------------------------------------------
def git_show(commit, path):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def changed_blocks(old, new):
    """The blocks of lines that differ between two texts: (old lines as one text, new lines as one text)."""
    a, b = old.splitlines(), new.splitlines()
    return [("\n".join(a[i1:i2]), "\n".join(b[j1:j2])) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if op != "equal"]


def squeeze(s):
    return " ".join(s.split())


# ---- the checks -----------------------------------------------------------------------------------------------------------------------------------------
def run_checks(before, now, extra, browser):
    """Every check, on the builds given. before, now: {"layer": build, "copy": build}; extra: the audit's rows, the table of the checks' changes, the csv's sha256 pair, the
    saved lists; browser: {"layer": result, "copy": result} of in_a_browser(), or None for a build that was not opened. Returns (results, the strings table)."""
    results = []

    def check(cid, what, ok, detail=""):
        results.append({"id": cid, "check": what, "pass": bool(ok), "detail": detail})
    S = {(w, k): strings(b) for w, src in (("before", before), ("after", now)) for k, b in src.items()}
    pairs = {k: paired(S[("before", k)], S[("after", k)]) for k in ("layer", "copy")}

    # a. the numbers
    check("a0", "the saved copies of the two builds, made before a word was changed, still have the sha256 that the lists made with them give", not extra["saved_wrong"],
          "; ".join(extra["saved_wrong"]) or f"{extra['saved_files']} files held against {len(SAVED_LISTS)} lists")
    check("a1", "60_layer/layer_by_unit.csv is byte for byte the saved copy's", extra["csv_now"] == extra["csv_saved"], f"sha256 {extra['csv_now'][:16]}... against {extra['csv_saved'][:16]}...")
    for k in ("layer", "copy"):
        A, B = before[k]["D"], now[k]["D"]
        d = []
        differ({x: v for x, v in A.items() if x not in ("f", "panel")}, {x: v for x, v in B.items() if x not in ("f", "panel")}, "", d)
        allowed = WORDS + TIMES + (IN_THE_COPY if k == "copy" else [])
        other = [(p, how) for p, how in d if not (p == ".tips" and how == "added") and not any(re.fullmatch(a, p) for a in allowed)]
        check(f"a2 ({k})", f"in the data.js of {CALLED[k]} every part is the saved copy's but the parts that hold words this task reworded (each written out in this check), the two build times, the new key `tips`"
              + (", and the overlay's part" if k == "copy" else "") + ": no class, count, colour, shape or figure array differs, and no key but `tips` was added or taken out",
              not other and set(B) == set(A) | {"tips"}, f"{len(d)} parts differ, all of them allowed" if not other else "NOT ALLOWED: " + "; ".join(f"{p} ({how})" for p, how in other[:6]))
        pa, pb = A["panel"], B["panel"]
        shape = lambda sec: ([r[1] for r in sec.get("rows", [])], sec.get("heading_field"), sec.get("flag_field"), bool(sec.get("top")), sec.get("bar"))
        check(f"a2 panel ({k})", f"the unit panel of {CALLED[k]} points at the same fields in the same order as the saved copy's: its first seven sections have the same rows of fields, the same heading field, warning field and bar; "
              "the eighth, NIRv's, which had a heading and a note and no row, is gone", len(pa) == 8 and len(pb) == 7 and [shape(s) for s in pa[:7]] == [shape(s) for s in pb] and not pa[7].get("rows"),
              f"{sum(len(s.get('rows', [])) for s in pb)} rows in {len(pb)} sections")
        flag = next(sec["flag_field"] for sec in pb if "flag_field" in sec)
        fa, fb = A["f"], B["f"]
        bad, moved = 0, Counter()
        if len(fa) == len(fb):
            for ra, rb in zip(fa, fb):
                if ra != rb:
                    if len(ra) != len(rb) or any(x != y for j, (x, y) in enumerate(zip(ra, rb)) if j != flag):
                        bad += 1
                    else:
                        moved[(ra[flag], rb[flag])] += 1
        same_figures = all(NUM.findall(x) == NUM.findall(y) and x.split(":")[0] == y.split(":")[0] for x, y in moved)
        check(f"a3 ({k})", f"every field of every unit's row in {CALLED[k]} is the saved copy's, but the small-forest warning; that warning changed from one sentence to one sentence, begins as it did, carries the same figures, and stands on "
              "the same units", len(fa) == len(fb) and bad == 0 and len(moved) == 1 and same_figures,
              f"{len(fb):,} units; rows that differ outside the warning: {bad}; the warning reworded on {sum(moved.values()):,} units, {len(moved)} sentence(s)" if len(fa) == len(fb) else f"{len(fa):,} units, now {len(fb):,}")
        # figures and placeholders, place by place
        old, new_ = Counter(), Counter()
        by_old, by_new = {}, {}
        for r in S[("before", k)]:
            if r["where"] not in BUILD_SPECIFIC and not r["exempt"].startswith(("a value of a unit's panel", "a legend class label")):
                by_old.setdefault(place(r["where"], True), Counter()).update(figures(r["text"]))
        for r in S[("after", k)]:
            if r["where"] not in BUILD_SPECIFIC and not r["exempt"].startswith(("a value of a unit's panel", "a legend class label")):
                by_new.setdefault(place(r["where"], False), Counter()).update(figures(r["text"]))
        unexplained, listed = [], []
        for pl in sorted(set(by_old) | set(by_new)):
            a_, b_ = by_old.get(pl, Counter()), by_new.get(pl, Counter())
            for tok in sorted(set(a_) | set(b_)):
                if a_[tok] != b_[tok]:
                    why = (WENT.get((k, pl)) or {}).get(tok) or (WENT.get(("both", pl)) or {}).get(tok)
                    (listed if why else unexplained).append({"build": CALLED[k], "place": pl, "figure": tok, "times_before": a_[tok], "times_after": b_[tok], "why": why or ""})
        extra.setdefault("figures_listed", []).extend(listed)
        check(f"a4 ({k})", f"in {CALLED[k]}, every figure and every {{placeholder}} of the old words stands as often in the new words of the same place, the place's 'i' counted with it, or is listed in this check with why it "
              "went or came (a place: a layer's name, legend and notes; a section of the unit panel; a control; the About text; Sources; the README but for its section on this copy's own files)",
              not unexplained, f"{sum(sum(c.values()) for c in by_new.values()):,} figures and placeholders in {len(by_new)} places; {len(listed)} differences listed with why" if not unexplained else
              "NOT LISTED: " + "; ".join(f"{u['place']}: {u['figure']} stood {u['times_before']} time(s), now {u['times_after']}" for u in unexplained[:8]) + (f" ... {len(unexplained)} in all" if len(unexplained) > 8 else ""))
        ta, tb = tokens_in_order(plain(A["about_html"])), tokens_in_order(plain(B["about_html"]))
        ops = [(ta[i1:i2], tb[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes() if op != "equal"]
        strange = [o for o in ops if (tuple(o[0]), tuple(o[1])) not in ABOUT_FIGURES[k]]
        extra.setdefault("figures_listed", []).extend({"build": CALLED[k], "place": "about_html, in order", "figure": " ".join(o[0]) or "(none)", "times_before": 1, "times_after": 0, "why": "now: " + (" ".join(o[1]) or "(none)") + ". "
                                                        + ABOUT_FIGURES[k][(tuple(o[0]), tuple(o[1]))]} for o in ops if (tuple(o[0]), tuple(o[1])) in ABOUT_FIGURES[k])
        check(f"a5 ({k})", f"the figures of the About text of {CALLED[k]} are the saved copy's, in the saved order, but for the changes written out in this check", not strange,
              f"{len(tb)} figures in order; {len(ops)} listed changes" if not strange else "NOT LISTED: " + "; ".join(f"{o[0]} -> {o[1]}" for o in strange[:5]))

    # b. the truth
    quoted = extra["provider_sentences"]
    for k in ("layer", "copy"):
        hits = []
        for r in S[("after", k)]:
            if r["exempt"]:
                continue
            text = unquoted(r["text"], quoted)
            for p in PHRASES + (PHRASES_COPY_ONLY if k == "copy" else []):
                if has_phrase(p, text):
                    hits.append(f"'{p}' in {r['where']}")
        check(f"b1 ({k})", f"none of the phrases the deck lists (its section 11) is in the words of {CALLED[k]}, in an 'i'" + (" or in its README" if k == "copy" else "") + ", outside what the deck exempts (quotations; strings from "
              "55_decision/; the values of a unit's panel; legend class labels; export column names and the two kinds of unit; the cells of Sources other than the overlay row's)", not hits,
              f"{len(PHRASES) + (len(PHRASES_COPY_ONLY) if k == 'copy' else 0)} phrases looked for in {sum(1 for r in S[('after', k)] if not r['exempt']):,} strings" if not hits else "FOUND: " + "; ".join(hits[:8]))
    whole = {k: norm(" \n ".join(r["text"] for r in S[("after", k)])) for k in ("layer", "copy")}
    whole_saved = {k: norm(" \n ".join(r["text"] for r in S[("before", k)])) for k in ("layer", "copy")}
    back, lost, never, n_fixed, n_listed = [], [], [], 0, 0
    for a in extra["audit"]:
        builds = [k for k in ("layer", "copy") if a["where"].startswith(("both builds",) + (("full layer",) if k == "layer" else ("published copy",)))]
        if not builds or not a["said"].strip():
            continue
        for k in builds:
            there = norm(a["said"]) in whole[k]
            if a["done"].startswith("fixed"):
                n_fixed += 1
                if there:
                    back.append(f"{CALLED[k]}: '{a['said'][:70]}'")
                if "as built in Step 2" not in a["where"] and norm(a["said"]) not in whole_saved[k]:
                    never.append(f"{CALLED[k]}: '{a['said'][:70]}'")
            elif a["done"].startswith("listed"):
                n_listed += 1
                if not there:
                    lost.append(f"{CALLED[k]}: '{a['said'][:70]}'")
    check("b2", "of the audit's findings about the page (60_layer/site_copy_audit.csv): the words of each one marked fixed stood in the saved copy of the build it was found in and are no longer in that build (a finding in the deck's "
          "own words, which were only ever in the build of Step 2, is held to the second half alone); and the words of each one marked as listed for the owner, with nothing changed, are still there", not back and not lost and not never
          and n_fixed > 0, f"{n_fixed} fixed findings looked for and not found; {n_listed} listed findings looked for and found" if not back and not lost and not never
          else "STILL THERE: " + "; ".join(back[:5]) + " | NO LONGER THERE: " + "; ".join(lost[:5]) + " | NEVER IN THE SAVED BUILD: " + "; ".join(never[:5]))
    ov = now["copy"]["D"]["decision"]["overlay"]
    check("b3", "in the copy's data the overlay's part is `available` 0 with `label` and `unavailable` and nothing else; the label is the full layer's and `unavailable` is the owner's sentence",
          ov == {"available": 0, "label": now["layer"]["D"]["decision"]["overlay"]["label"], "unavailable": OVERLAY_SAYS}, json.dumps(ov, ensure_ascii=False)[:200])

    # c. the cautions
    for n_, what, need, where in cautions(extra["across"]):
        missing = []
        for k in (("copy",) if where == "readme" else where):
            body = norm(now[k]["readme"] or "") if where == "readme" else whole[k]
            for w in need:
                if not any(norm(x) in body for x in (w if isinstance(w, tuple) else (w,))):
                    missing.append(f"{CALLED[k]}: '{w if isinstance(w, str) else ' / '.join(w)}'")
        check(f"c{n_:02d}", f"caution {n_} of the deck's section 8 - {what} - is reachable in " + ("the copy's README" if where == "readme" else "the full layer only" if where == ("layer",) else "both builds")
              + ": on the page, in an 'i' or in About this map", not missing, "MISSING: " + "; ".join(missing) if missing else "; ".join(w if isinstance(w, str) else w[0] for w in need)[:150])

    # d. the voice
    long_ = []
    for k in ("layer", "copy"):
        default = next(w["label"] for w in now[k]["D"]["decision"]["windows"] if w["id"] == now[k]["D"]["decision"]["default_window"])
        labels = [r for r in S[("after", k)] if r["kind"].startswith(LABEL)]
        for r in labels:
            t = r["text"].replace("{window}", default)
            if len(t.split()) > 6 or "?" in t or ";" in t:
                long_.append(f"{CALLED[k]}, {r['where']}: '{t}' ({len(t.split())} words)")
        extra.setdefault("labels", {})[k] = len(labels)
    check("d1", "each label of the deck's section 1 - a button, a heading on the side panel, the decision view's switch, a layer's or a group's name, an option of the minimum-forest choice, a heading of the decision view's controls, "
          "the overlay box's label, a column head of the list, a section heading in a unit's panel - has at most six words and no '?' or ';', in both builds", not long_,
          f"{extra['labels']['layer']} labels in the full layer, {extra['labels']['copy']} in the copy" if not long_ else "; ".join(long_[:6]))
    shows = [f"{CALLED[k]}, {r['where']}" for k in ("layer", "copy") for r in S[("after", k)] if r["kind"].startswith("legend note") and norm(r["text"]).startswith("this shows")]
    check("d2", "no legend note opens 'This shows', in either build", not shows, "; ".join(shows[:5]) or f"{sum(1 for r in S[('after', 'layer')] if r['kind'].startswith('legend note'))} legend notes in the full layer")
    poor = []
    for k in ("layer", "copy"):
        D, V = now[k]["D"], now[k]["D"]["decision"]
        tips = D.get("tips") or {}
        h2 = {m.group(1): plain(m.group(0)) for m in re.finditer(r'<h2>[^<]*<span class="tipslot" data-key="(\w+)"></span></h2>', now[k]["page"])}
        label_of = {"decision": [V["radio"]], "window_head": [V["t"]["window_head"]], "tiers": [V["t"]["tiers_head"]], "rank_none": [V["t"]["rank_none"]], "filter": [V["t"]["rank_filter_note"]], "col_share": [V["t"]["cols"][6]],
                    "floors": [h2.get("floors", "")], "units": [h2.get("units", "")]}
        for l in D["layers"]:
            label_of["layer:" + l["id"]] = [l.get("title", ""), l.get("legend_title") or l.get("title", "")]
        for j, sec in enumerate(D["panel"]):
            label_of[f"panel:{j}"] = [sec.get("heading", "")]
        both = [(f"tips.{t}", v, label_of.get(t)) for t, v in tips.items()] + [(f"decision.windows[{w['id']}].is", w["is"], [w["label"]]) for w in V["windows"]]
        if V["overlay"].get("available"):
            both.append(("the overlay's note and version", V["overlay"]["note"] + " " + V["overlay"]["version"], [V["overlay"]["label"]]))
        for where, words, labels in both:
            ws = set(re.findall(r"[a-z0-9]+", norm(words)))
            if not words.strip():
                poor.append(f"{CALLED[k]}, {where}: no words")
            elif not labels or not all(labels):
                poor.append(f"{CALLED[k]}, {where}: no label is known for this 'i'")
            elif any(norm(words) == norm(lb) or ws <= set(re.findall(r"[a-z0-9]+", norm(lb))) for lb in labels):
                poor.append(f"{CALLED[k]}, {where}: says nothing its label does not")
            elif any(norm(words) in norm(lb) for lb in labels):
                poor.append(f"{CALLED[k]}, {where}: its words stand in its label's own text")
        extra.setdefault("tips_counted", {})[k] = len(both)
    check("d3", "every 'i' has words, says something its label does not, and its label does not hold its words, in both builds (an 'i' and its label: the key of `tips` and the label the page draws it beside; a window's years and "
          "its description; the overlay's label and its note)", not poor, f"{extra['tips_counted']['layer']} in the full layer, {extra['tips_counted']['copy']} in the copy" if not poor else "; ".join(poor[:6]))
    for k in ("layer", "copy"):
        r = (browser or {}).get(k)
        if r is None:
            check(f"d4 ({k})", f"in a browser, {CALLED[k]}: not opened in this run", False, "the build was not opened")
            continue
        check(f"d4 ({k})", f"in a browser, {CALLED[k]} opened from disk, in the page as it opens, under each layer, with a unit's panel open, in the decision view, and with a district ranked and a filter on: every 'i' element's own text "
              "is empty; the one floating box is empty and hidden while no 'i' is open and again after each one closes; the pointer on an 'i' shows exactly that 'i''s words, wholly inside the window, and so does keyboard focus, also on an 'i' "
              "that the browser has first to scroll into view; every 'i' the data has words for is drawn in one of those states and no other is; a click on an 'i' that stands inside a label does not work the label's control; no script "
              "error, and nothing asked of the network", not r["wrong"],
              (f"{r['browser']}; {len(r['states'])} states; {r['i_with_distinct_words_drawn']} of {r['i_with_distinct_words_expected']} 'i' drawn; {r['bubbles_opened_by_the_pointer']} bubbles opened by the pointer and {r['bubbles_opened_by_keyboard_focus']} by keyboard focus "
               f"({r['of_them_on_an_i_that_had_first_to_scroll_into_view']} of them on an 'i' that had first to scroll into view); the slowest "
               f"took {r['the_slowest_bubble_to_open_or_close_s']} s to open or close" if not r["wrong"] else "WRONG: " + " | ".join(r["wrong"][:4]))
              + (f"; runs made: {r['runs_made']}, of which {r['runs_that_found_nothing_wrong']} found nothing wrong" + (f" (an earlier run found: {' | '.join(x for w in r['what_each_earlier_run_found_wrong'] for x in w[:2])})"
                                                                                                                      if r.get("what_each_earlier_run_found_wrong") else "") if "runs_made" in r else ""))

    # e. the checks' own changes
    vl = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", VERIFY_LAYER_AT, "--", "scripts/verify_layer.py"], capture_output=True).returncode
    check("e1", f"scripts/verify_layer.py is byte for byte the file of commit {VERIFY_LAYER_AT}, to which the stage-4 checks hold it", vl == 0, "unchanged" if vl == 0 else "IT DIFFERS, or git could not say")
    uncovered, unreal, n_blocks, per_file = [], [], 0, {}
    table = extra["changes"]
    used = set()
    for path in CHECK_FILES + list(OUTSIDE_GIT):
        old = (ROOT / OUTSIDE_GIT[path]).read_text(encoding="utf-8") if path in OUTSIDE_GIT else git_show(CHECKS_BEFORE, path)
        if old is None:
            uncovered.append(f"{path}: git has no such file at {CHECKS_BEFORE}")
            continue
        bl = changed_blocks(old, (ROOT / path).read_text(encoding="utf-8"))
        rows_ = [(n_, r) for n_, r in enumerate(table) if r["file"] == path]
        per_file[path] = len(bl)
        n_blocks += len(bl)
        for o, w in bl:
            hit = [n_ for n_, r in rows_ if squeeze(r["was"]) in squeeze(o) and squeeze(r["now"]) in squeeze(w) and (r["was"].strip() or r["now"].strip())]
            used.update(hit)
            if not hit:
                uncovered.append(f"{path}: '{squeeze(o)[:60]}' -> '{squeeze(w)[:60]}'")
    unreal = [f"{r['file']}: '{squeeze(r['was'])[:50]}' -> '{squeeze(r['now'])[:50]}'" for n_, r in enumerate(table) if n_ not in used]
    check("e2", f"every block of lines that differs from commit {CHECKS_BEFORE} in a check or a document writer this task changed has a row in {CHANGES} (the row's old words are in the block as it was, its new words in "
          "the block as it is), and every row of that table is such a change", not uncovered and not unreal and n_blocks > 0,
          f"{n_blocks} blocks in {sum(1 for v in per_file.values() if v)} files, {len(table)} rows; files with no change: {', '.join(p.split('/')[-1] for p, v in per_file.items() if not v) or 'none'}" if not uncovered and not unreal
          else "NO ROW FOR: " + " | ".join(uncovered[:4]) + " || NOT A CHANGE IN THE FILE: " + " | ".join(unreal[:4]))
    return results, pairs, S


NIRV_ITEM = "the deck's item on NIRv, in place of 'is pending and will be a reported column only': the years of the test (2013-2025) and the date of the decision (7 October 2026)"
ABOUT_FIGURES = {"layer": {((), ("2013", "2025", "7", "2026")): NIRV_ITEM},
                 "copy": {((), ("2013", "2025", "7", "2026")): NIRV_ITEM,
                          (("10", "2000", "1.13", "2025"), ()): "the full layer's paragraph on the overlay is replaced, in the copy, by the owner's paragraph, which has no figure"}}      # (figures taken out, figures put in) of the About text, in order -> why


def strings_table(pairs, figures_listed):
    """The rows of 60_layer/site_copy_strings.csv."""
    out = []
    for k in ("layer", "copy"):
        for a, b in pairs[k]:
            r = b or a
            status = "unchanged" if a and b and a["text"] == b["text"] else "reworded" if a and b else "new" if b else "gone"
            if b and b["kind"].startswith("i") and not a:
                status = "new: an i"
            note = came_from(r["where"]) if (b and not a) else next((why for start, why in GONE.items() if a["text"].startswith(start)), "") if (a and not b) else ""
            if b and b["exempt"]:
                note = (note + "; " if note else "") + "outside the deck's list of phrases: " + b["exempt"]
            out.append({"build": CALLED[k], "part": r["part"], "where": r["where"], "kind": r["kind"], "before": a["text"] if a else "", "after": b["text"] if b else "", "status": status, "note": note})
    for f in figures_listed:
        out.append({"build": f["build"], "part": "figures", "where": f["place"], "kind": "a figure that is not where it was", "before": f"{f['figure']}: {f['times_before']} time(s)", "after": f"{f['figure']}: {f['times_after']} time(s)",
                    "status": "listed", "note": f["why"]})
    return out


def gather():
    """Everything the checks need beside the builds: the saved lists, the csv's two hashes, the audit, the table of changes, the interval, the provider's sentences."""
    extra = {"saved_wrong": [], "saved_files": 0}
    for k, lst in SAVED_LISTS.items():
        base = read(lst).parent
        want = {line.split(None, 1)[1].strip().lstrip("./"): line.split()[0] for line in lst.read_text().splitlines() if line.strip()}
        for name in (("data.js", "index.html", "layer_by_unit.csv") if k == "layer" else (f"{NAME}/data.js", f"{NAME}/index.html", f"{NAME}/README.txt")):
            extra["saved_files"] += 1
            if name not in want or sha(base / name) != want[name]:
                extra["saved_wrong"].append(f"{rel(base / name)} is not the file that was saved")
    extra["csv_now"], extra["csv_saved"] = sha(read(NOW["layer"] / "layer_by_unit.csv")), sha(read(SAVED["layer"] / "layer_by_unit.csv"))
    with open(read(ROOT / AUDIT), newline="", encoding="utf-8") as fh:
        extra["audit"] = list(csv.DictReader(fh))
    with open(read(ROOT / CHANGES), newline="", encoding="utf-8") as fh:
        extra["changes"] = list(csv.DictReader(fh))
    with open(read(ROOT / "20_degradation/agreement_summary.csv"), newline="", encoding="utf-8") as fh:
        s = [r for r in csv.DictReader(fh) if r["window"] == "common_2017_2023" and float(r["minimum_reference_ha"]) == 100 and r["delivered"] == "1" and r["units"] == "lgd_panchayat"]
    if len(s) != 1:
        sys.exit("20_degradation/agreement_summary.csv has no single headline row for LGD panchayat units")
    extra["across"] = f"{float(s[0]['odds_ratio_lo95']):.2f} to {float(s[0]['odds_ratio_hi95']):.2f}"
    caut = json.loads(read(ROOT / "00_raw/05_forest_reference/provider_cautions.json").read_text(encoding="utf-8"))
    extra["provider_sentences"] = [v["text"] for v in caut["sentences"].values()]
    return extra


# ---- the planted errors -------------------------------------------------------------------------------------------------------------------------------
def with_data(b, **parts):
    """A copy of a build whose data has the given top-level parts replaced; nothing of the build given is changed."""
    n = dict(b)
    n["D"] = dict(b["D"])
    n["D"].update(parts)
    return n


def planted(before, now):
    """The errors to plant: (what, the build it is planted on, a function giving (the builds with the error in, a folder to open in a browser or None), the checks meant to catch it)."""
    L, C = now["layer"]["D"], now["copy"]["D"]

    def layer(**parts):
        return {"layer": with_data(now["layer"], **parts), "copy": now["copy"]}, None

    def copy_(**parts):
        return {"layer": now["layer"], "copy": with_data(now["copy"], **parts)}, None

    def t_of(D, **texts):
        V = dict(D["decision"])
        V["t"] = dict(V["t"])
        V["t"].update(texts)
        return V

    def page_of(k, old, new):
        if now[k]["page"].count(old) != 1:
            raise SystemExit(f"a planted error could not be planted: the page of {k} has '{old[:50]}' {now[k]['page'].count(old)} times")
        folder = Path(tempfile.mkdtemp(prefix="ictd_site_copy_trial_"))
        (folder / "index.html").write_text(now[k]["page"].replace(old, new), encoding="utf-8")
        os.symlink(NOW[k] / "data.js", folder / "data.js")
        b = dict(now[k])
        b["page"] = now[k]["page"].replace(old, new)
        return {**now, k: b}, folder

    def nirv():
        layers = copy.deepcopy(L["layers"])
        next(l for l in layers if l["id"] == "nirv")["pending"] = "pending, not yet computed"
        return layer(layers=layers)

    def about(old, new, k="layer"):
        D = now[k]["D"]
        if D["about_html"].count(old) < 1:
            raise SystemExit(f"a planted error could not be planted: the About text has no '{old}'")
        return (layer if k == "layer" else copy_)(about_html=D["about_html"].replace(old, new, 1))

    def swap(a, b):
        t = L["about_html"]
        i, j = t.index(a), t.index(b)
        if not i < j:
            raise SystemExit("a planted error could not be planted: the two figures are not in that order")
        return layer(about_html=t[:i] + b + t[i + len(a):j] + a + t[j + len(b):])

    def field(change):
        flag = next(sec["flag_field"] for sec in L["panel"] if "flag_field" in sec)
        f = list(L["f"])
        return layer(f=change(f, flag))

    def one_field(f, flag):
        i = next(i for i, r in enumerate(f) if re.fullmatch(r"[\d,]+\.\d\d ha", r[5]))
        f[i] = list(f[i])
        f[i][5] = f[i][5][:-4] + ("1" if f[i][5][-4] != "1" else "2") + " ha"
        return f

    def warning(f, flag):
        return [r[:flag] + [r[flag].replace("Under 100 ha", "Under 50 ha")] + r[flag + 1:] if r[flag].startswith("Under 100 ha") else r for r in f]

    def code():
        layers = copy.deepcopy(L["layers"])
        l = next(l for l in layers if l["id"] == "hansen_loss")
        s = l["cls"]["100"]
        l["cls"]["100"] = ("1" if s[0] != "1" else "2") + s[1:]
        return layer(layers=layers)

    def note_of_copy():
        layers = copy.deepcopy(C["layers"])
        l = next(l for l in layers if l["id"] == "hansen_loss")
        l["this_shows"] = "This shows " + l["this_shows"][0].lower() + l["this_shows"][1:]
        return copy_(layers=layers)

    tips = lambda **t: layer(tips={**L["tips"], **t})
    readme = dict(now["copy"])
    readme["readme"] = now["copy"]["readme"].replace("panchayat units, and the land outside", "gram panchayat units, and the land outside")
    return [
        ("1. 'pending' back on the NIRv entry", "the full layer's data", nirv, ["b1 (layer)"]),
        ("2. 'offline' back in the copy's subtitle", "the copy's data", lambda: copy_(subtitle=before["copy"]["D"]["subtitle"]), ["b1 (copy)"]),
        ("3. one figure of About changed by a digit (the count of units, which stands elsewhere too)", "the full layer's data", lambda: about("11,468", "11,469"), ["a5 (layer)", "a4 (layer)"]),
        ("4. one caution taken out (that Scheduled Tribe share never orders the list)", "the full layer's data",
         lambda: layer(decision=t_of(L, rank_filter_note=L["decision"]["t"]["rank_filter_note"].replace(" Scheduled Tribe share filters the list; it never orders it.", ""))), ["c15"]),
        ("5. an 'i''s words put into its label's text (the decision view's switch)", "the full layer's data", lambda: layer(decision={**L["decision"], "radio": L["decision"]["radio"] + ". " + L["tips"]["decision"]}), ["d1", "d3"]),
        ("6. a label of nine words (the heading over the order of tiers)", "the full layer's data", lambda: layer(decision=t_of(L, tiers_head="Provisional tier order that you can change at will")), ["d1"]),
        ("7. the overlay box enabled in the copy (the full layer's overlay put back)", "the copy's data", lambda: copy_(decision={**C["decision"], "overlay": L["decision"]["overlay"]}), ["b3"]),
        ("8. 'gram panchayat units' back in the README", "the copy's README", lambda: ({"layer": now["layer"], "copy": readme}, None), ["b1 (copy)"]),
        ("9. two figures of About exchanged (27 % and 59 %): every figure still there, in another order", "the full layer's data", lambda: swap("27 %", "59 %"), ["a5 (layer)"]),
        ("10. the 'i' element given text of its own", "a copy of the full layer's index.html", lambda: page_of("layer", """data-tip="' + attr(words) + '"></span>'""", """data-tip="' + attr(words) + '">i</span>'"""), ["d4 (layer)"]),
        ("11. the floating box not emptied when it closes", "a copy of the copy's index.html", lambda: page_of("copy", 'b.style.display = "none"; b.textContent = ""; tipFor = null;', 'b.style.display = "none"; tipFor = null;'), ["d4 (copy)"]),
        ("12. the 'i' beside a legend's title not drawn", "a copy of the full layer's index.html", lambda: page_of("layer", """esc(l.legend_title) + tip(TIPS["layer:" + l.id])""", "esc(l.legend_title)"), ["d4 (layer)"]),
        ("13. one hectare figure of one unit changed by a digit", "the full layer's data", lambda: field(one_field), ["a3 (layer)"]),
        ("14. the small-forest warning's figure changed (100 ha to 50 ha)", "the full layer's data", lambda: field(warning), ["a3 (layer)"]),
        ("15. the class of one unit on one layer changed", "the full layer's data", code, ["a2 (layer)"]),
        ("16. a legend note that opens 'This shows'", "the copy's data", note_of_copy, ["d2"]),
        ("17. an 'i' that only repeats its label", "the full layer's data", lambda: tips(window_head="Count loss over."), ["d3"]),
        ("18. a phrase of the deck's list in an 'i' ('the project owner')", "the full layer's data", lambda: tips(tiers="To be set by the project owner with the Foundation for Ecological Security. Use the arrows to change it."), ["b1 (layer)"]),
        ("19. a finding of the audit back in About ('Every number shown is a cell of')", "the copy's data", lambda: about("Every number in a unit's panel is a cell of", "Every number shown is a cell of", "copy"), ["b2"]),
        ("20. a {placeholder} dropped from a sentence of 'why this tier'", "the full layer's data", lambda: layer(decision=t_of(L, why_share=L["decision"]["t"]["why_share"].replace("{start} ha", "the"))), ["a4 (layer)"]),
        ("21. layer_by_unit.csv with one byte changed", "a copy of the table", None, ["a1"]),
        ("22. a bubble closed by any scroll, so that keyboard focus on an 'i' out of sight shows nothing (the page as it was until 11 October 2026, 16:50 IST)", "a copy of the full layer's index.html",
         lambda: page_of("layer", 'document.addEventListener("scroll", tipFollow, true);', 'document.addEventListener("scroll", function () { if (tipFor) { tipHide(); } }, true);'), ["d4 (layer)"]),
    ]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", action="store_true", help="plant errors on copies and record whether the check catches each")
    ap.add_argument("--out", default=str(ROOT / "60_layer"), help="the folder the output goes to (default: 60_layer/)")
    a = ap.parse_args()
    out = Path(a.out)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    before, now = {k: load(SAVED[k]) for k in SAVED}, {k: load(NOW[k]) for k in NOW}
    extra = gather()
    builds = {"layer_run_utc": json.loads(read(ROOT / "60_layer/layer.provenance.json").read_text())["run_utc"], "copy_run_utc": json.loads(read(ROOT / "70_share/share.provenance.json").read_text())["run_utc"],
              "files_sha256": {rel(NOW[k] / f): sha(NOW[k] / f) for k in NOW for f in ("index.html", "data.js")} | {rel(NOW["copy"] / "README.txt"): sha(NOW["copy"] / "README.txt")}}
    me = {"script": "scripts/check_site_copy.py", "script_sha256": sha(__file__)}
    browser = {k: in_a_browser_with_runs(NOW[k], now[k]["D"]) for k in NOW}
    results, pairs, S = run_checks(before, now, extra, browser)
    ok = all(r["pass"] for r in results)

    if a.trials:
        failed0 = [r["id"] for r in results if not r["pass"]]
        trials = []
        for what, on, make, meant in planted(before, now):
            ex = dict(extra)
            ex.pop("figures_listed", None)
            if make is None:                                     # the table: a copy with one byte changed, hashed
                tmp = Path(tempfile.mkdtemp(prefix="ictd_site_copy_trial_")) / "layer_by_unit.csv"
                data = bytearray((NOW["layer"] / "layer_by_unit.csv").read_bytes())
                data[len(data) // 2] = data[len(data) // 2] ^ 1
                tmp.write_bytes(bytes(data))
                ex["csv_now"] = sha(tmp)
                shutil.rmtree(tmp.parent, ignore_errors=True)
                res, _, _ = run_checks(before, now, ex, browser)
            else:
                builds_, folder = make()
                br = dict(browser)
                if folder is not None:
                    k = "layer" if "full layer" in on else "copy"
                    br[k] = in_a_browser(folder, now[k]["D"], port=9342)
                    shutil.rmtree(folder, ignore_errors=True)
                res, _, _ = run_checks(before, builds_, ex, br)
            failed = [r["id"] for r in res if not r["pass"] and r["id"] not in failed0]
            caught = any(m in failed for m in meant)
            trials.append({"planted": what, "on": on, "checks_meant_to_catch_it": meant, "checks_that_failed": failed, "what_the_first_of_them_said": next((r["detail"][:300] for r in res if r["id"] in failed and r["id"] in meant), ""), "caught": caught})
            print(("CAUGHT      " if caught else "NOT CAUGHT  ") + f"{what}  [{', '.join(failed) or 'no check failed'}]", flush=True)
        record = {**me, "run_utc": started, "ended_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "builds": builds, "inputs": INPUTS,
                  "how": "each error was planted on a copy - a copy of a build's data held in memory, a copy of its index.html in a temporary folder beside a link to its data.js, or a copy of the table - and never on the real files; "
                         "an error counts as caught only if a check meant to catch it failed, and a check that already fails on the builds as they are is not counted",
                  "the_builds_as_they_are": {"checks": len(results), "passed": sum(r["pass"] for r in results), "failed": failed0, "what_each_failed_check_said": {r["id"]: r["detail"] for r in results if not r["pass"]},
                                             "in_a_browser": {k: {x: v for x, v in browser[k].items() if x != "states"} for k in browser}},
                  "trials": trials, "planted": len(trials), "caught": sum(t["caught"] for t in trials), "every_planted_error_caught": all(t["caught"] for t in trials) and ok}
        out.mkdir(parents=True, exist_ok=True)
        json.dump(record, open(out / TRIALS, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"\n{record['caught']} of {record['planted']} planted errors caught; the builds as they are: {record['the_builds_as_they_are']['passed']} of {len(results)} checks passed; record: {rel(out / TRIALS) if out.resolve().is_relative_to(ROOT) else out / TRIALS}")
        return 0 if record["every_planted_error_caught"] else 1

    # t. the planted errors: the record of the trials must be of this script and of these builds
    tr = out / TRIALS if (out / TRIALS).is_file() else ROOT / "60_layer" / TRIALS
    if tr.is_file():
        T = json.loads(read(tr).read_text(encoding="utf-8")) if tr.resolve().is_relative_to(ROOT) else json.loads(tr.read_text(encoding="utf-8"))
        t_ok = T.get("script_sha256") == me["script_sha256"] and T.get("builds") == builds and T.get("planted", 0) >= 8 and T.get("every_planted_error_caught") is True and T["the_builds_as_they_are"]["failed"] == []
        detail = f"{T.get('caught')} of {T.get('planted')} caught, run {T.get('run_utc')}" + ("" if t_ok else "; NOT of this script as it is, or not of these builds, or an error was not caught")
    else:
        t_ok, detail = False, "there is no record of the trials: run this script with --trials first"
    results.append({"id": "t1", "check": f"the planted errors: the record of the trials (60_layer/{TRIALS}) is of this script as it is and of the builds on disk, the builds as they are passed every check in it, at least eight errors were "
                                         "planted - the eight the owner named among them - and every one was caught by a check meant to catch it", "pass": t_ok, "detail": detail})
    table = strings_table(pairs, extra.get("figures_listed", []))
    out.mkdir(parents=True, exist_ok=True)
    cols = ["build", "part", "where", "kind", "before", "after", "status", "note"]
    with open(out / "site_copy_strings.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(table)
    n_by = Counter((r["build"], r["status"]) for r in table)
    for r in results:
        print(("PASS  " if r["pass"] else "FAIL  ") + f"{r['id']:<16}{r['check'][:150]}" + (f"   [{r['detail'][:260]}]" if r["detail"] else ""), flush=True)
    ok = all(r["pass"] for r in results)
    json.dump({**me, "run_utc": started, "ended_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "builds": builds, "inputs": INPUTS,
               "the_saved_copies": {k: rel(SAVED[k]) for k in SAVED}, "checks_were_changed_since_commit": CHECKS_BEFORE,
               "checks": results, "checks_passed": sum(r["pass"] for r in results), "checks_made": len(results), "passed": ok,
               "in_a_browser": browser,
               "strings_table": {"path": "60_layer/site_copy_strings.csv", "rows": len(table), "columns": cols, "rows_with_no_text_before": sum(1 for r in table if not r["before"]), "rows_with_no_text_after": sum(1 for r in table if not r["after"]),
                                 "by_build_and_status": {f"{b}: {s}": n for (b, s), n in sorted(n_by.items())}}},
              open(out / "site_copy_check.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{sum(r['pass'] for r in results)} of {len(results)} checks passed; strings table: n = {len(table):,} rows ({sum(1 for r in table if not r['before']):,} with no text before, {sum(1 for r in table if not r['after']):,} with none after)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
