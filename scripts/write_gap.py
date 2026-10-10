#!/usr/bin/env python3
"""Writes docs/GAP.md: stage 4, the comparison of forest condition, need and allocation, as the owner ruled it on
10 October 2026. In the manner of docs/DECISION_LAYER.md: no figure in the document is typed.

    ~/.venvs/ictd-stage4/bin/python scripts/write_gap.py [--draft PATH]

Every figure is read from a table or record in 50_gap/ (or from a registered input) by the reading functions of
scripts/write_results.py, used here as they are, and is listed with its file in the document's last section. Every
conclusion the text draws from figures is tested against them before it is written (`hold`), and a figure that two
tables both carry is compared (`same`). The text itself may hold no digit outside a code span, a date, a year, a
financial year, a section number and the names of the comparisons, models, measures and figures (C1, P1, H1, N1, F1 ...):
a design constant (a floor, a level, a threshold) is written as code.

The script runs scripts/verify_gap.py and stops unless every check passes (not with --draft, which also refuses to
write into docs/). It reads the record of the deliberate errors tried against that verifier
(50_gap/verify_gap_trials.json) and stops unless every one was caught. It writes one file, docs/GAP.md.

Nothing in the document is about cause. The words "because", "led to", "effect of", "caused" and "drove" may appear
only where the text says what the analysis cannot show; the script counts them and holds each use to such a sentence.
"""
import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_results as W                      # its reading functions and gates, used as they are; importing it writes nothing

ROOT = W.ROOT
OUT = ROOT / "docs" / "GAP.md"
V, cell, key, count, agg, show, calc, hold, same, c, table = W.V, W.cell, W.key, W.count, W.agg, W.show, W.calc, W.hold, W.same, W.c, W.table
n0, dec, txt = W.n0, W.dec, W.txt
W.ALLOWED.append((r"\b(?:C(?:1[0-2]|[1-9])b?|B1|P[1-7]|H[1-9]|N[12]|R[12]|F[1-6]|L[1-5])\b", "the name of a comparison, a model, a measure of need or a figure"))
W.ALLOWED.append((r"\bCR1\b", "the name of a kind of standard error"))


def stop(message):
    raise SystemExit("GAP not written: " + message)


W.stop = stop                                  # the reading functions say which document was not written

SUM, LONG, NEED, ALLOC = "50_gap/need_vs_allocation_summary.csv", "50_gap/need_vs_allocation.csv", "50_gap/district_need.csv", "50_gap/district_allocation.csv"
SPLIT, MORE, PANEL, PM = "50_gap/marginalisation_split.csv", "50_gap/what_more.csv", "50_gap/district_year_panel.csv", "50_gap/panel_models.csv"
UH, UM = "50_gap/unit_history.csv", "50_gap/unit_history_models.csv"
FRA, FRS, FR2 = "50_gap/fra_by_district.csv", "50_gap/fra_summary.csv", "50_gap/fra_two_reports.csv"
PROV, FV, TRIALS = "50_gap/gap.provenance.json", "50_gap/forest_villages_pdf_record.json", "50_gap/verify_gap_trials.json"
STATE, CAUT2 = "00_raw/mis_reports/odisha_r620_state_totals_2014-2027.csv", "00_raw/05_forest_reference/provider_cautions_2026-10-10.json"
SHARE_EX = "70_share/exercise_share_chrome.json"
FSI, FSS = "50_gap/fsi_district_check.csv", "50_gap/fsi_summary.csv"                    # Phase 5b: the need beside the Forest Survey's figures
ISFR_V1 = "00_raw/05_forest_reference/isfr2023_vol1_pdf_pages_4_10_14_26_63_76_81.txt"  # the Survey's own definitions and data period (registered text of its pages)
SUP = "00_raw/07_project_record/supervisor_comments_as_recorded_2026-10-11.json"                     # the supervisor's comments, as the owner recorded them
REVIEWS = "50_gap/verify_gap_reviews.json"                                              # what the one round of review of the verifier's parts reported
RUN_LOG = "docs/stage4_run_log.md"
CAUSAL = re.compile(r"\b(because|led to|effect of|effects of|caused|drove|causes?|driven by)\b", re.I)


def lakh(x):
    return W.fix(f"{float(x):,.2f}")


def crore_of_lakh(x):
    return W.fix(f"{float(x) / 100:,.2f}")


def ci(path, lo, hi, fmt, **where):
    return cell(path, lo, **where), cell(path, hi, **where)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", help="write to this path, outside docs/, without running the verifier")
    a = ap.parse_args()
    if a.draft and Path(a.draft).resolve().parent == (ROOT / "docs").resolve():
        stop("a draft is not written into docs/")
    written = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    DOC = []
    P = W.J(PROV)

    # ==== what is on disk, and the checks ============================================================================================
    show("written_utc", V(written, "this run", "the UTC time at which this script ran"), txt)
    show("v_gap", W.verifier("verify_gap.py", a.draft), txt)
    trials = key(TRIALS, "trials").v
    show("trials_n", V(len(trials), TRIALS, "key `trials`: their number"), n0)
    show("trials_caught", V(sum(1 for t in trials if t["caught"]), TRIALS, "key `trials`: those with `caught` true"), n0)
    hold(len(trials) >= 15 and all(t["caught"] for t in trials), "at least fifteen deliberate errors were tried against the verifier and every one was caught")
    damaged = {x for t in trials for x in t["tables"]}
    show("trials_tables", V(len(damaged), TRIALS, "key `trials`: the distinct files the errors were planted in"), n0)
    on_disk = sorted([p_.name for p_ in (ROOT / "50_gap").glob("*.csv") if not p_.name.startswith(("gates_", "environment_", "results_md_", "rebuild_"))]
                     + ["deck_tables/" + p_.name for p_ in (ROOT / "50_gap" / "deck_tables").glob("*.csv")])
    hold(all(x in damaged for x in on_disk) and {"panel_models.txt", "unit_history_models.txt", "gap.provenance.json", "forest_villages_pdf_record.json"} <= damaged,
         "an error was planted in every table of `50_gap/` (the gate tables, the list of what changed in `docs/RESULTS.md` and the lists of what differs between two builds apart), in each of the two text files of the models, in the provenance record and in the record of the check of the forest villages PDF")
    hold(key(TRIALS, "control/passed").v is True and key(TRIALS, "verifier_sha256").v == W.sha256(W.use("scripts/verify_gap.py")),
         "the trials were made with the verifier that is on disk, and the untouched tables passed it")
    kinds = sorted({t["kind"] for t in trials})
    for k_ in ("a swapped district code", "a part-year leak into a sum", "a shifted lag", "a wrong denominator", "a dropped East Coast exclusion"):
        hold(k_ in kinds, f"among the errors tried: {k_}")
    steps = {k_: P["steps"][k_] for k_ in ("08_gap_environment", "08_gap_inputs", "08_build_gap_districts", "08_build_gap_panel", "08_build_gap_units", "08_build_gap_rights", "08_build_gap_fsi")}
    REQ = "requirements-stage4.txt"
    for k_, s_ in steps.items():
        hold(s_["script_sha256"] == W.sha256(W.use(s_["script"])) and s_["shared_module_sha256"] == W.sha256(W.use(s_["shared_module"]))
             and all(W.sha256(W.use(i_["path"])) == i_["sha256"] for i_ in s_["inputs"].values())
             and all(W.sha256(W.use(o_)) == m_["sha256"] for o_, m_ in s_["outputs"].items()) and s_["gates"] == s_["gates_passed"],
             f"the tables of `{s_['script']}` are those its record describes: made by the script and the shared module on disk from inputs that have not changed since, with every gate passed")
        hold(s_["environment"]["holds_exactly_what_the_file_pins"] is True and s_["environment"]["requirements_sha256"] == W.sha256(W.use(REQ))
             and s_["environment"]["packages"] == steps["08_gap_environment"]["environment"]["packages"],
             f"`{s_['script']}` ran in an environment that held exactly what `{REQ}` pins, the file as it is on disk")
    show("env_n", V(steps["08_gap_environment"]["environment"]["packages_pinned"], PROV, "key `steps` → `08_gap_environment` → `environment` → `packages_pinned`"), n0)
    show("main_numpy", V(steps["08_gap_environment"]["main_environment"]["numpy"], PROV, "key `steps` → `08_gap_environment` → `main_environment` → `numpy`"), txt)
    GENV = "50_gap/gates_environment.csv"
    show("env_gates", count(GENV, "its rows", lambda t: t.gate.notna()), n0)
    hold((W.C(GENV)["pass"] == "yes").all() and steps["08_gap_environment"]["main_environment"]["the_version_the_earlier_records_show"] == [steps["08_gap_environment"]["main_environment"]["numpy"]],
         "every gate on the two environments passed, and the main environment's numpy is the one version the earlier stages' provenance records show")
    show("run_districts", V(steps["08_build_gap_districts"]["run_utc"], PROV, "key `steps` → `08_build_gap_districts` → `run_utc`"), txt)
    show("pkg", V("; ".join(f"{k_} {v_}" for k_, v_ in steps["08_build_gap_units"]["package_versions"].items() if k_ in ("python", "numpy", "pandas", "scipy", "statsmodels", "numba", "wildboottest")),
                  PROV, "key `steps` → `08_build_gap_units` → `package_versions`"), txt)
    n_d = show("n_districts", count(NEED, "its rows", lambda t: t.pc11_district_code.notna()), n0)
    n_u = show("n_units", agg(NEED, "`n_units` summed", lambda t: t.n_units.sum()), n0)
    show("n_units_out", agg(NEED, "`n_units_outside` summed", lambda t: t.n_units_outside.sum()), n0)
    show("n_fy", V(int(W.C(PANEL).fy.nunique()), PANEL, "column `fy`: the distinct financial years"), n0)
    show("n_panel", count(PANEL, "its rows", lambda t: t.fy.notna()), n0)
    n_models = show("n_dy", count(PANEL, "rows with `in_models` 1", lambda t: t.in_models == 1), n0)
    same("district-years in the models, in the panel and in the table of models", n_models.v, cell(PM, "n", id="P1").v)

    DOC.append("""# Stage 4: forest condition, need and allocation, compared

*Written {written_utc} by `scripts/write_gap.py`. No figure in this document was typed. Each was read by that script from
the file named for it in the last section, and each conclusion drawn from figures was tested against them before it was
written. The figures change only when the files do.*

## 1. What this is

The supervisor's question, in his words: "determine which areas have seen forest degradation, are also marginalised,
and have they seen good enough resource allocation in the past".

This stage sets three things beside one another that the earlier stages measured apart: where forest was lost
(stage 1, read through the decision table), who lives there (stage 2), and where the employment scheme's money went
(stage 3, and the scheme's own state report). It was built on 10 October 2026 as the project owner ruled it that day
(§2). Its tables are in `50_gap/` (the tables of districts were made {run_districts}); `docs/RESULTS.md` and
`docs/DECISION_LAYER.md` describe what they are built from.

**It describes where money went relative to where forest was lost. It says nothing about why.** No figure here is an
effect of anything on anything, and the words that would claim one are used in this document only to say what the
analysis cannot show (§12).

Current allocation exists only by district, in the scheme's state report R6.20. So **the district is the unit of the
headline**: {n_districts} districts, holding the {n_units} units of the earlier stages, {n_units_out} of them land
outside any revenue village. A history of units within districts is its companion (§9), and it can speak only of
works started by FY2017-18, where the geotagged record of works effectively ends.

How far it was checked: `scripts/verify_gap.py`, which imports nothing from the scripts that built the tables,
recomputed the figures of every table the stage's steps write, from the inputs: "{v_gap}". {trials_n} deliberate
errors were then planted in copies of the stage's files, {trials_tables} files in all, and it caught {trials_caught}
(§14, which also says what it does not hold).
""")

    # ==== 2 and 3: the decisions, and the calls ======================================================================================
    c7 = cell(SUM, "districts_left_out", comparison="C7")
    c7b = cell(SUM, "districts_left_out", comparison="C7b")
    show("c7_list", V(c7.v.replace("; ", ", "), c7.file, c7.col, c7.row), txt)
    show("c7b_list", V(c7b.v.replace("; ", ", "), c7b.file, c7b.col, c7b.row), txt)
    c7n = show("c7_n", cell(SUM, "n_districts", comparison="C7"), n0)
    c7bn = show("c7b_n", cell(SUM, "n_districts", comparison="C7b"), n0)
    hold(set(c7.v.split("; ")) < set(c7b.v.split("; ")), "every district C7 leaves out is also left out under the other reading of its rule, which leaves out more")
    same("districts C7 leaves out, in the comparison table and in the table of districts", n_d.v - c7n.v, count(NEED, "rows with `left_out_of_c7` yes", lambda t: t.left_out_of_c7 == "yes").v)
    nz = show("n1_no_zone", agg(NEED, "`n1_ha_2018_2025_in_units_with_no_zone` summed", lambda t: t.n1_ha_2018_2025_in_units_with_no_zone.sum()), n0)
    hold(nz.v == 0, "no N1 lies in a unit for which no zone model is recorded, so the rule for C7 can be decided for every district")
    h9 = cell(UM, "n_units", id="H9")
    sd_pre = show("sd_pre", agg(PANEL, "the standard deviation (n in the divisor) of `plantation_pct_of_all` over the rows whose `period` is pre", lambda t: t.loc[t.period == "pre", "plantation_pct_of_all"].std(ddof=0)), dec(2))
    sd_post = show("sd_post", agg(PANEL, "the same over the rows whose `period` is post", lambda t: t.loc[t.period == "post", "plantation_pct_of_all"].std(ddof=0)), dec(2))
    show("sd_pre_n1", agg(PANEL, "the same over pre, with n - 1 in the divisor", lambda t: t.loc[t.period == "pre", "plantation_pct_of_all"].std(ddof=1)), dec(2))
    hold(sd_pre.v > 3 * sd_post.v, "plantation's share of district expenditure varies several times more across district-years before FY2018-19 than after")
    lag_of = lambda per: (lambda t: float(t[(t.in_models == 1) & (t.period == per)].groupby("fy").loss_ha_year_t_minus_1.sum().mean()))
    lag_pre = show("lag_pre", agg(PANEL, "`loss_ha_year_t_minus_1` summed over the districts for each financial year of the pre period, then the mean of those years", lag_of("pre")), n0)
    lag_post = show("lag_post", agg(PANEL, "the same for the financial years of the post period", lag_of("post")), n0)
    hold(lag_post.v > lag_pre.v, "the state's forest loss in the year before, the regressor of the panel, is higher on average over the post period's years than over the pre period's")
    open_of = lambda per: (lambda t: float(t[(t.in_models == 1) & (t.period == per)].assign(o=lambda x: x.loss_ha_year_t_minus_1 - x.loss_dense_ha_year_t_minus_1).groupby("fy").o.sum().mean()))
    hold(agg(PANEL, "open-band loss of the year before (both bands less the dense band), by year, mean over the post period", open_of("post")).v
         > agg(PANEL, "the same over the pre period", open_of("pre")).v, "the open band's loss, by year, is higher on average over the post period's years than over the pre period's")
    fv_pages = show("fv_pages", key(FV, "pages"), n0)
    show("fv_rows", key(FV, "summary_rows_read"), n0)
    show("fv_ok", key(FV, "summary_rows_that_add_up"), n0)
    fv_a = key(FV, "check_a").v
    hold(key(FV, "pages_that_are_one_image").v == fv_pages.v and key(FV, "text_usable_for_counts").v is False and fv_a["holds"] is False
         and key(FV, "which_check_failed").v == "(a)" and key(FV, "check_b").v["run"] is False and "forest_villages" not in " ".join(W.C(NEED).columns),
         "every page of the forest villages PDF is one scanned image; its text layer fails check (a) of the owner's rule; check (b) was not run; and no count from it is in the table of districts")
    hold(len(fv_a["parts"]) == len(fv_a["parts_that_fail"]) and all(x_["holds_in"] < x_["of"] for x_ in fv_a["parts"]),
         "the layer of the forest villages PDF fails every one of the parts check (a) was made into")
    show("fv_parts", V(len(fv_a["parts"]), FV, "key `check_a` → `parts`: their number"), n0)

    DOC.append("""
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
  land the CoRE Stack classes, and the units without one carry {n1_no_zone} ha of N1. So the first branch was used: a
  district is left out where units wholly under the East Coast model hold more than half of its N1, and a district
  with no N1 stays in. That leaves out {c7_list}, and {c7_n} districts stay. The other reading - every district that
  holds a unit the agreement headline left out - would leave out {c7b_list}, and {c7b_n} would stay. It is computed
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
- **The standard deviations the instruction quotes** ({sd_pre} and {sd_post} percentage points) are those with n in
  the divisor; with `n - 1` the first is {sd_pre_n1}.
- **How the bootstrap's p is reported** (§8): beside each interval, whether p fell steadily along the bracket.
- **How the owner's first check on the forest villages list was made into parts** (§10). His rule asks that what is
  parsed from the layer equal every total and running serial number the file prints. This stage reads the layer as
  `pdftotext` gives it and asks {fv_parts} things of it; what counts there as a row, a district's page and a serial
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
""")

    # ==== 4. definitions, with the state's totals ====================================================================================
    n1 = show("n1_state", agg(NEED, "`n1_ha_2018_2025` summed", lambda t: t.n1_ha_2018_2025.sum()), n0)
    allloss = show("loss_state", agg(NEED, "`forest_loss_ha_2018_2025_all_units` summed", lambda t: t.forest_loss_ha_2018_2025_all_units.sum()), n0)
    below = show("below_min", agg(NEED, "`loss_below_minimum_ha_2018_2025` summed", lambda t: t.loss_below_minimum_ha_2018_2025.sum()), n0)
    same("N1 plus the loss under the minimum, and all forest loss of the window", n1.v + below.v, allloss.v, 0.001)
    same("N1 of the state, in the table of districts and in the comparison table", n1.v, cell(SUM, "need_total", comparison="C1").v, 0.001)
    n1_out = agg(NEED, "`n1_ha_2018_2025_outside` summed", lambda t: t.n1_ha_2018_2025_outside.sum())
    calc("n1_out_pct", 100 * n1_out.v / n1.v, dec(1), "N1 on outside-village land ÷ N1 × 100", [n1_out, n1])
    hold(n1_out.v > n1.v / 2, "more than half of N1 lies on outside-village land")
    n2 = show("n2_state", agg(NEED, "`n2_ha` summed", lambda t: t.n2_ha.sum()), n0)
    show("loss_0113", agg(NEED, "`loss_2001_2013_ha` summed", lambda t: t.loss_2001_2013_ha.sum()), n0)
    show("n_loss_units", agg(NEED, "`n_units_loss_cells_2018_2025` summed", lambda t: t.n_units_loss_cells_2018_2025.sum()), n0)
    show("n_anr_units", agg(NEED, "`n_units_anr` summed", lambda t: t.n_units_anr.sum()), n0)
    cells_ = P["steps"]["08_build_gap_districts"]["cell_names"]
    show("loss_cell_names", V("; ".join(f'"{cells_[k_]}"' for k_ in ("open_loss", "dense_loss", "little_loss")), PROV, "key `steps` → `08_build_gap_districts` → `cell_names`: the three cells with loss recorded"), txt)
    show("anr_cell_name", V(f'"{cells_["open_none"]}"', PROV, "key `steps` → `08_build_gap_districts` → `cell_names` → `open_none`"), txt)
    pre = show("plant_pre", agg(ALLOC, "`r620_plantation_pre_lakh` summed", lambda t: t.r620_plantation_pre_lakh.sum()), lakh)
    post = show("plant_post", agg(ALLOC, "`r620_plantation_post_lakh` summed", lambda t: t.r620_plantation_post_lakh.sum()), lakh)
    show("plant_part", agg(ALLOC, "`r620_plantation_part_year_lakh` summed", lambda t: t.r620_plantation_part_year_lakh.sum()), lakh)
    all_pre = agg(ALLOC, "`r620_all_pre_lakh` summed", lambda t: t.r620_all_pre_lakh.sum())
    all_post = agg(ALLOC, "`r620_all_post_lakh` summed", lambda t: t.r620_all_post_lakh.sum())
    pre_pct = calc("plant_pre_pct", 100 * pre.v / all_pre.v, dec(2), "plantation ÷ all expenditure × 100, FY2014-15 to FY2017-18", [pre, all_pre])
    post_pct = calc("plant_post_pct", 100 * post.v / all_post.v, dec(2), "plantation ÷ all expenditure × 100, FY2018-19 to FY2025-26", [post, all_post])
    hold(post_pct.v < pre_pct.v / 10, "plantation's share of all expenditure after FY2017-18 is less than a tenth of what it was before")
    same("post-period plantation money, in the table of districts and in the comparison table", post.v, cell(SUM, "allocation_total", comparison="C1").v, 0.005)
    stamp = show("stamp_pre", V(str(W.C(ALLOC).r620_pre_years_last_updated.iloc[0]), ALLOC, "column `r620_pre_years_last_updated`"), txt)
    hold(W.C(ALLOC).r620_pre_years_last_updated.nunique() == 1, "the four pre-period tables carry one stamp")
    st_ = W.C(STATE)
    later = sorted({str(x) for x in st_.loc[st_.fy.isin([f"{y}-{y + 1}" for y in range(2020, 2027)]), "last_updated"]}, key=lambda d_: d_.split("/")[::-1])
    show("stamps_late", V(" and ".join(later), STATE, "column `last_updated` of the rows for FY2020-21 to FY2026-27: the distinct stamps"), txt)
    fn = show("dump_fn", agg(ALLOC, "`dump_forest_named_started_by_fy2017_18_inr` summed", lambda t: t.dump_forest_named_started_by_fy2017_18_inr.sum()), W.crore)
    show("dump_fn_missing", agg(ALLOC, "`dump_forest_named_start_year_missing_inr` summed", lambda t: t.dump_forest_named_start_year_missing_inr.sum()), n0)
    show("dump_fn_later", agg(ALLOC, "`dump_forest_named_started_later_inr` summed", lambda t: t.dump_forest_named_started_later_inr.sum()), W.crore)
    show("dump_pl", agg(ALLOC, "`dump_plantation_category_started_by_fy2017_18_inr` summed", lambda t: t.dump_plantation_category_started_by_fy2017_18_inr.sum()), W.crore)
    show("dump_pl_missing", agg(ALLOC, "`dump_plantation_category_start_year_missing_inr` summed", lambda t: t.dump_plantation_category_start_year_missing_inr.sum()), n0)
    show("no_unit", agg(ALLOC, "`dump_no_unit_total_inr` summed", lambda t: t.dump_no_unit_total_inr.sum()), W.crore)
    show("no_unit_fn", agg(ALLOC, "`dump_no_unit_forest_named_inr` summed", lambda t: t.dump_no_unit_forest_named_inr.sum()), W.crore)
    pop = show("pop_lgd", agg(NEED, "`population_lgd` summed", lambda t: t.population_lgd.sum()), n0)
    stp = agg(NEED, "`st_pop_lgd` summed", lambda t: t.st_pop_lgd.sum())
    calc("st_state_pct", 100 * stp.v / pop.v, dec(1), "Scheduled Tribe population ÷ population × 100, LGD panchayat units", [stp, pop])
    cov = show("adi_cov_min", agg(NEED, "the smallest `adi_2011_population_covered_pct`", lambda t: t.adi_2011_population_covered_pct.min()), dec(1))
    adi = P["steps"]["08_build_gap_districts"]["adi"]
    show("adi_source", V(adi["source_and_licence"], PROV, "key `steps` → `08_build_gap_districts` → `adi` → `source_and_licence` (read by the builder from the layer's list of sources)"), txt)
    show("adi_dir_need", V(adi["direction"]["docs/NEED.md"], PROV, "key `steps` → `08_build_gap_districts` → `adi` → `direction`: the sentence of `docs/NEED.md`"), txt)
    show("adi_dir_docx", V(adi["direction"]["00_raw/docs/Village_level_dataset_schema_31Oct2022.docx"], PROV, "the same key: the sentence of the group's data dictionary"), txt)
    hold(adi["direction"]["docs/NEED.md"] in " ".join(W.use("docs/NEED.md").read_text(encoding="utf-8").split()), "the sentence about the index quoted from `docs/NEED.md` stands in that document")

    DOC.append("""
## 4. Definitions

All of it comes from tables already on disk. Nothing here was read from Earth Engine.

**Forest** is Hansen canopy above ten per cent in the year 2000: the two bands the decision table uses, dense (above
thirty) and open (ten to thirty). The band at or below ten decides nothing here either. Hectares are those the
decision table carries.

**Need, for each district.**

- **N1, the headline need**: forest loss in a window of years, summed over the units whose cell in that window is one
  of the three with loss recorded ({loss_cell_names}). In the default window, the years 2018 to 2025, that is {n1_state} ha
  in {n_loss_units} units. All forest loss of the window, over every unit, is {loss_state} ha; the difference,
  {below_min} ha, is loss in units that lost less than the minimum of `1 ha`. {n1_out_pct} per cent of N1 lies on
  outside-village land.
- **N2**: the standing open-band hectares of the units whose cell in the default window is {anr_cell_name}:
  {n2_state} ha in {n_anr_units} units. "Standing" is the forest of 2000 with no loss recorded since; not a measure of
  tree cover today. **N2 is a stock and N1 is a flow. They are never added.**
- Both are also given for LGD-unit land and for outside-village land apart.
- **Forest loss of 2001 to 2013**, every unit, both bands: {loss_0113} ha. It is loss before the state report begins,
  and it is used by one comparison (C4).

**Allocation, for each district.**

- **R6.20 plantation expenditure**: {plant_pre} lakh rupees over FY2014-15 to FY2017-18 ("pre") and {plant_post} lakh
  over FY2018-19 to FY2025-26 ("post"): {plant_pre_pct} and {plant_post_pct} per cent of all the scheme's expenditure
  in the two periods. **The four pre years are those whose tables carry the stamp {stamp_pre}: a snapshot frozen in
  2020**, and that is said wherever "pre" appears. FY2026-27 is a part year ({plant_part} lakh so far); it is reported
  alone and enters no sum, no share and no model.
- **For context**, R6.20's natural-resource (NRM) and all expenditure of the same periods. They are compared with need
  only in the benchmark B1. NRM, water and plantation are nested categories: never added, never subtracted.
- **From the geotagged record of works ("the dump")**: expenditure on work types that name forest, on works started
  in or before FY2017-18, summed over the district's units: ₹{dump_fn} crore in all; and the plantation category on the
  same basis, ₹{dump_pl} crore. These are lifetime costs indexed by the year a work started, unlike R6.20, and are
  never put in a sum with it. A work with no start year counts as not started by then: ₹{dump_fn_missing} of
  forest-named money and ₹{dump_pl_missing} of plantation-category money, given by district beside each column;
  forest-named works started later carry ₹{dump_fn_later} crore. **Left out**: the works that fall in no unit,
  ₹{no_unit} crore of all expenditure (₹{no_unit_fn} crore of it forest-named), listed by the district of their file.

**Marginalisation, for each district**, on the census population of LGD panchayat units only ({pop_lgd} people,
{st_state_pct} per cent of them of the Scheduled Tribes). **Outside-village land has no census rows**, so none of
these columns knows anything of the land where most of N1 lies; that is said wherever they appear.

- **Scheduled Tribe share**, classed with the layer's own breaks.
- **The development index of 2011**: the mean over the district's LGD units that have a value, weighted by population
  (at least {adi_cov_min} per cent of a district's population is covered), in terciles of ten districts. Which way it
  runs is taken from two documents of the repository: `docs/NEED.md` ("{adi_dir_need}") and the group's data dictionary
  in `00_raw/docs/` ("{adi_dir_docx}"). A higher index is a more developed place. Its source and licence, as the layer's
  list of sources gives them: *{adi_source}*
- **Scheduled Caste share**, in terciles of ten districts.
- The poverty rate stays out, as before.
""")

    # ==== 5. the headline ============================================================================================================
    def cmp_(cid, col, blank_ok=False):
        return cell(SUM, col, blank_ok=blank_ok, comparison=cid)

    c1r, c1lo, c1hi, c1p = cmp_("C1", "rho"), cmp_("C1", "ci95_lo"), cmp_("C1", "ci95_hi"), cmp_("C1", "p_permutation")
    show("c1_rho", c1r, dec(2)); show("c1_lo", c1lo, dec(2)); show("c1_hi", c1hi, dec(2)); show("c1_p", c1p, dec(5))
    show("n_perm", cmp_("C1", "n_permutations"), n0); show("n_boot", cmp_("C1", "n_bootstrap"), n0)
    hold(c1r.v > 0 and c1lo.v > 0, "C1: need and post-period plantation money rise together across districts, and the interval of rho lies above zero")
    b1r, b1lo, b1hi = cmp_("B1", "rho"), cmp_("B1", "ci95_lo"), cmp_("B1", "ci95_hi")
    show("b1_rho", b1r, dec(2)); show("b1_lo", b1lo, dec(2)); show("b1_hi", b1hi, dec(2))
    hold(b1lo.v > 0 and c1lo.v < b1hi.v and b1lo.v < c1hi.v, "the benchmark's rho is also above zero, and its interval overlaps C1's: rank correlation of this size is what district size alone produces")
    bench_word = "above" if c1r.v > b1r.v else "below"
    hold((c1r.v > b1r.v) == (bench_word == "above"), f"C1's rho is {bench_word} the benchmark's")
    c12r, c12lo, c12hi, c12p = cmp_("C12", "rho"), cmp_("C12", "ci95_lo"), cmp_("C12", "ci95_hi"), cmp_("C12", "p_permutation")
    show("c12_rho", c12r, dec(2)); show("c12_lo", c12lo, dec(2)); show("c12_hi", c12hi, dec(2)); show("c12_p", c12p, dec(3))
    hold(0 < c12r.v < c1r.v, "with district size taken out of both sides (C12) rho is smaller than C1's and still positive")
    c12_word = "lies just above zero" if 0 < c12lo.v < 0.1 else ("lies above zero" if c12lo.v > 0 else "includes zero")
    hold((c12lo.v > 0) == ("above zero" in c12_word), f"C12's interval {c12_word}")
    c1b, c1bn = cmp_("C1", "need_share_pct_where_r_below_0_5"), cmp_("C1", "n_districts_r_below_0_5")
    c1a, c1an = cmp_("C1", "need_share_pct_where_r_above_2"), cmp_("C1", "n_districts_r_above_2")
    show("c1_below", c1b, dec(1)); show("c1_below_n", c1bn, n0); show("c1_above", c1a, dec(1)); show("c1_above_n", c1an, n0)
    show("c1_zero_n", cmp_("C1", "n_districts_need_zero"), n0)
    gaps = show("c1_gaps", cmp_("C1", "sum_positive_gaps_lakh"), lakh)
    calc("c1_gaps_pct", 100 * gaps.v / post.v, dec(0), "the sum of the positive gaps ÷ post-period plantation money × 100", [gaps, post])
    hold(c1b.v > 50 and c1bn.v < n_d.v / 3, "more than half of the state's need lies in a few districts whose share of the money is under half their share of the need")
    hold(c1a.v < 5 and c1an.v > c1bn.v, "more districts have over twice their need share of the money than have under half, and together they hold a small part of the need")
    hold(c12r.v < c1r.v - 0.2 and c12lo.v < c1lo.v, "with size taken out of both sides (C12) rho is lower than C1's by more than two tenths, and its interval starts lower: the association is much weaker than C1's figure alone suggests")
    long = W.C(LONG)
    c1_rows = long[long.comparison == "C1"].sort_values("need", ascending=False)
    below = c1_rows[c1_rows.r.notna() & (c1_rows.r < 0.5)]
    show("below_names", V(", ".join(below.district_name), LONG, "C1: the `district_name` of the rows whose `r` is below 0.5, the largest `need` first"), txt)
    hold(len(below) == c1bn.v and abs(float(below.need_share_pct.sum()) - c1b.v) < 0.001,
         "the districts named as having under half their need share of the money are those the summary counts, and their need shares add to the share it gives")
    table("T_three", ["", "need", "allocation", "Spearman's rho (interval)", "permutation p"],
          [[label_, c(cmp_(i_, "need_is"), txt), c(cmp_(i_, "allocation_is"), txt), W.span(cmp_(i_, "rho"), cmp_(i_, "ci95_lo"), cmp_(i_, "ci95_hi")), c(cmp_(i_, "p_permutation"), dec(5))]
           for i_, label_ in (("C1", "C1, the headline"), ("B1", "B1, what district size alone gives"), ("C12", "C12, with size taken out of both sides"))])
    top = c1_rows.head(8)
    show("top_n", V(len(top), LONG, "the rows of C1 with the largest `need`: how many are tabled"), n0)
    calc("top_need_pct", float(top.need_share_pct.sum()), dec(1), "the need shares of those districts added", [V(float(top.need_share_pct.sum()), LONG, "column `need_share_pct` of those rows")])
    need_t = W.C(NEED).set_index("pc11_district_code")
    rows_top = []
    for _, r_ in top.iterrows():
        code = int(r_.pc11_district_code)
        w_ = dict(comparison="C1", pc11_district_code=code)
        rows_top.append([c(cell(LONG, "district_name", **w_), txt), c(cell(LONG, "need", **w_), n0), c(cell(LONG, "need_share_pct", **w_), dec(1)),
                         c(cell(LONG, "allocation_share_pct", **w_), dec(1)), c(cell(LONG, "allocation_share_pct", comparison="C5", pc11_district_code=code), dec(1)),
                         c(cell(LONG, "r", **w_), dec(2)), c(cell(LONG, "gap_lakh", **w_), n0), c(cell(NEED, "st_class", pc11_district_code=code), txt),
                         c(cell(NEED, "adi_tercile", pc11_district_code=code), txt)])
    table("T_top", ["district", "N1, ha", "share of need, %", "share of post-period plantation money, %", "share of pre-period plantation money, % (frozen snapshot)",
                    "money share ÷ need share (`r`)", "the same money distributed by need, less what it had, lakh", "Scheduled Tribe class", "tercile of the development index"], rows_top)
    first, second = top.iloc[0], top.iloc[1]
    show("d1_name", V(first.district_name, LONG, "C1: the district with the largest `need`"), txt)
    show("d2_name", V(second.district_name, LONG, "C1: the district with the second largest `need`"), txt)
    hold(first.r < 0.5 and second.r > 1, "the district with the most need has under half its need share of the money, and the district with the second most has more than its share")
    ids = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C7b", "C8", "C9", "C10", "C11", "C12", "B1"]
    rows_cmp = []
    for i_ in ids:
        kind_ = cmp_(i_, "kind").v
        rows_cmp.append([i_ if i_ != "C7b" else "C7b (not fixed beforehand)", c(cmp_(i_, "need_is"), txt), c(cmp_(i_, "allocation_is"), txt), c(cmp_(i_, "n_districts"), n0),
                         W.span(cmp_(i_, "rho"), cmp_(i_, "ci95_lo"), cmp_(i_, "ci95_hi")), c(cmp_(i_, "p_permutation"), dec(5)),
                         c(cmp_(i_, "need_share_pct_where_r_below_0_5", blank_ok=True), dec(1)), c(cmp_(i_, "need_share_pct_where_r_above_2", blank_ok=True), dec(1)),
                         c(cmp_(i_, "sum_positive_gaps_lakh", blank_ok=True), n0)])
    table("T_cmp", ["comparison", "need", "allocation", "districts", "Spearman's rho (interval)", "permutation p", "need in districts with `r` below `0.5`, %",
                    "need in districts with `r` above `2`, %", "sum of the positive gaps, lakh"], rows_cmp)
    wins = [cmp_(i_, "rho").v for i_ in ("C8", "C9", "C10")]
    show("win_lo", V(min(wins), SUM, "the smallest `rho` among C8, C9 and C10"), dec(2)); show("win_hi", V(max(wins), SUM, "the largest `rho` among C8, C9 and C10"), dec(2))
    hold(all(cmp_(i_, "ci95_lo").v > 0 for i_ in ("C8", "C9", "C10")) and max(abs(w_ - c1r.v) for w_ in wins) < 0.05, "under each of the other three windows rho is within a few hundredths of C1's and its interval lies above zero")
    c7r, c7br = cmp_("C7", "rho"), cmp_("C7b", "rho")
    show("c7_rho", c7r, dec(2)); show("c7b_rho", c7br, dec(2))
    hold(abs(c7r.v - c1r.v) < 0.05 and abs(c7br.v - c1r.v) < 0.05 and cmp_("C7", "ci95_lo").v > 0 and cmp_("C7b", "ci95_lo").v > 0,
         "leaving out the East Coast districts, under either reading of the rule, changes rho by a few hundredths at most and its interval stays above zero")
    c11r = cmp_("C11", "rho"); show("c11_rho", c11r, dec(2)); show("c11_lo", cmp_("C11", "ci95_lo"), dec(2)); show("c11_hi", cmp_("C11", "ci95_hi"), dec(2))
    fy1 = agg(ALLOC, "`r620_plantation_post_lakh` less `r620_plantation_post_without_fy2018_19_lakh`, summed", lambda t: (t.r620_plantation_post_lakh - t.r620_plantation_post_without_fy2018_19_lakh).sum())
    calc("fy1819_pct", 100 * fy1.v / post.v, dec(0), "plantation money of FY2018-19 ÷ post-period plantation money × 100", [fy1, post])
    hold(c11r.v < c1r.v and cmp_("C11", "ci95_lo").v > 0, "without FY2018-19 rho is lower than C1's and its interval still lies above zero")
    c3r = cmp_("C3", "rho"); show("c3_rho", c3r, dec(2)); show("c3_lo", cmp_("C3", "ci95_lo"), dec(2)); show("c3_hi", cmp_("C3", "ci95_hi"), dec(2))
    hold(cmp_("C3", "ci95_lo").v < 0 < cmp_("C3", "ci95_hi").v, "for N2 the interval of rho includes zero")
    c4r, c5r, c6r = cmp_("C4", "rho"), cmp_("C5", "rho"), cmp_("C6", "rho")
    show("c4_rho", c4r, dec(2)); show("c5_rho", c5r, dec(2)); show("c6_rho", c6r, dec(2))
    hold(min(c4r.v, c5r.v, c6r.v) > c1r.v and all(cmp_(i_, "ci95_lo").v > 0 for i_ in ("C4", "C5", "C6")), "the three comparisons with money of the years before FY2018-19 each give a higher rho than C1, with intervals above zero")
    hold(all(cmp_(i_, "ci95_lo").v < cmp_("C1", "ci95_hi").v and cmp_("C1", "ci95_lo").v < cmp_(i_, "ci95_hi").v for i_ in ("C4", "C5", "C6")),
         "the interval of each of those three comparisons overlaps C1's: none of the three is shown to differ from C1")
    c2r = cmp_("C2", "rho"); show("c2_rho", c2r, dec(2))
    hold(abs(c2r.v - c1r.v) < 0.05, "on LGD-unit land alone rho is within a few hundredths of C1's")

    DOC.append("""
## 5. The headline: C1, and what it does and does not rest on

**C1 asks: in the years plantation fell out of the scheme, did what was left go where forest was being lost?** Need is
N1 of the years 2018 to 2025 on all land; allocation is R6.20 plantation expenditure of FY2018-19 to FY2025-26.

**The finding, in volumes first.** {c1_below} per cent of the state's N1 lies in {c1_below_n} districts whose share of
the post-period plantation money is under half their share of the need (`r` below `0.5`): {below_names}. {more_r1} ha
of N1, {more_r1_pct} per cent of it, lie in districts whose share of that money is below their share of the need (`r`
below `1`). At the other end {c1_above_n} districts have more than twice their need share of the money (`r` above
`2`), and together they hold {c1_above} per cent of the need. {c1_zero_n} districts have no N1 at all, so no `r`.

**The rank correlation is not read alone.** Across the {n_districts} districts need and allocation rise together, and
not one for one: Spearman's rho is {c1_rho} (`95 %` interval {c1_lo} to {c1_hi}, from {n_boot} resamples of districts;
two-sided permutation p {c1_p}, from {n_perm} shuffles). Two figures stand beside it, and it means little without
them.

{T_three}

*n = {n_districts} districts in each row; the interval is a `95 %` percentile bootstrap over districts and p is from
shuffling allocation against need.*

- **B1 is what district size alone gives.** A large district has more of everything. B1 sets the same need against
  *all* the scheme's expenditure of the same years: rho {b1_rho} ({b1_lo} to {b1_hi}). C1's rho is """ + bench_word + """ it, and the two
  intervals overlap: plantation money follows need across districts about as closely as the scheme's money as a whole
  does.
- **C12 takes size out of both sides**: N1 per `100 ha` of the district's forest, against plantation's share of the
  district's own expenditure. Its rho is {c12_rho} ({c12_lo} to {c12_hi}; p {c12_p}), and that interval
  """ + c12_word + """. What is left of the association once size is out is much weaker than C1's figure suggests.
- **The same money distributed by need** would move {c1_gaps} lakh rupees, {c1_gaps_pct} per cent of the post-period
  plantation money, from districts above their need share to districts below it. That is the sum of the positive
  gaps. It is the same money distributed by need; not a requirement.

The {top_n} districts with the most need hold {top_need_pct} per cent of it:

{T_top}

*n = {n_districts} districts in C1; these are the {top_n} with the largest N1. The classes of the last two columns rest
on the population of LGD panchayat units only. The gap is the same money distributed by need; not a requirement. The
pre-period years are a snapshot frozen on {stamp_pre}. The index's source and licence are in §6.* {d1_name} has the most
need and under half its need share of the money; {d2_name}, with the second most, has more than its share.

**The sensitivities**, fixed before any result was seen, with the one row that was not:

{T_cmp}

*n is the number of districts in each row. The interval is a `95 %` percentile bootstrap over districts; p is from
shuffling allocation against need. The last three columns do not apply to C12 (intensities) or B1 (a benchmark). The
gap is the same money distributed by need; not a requirement. Every "pre" row uses the four years whose tables are a
snapshot frozen on {stamp_pre}.*

- **The window changes rho little** (C8 to C10): it runs from {win_lo} to {win_hi}.
- **Leaving out the East Coast districts changes rho little** (C7: {c7_rho}; under the other reading of its rule, C7b: {c7b_rho}). C7 is
  there for comparability with the agreement headline of `docs/RESULTS.md` §5, which leaves out the units wholly under
  CoRE Stack's East Coast zone model. The placebo that failed in that zone tested CoRE Stack's model against Hansen.
  It did not test Hansen alone, and nothing here says that Hansen's record is worse in those districts.
- **One year carries much of the post period.** FY2018-19 alone is {fy1819_pct} per cent of the post-period plantation
  money. Without it (C11) rho is {c11_rho} ({c11_lo} to {c11_hi}).
- **Land that panchayat planning can reach** (C2, N1 on LGD-unit land only): rho {c2_rho}.
- **Open forest that could regenerate** (C3, N2): rho {c3_rho} ({c3_lo} to {c3_hi}), an interval that includes zero.
  Post-period plantation money is not shown to follow the stock of standing open forest.
- **The old geography** (C4, C5, C6): money of the years before FY2018-19 gives a higher rho than C1 in each of the
  three, with an interval that overlaps C1's in each, so none is shown to differ from it: {c4_rho} against the loss of 2001 to 2013, {c5_rho} against N1, and {c6_rho} for the narrow forest-named
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
""")

    # ==== 6. marginalisation ========================================================================================================
    sp = W.C(SPLIT)

    def split_rows(cid, grouping):
        out = []
        for _, r_ in sp[(sp.comparison == cid) & (sp.grouping == grouping)].iterrows():
            w_ = {"comparison": cid, "grouping": grouping, "class": r_["class"]}
            out.append([c(cell(SPLIT, "class", **w_), txt), c(cell(SPLIT, "n_districts", **w_), n0), c(cell(SPLIT, "need_share_pct", **w_), dec(1)),
                        c(cell(SPLIT, "allocation_share_pct", **w_), dec(1))])
        return out

    head_s = ["class", "districts", "share of need, %", "share of allocation, %"]
    for cid in ("C1", "C4"):
        for g_ in ("st_class", "adi_tercile", "sc_tercile"):
            table(f"T_{cid}_{g_}", head_s, split_rows(cid, g_))
            same(f"{cid}, {g_}: the districts of the classes, and the districts", sp[(sp.comparison == cid) & (sp.grouping == g_)].n_districts.sum(), n_d.v)
    labels = P["steps"]["08_build_gap_districts"]["st_classes"]["labels"]
    top_st = dict(comparison="C1", grouping="st_class")
    st_need, st_all, st_n = cell(SPLIT, "need_share_pct", **top_st, **{"class": labels[-1]}), cell(SPLIT, "allocation_share_pct", **top_st, **{"class": labels[-1]}), cell(SPLIT, "n_districts", **top_st, **{"class": labels[-1]})
    show("st_top_label", V(labels[-1], PROV, "key `steps` → `08_build_gap_districts` → `st_classes` → `labels`: the last"), txt)
    show("st_top_need", st_need, dec(1)); show("st_top_alloc", st_all, dec(1)); show("st_top_n", st_n, n0)
    lo_adi = dict(comparison="C1", grouping="adi_tercile")
    adi_lab = sp[(sp.comparison == "C1") & (sp.grouping == "adi_tercile")]["class"].iloc[0]
    a_need, a_all = cell(SPLIT, "need_share_pct", **lo_adi, **{"class": adi_lab}), cell(SPLIT, "allocation_share_pct", **lo_adi, **{"class": adi_lab})
    show("adi_low_label", V(adi_lab, SPLIT, "C1, `adi_tercile`: the first class"), txt)
    show("adi_low_need", a_need, dec(1)); show("adi_low_alloc", a_all, dec(1))
    hold(st_need.v > 50 and st_all.v > 50 and st_need.v > st_all.v,
         "in C1 the districts of the highest Scheduled Tribe class hold more than half the need and more than half the money, and a larger share of the need than of the money")
    hold(a_need.v > 50 and a_all.v > 50 and a_need.v > a_all.v and "lowest" in adi_lab,
         "in C1 the ten districts lowest on the development index hold more than half the need and more than half the money, and a larger share of the need than of the money")
    st4_need, st4_all = cell(SPLIT, "need_share_pct", comparison="C4", grouping="st_class", **{"class": labels[-1]}), cell(SPLIT, "allocation_share_pct", comparison="C4", grouping="st_class", **{"class": labels[-1]})
    show("st4_need", st4_need, dec(1)); show("st4_alloc", st4_all, dec(1))
    c4_word = "smaller" if st4_all.v < st4_need.v else "larger"
    hold((st4_all.v < st4_need.v) == (c4_word == "smaller"), f"in C4 the districts of the highest Scheduled Tribe class have a {c4_word} share of the pre-period money than of the earlier loss")

    DOC.append("""
## 6. The comparison split by marginalisation

The classes below **split** the comparison. They are not weights, and no score is made of them. Each rests on the
Census of 2011 for LGD panchayat units only: **outside-village land has no census rows**, and {n1_out_pct} per cent of
N1 lies on it. A district's class describes the people the census counted there, not the land where its forest was lost.

**C1: need (N1 of the years 2018 to 2025) and post-period plantation money.**

By Scheduled Tribe share of the district's population:

{T_C1_st_class}

By tercile of the development index of 2011 (a higher index is a more developed place):

{T_C1_adi_tercile}

By tercile of Scheduled Caste share:

{T_C1_sc_tercile}

*n = {n_districts} districts in each of the three tables; a share is the sum of the shares of the class's districts, and
each column adds to a hundred. The development index: {adi_source}*

The {st_top_n} districts in the class "{st_top_label}" hold {st_top_need} per cent of the need and received
{st_top_alloc} per cent of the post-period plantation money. The ten districts in the "{adi_low_label}" hold
{adi_low_need} per cent of the need and received {adi_low_alloc} per cent of the money. In both the larger part of the
money went where the larger part of the need is, and the share of the money is the smaller of the two.

**C4: forest loss of 2001 to 2013 and pre-period plantation money** (the four years frozen on {stamp_pre}).

{T_C4_st_class}

{T_C4_adi_tercile}

{T_C4_sc_tercile}

*n = {n_districts} districts in each table. The development index: {adi_source}*

In the years before FY2018-19 the districts of the class "{st_top_label}" held {st4_need} per cent of the earlier loss
and {st4_alloc} per cent of the plantation money: a """ + c4_word + """ share of the money than of the loss.
""")

    # ==== 7. what more ===============================================================================================================
    def more(col, **kw):
        return cell(MORE, col, district="state", **kw)

    r1 = show("more_r1", more("n1_ha_where_r_below_1"), n0)
    r05 = show("more_r05", more("n1_ha_where_r_below_0_5"), n0)
    calc("more_r1_pct", 100 * r1.v / n1.v, dec(0), "N1 in districts with `r` below one ÷ N1 × 100", [r1, n1])
    same("N1 in districts with r below 0.5: in the table of what more is needed and, as a share, in the comparison table", 100 * r05.v / n1.v, c1b.v, 0.001)
    w16, w25 = show("works16", more("works_per_1000_ha_n1_fy2016_17"), n0), show("works25", more("works_per_1000_ha_n1_fy2025_26"), n0)
    show("works16_n", more("plantation_works_fy2016_17"), n0); show("works25_n", more("plantation_works_fy2025_26"), n0)
    hold(w25.v < w16.v / 10, "plantation works per thousand hectares of N1 in FY2025-26 are less than a tenth of those of FY2016-17")
    show("vgpp_reason", more("cost_blank_because"), txt)
    hold(W.C(MORE).cost_at_vgpp_rate_inr.isna().all() and W.C(MORE).cost_blank_because.notna().all(), "the cost at the VGPP rate is blank in every row, with its reason")
    scale = show("scale_lakh", more("scale_of_the_fall_lakh"), lakh)
    show("scale_crore", scale, crore_of_lakh)
    actual = show("post_actual", more("plantation_post_actual_lakh"), lakh)
    same("post-period plantation money, in the table of what more is needed and in the table of districts", actual.v, post.v, 0.005)
    same("the pre-period plantation share applied to the post-period total, as tabled and as worked out here from the two periods' sums", scale.v, pre.v / all_pre.v * all_post.v, 0.005)
    show("scale_label", more("scale_is"), txt)

    DOC.append("""
## 7. What more is needed

Three answers, none of them in rupees of need. All are for C1.

- **In hectares.** {more_r1} ha of N1, {more_r1_pct} per cent of it, lie in districts whose share of the post-period
  plantation money is below their share of the need (`r` below `1`); {more_r05} ha lie in districts where it is under
  half (`r` below `0.5`).
- **As an intensity of works.** For every `1,000 ha` of N1 the state report counts {works16} plantation works, ongoing
  plus completed, in FY2016-17 ({works16_n} works) and {works25} in FY2025-26 ({works25_n} works). This is an intensity,
  not a requirement: works have no standard size. The same figure is given for each district.
- **As the same money distributed by need** (§5): {c1_gaps} lakh rupees would change districts. It is the same money
  distributed by need; not a requirement.

**The cost at the VGPP rate is blank.** The column is in the table and is empty in every row, with the reason:
"{vgpp_reason}". No rate was put in its place.

**For scale, not need.** Had plantation kept the share of all expenditure it had in the pre period, the post-period
total would have carried {scale_lakh} lakh rupees of it (₹{scale_crore} crore), against the {post_actual} lakh actually
spent. That figure is {scale_label}.
""")

    # ==== 8. the panel ===============================================================================================================
    pm = W.C(PM)

    def pmc(i_, col, term=None, blank_ok=False):
        w_ = {"id": i_} if term is None else {"id": i_, "term": term}
        return cell(PM, col, blank_ok=blank_ok, **w_)

    main_term = {r_.id: r_.term for _, r_ in pm.iterrows() if not str(r_.term).endswith("_x_post")}
    p1b, p1lo, p1hi, p1p = pmc("P1", "coefficient"), pmc("P1", "wcb_ci95_lo"), pmc("P1", "wcb_ci95_hi"), pmc("P1", "wcb_p")
    show("p1_b", p1b, dec(3)); show("p1_lo", p1lo, dec(3)); show("p1_hi", p1hi, dec(3)); show("p1_p", p1p, dec(3))
    show("p1_se", pmc("P1", "se_cr1"), dec(3)); show("p1_B", pmc("P1", "wcb_B"), n0); show("p_B", pmc("P2", "wcb_B"), n0)
    show("p1_clusters", pmc("P1", "clusters"), n0)
    show("p1_unit", pmc("P1", "coefficient_unit"), txt)
    hold(p1lo.v < 0 < p1hi.v and p1p.v > 0.05, "P1's interval includes zero")
    rows_pm = []
    for _, r_ in pm.iterrows():
        w_ = {"id": r_.id, "term": r_.term}
        tag = r_.id + (" (the headline)" if r_.headline == "yes" else "") + (", the product with the post period" if str(r_.term).endswith("_x_post") else "")
        rows_pm.append([tag, c(cell(PM, "outcome", **w_), txt), c(cell(PM, "regressor_unit", **w_), txt), c(cell(PM, "n", **w_), n0), c(cell(PM, "coefficient", **w_), dec(3)),
                        c(cell(PM, "se_cr1", **w_), dec(3)), W.span(cell(PM, "coefficient", **w_), cell(PM, "wcb_ci95_lo", blank_ok=True, **w_), cell(PM, "wcb_ci95_hi", blank_ok=True, **w_), dec(3)),
                        c(cell(PM, "wcb_p", **w_), dec(3)), c(cell(PM, "wcb_p_rises_again_lo", **w_), txt), c(cell(PM, "wcb_p_rises_again_hi", **w_), txt),
                        c(cell(PM, "wcb_p_at_bracket_end_lo", **w_), dec(3)), c(cell(PM, "wcb_p_at_bracket_end_hi", **w_), dec(3))])
    table("T_panel", ["model", "outcome", "a unit of the regressor", "district-years", "coefficient", "CR1 standard error (for reference)", "coefficient (wild-bootstrap interval)",
                      "wild-bootstrap p", "p climbs back, lower side", "p climbs back, upper side", "p at the lower end of the bracket", "p at the upper end of the bracket"], rows_pm)
    hold(all((r_.wcb_ci95_lo < 0 < r_.wcb_ci95_hi) for _, r_ in pm.iterrows()) and (pm.wcb_p > 0.05).all(), "in every model of the panel the interval of every reported term includes zero")
    hold((pm.wcb_unbounded_lo == "no").all() and (pm.wcb_unbounded_hi == "no").all(), "every interval of the panel is bounded on both sides")
    rises = pm[(pm.wcb_p_rises_again_lo == "yes") | (pm.wcb_p_rises_again_hi == "yes")]
    show("n_rise", V(len(rises), PM, "rows with `wcb_p_rises_again_lo` or `_hi` yes"), n0)
    show("rise_ids", V(", ".join(sorted(set(rises.id))) or "none", PM, "the `id` of those rows"), txt)
    show("n_terms", V(len(pm), PM, "its rows"), n0)
    end_max = max(float(pm.wcb_p_at_bracket_end_lo.max()), float(pm.wcb_p_at_bracket_end_hi.max()))
    near = pm[(pm.wcb_p_at_bracket_end_lo > 0.04) | (pm.wcb_p_at_bracket_end_hi > 0.04)]
    show("end_max", V(end_max, PM, "the largest of `wcb_p_at_bracket_end_lo` and `_hi`"), dec(3))
    show("near_ids", V(", ".join(sorted(set(near.id))) or "none", PM, "the `id` of the rows where p at an end of the bracket is above 0.04"), txt)
    hold(end_max < 0.05, "at the outer end of every bracket p is below the level, so every side has a crossing")
    show("p1_end_lo", pmc("P1", "wcb_p_at_bracket_end_lo"), dec(3))
    p2b = pmc("P2", "coefficient"); show("p2_b", p2b, dec(3)); show("p2_lo", pmc("P2", "wcb_ci95_lo"), dec(3)); show("p2_hi", pmc("P2", "wcb_ci95_hi"), dec(3))
    sign_word = "the opposite sign" if p1b.v * p2b.v < 0 else "the same sign"
    hold((p1b.v * p2b.v < 0) == (sign_word == "the opposite sign"), f"P2's coefficient has {sign_word} to P1's")

    DOC.append("""
## 8. The district-year panel

{n_districts} districts by {n_fy} financial years of R6.20 make {n_panel} rows (`50_gap/district_year_panel.csv`); the
part year FY2026-27 is flagged and is in no model, which leaves {n_dy} district-years. For each row: plantation, NRM,
water and all expenditure; plantation's share; plantation works; the report's stamp; forest loss of the calendar year
before and of the same year, for both bands and for the dense band alone; and the forest standing at the start of the
year before.

**What a coefficient asks.** Whether, within a district and within a period, years after more forest loss had more
plantation spending than that district's other years, beyond what all districts had in that year. It is not an
effect. Plantation is the scheme's label, and it is not specific to forest.

**Why the headline gives each district its own level in each period.** Plantation's share of district expenditure
varies far more before FY2018-19 than after: its standard deviation across district-years is {sd_pre} percentage
points before and {sd_post} after. A model with only district and year fixed effects is therefore identified largely
by how far each district fell in 2018, set against loss that rose after 2018 (the state's loss in the year before,
which is the regressor, averages {lag_pre} ha over the pre period's years and {lag_post} ha over the post period's);
it can show a relation that does not hold from year to year. P1 has district-by-period and financial-year fixed effects. P2, with plain district fixed
effects, is given for comparison and is read with that caveat.

**P1.** The coefficient is {p1_b} ({p1_unit}; CR1 standard error {p1_se}, for reference). Its interval is {p1_lo} to
{p1_hi} and it includes zero (p {p1_p}).
Within a district and a period, years after more forest loss are not shown to have had more, or less, plantation
spending. P2's coefficient, {p2_b} ({p2_lo} to {p2_hi}), has """ + sign_word + """.

{T_panel}

*n = {n_dy} district-years in every row, in {p1_clusters} clusters, the districts. The CR1 standard error is for
reference only. The interval that counts is that of a restricted wild cluster bootstrap with Webb's weights and the
null imposed (the `wildboottest` package; {p1_B} draws for P1 and {p_B} for the others), found by testing each value of
the coefficient in turn: the `95 %` interval is the set of values not rejected at `0.05`. P3's coefficient is in asinh
of lakh rupees, not in percentage points. The pre-period years are a snapshot frozen on {stamp_pre}.*

**How the bootstrap's p behaved, which the last four columns record.** As the tested value moves away from the
estimate, the p of this bootstrap does not always go on falling: with {p1_clusters} clusters of unequal weight it can
settle at a level, or climb back before it falls. The instruction's rule was applied as written: the bracket was
widened until p was below `0.05` at both ends, and the outermost crossing is the end of the interval. In {n_rise} of the
{n_terms} rows p climbed back by more than `0.01` on one side ({rise_ids}). At the outer end of a bracket p was at most
{end_max}; where it stands close to `0.05` there ({near_ids}), that end of the interval is weakly determined: a
different set of draws could put it elsewhere, or nowhere. For P1 the lower side settles at {p1_end_lo}. Every grid of p
values is kept in `50_gap/panel_models_wcb_grids.json`.
""")

    # ==== 9. the unit history ========================================================================================================
    um = W.C(UM)

    def umc(i_, col, blank_ok=False):
        return cell(UM, col, blank_ok=blank_ok, id=i_)

    h1b, h1lo, h1hi, h1p = umc("H1", "coefficient"), umc("H1", "wcb_ci95_lo"), umc("H1", "wcb_ci95_hi"), umc("H1", "wcb_p")
    show("h1_b", h1b, dec(2)); show("h1_lo", h1lo, dec(2)); show("h1_hi", h1hi, dec(2)); show("h1_p", h1p, dec(3))
    h1n = show("h1_n", umc("H1", "n_units"), n0); show("h1_exp", umc("H1", "n_exposed"), n0); show("h1_d", umc("H1", "n_districts"), n0)
    show("h1_B", umc("H1", "wcb_B"), n0); show("h_B", umc("H2", "wcb_B"), n0)
    show("h1_unit", umc("H1", "coefficient_unit"), txt)
    hold(h1lo.v < 0 < h1hi.v and h1p.v > 0.05, "H1's interval includes zero")
    same("units in H1, in the table of models and counted in the unit table", h1n.v, count(UH, "rows with `in_h1` 1", lambda t: t.in_h1 == 1).v)
    same("units exposed in H1, in the table of models and counted in the unit table", umc("H1", "n_exposed").v, count(UH, "rows with `in_h1` 1 and `e1_any_forest_named` 1", lambda t: (t.in_h1 == 1) & (t.e1_any_forest_named == 1)).v)
    uh = W.C(UH)
    h1s = uh[uh.in_h1 == 1]
    show("h1_out", V(int((h1s.outside_village == 1).sum()), UH, "rows with `in_h1` 1 and `outside_village` 1"), n0)
    show("h1_mean", V(float(h1s.forest_loss_share_pct.mean()), UH, "the mean of `forest_loss_share_pct` over the rows with `in_h1` 1"), dec(2))
    show("h1_median", V(float(h1s.forest_loss_share_pct.median()), UH, "the median of the same"), dec(2))
    show("near_floor", V(int(((uh.forest_at_window_start_ha >= 99.995) & (uh.forest_at_window_start_ha < 100)).sum() + ((uh.forest_at_window_start_ha >= 49.995) & (uh.forest_at_window_start_ha < 50)).sum()
                             + ((uh.forest_at_window_start_ha >= 9.995) & (uh.forest_at_window_start_ha < 10)).sum()), UH, "rows whose `forest_at_window_start_ha` lies in the last half hundredth below one of the three floors"), n0)
    rows_um = []
    for _, r_ in um.iterrows():
        tag = r_.id + (" (the headline)" if r_.headline == "yes" else "")
        rows_um.append([tag, c(umc(r_.id, "outcome"), txt), c(umc(r_.id, "exposure"), txt), c(umc(r_.id, "sample"), txt), c(umc(r_.id, "n_units"), n0), c(umc(r_.id, "n_exposed"), n0),
                        c(umc(r_.id, "n_districts"), n0), c(umc(r_.id, "coefficient"), dec(3)), c(umc(r_.id, "se_cr1"), dec(3)),
                        W.span(umc(r_.id, "coefficient"), umc(r_.id, "wcb_ci95_lo", True), umc(r_.id, "wcb_ci95_hi", True), dec(3)), c(umc(r_.id, "wcb_p"), dec(3)),
                        c(umc(r_.id, "wcb_p_at_bracket_end_lo"), dec(3)), c(umc(r_.id, "wcb_p_at_bracket_end_hi"), dec(3))])
    table("T_units", ["model", "outcome", "exposure", "sample", "units", "exposed", "districts", "coefficient", "CR1 standard error (for reference)",
                      "coefficient (wild-bootstrap interval)", "wild-bootstrap p", "p at the lower end of the bracket", "p at the upper end of the bracket"], rows_um)
    inc0 = [r_.id for _, r_ in um.iterrows() if r_.wcb_ci95_lo < 0 < r_.wcb_ci95_hi]
    exc0 = [r_.id for _, r_ in um.iterrows() if not (r_.wcb_ci95_lo < 0 < r_.wcb_ci95_hi)]
    show("h_inc0", V(len(inc0), UM, "rows whose interval includes zero"), n0); show("h_all", V(len(um), UM, "its rows"), n0)
    hold((um.wcb_unbounded_lo == "no").all() and (um.wcb_unbounded_hi == "no").all(), "every interval of the unit models is bounded on both sides")
    h_end = max(float(um.wcb_p_at_bracket_end_lo.max()), float(um.wcb_p_at_bracket_end_hi.max()))
    show("h_end_max", V(h_end, UM, "the largest of `wcb_p_at_bracket_end_lo` and `_hi`"), dec(3))
    hold(h_end < 0.05, "at the outer end of every bracket of the unit models p is below the level")
    h_rise = um[(um.wcb_p_rises_again_lo == "yes") | (um.wcb_p_rises_again_hi == "yes")]
    show("h_rise", V(", ".join(h_rise.id) or "none", UM, "the `id` of the rows with `wcb_p_rises_again_lo` or `_hi` yes"), txt)
    show("h9_n", h9, n0)
    hold("If the owner reads his condition" in " ".join(W.use(RUN_LOG).read_text(encoding="utf-8").split()) and "to the letter, H9 is the row to drop" in " ".join(W.use(RUN_LOG).read_text(encoding="utf-8").split()),
         "the run log's note on Phase 4 says that, if the owner's condition is read to the letter, H9 is the row to drop")
    hold(cell(UM, "outcome", id="H9").v != cell(UM, "outcome", id="H1").v and "downward" in cell(UM, "outcome", id="H9").v,
         "H9's outcome is not H1's: it is the downward share")
    if not exc0:
        exc_sentence = "No sensitivity gives an interval that excludes zero."
    elif len(exc0) == 1:
        exc_sentence = f"In {exc0[0]} the interval does not include zero; it is one of several sensitivities, read beside the headline and not in its place."
    else:
        exc_sentence = "In " + ", ".join(exc0) + " the intervals do not include zero; each is one of several sensitivities, read beside the headline and not in its place."
    hold("H1" not in exc0, "the models whose interval excludes zero are sensitivities: H1, the headline, is not among them")
    hold(bool(exc0) == exc_sentence.startswith("In "), "the sentence on which unit models have an interval that excludes zero follows the table")

    DOC.append("""
## 9. The historical companion: units within districts

**The question.** In the same district, did units that had forest-named works by FY2017-18 lose a different share of
their forest in the years 2018 to 2025 than units that had none, given their forest and their earlier loss?

The exposure comes before the outcome. **Planners sited the works, so this is an association, and selection is
likely**: works may have gone to places already losing forest, or to places easy to reach. The control for earlier
loss speaks to part of that, not all. And a unit is a shape on a map, not the panchayat that recorded a work
(`README.md` §5.8): where a work was geotagged is not always where its panchayat lies.

**The sample of the headline** is every unit with `100 ha` or more of forest at the start of 2018: {h1_n} units in
{h1_d} districts, {h1_out} of them outside-village units, {h1_exp} with any forest-named expenditure on works started
by FY2017-18. The floor is set on forest at the start of the window, not on the land the agreement test compares
(§3). Their mean loss in the window is {h1_mean} per cent of that forest and the median {h1_median}. No unit lies in
the last half hundredth of a hectare below a floor ({near_floor}), so the floor read on the figure as printed gives
the same samples.

**H1.** Outcome: the share of forest at the start of 2018 lost in the window, in per cent. Exposure: any forest-named
expenditure on works started by FY2017-18. Controls: the logarithm of forest at the start, the dense share of that
forest, the share of the forest of 2000 lost in 2001 to 2017, whether the unit is outside-village land, and a fixed
effect for every district. The coefficient is {h1_b} ({h1_unit}), with an interval of {h1_lo} to {h1_hi} that includes
zero (p {h1_p}). Units with such works are not shown to have lost a different share of their forest than the other
units of their district.

{T_units}

*n is the number of units in each row; clusters are the districts in the row's sample. The CR1 standard error is for
reference only; the interval is that of the restricted wild cluster bootstrap described in §8 ({h1_B} draws for H1,
{h_B} for the others). H6's coefficient is per unit of asinh of rupees per hectare, not a percentage; H8 is a linear
probability model, its coefficient a difference in probability; H9's outcome is CoRE Stack's downward share, degradation
over degradation plus improvement, never the degradation class alone, formed for {h9_n} units of H1's sample in which
the two classes are not both zero. H4 leaves out the units of the districts C7 leaves out, for comparability with the
agreement headline. H5 is LGD panchayat units only.*

The interval includes zero in {h_inc0} of the {h_all} models. """ + exc_sentence + """

**H9 is a lead, not a finding.** The owner keeps it as a sensitivity row (§2). It is to be read with four things.

- **It uses a different measure from H1's.** H1's outcome is Hansen's loss. H9's is CoRE Stack's downward share: the
  degradation class over degradation plus improvement.
- **The caveats on CoRE Stack's classes apply** (`docs/RESULTS.md` §4). They rest on classifiers their makers report
  as right about two times in three. And they compare the years around 2016 to 2019 with those around 2022 to 2025,
  so the first of the two periods overlaps the years in which the works were started: the outcome does not come
  cleanly after the exposure.
- **Its share was formed in this run, from two classes.** No table of stage 1 carries the downward share for each
  unit. It was made here from the hectares of the degradation class and of the improvement class, for the {h9_n}
  units of H1's sample in which the two are not both zero (§3).
- **A strict reading of the owner's instruction drops it.** The instruction said to run H9 only if stage 1 carries
  the downward share for each unit, and the run's own note says that, read to the letter, H9 is the row to drop
  (`docs/stage4_run_log.md`, in its notes on the unit history).

A unit with works and a lower downward share is described by that sentence; nothing is shown about what the works
did. At the outer end of a bracket p was at most {h_end_max}; rows in which p climbed back on a side: {h_rise}. The
grids are in `50_gap/unit_history_models_wcb_grids.json`.
""")

    # ==== 10. forest rights ==========================================================================================================
    fr = W.C(FRA)
    t_tit = show("fra_titles", agg(FRA, "`community_titles_distributed` summed", lambda t: t.community_titles_distributed.sum()), n0)
    t_ext = show("fra_extent", agg(FRA, "`community_extent_ha` summed", lambda t: t.community_extent_ha.sum()), n0)
    none_ = fr[fr.community_titles_distributed == 0]
    show("fra_none_n", V(len(none_), FRA, "rows with `community_titles_distributed` 0"), n0)
    show("fra_none", V(", ".join(none_.district_name), FRA, "the `district_name` of those rows"), txt)
    st_row, mo_row, df_row = fr2 = [r_ for _, r_ in W.C(FR2).iterrows()]
    hold(st_row.report.startswith("Odisha state report") and mo_row.report.startswith("Ministry of Tribal Affairs") and df_row.report.startswith("difference"), "the table of the two reports has the state's row, the national report's row and their difference, in that order")
    show("mota_titles", cell(FR2, "community_titles_distributed", report=mo_row.report), n0); show("mota_extent", cell(FR2, "community_extent_ha", report=mo_row.report), n0)
    show("diff_titles", cell(FR2, "community_titles_distributed", report=df_row.report), n0); show("diff_extent", cell(FR2, "community_extent_ha", report=df_row.report), n0)
    show("diff_pct", cell(FR2, "extent_difference_pct_of_state", report=df_row.report), dec(2))
    same("community titles of the state's report, in the table of districts and in the table of the two reports", t_tit.v, st_row.community_titles_distributed)
    same("community extent of the state's report, in the table of districts and in the table of the two reports", t_ext.v, st_row.community_extent_ha, 0.001)
    hold(df_row.community_titles_distributed > 0 and df_row.community_extent_ha > 0, "the state's report gives more community titles and more community extent than the national report of the same date")
    over = fr[fr.community_extent_pct_of_forest_2000 > 100]
    show("fra_over_n", V(len(over), FRA, "rows with `community_extent_pct_of_forest_2000` above 100"), n0)
    show("fra_over", V(", ".join(over.district_name), FRA, "the `district_name` of those rows"), txt)
    fra_over_word = "district" if len(over) == 1 else "districts"
    hold(len(over) >= 1 and (len(over) == 1) == (fra_over_word == "district"), f"the ratio is above a hundred in at least one district, and the sentence says '{fra_over_word}'")
    show("fra_label", V(str(fr.extent_is.iloc[0]), FRA, "column `extent_is`"), txt)

    def frs(i_, col):
        return cell(FRS, col, id=i_)

    for i_ in ("R1", "R2"):
        show(f"{i_.lower()}_rho", frs(i_, "rho"), dec(2)); show(f"{i_.lower()}_lo", frs(i_, "ci95_lo"), dec(2)); show(f"{i_.lower()}_hi", frs(i_, "ci95_hi"), dec(2)); show(f"{i_.lower()}_p", frs(i_, "p_permutation"), dec(3))
    r1_word = "lies above zero" if frs("R1", "ci95_lo").v > 0 else "includes zero"
    hold((frs("R1", "ci95_lo").v > 0) == (r1_word == "lies above zero"), f"R1's interval {r1_word}")
    hold(frs("R2", "ci95_lo").v < 0 < frs("R2", "ci95_hi").v, "R2's interval includes zero")
    r_ef = show("r_ext_forest", agg(FRA, "Spearman's rank correlation of `community_extent_ha` with `forest_2000_ha` over its rows", lambda t: float(t.community_extent_ha.corr(t.forest_2000_ha, method="spearman"))), dec(2))
    r_nf_v = show("r_n1_forest", agg(FRA, "Spearman's rank correlation of `n1_ha_2018_2025` with `forest_2000_ha` over its rows", lambda t: float(t.n1_ha_2018_2025.corr(t.forest_2000_ha, method="spearman"))), dec(2))
    r_nf = r_nf_v.v
    hold(frs("R1", "ci95_lo").v > 0 and frs("R2", "rho").v < frs("R1", "rho").v and r_ef.v > 0.4 and r_ef.v > frs("R2", "rho").v and r_nf > 0.4,
         "R1's interval lies above zero while R2's includes it; the rank correlations of community extent and of N1 with the forest of 2000 are each above four tenths, and the first is above R2's rho: what R1 shows is carried by how much forest a district has")
    show("fv_sha", V(key(FV, "sha256").v[:16], FV, "key `sha256`, its first sixteen characters"), txt)
    show("fv_bytes", key(FV, "bytes"), n0)
    show("fv_ppi", V("/".join(key(FV, "image_pixels_per_inch").v), FV, "key `image_pixels_per_inch`"), txt)
    show("fv_producer", V(f"{key(FV, 'producer').v}, in {key(FV, 'creator').v}", FV, "keys `producer` and `creator`"), txt)
    show("fv_bad", V("; ".join(key(FV, "summary_rows_that_do_not").v), FV, "key `summary_rows_that_do_not`: the lines as read"), txt)
    show("fv_nd", key(FV, "districts_in_the_file"), n0)
    show("fv_note", V(key(FV, "note_from_one_page_read_by_eye").v, FV, "key `note_from_one_page_read_by_eye`"), txt)
    hold(key(FV, "summary_rows_read").v - key(FV, "summary_rows_that_add_up").v == len(key(FV, "summary_rows_that_do_not").v) == 1 and key(FV, "printed_total_row_read").v == 0,
         "on the summary page of the forest villages PDF, as its layer reads it, one row does not add up and no total row can be read")
    table("T_fv", ["part of check (a)", "what it asks of the layer", "holds in", "of"],
          [[c(V(x_["part"], FV, "key `check_a` → `parts` → `part`"), txt), c(V(x_["asks"], FV, f"key `check_a` → `parts` → the part `{x_['part']}` → `asks`"), txt),
            c(V(x_["holds_in"], FV, f"key `check_a` → `parts` → the part `{x_['part']}` → `holds_in`"), n0),
            c(V(x_["of"], FV, f"key `check_a` → `parts` → the part `{x_['part']}` → `of`"), n0)] for x_ in fv_a["parts"]])

    DOC.append("""
## 10. Forest rights, at the level the data allow

**By district.** The state's monthly progress report on the Forest Rights Act, as on 31 December 2025, joined on the
census district code: {fra_titles} community titles distributed (Scheduled Tribes and other traditional forest
dwellers together) over {fra_extent} ha. {fra_none_n} districts have distributed none: {fra_none}.

For each district the table gives the community extent as a per cent of the district's forest of 2000 (both bands).
That figure is "{fra_label}". Titles are not mapped anywhere in this repository, and the report's "community" is
community rights and community forest resource rights together. In {fra_over_n} """ + fra_over_word + """ ({fra_over}) the ratio is
above a hundred, which a share of forest could not be.

Two rank correlations over the {n_districts} districts, computed as in §5:

- **R1**, community extent against N1 of the years 2018 to 2025: rho {r1_rho} ({r1_lo} to {r1_hi}; p {r1_p}), an
  interval that """ + r1_word + """. Both are larger in districts with more forest (below).
- **R2**, community extent per hectare of the forest of 2000 against N1 per hectare of forest at the start of the
  window: rho {r2_rho} ({r2_lo} to {r2_hi}; p {r2_p}), an interval that includes zero. With size taken out, districts
  where more forest land is under a community title are not shown to be those that lost more of their forest, or less.

**The two are read together.** R1's rank correlation does not survive per hectare: R2's interval includes zero. What
that leaves is size. Community-title extent tracks how much forest a district has: over the same {n_districts}
districts its rank correlation with the forest of the year 2000 is {r_ext_forest}, and N1's is {r_n1_forest} (both
worked out by this script from the table of districts; no interval was computed for either, and the verifier does
not check them). So R1 says that districts with more forest tend to have both more titled land and more loss, and
nothing about titles and loss beyond that.

**The two reports of the same date disagree.** This document cites the state's figures. Odisha's row of the national
report of the Ministry of Tribal Affairs, as on the same day, gives {mota_titles} community titles and {mota_extent} ha.
The state's report has {diff_titles} more titles and {diff_extent} ha more, {diff_pct} per cent of its own figure.

**The forest villages list.** The manifest has listed the ST & SC Development Department's "List of Forest Villages,
Old Habitations or Settlements & Unsurveyed Villages" since 4 October 2026, and it had not been opened. It was already
on disk (`00_raw/01_cfr_fra/`, {fv_bytes} bytes, `sha256` beginning `{fv_sha}`) and is registered with a manifest row
of its own that gives its exact size and hash; the row that lists its address is as it was. It is a scan: {fv_pages}
pages, each one image at {fv_ppi} pixels per inch. The only text in the file is a layer made by someone else's
character recognition ({fv_producer}).

*The owner's rule for that layer (10 October 2026).* It is unverified, and is used only if two checks hold. (a) The
district counts parsed from it equal every total and running serial number the file prints, exactly. (b) At least five
pages chosen at random, rendered upright and read by a reader, match the parsed rows row for row. If either fails,
the step records the page count, the layer and which check failed, and stops.

**Check (a) fails, in every part this stage made of it.** The layer gives {fv_nd} districts, each a page of totals
followed by a list of villages with running serial numbers, and before them a summary page with a row for each.

{T_fv}

*The layer is read as `pdftotext` gives it, a page at a time; the rule for what counts as a row, a district's page
and a serial number is in `scripts/08_build_gap_rights.py`, and the table of districts as the layer reads them is
`50_gap/forest_villages_districts_as_the_layer_reads_them.csv`. In one district the list is numbered block by block,
which this stage's rule for serial numbers does not follow.*

On the summary page {fv_ok} of {fv_rows} rows add up and one does not ("{fv_bad}"); no total row can be read from the
layer. A note recorded with the check, which is one reader's and no part of either check: "{fv_note}"

**Check (b) was not run**: the rule stops the step at the first check that fails. So **no count was taken from the
file, and none is in the table of districts**. No character recognition was run in this stage, and the list is not
matched to units.
""")

    # ==== 11. the need read against the Forest Survey's own figures (Phase 5b) =======================================================
    fs = W.C(FSI)

    def fsc(i_, col):
        return cell(FSS, col, id=i_)

    for i_ in ("a", "b", "c", "d"):
        show(f"f{i_}_rho", fsc(i_, "rho"), dec(2)); show(f"f{i_}_lo", fsc(i_, "ci95_lo"), dec(2)); show(f"f{i_}_hi", fsc(i_, "ci95_hi"), dec(2))
        show(f"f{i_}_p", fsc(i_, "p_permutation"), dec(5) if i_ in ("b", "d") else dec(3))
    hold(all(fsc(i_, "ci95_lo").v < 0 < fsc(i_, "ci95_hi").v for i_ in ("a", "c")),
         "the interval of rho for N1 against the Forest Survey's change in forest cover includes zero, with size left in (a) and with size taken out of both sides (c)")
    hold(all(fsc(i_, "ci95_lo").v > 0 for i_ in ("b", "d")) and fsc("d", "rho").v < fsc("b", "rho").v,
         "the interval of rho for N1 against the Forest Survey's scrub lies above zero, with size left in (b) and with size taken out of both sides (d), and rho is lower with size taken out")
    hold(all(fsc(i_, "size_free").v == w_ for i_, w_ in (("a", "no"), ("b", "no"), ("c", "yes"), ("d", "yes"))) and all(fsc(i_, "n_districts").v == n_d.v for i_ in ("a", "b", "c", "d")),
         "of the four rank correlations with the Forest Survey's figures, (a) and (b) leave size in and (c) and (d) take it out of both sides, and each is over all the districts")
    table("T_fsi_rho", ["", "what is set against what", "Spearman's rho (interval)", "permutation p", "size taken out of both sides"],
          [[c(fsc(i_, "id"), lambda x: f"({x})"), c(fsc(i_, "what"), txt), W.span(fsc(i_, "rho"), fsc(i_, "ci95_lo"), fsc(i_, "ci95_hi")), c(fsc(i_, "p_permutation"), dec(5)), c(fsc(i_, "size_free"), txt)]
           for i_ in ("a", "b", "c", "d")])
    fs_sorted = fs.sort_values("n1_ha_2018_2025", ascending=False)
    fs_top = fs_sorted.head(8)
    rows_fsi = []
    for _, r_ in fs_top.iterrows():
        w_ = dict(pc11_district_code=int(r_.pc11_district_code))
        rows_fsi.append([c(cell(FSI, "district_name", **w_), txt), c(cell(FSI, "n1_ha_2018_2025", **w_), n0), c(cell(FSI, "n1_km2_2018_2025", **w_), dec(1)),
                         c(cell(FSI, "n1_per_100_ha_of_forest_at_window_start", **w_), dec(2)), c(cell(FSI, "fsi_forest_cover_km2", **w_), n0),
                         c(cell(FSI, "fsi_change_wrt_2021_km2", **w_), dec(2)), c(cell(FSI, "fsi_change_pct_of_forest_cover", **w_), dec(2)),
                         c(cell(FSI, "fsi_scrub_km2", **w_), n0), c(cell(FSI, "fsi_scrub_pct_of_forest_cover", **w_), dec(1))])
    table("T_fsi", ["district", "N1, ha", "N1, km²", "N1 per `100 ha` of forest at the start of the window", "Forest Survey: forest cover, km²", "Forest Survey: change with respect to its earlier assessment, km²",
                    "that change, % of its forest cover", "Forest Survey: scrub, km²", "scrub, % of its forest cover"], rows_fsi)
    show("fsi_top_n", V(len(fs_top), FSI, "the rows with the largest `n1_ha_2018_2025`: how many are tabled"), n0)
    top5 = fs_sorted.head(5)
    show("top5_names", V(", ".join(top5.district_name), FSI, "the `district_name` of the five rows with the largest `n1_ha_2018_2025`"), txt)
    show("top5_n", V(len(top5), FSI, "those rows: how many"), n0)
    n1_all = agg(FSI, "`n1_ha_2018_2025` summed", lambda t: t.n1_ha_2018_2025.sum())
    n1_top5 = V(float(top5.n1_ha_2018_2025.sum()), FSI, "`n1_ha_2018_2025` of those five rows, summed")
    calc("top5_pct", 100 * n1_top5.v / n1_all.v, dec(0), "N1 of those five districts ÷ N1 of the state × 100", [n1_top5, n1_all])
    same("N1 of the state, in the table of districts and in the table of the Forest Survey's figures", n1.v, n1_all.v, 0.001)
    hold(top5.iloc[0].district_name == first.district_name and 100 * n1_top5.v / n1_all.v > 75,
         "the district with the most N1 is the same in the comparison table and in the table of the Forest Survey's figures, and the five districts with the most N1 hold more than three quarters of it")
    show("top5_small", V(int((top5.fsi_change_wrt_2021_km2.abs() < 0.1 * top5.n1_km2_2018_2025).sum()), FSI,
                         "of those five rows, those whose `fsi_change_wrt_2021_km2` is, in size, under a tenth of `n1_km2_2018_2025`"), n0)
    show("top5_fall", V(int((top5.fsi_change_wrt_2021_km2 < 0).sum()), FSI, "of those five rows, those with `fsi_change_wrt_2021_km2` below zero"), n0)
    show("top5_rise", V(int((top5.fsi_change_wrt_2021_km2 > 0).sum()), FSI, "of those five rows, those with `fsi_change_wrt_2021_km2` above zero"), n0)
    show("fsi_falls", count(FSI, "rows with `fsi_change_wrt_2021_km2` below zero", lambda t: t.fsi_change_wrt_2021_km2 < 0), n0)
    show("n1_km2_state", agg(FSI, "`n1_km2_2018_2025` summed", lambda t: t.n1_km2_2018_2025.sum()), n0)
    ch_state = show("fsi_change_state", agg(FSI, "`fsi_change_wrt_2021_km2` summed", lambda t: t.fsi_change_wrt_2021_km2.sum()), dec(2))
    sc_state = show("fsi_scrub_state", agg(FSI, "`fsi_scrub_km2` summed", lambda t: t.fsi_scrub_km2.sum()), n0)
    cov_state = show("fsi_cover_state", agg(FSI, "`fsi_forest_cover_km2` summed", lambda t: t.fsi_forest_cover_km2.sum()), n0)
    printed = P["steps"]["08_build_gap_fsi"]["the_table"]["grand_total_as_printed"]
    same("the Forest Survey's change in forest cover, the districts summed and the total its table prints", ch_state.v, float(printed["fsi_change_wrt_2021_km2"]), 0.005)
    same("the Forest Survey's scrub, the districts summed and the total its table prints", sc_state.v, float(printed["fsi_scrub_km2"]), 0.005)
    same("the Forest Survey's forest cover, the districts summed and the total its table prints", cov_state.v, float(printed["fsi_forest_cover_km2"]), 0.005)
    hold(ch_state.v > 0, "the Forest Survey's change in forest cover for the state is a rise")
    sc_top5 = V(float(top5.fsi_scrub_km2.sum()), FSI, "`fsi_scrub_km2` of those five rows, summed")
    calc("top5_scrub_pct", 100 * sc_top5.v / sc_state.v, dec(0), "scrub of those five districts ÷ scrub of the state × 100", [sc_top5, sc_state])
    d1 = dict(pc11_district_code=int(top5.iloc[0].pc11_district_code))
    show("d1_n1_km2", cell(FSI, "n1_km2_2018_2025", **d1), n0); show("d1_change", cell(FSI, "fsi_change_wrt_2021_km2", **d1), dec(2))
    show("fsi_table_name", V(P["steps"]["08_build_gap_fsi"]["the_table"]["name"], PROV, "key `steps` → `08_build_gap_fsi` → `the_table` → `name`"), txt)
    isfr = " ".join(W.use(ISFR_V1).read_text(encoding="utf-8").split())

    def quoted(name, sentence):
        if sentence not in isfr:
            stop(f"a sentence quoted from the Forest Survey's report is not in the registered text of its pages: {sentence[:60]}...")
        show(name, V(sentence, ISFR_V1, "the words as they stand in the file, line breaks apart"), txt)

    quoted("fsi_def", "all lands, more than one hectare with a tree canopy density of more than or equal to 10% irrespective of ownership, legal status and land use. Such lands may not necessarily be a recorded forest area. It also includes orchards, bamboo and palm")
    quoted("fsi_sensor", "using Indian remote sensing satellite data (IRS-LISS III sensor with 23.5 m resolution)")
    quoted("fsi_period", "The data period of the satellite used for this assessment is in general October 2021 to December 2021")
    quoted("fsi_prev", "changes in forest cover in respect of the previous assessment of 2021")
    hold("may be used for non- commercial purposes with due acknowledgment" in isfr and "© Forest Survey of India" in isfr,
         "the imprint of the Forest Survey's report, in the registered text, says that it is the Survey's copyright and that its contents may be used for non-commercial purposes with due acknowledgment")
    hold("scrub" not in isfr.lower(), "the registered pages of the report's first volume, which carry its definitions, do not mention scrub")

    DOC.append("""
## 11. The need read against the Forest Survey's own figures

*Added on 11 October 2026, by the owner's instruction.* N1 sits mostly in a few districts: {top5_names}, {top5_n}
of the {n_districts}, hold {top5_pct} per cent of it. This section sets beside each district's N1 what the Forest Survey of India reports for the
same district. It names no reason for either figure, and nothing in it is an account of why forest was lost.

**What each source measures.**

- **Hansen**, from which N1 is made: gross, stand-replacing loss of tree cover, year by year, on land with canopy
  above ten per cent in the year 2000. N1 is that loss summed over the years 2018 to 2025 in the units where loss is
  recorded (§4).
- **The Forest Survey**: {fsi_table_name}. For each district it gives the forest cover of its assessment of 2023, the
  change in that cover with respect to its assessment of 2021, and the area of scrub, in square kilometres. The
  change is a net figure between two assessments. Forest cover, in the report's own words, is "{fsi_def}". So an
  orchard or a plantation of that size and canopy is forest cover, whatever the land is used for. The report says the
  mapping was done "{fsi_sensor}", that "{fsi_period}", and that it gives "{fsi_prev}". That is other imagery than
  Hansen's, read by another method. The pages of the report registered here that carry its definitions do not define
  scrub.

**They are not the same quantity, and neither can be subtracted from the other.** One is a gross loss added up over
eight years on the forest of the year 2000. The other is a net change between two assessments, in which a loss in one
place is set off by a gain in another, on another definition of forest and from other imagery. For the state as a
whole N1 is {n1_km2_state} km² of gross loss, and the Survey's change is {fsi_change_state} km², a rise; its forest
cover is {fsi_cover_state} km² and its scrub {fsi_scrub_state} km².

**Side by side**, for the {fsi_top_n} districts with the most N1:

{T_fsi}

*n = {n_districts} districts in `50_gap/fsi_district_check.csv`; these are the {fsi_top_n} with the largest N1. The
Forest Survey's columns are as its table prints them, and each column that can be added, summed over the
{n_districts} districts, equals the table's own printed total. Source: Forest Survey of India, India State of Forest
Report of 2023; © Forest Survey of India, whose report allows the use of its contents for non-commercial purposes
with acknowledgment.*

In {top5_small} of the {top5_n} districts with the most N1 the Survey's change is, in size, under a tenth of N1; in
{top5_fall} of the {top5_n} it is a fall and in {top5_rise} a rise. In {d1_name}, which has the most N1, N1 is
{d1_n1_km2} km² and the Survey's change {d1_change} km². Across the state {fsi_falls} of the {n_districts} districts
show a fall. The same {top5_n} districts hold {top5_scrub_pct} per cent of the state's scrub.

**What the four rank correlations show**, over the {n_districts} districts, each computed as in §5:

{T_fsi_rho}

*The interval is a `95 %` percentile bootstrap over districts; p is from shuffling one side against the other. In (c)
and (d) both sides are divided by the district's own forest, as in C12.*

- **Gross loss and net change are not shown to go together across districts.** N1 against the Survey's change: rho {fa_rho}
  ({fa_lo} to {fa_hi}; p {fa_p}), an interval that includes zero. With size taken out of both sides: {fc_rho}
  ({fc_lo} to {fc_hi}; p {fc_p}), which includes zero too. Districts where Hansen records more loss are not shown to
  be those where the Survey reports a larger fall in forest cover, or a larger rise.
- **Gross loss and scrub do go together across districts.** N1 against the Survey's scrub: rho {fb_rho} ({fb_lo} to {fb_hi};
  p {fb_p}), an interval that lies above zero. With size taken out of both sides it is lower and still above zero:
  {fd_rho} ({fd_lo} to {fd_hi}; p {fd_p}). Districts with more N1, and with more N1 for the forest they have, tend
  to be districts where the Survey maps more scrub, and more scrub for its forest cover. These are ranks across
  districts at one time; they say nothing of how either figure moved over the years.

**Readings this run cannot test.** One reading of much gross loss beside little net change is rotational clearing,
in which trees are cut and the land comes back under cover: shifting cultivation is one such practice, and the
harvest and replanting of plantations another. They are named here only as readings this run cannot test. Nothing in these tables tells one from another, or from a difference in what the two sources see: the
definitions differ, the imagery differs, and the periods differ (N1 is of 2018 to 2025; the Survey's change lies
between two of its assessments). The scrub figure is a stock at one assessment and says nothing of when or how the
land came to be scrub.
""")

    # ==== 12. cannot show ============================================================================================================
    ca = {x["name"]: x["text"] for x in key(CAUT2, "cautions_about_the_data").v}
    for k_, n_ in (("sub_tropical_areas", "caut_subtropical"), ("smallholder_landscapes", "caut_small"), ("method_changed_in_2015", "caut_method"), ("loss_is_not_deforestation", "caut_loss")):
        show(n_, V(ca[k_], CAUT2, f"key `cautions_about_the_data`: the sentence named `{k_}`"), txt)

    DOC.append("""
## 12. What this cannot show

- **Cause.** Nothing here shows why forest was lost, why money went where it went, or what money did. A district with a
  small share of the money and a large share of the loss is described by that sentence and by nothing stronger. The
  words "because", "led to", "effect of", "caused" and "drove" are in this document only where it says so.
- **Current allocation at any level finer than a district.** The state report gives districts. The geotagged record,
  which gives places, effectively ends with works started in FY2017-18.
- **Plantation is not forest-specific.** It is the scheme's label and holds horticulture alongside forestry: mango
  orchards and avenue plantations are among its works in the geotagged record (`README.md` §5). The narrow
  forest-named measure exists only in that record, for the earlier years.
- **The pre years are a frozen snapshot.** The four tables of FY2014-15 to FY2017-18 carry the stamp {stamp_pre} and
  have not been rewritten since.
- **R6.20 from FY2020-21 on is restated continuously, so this is a dated copy.** Those tables carry the stamps
  {stamps_late}: the figures are what the report said on those days.
- **Hansen loss is not degradation and does not see thinning.** It is the removal of tree cover from any reason,
  in plantation and natural forest alike; gain is not netted off. The provider's own help text, registered on
  10 October 2026, says: "{caut_loss}" Of its accuracy: "{caut_subtropical}" "{caut_small}" And of its
  method, which has changed over the years: "{caut_method}" The open
  band's rise after 2018 may be on the ground or in the producers' method; that is not established
  (`docs/DECISION_LAYER.md` §18), and P6 is there for that reason.
- **The need on outside-village land.** {n1_out_pct} per cent of N1 lies on land outside any revenue village. That
  land lies in no panchayat unit of the layer, and the census has no row for it: every column of marginalisation
  here is silent about the land where most of the loss is.
- **A requirement.** The gap is the same money distributed by need; not a requirement.
- **A cost.** Nothing can be costed until a sourced rate is supplied. The VGPP rate is not in `00_raw/`. One possible
  source is the district schedule of rates that CLART uses; it is not in `00_raw/` either.
- **What the canopy is made of.** Every measure here that rests on canopy counts whatever meets its threshold as
  forest. Invasive cover, for example Lantana or Prosopis, counts as forest wherever it does.
- **Tree species.** They are not known: no input here names one, and no measure here tells a plantation from a
  natural forest.
- **Every limit of the measurements carries over** (`docs/RESULTS.md` §12): the unit is a geometry and not a
  jurisdiction; the canopy bands are fixed at the year 2000; the census is that of 2011.
""")

    # ==== 13. what this answers of the supervisor's comments =========================================================================
    MAN = "00_raw/data_manifest.csv"
    sup = key(SUP, "comments").v
    hold(len(sup) == 2 and [len(c_["points"]) for c_ in sup] == [3, 2] and all(" ".join(c_["points"]) == c_["text"] for c_ in sup),
         "the record of the supervisor's comments holds two comments, of three points and of two, and the points of each, set end to end, are its text")
    hold(cell(MAN, "dest", item_id="supervisor_comments_as_recorded").v == SUP[len("00_raw/"):] and int(cell(MAN, "bytes", item_id="supervisor_comments_as_recorded").v) == W.use(SUP).stat().st_size
         and W.sha256(W.use(SUP)) in cell(MAN, "how_verified_2026_10_04", item_id="supervisor_comments_as_recorded").v,
         "the record of the supervisor's comments is the file its manifest row describes: its place, its bytes and its SHA-256")
    show("sup_file", V(SUP, MAN, "the row `supervisor_comments_as_recorded`: `dest`, under `00_raw/`"), lambda x: f"`{x}`")
    for k_, c_ in zip("ab", sup):
        show(f"sup_{k_}_after", V(c_["after"], SUP, f"key `comments`: the comment after {c_['after']}: `after`"), txt)
        for j_, pt_ in enumerate(c_["points"], 1):
            show(f"sup_{k_}{j_}", V(pt_, SUP, f"key `comments`: the comment after {c_['after']}: point {j_} of `points`"), txt)
    figs = sorted(p_.name for p_ in (ROOT / "figures" / "stage4").glob("F*.png"))
    hold([n_[:2] for n_ in figs] == ["F1", "F2", "F3", "F4", "F5", "F6"], "the six figures this section names, F1 to F6, are in `figures/stage4/`")
    hold("Commons Connect" in W.use("docs/LAYER.md").read_text(encoding="utf-8") and "Commons Connect" in W.use("docs/DECISION_LAYER.md").read_text(encoding="utf-8"),
         "`docs/LAYER.md` and `docs/DECISION_LAYER.md` both speak of Commons Connect")
    import subprocess
    named = sorted(set(l.split(":", 1)[0] for l in subprocess.run(["git", "-C", str(ROOT), "grep", "-il", "shivani"], capture_output=True, text=True).stdout.split("\n") if l.strip()))
    hold(all(n_ in (SUP, "docs/GAP.md", "scripts/write_gap.py", RUN_LOG, "scripts/write_stage4_run_log.py") for n_ in named),
         "no tracked file of the repository names the paper the comment names, apart from the record of the comment and this stage's own documents and writers")
    hold("ATREE" in W.use("docs/NEED.md").read_text(encoding="utf-8") and not any("OD_CFR_Potential" in i_["path"] for s_ in P["steps"].values() for i_ in s_["inputs"].values()),
         "`docs/NEED.md` describes the use of ATREE's list in stage 2, and no step of this stage reads that list")
    atree_note = cell(MAN, "notes", item_id="atree_webgis").v
    hold("'CFR Recognized Villages' layers exist for Chhattisgarh and Maharashtra only" in atree_note,
         "the manifest's note on the one public map of recognised villages says it has layers for Chhattisgarh and Maharashtra only")
    hold("titles are not mapped" in str(fr.extent_is.iloc[0]), "the table of forest rights by district carries the label that titles are not mapped")

    DOC.append("""
## 13. What this answers of the supervisor's comments

The comments are quoted as the project owner recorded them and gave them on 11 October 2026 ({sup_file}, registered in
the manifest). The record is his; it is not the supervisor's own text. Each point is taken in turn: what in this
stage answers it, by section and figure, and what does not.

**After {sup_a_after}.**

- "{sup_a1}" **Answered here by** the framework of this stage: §4 (need as N1 and N2, never added; marginalisation as
  a split, never a weight), §5 with figure `F4` (need against allocation, district by district), §6 with figure `F5`
  (the comparison split by Scheduled Tribe share and by the development index) and §7 (what more is needed: in
  hectares, as an intensity of works, and as the same money distributed by need). Figure `F1` is the allocation done
  so far, in the state report. **Not answered:** what more is needed in rupees. The cost stays blank (§7, §12).
- "{sup_a2}" **Not a question this stage answers.** How the layer was matched to Commons Connect is in
  `docs/LAYER.md` and `docs/DECISION_LAYER.md`. The paper named is not in this repository, and no stage reads it.
- "{sup_a3}" **Answered in the earlier stages, and used here.** The geotagged record of MGNREGA works and the state
  report R6.20 are stage 3 (`docs/RESULTS.md` §8; figures `F1` and `F2` here). ATREE's list of villages with potential
  for community forest rights is the basis of the forest-dependent households of stage 2 (`docs/NEED.md`); no step of
  this stage reads it. **Not answered:** the villages granted community forest rights, and their boundaries. No file
  in `00_raw/` maps them for Odisha: the manifest notes that the one public map of recognised villages has layers
  for two other states only. This stage has the state's district table of community titles and nothing finer (§10).

**After {sup_b_after}.**

- "{sup_b1}" **Answered by saying what is done and what is not.** Nothing is extracted from documents on community
  forest rights at the level of a village. The state's district table of community titles is set beside need (§10);
  titles are not mapped, so nothing is related to satellite data below the district. The method of the stage is §4
  to §9, and the last section gives the file of every figure.
- "{sup_b2}" **This stage is that question, asked of districts**: where forest loss is recorded (§4; figure `F3`),
  who lives there (§6; figure `F5`), and where the scheme's money went (§5; figures `F1` and `F4`). For the years the
  geotagged record covers it is also asked of units within a district (§9; figure `F6`). **Not answered:** whether
  the allocation was "good enough". No requirement is set here, and none can be until a rate is supplied (§7).

**Not answered, plainly.** Community forest rights village by village: titles are not mapped (§10). Tree species:
no input names one (§12). Costing: no sourced rate is in `00_raw/` (§7, §12).
""")

    # ==== 14, 15 =====================================================================================================================
    show("v_layer", W.verifier("verify_layer.py", a.draft), txt)
    show("v_decision", W.verifier("verify_decision.py", a.draft), txt)
    show("v_r620", W.verifier("verify_r620.py", a.draft), txt)
    show("share_steps", key(SHARE_EX, "summary/steps"), n0)
    hold(key(SHARE_EX, "summary/steps").v == key(SHARE_EX, "summary/steps_as_expected").v and all(W.sha256(W.use(i_["path"])) == i_["sha256"] for i_ in key(SHARE_EX, "inputs").v),
         "the gate on the shared copy passed every step, on the files that are on disk")
    show("trial_kinds", V("; ".join(kinds), TRIALS, "key `trials`: the distinct kinds of error"), txt)
    rv = key(REVIEWS, "reports").v
    by_agents, own = key(REVIEWS, "parts_written_by_agents").v, key(REVIEWS, "parts_written_by_the_session").v
    in_script = re.findall(r"part_([a-z_]+)", re.search(r"^PARTS = \[(.*?)\]", W.use("scripts/verify_gap.py").read_text(encoding="utf-8"), re.M).group(1))
    hold(sorted(in_script) == sorted(by_agents + own) and all(sum(p_ in r_["parts"] for r_ in rv) == 1 for p_ in in_script) and key(REVIEWS, "reader_reported").v is True,
         "the parts the verifier runs are those the record of the review round lists, each is in one agent's report and in no other, and the last reader reported")
    second = [p_ for r_ in rv for p_ in r_["parts"] if r_["role"].startswith("reviewed")]
    own_writer = [p_ for r_ in rv for p_ in r_["parts"] if not r_["role"].startswith("reviewed")]
    hold(own_writer == ["fsi"] and sorted(second + own_writer) == sorted(in_script),
         "in the round of review every part but one went to an agent that had not written it; the part on the Forest Survey's figures was tried by the agent that wrote it and by no other")
    hold(key(REVIEWS, "verifier_sha256").v == W.sha256(W.use("scripts/verify_gap.py")), "the record of the review round is of the verifier that is on disk")
    show("vg_parts", V(len(in_script), "scripts/verify_gap.py", "its list `PARTS`: how many parts"), n0)
    show("vg_agent_parts", V(len(by_agents), REVIEWS, "key `parts_written_by_agents`: how many"), n0)
    show("vg_own_parts", V(len(own), REVIEWS, "key `parts_written_by_the_session`: how many"), n0)
    show("rev_second", V(len(second), REVIEWS, "key `reports`: the parts of the reports whose `role` begins 'reviewed'"), n0)
    planted, caught_ = sum(r_["errors_planted"] for r_ in rv), sum(r_["errors_caught"] for r_ in rv)
    show("rev_planted", V(planted, REVIEWS, "key `reports`: `errors_planted`, added"), n0)
    show("rev_caught", V(caught_, REVIEWS, "key `reports`: `errors_caught`, added"), n0)
    show("rev_missed", V(planted - caught_, REVIEWS, "key `reports`: `errors_planted` less `errors_caught`, added"), n0)
    show("rev_dis", V(sum(len(r_["disagreements"]) for r_ in rv), REVIEWS, "key `reports`: `disagreements`, counted"), n0)
    show("rev_changed", V(len(key(REVIEWS, "pieces_changed_after_the_round").v), REVIEWS, "key `pieces_changed_after_the_round`: how many"), n0)
    show("rev_pieces", V(len(key(REVIEWS, "pieces").v), REVIEWS, "key `pieces`: how many"), n0)
    rd = key(REVIEWS, "reader").v
    show("reader_claims", V(len(rd["names_that_claim_more_than_the_code_tests"]), REVIEWS, "key `reader` → `names_that_claim_more_than_the_code_tests`: how many"), n0)
    hold(len(rd["names_defined_in_two_parts"]) == 0, "the reader found no name defined in two pieces of the verifier")
    S3 = "50_gap/gates_step3.csv"
    s3 = W.C(S3)
    hold(len(s3) > 0 and (s3["pass"] == "yes").all(), "every gate of the rebuild that followed the review passed")
    same3 = cell(S3, "found", gate="tables of figures that are byte for byte what they were")
    m3 = re.fullmatch(r"(\d+) of (\d+)", same3.v)
    hold(bool(m3) and m3.group(1) == m3.group(2), "in the rebuild that followed the review every table of figures is byte for byte what it was")
    show("s3_same", V(int(m3.group(1)), S3, "column `found`, the gate on tables that are byte for byte what they were: its first number"), n0)
    LOOKED = "50_gap/figures_looked_at.json"
    looked = key(LOOKED, "files").v
    show("looked_n", V(len(looked), LOOKED, "key `files`: their number"), n0)
    show("looked_utc", key(LOOKED, "recorded_utc"), txt)
    hold(len(looked) > 0 and all(W.sha256(W.use("figures/stage4/" + n_)) == h_ for n_, h_ in looked.items()),
         "the figures on disk are, byte for byte, the images the record says were looked at")
    show("n_gates", V(sum(s_["gates"] for s_ in steps.values()), PROV, "key `steps`: `gates` of the seven steps that carry gates, added"), n0)
    show("seed", V(steps["08_build_gap_districts"]["seeds"]["base"], PROV, "key `steps` → `08_build_gap_districts` → `seeds` → `base`"), txt)

    DOC.append("""
## 14. How it was verified

- **Gates.** Every step with an expected value stops the build if the value found differs: {n_gates} gates across the
  seven steps that carry them (the two environments, the inputs, the districts, the panel, the unit history, forest
  rights and the Forest Survey's figures), each written to a table in `50_gap/` and to `docs/stage4_run_log.md`. No
  expected value and no tolerance was changed to pass one.
- **Independent recomputation.** `scripts/verify_gap.py` imports nothing from the builders. It is made of {vg_parts}
  parts. {vg_agent_parts} of them were written by agents from the builders' written definitions, not from their code;
  the other {vg_own_parts}, small ones that hold a derived file against the table it is cut from or the environment
  against its pins, are the session's own. It recomputes the figures of every table the stage's steps write, from the
  inputs: "{v_gap}". Sums are exact. A permutation p and a bootstrap interval of a rank correlation are recomputed
  twice: with the verifier's own draws, to a stated tolerance, and with the recorded seeds, to the digit, on a
  stated reading of how the random generator is called. For the models it recomputes each coefficient and CR1
  standard error in numpy, recomputes the wild-bootstrap p with its own code and its own draws, and tests both ends
  of every interval with the package and the recorded seed.
- **The review of the verifier: one round, as the owner ruled.** {rev_second} of the {vg_parts} parts each went to an
  agent that had not written it, which tried the part with planted errors and mended the checks that let one
  through. The part on the Forest Survey's figures was written in that round and tried by its own writer; no second
  agent has reviewed it. In the round {rev_planted} errors were planted in copies of the tables, and the part
  concerned caught {rev_caught}; the {rev_missed} it did not are named in `docs/stage4_run_log.md`, with what each
  was. The reviewers reported {rev_dis} disagreements, which the run log gives. All were put right in the builders'
  written definitions; the steps concerned were run again, and all {s3_same} tables of figures are byte for byte
  what they were (`50_gap/gates_step3.csv`). A last reader then went through
  every part for columns that no check reads. By its reading, every column of the tables is read by some check;
  labels, notes and reasons are held by key words and not word for word; and {reader_claims} descriptions or check
  names claimed more than the code tests, which the session then reworded or closed, bar one that cannot be: the
  owner's expected values are typed into the verifier from his instructions, and no file carries them for a check
  to read. After the round the session changed {rev_changed} of the script's {rev_pieces} pieces, with no agent to
  review the changes; the run log names them. What each part assumes and what it does not cover are in the run log
  too.
- **Deliberate errors.** {trials_n} errors were planted, one at a time, in copies of the stage's files: every table,
  the two text files of the models, the provenance record and the record of the check of the forest villages PDF,
  {trials_tables} files in all. The verifier caught {trials_caught}. Their kinds:
  {trial_kinds}. The record is
  `50_gap/verify_gap_trials.json`.
- **The earlier verifiers**, run by this script as it wrote the document: `scripts/verify_r620.py`: "{v_r620}";
  `scripts/verify_layer.py`: "{v_layer}"; `scripts/verify_decision.py`: "{v_decision}". The gate on the copy of the layer
  that is passed on: {share_steps} of {share_steps} steps.
- **Seeds and versions.** Every random draw is seeded from one base, `{seed}`; each table carries its own seeds. The
  packages: {pkg}. `50_gap/gap.provenance.json` has every input's `SHA-256`, the seeds and the run times.
- **The environment.** Every step ran with an interpreter that held exactly the {env_n} packages
  `requirements-stage4.txt` pins, and stopped otherwise; the record lists them at every step. The main environment's
  `numpy` is {main_numpy}, the version the earlier stages' provenance records show, and the earlier verifiers were run
  there. `50_gap/gates_environment.csv` has the {env_gates} gates on the two environments.
- **The figures** (`figures/stage4/`) are drawn from these tables by a script that measures its own layout. Each of
  the {looked_n} images was also opened and looked at ({looked_utc}), and the images on disk are those: the record,
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
""")

    # ==== gates, then the appendix ===================================================================================================
    body = "".join(DOC)
    bad = W.stray_digits(body)
    if bad:
        stop("the text carries digits of its own:\n  " + "\n  ".join(bad[:25]))
    asked = re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", body)
    known = set(W.FIG) | set(W.TABLES)
    if set(asked) - known:
        stop("printed but not defined: " + ", ".join(sorted(set(asked) - known)))
    if known - set(asked):
        stop("defined but not printed: " + ", ".join(sorted(known - set(asked))))
    text = body.format_map({**{k: v["text"] for k, v in W.FIG.items()}, **{k: v["md"] for k, v in W.TABLES.items()}})
    # nothing about cause: each use of a causal word must stand in a sentence that says what cannot be shown, or in a quotation
    flat = " ".join(text.split())
    for cell_name in P["steps"]["08_build_gap_districts"]["cell_names"].values():      # a cell's own name is the layer's ("... find the cause first"), not a claim
        flat = flat.replace(cell_name, "")
    for m in CAUSAL.finditer(flat):
        s0 = max(flat.rfind(". ", 0, m.start()), flat.rfind("** ", 0, m.start()), flat.rfind("- **", 0, m.start()))
        s1 = flat.find(". ", m.end())
        sentence = flat[s0 + 1:s1 + 1 if s1 > 0 else len(flat)]
        if not re.search(r"cannot show|nothing here shows|not an effect|is not an\s+effect|only where it says so|says nothing about why|No figure here is an effect|only to say what", sentence, re.I):
            stop("a word of cause stands in a sentence that does not say what the analysis cannot show: ..." + sentence[-260:])
    W.HELD.append("every use of \"because\", \"led to\", \"effect of\", \"caused\", \"drove\" or \"cause\" in the text stands in a sentence that says what the analysis cannot show (the names of the layer's cells apart)")

    order, seen_ = [], set()
    for k in asked:
        if k not in seen_:
            seen_.add(k)
            order.append(k)
    app = ["\n## 16. Where every figure comes from\n",
           "This section is the script's own record of what it read. Paths are relative to the repository. `50_gap/` is this stage's output and the other numbered folders are the outputs "
           "of the stages before it: each is rebuilt by the script named in the provenance record beside it, and none is in git.\n",
           "### 16.1 Figures in the text, in the order they first appear\n", "| as printed | file | where in the file |", "|---|---|---|"]
    for k in order:
        if k in W.FIG:
            f = W.FIG[k]
            files = "; ".join(dict.fromkeys(s[0] if s[0] == "this run" else f"`{s[0]}`" for s in f["sources"]))
            where = (f"computed here: {f['formula']}. From: " + "; ".join(s[1] for s in f["sources"])) if f["formula"] else f["sources"][0][1]
            shown = f["text"] if len(f["text"]) <= 160 else f["text"][:157] + "..."
            app.append(f"| {shown.replace('|', '/')} | {files} | {where.replace('|', '/')} |")
    app += ["\n### 16.2 Tables, in the order they appear\n", "Every cell of a table that is not a typed label was read from the file and columns given here.\n", "| table | cells read | file | columns or keys | rows |", "|---|---|---|---|---|"]
    names = {"T_top": "§5, the districts with the most need", "T_cmp": "§5, the comparisons", "T_panel": "§8, the panel models", "T_units": "§9, the unit models",
             **{f"T_{cid}_{g_}": f"§6, {cid} by {g_.replace('_', ' ')}" for cid in ("C1", "C4") for g_ in ("st_class", "adi_tercile", "sc_tercile")}}
    for k in order:
        if k in W.TABLES:
            for i, (file, s) in enumerate(W.TABLES[k]["src"].items()):
                rows_ = "; ".join(s["rows"])
                cols_ = ", ".join(x.replace("column ", "").replace("key ", "") for x in s["cols"])
                app.append(f"| {names.get(k, k) if i == 0 else ''} | {W.TABLES[k]['cells'] if i == 0 else ''} | `{file}` | {(cols_ if len(cols_) < 700 else cols_[:700] + ' ...').replace('|', '/')} | {(rows_ if len(rows_) < 500 else rows_[:500] + ' ...').replace('|', '/')} |")
    app += ["\n### 16.3 Files read\n", "| file | bytes | sha256 | the run stamp it carries |", "|---|---|---|---|"]
    for path in sorted(W.FILES):
        f = W.FILES[path]
        app.append(f"| `{path}` | {f['bytes']:,} | `{f['sha256'][:16]}` | {f['run_utc'] or '-'} |")
    app += ["\n### 16.4 Statements tested before they were written\n", "Each of these is something the text says in words. The script tested it against the files and would have stopped had it failed.\n"]
    app += [f"- {s}" for s in W.HELD]
    app += ["\n### 16.5 Totals that two places both carry, compared\n"] + [f"- {s}" for s in W.SAME]
    n_fig = len([k for k in order if k in W.FIG])
    app += ["\n### 16.6 Digits the text was allowed to carry\n", "The text itself may hold no digit except inside a code span (a file, a column, a design constant written as code, a command) and in: "
            + "; ".join(dict.fromkeys(why for _, why in W.ALLOWED)) + ". Everything else that is a number came from a file.\n",
            f"*{n_fig} figures and {len(W.TABLES)} tables ({sum(t['cells'] for t in W.TABLES.values())} cells) from {len(W.FILES)} files; {len(W.HELD)} statements tested; {len(W.SAME)} totals compared. "
            f"Written {written} by `scripts/write_gap.py` (sha256 `{W.sha256(__file__)[:16]}`), with the reading functions of `scripts/write_results.py` (sha256 `{W.sha256(W.__file__)[:16]}`).*\n"]
    out = Path(a.draft) if a.draft else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n".join(app), encoding="utf-8")
    print(f"{out}: {len(text.splitlines()) + len(app):,} lines; {n_fig} figures, {len(W.TABLES)} tables ({sum(t['cells'] for t in W.TABLES.values())} cells), {len(W.FILES)} files read; "
          f"{len(W.HELD)} statements tested, {len(W.SAME)} totals compared; verifiers {'NOT run (draft)' if a.draft else 'run'}")


if __name__ == "__main__":
    main()
