#!/usr/bin/env python3
"""Build the Alumni section of the About page from assets/data/alumni.json.

Writes the whole section (nothing if the file is empty) between <!-- @alumni --> and
<!-- @endalumni -->. Alumni are grouped by `year`, newest year first, each year under a
centered year heading. The newest MAX_VISIBLE_YEARS years are shown; any older years go
inside an "Earlier alumni" dropdown (a native <details>, no JavaScript).

Alumnus fields: name, year (required; whole number); role, bio, photo (optional, may be
blank; photo is an /images/... path, e.g. /images/team/name.webp).
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABOUT = ROOT / "about" / "index.html"
MARKER = re.compile(r"^(?P<indent>[ \t]*)<!-- @alumni -->\n.*?^[ \t]*<!-- @endalumni -->", re.S | re.M)
MAX_VISIBLE_YEARS = 4


def esc(value):
    return html.escape(str(value), quote=True)


def indent(text, ind):
    return "\n".join(ind + line if line.strip() else "" for line in text.split("\n"))


def initials(name):
    return "".join(w[0] for w in name.split()[:2]).upper()


def card(a):
    if a.get("photo"):
        photo = f'<img src="{esc(a["photo"])}" alt="{esc(a["name"])}" loading="lazy" decoding="async" />'
    else:
        photo = f'<span class="member-initials" aria-hidden="true">{esc(initials(a["name"]))}</span>'
    lines = [
        '<article class="member-card">',
        f'  <div class="member-photo">{photo}</div>',
        '  <div class="member-body">',
        f'    <h4 class="member-name">{esc(a["name"])}</h4>',
    ]
    if a.get("role"):
        lines.append(f'    <p class="member-role">{esc(a["role"])}</p>')
    if a.get("bio"):
        lines.append(f'    <p class="member-bio">{esc(a["bio"])}</p>')
    lines += ["  </div>", "</article>"]
    return "\n".join(lines)


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
        '<section class="section section--alt" id="alumni">\n'
        '  <div class="section-inner">\n'
        '    <div class="section-header">\n'
        "      <h2>Alumni</h2>\n"
        "    </div>\n"
        + indent("\n".join(blocks), "    ")
        + "\n  </div>\n</section>"
    )


def main():
    alumni = json.loads((ROOT / "assets" / "data" / "alumni.json").read_text())
    body = section(alumni)
    text = ABOUT.read_text()
    if "<!-- @alumni -->" not in text:
        raise SystemExit("error: about/index.html is missing <!-- @alumni --> ... <!-- @endalumni -->")

    def sub(m):
        ind = m["indent"]
        inner = indent(body, ind) + "\n" if body else ""
        return f"{ind}<!-- @alumni -->\n{inner}{ind}<!-- @endalumni -->"

    new = MARKER.sub(sub, text)
    if new != text:
        ABOUT.write_text(new)
    print(f"Alumni: {len(alumni)} in about/index.html")


if __name__ == "__main__":
    sys.exit(main())
