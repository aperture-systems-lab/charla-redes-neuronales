const quieto = matchMedia("(prefers-reduced-motion: reduce)").matches;

const lienzo = document.getElementById("lluvia");

if (lienzo && !quieto) {
  const ctx = lienzo.getContext("2d");
  const CARACTERES = "01<>{}[]()/\\=;:#$+*!?abcdef01".split("");
  const TAM = 15;

  let gotas = [];

  function redimensionar() {
    lienzo.width = window.innerWidth;
    lienzo.height = window.innerHeight;

    const columnas = Math.floor(lienzo.width / TAM);

    gotas = Array.from({ length: columnas }, () => Math.floor(Math.random() * -40));
  }

  function dibujar() {

    ctx.fillStyle = "rgba(5, 10, 14, .09)";
    ctx.fillRect(0, 0, lienzo.width, lienzo.height);
    ctx.font = `${TAM}px monospace`;

    gotas.forEach((y, i) => {
      const caracter = CARACTERES[Math.floor(Math.random() * CARACTERES.length)];
      ctx.fillStyle = Math.random() < 0.025 ? "#cfe8ec" : "#1f8fa0";
      ctx.fillText(caracter, i * TAM, y * TAM);

      gotas[i] = y * TAM > lienzo.height && Math.random() > 0.972 ? 0 : y + 1;
    });

    requestAnimationFrame(dibujar);
  }

  redimensionar();
  window.addEventListener("resize", redimensionar);
  dibujar();
}

function montarMalla(malla) {
  const ctx = malla.getContext("2d");
  const ALCANCE = Number(malla.dataset.alcance) || 165;
  const DENSIDAD = Number(malla.dataset.densidad) || 17000;

  let nodos = [];
  let ancho = 0;
  let alto = 0;

  function medir() {
    const caja = malla.getBoundingClientRect();
    if (!caja.width || !caja.height) return false;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    ancho = caja.width;
    alto = caja.height;

    malla.width = Math.round(ancho * dpr);
    malla.height = Math.round(alto * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return true;
  }

  function sembrar() {
    const cuantos = Math.round((ancho * alto) / DENSIDAD);

    nodos = Array.from({ length: cuantos }, () => ({
      x: Math.random() * ancho,
      y: Math.random() * alto,
      vx: (Math.random() - 0.5) * 0.22,
      vy: (Math.random() - 0.5) * 0.22,
      r: Math.random() < 0.22 ? 4.2 : 2.6,
    }));
  }

  function rehacer() {
    if (medir()) sembrar();
  }

  function dibujar() {

    if (!ancho || !alto) rehacer();

    ctx.clearRect(0, 0, ancho, alto);

    for (let i = 0; i < nodos.length; i++) {
      for (let j = i + 1; j < nodos.length; j++) {
        const dx = nodos[i].x - nodos[j].x;
        const dy = nodos[i].y - nodos[j].y;
        const d = Math.hypot(dx, dy);
        if (d > ALCANCE) continue;

        ctx.strokeStyle = `rgba(41, 197, 214, ${(1 - d / ALCANCE) * 0.42})`;
        ctx.lineWidth = 3.2;
        ctx.beginPath();
        ctx.moveTo(nodos[i].x, nodos[i].y);
        ctx.lineTo(nodos[j].x, nodos[j].y);
        ctx.stroke();
      }
    }

    for (const nodo of nodos) {
      ctx.fillStyle = "rgba(41, 197, 214, .72)";
      ctx.beginPath();
      ctx.arc(nodo.x, nodo.y, nodo.r, 0, Math.PI * 2);
      ctx.fill();

      nodo.x += nodo.vx;
      nodo.y += nodo.vy;
      if (nodo.x < 0 || nodo.x > ancho) nodo.vx *= -1;
      if (nodo.y < 0 || nodo.y > alto) nodo.vy *= -1;
    }

    requestAnimationFrame(dibujar);
  }

  rehacer();
  window.addEventListener("resize", rehacer);

  new ResizeObserver(rehacer).observe(malla.parentElement);
  dibujar();
}

if (!quieto) {
  for (const malla of document.querySelectorAll("canvas.malla")) montarMalla(malla);
}
