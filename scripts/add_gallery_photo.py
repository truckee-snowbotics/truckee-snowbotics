#!/usr/bin/env python3
"""Turn a "Submit a gallery photo" issue into a gallery image + caption.

Run by .github/workflows/gallery-photo.yml with the issue text in $ISSUE_BODY and the
issue number in $ISSUE_NUMBER. Downloads the one attached image (GitHub upload links
only), checks it is a real image under 10 MB, saves it as images/gallery/<slug>.webp
(max 1600px) and adds the caption to gallery-captions.json. The pull request is made by
the workflow. Prints the new file name on the last line.
"""
import io
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "images" / "gallery"
CAPTIONS = ROOT / "assets" / "data" / "gallery-captions.json"
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 60_000_000
MAX_WIDTH = 1600
# Only images uploaded through GitHub's own issue uploader are accepted.
URL_RE = re.compile(
    r"https://(?:github\.com/user-attachments/(?:assets|files)/[\w./-]+"
    r"|user-images\.githubusercontent\.com/[\w./-]+)"
)


def section(body, heading):
    m = re.search(rf"### {heading}\s*\n(.*?)(?=\n### |\Z)", body, re.S)
    return m.group(1).strip() if m else ""


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    body = os.environ.get("ISSUE_BODY", "")
    number = os.environ.get("ISSUE_NUMBER", "0")
    urls = list(dict.fromkeys(URL_RE.findall(section(body, "Photo"))))
    if not urls:
        fail("No GitHub-uploaded image found in the Photo box.")
    if len(urls) > 1:
        fail("Please submit one photo per request.")

    req = urllib.request.Request(urls[0], headers={"User-Agent": "snowbotics-gallery"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        fail("Image is over 10 MB.")

    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    try:
        img = Image.open(io.BytesIO(data))
        if img.format not in ("JPEG", "PNG", "WEBP"):
            fail("Only JPG, PNG or WebP images are accepted.")
        img = ImageOps.exif_transpose(img)  # also drops location EXIF on re-save
        img.load()
    except Exception as e:  # noqa: BLE001 - any decode failure means "not a usable image"
        fail(f"Not a valid image ({e}).")
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)), Image.LANCZOS)

    caption = re.sub(r"\s+", " ", section(body, "Caption")).strip()
    if caption == "_No response_":
        caption = ""
    caption = caption[:200]

    slug = re.sub(r"[^a-z0-9]+", "-", caption.lower()).strip("-")[:40] or "photo"
    name = f"{slug}-{number}.webp"
    GALLERY.mkdir(parents=True, exist_ok=True)
    img.save(GALLERY / name, "WEBP", quality=82)

    if caption:
        captions = json.loads(CAPTIONS.read_text()) if CAPTIONS.exists() else {}
        captions[name] = caption
        CAPTIONS.write_text(json.dumps(captions, indent=2, ensure_ascii=False) + "\n")
    print(name)


if __name__ == "__main__":
    main()
