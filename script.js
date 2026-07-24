/* =========================================================
   Shared site chrome — runs on every page.
   The hero flight sim lives in hero-jet.js and is pulled in
   only where its canvas exists.
   ========================================================= */

/* =========================================================
   Boot sequence
   ========================================================= */
const boot = document.getElementById('boot');
if (boot) {
  window.addEventListener('load', () => {
    setTimeout(() => boot.classList.add('is-done'), 1400);
  });
}

/* =========================================================
   Clock (UTC ticker in the nav)
   ========================================================= */
const pad = (n) => String(n).padStart(2, '0');
const clockEl = document.getElementById('clock');
if (clockEl) {
  const tickClock = () => {
    const d = new Date();
    clockEl.textContent = `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())} UTC`;
  };
  setInterval(tickClock, 1000);
  tickClock();
}

const tbDate = document.getElementById('tbDate');
if (tbDate) {
  const d = new Date();
  tbDate.textContent = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/* =========================================================
   Custom cursor (crosshair) with live coordinate readout
   ========================================================= */
const cursor = document.getElementById('cursor');
const cursorLabel = document.getElementById('cursorLabel');
if (cursor && cursorLabel) {
  let mx = window.innerWidth / 2, my = window.innerHeight / 2;
  let cx = mx, cy = my;

  window.addEventListener('pointermove', (e) => {
    mx = e.clientX;
    my = e.clientY;
  });

  const animateCursor = () => {
    cx += (mx - cx) * 0.35;
    cy += (my - cy) * 0.35;
    cursor.style.transform = `translate3d(${cx}px, ${cy}px, 0) translate(-50%, -50%)`;
    cursorLabel.textContent = `X: ${String(Math.round(cx)).padStart(3, '0')}  Y: ${String(Math.round(cy)).padStart(3, '0')}`;
    requestAnimationFrame(animateCursor);
  };
  animateCursor();

  document.querySelectorAll('a, button, .card, .contact__card, .btn, .skills__grid li, .shot, .spec')
    .forEach((el) => {
      el.addEventListener('mouseenter', () => cursor.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('is-hover'));
    });
}

/* =========================================================
   Scroll reveal
   ========================================================= */
const revealTargets = document.querySelectorAll(
  '.work__intro, .about, .skills, .contact, .divider, ' +
  '.phase, .proj__intro, .arch, .stack, .cadblock, .nextnav'
);
revealTargets.forEach((el) => el.classList.add('reveal'));
const io = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-in');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
revealTargets.forEach((el) => io.observe(el));

/* =========================================================
   Nav link smooth scroll (light polish)
   ========================================================= */
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    const id = link.getAttribute('href');
    if (id.length > 1) {
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  });
});

/* =========================================================
   Hero flight sim — only pages with the stage pay for three.js
   ========================================================= */
if (document.getElementById('gear') && document.getElementById('stage')) {
  // Carry this file's ?v= through so the sim can't be served from a stale cache
  // while the rest of the page is fresh.
  const version = new URL(import.meta.url).search;
  import(`./hero-jet.js${version}`);
}
