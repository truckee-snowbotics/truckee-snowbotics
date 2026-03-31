/* main.js — Truckee Snowbotics */
'use strict';

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
