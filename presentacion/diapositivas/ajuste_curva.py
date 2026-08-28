"""Diapositiva 14 — La red se ajusta a una curva.

Con la activación puesta, la salida de la red deja de ser una recta. Aquí se ve
literalmente cómo se ajusta, con el montaje de las visualizaciones de nnfs.io
(la demo ``ReLU activation (1, 64, 64, 1)``): la red a la izquierda y, a la
derecha, la curva objetivo con el ajuste encima.

Del original se copian tres cosas. Dibujo **plano**: nada de resplandores, solo
trazo limpio sobre el fondo. **Un color por papel**, no un color para todo: ejes
en azul acero, objetivo en verde y el ajuste en un degradado de ámbar a violeta
que es el mismo que toman las neuronas al encenderse. Y, sobre todo, la forma de
ajustarse: la salida de la red **ocupa el ancho entero desde el principio** y se
va moldeando, no se dibuja por pedazos dejando el resto sin hacer. Empieza
plana —todos los pesos a cero, la red no dice nada—, luego es un zigzag basto de
dos picos y de ahí se va pegando a la sinusoide.

Cada pareja de neuronas aporta un pliegue, y los pliegues no entran en orden de
izquierda a derecha sino por importancia: primero los dos picos, después el
cruce del centro y al final el detalle. Eso es lo que hace que la curva parezca
moldearse en vez de barrerse, y de paso enseña de dónde sale la capacidad de la
red: de acumular neuronas, cada una doblando un poco más la recta.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    ManimColor,
    MathTex,
    MoveAlongPath,
    Transform,
    VGroup,
    VMobject,
    interpolate_color,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, SECUNDARIO, VERDE

# El bloque entero va por debajo del eje del frame: arriba manda el título, así
# que el centro óptico de lo que queda es ``Y_CENTRO``, no el cero.
Y_CENTRO = -0.3
Y_PIE = -2.92      # rótulos de las capas y leyenda, a la misma altura

# --- La red, a la izquierda ------------------------------------------------
X_CAPAS = (-6.3, -4.75, -3.2, -1.65)   # entrada, dos ocultas y salida
Y_RED = Y_CENTRO
N_PAREJAS = 8
PASO_NEURONA = 0.56
RADIO_EXTREMO = 0.24
RADIO_OCULTA = 0.16

# --- La gráfica, a la derecha ----------------------------------------------
CENTRO_GRAFICA = [3.3, Y_CENTRO, 0]

# Los pliegues repartidos por el interior del tramo, uno por pareja.
X_PLIEGUES = [(i + 1) / (N_PAREJAS + 1) for i in range(N_PAREJAS)]

# La curva se muestrea en múltiplos de 1/144 y se corta en ocho bandas de color:
# 144 es divisible por 9 (los pliegues caen clavados en una muestra, así que los
# picos salen afilados) y por 8 (cada banda lleva las mismas 19 muestras, y así
# ``Transform`` mueve punto contra punto en vez de redibujar).
MUESTRAS = 144
POR_BANDA = MUESTRAS // N_PAREJAS

# En qué orden se ponen: los dos picos, luego el cruce del centro y al final el
# detalle. Barrer de izquierda a derecha se vería como un dibujo que avanza; así
# se ve una recta que se dobla, que es lo que hace de verdad la red.
ORDEN = (1, 6, 3, 4, 0, 2, 5, 7)


def _objetivo(x):
    """La curva que hay que aproximar: un seno completo entre 0 y 1."""
    return np.sin(2 * np.pi * x)


def _paleta():
    """Un color por pareja, de ámbar a violeta según baja por la capa.

    La rampa va en el mismo orden que la gráfica (arriba→abajo es
    izquierda→derecha), así que el degradado del dibujo y el de la curva son el
    mismo y se leen juntos. Arranca en ámbar y no en cian a propósito: el cian
    se confunde con el verde del objetivo justo donde el ajuste se le encima.
    """
    a, b = ManimColor(AMBAR), ManimColor(MORADO)
    return [
        interpolate_color(a, b, k / (N_PAREJAS - 1)) for k in range(N_PAREJAS)
    ]


def _neurona(centro, radio, color, opacidad=1.0, con_relu=False):
    """Nodo plano: circunferencia rellena del fondo, sin halos ni resplandor.

    Las ocultas llevan además su codo de ReLU dentro, el mismo de la
    diapositiva anterior, para que se reconozca qué hay en cada una.
    """
    cuerpo = Circle(radius=radio, color=color, stroke_width=3)
    cuerpo.set_fill(FONDO, opacity=1.0).move_to(centro)
    piezas = VGroup(cuerpo)
    if con_relu:
        codo = centro + np.array([-0.01, -radio * 0.34, 0.0])
        piezas.add(
            Line(codo + LEFT * radio * 0.54, codo, color=color, stroke_width=2),
            Line(codo, codo + np.array([radio * 0.52, radio * 0.8, 0]),
                 color=color, stroke_width=2),
        )
    return piezas.set_stroke(opacity=opacidad)


def _extremo(centro, color, simbolo):
    """Nodo de entrada o de salida, con su símbolo dentro."""
    nodo = _neurona(centro, RADIO_EXTREMO, color)
    etiqueta = MathTex(simbolo, color=color).scale(0.55).move_to(centro)
    return VGroup(nodo, etiqueta)


def _arista(desde, hasta, radio_desde, radio_hasta):
    """Conexión recortada al borde de los nodos, apagada: el peso aún es cero."""
    direccion = hasta - desde
    direccion = direccion / np.linalg.norm(direccion)
    linea = Line(
        desde + direccion * radio_desde, hasta - direccion * radio_hasta,
        color=SECUNDARIO, stroke_width=1.8,
    )
    return linea.set_stroke(opacity=0.18)


def _red():
    """Entrada, dos capas ocultas emparejadas y salida.

    Las ocultas se conectan una a una, no todas con todas: así se ve que cada
    pareja pone un pliegue, que es de lo que trata la diapositiva. Nacen
    apagadas —azul acero tenue— y solo se tiñen cuando les toca doblar.
    """
    centro_entrada = np.array([X_CAPAS[0], Y_RED, 0.0])
    centro_salida = np.array([X_CAPAS[-1], Y_RED, 0.0])
    entrada = _extremo(centro_entrada, PRIMARIO, "x")
    salida = _extremo(centro_salida, AMBAR, r"\hat{y}")

    alto = (N_PAREJAS - 1) * PASO_NEURONA
    columnas = [
        [
            np.array([x, Y_RED + alto / 2 - k * PASO_NEURONA, 0.0])
            for k in range(N_PAREJAS)
        ]
        for x in X_CAPAS[1:3]
    ]
    ocultas = [
        [
            _neurona(c, RADIO_OCULTA, SECUNDARIO, opacidad=0.45, con_relu=True)
            for c in columna
        ]
        for columna in columnas
    ]

    entrantes = [
        _arista(centro_entrada, c, RADIO_EXTREMO, RADIO_OCULTA)
        for c in columnas[0]
    ]
    medias = [
        _arista(a, b, RADIO_OCULTA, RADIO_OCULTA)
        for a, b in zip(columnas[0], columnas[1])
    ]
    salientes = [
        _arista(c, centro_salida, RADIO_OCULTA, RADIO_EXTREMO)
        for c in columnas[1]
    ]

    rotulos = VGroup(*[
        texto(nombre, 15, color=SECUNDARIO).move_to([x, Y_PIE, 0])
        for x, nombre in zip(X_CAPAS, ("entrada", "capa 1", "capa 2", "salida"))
    ])
    return entrada, salida, ocultas, (entrantes, medias, salientes), rotulos


def construir(scene):
    encabezado = hacer_titulo("Ahora sí puede curvarse")
    colores = _paleta()

    entrada, salida, ocultas, conexiones, rotulos = _red()
    entrantes, medias, salientes = conexiones

    # Ejes al estilo de nnfs: eje x con punta, eje y como una barra rematada por
    # las marcas de +1 y -1. Sin retícula: la curva es lo único que importa.
    ejes = Axes(
        x_range=[0, 1, 0.25], y_range=[-1.35, 1.35, 0.5],
        x_length=6.0, y_length=4.3,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5, "include_ticks": False,
        },
        x_axis_config={"tip_width": 0.16, "tip_height": 0.16},
        y_axis_config={"include_tip": False},
    ).move_to(CENTRO_GRAFICA)

    marcas = VGroup()
    for valor in (1, -1):
        marca = Line(
            ejes.c2p(0, valor) + LEFT * 0.12, ejes.c2p(0, valor) + RIGHT * 0.12,
            color=SECUNDARIO, stroke_width=2.5,
        )
        etiqueta = MathTex(str(valor), color=SECUNDARIO).scale(0.5)
        etiqueta.next_to(marca, LEFT, buff=0.12)
        marcas.add(marca, etiqueta)
    rot_x = MathTex("x", color=SECUNDARIO).scale(0.6)
    rot_x.next_to(ejes.c2p(1, 0), UP + RIGHT, buff=0.1)
    rot_y = MathTex("y", color=SECUNDARIO).scale(0.6)
    rot_y.next_to(ejes.c2p(0, 1.35), UP, buff=0.06)

    objetivo = ejes.plot(_objetivo, x_range=[0, 1], color=VERDE)
    objetivo.set_stroke(width=4)

    def _ajuste(activos):
        """La salida de la red con los pliegues ``activos`` puestos.

        Siempre de 0 a 1 y siempre con el mismo número de puntos: lo que cambia
        de un paso al siguiente es la altura de cada uno, así que ``Transform``
        la moldea de verdad en vez de redibujarla.

        El degradado va a mano, en bandas de color sólido, y no con
        ``set_color_by_gradient``: sobre un trazo hecho de esquinas manim no lo
        pinta. Las juntas entre bandas caen siempre en tramo recto —los octavos
        y los novenos solo coinciden en los extremos—, así que no se notan.
        """
        nodos_x = [0.0] + sorted(X_PLIEGUES[i] for i in activos) + [1.0]
        nodos_y = [_objetivo(x) for x in nodos_x]
        xs = np.linspace(0, 1, MUESTRAS + 1)
        ys = np.interp(xs, nodos_x, nodos_y)
        puntos = [ejes.c2p(x, y) for x, y in zip(xs, ys)]

        bandas = VGroup()
        for j in range(N_PAREJAS):
            banda = VMobject(color=colores[j], stroke_width=5)
            banda.set_points_as_corners(
                puntos[j * POR_BANDA:(j + 1) * POR_BANDA + 1]
            )
            bandas.add(banda)
        return bandas

    pliegues = [
        Dot(ejes.c2p(x, _objetivo(x)), radius=0.055, color=colores[i])
        for i, x in enumerate(X_PLIEGUES)
    ]

    # Leyenda: el objetivo es de un color, el ajuste es de ocho.
    vertices_muestra = [
        np.array([-0.33, -0.06, 0]), np.array([-0.11, 0.07, 0]),
        np.array([0.11, -0.05, 0]), np.array([0.33, 0.06, 0]),
    ]
    muestra_ajuste = VGroup(*[
        Line(vertices_muestra[j], vertices_muestra[j + 1],
             color=colores[j * 3 + 1], stroke_width=4)
        for j in range(3)
    ])
    leyenda = VGroup(
        VGroup(
            Line(LEFT * 0.28, RIGHT * 0.28, color=VERDE, stroke_width=4),
            texto("objetivo", 17, color=SECUNDARIO),
        ).arrange(RIGHT, buff=0.2),
        VGroup(
            muestra_ajuste, texto("salida de la red", 17, color=SECUNDARIO),
        ).arrange(RIGHT, buff=0.2),
    ).arrange(RIGHT, buff=0.75)
    leyenda.move_to([CENTRO_GRAFICA[0], Y_PIE, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(
        FadeIn(entrada), FadeIn(salida),
        LaggedStart(*[FadeIn(o, scale=0.5) for columna in ocultas
                      for o in columna], lag_ratio=0.04),
        run_time=1.2,
    )
    scene.play(
        LaggedStart(*[Create(a) for a in (*entrantes, *medias, *salientes)],
                    lag_ratio=0.02),
        FadeIn(rotulos),
        run_time=1.0,
    )
    scene.play(
        Create(ejes), FadeIn(marcas), FadeIn(rot_x), FadeIn(rot_y),
        run_time=0.9,
    )
    scene.play(Create(objetivo), FadeIn(leyenda), run_time=1.1)

    # Todos los pesos a cero: la red no dice nada y la salida es una recta plana
    # que ya ocupa todo el ancho. A partir de aquí solo se dobla.
    ajuste = _ajuste([])
    scene.play(Create(ajuste), run_time=0.6)
    scene.next_slide()

    # Y ahora, un pliegue por pareja de neuronas.
    activos = []
    for i in ORDEN:
        activos.append(i)
        color = colores[i]
        scene.play(
            # Solo el trazo: ``set_color`` teñiría también el relleno y los
            # nodos pasarían de círculos a bolas macizas.
            *[ocultas[c][i].animate.set_stroke(color=color, opacity=1.0)
              for c in (0, 1)],
            *[a.animate.set_stroke(color=color, opacity=0.95, width=2.6)
              for a in (entrantes[i], medias[i], salientes[i])],
            Transform(ajuste, _ajuste(activos)),
            FadeIn(pliegues[i], scale=0.5),
            run_time=0.55,
        )

    # Los ocho aportes bajan por sus cables y se suman en la salida.
    pulsos = [
        Dot(color=colores[i], radius=0.06).move_to(salientes[i].get_start())
        for i in range(N_PAREJAS)
    ]
    scene.add(*pulsos)
    scene.play(
        LaggedStart(*[MoveAlongPath(p, a) for p, a in zip(pulsos, salientes)],
                    lag_ratio=0.05),
        run_time=0.9, rate_func=linear,
    )
    scene.play(
        *[FadeOut(p, scale=0.2) for p in pulsos],
        Indicate(salida, color=CLARO, scale_factor=1.3),
        run_time=0.5,
    )
    scene.play(
        LaggedStart(*[Indicate(p, color=CLARO, scale_factor=1.6)
                      for p in pliegues], lag_ratio=0.07),
        run_time=1.0,
    )
    scene.wait(0.4)

    scene.next_slide()
