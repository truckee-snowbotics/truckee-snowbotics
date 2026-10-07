#!/usr/bin/env python3
"""Build the home page's "outreach" section from assets/data/outreach.json.

Writes the whole section between <!-- @outreach --> and <!-- @endoutreach -->; nothing is
written when "enabled" is false or the file has no title/intro, so the section just isn't on
the page.

    title, intro   required text
    invite         optional second paragraph (for example, how to get in touch)
    photo          optional {"src": "/images/...", "alt": "..."} shown beside the intro
    items          optional list of {"title", "text"} cards under it
    buttons        optional list of {"label", and either "link": "<id in links.json>" or
                   "url": "/contact/" ...}; "primary": true makes the white button
"""
import json
import sys

from _lib import ROOT, esc, fill_markers, image_size, indent

HOME = ROOT / "index.html"


def button(b):
    css = "btn-primary" if b.get("primary") else "btn-outline"
    if b.get("link"):  # a links.json id: the URL lives only there
        return f'<a href="#" data-link-key="{esc(b["link"])}" class="{css}" target="_blank" rel="noopener">{esc(b["label"])}</a>'
    url = b["url"]
    external = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    return f'<a href="{esc(url)}" class="{css}"{external}>{esc(b["label"])}</a>'


def section(data):
    if not data.get("enabled", True) or not data.get("title") or not data.get("intro"):
        return ""
    parts = [
        '<section class="section" id="outreach">',
        '  <div class="section-inner">',
        '    <div class="about-split">',
        '      <div class="about-split__text">',
        '        <div class="section-header">',
        f'          <h2>{esc(data["title"])}</h2>',
        "        </div>",
        f'        <p class="about-body">{esc(data["intro"])}</p>',
    ]
    if data.get("invite"):
        parts.append(f'        <p class="about-body">{esc(data["invite"])}</p>')
    if data.get("buttons"):
        parts.append('        <div class="btn-row">')
        parts += ["          " + button(b) for b in data["buttons"]]
        parts.append("        </div>")
    parts.append("      </div>")
    photo = data.get("photo")
    if photo:
        dims = image_size(photo["src"])
        wh = f' width="{dims[0]}" height="{dims[1]}"' if dims else ""
        parts += [
            '      <div class="about-split__img">',
            f'        <img src="{esc(photo["src"])}" alt="{esc(photo["alt"])}"{wh} loading="lazy" decoding="async" />',
            "      </div>",
        ]
    parts.append("    </div>")
    if data.get("items"):
        parts.append('    <div class="info-grid outreach-points">')
        for item in data["items"]:
            parts += [
                '      <div class="info-card">',
                f'        <span class="info-card-title">{esc(item["title"])}</span>',
                f'        <p class="info-card-body">{esc(item["text"])}</p>',
                "      </div>",
            ]
        parts.append("    </div>")
    parts += ["  </div>", "</section>"]
    return "\n".join(parts)


def main():
    data = json.loads((ROOT / "assets" / "data" / "outreach.json").read_text())
    text = HOME.read_text()
    new = fill_markers(text, "outreach", section(data), HOME)
    if new != text:
        HOME.write_text(new)
    print("Outreach section " + ("on" if section(data) else "off"))


if __name__ == "__main__":
    sys.exit(main())
