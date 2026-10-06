# Truckee Snowbotics

Website for FTC Team #32587. Live at [snowbotics.org](https://snowbotics.org).

Plain HTML/CSS/JS, hosted on GitHub Pages.

## Editing content

- `team.json` — team roster (About page cards and humans.txt are generated from it; see Team below)
- `alumni.json` — past members, grouped by year on the About page (see Alumni below)
- `news.json` — Home page news (see News below)
- `gallery-captions.json` — optional gallery captions (see Gallery below); `gallery.json` is generated
- `season.json` — Season page: on/off switch, live stream schedule, robot (see Season below)
- `sponsors.json` — Sponsor logos
- `links.json` — every link on the site (socials, forms, link cards)

### News

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

#### Date text

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

### Season page

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

### Team

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
`photo` the card shows the person's initials. Put portraits in `images/team/` (square-ish,
shrunk to 800px automatically). Get permission before posting anyone's photo or details
(see the Terms page).

### Alumni

`assets/data/alumni.json` fills the Alumni section of the About page (`build_alumni.py`):

```json
{ "name": "Eden Sacks", "year": 2026, "role": "", "bio": "", "photo": "" }
```

`name` and `year` are required; `role`, `bio` and `photo` can be blank and only show when filled in.
People are grouped under a centered year heading, newest year first. The newest 4 years show;
older years go inside an "Earlier alumni" dropdown. The section disappears if the file is empty.

### Gallery

Drop images into `images/gallery/`, optionally add a caption to
`assets/data/gallery-captions.json` (`"file.webp": "Caption"`), then run:

```sh
python3 scripts/build_gallery.py
```

This regenerates `gallery.json`, a plain list of image paths (don't edit it by hand).
Captions are read from `gallery-captions.json` by the page itself; images without
one use their filename.

### Folders

- `images/site/` — logo, favicons, social image, home photo
- `images/gallery/` — gallery photos (drop new ones here)
- `images/sponsors/` — sponsor logos
- `partials/` — shared header/footer/head chunks
- `scripts/` — build and check scripts

### Automation (GitHub Actions)

| Workflow | When | What |
|---|---|---|
| `deploy.yml` | every push to `main`, **and daily at 6 AM Pacific** | Builds, checks and deploys. The daily run refreshes date-based content (news order and RSS, upcoming-event data, sitemap dates) without a push. |
| `check.yml` | pull requests, non-main pushes | Same build and checks, no deploy. |
| `gallery-photo.yml` | a "Submit a gallery photo" issue is opened | Adds the photo and caption on a branch and opens a pull request for review. |
| `lighthouse.yml` | pull requests, or "Run workflow" | Scores the built pages with Lighthouse (accessibility, SEO, best practices, performance) and links a report. Targets are in `lighthouserc.json`; misses are warnings, change `warn` to `error` there to make them block. |
| `health.yml` | Mondays 8 AM Pacific, or "Run workflow" | Runs `scripts/health_check.py`: broken outside links, events within a week that have no stream link, `security.txt` expiring soon. Opens or updates **one** issue labeled `site-health`, and closes it when everything passes. In the first week of September it also opens a "Season rollover checklist" issue. |

Notes: scheduled workflows only run on the default branch (`main`) and GitHub pauses them
after 60 days without any repo activity (a push or a manual run wakes them up). The health
workflow needs Issues enabled on the repo. Sites that refuse automated requests (403/429)
are listed as "couldn't verify" and never open an issue by themselves.

The **team roster** lives only in `team.json`: `build_team.py` writes the About page cards
and the TEAM section of `humans.txt` from it. Optional fields: `photo` and `empty`.

### Build and checks

`python3 scripts/build.py` runs every step below. The deploy workflow runs it with
`--release` on each push to `main`; `check.yml` runs it (without deploying) on pull
requests and non-main pushes. Any ERROR stops the deploy.

| Script | What it does |
|---|---|
| `build_team.py` | Writes the About page team cards and the `humans.txt` team list from `team.json`. |
| `build_season.py` | Renders the Season page from `season.json` (and the on/off switch). |
| `build_pages.py` | Copies `partials/` (head-common, header, footer, scripts) into every page between `<!-- @partial name -->` markers. Edit the partial, run the build, commit the updated pages. Don't edit inside the markers. |
| `optimize_images.py` | Gallery: JPG/PNG → WebP capped at 1600px, plus small thumbnails (`images/gallery/thumbs/`, generated, gitignored) used by the grid. Sponsors capped at 800px and `images/site/` at 1600px, same format. Needs Pillow (skipped if missing). |
| `build_gallery.py` | Writes `gallery.json` from the folder + captions. |
| `build_sitemap.py` | Writes `sitemap.xml` from the page folders; `lastmod` comes from git history. New pages are picked up automatically (page order is `ORDER` in the script). `sitemap.xsl` makes the file display as a styled page in browsers; search engines read the plain XML. |
| `apply_links.py` | `--release` only: writes `links.json` URLs into the HTML (see Links). Edits HTML in place, so don't commit its output. |
| `minify_assets.py` | `--release` only: minifies `main.css`/`main.js` (whitespace and comments only). Edits files in place, so don't commit its output. |
| `stamp_assets.py` | `--release` only: adds `?v=<commit>` to CSS/JS URLs so browsers refetch after a deploy. Edits HTML in place, so don't commit its output. |
| `check_site.py` | Fails on invalid JSON, data files that don't match their schema (`SCHEMAS` in the script: required fields, types, sponsor tiers, duplicate ids), missing files in data/HTML references (case-sensitive), `<img>` without alt, duplicate ids, missing title/lang, links that bypass `links.json`. Warns on heading problems and more. |

Teammates can also use **Issues > New issue > Submit a gallery photo**: `gallery-photo.yml` turns the submission into a pull request (`scripts/add_gallery_photo.py` checks it's a real JPG/PNG under 10 MB, converts it to WebP and adds the caption). Merge the PR to publish it, or close it to reject. One-time setting: Settings > Actions > General > tick "Allow GitHub Actions to create and approve pull requests".

On GitHub you can upload a photo to `images/gallery/` and push; CI handles the rest.
The committed `gallery.json`/`sitemap.xml` are only used for local preview.
Build dependencies: `pip install -r requirements.txt` (Dependabot keeps them and the
GitHub Actions versions current). To preview locally: `python3 scripts/build.py`, then `python3 -m http.server`.

### Links

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

### Hiding sections / notice strips

`SECTION_VISIBILITY` at the top of `assets/js/main.js` hides parts of the site
and/or shows a yellow notice strip (like the season page's "under construction"
banner). Each rule:

```js
{
  page: '/season/',          // optional — only apply on this page; omit for all pages
  selector: '#main-content', // CSS selector for the target(s)
  hide: false,               // false = keep visible (notice only); default true = hide
  message: 'This page is under construction…', // optional notice strip
}
```

### Other settings

Site-wide switches live at the top of `assets/js/main.js`: `CONTACT_EMAIL`,
`CONTACT_NOTICE` (red banner + disables the contact form), and
`SPONSORSHIP_FORM_NOTICE` (hover warning on sponsorship form buttons).

