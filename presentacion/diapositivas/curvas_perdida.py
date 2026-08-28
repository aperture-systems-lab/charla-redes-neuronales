"""Diapositiva 26 — ¿Está aprendiendo de verdad?

La diapositiva empieza antes de las curvas, en los datos, porque las curvas no
se entienden sin el reparto:

1. una tabla de ejemplos, y el reparto: la mayoría a **entrenamiento**, unos
   pocos apartados para **test**, que el modelo no verá,
2. cada fila de la tabla se convierte en su punto, y al lado los ejes de la
   pérdida, todavía vacíos,
3. el entrenamiento corre por épocas y se ven **las dos cosas a la vez**: a la
   izquierda la función moldeándose sobre los datos y a la derecha las dos
   pérdidas dibujándose. Hasta el codo las dos bajan,
4. pasado el codo, la de entrenamiento sigue bajando y la de test se da la
   vuelta, mientras la función se retuerce para pasar por los puntos verdes,
5. y ahí ya están las dos palabras: **underfitting** al principio, cuando la
   función aún no dice nada, y **overfitting** al final, cuando se sabe los
   datos de memoria.

Un solo mando (``epoca``) mueve la función, las dos curvas y el contador, así
que lo de la izquierda y lo de la derecha no pueden contar cosas distintas: es
el mismo número el que dibuja las tres.

Colores por papel, y los mismos que la diapositiva siguiente: entrenamiento en
verde, test en morado, la función del modelo en cian. Las dos palabras heredan
color de lo que las delata —ámbar el underfitting, morado el overfitting, que
es la curva de test dándose la vuelta—, así que la 27 puede seguir con ellos.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Integer,
    LaggedStart,
    Line,
    ReplacementTransform,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, MORADO, PRIMARIO, SECUNDARIO, VERDE

# --- Los datos -------------------------------------------------------------
# Una nube de verdad, no cuatro puntos: con pocos ejemplos el sobreajuste no
# se distingue de una curva cualquiera que pasa cerca. Las ``x`` van al azar y
# no repartidas: unas se juntan y otras se separan, que es como vienen los
# datos, y así la curva del final se retuerce de forma desigual.
N_DATOS = 24
SEMILLA = 7
# Los apartados para test, salpicados por todo el rango. Los dos primeros caen
# dentro de las filas que se ven en la tabla, así que el reparto se ve ahí.
TEST_IDX = (2, 6, 11, 15, 19, 22)

_rng = np.random.default_rng(SEMILLA)
XS = np.sort(_rng.uniform(-2.6, 2.6, N_DATOS))
RUIDO = _rng.normal(0.0, 0.21, N_DATOS)
ES_TEST = np.array([i in TEST_IDX for i in range(N_DATOS)])

# --- La tabla --------------------------------------------------------------
# Solo asoman unas cuantas filas y debajo unos puntos suspensivos: la tabla es
# una muestra de la nube, no la nube entera.
FILAS_VISIBLES = 8
ANCHO_COL = 1.05
PASO_FILA = 0.42
Y_CABECERA = 1.55
X_TRAIN, X_TEST = -3.6, 3.2      # a dónde se van los dos montones

# --- Los dos paneles -------------------------------------------------------
CENTRO_AJUSTE = [-3.5, -0.45, 0]
CENTRO_PERDIDA = [3.4, -0.45, 0]
ANCHO_PANEL, ALTO_PANEL = 5.2, 3.4

# --- El entrenamiento ------------------------------------------------------
EPOCAS = 12.0
CODO = 6.0                        # donde la de test se da la vuelta
ANCHURA_MEMORIA = 0.13            # cuánto se estrecha cada joroba del modelo


def _verdad(x):
    """La forma que de verdad tienen los datos, y que nadie le enseña."""
    return 0.26 * x**2 - 0.15 * x + 0.70


def _ys():
    return _verdad(XS) + RUIDO


def _memorion(x, xs_train, residuos):
    """La curva del modelo que se ha aprendido los datos de memoria.

    Es la forma buena más una joroba estrecha en cada punto de entrenamiento,
    de la altura exacta de su ruido. Se dibuja así y no con el polinomio que
    pasa por todos: con dieciocho puntos ese polinomio es de grado diecisiete
    y se dispara a decenas en cuanto se sale un pelo del tramo con datos.
    """
    jorobas = residuos * np.exp(-((x - xs_train) / ANCHURA_MEMORIA) ** 2)
    return _verdad(x) + float(jorobas.sum())


def _perdida_train(t):
    return 0.12 + 1.90 * np.exp(-0.42 * t)


def _perdida_test(t):
    return 0.42 + 1.75 * np.exp(-0.50 * t) + 0.05 * max(t - CODO, 0) ** 1.8


def _tabla():
    """Cabecera, raya y las primeras filas, en rejilla de posiciones fijas.

    Colocada a mano y no con ``arrange``: las filas se van a mover luego cada
    una por su lado, y ``arrange`` alinea por caja, así que con números de
    distinto signo las columnas bailaban.
    """
    ys = _ys()
    cabecera = VGroup(
        texto("x", 19, color=SECUNDARIO).move_to([0, Y_CABECERA, 0]),
        texto("y", 19, color=SECUNDARIO).move_to([ANCHO_COL, Y_CABECERA, 0]),
    )
    raya = Line(
        [-0.45, Y_CABECERA - 0.26, 0], [ANCHO_COL + 0.45, Y_CABECERA - 0.26, 0],
        color=SECUNDARIO, stroke_width=1.5,
    ).set_stroke(opacity=0.6)
    filas = VGroup(*[
        VGroup(
            # El signo va siempre: así todas las celdas miden lo mismo y las
            # columnas siguen cuadradas cuando las filas se separen.
            texto(f"{XS[i]:+.1f}", 19, color=CLARO).move_to(
                [0, Y_CABECERA - 0.55 - i * PASO_FILA, 0]),
            texto(f"{ys[i]:+.1f}", 19, color=CLARO).move_to(
                [ANCHO_COL, Y_CABECERA - 0.55 - i * PASO_FILA, 0]),
        )
        for i in range(FILAS_VISIBLES)
    ])
    return VGroup(cabecera, raya), filas


def _puntos_suspensivos(x, y):
    """La marca de que la tabla sigue: tres puntos en vertical."""
    return VGroup(*[
        Dot([x, y - k * 0.16, 0], radius=0.035, color=SECUNDARIO)
        for k in range(3)
    ]).set_opacity(0.8)


def _rotulo_monton(nombre, color, x, cuantos):
    return VGroup(
        texto(nombre, 21, color=color),
        texto(f"{cuantos} ejemplos", 16, color=SECUNDARIO),
    ).arrange(DOWN, buff=0.12).move_to([x, Y_CABECERA + 0.55, 0])


def _ejes_ajuste():
    return Axes(
        x_range=[-3, 3, 1], y_range=[0, 3.6, 1],
        x_length=ANCHO_PANEL, y_length=ALTO_PANEL,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.2,
            "include_ticks": False, "tip_width": 0.14, "tip_height": 0.14,
        },
    ).move_to(CENTRO_AJUSTE)


def _ejes_perdida():
    return Axes(
        x_range=[0, EPOCAS, 1], y_range=[0, 2.6, 1],
        x_length=ANCHO_PANEL, y_length=ALTO_PANEL,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.2,
            "include_ticks": False, "tip_width": 0.14, "tip_height": 0.14,
        },
    ).move_to(CENTRO_PERDIDA)


def _leyenda(x_centro, y):
    """Qué es cada color, con el punto del mismo tamaño que los del dibujo."""
    entradas = (("entrenamiento", VERDE), ("test", MORADO))
    grupo = VGroup(*[
        VGroup(
            Dot(radius=0.075, color=color),
            texto(nombre, 17, color=SECUNDARIO),
        ).arrange(RIGHT, buff=0.16)
        for nombre, color in entradas
    ]).arrange(RIGHT, buff=0.7)
    return grupo.move_to([x_centro, y, 0])


def construir(scene):
    encabezado = hacer_titulo("¿Está aprendiendo de verdad?")
    ys = _ys()

    # --- Acto 1: la tabla, y el reparto ------------------------------------
    marco_tabla, filas = _tabla()
    n_test = int(ES_TEST.sum())
    rot_train = _rotulo_monton("entrenamiento", VERDE, X_TRAIN,
                               N_DATOS - n_test)
    rot_test = _rotulo_monton("test", MORADO, X_TEST, n_test)

    # Cada fila visible cae en su montón, y cada montón se apila desde arriba.
    orden = {}
    vistos = [0, 0]
    for i in range(FILAS_VISIBLES):
        monton = 1 if ES_TEST[i] else 0
        orden[i] = (monton, vistos[monton])
        vistos[monton] += 1

    def _destino(i):
        """Dónde acaba la fila ``i`` cuando la tabla se parte en dos."""
        monton, sitio = orden[i]
        x = X_TEST if monton else X_TRAIN
        return [x, Y_CABECERA - 0.2 - sitio * PASO_FILA, 0]

    seguidos = VGroup(*[
        _puntos_suspensivos(
            (X_TEST if monton else X_TRAIN) + ANCHO_COL / 2,
            Y_CABECERA - 0.45 - vistos[monton] * PASO_FILA,
        )
        for monton in (0, 1)
    ])

    # --- Acto 2: los datos, ya como puntos ---------------------------------
    ejes_ajuste = _ejes_ajuste()
    puntos = VGroup(*[
        Dot(ejes_ajuste.c2p(x, y), radius=0.062,
            color=MORADO if ES_TEST[i] else VERDE)
        for i, (x, y) in enumerate(zip(XS, ys))
    ])
    leyenda = _leyenda(CENTRO_AJUSTE[0], -2.75)

    ejes_perdida = _ejes_perdida()
    rot_perdida = texto("pérdida", 17, color=SECUNDARIO)
    rot_perdida.next_to(ejes_perdida.c2p(0, 2.6), UP, buff=0.12)
    # Centrado bajo el eje y no colgado de su punta: ahí a la derecha ya no
    # queda ancho y se salía del marco.
    rot_epocas = texto("épocas", 17, color=SECUNDARIO)
    rot_epocas.next_to(ejes_perdida.x_axis, DOWN, buff=0.22)

    # --- Actos 3 y 4: el entrenamiento, con un solo mando ------------------
    xs_train = XS[~ES_TEST]
    residuos = RUIDO[~ES_TEST]
    plana = float(np.mean(ys[~ES_TEST]))

    def _modelo(x, avance):
        """Lo que dice el modelo llevando ``avance`` de entrenamiento (0 a 1).

        Primera mitad: de una recta plana —no ha aprendido nada— a la forma
        buena. Segunda mitad: de la forma buena a la curva que se sabe de
        memoria cada punto de entrenamiento, que es el sobreajuste dibujado.
        """
        verdad = _verdad(x)
        if avance <= 0.5:
            return plana + (verdad - plana) * (avance / 0.5)
        memoria = _memorion(x, xs_train, residuos)
        return verdad + (memoria - verdad) * ((avance - 0.5) / 0.5)

    epoca = ValueTracker(0.0)

    # Muestreo fino: las jorobas de la memoria son estrechas y con el paso por
    # defecto salían con esquinas en vez de curvas.
    curva_modelo = always_redraw(lambda: ejes_ajuste.plot(
        lambda x: float(np.clip(_modelo(x, epoca.get_value() / EPOCAS),
                                0.05, 3.55)),
        x_range=[XS[0] - 0.12, XS[-1] + 0.12, 0.015], color=PRIMARIO,
    ).set_stroke(width=4))

    def _trazo(funcion, color):
        """La curva dibujada solo hasta la época actual."""
        return always_redraw(lambda: ejes_perdida.plot(
            funcion, x_range=[0, max(epoca.get_value(), 0.04)], color=color,
        ).set_stroke(width=4))

    trazo_train = _trazo(_perdida_train, VERDE)
    trazo_test = _trazo(_perdida_test, MORADO)

    etiqueta_epoca = texto("época", 20, color=SECUNDARIO)
    etiqueta_epoca.move_to([CENTRO_PERDIDA[0] - 0.55, 2.15, 0])
    numero = Integer(0, color=CLARO).scale(0.9)

    def _seguir(mob):
        mob.set_value(int(round(epoca.get_value())))
        mob.next_to(etiqueta_epoca, RIGHT, buff=0.22)

    numero.add_updater(_seguir)

    # --- Acto 5: las dos palabras ------------------------------------------
    corte = DashedLine(
        ejes_perdida.c2p(CODO, 0), ejes_perdida.c2p(CODO, 2.5),
        color=CLARO, stroke_width=2, dash_length=0.09,
    ).set_stroke(opacity=0.55)
    punto_codo = Dot(ejes_perdida.c2p(CODO, _perdida_test(CODO)),
                     radius=0.09, color=CLARO)
    rot_under = texto("underfitting", 19, color=AMBAR)
    rot_under.move_to(ejes_perdida.c2p(CODO / 2, 2.25))
    rot_over = texto("overfitting", 19, color=MORADO)
    rot_over.move_to(ejes_perdida.c2p((CODO + EPOCAS) / 2, 2.25))

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(FadeIn(marco_tabla), run_time=0.5)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in filas],
                    lag_ratio=0.12),
        run_time=1.4,
    )
    scene.next_slide()

    # El reparto: la mayoría a entrenar, unos pocos apartados sin mirar.
    scene.play(FadeOut(marco_tabla), run_time=0.4)
    scene.play(
        LaggedStart(*[f.animate.move_to(_destino(i))
                      for i, f in enumerate(filas)], lag_ratio=0.06),
        run_time=1.4,
    )
    scene.play(FadeIn(rot_train, shift=DOWN * 0.12),
               FadeIn(rot_test, shift=DOWN * 0.12),
               FadeIn(seguidos), run_time=0.6)
    scene.next_slide()

    # Cada fila es un punto. Las que se ven se transforman en el suyo, y el
    # resto de la nube —lo que había detrás de los puntos suspensivos— entra
    # después.
    scene.play(FadeOut(rot_train), FadeOut(rot_test), FadeOut(seguidos),
               run_time=0.4)
    scene.play(Create(ejes_ajuste), run_time=0.7)
    scene.play(
        LaggedStart(*[ReplacementTransform(f, puntos[i])
                      for i, f in enumerate(filas)], lag_ratio=0.07),
        run_time=1.5,
    )
    scene.play(
        LaggedStart(*[FadeIn(puntos[i], scale=0.5)
                      for i in range(FILAS_VISIBLES, N_DATOS)],
                    lag_ratio=0.05),
        run_time=1.2,
    )
    scene.play(FadeIn(leyenda), run_time=0.5)
    # El contador entra ya con su cero: la etiqueta sola, sin número, se leía
    # como un rótulo a medio poner.
    scene.add(numero)
    scene.play(Create(ejes_perdida), FadeIn(rot_perdida), FadeIn(rot_epocas),
               FadeIn(etiqueta_epoca), FadeIn(numero), run_time=0.9)
    scene.next_slide()

    # Entrenar: la función se moldea y las dos pérdidas bajan juntas.
    scene.add(curva_modelo, trazo_train, trazo_test)
    scene.play(epoca.animate.set_value(CODO), run_time=4.0, rate_func=linear)
    scene.next_slide()

    # Y pasado el codo, cada una tira para su lado.
    scene.play(epoca.animate.set_value(EPOCAS), run_time=4.0,
               rate_func=linear)
    scene.next_slide()

    # Las dos palabras, cada una sobre el trozo de curva que la delata.
    scene.play(Create(corte), FadeIn(punto_codo), run_time=0.6)
    scene.play(FadeIn(rot_under, shift=DOWN * 0.1), run_time=0.5)
    scene.play(FadeIn(rot_over, shift=DOWN * 0.1), run_time=0.5)
    scene.wait(0.4)

    scene.next_slide()
