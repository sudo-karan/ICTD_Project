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

THE SIX LINES. Later that day, in his third handoff, the owner gave his words for six lines of the page that the audit
had listed for him, and said: every other string stays as it is. Before they were changed both builds were copied again,
with a list of sha256, to
    .session_scratch_2026-10-05/60_layer_2026-10-11_before_six_fixes/
    .session_scratch_2026-10-05/70_share_2026-10-11_before_six_fixes/
and group f below holds the builds on disk against those: the strings that differ are his six lines, each differing by
exactly his replacement, and nothing else of either build differs but the build's own times and hashes. With them:
cautions 4 and 6 are in his new words; eight phrases joined the list of group b ("CoRE Stack's own check", "already
open in 2000", "fairly closed", "No forest loss in the window", "is none: under", "no village plan", "own dashboard",
"state totals reconciled"); and three kinds of string are no longer outside that list, because the page now words them
itself: the governance prompt, a cell's definition, and the Hansen row of Sources.

THE GUIDE AND THE LOADER. On 13 October 2026 the owner had a third button put on the page, Guide, which opens
docs/GUIDE.md in the window the About and Sources texts use, and a loader that says what the page is doing while it
opens. The guide is carried in data.js as one more key, `guide_html` (scripts/_guide.py turns the Markdown into HTML
when the layer is built; its five pictures go inside it), and index.html changed in ten places. Three checks that held
"nothing else was added" had therefore to be widened, each by exactly what was added and no more: a2 allows the one new
key; f1 allows four new strings on the page itself, written out (the button's label and hover text, the loader's two
messages), and fails unless all four are there; f2 holds index.html to the kept page with the ten places put back,
each written out and each found exactly once. Group g holds what was added. No check was taken out, and no expected
number or count was changed.

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
 f. THE SIX LINES (the owner's third handoff of 11 October 2026). The copies kept before them still have the sha256
    listed with them. Against those copies, in each build: no string was added or dropped; every string that differs
    is one of his six lines and differs by exactly his replacement; no place of a fix still holds its old words; every
    fix is found in the build. And no part of data.js differs but the parts those strings are in and the build time;
    index.html is byte for byte the kept one.
 g. THE GUIDE AND THE LOADER (the owner's handoff of 13 October 2026).
    g0  In both builds `guide_html` is docs/GUIDE.md as the converter turns it into HTML now, character for character,
        with its five pictures; the copy's is the full layer's; the layer's run record gives the sha256 of the guide
        and of each picture as they are on disk.
    g1  The same HTML held to the Markdown WITHOUT the converter: the words read the same; no tag or attribute but
        the few the converter writes; the links are the guide's own, each opened in a new tab; the five pictures are
        the bytes of their files under docs/guide/.
    g2  The button and the loader, read in index.html as text: where they stand, what they say, in what order the
        page changes the message and draws the map; the loader's words carry no figure and pass the voice rules.
    g3  The guide's words: none of the phrases of group b, no finding of the audit marked fixed, no block that opens
        "This shows", and the development index named nowhere.
    g4  THE GATE ON THE GUIDE'S FIGURES. The guide is cut into sentences and table cells. For each one that holds a
        figure, all its figures must stand together, each written the same way, in ONE passage of ONE of the files
        the owner named - the page's own strings in data.js, docs/GAP.md, docs/DECISION_LAYER.md, README.md,
        60_layer/decision_runs.json, 70_share/exercise_share_chrome.json,
        00_raw/05_forest_reference/provider_cautions.json and 60_layer/site_copy_looked_at.json - and that passage
        must share a word with the sentence. A passage is a paragraph, an item of a list or a row of a table; in a
        record, the plain values of one object; on the page, the strings of one place. Allowed, and nothing else:
        thousands separators, a space before %, the minus sign, and x for the multiplication sign. A figure that
        stands in no named file as the guide writes it may stand only as one of the cases listed in `GUIDE_DERIVED`,
        each worked out again from the file's own figure (bytes to megabytes, lakh to crore, 13.8 pixels to "about
        14", "per cent" in words, a shortened month, a shortened page number). Three short lists beside it are also
        written out: sentences whose figures stand in two passages, sentences whose passage is named because many
        passages hold their one small figure, and the two parts of the guide traced to one file only. One of those
        is a tenth file, used for one sentence: the registered page of the University of Maryland, for the citation
        of the paper behind Hansen's data. 60_layer/site_copy_check.json, the ninth of the owner's files, is the
        record this script itself writes: only the count of its own checks is held to it, by g7, and to the run
        that writes it. Picture file names, and the addresses links point to, are not figures.
        WHAT g4 DOES NOT SHOW: that a passage says what the sentence says. A sentence with several figures, or with
        a large one, is held tightly; a lone small figure can stand beside a shared word in a passage about
        something else. Every trace is written to 60_layer/site_copy_guide_figures.csv to be read, and was read by
        eye once, on 13 October 2026.
    g5  The guide's own counts: in its table "How it was checked", each result that is a count of this build's own
        runs is the result on record for that run, and is "N of N".
    g6  Those records are of the builds on disk, and of runs that passed. So this check is run AFTER the runner,
        the copy's check and the pictures: scripts/run_decision_checks.py, scripts/exercise_share.py, then the
        screenshots, then this.
    g7  The guide's count for this check itself is the number of checks this run makes.
 t. THE PLANTED ERRORS. The record of the trials (below) is of this script as it is and of the builds on disk, the
    builds as they are passed every check in it, and every planted error was caught by a check meant to catch it.

--trials plants each error on a COPY - a copy of a build's data held in memory, or a copy of its index.html written to
a temporary folder beside a link to its data.js - never on the real files, runs the checks on the copy, and counts the
error as caught only if a check that is MEANT to catch it fails. The eight errors the owner named are the first eight;
the four he named with the six lines, each of which puts an old line back, are numbers 23 to 26; the two he named with
the guide, a changed figure and a figure found nowhere, are 28 and 29, each planted on a copy of the guide's text held
in memory. Numbers 30 to 35 try the other checks of group g and the widened f2.

Reads   60_layer/: index.html, data.js, layer_by_unit.csv, layer.provenance.json, site_copy_audit.csv,
                   site_copy_check_changes.csv, and (the check only) site_copy_trials.json
        70_share/odisha_forest_decision_layer/: index.html, data.js, README.txt; 70_share/share.provenance.json
        the two saved copies named above, and the two kept before the six lines, with their lists of sha256
        20_degradation/agreement_summary.csv (the interval one caution quotes),
        00_raw/05_forest_reference/provider_cautions.json (the provider's sentences the About text quotes)
        docs/GUIDE.md, docs/guide/*.webp, scripts/_guide.py (the guide, its pictures and its converter)
        the files the guide's figures are traced to: docs/GAP.md, docs/DECISION_LAYER.md, README.md,
        60_layer/decision_runs.json, 70_share/exercise_share_chrome.json, 60_layer/site_copy_looked_at.json, and
        00_raw/05_forest_reference/umd_global_forest_change_2025_v1_13_page_2026-10-08.html
        git: the check scripts as they were at `CHECKS_BEFORE`, this script at `BEFORE_THE_GUIDE`, and
        scripts/verify_layer.py at 16b1efd
Writes  the check:   60_layer/site_copy_check.json, 60_layer/site_copy_strings.csv and
                     60_layer/site_copy_guide_figures.csv, and nothing else. The second holds every visible string
                     and every "i" of both builds, before and after, with where each one is, the guide's words
                     block by block, and one row for each figure that left or joined a place, with why. The third
                     holds every sentence and cell of the guide that has a figure, with the passage it stands in.
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
BEFORE_SIX = {"layer": SCRATCH / "60_layer_2026-10-11_before_six_fixes", "copy": SCRATCH / "70_share_2026-10-11_before_six_fixes" / NAME}      # both builds as they stood before the owner's six lines
BEFORE_SIX_LISTS = {"layer": SCRATCH / "60_layer_2026-10-11_before_six_fixes" / "sha256.txt", "copy": SCRATCH / "70_share_2026-10-11_before_six_fixes" / "sha256.txt"}
NOW = {"layer": ROOT / "60_layer", "copy": ROOT / "70_share" / NAME}
CALLED = {"layer": "the full layer", "copy": "the published copy"}
AUDIT, CHANGES, TRIALS = "60_layer/site_copy_audit.csv", "60_layer/site_copy_check_changes.csv", "site_copy_trials.json"
CHECKS_BEFORE = "2e748c9"            # the last commit before this task changed a check
VERIFY_LAYER_AT = "16b1efd"          # the commit the stage-4 checks hold scripts/verify_layer.py to
CHECK_FILES = ["scripts/verify_decision.py", "scripts/exercise_layer.py", "scripts/exercise_decision.py", "scripts/exercise_share.py", "scripts/exercise_layer_safari.py", "scripts/exercise_decision_safari.py",
               "scripts/run_decision_checks.py", "scripts/check_pages_live.py", "scripts/write_decision_layer.py", "scripts/write_results.py"]
OUTSIDE_GIT = {".session_scratch_2026-10-05/make_layer_md.py": ".session_scratch_2026-10-05/site_copy/make_layer_md.before_site_words.py"}    # a writer git does not hold: the file as it was, saved beside the audit's working files
THIS_SCRIPT, BEFORE_THE_GUIDE = "scripts/check_site_copy.py", "6607784"      # this script did not exist at CHECKS_BEFORE: its own changes are tabled against the last commit before the Guide button (13 October 2026)
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
        hansen = bool(cells) and cells[0].startswith("Tree canopy in 2000 and tree cover loss")       # reworded with the six lines of 11 October 2026: no longer outside the list of phrases
        for c_, cell in enumerate(cells):
            add("Sources", f"sources_html, row {n_ + 1}, cell {c_ + 1}", "text", cell, "" if overlay or hansen else "a cell of Sources other than the overlay row's and the Hansen row's", key="sources_html")
    for t in blocks(re.sub(r"<table>.*?</table>", " ", D["sources_html"], flags=re.S)):
        add("Sources", "sources_html, outside its table", "text", t, key="sources_html, outside its table")
    add("decision view: controls", "decision.title", "text held in the data (the page draws it nowhere since 11 October 2026)" if new else LABEL + "a heading on the side panel", V.get("title"))
    add("decision view: controls", "decision.radio", LABEL + "the decision view's switch", V["radio"])
    for w in V["windows"]:
        add("decision view: controls", f"decision.windows[{w['id']}].label", "text beside a button (a window's years)", w["label"])
        add("decision view: controls", f"decision.windows[{w['id']}].is", "i (the window's description)" if new else "text under a window's years", w["is"], FROM_55 + ": a window's description")
    for c in V["cells"]:
        for k, what in (("name", "a cell's name"), ("legend", "a cell's name"), ("def", "a cell's definition"), ("rests", "a cell's reason"), ("work", "a work-type field"), ("row", "a cell's row"), ("loss", "a cell's column")):
            add("decision view: legend and why this tier", f"decision.cells[{c['id']}].{k}", "text (a cell's definition, written by the page's builder)" if k == "def" else "text", c.get(k),
                "" if k == "def" else FROM_55 + ": " + what)                     # a definition is worded by scripts/_layer_decision.py, not read from 55_decision/: inside the list of phrases since the six lines
    for k, v in V["tier_why"].items():
        add("decision view: legend and why this tier", f"decision.tier_why[{k}]", "text", v, FROM_55 + ": a tier's reason")
    add("decision view: legend and why this tier", "decision.governance", "text (the prompt of an outside-village unit)", V["governance"])      # the page's own words since 11 October 2026 (the owner's ruling): no longer outside the list of phrases
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


# The copy's README, old beside new: which section became which. A heading named in neither column pairs with the section of the same heading.
README_PAIRS = {"WHAT IT IS": "WHAT IT SHOWS", "WHAT IT IS NOT": "WHAT IT ISN'T", "THE MAP OVERLAY IS NOT IN THIS COPY": "LEFT OUT OF THIS COPY", "THE DEVELOPMENT INDEX IS NOT IN THIS COPY": "LEFT OUT OF THIS COPY",
                "PASSING IT ON": "SHARING IT"}


def paired(before, after):
    """The strings of one build before and after, side by side: by key where a key holds one string, in order where it holds several; the page's own words and the README's sections by the lists written out above."""
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
        if k == "README.txt":
            head = lambda r: r["where"].split(": ", 1)[1]
            new_, used = {head(r): r for r in b}, set()
            for r in a:
                to = README_PAIRS.get(head(r), head(r))
                out.append((r, new_.get(to)))
                used.add(to)
            out += [(None, r) for r in b if head(r) not in used]
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
         r"|rank_none|within_tier|within_tier_share|rank_unranked|rank_filter_note|rank_out_kept|rank_out_dropped|keep_out|district_pick)",
         r"\.decision\.cells\[\d+\]\.def", r"\.decision\.governance", r"\.decision\.t\.grid_cols\[0\]"]        # the parts of data.js that hold words this task reworded: each written out (the last three with the six lines)
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
    ("both", "layer hansen_loss"): {"30": "the owner's words of 11 October 2026 for the layer's 'i' (his third handoff) say where the layer counts loss: 'only where canopy was above 30 % in 2000', the figure its grey notes already give",
                                    "2001": "the deck's note says 'cleared outright since 2001'; the year also stands in the layer's name and in its legend title",
                                    "2025": "the deck's name is 'Tree cover loss since 2001 (Hansen)': the end year left the name and still stands in the legend title, 'Tree cover loss 2001-2025 ...'"},
    ("both", "layer corestack_net"): {"2017": "the deck's name is 'Degradation minus improvement (CoRE Stack)': the years left the name and still stand in the legend title",
                                      "2023": "as for 2017: the years left the layer's name and still stand in its legend title"},
    ("both", "layer agreement"): {"2017": "the deck's name is 'Hansen and CoRE Stack compared': the years left the name and still stand, twice, in the legend title",
                                  "2023": "as for 2017: the years left the layer's name and still stand in its legend title"},
    ("both", "layer nirv"): {"8": "'Landsat 8' stood in the layer's name and in the heading of the unit panel's NIRv section; the section is gone and the name is 'Greenness trend (NIRv)', so it stands once, in the entry's 'i' (and in About)",
                             "2013": "as for 8: the years of the test, 2013-2025, now stand once, in the entry's 'i' (and in About)", "2025": "as for 8: the years of the test, 2013-2025"},
    ("both", "a unit's panel, section 2"): {"2000": "the section's heading no longer names the year: 'Loss by canopy in 2000 (what the forest mask leaves out)' became 'Loss outside the forest mask'; its rows and its 'i' still say 2000"},
    ("both", "about_html"): {"2000": "the owner's bullet on Hansen of 11 October 2026 (his third handoff) no longer names the year: 'canopy that was fairly closed in 2000' and 'land that was already open in 2000' are gone from it",
                             "2013": "the deck's item on NIRv gives the years of the test, 2013-2025", "2025": "the deck's item on NIRv gives the years of the test, 2013-2025",
                             "7": "the deck's item on NIRv gives the date of the decision, 7 October 2026 (docs/RESULTS.md section 6)", "2026": "the deck's item on NIRv gives the date of the decision, 7 October 2026"},
    ("copy", "about_html"): {"10": "the copy's About no longer has the full layer's paragraph on the overlay (tiles of loss on land with about 10 % canopy in 2000, version v1.13, loss through 2025): the owner's paragraph for the copy has no figure",
                             "2000": "as for 10: the overlay's paragraph is the owner's for the copy; and, as in the full layer, his bullet on Hansen of his third handoff no longer names the year", "1.13": "as for 10: the overlay's paragraph is the owner's for the copy"},
    ("both", "sources_html"): {t: "the Hansen row of Sources, in the owner's words of 11 October 2026 (his third handoff), says what was reconciled: 'the state's canopy of 2000 and its loss for 2001-2020 ... which stop at 2020'"
                               for t in ("2000", "2001", "2020")},
    ("copy", "README.txt"): {t: "the README's credits are read from the layer's Sources, and follow its Hansen row: 'the state's canopy of 2000 and its loss for 2001-2020 ... which stop at 2020'" for t in ("2000", "2001", "2020")},
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
PHRASES_OF_THE_SIX = ["core stack's own check", "already open in 2000", "fairly closed", "no forest loss in the window", "is none: under", "no village plan", "own dashboard", "state totals reconciled"]   # added by the owner with his six lines
BUT_NOT_AFTER = {"no forest loss in the window": "little or "}     # the head he gave the column, "Little or no forest loss in the window", holds the old head's words: the old head is the phrase without these words before it


def has_phrase(phrase, text):
    return re.search((f"(?<!{re.escape(BUT_NOT_AFTER[phrase])})" if phrase in BUT_NOT_AFTER else "") + r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", norm(text)) is not None


def unquoted(text, sentences):
    """A text without what it quotes: what stands between curly quotation marks, and the provider's registered sentences."""
    t = re.sub(r"“[^”]*”", " ", text)
    for s in sentences:
        t = t.replace(s, " ")
    return t


# ---- c. the cautions --------------------------------------------------------------------------------------------------------------------------------
def cautions(across):
    """The twenty-two cautions of the deck's section 8: (number, what it is, the words that must be reachable - every one of them; a tuple means any one of its members -, where).
    Cautions 4 and 6 are as the owner reworded them in his third handoff of 11 October 2026: Hansen does see loss on open land, and the check that fails in the East Coast zone is this project's placebo test."""
    page, full, readme = ("layer", "copy"), ("layer",), "readme"
    return [
        (1, "not a verdict on any place; not a score", ["not a verdict", "no score"], page),
        (2, "ranked within a district, never across the state; across-state agreement not established, with its interval", ["never across the state", "not established", across], page),
        (3, "what standing forest is, in the owner's words", [STANDING_IS], page),
        (4, "Hansen can't see thinning; it's a floor", ["can't see thinning", "a floor"], page),
        (5, "CoRE Stack's classifiers are right about two times in three; read Degradation with Improvement", ["two times in three", ("read it next to improvement", "read degradation beside improvement")], page),
        (6, "our placebo test fails in the East Coast zone, on few districts", ["our placebo test fails", "east coast zone", "few districts"], page),
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


# ---- g. the guide and the loader (the owner's handoff of 13 October 2026) ----------------------------------------------------------------------------
GUIDE_MD = "docs/GUIDE.md"
GUIDE_PICTURES = 5                                              # the owner's five: docs/guide/01_page.webp to 05_note.webp
GUIDE_BUTTON = ('<button id="b_sources" title="Where the data comes from, and under what licence">Sources</button>'
                '<button id="b_guide" title="What every control does, and how the map was made and checked">Guide</button></p>')      # the third button, after the other two, with his label and his hover text
LOADING, DRAWING = "Loading the map\u2026", "Drawing the units\u2026"      # the loader's two messages, in his words
# The strings a reader can see that the Guide button and the loader added to the page itself (index.html), each written out: (where it is, the string).
ADDED_13_OCT = [("index.html, <button>", "Guide"), ("index.html, title=", "What every control does, and how the map was made and checked"), ("index.html, markup", LOADING),
                ("index.html, a string of its script", DRAWING)]
ADDED_NOTE = "added with the Guide button and the loader (the owner's handoff of 13 October 2026)"
# The places where the Guide button and the loader changed index.html, each written out: (the page as it is, the page as it was). Each is found exactly once; with every one put back, the page is byte for byte the one kept.
PAGE_13_OCT = [
    ("""/* the guide (added 13 Oct 2026): docs/GUIDE.md as the builder turned it into HTML, shown in the window the About and Sources texts use. A picture is as wide as the text; a table wider than the window scrolls sideways inside it */
.guide h2 { font-size: 15px; text-transform: none; letter-spacing: 0; color: #1c1c1c; margin: 22px 0 6px; padding-bottom: 3px; border-bottom: 1px solid #ddd; }
.guide img { display: block; width: 100%; height: auto; border: 1px solid #bbb; box-sizing: border-box; }
.guide p.pic { margin: 12px 0 2px; }
.guide p.pic + p { color: #555; font-size: 12.5px; margin-top: 2px; }
.guide .wide { overflow-x: auto; margin: 8px 0; }
.guide code { font-size: 12.5px; background: #f3f3f0; border-radius: 2px; padding: 0 3px; }
.guide li { margin: 3px 0; }
#b_about, #b_sources, #b_guide { padding: 4px 8px; margin-right: 3px; }       /* the three buttons stay on one line in the side panel, also beside a scroll bar */
/* the loader (added 13 Oct 2026): over the map area from the moment the page opens until it is ready. Its bar moves and counts nothing: the page cannot know how much of data.js has arrived */
#loading { position: absolute; top: 0; right: 0; bottom: 0; left: 0; z-index: 1100; background: #e9eef2; display: flex; flex-direction: column; align-items: center; justify-content: center; }
#loadmsg { margin: 0 0 10px; font-size: 15px; color: #333; }
#loadbar { width: 180px; height: 4px; border-radius: 2px; background: #c9d3da; overflow: hidden; }
#loadbar span { display: block; width: 40%; height: 100%; border-radius: 2px; background: #47657a; animation: loadbar 1.1s ease-in-out infinite alternate; }
@keyframes loadbar { from { transform: translateX(0); } to { transform: translateX(150%); } }
""", ""),
    ('<button id="b_guide" title="What every control does, and how the map was made and checked">Guide</button>', ""),
    ('<div id="loading" role="status"><p id="loadmsg">Loading the map&hellip;</p><div id="loadbar"><span></span></div></div>', ""),
    ("""  // ---- the loader (added 13 Oct 2026) ---------------------------------------------------------------------------------------------
  // The page opens with a message over the map area. It is written in the markup above, so it shows while data.js is still arriving.
  // Here the data is in. The message changes, the browser is given one frame to paint it, and only then is the map drawn: by start(),
  // which is the rest of this script. A timer stands behind the frame, for a window that is given no frames (a tab in the background).
  // The message goes where the page says it is ready, at the end of start().
  document.getElementById("loadmsg").innerHTML = "Drawing the units&hellip;";
  var begun = false;
  function begin() { if (!begun) { begun = true; start(); } }
  if (window.requestAnimationFrame) { window.requestAnimationFrame(function () { setTimeout(begin, 0); }); }
  setTimeout(begin, 300);
  function start() {       // everything from here to the end of this script is this one function: its lines keep the indentation they had before 13 Oct 2026
""", ""),
    ("""$("modal").style.display = "block"; $("modalbody").parentNode.scrollTop = 0; }       // each text opens at its top (13 Oct 2026: the guide is long)
""", """$("modal").style.display = "block"; }
"""),
    ("""  $("b_guide").onclick = function () { modal(D.guide_html); };       // the guide (added 13 Oct 2026): docs/GUIDE.md as the builder turned it into HTML, in the same window
""", ""),
    ("open=about|sources|guide.", "open=about|sources."),
    (' else if (h0.open === "guide") { modal(D.guide_html); }', ""),
    ("""  $("loading").style.display = "none";       // the map is drawn: the loader goes (added 13 Oct 2026)
""", ""),
    ("""  }                        // the end of start()
""", ""),
]


def page_before_13_oct(page):
    """index.html with every place the Guide button and the loader changed put back as it was: (the page, what could not be put back - a list, empty when nothing)."""
    wrong = []
    for is_, was in PAGE_13_OCT:
        if page.count(is_) != 1:
            wrong.append(f"'{squeeze(is_)[:60]}' stands {page.count(is_)} time(s), not once")
        page = page.replace(is_, was)
    return page, wrong


# -- the gate on the guide's figures --
# A figure, as the guide or a file writes it: digits, with their thousands separators and decimals; a minus sign before them; a per cent sign after them, with or without a space; ha, km², MB, crore or lakh
# after them. Each of these is one figure, taken whole: a date (9 October 2026), a financial year (FY2018-19), a version (1.9.4), two figures joined by a multiplication sign (1280 × 800), a word with a digit
# in it (R6.20, v1.13, ACT4D, 21st-century, 2-Clause: compared without regard to capitals), and in the guide a code span with a digit in it (a file's or a command's name). A number written as a word is not
# a figure. The owner's four allowances, and no other, are made by g_norm(): thousands separators, a space before %, the minus sign, and × against x.
G_MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
G_NUMBER = r"\d+(?:,\d{3})*(?:\.\d+)?"
G_TOK = re.compile(rf"""`[^`]*\d[^`]*`
  | \d{{4}}-\d\d-\d\dT\d\d:\d\d:\d\dZ
  | \d{{1,2}}\s(?:{G_MONTHS})\s\d{{4}}
  | FY\d{{4}}-\d{{2}}
  | (?<![\w.])\d+(?:\.\d+){{2,}}(?![\w])
  | (?<![\w.])(?=[\w.-]*[A-Za-z])(?=[\w.-]*\d)[A-Za-z0-9_][\w.-]*[A-Za-z0-9_]
  | {G_NUMBER}\s[\u00d7x]\s{G_NUMBER}
  | (?:\u2212|(?<![\w)\u2212-])-)?{G_NUMBER}(?:\s?%|\s(?:ha|km\u00b2|km2|MB|crore|lakh)(?![A-Za-z]))?""", re.X)
G_WORD = re.compile(r"[A-Za-z]+(?:'[a-z]+)?")
G_SENTENCE = re.compile(r"""(?<=[.?!])(?<!\bSl\.)(?<!S\.O\.)(?<!\bal\.)(?<!Prof\.)\s+(?=[A-Z0-9\u201c"(`])""")      # where one sentence ends and the next begins; not after Sl., S.O., et al. or Prof.
G_NUMERIC_CELL = re.compile(r"[\d,.\s%\u2212-]+")
RULE_LINE = re.compile(r"\|(\s*:?-+:?\s*\|)+")


def g_norm(t):
    """A figure for comparing: the owner's four allowances and no other. A word with a digit in it is compared without regard to capitals."""
    if t.startswith("`"):
        return t
    if re.search(r"[A-Za-z]", re.sub(r"(?:\s?%|\s(?:ha|km\u00b2|km2|MB|crore|lakh)|\s[\u00d7x]\s|" + G_MONTHS + r"|^FY)", "", t)):
        return t.lower()
    t = t.replace("\u2212", "-").replace("\u00d7", "x").replace("km\u00b2", "km2")
    t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", t)
    return re.sub(r"(?<=\d)\s+%", "%", t)


def g_figures(text):
    """The figures of a text, each as g_norm() writes it, in order."""
    return [g_norm(m.group(0)) for m in G_TOK.finditer(text)]


def g_pairs(text):
    """Each figure of a text with the word before it and with the word after it: what stands beside a figure is part of how it is written ("30 districts", "tier 2")."""
    seq, pos = [], 0
    for m in G_TOK.finditer(text):
        seq += [("w", w.lower()) for w in G_WORD.findall(text[pos:m.start()])] + [("f", g_norm(m.group(0)))]
        pos = m.end()
    seq += [("w", w.lower()) for w in G_WORD.findall(text[pos:])]
    return {(seq[i][1], seq[i + 1][1]) for i in range(len(seq) - 1) if "f" in (seq[i][0], seq[i + 1][0]) and not seq[i][1].startswith("`") and not seq[i + 1][1].startswith("`")}


def g_words(text):
    return set(re.findall(r"[a-z]{4,}", text.lower()))


def g_md(s):
    """A line of Markdown without what is not its words: a picture leaves nothing (its file's name and the numbers in it are not figures), a link leaves its words (the address it points to is not a figure), bold loses its marks."""
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s.replace("**", "")


def guide_units(md):
    """The guide cut into the pieces its figures are held by: a sentence of a paragraph, of a list item or of a table's cell. Each: line, section, text, `beside` (for a cell that is only a figure:
    the other cells of its row, one of which the passage must hold too), and for a row of a table its first cell (`row`), the cell's place (`column`) and the whole row (`with`), whose words help
    to choose among the passages that hold the cell's figures."""
    out, section = [], ""
    for n, line in enumerate(md.splitlines(), 1):
        if not line.strip() or RULE_LINE.fullmatch(line.strip()):
            continue
        if line.startswith("#"):
            section = line.lstrip("#").strip()
        plain_ = g_md(line).strip()
        if not plain_:
            continue
        if plain_.startswith("|"):
            cells = [c.strip() for c in plain_.strip("|").split("|")]
            words_ = [c for c in cells if c and not G_NUMERIC_CELL.fullmatch(c)]
            for k, c in enumerate(cells):
                for s in G_SENTENCE.split(c):
                    if g_figures(s):
                        out.append({"line": n, "section": section, "text": s.strip(), "beside": words_ if G_NUMERIC_CELL.fullmatch(c) else None, "row": cells[0], "column": k, "with": " ".join(cells)})
        else:
            for s in G_SENTENCE.split(re.sub(r"^(#{1,3} |- |\d+\. )", "", plain_)):
                if g_figures(s):
                    out.append({"line": n, "section": section, "text": s.strip(), "beside": None, "row": None, "column": None, "with": ""})
    return out


def g_passage(where, text):
    text = text.replace("`", "").replace("**", "").replace("*", "")
    return {"where": where, "text": text, "figures": set(g_figures(text)), "pairs": g_pairs(text), "words": g_words(text), "norm": norm(text)}


def passages_of_markdown(text):
    """A document's passages: a paragraph, an item of a list, or a row of a table."""
    out = []
    for block in re.split(r"\n\s*\n", text):
        ls = [l.strip() for l in block.splitlines() if l.strip()]
        if ls and all(l.startswith("|") for l in ls):
            out += [g_passage("a row of a table", l) for l in ls if not RULE_LINE.fullmatch(l)]
            continue
        item = []
        for l in ls:
            if re.match(r"(- |\d+\. |#)", l) and item:           # a new item of a list, or a heading, ends the passage before it
                out.append(g_passage("an item of a list" if re.match(r"(- |\d+\. )", item[0]) else "a paragraph", " ".join(item)))
                item = []
            item.append(l)
        if item:
            out.append(g_passage("an item of a list" if re.match(r"(- |\d+\. )", item[0]) else "a paragraph", " ".join(item)))
    return out


def passages_of_json(x, path=""):
    """A record's passages: the plain values of one object, or of one list, read together."""
    out = []
    if isinstance(x, dict):
        scal = "; ".join(f"{k}: {v}" for k, v in x.items() if isinstance(v, (str, int, float)) and not isinstance(v, bool))
        if scal:
            out.append(g_passage(path or "(the top)", scal))
        for k, v in x.items():
            out += passages_of_json(v, f"{path}/{k}" if path else k)
    elif isinstance(x, list):
        scal = "; ".join(str(v) for v in x if isinstance(v, (str, int, float)) and not isinstance(v, bool))
        if scal:
            out.append(g_passage(path, scal))
        for k, v in enumerate(x):
            out += passages_of_json(v, f"{path}[{k}]")
    return out


def passages_of_html(text):
    """A registered web page's passages: the words between one block tag and the next."""
    parts = re.split(r"</?(?:p|div|li|ul|ol|blockquote|h[1-6]|br|tr|table|pre|section|article|header|footer)(?:\s[^>]*)?>", re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", text))
    return [g_passage("a block of the page", t) for t in (plain(p) for p in parts) if t]


def passages_of_the_page(b):
    """The page's own strings in data.js, as a reader meets them: the strings of one place read together - a layer's name, legend title, notes, "i" and the count beside each class; a section of the unit
    panel with its "i"; a cell with its definition, its reason, its work types, its count in each window and its label in the provisional order; a row of Sources - and every other string by itself.
    Not among them: the guide itself, the build's own date, and the values of the units' rows."""
    D, V = b["D"], b["D"]["decision"]
    groups = {}

    def put(key, text):
        groups.setdefault(key, []).append(text)
    for r in strings({**b, "readme": None}):
        w = r["where"]
        if (w.startswith("f[][") and ": " in w) or w in BUILD_SPECIFIC:      # a value of a unit's row, its figures written N: not a string with a figure. The small-forest warning, which is one, stays
            continue
        m = re.match(r"layers\[(\w+)\]\.|tips\.layer:(\w+)$", w)
        key = (f"the layer {m.group(1) or m.group(2)}" if m else None)
        m = key is None and re.match(r"panel\[(\d+)\]\.|tips\.panel:(\d+)$", w)
        key = key or (f"section {m.group(1) or m.group(2)} of the unit panel" if m else None)
        m = key is None and re.match(r"decision\.cells\[(\w+)\]\.|decision\.tier_why\[(\w+)\]$", w)
        key = key or (f"the cell {m.group(1) or m.group(2)}" if m else None)
        m = key is None and re.match(r"decision\.windows\[(\w+)\]\.", w)
        key = key or (f"the window {m.group(1)}" if m else None)
        m = key is None and re.match(r"sources_html, row (\d+), cell", w)
        key = key or (f"row {m.group(1)} of Sources" if m else None)
        key = key or ("the minimum-forest choice" if w.startswith("floors[") or w == "tips.floors" else "the kinds of unit" if w.startswith("unit_types.") or w == "tips.units" else w)
        put(key, r["text"])
    for l in D["layers"]:
        for s, counts in (l.get("counts") or {}).items():
            put(f"the layer {l['id']}", "; ".join(f"{c['label']}: {counts[i]}" for i, c in enumerate(l["classes"])) + ("" if s == "all" else f" (minimum forest {s} ha)"))
    for k, cid in enumerate(V["tiers"]):                        # a tier's label as the page draws it in the legend and the list: its own words for a tier, filled with the cell's place in the provisional order
        c = next(c for c in V["cells"] if c["id"] == cid)
        put(f"the cell {cid}", V["t"]["tier"].replace("{k}", str(k + 1)).replace("{name}", c["name"]))
    for w in V["windows"]:
        for i, c in enumerate(V["cells"]):
            put(f"the cell {c['id']}", f"{w['label']}: {V['counts'][w['id']][i]}")
    return [g_passage(k, " | ".join(v)) for k, v in groups.items()]


GUIDE_FILES = ["the page's own strings in data.js", "docs/GAP.md", "docs/DECISION_LAYER.md", "README.md", "60_layer/decision_runs.json", "60_layer/site_copy_check.json", "70_share/exercise_share_chrome.json",
               "00_raw/05_forest_reference/provider_cautions.json", "60_layer/site_copy_looked_at.json"]      # the owner's nine, in his order
UMD_PAGE = "00_raw/05_forest_reference/umd_global_forest_change_2025_v1_13_page_2026-10-08.html"      # a tenth, for one sentence: see GUIDE_ONLY_FROM
# Where a part of the guide may be traced to one file only. The analysis: the guide says its full account is docs/GAP.md. The citation of the paper behind Hansen's data: the registered page of the University of
# Maryland, which 00_raw/05_forest_reference/provider_cautions.json names as its input with its sha256 - the one file beyond the owner's nine, and for this one sentence only.
GUIDE_ONLY_FROM = [(lambda u: u["section"] == "What the analysis behind it found", ["docs/GAP.md"]), (lambda u: u["text"].startswith("Hansen et al. 2013, High-resolution global maps"), [UMD_PAGE])]
# The record this check itself writes is among the owner's nine for one thing, the count of its own checks: that count is held to the run that writes the record (g7), and no other figure is traced to the record of an earlier run.
NOT_SEARCHED = ["60_layer/site_copy_check.json"]
# The two tables of the guide whose rows are each about one file, named in the row's first cell: a figure of such a row is looked for only in passages that name that file.
ROWS_NAME_A_FILE = ["How it was checked", "The code and the documents"]


def _mb(x):
    f = {i["path"].split("/")[-1]: i["bytes"] for i in (x["json"].get("70_share/exercise_share_chrome.json") or {}).get("inputs", []) if i["path"].startswith(f"70_share/{NAME}/") and i["path"].endswith(("index.html", "data.js"))}
    if set(f) != {"index.html", "data.js"}:
        return None, "70_share/exercise_share_chrome.json does not give the bytes of the copy's index.html and data.js", None
    return f"{round(sum(f.values()) / 1e6)} MB", f"70_share/exercise_share_chrome.json, its inputs: index.html {f['index.html']:,} bytes and data.js {f['data.js']:,} bytes, {sum(f.values()):,} bytes together", None


def _from(file, must_hold, make):
    """A source for a derived figure: the one passage of `file` that holds every one of `must_hold` (words as they stand there); make() gives the figure the guide may then write.
    Gives (the figure, where it comes from in words, the passage)."""
    def source(x):
        hits = [p for p in x["passages"].get(file, []) if all(norm(w) in p["norm"] for w in must_hold)]
        if not hits:
            return None, f"{file}: no passage holds " + " ... ".join(must_hold), None
        return make(), f"{file}: '... " + " ... ".join(must_hold) + " ...'", hits[0]
    return source


# Every figure of the guide that stands in none of the named files as the guide writes it, with how it comes from one that does: (the first words of the guide's sentence, the figure as the guide writes it,
# how it comes from the file's, the source). The gate finds the source in the file, works the figure out again, and fails if the guide's differs. The megabytes are the one figure this build itself sets.
GUIDE_DERIVED = [
    ("The page carries about", "{megabytes}", "bytes to megabytes: the bytes of the published copy's index.html and data.js, as the record of the copy's own check gives them, added, divided by 1,000,000 and rounded to a whole number", _mb),
    ("1 ha is the smallest patch the Forest Survey of India counts as forest cover, and about", "14", "13.8 pixels, rounded to a whole number and said with 'about'",
     _from("docs/DECISION_LAYER.md", ["The proposal, 1 ha, is 13.8 pixels"], lambda: str(round(13.8)))),
    ("Splitting the same money by need would move", "72.07 crore", "lakh to crore: 7,207.11 lakh rupees, divided by 100 and rounded to two decimals",
     _from("docs/GAP.md", ["The same money distributed by need", "would move 7,207.11 lakh rupees"], lambda: f"{7207.11 / 100:.2f} crore")),
    ("Splitting the same money by need would move", "139.16 crore", "lakh to crore: 13,915.72 lakh, divided by 100 and rounded to two decimals",
     _from("docs/GAP.md", ["R6.20 plantation expenditure", "13,915.72 lakh over FY2018-19 to FY2025-26"], lambda: f"{13915.72 / 100:.2f} crore")),
    ("67.1 % of it lies in 5 districts", "67.1%", "the same figure: the file writes 'per cent' in words", _from("docs/GAP.md", ["67.1 per cent of the state's N1 lies in 5 districts"], lambda: "67.1%")),
    ("66,060 ha, 74 % of the need", "74%", "the same figure: the file writes 'per cent' in words", _from("docs/GAP.md", ["The finding, in volumes first", "66,060 ha of N1, 74 per cent of it, lie in districts"], lambda: "74%")),
    ("The 8 districts where over half the people are Scheduled Tribe", "78.1%", "the same figure: the file writes 'per cent' in words", _from("docs/GAP.md", ["The 8 districts in the class", "hold 78.1 per cent of the need"], lambda: "78.1%")),
    ("The 8 districts where over half the people are Scheduled Tribe", "57.7%", "the same figure: the file writes 'per cent' in words",
     _from("docs/GAP.md", ["The 8 districts in the class", "received 57.7 per cent of the post-period plantation money"], lambda: "57.7%")),
    ("The minimum forest of 100 ha for any loss rate was set on", "7 October 2026", "the same date: the file shortens the month, '7 Oct 2026'",
     _from("README.md", ["The floor for a rate is 100 ha, by ruling of the project owner (7 Oct 2026)"], lambda: "7 October 2026")),
    ("Hansen et al. 2013, High-resolution global maps", "853", "the same pages: the file shortens the last page, '850-53'",
     _from(UMD_PAGE, ["High-Resolution Global Maps of 21st-Century Forest Cover Change. Science 342 (15 November): 850-53"], lambda: "853")),
]
# The sentences of the guide whose figures stand in two passages: (the first words of the sentence, the figures that stand in a passage of their own, words that passage must hold). Each part must stand, whole, in one passage.
GUIDE_SPLIT = [
    ("A fixed 1 ha bar is easier for a large forest to cross", ["2"], "Tier 2: Closed forest, loss recorded - find the cause first"),      # "tier 2": the cell's place in the provisional order, which the page counts; the count of units and the share stand in the About text
    ("It does not track the Survey's net change in forest cover from 2021 to 2023", ["2023"], "India State of Forest Report 2023"),      # the year of the Survey's report; the correlation, and the year the change is measured from, stand in a row of a table
]
# The sentences of the guide that hold one small figure, where the passage is named here because many passages hold that figure: (the first words of the sentence, words the passage must hold).
GUIDE_PIN = [
    ("The other is a layer of 2011 that no file we share carries", "The development index of 2011 is left out of the copy"),
    ("`07_build_share.py` makes this copy from the full version: it leaves one 2011 layer out", "The development index of 2011 is left out of the copy"),
    ("Hansen's record changed method in 2011", "the 2011-2025 update"),
]
# The rows of the guide's table "How it was checked" whose result is a count of this build's own runs: the row (its first cell). Their result cells are not searched for: g5 holds them to the records of the runs, and g7 this check's own.
GUIDE_PINNED_ROWS = ["verify_layer.py", "verify_decision.py", "exercise_layer.py, in Chrome and in WebKit", "exercise_decision.py, in Chrome and in WebKit", "exercise_share.py", "check_site_copy.py"]


def trace_guide_figures(md, x):
    """Every figure of the guide, traced. x: {"passages": {file: [passage]}, "json": {file: its content}}. Returns (rows, wrong): a row for each sentence or cell with a figure, saying where its
    figures stand; and what is wrong (a list, empty when nothing is)."""
    units, rows, wrong = guide_units(md), [], []
    used = {"derived": set(), "split": set(), "pin": set()}
    for u in units:
        figs = list(dict.fromkeys(g_figures(u["text"])))
        row = {"line": u["line"], "section": u["section"], "the_guides_words": u["text"], "its_figures": "; ".join(f.strip("`") for f in figs)}
        if u["section"] == "How it was checked" and u["column"] == 2 and u["row"].replace("`", "") in GUIDE_PINNED_ROWS:
            rows.append({**row, "how": "a count of this build's own runs", "file": "the record of the run (checks g5 and g7)", "passage": ""})
            continue
        derived, first = [], []                                 # first: the passages the derived figures come from, where the sentence's other figures are looked for first
        for n_, (start, fig, how, source) in enumerate(GUIDE_DERIVED):
            if start not in u["text"]:
                continue
            used["derived"].add(n_)
            got, said, passage = source(x)
            if fig == "{megabytes}":                            # whatever megabytes the guide writes, they must be the megabytes of the copy on record
                mine = next((f for f in figs if f.endswith(" MB")), None)
                if mine is None or got is None or mine != got:
                    wrong.append(f"line {u['line']}: the guide writes '{mine}' and the copy's two files come to '{got}' ({said})")
                derived.append((mine, how, said))
            elif fig not in figs:
                wrong.append(f"line {u['line']}: the listed figure '{fig}' is not a figure of the sentence that begins '{start[:40]}'")
            elif got is None or g_norm(got) != fig:
                wrong.append(f"line {u['line']}: '{fig}' does not come from the file as listed ({said})" + ("" if got is None else f": it gives '{got}'"))
            else:
                derived.append((fig, how, said))
                first.append((said.split(":")[0], passage))
        for d in derived:
            rows.append({**row, "its_figures": (d[0] or "").strip("`"), "how": "comes from a figure of a named file: " + d[1], "file": d[2].split(":")[0].split(",")[0], "passage": d[2]})
        rest = [f for f in figs if f not in {d[0] for d in derived}]
        if not rest:
            continue
        only = next((files for test, files in GUIDE_ONLY_FROM if test(u)), None)
        files = [f for f in (only or GUIDE_FILES) if f not in NOT_SEARCHED]
        names = [f for f in rest if f.startswith("`")]          # a file's or a command's name stands whole, by itself: each is looked for in a passage of its own
        rest = [f for f in rest if not f.startswith("`")]
        parts, must = ([rest] if rest else []), {}
        for n_, (start, own, holds_) in enumerate(GUIDE_SPLIT):
            if u["text"].startswith(start):
                used["split"].add(n_)
                if not set(own) < set(rest):
                    wrong.append(f"line {u['line']}: the listed split {own} is not a part of this sentence's figures {rest}")
                parts = [[f for f in rest if f not in own], list(own)]
                must[tuple(own)] = [norm(holds_)]
        for n_, (start, holds_) in enumerate(GUIDE_PIN):
            if u["text"].startswith(start):
                used["pin"].add(n_)
                must[tuple(rest)] = [norm(holds_)]
        parts += [[f] for f in names]
        row_names = [norm(c) for c in re.findall(r"`([^`]+)`", u["row"] or "")] if u["section"] in ROWS_NAME_A_FILE and u["column"] else []
        mine_words, mine_pairs = g_words(u["text"]) | g_words(u["with"]), g_pairs(u["text"])
        for part in parts:
            def holds(p):
                return all((t.strip("`") in p["text"]) if t.startswith("`") else (t in p["figures"]) for t in part) and (u["beside"] is None or any(norm(c) in p["norm"] for c in u["beside"])) \
                    and all(w in p["norm"] for w in must.get(tuple(part), [])) and (part[0].startswith("`") or all(n_ in p["norm"] for n_ in row_names))
            best = None                                         # a passage that one of this sentence's figures comes from is taken if it holds the part. Otherwise, of the passages that hold every figure of
            for k, f in enumerate([q[0] for q in first] + files):      # the part: first by how many figures stand beside the same word as in the sentence, then by the files' order (the owner's), then by how
                if k == len(first) and best is not None:                # like the sentence the passage is (the words they share, over the words of either)
                    break
                for p in ([first[k][1]] if k < len(first) else x["passages"].get(f, [])):
                    if p is not None and holds(p):
                        shared = len(mine_words & p["words"])
                        beside = len({q for q in mine_pairs if q[0] in part or q[1] in part} & p["pairs"])
                        key = (beside, -k, shared / max(1, len(mine_words | p["words"])))
                        if (shared or beside or u["beside"] or part[0].startswith("`")) and (best is None or key > best[0]):
                            best = (key, f, p, shared, beside)
            if best is None:
                wrong.append(f"line {u['line']}: {[t.strip('`') for t in part]} of '{u['text'][:70]}' stand together in no passage of " + ("; ".join(files) if only else "a named file") + " that shares a word with it"
                             + (f" and names {row_names}" if row_names and not part[0].startswith("`") else ""))
                rows.append({**row, "its_figures": "; ".join(t.strip("`") for t in part), "how": "NOT FOUND", "file": "", "passage": ""})
            else:
                rows.append({**row, "its_figures": "; ".join(t.strip("`") for t in part), "how": "found, written the same way, in one passage" + (" (one of the passages this sentence draws on)" if len(parts) > 1 else ""),
                             "file": best[1], "passage": f"[{best[2]['where']}] " + best[2]["text"][:400], "words_shared_with_the_passage": best[3], "figures_beside_the_same_word": best[4]})
    for kind, table in (("derived", GUIDE_DERIVED), ("split", GUIDE_SPLIT), ("pin", GUIDE_PIN)):
        wrong += [f"a listed case ({kind}) is of no sentence of the guide: '{table[n_][0][:60]}'" for n_ in range(len(table)) if n_ not in used[kind]]
    return rows, wrong


def guide_sources(page_build, read_):
    """What the guide's figures are traced to: the passages of each named file, and the content of the records. read_(path): the file, recorded among this check's inputs; a file that is not there gives no passage."""
    x = {"passages": {GUIDE_FILES[0]: passages_of_the_page(page_build)}, "json": {}, "missing": []}
    for f in GUIDE_FILES[1:] + [UMD_PAGE]:
        if f in NOT_SEARCHED:
            continue
        if not (ROOT / f).is_file():
            x["missing"].append(f)
            x["passages"][f] = []
            continue
        text = read_(ROOT / f).read_text(encoding="utf-8", errors="replace")
        if f.endswith(".json"):
            x["json"][f] = json.loads(text)
            x["passages"][f] = passages_of_json(x["json"][f])
        else:
            x["passages"][f] = passages_of_html(text) if f.endswith(".html") else passages_of_markdown(text)
    return x


def words_of_markdown(md):
    """The guide's words as its Markdown gives them, with every mark and all spacing taken out: for holding the HTML to them without the converter."""
    out = []
    for line in md.splitlines():
        if RULE_LINE.fullmatch(line.strip()) or re.fullmatch(r"!\[[^\]]*\]\([^)\s]*\)", line.strip()):
            continue
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", re.sub(r"^(#{1,3} |- |\d+\. )", "", line))
        out.append((t.replace("|", " ") if line.startswith("|") else t).replace("**", "").replace("*", "").replace("`", ""))
    return "".join(" ".join(out).split())


def words_of_html(h):
    return "".join(html.unescape(re.sub(r"<[^>]+>", " ", h)).split())


GUIDE_TAGS = {"div", "h1", "h2", "h3", "p", "ul", "ol", "li", "table", "tr", "th", "td", "strong", "em", "code", "a", "img"}
GUIDE_ATTRS = {"class", "href", "target", "rel", "src", "alt", "width", "height"}


def guide_html_wrong(h, md, pictures):
    """What is wrong with the guide's HTML, held to the guide's Markdown without the converter (a list, empty when nothing is). pictures: {address as the guide names it: sha256 of the file under docs/}."""
    wrong = []
    if words_of_html(h) != words_of_markdown(md):
        a, b = words_of_html(h), words_of_markdown(md)
        k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
        wrong.append(f"its words are not the guide's: they part at '{a[max(0, k - 30):k + 30]}' against '{b[max(0, k - 30):k + 30]}'")
    tags = set(re.findall(r"</?([a-zA-Z0-9]+)", h))
    if not tags <= GUIDE_TAGS:
        wrong.append(f"a tag the converter does not write: {sorted(tags - GUIDE_TAGS)}")
    attrs = set(re.findall(r"""\s([a-zA-Z-]+)=["']""", " ".join(re.findall(r"<[a-zA-Z][^>]*>", h))))
    if not attrs <= GUIDE_ATTRS or re.search(r"javascript:|<script|<style|<iframe|<link|<object|<embed|<form", h, re.I):
        wrong.append(f"an attribute or a thing the converter does not write: {sorted(attrs - GUIDE_ATTRS)}")
    links = [html.unescape(u) for u in re.findall(r'<a href="([^"]*)" target="_blank" rel="noopener">', h)]
    if h.count("<a ") != len(links) or links != re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)", md) or not all(u.startswith("https://") for u in links):
        wrong.append(f"its links are not the guide's, each opened in a new tab: {len(links)} of {h.count('<a ')} written so")
    named = re.findall(r"(?m)^!\[([^\]]*)\]\(([^)\s]+)\)$", md)
    imgs = re.findall(r'<img src="data:image/webp;base64,([A-Za-z0-9+/=]+)" alt="([^"]*)" width="(\d+)" height="(\d+)">', h)
    if h.count("<img") != len(imgs) or len(imgs) != len(named) or len(named) != GUIDE_PICTURES or re.search(r"""(?:src|href)=["'](?!data:image/webp;base64,|https://)""", h):
        wrong.append(f"{len(imgs)} pictures carried as their own bytes, of {h.count('<img')} in the HTML and {len(named)} the guide names: {GUIDE_PICTURES} are expected")
    else:
        for (b64, alt, w, hgt), (want_alt, address) in zip(imgs, named):
            if hashlib.sha256(__import__("base64").b64decode(b64)).hexdigest() != pictures.get(address) or html.unescape(alt) != want_alt or (w, hgt) != ("1280", "800"):
                wrong.append(f"the picture {address} is not carried as the bytes of its file, with the guide's words for it, at 1280 x 800")
    return wrong


def loader_and_button_wrong(page, phrases):
    """What is wrong with the Guide button and the loader in one build's index.html, read as text (a list, empty when nothing is). What a browser does with them is scripts/exercise_layer.py's to show."""
    wrong = []
    if page.count(GUIDE_BUTTON) != 1 or page.count('id="b_guide"') != 1:
        wrong.append("the button Guide, with the owner's label and hover text, does not stand once, right after About this map and Sources")
    if page.count('$("b_guide").onclick = function () { modal(D.guide_html); };') != 1 or page.count('else if (h0.open === "guide") { modal(D.guide_html); }') != 1:
        wrong.append("the button, or #open=guide in the address, does not open guide_html in the window the other two texts use")
    first = '<div id="loading" role="status"><p id="loadmsg">Loading the map&hellip;</p><div id="loadbar"><span></span></div></div>'
    tag = '<script src="data.js">'
    if page.count(first) != 1 or page.count(tag) != 1 or not page.index('<div id="mapwrap">') < page.index(first) < page.index(tag) or page.count("Loading the map") != 1:
        wrong.append("'Loading the map...' does not stand once, as plain markup in the map's area, before the tag that asks for data.js")
    own = page[page.rindex("<script>"):]
    second, fatal = 'document.getElementById("loadmsg").innerHTML = "Drawing the units&hellip;";', "The map\\'s data didn\\'t load."
    if own.count(second) != 1 or page.count("Drawing the units") != 1 or own.count(fatal) != 1 or "function start() {" not in own or not own.index(fatal) < own.index(second) < own.index("function start() {"):
        wrong.append("'Drawing the units...' is not set once, after the message for data that did not load and before the map is drawn")
    if not re.search(r"window\.requestAnimationFrame\(function \(\) \{ setTimeout\(begin, 0\); \}\);", own) or own.count("function begin() { if (!begun) { begun = true; start(); } }") != 1:
        wrong.append("the page does not give the browser a frame to paint the second message before it draws the map")
    if not re.search(r'\$\("loading"\)\.style\.display = "none";[^\n]*\n\s*window\.ICTD_READY = true;', own) or own.count("ICTD_READY = true") != 1:
        wrong.append("the loader is not put away in the line before the page says it is ready")
    if "@keyframes loadbar" not in page or not re.search(r"#loadbar span \{[^}]*animation: loadbar", page) or re.search(r"<progress|aria-valuenow|loadbar[^\n]{0,80}\.style\.width", page):
        wrong.append("the bar is not one that only moves: it must have an animation of its own and nothing that sets its width")
    for words in (LOADING, DRAWING):
        if len(words.split()) > 6 or "?" in words or ";" in words or re.search(r"\d", words) or any(has_phrase(ph, words) for ph in phrases):
            wrong.append(f"the loader's words '{words}' carry a figure, a '?' or a ';', more than six words, or a phrase of the lists")
    for said in re.findall(r'<p id="loadmsg">(.*?)</p>', page) + re.findall(r'getElementById\("loadmsg"\)\.innerHTML = "(.*?)";', own):
        if html.unescape(said) not in (LOADING, DRAWING):
            wrong.append(f"the loader says '{html.unescape(said)}', which is neither of the owner's two messages")
    return wrong


def guide_table_of_checks(md):
    """The guide's table "How it was checked": {the row's first cell without its code marks: its result cell}."""
    out, inside = {}, False
    for line in md.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip() == "How it was checked"
        elif inside and line.startswith("|") and not RULE_LINE.fullmatch(line.strip()):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 3:
                out[cells[0].replace("`", "")] = cells[2]
    return out


OF = re.compile(r"(\d[\d,]*) of (\d[\d,]*)")
counts_of = lambda text: [(int(a.replace(",", "")), int(b.replace(",", ""))) for a, b in OF.findall(text)]


def guide_counts_wrong(md, x):
    """What is wrong with the counts the guide's table of checks gives for this build's own runs, each held to the record of the run (a list, empty when nothing is). The count of this check's own
    checks is held to the run itself, at its end (g7)."""
    T, wrong = guide_table_of_checks(md), []
    runs = {e["check"]: e for e in (x["json"].get("60_layer/decision_runs.json") or {}).get("checks", [])}
    line = lambda name: (runs[name]["runs"][-1]["last_line"] if name in runs and runs[name]["runs"][-1]["exit"] == 0 else "")

    def row(name):
        if name not in T:
            wrong.append(f"the table has no row for {name}")
        return T.get(name, "")
    for name, check in (("verify_layer.py", "verify_layer"), ("verify_decision.py", "verify_decision")):
        cell, said = row(name), line(check)
        if not said or not counts_of(cell) or not counts_of(said) or counts_of(cell)[0] != counts_of(said)[0] or counts_of(cell)[0][0] != counts_of(cell)[0][1] or not set(g_figures(cell)) <= set(g_figures(said)):
            wrong.append(f"{name}: the guide says '{cell}' and the run on record ended '{said[:110]}'")
    cell = row("exercise_layer.py, in Chrome and in WebKit")
    for browser in ("Chrome", "WebKit"):
        said = line(f"exercise_layer in {browser}")
        m = re.search(r"(\d+) of (\d+) control actions did what they should; .*?; (\d+) of (\d+) displayed values equal the stage tables; script errors: none", said)
        if not m or len(counts_of(cell)) != 2 or counts_of(cell) != [(int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4)))] or any(a != b for a, b in counts_of(cell)) or "in each browser" not in cell or "no script error" not in cell:
            wrong.append(f"exercise_layer.py in {browser}: the guide says '{cell}' and the run on record ended '{said[:150]}'")
    cell = row("exercise_decision.py, in Chrome and in WebKit")
    got = {}
    for browser in ("Chrome", "WebKit"):
        said = line(f"exercise_decision in {browser}")
        m = re.search(r"(\d+) of (\d+) steps did what they should; .*?; (\d+) of (\d+) lines of 'why this tier' are as the tables give them; exports: (\d+) of (\d+) cells", said)
        got[browser] = [int(v) for v in m.groups()] if m else None
        if not m or m.group(5) != m.group(6):
            wrong.append(f"exercise_decision.py in {browser}: the run on record ended '{said[:150]}'")
    m = re.search(r"(\d+) of (\d+) steps in Chrome, (\d+) of (\d+) in WebKit; ([\d,]+) of ([\d,]+) lines of", cell)
    if all(got.values()) and (not m or [int(v.replace(",", "")) for v in m.groups()] != got["Chrome"][:2] + got["WebKit"][:2] + got["Chrome"][2:4] or got["Chrome"][2:4] != got["WebKit"][2:4]
                              or any(a != b for a, b in counts_of(cell)) or "every cell of both downloads correct" not in cell):
        wrong.append(f"exercise_decision.py: the guide says '{cell}' and the runs on record gave {got}")
    cell, S = row("exercise_share.py"), (x["json"].get("70_share/exercise_share_chrome.json") or {}).get("summary", {})
    if not counts_of(cell) or counts_of(cell)[0] != (S.get("steps_as_expected"), S.get("steps")) or S.get("steps_as_expected") != S.get("steps") or S.get("requests_to_the_network") != 0 or "no request to the network" not in cell:
        wrong.append(f"exercise_share.py: the guide says '{cell}' and the record gives {S.get('steps_as_expected')} of {S.get('steps')} steps and {S.get('requests_to_the_network')} requests to the network")
    return wrong


def records_wrong(x, now_sha, layer_run, copy_run):
    """What is wrong with the records the guide's counts and megabytes are read from: each must be of the builds on disk, and of runs that passed (a list, empty when nothing is)."""
    wrong = [f"{f} is not there" for f in x["missing"]]
    R = x["json"].get("60_layer/decision_runs.json")
    if R is not None and (R.get("unfinished") or R.get("layer_run_utc") != layer_run or any(R.get("files_sha256", {}).get(f) != now_sha[f"60_layer/{f}"] for f in ("index.html", "data.js")) or not R.get("every_check_passed_on_its_last_run")):
        wrong.append(f"60_layer/decision_runs.json is not the record of a finished pass on the layer on disk in which every check passed on its last run (it is of the layer built {R.get('layer_run_utc')})")
    S = x["json"].get("70_share/exercise_share_chrome.json")
    if S is not None and (S.get("copy_run_utc") != copy_run or any(i["sha256"] != now_sha.get(i["path"]) for i in S.get("inputs", []) if i["path"] in now_sha) or not all(s_["ok"] for s_ in S.get("steps", [{"ok": False}]))):
        wrong.append(f"70_share/exercise_share_chrome.json is not the record of a run on the copy on disk in which every step did what it should (it is of the copy made {S.get('copy_run_utc')})")
    K = x["json"].get("60_layer/site_copy_looked_at.json")
    if K is not None and (K.get("builds") != {"layer_run_utc": layer_run, "copy_run_utc": copy_run} or any(v != now_sha.get(k) for k, v in K.get("files_sha256", {}).items())):
        wrong.append(f"60_layer/site_copy_looked_at.json is not of the builds on disk (it is of {K.get('builds')})")
    return wrong


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
        other = [(p, how) for p, how in d if (p, how) not in ((".tips", "added"), (".guide_html", "added")) and not any(re.fullmatch(a, p) for a in allowed)]
        check(f"a2 ({k})", f"in the data.js of {CALLED[k]} every part is the saved copy's but the parts that hold words this task reworded (each written out in this check), the two build times, the new key `tips`"
              + (", and the overlay's part" if k == "copy" else "") + ", and - since 13 October 2026 - the new key `guide_html`, the guide the page's third button opens, which check g0 holds to docs/GUIDE.md: no class, count, colour, "
              "shape or figure array differs, and no key but those two was added or taken out",
              not other and set(B) == set(A) | {"tips", "guide_html"}, f"{len(d)} parts differ, all of them allowed" if not other else "NOT ALLOWED: " + "; ".join(f"{p} ({how})" for p, how in other[:6]))
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
            for p in PHRASES + PHRASES_OF_THE_SIX + (PHRASES_COPY_ONLY if k == "copy" else []):
                if has_phrase(p, text):
                    hits.append(f"'{p}' in {r['where']}")
        check(f"b1 ({k})", f"none of the phrases the deck lists (its section 11), and none of the eight the owner added with his six lines of 11 October 2026, is in the words of {CALLED[k]}, in an 'i'" + (" or in its README" if k == "copy" else "")
              + ", outside what the deck exempts (quotations; strings from 55_decision/; the values of a unit's panel; legend class labels; export column names and the two kinds of unit; the cells of Sources other than the overlay row's "
              "and the Hansen row's). Since the six lines the governance prompt, a cell's definition and the Hansen row of Sources are the page's own words and are inside the list", not hits,
              f"{len(PHRASES) + len(PHRASES_OF_THE_SIX) + (len(PHRASES_COPY_ONLY) if k == 'copy' else 0)} phrases looked for in {sum(1 for r in S[('after', k)] if not r['exempt']):,} strings" if not hits else "FOUND: " + "; ".join(hits[:8]))
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
                if "as built in Step " not in a["where"] and norm(a["said"]) not in whole_saved[k]:
                    never.append(f"{CALLED[k]}: '{a['said'][:70]}'")
            elif a["done"].startswith("listed"):
                n_listed += 1
                if not there:
                    lost.append(f"{CALLED[k]}: '{a['said'][:70]}'")
    check("b2", "of the audit's findings about the page (60_layer/site_copy_audit.csv): the words of each one marked fixed stood in the saved copy of the build it was found in and are no longer in that build (a finding in the deck's "
          "own words, which were only ever in a build this task made, is held to the second half alone); and the words of each one marked as listed for the owner, with nothing changed, are still there", not back and not lost and not never
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

    # f. the six lines of the owner's third handoff of 11 October 2026
    check("f0", "the copies of the two builds kept before the six lines still have the sha256 that the lists made with them give", not extra["six_wrong"],
          "; ".join(extra["six_wrong"]) or f"{extra['six_files']} files held against {len(BEFORE_SIX_LISTS)} lists")
    extra["six_changes"] = []
    for k in ("layer", "copy"):
        kept = extra["six"][k]
        pp = paired(strings(kept), S[("after", k)])
        new_ = [(b["where"], b["text"]) for a, b in pp if a is None]
        added = [w + ": " + t[:50] for w, t in new_ if (w, t) not in ADDED_13_OCT] + [f"NOT THERE, of the four of 13 October 2026: {t}" for w, t in ADDED_13_OCT if (w, t) not in new_]
        dropped = [a["where"] for a, b in pp if b is None]
        stray, back, used = [], [], Counter()
        for a, b in pp:
            if a is None or b is None or b["where"] in BUILD_SPECIFIC:
                continue
            mine = [x for x in SIX if re.fullmatch(x[1], b["where"])]
            for fix, _, old, new in mine:                        # no place of a fix still holds its old words
                if (old.search(b["text"]) if isinstance(old, re.Pattern) else old in b["text"]):
                    back.append(f"fix {fix} in {b['where']}")
            if a["text"] == b["text"]:
                continue
            t, fixes = a["text"], []
            for fix, _, old, new in mine:
                t2 = old.sub(new, t) if isinstance(old, re.Pattern) else t.replace(old, new)
                if t2 != t:
                    fixes.append(fix)
                    used[(fix, SIX.index((fix, _, old, new)))] += 1
                    t = t2
            if t != b["text"] or not fixes:
                stray.append(b["where"])
            else:
                extra["six_changes"].append({"build": CALLED[k], "fix": fixes[0], "part": b["part"], "where": b["where"], "kind": b["kind"], "as_it_was": a["text"], "as_it_is": b["text"]})
        unused = [f"fix {x[0]} ({x[1]})" for n_, x in enumerate(SIX) if (k == "copy" or not x[1].startswith("README")) and not used[(x[0], n_)]]
        n_changed = sum(1 for c_ in extra["six_changes"] if c_["build"] == CALLED[k])
        check(f"f1 ({k})", f"against {CALLED[k]} as it was kept before the owner's six lines of 11 October 2026 (his third handoff): no string was dropped, and none was added but the four the Guide button and the loader put on the page "
              "on 13 October 2026, each written out in this check (the button's label and its hover text, and the loader's two messages), all four of which are there; every string that differs is one of the six lines and differs "
              "by exactly his replacement, written out in this check, and by nothing else; no place of a fix still holds its old words; and every fix is found in the build. The build's own date and, in the copy's README, its "
              "section on this copy's files are left out. The guide's own words are not among these strings: group g holds them", not added and not dropped and not stray and not back and not unused,
              f"{n_changed} strings differ, all of them his: " + "; ".join(f"fix {f_}: {sum(1 for c_ in extra['six_changes'] if c_['build'] == CALLED[k] and c_['fix'] == f_)}" for f_ in range(1, 7))
              if not (added or dropped or stray or back or unused) else "ADDED: " + "; ".join(added[:3]) + " | DROPPED: " + "; ".join(dropped[:3]) + " | DIFFERS OTHERWISE: " + "; ".join(stray[:4]) + " | OLD WORDS STILL THERE: "
              + "; ".join(back[:4]) + " | FIX NOT FOUND: " + "; ".join(unused[:4]))
        d6 = []
        differ(kept["D"], now[k]["D"], "", d6)
        other6 = [(p_, how) for p_, how in d6 if not any(re.fullmatch(x, p_) for x in SIX_PARTS) and (p_, how) != (".guide_html", "added")]
        was_page, not_put_back = page_before_13_oct(now[k]["page"])
        same_page = not not_put_back and was_page == kept["page"]
        check(f"f2 ({k})", f"against the same kept build, no part of the data.js of {CALLED[k]} differs - no row of a unit, class, count, colour, shape or figure array, and no other text - but the parts the six lines are in (the About "
              "and Sources texts, three cells' definitions, the four East Coast badges, the prompt, the head of the grid's first column, four 'i'), the build time, and the key `guide_html`, added on 13 October 2026 (check g0); "
              f"and index.html is the kept one but for the {len(PAGE_13_OCT)} places where the Guide button and the loader changed it that day, each written out in this check and each found exactly once: with every one put back "
              "as it was, the page is byte for byte the kept one",
              not other6 and same_page, f"{len(d6)} parts differ, all of them the six lines', the build time or the guide; index.html, with its {len(PAGE_13_OCT)} places put back, the same" if not other6 and same_page
              else "NOT THE SIX LINES': " + "; ".join(f"{p_} ({how})" for p_, how in other6[:6]) + ("" if same_page else " | index.html differs otherwise: " + ("; ".join(not_put_back[:3]) or "after its places were put back it is not the kept page")))

    # g. the guide and the loader (the owner's handoff of 13 October 2026)
    G = extra["guide"]
    md, lists = G["md"], PHRASES + PHRASES_OF_THE_SIX + PHRASES_COPY_ONLY
    htmls = {k: now[k]["D"].get("guide_html") for k in ("layer", "copy")}
    rec, on_disk = G["layer_record"] or {}, G["on_disk"]
    rec_ok = bool(rec) and rec.get("source", {}).get("sha256") == on_disk[GUIDE_MD] and not rec.get("pictures_left_out_of_this_build") and len(rec.get("pictures", [])) == GUIDE_PICTURES \
        and all(q["sha256"] == on_disk.get(q["path"]) for q in rec.get("pictures", []))
    check("g0", f"the guide in the data: in both builds `guide_html` is docs/GUIDE.md as scripts/_guide.py turns it into HTML now, character for character, with its {GUIDE_PICTURES} pictures inside it; the copy's is the full layer's; "
          "and the layer's run record gives the sha256 of the guide and of each picture as they are on disk, and says no picture was left out of the build",
          all(isinstance(h, str) and h == G["again"] for h in htmls.values()) and htmls["layer"] == htmls["copy"] and not G["would_stop_the_build"] and rec_ok,
          f"{len(G['again']):,} characters; the layer's record: guide {rec.get('source', {}).get('sha256', '')[:16]}..., {len(rec.get('pictures', []))} pictures" if rec_ok and all(h == G["again"] for h in htmls.values())
          else "NOT SO: " + "; ".join([f"{CALLED[k]}'s guide_html is not the guide as converted now" for k, h in htmls.items() if h != G["again"]] + ([] if rec_ok else ["the layer's run record is not of the guide and the pictures on disk"])
                                      + G["would_stop_the_build"][:2]))
    bad = [f"{CALLED[k]}: {w}" for k, h in htmls.items() for w in guide_html_wrong(h or "", md, G["pictures"])]
    check("g1", f"the guide's HTML held to docs/GUIDE.md without the converter, in both builds: with the marks of Markdown taken out of the one and the tags out of the other, the two read the same, character for character but for "
          "spacing; the HTML has no tag and no attribute but the few the converter writes, and no script; its links are the guide's own, in order, each an https address opened in a new tab; nothing else in it carries an address; "
          f"and it holds the {GUIDE_PICTURES} pictures the guide names, in the guide's order, each as the bytes of its file under docs/guide/, with the guide's words for it, at 1280 x 800",
          not bad, f"{len(words_of_markdown(md)):,} characters of words; {len(re.findall(r'<a ', htmls['copy'] or ''))} links; {len(re.findall(r'<img', htmls['copy'] or ''))} pictures" if not bad else "WRONG: " + " | ".join(bad[:4]))
    bad = [f"{CALLED[k]}: {w}" for k in ("layer", "copy") for w in loader_and_button_wrong(now[k]["page"], lists)]
    check("g2", "the Guide button and the loader, in the index.html of both builds, read as text: the button stands once, right after About this map and Sources, with the owner's label and hover text; the button and #open=guide "
          "both open `guide_html` in the window the other two texts use; 'Loading the map...' is plain markup in the map's area, before the tag that asks for data.js; 'Drawing the units...' is set once the data is in, after the "
          "message for data that did not load, and the browser is given a frame to paint it before the map is drawn; the loader is put away in the line before the page says it is ready; its bar only moves, and nothing "
          "sets its width; and its two messages have no figure, no '?' or ';', at most six words, and no phrase of the lists. (What a browser then does is scripts/exercise_layer.py's to show.)",
          not bad, f"'{LOADING}' and '{DRAWING}', in both builds" if not bad else "WRONG: " + " | ".join(bad[:4]))
    g_blocks = blocks(htmls["copy"] or "")
    hits = [f"'{ph}' in block {n_ + 1}" for n_, t in enumerate(g_blocks) for ph in lists if has_phrase(ph, unquoted(t, quoted))]
    whole_guide = norm(" \n ".join(g_blocks))
    hits += [f"a finding of the audit marked fixed: '{a['said'][:60]}'" for a in extra["audit"] if a["done"].startswith("fixed") and a["said"].strip() and norm(a["said"]) in whole_guide]
    hits += [f"block {n_ + 1} opens 'This shows'" for n_, t in enumerate(g_blocks) if norm(t).startswith("this shows")]
    index_title = next((l["title"] for l in now["layer"]["D"]["layers"] if l["id"] == "adi_2011"), None)
    hits += [f"the development index is named: '{w}'" for w in ("adi_2011", index_title) if w and w in (htmls["copy"] or "")] + (["the words 'development index'"] if re.search("development index", htmls["copy"] or "", re.I) else [])
    check("g3", "the guide's words, as both builds carry them: none of the phrases the deck lists, none of the eight the owner added with his six lines, and not 'is not beside this page'; no finding of the audit that is marked fixed; "
          "no block that opens 'This shows'; and the development index is named nowhere in it - not by the words in any case, not by its key, not by the name of its layer",
          not hits and len(g_blocks) > 100, f"{len(lists)} phrases and {sum(1 for a in extra['audit'] if a['done'].startswith('fixed'))} fixed findings looked for in {len(g_blocks)} blocks of the guide" if not hits else "FOUND: " + "; ".join(hits[:6]))
    rows_, bad = trace_guide_figures(md, G["x"])
    extra["guide_rows"] = rows_
    n_found, n_derived, n_runs = (sum(1 for r in rows_ if r["how"].startswith(w)) for w in ("found", "comes from", "a count"))
    check("g4", "every figure of docs/GUIDE.md is traced. The guide is cut into sentences and table cells; for each one that holds a figure, all its figures must stand together, each written the same way, in one passage of one "
          "of the named files (the page's own strings in data.js, docs/GAP.md, docs/DECISION_LAYER.md, README.md, the records of the runner, of the copy's check and of the pictures looked at, and the provider's "
          "cautions), and that passage must share a word with the sentence; for a cell that is only a figure it must hold another cell of the same row, and for a row about one file it must name the file. Allowed, and "
          "nothing else: thousands separators, a space before %, the minus sign, and x for the multiplication sign. A figure that stands in no named file as the guide writes it must be one of the cases listed in this check, "
          "each worked out again from the file's own figure; a sentence whose figures stand in two passages must be listed too. A picture's file name and the address a link points to are not figures; a file's or a "
          "command's name with a digit in it must stand whole in a named file. The counts of this build's own runs are held by g5 and g7. (What this does not show: that the passage says what the sentence says. A lone small "
          "figure can stand, beside a shared word, in a passage about something else; every trace is in 60_layer/site_copy_guide_figures.csv to be read.)",
          not bad and n_found > 100, f"{len(guide_units(md))} sentences and cells with a figure: {n_found} found in one passage, {n_derived} that come from a figure of a named file by a listed rule, {n_runs} counts of this build's own runs; "
          f"{len(GUIDE_SPLIT)} sentences listed as standing in two passages" if not bad else "NOT TRACED: " + " | ".join(bad[:5]) + (f" ... {len(bad)} in all" if len(bad) > 5 else ""))
    bad = guide_counts_wrong(md, G["x"])
    check("g5", "the guide's own counts: in its table 'How it was checked', the result of each row that is a count of this build's own runs is the result on record - verify_layer.py and verify_decision.py as the runner's record "
          "ends them; the layer's exercise in Chrome and in WebKit, the same count in both; the decision view's exercise, each browser's own count of steps, and the same lines and cells in both; and the copy's check, its "
          "steps and no request to the network. Each is 'N of N'. (The count of this check's own checks is held at the end of the run, by g7.)",
          not bad, "; ".join(f"{k}: {v}" for k, v in guide_table_of_checks(md).items() if k in GUIDE_PINNED_ROWS)[:330] if not bad else "NOT AS ON RECORD: " + " | ".join(bad[:4]))
    bad = records_wrong(G["x"], G["now_sha"], G["layer_run"], G["copy_run"])
    check("g6", "the records the guide's counts, megabytes and window size are read from are of the builds on disk: the runner's is of a finished pass on this layer in which every check passed on its last run; the copy's check "
          "is of this copy, and every step did what it should; the record of the pictures looked at is of these two builds; and none of the named files is missing",
          not bad, "60_layer/decision_runs.json, 70_share/exercise_share_chrome.json and 60_layer/site_copy_looked_at.json are of the builds on disk" if not bad else "NOT SO: " + " | ".join(bad[:4]))

    # e. the checks' own changes
    vl = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", VERIFY_LAYER_AT, "--", "scripts/verify_layer.py"], capture_output=True).returncode
    check("e1", f"scripts/verify_layer.py is byte for byte the file of commit {VERIFY_LAYER_AT}, to which the stage-4 checks hold it", vl == 0, "unchanged" if vl == 0 else "IT DIFFERS, or git could not say")
    uncovered, unreal, n_blocks, per_file = [], [], 0, {}
    table = extra["changes"]
    used = set()
    for path in CHECK_FILES + list(OUTSIDE_GIT) + [THIS_SCRIPT]:
        old = (ROOT / OUTSIDE_GIT[path]).read_text(encoding="utf-8") if path in OUTSIDE_GIT else git_show(BEFORE_THE_GUIDE if path == THIS_SCRIPT else CHECKS_BEFORE, path)
        if old is None:
            uncovered.append(f"{path}: git has no such file at {BEFORE_THE_GUIDE if path == THIS_SCRIPT else CHECKS_BEFORE}")
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
          f"the block as it is), and every row of that table is such a change. Since 13 October 2026 this script's own changes are tabled there too, against commit {BEFORE_THE_GUIDE}, the last before the Guide button: the "
          "checks that handoff added, and the three it had to widen, can be read off the table", not uncovered and not unreal and n_blocks > 0,
          f"{n_blocks} blocks in {sum(1 for v in per_file.values() if v)} files, {len(table)} rows; files with no change: {', '.join(p.split('/')[-1] for p, v in per_file.items() if not v) or 'none'}" if not uncovered and not unreal
          else "NO ROW FOR: " + " | ".join(uncovered[:4]) + " || NOT A CHANGE IN THE FILE: " + " | ".join(unreal[:4]))
    return results, pairs, S


# The six lines: (the fix, the places it is in - a pattern on `where` -, the words as they were, the words as they are). A compiled pattern stands where plain words would not find the one place.
SIX = [
    (1, r"decision\.corro_labels\[\d+\]", " - East Coast zone: CoRE Stack's own check fails here, so corroboration is unreliable", " - East Coast zone: our placebo test fails here, so corroboration is unreliable"),
    (1, r"tips\.layer:agreement", "because CoRE Stack's own check fails there (see About this map)", "because our placebo test fails there, though on few districts (see About this map)"),
    (1, r"tips\.panel:4", "The headline leaves out units wholly under CoRE Stack's East Coast zone model: CoRE Stack's Improvement class is its own check (clearing shouldn't go with improvement), and in that zone it fails, which is "
                          "what \"the placebo test fails\" in the zone line means.",
     "The headline leaves out units wholly under CoRE Stack's East Coast zone model. Our placebo test uses CoRE Stack's Improvement class as a check on its Degradation class (clearing shouldn't go with improvement); in that zone it fails, "
     "though on few districts. That is what \"the placebo test fails\" in the zone line means."),
    (1, r"about_html, block \d+", "The first is the headline because CoRE Stack's Improvement class is the check on its Degradation class: clearance should not go with improvement.",
     "The first is the headline because we use CoRE Stack's Improvement class as a check on its Degradation class, our placebo test: clearance should not go with improvement."),
    (2, r"tips\.layer:hansen_loss", "Hansen picks up clearing of fairly closed canopy. It can't see thinning under a canopy that's still standing, or change on land that was already open in 2000.",
     "This layer counts loss only where canopy was above 30 % in 2000; the next layer shows it on more open land. Hansen records clearing, tree canopy removed outright: it can't see thinning under a canopy that's still standing."),
    (2, r"about_html, block \d+", "Hansen tree cover loss dates the outright removal of canopy that was fairly closed in 2000. It's validated, and it's a floor: it can't see thinning, or change on land that was already open in 2000.",
     "Hansen tree cover loss dates the outright removal of tree canopy, year by year. It's validated, and it's a floor: it can't see thinning under a canopy that still stands."),
    (3, r"decision\.t\.grid_cols\[0\]", re.compile(r"^No forest loss in the window$"), "Little or no forest loss in the window"),
    (3, r"decision\.cells\[\w+\]\.def", "Forest loss in the window is none: under", "Forest loss in the window is little or none: under"),
    (3, r"about_html, block \d+", re.compile(r"(?<=mostly dense|.mostly open|ttle or none) none(?= [\d,]+ [\d,]+$)"), " little or none"),         # a row of the About text's table of cells: its column of loss, before the two counts that end it
    (4, r"decision\.governance", "No revenue village \u2014 this land is in no village plan. Whose plan covers it?", "Outside every revenue village. Whose plan covers this land?"),
    (4, r"about_html, block \d+", "No village plan covers them, their panel asks whose plan does, and it says what their assigned district rests on.",
     "They lie outside every revenue village, so their panel asks whose plan covers them, and says what their assigned district rests on."),
    (5, r"sources_html, row \d+, cell 2", "through Google Earth Engine; state totals reconciled to Global Forest Watch's published figures",
     "through Google Earth Engine; the state's canopy of 2000 and its loss for 2001-2020 reconciled to Global Forest Watch's published figures, which stop at 2020"),
    (5, r"README\.txt: CREDITS AND LICENCES", "through Google Earth Engine; state totals reconciled to Global Forest Watch's published figures",
     "through Google Earth Engine; the state's canopy of 2000 and its loss for 2001-2020 reconciled to Global Forest Watch's published figures, which stop at 2020"),
    (6, r"tips\.panel:3", "CoRE Stack's own dashboard takes Deforestation and Afforestation from its land-use maps instead, so its figures for those two will differ.",
     "CoRE Stack's published block rasters take Deforestation and Afforestation from its land-use maps instead, so their figures for those two will differ."),
]
SIX_PARTS = [r"\.about_html", r"\.sources_html", r"\.built", r"\.decision\.built", r"\.decision\.cells\[\d+\]\.def", r"\.decision\.corro_labels\[\d+\]", r"\.decision\.governance", r"\.decision\.t\.grid_cols\[0\]",
             r"\.tips\.layer:agreement", r"\.tips\.layer:hansen_loss", r"\.tips\.panel:3", r"\.tips\.panel:4"]          # the parts of data.js the six lines are in, and the two build times
NIRV_ITEM = "the deck's item on NIRv, in place of 'is pending and will be a reported column only': the years of the test (2013-2025) and the date of the decision (7 October 2026)"
HANSEN_BULLET = ("the owner's bullet on Hansen of 11 October 2026 (his third handoff) no longer names the year 2000: it said 'canopy that was fairly closed in 2000' and 'land that was already open in 2000', and says what Hansen "
                 "cannot see without them")
ABOUT_FIGURES = {"layer": {((), ("2013", "2025", "7", "2026")): NIRV_ITEM, (("2000", "2000"), ()): HANSEN_BULLET},
                 "copy": {((), ("2013", "2025", "7", "2026")): NIRV_ITEM, (("2000", "2000"), ()): HANSEN_BULLET,
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
            if b and not a and (b["where"], b["text"]) in ADDED_13_OCT:
                note = ADDED_NOTE
            if b and b["exempt"]:
                note = (note + "; " if note else "") + "outside the deck's list of phrases: " + b["exempt"]
            out.append({"build": CALLED[k], "part": r["part"], "where": r["where"], "kind": r["kind"], "before": a["text"] if a else "", "after": b["text"] if b else "", "status": status, "note": note})
    for f in figures_listed:
        out.append({"build": f["build"], "part": "figures", "where": f["place"], "kind": "a figure that is not where it was", "before": f"{f['figure']}: {f['times_before']} time(s)", "after": f"{f['figure']}: {f['times_after']} time(s)",
                    "status": "listed", "note": f["why"]})
    return out


def gather_guide(now, builds):
    """What group g needs: the guide and its pictures as they are on disk, the guide converted again, the layer's record of it, and the passages of the named files."""
    import _guide
    md = read(ROOT / GUIDE_MD).read_text(encoding="utf-8")
    named = [a for _, a in re.findall(r"(?m)^!\[([^\]]*)\]\(([^)\s]+)\)$", md)]
    stops = []
    again = _guide.build(ROOT, None, stops, pictures=True)
    read(ROOT / "scripts/_guide.py")
    pictures = {a: sha(read(ROOT / "docs" / a)) for a in named if (ROOT / "docs" / a).is_file()}
    return {"md": md, "again": again["html"], "would_stop_the_build": stops, "pictures": pictures, "on_disk": {GUIDE_MD: sha(ROOT / GUIDE_MD), **{"docs/" + a: v for a, v in pictures.items()}},
            "layer_record": json.loads((ROOT / "60_layer/layer.provenance.json").read_text(encoding="utf-8")).get("guide"), "x": guide_sources(now["copy"], read),
            "now_sha": builds["files_sha256"], "layer_run": builds["layer_run_utc"], "copy_run": builds["copy_run_utc"]}


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
    extra["six_wrong"], extra["six_files"] = [], 0
    for k, lst in BEFORE_SIX_LISTS.items():
        base = read(lst).parent
        want = {line.split(None, 1)[1].strip().lstrip("./"): line.split()[0] for line in lst.read_text().splitlines() if line.strip()}
        for name in (("data.js", "index.html", "layer_by_unit.csv") if k == "layer" else (f"{NAME}/data.js", f"{NAME}/index.html", f"{NAME}/README.txt")):
            extra["six_files"] += 1
            if name not in want or sha(base / name) != want[name]:
                extra["six_wrong"].append(f"{rel(base / name)} is not the file that was kept")
    extra["six"] = {k: load(BEFORE_SIX[k]) for k in BEFORE_SIX}
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


def planted(before, now, extra):
    """The errors to plant: (what, the build it is planted on, a function giving (the builds with the error in, a folder to open in a browser or None[, a copy of the guide's text with the error in]),
    the checks meant to catch it)."""
    L, C = now["layer"]["D"], now["copy"]["D"]
    guide_md = extra["guide"]["md"]

    def guide(old, new, nowhere=None):
        """An error planted on a copy of the guide's text, held in memory: docs/GUIDE.md is not touched."""
        if guide_md.count(old) != 1:
            raise SystemExit(f"a planted error could not be planted: the guide has '{old[:50]}' {guide_md.count(old)} times")
        if nowhere is not None and any(nowhere in p_["figures"] for ps in extra["guide"]["x"]["passages"].values() for p_ in ps):
            raise SystemExit(f"a planted error could not be planted: the figure {nowhere} does stand in a named file")
        return now, None, guide_md.replace(old, new)

    def page_text(k, old, new):
        """An error planted on a copy of a build's index.html held in memory, for the checks that read the page as text: nothing is opened in a browser."""
        if now[k]["page"].count(old) != 1:
            raise SystemExit(f"a planted error could not be planted: the page of {k} has '{old[:50]}' {now[k]['page'].count(old)} times")
        b = dict(now[k])
        b["page"] = now[k]["page"].replace(old, new)
        return {**now, k: b}, None

    def a_picture_for_another():
        pics = re.findall(r"data:image/webp;base64,[A-Za-z0-9+/=]+", C["guide_html"])
        if len(pics) < 2 or pics[0] == pics[1]:
            raise SystemExit("a planted error could not be planted: the guide in the copy does not hold two different pictures")
        return copy_(guide_html=C["guide_html"].replace(pics[0], pics[1], 1))

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
        ("23. an old line back: 'CoRE Stack's own check' in an East Coast badge", "the full layer's data",
         lambda: layer(decision={**L["decision"], "corro_labels": [x.replace("our placebo test fails here", "CoRE Stack's own check fails here") if n_ == 4 else x for n_, x in enumerate(L["decision"]["corro_labels"])]}), ["b1 (layer)", "f1 (layer)"]),
        ("24. an old line back: 'already open in 2000' in the Hansen layer's 'i'", "the copy's data",
         lambda: copy_(tips={**C["tips"], "layer:hansen_loss": "Hansen picks up clearing of fairly closed canopy. It can't see thinning under a canopy that's still standing, or change on land that was already open in 2000."}), ["b1 (copy)", "f1 (copy)"]),
        ("25. an old line back: 'No forest loss in the window' at the head of the grid's first column", "the full layer's data",
         lambda: layer(decision=t_of(L, grid_cols=["No forest loss in the window", L["decision"]["t"]["grid_cols"][1]])), ["b1 (layer)", "f1 (layer)"]),
        ("26. an old line back: 'no village plan' in the prompt of an outside-village unit", "the copy's data",
         lambda: copy_(decision={**C["decision"], "governance": "No revenue village \u2014 this land is in no village plan. Whose plan covers it?"}), ["b1 (copy)", "f1 (copy)"]),
        ("27. a seventh line: one word changed in a string the owner did not reword (the line under a ranked list for the units outside it)", "the full layer's data",
         lambda: layer(decision=t_of(L, rank_unranked=L["decision"]["t"]["rank_unranked"].replace("on the map but outside the list", "on the map and outside the list"))), ["f1 (layer)", "f2 (layer)"]),
        ("28. a figure of the guide changed: 59 % to 95 %, in 'hold 59 % of its forest' (95 % does stand in the named files, as the level of an interval: a search for the figure alone would have passed it)", "a copy of the guide",
         lambda: guide("but hold 59 % of its forest", "but hold 95 % of its forest"), ["g4"]),
        ("29. a figure found nowhere: a sentence added to the guide, 'The first build took 73,519 seconds.'", "a copy of the guide",
         lambda: guide("not a verdict on any place.\n\n## What the map is for", "not a verdict on any place. The first build took 73,519 seconds.\n\n## What the map is for", nowhere="73519"), ["g4"]),
        ("30. a phrase of the deck's list in the guide ('the project owner')", "the copy's data",
         lambda: copy_(guide_html=C["guide_html"].replace("so which rows bear on a cell is this project's proposal", "so which rows bear on a cell is the project owner's proposal", 1)), ["g3"]),
        ("31. a count of the guide's own table of checks raised by one: verify_decision.py's", "a copy of the guide",
         lambda: guide(guide_table_of_checks(guide_md)["verify_decision.py"], re.sub(r"\d+ of \d+", lambda m: "{0} of {0}".format(int(m.group(0).split()[0]) + 1), guide_table_of_checks(guide_md)["verify_decision.py"], count=1)), ["g5"]),
        ("32. one picture of the guide carried twice, in place of another", "the copy's data", a_picture_for_another, ["g1"]),
        ("33. a line of index.html changed that the Guide button and the loader did not add (the first line of the district list)", "a copy of the full layer's index.html, as text",
         lambda: page_text("layer", "Jump to a district&hellip;", "Go to a district&hellip;"), ["f2 (layer)"]),
        ("34. the loader's first message with a figure in it ('Loading 23 MB...')", "a copy of the copy's index.html, as text", lambda: page_text("copy", "Loading the map&hellip;", "Loading 23 MB&hellip;"), ["g2"]),
        ("35. a figure of the guide that comes from another by a listed rule, changed: 72.07 crore to 72.70 crore", "a copy of the guide", lambda: guide("\u20b972.07 crore", "\u20b972.70 crore"), ["g4"]),
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
    extra["guide"] = gather_guide(now, builds)
    browser = {k: in_a_browser_with_runs(NOW[k], now[k]["D"]) for k in NOW}
    results, pairs, S = run_checks(before, now, extra, browser)
    ok = all(r["pass"] for r in results)

    if a.trials:
        failed0 = [r["id"] for r in results if not r["pass"]]
        trials = []
        for what, on, make, meant in planted(before, now, extra):
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
                made = make()
                builds_, folder = made[0], made[1]
                if len(made) > 2:                                # a copy of the guide's text with the error in
                    ex["guide"] = {**extra["guide"], "md": made[2]}
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
        the_four = [t_ for t_ in T.get("trials", []) if t_["planted"].split(".")[0] in ("23", "24", "25", "26")]      # the four the owner named with his six lines: each puts an old line back
        the_two = [t_ for t_ in T.get("trials", []) if t_["planted"].split(".")[0] in ("28", "29")]                    # the two he named with the guide: a changed figure, and a figure found nowhere
        t_ok = T.get("script_sha256") == me["script_sha256"] and T.get("builds") == builds and T.get("planted", 0) >= 8 and T.get("every_planted_error_caught") is True and T["the_builds_as_they_are"]["failed"] == [] \
            and len(the_four) == 4 and all(t_["caught"] for t_ in the_four) and len(the_two) == 2 and all(t_["caught"] and "g4" in t_["checks_that_failed"] for t_ in the_two)
        detail = f"{T.get('caught')} of {T.get('planted')} caught, run {T.get('run_utc')}" + ("" if t_ok else "; NOT of this script as it is, or not of these builds, or an error was not caught")
    else:
        t_ok, detail = False, "there is no record of the trials: run this script with --trials first"
    results.append({"id": "t1", "check": f"the planted errors: the record of the trials (60_layer/{TRIALS}) is of this script as it is and of the builds on disk, the builds as they are passed every check in it, at least eight errors were "
                                         "planted - the eight the owner named among them, the four he named with his six lines, each of which puts an old line back, and the two he named with the guide, a changed figure and a figure found "
                                         "nowhere, each caught by the gate on the guide's figures - and every one was caught by a check meant to catch it", "pass": t_ok, "detail": detail})
    said = guide_table_of_checks(extra["guide"]["md"]).get("check_site_copy.py", "")
    made_now = len(results) + 1                                  # this check is the last one made
    results.append({"id": "g7", "check": "the guide's count for this check itself: in its table 'How it was checked' the row of check_site_copy.py gives 'N of N checks', and N is the number of checks this run makes, this one counted "
                                         "(whether all N pass is the run's own result)", "pass": counts_of(said)[:1] == [(made_now, made_now)], "detail": f"the guide says '{said}'; this run makes {made_now} checks"})
    table = strings_table(pairs, extra.get("figures_listed", []))
    for k in ("layer", "copy"):                                  # the guide's words, block by block: new on 13 October 2026, and the same in both builds
        table += [{"build": CALLED[k], "part": "Guide", "where": f"guide_html, block {n_ + 1}", "kind": "text", "before": "", "after": t_, "status": "new", "note": "the guide, docs/GUIDE.md: " + ADDED_NOTE}
                  for n_, t_ in enumerate(blocks(now[k]["D"].get("guide_html") or ""))]
    out.mkdir(parents=True, exist_ok=True)
    cols = ["build", "part", "where", "kind", "before", "after", "status", "note"]
    with open(out / "site_copy_strings.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(table)
    g_cols = ["line", "section", "the_guides_words", "its_figures", "how", "file", "passage", "words_shared_with_the_passage", "figures_beside_the_same_word"]
    with open(out / "site_copy_guide_figures.csv", "w", newline="", encoding="utf-8") as fh:      # every figure of the guide, with where it stands
        w = csv.DictWriter(fh, fieldnames=g_cols)
        w.writeheader()
        w.writerows({c_: r_.get(c_, "") for c_ in g_cols} for r_ in extra.get("guide_rows", []))
    n_by = Counter((r["build"], r["status"]) for r in table)
    for r in results:
        print(("PASS  " if r["pass"] else "FAIL  ") + f"{r['id']:<16}{r['check'][:150]}" + (f"   [{r['detail'][:260]}]" if r["detail"] else ""), flush=True)
    ok = all(r["pass"] for r in results)
    json.dump({**me, "run_utc": started, "ended_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "builds": builds, "inputs": INPUTS,
               "the_saved_copies": {k: rel(SAVED[k]) for k in SAVED}, "checks_were_changed_since_commit": CHECKS_BEFORE,
               "checks": results, "checks_passed": sum(r["pass"] for r in results), "checks_made": len(results), "passed": ok,
               "in_a_browser": browser,
               "the_six_lines": {"kept_before_them": {k: rel(BEFORE_SIX[k]) for k in BEFORE_SIX}, "strings_that_differ_from_the_kept_builds": extra.get("six_changes", [])},
               "the_guide": {"source": GUIDE_MD, "sha256": extra["guide"]["on_disk"][GUIDE_MD], "pictures_sha256": {k_: v_ for k_, v_ in extra["guide"]["on_disk"].items() if k_ != GUIDE_MD},
                             "strings_added_to_the_page_itself": [{"where": w_, "string": t_} for w_, t_ in ADDED_13_OCT], "places_of_index_html_changed": len(PAGE_13_OCT),
                             "files_its_figures_are_traced_to": [f_ for f_ in GUIDE_FILES if f_ not in NOT_SEARCHED] + [UMD_PAGE],
                             "figures_table": {"path": "60_layer/site_copy_guide_figures.csv", "rows": len(extra.get("guide_rows", [])), "columns": g_cols,
                                               "by_how": dict(Counter(r_["how"].split(":")[0] for r_ in extra.get("guide_rows", [])))},
                             "figures_that_come_from_a_figure_of_a_named_file": [{"the_guides_words": r_["the_guides_words"], "figure": r_["its_figures"], "how": r_["how"], "from": r_["passage"]}
                                                                                 for r_ in extra.get("guide_rows", []) if r_["how"].startswith("comes from")],
                             "sentences_whose_figures_stand_in_two_passages": [{"sentence_begins": a_, "figures_in_a_passage_of_their_own": b_, "that_passage_holds": c_} for a_, b_, c_ in GUIDE_SPLIT],
                             "sentences_whose_passage_is_named": [{"sentence_begins": a_, "the_passage_holds": b_} for a_, b_ in GUIDE_PIN]},
               "strings_table": {"path": "60_layer/site_copy_strings.csv", "rows": len(table), "columns": cols, "rows_with_no_text_before": sum(1 for r in table if not r["before"]), "rows_with_no_text_after": sum(1 for r in table if not r["after"]),
                                 "by_build_and_status": {f"{b}: {s}": n for (b, s), n in sorted(n_by.items())}}},
              open(out / "site_copy_check.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{sum(r['pass'] for r in results)} of {len(results)} checks passed; strings table: n = {len(table):,} rows ({sum(1 for r in table if not r['before']):,} with no text before, {sum(1 for r in table if not r['after']):,} with none after)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
