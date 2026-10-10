#!/usr/bin/env python3
"""The public site of the shared copy, checked as it is served. Publishes nothing.

    .venv/bin/python scripts/check_pages_live.py [--wait MINUTES]

The copy of the layer that is made to be passed on (`70_share/odisha_forest_decision_layer/`, built and gated by
`scripts/07_build_share.py` and `scripts/exercise_share.py`) is published by the project owner at ADDRESS: GitHub
Pages, from the branch `gh-pages` of `sudo-karan/ICTD_Project`, which holds the copy's three files and an empty
`.nojekyll` and nothing else (his decision of 11 October 2026; the push is made by a script of his, outside this
repository's branches). This script reads the address and checks what it serves. It runs in the main environment.

What it checks:
  1. `index.html`, `data.js` and `README.txt`, fetched from the site, have the bytes and the SHA-256 that
     `70_share/share.provenance.json` records for the copy, and the files on disk are that build too;
  2. in a separate, headless Chrome with an empty profile, driven through the DevTools protocol by the driver the
     gate on the copy uses (`scripts/_browser_chrome.py`): the page becomes ready; its data holds 11,468 units (the
     owner's figure) and the map draws every one of them;
  3. the page logs no script error: no exception and no console error or warning;
  4. the browser's own log holds no error but this one kind: "Failed to load resource", once for each address asked
     for that the site answers with 404, and each of those must be a `favicon.ico`, the icon a browser asks every
     site for by itself. The site has no icon. Any other line in that log fails the check;
  5. every request made over http or https goes to the host of ADDRESS, and there is at least one.
The overlay box is not ticked here: in the copy it would ask for a file that is left out on purpose, which the gate
on the copy tests.

`--wait MINUTES` (default 0): before checking, ask the address for `index.html` every 15 seconds until it serves the
recorded bytes, for at most that long. A site that has just been published takes a minute or two to build.

Writes, into `70_share/` only:
  pages_live_check.json     the address, the time, the browser, each file as fetched, what the page did, and each check
                            (`check`, `expected`, `found`, `pass`); `passed` is true only if every check passed
  pages_publication.json    the address; the commit at the head of `gh-pages` on GitHub when the check ran (read with
                            `git ls-remote`, which changes nothing); the build time of the copy; the layer's build
                            time; and the check's result with the time it ran
The exit status is 0 only if every check passed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

ADDRESS = "https://sudo-karan.github.io/ICTD_Project/"
REPOSITORY = "https://github.com/sudo-karan/ICTD_Project.git"
BRANCH = "gh-pages"
UNITS_EXPECTED = 11468
NAME = "odisha_forest_decision_layer"
COPY, PROV = ROOT / "70_share" / NAME, ROOT / "70_share" / "share.provenance.json"
OUT_CHECK, OUT_PUBLICATION = ROOT / "70_share" / "pages_live_check.json", ROOT / "70_share" / "pages_publication.json"
FILES = ("index.html", "data.js", "README.txt")
HOST = urllib.parse.urlsplit(ADDRESS).hostname
sha = lambda b: hashlib.sha256(b).hexdigest()
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def fetch(name: str) -> dict:
    """One file of the site, as served now. The query string is there so that no cache hands back an older answer."""
    url = ADDRESS + name
    req = urllib.request.Request(url + f"?checked={int(time.time())}", headers={"User-Agent": "ictd-check-pages-live", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            body = r.read()
            return {"file": name, "address": url, "status": r.status, "bytes": len(body), "sha256": sha(body)}
    except urllib.error.HTTPError as e:
        return {"file": name, "address": url, "status": e.code, "bytes": None, "sha256": None}
    except Exception as e:                                        # no connection, a timeout: the check fails and says why
        return {"file": name, "address": url, "status": None, "bytes": None, "sha256": None, "error": f"{type(e).__name__}: {e}"[:200]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wait", type=float, default=0, metavar="MINUTES", help="poll the address for at most this long before checking")
    a = ap.parse_args()
    started = now()
    recorded = json.loads(PROV.read_text(encoding="utf-8"))
    want = recorded["the_copy"]["files"]
    checks = []

    def add(check, expected, found, ok):
        checks.append({"check": check, "expected": str(expected), "found": str(found), "pass": bool(ok)})
        print(("PASS  " if ok else "FAIL  ") + f"{check} | expected {expected} | found {found}", flush=True)

    on_disk = {n: {"bytes": (COPY / n).stat().st_size, "sha256": sha((COPY / n).read_bytes())} for n in FILES}
    add("the copy on disk is the build its provenance record describes (bytes and SHA-256 of its three files)", "3 of 3",
        f"{sum(on_disk[n] == {'bytes': want[n]['bytes'], 'sha256': want[n]['sha256']} for n in FILES)} of 3",
        sorted(want) == sorted(FILES) and all(on_disk[n] == {"bytes": want[n]["bytes"], "sha256": want[n]["sha256"]} for n in FILES))

    polled, deadline = 0, time.time() + 60 * a.wait
    while a.wait and time.time() < deadline:
        polled += 1
        first = fetch("index.html")
        if first["status"] == 200 and first["sha256"] == want["index.html"]["sha256"]:
            break
        print(f"waiting: {ADDRESS}index.html answered {first['status']}" + ("" if first["sha256"] is None else " with other bytes than the record's"), flush=True)
        time.sleep(15)

    served = [fetch(n) for n in FILES]
    for f in served:
        f["as_recorded"] = f["bytes"] == want[f["file"]]["bytes"] and f["sha256"] == want[f["file"]]["sha256"]
        add(f"{f['address']}: the bytes and SHA-256 the site serves are those the provenance record gives for {f['file']}",
            f"{want[f['file']]['bytes']} bytes, sha256 {want[f['file']]['sha256'][:16]}",
            f"HTTP {f['status']}; {f['bytes']} bytes, sha256 {(f['sha256'] or 'none')[:16]}" + (f"; {f['error']}" if f.get("error") else ""), f["status"] == 200 and f["as_recorded"])

    page = {"opened": ADDRESS}
    try:
        from _browser_chrome import Chrome                        # the driver the gate on the copy uses
        c = Chrome(tempfile.mkdtemp(prefix="ictd_chrome_profile_"), port=9341)
        try:
            page["browser"] = c.version
            page["ready_after_seconds"] = c.open(ADDRESS, wait_s=600)
            b = c.js("(function(){var n=0; ICTD_MAP.eachLayer(function(l){ if(l._u!==undefined){n++;} }); return {units: (window.ICTD_LAYER.id || []).length, drawn: n};})()")
            time.sleep(2.0)                                       # anything the page asks for late is still counted
            c.js("1")                                             # reads the events that have arrived since
            page.update({"units_in_the_data": b["units"], "units_drawn": b["drawn"], "script_errors": list(c.errors or []), "requests": list(c.requests)})
        finally:
            c.close()
    except Exception as e:
        page["could_not_be_opened"] = f"{type(e).__name__}: {e}"[:300]
    if "could_not_be_opened" in page:
        add(f"{ADDRESS} opened in headless Chrome and became ready", "ready", page["could_not_be_opened"], False)
    else:
        add(f"{ADDRESS} opened in headless Chrome and became ready", "ready", f"ready after {page['ready_after_seconds']} s, in {page['browser']}", True)
        add("units in the page's data, and units drawn on the map", f"{UNITS_EXPECTED} and {UNITS_EXPECTED}", f"{page['units_in_the_data']} and {page['units_drawn']}",
            page["units_in_the_data"] == UNITS_EXPECTED and page["units_drawn"] == UNITS_EXPECTED)
        over_network = [u for u in page["requests"] if u.split(":", 1)[0] in ("http", "https")]
        log_lines = [e for e in page["script_errors"] if e.startswith("log: ")]
        of_scripts = [e for e in page["script_errors"] if not e.startswith("log: ")]
        page["script_errors"], page["errors_in_the_browsers_log"] = of_scripts, log_lines
        add("script errors the page logged (exceptions, console errors and warnings)", 0, f"{len(of_scripts)}" + (": " + " | ".join(of_scripts[:3]) if of_scripts else ""), not of_scripts)
        answers = {}
        for u in sorted(set(over_network)):                       # what the site answers for each address the page or the browser asked for
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ictd-check-pages-live"}), timeout=180) as r:
                    answers[u] = r.status
                    r.read()
            except urllib.error.HTTPError as e:
                answers[u] = e.code
            except Exception:
                answers[u] = None
        page["status_of_each_address_asked_for"] = answers
        not_found = sorted(u for u, s in answers.items() if s == 404)
        only_icons = all(urllib.parse.urlsplit(u).path.rsplit("/", 1)[-1] == "favicon.ico" for u in not_found)
        add("errors in the browser's own log, against the addresses asked for that the site answers with 404 (a browser asks every site for /favicon.ico by itself; the site has none)",
            "none but one 'Failed to load resource' for each favicon.ico the site does not have",
            f"{len(log_lines)} line(s)" + (": " + " | ".join(log_lines[:3]) if log_lines else "") + f"; answered 404: {', '.join(not_found) or 'nothing'}",
            all("Failed to load resource" in e and "404" in e for e in log_lines) and len(log_lines) == len(not_found) and only_icons
            and all(s in (200, 404) for s in answers.values()))
        elsewhere = sorted({u for u in over_network if urllib.parse.urlsplit(u).hostname != HOST or not u.startswith("https://")})
        page["requests_over_the_network"] = len(over_network)
        page["requests_to_another_host"] = elsewhere
        page["files_asked_for"] = sorted({urllib.parse.urlsplit(u).path for u in over_network})
        add(f"requests the page made over http or https, and those of them that did not go to https://{HOST}", "at least one, and none elsewhere",
            f"{len(over_network)} ({', '.join(page['files_asked_for'])}); elsewhere: {len(elsewhere)}" + (": " + ", ".join(elsewhere[:4]) if elsewhere else ""),
            len(over_network) >= 1 and not elsewhere)

    passed = all(x["pass"] for x in checks)
    record = {"script": "scripts/check_pages_live.py", "run_utc": started, "address": ADDRESS, "polled_before_checking": polled,
              "how_the_page_was_driven": "a separate, headless Chrome with an empty profile, through Chrome's DevTools protocol (scripts/_browser_chrome.py, the driver of the gate on the copy)",
              "copy_run_utc": recorded["run_utc"], "layer_run_utc": recorded["layer_run_utc"], "files_as_served": served, "the_page": page, "checks": checks,
              "checks_passed": sum(x["pass"] for x in checks), "checks_made": len(checks), "passed": passed}
    OUT_CHECK.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    head = subprocess.run(["git", "ls-remote", "--heads", REPOSITORY, BRANCH], capture_output=True, text=True, cwd=ROOT, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    commit = head.stdout.split()[0] if head.returncode == 0 and head.stdout.strip() else None
    OUT_PUBLICATION.write_text(json.dumps({
        "what": "The shared copy of the layer as published by the project owner (his decision of 11 October 2026): where, from which commit, which build, and what the check of the live site found.",
        "address": ADDRESS, "repository": REPOSITORY, "branch": BRANCH, "gh_pages_commit_when_checked": commit,
        "what_the_branch_holds": "index.html, data.js and README.txt of 70_share/odisha_forest_decision_layer/, and an empty .nojekyll",
        "copy_built_utc": recorded["run_utc"], "layer_built_utc": recorded["layer_run_utc"],
        "files": {n: {"bytes": want[n]["bytes"], "sha256": want[n]["sha256"]} for n in FILES},
        "live_check": {"record": "70_share/pages_live_check.json", "run_utc": started, "checks_passed": record["checks_passed"], "checks_made": record["checks_made"], "passed": passed}},
        indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{record['checks_passed']} of {record['checks_made']} checks passed; gh-pages is at {commit}; wrote 70_share/pages_live_check.json and 70_share/pages_publication.json")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
