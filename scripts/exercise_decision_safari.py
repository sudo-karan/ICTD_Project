"""The demo layer in the Safari application with its window found BY ITS ADDRESS - and the decision view in it.

    python scripts/exercise_decision_safari.py

This is a NEW check (8 Oct 2026). It is NOT the regression gate and does not stand in for it: the gate asks that
scripts/exercise_layer_safari.py passes by itself - which it has done since (see the end of this paragraph).

A NOTE OF 11 OCTOBER 2026, on the word "unchanged". Until that day scripts/exercise_layer.py and
scripts/exercise_layer_safari.py had been left exactly as they were on 7 October. On 11 October 2026 they were changed
only where they pinned reworded words, as listed in docs/SITE_COPY.md: exercise_layer.py in the words it expects of the
page, and exercise_layer_safari.py in none of its own lines - it pins no reworded word itself and compares a unit's
panel through exercise_layer.py's expected(). scripts/verify_layer.py is still unchanged. Where the account below says
"that script", it is exercise_layer_safari.py as it then was.
THIS script's own pins of reworded words were brought up to date on the same day (the legend's note; and the overlay's
note, which no longer stands in the page's text but in the "i" beside the box, which a reading of the page's text cannot
open). It was NOT run then, by the owner's ruling, and it has not been brought up to date with his rulings of 9 October
2026: it still reads a text of the data that those rulings removed (t.lower_bound), knows ten cells of a row where the
list has had eleven since, and does not fill the list's head with the order within a tier. It will stop at its first
window until that is done.

Why this script exists beside the gate's:

On 8 Oct 2026, on an earlier build of that day, that script stopped at its first reading, before any of its
assertions (one such stop is on record, with its error, among the session's working files). Two things about how it finds
and waits for its window can stop it, and both are in Safari and not in the layer.
 1. It finds its window by the address and then reads it through the reference Safari hands back - and Safari hands a
    document back BY ITS TITLE. When another window showing this page is open (here: one restored from the last Safari
    session, which every window of the page shares its title with), the reading is of that other window.
 2. It reads one second after asking for the window. A Safari that was started by the script itself is hidden, in the
    background, and took 7 to 14 seconds before the new window could be found at all.
No window of the owner's was closed, and Safari was not brought to the front, to get round this: both are the owner's.
The owner's windows were lost all the same, and not by these scripts: on 8 Oct 2026, mid-run, the hidden Safari received a
request to quit that nothing here sends (system log, 16:19:50 IST; the machine was heavily loaded), and when Safari was
started again the three windows it had restored from the owner's last session were no longer open. They were not recreated.
Later the same day, with Safari already running in the background and no other window showing the layer, that script
PASSED as written (60_layer/exercise_safari.json; scripts/run_decision_checks.py now records every run of it). So
the gate's Safari half can be met; this script is for the days when the owner's Safari is not in that state, and for the
decision view, which that script does not know.
(The command the scripts close their own window with - close (first document whose URL starts with the marked address) -
was tested on two windows of the same title: it closes the marked one and leaves the other.)
Run it by itself on a machine that is otherwise quiet: on 8 Oct 2026, with seven other jobs running, Safari stopped
answering and then received a quit request in the middle of a run, and the run was lost.

PART 1 runs main() of exercise_layer_safari.py - every address it opens, every comparison, every assertion, as that
       script has them - with ONE function of it replaced while this script runs: read(). The replacement asks for the title, the
       address and the text each THROUGH the address filter, never through a reference by title, and answers "nothing yet"
       while the window is not there instead of stopping. What is compared with what is exactly as it was.
       main() writes 60_layer/exercise_safari.json; this script puts that file back as it found it, so it stays the record
       of the last run of that script by itself, and keeps today's readings in its own output.
PART 2 is the decision view, reached through the parts of the address it understands (layer=decision, window, rank, tiers,
       st, keepout, unit): the legend of each of the four windows with the decision table's counts, the ranked list of two
       districts in two windows (its head, every unit in order, its first rows cell by cell), a changed tier order, the
       Scheduled Tribe filter with and without the outside-village units, and "why this tier" for the units that
       exercise_decision.py clicked in Chrome - so run that first.

NOTHING IS CLICKED, as in exercise_layer_safari.py and for the same reason. So the controls themselves, the export and the
online overlay are not looked at here: exercise_decision.py does that in Chrome and in WebKit, the engine of Safari. What
this adds is that the page, opened from disk in the Safari application, shows the decision view's text as the tables give it.

It opens one new window in Safari at a time, marked in its address, uses only that window and closes it.

Output: 60_layer/exercise_decision_safari.json - both parts, every address with what the page then showed, the sha256 of the
two files opened and of every table read, how the window was read, and the UTC time. Exits 1 unless everything held."""
import hashlib, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import exercise_layer_safari as S          # importing it opens nothing (it sets sys.argv for exercise_layer itself)
X = S.X
import exercise_decision as E              # the decision table and what a unit, a list and a legend should show; opens nothing

import pandas as pd

HOW = ("title, address and text were each asked for through the address filter (first document whose URL starts with the "
       "marked address), never through the by-title reference Safari returns; a reading made before the window exists "
       "counts as 'nothing yet'")
NOT_YET = ("-1719", "-1728", "-1700")      # no such document yet / cannot get it yet / its text is not there yet
waited = {"nothing_yet": 0}


def read():
    f = S.DOC
    try:
        out = S.osa(f'tell application "Safari"\nreturn (name of {f}) & "\\n<<<ictd>>>\\n" & (URL of {f}) & "\\n<<<ictd>>>\\n" & (text of {f})\nend tell')
    except RuntimeError as e:
        if not any(code in str(e) for code in NOT_YET):
            raise
        waited["nothing_yet"] += 1
        return {"name": "", "url": "", "text": ""}
    name, url, text = out.split(S.SEP, 2)
    return {"name": name, "url": url, "text": X.norm(text)}


def goto(part, until, wait_s=120):
    S.osa(f'tell application "Safari" to set URL of {S.DOC} to "{S.BASE}#{part}"')
    t0 = time.time()
    while True:
        time.sleep(0.6)
        s = read()
        if until(s) or time.time() - t0 > wait_s:
            return s


def has(text, words):
    return S.sq(X.norm(words)) in S.sq(text)


def row_of(u, w, order):
    """The ten cells of a unit's row in the ranked list, from the tables (the rule of exercise_decision.py, part A3)."""
    f = X.expected(u)
    fn = "not recorded" if pd.isna(X.AL.loc[u, "expenditure_forest_named_worktype"]) else f"Rs {X.AL.loc[u, 'expenditure_forest_named_worktype'] / 1e5:,.2f} lakh"
    st = X.NC if E.OUT[u] else ("not defined: no resident population" if pd.isna(X.N_.loc[u, "st_share"]) else f"{100 * X.N_.loc[u, 'st_share']:,.2f} %")
    adi = X.NC if E.OUT[u] else ("no index for this unit's villages" if pd.isna(X.N_.loc[u, "adi_2011"]) else f"{X.N_.loc[u, 'adi_2011']:,.2f}")
    return [E.tier_label(E.T[u][f"cell_{w}"], order), f"{f[0][1]} ({u})", "Outside-village unit" if E.OUT[u] else "LGD panchayat unit", E.shown(E.T[u]["standing_dense_ha"]), E.shown(E.T[u]["standing_open_ha"]),
            E.shown(E.T[u][f"forest_loss_ha_{w}"]), E.corro(u), st, adi, fn]


def main():
    files = {f: hashlib.sha256((ROOT / "60_layer" / f).read_bytes()).hexdigest() for f in ("index.html", "data.js")}
    prov = json.load(open(X.read("60_layer/layer.provenance.json")))
    raw = (ROOT / "60_layer" / "data.js").read_text(encoding="utf-8")
    D = json.loads(raw[len("window.ICTD_LAYER = "):].rstrip()[:-1])
    V = D["decision"]
    chrome = json.load(open(X.read("60_layer/exercise_decision_chrome.json")))
    if chrome["summary"]["layer_run_utc"] != prov["run_utc"]:
        raise SystemExit("60_layer/exercise_decision_chrome.json is of another build of the layer: run exercise_decision.py chrome first")
    for other in ("exercise_layer_safari.py", "exercise_layer.py", "exercise_decision.py"):
        X.read(f"scripts/{other}")                               # run here as they are on disk: recorded with their sha256 like every table read

    # ---- PART 1: main() of exercise_layer_safari.py, its window read by address ----------------------------------------------------------
    record = ROOT / "60_layer" / "exercise_safari.json"
    kept = record.read_bytes() if record.is_file() else None
    kept_summary = json.loads(kept)["summary"] if kept else None
    S.read = read
    print("PART 1: main() of exercise_layer_safari.py as it is on disk, with its window read by address\n", flush=True)
    try:
        rc1 = S.main()
        part1 = json.load(open(record))
    finally:
        if kept is not None:
            record.write_bytes(kept)                             # stays the record of the last run of that script by itself
        elif record.is_file():
            record.unlink()
    part1["summary"]["how_the_window_was_read"] = HOW
    part1["summary"]["readings_made_before_the_window_was_there"] = waited["nothing_yet"]
    n1 = len(S.steps)
    version = S.osa('tell application "Safari" to get version')

    # ---- PART 2: the decision view, by address ---------------------------------------------------------------------------------------------
    print("\nPART 2: the decision view, by address\n", flush=True)
    say = S.say
    default_order = list(E.ORDER0)
    tiers0 = "tiers=" + ".".join(default_order)
    title = lambda w: V["t"]["legend_title"].replace("{window}", E.WIN[w])
    units, lists = [], []
    S.osa(f'tell application "Safari" to make new document with properties {{URL:"{S.BASE}"}}')
    try:
        t0 = time.time()
        while True:
            time.sleep(1.0)
            s = read()
            if (s["name"] == D["title"] and X.norm(D["subtitle"]) in s["text"]) or time.time() - t0 > 180:
                break
        say("page", f"opened {S.BASE} in the Safari application, version {version}, with nothing of the decision view in the address",
            f"after {time.time() - t0:.0f} s the title is '{s['name']}'; the side panel carries the decision view's switch ('{V['radio'][:40]}...') and nothing else of it - its windows, tiers and overlay box are folded away - "
            f"and no legend of the decision view: an ordinary layer is on",
            s["name"] == D["title"] and has(s["text"], V["radio"]) and not has(s["text"], V["overlay"]["label"]) and not has(s["text"], V["t"]["tiers_head"]) and not has(s["text"], title(V["default_window"])))

        # the four windows: the legend, with the table's counts
        for w in ("2018_2025", "2001_2025", "2017_2023", "2021_2025"):
            want = E.legend_expected(w, default_order)
            s = goto(f"layer=decision&window={w}&{tiers0}&st=0", lambda s: has(s["text"], title(w)) and all(has(s["text"], r) for r in want))
            lost = S.in_order(s["text"], [(r, r) for r in want], after=X.norm(title(w)))
            say("window, by address", f"set the address to '#layer=decision&window={w}&...'",
                f"the legend's title names the window ('{title(w)}') and its six rows - five tiers and 'Not ranked' - follow in the provisional order, each with the decision table's count ({want[0]} ...)"
                + (f"; missing: {lost[:2]}" if lost else "") + "; with no district chosen the page says that units are ranked within a district and never across the state; the view's controls are unfolded, the overlay's box among them with nothing "
                "written under it: since 11 October 2026 its note - online, optional, off unless ticked - stands in the 'i' beside the box, which a reading of the page's text cannot open (exercise_decision.py opens it in Chrome and in WebKit)",
                has(s["text"], title(w)) and not lost and has(s["text"], V["t"]["rank_none"]) and has(s["text"], V["t"]["lower_bound"]) and has(s["text"], V["overlay"]["label"]) and not has(s["text"], V["overlay"]["note"]) and has(s["text"], V["t"]["tiers_head"]))

        # the ranked list: two districts, two windows
        names = [d["name"] for d in D["districts"]]
        n_out_by = {d: sum(1 for u in E.IDS if E.OUT[u] and E.T[u]["district"] == d and E.T[u]["cell_2018_2025"] != E.UNRANKED) for d in names}
        most_outside = max(n_out_by, key=n_out_by.get)
        for d, w in ((most_outside, "2018_2025"), (most_outside, "2017_2023"), ("Ganjam", "2018_2025"), ("Ganjam", "2001_2025")):
            rows, _, _, _ = E.ranked(d, w, default_order)
            n_un = sum(1 for u in E.IDS if E.T[u]["district"] == d and E.T[u][f"cell_{w}"] == E.UNRANKED)
            head = V["t"]["rank_head"].replace("{district}", d).replace("{n}", f"{len(rows):,}").replace("{window}", E.WIN[w]).replace("{order}", V["t"]["order_default"])
            foot = V["t"]["rank_unranked"].replace("{n}", f"{n_un:,}").replace("{name}", E.NAME[E.UNRANKED])
            s = goto(f"layer=decision&window={w}&{tiers0}&st=0&rank={d}", lambda s: has(s["text"], head))
            out_of_order = S.in_order(s["text"], [(u, f"({u})") for u in rows], after=X.norm(head))
            first = [(u, [c for c in row_of(u, w, default_order)]) for u in rows[:5]]
            bad_rows = [u for u, cells in first if S.in_order(s["text"], [(c, c) for c in cells], after=X.norm(head))]
            cols = [c.replace("{window}", E.WIN[w]) for c in V["t"]["cols"]]
            lists.append({"district": d, "window": w, "rows": len(rows), "outside_village_rows": sum(1 for u in rows if E.OUT[u]), "ids_not_found_in_order": len(out_of_order), "first_rows_checked": len(first), "first_rows_wrong": bad_rows})
            say("ranked list, by address", f"set the address to '#layer=decision&window={w}&rank={d}'",
                f"the head reads '{head[:95]}...'; all {len(rows):,} units of the list are in the page's text in the decision table's order ({sum(1 for u in rows if E.OUT[u]):,} of them outside-village units)"
                + (f" - NOT FOUND IN ORDER: {out_of_order[:3]}" if out_of_order else "") + f"; the first {len(first)} rows have their ten cells as the tables give them" + (f" - WRONG: {bad_rows}" if bad_rows else "")
                + f"; the column heads name the window ({E.WIN[w]}) and the badge's own (2017-2023); the foot says {n_un:,} more are '{E.NAME[E.UNRANKED]}'; the legend adds each cell's count in {d}",
                has(s["text"], head) and not out_of_order and not bad_rows and (n_un == 0 or has(s["text"], foot)) and not S.in_order(s["text"], [(c, c) for c in cols], after=X.norm(head))
                and all(has(s["text"], r) for r in E.legend_expected(w, default_order, d)) and f"rank={d}" in s["url"].replace("%20", " "))

        # a tier order changed through the address
        d, w = most_outside, "2018_2025"
        order = [default_order[1], default_order[0]] + default_order[2:]
        words = E.order_words(order)
        rows, _, _, _ = E.ranked(d, w, order)
        head = V["t"]["rank_head"].replace("{district}", d).replace("{n}", f"{len(rows):,}").replace("{window}", E.WIN[w]).replace("{order}", words)
        s = goto(f"layer=decision&window={w}&tiers={'.'.join(order)}&st=0&rank={d}", lambda s: has(s["text"], head))
        want = E.legend_expected(w, order, d)
        out_of_order = S.in_order(s["text"], [(u, f"({u})") for u in rows], after=X.norm(head))
        say("tier order, by address", f"set the address to '...&tiers={'.'.join(order)}' (the first two tiers changed places)",
            f"the legend's rows follow the new order ({want[0][:60]}...), the list's head says the order is '{words[:45]}...' and spells it out, and its {len(rows):,} units are in that order",
            has(s["text"], head) and not S.in_order(s["text"], [(r, r) for r in want], after=X.norm(title(w))) and not out_of_order and has(s["text"], "Tier order: " + words))

        # the filter, with the outside-village units kept and then left out (the address can untick the box, not tick it again: this comes last)
        for st, keep in (("50", True), ("33", True), ("33", False)):
            rows, dropped, out_kept, out_dropped = E.ranked(d, w, default_order, st, keep)
            label = dict(V["t"]["st_options"])[st]
            note = V["t"]["rank_filter_note"].replace("{label}", label).replace("{m}", str(dropped))
            out_note = V["t"]["rank_out_kept"].replace("{k}", str(out_kept)) if keep else V["t"]["rank_out_dropped"].replace("{k}", str(out_dropped))
            head = V["t"]["rank_head"].replace("{district}", d).replace("{n}", f"{len(rows):,}").replace("{window}", E.WIN[w]).replace("{order}", V["t"]["order_default"])
            s = goto(f"layer=decision&window={w}&{tiers0}&rank={d}&st={st}" + ("" if keep else "&keepout=0"), lambda s: has(s["text"], head) and has(s["text"], note))
            out_of_order = S.in_order(s["text"], [(u, f"({u})") for u in rows], after=X.norm(head))
            say("filter, by address", f"set the address to '...&st={st}" + ("'" if keep else "&keepout=0'"),
                f"the list holds {len(rows):,} units, the ones need_by_unit.csv gives, in the same order as without the filter; the note reads '{note[:80]}...' and '{out_note[:70]}...'",
                has(s["text"], head) and has(s["text"], note) and has(s["text"], out_note) and not out_of_order)

        # the units exercise_decision.py clicked in Chrome, each opened by its id, in the window it was seen in
        for k in chrome["units"]:
            u, w = k["unit"], k["window"]
            e = E.why_expected(u, w, default_order)
            lines = [("chip", e["chip"]), ("window", e["window"])] + [(f"hectares[{j}]", v) for j, v in enumerate(e["hectares"])] + [("standing", e["standing"]), ("loss", e["loss"])]
            if e["near"]:
                lines.append(("near", V["t"]["near"]))
            lines += [("cell", e["cell"]), ("corro", e["corro"]), ("work", e["work"])]
            if e["gov"]:
                lines += [("gov", e["gov"]), ("district", e["district"])]
            # the table of hectares is laid out row by row: standing then lost, for dense, open and the land below them - the order of e["hectares"]
            s = goto(f"layer=decision&window={w}&{tiers0}&st=0&unit={u}", lambda s: has(s["text"], V["t"]["why_head"]) and has(s["text"], "Unit id " + u) and has(s["text"], e["window"]) and has(s["text"], e["cell"]))
            missing = S.in_order(s["text"], lines, after=X.norm(V["t"]["why_head"]))
            wrongly_near = (not e["near"]) and has(s["text"], V["t"]["near"])
            wrongly_gov = (not e["gov"]) and has(s["text"], E.GOV_ON_THE_PAGE)      # the prompt as the page words it since 11 October 2026 (the owner's third handoff); until then, the decision table's sentence
            units.append({"unit": u, "window": w, "cell": E.T[u][f"cell_{w}"], "type": "outside_village" if E.OUT[u] else "lgd_panchayat", "found": len(lines) - len(missing), "of": len(lines), "missing": missing,
                          "close_call_shown_wrongly": wrongly_near, "governance_prompt_shown_wrongly": wrongly_gov})
            say("unit, by address", f"set the address to '#layer=decision&window={w}&unit={u}'",
                f"{len(lines) - len(missing)} of {len(lines)} lines of 'why this tier' are in the page's text, in the block's order (cell {E.T[u][f'cell_{w}']}, {E.WIN[w]}, {'outside-village' if E.OUT[u] else 'LGD panchayat'} unit)"
                + (f"; missing: {missing[:2]}" if missing else ""), not missing and not wrongly_near and not wrongly_gov)
    finally:
        try:
            S.osa(f'tell application "Safari" to close {S.DOC}', limit=30)
        except Exception:
            pass

    steps2 = S.steps[n1:]
    found, of = sum(r["found"] for r in units), sum(r["of"] for r in units)
    cells_seen = sorted({(r["cell"], r["window"]) for r in units})
    summary = {"script": "scripts/exercise_decision_safari.py", "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "inputs": X.INPUTS, "browser": f"Safari {version} (the application)",
               "events_were": "none: the page was driven by its address alone and read back through AppleScript (title, address, the text shown); nothing was clicked",
               "how_the_window_was_read": HOW, "opened": S.BASE, "layer_run_utc": prov["run_utc"], "decision_table_run_utc": E.PROV["run_utc"], "files_sha256": files,
               "this_is_not_the_regression_gate": "the gate is scripts/exercise_layer_safari.py passing by itself; part 1 is that script's main() with read() replaced while this script runs. (Until 11 October 2026 that script and scripts/exercise_layer.py "
                                                  "were unchanged; on that day they were changed only where they pinned reworded words, as listed in docs/SITE_COPY.md. The key 'part1_the_unchanged_scripts_main' keeps its name, which other scripts read.)",
               "part1_the_unchanged_scripts_main": {"exit": rc1, "addresses_tried": part1["summary"]["addresses_tried"], "addresses_as_expected": part1["summary"]["addresses_as_expected"],
                                                     "units_opened_by_address": part1["summary"]["units_opened_by_address"], "values_compared": part1["summary"]["values_compared"], "values_found": part1["summary"]["values_found"]},
               "part2_the_decision_view": {"addresses_tried": len(steps2), "addresses_as_expected": sum(s["ok"] for s in steps2), "lists_opened": lists, "units_opened_by_address": len(units), "lines_compared": of, "lines_found": found,
                                           "cells_and_windows_seen": [f"{c} in {w}" for c, w in cells_seen], "by_type": {t: sum(1 for r in units if r["type"] == t) for t in ("lgd_panchayat", "outside_village")}},
               "the_record_exercise_safari_json": "put back as it was found" + (f": it is of the run of {kept_summary['run_utc']} on the build of {kept_summary['layer_run_utc']}" if kept_summary else ": there was none"),
               "not_looked_at": "any control (nothing is clicked), the export, the online overlay, the map itself: exercise_decision.py covers them in Chrome and in WebKit"}
    p1, p2 = summary["part1_the_unchanged_scripts_main"], summary["part2_the_decision_view"]
    print(f"\nPART 1: {p1['addresses_as_expected']} of {p1['addresses_tried']} addresses showed what they should; {p1['units_opened_by_address']} units; {p1['values_found']} of {p1['values_compared']} values in the page's text"
          f"\nPART 2: {p2['addresses_as_expected']} of {p2['addresses_tried']} addresses showed what they should; {len(units)} units opened by address; {found} of {of} lines of 'why this tier' are in the page's text, in order; "
          f"{len(lists)} lists read in full; {len(cells_seen)} pairs of cell and window seen")
    json.dump({"summary": summary, "part1": part1, "part2": {"steps": steps2, "units": units}}, open(ROOT / "60_layer" / "exercise_decision_safari.json", "w", encoding="utf-8"), indent=1, default=str)
    ok = rc1 == 0 and p2["addresses_as_expected"] == p2["addresses_tried"] and found == of and len({c for c, _ in cells_seen}) == 6
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
