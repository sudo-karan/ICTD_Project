#!/usr/bin/env python3
"""
Parse MGNREGA / VB-G RAM G MIS "Excel" exports.

The MIS serves these as HTML <table> markup with a .xls extension, so pandas.read_excel and
openpyxl both fail on them. This parser expands rowspan/colspan, flattens the multi-row header,
and writes a tidy CSV. Standard library only.

    python parse_mis_html_reports.py --src 00_raw/mis_reports --out 00_raw/mis_reports

Two quirks of these reports that the parser handles, and that will bite anyone writing their own:
  * the Total row is printed BOTH above and below the data rows, and its serial-number cell is
    blank, so the label sits in column 1;
  * a row of column numbers ("1 2 3 ... 9=7/8*100") sits under the real header and is not data.

Verified on four Odisha FY 2016-17 reports supplied 5 Oct 2026. Each file embeds state_name and
fin_year in its row hyperlinks; both are extracted and written into every output row.
"""
import argparse, csv, glob, html, os, re, sys
from html.parser import HTMLParser

COLNUM_RE = re.compile(r"[\d=/*+.\s-]+")


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.cur, self.cell, self.in_cell = [], None, None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.cur = []
        elif tag in ("td", "th"):
            self.in_cell = True
            self.cell = {"rowspan": int(a.get("rowspan") or 1),
                         "colspan": int(a.get("colspan") or 1), "text": []}

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.in_cell = False
            if self.cur is not None:
                self.cur.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.cur is not None:
            self.rows.append(self.cur)
            self.cur = None

    def handle_data(self, d):
        if self.in_cell and self.cell is not None:
            self.cell["text"].append(d)


def grid(rows):
    """Expand rowspan/colspan into a dense grid.

    A cell spanning several rows is written into its first row; the rows it covers are marked
    occupied and left blank, which is what flatten_header expects.
    """
    occ = {}
    for r, cells in enumerate(rows):
        c = 0
        for cell in cells:
            while (r, c) in occ:
                c += 1
            txt = re.sub(r"\s+", " ", html.unescape("".join(cell["text"]))).strip()
            for dr in range(cell["rowspan"]):
                for dc in range(cell["colspan"]):
                    occ[(r + dr, c + dc)] = txt if dr == 0 else ""
            c += cell["colspan"]
    if not occ:
        return []
    n_rows = max(k[0] for k in occ) + 1
    n_cols = max(k[1] for k in occ) + 1
    return [[occ.get((r, c), "") for c in range(n_cols)] for r in range(n_rows)]


def is_total_row(row):
    return any((v or "").strip().lower() == "total" for v in row[:2])


def is_colnum_row(row):
    """The MIS prints a row of column numbers under the header ("1 2 3 ... 7=3+4+5+6 8").
    It looks like data because it starts with "1", but every cell is numeric or an arithmetic
    note, and no cell carries a district name."""
    cells = [(v or "").strip() for v in row if (v or "").strip()]
    return len(cells) >= 3 and all(COLNUM_RE.fullmatch(c) for c in cells)


def find_header_rows(g):
    """First row that is really data: starts with a serial number, or is a Total row - and is not
    the column-number row."""
    for i, row in enumerate(g):
        if is_colnum_row(row):
            continue
        if re.fullmatch(r"\d+", (row[0] if row else "").strip()) or is_total_row(row):
            return i
    return 1


def flatten_header(g, n_header):
    width = max((len(r) for r in g), default=0)
    names = []
    for c in range(width):
        parts = []
        for r in range(n_header):
            v = g[r][c] if c < len(g[r]) else ""
            if not v or re.fullmatch(r"[\d=/*+.\s-]+", v):   # drop the column-number row
                continue
            if parts and parts[-1] == v:
                continue
            parts.append(v)
        name = " - ".join(parts).strip() or f"col_{c}"
        base, k = name, 2
        while name in names:
            name, k = f"{base}_{k}", k + 1
        names.append(name)
    return names


def params(text):
    """state_name and fin_year live in the row hyperlinks. Some reports URL-encode the trailing
    space as "+" or "%20" (ODISHA+), others leave it literal (ODISHA )."""
    st = re.search(r"state_name=([^&\"\'>]*)", text)
    fy = re.search(r"fin_year=(\d{4}-\d{2,4})", text)
    state = ""
    if st:
        state = st.group(1).replace("+", " ").replace("%20", " ")
        state = re.sub(r"\s+", " ", state).strip()
    return state, (fy.group(1) if fy else "")


def parse_file(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    p = TableParser()
    p.feed(raw)
    if not p.rows:
        raise ValueError("no <tr> rows found - is this really an MIS HTML export?")
    g = grid(p.rows)
    n_header = find_header_rows(g)
    header = flatten_header(g, n_header)
    state, fy = params(raw)
    body = []
    for row in g[n_header:]:
        row = list(row) + [""] * (len(header) - len(row))
        if any(v.strip() for v in row) and not is_colnum_row(row):
            body.append(row[: len(header)])
    return header, body, state, fy, n_header


def check_totals(header, data, totals):
    """Do the data rows sum to the printed Total row? Percentage columns are ratios, not sums."""
    if not totals or not data:
        return "no Total row printed", []
    bad = []
    for c in range(len(header)):
        if re.search(r"%|age of|percent", header[c], re.I):
            continue
        vals = []
        for r in data:
            v = r[c].replace(",", "").strip()
            if re.fullmatch(r"-?\d+(\.\d+)?", v):
                vals.append(float(v))
        tv = totals[0][c].replace(",", "").strip()
        if len(vals) == len(data) and re.fullmatch(r"-?\d+(\.\d+)?", tv):
            if abs(sum(vals) - float(tv)) > 0.05 + 1e-6 * abs(float(tv)):
                bad.append((header[c], round(sum(vals), 3), float(tv)))
    return ("data rows sum to the printed Total" if not bad else "MISMATCH vs printed Total"), bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="folder of .xls files, or a single file")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    files = [a.src] if os.path.isfile(a.src) else sorted(glob.glob(os.path.join(a.src, "*.xls")))
    if not files:
        sys.exit(f"no .xls files under {a.src}")
    os.makedirs(a.out, exist_ok=True)
    for f in files:
        try:
            header, body, state, fy, nh = parse_file(f)
        except Exception as e:
            print(f"{os.path.basename(f):<45} FAILED: {e}")
            continue
        data = [r for r in body if not is_total_row(r)]
        totals = [r for r in body if is_total_row(r)]
        stem = re.sub(r"^[0-9a-f]{8}-", "", os.path.splitext(os.path.basename(f))[0])
        name = re.sub(r"[^a-z0-9]+", "_", f"{state.lower() or 'unknown'}_{stem}_{fy or 'unknown_fy'}").strip("_") + ".csv"
        with open(os.path.join(a.out, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["state", "fin_year", "is_total_row"] + header)
            for r in body:
                w.writerow([state, fy, int(is_total_row(r))] + r)
        verdict, bad = check_totals(header, data, totals)
        numeric = [c for c in range(len(header))
                   if all(re.fullmatch(r"-?[\d,]+(\.\d+)?", r[c].strip() or "x") for r in data)]
        allzero = sum(1 for c in numeric if all(float(r[c].replace(",", "") or 0) == 0 for r in data))
        print(f"{os.path.basename(f):<45} {state or '?':<7} {fy or '?':<10} "
              f"rows={len(data):<3} totals={len(totals)} cols={len(header):<3} hdr={nh}  {verdict}")
        for b in bad:
            print(f"{'':<45}   column {b[0]!r}: rows sum to {b[1]}, printed Total says {b[2]}")
        if numeric:
            print(f"{'':<45}   {allzero} of {len(numeric)} numeric columns are entirely zero")
        print(f"{'':<45}   -> {name}")
    print("\nA report whose numeric columns are all zero means the MIS holds no data for that")
    print("report, state and financial year. That is a finding about the MIS, not a parse failure.")


if __name__ == "__main__":
    main()
