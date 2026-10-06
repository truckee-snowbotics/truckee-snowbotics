#!/usr/bin/env python3
"""Generate each page's canonical URL, Open Graph / Twitter tags and breadcrumb data.

Each page keeps only its own <title> and <meta name="description"> (the one place the page's
name and summary are written). Everything derived from them lives between markers:

    <!-- @meta -->        ...canonical, og:*, twitter:*...   <!-- @endmeta -->
    <!-- @breadcrumb --> ...BreadcrumbList JSON-LD...        <!-- @endbreadcrumb -->

Pages marked noindex (the 404) get social tags but no canonical URL, og:url or breadcrumb.
The page path comes from the folder (about/index.html -> /about/). The breadcrumb name is the
title without " · Truckee Snowbotics". Social image: images/site/og-card.png (1200x630).
"""
import html
import json
import re
import sys
from pathlib import Path

from _lib import ROOT, fill_markers, read_domain

SITE = "Truckee Snowbotics"
IMAGE = "images/site/og-card.png"
IMAGE_ALT = "Truckee Snowbotics — FTC Team #32587"


def page_url(page, domain):
    folder = page.parent.relative_to(ROOT).as_posix()
    return f"https://{domain}/" + ("" if folder == "." or page.name != "index.html" else folder + "/")


def meta_block(title, desc, url, domain):
    tags = []
    if url:
        tags.append(f'<link rel="canonical" href="{url}" />')
    tags.append("<!-- Open Graph -->")
    tags.append('<meta property="og:type" content="website" />')
    tags.append(f'<meta property="og:site_name" content="{SITE}" />')
    if url:
        tags.append(f'<meta property="og:url" content="{url}" />')
    tags += [
        f'<meta property="og:title" content="{title}" />',
        f'<meta property="og:description" content="{desc}" />',
        f'<meta property="og:image" content="https://{domain}/{IMAGE}" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        '<meta property="og:image:type" content="image/png" />',
        f'<meta property="og:image:alt" content="{IMAGE_ALT}" />',
        "<!-- Twitter Card -->",
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{title}" />',
        f'<meta name="twitter:description" content="{desc}" />',
        f'<meta name="twitter:image" content="https://{domain}/{IMAGE}" />',
    ]
    return "\n".join(tags)


def breadcrumb_block(title, url, domain):
    name = html.unescape(re.sub(rf"\s*·\s*{SITE}$", "", title))
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"https://{domain}/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": url},
    ]
    lines = [
        '<script type="application/ld+json">',
        "{",
        '  "@context": "https://schema.org",',
        '  "@type": "BreadcrumbList",',
        '  "itemListElement": [',
        ",\n".join("    " + json.dumps(i, ensure_ascii=False) for i in items),
        "  ]",
        "}",
        "</script>",
    ]
    return "\n".join(lines)


def main():
    domain = read_domain()
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html"))
    changed = 0
    for page in pages:
        text = page.read_text()
        title = re.search(r"<title>(.*?)</title>", text, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', text)
        if not (title and desc):
            sys.exit(f"error: {page.relative_to(ROOT)} needs a <title> and <meta name=\"description\">")
        title, desc = title.group(1).strip(), desc.group(1)
        noindex = bool(re.search(r'<meta[^>]+name="robots"[^>]+noindex', text, re.I))
        url = None if noindex else page_url(page, domain)
        new = fill_markers(text, "meta", meta_block(title, desc, url, domain), page)
        is_home = page == ROOT / "index.html"
        if url and not is_home:
            new = fill_markers(new, "breadcrumb", breadcrumb_block(title, url, domain), page)
        if new != text:
            page.write_text(new)
            changed += 1
    print(f"Page meta up to date in {len(pages)} pages ({changed} changed)")


if __name__ == "__main__":
    main()
