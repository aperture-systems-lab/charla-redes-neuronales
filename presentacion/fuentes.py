"""Registro de las fuentes de marca para que Manim (Pango) las encuentre.

Los .ttf viven en ``assets/fonts/`` y se registran en el proceso al importar
este módulo, así no hace falta instalarlas en el sistema. ``estilo.py`` lo
importa, de modo que cualquier diapositiva las tiene disponibles.
"""

import os

import manimpango

_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")

# (familia visible en Manim, archivo .ttf)
_ARCHIVOS = (
    ("Press Start 2P", "PressStart2P-Regular.ttf"),
    ("JetBrains Mono", "JetBrainsMono-Regular.ttf"),
    ("JetBrains Mono", "JetBrainsMono-Bold.ttf"),
)

_registradas = False


def registrar():
    """Registra las fuentes de marca una sola vez por proceso."""
    global _registradas
    if _registradas:
        return
    for _familia, archivo in _ARCHIVOS:
        manimpango.register_font(os.path.join(_DIR, archivo))
    _registradas = True


registrar()
