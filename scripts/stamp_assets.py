#!/usr/bin/env python3
"""Cache busting: append ?v=<version> to the CSS/JS references in every HTML file.

Run only for releases (it edits the HTML in place). The version is the short git
commit hash, so browsers re-download CSS/JS exactly when a new deploy ships.
"""
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERN = re.compile(r'(assets/(?:css|js)/[\w.\-]+\.(?:css|js))(?:\?v=[\w]+)?')


def version():
    sha = os.environ.get("GITHUB_SHA", "")
    if not sha:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
        ).stdout.strip()
    return sha[:7] or "dev"


def main():
    v = version()
    count = 0
    pages = list(ROOT.glob("*.html")) + list(ROOT.glob("*/index.html"))
    for page in pages:
        text = page.read_text()
        new = PATTERN.sub(rf"\1?v={v}", text)
        if new != text:
            page.write_text(new)
            count += 1
    print(f"Stamped asset version {v} in {count} HTML files")


if __name__ == "__main__":
    main()
