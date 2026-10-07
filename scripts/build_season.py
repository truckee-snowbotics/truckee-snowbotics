#!/usr/bin/env python3
"""Build the Season page from assets/data/season.json.

Fills the marked regions of season/index.html:
  <!-- @season --> ... <!-- @endseason -->          page content
  <!-- @seasonmeta --> ... <!-- @endseasonmeta -->  description meta tag (+ noindex when off)
and the home page hero's calendar button (<!-- @seasoncta -->).

"enabled": false in season.json turns the whole page off: the page shows only a short
"not available" message and is marked noindex, and the Season links disappear from the
site navigation and sitemap (build_pages.py and build_sitemap.py read the same flag).

Event times in season.json are Pacific time; here they become absolute timestamps so the
browser can decide, for any visitor, whether an event is live right now.
"""
import datetime
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

from _lib import ROOT, esc, fill_markers

PAGE = ROOT / "season" / "index.html"
TIMEZONE = "America/Los_Angeles"
KEEP_DAYS = 90  # events that ended longer ago than this are dropped from the page


def pacific(value):
    """'2026-02-14T09:00' (Pacific) -> aware datetime."""
    from zoneinfo import ZoneInfo
    return datetime.datetime.fromisoformat(value).replace(tzinfo=ZoneInfo(TIMEZONE))


def clock(dt):
    return f"{dt.hour % 12 or 12}:{dt:%M} {'AM' if dt.hour < 12 else 'PM'}"


def when_text(start, end):
    zone = "PT"
    if start.date() == end.date():
        return f"{start:%A}, {start:%B} {start.day} · {clock(start)} – {clock(end)} {zone}"
    return (f"{start:%a}, {start:%b} {start.day}, {clock(start)} – "
            f"{end:%a}, {end:%b} {end.day}, {clock(end)} {zone}")


def link_ids():
    links = json.loads((ROOT / "assets" / "data" / "links.json").read_text())
    return {l["url"].strip().lower().rstrip("/"): l["id"] for l in links if l.get("url") and l["url"] != "#"}


def anchor(label, url, ids, css):
    key = ids.get(url.strip().lower().rstrip("/"))
    if key:
        return f'<a class="{css}" href="#" data-link-key="{key}" target="_blank" rel="noopener">{esc(label)}</a>'
    external = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    return f'<a class="{css}" href="{esc(url)}"{external}>{esc(label)}</a>'


def event_card(e, ids):
    start, end = pacific(e["start"]), pacific(e["end"])
    attrs = [f'data-name="{esc(e["name"])}"', f'data-start="{start.isoformat()}"', f'data-end="{end.isoformat()}"']
    if e.get("stream"):
        attrs.append(f'data-stream="{esc(e["stream"])}"')
    if e.get("youtubeChannelId"):
        attrs.append(f'data-youtube-channel="{esc(e["youtubeChannelId"])}"')
    if e.get("info"):
        attrs.append(f'data-info="{esc(e["info"])}"')
    if e.get("results"):
        attrs.append(f'data-results="{esc(e["results"])}"')
    lines = [
        f'<article class="season-event" {" ".join(attrs)}>',
        f'  <time class="season-event-when" datetime="{start.isoformat()}">{esc(when_text(start, end))}</time>',
        f'  <h3 class="season-event-name">{esc(e["name"])}</h3>',
    ]
    if e.get("location"):
        lines.append(f'  <p class="season-event-where">{esc(e["location"])}</p>')
    links = []
    if e.get("stream"):
        links.append(anchor("Watch stream", e["stream"], ids, "season-event-link"))
    if e.get("info"):
        links.append(anchor("Event page", e["info"], ids, "season-event-link"))
    if e.get("results"):
        links.append(anchor("Live results", e["results"], ids, "season-event-link"))
    if links:
        lines.append('  <div class="season-event-links">' + " ".join(links) + "</div>")
    lines.append("</article>")
    return "\n".join(lines)


def stream_section(stream, today):
    events = [e for e in stream.get("events", []) if pacific(e["end"]).date() + datetime.timedelta(days=KEEP_DAYS) >= today]
    events.sort(key=lambda e: e["start"])
    ids = link_ids()
    autoplay = "true" if stream.get("autoplay", True) else "false"
    listing = ""
    if events:
        cards = '<div class="season-events" id="season-events">\n' + "\n".join(event_card(e, ids) for e in events) + "\n</div>"
        listing = '    <h3 class="stream-events-title">Event schedule</h3>\n' + "\n".join("    " + line for line in cards.split("\n")) + "\n"
    return f'''<section class="section" id="watch" data-autoplay="{autoplay}">
  <div class="section-inner">
    <div class="section-header">
      <h2>Watch live</h2>
      <p>When one of our events is on air, the broadcast appears here automatically.</p>
    </div>
    <div class="stream-stage" id="stream-stage">
      <div class="stream-panel">
        <p class="stream-panel-title">Live stream</p>
        <p class="stream-panel-text">Event streams show up here while we compete. The schedule is below.</p>
      </div>
    </div>
{listing}  </div>
</section>'''


def robot_link(l, ids):
    """A robot button: "url" is a web address; "link" is an id from links.json (hidden while its url is #)."""
    if l.get("link"):
        if l["link"] not in set(ids.values()) | placeholder_ids():
            sys.exit(f'error: season.json robot link "{l.get("label")}": no "{l["link"]}" in links.json')
        return f'<a class="btn-outline" href="#" data-link-key="{esc(l["link"])}" target="_blank" rel="noopener">{esc(l["label"])}</a>'
    return anchor(l["label"], l["url"], ids, "btn-outline")


def placeholder_ids():
    return {l["id"] for l in json.loads((ROOT / "assets" / "data" / "links.json").read_text())}


def robot_section(robot):
    photos = robot.get("photos", [])
    specs = robot.get("specs", [])
    links = robot.get("links", [])
    ids = link_ids()
    title = robot.get("name") or "Our robot"
    parts = [f'<section class="section section--band" id="robot">', '  <div class="section-inner">',
             '    <div class="section-header">', f'      <h2>{esc(title)}</h2>']
    if robot.get("description"):
        parts.append(f'      <p>{esc(robot["description"])}</p>')
    parts += ["    </div>", '    <div class="robot-layout">']
    if photos:
        parts.append('      <div class="robot-photos">')
        for n, p in enumerate(photos):
            lead = " robot-photo--lead" if n == 0 else ""
            caption = p.get("caption", "")
            parts.append(f'        <figure class="robot-photo{lead}"><img src="{esc(p["src"])}" alt="{esc(caption)}" loading="lazy" decoding="async" />'
                         + (f"<figcaption>{esc(caption)}</figcaption>" if caption else "") + "</figure>")
        parts.append("      </div>")
    side = []
    if specs:
        side.append('        <dl class="spec-list">')
        side += [f'          <div><dt>{esc(s["label"])}</dt><dd>{esc(s["value"])}</dd></div>' for s in specs]
        side.append("        </dl>")
    if links:
        side.append('        <div class="robot-links">')
        side += ["          " + robot_link(l, ids) for l in links]
        side.append("        </div>")
    if side:
        parts.append('      <div class="robot-side">')
        parts += side
        parts.append("      </div>")
    parts += ["    </div>", "  </div>", "</section>"]
    return "\n".join(parts)


def calendar_section(cal):
    """The Season page's calendar: an embedded Google Calendar (settings under "calendar" in season.json)."""
    cid = cal["id"].strip()
    tz = cal.get("timezone") or TIMEZONE
    mode = {"month": "MONTH", "week": "WEEK", "agenda": "AGENDA"}.get((cal.get("view") or "month").lower(), "MONTH")
    height = int(cal.get("height") or 700)
    q = urllib.parse.quote
    src = ("https://calendar.google.com/calendar/embed?" + "&".join([
        f"src={q(cid, safe='')}", f"ctz={q(tz, safe='')}", f"mode={mode}", "hl=en",
        "showTitle=0", "showPrint=0", "showTabs=0", "showCalendars=0", "showTz=0", "bgcolor=%23ffffff"]))
    title = cal.get("title") or "Calendar"
    ids = link_ids()
    links = [f'<a class="season-event-link" href="https://calendar.google.com/calendar/ical/{q(cid, safe="")}/public/basic.ics" target="_blank" rel="noopener">iCal feed &rarr;</a>']
    for l in cal.get("links", []):
        links.append(robot_link(dict(l, label=l["label"] + " →"), ids).replace("btn-outline", "season-event-link"))
    description = f"      <p>{esc(cal['description'])}</p>\n" if cal.get("description") else ""
    return f'''<section class="section" id="calendar">
  <div class="section-inner">
    <div class="section-header">
      <h2>{esc(title)}</h2>
{description}    </div>
    <iframe class="gcal" src="{src}" title="{esc(title)}" style="height:{height}px" loading="lazy"></iframe>
    <div class="cal-links">{" ".join(links)}</div>
  </div>
</section>'''


def page_content(data, today):
    if not data.get("enabled", True):
        return '''<section class="section" id="season-off">
  <div class="section-inner section-inner--narrow">
    <div class="section-header">
      <h2>Season page</h2>
      <p>This page isn't available right now.</p>
    </div>
    <a href="/" class="btn-primary">Back to home</a>
  </div>
</section>'''
    hero = f'''<section class="page-hero">
  <h1>Season {esc(data.get("season", ""))}</h1>
  <p>See where we compete, meet our robot, and watch our events live.</p>
</section>'''
    blocks = [hero]
    # Page order: calendar, robot, then the live stream.
    if data.get("calendar", {}).get("enabled", True) and data.get("calendar", {}).get("id"):
        blocks.append(calendar_section(data["calendar"]))
    if data.get("robot", {}).get("enabled", True) and data.get("robot"):
        blocks.append(robot_section(data["robot"]))
    if data.get("stream", {}).get("enabled", True):
        blocks.append(stream_section(data.get("stream", {}), today))
    return "\n\n".join(blocks)


def long_date(d):
    return f"{d:%B} {d.day}, {d.year}"


def date_range(a, b):
    if a == b:
        return long_date(a)
    if (a.year, a.month) == (b.year, b.month):
        return f"{a:%B} {a.day}–{b.day}, {a.year}"
    if a.year == b.year:
        return f"{a:%B} {a.day} – {b:%B} {b.day}, {b.year}"
    return f"{long_date(a)} – {long_date(b)}"


def info_text(data):
    """Season sentences for the Information page, from season.json."""
    challenge = ""
    if data.get("gameTitle"):
        challenge = f" This season's game is {data['gameTitle']}"
        challenge += f", {data['gameSummary']}." if data.get("gameSummary") else "."
    season = ""
    kickoff = data.get("kickoff")
    if kickoff:
        season = f"The {data.get('season', '')} season kicked off on {long_date(datetime.date.fromisoformat(kickoff))}. "
    season += "Teams compete at league meets and qualifying tournaments"
    if data.get("qualifiersStart"):
        season += f" starting in {data['qualifiersStart']}"
    champ = data.get("championship")
    if champ:
        rng = date_range(datetime.date.fromisoformat(champ["start"]), datetime.date.fromisoformat(champ["end"]))
        season += f", advance to regional championships, and top teams qualify for the {champ['name']} ({rng})."
    else:
        season += ", then advance to regional championships."
    return challenge, season


def fill_inline(text, name, value):
    rx = re.compile(rf"(<!-- @{name} -->)(.*?)(<!-- @end{name} -->)", re.S)
    if not rx.search(text):
        raise SystemExit(f"error: missing <!-- @{name} --> ... <!-- @end{name} -->")
    return rx.sub(lambda m: m.group(1) + html.escape(value, quote=False) + m.group(3), text)


def cta_html(data, css, label):
    """Button to the Season page's calendar; empty when the Season page or its calendar is off."""
    cal = data.get("calendar") or {}
    if data.get("enabled", True) and cal.get("enabled", True) and cal.get("id"):
        return f'<a href="/season/#calendar" class="{css}">{esc(label)}</a>'
    return ""


def main():
    data = json.loads((ROOT / "assets" / "data" / "season.json").read_text())
    today = datetime.date.today()
    text = PAGE.read_text()
    new = fill_markers(text, "season", page_content(data, today), PAGE)
    season, game = data.get("season", ""), data.get("game", "")
    summary = (f"Watch Truckee Snowbotics FTC Team #32587 compete live and see our robot for the "
               f"{season} FIRST Tech Challenge season" + (f", {game}." if game else "."))
    # build_meta.py derives the og:/twitter: tags (and drops the canonical URL when noindex) from these
    meta = [f'<meta name="description" content="{esc(summary)}" />']
    if not data.get("enabled", True):
        meta.append('<meta name="robots" content="noindex" />')
    new = fill_markers(new, "seasonmeta", "\n".join(meta), PAGE)
    # Information page: this season's game and dates
    info = ROOT / "information" / "index.html"
    itext = info.read_text()
    challenge, season_sentence = info_text(data)
    inew = fill_inline(itext, "seasonchallenge", challenge)
    inew = fill_inline(inew, "seasonsummary", season_sentence)
    # Information page: button to our calendar (only while the Season page and its calendar are on)
    inew = fill_markers(inew, "calendarbtn", cta_html(data, "btn-primary", "Our event calendar"), info)
    if inew != itext:
        info.write_text(inew)
    # Home page hero button to the calendar (only while the Season page and its calendar are on)
    home = ROOT / "index.html"
    htext = home.read_text()
    hnew = fill_markers(htext, "seasoncta", cta_html(data, "btn-outline", "Event calendar"), home)
    if hnew != htext:
        home.write_text(hnew)
    if new != text:
        PAGE.write_text(new)
    state = "on" if data.get("enabled", True) else "OFF"
    print(f"Season page is {state}")


if __name__ == "__main__":
    sys.exit(main())
