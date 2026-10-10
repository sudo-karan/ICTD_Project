#!/usr/bin/env python3
"""The supervisor's comments on two decks, as the project owner recorded them in his handoff note of 11 October 2026.

    python 00_raw/07_project_record/_build_supervisor_comments.py

Why this file exists (11 Oct 2026). `docs/GAP.md` has a section on what the fourth stage answers of the supervisor's
comments, and quotes them. No figure and no quotation of that document is typed: each is read from a file. The comments
were given in the owner's handoff note of that day, a working file that is not in git. This script reads them out of
the note, word for word, and writes them to the small record beside it, which is in git and has a row in
`../data_manifest.csv`. The record is the owner's account of what his supervisor said. It is not the supervisor's own
text.

In      the owner's note (NOTE below), a working file of the session; not in git
Out     supervisor_comments_as_recorded_2026-10-11.json   for each of the two decks, the comment as one text and its
                                                          numbered points apart; the note's SHA-256

How the note is read. Under the line "The comments, as I recorded them:" the note has one item for each deck,
`- After <the deck>: "<the comment>"`, wrapped over several lines, and the items end at the first empty line. The lines
of an item are joined with single spaces; the comment is the text between the item's first and last double quotation
mark. A comment is cut into its points before each number that is followed by a full stop and a space and stands at
the comment's start or after a space.

What is checked here, and the run stops if one fails:
  - the note is the file as it was given on 11 October 2026 (its SHA-256, below);
  - exactly two items are read: one after the proposal deck, one after the methodology deck;
  - the points of a comment are numbered 1, 2, 3 in order, and joined by single spaces they are the comment;
  - every point stands in the note, word for word, once the note's line breaks and indents are made single spaces.
What is NOT checked: that the note records what the supervisor said. Only the owner can say that.

The output carries no time of writing, so that running this again writes the same bytes.
"""
import hashlib, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NOTE = ROOT / ".session_scratch_2026-10-05" / "handoff" / "2026-10-11_finish_stage4.md"
NOTE_SHA256 = "d8b05a081aebfb5794a74122c221d8fc6607ea9384d5d30b16f2ca8dfe1848e2"
OUT = HERE / "supervisor_comments_as_recorded_2026-10-11.json"
HEAD = "The comments, as I recorded them:"
DECKS = ("the proposal deck", "the methodology deck")


def stop(message):
    sys.exit("STOPPED: " + message)


def main():
    if not NOTE.is_file():
        stop(f"the owner's note is not at {NOTE.relative_to(ROOT)}: the record beside this script stands as it is and is not rebuilt")
    raw = NOTE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != NOTE_SHA256:
        stop("the note is not the file that was given on 11 October 2026 (its SHA-256 differs)")
    lines = raw.decode("utf-8").splitlines()
    heads = [i for i, l in enumerate(lines) if l.strip() == HEAD]
    if len(heads) != 1:
        stop(f"the line {HEAD!r} stands {len(heads)} times in the note, not once")
    items = []
    for l in lines[heads[0] + 1:]:
        if not l.strip():
            break
        if l.strip().startswith("- "):
            items.append(l.strip()[2:])
        elif items:
            items[-1] += " " + l.strip()
        else:
            stop("a line under the heading belongs to no item")
    flat = " ".join(raw.decode("utf-8").split())
    comments = []
    for item in items:
        m = re.fullmatch(r'After (.+?): "(.+)"\.?', item)
        if not m:
            stop(f"an item is not of the form After <the deck>: \"<the comment>\": {item[:60]!r}")
        after, text = m.group(1), m.group(2)
        points = [p.strip() for p in re.split(r"(?:(?<=\s)|^)(?=\d+\. )", text) if p.strip()]
        numbers = [int(re.match(r"(\d+)\. ", p).group(1)) for p in points]
        if numbers != list(range(1, len(points) + 1)) or " ".join(points) != text:
            stop(f"the points of the comment after {after} are not numbered in order, or do not make up the comment")
        if any(p not in flat for p in points):
            stop(f"a point of the comment after {after} does not stand word for word in the note")
        comments.append({"after": after, "text": text, "points": points})
    if tuple(c["after"] for c in comments) != DECKS:
        stop(f"the items read are {[c['after'] for c in comments]}, not one after each of {list(DECKS)}")
    record = {"what": "The supervisor's comments on two decks, as the project owner recorded them and gave them in his handoff note of 11 October 2026. This is the owner's record, "
                      "word for word as it stands in his note; it is not the supervisor's own text.",
              "given_in": "the owner's handoff note of 11 October 2026 (.session_scratch_2026-10-05/handoff/2026-10-11_finish_stage4.md, a working file that is not in git)",
              "note_sha256": NOTE_SHA256,
              "made_by": "00_raw/07_project_record/_build_supervisor_comments.py",
              "comments": comments}
    OUT.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    data = OUT.read_bytes()
    print(f"wrote {OUT.relative_to(ROOT)}: {len(comments)} comments, {sum(len(c['points']) for c in comments)} points; {len(data):,} bytes, sha256 {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
