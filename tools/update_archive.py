#!/usr/bin/env python3
"""Archive today's edition and keep the newest 30.

Usage (from the repository root, after index.html has been overwritten):
    python3 tools/update_archive.py 2026-11-27

Copies index.html to archive/<date>.html, rewrites editions.json (newest
first, at most 30 dates) and deletes archive pages that fell off the list.
The edition menu on every page reads editions.json, so no page needs editing.
"""
import json, re, shutil, sys
from pathlib import Path

KEEP = 30
root = Path(__file__).resolve().parent.parent
date = sys.argv[1] if len(sys.argv) > 1 else ""
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
    sys.exit("usage: update_archive.py YYYY-MM-DD")

index = root / "index.html"
if 'id="editions"' not in index.read_text(encoding="utf-8"):
    sys.exit("index.html is missing the edition menu block (id=\"editions\"); restore it before archiving")

archive = root / "archive"
archive.mkdir(exist_ok=True)
shutil.copyfile(index, archive / f"{date}.html")

listing = root / "editions.json"
try:
    dates = set(json.loads(listing.read_text(encoding="utf-8")))
except (FileNotFoundError, ValueError):
    dates = set()
dates.add(date)
dates = sorted((d for d in dates if (archive / f"{d}.html").exists()), reverse=True)[:KEEP]
listing.write_text(json.dumps(dates, indent=0) + "\n", encoding="utf-8")

for page in archive.glob("*.html"):
    if page.stem not in dates:
        page.unlink()
print(f"archived {date}; {len(dates)} editions listed, newest {dates[0]}, oldest {dates[-1]}")
