#!/usr/bin/env python3
"""Writes docs/SITE_COPY.md: what was untrue on the map page and what it says now, every string before and after, every
check whose words changed, the runs, and what was seen in the screenshots - the account of the owner's handoff of
11 October 2026, "The site in plain words, with every untrue line fixed".

    .venv/bin/python scripts/write_site_copy.py

It types no figure. Every count, time, hash and sentence of the page in the document is read from one of the files
below; the words typed in this script pass through typed(), which stops the run if they carry a digit outside a code
span, a date, a step or section number of the handoff, or a file's name. It reads, and stops unless each is there and
is of the builds on disk:
    60_layer/site_copy_audit.csv            the findings: the owner's table and the blind reader's, each with its fix
    60_layer/site_copy_strings.csv          every visible string and "i" of both builds, before and after
    60_layer/site_copy_check_changes.csv    every changed block of a check, with what it checks
    60_layer/site_copy_check.json           scripts/check_site_copy.py: its checks, and what it saw in a browser
    60_layer/site_copy_trials.json          the errors planted against that check
    60_layer/site_copy_looked_at.json       the screenshots: what was measured and what was seen
    60_layer/decision_runs.json             scripts/run_decision_checks.py: every run of the layer's checks
    70_share/exercise_share_chrome.json     scripts/exercise_share.py: the gate on the copy
    60_layer/layer.provenance.json, 70_share/share.provenance.json      the two builds
    README.md, docs/DEGRADATION.md, docs/LAYER.md                       for one hold: the two findings that were in documents
The run stops if a check did not pass, a planted error was not caught, a record is of another build, the check of the
words is not the committed file, a finding is still marked as to do, or a finding marked as fixed in a document still
stands in it.

Output: docs/SITE_COPY.md and nothing else; its inputs, their sha256 and the UTC time of the run are at its end.
"""
import csv
import hashlib
import json
import re
import subprocess
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "SITE_COPY.md"
INPUTS = []
ALLOWED = [r"`[^`]*`", r"\b\d{1,2} October 2026\b", r"\bSteps? \d\b", r"\bsection \d+\b", r"\brow \d+\b"]       # where the typed words may carry a digit: none of them is a measurement


def stop(m):
    raise SystemExit("SITE_COPY not written: " + m)


def typed(s):
    """Words typed in this script. The run stops if they carry a digit of their own."""
    bare = s
    for a in ALLOWED:
        bare = re.sub(a, "", bare)
    bare = re.sub(r"\{[^{}]*\}", "", bare)                    # a place a value read from a file goes into
    if re.search(r"\d", bare):
        stop("the typed words carry a digit of their own: " + repr(re.findall(r"[^.\n]*\d[^.\n]*", bare)[0][:120]))
    return s


def use(path):
    p = ROOT / path
    if not p.is_file():
        stop(f"{path} is not there")
    if not any(i["path"] == path for i in INPUTS):
        INPUTS.append({"path": path, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return p


def J(path):
    return json.loads(use(path).read_text(encoding="utf-8"))


def C(path):
    with open(use(path), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def mask(s):
    """The records of the browser checks carry the address the page was opened at, a path of the machine they ran on: the document names it from the repository."""
    return re.sub(r"(?<=file://)/[^\s|'\"]*?(?=/(?:60_layer|70_share)/)", "<repository>", str(s).replace(str(ROOT), "<repository>"))


def cellmd(s, cut=None):
    """A text as one cell of a table: no line break, no bar; cut to a length where one is given, and said to be cut."""
    s = " ".join(mask(s).split()).replace("|", "\\|")
    if cut and len(s) > cut:
        s = s[:cut].rstrip() + " [...]"
    return s or " "


def table(heads, rows):
    return "\n".join(["| " + " | ".join(typed(h) for h in heads) + " |", "|" + "---|" * len(heads)] + ["| " + " | ".join(r) + " |" for r in rows]) + "\n"


def main():
    written = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    audit, strings, changes = C("60_layer/site_copy_audit.csv"), C("60_layer/site_copy_strings.csv"), C("60_layer/site_copy_check_changes.csv")
    chk, tri, seen = J("60_layer/site_copy_check.json"), J("60_layer/site_copy_trials.json"), J("60_layer/site_copy_looked_at.json")
    runs, share = J("60_layer/decision_runs.json"), J("70_share/exercise_share_chrome.json")
    L, S = J("60_layer/layer.provenance.json"), J("70_share/share.provenance.json")
    sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
    now = {"layer_run_utc": L["run_utc"], "copy_run_utc": S["run_utc"]}

    # ---- what must hold before a word is written -------------------------------------------------------------------------------------------
    if not (chk["passed"] is True and chk["checks_passed"] == chk["checks_made"]):
        stop("scripts/check_site_copy.py did not pass: " + "; ".join(c["id"] for c in chk["checks"] if not c["pass"]))
    if any(chk["builds"][k] != v for k, v in now.items()) or any(sha(p) != h for p, h in chk["builds"]["files_sha256"].items()):
        stop("60_layer/site_copy_check.json is of other builds than the ones on disk: run scripts/check_site_copy.py again")
    if not (tri["every_planted_error_caught"] is True and tri["builds"] == chk["builds"] and tri["script_sha256"] == chk["script_sha256"]):
        stop("the record of the planted errors is not of this check and these builds, or an error was not caught")
    if chk["script_sha256"] != sha(chk["script"]) or subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", chk["script"], share["script"]], capture_output=True, text=True).stdout.strip():
        stop("the check of the words, or the gate on the copy, is not the committed file, or the check's record is of another version of it")
    if not (runs.get("every_check_passed_on_its_last_run") is True and runs["layer_run_utc"] == L["run_utc"] and not runs.get("unfinished")
            and all(sha("60_layer/" + f) == h for f, h in runs["files_sha256"].items())):
        stop("60_layer/decision_runs.json is not a finished pass of the layer on disk in which every check passed on its last run")
    if any(c["file_is_as_committed"] is not True for c in runs["checks"]):
        stop("a check of the pass was run from a file that was not the committed one: " + "; ".join(c["script"] for c in runs["checks"] if c["file_is_as_committed"] is not True))
    if not (share["copy_run_utc"] == S["run_utc"] and share["layer_run_utc"] == L["run_utc"] and all(s["ok"] for s in share["steps"])
            and all(sha(i["path"]) == i["sha256"] for i in share["inputs"])):
        stop("70_share/exercise_share_chrome.json is not a pass of the copy on disk")
    if not (seen["builds"] == now and all(sha(p) == h for p, h in seen["files_sha256"].items()) and all(p["seen"].strip() for p in seen["pictures"])):
        stop("60_layer/site_copy_looked_at.json is of other builds than the ones on disk, or a picture has no note")
    todo = [a["where"] for a in audit if not a["done"].startswith(("fixed", "listed"))]
    if todo:
        stop("a finding of the audit is neither fixed nor listed for the owner: " + "; ".join(todo))
    for a in audit:
        if any(not v.strip() for v in a.values()):
            stop("a finding of the audit has an empty cell: " + a["where"])
    for doc, gone, there in IN_DOCUMENTS:                     # the findings that were in documents and not on the page
        words = " ".join(use(doc).read_text(encoding="utf-8").split())
        if gone in words or there not in words:
            stop(f"{doc} still says '{gone}', or does not say '{there}': a finding of the audit that is marked as fixed in a document is not")

    fixed = [a for a in audit if a["done"].startswith("fixed")]
    listed = [a for a in audit if a["done"].startswith("listed")]
    on_page = lambda a: a["where"].startswith(("both builds", "full layer", "published copy"))
    not_deck = [a for a in fixed if "the deck's" in a["fix"] and ("not used" in a["fix"] or "added" in a["fix"] or "softened" in a["fix"])]
    full, copy_ = "the full layer", "the published copy"
    rows_of = lambda build, parts=None, status=None: [r for r in strings if r["build"] == build and (parts is None or r["part"] in parts) and (status is None or (r["status"] in status))]
    changed = ("reworded", "new", "new: an i", "gone")
    CONTROLS = ("side panel", "decision view: controls", "overlay", "search", "page messages")
    OTHER = ("legend", "a unit's panel", "decision view: the list", "decision view: legend and why this tier", "About this map", "Sources", "README.txt")
    layer_rows = {(r["where"], r["before"], r["after"]) for r in rows_of(full)}
    only_copy = [r for r in rows_of(copy_) if r["part"] != "figures" and r["status"] in changed and (r["where"], r["before"], r["after"]) not in layer_rows]
    string_row = lambda r, cut=None: [cellmd(r["where"]), cellmd(r["kind"]), cellmd(r["before"], cut), cellmd(r["after"], cut), cellmd(r["status"] + ("; " + r["note"] if r["note"] else ""))]
    n_strings = Counter((r["build"], r["status"]) for r in strings if r["part"] != "figures")
    ch_by_file = Counter(c["file"] for c in changes)
    safari = runs.get("checks_not_run_in_this_pass", [])
    B = chk["in_a_browser"]
    t_ids = {c["id"]: c for c in chk["checks"]}

    D = []
    D.append(typed("""# The site in plain words: what was changed on 11 October 2026

*Written {written} by `scripts/write_site_copy.py`. No figure in this document was typed: each count, time, hash and
sentence of the page was read by that script from the files listed at the end, which it holds against the builds on
disk before it writes a word.*

## 1. What this is

On 11 October 2026 the owner asked for three things to be put right on the map page that his supervisor and the
Foundation for Ecological Security will open, without moving a single figure:

- **some of it was no longer true**: NIRv was shown as pending, the page called itself offline, and more (section 2);
- **it read as if a machine had written it**: long labels, a question for a switch. A label is now short, and what
  it left out stands in a small "i" beside it, which opens a bubble on hover, on keyboard focus and on a tap;
- **the published copy showed an overlay box that could not work in it.** By his ruling of that day the box is now
  greyed out in the copy and says so.

The words are his: `2026-10-11_site_copy_deck.md`, beside the handoff among the session's working files. Where a word
of his would have misstated something it was changed, and section 11 lists each such change.

This is the account of that work, for the two builds as they stand: the full layer in `60_layer/`, built
{layer_run}, and the copy made to be published, `70_share/odisha_forest_decision_layer/`, made {copy_run} from it.
Publishing the copy is the owner's step and is not part of this document; `docs/DECISION_LAYER.md` says what the site
serves.

**How it was checked, in one paragraph.** Before a word was changed both builds were copied aside with a list of
their hashes. `scripts/check_site_copy.py` holds the builds against those copies: {n_checks} checks, all passed
(section 9), among them that `60_layer/layer_by_unit.csv` is byte for byte what it was, that no part of either
`data.js` differs but the parts that hold words, and that every unit's row is what it was but for one reworded
warning. {n_trials} errors were planted on copies and each was caught (section 9). The layer's own checks were run
again in Chrome and in WebKit with their expected words brought up to date, no expected number changed
(section 8). And every "i" was opened in a browser at three window sizes and looked at (section 10).

**What one data key was added.** `data.js` gained one key at its top, `tips`, which holds the words of every "i".
Nothing else was added to the data.
""").format(written=written, layer_run=L["run_utc"], copy_run=S["run_utc"], n_checks=chk["checks_made"], n_trials=tri["planted"]))

    D.append(typed("""
## 2. What was untrue, and what the page says now

{n_fixed} findings were fixed. The first group is the owner's own table, each row confirmed against its source; the
second is what one reader found besides. That reader was given every text of both builds, the README and the
documents, and had not seen the owner's list. "Done" names the step and the commit.
""").format(n_fixed=len(fixed)))
    D.append(table(["Where", "It said", "What is true", "Source", "What it says now", "Done"], [[cellmd(a[k]) for k in ("where", "said", "true", "source", "fix", "done")] for a in fixed]))

    D.append(typed("""
## 3. Listed for the owner, with nothing changed

{n_listed} findings are listed and nothing was changed for them: a string that comes from `55_decision/` (a cell's
name or reason, a tier's reason, a work-type field, a window's description, the governance prompt), a sentence of
`docs/RESULTS.md`, or the owner's own words. `scripts/check_site_copy.py` holds that each of the page's is still on the
page as quoted here.
""").format(n_listed=len(listed)))
    D.append(table(["Where", "It says", "What is true", "Source", "Why nothing was changed"], [[cellmd(a[k]) for k in ("where", "said", "true", "source", "fix")] for a in listed]))

    D.append(typed("""
## 4. The side panel and the decision view's controls, before and after

The full layer. Every string of the side panel, the search, the decision view's controls, the overlay's box and the
page's own messages that is not what it was: {n_controls} rows. A row marked "new: an i" is the bubble beside the
label above it.
""").format(n_controls=len(rows_of(full, CONTROLS, changed))))
    D.append(table(["Where", "What it is", "Before", "After", "What happened"], [string_row(r) for r in rows_of(full, CONTROLS, changed)]))
    D.append(typed("""
**In the copy** these rows differ from the full layer's: the overlay's box, by the owner's ruling.
"""))
    D.append(table(["Where", "What it is", "Before", "After", "What happened"], [string_row(r) for r in only_copy if r["part"] in CONTROLS]))

    D.append(typed("""
## 5. Every other string that changed

The full layer, part by part; then the rows of the copy that are not the full layer's (its README among them).
"""))
    for part in OTHER:
        rs = rows_of(full, (part,), changed)
        if rs:
            D.append(typed("\n### {part}\n\n").format(part=part[0].upper() + part[1:]) + table(["Where", "What it is", "Before", "After", "What happened"], [string_row(r) for r in rs]))
    D.append(typed("\n### In the copy only\n\n") + table(["Where", "What it is", "Before", "After", "What happened"], [string_row(r) for r in only_copy if r["part"] not in CONTROLS]))

    D.append(typed("""
## 6. Figures that are not where they were

`scripts/check_site_copy.py` counts every figure and every placeholder of the old words, place by place, a label and
its "i" being one place, and holds that each stands as often in the new words. These are the differences, each
written into that check with its reason; a difference not on this list fails the check.
"""))
    D.append(table(["Build", "Place", "Before", "After", "Why"], [[cellmd(r["build"]), cellmd(r["where"]), cellmd(r["before"]), cellmd(r["after"]), cellmd(r["note"])] for r in strings if r["part"] == "figures"]))

    D.append(typed("""
## 7. Strings that did not change

The full layer: {n_same} strings are what they were. They are listed whole in `60_layer/site_copy_strings.csv`
(status "unchanged"), with the copy's {n_same_copy}; here each is given by its place and how it begins.
""").format(n_same=n_strings[(full, "unchanged")], n_same_copy=n_strings[(copy_, "unchanged")]))
    D.append(table(["Part", "Where", "How it begins"], [[cellmd(r["part"]), cellmd(r["where"]), cellmd(r["after"], LEAD)] for r in rows_of(full, None, ("unchanged",))]))

    D.append(typed("""
## 8. The checks whose words changed

A check's expected words were changed only to follow a string this task reworded, and each still checks the same
fact; no expected number, count or tolerance was changed and no check was taken out. Where a caution moved into an
"i", the check now opens that "i" and reads it. Three things were tightened and one could not follow:

- the gate on the copy lets no line of the browser's log through (it let one through: "file not found" for
  `overlay.js`, which the page no longer asks for);
- `scripts/verify_decision.py` now holds that the "i" beside the order of tiers says the order is the reader's to
  change, which was in that check's name only;
- the decision view's exercise now holds that a click on the overlay's "i" does not tick its box;
- `scripts/exercise_decision_safari.py`, which reads the page's text through the Safari application and was not run,
  cannot open an "i": where it held that the overlay's note was in the page's text, it now holds that it is not.
  The note is read by `scripts/exercise_decision.py` in Chrome and in WebKit and by `scripts/verify_decision.py`.

`scripts/verify_layer.py` is unchanged: `scripts/check_site_copy.py` holds it byte for byte to the commit the stage
four checks hold it to. `scripts/exercise_layer.py` was changed only where it pinned reworded words.
`scripts/exercise_layer_safari.py` pins none of them in its own lines and did not change; what it expects of a unit's
panel comes from `scripts/exercise_layer.py`.

Every block of lines that differs from the commit before the checks were changed (`{before}`) is a row below:
{n_changes} rows in {n_files} files. The table is `60_layer/site_copy_check_changes.csv`, where the old and the new
words stand whole; here each is cut after its first {cut} characters.
""").format(before=chk["checks_were_changed_since_commit"], n_changes=len(changes), n_files=len(ch_by_file), cut=CUT))
    D.append(table(["File", "Blocks changed"], [[cellmd(f"`{f}`"), str(n)] for f, n in ch_by_file.items()]))
    D.append("\n" + table(["File", "Check", "Was", "Now", "The fact it checks"], [[cellmd("`" + c["file"].split("/")[-1] + "`"), cellmd(c["check"]), cellmd(c["was"], CUT), cellmd(c["now"], CUT), cellmd(c["the_fact_it_checks"])] for c in changes]))

    D.append(typed("""
## 9. The runs

Every check was committed before it was run, so each record is of committed code.

### The layer's checks, one at a time

`scripts/run_decision_checks.py`, on the layer built {layer_run}: started {started}, ended {ended}. A browser check
that does not pass is run again, up to {most} times, and every run is recorded.
""").format(layer_run=runs["layer_run_utc"], started=runs["started_utc"], ended=runs["ended_utc"], most=runs["most_runs_of_a_check"]))
    D.append(table(["Check", "Runs made", "Runs that passed", "The file is the committed one", "Its last line"],
                   [[cellmd(c["check"]), str(c["runs_made"]), str(c["runs_that_passed"]), "yes" if c["file_is_as_committed"] else "NO", cellmd(c["runs"][-1]["last_line"])] for c in runs["checks"]]))
    if safari:
        D.append(typed("\n**Not run in this pass:**\n\n") + table(["Check", "Why"], [[cellmd(c["check"]), cellmd(c["why"])] for c in safari]))
    D.append(typed("""
### The gate on the copy

`scripts/exercise_share.py`, run {share_run} in {share_browser}, on the copy made {copy_run}: {share_ok} of
{share_n} steps did what they should.
""").format(share_run=share["run_utc"], share_browser=share["browser"], copy_run=share["copy_run_utc"], share_ok=sum(s["ok"] for s in share["steps"]), share_n=len(share["steps"])))
    D.append(table(["What it did", "What happened"], [[cellmd(s["did"]), cellmd(s["happened"])] for s in share["steps"]]))
    D.append(typed("""
### The check of the words

`scripts/check_site_copy.py`, run {chk_run}: {chk_ok} of {chk_n} checks passed. In a browser it opened
{bub_layer} bubbles in the full layer and {bub_copy} in the copy with the pointer, and {foc_layer} and {foc_copy} by
keyboard focus ({scr_layer} and {scr_copy} of those on an "i" that the browser had first to scroll into view), in
{st_layer} and {st_copy} states of the page. Runs of the browser part it needed: {runs_layer} for the full layer,
{runs_copy} for the copy.

**One defect of the page was found by this check, and fixed.** The page closed a bubble whenever anything scrolled.
An "i" that takes keyboard focus while it is out of sight is scrolled into view by the browser, and that scroll
closed the bubble it had just opened: a reader who tabbed to an "i" below the fold of a panel saw nothing. The check
met it as a failure that came and went - it had moved the pointer onto an "i" straight after scrolling it into view,
and so won or lost the same race. The page now keeps the box with its "i" for as long as the "i" can be seen, and
closes it when the "i" is scrolled out of sight; the check gives every "i" keyboard focus, after putting it out of
sight wherever its panel can scroll; and the last of the planted errors below is the page as it was.
""").format(chk_run=chk["run_utc"], chk_ok=chk["checks_passed"], chk_n=chk["checks_made"], bub_layer=B["layer"]["bubbles_opened_by_the_pointer"], bub_copy=B["copy"]["bubbles_opened_by_the_pointer"],
            foc_layer=B["layer"]["bubbles_opened_by_keyboard_focus"], foc_copy=B["copy"]["bubbles_opened_by_keyboard_focus"], scr_layer=B["layer"]["of_them_on_an_i_that_had_first_to_scroll_into_view"],
            scr_copy=B["copy"]["of_them_on_an_i_that_had_first_to_scroll_into_view"], st_layer=len(B["layer"]["states"]), st_copy=len(B["copy"]["states"]), runs_layer=B["layer"]["runs_made"], runs_copy=B["copy"]["runs_made"]))
    D.append(table(["", "Check", "What it found"], [[cellmd(c["id"]), cellmd(c["check"]), cellmd(c["detail"])] for c in chk["checks"]]))
    D.append(typed("""
### The planted errors

{caught} of {planted} errors, each planted on a copy and never on the real files, were caught by a check meant to
catch them (run {tri_run}). The first eight are the ones the owner named.
""").format(caught=tri["caught"], planted=tri["planted"], tri_run=tri["run_utc"]))
    D.append(table(["Planted", "On", "Checks meant to catch it", "Checks that failed", "Caught"],
                   [[cellmd(t["planted"]), cellmd(t["on"]), cellmd(", ".join(t["checks_meant_to_catch_it"])), cellmd(", ".join(t["checks_that_failed"])), "yes" if t["caught"] else "NO"] for t in tri["trials"]]))

    D.append(typed("""
## 10. What was seen

The pictures were taken {shots_utc} in a headless Chrome, of both builds at three window sizes, each with an "i"
opened by the pointer, and every one was opened and looked at. The measurements are the script's; "seen" is what the
picture shows. The pictures are in `60_layer/site_copy_shots/`, outside git like the rest of that folder.

**Overall.** {overall}

**At a phone's width.** {phone}
""").format(shots_utc=seen["pictures_taken_utc"], overall=seen["overall"], phone=seen["what_breaks_at_a_phones_width"]))

    def measured(m):
        if "box" in m and not m.get("shown"):
            return cellmd(f"window {m['window'][0]} x {m['window'][1]}; no bubble opened: the pointer could not reach the i; the page scrolls sideways: {'YES' if m['page_scrolls_sideways'] else 'no'}")
        if "box" in m:
            return cellmd(f"window {m['window'][0]} x {m['window'][1]}; bubble at {m['box'][0]}, {m['box'][1]}, {m['box'][2]} x {m['box'][3]}; wholly inside the window: {'yes' if m['inside'] else 'NO'}; "
                          f"covers its own i: {'YES' if m['covers_its_own_i'] else 'no'}; the page scrolls sideways: {'YES' if m['page_scrolls_sideways'] else 'no'}")
        return cellmd("; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in m.items()))
    D.append(table(["Build", "Window", "Picture", "Measured", "Seen"], [[cellmd(p["build"]), cellmd(p["size"].replace("x", " x ")), cellmd(p["what"]), measured(p["measured"]), cellmd(p["seen"])] for p in seen["pictures"]]))

    D.append(typed("""
## 11. Words of the deck that were not used

The deck asks that its words be used as written and that a word which would misstate something be changed and
listed. These are those changes; each is a row of section 2.
"""))
    D.append(table(["Where", "The deck's words", "Why not", "What the page says"], [[cellmd(a["where"]), cellmd(a["said"]), cellmd(a["true"]), cellmd(a["fix"])] for a in not_deck]))
    D.append(typed("""
Three things of the handoff could not be done as written, and were done as closely as they could be:

- the picture "the decision view's list, with a district chosen and the prompt's i open" is two pictures, because
  the prompt stands only while no district is chosen (section 10);
- the sentence the owner gave for the scripts that were called unchanged is said of `scripts/exercise_layer.py`
  alone, with a clause for `scripts/exercise_layer_safari.py`, which did not need a change (section 8);
- the check of the words gained one group the owner did not list, on the checks' own changes (its checks `e1` and
  `e2`), so that "no check is removed or loosened" can be read off a table.
"""))

    D.append(typed("""
## 12. What this document was written from

| File | Bytes | SHA-256 |
|---|---|---|
"""))
    D.append("\n".join(f"| `{i['path']}` | {i['bytes']:,} | `{i['sha256']}` |" for i in INPUTS) + "\n")
    text = "".join(D)
    for bad in ("/Users/", "@gmail", "@anthropic"):
        if bad in text:
            stop(f"the document would carry '{bad}': a path of this machine or an address")
    OUT.write_text(text, encoding="utf-8")
    print(f"docs/SITE_COPY.md written: {len(text):,} characters; {len(fixed)} findings fixed, {len(listed)} listed; {len(strings):,} rows of strings read; {len(changes)} changed blocks of checks; {chk['checks_made']} checks; "
          f"{tri['planted']} planted errors; {len(seen['pictures'])} pictures")


NIRV_NOW = "stopped; not a measure (ruling of 7 Oct 2026); nothing queued; its columns are blank (`nirv_status` reads `pending`)"    # the owner's words for the state of NIRv, row 11 of his table
IN_DOCUMENTS = [("README.md", "pending, nothing queued", NIRV_NOW), ("docs/DEGRADATION.md", "pending, and **nothing is queued**", NIRV_NOW),      # (the document, what it said, what it must say now)
                ("README.md", "The page computes nothing", "The page works out no figure"), ("docs/LAYER.md", "it computes nothing", "it works out no figure")]
CUT = 260                                             # how much of a changed block of a check is shown in section 8: the table itself holds it whole
LEAD = 90                                             # how much of an unchanged string is shown in section 7


if __name__ == "__main__":
    main()
