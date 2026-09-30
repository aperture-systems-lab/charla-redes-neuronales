import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    DashedLine,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    MathTex,
    Rectangle,
    VGroup,
    VMobject,
)

from componentes import aspa, enmarcar, imagen, texto, visto
from componentes import titulo as hacer_titulo
from estilo import PRIMARIO, ROJO, SECUNDARIO, VERDE

ANCHO_BENEVOLENCIA = 11.0
Y_BENEVOLENCIA = -0.4

X_COLUMNA = 3.5
Y_CABECERA = 1.05
Y_CUADROS = -0.72
ANCHO_CUADRO = 1.9
ALTO_CUADRO = 1.85
PASO_CUADRO = 2.05
Y_FORMULA = -2.15


def _relu(x):
    return np.maximum(0.0, x)


def _sigmoide(x):
    return 1.0 / (1.0 + np.exp(-x))


POLINOMIOS = (
    (lambda x: 0.85 * x, "y = x"),
    (lambda x: 1.7 * x**2 - 0.85, "y = x^2"),
    (lambda x: 2.4 * x**3 - 1.7 * x, "y = x^3 - x"),
)
NO_POLINOMIOS = (
    (lambda x: 1.7 * _relu(x) - 0.5, r"\mathrm{ReLU}(x)"),
    (lambda x: 1.7 * _sigmoide(7 * x) - 0.85, r"\frac{1}{1 + e^{-x}}"),
    (lambda x: 0.85 * np.tanh(1.8 * x), r"\tanh(x)"),
)


def _cuadro(funcion, formula, color, centro):
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
    scene.play(Indicate(buenos[0], color=PRIMARIO, scale_factor=1.1),
               run_time=0.8)
    scene.wait(0.5)

    scene.next_slide()

    encabezado_elegir = hacer_titulo("Cómo elegir función de activación")
    benevolencia = imagen("benevolencia")
    benevolencia.scale_to_fit_width(ANCHO_BENEVOLENCIA)
    benevolencia.move_to([0, Y_BENEVOLENCIA, 0])
    marco_benevolencia = enmarcar(benevolencia, margen=0.16)
    scene.play(
        FadeOut(VGroup(divisoria, malos_cab, malos, buenos_cab, buenos)),
        FadeOut(encabezado), FadeIn(encabezado_elegir, shift=DOWN * 0.2),
        run_time=0.8,
    )
    scene.play(FadeIn(benevolencia), Create(marco_benevolencia), run_time=0.7)
    scene.wait(0.3)

    scene.next_slide()
