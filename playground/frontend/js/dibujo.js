import { pedir, piezaVisible, estadoServidor } from "./api.js?v=1";

const EJEMPLOS = [
  "dibuja un gato astronauta",
  "dibuja el sistema solar",
  "dibuja una ciudad de noche",
  "dibuja una red neuronal",
  "dibuja un pez en una pecera",
];

const $ = (sel) => document.querySelector(sel);
const entrada = $("#dPedido");
const marco = $("#dMarco");
const codigo = $("#dCodigo");
const meta = $("#dMeta");
const formato = new Intl.NumberFormat("es-CO");

let ocupado = false;

// Gemini a veces envuelve el HTML en ```html … ```: nos quedamos solo con el documento.
function extraerHtml(texto) {
  const limpio = texto.replace(/^\s*```(?:html)?\s*/i, "").replace(/```\s*$/, "");
  const desde = limpio.search(/<!doctype html|<html/i);
  if (desde < 0) return limpio.includes("<") ? limpio : null;
  const hasta = limpio.toLowerCase().lastIndexOf("</html>");
  return hasta > desde ? limpio.slice(desde, hasta + 7) : limpio.slice(desde);
}

// El código de Gemini ya corre en un iframe aislado (sandbox); además, esta política le
// prohíbe conectarse a cualquier sitio o cargar nada de fuera: solo puede dibujar.
const POLITICA =
  '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; ' +
  "script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:\">";

function blindar(html) {
  const cabeza = html.match(/<head[^>]*>/i);
  if (!cabeza) return POLITICA + html;
  const fin = cabeza.index + cabeza[0].length;
  return html.slice(0, fin) + POLITICA + html.slice(fin);
}

async function leerLineas(respuesta, alLeer) {
  const lector = respuesta.body.pipeThrough(new TextDecoderStream()).getReader();
  let resto = "";
  for (;;) {
    const { value, done } = await lector.read();
    if (done) break;
    resto += value;
    const lineas = resto.split("\n");
    resto = lineas.pop();
    for (const linea of lineas) if (linea.trim()) alLeer(JSON.parse(linea));
  }
  if (resto.trim()) alLeer(JSON.parse(resto));
}

function avisar(texto, error = false) {
  meta.textContent = texto;
  meta.classList.toggle("error", error);
}

function mostrarCodigo(si) {
  codigo.hidden = !si;
  $("#dVerCodigo").textContent = si ? "ver el dibujo" : "ver el código";
}

// ── tu mensaje, partido en tokens ──

async function mostrarTokens(texto) {
  $("#dMensaje").hidden = false;
  $("#dCuenta").textContent = "…";
  $("#dTokens").replaceChildren();

  try {
    const { tokens } = await pedir("/api/tokens", { texto });
    $("#dTokens").replaceChildren(
      ...tokens.map(({ id, texto: pieza, bytes }) => {
        const tok = document.createElement("span");
        tok.className = bytes ? "tok bytes" : "tok";
        tok.title = `token nº ${formato.format(id)}`;
        tok.append(piezaVisible(pieza));
        return tok;
      })
    );
    $("#dCuenta").textContent = `${tokens.length} tokens`;
  } catch (error) {
    $("#dCuenta").textContent = error.message;
  }
}

// ── el dibujo, escribiéndose ──

async function dibujar(texto) {
  texto = texto.trim();
  if (ocupado || !texto) return;

  ocupado = true;
  entrada.disabled = true;
  $("#dDibujar").disabled = true;
  $("#dDibujar").textContent = "… dibujando";
  $("#dVerCodigo").disabled = true;
  for (const b of $("#dEjemplos").children) b.disabled = true;

  const tokens = mostrarTokens(texto);
  marco.srcdoc = "";
  codigo.textContent = "";
  codigo.classList.add("escribiendo");
  mostrarCodigo(true);
  avisar("pensando…");

  const t0 = performance.now();
  const segundos = () => ((performance.now() - t0) / 1000).toFixed(1);
  let escrito = "";
  let fin = null;

  try {
    let respuesta;
    try {
      respuesta = await fetch("/api/dibujar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pedido: texto }),
      });
    } catch {
      throw new Error("no se pudo contactar con el servidor. ¿Sigue arrancado?");
    }
    // 404/405: la página es nueva pero el servidor sigue con código viejo (no se reinició).
    if (respuesta.status === 404 || respuesta.status === 405) {
      throw new Error("el servidor corre una versión vieja: detenlo (Ctrl+C) y vuelve a arrancarlo.");
    }
    if (!respuesta.ok) {
      const datos = await respuesta.json().catch(() => null);
      throw new Error(datos?.detail || `error ${respuesta.status} del servidor.`);
    }

    await leerLineas(respuesta, (m) => {
      if (m.error) throw new Error(m.error);
      if (m.fin) fin = m.fin;
      if (m.texto) {
        escrito += m.texto;
        codigo.textContent = escrito;
        codigo.scrollTop = codigo.scrollHeight;
        avisar(`escribiendo código… ${escrito.split("\n").length} líneas`);
      }
    });

    const html = extraerHtml(escrito);
    if (!html) throw new Error("Gemini no devolvió un dibujo en HTML. Prueba otra vez.");

    marco.srcdoc = blindar(html);
    mostrarCodigo(false);
    $("#dVerCodigo").disabled = false;

    const salida = fin?.tokens?.salida;
    avisar(
      `${salida ? `escribió ${formato.format(salida)} tokens · ` : ""}` +
        `${escrito.split("\n").length} líneas · ${segundos()} s` +
        (fin?.modelo ? ` · ${fin.modelo}` : "")
    );
  } catch (error) {
    if (!escrito) mostrarCodigo(false);
    avisar(error.message, true);
  } finally {
    codigo.classList.remove("escribiendo");
    await tokens;
    ocupado = false;
    entrada.disabled = false;
    $("#dDibujar").disabled = false;
    $("#dDibujar").textContent = "▸ dibujar";
    for (const b of $("#dEjemplos").children) b.disabled = false;
  }
}

$("#dFormulario").addEventListener("submit", (ev) => {
  ev.preventDefault();
  dibujar(entrada.value);
});

$("#dVerCodigo").addEventListener("click", () => mostrarCodigo(codigo.hidden));

for (const ejemplo of EJEMPLOS) {
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = "chip";
  boton.textContent = ejemplo;
  boton.addEventListener("click", () => {
    entrada.value = ejemplo;
    dibujar(ejemplo);
  });
  $("#dEjemplos").append(boton);
}

estadoServidor().then((datos) => {
  const chip = $("#dEstado");
  if (!datos) {
    chip.textContent = "servidor sin respuesta";
    chip.className = "cabecera-dato malo";
  } else if (!datos.gemini) {
    chip.textContent = "falta GEMINI_API_KEY en .env";
    chip.className = "cabecera-dato malo";
  } else {
    chip.textContent = datos.modelo;
  }
});
