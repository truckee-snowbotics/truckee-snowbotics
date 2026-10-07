#!/usr/bin/env python3
"""Put the home page hero photo and the About page photo in place, from assets/data/site.json.

    "heroPhoto":  {"src": "/images/site/home.avif",  "alt": "..."}   home page, beside the headline
    "aboutPhoto": {"src": "/images/gallery/x.webp",  "alt": "..."}   About page, beside the intro

src is any image in the project (images/site/ is the natural home for a new one); alt is a short
description for screen readers (required). Both photos are shown as landscape 4:3 boxes and
cropped to fit, so landscape photos with the subject near the middle work best. Width and height
are filled in from the file (needs Pillow, like the image optimizer) so the page doesn't jump
while the photo loads.
"""
import json
import sys

from _lib import ROOT, esc, fill_markers, image_size

HERO = ROOT / "index.html"
ABOUT = ROOT / "about" / "index.html"


def img(photo, extra):
    dims = image_size(photo["src"])
    wh = f' width="{dims[0]}" height="{dims[1]}"' if dims else ""
    return f'<img src="{esc(photo["src"])}" alt="{esc(photo["alt"])}"{wh}{extra} decoding="async" />'


def main():
    site = json.loads((ROOT / "assets" / "data" / "site.json").read_text())
    jobs = [(HERO, "heroPhoto", ' fetchpriority="high"'), (ABOUT, "aboutPhoto", "")]
    for page, key, extra in jobs:
        text = page.read_text()
        new = fill_markers(text, key, img(site[key], extra), page)
        if new != text:
            page.write_text(new)
    print("Hero and About photos in place")


if __name__ == "__main__":
    sys.exit(main())
