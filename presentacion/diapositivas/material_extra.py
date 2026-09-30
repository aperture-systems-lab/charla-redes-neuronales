import os

import numpy as np
from manim import (
    DOWN,
    UP,
    RIGHT,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    LaggedStart,
    RoundedRectangle,
    VGroup,
)
from PIL import Image, ImageDraw, ImageOps

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import (
    AMBAR,
    ASSETS,
    CLARO,
    FONT_TITULO,
    MORADO,
    PRIMARIO,
    SECUNDARIO,
    VERDE,
)

NOTEBOOKS = (
    ("01", "Primera neurona", "regression", "mensajes.png", PRIMARIO),
    ("02", "Titanic", "classification", "titanic.png", VERDE),
    ("03", "Hot dog or not", "vision", "hotdog.jpg", AMBAR),
    ("04", "Tic-tac-toe", "reinforcement", "alphago.png", MORADO),
)

ANCHO_FOTO, ALTO_FOTO = 2.95, 2.2
RADIO_FOTO = 0.16
PIXELES_ALTO = 600
OCUPACION_DIBUJO = 0.84
BUFF_TARJETAS = 0.36
Y_TARJETAS = -0.65

TAM_PASANDO = 34
TAM_PLAYGROUND = 50
ANCHO_MAX_PLAYGROUND = 10.4


# Fotos recortadas a la misma proporción; los dibujos con transparencia, sobre blanco.
def _recorte(nombre):
    original = Image.open(os.path.join(ASSETS, nombre)).convert("RGBA")
    alto = PIXELES_ALTO
    ancho = round(alto * ANCHO_FOTO / ALTO_FOTO)

    if original.getchannel("A").getextrema()[0] < 255:
        dibujo = ImageOps.contain(
            original, (int(ancho * OCUPACION_DIBUJO), int(alto * OCUPACION_DIBUJO)),
            Image.LANCZOS,
        )
        foto = Image.new("RGBA", (ancho, alto), (255, 255, 255, 255))
        foto.alpha_composite(
            dibujo, ((ancho - dibujo.width) // 2, (alto - dibujo.height) // 2)
        )
    else:
        foto = ImageOps.fit(original, (ancho, alto), Image.LANCZOS)

    radio = round(RADIO_FOTO / ALTO_FOTO * alto)
    mascara = Image.new("L", (ancho * 4, alto * 4), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        (0, 0, ancho * 4 - 1, alto * 4 - 1), radius=radio * 4, fill=255,
    )
    foto.putalpha(mascara.resize((ancho, alto), Image.LANCZOS))
    return foto


def _tarjeta(numero, nombre, tema, archivo, color):
    foto = ImageMobject(np.array(_recorte(archivo))).scale_to_fit_width(ANCHO_FOTO)
    borde = RoundedRectangle(
        width=ANCHO_FOTO, height=ALTO_FOTO, corner_radius=RADIO_FOTO,
        stroke_color=color, stroke_width=3,
    ).move_to(foto.get_center())

    # Cada renglón a una altura fija bajo la foto: así una "g" en el nombre
    # no descuadra el tema frente a las otras tarjetas.
    x, base = foto.get_center()[0], foto.get_bottom()[1]
    renglones = (
        (texto(numero, 16, color=color, font=FONT_TITULO), 0.32),
        (texto(nombre, 20, color=CLARO), 0.70),
        (texto(tema, 15, color=SECUNDARIO), 1.10),
    )
    pie = VGroup(*[
        mob.move_to([x, 0, 0]).align_to([0, base - bajada, 0], UP)
        for mob, bajada in renglones
    ])
    return Group(foto, borde, pie)


def construir(scene):
    encabezado = hacer_titulo("Material extra")
    subtitulo = texto("parte práctica  ·  4 notebooks, uno por tema", 18,
                      color=SECUNDARIO).next_to(encabezado, DOWN, buff=0.35)

    tarjetas = Group(*[_tarjeta(*nb) for nb in NOTEBOOKS])
    tarjetas.arrange(RIGHT, buff=BUFF_TARJETAS, aligned_edge=UP).set_y(Y_TARJETAS)

    pasando = VGroup(
        texto("PASANDO AL", TAM_PASANDO, color=CLARO, font=FONT_TITULO),
        texto("PLAYGROUND", TAM_PLAYGROUND, color=PRIMARIO, font=FONT_TITULO),
    ).arrange(DOWN, buff=0.55)
    if pasando.width > ANCHO_MAX_PLAYGROUND:
        pasando.scale(ANCHO_MAX_PLAYGROUND / pasando.width)
    comando = texto("$ ./playground.sh", 20, color=SECUNDARIO)
    comando.next_to(pasando, DOWN, buff=0.75)

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(FadeIn(subtitulo, shift=DOWN * 0.1), run_time=0.4)
    scene.play(
        LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in tarjetas], lag_ratio=0.3),
        run_time=1.6,
    )
    scene.next_slide()

    scene.play(FadeOut(encabezado), FadeOut(subtitulo), FadeOut(tarjetas),
               run_time=0.7)
    scene.play(FadeIn(pasando[0], shift=UP * 0.18), run_time=0.5)
    scene.play(FadeIn(pasando[1], shift=UP * 0.18), run_time=0.6)
    scene.play(FadeIn(comando, shift=UP * 0.1), run_time=0.4)
    scene.wait(0.4)

    scene.next_slide()
