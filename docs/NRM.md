# Why there is no NRM column per unit

*Ruling of 5 October 2026. Figures are R6.20's printed state totals, as written to
`40_allocation/state_fy_r620_vs_dump.csv` by `scripts/04_compare_dump_to_r620.py`.*

## The rule

**NRM expenditure comes from R6.20, at district level, and from nowhere else. It is never constructed per
unit.** `allocation_by_unit.csv` has no `expenditure_nrm` column and none is to be added.

## The reasoning

The asset dump carries no NRM marker. The only thing its work categories allow is water plus plantation, and
it is tempting to call that NRM. It is not, for two reasons, and the second is the one that matters.

1. **It is an undercount.** NRM also contains land development, drought proofing and flood control, and
   water plus plantation leaves all of that out. (That list is the project owner's, from the ruling of
   5 October 2026. Nothing in `00_raw/` itemises the remainder: R6.20 shows only that it exists and how
   large it is — the last column of the table below.)

2. **The size of the undercount is not stable.** In R6.20, water plus plantation as a share of NRM runs from
   90.1 % (2014-15) down to 51.8 % (2019-20) — a swing of 38 points — because plantation collapsed after
   FY2017-18 while the rest of NRM did not. A per-unit "NRM" built as water plus plantation would therefore
   capture nine-tenths of NRM in the early years and about half in the middle ones. Any series, share or
   regressor built on it would carry a time trend that comes from the proxy and not from the spending.

| FY | NRM, % of all expenditure | Water, % of all | Plantation, % of all | (Water + Plantation) / NRM, % | NRM that is neither, % | R6.20 table as of |
|---|---|---|---|---|---|---|
| 2014-15 | 42.8 | 17.2 | 21.39 | **90.1** | 9.9 | 10/10/2020 |
| 2015-16 | 38.2 | 15.2 | 17.55 | **85.7** | 14.3 | 10/10/2020 |
| 2016-17 | 53.6 | 23.9 | 24.17 | **89.7** | 10.3 | 10/10/2020 |
| 2017-18 | 40.6 | 16.8 | 18.62 | **87.2** | 12.8 | 10/10/2020 |
| 2018-19 | 42.2 | 21.3 | 3.34 | **58.4** | 41.6 | 27/12/2024 |
| 2019-20 | 37.2 | 18.9 | 0.33 | **51.8** | 48.2 | 27/12/2025 |
| 2020-21 | 61.0 | 34.2 | 0.03 | **56.1** | 43.9 | 03/10/2026 |
| 2021-22 | 68.6 | 39.8 | 0.01 | **58.0** | 42.0 | 03/10/2026 |
| 2022-23 | 76.7 | 46.6 | 0.02 | **60.8** | 39.2 | 03/10/2026 |
| 2023-24 | 66.0 | 40.9 | 0.03 | **62.0** | 38.0 | 03/10/2026 |
| 2024-25 | 67.6 | 43.1 | 0.63 | **64.6** | 35.4 | 03/10/2026 |
| 2025-26 | 64.8 | 50.4 | 0.54 | **78.6** | 21.4 | 04/10/2026 |
| 2026-27 (part-year) | 59.8 | 51.4 | 0.13 | **86.1** | 13.9 | 04/10/2026 |

n = 13 financial years, all 314 blocks, from the report's own printed Total rows.

## What this corrects

An earlier note in this project said that water plus plantation was "the sum README §5.6 warns against".
That was the wrong objection. §5.6 warns against adding NRM to Water or Plantation, which counts the same
money twice because Water and Plantation are inside NRM. Water plus plantation is the opposite error: it
counts too little. The column is dropped for being an unstable undercount, not for double counting.

## What may still be done

- Water as a share of NRM, from R6.20 — the monotonic series in README §2 — is sound: both terms are R6.20's.
- (Water + Plantation) / NRM is computed once, in `04_compare_dump_to_r620.py`, to produce the table above.
  It is a diagnostic of the remainder, not an NRM estimate.
- In the dump, `expenditure_water` and `expenditure_plantation_category` remain as separate, overlapping
  flags. `expenditure_water` is a construct from three CoRE Stack work categories and is itself noisy
  (see the docstring of `04_build_allocation.py`). Neither it, nor its sum with plantation, is NRM.
