"""Baja a playground/.cache todo lo que el playground necesita de internet.

    uv run python -m backend.descargar

Después, las pestañas de visión y de tokens funcionan sin conexión.
"""

from __future__ import annotations

import asyncio

from . import recursos


async def main() -> None:
    for ruta in recursos.TODOS:
        destino = recursos.ruta_local(ruta)
        if destino.exists():
            print(f"  ya estaba  {ruta}")
            continue

        print(f"  bajando    {ruta} …", flush=True)
        await recursos.asegurar(ruta)
        print(f"             {destino.stat().st_size / 1e6:.1f} MB")

    print(f"\nlisto: todo en {recursos.CACHE}")


if __name__ == "__main__":
    asyncio.run(main())
