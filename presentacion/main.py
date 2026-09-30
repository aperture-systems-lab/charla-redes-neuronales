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
        # self.slide_portada()
        # self.slide_porque_importan()
        # self.slide_como_aprendemos()
        # self.slide_idea_vieja()
        # self.slide_neurona_biologica()
        # self.slide_perceptron()
        # self.slide_red_neuronal()
        # self.slide_la_recta()
        # self.slide_falta_algo()
        # self.slide_potencial_accion()
        # self.slide_funcion_activacion()
        # self.slide_ajuste_curva()
        # self.slide_porque_funciona()
        # self.slide_activaciones_validas()
        # self.slide_decidir()
        # self.slide_softmax()
        # self.slide_funcion_error()
        # self.slide_pregunta_error()
        # self.slide_convexidad()
        # self.slide_diferenciable()
        # self.slide_perdida_regresion()
        # self.slide_perdida_clasificacion()
        # self.slide_entropia_cruzada()
        # self.slide_tabla_perdidas()
        # self.slide_bajar_el_valle()
        # self.slide_backpropagation()
        # self.slide_backprop_ejemplo()
        # self.slide_backprop_neurona()
        # self.slide_curvas_perdida()
        # self.slide_siguientes_pasos()
        # self.slide_frameworks()
        self.slide_material_extra()
        # self.slide_cierre()

