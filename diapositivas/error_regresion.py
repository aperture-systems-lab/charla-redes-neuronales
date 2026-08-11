"""Diapositiva 19 — Medir el error en regresión.

Si queremos mejorar, primero hay que poder medir cuánto nos equivocamos. Los
residuos de la 7 vuelven, pero ahora se elevan literalmente al cuadrado: cada
error se convierte en un cuadrado de verdad, y el área total es la pérdida.

Así se ve por qué el error cuadrático castiga tanto los fallos grandes.
"""

import numpy as np
from manim import (
    DOWN,
    UP,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    LaggedStart,
    MathTex,
    Square,
    VGroup,
    Write,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, PRIMARIO, SECUNDARIO, VERDE

PENDIENTE = 0.75
ORDENADA = 0.6
XS = (0.4, 1.0, 1.6, 2.2, 2.8, 3.4)
DESVIOS = (0.55, -0.3, 0.2, -0.75, 0.35, -0.45)


def construir(scene):
    encabezado = hacer_titulo("¿Cuánto nos equivocamos?")

    ejes = Axes(
        x_range=[0, 4, 1], y_range=[0, 4.2, 1],
        x_length=6.4, y_length=4.2,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5,
            "include_ticks": False, "tip_width": 0.16, "tip_height": 0.16,
        },
    ).move_to([-1.6, 0.35, 0])

    recta = ejes.plot(
        lambda x: PENDIENTE * x + ORDENADA, x_range=[0.15, 3.8], color=PRIMARIO,
    )
    recta.set_stroke(width=4)
    rot_recta = texto("predicción", 17, color=PRIMARIO)
    rot_recta.next_to(ejes.c2p(3.8, PENDIENTE * 3.8 + ORDENADA), UP, buff=0.12)

    reales, residuos, cuadrados = VGroup(), VGroup(), VGroup()
    unidad = ejes.c2p(1, 0)[0] - ejes.c2p(0, 0)[0]  # una unidad de dato en pantalla
    for x, desvio in zip(XS, DESVIOS):
        y_pred = PENDIENTE * x + ORDENADA
        y_real = y_pred + desvio
        reales.add(Dot(ejes.c2p(x, y_real), radius=0.075, color=CLARO))
        residuos.add(DashedLine(
            ejes.c2p(x, y_real), ejes.c2p(x, y_pred),
            color=AMBAR, stroke_width=2.5, dash_length=0.08,
        ))
        # El cuadrado del error, con el lado igual al residuo.
        lado = abs(desvio) * (ejes.c2p(0, 1)[1] - ejes.c2p(0, 0)[1])
        cuadrado = Square(
            side_length=lado, stroke_color=AMBAR, stroke_width=2,
            fill_color=AMBAR, fill_opacity=0.22,
        )
        borde_y = ejes.c2p(x, min(y_real, y_pred))[1]
        cuadrado.move_to([
            ejes.c2p(x, 0)[0] + lado / 2, borde_y + lado / 2, 0,
        ])
        cuadrados.add(cuadrado)

    formula = MathTex(
        r"\mathrm{ECM} = \frac{1}{n}\sum_i \left(y_i - \hat{y}_i\right)^2",
        color=CLARO,
    ).scale(0.7).move_to([4.2, 1.5, 0])

    idea = VGroup(
        texto("Elevar al cuadrado", 21, color=AMBAR),
        texto("castiga los fallos", 17, color=SECUNDARIO),
        texto("grandes mucho más", 17, color=SECUNDARIO),
    ).arrange(DOWN, buff=0.12).move_to([4.3, -1.1, 0])

    cierre_idea = texto(
        "La pérdida es un único número: el área total", 21, color=CLARO,
    ).move_to([0, -3.2, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(ejes), run_time=0.8)
    scene.play(
        LaggedStart(*[FadeIn(p, scale=0.5) for p in reales], lag_ratio=0.1),
        run_time=0.8,
    )
    scene.play(Create(recta), FadeIn(rot_recta), run_time=0.8)
    scene.next_slide()

    # El error de cada punto.
    scene.play(
        LaggedStart(*[Create(r) for r in residuos], lag_ratio=0.12),
        run_time=1.0,
    )
    scene.next_slide()

    # Cada error, al cuadrado.
    scene.play(
        LaggedStart(*[FadeIn(c, scale=0.4) for c in cuadrados], lag_ratio=0.15),
        run_time=1.2,
    )
    scene.play(FadeIn(idea, shift=UP * 0.12), run_time=0.6)
    scene.next_slide()

    scene.play(Write(formula), run_time=1.1)
    scene.play(FadeIn(cierre_idea, shift=UP * 0.12), run_time=0.6)
    scene.wait(0.4)

    scene.next_slide()
