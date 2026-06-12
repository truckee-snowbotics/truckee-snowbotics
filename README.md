# Truckee Snowbotics

Website for FTC Team #32587. Live at [snowbotics.org](https://snowbotics.org).

Plain HTML/CSS/JS, hosted on GitHub Pages.

## Editing content

- `team.json` — About page team cards
- `news.json` — Home page news cards
- `gallery.json` — Gallery images
- `sponsors.json` — Sponsor logos
- `links.json` — every link on the site (socials, forms, link cards)

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

