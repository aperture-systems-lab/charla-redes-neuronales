"""Diapositiva 27 — Lo que no cupo, y por dónde seguir.

La charla llega hasta backpropagation y ahí se corta, así que esta diapositiva
hace dos cosas y en este orden:

1. **lo que faltó**, repartido en tres columnas por para qué sirve —entrenar
   mejor, generalizar, otras arquitecturas—, en fichas para que se lea como un
   índice y no como un párrafo,
2. **por dónde seguir**: los papers que fundaron cada trozo de lo contado, con
   su año, y debajo los dos libros de la bibliografía.

Los nombres van sin explicación a propósito: son palabras para buscar, y quien
se las apunte ya tiene el hilo. Las columnas heredan el color del papel que
tenían en la charla —ámbar los pesos y su ajuste, verde lo que generaliza,
cian la red misma—, así que la primera pantalla se lee sin leyenda.
"""

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    LaggedStart,
    RoundedRectangle,
    VGroup,
)

from componentes import separador, texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, PRIMARIO, SECUNDARIO, VERDE

# --- Pantalla 1: lo que faltó ----------------------------------------------
# (columna, color, conceptos). Tres y tres: más columnas no caben y más filas
# convierten la pantalla en una lista de la compra.
FALTA = (
    ("entrenar mejor", AMBAR, (
        "optimizadores como Adam",
        "learning rate y su decay",
        "batches y shuffling",
        "inicialización de pesos",
        "normalizar las entradas",
    )),
    ("generalizar", VERDE, (
        "regularización L1 y L2",
        "dropout",
        "conjunto de validación",
        "early stopping",
        "aumento de datos",
    )),
    ("otras arquitecturas", PRIMARIO, (
        "convoluciones en visión",
        "recurrentes y LSTM",
        "atención y transformers",
        "embeddings y autoencoders",
        "aprendizaje por refuerzo",
    )),
)

CALLE = 0.5              # aire entre columnas
Y_CABECERA = 1.55
Y_PRIMERA_FICHA = 0.75
PASO_FICHA = 0.82
ALTO_FICHA = 0.66
TAM_FICHA = 16
MARGEN_FICHA = 0.55      # aire a los lados del texto, dentro de la caja

# --- Pantalla 2: por dónde seguir ------------------------------------------
# (año, título, quién). El año delante porque la lista se lee como una línea
# de tiempo: de la neurona de 1958 a la atención de 2017.
PAPERS = (
    ("1958", "The perceptron", "Rosenblatt"),
    ("1986", "Learning representations by back-propagating errors",
     "Rumelhart, Hinton & Williams"),
    ("1998", "Gradient-based learning applied to document recognition",
     "LeCun et al."),
    ("2012", "ImageNet classification with deep CNNs", "Krizhevsky et al."),
    ("2014", "Dropout", "Srivastava et al."),
    ("2014", "Adam: a method for stochastic optimization", "Kingma & Ba"),
    ("2015", "Deep residual learning", "He et al."),
    ("2017", "Attention is all you need", "Vaswani et al."),
)

LIBROS = (
    ("Neural Networks from Scratch", "Kinsley & Kukieła · nnfs.io"),
    ("Deep Learning: Foundations and Concepts", "Bishop & Bishop"),
)

# El renglón usa el ancho entero: el título de 1986 es larguísimo y con la
# firma a la derecha se tocaban.
X_ANIO = -6.45
X_TITULO = -5.6
X_AUTOR = 6.5                    # alineado por la derecha
Y_PRIMER_PAPER = 1.8
PASO_PAPER = 0.5


def _ficha(contenido, color, centro, ancho):
    """Un concepto, en su caja. Relleno tenue: marca sin gritar."""
    caja = RoundedRectangle(
        width=ancho, height=ALTO_FICHA, corner_radius=0.14,
        stroke_color=color, stroke_width=2.5,
    ).set_fill(color, opacity=0.08).move_to(centro)
    dentro = texto(contenido, TAM_FICHA, color=CLARO).move_to(centro)
    return VGroup(caja, dentro)


def _ancho_columna(conceptos):
    return max(texto(c, TAM_FICHA).width for c in conceptos) + MARGEN_FICHA


def _centros_columnas():
    """Dónde va cada columna: se reparten el ancho según lo que ocupan.

    Con las tres columnas a la misma anchura había que recortar las frases
    hasta que dejaban de decir lo que dicen. Así cada una pide lo suyo y el
    bloque entero queda centrado, sea cual sea el texto que se le meta.
    """
    anchos = [_ancho_columna(cs) for _, _, cs in FALTA]
    total = sum(anchos) + CALLE * (len(anchos) - 1)
    borde, centros = -total / 2, []
    for ancho in anchos:
        centros.append(borde + ancho / 2)
        borde += ancho + CALLE
    return centros


def _columna(nombre, color, conceptos, x):
    """Una columna entera: cabecera, raya y sus fichas."""
    ancho = _ancho_columna(conceptos)
    cabecera = texto(nombre, 21, color=color).move_to([x, Y_CABECERA, 0])
    raya = separador(largo=ancho / 2, grosor=2)
    raya.set_color(color).set_stroke(opacity=0.5)
    raya.move_to([x, Y_CABECERA - 0.34, 0])
    fichas = VGroup(*[
        _ficha(c, color, [x, Y_PRIMERA_FICHA - i * PASO_FICHA, 0], ancho)
        for i, c in enumerate(conceptos)
    ])
    return VGroup(cabecera, raya), fichas


def _fila_paper(anio, titulo, autor, y):
    """Año, título y firma: el año engancha, la firma es para buscarlo."""
    return VGroup(
        texto(anio, 18, color=AMBAR).move_to([X_ANIO, y, 0], aligned_edge=LEFT),
        texto(titulo, 17, color=CLARO).move_to(
            [X_TITULO, y, 0], aligned_edge=LEFT),
        texto(autor, 14, color=SECUNDARIO).move_to(
            [X_AUTOR, y, 0], aligned_edge=RIGHT),
    )


def construir(scene):
    encabezado = hacer_titulo("Lo que no cupo")
    encabezado_seguir = hacer_titulo("Por dónde seguir")

    # --- Pantalla 1 --------------------------------------------------------
    columnas, fichas_todas = [], []
    for x, (nombre, color, conceptos) in zip(_centros_columnas(), FALTA):
        cabecera, fichas = _columna(nombre, color, conceptos, x)
        columnas.append(cabecera)
        fichas_todas.append(fichas)
    cabeceras = VGroup(*columnas)
    fichas = VGroup(*fichas_todas)

    # --- Pantalla 2 --------------------------------------------------------
    filas = VGroup(*[
        _fila_paper(anio, titulo, autor, Y_PRIMER_PAPER - i * PASO_PAPER)
        for i, (anio, titulo, autor) in enumerate(PAPERS)
    ])
    raya_libros = separador(largo=5.4, grosor=2)
    raya_libros.set_stroke(opacity=0.4).move_to([0, -2.15, 0])
    libros = VGroup(*[
        VGroup(
            texto(titulo, 19, color=PRIMARIO),
            texto(quien, 15, color=SECUNDARIO),
        ).arrange(DOWN, buff=0.08)
        for titulo, quien in LIBROS
    ]).arrange(RIGHT, buff=1.4).move_to([0, -2.85, 0])

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(
        LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in cabeceras],
                    lag_ratio=0.3),
        run_time=1.0,
    )
    # Por filas y no por columnas: así se leen los tres temas a la vez y no
    # uno detrás de otro.
    for fila in range(len(FALTA[0][2])):
        scene.play(
            LaggedStart(*[FadeIn(grupo[fila], shift=UP * 0.12)
                          for grupo in fichas], lag_ratio=0.18),
            run_time=0.7,
        )
    scene.next_slide()

    # --- Pantalla 2: los papers --------------------------------------------
    scene.play(
        FadeOut(cabeceras), FadeOut(fichas),
        FadeOut(encabezado), FadeIn(encabezado_seguir, shift=DOWN * 0.2),
        run_time=0.9,
    )
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in filas],
                    lag_ratio=0.18),
        run_time=2.2,
    )
    scene.next_slide()

    # Y los dos libros, que es por donde se empieza de verdad.
    scene.play(FadeIn(raya_libros), run_time=0.4)
    scene.play(
        LaggedStart(*[FadeIn(li, shift=UP * 0.12) for li in libros],
                    lag_ratio=0.25),
        run_time=1.0,
    )
    scene.wait(0.4)

    scene.next_slide()
