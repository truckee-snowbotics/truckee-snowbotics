#!/usr/bin/env python3
"""Build the Alumni section of the About page from assets/data/alumni.json.

Writes the whole section (nothing if the file is empty) between <!-- @alumni --> and
<!-- @endalumni -->. Alumni are grouped by `year`, newest year first, as a compact
list (year on the left, names on the right). The newest MAX_VISIBLE_YEARS years are shown; any older years go
inside an "Earlier alumni" dropdown (a native <details>, no JavaScript).

Alumnus fields: name, year (required; whole number); role, bio, photo (optional, may be
blank; photo is an /images/... path, e.g. /images/team/name.webp; shown as a small thumbnail).
"""
import json
import sys

from _lib import ROOT, esc, fill_markers, indent

ABOUT = ROOT / "about" / "index.html"
MAX_VISIBLE_YEARS = 4


def person(a):
    parts = [f'<strong class="alumni-name">{esc(a["name"])}</strong>']
    if a.get("role"):
        parts.append(f'<span class="alumni-role">{esc(a["role"])}</span>')
    if a.get("bio"):
        parts.append(f'<span class="alumni-bio">{esc(a["bio"])}</span>')
    photo = ""
    if a.get("photo"):
        photo = f'<img class="alumni-photo" src="{esc(a["photo"])}" alt="" width="44" height="44" loading="lazy" decoding="async" />'
    return f"<li>{photo}<div>{' '.join(parts)}</div></li>"


def year_block(year, people):
    return (
        '<div class="alumni-row">\n'
        f'  <h3 class="alumni-row-year">{year}</h3>\n'
        '  <ul class="alumni-people">\n'
        + indent("\n".join(person(a) for a in people), "    ")
        + "\n  </ul>\n</div>"
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
        '<section class="section section--tight section--split" id="alumni">\n'
        '  <div class="section-inner">\n'
        '    <div class="section-header">\n'
        "      <h2>Alumni</h2>\n"
        "    </div>\n"
        '    <div class="alumni-list">\n'
        + indent("\n".join(blocks), "      ")
        + "\n    </div>\n  </div>\n</section>"
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
