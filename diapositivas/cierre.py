"""Diapositiva 29 — Cierre.

Cierra el círculo con la portada: mismo tipo de display (Press Start 2P) y el
mismo perceptrón vectorial, pero ahora **su salida es el QR**. Toda la charla
—entradas, pesos, suma, activación— desemboca en el sitio donde están los
enlaces, y eso se cuenta sin una sola frase que lo explique.

La última pausa se gana: al avanzar, la señal entra por las tres aristas, la
neurona la acusa, sale por la flecha y la tarjeta late al recibirla. Ahí se
queda la pantalla, con el QR puesto, mientras la gente pregunta.

Press Start 2P no trae acentos ni signos de apertura —lo mismo le pasa al
título de la portada, que dice «COMO» y no «CÓMO»—, así que el agradecimiento
va en mayúsculas y sin ellos.
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
    FadeOut,
    GrowFromCenter,
    Group,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    RoundedRectangle,
    VGroup,
    VMobject,
    there_and_back,
)

from componentes import imagen, separador, texto
from estilo import (
    AMBAR,
    BLANCO,
    CLARO,
    FONT_TITULO,
    MORADO,
    PRIMARIO,
    SECUNDARIO,
)

RELLENO_NODO = "#04121a"     # el mismo de la portada

# --- Cabecera --------------------------------------------------------------
Y_GRACIAS = 2.55
ANCHO_MAX_GRACIAS = 9.6

# --- El perceptrón que desemboca en el QR ----------------------------------
X_ENTRADAS = -5.75
Y_ENTRADAS = (0.35, -0.75, -1.85)
RADIO_ENTRADA = 0.27
CENTRO_CUERPO = np.array([-3.0, -0.75, 0.0])
RADIO_CUERPO = 0.8

# --- El QR -----------------------------------------------------------------
X_QR = 3.7
Y_QR = -0.75
LADO_TARJETA = 3.0
MARGEN_QR = 0.34         # zona de silencio: sin ella los lectores fallan


def _m(tex, color, escala=0.55):
    return MathTex(tex, color=color).scale(escala)


def _cuerpo():
    """El cuerpo de la neurona: Σ a la izquierda y el codo de ReLU a la derecha.

    Copiado de la portada a propósito: es la misma neurona con la que empezó
    la charla, y reconocerla es la mitad del chiste.
    """
    cx, cy, _ = CENTRO_CUERPO
    disco = Circle(radius=RADIO_CUERPO, color=PRIMARIO, stroke_width=4)
    disco.set_fill(RELLENO_NODO, opacity=1.0).move_to(CENTRO_CUERPO)
    divisor = Line(
        [cx, cy - RADIO_CUERPO + 0.06, 0], [cx, cy + RADIO_CUERPO - 0.06, 0],
        color=SECUNDARIO, stroke_width=1.5,
    ).set_stroke(opacity=0.55)
    sigma = _m(r"\Sigma", CLARO, 0.75).move_to([cx - 0.36, cy, 0])

    origen = np.array([cx + 0.34, cy - 0.18, 0])
    eje = Line(origen + LEFT * 0.24, origen + RIGHT * 0.34,
               color=SECUNDARIO, stroke_width=1.3).set_stroke(opacity=0.6)
    codo = VMobject(color=MORADO, stroke_width=3)
    codo.set_points_as_corners(
        [origen + LEFT * 0.22, origen, origen + np.array([0.3, 0.5, 0])],
    )
    return VGroup(disco, divisor, sigma, eje, codo)


def _entradas():
    """Las tres entradas con su peso, y el sesgo colgando por arriba."""
    nodos, aristas, pesos = VGroup(), VGroup(), VGroup()
    for i, y in enumerate(Y_ENTRADAS):
        centro = np.array([X_ENTRADAS, y, 0.0])
        nodo = Circle(radius=RADIO_ENTRADA, color=SECUNDARIO, stroke_width=3)
        nodo.set_fill(RELLENO_NODO, opacity=1.0).move_to(centro)
        nodos.add(VGroup(nodo, _m(f"x_{i + 1}", CLARO, 0.45).move_to(centro)))

        direccion = CENTRO_CUERPO - centro
        direccion = direccion / np.linalg.norm(direccion)
        arista = Line(
            centro + direccion * RADIO_ENTRADA,
            CENTRO_CUERPO - direccion * RADIO_CUERPO,
            color=PRIMARIO, stroke_width=2.5,
        ).set_stroke(opacity=0.85)
        aristas.add(arista)
        pesos.add(_m(f"w_{i + 1}", SECUNDARIO, 0.42).move_to(
            arista.point_from_proportion(0.45) + UP * 0.22,
        ))
    return nodos, aristas, pesos


def _sesgo():
    cx, cy, _ = CENTRO_CUERPO
    centro = np.array([cx, cy + RADIO_CUERPO + 0.78, 0.0])
    nodo = Circle(radius=0.23, color=AMBAR, stroke_width=3)
    nodo.set_fill(RELLENO_NODO, opacity=1.0).move_to(centro)
    etiqueta = _m("b", AMBAR, 0.45).move_to(centro)
    cable = Line(
        centro + DOWN * 0.23, CENTRO_CUERPO + UP * RADIO_CUERPO,
        color=AMBAR, stroke_width=2.5,
    ).set_stroke(opacity=0.85)
    return VGroup(nodo, etiqueta), cable


def construir(scene):
    # --- Cabecera ----------------------------------------------------------
    gracias = VGroup(
        texto("MUCHAS", 46, color=CLARO, font=FONT_TITULO),
        texto("GRACIAS", 46, color=PRIMARIO, font=FONT_TITULO),
    ).arrange(RIGHT, buff=0.45)
    if gracias.width > ANCHO_MAX_GRACIAS:
        gracias.scale(ANCHO_MAX_GRACIAS / gracias.width)
    gracias.move_to([0, Y_GRACIAS, 0])

    raya = separador(largo=3.6, grosor=2.5)
    raya.set_stroke(opacity=0.5).next_to(gracias, DOWN, buff=0.42)
    cortesia = texto("por tu atencion y tus preguntas", 20, color=SECUNDARIO)
    cortesia.next_to(raya, DOWN, buff=0.3)

    # --- El perceptrón -----------------------------------------------------
    nodos, aristas, pesos = _entradas()
    cuerpo = _cuerpo()
    nodo_sesgo, cable_sesgo = _sesgo()

    # --- El QR, que hace de salida -----------------------------------------
    papel = RoundedRectangle(
        width=LADO_TARJETA, height=LADO_TARJETA, corner_radius=0.2,
        stroke_color=PRIMARIO, stroke_width=3,
    ).set_fill(BLANCO, opacity=1.0).move_to([X_QR, Y_QR, 0])
    codigo = imagen("qr_links.png")
    codigo.scale_to_fit_width(LADO_TARJETA - MARGEN_QR * 2)
    codigo.move_to(papel.get_center())
    tarjeta = Group(papel, codigo)

    salida = Arrow(
        CENTRO_CUERPO + RIGHT * RADIO_CUERPO,
        papel.get_left() + LEFT * 0.12,
        color=PRIMARIO, stroke_width=4, buff=0.1,
        max_tip_length_to_length_ratio=0.06,
    )
    # --- La firma, abajo ---------------------------------------------------
    firma = texto("Semillero de Data Science e IA  ·  Aperture", 17,
                  color=SECUNDARIO)
    firma.move_to([-2.6, -3.15, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(gracias[0], shift=UP * 0.18), run_time=0.5)
    scene.play(FadeIn(gracias[1], shift=UP * 0.18), run_time=0.5)
    scene.play(Create(raya), run_time=0.4)
    scene.play(FadeIn(cortesia, shift=UP * 0.1), run_time=0.5)

    # La neurona se arma como en la portada, de la entrada a la salida.
    scene.play(
        LaggedStart(*[GrowFromCenter(n) for n in nodos], lag_ratio=0.18),
        run_time=0.8,
    )
    scene.play(
        LaggedStart(*[Create(a) for a in aristas], lag_ratio=0.2),
        FadeIn(pesos), run_time=0.9,
    )
    scene.play(GrowFromCenter(cuerpo), run_time=0.6)
    scene.play(GrowFromCenter(nodo_sesgo), Create(cable_sesgo), run_time=0.5)
    scene.play(Create(salida), run_time=0.6)
    scene.play(GrowFromCenter(papel), run_time=0.6)
    scene.play(FadeIn(codigo, scale=0.85), run_time=0.5)
    scene.play(FadeIn(firma, shift=UP * 0.1), run_time=0.5)

    # --- Y el disparo final ------------------------------------------------
    # La señal entra, la neurona la suma, sale por la flecha y la tarjeta
    # late: la charla entera, en un gesto, desembocando en el QR.
    scene.next_slide()
    caminos = (*aristas, cable_sesgo)
    pulsos = [Dot(color=CLARO, radius=0.055).move_to(c.get_start())
              for c in caminos]
    pulsos[-1].set_color(AMBAR)
    chispa = Dot(color=CLARO, radius=0.06).move_to(salida.get_start())

    # Entran y salen con fundido, nunca de golpe: aparecer de la nada delata
    # que son puntos dibujados y no una señal que llega.
    scene.play(*[FadeIn(p, scale=0.4) for p in pulsos], run_time=0.25)
    scene.play(
        *[MoveAlongPath(p, c) for p, c in zip(pulsos, caminos)],
        run_time=1.1,
    )
    scene.play(
        *[FadeOut(p, scale=0.2) for p in pulsos],
        cuerpo[0].animate(rate_func=there_and_back).set_stroke(width=7),
        FadeIn(chispa, scale=0.4),
        run_time=0.5,
    )
    scene.remove(*pulsos)
    scene.play(MoveAlongPath(chispa, salida), run_time=0.9)
    scene.play(
        FadeOut(chispa, scale=0.2),
        tarjeta.animate(rate_func=there_and_back).scale(1.06),
        run_time=0.8,
    )
    scene.remove(chispa)

    # Sin indicador: es la última pausa de la charla —no queda nada que
    # anunciar— y además su animación de entrada caería dentro del bucle, con
    # el logo parpadeando en cada vuelta.
    scene.next_slide(indicador=False)
