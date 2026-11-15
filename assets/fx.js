/* 3D tilt + parallax for the card (mouse/pen only; touch devices use a CSS sway instead) */
(function () {
  var wrap = document.querySelector('.cardpage .wrap');
  var card = document.querySelector('.cardpage .card');
  if (!wrap || !card) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var raf = 0, tx = 0, ty = 0;
  function apply() {
    raf = 0;
    wrap.style.setProperty('--ry', (tx * 7).toFixed(2) + 'deg');
    wrap.style.setProperty('--rx', (-ty * 5).toFixed(2) + 'deg');
    wrap.style.setProperty('--px', tx.toFixed(3));
    wrap.style.setProperty('--py', ty.toFixed(3));
    card.style.setProperty('--gx', ((tx + 1) * 50).toFixed(1) + '%');
    card.style.setProperty('--gy', ((ty + 1) * 50).toFixed(1) + '%');
  }
  window.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;
    tx = (e.clientX / innerWidth - 0.5) * 2;
    ty = (e.clientY / innerHeight - 0.5) * 2;
    wrap.classList.add('is-tilting');
    if (!raf) raf = requestAnimationFrame(apply);
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', function () {
    tx = 0; ty = 0; wrap.classList.remove('is-tilting');
    if (!raf) raf = requestAnimationFrame(apply);
  });
})();
