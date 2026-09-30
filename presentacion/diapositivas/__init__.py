from manim import UP, FadeIn, FadeOut

from componentes import logo_esquina, red_decorativa

from . import (
    activaciones_validas,
    ajuste_curva,
    backprop_ejemplo,
    backprop_neurona,
    backpropagation,
    bajar_el_valle,
    cierre,
    como_aprendemos,
    contenido,
    convexidad,
    curvas_perdida,
    decidir,
    diferenciable,
    entropia_cruzada,
    funcion_error,
    falta_algo,
    frameworks,
    funcion_activacion,
    idea_vieja,
    la_recta,
    material_extra,
    neurona_biologica,
    perdida_clasificacion,
    perdida_regresion,
    perceptron,
    porque_funciona,
    porque_importan,
    potencial_accion,
    portada,
    pregunta_error,
    pronto_iniciamos,
    red_neuronal,
    siguientes_pasos,
    softmax,
    tabla_perdidas,
)


class SlideBase:
    def indicador(self):
        if getattr(self, "_indicador", None) is None:
            self._indicador = logo_esquina()
        return self._indicador

    def next_slide(self, *args, indicador=True, **kwargs):
        if not indicador:
            super().next_slide(*args, **kwargs)
            return
        logo = self.indicador()
        self.play(FadeIn(logo, shift=UP * 0.1), run_time=0.3)
        super().next_slide(*args, **kwargs)
        self.remove(logo)

    def iniciar_slide(self):
        self._slide_actual = getattr(self, "_slide_actual", 0) + 1
        marco = getattr(self, "marco", None)
        fondo_viejo = getattr(self, "_fondo", None)
        resto = [m for m in self.mobjects if m is not marco and m is not fondo_viejo]
        for m in resto:
            m.clear_updaters()

        self._fondo = red_decorativa(self._slide_actual - 1)
        salidas = [FadeOut(m) for m in resto]
        if fondo_viejo is not None:
            salidas.append(FadeOut(fondo_viejo))
        self.play(*salidas, FadeIn(self._fondo))
        if marco is not None:
            self.add(marco)


def _slide(construir):
    def metodo(self):
        self.iniciar_slide()
        construir(self)

    return metodo


class SlidesInicio:
    slide_pronto_iniciamos = _slide(pronto_iniciamos.construir)
    slide_portada = _slide(portada.construir)
    slide_porque_importan = _slide(porque_importan.construir)


class SlidesCuerpo:
    slide_como_aprendemos = _slide(como_aprendemos.construir)
    slide_idea_vieja = _slide(idea_vieja.construir)
    slide_neurona_biologica = _slide(neurona_biologica.construir)
    slide_perceptron = _slide(perceptron.construir)
    slide_red_neuronal = _slide(red_neuronal.construir)
    slide_la_recta = _slide(la_recta.construir)
    slide_falta_algo = _slide(falta_algo.construir)
    slide_potencial_accion = _slide(potencial_accion.construir)
    slide_funcion_activacion = _slide(funcion_activacion.construir)
    slide_ajuste_curva = _slide(ajuste_curva.construir)
    slide_porque_funciona = _slide(porque_funciona.construir)
    slide_activaciones_validas = _slide(activaciones_validas.construir)
    slide_decidir = _slide(decidir.construir)
    slide_softmax = _slide(softmax.construir)
    slide_funcion_error = _slide(funcion_error.construir)
    slide_pregunta_error = _slide(pregunta_error.construir)
    slide_convexidad = _slide(convexidad.construir)
    slide_diferenciable = _slide(diferenciable.construir)
    slide_perdida_regresion = _slide(perdida_regresion.construir)
    slide_perdida_clasificacion = _slide(perdida_clasificacion.construir)
    slide_entropia_cruzada = _slide(entropia_cruzada.construir)
    slide_tabla_perdidas = _slide(tabla_perdidas.construir)
    slide_bajar_el_valle = _slide(bajar_el_valle.construir)
    slide_backpropagation = _slide(backpropagation.construir)
    slide_backprop_ejemplo = _slide(backprop_ejemplo.construir)
    slide_backprop_neurona = _slide(backprop_neurona.construir)
    slide_curvas_perdida = _slide(curvas_perdida.construir)
    slide_contenido = _slide(contenido.construir)


class SlidesFinal:
    slide_siguientes_pasos = _slide(siguientes_pasos.construir)
    slide_frameworks = _slide(frameworks.construir)
    slide_material_extra = _slide(material_extra.construir)
    slide_cierre = _slide(cierre.construir)
