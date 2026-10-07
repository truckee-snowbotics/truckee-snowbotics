#!/usr/bin/env python3
"""Weekly site health check. Prints a Markdown report; the health workflow turns it
into a GitHub issue. Run locally with:  python3 scripts/health_check.py

Checks
  - outside links still work (links.json, banner link, season stream/event/robot links,
    sponsor websites). Sites that block bots (403/429/999) are listed as "couldn't verify"
    and never open an issue on their own.
  - events starting within the next 7 days that still have no stream link
  - .well-known/security.txt expiring within 45 days
  - a season-rollover checklist during the first week of September

Output files (used by the workflow):
  health-report.md     the report (only meaningful when findings exist)
  health-findings      "1" if there is anything to open or keep an issue for, else "0"
  rollover-checklist.md  written only when the checklist is due
Exit code is always 0; the workflow decides what to do with the findings.
"""
import datetime
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date.fromisoformat(os.environ.get("HEALTH_TODAY") or datetime.date.today().isoformat())
TIMEOUT = 20
UA = "Mozilla/5.0 (compatible; SnowboticsLinkCheck/1.0; +https://snowbotics.org)"
SOFT_STATUS = {401, 403, 405, 406, 429, 451, 999}  # bots are often refused; not "broken"


def load(name):
    return json.loads((ROOT / "assets" / "data" / name).read_text())


def collect_links():
    """{url: [where it's used]}"""
    found = {}

    def add(url, where):
        # form endpoints (POST only) can't be checked with a plain request
        if isinstance(url, str) and url.startswith("http") and "formspree.io/f/" not in url:
            found.setdefault(url, []).append(where)

    for l in load("links.json"):
        add(l.get("url"), f'links.json "{l.get("label", l.get("id"))}"')
    add((load("site.json").get("banner") or {}).get("link"), "site.json banner")
    for s in load("sponsors.json"):
        add(s.get("website"), f'sponsors.json "{s.get("name")}"')
    season = load("season.json")
    for e in (season.get("stream") or {}).get("events", []):
        for field in ("stream", "info", "results"):
            add(e.get(field), f'season.json event "{e.get("name")}" ({field})')
    for l in (season.get("robot") or {}).get("links", []):
        add(l.get("url"), f'season.json robot link "{l.get("label")}"')
    return found


def fetch(url):
    """-> (state, detail) with state in ok / soft / broken"""
    ctx = ssl.create_default_context()
    last = ""
    for attempt in range(2):
        for method in ("HEAD", "GET"):
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                    return "ok", str(r.status)
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}"
                if method == "HEAD" and e.code in (400, 403, 404, 405, 501):
                    continue  # some servers mishandle HEAD; retry with GET
                if e.code in SOFT_STATUS:
                    return "soft", last
                break
            except (urllib.error.URLError, socket.timeout, ConnectionError, ssl.SSLError, TimeoutError) as e:
                last = str(getattr(e, "reason", e))
                # An incomplete certificate chain trips Python but not browsers, so only an
                # expired certificate counts as broken.
                if "CERTIFICATE_VERIFY_FAILED" in last and "expired" not in last:
                    return "soft", "certificate couldn't be verified here"
                break
    if last.startswith("HTTP") and int(last.split()[1]) in SOFT_STATUS:
        return "soft", last
    return "broken", last or "no response"


def check_links():
    links = collect_links()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(links, pool.map(fetch, links)))
    broken = [(u, results[u][1], links[u]) for u in links if results[u][0] == "broken"]
    soft = [(u, results[u][1], links[u]) for u in links if results[u][0] == "soft"]
    return len(links), broken, soft


def events_without_streams():
    out = []
    events = (load("season.json").get("stream") or {}).get("events", [])
    for e in events:
        try:
            start = datetime.datetime.fromisoformat(e["start"]).date()
        except (KeyError, ValueError):
            continue
        if 0 <= (start - TODAY).days <= 7 and not e.get("stream") and not e.get("youtubeChannelId"):
            out.append((e["name"], start))
    return out


def security_txt():
    f = ROOT / ".well-known" / "security.txt"
    if not f.exists():
        return None
    m = re.search(r"^Expires:\s*(\S+)", f.read_text(), re.M)
    if not m:
        return None
    try:
        expires = datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).date()
    except ValueError:
        return None
    days = (expires - TODAY).days
    return (expires, days) if days <= 45 else None


def rollover_checklist():
    if not (TODAY.month == 9 and TODAY.day <= 7):
        return None
    season = f"{TODAY.year}–{str(TODAY.year + 1)[2:]}"
    title = f"Season rollover checklist {season}"
    body = f"""FIRST Tech Challenge kickoff is usually in mid-September. Things to update for **{season}**:

- [ ] `assets/data/season.json`: season, game name, robot section (name, description, photos, specs), clear last season's events
- [ ] `assets/data/site.json`: update the home page banner message
- [ ] `assets/data/team.json`: this season's roster and roles
- [ ] Information page: season dates and a short description of the new game
- [ ] Sponsorship form and contract PDFs in `assets/files/`, plus the contract link in `links.json`
- [ ] Hero photo (`images/site/home.avif`) and gallery photos/captions
- [ ] Meeting times on the Information page
- [ ] Turn the Season page on or off (`"enabled"` in `season.json`)
- [ ] `llms.txt`: current season line
- [ ] Check the Hack Club / HCB donation link and the join form still work
"""
    return title, body


def main():
    total, broken, soft = check_links()
    missing = events_without_streams()
    sec = security_txt()
    checklist = rollover_checklist()

    lines = [f"_Checked {total} outside links on {TODAY.isoformat()}._", ""]
    findings = False
    if broken:
        findings = True
        lines += [f"### Broken links ({len(broken)})", ""]
        for url, detail, where in broken:
            lines.append(f"- {url} — **{detail}** (used in: {'; '.join(where)})")
        lines.append("")
    if missing:
        findings = True
        lines += ["### Events starting within a week with no stream link", ""]
        lines += [f"- **{name}** ({start:%a %b} {start.day}) — add `stream` (or `youtubeChannelId`) in `season.json`"
                  for name, start in missing]
        lines.append("")
    if sec:
        findings = True
        expires, days = sec
        state = "expired" if days < 0 else f"expires in {days} days"
        lines += ["### security.txt", "", f"- `.well-known/security.txt` {state} ({expires}). Update the `Expires:` date.", ""]
    if soft:
        lines += ["<details><summary>Couldn't verify (these sites often refuse automated checks)</summary>", ""]
        lines += [f"- {url} — {detail} (used in: {'; '.join(where)})" for url, detail, where in soft]
        lines += ["", "</details>", ""]
    if not findings:
        lines.append("Everything looks good.")

    (ROOT / "health-report.md").write_text("\n".join(lines) + "\n")
    (ROOT / "health-findings").write_text("1" if findings else "0")
    if checklist:
        title, body = checklist
        (ROOT / "rollover-checklist.md").write_text(f"{title}\n{body}")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
