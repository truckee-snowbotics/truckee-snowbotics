"""Small helpers shared by the build scripts."""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def esc(value):
    """HTML-escape text (including quotes) for element or attribute content."""
    return html.escape(str(value), quote=True)


def indent(text, prefix):
    """Indent every non-blank line of text."""
    return "\n".join(prefix + line if line.strip() else "" for line in text.rstrip("\n").split("\n"))


def read_domain():
    cname = ROOT / "CNAME"
    return cname.read_text().strip() if cname.exists() else "snowbotics.org"


def marker_pattern(name):
    return re.compile(
        rf"^(?P<indent>[ \t]*)<!-- @{name} -->\n.*?^[ \t]*<!-- @end{name} -->", re.S | re.M
    )


def fill_markers(text, name, body, page=None):
    """Replace what's between <!-- @name --> and <!-- @endname --> with body (re-indented to
    match the marker). An empty body leaves the markers adjacent. Exits with an error if the
    page has no such markers."""
    if f"<!-- @{name} -->" not in text:
        where = page.relative_to(ROOT) if page else "page"
        sys.exit(f"error: {where} is missing <!-- @{name} --> ... <!-- @end{name} -->")

    def sub(m):
        ind = m["indent"]
        inner = indent(body, ind) + "\n" if body else ""
        return f"{ind}<!-- @{name} -->\n{inner}{ind}<!-- @end{name} -->"

    return marker_pattern(name).sub(sub, text)


def initials(name):
    return "".join(w[0] for w in name.split()[:2]).upper()


def member_card(name, role="", grade="", bio="", photo="", level=4):
    """One person card (team and alumni): photo or initials, name, then whatever is filled in."""
    if photo:
        pic = f'<img src="{esc(photo)}" alt="{esc(name)}" loading="lazy" decoding="async" />'
    else:
        pic = f'<span class="member-initials" aria-hidden="true">{esc(initials(name))}</span>'
    lines = [
        '<article class="member-card">',
        f'  <div class="member-photo">{pic}</div>',
        '  <div class="member-body">',
        f'    <h{level} class="member-name">{esc(name)}</h{level}>',
    ]
    if role:
        lines.append(f'    <p class="member-role">{esc(role)}</p>')
    if grade:
        lines.append(f'    <p class="member-meta">{esc(grade)}</p>')
    if bio:
        lines.append(f'    <p class="member-bio">{esc(bio)}</p>')
    lines += ["  </div>", "</article>"]
    return "\n".join(lines)


def image_size(src):
    """(width, height) of a site image (path like /images/x.webp), or None if Pillow is missing."""
    try:
        from PIL import Image
        with Image.open(ROOT / src.lstrip("/")) as im:
            return im.size
    except Exception:  # Pillow missing or an unreadable format: pages work without the size
        return None
