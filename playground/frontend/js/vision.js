import { REDES, RUTAS, SEGMENTOS } from "./vision-datos.js?v=1";
import { pestanaActual } from "./pestanas.js?v=1";
import { colorCss, hexARgb } from "./api.js?v=1";

const MEDIAPIPE = "/cache/mediapipe";
const MODELOS = "/cache/modelos";
const CADA_CLASIFICACION = 250;

const $ = (sel) => document.querySelector(sel);

const lienzo = $("#vLienzo");
const ctx = lienzo.getContext("2d");
const video = document.createElement("video");
video.muted = true;
video.playsInline = true;

let flujo = null;
let visible = pestanaActual() === "vision";
let ultimoTs = 0;
let ultimaClasificacion = 0;
let ultimoPanel = 0;

const estado = Object.fromEntries(
  REDES.map((r) => [r.clave, { activa: false, tarea: null, cargando: null, error: null }])
);

const salidas = { top: [], conteo: null, total: 0 };

// ── mediapipe ──

let vision = null;
let fileset = null;

async function mediapipe() {
  if (!vision) {
    vision = await import(`${MEDIAPIPE}/vision_bundle.mjs`);
    fileset = await vision.FilesetResolver.forVisionTasks(`${MEDIAPIPE}/wasm`);
  }
  return vision;
}

async function crearTarea(nombre, ruta, opciones) {
  const Tarea = (await mediapipe())[nombre];
  const base = { modelAssetPath: `${MODELOS}/${ruta}` };

  try {
    return await Tarea.createFromOptions(fileset, {
      baseOptions: { ...base, delegate: "GPU" },
      runningMode: "VIDEO",
      ...opciones,
    });
  } catch (error) {
    console.warn(`${nombre}: sin GPU, se usa la CPU.`, error);
    return Tarea.createFromOptions(fileset, {
      baseOptions: { ...base, delegate: "CPU" },
      runningMode: "VIDEO",
      ...opciones,
    });
  }
}

const CREAR = {
  manos: () => crearTarea("HandLandmarker", RUTAS.manos, { numHands: 4 }),
  cara: () => crearTarea("FaceLandmarker", RUTAS.cara, { numFaces: 3 }),
  segmentacion: () =>
    crearTarea("ImageSegmenter", RUTAS.segmentacion, {
      outputCategoryMask: true,
      outputConfidenceMasks: false,
    }),
  clasificacion: () => crearTarea("ImageClassifier", RUTAS.clasificacion, { maxResults: 5 }),
};

// ── lista de redes ──

const botones = {};

for (const red of REDES) {
  const li = document.createElement("li");
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = "red-boton";
  boton.setAttribute("aria-pressed", "false");
  boton.style.setProperty("--tono", `var(${red.tono})`);
  boton.innerHTML = `
    <span class="icono" aria-hidden="true">${red.icono}</span>
    <b>${red.nombre}</b>
    <small>${red.detalle}</small>
    <span class="estado">apagada</span>`;

  boton.addEventListener("click", () => alternar(red.clave));
  botones[red.clave] = boton;
  li.append(boton);
  $("#vRedes").append(li);
}

function pintarBoton(clave) {
  const { activa, cargando, error } = estado[clave];
  const boton = botones[clave];

  boton.setAttribute("aria-pressed", String(activa));
  boton.classList.toggle("cargando", Boolean(cargando));
  boton.classList.toggle("fallo", Boolean(error));
  boton.querySelector(".estado").textContent = error
    ? "error"
    : cargando
      ? "cargando…"
      : activa
        ? "activa"
        : "apagada";
  if (error) boton.title = error;
  else boton.removeAttribute("title");
}

async function cargar(clave) {
  const e = estado[clave];
  if (e.tarea || e.cargando) return;

  e.error = null;
  e.cargando = CREAR[clave]();
  pintarBoton(clave);

  try {
    e.tarea = await e.cargando;
  } catch (error) {
    console.error(error);
    e.error = String(error?.message || error);
    e.activa = false;
  } finally {
    e.cargando = null;
    pintarBoton(clave);
    pintarSalidas();
  }
}

// Una red a la vez: al encender una se apagan las demás; tocar la activa la apaga.
function alternar(clave) {
  const encender = !estado[clave].activa;
  for (const red of REDES) estado[red.clave].activa = encender && red.clave === clave;

  if (encender) {
    estado[clave].error = null;
    cargar(clave);
  }
  for (const red of REDES) pintarBoton(red.clave);
  pintarSalidas();
}

// ── cámara ──

// Cada encendido abre una generación nueva: así un cuadro pendiente del flujo anterior
// no arranca un segundo bucle en paralelo.
let generacion = 0;

async function encender(dispositivo) {
  apagar();
  $("#vEncender").disabled = true;
  $("#vEstado").textContent = "pidiendo permiso…";

  try {
    flujo = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        ...(dispositivo ? { deviceId: { exact: dispositivo } } : { facingMode: "user" }),
      },
    });
  } catch (error) {
    $("#vEncender").disabled = false;
    $("#vEstado").textContent = "sin cámara";
    $("#vEstado").className = "cabecera-dato malo";
    const nota = $("#vApagado .escenario-nota");
    nota.textContent =
      error.name === "NotAllowedError"
        ? "el navegador no dio permiso para la cámara. Revísalo en el candado de la barra de direcciones."
        : `no se pudo abrir la cámara: ${error.message}`;
    nota.style.color = "var(--err)";
    return;
  }

  video.srcObject = flujo;
  await video.play();
  lienzo.width = video.videoWidth;
  lienzo.height = video.videoHeight;

  $("#vApagado").hidden = true;
  $("#vEncender").disabled = false;
  $("#vApagar").disabled = false;
  $("#vEstado").textContent = "en vivo";
  $("#vEstado").className = "cabecera-dato bien";

  await listarCamaras(flujo.getVideoTracks()[0]?.getSettings().deviceId);

  if (!REDES.some((r) => estado[r.clave].activa)) alternar("cara");
  generacion++;
  pedirCuadro();
}

function apagar() {
  if (!flujo) return;
  for (const pista of flujo.getTracks()) pista.stop();
  flujo = null;
  video.srcObject = null;

  $("#vApagado").hidden = false;
  $("#vApagar").disabled = true;
  $("#vEstado").textContent = "apagada";
  $("#vEstado").className = "cabecera-dato";
}

async function listarCamaras(actual) {
  const camaras = (await navigator.mediaDevices.enumerateDevices()).filter((d) => d.kind === "videoinput");
  const selector = $("#vCamaras");
  selector.hidden = camaras.length < 2;
  selector.replaceChildren(
    ...camaras.map((c, i) => new Option(c.label || `cámara ${i + 1}`, c.deviceId, false, c.deviceId === actual))
  );
}

// ── dibujo ──

const PALETA = new Uint32Array(256);
SEGMENTOS.colores.forEach((variable, i) => {
  if (!variable) return;
  const [r, g, b] = hexARgb(colorCss(variable));
  PALETA[i] = ((150 << 24) | (b << 16) | (g << 8) | r) >>> 0;
});

const mascara = document.createElement("canvas");
const mascaraCtx = mascara.getContext("2d");
let mascaraImagen = null;

function segmentar(ts, w, h) {
  estado.segmentacion.tarea.segmentForVideo(video, ts, (resultado) => {
    const categorias = resultado.categoryMask;
    if (!categorias) return;

    const { width: mw, height: mh } = categorias;
    if (mascara.width !== mw || mascara.height !== mh) {
      mascara.width = mw;
      mascara.height = mh;
      mascaraImagen = new ImageData(mw, mh);
    }

    const datos = categorias.getAsUint8Array();
    const pixeles = new Uint32Array(mascaraImagen.data.buffer);
    const conteo = new Uint32Array(256);
    for (let i = 0; i < datos.length; i++) {
      const c = datos[i];
      conteo[c]++;
      pixeles[i] = PALETA[c];
    }
    salidas.conteo = conteo;
    salidas.total = datos.length;
    mascaraCtx.putImageData(mascaraImagen, 0, 0);
  });

  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(mascara, 0, 0, w, h);
}

function trazar(marcas, conexiones, w, h) {
  ctx.beginPath();
  for (const { start, end } of conexiones) {
    ctx.moveTo(marcas[start].x * w, marcas[start].y * h);
    ctx.lineTo(marcas[end].x * w, marcas[end].y * h);
  }
  ctx.stroke();
}

function dibujarManos(listas, w, h) {
  const color = colorCss("--ambar");
  const lado = Math.max(3, w / 190);

  for (const marcas of listas) {
    ctx.strokeStyle = color;
    ctx.lineWidth = Math.max(2, w / 260);
    ctx.lineCap = "round";
    ctx.shadowColor = color;
    ctx.shadowBlur = 12;
    trazar(marcas, vision.HandLandmarker.HAND_CONNECTIONS, w, h);

    ctx.shadowBlur = 0;
    ctx.fillStyle = "#eafcff";
    for (const m of marcas) ctx.fillRect(m.x * w - lado / 2, m.y * h - lado / 2, lado, lado);
  }
}

// La malla completa, tenue, y encima los contornos de ojos, cejas, labios y rostro.
function dibujarCaras(listas, w, h) {
  const color = colorCss("--turquesa");
  const { FACE_LANDMARKS_TESSELATION, FACE_LANDMARKS_CONTOURS } = vision.FaceLandmarker;

  for (const marcas of listas) {
    ctx.strokeStyle = color;
    ctx.lineCap = "round";
    ctx.globalAlpha = 0.35;
    ctx.lineWidth = Math.max(1, w / 1300);
    trazar(marcas, FACE_LANDMARKS_TESSELATION, w, h);

    ctx.globalAlpha = 1;
    ctx.lineWidth = Math.max(1.5, w / 480);
    ctx.shadowColor = color;
    ctx.shadowBlur = 10;
    trazar(marcas, FACE_LANDMARKS_CONTOURS, w, h);
    ctx.shadowBlur = 0;
  }
}

// ── bucle ──

function pedirCuadro(gen = generacion) {
  if (!flujo || gen !== generacion) return;
  const siguiente = () => procesar(gen);
  if (video.requestVideoFrameCallback) video.requestVideoFrameCallback(siguiente);
  else requestAnimationFrame(siguiente);
}

function procesar(gen) {
  if (gen !== generacion) return;
  pedirCuadro(gen);
  if (!flujo || !visible || video.readyState < 2) return;

  const w = lienzo.width;
  const h = lienzo.height;
  const t0 = performance.now();
  const ts = (ultimoTs = Math.max(ultimoTs + 1, Math.round(t0)));
  const lista = (clave) => estado[clave].activa && estado[clave].tarea;

  // Todo se dibuja en espejo, como cuando uno se mira.
  ctx.save();
  ctx.translate(w, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, w, h);

  try {
    if (lista("segmentacion")) segmentar(ts, w, h);
    if (lista("cara")) {
      dibujarCaras(estado.cara.tarea.detectForVideo(video, ts).faceLandmarks, w, h);
    }
    if (lista("manos")) {
      dibujarManos(estado.manos.tarea.detectForVideo(video, ts).landmarks, w, h);
    }
  } finally {
    ctx.restore();
  }

  if (lista("clasificacion") && t0 - ultimaClasificacion > CADA_CLASIFICACION) {
    ultimaClasificacion = t0;
    const resultado = estado.clasificacion.tarea.classifyForVideo(video, ts);
    salidas.top = resultado.classifications[0]?.categories ?? [];
  }

  if (t0 - ultimoPanel > 300) {
    ultimoPanel = t0;
    pintarSalidas();
  }
}

// ── panel de salida ──

function mostrar(clave, si) {
  $(`[data-salida="${clave}"]`).hidden = !si;
}

function pintarSalidas() {
  const clasifica = estado.clasificacion.activa;
  mostrar("clasificacion", clasifica);
  if (clasifica) {
    $("#vTop").replaceChildren(
      ...salidas.top.map((c) => {
        const li = document.createElement("li");
        li.style.setProperty("--pct", `${(c.score * 100).toFixed(1)}%`);
        li.style.setProperty("--tono", "var(--azul)");
        const nombre = Object.assign(document.createElement("b"), { textContent: c.categoryName });
        const valor = Object.assign(document.createElement("span"), { textContent: `${(c.score * 100).toFixed(1)}%` });
        li.append(nombre, valor);
        return li;
      })
    );
  }

  const segmenta = estado.segmentacion.activa;
  mostrar("segmentacion", segmenta);
  if (segmenta && salidas.conteo) {
    const { etiquetas, colores } = SEGMENTOS;
    const filas = etiquetas
      .map((nombre, i) => ({ nombre, i, parte: salidas.conteo[i] / salidas.total }))
      .filter((f) => f.i > 0 && f.parte > 0.005)
      .sort((a, b) => b.parte - a.parte)
      .map(({ nombre, i, parte }) => {
        const li = document.createElement("li");
        li.style.setProperty("--c", `var(${colores[i]})`);
        li.innerHTML = `<i></i>${nombre} <em>${Math.round(parte * 100)}%</em>`;
        return li;
      });
    if (!filas.length) filas.push(Object.assign(document.createElement("li"), { innerHTML: "<em>solo fondo</em>" }));
    $("#vLeyenda").replaceChildren(...filas);
  }

  $("#vVacio").hidden = clasifica || segmenta;
}

// ── eventos ──

$("#vEncender").addEventListener("click", () => encender());
$("#vApagar").addEventListener("click", apagar);
$("#vCamaras").addEventListener("change", (ev) => encender(ev.target.value));

document.addEventListener("pestana", (ev) => {
  visible = ev.detail === "vision";
});

for (const red of REDES) pintarBoton(red.clave);
pintarSalidas();
