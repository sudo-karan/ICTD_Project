# Results: the state of the pipeline, and every headline number with its caveat

*Written 2026-10-10T22:33:10Z by `scripts/write_results.py`. No figure in this document was typed. Each was read by that script
from the file named for it in the appendix (§13), and each conclusion drawn from figures was tested against them before
it was written. The figures change only when the files do.*

## 1. What this is, and where it stands

The project asks whether work under the rural employment guarantee (MGNREGA) in Odisha goes to the places where forest
is degrading, and to the people who depend on it. To ask that, three things have to be measured on the same pieces of
land: the condition of the forest (stage 1), social need (stage 2), and what the scheme spent (stage 3). Stage 0 builds
the pieces of land, the *units*. A fourth stage sets the three beside one another.

**That fourth stage is built**, as the project owner specified it on 10 October 2026: districts for the headline,
units only within districts. Its account is `docs/GAP.md`. The sections that follow report the measurements and the
checks made on them, as they did before it was built; §14 gives the fourth stage's three headline rows. It describes
where money went relative to where forest was lost, and it says nothing about why.

| stage | main output | state | how it was checked |
|---|---|---|---|
| units | `10_units/units.gpkg` | built, 2026-10-05T20:11:19Z | counts and areas recorded by the builder (§2) |
| forest: Hansen tree-cover loss | `20_degradation/hansen_by_unit.csv` | built, 2026-10-05T20:44:23Z | state totals held against Global Forest Watch's published figures; replicated independently (§3) |
| forest: CoRE Stack tree-change classes | `20_degradation/corestack_by_unit.csv` | built, 2026-10-05T21:40:02Z | reconciled to the one Odisha figure its producers print (§4) |
| forest: do the two agree | `20_degradation/agreement_summary.csv` and five tables beside it | built, 2026-10-07T10:08:15Z | arithmetic rebuilt by `scripts/verify_agreement.py`, which imports nothing from the builder: 41 of 41 checks passed (§5) |
| forest: NIRv greenness trend | columns of `20_degradation/degradation_by_unit.csv` | **blank: the run was stopped, and it is not a measure** | replicated independently and found unfit (§6) |
| need | `30_need/need_by_unit.csv` | built, 2026-10-05T20:22:49Z | census rows re-added to the published state totals (§7) |
| allocation | `40_allocation/allocation_by_unit.csv` | built, 2026-10-05T20:25:06Z | district-by-year sums equal a separate aggregation to the rupee; `scripts/verify_r620.py`: passed (§8) |
| the comparison of the three | `50_gap/need_vs_allocation_summary.csv` and the tables beside it | built, 2026-10-10T20:20:22Z | the figures of every table its steps write, recomputed by `scripts/verify_gap.py`, which imports nothing from the builders: 338 of 338 checks passed (§14) |
| map layer for discussion | `60_layer/index.html`, `60_layer/data.js` | built, 2026-10-09T04:08:22Z | `scripts/verify_layer.py`: 92 of 92 checks passed; every control exercised in two browser engines, and the page last opened and read in the Safari application on an earlier build, not on this one (§10) |

Three statements carry most of what follows.

- **Where the forest is, the planning data are not.** 26.7 per cent of the land lies outside any revenue
  village. It holds 59.4 per cent of the forest and 57.2 per cent of the tree-cover loss, and the
  census has no row for it (§9).
- **Two measures of forest change, made independently, point weakly at the same units.** Among the 2,423 units with
  enough forest to compare, 137 are in the top fifth on both where two unrelated measures would share about
  97: an odds ratio of 1.80 (1.10 to 2.91). For LGD panchayat units taken alone it is not established, and
  the agreement is about units, not hectares (§5).
- **A third measure failed, and that is a result.** A greenness trend from Landsat 8 was built, replicated, and found
  to move with the correction applied for the date of each image (§6).

## 2. The unit: what it is, and what it is not

A unit is a polygon. There are 11,468, of two kinds.

- **7,976 LGD panchayat units.** Each is the set of village polygons that the Local Government Directory mapping
  assigns to one panchayat id, merged into one shape.
- **3,492 outside-village units.** Each is a polygon of the village-boundary layer that carries no census code: land
  outside any revenue village. What that land is in law (reserved forest or otherwise) is not in the data used here.
  Each such block is a unit by itself.

Together they cover 154,929 km², computed on the WGS84 ellipsoid; the outside-village units are 41,358 km² of it,
26.7 per cent. They are built from the 52,531 village polygons of DataMeet's layer, 49,039
of which carry a Census 2011 code.

What a unit is **not**:

- **Not a gram panchayat.** The id runs over panchayat names within a sub-district, so a panchayat whose villages lie
  in two sub-districts is two units. The mapping holds 8,152 ids; 176 of them have no village polygon
  and so no unit (293,285 people live in them). There are more units than Odisha has gram panchayats.
  The state's own count of gram panchayats, and the ratio, are quoted with their source in `docs/UNITS.md`; that count
  is in no file of this pipeline, so it is not repeated here. Anything stated "per panchayat" from these tables is per
  LGD panchayat unit.
- **Not the panchayat that recorded a work.** A work counts toward the unit its recorded location falls in. Only
  65.2 per cent of works fall in the unit that holds most of the works of their own recorded panchayat
  (70.4 per cent counting LGD panchayat units only). Against CoRE Stack's own panchayat polygons the figure is
  67.2 per cent, so this is a property of the recorded locations and not of this layer.
- **Not the whole state.** 161 villages (753 km²) have a census code but no row in the mapping, and
  belong to no unit. The layer's area is not validated against the state's official area and is not meant to be: the
  polygons never claimed to tile the state.
- **Not surveyed for district.** An outside-village unit has no census code and so no district of its own. One was
  assigned: the district named on its polygon for 3,460 units; another district for 13, where two
  independent checks contradicted the name and agreed with each other; and for the 19 whose polygon names no
  district, the district of the panchayat polygons or the coded villages round it. 139 units
  (310 km²) have a name and nothing to check it against. 3 are ambiguous: two districts within
  five points of each other by the unit's own area. 82 more are flagged and not moved, because one check
  contradicts the district they carry. On villages whose district is known, the polygon's name is right
  99.92 per cent of the time; but for 79 per cent of the outside-village land no check
  by area is possible, and that is where the forest is.

## 3. Forest, first measure: Hansen tree-cover loss

**What it is.** The Global Forest Change dataset of Hansen and others gives, for every Landsat pixel, the canopy cover
in the year 2000 and the year, if any, in which that cover was removed. *Forest* here is a pixel with more than thirty
per cent canopy in 2000 (`treecover2000 > 30`, strictly above); *loss* is the area of such pixels removed in
2001–2025. All 11,468 units are measured.

|  | units | area on the pixel grid, km² | forest, km² | forest, % of area | share of all forest, % | loss, km² | share of all loss, % | loss, % of forest |
|---|---|---|---|---|---|---|---|---|
| outside-village units | 3,492 | 41,356 | 15,830 | 38.3 | 59.4 | 888 | 57.2 | 5.61 |
| LGD panchayat units | 7,976 | 113,565 | 10,800 | 9.5 | 40.6 | 665 | 42.8 | 6.16 |
| all units | 11,468 | 154,922 | 26,630 | 17.2 | 100.0 | 1,553 | 100.0 | 5.83 |

- **More than half the units have almost no forest.** 4,310 have none, and 6,265 (54.6 per cent) have
  under a hectare. A loss *rate* on so little forest is noise, which is why the comparisons below are made only above a
  minimum area (§5.3).
- **Its totals are held against a published source.** Summed over the units, forest in 2000 is −0.64 per cent,
  and loss in 2001–2020 −0.26 per cent, away from the figures Global Forest Watch publishes for Odisha on its own
  outline of the state. The build stops beyond 2 and 10 per cent. Exact equality is not
  expected: the outlines differ.

**What it cannot see.** Loss is the outright removal of tree cover from any cause, in plantation and natural forest
alike. It is not deforestation; it does not see a forest thinning under a standing canopy; and gain is not netted off.
The producers changed their method from 2011, so a step at that year is partly the method.

### 3.1 The canopy-band finding: what the forest mask leaves out

The mask is a choice, and it is fixed at the year 2000. Every pixel is in exactly one band of year-2000 canopy; the
three periods are 2001–2010, 2011–2017 and 2018–2025.

| canopy in the year 2000 | land, km² | loss, km² | % of all recorded loss | loss, % of the band's land | loss in the first period | in the second | in the third |
|---|---|---|---|---|---|---|---|
| `treecover2000 > 30`: the forest mask | 26,630 | 1,553 | 54.8 | 5.83 | 435 | 444 | 674 |
| `10 < treecover2000 <= 30` | 10,887 | 364 | 12.8 | 3.34 | 23 | 114 | 226 |
| `treecover2000 <= 10` | 117,404 | 917 | 32.4 | 0.78 | 45 | 245 | 627 |
| of which `treecover2000 = 0` | 114,612 | 826 | 29.1 | 0.72 | 38 | 218 | 570 |
| all land | 154,922 | 2,834 | 100.0 | 1.83 | 503 | 803 | 1,528 |

- **45.2 per cent of the loss Hansen records inside the units is outside the mask**: 1,281 of
  2,834 km² lie on land that had thirty per cent canopy or less in 2000, and so are not in the loss figure above.
  1,948 units have recorded loss and none of it in the mask.
- **Most of that is not forest that stood in 2000.** 826 km², 90 per cent of the lowest band's loss, is
  on pixels with no canopy at all in 2000: tree cover that grew after 2000 and was then removed, or an artefact of
  detection.
- **Its rise over time is largely the method.** Loss on the lowest band goes 45, 245, 627 km² across the
  three periods while loss in the mask goes 435, 444, 674. It should not be read as a trend on the ground.
- **The band that bears on open forest is the middle one**: 10,887 km² of land, 3.3 per cent of it lost.

So the mask hides a large area of recorded loss, but Hansen cannot say that this area is degraded forest. Whether
forest that was already open is getting worse needs a measure of condition. That is the reason for the second measure.

## 4. Forest, second measure: CoRE Stack tree-change classes

**What it is.** A raster made by the CoRE Stack group at IIT Delhi. It puts each pixel inside its own tree mask into a
class by whether canopy density or tree height moved between two three-year periods, roughly 2016–2019 and 2022–2025.
The product is named for 2017–2023 and exists for that span only. The classes used here are *degradation* (density or
height went from High to Low), *improvement* (the reverse), *lost* and *gained* (tree cover gone, or new), and
*partially degraded*. In the tables' own labels these are class `-1`, class `1`, class `-2`, class `2`, and classes `3`
and `4`.

Three properties decide how far it can be trusted. All three are from the producers' own paper and code;
`docs/DEGRADATION.md` §4a gives the sources.

- **"Degradation" is the crossing of a line, not a measured loss.** A stand that thins without crossing its zone's
  threshold is "no change", and a stand already Low cannot register degradation at all.
- **The classifiers behind it were right about two times in three** on held-out data, and the producers validated only
  the *lost* class.
- **Its "tree cover" is far wider than forest**: 109,957 km², 71 per cent of the units' area, taking
  in orchards and trees on farms.

|  | tree cover at the start, km² | degradation, km² | improvement, km² | degradation less improvement, km² | downward share (interval) |
|---|---|---|---|---|---|
| all units, all land inside the producers' tree mask | 109,957 | 13,692 | 10,568 | 3,125 | 0.56 (0.55 to 0.59) |
| all units, land with `treecover2000 > 10` | 37,299 | 9,091 | 5,524 | 3,566 | 0.62 (0.59 to 0.65) |
| outside-village units, the same land | 20,411 | 5,527 | 3,124 | 2,403 | 0.64 (0.60 to 0.68) |
| LGD panchayat units, the same land | 16,888 | 3,564 | 2,401 | 1,163 | 0.60 (0.56 to 0.64) |
| all units, Eastern Plateau and Hills model, all land | 87,103 | 11,403 | 9,786 | 1,616 | 0.54 (0.52 to 0.56) |
| all units, East Coast Plains and Hills model, all land | 22,851 | 2,289 | 781 | 1,508 | 0.75 (0.71 to 0.78) |

- **Read the downward share, never the degradation class alone.** The downward share is degradation over degradation
  plus improvement; one half means no net signal. Improvement is the noise reference for degradation: on land with
  `treecover2000 > 10` the product puts 24 per cent of the tree cover in the degradation class and
  15 per cent in improvement, which is more change in six years than a forest undergoes and about what such
  classifiers produce by error.
- **It differs by zone model.** The state is covered by two separately trained models with different thresholds. Their
  downward shares are 0.54 (Eastern Plateau and Hills) and 0.75 (East Coast Plains and Hills). Part of that
  difference is the models and not the land. This is the origin of the caveat on the agreement result (§5.2).
- **About half of the degradation class, 50 per cent, is in outside-village units.**
- **Its totals can be held against one published figure only.** The producers print one figure for Odisha: degradation
  in Mayurbhanj district in their earlier product for 2017–2021. Reading that product the way this pipeline reads the
  2017–2023 one gives 189.2 thousand hectares against their 189; the build stops beyond 2 per
  cent. No total exists for 2017–2023 or for the state, so the 2017–2023 tallies themselves are unreconciled.

## 5. Do the two measures agree?

The two were made independently, by different groups with different methods, and they do not measure the same thing:
one dates the removal of canopy, the other classes a change in its density or height. If both point at the same places,
each is some evidence for the other.

**The test.** Take the land with more than ten per cent canopy in 2000 (`treecover2000 > 10`), so that both sources are
read on the same land. For each unit with at least 100 ha of it on both sources' grids, take Hansen's loss rate for 2017–2023 and the share
of the land CoRE Stack puts in its degradation class. Flag a unit on each measure if it is in the top fifth of the units
compared. The *odds ratio* says how much more often the two flags fall on the same unit than they would if the measures
were unrelated; one means no relation. Every interval is the central ninety-five per cent of the estimate recomputed on
resampled data, and unless it says otherwise whole districts were resampled (§5.4). 8,577 units have too
little such land to be compared at all.

### 5.1 The result, two ways, side by side

| version | units | units compared | in the top fifth on both | expected if unrelated | odds ratio (interval) | odds ratio within districts (interval) |
|---|---|---|---|---|---|---|
| **Headline: East Coast units left out** | all units | 2,423 | 137 | 97 | 1.80 (1.10 to 2.91) | 2.30 (1.71 to 3.45) |
| **Headline: East Coast units left out** | LGD panchayat units | 1,649 | 65 | 49 | 1.55 (0.80 to 3.61) | 2.84 (1.92 to 5.24) |
| **Headline: East Coast units left out** | outside-village units | 774 | 72 | 51 | 2.06 (1.34 to 3.33) | 2.27 (1.18 to 2.69) |
| Every unit kept | all units | 2,891 | 184 | 116 | 2.27 (1.42 to 3.65) | 2.38 (1.85 to 3.55) |
| Every unit kept | LGD panchayat units | 1,983 | 100 | 60 | 2.30 (1.10 to 4.70) | 3.04 (2.06 to 6.57) |
| Every unit kept | outside-village units | 908 | 84 | 58 | 2.16 (1.59 to 3.47) | 2.02 (1.33 to 2.66) |
| Eastern Plateau model only | all units | 2,267 | 136 | 91 | 2.01 (1.08 to 3.45) | 2.37 (1.80 to 3.86) |
| Eastern Plateau model only | LGD panchayat units | 1,543 | 65 | 46 | 1.72 (0.80 to 4.22) | 3.04 (2.13 to 7.08) |
| Eastern Plateau model only | outside-village units | 724 | 71 | 48 | 2.26 (1.36 to 4.67) | 2.26 (1.08 to 4.37) |

The third block also leaves out the 156 units whose land straddles the two zone models. It is printed to show that
the headline does not turn on them: for all units it gives 2.01 (1.08 to 3.45).

### 5.2 Which is the headline, and why

**The headline is the first block: the 468 units whose land lies wholly under CoRE Stack's East Coast zone
model are left out.**

The reason is a test that was written into the build before any magnitude was looked at. CoRE Stack's improvement class
is the check on its degradation class. Hansen's loss is clearance: it should go with degradation, and it should not go
with improvement. That check, the *placebo*, holds under one zone model and fails under the other.

| units whose valued land is under | units compared | districts | % of the compared land | odds ratio, degradation | rank correlation of Hansen's rate with degradation (interval) | with improvement, the placebo (interval, districts resampled) | the same interval, units resampled singly |
|---|---|---|---|---|---|---|---|
| Eastern Plateau and Hills model only | 2,267 | 19 | 74.7 | 1.89 | 0.30 (0.14 to 0.43) | 0.07 (−0.07 to 0.17) | 0.04 to 0.11 |
| East Coast Plains and Hills model only | 468 | 8 | 10.7 | 5.38 | 0.52 (−0.04 to 0.59) | 0.35 (−0.16 to 0.44) | 0.27 to 0.43 |
| land under both models | 156 | 15 | 14.6 | 0.95 | 0.01 (−0.32 to 0.28) | 0.03 (−0.41 to 0.28) | −0.10 to 0.18 |

- Under the Eastern Plateau model, Hansen's rate is related to degradation (0.30) and not to improvement
  (0.07, with an interval that includes zero).
- Under the East Coast model it goes with both: 0.52 with degradation and 0.35 with improvement. Where loss
  goes with improvement as well, its going with degradation cannot be read as agreement about degradation. Something
  else, the zone's model or how much tree cover a unit has, is moving all three.
- Those 468 units are also where the two measures agree most (an odds ratio of 5.38), so leaving them out
  *lowers* the result. The headline is the weaker version. It is the headline because its own test passes, not because
  it survives.
- The 156 units whose land straddles the two models stay in.

**What the exclusion changes.**

- **For all units together the conclusion stands, weakened.** With every unit kept, 184 of 2,891 units are in the
  top fifth on both where about 116 would be expected: an odds ratio of 2.27 (1.42 to 3.65). In the headline
  it is 137 of 2,423 against about 97: 1.80 (1.10 to 2.91). Both intervals lie above one.
- **For LGD panchayat units alone it changes the answer.** With every unit kept their odds ratio is 2.30 (1.10 to
  4.70). In the headline it is 1.55 (0.80 to 3.61), an interval that includes one. So across the state,
  agreement among LGD panchayat units is **not established** once the East Coast units are out. Within districts it
  is: comparing units only with others of their own district gives 2.84 (1.92 to 5.24).
- **For outside-village units alone it stands**: 2.06 (1.34 to 3.33).

**A caveat on the caveat.** The East Coast figures rest on 8 districts. When whole districts are resampled, neither
of its two correlations is firmly established: the interval is −0.04 to 0.59 for degradation and
−0.16 to 0.44 for improvement, and both reach zero. The improvement correlation excludes zero only when
units are resampled one at a time (0.27 to 0.43). So the failure of the placebo is a strong pattern
in few districts, and not an established fact. That is a reason to print both versions, as here. It is not a reason to
prefer the larger one.

### 5.3 The floor: 100 ha

Ruled by the project owner on 7 October 2026; it supersedes the 50 ha that the pipeline's own rule had proposed.
A unit's loss rate is worth comparing only if it is repeatable. The test of that is the rank correlation, across units
of one size class, between a unit's loss rate in odd years and its loss rate in even years.

| minimum land, ha | units compared, headline | odds ratio, headline (interval) | units compared, every unit kept | odds ratio, every unit kept (interval) | smallest class of units admitted, ha | its repeatability, loss of all years | its repeatability, loss of the headline window |
|---|---|---|---|---|---|---|---|
| 10 | 4,613 | 2.63 (1.70 to 4.03) | 5,693 | 3.42 (2.20 to 5.50) | 10 to 25 | 0.60 | 0.60 |
| 50 | 3,081 | 2.20 (1.35 to 3.47) | 3,711 | 2.67 (1.75 to 4.36) | 50 to 100 | 0.73 | 0.73 |
| 100 | 2,423 | 1.80 (1.10 to 2.91) | 2,891 | 2.27 (1.42 to 3.65) | 100 to 250 | 0.84 | 0.80 |

- At 50 ha the smallest units admitted have a repeatability of 0.73; at 100 ha, 0.84.
- **The stricter the floor, the weaker the agreement**: the headline odds ratio is 2.63 at 10 ha, 2.20 at
  50 ha and 1.80 at 100 ha. The 50 ha row is a sensitivity reading and should be quoted only with
  its repeatability beside it.
- On the forest mask proper (`treecover2000 > 30`), 2,067 units have at least 100 ha. They hold 97.0 per
  cent of the forest and 97.5 per cent of the loss. 9,401 units fall below it.

### 5.4 The intervals: two ways of clustering

Units of one district share forest type, terrain, forest administration and satellite scenes, so treating them as
independent overstates certainty. The primary interval therefore resamples whole districts, every unit in its district,
which for an outside-village unit is an *assigned* district (§2). Two other designs are printed beside it for the
headline comparison: whole districts for the LGD panchayat units with the outside-village units resampled one at a
time, and every unit resampled one at a time.

|  | estimate | primary: whole districts | LGD units by district, outside-village units singly | every unit singly | width of the first over the second |
|---|---|---|---|---|---|
| all units, odds ratio | 1.80 | 1.10 to 2.91 | 1.17 to 2.99 | 1.45 to 2.25 | 0.99 |
| LGD panchayat units, odds ratio | 1.55 | 0.80 to 3.61 | 0.77 to 3.60 | 1.11 to 2.11 | 0.99 |
| outside-village units, odds ratio | 2.06 | 1.34 to 3.33 | 1.46 to 2.96 | 1.45 to 2.94 | 1.33 |
| all units, odds ratio within districts | 2.30 | 1.71 to 3.45 | - | - | - |
| all units, rank correlation with degradation | 0.30 | 0.15 to 0.41 | 0.17 to 0.41 | 0.26 to 0.33 | 1.06 |

- **All units are kept in the estimate.** Leaving out the outside-village units would remove 59.4 per cent
  of the forest and 57.2 per cent of the loss.
- **What the district labels rest on.** Of the 3,492 outside-village units, 139 have a district that no
  check can confirm, 13 were moved off their polygon's own name, and 3 are ambiguous. Among the
  774 of them in the headline comparison the counts are 25, 0 and 0; 2 more
  carry a district that one check contradicts.
- **For all units together the two clusterings do not differ materially.** The interval is 1.10 to 2.91 with whole
  districts and 1.17 to 2.99 with only the LGD panchayat units grouped: the widths are in the ratio 0.99, and
  both lie above one. The result for all units does not hinge on the assigned districts.
- **For the outside-village units taken alone they do differ, and that is a finding about that land.** Grouped by
  assigned district their interval is 1.34 to 3.33; resampled one at a time it is 1.45 to 2.94. The
  first is 1.34 times as wide. Outside-village units of one district move together. They are not independent
  observations, and an analysis that treats them as such overstates what it knows about the forest land. The conclusion
  for them is the same either way: both intervals lie above one.
- **For LGD panchayat units alone the design decides the verdict.** Resampled one at a time their interval is
  1.11 to 2.11, which lies above one; by district it is 0.80 to 3.61, which does not. Their district is
  their own census district and nothing in it is assigned, so the wider interval is the one to believe.
- **Resampling every unit singly would overstate certainty**: for all units 1.45 to 2.25, an interval 2.3
  times narrower than the primary one.

### 5.5 What the result depends on, and what it does not show

The comparison can be made with other readings of CoRE Stack's classes. In the headline population:

| the CoRE Stack flag is the top fifth on | in the top fifth on both | expected if unrelated | odds ratio (interval) |
|---|---|---|---|
| class -1 (delivered) | 137 | 97 | 1.80 (1.10 to 2.91) |
| classes -1, 3 and 4 | 134 | 97 | 1.73 (1.05 to 2.72) |
| class -1 minus class 1 | 125 | 97 | 1.52 (0.93 to 2.78) |
| class -2, tree cover lost | 167 | 97 | 2.67 (1.88 to 3.76) |
| class 1, improvement (the placebo) | 69 | 97 | 0.61 (0.21 to 1.35) |

- **The reading matters.** The result is largest with the *lost* class (2.67; 1.88 to 3.76), the one class
  the producers validated, though on this land it is a small class (133 km² against 9,091 km² of
  degradation). It is smallest with degradation net of improvement (1.52; 0.93 to 2.78), whose interval
  includes one.
- **In the headline population the placebo passes.** Units in the top fifth on improvement coincide with Hansen's flags
  no more often than chance (0.61; 0.21 to 1.35).
- **Unit-level, not pixel-level.** The two measures agree about *which units* are degrading, not yet about *which
  hectares*. Inside a unit flagged by both, Hansen's loss and CoRE Stack's degradation may lie on different land. The
  pixel-by-pixel overlap has not been run; it needs one more Earth Engine job.
- **One window.** CoRE Stack covers 2017–2023 only, so the agreement is tested for that window and no other.
- **Modest.** Of the 485 units Hansen flags in the headline comparison, 137 are flagged by CoRE Stack too.
  Most units flagged by one measure are not flagged by the other.

## 6. NIRv from Landsat 8: a measure that failed, which is a result

**What was tried.** A trend, over the seasons 2013–2025, in the near-infrared reflectance of vegetation (NIRv) seen by
Landsat 8 in November and December: for each pixel, a yearly value and a test for decline. It was to be the measure of
thinning that Hansen cannot see.

**What was found.** An independent replication, written from the scripts' descriptions alone, reproduced the pipeline's
values: the design was implemented correctly. It then showed what the yearly value is made of. Greenness falls through
the window as leaves age, and cloud decides which dates are seen, so the value follows the calendar: over the
61 larger units of the replication's south-west sample, the median correlation between a unit's yearly
series and the mean date of its images is −0.79. The value was redesigned to move every image to one date, which
removed that dependence (the same correlation becomes 0.19). The redesigned trend then has three faults.

| | what was measured | result |
|---|---|---|
| the trend moves with the correction | the fitted seasonal rate scaled to nine tenths, to one, and to eleven tenths of itself | the declining share of the south-west sample is 6.3, 5.8 and 5.3 per cent |
| one image decides the flag | one image, drawn at random, taken away from every pixel | 24 per cent of the declining flags turn over in the south-west sample, 20 in the state-wide one |
| the decline is not beyond chance | the seasons put in random order and the test run again | re-ordered seasons reach the observed declining share in 7 per cent of orderings (south-west) and 22 (state-wide) |

The first two are properties of the measure and not of the sample. More units cannot repair them.

**What follows.** By ruling of 7 October 2026, NIRv is not a measure of degradation in this project. It remains as
reported columns of `20_degradation/degradation_by_unit.csv`, and those columns are blank in all 11,468 units:
the state-wide run was stopped partway, when its queued Earth Engine tasks were cancelled from outside the pipeline,
and nothing is queued. The finding does not wait for it: a seasonal greenness trend over deciduous forest needs the
dates of its images controlled, and once they are, the trend is a function of the control.

*These figures are the replication's, on its own samples (677,404 pixels in the south-west and 566,362
state-wide; 61 and 21 larger units). They are read from its working files, which are not
stage outputs (§13). `docs/DEGRADATION.md` §5 has the full account.*

## 7. Need

**What it is.** For each LGD panchayat unit, the Census 2011 counts of the villages mapped to it, and measures built on
them. The units hold 34,766,888 people in 8,043,218 households, of whom 8,895,006 (25.6 per cent) are of the
Scheduled Tribes.

**How it was checked.** The census rows used here, added up, equal the published Census 2011 totals for Odisha
(41,974,218 people) on population, rural population, urban population, Scheduled Caste population and Scheduled Tribe
population. The published figures were taken from a secondary copy. Households are not reconciled: no published total
was found.

**What is blank, and why.**

| column | LGD panchayat units with a value | LGD panchayat units blank | why a cell is blank | outside-village units blank |
|---|---|---|---|---|
| `st_share`: Scheduled Tribe share of population | 7,853 | 123 | the unit's villages have no resident population in the census rows | 3,492 |
| `adi_2011`: the development index, from Census 2011 | 7,442 | 534 | none of the unit's villages has an index | 3,492 |
| `adi_2019`: the same index as predicted for 2019 | 5,110 | 2,866 | none of the unit's villages has a prediction | 3,492 |
| `poverty_rate`: a small-area model estimate (SHRUG) | 7,812 | 164 | none of the unit's villages has an estimate | 3,492 |
| `forest_dependent_households`: a construct, see below | 7,976 | 0 | never blank in an LGD panchayat unit | 3,492 |

- **Every column is blank for all 3,492 outside-village units.** They have no census rows. This is not a
  gap that better joining would close: the census does not enumerate that land as villages.
- **Which columns carry the argument.** `st_share` is the axis of marginalisation and `adi_2011` is the control for
  development. `adi_2019` is a prediction, blank for 2,866 units, and is reported only.
- **`poverty_rate` is licensed.** It is a model estimate from SHRUG, under CC BY-NC-SA 4.0. It stays in the analysis
  table. It is left out of the map layer, and no value of it is printed in this document.
- **`forest_dependent_households` is a construct, not a count**: the estimated Scheduled Tribe households of villages
  that ATREE's list of potential community-forest villages classes as having forest inside the boundary
  (19,334 villages; 1,308,898 households, estimated). Under 9 other reasonable rules its rank
  correlation with itself across units runs from 0.46 to 0.96. It is reported, and used as a robustness
  reading, not as the measure of need.
- **Where the units fall short of the census.** 95 census villages (20,001 people) are not
  in the mapping. In 81 units more than half the population lives in villages that have no polygon: the counts
  are right, and the shape drawn is of a minority of the unit.

## 8. Allocation

**What it is.** The geotagged record of MGNREGA assets for Odisha: 1,302,664 works carrying ₹12,816.8 crore of
expenditure, each placed in the unit its recorded location falls in. 1,294,160 works fall in a unit;
8,504 (₹73.8 crore) fall in none.

**How it was checked.** Its sums by district and year equal a separate aggregation of the same record, to the rupee, in
579 of 579 cells and in 9 of 9 categories.

- **The record effectively ends in FY2017-18.** 97.8 per cent of all its expenditure is on works started in
  or before that year. Against the scheme's own state report (MIS report R6.20) it holds 83 per cent of the
  expenditure of FY2016-17 and 3 per cent of FY2018-19. It is a picture of where works were put up to
  FY2017-18. It is not current allocation.
- **What a work's money means.** A work's whole lifetime expenditure sits in the year the work started. 25,526 works
  report no expenditure, and no work reports person-days.
- **It is not what a panchayat received.** A work is counted where it lies (§2): 65.2 per cent of works lie in
  the unit that holds most of their own recorded panchayat's works.
- **The categories overlap and must never be added.** The plantation category is 15.1 per cent of expenditure,
  work types that name forest 1.1, and the water construct 28.7.
- **No natural-resource (NRM) figure exists per unit, and none should be built.** The record has no NRM marker, and
  water plus plantation undercounts NRM by a share that is not stable over time. NRM comes only from R6.20, for
  districts and the state:

| financial year | expenditure, ₹ crore | natural-resource works, % of it | plantation, % of it | water, % of natural-resource works | the geotagged record holds, % of it | report last updated |
|---|---|---|---|---|---|---|
| 2014-15 | 1,247 | 42.8 | 21.4 | 40.1 | 82.6 | 10/10/2020 |
| 2015-16 | 2,096 | 38.2 | 17.6 | 39.8 | 93.4 | 10/10/2020 |
| 2016-17 | 1,950 | 53.6 | 24.2 | 44.6 | 83.4 | 10/10/2020 |
| 2017-18 | 2,216 | 40.6 | 18.6 | 41.3 | 36.2 | 10/10/2020 |
| 2018-19 | 2,211 | 42.2 | 3.3 | 50.5 | 3.2 | 27/12/2024 |
| 2019-20 | 2,866 | 37.2 | 0.3 | 50.9 | 2.3 | 27/12/2025 |
| 2020-21 | 5,961 | 61.0 | 0.0 | 56.0 | 0.6 | 03/10/2026 |
| 2021-22 | 5,817 | 68.6 | 0.0 | 58.0 | 0.7 | 03/10/2026 |
| 2022-23 | 5,427 | 76.7 | 0.0 | 60.8 | 0.6 | 03/10/2026 |
| 2023-24 | 5,902 | 66.0 | 0.0 | 62.0 | 0.3 | 03/10/2026 |
| 2024-25 | 4,066 | 67.6 | 0.6 | 63.7 | 0.1 | 03/10/2026 |
| 2025-26 | 4,497 | 64.8 | 0.5 | 77.7 | 0.0 | 04/10/2026 |
| 2026-27 | 870 | 59.8 | 0.1 | 85.9 | 0.0 | 04/10/2026 |

- **Plantation's share of expenditure in the state report falls from 24.2 per cent in FY2016-17 to 3.3
  in FY2018-19, and is under one per cent in every later year. Water's share of natural-resource works rises from
  40.1 per cent in FY2014-15 to 63.7 in FY2024-25.**
- **Caveats on the state report.** 4 of its 13 years carry the stamp 10/10/2020: a snapshot frozen
  years ago, and they are the high-plantation years. Its three categories are nested, water and plantation both
  inside natural-resource works, and not a partition. The last year is a part year. Why plantation fell is not
  something these tables can say.

## 9. The outside-village asymmetry

The outside-village units are 26.7 per cent of the land. Set beside one another, the stages say this about
them:

| | outside-village units |
|---|---|
| forest (stage 1, Hansen) | 59.4 per cent of all forest; 38 per cent of their own area is forest, against 10 per cent in LGD panchayat units |
| tree-cover loss (stage 1, Hansen) | 57.2 per cent of all loss in the mask |
| degradation class (stage 1, CoRE Stack) | 50 per cent of it |
| the agreement comparison | 774 of the 2,423 units compared, and the agreement holds among them (§5.2) |
| need (stage 2) | **nothing: every column blank in all 3,492** |
| allocation (stage 3) | 131,687 works worth ₹1,443.5 crore lie inside them: 10.1 per cent of works and 11.3 per cent of expenditure. Of the 1,048 units with no work at all, 804 are outside-village units |
| district | assigned, not recorded (§2) |

Most of the forest, and most of its loss, is on land for which the planning system has no population figure of any
kind. Work is nonetheless recorded there. Any comparison of need with allocation that requires census data can describe
only the LGD panchayat units, which hold 40.6 per cent of the forest. That is a finding of its own, and it
stands whatever stage 4 turns out to be.

## 10. The map layer

**What it is.** Two files, `60_layer/index.html` and `60_layer/data.js` (22.5 MB together, 6.0 MB
zipped), that open from disk in a browser and fetch nothing from the network: a map of the 11,468 units with a layer
for each measure above, a panel of 44 figures for a clicked unit, a search, filters by kind of unit and by
district, and a minimum of forest below which a unit is drawn grey (100 ha unless changed). It is a demonstration
for discussion with people who know the places. It is not a verdict on any place.

- **Checked against the stage tables** by `scripts/verify_layer.py`: 92 of 92 checks passed.
- **Every control exercised on the build that is on disk** (2026-10-09T04:08:22Z), by `scripts/exercise_layer.py`, which writes
  `60_layer/exercise_chrome.json` and `60_layer/exercise_webkit.json`. In Chrome (Chrome/154.0.8037.99), opened from disk
  and driven with real mouse and keyboard events: 53 of 53 actions did what they should, and for
  29 units clicked on the map 1,276 of 1,276 displayed values equalled the stage tables. In
  WebKit 21624.5.1.11.3 (the engine of Safari 27.0 on this machine), with events made in script: 53 of 53, and for 29
  units 1,276 of 1,276. `docs/LAYER.md` lists each action and what happened.
- **Not opened in the Safari application on this build.** That check was left out of this build's checks, and their
  record gives the reason: "the owner's instruction of 9 October 2026 for the batch that applies his rulings: no run in the Safari application, since no unit changes cell". The last run of `scripts/exercise_layer_safari.py`, in Safari 27.0 (the application), was on
  the layer built 2026-10-08T22:42:59Z, not the one on disk: there the page was driven by its address alone and its text read
  back, nothing was clicked, 48 of 48 addresses showed what they should (every layer, every minimum of
  forest, the search, the two text panels), and for the same 29 units 1,265 of 1,265 values the
  panel should show were in the page's text. On the build on disk the layer was exercised in Chrome and in Safari's
  engine only.
- **Not done.** No click was made in the Safari application, only in its engine: that needs a Safari setting that is
  the owner's to change. And Firefox was not installed on the machine, so the layer has not been opened in it.
- **Left out on purpose**: the SHRUG-derived columns (§7).
- **The shapes are simplified** so that the file can be sent, with a tolerance of 30 m; 120 very small
  units change by more than five per cent in drawn area. Every area printed in a panel is the unit's true area.
- **Licence of the shapes.** They derive from DataMeet's village boundaries and carry the ODbL 1.0.

## 11. Not built, and inputs still blank

- **Stage 4, the comparison of forest condition, need and allocation, is no longer in this list**: it was built on
  10 October 2026 (§14; `docs/GAP.md`). It costs no shortfall and controls for no remoteness, for the two reasons
  given below.
- **The pixel-by-pixel overlap of Hansen's loss with CoRE Stack's degradation is not run** (§5.5). It needs an Earth
  Engine job.
- **The state-wide NIRv run is stopped and nothing is queued** (§6). Its columns are blank.
- **The VGPP plantation unit cost (₹ per hectare) is blank.** It is not in `00_raw/`, and no figure has been put in its
  place. Nothing can be costed until it is supplied.
- **The coordinates of the district headquarters are blank**, for the same reason; so no control for remoteness exists.
- **Whether Annexure-A of the order of 22 May 2026 carries a grade for each gram panchayat, or only the formula, is not
  known** (`docs/DATA_NOTES.md`).
- **Forest-rights titles are in no stage.** The two official reports on them disagree with each other
  (`docs/DATA_NOTES.md`), and no title data are joined to the units.

## 12. Limitations

Collected from `docs/UNITS.md`, `docs/DEGRADATION.md`, `docs/NEED.md`, `docs/NRM.md`, `docs/DATA_NOTES.md` and
`docs/LAYER.md`, which give the detail. The first seven are the ones a reviewer finds first.

**The seven.**

- **The agreement is unit-level, not pixel-level.** The two forest measures agree about which units are degrading, not
  about which hectares. The pixel overlap is unrun (§5.5).
- **CoRE Stack covers 2017–2023 only.** It compares two three-year periods; nothing before them is seen, and the
  agreement with Hansen is tested for that window alone (§4, §5.5).
- **The placebo fails in one zone.** Under CoRE Stack's East Coast model, Hansen's loss goes with improvement
  (0.35) as well as with degradation. Those 468 units are left out of the headline; leaving them out removes the
  result for LGD panchayat units taken alone (§5.2).
- **54.6 per cent of units have under a hectare of forest** (6,265 of 11,468). Rates on such units are
  noise; comparisons use a floor of 100 ha, below which 9,401 units fall (§3, §5.3).
- **The outside-village land has no census data at all.** 3,492 units, 26.7 per cent of the land and
  59.4 per cent of the forest, are blank in every column of need (§7, §9).
- **`poverty_rate` is SHRUG-licensed and omitted from the layer.** CC BY-NC-SA 4.0: any released file that carries it,
  or figures derived from it, may be bound by that licence. It is also a model estimate, blank for 164 LGD
  panchayat units (§7).
- **Species composition is not measurable from these sources.** Hansen sees canopy and its removal; CoRE Stack sees
  classes of canopy density and height. Neither tells a natural forest from a plantation, or one species from another.
  A plantation replacing a forest is, to both, tree cover.

**The unit.**

- A unit is an LGD panchayat id, not a gram panchayat, and there are more units than gram panchayats (§2).
- A unit is not the panchayat that recorded a work: 65.2 per cent of works lie in their recorded panchayat's
  main unit (§2).
- 161 coded villages (753 km²) are in no unit; 176 ids of the mapping
  (293,285 people) have no polygon.
- The layer's area is on the ellipsoid and is not validated against the state's official area.
- Two other layers are kept for sensitivity, one with the outside-village land dropped and one with it merged into the
  nearest unit. Nothing in this document uses them.
- The district of an outside-village unit is assigned: 139 with no possible check, 13 moved off the
  polygon's name, 3 ambiguous, 82 flagged and not moved. The crosswalk of district names inside
  the boundary layer has faults of its own, recorded in `docs/UNITS.md` and not corrected.

**Forest condition.**

- Hansen's loss is stand-replacing removal from any cause. It is not deforestation, cannot see thinning, and does not
  net off gain. Its method changed from 2011.
- The forest mask is a choice fixed at 2000. 45.2 per cent of recorded loss is outside it, most of that
  on land with no canopy in 2000, and its rise over time is largely the method (§3.1).
- Earth Engine's area for a pixel cut by a boundary is approximate; the sums over pixels and over polygons are compared
  in the build and held to a tolerance (`20_degradation/hansen.provenance.json`).
- CoRE Stack's degradation is the crossing of a line by classifiers right about two times in three; only its *lost*
  class was validated by its producers; its tree mask takes in 71 per cent of the units' area; its two zone
  models differ (0.54 against 0.75 in downward share); and only one published figure exists to reconcile it
  to (§4).
- The agreement is modest and depends on choices: the floor (weaker as the floor rises, §5.3), the CoRE Stack class
  used (§5.5), and the zone exclusion (§5.2). The failure of the placebo is itself not firmly established: it rests on
  8 districts.
- A flag is relative: it marks the top fifth of the units compared, not a stated amount of loss or degradation.
- The intervals rest on resampling districts, and for outside-village units the district is assigned (§5.4).
  25 districts is few clusters, so the intervals are themselves rough.
- All areas are on the ellipsoid. The producers of CoRE Stack count a nominal area for every pixel; this pipeline's
  area for the same pixel is 6.8 per cent smaller, so their own tallies of the same raster would be larger.
- NIRv is unfit as a measure, and its columns are blank (§6).

**Need.**

- The census is that of 2011. The development index for 2019 is a prediction, blank for 2,866 units.
- `st_share` is blank for 123 LGD panchayat units and `adi_2011` for 534.
- `forest_dependent_households` is a construct resting on one list and one rule (§7).
- Households are not reconciled to a published total, and the population totals were checked against a secondary copy
  of the census figures.
- In 81 units most of the population lives in villages with no polygon.
- The panchayat-level file supplied with the census data holds more people than the village rows in 83 ids (it
  double counts) and is used only as a cross-check; every figure here is built from village rows.
- The poverty estimate rests on fewer than a hundred people in 101 units, and in 73 units part of it comes
  from an area shared with another unit.

**Allocation.**

- The geotagged record effectively ends in FY2017-18 (97.8 per cent of expenditure up to then). It is not
  current allocation (§8).
- A work's lifetime expenditure sits in its start year; 25,526 works report none; none reports person-days.
- 8,504 works fall in no unit.
- Categories overlap; no NRM figure exists per unit; the work-type flags for water and for forest have no verified
  reference to be held against.
- The state report's high-plantation years are a frozen snapshot, and its categories are nested (§8).

**Sharing.**

- SHRUG-derived columns must stay out of anything released. The development index for 2011 is kept in the layer on a
  judgement that it is computed from census rows; a stricter reading of SHRUG's terms would remove it
  (`docs/DATA_NOTES.md`).
- The unit shapes are a database derived from DataMeet's under the ODbL 1.0, and may be shared under that licence and
  no narrower one.
- Two inputs carry no stated licence: the Global Forest Watch workbook and ATREE's list of villages. Only figures read
  from them are used, and neither file is redistributed. Whether the Foundation may pass the layer on, and under what
  statement, is not decided.
- The layer shows Scheduled Tribe share and the development index as maps. The paper it takes its vocabulary from
  reports a community that did not favour the mapping of inequity; whether those two layers belong in what is shown is
  the Foundation's call (`docs/LAYER.md` §9).
- The layer's controls were exercised in Chrome and in Safari's engine. In the Safari application it was opened and
  read, not clicked, and on an earlier build than the one on disk. It has not been opened in Firefox, on a phone, in print, or on a machine with little memory
  (§10).

## 13. Where every figure comes from

This section is the script's own record of what it read. Paths are relative to the repository. The numbered folders (`10_units/` to `60_layer/`) are stage outputs: each is rebuilt by the script named in the `.provenance.json` beside it, and none is in git. Files under `.session_scratch_2026-10-05/` are **working files** of the sessions that made the pipeline. They are not stage outputs and no tracked script rebuilds them; the NIRv replication (§6) has no other record.

### 13.1 Figures in the text, in the order they first appear

| as printed | file | where in the file |
|---|---|---|
| 2026-10-10T22:33:10Z | this run | the UTC time at which this script ran |
| 2026-10-05T20:11:19Z | `10_units/units.provenance.json` | key `run_utc` |
| 2026-10-05T20:44:23Z | `20_degradation/hansen.provenance.json` | key `run_utc` |
| 2026-10-05T21:40:02Z | `20_degradation/corestack.provenance.json` | key `run_utc` |
| 2026-10-07T10:08:15Z | `20_degradation/agreement.provenance.json` | key `run_utc` |
| 41 of 41 checks passed | `scripts/verify_agreement.py` | its exit status and last line, run by this script as it wrote the document |
| 2026-10-05T20:22:49Z | `30_need/need.provenance.json` | key `run_utc` |
| 2026-10-05T20:25:06Z | `40_allocation/allocation.provenance.json` | key `run_utc` |
| passed | `scripts/verify_r620.py` | its exit status and last line, run by this script as it wrote the document |
| 2026-10-10T20:20:22Z | `50_gap/gap.provenance.json` | key `steps` → `08_build_gap_districts` → `run_utc` |
| 338 of 338 checks passed | `scripts/verify_gap.py` | its exit status and last line, run by this script as it wrote the document |
| 2026-10-09T04:08:22Z | `60_layer/layer.provenance.json` | key `run_utc` |
| 92 of 92 checks passed | `scripts/verify_layer.py` | its exit status and last line, run by this script as it wrote the document |
| and the page last opened and read in the Safari application on an earlier build, not on this one | `60_layer/decision_runs.json` | key `checks_not_run_in_this_pass`: the check in the Safari application is named there |
| 26.7 | `10_units/units.provenance.json` | computed here: outside-village km² ÷ km² of all units × 100. From: key `counts` → `km2_outside_any_revenue_village`; key `counts` → `km2` |
| 59.4 | `20_degradation/hansen_by_unit_level.csv` | column `share_of_all_forest_pct`; row where `unit_level` is 'outside_village' |
| 57.2 | `20_degradation/hansen_by_unit_level.csv` | column `share_of_all_loss_pct`; row where `unit_level` is 'outside_village' |
| 2,423 | `20_degradation/agreement_summary.csv` | column `n_assessed`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 137 | `20_degradation/agreement_summary.csv` | column `both`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 97 | `20_degradation/agreement_summary.csv` | column `both_expected_if_unrelated`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 1.80 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 1.10 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 2.91 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 11,468 | `10_units/units.provenance.json` | key `counts` → `units` |
| 7,976 | `10_units/units.provenance.json` | key `counts` → `lgd_panchayat_polygons` |
| 3,492 | `10_units/units.provenance.json` | key `counts` → `outside_village_polygons` |
| 154,929 | `10_units/units.provenance.json` | key `counts` → `km2` |
| 41,358 | `10_units/units.provenance.json` | key `counts` → `km2_outside_any_revenue_village` |
| 52,531 | `10_units/units.provenance.json` | key `counts` → `village_polygons` |
| 49,039 | `10_units/units.provenance.json` | key `counts` → `polygons_with_census_2011_code` |
| 8,152 | `30_need/need_source_check.csv` | rows counted by this script: every row (one for each LGD panchayat id of the mapping) |
| 176 | `30_need/need.provenance.json` | key `ids_with_no_unit_polygon` → `n` |
| 293,285 | `30_need/need.provenance.json` | key `ids_with_no_unit_polygon` → `population` |
| 65.2 | `40_allocation/panchayat_of_record_check.csv` | column `share_in_modal_polygon`; row where `scope` is 'all units' |
| 70.4 | `40_allocation/panchayat_of_record_check.csv` | column `share_in_modal_polygon`; row where `scope` is 'lgd_panchayat units only' |
| 67.2 | `40_allocation/panchayat_of_record_check.csv` | column `share_in_modal_polygon`; row where `scope` is 'CoRE Stack panchayat polygons' |
| 161 | `10_units/units.provenance.json` | key `counts` → `villages_with_no_lgd_panchayat` |
| 753 | `10_units/units.provenance.json` | key `counts` → `villages_with_no_lgd_panchayat_km2` |
| 3,460 | `10_units/outside_village_district.provenance.json` | key `counts` → `assigned_by` → `label` → `units` |
| 13 | `10_units/outside_village_district.provenance.json` | key `counts` → `assigned_by` → `two checks against the label` → `units` |
| 19 | `10_units/outside_village_district.provenance.json` | computed here: the two ways a polygon with no district name was assigned, added. From: key `counts` → `assigned_by` → `area majority: the polygon has no district name` → `units`; key `counts` → `assigned_by` → `neighbours: the polygon has no district name` → `units` |
| 139 | `10_units/outside_village_district.provenance.json` | key `counts` → `no_check_possible_neither_covered_nor_with_a_coded_neighbour` → `units` |
| 310 | `10_units/outside_village_district.provenance.json` | key `counts` → `no_check_possible_neither_covered_nor_with_a_coded_neighbour` → `km2` |
| 3 | `10_units/outside_village_district.provenance.json` | key `counts` → `ambiguous_the_one_flag` → `units` |
| 82 | `10_units/outside_village_district.provenance.json` | key `counts` → `flagged_not_moved_one_check_contradicts_the_assigned_district` → `units` |
| 99.92 | `10_units/outside_village_district.provenance.json` | key `how_good_each_source_is_on_villages_whose_district_is_known` → `name_gives_it_pct` |
| 79 | `10_units/outside_village_district.provenance.json`; `10_units/units.provenance.json` | computed here: outside-village km² where the area majority cannot be taken ÷ outside-village km² × 100. From: key `counts` → `area_majority` → `not_measurable` → `km2`; key `counts` → `km2_outside_any_revenue_village` |
| 4,310 | `20_degradation/hansen_by_unit_level.csv` | column `units_with_no_forest`; row where `unit_level` is 'all units' |
| 6,265 | `20_degradation/hansen_by_unit_level.csv` | column `units_with_under_1_ha_of_forest_including_none`; row where `unit_level` is 'all units' |
| 54.6 | `20_degradation/hansen_by_unit_level.csv`; `10_units/units.provenance.json` | computed here: units with under a hectare of forest ÷ all units × 100. From: column `units_with_under_1_ha_of_forest_including_none`; row where `unit_level` is 'all units'; key `counts` → `units` |
| −0.64 | `20_degradation/hansen.provenance.json` | key `checks_passed` → `tree_cover_2000_gt_T_against_global_forest_watch_gated` → `30` |
| −0.26 | `20_degradation/hansen.provenance.json` | key `checks_passed` → `loss_2001_2020_gt_30_against_global_forest_watch_gated` |
| 2 | `20_degradation/hansen.provenance.json` | key `checks_passed` → `tolerances` → `gfw_extent` |
| 10 | `20_degradation/hansen.provenance.json` | key `checks_passed` → `tolerances` → `gfw_loss_2001_2020` |
| 45.2 | `20_degradation/hansen.provenance.json` | key `checks_passed` → `loss_outside_the_mask_share` |
| 1,281 | `20_degradation/hansen_loss_by_canopy_band.csv` | computed here: loss in the two bands below the mask, added. From: column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'gt10le30'; column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 2,834 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'any_cover' |
| 1,948 | `20_degradation/hansen_by_unit_level.csv` | column `units_with_loss_but_none_in_the_mask`; row where `unit_level` is 'all units' |
| 826 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'eq0' |
| 90 | `20_degradation/hansen_loss_by_canopy_band.csv` | computed here: loss on land with no canopy in 2000 ÷ loss on the lowest band × 100. From: column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'eq0'; column `loss_km2_2001_2025`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 45 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2010`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 245 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2011_2017`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 627 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2018_2025`; row where `units` is 'all units' and `canopy_band` is 'le10' |
| 435 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2001_2010`; row where `units` is 'all units' and `canopy_band` is 'gt30' |
| 444 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2011_2017`; row where `units` is 'all units' and `canopy_band` is 'gt30' |
| 674 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_km2_2018_2025`; row where `units` is 'all units' and `canopy_band` is 'gt30' |
| 10,887 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `land_km2`; row where `units` is 'all units' and `canopy_band` is 'gt10le30' |
| 3.3 | `20_degradation/hansen_loss_by_canopy_band.csv` | column `loss_pct_of_band_land`; row where `units` is 'all units' and `canopy_band` is 'gt10le30' |
| 109,957 | `20_degradation/corestack_by_unit_level.csv` | column `tree_cover_start_km2`; row where `units` is 'all units' and `land` is 'all land' |
| 71 | `20_degradation/corestack_by_unit_level.csv` | computed here: tree cover at the start ÷ the units' land on the product's grid × 100. From: column `tree_cover_start_km2`; row where `units` is 'all units' and `land` is 'all land'; column `land_km2`; row where `units` is 'all units' and `land` is 'all land' |
| 24 | `20_degradation/corestack_by_unit_level.csv` | column `degradation_pct_of_tree_cover_start`; row where `units` is 'all units' and `land` is 'treecover2000 > 10' |
| 15 | `20_degradation/corestack_by_unit_level.csv` | column `improvement_pct_of_tree_cover_start`; row where `units` is 'all units' and `land` is 'treecover2000 > 10' |
| 0.54 | `20_degradation/corestack_by_unit_level.csv` | column `downward_share`; row where `units` is 'all units' and `land` is 'zone EPAHR, all land' |
| 0.75 | `20_degradation/corestack_by_unit_level.csv` | column `downward_share`; row where `units` is 'all units' and `land` is 'zone ECPHR, all land' |
| 50 | `20_degradation/corestack_by_unit_level.csv` | computed here: degradation class in outside-village units ÷ in all units × 100, all land. From: column `degradation_km2`; row where `units` is 'outside_village' and `land` is 'all land'; column `degradation_km2`; row where `units` is 'all units' and `land` is 'all land' |
| 189.2 | `20_degradation/corestack_reconciliation.csv` | column `this_pipeline`; row where `quantity` begins 'class -1, Mayurbhanj' |
| 189 | `20_degradation/corestack_reconciliation.csv` | column `published`; row where `quantity` begins 'class -1, Mayurbhanj' |
| 2 | `20_degradation/corestack.provenance.json` | key `checks_passed` → `mayurbhanj_2017_2021_against_the_producers_paper` → `tolerance` |
| 100 | `20_degradation/agreement.provenance.json` | key `definitions` → `floor` → `minimum_reference_ha` |
| 8,577 | `20_degradation/agreement_summary.csv` | column `n_insufficient_forest`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 156 | `20_degradation/agreement_by_zone.csv` | column `n_assessed`; row where `zone_model_of_the_units_valued_land` is 'both models' |
| 2.01 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'eastern_plateau_only' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 1.08 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `population` is 'eastern_plateau_only' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 3.45 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `population` is 'eastern_plateau_only' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 468 | `20_degradation/agreement_summary.csv` | column `n_excluded_by_zone_model`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 0.30 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_degradation`; row where `zone_model_of_the_units_valued_land` is 'EPAHR only' |
| 0.07 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_improvement`; row where `zone_model_of_the_units_valued_land` is 'EPAHR only' |
| 0.52 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_degradation`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 0.35 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_improvement`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 468 | `20_degradation/agreement_by_zone.csv` | column `n_assessed`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 5.38 | `20_degradation/agreement_by_zone.csv` | column `odds_ratio_degradation`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 184 | `20_degradation/agreement_summary.csv` | column `both`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 2,891 | `20_degradation/agreement_summary.csv` | column `n_assessed`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 116 | `20_degradation/agreement_summary.csv` | column `both_expected_if_unrelated`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 2.27 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 1.42 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 3.65 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 2.30 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 1.10 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 4.70 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 1.55 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 0.80 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 3.61 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 2.84 | `20_degradation/agreement_summary.csv` | column `odds_ratio_within_districts`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 1.92 | `20_degradation/agreement_summary.csv` | column `odds_ratio_within_districts_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 5.24 | `20_degradation/agreement_summary.csv` | column `odds_ratio_within_districts_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' |
| 2.06 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' |
| 1.34 | `20_degradation/agreement_summary.csv` | column `odds_ratio_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' |
| 3.33 | `20_degradation/agreement_summary.csv` | column `odds_ratio_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' |
| 8 | `20_degradation/agreement_by_zone.csv` | column `n_districts`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| −0.04 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_degradation_lo95`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 0.59 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_degradation_hi95`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| −0.16 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_improvement_lo95`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 0.44 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_improvement_hi95`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 0.27 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_improvement_lo95_units_singly`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 0.43 | `20_degradation/agreement_by_zone.csv` | column `spearman_hansen_vs_corestack_improvement_hi95_units_singly`; row where `zone_model_of_the_units_valued_land` is 'ECPHR only' |
| 50 | `20_degradation/agreement.provenance.json` | key `definitions` → `floor` → `sensitivity_floors_ha` → `1` |
| 0.73 | `20_degradation/agreement_summary.csv` | column `repeatability_of_that_class_2001_2025`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 50.0 and `units` is 'all units' |
| 0.84 | `20_degradation/agreement_summary.csv` | column `repeatability_of_that_class_2001_2025`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 2.63 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 10.0 and `units` is 'all units' |
| 10 | `20_degradation/agreement.provenance.json` | key `definitions` → `floor` → `sensitivity_floors_ha` → `0` |
| 2.20 | `20_degradation/agreement_summary.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 50.0 and `units` is 'all units' |
| 2,067 | `20_degradation/forest_floor_options.csv` | column `units_kept`; row where `floor_ha` is 100.0 |
| 97.0 | `20_degradation/forest_floor_options.csv` | column `forest_kept_pct`; row where `floor_ha` is 100.0 |
| 97.5 | `20_degradation/forest_floor_options.csv` | column `loss_kept_pct`; row where `floor_ha` is 100.0 |
| 9,401 | `10_units/units.provenance.json`; `20_degradation/forest_floor_options.csv` | computed here: all units less the units with at least the floor of forest. From: key `counts` → `units`; column `units_kept`; row where `floor_ha` is 100.0 |
| 774 | `20_degradation/agreement_summary.csv` | column `n_assessed`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' |
| 25 | `20_degradation/agreement_intervals.csv` | column `outside_village_assessed_district_has_no_possible_check`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 0 | `20_degradation/agreement_intervals.csv` | column `outside_village_assessed_moved_off_the_polygons_name`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 0 | `20_degradation/agreement_intervals.csv` | column `outside_village_assessed_ambiguous`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 2 | `20_degradation/agreement_intervals.csv` | column `outside_village_assessed_one_check_contradicts_the_district`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 1.17 | `20_degradation/agreement_intervals.csv` | column `lo95_lgd_districts_outside_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 2.99 | `20_degradation/agreement_intervals.csv` | column `hi95_lgd_districts_outside_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 0.99 | `20_degradation/agreement_intervals.csv` | column `width_districts_over_lgd_only_design`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 1.45 | `20_degradation/agreement_intervals.csv` | column `lo95_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' and `statistic` is 'odds_ratio' |
| 2.94 | `20_degradation/agreement_intervals.csv` | column `hi95_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' and `statistic` is 'odds_ratio' |
| 1.34 | `20_degradation/agreement_intervals.csv` | column `width_districts_over_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' and `statistic` is 'odds_ratio' |
| 1.11 | `20_degradation/agreement_intervals.csv` | column `lo95_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' and `statistic` is 'odds_ratio' |
| 2.11 | `20_degradation/agreement_intervals.csv` | column `hi95_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' and `statistic` is 'odds_ratio' |
| 1.45 | `20_degradation/agreement_intervals.csv` | column `lo95_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 2.25 | `20_degradation/agreement_intervals.csv` | column `hi95_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 2.3 | `20_degradation/agreement_intervals.csv` | column `width_districts_over_units_singly`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio' |
| 2.67 | `20_degradation/agreement_definitions.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -2, tree cover lost' |
| 1.88 | `20_degradation/agreement_definitions.csv` | column `odds_ratio_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -2, tree cover lost' |
| 3.76 | `20_degradation/agreement_definitions.csv` | column `odds_ratio_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -2, tree cover lost' |
| 133 | `20_degradation/corestack_by_unit_level.csv` | column `loss_km2`; row where `units` is 'all units' and `land` is 'treecover2000 > 10' |
| 9,091 | `20_degradation/corestack_by_unit_level.csv` | column `degradation_km2`; row where `units` is 'all units' and `land` is 'treecover2000 > 10' |
| 1.52 | `20_degradation/agreement_definitions.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -1 minus class 1' |
| 0.93 | `20_degradation/agreement_definitions.csv` | column `odds_ratio_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -1 minus class 1' |
| 2.78 | `20_degradation/agreement_definitions.csv` | column `odds_ratio_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -1 minus class 1' |
| 0.61 | `20_degradation/agreement_definitions.csv` | column `odds_ratio`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class 1, improvement (the placebo)' |
| 0.21 | `20_degradation/agreement_definitions.csv` | column `odds_ratio_lo95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class 1, improvement (the placebo)' |
| 1.35 | `20_degradation/agreement_definitions.csv` | column `odds_ratio_hi95`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class 1, improvement (the placebo)' |
| 485 | `20_degradation/agreement_summary.csv` | column `flagged_by_hansen`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 61 | `.session_scratch_2026-10-05/replicate_nirv/claim3_round2.json` *(working file)* | key `part2` → `units with >= 50 ha of treecover2000 > 10` → `n` |
| −0.79 | `.session_scratch_2026-10-05/replicate_nirv/claim3_round2.json` *(working file)* | key `part2` → `units with >= 50 ha of treecover2000 > 10` → `raw_` → `r_median` |
| 0.19 | `.session_scratch_2026-10-05/replicate_nirv/claim3_round2.json` *(working file)* | key `part2` → `units with >= 50 ha of treecover2000 > 10` → `std_` → `r_median` |
| 6.3 | `.session_scratch_2026-10-05/replicate_nirv/rate_dose.json` *(working file)* | key `part2` → `0.9` → `declining` |
| 5.8 | `.session_scratch_2026-10-05/replicate_nirv/rate_dose.json` *(working file)* | key `part2` → `1.0` → `declining` |
| 5.3 | `.session_scratch_2026-10-05/replicate_nirv/rate_dose.json` *(working file)* | key `part2` → `1.1` → `declining` |
| 24 | `.session_scratch_2026-10-05/replicate_nirv/leave_one_pass_out.json` *(working file)* | computed here: (declining flags lost + declining flags gained) ÷ declining flags before × 100, one image removed at random. From: key `part2` → `a random pass` → `date-standardised` → `declining_before`; key `part2` → `a random pass` → `date-standardised` → `declining_lost`; key `part2` → `a random pass` → `date-standardised` → `declining_gained` |
| 20 | `.session_scratch_2026-10-05/replicate_nirv/leave_one_pass_out.json` *(working file)* | computed here: (declining flags lost + declining flags gained) ÷ declining flags before × 100, one image removed at random. From: key `part3` → `a random pass` → `date-standardised` → `declining_before`; key `part3` → `a random pass` → `date-standardised` → `declining_lost`; key `part3` → `a random pass` → `date-standardised` → `declining_gained` |
| 7 | `.session_scratch_2026-10-05/replicate_nirv/claim7_round2_pd.json` *(working file)* | key `part2 treecover2000 > 10, date-standardised` → `reorderings_declining_at_or_above_observed` |
| 22 | `.session_scratch_2026-10-05/replicate_nirv/claim7_round2_pd.json` *(working file)* | key `part3 treecover2000 > 10, date-standardised` → `reorderings_declining_at_or_above_observed` |
| 11,468 | `20_degradation/degradation_by_unit.provenance.json` | key `table` → `blank_cells` → `nirv_slope` |
| 677,404 | `.session_scratch_2026-10-05/replicate_nirv/claim7_round2_pd.json` *(working file)* | key `part2 treecover2000 > 10, date-standardised` → `n_pixels` |
| 566,362 | `.session_scratch_2026-10-05/replicate_nirv/claim7_round2_pd.json` *(working file)* | key `part3 treecover2000 > 10, date-standardised` → `n_pixels` |
| 21 | `.session_scratch_2026-10-05/replicate_nirv/claim3_round2.json` *(working file)* | key `part3` → `units with >= 50 ha of treecover2000 > 10` → `n` |
| 34,766,888 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `totals_over_units` → `population` |
| 8,043,218 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `totals_over_units` → `households` |
| 8,895,006 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `totals_over_units` → `st_pop` |
| 25.6 | `30_need/need.provenance.json` | computed here: Scheduled Tribe population of the units ÷ their population × 100. From: key `tables` → `need_by_unit.csv` → `totals_over_units` → `st_pop`; key `tables` → `need_by_unit.csv` → `totals_over_units` → `population` |
| 41,974,218 | `30_need/need.provenance.json` | key `checks_passed` → `published_census_2011_totals` → `figures` → `population` |
| 3,492 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_all_units` → `population` → `blank` |
| 2,866 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2019` → `blank` |
| 19,334 | `30_need/need.provenance.json` | key `atree_list` → `qualifying_villages` → `n` |
| 1,308,898 | `30_need/need.provenance.json` | key `atree_list` → `qualifying_villages` → `st_households_estimated` |
| 9 | `30_need/need_construct_sensitivity.csv` | rows counted by this script: rules other than the construct itself |
| 0.46 | `30_need/need_construct_sensitivity.csv` | worked out by this script from its rows: the smallest `spearman_with_the_construct_across_units` among the other rules |
| 0.96 | `30_need/need_construct_sensitivity.csv` | worked out by this script from its rows: the largest `spearman_with_the_construct_across_units` among the other rules |
| 95 | `30_need/need.provenance.json` | key `checks_passed` → `census_villages_not_in_the_mapping` → `n` |
| 20,001 | `30_need/need.provenance.json` | key `checks_passed` → `census_villages_not_in_the_mapping` → `population` |
| 81 | `30_need/need_by_unit.csv` | rows counted by this script: LGD panchayat units where more than half the population is in villages with no polygon |
| 1,302,664 | `40_allocation/allocation.provenance.json` | key `dump` → `n_works` |
| 12,816.8 | `40_allocation/allocation.provenance.json` | key `dump` → `expenditure_total` |
| 1,294,160 | `40_allocation/allocation.provenance.json` | key `join` → `works_assigned` |
| 8,504 | `40_allocation/allocation.provenance.json` | key `join` → `works_unassigned` |
| 73.8 | `40_allocation/allocation.provenance.json` | key `join` → `expenditure_unassigned_inr` |
| 579 | `40_allocation/allocation.provenance.json` | key `checks_passed` → `district_fy_cells_exact` |
| 9 | `40_allocation/allocation.provenance.json` | key `checks_passed` → `categories_exact` |
| 97.8 | `40_allocation/assets_district_fy.csv`; `40_allocation/allocation.provenance.json` | computed here: expenditure on works started in or before FY2017-18 ÷ all expenditure × 100. From: worked out by this script from its rows: `expenditure_total` of rows whose `fy_work_start` is a year up to 2017-18; key `dump` → `expenditure_total` |
| 83 | `40_allocation/state_fy_r620_vs_dump.csv` | column `dump_capture_pct`; row where `fy` is '2016-17' |
| 3 | `40_allocation/state_fy_r620_vs_dump.csv` | column `dump_capture_pct`; row where `fy` is '2018-19' |
| 25,526 | `40_allocation/allocation.provenance.json` | key `dump` → `n_works_expenditure_na` |
| 15.1 | `40_allocation/allocation.provenance.json` | computed here: expenditure in the plantation category ÷ all expenditure × 100. From: key `dump` → `expenditure_plantation_category`; key `dump` → `expenditure_total` |
| 1.1 | `40_allocation/allocation.provenance.json` | computed here: expenditure on work types that name forest ÷ all expenditure × 100. From: key `dump` → `expenditure_forest_named_worktype`; key `dump` → `expenditure_total` |
| 28.7 | `40_allocation/allocation.provenance.json` | computed here: expenditure in the water construct ÷ all expenditure × 100. From: key `dump` → `expenditure_water`; key `dump` → `expenditure_total` |
| 24.2 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_plantation_share_pct`; row where `fy` is '2016-17' |
| 3.3 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_plantation_share_pct`; row where `fy` is '2018-19' |
| 40.1 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_water_share_of_nrm_pct`; row where `fy` is '2014-15' |
| 2014-15 | `40_allocation/state_fy_r620_vs_dump.csv` | column `fy`; row where `fy` is '2014-15' |
| 63.7 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_water_share_of_nrm_pct`; row where `fy` is '2024-25' |
| 4 | `40_allocation/state_fy_r620_vs_dump.csv` | rows counted by this script: `r620_last_updated` is 10/10/2020 |
| 13 | `40_allocation/state_fy_r620_vs_dump.csv` | rows counted by this script: every row (one for each financial year) |
| 10/10/2020 | `40_allocation/state_fy_r620_vs_dump.csv` | column `r620_last_updated`; row where `fy` is '2014-15' |
| 38 | `20_degradation/hansen_by_unit_level.csv` | column `forest_share_of_area_pct`; row where `unit_level` is 'outside_village' |
| 10 | `20_degradation/hansen_by_unit_level.csv` | column `forest_share_of_area_pct`; row where `unit_level` is 'lgd_panchayat' |
| 131,687 | `40_allocation/allocation.provenance.json` | key `join` → `works_in_outside_village_units` |
| 1,443.5 | `40_allocation/allocation.provenance.json` | key `join` → `expenditure_in_outside_village_units_inr` |
| 10.1 | `40_allocation/allocation.provenance.json` | computed here: works in outside-village units ÷ all works × 100. From: key `join` → `works_in_outside_village_units`; key `dump` → `n_works` |
| 11.3 | `40_allocation/allocation.provenance.json` | computed here: expenditure in outside-village units ÷ all expenditure × 100. From: key `join` → `expenditure_in_outside_village_units_inr`; key `dump` → `expenditure_total` |
| 1,048 | `40_allocation/allocation.provenance.json` | key `join` → `units_with_no_works` |
| 804 | `40_allocation/allocation.provenance.json` | key `join` → `units_with_no_works_by_level` → `outside_village` |
| 40.6 | `20_degradation/hansen_by_unit_level.csv` | computed here: read as it stands. From: column `share_of_all_forest_pct`; row where `unit_level` is 'lgd_panchayat' |
| 22.5 | `60_layer/layer.provenance.json` | key `outputs` → `both_bytes` |
| 6.0 | `60_layer/layer.provenance.json` | key `outputs` → `both_zipped_bytes` |
| 44 | `60_layer/layer.provenance.json` | key `table` → `fields_per_unit_in_the_panel` |
| Chrome/154.0.8037.99 | `60_layer/exercise_chrome.json` | key `summary` → `browser` |
| 53 | `60_layer/exercise_chrome.json` | key `summary` → `controls_as_expected` |
| 53 | `60_layer/exercise_chrome.json` | key `summary` → `controls_exercised` |
| 29 | `60_layer/exercise_chrome.json` | key `summary` → `units_clicked` |
| 1,276 | `60_layer/exercise_chrome.json` | key `summary` → `values_equal` |
| 1,276 | `60_layer/exercise_chrome.json` | key `summary` → `values_compared` |
| WebKit 21624.5.1.11.3 (the engine of Safari 27.0 on this machine) | `60_layer/exercise_webkit.json` | key `summary` → `browser` |
| 53 | `60_layer/exercise_webkit.json` | key `summary` → `controls_as_expected` |
| 53 | `60_layer/exercise_webkit.json` | key `summary` → `controls_exercised` |
| 29 | `60_layer/exercise_webkit.json` | key `summary` → `units_clicked` |
| 1,276 | `60_layer/exercise_webkit.json` | key `summary` → `values_equal` |
| 1,276 | `60_layer/exercise_webkit.json` | key `summary` → `values_compared` |
| the owner's instruction of 9 October 2026 for the batch that applies his rulings: no run in the Safari application, since no unit changes cell | `60_layer/decision_runs.json` | key `checks_not_run_in_this_pass`: `why` of the check in the Safari application |
| Safari 27.0 (the application) | `60_layer/exercise_safari.json` | key `summary` → `browser` |
| 2026-10-08T22:42:59Z | `60_layer/exercise_safari.json` | key `summary` → `layer_run_utc` |
| 48 | `60_layer/exercise_safari.json` | key `summary` → `addresses_as_expected` |
| 48 | `60_layer/exercise_safari.json` | key `summary` → `addresses_tried` |
| 29 | `60_layer/exercise_safari.json` | key `summary` → `units_opened_by_address` |
| 1,265 | `60_layer/exercise_safari.json` | key `summary` → `values_found` |
| 1,265 | `60_layer/exercise_safari.json` | key `summary` → `values_compared` |
| 30 | `60_layer/layer.provenance.json` | key `geometry` → `tolerance_m` |
| 120 | `60_layer/layer.provenance.json` | key `geometry` → `units_changed_by_more_than_5_pct` |
| 164 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `poverty_rate` → `blank` |
| 25 | `20_degradation/agreement_summary.csv` | column `n_districts`; row where `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| 6.8 | `20_degradation/corestack_reconciliation.csv` | column `difference_pct_of_published`; row where `quantity` is 'area per pixel with a value' |
| 123 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `st_share` → `blank` |
| 534 | `30_need/need.provenance.json` | key `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2011` → `blank` |
| 83 | `30_need/need.provenance.json` | key `checks_passed` → `panchayat_file` → `ids_where_it_holds_more` |
| 101 | `30_need/need.provenance.json` | key `checks_passed` → `secc` → `units` → `rate_resting_on_fewer_than_100_people` |
| 73 | `30_need/need.provenance.json` | key `checks_passed` → `secc` → `units` → `some_of_the_rate_from_a_shrid_shared_with_another_id` |
| , and on an earlier build than the one on disk | `60_layer/exercise_safari.json` | key `summary` → `layer_run_utc`, against the layer's own record |
| 67.1 | `50_gap/need_vs_allocation_summary.csv` | column `need_share_pct_where_r_below_0_5`; row where `comparison` is 'C1' |
| 5 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts_r_below_0_5`; row where `comparison` is 'C1' |
| 1.9 | `50_gap/need_vs_allocation_summary.csv` | column `need_share_pct_where_r_above_2`; row where `comparison` is 'C1' |
| 7,207.11 | `50_gap/need_vs_allocation_summary.csv` | column `sum_positive_gaps_lakh`; row where `comparison` is 'C1' |
| 30 | `50_gap/need_vs_allocation_summary.csv` | column `n_districts`; row where `comparison` is 'C1' |
| 0.67 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C1' |
| 0.38 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C1' |
| 0.84 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C1' |
| 0.00012 | `50_gap/need_vs_allocation_summary.csv` | column `p_permutation`; row where `comparison` is 'C1' |
| 0.57 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'B1' |
| 0.37 | `50_gap/need_vs_allocation_summary.csv` | column `rho`; row where `comparison` is 'C12' |
| 0.01 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_lo`; row where `comparison` is 'C12' |
| 0.63 | `50_gap/need_vs_allocation_summary.csv` | column `ci95_hi`; row where `comparison` is 'C12' |
| 0.226 | `50_gap/panel_models.csv` | column `coefficient`; row where `id` is 'P1' |
| −0.065 | `50_gap/panel_models.csv` | column `wcb_ci95_lo`; row where `id` is 'P1' |
| 0.893 | `50_gap/panel_models.csv` | column `wcb_ci95_hi`; row where `id` is 'P1' |
| 0.383 | `50_gap/panel_models.csv` | column `wcb_p`; row where `id` is 'P1' |
| 360 | `50_gap/panel_models.csv` | column `n`; row where `id` is 'P1' |
| −0.14 | `50_gap/unit_history_models.csv` | column `coefficient`; row where `id` is 'H1' |
| −0.48 | `50_gap/unit_history_models.csv` | column `wcb_ci95_lo`; row where `id` is 'H1' |
| 0.20 | `50_gap/unit_history_models.csv` | column `wcb_ci95_hi`; row where `id` is 'H1' |
| 0.379 | `50_gap/unit_history_models.csv` | column `wcb_p`; row where `id` is 'H1' |
| 2,889 | `50_gap/unit_history_models.csv` | column `n_units`; row where `id` is 'H1' |
| 1,121 | `50_gap/unit_history_models.csv` | column `n_exposed`; row where `id` is 'H1' |

### 13.2 Tables, in the order they appear

Every cell of a table that is not a typed label was read from the file and columns given here.

| table | cells read | file | columns or keys | rows |
|---|---|---|---|---|
| §3, forest and loss by kind of unit | 24 | `20_degradation/hansen_by_unit_level.csv` | `n_units`, `area_km2`, `forest_km2`, `forest_share_of_area_pct`, `share_of_all_forest_pct`, `loss_km2_2001_2025`, `share_of_all_loss_pct`, `loss_share_of_forest_pct` | `unit_level` is 'outside_village'; `unit_level` is 'lgd_panchayat'; `unit_level` is 'all units' |
| §3.1, loss by band of canopy | 35 | `20_degradation/hansen_loss_by_canopy_band.csv` | `land_km2`, `loss_km2_2001_2025`, `share_of_these_units_loss_pct`, `loss_pct_of_band_land`, `loss_km2_2001_2010`, `loss_km2_2011_2017`, `loss_km2_2018_2025` | `units` is 'all units' and `canopy_band` is 'gt30'; `units` is 'all units' and `canopy_band` is 'gt10le30'; `units` is 'all units' and `canopy_band` is 'le10'; `units` is 'all units' and `canopy_band` is 'eq0'; `units` is 'all units' and `canopy_band` is 'any_cover' |
| §4, CoRE Stack classes | 30 | `20_degradation/corestack_by_unit_level.csv` | `tree_cover_start_km2`, `degradation_km2`, `improvement_km2`, `net_degradation_km2`, `downward_share`, `downward_share_lo_95`, `downward_share_hi_95` | `units` is 'all units' and `land` is 'all land'; `units` is 'all units' and `land` is 'treecover2000 > 10'; `units` is 'outside_village' and `land` is 'treecover2000 > 10'; `units` is 'lgd_panchayat' and `land` is 'treecover2000 > 10'; `units` is 'all units' and `land` is 'zone EPAHR, all land'; `units` is 'all units' and `land` is 'zone ECPHR, all land' |
| §5.1, the result two ways | 45 | `20_degradation/agreement_summary.csv` | `n_assessed`, `both`, `both_expected_if_unrelated`, `odds_ratio`, `odds_ratio_lo95`, `odds_ratio_hi95`, `odds_ratio_within_districts`, `odds_ratio_within_districts_lo95`, `odds_ratio_within_districts_hi95` | `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village'; `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units'; `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat'; `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village'; `population` is 'eastern_plateau_only' and `window` is 'common_2017_2023' and ` ... |
| §5.2, by zone model | 21 | `20_degradation/agreement_by_zone.csv` | `n_assessed`, `n_districts`, `reference_land_pct_of_assessed`, `odds_ratio_degradation`, `spearman_hansen_vs_corestack_degradation`, `spearman_hansen_vs_corestack_degradation_lo95`, `spearman_hansen_vs_corestack_degradation_hi95`, `spearman_hansen_vs_corestack_improvement`, `spearman_hansen_vs_corestack_improvement_lo95`, `spearman_hansen_vs_corestack_improvement_hi95`, `spearman_hansen_vs_corestack_improvement_lo95_units_singly`, `spearman_hansen_vs_corestack_improvement_hi95_units_singly` | `zone_model_of_the_units_valued_land` is 'EPAHR only'; `zone_model_of_the_units_valued_land` is 'ECPHR only'; `zone_model_of_the_units_valued_land` is 'both models' |
| §5.3, by floor | 24 | `20_degradation/agreement_summary.csv` | `minimum_reference_ha`, `n_assessed`, `odds_ratio`, `odds_ratio_lo95`, `odds_ratio_hi95`, `lowest_land_class_admitted_ha`, `repeatability_of_that_class_2001_2025`, `repeatability_of_that_class_2017_2023` | `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 10.0 and `units` is 'all units'; `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 10.0 and `units` is 'all units'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 50.0 and `units` is 'all units'; `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 50.0 and `units` is 'all units'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units'; `population` is 'all_assessed' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' |
| §5.4, three designs of resampling | 25 | `20_degradation/agreement_intervals.csv` | `estimate`, `lo95_districts`, `hi95_districts`, `lo95_lgd_districts_outside_singly`, `hi95_lgd_districts_outside_singly`, `lo95_units_singly`, `hi95_units_singly`, `width_districts_over_lgd_only_design` | `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'lgd_panchayat' and `statistic` is 'odds_ratio'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'outside_village' and `statistic` is 'odds_ratio'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'odds_ratio_within_districts_mantel_haenszel'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `statistic` is 'spearman_hansen_vs_corest ... |
| §5.5, by CoRE Stack reading | 20 | `20_degradation/agreement_definitions.csv` | `corestack_flag_is`, `both`, `both_expected_if_unrelated`, `odds_ratio`, `odds_ratio_lo95`, `odds_ratio_hi95` | `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -1 (delivered)'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'classes -1, 3 and 4'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -1 minus class 1'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `corestack_flag_is` is 'class -2, tree cover lost'; `population` is 'east_coast_excluded' and `window` is 'common_2017_2023' and `minimum_reference_ha` is 100.0 and `units` is 'all units' and `cores ... |
| §7, what is blank | 15 | `30_need/need.provenance.json` | `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `st_share` → `n`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `st_share` → `blank`, `tables` → `need_by_unit.csv` → `columns_all_units` → `population` → `blank`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2011` → `n`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2011` → `blank`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2019` → `n`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `adi_2019` → `blank`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `poverty_rate` → `n`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `poverty_rate` → `blank`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `forest_dependent_households` → `n`, `tables` → `need_by_unit.csv` → `columns_lgd_panchayat_units_only` → `forest_dependent_households` → `blank` |  |
| §8, the state report by year | 91 | `40_allocation/state_fy_r620_vs_dump.csv` | `fy`, `r620_exp_all_lakh`, `r620_nrm_share_pct`, `r620_plantation_share_pct`, `r620_water_share_of_nrm_pct`, `dump_capture_pct`, `r620_last_updated` | `fy` is '2014-15'; `fy` is '2015-16'; `fy` is '2016-17'; `fy` is '2017-18'; `fy` is '2018-19'; `fy` is '2019-20'; `fy` is '2020-21'; `fy` is '2021-22'; `fy` is '2022-23'; `fy` is '2023-24'; `fy` is '2024-25'; `fy` is '2025-26'; `fy` is '2026-27' |

### 13.3 Files read

| file | bytes | sha256 | the run stamp it carries |
|---|---|---|---|
| `.session_scratch_2026-10-05/replicate_nirv/claim3_round2.json` *(working file)* | 4,375 | `92c87296a5139a7b` | 2026-10-06T01:43:15.516879+00:00 |
| `.session_scratch_2026-10-05/replicate_nirv/claim7_round2_pd.json` *(working file)* | 9,461 | `48f34ef60361ae9c` | 2026-10-06T01:31:45.706732+00:00 |
| `.session_scratch_2026-10-05/replicate_nirv/leave_one_pass_out.json` *(working file)* | 4,371 | `c1dc4a55f6eda921` | 2026-10-06T01:45:00.949342+00:00 |
| `.session_scratch_2026-10-05/replicate_nirv/rate_dose.json` *(working file)* | 5,216 | `26946f5ceefcc890` | 2026-10-06T01:42:07.996873+00:00 |
| `10_units/outside_village_district.provenance.json` | 7,734 | `e5e02aa04ca51004` | 2026-10-07T08:21:28Z |
| `10_units/units.provenance.json` | 1,706 | `7a7aa9077c79b68d` | 2026-10-05T20:11:19Z |
| `20_degradation/agreement.provenance.json` | 10,756 | `0c0182e3a357255c` | 2026-10-07T10:08:15Z |
| `20_degradation/agreement_by_zone.csv` | 1,995 | `df07ed89f94db597` | - |
| `20_degradation/agreement_definitions.csv` | 7,739 | `9cb8ee2170c59e80` | - |
| `20_degradation/agreement_intervals.csv` | 7,950 | `558d8d0f517e9bce` | - |
| `20_degradation/agreement_summary.csv` | 32,470 | `6e0fb5e26102e318` | - |
| `20_degradation/corestack.provenance.json` | 12,320 | `8f03282fa339d4a3` | 2026-10-05T21:40:02Z |
| `20_degradation/corestack_by_unit_level.csv` | 4,028 | `b68eb9b7c0fd2a21` | - |
| `20_degradation/corestack_reconciliation.csv` | 1,558 | `05d64cc85fe25926` | - |
| `20_degradation/degradation_by_unit.provenance.json` | 21,969 | `f5f067c73aec7399` | 2026-10-06T21:26:10Z |
| `20_degradation/forest_floor.provenance.json` | 1,891 | `3691b99a971dda8c` | 2026-10-07T09:59:25Z |
| `20_degradation/forest_floor_options.csv` | 1,671 | `10fd206612c3c538` | - |
| `20_degradation/hansen.provenance.json` | 8,637 | `d6e816740e7dd41a` | 2026-10-05T20:44:23Z |
| `20_degradation/hansen_by_unit_level.csv` | 1,090 | `46d77ed69eac08ca` | - |
| `20_degradation/hansen_loss_by_canopy_band.csv` | 2,002 | `c6d479eb7492ccf5` | - |
| `30_need/need.provenance.json` | 15,023 | `8024375c3a69546b` | 2026-10-05T20:22:49Z |
| `30_need/need_by_unit.csv` | 1,212,483 | `0fc54bd7eb2a6d84` | - |
| `30_need/need_construct_sensitivity.csv` | 926 | `1c83f58a63180cab` | - |
| `30_need/need_source_check.csv` | 762,758 | `0d6aa40cbe8866d3` | - |
| `40_allocation/allocation.provenance.json` | 15,953 | `bf1e7052fa4ba2c7` | 2026-10-05T20:25:06Z |
| `40_allocation/allocation_by_unit.csv` | 1,072,899 | `3f81d2d3edefda9f` | - |
| `40_allocation/assets_district_fy.csv` | 65,174 | `5e8dcd030f973f36` | - |
| `40_allocation/panchayat_of_record_check.csv` | 363 | `f36e1bd24b73ce67` | - |
| `40_allocation/state_fy_r620_vs_dump.csv` | 2,707 | `bd845de7118bc579` | - |
| `50_gap/gap.provenance.json` | 48,350 | `71e13ff7968600ae` | - |
| `50_gap/need_vs_allocation_summary.csv` | 5,000 | `77831ac32e2c5717` | - |
| `50_gap/panel_models.csv` | 5,072 | `a8c7ef7ef69aa7dd` | - |
| `50_gap/unit_history_models.csv` | 6,920 | `f2684839d7db5310` | - |
| `60_layer/decision_runs.json` | 5,712 | `652a4083b557d2d5` | - |
| `60_layer/exercise_chrome.json` | 26,807 | `a4ecf3b563655739` | 2026-10-09T04:13:56Z |
| `60_layer/exercise_safari.json` | 17,705 | `b7584629baaa8553` | 2026-10-08T22:53:16Z |
| `60_layer/exercise_webkit.json` | 27,298 | `8d51b15504dcac7e` | 2026-10-09T04:18:45Z |
| `60_layer/layer.provenance.json` | 24,478 | `27ffbf7609d05e5c` | 2026-10-09T04:08:22Z |

### 13.4 Statements tested before they were written

Each of these is something the text says in words. The script tested it against the figures and would have stopped had it failed.

- stage 4 is built: its tables are in `50_gap/`, every gate of every step of it that carries gates passed, and its account is `docs/GAP.md`
- stage 4, the headline comparison: the rank correlation of need with post-period plantation money is above zero, and so is the benchmark's with all expenditure
- stage 4: the benchmark's interval overlaps the headline's; with district size taken out of both sides the rank correlation is lower than either, and its interval still lies above zero
- stage 4: the intervals of its panel headline and of its unit headline both include zero
- the headline rows of `agreement_summary.csv` are the ones marked delivered
- more than half the units have under a hectare of forest
- loss on the lowest canopy band rises several times faster across the three periods than loss in the mask
- the East Coast model's downward share is above the Eastern Plateau model's, and their intervals do not overlap
- about half of the degradation class is in outside-village units
- the reconciliation table has one row for Mayurbhanj
- with the straddling units left out as well, the interval for all units still lies above one
- for all units the interval of the odds ratio lies above one in both versions
- the headline odds ratio is the smaller of the two
- for LGD panchayat units alone the headline interval includes one
- for LGD panchayat units alone, with every unit kept, the interval lies above one
- for LGD panchayat units alone, within districts, the headline interval lies above one
- for outside-village units alone the headline interval lies above one
- fewer than half the units Hansen flags in the headline comparison are flagged by CoRE Stack too
- the table by zone model is at the ruled floor, in the headline window, with the flags of all assessed units
- the East Coast correlation with degradation also has an interval that reaches zero when whole districts are resampled
- under the Eastern Plateau model Hansen's rate is related to degradation and not to improvement
- under the East Coast model Hansen's rate goes with improvement, several times more strongly than under the other model
- the units under the East Coast model are where the two measures agree most
- the East Coast placebo's interval reaches zero when whole districts are resampled, and excludes it when units are resampled singly
- the repeatability of the smallest units admitted rises with the floor
- the stricter the floor, the smaller the odds ratio
- the floor in the agreement record is the floor the floor table calls ruled
- for all units the two clusterings give intervals of nearly the same width, and both lie above one
- resampling units singly gives a much narrower interval than resampling districts
- for outside-village units alone the district interval is materially wider than the one from resampling units singly, and both lie above one
- for LGD panchayat units alone, resampling units singly gives an interval above one where resampling districts does not
- the table of definitions has one row for each CoRE Stack reading of the headline comparison
- of the readings other than the placebo, the lost class gives the largest odds ratio and degradation net of improvement the smallest
- for degradation net of improvement the interval includes one
- on the compared land the lost class is a small fraction of the degradation class
- in the headline population the improvement flag coincides with Hansen's no more often than chance
- the first design's yearly value follows the date of the images, and the redesigned value does not
- the declining share falls as the fitted seasonal rate is scaled up
- re-ordered seasons reach the observed declining share more often than one time in twenty in both samples
- the assembled table records NIRv as pending
- the census rows equal the published state totals on population, rural population, urban population, Scheduled Caste and Scheduled Tribe population
- households were not checked against a published total
- the sensitivity table has one row for the construct itself
- nearly all of the record's expenditure is on works started in or before FY2017-18
- the record holds a small fraction of the state report's expenditure for FY2018-19
- no work in the record reports person-days
- plantation is under one per cent of expenditure in the state report in every year after FY2018-19
- the years of the state report that carry the oldest stamp are its high-plantation years
- the last year of the state report is a part year, and the only one
- the layer's default minimum of forest is the ruled floor
- the columns the layer leaves out on purpose are the SHRUG-derived ones
- the hand check (Chrome) was made on the build of the layer that is on disk
- the files the hand check (Chrome) opened have the sha256 the layer's record gives
- the hand check (Chrome) met no script error
- in the hand check every control did what it should and every displayed value equalled the stage tables
- the hand check (WebKit) was made on the build of the layer that is on disk
- the files the hand check (WebKit) opened have the sha256 the layer's record gives
- the hand check (WebKit) met no script error
- in the hand check every control did what it should and every displayed value equalled the stage tables
- the check in the Safari application was not made on the build of the layer that is on disk, and the runner's record of that build names it as left out with a reason, every check it did run having passed
- in the Safari application every address showed what it should and every value a panel should show was in the page's text
- the units opened in the Safari application are the units clicked in Chrome
- the reconciliation table has one row for the area of a pixel
- this pipeline's area for a CoRE Stack pixel is below the producers' nominal one

### 13.5 Totals that two places both carry, compared

- LGD panchayat units and outside-village units add up to the units
- units in the Hansen table and in the unit layer
- LGD panchayat ids that have a polygon, and LGD panchayat units
- ids with no polygon, in the need record and in its check table
- the four ways a district was assigned add up to the outside-village units
- outside-village districts, no_possible_check: the agreement record and the district record
- outside-village districts, moved_off_the_polygons_name: the agreement record and the district record
- outside-village districts, ambiguous: the agreement record and the district record
- loss outside the mask, in the Hansen record and in the band table (to within 0.02)
- loss in the mask, in the band table and in the table by unit type (to within 0.01)
- units compared, left out by zone model and with too little forest add up to the units
- units compared in the headline, in the summary table and in the agreement record
- every unit kept: units compared are the headline's plus those left out
- units under the East Coast model only, in the zone table and left out of the headline
- units under the floor of forest, here and in the layer's own count
- the primary interval of the headline odds ratio, in the summary table and in the table of intervals (to within 1e-09)
- outside-village units compared, in the table of intervals and in the summary
- units with a blank NIRv cell, and all units
- population summed over the rows of the need table, and the total in its record
- units blank in the need table's population column, and outside-village units
- `st_share`: units with a value and units blank add up to the LGD panchayat units
- `st_share`: blank in every outside-village unit
- `adi_2011`: units with a value and units blank add up to the LGD panchayat units
- `adi_2011`: blank in every outside-village unit
- `adi_2019`: units with a value and units blank add up to the LGD panchayat units
- `adi_2019`: blank in every outside-village unit
- `poverty_rate`: units with a value and units blank add up to the LGD panchayat units
- `poverty_rate`: blank in every outside-village unit
- works placed in a unit and works in none add up to the works
- works summed over the rows of the table by unit, and the works placed
- expenditure summed over the rows of the table by district and year, and the record's total (to within 1)
- district-by-year cells that were exact, and the rows of the table by district and year

### 13.6 Digits the text was allowed to carry

The text itself may hold no digit except inside a code span (a file, a column, a threshold written as code) and in: a date; a financial year; a year; the number of a heading; a reference to a section; the number of a stage of the pipeline; a name: a satellite, a report, a licence, a datum. Everything else that is a number came from a file.

*272 figures and 10 tables (330 cells) from 38 files; 64 statements tested; 32 totals compared. Written 2026-10-10T22:33:10Z by `scripts/write_results.py` (sha256 `b918073042879cfc`).*

## 14. Stage 4: need against allocation

*Added on 10 October 2026, after the section that says where every figure comes from, so that no section above changed
its number. Its figures are listed in §13 with the others.*

The fourth stage was built on 10 October 2026 as the project owner specified it that day. Its account is `docs/GAP.md`,
written from the tables in `50_gap/` by `scripts/write_gap.py`; only its three headline rows are given here. **It
describes where money went relative to where forest was lost. It does not say why.**

- **`C1`, the comparison across districts.** Need is the forest loss of the years 2018 to 2025 in the units where loss is
  recorded; allocation is plantation expenditure of FY2018-19 to FY2025-26 in the state report. 67.1 per cent
  of the need lies in 5 districts whose share of the money is under half their share of the need, and
  1.9 per cent in districts with more than twice their share. The same money distributed by need would move
  7,207.11 lakh rupees; that is not a requirement. Across the 30 districts the rank correlation of need
  and allocation is 0.67 (`95 %` interval 0.38 to 0.84; permutation p 0.00012), and it is not read
  alone. The same need against all the scheme's expenditure, which is what district size alone gives, has
  0.57, with an interval that overlaps the headline's. With size taken out of both sides the rank correlation is
  0.37 (0.01 to 0.63).
- **`P1`, the district-year panel.** Within a district and a period, plantation's share of the district's expenditure
  against the forest loss of the year before: 0.226 percentage points for every `100 ha` (wild-cluster-bootstrap
  interval −0.065 to 0.893; p 0.383; 360 district-years). The interval includes zero.
- **`H1`, units within districts.** Units that had forest-named works by FY2017-18 against units of the same district
  that had none, given their forest and their earlier loss: −0.14 percentage points of the forest at the start of
  2018 lost in the years 2018 to 2025 (interval −0.48 to 0.20; p 0.379; 2,889 units, 1,121 of them
  with such works). The interval includes zero. It is an association: planners sited the works.

`scripts/verify_gap.py`, which imports nothing from the scripts that built the tables, recomputed the figures of
every table the stage's steps write: 338 of 338 checks passed. What it does not hold is in `docs/GAP.md` §14.

**What this changes in the sections above.** §11 says forest-rights titles are in no stage. The fourth stage sets the
state's district table of community titles beside need (`docs/GAP.md` §10); it still joins no title to a unit, since
titles are not mapped. §9 says its finding stands whatever stage 4 turns out to be: it does, and the fourth stage
counts how much of the need lies on outside-village land.
