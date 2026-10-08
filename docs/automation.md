# Automation and builds

## Automation (GitHub Actions)

| Workflow | When | What |
|---|---|---|
| `deploy.yml` | every push to `main`, **and daily around 6:15 AM Pacific** | Builds, checks and deploys. The daily run refreshes date-based content (the live-stream schedule, sitemap dates) without a push. |
| `check.yml` | pull requests, non-main pushes, or "Run workflow" | The same release build and checks as the deploy, without deploying. On pull requests it also scores the built pages with Lighthouse (targets in `lighthouserc.json`; misses are warnings, change `warn` to `error` there to make them block) and links a public report. |
| `gallery-photo.yml` | a "Submit a gallery photo" issue is opened | Adds the photo and caption on a branch and opens a pull request for review. |
| `health.yml` | Mondays around 8:30 AM Pacific, or "Run workflow" | Runs `scripts/health_check.py`: broken outside links, events within a week that have no stream link, `security.txt` expiring soon. Opens or updates **one** issue labeled `site-health`, and closes it when everything passes. In the first week of September it also opens a "Season rollover checklist" issue. |

Notes: scheduled workflows only run on the default branch (`main`) and GitHub pauses them
after 60 days without any repo activity (a push or a manual run wakes them up). The health
workflow needs Issues enabled on the repo. Sites that refuse automated requests (403/429)
are listed as "couldn't verify" and never open an issue by themselves.


## Build and checks

`python3 scripts/build.py` runs every step below. The deploy workflow runs it with
`--release` on each push to `main`; `check.yml` runs it (without deploying) on pull
requests and non-main pushes. Any ERROR stops the deploy.

| Script | What it does |
|---|---|
| `build_meta.py` | Writes each page's canonical URL, Open Graph/Twitter tags and breadcrumb data between `<!-- @meta -->` and `<!-- @breadcrumb -->` markers, from the page's own `<title>` and description (the only place a page's name and summary are written). For a new page, write its title and description and copy the marker pairs from another page. |
| `build_team.py` | Writes the About page team cards and the `humans.txt` team list from `team.json`. |
| `build_alumni.py` | Renders the Alumni section of the About page from `alumni.json`. |
| `build_season.py` | Renders the Season page from `season.json` (and the on/off switch). |
| `build_pages.py` | Copies `partials/` (head-common, header, footer, scripts) into every page between `<!-- @partial name -->` markers. Edit the partial, run the build, commit the updated pages. Don't edit inside the markers. |
| `optimize_images.py` | Gallery: JPG/PNG → WebP capped at 1600px, plus small thumbnails (`images/gallery/thumbs/`, generated, gitignored) used by the grid. Sponsors capped at 800px and `images/site/` at 1600px, same format. Needs Pillow (skipped if missing). |
| `build_gallery.py` | Writes `gallery.json` from the folder + captions. |
| `build_sitemap.py` | Writes `sitemap.xml` from the page folders; `lastmod` comes from git history. New pages are picked up automatically (page order is `ORDER` in the script). `sitemap.xsl` makes the file display as a styled page in browsers; search engines read the plain XML. |
| `apply_links.py` | `--release` only: writes `links.json` URLs into the HTML (see Links). Edits HTML in place, so don't commit its output. |
| `minify_assets.py` | `--release` only: minifies `main.css`/`main.js` (whitespace and comments only). Edits files in place, so don't commit its output. |
| `stamp_assets.py` | `--release` only: adds `?v=<commit>` to CSS/JS URLs so browsers refetch after a deploy. Edits HTML in place, so don't commit its output. |
| `check_site.py` | Fails on invalid JSON, data files that don't match their schema (`SCHEMAS` in the script: required fields, types, sponsor tiers, duplicate ids), missing files in data/HTML references (case-sensitive), `<img>` without alt, duplicate ids, missing title/lang, links that bypass `links.json`. Warns on heading problems, files nothing references, pages missing from `llms.txt`, and more. |

`scripts/_lib.py` holds the small helpers the build scripts share (escaping, marker replacement, person cards).

## Photo submissions

Teammates can use **Issues > New issue > Submit a gallery photo**: `gallery-photo.yml` turns the submission into a pull request (`scripts/add_gallery_photo.py` checks it's a real JPG/PNG under 10 MB, converts it to WebP and adds the caption). Merge the PR to publish it, or close it to reject. One-time setting: Settings > Actions > General > tick "Allow GitHub Actions to create and approve pull requests".

On GitHub you can upload a photo to `images/gallery/` and push; CI handles the rest.
The committed `gallery.json`/`sitemap.xml` are only used for local preview.
Build dependencies: `pip install -r requirements.txt` (Dependabot keeps them and the
GitHub Actions versions current). To rebuild locally: `./build` (on Windows, run it from Git Bash).
