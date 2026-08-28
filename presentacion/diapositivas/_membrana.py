"""Piezas compartidas por las diapositivas de biología (10 y 11).

No es una diapositiva: no expone ``construir``. Aquí vive la bicapa lipídica y
los iones, que se dibujan igual en las dos para que la transición entre ellas
sea continua.
"""

import numpy as np
from manim import (
    Dot,
    Line,
    Rectangle,
    RoundedRectangle,
    VGroup,
    VMobject,
)

from componentes import texto
from estilo import FONDO, SECUNDARIO

X_IZQ = -6.2
X_DER = 6.2
Y_MEMBRANA = 0.0
ALTO_CABEZA = 0.30      # separación de cada fila de cabezas al centro
RADIO_CABEZA = 0.115


def bicapa(y=Y_MEMBRANA, x_izq=X_IZQ, x_der=X_DER, n=None):
    """Bicapa lipídica: dos filas de fosfolípidos y su núcleo hidrófobo.

    Los extremos son parámetros porque la membrana no siempre ocupa el ancho
    entero: cuando va dentro de un panel de zoom hay que recortarla ahí. Si no
    se dice cuántas cabezas, se calculan para que queden **tocándose**: con
    hueco entre ellas la membrana parece una valla, no una superficie.

    Cada lípido lleva sus dos colas abiertas, que es lo que lo hace reconocible
    a simple vista.
    """
    if n is None:
        n = max(2, int((x_der - x_izq) / (2 * RADIO_CABEZA)) + 1)
    xs = np.linspace(x_izq, x_der, n)

    # El interior grasiento, insinuado: da cuerpo y une las dos filas.
    nucleo = Rectangle(
        width=x_der - x_izq + 2 * RADIO_CABEZA, height=2 * ALTO_CABEZA,
        stroke_width=0,
    ).set_fill(SECUNDARIO, opacity=0.07).move_to([(x_izq + x_der) / 2, y, 0])

    capa = VGroup(nucleo)
    for x in xs:
        for signo in (1, -1):
            cuello = y + signo * (ALTO_CABEZA - 0.04)
            for sesgo in (-0.045, 0.045):
                capa.add(Line(
                    [x, cuello, 0], [x + sesgo, y + signo * 0.05, 0],
                    color=SECUNDARIO, stroke_width=1.5, stroke_opacity=0.45,
                ))
            capa.add(Dot(
                [x, y + signo * ALTO_CABEZA, 0],
                radius=RADIO_CABEZA, color=SECUNDARIO, fill_opacity=0.6,
            ))
    return capa


def ion(carga, posicion, color, radio=0.17, tam=18):
    """Ion: círculo con lo que lleve dentro (un signo, o "Na" / "K")."""
    disco = Dot(posicion, radius=radio, color=color, fill_opacity=0.28)
    borde = Dot(posicion, radius=radio, color=color, fill_opacity=0)
    borde.set_stroke(color=color, width=2.5)
    etiqueta = texto(carga, tam, color=color).move_to(posicion)
    return VGroup(disco, borde, etiqueta)


ANCHO_MITAD = 0.3       # cada hoja de la compuerta
ALTO_CANAL = 2 * ALTO_CABEZA + 0.44   # asoma un poco por los dos lados


def canal(x, color, y=Y_MEMBRANA, abertura=0.0):
    """Canal iónico incrustado en la membrana.

    Las dos mitades cierran a tope —con la separación de antes quedaba un canal
    entreabierto hasta estando "cerrado"— y ``abertura`` es lo que se apartan.
    Alto justo para atravesar la bicapa y asomar a los dos lados: así se ve
    metido en ella y no posado encima.
    """
    mitades = VGroup()
    for signo in (-1, 1):
        mitad = RoundedRectangle(
            width=ANCHO_MITAD, height=ALTO_CANAL, corner_radius=0.13,
            stroke_color=color, stroke_width=3,
            fill_color=FONDO, fill_opacity=1.0,
        )
        mitad.move_to([x + signo * (ANCHO_MITAD / 2 + abertura), y, 0])
        mitades.add(mitad)
    return mitades


def voltimetro(valor, color, posicion):
    """Etiqueta de voltaje de membrana."""
    return texto(valor, 26, color=color).move_to(posicion)


def trazo_suave(puntos, color, grosor=4):
    """Curva suave que pasa por una lista de puntos."""
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly([np.array(p) for p in puntos])
    return curva


__all__ = [
    "bicapa", "ion", "canal", "voltimetro", "trazo_suave",
    "X_IZQ", "X_DER", "Y_MEMBRANA", "ALTO_CABEZA",
]
