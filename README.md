# Truckee Snowbotics

Website for FTC Team #32587. Live at [snowbotics.org](https://snowbotics.org).

Plain HTML/CSS/JS, hosted on GitHub Pages. Python scripts in `scripts/` build the generated parts of the pages; GitHub Actions build, check and deploy on every push.

## Where to edit

| To change | Edit | Guide |
|---|---|---|
| Banner under the home hero | `assets/data/site.json` | [Banner](docs/content.md#home-banner) |
| Season page: live stream schedule, robot, on/off switch | `assets/data/season.json` | [Season page](docs/content.md#season-page) |
| Team roster (About page) | `assets/data/team.json` | [Team](docs/content.md#team) |
| Alumni (About page) | `assets/data/alumni.json` | [Alumni](docs/content.md#alumni) |
| Gallery photos and captions | `images/gallery/`, `assets/data/gallery-captions.json` | [Gallery](docs/content.md#gallery) |
| Home hero photo and About photo | `assets/data/site.json` | [Home and About photos](docs/content.md#home-and-about-photos) |
| Sponsors | `assets/data/sponsors.json` | |
| Any link or email (socials, forms, downloads) | `assets/data/links.json` | [Links](docs/content.md#links) |
| Header, footer, shared `<head>` | `partials/` | [Build and checks](docs/automation.md#build-and-checks) |

Generated files (`gallery.json`, `sitemap.xml`, the lists inside pages) are rewritten by the build; don't edit inside the `<!-- @... -->` markers.

## Rebuild for testing

```sh
./build
```

Rebuilds every generated part of the site and runs the checks; then refresh your preview (VS Code Live Preview, or any static server on the project folder). Run it after editing a data file. The first run sets up its own Python environment in `.venv`. On Windows, run it from Git Bash (the VS Code terminal can use it), with Python 3 installed.

## Folders

- `assets/` — `css/`, `js/`, `data/` (all site content), `fonts/` (Plus Jakarta Sans, self-hosted), `files/` (PDFs)
- `images/` — `site/` (logo, favicons, social card, home photo), `gallery/`, `sponsors/`, `team/` (portraits)
- `partials/` — shared header, footer and `<head>` chunks
- `scripts/` — build and check scripts ([what each does](docs/automation.md#build-and-checks))
- `docs/` — [editing content](docs/content.md) and [automation and builds](docs/automation.md)
- `.github/` — workflows, issue forms, Dependabot

## Rules the site follows

- Every URL lives once, in `links.json`. In HTML write `<a href="#" data-link-key="id">`.
- Every person or photo on the site has permission to be there; see the [Terms & Photo Policy](https://snowbotics.org/terms/).
- A failed site check stops the deploy.
