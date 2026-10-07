# The analysis unit

*Stage 0. Rulings of 5 October 2026; every figure below is from `10_units/*.provenance.json`,
`40_allocation/*.provenance.json` or the mapping file itself.*

## The unit is an LGD panchayat id, not a gram panchayat

The pipeline's unit is the `Panchayat_ID` of `00_raw/02_mgnrega/mis_panel/LGD_village_panchayat_mapping.csv`:
every village polygon carrying one id is dissolved into one polygon. It is called `lgd_panchayat` in code,
column values, file names and text. It must not be called a GP.

The reason is in the mapping file. For Odisha it holds:

| | |
|---|---|
| distinct `Panchayat_ID` | 8,152 |
| distinct (panchayat name, Census-2011 sub-district) pairs | 8,152 — one per id |
| distinct (panchayat name, district) pairs | 6,645 |
| ids whose panchayat name is the literal `None` | 162 ids, 968 villages |
| ids that have at least one village polygon, i.e. units | 7,976 |

So the id is a running index over panchayat name **within a sub-district**. A gram panchayat whose villages
lie in two sub-districts is two ids and two units. The 162 `None` ids are one-per-sub-district buckets of
villages with no named panchayat; they are units too, and they are not panchayats of any kind.
(176 ids have no village polygon in the DataMeet layer and so no unit.)

## How many gram panchayats Odisha actually has

**6,794**, on the Panchayati Raj & Drinking Water Department's own count:

> "Social Audit of all 6794 GPs under MGNREGA have been completed during FY: 2023-24."
> — Government of Odisha, Panchayati Raj & Drinking Water Department, *Annual Activity Report … for the year
> 2023-24*. <https://panchayat.odisha.gov.in/sites/default/files/2024-05/AAR%20%282023-24%29%20English.pdf>,
> fetched 5 October 2026 (PDF sha256 `d2516de3931f00a6…`).

The same department's 2022-23 report gives the 2022 panchayat election as electing "6794 Sarpanches …
excluding the office of Sarpanch and 23 Ward Members of Dhinkia Gram Panchayat", which implies 6,795 with
Dhinkia. <https://panchayat.odisha.gov.in/sites/default/files/2024-05/AAR_2022-23%29_English.pdf>
(sha256 `8cdfb49b029b784f…`). The one-panchayat difference does not move the ratios below at three decimals.

**Cross-check, verified by the project owner (October 2026).** Comptroller and Auditor General of India,
*Audit Report on Local Bodies, Government of Odisha* (2023), Chapter 1 "Overview of PRIs in Odisha",
Table 1.1 "State profile": **6,794 Gram Panchayats, 314 Panchayat Samitis, 30 Zilla Parishads**, sourced
there to Census 2011 and the Panchayati Raj & Drinking Water Department. The 314 matches the block count that
R6.20 prints for all 13 years (`00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv`;
`scripts/verify_r620.py` enforces it), so two unrelated documents agree on the block count as well as on the
panchayat count.

This reference was read and verified by the project owner, not by the pipeline. The report could not be
fetched from this machine on 5 October 2026 (cag.gov.in timed out, saiindia.gov.in refused the connection),
so it is not quoted here and no copy is in `00_raw/`.

Not checked against the Local Government Directory itself: its report download sits behind a captcha form.
An older figure in circulation, 6,209, comes from a 2016 audit report and predates the 2017 reorganisation;
the audit office's site refused connections on 5 October 2026, so it is not quoted here.

## The over-count

| | count | per gram panchayat (6,794) |
|---|---|---|
| LGD panchayat ids in the mapping | 8,152 | **1.200** |
| LGD panchayat units (ids with a polygon) | 7,976 | **1.174** |
| distinct (name, district) pairs in the mapping | 6,645 | 0.978 |

There are about 17 % more units than gram panchayats. The over-count is not even: it arises wherever a
panchayat straddles a sub-district line. Anything stated "per panchayat" from this pipeline is per LGD
panchayat unit and should say so. The name-and-district count (6,645) is *below* the true number because
different panchayats in one district can share a name; it is not an estimate of the number of panchayats.

## The area of the layer — stated once, here

**The base layer covers 154,929.33 km², ellipsoidal, WGS84** (the area of each polygon on the WGS84 ellipsoid,
geodesic polygon area, summed over the 11,468 units; `scripts/01_build_units.py`, 6 October 2026). Every
`area_ha` in `10_units/` is on that basis. This figure is frozen: quote it from here.

| | km², ellipsoidal, WGS84 |
|---|---|
| base layer `units.gpkg` (`--outside keep`), 11,468 units | **154,929.33** |
| of which the 7,976 LGD panchayat units (= `units_outside_drop.gpkg`) | 113,571.01 |
| of which the 3,492 outside-village units | 41,358.31 (26.7 %) |
| `units_outside_nearest.gpkg`, 7,976 units | 154,929.33 |
| the 52,531 village polygons the layers are built from | 155,682.03 |
| 161 coded villages with no row in the mapping, in no layer | 752.70 |

**It is not validated against Odisha's official 155,707 km², and must not be.** That is a surveyed total,
not an ellipsoidal computation of these shapes, and the polygons never claimed to tile the state. The
difference is 778 km².

Until 6 October 2026 the areas were computed in UTM zone 45N: 155,161 km² for the base layer, 41,437 km²
outside villages, 113,724 km² for `drop`, 155,917 km² for the village polygons, 755 km² unmapped. UTM 45N is
exact on its central meridian, 87°E, and stretches areas west of it: 0.15 % too large over the layer and
0.67 % too large west of 82°E, where the forest is. That is a longitude-correlated bias in the denominator of
every per-hectare measure, in a study that compares the forested west and south with the rest. The rebuild
changed `area_ha` and nothing else: every unit's geometry is byte-identical and so is every other column.

## The outside-village land, and the base layer

3,492 of the 52,531 village polygons carry no Census-2011 code.
`--outside keep` is the base layer (`10_units/units.gpkg`): each such block is its own unit. `nearest` and
`drop` are kept as sensitivity layers.

| layer | file | units | works assigned | ₹ crore assigned | works in no unit |
|---|---|---|---|---|---|
| keep (base) | `units.gpkg` | 11,468 | 1,294,160 | 12,743.0 | 8,504 |
| nearest | `units_outside_nearest.gpkg` | 7,976 | 1,294,160 | 12,743.0 | 8,504 |
| drop | `units_outside_drop.gpkg` | 7,976 | 1,162,473 | 11,299.5 | 140,191 |

n = 1,302,664 geotagged works and ₹12,816.8 crore in every row.

- The land is not empty: under `keep`, 131,687 works (₹1,443.5 crore) are geotagged inside it.
- `nearest` is arbitrary for almost all of it: 2,453 of the 3,492 blocks touch two or more LGD panchayat
  polygons, and they hold 95% of the land. Under `nearest`, 29,784 works land in a unit of a different
  district from the file they came from, against 8,366 under `keep`.
- 161 coded villages have no row in the mapping and are in no layer.
- Outside-village units have no census rows, so stage 2 leaves every column blank for them.

## A district for each outside-village unit

*Added 7 October 2026 and redone the same day after review. `scripts/01_assign_outside_district.py`, run 2026-10-07T08:21:28Z;
every figure is from `10_units/outside_village_district.csv`, its summary or its provenance record. n = 3,492 units,
41,358.3 km².*

The outside-village units have no Census-2011 code, so `pc11_district_code` is blank for them in `units.gpkg`. The
instruction was to assign a district "by spatial majority against the district boundaries already in 00_raw".

**What `00_raw/` holds.** No file of district boundaries. One file of polygons that carry a district code: the
panchayat polygons of `00_raw/04_boundaries/corestack_gp_odisha.json` (7,910 polygons, 30 districts). They are not wall
to wall. They cover **35.1 per cent of the outside-village land** — that land is where no panchayat is — so a majority against
them can be taken for some units and not for others. And every DataMeet polygon carries the *name* of its district as
of the 2001 Census.

*Correction.* The first version of this section, and of the script, said the DataMeet layer was the only district
geometry among the inputs. That was wrong: the panchayat file was there, and stage 3 already read it. It also took a
unit's district from its neighbours on one check alone and from the tally that the layer's faults contaminate. The
review of 7 October found all three (`docs/DEGRADATION.md` §9). 21 units (63.9 km²) have a different district now than in that version; the per-district figures of the layer and of the summary table moved with them.

**Three sources, and how good each is where the truth is known.** The coded villages have a district of their own
from their Census code, so each source can be scored on them:

| source of a district | what it is | scored on coded villages |
|---|---|---|
| the polygon's own name | the 2001 district name on the DataMeet polygon, turned into a 2011 code through the polygons that carry both (30 names, 30 codes, one to one) | gives the village's own district for **99.92 per cent** of 49,039 |
| the area majority — the method asked for | the share of the unit's own area on panchayat polygons of each district; taken as measurable where at least half the unit is covered | **97.88 per cent** of the 39,329 villages at least half covered |
| the neighbours | the share, by district, of a 100 m collar round the unit that falls on coded villages — tallied by their 2001 names, and again by their 2011 codes | — |

The name is the better of the two where they can be compared, so **the rule** is:

1. A unit takes the district its polygon names.
2. The name is overridden only when *both* checks contradict it and agree with each other: no coded village of the
   named district lies in the collar by either tally, the unit is at least half covered and its area majority is
   another district, and that district is the neighbours' largest.
3. A polygon with no name takes the area majority where it is at least half covered, and otherwise its neighbours'
   largest district.

| a unit's district is | units | km² |
|---|---|---|
| the district its polygon names | 3,460 | 41,345.1 |
| another district: both checks contradict the name and agree with each other | 13 | 8.5 |
| the area majority — the polygon names no district | 12 | 0.9 |
| its neighbours' district — the polygon names none and is less than half covered | 7 | 3.8 |
| **all outside-village units** | **3,492** | **41,358.3** |

**The area majority, where it can be taken.** Measurable for 2,170 units — but they are the small ones, 8,542 km²,
21 per cent of the land. For the other 1,322 units, 32,816 km², it cannot be taken: 251 of them touch no panchayat
polygon at all. Where it is measurable it gives the assigned district in 2,107 units and another in **63
(204.1 km²)** — 2.9 per cent, against the 2.1 per cent it gets wrong on villages whose district is known. Those
63 are flagged in the table (`area_majority_agrees_with_assigned` = 0), not moved. The largest: `OUTSIDE_2100` (4,385 ha, assigned Ganjam, 73 per cent of it on Gajapati polygons); `OUTSIDE_1229` (2,417 ha, assigned Cuttack, 59 per cent of it on Nayagarh polygons); `OUTSIDE_780` (1,940 ha, assigned Baudh, 61 per cent of it on Anugul polygons); `OUTSIDE_2927` (1,297 ha, assigned Ganjam, 40 per cent of it on Gajapati polygons); `OUTSIDE_2383` (1,272 ha, assigned Ganjam, 64 per cent of it on Gajapati polygons).

**Ambiguous, by the definition asked for** — two districts within 5 points of each other by the unit's own area —
**3 of the 2,170 units where it can be measured:**

| unit | name | district assigned | the two largest shares of the unit's area | covered | area, ha |
|---|---|---|---|---|---|
| `OUTSIDE_627` | Gaisilet | Bargarh | Bargarh 0.29, Balangir 0.27 | 0.56 | 226.4 |
| `OUTSIDE_1034` | Harbhanga | Baudh | Baudh 0.46, Anugul 0.43 | 0.89 | 1,970.0 |
| `OUTSIDE_2686` | Lakshmipur | Koraput | Rayagada 0.52, Koraput 0.48 | 1.00 | 50.4 |

For the units where it cannot be measured the collar stands in: of the 1,183 that have coded neighbours and are less than
half covered, 0 have two districts within 5 points of each other round them. 139 units (310.3 km²) are neither
half covered nor next to a coded village: for them there is the name and nothing to check it against. The column
`ambiguous` is the one flag (`ambiguous_basis` says which measure it rests on).

**The neighbours.** 3,138 units have a coded village within 100 m; 354 do not. In 32 the named district is in the
collar by neither tally. The area majority could be taken for 16 of those: it sides with the neighbours in 13 — the
units overridden — and with the name in 3. The 19 that are not overridden keep their name and are flagged
(`label_absent_from_collar` = 1). The 13 overridden:

| the polygon names | assigned (both checks) | units | km² |
|---|---|---|---|
| Cuttack | Jajapur | 9 | 4.4 |
| Gajapati | Ganjam | 2 | 2.9 |
| Ganjam | Gajapati | 1 | 0.9 |
| Sonapur | Balangir | 1 | 0.3 |

How the collar's counts move with its width — the name compared with the neighbours' largest district at every width:

| collar | units with a coded neighbour | without | ambiguous, tally by name | by code | name differs from the neighbours' largest, tally by name | by code | named district absent from the collar |
|---|---|---|---|---|---|---|---|
| 50 m | 3,128 | 364 | 6 | 7 | 55 | 85 | 32 |
| 100 m (used) | 3,138 | 354 | 3 | 5 | 58 | 89 | 32 |
| 250 m | 3,166 | 326 | 6 | 10 | 61 | 92 | 32 |

What to hold against it:

- **For 79 per cent of this land the district is the polygon's name and no area check exists.** That is where the
  forest is. The name is right for 99.92 per cent of the villages it can be scored on; nothing says it is as good
  on the land outside them.
- **82 units (268.0 km²) are flagged and not moved**: one of the two checks contradicts the district they carry.
  Whoever needs a district for one of them should look at it.
- **The layer's own crosswalk has faults, which is why the collar is tallied by name.** 41 coded polygons carry a 2011
  district code that is not their 2001 name's, and where that happens the villages lie where their names say. The
  tally by code puts 32 units' neighbours in a different district from the tally by name. The faults are in
  `00_raw/`-derived data and are recorded here, not corrected.
- The five districts with the most such land: Kandhamal 3,595 km² in 152 units, Kalahandi 2,954 km² in 193 units, Ganjam 2,915 km² in 558 units, Koraput 2,914 km² in 253 units, Sundargarh 2,588 km² in 143 units.

**Use.** For descriptive tables and for the demo layer (`docs/LAYER.md`). `units.gpkg` is unchanged, and these units
stay out of any regression: they have no census rows whatever district they are in. One use beyond description was
added on 7 October and is for the project owner to accept or refuse: `02_build_agreement.py` resamples whole
districts to get honest intervals (`docs/DEGRADATION.md` §4b), and takes the district of an assessed outside-village
unit from this table. No estimate depends on it; the width of the intervals does.

## Withdrawn

Unit counts of 13,438 and 9,946 and areas of 154,046 and 112,609 km² appeared in an earlier brief. They were
never measured: the mapping file had not been downloaded when they were written. Do not reconcile to them.

The UTM-based areas listed above (155,161, 41,437, 113,724, 155,917 and 755 km²) are withdrawn too, and so is
the use of 155,707 km² as a check on the layer.
