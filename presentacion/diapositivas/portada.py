"""Portada con la identidad de marca Aperture (Semillero de Data Science e IA).

Fondo oscuro, título en Press Start 2P, cuerpo en JetBrains Mono, acento cian.
A la derecha, una neurona artificial (perceptrón) animada y vectorial:
nodos de entrada x_i con pesos w_i, bias +b, cuerpo dividido en sumatorio Σ
y activación ReLU, salida ŷ y la fórmula ŷ = ReLU(Σ xᵢwᵢ + b).
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    Flash,
    GrowFromCenter,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    VGroup,
    VMobject,
    Write,
)

from componentes import logo_esquina, separador, texto
from estilo import AMBAR, CLARO, FONT_TITULO, MORADO, PRIMARIO, SECUNDARIO

RELLENO_NODO = "#04121a"


def _m(tex, color, s=0.6):
    return MathTex(tex, color=color).scale(s)


def _neurona_artificial(scene, centro=np.array([3.55, 0.3, 0.0])):
    """Perceptrón: nodos, pesos, bias +b, cuerpo Σ|ReLU y salida ŷ."""
    cx, cy, _ = centro
    R = 1.0

    # --- Cuerpo dividido: Σ a la izquierda, ReLU a la derecha --------------
    cuerpo = Circle(radius=R, color=PRIMARIO, stroke_width=4).move_to(centro)
    cuerpo.set_fill(RELLENO_NODO, opacity=1.0)
    divisor = Line(
        [cx, cy - R + 0.07, 0], [cx, cy + R - 0.07, 0],
        color=SECUNDARIO, stroke_width=1.6, stroke_opacity=0.55,
    )
    sigma = _m(r"\Sigma", CLARO, 0.9).move_to([cx - 0.45, cy, 0])

    # Mini gráfica de ReLU (eje tenue + curva en morado)
    o = np.array([cx + 0.42, cy - 0.22, 0])
    eje_x = Line(o + LEFT * 0.3, o + RIGHT * 0.42,
                 color=SECUNDARIO, stroke_width=1.4, stroke_opacity=0.6)
    relu = VMobject(color=MORADO, stroke_width=3.5)
    relu.set_points_as_corners([o + LEFT * 0.28, o, o + np.array([0.38, 0.62, 0])])
    activacion = VGroup(eje_x, relu)

    # --- Nodos de entrada x_i, pesos w_i y conexiones ----------------------
    ent_x = cx - 2.85
    nodo_r = 0.3
    filas = [(1.5, "x_1", "w_1"), (0.6, "x_2", "w_2"), (-1.3, "x_n", "w_n")]
    nodos, x_labels, aristas, w_labels = [], [], [], []
    for y, xt, wt in filas:
        nodo = Circle(radius=nodo_r, color=SECUNDARIO, stroke_width=3)
        nodo.set_fill(RELLENO_NODO, opacity=1.0).move_to([ent_x, y, 0])
        xl = _m(xt, CLARO, 0.52).move_to(nodo.get_center())
        dir_ = centro - nodo.get_center()
        dir_ = dir_ / np.linalg.norm(dir_)
        inicio = nodo.get_center() + dir_ * nodo_r
        fin = centro - dir_ * R
        arista = Line(inicio, fin, color=PRIMARIO, stroke_width=2.5,
                      stroke_opacity=0.9)
        wl = _m(wt, SECUNDARIO, 0.5).move_to(
            arista.point_from_proportion(0.42) + np.array([0, 0.25, 0])
        )
        nodos.append(nodo)
        x_labels.append(xl)
        aristas.append(arista)
        w_labels.append(wl)
    vdots = _m(r"\vdots", SECUNDARIO, 0.55).move_to([ent_x, -0.35, 0])

    # --- Bias: nodo b (como las entradas) que se suma al cuerpo -------------
    b_nodo = Circle(radius=0.26, color=AMBAR, stroke_width=3)
    b_nodo.set_fill(RELLENO_NODO, opacity=1.0).move_to([cx, cy + R + 0.85, 0])
    b_lbl = _m("b", AMBAR, 0.55).move_to(b_nodo.get_center())
    dir_b = centro - b_nodo.get_center()
    dir_b = dir_b / np.linalg.norm(dir_b)
    b_linea = Line(
        b_nodo.get_center() + dir_b * 0.26, centro - dir_b * R,
        color=AMBAR, stroke_width=2.5, stroke_opacity=0.9,
    )
    b_mas = _m("+", AMBAR, 0.5).move_to(
        b_linea.point_from_proportion(0.5) + RIGHT * 0.22
    )

    # --- Salida ŷ -----------------------------------------------------------
    salida_x = cx + 2.3
    flecha = Arrow(
        centro + RIGHT * R, [salida_x - 0.34, cy, 0],
        color=PRIMARIO, stroke_width=4, buff=0.05,
        max_tip_length_to_length_ratio=0.14,
    )
    salida = Circle(radius=0.3, color=PRIMARIO, stroke_width=3)
    salida.set_fill(RELLENO_NODO, opacity=1.0).move_to([salida_x, cy, 0])
    y_lbl = _m(r"\hat{y}", PRIMARIO, 0.62).move_to(salida.get_center())

    # --- Fórmula ------------------------------------------------------------
    formula = _m(r"\hat{y} = \mathrm{ReLU}\!\left(\sum_i x_i w_i + b\right)",
                 SECUNDARIO, 0.78)
    formula.move_to([cx, cy - R - 1.25, 0])

    # ---------------------- Animación ---------------------------------------
    scene.play(
        LaggedStart(*[GrowFromCenter(VGroup(n, l))
                      for n, l in zip(nodos, x_labels)],
                    FadeIn(vdots), lag_ratio=0.18),
        run_time=0.9,
    )
    scene.play(
        LaggedStart(*[Create(a) for a in aristas], lag_ratio=0.2),
        FadeIn(VGroup(*w_labels)), run_time=0.9,
    )
    scene.play(GrowFromCenter(cuerpo), Create(divisor), FadeIn(sigma),
               run_time=0.7)
    scene.play(Create(eje_x), Create(relu), run_time=0.6)
    scene.play(
        GrowFromCenter(VGroup(b_nodo, b_lbl)), Create(b_linea),
        FadeIn(b_mas), run_time=0.6,
    )

    # Pulsos de señal viajando por cada arista hacia el cuerpo
    pulsos = [Dot(color=CLARO, radius=0.06).move_to(a.get_start())
              for a in aristas]
    scene.play(*[MoveAlongPath(p, a) for p, a in zip(pulsos, aristas)],
               run_time=0.9)
    scene.play(
        Indicate(cuerpo, color=PRIMARIO, scale_factor=1.12),
        Flash(cuerpo, color=PRIMARIO, line_length=0.28, num_lines=16,
              flash_radius=R + 0.4),
        *[FadeIn(p, scale=0.1) for p in pulsos], run_time=0.7,
    )
    scene.remove(*pulsos)

    # Salida
    scene.play(Create(flecha), run_time=0.5)
    pulso_out = Dot(color=CLARO, radius=0.06).move_to(flecha.get_start())
    scene.play(MoveAlongPath(pulso_out, flecha), run_time=0.5)
    scene.play(
        FadeIn(salida), FadeIn(y_lbl), FadeIn(pulso_out, scale=0.1),
        run_time=0.4,
    )
    scene.remove(pulso_out)
    scene.play(Indicate(salida, color=PRIMARIO), run_time=0.4)

    # Fórmula
    scene.play(Write(formula), run_time=1.1)


def construir(scene):
    # --- Barra de acento y columna izquierda ------------------------------
    barra = Line(UP * 2.5, DOWN * 2.5, color=PRIMARIO, stroke_width=6)
    barra.to_edge(LEFT, buff=0.8)

    antetitulo = texto("SEMILLERO APERTURE", 15, color=PRIMARIO)
    titulo = VGroup(
        texto("COMO", 26, color=CLARO, font=FONT_TITULO),  # Press Start 2P: sin acento
        texto("FUNCIONAN", 26, color=CLARO, font=FONT_TITULO),
        texto("LAS REDES", 26, color=CLARO, font=FONT_TITULO),
        texto("NEURONALES", 26, color=PRIMARIO, font=FONT_TITULO),
    ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
    max_ancho = 5.2
    if titulo.width > max_ancho:
        titulo.scale(max_ancho / titulo.width)
    linea = separador(largo=2.4)
    subtitulo = VGroup(
        texto("Una introducción visual", 16, color=SECUNDARIO),
        texto("al aprendizaje profundo", 16, color=SECUNDARIO),
    ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

    titulo.next_to(antetitulo, DOWN, buff=0.32, aligned_edge=LEFT)
    linea.next_to(titulo, DOWN, buff=0.36, aligned_edge=LEFT)
    subtitulo.next_to(linea, DOWN, buff=0.3, aligned_edge=LEFT)
    bloque = VGroup(antetitulo, titulo, linea, subtitulo)
    bloque.next_to(barra, RIGHT, buff=0.5).set_y(0)

    # --- Logo del semillero en la esquina inferior derecha ----------------
    logo = logo_esquina()

    # --- Animación: primero el texto, luego la neurona --------------------
    scene.play(GrowFromEdge(barra, UP), run_time=0.5)
    scene.play(FadeIn(antetitulo, shift=RIGHT * 0.15), run_time=0.4)
    for linea_titulo in titulo:
        scene.play(FadeIn(linea_titulo, shift=UP * 0.12), run_time=0.3)
    scene.play(Create(linea), run_time=0.4)
    scene.play(FadeIn(subtitulo, shift=UP * 0.1), run_time=0.4)

    _neurona_artificial(scene)

    scene.play(FadeIn(logo), run_time=0.5)
    scene.wait(0.6)
    scene.next_slide()
