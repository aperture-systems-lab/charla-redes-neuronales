"""Fábricas de mobjects reutilizables (texto, tarjetas, marco, viñetas…).

Todas son funciones puras: reciben parámetros y devuelven mobjects listos
para posicionar y animar desde las diapositivas. Añade aquí las fábricas
propias de tu proyecto (iconos, diagramas) para no ensuciar las diapositivas.
"""

import os

import numpy as np
from manim import (
    DOWN,
    DR,
    LEFT,
    NORMAL,
    ORIGIN,
    RIGHT,
    UP,
    Dot,
    ImageMobject,
    Line,
    ManimColor,
    Rectangle,
    RoundedRectangle,
    Text,
    VGroup,
    config,
)
from PIL import Image, ImageDraw, ImageOps

from estilo import (
    ASSETS,
    BLANCO,
    CLARO,
    FONDO,
    FONT,
    FONT_TITULO,
    PRIMARIO,
    SECUNDARIO,
    TAM_TITULO,
)


def marco():
    """Borde decorativo del color de marca, del tamaño del frame."""
    return Rectangle(
        width=config.frame_width - 0.22,
        height=config.frame_height - 0.22,
        stroke_color=PRIMARIO,
        stroke_width=8,
        fill_opacity=0,
    )


# Presets del fondo de red: (nodos, alcance, semilla, color, opacidad, radio).
# ``alcance`` es la distancia máxima entre dos nodos para que se unan, así que
# junto al número de nodos decide si la malla sale dispersa o tupida.
PRESETS_RED = (
    (16, 3.2, 7, SECUNDARIO, 0.16, 0.028),    # dispersa (la de la portada)
    (26, 2.3, 13, PRIMARIO, 0.13, 0.024),     # tupida y fina
    (10, 4.4, 21, SECUNDARIO, 0.18, 0.038),   # pocos nodos, aristas largas
    (36, 1.8, 34, SECUNDARIO, 0.11, 0.020),   # constelación densa
    (18, 2.8, 55, PRIMARIO, 0.15, 0.032),     # media, nodos marcados
)


def red_decorativa(indice=0):
    """Malla tenue de nodos y conexiones para el fondo de una diapositiva.

    ``indice`` elige preset rotando (``indice % 5``): pásale el número de
    diapositiva y el fondo va variando solo. Es decorativo y va muy bajo de
    opacidad a propósito: nunca debe competir con el contenido.
    """
    n, alcance, semilla, color, opacidad, radio = PRESETS_RED[indice % len(PRESETS_RED)]
    rng = np.random.default_rng(semilla)
    w, h = config.frame_width / 2 - 0.4, config.frame_height / 2 - 0.4
    puntos = np.column_stack([
        rng.uniform(-w, w, n), rng.uniform(-h, h, n), np.zeros(n),
    ])
    grupo = VGroup()
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(puntos[i] - puntos[j]) < alcance:
                grupo.add(Line(
                    puntos[i], puntos[j],
                    color=color, stroke_width=1.0, stroke_opacity=opacidad,
                ))
    for p in puntos:
        grupo.add(Dot(p, radius=radio, color=color, fill_opacity=opacidad * 2.2))
    return grupo


def imagen(nombre, escala=1.0):
    """Carga ``assets/<nombre>`` como ImageMobject.

    Si ``nombre`` no trae extensión se asume ``.png``, así que
    ``imagen("logo")`` e ``imagen("foto.jpg")`` funcionan igual.
    """
    if not os.path.splitext(nombre)[1]:
        nombre = f"{nombre}.png"
    return ImageMobject(os.path.join(ASSETS, nombre)).scale(escala)


def imagen_circular(nombre, diametro=3.2, relleno=BLANCO, ocupacion=0.86):
    """``assets/<nombre>`` compuesta sobre un disco liso y recortada en círculo.

    Devuelve un único ImageMobject que ya llega con los bordes redondos, así que
    no hay que taparle las esquinas con otro mobject encima. ``ocupacion`` es la
    fracción del disco que ocupa la imagen (el resto queda de margen).
    """
    if not os.path.splitext(nombre)[1]:
        nombre = f"{nombre}.png"
    original = Image.open(os.path.join(ASSETS, nombre)).convert("RGBA")

    lado = max(original.size)
    foto = ImageOps.contain(
        original, (int(lado * ocupacion),) * 2, Image.LANCZOS
    )
    disco = Image.new("RGBA", (lado, lado), (*ManimColor(relleno).to_int_rgb(), 255))
    disco.alpha_composite(
        foto, ((lado - foto.width) // 2, (lado - foto.height) // 2)
    )

    # Máscara dibujada a 4x y reducida: el borde del círculo sale sin dientes.
    mascara = Image.new("L", (lado * 4, lado * 4), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, lado * 4 - 1, lado * 4 - 1), fill=255)
    disco.putalpha(mascara.resize((lado, lado), Image.LANCZOS))

    mob = ImageMobject(np.array(disco)).scale_to_fit_width(diametro)
    # El caché de escena de manim resume los arrays grandes recortándolos a su
    # esquina superior izquierda, que aquí siempre es blanca: sin esta marca en
    # el ``__dict__`` dos discos distintos tienen el mismo hash y al re-renderizar
    # se reutilizaría el vídeo antiguo (el cambio no se vería).
    mob.receta_circular = (nombre, diametro, relleno, ocupacion)
    return mob


def logo_esquina(ancho=0.8, buff=0.3):
    """Logo del semillero en la esquina inferior derecha.

    Lo usan la portada y el cierre como firma, y ``SlideBase.next_slide`` como
    indicador de avance antes de cada pausa. Misma fábrica a propósito: en esas
    dos diapositivas el indicador cae exactamente encima del que ya estaba, así
    que no se duplica ni se desalinea aunque se cambien aquí las medidas.
    """
    logo = imagen("aperture-eye-cyan")
    return logo.scale_to_fit_width(ancho).to_corner(DR, buff=buff)


def texto(contenido, tam, color=CLARO, weight=NORMAL, font=FONT):
    """Texto con la fuente del proyecto (``font`` permite sobreescribirla).

    Por defecto usa el color claro de marca, legible sobre el fondo oscuro.
    """
    return Text(contenido, font=font, font_size=tam, color=color, weight=weight)


def parrafo(lineas, buff=0.15, alinear=ORIGIN):
    """Varias líneas apiladas. ``lineas`` es una lista de tuplas ``(txt, tam, ...)``."""
    textos = [texto(*linea) for linea in lineas]
    return VGroup(*textos).arrange(DOWN, buff=buff, aligned_edge=alinear)


def tarjeta(lineas, ancho_extra=0.7, alto_extra=0.4, escala=1.0):
    """Tarjeta rellena de color de marca con texto blanco encima.

    ``lineas``: lista de tuplas ``(texto, font_size, weight)``.
    """
    textos = VGroup(*[
        texto(t, fs, color=FONDO, weight=w) for t, fs, w in lineas
    ]).arrange(DOWN, buff=0.1)
    fondo = RoundedRectangle(
        corner_radius=0.14,
        width=textos.width + ancho_extra,
        height=textos.height + alto_extra,
        fill_color=PRIMARIO,
        fill_opacity=1.0,
        stroke_width=0,
    )
    return VGroup(fondo, textos).scale(escala)


def titulo(contenido):
    """Título de diapositiva anclado al borde superior.

    Mismo tratamiento que la pantalla de espera (``pronto_iniciamos``): fuente
    pixel en cian directamente sobre el fondo, sin tarjeta detrás. Si el título
    es largo se encoge para no comerse el marco.
    """
    t = texto(contenido, TAM_TITULO, color=PRIMARIO, font=FONT_TITULO)
    ancho_max = config.frame_width - 1.8
    if t.width > ancho_max:
        t.scale(ancho_max / t.width)
    return t.to_edge(UP, buff=0.6)


def vinetas(textos, tam=26, buff=0.45):
    """Lista de viñetas (punto de marca + texto), alineadas a la izquierda."""
    filas = VGroup()
    for contenido in textos:
        punto = Dot(radius=0.07, color=PRIMARIO)
        filas.add(VGroup(punto, texto(contenido, tam)).arrange(RIGHT, buff=0.25))
    return filas.arrange(DOWN, buff=buff, aligned_edge=LEFT)


def aspa(color, tam=0.14, grosor=5):
    """Un ✗ dibujado con dos líneas (no depende de que la fuente lo tenga)."""
    return VGroup(
        Line(LEFT * tam + DOWN * tam, RIGHT * tam + UP * tam,
             color=color, stroke_width=grosor),
        Line(LEFT * tam + UP * tam, RIGHT * tam + DOWN * tam,
             color=color, stroke_width=grosor),
    )


def visto(color, tam=0.14, grosor=5):
    """Un ✓ dibujado, pareja de :func:`aspa`."""
    return VGroup(
        Line(np.array([-tam * 1.15, 0.0, 0]), np.array([-tam * 0.3, -tam, 0]),
             color=color, stroke_width=grosor),
        Line(np.array([-tam * 0.3, -tam, 0]), np.array([tam * 1.3, tam * 1.2, 0]),
             color=color, stroke_width=grosor),
    )


def separador(largo=4.6, grosor=3):
    """Línea horizontal fina del color de marca (para cierres, divisiones)."""
    return Line(LEFT * largo, RIGHT * largo, color=PRIMARIO, stroke_width=grosor)


def enmarcar(mob, margen=0.12):
    """Rectángulo redondeado del color de marca alrededor de un mobject."""
    return RoundedRectangle(
        width=mob.width + margen, height=mob.height + margen,
        corner_radius=0.14, stroke_color=PRIMARIO, stroke_width=5, fill_opacity=0,
    ).move_to(mob.get_center())
