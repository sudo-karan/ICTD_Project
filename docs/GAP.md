# Stage 4: forest condition, need and allocation, compared

*Written 2026-10-10T23:17:45Z by `scripts/write_gap.py`. No figure in this document was typed. Each was read by that script from
the file named for it in the last section, and each conclusion drawn from figures was tested against them before it was
written. The figures change only when the files do.*

## 1. What this is

The supervisor's question, in his words: "determine which areas have seen forest degradation, are also marginalised,
and have they seen good enough resource allocation in the past".

This stage sets three things beside one another that the earlier stages measured apart: where forest was lost
(stage 1, read through the decision table), who lives there (stage 2), and where the employment scheme's money went
(stage 3, and the scheme's own state report). It was built on 10 October 2026 as the project owner ruled it that day
(§2). Its tables are in `50_gap/` (the tables of districts were made 2026-10-10T20:20:22Z); `docs/RESULTS.md` and
`docs/DECISION_LAYER.md` describe what they are built from.

**It describes where money went relative to where forest was lost. It says nothing about why.** No figure here is an
effect of anything on anything, and the words that would claim one are used in this document only to say what the
analysis cannot show (§12).

Current allocation exists only by district, in the scheme's state report R6.20. So **the district is the unit of the
headline**: 30 districts, holding the 11,468 units of the earlier stages, 3,492 of them land
outside any revenue village. A history of units within districts is its companion (§9), and it can speak only of
works started by FY2017-18, where the geotagged record of works effectively ends.

How far it was checked: `scripts/verify_gap.py`, which imports nothing from the scripts that built the tables,
recomputed the figures of every table the stage's steps write, from the inputs: "338 of 338 checks passed". 42 deliberate
errors were then planted in copies of the stage's files, 29 files in all, and it caught 42
(§14, which also says what it does not hold).

## 2. The owner's decisions of 10 October 2026, and of 11 October 2026

These are his and are not this stage's to change.

- **Districts are the unit of the headline; the history of units is a companion, within districts.** Current
  allocation exists by district only.
- **Need is two things, never added.** N1 is a flow: the forest loss of a window of years, summed over the units in
  which loss is recorded. N2 is a stock: the standing open forest of the units the decision table calls candidates for
  assisted natural regeneration. Scheduled Tribe share and the development index **split** the comparison; they never
  weight it.
- **The comparison comes first and the models second.** The headline is a comparison of shares across districts
  (§5); the panel (§8) and the unit history (§9) follow it.
- **"What more is needed" is given three ways** (§7): in hectares, as an intensity of works, and as the same money
  distributed by need. **Rupees stay blank** until a VGPP rate is supplied.
- **Stage 4 runs in an environment of its own**, outside the repository and pinned in `requirements-stage4.txt`
  (`README.md`, its section on environments). The main environment, in which the earlier stages were built, is not
  changed by it (§14).
- **The text layer of the forest villages list is unverified**, and is used only if two checks hold: that what is
  parsed from it equals every total and running serial number the file prints, exactly; and that pages chosen at
  random, read by a reader, match the parsed rows. If either fails the step stops (§10).

On 11 October 2026 he added three things.

- **The need is read against the Forest Survey's own figures** (§11): the two sources set side by side, and no
  reason named for either.
- **H9 stays, as a sensitivity row**, read as a lead and not as a finding (§9).
- **The verifier's parts get one round of review, and no more** (§14).

## 3. Calls that are proposals

The owner can overrule each of these. The first eight came with his instruction for this stage, which marked them as
its own calls. The rest were made in the run, where the instruction left a choice or met something it had not foreseen.

**Calls of the instruction.**

- **The floor of the unit history is `100 ha` of forest at the start of the window** (§9), not `100 ha` of the land the
  agreement test compares. `50 ha` and `10 ha` are given beside it.
- **A district is left out whole for C7 and H4** (§5, §9). R6.20 cannot be split by zone, so a district goes with its
  need and its money together.
- **The lag of one year and the district-by-period fixed effects in P1** (§8).
- **`asinh` in P3 and H6**, so that a district-year or a unit with no money stays in.
- **Webb's weights** in the wild cluster bootstrap, as is usual with few clusters.
- **Terciles of the development index**, ten districts each.
- **A work with no start year counts as not started by FY2017-18**, as the decision layer counted it.
- **The development index of `2011` is taken out of the copy of the layer that is passed on**
  (`docs/DECISION_LAYER.md` §17.3). District-level results built from the index, here, are analysis and not the
  column; wherever they appear they carry the index's source and licence (§6).

**Calls made in the run.**

- **Which reading of the rule for C7.** The instruction gave two branches: a zone recorded for every unit, or only for
  the units the agreement test compared. Neither holds to the letter. A zone model is recorded for every unit that has
  land the CoRE Stack classes, and the units without one carry 0 ha of N1. So the first branch was used: a
  district is left out where units wholly under the East Coast model hold more than half of its N1, and a district
  with no N1 stays in. That leaves out Nayagarh, Khordha, Puri, Ganjam, Gajapati, and 25 districts stay. The other reading - every district that
  holds a unit the agreement headline left out - would leave out Baleshwar, Cuttack, Jajapur, Nayagarh, Khordha, Puri, Ganjam, Gajapati, and 22 would stay. It is computed
  too, as C7b, outside the comparisons fixed beforehand (§5).
- **The direction of the development index** is not stated in `docs/DATA_NOTES.md`. It was read from two documents of
  the repository (§6), and the index's columns are therefore in.
- **The index's source and licence line.** `docs/DATA_NOTES.md` gives a judgement about the index, not a line. The
  line carried here is the row of the layer's own list of sources, held against that document's sentence (§6).
- **Scheduled Caste terciles are in**: the need table carries the population.
- **H9 was run.** No table of stage 1 carries CoRE Stack's downward share as a column for each unit; it carries, for
  every unit, the hectares of the two classes the share is made of, on land with canopy above ten per cent in the year
  2000. The share was formed from them, for the units where the two classes are not both zero (§9).
- **The floors of the unit history are read on the hectares as the table carries them**, to four decimals; no unit
  lies in the last hundredth below a floor, so reading the figure as the map prints it would give the same samples.
- **The standard deviations the instruction quotes** (11.25 and 1.78 percentage points) are those with n in
  the divisor; with `n - 1` the first is 11.30.
- **How the bootstrap's p is reported** (§8): beside each interval, whether p fell steadily along the bracket.
- **How the owner's first check on the forest villages list was made into parts** (§10). His rule asks that what is
  parsed from the layer equal every total and running serial number the file prints. This stage reads the layer as
  `pdftotext` gives it and asks 6 things of it; what counts there as a row, a district's page and a serial
  number is this stage's, and is written out in `scripts/08_build_gap_rights.py`. The PDF was already on disk, fetched
  on 4 October 2026, and was not downloaded again.
- **The bracket of the bootstrap interval is doubled as a whole** (§8): one width for both sides, until p is below
  the level at both ends. That is the owner's sentence read to the letter. The first build of the models doubled each
  side on its own; the part of the verifier that was written from the definitions found the difference, and the
  builder was changed.
- **The totals of C12 are blank** in the table of comparisons: its need and its allocation are ratios, and thirty
  ratios added are a total of nothing.
- **In the table of the Forest Survey's figures** (§11) all the numbers of each row are kept, not only those the
  comparison uses; the two per cents are taken on the Survey's own forest cover; and two checks of the table against
  itself were added to the owner's (the three density classes add to the total; each printed per cent is the total
  over the calculated area).
- **The supervisor's comments are registered as an input** (§13): the owner's record of them, read word for word out
  of his note by a script, in a folder of its own in `00_raw/` with a manifest row, so that this document quotes them
  from a file and types none of it. The folder is new and is in git: the folder that holds the group's documents is
  not, and this record cannot be fetched again as those can.
- **One sentence of §10 rests on two figures this script works out itself**: the rank correlations of community
  extent and of N1 with the forest of the year 2000, from the table of districts. Neither has an interval and the
  verifier checks neither. The same holds for the two yearly means of forest loss in §8.

## 4. Definitions

All of it comes from tables already on disk. Nothing here was read from Earth Engine.

**Forest** is Hansen canopy above ten per cent in the year 2000: the two bands the decision table uses, dense (above
thirty) and open (ten to thirty). The band at or below ten decides nothing here either. Hectares are those the
decision table carries.

**Need, for each district.**

- **N1, the headline need**: forest loss in a window of years, summed over the units whose cell in that window is one
  of the three with loss recorded ("Open forest, loss recorded - restore"; "Closed forest, loss recorded - find the cause first"; "Little forest left, loss recorded - verify on the ground"). In the default window, the years 2018 to 2025, that is 89,657 ha
  in 1,734 units. All forest loss of the window, over every unit, is 90,028 ha; the difference,
  371 ha, is loss in units that lost less than the minimum of `1 ha`. 52.8 per cent of N1 lies on
  outside-village land.
- **N2**: the standing open-band hectares of the units whose cell in the default window is "Open forest, little or no loss recorded - assisted natural regeneration candidate":
  293,921 ha in 3,055 units. "Standing" is the forest of 2000 with no loss recorded since; not a measure of
  tree cover today. **N2 is a stock and N1 is a flow. They are never added.**
- Both are also given for LGD-unit land and for outside-village land apart.
- **Forest loss of 2001 to 2013**, every unit, both bands: 62,986 ha. It is loss before the state report begins,
  and it is used by one comparison (C4).

**Allocation, for each district.**

- **R6.20 plantation expenditure**: 151,843.18 lakh rupees over FY2014-15 to FY2017-18 ("pre") and 13,915.72 lakh
  over FY2018-19 to FY2025-26 ("post"): 20.22 and 0.38 per cent of all the scheme's expenditure
  in the two periods. **The four pre years are those whose tables carry the stamp 10/10/2020: a snapshot frozen in
  2020**, and that is said wherever "pre" appears. FY2026-27 is a part year (110.58 lakh so far); it is reported
  alone and enters no sum, no share and no model.
- **For context**, R6.20's natural-resource (NRM) and all expenditure of the same periods. They are compared with need
  only in the benchmark B1. NRM, water and plantation are nested categories: never added, never subtracted.
- **From the geotagged record of works ("the dump")**: expenditure on work types that name forest, on works started
  in or before FY2017-18, summed over the district's units: ₹134.6 crore in all; and the plantation category on the
  same basis, ₹1,899.3 crore. These are lifetime costs indexed by the year a work started, unlike R6.20, and are
  never put in a sum with it. A work with no start year counts as not started by then: ₹52,178 of
  forest-named money and ₹1,269,400 of plantation-category money, given by district beside each column;
  forest-named works started later carry ₹10.2 crore. **Left out**: the works that fall in no unit,
  ₹73.8 crore of all expenditure (₹1.8 crore of it forest-named), listed by the district of their file.

**Marginalisation, for each district**, on the census population of LGD panchayat units only (34,766,888 people,
25.6 per cent of them of the Scheduled Tribes). **Outside-village land has no census rows**, so none of
these columns knows anything of the land where most of N1 lies; that is said wherever they appear.

- **Scheduled Tribe share**, classed with the layer's own breaks.
- **The development index of 2011**: the mean over the district's LGD units that have a value, weighted by population
  (at least 90.6 per cent of a district's population is covered), in terciles of ten districts. Which way it
  runs is taken from two documents of the repository: `docs/NEED.md` ("ADI is the sum of five indicators each ranked 1–3, so it runs 5–15") and the group's data dictionary
  in `00_raw/docs/` ("rank each village at level-1 (low), level-2 (medium), or level-3 (advance) against these indicators"). A higher index is a more developed place. Its source and licence, as the layer's
  list of sources gives them: *Aggregate Development Index 2011: ICTD group, IIT Delhi, from Census 2011. Licence or terms: CC BY 4.0. Its documentation says SHRUG's keys were used to link 2001 and 2011 villages; the 2011 index itself is computed from Census 2011 rows.*
- **Scheduled Caste share**, in terciles of ten districts.
- The poverty rate stays out, as before.

## 5. The headline: C1, and what it does and does not rest on

**C1 asks: in the years plantation fell out of the scheme, did what was left go where forest was being lost?** Need is
N1 of the years 2018 to 2025 on all land; allocation is R6.20 plantation expenditure of FY2018-19 to FY2025-26.

**The finding, in volumes first.** 67.1 per cent of the state's N1 lies in 5 districts whose share of
the post-period plantation money is under half their share of the need (`r` below `0.5`): Kandhamal, Gajapati, Kalahandi, Koraput, Malkangiri. 66,060 ha
of N1, 74 per cent of it, lie in districts whose share of that money is below their share of the need (`r`
below `1`). At the other end 14 districts have more than twice their need share of the money (`r` above
`2`), and together they hold 1.9 per cent of the need. 5 districts have no N1 at all, so no `r`.

**The rank correlation is not read alone.** Across the 30 districts need and allocation rise together, and
not one for one: Spearman's rho is 0.67 (`95 %` interval 0.38 to 0.84, from 9,999 resamples of districts;
two-sided permutation p 0.00012, from 99,999 shuffles). Two figures stand beside it, and it means little without
them.

|  | need | allocation | Spearman's rho (interval) | permutation p |
|---|---|---|---|---|
| C1, the headline | N1, window 2018-2025, all land | R6.20 plantation, post (FY2018-19 to 2025-26) | 0.67 (0.38 to 0.84) | 0.00012 |
| B1, what district size alone gives | N1, 2018-2025 | R6.20 all expenditure, post | 0.57 (0.30 to 0.75) | 0.00103 |
| C12, with size taken out of both sides | N1 per 100 ha of the district's forest at window start | plantation as a share of the district's own expenditure, post | 0.37 (0.01 to 0.63) | 0.04570 |

*n = 30 districts in each row; the interval is a `95 %` percentile bootstrap over districts and p is from
shuffling allocation against need.*

- **B1 is what district size alone gives.** A large district has more of everything. B1 sets the same need against
  *all* the scheme's expenditure of the same years: rho 0.57 (0.30 to 0.75). C1's rho is above it, and the two
  intervals overlap: plantation money follows need across districts about as closely as the scheme's money as a whole
  does.
- **C12 takes size out of both sides**: N1 per `100 ha` of the district's forest, against plantation's share of the
  district's own expenditure. Its rho is 0.37 (0.01 to 0.63; p 0.046), and that interval
  lies just above zero. What is left of the association once size is out is much weaker than C1's figure suggests.
- **The same money distributed by need** would move 7,207.11 lakh rupees, 52 per cent of the post-period
  plantation money, from districts above their need share to districts below it. That is the sum of the positive
  gaps. It is the same money distributed by need; not a requirement.

The 8 districts with the most need hold 94.1 per cent of it:

| district | N1, ha | share of need, % | share of post-period plantation money, % | share of pre-period plantation money, % (frozen snapshot) | money share ÷ need share (`r`) | the same money distributed by need, less what it had, lakh | Scheduled Tribe class | tercile of the development index |
|---|---|---|---|---|---|---|---|---|
| Kandhamal | 26,688 | 29.8 | 3.8 | 6.1 | 0.13 | 3,615 | More than 50 % | lowest third of the index |
| Rayagada | 15,800 | 17.6 | 29.8 | 10.8 | 1.69 | −1,689 | More than 50 % | lowest third of the index |
| Gajapati | 12,163 | 13.6 | 3.7 | 3.8 | 0.27 | 1,371 | More than 50 % | lowest third of the index |
| Kalahandi | 9,654 | 10.8 | 4.6 | 3.8 | 0.43 | 851 | 18 to 33 % | lowest third of the index |
| Koraput | 7,729 | 8.6 | 3.5 | 3.0 | 0.40 | 718 | More than 50 % | lowest third of the index |
| Kendujhar | 4,442 | 5.0 | 3.0 | 5.3 | 0.60 | 277 | 33 to 50 % | middle third |
| Ganjam | 3,976 | 4.4 | 5.3 | 7.6 | 1.19 | −115 | Less than 18 % | highest third of the index |
| Malkangiri | 3,901 | 4.4 | 1.7 | 1.4 | 0.39 | 372 | More than 50 % | lowest third of the index |

*n = 30 districts in C1; these are the 8 with the largest N1. The classes of the last two columns rest
on the population of LGD panchayat units only. The gap is the same money distributed by need; not a requirement. The
pre-period years are a snapshot frozen on 10/10/2020. The index's source and licence are in §6.* Kandhamal has the most
need and under half its need share of the money; Rayagada, with the second most, has more than its share.

**The sensitivities**, fixed before any result was seen, with the one row that was not:

| comparison | need | allocation | districts | Spearman's rho (interval) | permutation p | need in districts with `r` below `0.5`, % | need in districts with `r` above `2`, % | sum of the positive gaps, lakh |
|---|---|---|---|---|---|---|---|---|
| C1 | N1, window 2018-2025, all land | R6.20 plantation, post (FY2018-19 to 2025-26) | 30 | 0.67 (0.38 to 0.84) | 0.00012 | 67.1 | 1.9 | 7,207 |
| C2 | N1, 2018-2025, LGD-unit land only | R6.20 plantation, post | 30 | 0.67 (0.39 to 0.84) | 0.00012 | 57.2 | 1.2 | 6,735 |
| C3 | N2 | R6.20 plantation, post | 30 | 0.12 (−0.27 to 0.47) | 0.53728 | 66.5 | 5.9 | 7,768 |
| C4 | total loss 2001-2013 | R6.20 plantation, pre (FY2014-15 to 2017-18; a frozen 2020 snapshot) | 30 | 0.76 (0.57 to 0.87) | 0.00001 | 53.7 | 7.6 | 74,755 |
| C5 | N1, 2018-2025 | R6.20 plantation, pre (a frozen 2020 snapshot) | 30 | 0.74 (0.53 to 0.86) | 0.00002 | 67.1 | 5.9 | 84,771 |
| C6 | N1, 2018-2025 | dump, forest-named, works started by FY2017-18 | 30 | 0.73 (0.49 to 0.86) | 0.00003 | 62.5 | 5.9 | 6,645 |
| C7 | N1, 2018-2025, East Coast districts left out | R6.20 plantation, post, the same districts left out | 25 | 0.67 (0.34 to 0.87) | 0.00046 | 65.7 | 1.7 | 6,303 |
| C7b (not fixed beforehand) | N1, 2018-2025, districts left out under the other reading of the rule | R6.20 plantation, post, the same districts left out | 22 | 0.68 (0.33 to 0.89) | 0.00073 | 65.8 | 1.5 | 5,741 |
| C8 | N1, window 2001-2025 | R6.20 plantation, post | 30 | 0.65 (0.38 to 0.82) | 0.00015 | 64.9 | 3.3 | 7,100 |
| C9 | N1, window 2017-2023 | R6.20 plantation, post | 30 | 0.66 (0.37 to 0.84) | 0.00006 | 67.9 | 1.6 | 7,350 |
| C10 | N1, window 2021-2025 | R6.20 plantation, post | 30 | 0.67 (0.38 to 0.85) | 0.00006 | 65.9 | 2.1 | 6,970 |
| C11 | N1, 2018-2025 | R6.20 plantation, FY2019-20 to 2025-26 | 30 | 0.45 (0.12 to 0.70) | 0.01247 | 73.8 | 19.3 | 4,165 |
| C12 | N1 per 100 ha of the district's forest at window start | plantation as a share of the district's own expenditure, post | 30 | 0.37 (0.01 to 0.63) | 0.04570 | - | - | - |
| B1 | N1, 2018-2025 | R6.20 all expenditure, post | 30 | 0.57 (0.30 to 0.75) | 0.00103 | - | - | - |

*n is the number of districts in each row. The interval is a `95 %` percentile bootstrap over districts; p is from
shuffling allocation against need. The last three columns do not apply to C12 (intensities) or B1 (a benchmark). The
gap is the same money distributed by need; not a requirement. Every "pre" row uses the four years whose tables are a
snapshot frozen on 10/10/2020.*

- **The window changes rho little** (C8 to C10): it runs from 0.65 to 0.67.
- **Leaving out the East Coast districts changes rho little** (C7: 0.67; under the other reading of its rule, C7b: 0.68). C7 is
  there for comparability with the agreement headline of `docs/RESULTS.md` §5, which leaves out the units wholly under
  CoRE Stack's East Coast zone model. The placebo that failed in that zone tested CoRE Stack's model against Hansen.
  It did not test Hansen alone, and nothing here says that Hansen's record is worse in those districts.
- **One year carries much of the post period.** FY2018-19 alone is 53 per cent of the post-period plantation
  money. Without it (C11) rho is 0.45 (0.12 to 0.70).
- **Land that panchayat planning can reach** (C2, N1 on LGD-unit land only): rho 0.67.
- **Open forest that could regenerate** (C3, N2): rho 0.12 (−0.27 to 0.47), an interval that includes zero.
  Post-period plantation money is not shown to follow the stock of standing open forest.
- **The old geography** (C4, C5, C6): money of the years before FY2018-19 gives a higher rho than C1 in each of the
  three, with an interval that overlaps C1's in each, so none is shown to differ from it: 0.76 against the loss of 2001 to 2013, 0.74 against N1, and 0.73 for the narrow forest-named
  measure of the geotagged record against N1. The pre-period years are a frozen snapshot, and the geotagged record's
  money is lifetime cost by the year a work started.

### 5.1 Why districts may be compared across the state here, when the layer never ranks units across it

The decision layer lists units within one district and never across the state. This stage compares districts across
the state. The two do not conflict. The layer's reason is about a ranking of units by a rate: for LGD panchayat units
at the agreement test's headline, the two measures of forest change are not shown to agree across the state
(`docs/DECISION_LAYER.md` §9), so an order of units across the state would rest on a comparison the analysis does not
establish. **Hectares of Hansen loss in a district are a measured quantity, not a ranking of units by a rate.**

How far that quantity was checked has to be said exactly. The dense band's state totals, for forest in 2000 and for
loss in 2001 to 2020, were held against Global Forest Watch's published figures (`docs/RESULTS.md` §3). **The open
band was not, and the years 2021 to 2025 were not.** District hectares also cannot tell plantation harvest from the
loss of natural forest, and nothing in this run tests that.

## 6. The comparison split by marginalisation

The classes below **split** the comparison. They are not weights, and no score is made of them. Each rests on the
Census of 2011 for LGD panchayat units only: **outside-village land has no census rows**, and 52.8 per cent of
N1 lies on it. A district's class describes the people the census counted there, not the land where its forest was lost.

**C1: need (N1 of the years 2018 to 2025) and post-period plantation money.**

By Scheduled Tribe share of the district's population:

| class | districts | share of need, % | share of allocation, % |
|---|---|---|---|
| Less than 18 % | 14 | 5.8 | 22.5 |
| 18 to 33 % | 3 | 10.8 | 11.9 |
| 33 to 50 % | 5 | 5.3 | 7.9 |
| More than 50 % | 8 | 78.1 | 57.7 |

By tercile of the development index of 2011 (a higher index is a more developed place):

| class | districts | share of need, % | share of allocation, % |
|---|---|---|---|
| lowest third of the index | 10 | 88.9 | 63.1 |
| middle third | 10 | 6.3 | 21.9 |
| highest third of the index | 10 | 4.8 | 15.0 |

By tercile of Scheduled Caste share:

| class | districts | share of need, % | share of allocation, % |
|---|---|---|---|
| lowest third of Scheduled Caste share | 10 | 79.1 | 63.4 |
| middle third | 10 | 16.2 | 24.0 |
| highest third of Scheduled Caste share | 10 | 4.7 | 12.6 |

*n = 30 districts in each of the three tables; a share is the sum of the shares of the class's districts, and
each column adds to a hundred. The development index: Aggregate Development Index 2011: ICTD group, IIT Delhi, from Census 2011. Licence or terms: CC BY 4.0. Its documentation says SHRUG's keys were used to link 2001 and 2011 villages; the 2011 index itself is computed from Census 2011 rows.*

The 8 districts in the class "More than 50 %" hold 78.1 per cent of the need and received
57.7 per cent of the post-period plantation money. The ten districts in the "lowest third of the index" hold
88.9 per cent of the need and received 63.1 per cent of the money. In both the larger part of the
money went where the larger part of the need is, and the share of the money is the smaller of the two.

**C4: forest loss of 2001 to 2013 and pre-period plantation money** (the four years frozen on 10/10/2020).

| class | districts | share of need, % | share of allocation, % |
|---|---|---|---|
| Less than 18 % | 14 | 7.9 | 27.2 |
| 18 to 33 % | 3 | 15.5 | 7.7 |
| 33 to 50 % | 5 | 6.1 | 10.1 |
| More than 50 % | 8 | 70.6 | 55.1 |

| class | districts | share of need, % | share of allocation, % |
|---|---|---|---|
| lowest third of the index | 10 | 85.7 | 59.6 |
| middle third | 10 | 9.0 | 23.9 |
| highest third of the index | 10 | 5.3 | 16.4 |

| class | districts | share of need, % | share of allocation, % |
|---|---|---|---|
| lowest third of Scheduled Caste share | 10 | 70.5 | 61.2 |
| middle third | 10 | 22.7 | 25.9 |
| highest third of Scheduled Caste share | 10 | 6.7 | 12.9 |

*n = 30 districts in each table. The development index: Aggregate Development Index 2011: ICTD group, IIT Delhi, from Census 2011. Licence or terms: CC BY 4.0. Its documentation says SHRUG's keys were used to link 2001 and 2011 villages; the 2011 index itself is computed from Census 2011 rows.*

In the years before FY2018-19 the districts of the class "More than 50 %" held 70.6 per cent of the earlier loss
and 55.1 per cent of the plantation money: a smaller share of the money than of the loss.

## 7. What more is needed

Three answers, none of them in rupees of need. All are for C1.

- **In hectares.** 66,060 ha of N1, 74 per cent of it, lie in districts whose share of the post-period
  plantation money is below their share of the need (`r` below `1`); 60,135 ha lie in districts where it is under
  half (`r` below `0.5`).
- **As an intensity of works.** For every `1,000 ha` of N1 the state report counts 637 plantation works, ongoing
  plus completed, in FY2016-17 (57,135 works) and 46 in FY2025-26 (4,105 works). This is an intensity,
  not a requirement: works have no standard size. The same figure is given for each district.
- **As the same money distributed by need** (§5): 7,207.11 lakh rupees would change districts. It is the same money
  distributed by need; not a requirement.

**The cost at the VGPP rate is blank.** The column is in the table and is empty in every row, with the reason:
"VGPP ₹/ha not in 00_raw". No rate was put in its place.

**For scale, not need.** Had plantation kept the share of all expenditure it had in the pre period, the post-period
total would have carried 743,148.16 lakh rupees of it (₹7,431.48 crore), against the 13,915.72 lakh actually
spent. That figure is the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier years are a frozen 2020 snapshot.

## 8. The district-year panel

30 districts by 13 financial years of R6.20 make 390 rows (`50_gap/district_year_panel.csv`); the
part year FY2026-27 is flagged and is in no model, which leaves 360 district-years. For each row: plantation, NRM,
water and all expenditure; plantation's share; plantation works; the report's stamp; forest loss of the calendar year
before and of the same year, for both bands and for the dense band alone; and the forest standing at the start of the
year before.

**What a coefficient asks.** Whether, within a district and within a period, years after more forest loss had more
plantation spending than that district's other years, beyond what all districts had in that year. It is not an
effect. Plantation is the scheme's label, and it is not specific to forest.

**Why the headline gives each district its own level in each period.** Plantation's share of district expenditure
varies far more before FY2018-19 than after: its standard deviation across district-years is 11.25 percentage
points before and 1.78 after. A model with only district and year fixed effects is therefore identified largely
by how far each district fell in 2018, set against loss that rose after 2018 (the state's loss in the year before,
which is the regressor, averages 8,099 ha over the pre period's years and 11,480 ha over the post period's);
it can show a relation that does not hold from year to year. P1 has district-by-period and financial-year fixed effects. P2, with plain district fixed
effects, is given for comparison and is read with that caveat.

**P1.** The coefficient is 0.226 (percentage points of the district's expenditure of the year per 100 ha of forest loss, dense plus open band, in calendar year t-1; CR1 standard error 0.214, for reference). Its interval is −0.065 to
0.893 and it includes zero (p 0.383).
Within a district and a period, years after more forest loss are not shown to have had more, or less, plantation
spending. P2's coefficient, −0.119 (−0.354 to 0.426), has the opposite sign.

| model | outcome | a unit of the regressor | district-years | coefficient | CR1 standard error (for reference) | coefficient (wild-bootstrap interval) | wild-bootstrap p | p climbs back, lower side | p climbs back, upper side | p at the lower end of the bracket | p at the upper end of the bracket |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 (the headline) | plantation_pct_of_all | 100 ha of forest loss, dense plus open band, in calendar year t-1 | 360 | 0.226 | 0.214 | 0.226 (−0.065 to 0.893) | 0.383 | no | no | 0.029 | 0.000 |
| P2 | plantation_pct_of_all | 100 ha of forest loss, dense plus open band, in calendar year t-1 | 360 | −0.119 | 0.118 | −0.119 (−0.354 to 0.426) | 0.333 | no | no | 0.003 | 0.002 |
| P3 | asinh_plantation_lakh | 100 ha of forest loss, dense plus open band, in calendar year t-1 | 360 | 0.063 | 0.076 | 0.063 (−0.140 to 0.276) | 0.541 | no | no | 0.039 | 0.001 |
| P4 | plantation_pct_of_all | 100 ha of forest loss, dense plus open band, in calendar year t | 360 | 0.088 | 0.107 | 0.088 (−0.158 to 0.309) | 0.422 | no | no | 0.021 | 0.003 |
| P5 | plantation_pct_of_all | percentage points of the forest standing at the start of year t-1, lost in year t-1 | 360 | 5.165 | 4.695 | 5.165 (−2.645 to 19.825) | 0.305 | no | no | 0.007 | 0.018 |
| P6 | plantation_pct_of_all | 100 ha of forest loss, dense band only, in calendar year t-1 | 360 | 0.298 | 0.286 | 0.298 (−0.072 to 1.308) | 0.287 | no | no | 0.043 | 0.005 |
| P7 | plantation_pct_of_all | 100 ha of forest loss, dense plus open band, in calendar year t-1 | 360 | 0.386 | 0.447 | 0.386 (−2.703 to 1.874) | 0.378 | yes | no | 0.033 | 0.002 |
| P7, the product with the post period | plantation_pct_of_all | 100 ha of forest loss, dense plus open band, in calendar year t-1, times the post period | 360 | −0.221 | 0.339 | −0.221 (−1.345 to 0.181) | 0.471 | no | yes | 0.015 | 0.031 |

*n = 360 district-years in every row, in 30 clusters, the districts. The CR1 standard error is for
reference only. The interval that counts is that of a restricted wild cluster bootstrap with Webb's weights and the
null imposed (the `wildboottest` package; 9,999 draws for P1 and 1,999 for the others), found by testing each value of
the coefficient in turn: the `95 %` interval is the set of values not rejected at `0.05`. P3's coefficient is in asinh
of lakh rupees, not in percentage points. The pre-period years are a snapshot frozen on 10/10/2020.*

**How the bootstrap's p behaved, which the last four columns record.** As the tested value moves away from the
estimate, the p of this bootstrap does not always go on falling: with 30 clusters of unequal weight it can
settle at a level, or climb back before it falls. The instruction's rule was applied as written: the bracket was
widened until p was below `0.05` at both ends, and the outermost crossing is the end of the interval. In 2 of the
8 rows p climbed back by more than `0.01` on one side (P7). At the outer end of a bracket p was at most
0.043; where it stands close to `0.05` there (P6), that end of the interval is weakly determined: a
different set of draws could put it elsewhere, or nowhere. For P1 the lower side settles at 0.029. Every grid of p
values is kept in `50_gap/panel_models_wcb_grids.json`.

## 9. The historical companion: units within districts

**The question.** In the same district, did units that had forest-named works by FY2017-18 lose a different share of
their forest in the years 2018 to 2025 than units that had none, given their forest and their earlier loss?

The exposure comes before the outcome. **Planners sited the works, so this is an association, and selection is
likely**: works may have gone to places already losing forest, or to places easy to reach. The control for earlier
loss speaks to part of that, not all. And a unit is a shape on a map, not the panchayat that recorded a work
(`README.md` §5.8): where a work was geotagged is not always where its panchayat lies.

**The sample of the headline** is every unit with `100 ha` or more of forest at the start of 2018: 2,889 units in
27 districts, 905 of them outside-village units, 1,121 with any forest-named expenditure on works started
by FY2017-18. The floor is set on forest at the start of the window, not on the land the agreement test compares
(§3). Their mean loss in the window is 2.08 per cent of that forest and the median 0.14. No unit lies in
the last half hundredth of a hectare below a floor (0), so the floor read on the figure as printed gives
the same samples.

**H1.** Outcome: the share of forest at the start of 2018 lost in the window, in per cent. Exposure: any forest-named
expenditure on works started by FY2017-18. Controls: the logarithm of forest at the start, the dense share of that
forest, the share of the forest of 2000 lost in 2001 to 2017, whether the unit is outside-village land, and a fixed
effect for every district. The coefficient is −0.14 (percentage points of the forest at the start of 2018 lost in 2018-2025, per a unit with any forest-named expenditure on works started by FY2017-18, against a unit with none), with an interval of −0.48 to 0.20 that includes
zero (p 0.379). Units with such works are not shown to have lost a different share of their forest than the other
units of their district.

| model | outcome | exposure | sample | units | exposed | districts | coefficient | CR1 standard error (for reference) | coefficient (wild-bootstrap interval) | wild-bootstrap p | p at the lower end of the bracket | p at the upper end of the bracket |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 (the headline) | forest_loss_share_pct | e1_any_forest_named | forest at the start of 2018 of 100 ha or more; every unit | 2,889 | 1,121 | 27 | −0.138 | 0.148 | −0.138 (−0.478 to 0.197) | 0.379 | 0.001 | 0.000 |
| H2 | forest_loss_share_pct | e1_any_forest_named | forest at the start of 2018 of 50 ha or more; every unit | 3,739 | 1,330 | 30 | −0.177 | 0.162 | −0.177 (−0.533 to 0.173) | 0.312 | 0.000 | 0.000 |
| H3 | forest_loss_share_pct | e1_any_forest_named | forest at the start of 2018 of 10 ha or more; every unit | 5,808 | 1,803 | 30 | −0.138 | 0.130 | −0.138 (−0.430 to 0.166) | 0.329 | 0.001 | 0.001 |
| H4 | forest_loss_share_pct | e1_any_forest_named | forest at the start of 2018 of 100 ha or more; units outside the districts C7 leaves out | 2,383 | 878 | 22 | −0.018 | 0.141 | −0.018 (−0.369 to 0.270) | 0.902 | 0.002 | 0.001 |
| H5 | forest_loss_share_pct | e1_any_forest_named | forest at the start of 2018 of 100 ha or more; LGD panchayat units only; complete cases | 1,936 | 876 | 27 | −0.177 | 0.167 | −0.177 (−0.547 to 0.164) | 0.316 | 0.002 | 0.000 |
| H6 | forest_loss_share_pct | e2_asinh_forest_named_inr_per_ha | forest at the start of 2018 of 100 ha or more; every unit | 2,889 | 1,121 | 27 | −0.018 | 0.022 | −0.018 (−0.066 to 0.032) | 0.416 | 0.001 | 0.000 |
| H7 | forest_loss_share_pct | e3_any_plantation_category | forest at the start of 2018 of 100 ha or more; every unit | 2,889 | 2,334 | 27 | −0.192 | 0.261 | −0.192 (−0.848 to 0.327) | 0.524 | 0.005 | 0.000 |
| H8 | loss_recorded | e1_any_forest_named | forest at the start of 2018 of 100 ha or more; every unit | 2,889 | 1,121 | 27 | −0.042 | 0.021 | −0.042 (−0.090 to 0.002) | 0.062 | 0.003 | 0.000 |
| H9 | downward_share_pct | e1_any_forest_named | forest at the start of 2018 of 100 ha or more; every unit; complete cases | 2,889 | 1,121 | 27 | −3.880 | 1.060 | −3.880 (−6.075 to −1.649) | 0.003 | 0.001 | 0.002 |

*n is the number of units in each row; clusters are the districts in the row's sample. The CR1 standard error is for
reference only; the interval is that of the restricted wild cluster bootstrap described in §8 (9,999 draws for H1,
1,999 for the others). H6's coefficient is per unit of asinh of rupees per hectare, not a percentage; H8 is a linear
probability model, its coefficient a difference in probability; H9's outcome is CoRE Stack's downward share, degradation
over degradation plus improvement, never the degradation class alone, formed for 2,889 units of H1's sample in which
the two classes are not both zero. H4 leaves out the units of the districts C7 leaves out, for comparability with the
agreement headline. H5 is LGD panchayat units only.*

The interval includes zero in 8 of the 9 models. In H9 the interval does not include zero; it is one of several sensitivities, read beside the headline and not in its place.

**H9 is a lead, not a finding.** The owner keeps it as a sensitivity row (§2). It is to be read with four things.

- **It uses a different measure from H1's.** H1's outcome is Hansen's loss. H9's is CoRE Stack's downward share: the
  degradation class over degradation plus improvement.
- **The caveats on CoRE Stack's classes apply** (`docs/RESULTS.md` §4). They rest on classifiers their makers report
  as right about two times in three. And they compare the years around 2016 to 2019 with those around 2022 to 2025,
  so the first of the two periods overlaps the years in which the works were started: the outcome does not come
  cleanly after the exposure.
- **Its share was formed in this run, from two classes.** No table of stage 1 carries the downward share for each
  unit. It was made here from the hectares of the degradation class and of the improvement class, for the 2,889
  units of H1's sample in which the two are not both zero (§3).
- **A strict reading of the owner's instruction drops it.** The instruction said to run H9 only if stage 1 carries
  the downward share for each unit, and the run's own note says that, read to the letter, H9 is the row to drop
  (`docs/stage4_run_log.md`, in its notes on the unit history).

A unit with works and a lower downward share is described by that sentence; nothing is shown about what the works
did. At the outer end of a bracket p was at most 0.005; rows in which p climbed back on a side: none. The
grids are in `50_gap/unit_history_models_wcb_grids.json`.

## 10. Forest rights, at the level the data allow

**By district.** The state's monthly progress report on the Forest Rights Act, as on 31 December 2025, joined on the
census district code: 9,432 community titles distributed (Scheduled Tribes and other traditional forest
dwellers together) over 331,568 ha. 6 districts have distributed none: Sundargarh, Bhadrak, Kendrapara, Jagatsinghapur, Khordha, Puri.

For each district the table gives the community extent as a per cent of the district's forest of 2000 (both bands).
That figure is "not an overlap: titles are not mapped, and 'community' lumps CR with CFR". Titles are not mapped anywhere in this repository, and the report's "community" is
community rights and community forest resource rights together. In 1 district (Baleshwar) the ratio is
above a hundred, which a share of forest could not be.

Two rank correlations over the 30 districts, computed as in §5:

- **R1**, community extent against N1 of the years 2018 to 2025: rho 0.42 (0.08 to 0.68; p 0.021), an
  interval that lies above zero. Both are larger in districts with more forest (below).
- **R2**, community extent per hectare of the forest of 2000 against N1 per hectare of forest at the start of the
  window: rho 0.15 (−0.24 to 0.50; p 0.436), an interval that includes zero. With size taken out, districts
  where more forest land is under a community title are not shown to be those that lost more of their forest, or less.

**The two are read together.** R1's rank correlation does not survive per hectare: R2's interval includes zero. What
that leaves is size. Community-title extent tracks how much forest a district has: over the same 30
districts its rank correlation with the forest of the year 2000 is 0.53, and N1's is 0.83 (both
worked out by this script from the table of districts; no interval was computed for either, and the verifier does
not check them). So R1 says that districts with more forest tend to have both more titled land and more loss, and
nothing about titles and loss beyond that.

**The two reports of the same date disagree.** This document cites the state's figures. Odisha's row of the national
report of the Ministry of Tribal Affairs, as on the same day, gives 9,352 community titles and 327,099 ha.
The state's report has 80 more titles and 4,469 ha more, 1.35 per cent of its own figure.

**The forest villages list.** The manifest has listed the ST & SC Development Department's "List of Forest Villages,
Old Habitations or Settlements & Unsurveyed Villages" since 4 October 2026, and it had not been opened. It was already
on disk (`00_raw/01_cfr_fra/`, 4,506,869 bytes, `sha256` beginning `6a7a4657b15b7afd`) and is registered with a manifest row
of its own that gives its exact size and hash; the row that lists its address is as it was. It is a scan: 64
pages, each one image at 100 pixels per inch. The only text in the file is a layer made by someone else's
character recognition (OmniPageCSDK18, in HP Smart Document Scan Software 3 3.10).

*The owner's rule for that layer (10 October 2026).* It is unverified, and is used only if two checks hold. (a) The
district counts parsed from it equal every total and running serial number the file prints, exactly. (b) At least five
pages chosen at random, rendered upright and read by a reader, match the parsed rows row for row. If either fails,
the step records the page count, the layer and which check failed, and stops.

**Check (a) fails, in every part this stage made of it.** The layer gives 25 districts, each a page of totals
followed by a list of villages with running serial numbers, and before them a summary page with a row for each.

| part of check (a) | what it asks of the layer | holds in | of |
|---|---|---|---|
| a1 | every row of the summary page adds up | 24 | 25 |
| a2 | a total row of the summary page is read, and each of its three numbers is the sum of its column | 0 | 1 |
| a3 | every district page gives its three numbers, and they add up | 23 | 25 |
| a4 | every district page's three numbers are those of a row of the summary page | 22 | 25 |
| a5 | every district's rows with a village code number what its page prints for the "ZERO" area | 21 | 25 |
| a6 | every district's serial numbers are exactly 1 to that count | 18 | 25 |

*The layer is read as `pdftotext` gives it, a page at a time; the rule for what counts as a row, a district's page
and a serial number is in `scripts/08_build_gap_rights.py`, and the table of districts as the layer reads them is
`50_gap/forest_villages_districts_as_the_layer_reads_them.csv`. In one district the list is numbered block by block,
which this stage's rule for serial numbers does not follow.*

On the summary page 24 of 25 rows add up and one does not ("t---StffitinWrh 1677=--- 46 -- 1745"); no total row can be read from the
layer. A note recorded with the check, which is one reader's and no part of either check: "The summary page, rendered at its own orientation, was read once by the session that wrote this step (10 October 2026). On the page every row is legible and the third row's total is printed plainly and equals its two parts: the row that fails here is a misreading by the layer, not an error of the print. Under the table the page carries the totals of the three columns written by hand, which the layer does not hold. This is one page, not chosen at random: it is not check (b)."

**Check (b) was not run**: the rule stops the step at the first check that fails. So **no count was taken from the
file, and none is in the table of districts**. No character recognition was run in this stage, and the list is not
matched to units.

## 11. The need read against the Forest Survey's own figures

*Added on 11 October 2026, by the owner's instruction.* N1 sits mostly in a few districts: Kandhamal, Rayagada, Gajapati, Kalahandi, Koraput, 5
of the 30, hold 80 per cent of it. This section sets beside each district's N1 what the Forest Survey of India reports for the
same district. It names no reason for either figure, and nothing in it is an account of why forest was lost.

**What each source measures.**

- **Hansen**, from which N1 is made: gross, stand-replacing loss of tree cover, year by year, on land with canopy
  above ten per cent in the year 2000. N1 is that loss summed over the years 2018 to 2025 in the units where loss is
  recorded (§4).
- **The Forest Survey**: Table 10.20.3, District-wise Forest Cover in Odisha (India State of Forest Report 2023, Volume II). For each district it gives the forest cover of its assessment of 2023, the
  change in that cover with respect to its assessment of 2021, and the area of scrub, in square kilometres. The
  change is a net figure between two assessments. Forest cover, in the report's own words, is "all lands, more than one hectare with a tree canopy density of more than or equal to 10% irrespective of ownership, legal status and land use. Such lands may not necessarily be a recorded forest area. It also includes orchards, bamboo and palm". So an
  orchard or a plantation of that size and canopy is forest cover, whatever the land is used for. The report says the
  mapping was done "using Indian remote sensing satellite data (IRS-LISS III sensor with 23.5 m resolution)", that "The data period of the satellite used for this assessment is in general October 2021 to December 2021", and that it gives "changes in forest cover in respect of the previous assessment of 2021". That is other imagery than
  Hansen's, read by another method. The pages of the report registered here that carry its definitions do not define
  scrub.

**They are not the same quantity, and neither can be subtracted from the other.** One is a gross loss added up over
eight years on the forest of the year 2000. The other is a net change between two assessments, in which a loss in one
place is set off by a gain in another, on another definition of forest and from other imagery. For the state as a
whole N1 is 897 km² of gross loss, and the Survey's change is 151.89 km², a rise; its forest
cover is 52,434 km² and its scrub 4,633 km².

**Side by side**, for the 8 districts with the most N1:

| district | N1, ha | N1, km² | N1 per `100 ha` of forest at the start of the window | Forest Survey: forest cover, km² | Forest Survey: change with respect to its earlier assessment, km² | that change, % of its forest cover | Forest Survey: scrub, km² | scrub, % of its forest cover |
|---|---|---|---|---|---|---|---|---|
| Kandhamal | 26,688 | 266.9 | 5.34 | 5,402 | −2.70 | −0.05 | 441 | 8.2 |
| Rayagada | 15,800 | 158.0 | 5.63 | 3,286 | 5.17 | 0.16 | 606 | 18.5 |
| Gajapati | 12,163 | 121.6 | 5.82 | 2,499 | −11.63 | −0.47 | 213 | 8.5 |
| Kalahandi | 9,654 | 96.5 | 4.96 | 2,377 | −61.94 | −2.61 | 403 | 16.9 |
| Koraput | 7,729 | 77.3 | 4.81 | 2,095 | 25.86 | 1.23 | 1,397 | 66.7 |
| Kendujhar | 4,442 | 44.4 | 2.30 | 3,189 | −30.92 | −0.97 | 86 | 2.7 |
| Ganjam | 3,976 | 39.8 | 1.93 | 2,416 | 169.18 | 7.00 | 453 | 18.7 |
| Malkangiri | 3,901 | 39.0 | 2.51 | 2,312 | −12.34 | −0.53 | 59 | 2.6 |

*n = 30 districts in `50_gap/fsi_district_check.csv`; these are the 8 with the largest N1. The
Forest Survey's columns are as its table prints them, and each column that can be added, summed over the
30 districts, equals the table's own printed total. Source: Forest Survey of India, India State of Forest
Report of 2023; © Forest Survey of India, whose report allows the use of its contents for non-commercial purposes
with acknowledgment.*

In 3 of the 5 districts with the most N1 the Survey's change is, in size, under a tenth of N1; in
3 of the 5 it is a fall and in 2 a rise. In Kandhamal, which has the most N1, N1 is
267 km² and the Survey's change −2.70 km². Across the state 12 of the 30 districts
show a fall. The same 5 districts hold 66 per cent of the state's scrub.

**What the four rank correlations show**, over the 30 districts, each computed as in §5:

|  | what is set against what | Spearman's rho (interval) | permutation p | size taken out of both sides |
|---|---|---|---|---|
| (a) | N1 of 2018-2025 (ha) against the Forest Survey's change in forest cover with respect to 2021 (km2) | −0.20 (−0.54 to 0.22) | 0.29484 | no |
| (b) | N1 of 2018-2025 (ha) against the Forest Survey's scrub (km2) | 0.81 (0.60 to 0.92) | 0.00001 | no |
| (c) | N1 per 100 ha of forest at the start of 2018 against the Forest Survey's change as a per cent of its forest cover | −0.21 (−0.54 to 0.20) | 0.25816 | yes |
| (d) | N1 per 100 ha of forest at the start of 2018 against the Forest Survey's scrub as a per cent of its forest cover | 0.58 (0.27 to 0.79) | 0.00094 | yes |

*The interval is a `95 %` percentile bootstrap over districts; p is from shuffling one side against the other. In (c)
and (d) both sides are divided by the district's own forest, as in C12.*

- **Gross loss and net change are not shown to go together across districts.** N1 against the Survey's change: rho −0.20
  (−0.54 to 0.22; p 0.295), an interval that includes zero. With size taken out of both sides: −0.21
  (−0.54 to 0.20; p 0.258), which includes zero too. Districts where Hansen records more loss are not shown to
  be those where the Survey reports a larger fall in forest cover, or a larger rise.
- **Gross loss and scrub do go together across districts.** N1 against the Survey's scrub: rho 0.81 (0.60 to 0.92;
  p 0.00001), an interval that lies above zero. With size taken out of both sides it is lower and still above zero:
  0.58 (0.27 to 0.79; p 0.00094). Districts with more N1, and with more N1 for the forest they have, tend
  to be districts where the Survey maps more scrub, and more scrub for its forest cover. These are ranks across
  districts at one time; they say nothing of how either figure moved over the years.

**Readings this run cannot test.** One reading of much gross loss beside little net change is rotational clearing,
in which trees are cut and the land comes back under cover: shifting cultivation is one such practice, and the
harvest and replanting of plantations another. They are named here only as readings this run cannot test. Nothing in these tables tells one from another, or from a difference in what the two sources see: the
definitions differ, the imagery differs, and the periods differ (N1 is of 2018 to 2025; the Survey's change lies
between two of its assessments). The scrub figure is a stock at one assessment and says nothing of when or how the
land came to be scrub.

## 12. What this cannot show

- **Cause.** Nothing here shows why forest was lost, why money went where it went, or what money did. A district with a
  small share of the money and a large share of the loss is described by that sentence and by nothing stronger. The
  words "because", "led to", "effect of", "caused" and "drove" are in this document only where it says so.
- **Current allocation at any level finer than a district.** The state report gives districts. The geotagged record,
  which gives places, effectively ends with works started in FY2017-18.
- **Plantation is not forest-specific.** It is the scheme's label and holds horticulture alongside forestry: mango
  orchards and avenue plantations are among its works in the geotagged record (`README.md` §5). The narrow
  forest-named measure exists only in that record, for the earlier years.
- **The pre years are a frozen snapshot.** The four tables of FY2014-15 to FY2017-18 carry the stamp 10/10/2020 and
  have not been rewritten since.
- **R6.20 from FY2020-21 on is restated continuously, so this is a dated copy.** Those tables carry the stamps
  03/10/2026 and 04/10/2026: the figures are what the report said on those days.
- **Hansen loss is not degradation and does not see thinning.** It is the removal of tree cover from any reason,
  in plantation and natural forest alike; gain is not netted off. The provider's own help text, registered on
  10 October 2026, says: "“Tree cover loss” refers to the removal or mortality of tree cover and can be due to a variety of factors, including mechanical harvesting, fire, disease or storm damage. As such, “loss” does not equate to deforestation." Of its accuracy: "Specifically, sub-tropical areas have the lowest accuracies (around 20% for commission and omission errors)." "The model often misses disturbances in smallholder landscapes, resulting in lower accuracy of the data in locations such as sub-Saharan Africa, where this type of disturbance is more common." And of its
  method, which has changed over the years: "For example, in 2015, the integration of Landsat 8 satellite data and updates to the loss detection algorithm from UMD resulted in better capturing of small-scale loss." The open
  band's rise after 2018 may be on the ground or in the producers' method; that is not established
  (`docs/DECISION_LAYER.md` §18), and P6 is there for that reason.
- **The need on outside-village land.** 52.8 per cent of N1 lies on land outside any revenue village. No
  panchayat plan reaches it: that is the owner's sentence, and what the tables show of it is that the land lies in
  no panchayat unit of the layer. The census has no row for it: every column of marginalisation here is silent
  about the land where most of the loss is.
- **A requirement.** The gap is the same money distributed by need; not a requirement.
- **A cost.** Nothing can be costed until a sourced rate is supplied. The VGPP rate is not in `00_raw/`. One possible
  source is the district schedule of rates that CLART uses; it is not in `00_raw/` either.
- **What the canopy is made of.** Every measure here that rests on canopy counts whatever meets its threshold as
  forest. Invasive cover, for example Lantana or Prosopis, counts as forest wherever it does.
- **Tree species.** They are not known: no input here names one, and no measure here tells a plantation from a
  natural forest.
- **Every limit of the measurements carries over** (`docs/RESULTS.md` §12): the unit is a geometry and not a
  jurisdiction; the canopy bands are fixed at the year 2000; the census is that of 2011.

## 13. What this answers of the supervisor's comments

The comments are quoted as the project owner recorded them and gave them on 11 October 2026 (`00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json`, registered in
the manifest). The record is his; it is not the supervisor's own text. Each point is taken in turn: what in this
stage answers it, by section and figure, and what does not.

**After the proposal deck.**

- "1. Design an analysis framework for social-ecological need identification and quantification vs. resource allocation done so far, and what more is needed." **Answered here by** the framework of this stage: §4 (need as N1 and N2, never added; marginalisation as
  a split, never a weight), §5 with figure `F4` (need against allocation, district by district), §6 with figure `F5`
  (the comparison split by Scheduled Tribe share and by the development index) and §7 (what more is needed: in
  hectares, as an intensity of works, and as the same money distributed by need). Figure `F1` is the allocation done
  so far, in the state report. **Not answered:** what more is needed in rupees. The cost stays blank (§7, §12).
- "2. Look at Commons Connect and Shivani's paper in detail…" **Not a question this stage answers.** How the layer was matched to Commons Connect is in
  `docs/LAYER.md` and `docs/DECISION_LAYER.md`. The paper named is not in this repository, and no stage reads it.
- "3. Explore access to data dumps of MGNREGA, CFR granted villages and boundaries, understand ATREE data carefully." **Answered in the earlier stages, and used here.** The geotagged record of MGNREGA works and the state
  report R6.20 are stage 3 (`docs/RESULTS.md` §8; figures `F1` and `F2` here). ATREE's list of villages with potential
  for community forest rights is the basis of the forest-dependent households of stage 2 (`docs/NEED.md`); no step of
  this stage reads it. **Not answered:** the villages granted community forest rights, and their boundaries. No file
  in `00_raw/` maps them for Odisha: the manifest notes that the one public map of recognised villages has layers
  for two other states only. This stage has the state's district table of community titles and nothing finer (§10).

**After the methodology deck.**

- "1. Overall methodology not clear; what info is extracted from CFR docs and how it is being related to satellite data" **Answered by saying what is done and what is not.** Nothing is extracted from documents on community
  forest rights at the level of a village. The state's district table of community titles is set beside need (§10);
  titles are not mapped, so nothing is related to satellite data below the district. The method of the stage is §4
  to §9, and the last section gives the file of every figure.
- "2. Why not simply determine which areas have seen forest degradation, are also marginalized, and have they seen good enough resource allocation in the past" **This stage is that question, asked of districts**: where forest loss is recorded (§4; figure `F3`),
  who lives there (§6; figure `F5`), and where the scheme's money went (§5; figures `F1` and `F4`). For the years the
  geotagged record covers it is also asked of units within a district (§9; figure `F6`). **Not answered:** whether
  the allocation was "good enough". No requirement is set here, and none can be until a rate is supplied (§7).

**Not answered, plainly.** Community forest rights village by village: titles are not mapped (§10). Tree species:
no input names one (§12). Costing: no sourced rate is in `00_raw/` (§7, §12).

## 14. How it was verified

- **Gates.** Every step with an expected value stops the build if the value found differs: 120 gates across the
  seven steps that carry them (the two environments, the inputs, the districts, the panel, the unit history, forest
  rights and the Forest Survey's figures), each written to a table in `50_gap/` and to `docs/stage4_run_log.md`. No
  expected value and no tolerance was changed to pass one.
- **Independent recomputation.** `scripts/verify_gap.py` imports nothing from the builders. It is made of 10
  parts. 7 of them were written by agents from the builders' written definitions, not from their code;
  the other 3, small ones that hold a derived file against the table it is cut from or the environment
  against its pins, are the session's own. It recomputes the figures of every table the stage's steps write, from the
  inputs: "338 of 338 checks passed". Sums are exact. A permutation p and a bootstrap interval of a rank correlation are recomputed
  twice: with the verifier's own draws, to a stated tolerance, and with the recorded seeds, to the digit, on a
  stated reading of how the random generator is called. For the models it recomputes each coefficient and CR1
  standard error in numpy, recomputes the wild-bootstrap p with its own code and its own draws, and tests both ends
  of every interval with the package and the recorded seed.
- **The review of the verifier: one round, as the owner ruled.** 9 of the 10 parts each went to an
  agent that had not written it, which tried the part with planted errors and mended the checks that let one
  through. The part on the Forest Survey's figures was written in that round and tried by its own writer; no second
  agent has reviewed it. In the round 213 errors were planted in copies of the tables, and the part
  concerned caught 209; the 4 it did not are named in `docs/stage4_run_log.md`, with what each
  was. The reviewers reported 3 disagreements, which the run log gives. All were put right in the builders'
  written definitions; the steps concerned were run again, and all 22 tables of figures are byte for byte
  what they were (`50_gap/gates_step3.csv`). A last reader then went through
  every part for columns that no check reads. By its reading, every column of the tables is read by some check;
  labels, notes and reasons are held by key words and not word for word; and 6 descriptions or check
  names claimed more than the code tests, which the session then reworded or closed, bar one that cannot be: the
  owner's expected values are typed into the verifier from his instructions, and no file carries them for a check
  to read. After the round the session changed 5 of the script's 12 pieces, with no agent to
  review the changes; the run log names them. What each part assumes and what it does not cover are in the run log
  too.
- **Deliberate errors.** 42 errors were planted, one at a time, in copies of the stage's files: every table,
  the two text files of the models, the provenance record and the record of the check of the forest villages PDF,
  29 files in all. The verifier caught 42. Their kinds:
  a check reported as passed; a count altered to pass a check; a district in the wrong class; a dropped East Coast exclusion; a figure altered; a method misnamed; a missing start year counted as early; a model under another's name; a need without its cell filter; a package stage 4 added, in the main environment; a part-year leak into a sum; a rounded ratio used where the exact one belongs; a rounding rule broken; a shifted lag; a sign lost; a step recorded as built by other code; a step run in the wrong environment; a sum of the wrong terms; a swapped district code; a unit in the wrong district; a wrong denominator; a wrong unit; an exposure miscoded; an interval from another method; an order not kept; another statistic under the same name; columns exchanged. The record is
  `50_gap/verify_gap_trials.json`.
- **The earlier verifiers**, run by this script as it wrote the document: `scripts/verify_r620.py`: "passed";
  `scripts/verify_layer.py`: "92 of 92 checks passed"; `scripts/verify_decision.py`: "62 of 62 checks passed". The gate on the copy of the layer
  that is passed on: 8 of 8 steps.
- **Seeds and versions.** Every random draw is seeded from one base, `20261010`; each table carries its own seeds. The
  packages: python 3.12.13; numpy 2.3.5; pandas 3.0.6; scipy 1.18.1; statsmodels 0.15.0; numba 0.62.1; wildboottest 0.3.2. `50_gap/gap.provenance.json` has every input's `SHA-256`, the seeds and the run times.
- **The environment.** Every step ran with an interpreter that held exactly the 29 packages
  `requirements-stage4.txt` pins, and stopped otherwise; the record lists them at every step. The main environment's
  `numpy` is 2.5.3, the version the earlier stages' provenance records show, and the earlier verifiers were run
  there. `50_gap/gates_environment.csv` has the 11 gates on the two environments.
- **The figures** (`figures/stage4/`) are drawn from these tables by a script that measures its own layout. Each of
  the 6 images was also opened and looked at (2026-10-10T18:38:40Z), and the images on disk are those: the record,
  `50_gap/figures_looked_at.json`, holds the `SHA-256` of each. The verifier does not check the figures.
- **Not done.** No second, independent team has looked at the design.

## 15. To rebuild

```
python3.12 -m venv ~/.venvs/ictd-stage4      # once: stage 4's own environment, outside the repository
PY=~/.venvs/ictd-stage4/bin/python
$PY -m pip install --only-binary=:all: -r requirements-stage4.txt
$PY scripts/08_gap_environment.py         # the gate on the two environments
$PY scripts/08_gap_inputs.py              # the inputs, the crosswalk, a district for every unit, the gates
$PY scripts/08_build_gap_districts.py     # need, allocation, the comparisons, the splits, what more is needed
$PY scripts/08_build_gap_panel.py         # the district-year panel and its models (about ten minutes)
$PY scripts/08_build_gap_units.py         # the unit history and its models (about an hour)
$PY scripts/08_build_gap_rights.py        # forest rights by district; the check of the forest villages PDF
$PY scripts/08_build_gap_fsi.py           # the need beside the Forest Survey's district figures
$PY scripts/08_build_gap_deck_tables.py   # three tables for the deck
$PY scripts/verify_gap.py                 # the independent check
$PY scripts/verify_gap_trials.py          # deliberate errors against it
$PY scripts/make_stage4_figures.py        # the figures
$PY scripts/write_gap.py                  # this document
```

The tables of `50_gap/` and the figures are not in git; the scripts and this document are.

## 16. Where every figure comes from

This section is the script's own record of what it read. Paths are relative to the repository. `50_gap/` is this stage's output and the other numbered folders are the outputs of the stages before it: each is rebuilt by the script named in the provenance record beside it, and none is in git.

### 16.1 Figures in the text, in the order they first appear

| as printed | file | where in the file |
|---|---|---|
| 2026-10-10T23:17:45Z | this run | the UTC time at which this script ran |
| 2026-10-10T20:20:22Z | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `run_utc` |
| 30 | `50_gap/district_need.csv` | rows counted by this script: its rows |
| 11,468 | `50_gap/district_need.csv` | worked out by this script from its rows: `n_units` summed |
| 3,492 | `50_gap/district_need.csv` | worked out by this script from its rows: `n_units_outside` summed |
| 338 of 338 checks passed | `scripts/verify_gap.py` | its exit status and last line, run by this script as it wrote the document |
| 42 | `50_gap/verify_gap_trials.json` | key `trials`: their number |
| 29 | `50_gap/verify_gap_trials.json` | key `trials`: the distinct files the errors were planted in |
| 42 | `50_gap/verify_gap_trials.json` | key `trials`: those with `caught` true |
| 0 | `50_gap/district_need.csv` | worked out by this script from its rows: `n1_ha_2018_2025_in_units_with_no_zone` summed |
| Nayagarh, Khordha, Puri, Ganjam, Gajapati | `50_gap/need_vs_allocation_summary.csv` | column `districts_left_out`; row where `comparison` is 'C7' |
| 25 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts`; row where `comparison` is 'C7' |
| Baleshwar, Cuttack, Jajapur, Nayagarh, Khordha, Puri, Ganjam, Gajapati | `50_gap/need_vs_allocation_summary.csv` | column `districts_left_out`; row where `comparison` is 'C7b' |
| 22 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts`; row where `comparison` is 'C7b' |
| 11.25 | `50_gap/district_year_panel.csv` | worked out by this script from its rows: the standard deviation (n in the divisor) of `plantation_pct_of_all` over the rows whose `period` is pre |
| 1.78 | `50_gap/district_year_panel.csv` | worked out by this script from its rows: the same over the rows whose `period` is post |
| 11.30 | `50_gap/district_year_panel.csv` | worked out by this script from its rows: the same over pre, with n - 1 in the divisor |
| 6 | `50_gap/forest_villages_pdf_record.json` | key `check_a` → `parts`: their number |
| "Open forest, loss recorded - restore"; "Closed forest, loss recorded - find the cause first"; "Little forest left, loss recorded - verify on the ground" | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `cell_names`: the three cells with loss recorded |
| 89,657 | `50_gap/district_need.csv` | worked out by this script from its rows: `n1_ha_2018_2025` summed |
| 1,734 | `50_gap/district_need.csv` | worked out by this script from its rows: `n_units_loss_cells_2018_2025` summed |
| 90,028 | `50_gap/district_need.csv` | worked out by this script from its rows: `forest_loss_ha_2018_2025_all_units` summed |
| 371 | `50_gap/district_need.csv` | worked out by this script from its rows: `loss_below_minimum_ha_2018_2025` summed |
| 52.8 | `50_gap/district_need.csv` | computed here: N1 on outside-village land ÷ N1 × 100. From: worked out by this script from its rows: `n1_ha_2018_2025_outside` summed; worked out by this script from its rows: `n1_ha_2018_2025` summed |
| "Open forest, little or no loss recorded - assisted natural regeneration candidate" | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `cell_names` → `open_none` |
| 293,921 | `50_gap/district_need.csv` | worked out by this script from its rows: `n2_ha` summed |
| 3,055 | `50_gap/district_need.csv` | worked out by this script from its rows: `n_units_anr` summed |
| 62,986 | `50_gap/district_need.csv` | worked out by this script from its rows: `loss_2001_2013_ha` summed |
| 151,843.18 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `r620_plantation_pre_lakh` summed |
| 13,915.72 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `r620_plantation_post_lakh` summed |
| 20.22 | `50_gap/district_allocation.csv` | computed here: plantation ÷ all expenditure × 100, FY2014-15 to FY2017-18. From: worked out by this script from its rows: `r620_plantation_pre_lakh` summed; worked out by this script from its rows: `r620_all_pre_lakh` summed |
| 0.38 | `50_gap/district_allocation.csv` | computed here: plantation ÷ all expenditure × 100, FY2018-19 to FY2025-26. From: worked out by this script from its rows: `r620_plantation_post_lakh` summed; worked out by this script from its rows: `r620_all_post_lakh` summed |
| 10/10/2020 | `50_gap/district_allocation.csv` | column `r620_pre_years_last_updated` |
| 110.58 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `r620_plantation_part_year_lakh` summed |
| 134.6 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_forest_named_started_by_fy2017_18_inr` summed |
| 1,899.3 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_plantation_category_started_by_fy2017_18_inr` summed |
| 52,178 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_forest_named_start_year_missing_inr` summed |
| 1,269,400 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_plantation_category_start_year_missing_inr` summed |
| 10.2 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_forest_named_started_later_inr` summed |
| 73.8 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_no_unit_total_inr` summed |
| 1.8 | `50_gap/district_allocation.csv` | worked out by this script from its rows: `dump_no_unit_forest_named_inr` summed |
| 34,766,888 | `50_gap/district_need.csv` | worked out by this script from its rows: `population_lgd` summed |
| 25.6 | `50_gap/district_need.csv` | computed here: Scheduled Tribe population ÷ population × 100, LGD panchayat units. From: worked out by this script from its rows: `st_pop_lgd` summed; worked out by this script from its rows: `population_lgd` summed |
| 90.6 | `50_gap/district_need.csv` | worked out by this script from its rows: the smallest `adi_2011_population_covered_pct` |
| ADI is the sum of five indicators each ranked 1–3, so it runs 5–15 | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `adi` → `direction`: the sentence of `docs/NEED.md` |
| rank each village at level-1 (low), level-2 (medium), or level-3 (advance) against these indicators | `50_gap/gap.provenance.json` | the same key: the sentence of the group's data dictionary |
| Aggregate Development Index 2011: ICTD group, IIT Delhi, from Census 2011. Licence or terms: CC BY 4.0. Its documentation says SHRUG's keys were used to link... | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `adi` → `source_and_licence` (read by the builder from the layer's list of sources) |
| 67.1 | `50_gap/need_vs_allocation_summary.csv` | column `need_share_pct_where_r_below_0_5`; row where `comparison` is 'C1' |
| 5 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts_r_below_0_5`; row where `comparison` is 'C1' |
| Kandhamal, Gajapati, Kalahandi, Koraput, Malkangiri | `50_gap/need_vs_allocation.csv` | C1: the `district_name` of the rows whose `r` is below 0.5, the largest `need` first |
| 66,060 | `50_gap/what_more.csv` | column `n1_ha_where_r_below_1`; row where `district` is 'state' |
| 74 | `50_gap/what_more.csv`; `50_gap/district_need.csv` | computed here: N1 in districts with `r` below one ÷ N1 × 100. From: column `n1_ha_where_r_below_1`; row where `district` is 'state'; worked out by this script from its rows: `n1_ha_2018_2025` summed |
| 14 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts_r_above_2`; row where `comparison` is 'C1' |
| 1.9 | `50_gap/need_vs_allocation_summary.csv` | column `need_share_pct_where_r_above_2`; row where `comparison` is 'C1' |
| 5 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts_need_zero`; row where `comparison` is 'C1' |
| 0.67 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C1' |
| 0.38 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C1' |
| 0.84 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C1' |
| 9,999 | `50_gap/need_vs_allocation_summary.csv` | column `n_bootstrap`; row where `comparison` is 'C1' |
| 0.00012 | `50_gap/need_vs_allocation_summary.csv` | column `p_permutation`; row where `comparison` is 'C1' |
| 99,999 | `50_gap/need_vs_allocation_summary.csv` | column `n_permutations`; row where `comparison` is 'C1' |
| 0.57 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'B1' |
| 0.30 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'B1' |
| 0.75 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'B1' |
| 0.37 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C12' |
| 0.01 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C12' |
| 0.63 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C12' |
| 0.046 | `50_gap/need_vs_allocation_summary.csv` | column `p_permutation`; row where `comparison` is 'C12' |
| 7,207.11 | `50_gap/need_vs_allocation_summary.csv` | column `sum_positive_gaps_lakh`; row where `comparison` is 'C1' |
| 52 | `50_gap/need_vs_allocation_summary.csv`; `50_gap/district_allocation.csv` | computed here: the sum of the positive gaps ÷ post-period plantation money × 100. From: column `sum_positive_gaps_lakh`; row where `comparison` is 'C1'; worked out by this script from its rows: `r620_plantation_post_lakh` summed |
| 8 | `50_gap/need_vs_allocation.csv` | the rows of C1 with the largest `need`: how many are tabled |
| 94.1 | `50_gap/need_vs_allocation.csv` | computed here: the need shares of those districts added. From: column `need_share_pct` of those rows |
| Kandhamal | `50_gap/need_vs_allocation.csv` | C1: the district with the largest `need` |
| Rayagada | `50_gap/need_vs_allocation.csv` | C1: the district with the second largest `need` |
| 0.65 | `50_gap/need_vs_allocation_summary.csv` | the smallest `rho` among C8, C9 and C10 |
| 0.67 | `50_gap/need_vs_allocation_summary.csv` | the largest `rho` among C8, C9 and C10 |
| 0.67 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C7' |
| 0.68 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C7b' |
| 53 | `50_gap/district_allocation.csv` | computed here: plantation money of FY2018-19 ÷ post-period plantation money × 100. From: worked out by this script from its rows: `r620_plantation_post_lakh` less `r620_plantation_post_without_fy2018_19_lakh`, summed; worked out by this script from its rows: `r620_plantation_post_lakh` summed |
| 0.45 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C11' |
| 0.12 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C11' |
| 0.70 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C11' |
| 0.67 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C2' |
| 0.12 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C3' |
| −0.27 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C3' |
| 0.47 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C3' |
| 0.76 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C4' |
| 0.74 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C5' |
| 0.73 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C6' |
| 8 | `50_gap/marginalisation_split.csv` | column `n_districts`; row where `comparison` is 'C1' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| More than 50 % | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `st_classes` → `labels`: the last |
| 78.1 | `50_gap/marginalisation_split.csv` | column `need_share_pct`; row where `comparison` is 'C1' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| 57.7 | `50_gap/marginalisation_split.csv` | column `allocation_share_pct`; row where `comparison` is 'C1' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| lowest third of the index | `50_gap/marginalisation_split.csv` | C1, `adi_tercile`: the first class |
| 88.9 | `50_gap/marginalisation_split.csv` | column `need_share_pct`; row where `comparison` is 'C1' and `grouping` is 'adi_tercile' and `class` is 'lowest third of the index' |
| 63.1 | `50_gap/marginalisation_split.csv` | column `allocation_share_pct`; row where `comparison` is 'C1' and `grouping` is 'adi_tercile' and `class` is 'lowest third of the index' |
| 70.6 | `50_gap/marginalisation_split.csv` | column `need_share_pct`; row where `comparison` is 'C4' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| 55.1 | `50_gap/marginalisation_split.csv` | column `allocation_share_pct`; row where `comparison` is 'C4' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| 60,135 | `50_gap/what_more.csv` | column `n1_ha_where_r_below_0_5`; row where `district` is 'state' |
| 637 | `50_gap/what_more.csv` | column `works_per_1000_ha_n1_fy2016_17`; row where `district` is 'state' |
| 57,135 | `50_gap/what_more.csv` | column `plantation_works_fy2016_17`; row where `district` is 'state' |
| 46 | `50_gap/what_more.csv` | column `works_per_1000_ha_n1_fy2025_26`; row where `district` is 'state' |
| 4,105 | `50_gap/what_more.csv` | column `plantation_works_fy2025_26`; row where `district` is 'state' |
| VGPP ₹/ha not in 00_raw | `50_gap/what_more.csv` | column `cost_blank_because`; row where `district` is 'state' |
| 743,148.16 | `50_gap/what_more.csv` | column `scale_of_the_fall_lakh`; row where `district` is 'state' |
| 7,431.48 | `50_gap/what_more.csv` | column `scale_of_the_fall_lakh`; row where `district` is 'state' |
| 13,915.72 | `50_gap/what_more.csv` | column `plantation_post_actual_lakh`; row where `district` is 'state' |
| the size of the fall, measured by the scheme's own earlier share; not a measure of need; the earlier years are a frozen 2020 snapshot | `50_gap/what_more.csv` | column `scale_is`; row where `district` is 'state' |
| 13 | `50_gap/district_year_panel.csv` | column `fy`: the distinct financial years |
| 390 | `50_gap/district_year_panel.csv` | rows counted by this script: its rows |
| 360 | `50_gap/district_year_panel.csv` | rows counted by this script: rows with `in_models` 1 |
| 8,099 | `50_gap/district_year_panel.csv` | worked out by this script from its rows: `loss_ha_year_t_minus_1` summed over the districts for each financial year of the pre period, then the mean of those years |
| 11,480 | `50_gap/district_year_panel.csv` | worked out by this script from its rows: the same for the financial years of the post period |
| 0.226 | `50_gap/panel_models.csv` | column `coefficient`; row where `id` is 'P1' |
| percentage points of the district's expenditure of the year per 100 ha of forest loss, dense plus open band, in calendar year t-1 | `50_gap/panel_models.csv` | column `coefficient_unit`; row where `id` is 'P1' |
| 0.214 | `50_gap/panel_models.csv` | column `se_cr1`; row where `id` is 'P1' |
| −0.065 | `50_gap/panel_models.csv` | column `wcb_ci95_lo`; row where `id` is 'P1' |
| 0.893 | `50_gap/panel_models.csv` | column `wcb_ci95_hi`; row where `id` is 'P1' |
| 0.383 | `50_gap/panel_models.csv` | column `wcb_p`; row where `id` is 'P1' |
| −0.119 | `50_gap/panel_models.csv` | column `coefficient`; row where `id` is 'P2' |
| −0.354 | `50_gap/panel_models.csv` | column `wcb_ci95_lo`; row where `id` is 'P2' |
| 0.426 | `50_gap/panel_models.csv` | column `wcb_ci95_hi`; row where `id` is 'P2' |
| 30 | `50_gap/panel_models.csv` | column `clusters`; row where `id` is 'P1' |
| 9,999 | `50_gap/panel_models.csv` | column `wcb_B`; row where `id` is 'P1' |
| 1,999 | `50_gap/panel_models.csv` | column `wcb_B`; row where `id` is 'P2' |
| 2 | `50_gap/panel_models.csv` | rows with `wcb_p_rises_again_lo` or `_hi` yes |
| 8 | `50_gap/panel_models.csv` | its rows |
| P7 | `50_gap/panel_models.csv` | the `id` of those rows |
| 0.043 | `50_gap/panel_models.csv` | the largest of `wcb_p_at_bracket_end_lo` and `_hi` |
| P6 | `50_gap/panel_models.csv` | the `id` of the rows where p at an end of the bracket is above 0.04 |
| 0.029 | `50_gap/panel_models.csv` | column `wcb_p_at_bracket_end_lo`; row where `id` is 'P1' |
| 2,889 | `50_gap/unit_history_models.csv` | column `n_units`; row where `id` is 'H1' |
| 27 | `50_gap/unit_history_models.csv` | column `n_districts`; row where `id` is 'H1' |
| 905 | `50_gap/unit_history.csv` | rows with `in_h1` 1 and `outside_village` 1 |
| 1,121 | `50_gap/unit_history_models.csv` | column `n_exposed`; row where `id` is 'H1' |
| 2.08 | `50_gap/unit_history.csv` | the mean of `forest_loss_share_pct` over the rows with `in_h1` 1 |
| 0.14 | `50_gap/unit_history.csv` | the median of the same |
| 0 | `50_gap/unit_history.csv` | rows whose `forest_at_window_start_ha` lies in the last half hundredth below one of the three floors |
| −0.14 | `50_gap/unit_history_models.csv` | column `coefficient`; row where `id` is 'H1' |
| percentage points of the forest at the start of 2018 lost in 2018-2025, per a unit with any forest-named expenditure on works started by FY2017-18, against a... | `50_gap/unit_history_models.csv` | column `coefficient_unit`; row where `id` is 'H1' |
| −0.48 | `50_gap/unit_history_models.csv` | column `wcb_ci95_lo`; row where `id` is 'H1' |
| 0.20 | `50_gap/unit_history_models.csv` | column `wcb_ci95_hi`; row where `id` is 'H1' |
| 0.379 | `50_gap/unit_history_models.csv` | column `wcb_p`; row where `id` is 'H1' |
| 9,999 | `50_gap/unit_history_models.csv` | column `wcb_B`; row where `id` is 'H1' |
| 1,999 | `50_gap/unit_history_models.csv` | column `wcb_B`; row where `id` is 'H2' |
| 2,889 | `50_gap/unit_history_models.csv` | column `n_units`; row where `id` is 'H9' |
| 8 | `50_gap/unit_history_models.csv` | rows whose interval includes zero |
| 9 | `50_gap/unit_history_models.csv` | its rows |
| 0.005 | `50_gap/unit_history_models.csv` | the largest of `wcb_p_at_bracket_end_lo` and `_hi` |
| none | `50_gap/unit_history_models.csv` | the `id` of the rows with `wcb_p_rises_again_lo` or `_hi` yes |
| 9,432 | `50_gap/fra_by_district.csv` | worked out by this script from its rows: `community_titles_distributed` summed |
| 331,568 | `50_gap/fra_by_district.csv` | worked out by this script from its rows: `community_extent_ha` summed |
| 6 | `50_gap/fra_by_district.csv` | rows with `community_titles_distributed` 0 |
| Sundargarh, Bhadrak, Kendrapara, Jagatsinghapur, Khordha, Puri | `50_gap/fra_by_district.csv` | the `district_name` of those rows |
| not an overlap: titles are not mapped, and 'community' lumps CR with CFR | `50_gap/fra_by_district.csv` | column `extent_is` |
| 1 | `50_gap/fra_by_district.csv` | rows with `community_extent_pct_of_forest_2000` above 100 |
| Baleshwar | `50_gap/fra_by_district.csv` | the `district_name` of those rows |
| 0.42 | `50_gap/fra_summary.csv` | column `rho`; row where `id` is 'R1' |
| 0.08 | `50_gap/fra_summary.csv` | column `ci95_lo`; row where `id` is 'R1' |
| 0.68 | `50_gap/fra_summary.csv` | column `ci95_hi`; row where `id` is 'R1' |
| 0.021 | `50_gap/fra_summary.csv` | column `p_permutation`; row where `id` is 'R1' |
| 0.15 | `50_gap/fra_summary.csv` | column `rho`; row where `id` is 'R2' |
| −0.24 | `50_gap/fra_summary.csv` | column `ci95_lo`; row where `id` is 'R2' |
| 0.50 | `50_gap/fra_summary.csv` | column `ci95_hi`; row where `id` is 'R2' |
| 0.436 | `50_gap/fra_summary.csv` | column `p_permutation`; row where `id` is 'R2' |
| 0.53 | `50_gap/fra_by_district.csv` | worked out by this script from its rows: Spearman's rank correlation of `community_extent_ha` with `forest_2000_ha` over its rows |
| 0.83 | `50_gap/fra_by_district.csv` | worked out by this script from its rows: Spearman's rank correlation of `n1_ha_2018_2025` with `forest_2000_ha` over its rows |
| 9,352 | `50_gap/fra_two_reports.csv` | column `community_titles_distributed`; row where `report` is "Ministry of Tribal Affairs national report, as on 31-12-2025 (Odisha's row)" |
| 327,099 | `50_gap/fra_two_reports.csv` | column `community_extent_ha`; row where `report` is "Ministry of Tribal Affairs national report, as on 31-12-2025 (Odisha's row)" |
| 80 | `50_gap/fra_two_reports.csv` | column `community_titles_distributed`; row where `report` is 'difference: state less national' |
| 4,469 | `50_gap/fra_two_reports.csv` | column `community_extent_ha`; row where `report` is 'difference: state less national' |
| 1.35 | `50_gap/fra_two_reports.csv` | column `extent_difference_pct_of_state`; row where `report` is 'difference: state less national' |
| 4,506,869 | `50_gap/forest_villages_pdf_record.json` | key `bytes` |
| 6a7a4657b15b7afd | `50_gap/forest_villages_pdf_record.json` | key `sha256`, its first sixteen characters |
| 64 | `50_gap/forest_villages_pdf_record.json` | key `pages` |
| 100 | `50_gap/forest_villages_pdf_record.json` | key `image_pixels_per_inch` |
| OmniPageCSDK18, in HP Smart Document Scan Software 3 3.10 | `50_gap/forest_villages_pdf_record.json` | keys `producer` and `creator` |
| 25 | `50_gap/forest_villages_pdf_record.json` | key `districts_in_the_file` |
| 24 | `50_gap/forest_villages_pdf_record.json` | key `summary_rows_that_add_up` |
| 25 | `50_gap/forest_villages_pdf_record.json` | key `summary_rows_read` |
| t---StffitinWrh 1677=--- 46 -- 1745 | `50_gap/forest_villages_pdf_record.json` | key `summary_rows_that_do_not`: the lines as read |
| The summary page, rendered at its own orientation, was read once by the session that wrote this step (10 October 2026). On the page every row is legible and ... | `50_gap/forest_villages_pdf_record.json` | key `note_from_one_page_read_by_eye` |
| Kandhamal, Rayagada, Gajapati, Kalahandi, Koraput | `50_gap/fsi_district_check.csv` | the `district_name` of the five rows with the largest `n1_ha_2018_2025` |
| 5 | `50_gap/fsi_district_check.csv` | those rows: how many |
| 80 | `50_gap/fsi_district_check.csv` | computed here: N1 of those five districts ÷ N1 of the state × 100. From: `n1_ha_2018_2025` of those five rows, summed; worked out by this script from its rows: `n1_ha_2018_2025` summed |
| Table 10.20.3, District-wise Forest Cover in Odisha (India State of Forest Report 2023, Volume II) | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_fsi` → `the_table` → `name` |
| all lands, more than one hectare with a tree canopy density of more than or equal to 10% irrespective of ownership, legal status and land use. Such lands may... | `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt` | the words as they stand in the file, line breaks apart |
| using Indian remote sensing satellite data (IRS-LISS III sensor with 23.5 m resolution) | `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt` | the words as they stand in the file, line breaks apart |
| The data period of the satellite used for this assessment is in general October 2021 to December 2021 | `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt` | the words as they stand in the file, line breaks apart |
| changes in forest cover in respect of the previous assessment of 2021 | `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt` | the words as they stand in the file, line breaks apart |
| 897 | `50_gap/fsi_district_check.csv` | worked out by this script from its rows: `n1_km2_2018_2025` summed |
| 151.89 | `50_gap/fsi_district_check.csv` | worked out by this script from its rows: `fsi_change_wrt_2021_km2` summed |
| 52,434 | `50_gap/fsi_district_check.csv` | worked out by this script from its rows: `fsi_forest_cover_km2` summed |
| 4,633 | `50_gap/fsi_district_check.csv` | worked out by this script from its rows: `fsi_scrub_km2` summed |
| 8 | `50_gap/fsi_district_check.csv` | the rows with the largest `n1_ha_2018_2025`: how many are tabled |
| 3 | `50_gap/fsi_district_check.csv` | of those five rows, those whose `fsi_change_wrt_2021_km2` is, in size, under a tenth of `n1_km2_2018_2025` |
| 3 | `50_gap/fsi_district_check.csv` | of those five rows, those with `fsi_change_wrt_2021_km2` below zero |
| 2 | `50_gap/fsi_district_check.csv` | of those five rows, those with `fsi_change_wrt_2021_km2` above zero |
| 267 | `50_gap/fsi_district_check.csv` | column `n1_km2_2018_2025`; row where `pc11_district_code` is 390 |
| −2.70 | `50_gap/fsi_district_check.csv` | column `fsi_change_wrt_2021_km2`; row where `pc11_district_code` is 390 |
| 12 | `50_gap/fsi_district_check.csv` | rows counted by this script: rows with `fsi_change_wrt_2021_km2` below zero |
| 66 | `50_gap/fsi_district_check.csv` | computed here: scrub of those five districts ÷ scrub of the state × 100. From: `fsi_scrub_km2` of those five rows, summed; worked out by this script from its rows: `fsi_scrub_km2` summed |
| −0.20 | `50_gap/fsi_summary.csv` | column `rho`; row where `id` is 'a' |
| −0.54 | `50_gap/fsi_summary.csv` | column `ci95_lo`; row where `id` is 'a' |
| 0.22 | `50_gap/fsi_summary.csv` | column `ci95_hi`; row where `id` is 'a' |
| 0.295 | `50_gap/fsi_summary.csv` | column `p_permutation`; row where `id` is 'a' |
| −0.21 | `50_gap/fsi_summary.csv` | column `rho`; row where `id` is 'c' |
| −0.54 | `50_gap/fsi_summary.csv` | column `ci95_lo`; row where `id` is 'c' |
| 0.20 | `50_gap/fsi_summary.csv` | column `ci95_hi`; row where `id` is 'c' |
| 0.258 | `50_gap/fsi_summary.csv` | column `p_permutation`; row where `id` is 'c' |
| 0.81 | `50_gap/fsi_summary.csv` | column `rho`; row where `id` is 'b' |
| 0.60 | `50_gap/fsi_summary.csv` | column `ci95_lo`; row where `id` is 'b' |
| 0.92 | `50_gap/fsi_summary.csv` | column `ci95_hi`; row where `id` is 'b' |
| 0.00001 | `50_gap/fsi_summary.csv` | column `p_permutation`; row where `id` is 'b' |
| 0.58 | `50_gap/fsi_summary.csv` | column `rho`; row where `id` is 'd' |
| 0.27 | `50_gap/fsi_summary.csv` | column `ci95_lo`; row where `id` is 'd' |
| 0.79 | `50_gap/fsi_summary.csv` | column `ci95_hi`; row where `id` is 'd' |
| 0.00094 | `50_gap/fsi_summary.csv` | column `p_permutation`; row where `id` is 'd' |
| 03/10/2026 and 04/10/2026 | `00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv` | column `last_updated` of the rows for FY2020-21 to FY2026-27: the distinct stamps |
| “Tree cover loss” refers to the removal or mortality of tree cover and can be due to a variety of factors, including mechanical harvesting, fire, disease or ... | `00_raw/05_forest_reference/provider_cautions_2026-10-10.json` | key `cautions_about_the_data`: the sentence named `loss_is_not_deforestation` |
| Specifically, sub-tropical areas have the lowest accuracies (around 20% for commission and omission errors). | `00_raw/05_forest_reference/provider_cautions_2026-10-10.json` | key `cautions_about_the_data`: the sentence named `sub_tropical_areas` |
| The model often misses disturbances in smallholder landscapes, resulting in lower accuracy of the data in locations such as sub-Saharan Africa, where this ty... | `00_raw/05_forest_reference/provider_cautions_2026-10-10.json` | key `cautions_about_the_data`: the sentence named `smallholder_landscapes` |
| For example, in 2015, the integration of Landsat 8 satellite data and updates to the loss detection algorithm from UMD resulted in better capturing of small-... | `00_raw/05_forest_reference/provider_cautions_2026-10-10.json` | key `cautions_about_the_data`: the sentence named `method_changed_in_2015` |
| `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | `00_raw/data_manifest.csv` | the row `supervisor_comments_as_recorded`: `dest`, under `00_raw/` |
| the proposal deck | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the proposal deck: `after` |
| 1. Design an analysis framework for social-ecological need identification and quantification vs. resource allocation done so far, and what more is needed. | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the proposal deck: point 1 of `points` |
| 2. Look at Commons Connect and Shivani's paper in detail… | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the proposal deck: point 2 of `points` |
| 3. Explore access to data dumps of MGNREGA, CFR granted villages and boundaries, understand ATREE data carefully. | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the proposal deck: point 3 of `points` |
| the methodology deck | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the methodology deck: `after` |
| 1. Overall methodology not clear; what info is extracted from CFR docs and how it is being related to satellite data | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the methodology deck: point 1 of `points` |
| 2. Why not simply determine which areas have seen forest degradation, are also marginalized, and have they seen good enough resource allocation in the past | `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | key `comments`: the comment after the methodology deck: point 2 of `points` |
| 120 | `50_gap/gap.provenance.json` | key `steps`: `gates` of the seven steps that carry gates, added |
| 10 | `scripts/verify_gap.py` | its list `PARTS`: how many parts |
| 7 | `50_gap/verify_gap_reviews.json` | key `parts_written_by_agents`: how many |
| 3 | `50_gap/verify_gap_reviews.json` | key `parts_written_by_the_session`: how many |
| 9 | `50_gap/verify_gap_reviews.json` | key `reports`: the parts of the reports whose `role` begins 'reviewed' |
| 213 | `50_gap/verify_gap_reviews.json` | key `reports`: `errors_planted`, added |
| 209 | `50_gap/verify_gap_reviews.json` | key `reports`: `errors_caught`, added |
| 4 | `50_gap/verify_gap_reviews.json` | key `reports`: `errors_planted` less `errors_caught`, added |
| 3 | `50_gap/verify_gap_reviews.json` | key `reports`: `disagreements`, counted |
| 22 | `50_gap/gates_step3.csv` | column `found`, the gate on tables that are byte for byte what they were: its first number |
| 6 | `50_gap/verify_gap_reviews.json` | key `reader` → `names_that_claim_more_than_the_code_tests`: how many |
| 5 | `50_gap/verify_gap_reviews.json` | key `pieces_changed_after_the_round`: how many |
| 12 | `50_gap/verify_gap_reviews.json` | key `pieces`: how many |
| a check reported as passed; a count altered to pass a check; a district in the wrong class; a dropped East Coast exclusion; a figure altered; a method misnam... | `50_gap/verify_gap_trials.json` | key `trials`: the distinct kinds of error |
| passed | `scripts/verify_r620.py` | its exit status and last line, run by this script as it wrote the document |
| 92 of 92 checks passed | `scripts/verify_layer.py` | its exit status and last line, run by this script as it wrote the document |
| 62 of 62 checks passed | `scripts/verify_decision.py` | its exit status and last line, run by this script as it wrote the document |
| 8 | `70_share/exercise_share_chrome.json` | key `summary` → `steps` |
| 20261010 | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `seeds` → `base` |
| python 3.12.13; numpy 2.3.5; pandas 3.0.6; scipy 1.18.1; statsmodels 0.15.0; numba 0.62.1; wildboottest 0.3.2 | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_units` → `package_versions` |
| 29 | `50_gap/gap.provenance.json` | key `steps` → `08_gap_environment` → `environment` → `packages_pinned` |
| 2.5.3 | `50_gap/gap.provenance.json` | key `steps` → `08_gap_environment` → `main_environment` → `numpy` |
| 11 | `50_gap/gates_environment.csv` | rows counted by this script: its rows |
| 6 | `50_gap/figures_looked_at.json` | key `files`: their number |
| 2026-10-10T18:38:40Z | `50_gap/figures_looked_at.json` | key `recorded_utc` |

### 16.2 Tables, in the order they appear

Every cell of a table that is not a typed label was read from the file and columns given here.

| table | cells read | file | columns or keys | rows |
|---|---|---|---|---|
| T_three | 12 | `50_gap/need_vs_allocation_summary.csv` | `need_is`, `allocation_is`, `rho`, `ci95_lo`, `ci95_hi`, `p_permutation` | `comparison` is 'C1'; `comparison` is 'B1'; `comparison` is 'C12' |
| §5, the districts with the most need | 72 | `50_gap/need_vs_allocation.csv` | `district_name`, `need`, `need_share_pct`, `allocation_share_pct`, `r`, `gap_lakh` | `comparison` is 'C1' and `pc11_district_code` is 390; `comparison` is 'C5' and `pc11_district_code` is 390; `comparison` is 'C1' and `pc11_district_code` is 396; `comparison` is 'C5' and `pc11_district_code` is 396; `comparison` is 'C1' and `pc11_district_code` is 389; `comparison` is 'C5' and `pc11_district_code` is 389; `comparison` is 'C1' and `pc11_district_code` is 395; `comparison` is 'C5' and `pc11_district_code` is 395; `comparison` is 'C1' and `pc11_district_code` is 398; `comparison` i ... |
|  |  | `50_gap/district_need.csv` | `st_class`, `adi_tercile` | `pc11_district_code` is 390; `pc11_district_code` is 396; `pc11_district_code` is 389; `pc11_district_code` is 395; `pc11_district_code` is 398; `pc11_district_code` is 375; `pc11_district_code` is 388; `pc11_district_code` is 399 |
| §5, the comparisons | 112 | `50_gap/need_vs_allocation_summary.csv` | `need_is`, `allocation_is`, `n_districts`, `rho`, `ci95_lo`, `ci95_hi`, `p_permutation`, `need_share_pct_where_r_below_0_5`, `need_share_pct_where_r_above_2`, `sum_positive_gaps_lakh` | `comparison` is 'C1'; `comparison` is 'C2'; `comparison` is 'C3'; `comparison` is 'C4'; `comparison` is 'C5'; `comparison` is 'C6'; `comparison` is 'C7'; `comparison` is 'C7b'; `comparison` is 'C8'; `comparison` is 'C9'; `comparison` is 'C10'; `comparison` is 'C11'; `comparison` is 'C12'; `comparison` is 'B1' |
| §6, C1 by st class | 16 | `50_gap/marginalisation_split.csv` | `class`, `n_districts`, `need_share_pct`, `allocation_share_pct` | `comparison` is 'C1' and `grouping` is 'st_class' and `class` is 'Less than 18 %'; `comparison` is 'C1' and `grouping` is 'st_class' and `class` is '18 to 33 %'; `comparison` is 'C1' and `grouping` is 'st_class' and `class` is '33 to 50 %'; `comparison` is 'C1' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| §6, C1 by adi tercile | 12 | `50_gap/marginalisation_split.csv` | `class`, `n_districts`, `need_share_pct`, `allocation_share_pct` | `comparison` is 'C1' and `grouping` is 'adi_tercile' and `class` is 'lowest third of the index'; `comparison` is 'C1' and `grouping` is 'adi_tercile' and `class` is 'middle third'; `comparison` is 'C1' and `grouping` is 'adi_tercile' and `class` is 'highest third of the index' |
| §6, C1 by sc tercile | 12 | `50_gap/marginalisation_split.csv` | `class`, `n_districts`, `need_share_pct`, `allocation_share_pct` | `comparison` is 'C1' and `grouping` is 'sc_tercile' and `class` is 'lowest third of Scheduled Caste share'; `comparison` is 'C1' and `grouping` is 'sc_tercile' and `class` is 'middle third'; `comparison` is 'C1' and `grouping` is 'sc_tercile' and `class` is 'highest third of Scheduled Caste share' |
| §6, C4 by st class | 16 | `50_gap/marginalisation_split.csv` | `class`, `n_districts`, `need_share_pct`, `allocation_share_pct` | `comparison` is 'C4' and `grouping` is 'st_class' and `class` is 'Less than 18 %'; `comparison` is 'C4' and `grouping` is 'st_class' and `class` is '18 to 33 %'; `comparison` is 'C4' and `grouping` is 'st_class' and `class` is '33 to 50 %'; `comparison` is 'C4' and `grouping` is 'st_class' and `class` is 'More than 50 %' |
| §6, C4 by adi tercile | 12 | `50_gap/marginalisation_split.csv` | `class`, `n_districts`, `need_share_pct`, `allocation_share_pct` | `comparison` is 'C4' and `grouping` is 'adi_tercile' and `class` is 'lowest third of the index'; `comparison` is 'C4' and `grouping` is 'adi_tercile' and `class` is 'middle third'; `comparison` is 'C4' and `grouping` is 'adi_tercile' and `class` is 'highest third of the index' |
| §6, C4 by sc tercile | 12 | `50_gap/marginalisation_split.csv` | `class`, `n_districts`, `need_share_pct`, `allocation_share_pct` | `comparison` is 'C4' and `grouping` is 'sc_tercile' and `class` is 'lowest third of Scheduled Caste share'; `comparison` is 'C4' and `grouping` is 'sc_tercile' and `class` is 'middle third'; `comparison` is 'C4' and `grouping` is 'sc_tercile' and `class` is 'highest third of Scheduled Caste share' |
| §8, the panel models | 88 | `50_gap/panel_models.csv` | `outcome`, `regressor_unit`, `n`, `coefficient`, `se_cr1`, `wcb_ci95_lo`, `wcb_ci95_hi`, `wcb_p`, `wcb_p_rises_again_lo`, `wcb_p_rises_again_hi`, `wcb_p_at_bracket_end_lo`, `wcb_p_at_bracket_end_hi` | `id` is 'P1' and `term` is 'loss_t_minus_1_per_100_ha'; `id` is 'P2' and `term` is 'loss_t_minus_1_per_100_ha'; `id` is 'P3' and `term` is 'loss_t_minus_1_per_100_ha'; `id` is 'P4' and `term` is 'loss_t_per_100_ha'; `id` is 'P5' and `term` is 'loss_pct_of_standing_t_minus_1'; `id` is 'P6' and `term` is 'loss_dense_t_minus_1_per_100_ha'; `id` is 'P7' and `term` is 'loss_t_minus_1_per_100_ha'; `id` is 'P7' and `term` is 'loss_t_minus_1_per_100_ha_x_post' |
| §9, the unit models | 108 | `50_gap/unit_history_models.csv` | `outcome`, `exposure`, `sample`, `n_units`, `n_exposed`, `n_districts`, `coefficient`, `se_cr1`, `wcb_ci95_lo`, `wcb_ci95_hi`, `wcb_p`, `wcb_p_at_bracket_end_lo`, `wcb_p_at_bracket_end_hi` | `id` is 'H1'; `id` is 'H2'; `id` is 'H3'; `id` is 'H4'; `id` is 'H5'; `id` is 'H6'; `id` is 'H7'; `id` is 'H8'; `id` is 'H9' |
| T_fv | 24 | `50_gap/forest_villages_pdf_record.json` | `check_a` → `parts` → `part`, `check_a` → `parts` → the part `a1` → `asks`, `check_a` → `parts` → the part `a1` → `holds_in`, `check_a` → `parts` → the part `a1` → `of`, `check_a` → `parts` → the part `a2` → `asks`, `check_a` → `parts` → the part `a2` → `holds_in`, `check_a` → `parts` → the part `a2` → `of`, `check_a` → `parts` → the part `a3` → `asks`, `check_a` → `parts` → the part `a3` → `holds_in`, `check_a` → `parts` → the part `a3` → `of`, `check_a` → `parts` → the part `a4` → `asks`, `check_a` → `parts` → the part `a4` → `holds_in`, `check_a` → `parts` → the part `a4` → `of`, `check_a` → `parts` → the part `a5` → `asks`, `check_a` → `parts` → the part `a5` → `holds_in`, `check_a` → `p ... |  |
| T_fsi | 72 | `50_gap/fsi_district_check.csv` | `district_name`, `n1_ha_2018_2025`, `n1_km2_2018_2025`, `n1_per_100_ha_of_forest_at_window_start`, `fsi_forest_cover_km2`, `fsi_change_wrt_2021_km2`, `fsi_change_pct_of_forest_cover`, `fsi_scrub_km2`, `fsi_scrub_pct_of_forest_cover` | `pc11_district_code` is 390; `pc11_district_code` is 396; `pc11_district_code` is 389; `pc11_district_code` is 395; `pc11_district_code` is 398; `pc11_district_code` is 375; `pc11_district_code` is 388; `pc11_district_code` is 399 |
| T_fsi_rho | 20 | `50_gap/fsi_summary.csv` | `id`, `what`, `rho`, `ci95_lo`, `ci95_hi`, `p_permutation`, `size_free` | `id` is 'a'; `id` is 'b'; `id` is 'c'; `id` is 'd' |

### 16.3 Files read

| file | bytes | sha256 | the run stamp it carries |
|---|---|---|---|
| `00_raw/01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf` | 4,506,869 | `6a7a4657b15b7afd` | - |
| `00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt` | 23,670 | `c40f12b61de9ddd3` | - |
| `00_raw/05_forest_reference/isfr2023_vol2_odisha_pdf_pages_260-265.txt` | 27,495 | `1f81d5059b2858db` | - |
| `00_raw/05_forest_reference/provider_cautions_2026-10-10.json` | 5,233 | `26f8c3daaeddc176` | 2026-10-10T11:19:43Z |
| `00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json` | 1,974 | `bc51835b1aa0a59e` | - |
| `00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv` | 2,273 | `e99800a09040373f` | - |
| `00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv` | 6,289 | `a2e2cc9c7df1a9b1` | - |
| `00_raw/data_manifest.csv` | 66,182 | `c54969bf437fbd0d` | - |
| `00_raw/docs/Village_level_dataset_schema_31Oct2022.docx` | 637,132 | `4956dd9762c7d89a` | - |
| `00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv` | 73,503 | `4e022d67a3d290bb` | - |
| `00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv` | 2,958 | `c960e84d949d2e80` | - |
| `10_units/outside_village_district.csv` | 536,828 | `763630369d3a544c` | - |
| `10_units/units.gpkg` | 48,369,664 | `ee86f0c3ac99c0c4` | - |
| `20_degradation/agreement.provenance.json` | 10,756 | `0c0182e3a357255c` | - |
| `20_degradation/agreement_by_unit.csv` | 2,551,239 | `c8a7dc67a24b25fa` | - |
| `20_degradation/corestack.provenance.json` | 12,320 | `8f03282fa339d4a3` | - |
| `20_degradation/corestack_by_unit.csv` | 2,788,494 | `2b1e83e529e32993` | - |
| `20_degradation/forest_floor.provenance.json` | 1,891 | `3691b99a971dda8c` | - |
| `20_degradation/hansen.provenance.json` | 8,637 | `d6e816740e7dd41a` | - |
| `20_degradation/hansen_loss_by_canopy_band_by_unit.csv` | 4,675,831 | `653eda9cef75aef8` | - |
| `30_need/need.provenance.json` | 15,023 | `8024375c3a69546b` | - |
| `30_need/need_by_unit.csv` | 1,212,483 | `0fc54bd7eb2a6d84` | - |
| `40_allocation/allocation.provenance.json` | 15,953 | `bf1e7052fa4ba2c7` | - |
| `40_allocation/allocation_by_unit.csv` | 1,072,899 | `3f81d2d3edefda9f` | - |
| `40_allocation/allocation_by_unit_fy.csv` | 7,544,719 | `8c991a5917f14e0e` | - |
| `40_allocation/allocation_unassigned.csv` | 26,189 | `0aec410b14fd5c1c` | - |
| `40_allocation/assets_district_fy.csv` | 65,174 | `5e8dcd030f973f36` | - |
| `40_allocation/r620_vs_dump.provenance.json` | 2,804 | `d536d248302a30da` | - |
| `50_gap/district_allocation.csv` | 8,152 | `a98526993a9de84a` | - |
| `50_gap/district_crosswalk.csv` | 1,392 | `8a127601ce0254c8` | - |
| `50_gap/district_need.csv` | 15,984 | `ea978fc16f8500ca` | - |
| `50_gap/district_year_panel.csv` | 59,379 | `49012547ee8ec3f5` | - |
| `50_gap/environment_before_stage4.txt` | 833 | `e3209059d58c25fe` | - |
| `50_gap/environment_main_now.txt` | 833 | `e3209059d58c25fe` | - |
| `50_gap/figures_looked_at.json` | 1,649 | `279f30578fd48b10` | - |
| `50_gap/forest_villages_districts_as_the_layer_reads_them.csv` | 1,644 | `357a86c94d2d2b63` | - |
| `50_gap/forest_villages_pdf_record.json` | 3,474 | `0c51a34156bfa4ce` | - |
| `50_gap/forest_villages_text_layer_check.csv` | 1,599 | `dd77b52f5809ab48` | - |
| `50_gap/fra_by_district.csv` | 4,568 | `37cf178731fafc68` | - |
| `50_gap/fra_summary.csv` | 708 | `cfbe515474ad9f4b` | - |
| `50_gap/fra_two_reports.csv` | 310 | `8630d58c44690c10` | - |
| `50_gap/fsi_district_check.csv` | 4,676 | `bf01bd9e191dcb8c` | - |
| `50_gap/fsi_summary.csv` | 2,210 | `2f2e621f9e30fc1d` | - |
| `50_gap/gap.provenance.json` | 48,350 | `71e13ff7968600ae` | - |
| `50_gap/gates_environment.csv` | 1,384 | `0db35e1441b74f38` | - |
| `50_gap/gates_phase2.csv` | 3,247 | `984723269ebd05b0` | - |
| `50_gap/gates_phase3.csv` | 1,629 | `6d12e48b7d993518` | - |
| `50_gap/gates_phase4.csv` | 1,167 | `c71ad60715956d7f` | - |
| `50_gap/gates_phase5.csv` | 1,060 | `6f8c180006589206` | - |
| `50_gap/gates_phase5b.csv` | 2,270 | `abacddb86066d298` | - |
| `50_gap/gates_step3.csv` | 587 | `2eae4aa7335390ee` | - |
| `50_gap/inputs_check.csv` | 3,941 | `524cc7de7a83aa12` | - |
| `50_gap/inputs_listing.json` | 23,556 | `e7544b139b1c3216` | - |
| `50_gap/marginalisation_split.csv` | 7,305 | `df523c940c65776f` | - |
| `50_gap/need_vs_allocation.csv` | 38,574 | `4145eb19ecb474d0` | - |
| `50_gap/need_vs_allocation_summary.csv` | 5,000 | `77831ac32e2c5717` | - |
| `50_gap/panel_models.csv` | 5,072 | `a8c7ef7ef69aa7dd` | - |
| `50_gap/panel_models.txt` | 4,986 | `8a9e9fb1e9b2ba06` | - |
| `50_gap/panel_models_wcb_grids.json` | 21,704 | `9defe9bcfc11abaa` | - |
| `50_gap/unit_district.csv` | 630,249 | `2a76e6ed9d5977a8` | - |
| `50_gap/unit_history.csv` | 1,983,358 | `6fe3a6f4a660f2b2` | - |
| `50_gap/unit_history_models.csv` | 6,920 | `f2684839d7db5310` | - |
| `50_gap/unit_history_models.txt` | 6,823 | `1c87824a24eba5c6` | - |
| `50_gap/unit_history_models_wcb_grids.json` | 24,175 | `a8429977eef4ef10` | - |
| `50_gap/verify_gap_reviews.json` | 167,498 | `2cf452bae56dcb6c` | - |
| `50_gap/verify_gap_trials.json` | 37,296 | `c148730d4e0f7ae2` | 2026-10-10T22:07:07Z |
| `50_gap/what_more.csv` | 12,125 | `c70bc6eb0d75b804` | - |
| `55_decision/condition_by_unit.csv` | 7,275,979 | `f5f8a218e86a16b7` | - |
| `55_decision/decision.provenance.json` | 25,625 | `d62a8eb63f364179` | - |
| `55_decision/tiers.csv` | 3,015 | `a7a7db34b7bcb90f` | - |
| `60_layer/data.js` | 22,260,285 | `c0224a1627682b2a` | - |
| `60_layer/index.html` | 205,721 | `94c9a3a8f195fec4` | - |
| `60_layer/layer_by_unit.csv` | 10,856,200 | `7558cff1e5aeb469` | - |
| `70_share/exercise_share_chrome.json` | 5,063 | `01798797082efcbd` | 2026-10-10T22:16:08Z |
| `70_share/odisha_forest_decision_layer/README.txt` | 7,390 | `8cf3242e8c5978ad` | - |
| `70_share/odisha_forest_decision_layer/data.js` | 22,066,227 | `4df21a9f2c43845a` | - |
| `70_share/odisha_forest_decision_layer/index.html` | 205,691 | `508144e070577a5e` | - |
| `70_share/share.provenance.json` | 3,871 | `4678936032348686` | - |
| `docs/DATA_NOTES.md` | 17,554 | `a8d4cb646aab38a1` | - |
| `docs/DECISION_LAYER.md` | 242,836 | `6d55c0c9137362c7` | - |
| `docs/LAYER.md` | 69,860 | `030a6f59b6306700` | - |
| `docs/NEED.md` | 19,029 | `de30a2951f052f54` | - |
| `docs/stage4_run_log.md` | 141,169 | `b2f235a062833792` | - |
| `figures/stage4/F1_state_report.png` | 169,399 | `c4e238215e532a6b` | - |
| `figures/stage4/F2_outside_village_asymmetry.png` | 93,303 | `f033aeabd3b3efed` | - |
| `figures/stage4/F3_map_of_cells.png` | 1,167,578 | `e4ccf36206922a92` | - |
| `figures/stage4/F4_need_share_against_money_share.png` | 210,719 | `bba9e11543356f59` | - |
| `figures/stage4/F5_need_and_money_by_marginalisation.png` | 158,318 | `896b2330113b87c2` | - |
| `figures/stage4/F6_estimates_with_wild_bootstrap_intervals.png` | 363,743 | `55bc528befd1ed74` | - |
| `requirements-stage4.txt` | 2,110 | `ce2ca3bda40374df` | - |
| `scripts/06_build_layer.py` | 69,130 | `2772b1c452dbcd8c` | - |
| `scripts/08_build_gap_districts.py` | 53,675 | `cd1d56a5ac0a16f8` | - |
| `scripts/08_build_gap_fsi.py` | 16,738 | `ef81b08886e0c180` | - |
| `scripts/08_build_gap_panel.py` | 24,335 | `dbdae06f86ca8eac` | - |
| `scripts/08_build_gap_rights.py` | 28,411 | `58a36ee7cc2a99f8` | - |
| `scripts/08_build_gap_units.py` | 23,170 | `cec9903d73558ef9` | - |
| `scripts/08_gap_environment.py` | 9,425 | `444796fa5c5fa797` | - |
| `scripts/08_gap_inputs.py` | 20,505 | `11133ffe99fd3f5c` | - |
| `scripts/_gap_common.py` | 25,815 | `6c91e04bb18d1da2` | - |
| `scripts/verify_gap.py` | 508,125 | `85e9a1e9fbbc35c6` | - |

### 16.4 Statements tested before they were written

Each of these is something the text says in words. The script tested it against the files and would have stopped had it failed.

- at least fifteen deliberate errors were tried against the verifier and every one was caught
- an error was planted in every table of `50_gap/` (the gate tables, the list of what changed in `docs/RESULTS.md` and the lists of what differs between two builds apart), in each of the two text files of the models, in the provenance record and in the record of the check of the forest villages PDF
- the trials were made with the verifier that is on disk, and the untouched tables passed it
- among the errors tried: a swapped district code
- among the errors tried: a part-year leak into a sum
- among the errors tried: a shifted lag
- among the errors tried: a wrong denominator
- among the errors tried: a dropped East Coast exclusion
- the tables of `scripts/08_gap_environment.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_gap_environment.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- the tables of `scripts/08_gap_inputs.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_gap_inputs.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- the tables of `scripts/08_build_gap_districts.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_build_gap_districts.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- the tables of `scripts/08_build_gap_panel.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_build_gap_panel.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- the tables of `scripts/08_build_gap_units.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_build_gap_units.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- the tables of `scripts/08_build_gap_rights.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_build_gap_rights.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- the tables of `scripts/08_build_gap_fsi.py` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed
- `scripts/08_build_gap_fsi.py` ran in an environment that held exactly what `requirements-stage4.txt` pins, the file as it is on disk
- every gate on the two environments passed, and the main environment's numpy is the one version the earlier stages' provenance records show
- every district C7 leaves out is also left out under the other reading of its rule, which leaves out more
- no N1 lies in a unit for which no zone model is recorded, so the rule for C7 can be decided for every district
- plantation's share of district expenditure varies several times more across district-years before FY2018-19 than after
- the state's forest loss in the year before, the regressor of the panel, is higher on average over the post period's years than over the pre period's
- the open band's loss, by year, is higher on average over the post period's years than over the pre period's
- every page of the forest villages PDF is one scanned image; its text layer fails check (a) of the owner's rule; check (b) was not run; and no count from it is in the table of districts
- the layer of the forest villages PDF fails every one of the parts check (a) was made into
- more than half of N1 lies on outside-village land
- plantation's share of all expenditure after FY2017-18 is less than a tenth of what it was before
- the four pre-period tables carry one stamp
- the sentence about the index quoted from `docs/NEED.md` stands in that document
- C1: need and post-period plantation money rise together across districts, and the interval of rho lies above zero
- the benchmark's rho is also above zero, and its interval overlaps C1's: rank correlation of this size is what district size alone produces
- C1's rho is above the benchmark's
- with district size taken out of both sides (C12) rho is smaller than C1's and still positive
- C12's interval lies just above zero
- more than half of the state's need lies in a few districts whose share of the money is under half their share of the need
- more districts have over twice their need share of the money than have under half, and together they hold a small part of the need
- with size taken out of both sides (C12) rho is lower than C1's by more than two tenths, and its interval starts lower: the association is much weaker than C1's figure alone suggests
- the districts named as having under half their need share of the money are those the summary counts, and their need shares add to the share it gives
- the district with the most need has under half its need share of the money, and the district with the second most has more than its share
- under each of the other three windows rho is within a few hundredths of C1's and its interval lies above zero
- leaving out the East Coast districts, under either reading of the rule, changes rho by a few hundredths at most and its interval stays above zero
- without FY2018-19 rho is lower than C1's and its interval still lies above zero
- for N2 the interval of rho includes zero
- the three comparisons with money of the years before FY2018-19 each give a higher rho than C1, with intervals above zero
- the interval of each of those three comparisons overlaps C1's: none of the three is shown to differ from C1
- on LGD-unit land alone rho is within a few hundredths of C1's
- in C1 the districts of the highest Scheduled Tribe class hold more than half the need and more than half the money, and a larger share of the need than of the money
- in C1 the ten districts lowest on the development index hold more than half the need and more than half the money, and a larger share of the need than of the money
- in C4 the districts of the highest Scheduled Tribe class have a smaller share of the pre-period money than of the earlier loss
- plantation works per thousand hectares of N1 in FY2025-26 are less than a tenth of those of FY2016-17
- the cost at the VGPP rate is blank in every row, with its reason
- P1's interval includes zero
- in every model of the panel the interval of every reported term includes zero
- every interval of the panel is bounded on both sides
- at the outer end of every bracket p is below the level, so every side has a crossing
- P2's coefficient has the opposite sign to P1's
- H1's interval includes zero
- every interval of the unit models is bounded on both sides
- at the outer end of every bracket of the unit models p is below the level
- the run log's note on Phase 4 says that, if the owner's condition is read to the letter, H9 is the row to drop
- H9's outcome is not H1's: it is the downward share
- the models whose interval excludes zero are sensitivities: H1, the headline, is not among them
- the sentence on which unit models have an interval that excludes zero follows the table
- the table of the two reports has the state's row, the national report's row and their difference, in that order
- the state's report gives more community titles and more community extent than the national report of the same date
- the ratio is above a hundred in at least one district, and the sentence says 'district'
- R1's interval lies above zero
- R2's interval includes zero
- R1's interval lies above zero while R2's includes it; the rank correlations of community extent and of N1 with the forest of 2000 are each above four tenths, and the first is above R2's rho: what R1 shows is carried by how much forest a district has
- on the summary page of the forest villages PDF, as its layer reads it, one row does not add up and no total row can be read
- the interval of rho for N1 against the Forest Survey's change in forest cover includes zero, with size left in (a) and with size taken out of both sides (c)
- the interval of rho for N1 against the Forest Survey's scrub lies above zero, with size left in (b) and with size taken out of both sides (d), and rho is lower with size taken out
- of the four rank correlations with the Forest Survey's figures, (a) and (b) leave size in and (c) and (d) take it out of both sides, and each is over all the districts
- the district with the most N1 is the same in the comparison table and in the table of the Forest Survey's figures, and the five districts with the most N1 hold more than three quarters of it
- the Forest Survey's change in forest cover for the state is a rise
- the imprint of the Forest Survey's report, in the registered text, says that it is the Survey's copyright and that its contents may be used for non-commercial purposes with due acknowledgment
- the registered pages of the report's first volume, which carry its definitions, do not mention scrub
- the record of the supervisor's comments holds two comments, of three points and of two, and the points of each, set end to end, are its text
- the record of the supervisor's comments is the file its manifest row describes: its place, its bytes and its SHA-256
- the six figures this section names, F1 to F6, are in `figures/stage4/`
- `docs/LAYER.md` and `docs/DECISION_LAYER.md` both speak of Commons Connect
- no tracked file of the repository names the paper the comment names, apart from the record of the comment and this stage's own documents and writers
- `docs/NEED.md` describes the use of ATREE's list in stage 2, and no step of this stage reads that list
- the manifest's note on the one public map of recognised villages says it has layers for Chhattisgarh and Maharashtra only
- the table of forest rights by district carries the label that titles are not mapped
- the gate on the shared copy passed every step, on the files that are on disk
- the parts the verifier runs are those the record of the review round lists, each is in one agent's report and in no other, and the last reader reported
- in the round of review every part but one went to an agent that had not written it; the part on the Forest Survey's figures was tried by the agent that wrote it and by no other
- the record of the review round is of the verifier that is on disk
- the reader found no name defined in two pieces of the verifier
- every gate of the rebuild that followed the review passed
- in the rebuild that followed the review every table of figures is byte for byte what it was
- the figures on disk are, byte for byte, the images the record says were looked at
- every use of "because", "led to", "effect of", "caused", "drove" or "cause" in the text stands in a sentence that says what the analysis cannot show (the names of the layer's cells apart)

### 16.5 Totals that two places both carry, compared

- district-years in the models, in the panel and in the table of models
- districts C7 leaves out, in the comparison table and in the table of districts
- N1 plus the loss under the minimum, and all forest loss of the window (to within 0.001)
- N1 of the state, in the table of districts and in the comparison table (to within 0.001)
- post-period plantation money, in the table of districts and in the comparison table (to within 0.005)
- C1, st_class: the districts of the classes, and the districts
- C1, adi_tercile: the districts of the classes, and the districts
- C1, sc_tercile: the districts of the classes, and the districts
- C4, st_class: the districts of the classes, and the districts
- C4, adi_tercile: the districts of the classes, and the districts
- C4, sc_tercile: the districts of the classes, and the districts
- N1 in districts with r below 0.5: in the table of what more is needed and, as a share, in the comparison table (to within 0.001)
- post-period plantation money, in the table of what more is needed and in the table of districts (to within 0.005)
- the pre-period plantation share applied to the post-period total, as tabled and as worked out here from the two periods' sums (to within 0.005)
- units in H1, in the table of models and counted in the unit table
- units exposed in H1, in the table of models and counted in the unit table
- community titles of the state's report, in the table of districts and in the table of the two reports
- community extent of the state's report, in the table of districts and in the table of the two reports (to within 0.001)
- N1 of the state, in the table of districts and in the table of the Forest Survey's figures (to within 0.001)
- the Forest Survey's change in forest cover, the districts summed and the total its table prints (to within 0.005)
- the Forest Survey's scrub, the districts summed and the total its table prints (to within 0.005)
- the Forest Survey's forest cover, the districts summed and the total its table prints (to within 0.005)

### 16.6 Digits the text was allowed to carry

The text itself may hold no digit except inside a code span (a file, a column, a design constant written as code, a command) and in: a date; a financial year; a year; the number of a heading; a reference to a section; the number of a stage of the pipeline; a name: a satellite, a report, a licence, a datum; the name of a comparison, a model, a measure of need or a figure; the name of a kind of standard error. Everything else that is a number came from a file.

*256 figures and 14 tables (588 cells) from 100 files; 99 statements tested; 22 totals compared. Written 2026-10-10T23:17:45Z by `scripts/write_gap.py` (sha256 `059ac9988190d532`), with the reading functions of `scripts/write_results.py` (sha256 `b918073042879cfc`).*
