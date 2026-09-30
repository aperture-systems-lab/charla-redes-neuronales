import { FORMAS, generar } from "./fronteras-datos.js?v=1";
import { Red, Arbol } from "./fronteras-modelos.js?v=1";
import { pestanaActual } from "./pestanas.js?v=1";
import { colorCss, hexARgb } from "./api.js?v=1";

const SVG = "http://www.w3.org/2000/svg";
const RES = 96;
const PUNTOS = 200;
const RUIDO = 0.04;
const MAX_EPOCAS = 2000;
const FONDO = [4, 8, 12];
const COLORES = ["--clase-0", "--clase-1"].map((v) => colorCss(v));
const RGB = COLORES.map((c) => hexARgb(c));

const MODELOS = {
  logistica: {
    comando: "regresion_logistica",
    nota: "una red <b>sin capas ocultas</b>: una sola recta separa las dos clases.",
    metricas: ["acierto", "pérdida", "época"],
  },
  arbol: {
    comando: "arbol_de_decision",
    nota: "preguntas <b>sí / no</b> sobre x o y: solo cortes rectos, en escalera.",
    metricas: ["acierto", "hojas", "profundidad"],
  },
  red: {
    comando: "red_neuronal",
    nota: "capas de neuronas que <b>doblan el espacio</b>: fronteras curvas.",
    metricas: ["acierto", "pérdida", "época"],
  },
};

const $ = (sel) => document.querySelector(sel);

let forma = "espiral";
let puntos = [];
let actual = "red";
let entrenando = true;
let visible = pestanaActual() === "fronteras";
let hayCambios = true;
let regionSucia = true;

const ARQUITECTURA = { capas: 2, neuronas: 8, activacion: "tanh" };
const PROFUNDIDAD_ARBOL = 5;

let logistica;
let red;
const arbol = new Arbol(PROFUNDIDAD_ARBOL);

// Cada modelo responde p(clase B) en el punto (x, y).
const predecir = {
  logistica: (x, y) => logistica.predecir(x, y)[1],
  arbol: (x, y) => arbol.predecir(x, y)[1],
  red: (x, y) => red.predecir(x, y)[1],
};

// ── el plano ──

const lienzo = $("#fPlano");
const ctx = lienzo.getContext("2d");
const lejos = document.createElement("canvas");
lejos.width = lejos.height = RES;
const lejosCtx = lejos.getContext("2d");
const imagen = new ImageData(RES, RES);
const clases = new Uint8Array(RES * RES);

new ResizeObserver(() => {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  lienzo.width = Math.round(lienzo.clientWidth * dpr);
  lienzo.height = Math.round(lienzo.clientHeight * dpr);
  hayCambios = true;
}).observe(lienzo);

function pintarRegion() {
  const datos = imagen.data;
  const f = predecir[actual];

  for (let j = 0; j < RES; j++) {
    const y = 1 - ((j + 0.5) / RES) * 2;
    for (let i = 0; i < RES; i++) {
      const x = ((i + 0.5) / RES) * 2 - 1;
      const p = f(x, y);
      const celda = j * RES + i;

      // Más intenso cuanto más seguro: nada en p = 0.5 (la frontera), todo en 0 o en 1.
      const k = p > 0.5 ? 1 : 0;
      const alfa = 0.1 + 0.42 * Math.abs(2 * p - 1);
      clases[celda] = k;

      const o = celda * 4;
      for (let c = 0; c < 3; c++) datos[o + c] = FONDO[c] + (RGB[k][c] - FONDO[c]) * alfa;
      datos[o + 3] = 255;
    }
  }

  // La frontera: celdas cuyo vecino de la derecha o de abajo cae en otra clase.
  for (let j = 0; j < RES; j++) {
    for (let i = 0; i < RES; i++) {
      const celda = j * RES + i;
      const k = clases[celda];
      const derecha = i + 1 < RES && clases[celda + 1] !== k;
      const abajo = j + 1 < RES && clases[celda + RES] !== k;
      if (!derecha && !abajo) continue;

      const o = celda * 4;
      for (let c = 0; c < 3; c++) datos[o + c] = FONDO[c] + (RGB[k][c] - FONDO[c]) * 0.85;
    }
  }

  lejosCtx.putImageData(imagen, 0, 0);
}

// Clase A: círculo. Clase B: cuadrado. Así se distinguen también sin color.
function forma2d(clase, px, py, r) {
  ctx.beginPath();
  if (clase === 0) ctx.arc(px, py, r, 0, Math.PI * 2);
  else ctx.rect(px - r * 0.9, py - r * 0.9, r * 1.8, r * 1.8);
}

function dibujar() {
  const w = lienzo.width;
  const h = lienzo.height;
  if (!w || !h) return;

  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(lejos, 0, 0, w, h);

  ctx.strokeStyle = "rgba(31,111,124,.4)";
  ctx.lineWidth = Math.max(1, w / 500);
  ctx.beginPath();
  ctx.moveTo(w / 2, 0);
  ctx.lineTo(w / 2, h);
  ctx.moveTo(0, h / 2);
  ctx.lineTo(w, h / 2);
  ctx.stroke();

  const r = w / 110;
  ctx.lineWidth = r * 0.35;
  ctx.strokeStyle = "#04080c";

  for (const p of puntos) {
    forma2d(p.clase, ((p.x + 1) / 2) * w, ((1 - p.y) / 2) * h, r);
    ctx.fillStyle = COLORES[p.clase];
    ctx.fill();
    ctx.stroke();
  }
}

// ── métricas ──

const porciento = (v) => (Number.isFinite(v) ? `${Math.round(v * 100)}%` : "—");
const decimal = (v) => (Number.isFinite(v) ? v.toFixed(3) : "—");

function poner(el, valor) {
  if (el.textContent !== valor) el.textContent = valor;
}

function actualizarMetricas() {
  const modelos = { logistica, arbol, red };
  for (const boton of document.querySelectorAll("[data-modelo]")) {
    poner(boton.querySelector(".acierto"), porciento(modelos[boton.dataset.modelo].acierto));
  }

  const valores =
    actual === "arbol"
      ? [porciento(arbol.acierto), String(arbol.hojas), String(arbol.profundidad)]
      : (({ acierto, perdida, epoca }) => [porciento(acierto), decimal(perdida), String(epoca)])(
          actual === "red" ? red : logistica
        );

  valores.forEach((v, i) => poner($(`#fValor${i + 1}`), v));
}

// ── svg ──

function nodo(nombre, atributos, texto) {
  const el = document.createElementNS(SVG, nombre);
  for (const [clave, valor] of Object.entries(atributos)) el.setAttribute(clave, String(valor));
  if (texto != null) el.textContent = texto;
  return el;
}

// ── estado ──

function elegirModelo(clave) {
  actual = clave;
  const info = MODELOS[clave];

  for (const boton of document.querySelectorAll("[data-modelo]")) {
    boton.setAttribute("aria-pressed", String(boton.dataset.modelo === clave));
  }
  for (const bloque of document.querySelectorAll("[data-controles]")) {
    bloque.hidden = bloque.dataset.controles !== clave;
  }
  info.metricas.forEach((texto, i) => poner($(`#fEtiqueta${i + 1}`), texto));
  $("#fModeloActual").textContent = info.comando;
  $("#fNota").innerHTML = info.nota;

  regionSucia = hayCambios = true;
  actualizarMetricas();
}

function crearRedes() {
  logistica = new Red([2, 1], "tanh", 0.05);
  const { capas, neuronas, activacion } = ARQUITECTURA;
  red = new Red([2, ...Array(capas).fill(neuronas), 1], activacion, 0.03);

  poner($('[data-m="parametros-logistica"]'), String(logistica.parametros));
  poner($('[data-m="parametros-red"]'), String(red.parametros));
  poner($('[data-m="capas"]'), String(capas));
  poner($('[data-m="neuronas"]'), String(neuronas));
  poner($('[data-m="activacion"]'), activacion);

  regionSucia = hayCambios = true;
}

function ajustarArbol() {
  arbol.ajustar(puntos, 2);
  regionSucia = hayCambios = true;
  actualizarMetricas();
}

function nuevosPuntos() {
  puntos = generar(forma, PUNTOS, RUIDO);
  $("#fFormaActual").textContent = FORMAS[forma].nombre;
  crearRedes();
  ajustarArbol();
}

// ── controles ──

function iconoForma(clave) {
  const svg = nodo("svg", { viewBox: "-1.1 -1.1 2.2 2.2", "aria-hidden": "true" });
  for (const p of generar(clave, 42, 0.03)) {
    svg.append(nodo("circle", { cx: p.x, cy: -p.y, r: 0.09, fill: COLORES[p.clase] }));
  }
  return svg;
}

for (const [clave, { nombre }] of Object.entries(FORMAS)) {
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = "chip forma-chip";
  boton.dataset.forma = clave;
  boton.setAttribute("aria-pressed", String(clave === forma));
  boton.append(iconoForma(clave), nombre);

  boton.addEventListener("click", () => {
    forma = clave;
    for (const b of $("#fFormas").children) b.setAttribute("aria-pressed", String(b === boton));
    nuevosPuntos();
  });
  $("#fFormas").append(boton);
}

for (const boton of document.querySelectorAll("[data-modelo]")) {
  boton.addEventListener("click", () => elegirModelo(boton.dataset.modelo));
}

$("#fEntrenar").addEventListener("click", () => {
  entrenando = !entrenando;
  $("#fEntrenar").textContent = entrenando ? "❚❚ pausar" : "▸ entrenar";
  $("#fEntrenar").classList.toggle("primario", entrenando);
});

$("#fReiniciar").addEventListener("click", () => {
  crearRedes();
  actualizarMetricas();
});


// 1, 2 y 3 cambian de modelo, salvo mientras se escribe en un campo.
document.addEventListener("keydown", (ev) => {
  if (!visible || ev.ctrlKey || ev.metaKey || ev.altKey) return;
  if (ev.target.closest?.("input, textarea, select")) return;
  const clave = { 1: "logistica", 2: "arbol", 3: "red" }[ev.key];
  if (clave) elegirModelo(clave);
});

document.addEventListener("pestana", (ev) => {
  visible = ev.detail === "fronteras";
  hayCambios = true;
});

// ── bucle ──

let cuadro = 0;

function bucle() {
  requestAnimationFrame(bucle);
  if (!visible || document.hidden) return;
  cuadro++;

  // Los tres modelos aprenden a la vez (hasta MAX_EPOCAS); solo se dibuja el elegido.
  let entreno = false;
  if (entrenando) {
    for (const [modelo, epocas] of [[logistica, 2], [red, 5]]) {
      const faltan = MAX_EPOCAS - modelo.epoca;
      if (faltan <= 0) continue;
      modelo.entrenar(puntos, Math.min(epocas, faltan));
      entreno = true;
    }
    if (entreno) {
      hayCambios = true;
      if (actual !== "arbol") regionSucia = true;
    }
  }

  const terminado = logistica.epoca >= MAX_EPOCAS && red.epoca >= MAX_EPOCAS;
  poner(
    $("#fEstadoPlano"),
    terminado ? `listo · ${MAX_EPOCAS} épocas` : entrenando ? "entrenando" : "en pausa"
  );

  if (!hayCambios) return;
  hayCambios = false;

  if (regionSucia) {
    pintarRegion();
    regionSucia = false;
  }
  dibujar();

  // Al llegar a MAX_EPOCAS se pinta la última cifra, aunque no toque por el ritmo.
  if (cuadro % 6 === 0 || !entreno || terminado) actualizarMetricas();
}

poner($('[data-m="profundidad-max"]'), String(PROFUNDIDAD_ARBOL));
nuevosPuntos();
elegirModelo(actual);
requestAnimationFrame(bucle);
