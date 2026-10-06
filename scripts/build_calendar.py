#!/usr/bin/env python3
"""Fetch the public FIRST Nevada FTC calendar (an iCal feed) into assets/data/calendar.json.

The Season page's "Northern Nevada FTC calendar" section is rendered from that file by
build_season.py. This script runs on every build, and the daily deploy keeps it fresh.

If the feed can't be reached the existing calendar.json is kept (and a warning printed), so
a Google or network hiccup never breaks a deploy. Does nothing when season.json has
calendar.enabled false or no calendar.feed.

calendar.json: {"events": [{"title", "start", "end", "allDay", "location"}...]} with Pacific
times as "YYYY-MM-DDTHH:MM" (all-day events use "YYYY-MM-DD"). Only events that haven't ended
yet are kept; cancelled events are dropped. Recurring events (RRULE) aren't expanded; the
feed's current events don't use them, and a warning names any that would matter.
"""
import datetime
import json
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

from _lib import ROOT

PACIFIC = ZoneInfo("America/Los_Angeles")
UTC = datetime.timezone.utc
OUTPUT = ROOT / "assets" / "data" / "calendar.json"


def unescape(text):
    return re.sub(r"\\([,;nN\\])", lambda m: "\n" if m.group(1) in "nN" else m.group(1), text)


def unfold(raw):
    return re.sub(r"\r?\n[ \t]", "", raw).replace("\r", "").split("\n")


def parse_time(prop, params, value):
    """-> (datetime in Pacific, is_all_day)."""
    if "VALUE=DATE" in params or re.fullmatch(r"\d{8}", value):
        d = datetime.datetime.strptime(value, "%Y%m%d")
        return d.replace(tzinfo=PACIFIC), True
    if value.endswith("Z"):
        return datetime.datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC).astimezone(PACIFIC), False
    local = datetime.datetime.strptime(value, "%Y%m%dT%H%M%S")
    tz = re.search(r"TZID=([^;:]+)", params)
    try:
        zone = ZoneInfo(tz.group(1)) if tz else PACIFIC
    except Exception:  # unknown zone name: treat as Pacific
        zone = PACIFIC
    return local.replace(tzinfo=zone).astimezone(PACIFIC), False


def parse_events(raw, today):
    events, recurring = [], []
    for block in re.findall(r"BEGIN:VEVENT\n(.*?)\nEND:VEVENT", "\n".join(unfold(raw)), re.S):
        props = {}
        for line in block.split("\n"):
            if ":" not in line:
                continue
            head, value = line.split(":", 1)
            name, _, params = head.partition(";")
            props.setdefault(name.upper(), (params, value))
        if props.get("STATUS", ("", ""))[1].upper() == "CANCELLED" or "DTSTART" not in props:
            continue
        title = unescape(props.get("SUMMARY", ("", "Untitled event"))[1]).strip()
        start, all_day = parse_time("DTSTART", *props["DTSTART"])
        if "DTEND" in props:
            end, _ = parse_time("DTEND", *props["DTEND"])
        else:
            end = start
        if all_day:  # iCal all-day end dates are exclusive
            end = max(start, end - datetime.timedelta(days=1))
        if "RRULE" in props:
            until = re.search(r"UNTIL=(\d{8})", props["RRULE"][1])
            if not until or until.group(1) >= f"{today:%Y%m%d}":
                recurring.append(title)
            continue
        if end.date() < today:
            continue
        fmt = "%Y-%m-%d" if all_day else "%Y-%m-%dT%H:%M"
        event = {"title": title, "start": start.strftime(fmt), "end": end.strftime(fmt), "allDay": all_day}
        if props.get("LOCATION", ("", ""))[1].strip():
            event["location"] = unescape(props["LOCATION"][1]).strip()
        events.append(event)
    events.sort(key=lambda e: (e["start"], e["title"]))
    return events, recurring


def main():
    season = json.loads((ROOT / "assets" / "data" / "season.json").read_text())
    cal = season.get("calendar") or {}
    if not cal.get("enabled", True) or not cal.get("feed"):
        print("Calendar: off")
        return 0
    today = datetime.datetime.now(PACIFIC).date()
    try:
        req = urllib.request.Request(cal["feed"], headers={"User-Agent": "snowbotics-site-build"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", "replace")
        if "BEGIN:VCALENDAR" not in raw:
            raise ValueError("response isn't an iCal feed")
    except Exception as e:  # noqa: BLE001 - any failure means "keep the last good copy"
        print(f"WARNING calendar feed unavailable ({e}); keeping the existing calendar.json")
        return 0
    events, recurring = parse_events(raw, today)
    for title in sorted(set(recurring)):
        print(f"WARNING calendar: recurring event not expanded: {title}")
    text = json.dumps({"events": events}, indent=2, ensure_ascii=False) + "\n"
    if not OUTPUT.exists() or OUTPUT.read_text() != text:
        OUTPUT.write_text(text)
    print(f"Calendar: {len(events)} upcoming events from the feed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
