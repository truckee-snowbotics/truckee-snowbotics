/* main.js — Truckee Snowbotics */
'use strict';

// ╔══════════════════════════════════════════════════╗
// ║  CONTACT NOTICE BANNER                           ║
// ╠══════════════════════════════════════════════════╣
// ║  Set enabled: true to show the banner,           ║
// ║  false to hide it site-wide instantly.           ║
// ║  The address shown is the "noticeEmail" entry in ║
// ║  /assets/data/links.json.                        ║
// ╚══════════════════════════════════════════════════╝
const CONTACT_NOTICE = {
  enabled: false,
};

// ╔══════════════════════════════════════════════════╗
// ║  SPONSORSHIP FORM NOTICE                         ║
// ╠══════════════════════════════════════════════════╣
// ║  Set enabled: true to show a hover popup on all  ║
// ║  sponsorship form buttons. Edit message freely;  ║
// ║  {email} becomes the "email" entry in links.json. ║
// ╚══════════════════════════════════════════════════╝
const SPONSORSHIP_FORM_NOTICE = {
  enabled: false,
  message: 'The sponsorship form has an incorrect email. Please use {email} instead.',
};

// ╔══════════════════════════════════════════════════╗
// ║  LINKS — single source of truth:                 ║
// ║  /assets/data/links.json                         ║
// ╠══════════════════════════════════════════════════╣
// ║  Each entry: { id, label, url, category, listed }║
// ║  - id matches data-link-key / data-form-action   ║
// ║    attributes in the HTML                        ║
// ║  - listed: true → also rendered on the           ║
// ║    Information page links grid and in the footer ║
// ║  - url "#" → no destination yet; the element is  ║
// ║    hidden until a real URL is set                ║
// ║  - emails are entries too: "email" (public) and  ║
// ║    "noticeEmail", as mailto: URLs                ║
// ║  - at deploy, scripts/apply_links.py writes these║
// ║    URLs into the HTML, so the HTML needs only    ║
// ║    data-link-key (href stays "#")                ║
// ╚══════════════════════════════════════════════════╝
let linksPromise = null;
const linkUrls = {};
// Address from a mailto: entry in links.json (empty until links have loaded).
const emailOf = id => (linkUrls[id] || '').replace(/^mailto:/i, '');
function getLinks() {
  if (!linksPromise) {
    linksPromise = fetch('/assets/data/links.json')
      .then(r => { if (!r.ok) throw new Error('Links JSON not found'); return r.json(); })
      .then(items => Array.isArray(items) ? items : []);
  }
  return linksPromise;
}

// ── Wire data-link-key / data-form-action elements ──
getLinks().then(items => {
  const urlById = linkUrls;
  items.forEach(item => {
    if (item.id) urlById[item.id] = (item.url || '').trim();
  });

  document.querySelectorAll('[data-link-key]').forEach(el => {
    const url = urlById[el.dataset.linkKey];
    if (url === undefined) return;
    // '#' or empty marks a link with no destination yet — hide it instead
    // of rendering a dead button that opens a blank tab.
    if (!url || url === '#') { el.style.display = 'none'; return; }
    el.href = url;
    if (/^mailto:/i.test(url) && el.textContent.includes('@')) el.textContent = emailOf(el.dataset.linkKey);
    // This runs after the eval-time external-links pass below, so external
    // URLs assigned here must get target/rel themselves.
    if (/^https?:/i.test(url)) {
      el.setAttribute('target', '_blank');
      el.setAttribute('rel', 'noopener noreferrer');
    }
  });

  document.querySelectorAll('[data-form-action]').forEach(el => {
    const url = urlById[el.dataset.formAction];
    if (url && url !== '#') el.action = url;
  });
}).catch(() => { /* keep the fallback hrefs hard-coded in the HTML */ });

// ── Contact notice banner ─────────────────────────
getLinks().then(() => {
  const banner = document.getElementById('notice-banner');
  if (!banner || !CONTACT_NOTICE.enabled) return;
  const noticeEmail = emailOf('noticeEmail');

  // Populate email link from links.json
  const link = banner.querySelector('a[data-notice-email]');
  if (link) {
    link.href = 'mailto:' + noticeEmail;
    link.textContent = noticeEmail;
  }

  // Wire up close button
  const btn = banner.querySelector('[data-notice-close]');
  if (btn) btn.addEventListener('click', () => { banner.style.display = 'none'; });

  // Show only after setup is complete — prevents flash
  banner.style.display = 'block';

  // Disable contact form send button when notice is active
  const sendBtn = document.querySelector('.contact-send-btn');
  if (sendBtn) {
    sendBtn.disabled = true;

    // Insert explanation below the button
    const notice = document.createElement('p');
    notice.className = 'form-notice';
    notice.innerHTML = '&#9888; Contact form submissions are currently unavailable. Please reach us directly at <a href="mailto:' + noticeEmail + '">' + noticeEmail + '</a>.';
    sendBtn.insertAdjacentElement('afterend', notice);

    const form = sendBtn.closest('form');
    if (form) {
      form.addEventListener('submit', (e) => { e.preventDefault(); });
    }
  }
}).catch(() => {});

// ── Sponsorship form hover notice ────────────
getLinks().then(() => {
  if (!SPONSORSHIP_FORM_NOTICE.enabled) return;

  const tooltip = document.createElement('div');
  tooltip.style.cssText = [
    'position:fixed',
    'z-index:9999',
    'max-width:280px',
    'padding:.6rem .9rem',
    'background:#3b1010',
    'color:#fca5a5',
    'border:1px solid #7f1d1d',
    'border-radius:0',
    'font-size:.825rem',
    'line-height:1.5',
    'pointer-events:none',
    'display:none',
    'box-shadow:0 4px 16px rgba(0,0,0,.45)',
  ].join(';');
  tooltip.textContent = SPONSORSHIP_FORM_NOTICE.message.replace('{email}', emailOf('email'));
  document.body.appendChild(tooltip);

  function show(btn) {
    const r = btn.getBoundingClientRect();
    tooltip.style.visibility = 'hidden';
    tooltip.style.display = 'block';
    const gap = 8;
    let top = r.bottom + gap;
    if (top + tooltip.offsetHeight > window.innerHeight) top = r.top - tooltip.offsetHeight - gap;
    let left = r.left;
    if (left + tooltip.offsetWidth > window.innerWidth) left = window.innerWidth - tooltip.offsetWidth - 8;
    tooltip.style.top  = top  + 'px';
    tooltip.style.left = left + 'px';
    tooltip.style.visibility = '';
  }

  function hide() { tooltip.style.display = 'none'; }

  document.querySelectorAll('[data-link-key="sponsorshipForm"]').forEach(btn => {
    btn.addEventListener('mouseenter', () => show(btn));
    btn.addEventListener('mouseleave', hide);
    btn.addEventListener('focus',      () => show(btn));
    btn.addEventListener('blur',       hide);
  });
}).catch(() => {});

// ── Active nav link (page-based) ─────────────
(function () {
  const links = document.querySelectorAll('.nav a');
  if (!links.length) return;

  // Normalise pathname to always end with /
  const currentPath = window.location.pathname.replace(/\/?$/, '/');

  links.forEach(l => {
    const href = l.getAttribute('href') || '';
    const linkPath = href.split('#')[0].replace(/\/?$/, '/');
    l.classList.toggle('active', linkPath === currentPath);
  });
})();

// ── Hamburger / mobile nav toggle ────────────
(function () {
  const btn = document.getElementById('hamburger');
  const nav = document.getElementById('mobile-nav');
  if (!btn || !nav) return;

  btn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    btn.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', String(open));
    nav.setAttribute('aria-hidden', String(!open));
  });

  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      nav.setAttribute('aria-hidden', 'true');
    });
  });
})();

// ── Collapsible sections on phones ───────────
// <details data-collapse-mobile open>: open (and not toggleable) on desktop, collapsed on phones.
(function () {
  const groups = document.querySelectorAll('details[data-collapse-mobile]');
  if (!groups.length) return;
  const phone = window.matchMedia('(max-width: 700px)');
  const sync = () => groups.forEach(d => { d.open = !phone.matches; });
  groups.forEach(d => {
    const summary = d.querySelector('summary');
    if (summary) summary.addEventListener('click', e => { if (!phone.matches) e.preventDefault(); });
  });
  if (phone.addEventListener) phone.addEventListener('change', sync); else phone.addListener(sync);
  sync();
})();

// ── Light / dark theme toggle ─────────────────
// The head script sets data-theme before first paint (saved choice, else the device setting).
(function () {
  const root = document.documentElement;
  const meta = document.querySelector('meta[name="theme-color"]');
  const buttons = document.querySelectorAll('.theme-toggle');
  const apply = theme => {
    root.dataset.theme = theme;
    if (meta) meta.setAttribute('content', theme === 'light' ? '#eceef0' : '#131416');
    buttons.forEach(b => {
      b.setAttribute('aria-label', theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme');
      if (b.classList.contains('theme-toggle-text')) b.textContent = theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme';
    });
  };
  apply(root.dataset.theme === 'light' ? 'light' : 'dark');
  buttons.forEach(b => b.addEventListener('click', () => {
    const next = root.dataset.theme === 'light' ? 'dark' : 'light';
    apply(next);
    try { localStorage.setItem('snowbotics-theme', next); } catch (e) { /* private mode: the choice just isn't remembered */ }
  }));
})();

// ── External links ────────────────────────────
document.querySelectorAll('a[href^="http"]').forEach(a => {
  a.setAttribute('target', '_blank');
  a.setAttribute('rel', 'noopener noreferrer');
});

function escapeHTML(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Load gallery from JSON ─────────────────
(function () {
  const track = document.querySelector('.gallery-track');
  if (!track) return;

  // Captions live in gallery-captions.json ({"file.webp": "Caption"}); images
  // without one fall back to their filename.
  const loadJSON = url => fetch(url).then(response => {
    if (!response.ok) throw new Error(url + ' not found');
    return response.json();
  });

  Promise.all([
    loadJSON('/assets/data/gallery.json'),
    loadJSON('/assets/data/gallery-captions.json').catch(() => ({}))
  ])
    .then(([items, captions]) => {
      if (!Array.isArray(items) || !items.length) throw new Error('Invalid gallery data');

      const captionFor = src => {
        const file = src.split('/').pop();
        const stem = file.replace(/\.[^.]+$/, '');
        const custom = captions[file] || Object.keys(captions).filter(k => k.replace(/\.[^.]+$/, '') === stem).map(k => captions[k])[0];
        return (custom && custom.trim()) || stem.replace(/[_\-\s]+/g, ' ').trim();
      };

      // The grid loads small thumbnails (made at deploy time by
      // scripts/optimize_images.py); the modal and the fallback use the full image.
      const thumbFor = src => src.replace('/images/gallery/', '/images/gallery/thumbs/').replace(/\.[^.\/]+$/, '.webp');

      const cards = items.map(src => {
        src = String(src || '').trim();
        const caption = captionFor(src);
        const alt = caption || 'Gallery image';

        return `
          <div class="gallery-item" role="button" tabindex="0" aria-label="${escapeHTML('View photo: ' + caption)}" data-src="${escapeHTML(src)}" data-alt="${escapeHTML(alt)}" data-caption="${escapeHTML(caption)}">
            <div class="gallery-image">
              ${src ? `<img src="${escapeHTML(thumbFor(src))}" alt="${escapeHTML(alt)}" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=this.closest('.gallery-item').dataset.src" />` : `<span>${escapeHTML(caption)}</span>`}
            </div>
          </div>
        `;
      }).join('');

      track.innerHTML = cards;
      attachGalleryModal();
    })
    .catch(() => {
      // keep the existing static markup if loading fails
    });
  function attachGalleryModal() {
    const modal = document.querySelector('.gallery-modal');
    const modalImage = document.querySelector('.gallery-modal-image');
    const modalCaption = document.querySelector('.gallery-modal-caption');
    const closeButton = document.querySelector('.gallery-modal-close');
    const backdrop = document.querySelector('.gallery-modal-backdrop');
    if (!modal || !modalImage || !closeButton || !backdrop) return;

    function openModal(item) {
      const src = item.getAttribute('data-src');
      const alt = item.getAttribute('data-alt');
      const caption = item.getAttribute('data-caption') || '';

      modalImage.innerHTML = src ? `<img src="${escapeHTML(src)}" alt="${escapeHTML(alt)}" />` : '';
      if (modalCaption) modalCaption.textContent = caption;
      modal.classList.remove('hidden');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      modal.classList.add('hidden');
      modal.setAttribute('aria-hidden', 'true');
      modalImage.innerHTML = '';
      if (modalCaption) modalCaption.textContent = '';
      document.body.style.overflow = '';
    }

    if (track) {
      track.addEventListener('click', (event) => {
        const item = event.target.closest('.gallery-item');
        if (!item) return;
        openModal(item);
      });
      track.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        const item = event.target.closest('.gallery-item');
        if (!item) return;
        event.preventDefault();
        openModal(item);
      });
    }

    closeButton.addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeModal();
      }
    });
  }
})();

// ── Sponsors data (shared by grid + bar) ─────
let sponsorsPromise = null;
function getSponsors() {
  if (!sponsorsPromise) {
    sponsorsPromise = fetch('/assets/data/sponsors.json')
      .then(response => {
        if (!response.ok) throw new Error('Sponsors JSON not found');
        return response.json();
      });
  }
  return sponsorsPromise;
}

// ── Load sponsors from JSON ─────────────────
(function () {
  const container = document.querySelector('.sponsor-grid');
  if (!container) return;

  const TIER_ORDER = ['platinum', 'gold', 'silver', 'bronze'];
  const TIER_LABELS = { platinum: 'Platinum', gold: 'Gold', silver: 'Silver', bronze: 'Bronze' };

  getSponsors()
    .then(items => {
      if (!Array.isArray(items)) throw new Error('Invalid sponsors data');

      const byTier = {};
      items.forEach(item => {
        const tier = (item.tier || 'bronze').toLowerCase();
        if (!byTier[tier]) byTier[tier] = [];
        byTier[tier].push(item);
      });

      const html = TIER_ORDER
        .filter(tier => byTier[tier] && byTier[tier].length)
        .map(tier => {
          const cards = byTier[tier].map(item => {
            const hasLink = item.website && item.website.trim();
            const tag = hasLink ? 'a' : 'div';
            const hrefAttr = hasLink ? ` href="${escapeHTML(item.website)}" target="_blank" rel="noopener noreferrer"` : '';
            const banner = item.banner
              ? `<img src="${escapeHTML(item.banner)}" alt="${escapeHTML(item.name || 'Sponsor')} banner" loading="lazy" decoding="async" />`
              : '';
            return `<${tag} class="sponsor-item"${hrefAttr}>${banner}</${tag}>`;
          }).join('');

          return `
            <div class="sponsor-tier">
              <div class="sponsor-tier-header">
                <span class="sponsor-tier-badge sponsor-tier-badge--${escapeHTML(tier)}">${escapeHTML(TIER_LABELS[tier] || tier)}</span>
                <span class="sponsor-tier-line"></span>
              </div>
              <div class="sponsor-tier-grid">${cards}</div>
            </div>`;
        }).join('');

      container.innerHTML = html;
    })
    .catch(() => {});
})();

// ── Sponsor bar ───────────────────────────────────────
(function () {
  const bar = document.getElementById('sponsor-bar-logos');
  if (!bar) return;

  getSponsors()
    .then(items => {
      if (!Array.isArray(items) || !items.length) return;
      bar.innerHTML = items.map(item => {
        const hasLink = item.website && item.website.trim();
        const tag = hasLink ? 'a' : 'div';
        const attrs = hasLink ? ` href="${escapeHTML(item.website)}" target="_blank" rel="noopener noreferrer"` : '';
        const banner = item.banner
          ? `<img src="${escapeHTML(item.banner)}" alt="${escapeHTML(item.name || 'Sponsor')} banner" loading="lazy" decoding="async" />`
          : '';
        return `<${tag} class="sponsor-bar-logo"${attrs}>${banner}</${tag}>`;
      }).join('');
    })
    .catch(() => {});
})();

// ── Render listed links (Information grid + footer) ──
(function () {
  getLinks()
    .then(allItems => {
      // Only entries flagged listed, and skip entries without a real
      // destination yet (url empty or '#')
      const items = allItems.filter(item => {
        const url = item.url && item.url.trim();
        return item.listed && url && url !== '#';
      });
      if (!items.length) return;

      const grid = document.getElementById('links-grid');
      if (grid) {
        grid.innerHTML = items.map(item => `
            <a class="link-card" href="${escapeHTML(item.url)}" target="_blank" rel="noopener noreferrer">
              <span class="link-card-label">${escapeHTML(item.label || '')}</span>
              ${item.category ? `<span class="link-card-category">${escapeHTML(item.category)}</span>` : ''}
            </a>`).join('');
      }

      const footerLinks = document.getElementById('footer-links-list');
      if (footerLinks) {
        footerLinks.innerHTML = items.map(item =>
          `<a href="${escapeHTML(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(item.label || '')}</a>`
        ).join('');
      }

      const footerNav = document.querySelector('.footer-nav');
      if (footerNav && !footerLinks) {
        const sep = document.createElement('span');
        sep.className = 'footer-nav-sep';
        footerNav.appendChild(sep);
        items.forEach(item => {
          const a = document.createElement('a');
          a.href = item.url;
          a.target = '_blank';
          a.rel = 'noopener noreferrer';
          a.textContent = item.label || '';
          footerNav.appendChild(a);
        });
      }
    })
    .catch(() => {});
})();

// ── News ─────────────────────────────────────────────
// The cards are rendered into the page at build time (scripts/build_news.py from
// news.json). Here we only hide items whose "expires" date has passed since the
// last deploy, and show the "no news" message if nothing is left.
(function () {
  const grid = document.getElementById('news-grid');
  if (!grid) return;
  const now = new Date();
  const today = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
  grid.querySelectorAll('.news-card[data-expires]').forEach(card => {
    if (card.dataset.expires < today) card.remove();
  });
  if (!grid.querySelector('.news-card') && !grid.querySelector('.news-empty')) {
    grid.innerHTML = '<p class="news-empty">' + escapeHTML(grid.dataset.empty || 'No news right now.') + '</p>';
  }
})();

// ── Contact form ─────────────────────────────────────
(function () {
  const form = document.querySelector('.contact-form');
  if (!form) return;

  const btn = form.querySelector('.contact-send-btn');
  const errorDiv = form.querySelector('.form-error');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!btn || btn.disabled) return;

    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Sending…';
    if (errorDiv) errorDiv.classList.add('hidden');

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) throw new Error();

      form.reset();
      btn.textContent = 'Sent!';
      const success = document.createElement('p');
      success.className = 'form-success';
      success.textContent = "Message sent! We’ll get back to you within a few business days.";
      btn.insertAdjacentElement('afterend', success);
    } catch {
      if (errorDiv) {
        errorDiv.textContent = 'Something went wrong. Please email us directly at ' + emailOf('email') + '.';
        errorDiv.classList.remove('hidden');
      }
      btn.disabled = false;
      btn.textContent = originalText;
    }
  });
})();

// ── Season page: month-grid calendar ───────────────────
// Draws a Google-Calendar-style month view from the JSON in #cal-data. Without JavaScript (and
// on phones, where CSS hides the grid) the plain event list below it is what visitors see.
(function () {
  const mount = document.getElementById('mcal');
  const dataEl = document.getElementById('cal-data');
  if (!mount || !dataEl) return;
  let events;
  try { events = JSON.parse(dataEl.textContent); } catch (e) { return; }
  if (!Array.isArray(events) || !events.length) return;

  const pad = n => String(n).padStart(2, '0');
  const key = (y, m, d) => y + '-' + pad(m + 1) + '-' + pad(d);
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const clock = t => {
    const h = +t.slice(0, 2), m = t.slice(3, 5);
    return (h % 12 || 12) + (m === '00' ? '' : ':' + m) + (h < 12 ? 'am' : 'pm');
  };
  const isCompetition = title => /meet|tournament|championship|scrimmage|kickoff/i.test(title);

  // One entry per day an event covers.
  const byDay = {};
  events.forEach((e, i) => {
    const s = e.start.slice(0, 10), end = e.end.slice(0, 10);
    const t = new Date(s + 'T00:00:00Z'), last = new Date(end + 'T00:00:00Z');
    for (let n = 0; t <= last && n < 60; n++, t.setUTCDate(t.getUTCDate() + 1)) {
      const k = t.toISOString().slice(0, 10);
      (byDay[k] = byDay[k] || []).push({ e, i, first: k === s });
    }
  });

  const now = new Date();
  const todayKey = key(now.getFullYear(), now.getMonth(), now.getDate());
  const lastEnd = events.reduce((m, e) => (e.end > m ? e.end : m), todayKey).slice(0, 7);
  const first = { y: now.getFullYear(), m: now.getMonth() };
  const maxIndex = (+lastEnd.slice(0, 4) - first.y) * 12 + (+lastEnd.slice(5, 7) - 1 - first.m);
  let offset = 0; // months from the current month
  mount.innerHTML = '<div class="mcal-view"></div><div class="mcal-pop" id="mcal-pop" role="tooltip" hidden></div>';
  const view = mount.firstChild, pop = mount.lastChild;

  function render() {
    const y = first.y + Math.floor((first.m + offset) / 12);
    const m = (first.m + offset) % 12;
    const firstDay = new Date(Date.UTC(y, m, 1)).getUTCDay();
    const days = new Date(Date.UTC(y, m + 1, 0)).getUTCDate();
    const weeks = Math.ceil((firstDay + days) / 7);
    let body = '';
    for (let w = 0; w < weeks; w++) {
      body += '<tr>';
      for (let d = 0; d < 7; d++) {
        const day = new Date(Date.UTC(y, m, 1 - firstDay + w * 7 + d));
        const k = day.toISOString().slice(0, 10);
        const inMonth = day.getUTCMonth() === m;
        const items = (byDay[k] || []).map(x => {
          const time = !x.e.allDay && x.first ? '<span class="mcal-time">' + clock(x.e.start.slice(11)) + '</span> ' : '';
          const kind = isCompetition(x.e.title) ? 'mcal-ev--comp' : 'mcal-ev--misc';
          return '<li class="mcal-ev ' + kind + '" tabindex="0" data-i="' + x.i + '">' + time + escapeHTML(x.e.title) + '</li>';
        }).join('');
        const cls = 'mcal-cell' + (inMonth ? '' : ' mcal-cell--out') + (k === todayKey ? ' mcal-cell--today' : '');
        body += '<td class="' + cls + '"><span class="mcal-num">' + day.getUTCDate() + '</span>' + (items ? '<ul class="mcal-evs">' + items + '</ul>' : '') + '</td>';
      }
      body += '</tr>';
    }
    view.innerHTML =
      '<div class="mcal-bar">' +
        '<h3 class="mcal-title" aria-live="polite">' + MONTHS[m] + ' ' + y + '</h3>' +
        '<div class="mcal-nav">' +
          '<button type="button" class="mcal-btn mcal-today"' + (offset === 0 ? ' disabled' : '') + '>Today</button>' +
          '<button type="button" class="mcal-btn mcal-prev" aria-label="Previous month"' + (offset <= 0 ? ' disabled' : '') + '>&#8249;</button>' +
          '<button type="button" class="mcal-btn mcal-next" aria-label="Next month"' + (offset >= maxIndex ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
      '</div>' +
      '<table class="mcal-table"><caption class="sr-only">' + MONTHS[m] + ' ' + y + '</caption>' +
      '<thead><tr>' + DAYS.map(d => '<th scope="col">' + d + '</th>').join('') + '</tr></thead>' +
      '<tbody>' + body + '</tbody></table>';
  }

  // Hover / keyboard-focus / tap card with an event's details.
  let current = null;
  function hidePop() {
    pop.hidden = true;
    if (current) current.removeAttribute('aria-describedby');
    current = null;
  }
  function showPop(chip) {
    const e = events[+chip.dataset.i];
    if (!e) return;
    if (current && current !== chip) current.removeAttribute('aria-describedby');
    current = chip;
    chip.setAttribute('aria-describedby', 'mcal-pop');
    pop.className = 'mcal-pop ' + (chip.classList.contains('mcal-ev--comp') ? 'mcal-pop--comp' : 'mcal-pop--misc');
    pop.innerHTML =
      '<p class="mcal-pop-title">' + escapeHTML(e.title) + '</p>' +
      '<p class="mcal-pop-when">' + escapeHTML(e.when) + '</p>' +
      (e.venue ? '<p class="mcal-pop-where"><strong>' + escapeHTML(e.venue) + '</strong>' +
        (e.address ? '<br>' + escapeHTML(e.address) : '') + '</p>' : '');
    pop.hidden = false;
    // Place under the chip (above it near the bottom), kept inside the calendar's width.
    const box = mount.getBoundingClientRect(), r = chip.getBoundingClientRect();
    const w = pop.offsetWidth, h = pop.offsetHeight;
    let left = r.left - box.left;
    left = Math.max(0, Math.min(left, box.width - w));
    let top = r.bottom - box.top + 6;
    if (r.bottom + h + 12 > window.innerHeight && r.top - box.top - h - 6 >= 0) top = r.top - box.top - h - 6;
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
  }
  const chipOf = t => (t.closest ? t.closest('.mcal-ev') : null);
  mount.addEventListener('mouseover', e => { const c = chipOf(e.target); if (c) showPop(c); });
  mount.addEventListener('mouseout', e => { if (chipOf(e.target) && !chipOf(e.relatedTarget || document.body)) hidePop(); });
  mount.addEventListener('focusin', e => { const c = chipOf(e.target); if (c) showPop(c); });
  mount.addEventListener('focusout', e => { if (chipOf(e.target)) hidePop(); });
  mount.addEventListener('click', e => {
    const c = chipOf(e.target);
    if (c) { if (current === c && !pop.hidden) hidePop(); else showPop(c); return; }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') hidePop(); });

  mount.addEventListener('click', e => {
    const btn = e.target.closest('button');
    if (!btn || btn.disabled) return;
    if (btn.classList.contains('mcal-prev')) offset = Math.max(0, offset - 1);
    else if (btn.classList.contains('mcal-next')) offset = Math.min(maxIndex, offset + 1);
    else if (btn.classList.contains('mcal-today')) offset = 0;
    else return;
    hidePop();
    render();
    const again = mount.querySelector('.' + btn.className.split(' ').filter(c => c !== 'mcal-btn')[0]);
    if (again && !again.disabled) again.focus();
  });

  render();
  mount.hidden = false;
  document.getElementById('calendar').classList.add('has-grid');
})();

// ── Season page: live stream ──────────────────────────
// Event cards are rendered at build time from /assets/data/season.json (with absolute
// start/end timestamps). Here the browser decides which state to show: the event's
// stream while it's on air (from 30 minutes before the start to 1 hour after the end),
// otherwise the next event, otherwise a "nothing scheduled" note.
(function () {
  const stage = document.getElementById('stream-stage');
  if (!stage) return;

  const PRE_MS = 30 * 60 * 1000;
  const POST_MS = 60 * 60 * 1000;
  const autoplay = (stage.closest('#watch') || {}).dataset?.autoplay !== 'false';

  const events = Array.from(document.querySelectorAll('.season-event')).map(el => ({
    el,
    name: el.dataset.name || 'Event',
    start: new Date(el.dataset.start).getTime(),
    end: new Date(el.dataset.end).getTime(),
    stream: el.dataset.stream || '',
    channel: el.dataset.youtubeChannel || '',
    info: el.dataset.info || '',
    results: el.dataset.results || ''
  })).sort((a, b) => a.start - b.start);

  // Turn a YouTube or Twitch link into an embeddable player URL (or '' if unsupported).
  function embedUrl(event) {
    const yt = 'https://www.youtube-nocookie.com/embed/';
    const ytParams = '?autoplay=' + (autoplay ? 1 : 0) + '&mute=1&playsinline=1&rel=0';
    if (event.channel) {
      return yt + 'live_stream' + ytParams + '&channel=' + encodeURIComponent(event.channel);
    }
    let url;
    try { url = new URL(event.stream); } catch (e) { return ''; }
    const host = url.hostname.replace(/^www\./, '');
    if (host === 'youtu.be') {
      return yt + encodeURIComponent(url.pathname.slice(1)) + ytParams;
    }
    if (host === 'youtube.com' || host === 'm.youtube.com') {
      const id = url.searchParams.get('v') || (url.pathname.match(/^\/(?:live|embed)\/([\w-]+)/) || [])[1];
      return id ? yt + encodeURIComponent(id) + ytParams : '';
    }
    if (host === 'twitch.tv') {
      const channel = url.pathname.split('/').filter(Boolean)[0];
      return channel
        ? 'https://player.twitch.tv/?channel=' + encodeURIComponent(channel) +
          '&parent=' + encodeURIComponent(location.hostname) +
          '&autoplay=' + (autoplay ? 'true' : 'false') + '&muted=true'
        : '';
    }
    return '';
  }

  function relative(ms) {
    const mins = Math.round(ms / 60000);
    if (mins < 60) return mins + ' minute' + (mins === 1 ? '' : 's');
    const hours = Math.round(mins / 60);
    if (hours < 48) return hours + ' hour' + (hours === 1 ? '' : 's');
    const days = Math.round(hours / 24);
    return days + ' days';
  }

  function linkButtons(event) {
    const out = [];
    if (event.stream) out.push(['Open stream', event.stream]);
    if (event.info) out.push(['Event page', event.info]);
    if (event.results) out.push(['Live results', event.results]);
    return out.map(([label, href]) =>
      '<a class="btn-outline" href="' + escapeHTML(href) + '" target="_blank" rel="noopener noreferrer">' + escapeHTML(label) + '</a>'
    ).join('');
  }

  function panel(title, text, extra) {
    stage.className = 'stream-stage';
    stage.innerHTML =
      '<div class="stream-panel">' +
      '<p class="stream-panel-title">' + escapeHTML(title) + '</p>' +
      '<p class="stream-panel-text">' + text + '</p>' +
      (extra ? '<div class="stream-panel-actions">' + extra + '</div>' : '') +
      '</div>';
  }

  let shown = null;
  function update() {
    const now = Date.now();
    events.forEach(e => {
      e.el.classList.toggle('is-past', now > e.end + POST_MS);
      e.el.classList.toggle('is-live', now >= e.start - PRE_MS && now <= e.end + POST_MS);
    });
    const live = events.find(e => now >= e.start - PRE_MS && now <= e.end + POST_MS);
    const next = events.find(e => e.start - PRE_MS > now);
    const key = live ? 'live:' + live.start : next ? 'next:' + next.start : 'none';
    // Re-render only when the state changes, so a playing stream is never reloaded.
    if (key === shown && !(next && !live)) return;
    shown = key;

    if (live) {
      const src = embedUrl(live);
      if (src) {
        stage.className = 'stream-stage is-live';
        stage.innerHTML =
          '<iframe src="' + escapeHTML(src) + '" title="' + escapeHTML(live.name) + ' live stream" ' +
          'allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen ' +
          'referrerpolicy="strict-origin-when-cross-origin"></iframe>';
        return;
      }
      panel('Live now: ' + live.name, 'We\'re competing right now. The stream link isn\'t available on this page yet.', linkButtons(live));
      return;
    }
    if (next) {
      panel('Next up: ' + next.name,
        'Starts in about ' + relative(next.start - now) + '. The stream will appear here when the event goes on air.',
        linkButtons(next));
      return;
    }
    panel('No events scheduled', 'There\'s nothing on air right now. Check back before our next competition.', '');
  }

  update();
  setInterval(update, 60 * 1000);
})();