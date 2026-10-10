# Stage 2 — social need per unit

*Built 5 October 2026 by `scripts/03_build_need.py`. Every figure is from `30_need/need.provenance.json` or the
tables beside it. Output: `30_need/need_by_unit.csv`, n = 11,468 units.*

## What it is keyed on, and what the join loses

The unit is an LGD panchayat id (`docs/UNITS.md`). The census and ADI files are keyed on Census-2011 village
codes and reach a unit through `LGD_village_panchayat_mapping.csv`. Nothing is matched by name.

| | |
|---|---|
| `lgd_panchayat` units with figures | 7,976 of 7,976 — the join loses no unit |
| `outside_village` units | 3,492, **blank in every column**: no census rows exist for land outside revenue villages |
| mapped Odisha villages found in the census file | 51,231 of 51,231 (15 of them census towns the mapping places under panchayats) |
| census villages the mapping does not contain | 95 villages, population 20,001 |
| LGD panchayat ids with no polygon, so in no unit | 176 ids, population 293,285 |
| inside units, but in villages that have no polygon | 2,144 villages, population 776,795 |

The units together hold a population of 34,766,888 and 8,043,218 households. A unit's figures cover
every village the mapping gives its id, whether or not that village is drawn in the unit's polygon. In 81 units
more than half the population lives in villages that are not drawn, so a per-hectare figure from stage 1
and a per-person figure from here do not describe quite the same ground.

## What each column is for

Rulings of 5 October 2026.

- **`st_share` is the marginalisation axis.**
- **`adi_2011` is the development regressor.** It is blank for 534 of the 7,976 units (6.7%). `adi_2019` is blank
  for 2,866 (36%) and would silently drop more than a third of the sample, so it is a reported column
  and not a regressor.
- **`poverty_rate`** is a second, independent reading of deprivation, from the SECC rather than the census.
  It is a model estimate and rural only (see below).
- **`forest_dependent_households` is a reported column and a robustness check, not the need measure.** The
  brief's three axes are degraded, marginalised and under-allocated. This composite folded forest into
  marginalisation, collapsing two of the axes and duplicating stage 1's job. Forest comes from stage 1.

## Reconciliation

The census file holds only village, town and ward rows — it prints no state or district totals. What it
does print was checked: for each of the 15 census towns used, the town row equals the sum of its ward rows.
Its Odisha rows sum to:

| | population | households | SC | ST |
|---|---|---|---|---|
| village rows (rural) | 34,970,562 | 8,089,987 | 6,218,642 | 8,994,967 |
| ward rows (urban) | 7,003,656 | 1,547,833 | 969,821 | 595,789 |
| state | 41,974,218 | 9,637,820 | 7,188,463 | 9,590,756 |

**Against the published Census 2011 totals:** population (total 41,974,218, rural 34,970,562, urban
7,003,656), SC (7,188,463) and ST (9,590,756) all agree exactly, and the script fails if they stop
agreeing. Two cautions. The published figures were read from a **secondary copy** —
<https://www.citypopulation.de/en/india/admin/21__odisha/>, which credits the Registrar General — because on
5 October 2026 the census site and two Government of Odisha pages could not be reached (a certificate
error, HTTP 503, an expired certificate). And **households is not reconciled**: no published total was found.

Two rows of the census file (village codes 384333, 392003) and three of the village ADI file
(384333, 392003, 382945) had to be repaired: an unquoted comma in the village name shifts every later field one
place to the right. In the ADI file the last field falls off the end of a shifted row. For village 382945
the 2011 ADI reads 3 at face value and is 7; its 2019 ADI is lost and is treated as missing, not rebuilt.

**The SECC module prints totals of its own**, one row per district. Weighting each shrid's rate by the census
population of its villages reproduces all 30 Odisha rows, for both poverty rates, to within 1e-16; the
script stops if any differs by more than 1e-09. The key that links shrids to villages agrees with the census on village
population in 100.00% of its 47,673 Odisha villages. What this check cannot show: the module has no
village rows, so a village takes its shrid's rate, and the district rows would come out the same either way.

## Why the counts are not taken from `panchayat_census_adi_data.csv`

The brief names that file as the input. It is keyed on the same id and joins to every unit, but its contents
do not reconcile to the census rows it was built from, so it is used as a cross-check only.

- **It double counts.** In 83 of 8,152 Odisha ids it holds more than the id's villages do: +192,336 people and
  +44,146 households in all. The 15 census towns are counted twice, and so is every village that has more than
  one row in the village ADI file. It never holds less, and agrees exactly in the other 8,069.
- **Its ADI is diluted.** Its numerator, Σ(ADI × population), matches ours in all 8,069 ids that agree on
  population — but it divides by the population of *all* the id's villages, including those with no ADI,
  which are thereby averaged in as zeros. That understates ADI in 4,593 populated ids for 2011 and 3,360 for
  2019, and leaves it at zero in 458 and 2,820 that have people but no village ADI at all.

`30_need/need_source_check.csv` sets the two side by side for every id. The script fails if the panchayat
file ever holds *fewer* people than these sums, or if the ADI numerators stop matching.

## Columns, with n and missingness

Among the 7,976 `lgd_panchayat` units (the 3,492 `outside_village` units are blank throughout):

| column | n | blank | what it is |
|---|---|---|---|
| `n_villages` | 7,976 | 0 | villages (and census towns) the mapping gives this id |
| `n_villages_uninhabited` | 7,976 | 0 | of those, with no population |
| `n_villages_without_polygon` | 7,976 | 0 | of those, with no polygon in the DataMeet layer |
| `population` | 7,976 | 0 | Census 2011, summed over the id's villages |
| `population_in_villages_without_polygon` | 7,976 | 0 | the part of `population` that lies outside the unit's drawn area |
| `households` | 7,976 | 0 | Census 2011 (`No_HH`) |
| `st_pop` | 7,976 | 0 | Census 2011 Scheduled Tribe population |
| `st_share` | 7,853 | 123 | `st_pop / population`; blank where population is 0 |
| `sc_pop` | 7,976 | 0 | Census 2011 Scheduled Caste population |
| `sc_share` | 7,853 | 123 | `sc_pop / population`; blank where population is 0 |
| `adi_2011` | 7,442 | 534 | population-weighted mean village ADI over villages that have one; blank where none has |
| `adi_2011_population_covered_share` | 7,853 | 123 | share of the id's population in villages with a 2011 ADI |
| `adi_2019` | 5,110 | 2,866 | the same for the 2019 prediction |
| `adi_2019_population_covered_share` | 7,853 | 123 | share of the id's population in villages with a 2019 ADI |
| `poverty_rate` | 7,812 | 164 | SECC small-area poverty rate at the Tendulkar rural line, population-weighted over villages that have one; a model estimate |
| `poverty_rate_ppp2` | 7,812 | 164 | the same at the module's higher line ($2 a day PPP) |
| `poverty_rate_population_covered_share` | 7,853 | 123 | share of the id's population in villages with a rate |
| `poverty_rate_population_rated` | 7,976 | 0 | the people in those villages: how much the rate rests on |
| `poverty_rate_shared_shrid_population_share` | 7,812 | 164 | of those people, the share whose shrid also holds villages of another id |
| `forest_dependent_households` | 7,976 | 0 | the construct below |
| `n_forest_villages` | 7,976 | 0 | villages of the id that qualify for the construct |
| `households_in_forest_villages` | 7,976 | 0 | all households in those villages, ST or not |

ADI is the sum of five indicators each ranked 1–3, so it runs 5–15; the 2019 figure is a satellite-based
prediction, not a census measure. Read `adi_*` with its coverage column. In 842 units the 2011 figure rests
on villages holding less than half the unit's people, and in 678 the 2019 figure does.

## `poverty_rate` is an estimate, not a count

It is SHRUG 2.2's SECC rural consumption module: household consumption from the 2011-12 India Human
Development Survey imputed onto the asset and earnings lists of every SECC household, and the share of people
falling below a poverty line (Asher, Lunt, Matsuura and Novosad 2021). Carry these with it:

- **Which line, read from the data.** `poverty_rate` uses the Tendulkar rural line and `poverty_rate_ppp2` the
  module's higher line, $2 a day at purchasing-power parity. SHRUG's documentation gives them as Rs 27 and Rs 31
  a day. The script does not take that on trust or from the column names: where a shrid's rate is 1 its mean
  consumption per head is below the line, and where it is 0, at or above it. Across the country's shrid rows
  that puts the first line above Rs 27.18 and at most Rs 27.22 a day (736 shrids all poor, 34,559 none poor) and the
  second above Rs 30.99 and at most Rs 31.07 (1,138 and 21,998). The run stops unless both round to the documented
  figures. The rates are shares of people, not of households. (The replication reported that the variable table on
  SHRUG's site gave Rs 33 and "households" for the Tendulkar column when it fetched it; the data contradict both,
  and that page was not re-read here.) Weighted by population over the mapped villages
  that have a rate, they are 35.3% and 44.9%.
- **Coverage.** 45,890 of the 51,231 mapped villages have a rate, holding 96.9% of the mapped population.
  164 units are blank: 123 have no population at all and 41 have people but no rated village. It is rural: the census
  towns the mapping places under panchayats have none.
- **The rate belongs to a shrid, not a village.** A shrid is SHRUG's own location unit, usually one village and
  sometimes several merged: 165 of the 45,767 rated Odisha shrids hold more than one. 63 of them span more than one LGD
  panchayat id, so 73 units take part of their rate from a shrid they share with another id and 8 take all of it.
  `poverty_rate_shared_shrid_population_share` marks them.
- **Thin evidence.** 101 units' rates rest on fewer than 100 people and 35 are exactly 0 or 1.
  `poverty_rate_population_rated` gives the count; weight or filter on it.
- **The module's own flags are not used.** Its shrid rows carry two undocumented columns, `_mean_p_miss` and
  `_core_p_miss`. They are above zero for 8 rated Odisha shrids, touching 11 units. The rates are used as given.
- **Terms.** SHRUG is CC BY-NC-SA 4.0, and its README adds that "any data that you link to the SHRUG must be
  posted with SHRUG identifiers at the time that your paper or project is published". Non-commercial and
  share-alike both bind anything released with these columns in it: `docs/DATA_NOTES.md`, "Publication
  constraints", has the rule (check every released dataset or public demo against the terms first) and the
  fallback (keep the SHRUG-derived columns out of the released file and cite them only in the paper).

The module was fetched on 5 October 2026 from the SHRUG download page, which needs no login and no form. No
proxy was substituted for it and none should be.

## `forest_dependent_households` is a construct, not a measurement

**It is no longer the need measure** (above). It is kept because it is cheap to report and useful as a
robustness check on results that rest on `st_share`.

**In words:** the estimated number of Scheduled Tribe households living in villages that have forest inside
their revenue boundary.

**The threshold, and why.** A village qualifies when ATREE's CFR-potential list gives it the class "Forest
within village" or "Both". That is ATREE's line, not one chosen here: in ATREE's file those two classes begin
at 9.90 ha of forest inside the revenue boundary and the third class, "Forest adjacent to village", ends at
9.88 ha. So the rule amounts to "about 10 ha of forest or more inside the boundary". It was adopted because the
alternative was to invent a cut-off, and the source's own classification is the one line in this data that
someone else has already defended. The script stops if the classes ever cease to split this way.

**How ST households are estimated.** The census does not count households by tribe at village level. Each
qualifying village contributes `households × ST population / population`, which assumes ST households are the
same size as others in the same village.

**What the choice of line does.** Statewide, over villages that reach an LGD panchayat id. The last column is
the Spearman rank correlation, across the 7,976 units, between the construct and what the other rule would give.

| rule | villages | households | ST households (est.) | LGD panchayat ids with any | rank agreement with the construct |
|---|---|---|---|---|---|
| on ATREE's list at all | 25,761 | 3,921,927 | 1,585,672 | 5,507 | 0.93 |
| forest inside the boundary > 0 ha | 23,910 | 3,683,664 | 1,495,724 | 5,313 | 0.96 |
| ATREE class 'Forest within village' or 'Both' **← the construct** | 19,334 | 3,219,021 | 1,308,898 | 5,008 | 1.00 |
| forest inside the boundary >= 25 ha | 13,062 | 2,274,689 | 993,507 | 3,974 | 0.90 |
| forest inside the boundary >= 50 ha | 8,508 | 1,571,367 | 722,624 | 3,036 | 0.78 |
| forest inside the boundary >= 100 ha | 4,647 | 955,447 | 466,155 | 2,076 | 0.64 |
| forest >= 10% of the village's geographical area | 14,744 | 1,846,641 | 858,815 | 3,866 | 0.82 |
| forest >= 25% of the village's geographical area | 9,066 | 958,282 | 483,816 | 2,722 | 0.66 |
| forest >= 50% of the village's geographical area | 4,071 | 339,322 | 184,985 | 1,520 | 0.46 |
| every village of the id, on ATREE's list or not (ST households, forest or no forest) | 51,231 | 8,110,977 | 2,081,476 | 8,152 | 0.81 |

Three things follow, and they should travel with the column:

- **The ranking is fairly robust to a lower line and not to a higher one.** Counting any forest at all gives
  nearly the same ordering of units (0.96); 25 ha still agrees well (0.90); by 100 ha it is a different variable
  (0.64).
- **It is not much more than ST presence.** It ranks units 0.81 alike with ST households counted regardless of
  forest, and holds 63% of them (1,308,898 of 2,081,476). Do not enter it beside `st_pop` or
  `st_share` as if it carried separate information.
- **Zero does not mean no tribal population.** 3,619 of the 7,976 units score zero, and 2,459 of those have
  Scheduled Tribe residents.

**What it leaves out, and what it is not.**

- A village not on ATREE's list contributes nothing.
- 676 of ATREE's 26,489 rows carry no Census-2011 village code (621 labelled 'Unknown', 54 labelled 'Forest with Settlement', 1 with no label). They cannot be placed
  in a unit without matching names, which this pipeline does not do. ATREE itself gives them no usable
  figures: 0 are in the qualifying classes, 1 has a forest area and 1 a household count. So forest
  settlements, which have no census row, are not in the construct at all — a gap in the sources.
- 1,072 qualifying villages are uninhabited and add nothing.
- 150 qualifying villages (8,992 estimated ST households) sit in ids that have no polygon and so in no unit; the
  units' total is that much below the statewide figure in the table.
- Household and population counts are the census's, by village code. ATREE's own household column is the same
  figure wherever it gives one (24,305 of 24,305) and blank otherwise.
- The area-share rows use ATREE's "Total Geographical Area". Its "Calculated GIS Area" is not usable for this:
  forest exceeds it in 377 villages. 73 villages have no geographical area and fall out of those three rows.
- It says where ST households live beside forest. It does not measure use of, income from, or rights over forest.

**The ATREE list is registered.** It is `00_raw/01_cfr_fra/OD_CFR_Potential_Villages_22_April_2025.xlsx` (2,452,749 bytes,
sha256 `40a30b6999af576b…`), with a row in `00_raw/data_manifest.csv`. On 5 October 2026 the copy the project owner
held was confirmed byte-identical to a fresh download from the Drive id the manifest already listed, and
copied in. The column is no longer provisional.

## Verification applied

Full independent replication, 5 October 2026. A separate agent, allowed to read only the script's docstring,
rebuilt every column from the raw files with its own code and compared cell by cell.

- **All 18 value columns agreed in all 7,976 units** — no cell differing beyond the rounding the file is written
  to — as did all 8,152 rows of the source-check table and every claim above about the census file, the
  panchayat file and the ATREE list.
- **It found three defects, all since fixed.** The shifted ADI row for village 382945, which the first version
  read at face value. The area-share rows of the sensitivity table, which divided by "Calculated GIS Area".
  And a sentence claiming the uncoded ATREE rows hid forest-dependent settlements from the construct, when
  ATREE gives those rows nothing to count. After the fixes the only cells that changed were that one unit's
  ADI and the three area-share rows, each to the figure the replication had derived on its own.
- **The rank-agreement column was added afterwards** and reproduces the replication's own correlations to four
  decimals.
- **Not replicated:** the reading of the published census totals, which rests on one fetch of a secondary page.
  The replication was cut off before it wrote its report, so its conclusions were taken from the recorded
  output of its checks rather than from a summary in its own words.
- **The poverty columns came later** and were not part of that replication. They had their own full independent replication the same day, by a separate agent that read only the docstring. All 23,928 cells of the three poverty columns in the 7,976 panchayat units agreed, the 3,492 outside-village units are blank, and each claim about the module held: the district rows, the agreement of the key with the census, the ordering of the two rates, the coverage. It also found that the script identified the two poverty lines only by column name and ordering, that the district check was looser than the data allowed, that nothing recorded how few people some rates rest on or where a shrid spans two ids, and that this document still said the column was blank. All four are fixed: the lines are now bracketed from the data and gated, the tolerance is 1e-9, two columns carry the evidence, and this document is regenerated. The counts in the section on poverty are the script's own and equal the replication's. After those changes every earlier cell of need_by_unit.csv is unchanged and the other two tables are byte-identical.
- **Registering the ATREE list changed nothing:** every earlier column, the source-check table and the
  sensitivity table are identical cell for cell to the run that read the unregistered copy.
