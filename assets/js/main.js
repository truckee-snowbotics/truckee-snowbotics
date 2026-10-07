/* main.js — Truckee Snowbotics */
'use strict';

// ╔══════════════════════════════════════════════════╗
// ║  LINKS — single source of truth:                 ║
// ║  /assets/data/links.json                         ║
// ╠══════════════════════════════════════════════════╣
// ║  Each entry: { id, label, url, listed }          ║
// ║  - id matches data-link-key / data-form-action   ║
// ║    attributes in the HTML                        ║
// ║  - listed: true → also rendered on the           ║
// ║    Information page links grid and in the footer ║
// ║  - url "#" → no destination yet; the element is  ║
// ║    hidden until a real URL is set                ║
// ║  - emails are entries too, as mailto: URLs       ║
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
// ── Active nav link (page-based) ─────────────
(function () {
  const links = document.querySelectorAll('.nav a, #mobile-nav > a');
  if (!links.length) return;

  // Normalise pathname to always end with /
  const currentPath = window.location.pathname.replace(/\/?$/, '/');

  links.forEach(l => {
    const href = l.getAttribute('href') || '';
    const linkPath = href.split('#')[0].replace(/\/?$/, '/');
    l.classList.toggle('active', linkPath === currentPath);
  });
})();

// ── Nav that folds into the hamburger ────────
// As the window narrows, the last links move into the hamburger menu one at a time. If fewer
// than MIN_INLINE links would stay in the bar, they all move into the menu.
(function () {
  const nav = document.getElementById('main-nav');
  const btn = document.getElementById('hamburger');
  const drawer = document.getElementById('mobile-nav');
  if (!nav || !btn || !drawer) return;
  const MIN_INLINE = 3;
  const links = Array.from(nav.querySelectorAll('a'));
  const drawerLinks = Array.from(drawer.querySelectorAll(':scope > a'));

  const fitCount = () => {
    let n = 0;
    links.forEach((l, i) => { if (l.offsetLeft + l.offsetWidth <= nav.clientWidth) n = i + 1; });
    return n;
  };
  const layout = () => {
    links.forEach(l => l.classList.remove('in-menu'));
    btn.classList.remove('show');
    let n = fitCount();
    if (n < links.length) {            // something doesn't fit: the hamburger takes space, so measure again
      btn.classList.add('show');
      n = fitCount();
    }
    if (n < MIN_INLINE) n = 0;
    links.forEach((l, i) => l.classList.toggle('in-menu', i >= n));
    drawerLinks.forEach((l, i) => l.classList.toggle('in-bar', i < n));
    btn.classList.toggle('show', n < links.length);
    if (n >= links.length) {           // everything fits: close the menu if it was open
      drawer.classList.remove('open'); btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false'); drawer.setAttribute('aria-hidden', 'true');
    }
  };
  layout();
  if (window.ResizeObserver) new ResizeObserver(layout).observe(nav.parentElement); else window.addEventListener('resize', layout);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
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

  const close = () => {
    nav.classList.remove('open');
    btn.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
    nav.setAttribute('aria-hidden', 'true');
  };
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) { close(); btn.focus(); } });
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