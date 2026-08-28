"""Diapositiva 19 — ¿Cómo calificamos el modelo?

Une lo que antes eran dos diapositivas sueltas (el error en regresión y el error
en clasificación) en un solo hilo, porque son la misma idea contada dos veces:
para poder mejorar hay que poder ponerle nota a lo que hace el modelo, y esa
nota la da una **función de error**.

Tres pantallas, y las tres con el mismo gesto —primero un modelo malo, con el
termómetro arriba, y luego uno bueno, con el termómetro abajo—, que es lo que
hace que se lean como la misma idea:

1. los datos y lo que falla en cada punto, medido como distancia,
2. el MSE, con los errores dibujados como **cuadrados**, porque lo que suma la
   fórmula es el área y no la distancia,
3. la binary cross entropy, con la curva de ``-log`` y el coste de acertar con
   dudas frente a acertar seguro.

Los datos son curvados a propósito: si fueran una recta, cualquier recta
acertaría y no habría nada que calificar. Y los colores se mantienen de punta a
punta —lo real en claro, lo que predice el modelo en cian y el error siempre en
rojo—, en los dibujos y dentro de las fórmulas.
"""

import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    MathTex,
    Rectangle,
    Square,
    Transform,
    VGroup,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import CLARO, FONDO, PRIMARIO, ROJO, SECUNDARIO, VERDE

# --- Los datos -------------------------------------------------------------
# Pocos y bien separados: los cuadrados del error crecen con el lado, y con los
# puntos juntos se montaban unos encima de otros y tapaban el dibujo.
XS = (0.4, 1.05, 1.7, 2.35, 3.0, 3.65)
RUIDO = (0.1, -0.12, 0.08, -0.1, 0.12, -0.08)

# --- El termómetro grande de la pantalla 1 ---------------------------------
X_TERMO = 4.35
ANCHO_TERMO = 0.75
ALTO_TERMO = 3.1
Y_PIE_TERMO = -2.05
LLENO = 0.9              # hasta dónde sube con el modelo malo

# --- La rejilla de las pantallas de fórmula --------------------------------
Y_PIE = 1.85
Y_FORMULA = 0.8
Y_LEYENDA = -0.85        # primera fila
CENTRO_GRAFICA_APOYO = [2.35, -1.5, 0]
ANCHO_GRAFICA_APOYO = 4.3
ALTO_GRAFICA_APOYO = 2.5
X_TERMO_APOYO = 5.5
ANCHO_TERMO_APOYO = 0.5
ALTO_TERMO_APOYO = 2.1
Y_PIE_TERMO_APOYO = -2.6

# Las dos probabilidades que se comparan en clasificación.
P_MALA, P_BUENA = 0.1, 0.9


def _real(x):
    """Lo que hacen los datos de verdad: suben, bajan y vuelven a subir."""
    return 2.1 + 1.15 * np.sin(1.75 * np.asarray(x) - 0.7)


def _leyenda(entradas, x_simbolo=-5.5, paso=0.6):
    """Los símbolos de una fórmula, uno por fila, con su color y su glosa."""
    grupo = VGroup()
    for fila, (simbolo, color, glosa) in enumerate(entradas):
        y = Y_LEYENDA - fila * paso
        grupo.add(
            MathTex(simbolo, color=color).scale(0.8).move_to([x_simbolo, y, 0]),
            texto(glosa, 19, color=SECUNDARIO).next_to(
                np.array([x_simbolo + 0.45, y, 0]), RIGHT, buff=0,
            ),
        )
    return grupo


def _tubo(x, y_pie, ancho, alto):
    """El envase del termómetro, que nunca cambia."""
    tubo = Rectangle(
        width=ancho, height=alto,
        stroke_color=SECUNDARIO, stroke_width=2,
    ).set_fill(FONDO, opacity=1.0)
    return tubo.move_to([x, y_pie + alto / 2, 0])


def _liquido(x, y_pie, ancho, alto, fraccion, color=ROJO):
    """El nivel, siempre anclado al fondo del tubo."""
    llenado = max(alto * fraccion, 0.03)
    barra = Rectangle(
        width=ancho - 0.13, height=llenado,
        stroke_width=0, fill_color=color, fill_opacity=0.8,
    )
    return barra.move_to([x, y_pie + llenado / 2, 0])


def _ejes_datos(centro, ancho, alto):
    return Axes(
        x_range=[0, 4.1, 1], y_range=[0, 4.2, 1],
        x_length=ancho, y_length=alto,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.2,
            "include_ticks": False, "tip_width": 0.14, "tip_height": 0.14,
        },
    ).move_to(centro)


def _dibujo_datos(ejes, ys, funcion, forma, radio=0.085, grosor=4):
    """Puntos, aproximación y el error de cada uno.

    ``forma`` decide cómo se pinta ese error. Como distancia mientras solo se
    habla de "lo que falla", y como **cuadrado** en cuanto aparece el MSE: lo
    que esa fórmula suma es el área, no la distancia, y con segmentos el dibujo
    sería el del MAE y engañaría.
    """
    puntos = VGroup(*[
        Dot(ejes.c2p(x, y), radius=radio, color=CLARO) for x, y in zip(XS, ys)
    ])
    curva = ejes.plot(
        lambda x: float(funcion(x)), x_range=[0.15, 3.9], color=PRIMARIO,
    ).set_stroke(width=grosor)

    alto_unidad = ejes.c2p(0, 1)[1] - ejes.c2p(0, 0)[1]
    errores = VGroup()
    for x, y in zip(XS, ys):
        prediccion = float(funcion(x))
        if forma == "distancias":
            errores.add(DashedLine(
                ejes.c2p(x, y), ejes.c2p(x, prediccion),
                color=ROJO, stroke_width=grosor, dash_length=0.11,
            ))
            continue
        lado = max(abs(y - prediccion) * alto_unidad, 0.02)
        cuadrado = Square(
            side_length=lado, stroke_color=ROJO, stroke_width=grosor * 0.55,
            fill_color=ROJO, fill_opacity=0.25,
        )
        cuadrado.move_to([
            ejes.c2p(x, 0)[0] + lado / 2,
            ejes.c2p(x, min(y, prediccion))[1] + lado / 2, 0,
        ])
        errores.add(cuadrado)
    return puntos, curva, errores


def _ejes_log(centro, ancho, alto):
    ejes = Axes(
        x_range=[0, 1.05, 0.25], y_range=[0, 3.2, 1],
        x_length=ancho, y_length=alto,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.2,
            "include_ticks": False, "tip_width": 0.14, "tip_height": 0.14,
        },
    ).move_to(centro)
    curva = ejes.plot(lambda p: -np.log(p), x_range=[0.043, 1.0, 0.01],
                      color=ROJO).set_stroke(width=3.5)
    rot_x = MathTex(r"\hat{y}", color=PRIMARIO).scale(0.65)
    rot_x.next_to(ejes.c2p(1.05, 0), DOWN, buff=0.2)
    return VGroup(ejes, rot_x), curva


def _marca_log(ejes, p, color):
    """Dónde cae una probabilidad en la curva, y cuánto cuesta."""
    coste = -np.log(p)
    return VGroup(
        DashedLine(ejes.c2p(p, 0), ejes.c2p(p, coste), color=color,
                   stroke_width=2, dash_length=0.08).set_stroke(opacity=0.7),
        Dot(ejes.c2p(p, coste), radius=0.085, color=color),
        texto(f"{p}", 18, color=color).next_to(
            ejes.c2p(p, 0), DOWN, buff=0.14,
        ),
    )


def construir(scene):
    encabezado = hacer_titulo("¿Cómo calificamos el modelo?")
    ys = _real(XS) + np.array(RUIDO)

    # La mala es la mejor recta posible: aun así no puede con una curva.
    pendiente, ordenada = np.polyfit(XS, ys, 1)

    def _mala(x):
        return pendiente * np.asarray(x) + ordenada

    error = {
        nombre: float(np.mean((ys - funcion(XS)) ** 2))
        for nombre, funcion in (("mala", _mala), ("buena", _real))
    }
    proporcion = error["buena"] / error["mala"]

    # --- Pantalla 1: lo que falla, medido como distancia -------------------
    ejes = _ejes_datos([-1.7, -0.35, 0], 7.4, 3.9)
    puntos, curva_mala, dist_mala = _dibujo_datos(ejes, ys, _mala, "distancias")
    _, curva_buena, dist_buena = _dibujo_datos(ejes, ys, _real, "distancias")

    tubo = _tubo(X_TERMO, Y_PIE_TERMO, ANCHO_TERMO, ALTO_TERMO)
    rotulo_termo = texto("error", 20, color=ROJO).next_to(tubo, UP, buff=0.24)
    nivel = _liquido(X_TERMO, Y_PIE_TERMO, ANCHO_TERMO, ALTO_TERMO, LLENO)

    # --- Pantalla 2: el MSE, con los errores como cuadrados ----------------
    mse = MathTex(
        r"L_{\mathrm{MSE}}", "=", r"\frac{1}{n}\sum",
        r"(", "y", "-", r"\hat{y}", ")^2",
    ).scale(1.1).move_to([0, Y_FORMULA, 0])
    mse[0].set_color(ROJO)
    mse[4].set_color(CLARO)
    mse[6].set_color(PRIMARIO)
    leyenda_mse = _leyenda((
        ("y", CLARO, "lo que era de verdad"),
        (r"\hat{y}", PRIMARIO, "lo que dijo el modelo"),
        ("n", SECUNDARIO, "cuántos ejemplos hay"),
    ))
    pie_mse = texto("para regresión", 21, color=SECUNDARIO)
    pie_mse.move_to([0, Y_PIE, 0])

    ejes_mse = _ejes_datos(
        CENTRO_GRAFICA_APOYO, ANCHO_GRAFICA_APOYO, ALTO_GRAFICA_APOYO,
    )
    puntos_mse, curva_mse_mala, cuad_mala = _dibujo_datos(
        ejes_mse, ys, _mala, "cuadrados", radio=0.055, grosor=2.6,
    )
    _, curva_mse_buena, cuad_buena = _dibujo_datos(
        ejes_mse, ys, _real, "cuadrados", radio=0.055, grosor=2.6,
    )
    tubo_mse = _tubo(X_TERMO_APOYO, Y_PIE_TERMO_APOYO,
                     ANCHO_TERMO_APOYO, ALTO_TERMO_APOYO)
    rotulo_mse = texto("error", 17, color=ROJO).next_to(tubo_mse, UP, buff=0.2)
    nivel_mse = _liquido(X_TERMO_APOYO, Y_PIE_TERMO_APOYO,
                         ANCHO_TERMO_APOYO, ALTO_TERMO_APOYO, LLENO)

    # --- Pantalla 3: la BCE, con el mismo gesto ----------------------------
    bce = MathTex(
        r"L_{\mathrm{BCE}}", "=", "-", r"\big[", "y", r"\log(", r"\hat{y}", ")",
        "+", "(1-", "y", r")\log(1-", r"\hat{y}", r")\big]",
    ).scale(0.85).move_to([0, Y_FORMULA, 0])
    for i in (0, 2):
        bce[i].set_color(ROJO)
    for i in (4, 10):
        bce[i].set_color(CLARO)
    for i in (6, 12):
        bce[i].set_color(PRIMARIO)
    leyenda_bce = _leyenda((
        ("y", CLARO, "0 o 1: la respuesta correcta"),
        (r"\hat{y}", PRIMARIO, "la probabilidad del modelo"),
    ))
    pie_bce = texto("para clasificación", 21, color=SECUNDARIO)
    pie_bce.move_to([0, Y_PIE, 0])

    ejes_bce, curva_bce = _ejes_log(
        CENTRO_GRAFICA_APOYO, ANCHO_GRAFICA_APOYO, ALTO_GRAFICA_APOYO,
    )
    marca_mala = _marca_log(ejes_bce[0], P_MALA, ROJO)
    marca_buena = _marca_log(ejes_bce[0], P_BUENA, VERDE)
    tubo_bce = _tubo(X_TERMO_APOYO, Y_PIE_TERMO_APOYO,
                     ANCHO_TERMO_APOYO, ALTO_TERMO_APOYO)
    rotulo_bce = texto("error", 17, color=ROJO).next_to(tubo_bce, UP, buff=0.2)
    nivel_bce = _liquido(X_TERMO_APOYO, Y_PIE_TERMO_APOYO,
                         ANCHO_TERMO_APOYO, ALTO_TERMO_APOYO, LLENO, ROJO)
    nivel_bce_bajo = _liquido(
        X_TERMO_APOYO, Y_PIE_TERMO_APOYO, ANCHO_TERMO_APOYO, ALTO_TERMO_APOYO,
        LLENO * float(np.log(P_BUENA) / np.log(P_MALA)), VERDE,
    )

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)

    # 1. Unos datos que no son una recta, y un modelo que lo hace mal.
    scene.play(Create(ejes), run_time=0.7)
    scene.play(
        LaggedStart(*[FadeIn(p, scale=0.5) for p in puntos], lag_ratio=0.08),
        run_time=0.9,
    )
    scene.play(Create(tubo), FadeIn(rotulo_termo), run_time=0.6)
    scene.play(Create(curva_mala), run_time=0.8)
    scene.play(
        LaggedStart(*[Create(d) for d in dist_mala], lag_ratio=0.1),
        FadeIn(nivel),
        run_time=1.1,
    )
    scene.next_slide()

    # Y uno que lo hace bien: mismos datos, otro modelo, y el termómetro baja.
    scene.play(
        Transform(curva_mala, curva_buena),
        Transform(dist_mala, dist_buena),
        Transform(nivel, _liquido(X_TERMO, Y_PIE_TERMO, ANCHO_TERMO,
                                  ALTO_TERMO, LLENO * proporcion)),
        run_time=1.5,
    )
    scene.next_slide()

    # 2. El MSE. Mismo gesto: primero el error alto, luego el bajo.
    scene.play(
        FadeOut(ejes), FadeOut(puntos), FadeOut(curva_mala),
        FadeOut(dist_mala), FadeOut(tubo), FadeOut(rotulo_termo),
        FadeOut(nivel),
        run_time=0.8,
    )
    scene.play(FadeIn(pie_mse), FadeIn(mse, shift=UP * 0.12), run_time=1.0)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15) for f in leyenda_mse],
                    lag_ratio=0.18),
        FadeIn(VGroup(ejes_mse, puntos_mse, curva_mse_mala, tubo_mse,
                      rotulo_mse)),
        run_time=1.2,
    )
    scene.play(
        LaggedStart(*[FadeIn(c, scale=0.4) for c in cuad_mala],
                    lag_ratio=0.12),
        FadeIn(nivel_mse),
        run_time=1.0,
    )
    scene.next_slide()

    scene.play(
        Transform(curva_mse_mala, curva_mse_buena),
        Transform(cuad_mala, cuad_buena),
        Transform(nivel_mse, _liquido(
            X_TERMO_APOYO, Y_PIE_TERMO_APOYO, ANCHO_TERMO_APOYO,
            ALTO_TERMO_APOYO, LLENO * proporcion,
        )),
        run_time=1.4,
    )
    scene.next_slide()

    # 3. La BCE, montada igual. El pie entra y sale, no se transforma: entre dos
    # textos de distinto largo el morfeo de letras sale ilegible.
    scene.play(
        FadeOut(mse), FadeOut(leyenda_mse), FadeOut(pie_mse),
        FadeOut(VGroup(ejes_mse, puntos_mse, curva_mse_mala, cuad_mala,
                       tubo_mse, rotulo_mse, nivel_mse)),
        FadeIn(pie_bce, shift=DOWN * 0.1),
        run_time=0.8,
    )
    scene.play(FadeIn(bce, shift=UP * 0.12), run_time=1.0)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15) for f in leyenda_bce],
                    lag_ratio=0.18),
        FadeIn(ejes_bce), FadeIn(tubo_bce), FadeIn(rotulo_bce),
        run_time=1.1,
    )
    scene.play(Create(curva_bce), run_time=0.9)
    scene.play(FadeIn(marca_mala), FadeIn(nivel_bce), run_time=0.9)
    scene.next_slide()

    # Acertar con seguridad: el mismo dibujo, y el termómetro se vacía.
    scene.play(
        Transform(marca_mala, marca_buena),
        Transform(nivel_bce, nivel_bce_bajo),
        run_time=1.4,
    )
    scene.wait(0.4)

    scene.next_slide()
