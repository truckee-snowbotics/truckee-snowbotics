#!/usr/bin/env python3
"""Sync the shared page chunks in partials/ into every HTML page.

Each page marks where a chunk goes:

    <!-- @partial header -->
    ...copy of partials/header.html (managed — don't edit here)...
    <!-- @endpartial header -->

Edit the file in partials/, run this script (build.py does), and commit the updated
pages. Pages stay complete HTML, so they preview locally without a build.
The header's link to the current page gets class="active" and aria-current="page".
Partials: head-common (icons, fonts, stylesheet), header, footer, scripts (on every page);
support (the "Support Us" donate section, on the pages that include it).
"""
import datetime
import json
import re
import sys

from _lib import ROOT, indent

PARTIALS = ROOT / "partials"
# Partials every page must include; any other partial goes only where a page has its markers.
REQUIRED = ("head-common", "header", "footer", "scripts")
MARKER = re.compile(
    r"^(?P<indent>[ \t]*)<!-- @partial (?P<name>[\w-]+) -->\n.*?^[ \t]*<!-- @endpartial (?P=name) -->",
    re.S | re.M,
)


def season_enabled():
    try:
        return json.loads((ROOT / "assets" / "data" / "season.json").read_text()).get("enabled", True)
    except (OSError, ValueError):
        return True


def main():
    partials = {p.stem: p.read_text() for p in PARTIALS.glob("*.html")}
    # {{year}} in a partial becomes the current year (the daily deploy keeps it fresh)
    partials = {name: text.replace("{{year}}", str(datetime.date.today().year)) for name, text in partials.items()}
    if not season_enabled():  # season.json "enabled": false removes the Season links
        partials = {
            name: "\n".join(l for l in text.split("\n") if 'href="/season/"' not in l)
            for name, text in partials.items()
        }
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html"))
    changed, problems = 0, 0
    for page in pages:
        text = page.read_text()
        # This page's address in the nav: index.html -> "/", about/index.html -> "/about/", 404.html -> none
        rel = page.relative_to(ROOT).as_posix()
        path = "/" if rel == "index.html" else "/" + rel.removesuffix("index.html") if rel.endswith("/index.html") else None

        def fill(m):
            name = m["name"]
            if name not in partials:
                print(f"error: {page.relative_to(ROOT)} uses unknown partial '{name}'")
                nonlocal problems
                problems += 1
                return m.group(0)
            ind = m["indent"]
            body = partials[name]
            if name == "header" and path:  # mark this page's nav links (works without JS)
                body = body.replace(f'<a href="{path}">', f'<a href="{path}" class="active" aria-current="page">')
            return (f"{ind}<!-- @partial {name} -->\n{indent(body, ind)}\n"
                    f"{ind}<!-- @endpartial {name} -->")

        new = MARKER.sub(fill, text)
        for name in REQUIRED:
            if f"<!-- @partial {name} -->" not in new:
                print(f"error: {page.relative_to(ROOT)} is missing <!-- @partial {name} -->")
                problems += 1
        if new != text:
            page.write_text(new)
            changed += 1
    print(f"Synced partials into {changed} HTML files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
