/* main.js — Truckee Snowbotics */
'use strict';

const LINK_TARGETS = {
  instagram: 'https://www.instagram.com/truckeesnowbotics/',
  githubRepo: 'https://github.com/NoisyDream18/FTC-Truckee-Robotics',
  github: 'https://github.com/NoisyDream18',
  about: '#about',
  team: '#team',
  gallery: '#gallery',
  sponsors: '#sponsors',
  contact: '#contact',
  join: 'https://forms.gle/21LAVqmfFErDXKMv6',
  sponsorshipForm: '#',
  formAction: 'https://formspree.io/f/{your-form-id}'
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

// ── Active nav on scroll ──────────────────────
(function () {
  const sections = document.querySelectorAll('section[id]');
  const links    = document.querySelectorAll('.nav a[href^="#"]');
  if (!sections.length || !links.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      links.forEach(l => {
        l.classList.toggle('active', l.getAttribute('href') === `#${e.target.id}`);
      });
    });
  }, { threshold: 0.45 });

  sections.forEach(s => io.observe(s));
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

  fetch('assets/data/team.json')
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

  fetch('assets/data/gallery.json')
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
            ${image ? `<img src="${escapeHTML(src)}" alt="${escapeHTML(alt)}" />` : `<span>${escapeHTML(caption)}</span>`}
            <div class="gallery-caption">${escapeHTML(caption)}</div>
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

  fetch('assets/data/sponsors.json')
    .then(response => {
      if (!response.ok) throw new Error('Sponsors JSON not found');
      return response.json();
    })
    .then(items => {
      if (!Array.isArray(items)) throw new Error('Invalid sponsors data');
      const sponsorHtml = items.map(item => {
        const logo = item.logo ? `<div class="sponsor-item-logo"><img src="${escapeHTML(item.logo)}" alt="${escapeHTML(item.name || 'Sponsor')} logo" /></div>` : '';
        const copy = `
          <div class="sponsor-item-copy">
            <span class="sponsor-name">${escapeHTML(item.name || 'Sponsor')}</span>
            <span class="sponsor-description">${escapeHTML(item.description || '')}</span>
          </div>
        `;
        const hasLink = item.website && item.website.trim();
        const tag = hasLink ? 'a' : 'div';
        const hrefAttr = hasLink ? ` href="${escapeHTML(item.website)}" target="_blank" rel="noopener noreferrer"` : '';

        return `
          <${tag} class="sponsor-item"${hrefAttr}>
            ${logo}
            ${copy}
          </${tag}>
        `;
      }).join('');

      grid.innerHTML = sponsorHtml;
    })
    .catch(() => {
      // keep the existing static markup if loading fails
    });
})();
// ── Contact form demo error handler ─────────────────
(function () {
  const contactForm = document.querySelector('.contact-form');
  if (!contactForm) return;

  const contactFormErrorText = 'Error: No FormSpree endpoint configured.';
  const errorEl = contactForm.querySelector('.form-error');

  contactForm.addEventListener('submit', function (event) {
    event.preventDefault();
    if (errorEl) {
      errorEl.textContent = contactFormErrorText;
      errorEl.classList.remove('hidden');
    }
  });
})();