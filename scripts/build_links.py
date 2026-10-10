#!/usr/bin/env python3
"""Write the "listed" entries of assets/data/links.json as link lists, so they show without
JavaScript.

  partials/footer.html       <!-- @footerlinks --> ... <!-- @endfooterlinks -->  (the footer's Resources list;
                             runs before build_pages.py copies the footer into every page)
  information/index.html     <!-- @linksgrid --> ... <!-- @endlinksgrid -->      (Important Links & Forms)

Entries whose url is "#" or empty are left out. Links carry data-link-key with href="#", like
the rest of the HTML; the release build (apply_links.py) writes the real URLs in.
"""
import json
import sys

from _lib import ROOT, esc, fill_markers

TARGETS = [
    (ROOT / "partials" / "footer.html", "footerlinks",
     lambda i: f'<a href="#" data-link-key="{esc(i["id"])}">{esc(i["label"])}</a>'),
    (ROOT / "information" / "index.html", "linksgrid",
     lambda i: f'<a class="link-card" href="#" data-link-key="{esc(i["id"])}"><span class="link-card-label">{esc(i["label"])}</span></a>'),
]


def main():
    items = json.loads((ROOT / "assets" / "data" / "links.json").read_text())
    listed = [i for i in items if i.get("listed") and (i.get("url") or "").strip() not in ("", "#")]
    for path, name, render in TARGETS:
        text = path.read_text()
        new = fill_markers(text, name, "\n".join(render(i) for i in listed), path)
        if new != text:
            path.write_text(new)
    print(f"Links: {len(listed)} listed links into the footer and the Information page")


if __name__ == "__main__":
    sys.exit(main())
