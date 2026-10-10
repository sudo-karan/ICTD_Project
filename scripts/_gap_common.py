"""Not a step and writes nothing of its own: what the stage-4 builders (`scripts/08_*.py`) share.

Stage 4 is the comparison of forest condition, need and allocation, as the project owner ruled it on 10 October 2026
(`docs/GAP.md`). Everything here reads tables already on disk. Nothing calls Earth Engine or the network.

Stage 4 runs in an environment of its own, outside the repository (`README.md` section 0), which holds exactly what
`requirements-stage4.txt` pins. The repository's main environment is not touched by it: the bootstrap package needs
`numba`, which needs an older `numpy` than the earlier stages were built with. Every builder calls
`require_stage4_environment()` first and stops if it is run anywhere else.

What is in this module, and the conventions every builder keeps:

* **Paths** of every input, in one place (`IN`), and the output folder `50_gap/`. `IN` holds every file that any step
  of the stage reads and that is not the stage's own output: `record_step` stops a step that records an input from
  anywhere else, so the listing of inputs that step 0 writes from `IN` cannot leave one out.
* **Exact sums.** Hectares in the stage tables carry four decimals and money in R6.20 two. They are added as
  `decimal.Decimal`, so a district sum is exact and equals the same sum made in any other order. Floats are used only
  where a statistic needs them (ranks, regressions), and are made from the exact sums.
* **Financial years.** R6.20 writes a financial year as `2014-2015`. `PRE` is FY2014-15 to FY2017-18, the four tables that
  carry the stamp 10/10/2020 (a snapshot frozen in 2020). `POST` is FY2018-19 to FY2025-26. `PART` is FY2026-27, a part
  year: it is reported alone and enters no sum, no share and no model. The geotagged record ("the dump") writes a
  financial year as `2017-18`; `fy_work_start` is the text `NA` where a work has no usable start date, and such a work
  counts as NOT started by FY2017-18 (the rule `docs/DECISION_LAYER.md` used for its 92.9 per cent). A money cell of
  the dump's tables is blank where the cell holds works and none of them reports expenditure: it adds nothing to a sum.
* **Windows** of calendar years are those of the decision table, ends included; `2018_2025` is the default.
* **Cells.** The three "loss recorded" cells are `open_loss`, `dense_loss`, `little_loss`; the assisted-natural-
  regeneration cell is `open_none`. Their full names are read from `55_decision/tiers.csv`, never typed.
* **The provenance record**, `50_gap/gap.provenance.json`: one section per builder, each with every input's SHA-256,
  the seeds, the package versions and the run time in UTC, and under `environment` every package the interpreter
  holds with its version, the SHA-256 of `requirements-stage4.txt` and whether the two agree. A builder rewrites its
  own section and no other.
* **Rank statistics** for 30 districts (`spearman_with_inference`): Spearman's rho with average ranks for ties, a
  two-sided permutation p and a percentile bootstrap interval over districts, with the seeds given by the caller.
* **Regressions** (`fit_cluster_model`): OLS on complete cases with dummies written out, CR1 standard errors by
  district for reference, and the interval that counts: a restricted wild cluster bootstrap (the `wildboottest`
  package, Webb weights, the null imposed), inverted by refitting with `y - b0 * x` (`wcb_interval`). The bracket is
  doubled as a whole, both ends together, until p is below 0.05 at both ends: the owner's sentence, to the letter.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "50_gap"
PROVENANCE = OUT / "gap.provenance.json"

IN = {
    "r620_district": ROOT / "00_raw/mis_reports/odisha_r620_district_fy_category_2014-2027.csv",
    "r620_state": ROOT / "00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv",
    "fra_district": ROOT / "00_raw/cfr_fra/odisha_fra_mpr_district_2025-12-31.csv",
    "fra_mota": ROOT / "00_raw/cfr_fra/mota_fra_state_wise_2025-12-31.csv",
    "manifest": ROOT / "00_raw/data_manifest.csv",
    "units_gpkg": ROOT / "10_units/units.gpkg",
    "outside_district": ROOT / "10_units/outside_village_district.csv",
    "hansen_bands": ROOT / "20_degradation/hansen_loss_by_canopy_band_by_unit.csv",
    "agreement_by_unit": ROOT / "20_degradation/agreement_by_unit.csv",
    "corestack_by_unit": ROOT / "20_degradation/corestack_by_unit.csv",
    "need_by_unit": ROOT / "30_need/need_by_unit.csv",
    "allocation_by_unit": ROOT / "40_allocation/allocation_by_unit.csv",
    "allocation_by_unit_fy": ROOT / "40_allocation/allocation_by_unit_fy.csv",
    "allocation_unassigned": ROOT / "40_allocation/allocation_unassigned.csv",
    "assets_district_fy": ROOT / "40_allocation/assets_district_fy.csv",
    "condition_by_unit": ROOT / "55_decision/condition_by_unit.csv",
    "tiers": ROOT / "55_decision/tiers.csv",
    "data_notes": ROOT / "docs/DATA_NOTES.md",
    "need_md": ROOT / "docs/NEED.md",
    "adi_schema_docx": ROOT / "00_raw/docs/Village_level_dataset_schema_31Oct2022.docx",
    "layer_builder": ROOT / "scripts/06_build_layer.py",
    # read by one step each, and until 11 October 2026 named only in that step (so the listing of inputs left them out)
    "layer_by_unit": ROOT / "60_layer/layer_by_unit.csv",                   # districts: the class of Scheduled Tribe share the layer shows for a unit
    "layer_data_js": ROOT / "60_layer/data.js",                             # districts: the layer's own row of sources for the development index
    "forest_villages_pdf": ROOT / "00_raw/01_cfr_fra/List_of_Forest_Villages_Old_Habitation.pdf",   # rights
    "isfr_vol2_odisha": ROOT / "00_raw/05_forest_reference/isfr2023_vol2_odisha_pdf_pages_260-265.txt",   # Phase 5b: the Forest Survey's district table
    "requirements": ROOT / "requirements-stage4.txt",                       # the environment
    "provenance_hansen": ROOT / "20_degradation/hansen.provenance.json",    # the environment: the numpy each earlier stage was built with
    "provenance_corestack": ROOT / "20_degradation/corestack.provenance.json",
    "provenance_agreement": ROOT / "20_degradation/agreement.provenance.json",
    "provenance_forest_floor": ROOT / "20_degradation/forest_floor.provenance.json",
    "provenance_need": ROOT / "30_need/need.provenance.json",
    "provenance_allocation": ROOT / "40_allocation/allocation.provenance.json",
    "provenance_r620_vs_dump": ROOT / "40_allocation/r620_vs_dump.provenance.json",
    "provenance_decision": ROOT / "55_decision/decision.provenance.json",
}

REQUIREMENTS = IN["requirements"]                              # what the stage-4 environment holds, pinned

FY_ALL = [f"{y}-{y + 1}" for y in range(2014, 2027)]          # as R6.20 writes them
PRE = FY_ALL[:4]                                               # FY2014-15 .. FY2017-18: stamp 10/10/2020
POST = FY_ALL[4:12]                                            # FY2018-19 .. FY2025-26
PART = FY_ALL[12]                                              # FY2026-27, a part year
POST_WITHOUT_FIRST = POST[1:]                                  # FY2019-20 .. FY2025-26 (comparison C11)
MODEL_FYS = FY_ALL[:12]                                        # the 12 full years of the panel models
FROZEN_STAMP = "10/10/2020"
CATEGORIES = ("NRM", "Water", "Plantation")

WINDOWS = {"2018_2025": (2018, 2025), "2001_2025": (2001, 2025), "2017_2023": (2017, 2023), "2021_2025": (2021, 2025)}
DEFAULT_WINDOW = "2018_2025"
LOSS_CELLS = ("open_loss", "dense_loss", "little_loss")
ANR_CELL = "open_none"
YEARS = list(range(2001, 2026))
DUMP_LAST_FY = "2017-18"                                       # "works started in or before FY2017-18"

# The six districts R6.20 spells differently from the census (the owner's list, 10 October 2026). No other needs a rule.
R620_SPELLING_RULE = {"ANGUL": "384", "BOLANGIR": "393", "BOUDH": "391", "DEOGARH": "373", "JAJPUR": "382",
                      "SONEPUR": "392"}

LAKH = Decimal(100000)


class GateFailure(SystemExit):
    """A gate did not hold. The message says what was expected and what was found."""


def stop(message: str) -> None:
    raise GateFailure("\nSTOPPED: " + message + "\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def D(x) -> Decimal:
    """A cell of a stage table as an exact number. A blank cell is an error here: callers test for blanks first."""
    s = str(x).strip()
    if s == "":
        raise ValueError("blank cell where a number was required")
    return Decimal(s)


def dsum(values) -> Decimal:
    total = Decimal(0)
    for v in values:
        total += v
    return total


def read_rows(path: Path) -> list[dict]:
    """Every cell as text, blanks as empty strings: nothing is parsed or filled on the way in."""
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_header(path: Path) -> list[str]:
    with open(path, encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def write_rows(path: Path, rows: list[dict], columns: list[str]) -> None:
    """One CSV, columns in the order given. A cell that is None is written blank; a Decimal as its own digits."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(columns)
        for r in rows:
            missing = [c for c in columns if c not in r]
            if missing:
                stop(f"{rel(path)}: a row lacks the columns {missing}")
            w.writerow(["" if r[c] is None else fmt(r[c]) for c in columns])


def fmt(v) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, Decimal):
        return format(v, "f")
    if isinstance(v, (float, np.floating)):
        if math.isnan(v):
            return ""
        return repr(float(v))
    return str(v)


def fy_short(fy_r620: str) -> str:
    """`2014-2015` (R6.20) -> `2014-15` (the dump, and the way a financial year is printed)."""
    a, b = fy_r620.split("-")
    return f"{a}-{b[2:]}"


def fy_start_year(fy_r620: str) -> int:
    return int(fy_r620.split("-")[0])


DUMP_NO_START = "NA"                                           # how the dump's tables write a missing start year


def dump_fy_started_by(fy: str, last: str = DUMP_LAST_FY) -> bool:
    """True when a dump financial year (`2017-18`) is in or before `last`. A missing start year (`NA`) is False."""
    fy = fy.strip()
    if fy == DUMP_NO_START:
        return False
    a, b = fy.split("-")
    if len(a) != 4 or len(b) != 2 or int(b) != (int(a) + 1) % 100:
        stop(f"a financial year of the dump is not written as expected: {fy!r}")
    return int(a) <= int(last.split("-")[0])


def money(cell: str) -> Decimal:
    """A money cell of the dump's tables in rupees; a blank cell (works, none with expenditure reported) adds 0."""
    cell = cell.strip()
    return Decimal(cell) if cell else Decimal(0)


def package_versions(names=("python", "numpy", "pandas", "scipy", "statsmodels", "numba", "llvmlite", "tabulate",
                            "wildboottest", "pyogrio", "geopandas", "shapely", "matplotlib")) -> dict:
    import importlib.metadata as md
    out = {}
    for n in names:
        if n == "python":
            out[n] = sys.version.split()[0]
            continue
        try:
            out[n] = md.version(n)
        except md.PackageNotFoundError:
            out[n] = "not installed"
    return out


def _canonical(name: str) -> str:
    return name.strip().lower().replace("_", "-").replace(".", "-")


def requirement_pins(path: Path | None = None) -> dict:
    """`requirements-stage4.txt` as {package: version}: its lines of the form `name==version`, comments apart."""
    pins = {}
    for line in (path or REQUIREMENTS).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name, eq, version = line.partition("==")
        if not eq or not version:
            stop(f"{rel(path or REQUIREMENTS)}: a line is not `name==version`: {line!r}")
        pins[_canonical(name)] = version.strip()
    return pins


def environment() -> dict:
    """What the interpreter running this holds, set against `requirements-stage4.txt`.

    Every installed distribution but `pip` itself is listed with its version (`pip freeze` leaves pip out too). The
    environment "holds exactly what the file pins" when the two lists are the same: no package more, none fewer, no
    version different.
    """
    import importlib.metadata as md
    held = {}
    for d in md.distributions():
        name = _canonical(d.metadata["Name"])
        if name != "pip":
            held[name] = d.version
    pins = requirement_pins()
    differ = sorted(n for n in set(pins) | set(held) if pins.get(n) != held.get(n))
    return {"python": sys.version.split()[0], "requirements_file": rel(REQUIREMENTS), "requirements_sha256": sha256(REQUIREMENTS),
            "packages": dict(sorted(held.items())), "packages_pinned": len(pins),
            "differences": [f"{n}: pinned {pins.get(n, 'not pinned')}, held {held.get(n, 'not installed')}" for n in differ],
            "holds_exactly_what_the_file_pins": not differ}


def require_stage4_environment() -> dict:
    """Stop unless this interpreter holds exactly what `requirements-stage4.txt` pins. Returns `environment()`."""
    if not REQUIREMENTS.exists():
        stop(f"{rel(REQUIREMENTS)} is missing: stage 4 runs in the environment that file pins (README.md section 0)")
    env = environment()
    if not env["holds_exactly_what_the_file_pins"]:
        stop("this is not the stage-4 environment: it does not hold exactly what requirements-stage4.txt pins "
             "(README.md section 0 says how to make it). " + "; ".join(env["differences"][:8])
             + (f"; and {len(env['differences']) - 8} more" if len(env["differences"]) > 8 else ""))
    return env


def record_step(step: str, script: Path, inputs: dict, outputs: list[Path], extra: dict | None = None) -> None:
    """Write this builder's section of `50_gap/gap.provenance.json`, leaving every other section as it is."""
    env = require_stage4_environment()
    listed = {p.resolve() for p in IN.values()}
    stray = [rel(p) for p in inputs.values() if p.resolve() not in listed and not p.resolve().is_relative_to(OUT.resolve())]
    if stray:
        stop(f"the step {step} records an input that is neither the stage's own output nor in the list of inputs (IN), so the "
             "listing of inputs would leave it out: " + ", ".join(stray))
    OUT.mkdir(parents=True, exist_ok=True)
    record = {}
    if PROVENANCE.exists():
        record = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    record.setdefault("what", "Stage 4: forest condition, need and allocation compared. One section per builder; "
                              "each lists every input with its SHA-256, the seeds, the package versions and the "
                              "run time in UTC.")
    record.setdefault("steps", {})
    section = {
        "script": rel(script),
        "script_sha256": sha256(script),
        "shared_module": rel(Path(__file__)),
        "shared_module_sha256": sha256(Path(__file__)),
        "run_utc": utc_now(),
        "inputs": {k: {"path": rel(p), "bytes": p.stat().st_size, "sha256": sha256(p)} for k, p in inputs.items()},
        "outputs": {rel(p): {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in outputs},
        "package_versions": package_versions(),
        "environment": env,
    }
    if extra:
        section.update(extra)
    record["steps"][step] = section
    PROVENANCE.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------------------------------
# Rank statistics over districts
# ---------------------------------------------------------------------------------------------------------------------

def _rank(a: np.ndarray) -> np.ndarray:
    from scipy.stats import rankdata
    return rankdata(a, method="average")


def spearman(x, y) -> float:
    """Spearman's rho: the Pearson correlation of average ranks. NaN when either side is constant."""
    rx, ry = _rank(np.asarray(x, float)), _rank(np.asarray(y, float))
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return float("nan")
    return float(((rx - rx.mean()) * (ry - ry.mean())).mean() / (sx * sy))


def spearman_with_inference(x, y, seed_permutation: int, seed_bootstrap: int, n_permutations: int = 99999,
                            n_bootstrap: int = 9999) -> dict:
    """Rho over the districts given, with a two-sided permutation p and a percentile bootstrap 95 % interval.

    Permutation: `y` is shuffled against `x` `n_permutations` times; p = (1 + the number of shuffles whose |rho| is at
    least the observed |rho|) / (1 + n_permutations). Bootstrap: districts are drawn with replacement, as pairs,
    `n_bootstrap` times; the interval is the 2.5th and 97.5th percentiles of the rho of the draws in which rho is
    defined (the number in which it is not is returned). Both use `numpy.random.default_rng(seed)`.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    rho = spearman(x, y)
    rx, ry = _rank(x), _rank(y)
    rxc = rx - rx.mean()
    denom = math.sqrt((rxc ** 2).sum() * ((ry - ry.mean()) ** 2).sum())
    rng = np.random.default_rng(seed_permutation)
    at_least = 0
    for _ in range(n_permutations):
        p = rng.permutation(n)
        r = float((rxc * (ry[p] - ry.mean())).sum() / denom)
        if abs(r) >= abs(rho) - 1e-12:
            at_least += 1
    p_perm = (1 + at_least) / (1 + n_permutations)
    rng = np.random.default_rng(seed_bootstrap)
    draws, undefined = [], 0
    for _ in range(n_bootstrap):
        i = rng.integers(0, n, n)
        r = spearman(x[i], y[i])
        if math.isnan(r):
            undefined += 1
        else:
            draws.append(r)
    lo, hi = (float(v) for v in np.percentile(draws, [2.5, 97.5]))
    return {"n": n, "rho": rho, "p_permutation": p_perm, "ci95_lo": lo, "ci95_hi": hi,
            "n_permutations": n_permutations, "n_bootstrap": n_bootstrap, "n_bootstrap_undefined": undefined,
            "seed_permutation": seed_permutation, "seed_bootstrap": seed_bootstrap}


# ---------------------------------------------------------------------------------------------------------------------
# Regressions with district clusters
# ---------------------------------------------------------------------------------------------------------------------

def dummies(labels, prefix: str, drop: list | None = None) -> tuple[np.ndarray, list[str]]:
    """One 0/1 column per distinct label (sorted), named `prefix[label]`, without the labels listed in `drop`."""
    labels = np.asarray(labels)
    levels = [l for l in sorted(set(labels.tolist())) if not drop or l not in drop]
    cols = np.column_stack([(labels == l).astype(float) for l in levels]) if levels else np.zeros((len(labels), 0))
    return cols, [f"{prefix}[{l}]" for l in levels]


def fit_cluster_model(y, X, names: list[str], clusters):
    """OLS of `y` on the columns of `X` (named `names`; the caller writes out every dummy and any constant).

    Returns the statsmodels model (unfitted, as `wildboottest` wants it), the coefficients, and CR1 standard errors
    clustered on `clusters`: the sandwich with the factor G/(G-1) * (N-1)/(N-K). The design must have full column rank;
    this stops if it has not, because a dropped column would silently change what a coefficient means.
    """
    import pandas as pd
    import statsmodels.api as sm
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if np.isnan(y).any() or np.isnan(X).any():
        stop("a model was given a missing value: fit on complete cases only")
    rank = np.linalg.matrix_rank(X)
    if rank < X.shape[1]:
        stop(f"the design matrix has rank {rank} for {X.shape[1]} columns")
    exog = pd.DataFrame(X, columns=names)
    model = sm.OLS(pd.Series(y, name="y"), exog)
    groups = pd.factorize(np.asarray(clusters))[0]
    res = model.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True, "df_correction": True})
    return model, res


def wcb_test(y, X, names, clusters, param: str, B: int, seed: int) -> tuple[float, float]:
    """One restricted wild cluster bootstrap test of H0: the coefficient on `param` is zero. Returns (t, p)."""
    import pandas as pd
    import statsmodels.api as sm
    from wildboottest.wildboottest import wildboottest
    exog = pd.DataFrame(np.asarray(X, float), columns=names)
    model = sm.OLS(pd.Series(np.asarray(y, float), name="y"), exog)
    # The package compiles its inner loop and cannot take labels that are text: the clusters go in as whole numbers,
    # 0, 1, 2, ... in the sorted order of their labels (the district codes), which fixes which cluster gets which weight.
    codes = np.unique(np.asarray(clusters), return_inverse=True)[1].astype(np.int64)
    out = wildboottest(model, B=B, cluster=pd.Series(codes), param=param, weights_type="webb",
                       impose_null=True, seed=seed, show=False)
    return float(np.ravel(out["statistic"].iloc[0])[0]), float(np.ravel(out["p-value"].iloc[0])[0])


def wcb_interval(y, X, names, clusters, param: str, B: int, seed: int, estimate: float, se_cr1: float,
                 level: float = 0.05, grid_points: int = 16, max_doublings: int = 10, tol_se: float = 0.001) -> dict:
    """The wild-cluster-bootstrap interval for `param`, by test inversion, and the p-value of H0: beta = 0.

    H0: beta = b0 is tested by refitting with `y - b0 * x` (the same seed every time, so the same bootstrap weights).
    The bracket starts at the estimate +/- 4 CR1 standard errors and is doubled as a whole (both ends move together,
    so the two sides always reach the same number of standard errors from the estimate), at most `max_doublings` times,
    until p is below `level` at both ends. p is then read on `grid_points` equal steps from the estimate to each end; a side is
    bisected, to within `tol_se` of a CR1 standard error, inside the OUTERMOST step in which p crosses `level`. If an
    end never gets below `level`, that side is reported unbounded. For each side three things are returned about how p
    behaved along the bracket, because the p of this bootstrap need not fall steadily: `crossings` (how many steps of
    the grid cross `level`), `p_rises_again` (going outward, p climbs more than 0.01 above a value it had already
    fallen to: it is not monotone beyond the jitter of the draws) and `p_at_end` (p at the outer end of the bracket,
    which is where p settles when it stops falling). The grid of p values is returned in every case, and the caller
    saves it in every case.
    """
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    x = X[:, names.index(param)]
    cache: dict[float, float] = {}

    def p_at(b0: float) -> float:
        if b0 not in cache:
            cache[b0] = wcb_test(y - b0 * x, X, names, clusters, param, B, seed)[1]
        return cache[b0]

    t0, p0 = wcb_test(y, X, names, clusters, param, B, seed)
    out = {"wcb_t": t0, "wcb_p": p0, "B": B, "seed": seed, "weights": "webb", "impose_null": True}
    grids = {}
    width = 4.0 * se_cr1
    doublings = 0
    while (p_at(estimate - width) >= level or p_at(estimate + width) >= level) and doublings < max_doublings:
        width *= 2.0                                            # the bracket is doubled as a whole: both ends together
        doublings += 1
    for side, sign in (("lo", -1.0), ("hi", 1.0)):
        end = estimate + sign * width
        steps = [estimate + sign * width * k / grid_points for k in range(0, grid_points + 1)]
        ps = [p_at(b) for b in steps]
        grids[side] = [{"b0": b, "p": p} for b, p in zip(steps, ps)]
        out[f"doublings_{side}"] = doublings
        inside = [p >= level for p in ps]                       # True: b0 is not rejected
        crossings = [k for k in range(grid_points) if inside[k] != inside[k + 1]]
        lowest, rises = ps[0], False
        for p in ps[1:]:                                        # going outward: does p climb back above where it had been?
            rises = rises or p > lowest + 0.01
            lowest = min(lowest, p)
        out[f"crossings_{side}"] = len(crossings)
        out[f"p_rises_again_{side}"] = rises
        out[f"p_at_end_{side}"] = ps[-1]
        if p_at(end) >= level:
            out[f"ci95_{side}"] = None
            out[f"unbounded_{side}"] = True
            continue
        out[f"unbounded_{side}"] = False
        k = max(crossings)                                      # the outermost crossing
        a, b = steps[k], steps[k + 1]                           # p(a) >= level > p(b)
        while abs(b - a) > tol_se * se_cr1:
            mid = (a + b) / 2.0
            if p_at(mid) >= level:
                a = mid
            else:
                b = mid
        out[f"ci95_{side}"] = (a + b) / 2.0
    out["grid"] = grids
    out["n_tests"] = len(cache) + 1
    return out
