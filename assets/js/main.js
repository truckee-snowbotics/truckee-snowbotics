/* main.js — NoisyDream18.github.io
   Zero dependencies. Vanilla ES6+. */

'use strict';

// ── Animated grid canvas ──────────────────────
(function () {
  const canvas = document.getElementById('grid-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, cols, rows, cells;

  const CELL = 48;
  const COLOR_DIM  = 'rgba(26, 35, 50, 0.9)';   // --border
  const COLOR_ACC  = 'rgba(0, 200, 255, 0.5)';  // --acc bright
  const COLOR_MED  = 'rgba(0, 200, 255, 0.15)'; // midpoint
  const DOT_R = 1.5;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
    cols = Math.ceil(W / CELL) + 1;
    rows = Math.ceil(H / CELL) + 1;
    cells = Array.from({ length: cols * rows }, () => ({
      brightness: 0,
      target: 0,
      delay: Math.random() * 200,
    }));
  }

  // Randomly light up cells
  function spark() {
    const idx = Math.floor(Math.random() * cells.length);
    cells[idx].target = Math.random() * 0.9 + 0.1;
    cells[idx].delay = 0;
  }

  let last = 0;
  function loop(ts) {
    requestAnimationFrame(loop);
    const dt = Math.min(ts - last, 50);
    last = ts;

    // Spark a few cells per frame
    if (Math.random() < 0.08) spark();

    ctx.clearRect(0, 0, W, H);

    cells.forEach((cell, i) => {
      // Ease toward target
      if (cell.delay > 0) { cell.delay -= dt; return; }
      cell.brightness += (cell.target - cell.brightness) * 0.04;
      if (Math.abs(cell.target - cell.brightness) < 0.005 && cell.target > 0.01) {
        cell.target = 0;
      }

      const col = i % cols;
      const row = Math.floor(i / cols);
      const x = col * CELL;
      const y = row * CELL;
      const b = cell.brightness;

      // Draw grid lines only when bright enough
      if (b > 0.01) {
        ctx.globalAlpha = b * 0.35;
        ctx.strokeStyle = COLOR_ACC;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        // right line
        ctx.moveTo(x, y); ctx.lineTo(x + CELL, y);
        // down line
        ctx.moveTo(x, y); ctx.lineTo(x, y + CELL);
        ctx.stroke();
      }

      // Draw dot at intersection
      ctx.globalAlpha = b > 0.01 ? b * 0.8 : 0.12;
      ctx.fillStyle = b > 0.01 ? COLOR_ACC : COLOR_DIM;
      ctx.beginPath();
      ctx.arc(x, y, b > 0.01 ? DOT_R * (1 + b) : DOT_R * 0.6, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.globalAlpha = 1;
  }

  resize();
  window.addEventListener('resize', resize, { passive: true });
  requestAnimationFrame(loop);
})();

// ── Scroll reveal ─────────────────────────────
(function () {
  const els = document.querySelectorAll('.section, .project-card, .contact-layout');
  if (!els.length) return;

  els.forEach(el => el.classList.add('reveal'));

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        // Stagger cards
        const cards = e.target.querySelectorAll('.project-card');
        if (cards.length) {
          cards.forEach((c, idx) => {
            c.style.transitionDelay = `${idx * 0.08}s`;
          });
        }
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });

  els.forEach(el => io.observe(el));
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

// ── Smooth external links ─────────────────────
document.querySelectorAll('a[href^="http"]').forEach(a => {
  a.setAttribute('target', '_blank');
  a.setAttribute('rel', 'noopener noreferrer');
});

// ── Console signature ─────────────────────────
const S = [
  ['%c /jw ', 'background:#00c8ff;color:#080b0f;font-family:monospace;font-weight:bold;font-size:13px;padding:2px 4px;border-radius:3px'],
  ['%c NoisyDream18.github.io ', 'color:#3d5468;font-family:monospace;font-size:11px;'],
  ['%c built with vanilla html/css/js ', 'color:#3d5468;font-family:monospace;font-size:11px;'],
];
S.forEach(([msg, style]) => console.log(msg, style));
