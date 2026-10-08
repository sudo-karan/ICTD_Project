#!/usr/bin/env python3
"""
The condition of each unit's forest, as a planner would ask it: is there forest standing now, is it mostly closed or
mostly open, and has forest been lost lately? One of six cells per unit and per window of years, with the hectares the
cell is a summary of. No Earth Engine: everything is read from tables that stage 0 and stage 1 already wrote.

    python scripts/05_build_decision.py

WHY PER UNIT AND NOT PER PIXEL. Hansen's loss is recorded for a whole pixel (the provider defines it as the clearing of
at least half of the pixel's tree cover), so a pixel is either standing or lost and "dense and losing" cannot be shown
at the level of a pixel. A unit is classed from its hectares.

INPUTS (read, never written)
  20_degradation/hansen_loss_by_canopy_band_by_unit.csv   one row per unit; hectares, 4 decimals:
        area_ha_gt30, area_ha_gt10le30, area_ha_le10      land by canopy in the year 2000: treecover2000 > 30,
                                                          10 < treecover2000 <= 30, treecover2000 <= 10
        loss_ha_<band>_<year>                             Hansen loss on that land in that year, band in gt30, gt10le30,
                                                          le10; year 2001 ... 2025
        loss_ha_gt30, loss_ha_gt10le30, loss_ha_le10      the table's own totals over 2001-2025 (used only as a check)
  10_units/units_attributes.csv                           unit_id, unit_name, unit_level, outside_village, pc11_district_code.
                                                          The kind of unit is read from outside_village (1 or 0); the run
                                                          stops unless unit_level says the same in every unit. unit_name is
                                                          written without space before or after it, blank where there is none
  10_units/outside_village_district.csv                   the assigned district of each outside_village unit and how it was checked
  00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv   district name for each pc11_district_code
  20_degradation/agreement_by_unit.csv                    what the existing two-measure comparison says of the unit (2017-2023)
  checked against, and not otherwise used: 20_degradation/hansen_loss_by_canopy_band.csv, hansen_by_unit.csv,
        agreement.provenance.json, agreement_by_zone.csv, agreement_floor_repeatability.csv; 10_units/outside_village_district.provenance.json
  read for the table of what the thresholds rest on (condition_threshold_evidence.csv), and for nothing in the per-unit table:
        20_degradation/forest_floor_repeatability.csv (the area of one pixel in the middle of the state, a constant of stage 1);
        00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt (the one-hectare wording);
        40_allocation/state_fy_r620_vs_dump.csv (plantation's share of expenditure in two years: the reason given for the
        default window, written into that table and held to a test)
  read if it is there: 00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv, the registered schedule of
        permissible works. Only then does a cell name work types; otherwise its field reads "pending — schedule not yet registered"

ARITHMETIC IS DONE IN WHOLE TEN-THOUSANDTHS OF A HECTARE. Every input figure has four decimals (the run stops if one has
more, or is blank), so t(x) = round(x * 10000) is exact, and sums and differences of t() are exact integers: every hectare
in the table is exact. THE TWO THRESHOLDS OF THE CELLS, and the comparison of standing dense with standing open, are made
on a figure AS THE MAP PRINTS IT: with two decimals, by the ordinary formatting of the four-decimal figure held as a double -
q(v) is the whole number of hundredths in format(v / 10000, ".2f"), Python's formatting, which is correctly rounded from the
binary value (a figure whose third and fourth decimals are exactly 50 therefore goes up or down as its double lies, not
always up). That is the rule by which every other hectare on the map is printed; taking it here means that one figure
never prints two ways in a unit's panel, and that a unit's cell never contradicts the hundredths printed beside it. This
table itself carries four decimals, and read at four decimals a few units look otherwise: where standing dense and
standing open print the same hundredth the tie goes to dense, though the fourth decimal of open may be the larger; and a
loss that prints as 1.00 counts as some though its fourth decimal may be under it. The provenance record counts both, and
counts the cells that the other common rule (half up on the decimal figure) would print differently.

THE HECTARES (the lossless record; the cell is a summary of it). Names: dense = treecover2000 > 30, open =
10 < treecover2000 <= 30, low = treecover2000 <= 10.
  dense_2000_ha, open_2000_ha, low_2000_ha   = area_ha_gt30, area_ha_gt10le30, area_ha_le10
  standing_dense_ha  = area_ha_gt30     - the sum of loss_ha_gt30_<year>     over ALL years 2001 ... 2025
  standing_open_ha   = area_ha_gt10le30 - the sum of loss_ha_gt10le30_<year> over ALL years 2001 ... 2025
                       each set to 0 where the subtraction gives less than 0. It does in a handful of units, by one
                       ten-thousandth of a hectare (a square metre): the source rounds each year's loss and the band's area
                       to four decimals separately. The provenance record counts them.
  standing_forest_ha = standing_dense_ha + standing_open_ha
  "Standing" is always NOW, through 2025, whatever window is asked for. It is a LOWER BOUND on tree cover present: Hansen
  does not net off gain, so land that lost its cover and grew it back, and land that gained cover since 2000, is not in it.
  For each window W = (first year, last year), inclusive:
  loss_dense_ha_W  = the sum of loss_ha_gt30_<year>     over the years of W
  loss_open_ha_W   = the sum of loss_ha_gt10le30_<year> over the years of W
  forest_loss_ha_W = loss_dense_ha_W + loss_open_ha_W        (loss by the band the forest was in, in 2000)
  loss_low_ha_W    = the sum of loss_ha_le10_<year> over the years of W   REPORTED ONLY. It decides nothing: most of it is on
                     pixels with no canopy at all in 2000, and its rise over time is largely the producers' change of method
                     (docs/RESULTS.md section 3.1).
THE WINDOWS, each with its own columns (suffix): 2018_2025 (the default: the years after plantation fell out of the scheme's
spending), 2001_2025 (the full record), 2017_2023 (CoRE Stack's window, so that corroboration is like for like),
2021_2025 (the most recent five years).

THE TWO THRESHOLDS (decisions, proposed here; alternatives in the sensitivity table)
  STANDING_MIN_HA = 10    a unit whose standing_forest_ha, printed, is under this has "little or none"
  LOSS_MIN_HA     = 1     a unit whose forest_loss_ha_W, printed, is at least this has "some" loss in W; under it, "none"
  alternatives: standing 5 and 25; loss 0.5 and 2.
THE ROW (standing forest now; the same in every window)
  little_or_none   q(standing_forest) <  STANDING_MIN_HA
  mostly_dense     otherwise, and q(standing_dense) >= q(standing_open)       (a tie goes to dense)
  mostly_open      otherwise
THE COLUMN (forest loss in the window)     some if q(forest_loss_W) >= LOSS_MIN_HA, else none
THE SIX CELLS  cell_<W> =
  dense_none   "Protect - intact closed forest"                       mostly_dense,   none
  dense_loss   "Closed forest under pressure - find the cause first"  mostly_dense,   some
  open_none    "Open forest - assisted natural regeneration candidate" mostly_open,    none
  open_loss    "Open forest still losing - restore"                   mostly_open,    some
  little_loss  "Little forest left, recent loss - verify on the ground" little_or_none, some
  little_none  "Not a forest site"                                    little_or_none, none
NEAR THE DENSE/OPEN BOUNDARY. dense_open_ratio = the smaller of standing_dense_ha and standing_open_ha over the larger,
on the exact four-decimal figures, rounded half up to four decimals; 0 where one of the two is zero; blank if both are.
near_dense_open_boundary = 1 for a unit in the row mostly_dense or mostly_open for which 10 x the smaller >= 8 x the
larger, in ten-thousandths (a ratio of at least 0.8), else 0: the unit most likely to be mis-summarised.
ORDER WITHIN A CELL, WITHIN A DISTRICT. order_in_district_cell_<W> = 1, 2, 3 ... among the units of one district in
one cell, LGD panchayat and outside-village units together: a cell with loss (dense_loss, open_loss, little_loss) by
forest_loss_ha_W, largest first; dense_none by standing_dense_ha, open_none by standing_open_ha, little_none by
standing_forest_ha, largest first - each on the exact four-decimal figure, not the printed hundredth; ties by unit_id as
text, ascending. tier_provisional_2018_2025 = 1 ... 5, a whole number: the place of cell_2018_2025 in the provisional
order of tiers below (open_loss, dense_loss, open_none, dense_none, little_loss); blank for little_none. There is NO
order across districts and NO score: among the LGD panchayat units of the agreement test's headline the two forest measures
agree within districts, and their agreement across the state is not established (docs/RESULTS.md sections 5.1 and 5.2).
THE DISTRICT of a unit: for unit_level lgd_panchayat, pc11_district_code of units_attributes.csv; for outside_village,
pc11_district_code of outside_village_district.csv (assigned, not surveyed). district = its name in the FRA table.

CORROBORATION (copied from agreement_by_unit.csv; NO new statistic). Its window is always 2017-2023:
corroboration_window holds "2017-2023" in every row. agreement_reference_ha and agreement_corestack_valued_ha are that
table's reference_ha and corestack_valued_ha, copied, four decimals.
  corroboration          both | hansen_only | corestack_only | neither | not_compared
  corroboration_basis    headline                 agreement_class is one of the four classes
                         east_coast_every_unit_kept  agreement_class is zone_model_excluded: the class is then
                                                  agreement_class_all_assessed, and the placebo failed under that zone
                                                  model, so corroboration is unreliable there
                         for a unit that was not compared (agreement_class insufficient_forest), on the exact four-decimal
                         figures and against the comparison's floor of 100 ha:
                         below_floor              reference_ha is under 100 ha, and corestack_valued_ha is above 0
                         below_floor_no_corestack_coverage   reference_ha is under 100 ha, and corestack_valued_ha is 0.
                                                  What that zero means: CoRE Stack assigns no class to the unit's land with
                                                  canopy above 10 % in 2000 - in most of these units because there is no such
                                                  land. It does NOT mean the product does not reach the unit.
                         corestack_covers_under_floor        reference_ha is at least 100 ha; corestack_valued_ha is under 100 ha
THE OUTSIDE-VILLAGE UNITS are classed and ordered like any unit. district_check says what the assigned district rests
on, every status that applies, in this order, joined by "; ": moved_off_the_name (assigned_by is "two checks against
the label"), polygon_has_no_name (assigned_by ends "has no district name"), ambiguous (ambiguous is 1),
flagged_one_check_contradicts ((area_majority_agrees_with_assigned is 0) or (label_absent_from_collar is 1 and
assigned_by is "label")), no_check_possible (ambiguous_basis is "not measurable"); none of these:
name_on_the_polygon_not_contradicted - which means that none of the five flags of 10_units is raised, not that every
check agrees (a unit whose neighbours' largest district is another one is flagged upstream only when its own district is
absent from the collar). Blank for lgd_panchayat units. governance_prompt holds, for every outside_village
unit and no other, the sentence: No revenue village — this land is in no village plan. Whose plan covers it?

OUTPUT: 55_decision/ and nowhere else
  condition_by_unit.csv            one row per unit, 11,468, in the order of unit_id as text (code-point order). Every
                                   hectare is written with exactly four decimals, the ratio likewise; the tier, the order
                                   columns and the two 0/1 flags as whole numbers; a blank as an empty field; UTF-8, no
                                   byte-order mark. Its 51 columns, in order:
                                     unit_id, unit_name, unit_level, outside_village, pc11_district_code (the district's code
                                     as resolved under THE DISTRICT), district, dense_2000_ha, open_2000_ha, low_2000_ha,
                                     standing_dense_ha, standing_open_ha, standing_forest_ha, standing_row (THE ROW),
                                     dense_open_ratio, near_dense_open_boundary;
                                     then for each window W in the order 2018_2025, 2001_2025, 2017_2023, 2021_2025:
                                     loss_dense_ha_W, loss_open_ha_W, forest_loss_ha_W, loss_low_ha_W, loss_column_W (THE
                                     COLUMN: some or none), cell_W, order_in_district_cell_W;
                                     then tier_provisional_2018_2025, corroboration, corroboration_basis, corroboration_window,
                                     agreement_reference_ha, agreement_corestack_valued_ha, district_check, governance_prompt
  condition_cells.csv              units, standing hectares and loss by window x kind of unit x cell
  condition_cells_by_district.csv  units by window x district x cell
  condition_sensitivity.csv        units per cell at each pair of thresholds (3 x 3), and how many units change cell
  condition_boundary.csv           how many units sit near the dense/open boundary, at four ratios
  condition_threshold_evidence.csv what the two proposed thresholds rest on, each row with a key: the pixel, the one-hectare
                                   definition, recurrence, repeatability on the threshold's own land, and how the loss
                                   column follows the size of a unit's forest
  tiers.csv                        the PROVISIONAL order of the cells, with one line of reason each
  work_types.csv                   the work-type field of each cell: rows of the registered list of permissible works, cited
                                   by serial number with their names read from the list - or "pending — schedule not yet registered"
  work_rows_naming_forest.csv      every row of the registered list whose work type or name holds the word forest, and the
                                   cells that cite it - so that the rows cited by no cell can be seen (absent if no list)
  decision.provenance.json         inputs with sha256, the UTC run time, definitions, thresholds, checks, n and blanks

STOP CONDITIONS (the tables are written to a temporary folder, read back as text, and put in place only if all hold)
  - every unit of the layer once in each per-unit table, and exactly the outside_village units in outside_village_district.csv;
    unit_level and outside_village say the same of every unit, in all three tables that carry them;
  - every hectare read has at most four decimals and none is blank; every unit has a district, and there are 30;
  - the existing comparison's floor is 100 ha and its window 2017-2023, its classes are the six this script has words
    for, and "insufficient_forest" means under 100 ha on one of the two grids;
  - per unit and band: the yearly losses add up to the table's own total (to 0.002 ha);
  - ON THE FILE AS WRITTEN, read back as text: every one of its 24 hectare columns equals the figure computed or copied;
    and, per unit, standing +
    loss 2001-2025 = the year-2000 band hectares for the dense band and for the open band, exactly, except in the units
    where standing was set to 0 - there the gap is what the source's rounding put below zero, and may not pass 0.002 ha
    (the record counts the units and gives the gap);
  - in total, by kind of unit: the year-2000 band hectares, the loss 2001-2025 and the loss 2018-2025 per band equal
    hansen_loss_by_canopy_band.csv to the two decimals of a square kilometre that table prints (0.006 km2);
  - per unit: dense_2000_ha and the dense loss 2001-2025 equal forest_ha and hansen_loss_ha of hansen_by_unit.csv (to 0.002 ha),
    the dense loss of 2021-2025 equals the sum of its hansen_loss_ha_2021 ... 2025, and forest_loss_ha_2017_2023 equals
    hansen_loss_ha_common_2017_2023 of agreement_by_unit.csv (to 0.002 ha);
  - the six agreement classes counted here equal agreement.provenance.json's own; the corroboration column on the
    headline basis equals that record's four classes, and on the East Coast basis it equals what agreement_by_zone.csv
    counts for those units (flagged by both, by Hansen, on degradation); the district-check counts equal
    outside_village_district.provenance.json's own;
  - the Forest Survey extract still holds the one-hectare wording the loss threshold cites; the repeatability worked out
    here on land with canopy above 10 % equals agreement_floor_repeatability.csv in the two classes that table has in
    common; plantation's share of expenditure in the scheme's state report more than halves between FY2016-17 and FY2018-19;
  - every unit is in exactly one cell in every window, and its row is the same in all four.
"""
import datetime, hashlib, json, shutil, sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "55_decision"
WINDOWS = {"2018_2025": (2018, 2025), "2001_2025": (2001, 2025), "2017_2023": (2017, 2023), "2021_2025": (2021, 2025)}
WINDOW_IS = {"2018_2025": "the default: the years after plantation fell out of spending in the scheme's state report", "2001_2025": "the full record",
             "2017_2023": "CoRE Stack's window, so that corroboration is like for like", "2021_2025": "the most recent five years"}
DEFAULT_WINDOW = "2018_2025"
STANDING_MIN_HA, LOSS_MIN_HA = 10.0, 1.0                      # PROPOSALS, flagged for the project owner. Never the agreement test's 100 ha
STANDING_ALTERNATIVES, LOSS_ALTERNATIVES = (5.0, 25.0), (0.5, 2.0)
NEAR_RATIO = 0.8
RATIOS = (0.5, 2 / 3, 0.8, 0.9)
AGREEMENT_FLOOR_HA = 100.0                                   # the existing comparison's own floor: read here only to say why a unit was not compared
BANDS = {"dense": "gt30", "open": "gt10le30", "low": "le10"}
_L, _S = f"{LOSS_MIN_HA:g} ha", f"{STANDING_MIN_HA:g} ha"
CELLS = {  # id: (row, column, name, what the name rests on). The names are the project owner's; each sentence after it says the cell's own test and no more
    "dense_none": ("mostly_dense", "none", "Protect - intact closed forest", f"Mostly closed forest, with under {_L} of forest loss recorded in the window: protection and conservation work, not planting."),
    "dense_loss": ("mostly_dense", "some", "Closed forest under pressure - find the cause first", f"Mostly closed forest, with {_L} or more of forest loss recorded in the window: the cause comes before any work."),
    "open_none": ("mostly_open", "none", "Open forest - assisted natural regeneration candidate", f"Mostly open forest, with under {_L} of forest loss recorded in the window: a candidate for assisted natural regeneration."),
    "open_loss": ("mostly_open", "some", "Open forest still losing - restore", f"Mostly open forest, with {_L} or more of forest loss recorded in the window: restoration."),
    "little_loss": ("little_or_none", "some", "Little forest left, recent loss - verify on the ground", f"Under {_S} of standing forest, and {_L} or more of forest loss recorded in the window: to be verified on the ground."),
    "little_none": ("little_or_none", "none", "Not a forest site", f"Under {_S} of standing forest, whatever the size of the unit, and under {_L} of forest loss recorded in the window."),
}
# PROVISIONAL, to be set with the Foundation for Ecological Security. A user control in the layer, not a constant of the analysis.
TIERS = [("open_loss", "Open forest is where the standing canopy is thinnest, and loss is recorded in the window: restoration has the most to hold on to and the most to lose by waiting."),
         ("dense_loss", "Closed forest with loss recorded in the window needs its cause found before any work is planned; a forester could reasonably put this tier first."),
         ("open_none", f"Open forest with under {_L} of loss recorded in the window is a candidate for assisted natural regeneration."),
         ("dense_none", f"Closed forest with under {_L} of loss recorded in the window calls for protection and conservation work, not planting."),
         ("little_loss", "Little forest stands and loss is recorded in the window: the record may be of plantation felled, of regrowth cleared, or of error - it has to be seen on the ground.")]
WHY_UNRANKED = f"On the map, outside the ranked list: under {_S} of standing forest and under {_L} of forest loss recorded in the window to act on."
UNRANKED = "little_none"
PENDING = "pending — schedule not yet registered"
GOVERNANCE = "No revenue village — this land is in no village plan. Whose plan covers it?"
SCHEDULE = "00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv"
SCHEDULE_CITE = "Ministry of Rural Development notification S.O. 5448(E), 5 October 2026: the list of permissible works under the VB-G RAM G Act (375 works)"
WORK_ROWS = {"fire": [372, 373, 374], "trenches": [121, 123], "forestry": [105, 108, 110], "bamboo": [91]}       # serial numbers of the registered list
WORK_NOTE = ("No row of the list names forest land, and the list does not sort its works by the condition of a forest. Which rows bear on a cell is this project's proposal, to be set with the Foundation "
             "for Ecological Security; the rows that name forest and are cited by no cell are listed under Work types in the text on how to read this layer. Serial numbers were read from the page images of the Gazette.")
SIZE_CLASSES = ((10, 25), (25, 50), (50, 100), (100, 250), (250, 500), (500, 1000), (1000, 5000), (5000, None))   # ha of standing forest: how the loss column follows size
REPEAT_CLASSES = {5.0: (5, 10), 10.0: (10, 25), 25.0: (25, 50)}                                                  # ha of land with canopy above 10 % in 2000: the class that starts at each standing minimum
fails = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stop_if_failed(stage):
    if fails:
        print(f"\nFAILED at {stage} - {len(fails)} check(s). Nothing written.", file=sys.stderr)
        for m in fails:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)


def t(x):
    """Hectares with four decimals as whole ten-thousandths. Stops on a blank, or on a figure with more than four decimals."""
    v = np.asarray(x, float) * 10000
    if np.isnan(v).any() or (np.abs(v - np.rint(v)) > 1e-4).any():
        fails.append("a hectare figure is blank or has more than four decimals: the arithmetic in whole ten-thousandths would not be exact")
        stop_if_failed("reading the hectares")
    return np.rint(v).astype(np.int64)


def q(v):
    """Whole ten-thousandths as the hundredths the map prints: the two-decimal formatting of the four-decimal figure as a double."""
    a = np.asarray(v, np.int64)
    return np.array([int(f"{x / 10000:.2f}".replace(".", "")) for x in a.ravel()], dtype=np.int64).reshape(a.shape)


def ha(v):
    """Whole ten-thousandths as the text of hectares with exactly four decimals: written from the integers, not from a float."""
    return np.array([("-" if x < 0 else "") + f"{abs(int(x)) // 10000}.{abs(int(x)) % 10000:04d}" for x in np.asarray(v, np.int64)], dtype=object)


def classify(sd, so, loss, standing_min, loss_min):
    """Row, column and cell index (in the order of CELLS) of each unit, from ten-thousandths."""
    little = q(sd + so) < int(round(standing_min * 100))
    dense = ~little & (q(sd) >= q(so))
    some = q(loss) >= int(round(loss_min * 100))
    row = np.where(little, "little_or_none", np.where(dense, "mostly_dense", "mostly_open"))
    col = np.where(some, "some", "none")
    index = {(r, c): k for k, (r, c, _, _) in CELLS.items()}
    return row, col, np.array([index[(r, c)] for r, c in zip(row, col)], dtype=object)


def main():
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    inputs = []

    def use(path, role=""):
        p = ROOT / path
        if not p.is_file():
            fails.append(f"{path} is not there")
            stop_if_failed("reading the inputs")
        if not any(i["path"] == path for i in inputs):
            inputs.append({"path": path, "bytes": p.stat().st_size, "sha256": sha256(p), **({"role": role} if role else {})})
        return p

    U = pd.read_csv(use("10_units/units_attributes.csv"), dtype={"unit_id": str, "pc11_district_code": str, "unit_name": str}, keep_default_na=False, na_values={"pc11_district_code": [""], "area_ha": [""]})
    U = U.sort_values("unit_id").reset_index(drop=True)
    ids, n = U["unit_id"], len(U)
    B = pd.read_csv(use("20_degradation/hansen_loss_by_canopy_band_by_unit.csv"), dtype={"unit_id": str})
    A = pd.read_csv(use("20_degradation/agreement_by_unit.csv"), dtype={"unit_id": str})
    HB = pd.read_csv(use("20_degradation/hansen_by_unit.csv", "checked against"), dtype={"unit_id": str})
    OD = pd.read_csv(use("10_units/outside_village_district.csv"), dtype=str, keep_default_na=False)
    names = pd.read_csv(use("00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv"), dtype=str).set_index("pc11_district_code")["district"]
    for name, tab in (("hansen_loss_by_canopy_band_by_unit", B), ("agreement_by_unit", A), ("hansen_by_unit", HB)):
        if len(tab) != n or not tab["unit_id"].is_unique or set(tab["unit_id"]) != set(ids):
            fails.append(f"{name}.csv does not hold each of the layer's {n:,} units once")
    stop_if_failed("reading the inputs")
    B, A, HB = (x.set_index("unit_id").loc[ids].reset_index() for x in (B, A, HB))
    outside = (U["outside_village"] == 1).to_numpy()
    for name, tab in (("units_attributes", U), ("hansen_loss_by_canopy_band_by_unit", B), ("agreement_by_unit", A)):
        if not ((tab["unit_level"] == "outside_village").to_numpy() == outside).all() or not ((tab["outside_village"] == 1).to_numpy() == outside).all() or not set(tab["unit_level"]) <= {"lgd_panchayat", "outside_village"}:
            fails.append(f"{name}.csv: unit_level and outside_village do not say the same of every unit as units_attributes.csv does")
    OD = OD.set_index("unit_id")
    if set(OD.index) != set(ids[outside]):
        fails.append("outside_village_district.csv does not hold exactly the outside_village units")
    stop_if_failed("reading the inputs")
    years = list(range(2001, 2026))

    # ---- the hectares, in whole ten-thousandths ------------------------------------------------------------------------------------------
    area = {b: t(B[f"area_ha_{s}"]) for b, s in BANDS.items()}
    yearly = {b: np.column_stack([t(B[f"loss_ha_{s}_{y}"]) for y in years]) for b, s in BANDS.items()}
    all_loss = {b: yearly[b].sum(axis=1) for b in BANDS}
    for b, s in BANDS.items():
        gap = np.abs(all_loss[b] - t(B[f"loss_ha_{s}"])).max()
        if gap > 20:
            fails.append(f"{b}: the yearly losses differ from the table's own total by up to {gap / 10000:.4f} ha")
    raw_standing = {b: area[b] - all_loss[b] for b in ("dense", "open")}
    below_zero = {b: {"units": int((raw_standing[b] < 0).sum()), "smallest_ha": round(float(raw_standing[b].min()) / 1e4, 4) if (raw_standing[b] < 0).any() else 0.0} for b in raw_standing}
    for b in raw_standing:
        if raw_standing[b].min() < -20:                                # more than the rounding of 25 four-decimal figures can give
            fails.append(f"standing {b} forest is below zero by up to {-raw_standing[b].min() / 10000:.4f} ha: more than the source's rounding explains")
    standing = {b: np.maximum(raw_standing[b], 0) for b in raw_standing}
    stop_if_failed("the hectares")
    sd, so = standing["dense"], standing["open"]
    win = {w: {b: yearly[b][:, [y - 2001 for y in range(a, z + 1)]].sum(axis=1) for b in BANDS} for w, (a, z) in WINDOWS.items()}
    clipped = {b: raw_standing[b] < 0 for b in raw_standing}          # the units where standing was set to 0; the identity itself is tested on the file as written, below

    # ---- against the sources' own tables ---------------------------------------------------------------------------------------------------
    S = S0 = pd.read_csv(use("20_degradation/hansen_loss_by_canopy_band.csv", "its own totals, checked against"))
    level = {"all units": np.ones(n, bool), "lgd_panchayat": ~outside, "outside_village": outside}
    reconciled = []
    for label, m in level.items():
        for b, s in BANDS.items():
            row = S[(S["units"] == label) & (S["canopy_band"] == s)]
            if len(row) != 1:
                fails.append(f"hansen_loss_by_canopy_band.csv: {len(row)} rows for {label}, {s}")
                continue
            row = row.iloc[0]
            for what, mine, theirs in (("land in 2000", area[b][m].sum(), row["land_km2"]), ("loss 2001-2025", all_loss[b][m].sum(), row["loss_km2_2001_2025"]),
                                       ("loss 2018-2025", win["2018_2025"][b][m].sum(), row["loss_km2_2018_2025"])):
                km2 = mine / 1e6
                reconciled.append({"units": label, "band": b, "what": what, "this_table_km2": round(km2, 4), "hansen_loss_by_canopy_band_km2": float(theirs)})
                if abs(km2 - float(theirs)) > 0.006:                       # that table prints two decimals of a km2
                    fails.append(f"{label}, {b}, {what}: {km2:,.3f} km2 here, {float(theirs):,.2f} in hansen_loss_by_canopy_band.csv")
    per_unit = {"dense_2000_ha against forest_ha of hansen_by_unit.csv": np.abs(area["dense"] - t(HB["forest_ha"])).max(),
                "dense loss 2001-2025 against hansen_loss_ha of hansen_by_unit.csv": np.abs(all_loss["dense"] - t(HB["hansen_loss_ha"])).max(),
                "dense loss 2021-2025 against the yearly columns of hansen_by_unit.csv": np.abs(win["2021_2025"]["dense"] - sum(t(HB[f"hansen_loss_ha_{y}"]) for y in range(2021, 2026))).max(),
                "forest loss 2017-2023 against hansen_loss_ha_common_2017_2023 of agreement_by_unit.csv": np.abs(win["2017_2023"]["dense"] + win["2017_2023"]["open"] - t(A["hansen_loss_ha_common_2017_2023"])).max()}
    for what, gap in per_unit.items():
        if gap > 20:
            fails.append(f"{what}: differs by up to {gap / 10000:.4f} ha in a unit")
    stop_if_failed("reconciling with the sources' own tables")
    print(f"OK  hectares: n = {n:,} units; standing dense {sd.sum() / 1e6:,.1f} km2, standing open {so.sum() / 1e6:,.1f} km2; totals by band equal hansen_loss_by_canopy_band.csv "
          f"({len(reconciled)} figures); per unit, four comparisons with other tables, largest gap {max(per_unit.values()) / 10000:.4f} ha")

    # ---- the district --------------------------------------------------------------------------------------------------------------------
    code = U["pc11_district_code"].astype("string").to_numpy(dtype=object)
    code[outside] = OD["pc11_district_code"].reindex(ids[outside]).to_numpy()
    district = pd.Series(code).map(names).to_numpy(dtype=object)
    if pd.isna(district).any() or len(set(district)) != 30:
        fails.append(f"{int(pd.isna(district).sum())} units have no district, or the districts are not 30")
    stop_if_failed("the district")

    # ---- the table -------------------------------------------------------------------------------------------------------------------------
    T = pd.DataFrame({"unit_id": ids, "unit_name": U["unit_name"].fillna("").astype(str).str.strip(), "unit_level": U["unit_level"], "outside_village": U["outside_village"].astype(int),
                      "pc11_district_code": code, "district": district, "dense_2000_ha": ha(area["dense"]), "open_2000_ha": ha(area["open"]), "low_2000_ha": ha(area["low"]),
                      "standing_dense_ha": ha(sd), "standing_open_ha": ha(so), "standing_forest_ha": ha(sd + so)})
    row, _, _ = classify(sd, so, win[DEFAULT_WINDOW]["dense"] + win[DEFAULT_WINDOW]["open"], STANDING_MIN_HA, LOSS_MIN_HA)
    T["standing_row"] = row
    big, small = np.maximum(sd, so), np.minimum(sd, so)
    ratio_tt = (2 * small * 10000 + big) // np.where(big > 0, 2 * big, 1)            # the ratio in ten-thousandths, rounded half up, in whole numbers
    T["dense_open_ratio"] = np.where(big > 0, ha(ratio_tt), "")
    T["near_dense_open_boundary"] = ((row != "little_or_none") & (10 * small >= int(NEAR_RATIO * 10) * big)).astype(int)
    cells, half_up_cells = {}, {}
    for w in WINDOWS:
        ld, lo, ll = win[w]["dense"], win[w]["open"], win[w]["low"]
        hu = lambda x: (x + 50) // 100                                   # the other common rule, half up on the decimal figure: only to say how many cells it would change
        hl = hu(sd + so) < int(STANDING_MIN_HA * 100)
        half_up_cells[w] = np.array([{("little_or_none", "none"): "little_none", ("little_or_none", "some"): "little_loss", ("mostly_dense", "none"): "dense_none", ("mostly_dense", "some"): "dense_loss",
                                      ("mostly_open", "none"): "open_none", ("mostly_open", "some"): "open_loss"}[(a_, b_)]
                                     for a_, b_ in zip(np.where(hl, "little_or_none", np.where(hu(sd) >= hu(so), "mostly_dense", "mostly_open")), np.where(hu(ld + lo) >= int(LOSS_MIN_HA * 100), "some", "none"))], dtype=object)
        r, c, cell = classify(sd, so, ld + lo, STANDING_MIN_HA, LOSS_MIN_HA)
        if not np.array_equal(r, row):
            fails.append("the row changed with the window")
        cells[w] = cell
        T[f"loss_dense_ha_{w}"], T[f"loss_open_ha_{w}"], T[f"forest_loss_ha_{w}"], T[f"loss_low_ha_{w}"] = ha(ld), ha(lo), ha(ld + lo), ha(ll)
        T[f"loss_column_{w}"], T[f"cell_{w}"] = c, cell
        key = np.where(np.isin(cell, ["dense_loss", "open_loss", "little_loss"]), ld + lo, np.where(cell == "dense_none", sd, np.where(cell == "open_none", so, sd + so)))
        order = pd.DataFrame({"d": district, "c": cell, "k": -key, "u": ids.to_numpy()}).sort_values(["d", "c", "k", "u"], kind="mergesort")
        order["o"] = order.groupby(["d", "c"]).cumcount() + 1
        T[f"order_in_district_cell_{w}"] = order["o"].reindex(T.index).to_numpy()
    place = {c: str(i + 1) for i, (c, _) in enumerate(TIERS)}
    T["tier_provisional_" + DEFAULT_WINDOW] = [place.get(c, "") for c in cells[DEFAULT_WINDOW]]

    # ---- corroboration: copied from the existing comparison --------------------------------------------------------------------------------
    AP = json.load(open(use("20_degradation/agreement.provenance.json", "its own counts, checked against")))
    if float(AP["definitions"]["floor"]["minimum_reference_ha"]) != AGREEMENT_FLOOR_HA or AP["definitions"]["headline_window"] != "common_2017_2023":
        fails.append("the existing comparison's floor or window is not the one this script describes (100 ha, 2017-2023)")
    cls, every = A["agreement_class"].to_numpy(dtype=object), A["agreement_class_all_assessed"].to_numpy(dtype=object)
    four = ["both", "hansen_only", "corestack_only", "neither"]
    ref, val, floor_tt = t(A["reference_ha"]), t(A["corestack_valued_ha"]), int(AGREEMENT_FLOOR_HA * 10000)
    if (ref < 0).any() or (val < 0).any():
        fails.append("agreement_by_unit.csv has a negative hectare figure")
    corro = np.where(np.isin(cls, four), cls, np.where(cls == "zone_model_excluded", every, "not_compared"))
    basis = np.where(np.isin(cls, four), "headline", np.where(cls == "zone_model_excluded", "east_coast_every_unit_kept",
                     np.where(ref < floor_tt, np.where(val > 0, "below_floor", "below_floor_no_corestack_coverage"), "corestack_covers_under_floor")))
    if not set(cls) <= set(four) | {"zone_model_excluded", "insufficient_forest"} or not set(corro) <= set(four) | {"not_compared"}:
        fails.append("agreement_by_unit.csv has a class this script has no words for")
    if ((cls == "insufficient_forest") != ~((ref >= floor_tt) & (val >= floor_tt))).any():
        fails.append("'insufficient_forest' in agreement_by_unit.csv is not 'under 100 ha on one of the two grids'")
    T["corroboration"], T["corroboration_basis"], T["corroboration_window"] = corro, basis, "2017-2023"
    T["agreement_reference_ha"], T["agreement_corestack_valued_ha"] = ha(ref), ha(val)
    by_level = AP["counts"]["by_level"]["all units"]
    mine = {k: int(((cls == k)).sum()) for k in four + ["zone_model_excluded", "insufficient_forest"]}
    if any(mine[k] != int(by_level.get(k, 0)) for k in mine):
        fails.append(f"the agreement classes counted here ({mine}) are not agreement.provenance.json's own ({by_level})")
    Z = pd.read_csv(use("20_degradation/agreement_by_zone.csv", "its own counts for the East Coast units, checked against"))
    z = Z[Z["zone_model_of_the_units_valued_land"] == "ECPHR only"]
    by_basis = {"headline": {k: int(((corro == k) & (basis == "headline")).sum()) for k in four}, "east_coast_every_unit_kept": {k: int(((corro == k) & (basis == "east_coast_every_unit_kept")).sum()) for k in four},
                "not_compared": int((corro == "not_compared").sum())}
    if any(by_basis["headline"][k] != int(by_level.get(k, 0)) for k in four) or by_basis["not_compared"] != int(by_level.get("insufficient_forest", -1)):
        fails.append(f"the corroboration column on the headline basis ({by_basis['headline']}), or the units not compared, is not agreement.provenance.json's own count")
    e = by_basis["east_coast_every_unit_kept"]
    if len(z) != 1 or float(z["minimum_reference_ha"].iloc[0]) != AGREEMENT_FLOOR_HA or sum(e.values()) != int(z["n_assessed"].iloc[0]) or e["both"] != int(z["both_degradation"].iloc[0]) \
            or e["both"] + e["hansen_only"] != int(z["flagged_by_hansen"].iloc[0]) or e["both"] + e["corestack_only"] != int(z["flagged_on_degradation"].iloc[0]):
        fails.append(f"the corroboration of the East Coast units ({e}) is not what agreement_by_zone.csv counts for them")

    # ---- the outside-village units: what the assigned district rests on -----------------------------------------------------------------------
    o = OD.reindex(ids)
    status = {"moved_off_the_name": (o["assigned_by"] == "two checks against the label"), "polygon_has_no_name": o["assigned_by"].fillna("").str.endswith("has no district name"),
              "ambiguous": (o["ambiguous"] == "1"), "flagged_one_check_contradicts": ((o["area_majority_agrees_with_assigned"] == "0") | ((o["label_absent_from_collar"] == "1") & (o["assigned_by"] == "label"))),
              "no_check_possible": (o["ambiguous_basis"] == "not measurable")}
    status = {k: v.fillna(False).to_numpy() & outside for k, v in status.items()}
    check = np.array(["; ".join(k for k in status if status[k][i]) for i in range(n)], dtype=object)
    T["district_check"] = np.where(outside, np.where(check == "", "name_on_the_polygon_not_contradicted", check), "")
    T["governance_prompt"] = np.where(outside, GOVERNANCE, "")
    DP = json.load(open(use("10_units/outside_village_district.provenance.json", "its own counts, checked against")))["counts"]
    theirs = {"moved_off_the_name": DP["assigned_by"]["two checks against the label"]["units"], "ambiguous": DP["ambiguous_the_one_flag"]["units"],
              "flagged_one_check_contradicts": DP["flagged_not_moved_one_check_contradicts_the_assigned_district"]["units"], "no_check_possible": DP["no_check_possible_neither_covered_nor_with_a_coded_neighbour"]["units"],
              "polygon_has_no_name": DP["assigned_by"]["area majority: the polygon has no district name"]["units"] + DP["assigned_by"]["neighbours: the polygon has no district name"]["units"]}
    for k, v in theirs.items():
        if int(status[k].sum()) != int(v):
            fails.append(f"district check '{k}': {int(status[k].sum())} units here, {v} in outside_village_district.provenance.json")
    stop_if_failed("corroboration and the district check")
    for w in WINDOWS:
        if T[f"cell_{w}"].isna().any() or not set(T[f"cell_{w}"]) <= set(CELLS):
            fails.append(f"window {w}: a unit is in no cell")
    stop_if_failed("the cells")

    # ---- summaries -----------------------------------------------------------------------------------------------------------------------------
    rows = []
    for w in WINDOWS:
        for label, m in level.items():
            for cell, (r, c, name, _) in CELLS.items():
                k = m & (cells[w] == cell)
                rows.append({"window": w, "units": label, "cell": cell, "cell_name": name, "standing_row": r, "loss_column": c, "n_units": int(k.sum()), "n_units_of_this_kind": int(m.sum()),
                             "standing_dense_ha": round(int(sd[k].sum()) / 1e4, 2), "standing_open_ha": round(int(so[k].sum()) / 1e4, 2), "forest_loss_ha_in_window": round(int((win[w]["dense"][k] + win[w]["open"][k]).sum()) / 1e4, 2),
                             "loss_low_ha_in_window_reported_only": round(int(win[w]["low"][k].sum()) / 1e4, 2), "near_dense_open_boundary": int((k & (T["near_dense_open_boundary"] == 1).to_numpy()).sum())})
    cells_table = pd.DataFrame(rows)
    by_district = pd.DataFrame([{"window": w, "district": d, "cell": cell, "n_units": int(((district == d) & (cells[w] == cell)).sum()), "n_outside_village": int(((district == d) & (cells[w] == cell) & outside).sum())}
                                for w in WINDOWS for d in sorted(set(district)) for cell in CELLS])
    sens = []
    for smin in sorted((STANDING_MIN_HA,) + STANDING_ALTERNATIVES):
        for lmin in sorted((LOSS_MIN_HA,) + LOSS_ALTERNATIVES):
            for w in WINDOWS:
                _, _, cell = classify(sd, so, win[w]["dense"] + win[w]["open"], smin, lmin)
                for name in CELLS:
                    sens.append({"standing_min_ha": smin, "loss_min_ha": lmin, "is_the_default": int(smin == STANDING_MIN_HA and lmin == LOSS_MIN_HA), "window": w, "cell": name, "n_units": int((cell == name).sum()),
                                 "n_units_in_this_cell_at_the_default": int((cells[w] == name).sum()), "units_whose_cell_differs_from_the_default_all_cells": int((cell != cells[w]).sum())})
    sens = pd.DataFrame(sens)
    forest_site = row != "little_or_none"
    boundary = pd.DataFrame([{"ratio_at_least": round(r_, 4), "is_the_flag_in_the_table": int(abs(r_ - NEAR_RATIO) < 1e-9), "units": label, "n_units_mostly_dense_or_mostly_open": int((m & forest_site).sum()),
                              "n_near_the_boundary": int((m & forest_site & (small >= r_ * big - 1e-9)).sum()), "of_them_mostly_dense": int((m & (row == "mostly_dense") & (small >= r_ * big - 1e-9)).sum()),
                              "of_them_mostly_open": int((m & (row == "mostly_open") & (small >= r_ * big - 1e-9)).sum())} for r_ in RATIOS for label, m in level.items()])

    # ---- what the two thresholds rest on -----------------------------------------------------------------------------------------------------
    # Every row has a key that the layer and the document look it up by; "what" says it in words.
    R = pd.read_csv(use("20_degradation/forest_floor_repeatability.csv", "the area of one pixel in the middle of the state")).set_index("forest_ha_from")
    pixel_ha = float(R.loc[1.0, "one_pixel_as_share_of_forest_at_the_bottom"]) * 1.0
    pixel_tt = int(round(pixel_ha * 1e4))
    isfr = use("00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt", "the Forest Survey's definition of forest cover").read_text(encoding="utf-8")
    phrase = "more than or equal to one hectare in area"
    if phrase not in " ".join(isfr.split()):
        fails.append("the Forest Survey extract no longer holds the one-hectare wording the loss threshold cites")
    one_pixel = (f"under {pixel_ha:g} ha, the area of one pixel in the middle of the state. A pixel is a little smaller than that to the north and a little larger to the south, so this count takes in slivers cut by a boundary "
                 f"and, in the north, whole single pixels, and leaves out whole single pixels in the south")
    ev = [{"key": "pixel_ha", "about": "pixel", "what": "area of one Hansen pixel in the middle of the state, ha (the grid is in degrees: a pixel is a little smaller to the north, a little larger to the south)", "value": round(pixel_ha, 4), "n": "",
           "source": "forest_floor_repeatability.csv: one_pixel_as_share_of_forest_at_the_bottom, at 1 ha - a constant of scripts/02_propose_forest_floor.py"},
          {"key": "fsi_min_patch_ha", "about": "loss threshold", "what": "the Forest Survey of India counts as forest cover only land of one hectare or more: the smallest patch its maps hold", "value": 1.0, "n": "",
           "source": f"00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt: '{phrase}'"}]
    for lmin in sorted((LOSS_MIN_HA,) + LOSS_ALTERNATIVES):
        ev.append({"key": f"pixels_in_loss_{lmin:g}", "about": "loss threshold", "what": f"pixels of that size in a loss of {lmin:g} ha", "value": round(lmin / pixel_ha, 1), "n": "", "source": "computed here from the pixel area"})
    for w in WINDOWS:
        fl = win[w]["dense"] + win[w]["open"]
        ev.append({"key": f"under_mid_pixel_{w}", "about": "loss threshold", "what": f"window {w}: units with forest loss above zero and {one_pixel}", "value": int(((fl > 0) & (fl < pixel_tt)).sum()), "n": n, "source": "this table"})
        ev.append({"key": f"mid_pixel_to_loss_min_{w}", "about": "loss threshold", "what": f"window {w}: units with forest loss of {pixel_ha:g} ha or more and under {LOSS_MIN_HA:g} ha", "value": int(((fl >= pixel_tt) & (q(fl) < LOSS_MIN_HA * 100)).sum()), "n": n, "source": "this table"})
    first = sum(yearly[b][:, [y - 2001 for y in range(2018, 2022)]].sum(axis=1) for b in ("dense", "open"))
    second = sum(yearly[b][:, [y - 2001 for y in range(2022, 2026)]].sum(axis=1) for b in ("dense", "open"))
    for smin in sorted((STANDING_MIN_HA,) + STANDING_ALTERNATIVES):
        site = q(sd + so) >= smin * 100
        for lmin in sorted((LOSS_MIN_HA,) + LOSS_ALTERNATIVES):
            had = site & (q(first) >= lmin * 100)
            ev.append({"key": f"recur_{smin:g}_{lmin:g}", "about": "loss threshold", "what": f"recurrence: of units with at least {smin:g} ha standing and at least {lmin:g} ha of forest loss in 2018-2021, the share with at least {lmin:g} ha again in 2022-2025, %",
                       "value": round(100 * float((q(second)[had] >= lmin * 100).mean()), 1), "n": int(had.sum()), "source": "this table's yearly figures"})
        none = site & (first < pixel_tt)
        ev.append({"key": f"fresh_{smin:g}", "about": "loss threshold", "what": f"of units with at least {smin:g} ha standing and under {pixel_ha:g} ha of forest loss in 2018-2021 (none, or less than the pixel in the middle of the state), the share with at least {LOSS_MIN_HA:g} ha in 2022-2025, %",
                   "value": round(100 * float((q(second)[none] >= LOSS_MIN_HA * 100).mean()), 1), "n": int(none.sum()), "source": "this table's yearly figures"})
    # an absolute loss minimum follows the size of a unit's forest: the larger the forest, the likelier some hectare of it was lost
    fl0, sf = win[DEFAULT_WINDOW]["dense"] + win[DEFAULT_WINDOW]["open"], sd + so
    some0 = q(fl0) >= LOSS_MIN_HA * 100
    sf_printed = q(sf)                                                   # hundredths, as printed: the classes are cut on the figure the map shows, like every threshold
    for lo_, hi_ in SIZE_CLASSES:
        m_ = (row != "little_or_none") & (sf_printed >= lo_ * 100) & ((sf_printed < hi_ * 100) if hi_ else True)
        label_ = f"{lo_:,} ha" + (f" to under {hi_:,} ha" if hi_ else " or more") + " of standing forest"
        ev.append({"key": f"some_loss_share_{lo_}", "about": "loss threshold: size", "what": f"window {DEFAULT_WINDOW}: of forest-site units with {label_}, the share with some loss ({LOSS_MIN_HA:g} ha or more), %",
                   "value": round(100 * float(some0[m_].mean()), 1), "n": int(m_.sum()), "source": "this table"})
        had_ = m_ & (q(first) >= LOSS_MIN_HA * 100)
        none_ = m_ & (first < pixel_tt)
        ev.append({"key": f"recur_size_{lo_}", "about": "loss threshold: size", "what": f"recurrence by size: of forest-site units with {label_} and at least {LOSS_MIN_HA:g} ha of forest loss in 2018-2021, the share with at least {LOSS_MIN_HA:g} ha again in 2022-2025, %",
                   "value": round(100 * float((q(second)[had_] >= LOSS_MIN_HA * 100).mean()), 1) if had_.any() else "", "n": int(had_.sum()), "source": "this table's yearly figures"})
        ev.append({"key": f"fresh_size_{lo_}", "about": "loss threshold: size", "what": f"by size: of forest-site units with {label_} and under {pixel_ha:g} ha of forest loss in 2018-2021, the share with at least {LOSS_MIN_HA:g} ha in 2022-2025, %",
                   "value": round(100 * float((q(second)[none_] >= LOSS_MIN_HA * 100).mean()), 1) if none_.any() else "", "n": int(none_.sum()), "source": "this table's yearly figures"})
    dl = cells[DEFAULT_WINDOW] == "dense_loss"
    ev += [{"key": "dense_loss_under_1pct", "about": "loss threshold: size", "what": f"window {DEFAULT_WINDOW}: units in the cell dense_loss whose forest loss in the window is under 1 % of their standing forest", "value": int((dl & (100 * fl0 < sf)).sum()), "n": int(dl.sum()), "source": "this table"},
           {"key": "dense_loss_under_01pct", "about": "loss threshold: size", "what": f"window {DEFAULT_WINDOW}: units in the cell dense_loss whose forest loss in the window is under 0.1 % of their standing forest", "value": int((dl & (1000 * fl0 < sf)).sum()), "n": int(dl.sum()), "source": "this table"},
           {"key": "none_cell_over_2pct", "about": "loss threshold: size", "what": f"window {DEFAULT_WINDOW}: forest-site units in a cell with no loss whose forest loss in the window is over 2 % of their standing forest",
            "value": int(((row != "little_or_none") & ~some0 & (100 * fl0 > 2 * sf)).sum()), "n": int(((row != "little_or_none") & ~some0).sum()), "source": "this table"}]
    total_standing = float((sd + so).sum())
    # repeatability on the land the standing minimum is about (canopy above 10 % in 2000, dense and open), by the method of agreement_floor_repeatability.csv, and held against it
    AFR = pd.read_csv(use("20_degradation/agreement_floor_repeatability.csv", "its two classes in common, checked against"))
    land_f = sum(B[f"area_ha_{s}"].to_numpy(float) for s in ("gt30", "gt10le30"))
    odd_f, even_f = (sum(B[f"loss_ha_{s}_{y}"].to_numpy(float) for s in ("gt30", "gt10le30") for y in years if y % 2 == r_) for r_ in (1, 0))
    repeat = {}
    for smin, (lo_, hi_) in REPEAT_CLASSES.items():
        sel = (land_f >= lo_) & (land_f < hi_)
        repeat[smin] = {"n": int(sel.sum()), "no_loss": int(((odd_f + even_f)[sel] == 0).sum()), "rho": round(float(spearmanr(odd_f[sel] / land_f[sel], even_f[sel] / land_f[sel])[0]), 3), "class": f"{lo_:g} to under {hi_:g} ha"}
        theirs = AFR[(AFR["reference_ha_from"] == lo_) & (AFR["hansen_loss_years"] == "2001-2025")]
        if len(theirs) == 1:
            th = theirs.iloc[0]
            if (repeat[smin]["n"], repeat[smin]["no_loss"], repeat[smin]["rho"]) != (int(th["n_units"]), int(th["units_with_no_loss_in_those_years"]), float(th["odd_years_vs_even_years_spearman"])):
                fails.append(f"repeatability of the class {lo_}-{hi_} ha worked out here ({repeat[smin]}) is not agreement_floor_repeatability.csv's own")
        elif lo_ >= 10:
            fails.append(f"agreement_floor_repeatability.csv has no single row for the class from {lo_} ha, 2001-2025")
    for smin in sorted((STANDING_MIN_HA,) + STANDING_ALTERNATIVES):
        site = q(sd + so) >= smin * 100
        rp = repeat[smin]
        src = "worked out here from hansen_loss_by_canopy_band_by_unit.csv by the method of agreement_floor_repeatability.csv" + ("; equal to that table's row" if REPEAT_CLASSES[smin][0] >= 10 else "; that table has no class below 10 ha")
        ev += [{"key": f"pixels_in_standing_{smin:g}", "about": "standing threshold", "what": f"pixels of that size in {smin:g} ha", "value": round(smin / pixel_ha, 1), "n": "", "source": "computed here from the pixel area"},
               {"key": f"units_standing_{smin:g}", "about": "standing threshold", "what": f"units with at least {smin:g} ha of standing forest", "value": int(site.sum()), "n": n, "source": "this table"},
               {"key": f"share_standing_{smin:g}", "about": "standing threshold", "what": f"share of all standing forest that is in units with at least {smin:g} ha of it, %", "value": round(100 * float((sd + so)[site].sum()) / total_standing, 2), "n": int(site.sum()), "source": "this table"},
               {"key": f"repeat_rho_{smin:g}", "about": "standing threshold", "what": f"units with {rp['class']} of land with canopy above 10 % in 2000 (dense and open): rank correlation of a unit's loss rate between odd and even years, 2001-2025",
                "value": rp["rho"], "n": rp["n"], "source": src},
               {"key": f"repeat_no_loss_{smin:g}", "about": "standing threshold", "what": f"the same class ({rp['class']}): share of its units with no recorded loss on that land in 2001-2025, %", "value": round(100 * rp["no_loss"] / rp["n"], 1), "n": rp["n"], "source": src}]
    ev += [{"key": "loss_min_over_standing_min_pct", "about": "standing threshold", "what": "the loss threshold as a share of the standing threshold, %", "value": round(100 * LOSS_MIN_HA / STANDING_MIN_HA, 1), "n": "", "source": "the two proposals"}]
    # the reason given for the default window, held against the scheme's state report
    R620 = pd.read_csv(use("40_allocation/state_fy_r620_vs_dump.csv", "the reason given for the default window, checked against"), dtype={"fy": str}).set_index("fy")
    pl16, pl18 = float(R620.loc["2016-17", "r620_plantation_share_pct"]), float(R620.loc["2018-19", "r620_plantation_share_pct"])
    if not pl18 < pl16 / 2:
        fails.append(f"the default window is described as the years after plantation fell out of the state report's spending, and its share is {pl16} % in FY2016-17 and {pl18} % in FY2018-19")
    ev += [{"key": "plantation_share_fy2016_17", "about": "default window", "what": "plantation as a share of expenditure in the scheme's state report (R6.20), FY2016-17, %", "value": round(pl16, 1), "n": "", "source": "40_allocation/state_fy_r620_vs_dump.csv"},
           {"key": "plantation_share_fy2018_19", "about": "default window", "what": "the same, FY2018-19, %", "value": round(pl18, 1), "n": "", "source": "40_allocation/state_fy_r620_vs_dump.csv"}]
    if len({e_["key"] for e_ in ev}) != len(ev):
        fails.append("two rows of the evidence table carry the same key")
    evidence = pd.DataFrame(ev)
    tiers = pd.DataFrame([{"tier": i + 1, "cell": c, "tier_label": f"Tier {i + 1}: {CELLS[c][2]}", "cell_name": CELLS[c][2], "standing_row": CELLS[c][0], "loss_column": CELLS[c][1], "what_the_name_rests_on": CELLS[c][3],
                           "why_this_place_in_the_order": why, "status": "PROVISIONAL - to be set with the Foundation for Ecological Security; a user control in the layer"} for i, (c, why) in enumerate(TIERS)]
                         + [{"tier": "", "cell": UNRANKED, "tier_label": f"Not ranked: {CELLS[UNRANKED][2]}", "cell_name": CELLS[UNRANKED][2], "standing_row": CELLS[UNRANKED][0], "loss_column": CELLS[UNRANKED][1],
                             "what_the_name_rests_on": CELLS[UNRANKED][3], "why_this_place_in_the_order": WHY_UNRANKED, "status": "outside the ranked list"}])
    # the work-type field: only from the registered list of permissible works. A row is cited by its serial number and its
    # name is READ from the list, never typed here; which rows bear on a cell is this project's proposal, and says so.
    schedule = ROOT / SCHEDULE
    if schedule.is_file():
        S = pd.read_csv(use(SCHEDULE, "the registered list of permissible works"), dtype={"serial": int}, keep_default_na=False).set_index("serial")
        SR = json.load(open(use(SCHEDULE.replace(".csv", ".provenance.json"), "the registered list's own record")))
        text = (S["work_type"] + " | " + S["work_name"]).str.lower()
        groups = {"fire": WORK_ROWS["fire"], "trenches": WORK_ROWS["trenches"], "forestry": WORK_ROWS["forestry"], "bamboo": WORK_ROWS["bamboo"]}
        want = {"fire": lambda r: r.work_type == "Forest fire management works", "trenches": lambda r: r.work_type == "Soil moisture conservation" and "contour trench" in r.work_name and r.work_name.endswith("for community"),
                "forestry": lambda r: "forestry trees" in r.work_name and r.work_name.endswith("for community"), "bamboo": lambda r: "bamboo plantation" in r.work_name and r.work_name.endswith("for community")}
        for g_, serials in groups.items():
            if any(n_ not in S.index or not want[g_](S.loc[n_]) for n_ in serials):
                fails.append(f"the registered list's rows {serials} are not the {g_} works this script cites them as")
        absent = {w_: int(text.str.contains(w_, regex=False).sum()) for w_ in ("regeneration", "forest land", "grazing", "biodiversity")}
        if len(S) != 375 or int(SR["checks_passed"]["rows"]) != 375 or any(absent.values()):
            fails.append(f"the registered list does not have 375 rows, or a word this script says is in no row is in one: {absent}")
        stop_if_failed("the work types")
        cite = lambda n_: f"Sl. {n_} {S.loc[n_, 'work_name']}"
        for g_, serials in groups.items():
            if len({S.loc[n_, "work_type"] for n_ in serials}) != 1:
                fails.append(f"the rows {serials} do not share one work type in the registered list, so they cannot stand under one heading")
        named = {g_: f"{S.loc[serials[0], 'work_type']} - " + "; ".join(cite(n_) for n_ in serials) for g_, serials in groups.items()}       # each heading is the list's own work type
        named["forestry"] = named["forestry"] + ". " + named["bamboo"]
        fields = {"dense_none": ("Protection, not planting. In the list: " + named["fire"] + ".", groups["fire"]),
                  "dense_loss": ("Find the cause before choosing work; no row of the list is a way of finding it. If the cause is fire: " + named["fire"] + ".", groups["fire"]),
                  "open_none": ("Assisted natural regeneration is not in the list: the word regeneration is in none of its 375 rows. Rows that could support it: " + named["trenches"] + ". " + named["fire"] + ".", groups["trenches"] + groups["fire"]),
                  "open_loss": (named["forestry"] + ". " + named["trenches"] + ". " + named["fire"] + ".", groups["forestry"] + groups["bamboo"] + groups["trenches"] + groups["fire"]),
                  "little_loss": ("None until the recorded loss has been seen on the ground.", []), "little_none": ("None: not a forest site.", [])}
        work = pd.DataFrame([{"cell": c, "work_type_field": fields[c][0], "entries": "; ".join(str(n_) for n_ in fields[c][1]), "schedule": SCHEDULE_CITE, "note": WORK_NOTE} for c in CELLS])
        forest_named = S[(S["work_type"] + " " + S["work_name"]).str.lower().str.contains("forest", regex=False)]
        naming = pd.DataFrame([{"serial": int(n_), "work_type": r_.work_type, "work_name": r_.work_name, "gazette_page": r_.gazette_page, "cited_by_cells": "; ".join(c for c in CELLS if n_ in fields[c][1])} for n_, r_ in forest_named.iterrows()])
    else:
        work = pd.DataFrame([{"cell": c, "work_type_field": PENDING, "entries": "", "schedule": "", "note": ""} for c in CELLS])
        naming = None
    stop_if_failed("the summaries")

    # ---- write ---------------------------------------------------------------------------------------------------------------------------------
    OUT.mkdir(exist_ok=True)
    TMP = OUT / ".being_written"                                  # everything is written here first, read back, and only then put in place
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir()
    tables = {"condition_by_unit.csv": T, "condition_cells.csv": cells_table, "condition_cells_by_district.csv": by_district, "condition_sensitivity.csv": sens, "condition_boundary.csv": boundary,
              "condition_threshold_evidence.csv": evidence, "tiers.csv": tiers, "work_types.csv": work}
    if naming is not None:
        tables["work_rows_naming_forest.csv"] = naming
    for name, tab in tables.items():
        tab.to_csv(TMP / name, index=False)
    # read back AS TEXT, and reconcile on what was written: this is the check the project owner asked for, made on the file itself
    back = pd.read_csv(TMP / "condition_by_unit.csv", dtype=str, keep_default_na=False)
    wrong = []
    if len(back) != n or list(back["unit_id"]) != list(ids) or any(list(back[f"cell_{w}"]) != list(cells[w]) for w in WINDOWS):
        wrong.append("the units or the cells do not read back as they were computed")
    else:
        tt = lambda col: np.array([int(v.replace(".", "")) if len(v.split(".")[-1]) == 4 else -10**12 for v in back[col]], dtype=np.int64)     # the text of four decimals, as whole ten-thousandths
        computed = {"dense_2000_ha": area["dense"], "open_2000_ha": area["open"], "low_2000_ha": area["low"], "standing_dense_ha": sd, "standing_open_ha": so, "standing_forest_ha": sd + so}
        computed.update({"agreement_reference_ha": ref, "agreement_corestack_valued_ha": val})                  # copied from the agreement table: read back like the rest
        for w in WINDOWS:
            computed.update({f"loss_dense_ha_{w}": win[w]["dense"], f"loss_open_ha_{w}": win[w]["open"], f"forest_loss_ha_{w}": win[w]["dense"] + win[w]["open"], f"loss_low_ha_{w}": win[w]["low"]})
        if len(computed) != sum(1 for c_ in back.columns if c_.endswith("_ha") or "_ha_" in c_):
            wrong.append("a hectare column of the table is not among those read back")
        for col, v in computed.items():
            if not np.array_equal(tt(col), v):
                wrong.append(f"{col} does not read back as it was computed")
        identity = {}
        for b in ("dense", "open"):
            gap = tt(f"standing_{b}_ha") + tt(f"loss_{b}_ha_2001_2025") - tt(f"{b}_2000_ha")        # on the file: standing + all loss - the year-2000 band
            if (gap[~clipped[b]] != 0).any() or (gap[clipped[b]] <= 0).any() or gap.max() > 20:
                wrong.append(f"standing + loss 2001-2025 is not the year-2000 {b} band in {int((gap[~clipped[b]] != 0).sum())} units where it should be exact (largest gap {gap.max() / 1e4:.4f} ha)")
            identity[b] = {"units_exact": int((gap == 0).sum()), "units_not_exact": int((gap != 0).sum()), "largest_gap_ha": round(float(np.abs(gap).max()) / 1e4, 4)}
            for label, m in level.items():                                # and in total, against the band table, from the file
                ref_ = S0[(S0["units"] == label) & (S0["canopy_band"] == BANDS[b])].iloc[0]
                if abs((tt(f"standing_{b}_ha")[m].sum() + tt(f"loss_{b}_ha_2001_2025")[m].sum()) / 1e6 - float(ref_["land_km2"])) > 0.006 or abs(tt(f"loss_{b}_ha_2001_2025")[m].sum() / 1e6 - float(ref_["loss_km2_2001_2025"])) > 0.006:
                    wrong.append(f"{label}, {b}: standing plus loss, or loss, summed over the file is not hansen_loss_by_canopy_band.csv's own")
    for name, tab in tables.items():                                      # every small table reads back with its rows and columns
        if name != "condition_by_unit.csv":
            b_ = pd.read_csv(TMP / name, dtype=str, keep_default_na=False)
            if len(b_) != len(tab) or list(b_.columns) != list(tab.columns):
                wrong.append(f"{name} does not read back with the rows and columns it was written with")
    if wrong:
        shutil.rmtree(TMP)
        print("FAILED on the tables as written. Nothing put in place.", file=sys.stderr)
        for m_ in wrong:
            print(f"  {m_}", file=sys.stderr)
        sys.exit(1)
    print(f"OK  on the file as written: every hectare column reads back as computed; standing + loss 2001-2025 = the year-2000 band exactly in {identity['dense']['units_exact']:,} units (dense) and {identity['open']['units_exact']:,} (open), "
          f"and by {max(identity['dense']['largest_gap_ha'], identity['open']['largest_gap_ha']):.4f} ha at most in the {identity['dense']['units_not_exact'] + identity['open']['units_not_exact']} where standing was set to 0")
    counts = {w: {c: int((cells[w] == c).sum()) for c in CELLS} for w in WINDOWS}
    with open(TMP / "decision.provenance.json", "w", encoding="utf-8") as fh:
        json.dump({"script": "scripts/05_build_decision.py", "script_sha256": sha256(__file__), "run_utc": started, "inputs": inputs,
                   "definitions": {"arithmetic": "whole ten-thousandths of a hectare; the thresholds are compared with the figure as the map prints it - format(x, '.2f') of the four-decimal figure as a double, the rule of every other hectare on the map",
                                   "standing": "year-2000 band hectares less ALL Hansen loss on them through 2025; always now, whatever the window. A LOWER BOUND: Hansen does not net off gain",
                                   "forest_loss_in_a_window": "loss on the dense band plus loss on the open band in the window's years, by the band the forest was in, in 2000",
                                   "loss_on_low_canopy": "reported only; decides nothing (docs/RESULTS.md section 3.1)", "bands": {"dense": "treecover2000 > 30", "open": "10 < treecover2000 <= 30", "low": "treecover2000 <= 10"},
                                   "windows": {w: {"years": list(v), "is": WINDOW_IS[w]} for w, v in WINDOWS.items()}, "default_window": DEFAULT_WINDOW,
                                   "cells": {c: {"standing_row": r, "loss_column": col, "name": name, "what_the_name_rests_on": rests} for c, (r, col, name, rests) in CELLS.items()},
                                   "row": "little_or_none if printed standing forest < the standing threshold; else mostly_dense if printed standing dense >= printed standing open; else mostly_open",
                                   "column": "some if printed forest loss in the window >= the loss threshold; else none",
                                   "order": "within a district, within a cell: cells with loss by forest loss in the window, largest first; the others by standing hectares of the row's band; ties by unit_id. No order across districts; no score",
                                   "near_dense_open_boundary": f"row mostly_dense or mostly_open, and the smaller of standing dense and standing open is at least {NEAR_RATIO:g} of the larger",
                                   "corroboration": "copied from agreement_by_unit.csv; its window is 2017-2023 whatever window is selected; no new statistic",
                                   "district": "lgd_panchayat units: their Census-2011 district; outside_village units: the district assigned in outside_village_district.csv"},
                   "thresholds": {"status": "PROPOSED, for the project owner to rule on. The agreement test's 100 ha is not used here.",
                                  "standing_min_ha": STANDING_MIN_HA, "loss_min_ha": LOSS_MIN_HA, "alternatives": {"standing_min_ha": list(STANDING_ALTERNATIVES), "loss_min_ha": list(LOSS_ALTERNATIVES)},
                                  "pixel_ha": round(pixel_ha, 4), "pixel_ha_is": "one pixel in the middle of the state; a pixel is a little smaller to the north", "rationale_table": "55_decision/condition_threshold_evidence.csv", "sensitivity_table": "55_decision/condition_sensitivity.csv"},
                   "tiers": {"status": "PROVISIONAL - to be set with the Foundation for Ecological Security; a user control in the layer, not a constant", "order": [c for c, _ in TIERS], "unranked": UNRANKED,
                             "tier_column_of_the_table": "tier_provisional_2018_2025 is the place of the unit's cell in THIS order, for the default window only, as a number; the labels are in tiers.csv",
                             "note": "a forester could reasonably put dense_loss above open_loss"},
                   "work_types": {"registered": bool(schedule.is_file()), "field_when_not_registered": PENDING, "list": SCHEDULE_CITE if schedule.is_file() else "", "rows_cited": WORK_ROWS if schedule.is_file() else {},
                                  "words_in_no_row_of_the_list": ["regeneration", "forest land", "grazing", "biodiversity"] if schedule.is_file() else [], "note": WORK_NOTE if schedule.is_file() else ""},
                   "checks_passed": {"units_each_once": n,
                                     "standing_plus_all_loss_against_the_band_hectares_per_unit": identity,
                                     "that_identity_was_tested_on": "the file as written, read back as text; exact except in the units where standing was set to 0",
                                     "standing_set_to_zero_where_the_sources_rounding_put_it_below": below_zero,
                                     "yearly_losses_against_the_tables_own_totals_largest_gap_ha": round(float(max(np.abs(all_loss[b] - t(B[f'loss_ha_{s}'])).max() for b, s in BANDS.items())) / 1e4, 4),
                                     "totals_against_hansen_loss_by_canopy_band": reconciled, "per_unit_against_other_tables_largest_gap_ha": {k: round(float(v) / 1e4, 4) for k, v in per_unit.items()},
                                     "not_checked_against_a_second_table": "the open band's loss in 2021-2025 and in 2017-2023 taken alone: only hansen_loss_by_canopy_band_by_unit.csv carries it by year",
                                     "agreement_classes_equal_the_agreement_records_own": mine, "corroboration_by_its_basis_equals_the_agreement_record_and_the_zone_table": by_basis,
                                     "the_printing_rule_against_half_up_on_the_decimal_figure": {
                                         "hectare_cells_that_would_print_differently": int(sum((q(x) != (x + 50) // 100).sum() for x in [area["dense"], area["open"], area["low"], sd, so, sd + so]
                                                                                           + [y for w in WINDOWS for y in (win[w]["dense"], win[w]["open"], win[w]["dense"] + win[w]["open"], win[w]["low"])])),
                                         "unit_windows_whose_cell_would_differ": int(sum((classify(sd, so, win[w]["dense"] + win[w]["open"], STANDING_MIN_HA, LOSS_MIN_HA)[2] != half_up_cells[w]).sum() for w in WINDOWS))},
                                     "printed_parts_add_to_a_threshold_the_printed_total_is_under": {
                                         "units_standing": int(((q(sd) + q(so) >= int(STANDING_MIN_HA * 100)) & (q(sd + so) < int(STANDING_MIN_HA * 100))).sum()),
                                         "unit_windows_loss": int(sum(((q(win[w]["dense"]) + q(win[w]["open"]) >= int(LOSS_MIN_HA * 100)) & (q(win[w]["dense"] + win[w]["open"]) < int(LOSS_MIN_HA * 100))).sum() for w in WINDOWS))},
                                     "read_at_four_decimals_and_not_as_printed": {"units_mostly_dense_whose_standing_open_is_larger_in_the_fourth_decimal": int(((row == "mostly_dense") & (so > sd)).sum()),
                                                                                  "unit_windows_with_some_loss_and_under_the_threshold_in_the_fourth_decimal": int(sum(((cells[w] != "x") & (q(win[w]["dense"] + win[w]["open"]) >= int(LOSS_MIN_HA * 100))
                                                                                                                                                                   & (win[w]["dense"] + win[w]["open"] < int(LOSS_MIN_HA * 10000))).sum() for w in WINDOWS))}, "district_check_counts_equal_the_district_records_own": {k: int(v.sum()) for k, v in status.items()}},
                   "counts": {"units": n, "by_level": {"lgd_panchayat": int((~outside).sum()), "outside_village": int(outside.sum())}, "standing_row": {r: int((row == r).sum()) for r in ("mostly_dense", "mostly_open", "little_or_none")},
                              "cells": counts, "near_dense_open_boundary": int(T["near_dense_open_boundary"].sum()),
                              "corroboration_two_bases_pooled_do_not_quote": {k: int((corro == k).sum()) for k in four + ["not_compared"]},
                              "corroboration_note": "the pooled counts add flags cut in two populations (the headline, and every unit kept for the East Coast units): quote the counts by basis under checks_passed",
                              "corroboration_basis": {k: int((basis == k).sum()) for k in sorted(set(basis))}},
                   "tables": {name: {"rows": int(len(tab)), "columns": int(len(tab.columns)), "blank_cells": {c: int(tab[c].isna().sum() + (tab[c].astype(str) == "").sum()) for c in tab.columns if (tab[c].isna() | (tab[c].astype(str) == "")).any()}}
                              for name, tab in tables.items()},
                   "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__}}, fh, indent=2)
    json.load(open(TMP / "decision.provenance.json", encoding="utf-8"))            # the record reads back as JSON, or nothing is put in place
    for f in sorted(TMP.iterdir()):
        f.replace(OUT / f.name)
    TMP.rmdir()
    print(f"55_decision/: condition_by_unit.csv n = {n:,} units, {len(T.columns)} columns; thresholds (proposed) standing {STANDING_MIN_HA:g} ha, loss {LOSS_MIN_HA:g} ha")
    for w in WINDOWS:
        print(f"  {w}: " + "; ".join(f"{c} {counts[w][c]:,}" for c in CELLS))
    print(f"  rows: " + "; ".join(f"{r} {int((row == r).sum()):,}" for r in ("mostly_dense", "mostly_open", "little_or_none")) + f"; near the dense/open boundary {int(T['near_dense_open_boundary'].sum()):,}")
    print(f"done. run_utc {started}")


if __name__ == "__main__":
    main()
