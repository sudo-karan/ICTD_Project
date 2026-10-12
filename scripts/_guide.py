#!/usr/bin/env python3
"""The guide that the page's third button opens (added 13 Oct 2026): docs/GUIDE.md turned into the page's own HTML.

    python scripts/_guide.py            a dry run: says what the guide holds and writes nothing

scripts/06_build_layer.py calls build() and carries the result in data.js as `guide_html`, beside `about_html` and
`sources_html`. The page never reads Markdown and never asks for a file of the guide: the text is turned into HTML
here, when the page is built, and each picture is carried inside that HTML as a `data:image/webp;base64,` address. So
the Guide window opens without a connection, like the other two.

docs/GUIDE.md is the one source. Its words are the owner's and none is changed here.

WHAT IS UNDERSTOOD, and nothing else (no package is used: this is the whole converter):
  a heading                  a line that begins `# `, `## ` or `### `
  a paragraph                one or more lines, joined by a space
  a list                     lines that begin `- `, or `1. `, `2. ` ... counted from one
  a pipe table               lines that begin `|`; the second is the rule under the head (`| --- | --- |`)
  a picture                  a line that is `![what it shows](guide/NAME.webp)` and nothing else; the address is read
                             from docs/, and must be a WebP file under docs/guide/
  inside a line              `code`, [words](https://address), **bold**, *italics*
EVERYTHING ELSE IS ESCAPED: a `<`, a `>` or an `&` anywhere, and any Markdown this list does not name, reaches the
page as the characters themselves. No tag of the source is passed through.

WHAT STOPS THE BUILD (each is said in the list the builder prints):
  - a picture the guide names is missing, is not under docs/guide/, or is not a WebP file;
  - a picture stands anywhere but on a line of its own;
  - a link's address does not begin `https://` (a link opens only when clicked, in a new tab; nothing else in the
    HTML carries an address);
  - a row of a table has another number of cells than its head, or a table has no rule under its head;
  - a numbered list does not count 1, 2, 3 ...;
  - the guide does not begin with its one first-level heading.
"""
import base64, hashlib, html, re, sys
from pathlib import Path

SOURCE = "docs/GUIDE.md"
PICTURES_UNDER = "guide/"                       # where the guide's pictures lie, beside it: docs/guide/
INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)|\*\*(.+?)\*\*|\*(.+?)\*")
PICTURE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
RULE = re.compile(r"\|(\s*:?-+:?\s*\|)+")
esc = lambda s: html.escape(s, quote=False)
attr = lambda s: html.escape(s, quote=True)


def webp_size(data):
    """(width, height) of a WebP file read from its own header, or None if the bytes are not a WebP file."""
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    kind = data[12:16]
    if kind == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
        return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
    if kind == b"VP8L" and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    return None


def inline(s, links, wrong):
    """One line's words as HTML: code, links, bold and italics understood, everything else escaped."""
    out, pos = [], 0
    for m in INLINE.finditer(s):
        out.append(esc(s[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<code>" + esc(m.group(1)) + "</code>")
        elif m.group(2) is not None:
            if not m.group(3).startswith("https://"):
                wrong.append(f"a link's address does not begin https://: {m.group(3)[:80]}")
            links.append(m.group(3))
            out.append(f'<a href="{attr(m.group(3))}" target="_blank" rel="noopener">' + inline(m.group(2), links, wrong) + "</a>")
        elif m.group(4) is not None:
            out.append("<strong>" + inline(m.group(4), links, wrong) + "</strong>")
        else:
            out.append("<em>" + inline(m.group(5), links, wrong) + "</em>")
        pos = m.end()
    out.append(esc(s[pos:]))
    return "".join(out)


def cells(line):
    return [c.strip() for c in line.strip()[1:-1].split("|")] if line.strip().endswith("|") else None


def convert(text, picture):
    """The guide's Markdown as HTML. picture(what it shows, address) gives the HTML of one picture, or "" to leave it out.
    Returns (the HTML, what it holds, what is wrong - a list, empty when nothing is)."""
    lines = text.splitlines()
    out, wrong, links = [], [], []
    holds = {"headings": [0, 0, 0], "paragraphs": 0, "lists": 0, "list_items": 0, "tables": 0, "table_rows": 0, "pictures_named": [], "first_heading": None}
    i, n = 0, len(lines)
    block_start = lambda s: bool(re.match(r"(#{1,3} |\||- |\d+\. )", s)) or bool(PICTURE.fullmatch(s.strip()))
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if PICTURE.search(line) and not PICTURE.fullmatch(line.strip()):
            wrong.append(f"line {i + 1}: a picture stands inside a line; a picture must be a line of its own")
        m = re.match(r"(#{1,3}) (.*)$", line)
        if m:
            k = len(m.group(1))
            if holds["first_heading"] is None:
                holds["first_heading"] = (k, m.group(2).strip())
            holds["headings"][k - 1] += 1
            out.append(f"<h{k}>" + inline(m.group(2).strip(), links, wrong) + f"</h{k}>")
            i += 1
        elif PICTURE.fullmatch(line.strip()):
            m = PICTURE.fullmatch(line.strip())
            holds["pictures_named"].append(m.group(2))
            got = picture(m.group(1), m.group(2))
            if got:
                out.append('<p class="pic">' + got + "</p>")
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            head = cells(rows[0])
            if len(rows) < 2 or not RULE.fullmatch(rows[1].strip()) or head is None:
                wrong.append(f"line {i - len(rows) + 1}: a table without a rule under its head")
                head = head or []
            body = [cells(r) for r in rows[2:]]
            for k, r in enumerate(body):
                if r is None or len(r) != len(head):
                    wrong.append(f"line {i - len(rows) + 3 + k}: a row of {0 if r is None else len(r)} cells under a head of {len(head)}")
            holds["tables"] += 1
            holds["table_rows"] += len(body)
            out.append('<div class="wide"><table><tr>' + "".join("<th>" + inline(c, links, wrong) + "</th>" for c in head) + "</tr>"
                       + "".join("<tr>" + "".join("<td>" + inline(c, links, wrong) + "</td>" for c in (r or [])) + "</tr>" for r in body) + "</table></div>")
        elif re.match(r"(- |\d+\. )", line):
            numbered = not line.startswith("- ")
            items = []
            while i < n and re.match(r"\d+\. " if numbered else r"- ", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i], count=1).strip())
                if numbered and int(lines[i].split(".", 1)[0]) != len(items):
                    wrong.append(f"line {i + 1}: a numbered list that does not count 1, 2, 3 ...")
                i += 1
            holds["lists"] += 1
            holds["list_items"] += len(items)
            tag = "ol" if numbered else "ul"
            out.append(f"<{tag}>" + "".join("<li>" + inline(x, links, wrong) + "</li>" for x in items) + f"</{tag}>")
        else:
            para = []
            while i < n and lines[i].strip() and not block_start(lines[i]):
                para.append(lines[i].strip())
                i += 1
            holds["paragraphs"] += 1
            out.append("<p>" + inline(" ".join(para), links, wrong) + "</p>")
    if holds["first_heading"] is None or holds["first_heading"][0] != 1 or holds["headings"][0] != 1 or not out[0].startswith("<h1>"):
        wrong.append("the guide does not begin with its one first-level heading")
    holds["links"] = links
    return '<div class="guide">' + "".join(out) + "</div>", holds, wrong


def build(root, also=None, fails=None, pictures=True):
    """The guide as the page carries it. also(path, role): the builder's way of recording a file it reads among its inputs (None: the file is only read).
    fails: the builder's list of what stops the build. pictures=False leaves the guide's picture lines out: for the one build the pictures are taken of,
    before they exist; the record says so, and no check passes such a build.
    Returns {"html": the text of `guide_html`, "record": what the layer's run record says of it}."""
    root, fails = Path(root), ([] if fails is None else fails)
    path = lambda p, role: Path(also(p, role)) if also else root / p
    src = path(SOURCE, "the guide: the one source of the Guide window")
    text = src.read_text(encoding="utf-8")
    seen = []

    def picture(alt, address):
        if not address.startswith(PICTURES_UNDER) or "/" in address[len(PICTURES_UNDER):] or ".." in address or not address.endswith(".webp"):
            fails.append(f"the guide names a picture that is not a .webp file under docs/{PICTURES_UNDER}: {address}")
            return ""
        if not pictures:
            return ""
        rel = "docs/" + address
        if not (root / rel).is_file():
            fails.append(f"the guide names a picture that is missing: {rel}")
            return ""
        data = path(rel, "a picture of the guide").read_bytes()
        size = webp_size(data)
        if size is None:
            fails.append(f"a picture of the guide is not a WebP file: {rel}")
            return ""
        b64 = base64.b64encode(data).decode("ascii")
        seen.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "width": size[0], "height": size[1], "what_it_shows": alt, "as_base64_characters": len(b64)})
        return f'<img src="data:image/webp;base64,{b64}" alt="{attr(alt)}" width="{size[0]}" height="{size[1]}">'

    out, holds, wrong = convert(text, picture)
    fails.extend("docs/GUIDE.md, " + w for w in wrong)
    if pictures and len({p["path"] for p in seen}) != len(holds["pictures_named"]):
        fails.append(f"the guide names {len(holds['pictures_named'])} pictures and {len({p['path'] for p in seen})} different files were read: a picture is missing or is named twice")
    record = {"source": {"path": SOURCE, "bytes": src.stat().st_size, "sha256": hashlib.sha256(src.read_bytes()).hexdigest()},
              "converter": {"path": "scripts/_guide.py", "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              "pictures_named_in_the_guide": ["docs/" + a for a in holds["pictures_named"]], "pictures_left_out_of_this_build": not pictures, "pictures": seen,
              "html": {"characters": len(out), "bytes": len(out.encode("utf-8")), "sha256": hashlib.sha256(out.encode("utf-8")).hexdigest(), "of_them_the_pictures_as_base64": sum(p["as_base64_characters"] for p in seen)},
              "holds": {"first_heading": holds["first_heading"][1] if holds["first_heading"] else None, "headings_of_level_1_2_3": holds["headings"], "paragraphs": holds["paragraphs"], "lists": holds["lists"],
                        "list_items": holds["list_items"], "tables": holds["tables"], "table_rows_under_their_heads": holds["table_rows"], "links": len(holds["links"]), "link_addresses": sorted(set(holds["links"]))},
              "how_it_reaches_the_page": "turned into HTML when the page is built and carried in data.js as guide_html; each picture inside it as a data:image/webp;base64 address; links open only when clicked, in a new tab"}
    return {"html": out, "record": record}


if __name__ == "__main__":
    stopped = []
    g = build(Path(__file__).resolve().parent.parent, None, stopped, pictures="--without-pictures" not in sys.argv)
    r = g["record"]
    print(f"{SOURCE}: {r['source']['bytes']:,} bytes, sha256 {r['source']['sha256'][:16]}...; first heading '{r['holds']['first_heading']}'")
    print(f"  holds: headings {r['holds']['headings_of_level_1_2_3']} (levels 1, 2, 3), {r['holds']['paragraphs']} paragraphs, {r['holds']['list_items']} items in {r['holds']['lists']} lists, "
          f"{r['holds']['table_rows_under_their_heads']} rows in {r['holds']['tables']} tables, {r['holds']['links']} links to {len(r['holds']['link_addresses'])} addresses, {len(r['pictures_named_in_the_guide'])} pictures named")
    for p in r["pictures"]:
        print(f"  {p['path']}: {p['width']} x {p['height']}, {p['bytes']:,} bytes ({p['as_base64_characters']:,} characters as base64), sha256 {p['sha256'][:16]}...")
    print(f"  as HTML: {r['html']['bytes']:,} bytes, of them {r['html']['of_them_the_pictures_as_base64']:,} the pictures" + ("; THE PICTURES ARE LEFT OUT" if r["pictures_left_out_of_this_build"] else ""))
    for s in stopped:
        print("  WOULD STOP THE BUILD: " + s)
    sys.exit(1 if stopped else 0)
