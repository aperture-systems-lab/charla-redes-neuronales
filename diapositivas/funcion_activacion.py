"""Diapositiva 13 — La función de activación.

El umbral de la neurona, traducido a matemáticas: si la suma es negativa, sale
0; si es positiva, sale tal cual. Esa es la función de activación —aquí, ReLU— y
al final la pieza cae en el hueco que quedó marcado con la interrogación.

Arranca con el nombre entero —Rectified Linear Unit— encima de la gráfica y, ya
vista la fórmula, se queda en la sigla. Cierra enseñando la neurona entera ya
montada: el mismo perceptrón, pero con el cuerpo partido en el sumatorio y,
detrás, la activación.
"""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Axes,
    Circle,
    Create,
    DashedVMobject,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    Transform,
    VGroup,
    Write,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, SECUNDARIO, VERDE

X_GRAFICA = -3.3
RANGO = 3.0

# El modelo completo con el que cierra la diapositiva.
X_ENTRADAS = -4.3
X_MODELO = 0.0
Y_MODELO = 0.35
X_SALIDA = 3.9
RADIO_CUERPO = 1.0
RADIO_NODO = 0.3
Y_FORMULA = -2.75
FILAS_MODELO = ((1.75, "x_1", "w_1"), (0.35, "x_2", "w_2"), (-1.05, "x_n", "w_n"))


def _trazo(inicio, fin, color):
    """Tramo de la curva con su resplandor detrás: le da cuerpo sin engordarlo."""
    resplandor = Line(inicio, fin, color=color, stroke_width=15)
    resplandor.set_stroke(opacity=0.15)
    linea = Line(inicio, fin, color=color, stroke_width=5)
    return VGroup(resplandor, linea)


def _modelo():
    """El perceptrón completo: entradas, cuerpo partido en Σ y activación, salida.

    Es el mismo dibujo de la diapositiva del perceptrón, con la diferencia que
    justifica esta: el cuerpo ya no solo suma, detrás tiene la activación.
    """
    centro = np.array([X_MODELO, Y_MODELO, 0.0])
    cx, cy = X_MODELO, Y_MODELO

    nodos, etiquetas, aristas, pesos = [], [], [], VGroup()
    for y, nombre_x, nombre_w in FILAS_MODELO:
        nodo = Circle(radius=RADIO_NODO, color=VERDE, stroke_width=3)
        nodo.set_fill(FONDO, opacity=1.0).move_to([X_ENTRADAS, y, 0])
        nodos.append(nodo)
        etiquetas.append(
            MathTex(nombre_x, color=CLARO).scale(0.5).move_to(nodo.get_center())
        )
        direccion = centro - nodo.get_center()
        direccion = direccion / np.linalg.norm(direccion)
        arista = Line(
            nodo.get_center() + direccion * RADIO_NODO,
            centro - direccion * RADIO_CUERPO,
            color=SECUNDARIO, stroke_width=2.5,
        )
        aristas.append(arista)
        pesos.add(
            MathTex(nombre_w, color=VERDE).scale(0.46).move_to(
                arista.point_from_proportion(0.42) + UP * 0.24
            )
        )
    vdots = MathTex(r"\vdots", color=SECUNDARIO).scale(0.55)
    vdots.move_to([X_ENTRADAS, (FILAS_MODELO[1][0] + FILAS_MODELO[2][0]) / 2, 0])

    cuerpo = Circle(radius=RADIO_CUERPO, color=PRIMARIO, stroke_width=4.5)
    cuerpo.set_fill(FONDO, opacity=1.0).move_to(centro)
    divisor = Line(
        [cx, cy - RADIO_CUERPO + 0.12, 0], [cx, cy + RADIO_CUERPO - 0.12, 0],
        color=SECUNDARIO, stroke_width=1.6,
    ).set_stroke(opacity=0.5)
    sigma = MathTex(r"\Sigma", color=CLARO).scale(0.95)
    sigma.move_to([cx - 0.44, cy, 0])

    # La mitad de atrás: la ReLU en pequeño, con su eje.
    origen = np.array([cx + 0.36, cy - 0.24, 0.0])
    activacion = VGroup(
        Line(origen + LEFT * 0.28, origen + RIGHT * 0.42,
             color=SECUNDARIO, stroke_width=1.4).set_stroke(opacity=0.6),
        Line(origen + LEFT * 0.26, origen, color=VERDE, stroke_width=4),
        Line(origen, origen + np.array([0.36, 0.58, 0]), color=VERDE,
             stroke_width=4),
    )

    centro_bias = np.array([cx, cy + RADIO_CUERPO + 0.95, 0.0])
    bias = VGroup(
        Circle(radius=0.27, color=MORADO, stroke_width=3)
        .set_fill(FONDO, opacity=1.0).move_to(centro_bias),
        MathTex("b", color=MORADO).scale(0.5).move_to(centro_bias),
    )
    direccion_bias = centro - centro_bias
    direccion_bias = direccion_bias / np.linalg.norm(direccion_bias)
    arista_bias = Line(
        centro_bias + direccion_bias * 0.27,
        centro - direccion_bias * RADIO_CUERPO,
        color=MORADO, stroke_width=2.5,
    ).set_stroke(opacity=0.9)

    flecha = Arrow(
        centro + RIGHT * RADIO_CUERPO, [X_SALIDA - 0.36, cy, 0],
        color=AMBAR, stroke_width=4, buff=0.05,
        max_tip_length_to_length_ratio=0.14,
    )
    nodo_salida = VGroup(
        Circle(radius=0.32, color=AMBAR, stroke_width=3)
        .set_fill(FONDO, opacity=1.0).move_to([X_SALIDA, cy, 0]),
        MathTex(r"\hat{y}", color=AMBAR).scale(0.58).move_to([X_SALIDA, cy, 0]),
    )

    formula = MathTex(
        r"\hat{y}", "=", r"\mathrm{ReLU}",
        r"\!\left(\sum_i x_i w_i + b\right)",
    ).scale(0.85).move_to([0, Y_FORMULA, 0])
    formula[0].set_color(AMBAR)
    formula[2].set_color(VERDE)

    return {
        "nodos": nodos, "etiquetas": etiquetas, "aristas": aristas,
        "pesos": pesos, "vdots": vdots, "cuerpo": cuerpo, "divisor": divisor,
        "sigma": sigma, "activacion": activacion, "bias": bias,
        "arista_bias": arista_bias, "flecha": flecha,
        "nodo_salida": nodo_salida, "formula": formula,
    }


def construir(scene):
    encabezado = hacer_titulo("¿Cómo activo la neurona?")

    ejes = Axes(
        x_range=[-RANGO, RANGO, 1], y_range=[-0.6, 3.0, 1],
        x_length=5.4, y_length=3.9,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5,
            "include_ticks": False, "tip_width": 0.16, "tip_height": 0.16,
        },
    ).move_to([X_GRAFICA, -0.35, 0])

    # ReLU en dos tramos, cada uno con su color —apagado / deja pasar—, con su
    # resplandor detrás y un punto en el codo.
    tramo_cero = _trazo(ejes.c2p(-RANGO + 0.2, 0), ejes.c2p(0, 0), SECUNDARIO)
    tramo_pasa = _trazo(ejes.c2p(0, 0), ejes.c2p(2.7, 2.7), VERDE)
    quiebro = VGroup(
        Dot(ejes.c2p(0, 0), radius=0.16, color=VERDE).set_opacity(0.2),
        Dot(ejes.c2p(0, 0), radius=0.075, color=CLARO),
    )

    # Primero el nombre entero, y en cuanto se ha leído se queda en la sigla.
    nombre = texto("Rectified Linear Unit", 22, color=VERDE)
    nombre.move_to([X_GRAFICA, 1.95, 0])
    sigla = texto("ReLU", 30, color=VERDE, weight=BOLD)
    sigla.move_to([X_GRAFICA, 1.95, 0])

    formula = MathTex(
        r"\mathrm{ReLU}(z) = \max(0,\, z)", color=CLARO,
    ).scale(0.85).move_to([X_GRAFICA, -2.7, 0])

    # --- El hueco de la 9, ahora relleno -----------------------------------
    x_hueco = 3.4
    y_hueco = 0.9
    entrada = MathTex(r"\Sigma", color=PRIMARIO).scale(0.8)
    entrada.move_to([x_hueco - 2.0, y_hueco, 0])
    salida = MathTex(r"\hat{y}", color=AMBAR).scale(0.7)
    salida.move_to([x_hueco + 2.0, y_hueco, 0])
    flecha_a = Arrow(
        entrada.get_right(), [x_hueco - 0.72, y_hueco, 0],
        color=SECUNDARIO, stroke_width=3.5, buff=0.12,
        max_tip_length_to_length_ratio=0.18,
    )
    flecha_b = Arrow(
        [x_hueco + 0.72, y_hueco, 0], salida.get_left(),
        color=AMBAR, stroke_width=3.5, buff=0.12,
        max_tip_length_to_length_ratio=0.18,
    )
    hueco = DashedVMobject(
        Circle(radius=0.68, color=CLARO, stroke_width=4), num_dashes=26,
    ).move_to([x_hueco, y_hueco, 0])
    interrogacion = texto("?", 44, color=CLARO).move_to([x_hueco, y_hueco, 0])

    relleno = Circle(radius=0.68, color=VERDE, stroke_width=4)
    relleno.set_fill(FONDO, opacity=1.0).move_to([x_hueco, y_hueco, 0])
    mini_relu = VGroup(
        Line([x_hueco - 0.42, y_hueco - 0.26, 0], [x_hueco, y_hueco - 0.26, 0],
             color=VERDE, stroke_width=4),
        Line([x_hueco, y_hueco - 0.26, 0], [x_hueco + 0.38, y_hueco + 0.32, 0],
             color=VERDE, stroke_width=4),
    )

    resuelto = VGroup(
        texto("La pieza que faltaba", 24, color=CLARO),
        texto("ya está en su sitio", 20, color=VERDE),
    ).arrange(DOWN, buff=0.16).move_to([x_hueco, -1.6, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(FadeIn(nombre, shift=DOWN * 0.15), run_time=0.7)
    scene.play(Create(ejes), run_time=0.8)
    scene.play(Create(tramo_cero), FadeIn(quiebro, scale=0.4), run_time=0.8)
    scene.play(Create(tramo_pasa), run_time=0.9)
    scene.play(Write(formula), run_time=0.9)

    # Ya dicho el nombre entero y vista la fórmula, se queda en la sigla, que
    # es como la llamaremos el resto de la charla.
    scene.play(Transform(nombre, sigla), run_time=0.8)
    scene.next_slide()

    # Vuelve el hueco que quedó marcado, y ReLU cae dentro.
    scene.play(
        FadeIn(entrada), FadeIn(salida),
        Create(flecha_a), Create(flecha_b),
        Create(hueco), FadeIn(interrogacion),
        run_time=0.9,
    )
    scene.play(
        FadeOut(interrogacion, scale=0.5),
        Transform(hueco, relleno),
        run_time=0.6,
    )
    scene.play(Create(mini_relu), run_time=0.6)
    scene.play(
        Indicate(VGroup(hueco, mini_relu), color=VERDE, scale_factor=1.15),
        FadeIn(resuelto, shift=UP * 0.12),
        run_time=0.8,
    )
    scene.next_slide()

    # --- Y así queda la neurona entera -------------------------------------
    # El mismo perceptrón de su diapositiva, pero con el cuerpo partido en dos:
    # el sumatorio y, detrás, la activación que acabamos de meter.
    viejo = VGroup(
        ejes, tramo_cero, tramo_pasa, quiebro, formula, nombre,
        entrada, salida, flecha_a, flecha_b, hueco, mini_relu, resuelto,
    )
    modelo = _modelo()
    scene.play(FadeOut(viejo), run_time=0.7)

    scene.play(
        LaggedStart(*[GrowFromCenter(VGroup(n, e))
                      for n, e in zip(modelo["nodos"], modelo["etiquetas"])],
                    lag_ratio=0.18),
        FadeIn(modelo["vdots"]),
        run_time=0.9,
    )
    scene.play(
        LaggedStart(*[Create(a) for a in modelo["aristas"]], lag_ratio=0.18),
        FadeIn(modelo["pesos"]),
        run_time=0.9,
    )
    scene.play(
        GrowFromCenter(modelo["cuerpo"]), FadeIn(modelo["sigma"]),
        run_time=0.7,
    )
    # La mitad nueva del cuerpo: la activación.
    scene.play(Create(modelo["divisor"]), Create(modelo["activacion"]),
               run_time=0.8)
    scene.play(
        GrowFromCenter(modelo["bias"]), Create(modelo["arista_bias"]),
        Create(modelo["flecha"]), GrowFromCenter(modelo["nodo_salida"]),
        run_time=0.8,
    )
    scene.next_slide()

    # Una señal lo recorre entero, ya con activación.
    pulsos = [
        Dot(color=VERDE, radius=0.07).move_to(a.get_start())
        for a in modelo["aristas"]
    ]
    scene.add(*pulsos)
    scene.play(
        *[MoveAlongPath(p, a) for p, a in zip(pulsos, modelo["aristas"])],
        run_time=0.7, rate_func=linear,
    )
    scene.play(
        *[FadeOut(p, scale=0.2) for p in pulsos],
        Indicate(modelo["sigma"], color=CLARO, scale_factor=1.3),
        run_time=0.45,
    )
    scene.play(Indicate(modelo["activacion"], color=CLARO, scale_factor=1.25),
               run_time=0.5)
    pulso_salida = Dot(color=AMBAR, radius=0.07)
    pulso_salida.move_to(modelo["flecha"].get_start())
    scene.add(pulso_salida)
    scene.play(MoveAlongPath(pulso_salida, modelo["flecha"]), run_time=0.5,
               rate_func=linear)
    scene.play(
        FadeOut(pulso_salida, scale=0.2),
        Indicate(modelo["nodo_salida"], color=AMBAR, scale_factor=1.35),
        run_time=0.45,
    )

    scene.play(Write(modelo["formula"]), run_time=1.2)
    scene.play(Indicate(modelo["formula"][2], color=VERDE, scale_factor=1.25),
               run_time=0.7)
    scene.wait(0.4)

    scene.next_slide()
