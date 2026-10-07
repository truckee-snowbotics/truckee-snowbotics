# Editing content

Every page is generated from the data files in `assets/data/`. Edit a file, push to `main`, and the deploy rebuilds the site. To test locally, run `./build` and refresh your preview.

## Home banner

The strip under the home page hero comes from `banner` in `assets/data/site.json` (`build_banner.py`):

```json
"banner": {
  "enabled": true,
  "message": "2026–27 season: BIOBUZZ presented by RTX. See our robot, the live stream and the regional event calendar.",
  "linkLabel": "Season page",
  "link": "/season/"
}
```

`message` is the text. `link` is a page on the site (`/season/`), a full URL, or an id from `links.json`; leave it out for a banner with no button, and `linkLabel` sets the button's words. Set `"enabled": false` to hide the banner.

## Season page

`assets/data/season.json` drives the whole page; the build renders it into `season/index.html`.

**Turn the page off:** set `"enabled": false`. The page then shows only "This page isn't
available right now", is marked noindex, and the Season links disappear from the header,
footer and sitemap. (Set it back to `true` to bring everything back.) `stream.enabled` and
`robot.enabled` switch off just one of the two sections.

`season`, `gameTitle`, `gameSummary`, `kickoff`, `qualifiersStart` and `championship` also feed the
Information page's season sentences ("The 2026–27 season kicked off on…"), so a new season
is mostly a `season.json` edit. The footer year updates itself.

**Live stream.** Add each event we compete in to `stream.events`. Times are Pacific:

```json
{
  "name": "Northern Nevada Qualifier",
  "start": "2026-12-06T09:00",
  "end": "2026-12-06T18:00",
  "location": "Reno, NV",
  "stream": "https://www.youtube.com/watch?v=VIDEO_ID",
  "info": "https://ftc-events.firstinspires.org/…",
  "results": "https://ftcscores.com/…"
}
```

- `stream` can be a YouTube video/live link (`youtube.com/watch?v=…`, `youtu.be/…`,
  `youtube.com/live/…`) or a Twitch channel (`twitch.tv/NAME`). For a YouTube channel that
  goes live repeatedly, use `"youtubeChannelId": "UC…"` instead.
- From 30 minutes before the start until 1 hour after the end, the page embeds the stream
  and starts it automatically. Browsers only allow autoplay when the video is **muted**
  (visitors click to unmute); that can't be changed. Set `"autoplay": false` to stop autoplay.
- Outside an event window it shows the next event with a countdown, or "No events scheduled".
- Embeds use YouTube's no-cookie player. The privacy page says the stream autoplays and
  that YouTube/Twitch may set cookies; update it if you change providers.
- Events that ended more than 90 days ago drop off the schedule.

**Regional calendar.** Below the stream, the page shows upcoming Northern Nevada FTC events from FIRST Nevada's public calendar: a month view (with Previous, Next and Today buttons; hover, focus or click an event for its date, time and venue) on wide screens, and a plain event list on phones and for visitors without JavaScript. League meets, tournaments, scrimmages and kickoffs are tinted blue; workshops and deadlines are grey. The build (`build_calendar.py`) fetches the feed into `assets/data/calendar.json`, and the daily deploy keeps it fresh; if the feed is down the last good copy is used. Configure it under `calendar` in `season.json`:

```json
"calendar": {
  "enabled": true,
  "title": "Northern Nevada FTC calendar",
  "feed": "https://calendar.google.com/calendar/ical/ftc%40firstnevada.org/public/basic.ics",
  "exclude": ["SoNV"],
  "limit": 12
}
```

`exclude` hides events whose title contains any of those words (add `"Coaches Corner"` to drop workshops, for example); `limit` is how many events the list shows before a "More events (N)" dropdown (default 10; the month view shows all of them). This list is separate from `stream.events`, which are the events *we* compete in and drive the live embed.

**Robot.** `robot` takes optional `name`, `description`, `photos` (`src` + `caption`),
`specs` (`label` + `value`) and `links`. Only what you fill in is shown.

## Team

`assets/data/team.json` drives the About page's "Meet the team" cards (students first, then
mentors) and the TEAM block in `humans.txt`. Only `name` and `role` are required; everything
else is shown only when you fill it in:

```json
{
  "name": "Bach Le", "role": "President - Engineering Lead",
  "group": "students",
  "photo": "/images/team/bach-le.webp",
  "grade": "11th grade",
  "bio": "One or two sentences."
}
```

`group` is `students` (default) or `mentors`; `role` can be blank. Without a
`photo` the card shows the person's initials (worked out from the name). Put portraits in
`images/team/` (square-ish, shrunk to 800px automatically). Get permission before posting anyone's photo or details
(see the Terms page).

## Alumni

`assets/data/alumni.json` fills the Alumni section of the About page (`build_alumni.py`):

```json
{ "name": "Eden Sacks", "year": 2026, "role": "", "bio": "", "photo": "" }
```

`name` and `year` are required; `role`, `bio` and `photo` can be blank and only show when filled in.
People are grouped by year (year on the left, names on the right), newest year first, as a compact list inside a "Show alumni" dropdown (open by default); a `photo` shows as a small thumbnail. The newest 4 years show;
older years go inside an "Earlier alumni" dropdown. The section disappears if the file is empty.

## Gallery

Drop images into `images/gallery/`, optionally add a caption to
`assets/data/gallery-captions.json` (`"file.webp": "Caption"`), then run:

```sh
python3 scripts/build_gallery.py
```

This regenerates `gallery.json`, a plain list of image paths (don't edit it by hand).
Captions are read from `gallery-captions.json` by the page itself; images without
one use their filename.

## Links

`assets/data/links.json` is the single source of truth for URLs. Each entry:

```json
{
  "id": "join",
  "label": "Join the Team",
  "url": "https://forms.gle/...",
  "listed": true
}
```

- `id` — matched against `data-link-key` (and `data-form-action`) attributes in the
  HTML, so any button/anchor with that key picks up the URL automatically.
- `listed: true` — the link also appears as a card on the Information page and in
  the footer link list. `listed: false` entries only wire up `data-link-key` elements.
- `url: "#"` — placeholder for a link that has no destination yet; elements bound to
  it are hidden and it is excluded from the Information page until a real URL is set.
- Emails are entries too, as `mailto:` URLs: `email` (public address, also used for
  visible text and the JSON-LD).

This is the only place URLs live. In the HTML, write links as
`<a href="#" data-link-key="instagram">`; the deploy build (`apply_links.py`) fills in
the real `href` (and `target`/`rel` for external links), and `main.js` does the same
at runtime. The repo's HTML therefore shows `href="#"`, not the live URL. The site
check fails the deploy if a link hard-codes a URL that's in `links.json`, or uses a
`data-link-key` that doesn't exist.

## Home and About photos

`assets/data/site.json` sets the two big photos that aren't part of the gallery:

```json
{
  "heroPhoto":  { "src": "/images/site/home.avif",            "alt": "Truckee Snowbotics team at a competition" },
  "aboutPhoto": { "src": "/images/gallery/2025-team-photo.webp", "alt": "The Snowbotics team" }
}
```

`src` is any image in the project (put new ones in `images/site/`); `alt` is a short description for screen readers and is required. Both are shown in landscape 4:3 boxes and cropped to fit, so use landscape photos with the subject near the middle. Phone-sized photos are shrunk to 1600px by the build (`./build`). Run `./build` after changing the file; a missing file fails the site check.

## Other settings

Site-wide switches live in the data files: the Season page with `enabled` in `season.json`, and the home banner with `banner.enabled` in `site.json`.

The email addresses and every other URL come from `links.json`; fonts (Plus Jakarta Sans) are hosted in `assets/fonts/`, so visitors never contact Google Fonts.
