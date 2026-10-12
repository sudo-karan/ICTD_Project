#!/usr/bin/env python3
"""Writes docs/SITE_COPY.md: what was untrue on the map page and what it says now, every string before and after, every
check whose words changed, the runs, and what was seen in the screenshots - the account of the owner's handoff of
11 October 2026, "The site in plain words, with every untrue line fixed".

    .venv/bin/python scripts/write_site_copy.py

It types no figure. Every count, time, hash and sentence of the page in the document is read from one of the files
below; the words typed in this script pass through typed(), which stops the run if they carry a digit outside a code
span, a date, a step of the handoff, the number of a section or of a row of the owner's table, or the name of a hash.
It reads, and stops unless each is there and is of the builds on disk:
    60_layer/site_copy_audit.csv            the findings: the owner's table and the blind reader's, each with its fix
    60_layer/site_copy_strings.csv          every visible string and "i" of both builds, before and after
    60_layer/site_copy_check_changes.csv    every changed block of a check, with what it checks
    60_layer/site_copy_check.json           scripts/check_site_copy.py: its checks, and what it saw in a browser
    60_layer/site_copy_trials.json          the errors planted against that check
    60_layer/site_copy_looked_at.json       the screenshots: what was measured and what was seen
    60_layer/site_copy_results_changes.json the figures of docs/RESULTS.md that changed when it was written again
    60_layer/decision_runs.json             scripts/run_decision_checks.py: every run of the layer's checks
    70_share/exercise_share_chrome.json     scripts/exercise_share.py: the gate on the copy
    60_layer/layer.provenance.json, 70_share/share.provenance.json      the two builds
    README.md, docs/DEGRADATION.md, docs/LAYER.md                       for one hold: the two findings that were in documents
    docs/RESULTS.md                                                     for one hold: the list of its changed figures is of it
The run stops if a check did not pass, a planted error was not caught, a record is of another build, the check of the
words is not the committed file, a finding is still marked as to do, a finding marked as fixed in a document still
stands in it, or a line of docs/RESULTS.md changed in anything but a figure that is listed.

THE SIX LINES. Later on 11 October 2026 the owner gave his words for six lines of the page that the audit had listed
for him (his third handoff of that day). They are rows of the audit like any other, marked as fixed with his ruling,
and a section of their own sets each string beside what it was in the build kept before them, from the record of
scripts/check_site_copy.py (its group f). That section also lists, by `git grep`, where his eight phrases still
stand in the tracked files this task does not write.

THE GUIDE BUTTON AND THE LOADER. On 13 October 2026 the owner had a third button put on the page, Guide, which opens
docs/GUIDE.md with its pictures, and a loader. A section of its own says what was added, sets the guide's pictures
beside what was seen in each, gives the gate on the guide's figures with every figure it lists as coming from another,
and lists the figures of the guide that are not the ones the owner wrote, from git. For it the script also reads
docs/GUIDE.md and its pictures, and the record of the layer as it was kept before the Guide button. The run stops
unless the checks of group g passed, the two planted errors the owner named with the guide were caught by the gate,
and every picture of the guide is the one that was looked at.

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
ALLOWED = [r"`[^`]*`", r"\b\d{1,2} October 2026\b", r"\bSteps? \d\b", r"\bsection \d+\b", r"\brow \d+\b", r"(?m)^#{1,6} \d+\. ", r"\bSHA-256\b"]       # where the typed words may carry a digit (a code span, a date, a step, a section, a row of the owner's table, a heading's number, the name of a hash): none of them is a measurement


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


def around(a, b, margin=110):
    """Two texts that differ in one stretch: each cut to that stretch and to what stands on either side of it, at whole words, and said to be cut."""
    n, p, e = min(len(a), len(b)), 0, 0
    while p < n and a[p] == b[p]:
        p += 1
    while e < n - p and a[len(a) - 1 - e] == b[len(b) - 1 - e]:
        e += 1
    lo = max(0, p - margin)
    lo = a.rfind(" ", 0, lo) + 1 if lo else 0
    out = []
    for t in (a, b):
        hi = len(t) - max(0, e - margin)
        hi = t.find(" ", hi) if 0 <= t.find(" ", hi) else len(t)
        out.append(("[...] " if lo else "") + t[lo:hi] + (" [...]" if hi < len(t) else ""))
    return out


def table(heads, rows):
    return "\n" + "\n".join(["| " + " | ".join(typed(h) for h in heads) + " |", "|" + "---|" * len(heads)] + ["| " + " | ".join(r) + " |" for r in rows]) + "\n"


def merged(rows):
    """Rows of strings that say the same thing in several places (the same kind of string, the same words before and after) as one row, which names the first place and counts the others."""
    out, at = [], {}
    for r in rows:
        k = (r["kind"], r["before"], r["after"], r["status"], r["note"])
        if k in at:
            at[k]["more"] += 1
        else:
            at[k] = dict(r, more=0)
            out.append(at[k])
    return [dict(r, where=r["where"] + (f" (and {r['more']} more of the same)" if r["more"] else "")) for r in out]


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
    pics = seen.get("against_the_pictures_kept_before_the_guide")
    if not pics or pics["pictures"] != len(seen["pictures"]) or pics["byte_for_byte_the_same"] + pics["differ_only_inside_the_row_of_the_three_buttons"] + pics["differ_elsewhere_and_were_looked_at_again"] + pics["new_and_were_looked_at"] != pics["pictures"]:
        stop("60_layer/site_copy_looked_at.json does not say, for every picture, how it stands to the picture kept before the Guide button")
    gp = seen.get("the_guides_pictures") or {}
    if not (gp.get("each_is_byte_for_byte_the_picture_in_docs_guide") is True and gp.get("builds") == now and len(gp.get("pictures", [])) == GUIDE_PICTURES
            and all(q["seen"].strip() and q["sha256"] == hashlib.sha256(use(q["file"]).read_bytes()).hexdigest() for q in gp["pictures"])):
        stop("60_layer/site_copy_looked_at.json does not hold the guide's pictures as they are in docs/guide/, each taken again of the builds on disk and each with what was seen in it")
    row = (seen.get("the_row_of_the_three_buttons") or {}).get("measured") or {}
    for b_ in ("full layer", "published copy"):                 # what section 14 says of the row of the three buttons, as it was measured in a browser
        phone = next((x for x in row.get(f"{b_} | 390x844", {}).get("buttons", []) if x["button"] == "Guide"), {})
        if [row.get(f"{b_} | {size}", {}).get("lines_of_the_row") for size in ("1280x800", "1000x700")] != [1, 2] or phone.get("what_lies_on_top_of_its_middle") != "the legend":
            stop("the three buttons were not measured on one line at 1280 px, on two at 1000 px and, at a phone's width, with the legend over Guide, as section 14 says")
    g_checks = [c for c in chk["checks"] if c["id"].startswith("g")]
    tg = chk.get("the_guide") or {}
    if not (len(g_checks) == len(G_CHECKS) and all(c["pass"] for c in g_checks) and tg.get("sha256") == hashlib.sha256(use("docs/GUIDE.md").read_bytes()).hexdigest()
            and L.get("guide", {}).get("source", {}).get("sha256") == tg.get("sha256") and len(L["guide"]["pictures"]) == GUIDE_PICTURES):
        stop("60_layer/site_copy_check.json does not carry the guide of docs/GUIDE.md with its group g passed, or the layer was not built from that guide")
    named = [t for t in tri["trials"] if t["planted"].split(".")[0] in GUIDE_TRIALS]
    if len(named) != len(GUIDE_TRIALS) or not all(t["caught"] and "g4" in t["checks_that_failed"] for t in named):
        stop("the two errors the owner named with the guide - a changed figure, and a figure found nowhere - were not both caught by the gate on the guide's figures")
    six = chk.get("the_six_lines", {}).get("strings_that_differ_from_the_kept_builds") or []
    f_checks = [c for c in chk["checks"] if c["id"].startswith("f")]
    if not (six and len(f_checks) == len(F_CHECKS) and all(c["pass"] for c in f_checks) and {x["fix"] for x in six} == set(FIXES)):
        stop("60_layer/site_copy_check.json does not carry the six lines of the owner's third handoff, each found in the builds, with its group f passed")
    by_owner = [a for a in audit if a["done"].startswith(SIX_DONE)]
    todo = [a["where"] for a in audit if not a["done"].startswith(("fixed", "listed"))]
    if todo:
        stop("a finding of the audit is neither fixed nor listed for the owner: " + "; ".join(todo))
    for a in audit:
        if any(not v.strip() for v in a.values()):
            stop("a finding of the audit has an empty cell: " + a["where"])
    res = J("60_layer/site_copy_results_changes.json")
    if not (res["now_sha256"] == hashlib.sha256(use(res["document"]).read_bytes()).hexdigest() and res["no_sentence_was_changed"] is True and not res["any_other_line_gone_or_changed"]):
        stop("60_layer/site_copy_results_changes.json is not of docs/RESULTS.md as it is, or a line of that document changed in more than a listed figure")
    for doc, gone, there in IN_DOCUMENTS:                     # the findings that were in documents and not on the page
        words = " ".join(use(doc).read_text(encoding="utf-8").split())
        if gone in words or there not in words:
            stop(f"{doc} still says '{gone}', or does not say '{there}': a finding of the audit that is marked as fixed in a document is not")

    fixed = [a for a in audit if a["done"].startswith("fixed")]
    fixed = [a for a in fixed if not a["done"].startswith(SIX_DONE)] + [a for a in fixed if a["done"].startswith(SIX_DONE)]       # the lines the owner reworded in his third handoff stand last
    listed = [a for a in audit if a["done"].startswith("listed")]
    on_page = lambda a: a["where"].startswith(("both builds", "full layer", "published copy"))
    why = {}                                                  # a finding that says "As the row above" takes that row's reason
    for i, a in enumerate(audit):
        why[a["where"]] = why[audit[i - 1]["where"]] if a["true"].strip() == "As the row above." and i else a["true"][len("As the row above: "):].capitalize() if a["true"].startswith("As the row above: ") else a["true"]
    not_deck = [a for a in fixed if "the deck's own" in a["where"]]
    full, copy_ = "the full layer", "the published copy"
    rows_of = lambda build, parts=None, status=None: [r for r in strings if r["build"] == build and (parts is None or r["part"] in parts) and (status is None or (r["status"] in status))]
    changed = ("reworded", "new", "new: an i", "gone")
    CONTROLS = ("side panel", "decision view: controls", "overlay", "search", "page messages")
    OTHER = ("legend", "a unit's panel", "decision view: the list", "decision view: legend and why this tier", "About this map", "Sources", "README.txt")
    layer_rows = {(r["before"], r["after"]) for r in rows_of(full)}
    only_copy = [r for r in rows_of(copy_) if r["part"] != "figures" and r["status"] in changed and (r["before"], r["after"]) not in layer_rows]
    moved = lambda r: r["status"] == "unchanged" and r["kind"].startswith("i (")           # the same words, now in an "i"
    controls = [dict(r, status="the same words, now in an i" if moved(r) else r["status"]) for r in rows_of(full, CONTROLS) if r["status"] in changed or moved(r)]
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
  it left out stands in a small "i" beside it, which opens a bubble on hover and on keyboard focus, and on a click,
  which is what a tap on a touch screen sends (no touch screen was tried);
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
Nothing else was added to the data that day. (On 13 October 2026 a second key was added, `guide_html`, the guide that
the page's third button opens: section 14.)

**Six lines were corrected later the same day.** The audit had listed them for the owner with nothing changed; in his
third handoff of 11 October 2026 he gave his words for each and asked that every other string stay as it is. They
are the last {n_six} rows of section 2, with his ruling, and section 13 sets each string beside what it was.

**A Guide button and a loader were added on 13 October 2026.** A third button opens the owner's guide to the map,
with its pictures, in the window the other two texts use; and the map's area says what the page is doing while it
opens. No word that this document describes was changed by it. Its account is section 14: what was added, the
pictures, and the gate that traces every figure of the guide.
""").format(written=written, layer_run=L["run_utc"], copy_run=S["run_utc"], n_checks=chk["checks_made"], n_trials=tri["planted"], n_six=len(by_owner)))

    D.append(typed("""
## 2. What was untrue, and what the page says now

{n_fixed} findings were fixed. The first group is the owner's own table, each row confirmed against its source; the
second is what one reader found besides. That reader was given every text of both builds, the README and the
documents, and had not seen the owner's list. "Done" names the step and the commit. The last {n_six} rows are lines
that stood in section 3, listed for the owner, until he gave his words for them in his third handoff of the day
(section 13); "What it says now" gives those words and, for the prompt, his ruling.
""").format(n_fixed=len(fixed), n_six=len(by_owner)))
    D.append(table(["Where", "It said", "What is true", "Source", "What it says now", "Done"], [[cellmd(a[k]) for k in ("where", "said", "true", "source", "fix", "done")] for a in fixed]))

    D.append(typed("""
## 3. Listed for the owner, with nothing changed

{n_listed} findings are listed and nothing was changed for them. Each is one of these: a string that comes from
`55_decision/` (a cell's name or reason, a tier's reason, a work-type field, a window's description, the governance
prompt); a sentence of `docs/RESULTS.md`, or of another document this task does not rewrite; words the deck keeps as
they are; or the owner's own words. `scripts/check_site_copy.py` holds that each of the page's is still on the page as
quoted here. The lines he has since reworded are no longer here: they are in section 2.
""").format(n_listed=len(listed)))
    D.append(table(["Where", "It says", "What is true", "Source", "Why nothing was changed"], [[cellmd(a[k]) for k in ("where", "said", "true", "source", "fix")] for a in listed]))

    D.append(typed("""
## 4. The side panel and the decision view's controls, before and after

The full layer. Every string of the side panel, the search, the decision view's controls, the overlay's box and the
page's own messages that is not what it was, or that keeps its words and now stands in an "i": {n_controls} strings,
in {n_rows} rows, a string that says the same thing in several places being one row. "Where" is the string's key in
`data.js`, or its place in `index.html`. A row marked "new: an i" is a bubble that did not exist before.
""").format(n_controls=len(controls), n_rows=len(merged(controls))))
    D.append(table(["Where", "What it is", "Before", "After", "What happened"], [string_row(r) for r in merged(controls)]))
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
four checks hold it to. `scripts/exercise_layer.py` was changed only where it pinned reworded words, until
13 October 2026, when it gained the steps of the Guide button and the loader (section 14).
`scripts/exercise_layer_safari.py` pins none of them in its own lines and did not change; what it expects of a unit's
panel comes from `scripts/exercise_layer.py`.

Every block of lines that differs from the commit before the checks were changed (`{before}`) is a row below, for
each check and for the two document writers whose holds and quotations follow the page's words: {n_changes} rows in
{n_files} files. The table is `60_layer/site_copy_check_changes.csv`, where the old and the new words stand whole;
here each is cut after its first {cut} characters. Since 13 October 2026 the rows of `scripts/check_site_copy.py`
itself are in the table too, against the last commit before the Guide button (`{before_guide}`): that script did not
exist at the commit the other files are set against.
""").format(before=chk["checks_were_changed_since_commit"], n_changes=len(changes), n_files=len(ch_by_file), cut=CUT, before_guide=BEFORE_THE_GUIDE))
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
catch them (run {tri_run}). The first eight are the ones the owner named; those numbered from twenty-three to
twenty-six are the four he named with the six lines, each of which puts an old line back; and those numbered
twenty-eight and twenty-nine are the two he named with the guide, a changed figure and a figure found nowhere, each
planted on a copy of the guide's text. The ones after them try the other checks of the guide and the loader.
""").format(caught=tri["caught"], planted=tri["planted"], tri_run=tri["run_utc"]))
    D.append(table(["Planted", "On", "Checks meant to catch it", "Checks that failed", "Caught"],
                   [[cellmd(t["planted"]), cellmd(t["on"]), cellmd(", ".join(t["checks_meant_to_catch_it"])), cellmd(", ".join(t["checks_that_failed"])), "yes" if t["caught"] else "NO"] for t in tri["trials"]]))

    D.append(typed("""
## 10. What was seen

The pictures were taken {shots_utc} in a headless Chrome, of both builds at three window sizes, each with an "i"
opened by the pointer. Every one was opened and looked at when it was first taken, and again whenever it came out
different outside the row of the three buttons; the paragraph below says which were looked at on these builds. The
measurements are the script's; "seen" is what the picture shows. The pictures are in `60_layer/site_copy_shots/`,
outside git like the rest of that folder.

**The pictures are of the builds with the Guide button.** With the six lines, four more had been taken of each
build at the largest size: a ranked list with an East Coast badge in view, the prompt of a unit outside villages, the
comparison section's "i" in the panel of an East Coast unit, and the grid of "why this tier". On 13 October 2026
every picture was taken again, since each shows the side panel and the side panel has a third button; and more were
taken of the published copy, of the Guide's window and of the loader. Each picture was then held, pixel for pixel,
against the picture of the same name that had been kept, and looked at, before the Guide button. Of {pic_n} pictures,
byte for byte the kept one: {pic_same}; differing only inside the row of the three buttons, and so showing everywhere
else exactly what was looked at before: {pic_row}; differing elsewhere too, each opened and looked at again:
{pic_else}; new, and looked at: {pic_new}. {pic_how}

**Overall.** {overall}

**At a phone's width.** {phone}
""").format(shots_utc=seen["pictures_taken_utc"], overall=seen["overall"], phone=seen["what_breaks_at_a_phones_width"], pic_n=pics["pictures"], pic_same=pics["byte_for_byte_the_same"],
            pic_row=pics["differ_only_inside_the_row_of_the_three_buttons"], pic_else=pics["differ_elsewhere_and_were_looked_at_again"], pic_new=pics["new_and_were_looked_at"], pic_how=pics["how"][0].upper() + pics["how"][1:] + "."))

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
listed. These are those changes; each is a row of section 2, where the finding that led to it stands just above it.
"""))
    D.append(table(["Where", "The deck's words", "Why not", "What it says", "Done"], [[cellmd(a["where"]), cellmd(a["said"]), cellmd(why[a["where"]]), cellmd(a["fix"]), cellmd(a["done"])] for a in not_deck]))
    D.append(typed("""
Four things of the handoff were not done exactly as written:

- the picture "the decision view's list, with a district chosen and the prompt's i open" is two pictures, because
  the prompt stands only while no district is chosen (section 10);
- the sentence the owner gave for the scripts that were called unchanged is said of `scripts/exercise_layer.py`
  alone, with a clause for `scripts/exercise_layer_safari.py`, which did not need a change (section 8);
- the check of the words gained one group the owner did not list, on the checks' own changes (its checks `e1` and
  `e2`), so that "no check is removed or loosened" can be read off a table; and in a browser it gives every "i"
  keyboard focus as well as the pointer, which is how the defect of section 9 was pinned down;
- this document is written from the `60_layer/site_copy_*` files, as asked, and from what its section on the runs
  needs besides: the runner's record, the record of the gate on the copy and the two builds' own records. It also
  reads four documents, to hold a fix or a list against each (section 14).
"""))

    D.append(typed("""
## 12. The documents

The documents that describe the page were brought up to date in the same step. `docs/LAYER.md`,
`docs/DECISION_LAYER.md` and `docs/RESULTS.md` were each written again by its own script; `README.md` and
`docs/DEGRADATION.md` were edited by hand, for the rows of section 2 that are in documents.

**`docs/RESULTS.md`: every figure that changed.** The owner asked that no sentence of it be changed by hand and that
every figure that changed be listed, old beside new. `scripts/write_results.py` wrote it again, unchanged itself, from
the records of the day. The document lists every figure of its own text with the file it is read from, and that list
was set against the same list of the version of commit `{res_commit}`: of {res_n} figures, {res_changed} are printed
differently, {res_gone} are gone and {res_added} are new. {res_lines} lines of its text above that list differ, and
each is the old line with nothing changed in it but those figures; its headings are the same.
""").format(res_commit=res["before_is_the_document_of_commit"], res_n=res["figures_in_the_text_now"], res_changed=res["figures_printed_differently"], res_gone=res["figures_gone"],
            res_added=res["figures_added"], res_lines=res["lines_of_the_text_above_section_13_gone_or_changed"]))
    D.append(table(["What happened", "Before", "Now", "Read from", "Where in that file"],
                   [[cellmd(r["kind"]), cellmd(r["as_printed_before"]), cellmd(r["as_printed_now"]), cellmd(r["file"]), cellmd(r["where_in_the_file"])] for r in res["changes"]]))

    D.append(typed("""
## 13. The six lines of the owner's third handoff

Later on 11 October 2026 the owner ruled on six lines that section 3 then listed for him. They were untrue or
misleading, he gave his words for each, and he asked that every other string stay as it is.

- **It is our placebo test, not "CoRE Stack's own check".** The check that fails in the East Coast zone is this
  project's: it uses CoRE Stack's Improvement class as a check on its Degradation class. Its failure rests on few
  districts, and the two "i" that speak of it now say so.
- **Hansen does see loss on open land; what it cannot see is thinning.** The layer after the Hansen layer draws
  Hansen's loss on land that was open in the first year of its record.
- **"Little or no" loss, as the cells' names say.** The column holds every unit under the loss minimum in the
  window, not only units with none. Only what the page prints changes; the decision table's code for the column is
  as it was.
- **Outside villages: the question is kept and the claim dropped.** Nothing in the repository shows that this land
  is in no village plan, and works are geotagged on it.
- **The Hansen row of Sources says what was reconciled**, and up to which year. The copy's README takes its credits
  from that row and follows it.
- **Block rasters, not a dashboard**, as `docs/LAYER.md` says of the same thing.

**His ruling on the prompt.** The prompt of an outside-village unit comes from the decision table,
`55_decision/condition_by_unit.csv`, column `governance_prompt`. To rebuild that table for one sentence would send
the fourth stage through four more steps, so it is not rebuilt now. Until it is next rebuilt the builder of the
decision view, `scripts/_layer_decision.py`, shows the new words in place of the table's, a change of the page only.
The builder still guards the table: it stops unless the table's prompt is exactly the old sentence, so that the swap
cannot hide a change in the table. When the decision table is next rebuilt, with the Foundation's ruling on the
tiers, `scripts/05_build_decision.py` takes the new words and the swap goes. `scripts/verify_decision.py` holds both
halves: that the page shows the new words, and that the table still carries the old sentence.

**Every string that differs from the builds kept before the six lines.** Both builds were copied aside before a
line was changed, as they were before the words were first rewritten. `scripts/check_site_copy.py` holds the builds
on disk against those copies (its group `f`): no string was dropped, and none was added but the four that the Guide
button and the loader put on the page on 13 October 2026 (section 14); each string below differs by exactly the
owner's replacement and by nothing else; no place of a fix still holds its old words; no other part of `data.js`
differs but the build's own time and the guide's key; and `index.html` differs only in the places the Guide button
and the loader changed, each written out in the check. In the full layer {six_layer} strings differ, in the
copy {six_copy}. Where the same string differs in both builds it is one row. A long string is shown by the stretch
that differs and what stands on either side of it, with a mark where it is cut; the record of the check holds each
whole.
""").format(six_layer=sum(1 for x in six if x["build"] == full), six_copy=sum(1 for x in six if x["build"] == copy_)))
    rows6, at6 = [], {}
    for x in six:
        k6 = (x["fix"], x["as_it_was"], x["as_it_is"])
        if k6 in at6:
            at6[k6]["builds"].add(x["build"])
            at6[k6]["wheres"].append(x["where"])
        else:
            at6[k6] = dict(x, builds={x["build"]}, wheres=[x["where"]])
            rows6.append(at6[k6])
    shown6 = lambda x: around(x["as_it_was"], x["as_it_is"]) if max(len(x["as_it_was"]), len(x["as_it_is"])) > LONG else [x["as_it_was"], x["as_it_is"]]
    D.append(table(["Fix", "In", "Where", "As it was", "As it is"],
                   [[cellmd(f"{x['fix']}. {FIXES[x['fix']]}"), cellmd("both builds" if len(x["builds"]) > 1 else next(iter(x["builds"]))), cellmd("; ".join(dict.fromkeys(x["wheres"])))] + [cellmd(t) for t in shown6(x)]
                    for x in sorted(rows6, key=lambda x: x["fix"])]))
    D.append("\n" + table(["", "Check", "What it found"], [[cellmd(c["id"]), cellmd(c["check"]), cellmd(c["detail"])] for c in f_checks]))
    found = {}
    for f_ in subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines():
        if any(f_ == x or f_.startswith(x + "/") for x in NOT_SEARCHED) or (ROOT / f_).stat().st_size > BIGGEST:
            continue
        try:
            words = " ".join((ROOT / f_).read_text(encoding="utf-8").split())            # a phrase broken over two lines is still the phrase
        except (UnicodeDecodeError, OSError):
            continue
        for ph in OLD_WORDS:
            if words.count(ph):
                found[(OLD_WORDS.index(ph), f_)] = words.count(ph)
    grep = [[cellmd(OLD_WORDS[k]), cellmd("`" + f_ + "`"), str(n_)] for (k, f_), n_ in sorted(found.items())]
    D.append(typed("""
**Where the old words still stand, outside the page.** The eight phrases the owner added to the list of
`scripts/check_site_copy.py` were looked for, as he wrote them and with a break of line between two of their words
counted as a space, in every file of text git tracks but the registered inputs and the documents this task writes by
script (those say what changed, and so quote the old words). None of these is a string of the page. They are of three kinds: a check or a builder that names an old line in order to forbid it, to
guard the decision table's sentence or to record the change; the script that builds the decision table, which keeps
its sentence until that table is next rebuilt; and a hand-kept document or a stage script's own account, which this
handoff does not rewrite. `README.md` speaks of Hansen on the forest mask, which is blind to open land by
construction: the owner asked that it be left.
"""))
    D.append(table(["The owner's phrase", "File", "Times it stands there"], grep))

    # ---- section 14: the Guide button and the loader (the owner's handoff of 13 October 2026)
    G, L0 = L["guide"], J(BEFORE_GUIDE_RECORD)
    first = subprocess.run(["git", "-C", str(ROOT), "log", "--diff-filter=A", "--format=%h", "--", "docs/GUIDE.md"], capture_output=True, text=True, check=True).stdout.split()[-1]
    was = subprocess.run(["git", "-C", str(ROOT), "show", f"{first}:docs/GUIDE.md"], capture_output=True, text=True, check=True).stdout.splitlines()
    is_ = (ROOT / "docs" / "GUIDE.md").read_text(encoding="utf-8").splitlines()
    if len(was) != len(is_) or any(re.sub(r"\d", "", a) != re.sub(r"\d", "", b) for a, b in zip(was, is_)):
        stop("docs/GUIDE.md differs from the file the owner wrote in more than figures")
    not_his = []
    for n_, (a, b) in enumerate(zip(was, is_), 1):
        if a != b:
            fa, fb = re.findall(r"\d[\d,.]*\d|\d", a), re.findall(r"\d[\d,.]*\d|\d", b)
            ks = [i for i in range(len(fa)) if fa[i] != fb[i]]
            near = lambda line, t, i: " ".join(re.search(r"(?:\S+\s+){0,3}" + re.escape(t[i]) + r"(?:\s+\S+){0,5}", line).group(0).split())
            why = WHY_MEGABYTES if " MB" in near(b, fb, ks[0]) else WHY_COUNT
            not_his.append([str(n_), cellmd("; ".join(dict.fromkeys(near(a, fa, i) for i in ks))), cellmd("; ".join(dict.fromkeys(near(b, fb, i) for i in ks))), cellmd(why)])
    by_how = tg["figures_table"]["by_how"]
    how_n = lambda start: sum(v for k, v in by_how.items() if k.startswith(start))
    if how_n("found") + how_n("comes from") + how_n("a count") != tg["figures_table"]["rows"]:
        stop("the rows of the table of the guide's figures are not all of the three kinds section 14 names")
    lay_runs = {c["check"]: c["runs"][-1]["last_line"] for c in runs["checks"]}
    D.append(typed("""
## 14. The Guide button and the loader (13 October 2026)

On 13 October 2026 the owner asked for three things: a third button on the page, Guide, which opens his guide to the
map with its pictures; a loader, which says what the page is doing while it opens; and the site published with them.
Nothing that section 2 to section 13 describe was changed by it, and no figure, class, count or colour of the page
moved: the checks of section 9 still hold both builds against the copies kept before, with what was added written
out in the check itself.

**What was added to the page.** These strings, and no other, are new in `index.html`, the same in both builds:
""") + table(["Where", "The string"], [[cellmd(x["where"]), cellmd(x["string"])] for x in tg["strings_added_to_the_page_itself"]]) + typed("""
The button stands after About this map and Sources and opens the guide in the window those two use; Close, or a
click outside, shuts it; an address that ends in `#open=guide` opens it. `index.html` changed in {places} places, each
written out in `scripts/check_site_copy.py`; with every one put back, the page is byte for byte the page kept before.
Beyond the button and the loader themselves, three small things are among them. Each of the three texts now opens at
its top. The three buttons have a little less padding, so that they stay on one line beside a scroll bar in a window
{w_wide} px wide; in one {w_narrow} px wide the side panel has no room for three, and Guide stands on a second line,
under the other two; at a phone's width the legend lies over it (section 10). And the page says that it has no icon
(`<link rel="icon" href="data:,">`), so that a browser asks the site for none.

**Why the page says it has no icon.** A browser asks every site for `/favicon.ico` by itself, and this site has none.
`scripts/check_pages_live.py` lets that refused request stand once. The loader lets the page finish loading before the
map is drawn, so the address the page writes its state into changes after the load, and Chrome then asked for the
missing icon a second time. The first copy published with the Guide button failed that one check of the live site for
it, twice, with every other check passed. The line was added, both builds were made again, every check and every
picture of this document was made again on them, and the copy was published again. No check was changed for it;
`scripts/check_site_copy.py` holds the line (check `g2`) and plants its removal.

**The guide.** `docs/GUIDE.md` is the owner's text ({g_bytes} bytes) and the one source of that window.
`scripts/_guide.py`, a converter of its own for what the guide uses, with no package, turns it into HTML when the
layer is built; a tag of the source is never passed through. The HTML is carried in `data.js` as one more key,
`guide_html`, beside `about_html` and `sources_html`: {html_bytes} bytes, of which {pic_b64} are its pictures. A link
in it opens only when clicked, in a new tab, and nothing else in it carries an address. The copy carries the same
guide, unchanged: the guide describes the published copy, and the full layer shows that same text.

**Its pictures.** {n_pics} pictures of the published copy, in a window of {pw} × {ph}, taken {gp_taken} in
{gp_browser} and captured by the browser itself as WebP at quality {gp_quality}; no note is open but the one the last
picture asks for. Each goes into the guide's HTML as its own bytes, so the window opens without a connection; the
build stops if one the guide names is missing. They could not be in the build before they existed, so they were taken
of a build made with the guide's picture lines left out. None of them shows the Guide's window, so that build looks
the same; and taken again of the builds on disk ({gp_again}), each came out byte for byte the picture in
`docs/guide/`. Each was opened and looked at. "Its caption" is the guide's own line under the picture.
""").format(w_wide=row["full layer | 1280x800"]["window"][0], w_narrow=row["full layer | 1000x700"]["window"][0], places=tg["places_of_index_html_changed"], g_bytes=f"{G['source']['bytes']:,}", html_bytes=f"{G['html']['bytes']:,}", pic_b64=f"{G['html']['of_them_the_pictures_as_base64']:,}", n_pics=len(gp["pictures"]),
            pw=G["pictures"][0]["width"], ph=G["pictures"][0]["height"], gp_taken=gp["first_taken_utc"], gp_browser=gp["browser"], gp_quality=gp["webp_quality"], gp_again=gp["taken_again_utc"]))
    D.append(table(["Picture", "Bytes", "What was done", "Its caption", "Seen"],
                   [[cellmd("`" + q["file"] + "`"), f"{q['bytes']:,}", cellmd(q["what_was_done"]), cellmd(q["caption_in_the_guide"]), cellmd(q["seen"])] for q in gp["pictures"]]))
    D.append(typed("""
**The loader.** While the page opens, the map's area says "{loading}" until `data.js` has arrived, then
"{drawing}", and the message goes when the map is ready. The first message is plain markup placed before the tag that
asks for `data.js`; once the data is in, the page changes the message, gives the browser a frame to paint it, and only
then draws the units. Its bar moves and counts nothing: `scripts/verify_layer.py`, which is unedited, holds that the
page's script never uses `fetch` or `XMLHttpRequest`, and without them a browser reports no progress for `data.js`. If
the data never arrives, the page says so as it did. What a reader sees while the page loads was looked at in two of
the frames the browser painted (the last two pictures of section 10).

**The sizes.** In `60_layer/` the two files were {b0} bytes together before the guide (`index.html` {i0}, `data.js`
{d0}; the layer built {t0}) and are {b1} bytes with it (`index.html` {i1}, `data.js` {d1}), against the {limit}
bytes that `scripts/verify_layer.py` allows. The guide's pictures are {pic_bytes} bytes as files.
""").format(loading=next(x["string"] for x in tg["strings_added_to_the_page_itself"] if x["where"] == "index.html, markup"), drawing=next(x["string"] for x in tg["strings_added_to_the_page_itself"] if "script" in x["where"]),
            b0=f"{L0['outputs']['both_bytes']:,}", i0=f"{L0['outputs']['index.html']:,}", d0=f"{L0['outputs']['data.js']:,}", t0=L0["run_utc"], b1=f"{L['outputs']['both_bytes']:,}", i1=f"{L['outputs']['index.html']:,}",
            d1=f"{L['outputs']['data.js']:,}", limit=f"{L['outputs']['limit_bytes']:,}", pic_bytes=f"{sum(q['bytes'] for q in G['pictures']):,}"))
    D.append(typed("""
**What the checks gained.** No check was taken out, and no expected number or count was changed; counts rose only by
what this handoff added, and every changed block is a row of section 8. The layer's exercise now ends, in Chrome,
"{lay_c}" and, in WebKit, "{lay_w}"; the gate on the copy has {share_n} steps. `scripts/check_site_copy.py` gained a
group of its own, `g`, and three of its checks that held "nothing else was added" were widened by exactly what was
added, each written out: `a2` by the one key; `f1` by the strings above, all of which must be there; `f2` by the
places of `index.html`, each found exactly once.
""").format(lay_c=mask(lay_runs["exercise_layer in Chrome"]), lay_w=mask(lay_runs["exercise_layer in WebKit"]), share_n=len(share["steps"])))
    D.append(table(["", "Check", "What it found"], [[cellmd(c["id"]), cellmd(c["check"]), cellmd(c["detail"])] for c in g_checks]))
    D.append(typed("""
**The gate on the guide's figures** (check `g4`). The guide is cut into sentences and table cells. For each one that
holds a figure, all its figures must stand together, each written the same way, in one passage of one of the files
the owner named, a passage that shares a word with the sentence. Allowed, and nothing else: thousands separators, a
space before the per cent sign, the minus sign, and the letter for the multiplication sign. {n_units} sentences and
cells hold a figure. Their traces are {n_rows} rows of a table, since a sentence that draws on two passages has two:
{n_found} found so, {n_from} figures that come from a figure of a named file by a rule written out in the check, and
{n_runs} counts of this build's own runs, which other checks of the group hold to the records of those runs. Every
trace is in `{g_table}`, with the passage beside the sentence.

The files: {files}. The last is not among the files the owner named. It is the registered page of the University of
Maryland, which the record of the provider's cautions names as its input, and it is used for one sentence only: the
citation of the paper behind Hansen's data. The record this check itself writes was among the files he named; only
the count of its own checks is held to it, and to the run that writes it.

**What the gate does not show.** That a passage says what the sentence says. A sentence with several figures, or
with a large one, is held tightly, because another passage would have to hold them all. A lone small figure can stand
beside a shared word in a passage about something else. Every trace was read once, by eye, on 13 October 2026; where
the passage found for a lone figure was not the right one, the right one is named in the check.

**Every figure that stands in no named file as the guide writes it**, with how it comes from one that does. The gate
works each out again from the file's own figure and fails if the guide's differs:
""").format(n_units=tg["figures_table"]["sentences_and_cells_with_a_figure"], n_rows=tg["figures_table"]["rows"], n_found=how_n("found"), n_from=how_n("comes from"), n_runs=how_n("a count"), g_table=tg["figures_table"]["path"],
            files="; ".join("`" + f + "`" if "/" in f or f.endswith(".md") else f for f in tg["files_its_figures_are_traced_to"])))
    D.append(table(["The guide's words", "The figure", "How it comes from the file's", "From"],
                   [[cellmd(x["the_guides_words"], LONG), cellmd(x["figure"]), cellmd(x["how"].split(": ", 1)[1]), cellmd(x["from"])] for x in tg["figures_that_come_from_a_figure_of_a_named_file"]]))
    D.append(typed("""
**Sentences whose figures stand in two passages**, and **sentences whose passage is named** in the check because
many passages hold their one small figure:
""") + table(["The sentence begins", "What is listed", "The passage must hold"],
             [[cellmd(x["sentence_begins"]), cellmd("these figures stand in a passage of their own: " + ", ".join(x["figures_in_a_passage_of_their_own"])), cellmd(x["that_passage_holds"])] for x in tg["sentences_whose_figures_stand_in_two_passages"]]
             + [[cellmd(x["sentence_begins"].replace("`", "")), "its passage is named", cellmd(x["the_passage_holds"])] for x in tg["sentences_whose_passage_is_named"]]))
    D.append(typed("""
**The figures of the guide that are not the ones the owner wrote.** No word of the guide was changed. Its file was set,
line by line, against the file of the commit that added it (`{first}`); these lines differ, each in figures alone:
""").format(first=first) + table(["Line", "The owner's file", "Now", "Why"], not_his))
    D.append(typed("""
## 15. What this document was written from

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


SIX_DONE = "fixed (the owner's words of 11 October 2026, his third handoff"            # how the audit marks a line the owner reworded in his third handoff
FIXES = {1: "our placebo test, not CoRE Stack's own check", 2: "Hansen does see loss on open land", 3: "little or no loss", 4: "outside villages: the question kept, the claim dropped", 5: "the Hansen row of Sources",
         6: "block rasters, not a dashboard"}                                             # the six lines, by the number the check gives each
F_CHECKS = ("f0", "f1 (layer)", "f2 (layer)", "f1 (copy)", "f2 (copy)")
G_CHECKS = ("g0", "g1", "g2", "g3", "g4", "g5", "g6", "g7")                              # the group of the Guide button and the loader (13 October 2026)
GUIDE_TRIALS = ("28", "29")                                                               # the two planted errors the owner named with the guide
GUIDE_PICTURES = 5                                                                        # the guide's pictures, as the owner listed them
BEFORE_THE_GUIDE = "6607784"                                                              # the last commit before the Guide button
BEFORE_GUIDE_RECORD = ".session_scratch_2026-10-05/60_layer_2026-10-13_before_guide/layer.provenance.json"      # the record of the layer as it was kept before the Guide button
WHY_MEGABYTES = "with the guide and its pictures inside, the published copy's two files come to that many megabytes; the gate works it out from their bytes (check `g4`)"
WHY_COUNT = "the count of the run on these builds: the check gained the steps or the checks this handoff added (checks `g5` and `g7` hold the guide to the runs)"
OLD_WORDS = ["CoRE Stack's own check", "already open in 2000", "fairly closed", "No forest loss in the window", "is none: under", "no village plan", "own dashboard", "state totals reconciled"]   # the owner's eight phrases, as he wrote them
NOT_SEARCHED = ["00_raw", "docs/SITE_COPY.md", "docs/DECISION_LAYER.md", "docs/LAYER.md", "docs/RESULTS.md", "docs/GAP.md", "docs/stage4_run_log.md"]      # registered inputs, and the documents this task writes by script
NIRV_NOW = "stopped; not a measure (ruling of 7 Oct 2026); nothing queued; its columns are blank (`nirv_status` reads `pending`)"    # the owner's words for the state of NIRv, row 11 of his table
IN_DOCUMENTS = [("README.md", "pending, nothing queued", NIRV_NOW), ("docs/DEGRADATION.md", "pending, and **nothing is queued**", NIRV_NOW),      # (the document, what it said, what it must say now)
                ("README.md", "The page computes nothing", "The page works out no figure"), ("docs/LAYER.md", "it computes nothing", "it works out no figure")]
BIGGEST = 5_000_000                                   # a tracked file larger than this many bytes is not searched for the owner's phrases: none of the texts is
LONG = 420                                            # a string of section 13 longer than this is shown by the stretch that differs
CUT = 260                                             # how much of a changed block of a check is shown in section 8: the table itself holds it whole
LEAD = 90                                             # how much of an unchanged string is shown in section 7


if __name__ == "__main__":
    main()
