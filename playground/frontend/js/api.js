export async function pedir(ruta, cuerpo) {
  let respuesta;
  try {
    respuesta = await fetch(ruta, {
      method: cuerpo ? "POST" : "GET",
      headers: cuerpo ? { "Content-Type": "application/json" } : undefined,
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
  } catch {
    throw new Error("no se pudo contactar con el servidor. ¿Sigue arrancado?");
  }

  const datos = await respuesta.json().catch(() => null);

  if (!respuesta.ok) {
    const detalle = datos?.detail;
    if (Array.isArray(detalle)) throw new Error(detalle.map((d) => d.msg).join("; "));
    throw new Error(detalle || `error ${respuesta.status} del servidor.`);
  }
  return datos;
}

let promesaEstado = null;
export const estadoServidor = () => (promesaEstado ??= pedir("/api/estado").catch(() => null));

export function colorCss(nombre) {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}

export function hexARgb(hex) {
  const n = parseInt(hex.replace("#", ""), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

// Muestra espacios y saltos de línea de un token, que si no serían invisibles.
export function piezaVisible(texto) {
  const span = document.createElement("span");
  for (const trozo of texto.split(/( +|\n)/)) {
    if (!trozo) continue;
    if (trozo === "\n" || /^ +$/.test(trozo)) {
      const esp = document.createElement("span");
      esp.className = "esp";
      esp.textContent = trozo === "\n" ? "↵" : "·".repeat(trozo.length);
      span.append(esp);
    } else {
      span.append(trozo);
    }
  }
  return span;
}
