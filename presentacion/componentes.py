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
    return Rectangle(
        width=config.frame_width - 0.22,
        height=config.frame_height - 0.22,
        stroke_color=PRIMARIO,
        stroke_width=8,
        fill_opacity=0,
    )


PRESETS_RED = (
    (16, 3.2, 7, SECUNDARIO, 0.16, 0.028),
    (26, 2.3, 13, PRIMARIO, 0.13, 0.024),
    (10, 4.4, 21, SECUNDARIO, 0.18, 0.038),
    (36, 1.8, 34, SECUNDARIO, 0.11, 0.020),
    (18, 2.8, 55, PRIMARIO, 0.15, 0.032),
)


def puntos_separados(sortear, cantidad, separacion, intentos):
    puntos = []
    for _ in range(intentos):
        if len(puntos) == cantidad:
            break
        punto = sortear()
        if all(np.linalg.norm(punto - otro) > separacion for otro in puntos):
            puntos.append(punto)
    return puntos


def pares_cercanos(puntos, alcance):
    return [
        (uno, otro)
        for i, uno in enumerate(puntos)
        for otro in puntos[i + 1:]
        if np.linalg.norm(uno - otro) < alcance
    ]


def red_decorativa(indice=0):
    n, alcance, semilla, color, opacidad, radio = PRESETS_RED[indice % len(PRESETS_RED)]
    rng = np.random.default_rng(semilla)
    w, h = config.frame_width / 2 - 0.4, config.frame_height / 2 - 0.4
    puntos = np.column_stack([
        rng.uniform(-w, w, n), rng.uniform(-h, h, n), np.zeros(n),
    ])
    grupo = VGroup()
    for uno, otro in pares_cercanos(puntos, alcance):
        grupo.add(Line(
            uno, otro, color=color, stroke_width=1.0, stroke_opacity=opacidad,
        ))
    for p in puntos:
        grupo.add(Dot(p, radius=radio, color=color, fill_opacity=opacidad * 2.2))
    return grupo


def imagen(nombre, escala=1.0):
    if not os.path.splitext(nombre)[1]:
        nombre = f"{nombre}.png"
    return ImageMobject(os.path.join(ASSETS, nombre)).scale(escala)


def imagen_circular(nombre, diametro=3.2, relleno=BLANCO, ocupacion=0.86):
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

    mascara = Image.new("L", (lado * 4, lado * 4), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, lado * 4 - 1, lado * 4 - 1), fill=255)
    disco.putalpha(mascara.resize((lado, lado), Image.LANCZOS))

    mob = ImageMobject(np.array(disco)).scale_to_fit_width(diametro)
    mob.receta_circular = (nombre, diametro, relleno, ocupacion)
    return mob


def logo_esquina(ancho=0.8, buff=0.3):
    logo = imagen("aperture-eye-cyan")
    return logo.scale_to_fit_width(ancho).to_corner(DR, buff=buff)


def texto(contenido, tam, color=CLARO, weight=NORMAL, font=FONT):
    return Text(contenido, font=font, font_size=tam, color=color, weight=weight)


def parrafo(lineas, buff=0.15, alinear=ORIGIN):
    textos = [texto(*linea) for linea in lineas]
    return VGroup(*textos).arrange(DOWN, buff=buff, aligned_edge=alinear)


def tarjeta(lineas, ancho_extra=0.7, alto_extra=0.4, escala=1.0):
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
    t = texto(contenido, TAM_TITULO, color=PRIMARIO, font=FONT_TITULO)
    ancho_max = config.frame_width - 1.8
    if t.width > ancho_max:
        t.scale(ancho_max / t.width)
    return t.to_edge(UP, buff=0.6)


def vinetas(textos, tam=26, buff=0.45):
    filas = VGroup()
    for contenido in textos:
        punto = Dot(radius=0.07, color=PRIMARIO)
        filas.add(VGroup(punto, texto(contenido, tam)).arrange(RIGHT, buff=0.25))
    return filas.arrange(DOWN, buff=buff, aligned_edge=LEFT)


def aspa(color, tam=0.14, grosor=5):
    return VGroup(
        Line(LEFT * tam + DOWN * tam, RIGHT * tam + UP * tam,
             color=color, stroke_width=grosor),
        Line(LEFT * tam + UP * tam, RIGHT * tam + DOWN * tam,
             color=color, stroke_width=grosor),
    )


def visto(color, tam=0.14, grosor=5):
    return VGroup(
        Line(np.array([-tam * 1.15, 0.0, 0]), np.array([-tam * 0.3, -tam, 0]),
             color=color, stroke_width=grosor),
        Line(np.array([-tam * 0.3, -tam, 0]), np.array([tam * 1.3, tam * 1.2, 0]),
             color=color, stroke_width=grosor),
    )


def separador(largo=4.6, grosor=3):
    return Line(LEFT * largo, RIGHT * largo, color=PRIMARIO, stroke_width=grosor)


def enmarcar(mob, margen=0.12):
    return RoundedRectangle(
        width=mob.width + margen, height=mob.height + margen,
        corner_radius=0.14, stroke_color=PRIMARIO, stroke_width=5, fill_opacity=0,
    ).move_to(mob.get_center())
