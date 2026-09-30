from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from tokenizers import Tokenizer

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / ".cache"

ORIGENES = {
    "mediapipe": "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/",
    "modelos": "https://storage.googleapis.com/mediapipe-models/",
    "gemma": "https://huggingface.co/onnx-community/gemma-3-270m-it-ONNX/",
}

VISION = [
    "mediapipe/vision_bundle.mjs",
    "mediapipe/wasm/vision_wasm_internal.js",
    "mediapipe/wasm/vision_wasm_internal.wasm",
    "mediapipe/wasm/vision_wasm_nosimd_internal.js",
    "mediapipe/wasm/vision_wasm_nosimd_internal.wasm",
    "modelos/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
    "modelos/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
    "modelos/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite",
    "modelos/image_classifier/efficientnet_lite0/float32/1/efficientnet_lite0.tflite",
]

# Gemma 3 usa el mismo tokenizador que Gemini (SentencePiece, 262k piezas).
TOKENIZADOR = "gemma/resolve/main/tokenizer.json"

TODOS = [*VISION, TOKENIZADOR]

# Solo se sirve (y se baja) lo que está en esta lista: nada de pedir archivos arbitrarios.
PERMITIDOS = frozenset(TODOS)

TIPOS = {
    ".mjs": "text/javascript",
    ".js": "text/javascript",
    ".wasm": "application/wasm",
    ".json": "application/json",
}

_candados: dict[str, asyncio.Lock] = {}
_tokenizador: Tokenizer | None = None


def ruta_local(ruta: str) -> Path | None:
    return CACHE / ruta if ruta in PERMITIDOS else None


def tipo(destino: Path) -> str:
    return TIPOS.get(destino.suffix, "application/octet-stream")


async def asegurar(ruta: str) -> Path:
    """Devuelve el fichero en disco; si no está, lo baja una vez y lo guarda."""
    destino = ruta_local(ruta)
    if destino is None:
        raise LookupError(ruta)
    if destino.exists():
        return destino

    async with _candados.setdefault(ruta, asyncio.Lock()):
        if destino.exists():
            return destino

        origen, _, resto = ruta.partition("/")
        destino.parent.mkdir(parents=True, exist_ok=True)
        parcial = destino.with_name(destino.name + ".parcial")

        tiempo = httpx.Timeout(30, read=120)
        async with httpx.AsyncClient(timeout=tiempo, follow_redirects=True) as cliente:
            async with cliente.stream("GET", ORIGENES[origen] + resto) as respuesta:
                respuesta.raise_for_status()
                with parcial.open("wb") as fichero:
                    async for trozo in respuesta.aiter_bytes(1 << 16):
                        fichero.write(trozo)

        parcial.replace(destino)
        return destino


async def tokenizador() -> Tokenizer:
    global _tokenizador
    if _tokenizador is None:
        ruta = await asegurar(TOKENIZADOR)
        _tokenizador = await asyncio.to_thread(Tokenizer.from_file, str(ruta))
    return _tokenizador
