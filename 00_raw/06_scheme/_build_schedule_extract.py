#!/usr/bin/env python3
"""
The list of permissible works under the VB-G RAM G Act, as a table. Made 8 October 2026.

    python 00_raw/06_scheme/_build_schedule_extract.py        (needs pdftotext, from poppler)

Source  egazette_276796_SO5448E_2026-10-05_list_of_permissible_works.pdf
        Ministry of Rural Development notification S.O. 5448(E), 5 October 2026, Gazette of India, Extraordinary,
        Part II, Section 3(ii), No. 5238 - "LIST OF PERMISSIBLE WORKS UNDER THE VIKSIT BHARAT-GUARANTEE FOR ROZGAR AND
        AJEEVIKA MISSION (GRAMIN): VB-G RAM G SCHEME", made "in pursuance of paragraph 4 of the SCHEDULE I" of Act 36 of 2025.
        https://egazette.gov.in/WriteReadData/2026/276796.pdf   1,700,498 bytes   sha256 below.
In      so5448e_2026-10-05_permissible_works_verbatim_transcription.txt
        The English table (pages 17-28) transcribed row by row on 8 October 2026 by an independent verifier, which says in
        its own header how: the words from the PDF's text layer, the rows from the ruled lines of the rendered pages, and
        THE SERIAL NUMBERS FROM THE PAGE IMAGES - the digits of the serial-number column are not in the PDF's text layer.
        pib_2319426_2026-10-06_ministry_notifies_375_permissible_works.html
        The Ministry's press release of 6 October 2026 on this list (Press Information Bureau, PRID 2319426), as fetched
        on 8 October 2026: the source of the totals the table is held against. The page is made afresh for each reader, so
        its bytes are those of that one fetch; the totals are read out of its text here, not typed.
Out     so5448e_2026-10-05_permissible_works_english_table.csv    serial, category, sub-item, work type, work name, page
        so5448e_2026-10-05_permissible_works_english_table.provenance.json

What is checked here, and the run stops if one fails:
  - the PDF on disk is the registered one (sha256);
  - 375 rows, numbered 1 to 375 without a gap, the last serial the table prints;
  - the total and the four category totals that the Ministry's press release prints for this list ("375 Permissible
    Works"; "128 works under Water Security, 111 under Core Rural Infrastructure, 98 under Livelihood-related
    Infrastructure and 38 under Disaster Preparedness"), read from the registered copy of the release;
  - THE WHOLE TABLE IN THE PDF'S OWN ORDER, CELL BY CELL. The text layer of pages 17 to 28 (pdftotext -raw; line breaks and
    runs of spaces ignored; a hyphen at a line's end joined; capitals and dashes kept) is walked once from the first row to the last:
    each row's work name must come next, with exactly its own work type before it and nothing else between it and the row
    before - except the printed running head of a page, and, where the transcription says a category or a sub-item
    begins, that heading, word for word and with its spaces as printed (a run of spaces counts as one). Straight after the last row must come the notification's file number. So a name
    on the wrong row, a cell cut short in any row (its last words would be left over), a work type on the wrong name and
    a row left out all stop the run.
  - EACH ROW'S TWO CELLS, WHOLE, FROM WHERE THE WORDS STAND ON THE PAGE. The walk cannot see where a work type ends and
    its name begins, nor where one row ends and the next begins: the text layer runs the cells together. Both are taken
    from the positions of the words (pdftotext -bbox-layout). Every row must begin on the page the transcription gives
    it, below the row before, on a line where the first word of its work type stands at the left edge of the table's
    second column and the first word of its work name at the left edge of the third (the same two edges on every page,
    to 3 points). Then every word from that line down to the line the next row begins on - stopping at a heading, a
    page's running head or the end of the table - is put in the work type if it stands left of the line between the two
    columns and in the work name if not, and the two cells so read must be the transcription's, word for word.
  - no work type and no work name is blank.
Tried on deliberate errors put into a copy of the transcription, each of which stops the run (the session's record of
the trials lists them): names changed over, a name cut short, a wrong work type, a word moved across the line between
the two cells either way, rows run together and split, a row given another page, a capital, a dash, a space in a heading.
What is NOT checked here: the digits of the serial numbers against the PDF (they cannot be read by machine: see above).
What the walk does establish is that the n-th row of the printed table is the n-th row here; that the printed numbers run
1 to 375 with no gap rests on the transcriber's reading of the page images. Also not checked: the Hindi half of the
notification; whether the list has been amended since 8 October 2026.
"""
import csv, datetime, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF = HERE / "egazette_276796_SO5448E_2026-10-05_list_of_permissible_works.pdf"
TXT = HERE / "so5448e_2026-10-05_permissible_works_verbatim_transcription.txt"
OUT = HERE / "so5448e_2026-10-05_permissible_works_english_table.csv"
SHA256 = "ec89d3a85bf49f1a4218b897c1daca2b3ab86d71b42f8f52c2d9860b6e0279a4"
URL = "https://egazette.gov.in/WriteReadData/2026/276796.pdf"
PIB = HERE / "pib_2319426_2026-10-06_ministry_notifies_375_permissible_works.html"
PIB_URL = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2319426"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def stop(m):
    sys.exit("NOT WRITTEN: " + m)


def norm(s):
    s = re.sub(r"-\s*\n\s*", "-", s)                        # a hyphen at a line's end: the word goes on
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()        # capitals and dashes are kept: the comparison is of the characters as printed


if sha(PDF) != SHA256:
    stop(f"{PDF.name} is not the registered file (sha256 {sha(PDF)})")
if not PIB.is_file():
    stop(f"{PIB.name} is not there: the Ministry's own totals are read from it ({PIB_URL})")
import html as _html
release = " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", PIB.read_text(encoding="utf-8", errors="replace")))).split())
m_total = re.search(r"Notifies (\d+) Permissible Works under VB.G RAM G", release)
m_cats = re.search(r"(\d+) works under Water Security, (\d+) under Core Rural Infrastructure, (\d+) under Livelihood-related Infrastructure and (\d+) under Disaster Preparedness", release)
if not m_total or not m_cats or "Ministry of Rural Development" not in release:
    stop(f"{PIB.name} does not carry the sentence with the Ministry's totals")
PUBLISHED = dict(zip(("I", "II", "III", "IV"), (int(x) for x in m_cats.groups())))        # the Ministry's own totals, read from its release
PUBLISHED_TOTAL = int(m_total.group(1))
rows, cat, cat_head, sub, sub_head, page = [], "", "", "", "", ""
for line in TXT.read_text(encoding="utf-8").splitlines():
    if line.startswith("#") or not line.strip():
        continue
    m = re.match(r"\[page (\d+)\]", line)
    if m:
        page = m.group(1)
        continue
    m = re.match(r"Category (I{1,3}|IV)\s*[—-]\s*(.*)", line)
    if m:
        cat, cat_head, sub, sub_head = m.group(1), line.strip(), "", ""
        continue
    m = re.match(r"\((i{1,3}|iv|v|vi{1,3}|ix)\) (.*)", line)
    if m and " | " not in line:
        sub, sub_head = m.group(1), m.group(2).strip()
        continue
    parts = [p.strip() for p in line.split(" | ")]
    if len(parts) == 3 and parts[0].isdigit():
        rows.append({"serial": int(parts[0]), "category": cat, "category_heading": cat_head, "sub_item": sub, "sub_item_heading": sub_head, "work_type": parts[1], "work_name": parts[2], "gazette_page": page})
if [r["serial"] for r in rows] != list(range(1, 376)):
    stop(f"{len(rows)} rows, or the serial numbers do not run 1 to 375")
if len(rows) != PUBLISHED_TOTAL or sum(PUBLISHED.values()) != PUBLISHED_TOTAL:
    stop(f"{len(rows)} rows; the Ministry's release says {PUBLISHED_TOTAL} works, and its four categories add to {sum(PUBLISHED.values())}")
counts = {c: sum(1 for r in rows if r["category"] == c) for c in PUBLISHED}
if counts != PUBLISHED:
    stop(f"rows by category {counts} are not the Ministry's published totals {PUBLISHED}")
if any(not r["category"] or not r["sub_item"] or not r["gazette_page"] for r in rows):
    stop("a row has no category, sub-item or page")
blank = [r["serial"] for r in rows if not r["work_type"].strip() or not r["work_name"].strip()]
if blank:
    stop(f"rows {blank[:5]} have a blank work type or work name")
try:
    pages = {p: norm(subprocess.run(["pdftotext", "-raw", "-f", str(p), "-l", str(p), str(PDF), "-"], capture_output=True, text=True, check=True).stdout) for p in range(17, 29)}
except (FileNotFoundError, subprocess.CalledProcessError) as e:
    stop(f"pdftotext could not read the PDF: {e}")
missing = []
for r in rows:
    near = " ".join(pages.get(int(r["gazette_page"]) + d, "") for d in (-1, 0, 1))          # a row at a page break may sit on either side of it
    for field in ("work_name", "work_type"):
        if norm(r[field]) not in near:
            missing.append((r["serial"], field, r[field]))
if missing:
    stop(f"{len(missing)} fields of the transcription are not in the PDF's text layer word for word, e.g. {missing[:5]}")
# the whole table in the PDF's own order: one walk through the text of pages 17 to 28
full = " ".join(pages[p] for p in range(17, 29))
squash = lambda s: re.sub(r"\s+", "", s)
HEADS = (r"THE GAZETTE OF INDIA : EXTRAORDINARY \[PART II—SEC ii\)\]", r"\[भाग II—खण्ड 3\(ii\)\] भारत का रािपत्र : असाधारण")       # the running heads of the pages, as the text layer has them
pos, walk = 0, []
for k, r in enumerate(rows):
    ty, nm = norm(r["work_type"]), norm(r["work_name"])
    i = full.find(nm, pos)
    if i < 0:
        stop(f"Sl. {r['serial']}: its work name does not come after that of Sl. {r['serial'] - 1} in the PDF's text: a row is out of order, missing, or not as printed")
    between = full[pos:i].strip()
    if not between.endswith(ty):
        stop(f"Sl. {r['serial']}: the text before its name does not end with its work type '{r['work_type']}': {between[-120:]!r}")
    rest = between[:len(between) - len(ty)].strip()
    for h in HEADS:
        rest = re.sub(h, " ", rest)
    new_cat = k == 0 or r["category"] != rows[k - 1]["category"]
    new_sub = new_cat or r["sub_item"] != rows[k - 1]["sub_item"]
    want = " ".join(x_ for x_ in (norm(r["category_heading"]) if new_cat else "", f"({r['sub_item']}) " + norm(r["sub_item_heading"]) if new_sub else "") if x_)
    if k == 0:
        if not norm(rest).endswith(want):                    # before the first row lie the Hindi table and the English title: only the end is held, the two headings
            stop(f"Sl. 1: the text before it does not end with its category and sub-item headings: {rest[-200:]!r}")
    elif norm(rest) != want:
        stop(f"Sl. {r['serial']}: between the row before and this one the PDF has {rest!r}, and the transcription expects {want!r}: a cell is cut short, or a heading is not as printed")
    walk.append((new_cat, new_sub))
    pos = i + len(nm)
if not full[pos:].strip().startswith("[F. No."):
    stop(f"straight after the last row the PDF does not go on with the notification's file number - the last name is cut short, or something follows it: {full[pos:pos + 80]!r}")
# where a work type ends and its name begins: from the positions of the words on the page
import collections
try:
    xml = subprocess.run(["pdftotext", "-bbox-layout", "-f", "17", "-l", "28", str(PDF), "-"], capture_output=True, text=True, check=True).stdout
except (FileNotFoundError, subprocess.CalledProcessError) as e:
    stop(f"pdftotext could not give the positions of the words: {e}")
words = collections.defaultdict(list)                       # page -> [(left edge of the word, top of its line, the word)]
for k, pg in enumerate(re.split(r"<page ", xml)[1:]):
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">(.*?)</word>', pg):
        words[17 + k].append((float(m.group(1)), float(m.group(2)), _html.unescape(m.group(3))))
EDGES = {"work_type": 131, "work_name": 265}                # the left edges of the table's second and third columns, in points: the same on every page
SPLIT = 262                                                 # a word whose left edge is left of this is in the second column; from it on, in the third
first = lambda s: s.replace("\u00a0", " ").split()[0]
lines_of = {}                                               # page -> [(top of the line, [(left edge, word), ...] left to right)], down the page
for pg_, ws_ in words.items():
    ls_ = collections.defaultdict(list)
    for x, y, w in ws_:
        ls_[next((k_ for k_ in ls_ if abs(k_ - y) <= 2), y)].append((x, w))
    lines_of[pg_] = sorted((y, sorted(v)) for y, v in ls_.items())
HEADING = re.compile(r"\((i{1,3}|iv|v|vi{1,3}|ix)\)")


def cell_text(lines):
    """The words of one cell, line after line, as norm() joins them: a hyphen at a line's end joins the next line to it."""
    out = ""
    for ws_ in lines:
        if ws_:
            piece = " ".join(ws_)
            out = out + piece if out.endswith("-") and not out.endswith(" -") else (out + " " + piece if out else piece)
    return norm(out)


off, starts, prev = [], [], (None, -1.0)
for r in rows:                                              # 1. where each row BEGINS: on its own page, below the row before, both cells on one line at their columns' edges
    pg = int(r["gazette_page"])
    ys_t = [y for x, y, w in words[pg] if w == first(r["work_type"]) and abs(x - EDGES["work_type"]) <= 3]
    ys_n = [y for x, y, w in words[pg] if w == first(r["work_name"]) and abs(x - EDGES["work_name"]) <= 3]
    below = prev[1] if prev[0] == pg else -1.0
    line = sorted(y for y in ys_t if y > below + 2 and any(abs(y - y2) <= 2 for y2 in ys_n))
    if not line:
        off.append((r["serial"], pg, "no line begins with the first words of its two cells"))
        starts.append(None)
        continue
    prev = (pg, line[0])
    starts.append(prev)
for k, r in enumerate(rows):                                # 2. each row's two cells WHOLE: every word from its first line down to the next row's first line, split at the line between the columns
    if starts[k] is None:
        continue
    pg, y0 = starts[k]
    nxt = starts[k + 1] if k + 1 < len(rows) else None
    y1 = nxt[1] if nxt and nxt[0] == pg else 1e9
    ty, nm = [], []
    for y, ws_ in lines_of[pg]:
        if y < y0 - 2 or y >= y1 - 2:
            continue
        if not (abs(ws_[0][0] - EDGES["work_type"]) <= 3 or abs(ws_[0][0] - EDGES["work_name"]) <= 3) or HEADING.fullmatch(ws_[0][1]) or ws_[0][1] == "Category":
            break                                           # a heading, a page's running head or what follows the table: the row has ended
        ty.append([w for x, w in ws_ if x < SPLIT])
        nm.append([w for x, w in ws_ if x >= SPLIT])
    got = (cell_text(ty), cell_text(nm))
    if got != (norm(r["work_type"]), norm(r["work_name"])):
        off.append((r["serial"], pg, f"by the positions of the words its cells read {got}"))
if off:
    stop(f"{len(off)} rows are not, by the positions of the words on the page the transcription gives them, the two cells the transcription has ({EDGES}): the line between a work type and its name, a row's page, "
         f"or the rows themselves are not as printed, e.g. {off[:3]}")
edges = EDGES
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
json.dump({"script": "00_raw/06_scheme/_build_schedule_extract.py", "run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "inputs": [{"path": "00_raw/06_scheme/" + p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in (PDF, TXT, PIB)], "source_url": URL, "totals_url": PIB_URL,
           "document": "Ministry of Rural Development notification S.O. 5448(E), 5 October 2026; Gazette of India, Extraordinary, Part II, Section 3(ii), No. 5238; Gazette ID CG-DL-E-05102026-276796",
           "checks_passed": {"rows": len(rows), "serials_run_1_to_375": True, "rows_by_category_equal_the_ministrys_published_totals": counts, "rows_equal_the_ministrys_published_total": PUBLISHED_TOTAL,
                             "rows_walked_in_the_pdfs_own_order_each_work_type_and_name_whole_and_on_its_own_row": len(rows), "sub_item_headings_met_on_the_way_and_held_word_for_word": sum(1 for c_, s_ in walk if s_),
                             "category_headings_met_on_the_way_and_held_word_for_word": sum(1 for c_, s_ in walk if c_), "capitals_are_compared": True, "dashes_are_compared": True,
                             "rows_that_begin_on_their_own_page_below_the_row_before_with_both_cells_on_one_line_at_their_columns_left_edges": sum(1 for s_ in starts if s_ is not None),
                             "rows_whose_two_cells_read_whole_from_the_positions_of_the_words_are_the_transcriptions": len(rows) - len(off), "spaces_inside_headings_are_compared": True, "left_edges_of_the_two_columns_in_points": {"work_type": edges["work_type"], "work_name": edges["work_name"]}, "published_totals_from": "Press Information Bureau release 2319426, 6 October 2026",
                             "work_names_and_types_found_word_for_word_in_the_pdf_text_layer": 2 * len(rows)},
           "not_checked": ["the digits of the serial numbers against the PDF: they are not in its text layer and were read from the page images by the transcriber; what is established is that the n-th row printed is the n-th row here", "the Hindi half of the notification", "amendments after 8 October 2026"],
           "table": {"path": "00_raw/06_scheme/" + OUT.name, "rows": len(rows), "columns": len(rows[0]), "blank_cells": sum(1 for r in rows for v in r.values() if not str(v).strip()), "sha256": sha(OUT)}}, open(OUT.with_suffix(".provenance.json"), "w", encoding="utf-8"), indent=2)
print(f"{OUT.name}: {len(rows)} works, the total the Ministry's release prints; by category {counts}, its totals; the table walked in the PDF's own order, every work type and name whole and on its own row, {sum(1 for c_, s_ in walk if s_)} sub-item and {sum(1 for c_, s_ in walk if c_)} category headings held word for word; every row's two cells, read whole from the positions of the words on its own page, are the transcription's (column edges {edges})")
