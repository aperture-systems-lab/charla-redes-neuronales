"""Cómo funcionan las redes neuronales — orquestador delgado de la charla.

El estilo vive en ``estilo.py``, las fábricas de mobjects en ``componentes.py``,
los helpers de animación en ``animaciones.py`` y cada diapositiva en su archivo
dentro de ``diapositivas/``. Las diapositivas se agrupan en mixins temáticos
(``Slides*``) que aportan los métodos ``slide_*`` invocados desde ``construct``.

Desde la raíz del repositorio:

    Renderizar:   uv run python -m manim_slides render main.py presentation
    Presentar:    uv run python -m manim_slides present presentation
    Exportar:     uv run python -m manim_slides convert presentation salida.pptx
"""

from manim import ManimColor
from manim_slides import Slide

from componentes import marco
from diapositivas import (
    SlideBase,
    SlidesCuerpo,
    SlidesFinal,
    SlidesInicio,
)
from estilo import FONDO


class presentation(
    SlidesInicio,
    SlidesCuerpo,
    SlidesFinal,
    SlideBase,
    Slide,
):
    def construct(self):
        self._slide_actual = 0
        self.camera.background_color = ManimColor(FONDO)
        self.marco = marco()
        self.add(self.marco)

        self.slide_pronto_iniciamos()
        self.slide_portada()
        self.slide_porque_importan()
        self.slide_como_aprendemos()
        self.slide_idea_vieja()
        self.slide_neurona_biologica()
        self.slide_perceptron()
        self.slide_la_recta()
        self.slide_falta_algo()
        self.slide_potencial_accion()
        self.slide_funcion_activacion()
        self.slide_ajuste_curva()
        self.slide_porque_funciona()
        self.slide_activaciones_validas()
        self.slide_decidir()
        self.slide_softmax()
        self.slide_funcion_error()
        self.slide_bajar_el_valle()
        self.slide_backpropagation()
        self.slide_curvas_perdida()
        self.slide_siguientes_pasos()
        self.slide_frameworks()
        self.slide_cierre()

