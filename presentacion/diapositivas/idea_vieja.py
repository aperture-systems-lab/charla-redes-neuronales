"""Diapositiva 3 — No es una idea nueva.

Arranca donde terminó la diapositiva anterior (hoy: ChatGPT, Claude) y rebobina
hacia atrás: la línea temporal se dibuja de derecha a izquierda hasta aterrizar
en 1957, con Rosenblatt y el perceptrón. Cierra con el puente a la neurona
biológica, que es lo que el perceptrón intentaba imitar.

El hito de 1986 se planta aquí sin explicar a propósito: lo recoge la
diapositiva de backpropagation.
"""

from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    Dot,
    FadeIn,
    Flash,
    GrowFromCenter,
    GrowFromPoint,
    Group,
    LaggedStart,
    Line,
    VGroup,
)

from componentes import enmarcar, imagen, texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONT_TITULO, PRIMARIO, SECUNDARIO

Y_LINEA = 1.35
Y_TARJETA = -1.0
Y_PUENTE = -3.05
X_EXTREMO = 5.9       # medio ancho de la línea temporal
SEPARACION = 2.5      # distancia entre hitos consecutivos
ANCHO_MAX_HITO = 2.1  # tope para que las etiquetas vecinas no se toquen
ALTO_FOTO = 1.8       # alto del retrato de Rosenblatt
ANIO_ACTUAL = 2026    # para el "hace N años"
ANIO_PERCEPTRON = 1957

# De más antiguo a más reciente: así se colocan en pantalla (izquierda→derecha).
HITOS = (
    ("1957", "El perceptrón"),
    ("1969", "Primer invierno"),
    ("1986", "Backpropagation"),
    ("2012", "AlexNet"),
    ("HOY", "ChatGPT, Claude"),
)


def _marcador(anio, descripcion, x, destacado=False):
    """Punto sobre la línea con el año encima y el hito debajo."""
    color = PRIMARIO if destacado else SECUNDARIO
    punto = Dot(radius=0.12 if destacado else 0.08, color=color)
    punto.move_to([x, Y_LINEA, 0])
    etiqueta_anio = texto(anio, 26 if destacado else 22, color=color, weight=BOLD)
    etiqueta_anio.next_to(punto, UP, buff=0.22)
    etiqueta_hito = texto(
        descripcion, 14, color=CLARO if destacado else SECUNDARIO,
    )
    if etiqueta_hito.width > ANCHO_MAX_HITO:
        etiqueta_hito.scale(ANCHO_MAX_HITO / etiqueta_hito.width)
    etiqueta_hito.next_to(punto, DOWN, buff=0.22)
    return VGroup(punto, etiqueta_anio, etiqueta_hito)


def _tarjeta_rosenblatt():
    """Retrato, el año en grande y al lado quién fue y cuánto hace de esto."""
    foto = imagen("frank.jpg").scale_to_fit_height(ALTO_FOTO)
    marco_foto = enmarcar(foto, margen=0.12).set_stroke(width=3)
    retrato = Group(foto, marco_foto)

    anio = texto(str(ANIO_PERCEPTRON), 44, color=PRIMARIO, font=FONT_TITULO)
    divisor = Line(
        UP * 0.55, DOWN * 0.55,
        color=SECUNDARIO, stroke_width=2, stroke_opacity=0.6,
    )
    detalle = VGroup(
        texto("Frank Rosenblatt", 26, color=CLARO, weight=BOLD),
        texto("propone el perceptrón", 20, color=SECUNDARIO),
        texto(f"hace {ANIO_ACTUAL - ANIO_PERCEPTRON} años", 18, color=AMBAR),
    ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)

    # Group (no VGroup): la foto es un ImageMobject, no un VMobject.
    fila = Group(retrato, anio, divisor, detalle).arrange(RIGHT, buff=0.45)
    caja = enmarcar(fila, margen=0.8)
    return Group(caja, fila).move_to([0, Y_TARJETA, 0])


def construir(scene):
    encabezado = hacer_titulo("No es una idea nueva")

    xs = [(i - (len(HITOS) - 1) / 2) * SEPARACION for i in range(len(HITOS))]
    marcadores = [
        _marcador(anio, hito, x, destacado=(anio == str(ANIO_PERCEPTRON)))
        for (anio, hito), x in zip(HITOS, xs)
    ]
    perceptron, *anteriores = marcadores  # el de 1957 va aparte, es el destino

    # Definida de derecha a izquierda: ``Create`` la dibuja rebobinando.
    linea = Line(
        [X_EXTREMO, Y_LINEA, 0], [-X_EXTREMO, Y_LINEA, 0],
        color=SECUNDARIO, stroke_width=3, stroke_opacity=0.7,
    )

    tarjeta = _tarjeta_rosenblatt()
    puente = VGroup(
        texto("Un algoritmo que aprenda", 26, color=CLARO),
        texto("como una neurona", 26, color=PRIMARIO, weight=BOLD),
    ).arrange(RIGHT, buff=0.22).move_to([0, Y_PUENTE, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)

    # Partimos de hoy: lo que acabamos de ver en la diapositiva anterior.
    scene.play(GrowFromCenter(anteriores[-1]), run_time=0.6)
    scene.next_slide()

    # Rebobinado: la línea barre hacia la izquierda destapando los hitos.
    scene.play(
        Create(linea),
        LaggedStart(
            *[FadeIn(m, shift=UP * 0.12) for m in reversed(anteriores[:-1])],
            lag_ratio=0.45,
        ),
        run_time=1.6,
    )
    scene.next_slide()

    # Destino: 1957.
    scene.play(GrowFromCenter(perceptron), run_time=0.5)
    scene.play(
        Flash(perceptron[0], color=PRIMARIO, line_length=0.25, num_lines=16,
              flash_radius=0.45),
        run_time=0.5,
    )
    scene.play(
        GrowFromPoint(tarjeta, perceptron[0].get_center()), run_time=0.9,
    )
    scene.next_slide()

    # Puente hacia la neurona biológica (diapositiva 4).
    scene.play(FadeIn(puente, shift=UP * 0.15), run_time=0.7)
    scene.wait(0.4)

    scene.next_slide()
