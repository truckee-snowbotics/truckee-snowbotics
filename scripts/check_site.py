#!/usr/bin/env python3
"""Pre-deploy checks. Exits non-zero (failing the deploy) if any ERROR is found.

ERROR (blocks deploy):
  - invalid JSON in assets/data/*.json or site.webmanifest
  - data files that don't match their schema (see SCHEMAS): wrong type, missing
    required field, bad sponsor tier, duplicate id, more than one current season
  - local /images/... or /assets/... paths in JSON data that don't exist
  - HTML src/href/srcset (and og:image) pointing at a local file that doesn't exist
    (exact-case match, since GitHub's Linux servers are case-sensitive)
  - <img> without an alt attribute, duplicate ids, missing <title> or <html lang>
  - links: a data-link-key / data-form-action with no matching links.json id, or a
    link whose href is a URL from links.json but has no data-link-key (use the key
    so the URL stays in one place); with --release, a keyed link whose href didn't
    get its URL
WARNING (printed only):
  - unknown fields in data files (usually typos), "Update..." placeholder text left
    in data files
  - missing meta description, not exactly one <h1>, skipped heading levels,
    target="_blank" without rel="noopener", #fragment links to a missing id
"""
import datetime
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = (ROOT / "CNAME").read_text().strip() if (ROOT / "CNAME").exists() else "snowbotics.org"
REF_ATTRS = {
    ("a", "href"), ("link", "href"), ("script", "src"), ("img", "src"), ("source", "src"),
    ("iframe", "src"), ("video", "src"), ("audio", "src"), ("embed", "src"),
    ("video", "poster"), ("form", "action"),
}
SKIP_SCHEMES = ("http:", "https:", "mailto:", "tel:", "javascript:", "data:", "sms:")

RELEASE = "--release" in sys.argv
errors, warnings = [], []


def load_links():
    f = ROOT / "assets" / "data" / "links.json"
    try:
        return {i["id"]: (i.get("url") or "").strip() for i in json.loads(f.read_text()) if i.get("id")}
    except (OSError, ValueError, KeyError):
        return {}  # reported by check_json


def norm_url(u):
    return u.strip().lower().rstrip("/")


LINKS = load_links()
URL_TO_ID = {norm_url(u): i for i, u in LINKS.items() if u and u != "#"}


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def exists_exact(path: Path) -> bool:
    """True if path exists with exactly this casing (works on case-insensitive disks)."""
    try:
        parts = path.resolve().relative_to(ROOT.resolve()).parts
    except ValueError:
        return False
    cur = ROOT
    for part in parts:
        if not cur.is_dir() or part not in {c.name for c in cur.iterdir()}:
            return False
        cur = cur / part
    return True


def resolve_local(value, page_dir):
    """Map a URL to a local path, or None if it's external / not checkable."""
    value = value.strip()
    if not value or value.startswith("#"):
        return None
    low = value.lower()
    if low.startswith(("http://", "https://", "//")):
        parts = urlsplit(value if not value.startswith("//") else "https:" + value)
        if parts.netloc.lower().removeprefix("www.") != DOMAIN:
            return None
        value = parts.path or "/"
    elif low.startswith(SKIP_SCHEMES):
        return None
    path = unquote(urlsplit(value).path)
    if not path:
        return None
    base = ROOT / path.lstrip("/") if path.startswith("/") else page_dir / path
    return base


def target_ok(base: Path) -> bool:
    if base.is_dir() or str(base).endswith("/"):
        return exists_exact(base / "index.html")
    return exists_exact(base) or exists_exact(base.with_name(base.name) / "index.html")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.headings = [], [], []
        self.imgs_no_alt = 0
        self.title = self.lang = self.description = None
        self.in_title = False
        self.blank_no_rel = 0
        self.link_attrs = []  # (line, tag, attrs) for links/forms checked against links.json

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.in_title = True
            self.title = ""
        if tag == "meta":
            if a.get("name") == "description":
                self.description = a.get("content")
            if a.get("property") in ("og:image", "og:url") and a.get("content") and a["property"] == "og:image":
                self.refs.append((line, a["content"]))
            if a.get("name") == "twitter:image" and a.get("content"):
                self.refs.append((line, a["content"]))
        if tag in ("a", "form"):
            self.link_attrs.append((line, tag, a))
        if "id" in a:
            self.ids.append((line, a["id"]))
        if tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1
            err(self.where, f"line {line}: <img> missing alt attribute")
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append((line, int(tag[1])))
        if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
            warn(self.where, f"line {line}: target=\"_blank\" link without rel=\"noopener\"")
        for t, attr in REF_ATTRS:
            if tag == t and a.get(attr):
                self.refs.append((line, a[attr]))
        for attr in ("srcset", "imagesrcset"):
            if a.get(attr):
                for candidate in a[attr].split(","):
                    if candidate.strip():
                        self.refs.append((line, candidate.strip().split()[0]))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def check_html():
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html"))
    parsed = {}
    for page in pages:
        p = PageParser()
        p.where = str(page.relative_to(ROOT))
        p.feed(page.read_text())
        parsed[page.resolve()] = p
    for page in pages:
        p = parsed[page.resolve()]
        where = p.where
        if not p.lang:
            err(where, "<html> missing lang attribute")
        if not (p.title or "").strip():
            err(where, "missing <title>")
        if not p.description:
            warn(where, "missing meta description")
        seen = set()
        for line, i in p.ids:
            if i in seen:
                err(where, f"line {line}: duplicate id \"{i}\"")
            seen.add(i)
        h1s = [h for h in p.headings if h[1] == 1]
        if len(h1s) != 1:
            warn(where, f"expected one <h1>, found {len(h1s)}")
        prev = 0
        for line, level in p.headings:
            if prev and level > prev + 1:
                warn(where, f"line {line}: heading jumps from h{prev} to h{level}")
            prev = level
        for line, tag, a in p.link_attrs:
            key = a.get("data-link-key") or a.get("data-form-action")
            attr = "action" if tag == "form" else "href"
            if key:
                if key not in LINKS:
                    err(where, f"line {line}: \"{key}\" is not an id in links.json")
                elif RELEASE and LINKS[key] not in ("", "#") and a.get(attr) != LINKS[key]:
                    err(where, f"line {line}: {attr} for \"{key}\" wasn't filled from links.json")
            elif a.get(attr) and norm_url(a[attr]) in URL_TO_ID:
                err(where, f"line {line}: {attr} duplicates links.json entry \"{URL_TO_ID[norm_url(a[attr])]}\"; use data-link-key=\"{URL_TO_ID[norm_url(a[attr])]}\" instead")
        for line, value in p.refs:
            base = resolve_local(value, page.parent)
            if base is None:
                if value.startswith("#") and len(value) > 1 and value[1:] not in seen:
                    warn(where, f"line {line}: #{value[1:]} not found on this page")
                continue
            if not target_ok(base):
                err(where, f"line {line}: broken reference \"{value}\"")
                continue
            frag = urlsplit(value).fragment
            if frag:
                target = base / "index.html" if base.is_dir() else base
                other = parsed.get(target.resolve())
                if other and frag not in {i for _, i in other.ids}:
                    warn(where, f"line {line}: \"{value}\" — no id \"{frag}\" on that page")


# ── Data file schemas ─────────────────────────────────
# Leaf types: "str" (non-empty), "text" (may be blank), "int", "bool", "url" (http(s)://, mailto:, /path or #),
# "weburl" (http(s):// only), "date" (YYYY-MM-DD), "datetime" (YYYY-MM-DDTHH:MM), "time" (HH:MM), ("enum", [...]). Containers: ("list", node) and
# ("obj", {field: (node, required)}). Unknown fields only warn (usually typos).
def obj(**fields):
    return ("obj", fields)


def req(node):
    return (node, True)


def opt(node):
    return (node, False)


SCHEMAS = {
    "team.json": ("list", obj(
        id=opt("str"), name=req("str"), role=req("text"),
        photo=opt("text"),
        group=opt(("enum", ["students", "mentors"])), grade=opt("text"), bio=opt("text"))),
    "alumni.json": ("list", obj(
        name=req("str"), year=req("int"), role=opt("text"), bio=opt("text"), photo=opt("text"))),
    "news.json": ("list", obj(
        date=req("date"), endDate=opt("date"), displayDate=opt("str"),
        title=req("str"), text=req("str"),
        link=opt("url"), linkLabel=opt("str"), image=opt("str"), imageAlt=opt("str"),
        featured=opt("bool"), expires=opt("date"), event=opt("bool"),
        location=opt("str"), address=opt("str"), startTime=opt("time"), endTime=opt("time"))),
    "sponsors.json": ("list", obj(
        id=req("str"), name=req("str"), banner=req("str"), website=req("weburl"),
        tier=req(("enum", ["platinum", "gold", "silver", "bronze"])))),
    "links.json": ("list", obj(
        id=req("str"), label=req("str"), url=req("url"), category=req("str"), listed=req("bool"))),
    "gallery.json": ("list", "str"),
    "gallery-captions.json": ("dict", "str"),
    "outreach.json": obj(
        enabled=opt("bool"), title=req("str"), intro=req("str"), invite=opt("text"),
        photo=opt(obj(src=req("str"), alt=req("str"))),
        items=opt(("list", obj(title=req("str"), text=req("str")))),
        buttons=opt(("list", obj(label=req("str"), url=opt("url"), link=opt("str"), primary=opt("bool"))))),
    "site.json": obj(
        heroPhoto=req(obj(src=req("str"), alt=req("str"))),
        aboutPhoto=req(obj(src=req("str"), alt=req("str")))),
    "calendar.json": obj(events=req(("list", obj(
        title=req("str"), start=req("str"), end=req("str"), allDay=req("bool"), location=opt("str"))))),
    "season.json": obj(
        enabled=opt("bool"), season=req("str"), game=opt("str"),
        gameTitle=opt("str"), gameSummary=opt("str"), kickoff=opt("date"), qualifiersStart=opt("str"),
        championship=opt(obj(name=req("str"), start=req("date"), end=req("date"))),
        stream=opt(obj(
            enabled=opt("bool"), autoplay=opt("bool"),
            events=req(("list", obj(
                name=req("str"), start=req("datetime"), end=req("datetime"),
                location=opt("str"), stream=opt("weburl"), youtubeChannelId=opt("str"),
                info=opt("weburl"), results=opt("weburl")))))),
        calendar=opt(obj(
            enabled=opt("bool"), title=opt("str"), feed=opt("weburl"),
            exclude=opt(("list", "str")), limit=opt("int"))),
        robot=opt(obj(
            enabled=opt("bool"), name=opt("str"), description=opt("text"),
            photos=opt(("list", obj(src=req("str"), caption=opt("str")))),
            specs=opt(("list", obj(label=req("str"), value=req("str")))),
            links=opt(("list", obj(label=req("str"), url=req("url"))))))),
}
PLACEHOLDERS = {}  # data file -> count of "Update..." values
UNIQUE_IDS = {"team.json", "sponsors.json", "links.json"}


def validate(node, value, path, where):
    kind = node if isinstance(node, str) else node[0]
    if kind == "str":
        if not isinstance(value, str) or not value.strip():
            err(where, f"{path}: expected non-empty text")
        elif value.strip().startswith("Update"):
            PLACEHOLDERS[where] = PLACEHOLDERS.get(where, 0) + 1
    elif kind == "text":  # like "str", but may be left blank
        if not isinstance(value, str):
            err(where, f"{path}: expected text")
    elif kind == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            err(where, f"{path}: expected a whole number")
    elif kind == "bool":
        if not isinstance(value, bool):
            err(where, f"{path}: expected true or false")
    elif kind in ("url", "weburl"):
        ok = isinstance(value, str) and (
            re.match(r"https?://\S+$", value) if kind == "weburl"
            else re.match(r"(https?://\S+|mailto:\S+|/\S*|#)$", value))
        if not ok:
            err(where, f"{path}: expected a {'web ' if kind == 'weburl' else ''}URL, got {value!r}")
    elif kind == "date":
        try:
            datetime.date.fromisoformat(value)
        except (TypeError, ValueError):
            err(where, f"{path}: expected a date like 2026-06-07, got {value!r}")
    elif kind == "datetime":
        try:
            datetime.datetime.fromisoformat(value)
        except (TypeError, ValueError):
            err(where, f"{path}: expected a date and time like 2026-02-14T09:00, got {value!r}")
    elif kind == "time":
        if not (isinstance(value, str) and re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", value)):
            err(where, f"{path}: expected a time like 17:30, got {value!r}")
    elif kind == "enum":
        if value not in node[1]:
            err(where, f"{path}: \"{value}\" is not one of {', '.join(node[1])}")
    elif kind == "list":
        if not isinstance(value, list):
            err(where, f"{path}: expected a list")
            return
        for i, item in enumerate(value):
            validate(node[1], item, f"{path}[{i}]", where)
    elif kind == "dict":
        if not isinstance(value, dict):
            err(where, f"{path}: expected an object")
            return
        for k, v in value.items():
            validate(node[1], v, f"{path}[\"{k}\"]", where)
    elif kind == "obj":
        if not isinstance(value, dict):
            err(where, f"{path}: expected an object")
            return
        for name, (child, required) in node[1].items():
            if name in value:
                validate(child, value[name], f"{path}.{name}", where)
            elif required:
                err(where, f"{path}: missing \"{name}\"")
        for name in value:
            if name not in node[1]:
                warn(where, f"{path}: unknown field \"{name}\" (typo?)")


def check_news(items, where):
    today = datetime.date.today()
    dated = [i for i in items if isinstance(i, dict) and isinstance(i.get("date"), str)]

    def parse(value):
        try:
            return datetime.date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    for n, i in enumerate(dated):
        start, end = parse(i["date"]), parse(i.get("endDate") or i["date"])
        if start and end and end < start:
            err(where, f"$[{n}]: endDate is before date")
        if i.get("event") and end and end < today and not i.get("expires"):
            warn(where, f"\"{i.get('title')}\" is a past event with no expires date; it will keep showing")
        if i.get("image") and not i.get("imageAlt"):
            pass  # decorative by default; the title sits right next to it
    live = [i for i in dated if not i.get("expires") or (parse(i["expires"]) or today) >= today]
    if dated and not live:
        warn(where, "every news item has expired, so the news section will be hidden")


def check_schema(name, data, where):
    schema = SCHEMAS.get(name)
    if not schema:
        return
    validate(schema, data, "$", where)
    if name in UNIQUE_IDS and isinstance(data, list):
        seen = set()
        for item in data:
            i = item.get("id") if isinstance(item, dict) else None
            if i in seen:
                err(where, f"duplicate id \"{i}\"")
            seen.add(i)
    if name == "news.json" and isinstance(data, list):
        check_news(data, where)
    if name == "season.json" and isinstance(data, dict):
        for n, e in enumerate((data.get("stream") or {}).get("events", [])):
            try:
                if datetime.datetime.fromisoformat(e["end"]) < datetime.datetime.fromisoformat(e["start"]):
                    err(where, f"stream.events[{n}]: end is before start")
            except (KeyError, TypeError, ValueError):
                pass  # reported by the schema
            if not e.get("stream") and not e.get("youtubeChannelId"):
                warn(where, f"stream.events[{n}] (\"{e.get('name')}\") has no stream link yet")


def local_paths_in(node):
    if isinstance(node, str):
        if re.match(r"^/(images|assets)/", node):
            yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from local_paths_in(v)
    elif isinstance(node, list):
        for v in node:
            yield from local_paths_in(v)


def check_json():
    files = sorted((ROOT / "assets" / "data").glob("*.json")) + [ROOT / "site.webmanifest"]
    for f in files:
        if not f.exists():
            continue
        where = str(f.relative_to(ROOT))
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            err(where, f"invalid JSON ({e})")
            continue
        check_schema(f.name, data, where)
        for path in local_paths_in(data):
            if not exists_exact(ROOT / path.lstrip("/")):
                err(where, f"missing file \"{path}\"")


def check_xml():
    import xml.etree.ElementTree as ET
    for name in ("sitemap.xml", "sitemap.xsl", "news.xml"):
        f = ROOT / name
        if not f.exists():
            continue
        try:
            ET.parse(f)
        except ET.ParseError as e:
            err(name, f"not well-formed XML ({e})")


def check_llms():
    """Every page in the sitemap should be described in llms.txt (what AI tools read)."""
    llms, sitemap = ROOT / "llms.txt", ROOT / "sitemap.xml"
    if not (llms.exists() and sitemap.exists()):
        return
    text = llms.read_text()
    for url in re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text()):
        if url not in text:
            warn("llms.txt", f"doesn't mention {url}")


def check_big_images():
    """Phone photos dropped in as-is are huge; the build shrinks them, but flag them early."""
    for f in sorted((ROOT / "images").rglob("*")):
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".avif") \
                and "thumbs" not in f.parts and f.stat().st_size > 1_500_000:
            warn(str(f.relative_to(ROOT)), f"is {f.stat().st_size // 1_000_000} MB; run python3 scripts/build.py with Pillow installed (pip install -r requirements.txt) to shrink it before committing")


def check_unreferenced():
    """Images and downloads that nothing on the site points to (likely leftovers)."""
    suffixes = {".html", ".css", ".js", ".json", ".xml", ".xsl", ".txt", ".webmanifest", ".md", ".py", ".yml"}
    corpus = ""
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix in suffixes and ".git" not in f.parts and "thumbs" not in f.parts:
            corpus += f.read_text(errors="ignore")
    for folder in ("images", "assets/files", "assets/fonts"):
        for f in sorted((ROOT / folder).rglob("*")):
            if f.is_file() and not f.name.startswith(".") and "thumbs" not in f.parts and f.suffix != ".txt" and f.name not in corpus:
                warn(str(f.relative_to(ROOT)), "isn't referenced anywhere (remove it, or link to it)")


def main():
    check_xml()
    check_json()
    check_llms()
    check_unreferenced()
    check_big_images()
    for where, count in PLACEHOLDERS.items():
        warn(where, f"{count} placeholder value(s) starting with \"Update\" still present")
    check_html()
    for w in warnings:
        print(f"WARNING {w}")
    for e in errors:
        print(f"ERROR   {e}")
    print(f"\nSite check: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
