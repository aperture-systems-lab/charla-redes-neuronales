"""Diapositiva 20 — Aprender es bajar al valle.

De dónde sale la dirección en la que hay que mover los pesos. El hilo va del
dibujo a la fórmula, de la fórmula al paisaje y del paisaje a la regla:

1. la red entera sacando su salida, y esa salida entrando en la función de
   error junto con la respuesta buena, con cada pieza rotulada,
2. cada pieza de ese dibujo **convertida en su trozo de fórmula** —la red en
   ``f(x;w)``, la caja en la ``L`` de fuera, la respuesta buena en la ``y``—,
   con la leyenda de siempre debajo: el error acaba siendo función de ``w``,
3. y si es una función de ``w``, se puede dibujar: el paisaje, con una tangente
   que recorre toda la curva,
4. la flecha en el eje dice hacia qué lado mover ``w`` para que el error suba,
5. con el signo cambiado, hacia dónde baja: esa es la regla, y se aplica ahí
   mismo, sin llevarse la bola a ningún otro sitio, paso a paso y despacio —la
   resta primero, sobre el eje, y la bola después.

El termómetro está **desde el principio del paisaje**, no solo al final, y su
fondo y su altura son los mismos que los del eje ``L``: el nivel del líquido
cae siempre a la altura exacta del punto de la curva, y una punteada los une.
Así el paisaje no es una gráfica abstracta, sino el mismo termómetro de la
diapositiva anterior leído de otra manera — y de paso el lado derecho de la
pantalla deja de estar vacío durante media diapositiva.

La tangente se dibuja con **largo fijo en pantalla**, no en unidades de ``w``:
midiéndola en unidades de ``w`` se disparaba fuera del cuadro en cuanto la
pendiente crecía. El montaje —tangente larga cruzando la curva, punto, y la
flecha sobre el eje— viene de las animaciones de 3Blue1Brown, que es donde
mejor se ve que lo que se decide es **hacia qué lado mover w**, no otra cosa.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Axes,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    RoundedRectangle,
    Transform,
    VGroup,
    ValueTracker,
    always_redraw,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, ROJO, SECUNDARIO, VERDE

# --- El diagrama del primer acto -------------------------------------------
# Todo el primer acto es una sola fila con sus rótulos debajo, a la misma
# altura: leído de un vistazo es una cadena de montaje.
Y_FILA = -0.3
Y_PIE = -2.05
CAPAS = ((-5.4, 3), (-4.1, 4), (-2.8, 4), (-1.5, 1))
RADIO = 0.24
PASO_NODO = 0.78
X_RED = (CAPAS[0][0] + CAPAS[-1][0]) / 2
X_SALIDA = 0.5
X_CAJA = 3.0
X_ERROR = 5.4
Y_REAL = 1.75

# --- El paisaje ------------------------------------------------------------
X_MIN, X_MAX = -3.2, 3.2
L_MAX = 3.7
MARGEN = 0.45             # ni la curva ni el barrido llegan al borde del eje
CENTRO_PAISAJE = [-1.55, -0.35, 0]
ANCHO_PAISAJE, ALTO_PAISAJE = 7.4, 4.2
LARGO_TANGENTE = 2.0      # en pantalla: así nunca se sale del cuadro
LARGO_FLECHA = 0.95

X_PARADA = 1.9            # donde se para a mirar el signo de la pendiente
# La bajada arranca en ese mismo punto, sin recolocar la bola en ningún otro
# sitio: la flecha verde acaba de decir hacia dónde ir, y lo que se ve es
# exactamente eso, aplicado ahí. Tasa alta y pocos pasos a propósito: cada
# paso se enseña entero —primero la resta sobre el eje, después la bola— y con
# pasos diminutos ni se vería la resta ni se llegaría al fondo.
TASA = 0.6
PASOS = 8

# --- El termómetro, el mismo de la diapositiva anterior --------------------
# Sin alto propio: lo toma del eje ``L`` para que los dos midan igual.
X_TERMO = 4.6
ANCHO_TERMO = 0.85


def _perdida(x):
    """Valle con un poco de relieve, para que no parezca una parábola exacta."""
    return 0.28 * x**2 + 0.35 * np.sin(1.6 * x) + 0.55


def _derivada(x):
    return 0.56 * x + 0.56 * np.cos(1.6 * x)


def _red_dibujo():
    """La red entera, a lo grande: nodos en cian y conexiones en ámbar.

    El ámbar es el color de los pesos en toda la diapositiva, así que cuando
    esto se convierta en ``f(x; w)`` la ``w`` ya viene con su color puesto y no
    hay que explicar de dónde sale.
    """
    columnas = [
        [np.array([x, Y_FILA + (n - 1) / 2 * PASO_NODO - k * PASO_NODO, 0.0])
         for k in range(n)]
        for x, n in CAPAS
    ]
    nodos = VGroup(*[
        Circle(radius=RADIO, color=PRIMARIO, stroke_width=3)
        .set_fill(FONDO, opacity=1.0).move_to(c)
        for columna in columnas for c in columna
    ])
    aristas = VGroup()
    for izquierda, derecha in zip(columnas, columnas[1:]):
        for a in izquierda:
            for b in derecha:
                direccion = (b - a) / np.linalg.norm(b - a)
                aristas.add(Line(
                    a + direccion * RADIO, b - direccion * RADIO,
                    color=AMBAR, stroke_width=1.6,
                ).set_stroke(opacity=0.45))
    return VGroup(aristas, nodos), columnas[-1][0]


def _rotulo(contenido, x, color=SECUNDARIO):
    """Glosa de una pieza del diagrama, en la fila de rótulos."""
    return texto(contenido, 18, color=color).move_to([x, Y_PIE, 0])


def _leyenda(entradas, x_simbolo=-3.85, y_primera=-0.25, paso=0.62):
    """Los símbolos de la fórmula, uno por fila, con su glosa.

    La misma leyenda de la diapositiva del error, con dos cambios. Cada símbolo
    llega ya construido y coloreado, porque uno de ellos es ``f(x;w)`` y su
    ``w`` tiene que ir en ámbar como en la fórmula. Y van alineados por la
    derecha: siendo ese tan ancho, alinearlos por la izquierda dejaba las
    glosas en escalera.
    """
    grupo = VGroup()
    for fila, (simbolo, glosa) in enumerate(entradas):
        y = y_primera - fila * paso
        grupo.add(
            simbolo.scale(0.8).next_to(
                np.array([x_simbolo, y, 0]), LEFT, buff=0,
            ),
            texto(glosa, 19, color=SECUNDARIO).next_to(
                np.array([x_simbolo + 0.35, y, 0]), RIGHT, buff=0,
            ),
        )
    return grupo


def _flecha(desde, hasta, color=SECUNDARIO):
    """Las flechas del diagrama, todas iguales: el hilo, no el contenido."""
    return Arrow(
        desde, hasta, color=color, stroke_width=3.5, buff=0.16,
        tip_length=0.22,
    ).set_stroke(opacity=0.85)


def _tangente(ejes, x0):
    """La recta que roza la curva en ``x0``, cruzándola de lado a lado.

    El largo se mide **en pantalla**: la pendiente del valle pasa de casi cero
    a más de dos, y con un largo medido en unidades de ``w`` la tangente salía
    disparada por encima del marco justo en los extremos, que es donde más se
    la mira.
    """
    base = np.array(ejes.c2p(x0, _perdida(x0)))
    direccion = np.array(ejes.c2p(x0 + 1, _perdida(x0) + _derivada(x0))) - base
    direccion = direccion / np.linalg.norm(direccion)
    return Line(
        base - direccion * LARGO_TANGENTE, base + direccion * LARGO_TANGENTE,
        color=PRIMARIO, stroke_width=3.5,
    )


def _punto(ejes, x0, radio=0.11):
    return Dot(ejes.c2p(x0, _perdida(x0)), radius=radio, color=AMBAR)


def _guia(ejes, x0):
    """La punteada que baja del punto al eje, para leer qué ``w`` es."""
    return DashedLine(
        ejes.c2p(x0, _perdida(x0)), ejes.c2p(x0, 0),
        color=AMBAR, stroke_width=2, dash_length=0.09,
    ).set_stroke(opacity=0.6)


def _marca(ejes, x0):
    """Ese mismo ``w``, marcado sobre el eje: lo único que se mueve."""
    return Dot(ejes.c2p(x0, 0), radius=0.07, color=AMBAR)


def _lectura(ejes, x0):
    """La punteada que lleva la altura de la curva hasta el termómetro."""
    extremo = ejes.c2p(x0, _perdida(x0))
    return DashedLine(
        [extremo[0] + 0.22, extremo[1], 0],
        [X_TERMO - ANCHO_TERMO / 2, extremo[1], 0],
        color=ROJO, stroke_width=1.6, dash_length=0.08,
    ).set_stroke(opacity=0.35)


def _medidas_termo(ejes):
    """Pie y alto del tubo, calcados del eje ``L``."""
    pie = ejes.c2p(0, 0)[1]
    return pie, ejes.c2p(0, L_MAX)[1] - pie


def _tubo(ejes):
    pie, alto = _medidas_termo(ejes)
    tubo = Rectangle(
        width=ANCHO_TERMO, height=alto,
        stroke_color=SECUNDARIO, stroke_width=2,
    ).set_fill(FONDO, opacity=1.0)
    return tubo.move_to([X_TERMO, pie + alto / 2, 0])


def _liquido(ejes, valor):
    """El nivel: la misma altura que tiene la curva, medida en el mismo eje."""
    pie, alto = _medidas_termo(ejes)
    llenado = max(alto * valor / L_MAX, 0.04)
    barra = Rectangle(
        width=ANCHO_TERMO - 0.14, height=llenado,
        stroke_width=0, fill_color=ROJO, fill_opacity=0.8,
    )
    return barra.move_to([X_TERMO, pie + llenado / 2, 0])


def _paso_eje(ejes, desde, hasta):
    """Lo que se le resta a ``w`` en un paso, dibujado sobre el eje.

    Es la flecha verde de antes, pero ya no dice solo el lado: mide. Va en
    verde, el color de ``-\\eta\\,dL/dw`` en la regla, para que se lea que este
    salto **es** ese término.
    """
    return Arrow(
        ejes.c2p(desde, 0), ejes.c2p(hasta, 0),
        color=VERDE, stroke_width=5, buff=0, tip_length=0.2,
        max_tip_length_to_length_ratio=0.4,
    )


def _flecha_eje(ejes, x0, hacia_arriba, color):
    """La flecha sobre el eje: hacia qué lado mover ``w``.

    Va en el eje y no sobre la curva porque lo que se decide es exactamente
    eso, el lado al que se mueve el peso.
    """
    signo = 1.0 if _derivada(x0) >= 0 else -1.0
    if not hacia_arriba:
        signo = -signo
    base = np.array(ejes.c2p(x0, 0))
    return Arrow(
        base, base + RIGHT * signo * LARGO_FLECHA,
        color=color, stroke_width=5, buff=0.05, tip_length=0.24,
    )


def construir(scene):
    encabezado = hacer_titulo("Aprender es bajar al valle")

    # --- Acto 1: la red saca su salida, y el error la mide -----------------
    red, centro_salida = _red_dibujo()
    rot_red = VGroup(
        texto("la red", 18, color=SECUNDARIO),
        texto("y sus pesos", 18, color=AMBAR),
    ).arrange(RIGHT, buff=0.14).move_to([X_RED, Y_PIE, 0])

    salida = MathTex(r"\hat{y}", color=PRIMARIO).scale(1.5)
    salida.move_to([X_SALIDA, Y_FILA, 0])
    rot_salida = _rotulo("lo que predice", X_SALIDA)
    flecha_salida = _flecha(centro_salida + RIGHT * RADIO, salida.get_left())

    caja = RoundedRectangle(
        width=2.2, height=1.5, corner_radius=0.18,
        stroke_color=ROJO, stroke_width=3,
    ).set_fill(ROJO, opacity=0.1).move_to([X_CAJA, Y_FILA, 0])
    nombre_caja = texto("error", 24, color=ROJO).move_to(caja.get_center())
    flecha_caja = _flecha(salida.get_right(), caja.get_left())

    real = MathTex("y", color=CLARO).scale(1.4).move_to([X_CAJA, Y_REAL, 0])
    # En el dibujo va corto —a la derecha ya no queda ancho—; el "es fija", que
    # es el matiz que importa, lo dice la leyenda del acto siguiente.
    rot_real = texto("la observación", 17, color=SECUNDARIO)
    rot_real.next_to(real, RIGHT, buff=0.28)
    flecha_real = _flecha(real.get_bottom(), caja.get_top())

    valor_error = MathTex("L", color=ROJO).scale(1.6)
    valor_error.move_to([X_ERROR, Y_FILA, 0])
    rot_error = _rotulo("cuánto falla", X_ERROR, color=ROJO)
    flecha_error = _flecha(caja.get_right(), valor_error.get_left())

    # --- Acto 2: todo el diagrama, en una sola función ---------------------
    compuesta = MathTex(
        "L", "(", "w", ")", "=",
        "L", r"\big(", "f(x;", "w", ")", ",", "y", r"\big)",
    ).scale(1.4).move_to([0, 1.2, 0])
    for i in (0, 1, 3, 5, 6, 12):
        compuesta[i].set_color(ROJO)
    for i in (2, 8):
        compuesta[i].set_color(AMBAR)
    for i in (7, 9):
        compuesta[i].set_color(PRIMARIO)
    for i in (10, 11):
        compuesta[i].set_color(CLARO)

    # Cada pieza del dibujo se convierte en su trozo de fórmula, no todo en
    # todo: la red en ``f(x;w)``, la caja en la ``L`` de fuera, la ``y`` en la
    # ``y`` y el valor del error en el lado izquierdo.
    morfos = (
        (VGroup(red, rot_red), compuesta[7:10]),
        (VGroup(flecha_salida, salida, rot_salida), compuesta[7:10]),
        (VGroup(flecha_caja, caja, nombre_caja),
         VGroup(compuesta[5], compuesta[6], compuesta[12])),
        (VGroup(real, flecha_real, rot_real), compuesta[10:12]),
        (VGroup(flecha_error, valor_error, rot_error), compuesta[0:5]),
    )

    # La leyenda debajo, como en la diapositiva del error: la fórmula sola en
    # mitad de la pantalla se queda coja, y estos tres renglones son los mismos
    # rótulos del dibujo de arriba, ya sin dibujo.
    simbolo_f = MathTex("f(x;", "w", ")")
    simbolo_f[0].set_color(PRIMARIO)
    simbolo_f[1].set_color(AMBAR)
    simbolo_f[2].set_color(PRIMARIO)
    leyenda = _leyenda((
        (simbolo_f, "lo que predice la red"),
        (MathTex("y", color=CLARO), "la observación, es fija"),
        (MathTex("w", color=AMBAR), "los pesos, lo que vamos a optimizar"),
    ))
    clave = texto("el error es una función de los pesos", 22, color=AMBAR)
    clave.move_to([0, -2.45, 0])

    # --- Actos 3 a 5: el paisaje -------------------------------------------
    ejes = Axes(
        x_range=[X_MIN, X_MAX, 1], y_range=[0, L_MAX, 1],
        x_length=ANCHO_PAISAJE, y_length=ALTO_PAISAJE,
        axis_config={
            "color": SECUNDARIO, "stroke_width": 2.5,
            "include_ticks": False, "tip_width": 0.16, "tip_height": 0.16,
        },
    ).move_to(CENTRO_PAISAJE)
    valle = ejes.plot(_perdida, x_range=[X_MIN + 0.25, X_MAX - 0.25],
                      color=ROJO).set_stroke(width=4)
    # Los nombres van en los ejes, no colgados de la curva: la tangente barre
    # todo el cuadro y cualquier rótulo suelto acaba debajo de ella.
    rot_w = MathTex("w", color=AMBAR).scale(0.95)
    rot_w.next_to(ejes.c2p(X_MAX, 0), DOWN + RIGHT, buff=0.16)
    rot_L = MathTex("L", color=ROJO).scale(0.95)
    rot_L.next_to(ejes.c2p(0, L_MAX), UP, buff=0.14)

    tubo = _tubo(ejes)
    rotulo_termo = texto("error", 19, color=ROJO).next_to(tubo, UP, buff=0.24)

    # Un solo mando para todo el paisaje: punto, guías, marca del eje y nivel
    # del termómetro cuelgan de ``donde``, así que el barrido de la tangente y
    # cada paso de la bajada son la misma animación contada dos veces.
    arranque = X_MIN + MARGEN
    donde = ValueTracker(arranque)
    dinamicos = (_tangente, _lectura, _guia, _marca, _punto)
    tangente, lectura, guia, marca, punto = [
        always_redraw(lambda f=f: f(ejes, donde.get_value()))
        for f in dinamicos
    ]
    nivel = always_redraw(
        lambda: _liquido(ejes, _perdida(donde.get_value()))
    )

    # --- La regla, y la bajada ---------------------------------------------
    regla = MathTex(
        "w", r"\leftarrow", "w", "-", r"\eta", r"\frac{dL}{dw}",
    ).scale(0.95)
    for i in (0, 2):
        regla[i].set_color(AMBAR)
    regla[3].set_color(VERDE)
    regla[4].set_color(MORADO)
    regla[5].set_color(VERDE)
    glosa = VGroup(
        MathTex(r"\eta", color=MORADO).scale(0.75),
        texto("el tamaño del paso", 18, color=SECUNDARIO),
    ).arrange(RIGHT, buff=0.22)
    fila_regla = VGroup(regla, glosa).arrange(RIGHT, buff=0.9)
    fila_regla.move_to([CENTRO_PAISAJE[0] + 0.6, -3.2, 0])

    recorrido = [X_PARADA]
    for _ in range(PASOS):
        recorrido.append(recorrido[-1] - TASA * _derivada(recorrido[-1]))

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(FadeIn(red), FadeIn(rot_red), run_time=1.0)
    scene.play(Create(flecha_salida), FadeIn(salida, shift=RIGHT * 0.2),
               FadeIn(rot_salida), run_time=0.8)
    scene.play(Create(flecha_caja), Create(caja), FadeIn(nombre_caja),
               run_time=0.8)
    scene.play(FadeIn(real, shift=DOWN * 0.15), FadeIn(rot_real),
               Create(flecha_real), run_time=0.8)
    scene.play(Create(flecha_error), FadeIn(valor_error, shift=RIGHT * 0.2),
               FadeIn(rot_error), run_time=0.8)
    scene.next_slide()

    # 2. Cada pieza, su fórmula. Y las cinco juntas, una sola función.
    scene.play(*[Transform(a, b.copy()) for a, b in morfos], run_time=1.5)
    scene.remove(*[a for a, _ in morfos])
    scene.add(compuesta)
    scene.play(
        LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15) for f in leyenda],
                    lag_ratio=0.18),
        run_time=1.2,
    )
    scene.play(
        FadeIn(clave, shift=UP * 0.1),
        LaggedStart(*[Indicate(compuesta[i], color=CLARO, scale_factor=1.4)
                      for i in (2, 8)], lag_ratio=0.3),
        run_time=1.2,
    )
    scene.next_slide()

    # 3. Y si es una función de w, se dibuja. El termómetro entra con ella:
    # la altura de la curva y el nivel del líquido son la misma medida.
    scene.play(FadeOut(compuesta), FadeOut(leyenda), FadeOut(clave),
               run_time=0.7)
    scene.play(Create(ejes), FadeIn(rot_w), FadeIn(rot_L), run_time=0.8)
    scene.play(Create(valle), Create(tubo), FadeIn(rotulo_termo), run_time=1.3)

    # Los dinámicos entran como copias quietas y se relevan al vuelo: un
    # ``always_redraw`` no se puede desvanecer, se repinta entero cada frame.
    quietos = VGroup(*[f(ejes, arranque) for f in dinamicos],
                     _liquido(ejes, _perdida(arranque)))
    scene.play(FadeIn(quietos), run_time=0.9)
    scene.remove(quietos)
    scene.add(nivel, lectura, guia, marca, tangente, punto)

    # La pendiente, recorriendo la curva entera.
    scene.play(donde.animate.set_value(X_MAX - MARGEN), run_time=4.0,
               rate_func=linear)
    scene.next_slide()

    # 4. En un punto cualquiera: hacia qué lado sube el error.
    scene.play(donde.animate.set_value(X_PARADA), run_time=0.9)
    flecha_sube = _flecha_eje(ejes, X_PARADA, True, ROJO)
    etiqueta_sube = MathTex(r"\frac{dL}{dw}", color=ROJO).scale(0.85)
    etiqueta_sube.next_to(flecha_sube, DOWN, buff=0.22)
    scene.play(Create(flecha_sube), FadeIn(etiqueta_sube), run_time=0.9)
    scene.next_slide()

    # 5. Con el signo cambiado, hacia el otro lado: hacia donde baja.
    flecha_baja = _flecha_eje(ejes, X_PARADA, False, VERDE)
    etiqueta_baja = MathTex(r"-\frac{dL}{dw}", color=VERDE).scale(0.85)
    etiqueta_baja.next_to(flecha_baja, DOWN, buff=0.22)
    scene.play(
        Transform(flecha_sube, flecha_baja),
        Transform(etiqueta_sube, etiqueta_baja),
        run_time=1.1,
    )
    scene.next_slide()

    # Eso es la regla entera: se escribe abajo, y la flecha verde se queda
    # donde está. La tangente sí sobra: a partir de aquí se mira el eje.
    tangente.clear_updaters()
    scene.play(
        FadeOut(etiqueta_sube), FadeOut(tangente),
        FadeIn(fila_regla, shift=UP * 0.12),
        run_time=0.9,
    )

    # Y aplicarla, paso a paso y sin prisa. Cada paso son dos tiempos: primero
    # la resta, medida sobre el eje —cuánto se le quita a ``w`` esta vez—, y
    # después la bola, que no hace más que obedecer. El primer salto no se
    # dibuja de cero: es la flecha de antes, encogida hasta lo que de verdad
    # mide un paso.
    saltos = [_paso_eje(ejes, a, b) for a, b in zip(recorrido, recorrido[1:])]
    scene.play(Transform(flecha_sube, saltos[0]), run_time=0.8)

    salto = flecha_sube
    for i, x_siguiente in enumerate(recorrido[1:]):
        rastro = _punto(ejes, recorrido[i], radio=0.07)
        scene.add(rastro.set_opacity(0.35))
        scene.play(donde.animate.set_value(x_siguiente), FadeOut(salto),
                   run_time=0.55)
        if i + 1 < len(saltos):
            salto = saltos[i + 1]
            scene.play(Create(salto), run_time=0.4)

    scene.play(Indicate(regla, color=CLARO, scale_factor=1.1), run_time=0.9)
    scene.wait(0.3)

    scene.next_slide()
