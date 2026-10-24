import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    Transform,
    TransformFromCopy,
    VGroup,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, PRIMARIO, SECUNDARIO, VERDE

CLASES = ("gato", "perro", "pájaro", "caballo")
PUNTUACIONES = (2.0, -1.0, 0.5, 3.0)
DESTACADA = 0

ANCHO_BARRA = 1.0
SEPARACION = 2.45
Y_BASE = -1.5
ALTO_MAX = 2.7
Y_CABECERA = 2.0

Y_CENTRO = -0.45


def _xs():
    n = len(CLASES)
    return [(i - (n - 1) / 2) * SEPARACION for i in range(n)]


def _altos(valores):
    tope = max(abs(v) for v in valores)
    return [ALTO_MAX * v / tope for v in valores]


def _barras(valores, color):
    barras = VGroup()
    for x, alto in zip(_xs(), _altos(valores)):
        barra = Rectangle(
            width=ANCHO_BARRA, height=max(abs(alto), 0.04),
            stroke_color=color, stroke_width=2.5,
            fill_color=color, fill_opacity=0.3,
        )
        barra.move_to([x, Y_BASE + alto / 2, 0])
        barras.add(barra)
    return barras


def _valores(valores, color, formato="{:.2f}"):
    etiquetas = VGroup()
    for x, valor, alto in zip(_xs(), valores, _altos(valores)):
        etiqueta = texto(formato.format(valor), 20, color=color)
        etiqueta.move_to([x, Y_BASE + alto + (0.26 if alto >= 0 else -0.26), 0])
        etiquetas.add(etiqueta)
    return etiquetas


def _fraccion(arriba, abajo, buff=0.16):
    ancho = max(arriba.width, abajo.width) + 0.26
    raya = Line(LEFT * ancho / 2, RIGHT * ancho / 2,
                color=SECUNDARIO, stroke_width=2.6)
    arriba.next_to(raya, UP, buff=buff)
    abajo.next_to(raya, DOWN, buff=buff)
    return VGroup(raya, arriba, abajo)


def _euler(exponenciales):
    ejes = Axes(
        x_range=[-1.6, 3.4, 1], y_range=[0, 22, 5],
        x_length=6.2, y_length=3.6,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5, "include_ticks": False,
            "tip_width": 0.16, "tip_height": 0.16,
        },
    ).move_to([0, Y_CENTRO, 0])
    curva = ejes.plot(lambda x: float(np.exp(x)), x_range=[-1.6, 3.15],
                      color=AMBAR)
    curva.set_stroke(width=4)
    etiqueta = MathTex("e^x", color=AMBAR).scale(0.95)
    etiqueta.next_to(ejes.c2p(2.75, 15), LEFT, buff=0.15)

    marcas = VGroup()
    for nombre, s, e in zip(CLASES, PUNTUACIONES, exponenciales):
        marcas.add(VGroup(
            Line(ejes.c2p(s, 0), ejes.c2p(s, e), color=SECUNDARIO,
                 stroke_width=1.6).set_stroke(opacity=0.45),
            Dot(ejes.c2p(s, e), radius=0.07, color=CLARO),
            texto(nombre, 15, color=SECUNDARIO).next_to(
                ejes.c2p(s, 0), DOWN, buff=0.16,
            ),
        ))
    return ejes, VGroup(curva, etiqueta), marcas


def _fila(sumandos, total_mob):
    piezas, cruces = [], []
    for i, sumando in enumerate(sumandos):
        if i:
            mas = MathTex("+", color=SECUNDARIO).scale(0.85)
            piezas.append(mas)
            cruces.append(mas)
        piezas.append(sumando)
    cierre = VGroup(
        MathTex("=", color=SECUNDARIO).scale(0.85), total_mob,
    ).arrange(RIGHT, buff=0.26)
    piezas.append(cierre)
    fila = VGroup(*piezas).arrange(RIGHT, buff=0.26)
    return fila.move_to([0, Y_BASE - 1.15, 0]), sumandos, cruces, cierre


def _leyenda():
    entradas = (
        (r"\mathbf{z}", CLARO, "los outputs de la red"),
        ("z_i", AMBAR, "el output de la clase que miramos"),
        (r"\textstyle\sum", VERDE, "sumar todos los outputs"),
    )
    leyenda = VGroup()
    for fila, (simbolo, color, glosa) in enumerate(entradas):
        y = -1.25 - fila * 0.66
        leyenda.add(
            MathTex(simbolo, color=color).scale(0.8).move_to([-2.0, y, 0]),
            texto(glosa, 19, color=SECUNDARIO).next_to(
                np.array([-1.55, y, 0]), RIGHT, buff=0,
            ),
        )
    return leyenda


def _puntuaciones(scene):
    suelo = Line(
        [_xs()[0] - 0.9, Y_BASE, 0], [_xs()[-1] + 0.9, Y_BASE, 0],
        color=SECUNDARIO, stroke_width=2, stroke_opacity=0.55,
    )
    cabeceras = VGroup(*[
        texto(nombre, 20, color=SECUNDARIO).move_to([x, Y_CABECERA, 0])
        for nombre, x in zip(CLASES, _xs())
    ])
    barras = _barras(PUNTUACIONES, PRIMARIO)
    etiquetas = _valores(PUNTUACIONES, PRIMARIO, formato="{:.1f}")

    scene.play(Create(suelo), FadeIn(cabeceras), run_time=0.7)
    scene.play(
        LaggedStart(*[FadeIn(b, shift=UP * 0.25) for b in barras],
                    lag_ratio=0.12),
        FadeIn(etiquetas),
        run_time=1.1,
    )
    scene.next_slide()
    return suelo, cabeceras, barras, etiquetas


def _formula(scene, panel):
    general = VGroup(
        MathTex(r"\mathrm{softmax}(\mathbf{z})_i", "=", color=CLARO),
        _fraccion(
            MathTex("e^{z_i}", color=AMBAR),
            MathTex(r"\sum_{j=1}^{N} e^{z_j}", color=VERDE),
        ),
    ).arrange(RIGHT, buff=0.3).scale(1.15).move_to([0, 0.65, 0])
    leyenda = _leyenda()

    scene.play(*[FadeOut(p) for p in panel], run_time=0.7)
    scene.play(FadeIn(general, shift=UP * 0.15), run_time=0.9)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15) for f in leyenda],
                    lag_ratio=0.18),
        run_time=1.3,
    )
    scene.next_slide()
    return general, leyenda


def _exponencial(scene, general, leyenda, exponenciales):
    ejes, curva, marcas = _euler(exponenciales)
    scene.play(FadeOut(general), FadeOut(leyenda), run_time=0.6)
    scene.play(Create(ejes), run_time=0.7)
    scene.play(Create(curva), run_time=1.0)
    scene.play(
        LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in marcas],
                    lag_ratio=0.15),
        run_time=1.2,
    )
    scene.next_slide()
    return ejes, curva, marcas


def _sumar(scene, panel, euler, exponenciales):
    _, _, barras, etiquetas = panel
    fila, sumandos, cruces, cierre = _fila(
        [texto(f"{e:.2f}", 26, color=AMBAR) for e in exponenciales],
        texto(f"{sum(exponenciales):.2f}", 30, color=CLARO),
    )

    scene.play(
        *[FadeOut(m) for m in euler],
        *[FadeIn(p) for p in panel],
        run_time=0.85,
    )
    scene.play(
        Transform(barras, _barras(exponenciales, AMBAR)),
        Transform(etiquetas, _valores(exponenciales, AMBAR)),
        run_time=1.2,
    )

    scene.play(
        *[TransformFromCopy(etiquetas[i], s) for i, s in enumerate(sumandos)],
        run_time=1.1,
    )
    scene.play(
        LaggedStart(*[FadeIn(c) for c in cruces], lag_ratio=0.15),
        run_time=0.5,
    )
    scene.play(FadeIn(cierre, shift=RIGHT * 0.2), run_time=0.8)
    scene.next_slide()
    return fila, cierre


def _dividir(scene, panel, fila, cierre, exponenciales, probabilidades,
             porcentajes):
    _, _, barras, etiquetas = panel
    total = sum(exponenciales)
    fila_div, _, _, _ = _fila(
        [MathTex(rf"\frac{{{e:.2f}}}{{{total:.2f}}}", color=AMBAR).scale(0.85)
         for e in exponenciales],
        MathTex(rf"\frac{{{total:.2f}}}{{{total:.2f}}}", color=CLARO).scale(0.85),
    )
    fila_uno, _, _, _ = _fila(
        [texto(f"{p:.2f}", 26, color=VERDE) for p in probabilidades],
        texto("1", 30, color=CLARO),
    )
    fila_pct, _, _, _ = _fila(
        [texto(f"{p:.0f}%", 26, color=VERDE) for p in porcentajes],
        texto(f"{sum(porcentajes):.0f}%", 30, color=CLARO),
    )

    scene.play(Indicate(cierre, color=VERDE, scale_factor=1.15),
               run_time=0.7)
    scene.play(Transform(fila, fila_div), run_time=1.3)
    scene.next_slide()

    scene.play(
        Transform(fila, fila_uno),
        Transform(barras, _barras(probabilidades, VERDE)),
        Transform(etiquetas, _valores(probabilidades, VERDE)),
        run_time=1.3,
    )
    scene.next_slide()

    scene.play(
        Transform(fila, fila_pct),
        Transform(etiquetas, _valores(porcentajes, VERDE, formato="{:.0f}%")),
        run_time=1.2,
    )
    scene.next_slide()


def _ganadora(scene, panel, probabilidades):
    _, cabeceras, barras, etiquetas = panel
    ganadora = max(range(len(CLASES)), key=lambda i: probabilidades[i])
    resto = [i for i in range(len(CLASES)) if i != ganadora]
    scene.play(
        *[barras[i].animate.set_opacity(0.18) for i in resto],
        *[cabeceras[i].animate.set_opacity(0.3) for i in resto],
        *[etiquetas[i].animate.set_opacity(0.3) for i in resto],
        barras[ganadora].animate.set_fill(VERDE, opacity=0.55),
        cabeceras[ganadora].animate.set_color(CLARO).scale(1.2),
        etiquetas[ganadora].animate.set_color(CLARO).scale(1.2),
        run_time=1.0,
    )
    scene.play(
        Indicate(VGroup(barras[ganadora], cabeceras[ganadora],
                        etiquetas[ganadora]),
                 color=CLARO, scale_factor=1.06),
        run_time=0.9,
    )
    scene.wait(0.4)

    scene.next_slide()


def construir(scene):
    encabezado = hacer_titulo("Softmax")

    exponenciales = [float(np.exp(s)) for s in PUNTUACIONES]
    total = sum(exponenciales)
    probabilidades = [e / total for e in exponenciales]
    porcentajes = [p * 100 for p in probabilidades]

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    panel = _puntuaciones(scene)
    general, leyenda = _formula(scene, panel)
    euler = _exponencial(scene, general, leyenda, exponenciales)
    fila, cierre = _sumar(scene, panel, euler, exponenciales)
    _dividir(scene, panel, fila, cierre, exponenciales, probabilidades,
             porcentajes)
    _ganadora(scene, panel, probabilidades)
