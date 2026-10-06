#!/usr/bin/env python3
"""Run every build step in order. Used by CI and handy for local previews.

    python3 scripts/build.py             # local: sync partials, optimize images, gallery.json,
                                         # sitemap, checks
    python3 scripts/build.py --release   # CI: also writes links.json URLs into the HTML,
                                         # minifies CSS/JS and stamps them with the commit hash
                                         # (edits HTML in place — don't commit that)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["optimize_images.py", "build_pages.py", "build_news.py", "build_calendar.py", "build_season.py", "build_meta.py", "build_team.py", "build_alumni.py", "build_gallery.py", "build_sitemap.py"]


def main():
    release = "--release" in sys.argv
    steps = list(STEPS)
    if release:
        steps += ["apply_links.py", "minify_assets.py", "stamp_assets.py"]
    # last, so it validates the final output
    steps.append("check_site.py --release" if release else "check_site.py")
    for step in steps:
        print(f"\n== {step}", flush=True)
        script, *args = step.split()
        result = subprocess.run([sys.executable, str(HERE / script), *args])
        if result.returncode:
            print(f"\n{script} failed")
            return result.returncode


if __name__ == "__main__":
    sys.exit(main())
