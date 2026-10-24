from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

from .recursos import RAIZ

load_dotenv(RAIZ / ".env")

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODELO = os.getenv("GEMINI_MODELO", "gemini-3.6-flash").strip()
MODELO_RESPALDO = os.getenv("GEMINI_MODELO_RESPALDO", "gemini-3.5-flash-lite").strip()

BASE = "https://generativelanguage.googleapis.com/v1beta/models"
REINTENTOS = 2

INSTRUCCION_DIBUJAR = (
    "Eres un artista que dibuja con código. Responde SOLO con un documento HTML completo "
    "y autónomo que empiece por <!doctype html>, sin markdown ni explicaciones. Dibuja lo que "
    "pida el usuario con SVG o <canvas> y JavaScript, con colores vivos y, si queda bien, una "
    "animación suave. Reglas: nada externo (ni imágenes, ni fuentes, ni librerías, ni fetch); "
    "el dibujo llena toda la ventana (100vw × 100vh, sin barras de desplazamiento) y se adapta "
    "a su tamaño; fondo oscuro; como mucho 100 líneas."
)

# Sin pensar antes, el código empieza a salir en menos de un segundo (y no en ~20).
# Si el modelo no acepta thinkingLevel, se reintenta con la segunda opción: sin configurar.
SIN_PENSAR = [{"thinkingConfig": {"thinkingLevel": "minimal"}}, {}]

HEADERS = {"x-goog-api-key": API_KEY}


def exigir_clave() -> None:
    if not API_KEY:
        raise HTTPException(
            400, "falta GEMINI_API_KEY: ponla en el fichero .env y reinicia el servidor."
        )


def detalle_error(modelo: str, respuesta: httpx.Response, cuerpo: bytes) -> str:
    try:
        mensaje = json.loads(cuerpo).get("error", {}).get("message")
    except ValueError:
        mensaje = None
    return f"{modelo} devolvió {respuesta.status_code}: {mensaje or cuerpo[:200].decode(errors='replace')}"


class _Intentos:
    """Qué modelo y qué configuración toca probar, y cómo seguir si Gemini contesta con error."""

    def __init__(self) -> None:
        self.modelos = list(dict.fromkeys([MODELO, MODELO_RESPALDO]))
        self.configuraciones = list(SIN_PENSAR)
        self.reintentos = 0

    @property
    def modelo(self) -> str:
        return self.modelos[0]

    def peticion(self, cliente: httpx.AsyncClient, pedido: str) -> httpx.Request:
        cuerpo = {
            "systemInstruction": {"parts": [{"text": INSTRUCCION_DIBUJAR}]},
            "contents": [{"parts": [{"text": pedido}]}],
            "generationConfig": self.configuraciones[0],
        }
        url = f"{BASE}/{self.modelo}:streamGenerateContent?alt=sse"
        return cliente.build_request("POST", url, json=cuerpo, headers=HEADERS)

    def siguiente(self, estado: int) -> float | None:
        """Prepara el próximo intento y devuelve cuántos segundos esperar; None si no hay arreglo."""
        # 503 = "alta demanda" en Google: suele pasar en segundos.
        if estado == 503 and self.reintentos < REINTENTOS:
            self.reintentos += 1
            return 1.5 * self.reintentos
        # 429 = cuota agotada (el plan gratis da unas 20 al día por modelo).
        if estado == 429 and len(self.modelos) > 1:
            self.modelos.pop(0)
            self.configuraciones = list(SIN_PENSAR)
            return 0
        # 400 = el modelo no acepta thinkingLevel: se prueba sin configurar.
        if estado == 400 and len(self.configuraciones) > 1:
            self.configuraciones.pop(0)
            return 0
        return None


@asynccontextmanager
async def _conectar(
    cliente: httpx.AsyncClient, intentos: _Intentos, pedido: str
) -> AsyncIterator[httpx.Response]:
    """Abre el stream con Gemini, reintentando mientras el error tenga arreglo."""
    while True:
        respuesta = await cliente.send(intentos.peticion(cliente, pedido), stream=True)
        espera = intentos.siguiente(respuesta.status_code)
        if espera is None:
            break
        await respuesta.aclose()
        await asyncio.sleep(espera)
    try:
        yield respuesta
    finally:
        await respuesta.aclose()


def _datos(linea: str) -> dict:
    """Los datos de una línea del stream (SSE); vacío si la línea no trae datos."""
    if not linea.startswith("data:"):
        return {}
    try:
        return json.loads(linea[5:])
    except ValueError:
        return {}


def _textos(datos: dict) -> Iterator[str]:
    """Los trozos de HTML que trae un mensaje, sin los pensamientos del modelo."""
    for candidato in datos.get("candidates") or []:
        for parte in candidato.get("content", {}).get("parts", []):
            if parte.get("text") and not parte.get("thought"):
                yield parte["text"]


def _resumen(modelo: str, uso: dict) -> dict:
    return {
        "modelo": modelo,
        "tokens": {
            "entrada": int(uso.get("promptTokenCount", 0)),
            "pensamiento": int(uso.get("thoughtsTokenCount", 0)),
            "salida": int(uso.get("candidatesTokenCount", 0)),
        },
    }


async def _leer(modelo: str, respuesta: httpx.Response) -> AsyncIterator[dict]:
    """Lo que contesta Gemini, ya convertido en los mensajes que espera el navegador."""
    if respuesta.status_code >= 400:
        yield {"error": detalle_error(modelo, respuesta, await respuesta.aread())}
        return
    uso: dict = {}
    async for linea in respuesta.aiter_lines():
        datos = _datos(linea)
        uso = datos.get("usageMetadata") or uso
        for texto in _textos(datos):
            yield {"texto": texto}
    yield {"fin": _resumen(modelo, uso)}


async def dibujar(pedido: str) -> AsyncIterator[dict]:
    """Va soltando el HTML según Gemini lo escribe: {"texto"}… y al final {"fin"} o {"error"}."""
    intentos = _Intentos()
    try:
        async with (
            httpx.AsyncClient(timeout=httpx.Timeout(20, read=120)) as cliente,
            _conectar(cliente, intentos, pedido) as respuesta,
        ):
            async for mensaje in _leer(intentos.modelo, respuesta):
                yield mensaje
    except httpx.TimeoutException:
        yield {"error": "Gemini tardó demasiado en responder. Reintenta."}
    except httpx.HTTPError:
        yield {"error": "se cortó la conexión con Gemini (¿sin internet?)."}
