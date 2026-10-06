#!/usr/bin/env python3
"""Build the team lists from assets/data/team.json (the one place the roster lives).

Writes:
  - the member cards on the About page, between <!-- @team --> and <!-- @endteam -->
  - the TEAM section of humans.txt (and its "Last update" month)

Member fields: name, role (required); id, initials (initials default to the name's
first letters); group ("students" by default, "mentors" or "alumni"); photo (optional /images/...
path); grade ("10th grade"); years (text shown as written, e.g. "2026" or "2024–2026");
bio (one or two sentences); empty (true = greyed-out placeholder). A blank role is
allowed (the line is skipped). Alumni are left out of humans.txt. Everything except name and role is optional and only shown when filled in.
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ABOUT = ROOT / "about" / "index.html"
HUMANS = ROOT / "humans.txt"
MARKER = re.compile(r"^(?P<indent>[ \t]*)<!-- @team -->\n.*?^[ \t]*<!-- @endteam -->", re.S | re.M)


def esc(value):
    return html.escape(str(value), quote=True)


def initials(member):
    if member.get("initials"):
        return member["initials"]
    return "".join(w[0] for w in member["name"].split()[:2]).upper()


GROUPS = [("students", "Students"), ("mentors", "Mentors &amp; Advisors"), ("alumni", "Alumni")]


def card(m):
    empty = bool(m.get("empty"))
    classes = "member-card" + (" member-card--empty" if empty else "")
    if m.get("photo") and not empty:
        photo = f'<img src="{esc(m["photo"])}" alt="{esc(m["name"])}" loading="lazy" decoding="async" />'
    else:
        photo = f'<span class="member-initials" aria-hidden="true">{esc(initials(m))}</span>'
    lines = [
        f'<article class="{classes}">',
        f'  <div class="member-photo">{photo}</div>',
        '  <div class="member-body">',
        f'    <h4 class="member-name">{esc(m["name"])}</h4>',
    ]
    if m.get("role"):
        lines.append(f'    <p class="member-role">{esc(m["role"])}</p>')
    detail = " · ".join(str(m[k]) for k in ("years", "grade") if m.get(k))
    if detail:
        lines.append(f'    <p class="member-meta">{esc(detail)}</p>')
    if m.get("bio"):
        lines.append(f'    <p class="member-bio">{esc(m["bio"])}</p>')
    lines += ["  </div>", "</article>"]
    return "\n".join(lines)


def groups_html(members):
    out = []
    for key, title in GROUPS:
        group = [m for m in members if m.get("group", "students") == key]
        if not group:
            continue
        out.append(
            f'<div class="team-group">\n'
            f'  <h3 class="team-group-title">{title}</h3>\n'
            '  <div class="team-grid">\n'
            + "\n".join("    " + line if line.strip() else "" for line in "\n".join(card(m) for m in group).split("\n"))
            + "\n  </div>\n</div>"
        )
    return "\n".join(out)


def main():
    members = json.loads((ROOT / "assets" / "data" / "team.json").read_text())
    real = [m for m in members if not m.get("empty") and m.get("group") != "alumni"]

    body = groups_html(members)
    text = ABOUT.read_text()

    def sub(m):
        ind = m["indent"]
        inner = "\n".join(ind + line if line.strip() else "" for line in body.split("\n"))
        return f"{ind}<!-- @team -->\n{inner}\n{ind}<!-- @endteam -->"

    new = MARKER.sub(sub, text)
    if new == text and "<!-- @team -->" not in text:
        raise SystemExit("error: about/index.html is missing <!-- @team --> ... <!-- @endteam -->")
    if new != text:
        ABOUT.write_text(new)

    humans = HUMANS.read_text()
    lines = [f"  {m['role']}: {m['name']}" for m in real]
    location = re.search(r"^  Location:.*$", humans, re.M)
    block = "/* TEAM */\n" + "\n".join(lines) + ("\n" + location.group(0) if location else "") + "\n"
    humans = re.sub(r"/\* TEAM \*/\n.*?(?=\n/\* |\Z)", block.rstrip("\n") + "\n", humans, count=1, flags=re.S)
    humans = re.sub(r"(  Last update: )\d{4}/\d{2}", rf"\g<1>{datetime.date.today():%Y/%m}", humans)
    if humans != HUMANS.read_text():
        HUMANS.write_text(humans)
    print(f"Team: {len(members)} members into about/index.html and humans.txt")


if __name__ == "__main__":
    sys.exit(main())
