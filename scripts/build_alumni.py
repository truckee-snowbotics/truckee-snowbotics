#!/usr/bin/env python3
"""Build the Alumni section of the About page from assets/data/alumni.json.

Writes the whole section (nothing if the file is empty) between <!-- @alumni --> and
<!-- @endalumni -->. Alumni are grouped by `year`, newest year first, each year under a
centered year heading. The newest MAX_VISIBLE_YEARS years are shown; any older years go
inside an "Earlier alumni" dropdown (a native <details>, no JavaScript). On phones the
whole list is collapsed behind a "Show alumni" button (see main.js, data-collapse-mobile).

Alumnus fields: name, year (required; whole number); role, bio, photo (optional, may be
blank; photo is an /images/... path, e.g. /images/team/name.webp).
"""
import json
import sys

from _lib import ROOT, fill_markers, indent, member_card

ABOUT = ROOT / "about" / "index.html"
MAX_VISIBLE_YEARS = 4


def card(a):
    return member_card(a["name"], a.get("role", ""), "", a.get("bio", ""), a.get("photo", ""))


def year_block(year, people):
    return (
        '<div class="alumni-year">\n'
        f'  <h3 class="alumni-year-title">{year}</h3>\n'
        '  <div class="team-grid">\n'
        + indent("\n".join(card(a) for a in people), "    ")
        + "\n  </div>\n</div>"
    )


def section(alumni):
    if not alumni:
        return ""
    by_year = {}
    for a in alumni:
        by_year.setdefault(a["year"], []).append(a)
    years = sorted(by_year, reverse=True)
    shown, older = years[:MAX_VISIBLE_YEARS], years[MAX_VISIBLE_YEARS:]
    blocks = [year_block(y, by_year[y]) for y in shown]
    if older:
        count = sum(len(by_year[y]) for y in older)
        blocks.append(
            '<details class="alumni-more">\n'
            f"  <summary>Earlier alumni ({count})</summary>\n"
            + indent("\n".join(year_block(y, by_year[y]) for y in older), "  ")
            + "\n</details>"
        )
    return (
        '<section class="section" id="alumni">\n'
        '  <div class="section-inner">\n'
        '    <div class="section-header">\n'
        "      <h2>Alumni</h2>\n"
        "    </div>\n"
        '    <details class="alumni-all" data-collapse-mobile open>\n'
        f"      <summary>Show alumni ({len(alumni)})</summary>\n"
        + indent("\n".join(blocks), "      ")
        + "\n    </details>\n  </div>\n</section>"
    )


def main():
    alumni = json.loads((ROOT / "assets" / "data" / "alumni.json").read_text())
    text = ABOUT.read_text()
    new = fill_markers(text, "alumni", section(alumni), ABOUT)
    if new != text:
        ABOUT.write_text(new)
    print(f"Alumni: {len(alumni)} in about/index.html")


if __name__ == "__main__":
    sys.exit(main())
