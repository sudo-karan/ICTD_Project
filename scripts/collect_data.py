#!/usr/bin/env python3
"""
collect_data.py - download the public datasets listed in data_manifest.csv into one folder.

  python collect_data.py --list                      # show what would be fetched, with sizes and browser links
  python collect_data.py --dest ~/ictd_data          # everything except the two 1 GB pan-India boundary files
  python collect_data.py --dest ~/ictd_data --only nrega_s3 boundaries
  python collect_data.py --dest ~/ictd_data --only boundaries_big        # the 0.8 GB + 1.1 GB files, on request

Groups: cfr, nrega_s3, nrega_mis, adi, shrug, boundaries, boundaries_big, docs.
Rows of kind manual / gee / git / delivered are never downloaded; --list prints where they live.

Google Drive files: uses the `gdown` package if it is installed (pip install gdown), otherwise a
standard-library fallback. Everything else is standard library.

STATUS: written on 2026-10-04 in a sandbox that cannot reach Google Drive or S3. The HTTP/S3 path and the
Drive fallback's page-parsing were exercised against a local mock server only; neither has been run
against the live services. Every finished file is size-checked against the manifest, so a wrong or
truncated download is reported rather than silently kept.
"""
import argparse, csv, datetime, hashlib, os, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = "Mozilla/5.0 (compatible; ictd-data-collector/1.0)"
GDRIVE_BASE = os.environ.get("ICTD_GDRIVE_BASE", "https://drive.usercontent.google.com/download")
DEFAULT_SKIP = {"boundaries_big"}
CHUNK = 1 << 20


def find_manifest():
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in ("data_manifest.csv", "../00_raw/data_manifest.csv", "../data_manifest.csv",
                "00_raw/data_manifest.csv"):
        p = os.path.join(here, rel)
        if os.path.exists(p):
            return os.path.normpath(p)
    sys.exit("data_manifest.csv not found; looked next to this script, in ../00_raw/ and one level up")


def browser_link(row):
    if row["kind"] == "gdrive_file":
        return "https://drive.google.com/file/d/%s/view" % row["ref"]
    return row["ref"]


def stream_to(resp, tmp, mode, expect_total, label):
    done = os.path.getsize(tmp) if mode == "ab" and os.path.exists(tmp) else 0
    t0 = time.time(); last = 0
    with open(tmp, mode) as fh:
        while True:
            buf = resp.read(CHUNK)
            if not buf:
                break
            fh.write(buf); done += len(buf)
            if time.time() - last > 2:
                last = time.time()
                pct = " %5.1f%%" % (100.0 * done / expect_total) if expect_total else ""
                sys.stdout.write("\r    %s %8.1f MB%s" % (label, done / 1e6, pct)); sys.stdout.flush()
    sys.stdout.write("\r    %s %8.1f MB in %.0f s\n" % (label, done / 1e6, time.time() - t0))
    return done


def http_download(url, out, expect):
    """Plain HTTPS GET with resume. Used for S3 and ordinary web files."""
    tmp = out + ".part"
    have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    headers = {"User-Agent": UA}
    if have:
        headers["Range"] = "bytes=%d-" % have
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120)
    except urllib.error.HTTPError as e:
        if e.code == 416 and have:            # range not satisfiable: the .part file is already complete
            os.replace(tmp, out); return
        raise
    mode = "ab" if (have and resp.status == 206) else "wb"   # a server that ignores Range sends 200: start again
    stream_to(resp, tmp, mode, expect, os.path.basename(out))
    os.replace(tmp, out)


def gdrive_download(file_id, out, expect):
    try:
        import gdown                                              # preferred: handles Drive's interstitial pages
        tmp = out + ".part"
        got = gdown.download(id=file_id, output=tmp, quiet=False, resume=True)
        if not got or not os.path.exists(tmp):
            raise RuntimeError("gdown returned nothing (file not public, or Drive download quota exceeded)")
        os.replace(tmp, out); return
    except ImportError:
        pass
    def _open(extra=None):
        q = {"id": file_id, "export": "download", "confirm": "t"}
        q.update(extra or {})
        return urllib.request.urlopen(urllib.request.Request(GDRIVE_BASE + "?" + urllib.parse.urlencode(q), headers={"User-Agent": UA}), timeout=120)
    resp = _open()
    if resp.headers.get("Content-Type", "").lower().startswith("text/html"):
        page = resp.read(400000).decode("utf-8", "replace")
        hidden = dict(re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', page))
        if "uuid" not in hidden:
            raise RuntimeError("Drive returned a web page, not the file (not public, or the download quota for this file is "
                               "exhausted). Open https://drive.google.com/file/d/%s/view in a signed-in browser instead." % file_id)
        resp = _open({k: v for k, v in hidden.items() if k in ("uuid", "at", "confirm")})
        if resp.headers.get("Content-Type", "").lower().startswith("text/html"):
            raise RuntimeError("Drive still returned a web page after confirmation; download this file in a browser.")
    tmp = out + ".part"
    stream_to(resp, tmp, "wb", expect, os.path.basename(out))
    os.replace(tmp, out)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()


def size_verdict(row, got):
    if not row["bytes"]:
        return "size not in manifest"
    exp = int(row["bytes"])
    if row["bytes_exact"] == "Y":
        return "size matches manifest" if got == exp else "SIZE DIFFERS from manifest (%d expected) - source updated, or download incomplete" % exp
    return "size plausible" if abs(got - exp) <= 0.1 * exp else "SIZE far from the approximate figure in the manifest (%d)" % exp


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", default="./00_raw")
    ap.add_argument("--only", nargs="*", help="groups to fetch (default: all except boundaries_big)")
    ap.add_argument("--list", action="store_true", help="print the plan and exit")
    ap.add_argument("--force", action="store_true", help="re-download files that already exist with the expected size")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(find_manifest(), encoding="utf-8")))
    groups = sorted({r["group"] for r in rows})
    if a.only:
        unknown = set(a.only) - set(groups)
        if unknown:
            sys.exit("unknown group(s) %s; available: %s" % (sorted(unknown), groups))
    want = set(a.only) if a.only else set(groups) - DEFAULT_SKIP
    todo = [r for r in rows if r["group"] in want and r["kind"] in ("gdrive_file", "s3", "http")]
    other = [r for r in rows if r["group"] in want and r["kind"] not in ("gdrive_file", "s3", "http")]
    total = sum(int(r["bytes"]) for r in todo if r["bytes"])
    print("%d files to fetch, about %.2f GB, into %s" % (len(todo), total / 1e9, os.path.abspath(os.path.expanduser(a.dest))))
    if a.list:
        for r in todo:
            print("  [%s] %-34s %8s MB  %s" % (r["group"], r["item_id"], ("%.1f" % (int(r["bytes"]) / 1e6)) if r["bytes"] else "?", browser_link(r)))
        print("\nNot downloadable by script (open by hand):")
        for r in other:
            print("  [%s/%s] %s\n        %s" % (r["group"], r["kind"], r["title"], r["ref"]))
        return
    dest = os.path.abspath(os.path.expanduser(a.dest)); os.makedirs(dest, exist_ok=True)
    log_path = os.path.join(dest, "download_log.csv"); new_log = not os.path.exists(log_path)
    ok = fail = skipped = 0
    with open(log_path, "a", newline="", encoding="utf-8") as lf:
        log = csv.writer(lf)
        if new_log:
            log.writerow(["utc_time", "item_id", "source", "path", "bytes", "sha256", "verdict"])
        for i, r in enumerate(todo, 1):
            out = os.path.join(dest, r["dest"]); os.makedirs(os.path.dirname(out), exist_ok=True)
            exp = int(r["bytes"]) if r["bytes"] else None
            print("[%d/%d] %s" % (i, len(todo), r["item_id"]))
            if os.path.exists(out) and not a.force and (exp is None or r["bytes_exact"] != "Y" or os.path.getsize(out) == exp):
                print("    already present, skipping"); skipped += 1; continue
            try:
                if r["kind"] == "gdrive_file":
                    gdrive_download(r["ref"], out, exp)
                else:
                    http_download(r["ref"], out, exp)
                got = os.path.getsize(out); verdict = size_verdict(r, got)
                print("    " + verdict)
                log.writerow([datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), r["item_id"], browser_link(r), r["dest"], got, sha256(out), verdict]); lf.flush()
                ok += 1
            except Exception as e:                                   # keep going; report at the end
                print("    FAILED: %s" % e); fail += 1
                log.writerow([datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), r["item_id"], browser_link(r), r["dest"], "", "", "FAILED: %s" % e]); lf.flush()
    print("\ndone: %d downloaded, %d already present, %d failed. Log: %s" % (ok, skipped, fail, log_path))
    if any(r["group"] == "nrega_s3" for r in todo):
        print("next: python aggregate_nrega_assets.py --dest %s" % a.dest)
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
