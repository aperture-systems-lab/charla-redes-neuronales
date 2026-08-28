"""Diapositiva 7 — Del diagrama a las matemáticas: la recta.

Sin una palabra. La diapositiva se lee de izquierda a derecha, que es también la
dirección del argumento: **el modelo** a la izquierda, una flecha, y **lo que
dibuja** a la derecha.

  1. Una neurona recibe su señal, el pulso sale por la flecha y de ahí nace la
     recta que ajusta los puntos: la traza ella.
  2. Los mismos puntos se curvan. La neurona hace lo único que sabe —aplanar la
     recta— y los residuos en ámbar dejan ver que no llega.
  3. La neurona crece hasta ser una red entera, con las mismas entradas y la
     misma salida, y lo reintenta: la recta cambia de pendiente pero sigue
     siendo una recta, y los residuos siguen ahí.

El motivo —componer funciones lineales da otra función lineal— se dice de viva
voz; la diapositiva solo lo enseña. Deja el terreno listo para "Falta algo".
"""

import numpy as np
from manim import (
    DOWN,
    Arrow,
    Axes,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MoveAlongPath,
    ReplacementTransform,
    Transform,
    VGroup,
    linear,
)

from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, PRIMARIO, SECUNDARIO, VERDE

PENDIENTE = 0.5
ORDENADA = 0.75
VERTICE = 2.6        # centro de la parábola, en coordenadas de datos
NIVEL_PLANO = 1.45   # mejor recta posible para la parábola: casi horizontal
X_TRAZO = (0.15, 5.05)   # tramo de x donde se dibujan las rectas

# Columna izquierda: el modelo. Primero una neurona, después la red entera.
Y_MODELO = 0.35
X_CAPAS = (-6.05, -5.1, -4.15, -3.2)   # entradas, dos ocultas y salida
TAMANOS_CAPAS = (2, 3, 3, 1)
PASO_RED = 0.72
RADIO_ENTRADA = 0.16
RADIO_OCULTO = 0.22
RADIO_SALIDA = 0.2
RADIO_CUERPO = 0.44    # el cuerpo de la neurona, antes de volverse capa

# Columna derecha: lo que el modelo dibuja.
CENTRO_GRAFICA = [2.3, 0.0, 0]


def _datos():
    """Los mismos puntos, primero alineados y después curvados."""
    rng = np.random.default_rng(11)
    xs = np.linspace(0.35, 4.85, 11)
    ruido = rng.normal(0, 0.14, xs.size)
    return (xs,
            PENDIENTE * xs + ORDENADA + ruido,
            0.4 * (xs - VERTICE) ** 2 + 0.55 + ruido)


def _nodo(centro, radio, color, halo_factor=1.55):
    """Nodo con halo. El halo da cuerpo, pero pasado de tamaño mancha: en la
    red los de nodos vecinos se solapan y todo se vuelve una nube."""
    halo = Circle(radius=radio * halo_factor, color=color, stroke_width=0)
    halo.set_fill(color, opacity=0.1).move_to(centro)
    cuerpo = Circle(radius=radio, color=color, stroke_width=3.5)
    cuerpo.set_fill(FONDO, opacity=1.0).move_to(centro)
    return VGroup(halo, cuerpo)


def _arista(origen, destino, radio_origen, radio_destino, color=SECUNDARIO):
    """Conexión recortada en el borde de los dos nodos que une."""
    direccion = destino - origen
    direccion = direccion / np.linalg.norm(direccion)
    linea = Line(
        origen + direccion * radio_origen, destino - direccion * radio_destino,
        color=color, stroke_width=2,
    )
    return linea.set_stroke(opacity=0.5)


def _neurona():
    """Perceptrón compacto: dos entradas, cuerpo y salida. Traza la recta."""
    centro = np.array([(X_CAPAS[1] + X_CAPAS[2]) / 2, Y_MODELO, 0.0])
    centros_entrada = [
        np.array([X_CAPAS[0], Y_MODELO + lado * 0.62, 0.0]) for lado in (1, -1)
    ]
    centro_salida = np.array([X_CAPAS[-1], Y_MODELO, 0.0])

    entradas = VGroup(*[_nodo(c, RADIO_ENTRADA, VERDE) for c in centros_entrada])
    cuerpo = _nodo(centro, RADIO_CUERPO, PRIMARIO, halo_factor=1.35)
    salida = _nodo(centro_salida, RADIO_SALIDA, AMBAR)
    aristas = VGroup(*[
        _arista(c, centro, RADIO_ENTRADA, RADIO_CUERPO) for c in centros_entrada
    ])
    axon = _arista(centro, centro_salida, RADIO_CUERPO, RADIO_SALIDA, AMBAR)
    return {
        "grupo": VGroup(aristas, axon, entradas, cuerpo, salida),
        "centros_entrada": centros_entrada, "centro_salida": centro_salida,
        "entradas": entradas, "aristas": aristas, "cuerpo": cuerpo,
        "axon": axon, "salida": salida,
    }


def _red(centros_entrada, centro_salida):
    """La red que sustituye a la neurona: mismas entradas, misma salida."""
    capas = [centros_entrada]
    for x, cantidad in zip(X_CAPAS[1:-1], TAMANOS_CAPAS[1:-1]):
        capas.append([
            np.array([x, Y_MODELO + (cantidad - 1) / 2 * PASO_RED - k * PASO_RED, 0.0])
            for k in range(cantidad)
        ])
    capas.append([centro_salida])

    ocultos = [
        VGroup(*[_nodo(c, RADIO_OCULTO, PRIMARIO) for c in capa])
        for capa in capas[1:-1]
    ]
    radios = (RADIO_ENTRADA, RADIO_OCULTO, RADIO_OCULTO, RADIO_SALIDA)
    conexiones = VGroup(*[
        _arista(origen, destino, radios[i], radios[i + 1],
                AMBAR if i == len(capas) - 2 else SECUNDARIO)
        for i, (izquierda, derecha) in enumerate(zip(capas, capas[1:]))
        for origen in izquierda for destino in derecha
    ])
    return ocultos, conexiones


def _recta(ejes, funcion, color):
    """Recta con resplandor detrás: da cuerpo sin engordar el trazo."""
    resplandor = ejes.plot(funcion, x_range=X_TRAZO, color=color)
    resplandor.set_stroke(width=13, opacity=0.16)
    linea = ejes.plot(funcion, x_range=X_TRAZO, color=color)
    linea.set_stroke(width=4.5)
    return VGroup(resplandor, linea)


def _residuos(ejes, xs, ys, funcion):
    """Segmentos verticales del punto a la recta: el error, hecho visible."""
    return VGroup(*[
        DashedLine(
            ejes.c2p(x, y), ejes.c2p(x, funcion(x)),
            color=AMBAR, stroke_width=2.5, dash_length=0.09,
        )
        for x, y in zip(xs, ys)
    ])


def construir(scene):
    encabezado = hacer_titulo("Llevémoslo a las matemáticas")

    ejes = Axes(
        x_range=[0, 5.2, 1], y_range=[0, 3.8, 1],
        x_length=6.4, y_length=4.3,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5, "stroke_opacity": 0.7,
            "include_ticks": False, "tip_width": 0.18, "tip_height": 0.18,
        },
    ).move_to(CENTRO_GRAFICA)

    xs, ys_lineal, ys_curva = _datos()
    puntos = VGroup(*[
        Dot(ejes.c2p(x, y), radius=0.08, color=CLARO)
        for x, y in zip(xs, ys_lineal)
    ])

    modelo = _neurona()
    flecha = Arrow(
        [X_CAPAS[-1] + 0.45, Y_MODELO, 0], [X_CAPAS[-1] + 1.5, Y_MODELO, 0],
        color=AMBAR, stroke_width=5, buff=0,
        max_tip_length_to_length_ratio=0.28,
    ).set_opacity(0.9)

    # ---------------------- 1: la neurona traza la recta --------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(ejes), run_time=0.8)
    scene.play(
        LaggedStart(*[FadeIn(p, scale=0.5) for p in puntos], lag_ratio=0.08),
        run_time=0.9,
    )
    scene.play(FadeIn(modelo["grupo"], scale=0.85), FadeIn(flecha), run_time=0.8)

    # La señal lo atraviesa, sale por la flecha y de ahí nace la recta.
    pulsos = [
        Dot(color=VERDE, radius=0.07).move_to(a.get_start())
        for a in modelo["aristas"]
    ]
    scene.add(*pulsos)
    scene.play(
        *[MoveAlongPath(p, a) for p, a in zip(pulsos, modelo["aristas"])],
        run_time=0.55, rate_func=linear,
    )
    scene.play(
        *[FadeOut(p, scale=0.2) for p in pulsos],
        Indicate(modelo["cuerpo"], color=PRIMARIO, scale_factor=1.1),
        run_time=0.4,
    )
    pulso = Dot(color=AMBAR, radius=0.07).move_to(modelo["axon"].get_start())
    scene.add(pulso)
    scene.play(MoveAlongPath(pulso, modelo["axon"]), run_time=0.4,
               rate_func=linear)
    scene.play(MoveAlongPath(pulso, flecha), run_time=0.45, rate_func=linear)

    recta = _recta(ejes, lambda x: PENDIENTE * x + ORDENADA, VERDE)
    scene.play(
        FadeOut(pulso, scale=0.2), Create(recta), run_time=1.0,
    )
    scene.next_slide()

    # ---------------------- 2: los puntos se curvan -------------------------
    scene.play(
        *[p.animate.move_to(ejes.c2p(x, y))
          for p, x, y in zip(puntos, xs, ys_curva)],
        run_time=1.3,
    )
    scene.next_slide()

    # La neurona hace lo que puede: aplanar la recta. Y aun así falla.
    scene.play(
        Indicate(modelo["cuerpo"], color=AMBAR, scale_factor=1.1),
        Transform(recta, _recta(ejes, lambda x: NIVEL_PLANO, AMBAR)),
        run_time=1.0,
    )
    residuos = _residuos(ejes, xs, ys_curva, lambda x: NIVEL_PLANO)
    scene.play(
        LaggedStart(*[Create(r) for r in residuos], lag_ratio=0.06),
        run_time=1.0,
    )
    scene.next_slide()

    # ---------------------- 3: ni con una red entera ------------------------
    # El cuerpo se convierte en el nodo del medio y la red crece a su alrededor;
    # entradas y salida son las mismas, así se ve que el problema no cambió.
    ocultos, conexiones = _red(modelo["centros_entrada"], modelo["centro_salida"])
    nodos_nuevos = [n for capa in ocultos for n in capa]
    scene.play(
        FadeOut(modelo["aristas"]), FadeOut(modelo["axon"]),
        ReplacementTransform(modelo["cuerpo"], nodos_nuevos[1]),
        run_time=0.8,
    )
    scene.play(
        LaggedStart(*[FadeIn(n, scale=0.4)
                      for n in nodos_nuevos[:1] + nodos_nuevos[2:]],
                    lag_ratio=0.1),
        run_time=0.9,
    )
    scene.play(
        LaggedStart(*[Create(c) for c in conexiones], lag_ratio=0.03),
        run_time=1.1,
    )
    scene.next_slide()

    # Cambian los parámetros, cambia la recta... pero sigue siendo una recta,
    # y los residuos siguen ahí.
    for pendiente, altura in ((-0.42, 1.95), (0.55, 1.15), (0.12, 1.5)):
        def recta_func(x, m=pendiente, c=altura):
            return m * (x - VERTICE) + c

        scene.play(
            LaggedStart(*[Indicate(n, color=CLARO, scale_factor=1.25)
                          for n in nodos_nuevos], lag_ratio=0.04),
            Transform(recta, _recta(ejes, recta_func, AMBAR)),
            Transform(residuos, _residuos(ejes, xs, ys_curva, recta_func)),
            run_time=0.85,
        )
    scene.play(
        LaggedStart(*[Indicate(r, color=AMBAR, scale_factor=1.15)
                      for r in residuos], lag_ratio=0.05),
        run_time=0.9,
    )
    scene.wait(0.3)

    scene.next_slide()
