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

from animaciones import impulsos_al_azar
from componentes import pares_cercanos, puntos_separados
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, FONDO, MORADO, PRIMARIO, SECUNDARIO, VERDE

X_FIG = 0.0
Y_SUELO = -2.5
ESCALA = 1.32
ALTO_MANO = 1.5
SEP_MANO = 1.0
RADIO_BOLA = 0.16
CIMA = 2.15
CIMA_CASCADA = 1.05

VUELO = 0.8
INTERVALO = 0.42
CICLOS = 4

DESVIOS = (2.1, 1.15, 0.5)

Y_MARCAS = -3.35
PASO_MARCAS = 0.46

ANCLA = np.array([X_FIG, Y_SUELO, 0.0])


def _escalar(punto):
    return ANCLA + (np.array(punto) - ANCLA) * ESCALA


def _mano(signo):
    return _escalar([X_FIG + signo * SEP_MANO, Y_SUELO + ALTO_MANO, 0.0])


def _curva(puntos, color=CLARO, grosor=5):
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly([np.array(p) for p in puntos])
    curva.cap_style = CapStyleType.ROUND
    return curva


def _figura():
    cadera = np.array([X_FIG, Y_SUELO + 1.05, 0.0])
    hombros = np.array([X_FIG, Y_SUELO + 1.95, 0.0])

    cabeza = Circle(radius=0.3, color=CLARO, stroke_width=5)
    cabeza.move_to([X_FIG, Y_SUELO + 2.36, 0])
    cuello = Line(hombros, [X_FIG, Y_SUELO + 2.06, 0], color=CLARO, stroke_width=5)

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
    inicio, fin = np.array(inicio, dtype=float), np.array(fin, dtype=float)
    curvatura = 4 * (cima - (inicio[1] + fin[1]) / 2)

    def volar(mob, alfa):
        x = inicio[0] + (fin[0] - inicio[0]) * alfa
        y = (inicio[1] + (fin[1] - inicio[1]) * alfa
             + curvatura * alfa * (1 - alfa))
        mob.move_to([x, y, 0])

    return UpdateFromAlphaFunc(bola, volar, rate_func=linear, **kwargs)


def _rastro(bola, color):
    return TracedPath(
        bola.get_center, stroke_color=color, stroke_width=4,
        stroke_opacity=0.75, dissipating_time=0.5,
    )


def _panel_zoom(centro, radio):
    halo = VGroup(*[
        Circle(radius=radio + separacion, color=PRIMARIO, stroke_width=grosor)
        .set_stroke(opacity=opacidad).move_to(centro)
        for separacion, grosor, opacidad in ((0.19, 10, 0.09), (0.08, 6, 0.2))
    ])
    cristal = Circle(radius=radio, color=PRIMARIO, stroke_width=5)
    cristal.set_fill(FONDO, opacity=1.0).move_to(centro)
    return VGroup(halo, cristal)


def _mira(centro, radio):
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


def _al_azar_en_disco(rng, centro, radio):
    distancia = radio * np.sqrt(rng.random())
    angulo = rng.uniform(0, 2 * PI)
    return centro + np.array([distancia * np.cos(angulo),
                              distancia * np.sin(angulo), 0.0])


def _soma(rng, punto):
    halo = Circle(radius=0.13, color=PRIMARIO, stroke_width=0)
    halo.set_fill(PRIMARIO, opacity=0.13).move_to(punto)
    muñones = VGroup(*[
        Line(punto, punto + np.array([np.cos(a) * 0.17, np.sin(a) * 0.17, 0]),
             color=PRIMARIO, stroke_width=2).set_stroke(opacity=0.55)
        for a in rng.uniform(0, 2 * PI, 3)
    ])
    return VGroup(halo, muñones, Dot(punto, radius=0.055, color=PRIMARIO))


def _tejido(centro, radio, cantidad=26, semilla=11):
    rng = np.random.default_rng(semilla)
    puntos = puntos_separados(
        lambda: _al_azar_en_disco(rng, centro, radio - 0.4),
        cantidad, separacion=0.33, intentos=6000,
    )

    conexiones = []
    for uno, otro in pares_cercanos(puntos, 0.72):
        medio = (uno + otro) / 2 + rng.uniform(-0.06, 0.06, 3) * [1, 1, 0]
        hilo = _curva([uno, medio, otro], color=PRIMARIO, grosor=1.6)
        conexiones.append(hilo.set_stroke(opacity=0.4))

    somas = VGroup(*[_soma(rng, punto) for punto in puntos])
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
    total = len(DESVIOS) + 1
    return [X_FIG + (indice - (total - 1) / 2) * PASO_MARCAS, Y_MARCAS, 0]


def _impulso(scene, figura):
    scene.play(figura.animate.shift(DOWN * 0.09), run_time=0.3,
               rate_func=there_and_back)


def _fallar(scene, figura, bola, diana):
    for intento, desvio in enumerate(DESVIOS):
        rastro = _rastro(bola, PRIMARIO)
        scene.add(rastro)

        caida = np.array([_mano(-1)[0] - desvio, Y_SUELO + RADIO_BOLA, 0.0])
        _impulso(scene, figura)
        scene.play(_lanzamiento(bola, _mano(1), caida), run_time=0.95)
        scene.play(bola.animate.shift(UP * 0.2), run_time=0.28,
                   rate_func=there_and_back)
        scene.remove(rastro)

        error = DashedLine(
            [caida[0], Y_SUELO + 0.08, 0], [_mano(-1)[0], Y_SUELO + 0.08, 0],
            color=AMBAR, stroke_width=3.5, dash_length=0.11,
        )
        cruz = _cruz().move_to(_sitio_marca(intento))
        scene.play(Create(error), FadeIn(cruz),
                   Indicate(diana, color=AMBAR, scale_factor=1.3), run_time=0.5)
        scene.next_slide()

        scene.play(
            _lanzamiento(bola, caida, _mano(1), Y_SUELO + 1.15),
            FadeOut(error), run_time=0.6,
        )


def _acertar(scene, figura, bola, diana, guia):
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


def _cascada(indice, bola, hueco, signo):
    partes = [] if indice == 0 else [Wait(run_time=indice * INTERVALO)]
    actual = hueco
    espera = 3 * INTERVALO - VUELO
    for ciclo in range(CICLOS):
        signo *= -1
        destino = _mano(signo) + np.array([(indice - 1) * 0.15, 0.07 - indice * 0.05, 0])
        partes.append(_lanzamiento(
            bola, actual, destino, CIMA_CASCADA + indice * 0.09, run_time=VUELO,
        ))
        actual = destino
        if ciclo < CICLOS - 1:
            partes.append(Wait(run_time=espera))
    return Succession(*partes)


def _malabares(scene, figura, bola):
    otras = VGroup(
        _bola(AMBAR, _mano(1) + np.array([0.19, -0.03, 0])),
        _bola(MORADO, _mano(-1) + np.array([-0.17, 0.03, 0])),
    )
    scene.play(GrowFromCenter(otras), run_time=0.5)

    bolas = [bola, otras[0], otras[1]]
    colores = (PRIMARIO, AMBAR, MORADO)
    rastros = [_rastro(b, c) for b, c in zip(bolas, colores)]
    scene.add(*rastros)

    huecos = [_mano(-1), _mano(1) + np.array([0.19, -0.03, 0]),
              _mano(-1) + np.array([-0.17, 0.03, 0])]
    signos = [-1, 1, -1]
    secuencias = [
        _cascada(i, b, hueco, signo)
        for i, (b, hueco, signo) in enumerate(zip(bolas, huecos, signos))
    ]

    _impulso(scene, figura)
    scene.play(*secuencias)
    scene.wait(0.5)
    scene.remove(*rastros)
    scene.next_slide()
    return bolas


def _mirar_dentro(scene, bolas):
    centro_zoom = np.array([3.6, 0.85, 0.0])
    radio_zoom = 1.55
    cabeza = _escalar([X_FIG, Y_SUELO + 2.36, 0.0])

    radio_cabeza = 0.3 * ESCALA
    haz = _haz(cabeza, radio_cabeza, centro_zoom, radio_zoom)
    panel = _panel_zoom(centro_zoom, radio_zoom)
    malla, somas, conexiones = _tejido(centro_zoom, radio_zoom)

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
    scene.play(FadeIn(malla, scale=0.82), run_time=0.9)
    scene.play(
        LaggedStart(*[FadeIn(s, scale=0.4) for s in somas], lag_ratio=0.04),
        run_time=1.4,
    )
    impulsos_al_azar(scene, conexiones, semilla=5, cantidad=9, lag_ratio=0.25,
                     run_time=1.5)
    scene.wait(0.4)

    scene.next_slide()


def construir(scene):
    encabezado = hacer_titulo("¿Cómo aprendemos nosotros?")

    figura = _figura()
    suelo = Line(
        [X_FIG - 5.2, Y_SUELO, 0], [X_FIG + 5.2, Y_SUELO, 0],
        color=SECUNDARIO, stroke_width=2, stroke_opacity=0.4,
    )
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

    _fallar(scene, figura, bola, diana)
    _acertar(scene, figura, bola, diana, guia)
    bolas = _malabares(scene, figura, bola)
    _mirar_dentro(scene, bolas)
