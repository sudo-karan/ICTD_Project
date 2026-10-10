"""Stage 4: forest rights, at the level the data allow - the district. Writes into `50_gap/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_build_gap_rights.py

DEFINITIONS (`scripts/verify_gap.py` is written from this text)

fra_by_district.csv - one row per district (30), from the Odisha FRA monthly progress report as on 31-12-2025
(`00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv`), joined on the census district code
  community_titles_distributed    `titles_distributed_comm_st` + `titles_distributed_comm_otfd`
  community_extent_ha             `extent_ha_comm_st` + `extent_ha_comm_otfd`
  forest_2000_ha, n1_ha_2018_2025, forest_at_window_start_ha_2018_2025        from `50_gap/district_need.csv`
  community_extent_pct_of_forest_2000      100 x community_extent_ha / forest_2000_ha. NOT an overlap: titles are not
                                  mapped, and "community" lumps community rights (CR) with community forest resource
                                  rights (CFR). It can exceed 100
  n1_per_100_ha_of_forest_at_window_start  100 x n1_ha_2018_2025 / forest_at_window_start_ha_2018_2025
  extent_is                       that label, on every row

fra_summary.csv - two rank correlations over the 30 districts, computed as in step 2 (Spearman's rho with average
ranks, a two-sided permutation p from 99,999 shuffles, a percentile bootstrap 95 % interval from 9,999 draws of
districts, seeds recorded)
  R1   community_extent_ha  against  n1_ha_2018_2025
  R2   community_extent_pct_of_forest_2000  against  n1_per_100_ha_of_forest_at_window_start

fra_two_reports.csv - the same date in two reports: the state's (the district file summed) and Odisha's row of the
national report of the Ministry of Tribal Affairs (`00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv`, columns
`titles_distributed_community` and `extent_ha_community`), and the difference (state less national; for the extent
also as a per cent of the state's figure).

forest_villages_pdf_record.json, forest_villages_text_layer_check.csv and
forest_villages_districts_as_the_layer_reads_them.csv - the ST & SC Development Department's "List of Forest Villages,
Old Habitations or Settlements & Unsurveyed Villages". The PDF is a fetched file, in `00_raw/01_cfr_fra/`, registered
by the manifest row `forest_villages_pdf_as_fetched`. It is a scan: every page is one image, and the only text in the
file is a layer made by someone else's character recognition (the file's producer). This step recognises no text
itself.

THE OWNER'S RULE (10 October 2026). That layer is unverified. It is used only if both of these hold:
  (a) the district counts parsed from it equal every total and running serial number the PDF prints, exactly;
  (b) at least five pages chosen at random are rendered upright and read by a reader, and every row on them matches
      the parsed rows.
If either fails, or the PDF prints nothing to check against, the step records the page count, the layer and which
check failed, and stops: no count is taken and nothing is added to `district_need.csv`. Check (b) is a reader's work,
not a script's; it is done only if (a) holds, and this script stops with a message if (a) ever does.

How the layer is read (the text is `pdftotext -layout`, one page at a time; nothing else is read):
  * the summary page is the first of the first six pages whose text, white space collapsed, has the heading
    "List of Forest / Un-Surveyed Villages in the Districts". A row of it is a line that ends in three whole numbers,
    with nothing but white space and marks between them: revenue villages, "ZERO" area villages, total inhabited
    villages. A total row is a row whose label has the word "total".
  * a district page is a page whose text has "Total Number of Villages" or "Revenue Villages (Surveyed". Its three
    numbers are the digits that follow "Total Number of Villages", "Revenue Villages (Surveyed villages)" and
    "Settlements etc.)", marks between; one that cannot be found is blank. A district is a district page and the
    pages after it up to the next district page.
  * a village code is a run of exactly eight digits. A row of a district's list is a line of its pages that holds a
    village code. A serial number is a whole number from 1 to 999 that begins a line (marks before it apart) and is
    followed by nothing, by a village code, or by a word with a letter in it, on a line without the word "Total".

forest_villages_text_layer_check.csv - the summary page as the layer reads it, a row a line:
  page, line_as_read, label_as_read, revenue_villages, zero_area_villages, total_inhabited_villages,
  adds_up (yes where the first two add to the third), is_a_total_row

forest_villages_districts_as_the_layer_reads_them.csv - one row for each district of the file, in its order:
  order_in_file, district_page, list_pages (the pages of the district that hold a village code, separated by spaces),
  page_total_inhabited, page_revenue_villages, page_zero_area_villages (the district page's three numbers; blank
  where the layer does not give one), page_adds_up (yes / no; blank where a number is missing),
  page_equals_a_summary_row (yes where the three numbers are those of a row of the summary page; blank where a number
  is missing), rows_with_a_village_code, rows_equal_the_page_s_zero_area_count (yes / no; blank where that number is
  missing), serial_numbers_read (how many distinct ones), last_serial_number_read,
  serial_numbers_not_read (those from 1 to the page's zero-area count that were not read, separated by spaces; blank
  where that number is missing), serial_number_1_read_more_than_once (yes where the list is numbered in more than one
  run, as a list numbered block by block is; this step does not follow such numbering),
  serial_numbers_are_1_to_the_count (yes only where the distinct serial numbers read are exactly 1 to the page's
  zero-area count)

Check (a) has six parts, and holds only if every one holds for every row it is asked of:
  a1  every row of the summary page adds up
  a2  a total row of the summary page is read, and each of its three numbers is the sum of its column
  a3  every district page gives its three numbers, and they add up
  a4  every district page's three numbers are those of a row of the summary page
  a5  every district's rows with a village code number what its page prints for the "ZERO" area
  a6  every district's serial numbers are exactly 1 to that count
The record gives, for each part, in how many rows it holds and of how many.

forest_villages_pdf_record.json: path, bytes, sha256; examined; pages; creator and producer (the software that made
the scan and its text layer); pages_that_are_one_image; image_pixels_per_inch; pages_rotated (page: degrees, for the
pages `pdfinfo` reports as rotated); fonts_named_in_the_file; characters_of_text_in_the_file (the length of
`pdftotext`'s default output with the white space at its two ends removed); poppler; summary_page;
summary_rows_read, summary_rows_that_add_up, summary_rows_that_do_not (the lines), printed_total_row_read,
zero_area_villages_summed_over_the_rows_read; districts_in_the_file; check_a (`holds`, and `parts`: for each of a1 to
a6 what it asks, `holds_in`, `of`); check_b (`run`, and why not); which_check_failed; text_usable_for_counts;
note_from_one_page_read_by_eye (words only: what one reader saw on the summary page as rendered; it is not check (b));
conclusion; checked_utc.

gates_phase5.csv, and this step's section of `gap.provenance.json`.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D, dsum  # noqa: E402

STEP = "08_build_gap_rights"
SEED = 20261010
EXTENT_IS = "not an overlap: titles are not mapped, and 'community' lumps CR with CFR"
PDF = G.ROOT / "00_raw/01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf"
SUMMARY_HEADING = "List of Forest / Un-Surveyed Villages in the Districts"


def q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def tool(*args: str) -> str:
    return subprocess.run(list(args), capture_output=True, text=True, timeout=300).stdout


CODE = re.compile(r"(?<!\d)\d{8}(?!\d)")
# The summary page of the file with this SHA-256 was rendered and read once, by the session that wrote this step on
# 10 October 2026, to see what kind of failure the layer's bad row is. The note is attached to that file and to no other.
READ_BY_EYE_SHA256 = "6a7a4657b15b7afdd12f7d76a1e58163bb62bb5a2c9a5f5ee762eb59ec98bcc7"
NOTE_BY_EYE = ("The summary page, rendered at its own orientation, was read once by the session that wrote this step (10 October 2026). On the page "
               "every row is legible and the third row's total is printed plainly and equals its two parts: the row that fails here is a "
               "misreading by the layer, not an error of the print. Under the table the page carries the totals of the three columns written "
               "by hand, which the layer does not hold. This is one page, not chosen at random: it is not check (b).")


def page_text(p: int) -> str:
    return tool("pdftotext", "-f", str(p), "-l", str(p), "-layout", str(PDF), "-")


def serial_of(line: str):
    """The serial number a line of a list begins with, by the rule of the docstring; None if it begins with none."""
    if re.search(r"total", line, re.I):
        return None
    m = re.match(r"^\W*(\d{1,3})(?!\d)(.*)$", line)
    if not m or int(m.group(1)) < 1:
        return None
    rest = m.group(2).split()
    after = rest[0] if rest else ""
    if after == "" or CODE.fullmatch(after) or re.search(r"[A-Za-z]", after):
        return int(m.group(1))
    return None


def forest_villages(gates) -> tuple[dict, list[dict], list[dict]]:
    """What the file is, and whether its text layer passes the owner's check (a). Recognises no text itself."""
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    record = {"path": G.rel(PDF), "bytes": PDF.stat().st_size, "sha256": G.sha256(PDF)}
    manifest = [r for r in G.read_rows(G.IN["manifest"]) if (r.get("dest") or "") == "01_cfr_fra/" + PDF.name]
    registered = [r for r in manifest if (r.get("bytes") or "") == str(record["bytes"]) and (r.get("bytes_exact") or "") == "Y"
                  and record["sha256"] in " ".join(v or "" for v in r.values())]
    add("the forest villages PDF is the registered file: a row of 00_raw/data_manifest.csv names it with its exact size and SHA-256", "one row", f"{len(registered)} row(s)", len(registered) == 1)
    missing = [x for x in ("pdfinfo", "pdfimages", "pdffonts", "pdftotext") if shutil.which(x) is None]
    if missing:
        G.stop(f"the poppler tools are not installed ({', '.join(missing)}): the forest villages PDF cannot be examined")
    info = dict(l.split(":", 1) for l in tool("pdfinfo", str(PDF)).splitlines() if ":" in l)
    pages = int(info["Pages"].strip())
    rotated = {}
    for l in tool("pdfinfo", "-f", "1", "-l", str(pages), str(PDF)).splitlines():
        m = re.match(r"Page\s+(\d+) rot:\s+(\d+)", l)
        if m and int(m.group(2)) != 0:
            rotated[m.group(1)] = int(m.group(2))
    images = [l.split() for l in tool("pdfimages", "-list", str(PDF)).splitlines()[2:] if l.strip()]
    per_page = {}
    for im in images:
        per_page.setdefault(int(im[0]), []).append(im)
    ppi = sorted({im[12] for im in images})
    fonts = [l for l in tool("pdffonts", str(PDF)).splitlines()[2:] if l.strip()]
    text_chars = len(tool("pdftotext", str(PDF), "-").strip())
    record.update({"examined": True, "pages": pages, "creator": info.get("Creator", "").strip(), "producer": info.get("Producer", "").strip(),
                   "pages_that_are_one_image": sum(1 for p in range(1, pages + 1) if len(per_page.get(p, [])) == 1),
                   "image_pixels_per_inch": ppi, "pages_rotated": rotated, "fonts_named_in_the_file": len(fonts), "characters_of_text_in_the_file": text_chars,
                   "poppler": tool("pdftotext", "-v") or subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]})
    text = {p: page_text(p) for p in range(1, pages + 1)}

    # the summary page, as the layer reads it
    summary_page = next((p for p in range(1, min(pages, 6) + 1) if SUMMARY_HEADING in " ".join(text[p].split())), None)
    rows = []
    if summary_page:
        for line in text[summary_page].splitlines():
            m = re.search(r"(\d+)\D*?\s+(\d+)\s+\D*?(\d+)\s*$", line)
            if not m or len(re.findall(r"\d+", line)) < 3:
                continue
            a, b, c = (int(x) for x in m.groups())
            label = " ".join(line[:m.start()].split())
            rows.append({"page": summary_page, "line_as_read": " ".join(line.split()), "label_as_read": label, "revenue_villages": a,
                         "zero_area_villages": b, "total_inhabited_villages": c, "adds_up": "yes" if a + b == c else "no",
                         "is_a_total_row": "yes" if re.search(r"total", label, re.I) else "no"})
    body = [r for r in rows if r["is_a_total_row"] == "no"]
    total = [r for r in rows if r["is_a_total_row"] == "yes"]
    ok_rows = sum(1 for r in body if r["adds_up"] == "yes")
    triples = {(r["revenue_villages"], r["zero_area_villages"], r["total_inhabited_villages"]) for r in body}
    total_holds = len(total) == 1 and all(total[0][k] == sum(r[k] for r in body) for k in ("revenue_villages", "zero_area_villages", "total_inhabited_villages"))

    # the districts, as the layer reads them
    districts, cur = [], None
    for p in range((summary_page or 0) + 1, pages + 1):
        t = text[p]
        if "Total Number of Villages" in t or "Revenue Villages (Surveyed" in t:
            grab = lambda pattern: (lambda m: int(m.group(1)) if m else None)(re.search(pattern, t))
            cur = {"district_page": p, "total": grab(r"Total Number of Villages\W*(\d+)"), "revenue": grab(r"Revenue Villages \(Surveyed villages\)\W*(\d+)"),
                   "zero": grab(r"Settlements etc\.\)\W*(\d+)"), "list_pages": [], "rows": 0, "serials": []}
            districts.append(cur)
            continue
        lines = t.splitlines()
        if cur is None or not any(CODE.search(l) for l in lines):
            continue
        cur["list_pages"].append(p)
        cur["rows"] += sum(1 for l in lines if CODE.search(l))
        cur["serials"] += [s for s in (serial_of(l) for l in lines) if s is not None]
    drows = []
    for k, d in enumerate(districts, 1):
        three = None not in (d["total"], d["revenue"], d["zero"])
        distinct = sorted(set(d["serials"]))
        n = d["zero"]
        drows.append({"order_in_file": k, "district_page": d["district_page"], "list_pages": " ".join(str(x) for x in d["list_pages"]),
                      "page_total_inhabited": d["total"], "page_revenue_villages": d["revenue"], "page_zero_area_villages": d["zero"],
                      "page_adds_up": None if not three else ("yes" if d["revenue"] + d["zero"] == d["total"] else "no"),
                      "page_equals_a_summary_row": None if not three else ("yes" if (d["revenue"], d["zero"], d["total"]) in triples else "no"),
                      "rows_with_a_village_code": d["rows"],
                      "rows_equal_the_page_s_zero_area_count": None if n is None else ("yes" if d["rows"] == n else "no"),
                      "serial_numbers_read": len(distinct), "last_serial_number_read": distinct[-1] if distinct else None,
                      "serial_numbers_not_read": None if n is None else " ".join(str(x) for x in range(1, n + 1) if x not in distinct),
                      "serial_number_1_read_more_than_once": "yes" if d["serials"].count(1) > 1 else "no",
                      "serial_numbers_are_1_to_the_count": "yes" if n is not None and distinct == list(range(1, n + 1)) else "no"})
    nd = len(drows)
    yes = lambda key: sum(1 for r in drows if r[key] == "yes")
    parts = [
        {"part": "a1", "asks": "every row of the summary page adds up", "holds_in": ok_rows, "of": len(body)},
        {"part": "a2", "asks": "a total row of the summary page is read, and each of its three numbers is the sum of its column", "holds_in": 1 if total_holds else 0, "of": 1},
        {"part": "a3", "asks": "every district page gives its three numbers, and they add up", "holds_in": yes("page_adds_up"), "of": nd},
        {"part": "a4", "asks": "every district page's three numbers are those of a row of the summary page", "holds_in": yes("page_equals_a_summary_row"), "of": nd},
        {"part": "a5", "asks": "every district's rows with a village code number what its page prints for the \"ZERO\" area", "holds_in": yes("rows_equal_the_page_s_zero_area_count"), "of": nd},
        {"part": "a6", "asks": "every district's serial numbers are exactly 1 to that count", "holds_in": yes("serial_numbers_are_1_to_the_count"), "of": nd},
    ]
    a_holds = bool(body) and nd > 0 and len(body) == nd and all(x["holds_in"] == x["of"] for x in parts)
    failed_parts = [x["part"] for x in parts if x["holds_in"] != x["of"]]
    record.update({"summary_page": summary_page, "summary_rows_read": len(body), "summary_rows_that_add_up": ok_rows,
                   "summary_rows_that_do_not": [r["line_as_read"] for r in body if r["adds_up"] == "no"],
                   "printed_total_row_read": len(total), "zero_area_villages_summed_over_the_rows_read": sum(r["zero_area_villages"] for r in body),
                   "districts_in_the_file": nd,
                   "rule": "the owner's, 10 October 2026: the layer is used only if (a) the district counts parsed from it equal every total and running serial "
                           "number the PDF prints, exactly, and (b) at least five pages chosen at random, rendered upright and read by a reader, match the "
                           "parsed rows row for row; if either fails, record the page count, the layer and which check failed, and stop",
                   "check_a": {"holds": a_holds, "parts": parts, "parts_that_fail": failed_parts},
                   "check_b": {"run": False, "why": "check (a) holds, so a reader has to do check (b) before anything is taken" if a_holds else
                               "check (a) had already failed, and the rule stops the step at the first check that fails"},
                   "which_check_failed": None if a_holds else "(a)", "text_usable_for_counts": False})
    if record["sha256"] == READ_BY_EYE_SHA256:
        record["note_from_one_page_read_by_eye"] = NOTE_BY_EYE
    record["conclusion"] = (
        "check (a) holds for the layer; check (b), a reader's, has not been done, so nothing is taken yet" if a_holds else
        f"the file is a scan of {pages} pages, every page one image at {'/'.join(ppi)} pixels per inch, and the only text it carries is a layer made by "
        f"the scanner's character recognition ({record['producer']}). That layer fails check (a) of the owner's rule, in its parts {', '.join(failed_parts)}: "
        "what it reads does not equal every total and running serial number the file prints. Check (b) was not run. So no count is taken from the "
        "file and nothing is added to district_need.csv. No character recognition was run here, and the list is not matched to units")
    add("the forest villages PDF: pages, and pages that are one scanned image", "every page one image", f"{pages} pages, {record['pages_that_are_one_image']} of them one image",
        record["pages_that_are_one_image"] == pages)
    if a_holds:
        G.stop("the forest villages PDF's text layer passed check (a): check (b) has to be done by a reader (five pages chosen at random, rendered "
               "upright, every row against the parsed rows) before this step can go on")
    add("the forest villages PDF: district counts taken from its text layer into district_need.csv (the owner's rule: only if checks (a) and (b) both hold)",
        "none unless both hold", "none: check (a) fails ("
        + "; ".join(f"{x['part']} holds in {x['holds_in']} of {x['of']}" for x in parts) + "); check (b) not run", True)
    return record, rows, drows


def main() -> None:
    G.require_stage4_environment()
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    inputs = {"fra_district": G.IN["fra_district"], "fra_mota": G.IN["fra_mota"], "district_need": G.OUT / "district_need.csv",
              "forest_villages_pdf": PDF, "manifest": G.IN["manifest"]}
    for p in inputs.values():
        if not p.exists():
            G.stop(f"an input is missing: {G.rel(p)}")
    need = {r["pc11_district_code"]: r for r in G.read_rows(inputs["district_need"])}
    fra = G.read_rows(inputs["fra_district"])
    if {r["pc11_district_code"] for r in fra} != set(need):
        G.stop("the FRA district table and district_need.csv do not hold the same 30 districts")
    rows = []
    for r in sorted(fra, key=lambda r: r["pc11_district_code"]):
        n = need[r["pc11_district_code"]]
        if n["district_name"] != r["district"]:
            G.stop(f"district name differs for code {r['pc11_district_code']}")
        titles = int(r["titles_distributed_comm_st"]) + int(r["titles_distributed_comm_otfd"])
        extent = D(r["extent_ha_comm_st"]) + D(r["extent_ha_comm_otfd"])
        f2000, n1, start = D(n["forest_2000_ha"]), D(n["n1_ha_2018_2025"]), D(n["forest_at_window_start_ha_2018_2025"])
        rows.append({"pc11_district_code": r["pc11_district_code"], "district_name": r["district"], "community_titles_distributed": titles,
                     "community_extent_ha": extent, "forest_2000_ha": f2000, "community_extent_pct_of_forest_2000": q(100 * extent / f2000, "0.000001"),
                     "extent_is": EXTENT_IS, "n1_ha_2018_2025": n1, "forest_at_window_start_ha_2018_2025": start,
                     "n1_per_100_ha_of_forest_at_window_start": q(100 * n1 / start, "0.000001")})
    t_titles, t_extent = sum(r["community_titles_distributed"] for r in rows), dsum(r["community_extent_ha"] for r in rows)
    add("FRA community titles distributed, state (the gate of step 0)", 9432, t_titles, t_titles == 9432)
    add("FRA community extent, state, ha (the gate of step 0)", "331568", format(t_extent, "f"), t_extent == 331568)
    none = sorted(r["district_name"] for r in rows if r["community_titles_distributed"] == 0)
    add("districts with no community title distributed", 6, f"{len(none)}: {', '.join(none)}", len(none) == 6)

    f = lambda key: [float(r[key]) for r in rows]
    summary = []
    for k, (rid, a, b, words) in enumerate((
            ("R1", "community_extent_ha", "n1_ha_2018_2025", "community extent (ha) against N1 of 2018-2025 (ha)"),
            ("R2", "community_extent_pct_of_forest_2000", "n1_per_100_ha_of_forest_at_window_start",
             "community extent per 100 ha of the forest of 2000 against N1 per 100 ha of forest at the start of 2018"))):
        st = G.spearman_with_inference(f(a), f(b), SEED + 700 + k, SEED + 800 + k)
        summary.append({"id": rid, "what": words, "x": a, "y": b, "n_districts": st["n"], "rho": round(st["rho"], 6), "p_permutation": st["p_permutation"],
                        "ci95_lo": round(st["ci95_lo"], 6), "ci95_hi": round(st["ci95_hi"], 6), "n_permutations": st["n_permutations"],
                        "n_bootstrap": st["n_bootstrap"], "n_bootstrap_undefined": st["n_bootstrap_undefined"],
                        "seed_permutation": st["seed_permutation"], "seed_bootstrap": st["seed_bootstrap"], "extent_is": EXTENT_IS})

    mota = [r for r in G.read_rows(inputs["fra_mota"]) if r["state"] == "Odisha"]
    if len(mota) != 1:
        G.stop("the national report's table does not have one row for Odisha")
    m_titles, m_extent = int(mota[0]["titles_distributed_community"]), D(mota[0]["extent_ha_community"])
    two = [{"report": "Odisha state report, as on 31-12-2025 (the district table summed)", "community_titles_distributed": t_titles, "community_extent_ha": t_extent, "extent_difference_pct_of_state": None},
           {"report": "Ministry of Tribal Affairs national report, as on 31-12-2025 (Odisha's row)", "community_titles_distributed": m_titles, "community_extent_ha": m_extent, "extent_difference_pct_of_state": None},
           {"report": "difference: state less national", "community_titles_distributed": t_titles - m_titles, "community_extent_ha": t_extent - m_extent,
            "extent_difference_pct_of_state": q(100 * (t_extent - m_extent) / t_extent, "0.01")}]
    add("the two FRA reports of the same date differ (the README's 80 titles and 4,469 ha, here from the files)", "80 titles; 4469 ha",
        f"{t_titles - m_titles} titles; {format(q(t_extent - m_extent, '1'), 'f')} ha", t_titles - m_titles == 80 and q(t_extent - m_extent, "1") == 4469)

    record, check_rows, district_rows = forest_villages(gates)
    G.write_rows(G.OUT / "fra_by_district.csv", rows,
                 ["pc11_district_code", "district_name", "community_titles_distributed", "community_extent_ha", "forest_2000_ha",
                  "community_extent_pct_of_forest_2000", "extent_is", "n1_ha_2018_2025", "forest_at_window_start_ha_2018_2025",
                  "n1_per_100_ha_of_forest_at_window_start"])
    G.write_rows(G.OUT / "fra_summary.csv", summary,
                 ["id", "what", "x", "y", "n_districts", "rho", "p_permutation", "ci95_lo", "ci95_hi", "n_permutations", "n_bootstrap",
                  "n_bootstrap_undefined", "seed_permutation", "seed_bootstrap", "extent_is"])
    G.write_rows(G.OUT / "fra_two_reports.csv", two, ["report", "community_titles_distributed", "community_extent_ha", "extent_difference_pct_of_state"])
    G.write_rows(G.OUT / "forest_villages_text_layer_check.csv", check_rows,
                 ["page", "line_as_read", "label_as_read", "revenue_villages", "zero_area_villages", "total_inhabited_villages", "adds_up", "is_a_total_row"])
    G.write_rows(G.OUT / "forest_villages_districts_as_the_layer_reads_them.csv", district_rows,
                 ["order_in_file", "district_page", "list_pages", "page_total_inhabited", "page_revenue_villages", "page_zero_area_villages", "page_adds_up",
                  "page_equals_a_summary_row", "rows_with_a_village_code", "rows_equal_the_page_s_zero_area_count", "serial_numbers_read",
                  "last_serial_number_read", "serial_numbers_not_read", "serial_number_1_read_more_than_once", "serial_numbers_are_1_to_the_count"])
    record["checked_utc"] = G.utc_now()
    (G.OUT / "forest_villages_pdf_record.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    grows = [{"gate": g, "expected": e, "found": f_, "pass": "yes" if ok else "NO"} for g, e, f_, ok in gates]
    G.write_rows(G.OUT / "gates_phase5.csv", grows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("fra_by_district.csv", "fra_summary.csv", "fra_two_reports.csv", "forest_villages_text_layer_check.csv",
                                   "forest_villages_districts_as_the_layer_reads_them.csv", "forest_villages_pdf_record.json", "gates_phase5.csv")]
    G.record_step(STEP, Path(__file__), inputs, outputs, {
        "seeds": {"base": SEED, "R1": [SEED + 700, SEED + 800], "R2": [SEED + 701, SEED + 801], "generator": "numpy.random.default_rng"},
        "permutations": 99999, "bootstrap_resamples": 9999, "forest_villages": record,
        "gates": len(grows), "gates_passed": sum(r["pass"] == "yes" for r in grows)})
    for r in grows:
        print(("ok   " if r["pass"] == "yes" else "FAIL ") + r["gate"] + "  |  expected " + r["expected"] + "  |  found " + r["found"])
    failed = [r for r in grows if r["pass"] != "yes"]
    print(f"\n{len(grows) - len(failed)} of {len(grows)} gates passed; wrote {', '.join(G.rel(p) for p in outputs)}")
    for s in summary:
        print(f"{s['id']}: rho {s['rho']} ({s['ci95_lo']} to {s['ci95_hi']}), permutation p {s['p_permutation']:.5f}")
    print("forest villages PDF:", record["conclusion"])
    if failed:
        G.stop(f"{len(failed)} gate(s) failed; see 50_gap/gates_phase5.csv")


if __name__ == "__main__":
    main()
