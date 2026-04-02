/* main.js — Truckee Snowbotics */
'use strict';

// ╔══════════════════════════════════════════════════╗
// ║  LINKS — edit these when URLs change             ║
// ╠══════════════════════════════════════════════════╣
// ║  Any element with data-link-key="keyName" will   ║
// ║  automatically get its href set to the value     ║
// ║  below. Forms use data-form-action="formAction". ║
// ╚══════════════════════════════════════════════════╝
const LINK_TARGETS = {
  // ── Socials ──────────────────────────────────────
  instagram:      'https://www.instagram.com/truckeesnowbotics/',
  github:         'https://github.com/truckee-snowbotics',
  githubRepo:     'https://github.com/truckee-snowbotics/truckee-snowbotics',

  // ── Forms ─────────────────────────────────────────
  join:           'https://forms.gle/21LAVqmfFErDXKMv6',
  sponsorshipForm:'/assets/files/sponsorship-form.pdf',
  formAction:     'https://formspree.io/f/xkopzlvz',
  donate:         'https://hcb.hackclub.com/donations/start/truckee-snowbotics',

  // ── Internal pages ────────────────────────────────
  contact:        '/contact/',
};

function applyLinkTargets() {
  document.querySelectorAll('[data-link-key]').forEach(el => {
    const key = el.dataset.linkKey;
    if (!key || !(key in LINK_TARGETS)) return;
    el.href = LINK_TARGETS[key];
  });

  document.querySelectorAll('[data-form-action]').forEach(el => {
    const key = el.dataset.formAction;
    if (!key || !(key in LINK_TARGETS)) return;
    el.action = LINK_TARGETS[key];
  });
}

applyLinkTargets();

// ── Scroll reveal ─────────────────────────────
(function () {
  const targets = document.querySelectorAll('.section, .card, .about-stats, .about-text');
  if (!targets.length) return;

  targets.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
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
              ${hasPhoto ? `<img src="${escapeHTML(member.photo)}" alt="${escapeHTML(member.name || 'Team member')}" />` : escapeHTML(initials)}
            </div>
            <div class="member-info">
              <span class="member-name">${escapeHTML(member.name || 'Unnamed')}</span>
              <span class="member-role">${escapeHTML(member.role || '')}</span>
            </div>
          </div>
        `;
      }).join('');
    })
    .catch(() => {
      // keep the existing static markup if loading fails
    });

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

  function escapeHTML(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
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
              ${image ? `<img src="${escapeHTML(src)}" alt="${escapeHTML(alt)}" />` : `<span>${escapeHTML(caption)}</span>`}
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
    }

    function closeModal() {
      modal.classList.add('hidden');
      modal.setAttribute('aria-hidden', 'true');
      modalImage.innerHTML = '';
      if (modalCaption) modalCaption.textContent = '';
    }

    const track = document.querySelector('.gallery-track');
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

// ── Load sponsors from JSON ─────────────────
(function () {
  const grid = document.querySelector('.sponsor-grid');
  if (!grid) return;

  fetch('/assets/data/sponsors.json')
    .then(response => {
      if (!response.ok) throw new Error('Sponsors JSON not found');
      return response.json();
    })
    .then(items => {
      if (!Array.isArray(items)) throw new Error('Invalid sponsors data');
      const sponsorHtml = items.map(item => {
        const hasLink = item.website && item.website.trim();
        const tag = hasLink ? 'a' : 'div';
        const hrefAttr = hasLink ? ` href="${escapeHTML(item.website)}" target="_blank" rel="noopener noreferrer"` : '';
        const banner = item.banner
          ? `<img src="${escapeHTML(item.banner)}" alt="${escapeHTML(item.name || 'Sponsor')} banner" />`
          : '';

        return `<${tag} class="sponsor-item"${hrefAttr}>${banner}</${tag}>`;
      }).join('');

      grid.innerHTML = sponsorHtml;
    })
    .catch(() => {
      // keep the existing static markup if loading fails
    });
})();

// ── Sponsor bar ───────────────────────────────────────
(function () {
  const bar = document.getElementById('sponsor-bar-logos');
  if (!bar) return;

  fetch('/assets/data/sponsors.json')
    .then(r => { if (!r.ok) throw new Error(); return r.json(); })
    .then(items => {
      if (!Array.isArray(items) || !items.length) return;
      bar.innerHTML = items.map(item => {
        const hasLink = item.website && item.website.trim();
        const tag = hasLink ? 'a' : 'div';
        const attrs = hasLink ? ` href="${escapeHTML(item.website)}" target="_blank" rel="noopener noreferrer"` : '';
        const banner = item.banner
          ? `<img src="${escapeHTML(item.banner)}" alt="${escapeHTML(item.name || 'Sponsor')} banner" />`
          : '';
        return `<${tag} class="sponsor-bar-logo"${attrs}>${banner}</${tag}>`;
      }).join('');
    })
    .catch(() => {});
})();

// ── Load links from JSON ──────────────────────────────
(function () {
  fetch('/assets/data/links.json')
    .then(r => { if (!r.ok) throw new Error(); return r.json(); })
    .then(items => {
      if (!Array.isArray(items) || !items.length) return;

      const grid = document.getElementById('links-grid');
      if (grid) {
        grid.innerHTML = items.map(item => {
          const url = item.url && item.url.trim() ? item.url : '#';
          return `
            <a class="link-card" href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">
              <span class="link-card-label">${escapeHTML(item.label || '')}</span>
              ${item.category ? `<span class="link-card-category">${escapeHTML(item.category)}</span>` : ''}
            </a>`;
        }).join('');
      }

      const footerLinks = document.getElementById('footer-links-list');
      if (footerLinks) {
        footerLinks.innerHTML = items.map(item => {
          const url = item.url && item.url.trim() ? item.url : '#';
          return `<a href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(item.label || '')}</a>`;
        }).join('');
      }

      const footerNav = document.querySelector('.footer-nav');
      if (footerNav) {
        const sep = document.createElement('span');
        sep.className = 'footer-nav-sep';
        footerNav.appendChild(sep);
        items.forEach(item => {
          const url = item.url && item.url.trim() ? item.url : '#';
          const a = document.createElement('a');
          a.href = url;
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
    .then(r => r.json())
    .then(items => {
      // Sort by order ascending; items with same order are left in random relative positions
      items.sort((a, b) => {
        if (a.order !== b.order) return a.order - b.order;
        return Math.random() - 0.5;
      });
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
  const contactForm = document.querySelector('.contact-form');
  if (!contactForm) return;
  // Form submits natively to Formspree via action attribute set by applyLinkTargets()
})();