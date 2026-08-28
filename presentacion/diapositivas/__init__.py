"""Diapositivas agrupadas en mixins temáticos.

Cada diapositiva vive en su propio archivo como ``construir(scene)``; aquí se
agrupan en mixins que exponen métodos ``slide_<nombre>(self)`` para la clase
principal de ``main.py``. ``SlideBase`` aporta la limpieza de pantalla entre
diapositivas y el contador de avance.

Para añadir una diapositiva:
  1) crea ``diapositivas/<nombre>.py`` (copia ``_plantilla.py``);
  2) impórtalo abajo y añade ``slide_<nombre> = _slide(<nombre>.construir)``
     al mixin que corresponda;
  3) llámalo desde ``construct`` en ``main.py``.
"""

from manim import UP, FadeIn, FadeOut

from componentes import logo_esquina, red_decorativa

from . import (
    activaciones_validas,
    ajuste_curva,
    backpropagation,
    bajar_el_valle,
    cierre,
    como_aprendemos,
    contenido,
    curvas_perdida,
    decidir,
    funcion_error,
    falta_algo,
    frameworks,
    funcion_activacion,
    idea_vieja,
    la_recta,
    neurona_biologica,
    perceptron,
    porque_funciona,
    porque_importan,
    potencial_accion,
    portada,
    pronto_iniciamos,
    siguientes_pasos,
    softmax,
)


class SlideBase:
    """Estado y utilidades compartidas por todas las diapositivas.

    Va antes de ``Slide`` en la herencia de ``presentation``, así que su
    ``next_slide`` envuelve al de manim-slides: ninguna diapositiva tiene que
    acordarse del indicador de avance.
    """

    def indicador(self):
        """Logo de la esquina, creado una sola vez y reutilizado en cada pausa."""
        if getattr(self, "_indicador", None) is None:
            self._indicador = logo_esquina()
        return self._indicador

    def next_slide(self, *args, indicador=True, **kwargs):
        """Pausa marcando con el logo del semillero que la charla sigue.

        El logo entra como última animación de la diapositiva —así queda en el
        fotograma congelado de la pausa— y se retira nada más avanzar, para que
        no se quede encima del contenido siguiente.

        ``indicador=False`` cierra el tramo sin él. Hace falta en dos casos: en
        la última pausa de la charla, donde ya no queda nada que anunciar, y al
        cerrar un tramo en bucle, donde esa animación de entrada caería dentro
        del bucle y el logo parpadearía en cada vuelta.
        """
        if not indicador:
            super().next_slide(*args, **kwargs)
            return
        logo = self.indicador()
        self.play(FadeIn(logo, shift=UP * 0.1), run_time=0.3)
        super().next_slide(*args, **kwargs)
        self.remove(logo)

    def iniciar_slide(self):
        """Limpia la pantalla (salvo el marco) y estrena el fondo de red.

        Cada diapositiva estrena un preset distinto de ``red_decorativa``, que
        rota con el número de diapositiva: el fondo va cambiando solo, sin que
        ninguna diapositiva tenga que ocuparse de él.
        """
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
            self.add(marco)  # re-añadir lo trae al frente, por encima de la red


def _slide(construir):
    """Adapta un ``construir(scene)`` a un método de diapositiva (limpia y delega)."""

    def metodo(self):
        self.iniciar_slide()
        construir(self)

    return metodo


# --- Mixins temáticos: agrupa las diapositivas por sección ------------------
class SlidesInicio:
    slide_pronto_iniciamos = _slide(pronto_iniciamos.construir)
    slide_portada = _slide(portada.construir)
    slide_porque_importan = _slide(porque_importan.construir)


class SlidesCuerpo:
    slide_como_aprendemos = _slide(como_aprendemos.construir)
    slide_idea_vieja = _slide(idea_vieja.construir)
    slide_neurona_biologica = _slide(neurona_biologica.construir)
    slide_perceptron = _slide(perceptron.construir)
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
    slide_bajar_el_valle = _slide(bajar_el_valle.construir)
    slide_backpropagation = _slide(backpropagation.construir)
    slide_curvas_perdida = _slide(curvas_perdida.construir)
    slide_contenido = _slide(contenido.construir)


class SlidesFinal:
    slide_siguientes_pasos = _slide(siguientes_pasos.construir)
    slide_frameworks = _slide(frameworks.construir)
    slide_cierre = _slide(cierre.construir)
