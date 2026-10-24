import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    ReplacementTransform,
    RoundedRectangle,
    TransformFromCopy,
    VGroup,
    Write,
)

from componentes import titulo as hacer_titulo
from estilo import CLARO, FONDO, MORADO, SECUNDARIO, VERDE

from . import _backprop

ANCHO_NODO, ALTO_NODO = 1.4, 1.0
RADIO_OP = 0.26
PASO_X = 1.6
PASO_Y = 1.35
X_INICIO = -3 * PASO_X
Y_INICIO = 2.0
Y_TEXTO = -2.4

VALORES = {
    "a": ("2", (0, 0)),
    "b": ("-3", (0, 2)),
    "c": ("10", (2, 3)),
    "f": ("-2", (4, 4)),
    "e": ("-6", (2, 1)),
    "d": ("4", (4, 2)),
    "L": ("-8", (6, 3)),
}
HOJAS = ("a", "b", "c", "f")

OPERACIONES = (
    (r"\times", ("a", "b"), "e", (1, 1)),
    ("+", ("e", "c"), "d", (3, 2)),
    (r"\times", ("d", "f"), "L", (5, 3)),
)

PASOS = (
    ("d", 2, "1", "(-2)", "-2"),
    ("f", 2, "1", "4", "4"),
    ("e", 1, "(-2)", "1", "-2"),
    ("c", 1, "(-2)", "1", "-2"),
    ("a", 0, "(-2)", "(-3)", "6"),
    ("b", 0, "(-2)", "2", "-4"),
)


def _pos(columna, fila):
    return np.array([X_INICIO + columna * PASO_X, Y_INICIO - fila * PASO_Y / 2, 0])


def _nodo(nombre, dato, centro):
    caja = RoundedRectangle(
        width=ANCHO_NODO, height=ALTO_NODO, corner_radius=0.12,
        stroke_color=SECUNDARIO, stroke_width=2.5,
    ).set_fill(SECUNDARIO, opacity=0.08).move_to(centro)
    division = Line(caja.get_left(), caja.get_right())
    division.set_stroke(color=SECUNDARIO, width=1.5, opacity=0.5)
    valor = MathTex(f"{nombre} = {dato}", color=CLARO).scale(0.7)
    valor.move_to(centro + UP * ALTO_NODO / 4)
    return VGroup(caja, division, valor)


def _hueco(nodo):
    return nodo[0].get_center() + DOWN * ALTO_NODO / 4


def _operacion(simbolo, centro):
    return VGroup(
        Circle(radius=RADIO_OP, color=SECUNDARIO, stroke_width=2.5)
        .set_fill(FONDO, opacity=1.0),
        MathTex(simbolo, color=SECUNDARIO).scale(0.7),
    ).move_to(centro)


def _flecha(inicio, fin):
    return Arrow(
        inicio, fin, color=SECUNDARIO, stroke_width=3, buff=0,
        tip_length=0.16,
    ).set_stroke(opacity=0.85)


def _hacia(op, desde):
    direccion = op.get_center() - desde
    return op.get_center() - direccion / np.linalg.norm(direccion) * RADIO_OP


def _desde(op, hacia):
    direccion = hacia - op.get_center()
    return op.get_center() + direccion / np.linalg.norm(direccion) * RADIO_OP


def _viaje(flecha, color=VERDE):
    punto = Dot(flecha.get_start(), radius=0.06, color=color)
    return punto, MoveAlongPath(punto, Line(flecha.get_start(), flecha.get_end()))


def _parcial(de, respecto):
    return rf"\frac{{\partial {de}}}{{\partial {respecto}}}"


def _cadena(destino, salida, n_llega, n_local, resultado):
    formula = MathTex(
        _parcial("L", destino), "=", _parcial("L", salida), r"\cdot",
        _parcial(salida, destino), "=", n_llega, r"\cdot", n_local, "=",
        resultado, color=CLARO,
    ).scale(0.85).move_to([0, Y_TEXTO, 0])
    for i in (0, 2, 6, 10):
        formula[i].set_color(MORADO)
    return formula


def _grafo():
    nodos = {
        nombre: _nodo(nombre, dato, _pos(*celda))
        for nombre, (dato, celda) in VALORES.items()
    }
    huecos = {nombre: _hueco(nodo) for nombre, nodo in nodos.items()}

    ops, entrantes, salientes = [], {}, []
    for simbolo, entradas, salida, celda in OPERACIONES:
        op = _operacion(simbolo, _pos(*celda))
        for nombre in entradas:
            inicio = nodos[nombre][0].get_right()
            entrantes[nombre] = _flecha(inicio, _hacia(op, inicio))
        fin = nodos[salida][0].get_left()
        salientes.append(_flecha(_desde(op, fin), fin))
        ops.append(op)
    return nodos, huecos, ops, entrantes, salientes


def _operar(scene, flechas, op, saliente, resultado):
    scene.play(*[Create(f) for f in flechas], FadeIn(op, scale=0.6),
               run_time=0.5)
    viajes = [_viaje(f) for f in flechas]
    scene.play(*[m for _, m in viajes], run_time=0.45)
    scene.remove(*[p for p, _ in viajes])
    punto, movimiento = _viaje(saliente)
    scene.play(_backprop.pulso(op[0], VERDE), Create(saliente),
               movimiento, run_time=0.45)
    scene.remove(punto)
    scene.play(FadeIn(resultado, shift=RIGHT * 0.15), run_time=0.5)


def _hacia_adelante(scene, nodos, ops, entrantes, salientes):
    scene.play(
        LaggedStart(*[FadeIn(nodos[h], shift=RIGHT * 0.2) for h in HOJAS],
                    lag_ratio=0.15),
        run_time=1.0,
    )
    for (_, entradas, salida, _), op, saliente in zip(
        OPERACIONES, ops, salientes,
    ):
        flechas = [entrantes[n] for n in entradas]
        _operar(scene, flechas, op, saliente, nodos[salida])
    scene.next_slide()


def construir(scene):
    encabezado = hacer_titulo("Un ejemplo sencillo")
    nodos, huecos, ops, entrantes, salientes = _grafo()

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    _hacia_adelante(scene, nodos, ops, entrantes, salientes)

    funcion = MathTex(r"L = (a \cdot b + c) \cdot f", color=CLARO).scale(0.85)
    funcion.move_to([0, Y_TEXTO, 0])
    scene.play(Write(funcion), run_time=1.2)
    scene.next_slide()

    inicio = MathTex(
        r"\frac{\partial L}{\partial L}", "=", "1", color=CLARO,
    ).scale(0.85).move_to([0, Y_TEXTO, 0])
    inicio[0].set_color(MORADO)
    inicio[2].set_color(MORADO)
    uno = MathTex("1", color=MORADO).scale(0.7).move_to(huecos["L"])
    scene.play(FadeOut(funcion), FadeIn(inicio), run_time=0.6)
    scene.play(
        ReplacementTransform(inicio[2].copy(), uno),
        _backprop.pulso(nodos["L"][0], MORADO), run_time=0.8,
    )
    valores_grad = {"L": "1"}
    anterior = inicio
    scene.next_slide()

    for destino, i_op, n_llega, n_local, resultado in PASOS:
        salida = OPERACIONES[i_op][2]
        ficha = _backprop.ficha(valores_grad[salida]).move_to(huecos[salida])
        scene.play(FadeIn(ficha, scale=0.6), run_time=0.4)
        _backprop.llevar(scene, [ficha], [ops[i_op].get_center()],
                         [salientes[i_op]], run_time=0.6)

        formula = _cadena(destino, salida, n_llega, n_local, resultado)
        scene.play(FadeOut(anterior), Write(formula[:5]), run_time=0.9)
        scene.play(
            FadeIn(formula[5]), FadeIn(formula[7]),
            TransformFromCopy(formula[2], formula[6]),
            TransformFromCopy(formula[4], formula[8]),
            run_time=0.9,
        )
        scene.play(Write(formula[9:]), run_time=0.5)

        _backprop.llevar(scene, [ficha], [huecos[destino]],
                         [entrantes[destino]], run_time=0.6)
        nuevo = MathTex(resultado, color=MORADO).scale(0.7)
        nuevo.move_to(huecos[destino])
        scene.play(
            ReplacementTransform(ficha, nuevo),
            _backprop.pulso(nodos[destino][0], MORADO), run_time=0.6,
        )
        valores_grad[destino] = resultado
        anterior = formula
        scene.next_slide()
