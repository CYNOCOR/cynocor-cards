(function initCynocorPreloader() {
  if (typeof window === 'undefined' || !document.body) return;

  if (!window.__splash) return;

  // Dark theme temporarily locked to light atmosphere
  document.body.classList.remove('atmosphere-dark');
  const isDark = false;

  const overlay = document.createElement('div');
  overlay.className = 'cyno-loader' + (isDark ? ' is-dark' : '');
  overlay.id = 'cynoPreloader';
  overlay.setAttribute('role', 'status');
  overlay.setAttribute('aria-label', 'Loading Cynocor');
  overlay.innerHTML = `
    <div class="cyno-loader-graphics" aria-hidden="true">
      <div class="cyno-loader-ring cyno-loader-ring--outer"></div>
      <div class="cyno-loader-ring cyno-loader-ring--inner"></div>
      <div class="cyno-loader-crosshair"></div>
      <span class="cyno-loader-node n1"></span>
      <span class="cyno-loader-node n2"></span>
      <span class="cyno-loader-node n3"></span>
      <span class="cyno-loader-node n4"></span>
      <span class="cyno-loader-node n5"></span>
      <span class="cyno-loader-node n6"></span>
    </div>
    <div class="cyno-loader-bg-word" aria-hidden="true">CYNOCOR</div>
    <canvas class="cyno-loader-canvas" id="cynoLoaderCanvas" aria-hidden="true"></canvas>
    <div class="cyno-loader-scanlines" aria-hidden="true"></div>
    <div class="cyno-loader-center">
      <div class="cyno-loader-tagline">
        <span class="cyno-loader-word">we</span>
        <span class="cyno-loader-word">create</span>
        <span class="cyno-loader-word cyno-loader-word--accent">future.</span>
      </div>
    </div>
    <div class="cyno-loader-hint" aria-hidden="true">Tap to skip</div>
    <div class="cyno-loader-bar" id="cynoLoaderBar"></div>
  `;

  document.body.appendChild(overlay);
  overlay.addEventListener('click', function () { finishPreloader(); });
  const prevOverflow = document.body.style.overflow;
  document.body.style.overflow = 'hidden';

  const canvas = document.getElementById('cynoLoaderCanvas');
  const barEl = document.getElementById('cynoLoaderBar');
  const ctx = canvas ? canvas.getContext('2d') : null;

  let closed = false;
  let rafId = 0;

  const finishPreloader = () => {
    if (closed) return;
    closed = true;
    if (barEl) barEl.style.width = '100%';
    document.documentElement.classList.remove('has-splash');
    overlay.classList.add('is-leaving');
    document.body.style.overflow = prevOverflow;
    setTimeout(() => {
      if (rafId) cancelAnimationFrame(rafId);
      overlay.remove();
    }, 1000);
  };

  // Procedural 3D Nerve-Filament Human Holographic Scene
  if (ctx && canvas) {
    let seed = 4219;
    const rand = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };

    // Anatomical 3D capsules: [x1, y1, z1, r1, x2, y2, z2, r2, strandCount]
    const capsules = [
      // Head & cranium
      [0.14, -0.35, -0.02, 0.082, 0.14, -0.22, 0.0, 0.07, 46],
      // Neck
      [0.13, -0.21, 0.0, 0.042, 0.12, -0.12, 0.0, 0.055, 20],
      // Upper torso & shoulders
      [0.12, -0.11, 0.0, 0.145, 0.12, 0.18, -0.02, 0.115, 72],
      // Lower torso
      [0.12, 0.16, -0.02, 0.115, 0.13, 0.46, -0.03, 0.125, 48],
      // Right shoulder -> arm extending down-right
      [0.24, -0.06, -0.01, 0.058, 0.34, 0.22, 0.04, 0.046, 28],
      [0.34, 0.22, 0.04, 0.044, 0.43, 0.46, 0.08, 0.036, 22],
      // Left shoulder -> reaching forearm toward viewer
      [0.01, -0.06, 0.02, 0.058, -0.08, -0.08, 0.32, 0.052, 34],
      [-0.08, -0.08, 0.32, 0.052, -0.15, -0.13, 0.56, 0.056, 38],
      // Reaching Palm
      [-0.15, -0.13, 0.56, 0.064, -0.19, -0.19, 0.63, 0.058, 34],
      // Thumb (reaching right-up)
      [-0.12, -0.14, 0.58, 0.024, -0.05, -0.23, 0.67, 0.017, 16],
      // Index finger (iconic tall reach)
      [-0.17, -0.21, 0.62, 0.021, -0.25, -0.42, 0.72, 0.013, 22],
      // Middle finger
      [-0.20, -0.20, 0.61, 0.021, -0.29, -0.34, 0.67, 0.013, 20],
      // Ring finger
      [-0.21, -0.17, 0.59, 0.019, -0.29, -0.24, 0.61, 0.012, 16],
      // Pinky finger
      [-0.21, -0.14, 0.57, 0.017, -0.27, -0.15, 0.56, 0.011, 14]
    ];

    const strands = [];
    capsules.forEach((cap) => {
      const [x1, y1, z1, r1, x2, y2, z2, r2, count] = cap;
      for (let i = 0; i < count; i++) {
        const pts = [];
        const steps = 11;
        const a0 = rand() * Math.PI * 2;
        const twist = (rand() - 0.5) * 3.8;
        const freq = 1.5 + rand() * 3.0;
        const phase = rand() * Math.PI * 2;
        const amp = 0.35 + rand() * 0.85;
        const isAccent = rand() < 0.24;

        for (let s = 0; s <= steps; s++) {
          const t = s / steps;
          const bx = x1 + (x2 - x1) * t;
          const by = y1 + (y2 - y1) * t;
          const bz = z1 + (z2 - z1) * t;
          const r = (r1 + (r2 - r1) * t) * (0.55 + 0.65 * Math.sin(t * Math.PI * 0.9 + phase) * 0.45 + 0.35);
          const ang = a0 + twist * t + Math.sin(t * Math.PI * freq + phase) * amp;
          pts.push({
            x: bx + Math.cos(ang) * r,
            y: by + Math.sin(ang) * r * 0.85,
            z: bz + Math.sin(ang + 1.2) * r
          });
        }

        strands.push({
          pts,
          isAccent,
          width: isAccent ? 0.85 + rand() * 0.75 : 0.45 + rand() * 0.7,
          alpha: isAccent ? 0.55 + rand() * 0.35 : 0.22 + rand() * 0.48,
          revealOrder: rand() * 0.72,
          pulseSpeed: 0.4 + rand() * 0.9,
          pulseOffset: rand()
        });
      }
    });

    const convergeNerves = [];
    for (let i = 0; i < 68; i++) {
      const edge = i % 4; // 0: top, 1: right, 2: bottom, 3: left
      let sx = 0.5;
      let sy = 0.5;
      if (edge === 0) { sx = 0.05 + rand() * 0.9; sy = -0.06; }
      else if (edge === 1) { sx = 1.06; sy = 0.05 + rand() * 0.9; }
      else if (edge === 2) { sx = 0.05 + rand() * 0.9; sy = 1.06; }
      else { sx = -0.06; sy = 0.05 + rand() * 0.9; }

      const targetOffsetX = (rand() - 0.5) * 0.09;
      const targetOffsetY = (rand() - 0.5) * 0.12;
      const bend1 = (rand() - 0.5) * 0.18;
      const bend2 = (rand() - 0.5) * 0.18;
      const isAccent = rand() < 0.36;

      convergeNerves.push({
        sx,
        sy,
        tx: 0.51 + targetOffsetX,
        ty: 0.54 + targetOffsetY,
        bend1,
        bend2,
        delay: rand() * 0.16,
        isAccent,
        width: isAccent ? 1.15 + rand() * 0.75 : 0.6 + rand() * 0.65,
        alpha: isAccent ? 0.65 + rand() * 0.3 : 0.28 + rand() * 0.35
      });
    }

    let width = 0;
    let height = 0;
    let dpr = 1;

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize, { passive: true });

    const startTime = performance.now();
    let pageLoaded = document.readyState === 'complete';
    window.addEventListener('load', () => { pageLoaded = true; }, { once: true });

    const minDuration = 2600;
    let progress = 0;

    const project = (pt, yaw, pitch, scale, cx, cy, tSec) => {
      const wobble = Math.sin(tSec * 1.6 + pt.y * 5.0 + pt.x * 4.0) * 0.0045;
      const x0 = pt.x + wobble;
      const y0 = pt.y + wobble * 0.6;
      const z0 = pt.z;

      const cosY = Math.cos(yaw);
      const sinY = Math.sin(yaw);
      const x1 = x0 * cosY - z0 * sinY;
      const z1 = x0 * sinY + z0 * cosY;

      const cosP = Math.cos(pitch);
      const sinP = Math.sin(pitch);
      const y2 = y0 * cosP - z1 * sinP;
      const z2 = y0 * sinP + z1 * cosP;

      const fov = 1.65;
      const persp = fov / (fov - z2 * 0.72);
      return {
        x: cx + x1 * scale * persp,
        y: cy + y2 * scale * persp,
        z: z2,
        persp
      };
    };

    const render = (now) => {
      if (closed) return;
      const elapsed = now - startTime;
      const tSec = elapsed * 0.001;

      const target = pageLoaded ? Math.min(1, elapsed / minDuration) : Math.min(0.9, elapsed / minDuration);
      progress += (target - progress) * 0.12;
      if (pageLoaded && elapsed >= minDuration && progress > 0.985) {
        progress = 1;
      }

      const pct = Math.min(100, Math.round(progress * 100));
      if (barEl) barEl.style.width = pct + '%';

      ctx.clearRect(0, 0, width, height);

      const scale = Math.min(Math.max(Math.min(width, height) * 1.24, width * 0.56), height * 1.38);
      const cx = width * 0.51;
      const cy = height * 0.56;
      const yaw = Math.sin(tSec * 0.55) * 0.1;
      const pitch = Math.cos(tSec * 0.45) * 0.05;

      const dark = overlay.classList.contains('is-dark');

      // Phase 1 (Inward 0 -> 0.56) & Phase 3 (Outward Dispersion 0.78 -> 1.00)
      if (progress < 0.56) {
        const convergeFade = progress < 0.36 ? 1 : Math.max(0, 1 - (progress - 0.36) / 0.20);
        for (let i = 0; i < convergeNerves.length; i++) {
          const cn = convergeNerves[i];
          const localP = Math.max(0, Math.min(1, (progress - cn.delay) / 0.28));
          if (localP <= 0.01) continue;

          const easeP = 1 - Math.pow(1 - localP, 2.2);
          const x0 = cn.sx * width;
          const y0 = cn.sy * height;
          const x3 = cn.tx * width;
          const y3 = cn.ty * height;
          const dx = x3 - x0;
          const dy = y3 - y0;
          const len = Math.hypot(dx, dy) || 1;
          const nx = -dy / len;
          const ny = dx / len;

          const segs = 14;
          const maxSeg = Math.max(1, Math.floor(segs * easeP));
          ctx.beginPath();
          let tipX = x0;
          let tipY = y0;
          for (let s = 0; s <= maxSeg; s++) {
            const u = (s / segs) * easeP;
            const wave = Math.sin(u * Math.PI * 2.2 + tSec * 2.0 + i) * (1 - u) * Math.min(width, height) * 0.055;
            const px = x0 + dx * u + nx * (cn.bend1 * width * u * (1 - u) + wave);
            const py = y0 + dy * u + ny * (cn.bend2 * height * u * (1 - u) + wave);
            if (s === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
            tipX = px;
            tipY = py;
          }

          const strokeAlpha = cn.alpha * convergeFade * Math.min(1, localP * 2.2);
          ctx.lineWidth = cn.width;
          ctx.strokeStyle = cn.isAccent
            ? (dark ? `rgba(56, 189, 248, ${strokeAlpha.toFixed(3)})` : `rgba(0, 112, 255, ${strokeAlpha.toFixed(3)})`)
            : (dark ? `rgba(215, 232, 255, ${(strokeAlpha * 0.72).toFixed(3)})` : `rgba(15, 23, 42, ${(strokeAlpha * 0.55).toFixed(3)})`);
          ctx.stroke();

          if (cn.isAccent && localP < 0.98) {
            ctx.beginPath();
            ctx.arc(tipX, tipY, 2.4, 0, Math.PI * 2);
            ctx.fillStyle = dark
              ? `rgba(125, 211, 252, ${(0.9 * convergeFade).toFixed(3)})`
              : `rgba(0, 112, 255, ${(0.9 * convergeFade).toFixed(3)})`;
            ctx.fill();
          }
        }

        // Subtle central nexus glow as the 4-way nerves gather
        if (progress > 0.16) {
          const nexusAlpha = Math.sin(Math.min(1, (progress - 0.16) / 0.40) * Math.PI) * 0.28;
          const grad = ctx.createRadialGradient(cx, cy, 4, cx, cy, Math.min(width, height) * 0.22);
          grad.addColorStop(0, dark ? `rgba(56, 189, 248, ${nexusAlpha.toFixed(3)})` : `rgba(0, 112, 255, ${(nexusAlpha * 0.85).toFixed(3)})`);
          grad.addColorStop(1, 'rgba(0, 112, 255, 0)');
          ctx.fillStyle = grad;
          ctx.beginPath();
          ctx.arc(cx, cy, Math.min(width, height) * 0.22, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Phase 3: Disperse outward to all 4 sides when loading finishes
      const disperseP = Math.max(0, Math.min(1, (progress - 0.78) / 0.22));
      if (disperseP > 0.01) {
        const outFade = 1 - Math.pow(disperseP, 1.8);
        for (let i = 0; i < convergeNerves.length; i++) {
          const cn = convergeNerves[i];
          const localOut = Math.max(0, Math.min(1, (disperseP - cn.delay * 0.45) / 0.85));
          if (localOut <= 0.01) continue;

          const easeOut = 1 - Math.pow(1 - localOut, 2.0);
          const x0 = cn.tx * width;
          const y0 = cn.ty * height;
          const x3 = cn.sx * width;
          const y3 = cn.sy * height;
          const dx = x3 - x0;
          const dy = y3 - y0;
          const len = Math.hypot(dx, dy) || 1;
          const nx = -dy / len;
          const ny = dx / len;

          const segs = 14;
          const startU = Math.max(0, easeOut - 0.55);
          ctx.beginPath();
          let tipX = x0;
          let tipY = y0;
          for (let s = 0; s <= segs; s++) {
            const u = startU + (easeOut - startU) * (s / segs);
            const wave = Math.sin(u * Math.PI * 2.2 + tSec * 2.2 + i) * u * Math.min(width, height) * 0.045;
            const px = x0 + dx * u + nx * (cn.bend1 * width * u * (1 - u) + wave);
            const py = y0 + dy * u + ny * (cn.bend2 * height * u * (1 - u) + wave);
            if (s === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
            tipX = px;
            tipY = py;
          }

          const strokeAlpha = cn.alpha * outFade * 1.15;
          ctx.lineWidth = cn.width * 1.08;
          ctx.strokeStyle = cn.isAccent
            ? (dark ? `rgba(56, 189, 248, ${Math.min(1, strokeAlpha).toFixed(3)})` : `rgba(0, 112, 255, ${Math.min(1, strokeAlpha).toFixed(3)})`)
            : (dark ? `rgba(215, 232, 255, ${(strokeAlpha * 0.72).toFixed(3)})` : `rgba(15, 23, 42, ${(strokeAlpha * 0.55).toFixed(3)})`);
          ctx.stroke();

          if (cn.isAccent) {
            ctx.beginPath();
            ctx.arc(tipX, tipY, 2.5, 0, Math.PI * 2);
            ctx.fillStyle = dark
              ? `rgba(125, 211, 252, ${(0.95 * outFade).toFixed(3)})`
              : `rgba(0, 112, 255, ${(0.95 * outFade).toFixed(3)})`;
            ctx.fill();
          }
        }
      }

      // Phase 2: Nerve Human slowly forms in the center, then dissolves into Phase 3 dispersion
      const nerveProgress = Math.max(0, Math.min(1, (progress - 0.24) / 0.46));
      const humanDisperseFade = 1 - Math.pow(disperseP, 1.35);
      const humanScale = scale * (1 + disperseP * 0.16);

      for (let i = 0; i < strands.length; i++) {
        const st = strands[i];
        const drawFrac = Math.max(0, Math.min(1, (nerveProgress * 1.18 - st.revealOrder) / 0.36));
        if (drawFrac <= 0.02 || humanDisperseFade <= 0.01) continue;

        const pts = st.pts;
        const maxIdx = Math.max(2, Math.floor(pts.length * drawFrac));

        ctx.beginPath();
        let avgZ = 0;
        const maxHover = 0;
        const projected = [];
        for (let j = 0; j < maxIdx; j++) {
          const p = project(pts[j], yaw, pitch, humanScale, cx, cy, tSec);
          projected.push(p);
          avgZ += p.z;
        }
        avgZ /= projected.length;

        ctx.moveTo(projected[0].x, projected[0].y);
        for (let j = 1; j < projected.length - 1; j++) {
          const xc = (projected[j].x + projected[j + 1].x) * 0.5;
          const yc = (projected[j].y + projected[j + 1].y) * 0.5;
          ctx.quadraticCurveTo(projected[j].x, projected[j].y, xc, yc);
        }
        const last = projected[projected.length - 1];
        ctx.lineTo(last.x, last.y);

        const depthBoost = Math.max(0.45, Math.min(1.5, 0.88 + avgZ * 0.85));
        ctx.lineWidth = st.width * depthBoost * (1 + maxHover * 0.9);

        if (st.isAccent || maxHover > 0.2) {
          const alphaBoost = Math.min(1, (st.alpha + maxHover * 0.55) * drawFrac * humanDisperseFade);
          ctx.strokeStyle = dark
            ? `rgba(56, 189, 248, ${alphaBoost.toFixed(3)})`
            : `rgba(0, 112, 255, ${(alphaBoost * 0.95).toFixed(3)})`;
        } else {
          ctx.strokeStyle = dark
            ? `rgba(215, 232, 255, ${(st.alpha * 0.74 * drawFrac * humanDisperseFade).toFixed(3)})`
            : `rgba(12, 18, 32, ${(st.alpha * 0.88 * drawFrac * humanDisperseFade).toFixed(3)})`;
        }
        ctx.stroke();

        // Synaptic holographic pulse traveling along accent or hovered nerves
        if ((st.isAccent || maxHover > 0.25) && projected.length > 3) {
          const pulsePos = ((tSec * (st.pulseSpeed + maxHover * 0.8) + st.pulseOffset) % 1) * (projected.length - 1);
          const idx = Math.floor(pulsePos);
          const frac = pulsePos - idx;
          const pA = projected[idx];
          const pB = projected[Math.min(idx + 1, projected.length - 1)];
          const px = pA.x + (pB.x - pA.x) * frac;
          const py = pA.y + (pB.y - pA.y) * frac;

          ctx.beginPath();
          ctx.arc(px, py, (2.0 + maxHover * 1.8) * pA.persp, 0, Math.PI * 2);
          ctx.fillStyle = dark ? 'rgba(125, 211, 252, 0.95)' : 'rgba(0, 112, 255, 0.95)';
          ctx.fill();
        }
      }

      if (progress >= 1) {
        window.removeEventListener('resize', resize);
        setTimeout(finishPreloader, 180);
        return;
      }

      rafId = requestAnimationFrame(render);
    };

    rafId = requestAnimationFrame(render);
    // Safety fallback so preloader never blocks indefinitely
    setTimeout(finishPreloader, 4200);
  } else {
    setTimeout(finishPreloader, 2500);
  }
})();
