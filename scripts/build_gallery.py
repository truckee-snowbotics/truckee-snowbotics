#!/usr/bin/env python3
"""Regenerate assets/data/gallery.json (a plain list of image paths) from images/gallery/.

Also writes the photo grid into the Gallery page (between <!-- @gallery --> and
<!-- @endgallery -->), so photos show without JavaScript. Each photo links to the full
image; with JavaScript, main.js opens it in the photo viewer instead.

Captions come from assets/data/gallery-captions.json ({"file.webp": "Caption"}); images
without one fall back to their filename. Captions that point at images that no longer
exist get a warning. Images are listed in filename order, one entry per name (a .webp
wins over a leftover original).
"""
import json
import re
from pathlib import Path

from _lib import ROOT, esc, fill_markers

PAGE = ROOT / "gallery" / "index.html"
IMAGE_DIR = ROOT / "images" / "gallery"
CAPTIONS = ROOT / "assets" / "data" / "gallery-captions.json"
OUTPUT = ROOT / "assets" / "data" / "gallery.json"
EXTENSIONS = {".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif"}


def caption_for(src, captions):
    """The caption for an image (matched by file name, or by name without extension), else its name."""
    file = src.rsplit("/", 1)[-1]
    stem = Path(file).stem
    custom = captions.get(file) or next((v for k, v in captions.items() if Path(k).stem == stem), "")
    return (custom or "").strip() or re.sub(r"[_\-\s]+", " ", stem).strip()


def card(src, captions):
    """One photo: a link to the full image, showing the small thumbnail (made by optimize_images.py)."""
    caption = caption_for(src, captions)
    thumb = src.replace("/images/gallery/", "/images/gallery/thumbs/").rsplit(".", 1)[0] + ".webp"
    return (
        f'<a class="gallery-item" href="{esc(src)}" aria-label="{esc("View photo: " + caption)}" '
        f'data-src="{esc(src)}" data-alt="{esc(caption)}" data-caption="{esc(caption)}">'
        f'<div class="gallery-image"><img src="{esc(thumb)}" alt="{esc(caption)}" loading="lazy" decoding="async" '
        f'onerror="this.onerror=null;this.src=this.closest(&#39;.gallery-item&#39;).dataset.src" /></div></a>'
    )


def main():
    captions = json.loads(CAPTIONS.read_text()) if CAPTIONS.exists() else {}

    chosen = {}
    for p in IMAGE_DIR.iterdir():
        if p.suffix.lower() not in EXTENSIONS:
            continue
        if p.stem not in chosen or p.suffix.lower() == ".webp":
            chosen[p.stem] = p
    files = sorted(chosen.values(), key=lambda p: p.name.lower())
    items = [f"/images/gallery/{p.name}" for p in files]

    for name in captions:
        if Path(name).stem not in chosen:
            print(f"warning: caption for missing image '{name}'")

    OUTPUT.write_text(json.dumps(items, indent=2) + "\n")
    text = PAGE.read_text()
    new = fill_markers(text, "gallery", "\n".join(card(src, captions) for src in items), PAGE)
    if new != text:
        PAGE.write_text(new)
    print(f"Wrote {len(items)} images to {OUTPUT.relative_to(ROOT)} and the Gallery page")


if __name__ == "__main__":
    main()
