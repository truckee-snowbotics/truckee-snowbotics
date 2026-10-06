#!/usr/bin/env python3
"""Shrink images so big photos don't slow the site. Needs Pillow (pip install pillow);
skipped with a notice if it's missing.

- images/gallery/   .jpg/.jpeg/.png -> .webp (original removed), width capped at 1600px;
                    existing .webp wider than that are downscaled in place.
                    Also writes 480px thumbnails to images/gallery/thumbs/ (generated,
                    gitignored) which the gallery grid loads instead of the full image.
- images/sponsors/  width capped at 800px, same format (file names are referenced
                    from sponsors.json, so they never change).
- images/team/      portraits, width capped at 800px, same format.
- images/site/      width capped at 1600px, same format (icons are already smaller
                    and are left alone).
Images already within their cap are never re-encoded, so there's no quality loss on
repeated runs.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
GALLERY = IMAGES / "gallery"
THUMBS = GALLERY / "thumbs"
GALLERY_WIDTH = 1600
THUMB_WIDTH = 480
THUMB_QUALITY = 70
QUALITY = 82
RASTER = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
CONVERT_TO_WEBP = {".jpg", ".jpeg", ".png"}


def kb(path):
    return f"{path.stat().st_size // 1024} KB"


def main():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("Pillow not installed; skipping image optimization (pip install pillow)")
        return

    def load(path):
        im = Image.open(path)
        if getattr(im, "is_animated", False):
            return None
        return ImageOps.exif_transpose(im)

    def resized(im, width):
        if im.width <= width:
            return im
        return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)

    def save(im, target, fmt, quality=QUALITY):
        if fmt == "WEBP":
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.getbands() or "transparency" in im.info else "RGB")
            im.save(target, "WEBP", quality=quality, method=6)
        elif fmt == "AVIF":
            im.save(target, "AVIF", quality=60)
        elif fmt == "PNG":
            im.save(target, "PNG", optimize=True)
        else:
            im.convert("RGB").save(target, "JPEG", quality=85, optimize=True, progressive=True)

    def cap_in_place(folder, width):
        if not folder.exists():
            return
        for p in sorted(folder.iterdir()):
            if p.suffix.lower() not in RASTER:
                continue
            with load(p) or Image.new("RGB", (1, 1)) as im:
                if im.width <= width:
                    continue
                before = kb(p)
                fmt = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
                       ".webp": "WEBP", ".avif": "AVIF"}[p.suffix.lower()]
                save(resized(im, width), p, fmt)
            print(f"resized {p.relative_to(ROOT)} ({before} -> {kb(p)})")

    # Gallery: convert originals, cap width, build thumbnails.
    for p in sorted(GALLERY.iterdir()):
        if p.suffix.lower() not in CONVERT_TO_WEBP:
            continue
        target = p.with_suffix(".webp")
        if target.exists():
            print(f"warning: {target.name} already exists; leaving {p.name} unconverted")
            continue
        im = load(p)
        if im is None:
            continue
        before = kb(p)
        save(resized(im, GALLERY_WIDTH), target, "WEBP")
        im.close()
        p.unlink()
        print(f"optimized {p.name} -> {target.name} ({before} -> {kb(target)})")
    cap_in_place(GALLERY, GALLERY_WIDTH)

    THUMBS.mkdir(exist_ok=True)
    wanted = set()
    for p in sorted(GALLERY.iterdir()):
        if p.suffix.lower() not in RASTER:
            continue
        thumb = THUMBS / f"{p.stem}.webp"
        wanted.add(thumb.name)
        if thumb.exists() and thumb.stat().st_mtime >= p.stat().st_mtime:
            continue
        im = load(p)
        if im is not None:
            save(resized(im, THUMB_WIDTH), thumb, "WEBP", THUMB_QUALITY)
            if p.suffix.lower() == ".webp" and thumb.stat().st_size >= 0.9 * p.stat().st_size:
                shutil.copyfile(p, thumb)  # already small; a thumbnail wouldn't help
            print(f"thumbnail {thumb.relative_to(ROOT)} ({kb(thumb)})")
    for stale in THUMBS.glob("*.webp"):
        if stale.name not in wanted:
            stale.unlink()

    cap_in_place(IMAGES / "sponsors", 800)
    cap_in_place(IMAGES / "team", 800)
    cap_in_place(IMAGES / "site", 1600)


if __name__ == "__main__":
    sys.exit(main())
