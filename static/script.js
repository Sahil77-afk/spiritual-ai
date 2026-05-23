/**
 * Spiritual AI — Global Scripts
 * Handles: preloader, particle canvas, BGM, active nav, Lottie loading animation.
 */

// ── Particle Background ───────────────────────────────────────────────────────
(function initParticles() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, pts = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function init() {
    pts = [];
    const count = Math.floor((W * H) / 22000);
    for (let i = 0; i < count; i++) {
      pts.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.2 + 0.2,
        a: Math.random() * Math.PI * 2,
        s: Math.random() * 0.12 + 0.04,
        d: (Math.random() - 0.5) * 0.07,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    pts.forEach(p => {
      p.y -= p.s;
      p.x += p.d;
      p.a += 0.004;
      if (p.y < -5) { p.y = H + 5; p.x = Math.random() * W; }
      const alpha = (Math.sin(p.a) * 0.5 + 0.5) * 0.4 + 0.08;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(212,168,83,${alpha})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }

  resize(); init(); draw();
  window.addEventListener('resize', () => { resize(); init(); });
}());

// ── Preloader ─────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  const pre = document.getElementById('preloader');
  if (!pre) return;
  pre.style.opacity = '0';
  setTimeout(() => { pre.style.display = 'none'; }, 700);
});

// ── Background Music ──────────────────────────────────────────────────────────
(function initBGM() {
  const bgm = document.getElementById('bgm');
  const btn = document.getElementById('audioBtn');
  if (!bgm || !btn) return;

  let playing = false;

  function setPlaying(on) {
    playing = on;
    btn.innerHTML = on
      ? '<i class="fas fa-pause"></i>'
      : '<i class="fas fa-music"></i>';
    btn.style.opacity = on ? '1' : '0.5';
  }

  btn.addEventListener('click', () => {
    if (playing) { bgm.pause(); setPlaying(false); }
    else         { bgm.play().catch(() => {}); setPlaying(true); }
  });

  // Auto-play on first user interaction anywhere on the page
  document.addEventListener('click', function autoPlay(e) {
    if (e.target.closest('#audioBtn')) return;
    bgm.play()
      .then(() => setPlaying(true))
      .catch(() => {});
    document.removeEventListener('click', autoPlay);
  }, { once: true });
}());

// ── Active Nav Link ───────────────────────────────────────────────────────────
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.href === window.location.href) {
    link.classList.add('active-page');
  }
});

// ── Lottie Loading Animation ──────────────────────────────────────────────────
(function initLottie() {
  const container = document.getElementById('loading');
  if (!container || typeof bodymovin === 'undefined') return;
  bodymovin.loadAnimation({
    container,
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: 'https://assets10.lottiefiles.com/packages/lf20_poqmycwy.json',
  });
}());
