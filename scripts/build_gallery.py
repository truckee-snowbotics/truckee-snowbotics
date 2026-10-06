#!/usr/bin/env python3
"""Regenerate assets/data/gallery.json (a plain list of image paths) from images/gallery/.

Captions are not stored here: the page reads assets/data/gallery-captions.json
({"file.webp": "Caption"}) itself and falls back to the filename. This script only
warns about captions that point at images that no longer exist. Images are listed
in filename order, one entry per name (a .webp wins over a leftover original).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = ROOT / "images" / "gallery"
CAPTIONS = ROOT / "assets" / "data" / "gallery-captions.json"
OUTPUT = ROOT / "assets" / "data" / "gallery.json"
EXTENSIONS = {".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif"}


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
    print(f"Wrote {len(items)} images to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
