"""Diapositiva 20 — Medir el error en clasificación.

Acertar con 0.9 de confianza y acertar con 0.51 no es lo mismo. La entropía
cruzada mide justo eso: el coste es −log(p), donde p es la probabilidad que el
modelo le dio a la respuesta correcta.

La curva se dispara cuando p se acerca a 0: equivocarse con mucha seguridad sale
carísimo.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    LaggedStart,
    MathTex,
    VGroup,
    Write,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, MORADO, PRIMARIO, SECUNDARIO, VERDE

CASOS = (
    (0.9, "muy seguro y acierta", VERDE),
    (0.51, "duda, pero acierta", AMBAR),
    (0.1, "seguro y se equivoca", MORADO),
)


def construir(scene):
    encabezado = hacer_titulo("Acertar con dudas cuesta más")

    ejes = Axes(
        x_range=[0, 1.05, 0.25], y_range=[0, 3.0, 1],
        x_length=6.2, y_length=4.0,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5,
            "include_ticks": False, "tip_width": 0.16, "tip_height": 0.16,
        },
    ).move_to([-1.9, 0.4, 0])

    curva = ejes.plot(
        lambda p: -np.log(p), x_range=[0.052, 1.0, 0.01], color=PRIMARIO,
    )
    curva.set_stroke(width=4)

    rot_x = texto("probabilidad dada a la respuesta correcta", 16,
                  color=SECUNDARIO)
    rot_x.next_to(ejes.x_axis, DOWN, buff=0.62)
    rot_y = texto("coste", 17, color=SECUNDARIO)
    rot_y.next_to(ejes.c2p(0, 2.6), LEFT, buff=0.2)

    marcas = VGroup()
    for p, descripcion, color in CASOS:
        coste = -np.log(p)
        punto = Dot(ejes.c2p(p, coste), radius=0.09, color=color)
        guia = DashedLine(
            ejes.c2p(p, 0), ejes.c2p(p, coste),
            color=color, stroke_width=2, stroke_opacity=0.6, dash_length=0.08,
        )
        etiqueta = texto(f"p = {p}", 16, color=color)
        etiqueta.next_to(ejes.c2p(p, 0), DOWN, buff=0.12)
        marcas.add(VGroup(guia, punto, etiqueta))

    lista = VGroup(*[
        VGroup(
            texto(f"{-np.log(p):.2f}", 24, color=color),
            texto(descripcion, 16, color=SECUNDARIO),
        ).arrange(RIGHT, buff=0.25)
        for p, descripcion, color in CASOS
    ]).arrange(DOWN, buff=0.32, aligned_edge=LEFT).move_to([4.0, 1.1, 0])

    formula = MathTex(r"\mathcal{L} = -\log(p)", color=CLARO)
    formula.scale(0.85).move_to([4.0, -1.0, 0])

    cierre_idea = texto(
        "Equivocarse con mucha seguridad sale carísimo", 21, color=CLARO,
    ).move_to([0, -3.2, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(ejes), FadeIn(rot_x), FadeIn(rot_y), run_time=0.9)
    scene.play(Create(curva), run_time=1.2)
    scene.play(Write(formula), run_time=0.8)
    scene.next_slide()

    # Los tres casos, de mejor a peor.
    for marca, fila in zip(marcas, lista):
        scene.play(FadeIn(marca), FadeIn(fila, shift=RIGHT * 0.15),
                   run_time=0.7)
    scene.next_slide()

    scene.play(FadeIn(cierre_idea, shift=UP * 0.12), run_time=0.7)
    scene.wait(0.4)

    scene.next_slide()
