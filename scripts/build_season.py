#!/usr/bin/env python3
"""Build the Season page from assets/data/season.json.

Fills the marked regions of season/index.html:
  <!-- @season --> ... <!-- @endseason -->          page content
  <!-- @seasonmeta --> ... <!-- @endseasonmeta -->  description meta tags (+ noindex when off)
and the current-season stat in the home page hero (<!-- @seasonstat -->).

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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "season" / "index.html"
TIMEZONE = "America/Los_Angeles"
KEEP_DAYS = 90  # events that ended longer ago than this are dropped from the page


def esc(value):
    return html.escape(str(value), quote=True)


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


def robot_section(robot):
    photos = robot.get("photos", [])
    specs = robot.get("specs", [])
    links = robot.get("links", [])
    ids = link_ids()
    title = robot.get("name") or "Our robot"
    parts = ['<section class="section section--alt" id="robot">', '  <div class="section-inner">',
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
        side += ["          " + anchor(l["label"] + " →", l["url"], ids, "btn-outline") for l in links]
        side.append("        </div>")
    if side:
        parts.append('      <div class="robot-side">')
        parts += side
        parts.append("      </div>")
    parts += ["    </div>", "  </div>", "</section>"]
    return "\n".join(parts)


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
    eyebrow = " · ".join(x for x in (f'{data.get("season", "")} season'.strip(), data.get("game", "")) if x and x != "season")
    hero = f'''<section class="page-hero">
  <p class="eyebrow">{esc(eyebrow)}</p>
  <h1>Season {esc(data.get("season", ""))}</h1>
  <p>Watch our events live and see the robot we built.</p>
</section>'''
    blocks = [hero]
    if data.get("stream", {}).get("enabled", True):
        blocks.append(stream_section(data.get("stream", {}), today))
    if data.get("robot", {}).get("enabled", True) and data.get("robot"):
        blocks.append(robot_section(data["robot"]))
    return "\n\n".join(blocks)


def fill(text, start_marker, end_marker, body):
    rx = re.compile(rf"^(?P<i>[ \t]*){re.escape(start_marker)}\n.*?^[ \t]*{re.escape(end_marker)}", re.S | re.M)

    def sub(m):
        ind = m["i"]
        inner = "\n".join(ind + line if line.strip() else "" for line in body.split("\n")) if body else ""
        return f"{ind}{start_marker}\n" + (inner + "\n" if inner else "") + f"{ind}{end_marker}"

    if not rx.search(text):
        raise SystemExit(f"error: season/index.html is missing {start_marker} ... {end_marker}")
    return rx.sub(sub, text)


def main():
    data = json.loads((ROOT / "assets" / "data" / "season.json").read_text())
    today = datetime.date.today()
    text = PAGE.read_text()
    new = fill(text, "<!-- @season -->", "<!-- @endseason -->", page_content(data, today))
    season, game = data.get("season", ""), data.get("game", "")
    summary = (f"Watch Truckee Snowbotics FTC Team #32587 compete live and see our robot for the "
               f"{season} FIRST Tech Challenge season" + (f", {game}." if game else "."))
    meta = [f'<meta name="description" content="{esc(summary)}" />',
            f'<meta property="og:description" content="{esc(summary)}" />',
            f'<meta name="twitter:description" content="{esc(summary)}" />']
    if not data.get("enabled", True):
        meta.append('<meta name="robots" content="noindex" />')
    new = fill(new, "<!-- @seasonmeta -->", "<!-- @endseasonmeta -->", "\n".join(meta))
    # Home page hero stat for the current season
    home = ROOT / "index.html"
    htext = home.read_text()
    stat = (f'<div class="hstat">\n  <dt class="hstat-key">{esc(season)} season</dt>\n'
            f'  <dd class="hstat-val">{esc(game or "FTC")}</dd>\n</div>')
    hnew = fill(htext, "<!-- @seasonstat -->", "<!-- @endseasonstat -->", stat)
    if hnew != htext:
        home.write_text(hnew)
    if new != text:
        PAGE.write_text(new)
    state = "on" if data.get("enabled", True) else "OFF"
    print(f"Season page is {state}")


if __name__ == "__main__":
    sys.exit(main())
