# The decision layer: where forest work is warranted

*Written 2026-10-10T23:09:20Z by `scripts/write_decision_layer.py`. No figure in this document was typed: each was read from a
file, and §20 says which. It describes the decision table built 2026-10-09T03:37:07Z and the layer built 2026-10-09T04:08:22Z.*

## 1. What this is

The supervisor asked the project to "determine which areas have seen forest degradation, are also marginalised, and
have they seen good enough resource allocation in the past". Until now that was answered as measurement: two measures
of forest, a measure of need, a record of allocation (`docs/RESULTS.md`). The project owner now reads the request as
one for a **decision layer**: something a planner opens to see where forest work is warranted, comparable in purpose,
in his words, to the recharge-potential layer of CLART in Commons Connect.

This document describes that layer. Four things about it come first.

- **It is added; nothing is replaced.** The measurement stays exactly as it was. No file of `10_units/` to `50_gap/`
  and no existing column was changed. The new tables are in a new folder, `55_decision/` (10 tables, a run
  record and the record of a gate). The view is a new entry in the layer of `60_layer/`,
  beside the existing ones, which keep their behaviour and their defaults (§16 says how that was checked).
- **It is a way of reading the measurements, not a new measurement.** Each of the 11,468 units
  (7,976 LGD panchayat units and 3,492 outside-village units) is placed in one of six cells by two questions put
  to Hansen's record: how much forest stands now, and is it mostly closed or mostly open; and was forest lost in a
  window of years. No unit is without a cell in any window. The cells are put in an order of tiers. That is all.
- **There is no score.** No index, no weights, no number out of a hundred. Need and past allocation are shown beside
  a unit's tier and are never folded into it (§10).
- **The owner ruled on it on 9 October 2026, and three things are still open.** He accepted the two thresholds as
  proposed (10 ha of standing forest; 1 ha of forest loss), renamed five of the six cells so that each name
  states its test, had the loss of the window shown also as a share of the forest, struck the words "lower bound",
  took one column out of the exported list, and had a copy of the layer made without the map overlay. Still open, for
  the Foundation for Ecological Security: the order of tiers (§8), which rows of the official list of works bear on
  which cell (§13), and whether Scheduled Tribe share appears in a list they pass on (§10). §17 gives every ruling and
  every open point.

Neither threshold is the 100 ha floor of the agreement statistics. That floor stays what it was, for the purpose
it was set for, and the decision view does not use it.

Stage 4 is built, and it is another document: `docs/GAP.md`, the comparison of forest condition, need and allocation, written
from the tables in `50_gap/`. It describes where money went relative to where forest was lost. It is not an argument
about why forest was lost or work withheld, and nothing here stands in for one.

The two verifiers were run by this script as it wrote the document: `scripts/verify_layer.py`, unchanged, gave
"92 of 92 checks passed"; `scripts/verify_decision.py` gave "62 of 62 checks passed".

## 2. Why a unit and not a pixel

Hansen's loss is stand-replacing: a pixel is recorded as lost when its tree cover is cleared - by the definition in
the provider's record of the data, when at least half of it is (§18). So at the level of a pixel there is "standing"
and there is "lost", and "dense and losing" cannot be shown. The owner put it more strongly, "every lost pixel is bare
by construction"; the source bears out the weaker form, and the conclusion is the same. A place can be both only as an
area: this much closed forest standing, this much lost. Each unit is therefore classed from its hectares, and the
hectares are kept. The cell is a summary of them, and a unit's panel shows them all (§15).

## 3. The record behind every cell

`55_decision/condition_by_unit.csv` has one row for each of the 11,468 units and 67 columns. Before any
cell, it records, from Hansen (UMD/hansen/global_forest_change_2025_v1_13, as tabulated by stage 1, by band of canopy in the year 2000):

- **standing dense** hectares: land with `treecover2000 > 30`, less all loss Hansen records on it through 2025;
- **standing open** hectares: land with `10 < treecover2000 <= 30`, less all loss on it;
- **forest loss** in each window, split by the band the forest was in: lost from dense, lost from open;
- **loss on land with `treecover2000 <= 10`** in each window. It is reported, and it decides nothing.

**"Standing" is always now**, through 2025, whatever window is chosen. **It is the forest of 2000 with no loss recorded since; not a measure of tree cover today.** That is the wording
the owner ruled on 9 October 2026, and it is what the table's run record says and what the layer says in the legend,
in every unit's panel and under the ranked list.

**Until that ruling it was called a lower bound, and it is not strictly one in either direction.** It is too low
where forest grew: Hansen does not net off gain, so land that lost its cover and grew it back, and land that has
gained cover since 2000, is not in it. And recorded loss is itself uncertain both ways. The provider's record of the
data, registered in `00_raw/` (§14), says in its own words: "Accordingly, “net” loss cannot be calculated by subtracting figures for tree cover gain from tree cover loss, and current (post-2000) tree cover cannot be determined by subtracting figures for annual tree cover loss from year 2000 tree cover." and "In the original publication, the authors evaluated the overall prevalence of false positives (commission errors) in this data at 13%, and the prevalence of false negatives (omission errors) at 12%, though the accuracy varies by biome and thus may be higher or lower in any particular location." With missed loss
at about 12 per cent the subtraction leaves in forest that was lost; with false loss at about 13 per cent
it takes out forest that was not. So the words "lower bound" were taken out of the layer, the tables' record and this
document, and the reason is kept here. The split into dense and open is that of 2000: a stand that has thinned since is still
"dense" here. And the provider of the data cautions against reading the subtraction as present cover (§18).

**Why the lowest band decides nothing.** `docs/RESULTS.md` §3.1: of the 917 km² of loss recorded on land with
`treecover2000 <= 10`, 826 km², 90 per cent, is on land with no canopy at all in 2000. That is tree
cover that grew after 2000 and was removed, or an artefact of detection; it is not forest that stood in 2000. And its
rise over time is largely the producers' change of method: it goes 45, 245, 627 km² across
2001–2010, 2011–2017 and 2018–2025, while loss on the dense band (canopy above thirty per cent: the "forest mask" of
`docs/RESULTS.md`) goes 435, 444, 674. In the default
window that band carries 62,748 ha of recorded loss against 90,028 ha of forest loss. Had it
been let into the classification it would have moved many units for a reason that is not about forest.

**The table reconciles with the stage it is built from.** The owner set one condition: standing plus lost hectares in
each band must equal that band's hectares in the year 2000, for each unit and in total, against
`20_degradation/hansen_loss_by_canopy_band.csv`. This script made the comparison again from the table itself:

| band of canopy in the year 2000 | standing now, km² | lost in all years, km² | the two added: land in that year, km² | that land in the band table, km² | loss in the band table, km² |
|---|---|---|---|---|---|
| dense: `treecover2000 > 30` | 25,077.79 | 1,552.64 | 26,630.43 | 26,630.43 | 1,552.64 |
| open: `10 < treecover2000 <= 30` | 10,523.11 | 363.84 | 10,886.95 | 10,886.95 | 363.84 |

*n = 11,468 units; no unit is missing from either band. The band table prints two decimals of a square kilometre,
and the totals agree to that.* The build made 27 such comparisons (three bands, three kinds of unit, land and
two spans of loss) and stops if one fails.

For each unit: the dense band adds up exactly in 11,465 units and the open band in 11,467.
The build makes this test on the file it has written, read back as text, and this script made it again. In
3 units for dense and 1 for open the band does not add up, by 0.0001 ha, a square metre:
the source rounds each year's loss and the band's area to four decimals separately, so the years can add to a hair
more than the land. There, standing is set to zero and not left negative. **This is the one place where the identity
the owner asked for holds to a tolerance and not exactly**, and the run record counts the units.

One more thing rests on the same rounding, and it is not the identity. Stage 1's table prints for each unit and band
both the loss of each year and its own total over the whole record. "Lost" in this table is the sum of the years, the
only figure that can be cut into windows. That sum is not the source's own total in 1,765 units for dense and
1,478 for open, by at most 0.0005 ha. The build compares the two in every unit and stops beyond a tolerance
that its docstring gives (`0.002 ha`). So against stage 1's own total of all loss, standing is exact to that
tolerance and not to the last digit.

**How figures are compared with a threshold.** Hectares are added and subtracted as whole ten-thousandths, so every
hectare in the table is exact. A threshold is then compared with the figure as the map prints it, to two decimals, by
the rule that prints every other hectare on the map (`format(x, ".2f")`). So a unit's cell never contradicts the
hectares printed beside it. The other common rule, half up, would print 630 of the hectare figures of land, standing forest and loss
(the two hectare columns copied from the agreement test are not in that count) differently in the last digit, and would change the cell of no unit in any window. Read at four decimals and not as
printed, 2 units are mostly dense though their standing open is larger in the fourth decimal, and in
6 cases a loss counts as some though its fourth decimal is under the threshold. One more oddity of printing:
a total is rounded as a total, so in 1 unit the two printed parts of standing forest add up to the
threshold while the printed total is a hundredth under it, and in 2 cases the same happens to a loss. The
cell follows the printed total.

**What is blank in the table, and why.** `unit_name` in 168 units that have no name; `dense_open_ratio` in
708 units with no standing forest in either band; the tier in the units of the cell that is outside the
ranked list; the district check and the governance prompt in the 7,976 LGD panchayat units, which they do not
concern; and, in each window, the share of the units that have none, whose reason is then given in words in the
column beside it, which is blank wherever a share is given (§5.4). No hectare and no cell is blank.

## 4. The four windows

Loss is counted over a window of years, and the window is a choice. There are four, each with its own cell for every
unit. The layer opens on the first.

| window | what it is | Closed forest, little or no loss recorded - protect | Closed forest, loss recorded - find the cause first | Open forest, little or no loss recorded - assisted natural regeneration candidate | Open forest, loss recorded - restore | Little forest left, loss recorded - verify on the ground | Not a forest site | units in another cell than in the default window |
|---|---|---|---|---|---|---|---|---|
| 2018–2025 | the default: the years after plantation fell out of spending in the scheme's state report | 1,040 | 1,295 | 3,055 | 406 | 33 | 5,639 | - |
| 2001–2025 | the full record | 618 | 1,717 | 2,661 | 800 | 74 | 5,598 | 857 |
| 2017–2023 | CoRE Stack's window, so that corroboration is like for like | 1,140 | 1,195 | 3,129 | 332 | 25 | 5,647 | 236 |
| 2021–2025 | the most recent five years | 1,154 | 1,181 | 3,115 | 346 | 22 | 5,650 | 185 |

*n = 11,468 units in every row; each unit is in exactly one cell of each window.*

**Why 2018–2025 is the default.** It is the regime after plantation fell out of the scheme's spending. In the state's
own report (MIS report R6.20, `40_allocation/state_fy_r620_vs_dump.csv`), plantation is 24.2 per cent of
expenditure in FY2016-17 and 3.3 per cent in FY2018-19, and under one per cent in every later year. The decision
stage reads those two shares and stops if the second is not under half the first. Three
caveats come with that reason; the first and the third are from `docs/RESULTS.md` §8, the second is this document's. The high-plantation years of that report are a snapshot
frozen long ago (the row for FY2016-17 carries the stamp 10/10/2020). A financial year runs from April, and Hansen's
years are calendar years, so the window and the regime do not start on the same day. And why plantation fell is not
something these tables can say. The owner confirmed this window as the default, with these three caveats, on
9 October 2026 (§17).

**A cell's name speaks of loss recorded in the window chosen.** Under the full record that is at any time since 2001:
of the 800 units in "Open forest, loss recorded - restore" under 2001–2025, 394 lost under 1 ha in 2018–2025. The
layer's About text says so.

**The window is named wherever a cell is shown**: in the legend's title, in every unit's panel, at the head of the
ranked list and in every row of an exported list (§15). The corroboration badge carries its own window, 2017–2023,
whatever window is chosen (§11).

## 5. The two thresholds: proposed on 8 October 2026, accepted by the owner on 9 October 2026

Two thresholds turn hectares into cells. **Both are decisions. The owner took them on 9 October 2026, as they were
proposed** (§17): the standing minimum, and the loss minimum as the rule of the cells. What follows is what was
proposed, why, and how much the answer moves at two alternatives; none of it changed with the ruling. What the ruling
added is §5.4: because a fixed number of hectares follows the size of a forest, the loss is now also shown as a share.

- **(a) The standing minimum: 10 ha.** A unit with less standing forest than this, dense and open together, has
  "little or none".
- **(b) The loss minimum: 1 ha.** A unit that lost at least this much forest in the window, from dense and open
  together, has "some" loss.

Neither is the 100 ha of the agreement test. That floor exists so that a rate of loss is a stable number to
compare between two measures; here nothing is a rate.

### 5.1 The loss minimum

**A single pixel must not move a unit.** One Hansen pixel is 0.0725 ha in the middle of the state; the grid is in
degrees, so a pixel is a little smaller to the north and a little larger to the south. In the default window 147
units have a recorded forest loss above zero and under 0.0725 ha. That count is of a size, not of "one pixel or
less": it takes in slivers of a lost pixel cut off by a unit's boundary and, in the north, units that lost exactly one
whole pixel; and it leaves out units in the south that lost one whole pixel, which is a little more than 0.0725 ha
there and so falls in the second column below. The stage tables carry no latitude, so the two were not told apart; the
argument does not need it: there are units, well over a hundred in every window, whose cell one pixel would decide.

| window | units with forest loss above zero and under the area of the pixel in the middle of the state | units with forest loss from that area to under the loss minimum |
|---|---|---|
| 2018–2025 | 147 | 924 |
| 2001–2025 | 348 | 1,437 |
| 2017–2023 | 126 | 794 |
| 2021–2025 | 144 | 919 |

*n = 11,468 units in each window; the counts are of units, and a unit with no forest loss is in neither column.*

The proposal, 1 ha, is 13.8 pixels. It is the smallest patch the Forest Survey of India counts as forest
cover: its report gives the minimum as "more than or equal to one hectare in area" (the extract registered in
`00_raw/05_forest_reference/`), 1 ha. So "some loss" means the loss of at least the least thing the national
inventory would call forest.

**Is a loss of that size a real signal?** What can be asked of this table is whether loss recurs. Among units with at
least 10 ha standing that lost 1 ha or more in 2018–2021, 87.7 per cent (n = 1,171) lost that much
again in 2022–2025. Among those that lost under 0.0725 ha, or nothing, in 2018–2021, 5.2 per cent
(n = 4,028) lost 1 ha or more in 2022–2025.

| standing forest of at least, ha | lost at least the lower alternative, and again | lost at least the proposal, and again | lost at least the higher alternative, and again | lost under the mid-state pixel's area, or nothing, then the proposal or more |
|---|---|---|---|---|
| 5 | 88.8 (n = 1,391) | 87.5 (n = 1,177) | 87.5 (n = 951) | 4.3 (n = 4,989) |
| 10 | 89.1 (n = 1,381) | 87.7 (n = 1,171) | 87.7 (n = 948) | 5.2 (n = 4,028) |
| 25 | 90.1 (n = 1,336) | 88.8 (n = 1,139) | 88.3 (n = 934) | 6.7 (n = 2,907) |

*Each cell is a share in per cent with the number of units it is a share of. The rows are the three standing
minimums; the first three columns are the three loss minimums.*

**What this does not settle.** Recurrence is within two points whichever of the three loss minimums is used. It shows
that a loss at or above any of them is not noise; it does not pick between them. The choice of 1 ha rests on the
Forest Survey's patch and on being more than a dozen pixels, and that is a judgement.

**What a fixed number of hectares does: it follows the size of the forest.** The owner asked for a minimum in
hectares, and this is its consequence. The more forest a unit has, the likelier that some hectare of it was lost:

| standing forest in the unit, ha | forest-site units | of them with some loss in the default window, % | of those that lost the loss minimum or more in the first half of the window, the share that did again in the second, % | of those that lost under the mid-state pixel's area, or nothing, in the first half, the share that lost the loss minimum or more in the second, % |
|---|---|---|---|---|
| ten to twenty-five | 1,207 | 5.0 | 50.0 (n = 32) | 1.2 (n = 1,121) |
| twenty-five to fifty | 871 | 11.1 | 72.7 (n = 44) | 3.2 (n = 751) |
| fifty to a hundred | 852 | 22.8 | 70.5 (n = 105) | 5.8 (n = 652) |
| a hundred to two hundred and fifty | 979 | 29.2 | 82.0 (n = 183) | 5.6 (n = 682) |
| two hundred and fifty to five hundred | 621 | 43.3 | 91.4 (n = 175) | 9.5 (n = 349) |
| five hundred to a thousand | 558 | 53.2 | 93.9 (n = 231) | 9.9 (n = 263) |
| a thousand to five thousand | 589 | 67.4 | 94.3 (n = 315) | 17.4 (n = 190) |
| five thousand or more | 119 | 84.9 | 94.2 (n = 86) | 20.0 (n = 20) |

*n = 5,796 forest-site units, each in one row, classed by standing forest as printed; default window, whose
first half is 2018–2021 and second 2022–2025. The last two columns give a share in per cent with the number of units
it is a share of.*

Of forest sites with ten to twenty-five hectares standing, 5 per cent have "some" loss; of those with five
thousand or more, 85 per cent: 101 of 119 units in the state. In 22 of the
30 districts the unit with the most standing forest is in a cell with loss. A cell with loss therefore says
little about a large unit's rate of loss: 349 of the units in "Closed forest, loss recorded - find the cause first" lost under one per cent
of the forest they had at the start of the window, and 48 lost under a tenth of one per cent of it. The
unit of that cell with the most forest, kuchilaghati (132731), Mayurbhanj, has 55,114 ha standing and lost 35.77 ha. And the
other way: 74 forest-site units lost more than two per cent of the forest they had at the start of the
window and are in a cell without loss, because that came to less than 1 ha. All three are counted on the share a
unit's panel prints (§5.4), whose denominator is the forest at the start of the window; until 10 October 2026 this
paragraph counted them against standing forest. A unit's panel shows the hectares, so a reader can see which
kind of unit is in front of them; the cell alone does not say. The recurrence that speaks for the loss minimum is
also mostly a matter of large units: among forest sites of ten to twenty-five hectares that lost 1 ha or more in
the first half of the window, 50 per cent (n = 32) did so again in the second. The owner's
ruling on this (§17): the minimum stays a number of hectares as the rule of the cells; the names of the cells no
longer claim more than that rule (§7); and the loss is shown as a share beside the cell (§5.4).

### 5.2 The standing minimum

| standing minimum, ha | pixels in it | units with at least that much standing forest | share of all standing forest that is in them, % | rank correlation of a unit's loss rate between odd and even years, in the class of land that starts there | units in that class | share of that class with no loss recorded on that land in any year, % |
|---|---|---|---|---|---|---|
| 5 | 69 | 6,786 | 99.83 | 0.482 | 984 | 80.4 |
| 10 | 138 | 5,796 | 99.63 | 0.596 | 1,199 | 68.7 |
| 25 | 345 | 4,589 | 99.08 | 0.699 | 874 | 52.9 |

*n = 11,468 units. The last three columns are the repeatability of stage 1's kind, worked out by the decision
stage on the land this threshold is about (canopy above ten per cent in 2000, dense and open) by the method of
`20_degradation/agreement_floor_repeatability.csv`; for the two classes that table also has, the figures equal its
own, and the build stops if they do not. Classes are of land in the year 2000.*

At 10 ha, 5,796 units are forest sites and they hold 99.63 per cent of all standing forest. The
share barely changes across the three settings, so it does not pick between them. Nor does the evidence on
repeatability pick one. It rises steadily with the size of the class, with no break at any of the three: the rank
correlation of a unit's loss rate between odd and even years is 0.48 in the class that starts at 5 ha,
0.60 in the class that starts at 10 ha and 0.70 in the class that starts at 25 ha, and the share
of units with no loss recorded on that land in any year is 80, 69 and 53 per cent: more than
half in all three. (Loss on land with less canopy is not in that count.)

So the proposal is a judgement, and these are the two things it rests on. 10 ha is the lowest floor at which this
project's agreement test was itself run, and the lowest class of the repeatability table made on this land, the land
with canopy above ten per cent in 2000: on that land no table of stage 1 goes lower. Another table of stage 1 does go
lower (`20_degradation/forest_floor_repeatability.csv`), but on the forest mask, canopy above thirty per cent, which
is not the land this threshold is about; the proposal does not lean on it. And the higher alternative would set aside 1,207 more units, holding
0.55 per cent of all standing forest, as having little or none.

**The minimum is absolute, like the other.** 173 units have less than 10 ha of land altogether and are
in "little or none" whatever their cover. In 37 units of the cell "Not a forest site" standing forest covers
half or more of the unit's land. Their panels say what the test is.

### 5.3 Sensitivity

Every combination of the proposal and its two alternatives (5 and 25 ha standing; 0.5 and
2 ha of loss), in the default window:

| standing minimum, ha | loss minimum, ha | Closed forest, little or no loss recorded - protect | Closed forest, loss recorded - find the cause first | Open forest, little or no loss recorded - assisted natural regeneration candidate | Open forest, loss recorded - restore | Little forest left, loss recorded - verify on the ground | Not a forest site | units in another cell than at the proposal |
|---|---|---|---|---|---|---|---|---|
| 5 | 0.5 | 917 | 1,456 | 3,851 | 562 | 24 | 4,658 | 1,288 |
| 5 | 1 | 1,072 | 1,301 | 3,994 | 419 | 14 | 4,668 | 990 |
| 5 | 2 | 1,229 | 1,144 | 4,114 | 299 | 9 | 4,673 | 1,262 |
| 10 | 0.5 | 887 | 1,448 | 2,920 | 541 | 53 | 5,619 | 308 |
| 10 | 1 | 1,040 | 1,295 | 3,055 | 406 | 33 | 5,639 | the proposal |
| 10 | 2 | 1,196 | 1,139 | 3,166 | 295 | 18 | 5,654 | 282 |
| 25 | 0.5 | 808 | 1,417 | 1,890 | 474 | 151 | 6,728 | 1,477 |
| 25 | 1 | 945 | 1,280 | 2,003 | 361 | 93 | 6,786 | 1,207 |
| 25 | 2 | 1,095 | 1,130 | 2,099 | 265 | 57 | 6,822 | 1,468 |

*n = 11,468 units in every row.*

With the loss minimum at the proposal, moving the standing minimum to 5 ha or to 25 ha puts 990
or 1,207 units in another cell. With the standing minimum at the proposal, moving the loss minimum to 0.5 ha
or to 2 ha moves 308 or 282. **The standing minimum is the more consequential of the two.** The
same four moves in each window:

| window | standing minimum at the lower alternative | standing minimum at the higher alternative | loss minimum at the lower alternative | loss minimum at the higher alternative |
|---|---|---|---|---|
| 2018–2025 | 990 | 1,207 | 308 | 282 |
| 2001–2025 | 990 | 1,207 | 432 | 437 |
| 2017–2023 | 990 | 1,207 | 250 | 274 |
| 2021–2025 | 990 | 1,207 | 321 | 279 |

*Units whose cell differs from their cell at the proposal, of 11,468.*

### 5.4 Loss as a share: beside the cell, never in it

Added by the owner's ruling of 9 October 2026. It changes no cell: `scripts/05_check_rename.py` holds every unit's cell
in every window against the table as it stood before (§16).

For each unit and each window the table now carries two more figures:

- **forest at the start of the window**: the unit's dense and open hectares of 2000, less the forest loss recorded in
  the years before the window's first year (`forest_at_window_start_ha`). For the full record that is the forest of 2000;
- **the loss of the window as a share of it**, in per cent (`forest_loss_share_pct`), rounded half up to two decimals
  in whole numbers.

**Where the forest at the start of the window is under the standing minimum, 10 ha as printed, no share is
given**: a share of almost nothing means nothing. The table then holds the reason in words, "under 10 ha of forest at the start of the window: too little for a share to mean anything", and the
layer shows words, not a blank and not a zero. In the default window 5,808 units have a share and 5,660
have none; 22 of those are in a cell with loss recorded, all of them in the cell with little forest
left. By window:

| window | units with a share | units with none | of those, in a cell with loss recorded |
|---|---|---|---|
| 2018–2025 | 5,808 | 5,660 | 22 |
| 2001–2025 | 5,824 | 5,644 | 50 |
| 2017–2023 | 5,809 | 5,659 | 15 |
| 2021–2025 | 5,805 | 5,663 | 15 |

*n = 11,468 units in each window.*

How the share falls across the cells, in the default window:

| cell | units | with a share | no share: too little forest at the start | share under one per cent | one to under five per cent | five per cent or more | median share, % | largest share, % |
|---|---|---|---|---|---|---|---|---|
| Open forest, loss recorded - restore | 406 | 406 | 0 | 81 | 158 | 167 | 3.69 | 59.90 |
| Closed forest, loss recorded - find the cause first | 1,295 | 1,295 | 0 | 349 | 512 | 434 | 2.87 | 53.55 |
| Open forest, little or no loss recorded - assisted natural regeneration candidate | 3,055 | 3,055 | 0 | 2,961 | 89 | 5 | 0.00 | 7.93 |
| Closed forest, little or no loss recorded - protect | 1,040 | 1,040 | 0 | 989 | 45 | 6 | 0.00 | 7.27 |
| Little forest left, loss recorded - verify on the ground | 33 | 11 | 22 | 0 | 0 | 11 | 36.09 | 72.73 |
| Not a forest site | 5,639 | 1 | 5,638 | 0 | 1 | 0 | 2.85 | 2.85 |

*n = 11,468 units. The share is classed as printed. The median is of the units that have a share.*

Read against §5.1: 349 of the units in "Closed forest, loss recorded - find the cause first" lost under one per cent of the forest they had
at the start of the window, and 74 forest sites in a cell with little or no loss recorded lost over two
per cent of theirs. (§5.1 gives the same two counts: since 10 October 2026 it counts on this share too, and no longer
against standing forest, which is the forest at the start less the loss of the window.) The unit of that cell
with the most forest, kuchilaghati (132731), Mayurbhanj, had 55,150 ha at the start of the window and lost 0.06 per cent of it.

**A second order in the ranked list.** Within a tier the list is ordered by hectares lost, as before and as it
opens, or by share lost. It applies to the cells with loss recorded: there the units that have a share come first,
largest share first, and the units with no share after them, by hectares lost. The cells with little or no loss
recorded stay ordered by standing hectares under either choice. In the default window 1,653 of the
1,734 units in a cell with loss have another place within their district and cell by share than by
hectares. The order in use is named in the head of the list, carried in the page's address and written in every row
of an exported list (§15). It is an order within a tier; it moves no unit between tiers and it is not a score.

**What was not done for these two columns.** They were not in the table that two independent replicators rebuilt on
8 October 2026. `scripts/verify_decision.py`, which shares no code with the build, rebuilds both from the yearly
columns of stage 1 for every unit and window, with the blanks, their reason and their count, and the order by share
(§16). That is one independent rebuild, not two.

## 6. Mostly dense or mostly open, and the units near that line

A unit with at least the standing minimum is **mostly dense** if its standing dense hectares are at least its standing
open hectares, and **mostly open** otherwise. 2,335 units are mostly dense, 3,461 mostly open, and
5,672 have little or none.

A unit with a lot of both is the one a single word summarises worst. So the table flags the units where the smaller of
the two is within a fifth of the larger: **603 of the 5,796 forest-site units, 10.4 per cent**.
Their panels say "close call", and an exported list says so in a column of its own. The count at other margins:

| the smaller of standing dense and standing open is at least this share of the larger | units | units that are mostly dense or mostly open | of them near the boundary | of those, mostly dense | of those, mostly open |
|---|---|---|---|---|---|
| 0.5 | all units | 5,796 | 1,742 | 923 | 819 |
| 0.5 | LGD panchayat units | 4,006 | 1,098 | 567 | 531 |
| 0.5 | outside-village units | 1,790 | 644 | 356 | 288 |
| 0.6667 | all units | 5,796 | 1,061 | 543 | 518 |
| 0.6667 | LGD panchayat units | 4,006 | 680 | 345 | 335 |
| 0.6667 | outside-village units | 1,790 | 381 | 198 | 183 |
| 0.8 (the flag in the table) | all units | 5,796 | 603 | 299 | 304 |
| 0.8 (the flag in the table) | LGD panchayat units | 4,006 | 386 | 190 | 196 |
| 0.8 (the flag in the table) | outside-village units | 1,790 | 217 | 109 | 108 |
| 0.9 | all units | 5,796 | 278 | 142 | 136 |
| 0.9 | LGD panchayat units | 4,006 | 165 | 82 | 83 |
| 0.9 | outside-village units | 1,790 | 113 | 60 | 53 |

*n = 11,468 units; a unit with little or none is in no row of this table.*

A fifth is a round margin and not a finding: the table above is there so that another can be read off. The flag does
not change a unit's cell. It tells the reader that for this unit "mostly dense" and "mostly open" are a
fine distinction, and that the hectares beside the label are the thing to read.

## 7. The six cells

Rows: forest standing now is mostly dense, mostly open, or little or none. Columns: forest loss in the window is
none, or some. In the default window, in the provisional order of tiers:

| cell | standing forest now | forest loss in the window | units | LGD panchayat units | outside-village units | standing dense, ha | standing open, ha | forest loss in the window, ha | of the units, near the dense and open line |
|---|---|---|---|---|---|---|---|---|---|
| Open forest, loss recorded - restore | mostly open | some | 406 | 294 | 112 | 51,741 | 86,627 | 4,603 | 98 |
| Closed forest, loss recorded - find the cause first | mostly dense | some | 1,295 | 745 | 550 | 1,918,704 | 489,316 | 84,957 | 106 |
| Open forest, little or no loss recorded - assisted natural regeneration candidate | mostly open | none | 3,055 | 2,441 | 614 | 117,869 | 293,921 | 161 | 206 |
| Closed forest, little or no loss recorded - protect | mostly dense | none | 1,040 | 526 | 514 | 418,475 | 170,432 | 176 | 193 |
| Little forest left, loss recorded - verify on the ground | little or none | some | 33 | 19 | 14 | 64 | 116 | 97 | 0 |
| Not a forest site | little or none | none | 5,639 | 3,951 | 1,688 | 927 | 11,899 | 34 | 0 |

*n = 11,468 units: every unit is in one row. Hectares are sums over the units of the cell; "standing" is through
2025, and is the forest of 2000 with no loss recorded since; not a measure of tree cover today.*

**Five of the six names were changed on 9 October 2026, by the owner's ruling, and no unit moved.** With a flat
minimum of 1 ha of loss, the first names claimed more than the test behind them:

| name until 9 October 2026 | name as ruled |
|---|---|
| Open forest still losing - restore | Open forest, loss recorded - restore |
| Closed forest under pressure - find the cause first | Closed forest, loss recorded - find the cause first |
| Open forest - assisted natural regeneration candidate | Open forest, little or no loss recorded - assisted natural regeneration candidate |
| Protect - intact closed forest | Closed forest, little or no loss recorded - protect |
| Little forest left, recent loss - verify on the ground | Little forest left, loss recorded - verify on the ground |
| Not a forest site | unchanged |

*Six cells. The first column is read from the tiers table of the build of 8 October 2026, kept with the session's
working files; the second from the one on disk.*

Why, in figures read from the files:

- **"Under pressure" mostly meant large.** 349 of the 1,295 units of that cell lost under one per cent of
  the forest they had at the start of the window. The one with the most forest, kuchilaghati (132731), Mayurbhanj, has 55,114 ha
  standing and lost 35.77 ha. And 74 forest sites that lost over two per cent of the forest they
  had at the start of the window are in cells without loss, because that came to less than 1 ha (§5.1, §5.4).
- **"Intact" was contradicted.** Of the 671 units of that cell that the comparison with CoRE Stack
  covers, 157 are flagged by CoRE Stack for degradation (19 of them under the East Coast model, where
  that flag is itself unreliable, §11). The 1,040 units of the cell carry 176 ha of forest loss in the
  window between them; 422 of them lost 1 ha or more at some time in 2001–2025, and only 226
  have no recorded forest loss at all since 2001. And Hansen cannot see a canopy thinning.
- **A name now states the test and no more.** "Loss recorded" is 1 ha or more of forest loss in the window
  chosen; "little or no loss recorded" is less than that. The words after the hyphen say what the cell points to, as
  before. The sentence under each name in a unit's panel states the same test in hectares.

**The gate on the renaming.** Every unit's cell as it stood before, in each of the four windows, was taken through
that list of names and compared with the table as it is now: 45,872 assignments, and every one matches. The
51 columns the table had are equal as text in every row (584,868 cells), so the hectares, the orders
within a cell, the tier and the corroboration are what they were; 16 columns were added beside them
(§5.4). `scripts/05_check_rename.py` does this, stops on one mismatch, and writes `55_decision/rename_gate.json`. The
table it compares with, whose `sha256` begins `f129962e816e4da3`, is the one two independent replicators rebuilt on
8 October 2026 (§16).

More about the names.

- **They are the owner's**, with one change of typography that he accepted: the layer writes the dash in them as a
  hyphen. The governance prompt of §12, which was given as a quotation, keeps its dash. Every name is shown in full
  everywhere, the legend included: none was shortened there.
- **"Open forest, little or no loss recorded - assisted natural regeneration candidate"** is the largest cell among the forest sites by number of units (3,055). The official list of
  permissible works does not name that work (§13).
- **"Open forest, loss recorded - restore" is about what stands, not about what was lost.** A unit is in that cell when the forest standing
  in it is mostly open and it lost forest of either band. 41 per cent of the cell's forest loss in the
  window was from the dense band, and in 102 of its 406 units more was lost from dense than from open.
  The panel shows the two losses apart.
- **"Little forest left, loss recorded - verify on the ground"** holds 33 units. Little forest stands in them and loss is recorded: plantation
  felled, regrowth cleared, or an error. The name says what to do about that.

**The order inside a cell**, as the run record states it: "within a district, within a cell: cells with loss by forest loss in the window, largest first; the others by standing hectares of the row's band; ties by unit_id. No order across districts; no score". The order is kept district by district and
nowhere else (§9). The head of every ranked list, the About text and a column of every exported row say what orders
the units within a tier.

**One column of the table is a number where the layer shows a label.** `tier_provisional_2018_2025` holds the place of
the unit's cell in the provisional order, for the default window only, as a whole number. It is a convenience for
anyone working from the table; the labels are in `55_decision/tiers.csv`, and the layer never shows the bare number.

## 8. The tiers: provisional

The ranked view puts the cells in an order. The status of that order, as the run record carries it: "PROVISIONAL - to be set with the Foundation for Ecological Security; a user control in the layer, not a constant".

| tier, as the layer labels it | the line recorded for it |
|---|---|
| Tier 1: Open forest, loss recorded - restore | Open forest is where the standing canopy is thinnest, and loss is recorded in the window: restoration has the most to hold on to and the most to lose by waiting. |
| Tier 2: Closed forest, loss recorded - find the cause first | Closed forest with loss recorded in the window needs its cause found before any work is planned; a forester could reasonably put this tier first. |
| Tier 3: Open forest, little or no loss recorded - assisted natural regeneration candidate | Open forest with under 1 ha of loss recorded in the window is a candidate for assisted natural regeneration. |
| Tier 4: Closed forest, little or no loss recorded - protect | Closed forest with under 1 ha of loss recorded in the window calls for protection and conservation work, not planting. |
| Tier 5: Little forest left, loss recorded - verify on the ground | Little forest stands and loss is recorded in the window: the record may be of plantation felled, of regrowth cleared, or of error - it has to be seen on the ground. |
| Not ranked: Not a forest site | On the map, outside the ranked list: under 10 ha of standing forest and under 1 ha of forest loss recorded in the window to act on. |

*Six cells: five tiers and the one cell left outside the ranked list.*

The lines of the first, second and fifth tiers argue for a place in the order. Those of the third and fourth say what
the tier is for and give no argument for its place: why, of the two cells without recorded forest loss, open forest
comes before closed is argued nowhere yet. It is the owner's provisional order.

**A forester could reasonably put the second tier above the first.** Closed forest that is being removed is arguably
the more urgent thing to understand; open forest with loss recorded is arguably where work has most to gain. That is
a judgement for the Foundation, and the order above is only where the layer starts.

So **the order is a control in the layer, not a constant.** A user can move any tier up or down and go back to the
provisional order. The legend, the ranked list and its head follow, the page's address carries the order, and an
exported list states the order that made it and whether the user changed it; otherwise "the first tier" would mean
different things in different files (§15).

**A rank is shown as a tier label, never as a bare number**, in the legend, in the list and in the export.

**There is no composite score.** No index, no weights, no number out of a hundred, in the table or in the layer.
Within a tier, units are ordered by one physical quantity (§7), and across tiers by the order above.

## 9. Ranked within a district, never across the state

The ranked view is scoped to a district. The user picks one; its units are listed tier by tier. **There is no
state-wide ranking, and none was built**: the page holds an order for each district and no order across them.

**The reason the owner gave is in this project's own analysis, and it is narrower than it sounds.** Among the LGD
panchayat units of the agreement test's headline, from `20_degradation/agreement_summary.csv`: within districts the
odds ratio is 2.84 (interval 1.92 to 5.24); across the state it is 1.55
(0.80 to 3.61), an interval that includes one. So for those units agreement across the state is
not established, and a state-wide leaderboard of them would rest on a comparison the analysis does not establish. The
layer's About text says this, with the units it is true of, and so does the panel under the map while no district is
chosen.

**What that row is, and what it is not.** It is the delivered headline of the agreement test: 1,649 LGD panchayat
units in 25 districts, with the East Coast zone left out, at the 100 ha floor (`docs/RESULTS.md` §5).
The same file carries the same comparison at two lower floors:

| floor of the agreement test, ha | LGD panchayat units compared | odds ratio across the state (interval) | odds ratio within districts (interval) |
|---|---|---|---|
| 10 | 3,146 | 2.62 (1.42 to 5.02) | 3.04 (2.17 to 4.63) |
| 50 | 2,067 | 2.11 (1.09 to 4.54) | 3.26 (2.17 to 5.43) |
| 100 (the headline) | 1,649 | 1.55 (0.80 to 3.61) | 2.84 (1.92 to 5.24) |

*LGD panchayat units, East Coast zone left out, window 2017–2023. Intervals are from resampling whole districts.*

Four things qualify the reason. The figures of the first, second and fourth are from the same file; the counts of
units and of districts are from the decision table.

- **It is about LGD panchayat units only.** At the same headline, for all units together the across-state odds ratio
  is 1.80 (1.10 to 2.91), and for outside-village units 2.06 (1.34 to 3.33): both
  intervals lie above one. The ranked lists hold both kinds of unit.
- **It is about one floor.** At the two lower floors the across-state interval for LGD panchayat units lies above one
  as well; the within-district agreement holds at all three.
- **It is about 1,649 units.** The ranked lists of the default window hold 5,829, of which 2,938
  carry no badge at the test's 100 ha floor (§11); the decision view uses none of these floors (§5).
- **It is about the headline's population, and about districts taken together.** The headline leaves the East Coast
  zone out. With those units kept, the across-state odds ratio for LGD panchayat units at the same floor is 2.30
  (1.10 to 4.70), an interval above one; the ranked lists make no such exclusion. And the
  within-district figure is one figure pooled over 25 districts. In 14 of them one of the two
  measures flags no LGD panchayat unit of the comparison, so the district adds nothing to it. In 5 districts
  (Bhadrak, Jagatsinghapur, Kendrapara, Khordha, Puri) no unit of either kind is in the comparison at all; their lists hold 187 ranked
  units. So the figure says nothing of any one district's list.

So "the two measures do not agree across the state" is not what the file says; "for LGD panchayat units at the
headline, agreement across the state is not established" is. What the file does bear out for LGD panchayat units is
that agreement within districts holds at all three floors, where agreement across the state does not hold at the
headline. That, and not the absence of agreement across the state, is the case for ranking within a district. The
owner accepted this narrower wording, which is the one the layer uses, on 9 October 2026 (§17). No state-wide ranking
was built.

What a district's list holds, in the default window:

| district | units in the ranked list | of them outside-village units | units outside the list: not a forest site |
|---|---|---|---|
| Anugul | 249 | 63 | 133 |
| Balangir | 273 | 53 | 148 |
| Baleshwar | 46 | 8 | 537 |
| Bargarh | 168 | 21 | 149 |
| Baudh | 89 | 36 | 74 |
| Bhadrak | 8 | 1 | 259 |
| Cuttack | 78 | 18 | 508 |
| Debagarh | 95 | 20 | 18 |
| Dhenkanal | 161 | 29 | 156 |
| Gajapati | 254 | 74 | 17 |
| Ganjam | 457 | 185 | 699 |
| Jagatsinghapur | 24 | 2 | 216 |
| Jajapur | 16 | 3 | 393 |
| Jharsuguda | 86 | 18 | 21 |
| Kalahandi | 324 | 94 | 219 |
| Kandhamal | 374 | 150 | 4 |
| Kendrapara | 11 | 4 | 295 |
| Kendujhar | 274 | 41 | 168 |
| Khordha | 72 | 3 | 177 |
| Koraput | 427 | 174 | 134 |
| Malkangiri | 164 | 46 | 73 |
| Mayurbhanj | 281 | 16 | 257 |
| Nabarangapur | 188 | 66 | 169 |
| Nayagarh | 214 | 55 | 75 |
| Nuapada | 112 | 28 | 75 |
| Puri | 72 | 5 | 297 |
| Rayagada | 589 | 380 | 151 |
| Sambalpur | 251 | 94 | 33 |
| Subarnapur | 84 | 12 | 106 |
| Sundargarh | 388 | 105 | 78 |

*n = 11,468 units in 30 districts: 5,829 in a ranked cell, 1,804 of them outside-village
units. The ranked list of 30 of the 30 districts holds outside-village units. A unit is in one district: an LGD panchayat unit in its census district, an
outside-village unit in the district assigned to it (§12).*

## 10. What stands beside the tier, and what stays out

In the ranked list each unit's row carries, beside its tier label: standing dense and standing open hectares; forest
loss in the window, and that loss as a share of the forest at the window's start (§5.4); the corroboration badge (§11); Scheduled Tribe share (`st_share`); the development index of 2011
(`adi_2011`); past expenditure on work types that name forest; and whether it is an outside-village unit.

- **Need and allocation are beside the tier and never inside it.** They do not move a unit up or down.
- **Past forest-named expenditure is labelled for what it is.** The geotagged record effectively ends in FY2017-18:
  97.8 per cent of all its expenditure, and 92.9 per cent of its expenditure on work types
  that name forest, is on works started in or before that year. The column's heading says so. It is mostly where
  works were put up to then, and it is not current allocation. 2,781 units have any such expenditure recorded,
  and 371 of them show only works started later; the other 8,687 have none recorded.
- **Scheduled Tribe share can filter the list and never orders it.** The filter has three settings, and they are the
  class breaks of the existing Scheduled Tribe layer (`docs/LAYER.md`), chosen there and not here: eighteen per cent
  or more, above thirty-three per cent, and more than fifty per cent (a share that prints as exactly thirty-three is
  in that layer's class below the break, so the middle setting is labelled "above"). The order within the list does not change. Outside-village units have no census data, so the filter cannot be applied
  to them: a box keeps them in the list or leaves them out, and the page says how many either way.
- **What is blank.** `st_share` is blank for 123 LGD panchayat units (no resident population in the census
  rows) and `adi_2011` for 534. The list says which, in words. For the 3,492 outside-village units both
  columns read "no census data for this land", never blank and never zero (§12).
- **Whether Scheduled Tribe share belongs in a shared ranked list is the Foundation's call.** `docs/LAYER.md` §9
  records, with its page reference, that the Commons Connect paper reports that in one of its pilot blocks, Angul, in
  this state, the community did not favour the mapping of inequity. That paper is not among the files registered in
  `00_raw/`, so this document repeats the record and has not read the paper again.
- **SHRUG-derived columns stay out**, as before: no poverty estimate is in the decision table, the view or the export.
  One judgement recorded earlier carries over: the development index of 2011 is kept in the layer on the reading, set
  out in `docs/DATA_NOTES.md`, that it is computed from census rows; a stricter reading of SHRUG's terms would remove
  it. **By the owner's ruling of 9 October 2026 it is no longer a column of the exported list**, which is the file that
  gets passed on; it stays in the interactive view of `60_layer/`, as a layer of its own and as a column of the list
  on the page. **Since 10 October 2026 it is also left out of the copy made to be passed on**
  (`70_share/odisha_forest_decision_layer/`, §14): no file that is passed on carries the index for a unit. That was a
  call of the instruction that opened stage 4, and it is reversible (§17.3). Whether Scheduled Tribe share belongs in
  a list that is passed on is still the Foundation's call.

## 11. Corroboration: what the existing comparison already says

No new agreement statistic was built. Each unit carries what the existing two-measure comparison
(`20_degradation/agreement_by_unit.csv`) already says of it: both measures flag it, only Hansen, only CoRE Stack,
neither, or not compared, with the reason.

| what the badge rests on | units | both measures flag it | only Hansen | only CoRE Stack | neither | not compared |
|---|---|---|---|---|---|---|
| compared, in the headline of the agreement test | 2,423 | 137 | 348 | 348 | 1,590 | 0 |
| compared, under the East Coast zone model: badge carries the note | 468 | 59 | 61 | 53 | 295 | 0 |
| not compared: below the agreement test's floor | 7,748 | 0 | 0 | 0 | 0 | 7,748 |
| not compared: below the floor, and CoRE Stack gives no class on such land | 808 | 0 | 0 | 0 | 0 | 808 |
| not compared: at or above the floor on Hansen's grid, and CoRE Stack gives a class on less of that land than the floor | 21 | 0 | 0 | 0 | 0 | 21 |

*n = 11,468 units: 2,891 compared, 8,577 not. The first row's four counts equal the agreement
record's own; so do the East Coast count and the count not compared.*

- **The badge has its own window, 2017–2023**, and is labelled with it whatever window the user has chosen. With the
  window set to 2017–2023 the cell and the badge are about the same years; in any other window they are not, and the
  label is there so that nobody reads them as if they were.
- **The 468 units under CoRE Stack's East Coast zone model** carry a note on the badge: the placebo failed
  there, so corroboration is unreliable (`docs/RESULTS.md` §5.2). That failure itself rests on 8
  districts. Their class is the one computed with every unit
  kept, since the headline leaves them out.
- **A flag is relative.** It marks the top fifth of the units compared on that measure, not a stated amount of loss
  or degradation (`docs/RESULTS.md` §5).
- **"Not compared" is most units**, and the reason is always the floor of the agreement test, which the decision view
  does not use. So most small forest sites have a cell and no badge.
- **"No CoRE Stack coverage" turned out not to be a reason of its own.** The owner expected two reasons for a unit not
  being compared: below the floor, or no CoRE Stack coverage. Every unit not compared is below the floor on one of the
  two grids. In 808 of them CoRE Stack assigns no class to the unit's land with canopy above ten per cent
  in 2000 - in 696 because the unit has no such land at all. That is what their badge says. It does not
  mean the product fails to reach the unit. (The table's code for this basis, `below_floor_no_corestack_coverage`,
  keeps its first name; the words shown are the ones above.)
- **The counts in the last table but one are by basis; pooled, they would mix two cut-offs.** A flag in the first row
  is cut among the headline's units, a flag in the second among every unit kept. The run record labels the pooled
  counts "do not quote". The table below pools them by cell, and is to be read with that in mind.

How the badge falls across the cells, in the default window:

| cell, in the default window | units | both measures flag it | only Hansen | only CoRE Stack | neither | not compared |
|---|---|---|---|---|---|---|
| Open forest, loss recorded - restore | 406 | 2 | 72 | 9 | 141 | 182 |
| Closed forest, loss recorded - find the cause first | 1,295 | 194 | 335 | 170 | 461 | 135 |
| Open forest, little or no loss recorded - assisted natural regeneration candidate | 3,055 | 0 | 1 | 65 | 770 | 2,219 |
| Closed forest, little or no loss recorded - protect | 1,040 | 0 | 1 | 157 | 513 | 369 |
| Little forest left, loss recorded - verify on the ground | 33 | 0 | 0 | 0 | 0 | 33 |
| Not a forest site | 5,639 | 0 | 0 | 0 | 0 | 5,639 |

*n = 11,468 units. The badge is of 2017–2023 and the cells here are of 2018–2025: the two are not the same years.*

## 12. The outside-village units

The 3,492 outside-village units are land outside any revenue village. They have forest: they are 30.4 per
cent of the units and hold 54.5 per cent of all standing forest. So they are classed and ranked like any
other unit, and 1,804 of them are in a ranked cell in the default window (§9).

Their panel differs in three ways.

- **A governance prompt**, in these words: "No revenue village — this land is in no village plan. Whose plan covers it?"
- **What their district rests on.** An outside-village unit has no census district; one was assigned in `10_units/`,
  and the panel shows how that assignment was checked:

| what the assigned district rests on | outside-village units |
|---|---|
| the name on its boundary polygon; none of the district checks' flags is raised | 3,237 |
| moved off the name on its polygon | 13 |
| its polygon names no district | 19 |
| ambiguous between two districts | 3 |
| flagged: one check contradicts the district it carries | 82 |
| no check possible | 139 |

*n = 3,492 outside-village units. A unit can carry more than one of these statuses (1 of them do), so the
column can add to more than n. LGD panchayat units carry none: their district is the census's.*

  The first status means that none of the flags of `10_units/` is raised, which is less than "every check agrees":
  in 15 of those units the neighbours' largest district is another one by the tally the rule uses, by
  name (44 by the tally by census code, which the record reports beside it), and the rule of `10_units/` flags
  that only when the unit's own district is absent from its neighbours altogether.

- **Need columns read "no census data for this land"**, never blank and never zero. The census has no rows for this
  land. A zero would be a claim.

## 13. Work types: the official list of permissible works

**The list was found, verified and registered.** It is: Ministry of Rural Development notification S.O. 5448(E), 5 October 2026; Gazette of India, Extraordinary, Part II, Section 3(ii), No. 5238; Gazette ID CG-DL-E-05102026-276796. Source: https://egazette.gov.in/WriteReadData/2026/276796.pdf, 1,700,498 bytes, `sha256`
`ec89d3a85bf49f1a4218b897c1daca2b3ab86d71b42f8f52c2d9860b6e0279a4`. The file is on this machine and has that size and hash. `00_raw/data_manifest.csv` has 5 rows for this: the list with its
address, bytes, hash and date; the transcription; the table made from it; the Act it is issued under (The Viksit Bharat-Guarantee for Rozgar and Ajeevika Mission (Gramin): VB-G RAM G Act, 2025 (No. 36 of 2025), as published in the Gazette of India, Extraordinary, Part II, Section 1, No. 60, 21 December 2025);
and the Ministry's press release that prints the list's totals. The release was added after the first review and
the check was made stronger after each of the three. So `00_raw/` was written to more than once for this. Against the
last commit it is addition only: nothing that was in `00_raw/` before is changed. Within this batch it is not: the
check script there was rewritten in place after each review, the run record it writes was overwritten each time it
ran, and the notes of the new manifest rows were reworded to match. The table itself came out the same, byte for
byte, every time (its hash is in the manifest), and the
committed manifest's rows are untouched (§16).

**It was checked against the source's own totals.** `00_raw/06_scheme/_build_schedule_extract.py` stops unless the
table has 375 rows numbered without a gap, the total the Ministry's release prints, and unless the rows in the
Act's four categories number 128, 111, 98, 38, the totals the same release prints (Press Information Bureau release 2319426, 6 October 2026; https://www.pib.gov.in/PressReleasePage.aspx?PRID=2319426). The
release is registered and the totals are read out of its text, not typed. This script counted the categories again.

**And against the Gazette itself, cell by cell.** The script walks the text of the Gazette's English table once, in
the Gazette's own order, with capitals and dashes kept: each of the 375 rows must come next, its work name whole, with
exactly its own work type before it and nothing between rows but the pages' running heads and the 30 sub-item
and 4 category headings, each word for word; straight after the last row must come the notification's
file number. Where a work type ends and its name begins cannot be seen in running text, so that is taken from the
positions of the words on the page: every row must begin on the page the transcription gives it, below the row
before, on a line where the first word of its work type stands at the left edge of the second column and the first
word of its work name at the left edge of the third; and then its two cells, read whole from where the words stand -
every word from that line down to the line the next row begins on, split at the line between the two columns - must
be the transcription's. 375 rows read so. It was tried on 22 deliberate errors put into a copy of the
transcription, and each stopped it: the names of Sl. 105 and Sl. 106 changed over; the name of Sl. 91 cut short; the name of the last row, Sl. 375, cut short; Sl. 372 given the work type of Sl. 375; the name of Sl. 201 put in place of the name of Sl. 200; the first word of the name of Sl. 372 moved into its work type; the first two words of the name of Sl. 100 moved into its work type; the last word of the work type of Sl. 121 moved into its name; the last word of the work type of Sl. 178 moved into its name; the last two words of the work type of Sl. 261 moved into its name; Sl. 373 and 374 run into one row, and Sl. 375 split in two, the second half with a blank work type; Sl. 1 and 2 run into one row, and Sl. 87 split in two with no cell left blank; the name of Sl. 108 written without its capital; the mark of page 20 taken out, so that its rows are given page 19; the mark of page 28 moved three rows up; a hyphen written for the dash in the heading of Category III; a dash written for the hyphen in the work type of Sl. 375; Sl. 89 split in two where its name runs on to a second line, and Sl. 90 and 91 run into one row; the end of the name of Sl. 227 given to the work type of Sl. 228; Sl. 2, in the middle of page 17, given page 18; two words of a sub-item heading run together; a space put before the dash in the heading of Category II, which prints none. The record of those trials is a working file of the session (§20).
What the trials show is that these errors stop it, not that no error could pass: two earlier forms of this check
passed their own trials and let through errors a reviewer then found.

**What was not checked**, in the extract's own words: the digits of the serial numbers against the PDF: they are not in its text layer and were read from the page images by the transcriber; what is established is that the n-th row printed is the n-th row here; the Hindi half of the notification; amendments after 8 October 2026.

**Only this list is used.** No count or list of works from anywhere else enters the work-type fields: not the count in
`README.md`, which the manifest's note attributes to an earlier list circulated for comments (that letter is not
registered here), and none from the owner's earlier messages. Had the
list not been found, every field would read "pending — schedule not yet registered".

Each cell's field, as it appears in "why this tier" on every unit of the cell. Each group of rows stands under the
list's own work type for those rows:

| cell | its work-type field, as every unit of the cell shows it |
|---|---|
| Open forest, loss recorded - restore | Plantation - Sl. 105 Line plantation of forestry trees for community; Sl. 108 Wasteland block plantation of forestry trees for community; Sl. 110 Block plantation of forestry trees in fields for community. Afforestation - Sl. 91 Raising of bamboo plantation for community. Soil moisture conservation - Sl. 121 Construction of continuous contour trench for community; Sl. 123 Construction of staggered contour trench for community. Forest fire management works - Sl. 372 Raising of firebreak hedges for community; Sl. 373 Construction of forest fire line for community; Sl. 374 Raising of fuel buffer zone for community. |
| Closed forest, loss recorded - find the cause first | Find the cause before choosing work; no row of the list is a way of finding it. If the cause is fire: Forest fire management works - Sl. 372 Raising of firebreak hedges for community; Sl. 373 Construction of forest fire line for community; Sl. 374 Raising of fuel buffer zone for community. |
| Open forest, little or no loss recorded - assisted natural regeneration candidate | Assisted natural regeneration is not in the list: the word regeneration is in none of its 375 rows. Rows that could support it: Soil moisture conservation - Sl. 121 Construction of continuous contour trench for community; Sl. 123 Construction of staggered contour trench for community. Forest fire management works - Sl. 372 Raising of firebreak hedges for community; Sl. 373 Construction of forest fire line for community; Sl. 374 Raising of fuel buffer zone for community. |
| Closed forest, little or no loss recorded - protect | Protection, not planting. In the list: Forest fire management works - Sl. 372 Raising of firebreak hedges for community; Sl. 373 Construction of forest fire line for community; Sl. 374 Raising of fuel buffer zone for community. |
| Little forest left, loss recorded - verify on the ground | None until the recorded loss has been seen on the ground. |
| Not a forest site | None: not a forest site. |

*Six cells; 9 distinct rows of the list are cited, each by its serial number, and this script checked that the
work named beside each number is that row of the table and that it stands under that row's own work type.*

Every field is followed in the panel by this note: "No row of the list names forest land, and the list does not sort its works by the condition of a forest. Which rows bear on a cell is this project's proposal, to be set with the Foundation for Ecological Security; the rows that name forest and are cited by no cell are listed under Work types in the text on how to read this layer. Serial numbers were read from the page images of the Gazette."

**The rows that name forest and are cited by no cell.** 24 rows of the list hold the word forest in their
work type or name. 17 of them are cited by no cell. They are listed so that the Foundation can see what
was passed over, and overrule it:

| serial number | work type | work name |
|---|---|---|
| Sl. 90 | Afforestation | Plantation in coastal area for community |
| Sl. 92 | Afforestation | Raising of cactus plantation for community |
| Sl. 93 | Afforestation | Raising of mangrove plantation for community |
| Sl. 94 | Afforestation | Construction of vegetable pandals or trellis for community |
| Sl. 95 | Afforestation | Construction of vegetable pandals or trellis for individuals |
| Sl. 96 | Afforestation | Raising of bamboo plantation for individual |
| Sl. 97 | Afforestation | Raising of cactus plantation for individual |
| Sl. 98 | Afforestation | Miyawaki plantation for ecological restoration post cyclone and other natural calamities for community |
| Sl. 104 | Plantation | Block plantation of forestry trees in fields for individual |
| Sl. 106 | Plantation | Along the coastline plantation of forestry trees for community |
| Sl. 107 | Plantation | Along the coast block plantation of forestry trees for community |
| Sl. 109 | Plantation | line plantation of forestry trees for individual |
| Sl. 111 | Plantation | Agro forestry block plantation for individual |
| Sl. 112 | Plantation | Agro forestry block plantation for community |
| Sl. 113 | Plantation | Agro forestry block plantation in wastelands for community |
| Sl. 333 | Processing unit | Construction of forest produce processing unit for community |
| Sl. 375 | Allied measures - forest | Construction of animal protection trenches for community |

*n = 17 rows; the rule is the word "forest" in the row's work type or work name, which takes in
"afforestation" and "forestry".*

One of them needs saying aloud. The list's own item for forest work is "(vi) forest fire management works, including firebreaks, fuel buffer zones and allied measures", and it has a row that is neither
fire nor planting and that no cell cites: Sl. 375, Allied measures - forest: Construction of animal protection trenches for community. Whether trenches of that kind protect a forest from grazing, or
fields from wild animals, the list does not say, so this project did not assign the row; the Foundation will know.

Four limits on what this mapping is.

- **No row of the list names forest land.** The list names works, and for some of them a kind of place ("wasteland",
  "in fields", "along the coastline"); none says a work may be done on forest land.
- **Assisted natural regeneration is not a work the list names.** These words are in no row, type or heading of the
  table: regeneration; forest land; grazing; biodiversity. The cell with the most units among the forest sites points to that work (§7), so for it the
  field names the rows that could support it and says the work itself is absent.
- **Which rows bear on which cell is this project's proposal**, to be set with the Foundation. The list does not sort
  its works by the condition of a forest.
- **The list carries no unit, rate or cost.** The plantation unit cost under the scheme therefore stays blank, as the
  standing rule requires; nothing here supplies it.

The list was three days old when it was registered and can be amended by a later notification. It should be checked
again before a later use.

## 14. The site-level overlay

The units say where to look; they do not show where inside a unit the loss is. For that the layer can lay Hansen's
loss over the map as public map tiles. **It is optional, online, and off unless ticked.**

- **With no network the layer is exactly what it was.** Nothing is asked for until the box is ticked. If the browser
  reports no connection, or the tiles cannot be reached, the box does not stay ticked and the control says the
  overlay needs a connection; if the overlay's file is missing, the box does not stay ticked and the control says the
  file is not beside the page. Everything else works as before.
- **It belongs to the decision view and to nothing else.** Its box is folded away with that view's other controls
  while an ordinary layer is on, and the overlay switches itself off when the view is left. No existing view can show
  it or be changed by it.
- **It does not pretend when tiles fail.** As soon as one tile fails, the control beside the box and the note drawn
  on the map both say that where no pink is drawn, that is not a sign of no loss; by the page's code the warning
  stays until the overlay is drawn again. The note, with the credit, stays on the map when the rest of the legend is
  hidden. What the page has no words for is tiles still on their way: between the tick and the first tile it says
  the overlay is on while no pink is yet drawn, and on a slow connection that can last. When every tile asked for has failed, the overlay takes itself off as unreachable, however few they
  were; when eight in a row fail after some had arrived, it takes itself off as lost. Eight is a round number.
- **It cannot come on behind the user's back.** Its file is asked for on a tick, and if the box has been unticked or
  the view left by the time the file arrives, nothing is drawn.
- **Where its code lives.** The layer's two files, `index.html` and `data.js`, ask the network for nothing, and the
  existing checks that enforce this are unchanged and still pass. The overlay's code is in a third file,
  `60_layer/overlay.js`, loaded only when the box is ticked. So the existing statements that the layer is "pre-computed and
  offline" and fetches nothing remain true of the layer with the overlay off, which is how it opens. They are not true
  while the box is ticked, and the layer's About text says so in as many words. One thing about this has to be said
  plainly: the unchanged check `scripts/verify_layer.py` still prints that the page's "own script asks for nothing
  else" than `data.js`. That is true of the page as it opens; the check looks for certain words and cannot see the
  few lines that load the overlay's file on a tick. `scripts/verify_decision.py` pins those lines down instead: one
  script element, one address, reached only from the box's own change.
- **What leaves the machine when it is ticked**, as the registration puts it: only requests for tiles, to the registered host and no other, and only while the box is ticked: each carries the tile's place and zoom and the years of the window chosen, with the browser's usual headers. Opened from disk, the page has no web address of its own to pass on. Nothing about a unit is sent.
  The control says this beside the box.

**The endpoint and its terms, as registered** in `scripts/layer_overlay.json` (as read 2026-10-08T12:31:13Z):

| | |
|---|---|
| provider | Global Forest Watch (World Resources Institute) |
| address | `https://tiles.globalforestwatch.org/umd_tree_cover_loss/v1.13/dynamic/{z}/{x}/{y}.png?render_type=true_color&tree_cover_density_threshold=10` |
| where it is documented | https://tiles.globalforestwatch.org/openapi.json - the specification behind the provider's own reference pages https://tiles.globalforestwatch.org/ and https://tiles.globalforestwatch.org/docs. It states the path /umd_tree_cover_loss/{version}/dynamic/{z}/{x}/{y}.png, the versions (latest, v1.11, v1.12, v1.13) and the query parameters start_year, end_year, render_type and tree_cover_density_threshold. It names no host: by the OpenAPI rule the host is the one that serves the document |
| what kind of documentation | a machine-generated API reference on the tile host. There is no prose guide; the provider's developer help does not name the tile host |
| data the tiles carry | Hansen/UMD Global Forest Change v1.13, loss through 2025 |
| the version in the address | v1.13 is in the address. The alias 'latest' is not used: it moves to the next release without notice |
| the years drawn | start_year and end_year are added by the page from the window chosen for the decision view |
| canopy setting | tree_cover_density_threshold=10: loss on land with about 10 % tree canopy or more in 2000, the dense and the open band of the decision view together. The reference says 'greater than or equal to this threshold'; the unit tables use strictly above 10 |
| the tiles | 512-pixel PNG on the ordinary web-map grid; with render_type=true_color, pink on transparent. Below zoom 12 a tile is an aggregate shaded by the density of loss |
| finest zoom this layer asks for | 12: this layer's own setting, not a limit of the provider: a tile at zoom 12 is already at the data's full resolution, and the layer enlarges it beyond that. The provider's reference allows zoom up to 22 |
| licence of the data | CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), stated in the provider's dataset record https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss and on the University of Maryland's page for v1.13 |
| attribution shown, beside the box and on the map | Source: Hansen/UMD/Google/USGS/NASA. Global Forest Change v1.13, CC BY 4.0. Tiles served by Global Forest Watch (World Resources Institute) |
| terms of use | https://globalnaturewatch.org/terms/ |
| why those terms | The address https://www.globalforestwatch.org/terms/ redirects to this page, 'Terms of Service \| Global Nature Watch'. It names resourcewatch.org, globalforestwatch.org and prepdata.org among the sites it covers, 'owned and operated by the World Resources Institute'. The tile host's own reference is titled 'GFW Tile Cache API' |
| what the terms say | Use of the services is agreement to the terms. 'You may not use the Services in any manner that could damage or overburden the Services or interfere with any other party's use of the Services.' 'If You use Our APIs in Your own products, please credit Us. You agree to attribute our APIs in line with our Attribution Requirements, available at [https://resourcewatch.org/api-attribution-requirements].' 'We may cancel or suspend Your access to the Services at any time and for any reason, without notice.' No rate limit is published; the words tile, embed and hot-link do not occur |
| the attribution page the terms point to | https://resourcewatch.org/api-attribution-requirements - it speaks of 'the Resource Watch API': 'Websites that use the Resource Watch API must include the "powered by Resource Watch" logo linking to http://resourcewatch.org on pages that make use of the Resource Watch API.' and 'Graphics, charts, and maps created using the Resource Watch API must include the text and link "powered by Resource Watch" if the Resource Watch logo does not appear elsewhere on the page'. The same page says: 'This site is no longer being updated and will be archived in the coming months.' The overlay's attribution carries no such words |
| how it was verified | Two independent searches and an adversarial verifier read the provider's reference, dataset record and terms on 8 Oct 2026; tiles over central Odisha were fetched at zoom 9 and 12 (HTTP 200, image/png) with canopy settings 10 and 30 and with and without a year range, and decoded: the year range and the canopy setting each change the pixels shown, as the reference says. On the same day an adversarial review read the terms, the attribution page, the developer pages, the dataset record and the tile reference again and corrected this record; every sentence quoted here was then found in a copy of each page fetched at the time given above |

**The version.** The tiles carry Hansen/UMD Global Forest Change v1.13, the version the unit tables are built from (UMD/hansen/global_forest_change_2025_v1_13), and the
address pins it. So no warning about disagreeing versions is needed, and the overlay is labelled with its version all
the same. Two differences remain and are stated on the overlay: its canopy setting takes dense and open forest
together, where the unit tables keep them apart, and it is a picture to find places by, not something to measure from.

**Two points about the terms are unresolved, and they are the owner's to decide** (§17). Two points, both the project owner's to decide; one note to gfw@wri.org could settle both. (1) API keys. The terms read 'each request to an API must include one of Your Account's unique API keys'. The tile service's reference declares no key scheme and the service returns every tile without one. The provider's developer page counts the Tile Cache among the Data API's five core services and says 'Some endpoints require users to include an API key with their request'; the guide it links says 'To make most requests to the GFW Data API using third-party applications (e.g., scripts or websites), you need an API key.' Nothing read says whether tiles drawn in a page like this one are among them. (2) Attribution. The terms bind a user to the Attribution Requirements page, which asks for the words and link 'powered by Resource Watch' on maps made with 'the Resource Watch API'. Whether that page governs the tile service of Global Forest Watch is not said anywhere read, and the page is to be archived. The overlay credits the data's authors, its licence and the tile provider, and does not carry those words

**Where the quoted pages are.** By the owner's ruling of 9 October 2026, 5 of the provider's pages are now
registered in `00_raw/05_forest_reference/`, each with a manifest row giving its address, bytes, `sha256` and date:
the provider's record of the dataset, its terms of service, the attribution page those terms point to, the reference
of the tile service, and the University of Maryland's page for the version of the data used here. They are fetched
files and are not in git.
The registered files are byte for byte the copies read on 8 October 2026. The developer page and the guide to API
keys, which the note on the unresolved terms also quotes, were registered beside them on 10 October 2026, from the
same fetch: 2 more rows of the manifest. (The overlay's own registration, written into the layer on
9 October 2026, still says they are only with the session's working files; it is part of the layer's build and was
not rewritten.) This
script looked in 5 of the copies for 13 of the sentences the overlay's registration quotes, whole or
by their distinguishing words, and stops if one is missing. It did not look for every quotation.

**The provider's cautions about the data have a home of their own.** `00_raw/05_forest_reference/provider_cautions.json`
holds 13 sentences taken word for word from two of those pages - the provider's record of the dataset and the
University's page - and the four percentages those sentences state. It is made and checked by the script beside it,
and it is in git. The layer's About text quotes the cautions from that file and no longer from the overlay's
registration, so they stay whether or not the overlay is shipped (§18 gives them).

**A copy without the overlay, and since 10 October 2026 without the development index.** `scripts/07_build_share.py`
writes `70_share/odisha_forest_decision_layer/`: a folder with the layer's `index.html` and `data.js` and a README; no
`overlay.js`; and a zip of that folder beside it, `70_share/odisha_forest_decision_layer.zip` (6.0 MB). The
two files are the layer's with the development index of 2011 taken out and nothing else: its layer, its value in
every unit's row, its line in a unit's panel, its column of the ranked list, its row of the sources, and the places of
the About text that speak of it (11,468 units' values; the copy's `data.js` is 194,058 bytes
shorter than the layer's). The script first writes the layer's `data.js` out again untouched and stops unless that
gives back the layer's own bytes, so what was not taken out is the layer's. The README says how to open the copy,
what it is and is not, that the map overlay and the development index are not in it, whose data it draws on
(11 rows, read from the copy's own list of sources) and where the copy is published.
The page in the copy is the layer's page less the one cell of the ranked list that printed the index, so its box
"Site-level overlay" is still there. `scripts/exercise_share.py` opened the copy from disk in Chrome
(Chrome/154.0.8037.99): 8 of 8 steps did what they should. It holds the two files against
`60_layer/`'s under that rule, written out a second time in the gate; it looks for the index's id and its names on
the page in both files and finds none; the page loaded those two files and asked the network for nothing; with the
box ticked the control said "The overlay's file, overlay.js, is not beside this page. Everything else on the map works as before.", the box was unticked again and no tile was drawn; and with a district
ranked and one of its units opened, the list, the panel, the list of layers and the two text panels showed the index
nowhere, and no empty or shifted cell where it had been. The browser logged once that a file was not found, which is
the point of the copy; nothing else was logged. **Which checks of the copy changed, and why:** until 10 October 2026
the script and the gate each held the copy's two files byte for byte against `60_layer/`'s; that comparison cannot
hold once the index is out, and each now holds them against the layer's files under the rule above. `60_layer/` is
unchanged and keeps the index (§10).

**The copy is published.** On 11 October 2026 the owner decided to publish it, without a password, at
https://sudo-karan.github.io/ICTD_Project/: GitHub Pages, from the branch `gh-pages` of the public repository (commit `907d0f905b33`), which
holds the copy's three files and an empty `.nojekyll` and no other file of the repository. Until that day the copy's
README said that terms for passing it on were not yet agreed and asked that it not be published; it now gives the
address, and says that each source keeps its own licence. `scripts/check_pages_live.py` fetched the three files from
the site and opened it in Chrome (2026-10-10T20:09:31Z): 9 of 9 checks passed. The bytes the site
serves are the build's; the map draws every unit; the page logs no script error; and every request goes to the
site's own host. The browser's own request for an icon, which the site does not have, is refused, and the check
records it.

**How it behaved under test.** In Chrome, with a connection, ticking the box drew 12 tiles of
12 asked for, from the registered host and no other (one address asked for: `https://tiles.globalforestwatch.org/umd_tree_cover_loss/v1.13/dynamic/9/375/226.png?render_type=true_color&tree_cover_density_threshold=10&start_year=2018&end_year=2025`), with the
whole credit beside the box and on the map; with the browser set to no connection the page opened and worked as
before and asked the network for nothing; with the host cut off after tiles had arrived and the map moved far, the
overlay took itself off;
with a few tiles failing after others had arrived it stayed on and said that pink may be missing; zoomed in, where a
view asks for only a few tiles, it gave up as unreachable just the same; on leaving the decision view it went off. In
WebKit, with a connection, 12 of 12 tiles
were drawn. WebKit as driven here cannot be put offline or have an address blocked from outside, so those steps are
Chrome's alone (§16).

## 15. Where the window, the thresholds and the order are stated

No screenshot and no exported file should lose which window, which thresholds and which order produced it.

- **The legend**: its title names the window; a note under it gives both thresholds, says what standing forest is in
  the owner's words (§3), and states the tier order in use.
- **Every unit's panel** carries a block, "why this tier", on every unit and not behind any toggle: right under the
  unit's name in the decision view, and after the panel's own sections in every other view, so that the existing
  panels read as they did. In those other views the block is always of the default window and the provisional order,
  whatever was last set in the decision view: its controls are folded away there and the address says nothing of
  them, so the block is what the same address shows on a fresh page. It shows the six hectare figures (standing dense, lost from dense, standing open, lost from
  open, land with ten per cent canopy or less, lost on it), with the window in the table's heading; the sentence that
  puts the unit in its row, with the standing minimum; the sentence that puts it in its column, with the loss minimum;
  the forest at the start of the window and the loss as a share of it, or the words that say why no share is given;
  the grid of six cells with the unit's own outlined; the cell's place under the tier order in use, and the one line
  of reason for that place (when the user has changed the order, it says that the reason is the one given for the
  cell's provisional place); the corroboration badge with its own window; and the work-type field (§13). For an
  outside-village unit it adds the governance prompt and what the district rests on (§12).
- **The head of the ranked list** names the district, the window and the tier order, says which of the two orders
  within a tier is in use (by hectares lost, or by share lost: §5.4), and under a filter says what was left out.
- **Every row of an exported list** carries all of it. **The export has 32 columns**: `district`, `unit_id`, `unit_name`, `unit_type`, `outside_village`, `window_of_forest_loss`, `standing_forest_is_through`, `tier_label`, `tier_definition`, `tier_order_in_use`, `tier_order_is`, `order_within_a_tier`, `standing_dense_ha`, `lost_from_dense_in_window_ha`, `standing_open_ha`, `lost_from_open_in_window_ha`, `land_with_10pct_canopy_or_less_in_2000_ha`, `lost_on_that_land_in_window_ha_reported_only`, `standing_forest_ha`, `forest_loss_in_window_ha`, `forest_at_window_start_ha`, `forest_loss_share_pct`, `standing_minimum`, `loss_minimum`, `close_call_dense_or_open`, `corroboration`, `corroboration_window`, `scheduled_tribe_share`, `forest_named_expenditure_geotagged_record_ends_FY2017_18`, `district_assigned_by`, `filter_in_use`, `layer_built_utc`. By the
  owner's ruling of 9 October 2026 the development index of 2011 is not among them, and the forest at the start of the
  window and the loss as a share of it are. Where a unit has no share the cell says so in words.
- **The address** of a decision view says all of it too: the window, the district, the order of tiers where the user
  changed it, the filter, and the order within a tier where it is by share. A part left out means its default, on a page already open as on a fresh one. The
  address of an ordinary layer carries nothing of the decision view, as before.

Two exports were opened and checked field by field, each value under its own column name and the names held against
a list written out in the check, so that neither the window nor the order in the file could be a constant and no name
could drift from its value. The first: Rayagada, window 2018-2025, under an order the user had changed
("1 Closed forest, loss recorded - find the cause first; 2 Open forest, loss recorded - restore; 3 Closed forest, little or no loss recorded - protect; 4 Little forest left, loss recorded - verify on the ground; 5 Open forest, little or no loss recorded - assisted natural regeneration candidate; not ranked: Not a forest site") and a filter ("Scheduled Tribe share 18 % or more; outside-village units left out"): 201 rows, as the tables give, and all 6,432 cells equal
to the tables. The
second: Ganjam, window 2017-2023, the provisional order, "No filter", ordered by share within a tier:
455 rows and all 14,560 cells equal. Each row said which order of tiers had made it and what ordered the
units within a tier; the first list was ordered by hectares lost and the second by share. 1 row of the
first list had no share and said so in words. An empty list is not offered as a file: with no row
to carry the window, the export button is off.

## 16. How it was verified: which check was applied where

**This build applies the owner's rulings of 9 October 2026, and it was verified lightly, on purpose.** No unit changes
cell, so, as he instructed, no independent replication was made, no adversarial review, and no run in the Safari
application. What follows says which check was applied to what.

**That no unit changed cell.**

- *The gate on the renaming*, `scripts/05_check_rename.py`, run 2026-10-09T04:08:58Z: 45,872 assignments - every unit, every
  window - taken through the owner's list of names, and every one matches; the 51 columns the table had are
  equal as text in every row (584,868 cells); the two thresholds, the order of tiers and the default window are
  what they were (§7). It stops on one mismatch.

**The decision table, `55_decision/condition_by_unit.csv`.**

- *Stop conditions in the build.* `scripts/05_build_decision.py` writes its tables into a holding folder, reads them
  back as text, and moves them into place only if every check holds: each unit once; every hectare column as written
  equal to the figure computed; the reconciliation of §3 made on the file itself, for each unit and in total; its
  yearly sums against stage 1's own totals; its repeatability figures against the existing table's; its
  corroboration counts against the agreement record's own; its district-check counts against the district record's
  own; and, added with the rulings, every share and its blank as written, no share above a hundred, and the forest at
  the start of a window less the loss of the window equal to standing forest where the window runs to the last year.
  Its run record lists what passed.
- *The independent replication of 8 October 2026 still covers what it covered, and no more.* Two agents, each given
  the script's docstring and nothing else of it, rebuilt the table as it stood then, for all four windows, by
  different means (pandas, with every hectare held as a whole number of ten-thousandths; the Python standard library alone, with decimal arithmetic). Each table was hashed before it was compared. Over 46 of that table's
  51 columns and 527,528 cells each, **no cell differs in value**; 0 differ in how a value is
  written. Neither replicator wrote the five columns that the docstring they were given described without naming (the standing row, and the loss column of each window); each of those repeats what the unit's cell already says, and in no unit and no window does it differ from what the cell implies. The two replicators' files are the same byte for byte. The docstring has since been given a list of the table's columns; the table's bytes did not change. The replicators reported 29 places where the docstring left them a choice; none changed a
  value. The gate above holds that each of those 51 columns is, cell for cell, in today's table of
  67 columns. **The 16 columns added on 9 October 2026 were not replicated**: the forest at the
  start of each window, the share, the reason for a blank share and the order by share. They are rebuilt by the
  verifier below, once. The record of the replication is a working file of the session, not a stage output (§20).
- *`scripts/verify_decision.py`*, which shares no code with the builders: "62 of 62 checks passed". It re-adds every hectare
  from stage 1's yearly columns, re-derives every cell from the printed hectares, every unit's district from
  `10_units/`, the order of every list from those, and every count and share of the layer's About text with its
  statements of the thresholds, the windows and the tier order; it holds the tier order and the six names against the
  owner's specification written out in it, and the rows the cells cite against the registered list. Extended with the
  rulings: it rebuilds the forest at the start of each window and the share for every unit and window from the yearly
  columns, the blanks with their reason and their count, and the order by share in the table and on the page; it
  holds the five new names as he gave them and that none of the old names, and nowhere the words "lower bound", is
  left in the page or its data; and it holds the export's columns, one for one with the expressions that fill them.

**How the checks were run.** By `scripts/run_decision_checks.py`, one after another and never two at once, on the
build described here; it writes down every run it makes, a failed one included (`60_layer/decision_runs.json`). In
this pass it ran 6 checks, and 5 passed on their first run. The runs of each browser check are
given with it below.

**The pass on record was started 2026-10-10T22:41:56Z (UTC), and it is of the verifier as it now is.** In it
`scripts/verify_decision.py` gave "62 of 62 checks passed", which is what the run this script made of the verifier as it wrote
the document gave: "62 of 62 checks passed". The check added on 10 October 2026 (§17.3) is therefore in the pass. An earlier
pass, started 2026-10-10T11:29:27Z (UTC) for the same purpose, could not be finished: 5 of its 6
checks passed, the verifier with its new check among them, and the check of the decision view in WebKit did not run
to its end. The machine had gone into standby on a flat battery during that pass, and afterwards the off-screen
WebKit view stopped answering; the run was stopped by hand, and the runner wrote down "RuntimeError: the WebKit driver ended". That record
is kept with the session's working files. The pass on record was made on mains power with the machine kept awake,
on the same build of the layer, and in it the check of the decision view in WebKit ran to its end and passed.

**The regression gate: the existing views.**

- `scripts/verify_layer.py`, unchanged: "92 of 92 checks passed" (with the one remark of §14 on what its sentence about the page's
  own script can and cannot see).
- `scripts/exercise_layer.py`, unchanged, in Chrome (Chrome/154.0.8037.99): 53 of 53 actions did what they
  should; 29 units clicked on the map; 1,276 of 1,276 displayed values equal the stage tables.
  Runs made of it on this build: 1; runs that passed: 1.
- `scripts/exercise_layer.py`, unchanged, in WebKit (WebKit 21624.5.1.11.3 (the engine of Safari 27.0 on this machine)): 53 of 53 actions; 29
  units; 1,276 of 1,276 values. Runs made of it on this build: 2; runs that passed every step:
  1; steps that failed in any run: [map] dragged the map 180 px left and 120 px up (mouse-down, eight mouse-moves and mouse-up, made in script).
- **`scripts/exercise_layer_safari.py`, unchanged, in the Safari application: NOT RUN on this build.** The runner's
  record names it as left out and gives the reason: "the owner's handoff of 11 October 2026: Chrome and WebKit only; the Safari application is not to be started". Its last record, still in `60_layer/`, is of the run
  of 2026-10-08T22:53:16Z on the layer built 2026-10-08T22:42:59Z, the build the owner ruled on: 48 addresses showed what they
  should and 1,265 values of the units' panels were in the page's text. So **the Safari third of the regression
  gate is not shown for the build described here.** What can be said without it: that script reads the existing
  views only; they are drawn by lines of the page that this batch did not touch (the table below) from stage tables
  that did not change; and the same views passed the unchanged exercise in Chrome and in WebKit on this build. That
  is an argument and not a run.
- *The same holds for `scripts/exercise_decision_safari.py`*, which ran the main routine of that unchanged script in
  the Safari application (Safari 27.0 (the application)) with one function replaced, the one that reads the window (title, address and text were each asked for through the address filter (first document whose URL starts with the marked address), never through the by-title reference Safari returns; a reading made before the window exists counts as 'nothing yet'): its last
  record is of the layer built 2026-10-08T22:42:59Z, where 48 of 48 addresses showed what they should and
  1,265 of 1,265 values of 29 units' panels were in the page's text. Not run on this build.
- **That nothing existing changed in code or data** was also checked directly. This script compared the record of the
  layer built 2026-10-07T12:05:18Z, kept with the session's working files, with today's: all 23 inputs that layer
  was built from go into today's layer with the same hash, beside 13 new inputs. It asked git what changed
  since the commit before the decision view (`44890a1`): four files of code and data that existed then have lines
  added and none removed.

| file that existed before | lines added | lines removed |
|---|---|---|
| `.gitignore` | 30 | 0 |
| `00_raw/data_manifest.csv` | 16 | 0 |
| `scripts/06_build_layer.py` | 16 | 0 |
| `scripts/layer_template.html` | 311 | 0 |

  *The lines added to `.gitignore` keep fetched files and stage outputs out of git; those added to the manifest are
  the rows of §13 and §14.* The only other files that existed then and are modified are documents the owner ordered
  brought up to date on 9 October 2026: `CLAUDE.md`, `README.md`, `docs/DATA_NOTES.md`, `docs/LAYER.md`, `docs/RESULTS.md`; and the script that writes one of them. **`scripts/write_results.py`
  was changed, by the owner's choice of 9 October 2026, in one rule**: it refused to write `docs/RESULTS.md` unless
  the record of the check in the Safari application was of the layer on disk; it now allows that record to be of an
  earlier build when the runner's record of this build names the check as left out with a reason, and then says so in
  the text. Its rule for the Chrome and WebKit records is unchanged. Since then the fourth stage has changed the same script again (on 10 October 2026 and on 11 October 2026): it reports that stage's headline rows in a section of its own, and runs each verifier with the interpreter of its stage. With both changes the script has 140 lines added and 20 removed since that commit. The unchanged check scripts
  that were run are as committed (the runner's record says so of each); and the decision view's build wrote no file
  of `10_units/` to `40_allocation/`. `50_gap/` is the fourth stage's and was built after it (`docs/GAP.md`).
- **What did change for an existing view**, and the owner accepted (§17): a heading and one line, the decision view's
  switch, stand above the list of layers; and every unit's panel ends with the block "why this tier". The decision
  view's other controls stay folded away, its radio button is a group of its own so that the keyboard moves through
  the existing layers as before, and an existing view's address is what it was.

**The new view.**

- `scripts/exercise_decision.py` in Chrome: 53 of 53 steps did what they should (6
  of them are statements of what was not done, readings of the page's script errors or the summary of the clicks on
  the map, the rest actions on the new controls: the view's switch, the four windows, the district, the order within
  a tier, 3 of the 8 tier arrows and the way back, the filter and its box, a row of the
  list, two exports, the legend, the address, two window sizes, leaving and returning, the overlay). 46 units
  opened by a click on the map, 18 LGD panchayat and 28 outside-village units, the latter in
  16 districts, covering all six cells in 2 windows and all 11 kinds of
  corroboration badge; 874 of 874 comparisons of the block "why this tier" with the tables held
  (nineteen a unit: lines that must be there, the share among them, lines that must not, and the block's place in the
  panel). A click that opens nothing, or a unit that does not touch the one aimed at, fails the run: there was none.
  0 clicks opened a touching neighbour. The page's script errors were read at the end of every part and
  before every reload: none. Runs made of it on this build: 1; runs that passed: 1.
- The same in WebKit: 47 of 47 steps, 46 units, 874 of 874 comparisons.
  There events are made inside the page, the exported text is read from the page and not from a saved file, and the
  browser cannot be put offline or have an address blocked. Runs made of it on this build: 1; runs that
  passed: 1.
- The exports, field by field: §15. The overlay, online in both and offline in Chrome: §14.
- In the Safari application, by address and with nothing clicked: **not run on this build** (the same reason). On
  the build the owner ruled on, 59 of 59 addresses of the decision view showed what they should, and
  657 of 657 lines of "why this tier" for 46 units were in the page's text in order. That
  build's block had one line fewer: the share was added since, and has been read in Chrome and WebKit only.

**The copy made to be passed on.** `scripts/exercise_share.py`, run 2026-10-10T22:16:08Z, opened the copy in
`70_share/odisha_forest_decision_layer/` from disk in Chrome: 8 of 8 steps did what they
should (§14).

**The fragility of the Safari and WebKit checks: recorded, and by the owner's ruling not chased.** On the layer built
2026-10-08T13:02:50Z, 3 runs of the unchanged WebKit exercise were made and in 1, the first, one step
failed: a drag of the map made in script, which did not move the map. No cause was established. One candidate, not
tested: the step before the drag is a zoom by the mouse wheel, and the map library ignores a mouse-down while it
still marks a zoom as under way; the unchanged script waits a fixed time. Of the unchanged Safari script on that
day: it stopped at its first reading, twice, before any assertion: Safari held another window of the same page, and had just been started in the background. On the layer built 2026-10-08T20:41:54Z, 3 runs of it were made and 1 passed; the note
added by hand to that pass's record: *This is the record the runner wrote on 9 October 2026, as it was written, with this one note added. In it the unchanged Safari script was run three times. The first run, with Safari not yet running, stopped at its first reading and left its window open. The second run read that left-over window instead of its own, as Safari hands a window back by its title, and failed most of its addresses. While the second run was still going, the left-over window - the one whose address carried the first run's own mark - was closed by hand; no other window was touched. The third run then passed as written. The runner was changed after this pass to close such left-over windows of its own checks itself, before each Safari run, and to record how many it closed.* On the layer the owner ruled on, built 2026-10-08T22:42:59Z, all
8 checks were run and 8 passed on their first run. And what happened to the owner's Safari
windows on 8 October 2026, from the session's note of that day: *During the Safari runs of 8 October the Safari that the check had started in the background received a request to quit (the system log has it at 16:19:50 IST, as 'Handling Quit AppleEvent'); the scripts send no such request, and what sent it was not established - seven other jobs were running and the machine was heavily loaded. When Safari was started again, the three windows it had restored from the owner's last session - two Start Pages and the layer at #layer=forest_named_expenditure&floor=50&unit=132164 - were no longer open. They were not recreated. The scripts close only the window they mark with their own address, which was tested on two windows of one title.*

**What three adversarial reviews changed, on 8 October 2026.** Reviewers set against the first version found things
that its own checks had passed: a count of "slivers" that were mostly whole pixels; a sentence shown for every
district that was true of the state and false of many districts; evidence on repeatability measured on the wrong
land; a browser check that compared a stale panel twice and called it a neighbour; an overlay that stayed "on" after
its tiles stopped arriving; and a clause of the provider's terms that had been left out. No cell, hectare or tier was
wrong. A second review, of those corrections, found two new sentences that repeated the fault and several new checks
weaker than their names. A third found one more false sentence in the layer - a badge that had dropped the words
"with canopy above ten per cent" - and again checks weaker than their names: the list's check, the gate on tiles
drawn, the verifier's checks of the view's lists and of the page's handlers. Each was corrected. What that history
shows is that sentences in words are where this work has gone wrong, more than figures, and that each round of
checking found the round before it too generous to itself. **No review was made of this build**, by the owner's
instruction: it changes labels, adds two figures beside the cell and an order within a tier, and moves no unit. The
conclusions this text draws from figures are tested when it is written and listed in §20.4; a sentence that is not
such a conclusion is tested by nothing, and a reader should hold the prose to the tables.

**What was not done.** No run was made in the Safari application on this build, and no control was ever clicked
there. The layer has not been opened in Firefox (not installed on this machine), on a phone, in print, or on a
machine with little memory. The district's list, the filter's list and the list of the order within a tier were set
through their change events in both engines, because a native pop-up cannot be clicked in a window that is not on a
screen. Two behaviours of the overlay were read in the page's code and not exercised in a browser: that nothing is
drawn if its file arrives after the box has been unticked or the view left, and that the warning of a failed tile
stays until the overlay is drawn again. 3 of the 8 tier arrows were pressed. The digits of
the Gazette's serial numbers were read by eye. The two columns of the share were rebuilt independently once, not
twice. Nobody who knows these places has yet looked at a single tier.

## 17. The owner's rulings of 9 October 2026, and what is still open

On 9 October 2026 the owner read the list of decisions this section then held and ruled on it. It is split in two as
he asked.

### 17.1 Ruled on 9 October 2026

**Accepted as proposed.**

- **The standing minimum, 10 ha** (§5.2). The alternatives would move 990 and 1,207 units.
- **The loss minimum, 1 ha, as the rule of the cells** (§5.1). The alternatives would move 308 and
  282 units.
- **The default window, 2018–2025, with its three caveats** (§4).
- **The narrower wording of the reason for ranking only within a district**, which is the one the layer uses (§9):
  it holds for LGD panchayat units at the headline, not for all units, at every floor, with the East Coast units
  kept, or of any one district.
- **The rounding tolerance** (§3): standing set to zero in 3 units for dense and 1 for
  open, where the source's rounding put it a square metre below; and "lost" taken as the sum of the years, which is
  not the source's own total to the last digit in 1,765 units for dense and 1,478 for open.
- **The additions to the existing views** (§16): a heading and one line above the list of layers, and a block at the
  end of every unit's panel.
- **Hyphen for dash** in the cells' names (§7).
- **The weaker form of "every lost pixel is bare by construction"** (§2), which is the form the source bears out.
- **The margin of the "close call" flag, a fifth** (§6).
- **The fragility of the Safari and WebKit checks**: to be recorded, and not chased (§16 records it).

**Changed by the rulings, and done in this build.**

- **Five cells renamed, labels only** (§7), because with a flat minimum of 1 ha the first names over-claimed:
  349 units of the cell then called "under pressure" lost under one per cent of the forest they had at the
  start of the window, and
  157 units of the cell then called "intact" are flagged by CoRE Stack. No unit changed cell: 45,872
  assignments held by the gate.
- **Loss as a share, beside the cell and not in it** (§5.4), with a second order within a tier, by share lost.
  Blank, with the reason in words, where the forest at the start of the window is under the standing minimum:
  5,660 units in the default window.
- **"Lower bound" taken out** (§3) of the layer, the tables' record and this document, and replaced by the owner's
  words; the reason is kept in §3 and §18.
- **The export** (§15, §10): the development index of 2011 removed from it and kept in the interactive view (of
  `60_layer/`; the copy that is passed on lost it too on 10 October 2026, §17.3); the forest at the start of the
  window and the share added; 32 columns.
- **The provider's cautions given a home of their own** (§14): 5 of the provider's pages registered in
  `00_raw/` with manifest rows, and the cautions quoted in the layer's About text from the dataset record whether or
  not the overlay is shipped.
- **A copy of the layer without the overlay**, `70_share/odisha_forest_decision_layer/`, with a README, and a zip
  of it beside it (§14).
- **The standing rule on `00_raw/`**, reworded in `CLAUDE.md` as he gave it: files in `00_raw/` at a commit are never
  edited; registering a new input adds files and manifest rows. Under it the files this stage put into `00_raw/` on
  8 October 2026, which were rewritten in place before they were committed, were not touched again: this build added
  files and manifest rows there and changed nothing that was committed.
- **The documents** brought up to date as he listed them (§18 says which were). To regenerate `docs/RESULTS.md` with
  no run in the Safari application he chose, the same day, to change one rule of `scripts/write_results.py`: Chrome
  and WebKit on the build on disk are enough, and the text says that Safari was not opened on it (§16).

### 17.2 Still open, for the Foundation for Ecological Security

- **The order of tiers** (§8). Provisional; in particular whether closed forest with loss recorded goes above open
  forest with loss recorded. It is a control in the layer, and an exported list says which order made it.
- **Which rows of the list of permissible works bear on which cell** (§13), and the forest-named rows cited by none,
  above all the last row of the list.
- **Whether Scheduled Tribe share appears in a list they pass on** (§10).

Until these are settled a tier is a starting point for a conversation with the Foundation and not a recommendation.
One thing is open that is not the Foundation's and that the owner knows of: the two points of the tile provider's
terms (§14), which is why the copy made to be passed on has no overlay. The terms on which that copy is passed on
were open until 11 October 2026, when the owner decided to publish it (§14); its README says so.

### 17.3 Changed on 10 October 2026, with the instruction that opened stage 4

These were not rulings on a list put to the owner. They came with his instruction of 10 October 2026 for the next
stage, and the first is recorded here as a call of that instruction that he can reverse.

- **The development index of 2011 is left out of the copy that is passed on** (§10, §14). The exported list lost the
  index on 9 October 2026 because that file is passed on; the copy in `70_share/odisha_forest_decision_layer/` is
  passed on too, and its `data.js` still carried `adi_2011` for every unit. The script that builds the copy now takes
  the field out, with everything that displays it; the gate on the copy looks for the index's id and names in the
  copy's two files and fails if it finds one; the copy's README says the index is not in it. `60_layer/` keeps the
  index. **Reversible:** the change is confined to `scripts/07_build_share.py` and its gate,
  `scripts/exercise_share.py`; no stage table, no cell and nothing in `60_layer/` was touched. Putting those two
  scripts back as they stood on 9 October 2026 and running them gives back the copy of that day; this document's own
  check of the copy (§14) would go back with them.
- **The three counts of §5.1 are on the share the panel prints** (§5.1, §5.4, §7): its denominator is the forest at
  the start of the window, not standing forest. `scripts/verify_decision.py` works the three out from stage 1's
  yearly columns, holds them against the table's column, and this script holds its own count against the verifier's.
- **Two more of the provider's pages are registered** (§14): its developer page and its guide to API keys.

## 18. What this does not show

- **It is Hansen's record, read one way.** Standing forest is the forest of 2000 with no loss recorded since; not a measure of tree cover today: it ignores gain, and it inherits
  whatever recorded loss misses or wrongly includes (§3). Loss is the removal of cover; thinning under a canopy is
  invisible to it, and the split into dense and open is that of the year 2000. Tree
  cover is any vegetation taller than five metres: a plantation counts as a natural forest does. The only second
  opinion is the corroboration badge, for the units it covers and for 2017–2023.
- **The provider of the data cautions against part of what is done here.** From Global Forest Watch's record of the
  dataset, registered in `00_raw/` (§14), word for word: "Tree cover loss is defined as “stand replacement disturbance” which is considered to be clearing of at least half of tree cover within a 30-meter pixel." "“Loss” indicates the removal or mortality of tree cover and can be due to a variety of factors, including mechanical harvesting, fire, disease, or storm damage. As such, “loss” does not equate to deforestation." "Accordingly, “net” loss cannot be calculated by subtracting figures for tree cover gain from tree cover loss, and current (post-2000) tree cover cannot be determined by subtracting figures for annual tree cover loss from year 2000 tree cover."
  "Comparisons between the original 2001-2010 data and the 2011-2025 update should be performed with caution." "In the original publication, the authors evaluated the overall prevalence of false positives (commission errors) in this data at 13%, and the prevalence of false negatives (omission errors) at 12%, though the accuracy varies by biome and thus may be higher or lower in any particular location." "Largely because of a delay between an actual disturbance and the event being observed by the satellite imagery, the authors are 75% confident that the loss occurred within the stated year, and 97% confident that it occurred within a year before or after." The University of Maryland, whose data it is, defines loss so:
  "Forest loss during the period 2000-2025, defined as a stand-replacement disturbance, or a change from a forest to non-forest state." The decision view's "standing" is exactly the subtraction the record cautions against. It is offered
  as the forest of 2000 with no loss recorded since, and as nothing more: not as tree cover today, and - since the
  owner's ruling of 9 October 2026 - not as a lower bound on it either, because with loss missed at about 12 per
  cent and loss falsely recorded at about 13 per cent it can err in either direction. The two halves of the full
  record were made by different methods, which bears on the window 2001–2025; and a loss can be a year off, which
  bears on the edges of every window.
- **Recorded loss on open forest has risen steeply, and these tables cannot say why.** On the open band it goes
  23, 114, 226 km² across 2001–2010, 2011–2017 and 2018–2025, against 435, 444,
  674 on the dense band. `docs/RESULTS.md` §3.1 calls the like rise on the lowest band largely the producers'
  change of method. Whether the open band's rise is on the ground or in the method is not established here, and every
  cell with loss counts it.
- **A cell's name says where the forest stands, not where the loss was.** The row is set by standing forest and the
  column by loss from the dense and open bands together (§5). In 102 of the 406 units of
  "Open forest, loss recorded - restore" more was lost from the dense band than from the open, and in 207 of the 1,295 units
  of "Closed forest, loss recorded - find the cause first" more from the open than from the dense. The panel and the export show the two apart.
- **A cell is a summary of hectares in a unit.** It says nothing about where in the unit, why, or by whom. A unit in
  the first tier is a place to look, not a finding about a village. And because the loss minimum is a number of
  hectares, a cell with loss says more about the size of a large unit than about its rate of loss (§5.1).
- **Every limit of the measurements carries over** (`docs/RESULTS.md` §12): the unit is a geometry and not a
  jurisdiction; the canopy bands are fixed at the year 2000; the agreement between the two measures is modest and
  depends on choices; the geotagged record of works ends in FY2017-18; the census is that of 2011.
- **The order of tiers and the mapping to works are still open** (§17). Until the Foundation has set them, a tier is a
  starting point for a conversation and not a recommendation.
- **The other documents.** By the owner's instruction of 9 October 2026 these were brought up to date with the
  decision view, and are modified since the commit before it: `CLAUDE.md`, `README.md`, `docs/DATA_NOTES.md`, `docs/LAYER.md`, `docs/RESULTS.md`. A document of that instruction that is
  not in this list was not changed and still describes the state before the decision view; §16 says which checks its
  own script asks for. The layer's two files are now 22.5 MB together (6.0 MB zipped, against the
  25.0 MB it is held under), and beside them is a third file of 1,213 bytes, the overlay's. One
  sentence of the existing About text, that Hansen "cannot see change on land that was already open in 2000", is
  about change short of clearance; the decision view counts Hansen's clearance on that land.

## 19. To rebuild

```
.venv/bin/python scripts/05_build_decision.py
.venv/bin/python scripts/05_check_rename.py                      # the gate on the renaming: every unit's cell, against the table as ruled on
.venv/bin/python scripts/06_build_layer.py --units 10_units/units.gpkg
.venv/bin/python scripts/run_decision_checks.py                  # both verifiers, then the browser checks, one at a time
.venv/bin/python scripts/07_build_share.py                       # the copy without the overlay, and its zip
.venv/bin/python scripts/exercise_share.py                       # the copy opened from disk in Chrome
.venv/bin/python scripts/write_decision_layer.py
```

The two scripts inside `00_raw/` - the one that checks the list of permissible works and the one that extracts the
provider's cautions - are not in this list: their outputs are registered, and a file in `00_raw/` at a commit is not
written again. `scripts/run_decision_checks.py` runs each check in turn and writes `60_layer/decision_runs.json`,
the record of every run it made, a failed one included; with `--leave-out safari --because "..."` it leaves the two
checks in the Safari application out and writes the reason into the record. This document is written from that
record and stops unless it is of the build in `60_layer/`. The overlay's steps need a connection; the Safari steps
need the terminal's leave to control Safari and no other Safari window showing the layer.

Some things this document reads are working files of the session and are rebuilt by no script: the record of the
independent replication, the decision tables and the layer's records as they stood when the owner ruled on them, the
record of the trials of the list's check, the copies of the provider's pages, the record of the layer built on
7 October 2026, the note of the runs of 8 October 2026 and the record of a pass of the runner with a step made by hand
(§20). It stops if one is missing. The gate on the renaming needs the table as it was ruled on, and stops unless that
copy has the hash written in the gate's script.

Run the browser checks one at a time, on a machine that is otherwise quiet.

## 20. Where every figure comes from

This section is the script's own record of what it read. Paths are relative to the repository. The numbered folders (`10_units/` to `60_layer/`) are stage outputs: each is rebuilt by the script named in the `.provenance.json` beside it, except that the records of the checks in `60_layer/` are written by the checks themselves; none is in git. Files under `.session_scratch_2026-10-05/` are **working files** of the session that made this stage. They are not stage outputs and no tracked script rebuilds them; the independent replication of the decision table (§16) has no other record.

### 20.1 Figures in the text, in the order they first appear

| as printed | file | where in the file |
|---|---|---|
| 2026-10-10T23:09:20Z | this run | the UTC time at which this script ran |
| 2026-10-09T03:37:07Z | `55_decision/decision.provenance.json` | key `run_utc` |
| 2026-10-09T04:08:22Z | `60_layer/layer.provenance.json` | key `run_utc` |
| 10 | `55_decision/decision.provenance.json` | key `tables`: the number of tables it lists |
| 11,468 | `55_decision/decision.provenance.json` | key `counts` → `units` |
| 7,976 | `55_decision/decision.provenance.json` | key `counts` → `by_level` → `lgd_panchayat` |
| 3,492 | `55_decision/decision.provenance.json` | key `counts` → `by_level` → `outside_village` |
| 10 | `55_decision/decision.provenance.json` | key `thresholds` → `standing_min_ha` |
| 1 | `55_decision/decision.provenance.json` | key `thresholds` → `loss_min_ha` |
| 100 | `60_layer/layer.provenance.json` | key `default_floor_ha` |
| 92 of 92 checks passed | `scripts/verify_layer.py` | its exit status and last line, run by this script as it wrote the document |
| 62 of 62 checks passed | `scripts/verify_decision.py` | its exit status and last line, run by this script as it wrote the document |
| 67 | `55_decision/decision.provenance.json` | key `tables` → `condition_by_unit.csv` → `columns` |
| UMD/hansen/global_forest_change_2025_v1_13 | `20_degradation/hansen.provenance.json` | key `inputs`: the Earth Engine dataset it names |
| the forest of 2000 with no loss recorded since; not a measure of tree cover today | `55_decision/decision.provenance.json` | key `definitions` → `standing`: its closing words |
| Accordingly, “net” loss cannot be calculated by subtracting figures for tree cover gain from tree cover loss, and current (post-2000) tree cover cannot be de... | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `cover_today_is_not_cover_of_2000_less_loss` → `text` |
| In the original publication, the authors evaluated the overall prevalence of false positives (commission errors) in this data at 13%, and the prevalence of f... | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `errors` → `text` |
| 12 | `00_raw/05_forest_reference/provider_cautions.json` | key `percentages_read_from_the_sentences` → `false_negatives_pct` |
| 13 | `00_raw/05_forest_reference/provider_cautions.json` | key `percentages_read_from_the_sentences` → `false_positives_pct` |
| 917 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 826 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'eq0' |
| 90 | `20_degradation/hansen_loss_by_canopy_band.csv` | computed here: loss on land with no canopy in 2000 ÷ loss on land with `treecover2000 <= 10` × 100. From: column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'eq0'; column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 45 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2010`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 245 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2011_2017`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 627 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2018_2025`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 435 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2010`; row where `units` is 'all units' and `canopy_band` is 'gt30' |
| 444 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2011_2017`; row where `units` is 'all units' and `canopy_band` is 'gt30' |
| 674 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2018_2025`; row where `units` is 'all units' and `canopy_band` is 'gt30' |
| 62,748 | `55_decision/condition_cells.csv` | worked out by this script from its rows: `loss_low_ha_in_window_reported_only` summed over the six cells, all units, window 2018_2025 |
| 90,028 | `55_decision/condition_cells.csv` | worked out by this script from its rows: `forest_loss_ha_in_window` summed over the six cells, all units, window 2018_2025 |
| 27 | `55_decision/decision.provenance.json` | key `checks_passed` → `totals_against_hansen_loss_by_canopy_band`: the number of totals compared |
| 11,465 | `55_decision/decision.provenance.json` | key `checks_passed` → `standing_plus_all_loss_against_the_band_hectares_per_unit` → `dense` → `units_exact` |
| 11,467 | `55_decision/decision.provenance.json` | key `checks_passed` → `standing_plus_all_loss_against_the_band_hectares_per_unit` → `open` → `units_exact` |
| 3 | `55_decision/decision.provenance.json` | key `checks_passed` → `standing_plus_all_loss_against_the_band_hectares_per_unit` → `dense` → `units_not_exact` |
| 1 | `55_decision/decision.provenance.json` | key `checks_passed` → `standing_plus_all_loss_against_the_band_hectares_per_unit` → `open` → `units_not_exact` |
| 0.0001 | `55_decision/decision.provenance.json` | key `checks_passed` → `standing_plus_all_loss_against_the_band_hectares_per_unit` → `dense` → `largest_gap_ha` |
| 1,765 | `20_degradation/hansen_loss_by_canopy_band_by_unit.csv` | rows counted by this script: rows whose yearly losses on the dense band (`loss_ha_gt30_<year>`) do not add to the table's own total `loss_ha_gt30`, at four decimals |
| 1,478 | `20_degradation/hansen_loss_by_canopy_band_by_unit.csv` | rows counted by this script: rows whose yearly losses on the open band (`loss_ha_gt10le30_<year>`) do not add to the table's own total `loss_ha_gt10le30`, at four decimals |
| 0.0005 | `55_decision/decision.provenance.json` | key `checks_passed` → `yearly_losses_against_the_tables_own_totals_largest_gap_ha` |
| 630 | `55_decision/decision.provenance.json` | key `checks_passed` → `the_printing_rule_against_half_up_on_the_decimal_figure` → `hectare_cells_that_would_print_differently` |
| 2 | `55_decision/decision.provenance.json` | key `checks_passed` → `read_at_four_decimals_and_not_as_printed` → `units_mostly_dense_whose_standing_open_is_larger_in_the_fourth_decimal` |
| 6 | `55_decision/decision.provenance.json` | key `checks_passed` → `read_at_four_decimals_and_not_as_printed` → `unit_windows_with_some_loss_and_under_the_threshold_in_the_fourth_decimal` |
| 1 | `55_decision/decision.provenance.json` | key `checks_passed` → `printed_parts_add_to_a_threshold_the_printed_total_is_under` → `units_standing` |
| 2 | `55_decision/decision.provenance.json` | key `checks_passed` → `printed_parts_add_to_a_threshold_the_printed_total_is_under` → `unit_windows_loss` |
| 168 | `55_decision/decision.provenance.json` | key `tables` → `condition_by_unit.csv` → `blank_cells` → `unit_name` |
| 708 | `55_decision/decision.provenance.json` | key `tables` → `condition_by_unit.csv` → `blank_cells` → `dense_open_ratio` |
| 24.2 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_plantation_share_pct`; row where `fy` is '2016-17' |
| 3.3 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_plantation_share_pct`; row where `fy` is '2018-19' |
| 10/10/2020 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_last_updated`; row where `fy` is '2016-17' |
| 800 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2001_2025` is open_loss |
| Open forest, loss recorded - restore | `55_decision/tiers.csv` | column `cell_name`; row where `cell` is 'open_loss' |
| 394 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2001_2025` is open_loss and whose `forest_loss_ha_2018_2025`, as printed, is under the loss minimum |
| 0.0725 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'pixel_ha' |
| 147 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'under_mid_pixel_2018_2025' |
| 13.8 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'pixels_in_loss_1' |
| 1 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'fsi_min_patch_ha' |
| 87.7 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'recur_10_1' |
| 1,171 | `55_decision/condition_threshold_evidence.csv` | column `n`; row where `key` is 'recur_10_1' |
| 5.2 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'fresh_10' |
| 4,028 | `55_decision/condition_threshold_evidence.csv` | column `n`; row where `key` is 'fresh_10' |
| 5,796 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'units_standing_10' |
| 5 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'some_loss_share_10' |
| 85 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'some_loss_share_5000' |
| 101 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `standing_forest_ha`, as printed, is five thousand or more and whose `cell_2018_2025` is a cell with loss |
| 119 | `55_decision/condition_threshold_evidence.csv` | column `n`; row where `key` is 'some_loss_share_5000' |
| 22 | `55_decision/condition_by_unit.csv` | districts whose row with the largest `standing_forest_ha` has a `cell_2018_2025` with loss |
| 30 | `55_decision/condition_cells_by_district.csv` | column `district`: the number of distinct districts |
| 349 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_loss and whose `forest_loss_share_pct_2018_2025` is under 1 |
| Closed forest, loss recorded - find the cause first | `55_decision/tiers.csv` | column `cell_name`; row where `cell` is 'dense_loss' |
| 48 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_loss and whose `forest_loss_share_pct_2018_2025` is under 0.1 |
| kuchilaghati (132731), Mayurbhanj | `55_decision/condition_by_unit.csv` | the row with the largest `standing_forest_ha` among those whose `cell_2018_2025` is dense_loss: its name, id and district |
| 55,114 | `55_decision/condition_by_unit.csv` | `standing_forest_ha` of that row |
| 35.77 | `55_decision/condition_by_unit.csv` | `forest_loss_ha_2018_2025` of that row |
| 74 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_none or open_none and whose `forest_loss_share_pct_2018_2025` is over 2 |
| 50 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'recur_size_10' |
| 32 | `55_decision/condition_threshold_evidence.csv` | column `n`; row where `key` is 'recur_size_10' |
| 99.63 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is 'share_standing_10' |
| 0.48 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is the rank correlation of the class that starts at the lower alternative |
| 5 | `55_decision/decision.provenance.json` | key `thresholds` → `alternatives` → `standing_min_ha` → `0` |
| 0.60 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is the rank correlation of the class that starts at the proposed standing minimum |
| 0.70 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is the rank correlation of the class that starts at the higher alternative |
| 25 | `55_decision/decision.provenance.json` | key `thresholds` → `alternatives` → `standing_min_ha` → `1` |
| 80 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is the share with no loss in the class that starts at the lower alternative |
| 69 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is the share with no loss in the class that starts at the proposed standing minimum |
| 53 | `55_decision/condition_threshold_evidence.csv` | column `value`; row where `key` is the share with no loss in the class that starts at the higher alternative |
| 1,207 | `55_decision/condition_threshold_evidence.csv` | computed here: units with at least the proposed standing minimum less units with at least the higher alternative. From: column `value`; row where `key` is 'units_standing_10'; column `value`; row where `key` is 'units_standing_25' |
| 0.55 | `55_decision/condition_threshold_evidence.csv` | computed here: share of standing forest in units with at least the proposed standing minimum less the share in units with at least the higher alternative. From: column `value`; row where `key` is 'share_standing_10'; column `value`; row where `key` is 'share_standing_25' |
| 173 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose three bands of land in the year 2000 add to less than the standing minimum |
| 37 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is the cell outside the ranked list and whose standing forest is half or more of their land |
| Not a forest site | `55_decision/tiers.csv` | column `cell_name`; row where `cell` is 'little_none' |
| 0.5 | `55_decision/decision.provenance.json` | key `thresholds` → `alternatives` → `loss_min_ha` → `0` |
| 2 | `55_decision/decision.provenance.json` | key `thresholds` → `alternatives` → `loss_min_ha` → `1` |
| 990 | `55_decision/condition_sensitivity.csv` | column `units_whose_cell_differs_from_the_default_all_cells`; row where `standing_min_ha` is 5.0 and `loss_min_ha` is 1.0 and `window` is '2018_2025' and `cell` is 'dense_none' |
| 1,207 | `55_decision/condition_sensitivity.csv` | column `units_whose_cell_differs_from_the_default_all_cells`; row where `standing_min_ha` is 25.0 and `loss_min_ha` is 1.0 and `window` is '2018_2025' and `cell` is 'dense_none' |
| 308 | `55_decision/condition_sensitivity.csv` | column `units_whose_cell_differs_from_the_default_all_cells`; row where `standing_min_ha` is 10.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'dense_none' |
| 282 | `55_decision/condition_sensitivity.csv` | column `units_whose_cell_differs_from_the_default_all_cells`; row where `standing_min_ha` is 10.0 and `loss_min_ha` is 2.0 and `window` is '2018_2025' and `cell` is 'dense_none' |
| under 10 ha of forest at the start of the window: too little for a share to mean anything | `55_decision/condition_by_unit.csv` | column `forest_loss_share_blank_because_2018_2025`: the one sentence it holds |
| 5,808 | `55_decision/decision.provenance.json` | key `counts` → `loss_as_a_share` → `2018_2025` → `units_with_a_share` |
| 5,660 | `55_decision/decision.provenance.json` | key `counts` → `loss_as_a_share` → `2018_2025` → `units_with_no_share` |
| 22 | `55_decision/decision.provenance.json` | key `counts` → `loss_as_a_share` → `2018_2025` → `units_with_no_share_in_a_cell_with_loss` |
| 55,150 | `55_decision/condition_by_unit.csv` | column `forest_at_window_start_ha_2018_2025` of the same row |
| 0.06 | `55_decision/condition_by_unit.csv` | column `forest_loss_share_pct_2018_2025` of the row with the largest `standing_forest_ha` among those whose `cell_2018_2025` is dense_loss |
| 1,653 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows in a cell with loss whose `order_in_district_cell_by_share_2018_2025` is not their `order_in_district_cell_2018_2025` |
| 1,734 | `55_decision/condition_by_unit.csv` | rows whose `cell_2018_2025` is a cell with loss |
| 2,335 | `55_decision/decision.provenance.json` | key `counts` → `standing_row` → `mostly_dense` |
| 3,461 | `55_decision/decision.provenance.json` | key `counts` → `standing_row` → `mostly_open` |
| 5,672 | `55_decision/decision.provenance.json` | key `counts` → `standing_row` → `little_or_none` |
| 603 | `55_decision/condition_boundary.csv` | column `n_near_the_boundary`; row where `ratio_at_least` is 0.8 and `units` is 'all units' |
| 10.4 | `55_decision/condition_boundary.csv`; `55_decision/condition_threshold_evidence.csv` | computed here: units near the boundary ÷ units that are mostly dense or mostly open × 100. From: column `n_near_the_boundary`; row where `ratio_at_least` is 0.8 and `units` is 'all units'; column `value`; row where `key` is 'units_standing_10' |
| 1,295 | `55_decision/condition_cells.csv` | column `n_units`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_loss' |
| 671 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_none and whose `corroboration` is not not_compared |
| 157 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_none and whose `corroboration` is corestack_only or both |
| 19 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_none, whose `corroboration` is corestack_only or both, and whose `corroboration_basis` is east_coast_every_unit_kept |
| 1,040 | `55_decision/condition_cells.csv` | column `n_units`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_none' |
| 176 | `55_decision/condition_cells.csv` | column `forest_loss_ha_in_window`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_none' |
| 422 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_none and whose `forest_loss_ha_2001_2025`, as printed, is the loss minimum or more |
| 226 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is dense_none and whose `forest_loss_ha_2001_2025` is zero |
| 45,872 | `55_decision/rename_gate.json` | key `assignments_compared_units_x_windows` |
| 51 | `55_decision/rename_gate.json` | key `columns_the_table_had_before` |
| 584,868 | `55_decision/rename_gate.json` | key `cells_compared_as_text` |
| 16 | `55_decision/rename_gate.json` | key `columns_added_since_not_compared`: their number |
| `f129962e816e4da3` | `55_decision/rename_gate.json` | key `table_before_is_the_one_ruled_on_sha256` |
| Open forest, little or no loss recorded - assisted natural regeneration candidate | `55_decision/tiers.csv` | column `cell_name`; row where `cell` is 'open_none' |
| 3,055 | `55_decision/condition_cells.csv` | column `n_units`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_none' |
| 41 | `55_decision/condition_by_unit.csv` | computed here: loss from the dense band ÷ forest loss, in the cell with open forest and loss, × 100. From: worked out by this script from its rows: `loss_dense_ha_2018_2025` summed over the rows whose `cell_2018_2025` is open_loss; worked out by this script from its rows: `forest_loss_ha_2018_2025` summed over the rows whose `cell_2018_2025` is open_loss |
| 102 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is open_loss and whose `loss_dense_ha_2018_2025` is larger than their `loss_open_ha_2018_2025` |
| 406 | `55_decision/condition_cells.csv` | column `n_units`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_loss' |
| Little forest left, loss recorded - verify on the ground | `55_decision/tiers.csv` | column `cell_name`; row where `cell` is 'little_loss' |
| 33 | `55_decision/condition_cells.csv` | column `n_units`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'little_loss' |
| within a district, within a cell: cells with loss by forest loss in the window, largest first; the others by standing hectares of the row's band; ties by uni... | `55_decision/decision.provenance.json` | key `definitions` → `order` |
| PROVISIONAL - to be set with the Foundation for Ecological Security; a user control in the layer, not a constant | `55_decision/decision.provenance.json` | key `tiers` → `status` |
| 2.84 | `20_degradation/agreement_summary.csv` | column `odds_ratio_within_districts`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 1.92 | `20_degradation/agreement_summary.csv` | column `odds_ratio_within_districts_lo95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 5.24 | `20_degradation/agreement_summary.csv` | column `odds_ratio_within_districts_hi95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 1.55 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 0.80 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 3.61 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 1,649 | `20_degradation/agreement_summary.csv` | column `n_assessed`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 25 | `20_degradation/agreement_summary.csv` | column `n_districts`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 1.80 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'all units' |
| 1.10 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'all units' |
| 2.91 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'all units' |
| 2.06 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'outside_village' |
| 1.34 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'outside_village' |
| 3.33 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'outside_village' |
| 5,829 | `55_decision/condition_cells_by_district.csv` | column `n_units` summed over every district and every cell but the one outside the ranked list, window 2018_2025 |
| 2,938 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is not the cell outside the ranked list and whose `corroboration` is not_compared |
| 2.30 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `minimum_reference_ha` is 100.0 and `population` is 'all_assessed' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 1.10 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `minimum_reference_ha` is 100.0 and `population` is 'all_assessed' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 4.70 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `minimum_reference_ha` is 100.0 and `population` is 'all_assessed' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| 14 | `55_decision/condition_by_unit.csv` | districts in which, among the LGD panchayat units whose `corroboration_basis` is headline, no unit is flagged by Hansen or none by CoRE Stack (column `corroboration`) |
| 5 | `55_decision/condition_by_unit.csv` | districts with no unit of either kind whose `corroboration_basis` is headline |
| Bhadrak, Jagatsinghapur, Kendrapara, Khordha, Puri | `55_decision/condition_by_unit.csv` | the districts with no unit whose `corroboration_basis` is headline |
| 187 | `55_decision/condition_by_unit.csv` | units of those districts whose `cell_2018_2025` is a ranked cell |
| 1,804 | `55_decision/condition_cells_by_district.csv` | column `n_outside_village` summed over every district and every cell but the one outside the ranked list, window 2018_2025 |
| 30 | `55_decision/condition_cells_by_district.csv` | districts whose ranked cells hold at least one outside-village unit, window 2018_2025 |
| 97.8 | `40_allocation/assets_district_fy.csv`; `40_allocation/allocation.provenance.json` | computed here: expenditure on works started in or before FY2017-18 ÷ all expenditure × 100. From: worked out by this script from its rows: `expenditure_total` of rows whose `fy_work_start` is a year up to 2017-18; key `dump` → `expenditure_total` |
| 92.9 | `40_allocation/allocation_by_unit_fy.csv` | computed here: expenditure on work types that name forest, on works started in or before FY2017-18 ÷ all such expenditure × 100. From: worked out by this script from its rows: `expenditure_forest_named_worktype` summed over the rows whose `fy_work_start` is 2017-18 or earlier; worked out by this script from its rows: `expenditure_forest_named_worktype` summed over every row |
| 2,781 | `40_allocation/allocation_by_unit.csv` | rows counted by this script: rows whose `expenditure_forest_named_worktype` is above zero |
| 371 | `40_allocation/allocation_by_unit_fy.csv` | worked out by this script from its rows: units with expenditure on work types that name forest, all of it on works whose `fy_work_start` is after 2017-18 |
| 8,687 | `55_decision/decision.provenance.json`; `40_allocation/allocation_by_unit.csv` | computed here: units less the units with any expenditure on work types that name forest. From: key `counts` → `units`; rows counted by this script: rows whose `expenditure_forest_named_worktype` is above zero |
| 123 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `st_share` → `blank` |
| 534 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2011` → `blank` |
| 2,891 | `55_decision/decision.provenance.json`; `55_decision/condition_by_unit.csv` | computed here: units less the units not compared. From: key `counts` → `units`; rows counted by this script: rows whose `corroboration` is not_compared |
| 8,577 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `corroboration` is not_compared |
| 468 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `corroboration_basis` is east_coast_every_unit_kept |
| 8 | `20_degradation/agreement_by_zone.csv` | column `n_districts`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 808 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `corroboration_basis` is below_floor_no_corestack_coverage |
| 696 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `corroboration_basis` is below_floor_no_corestack_coverage and whose `agreement_reference_ha` is zero |
| 30.4 | `55_decision/decision.provenance.json` | computed here: outside-village units ÷ units × 100. From: key `counts` → `by_level` → `outside_village`; key `counts` → `units` |
| 54.5 | `55_decision/condition_by_unit.csv` | computed here: standing forest in outside-village units ÷ standing forest in all units × 100. From: worked out by this script from its rows: `standing_forest_ha` summed over the outside-village units; worked out by this script from its rows: `standing_forest_ha` summed over all units |
| No revenue village — this land is in no village plan. Whose plan covers it? | `55_decision/condition_by_unit.csv` | column `governance_prompt`: the one text every outside-village unit carries |
| 1 | `55_decision/condition_by_unit.csv` | outside-village rows whose `district_check` names more than one status |
| 15 | `10_units/outside_village_district.csv` | rows whose `neighbours_agree_with_assigned` is 0, among the units whose `district_check` in the decision table is name_on_the_polygon_not_contradicted |
| 44 | `10_units/outside_village_district.csv` | rows whose `neighbours_by_code_district_code` is present and is not their `pc11_district_code`, among the units whose `district_check` in the decision table is name_on_the_polygon_not_contradicted |
| Ministry of Rural Development notification S.O. 5448(E), 5 October 2026; Gazette of India, Extraordinary, Part II, Section 3(ii), No. 5238; Gazette ID CG-DL-... | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `document` |
| https://egazette.gov.in/WriteReadData/2026/276796.pdf | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `source_url` |
| 1,700,498 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `inputs` → `0` → `bytes` |
| ec89d3a85bf49f1a4218b897c1daca2b3ab86d71b42f8f52c2d9860b6e0279a4 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `inputs` → `0` → `sha256` |
| is on this machine and has that size and hash | this run | the file was read and hashed by this script |
| 5 | `00_raw/data_manifest.csv` | rows counted by this script: rows whose `item_id` begins vbgramg_ |
| The Viksit Bharat-Guarantee for Rozgar and Ajeevika Mission (Gramin): VB-G RAM G Act, 2025 (No. 36 of 2025), as published in the Gazette of India, Extraordin... | `00_raw/data_manifest.csv` | column `title`; row where `item_id` is 'vbgramg_act_36_of_2025_pdf' |
| 375 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `rows` |
| 128, 111, 98, 38 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `rows_by_category_equal_the_ministrys_published_totals` |
| Press Information Bureau release 2319426, 6 October 2026 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `published_totals_from` |
| https://www.pib.gov.in/PressReleasePage.aspx?PRID=2319426 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `totals_url` |
| 375 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `rows_walked_in_the_pdfs_own_order_each_work_type_and_name_whole_and_on_its_own_row` |
| 30 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `sub_item_headings_met_on_the_way_and_held_word_for_word` |
| 4 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `category_headings_met_on_the_way_and_held_word_for_word` |
| 375 | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `checks_passed` → `rows_whose_two_cells_read_whole_from_the_positions_of_the_words_are_the_transcriptions` |
| 22 | `.session_scratch_2026-10-05/schedule_extract_trials_2026-10-09.json` *(working file)* | key `errors_tried` |
| the names of Sl. 105 and Sl. 106 changed over; the name of Sl. 91 cut short; the name of the last row, Sl. 375, cut short; Sl. 372 given the work type of Sl.... | `.session_scratch_2026-10-05/schedule_extract_trials_2026-10-09.json` *(working file)* | key `trials`: the errors tried |
| the digits of the serial numbers against the PDF: they are not in its text layer and were read from the page images by the transcriber; what is established i... | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | key `not_checked` |
| pending — schedule not yet registered | `55_decision/decision.provenance.json` | key `work_types` → `field_when_not_registered` |
| 9 | `55_decision/work_types.csv` | column `entries`: the number of distinct serial numbers cited |
| No row of the list names forest land, and the list does not sort its works by the condition of a forest. Which rows bear on a cell is this project's proposal... | `55_decision/work_types.csv` | column `note`: the one note every row carries |
| 24 | `55_decision/work_rows_naming_forest.csv` | its rows: every row of the list whose work type or name holds the word forest |
| 17 | `55_decision/work_rows_naming_forest.csv` | rows whose `cited_by_cells` is blank |
| (vi) forest fire management works, including firebreaks, fuel buffer zones and allied measures | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv` | the sub-item heading of its last row |
| Sl. 375, Allied measures - forest: Construction of animal protection trenches for community | `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv` | its last row: serial, work type and work name |
| regeneration; forest land; grazing; biodiversity | `55_decision/decision.provenance.json` | key `work_types` → `words_in_no_row_of_the_list` |
| 60_layer/overlay.js | `60_layer/layer.provenance.json` | key `decision_view` → `overlay_file` → `path` |
| only requests for tiles, to the registered host and no other, and only while the box is ticked: each carries the tile's place and zoom and the years of the w... | `scripts/layer_overlay.json` | key `what_is_sent` |
| 2026-10-08T12:31:13Z | `scripts/layer_overlay.json` | key `verified_utc` |
| Global Forest Watch (World Resources Institute) | `scripts/layer_overlay.json` | key `provider` |
| https://tiles.globalforestwatch.org/umd_tree_cover_loss/v1.13/dynamic/{z}/{x}/{y}.png?render_type=true_color&tree_cover_density_threshold=10 | `scripts/layer_overlay.json` | key `url_template` |
| https://tiles.globalforestwatch.org/openapi.json - the specification behind the provider's own reference pages https://tiles.globalforestwatch.org/ and https... | `scripts/layer_overlay.json` | key `documented_at` |
| a machine-generated API reference on the tile host. There is no prose guide; the provider's developer help does not name the tile host | `scripts/layer_overlay.json` | key `documentation_is` |
| Hansen/UMD Global Forest Change v1.13 | `scripts/layer_overlay.json` | key `data_version` |
| 2025 | `scripts/layer_overlay.json` | key `loss_through_year` |
| v1.13 is in the address. The alias 'latest' is not used: it moves to the next release without notice | `scripts/layer_overlay.json` | key `version_is_pinned` |
| start_year and end_year are added by the page from the window chosen for the decision view | `scripts/layer_overlay.json` | key `year_parameters` |
| tree_cover_density_threshold=10: loss on land with about 10 % tree canopy or more in 2000, the dense and the open band of the decision view together. The ref... | `scripts/layer_overlay.json` | key `canopy_setting` |
| 512-pixel PNG on the ordinary web-map grid; with render_type=true_color, pink on transparent. Below zoom 12 a tile is an aggregate shaded by the density of loss | `scripts/layer_overlay.json` | key `tiles_are` |
| 12 | `scripts/layer_overlay.json` | key `max_native_zoom` |
| this layer's own setting, not a limit of the provider: a tile at zoom 12 is already at the data's full resolution, and the layer enlarges it beyond that. The... | `scripts/layer_overlay.json` | key `max_native_zoom_is` |
| CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), stated in the provider's dataset record https://data-api.globalforestwatch.org/dataset/umd_tree_cov... | `scripts/layer_overlay.json` | key `data_licence` |
| Source: Hansen/UMD/Google/USGS/NASA. Global Forest Change v1.13, CC BY 4.0. Tiles served by Global Forest Watch (World Resources Institute) | `scripts/layer_overlay.json` | key `attribution` |
| https://globalnaturewatch.org/terms/ | `scripts/layer_overlay.json` | key `terms_url` |
| The address https://www.globalforestwatch.org/terms/ redirects to this page, 'Terms of Service \/ Global Nature Watch'. It names resourcewatch.org, globalfor... | `scripts/layer_overlay.json` | key `terms_cover` |
| Use of the services is agreement to the terms. 'You may not use the Services in any manner that could damage or overburden the Services or interfere with any... | `scripts/layer_overlay.json` | key `terms_say` |
| https://resourcewatch.org/api-attribution-requirements - it speaks of 'the Resource Watch API': 'Websites that use the Resource Watch API must include the "p... | `scripts/layer_overlay.json` | key `attribution_requirements_page` |
| Two independent searches and an adversarial verifier read the provider's reference, dataset record and terms on 8 Oct 2026; tiles over central Odisha were fe... | `scripts/layer_overlay.json` | key `verified_how` |
| Two points, both the project owner's to decide; one note to gfw@wri.org could settle both. (1) API keys. The terms read 'each request to an API must include ... | `scripts/layer_overlay.json` | key `terms_unresolved` |
| 5 | `00_raw/data_manifest.csv` | the rows of the provider's pages registered on 9 October 2026: their number |
| 2 | `00_raw/data_manifest.csv` | the rows of the provider's pages registered on 10 October 2026: their number |
| 5 | this run | the kept copies of the provider's pages that this script read |
| 13 | `scripts/layer_overlay.json` | the sentences this script looked for in the kept copies of the provider's pages |
| 13 | `00_raw/05_forest_reference/provider_cautions.json` | key `checks_passed` → `sentences_found_word_for_word` |
| 6.0 | `70_share/share.provenance.json` | key `the_copy` → `zip` → `bytes` |
| 11,468 | `70_share/share.provenance.json` | key `development_index_left_out` → `unit_rows_from_which_the_value_was_taken` |
| 194,058 | `70_share/share.provenance.json` | key `development_index_left_out` → `bytes_shorter_than_the_layers` → `data.js` |
| 11 | `70_share/share.provenance.json` | key `checks_passed` → `credits_read_from_the_layers_own_sources` |
| Chrome/154.0.8037.99 | `70_share/exercise_share_chrome.json` | key `browser` |
| 8 | `70_share/exercise_share_chrome.json` | key `summary` → `steps` |
| The overlay's file, overlay.js, is not beside this page. Everything else on the map works as before. | `70_share/exercise_share_chrome.json` | key `summary` → `what_the_control_said_when_ticked` |
| https://sudo-karan.github.io/ICTD_Project/ | `70_share/pages_publication.json` | key `address` |
| 907d0f905b33 | `70_share/pages_publication.json` | key `gh_pages_commit_when_checked`, its first twelve characters |
| 2026-10-10T20:09:31Z | `70_share/pages_live_check.json` | key `run_utc` |
| 9 | `70_share/pages_live_check.json` | key `checks_made` |
| 12 | `60_layer/exercise_decision_chrome.json` | key `summary` → `overlay` → `notes` → the first → `tiles_drawn`: its second figure, the tiles drawn |
| 12 | `60_layer/exercise_decision_chrome.json` | key `summary` → `overlay` → `notes` → the first → `tiles_drawn`: its first figure, the tiles asked for |
| https://tiles.globalforestwatch.org/umd_tree_cover_loss/v1.13/dynamic/9/375/226.png?render_type=true_color&tree_cover_density_threshold=10&start_year=2018&en... | `60_layer/exercise_decision_chrome.json` | key `summary` → `overlay` → `notes` → `0` → `one_tile_address` |
| 12 | `60_layer/exercise_decision_webkit.json` | key `summary` → `overlay` → `notes` → the first → `tiles_drawn`: its second figure, the tiles drawn |
| 12 | `60_layer/exercise_decision_webkit.json` | key `summary` → `overlay` → `notes` → the first → `tiles_drawn`: its first figure, the tiles asked for |
| 32 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `columns`: their number |
| `district`, `unit_id`, `unit_name`, `unit_type`, `outside_village`, `window_of_forest_loss`, `standing_forest_is_through`, `tier_label`, `tier_definition`, `... | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `columns` |
| Rayagada | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `district` |
| 2018-2025 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `window` |
| 1 Closed forest, loss recorded - find the cause first; 2 Open forest, loss recorded - restore; 3 Closed forest, little or no loss recorded - protect; 4 Littl... | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `tier_order` |
| Scheduled Tribe share 18 % or more; outside-village units left out | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `filter` |
| 201 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `rows` |
| 6,432 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `cells_compared` |
| Ganjam | `60_layer/exercise_decision_chrome.json` | key `summary` → `export_second` → `district` |
| 2017-2023 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export_second` → `window` |
| No filter | `60_layer/exercise_decision_chrome.json` | key `summary` → `export_second` → `filter` |
| 455 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export_second` → `rows` |
| 14,560 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export_second` → `cells_compared` |
| 1 | `60_layer/exercise_decision_chrome.json` | key `summary` → `export` → `rows_with_no_share` |
| 2026-10-09T04:08:58Z | `55_decision/rename_gate.json` | key `run_utc` |
| pandas, with every hectare held as a whole number of ten-thousandths | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `replicator_a` → `means` |
| the Python standard library alone, with decimal arithmetic | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `replicator_b` → `means` |
| 46 | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `columns_compared` |
| 51 | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `columns_of_the_table` |
| 527,528 | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `cells_compared_each` |
| 0 | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `cells_that_differ_only_in_how_they_are_written` |
| Neither replicator wrote the five columns that the docstring they were given described without naming (the standing row, and the loss column of each window);... | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `note` |
| 29 | `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | key `ambiguities_reported` |
| 67 | `55_decision/condition_by_unit.csv` | its columns: their number |
| 6 | `60_layer/decision_runs.json` | key `checks`: their number |
| 5 | `60_layer/decision_runs.json` | key `checks`: the checks whose first run passed |
| 2026-10-10T22:41:56Z | `60_layer/decision_runs.json` | key `started_utc` |
| 62 of 62 checks passed | `60_layer/decision_runs.json` | key `checks`: the first clause of the last line of the run of `verify_decision` in that pass |
| 2026-10-10T11:29:27Z | `.session_scratch_2026-10-05/decision_runs_2026-10-10_pass_not_finished_webkit_stalled.json` *(working file)* | key `started_utc` |
| 5 | `.session_scratch_2026-10-05/decision_runs_2026-10-10_pass_not_finished_webkit_stalled.json` *(working file)* | key `checks`: the checks whose last run passed |
| 6 | `.session_scratch_2026-10-05/decision_runs_2026-10-10_pass_not_finished_webkit_stalled.json` *(working file)* | key `checks`: their number |
| RuntimeError: the WebKit driver ended | `.session_scratch_2026-10-05/decision_runs_2026-10-10_pass_not_finished_webkit_stalled.json` *(working file)* | key `checks`: what the last run of that check said |
| Chrome/154.0.8037.99 | `60_layer/exercise_chrome.json` | key `summary` → `browser` |
| 53 | `60_layer/exercise_chrome.json` | key `summary` → `controls_exercised` |
| 29 | `60_layer/exercise_chrome.json` | key `summary` → `units_clicked` |
| 1,276 | `60_layer/exercise_chrome.json` | key `summary` → `values_compared` |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_made` of the check 'exercise_layer in Chrome' |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_that_passed` of the check 'exercise_layer in Chrome' |
| WebKit 21624.5.1.11.3 (the engine of Safari 27.0 on this machine) | `60_layer/exercise_webkit.json` | key `summary` → `browser` |
| 53 | `60_layer/exercise_webkit.json` | key `summary` → `controls_exercised` |
| 29 | `60_layer/exercise_webkit.json` | key `summary` → `units_clicked` |
| 1,276 | `60_layer/exercise_webkit.json` | key `summary` → `values_compared` |
| 2 | `60_layer/decision_runs.json` | key `checks`: `runs_made` of the check 'exercise_layer in WebKit' |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_that_passed` of the check 'exercise_layer in WebKit' |
| [map] dragged the map 180 px left and 120 px up (mouse-down, eight mouse-moves and mouse-up, made in script) | `60_layer/decision_runs.json` | key `checks`: the `failed_lines` of the runs of 'exercise_layer in WebKit' |
| the owner's handoff of 11 October 2026: Chrome and WebKit only; the Safari application is not to be started | `60_layer/decision_runs.json` | key `checks_not_run_in_this_pass`: `why` |
| 2026-10-08T22:53:16Z | `60_layer/exercise_safari.json` | key `summary` → `run_utc` |
| 2026-10-08T22:42:59Z | `60_layer/exercise_safari.json` | key `summary` → `layer_run_utc` |
| 48 | `60_layer/exercise_safari.json` | key `summary` → `addresses_tried` |
| 1,265 | `60_layer/exercise_safari.json` | key `summary` → `values_compared` |
| Safari 27.0 (the application) | `60_layer/exercise_decision_safari.json` | key `summary` → `browser` |
| title, address and text were each asked for through the address filter (first document whose URL starts with the marked address), never through the by-title ... | `60_layer/exercise_decision_safari.json` | key `summary` → `how_the_window_was_read` |
| 2026-10-08T22:42:59Z | `60_layer/exercise_decision_safari.json` | key `summary` → `layer_run_utc` |
| 48 | `60_layer/exercise_decision_safari.json` | key `summary` → `part1_the_unchanged_scripts_main` → `addresses_tried` |
| 1,265 | `60_layer/exercise_decision_safari.json` | key `summary` → `part1_the_unchanged_scripts_main` → `values_compared` |
| 29 | `60_layer/exercise_decision_safari.json` | key `summary` → `part1_the_unchanged_scripts_main` → `units_opened_by_address` |
| 2026-10-07T12:05:18Z | `.session_scratch_2026-10-05/60_layer_2026-10-07/layer.provenance.json` *(working file)* | key `run_utc` |
| 23 | `.session_scratch_2026-10-05/60_layer_2026-10-07/layer.provenance.json` *(working file)* | key `inputs`: the files it lists with a sha256 |
| 13 | `60_layer/layer.provenance.json`; `.session_scratch_2026-10-05/60_layer_2026-10-07/layer.provenance.json` *(working file)* | computed here: inputs of today's layer less inputs of the layer of 7 October. From: key `inputs`: the files it lists with a sha256; key `inputs` |
| `44890a1` | `git` | the commit this batch started from |
| `CLAUDE.md`, `README.md`, `docs/DATA_NOTES.md`, `docs/LAYER.md`, `docs/RESULTS.md` | `git diff --name-status 44890a1` | the documents among the files modified |
| 140 | `git diff --numstat 44890a1 -- scripts/write_results.py` | lines added |
| 20 | `git diff --numstat 44890a1 -- scripts/write_results.py` | lines removed |
| 53 | `60_layer/exercise_decision_chrome.json` | key `summary` → `steps` |
| 6 | `60_layer/exercise_decision_chrome.json` | key `summary` → `steps_that_are_statements_and_not_actions` |
| 3 | `60_layer/exercise_decision_chrome.json` | key `summary` → `tier_arrows_pressed` |
| 8 | `60_layer/exercise_decision_chrome.json` | key `summary` → `tier_arrows_there_are` |
| 46 | `60_layer/exercise_decision_chrome.json` | key `summary` → `units_opened` |
| 18 | `60_layer/exercise_decision_chrome.json` | key `summary` → `by_type` → `lgd_panchayat` |
| 28 | `60_layer/exercise_decision_chrome.json` | key `summary` → `by_type` → `outside_village` |
| 16 | `60_layer/exercise_decision_chrome.json` | key `summary` → `districts_of_outside_village_units_opened`: their number |
| 2 | `60_layer/exercise_decision_chrome.json` | key `summary` → `cells_and_windows_seen`: windows in which all six cells were opened |
| 11 | `60_layer/exercise_decision_chrome.json` | key `summary` → `kinds_of_badge_there_are` |
| 874 | `60_layer/exercise_decision_chrome.json` | key `summary` → `lines_compared` |
| 0 | `60_layer/exercise_decision_chrome.json` | key `summary` → `units_opened_that_touch_the_one_aimed_at` |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_made` of the check 'exercise_decision in Chrome' |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_that_passed` of the check 'exercise_decision in Chrome' |
| 47 | `60_layer/exercise_decision_webkit.json` | key `summary` → `steps` |
| 46 | `60_layer/exercise_decision_webkit.json` | key `summary` → `units_opened` |
| 874 | `60_layer/exercise_decision_webkit.json` | key `summary` → `lines_compared` |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_made` of the check 'exercise_decision in WebKit' |
| 1 | `60_layer/decision_runs.json` | key `checks`: `runs_that_passed` of the check 'exercise_decision in WebKit' |
| 59 | `60_layer/exercise_decision_safari.json` | key `summary` → `part2_the_decision_view` → `addresses_tried` |
| 657 | `60_layer/exercise_decision_safari.json` | key `summary` → `part2_the_decision_view` → `lines_compared` |
| 46 | `60_layer/exercise_decision_safari.json` | key `summary` → `part2_the_decision_view` → `units_opened_by_address` |
| 2026-10-10T22:16:08Z | `70_share/exercise_share_chrome.json` | key `run_utc` |
| 2026-10-08T13:02:50Z | `.session_scratch_2026-10-05/decision_runs_2026-10-08.json` *(working file)* | key `layer_run_utc` |
| 3 | `.session_scratch_2026-10-05/decision_runs_2026-10-08.json` *(working file)* | key `unchanged_webkit_exercise` → `runs` |
| 1 | `.session_scratch_2026-10-05/decision_runs_2026-10-08.json` *(working file)* | key `unchanged_webkit_exercise` → `runs_with_a_failed_step` |
| it stopped at its first reading, twice, before any assertion: Safari held another window of the same page, and had just been started in the background | `.session_scratch_2026-10-05/decision_runs_2026-10-08.json` *(working file)* | key `unchanged_safari_script_as_written` → `earlier_the_same_day_on_an_earlier_build` |
| 2026-10-08T20:41:54Z | `.session_scratch_2026-10-05/decision_runs_2026-10-09_pass_with_a_step_by_hand.json` *(working file)* | key `layer_run_utc` |
| 3 | `.session_scratch_2026-10-05/decision_runs_2026-10-09_pass_with_a_step_by_hand.json` *(working file)* | key `checks`: `runs_made` of the check 'exercise_layer_safari, as written' |
| 1 | `.session_scratch_2026-10-05/decision_runs_2026-10-09_pass_with_a_step_by_hand.json` *(working file)* | key `checks`: `runs_that_passed` of the check 'exercise_layer_safari, as written' |
| This is the record the runner wrote on 9 October 2026, as it was written, with this one note added. In it the unchanged Safari script was run three times. Th... | `.session_scratch_2026-10-05/decision_runs_2026-10-09_pass_with_a_step_by_hand.json` *(working file)* | key `note_added_by_hand` |
| 2026-10-08T22:42:59Z | `.session_scratch_2026-10-05/60_layer_2026-10-08_as_ruled_on/decision_runs.json` *(working file)* | key `layer_run_utc` |
| 8 | `.session_scratch_2026-10-05/60_layer_2026-10-08_as_ruled_on/decision_runs.json` *(working file)* | key `checks`: their number |
| 8 | `.session_scratch_2026-10-05/60_layer_2026-10-08_as_ruled_on/decision_runs.json` *(working file)* | key `checks`: the checks whose first run passed |
| During the Safari runs of 8 October the Safari that the check had started in the background received a request to quit (the system log has it at 16:19:50 IST... | `.session_scratch_2026-10-05/decision_runs_2026-10-08.json` *(working file)* | key `the_owners_safari_windows_on_8_october` |
| Tree cover loss is defined as “stand replacement disturbance” which is considered to be clearing of at least half of tree cover within a 30-meter pixel. | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `loss_is` → `text` |
| “Loss” indicates the removal or mortality of tree cover and can be due to a variety of factors, including mechanical harvesting, fire, disease, or storm dama... | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `loss_is_not_deforestation` → `text` |
| Comparisons between the original 2001-2010 data and the 2011-2025 update should be performed with caution. | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `two_halves_of_the_record` → `text` |
| Largely because of a delay between an actual disturbance and the event being observed by the satellite imagery, the authors are 75% confident that the loss o... | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `year_of_loss` → `text` |
| Forest loss during the period 2000-2025, defined as a stand-replacement disturbance, or a change from a forest to non-forest state. | `00_raw/05_forest_reference/provider_cautions.json` | key `sentences` → `umd_loss_is` → `text` |
| 23 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2010`; row where `units` is 'all units' and `canopy_band` is 'gt10le30' |
| 114 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2011_2017`; row where `units` is 'all units' and `canopy_band` is 'gt10le30' |
| 226 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2018_2025`; row where `units` is 'all units' and `canopy_band` is 'gt10le30' |
| 207 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is the cell of closed forest with loss and whose `loss_open_ha_2018_2025` is above their `loss_dense_ha_2018_2025` |
| 1,295 | `55_decision/condition_cells.csv` | column `n_units`; row where `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_loss' |
| 22.5 | `60_layer/layer.provenance.json` | key `outputs` → `both_bytes` |
| 6.0 | `60_layer/layer.provenance.json` | key `outputs` → `both_zipped_bytes` |
| 25.0 | `60_layer/layer.provenance.json` | key `outputs` → `limit_bytes` |
| 1,213 | `60_layer/layer.provenance.json` | key `decision_view` → `overlay_file` → `bytes` |

### 20.2 Tables, in the order they appear

Every cell of a table that is not a typed label was read from the file and columns given here.

| table | cells read | file | columns or keys | rows |
|---|---|---|---|---|
| §3, the reconciliation | 10 | `55_decision/condition_by_unit.csv` | worked out by this script from its rows: `standing_dense_ha` summed over all units, as km², worked out by this script from its rows: `dense_2000_ha` less `standing_dense_ha`, summed over all units, as km², worked out by this script from its rows: `dense_2000_ha` summed over all units, as km², worked out by this script from its rows: `standing_open_ha` summed over all units, as km², worked out by this script from its rows: `open_2000_ha` less `standing_open_ha`, summed over all units, as km², worked out by this script from its rows: `open_2000_ha` summed over all units, as km² |  |
|  |  | `20_degradation/hansen_loss_by_canopy_band.csv` | `land_km2`, `loss_km2_2001_2025` | `units` is 'all units' and `canopy_band` is 'gt30'; `units` is 'all units' and `canopy_band` is 'gt10le30' |
| §4, the four windows | 31 | `55_decision/decision.provenance.json` | `definitions` → `windows` → `2018_2025` → `is`, `definitions` → `windows` → `2001_2025` → `is`, `definitions` → `windows` → `2017_2023` → `is`, `definitions` → `windows` → `2021_2025` → `is` |  |
|  |  | `55_decision/condition_cells.csv` | `n_units` | `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_none'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_none'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'little_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'little_none'; `window` is '2001_2025' and `units` is 'all units' and `cell` is 'dense_none'; `window` is '2001_2025' and `units` is 'all units' and `cell` is 'dense_loss'; `window` is '2001_2025' and `units` is 'all units' and `cell` is 'op ... |
|  |  | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2001_2025` differs from `cell_2018_2025`, rows counted by this script: rows whose `cell_2017_2023` differs from `cell_2018_2025`, rows counted by this script: rows whose `cell_2021_2025` differs from `cell_2018_2025` |  |
| §5.1, small losses | 8 | `55_decision/condition_threshold_evidence.csv` | `value` | `key` is 'under_mid_pixel_2018_2025'; `key` is 'mid_pixel_to_loss_min_2018_2025'; `key` is 'under_mid_pixel_2001_2025'; `key` is 'mid_pixel_to_loss_min_2001_2025'; `key` is 'under_mid_pixel_2017_2023'; `key` is 'mid_pixel_to_loss_min_2017_2023'; `key` is 'under_mid_pixel_2021_2025'; `key` is 'mid_pixel_to_loss_min_2021_2025' |
| §5.1, recurrence of loss | 15 | `55_decision/decision.provenance.json` | `thresholds` → `alternatives` → `standing_min_ha` → `0`, `thresholds` → `standing_min_ha`, `thresholds` → `alternatives` → `standing_min_ha` → `1` |  |
|  |  | `55_decision/condition_threshold_evidence.csv` | `value`, `n` | `key` is 'recur_5_0.5'; `key` is 'recur_5_1'; `key` is 'recur_5_2'; `key` is 'fresh_5'; `key` is 'recur_10_0.5'; `key` is 'recur_10_1'; `key` is 'recur_10_2'; `key` is 'fresh_10'; `key` is 'recur_25_0.5'; `key` is 'recur_25_1'; `key` is 'recur_25_2'; `key` is 'fresh_25' |
| §5.1, the loss column by size of forest | 32 | `55_decision/condition_threshold_evidence.csv` | `n`, `value` | `key` is 'some_loss_share_10'; `key` is 'recur_size_10'; `key` is 'fresh_size_10'; `key` is 'some_loss_share_25'; `key` is 'recur_size_25'; `key` is 'fresh_size_25'; `key` is 'some_loss_share_50'; `key` is 'recur_size_50'; `key` is 'fresh_size_50'; `key` is 'some_loss_share_100'; `key` is 'recur_size_100'; `key` is 'fresh_size_100'; `key` is 'some_loss_share_250'; `key` is 'recur_size_250'; `key` is 'fresh_size_250'; `key` is 'some_loss_share_500'; `key` is 'recur_size_500'; `key` is 'fresh_size_500'; `key` is 'some_loss_share_1000'; `key` is 'recur_size_1000'; `key` is 'fresh_size_1000'; `key` is 'some_loss_share_5000'; `key` is 'recur_size_5000'; `key` is 'fresh_size_5000' |
| §5.2, the standing minimum | 21 | `55_decision/decision.provenance.json` | `thresholds` → `alternatives` → `standing_min_ha` → `0`, `thresholds` → `standing_min_ha`, `thresholds` → `alternatives` → `standing_min_ha` → `1` |  |
|  |  | `55_decision/condition_threshold_evidence.csv` | `value`, `n` | `key` is 'pixels_in_standing_5'; `key` is 'units_standing_5'; `key` is 'share_standing_5'; `key` is 'repeat_rho_5'; `key` is 'repeat_no_loss_5'; `key` is 'pixels_in_standing_10'; `key` is 'units_standing_10'; `key` is 'share_standing_10'; `key` is 'repeat_rho_10'; `key` is 'repeat_no_loss_10'; `key` is 'pixels_in_standing_25'; `key` is 'units_standing_25'; `key` is 'share_standing_25'; `key` is 'repeat_rho_25'; `key` is 'repeat_no_loss_25' |
| §5.3, sensitivity in the default window | 80 | `55_decision/decision.provenance.json` | `thresholds` → `alternatives` → `standing_min_ha` → `0`, `thresholds` → `alternatives` → `loss_min_ha` → `0`, `thresholds` → `loss_min_ha`, `thresholds` → `alternatives` → `loss_min_ha` → `1`, `thresholds` → `standing_min_ha`, `thresholds` → `alternatives` → `standing_min_ha` → `1` |  |
|  |  | `55_decision/condition_sensitivity.csv` | `n_units`, `units_whose_cell_differs_from_the_default_all_cells` | `standing_min_ha` is 5.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'dense_none'; `standing_min_ha` is 5.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'dense_loss'; `standing_min_ha` is 5.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'open_none'; `standing_min_ha` is 5.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'open_loss'; `standing_min_ha` is 5.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'little_loss'; `standing_min_ha` is 5.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'little_none'; `standing_min_ha` is 5.0 and `loss_min_ha` is 1.0 and `window` i ... |
| §5.3, sensitivity by window | 16 | `55_decision/condition_sensitivity.csv` | `units_whose_cell_differs_from_the_default_all_cells` | `standing_min_ha` is 5.0 and `loss_min_ha` is 1.0 and `window` is '2018_2025' and `cell` is 'dense_none'; `standing_min_ha` is 25.0 and `loss_min_ha` is 1.0 and `window` is '2018_2025' and `cell` is 'dense_none'; `standing_min_ha` is 10.0 and `loss_min_ha` is 0.5 and `window` is '2018_2025' and `cell` is 'dense_none'; `standing_min_ha` is 10.0 and `loss_min_ha` is 2.0 and `window` is '2018_2025' and `cell` is 'dense_none'; `standing_min_ha` is 5.0 and `loss_min_ha` is 1.0 and `window` is '2001_2025' and `cell` is 'dense_none'; `standing_min_ha` is 25.0 and `loss_min_ha` is 1.0 and `window` is '2001_2025' and `cell` is 'dense_none'; `standing_min_ha` is 10.0 and `loss_min_ha` is 0.5 and `wind ... |
| T_share_w | 16 | `this run` | the window's years |  |
|  |  | `55_decision/decision.provenance.json` | `counts` → `loss_as_a_share` → `2018_2025` → `units_with_a_share`, `counts` → `loss_as_a_share` → `2018_2025` → `units_with_no_share`, `counts` → `loss_as_a_share` → `2018_2025` → `units_with_no_share_in_a_cell_with_loss`, `counts` → `loss_as_a_share` → `2001_2025` → `units_with_a_share`, `counts` → `loss_as_a_share` → `2001_2025` → `units_with_no_share`, `counts` → `loss_as_a_share` → `2001_2025` → `units_with_no_share_in_a_cell_with_loss`, `counts` → `loss_as_a_share` → `2017_2023` → `units_with_a_share`, `counts` → `loss_as_a_share` → `2017_2023` → `units_with_no_share`, `counts` → `loss_as_a_share` → `2017_2023` → `units_with_no_share_in_a_cell_with_loss`, `counts` → `loss_as_a_share` →  ... |  |
| T_share | 54 | `55_decision/tiers.csv` | `cell_name` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
|  |  | `55_decision/condition_share.csv` | `n_units`, `n_with_a_share`, `n_no_share_too_little_forest_at_the_start`, `share_under_1pct`, `share_1_to_under_5pct`, `share_5pct_or_more`, `median_share_pct`, `largest_share_pct` | `window` is '2018_2025' and `cell` is 'open_loss'; `window` is '2018_2025' and `cell` is 'dense_loss'; `window` is '2018_2025' and `cell` is 'open_none'; `window` is '2018_2025' and `cell` is 'dense_none'; `window` is '2018_2025' and `cell` is 'little_loss'; `window` is '2018_2025' and `cell` is 'little_none' |
| §6, near the dense and open line | 60 | `55_decision/condition_boundary.csv` | `ratio_at_least`, `n_units_mostly_dense_or_mostly_open`, `n_near_the_boundary`, `of_them_mostly_dense`, `of_them_mostly_open` | `ratio_at_least` is 0.5 and `units` is 'all units'; `ratio_at_least` is 0.5 and `units` is 'lgd_panchayat'; `ratio_at_least` is 0.5 and `units` is 'outside_village'; `ratio_at_least` is 0.6667 and `units` is 'all units'; `ratio_at_least` is 0.6667 and `units` is 'lgd_panchayat'; `ratio_at_least` is 0.6667 and `units` is 'outside_village'; `ratio_at_least` is 0.8 and `units` is 'all units'; `ratio_at_least` is 0.8 and `units` is 'lgd_panchayat'; `ratio_at_least` is 0.8 and `units` is 'outside_village'; `ratio_at_least` is 0.9 and `units` is 'all units'; `ratio_at_least` is 0.9 and `units` is 'lgd_panchayat'; `ratio_at_least` is 0.9 and `units` is 'outside_village' |
| §7, the six cells | 48 | `55_decision/tiers.csv` | `cell_name` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
|  |  | `55_decision/condition_cells.csv` | `n_units`, `standing_dense_ha`, `standing_open_ha`, `forest_loss_ha_in_window`, `near_dense_open_boundary` | `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_loss'; `window` is '2018_2025' and `units` is 'lgd_panchayat' and `cell` is 'open_loss'; `window` is '2018_2025' and `units` is 'outside_village' and `cell` is 'open_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_loss'; `window` is '2018_2025' and `units` is 'lgd_panchayat' and `cell` is 'dense_loss'; `window` is '2018_2025' and `units` is 'outside_village' and `cell` is 'dense_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_none'; `window` is '2018_2025' and `units` is 'lgd_panchayat' and `cell` is 'open_none'; `window` is '2018_2025' and `units` is 'outside_v ... |
| T_names | 11 | `.session_scratch_2026-10-05/55_decision_2026-10-08_as_ruled_on/tiers.csv` *(working file)* | `cell_name` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
|  |  | `55_decision/tiers.csv` | `cell_name` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss' |
| §8, the tiers | 12 | `55_decision/tiers.csv` | `tier_label`, `why_this_place_in_the_order` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
| §9, the odds ratios by floor | 12 | `20_degradation/agreement_summary.csv` | `minimum_reference_ha`, `n_assessed`, `odds_ratio`, `odds_ratio_lo95`, `odds_ratio_hi95`, `odds_ratio_within_districts`, `odds_ratio_within_districts_lo95`, `odds_ratio_within_districts_hi95` | `minimum_reference_ha` is 10.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat'; `minimum_reference_ha` is 50.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat'; `minimum_reference_ha` is 100.0 and `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `units` is 'lgd_panchayat' |
| §9, by district | 120 | `55_decision/condition_cells_by_district.csv` | `district`, worked out by this script from its rows: `n_units` summed over the cells other than the one outside the ranked list, window 2018_2025, district Anugul, worked out by this script from its rows: `n_outside_village` summed over the cells other than the one outside the ranked list, window 2018_2025, district Anugul, worked out by this script from its rows: `n_units` summed over the cells of the cell outside the ranked list, window 2018_2025, district Anugul, worked out by this script from its rows: `n_units` summed over the cells other than the one outside the ranked list, window 2018_2025, district Balangir, worked out by this script from its rows: `n_outside_village` summed over th ... |  |
| §11, what the badge rests on | 30 | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `corroboration_basis` is headline, rows counted by this script: rows whose `corroboration_basis` is headline and whose `corroboration` is both, rows counted by this script: rows whose `corroboration_basis` is headline and whose `corroboration` is hansen_only, rows counted by this script: rows whose `corroboration_basis` is headline and whose `corroboration` is corestack_only, rows counted by this script: rows whose `corroboration_basis` is headline and whose `corroboration` is neither, rows counted by this script: rows whose `corroboration_basis` is headline and whose `corroboration` is not_compared, rows counted by this script: rows whose `corroborati ... |  |
| §11, the badge by cell | 42 | `55_decision/tiers.csv` | `cell_name` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
|  |  | `55_decision/condition_cells.csv` | `n_units` | `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'open_none'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'dense_none'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'little_loss'; `window` is '2018_2025' and `units` is 'all units' and `cell` is 'little_none' |
|  |  | `55_decision/condition_by_unit.csv` | rows counted by this script: rows whose `cell_2018_2025` is open_loss and whose `corroboration` is both, rows counted by this script: rows whose `cell_2018_2025` is open_loss and whose `corroboration` is hansen_only, rows counted by this script: rows whose `cell_2018_2025` is open_loss and whose `corroboration` is corestack_only, rows counted by this script: rows whose `cell_2018_2025` is open_loss and whose `corroboration` is neither, rows counted by this script: rows whose `cell_2018_2025` is open_loss and whose `corroboration` is not_compared, rows counted by this script: rows whose `cell_2018_2025` is dense_loss and whose `corroboration` is both, rows counted by this script: rows whose ` ... |  |
| §12, the district checks | 6 | `55_decision/condition_by_unit.csv` | rows counted by this script: outside-village rows whose `district_check` names name_on_the_polygon_not_contradicted, rows counted by this script: outside-village rows whose `district_check` names moved_off_the_name, rows counted by this script: outside-village rows whose `district_check` names polygon_has_no_name, rows counted by this script: outside-village rows whose `district_check` names ambiguous, rows counted by this script: outside-village rows whose `district_check` names flagged_one_check_contradicts, rows counted by this script: outside-village rows whose `district_check` names no_check_possible |  |
| §13, work types | 12 | `55_decision/tiers.csv` | `cell_name` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
|  |  | `55_decision/work_types.csv` | `work_type_field` | `cell` is 'open_loss'; `cell` is 'dense_loss'; `cell` is 'open_none'; `cell` is 'dense_none'; `cell` is 'little_loss'; `cell` is 'little_none' |
| §13, forest-named rows cited by no cell | 51 | `55_decision/work_rows_naming_forest.csv` | `serial`, `work_type`, `work_name` | `serial` is 90; `serial` is 92; `serial` is 93; `serial` is 94; `serial` is 95; `serial` is 96; `serial` is 97; `serial` is 98; `serial` is 104; `serial` is 106; `serial` is 107; `serial` is 109; `serial` is 111; `serial` is 112; `serial` is 113; `serial` is 333; `serial` is 375 |
| §16, the files that existed before and were added to | 12 | `git diff --numstat 44890a1` | the file, lines added, lines removed |  |

### 20.3 Files read

| file | bytes | sha256 | the run stamp it carries |
|---|---|---|---|
| `.session_scratch_2026-10-05/55_decision_2026-10-08_as_ruled_on/tiers.csv` *(working file)* | 2,893 | `a734d457e7718afa` | - |
| `.session_scratch_2026-10-05/60_layer_2026-10-07/layer.provenance.json` *(working file)* | 14,664 | `6e93fd76b286d905` | 2026-10-07T12:05:18Z |
| `.session_scratch_2026-10-05/60_layer_2026-10-08_as_ruled_on/decision_runs.json` *(working file)* | 6,680 | `6eec553b95fa0587` | - |
| `.session_scratch_2026-10-05/decision_runs_2026-10-08.json` *(working file)* | 5,032 | `61eeeb47e485e682` | - |
| `.session_scratch_2026-10-05/decision_runs_2026-10-09_pass_with_a_step_by_hand.json` *(working file)* | 9,187 | `8d52b25a4496ad2c` | - |
| `.session_scratch_2026-10-05/decision_runs_2026-10-10_pass_not_finished_webkit_stalled.json` *(working file)* | 6,230 | `8308830d5aa72e67` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/apikey.html` *(working file)* | 2,165,712 | `9a1057979c6fe095` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/attribution.html` *(working file)* | 110,355 | `b2b412bcaf9f2fc8` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/dataset.json` *(working file)* | 7,467 | `d6fda9a9023de671` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/developers.html` *(working file)* | 2,427,052 | `ad50f515ac6703c5` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/openapi.json` *(working file)* | 415,519 | `75e41eafb31af361` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/terms.html` *(working file)* | 91,265 | `edb7dcf50ddcfba4` | - |
| `.session_scratch_2026-10-05/overlay_pages_2026-10-08/umd_v1_13_download.html` *(working file)* | 71,893 | `4b2d38f20e6cb6df` | - |
| `.session_scratch_2026-10-05/replicate_decision/final_comparison.json` *(working file)* | 2,453 | `766935d525b3d3a1` | - |
| `.session_scratch_2026-10-05/schedule_extract_trials_2026-10-09.json` *(working file)* | 11,344 | `7cc40b7344845767` | 2026-10-08T22:34:43Z |
| `00_raw/05_forest_reference/gfw_api_key_guide_2026-10-08.html` | 2,165,712 | `9a1057979c6fe095` | - |
| `00_raw/05_forest_reference/gfw_dataset_record_umd_tree_cover_loss_2026-10-08.json` | 7,467 | `d6fda9a9023de671` | - |
| `00_raw/05_forest_reference/gfw_developer_help_page_2026-10-08.html` | 2,427,052 | `ad50f515ac6703c5` | - |
| `00_raw/05_forest_reference/gfw_terms_of_service_2026-10-08.html` | 91,265 | `edb7dcf50ddcfba4` | - |
| `00_raw/05_forest_reference/gfw_tile_cache_api_reference_openapi_2026-10-08.json` | 415,519 | `75e41eafb31af361` | - |
| `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt` | 23,670 | `c40f12b61de9ddd3` | - |
| `00_raw/05_forest_reference/provider_cautions.json` | 11,359 | `018923092e50c3d6` | 2026-10-09T03:33:43Z |
| `00_raw/05_forest_reference/resourcewatch_api_attribution_requirements_2026-10-08.html` | 110,355 | `b2b412bcaf9f2fc8` | - |
| `00_raw/05_forest_reference/umd_global_forest_change_2025_v1_13_page_2026-10-08.html` | 71,893 | `4b2d38f20e6cb6df` | - |
| `00_raw/06_scheme/_build_schedule_extract.py` | 18,778 | `2363f4bea9466063` | - |
| `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.csv` | 92,751 | `ac7e642dd1d0e040` | - |
| `00_raw/06_scheme/so5448e_2026-10-05_permissible_works_english_table.provenance.json` | 2,772 | `293d82fe6f6665f4` | 2026-10-08T22:32:57Z |
| `00_raw/data_manifest.csv` | 66,182 | `c54969bf437fbd0d` | - |
| `10_units/outside_village_district.csv` | 536,828 | `763630369d3a544c` | - |
| `20_degradation/agreement.provenance.json` | 10,756 | `0c0182e3a357255c` | 2026-10-07T10:08:15Z |
| `20_degradation/agreement_by_zone.csv` | 1,995 | `df07ed89f94db597` | - |
| `20_degradation/agreement_floor_repeatability.csv` | 1,277 | `656d67107fd39010` | - |
| `20_degradation/agreement_summary.csv` | 32,470 | `6e0fb5e26102e318` | - |
| `20_degradation/hansen.provenance.json` | 8,637 | `d6e816740e7dd41a` | 2026-10-05T20:44:23Z |
| `20_degradation/hansen_loss_by_canopy_band.csv` | 2,002 | `c6d479eb7492ccf5` | - |
| `20_degradation/hansen_loss_by_canopy_band_by_unit.csv` | 4,675,831 | `653eda9cef75aef8` | - |
| `30_need/need.provenance.json` | 15,023 | `8024375c3a69546b` | 2026-10-05T20:22:49Z |
| `40_allocation/allocation.provenance.json` | 15,953 | `bf1e7052fa4ba2c7` | 2026-10-05T20:25:06Z |
| `40_allocation/allocation_by_unit.csv` | 1,072,899 | `3f81d2d3edefda9f` | - |
| `40_allocation/allocation_by_unit_fy.csv` | 7,544,719 | `8c991a5917f14e0e` | - |
| `40_allocation/assets_district_fy.csv` | 65,174 | `5e8dcd030f973f36` | - |
| `40_allocation/state_fy_r620_vs_dump.csv` | 2,707 | `bd845de7118bc579` | - |
| `55_decision/condition_boundary.csv` | 587 | `0ba2695976dfb3e7` | - |
| `55_decision/condition_by_unit.csv` | 7,275,979 | `f5f8a218e86a16b7` | - |
| `55_decision/condition_cells.csv` | 10,888 | `92687a08c37e4098` | - |
| `55_decision/condition_cells_by_district.csv` | 25,656 | `7b570808887b85d5` | - |
| `55_decision/condition_sensitivity.csv` | 9,850 | `a4e2bc786ec2593b` | - |
| `55_decision/condition_share.csv` | 3,133 | `dd81a6e4adf06933` | - |
| `55_decision/condition_threshold_evidence.csv` | 15,901 | `6660628f5c963bed` | - |
| `55_decision/decision.provenance.json` | 25,625 | `d62a8eb63f364179` | 2026-10-09T03:37:07Z |
| `55_decision/rename_gate.json` | 4,088 | `1f620bab116db10c` | 2026-10-09T04:08:58Z |
| `55_decision/tiers.csv` | 3,015 | `a7a7db34b7bcb90f` | - |
| `55_decision/work_rows_naming_forest.csv` | 2,055 | `a1c52ae8265c0c5c` | - |
| `55_decision/work_types.csv` | 5,133 | `f6d27c0a66b4100a` | - |
| `60_layer/data.js` | 22,260,285 | `c0224a1627682b2a` | - |
| `60_layer/decision_runs.json` | 6,283 | `ec5e567f36c3eb86` | - |
| `60_layer/exercise_chrome.json` | 26,823 | `67ea8be4deefc1eb` | 2026-10-10T22:45:57Z |
| `60_layer/exercise_decision_chrome.json` | 51,691 | `79b6595a09b1dbb3` | 2026-10-10T22:58:37Z |
| `60_layer/exercise_decision_safari.json` | 59,230 | `4e0185fff677500e` | 2026-10-08T23:04:30Z |
| `60_layer/exercise_decision_webkit.json` | 49,674 | `6276c97084b8f642` | 2026-10-10T23:02:53Z |
| `60_layer/exercise_safari.json` | 17,705 | `b7584629baaa8553` | 2026-10-08T22:53:16Z |
| `60_layer/exercise_webkit.json` | 27,314 | `4f73f836d6ee40ea` | 2026-10-10T22:54:10Z |
| `60_layer/index.html` | 205,721 | `94c9a3a8f195fec4` | - |
| `60_layer/layer.provenance.json` | 24,478 | `27ffbf7609d05e5c` | 2026-10-09T04:08:22Z |
| `70_share/exercise_share_chrome.json` | 5,063 | `01798797082efcbd` | 2026-10-10T22:16:08Z |
| `70_share/odisha_forest_decision_layer/README.txt` | 7,390 | `8cf3242e8c5978ad` | - |
| `70_share/odisha_forest_decision_layer/data.js` | 22,066,227 | `4df21a9f2c43845a` | - |
| `70_share/odisha_forest_decision_layer/index.html` | 205,691 | `508144e070577a5e` | - |
| `70_share/pages_live_check.json` | 4,511 | `151685df83b61163` | 2026-10-10T20:09:31Z |
| `70_share/pages_publication.json` | 1,179 | `4f3655a396a1be8d` | - |
| `70_share/share.provenance.json` | 3,871 | `4678936032348686` | 2026-10-10T20:05:42Z |
| `scripts/05_build_decision.py` | 88,855 | `1e1419645c581203` | - |
| `scripts/layer_overlay.json` | 8,357 | `61000c5a09259cf5` | - |
| `scripts/run_decision_checks.py` | 9,681 | `48a395deca2576e3` | - |
| `scripts/write_results.py` | 114,011 | `b918073042879cfc` | - |

### 20.4 Statements tested before they were written

Each of these is something the text says in words. The script tested it against the files and would have stopped had it failed.

- the four windows of the table are the four named here, the first of them the default
- the tier order names every cell but one, and that one is the cell left outside the ranked list
- the decision table's record and the layer say of standing forest what the owner ruled, in his words, and the layer's decision view nowhere calls it a lower bound
- the layer's About text quotes the provider's two cautions word for word from the registered record
- the gate on the renaming was run on the decision table that is on disk: every unit's cell in every window matches through the owner's list of names, and every column the table had is unchanged
- the layer in `60_layer/` was built from the decision table that is in `55_decision/`
- stage 4 is built: its tables are in `50_gap/` and its account is `docs/GAP.md`
- every unit has a cell in every window: no cell of the four cell columns is blank
- neither threshold of the decision view is the floor of the agreement test
- most of the loss on the lowest band is on land with no canopy at all in 2000
- loss on the lowest band rises across the three periods several times faster than loss in the forest mask
- the build's docstring gives the tolerance on the yearly sums, and the largest difference its run record carries is inside it
- every total the decision stage compared with `hansen_loss_by_canopy_band.csv` equals it to the two decimals that table prints
- where a band does not add up exactly the gap is one ten-thousandth of a hectare
- the build tested the identity on the file as written, read back
- on the table as read here, standing plus loss 2001-2025 never differs from the year-2000 dense band by more than one ten-thousandth of a hectare
- on the table as read here, standing plus loss 2001-2025 never differs from the year-2000 open band by more than one ten-thousandth of a hectare
- no unit's cell, in any window, depends on which of the two rounding rules is used
- the decision table is blank in five columns and, for each window, in the share where none is given and in the share's reason where one is: in every unit and window exactly one of those two is blank
- plantation's share of expenditure in the state report more than halves between FY2016-17 and FY2018-19
- plantation's share of expenditure in the state report is under one per cent in every year after FY2018-19
- the default window's reason, as the layer shows it, names the state report it rests on
- each proposal has one alternative below it and one above
- the proposed loss minimum is more than a dozen pixels
- the Forest Survey's wording on its smallest patch is in `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt`
- Hansen's grid is in degrees, so the ground area of a pixel shrinks towards the north
- in every window more than a hundred units have a forest loss above zero and under the area of the mid-state pixel
- at the proposed standing minimum, the recurrence of loss is within two points whichever of the three loss minimums is used
- loss recurs in more than eighty-five per cent of units at every setting, and starts afresh in under ten per cent
- loss recurs less often among the smallest forest sites than among those with two hundred and fifty hectares or more, where it recurs in more than nine cases in ten
- the share of units with some loss rises with every step up in the size of their standing forest
- the unit with the most standing forest in the cell with closed forest and loss lost under one per cent of it in the window
- more than ninety-nine per cent of all standing forest is in the units kept, at each of the three standing minimums
- a unit's loss rate repeats better between odd and even years the larger the class of land it is in
- in each of the three classes more than half the units have no loss recorded on that land (canopy above ten per cent in 2000) in any year, and the share falls as the class grows
- the proposed standing minimum is the lowest floor at which the agreement test was run, and the lowest class its repeatability table has
- every unit with less land than the standing minimum is in the row 'little or none'
- at the proposal no unit differs from the default
- in the default window, moving the standing minimum to either alternative moves more units than moving the loss minimum to either of its own
- in 2018_2025 a share is blank exactly where the table gives the reason in words, and the reason is one sentence
- in 2018_2025 no share is above a hundred
- in 2001_2025 a share is blank exactly where the table gives the reason in words, and the reason is one sentence
- in 2001_2025 no share is above a hundred
- in 2017_2023 a share is blank exactly where the table gives the reason in words, and the reason is one sentence
- in 2017_2023 no share is above a hundred
- in 2021_2025 a share is blank exactly where the table gives the reason in words, and the reason is one sentence
- in 2021_2025 no share is above a hundred
- the units that lost under a tenth of one per cent are among those that lost under one per cent
- `scripts/verify_decision.py` printed the three counts of §5.1 as it worked them out from stage 1's yearly columns
- in the cells without loss the order by share is the order by standing hectares, unit for unit
- one ratio, and only one, is the flag carried in the table: the smaller within a fifth of the larger
- the owner's list takes the old name of the cell open_loss to the name it has now
- the owner's list takes the old name of the cell dense_loss to the name it has now
- the owner's list takes the old name of the cell open_none to the name it has now
- the owner's list takes the old name of the cell dense_none to the name it has now
- the owner's list takes the old name of the cell little_loss to the name it has now
- the owner's list takes the old name of the cell little_none to the name it has now
- five of the six cells were renamed, and the order of the tiers table is what it was
- the layer's record says no name was shortened for the legend
- the provisional order puts open forest with loss recorded first and closed forest with loss recorded second, and the record notes that a forester could reverse them
- no column name of the decision table carries the words score, index or weight, and every column is one the build's docstring names, by its own name or, for the columns of a window, under the letter W
- the row read for the two odds ratios is the agreement test's delivered headline row for LGD panchayat units
- within districts, the interval of the odds ratio for LGD panchayat units lies above one
- across the state, the interval of the odds ratio for LGD panchayat units includes one
- the two odds ratios in the layer's About text are the ones in `agreement_summary.csv`
- at the headline, the interval of the across-state odds ratio lies above one for all units together and for outside-village units
- the all-units figure in the layer's About text is the one in `agreement_summary.csv`
- with the East Coast units kept, the interval of the across-state odds ratio for LGD panchayat units at the headline floor lies above one
- at the two lower floors of the same table the interval of the across-state odds ratio for LGD panchayat units lies above one
- at every floor of the table the interval of the within-district odds ratio for LGD panchayat units lies above one
- nearly all of the geotagged record's expenditure is on works started in or before FY2017-18
- more than nine tenths of the expenditure on work types that name forest is on works started in or before FY2017-18, and fewer than a fifth of the units with any show only later works
- every unit's badge carries the window 2017-2023
- every unit that was not compared is under the agreement test's floor on one of its two grids: no unit is left out for want of CoRE Stack coverage alone
- one governance prompt is carried by every outside-village unit and by no other
- the governance prompt is the owner's sentence, word for word, with its dash
- every outside-village unit carries a district check, and every status is one of the six listed
- the manifest row carries the address the extract's record names
- the manifest row carries the file's sha256 and the date it was registered
- the Gazette file on disk has the sha256 the manifest row carries
- the serial numbers of the table run from one to its number of rows without a gap
- the release the totals are read from is registered: the extract's record lists it among its inputs and the manifest has a row for it
- the list's headings were compared with their spaces as printed
- the list's table was compared with capitals and dashes kept, and has no blank cell
- the trials of the list's check were made with the script that is on disk, and the unaltered transcription passed
- the decision stage found the registered list and built its work-type fields from it
- no cell's work-type field reads 'pending': the list is registered
- the work a cell's field names beside serial number 372 is that row of the registered table, word for word
- serial number 372 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 373 is that row of the registered table, word for word
- serial number 373 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 374 is that row of the registered table, word for word
- serial number 374 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 372 is that row of the registered table, word for word
- serial number 372 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 373 is that row of the registered table, word for word
- serial number 373 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 374 is that row of the registered table, word for word
- serial number 374 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 121 is that row of the registered table, word for word
- serial number 121 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 123 is that row of the registered table, word for word
- serial number 123 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 372 is that row of the registered table, word for word
- serial number 372 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 373 is that row of the registered table, word for word
- serial number 373 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 374 is that row of the registered table, word for word
- serial number 374 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 105 is that row of the registered table, word for word
- serial number 105 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 108 is that row of the registered table, word for word
- serial number 108 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 110 is that row of the registered table, word for word
- serial number 110 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 91 is that row of the registered table, word for word
- serial number 91 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 121 is that row of the registered table, word for word
- serial number 121 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 123 is that row of the registered table, word for word
- serial number 123 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 372 is that row of the registered table, word for word
- serial number 372 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 373 is that row of the registered table, word for word
- serial number 373 stands under its own work type in a cell's field
- the work a cell's field names beside serial number 374 is that row of the registered table, word for word
- serial number 374 stands under its own work type in a cell's field
- none of the words the record lists as absent is in any row, type or heading of the registered table
- the registered table has no column of cost, rate or amount
- every cell's work-type field carries the same note
- every forest-named row marked as cited is cited by a cell, and the last row of the list is among those cited by none
- the tiles carry the version of Hansen's data that the unit tables are built from, and the address pins that version
- the layer's record of its overlay is the registration's
- the layer's own two files ask the network for nothing
- the registration sets out two unresolved points about the provider's terms
- the registration carries the provider's caution against reading present tree cover from the cover of 2000 less loss
- in Chrome the overlay's box is out of reach outside the decision view, and before it is ticked the page has asked the network for nothing
- in Chrome, with a connection, the overlay drew tiles from the registered host, asked no other, and showed the whole credit beside the box and on the map
- in Chrome, with no connection, the page worked as before, asked the network for nothing, and the control said it needs a connection
- in Chrome, with the overlay's own file kept from loading, the control said that the file is not beside the page
- in Chrome, with the legend hidden, the overlay's note - its credit and its window - was still on the map
- in WebKit, with the legend hidden, the overlay's note - its credit and its window - was still on the map
- in Chrome the overlay steps aside when its host cannot be reached or its file is missing, and follows the window when it is on
- in Chrome, when a few tiles failed after others had arrived, the overlay stayed on and said, beside the box and on the map, that pink may be missing
- in Chrome, when tiles kept failing after some had arrived, the overlay took itself off and said so
- in Chrome, zoomed in to where a view asks for only a few tiles and with the host out of reach, the overlay took itself off as unreachable
- the copy of the provider's page kept with the session's working files (terms.html) holds the words the registration quotes: 'You may not use the Services in any manner that could damage or overbu...'
- the registration quotes those words of terms.html
- the copy of the provider's page kept with the session's working files (terms.html) holds the words the registration quotes: 'If You use Our APIs in Your own products, please credit Us. You agree ...'
- the registration quotes those words of terms.html
- the copy of the provider's page kept with the session's working files (terms.html) holds the words the registration quotes: 'We may cancel or suspend Your access to the Services at any time and f...'
- the registration quotes those words of terms.html
- the copy of the provider's page kept with the session's working files (terms.html) holds the words the registration quotes: 'each request to an API must include one of Your Account's unique API k...'
- the registration quotes those words of terms.html
- the copy of the provider's page kept with the session's working files (terms.html) holds the words the registration quotes: 'resourcewatch.org, globalforestwatch.org, and prepdata.org...'
- the registration names the three sites that terms.html says its terms cover
- the copy of the provider's page kept with the session's working files (attribution.html) holds the words the registration quotes: 'Websites that use the Resource Watch API must include the "powered by ...'
- the registration quotes those words of attribution.html
- the copy of the provider's page kept with the session's working files (attribution.html) holds the words the registration quotes: 'This site is no longer being updated and will be archived in the comin...'
- the registration quotes those words of attribution.html
- the copy of the provider's page kept with the session's working files (developers.html) holds the words the registration quotes: 'Some endpoints require users to include an API key with their request...'
- the registration quotes those words of developers.html
- the copy of the provider's page kept with the session's working files (apikey.html) holds the words the registration quotes: 'To make most requests to the GFW Data API using third-party applicatio...'
- the registration quotes those words of apikey.html
- the copy of the provider's page kept with the session's working files (dataset.json) holds the words the registration quotes: 'clearing of at least half of tree cover within a 30-meter pixel...'
- the registration quotes those words of dataset.json
- the copy of the provider's page kept with the session's working files (dataset.json) holds the words the registration quotes: 'current (post-2000) tree cover cannot be determined by subtracting fig...'
- the registration quotes those words of dataset.json
- the copy of the provider's page kept with the session's working files (dataset.json) holds the words the registration quotes: 'Comparisons between the original 2001-2010 data and the 2011-2025 upda...'
- the registration quotes those words of dataset.json
- the copy of the provider's page kept with the session's working files (dataset.json) holds the words the registration quotes: 'may take the form of natural forests or plantations...'
- the registration quotes those words of dataset.json
- the kept copy of the tile service's reference has the path the registration names
- in Chrome the overlay goes off when the decision view is left
- every tile Chrome asked for was drawn - the tiles drawn, the tiles asked for and the requests to the tile host are one number - and no other host was asked
- every tile WebKit asked for was drawn - the tiles drawn, the tiles asked for and the requests to the tile host are one number - and no other host was asked
- the registered page `05_forest_reference/gfw_dataset_record_umd_tree_cover_loss_2026-10-08.json` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the registered page `05_forest_reference/gfw_terms_of_service_2026-10-08.html` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the registered page `05_forest_reference/resourcewatch_api_attribution_requirements_2026-10-08.html` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the registered page `05_forest_reference/gfw_tile_cache_api_reference_openapi_2026-10-08.json` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the registered page `05_forest_reference/umd_global_forest_change_2025_v1_13_page_2026-10-08.html` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the registered page `05_forest_reference/gfw_developer_help_page_2026-10-08.html` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the registered page `05_forest_reference/gfw_api_key_guide_2026-10-08.html` is byte for byte the copy read on 8 October 2026, and its manifest row gives its bytes and its sha256
- the extract of the provider's cautions is the file its manifest row describes, it was made from the two registered pages that are on disk, and the layer's record says the About text reads the cautions from it
- the copy in `70_share/odisha_forest_decision_layer/` was made from the layer that is in `60_layer/`; its two files are the layer's without the development index of 2011, which neither names; its three files are the ones its record describes and it holds no other; and the check that opened it in Chrome was made on those files and passed every step
- the field left out of the copy is `adi_2011`, its value was taken from the row of every unit, and `60_layer/data.js` still has it
- what the copy's control said when ticked is the layer's own sentence for a file that is not beside the page
- the copy on disk is the one the public site serves: the check of the live site passed every check on this build, the three files it fetched are byte for byte those on disk, and the copy's README gives the site's address and no longer says that terms are not agreed
- an exported row carries district, unit id, unit type, window, tier label, tier definition, the tier order in use and whether it was changed, what orders units within a tier, the six hectare figures, corroboration with its window, the outside-village flag and the build time
- the export has the same columns in WebKit as in Chrome, and in the second list as in the first
- in Chrome the exported file was saved by the browser, read back from disk, and equal to the text the page made (export)
- in Chrome the exported file was saved by the browser, read back from disk, and equal to the text the page made (export_second)
- the exported file has the number of columns the layer's record gives; the development index of 2011 is not among them; the forest at the start of the window and the share follow the forest loss of the window
- of the two lists exported and checked, one was ordered within a tier by hectares lost and one by share lost, and at least one row had no share
- of the two lists exported and checked, one was made under a changed tier order and one under the provisional order, and they are of different windows
- `60_layer/exercise_chrome.json` is the record of a run on the layer that is in `60_layer/`
- `60_layer/exercise_webkit.json` is the record of a run on the layer that is in `60_layer/`
- `60_layer/exercise_decision_chrome.json` is the record of a run on the layer that is in `60_layer/`
- `60_layer/exercise_decision_webkit.json` is the record of a run on the layer that is in `60_layer/`
- the decision view's exercises ran on the decision table that is in `55_decision/` and the page raised no script error
- the decision view's exercises ran on the decision table that is in `55_decision/` and the page raised no script error
- the existing views raised no script error in 60_layer/exercise_chrome.json
- the existing views raised no script error in 60_layer/exercise_webkit.json
- in 60_layer/exercise_decision_chrome.json no click aimed at a unit opened nothing, and none opened a unit that does not touch the one aimed at
- in 60_layer/exercise_decision_webkit.json no click aimed at a unit opened nothing, and none opened a unit that does not touch the one aimed at
- the units opened in Chrome cover all six cells in at least two windows
- the replication's record is of the table the rename gate compares with, and that gate was run on the decision table that is in `55_decision/`: so the columns the replication covered are, cell for cell, today's
- replicator a's table has no cell whose value differs from the decision table's
- replicator b's table has no cell whose value differs from the decision table's
- the columns the replicators did not write are the difference between the table's columns and those compared, and none of them says anything the unit's cell does not
- `60_layer/decision_runs.json` is the finished record of the checks run, one at a time, on the layer that is in `60_layer/`, by the runner as it is on disk
- the two checks in the Safari application were either run in this pass or are named in its record as not run, with the reason
- the runner's record accounts for each of its eight checks once: run, or named as not run
- the script of the check 'verify_layer' is byte for byte the one in the last commit
- the script of the check 'exercise_layer in Chrome' is byte for byte the one in the last commit
- the script of the check 'exercise_layer in WebKit' is byte for byte the one in the last commit
- the last run of the check 'verify_layer' on this build passed
- the last run of the check 'verify_decision' on this build passed
- the last run of the check 'exercise_layer in Chrome' on this build passed
- the last run of the check 'exercise_layer in WebKit' on this build passed
- the last run of the check 'exercise_decision in Chrome' on this build passed
- the last run of the check 'exercise_decision in WebKit' on this build passed
- the kept record of the pass that could not be finished is of the layer on disk, was started before the pass on record, and is marked unfinished
- in the unfinished pass every check but the one of the decision view in WebKit passed on its last run, the verifier among them
- in the unfinished pass the verifier gave the count this script's own run of it gave
- the pass on record was made with the verifier as it now is: its count is the count of this script's own run of it
- in the pass on record the check of the decision view in WebKit, which the earlier pass could not finish, ran to its end and passed
- the two records of the Safari checks in `60_layer/` are of an earlier build, the same one, and on it the unchanged script passed
- the record gives one reason for leaving out both Safari checks
- on an earlier build, the run of the unchanged WebKit exercise that failed a step was the first made of it, and the step was the map drag
- the kept record of the pass with a step made by hand is a finished record, made before the pass reported here, in which every check passed on its last run
- the kept record of the checks of the build the owner ruled on is a finished record of that build
- the map library embedded in the page ignores a mouse-down on a map that still marks a zoom as under way
- the four tracked files that existed before and were changed have lines added and none removed
- of the files that existed before the decision view, the only ones modified are the four of code and data that were added to, documents the owner ordered brought up to date, and the script that writes one of those documents; none is deleted or renamed
- if the results script is changed, it carries the one exception its own docstring states, on the record of the check in the Safari application, and its rule for the Chrome and WebKit records is unchanged
- what is said of the results script's later changes follows the script on disk: whether it has the fourth stage's section and chooses an interpreter for each verifier
- the three unchanged scripts of the regression gate that were run are as committed
- no file of `00_raw/` that is in the last commit was edited: the manifest, if it differs from that commit, has rows appended to it and every committed byte in place
- every stage table the layer of 7 October 2026 was built from goes into today's layer with the same sha256
- recorded loss on the open band rises across the three periods several times faster than loss in the forest mask

### 20.5 Totals that two places both carry, compared

- LGD panchayat units and outside-village units add up to the units
- rows of the decision table, and the units
- land in the dense band in 2000: summed over the decision table, and in `hansen_loss_by_canopy_band.csv` (to within 0.0051)
- loss on the dense band, all years (land in 2000 less standing, summed over the decision table), and in `hansen_loss_by_canopy_band.csv` (to within 0.0051)
- land in the open band in 2000: summed over the decision table, and in `hansen_loss_by_canopy_band.csv` (to within 0.0051)
- loss on the open band, all years (land in 2000 less standing, summed over the decision table), and in `hansen_loss_by_canopy_band.csv` (to within 0.0051)
- units where the dense band adds up exactly and units where it does not, and the units
- units where the open band adds up exactly and units where it does not, and the units
- units where standing plus loss 2001-2025 is exactly the year-2000 dense band: counted here on the table, and in the run record
- units where standing plus loss 2001-2025 is exactly the year-2000 open band: counted here on the table, and in the run record
- units whose standing dense was set to zero, and units where the dense band does not add up exactly
- units whose standing open was set to zero, and units where the open band does not add up exactly
- units with no tier in the default window, and units in the cell left outside the ranked list
- units with no district check and no governance prompt, and LGD panchayat units
- units with no governance prompt, and LGD panchayat units
- units in the six cells of window 2018_2025, and the units
- units in the six cells of window 2001_2025, and the units
- units in the six cells of window 2017_2023, and the units
- units in the six cells of window 2021_2025, and the units
- plantation's share in FY2016-17: in the state report's table and in the decision stage's evidence table
- plantation's share in FY2018-19: in the state report's table and in the decision stage's evidence table
- units of the cell of open forest with loss under the full record that lost under the minimum in the default window: counted here, and in the layer's record of its About text
- the area of a pixel in the evidence table and in the run record
- units with a loss above zero and under the area of the pixel in the middle of the state, in the evidence table and counted here in the decision table
- that count in the evidence table and in the layer's record of its About text
- units with five thousand hectares or more: in the evidence table and counted here
- forest-site units over the eight size classes, and the forest-site units
- units in the cell with closed forest and loss: in the evidence table and in the table of cells
- the rank correlation of the class from 10 ha in the evidence table and in `agreement_floor_repeatability.csv`
- the units of the class from 10 ha in the evidence table and in `agreement_floor_repeatability.csv`
- the rank correlation of the class from 25 ha in the evidence table and in `agreement_floor_repeatability.csv`
- the units of the class from 25 ha in the evidence table and in `agreement_floor_repeatability.csv`
- units with less land than the standing minimum: counted here, and in the layer's record of its About text
- units outside the ranked list with forest on half their land: counted here, and in the layer's record of its About text
- units in the six cells at 5 ha standing and 0.5 ha loss, window 2018_2025, and the units
- units in the six cells at 5 ha standing and 1 ha loss, window 2018_2025, and the units
- units in the six cells at 5 ha standing and 2 ha loss, window 2018_2025, and the units
- units in the six cells at 10 ha standing and 0.5 ha loss, window 2018_2025, and the units
- units in the six cells at 10 ha standing and 1 ha loss, window 2018_2025, and the units
- units in the cell dense_none at the proposal: in the sensitivity table and in the table of cells
- units in the cell dense_loss at the proposal: in the sensitivity table and in the table of cells
- units in the cell open_none at the proposal: in the sensitivity table and in the table of cells
- units in the cell open_loss at the proposal: in the sensitivity table and in the table of cells
- units in the cell little_loss at the proposal: in the sensitivity table and in the table of cells
- units in the cell little_none at the proposal: in the sensitivity table and in the table of cells
- units in the six cells at 10 ha standing and 2 ha loss, window 2018_2025, and the units
- units in the six cells at 25 ha standing and 0.5 ha loss, window 2018_2025, and the units
- units in the six cells at 25 ha standing and 1 ha loss, window 2018_2025, and the units
- units in the six cells at 25 ha standing and 2 ha loss, window 2018_2025, and the units
- units of the cell dense_none in the share table and in the table of cells
- units of the cell dense_none with a share and without one, and its units
- the three classes of the share in the cell dense_none, and its units with a share
- units of the cell dense_loss in the share table and in the table of cells
- units of the cell dense_loss with a share and without one, and its units
- the three classes of the share in the cell dense_loss, and its units with a share
- units of the cell open_none in the share table and in the table of cells
- units of the cell open_none with a share and without one, and its units
- the three classes of the share in the cell open_none, and its units with a share
- units of the cell open_loss in the share table and in the table of cells
- units of the cell open_loss with a share and without one, and its units
- the three classes of the share in the cell open_loss, and its units with a share
- units of the cell little_loss in the share table and in the table of cells
- units of the cell little_loss with a share and without one, and its units
- the three classes of the share in the cell little_loss, and its units with a share
- units of the cell little_none in the share table and in the table of cells
- units of the cell little_none with a share and without one, and its units
- the three classes of the share in the cell little_none, and its units with a share
- units with a share and without one in 2018_2025, and the units
- units with no share in 2018_2025: in the run record and blank in the table
- units with a share and without one in 2001_2025, and the units
- units with no share in 2001_2025: in the run record and blank in the table
- units with a share and without one in 2017_2023, and the units
- units with no share in 2017_2023: in the run record and blank in the table
- units with a share and without one in 2021_2025, and the units
- units with no share in 2021_2025: in the run record and blank in the table
- units of the cell of closed forest with loss whose share prints under one per cent: counted here on the column and in the build's evidence table
- forest sites in a cell without loss whose share prints over two per cent: counted here on the column and in the build's evidence table
- units that lost under one per cent, in the cell of closed forest with loss: counted here on the column `forest_loss_share_pct_2018_2025` and worked out by `scripts/verify_decision.py` from stage 1's yearly columns
- units that lost under a tenth of one per cent, in that cell: counted here on the column `forest_loss_share_pct_2018_2025` and worked out by `scripts/verify_decision.py` from stage 1's yearly columns
- units that lost over two per cent, forest sites in a cell without loss: counted here on the column `forest_loss_share_pct_2018_2025` and worked out by `scripts/verify_decision.py` from stage 1's yearly columns
- units of the cell of closed forest with loss whose share prints under one per cent: in the evidence table and in the share table
- units near the boundary in the boundary table and in the run record
- units near the boundary in the boundary table and counted in the decision table
- forest-site units in the boundary table and in the evidence table
- units in the three rows, and the units
- units mostly dense and mostly open, and the forest-site units
- LGD panchayat and outside-village units in the cell dense_none, and its units
- LGD panchayat and outside-village units in the cell dense_loss, and its units
- LGD panchayat and outside-village units in the cell open_none, and its units
- LGD panchayat and outside-village units in the cell open_loss, and its units
- LGD panchayat and outside-village units in the cell little_loss, and its units
- LGD panchayat and outside-village units in the cell little_none, and its units
- units of the closed-forest cell without loss that CoRE Stack flags: counted here, and in the layer's record of its About text
- units of the closed-forest cell without loss that lost the minimum or more over the full record: counted here, and in the layer's record of its About text
- units of the closed-forest cell without loss flagged by CoRE Stack under the East Coast model: counted here, and in the layer's record of its About text
- LGD panchayat units of the headline: counted in the decision table, and in the agreement summary
- districts with an LGD panchayat unit of the headline: counted in the decision table, and in the agreement summary
- units in the ranked lists of all districts and units outside them, and the units
- outside-village units in a ranked cell: summed over the districts, and in the layer's record of its About text
- units with any expenditure on work types that name forest: in the table by unit and in the table by unit and year
- units over the five bases of the badge, and the units
- headline units whose badge is both, and the agreement record's own count of that class
- headline units whose badge is hansen_only, and the agreement record's own count of that class
- headline units whose badge is corestack_only, and the agreement record's own count of that class
- headline units whose badge is neither, and the agreement record's own count of that class
- units whose badge carries the East Coast note, and the agreement record's count of units left out by the zone model
- units under the East Coast zone model: in the decision table and in the table by zone
- units not compared, and the agreement record's count of units with insufficient forest
- outside-village units whose district check names moved_off_the_name, and the decision record's count checked against the district record
- outside-village units whose district check names polygon_has_no_name, and the decision record's count checked against the district record
- outside-village units whose district check names ambiguous, and the decision record's count checked against the district record
- outside-village units whose district check names flagged_one_check_contradicts, and the decision record's count checked against the district record
- outside-village units whose district check names no_check_possible, and the decision record's count checked against the district record
- bytes of the Gazette file in the manifest row and in the extract's record
- bytes of the Gazette file on disk and in the manifest row
- rows of the table of permissible works, and the rows its record says it has
- rows of the table, and the total the Ministry's release prints
- rows in the four categories, and the rows
- rows of category I counted in the table, and the Ministry's published total for it
- rows of category II counted in the table, and the Ministry's published total for it
- rows of category III counted in the table, and the Ministry's published total for it
- rows of category IV counted in the table, and the Ministry's published total for it
- rows walked in the PDF's own order, and the rows
- rows that begin on their own page and line with both cells at their columns' edges, and the rows
- rows whose two cells, read whole from the positions of the words, are the transcription's, and the rows
- deliberate errors tried on the list's check, and those that stopped it
- rows of the list that hold the word forest: in the decision stage's table and counted here in the registered list
- rows in the exported file and rows the tables give for that list (export)
- cells of the exported file compared and cells equal, Chrome (export)
- rows times columns of the exported file, and the cells compared (export)
- cells of the exported text compared and cells equal, WebKit (export)
- rows in the exported file and rows the tables give for that list (export_second)
- cells of the exported file compared and cells equal, Chrome (export_second)
- rows times columns of the exported file, and the cells compared (export_second)
- cells of the exported text compared and cells equal, WebKit (export_second)
- actions exercised and actions as expected, existing views, 60_layer/exercise_chrome.json
- values compared and values equal, existing views, 60_layer/exercise_chrome.json
- actions exercised and actions as expected, existing views, 60_layer/exercise_webkit.json
- values compared and values equal, existing views, 60_layer/exercise_webkit.json
- steps and steps as expected, decision view, 60_layer/exercise_decision_chrome.json
- lines of 'why this tier' compared and lines equal, 60_layer/exercise_decision_chrome.json
- units opened as aimed and units opened that touch the one aimed at, and the units opened, 60_layer/exercise_decision_chrome.json
- kinds of corroboration badge seen and kinds there are, 60_layer/exercise_decision_chrome.json
- steps and steps as expected, decision view, 60_layer/exercise_decision_webkit.json
- lines of 'why this tier' compared and lines equal, 60_layer/exercise_decision_webkit.json
- units opened as aimed and units opened that touch the one aimed at, and the units opened, 60_layer/exercise_decision_webkit.json
- kinds of corroboration badge seen and kinds there are, 60_layer/exercise_decision_webkit.json
- units opened in Chrome by kind, and the units opened
- columns of the table that was replicated, and the columns the rename gate found unchanged
- part one in Safari: addresses tried and addresses as expected
- part one in Safari: values compared and values found
- part two in Safari: addresses tried and addresses as expected
- part two in Safari: lines compared and lines found

### 20.6 Digits the text was allowed to carry

The text itself may hold no digit except inside a code span (a file, a column, a threshold written as code, a command) and in: a date; a financial year; a year; the number of a heading; a reference to a section; the number of a stage of the pipeline; a name: a satellite, a report, a licence, a datum. Everything else that is a number came from a file.

*357 figures and 22 tables (699 cells) from 75 files; 241 statements tested; 153 totals compared. Written 2026-10-10T23:09:20Z by `scripts/write_decision_layer.py` (sha256 `6f2e4a749fc683da`), with the reading functions of `scripts/write_results.py` (sha256 `b918073042879cfc`).*
