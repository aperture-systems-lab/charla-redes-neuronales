"""Diapositiva 16 — Qué activaciones valen.

La letra pequeña del teorema de la diapositiva anterior. "Una capa oculta basta"
no vale para cualquier activación: hay exactamente una familia prohibida, los
polinomios, y todo lo demás sirve.

La razón cabe en una frase, y es la que cierra la diapositiva: si la activación
es un polinomio, componer capas solo da otro polinomio del mismo grado, así que
la red nunca sale de ahí por muchas neuronas que le pongas. En cuanto la
activación no es un polinomio, se acabó el techo.

El montaje es el clásico de este enunciado: dos columnas separadas por una línea
de puntos, la prohibida a la izquierda con su aspa y la buena a la derecha con
su visto, y en cada una tres ejemplos dibujados en su cuadrito con la fórmula
debajo. A la derecha van ReLU, sigmoide y tanh —las tres que se nombran en una
charla— en vez de los ejemplos de libro tipo coseno, para que se vea que la que
ya hemos usado está en el lado bueno.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    DashedLine,
    FadeIn,
    Indicate,
    LaggedStart,
    MathTex,
    Rectangle,
    VGroup,
    VMobject,
)

from componentes import aspa, texto, visto
from componentes import titulo as hacer_titulo
from estilo import PRIMARIO, ROJO, SECUNDARIO, VERDE

# --- Rejilla de las dos columnas -------------------------------------------
# Sin texto debajo, el contenido es cabecera + cuadros + fórmula, y va centrado
# en lo que deja el título: de 2.75 al marco de abajo, o sea en torno a -0.6.
X_COLUMNA = 3.5         # centro de cada columna (±)
Y_CABECERA = 1.05
Y_CUADROS = -0.72
ANCHO_CUADRO = 1.9
ALTO_CUADRO = 1.85      # casi cuadrados, como en la figura clásica
PASO_CUADRO = 2.05      # separación entre los tres ejemplos de una columna
# Altura fija para las fórmulas. Con ``next_to`` quedaban en escalera: alinea
# por el borde de arriba, y el exponente de x² baja toda la fórmula.
Y_FORMULA = -2.15


def _relu(x):
    return np.maximum(0.0, x)


def _sigmoide(x):
    return 1.0 / (1.0 + np.exp(-x))


# Cada ejemplo es (función ya encajada en el cuadro, fórmula). Las funciones van
# reescaladas para que llenen el cuadrito de lado a lado: lo que se lee es la
# forma, y la fórmula de debajo es la de verdad.
POLINOMIOS = (
    (lambda x: 0.85 * x, "y = x"),
    (lambda x: 1.7 * x**2 - 0.85, "y = x^2"),
    (lambda x: 2.4 * x**3 - 1.7 * x, "y = x^3 - x"),
)
NO_POLINOMIOS = (
    (lambda x: 1.7 * _relu(x) - 0.5, r"\mathrm{ReLU}(x)"),
    # Una escalonada y la otra suave: matemáticamente son familia, pero
    # dibujadas con la misma pendiente salían calcadas y parecían un duplicado.
    (lambda x: 1.7 * _sigmoide(7 * x) - 0.85, r"\frac{1}{1 + e^{-x}}"),
    (lambda x: 0.85 * np.tanh(1.8 * x), r"\tanh(x)"),
)


def _cuadro(funcion, formula, color, centro):
    """Un ejemplo: su cuadrito con la curva dentro y la fórmula debajo.

    El marco lleva su cruz de referencia punteada, como en la figura clásica;
    ubica la curva sin necesidad de poner ejes con números.
    """
    marco = Rectangle(
        width=ANCHO_CUADRO, height=ALTO_CUADRO,
        stroke_color=SECUNDARIO, stroke_width=1.8,
    ).set_stroke(opacity=0.5).move_to(centro)

    guias = VGroup(
        DashedLine(
            centro + LEFT * ANCHO_CUADRO / 2, centro + RIGHT * ANCHO_CUADRO / 2,
            color=SECUNDARIO, stroke_width=1.2, dash_length=0.05,
        ),
        DashedLine(
            centro + DOWN * ALTO_CUADRO / 2, centro + UP * ALTO_CUADRO / 2,
            color=SECUNDARIO, stroke_width=1.2, dash_length=0.05,
        ),
    ).set_stroke(opacity=0.28)

    # La curva se recorta al cuadro en vez de dejarla salir: lo de fuera no
    # aporta nada y ensucia la rejilla.
    xs = np.linspace(-1, 1, 120)
    ys = np.clip(funcion(xs), -1.0, 1.0)
    curva = VMobject(color=color, stroke_width=3.5)
    curva.set_points_as_corners([
        centro + np.array([x * ANCHO_CUADRO * 0.46, y * ALTO_CUADRO * 0.46, 0])
        for x, y in zip(xs, ys)
    ])

    etiqueta = MathTex(formula, color=color).scale(0.55)
    etiqueta.move_to([centro[0], Y_FORMULA, 0])
    return VGroup(marco, guias, curva, etiqueta)


def _columna(ejemplos, color, rotulo, marca, signo):
    """Una de las dos mitades: cabecera con su marca y los tres ejemplos."""
    cabecera = VGroup(
        texto(rotulo, 24, color=color),
        marca,
    ).arrange(RIGHT, buff=0.28)
    cabecera.move_to([signo * X_COLUMNA, Y_CABECERA, 0])

    cuadros = VGroup(*[
        _cuadro(
            funcion, formula, color,
            np.array([signo * X_COLUMNA + (i - 1) * PASO_CUADRO, Y_CUADROS, 0]),
        )
        for i, (funcion, formula) in enumerate(ejemplos)
    ])
    return cabecera, cuadros


def construir(scene):
    encabezado = hacer_titulo("¿Vale cualquier activación?")

    divisoria = DashedLine(
        np.array([0, 1.5, 0]), np.array([0, -2.5, 0]),
        color=SECUNDARIO, stroke_width=2, dash_length=0.1,
    ).set_stroke(opacity=0.35)

    malos_cab, malos = _columna(
        POLINOMIOS, ROJO, "Polinomios", aspa(ROJO), -1,
    )
    buenos_cab, buenos = _columna(
        NO_POLINOMIOS, VERDE, "Todo lo demás", visto(VERDE), +1,
    )

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(divisoria), run_time=0.5)

    scene.play(FadeIn(malos_cab, shift=DOWN * 0.12), run_time=0.6)
    scene.play(
        LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in malos],
                    lag_ratio=0.25),
        run_time=1.2,
    )
    scene.next_slide()

    scene.play(FadeIn(buenos_cab, shift=DOWN * 0.12), run_time=0.6)
    scene.play(
        LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in buenos],
                    lag_ratio=0.25),
        run_time=1.2,
    )
    # Y la que ya conocen está en el lado bueno.
    scene.play(Indicate(buenos[0], color=PRIMARIO, scale_factor=1.1),
               run_time=0.8)
    scene.wait(0.5)

    scene.next_slide()
