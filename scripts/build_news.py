#!/usr/bin/env python3
"""Build the news section and feed from assets/data/news.json.

Writes, on every build:
  - the whole "News & Updates" section (heading, cards, plus Event structured data for
    upcoming events) into every page that has <!-- @news --> ... <!-- @endnews --> markers
    (the home page), so the news is real HTML for search engines and visitors without
    JavaScript. With no news to show (empty file, or everything expired), the section is
    left out entirely;
  - news.xml, an RSS feed.

Item fields (all dates are ISO, YYYY-MM-DD):
  date          required; sort key: upcoming items soonest-first, then past items newest-first
  title, text   required
  endDate       optional; for a span of days
  displayDate   optional text shown instead of the formatted date ("Post-Season 2026")
  link          optional URL; shown as a "Read more" link (linkLabel changes the words)
  image         optional /images/... path (imageAlt is its alt text; empty by default)
  featured      optional true: pinned above the rest and highlighted
  expires       optional; the item is hidden after this date (also checked in the
                browser, so it disappears even between deploys)
  event         optional true: publishes Event structured data while it's upcoming
  location, address, startTime, endTime ("HH:MM", Pacific time)  optional; for events
"""
import datetime
import html
import json
import os
import re
import sys
from email.utils import format_datetime

from _lib import ROOT, indent, marker_pattern, read_domain

DOMAIN = read_domain()
TIMEZONE = "America/Los_Angeles"
TODAY = datetime.date.fromisoformat(os.environ.get("NEWS_TODAY") or datetime.date.today().isoformat())
MARKER = marker_pattern("news")


def day(value):
    return datetime.date.fromisoformat(value)


def long_date(d):
    return f"{d:%A}, {d:%B} {d.day}, {d.year}"


def date_text(item):
    if item.get("displayDate"):
        return item["displayDate"]
    start, end = day(item["date"]), day(item.get("endDate") or item["date"])
    if start == end:
        return long_date(start)
    if (start.year, start.month) == (end.year, end.month):
        return f"{start:%B} {start.day}–{end.day}, {start.year}"
    if start.year == end.year:
        return f"{start:%B} {start.day} – {end:%B} {end.day}, {end.year}"
    return f"{start:%B} {start.day}, {start.year} – {end:%B} {end.day}, {end.year}"


def slug(item):
    words = re.sub(r"[^a-z0-9]+", "-", item["title"].lower()).strip("-")
    return f"news-{item['date']}-{words}"[:80].rstrip("-")


def active_items(items):
    shown = [i for i in items if not i.get("expires") or day(i["expires"]) >= TODAY]

    def order(i):
        d = day(i.get("endDate") or i["date"])
        upcoming = d >= TODAY
        # featured first; then upcoming items soonest-first; then past items newest-first
        return (not i.get("featured"), not upcoming,
                day(i["date"]).toordinal() if upcoming else -day(i["date"]).toordinal(), i["title"])

    return sorted(shown, key=order)


def norm(url):
    return url.strip().lower().rstrip("/")


def attr(value):
    return html.escape(str(value), quote=True)


def card(item, link_ids):
    classes = ["news-card"]
    if item.get("featured"):
        classes.append("news-card--featured")
    if item.get("image"):
        classes.append("news-card--media")
    expires = f' data-expires="{attr(item["expires"])}"' if item.get("expires") else ""
    parts = [
        f'<article class="{" ".join(classes)}" id="{slug(item)}"{expires}>',
        f'  <time class="news-card-date" datetime="{attr(item["date"])}">{html.escape(date_text(item))}</time>',
        '  <div class="news-card-body">',
        f'    <h3 class="news-card-title">{html.escape(item["title"])}</h3>',
        f'    <p class="news-card-text">{html.escape(item["text"])}</p>',
    ]
    if item.get("link"):
        label = html.escape(item.get("linkLabel") or "Read more")
        key = link_ids.get(norm(item["link"]))
        external = item["link"].startswith("http")
        href = '#" data-link-key="' + key if key else attr(item["link"])
        extra = ' target="_blank" rel="noopener"' if external else ""
        parts.append(f'    <a class="news-card-link" href="{href}"{extra}>{label} →</a>')
    parts.append("  </div>")
    if item.get("image"):
        alt = attr(item.get("imageAlt", ""))
        parts.append(f'  <img class="news-card-media" src="{attr(item["image"])}" alt="{alt}" loading="lazy" decoding="async" />')
    parts.append("</article>")
    return "\n".join(parts)


def pacific(d, hhmm):
    """ISO datetime with the correct Pacific offset for that date, or just the date."""
    if not hhmm:
        return d.isoformat()
    try:
        from zoneinfo import ZoneInfo
        hour, minute = map(int, hhmm.split(":"))
        return datetime.datetime(d.year, d.month, d.day, hour, minute, tzinfo=ZoneInfo(TIMEZONE)).isoformat()
    except Exception:
        return d.isoformat()


def event_ld(item):
    end = day(item.get("endDate") or item["date"])
    if not item.get("event") or end < TODAY:
        return None
    start = day(item["date"])
    data = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": item["title"],
        "description": item["text"],
        "startDate": pacific(start, item.get("startTime")),
        "endDate": pacific(end, item.get("endTime")),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "organizer": {"@type": "Organization", "name": "Truckee Snowbotics", "url": f"https://{DOMAIN}/"},
        "url": item["link"] if str(item.get("link", "")).startswith("http") else f"https://{DOMAIN}/#{slug(item)}",
    }
    if item.get("location"):
        place = {"@type": "Place", "name": item["location"]}
        if item.get("address"):
            place["address"] = item["address"]
        data["location"] = place
    if item.get("image"):
        data["image"] = f"https://{DOMAIN}{item['image']}"
    body = json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{body}\n</script>'


def render(items, link_ids):
    """The whole news section, or "" when there is nothing to show."""
    if not items:
        return ""
    chunks = [card(i, link_ids) for i in items]
    chunks += [ld for ld in (event_ld(i) for i in items) if ld]
    cards = "\n".join("      " + line if line.strip() else "" for line in "\n".join(chunks).split("\n"))
    return (
        '<section class="section" id="news">\n'
        '  <div class="section-inner">\n'
        '    <div class="section-header">\n'
        "      <h2>News &amp; Updates</h2>\n"
        "    </div>\n"
        '    <div class="news-grid" id="news-grid">\n'
        f"{cards}\n"
        "    </div>\n"
        "  </div>\n"
        "</section>"
    )


def feed(items):
    out = []
    for i in items:
        d = day(i["date"])
        permalink = f"https://{DOMAIN}/#{slug(i)}"
        link = i["link"] if str(i.get("link", "")).startswith("http") else permalink
        stamp = format_datetime(datetime.datetime(d.year, d.month, d.day, 12, tzinfo=datetime.timezone.utc))
        out.append(
            "    <item>\n"
            f"      <title>{html.escape(i['title'])}</title>\n"
            f"      <link>{html.escape(link)}</link>\n"
            f'      <guid isPermaLink="true">{permalink}</guid>\n'
            f"      <pubDate>{stamp}</pubDate>\n"
            f"      <description>{html.escape(i['text'])}</description>\n"
            "    </item>\n"
        )
    newest = max((day(i["date"]) for i in items), default=TODAY)
    built = format_datetime(datetime.datetime(newest.year, newest.month, newest.day, 12, tzinfo=datetime.timezone.utc))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Truckee Snowbotics News</title>\n"
        f"    <link>https://{DOMAIN}/</link>\n"
        "    <description>News and updates from Truckee Snowbotics, FTC Team #32587.</description>\n"
        "    <language>en-us</language>\n"
        f"    <lastBuildDate>{built}</lastBuildDate>\n"
        f'    <atom:link href="https://{DOMAIN}/news.xml" rel="self" type="application/rss+xml" />\n'
        + "".join(out)
        + "  </channel>\n</rss>\n"
    )


def main():
    items = json.loads((ROOT / "assets" / "data" / "news.json").read_text())
    links = json.loads((ROOT / "assets" / "data" / "links.json").read_text())
    link_ids = {norm(l["url"]): l["id"] for l in links if l.get("url") and l["url"] != "#"}
    shown = active_items(items)
    body = render(shown, link_ids)

    changed = 0
    for page in sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/index.html")):
        text = page.read_text()
        new = MARKER.sub(
            lambda m: f"{m['indent']}<!-- @news -->\n{indent(body, m['indent'])}\n{m['indent']}<!-- @endnews -->"
            if body else f"{m['indent']}<!-- @news -->\n{m['indent']}<!-- @endnews -->",
            text,
        )
        if new != text:
            page.write_text(new)
            changed += 1
    (ROOT / "news.xml").write_text(feed(shown))
    print(f"Rendered {len(shown)} of {len(items)} news items into {changed} page(s) and news.xml")


if __name__ == "__main__":
    sys.exit(main())
