"""Diapositiva 3 — ¿Cómo aprendemos nosotros?

Sin explicaciones: se ve. Alguien lanza una bola hacia su otra mano y falla. Ve
por cuánto ha fallado —la distancia queda marcada en el suelo—, vuelve a tirar y
falla menos. Y menos. Hasta que la coge. Entonces saca las otras dos y hace la
cascada entera.

Toda la idea de la charla está aquí en gestos: intentar, mirar el error,
corregir, repetir. Cuando lleguemos a la función de pérdida y al descenso del
gradiente, será esta misma diapositiva con números.

Va antes de "No es una idea nueva" para que, cuando aparezca Rosenblatt, ya se
entienda qué estaba intentando imitar.
"""

import numpy as np
from manim import (
    DOWN,
    PI,
    UP,
    CapStyleType,
    Circle,
    Create,
    DashedLine,
    Dot,
    Ellipse,
    FadeIn,
    FadeOut,
    Flash,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    Line,
    MoveAlongPath,
    Polygon,
    Succession,
    TracedPath,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    Wait,
    linear,
    there_and_back,
)

from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, SECUNDARIO, VERDE

X_FIG = 0.0
Y_SUELO = -2.5
ESCALA = 1.32          # tamaño del malabarista (todo lo demás lo sigue)
ALTO_MANO = 1.5        # altura de las manos, antes de escalar
SEP_MANO = 1.0         # separación de cada mano al eje del cuerpo, sin escalar
RADIO_BOLA = 0.16
CIMA = 2.15            # vértice de los lanzamientos largos (los que fallan)
# Vértice de los lanzamientos de mano a mano. Tiene que quedar por debajo de la
# anchura del tiro: si el arco sube más de lo que cruza, las bolas parecen subir
# y bajar en vertical en vez de dibujar la cascada.
CIMA_CASCADA = 1.05

# Ritmo de la cascada. ``INTERVALO`` es cada cuánto sale una bola de la mano;
# con tres bolas, cada una lanza cada ``3 * INTERVALO``, así que el vuelo tiene
# que caber ahí dentro y lo que sobra es el tiempo que descansa en la mano.
VUELO = 0.8
INTERVALO = 0.42
CICLOS = 4             # lanzamientos por bola

# Por cuánto falla en cada intento (a la izquierda de la mano que espera).
# El cuarto intento es acertar: la secuencia entera es el aprendizaje.
DESVIOS = (2.1, 1.15, 0.5)

Y_MARCAS = -3.35       # fila de ✗ / ✓, debajo del suelo
PASO_MARCAS = 0.46

ANCLA = np.array([X_FIG, Y_SUELO, 0.0])


def _escalar(punto):
    """Lleva un punto de las proporciones base al tamaño final de la figura."""
    return ANCLA + (np.array(punto) - ANCLA) * ESCALA


def _mano(signo):
    """Posición de una mano: ``-1`` la izquierda, ``+1`` la derecha."""
    return _escalar([X_FIG + signo * SEP_MANO, Y_SUELO + ALTO_MANO, 0.0])


def _curva(puntos, color=CLARO, grosor=5):
    """Trazo suave que pasa por los puntos dados, con las puntas redondeadas."""
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly([np.array(p) for p in puntos])
    curva.cap_style = CapStyleType.ROUND
    return curva


def _figura():
    """El malabarista: trazos curvos, cabeza hueca y sombra en el suelo.

    Se dibuja en proporciones base y se escala al final desde los pies, que es
    lo que mantiene coherentes las posiciones que devuelve ``_mano``.
    """
    cadera = np.array([X_FIG, Y_SUELO + 1.05, 0.0])
    hombros = np.array([X_FIG, Y_SUELO + 1.95, 0.0])

    cabeza = Circle(radius=0.3, color=CLARO, stroke_width=5)
    cabeza.move_to([X_FIG, Y_SUELO + 2.36, 0])
    cuello = Line(hombros, [X_FIG, Y_SUELO + 2.06, 0], color=CLARO, stroke_width=5)

    # Tronco y piernas con una curvatura mínima: quita rigidez de palo.
    tronco = _curva([hombros, [X_FIG - 0.05, Y_SUELO + 1.5, 0], cadera])
    piernas = VGroup(*[
        _curva([
            cadera,
            [X_FIG + s * 0.28, Y_SUELO + 0.55, 0],
            [X_FIG + s * 0.34, Y_SUELO, 0],
        ])
        for s in (-1, 1)
    ])
    brazos = VGroup(*[
        _curva([
            hombros,
            [X_FIG + s * 0.55, Y_SUELO + 1.5, 0],
            [X_FIG + s * SEP_MANO, Y_SUELO + ALTO_MANO, 0],
        ])
        for s in (-1, 1)
    ])

    sombra = Ellipse(width=1.5, height=0.22, color=SECUNDARIO)
    sombra.set_fill(SECUNDARIO, opacity=0.18).set_stroke(width=0)
    sombra.move_to([X_FIG, Y_SUELO - 0.02, 0])

    figura = VGroup(sombra, piernas, tronco, cuello, cabeza, brazos)
    return figura.scale(ESCALA, about_point=ANCLA)


def _bola(color, posicion):
    """Bola de cristal: halos concentrados, núcleo sólido y un brillo arriba."""
    halos = VGroup(*[
        Circle(radius=RADIO_BOLA * factor, color=color, stroke_width=0)
        .set_fill(color, opacity=opacidad)
        for factor, opacidad in ((3.0, 0.06), (2.2, 0.11), (1.5, 0.2))
    ])
    nucleo = Dot(radius=RADIO_BOLA, color=color)
    brillo = Dot(radius=RADIO_BOLA * 0.32, color=CLARO).set_opacity(0.8)
    brillo.shift(np.array([-RADIO_BOLA * 0.33, RADIO_BOLA * 0.33, 0.0]))
    return VGroup(halos, nucleo, brillo).move_to(posicion)


def _lanzamiento(bola, inicio, fin, cima=CIMA, **kwargs):
    """Vuelo de una bola: parábola real, con su gravedad.

    Mover la bola por un arco a velocidad constante la hace flotar arriba y
    frenar en seco al llegar. Aquí la horizontal avanza a ritmo fijo y la
    vertical es cuadrática en el tiempo, que es exactamente caída libre: sale
    rápida de la mano, se demora en el vértice y vuelve a acelerar al caer.
    """
    inicio, fin = np.array(inicio, dtype=float), np.array(fin, dtype=float)
    curvatura = 4 * (cima - (inicio[1] + fin[1]) / 2)

    def volar(mob, alfa):
        x = inicio[0] + (fin[0] - inicio[0]) * alfa
        y = (inicio[1] + (fin[1] - inicio[1]) * alfa
             + curvatura * alfa * (1 - alfa))
        mob.move_to([x, y, 0])

    return UpdateFromAlphaFunc(bola, volar, rate_func=linear, **kwargs)


def _rastro(bola, color):
    """Estela que sigue a la bola y se va borrando sola."""
    return TracedPath(
        bola.get_center, stroke_color=color, stroke_width=4,
        stroke_opacity=0.75, dissipating_time=0.5,
    )


def _panel_zoom(centro, radio):
    """Círculo de aumento: cristal opaco, aro de marca y halo alrededor.

    Nada de lupa con mango; es una ventana al interior. El relleno va del color
    de fondo para que tape lo que haya debajo y dentro solo se vea lo que
    pongamos después.
    """
    halo = VGroup(*[
        Circle(radius=radio + separacion, color=PRIMARIO, stroke_width=grosor)
        .set_stroke(opacity=opacidad).move_to(centro)
        for separacion, grosor, opacidad in ((0.19, 10, 0.09), (0.08, 6, 0.2))
    ])
    cristal = Circle(radius=radio, color=PRIMARIO, stroke_width=5)
    cristal.set_fill(FONDO, opacity=1.0).move_to(centro)
    return VGroup(halo, cristal)


def _mira(centro, radio):
    """Cuatro esquinas de encuadre alrededor de la cabeza."""
    brazo = radio * 0.55
    esquinas = VGroup()
    for lado_x in (-1, 1):
        for lado_y in (-1, 1):
            vertice = centro + np.array([lado_x * radio, lado_y * radio, 0.0])
            esquinas.add(
                Line(vertice, vertice - np.array([lado_x * brazo, 0, 0]),
                     color=PRIMARIO, stroke_width=4),
                Line(vertice, vertice - np.array([0, lado_y * brazo, 0]),
                     color=PRIMARIO, stroke_width=4),
            )
    return esquinas


def _barrido(centro, radio):
    """Línea de escáner con su resplandor, lista para recorrer la cabeza.

    Devuelve el grupo y la función que lo coloca según el avance: el ancho de
    la línea se recorta a la cuerda del círculo a esa altura, así el barrido
    queda ceñido a la cabeza en vez de ser una raya que la cruza.
    """
    barra = VGroup(
        Line(centro, centro + np.array([0.01, 0, 0]),
             color=PRIMARIO, stroke_width=14).set_stroke(opacity=0.22),
        Line(centro, centro + np.array([0.01, 0, 0]),
             color=CLARO, stroke_width=3),
    )

    def colocar(grupo, alfa):
        altura = radio * (1 - 2 * alfa)
        media = max(np.sqrt(max(radio ** 2 - altura ** 2, 0.0)), 0.02)
        for linea in grupo:
            linea.put_start_and_end_on(
                centro + np.array([-media, altura, 0]),
                centro + np.array([media, altura, 0]),
            )

    colocar(barra, 0)
    return barra, colocar


def _haz(origen, radio_origen, destino, radio_destino):
    """Cono de aumento entre la cabeza y el panel, como un haz de luz."""
    eje = destino - origen
    perpendicular = np.array([-eje[1], eje[0], 0.0]) / np.linalg.norm(eje)
    a, b = (origen + perpendicular * radio_origen,
            origen - perpendicular * radio_origen)
    c, d = (destino + perpendicular * radio_destino,
            destino - perpendicular * radio_destino)
    relleno = Polygon(a, c, d, b, stroke_width=0)
    relleno.set_fill(PRIMARIO, opacity=0.05)
    bordes = VGroup(*[
        Line(inicio, fin, color=PRIMARIO, stroke_width=2).set_stroke(opacity=0.3)
        for inicio, fin in ((a, c), (b, d))
    ])
    return VGroup(relleno, bordes)


def _tejido(centro, radio, cantidad=26, semilla=11):
    """Maraña densa de neuronas: somas con halo y la red que las une.

    Devuelve ``(malla, somas, conexiones)``; las conexiones sueltas sirven para
    mandar impulsos por ellas. Las posiciones se reparten con rechazo simple
    para que ninguna quede pegada a otra.
    """
    rng = np.random.default_rng(semilla)
    util = radio - 0.4
    puntos = []
    for _ in range(6000):
        if len(puntos) == cantidad:
            break
        distancia = util * np.sqrt(rng.random())
        angulo = rng.uniform(0, 2 * PI)
        punto = centro + np.array([distancia * np.cos(angulo),
                                   distancia * np.sin(angulo), 0.0])
        if all(np.linalg.norm(punto - otro) > 0.33 for otro in puntos):
            puntos.append(punto)

    conexiones = []
    for i, uno in enumerate(puntos):
        for otro in puntos[i + 1:]:
            if np.linalg.norm(uno - otro) < 0.72:
                medio = (uno + otro) / 2 + rng.uniform(-0.06, 0.06, 3) * [1, 1, 0]
                conexiones.append(_curva([uno, medio, otro],
                                         color=PRIMARIO, grosor=1.6))
    for hilo in conexiones:
        hilo.set_stroke(opacity=0.4)

    somas = VGroup()
    for punto in puntos:
        halo = Circle(radius=0.13, color=PRIMARIO, stroke_width=0)
        halo.set_fill(PRIMARIO, opacity=0.13).move_to(punto)
        # Dos o tres muñones cortos: dan textura de neurona sin ensuciar la red.
        muñones = VGroup(*[
            Line(punto, punto + np.array([np.cos(a) * 0.17, np.sin(a) * 0.17, 0]),
                 color=PRIMARIO, stroke_width=2).set_stroke(opacity=0.55)
            for a in rng.uniform(0, 2 * PI, 3)
        ])
        somas.add(VGroup(halo, muñones, Dot(punto, radius=0.055, color=PRIMARIO)))

    return VGroup(*conexiones), somas, conexiones


def _cruz(color=SECUNDARIO):
    d = 0.11
    return VGroup(
        Line([-d, -d, 0], [d, d, 0], color=color, stroke_width=4),
        Line([-d, d, 0], [d, -d, 0], color=color, stroke_width=4),
    )


def _tick(color=VERDE):
    marca = VMobject(color=color, stroke_width=5)
    marca.set_points_as_corners([
        [-0.13, 0.02, 0], [-0.04, -0.11, 0], [0.16, 0.17, 0],
    ])
    return marca


def _sitio_marca(indice):
    """Hueco de la marca nº ``indice`` en una fila centrada bajo la figura."""
    total = len(DESVIOS) + 1
    return [X_FIG + (indice - (total - 1) / 2) * PASO_MARCAS, Y_MARCAS, 0]


def _impulso(scene, figura):
    """Flexión mínima del cuerpo justo antes de lanzar: da vida al muñeco.

    Nada por debajo de ~0.25 s: un ``play`` de dos fotogramas hace fallar el
    concatenado de manim-slides (``ArgumentError`` al muxear).
    """
    scene.play(figura.animate.shift(DOWN * 0.09), run_time=0.3,
               rate_func=there_and_back)


def construir(scene):
    encabezado = hacer_titulo("¿Cómo aprendemos nosotros?")

    figura = _figura()
    suelo = Line(
        [X_FIG - 5.2, Y_SUELO, 0], [X_FIG + 5.2, Y_SUELO, 0],
        color=SECUNDARIO, stroke_width=2, stroke_opacity=0.4,
    )
    # Dónde tiene que caer la bola, y esa altura bajada al suelo: sin la guía
    # vertical, la marca de error parecería medir hasta ningún sitio.
    diana = Circle(radius=0.22, color=SECUNDARIO, stroke_width=2.5)
    diana.set_stroke(opacity=0.55).move_to(_mano(-1))
    guia = DashedLine(
        _mano(-1) + DOWN * 0.22, [_mano(-1)[0], Y_SUELO, 0],
        color=SECUNDARIO, stroke_width=1.6, dash_length=0.07,
    ).set_stroke(opacity=0.4)

    bola = _bola(PRIMARIO, _mano(1))

    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(figura), Create(suelo), run_time=1.2)
    scene.play(GrowFromCenter(bola), FadeIn(diana), FadeIn(guia), run_time=0.5)
    scene.next_slide()

    # --- Fallar, ver por cuánto, y volver a tirar --------------------------
    for intento, desvio in enumerate(DESVIOS):
        rastro = _rastro(bola, PRIMARIO)
        scene.add(rastro)

        # Se queda corta: cae al suelo a ``desvio`` de la mano que esperaba.
        caida = np.array([_mano(-1)[0] - desvio, Y_SUELO + RADIO_BOLA, 0.0])
        _impulso(scene, figura)
        scene.play(_lanzamiento(bola, _mano(1), caida), run_time=0.95)
        scene.play(bola.animate.shift(UP * 0.2), run_time=0.28,
                   rate_func=there_and_back)
        scene.remove(rastro)

        # Lo que se ve es el error: lo que le ha faltado para llegar a la mano.
        error = DashedLine(
            [caida[0], Y_SUELO + 0.08, 0], [_mano(-1)[0], Y_SUELO + 0.08, 0],
            color=AMBAR, stroke_width=3.5, dash_length=0.11,
        )
        cruz = _cruz().move_to(_sitio_marca(intento))
        scene.play(Create(error), FadeIn(cruz),
                   Indicate(diana, color=AMBAR, scale_factor=1.3), run_time=0.5)
        scene.next_slide()

        # Corrige y vuelve a empezar: recoge la bola con un arco bajo.
        scene.play(
            _lanzamiento(bola, caida, _mano(1), Y_SUELO + 1.15),
            FadeOut(error), run_time=0.6,
        )

    # --- Ahora sí: la bola cae en la mano ----------------------------------
    rastro = _rastro(bola, PRIMARIO)
    scene.add(rastro)
    _impulso(scene, figura)
    scene.play(
        _lanzamiento(bola, _mano(1), _mano(-1), CIMA_CASCADA + 0.2),
        run_time=0.85,
    )
    scene.remove(rastro)
    scene.play(
        FadeIn(_tick().move_to(_sitio_marca(len(DESVIOS)))),
        Flash(bola, color=VERDE, line_length=0.26, num_lines=14,
              flash_radius=0.5),
        FadeOut(diana), FadeOut(guia),
        run_time=0.7,
    )
    scene.next_slide()

    # --- Y con el gesto aprendido, las tres --------------------------------
    otras = VGroup(
        _bola(AMBAR, _mano(1) + np.array([0.19, -0.03, 0])),
        _bola(MORADO, _mano(-1) + np.array([-0.17, 0.03, 0])),
    )
    scene.play(GrowFromCenter(otras), run_time=0.5)

    bolas = [bola, otras[0], otras[1]]
    colores = (PRIMARIO, AMBAR, MORADO)
    rastros = [_rastro(b, c) for b, c in zip(bolas, colores)]
    scene.add(*rastros)

    # Cascada: una secuencia por bola, lanzadas en paralelo y desfasadas.
    #
    # No vale meter los doce lanzamientos en un LaggedStart: al arrancar, el
    # grupo hace ``begin()`` de todos a la vez y cada ``begin()`` planta su bola
    # en el punto de salida de ese lanzamiento, así que manda el último y las
    # bolas aparecen en la mano equivocada para luego saltar de golpe. Con una
    # Succession por bola solo está viva una animación de esa bola a la vez.
    huecos = [_mano(-1), _mano(1) + np.array([0.19, -0.03, 0]),
              _mano(-1) + np.array([-0.17, 0.03, 0])]
    signos = [-1, 1, -1]
    espera = 3 * INTERVALO - VUELO  # lo que la bola descansa en la mano

    secuencias = []
    for i, bola_i in enumerate(bolas):
        partes = [] if i == 0 else [Wait(run_time=i * INTERVALO)]
        actual, signo = huecos[i], signos[i]
        for ciclo in range(CICLOS):
            signo *= -1
            # Cada bola aterriza con su propio sesgo: si no, dos caen en el
            # mismo punto de la mano y una tapa a la otra.
            destino = _mano(signo) + np.array([(i - 1) * 0.15, 0.07 - i * 0.05, 0])
            partes.append(_lanzamiento(
                bola_i, actual, destino, CIMA_CASCADA + i * 0.09, run_time=VUELO,
            ))
            actual = destino
            if ciclo < CICLOS - 1:
                partes.append(Wait(run_time=espera))
        secuencias.append(Succession(*partes))

    _impulso(scene, figura)
    scene.play(*secuencias)
    # Las estelas se apagan solas; darles ese medio segundo evita el corte seco.
    scene.wait(0.5)
    scene.remove(*rastros)
    scene.next_slide()

    # --- ¿Y dónde ha quedado lo aprendido? ---------------------------------
    # Se escanea la cabeza y una ventana de aumento se abre al lado —no encima,
    # que taparía media figura— con lo que hay dentro: neuronas. Ni una palabra:
    # es el puente a la parte biológica.
    centro_zoom = np.array([3.6, 0.85, 0.0])
    radio_zoom = 1.55
    cabeza = _escalar([X_FIG, Y_SUELO + 2.36, 0.0])

    radio_cabeza = 0.3 * ESCALA
    haz = _haz(cabeza, radio_cabeza, centro_zoom, radio_zoom)
    panel = _panel_zoom(centro_zoom, radio_zoom)
    malla, somas, conexiones = _tejido(centro_zoom, radio_zoom)

    # Primero se escanea la cabeza: encuadre, dos pasadas de la línea y un
    # destello. De ahí sale el haz que abre la ventana.
    mira = _mira(cabeza, radio_cabeza * 1.55)
    barra, colocar_barra = _barrido(cabeza, radio_cabeza)

    scene.play(FadeOut(VGroup(*bolas)), run_time=0.4)
    scene.play(LaggedStart(*[Create(e) for e in mira], lag_ratio=0.08),
               run_time=0.7)
    scene.add(barra)
    for duracion in (1.1, 0.8):
        scene.play(
            UpdateFromAlphaFunc(barra, colocar_barra, rate_func=there_and_back),
            run_time=duracion,
        )
    scene.play(
        Flash(cabeza, color=PRIMARIO, line_length=0.25, num_lines=16,
              flash_radius=radio_cabeza + 0.3),
        FadeOut(barra), run_time=0.6,
    )

    scene.play(FadeIn(haz), FadeIn(panel, scale=0.6), run_time=0.8)
    # Lo que hay dentro: la maraña primero y encima los cuerpos, uno a uno.
    scene.play(FadeIn(malla, scale=0.82), run_time=0.9)
    scene.play(
        LaggedStart(*[FadeIn(s, scale=0.4) for s in somas], lag_ratio=0.04),
        run_time=1.4,
    )

    # La red se enciende: impulsos sueltos recorriendo la maraña.
    rng = np.random.default_rng(5)
    for ronda in range(2):
        elegidas = rng.choice(len(conexiones), size=9, replace=False)
        impulsos = [
            Dot(color=CLARO, radius=0.06).move_to(conexiones[k].get_start())
            for k in elegidas
        ]
        scene.play(
            LaggedStart(*[
                MoveAlongPath(punto, conexiones[k], rate_func=linear)
                for punto, k in zip(impulsos, elegidas)
            ], lag_ratio=0.25),
            run_time=1.5,
        )
        scene.play(*[FadeOut(p, scale=0.1) for p in impulsos], run_time=0.3)
    scene.wait(0.4)

    scene.next_slide()
