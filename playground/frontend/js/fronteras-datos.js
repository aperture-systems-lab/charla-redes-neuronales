// Todos los puntos viven en el cuadrado [-1, 1] × [-1, 1].

const azar = (a, b) => a + Math.random() * (b - a);

function gauss() {
  const u = 1 - Math.random();
  const v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function lineal(n) {
  const puntos = [];
  while (puntos.length < n) {
    const x = azar(-0.9, 0.9);
    const y = azar(-0.9, 0.9);
    const lado = y - (0.55 * x + 0.05);
    if (Math.abs(lado) < 0.1) continue;
    puntos.push({ x, y, clase: lado > 0 ? 0 : 1 });
  }
  return puntos;
}

function xor(n) {
  const puntos = [];
  while (puntos.length < n) {
    const x = azar(-0.9, 0.9);
    const y = azar(-0.9, 0.9);
    if (Math.abs(x) < 0.08 || Math.abs(y) < 0.08) continue;
    puntos.push({ x, y, clase: x * y > 0 ? 0 : 1 });
  }
  return puntos;
}

function circulo(n) {
  return Array.from({ length: n }, (_, i) => {
    const dentro = i % 2 === 0;
    const r = dentro ? Math.sqrt(Math.random()) * 0.38 : azar(0.62, 0.9);
    const a = azar(0, 2 * Math.PI);
    return { x: r * Math.cos(a), y: r * Math.sin(a), clase: dentro ? 0 : 1 };
  });
}

function lunas(n) {
  return Array.from({ length: n }, (_, i) => {
    const arriba = i % 2 === 0;
    const t = azar(0, Math.PI);
    const x = arriba ? Math.cos(t) : 1 - Math.cos(t);
    const y = arriba ? Math.sin(t) : 0.5 - Math.sin(t);
    return { x: (x - 0.5) * 0.6, y: (y - 0.25) * 0.6 * 1.25, clase: arriba ? 0 : 1 };
  });
}

function espiral(n) {
  const porBrazo = Math.floor(n / 2);
  const puntos = [];
  for (let clase = 0; clase < 2; clase++) {
    for (let i = 0; i < porBrazo; i++) {
      const t = i / porBrazo;
      const r = 0.08 + 0.82 * t;
      const a = t * 1.75 * 2 * Math.PI + clase * Math.PI;
      puntos.push({ x: r * Math.cos(a), y: r * Math.sin(a), clase });
    }
  }
  return puntos;
}

// Todas con dos clases: 0 (A) y 1 (B).
export const FORMAS = {
  lineal: { nombre: "lineal", generar: lineal },
  xor: { nombre: "xor", generar: xor },
  circulo: { nombre: "círculo", generar: circulo },
  lunas: { nombre: "lunas", generar: lunas },
  espiral: { nombre: "espiral", generar: espiral },
};

const recortar = (v) => Math.max(-0.99, Math.min(0.99, v));

export function generar(forma, n, ruido) {
  return FORMAS[forma].generar(n).map((p) => ({
    x: recortar(p.x + gauss() * ruido),
    y: recortar(p.y + gauss() * ruido),
    clase: p.clase,
  }));
}
