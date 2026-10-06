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

## Withdrawn

Unit counts of 13,438 and 9,946 and areas of 154,046 and 112,609 km² appeared in an earlier brief. They were
never measured: the mapping file had not been downloaded when they were written. Do not reconcile to them.

The UTM-based areas listed above (155,161, 41,437, 113,724, 155,917 and 755 km²) are withdrawn too, and so is
the use of 155,707 km² as a check on the layer.
