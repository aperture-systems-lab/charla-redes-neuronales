"""Diapositiva 17 — ¿Y si hay que decidir?

Dos actos con la misma red: lo único que cambia es lo que le entra.

Acto 1, regresión: le enseñamos una casa y sale 240 €. Eso es la respuesta, tal
cual. Es lo que llevamos toda la charla haciendo y funciona.

Acto 2, clasificación: le enseñamos un gato. La red no sabe hacer otra cosa que
dar un número, así que da un número: 2.7. ¿Y eso qué es? No hay forma de leerlo
—en la recta no hay ninguna marca que diga de dónde para allá es que sí—, así
que se dibujan tres cortes posibles, todos igual de defendibles, y ahí se queda
la pregunta. La respuesta es la diapositiva siguiente.

Va sin apenas letra: la pregunta la hace un dibujo (la casa, el gato) en vez de
una frase, y lo que queda son la red, el número y la recta. En el acto 1 la red
va a lo grande, porque no comparte pantalla con nada; al entrar el acto 2 se
encoge y sube para dejarle sitio abajo a la recta. Ese encogerse es la propia
transición entre los dos actos.
"""

import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    ManimColor,
    MoveAlongPath,
    Polygon,
    Rectangle,
    Transform,
    VGroup,
    interpolate_color,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, FONDO, MORADO, PRIMARIO, ROJO, SECUNDARIO, VERDE

# --- La fila: dibujo → red → número ----------------------------------------
# Las medidas de abajo son las del acto 2. El acto 1 es la misma fila a
# ``K_ACTO1``, centrada en pantalla; el ancho es lo que pone el techo al
# aumento, no el alto.
CX = 0.0               # eje sobre el que se escala la fila
K_ACTO1 = 1.6
K_ACTO2 = 0.9
Y_ACTO1 = -0.6         # centro óptico de lo que deja libre el título
Y_FILA = 0.85

# Las x van cuadradas para que la fila quede centrada en pantalla a escala 1.
X_ICONO = -3.49
X_CAPAS = (-2.29, -1.29, -0.29, 0.71)   # entrada, dos ocultas y salida
CAPAS = (4, 6, 6, 1)
PASO_NODO = 0.5
RADIOS = (0.16, 0.15, 0.15, 0.21)
X_FLECHA = (1.01, 2.06)
X_NUMERO = 3.06

# --- La recta de abajo -----------------------------------------------------
Y_RECTA = -2.75
V_MIN, V_MAX = -1, 4
V_CENTRO = 1.5          # qué valor cae en x = 0
ESCALA = 1.4            # unidades de pantalla por unidad de la recta
SALIDA = 2.7            # lo que responde la red al enseñarle el gato
CORTES = (0, 1, 2)      # los tres sitios donde sería razonable partirla


def _x(valor):
    """Sitio en pantalla del valor ``valor`` de la recta."""
    return (valor - V_CENTRO) * ESCALA


def _px(x, k):
    """Una x de la fila, escalada respecto al eje ``CX``."""
    return CX + (x - CX) * k


def _punto(x, dy, y, k):
    """Un punto de la fila: ``x`` de la tabla, ``dy`` respecto a su línea."""
    return np.array([_px(x, k), y + dy * k, 0.0])


def _colores_capa():
    """De cian a violeta por las ocultas, y ámbar en la salida.

    La misma idea que en las diapositivas del ajuste: el color dice por dónde
    va la señal, y el ámbar de la salida es el de siempre.
    """
    a, b = ManimColor(PRIMARIO), ManimColor(MORADO)
    return [a, interpolate_color(a, b, 0.5), b, ManimColor(AMBAR)]


def _nodo(centro, color, radio):
    """Nodo plano, sin halo: circunferencia rellena del fondo."""
    return Circle(radius=radio, color=color, stroke_width=2.8).set_fill(
        FONDO, opacity=1.0
    ).move_to(centro)


def _casa(color, k):
    """La pregunta del acto 1, dibujada: ¿cuánto cuesta esta casa?"""
    casa = VGroup(
        Polygon([-0.52, 0.1, 0], [0.0, 0.58, 0], [0.52, 0.1, 0],
                color=color, stroke_width=3),
        Rectangle(width=0.82, height=0.62, color=color, stroke_width=3)
        .move_to([0.0, -0.21, 0]),
        Rectangle(width=0.22, height=0.3, color=color, stroke_width=2.4)
        .move_to([-0.16, -0.37, 0]),
        Rectangle(width=0.2, height=0.2, color=color, stroke_width=2.4)
        .move_to([0.19, -0.09, 0]),
    )
    return casa.scale(k)


def _gato(color, k):
    """La pregunta del acto 2, dibujada: ¿esto es un gato?"""
    gato = VGroup(
        Circle(radius=0.42, color=color, stroke_width=3),
        VGroup(*[
            Polygon([lado * 0.40, 0.17, 0], [lado * 0.30, 0.62, 0],
                    [lado * 0.10, 0.36, 0], color=color, stroke_width=3)
            for lado in (-1, 1)
        ]),
        VGroup(*[
            Dot([lado * 0.16, 0.07, 0], radius=0.045, color=color)
            for lado in (-1, 1)
        ]),
        Polygon([-0.07, -0.09, 0], [0.07, -0.09, 0], [0.0, -0.19, 0],
                color=color, stroke_width=2.2),
        VGroup(*[
            Line([lado * 0.12, -0.13 + alto, 0],
                 [lado * 0.52, -0.09 + alto * 1.8, 0],
                 color=color, stroke_width=1.8).set_stroke(opacity=0.8)
            for lado in (-1, 1) for alto in (0.06, -0.05)
        ]),
    )
    return gato.scale(k)


def _red(y, k):
    """La red entera: cuatro entradas, dos capas ocultas y una salida.

    Se dibuja completa —es la protagonista de los dos actos— con cada capa de
    su color y las conexiones tomando el del extremo del que salen, que es lo
    que hace que la malla se lea y no sea una maraña gris.
    """
    colores = _colores_capa()
    columnas = [
        [
            _punto(x, (n - 1) / 2 * PASO_NODO - j * PASO_NODO, y, k)
            for j in range(n)
        ]
        for x, n in zip(X_CAPAS, CAPAS)
    ]
    nodos = VGroup(*[
        VGroup(*[_nodo(c, colores[i], RADIOS[i] * k) for c in columna])
        for i, columna in enumerate(columnas)
    ])

    tramos = []
    for i, (izq, der) in enumerate(zip(columnas, columnas[1:])):
        tramo = VGroup()
        for a in izq:
            for b in der:
                direccion = (b - a) / np.linalg.norm(b - a)
                tramo.add(Line(
                    a + direccion * RADIOS[i] * k,
                    b - direccion * RADIOS[i + 1] * k,
                    color=colores[i], stroke_width=1.3,
                ).set_stroke(opacity=0.3))
        tramos.append(tramo)
    return nodos, VGroup(*tramos), tramos, colores


def _flecha(y, k):
    return Arrow(
        _punto(X_FLECHA[0], 0, y, k), _punto(X_FLECHA[1], 0, y, k),
        color=SECUNDARIO, stroke_width=3, buff=0,
        max_tip_length_to_length_ratio=0.16,
    ).set_stroke(opacity=0.7)


def _bloque(y, k, dibujo, etiqueta, valor, color_valor):
    """Coloca las piezas que rodean a la red, a la altura y escala dadas."""
    dibujo.move_to(_punto(X_ICONO, 0.12, y, k))
    pie = texto(etiqueta, 19, color=SECUNDARIO).scale(k)
    pie.move_to(_punto(X_ICONO, -0.95, y, k))
    numero = texto(valor, 40, color=color_valor).scale(k)
    numero.move_to(_punto(X_NUMERO, 0, y, k))
    return dibujo, pie, numero


def construir(scene):
    encabezado = hacer_titulo("¿Y si hay que decidir?")

    # --- Acto 1: la regresión, que ya sabemos hacer ------------------------
    nodos, aristas, tramos, colores = _red(Y_ACTO1, K_ACTO1)
    flecha = _flecha(Y_ACTO1, K_ACTO1)
    casa, pie, respuesta = _bloque(
        Y_ACTO1, K_ACTO1, _casa(PRIMARIO, K_ACTO1), "¿cuánto?",
        "240 €", VERDE,
    )

    # --- Acto 2, primero en grande: el gato y el número que da la red ------
    gato, pie_2, respuesta_2 = _bloque(
        Y_ACTO1, K_ACTO1, _gato(PRIMARIO, K_ACTO1), "¿gato?",
        f"{SALIDA}", AMBAR,
    )

    # --- Y ya luego encogido, para que quepa la recta ----------------------
    nodos_3, aristas_3, _, _ = _red(Y_FILA, K_ACTO2)
    flecha_3 = _flecha(Y_FILA, K_ACTO2)
    gato_3, pie_3, respuesta_3 = _bloque(
        Y_FILA, K_ACTO2, _gato(PRIMARIO, K_ACTO2), "¿gato?",
        f"{SALIDA}", AMBAR,
    )

    # La recta donde vive ese número, sin ninguna marca que diga qué es mucho.
    recta = Line(
        np.array([_x(V_MIN) - 0.3, Y_RECTA, 0]),
        np.array([_x(V_MAX) + 0.3, Y_RECTA, 0]),
        color=SECUNDARIO, stroke_width=2.5,
    )
    marcas = VGroup()
    for valor in range(V_MIN, V_MAX + 1):
        marcas.add(
            Line(np.array([_x(valor), Y_RECTA - 0.09, 0]),
                 np.array([_x(valor), Y_RECTA + 0.09, 0]),
                 color=SECUNDARIO, stroke_width=2),
            texto(str(valor), 16, color=SECUNDARIO).move_to(
                [_x(valor), Y_RECTA - 0.34, 0]
            ),
        )

    punto = Dot(np.array([_x(SALIDA), Y_RECTA, 0]), radius=0.09, color=AMBAR)
    etiqueta_punto = texto(f"{SALIDA}", 20, color=AMBAR).move_to(
        [_x(SALIDA), Y_RECTA + 0.38, 0]
    )
    bajada = DashedLine(
        respuesta_3.get_bottom() + DOWN * 0.2,
        np.array([_x(SALIDA), Y_RECTA + 0.6, 0]),
        color=AMBAR, stroke_width=1.8, dash_length=0.09,
    ).set_stroke(opacity=0.4)

    # Tres sitios por donde partir, todos igual de defendibles.
    cortes = VGroup(*[
        VGroup(
            DashedLine(
                np.array([_x(valor), Y_RECTA - 0.55, 0]),
                np.array([_x(valor), Y_RECTA + 0.62, 0]),
                color=ROJO, stroke_width=2, dash_length=0.08,
            ).set_stroke(opacity=0.65),
            texto("?", 26, color=ROJO).move_to([_x(valor), Y_RECTA + 0.92, 0]),
        )
        for valor in CORTES
    ])

    def _oleada():
        """La señal atravesando la red, un tramo detrás de otro."""
        for i, tramo in enumerate(tramos):
            pulsos = [
                Dot(color=colores[i], radius=0.055).move_to(a.get_start())
                for a in tramo
            ]
            scene.add(*pulsos)
            scene.play(
                *[MoveAlongPath(p, a) for p, a in zip(pulsos, tramo)],
                run_time=0.32, rate_func=linear,
            )
            scene.remove(*pulsos)

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(
        LaggedStart(*[FadeIn(c, scale=0.5) for c in nodos], lag_ratio=0.15),
        run_time=1.0,
    )
    scene.play(Create(aristas), run_time=0.9)
    scene.play(FadeIn(casa, shift=RIGHT * 0.2), FadeIn(pie), run_time=0.7)
    _oleada()
    scene.play(
        Create(flecha), FadeIn(respuesta, shift=RIGHT * 0.2),
        run_time=0.7,
    )
    scene.next_slide()

    # Misma red, otra pregunta. Se queda en grande: lo que hay que mirar ahora
    # es el número que sale, no la red. Y se recorre otra vez entera, porque es
    # exactamente la misma cuenta de antes: nada de la red ha cambiado.
    scene.play(
        FadeOut(casa, shift=UP * 0.3), FadeIn(gato, shift=UP * 0.3),
        Transform(pie, pie_2),
        FadeOut(respuesta),
        run_time=0.8,
    )
    _oleada()
    scene.play(FadeIn(respuesta_2, shift=RIGHT * 0.2), run_time=0.7)
    scene.next_slide()

    # Y ahora sí, todo se encoge y sube para dejarle sitio abajo a la recta.
    scene.play(
        Transform(nodos, nodos_3), Transform(aristas, aristas_3),
        Transform(flecha, flecha_3),
        Transform(gato, gato_3),
        Transform(pie, pie_3),
        Transform(respuesta_2, respuesta_3),
        run_time=1.0,
    )
    scene.play(Create(recta), FadeIn(marcas), run_time=0.8)
    scene.play(
        Create(bajada), FadeIn(punto, scale=0.4), FadeIn(etiqueta_punto),
        run_time=0.7,
    )
    scene.play(
        LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cortes],
                    lag_ratio=0.22),
        run_time=1.0,
    )
    scene.wait(0.5)

    scene.next_slide()
