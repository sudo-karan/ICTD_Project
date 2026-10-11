#!/usr/bin/env bash
# Publish the shared copy of the layer at https://sudo-karan.github.io/ICTD_Project/
#
#   bash scripts/publish_site.sh [--no-push]
#
# Run it yourself, from the repository, with main checked out and nothing uncommitted. It:
# 1. checks that the three files of 70_share/odisha_forest_decision_layer/ are the gated build: each file's bytes and
#    sha256 must match 70_share/share.provenance.json, and the development index must not appear in index.html or
#    data.js;
# 2. copies them into site/, and commits that folder if it has changed;
# 3. pushes main to GitHub (no force), with any of its commits not yet there. With --no-push it stops before this.
# GitHub Actions then deploys site/ (.github/workflows/pages.yml), and the site changes a minute or two later.
# Check it afterwards: .venv/bin/python scripts/check_pages_live.py --wait 10
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
SRC="70_share/odisha_forest_decision_layer"
PROV="70_share/share.provenance.json"
PUSH=1
case "${1:-}" in
  "") ;;
  --no-push) PUSH=0 ;;
  *) echo "STOP: the only option is --no-push."; exit 1 ;;
esac

[ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] || { echo "STOP: check out main first."; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "STOP: commit or set aside the changes first, so that the commit holds site/ and nothing else."; exit 1; }

# 1. The files must be the gated build.
python3 - "$SRC" "$PROV" <<'PY'
import hashlib, json, pathlib, sys
src, prov = pathlib.Path(sys.argv[1]), json.load(open(sys.argv[2]))
files = prov["the_copy"]["files"]
bad = [n for n, r in files.items()
       if (src / n).stat().st_size != r["bytes"]
       or hashlib.sha256((src / n).read_bytes()).hexdigest() != r["sha256"]]
extra = sorted({p.name for p in src.iterdir() if not p.name.startswith(".")} - set(files))  # .DS_Store etc. ignored
if bad or extra:
    sys.exit(f"STOP: differ from the provenance record: {bad}; not in the record: {extra}")
for n in ("index.html", "data.js"):
    t = (src / n).read_text(encoding="utf-8", errors="replace")
    if "adi_2011" in t or "development index" in t.lower():
        sys.exit(f"STOP: the development index appears in {n}")
print("OK: the three files are the gated build of", prov["run_utc"])
PY
BUILT="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['run_utc'])" "$PROV")"

# 2. site/ takes the copy, and holds nothing else.
mkdir -p site
cp "$SRC/index.html" "$SRC/data.js" "$SRC/README.txt" site/
git add site
EXTRA="$(git ls-files site | grep -v -x -E 'site/(index\.html|data\.js|README\.txt)' || true)"
[ -z "$EXTRA" ] || { git reset -q -- site; echo "STOP: site/ holds other files: $EXTRA"; exit 1; }
if git diff --cached --quiet; then
  echo "site/ already holds the copy built $BUILT."
else
  git commit --quiet -m "Publish the shared copy of the layer, built $BUILT"
  echo "Committed site/: the copy built $BUILT."
fi

# 3. Push main, naming the branch in full.
if [ "$PUSH" = 0 ]; then
  echo "Not pushed (--no-push)."
  exit 0
fi
git push origin main:refs/heads/main
echo
echo "Pushed main. GitHub Actions deploys site/ in a minute or two: https://sudo-karan.github.io/ICTD_Project/"
