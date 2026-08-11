"""Diapositiva 6 — El perceptrón.

Lo que Rosenblatt propuso, con las partes de la neurona biológica rotuladas
debajo y en el mismo código de color de la diapositiva 5: entradas en verde
(dendritas), cuerpo en cian (soma), salida en ámbar (axón). El bias se lleva
morado para no robarle el ámbar a la salida.

Importante: aquí **no hay función de activación**. El modelo es una suma
ponderada y nada más — es exactamente lo que hará que falle en la 7 y en la 8,
y el hueco que la 9 vendrá a señalar.
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
    GrowFromCenter,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    ReplacementTransform,
    TransformFromCopy,
    VGroup,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, SECUNDARIO, VERDE

X_ENTRADAS = -4.3
X_CUERPO = 0.0
X_SALIDA = 3.9
Y_EJE = 0.4
RADIO_CUERPO = 0.85
RADIO_NODO = 0.32
Y_ROTULOS = -1.75      # fila con los nombres de la neurona biológica
Y_FORMULA = -2.7    # el subíndice de \sum_i baja bastante: deja aire debajo

FILAS = ((1.7, "x_1", "w_1"), (0.4, "x_2", "w_2"), (-0.9, "x_n", "w_n"))

# La red del final: las entradas ya dibujadas más tres capas de perceptrones.
X_CAPAS = (-1.4, 1.5, 4.3)
TAMANOS_CAPAS = (4, 4, 2)
COLORES_CAPAS = (PRIMARIO, PRIMARIO, AMBAR)
PASO_RED = 1.15
RADIO_RED = 0.34
Y_NOMBRES = -2.15      # f_1 f_2 f_3, debajo de cada capa
Y_COMPOSICION = -3.15


def _m(tex, color, escala=0.6):
    return MathTex(tex, color=color).scale(escala)


def _nodo(centro, radio, color):
    """Círculo relleno del fondo para que las aristas no se vean por debajo."""
    nodo = Circle(radius=radio, color=color, stroke_width=3.5)
    return nodo.set_fill(FONDO, opacity=1.0).move_to(centro)


def _conexion(origen, destino):
    """Arista de la red, recortada en el borde de los dos nodos que une."""
    direccion = destino - origen
    direccion = direccion / np.linalg.norm(direccion)
    linea = Line(
        origen + direccion * RADIO_NODO, destino - direccion * RADIO_RED,
        color=SECUNDARIO, stroke_width=1.6,
    )
    return linea.set_stroke(opacity=0.45)


def _rotulo_biologico(nombre, color, x, ancla):
    """Nombre de la parte de la neurona, con guía discontinua hasta el diagrama."""
    etiqueta = texto(nombre, 19, color=color)
    etiqueta.move_to([x, Y_ROTULOS, 0])
    guia = DashedLine(
        etiqueta.get_top() + UP * 0.1, ancla,
        color=color, stroke_width=2, stroke_opacity=0.45, dash_length=0.09,
    )
    return etiqueta, guia


def construir(scene):
    encabezado = hacer_titulo("El perceptrón")
    centro = np.array([X_CUERPO, Y_EJE, 0.0])

    # --- Entradas ----------------------------------------------------------
    nodos, etiquetas_x, aristas, pesos = [], [], [], []
    for y, nombre_x, nombre_w in FILAS:
        nodo = _nodo([X_ENTRADAS, y, 0], RADIO_NODO, VERDE)
        nodos.append(nodo)
        etiquetas_x.append(_m(nombre_x, CLARO, 0.55).move_to(nodo.get_center()))

        direccion = centro - nodo.get_center()
        direccion = direccion / np.linalg.norm(direccion)
        arista = Line(
            nodo.get_center() + direccion * RADIO_NODO,
            centro - direccion * RADIO_CUERPO,
            color=SECUNDARIO, stroke_width=2.5,
        )
        aristas.append(arista)
        pesos.append(_m(nombre_w, VERDE, 0.5).move_to(
            arista.point_from_proportion(0.42) + UP * 0.26
        ))
    puntos_suspensivos = _m(r"\vdots", SECUNDARIO, 0.6)
    puntos_suspensivos.move_to([X_ENTRADAS, -0.28, 0])

    # --- Cuerpo: solo el sumatorio, sin activación -------------------------
    cuerpo = _nodo(centro, RADIO_CUERPO, PRIMARIO)
    cuerpo.set_stroke(width=4.5)
    sigma = _m(r"\Sigma", CLARO, 1.1).move_to(centro)

    # --- Bias ---------------------------------------------------------------
    centro_bias = np.array([X_CUERPO, 2.15, 0.0])
    nodo_bias = _nodo(centro_bias, 0.28, MORADO)
    etiqueta_bias = _m("b", MORADO, 0.55).move_to(centro_bias)
    direccion_bias = centro - centro_bias
    direccion_bias = direccion_bias / np.linalg.norm(direccion_bias)
    arista_bias = Line(
        centro_bias + direccion_bias * 0.28,
        centro - direccion_bias * RADIO_CUERPO,
        color=MORADO, stroke_width=2.5, stroke_opacity=0.9,
    )

    # --- Salida -------------------------------------------------------------
    flecha = Arrow(
        centro + RIGHT * RADIO_CUERPO, [X_SALIDA - 0.38, Y_EJE, 0],
        color=AMBAR, stroke_width=4, buff=0.05,
        max_tip_length_to_length_ratio=0.13,
    )
    salida = _nodo([X_SALIDA, Y_EJE, 0], 0.34, AMBAR)
    etiqueta_salida = _m(r"\hat{y}", AMBAR, 0.62).move_to(salida.get_center())

    # --- La analogía con la neurona biológica ------------------------------
    rot_dendritas, guia_dendritas = _rotulo_biologico(
        "dendritas", VERDE, X_ENTRADAS, [X_ENTRADAS, -0.9 - RADIO_NODO, 0],
    )
    rot_soma, guia_soma = _rotulo_biologico(
        "soma", PRIMARIO, X_CUERPO, [X_CUERPO, Y_EJE - RADIO_CUERPO, 0],
    )
    rot_axon, guia_axon = _rotulo_biologico(
        "axón", AMBAR, X_SALIDA, [X_SALIDA, Y_EJE - 0.34, 0],
    )

    # La suma escrita a mano, término a término, y la misma ya compactada. Los
    # índices de ``suma``: 0 ŷ, 1 =, 2 x1w1, 3 +, 4 x2w2, 5 +, 6 ⋯, 7 +,
    # 8 xnwn, 9 +, 10 b. Del 2 al 8 es lo que acaba colapsando en el sumatorio.
    suma = MathTex(
        r"\hat{y}", "=", "x_1 w_1", "+", "x_2 w_2", "+", r"\cdots", "+",
        "x_n w_n", "+", "b",
    ).scale(0.85).move_to([0, Y_FORMULA, 0])
    suma[0].set_color(AMBAR)
    suma[10].set_color(MORADO)

    compacta = MathTex(
        r"\hat{y}", "=", r"\sum_i x_i w_i", "+", "b",
    ).scale(0.95).move_to([0, Y_FORMULA, 0])
    compacta[0].set_color(AMBAR)
    compacta[2].set_color(CLARO)
    compacta[4].set_color(MORADO)

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(
        LaggedStart(*[GrowFromCenter(VGroup(n, e))
                      for n, e in zip(nodos, etiquetas_x)], lag_ratio=0.2),
        FadeIn(puntos_suspensivos),
        run_time=0.9,
    )
    scene.next_slide()

    # Cada entrada llega con su peso.
    scene.play(
        LaggedStart(*[Create(a) for a in aristas], lag_ratio=0.2),
        run_time=0.9,
    )
    scene.play(
        LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pesos], lag_ratio=0.2),
        run_time=0.7,
    )
    scene.play(GrowFromCenter(cuerpo), FadeIn(sigma), run_time=0.7)
    scene.next_slide()

    # Bias y salida.
    scene.play(
        GrowFromCenter(VGroup(nodo_bias, etiqueta_bias)), Create(arista_bias),
        run_time=0.6,
    )
    scene.play(Create(flecha), run_time=0.5)
    scene.play(GrowFromCenter(VGroup(salida, etiqueta_salida)), run_time=0.5)
    scene.next_slide()

    # La misma neurona de la 5, ahora en matemáticas.
    scene.play(
        LaggedStart(
            *[FadeIn(r) for r in (rot_dendritas, rot_soma, rot_axon)],
            *[Create(g) for g in (guia_dendritas, guia_soma, guia_axon)],
            lag_ratio=0.12,
        ),
        run_time=1.1,
    )
    scene.next_slide()

    # --- Cómo se hace la cuenta: una entrada, un sumando -------------------
    scene.play(FadeIn(VGroup(suma[0], suma[1])), run_time=0.4)

    # Cada entrada llega al cuerpo y deja su término escrito. Las piezas que
    # entran con cada una incluyen el "+" que la enlaza con la anterior.
    for arista, peso, trozos in zip(aristas, pesos, ([2], [3, 4], [5, 6, 7, 8])):
        pulso = Dot(color=VERDE, radius=0.07).move_to(arista.get_start())
        scene.add(pulso)
        scene.play(
            Indicate(peso, color=CLARO, scale_factor=1.35),
            MoveAlongPath(pulso, arista), run_time=0.55, rate_func=linear,
        )
        scene.play(
            Indicate(cuerpo, color=PRIMARIO, scale_factor=1.06),
            FadeOut(pulso, scale=0.2),
            FadeIn(VGroup(*[suma[t] for t in trozos]), shift=UP * 0.12),
            run_time=0.5,
        )

    # El bias entra por arriba y se suma igual que los demás.
    pulso_bias = Dot(color=MORADO, radius=0.07).move_to(arista_bias.get_start())
    scene.add(pulso_bias)
    scene.play(MoveAlongPath(pulso_bias, arista_bias), run_time=0.45,
               rate_func=linear)
    scene.play(
        Indicate(cuerpo, color=PRIMARIO, scale_factor=1.06),
        FadeOut(pulso_bias, scale=0.2),
        FadeIn(VGroup(suma[9], suma[10]), shift=UP * 0.12),
        run_time=0.5,
    )

    # Y el resultado sale por el axón.
    pulso_salida = Dot(color=AMBAR, radius=0.07).move_to(flecha.get_start())
    scene.add(pulso_salida)
    scene.play(MoveAlongPath(pulso_salida, flecha), run_time=0.5,
               rate_func=linear)
    scene.play(
        FadeOut(pulso_salida, scale=0.2),
        Indicate(VGroup(salida, etiqueta_salida), color=AMBAR),
        run_time=0.45,
    )
    scene.next_slide()

    # --- Y eso mismo, escrito corto ----------------------------------------
    # Los sumandos colapsan sobre el sumatorio mientras el Σ del cuerpo se
    # enciende: la notación y el dibujo dicen lo mismo.
    scene.play(
        Indicate(sigma, color=PRIMARIO, scale_factor=1.4),
        ReplacementTransform(suma[0], compacta[0]),
        ReplacementTransform(suma[1], compacta[1]),
        ReplacementTransform(VGroup(*suma[2:9]), compacta[2]),
        ReplacementTransform(suma[9], compacta[3]),
        ReplacementTransform(suma[10], compacta[4]),
        run_time=1.3,
    )
    scene.wait(0.4)
    scene.next_slide()

    # --- Y uno solo no hace nada: la red -----------------------------------
    # Las entradas se quedan donde están y el cuerpo que acabamos de estudiar
    # se encoge hasta ser el primero de una capa: la misma cuenta, repetida.
    # Los nodos de la red van vacíos: a este tamaño la Σ dentro de cada círculo
    # solo hace ruido, y lo que importa aquí ya no es la cuenta sino la forma.
    capas = [[n.get_center() for n in nodos]]
    nodos_red = []
    for x, cantidad, color in zip(X_CAPAS, TAMANOS_CAPAS, COLORES_CAPAS):
        centros = [
            np.array([x, Y_EJE + (cantidad - 1) / 2 * PASO_RED - k * PASO_RED, 0.0])
            for k in range(cantidad)
        ]
        capas.append(centros)
        nodos_red.append([_nodo(c, RADIO_RED, color) for c in centros])

    tramos = []
    for izquierda, derecha in zip(capas, capas[1:]):
        tramos.append(VGroup(*[
            _conexion(origen, destino) for origen in izquierda for destino in derecha
        ]))

    sobrantes = VGroup(
        compacta, rot_dendritas, rot_soma, rot_axon,
        guia_dendritas, guia_soma, guia_axon,
        *pesos, puntos_suspensivos, *aristas,
        nodo_bias, etiqueta_bias, arista_bias,
        flecha, salida, etiqueta_salida,
    )
    scene.play(FadeOut(sobrantes), run_time=0.7)

    # El perceptrón estudiado se convierte en el primer nodo de la capa oculta.
    scene.play(
        ReplacementTransform(cuerpo, nodos_red[0][0]),
        FadeOut(sigma, scale=0.3),
        run_time=0.9,
    )
    resto = [nodo for capa in nodos_red for nodo in capa][1:]
    scene.play(
        LaggedStart(*[FadeIn(p, scale=0.4) for p in resto], lag_ratio=0.07),
        run_time=1.3,
    )
    scene.play(
        LaggedStart(*[Create(c) for tramo in tramos for c in tramo],
                    lag_ratio=0.01),
        run_time=1.4,
    )
    scene.next_slide()

    # La señal atraviesa la red entera, capa por capa.
    for tramo, capa in zip(tramos, nodos_red):
        pulsos = [
            Dot(color=VERDE, radius=0.06).move_to(c.get_start()) for c in tramo
        ]
        scene.add(*pulsos)
        scene.play(
            *[MoveAlongPath(p, c) for p, c in zip(pulsos, tramo)],
            run_time=0.6, rate_func=linear,
        )
        scene.play(
            Indicate(VGroup(*capa), color=CLARO, scale_factor=1.1),
            *[FadeOut(p, scale=0.2) for p in pulsos],
            run_time=0.4,
        )
    scene.wait(0.4)
    scene.next_slide()

    # --- Leído de otra forma: funciones compuestas -------------------------
    # Cada capa es una función; la red entera es meterlas una dentro de otra.
    nombres = VGroup(*[
        _m(nombre, color, 0.75).move_to([x, Y_NOMBRES, 0])
        for nombre, color, x in zip(("f_1", "f_2", "f_3"), COLORES_CAPAS, X_CAPAS)
    ])
    scene.play(
        LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in nombres],
                    lag_ratio=0.25),
        run_time=0.9,
    )
    scene.next_slide()

    # Índices: 0 ŷ, 1 =, 2 f_3, 3 (, 4 f_2, 5 (, 6 f_1, 7 (, 8 x, 9-11 cierres.
    composicion = MathTex(
        r"\hat{y}", "=", "f_3", r"\big(", "f_2", r"\big(", "f_1", "(", "x",
        ")", r"\big)", r"\big)",
    ).scale(0.95).move_to([0, Y_COMPOSICION, 0])
    composicion[0].set_color(AMBAR)
    composicion[2].set_color(AMBAR)
    composicion[4].set_color(PRIMARIO)
    composicion[6].set_color(PRIMARIO)
    composicion[8].set_color(VERDE)

    scene.play(FadeIn(VGroup(composicion[0], composicion[1])), run_time=0.4)
    # Cada función baja desde su capa con su par de paréntesis, de fuera adentro.
    for capa, funcion, abre, cierra in ((2, 2, 3, 11), (1, 4, 5, 10), (0, 6, 7, 9)):
        scene.play(
            TransformFromCopy(nombres[capa], composicion[funcion]),
            FadeIn(VGroup(composicion[abre], composicion[cierra])),
            run_time=0.6,
        )
    scene.play(
        TransformFromCopy(VGroup(*etiquetas_x), composicion[8]), run_time=0.6,
    )
    scene.wait(0.4)

    scene.next_slide()
