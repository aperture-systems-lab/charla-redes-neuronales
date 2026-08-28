"""Diapositiva 18 — Softmax.

La respuesta a la pregunta de la 17: cómo se convierte un puñado de números
sueltos en algo que se pueda leer.

Va **de uno en uno**: en cada momento hay una sola cosa en pantalla y ocupa todo
el sitio, en vez de amontonar barras, curva y fórmulas a la vez. El orden es el
del razonamiento, y a las barras se vuelve dos veces, que es donde se ve el
efecto de cada paso:

1. las puntuaciones que escupe la red —hay una negativa y no suman nada—,
2. la fórmula, sola y grande,
3. la curva de ``e^x`` con esas cuatro puntuaciones encima: el porqué del paso,
4. de vuelta a las barras, que se vuelven exponenciales,
5. la fórmula aplicada a "gato", con los números metidos dentro,
6. de vuelta a las barras, ya probabilidades, que suman 1.

Los colores hacen de pegamento entre pantallas: el numerador siempre ámbar y el
denominador siempre verde, en la fórmula general y en la aplicada, así se ve qué
trozo es cada cosa sin tener que decirlo.

Animada en Manim en vez de usar ``assets/softmax.png``, que es una captura de
vídeo en inglés.
"""

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
DESTACADA = 0            # la clase que se lleva el desarrollo de la fórmula

# Como en cada pantalla solo hay una cosa, todo va a lo grande.
ANCHO_BARRA = 1.0
SEPARACION = 2.45
Y_BASE = -1.5
ALTO_MAX = 2.7
Y_CABECERA = 2.0

Y_CENTRO = -0.45         # centro óptico de lo que deja libre el título


def _xs():
    n = len(CLASES)
    return [(i - (n - 1) / 2) * SEPARACION for i in range(n)]


def _altos(valores):
    """Altura de cada barra, normalizada al valor más grande en magnitud."""
    tope = max(abs(v) for v in valores)
    return [ALTO_MAX * v / tope for v in valores]


def _barras(valores, color):
    """Una barra por clase, hacia arriba o hacia abajo según el signo."""
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
    """El número de cada barra, siempre por el lado por el que crece."""
    etiquetas = VGroup()
    for x, valor, alto in zip(_xs(), valores, _altos(valores)):
        etiqueta = texto(formato.format(valor), 20, color=color)
        etiqueta.move_to([x, Y_BASE + alto + (0.26 if alto >= 0 else -0.26), 0])
        etiquetas.add(etiqueta)
    return etiquetas


def _fraccion(arriba, abajo, buff=0.16):
    """Una fracción montada a mano.

    Con ``\\frac`` de LaTeX el numerador y el denominador salen pegados en un
    solo mobject y no se pueden pintar por separado; aquí cada mitad es suya y
    lleva su color, que es lo que hace legible el paralelismo entre la fórmula
    general y la aplicada.
    """
    ancho = max(arriba.width, abajo.width) + 0.26
    raya = Line(LEFT * ancho / 2, RIGHT * ancho / 2,
                color=SECUNDARIO, stroke_width=2.6)
    arriba.next_to(raya, UP, buff=buff)
    abajo.next_to(raya, DOWN, buff=buff)
    return VGroup(raya, arriba, abajo)


def _euler(exponenciales):
    """La curva de ``e^x`` con las cuatro puntuaciones puestas encima.

    Es el porqué del paso, dibujado: nunca baja de cero —de ahí que se acaben
    los negativos— y sube tan rápido que la puntuación mayor se despega de las
    otras tres, que quedan aplastadas contra el eje.
    """
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


def construir(scene):
    encabezado = hacer_titulo("Softmax")

    exponenciales = [float(np.exp(s)) for s in PUNTUACIONES]
    total = sum(exponenciales)
    probabilidades = [e / total for e in exponenciales]
    # En porcentajes se leen mucho mejor de un vistazo, y redondeados a entero
    # los cuatro suman 100 clavados, así que la comprobación de abajo cuadra.
    porcentajes = [p * 100 for p in probabilidades]

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
    # Las piezas del panel se listan sueltas: un ``FadeOut`` sobre un ``VGroup``
    # montado al vuelo anima el grupo pero deja en escena a sus miembros, que se
    # habían añadido por su cuenta, y el panel se quedaba pegado detrás.
    panel = (suelo, cabeceras, barras, etiquetas)

    # --- Pantalla 2: la fórmula tal cual se escribe, y su leyenda ----------
    general = VGroup(
        MathTex(r"\mathrm{softmax}(\mathbf{z})_i", "=", color=CLARO),
        _fraccion(
            MathTex("e^{z_i}", color=AMBAR),
            MathTex(r"\sum_{j=1}^{N} e^{z_j}", color=VERDE),
        ),
    ).arrange(RIGHT, buff=0.3).scale(1.15).move_to([0, 0.65, 0])

    # Cada símbolo, por su nombre. Los colores son los mismos que en la fórmula,
    # así que la leyenda se lee sin tener que ir señalando.
    entradas = (
        (r"\mathbf{z}", CLARO, "los outputs de la red"),
        ("z_i", AMBAR, "el output de la clase que miramos"),
        # Sin los límites de arriba y abajo: aquí lo que se explica es el
        # símbolo, y con ellos crecía tanto que se subía a la fila anterior.
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

    # --- La suma, escrita en una línea bajo las barras ---------------------
    # Rematada con un ``=``: puesta en dos pisos con una raya en medio se leía
    # como una división, no como una suma.
    def _fila(sumandos, total_mob):
        """Monta ``a + b + c + d = total`` con las piezas que se le den."""
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

    # Los cuatro estados por los que pasa la fila de abajo: la suma de las
    # exponenciales, esa misma suma dividida por el total **en los dos lados**
    # —que es lo que justifica que el resultado sea 1—, resuelta, y en tantos
    # por ciento.
    fila_exp, sumandos, cruces, cierre_exp = _fila(
        [texto(f"{e:.2f}", 26, color=AMBAR) for e in exponenciales],
        texto(f"{total:.2f}", 30, color=CLARO),
    )
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

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)

    # 1. Lo que escupe la red: hay una negativa y no suman nada. Sin rótulo:
    # esto no es un paso de la receta todavía, es el material de partida, y los
    # propios números lo dicen.
    scene.play(Create(suelo), FadeIn(cabeceras), run_time=0.7)
    scene.play(
        LaggedStart(*[FadeIn(b, shift=UP * 0.25) for b in barras],
                    lag_ratio=0.12),
        FadeIn(etiquetas),
        run_time=1.1,
    )
    scene.next_slide()

    # 2. La fórmula, sola y a lo grande, y debajo qué es cada símbolo.
    scene.play(*[FadeOut(p) for p in panel], run_time=0.7)
    scene.play(FadeIn(general, shift=UP * 0.15), run_time=0.9)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15) for f in leyenda],
                    lag_ratio=0.18),
        run_time=1.3,
    )
    scene.next_slide()

    # 3. Por qué la exponencial: la curva, con las cuatro puntuaciones encima.
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

    # 4. Vuelta a las barras: ahora son las exponenciales.
    scene.play(
        FadeOut(ejes), FadeOut(curva), FadeOut(marcas),
        *[FadeIn(p) for p in panel],
        run_time=0.85,
    )
    scene.play(
        Transform(barras, _barras(exponenciales, AMBAR)),
        Transform(etiquetas, _valores(exponenciales, AMBAR)),
        run_time=1.2,
    )

    # Y se suman a la vista: los cuatro bajan de sus barras, se ponen en fila y
    # el igual remata con el total, que es justo el número que hace de divisor.
    scene.play(
        *[TransformFromCopy(etiquetas[i], s) for i, s in enumerate(sumandos)],
        run_time=1.1,
    )
    scene.play(
        LaggedStart(*[FadeIn(c) for c in cruces], lag_ratio=0.15),
        run_time=0.5,
    )
    scene.play(FadeIn(cierre_exp, shift=RIGHT * 0.2), run_time=0.8)
    scene.next_slide()

    # 5. Dividir por el total, y no solo a la izquierda: partiendo los dos
    # lados de la igualdad se ve de dónde sale el 1, en vez de tener que
    # creérselo.
    scene.play(Indicate(cierre_exp, color=VERDE, scale_factor=1.15),
               run_time=0.7)
    scene.play(Transform(fila_exp, fila_div), run_time=1.3)
    scene.next_slide()

    scene.play(
        Transform(fila_exp, fila_uno),
        Transform(barras, _barras(probabilidades, VERDE)),
        Transform(etiquetas, _valores(probabilidades, VERDE)),
        run_time=1.3,
    )
    scene.next_slide()

    # 6. Y en tantos por ciento, que es como se dice en voz alta.
    scene.play(
        Transform(fila_exp, fila_pct),
        Transform(etiquetas, _valores(porcentajes, VERDE, formato="{:.0f}%")),
        run_time=1.2,
    )
    scene.next_slide()

    # 7. Y la decisión: la clase que se lleva el porcentaje más alto. El resto
    # se apaga en vez de dibujar nada nuevo, que es lo que hace evidente cuál
    # es sin tener que anunciarlo.
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
