# Working rules for this repository

Read `README.md` first — it is the full brief. These are the standing rules.

## Non-negotiable

- **Never invent a number.** If it is not in `00_raw/`, leave it blank and say so in the output.
  This applies above all to the VGPP plantation unit cost (₹/ha) and district HQ coordinates.
- `00_raw/` is immutable. Never edit or overwrite anything in it.
- Every script writes into exactly one numbered folder (`10_units/`, `20_degradation/`, …) and records
  its input filenames and a UTC run timestamp in the output.
- Where a source prints its own totals, check against them and fail loudly on mismatch.
  `parse_mis_html_reports.py` and `00_raw/cfr_fra/_build_mota.py` show the pattern.
- State `n` and missingness on every table you produce.

## Before building a stage

Re-read the matching section of `README.md` §4 and the gotchas in §5. Most of the ways this analysis
can go quietly wrong are listed there, with measured numbers.

## Environment

Expected: `pandas`, `numpy`, `geopandas`, `pyogrio`, `shapely`, `scipy`, `scikit-learn`.
`statsmodels` is **not** assumed — either add it deliberately or write OLS with robust standard errors
in numpy. Prefer the standard library for parsers.

## Data not in this repository

The 1.99 GB of district asset GeoJSONs are fetched by `scripts/collect_data.py` into `00_raw/` and are
gitignored. Do not commit them. Do not commit the Drive CSVs either.

## Build order

Stage 3 before stages 1 and 2. `README.md` §7 explains why: stage 3 can invalidate the project's premise
cheaply, and it is the stage whose data is already verified.
