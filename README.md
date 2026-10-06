# Truckee Snowbotics

Website for FTC Team #32587. Live at [snowbotics.org](https://snowbotics.org).

Plain HTML/CSS/JS, hosted on GitHub Pages.

## Editing content

- `team.json` — About page team cards
- `news.json` — Home page news cards
- `gallery-captions.json` — optional gallery captions (see Gallery below); `gallery.json` is generated
- `sponsors.json` — Sponsor logos
- `links.json` — every link on the site (socials, forms, link cards)

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

### Build and checks

`python3 scripts/build.py` runs every step below. The deploy workflow runs it with
`--release` on each push to `main`; `check.yml` runs it (without deploying) on pull
requests and non-main pushes. Any ERROR stops the deploy.

| Script | What it does |
|---|---|
| `build_pages.py` | Copies `partials/` (head-common, header, footer, scripts) into every page between `<!-- @partial name -->` markers. Edit the partial, run the build, commit the updated pages. Don't edit inside the markers. |
| `optimize_images.py` | Gallery: JPG/PNG → WebP capped at 1600px, plus small thumbnails (`images/gallery/thumbs/`, generated, gitignored) used by the grid. Sponsors capped at 800px and `images/site/` at 1600px, same format. Needs Pillow (skipped if missing). |
| `build_gallery.py` | Writes `gallery.json` from the folder + captions. |
| `build_sitemap.py` | Writes `sitemap.xml` from the page folders; `lastmod` comes from git history. New pages are picked up automatically (set priority in `META` there). |
| `apply_links.py` | `--release` only: writes `links.json` URLs into the HTML (see Links). Edits HTML in place, so don't commit its output. |
| `minify_assets.py` | `--release` only: minifies `main.css`/`main.js` (whitespace and comments only). Edits files in place, so don't commit its output. |
| `stamp_assets.py` | `--release` only: adds `?v=<commit>` to CSS/JS URLs so browsers refetch after a deploy. Edits HTML in place, so don't commit its output. |
| `check_site.py` | Fails on invalid JSON, data files that don't match their schema (`SCHEMAS` in the script: required fields, types, sponsor tiers, duplicate ids), missing files in data/HTML references (case-sensitive), `<img>` without alt, duplicate ids, missing title/lang, links that bypass `links.json`. Warns on heading problems and more. |

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

