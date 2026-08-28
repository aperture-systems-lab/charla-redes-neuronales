"""Diapositiva 0 — pantalla de espera, antes de que empiece la charla.

Es lo que se proyecta mientras llega la gente: el gato tostada del semillero
dentro de un círculo blanco con borde de marca y, debajo, el aviso de que ya
casi empezamos. Sin más adorno: tiene que aguantar en pantalla varios minutos.
"""

from manim import (
    DOWN,
    UP,
    Circle,
    FadeIn,
    GrowFromCenter,
)

from componentes import imagen_circular, texto
from estilo import FONT_TITULO, PRIMARIO

Y_CIRCULO = 0.75       # centro del disco con el gato
DIAMETRO = 4.4
OCUPACION = 0.62       # cuánto del disco ocupa el gato (el resto, margen blanco)


def construir(scene):
    gato = imagen_circular("gato_tostada", diametro=DIAMETRO, ocupacion=OCUPACION)
    gato.move_to([0, Y_CIRCULO, 0])

    # El borde se dibuja encima del disco: tapa el recorte de la máscara.
    borde = Circle(radius=DIAMETRO / 2, color=PRIMARIO, stroke_width=7)
    borde.move_to(gato.get_center())

    mensaje = texto("PRONTO INICIAMOS", 32, color=PRIMARIO, font=FONT_TITULO)
    mensaje.next_to(borde, DOWN, buff=0.8)

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(gato, scale=0.85), GrowFromCenter(borde), run_time=0.9)
    scene.play(FadeIn(mensaje, shift=UP * 0.15), run_time=0.6)
    scene.wait(0.5)

    scene.next_slide()
