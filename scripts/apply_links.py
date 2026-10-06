#!/usr/bin/env python3
"""Write the URLs from assets/data/links.json into the HTML (release builds only).

The HTML only carries data-link-key / data-form-action attributes (href stays "#");
this step fills in the real href/action so links work without JavaScript and the
repo holds each URL in exactly one place. It edits HTML in place, so don't commit
its output.

  <a data-link-key="id">          -> href = that entry's url (external URLs also get
                                     target="_blank" rel="noopener noreferrer")
  <a data-link-key="email">text   -> mailto: entries also replace visible text that
                                     contains an "@" with the address
  <form data-form-action="id">    -> action = that entry's url
  JSON-LD "email"                 -> the "email" entry's address
Entries whose url is "#" are skipped (JS hides those elements at runtime).
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = r'(?:[^>"\']|"[^"]*"|\'[^\']*\')*'
OPEN_TAG = re.compile(rf"<(a|form)\b{TAG}>")
EMAIL_LINK = re.compile(rf'(<a\b{TAG}data-link-key="([^"]+)"{TAG}>)([^<]*)(</a>)')
JSON_LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def load_urls():
    items = json.loads((ROOT / "assets" / "data" / "links.json").read_text())
    return {i["id"]: (i.get("url") or "").strip() for i in items if i.get("id")}


def set_attr(tag, name, value):
    value = html.escape(value, quote=True)
    if re.search(rf'\s{name}="[^"]*"', tag):
        return re.sub(rf'(\s{name}=")[^"]*(")', lambda m: m.group(1) + value + m.group(2), tag, count=1)
    return tag[:-1] + f' {name}="{value}">'


def main():
    urls = load_urls()
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html"))
    changed = 0

    def rewrite_tag(m):
        tag = m.group(0)
        if m.group(1) == "a":
            key = re.search(r'data-link-key="([^"]+)"', tag)
            url = urls.get(key.group(1)) if key else None
            if not url or url == "#":
                return tag
            tag = set_attr(tag, "href", url)
            if re.match(r"https?:", url, re.I) and "target=" not in tag:
                tag = set_attr(set_attr(tag, "target", "_blank"), "rel", "noopener noreferrer")
            return tag
        key = re.search(r'data-form-action="([^"]+)"', tag)
        url = urls.get(key.group(1)) if key else None
        return set_attr(tag, "action", url) if url and url != "#" else tag

    def rewrite_email_text(m):
        url = urls.get(m.group(2))
        if url and url.lower().startswith("mailto:") and "@" in m.group(3):
            return m.group(1) + html.escape(url[7:]) + m.group(4)
        return m.group(0)

    email = urls.get("email", "")[7:]

    def rewrite_json_ld(m):
        if not email:
            return m.group(0)
        body = re.sub(r'("email"\s*:\s*")[^"]*(")', lambda e: e.group(1) + email + e.group(2), m.group(2))
        return m.group(1) + body + m.group(3)

    for page in pages:
        text = page.read_text()
        new = OPEN_TAG.sub(rewrite_tag, text)
        new = EMAIL_LINK.sub(rewrite_email_text, new)
        new = JSON_LD.sub(rewrite_json_ld, new)
        if new != text:
            page.write_text(new)
            changed += 1
    print(f"Applied links.json URLs in {changed} HTML files")


if __name__ == "__main__":
    main()
