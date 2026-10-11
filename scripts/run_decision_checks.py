#!/usr/bin/env python3
"""Runs every check of the layer on the build that is in 60_layer/, ONE AT A TIME, and keeps a record of every run it
makes - a run that fails included.

    python scripts/run_decision_checks.py [--leave-out safari --because "why"]

Why this script exists (9 Oct 2026). The records the checks write (60_layer/exercise_*.json) hold only the LAST run of
each. On 8 Oct one run of the layer's own WebKit exercise failed one step and the next two passed; nothing but a note made
by hand said so. And two browser checks run at the same time, or beside other heavy work, spoil each other. So the
checks are run from here, in one order, never two at once, and what each run did is written down as it happens.

Order: the two verifiers; the layer's own exercise in Chrome and in WebKit; the layer's Safari script, as written; the
decision view's exercise in Chrome and in WebKit; the Safari check by address. A browser check that does not pass is
run again, up to two more times, and EVERY run is recorded: how many runs a check needed is part of the result.

For each script it also records whether the file is byte for byte the one in the last commit (git), so that each record
is of committed code, and the sha256 of the file as it was run; and its own. Of the three checks of the regression gate
(the layer's own, from before the decision view), scripts/verify_layer.py is still unchanged. scripts/exercise_layer.py
and scripts/exercise_layer_safari.py were changed on 11 October 2026 only where they pinned reworded words, as listed in
docs/SITE_COPY.md (the Safari script in none of its own lines: it pins no reworded word itself, and what it expects of a
unit's panel comes from exercise_layer.py).
The browser exercises are given a temporary folder for their screenshots; it is not part of the record.

A pass may LEAVE OUT the two checks in the Safari application (--leave-out safari), and must then say why (--because): the
record names the checks that were not run and gives the reason, so that a pass without them cannot be read as a pass
with them. On 9 October 2026 the owner ruled that the batch applying his rulings makes no run in the Safari application.

Run it on a machine that is otherwise quiet. The overlay's steps need a connection. The Safari steps need the terminal's
leave to control Safari, and no other Safari window showing the layer.

One thing it does to Safari, and only this: before each run of a Safari check it closes any window that an EARLIER run
of these checks left open - a window whose address carries the scripts' own mark, 60_layer/index.html?exercise=<time>.
The layer's Safari script leaves its window open when it stops at its first reading, and then every later run of it
reads that left-over window instead of its own (Safari hands a window back by its title) and fails too: on 9 Oct 2026
that is what happened to the second run, until the left-over window was closed by hand. No other window is touched, and
Safari is not started for this. How many it closed is in the record of each run.

Output: 60_layer/decision_runs.json and nothing else of its own (each check writes its own record, as before). Exits 1
unless the last run of every check passed."""
import argparse, hashlib, json, re, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "60_layer" / "decision_runs.json"
PY = sys.executable
SHOTS = tempfile.mkdtemp(prefix="ictd_decision_runs_")
CHECKS = [  # name, script, arguments, is it a browser check (run again if it fails), is it one of the regression gate's three scripts (the layer's own, from before the decision view)
    ("verify_layer", "scripts/verify_layer.py", [], False, True),
    ("verify_decision", "scripts/verify_decision.py", [], False, False),
    ("exercise_layer in Chrome", "scripts/exercise_layer.py", ["chrome", SHOTS], True, True),
    ("exercise_layer in WebKit", "scripts/exercise_layer.py", ["webkit", SHOTS], True, True),
    ("exercise_layer_safari, as written", "scripts/exercise_layer_safari.py", [], True, True),
    ("exercise_decision in Chrome", "scripts/exercise_decision.py", ["chrome", SHOTS], True, False),
    ("exercise_decision in WebKit", "scripts/exercise_decision.py", ["webkit", SHOTS], True, False),
    ("exercise_decision_safari, by address", "scripts/exercise_decision_safari.py", [], True, False),
]
MOST = 3
MARK = "file://" + str(ROOT / "60_layer" / "index.html") + "?exercise="          # how the two Safari scripts mark the one window each opens
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def close_left_over():
    """Close the Safari windows an earlier run of the Safari checks left open: those whose address begins with the scripts' own mark, and no other. Returns how many; None if Safari is not running, did not answer in time,
    or answered with anything but "no such window" (then nothing more is tried). It would also close a marked window of a Safari check started by hand at that moment: do not run one beside this."""
    if subprocess.run(["pgrep", "-x", "Safari"], capture_output=True).returncode != 0:
        return None
    closed = 0
    for _ in range(10):
        try:
            r = subprocess.run(["osascript", "-e", f'tell application "Safari" to close (first document whose URL starts with "{MARK}")'], capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return None
        if r.returncode != 0:
            if "Invalid index" in r.stderr or "-1719" in r.stderr or "-1728" in r.stderr:      # Safari's answer when no such window is left
                break
            return None
        closed += 1
        time.sleep(1)
    return closed


def as_committed(script):
    """Is the file byte for byte the one in the last commit? None if git cannot say (the file is not in the commit)."""
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", script], capture_output=True)
    tracked = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"HEAD:{script}"], capture_output=True).returncode == 0
    return (r.returncode == 0) if tracked else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leave-out", choices=["safari"], help="leave out the two checks made in the Safari application")
    ap.add_argument("--because", default="", help="why they are left out: written into the record")
    a = ap.parse_args()
    if a.leave_out and not a.because.strip():
        sys.exit("--leave-out needs --because: the record must say why a check was not run")
    left_out = [c for c in CHECKS if a.leave_out == "safari" and "safari" in c[1]]
    checks = [c for c in CHECKS if c not in left_out]
    layer = json.load(open(ROOT / "60_layer" / "layer.provenance.json"))["run_utc"]
    record = {"script": "scripts/run_decision_checks.py", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "started_utc": now(), "layer_run_utc": layer, "one_at_a_time": True, "most_runs_of_a_check": MOST,
              "files_sha256": {f: hashlib.sha256((ROOT / "60_layer" / f).read_bytes()).hexdigest() for f in ("index.html", "data.js")},
              "checks_not_run_in_this_pass": [{"check": c[0], "script": c[1], "of_the_regression_gate": c[4], "why": a.because.strip()} for c in left_out], "checks": []}
    for name, script, args, browser, gate in checks:
        entry = {"check": name, "script": script, "arguments": [a for a in args if a != SHOTS], "of_the_regression_gate": gate, "file_is_as_committed": as_committed(script),
                 "file_sha256": hashlib.sha256((ROOT / script).read_bytes()).hexdigest(), "runs": []}
        for attempt in range(1, (MOST if browser else 1) + 1):
            left = close_left_over() if "safari" in script else None
            started = now()
            r = subprocess.run([PY, str(ROOT / script)] + args, capture_output=True, text=True, cwd=ROOT)
            lines = [l for l in (r.stdout + "\n" + r.stderr).splitlines() if l.strip()]
            entry["runs"].append({"run": attempt, "started_utc": started, "ended_utc": now(), "exit": r.returncode, "last_line": lines[-1][:600] if lines else "",
                                  "failed_lines": [l[:600] for l in lines if l.startswith("FAIL")][:10], "error": lines[-1][:300] if lines and (r.returncode not in (0, 1) or re.match(r"\w*(Error|Exception)\b", lines[-1]) or "Traceback (most recent call last)" in "\n".join(lines)) else ""}
                                 | ({"left_over_safari_windows_of_earlier_runs_closed_first": left} if "safari" in script else {}))
            print(f"{'PASS' if r.returncode == 0 else 'FAIL'}  {name}, run {attempt}: {entry['runs'][-1]['last_line'][:200]}", flush=True)
            json.dump(record | {"checks": record["checks"] + [entry], "unfinished": True}, open(OUT, "w", encoding="utf-8"), indent=1)      # written as it goes: a run cut short leaves what was done
            if r.returncode == 0:
                break
            time.sleep(3)
        entry["runs_made"], entry["runs_that_passed"] = len(entry["runs"]), sum(1 for x in entry["runs"] if x["exit"] == 0)
        entry["last_run_passed"] = entry["runs"][-1]["exit"] == 0
        record["checks"].append(entry)
        time.sleep(2)
    record["ended_utc"] = now()
    record["every_check_passed_on_its_last_run"] = all(e["last_run_passed"] for e in record["checks"])
    record["every_check_passed_on_its_first_run"] = all(e["runs"][0]["exit"] == 0 for e in record["checks"])
    json.dump(record, open(OUT, "w", encoding="utf-8"), indent=1)
    for c in left_out:
        print(f"NOT RUN  {c[0]}: {a.because.strip()}")
    print(f"\n{sum(e['last_run_passed'] for e in record['checks'])} of {len(record['checks'])} checks passed on their last run; "
          f"{sum(e['runs'][0]['exit'] == 0 for e in record['checks'])} on their first; record: 60_layer/decision_runs.json")
    return 0 if record["every_check_passed_on_its_last_run"] else 1


if __name__ == "__main__":
    sys.exit(main())
