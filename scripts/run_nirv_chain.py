#!/usr/bin/env python3
"""
Runs what is left of the NIRv column, unattended, and watches what it costs. Not a stage: it runs the stage-1
NIRv scripts in order and writes only its own logs (logs/, which git ignores).

    nohup .venv/bin/python scripts/run_nirv_chain.py --units 10_units/units.gpkg > /dev/null 2>&1 &
    .venv/bin/python scripts/run_nirv_chain.py --self-test          (no Earth Engine: checks the decisions on made-up task lists)

NIRv IS A BACKGROUND COLUMN (ruling of 7 Oct 2026): nothing in stage 1 waits for this. When it ends,
degradation_by_unit.csv has its NIRv columns filled and nirv_status "built".

WHAT IT DOES, in order. It decides from what Earth Engine holds, never from what an earlier process left behind,
so it can be started again at any point.
  1. Waits while tile exports of the observations are queued or running. If a tile's export FAILED or was
     cancelled and nothing is queued for it, it STOPS: the blocks of yearly values were queued behind the tiles
     (6 Oct 2026), so a block would be computed without that tile. It resubmits nothing and cancels nothing.
  2. Runs 02_export_nirv_observations.py once all tiles exist: it finds them, starts nothing, and writes the
     scene list and its record.
  3. Waits while block exports are queued or running. As soon as block PROBE_BLOCK exists it runs
     check_nirv_blocks.py --probe on it (does a block queued before its tiles existed hold them?) and stops if not.
  4. Runs 02_export_nirv_yearly.py (finds the blocks, writes its record), then check_nirv_blocks.py (every block
     started after the tiles under it had finished; same pass-days), then 02_build_nirv.py, then
     02_assemble_degradation.py.
Its log, logs/nirv_chain.log, ends with a line that says FINISHED or STOPPED, whatever happens short of the
machine losing power - including being killed.

A STEP THAT FAILS. If its log holds "still running" (tasks of an earlier attempt), or check_nirv_blocks.py says
"not decided yet", it waits five minutes and asks again, without limit. If it ended in a Python traceback and not
at a check (a dropped connection, a request that timed out) it is run again, three times running at most: the
scripts take up the tables already computed. Anything else - a failed check, a failed batch task, a refusal - is
NOT run again: it has to be looked at. A step whose log has not grown for 45 minutes is taken to hang and is
killed, which counts as a failure of the second kind.

THE COST WATCH. Every poll, each RUNNING batch task of this pipeline is compared with a limit of about six times
the largest cost measured for its kind (EECU-seconds: a tile of observations 1,831; a block of yearly values 392
per million cells, about 25,000 for the largest; a group of per-unit sums 13,758, first design, 1,432 units; the
point reads have not been measured). A task over its limit is cancelled, the chain stops, and for the per-unit
sums and point reads the tasks of the same kind still pending are cancelled with it (they are the same
computation). This is the stop that was missing on 6 October, when one group of sums used 380,962
EECU-seconds before it was cancelled by hand. After a stop the watch goes on for as long as tasks are queued.

logs/STOP_THE_CHAIN (written here on a cost stop, or by hand) keeps the chain from starting until it is removed.

Needs earthengine-api, geopandas; scripts/_ee_units.py and the NIRv scripts.
"""
import argparse, datetime as dt, importlib.util, os, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
LOG, PIDFILE, STOPFILE = LOGS / "nirv_chain.log", LOGS / "nirv_chain.pid", LOGS / "STOP_THE_CHAIN"
PYTHON = sys.executable
POLL_S, STEP_POLL_S, WAIT_S, STALE_S, TRIES = 300, 60, 300, 45 * 60, 3
PROBE_BLOCK = "b_0820_0180"            # the first block in the queue with tiles under it that did not exist when the blocks were queued
LIMITS = {"nirvobs_": 20000.0, "nirvstd_block_": 150000.0, "nirv_points_": 30000.0, "nirvraw_group_": 80000.0, "nirvstd_group_": 80000.0}
SIBLINGS = ("nirv_points_", "nirvraw_group_", "nirvstd_group_")           # kinds whose pending tasks are cancelled with one that overran
LIVE = ("PENDING", "RUNNING")


def stamp():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def say(message):
    LOGS.mkdir(exist_ok=True)
    line = f"{stamp()} {message}"
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


# ---- decisions, as plain functions of what Earth Engine reports (tested by --self-test) ------------------------------------
def queue_state(ops, prefix, wanted, present):
    """For one kind of export (description prefix): which of the wanted ids exist, are queued, failed, or have nothing."""
    latest = {}
    for o in ops:
        m = o.get("metadata", {})
        d = str(m.get("description", ""))
        if d.startswith(prefix):
            i = d[len(prefix):]
            key = m.get("createTime", "")
            if i not in latest or key > latest[i][0]:
                latest[i] = (key, m.get("state"))
    live = sorted(i for i in wanted if any(str(o.get("metadata", {}).get("description", "")) == prefix + i and o["metadata"].get("state") in LIVE for o in ops))
    failed = sorted(i for i in wanted if i not in present and i not in live and i in latest and latest[i][1] in ("FAILED", "CANCELLED", "CANCELLING"))
    nothing = sorted(i for i in wanted if i not in present and i not in live and i not in latest)
    return {"wanted": len(wanted), "present": sorted(set(wanted) & set(present)), "live": live, "failed": failed, "nothing": nothing}


def over_limit(ops, stem):
    """[(description, operation name, EECU-seconds used, limit)] for running tasks of this pipeline that are over their limit."""
    out = []
    for o in ops:
        m = o.get("metadata", {})
        d = str(m.get("description", ""))
        if m.get("state") != "RUNNING" or not d.startswith(f"ictd_{stem}_"):
            continue
        kind = d[len(f"ictd_{stem}_"):]
        limit = next((v for k, v in LIMITS.items() if kind.startswith(k)), None)
        used = float(m.get("batchEecuUsageSeconds") or 0)
        if limit is not None and used > limit:
            out.append((d, o["name"], used, limit))
    return out


def verdict(code, text):
    """What to do with a step that ended: 'ok', 'wait' (ask again), 'retry' (it broke, not at a check), or 'stop'."""
    if code == 0:
        return "ok"
    if "still running" in text or code == 3:
        return "wait"
    deliberate = any(k in text for k in ("FAILED at", "NOT ASSEMBLED", "FAIL  "))
    return "retry" if ("Traceback (most recent call last)" in text or code < 0) and not deliberate else "stop"


def self_test():
    op = lambda d, state, created="2026-10-06T04:30:00Z", used=0: {"name": "operations/" + d, "metadata": {"description": d, "state": state, "createTime": created, "batchEecuUsageSeconds": used}}
    ops = [op("ictd_units_nirvobs_t_1", "SUCCEEDED"), op("ictd_units_nirvobs_t_2", "PENDING"), op("ictd_units_nirvobs_t_3", "FAILED"),
           op("ictd_units_nirvobs_t_4", "CANCELLED", "2026-10-06T03:00:00Z"), op("ictd_units_nirvobs_t_4", "RUNNING", "2026-10-06T04:30:00Z", 30000),
           op("ictd_units_nirvobs_t_5", "CANCELLED", "2026-10-06T03:00:00Z"), op("ictd_units_nirvobs_t_5", "SUCCEEDED", "2026-10-06T04:30:00Z"),
           op("ictd_units_nirvstd_block_b_1", "RUNNING", used=120000), op("ictd_units_nirvstd_group_0", "RUNNING", used=90000), op("ictd_other_x", "RUNNING", used=9e9)]
    s = queue_state(ops, "ictd_units_nirvobs_", ["t_1", "t_2", "t_3", "t_4", "t_5", "t_6"], {"t_1", "t_5"})
    assert s["present"] == ["t_1", "t_5"] and s["live"] == ["t_2", "t_4"] and s["failed"] == ["t_3"] and s["nothing"] == ["t_6"], s
    assert queue_state(ops, "ictd_units_nirvobs_", ["t_3"], {"t_3"})["failed"] == []                    # exported again since: it exists
    over = over_limit(ops, "units")
    assert [x[0] for x in over] == ["ictd_units_nirvobs_t_4", "ictd_units_nirvstd_group_0"], over        # the block is under its limit; another pipeline's task is not ours
    assert verdict(0, "") == "ok" and verdict(1, "Earth Engine is still running 13 block exports") == "wait" and verdict(3, "NOT DECIDED YET") == "wait"
    assert verdict(1, "Traceback (most recent call last):\n ConnectionError") == "retry" and verdict(-9, "") == "retry"
    assert verdict(1, "FAILED at checking the stored values") == "stop" and verdict(1, "NOT ASSEMBLED:") == "stop" and verdict(1, "some refusal") == "stop"
    assert verdict(1, "Traceback (most recent call last):\n ...\nFAILED at the zonal-statistics tasks") == "stop"
    print("self-test passed: queue states, cost limits and the verdict on a failed step")


# ---- the chain ---------------------------------------------------------------------------------------------------------------
class Chain:
    def __init__(self, units, project):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ee, _ee_units as eu
        self.ee, self.eu = ee, eu
        self.units, self.stem = units, Path(units).stem
        self.project = eu.init(project)
        spec = importlib.util.spec_from_file_location("yearly", Path(__file__).with_name("02_export_nirv_yearly.py"))
        Y = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(Y)
        self.tiles = [t[0] for t in Y.OBS.tiles_over(units)[0]]
        self.blocks = [b[0] for b in Y.blocks_over(units)[0]]
        self.child, self.stopped, self.last_line = None, False, {}

    def ops(self):
        try:
            return self.ee.data.listOperations()
        except Exception as e:                               # a dropped connection must not end the chain
            say(f"could not list Earth Engine's tasks ({type(e).__name__}); asking again")
            return None

    def present(self, collection):
        try:
            return {a["name"].split("/")[-1] for a in self.ee.data.listAssets({"parent": f"projects/{self.project}/assets/ictd/{collection}"}).get("assets", [])}
        except Exception:
            return None

    def watch(self, ops):
        """Cancel any task over its limit; True if one was."""
        hit = over_limit(ops, self.stem)
        for d, name, used, limit in hit:
            try:
                self.ee.data.cancelOperation(name)
                note = f"COST STOP: {d} had used {used:,.0f} EECU-seconds, limit {limit:,.0f}; cancelled"
            except Exception as e:
                note = f"COST STOP: {d} had used {used:,.0f} EECU-seconds, limit {limit:,.0f}; COULD NOT CANCEL IT ({type(e).__name__}) - cancel it by hand"
            say(note)
            with open(STOPFILE, "a", encoding="utf-8") as fh:
                fh.write(f"{stamp()} {note}\n")
            kind = d[len(f"ictd_{self.stem}_"):]
            if kind.startswith(SIBLINGS):
                for o in ops:
                    m = o.get("metadata", {})
                    if m.get("state") == "PENDING" and str(m.get("description", ""))[len(f"ictd_{self.stem}_"):].startswith(SIBLINGS):
                        try:
                            self.ee.data.cancelOperation(o["name"])
                            say(f"  also cancelled the pending {m['description']} (the same computation)")
                        except Exception:
                            say(f"  could not cancel the pending {m['description']}")
        return bool(hit)

    def stop(self, why):
        if self.child is not None and self.child.poll() is None:
            self.child.terminate()
        self.stopped = True
        say(f"{why} STOPPED")
        while True:                                          # the watch outlives the chain while anything of ours is queued
            ops = self.ops()
            if ops is not None:
                self.watch(ops)
                live = [o for o in ops if o.get("metadata", {}).get("state") in LIVE and str(o["metadata"].get("description", "")).startswith(f"ictd_{self.stem}_")]
                if not live:
                    break
                self.note("watch", f"the chain has stopped; still watching the cost of {len(live)} queued or running tasks")
            time.sleep(POLL_S)
        say("nothing of this pipeline is queued any more; the watch ends. (the chain STOPPED above)")
        sys.exit(1)

    def note(self, key, message, every_s=3600):
        """Say something at most once an hour unless it changes."""
        was = self.last_line.get(key)
        if was is None or was[0] != message or time.time() - was[1] > every_s:
            say(message)
            self.last_line[key] = (message, time.time())

    def wait_for(self, what, prefix, wanted, collection, each_poll=None):
        while True:
            ops, have = self.ops(), self.present(collection)
            if ops is None or have is None:
                time.sleep(STEP_POLL_S)
                continue
            if self.watch(ops):
                self.stop("a task went over its cost limit (see above and logs/STOP_THE_CHAIN).")
            s = queue_state(ops, prefix, wanted, have)
            self.note(what, f"{what}: {len(s['present'])} of {s['wanted']} exported, {len(s['live'])} queued or running")
            if s["failed"] or s["nothing"]:
                self.stop(f"{what}: the export of {s['failed'] + s['nothing']} failed, was cancelled, or was never queued, and nothing is queued for it. Nothing was resubmitted and nothing cancelled: "
                          "anything queued behind it runs without it. This needs a decision.")
            if each_poll is not None:
                each_poll(have)
            if len(s["present"]) == s["wanted"] and not s["live"]:
                return
            time.sleep(POLL_S)

    def step(self, label, stem, command):
        tries = 0
        while True:
            if STOPFILE.exists():
                self.stop(f"{label}: not run, logs/STOP_THE_CHAIN exists.")
            log = LOGS / f"{stem}_{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}.log"
            say(f"{label}: started, log {log.relative_to(ROOT)}")
            with open(log, "w", encoding="utf-8") as fh:
                self.child = subprocess.Popen(command, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUNBUFFERED": "1"})
            hung = False
            while self.child.poll() is None:
                time.sleep(STEP_POLL_S)
                ops = self.ops()
                if ops is not None and self.watch(ops):
                    self.stop(f"{label}: a task went over its cost limit (see above and logs/STOP_THE_CHAIN).")
                if time.time() - log.stat().st_mtime > STALE_S and self.child.poll() is None:
                    self.child.kill()
                    hung = True
            code = self.child.wait()
            text = log.read_text(encoding="utf-8", errors="replace")
            with open(log, "a", encoding="utf-8") as fh:
                fh.write(f"exit {code}" + (" (killed: the log had not grown for 45 minutes)\n" if hung else "\n"))
            what = verdict(code, text)
            if what == "ok":
                say(f"{label}: done")
                return
            if what == "wait":
                tries = 0
                self.note(label, f"{label}: not yet (tasks of an earlier attempt are still running, or it cannot be decided yet); asking again every five minutes")
                time.sleep(WAIT_S)
                continue
            if what == "retry" and tries + 1 < TRIES:
                tries += 1
                say(f"{label}: ended with exit {code}" + (" after hanging" if hung else "") + f" and not at a check (see {log.name}); running it again in five minutes (attempt {tries + 1} of {TRIES})")
                time.sleep(WAIT_S)
                continue
            self.stop(f"{label}: ended with exit {code}" + (" three times running, not at a check" if what == "retry" else " at a failed check, a failed task or a refusal") + f" (see {log.relative_to(ROOT)}); not run again.")

    def run(self):
        py, u = [PYTHON], ["--units", self.units]
        say(f"chain {os.getpid()} started for {self.units}: {len(self.tiles)} tiles, {len(self.blocks)} blocks; project {self.project}")
        self.wait_for("tiles of observations", f"ictd_{self.stem}_nirvobs_", self.tiles, f"nirv_obs_{self.stem}")
        self.step("02_export_nirv_observations.py (all tiles exist: writes the scene list and its record)", "nirv_observations", py + ["scripts/02_export_nirv_observations.py"] + u)
        probed = {"done": False, "tries": 0}

        def probe(have):
            if not probed["done"] and PROBE_BLOCK in have:
                probed["tries"] += 1
                log = LOGS / f"nirv_probe_{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}.log"
                r = subprocess.run(py + ["scripts/check_nirv_blocks.py", "--probe", PROBE_BLOCK] + u, cwd=ROOT, capture_output=True, text=True)
                log.write_text(r.stdout + r.stderr + f"exit {r.returncode}\n", encoding="utf-8")
                last = (r.stdout.strip().splitlines() or [""])[-1]
                if r.returncode == 0:
                    probed["done"] = True
                    say(f"probe of block {PROBE_BLOCK}: passed. {last}")
                elif r.returncode == 1 and "FAILED at" in r.stderr:
                    self.stop(f"probe of block {PROBE_BLOCK}: FAILED (see {log.relative_to(ROOT)}): a block queued before its tiles existed does not hold them. Nothing was cancelled or exported again: "
                              "tell the project owner before doing either.")
                else:
                    probed["done"] = probed["tries"] >= 6               # asked again at the next polls; after six, the order check and the build's own gates remain
                    say(f"probe of block {PROBE_BLOCK}: not decided (exit {r.returncode}; see {log.relative_to(ROOT)}). {last}" + (" Not asked again." if probed["done"] else ""))

        self.wait_for("blocks of yearly values", f"ictd_{self.stem}_nirvstd_block_", self.blocks, f"nirv_std_{self.stem}", each_poll=probe)
        self.step("02_export_nirv_yearly.py (all blocks exist: writes its record)", "nirv_yearly", py + ["scripts/02_export_nirv_yearly.py"] + u)
        self.step("check_nirv_blocks.py (every block after the tiles under it)", "nirv_blocks_check", py + ["scripts/check_nirv_blocks.py"] + u)
        self.step("02_build_nirv.py", "nirv_build", py + ["scripts/02_build_nirv.py"] + u)
        self.step("02_assemble_degradation.py (fills the NIRv columns)", "assemble", py + ["scripts/02_assemble_degradation.py"] + u)
        say("every step ended with exit 0: degradation_by_unit.csv now carries the NIRv columns. FINISHED")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", help="the stage-0 layer, e.g. 10_units/units.gpkg")
    ap.add_argument("--project", help="Cloud project; default is the one in the Earth Engine credentials file")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.units:
        ap.error("--units is required")
    LOGS.mkdir(exist_ok=True)
    if PIDFILE.exists():
        try:
            os.kill(int(PIDFILE.read_text().strip()), 0)
            say(f"a second start was refused: the chain is already running as {PIDFILE.read_text().strip()}")
            sys.exit(3)
        except (OSError, ValueError):
            pass
    if STOPFILE.exists():
        say(f"not started: logs/STOP_THE_CHAIN exists ({STOPFILE.read_text().strip()[:300]}). Deal with what it says, remove it, start again. STOPPED")
        sys.exit(4)
    PIDFILE.write_text(str(os.getpid()))

    def on_signal(number, frame):
        say(f"chain {os.getpid()} was ended by signal {number}. STOPPED")
        PIDFILE.unlink(missing_ok=True)
        os._exit(1)

    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)
    try:
        subprocess.Popen(["caffeinate", "-s", "-w", str(os.getpid())])        # on mains power, hold off sleep while this runs; changes no setting
    except OSError:
        pass
    try:
        Chain(a.units, a.project).run()
    except SystemExit:
        raise
    except BaseException as e:
        say(f"the chain itself broke ({type(e).__name__}: {str(e)[:300]}). STOPPED")
        raise
    finally:
        PIDFILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
