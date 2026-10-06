#!/usr/bin/env python3
"""Regenerate sitemap.xml from the page folders.

Every index.html (root and one folder deep) is listed, except pages marked noindex.
<lastmod> is the latest git commit touching the page or the data/images it shows,
so CI needs a full checkout (fetch-depth: 0).
"""
import datetime
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "sitemap.xml"
DOMAIN = (ROOT / "CNAME").read_text().strip() if (ROOT / "CNAME").exists() else "snowbotics.org"

# folder -> (changefreq, priority); "" is the home page. Unlisted pages get DEFAULT.
META = {
    "": ("monthly", "1.0"),
    "about": ("monthly", "0.8"),
    "season": ("monthly", "0.8"),
    "gallery": ("monthly", "0.7"),
    "information": ("monthly", "0.7"),
    "contact": ("yearly", "0.7"),
    "sponsors": ("monthly", "0.6"),
    "privacy": ("yearly", "0.3"),
}
DEFAULT = ("monthly", "0.5")

# Content a page loads at runtime, so changes to it count as changes to the page.
DEPENDENCIES = {
    "": ["assets/data/news.json", "assets/data/sponsors.json"],
    "about": ["assets/data/team.json"],
    "season": ["assets/data/seasons.json"],
    "gallery": ["images/gallery", "assets/data/gallery-captions.json"],
    "sponsors": ["assets/data/sponsors.json", "images/sponsors"],
    "information": ["assets/data/links.json"],
}


def git_date(paths):
    paths = [str(p) for p in paths if (ROOT / p).exists()]
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", *paths],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or datetime.date.today().isoformat()


def main():
    found = {p.parent.name for p in ROOT.glob("*/index.html")} | {""}
    folders = [f for f in META if f in found] + sorted(found - set(META))
    entries = []
    for folder in folders:
        page = ROOT / folder / "index.html"
        if re.search(r'<meta[^>]+name="robots"[^>]+noindex', page.read_text(), re.I):
            continue
        rel = (Path(folder) / "index.html").as_posix()
        lastmod = max(git_date([rel]), git_date(DEPENDENCIES[folder]) if folder in DEPENDENCIES else "")
        freq, priority = META.get(folder, DEFAULT)
        url = f"https://{DOMAIN}/" + (f"{folder}/" if folder else "")
        entries.append(
            "  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>\n"
        )
    OUTPUT.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(entries)
        + "</urlset>\n"
    )
    print(f"Wrote {len(entries)} URLs to sitemap.xml")


if __name__ == "__main__":
    main()
