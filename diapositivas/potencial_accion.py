"""Diapositiva 10 — El potencial de acción, de la célula a la curva.

Unifica lo que antes eran tres diapositivas sueltas (polarización, canales y
umbral) en un solo cuadro, como el de una clase de fisiología. Es larga a
propósito: aquí se juntan las tres ideas y conviene verlas encajar.

  * Arriba, la célula entera, sin rótulos: aquí no toca nombrar sus partes,
    ya se hizo en su diapositiva.
  * Abajo a la izquierda, el zoom de la membrana de una dendrita: la bicapa,
    las cargas separadas y los dos canales.
  * A la derecha, el voltaje en el tiempo, con la línea de reposo y la del
    umbral.

Primero un estímulo que se queda corto —y que se borra antes de seguir, para no
ensuciar la gráfica—. Después el que cruza el umbral, contado en sus dos partes:
entra sodio y el voltaje sube hasta el pico; desde ahí sale potasio y el voltaje
vuelve a bajar. Las dos fases se cuentan de viva voz: en pantalla se ven los
iones cruzando y la curva, sin rótulos encima. Todo o nada, que es la no linealidad que le
falta al perceptrón.

Detalles de dibujo: las trazas se construyen con ``set_points_smoothly`` —una
poligonal deja el pico y las esquinas angulosos— y llevan un resplandor detrás.
El ``Axes`` se usa solo para mapear coordenadas (``c2p``); nunca se añade a la
escena, porque dibujaría su eje horizontal en y = 0, en mitad de la gráfica.
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
    Flash,
    Indicate,
    LaggedStart,
    MoveAlongPath,
    RoundedRectangle,
    VGroup,
    VMobject,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, MORADO, PRIMARIO, SECUNDARIO, VERDE

from . import _membrana
# La célula es la misma que se dibujó en la diapositiva de la neurona biológica:
# si aquí se dibujara otra, el público no reconocería el sitio.
from .neurona_biologica import _neurona as _celula

# --- Arriba: la célula -----------------------------------------------------
ESCALA_CELULA = 0.52
CENTRO_CELULA = [-3.55, 2.15, 0]
RADIO_MIRA = 0.32
DENDRITA_MIRA = 1        # de qué tronco dendrítico sale el zoom
# Casi en la punta del tronco: a media dendrita el círculo todavía pilla el
# soma y parece que el zoom es del cuerpo celular.
PROPORCION_MIRA = 1.0

# --- Abajo a la izquierda: la membrana ampliada ----------------------------
Y_MEMBRANA = -1.15
X_PANEL = (-6.45, -0.75)
ALTO_PANEL = 3.3
RADIO_ION = 0.2
APERTURA_CANAL = 0.24   # lo justo para que quepa un ion por el hueco
X_CANAL_NA = -4.9
X_CANAL_K = -2.3
Y_FUERA = Y_MEMBRANA + 0.95
Y_DENTRO = Y_MEMBRANA - 0.95

# --- A la derecha: el voltaje en el tiempo ---------------------------------
REPOSO = -70
UMBRAL = -55
PICO = 40
T_MAX = 9.5
V_MIN, V_MAX = -95, 55
CENTRO_GRAFICA = [3.6, 0.15, 0]

TRAZA_DEBIL = (
    (0.0, REPOSO), (1.4, REPOSO), (2.1, -66), (2.7, -61), (3.2, -60.5),
    (3.8, -63), (4.6, -67), (5.6, -69.5), (7.0, REPOSO), (T_MAX, REPOSO),
)
# El potencial de acción tiene dos partes y se cuentan por separado: la subida
# es sodio entrando; la bajada es potasio saliendo.
T_PICO = 4.05
SUBIDA = (
    (0.0, REPOSO), (1.4, REPOSO), (2.1, -66), (2.6, -58), (2.9, UMBRAL),
    (3.2, -34), (3.5, 6), (3.8, 32), (T_PICO, PICO),
)
BAJADA = (
    (T_PICO, PICO), (4.3, 29), (4.6, -6), (5.0, -38), (5.4, -62),
    (5.9, -78), (6.5, -82), (7.4, -77), (8.4, -71.5), (T_MAX, REPOSO),
)


def _iones(carga, color, x_canal, y, desplazamientos):
    """Grupo de iones esperando su turno a un lado del canal.

    Solo llevan su signo dentro: quién es cada uno ya lo dice el color y el
    rótulo de su canal, y con "Na"/"K" escritos la bolita se ensucia.
    """
    return VGroup(*[
        _membrana.ion(carga, [x_canal + dx, y + dy, 0], color,
                      radio=RADIO_ION, tam=17)
        for dx, dy in desplazamientos
    ])


def _tren(camino, simbolo, color, cantidad=4):
    """Fila de símbolos lista para recorrer el axón."""
    return [
        _membrana.ion(simbolo, camino.get_start(), color, radio=0.15, tam=15)
        for _ in range(cantidad)
    ]


def _recorrer(scene, camino, simbolo, color, run_time=1.3):
    """Manda esa fila axón abajo, escalonada, y la apaga al llegar."""
    tren = _tren(camino, simbolo, color)
    scene.add(*tren)
    scene.play(
        LaggedStart(*[MoveAlongPath(t, camino) for t in tren], lag_ratio=0.22),
        run_time=run_time, rate_func=linear,
    )
    scene.play(*[FadeOut(t, scale=0.2) for t in tren], run_time=0.35)


def _abrir(canal, cantidad):
    """Abre o cierra un canal separando sus dos mitades.

    Rehacerlo con ``become`` interpola entre dos formas distintas y el gesto
    sale seco; deslizar las mitades es lo que hace de verdad una compuerta.
    """
    izquierda, derecha = canal
    return (izquierda.animate.shift(LEFT * cantidad),
            derecha.animate.shift(RIGHT * cantidad))


def _traza(ejes, puntos, color):
    """Curva de voltaje, suave y con resplandor.

    Devuelve ``(grupo, curva)``: la curva suelta es la que recorre el punto
    encendido que va marcando la punta mientras se dibuja.
    """
    curva = VMobject(color=color, stroke_width=4.5)
    curva.set_points_smoothly([ejes.c2p(t, v) for t, v in puntos])
    resplandor = curva.copy().set_stroke(width=14, opacity=0.15)
    return VGroup(resplandor, curva), curva


def _dibujar_traza(scene, grupo, curva, color, run_time):
    """Dibuja la traza con un punto encendido montado en la punta."""
    punta = Dot(color=color, radius=0.075).move_to(curva.get_start())
    scene.add(punta)
    scene.play(
        Create(grupo), MoveAlongPath(punta, curva),
        run_time=run_time, rate_func=linear,
    )
    scene.play(FadeOut(punta, scale=0.3), run_time=0.3)


def construir(scene):
    encabezado = hacer_titulo("El potencial de acción")

    # --- La célula y la dendrita por la que nos vamos a meter --------------
    celula, piezas = _celula()
    celula.scale(ESCALA_CELULA).move_to(CENTRO_CELULA)
    tronco = piezas["troncos"][DENDRITA_MIRA]
    punto_mira = tronco.point_from_proportion(PROPORCION_MIRA)
    mira = Circle(radius=RADIO_MIRA, color=PRIMARIO, stroke_width=3)
    mira.move_to(punto_mira)
    halo_mira = Circle(radius=RADIO_MIRA * 1.45, stroke_width=0)
    halo_mira.set_fill(PRIMARIO, opacity=0.12).move_to(punto_mira)

    # --- El zoom de esa membrana -------------------------------------------
    capa = _membrana.bicapa(
        y=Y_MEMBRANA, x_izq=X_PANEL[0], x_der=X_PANEL[1],
    )
    panel = RoundedRectangle(
        width=X_PANEL[1] - X_PANEL[0] + 0.55, height=ALTO_PANEL, corner_radius=0.2,
        stroke_color=SECUNDARIO, stroke_width=2, fill_opacity=0,
    ).set_stroke(opacity=0.32)
    panel.move_to([(X_PANEL[0] + X_PANEL[1]) / 2, Y_MEMBRANA, 0])
    guias = VGroup(*[
        DashedLine(
            punto_mira + np.array([lado * RADIO_MIRA * 0.6, -RADIO_MIRA * 0.85, 0]),
            [panel.get_corner(esquina)[0], panel.get_top()[1], 0],
            color=SECUNDARIO, stroke_width=1.8, dash_length=0.1,
        ).set_stroke(opacity=0.35)
        for lado, esquina in ((-1, LEFT + UP), (1, RIGHT + UP))
    ])

    canal_na = _membrana.canal(X_CANAL_NA, AMBAR, y=Y_MEMBRANA)
    canal_k = _membrana.canal(X_CANAL_K, VERDE, y=Y_MEMBRANA)
    rot_na = texto("Na⁺", 17, color=AMBAR)
    rot_na.move_to([X_CANAL_NA, Y_MEMBRANA + 0.82, 0])
    rot_k = texto("K⁺", 17, color=VERDE)
    rot_k.move_to([X_CANAL_K, Y_MEMBRANA - 0.82, 0])

    positivos = VGroup(*[
        _membrana.ion("+", [x, Y_FUERA + 0.32, 0], MORADO, radio=0.13)
        for x in (-6.15, -3.55, -1.1)
    ])
    negativos = VGroup(*[
        _membrana.ion("−", [x, Y_DENTRO - 0.32, 0], PRIMARIO, radio=0.13)
        for x in (-6.2, -3.45, -1.0)
    ])
    sodio = _iones("+", AMBAR, X_CANAL_NA, Y_FUERA,
                   ((-0.66, 0.06), (0.0, 0.38), (0.66, 0.02)))
    potasio = _iones("+", VERDE, X_CANAL_K, Y_DENTRO,
                     ((-0.64, -0.04), (0.0, -0.36), (0.64, 0.0)))

    # --- La gráfica ---------------------------------------------------------
    ejes = Axes(
        x_range=[0, T_MAX, 1], y_range=[V_MIN, V_MAX, 25],
        x_length=6.0, y_length=4.6,
    ).move_to(CENTRO_GRAFICA)

    eje_v = Arrow(
        ejes.c2p(0, V_MIN), ejes.c2p(0, V_MAX + 4),
        color=SECUNDARIO, stroke_width=2.5, buff=0,
        max_tip_length_to_length_ratio=0.05,
    )
    eje_t = Arrow(
        ejes.c2p(0, V_MIN), ejes.c2p(T_MAX + 0.2, V_MIN),
        color=SECUNDARIO, stroke_width=2.5, buff=0,
        max_tip_length_to_length_ratio=0.04,
    )
    rot_v = texto("mV", 15, color=SECUNDARIO)
    rot_v.next_to(ejes.c2p(0, V_MAX), LEFT, buff=0.16)
    rot_t = texto("tiempo", 15, color=SECUNDARIO)
    rot_t.next_to(ejes.c2p(T_MAX - 0.9, V_MIN), DOWN, buff=0.2)

    linea_reposo = DashedLine(
        ejes.c2p(0, REPOSO), ejes.c2p(T_MAX, REPOSO),
        color=SECUNDARIO, stroke_width=2, dash_length=0.1,
    ).set_stroke(opacity=0.5)
    rot_reposo = texto("reposo −70", 15, color=SECUNDARIO)
    rot_reposo.move_to(ejes.c2p(7.4, REPOSO - 18))

    linea_umbral = DashedLine(
        ejes.c2p(0, UMBRAL), ejes.c2p(T_MAX, UMBRAL),
        color=PRIMARIO, stroke_width=2.5, dash_length=0.12,
    )
    rot_umbral = texto("umbral −55", 16, color=PRIMARIO)
    rot_umbral.move_to(ejes.c2p(1.5, UMBRAL + 9))

    grupo_debil, curva_debil = _traza(ejes, TRAZA_DEBIL, AMBAR)
    grupo_subida, curva_subida = _traza(ejes, SUBIDA, AMBAR)
    grupo_bajada, curva_bajada = _traza(ejes, BAJADA, VERDE)

    # ---------------------- Animación --------------------------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(celula), run_time=1.3)
    scene.play(FadeIn(halo_mira), Create(mira), run_time=0.6)
    scene.play(Indicate(mira, color=PRIMARIO, scale_factor=1.25), run_time=0.5)
    scene.next_slide()

    # --- Ahí dentro: la membrana en reposo ---------------------------------
    scene.play(Create(guias), FadeIn(panel), run_time=0.6)
    scene.play(
        LaggedStart(*[Create(p) for p in capa], lag_ratio=0.01), run_time=1.1,
    )

    # La polarización no aparece de golpe: las cargas llegan de fuera del panel,
    # se colocan a cada lado y después las recorre una onda. Así se ve que lo
    # que hay en reposo es una separación de cargas, no unos adornos.
    scene.play(
        LaggedStart(*[FadeIn(i, shift=DOWN * 0.8) for i in positivos],
                    lag_ratio=0.18),
        LaggedStart(*[FadeIn(i, shift=UP * 0.8) for i in negativos],
                    lag_ratio=0.18),
        run_time=1.3,
    )
    scene.play(
        LaggedStart(*[Indicate(i, color=CLARO, scale_factor=1.35)
                      for i in (*positivos, *negativos)], lag_ratio=0.08),
        run_time=1.0,
    )

    # Esa separación es el reposo: la gráfica arranca ahí.
    scene.play(Create(eje_v), Create(eje_t), FadeIn(rot_v), FadeIn(rot_t),
               run_time=0.9)
    scene.play(Create(linea_reposo), FadeIn(rot_reposo), run_time=0.6)
    scene.next_slide()

    # --- Las puertas ------------------------------------------------------
    scene.play(
        FadeIn(canal_na), FadeIn(canal_k), FadeIn(rot_na), FadeIn(rot_k),
        run_time=0.7,
    )
    scene.play(
        LaggedStart(*[FadeIn(i, shift=DOWN * 0.12) for i in sodio],
                    lag_ratio=0.15),
        LaggedStart(*[FadeIn(i, shift=UP * 0.12) for i in potasio],
                    lag_ratio=0.15),
        run_time=0.8,
    )
    scene.play(Create(linea_umbral), FadeIn(rot_umbral), run_time=0.7)
    scene.next_slide()

    # --- Primer intento: se queda corto ------------------------------------
    pulso = Dot(color=VERDE, radius=0.06).move_to(tronco.get_end())
    scene.add(pulso)
    scene.play(MoveAlongPath(pulso, tronco.copy().reverse_points()),
               run_time=0.5, rate_func=linear)
    scene.play(FadeOut(pulso, scale=0.2),
               Indicate(mira, color=AMBAR, scale_factor=1.2), run_time=0.4)
    scene.play(
        *_abrir(canal_na, APERTURA_CANAL * 0.45),
        Indicate(rot_na, color=CLARO, scale_factor=1.15),
        sodio[1].animate.move_to([X_CANAL_NA, Y_DENTRO + 0.3, 0]),
        run_time=0.7,
    )
    _dibujar_traza(scene, grupo_debil, curva_debil, AMBAR, 1.8)
    scene.play(
        *_abrir(canal_na, -APERTURA_CANAL * 0.45),
        sodio[1].animate.move_to([X_CANAL_NA, Y_FUERA + 0.38, 0]),
        run_time=0.9,
    )
    scene.next_slide()

    # El intento fallido se borra: la gráfica queda limpia para el que sí va.
    scene.play(FadeOut(grupo_debil), run_time=0.7)

    # --- Segundo intento, parte 1: entra sodio y sube hasta el pico --------
    pulsos = [
        Dot(color=VERDE, radius=0.07).move_to(t.get_end())
        for t in piezas["troncos"]
    ]
    caminos = [t.copy().reverse_points() for t in piezas["troncos"]]
    scene.add(*pulsos)
    scene.play(
        *[MoveAlongPath(p, c) for p, c in zip(pulsos, caminos)],
        run_time=0.5, rate_func=linear,
    )
    scene.play(
        *[FadeOut(p, scale=0.2) for p in pulsos],
        Indicate(mira, color=VERDE, scale_factor=1.35), run_time=0.4,
    )
    scene.play(
        *_abrir(canal_na, APERTURA_CANAL),
        Indicate(rot_na, color=CLARO, scale_factor=1.2),
        LaggedStart(*[
            i.animate.move_to([X_CANAL_NA + dx, Y_DENTRO + dy, 0])
            for i, (dx, dy) in zip(sodio, ((-0.72, -0.06), (0.05, -0.36), (0.78, 0.02)))
        ], lag_ratio=0.2),
        run_time=1.3,
    )
    _dibujar_traza(scene, grupo_subida, curva_subida, AMBAR, 1.7)
    scene.play(
        Flash(ejes.c2p(T_PICO, PICO), color=CLARO, line_length=0.3,
              num_lines=16, flash_radius=0.42),
        run_time=0.6,
    )

    # En el pico la neurona ya ha disparado: lo que viaja axón abajo es carga
    # positiva, así que se ve como una fila de "+".
    _recorrer(scene, piezas["linea_axon"], "+", AMBAR)
    scene.play(
        *[Flash(b, color=AMBAR, line_length=0.12, num_lines=10,
                flash_radius=0.18) for b in piezas["puntas"]],
        run_time=0.5,
    )
    scene.next_slide()

    # --- Parte 2: gastando ATP sale el potasio y vuelve abajo --------------
    scene.play(
        *_abrir(canal_na, -APERTURA_CANAL),
        run_time=0.7,
    )
    scene.play(
        *_abrir(canal_k, APERTURA_CANAL),
        Indicate(rot_k, color=CLARO, scale_factor=1.2),
        LaggedStart(*[
            i.animate.move_to([X_CANAL_K + dx, Y_FUERA + dy, 0])
            for i, (dx, dy) in zip(potasio, ((-0.72, 0.06), (0.05, 0.36), (0.78, -0.02)))
        ], lag_ratio=0.2),
        run_time=1.4,
    )
    _dibujar_traza(scene, grupo_bajada, curva_bajada, VERDE, 1.9)
    scene.play(
        *_abrir(canal_k, -APERTURA_CANAL),
        Indicate(VGroup(linea_reposo, rot_reposo), color=CLARO),
        run_time=0.9,
    )
    scene.wait(0.3)

    scene.next_slide()
