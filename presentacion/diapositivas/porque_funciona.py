"""Diapositiva 15 — Por qué funciona.

La anterior enseñó *que* la red se curva. Esta contesta *por qué*: el teorema de
aproximación universal. Con una sola capa oculta —o sea, una red de dos capas—
se aproxima cualquier función continua tan bien como se quiera; lo único que
hace falta es ponerle neuronas.

El montaje es el del dibujo clásico del teorema: la red en rombo, con la entrada
abajo, la salida arriba y **una única fila** de neuronas en medio, todas colgando
de las dos. A la derecha, unos datos con forma fea y el ajuste de la red encima.

Lo que se anima es una sola cosa, que es justo el enunciado: la fila se llena de
neuronas —4, 8, 16— y el ajuste se pega más a los datos en cada paso, sin tocar
nada más. No hay capas nuevas ni trucos: solo más neuronas en la misma fila.

Sigue la paleta de la diapositiva anterior a propósito —datos en verde, ajuste en
la rampa de ámbar a violeta, cada neurona del color del trozo que le toca—, para
que se lea como su continuación.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Circle,
    Create,
    Dot,
    FadeIn,
    LaggedStart,
    Line,
    ManimColor,
    MathTex,
    Square,
    Transform,
    VGroup,
    VMobject,
    interpolate_color,
)

from componentes import separador, texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, FONDO, MORADO, PRIMARIO, SECUNDARIO, VERDE

# --- La red en rombo, a la izquierda ---------------------------------------
X_RED = -3.7
ANCHO_FILA = 5.2
Y_FILA = -0.1
Y_ENTRADA = -2.2
Y_SALIDA = 1.9
RADIO_EXTREMO = 0.28
LADO_NEURONA = 0.2   # con las 16 puestas la fila tiene que respirar
Y_CONTADOR = -3.0

# Las 16 posiciones de la fila no se mueven nunca: los pasos son subconjuntos
# encajados, así que al subir de 4 a 8 a 16 las neuronas que ya estaban se
# quedan quietas y solo aparecen las nuevas entre medias. Eso es lo que se
# quiere contar —añadir neuronas, no rehacer la red— y además se ve mucho más
# limpio que recolocar la fila entera en cada paso.
N_MAX = 16
PASOS = (
    tuple(range(1, N_MAX, 4)),   # 4
    tuple(range(1, N_MAX, 2)),   # 8
    tuple(range(N_MAX)),         # 16
)

# --- La gráfica, a la derecha ----------------------------------------------
CENTRO_GRAFICA = [3.5, 0.05, 0]
N_BANDAS = 8
# Divisible por 16, 8 y 4: los nodos de cada ajuste caen clavados en una muestra
# (los picos salen afilados) y las bandas de color se reparten exactas.
MUESTRAS = 144


def _objetivo(x):
    """Unos datos con forma fea: tres senos encima, ni recta ni sinusoide.

    Interesa que no se parezca a la curva de la diapositiva anterior. Si fuera
    otra vez un seno, el teorema parecería un truco para senos.
    """
    return (
        0.62 * np.sin(2 * np.pi * x)
        + 0.34 * np.sin(5.5 * np.pi * x + 1.2)
        + 0.17 * np.sin(10.5 * np.pi * x + 0.5)
    )


def _paleta(n):
    """Rampa de ámbar a violeta, la misma que usa la diapositiva del ajuste."""
    a, b = ManimColor(AMBAR), ManimColor(MORADO)
    return [interpolate_color(a, b, k / (n - 1)) for k in range(n)]


def _extremo(centro, color, simbolo):
    """Nodo de entrada o de salida, plano y con su símbolo dentro."""
    cuerpo = Circle(radius=RADIO_EXTREMO, color=color, stroke_width=3)
    cuerpo.set_fill(FONDO, opacity=1.0).move_to(centro)
    etiqueta = MathTex(simbolo, color=color).scale(0.6).move_to(centro)
    return VGroup(cuerpo, etiqueta)


def _neurona(centro, color):
    """Neurona de la fila: cajita con su codo de ReLU dentro, como en el dibujo
    clásico del teorema (allí llevan sigmoides; aquí, la activación que hemos
    enseñado)."""
    caja = Square(side_length=LADO_NEURONA, color=color, stroke_width=2.2)
    caja.set_fill(FONDO, opacity=1.0).move_to(centro)
    codo = centro + np.array([-0.01, -LADO_NEURONA * 0.2, 0.0])
    return VGroup(
        caja,
        Line(codo + LEFT * LADO_NEURONA * 0.34, codo, color=color,
             stroke_width=1.8),
        Line(codo, codo + np.array([LADO_NEURONA * 0.32, LADO_NEURONA * 0.46, 0]),
             color=color, stroke_width=1.8),
    )


def construir(scene):
    encabezado = hacer_titulo("¿Por qué funciona?")
    colores = _paleta(N_MAX)

    centro_entrada = np.array([X_RED, Y_ENTRADA, 0.0])
    centro_salida = np.array([X_RED, Y_SALIDA, 0.0])
    entrada = _extremo(centro_entrada, PRIMARIO, "x")
    salida = _extremo(centro_salida, AMBAR, "y")

    posiciones = [
        np.array([
            X_RED - ANCHO_FILA / 2 + j * ANCHO_FILA / (N_MAX - 1), Y_FILA, 0.0,
        ])
        for j in range(N_MAX)
    ]
    neuronas = [_neurona(p, colores[j]) for j, p in enumerate(posiciones)]

    def _cable(desde, hasta, color):
        """Conexión recortada en los bordes, fina: aquí manda la fila, no ella."""
        direccion = hasta - desde
        direccion = direccion / np.linalg.norm(direccion)
        linea = Line(
            desde + direccion * RADIO_EXTREMO,
            hasta - direccion * LADO_NEURONA * 0.62,
            color=color, stroke_width=1.3,
        )
        return linea.set_stroke(opacity=0.4)

    cables = [
        VGroup(
            _cable(centro_entrada, p, PRIMARIO),
            _cable(centro_salida, p, AMBAR),
        )
        for p in posiciones
    ]

    # --- La gráfica --------------------------------------------------------
    ejes = Axes(
        x_range=[0, 1, 0.25], y_range=[-1.35, 1.35, 0.5],
        x_length=5.5, y_length=3.9,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5, "include_ticks": False,
        },
        x_axis_config={"tip_width": 0.16, "tip_height": 0.16},
        y_axis_config={"include_tip": False},
    ).move_to(CENTRO_GRAFICA)

    # Mismas marcas de referencia que la diapositiva anterior, para que las dos
    # gráficas se lean a la misma escala.
    marcas = VGroup()
    for valor in (1, -1):
        marca = Line(
            ejes.c2p(0, valor) + LEFT * 0.12, ejes.c2p(0, valor) + RIGHT * 0.12,
            color=SECUNDARIO, stroke_width=2.5,
        )
        etiqueta = MathTex(str(valor), color=SECUNDARIO).scale(0.5)
        etiqueta.next_to(marca, LEFT, buff=0.12)
        marcas.add(marca, etiqueta)

    rot_x = MathTex("x", color=SECUNDARIO).scale(0.6)
    rot_x.next_to(ejes.c2p(1, 0), UP + RIGHT, buff=0.1)
    rot_y = MathTex("y", color=SECUNDARIO).scale(0.6)
    rot_y.next_to(ejes.c2p(0, 1.35), UP, buff=0.06)

    objetivo = ejes.plot(_objetivo, x_range=[0, 1], color=VERDE)
    objetivo.set_stroke(width=3)
    datos = VGroup(*[
        Dot(ejes.c2p(x, _objetivo(x)), radius=0.045, color=VERDE)
        for x in np.linspace(0.02, 0.98, 22)
    ])

    def _ajuste(n):
        """Lo que da la red con ``n`` neuronas: ``n`` tramos rectos.

        Cada ReLU aporta un codo, así que con n neuronas salen n tramos: se
        interpola la curva en n+1 nodos repartidos. El degradado va a mano, en
        bandas de color sólido, porque sobre un trazo hecho de esquinas manim no
        pinta ``set_color_by_gradient``.
        """
        nodos_x = np.linspace(0, 1, n + 1)
        xs = np.linspace(0, 1, MUESTRAS + 1)
        ys = np.interp(xs, nodos_x, _objetivo(nodos_x))
        puntos = [ejes.c2p(x, y) for x, y in zip(xs, ys)]

        por_banda = MUESTRAS // N_BANDAS
        bandas = VGroup()
        for j in range(N_BANDAS):
            banda = VMobject(color=colores[j * 2], stroke_width=4.5)
            banda.set_points_as_corners(
                puntos[j * por_banda:(j + 1) * por_banda + 1]
            )
            bandas.add(banda)
        return bandas

    def _contador(n):
        return texto(f"{n} neuronas", 24, color=colores[min(n, N_MAX) - 1])

    contador = _contador(len(PASOS[0])).move_to([X_RED, Y_CONTADOR, 0])

    # Solo el nombre del teorema: la explicación ya la ha dado la animación, y
    # tres líneas de texto se metían debajo del logo de la esquina.
    remate = VGroup(
        separador(largo=1.15, grosor=2),
        texto("Teorema de aproximación universal", 20, color=PRIMARIO),
    ).arrange(DOWN, buff=0.24)
    remate.move_to([CENTRO_GRAFICA[0], -2.45, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(FadeIn(entrada), FadeIn(salida), run_time=0.6)

    visibles = list(PASOS[0])
    scene.play(
        LaggedStart(*[FadeIn(neuronas[j], scale=0.5) for j in visibles],
                    lag_ratio=0.12),
        LaggedStart(*[Create(cables[j]) for j in visibles], lag_ratio=0.12),
        FadeIn(contador),
        run_time=1.2,
    )
    scene.play(
        Create(ejes), FadeIn(marcas), FadeIn(rot_x), FadeIn(rot_y),
        run_time=0.8,
    )
    scene.play(Create(objetivo), FadeIn(datos, lag_ratio=0.05), run_time=1.1)

    ajuste = _ajuste(len(visibles))
    scene.play(Create(ajuste), run_time=0.8)
    scene.next_slide()

    # Y ahora lo único que cambia: más neuronas en la misma fila.
    for paso in PASOS[1:]:
        nuevas = [j for j in paso if j not in visibles]
        visibles = list(paso)
        scene.play(
            LaggedStart(*[FadeIn(neuronas[j], scale=0.4) for j in nuevas],
                        lag_ratio=0.05),
            LaggedStart(*[Create(cables[j]) for j in nuevas], lag_ratio=0.05),
            Transform(ajuste, _ajuste(len(visibles))),
            Transform(contador,
                      _contador(len(visibles)).move_to([X_RED, Y_CONTADOR, 0])),
            run_time=1.3,
        )

    # Sin remate luminoso al final: ``Indicate`` sobre el ajuste lo dejaría
    # blanco justo en el fotograma que hay que mirar, que es el de la curva
    # pegada a los datos.
    scene.play(FadeIn(remate, shift=UP * 0.12), run_time=0.9)
    scene.wait(0.5)

    scene.next_slide()
