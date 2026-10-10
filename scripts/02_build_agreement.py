#!/usr/bin/env python3
"""
Stage 1 - do the two measures of forest condition point at the same units? Hansen beside CoRE Stack.

    python scripts/02_build_agreement.py --units 10_units/units.gpkg

In : --units                                                 the stage-0 layer: which units there are, their type, and the
                                                             district of the lgd_panchayat units
     10_units/outside_village_district.csv                   the district of the outside_village units (01_assign_outside_district.py)
     20_degradation/hansen_loss_by_canopy_band_by_unit.csv   02_build_hansen.py: land and yearly loss by band of year-2000 canopy
     20_degradation/corestack_by_unit_bands.csv              02_build_corestack.py: every class by the same bands
     20_degradation/corestack_by_unit.csv                    the same source's own per-unit totals on treecover2000 > 10
     20_degradation/hansen_loss_by_canopy_band.csv, corestack_by_unit_level.csv
                                                             the two sources' own summary tables: what the margins must add up to
     and the two provenance records, which must name this layer
Out: 20_degradation/ and nowhere else
     agreement_by_unit.csv        per unit: the rates of each measure, its flags, its zone model, and the agreement class
     agreement_summary.csv        by population, window, minimum forest and unit type: how many units each measure
                                  flags, how many both flag beside the number chance would give, the rank correlations
     agreement_definitions.csv    the same headline for other readings of "CoRE Stack says degraded"
     agreement_intervals.csv      the headline's intervals from three ways of resampling, side by side
     agreement_by_zone.csv        CoRE Stack's two zone models one at a time: is the placebo clean in each?
     agreement_floor_repeatability.csv     the evidence for the minimum forest, measured on this table's own land
     agreement.provenance.json    inputs, UTC run time, definitions, the rulings, checks, n and missingness

It reads tables and calls no Earth Engine. NIRv is not in this table: since 7 Oct 2026 it is a reported column, not
a degradation measure (docs/DEGRADATION.md).

WHAT IS COMPARED, AND WHY UNIT BY UNIT.
  Hansen      a year in which a 30 m pixel's tree cover was removed outright (lossyear).
  CoRE Stack  a class of change between two three-year periods inside its own tree mask: -2 tree cover lost,
              -1 canopy density or height down a class ("degradation"), 1 up a class ("improvement"), 3 and 4 one
              up and one down ("partially degraded").
They do not measure the same thing and are not expected to mark the same pixels: Hansen sees clearance and is
blind to thinning; CoRE Stack's class -1 is thinning under a canopy that still stands. The question this table
answers is the one the project needs: DO THE TWO POINT AT THE SAME UNITS? A pixel-by-pixel overlap needs one more
Earth Engine job and is not in this table.

THE REFERENCE LAND, the same for both: land with treecover2000 > 10 (the two canopy bands 10 < treecover2000 <= 30
and treecover2000 > 30 of both sources' tables). Hansen's loss inside its own mask (treecover2000 > 30) is the
larger part of it; the band 10 < treecover2000 <= 30 is land Hansen's mask leaves out and CoRE Stack covers.
  hansen rate      Hansen loss dated in the window on that land / that land (Hansen's grid)
  corestack rates  the area of a class on that land / the land there that has a CoRE Stack class from -2 to 4
                   (CoRE Stack's own 25 m grid; class 5, "missing", is left out of the denominator)

THE WINDOWS. THE FIRST IS THE HEADLINE. They are never averaged or pooled.
  common_2017_2023      Hansen loss dated 2017 to 2023 beside CoRE Stack's change 2017-2023: the span the CoRE Stack
                        product itself names. THE HEADLINE.
  between_2019_2022     Hansen loss dated 2019 to 2022 only. CoRE Stack's "2017" is the mode of the agricultural
                        years 2016-17 to 2018-19 and its "2023" that of 2022-23 to 2024-25, so a loss dated 2017 or
                        2018 falls inside its first period and one dated 2023 inside its second. This narrower
                        window holds only the years strictly between the two periods. A sensitivity row.
  full_span_2001_2025   Hansen loss in any year 2001 to 2025 beside the same CoRE Stack classes. NOT ONE PERIOD:
                        reported separately and labelled, and not a test of agreement - a unit cleared in 2005
                        counts for Hansen and cannot count for a product that starts in 2017.

A UNIT IS ASSESSED only if it has at least MIN_REFERENCE_HA (100 ha) of reference land by Hansen's grid AND at
least that much land with a CoRE Stack class there. THE FLOOR IS 100 HA BY RULING OF THE PROJECT OWNER (7 Oct 2026).
Below it a rate is not a property of the unit: agreement_floor_repeatability.csv gives, by how much reference land a
unit has, the rank correlation of its Hansen loss rate between odd and even years, and on this land that passes 0.8
only from 100 ha. It supersedes the 50 ha first proposed by 02_propose_forest_floor.py, whose evidence was measured
on the treecover2000 > 30 mask, which is not this table's land. The summary keeps rows at 50 ha and at 10 ha as
sensitivity, and every row carries the repeatability of the lowest class of land its floor lets in. Units below
the floor get the class "insufficient_forest" - they are not "neither".

FLAGS. Among the assessed units of a population (all unit types together, so that a flag means the same thing in an
lgd_panchayat unit and an outside_village one): a unit is flagged by Hansen if its Hansen rate is above the 80th
percentile of those units' rates (or above zero, if that percentile is zero), and by CoRE Stack if its class -1
rate is above the 80th percentile of theirs. The cut is taken again for every population, window and floor. THE
FLAG IS RELATIVE: it says "in the top fifth", not "degraded by some absolute amount" - no absolute threshold has a
basis.
  agreement class   both | hansen_only | corestack_only | neither | zone_model_excluded | insufficient_forest
Where both flag a unit the claim that it degraded is as strong as these two sources can make it; where one
flags it the table says which, and neither is preferred.

WHAT "AGREEMENT" IS MEASURED BY.
  expected if unrelated   n x (share flagged by Hansen) x (share flagged by CoRE Stack): what two unrelated flags of
                          these sizes would share. With two flags of a fifth each that is a twenty-fifth of the units.
  observed / expected     1 = no better than chance
  odds ratio              (both)(neither) / (hansen_only)(corestack_only)
  odds ratio within districts   the same, Mantel-Haenszel over the districts: do the two agree unit by unit inside a
                          district, or only by both being high in the same districts?
  rank correlation        Spearman's, between the Hansen rate and each CoRE Stack rate over the assessed units.
                          Class 1 ("improvement") is there as THE PLACEBO: if Hansen's rate goes with improvement as
                          much as with degradation, the two do not agree, whatever the count of units flagged by both.
  where the area is       the share of all Hansen loss in the window that lies in units CoRE Stack flags, and of all
                          class -1 area that lies in units Hansen flags, each beside the share of the reference
                          land in those units (what an unrelated flag would hold)

THE POPULATIONS, AND WHICH IS THE HEADLINE. CoRE Stack's classes come from two agro-climatic zone models, the Eastern
Plateau and Hills (EPAHR) and the East Coast Plains and Hills (ECPHR). A unit's valued land lies under one, the
other, or both. agreement_by_zone.csv takes them one at a time, and in the units wholly under the East Coast model
the placebo FAILS: there Hansen's rate goes with "improvement" too. So every figure is computed for:
  east_coast_excluded    the assessed units EXCEPT those wholly under the East Coast model. THE HEADLINE.
  all_assessed           every assessed unit. Printed beside the headline everywhere.
  eastern_plateau_only   the assessed units wholly under the Eastern Plateau model (the units that straddle both
                         models left out too). Headline window only: a sensitivity.
WHY THAT ONE: the rule for reading this table was written before any of it was computed - the placebo, above. Where
the placebo fails, a unit flagged by both is not evidence that the two sources see the same degradation. The East
Coast units are also where the agreement is strongest, so leaving them out LOWERS every figure: the headline is the
weaker version, chosen for what it can be claimed to mean, and the other is printed with it so that what the
exclusion costs can be read off. The units that straddle both models stay in the headline: the placebo does not
fail there - the two measures simply do not agree there - and dropping units because they disagree would be
choosing the answer. The cuts are taken again inside each population.

THE INTERVALS (95 per cent: percentiles 2.5 and 97.5 of BOOTSTRAP resamples; every fourth for the correlations; in
every resample the flags are the population's own and the cut is not taken again).
  PRIMARY: whole districts are resampled, every unit in its district. Units are not independent draws - flagged
    units cluster in space - and resampling them singly gave intervals several times too narrow. These are the
    columns _lo95 and _hi95 of the summary and of the definitions table. About thirty clusters is few: they are
    rough themselves.
  THE DISTRICT OF AN OUTSIDE-VILLAGE UNIT IS ASSIGNED, NOT SURVEYED (10_units/outside_village_district.csv;
    docs/UNITS.md): from the name on its polygon, which for some units no check can confirm. So
    agreement_intervals.csv gives two more beside the primary, for the delivered rows:
      districts for the lgd_panchayat units only   whole districts are resampled for the units whose district is a
                           Census code, the outside_village units are resampled one at a time, the two independently;
                           every unit stays in the estimate
      units singly         every unit resampled one at a time: what the first version of this table printed
    with, for the assessed outside_village units, how many have a district that no check can confirm, were moved
    off their polygon's own name, or are ambiguous. Where the first two differ, the difference is what the
    district labels of the outside-village land are carrying.

THE PER-UNIT TABLE. agreement_class, hansen_flag and corestack_flag are the HEADLINE population's (headline window;
agreement_class_<window> and hansen_flag_<window> for the other two windows): an assessed unit wholly under the East
Coast model is "zone_model_excluded" there. agreement_class_all_assessed, hansen_flag_all_assessed and
corestack_flag_all_assessed are the same with nothing excluded. corestack_zone_model says which model a unit's
valued land lies under.

OTHER READINGS OF "CORE STACK SAYS DEGRADED" (agreement_definitions.csv, headline window, for the headline
population and for all assessed units): class -1 alone (the delivered one); class -1 with classes 3 and 4; the net,
class -1 minus class 1; class -2 (tree cover lost), which is the class that should go with Hansen if either product
sees what the other sees; and class 1, the placebo. Classes -1 and 1 come from classifiers the producers report as
right about two times in three.

Needs geopandas, pandas, numpy, scipy.
"""
import argparse, datetime, hashlib, json, sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "20_degradation"
TREE = ("gt10le30", "gt30")                                  # the two canopy bands that make up treecover2000 > 10
WINDOWS = {"common_2017_2023": (2017, 2023), "between_2019_2022": (2019, 2022), "full_span_2001_2025": (2001, 2025)}
HEADLINE = "common_2017_2023"
WINDOW_IS = {"common_2017_2023": "HEADLINE: Hansen loss 2017-2023 beside CoRE Stack change 2017-2023", "between_2019_2022": "sensitivity: Hansen loss 2019-2022 (the years between CoRE Stack's two periods)",
             "full_span_2001_2025": "NOT ONE PERIOD: Hansen loss 2001-2025 beside CoRE Stack change 2017-2023"}
VALUED = ("lost", "degradation", "nochange", "improvement", "gained", "partial3", "partial4")       # classes -2 to 4; class 5 (missing) is not valued
CORE_RATES = {"degradation": ("degradation",), "degradation_with_partial": ("degradation", "partial3", "partial4"), "lost": ("lost",), "improvement": ("improvement",)}
MIN_REFERENCE_HA = 100.0
FLOOR_RULING = ("100 ha, by ruling of the project owner on 7 Oct 2026. On this table's land (treecover2000 > 10) the rank correlation of a unit's Hansen loss rate "
                "between odd and even years passes 0.8 only from 100 ha (agreement_floor_repeatability.csv). It supersedes the 50 ha proposed by 02_propose_forest_floor.py, "
                "whose evidence was measured on the treecover2000 > 30 mask. 50 ha and 10 ha are kept as sensitivity rows")
POPULATIONS = {"east_coast_excluded": "assessed units, except those whose valued land lies wholly under CoRE Stack's East Coast Plains and Hills zone model",
               "all_assessed": "every assessed unit",
               "eastern_plateau_only": "assessed units whose valued land lies wholly under CoRE Stack's Eastern Plateau and Hills zone model"}
HEADLINE_POPULATION = "east_coast_excluded"
HEADLINE_REASON = ("The placebo - Hansen's rate against CoRE Stack's class 1, 'improvement' - was written into this script as the test of whether agreement on class -1 is agreement "
                   "about degradation, before any figure was computed. It fails in the units wholly under the East Coast Plains and Hills zone model (agreement_by_zone.csv). "
                   "Those units are also where the agreement is strongest, so excluding them lowers every figure; the version with nothing excluded is printed beside it. "
                   "Units that straddle both zone models stay in: the placebo does not fail there")
SP = "spearman_hansen_vs_corestack_"
FLOORS = (10.0, 50.0, 100.0)
FLAG_PERCENTILE = 80
BOOTSTRAP, BOOTSTRAP_SEED = 2000, 20261008
LEVELS = {"all units": None, "lgd_panchayat": "lgd_panchayat", "outside_village": "outside_village"}
OUTSIDE_DISTRICT = ROOT / "10_units" / "outside_village_district.csv"
N_DISTRICTS = 30
LAND_CLASSES = ((10, 25), (25, 50), (50, 100), (100, 250), (250, 500), (500, 1000), (1000, None))     # ha of reference land, for the repeatability table
HA_TOLERANCE = 0.003
GRID_TOLERANCE = 0.0005                                      # the reference land summed on Hansen's grid against the same land on CoRE Stack's, all units
fails = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Stopped before writing this step's tables.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def cut_and_flag(rate, pop):
    """The 80th percentile of a population's rates, and which of its units lie above it (above zero if it is zero)."""
    cut = float(np.percentile(rate[pop], FLAG_PERCENTILE))
    return cut, pop & (rate > cut)


def classes(h_flag, c_flag, pop, assessed):
    """A class for every unit: the four combinations inside the population, and why a unit is outside it."""
    out = np.full(len(assessed), "insufficient_forest", dtype=object)
    out[assessed & ~pop] = "zone_model_excluded"
    out[pop & h_flag & c_flag] = "both"
    out[pop & h_flag & ~c_flag] = "hansen_only"
    out[pop & ~h_flag & c_flag] = "corestack_only"
    out[pop & ~h_flag & ~c_flag] = "neither"
    return out


def odds_ratio(a, b, c, d):
    """(both)(neither) / (hansen_only)(corestack_only); None if a cell of the denominator is empty."""
    return float(a * d / (b * c)) if b > 0 and c > 0 else None


def four(idx, hf, cf):
    h_, c_ = hf[idx], cf[idx]
    return int((h_ & c_).sum()), int((h_ & ~c_).sum()), int((~h_ & c_).sum()), int((~h_ & ~c_).sum())


def figures(idx, hf, cf, hr, rates):
    """Odds ratio, observed over expected, and the rank correlation of the Hansen rate with each rate given."""
    a, b, c, d = four(idx, hf, cf)
    e = (a + b) * (a + c) / len(idx) if len(idx) else 0.0
    out = {"odds_ratio": odds_ratio(a, b, c, d), "both_observed_over_expected": a / e if e > 0 else None}
    for name, rate in rates.items():
        x, y = hr[idx], rate[idx]
        out[SP + name] = float(spearmanr(x, y)[0]) if len(idx) > 2 and np.std(x) > 0 and np.std(y) > 0 else None
    return out


def mantel_haenszel(idx, hf, cf, district, rng=None):
    """The odds ratio within districts, pooled over them (Mantel-Haenszel). With rng: also its 95 per cent interval from
    resampling whole districts - each district's term is drawn, with replacement, as many times as there are districts."""
    num, den = [], []
    for d_ in sorted(set(district[idx])):
        m = idx[district[idx] == d_]
        a, b, c, d = four(m, hf, cf)
        num.append(a * d / len(m)); den.append(b * c / len(m))
    num, den = np.asarray(num, float), np.asarray(den, float)
    est = float(num.sum() / den.sum()) if den.sum() > 0 else None
    if rng is None:
        return est
    pick = rng.integers(0, len(num), size=(BOOTSTRAP, len(num)))
    top, bottom = num[pick].sum(axis=1), den[pick].sum(axis=1)
    return est, interval(np.where(bottom > 0, top / np.where(bottom > 0, bottom, 1), np.nan), BOOTSTRAP)


def resampler(idx, design, district, outside, rng):
    """A function that returns one resample of idx. 'districts': whole districts, every unit in its assigned district.
    'lgd_districts': whole districts for the lgd_panchayat units and single units for the outside_village ones, the
    two drawn independently. 'units_singly': single units."""
    if design == "units_singly":
        one = lambda: idx[rng.integers(0, len(idx), len(idx))]
        one.clusters, one.singles = 0, len(idx)
        return one
    grouped = idx if design == "districts" else idx[~outside[idx]]
    single = idx[:0] if design == "districts" else idx[outside[idx]]
    members = [grouped[district[grouped] == d_] for d_ in sorted(set(district[grouped]))]

    def one():
        parts = [members[i] for i in rng.integers(0, len(members), len(members))] if members else []
        if len(single):
            parts.append(single[rng.integers(0, len(single), len(single))])
        return np.concatenate(parts)
    one.clusters, one.singles = len(members), len(single)
    return one


def interval(values, expected):
    v = np.asarray([x for x in values if x is not None and not np.isnan(x)], float)
    return (round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)) if len(v) >= 0.9 * expected else (None, None)


def intervals(idx, hf, cf, hr, rates, design, district, outside, rng):
    """95 per cent intervals (percentiles 2.5 and 97.5) of figures() over BOOTSTRAP resamples of one design; the
    correlations on every fourth resample. The flags are the full population's and are not cut again."""
    one = resampler(idx, design, district, outside, rng)
    got = {}
    for k in range(BOOTSTRAP):
        j = one()
        for key, v in figures(j, hf, cf, hr, rates if k % 4 == 0 else {}).items():
            got.setdefault(key, []).append(v)
    return {key: interval(v, BOOTSTRAP // 4 if key.startswith(SP) else BOOTSTRAP) for key, v in got.items()}, one


def agreement_row(idx, hf, cf, hr, rates, with_interval, land, h_loss, c_deg, district, outside, rng):
    """The figures for the assessed units idx of one population and unit type: counts, chance, odds ratio, rank
    correlations, intervals from resampling whole districts, the odds ratio within districts, and where the area lies."""
    n = int(len(idx))
    row = {"n_assessed": n}
    if n == 0:
        return row
    a, b, c, d = four(idx, hf, cf)
    expected = (a + b) * (a + c) / n
    est = figures(idx, hf, cf, hr, rates)
    row.update({"flagged_by_hansen": a + b, "flagged_by_corestack": a + c, "both": a, "hansen_only": b, "corestack_only": c, "neither": d,
                "both_expected_if_unrelated": round(float(expected), 2), "both_observed_over_expected": round(a / expected, 3) if expected > 0 else None,
                "odds_ratio": round(est["odds_ratio"], 3) if est["odds_ratio"] is not None else None})
    for name in rates:
        row[SP + name] = round(est[SP + name], 4) if est[SP + name] is not None else None
    ci, one = intervals(idx, hf, cf, hr, {k: rates[k] for k in with_interval}, "districts", district, outside, rng)
    row["n_districts"] = one.clusters
    for key in ["odds_ratio", "both_observed_over_expected"] + [SP + k for k in with_interval]:
        row[f"{key}_lo95"], row[f"{key}_hi95"] = ci.get(key, (None, None))
    mh, (mh_lo, mh_hi) = mantel_haenszel(idx, hf, cf, district, rng)
    row["odds_ratio_within_districts"] = round(mh, 3) if mh is not None else None
    row["odds_ratio_within_districts_lo95"], row["odds_ratio_within_districts_hi95"] = mh_lo, mh_hi
    sel = np.zeros(len(land), bool); sel[idx] = True
    tot_land, tot_loss, tot_deg = land[sel].sum(), h_loss[sel].sum(), c_deg[sel].sum()
    row.update({"reference_km2": round(float(tot_land) / 100, 2), "hansen_loss_km2": round(float(tot_loss) / 100, 2), "corestack_degradation_km2": round(float(tot_deg) / 100, 2),
                "hansen_loss_pct_in_units_corestack_flags": round(100 * float(h_loss[sel & cf].sum() / tot_loss), 2) if tot_loss > 0 else None,
                "reference_land_pct_in_units_corestack_flags": round(100 * float(land[sel & cf].sum() / tot_land), 2),
                "corestack_degradation_pct_in_units_hansen_flags": round(100 * float(c_deg[sel & hf].sum() / tot_deg), 2) if tot_deg > 0 else None,
                "reference_land_pct_in_units_hansen_flags": round(100 * float(land[sel & hf].sum() / tot_land), 2)})
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    a = ap.parse_args()
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    layer_sha = sha256(a.units)
    units = pd.DataFrame(gpd.read_file(a.units, layer="units", ignore_geometry=True))[["unit_id", "unit_level", "outside_village", "pc11_district_code"]]
    units["unit_id"] = units["unit_id"].astype(str)
    units = units.sort_values("unit_id").reset_index(drop=True)
    inputs = [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": layer_sha}]
    od = pd.read_csv(OUTSIDE_DISTRICT, dtype=str).set_index("unit_id")["pc11_district_code"]
    inputs.append({"path": str(OUTSIDE_DISTRICT.relative_to(ROOT)), "bytes": OUTSIDE_DISTRICT.stat().st_size, "sha256": sha256(OUTSIDE_DISTRICT), "role": "the district of the outside_village units"})
    code = units["pc11_district_code"].astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    district = code.where(units["unit_level"] != "outside_village", units["unit_id"].map(od)).fillna("").to_numpy(str)
    units = units.drop(columns="pc11_district_code")
    if (district == "").any() or len(set(district)) != N_DISTRICTS:
        fails.append(f"{int((district == '').sum()):,} units have no district and there are {len(set(district))} districts, not {N_DISTRICTS}")

    def load(table, record):
        tp, rp = OUT / table, OUT / record
        if not tp.exists() or not rp.exists():
            fails.append(f"{table} or {record} is missing: build that source first")
            return None
        prov = json.load(open(rp))
        if layer_sha not in [i.get("sha256") for i in prov.get("inputs", []) if i.get("path") == str(a.units)]:
            fails.append(f"{record} does not name this layer ({a.units}, sha256 {layer_sha[:12]}...)")
        t = pd.read_csv(tp, dtype={"unit_id": str})
        if len(t) != len(units) or not t["unit_id"].is_unique or set(t["unit_id"]) != set(units["unit_id"]):
            fails.append(f"{table} holds {len(t):,} rows and {t['unit_id'].nunique():,} distinct unit_id; the layer has {len(units):,} units")
            return None
        inputs.append({"path": str(tp.relative_to(ROOT)), "bytes": tp.stat().st_size, "sha256": sha256(tp), "built_by": prov.get("script"), "run_utc": prov.get("run_utc")})
        return t.set_index("unit_id").loc[units["unit_id"]]

    hb = load("hansen_loss_by_canopy_band_by_unit.csv", "hansen.provenance.json")
    cb = load("corestack_by_unit_bands.csv", "corestack.provenance.json")
    cu = load("corestack_by_unit.csv", "corestack.provenance.json")
    stop_if_failed("reading the two sources' tables")
    level = units["unit_level"].to_numpy()
    print(f"{a.units}: n = {len(units):,} units ({dict(units['unit_level'].value_counts())})")

    # ---- the margins, and what they must add up to -----------------------------------------------------------------------
    land = sum(hb[f"area_ha_{b}"].to_numpy(float) for b in TREE)                                   # Hansen's grid
    loss = {w: sum(hb[f"loss_ha_{b}_{y}"].to_numpy(float) for b in TREE for y in range(lo, hi + 1)) for w, (lo, hi) in WINDOWS.items()}
    cls = {k: sum(cb[f"class_{k}_ha_{b}"].to_numpy(float) for b in TREE) for k in VALUED + ("missing",)}
    valued = sum(cls[k] for k in VALUED)                                                           # CoRE Stack's grid
    checks = {}
    for b in TREE + ("le10",):                                                                      # the yearly columns are what the windows are made of
        gap = float(np.abs(sum(hb[f"loss_ha_{b}_{y}"].to_numpy(float) for y in range(2001, 2026)) - hb[f"loss_ha_{b}"].to_numpy(float)).max())
        if gap > HA_TOLERANCE:
            fails.append(f"band {b}: the yearly loss columns do not add up to loss_ha_{b} (largest gap {gap:.4f} ha)")
    hs = pd.read_csv(OUT / "hansen_loss_by_canopy_band.csv").set_index(["units", "canopy_band"])
    cl = pd.read_csv(OUT / "corestack_by_unit_level.csv").set_index(["units", "land"])
    worst = 0.0
    for label, lv in LEVELS.items():
        sel = level == lv if lv else np.ones(len(units), bool)
        for b in TREE:
            for theirs, years in (("loss_km2_2001_2010", range(2001, 2011)), ("loss_km2_2011_2017", range(2011, 2018)), ("loss_km2_2018_2025", range(2018, 2026)), ("loss_km2_2001_2025", range(2001, 2026))):
                mine = float(sum(hb.loc[sel, f"loss_ha_{b}_{y}"].sum() for y in years)) / 100
                worst = max(worst, abs(mine - float(hs.loc[(label, b), theirs])))
                if abs(mine - float(hs.loc[(label, b), theirs])) > 0.006:
                    fails.append(f"{label}, band {b}: yearly loss sums to {mine:,.3f} km2 over {years[0]}-{years[-1]}; hansen_loss_by_canopy_band.csv prints {float(hs.loc[(label, b), theirs]):,.2f}")
            mine = float(hb.loc[sel, f"area_ha_{b}"].sum()) / 100
            if abs(mine - float(hs.loc[(label, b), "land_km2"])) > 0.006:
                fails.append(f"{label}, band {b}: land sums to {mine:,.3f} km2; hansen_loss_by_canopy_band.csv prints {float(hs.loc[(label, b), 'land_km2']):,.2f}")
        for k, theirs in (("degradation", "degradation_km2"), ("lost", "loss_km2"), ("improvement", "improvement_km2"), ("gained", "gain_km2")):
            mine = float(cls[k][sel].sum()) / 100
            worst = max(worst, abs(mine - float(cl.loc[(label, "treecover2000 > 10"), theirs])))
            if abs(mine - float(cl.loc[(label, "treecover2000 > 10"), theirs])) > 0.006:
                fails.append(f"{label}: CoRE Stack class {k} on treecover2000 > 10 sums to {mine:,.3f} km2; corestack_by_unit_level.csv prints {float(cl.loc[(label, 'treecover2000 > 10'), theirs]):,.2f}")
        mine = float((cls["partial3"] + cls["partial4"])[sel].sum()) / 100
        if abs(mine - float(cl.loc[(label, "treecover2000 > 10"), "partial_degradation_km2"])) > 0.006:
            fails.append(f"{label}: classes 3 and 4 on treecover2000 > 10 sum to {mine:,.3f} km2; corestack_by_unit_level.csv prints {float(cl.loc[(label, 'treecover2000 > 10'), 'partial_degradation_km2']):,.2f}")
    checks["margins_against_the_sources_own_summary_tables_largest_gap_km2"] = round(worst, 4)
    gap = float(np.abs(cls["degradation"] - cu["corestack_degradation_ha_tc_gt10"].to_numpy(float)).max())
    checks["corestack_degradation_on_reference_land_two_tables_largest_gap_ha"] = round(gap, 5)
    if gap > HA_TOLERANCE:
        fails.append(f"class -1 on treecover2000 > 10 differs between corestack_by_unit_bands.csv and corestack_by_unit.csv (largest gap {gap:.4f} ha)")
    grid = float(sum(cb[f"land_ha_{b}"].to_numpy(float) for b in TREE).sum() / land.sum() - 1)
    checks["reference_land_on_corestack_grid_vs_hansen_grid_all_units"] = round(grid, 6)
    if abs(grid) > GRID_TOLERANCE:
        fails.append(f"the reference land summed on CoRE Stack's grid differs from Hansen's by {grid:+.4%} over all units")
    stop_if_failed("checking the margins against the two sources' own tables")
    print(f"OK  the windows' yearly columns and the CoRE Stack classes add up to the two sources' own summary tables (largest gap {worst:.4f} km2); "
          f"the reference land is {land.sum() / 100:,.1f} km2 on Hansen's grid and {grid:+.4%} from that on CoRE Stack's")

    # ---- rates, the floor, the zone models, the populations ---------------------------------------------------------------
    n_units = len(units)
    outside = (level == "outside_village")
    with np.errstate(invalid="ignore", divide="ignore"):
        h_rate = {w: np.nan_to_num(np.where(land > 0, loss[w] / land, np.nan)) for w in WINDOWS}
        c_rate_raw = {name: np.where(valued > 0, sum(cls[k] for k in parts) / valued, np.nan) for name, parts in CORE_RATES.items()}
        c_rate_raw["net"] = np.where(valued > 0, (cls["degradation"] - cls["improvement"]) / valued, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        h_rate_raw = {w: np.where(land > 0, loss[w] / land, np.nan) for w in WINDOWS}
    c_rate = {k: np.nan_to_num(v) for k, v in c_rate_raw.items()}
    assessed_at = {f: (land >= f) & (valued >= f) for f in FLOORS}
    assessed = assessed_at[MIN_REFERENCE_HA]
    ze, zc = cb["value_ha_zone_EPAHR"].to_numpy(float), cb["value_ha_zone_ECPHR"].to_numpy(float)
    zone = np.where((ze > 0) & (zc == 0), "EPAHR only", np.where((zc > 0) & (ze == 0), "ECPHR only", np.where((ze > 0) & (zc > 0), "both models", "neither")))
    if (zone[assessed_at[min(FLOORS)]] == "neither").any():
        fails.append("an assessed unit has valued land under neither zone model")
    in_pop = {"all_assessed": np.ones(n_units, bool), "east_coast_excluded": zone != "ECPHR only", "eastern_plateau_only": zone == "EPAHR only"}
    stop_if_failed("splitting the units by zone model")

    # ---- the minimum forest, tested on this table's own land (before the summary: each floor carries its figure) ----------
    yearly = {y: sum(hb[f"loss_ha_{b}_{y}"].to_numpy(float) for b in TREE) for y in range(2001, 2026)}
    rrows = []
    for span, (lo_y, hi_y) in (("2001-2025", (2001, 2025)), ("2017-2023", WINDOWS[HEADLINE])):
        odd, even = (sum(yearly[y] for y in range(lo_y, hi_y + 1) if y % 2 == r_) for r_ in (1, 0))
        for lo_h, hi_h in LAND_CLASSES:
            sel = (land >= lo_h) & ((land < hi_h) if hi_h else np.ones(n_units, bool))
            x, y = odd[sel] / land[sel], even[sel] / land[sel]
            rrows.append({"land": "treecover2000 > 10 (this table's reference land)", "reference_ha_from": lo_h, "reference_ha_below": hi_h, "hansen_loss_years": span, "n_units": int(sel.sum()),
                          "units_with_no_loss_in_those_years": int(((odd + even)[sel] == 0).sum()),
                          "odd_years_vs_even_years_spearman": round(float(spearmanr(x, y)[0]), 3) if np.std(x) > 0 and np.std(y) > 0 else None})
    repeat = pd.DataFrame(rrows)
    rep_at = lambda floor, span: repeat[(repeat.reference_ha_from == floor) & (repeat.hansen_loss_years == span)].iloc[0]

    # ---- the summary: every population, window, floor and unit type ----------------------------------------------------------
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    rated = ("degradation", "net", "lost", "improvement")                  # the rank correlations that carry an interval
    rows, flags, cuts = [], {}, {}
    for pop, keep in in_pop.items():
        for w in (WINDOWS if pop != "eastern_plateau_only" else (HEADLINE,)):
            for floor in FLOORS:
                ok = assessed_at[floor] & keep
                cut_h, hf = cut_and_flag(h_rate[w], ok)
                cut_c, cf = cut_and_flag(c_rate["degradation"], ok)
                flags[(pop, w, floor)] = (hf, cf, ok)
                cuts[(pop, w, floor)] = (cut_h, cut_c)
                lowest = next((lo, hi) for lo, hi in LAND_CLASSES if lo == floor)
                for label, lv in LEVELS.items():
                    in_level = level == lv if lv else np.ones(n_units, bool)
                    row = {"population": pop, "population_is": POPULATIONS[pop], "window": w, "window_is": WINDOW_IS[w], "minimum_reference_ha": floor,
                           "delivered": int(pop == HEADLINE_POPULATION and w == HEADLINE and floor == MIN_REFERENCE_HA), "units": label, "n_units": int(in_level.sum()),
                           "n_insufficient_forest": int((in_level & ~assessed_at[floor]).sum()), "n_excluded_by_zone_model": int((in_level & assessed_at[floor] & ~keep).sum()),
                           "hansen_rate_cut": round(cut_h, 6), "corestack_degradation_rate_cut": round(cut_c, 6),
                           "lowest_land_class_admitted_ha": f"{lowest[0]:g} to {lowest[1]:g}", "repeatability_of_that_class_2001_2025": float(rep_at(floor, "2001-2025").odd_years_vs_even_years_spearman),
                           "repeatability_of_that_class_2017_2023": float(rep_at(floor, "2017-2023").odd_years_vs_even_years_spearman)}
                    row.update(agreement_row(np.flatnonzero(in_level & ok), hf, cf, h_rate[w], c_rate, rated, land, loss[w], cls["degradation"], district, outside, rng))
                    rows.append(row)
    summary = pd.DataFrame(rows)
    key = lambda pop, label, w=HEADLINE, floor=MIN_REFERENCE_HA: summary[(summary.population == pop) & (summary.window == w) & (summary.minimum_reference_ha == floor) & (summary.units == label)].iloc[0]
    for pop in in_pop:                                                     # every assessed unit is in the population or shut out of it by its zone model
        r = key(pop, "all units")
        if int(r.n_assessed) + int(r.n_excluded_by_zone_model) + int(r.n_insufficient_forest) != n_units:
            fails.append(f"{pop}: assessed, excluded and insufficient units do not add up to the layer's {n_units:,}")
    stop_if_failed("building the summary")

    # ---- the per-unit table: the headline population's classes, and the classes with nothing excluded -------------------------
    by_unit = units.copy()
    by_unit["reference_ha"] = np.round(land, 4)
    by_unit["corestack_valued_ha"] = np.round(valued, 4)
    by_unit["assessed"] = assessed.astype(int)
    by_unit["corestack_zone_model"] = pd.Series(np.where(valued > 0, zone, None), dtype=object).to_numpy()      # blank: the unit has no land with a class
    head_pop = assessed & in_pop[HEADLINE_POPULATION]
    by_unit["in_headline_population"] = head_pop.astype(int)

    def flag_col(f, pop_):
        out = pd.array(np.where(pop_, f.astype(int), 0), dtype="Int64")
        out[~pop_] = pd.NA
        return out
    for w in WINDOWS:
        hf, cf, ok = flags[(HEADLINE_POPULATION, w, MIN_REFERENCE_HA)]
        name = "agreement_class" if w == HEADLINE else f"agreement_class_{w}"
        by_unit[name] = classes(hf, cf, ok, assessed)
        by_unit["hansen_flag" if w == HEADLINE else f"hansen_flag_{w}"] = flag_col(hf, ok)
        if w == HEADLINE:
            by_unit["corestack_flag"] = flag_col(cf, ok)
    hf_all, cf_all, ok_all = flags[("all_assessed", HEADLINE, MIN_REFERENCE_HA)]
    by_unit["agreement_class_all_assessed"] = classes(hf_all, cf_all, ok_all, assessed)
    by_unit["hansen_flag_all_assessed"] = flag_col(hf_all, ok_all)
    by_unit["corestack_flag_all_assessed"] = flag_col(cf_all, ok_all)
    for w in WINDOWS:
        by_unit[f"hansen_loss_ha_{w}"] = np.round(loss[w], 4)
        by_unit[f"hansen_rate_{w}"] = np.round(h_rate_raw[w], 6)
    for k, parts in (("degradation", ("degradation",)), ("partial_degradation", ("partial3", "partial4")), ("lost", ("lost",)), ("improvement", ("improvement",))):
        by_unit[f"corestack_{k}_ha"] = np.round(sum(cls[p] for p in parts), 4)
    for name in ("degradation", "degradation_with_partial", "net", "lost", "improvement"):
        by_unit[f"corestack_rate_{name}"] = np.round(c_rate_raw[name], 6)

    # ---- other readings of "CoRE Stack says degraded", for the headline population and with nothing excluded ----------------
    drows = []
    for pop in (HEADLINE_POPULATION, "all_assessed"):
        hf, _, ok = flags[(pop, HEADLINE, MIN_REFERENCE_HA)]
        for name, what in (("degradation", "class -1 (delivered)"), ("degradation_with_partial", "classes -1, 3 and 4"), ("net", "class -1 minus class 1"), ("lost", "class -2, tree cover lost"),
                           ("improvement", "class 1, improvement (the placebo)")):
            cut_c, cf = cut_and_flag(c_rate[name], ok)
            for label, lv in LEVELS.items():
                in_level = level == lv if lv else np.ones(n_units, bool)
                row = {"population": pop, "window": HEADLINE, "minimum_reference_ha": MIN_REFERENCE_HA, "corestack_flag_is": what, "corestack_rate": name, "units": label, "corestack_rate_cut": round(cut_c, 6)}
                r = agreement_row(np.flatnonzero(in_level & ok), hf, cf, h_rate[HEADLINE], {name: c_rate[name]}, (name,) if name in rated else (), land, loss[HEADLINE],
                                  sum(cls[k] for k in CORE_RATES.get(name, ("degradation",))), district, outside, rng)
                row.update({k: v for k, v in r.items() if not k.startswith(("hansen_loss_pct", "reference_land_pct", "corestack_degradation_pct", "reference_km2", "hansen_loss_km2", "corestack_degradation_km2"))})
                if name == "degradation":                                   # the delivered reading is the summary's row: one figure, one interval
                    for col in [c_ for c_ in row if c_.endswith(("_lo95", "_hi95"))]:
                        row[col] = key(pop, label)[col]
                drows.append(row)
    definitions = pd.DataFrame(drows)

    # ---- the intervals three ways: districts (primary), districts for the lgd units only, units singly ---------------------------
    odt = pd.read_csv(OUTSIDE_DISTRICT, dtype=str).set_index("unit_id").reindex(units["unit_id"])
    cover, nbrs = pd.to_numeric(odt["area_cover_share"], errors="coerce").to_numpy(float), pd.to_numeric(odt["neighbours_n_districts"], errors="coerce").to_numpy(float)
    no_check = outside & ~(cover >= 0.5) & ~(nbrs > 0)
    moved = outside & (odt["assigned_by"] == "two checks against the label").to_numpy()
    no_name = outside & odt["assigned_by"].fillna("").str.endswith("has no district name").to_numpy()
    ambiguous = outside & (odt["ambiguous"] == "1").to_numpy()
    one_check = outside & (((odt["area_majority_agrees_with_assigned"] == "0") | ((odt["label_absent_from_collar"] == "1") & (odt["assigned_by"] == "label"))).to_numpy())
    rng2 = np.random.default_rng(BOOTSTRAP_SEED + 1)
    irows = []
    for pop in (HEADLINE_POPULATION, "all_assessed"):
        hf, cf, ok = flags[(pop, HEADLINE, MIN_REFERENCE_HA)]
        rates = {k: c_rate[k] for k in rated}
        for label, lv in LEVELS.items():
            idx = np.flatnonzero(ok & ((level == lv) if lv else np.ones(n_units, bool)))
            s = key(pop, label)
            lgd_ci, lgd_one = intervals(idx, hf, cf, h_rate[HEADLINE], rates, "lgd_districts", district, outside, rng2)
            one_ci, _ = intervals(idx, hf, cf, h_rate[HEADLINE], rates, "units_singly", district, outside, rng2)
            sel = np.zeros(n_units, bool); sel[idx] = True
            common = {"population": pop, "window": HEADLINE, "minimum_reference_ha": MIN_REFERENCE_HA, "delivered": int(pop == HEADLINE_POPULATION), "units": label, "n_assessed": int(len(idx)),
                      "n_lgd_panchayat": int((sel & ~outside).sum()), "n_outside_village": int((sel & outside).sum()), "districts_resampled_primary": int(s.n_districts),
                      "districts_resampled_lgd_only_design": lgd_one.clusters, "units_resampled_singly_lgd_only_design": lgd_one.singles,
                      "outside_village_assessed_district_has_no_possible_check": int((sel & no_check).sum()), "outside_village_assessed_moved_off_the_polygons_name": int((sel & moved).sum()),
                      "outside_village_assessed_polygon_has_no_name": int((sel & no_name).sum()), "outside_village_assessed_ambiguous": int((sel & ambiguous).sum()),
                      "outside_village_assessed_one_check_contradicts_the_district": int((sel & one_check).sum())}
            for k in ["odds_ratio", "both_observed_over_expected"] + [SP + r_ for r_ in rated]:
                lo_d, hi_d = s[f"{k}_lo95"], s[f"{k}_hi95"]
                (lo_l, hi_l), (lo_u, hi_u) = lgd_ci[k], one_ci[k]
                width = lambda lo, hi: (hi - lo) if lo is not None and hi is not None and not pd.isna(lo) and not pd.isna(hi) else None
                wd, wl, wu = width(lo_d, hi_d), width(lo_l, hi_l), width(lo_u, hi_u)
                irows.append({**common, "statistic": k, "estimate": float(s[k]) if not pd.isna(s[k]) else None,
                              "lo95_districts": lo_d, "hi95_districts": hi_d, "lo95_lgd_districts_outside_singly": lo_l, "hi95_lgd_districts_outside_singly": hi_l,
                              "lo95_units_singly": lo_u, "hi95_units_singly": hi_u,
                              "width_districts_over_lgd_only_design": round(wd / wl, 2) if wd and wl else None, "width_districts_over_units_singly": round(wd / wu, 2) if wd and wu else None})
            irows.append({**common, "statistic": "odds_ratio_within_districts_mantel_haenszel", "estimate": float(s.odds_ratio_within_districts) if not pd.isna(s.odds_ratio_within_districts) else None,
                          "lo95_districts": s.odds_ratio_within_districts_lo95, "hi95_districts": s.odds_ratio_within_districts_hi95})
    three_ways = pd.DataFrame(irows)

    # ---- the zone models one at a time: is the placebo clean in each? (flags: those of all assessed units) ------------------------
    cut_p, placebo_flag = cut_and_flag(c_rate["improvement"], ok_all)
    tot = {"land": land[ok_all].sum(), "loss": loss[HEADLINE][ok_all].sum(), "deg": cls["degradation"][ok_all].sum()}
    zrows = []
    for zname in ("EPAHR only", "ECPHR only", "both models"):
        zsel = ok_all & (zone == zname)
        idx = np.flatnonzero(zsel)
        n = int(len(idx))
        row = {"window": HEADLINE, "minimum_reference_ha": MIN_REFERENCE_HA, "units": "all units", "flags_are": "those of all assessed units", "zone_model_of_the_units_valued_land": zname,
               "in_the_headline_population": int(zname != "ECPHR only"), "n_assessed": n, "n_lgd_panchayat": int((zsel & ~outside).sum()), "n_outside_village": int((zsel & outside).sum()),
               "n_districts": len(set(district[idx])), "assessed_units_pct": round(100 * n / int(ok_all.sum()), 2), "reference_land_pct_of_assessed": round(100 * float(land[zsel].sum() / tot["land"]), 2),
               "hansen_loss_pct_of_assessed": round(100 * float(loss[HEADLINE][zsel].sum() / tot["loss"]), 2), "corestack_degradation_pct_of_assessed": round(100 * float(cls["degradation"][zsel].sum() / tot["deg"]), 2),
               "flagged_by_hansen": int(hf_all[idx].sum()), "flagged_by_hansen_pct": round(100 * float(hf_all[idx].mean()), 1) if n else None,
               "median_corestack_degradation_rate": round(float(np.median(c_rate["degradation"][idx])), 4) if n else None, "median_corestack_improvement_rate": round(float(np.median(c_rate["improvement"][idx])), 4) if n else None}
        for tag, cflag in (("degradation", cf_all), ("improvement_the_placebo", placebo_flag)):
            a_, b_, c__, d_ = four(idx, hf_all, cflag)
            e_ = (a_ + b_) * (a_ + c__) / n if n else 0.0
            row.update({f"flagged_on_{tag}": a_ + c__, f"both_{tag}": a_, f"both_{tag}_expected_if_unrelated": round(e_, 2), f"both_{tag}_observed_over_expected": round(a_ / e_, 3) if e_ > 0 else None,
                        f"odds_ratio_{tag}": round(odds_ratio(a_, b_, c__, d_), 3) if odds_ratio(a_, b_, c__, d_) is not None else None})
        est = figures(idx, hf_all, cf_all, h_rate[HEADLINE], {k: c_rate[k] for k in ("degradation", "improvement")})
        ci_d, _ = intervals(idx, hf_all, cf_all, h_rate[HEADLINE], {k: c_rate[k] for k in ("degradation", "improvement")}, "districts", district, outside, rng2)
        ci_u, _ = intervals(idx, hf_all, cf_all, h_rate[HEADLINE], {k: c_rate[k] for k in ("degradation", "improvement")}, "units_singly", district, outside, rng2)
        for k in ("degradation", "improvement"):
            row[SP + k] = round(est[SP + k], 4)
            row[f"{SP}{k}_lo95"], row[f"{SP}{k}_hi95"] = ci_d[SP + k]
            row[f"{SP}{k}_lo95_units_singly"], row[f"{SP}{k}_hi95_units_singly"] = ci_u[SP + k]
        zrows.append(row)
    by_zone = pd.DataFrame(zrows)
    if int(by_zone["n_assessed"].sum()) != int(ok_all.sum()):
        fails.append(f"the zone models hold {int(by_zone['n_assessed'].sum()):,} assessed units between them; there are {int(ok_all.sum()):,}")
    if int(by_zone["both_degradation"].sum()) != int(key("all_assessed", "all units").both):
        fails.append("units flagged by both, summed over the zone models, are not the summary's for all assessed units")
    if int(by_zone.loc[by_zone.in_the_headline_population == 1, "n_assessed"].sum()) != int(key(HEADLINE_POPULATION, "all units").n_assessed):
        fails.append("the zone models kept in the headline do not hold the headline population's units")
    stop_if_failed("the three interval designs and the zone models")

    out_tables = {"agreement_by_unit.csv": by_unit, "agreement_summary.csv": summary, "agreement_definitions.csv": definitions,
                  "agreement_intervals.csv": three_ways, "agreement_by_zone.csv": by_zone, "agreement_floor_repeatability.csv": repeat}
    for name, t in out_tables.items():
        t.to_csv(OUT / name, index=False)
    old = OUT / "agreement_intervals_by_district.csv"                       # the table agreement_intervals.csv replaces
    if old.exists():
        old.unlink()
    # read back what was written: the delivered counts recounted from the per-unit table on disk
    back_u, back_s = pd.read_csv(OUT / "agreement_by_unit.csv", dtype={"unit_id": str}), pd.read_csv(OUT / "agreement_summary.csv")
    for pop, col in ((HEADLINE_POPULATION, "agreement_class"), ("all_assessed", "agreement_class_all_assessed")):
        back_h = back_s[(back_s.population == pop) & (back_s.window == HEADLINE) & (back_s.minimum_reference_ha == MIN_REFERENCE_HA)].set_index("units")
        for label, lv in LEVELS.items():
            n_ = back_u.loc[(back_u["unit_level"] == lv) if lv else np.ones(len(back_u), bool), col].value_counts()
            for k in ("both", "hansen_only", "corestack_only", "neither"):
                if int(n_.get(k, 0)) != int(back_h.loc[label, k]):
                    fails.append(f"read back from disk, {pop}, {label}: {int(n_.get(k, 0))} units are '{k}' in agreement_by_unit.csv ({col}) and {int(back_h.loc[label, k])} in agreement_summary.csv")
            if int(n_.get("insufficient_forest", 0)) != int(back_h.loc[label, "n_insufficient_forest"]) or int(n_.get("zone_model_excluded", 0)) != int(back_h.loc[label, "n_excluded_by_zone_model"]):
                fails.append(f"read back from disk, {pop}, {label}: the units of insufficient forest, or those shut out by their zone model, differ between the two tables")
    if list(back_u["unit_id"]) != list(units["unit_id"]) or int(back_s["delivered"].sum()) != len(LEVELS):
        fails.append("agreement_by_unit.csv read back from disk does not hold the layer's units in order, or the summary does not mark exactly one delivered row per unit type")
    stop_if_failed("reading the written tables back (the tables are on disk and are NOT to be used)")
    blank = lambda t: {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}
    H = key(HEADLINE_POPULATION, "all units")
    with open(OUT / "agreement.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/02_build_agreement.py", "script_sha256": sha256(__file__), "run_utc": started,
                   "inputs": inputs + [{"path": f"20_degradation/{n}", "sha256": sha256(OUT / n), "role": "the source's own summary table, checked against"} for n in ("hansen_loss_by_canopy_band.csv", "corestack_by_unit_level.csv")],
                   "definitions": {"measures": ["Hansen tree-cover loss", "CoRE Stack tree-change classes 2017-2023"], "not_in_this_table": "NIRv (a reported column since 7 Oct 2026)",
                                   "reference_land": "treecover2000 > 10 (canopy bands gt10le30 and gt30)", "windows": {w: {"hansen_loss_years": list(v), "is": WINDOW_IS[w]} for w, v in WINDOWS.items()},
                                   "headline_window": HEADLINE,
                                   "floor": {"minimum_reference_ha": MIN_REFERENCE_HA, "ruling": FLOOR_RULING, "sensitivity_floors_ha": [f for f in FLOORS if f != MIN_REFERENCE_HA]},
                                   "assessed": f"at least {MIN_REFERENCE_HA:g} ha of reference land on Hansen's grid and at least that much with a CoRE Stack class from -2 to 4",
                                   "populations": POPULATIONS, "headline_population": HEADLINE_POPULATION, "why_that_population_is_the_headline": HEADLINE_REASON,
                                   "flag": f"rate above the {FLAG_PERCENTILE}th percentile of the rates of the population's assessed units (above zero if that is zero); all unit types together; cut again for each population, window and floor",
                                   "cuts_at_the_delivered_floor": {f"{pop}__{w}": {"hansen": round(cuts[(pop, w, MIN_REFERENCE_HA)][0], 6), "corestack_degradation": round(cuts[(pop, w, MIN_REFERENCE_HA)][1], 6)}
                                                                   for (pop, w, f) in cuts if f == MIN_REFERENCE_HA},
                                   "corestack_flag_rate": "class -1 over the valued land",
                                   "intervals": {"primary": f"whole districts resampled, every unit in its assigned district (the columns _lo95 and _hi95 of the summary and the definitions table); percentiles 2.5 and 97.5 of {BOOTSTRAP} "
                                                            f"resamples, every fourth for the correlations; the population's flags are held fixed; seed {BOOTSTRAP_SEED}",
                                                 "alongside": f"agreement_intervals.csv: whole districts for the lgd_panchayat units with the outside_village units resampled singly, and every unit resampled singly; seed {BOOTSTRAP_SEED + 1}",
                                                 "district_of_an_outside_village_unit": "10_units/outside_village_district.csv - assigned, not surveyed: see docs/UNITS.md"}},
                   "checks_passed": {**checks, "summary_counts_recounted_from_the_per_unit_table_read_back_from_disk": True, "zone_models_hold_every_assessed_unit_and_every_unit_flagged_by_both": True,
                                     "assessed_excluded_and_insufficient_add_up_to_the_layer_in_every_population": True, "districts": int(len(set(district)))},
                   "counts": {"units": int(n_units), "assessed": int(assessed.sum()), "in_the_headline_population": int(head_pop.sum()),
                              "by_level": {lab: {k: int(v) for k, v in by_unit.loc[(by_unit['unit_level'] == lv) if lv else slice(None), "agreement_class"].value_counts().items()} for lab, lv in LEVELS.items()},
                              "by_level_all_assessed": {lab: {k: int(v) for k, v in by_unit.loc[(by_unit['unit_level'] == lv) if lv else slice(None), "agreement_class_all_assessed"].value_counts().items()} for lab, lv in LEVELS.items()},
                              "outside_village_units_district": {"no_possible_check": int(no_check.sum()), "moved_off_the_polygons_name": int(moved.sum()), "polygon_has_no_name": int(no_name.sum()), "ambiguous": int(ambiguous.sum()),
                                                                 "one_check_contradicts_the_district": int(one_check.sum())}},
                   "tables": {name: {"rows": int(len(t)), "columns": int(len(t.columns)), "blank_cells": blank(t)} for name, t in out_tables.items()},
                   "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__}}, fh, indent=2)

    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 60)
    print(f"\nagreement_by_unit.csv: n = {n_units:,} units; assessed (at least {MIN_REFERENCE_HA:g} ha of reference land on both grids): {int(assessed.sum()):,}; insufficient forest: {int((~assessed).sum()):,}; "
          f"in the headline population ({POPULATIONS[HEADLINE_POPULATION]}): {int(head_pop.sum()):,}")
    show = ["population", "units", "n_assessed", "n_excluded_by_zone_model", "both", "both_expected_if_unrelated", "both_observed_over_expected", "both_observed_over_expected_lo95", "both_observed_over_expected_hi95",
            "odds_ratio", "odds_ratio_lo95", "odds_ratio_hi95", "odds_ratio_within_districts", "odds_ratio_within_districts_lo95", "odds_ratio_within_districts_hi95", SP + "degradation", SP + "degradation_lo95", SP + "degradation_hi95", SP + "improvement", SP + "improvement_lo95", SP + "improvement_hi95"]
    print(f"\nagreement_summary.csv: n = {len(summary)} rows; shown: the headline window at {MIN_REFERENCE_HA:g} ha, every population (intervals: whole districts resampled)")
    print(summary[(summary.window == HEADLINE) & (summary.minimum_reference_ha == MIN_REFERENCE_HA)][show].T.to_string(header=False))
    print(f"\nthe floors, headline population and all assessed, all units:")
    print(summary[(summary.window == HEADLINE) & (summary.units == "all units") & (summary.population != "eastern_plateau_only")][["population", "minimum_reference_ha", "lowest_land_class_admitted_ha", "repeatability_of_that_class_2001_2025",
          "n_assessed", "both", "both_expected_if_unrelated", "odds_ratio", "odds_ratio_lo95", "odds_ratio_hi95"]].to_string(index=False))
    print(f"\nagreement_intervals.csv: n = {len(three_ways)} rows; all units:")
    print(three_ways[three_ways.units == "all units"][["population", "statistic", "estimate", "lo95_districts", "hi95_districts", "lo95_lgd_districts_outside_singly", "hi95_lgd_districts_outside_singly", "lo95_units_singly", "hi95_units_singly"]].to_string(index=False))
    print(three_ways[three_ways.statistic == "odds_ratio"][["population", "units", "n_assessed", "n_outside_village", "districts_resampled_primary", "districts_resampled_lgd_only_design", "outside_village_assessed_district_has_no_possible_check",
          "outside_village_assessed_moved_off_the_polygons_name", "outside_village_assessed_ambiguous", "outside_village_assessed_one_check_contradicts_the_district"]].to_string(index=False))
    print(f"\nagreement_by_zone.csv: n = {len(by_zone)} rows")
    print(by_zone.T.to_string(header=False))
    print(f"\nagreement_definitions.csv: n = {len(definitions)} rows; all units:")
    print(definitions[definitions.units == "all units"][["population", "corestack_flag_is", "corestack_rate_cut", "both", "both_expected_if_unrelated", "both_observed_over_expected", "odds_ratio", "odds_ratio_lo95", "odds_ratio_hi95"]].to_string(index=False))
    print(f"\nagreement_floor_repeatability.csv: n = {len(repeat)} rows")
    print(repeat.drop(columns="land").to_string(index=False))
    print(f"\ndone. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
