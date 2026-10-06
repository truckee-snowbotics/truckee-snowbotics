# Editing content

Every page is generated from the data files in `assets/data/`. Edit a file, push to `main`, and the deploy rebuilds the site. To preview locally, run `python3 scripts/build.py` and then `python3 -m http.server`.

## News

`assets/data/news.json` is a list of items; the build renders them into the home page
(real HTML, so search engines see them), writes `news.xml` (RSS) and, for upcoming
events, Event structured data. Featured items first, then upcoming items soonest-first, then past items newest-first (by `date`); no ordering field to maintain.

```json
{
  "date": "2026-06-07",
  "title": "Truckee Maker Show",
  "text": "Join us at the Truckee Maker Show…",
  "event": true, "location": "Truckee Community Center",
  "startTime": "11:00", "endTime": "17:00"
}
```

| Field | |
|---|---|
| `date`, `title`, `text` | required (`date` is `YYYY-MM-DD`) |
| `endDate` | optional, for a span of days |
| `displayDate` | optional text shown instead of the formatted date ("Post-Season 2026") |
| `link`, `linkLabel` | optional "Read more →" link (URLs already in `links.json` are kept single-source) |
| `image`, `imageAlt` | optional picture shown under the text |
| `featured` | `true` pins the item to the top, highlighted |
| `expires` | hidden after this date, including in visitors' browsers between deploys |
| `event`, `location`, `address`, `startTime`, `endTime` | `event: true` publishes Event data while upcoming (times are Pacific) |

The site check warns about past events without an `expires` date, and if every item has expired.

### Date text

The text shown next to each item is built automatically from `date` and `endDate`:

| `date` / `endDate` | Shown as |
|---|---|
| `2026-06-07` | Sunday, June 7, 2026 |
| `2026-10-20` / `2026-10-22` | October 20–22, 2026 |
| `2026-03-01` / `2026-06-30` | March 1 – June 30, 2026 |
| `2026-12-28` / `2027-01-03` | December 28, 2026 – January 3, 2027 |

`displayDate` is an optional override for timing that isn't a real date ("Fall 2026").
`date` still decides the sort order, so it needs a sensible value even when you
override the text. **Leave `displayDate` out whenever the real date is known**, so the
exact date shows and you have one less thing to keep in sync.

Two current items still use `displayDate` because their dates are placeholders I made up
to get the sort order right: "Recruiting New Members" (`2026-06-01`, shown as "Post-Season
2026") and "Post-Season Begins" (`2026-03-01` to `2026-06-30`, shown as "March-June 2026").
When their real dates are known, set `date` / `endDate` and delete `displayDate`.

## Season page

`assets/data/season.json` drives the whole page; the build renders it into `season/index.html`.

**Turn the page off:** set `"enabled": false`. The page then shows only "This page isn't
available right now", is marked noindex, and the Season links disappear from the header,
footer and sitemap. (Set it back to `true` to bring everything back.) `stream.enabled` and
`robot.enabled` switch off just one of the two sections.

`season`, `gameTitle`, `gameSummary`, `kickoff`, `qualifiersStart` and `championship` also feed the
Information page's season sentences ("The 2026–27 season kicked off on…") and the home
page stat, so a new season is a `season.json` edit. The footer year updates itself.

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
People are grouped under a centered year heading, newest year first. The newest 4 years show;
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
  "category": "Forms",
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
  visible text and the JSON-LD) and `noticeEmail` (shown by the contact notice banner).

This is the only place URLs live. In the HTML, write links as
`<a href="#" data-link-key="instagram">`; the deploy build (`apply_links.py`) fills in
the real `href` (and `target`/`rel` for external links), and `main.js` does the same
at runtime. The repo's HTML therefore shows `href="#"`, not the live URL. The site
check fails the deploy if a link hard-codes a URL that's in `links.json`, or uses a
`data-link-key` that doesn't exist.

## Other settings

Site-wide switches live at the top of `assets/js/main.js`: `CONTACT_NOTICE` (red banner + disables the contact form) and `SPONSORSHIP_FORM_NOTICE` (hover warning on sponsorship form buttons). The Season page is switched with `enabled` in `season.json`.

The email addresses and every other URL come from `links.json`; fonts (Inter) are hosted in `assets/fonts/`, so visitors never contact Google Fonts.
