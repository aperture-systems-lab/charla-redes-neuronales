from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator

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


async def dibujar(pedido: str) -> AsyncIterator[dict]:
    """Va soltando el HTML según Gemini lo escribe: {"texto"}… y al final {"fin"} o {"error"}."""
    modelos = list(dict.fromkeys([MODELO, MODELO_RESPALDO]))
    configuraciones = list(SIN_PENSAR)
    uso: dict = {}
    intento = 0

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20, read=120)) as cliente:
            while True:
                modelo = modelos[0]
                url = f"{BASE}/{modelo}:streamGenerateContent?alt=sse"
                cuerpo = {
                    "systemInstruction": {"parts": [{"text": INSTRUCCION_DIBUJAR}]},
                    "contents": [{"parts": [{"text": pedido}]}],
                    "generationConfig": configuraciones[0],
                }
                async with cliente.stream("POST", url, json=cuerpo, headers=HEADERS) as respuesta:
                    # 503 = "alta demanda" en Google: suele pasar en segundos.
                    if respuesta.status_code == 503 and intento < REINTENTOS:
                        intento += 1
                        await asyncio.sleep(1.5 * intento)
                        continue
                    # 429 = cuota agotada (el plan gratis da unas 20 al día por modelo).
                    if respuesta.status_code == 429 and len(modelos) > 1:
                        modelos.pop(0)
                        configuraciones = list(SIN_PENSAR)
                        continue
                    if respuesta.status_code == 400 and len(configuraciones) > 1:
                        configuraciones.pop(0)
                        continue
                    if respuesta.status_code >= 400:
                        yield {"error": detalle_error(modelo, respuesta, await respuesta.aread())}
                        return

                    async for linea in respuesta.aiter_lines():
                        if not linea.startswith("data:"):
                            continue
                        try:
                            datos = json.loads(linea[5:])
                        except ValueError:
                            continue
                        uso = datos.get("usageMetadata") or uso
                        for candidato in datos.get("candidates") or []:
                            for parte in candidato.get("content", {}).get("parts", []):
                                if parte.get("text") and not parte.get("thought"):
                                    yield {"texto": parte["text"]}
                    break
    except httpx.TimeoutException:
        yield {"error": "Gemini tardó demasiado en responder. Reintenta."}
        return
    except httpx.HTTPError:
        yield {"error": "se cortó la conexión con Gemini (¿sin internet?)."}
        return

    yield {
        "fin": {
            "modelo": modelo,
            "tokens": {
                "entrada": int(uso.get("promptTokenCount", 0)),
                "pensamiento": int(uso.get("thoughtsTokenCount", 0)),
                "salida": int(uso.get("candidatesTokenCount", 0)),
            },
        }
    }
