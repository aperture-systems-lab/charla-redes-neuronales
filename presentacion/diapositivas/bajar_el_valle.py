import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
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
    MathTex,
    Rectangle,
    RoundedRectangle,
    Transform,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, ROJO, SECUNDARIO, VERDE

Y_FILA = -0.3
Y_PIE = -2.05
CAPAS = ((-5.4, 3), (-4.1, 4), (-2.8, 4), (-1.5, 1))
RADIO = 0.24
PASO_NODO = 0.78
X_RED = (CAPAS[0][0] + CAPAS[-1][0]) / 2
X_SALIDA = 0.5
X_CAJA = 3.0
X_ERROR = 5.4
Y_REAL = 1.75

X_MIN, X_MAX = -3.2, 3.2
L_MAX = 3.7
MARGEN = 0.45
CENTRO_PAISAJE = [-1.55, -0.35, 0]
ANCHO_PAISAJE, ALTO_PAISAJE = 7.4, 4.2
LARGO_TANGENTE = 2.0
LARGO_FLECHA = 0.95

X_PARADA = 1.9
TASA = 0.6
PASOS = 8

X_TERMO = 4.6
ANCHO_TERMO = 0.85


def _perdida(x):
    return 0.28 * x**2 + 0.35 * np.sin(1.6 * x) + 0.55


def _derivada(x):
    return 0.56 * x + 0.56 * np.cos(1.6 * x)


def _red_dibujo():
    columnas = [
        [np.array([x, Y_FILA + (n - 1) / 2 * PASO_NODO - k * PASO_NODO, 0.0])
         for k in range(n)]
        for x, n in CAPAS
    ]
    nodos = VGroup(*[
        Circle(radius=RADIO, color=PRIMARIO, stroke_width=3)
        .set_fill(FONDO, opacity=1.0).move_to(c)
        for columna in columnas for c in columna
    ])
    aristas = VGroup()
    for izquierda, derecha in zip(columnas, columnas[1:]):
        for a in izquierda:
            for b in derecha:
                direccion = (b - a) / np.linalg.norm(b - a)
                aristas.add(Line(
                    a + direccion * RADIO, b - direccion * RADIO,
                    color=AMBAR, stroke_width=1.6,
                ).set_stroke(opacity=0.45))
    return VGroup(aristas, nodos), columnas[-1][0]


def _rotulo(contenido, x, color=SECUNDARIO):
    return texto(contenido, 18, color=color).move_to([x, Y_PIE, 0])


def _leyenda(entradas, x_simbolo=-3.85, y_primera=-0.25, paso=0.62):
    grupo = VGroup()
    for fila, (simbolo, glosa) in enumerate(entradas):
        y = y_primera - fila * paso
        grupo.add(
            simbolo.scale(0.8).next_to(
                np.array([x_simbolo, y, 0]), LEFT, buff=0,
            ),
            texto(glosa, 19, color=SECUNDARIO).next_to(
                np.array([x_simbolo + 0.35, y, 0]), RIGHT, buff=0,
            ),
        )
    return grupo


def _flecha(desde, hasta, color=SECUNDARIO):
    return Arrow(
        desde, hasta, color=color, stroke_width=3.5, buff=0.16,
        tip_length=0.22,
    ).set_stroke(opacity=0.85)


def _tangente(ejes, x0):
    base = np.array(ejes.c2p(x0, _perdida(x0)))
    direccion = np.array(ejes.c2p(x0 + 1, _perdida(x0) + _derivada(x0))) - base
    direccion = direccion / np.linalg.norm(direccion)
    return Line(
        base - direccion * LARGO_TANGENTE, base + direccion * LARGO_TANGENTE,
        color=PRIMARIO, stroke_width=3.5,
    )


def _punto(ejes, x0, radio=0.11):
    return Dot(ejes.c2p(x0, _perdida(x0)), radius=radio, color=AMBAR)


def _guia(ejes, x0):
    return DashedLine(
        ejes.c2p(x0, _perdida(x0)), ejes.c2p(x0, 0),
        color=AMBAR, stroke_width=2, dash_length=0.09,
    ).set_stroke(opacity=0.6)


def _marca(ejes, x0):
    return Dot(ejes.c2p(x0, 0), radius=0.07, color=AMBAR)


def _lectura(ejes, x0):
    extremo = ejes.c2p(x0, _perdida(x0))
    return DashedLine(
        [extremo[0] + 0.22, extremo[1], 0],
        [X_TERMO - ANCHO_TERMO / 2, extremo[1], 0],
        color=ROJO, stroke_width=1.6, dash_length=0.08,
    ).set_stroke(opacity=0.35)


def _medidas_termo(ejes):
    pie = ejes.c2p(0, 0)[1]
    return pie, ejes.c2p(0, L_MAX)[1] - pie


def _tubo(ejes):
    pie, alto = _medidas_termo(ejes)
    tubo = Rectangle(
        width=ANCHO_TERMO, height=alto,
        stroke_color=SECUNDARIO, stroke_width=2,
    ).set_fill(FONDO, opacity=1.0)
    return tubo.move_to([X_TERMO, pie + alto / 2, 0])


def _liquido(ejes, valor):
    pie, alto = _medidas_termo(ejes)
    llenado = max(alto * valor / L_MAX, 0.04)
    barra = Rectangle(
        width=ANCHO_TERMO - 0.14, height=llenado,
        stroke_width=0, fill_color=ROJO, fill_opacity=0.8,
    )
    return barra.move_to([X_TERMO, pie + llenado / 2, 0])


def _paso_eje(ejes, desde, hasta):
    return Arrow(
        ejes.c2p(desde, 0), ejes.c2p(hasta, 0),
        color=VERDE, stroke_width=5, buff=0, tip_length=0.2,
        max_tip_length_to_length_ratio=0.4,
    )


def _flecha_eje(ejes, x0, hacia_arriba, color):
    signo = 1.0 if _derivada(x0) >= 0 else -1.0
    if not hacia_arriba:
        signo = -signo
    base = np.array(ejes.c2p(x0, 0))
    return Arrow(
        base, base + RIGHT * signo * LARGO_FLECHA,
        color=color, stroke_width=5, buff=0.05, tip_length=0.24,
    )


def _diagrama(scene):
    red, centro_salida = _red_dibujo()
    rot_red = VGroup(
        texto("la red", 18, color=SECUNDARIO),
        texto("y sus pesos", 18, color=AMBAR),
    ).arrange(RIGHT, buff=0.14).move_to([X_RED, Y_PIE, 0])

    salida = MathTex(r"\hat{y}", color=PRIMARIO).scale(1.5)
    salida.move_to([X_SALIDA, Y_FILA, 0])
    rot_salida = _rotulo("lo que predice", X_SALIDA)
    flecha_salida = _flecha(centro_salida + RIGHT * RADIO, salida.get_left())

    caja = RoundedRectangle(
        width=2.2, height=1.5, corner_radius=0.18,
        stroke_color=ROJO, stroke_width=3,
    ).set_fill(ROJO, opacity=0.1).move_to([X_CAJA, Y_FILA, 0])
    nombre_caja = texto("error", 24, color=ROJO).move_to(caja.get_center())
    flecha_caja = _flecha(salida.get_right(), caja.get_left())

    real = MathTex("y", color=CLARO).scale(1.4).move_to([X_CAJA, Y_REAL, 0])
    rot_real = texto("la observación", 17, color=SECUNDARIO)
    rot_real.next_to(real, RIGHT, buff=0.28)
    flecha_real = _flecha(real.get_bottom(), caja.get_top())

    valor_error = MathTex("L", color=ROJO).scale(1.6)
    valor_error.move_to([X_ERROR, Y_FILA, 0])
    rot_error = _rotulo("cuánto falla", X_ERROR, color=ROJO)
    flecha_error = _flecha(caja.get_right(), valor_error.get_left())

    scene.play(FadeIn(red), FadeIn(rot_red), run_time=1.0)
    scene.play(Create(flecha_salida), FadeIn(salida, shift=RIGHT * 0.2),
               FadeIn(rot_salida), run_time=0.8)
    scene.play(Create(flecha_caja), Create(caja), FadeIn(nombre_caja),
               run_time=0.8)
    scene.play(FadeIn(real, shift=DOWN * 0.15), FadeIn(rot_real),
               Create(flecha_real), run_time=0.8)
    scene.play(Create(flecha_error), FadeIn(valor_error, shift=RIGHT * 0.2),
               FadeIn(rot_error), run_time=0.8)
    scene.next_slide()

    return (
        VGroup(red, rot_red),
        VGroup(flecha_salida, salida, rot_salida),
        VGroup(flecha_caja, caja, nombre_caja),
        VGroup(real, flecha_real, rot_real),
        VGroup(flecha_error, valor_error, rot_error),
    )


def _compuesta():
    compuesta = MathTex(
        "L", "(", "w", ")", "=",
        "L", r"\big(", "f(x;", "w", ")", ",", "y", r"\big)",
    ).scale(1.4).move_to([0, 1.2, 0])
    for i in (0, 1, 3, 5, 6, 12):
        compuesta[i].set_color(ROJO)
    for i in (2, 8):
        compuesta[i].set_color(AMBAR)
    for i in (7, 9):
        compuesta[i].set_color(PRIMARIO)
    for i in (10, 11):
        compuesta[i].set_color(CLARO)
    return compuesta


def _a_formula(scene, piezas):
    compuesta = _compuesta()
    destinos = (
        compuesta[7:10],
        compuesta[7:10],
        VGroup(compuesta[5], compuesta[6], compuesta[12]),
        compuesta[10:12],
        compuesta[0:5],
    )

    simbolo_f = MathTex("f(x;", "w", ")")
    simbolo_f[0].set_color(PRIMARIO)
    simbolo_f[1].set_color(AMBAR)
    simbolo_f[2].set_color(PRIMARIO)
    leyenda = _leyenda((
        (simbolo_f, "lo que predice la red"),
        (MathTex("y", color=CLARO), "la observación, es fija"),
        (MathTex("w", color=AMBAR), "los pesos, lo que vamos a optimizar"),
    ))
    clave = texto("el error es una función de los pesos", 22, color=AMBAR)
    clave.move_to([0, -2.45, 0])

    scene.play(*[Transform(a, b.copy()) for a, b in zip(piezas, destinos)],
               run_time=1.5)
    scene.remove(*piezas)
    scene.add(compuesta)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15) for f in leyenda],
                    lag_ratio=0.18),
        run_time=1.2,
    )
    scene.play(
        FadeIn(clave, shift=UP * 0.1),
        LaggedStart(*[Indicate(compuesta[i], color=CLARO, scale_factor=1.4)
                      for i in (2, 8)], lag_ratio=0.3),
        run_time=1.2,
    )
    scene.next_slide()

    scene.play(FadeOut(compuesta), FadeOut(leyenda), FadeOut(clave),
               run_time=0.7)


def _paisaje(scene):
    ejes = Axes(
        x_range=[X_MIN, X_MAX, 1], y_range=[0, L_MAX, 1],
        x_length=ANCHO_PAISAJE, y_length=ALTO_PAISAJE,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5,
            "include_ticks": False, "tip_width": 0.16, "tip_height": 0.16,
        },
    ).move_to(CENTRO_PAISAJE)
    valle = ejes.plot(_perdida, x_range=[X_MIN + 0.25, X_MAX - 0.25],
                      color=ROJO).set_stroke(width=4)
    rot_w = MathTex("w", color=AMBAR).scale(0.95)
    rot_w.next_to(ejes.c2p(X_MAX, 0), DOWN + RIGHT, buff=0.16)
    rot_L = MathTex("L", color=ROJO).scale(0.95)
    rot_L.next_to(ejes.c2p(0, L_MAX), UP, buff=0.14)

    tubo = _tubo(ejes)
    rotulo_termo = texto("error", 19, color=ROJO).next_to(tubo, UP, buff=0.24)

    arranque = X_MIN + MARGEN
    donde = ValueTracker(arranque)
    dinamicos = (_tangente, _lectura, _guia, _marca, _punto)
    tangente, lectura, guia, marca, punto = [
        always_redraw(lambda f=f: f(ejes, donde.get_value()))
        for f in dinamicos
    ]
    nivel = always_redraw(
        lambda: _liquido(ejes, _perdida(donde.get_value()))
    )

    scene.play(Create(ejes), FadeIn(rot_w), FadeIn(rot_L), run_time=0.8)
    scene.play(Create(valle), Create(tubo), FadeIn(rotulo_termo), run_time=1.3)

    quietos = VGroup(*[f(ejes, arranque) for f in dinamicos],
                     _liquido(ejes, _perdida(arranque)))
    scene.play(FadeIn(quietos), run_time=0.9)
    scene.remove(quietos)
    scene.add(nivel, lectura, guia, marca, tangente, punto)

    scene.play(donde.animate.set_value(X_MAX - MARGEN), run_time=4.0,
               rate_func=linear)
    scene.next_slide()
    return ejes, donde, tangente


def _pendiente(scene, ejes, donde):
    scene.play(donde.animate.set_value(X_PARADA), run_time=0.9)
    flecha_sube = _flecha_eje(ejes, X_PARADA, True, ROJO)
    etiqueta_sube = MathTex(r"\frac{dL}{dw}", color=ROJO).scale(0.85)
    etiqueta_sube.next_to(flecha_sube, DOWN, buff=0.22)
    scene.play(Create(flecha_sube), FadeIn(etiqueta_sube), run_time=0.9)
    scene.next_slide()

    flecha_baja = _flecha_eje(ejes, X_PARADA, False, VERDE)
    etiqueta_baja = MathTex(r"-\frac{dL}{dw}", color=VERDE).scale(0.85)
    etiqueta_baja.next_to(flecha_baja, DOWN, buff=0.22)
    scene.play(
        Transform(flecha_sube, flecha_baja),
        Transform(etiqueta_sube, etiqueta_baja),
        run_time=1.1,
    )
    scene.next_slide()
    return flecha_sube, etiqueta_sube


def _regla():
    regla = MathTex(
        "w", r"\leftarrow", "w", "-", r"\eta", r"\frac{dL}{dw}",
    ).scale(0.95)
    for i in (0, 2):
        regla[i].set_color(AMBAR)
    regla[3].set_color(VERDE)
    regla[4].set_color(MORADO)
    regla[5].set_color(VERDE)
    glosa = VGroup(
        MathTex(r"\eta", color=MORADO).scale(0.75),
        texto("el tamaño del paso", 18, color=SECUNDARIO),
    ).arrange(RIGHT, buff=0.22)
    fila_regla = VGroup(regla, glosa).arrange(RIGHT, buff=0.9)
    fila_regla.move_to([CENTRO_PAISAJE[0] + 0.6, -3.2, 0])
    return regla, fila_regla


def _descender(scene, ejes, donde, tangente, flecha, etiqueta):
    regla, fila_regla = _regla()
    recorrido = [X_PARADA]
    for _ in range(PASOS):
        recorrido.append(recorrido[-1] - TASA * _derivada(recorrido[-1]))

    tangente.clear_updaters()
    scene.play(
        FadeOut(etiqueta), FadeOut(tangente),
        FadeIn(fila_regla, shift=UP * 0.12),
        run_time=0.9,
    )

    saltos = [_paso_eje(ejes, a, b) for a, b in zip(recorrido, recorrido[1:])]
    scene.play(Transform(flecha, saltos[0]), run_time=0.8)

    salto = flecha
    for i, x_siguiente in enumerate(recorrido[1:]):
        rastro = _punto(ejes, recorrido[i], radio=0.07)
        scene.add(rastro.set_opacity(0.35))
        scene.play(donde.animate.set_value(x_siguiente), FadeOut(salto),
                   run_time=0.55)
        if i + 1 < len(saltos):
            salto = saltos[i + 1]
            scene.play(Create(salto), run_time=0.4)

    scene.play(Indicate(regla, color=CLARO, scale_factor=1.1), run_time=0.9)
    scene.wait(0.3)

    scene.next_slide()


def construir(scene):
    encabezado = hacer_titulo("Aprender es bajar al valle")
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)

    piezas = _diagrama(scene)
    _a_formula(scene, piezas)
    ejes, donde, tangente = _paisaje(scene)
    flecha, etiqueta = _pendiente(scene, ejes, donde)
    _descender(scene, ejes, donde, tangente, flecha, etiqueta)
