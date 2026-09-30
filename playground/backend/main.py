from __future__ import annotations

import json
import mimetypes

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import gemini, recursos

# En Windows el registro a veces sirve .js como text/plain y los módulos no cargan.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")

app = FastAPI(title="playground-redes")


@app.middleware("http")
async def sin_cache(peticion, siguiente):
    respuesta = await siguiente(peticion)
    if not peticion.url.path.startswith("/cache/"):
        respuesta.headers["Cache-Control"] = "no-store, must-revalidate"
    return respuesta


class Texto(BaseModel):
    texto: str = Field(..., max_length=4000)


class Pedido(BaseModel):
    pedido: str = Field(..., min_length=1, max_length=300)


@app.get("/api/estado")
async def estado() -> dict:
    return {"gemini": bool(gemini.API_KEY), "modelo": gemini.MODELO}


@app.post("/api/tokens")
async def tokens(peticion: Texto) -> dict:
    try:
        tokenizador = await recursos.tokenizador()
    except httpx.HTTPError:
        raise HTTPException(502, "no se pudo descargar el tokenizador (¿sin conexión?).")

    texto = peticion.texto
    codificado = tokenizador.encode(texto, add_special_tokens=False)

    piezas = []
    anterior = None
    for id_, crudo, (desde, hasta) in zip(
        codificado.ids, codificado.tokens, codificado.offsets
    ):
        # Un carácter raro se parte en varios tokens de bytes que comparten el mismo tramo.
        de_bytes = crudo.startswith("<0x") or (desde, hasta) == anterior
        piezas.append({"id": id_, "texto": crudo if de_bytes else texto[desde:hasta], "bytes": de_bytes})
        anterior = (desde, hasta)

    return {"tokens": piezas}


@app.post("/api/dibujar")
async def dibujar(peticion: Pedido) -> StreamingResponse:
    gemini.exigir_clave()

    async def lineas():
        async for mensaje in gemini.dibujar(peticion.pedido):
            yield json.dumps(mensaje, ensure_ascii=False) + "\n"

    return StreamingResponse(lineas(), media_type="application/x-ndjson")


@app.get("/cache/{ruta:path}")
async def cache(ruta: str) -> FileResponse:
    try:
        destino = await recursos.asegurar(ruta)
    except LookupError:
        raise HTTPException(404, f"no se sirve {ruta}")
    except httpx.HTTPStatusError as error:
        raise HTTPException(error.response.status_code, f"el origen no tiene {ruta}")
    except httpx.HTTPError:
        raise HTTPException(502, f"{ruta} no está en caché y no hay conexión para bajarlo.")

    return FileResponse(
        destino,
        media_type=recursos.tipo(destino),
        headers={"Cache-Control": "public, max-age=604800"},
    )


app.mount("/", StaticFiles(directory=recursos.RAIZ / "frontend", html=True), name="web")
