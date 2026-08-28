"""Diapositiva 23 — De la regla de la cadena a backpropagation.

Une en un solo hilo lo que antes eran tres diapositivas sueltas (la regla de la
cadena, derivar a mano y backpropagation), porque las tres son un solo
razonamiento y contadas por separado se rompía justo donde tiene gracia:

1. vuelve la compuesta de la diapositiva del valle y se **abre**: la red no es
   una función, es una cadena de funciones, con la ``w`` colgando de la
   primera,
2. la regla de la cadena sobre ese dibujo, con cada factor numerado —y los
   números van de la salida hacia atrás, que es ya la mitad de backprop,
3. el intento en una red de verdad: una sola ``w`` llega a la salida por ocho
   caminos, y la cuenta de parámetros explota. A mano no es difícil: no escala,
4. y la solución, con su propio título: pasada hacia delante con el error alto,
   zoom a una neurona para ver que cada peso **solo necesita lo que le llega de
   la derecha**, vuelta atrás capa a capa restando el gradiente, y otra pasada
   hacia delante con el error más bajo.

Los pesos se dibujan como **perillas** con aguja, del ámbar de siempre: una
perilla se gira, y girarla es literalmente lo que hace el paso de gradiente.
El termómetro del error es el mismo de las dos diapositivas anteriores, así que
"alto" y "bajo" se leen sin explicar nada.

Colores por papel: la red en azul acero, los pesos en ámbar, el error en rojo,
la ida en verde y la vuelta —la culpa que baja— en morado. Cuando una capa
termina de corregirse, sus aristas se quedan en ámbar: pesos nuevos.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    Rectangle,
    Rotate,
    RoundedRectangle,
    Transform,
    VGroup,
    Write,
    there_and_back,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, ROJO, SECUNDARIO, VERDE

# --- Acto 1: la cadena de funciones ----------------------------------------
Y_CADENA = 0.35
ANCHO_CAJA, ALTO_CAJA = 1.15, 0.95
LARGO_FLECHA = 0.62

# --- Actos 3 a 8: la red ---------------------------------------------------
CAPAS_RED = (3, 4, 4, 2)
X_RED = -2.0
Y_RED = -0.65           # el bloque red + termómetro, centrado bajo el título
SEP_CAPA = 2.35
SEP_NODO = 0.95
RADIO_NODO = 0.28
# Cuando el termómetro no está en pantalla, la red se centra sola y además
# crece: el tubo se lleva el tercio derecho, y sin él sobra sitio de sobra.
CENTRADO = -X_RED
AMPLIACION = 1.25
ZOOM = 3.4              # cuánto se empuja la cámara al entrar en una neurona
Y_ROTULO_GRADIENTE = 1.55   # la fila de ``-∇w``, justo encima de la red
# La arista que se sigue: del nodo 0 de la entrada al nodo 1 de la capa 1.
ARISTA_ELEGIDA = 1

# --- El termómetro, el mismo de las dos diapositivas anteriores ------------
X_TERMO = 4.6
ANCHO_TERMO = 0.8
ALTO_TERMO = 3.2
Y_PIE_TERMO = -2.3
LLENO = 0.86              # con los pesos sin tocar
TRAS_EL_PASO = 0.34       # después de restar el gradiente

# --- Acto 4: la cuenta que explota -----------------------------------------
# (capas, expresión, escala, parámetros que habría que derivar)
CRECIMIENTO = (
    (1, r"\frac{\partial L}{\partial h_1}"
        r"\cdot \frac{\partial h_1}{\partial w}", 1.15, "12"),
    (2, r"\frac{\partial L}{\partial h_2}"
        r"\cdot \frac{\partial h_2}{\partial h_1}"
        r"\cdot \frac{\partial h_1}{\partial w}", 1.0, "160"),
    (3, r"\frac{\partial L}{\partial h_3}"
        r"\cdot \frac{\partial h_3}{\partial h_2}"
        r"\cdot \frac{\partial h_2}{\partial h_1}"
        r"\cdot \frac{\partial h_1}{\partial w}", 0.86, "2 400"),
    (4, r"\frac{\partial L}{\partial h_4}"
        r"\cdot \frac{\partial h_4}{\partial h_3}"
        r"\cdot \frac{\partial h_3}{\partial h_2}"
        r"\cdot \frac{\partial h_2}{\partial h_1}"
        r"\cdot \frac{\partial h_1}{\partial w}", 0.74, "38 000"),
)

# --- Acto 6: el zoom a una neurona -----------------------------------------
Y_NEURONA = 0.2
PASO_ENTRADA = 1.15
X_ENTRADA = -4.0
X_PERILLA = -3.2
X_MULT = -1.8
X_SUMA = 0.0
X_RELU = 1.8
X_PERDIDA = 3.8
# Las tres ramas, a la misma altura para el dibujo y para las paradas de la
# ficha que baja: si cada uno las calcula por su cuenta acaban descuadradas.
ALTURAS_NEURONA = tuple(
    Y_NEURONA + PASO_ENTRADA - i * PASO_ENTRADA for i in range(3)
)


def _perilla(nombre=None, angulo=np.pi / 2, radio=0.22, lado=LEFT):
    """Un peso, dibujado como una perilla con aguja.

    Se dibuja así y no como un número porque lo que va a pasar con él es
    exactamente lo que se le hace a una perilla: girarla un poco. La aguja
    arranca **recta**, a las doce: así el giro de la corrección se ve como
    giro y no como un desorden que ya estaba. Devuelve ``VGroup(cuerpo,
    aguja)`` o, si lleva nombre, ese grupo más su etiqueta, de modo que
    ``perilla[0][1]`` es siempre la aguja.
    """
    cuerpo = Circle(radius=radio, color=AMBAR, stroke_width=3)
    cuerpo.set_fill(FONDO, opacity=1.0)
    aguja = Line(
        ORIGIN, np.array([np.cos(angulo), np.sin(angulo), 0.0]) * radio * 0.74,
        color=AMBAR, stroke_width=3,
    )
    mando = VGroup(cuerpo, aguja)
    if nombre is None:
        return VGroup(mando)
    etiqueta = MathTex(nombre, color=AMBAR).scale(0.6)
    etiqueta.next_to(mando, lado, buff=0.14)
    return VGroup(mando, etiqueta)


def _colgar(perilla, de, buff):
    """Cuelga una perilla debajo de ``de``, con el cable a plomo.

    Alinea el **mando** con el centro de ``de``, no el grupo entero: la
    etiqueta va a un lado y descentra el conjunto, así que un ``next_to`` a
    secas deja el cable torcido.
    """
    perilla.next_to(de, DOWN, buff=buff)
    return perilla.shift(
        RIGHT * (de.get_center()[0] - perilla[0].get_center()[0]),
    )


def _girar(perilla, angulo=-0.7):
    """La corrección de un peso: la aguja se mueve un poco."""
    return Rotate(perilla[0][1], angle=angulo,
                  about_point=perilla[0][0].get_center())


def _caja(etiqueta, color, ancho=ANCHO_CAJA, escala=0.8):
    caja = RoundedRectangle(
        width=ancho, height=ALTO_CAJA, corner_radius=0.16,
        stroke_color=color, stroke_width=3,
    ).set_fill(color, opacity=0.08)
    dentro = MathTex(etiqueta, color=color).scale(escala)
    return VGroup(caja, dentro.move_to(caja.get_center()))


def _flecha_corta(color=SECUNDARIO):
    return Arrow(
        LEFT * LARGO_FLECHA / 2, RIGHT * LARGO_FLECHA / 2, color=color,
        stroke_width=3, buff=0, tip_length=0.18,
    ).set_stroke(opacity=0.85)


def _cadena_funciones():
    """``x → f1 → f2 → f3 → ℓ → L``, con la ``w`` colgando de la primera.

    Se monta con ``arrange`` y no a mano: son once piezas en fila y basta con
    que quepan; los rótulos ``h`` y la perilla se cuelgan después de las piezas
    ya colocadas.
    """
    entrada = MathTex("x", color=CLARO).scale(0.95)
    efes = [_caja(f"f_{i}", PRIMARIO) for i in (1, 2, 3)]
    perdida = _caja(r"\ell", ROJO)
    salida = MathTex("L", color=ROJO).scale(1.2)
    flechas = [_flecha_corta() for _ in range(5)]

    fila = VGroup(
        entrada, flechas[0], efes[0], flechas[1], efes[1], flechas[2],
        efes[2], flechas[3], perdida, flechas[4], salida,
    ).arrange(RIGHT, buff=0.24).move_to([0, Y_CADENA, 0])

    # h1, h2 y h3 son lo que sale de cada f: van sobre las flechas de en medio.
    hs = VGroup(*[
        MathTex(f"h_{i}", color=SECUNDARIO).scale(0.65).next_to(
            flechas[i], UP, buff=0.12,
        )
        for i in (1, 2, 3)
    ])

    perilla = _colgar(_perilla("w", lado=LEFT), efes[0], buff=0.55)
    cable = Line(
        efes[0].get_bottom(), perilla[0].get_top(),
        color=AMBAR, stroke_width=2,
    ).set_stroke(opacity=0.7)

    return fila, hs, VGroup(cable, perilla), efes, perdida


def _numerito(n, debajo_de):
    """El orden en que se calculan los factores, en un círculo pequeño."""
    circulo = Circle(radius=0.16, color=SECUNDARIO, stroke_width=1.8)
    circulo.set_fill(FONDO, opacity=1.0)
    numero = texto(str(n), 13, color=SECUNDARIO).move_to(circulo.get_center())
    return VGroup(circulo, numero).next_to(debajo_de, DOWN, buff=0.16)


def _x_capa(i):
    """Abscisa de la capa ``i`` en la posición **final** de la red.

    Se calcula de las constantes y no del mobject a propósito: durante los
    actos 3 y 4 la red anda centrada y ampliada, así que preguntarle dónde
    está devuelve el sitio de entonces, no el de después.
    """
    return X_RED + (i - (len(CAPAS_RED) - 1) / 2) * SEP_CAPA


def _red():
    """La red de verdad: cuatro capas, nodos apagados y aristas finas.

    Las aristas de cada grupo se guardan en el orden ``origen`` mayor, así que
    las que salen del nodo ``k`` de la izquierda son un tramo contiguo: eso es
    lo que permite encender el abanico de un solo peso sin buscar nada.
    """
    capas = []
    for i, n in enumerate(CAPAS_RED):
        x = _x_capa(i)
        alto = (n - 1) * SEP_NODO
        capas.append(VGroup(*[
            Circle(radius=RADIO_NODO, color=SECUNDARIO, stroke_width=2.5)
            .set_fill(FONDO, opacity=1.0)
            .move_to([x, Y_RED + alto / 2 - j * SEP_NODO, 0])
            for j in range(n)
        ]))

    conexiones = []
    for izquierda, derecha in zip(capas, capas[1:]):
        grupo = VGroup()
        for a in izquierda:
            for b in derecha:
                direccion = b.get_center() - a.get_center()
                direccion = direccion / np.linalg.norm(direccion)
                grupo.add(Line(
                    a.get_center() + direccion * RADIO_NODO,
                    b.get_center() - direccion * RADIO_NODO,
                    color=SECUNDARIO, stroke_width=1.5, stroke_opacity=0.4,
                ))
        conexiones.append(grupo)
    return capas, conexiones


def _tubo():
    tubo = Rectangle(
        width=ANCHO_TERMO, height=ALTO_TERMO,
        stroke_color=SECUNDARIO, stroke_width=2,
    ).set_fill(FONDO, opacity=1.0)
    return tubo.move_to([X_TERMO, Y_PIE_TERMO + ALTO_TERMO / 2, 0])


def _liquido(fraccion):
    llenado = max(ALTO_TERMO * fraccion, 0.04)
    barra = Rectangle(
        width=ANCHO_TERMO - 0.14, height=llenado,
        stroke_width=0, fill_color=ROJO, fill_opacity=0.8,
    )
    return barra.move_to([X_TERMO, Y_PIE_TERMO + llenado / 2, 0])


def _restaurar_red(capas, conexiones):
    """Deja la red como recién dibujada.

    Hace falta porque el zoom la agranda y la desvanece a mano —``FadeOut`` no
    sabe crecer desde un punto concreto— y luego hay que devolverla entera.
    """
    for capa in capas:
        for nodo in capa:
            nodo.set_stroke(color=SECUNDARIO, width=2.5, opacity=1.0)
            nodo.set_fill(FONDO, opacity=1.0)
    for grupo in conexiones:
        grupo.set_stroke(color=SECUNDARIO, width=1.5, opacity=0.4)


def _ficha(expresion):
    """El valor que baja, en una etiqueta que tapa el cable por el que viaja.

    Es **una sola cosa** que se mueve y se reescribe, no un rótulo distinto en
    cada sitio: de eso va el acto. Va rellena del fondo para que al pasar por
    encima de un cable no se lea encima de él.
    """
    formula = MathTex(expresion, color=MORADO).scale(0.55)
    caja = RoundedRectangle(
        width=formula.width + 0.26, height=formula.height + 0.2,
        corner_radius=0.09, stroke_color=MORADO, stroke_width=2,
    ).set_fill(FONDO, opacity=1.0)
    return VGroup(caja, formula.move_to(caja.get_center()))


def _llevar(scene, fichas, destinos, cables=(), run_time=0.75):
    """Las fichas van a su siguiente parada, y el cable que usan se enciende.

    El cable se queda morado detrás, así que al final el camino recorrido
    está dibujado y se ve qué parte ya está calculada.
    """
    scene.play(
        *[f.animate.move_to(d) for f, d in zip(fichas, destinos)],
        *[c.animate.set_color(MORADO) for c in cables],
        run_time=run_time,
    )


def _convertir(ficha, expresion):
    """La ficha recoge la derivada local del sitio y pasa a ser la siguiente."""
    return Transform(ficha, _ficha(expresion).move_to(ficha.get_center()))


def _pulso(nodo, color, ancho=4.0):
    """Un nodo acusando el golpe: **solo el trazo**, y vuelto a su sitio.

    Con ``Indicate`` no vale: tiñe el mobject entero, y estos nodos van
    rellenos del color de fondo, así que por un instante se convierten en
    bolas macizas. ``there_and_back`` deja el nodo exactamente como estaba.
    """
    return nodo.animate(rate_func=there_and_back).set_stroke(
        color=color, width=ancho,
    )


def _pasada(scene, capas, conexiones, color, run_time=0.45):
    """La señal recorriendo la red hacia delante, capa a capa.

    Tres cosas a la vez en cada tramo: los puntos que viajan, el **cable que
    se enciende al paso y se apaga detrás** —de ahí el ``there_and_back``, que
    además devuelve el cable a su color de antes sin tener que recordarlo— y
    los nodos de llegada, que acusan el golpe. Sin esto último la señal
    parecía atravesar la red sin tocarla.
    """
    scene.play(
        LaggedStart(*[_pulso(n, color) for n in capas[0]], lag_ratio=0.08),
        run_time=0.5,
    )
    for grupo, destino in zip(conexiones, capas[1:]):
        pulsos = [Dot(color=color, radius=0.06).move_to(c.get_start())
                  for c in grupo]
        scene.add(*pulsos)
        scene.play(
            *[MoveAlongPath(p, c) for p, c in zip(pulsos, grupo)],
            grupo.animate(rate_func=there_and_back).set_stroke(
                color=color, opacity=0.9, width=2.2,
            ),
            run_time=run_time,
        )
        scene.play(
            *[FadeOut(p, scale=0.4) for p in pulsos],
            LaggedStart(*[_pulso(n, color) for n in destino], lag_ratio=0.06),
            run_time=0.35,
        )
        scene.remove(*pulsos)


def _neurona():
    """Una neurona por dentro: entradas, perillas, ×, +, ReLU y la pérdida.

    Es el mismo cálculo de la diapositiva del perceptrón, pero desarmado en
    piezas, porque lo que hay que ver aquí es que entre cada perilla y el error
    solo hay tres pasos, no toda la red.
    """
    ys = ALTURAS_NEURONA

    entradas = VGroup(*[
        MathTex(f"x_{i + 1}", color=CLARO).scale(0.75).move_to(
            [X_ENTRADA, y, 0],
        )
        for i, y in enumerate(ys)
    ])
    perillas = VGroup(*[
        _perilla(f"w_{i + 1}").move_to([X_PERILLA, y - 0.62, 0])
        for i, y in enumerate(ys)
    ])
    multiplicadores = VGroup(*[
        VGroup(
            Circle(radius=0.24, color=SECUNDARIO, stroke_width=2.5)
            .set_fill(FONDO, opacity=1.0),
            MathTex(r"\times", color=SECUNDARIO).scale(0.7),
        ).move_to([X_MULT, y, 0])
        for y in ys
    ])
    suma = VGroup(
        Circle(radius=0.28, color=SECUNDARIO, stroke_width=2.5)
        .set_fill(FONDO, opacity=1.0),
        MathTex("+", color=SECUNDARIO).scale(0.8),
    ).move_to([X_SUMA, Y_NEURONA, 0])
    sesgo = _colgar(_perilla("b", lado=LEFT), suma, buff=1.35)

    relu = _caja(r"\mathrm{ReLU}", PRIMARIO, ancho=1.5, escala=0.55)
    relu.move_to([X_RELU, Y_NEURONA, 0])
    perdida = _caja("L", ROJO, ancho=0.95, escala=0.85)
    perdida.move_to([X_PERDIDA, Y_NEURONA, 0])

    # Los cables van por tramos con nombre, no en un montón: la vuelta los
    # recorre uno a uno y en orden, y cada tramo es un factor de la cadena.
    cables_entrada = VGroup(*[
        Line([X_ENTRADA + 0.22, y, 0], [X_MULT - 0.24, y, 0],
             color=SECUNDARIO, stroke_width=2).set_stroke(opacity=0.7)
        for y in ys
    ])
    cables_peso = VGroup(*[
        Line(perillas[i][0].get_top(), [X_MULT - 0.17, y - 0.17, 0],
             color=AMBAR, stroke_width=2).set_stroke(opacity=0.7)
        for i, y in enumerate(ys)
    ])
    cables_suma = VGroup(*[
        Line([X_MULT + 0.24, y, 0], suma[0].get_center(),
             color=SECUNDARIO, stroke_width=2).set_stroke(opacity=0.7)
        for y in ys
    ])
    cable_sesgo = Line(
        sesgo[0].get_top(), suma[0].get_bottom(),
        color=AMBAR, stroke_width=2,
    ).set_stroke(opacity=0.7)
    flecha_z = Arrow(suma[0].get_right(), relu.get_left(), color=SECUNDARIO,
                     stroke_width=3, buff=0.12, tip_length=0.18)
    flecha_a = Arrow(relu.get_right(), perdida.get_left(), color=SECUNDARIO,
                     stroke_width=3, buff=0.12, tip_length=0.18)
    VGroup(flecha_z, flecha_a).set_stroke(opacity=0.85)

    # Los valores intermedios, nombrados: sin esto la cadena de abajo habla de
    # ``p``, ``z`` y ``a`` sin que se sepa dónde están.
    etiquetas = VGroup(
        *[MathTex(f"p_{i + 1}", color=SECUNDARIO).scale(0.55).next_to(
            multiplicadores[i], UP, buff=0.12,
        ) for i in range(3)],
        MathTex("z", color=SECUNDARIO).scale(0.6).next_to(
            flecha_z, UP, buff=0.1),
        MathTex("a", color=SECUNDARIO).scale(0.6).next_to(
            flecha_a, UP, buff=0.1),
    )

    # El ``+`` sale aparte del resto: es la pieza en la que se convierte el
    # nodo de la red al hacer zoom, así que la animación necesita agarrarla.
    resto = VGroup(
        cables_entrada, cables_peso, cables_suma, cable_sesgo,
        flecha_z, flecha_a, entradas, multiplicadores, relu, perdida,
        perillas, sesgo, etiquetas,
    )
    tramos = (flecha_a, flecha_z, cables_suma, cables_peso, cable_sesgo)
    return suma, resto, perillas, sesgo, tramos


def construir(scene):
    encabezado = hacer_titulo("Una función dentro de otra")
    encabezado_bp = hacer_titulo("Backpropagation")

    # --- Acto 1: la compuesta, abierta -------------------------------------
    compuesta = MathTex(
        "L", "(", "w", ")", "=", "L", r"\big(", "f(x;", "w", ")", ",", "y",
        r"\big)",
    ).scale(1.05).move_to([0, 1.95, 0])
    for i in (0, 1, 3, 5, 6, 12):
        compuesta[i].set_color(ROJO)
    for i in (2, 8):
        compuesta[i].set_color(AMBAR)
    for i in (7, 9):
        compuesta[i].set_color(PRIMARIO)
    for i in (10, 11):
        compuesta[i].set_color(CLARO)

    fila, hs, mando, efes, caja_perdida = _cadena_funciones()

    # --- Acto 2: la regla de la cadena -------------------------------------
    cadena = MathTex(
        r"\frac{\partial L}{\partial w}", "=",
        r"\frac{\partial L}{\partial h_3}", r"\cdot",
        r"\frac{\partial h_3}{\partial h_2}", r"\cdot",
        r"\frac{\partial h_2}{\partial h_1}", r"\cdot",
        r"\frac{\partial h_1}{\partial w}",
    ).scale(1.0).move_to([0, -1.9, 0])
    cadena[0].set_color(AMBAR)
    cadena[2].set_color(ROJO)
    cadena[4].set_color(PRIMARIO)
    cadena[6].set_color(PRIMARIO)
    cadena[8].set_color(AMBAR)
    numeros = VGroup(*[
        _numerito(n, cadena[2 * n]) for n in (1, 2, 3, 4)
    ])

    # --- Actos 3 a 8: la red ------------------------------------------------
    capas, conexiones = _red()
    red = VGroup(*conexiones, *capas)
    # Los actos 3 y 4 no llevan termómetro, así que para ellos la red se
    # centra y se agranda —y todo lo que se cuelga de ella se calcula ya en
    # ese tamaño—; en el acto 5 deshace las dos cosas y vuelve a su sitio,
    # con el tubo ocupando la derecha.
    centro_red = np.array([0.0, Y_RED, 0.0])
    red.shift(RIGHT * CENTRADO).scale(AMPLIACION, about_point=centro_red)

    # El abanico de un solo peso: la arista elegida y todo lo que cuelga de
    # ella. Con 4 y 2 nodos por delante son ocho caminos hasta la salida.
    elegida = conexiones[0][ARISTA_ELEGIDA]
    rot_elegida = MathTex("w", color=AMBAR).scale(0.7)
    rot_elegida.next_to(elegida.get_center(), UP + LEFT, buff=0.08)
    destino = ARISTA_ELEGIDA % len(capas[1])
    abanico = [
        VGroup(*conexiones[1][destino * len(capas[2]):
                             (destino + 1) * len(capas[2])]),
        conexiones[2],
    ]
    # --- Acto 4: la cuenta que explota -------------------------------------
    def _bloque(capas_n, expresion, escala, parametros):
        """Los tres renglones del acto, cada uno anclado a su altura fija.

        Anclados y no apilados con ``arrange``: la fórmula encoge conforme se
        alarga —de eso va el acto— y con una pila el rótulo y la cuenta darían
        un brinco en cada paso.
        """
        formula = MathTex(expresion, color=CLARO).scale(escala)
        formula.move_to([0, -0.05, 0])
        rotulo = texto(f"{capas_n} capa{'s' if capas_n > 1 else ''}", 24,
                       color=PRIMARIO).move_to([0, 1.55, 0])
        cuenta = VGroup(
            texto(parametros, 40, color=AMBAR),
            texto("parámetros que derivar", 19, color=SECUNDARIO),
        ).arrange(DOWN, buff=0.14).move_to([0, -2.1, 0])
        return formula, rotulo, cuenta

    formula, rotulo, cuenta = _bloque(*CRECIMIENTO[0])

    # --- Actos 5 a 8: backpropagation --------------------------------------
    tubo = _tubo()
    rotulo_termo = texto("error", 19, color=ROJO).next_to(tubo, UP, buff=0.22)
    nivel_alto = _liquido(LLENO)

    nucleo, resto_neurona, perillas, sesgo, tramos = _neurona()
    flecha_a, flecha_z, cables_suma, cables_peso, cable_sesgo = tramos
    piezas_neurona = VGroup(nucleo, resto_neurona)

    # Un ``-∇w`` por capa, encima del grupo de conexiones que le toca. Solo se
    # ve mientras esa capa se corrige: el de al lado no ha llegado todavía y
    # el de atrás ya se aplicó, y con los tres a la vez el ojo no sabía cuál
    # mirar.
    gradientes = VGroup(*[
        MathTex(r"-\nabla w", color=MORADO).scale(0.75).move_to([
            (_x_capa(i) + _x_capa(i + 1)) / 2, Y_ROTULO_GRADIENTE, 0,
        ])
        for i in range(len(CAPAS_RED) - 1)
    ])

    # La moraleja del acto, en una línea: el trozo morado es el que ya venía
    # calculado y sirve igual para los tres pesos; lo único propio de cada uno
    # es su ``x``. Escrito con los mismos colores que la ficha y las entradas.
    reuso = MathTex(
        r"\frac{\partial L}{\partial w_i}", "=",
        r"\frac{\partial L}{\partial z}", r"\cdot", "x_i",
    ).scale(0.9).move_to([0, -2.9, 0])
    reuso[0].set_color(AMBAR)
    reuso[2].set_color(MORADO)
    reuso[4].set_color(CLARO)

    # Las paradas de la ficha, todas sobre el camino que recorre.
    parada_salida = np.array([(X_RELU + X_PERDIDA) / 2, Y_NEURONA, 0])
    parada_activa = np.array([(X_SUMA + X_RELU) / 2, Y_NEURONA, 0])
    parada_suma = np.array([X_SUMA - 0.62, Y_NEURONA, 0])
    paradas_mult = [np.array([X_MULT + 0.85, y, 0]) for y in ALTURAS_NEURONA]
    etiqueta_relu = MathTex(
        r"\cdot\ \frac{\partial a}{\partial z}", color=PRIMARIO,
    ).scale(0.6).move_to([X_RELU, Y_NEURONA + 0.95, 0])
    # Se hace zoom a la neurona que ya venía marcada del acto 3: la que recibe
    # la ``w`` que seguimos. Y es de la primera capa oculta, así que tiene
    # exactamente tres entradas, las mismas que el dibujo de dentro.
    nodo_zoom = capas[1][ARISTA_ELEGIDA % len(capas[1])]

    # ---------------------- Animación --------------------------------------
    # 1. La compuesta de la diapositiva anterior, abierta en cadena.
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(FadeIn(compuesta), run_time=0.8)
    scene.play(
        LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in fila],
                    lag_ratio=0.12),
        run_time=1.8,
    )
    scene.play(FadeIn(hs), Create(mando), run_time=0.8)
    scene.next_slide()

    # 2. La regla de la cadena: un eslabón por salto del dibujo. Los números
    # dicen en qué orden se calculan, que es de la salida hacia atrás.
    scene.play(Write(cadena), run_time=1.6)
    scene.play(
        LaggedStart(*[FadeIn(n, scale=0.5) for n in numeros], lag_ratio=0.2),
        run_time=1.0,
    )
    scene.next_slide()

    # 3. En una red de verdad: una sola w toca todo lo que hay por delante.
    scene.play(
        FadeOut(compuesta), FadeOut(fila), FadeOut(hs), FadeOut(mando),
        FadeOut(cadena), FadeOut(numeros),
        run_time=0.8,
    )
    scene.play(FadeIn(red), run_time=0.9)
    scene.play(
        elegida.animate.set_stroke(color=AMBAR, opacity=1.0, width=3.5),
        FadeIn(rot_elegida),
        run_time=0.7,
    )
    for grupo in abanico:
        scene.play(grupo.animate.set_stroke(color=ROJO, opacity=0.75,
                                            width=2.2), run_time=0.6)
    scene.next_slide()

    # 4. Y la cuenta, que crece con cada capa hasta que deja de tener sentido.
    scene.play(FadeOut(red), FadeOut(rot_elegida), run_time=0.7)
    scene.play(FadeIn(rotulo), Write(formula), FadeIn(cuenta), run_time=1.2)
    for paso in CRECIMIENTO[1:]:
        nueva_formula, nuevo_rotulo, nueva_cuenta = _bloque(*paso)
        scene.play(
            Transform(formula, nueva_formula),
            Transform(rotulo, nuevo_rotulo),
            Transform(cuenta, nueva_cuenta),
            run_time=0.9,
        )
    scene.next_slide()

    # 5. La solución tiene nombre. Una pasada hacia delante, y el error arriba.
    scene.play(
        FadeOut(formula), FadeOut(rotulo), FadeOut(cuenta),
        FadeOut(encabezado), FadeIn(encabezado_bp, shift=DOWN * 0.2),
        run_time=0.9,
    )
    # La red vuelve a su tamaño, a su sitio y a como estaba: sin abanico.
    red.scale(1 / AMPLIACION, about_point=centro_red).shift(LEFT * CENTRADO)
    for grupo in conexiones:
        grupo.set_stroke(color=SECUNDARIO, opacity=0.4, width=1.5)
    scene.play(FadeIn(red), Create(tubo), FadeIn(rotulo_termo), run_time=0.9)
    _pasada(scene, capas, conexiones, VERDE, run_time=0.42)
    # El termómetro se llena subiendo, no apareciendo de golpe: es el gesto de
    # un termómetro y además encadena con la señal que acaba de llegar.
    nivel = _liquido(0.02)
    scene.add(nivel)
    scene.play(Transform(nivel, nivel_alto), run_time=0.8)
    scene.next_slide()

    # 6. Zoom a una neurona: se marca cuál, y el nodo se abre por dentro.
    scene.play(nodo_zoom.animate.set_stroke(color=AMBAR, width=4.5),
               run_time=0.5)
    scene.play(nodo_zoom.animate(rate_func=there_and_back).scale(1.35),
               run_time=0.6)
    # El zoom es un empuje de cámara fingido: la red entera crece **desde el
    # nodo marcado** y se apaga a la vez, así que el ojo se mete por ahí. Un
    # ``FadeOut`` con ``scale`` no sirve: crece desde el centro del grupo, no
    # desde el punto que interesa.
    foco = nodo_zoom.get_center()
    scene.play(
        red.animate.scale(ZOOM, about_point=foco).set_opacity(0),
        FadeOut(tubo), FadeOut(rotulo_termo), FadeOut(nivel),
        run_time=1.2,
    )
    scene.remove(red)
    scene.play(FadeIn(nucleo), FadeIn(resto_neurona), run_time=0.9)
    scene.next_slide()

    # Una sola ficha baja desde el error, y en cada parada se multiplica por
    # la derivada local del sitio: no se recalcula nada, se arrastra lo de
    # antes. Empieza valiendo lo que le llega a la salida de la neurona.
    ficha = _ficha(r"\frac{\partial L}{\partial a}").move_to(parada_salida)
    scene.play(FadeIn(ficha, scale=0.6), run_time=0.6)
    _llevar(scene, [ficha], [parada_activa], [flecha_a])
    scene.play(FadeIn(etiqueta_relu, shift=DOWN * 0.1), run_time=0.4)
    scene.play(_convertir(ficha, r"\frac{\partial L}{\partial z}"),
               run_time=0.7)
    _llevar(scene, [ficha], [parada_suma], [flecha_z])
    scene.next_slide()

    # En la suma no hay nada que multiplicar: la ficha se reparte tal cual.
    # Esa copia es el ahorro entero de backpropagation, así que se ve.
    ramas = [ficha.copy() for _ in ALTURAS_NEURONA]
    rama_sesgo = ficha.copy()
    scene.add(*ramas, rama_sesgo)
    scene.remove(ficha)
    _llevar(
        scene, ramas + [rama_sesgo],
        paradas_mult + [sesgo[0].get_center() + UP * 0.8],
        list(cables_suma) + [cable_sesgo], run_time=0.9,
    )
    scene.play(FadeIn(reuso, shift=UP * 0.12), run_time=0.7)

    # Y en cada producto, lo único propio de cada peso: su entrada.
    scene.play(
        LaggedStart(*[
            _convertir(r, rf"\frac{{\partial L}}{{\partial w_{i + 1}}}")
            for i, r in enumerate(ramas)
        ], lag_ratio=0.18),
        _convertir(rama_sesgo, r"\frac{\partial L}{\partial b}"),
        run_time=1.0,
    )
    scene.next_slide()

    # La ficha se gasta girando su perilla: ahí se acaba el viaje.
    _llevar(
        scene, ramas + [rama_sesgo],
        [p[0].get_center() for p in perillas] + [sesgo[0].get_center()],
        list(cables_peso), run_time=0.8,
    )
    scene.play(
        LaggedStart(*[FadeOut(r, scale=0.3) for r in ramas + [rama_sesgo]],
                    lag_ratio=0.12),
        LaggedStart(*[_girar(p) for p in perillas], lag_ratio=0.12),
        _girar(sesgo),
        run_time=1.0,
    )
    scene.next_slide()

    # 7. Y lo mismo en toda la red: hacia atrás, capa a capa, restando.
    scene.play(FadeOut(piezas_neurona), FadeOut(reuso),
               FadeOut(etiqueta_relu), run_time=0.7)
    red.scale(1 / ZOOM, about_point=foco)
    _restaurar_red(capas, conexiones)
    scene.play(FadeIn(red), FadeIn(tubo), FadeIn(rotulo_termo),
               FadeIn(nivel), run_time=0.7)
    # El ``-∇w`` de cada capa es de quita y pon: baja sobre la capa que se
    # está corrigiendo y se hunde en ella cuando la culpa sigue camino, así
    # que en pantalla hay siempre uno solo, el de la capa que toca.
    anterior = None
    for i in range(len(conexiones) - 1, -1, -1):
        grupo = conexiones[i]
        pulsos = [Dot(color=MORADO, radius=0.06).move_to(c.get_end())
                  for c in grupo]
        caminos = [Line(c.get_end(), c.get_start()) for c in grupo]
        scene.add(*pulsos)
        scene.play(
            *[MoveAlongPath(p, c) for p, c in zip(pulsos, caminos)],
            *([FadeOut(anterior, shift=DOWN * 0.3)] if anterior else []),
            run_time=0.6,
        )
        scene.play(
            *[p.animate.set_opacity(0) for p in pulsos],
            LaggedStart(*[_pulso(n, MORADO) for n in capas[i]],
                        lag_ratio=0.07),
            # Y se quedan en ámbar: son pesos nuevos.
            grupo.animate.set_stroke(color=AMBAR, opacity=0.8, width=1.8),
            FadeIn(gradientes[i], shift=DOWN * 0.3),
            run_time=0.6,
        )
        scene.remove(*pulsos)
        anterior = gradientes[i]
    scene.play(FadeOut(anterior, shift=DOWN * 0.3), run_time=0.45)
    scene.next_slide()

    # 8. Otra vez hacia delante, con los pesos ya corregidos.
    _pasada(scene, capas, conexiones, VERDE, run_time=0.42)
    scene.play(Transform(nivel, _liquido(TRAS_EL_PASO)), run_time=1.0)
    scene.wait(0.4)

    scene.next_slide()
