/* main.js — Truckee Snowbotics */
'use strict';

// ╔══════════════════════════════════════════════════╗
// ║  CONTACT EMAIL — change this one value to update ║
// ║  the email address everywhere on the site.       ║
// ╚══════════════════════════════════════════════════╝
const CONTACT_EMAIL = 'contact@snowbotics.org';

// ╔══════════════════════════════════════════════════╗
// ║  CONTACT NOTICE BANNER                           ║
// ╠══════════════════════════════════════════════════╣
// ║  Set enabled: true to show the banner,           ║
// ║  false to hide it site-wide instantly.           ║
// ╚══════════════════════════════════════════════════╝
const CONTACT_NOTICE = {
  enabled: false,
  email:   'truckeesnowbotics@gmail.com',
};

// ╔══════════════════════════════════════════════════╗
// ║  SPONSORSHIP FORM NOTICE                         ║
// ╠══════════════════════════════════════════════════╣
// ║  Set enabled: true to show a hover popup on all  ║
// ║  sponsorship form buttons. Edit message freely.  ║
// ╚══════════════════════════════════════════════════╝
const SPONSORSHIP_FORM_NOTICE = {
  enabled: true,
  message: 'The sponsorship form has an incorrect email. Please use contact@snowbotics.org instead.',
};

// ╔══════════════════════════════════════════════════╗
// ║  SECTION VISIBILITY                              ║
// ╠══════════════════════════════════════════════════╣
// ║  Hide parts of the site and/or show a notice     ║
// ║  strip. Each rule:                               ║
// ║    page:     optional — only apply on this page  ║
// ║              (e.g. '/season/'; omit = all pages) ║
// ║    selector: CSS selector for the target(s)      ║
// ║    hide:     false → keep visible, notice only   ║
// ║              (default true: hide the target)     ║
// ║    message:  optional notice strip shown where   ║
// ║              the target is/was                   ║
// ║  Examples:                                       ║
// ║  { page: '/gallery/', selector: '#gallery',      ║
// ║    message: 'Gallery is being updated.' }        ║
// ║  { selector: '#news', hide: true }  ← silent     ║
// ╚══════════════════════════════════════════════════╝
const SECTION_VISIBILITY = [
  {
    page: '/season/',
    selector: '#main-content',
    hide: true,
    message: 'This page is under construction — check back soon for robot specs and competition results.',
  },
];

// ── Apply section visibility rules ────────────────
(function () {
  const currentPath = window.location.pathname.replace(/\/?$/, '/');
  SECTION_VISIBILITY.forEach(rule => {
    if (!rule.selector) return;
    if (rule.page && rule.page.replace(/\/?$/, '/') !== currentPath) return;
    const targets = document.querySelectorAll(rule.selector);
    if (!targets.length) return;
    if (rule.hide !== false) {
      // Class with !important so later scripts toggling inline styles
      // (e.g. the season loader) can't accidentally reveal the section.
      targets.forEach(el => el.classList.add('section-hidden'));
    }
    if (rule.message) {
      const notice = document.createElement('div');
      notice.className = 'section-notice';
      notice.textContent = rule.message;
      targets[0].insertAdjacentElement('beforebegin', notice);
    }
  });
})();

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
// ╚══════════════════════════════════════════════════╝
let linksPromise = null;
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
  const urlById = {};
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

// ── Apply CONTACT_EMAIL to all mailto links ───────
(function applyContactEmail() {
  // Update all mailto anchor href and visible email text
  document.querySelectorAll('a[href^="mailto:"]').forEach(el => {
    el.href = 'mailto:' + CONTACT_EMAIL;
    if (el.textContent.includes('@')) el.textContent = CONTACT_EMAIL;
  });

  // Update JSON-LD structured data email field if present
  document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
    try {
      const data = JSON.parse(script.textContent);
      if (data.email !== undefined) {
        data.email = CONTACT_EMAIL;
        script.textContent = JSON.stringify(data, null, 2);
      }
    } catch (e) { /* malformed JSON-LD — skip */ }
  });
})();

// ── Contact notice banner ─────────────────────────
(function () {
  const banner = document.getElementById('notice-banner');
  if (!banner || !CONTACT_NOTICE.enabled) return;

  // Populate email link from config
  const link = banner.querySelector('a[data-notice-email]');
  if (link) {
    link.href = 'mailto:' + CONTACT_NOTICE.email;
    link.textContent = CONTACT_NOTICE.email;
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
    sendBtn.style.opacity = '0.45';
    sendBtn.style.cursor = 'not-allowed';

    // Insert explanation below the button
    const notice = document.createElement('p');
    notice.style.cssText = 'margin-top:.75rem;font-size:.875rem;background:#3b1010;color:#fca5a5;border:1px solid #7f1d1d;border-radius:0;padding:.6rem .85rem;line-height:1.5;';
    notice.innerHTML = '&#9888; Contact form submissions are currently unavailable. Please reach us directly at <a href="mailto:' + CONTACT_NOTICE.email + '" style="color:#fde68a;text-decoration:underline;font-weight:600;">' + CONTACT_NOTICE.email + '</a>.';
    sendBtn.insertAdjacentElement('afterend', notice);

    const form = sendBtn.closest('form');
    if (form) {
      form.addEventListener('submit', (e) => { e.preventDefault(); });
    }
  }
})();

// ── Sponsorship form hover notice ────────────
(function () {
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
  tooltip.textContent = SPONSORSHIP_FORM_NOTICE.message;
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
})();

// ── Scroll reveal ─────────────────────────────
(function () {
  const targets = document.querySelectorAll('.section, .card, .about-stats, .about-text');
  if (!targets.length) return;

  targets.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('visible');
      io.unobserve(e.target);
    });
  }, { threshold: 0.08 });

  targets.forEach(el => io.observe(el));
})();

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

// ── Load team cards from JSON ─────────────────
(function () {
  const grid = document.querySelector('.team-grid');
  if (!grid) return;

  fetch('/assets/data/team.json')
    .then(response => {
      if (!response.ok) throw new Error('Team JSON not found');
      return response.json();
    })
    .then(members => {
      if (!Array.isArray(members)) throw new Error('Invalid team data');
      grid.innerHTML = members.map(member => {
        const empty = member.empty ? ' member-card--empty' : '';
        const avatarClass = member.empty ? 'member-avatar member-avatar--empty' : 'member-avatar';
        const initials = member.initials || getInitials(member.name);
        const hasPhoto = member.photo && !member.empty;

        return `
          <div class="member-card${empty}">
            <div class="${avatarClass}">
              ${hasPhoto ? `<img src="${escapeHTML(member.photo)}" alt="${escapeHTML(member.name || 'Team member')}" loading="lazy" decoding="async" />` : escapeHTML(initials)}
            </div>
            <div class="member-info">
              <span class="member-name">${escapeHTML(member.name || 'Unnamed')}</span>
              <span class="member-role">${escapeHTML(member.role || '')}</span>
            </div>
          </div>
        `;
      }).join('');
    })
    .catch(() => {});

  function getInitials(name) {
    if (!name) return '';
    return name
      .split(/\s+/)
      .filter(Boolean)
      .map(word => word[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

})();

// ── Load gallery from JSON ─────────────────
(function () {
  const track = document.querySelector('.gallery-track');
  if (!track) return;

  fetch('/assets/data/gallery.json')
    .then(response => {
      if (!response.ok) throw new Error('Gallery JSON not found');
      return response.json();
    })
    .then(items => {
      if (!Array.isArray(items) || !items.length) throw new Error('Invalid gallery data');

      const cards = items.map(item => {
        const image = item.src && item.src.trim();
        const src = item.src || '';
        const caption = item.description && item.description.trim() ? item.description.trim() : 'No caption';
        const alt = caption || 'Gallery image';

        return `
          <div class="gallery-item" data-src="${escapeHTML(src)}" data-alt="${escapeHTML(alt)}" data-caption="${escapeHTML(caption)}">
            <div class="gallery-image">
              ${image ? `<img src="${escapeHTML(src)}" alt="${escapeHTML(alt)}" loading="lazy" decoding="async" />` : `<span>${escapeHTML(caption)}</span>`}
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
      if (footerNav) {
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

// ── News feed ────────────────────────────────────────
(function () {
  const grid = document.getElementById('news-grid');
  if (!grid) return;
  fetch('/assets/data/news.json')
    .then(r => { if (!r.ok) throw new Error(); return r.json(); })
    .then(items => {
      // Sort by order ascending; items without an order sink to the bottom.
      // Ties keep their order from news.json (Array.sort is stable).
      items.sort((a, b) => (a.order ?? Infinity) - (b.order ?? Infinity));
      grid.innerHTML = items.map(item => `
        <div class="news-card">
          <div class="news-card-meta">
            <span class="news-card-date">${escapeHTML(item.date || '')}</span>
            <span class="news-card-tag">${escapeHTML(item.tag || '')}</span>
          </div>
          <h3 class="news-card-title">${escapeHTML(item.title || '')}</h3>
          <p class="news-card-text">${escapeHTML(item.text || '')}</p>
        </div>`).join('');
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
        errorDiv.textContent = 'Something went wrong. Please email us directly at ' + CONTACT_EMAIL + '.';
        errorDiv.classList.remove('hidden');
      }
      btn.disabled = false;
      btn.textContent = originalText;
    }
  });
})();

// ── Season page ───────────────────────────────────────
(function () {
  // Only run on the season page
  if (!document.getElementById('results-table-body')) return;

  fetch('/assets/data/seasons.json')
    .then(r => { if (!r.ok) throw new Error(); return r.json(); })
    .then(seasons => {
      if (!Array.isArray(seasons) || !seasons.length) return;

      const current = seasons.find(s => s.current) || seasons[0];

      // Hide static SEO anchor now that real content is loading
      const seoAnchor = document.getElementById('season-intro-seo');
      if (seoAnchor) seoAnchor.style.display = 'none';

      // Reveal the data-driven sections (hidden with inline display:none
      // in the HTML so they never flash empty before data arrives)
      ['season-hero', 'robot', 'results', 'archive'].forEach(id => {
        const section = document.getElementById(id);
        if (section) section.style.display = '';
      });

      // Hero
      const badge = document.getElementById('season-badge');
      const gameName = document.getElementById('season-game-name');
      const robotNameLabel = document.getElementById('season-robot-name-label');
      if (badge) badge.textContent = current.year + ' Season';
      if (gameName) gameName.textContent = current.game || current.year + ' Season';
      if (robotNameLabel && current.robot) robotNameLabel.textContent = current.robot.name || '';

      // Robot section
      const robotHeading = document.getElementById('robot-name-heading');
      const robotDesc = document.getElementById('robot-description');
      const robotSpecs = document.getElementById('robot-specs-grid');
      if (current.robot) {
        if (robotHeading) robotHeading.textContent = current.robot.name || 'Robot';
        if (robotDesc) robotDesc.textContent = current.robot.description || '';
        if (robotSpecs && Array.isArray(current.robot.specs)) {
          robotSpecs.innerHTML = current.robot.specs.map(spec => `
            <div class="info-card">
              <span class="info-card-title">${escapeHTML(spec.label)}</span>
              <p class="info-card-body">${escapeHTML(spec.value)}</p>
            </div>`).join('');
        }
      }

      // Results table
      const resultsLabel = document.getElementById('results-season-label');
      const tbody = document.getElementById('results-table-body');
      if (resultsLabel) resultsLabel.textContent = current.year + ' Season';
      if (tbody && Array.isArray(current.tournaments) && current.tournaments.length) {
        tbody.innerHTML = current.tournaments.map(t => `
          <tr>
            <td>${escapeHTML(t.name || '—')}</td>
            <td>${escapeHTML(t.date || '—')}</td>
            <td>${escapeHTML(t.location || '—')}</td>
            <td>${escapeHTML(t.ranking || '—')}</td>
            <td>${escapeHTML(t.record || '—')}</td>
            <td>${escapeHTML(t.awards || '—')}</td>
          </tr>`).join('');
      } else if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-dim);padding:2rem;">No results available yet.</td></tr>';
      }

      // Archive (all non-current seasons)
      const archiveList = document.getElementById('season-archive-list');
      const past = seasons.filter(s => !s.current);
      if (archiveList && past.length) {
        archiveList.innerHTML = past.map(s => `
          <div class="season-archive-item">
            <div class="season-archive-header">
              <span class="season-badge">${escapeHTML(s.year)} Season</span>
              <span class="season-archive-game">${escapeHTML(s.game || '')}</span>
            </div>
            ${s.robot ? `<p class="season-archive-robot"><strong>Robot:</strong> ${escapeHTML(s.robot.name || '—')}</p>` : ''}
            ${Array.isArray(s.tournaments) && s.tournaments.length ? `
            <div class="results-table-wrapper">
              <table class="results-table">
                <thead><tr><th>Event</th><th>Date</th><th>Location</th><th>Ranking</th><th>Record</th><th>Awards</th></tr></thead>
                <tbody>${s.tournaments.map(t => `
                  <tr>
                    <td>${escapeHTML(t.name || '—')}</td>
                    <td>${escapeHTML(t.date || '—')}</td>
                    <td>${escapeHTML(t.location || '—')}</td>
                    <td>${escapeHTML(t.ranking || '—')}</td>
                    <td>${escapeHTML(t.record || '—')}</td>
                    <td>${escapeHTML(t.awards || '—')}</td>
                  </tr>`).join('')}
                </tbody>
              </table>
            </div>` : ''}
          </div>`).join('');
      } else if (archiveList) {
        archiveList.innerHTML = '<p style="color:var(--text-dim);font-size:.9rem;">Past seasons will appear here as they are added to seasons.json.</p>';
      }
    })
    .catch(() => {
      const results = document.getElementById('results');
      if (results) results.style.display = '';
      const tbody = document.getElementById('results-table-body');
      if (tbody) tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-dim);padding:2rem;">Could not load season data.</td></tr>';
    });
})();