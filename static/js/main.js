(function () {
  const root = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.classList.add('js');

  /* ---------- Theme toggle ---------- */
  const themeBtn = document.querySelector('.theme-toggle');
  function paintToggle() {
    const dark = root.getAttribute('data-theme') === 'dark';
    themeBtn.textContent = dark ? '☀' : '☾';
    themeBtn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
  }
  paintToggle();
  themeBtn.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    paintToggle();
  });

  /* ---------- Mobile menu ---------- */
  const toggle = document.querySelector('.nav-toggle');
  const links = document.getElementById('nav-links');
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });

  /* ---------- Skill bars ---------- */
  const bars = document.querySelectorAll('.bar');
  if (bars.length && 'IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          const i = [...bars].indexOf(e.target);
          e.target.style.transitionDelay = (i % 6) * 0.08 + 's';
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.4 });
    bars.forEach((b) => io.observe(b));
  } else {
    bars.forEach((b) => b.classList.add('in'));
  }

  /* ---------- Scroll reveal ---------- */
  const revealEls = document.querySelectorAll('.page-head, .card, .tile, .project, .timeline li, .chips li, .block > h2');
  if (!reduce && 'IntersectionObserver' in window) {
    revealEls.forEach((el) => {
      el.classList.add('reveal');
      const sibs = [...el.parentElement.children].filter((c) => c.classList.contains('reveal') || c === el);
      el.style.setProperty('--d', Math.min(sibs.indexOf(el), 5) * 0.08 + 's');
      el.addEventListener('animationend', () => el.classList.add('done'), { once: true });
    });
    const rio = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach((el) => rio.observe(el));
  }

  /* ---------- Typing animation ---------- */
  const typed = document.getElementById('typed');
  if (typed && !reduce) {
    let phrases = [];
    try { phrases = JSON.parse(typed.dataset.phrases); } catch (e) {}
    if (phrases.length) {
      let p = 0, c = phrases[0].length, deleting = true;
      const tick = () => {
        const word = phrases[p];
        if (deleting) { c--; } else { c++; }
        typed.textContent = word.slice(0, c);
        let delay = deleting ? 45 : 90;
        if (!deleting && c === word.length) { deleting = true; delay = 1600; }
        else if (deleting && c === 0) { deleting = false; p = (p + 1) % phrases.length; delay = 350; }
        setTimeout(tick, delay);
      };
      setTimeout(tick, 1800);
    }
  }

  /* ---------- Floating hearts and sparkles ---------- */
  const cv = document.getElementById('particles');
  if (cv && !reduce) {
    const ctx = cv.getContext('2d');
    let W, H, dpr, parts = [];
    const heart = (x, y, s) => {
      ctx.beginPath();
      ctx.moveTo(x, y + s * 0.3);
      ctx.bezierCurveTo(x, y - s * 0.1, x - s * 0.6, y - s * 0.1, x - s * 0.6, y + s * 0.3);
      ctx.bezierCurveTo(x - s * 0.6, y + s * 0.65, x, y + s * 0.8, x, y + s);
      ctx.bezierCurveTo(x, y + s * 0.8, x + s * 0.6, y + s * 0.65, x + s * 0.6, y + s * 0.3);
      ctx.bezierCurveTo(x + s * 0.6, y - s * 0.1, x, y - s * 0.1, x, y + s * 0.3);
      ctx.fill();
    };
    const spark = (x, y, s) => {
      ctx.beginPath();
      ctx.moveTo(x, y - s);
      ctx.quadraticCurveTo(x, y, x + s, y);
      ctx.quadraticCurveTo(x, y, x, y + s);
      ctx.quadraticCurveTo(x, y, x - s, y);
      ctx.quadraticCurveTo(x, y, x, y - s);
      ctx.fill();
    };
    const make = (anywhere) => ({
      x: Math.random() * W,
      y: anywhere ? Math.random() * H : H + 20,
      s: 6 + Math.random() * 10,
      v: 0.2 + Math.random() * 0.45,
      sway: Math.random() * Math.PI * 2,
      type: Math.random() < 0.55 ? 'heart' : 'spark',
      t: Math.random() * Math.PI * 2,
    });
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth; H = window.innerHeight;
      cv.width = W * dpr; cv.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.round(Math.min(34, Math.max(14, W / 45)));
      parts = Array.from({ length: n }, () => make(true));
    };
    const frame = () => {
      if (!document.hidden) {
        ctx.clearRect(0, 0, W, H);
        const color = getComputedStyle(root).getPropertyValue('--bubble').trim() || '#FFA9CD';
        ctx.fillStyle = color;
        parts.forEach((p, i) => {
          p.y -= p.v; p.sway += 0.01; p.t += 0.03;
          const x = p.x + Math.sin(p.sway) * 18;
          ctx.globalAlpha = 0.35 + 0.25 * Math.sin(p.t);
          (p.type === 'heart' ? heart : spark)(x, p.y, p.s);
          if (p.y < -30) parts[i] = make(false);
        });
        ctx.globalAlpha = 1;
      }
      requestAnimationFrame(frame);
    };
    window.addEventListener('resize', resize);
    resize();
    frame();
  }

  /* ---------- Custom cursor + sparkle trail ---------- */
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    const dot = document.createElement('div'); dot.className = 'cursor-dot';
    const ring = document.createElement('div'); ring.className = 'cursor-ring';
    document.body.append(ring, dot);
    root.classList.add('has-cursor');

    let mx = 0, my = 0, rx = 0, ry = 0, scale = 1, target = 1, lastX = 0, lastY = 0;
    const symbols = ['♡', '✦', '✧', '♥'];

    window.addEventListener('mousemove', (e) => {
      mx = e.clientX; my = e.clientY;
      if (!root.classList.contains('cursor-on')) { rx = mx; ry = my; root.classList.add('cursor-on'); }
      dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;
      target = e.target.closest && e.target.closest('a, button, [role=tab], label, input, textarea, .tile') ? 1.7 : 1;
      if (!reduce && Math.hypot(mx - lastX, my - lastY) > 30) {
        lastX = mx; lastY = my;
        const s = document.createElement('span');
        s.className = 'trail';
        s.textContent = symbols[Math.floor(Math.random() * symbols.length)];
        s.style.left = mx + 'px'; s.style.top = my + 'px';
        s.style.setProperty('--dx', (Math.random() * 30 - 15) + 'px');
        s.style.fontSize = (11 + Math.random() * 9) + 'px';
        document.body.appendChild(s);
        s.addEventListener('animationend', () => s.remove());
      }
    });
    document.addEventListener('mouseleave', () => root.classList.remove('cursor-on'));
    document.addEventListener('mouseenter', () => root.classList.add('cursor-on'));

    const follow = () => {
      rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18; scale += (target - scale) * 0.2;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%) scale(${scale})`;
      requestAnimationFrame(follow);
    };
    follow();
  }
})();
