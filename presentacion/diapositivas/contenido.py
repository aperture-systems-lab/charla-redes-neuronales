"""Diapositiva de contenido tipo: título + viñetas + elemento visual.

Úsala como referencia del patrón más común. Duplica y adapta.
"""

from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    Line,
    VGroup,
)

from componentes import tarjeta, texto, vinetas
from componentes import titulo as hacer_titulo
from estilo import PRIMARIO, SECUNDARIO


def _icono():
    """Fábrica local de un mobject propio de esta diapositiva."""
    aro = Line(LEFT * 0.4, RIGHT * 0.4, color=PRIMARIO, stroke_width=5)
    tallo = Line(UP * 0.4, DOWN * 0.4, color=SECUNDARIO, stroke_width=5)
    return VGroup(aro, tallo)


def construir(scene):
    encabezado = hacer_titulo("Título de la sección")

    puntos = vinetas([
        "Primera idea clave",
        "Segunda idea que la refuerza",
        "Tercera idea que cierra el argumento",
    ]).shift(LEFT * 2.6 + DOWN * 0.4)

    icono = _icono().scale(1.4).shift(RIGHT * 3.6 + DOWN * 0.2)
    resaltado = tarjeta(
        [("Dato o cifra", 20, BOLD), ("que destacar", 16, BOLD)],
    ).next_to(icono, DOWN, buff=0.5)

    nota = texto("Fuente / aclaración", 15, color=SECUNDARIO).to_edge(DOWN, buff=0.6)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)
    for punto in puntos:
        scene.play(FadeIn(punto, shift=RIGHT * 0.2), run_time=0.35)
    scene.play(Create(icono), run_time=0.6)
    scene.play(FadeIn(resaltado, shift=UP * 0.2), run_time=0.5)
    scene.play(FadeIn(nota), run_time=0.4)
    scene.wait(0.5)

    scene.next_slide()
