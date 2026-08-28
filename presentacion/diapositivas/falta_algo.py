"""Diapositiva 9 — Entonces, ¿qué nos falta?

Vuelve el perceptrón de la 6, pero ahora se abre un hueco entre el sumatorio y
la salida. Ese hueco se queda marcado con una interrogación y no se rellena
hasta la 13 (ReLU): todo el bloque 2 existe para encontrar qué va ahí.
"""

import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    DashedVMobject,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    VGroup,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, PRIMARIO, SECUNDARIO, VERDE

X_ENTRADAS = -5.2
X_CUERPO = -1.9
X_HUECO = 1.2
X_SALIDA = 4.3
Y_EJE = 0.7
RADIO_CUERPO = 0.72
RADIO_HUECO = 0.62
RADIO_NODO = 0.26


def _nodo(centro, radio, color, grosor=3):
    nodo = Circle(radius=radio, color=color, stroke_width=grosor)
    return nodo.set_fill(FONDO, opacity=1.0).move_to(centro)


def construir(scene):
    encabezado = hacer_titulo("Entonces, ¿qué nos falta?")
    centro_cuerpo = np.array([X_CUERPO, Y_EJE, 0.0])

    # --- El perceptrón de la 6, en versión compacta ------------------------
    entradas, aristas = VGroup(), VGroup()
    for y in (1.75, 0.7, -0.35):
        nodo = _nodo([X_ENTRADAS, y, 0], RADIO_NODO, VERDE)
        entradas.add(nodo)
        direccion = centro_cuerpo - nodo.get_center()
        direccion = direccion / np.linalg.norm(direccion)
        aristas.add(Line(
            nodo.get_center() + direccion * RADIO_NODO,
            centro_cuerpo - direccion * RADIO_CUERPO,
            color=SECUNDARIO, stroke_width=2.2,
        ))

    cuerpo = _nodo(centro_cuerpo, RADIO_CUERPO, PRIMARIO, grosor=4)
    sigma = MathTex(r"\Sigma", color=CLARO).scale(0.85).move_to(centro_cuerpo)

    salida = _nodo([X_SALIDA, Y_EJE, 0], 0.3, AMBAR)
    etiqueta_salida = MathTex(r"\hat{y}", color=AMBAR).scale(0.6)
    etiqueta_salida.move_to(salida.get_center())

    # Flecha directa Σ → ŷ: lo que teníamos hasta ahora.
    flecha_directa = Arrow(
        centro_cuerpo + RIGHT * RADIO_CUERPO, [X_SALIDA - 0.34, Y_EJE, 0],
        color=AMBAR, stroke_width=4, buff=0.05,
        max_tip_length_to_length_ratio=0.1,
    )

    # --- El hueco ----------------------------------------------------------
    hueco = DashedVMobject(
        Circle(radius=RADIO_HUECO, color=CLARO, stroke_width=4),
        num_dashes=26,
    ).move_to([X_HUECO, Y_EJE, 0])
    interrogacion = texto("?", 54, color=CLARO).move_to([X_HUECO, Y_EJE, 0])

    flecha_a = Arrow(
        centro_cuerpo + RIGHT * RADIO_CUERPO,
        [X_HUECO - RADIO_HUECO - 0.06, Y_EJE, 0],
        color=SECUNDARIO, stroke_width=4, buff=0.04,
        max_tip_length_to_length_ratio=0.16,
    )
    flecha_b = Arrow(
        [X_HUECO + RADIO_HUECO + 0.06, Y_EJE, 0], [X_SALIDA - 0.34, Y_EJE, 0],
        color=AMBAR, stroke_width=4, buff=0.04,
        max_tip_length_to_length_ratio=0.16,
    )

    diagnostico = VGroup(
        texto("Copiamos la neurona a medias", 26, color=CLARO),
        texto("le falta la pieza que decide cuándo dispara", 19,
              color=SECUNDARIO),
    ).arrange(DOWN, buff=0.2).move_to([0, -1.9, 0])

    vuelta = VGroup(
        texto("Volvamos a la", 26, color=CLARO),
        texto("biología", 26, color=PRIMARIO),
    ).arrange(RIGHT, buff=0.22).move_to([0, -3.1, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(
        LaggedStart(*[GrowFromCenter(n) for n in entradas], lag_ratio=0.15),
        run_time=0.6,
    )
    scene.play(
        LaggedStart(*[Create(a) for a in aristas], lag_ratio=0.15),
        GrowFromCenter(cuerpo), FadeIn(sigma),
        run_time=0.8,
    )
    scene.play(
        Create(flecha_directa),
        GrowFromCenter(VGroup(salida, etiqueta_salida)),
        run_time=0.7,
    )
    scene.next_slide()

    # Se abre el hueco entre el sumatorio y la salida.
    scene.play(FadeOut(flecha_directa), run_time=0.4)
    scene.play(Create(flecha_a), Create(flecha_b), run_time=0.7)
    scene.play(Create(hueco), run_time=0.7)
    scene.play(FadeIn(interrogacion, scale=0.4), run_time=0.5)
    scene.play(Indicate(VGroup(hueco, interrogacion), color=PRIMARIO,
                        scale_factor=1.12), run_time=0.7)
    scene.next_slide()

    scene.play(FadeIn(diagnostico, shift=UP * 0.12), run_time=0.7)
    scene.next_slide()

    scene.play(FadeIn(vuelta, shift=UP * 0.15), run_time=0.7)
    scene.wait(0.4)

    scene.next_slide()
