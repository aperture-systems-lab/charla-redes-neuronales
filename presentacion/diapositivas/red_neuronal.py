import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    Rectangle,
    ReplacementTransform,
    TransformFromCopy,
    VGroup,
    linear,
)

from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, PRIMARIO, SECUNDARIO, VERDE

from .perceptron import (
    RADIO_NODO,
    Y_EJE,
    _cuerpo,
    _entradas,
    _factor,
    _m,
    _nodo,
    _rotulo_ejemplo,
)

X_CAPAS = (-1.4, 1.5, 4.3)
TAMANOS_CAPAS = (4, 4, 2)
COLORES_CAPAS = (PRIMARIO, PRIMARIO, AMBAR)
PASO_RED = 1.15
RADIO_RED = 0.34
Y_NOMBRES = -2.15
Y_COMPOSICION = -3.15

ENTRADAS_MINI = (2, 1)
PESOS_OCULTA = ((1, 2), (3, -1), (1, 1))
PESOS_SALIDA = (2, -1, 1)
X_MINI = (-5.0, -2.4, 0.2)
Y_ENTRADAS_MINI = (1.2, -0.4)
Y_OCULTAS_MINI = (1.75, 0.4, -0.95)
Y_SALIDA_MINI = 0.4
RADIO_MINI = 0.38
LUGAR_PESO_OCULTA = 0.8
LUGAR_PESO_SALIDA = 0.55
X_IGUAL = 2.0
Y_CUENTAS = (1.75, 0.95, 0.15, -0.65)
Y_NOMBRES_MINI = -1.8
Y_COMPOSICION_MINI = -2.8


def _conexion(origen, destino):
    direccion = destino - origen
    direccion = direccion / np.linalg.norm(direccion)
    linea = Line(
        origen + direccion * RADIO_NODO, destino - direccion * RADIO_RED,
        color=SECUNDARIO, stroke_width=1.6,
    )
    return linea.set_stroke(opacity=0.45)


def _arista_mini(origen, destino):
    direccion = destino - origen
    direccion = direccion / np.linalg.norm(direccion)
    return Line(
        origen + direccion * RADIO_MINI, destino - direccion * RADIO_MINI,
        color=SECUNDARIO, stroke_width=2.2,
    ).set_stroke(opacity=0.75)


def _peso_mini(valor, arista, lugar):
    numero = _m(f"{valor}", VERDE, 0.5)
    fondo = Rectangle(
        width=numero.width + 0.14, height=numero.height + 0.1,
        stroke_width=0, fill_color=FONDO, fill_opacity=1.0,
    )
    return VGroup(fondo, numero).move_to(arista.point_from_proportion(lugar))


def _neurona_mini(centro, color, rotulo, color_rotulo, escala):
    nodo = _nodo(centro, RADIO_MINI, color)
    return VGroup(nodo, _m(rotulo, color_rotulo, escala).move_to(centro))


def _llegadas_mini(origenes, destino, pesos, lugar):
    aristas = [_arista_mini(origen, destino) for origen in origenes]
    marcas = [_peso_mini(p, a, lugar) for p, a in zip(pesos, aristas)]
    return aristas, marcas


def _cuenta_mini(nombre, color, entradas, color_entradas, pesos, y):
    partes = [nombre, "="]
    for k, (entrada, peso) in enumerate(zip(entradas, pesos)):
        if k:
            partes.append("+")
        partes += [_factor(entrada), r"\cdot", _factor(peso)]
    resultado = sum(e * p for e, p in zip(entradas, pesos))
    partes += ["=", f"{resultado}"]

    formula = MathTex(*partes, color=CLARO).scale(0.7)
    formula[0].set_color(color)
    formula[-1].set_color(color)
    for k in range(len(entradas)):
        formula[2 + 4 * k].set_color(color_entradas)
        formula[4 + 4 * k].set_color(VERDE)
    igual = formula[1].get_center()
    formula.shift([X_IGUAL - igual[0], y - igual[1], 0])
    return formula, resultado


def _pulsos(scene, aristas, pesos):
    puntos = [Dot(color=VERDE, radius=0.06).move_to(a.get_start())
              for a in aristas]
    scene.add(*puntos)
    scene.play(
        *[MoveAlongPath(p, a) for p, a in zip(puntos, aristas)],
        *[Indicate(p[1], color=VERDE, scale_factor=1.3) for p in pesos],
        run_time=0.6, rate_func=linear,
    )
    return puntos


def _mostrar_mini(scene, entradas, ocultas, salida, llegadas):
    scene.play(
        FadeIn(_rotulo_ejemplo(), shift=RIGHT * 0.15),
        LaggedStart(*[FadeIn(n, scale=0.6) for n in entradas], lag_ratio=0.2),
        LaggedStart(*[FadeIn(n, scale=0.6) for n in ocultas], lag_ratio=0.2),
        FadeIn(salida, scale=0.6),
        run_time=0.9,
    )
    scene.play(
        *[Create(a) for aristas, _ in llegadas for a in aristas],
        run_time=0.8,
    )
    scene.play(
        LaggedStart(*[FadeIn(p, scale=0.6) for _, pesos in llegadas for p in pesos],
                    lag_ratio=0.1),
        run_time=0.9,
    )
    scene.next_slide()


def _calcular_mini(scene, neurona, color, llegadas, cuenta, numero):
    nodo, etiqueta = neurona
    puntos = _pulsos(scene, *llegadas)
    scene.play(
        *[FadeOut(p, scale=0.2) for p in puntos],
        Indicate(nodo, color=color, scale_factor=1.12),
        FadeIn(cuenta, shift=RIGHT * 0.12),
        run_time=0.7,
    )
    scene.play(
        FadeOut(etiqueta),
        TransformFromCopy(cuenta[-1], numero),
        run_time=0.6,
    )


def _componer_mini(scene, valores_oculta, valor_salida):
    nombres_capas = VGroup(
        _m("f_1", PRIMARIO, 0.7).move_to([X_MINI[1], Y_NOMBRES_MINI, 0]),
        _m("f_2", AMBAR, 0.7).move_to([X_MINI[2], Y_NOMBRES_MINI, 0]),
    )
    entradas_texto = r",\ ".join(f"{v}" for v in ENTRADAS_MINI)
    ocultas_texto = r",\ ".join(f"{v}" for v in valores_oculta)
    composicion = MathTex(
        r"\hat{y}", "=", "f_2", r"\big(", "f_1", "(", entradas_texto, ")",
        r"\big)", "=", "f_2", "(", ocultas_texto, ")", "=",
        f"{valor_salida}", color=CLARO,
    ).scale(0.85).move_to([0, Y_COMPOSICION_MINI, 0])
    for i, color in ((0, AMBAR), (2, AMBAR), (4, PRIMARIO), (6, VERDE),
                     (10, AMBAR), (12, PRIMARIO), (15, AMBAR)):
        composicion[i].set_color(color)

    scene.play(
        LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in nombres_capas],
                    lag_ratio=0.25),
        run_time=0.7,
    )
    scene.play(FadeIn(composicion[:9], shift=UP * 0.1), run_time=0.8)
    scene.play(FadeIn(composicion[9:14], shift=RIGHT * 0.1), run_time=0.7)
    scene.play(FadeIn(composicion[14:], shift=RIGHT * 0.1), run_time=0.5)
    scene.wait(0.4)
    scene.next_slide()


def _ejemplo(scene, anteriores):
    centros_entrada = [np.array([X_MINI[0], y, 0.0]) for y in Y_ENTRADAS_MINI]
    centros_oculta = [np.array([X_MINI[1], y, 0.0]) for y in Y_OCULTAS_MINI]
    centro_salida = np.array([X_MINI[2], Y_SALIDA_MINI, 0.0])
    nombres_oculta = [f"h_{j + 1}" for j in range(len(centros_oculta))]

    entradas = [
        _neurona_mini(c, VERDE, f"{v}", CLARO, 0.65)
        for v, c in zip(ENTRADAS_MINI, centros_entrada)
    ]
    ocultas = [
        _neurona_mini(c, PRIMARIO, nombre, PRIMARIO, 0.55)
        for nombre, c in zip(nombres_oculta, centros_oculta)
    ]
    salida = _neurona_mini(centro_salida, AMBAR, r"\hat{y}", AMBAR, 0.62)

    llegadas_oculta = [
        _llegadas_mini(centros_entrada, c, pesos, LUGAR_PESO_OCULTA)
        for c, pesos in zip(centros_oculta, PESOS_OCULTA)
    ]
    llegadas_salida = _llegadas_mini(
        centros_oculta, centro_salida, PESOS_SALIDA, LUGAR_PESO_SALIDA,
    )

    cuentas, valores_oculta = [], []
    for nombre, pesos, y in zip(nombres_oculta, PESOS_OCULTA, Y_CUENTAS):
        formula, valor = _cuenta_mini(
            nombre, PRIMARIO, ENTRADAS_MINI, CLARO, pesos, y,
        )
        cuentas.append(formula)
        valores_oculta.append(valor)
    cuenta_salida, valor_salida = _cuenta_mini(
        r"\hat{y}", AMBAR, valores_oculta, PRIMARIO, PESOS_SALIDA,
        Y_CUENTAS[-1],
    )
    numeros_oculta = [
        _m(f"{v}", CLARO, 0.65).move_to(c)
        for v, c in zip(valores_oculta, centros_oculta)
    ]
    numero_salida = _m(f"{valor_salida}", AMBAR, 0.65).move_to(centro_salida)

    scene.play(FadeOut(anteriores), run_time=0.7)
    _mostrar_mini(scene, entradas, ocultas, salida,
                  [*llegadas_oculta, llegadas_salida])

    for neurona, llegadas, cuenta, numero in zip(
        ocultas, llegadas_oculta, cuentas, numeros_oculta,
    ):
        _calcular_mini(scene, neurona, PRIMARIO, llegadas, cuenta, numero)
    scene.next_slide()

    _calcular_mini(scene, salida, AMBAR, llegadas_salida, cuenta_salida,
                   numero_salida)
    scene.next_slide()

    _componer_mini(scene, valores_oculta, valor_salida)


def _red(nodos_entrada):
    capas = [[n.get_center() for n in nodos_entrada]]
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
    return nodos_red, tramos


def _propagar(scene, tramos, nodos_red):
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


def _componer(scene, nombres, etiquetas_x):
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
    return composicion


def construir(scene):
    encabezado = hacer_titulo("De la neurona a la red")

    nodos, etiquetas_x, aristas, _, puntos_suspensivos = _entradas()
    cuerpo, sigma = _cuerpo()
    perceptron = VGroup(
        *nodos, *etiquetas_x, puntos_suspensivos, *aristas, cuerpo, sigma,
    )
    nodos_red, tramos = _red(nodos)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(*[FadeIn(m) for m in perceptron], run_time=0.8)
    scene.play(FadeOut(VGroup(puntos_suspensivos, *aristas)), run_time=0.6)

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

    _propagar(scene, tramos, nodos_red)

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

    composicion = _componer(scene, nombres, etiquetas_x)

    _ejemplo(scene, VGroup(
        *nodos, *etiquetas_x, *[n for capa in nodos_red for n in capa],
        *tramos, nombres, composicion,
    ))
