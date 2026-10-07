#!/usr/bin/env python3
"""Build the home page banner from "banner" in assets/data/site.json.

Fills <!-- @banner --> ... <!-- @endbanner --> in index.html:

  "banner": { "enabled": true, "message": "…", "linkLabel": "Season page", "link": "/season/" }

  enabled    false hides the banner
  message    the text (required)
  linkLabel  words on the button; the button is left out when there is no link
  link       a page ("/season/"), a full URL, or an id from links.json
"""
import json

from _lib import ROOT, esc, fill_markers

HOME = ROOT / "index.html"


def banner_html(banner, link_ids):
    if not banner or banner.get("enabled", True) is False or not banner.get("message"):
        return ""
    out = ['<div class="banner">', f'  <span class="banner-text">{esc(banner["message"])}</span>']
    link = banner.get("link")
    if link:
        label = esc(banner.get("linkLabel") or "Learn more")
        if link in link_ids:
            out.append(f'  <a class="banner-link" href="#" data-link-key="{esc(link)}">{label}</a>')
        else:
            external = link.startswith("http")
            extra = ' target="_blank" rel="noopener"' if external else ""
            out.append(f'  <a class="banner-link" href="{esc(link)}"{extra}>{label}</a>')
    out.append("</div>")
    return "\n".join(out)


def main():
    data = ROOT / "assets" / "data"
    site = json.loads((data / "site.json").read_text())
    link_ids = {l["id"] for l in json.loads((data / "links.json").read_text())}
    html = banner_html(site.get("banner"), link_ids)
    text = HOME.read_text()
    new = fill_markers(text, "banner", html, HOME)
    if new != text:
        HOME.write_text(new)
    print("Banner is " + ("on" if html else "off"))


if __name__ == "__main__":
    main()
