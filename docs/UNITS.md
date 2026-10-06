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

*Added 7 October 2026. `scripts/01_assign_outside_district.py`, run 2026-10-06T19:19:40Z; every figure is from
`10_units/outside_village_district.csv`, its summary or its provenance record. n = 3,492 units, 41,358.3 km².*

The outside-village units have no Census-2011 code, so `pc11_district_code` is blank for them in `units.gpkg`. The
instruction was to assign a district "by spatial majority against the district boundaries already in 00_raw".
**There is no district boundary file in `00_raw/`.** The only district geometry among the inputs is the DataMeet
village layer itself. So the method is not the one asked for, and is this:

1. Each outside-village unit is one DataMeet polygon that carries no census code — one for one, 3,492 of them. The
   polygon does carry a **Census-2001 district name**.
2. A name becomes a Census-2011 district through the 49,039 coded polygons that carry a name: each of the
   30 names goes with one code and each code with one name, and at least 99.30 per cent of a name's coded polygons
   carry that code.
3. The name is **checked against the neighbours**: a 100 m collar is drawn round the unit and the part of it lying on
   coded villages is tallied by district — once by the villages' 2011 codes and once by their 2001 names.
4. The name is kept unless its district is absent from the collar in both tallies; then the unit takes the
   neighbours' largest district. A polygon with no name takes the neighbours' largest.

| a unit's district is | units | km² |
|---|---|---|
| the district its polygon names | 3,441 | 41,281.2 |
| its coded neighbours' district — the polygon names none | 19 | 4.8 |
| its coded neighbours' district — the one it names is nowhere round it | 32 | 72.3 |
| **all outside-village units** | **3,492** | **41,358.3** |

**Ambiguous** — the two largest districts in the collar within 0.05 of each other by area — **5 units**:

| unit | name | district assigned | the collar's two largest shares | area, ha |
|---|---|---|---|---|
| `OUTSIDE_1229` | Kanpur | Cuttack | Nayagarh 0.50, Cuttack 0.50 | 2,416.8 |
| `OUTSIDE_1287` | Barang | Cuttack | Khordha 0.52, Cuttack 0.48 | 11.2 |
| `OUTSIDE_2003` | Khalikote | Ganjam | Cuttack 0.52, Ganjam 0.48 | 47.5 |
| `OUTSIDE_3344` | Lakshmipur | Koraput | Rayagada 0.52, Koraput 0.48 | 829.0 |
| `OUTSIDE_3412` | Khalikote | Ganjam | Cuttack 0.52, Ganjam 0.48 | 25.8 |

2 of the 5 — `OUTSIDE_2003`, `OUTSIDE_3412` — are ambiguous only because of a fault in the layer (below): tallied by their neighbours' 2001 names instead of their 2011 codes, each has one district round it (Ganjam 1.00). 3 units lie on a district boundary in both tallies.

How that moves with the width of the collar:

| collar | units with a coded neighbour | without | ambiguous | name differs from the neighbours' largest |
|---|---|---|---|---|
| 50 m | 3,128 | 364 | 7 | 85 |
| 100 m (used) | 3,138 | 354 | 5 | 89 |
| 250 m | 3,166 | 326 | 10 | 60 |

What to hold against it:

- **354 units have no coded village within 100 m** — they are surrounded by other outside-village units — and
  rest on the polygon's name alone, unchecked.
- In 89 units the name is not the neighbours' largest district. In 57 of them the named district is present
  in the collar and the name is kept: a tract on a district boundary has neighbours on both sides. In the other
  32 it is nowhere round the unit and the neighbours' district is taken:

| the polygon names | assigned | units | km² |
|---|---|---|---|
| Cuttack | Jajapur | 12 | 10.1 |
| Cuttack | Khordha | 7 | 37.0 |
| Ganjam | Gajapati | 5 | 10.1 |
| Gajapati | Ganjam | 4 | 5.3 |
| Rayagada | Koraput | 2 | 0.7 |
| Cuttack | Kendrapara | 1 | 8.9 |
| Sonapur | Balangir | 1 | 0.3 |

- **The layer's own crosswalk has faults, which is why the neighbours are tallied two ways.** 41 coded polygons carry
  a 2011 district code that is not their 2001 name's — the largest group, 15 polygons named Ganjam with the code
  of Cuttack. A tally by code alone would have moved units into districts they are not in. The faults
  are in `00_raw/`-derived data and are recorded here, not corrected.
- The five districts with the most such land: Kandhamal 3,595 km² in 152 units, Kalahandi 2,954 km² in 193 units, Koraput 2,915 km² in 255 units, Ganjam 2,908 km² in 556 units, Sundargarh 2,588 km² in 143 units.

**Use.** For descriptive tables and for the demo layer (`docs/LAYER.md`). `units.gpkg` is unchanged, and these units
stay out of any regression: they have no census rows whatever district they are in.

## Withdrawn

Unit counts of 13,438 and 9,946 and areas of 154,046 and 112,609 km² appeared in an earlier brief. They were
never measured: the mapping file had not been downloaded when they were written. Do not reconcile to them.

The UTM-based areas listed above (155,161, 41,437, 113,724, 155,917 and 755 km²) are withdrawn too, and so is
the use of 155,707 km² as a check on the layer.
