"""Stage 4: three small tables for the deck, cut from the stage's own tables. Writes into `50_gap/deck_tables/` only.

    ~/.venvs/ictd-stage4/bin/python scripts/08_build_gap_deck_tables.py

Nothing is computed here that the stage tables do not already hold: each cell is a cell of a table in `50_gap/`, put
beside others and rounded for a slide (the rounding of each column is stated in the lists below; a column's name does
not carry it). `scripts/verify_gap.py` holds
every cell against the table it comes from.

districts_by_need.csv - the 30 districts, largest N1 first (ties by census code)
  rank_by_n1, district_name, pc11_district_code
  n1_ha                                   N1 of the default window, whole hectares (`district_need.csv`)
  need_share_pct                          C1's need share, one decimal (`need_vs_allocation.csv`)
  plantation_post_share_pct               C1's allocation share: the district's share of R6.20 plantation expenditure,
                                          FY2018-19 to 2025-26, one decimal
  plantation_pre_share_pct                C5's allocation share: the same for FY2014-15 to 2017-18, one decimal. Those
                                          four years are a snapshot frozen on 10/10/2020
  r_post_share_over_need_share            C1's r, two decimals; blank where N1 is zero
  st_class                                the district's Scheduled Tribe class, on the population of LGD panchayat units
  adi_tercile                             the district's tercile of the development index of 2011, on the same population
  adi_source                              the index's source and licence, as the layer's list of sources gives them
marginalisation_split_c1.csv - the rows of `marginalisation_split.csv` for C1: grouping, class, n_districts,
  need_share_pct and allocation_share_pct to one decimal, and the note (the classes rest on LGD population only; the
  index's source and licence on its rows)
headline_rows.csv - C1, P1 and H1: id, what_it_is, estimate, interval_lo, interval_hi, interval_is, p, p_is, n, unit,
  read_from. C1's estimate is Spearman's rho with its bootstrap interval and permutation p; P1's and H1's are
  coefficients with wild-cluster-bootstrap intervals and p. Estimates and interval ends are rounded to three decimals
  (C1) or four (P1, H1); p to five decimals for C1 (its permutation p can be as small as one in a hundred thousand) and
  four for the models.
Each table is also written as markdown (`.md`) with the same cells.
"""
from __future__ import annotations

import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gap_common as G  # noqa: E402
from _gap_common import D  # noqa: E402

STEP = "08_build_gap_deck_tables"
OUT = G.OUT / "deck_tables"


def r(x, places: str):
    return None if x in (None, "") else D(x).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def markdown(path: Path, rows: list[dict], columns: list[str]) -> None:
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    for row in rows:
        lines.append("| " + " | ".join("" if row[c] is None else G.fmt(row[c]).replace("|", "/") for c in columns) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    G.require_stage4_environment()
    inputs = {n: G.OUT / f"{n}.csv" for n in ("district_need", "need_vs_allocation", "need_vs_allocation_summary", "marginalisation_split",
                                              "panel_models", "unit_history_models")}
    for p in inputs.values():
        if not p.exists():
            G.stop(f"an input is missing: {G.rel(p)}")
    OUT.mkdir(parents=True, exist_ok=True)
    need = G.read_rows(inputs["district_need"])
    long = {(x["comparison"], x["pc11_district_code"]): x for x in G.read_rows(inputs["need_vs_allocation"])}
    split = G.read_rows(inputs["marginalisation_split"])
    adi_note = next(x["note"] for x in split if x["grouping"] == "adi_tercile")
    adi_source = adi_note.split("; ", 1)[1]
    order = sorted(need, key=lambda x: (-D(x["n1_ha_2018_2025"]), x["pc11_district_code"]))
    t1 = []
    for i, x in enumerate(order, 1):
        c1, c5 = long[("C1", x["pc11_district_code"])], long[("C5", x["pc11_district_code"])]
        t1.append({"rank_by_n1": i, "district_name": x["district_name"], "pc11_district_code": x["pc11_district_code"],
                   "n1_ha": r(x["n1_ha_2018_2025"], "1"), "need_share_pct": r(c1["need_share_pct"], "0.1"),
                   "plantation_post_share_pct": r(c1["allocation_share_pct"], "0.1"), "plantation_pre_share_pct": r(c5["allocation_share_pct"], "0.1"),
                   "r_post_share_over_need_share": r(c1["r"], "0.01"), "st_class": x["st_class"], "adi_tercile": x["adi_tercile"], "adi_source": adi_source})
    cols1 = ["rank_by_n1", "district_name", "pc11_district_code", "n1_ha", "need_share_pct", "plantation_post_share_pct", "plantation_pre_share_pct",
             "r_post_share_over_need_share", "st_class", "adi_tercile", "adi_source"]
    t2 = [{"grouping": x["grouping"], "class": x["class"], "n_districts": int(x["n_districts"]), "need_share_pct": r(x["need_share_pct"], "0.1"),
           "allocation_share_pct": r(x["allocation_share_pct"], "0.1"), "note": x["note"]} for x in split if x["comparison"] == "C1"]
    cols2 = ["grouping", "class", "n_districts", "need_share_pct", "allocation_share_pct", "note"]
    c1 = next(x for x in G.read_rows(inputs["need_vs_allocation_summary"]) if x["comparison"] == "C1")
    p1 = next(x for x in G.read_rows(inputs["panel_models"]) if x["id"] == "P1")
    h1 = next(x for x in G.read_rows(inputs["unit_history_models"]) if x["id"] == "H1")
    wcb = lambda clusters: f"95 % interval of a restricted wild cluster bootstrap ({clusters} district clusters, Webb weights), by test inversion"
    t3 = [{"id": "C1", "what_it_is": f"Spearman's rho between need ({c1['need_is']}) and allocation ({c1['allocation_is']}) over the districts",
           "estimate": r(c1["rho"], "0.001"), "interval_lo": r(c1["ci95_lo"], "0.001"), "interval_hi": r(c1["ci95_hi"], "0.001"),
           "interval_is": "95 % percentile bootstrap over districts", "p": r(c1["p_permutation"], "0.00001"), "p_is": "two-sided permutation",
           "n": f"{c1['n_districts']} districts", "unit": "rank correlation", "read_from": "50_gap/need_vs_allocation_summary.csv"},
          {"id": "P1", "what_it_is": f"{p1['outcome']} on {p1['regressor']}; {p1['spec']}", "estimate": r(p1["coefficient"], "0.0001"),
           "interval_lo": r(p1["wcb_ci95_lo"], "0.0001"), "interval_hi": r(p1["wcb_ci95_hi"], "0.0001"), "interval_is": wcb(p1["clusters"]),
           "p": r(p1["wcb_p"], "0.0001"), "p_is": "wild cluster bootstrap", "n": f"{p1['n']} district-years, {p1['clusters']} districts",
           "unit": p1["coefficient_unit"], "read_from": "50_gap/panel_models.csv"},
          {"id": "H1", "what_it_is": f"{h1['outcome']} on {h1['exposure']}; {h1['sample']}; controls: {h1['controls']}", "estimate": r(h1["coefficient"], "0.0001"),
           "interval_lo": r(h1["wcb_ci95_lo"], "0.0001"), "interval_hi": r(h1["wcb_ci95_hi"], "0.0001"), "interval_is": wcb(h1["n_districts"]),
           "p": r(h1["wcb_p"], "0.0001"), "p_is": "wild cluster bootstrap", "n": f"{h1['n_units']} units ({h1['n_exposed']} exposed), {h1['n_districts']} districts",
           "unit": h1["coefficient_unit"], "read_from": "50_gap/unit_history_models.csv"}]
    cols3 = ["id", "what_it_is", "estimate", "interval_lo", "interval_hi", "interval_is", "p", "p_is", "n", "unit", "read_from"]
    outputs = []
    for stem, rows, cols in (("districts_by_need", t1, cols1), ("marginalisation_split_c1", t2, cols2), ("headline_rows", t3, cols3)):
        G.write_rows(OUT / f"{stem}.csv", rows, cols)
        markdown(OUT / f"{stem}.md", rows, cols)
        outputs += [OUT / f"{stem}.csv", OUT / f"{stem}.md"]
    G.record_step(STEP, Path(__file__), inputs, outputs, {"note": "every cell is a cell of a table of 50_gap/, rounded as the column's definition says"})
    print("wrote " + ", ".join(G.rel(p) for p in outputs))


if __name__ == "__main__":
    main()
