"""Helpers de animación compartidos: reciben la escena como primer argumento.

Centraliza aquí los patrones de animación que repitas en varias diapositivas
(entradas escalonadas, transiciones, énfasis) para no copiarlos por todos lados.
"""

from manim import (
    RIGHT,
    FadeIn,
    FadeOut,
)


def limpiar_pantalla(scene):
    """Desvanece todo lo que hay en escena salvo el marco fijo."""
    resto = [m for m in scene.mobjects if m is not getattr(scene, "marco", None)]
    for m in resto:
        m.clear_updaters()
    if resto:
        scene.play(*[FadeOut(m) for m in resto])


def aparecer_uno_a_uno(scene, grupo, run_time=0.4, shift=RIGHT * 0.2):
    """Hace aparecer los elementos de un VGroup uno tras otro."""
    for elemento in grupo:
        scene.play(FadeIn(elemento, shift=shift), run_time=run_time)
