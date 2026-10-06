#!/usr/bin/env python3
"""Minify assets/css/main.css and assets/js/main.js in place (release builds only).

Uses rcssmin/rjsmin, which only strip comments and whitespace (no renaming), so
behavior is unchanged. Edits the files in place, so don't commit the output.
Skipped with a notice if the packages aren't installed (pip install -r requirements.txt).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    try:
        import rcssmin
        import rjsmin
    except ImportError:
        print("rcssmin/rjsmin not installed; skipping minification")
        return
    for path, minify in (
        (ROOT / "assets" / "css" / "main.css", rcssmin.cssmin),
        (ROOT / "assets" / "js" / "main.js", lambda s: rjsmin.jsmin(s)),
    ):
        source = path.read_text()
        minified = minify(source)
        path.write_text(minified)
        print(f"minified {path.relative_to(ROOT)}: {len(source) // 1024} KB -> {len(minified) // 1024} KB")


if __name__ == "__main__":
    main()
