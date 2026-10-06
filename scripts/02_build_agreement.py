#!/usr/bin/env python3
"""
Stage 1 - the three measures of forest condition set beside one another, pixel by pixel and unit by unit.

    python scripts/02_build_agreement.py --units 10_units/units.gpkg

In : --units    the stage-0 layer and its Earth Engine table asset (see 02_upload_units_asset.py)
     projects/<project>/assets/ictd/nirv_std_<layer stem>       the stored date-standardised yearly NIRv of every grid cell
                                                                 (02_export_nirv_yearly.py), band std_<season>
     20_degradation/nirv_scenes.csv, nirv_observations.provenance.json, nirv_yearly.provenance.json
                                                                 the scenes behind it and the records of the two exports
     UMD/hansen/global_forest_change_2025_v1_13                  bands treecover2000, lossyear
     projects/corestack-trees/assets/tree_characteristics/overall_change_2017_2023
     20_degradation/hansen_loss_by_canopy_band_by_unit.csv, nirv_by_unit_bands.csv, corestack_by_unit_bands.csv
                                                                 the three sources' own tables: this script's margins
                                                                 are checked against them before anything is written
Out: 20_degradation/ and nowhere else
     agreement_by_unit.csv            per unit: the eight cells of the headline table, rates, and which measures flag it
     agreement_cells_by_unit.csv      per unit: every cell of both cross-tabulations
     agreement_summary.csv            all units, lgd_panchayat units, outside_village units: cells and margins
     agreement_pairs.csv              every pair of flags: overlap, overlap expected by chance, odds ratio, conditional rates
     agreement_units.csv              unit by unit: rank agreement of the three rates, and the units all three flag
     agreement_positive_control.csv   does NIRv see what Hansen dates? its flags on Hansen-loss pixels, by year of loss
     agreement.provenance.json        inputs, UTC run time, definitions, checks, n and missingness

THE THREE MEASURES DO NOT MEASURE THE SAME THING, and the table is built so that this can be seen, not hidden.
  Hansen      a year in which a 30 m pixel's tree cover was removed outright
  NIRv        canopy greenness of a pixel around 1 December, season by season: the DATE-STANDARDISED yearly value of
              02_build_nirv.py (every clear pass moved to 1 December by the pixel's own rate), not the first design's
  CoRE Stack  a class of change between two three-year periods, inside its own tree mask: tree cover lost (-2),
              canopy density or height down a class (-1), up a class (1)
A cleared pixel should show in all three (Hansen loss, NIRv lower, CoRE -2). A pixel that thinned under a standing
canopy can show only in NIRv and CoRE -1. So CoRE Stack is kept in four states, not two.

TWO VERSIONS. THE FIRST IS THE HEADLINE.
1. THE COMMON WINDOW: change between the three years to mid-2019 and the three years from mid-2022.
     CoRE Stack compares the agricultural years 2016-17 to 2018-19 with 2022-23 to 2024-25 (each of its "years" is
     the mode of three). So:
     NIRv    LOWER  = every one of the seasons (Nov-Dec) 2022, 2023, 2024 below every one of 2016, 2017, 2018;
             HIGHER = the mirror; otherwise NEITHER. All six seasons needed. Both sets of seasons lie inside CoRE
             Stack's two periods. (Not a trend test: over seven seasons a trend test cannot see a one-step loss.)
     Hansen  loss dated 2019, 2020, 2021 or 2022: the calendar years between the two periods. A loss dated 2023
             cannot make NIRv "lower" by this rule (the 2022 season precedes it), so it is not in the window; the
             positive-control table shows the losses of 2016-2018 and of 2023 beside it.
     CoRE    class -2 (LOST), -1 (DEGRADATION), 1 (IMPROVEMENT), or any of 0, 2, 3, 4 (REST).
   REFERENCE LAND, the same for all three: grid cells with treecover2000 > 10, where CoRE Stack has a class from
   -2 to 4 (so inside its tree mask in at least one period, and not "missing"), and where NIRv has all six
   seasons. What that leaves out, and why, is tallied per unit. Every reference cell is in exactly one of
   2 x 3 x 4 = 24 cells, separately for 10 < treecover2000 <= 30 and treecover2000 > 30.
   THE HEADLINE TABLE is those 24 folded to 2 x 2 x 2: Hansen loss 2019-2022 x NIRv lower x CoRE class -1.
   Improvement (class 1) and NIRv higher are in the cross-tabulation as placebos: if NIRv "lower" is as common
   on CoRE "improvement" as on CoRE "degradation", the two do not agree, whatever the overlap in hectares.
2. THE FULL SPAN, each measure over all it covers - which is NOT one period, and is reported for that reason only:
     Hansen loss in any year 2001-2025; NIRv declining / increasing / neither by the 13-season test of
     02_build_nirv.py (2013-2025); CoRE as above (2017-2023). Reference: treecover2000 > 10 with a CoRE class from
     -2 to 4 and an NIRv trend. A pixel cleared in 2005 and regrown is "Hansen loss" and "NIRv increasing" here:
     disagreement by construction. Do not read this version as a test of agreement.

EVERYTHING IS ON HANSEN'S GRID (EPSG:4326, 0.00025 degrees). NIRv is stored on it. CoRE Stack is 25 m: each grid cell
takes the CoRE pixel that contains its centre, so the CoRE margins here differ slightly from 02_build_corestack.py's,
which are summed on CoRE's own grid; the difference is measured and reported. The NIRv and Hansen flags are built by
the same code as 02_build_nirv.py (imported, not copied), from its date-standardised yearly values.

WHAT "AGREEMENT" IS MEASURED BY. For two flags A and B on the reference land:
  expected overlap by chance   area(A) x area(B) / reference area: what two unrelated flags of these sizes share
  observed / expected          1 = no better than chance
  odds ratio                   (A and B)(neither) / (A only)(B only), with a 95 per cent interval from resampling
                               UNITS (pixels are not independent; units are the nearest thing to it)
  conditional rates            the share of A that is also B, beside the share of not-A that is B
Overlap in hectares alone says nothing: two flags that each cover a tenth of the land share a hundredth by chance.

UNIT BY UNIT. For each unit with at least 50 ha of reference land: the three rates (Hansen loss, NIRv lower, CoRE
class -1, each as a share of its reference land) and the two net rates (NIRv lower minus higher; CoRE -1 minus 1).
A unit is FLAGGED by a measure if its rate is above the 80th percentile of such units (or above zero, if the 80th
percentile is zero). agreement_units.csv gives the rank correlations and how many units are flagged by all three,
two, one and none, beside the number expected if the three flags were unrelated. Where all three flag a unit the
claim that it degraded is as strong as these data can make it; where they disagree the table says which disagree.

Needs earthengine-api, geopandas, pyproj, pandas, numpy, scipy; scripts/_ee_units.py, 02_build_nirv.py (and through it
02_export_nirv_yearly.py and 02_export_nirv_observations.py), 02_build_corestack.py.
"""
import argparse, importlib.util, itertools, json, sys
from pathlib import Path

import ee
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ee_units as eu
from _ee_units import OUT, ROOT, fail, now, sha256, stop_if_failed


def load(name):
    """A sibling script as a module: its definitions are used here, not copied."""
    path = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(name[:-3].replace("02_build_", ""), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NIRV = load("02_build_nirv.py")
CORE = load("02_build_corestack.py")
HANSEN, GRID = NIRV.HANSEN, NIRV.GRID
TREE = ("gt10le30", "gt30")                                  # the two canopy bands that make up treecover2000 > 10
HANSEN_WINDOW = (2019, 2022)                                 # loss years between CoRE Stack's two periods
H_STATES = ("h0", "h1")                                      # no loss in the window / loss in the window
N_STATES = ("nl", "nn", "nh")                                # NIRv lower / neither / higher
T_STATES = ("nd", "nn", "ni")                                # full span: NIRv declining / neither / increasing
C_STATES = {"lost": (-2,), "deg": (-1,), "imp": (1,), "rest": (0, 2, 3, 4)}
C_VALUED = (-2, -1, 0, 1, 2, 3, 4)
LOSS_GROUPS = {"none": (0, 0), "2001_2012": (1, 12), "2013_2015": (13, 15), "2016_2018": (16, 18), "2019_2020": (19, 20),
               "2021_2022": (21, 22), "2023": (23, 23), "2024_2025": (24, 25)}
CONTROL = ("land", "evalid", "lower", "higher", "trend", "declining", "increasing")
UNIT_MIN_REFERENCE_HA = 50.0
FLAG_PERCENTILE = 80
BOOTSTRAP, BOOTSTRAP_SEED = 2000, 20261008
CORE_GRID_TOLERANCE = 0.05                                   # CoRE class -1 on treecover2000 > 10, this grid against CoRE's own, all units
GROUPS, TILE_SCALE = 8, 4


def images(yearly, tables):
    """0/1 images of every flag, all on whatever grid the reduction asks for (Hansen's). `yearly` is the stored yearly values."""
    annual, _ = NIRV.stored_standardised(yearly)               # the date-standardised yearly values, as stored
    px = NIRV.pixel_image(annual)
    tier = NIRV.flags(px, tables)
    in_band, _, cover, lossyear = NIRV.canopy_images()
    value = ee.ImageCollection([ee.Image(f"{CORE.CHANGE}/{z}").select(0) for z in CORE.ZONES]).mosaic()       # as 02_build_corestack.py: the last zone listed wins
    full = lambda image: image.unmask(0, False)
    c = {name: full(value.eq(codes[0]) if len(codes) == 1 else value.remap(list(codes), [1] * len(codes), 0)) for name, codes in C_STATES.items()}
    e_valid, e_lower, e_higher = px.select("e_valid").unmask(0), px.select("e_lower").unmask(0), px.select("e_higher").unmask(0)
    trend, declining, increasing = tier["full"]["trend"], tier["full"]["declining"], tier["full"]["increasing"]
    return {"in_band": {b: in_band[b] for b in TREE}, "lossyear": lossyear,
            "h": {"h1": lossyear.gte(HANSEN_WINDOW[0] - 2000).And(lossyear.lte(HANSEN_WINDOW[1] - 2000))}, "hf": {"h1": lossyear.gte(1)},
            "n": {"nl": e_lower, "nh": e_higher, "valid": e_valid}, "t": {"nd": declining, "ni": increasing, "valid": trend},
            "c": c, "c_valued": full(value.remap(list(C_VALUED), [1] * len(C_VALUED), 0)), "c_missing": full(value.eq(5)), "c_any": full(value.mask().gt(0))}


def unit_bands(yearly, tables):
    """Square metres per unit for every cell and every check. Returns the image and its band names in order."""
    f = images(yearly, tables)
    area = ee.Image.pixelArea()
    tree = f["in_band"]["gt10le30"].Or(f["in_band"]["gt30"])
    named = [("area_m2", area)]
    states = lambda flags, names: {names[0]: flags[names[0]], names[2]: flags[names[2]], names[1]: flags[names[0]].Or(flags[names[2]]).Not()} if len(names) == 3 else None
    n3, t3 = states(f["n"], N_STATES), states(f["t"], T_STATES)
    h2, hf2 = {"h1": f["h"]["h1"], "h0": f["h"]["h1"].Not()}, {"h1": f["hf"]["h1"], "h0": f["hf"]["h1"].Not()}
    for b, cond in f["in_band"].items():                                               # the common window, by canopy band
        ref = cond.And(f["c_valued"]).And(f["n"]["valid"])
        named.append((f"land_{b}_m2", area.multiply(cond)))
        named.append((f"cref_{b}_m2", area.multiply(ref)))
        named.append((f"x_{b}_novalue_m2", area.multiply(cond.And(f["c_any"].Not()))))
        named.append((f"x_{b}_missing_m2", area.multiply(cond.And(f["c_missing"]))))
        named.append((f"x_{b}_nirv6_m2", area.multiply(cond.And(f["n"]["valid"].Not()))))
        named.append((f"m_{b}_hloss_m2", area.multiply(cond.And(f["h"]["h1"]))))       # margins over ALL the band's land, for the checks against the sources' own tables
        named.append((f"m_{b}_nlower_m2", area.multiply(cond.And(f["n"]["nl"]))))
        named.append((f"m_{b}_nvalid_m2", area.multiply(cond.And(f["n"]["valid"]))))
        named.append((f"m_{b}_cdeg_m2", area.multiply(cond.And(f["c"]["deg"]))))
        named.append((f"m_{b}_cvalue_m2", area.multiply(cond.And(f["c_any"]))))
        for h, n, c in itertools.product(H_STATES, N_STATES, C_STATES):
            named.append((f"c_{b}_{h}_{n}_{c}_m2", area.multiply(ref.And(h2[h]).And(n3[n]).And(f["c"][c]))))
    reff = tree.And(f["c_valued"]).And(f["t"]["valid"])                                # the full span, treecover2000 > 10 together
    named.append(("fref_m2", area.multiply(reff)))
    named.append(("xf_notrend_m2", area.multiply(tree.And(f["t"]["valid"].Not()))))
    for h, n, c in itertools.product(H_STATES, T_STATES, C_STATES):
        named.append((f"f_{h}_{n}_{c}_m2", area.multiply(reff.And(hf2[h]).And(t3[n]).And(f["c"][c]))))
    control = {"land": None, "evalid": f["n"]["valid"], "lower": f["n"]["nl"], "higher": f["n"]["nh"], "trend": f["t"]["valid"], "declining": f["t"]["nd"], "increasing": f["t"]["ni"]}
    for g, (lo, hi) in LOSS_GROUPS.items():                                            # the positive control, treecover2000 > 10 together
        in_group = tree.And(f["lossyear"].gte(lo)).And(f["lossyear"].lte(hi))
        for k, flag in control.items():
            named.append((f"p_{g}_{k}_m2", area.multiply(in_group if flag is None else in_group.And(flag))))
    names = [n for n, _ in named]
    return ee.Image.cat([im.rename(n) for n, im in named]), names


# ---- the arithmetic, on plain arrays ---------------------------------------------------------------------------------
def fold(cells, h_states, n_states, a, b):
    """The 2 x 2 of two flags from an array of cells [..., h, n, c]. A flag is ("h", "h1"), ("n", "nl"), ("c", "deg") and so on."""
    axis = {"h": (-3, h_states), "n": (-2, n_states), "c": (-1, tuple(C_STATES))}

    def member(flag):
        ax, names = axis[flag[0]]
        shape = [1, 1, 1]
        sel = np.array([name == flag[1] for name in names])
        shape[ax] = len(names)
        return sel.reshape(shape)

    A, B = member(a), member(b)
    tot = lambda mask: (cells * mask).sum(axis=(-3, -2, -1))
    return tot(A & B), tot(A & ~B), tot(~A & B), tot(~A & ~B)


def pair_stats(n11, n10, n01, n00):
    total = n11 + n10 + n01 + n00
    a, b = n11 + n10, n11 + n01
    with np.errstate(divide="ignore", invalid="ignore"):
        expected = a * b / total
        return {"both": n11, "expected_by_chance": expected, "observed_over_expected": n11 / expected, "odds_ratio": (n11 * n00) / (n10 * n01),
                "share_of_first_that_is_second": n11 / a, "share_of_not_first_that_is_second": n01 / (n01 + n00),
                "share_of_second_that_is_first": n11 / b, "share_of_not_second_that_is_first": n10 / (n10 + n00), "first": a, "second": b, "reference": total}


def pairs_table(cells, sel_groups, h_states, n_states, pairs, window, land, rng):
    """One row per (group of units, pair of flags): the statistics, with an interval for the odds ratio from resampling units."""
    rows = []
    for gname, sel in sel_groups.items():
        sub = cells[sel]
        boot_cells = np.stack([sub[rng.integers(0, len(sub), len(sub))].sum(axis=0) for _ in range(BOOTSTRAP)]) if len(sub) else None
        for a, b in pairs:
            s = pair_stats(*[v.sum() for v in fold(sub, h_states, n_states, a, b)])
            bs = pair_stats(*fold(boot_cells, h_states, n_states, a, b))["odds_ratio"] if len(sub) else np.array([np.nan])
            bs = bs[np.isfinite(bs)]
            lo, hi = (np.percentile(bs, [2.5, 97.5]) if len(bs) >= BOOTSTRAP * 0.9 else (np.nan, np.nan))
            km2 = lambda v: round(float(v) / 1e6, 3)
            r4 = lambda v: round(float(v), 4) if np.isfinite(v) else None
            rows.append({"window": window, "land": land, "units": gname, "n_units": int(sel.sum()), "first": "_".join(a), "second": "_".join(b),
                         "reference_km2": km2(s["reference"]), "first_km2": km2(s["first"]), "second_km2": km2(s["second"]), "both_km2": km2(s["both"]),
                         "expected_by_chance_km2": km2(s["expected_by_chance"]) if np.isfinite(s["expected_by_chance"]) else None,
                         "observed_over_expected": r4(s["observed_over_expected"]), "odds_ratio": r4(s["odds_ratio"]), "odds_ratio_lo95": r4(lo), "odds_ratio_hi95": r4(hi),
                         "pct_of_first_that_is_second": r4(100 * s["share_of_first_that_is_second"]), "pct_of_not_first_that_is_second": r4(100 * s["share_of_not_first_that_is_second"]),
                         "pct_of_second_that_is_first": r4(100 * s["share_of_second_that_is_first"]), "pct_of_not_second_that_is_first": r4(100 * s["share_of_not_second_that_is_first"])})
    return rows


def headline(cells, h_states, n_states, n_flag):
    """The eight cells of (Hansen loss) x (NIRv lower, or declining) x (CoRE class -1), in the order of HEADLINE_CELLS."""
    h1 = np.array([s == "h1" for s in h_states])[:, None, None]
    n1 = np.array([s == n_flag for s in n_states])[None, :, None]
    c1 = np.array([s == "deg" for s in C_STATES])[None, None, :]
    out = []
    for hv, nv, cv in itertools.product((True, False), repeat=3):
        out.append((cells * ((h1 == hv) & (n1 == nv) & (c1 == cv))).sum(axis=(-3, -2, -1)))
    return out


HEADLINE_CELLS = ["hansen_nirv_corestack", "hansen_nirv_only", "hansen_corestack_only", "hansen_only", "nirv_corestack_only", "nirv_only", "corestack_only", "none"]


def cell_arrays(m):
    """The cells as arrays [unit, h, n, c]: the common window by canopy band and for treecover2000 > 10, and the full span."""
    def cell(stub, n_states):
        return np.stack([np.stack([np.stack([m[stub.format(h=h, n=n, c=c)].to_numpy(float) for c in C_STATES], axis=-1) for n in n_states], axis=-2) for h in H_STATES], axis=-3)

    common = {b: cell("c_" + b + "_{h}_{n}_{c}_m2", N_STATES) for b in TREE}
    common["gt10"] = common["gt10le30"] + common["gt30"]
    return common, cell("f_{h}_{n}_{c}_m2", T_STATES)


def check_cells(m, common, fullspan):
    """The arithmetic the cells must obey, whatever the data."""
    tol = 0.02
    for b in TREE:
        if np.abs(common[b].sum(axis=(1, 2, 3)) - m[f"cref_{b}_m2"]).max() > tol:
            fail(f"{b}: the 24 cells do not add up to the reference land")
        if (m[f"cref_{b}_m2"] > m[f"land_{b}_m2"] + tol).any() or (m[f"cref_{b}_m2"] > m[f"m_{b}_nvalid_m2"] + tol).any():
            fail(f"{b}: the reference land exceeds the band's land, or the land with all six NIRv seasons")
        left_out = m[f"land_{b}_m2"] - m[f"cref_{b}_m2"]
        if (left_out > m[f"x_{b}_novalue_m2"] + m[f"x_{b}_missing_m2"] + m[f"x_{b}_nirv6_m2"] + tol).any():
            fail(f"{b}: land outside the reference that none of the three reasons accounts for")
    if np.abs(fullspan.sum(axis=(1, 2, 3)) - m["fref_m2"]).max() > tol:
        fail("full span: the 24 cells do not add up to the reference land")
    land_tree = m[[f"land_{b}_m2" for b in TREE]].sum(axis=1)
    if np.abs(m[[f"p_{g}_land_m2" for g in LOSS_GROUPS]].sum(axis=1) - land_tree).max() > tol:
        fail("positive control: the loss-year groups do not add up to the land with treecover2000 > 10")
    for g in LOSS_GROUPS:
        if (m[f"p_{g}_lower_m2"] + m[f"p_{g}_higher_m2"] > m[f"p_{g}_evalid_m2"] + tol).any() or (m[f"p_{g}_declining_m2"] + m[f"p_{g}_increasing_m2"] > m[f"p_{g}_trend_m2"] + tol).any():
            fail(f"positive control {g}: flags exceed the land they are defined on")
    return land_tree


def check_margins(m, sources):
    """This table's margins against the three sources' own per-unit tables. Hansen and NIRv must be equal; CoRE is on another grid."""
    hansen = pd.read_csv(sources["hansen"], dtype={"unit_id": str}).set_index("unit_id").loc[m["unit_id"]]
    nirv = pd.read_csv(sources["nirv"], dtype={"unit_id": str}).set_index("unit_id").loc[m["unit_id"]]
    core = pd.read_csv(sources["corestack"], dtype={"unit_id": str}).set_index("unit_id").loc[m["unit_id"]]
    years, checks = range(HANSEN_WINDOW[0], HANSEN_WINDOW[1] + 1), {}
    for b in TREE:
        theirs = hansen[[f"loss_ha_{b}_{y}" for y in years]].sum(axis=1).to_numpy()
        gap = np.abs(m[f"m_{b}_hloss_m2"].to_numpy() / 1e4 - theirs)
        checks[f"hansen_loss_{HANSEN_WINDOW[0]}_{HANSEN_WINDOW[1]}_{b}"] = {"this_ha": float(m[f"m_{b}_hloss_m2"].sum() / 1e4), "source_table_ha": float(theirs.sum()), "largest_gap_for_a_unit_ha": float(gap.max())}
        if gap.max() > 0.001:
            fail(f"Hansen loss {HANSEN_WINDOW[0]}-{HANSEN_WINDOW[1]} on {b}: differs from {sources['hansen'].name} by up to {gap.max():.4f} ha in a unit")
        for mine, col in ((f"m_{b}_nlower_m2", f"std_epoch_{b}_lower_ha"), (f"m_{b}_nvalid_m2", f"std_epoch_{b}_valid_ha")):
            gap = np.abs(m[mine].to_numpy() / 1e4 - nirv[col].to_numpy())
            checks[f"nirv_{col}"] = {"this_ha": float(m[mine].sum() / 1e4), "source_table_ha": float(nirv[col].sum()), "largest_gap_for_a_unit_ha": float(gap.max())}
            if gap.max() > 0.001:
                fail(f"NIRv {col}: differs from {sources['nirv'].name} by up to {gap.max():.4f} ha in a unit")
        theirs = core[f"class_degradation_ha_{b}"].to_numpy()
        mine = m[f"m_{b}_cdeg_m2"].to_numpy() / 1e4
        rel = (mine.sum() - theirs.sum()) / theirs.sum() if theirs.sum() else float("nan")
        checks[f"corestack_degradation_{b}"] = {"this_grid_ha": float(mine.sum()), "corestack_grid_ha": float(theirs.sum()), "relative_difference": float(rel),
                                                 "note": "not expected to be equal: here each Hansen grid cell takes the CoRE pixel at its centre"}
        if not abs(rel) <= CORE_GRID_TOLERANCE:
            fail(f"CoRE class -1 on {b}: {mine.sum():,.0f} ha on this grid against {theirs.sum():,.0f} on CoRE's own ({rel:+.1%}); more than the {CORE_GRID_TOLERANCE:.0%} a change of grid can explain")
    return checks


def build_tables(m, common, fullspan, land_tree):
    """Every table, from the per-unit sums. Returns ({file name: table}, the cuts used for the unit flags)."""
    level = m["unit_level"].to_numpy()
    groups = {"all units": np.ones(len(m), bool), **{k: level == k for k in sorted(set(level))}}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    pairs_c = [(("h", "h1"), ("n", "nl")), (("h", "h1"), ("c", "lost")), (("h", "h1"), ("c", "deg")), (("h", "h1"), ("c", "imp")), (("h", "h1"), ("n", "nh")),
               (("n", "nl"), ("c", "lost")), (("n", "nl"), ("c", "deg")), (("n", "nl"), ("c", "imp")), (("n", "nh"), ("c", "deg")), (("n", "nh"), ("c", "imp")), (("n", "nh"), ("c", "lost"))]
    pairs_f = [(("h", "h1"), ("n", "nd")), (("h", "h1"), ("n", "ni")), (("h", "h1"), ("c", "lost")), (("h", "h1"), ("c", "deg")),
               (("n", "nd"), ("c", "lost")), (("n", "nd"), ("c", "deg")), (("n", "nd"), ("c", "imp")), (("n", "ni"), ("c", "deg")), (("n", "ni"), ("c", "imp"))]
    pair_rows = []
    for land in ("gt10", "gt10le30", "gt30"):
        pair_rows += pairs_table(common[land], groups, H_STATES, N_STATES, pairs_c, "common window", land, rng)
    pair_rows += pairs_table(fullspan, groups, H_STATES, T_STATES, pairs_f, "full span (not one period)", "gt10", rng)
    pairs = pd.DataFrame(pair_rows)

    summary_rows = []
    for window, land, cells, ns, nflag in ([("common window", land, common[land], N_STATES, "nl") for land in ("gt10", "gt10le30", "gt30")]
                                           + [("full span (not one period)", "gt10", fullspan, T_STATES, "nd")]):
        for gname, sel in groups.items():
            sub = cells[sel].sum(axis=0)
            ref = float(sub.sum())
            row = {"window": window, "land": land, "units": gname, "n_units": int(sel.sum()), "reference_km2": round(ref / 1e6, 2)}
            if window == "common window":
                lb = TREE if land == "gt10" else (land,)
                tot = lambda stub: float(sum(m.loc[sel, stub.format(b=b)].sum() for b in lb))
                row["land_km2"] = round(tot("land_{b}_m2") / 1e6, 2)
                row["left_out_no_corestack_value_km2"], row["left_out_corestack_missing_km2"], row["left_out_nirv_lacks_a_season_km2"] = (round(tot(s) / 1e6, 2) for s in ("x_{b}_novalue_m2", "x_{b}_missing_m2", "x_{b}_nirv6_m2"))
            else:
                row["land_km2"] = round(float(land_tree[sel].sum()) / 1e6, 2)
                row["left_out_nirv_has_no_trend_km2"] = round(float(m.loc[sel, "xf_notrend_m2"].sum()) / 1e6, 2)
            eight = headline(sub, H_STATES, ns, nflag)
            for name, v in zip(HEADLINE_CELLS, eight):
                row[f"{name}_km2"] = round(float(v) / 1e6, 3)
            margins = {"hansen": sub[1].sum(), "nirv_down": sub[:, 0].sum(), "nirv_up": sub[:, 2].sum(),
                       "corestack_lost": sub[:, :, 0].sum(), "corestack_degradation": sub[:, :, 1].sum(), "corestack_improvement": sub[:, :, 2].sum()}
            for k, v in margins.items():
                row[f"{k}_km2"], row[f"{k}_pct_of_reference"] = round(float(v) / 1e6, 2), round(100 * float(v) / ref, 3) if ref else None
            exp3 = margins["hansen"] * margins["nirv_down"] * margins["corestack_degradation"] / ref ** 2 if ref else float("nan")
            row["all_three_expected_by_chance_km2"] = round(float(exp3) / 1e6, 4) if ref else None
            row["all_three_observed_over_expected"] = round(float(eight[0] / exp3), 3) if ref and exp3 > 0 else None
            summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)

    # per unit
    ha = lambda v: np.round(np.asarray(v, float) / 1e4, 4)
    cg = common["gt10"]
    ref = cg.sum(axis=(1, 2, 3))
    by_unit = pd.DataFrame({"unit_id": m["unit_id"], "unit_level": m["unit_level"], "outside_village": m["outside_village"],
                            "land_treecover2000_gt10_ha": ha(land_tree), "reference_ha": ha(ref)})
    for name, v in zip(HEADLINE_CELLS, headline(cg, H_STATES, N_STATES, "nl")):
        by_unit[f"{name}_ha"] = ha(v)
    marg = {"hansen_loss_2019_2022": cg[:, 1].sum(axis=(1, 2)), "nirv_lower": cg[:, :, 0].sum(axis=(1, 2)), "nirv_higher": cg[:, :, 2].sum(axis=(1, 2)),
            "corestack_lost": cg[:, :, :, 0].sum(axis=(1, 2)), "corestack_degradation": cg[:, :, :, 1].sum(axis=(1, 2)), "corestack_improvement": cg[:, :, :, 2].sum(axis=(1, 2))}
    for k, v in marg.items():
        by_unit[f"{k}_ha"] = ha(v)
    big = ref >= UNIT_MIN_REFERENCE_HA * 1e4
    with np.errstate(divide="ignore", invalid="ignore"):
        rate = {"hansen": marg["hansen_loss_2019_2022"] / ref, "nirv": marg["nirv_lower"] / ref, "corestack": marg["corestack_degradation"] / ref,
                "nirv_net": (marg["nirv_lower"] - marg["nirv_higher"]) / ref, "corestack_net": (marg["corestack_degradation"] - marg["corestack_improvement"]) / ref}
    flagged, cuts = {}, {}
    for k in ("hansen", "nirv", "corestack"):
        by_unit[f"rate_{k}"] = np.where(ref > 0, rate[k], np.nan).round(6)
        cuts[k] = float(np.percentile(rate[k][big], FLAG_PERCENTILE)) if big.any() else float("nan")
        flagged[k] = big & (rate[k] > cuts[k])
        by_unit[f"flagged_{k}"] = np.where(big, flagged[k], None)
    for k in ("nirv_net", "corestack_net"):
        by_unit[f"rate_{k}"] = np.where(ref > 0, rate[k], np.nan).round(6)
    by_unit["flagged_by"] = np.where(big, flagged["hansen"].astype(int) + flagged["nirv"].astype(int) + flagged["corestack"].astype(int), None)
    by_unit["in_unit_level_comparison"] = big
    by_unit["full_span_reference_ha"] = ha(fullspan.sum(axis=(1, 2, 3)))
    for name, v in zip(HEADLINE_CELLS, headline(fullspan, H_STATES, T_STATES, "nd")):
        by_unit[f"full_span_{name}_ha"] = ha(v)

    cells_by_unit = pd.DataFrame({"unit_id": m["unit_id"], "unit_level": m["unit_level"], "outside_village": m["outside_village"]})
    for c in m.columns:
        if c.startswith(("c_", "f_", "cref_", "fref_", "x_", "xf_", "land_")) and c.endswith("_m2"):
            cells_by_unit[c[:-3] + "_ha"] = ha(m[c])

    # unit by unit: rank agreement and the pattern of flags
    unit_rows = []
    for gname, sel0 in groups.items():
        sel = sel0 & big
        n = int(sel.sum())
        row = {"units": gname, "n_units_with_enough_reference_land": n, "of_units": int(sel0.sum()), "minimum_reference_ha": UNIT_MIN_REFERENCE_HA,
               "reference_km2_in_them": round(float(ref[sel].sum()) / 1e6, 1), "share_of_all_reference_land_pct": round(100 * float(ref[sel].sum() / ref[sel0].sum()), 2) if ref[sel0].sum() else None}
        for x, y in (("hansen", "nirv"), ("hansen", "corestack"), ("nirv", "corestack"), ("hansen", "nirv_net"), ("hansen", "corestack_net"), ("nirv_net", "corestack_net")):
            row[f"spearman_{x}_vs_{y}"] = round(float(spearmanr(rate[x][sel], rate[y][sel])[0]), 4) if n > 2 else None
        p = {k: float(flagged[k][sel].mean()) if n else float("nan") for k in flagged}
        for k in flagged:
            row[f"flagged_{k}"], row[f"cut_{k}_rate"] = int(flagged[k][sel].sum()), cuts[k]
        count = flagged["hansen"][sel].astype(int) + flagged["nirv"][sel].astype(int) + flagged["corestack"][sel].astype(int)
        ph, pn, pc = p["hansen"], p["nirv"], p["corestack"]
        expected = {3: ph * pn * pc, 2: ph * pn * (1 - pc) + ph * (1 - pn) * pc + (1 - ph) * pn * pc,
                    1: ph * (1 - pn) * (1 - pc) + (1 - ph) * pn * (1 - pc) + (1 - ph) * (1 - pn) * pc, 0: (1 - ph) * (1 - pn) * (1 - pc)}
        for k in (3, 2, 1, 0):
            row[f"flagged_by_{k}"] = int((count == k).sum())
            row[f"flagged_by_{k}_expected_if_unrelated"] = round(n * expected[k], 1) if n else None
        for x, y in (("hansen", "nirv"), ("hansen", "corestack"), ("nirv", "corestack")):
            row[f"flagged_by_both_{x}_and_{y}"] = int((flagged[x][sel] & flagged[y][sel]).sum())
            row[f"flagged_by_both_{x}_and_{y}_expected_if_unrelated"] = round(n * p[x] * p[y], 1) if n else None
        unit_rows.append(row)
    units_table = pd.DataFrame(unit_rows)

    # positive control
    control_rows = []
    for gname, sel in groups.items():
        for g in LOSS_GROUPS:
            t = {k: float(m.loc[sel, f"p_{g}_{k}_m2"].sum()) for k in CONTROL}
            pct = lambda x, y: round(100 * x / y, 3) if y else None
            control_rows.append({"units": gname, "n_units": int(sel.sum()), "hansen_loss_year": "no loss" if g == "none" else g.replace("_", "-"), "land_km2": round(t["land"] / 1e6, 3),
                                 "with_all_six_seasons_km2": round(t["evalid"] / 1e6, 3), "nirv_lower_pct": pct(t["lower"], t["evalid"]), "nirv_higher_pct": pct(t["higher"], t["evalid"]),
                                 "with_a_trend_km2": round(t["trend"] / 1e6, 3), "nirv_declining_pct": pct(t["declining"], t["trend"]), "nirv_increasing_pct": pct(t["increasing"], t["trend"])})
    control_table = pd.DataFrame(control_rows)
    return {"agreement_by_unit.csv": by_unit, "agreement_cells_by_unit.csv": cells_by_unit, "agreement_summary.csv": summary, "agreement_pairs.csv": pairs,
            "agreement_units.csv": units_table, "agreement_positive_control.csv": control_table}, cuts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", required=True, help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    ap.add_argument("--asset", help="the layer's table asset; default projects/<project>/assets/ictd/<layer stem>")
    a = ap.parse_args()
    started = now()
    project = eu.init(a.project)
    stem = Path(a.units).stem
    asset = a.asset or f"projects/{project}/assets/ictd/{stem}"
    obs_collection, std_collection = f"projects/{project}/assets/ictd/nirv_obs_{stem}", f"projects/{project}/assets/ictd/nirv_std_{stem}"
    units, fc, record = eu.load_units(a.units, asset)
    print(f"{a.units}: n = {len(units):,} units ({dict(units['unit_level'].value_counts())}); asset {asset}")
    sources = {"hansen": OUT / "hansen_loss_by_canopy_band_by_unit.csv", "nirv": OUT / "nirv_by_unit_bands.csv", "corestack": OUT / "corestack_by_unit_bands.csv"}
    for k, p in sources.items():
        if not p.exists():
            fail(f"{p.relative_to(ROOT)} is missing: build that source first (its figures are what this table's margins are checked against)")
    stop_if_failed("finding the three sources' tables")
    scenes, obs_prov, yearly_prov = NIRV.load_records(obs_collection, std_collection)
    stop_if_failed("reading the records of the two exports")
    blocks = set(yearly_prov["outputs_in_earth_engine"]["block_boxes"])
    have = {x["name"].split("/")[-1] for x in ee.data.listAssets({"parent": std_collection}).get("assets", [])}
    if blocks - have:
        fail(f"{len(blocks - have)} of {len(blocks)} blocks of stored yearly values are missing from {std_collection}")
    nirv_prov = json.load(open(OUT / "nirv.provenance.json")) if (OUT / "nirv.provenance.json").exists() else None
    made = [(i.get("recipe_sha256"), i.get("sha256")) for i in nirv_prov["inputs"]] if nirv_prov else []
    if (NIRV.YEARLY.RECIPE_SHA256 not in [x[0] for x in made] or sha256(OUT / "nirv_scenes.csv") not in [x[1] for x in made] or sha256(a.units) not in [x[1] for x in made]
            or nirv_prov["script_sha256"] != sha256(Path(__file__).with_name("02_build_nirv.py"))):
        fail("20_degradation/nirv_by_unit_bands.csv was not built by 02_build_nirv.py as it now is, from this layer, this scene list and stored yearly values of this recipe: run scripts/02_build_nirv.py again")
    stop_if_failed("finding the inputs")
    tables = {w: NIRV.critical_table(NIRV.SEASONS[w], NIRV.MIN_SEASONS[w]) for w in NIRV.SEASONS}
    _, yearly = NIRV.stored_images(obs_collection, std_collection)
    image, bands = unit_bands(yearly, tables)
    if image.bandNames().getInfo() != bands:
        fail("the per-unit image's bands are not the ones named")
        stop_if_failed("building the per-unit image")
    # the folder's name carries a fingerprint of what its tables hold, so that a table left by other code or other stored values is never reused
    folder = f"{asset}_agreement_parts_" + NIRV.fingerprint(image, repr(bands), str(GROUPS), str(TILE_SCALE), sha256(a.units), sha256(OUT / "nirv_scenes.csv"),
                                                            NIRV.OBS.RECIPE_SHA256, NIRV.YEARLY.RECIPE_SHA256, repr(GRID))
    print(f"{len(bands)} bands per unit; group tables in {folder.split('/')[-1]}", flush=True)
    raw, status, cleanup = eu.zonal(image, bands, fc, units, folder, f"{stem}_agreement", GRID, GROUPS, TILE_SCALE)
    m = units[["unit_id", "unit_level", "outside_village", "polygon_m2"]].merge(raw, on="unit_id", validate="one_to_one")
    area = eu.area_check(m)
    common, fullspan = cell_arrays(m)
    land_tree = check_cells(m, common, fullspan)
    stop_if_failed("checking the cells")
    checks = check_margins(m, sources)
    stop_if_failed("checking the margins against the three sources' own tables")
    print("OK  cells add up to the reference land; the Hansen and NIRv margins equal the sources' own tables unit by unit; the CoRE margin is within "
          + ", ".join(f"{checks[f'corestack_degradation_{b}']['relative_difference']:+.2%}" for b in TREE) + " of CoRE's own grid")
    out_tables, cuts = build_tables(m, common, fullspan, land_tree)
    summary, pairs, units_table, control_table = (out_tables[k] for k in ("agreement_summary.csv", "agreement_pairs.csv", "agreement_units.csv", "agreement_positive_control.csv"))

    OUT.mkdir(exist_ok=True)
    for name, t in out_tables.items():
        t.to_csv(OUT / name, index=False)
    blank = lambda t: {c: int(t[c].isna().sum()) for c in t.columns if t[c].isna().any()}
    with open(OUT / "agreement.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({
            "script": "scripts/02_build_agreement.py", "script_sha256": sha256(__file__),
            "uses": {n: sha256(Path(__file__).with_name(n)) for n in ("_ee_units.py", "02_build_nirv.py", "02_export_nirv_yearly.py", "02_export_nirv_observations.py", "02_build_corestack.py")},
            "run_utc": started, "finished_utc": now(),
            "inputs": [{"path": str(a.units), "bytes": Path(a.units).stat().st_size, "sha256": sha256(a.units)},
                       {"earth_engine_asset": asset, "checked_against_the_layer_by": str(record.relative_to(ROOT))},
                       {"earth_engine_image_collection": std_collection, "blocks": len(blocks), "recipe_sha256": NIRV.YEARLY.RECIPE_SHA256, "exported_by_run": yearly_prov["run_utc"],
                        "recorded_in": yearly_prov.get("_read_from"),
                        "made_from": {"earth_engine_image_collection": obs_collection, "recipe_sha256": NIRV.OBS.RECIPE_SHA256, "exported_by_run": obs_prov["run_utc"], "recorded_in": obs_prov.get("_read_from")}},
                       {"path": "20_degradation/nirv.provenance.json", "sha256": sha256(OUT / "nirv.provenance.json"), "run_utc": nirv_prov["run_utc"]},
                       {"path": "20_degradation/nirv_scenes.csv", "sha256": sha256(OUT / "nirv_scenes.csv"), "scenes": int(len(scenes))},
                       {"earth_engine_dataset": HANSEN, "bands": ["treecover2000", "lossyear"]}, {"earth_engine_image_collection": CORE.CHANGE, "zones_in_order": CORE.ZONES}]
                      + [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sources.values()],
            "definitions": {"grid": GRID, "reference_common": "treecover2000 > 10, CoRE Stack class in -2..4 at the cell's centre, NIRv has all six seasons 2016-2018 and 2022-2024",
                            "hansen_common": f"lossyear in {HANSEN_WINDOW[0]}..{HANSEN_WINDOW[1]}", "nirv_common": "lower / higher as in 02_build_nirv.py (before-and-after contrast), on its date-standardised yearly values",
                            "corestack_states": {k: list(v) for k, v in C_STATES.items()}, "reference_full_span": "treecover2000 > 10, CoRE Stack class in -2..4, NIRv has a trend (at least 10 seasons)",
                            "hansen_full_span": "lossyear in 1..25", "nirv_full_span": "declining / increasing as in 02_build_nirv.py (13-season exact Mann-Kendall)",
                            "headline_cells": HEADLINE_CELLS, "unit_flag": f"rate above the {FLAG_PERCENTILE}th percentile of units with at least {UNIT_MIN_REFERENCE_HA:g} ha of reference land",
                            "unit_flag_cuts": cuts, "odds_ratio_interval": f"percentiles 2.5 and 97.5 of {BOOTSTRAP} resamplings of units, seed {BOOTSTRAP_SEED}", "loss_year_groups": {k: list(v) for k, v in LOSS_GROUPS.items()}},
            "earth_engine": {"project": project, "zonal_tasks": eu.task_record(status), "zonal_eecu_seconds": round(eu.eecu(status), 1),
                             "group_tables_taken_from_an_earlier_attempt_of_the_same_computation": GROUPS - len(status), "group_table_folder": folder},
            "checks_passed": {"units_returned_each_once": int(len(m)), "cells_add_up_to_the_reference_land": True, "area_summed_over_pixels_vs_polygons": area, "margins_against_the_sources_own_tables": checks},
            "tables": {name: {"rows": int(len(t)), "columns": int(len(t.columns)), "blank_cells": blank(t)} for name, t in out_tables.items()},
            "versions": {"python": sys.version.split()[0], "earthengine-api": ee.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        }, fh, indent=2)
    try:                                                   # only now that the tables and their record are written; a failed delete loses nothing
        cleanup()
    except Exception as e:
        print(f"NOTE  the intermediate tables could not all be deleted ({type(e).__name__}: {e}). Left in Earth Engine, to delete by hand: {folder.split('/')[-1]}")

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    print(f"\nagreement_summary.csv: n = {len(summary)} rows; the headline (common window, treecover2000 > 10):")
    print(summary[(summary.window == "common window") & (summary.land == "gt10")].drop(columns=["window", "land"]).T.to_string(header=False))
    print(f"\nagreement_pairs.csv: n = {len(pairs)} rows; common window, treecover2000 > 10, all units:")
    print(pairs[(pairs.window == "common window") & (pairs.land == "gt10") & (pairs.units == "all units")].drop(columns=["window", "land", "units", "n_units"]).to_string(index=False))
    print(f"\nagreement_units.csv: n = {len(units_table)} rows")
    print(units_table.T.to_string(header=False))
    print(f"\nagreement_positive_control.csv: n = {len(control_table)} rows; all units:")
    print(control_table[control_table.units == "all units"].drop(columns=["units", "n_units"]).to_string(index=False))
    print(f"\nEarth Engine: {eu.eecu(status):,.0f} EECU-seconds; done. run_utc {started}; outputs in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
