"""Stage 4: forest rights, at the level the data allow - the district. Writes into `50_gap/` only.

    .venv/bin/python scripts/08_build_gap_rights.py

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

forest_villages_pdf_record.json and forest_villages_text_layer_check.csv - the ST & SC Development Department's "List of
Forest Villages, Old Habitations or Settlements & Unsurveyed Villages". The PDF is a fetched file
(`00_raw/01_cfr_fra/`). This step does NOT recognise any text itself. It asks three things of the file with the
poppler tools (`pdfinfo`, `pdfimages`, `pdffonts`, `pdftotext`): how many pages; whether each page is one scanned
image; and whether the text the file carries can be trusted for a count. For the last it reads the text of the
summary page (the page whose text has the heading "List of Forest / Un-Surveyed Villages in the Districts"), takes
every line that ends in three whole numbers as a row (revenue villages, "ZERO" area villages, total inhabited
villages), and tests each row's own arithmetic (the first two must add to the third) and looks for a total row. The
table gives each line as read with its three numbers and whether it adds up. The step's rule, fixed before the file was
opened by this script: district counts are taken into `district_need.csv` only if every row adds up, 30 districts are
read and a printed total is read and equals the column's sum; otherwise nothing is taken, and the record says why.

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


def forest_villages(gates) -> tuple[dict, list[dict]]:
    """What the file is, and whether its text can be trusted for a count. Recognises no text itself."""
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    record = {"path": G.rel(PDF), "bytes": PDF.stat().st_size, "sha256": G.sha256(PDF)}
    missing = [t for t in ("pdfinfo", "pdfimages", "pdffonts", "pdftotext") if shutil.which(t) is None]
    if missing:
        record["examined"] = False
        record["conclusion"] = f"not examined: the poppler tools are not installed ({', '.join(missing)})"
        return record, []
    info = dict(l.split(":", 1) for l in tool("pdfinfo", str(PDF)).splitlines() if ":" in l)
    pages = int(info["Pages"].strip())
    images = [l.split() for l in tool("pdfimages", "-list", str(PDF)).splitlines()[2:] if l.strip()]
    per_page = {}
    for im in images:
        per_page.setdefault(int(im[0]), []).append(im)
    ppi = sorted({im[12] for im in images})
    fonts = [l for l in tool("pdffonts", str(PDF)).splitlines()[2:] if l.strip()]
    text_chars = len(tool("pdftotext", str(PDF), "-").strip())
    record.update({"examined": True, "pages": pages, "creator": info.get("Creator", "").strip(), "producer": info.get("Producer", "").strip(),
                   "pages_that_are_one_image": sum(1 for p in range(1, pages + 1) if len(per_page.get(p, [])) == 1),
                   "image_pixels_per_inch": ppi, "fonts_named_in_the_file": len(fonts), "characters_of_text_in_the_file": text_chars,
                   "poppler": tool("pdftotext", "-v") or subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]})
    summary_page = None
    for p in range(1, min(pages, 6) + 1):
        if SUMMARY_HEADING in " ".join(tool("pdftotext", "-f", str(p), "-l", str(p), "-layout", str(PDF), "-").split()):
            summary_page = p
            break
    rows = []
    if summary_page:
        for line in tool("pdftotext", "-f", str(summary_page), "-l", str(summary_page), "-layout", str(PDF), "-").splitlines():
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
    usable = bool(body) and ok_rows == len(body) and len(body) == 30 and len(total) == 1 and \
        total[0]["zero_area_villages"] == sum(r["zero_area_villages"] for r in body)
    record.update({"summary_page": summary_page, "summary_rows_read": len(body), "summary_rows_that_add_up": ok_rows,
                   "summary_rows_that_do_not": [r["line_as_read"] for r in body if r["adds_up"] == "no"],
                   "printed_total_row_read": len(total), "zero_area_villages_summed_over_the_rows_read": sum(r["zero_area_villages"] for r in body),
                   "text_usable_for_counts": usable,
                   "conclusion": ("the file's text passes the summary page's own arithmetic" if usable else
                                  "the file is a scan: every page is one image, and the only text it carries is a layer made by the scanner's "
                                  "character recognition. That layer fails the summary page's own arithmetic or does not give 30 districts and a "
                                  "printed total, so no count is taken from it and nothing is added to district_need.csv. No character recognition "
                                  "was run here")})
    add("the forest villages PDF: pages, and pages that are one scanned image", "every page one image", f"{pages} pages, {record['pages_that_are_one_image']} of them one image",
        record["pages_that_are_one_image"] == pages)
    add("the forest villages PDF: rows of its summary page read from the text it carries, and rows whose two parts add to their total", "30 rows, all adding up, and a printed total",
        f"{len(body)} rows read, {ok_rows} add up, printed total rows read: {len(total)}", True)
    if usable:
        G.stop("the forest villages PDF's text passed the summary page's arithmetic: the district parse has to be written and checked against "
               "every total the PDF prints before this step can go on")
    add("the forest villages PDF: district counts taken into district_need.csv (only if the text passes its own totals)", "none unless it passes", "none", True)
    return record, rows


def main() -> None:
    gates: list[tuple] = []
    add = lambda gate, expected, found, ok: gates.append((gate, str(expected), str(found), bool(ok)))
    inputs = {"fra_district": G.IN["fra_district"], "fra_mota": G.IN["fra_mota"], "district_need": G.OUT / "district_need.csv",
              "forest_villages_pdf": PDF}
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

    record, check_rows = forest_villages(gates)
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
    record["checked_utc"] = G.utc_now()
    (G.OUT / "forest_villages_pdf_record.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    grows = [{"gate": g, "expected": e, "found": f_, "pass": "yes" if ok else "NO"} for g, e, f_, ok in gates]
    G.write_rows(G.OUT / "gates_phase5.csv", grows, ["gate", "expected", "found", "pass"])
    outputs = [G.OUT / n for n in ("fra_by_district.csv", "fra_summary.csv", "fra_two_reports.csv", "forest_villages_text_layer_check.csv",
                                   "forest_villages_pdf_record.json", "gates_phase5.csv")]
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
