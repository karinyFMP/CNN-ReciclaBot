/* ──────────────────────────────────────────────
   ReciclaBot — Apresentação: Scroll animations
   ────────────────────────────────────────────── */

// ── Floating background emojis ──
(function () {
  const items = [
    ["♻️",  4, 22, 0.0,  1.55, 12], ["📄", 16, 28, 3.5,  1.25, -8],
    ["🥫", 31, 19, 1.2,  1.70, 15], ["🍾", 47, 25, 5.8,  1.40, -5],
    ["📦", 62, 21, 2.1,  1.85,-18], ["♻️", 75, 30, 0.7,  1.10, 10],
    ["📄", 88, 17, 4.3,  1.55, -6], ["🥫", 11, 26, 8.0,  1.75,-12],
    ["🍾",  9, 26, 5.0,  1.70, 11], ["📦", 23, 20, 1.9,  1.15, 16],
    ["♻️", 38, 32, 4.0,  1.45, -9], ["📄", 53, 18, 7.2,  1.60,  7],
  ];
  const bg = document.getElementById('waste-bg');
  if (bg) {
    items.forEach(([emoji, left, dur, delay, size, rot]) => {
      const s = document.createElement('span');
      s.textContent = emoji;
      s.style.cssText = `left:${left}vw;font-size:${size}rem;animation-duration:${dur}s;animation-delay:-${delay}s;--rs:${rot}deg;--re:${-rot}deg;`;
      bg.appendChild(s);
    });
  }
})();

// ── Scroll-reveal using IntersectionObserver ──
(function () {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  els.forEach(el => io.observe(el));
})();

// ── FAB: hide when fully at top (hero shows its own CTA) ──
(function () {
  const fab = document.getElementById('fab-test-model');
  if (!fab) return;

  const onScroll = () => {
    const scrolled = window.scrollY > 80;
    fab.style.opacity = scrolled ? '1' : '0';
    fab.style.pointerEvents = scrolled ? 'auto' : 'none';
  };

  // Start hidden until user scrolls
  fab.style.opacity = '0';
  fab.style.pointerEvents = 'none';
  fab.style.transition = 'opacity 0.3s ease';

  window.addEventListener('scroll', onScroll, { passive: true });
})();
