"""PLANTILLA de diapositiva — copia este archivo para crear una nueva.

Pasos para dar de alta la diapositiva:
  1) Copia a ``diapositivas/<nombre>.py`` y renombra el contenido.
  2) En ``diapositivas/__init__.py``: impórtalo y añade
     ``slide_<nombre> = _slide(<nombre>.construir)`` al mixin adecuado.
  3) En ``main.py``: llama ``self.slide_<nombre>()`` desde ``construct``.

Reglas:
  * No limpies la pantalla al entrar (lo hace ``SlideBase.iniciar_slide``).
  * No añadas fondo: ``SlideBase.iniciar_slide`` pone la malla de red decorativa
    y va rotando el preset en cada diapositiva.
  * Nunca hardcodees colores: úsalos desde ``estilo``.
  * Termina SIEMPRE con ``scene.next_slide()``.
  * No pongas nada en la esquina inferior derecha: ahí sale el indicador de
    avance (el logo del semillero) que ``SlideBase.next_slide`` añade en cada
    pausa.
"""

from manim import (
    DOWN,
    RIGHT,
    FadeIn,
)

from componentes import vinetas
from componentes import titulo as hacer_titulo


def construir(scene):
    encabezado = hacer_titulo("Título de la diapositiva")
    cuerpo = vinetas([
        "Idea uno",
        "Idea dos",
        "Idea tres",
    ]).shift(DOWN * 0.3)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.7)
    for elemento in cuerpo:
        scene.play(FadeIn(elemento, shift=RIGHT * 0.2), run_time=0.35)
    scene.wait(0.5)

    scene.next_slide()
