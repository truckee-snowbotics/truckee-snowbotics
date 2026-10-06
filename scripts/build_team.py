#!/usr/bin/env python3
"""Build the team lists from assets/data/team.json (the one place the roster lives).

Writes:
  - the student and mentor cards on the About page, between <!-- @team --> and <!-- @endteam -->
  - the TEAM section of humans.txt (and its "Last update" month)

Member fields: name, role (required); id; group ("students" by default, or "mentors"); photo (optional /images/...
path); grade ("10th grade"); bio (one or two sentences). Without a photo the card shows the
name's initials. A blank role is allowed (the line is skipped). Everything except name and
role is optional and only shown when filled in. Alumni live in alumni.json (build_alumni.py).
"""
import datetime
import json
import re
import sys

from _lib import ROOT, fill_markers, indent, member_card

ABOUT = ROOT / "about" / "index.html"
HUMANS = ROOT / "humans.txt"

GROUPS = [("students", "Students"), ("mentors", "Mentors &amp; Advisors")]


def card(m):
    return member_card(m["name"], m.get("role", ""), m.get("grade", ""), m.get("bio", ""), m.get("photo", ""))


def groups_html(members):
    out = []
    for key, title in GROUPS:
        group = [m for m in members if m.get("group", "students") == key]
        if not group:
            continue
        out.append(
            '<details class="team-group" data-collapse-mobile open>\n'
            f'  <summary><h3 class="team-group-title"><span>{title}</span><span class="team-group-count">{len(group)}</span></h3></summary>\n'
            '  <div class="team-grid">\n'
            + indent("\n".join(card(m) for m in group), "    ")
            + "\n  </div>\n</details>"
        )
    return "\n".join(out)


def main():
    members = json.loads((ROOT / "assets" / "data" / "team.json").read_text())
    real = [m for m in members if not m.get("empty")]

    text = ABOUT.read_text()
    new = fill_markers(text, "team", groups_html(members), ABOUT)
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
