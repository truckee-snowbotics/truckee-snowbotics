#!/usr/bin/env python3
"""Write the sponsor logos from assets/data/sponsors.json into the pages, so they show
without JavaScript.

  <!-- @sponsors -->   ... <!-- @endsponsors -->     the Sponsors page grid
  <!-- @sponsorbar --> ... <!-- @endsponsorbar -->   the "Our Sponsors" bar (on any page that has it)

All sponsors are shown equally, in sponsors.json order. A sponsor with a website links to it.
"""
import json
import sys

from _lib import ROOT, esc, fill_markers


def logo(item, css):
    img = f'<img src="{esc(item["banner"])}" alt="{esc(item.get("name") or "Sponsor")} banner" loading="lazy" decoding="async" />'
    url = (item.get("website") or "").strip()
    if url:
        return f'<a class="{css}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{img}</a>'
    return f'<div class="{css}">{img}</div>'


def main():
    sponsors = json.loads((ROOT / "assets" / "data" / "sponsors.json").read_text())
    grid = "\n".join(logo(s, "sponsor-item") for s in sponsors)
    bar = "\n".join(logo(s, "sponsor-bar-logo") for s in sponsors)
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html"))
    changed = 0
    for page in pages:
        text = new = page.read_text()
        if "<!-- @sponsors -->" in new:
            new = fill_markers(new, "sponsors", grid, page)
        if "<!-- @sponsorbar -->" in new:
            new = fill_markers(new, "sponsorbar", bar, page)
        if new != text:
            page.write_text(new)
            changed += 1
    print(f"Sponsors: {len(sponsors)} logos ({changed} pages changed)")


if __name__ == "__main__":
    sys.exit(main())
