"""Diapositiva 4 — La neurona biológica.

Se dibuja una neurona vectorial y se nombran sus tres partes, cada una con su
color: dendritas (verde, entradas), soma (cian, integra) y axón (ámbar, salida).
Después una señal recorre la célula en ese orden, que es lo que fija la
dirección de la información — el guion original la tenía invertida. Y al final
la cámara se aleja: la célula se encoge hasta ser un punto de un campo entero
que se enciende, que es como se ve "miles de millones, conectadas en red" sin
tener que escribirlo.

Los colores no son decorativos: la diapositiva 5 reutiliza el mismo código de
color sobre el perceptrón para que la analogía se lea sola.

Se dibuja en Manim en lugar de usar ``assets/neurona_partes.jpg`` porque esa
imagen tiene fondo blanco y rótulos negros, ilegibles sobre el fondo oscuro.
"""

import numpy as np
from manim import (
    BOLD,
    DOWN,
    RIGHT,
    TAU,
    UP,
    CapStyleType,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    MoveAlongPath,
    VGroup,
    VMobject,
    linear,
)

from componentes import texto
from componentes import titulo as hacer_titulo
from estilo import AMBAR, CLARO, PRIMARIO, SECUNDARIO, VERDE

X_SOMA = -3.0
Y_NEURONA = 0.0
RADIO_SOMA = 0.68
LARGO_DENDRITA = 1.0
LARGO_AXON = 6.4
ANGULOS_DENDRITA = (2.75, 3.03, 3.31, 3.59)  # ~157° a ~206°: apuntan a la izquierda


def _u(angulo):
    """Vector unitario en el plano para un ángulo en radianes."""
    return np.array([np.cos(angulo), np.sin(angulo), 0.0])


def _curva(puntos, grosor, color=SECUNDARIO):
    """Trazo suave con las puntas redondeadas: nada de esquinas de palillo."""
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly([np.array(p) for p in puntos])
    curva.cap_style = CapStyleType.ROUND
    return curva


def _tramo(camino, desde, hasta, grosor, color=SECUNDARIO):
    """Trozo de un camino ya existente, para envainar el axón siguiéndolo."""
    tramo = VMobject(color=color, stroke_width=grosor)
    tramo.pointwise_become_partial(camino, desde, hasta)
    tramo.cap_style = CapStyleType.ROUND
    return tramo


def _ramificar(rng, origen, angulo, largo, profundidad, grosor):
    """Rama dendrítica recursiva: curvada, más fina en cada bifurcación."""
    giro = rng.uniform(-0.3, 0.3)
    fin = origen + largo * _u(angulo + giro)
    medio = origen + largo * 0.55 * _u(angulo + giro * 0.3)
    grupo = VGroup(_curva([origen, medio, fin], grosor))
    if profundidad > 0:
        for lado in (-1, 1):
            grupo.add(_ramificar(
                rng, fin, angulo + giro + lado * rng.uniform(0.34, 0.6),
                largo * rng.uniform(0.55, 0.7), profundidad - 1, grosor * 0.7,
            ))
    return grupo


def _neurona(largo_axon=LARGO_AXON, semilla=5):
    """Neurona completa. Devuelve el grupo y las piezas que la animación usa."""
    centro = np.array([X_SOMA, Y_NEURONA, 0.0])
    rng = np.random.default_rng(semilla)

    # --- Soma: blob orgánico con relleno tenue y un resplandor detrás ------
    contorno = [
        centro + RADIO_SOMA * rng.uniform(0.93, 1.09) * _u(a)
        for a in np.linspace(0, TAU, 14, endpoint=False)
    ]
    blob = VMobject(color=SECUNDARIO, stroke_width=6)
    blob.set_points_smoothly([*contorno, contorno[0]])
    blob.set_fill(SECUNDARIO, opacity=0.14)
    resplandor = Circle(radius=RADIO_SOMA * 1.5, stroke_width=0)
    resplandor.set_fill(SECUNDARIO, opacity=0.06).move_to(centro)
    soma = VGroup(resplandor, blob)
    nucleo = VGroup(
        Circle(radius=0.34, stroke_width=0)
        .set_fill(SECUNDARIO, opacity=0.2).move_to(centro),
        Dot(centro, radius=0.18, color=SECUNDARIO, fill_opacity=0.9),
    )

    # --- Dendritas: los troncos se guardan aparte, son el camino del pulso -
    # Arrancan un poco dentro del soma para que no se vea la costura.
    troncos = VGroup()
    dendritas = VGroup()
    for angulo in ANGULOS_DENDRITA:
        inicio = centro + RADIO_SOMA * 0.85 * _u(angulo)
        fin = inicio + LARGO_DENDRITA * _u(angulo)
        medio = inicio + LARGO_DENDRITA * 0.55 * _u(angulo + 0.13)
        tronco = _curva([inicio, medio, fin], 6)
        troncos.add(tronco)
        dendritas.add(tronco)
        for lado in (-1, 1):
            dendritas.add(_ramificar(
                rng, fin, angulo + lado * 0.45, LARGO_DENDRITA * 0.66, 1, 4.2,
            ))

    # --- Axón: curva suave envainada en mielina ---------------------------
    inicio_axon = centro + RADIO_SOMA * 0.85 * RIGHT
    fin_axon = inicio_axon + RIGHT * largo_axon
    linea_axon = _curva([
        inicio_axon,
        inicio_axon + RIGHT * largo_axon * 0.32 + UP * 0.24,
        inicio_axon + RIGHT * largo_axon * 0.68 - UP * 0.2,
        fin_axon,
    ], 5)
    # Las vainas son trozos gruesos del propio axón, no cápsulas encima: así
    # siguen la curva y los huecos entre ellas leen como nódulos de Ranvier.
    mielina = VGroup(*[
        _tramo(linea_axon, arranque, arranque + 0.115, 16)
        for arranque in (0.16, 0.3, 0.44, 0.58, 0.72)
    ]).set_stroke(opacity=0.8)

    # --- Terminales ---------------------------------------------------------
    terminales = VGroup()
    puntas = VGroup()
    for giro in (-0.62, -0.21, 0.21, 0.62):
        punta = fin_axon + 0.85 * _u(giro)
        codo = fin_axon + 0.45 * _u(giro * 0.55)
        terminales.add(_curva([fin_axon, codo, punta], 4))
        boton = VGroup(
            Circle(radius=0.19, stroke_width=0)
            .set_fill(SECUNDARIO, opacity=0.18).move_to(punta),
            Dot(punta, radius=0.1, color=SECUNDARIO),
        )
        terminales.add(boton)
        puntas.add(boton)

    neurona = VGroup(dendritas, soma, nucleo, linea_axon, mielina, terminales)
    piezas = {
        "dendritas": dendritas,
        "troncos": troncos,
        "soma": soma,
        "nucleo": nucleo,
        "linea_axon": linea_axon,
        "mielina": mielina,
        "terminales": terminales,
        "puntas": puntas,
    }
    return neurona, piezas


def _celula_mini(rng, centro):
    """Neurona de lejos: núcleo con halo y unas ramas cortas alrededor."""
    radio = 0.075
    halo = Circle(radius=radio * 2.8, stroke_width=0)
    halo.set_fill(PRIMARIO, opacity=0.12).move_to(centro)
    ramas = VGroup(*[
        _curva([
            centro + _u(angulo) * radio,
            centro + _u(angulo + rng.uniform(-0.3, 0.3)) * (radio + 0.14),
            centro + _u(angulo + rng.uniform(-0.5, 0.5)) * (radio + 0.28),
        ], 2.2, PRIMARIO)
        for angulo in rng.uniform(0, TAU, 5)
    ]).set_stroke(opacity=0.7)
    return VGroup(halo, ramas, Dot(centro, radius=radio, color=PRIMARIO))


def _campo(cantidad=34, semilla=17):
    """Campo de neuronas repartidas por la pantalla, con la red que las une.

    Devuelve ``(celulas, hilos, conexiones)``. Las posiciones se sortean con
    rechazo para que ninguna se pegue a otra, y se dejan libres la franja del
    título y el borde del marco.
    """
    rng = np.random.default_rng(semilla)
    puntos = []
    for _ in range(8000):
        if len(puntos) == cantidad:
            break
        punto = np.array([rng.uniform(-6.1, 6.1), rng.uniform(-3.1, 2.05), 0.0])
        if all(np.linalg.norm(punto - otro) > 1.05 for otro in puntos):
            puntos.append(punto)

    conexiones = []
    for i, uno in enumerate(puntos):
        for otro in puntos[i + 1:]:
            if np.linalg.norm(uno - otro) < 2.1:
                medio = (uno + otro) / 2 + rng.uniform(-0.12, 0.12, 3) * [1, 1, 0]
                conexiones.append(_curva([uno, medio, otro], 1.6, SECUNDARIO))
    hilos = VGroup(*conexiones).set_stroke(opacity=0.3)
    celulas = VGroup(*[_celula_mini(rng, p) for p in puntos])
    return celulas, hilos, conexiones


def _etiqueta(nombre, color, posicion, ancla):
    """Rótulo con una línea guía discontinua hasta ``ancla``."""
    bloque = texto(nombre, 24, color=color, weight=BOLD).move_to(posicion)

    direccion = np.array(ancla) - bloque.get_center()
    direccion = direccion / np.linalg.norm(direccion)
    guia = DashedLine(
        bloque.get_boundary_point(direccion) + direccion * 0.12, ancla,
        color=color, stroke_width=2, stroke_opacity=0.5, dash_length=0.09,
    )
    return bloque, guia


def construir(scene):
    encabezado = hacer_titulo("La neurona biológica")
    neurona, piezas = _neurona()

    rotulo_dendritas, guia_dendritas = _etiqueta(
        "Dendritas", VERDE,
        [-5.0, 2.0, 0], [-4.5, 0.95, 0],
    )
    rotulo_soma, guia_soma = _etiqueta(
        "Soma", PRIMARIO,
        [-3.0, -1.7, 0], [X_SOMA, Y_NEURONA - RADIO_SOMA, 0],
    )
    rotulo_axon, guia_axon = _etiqueta(
        "Axón", AMBAR,
        [1.4, 1.9, 0], [1.4, Y_NEURONA + 0.16, 0],
    )
    rotulos = VGroup(
        rotulo_dendritas, guia_dendritas,
        rotulo_soma, guia_soma,
        rotulo_axon, guia_axon,
    )

    # ---------------------- Animación: se dibuja la célula ------------------
    scene.play(FadeIn(encabezado, shift=DOWN * 0.2), run_time=0.6)
    scene.play(Create(piezas["soma"]), FadeIn(piezas["nucleo"]), run_time=0.7)
    scene.play(
        LaggedStart(*[Create(r) for r in piezas["dendritas"]], lag_ratio=0.06),
        run_time=1.1,
    )
    scene.play(Create(piezas["linea_axon"]), run_time=0.7)
    scene.play(
        LaggedStart(*[GrowFromCenter(v) for v in piezas["mielina"]],
                    lag_ratio=0.15),
        run_time=0.6,
    )
    scene.play(Create(piezas["terminales"]), run_time=0.6)
    scene.next_slide()

    # --- Se nombran las partes, cada una con su color ----------------------
    scene.play(
        piezas["dendritas"].animate.set_color(VERDE),
        FadeIn(rotulo_dendritas), Create(guia_dendritas),
        run_time=0.7,
    )
    scene.next_slide()

    scene.play(
        piezas["soma"].animate.set_color(PRIMARIO),
        piezas["nucleo"].animate.set_color(PRIMARIO),
        FadeIn(rotulo_soma), Create(guia_soma),
        run_time=0.7,
    )
    scene.next_slide()

    scene.play(
        piezas["linea_axon"].animate.set_color(AMBAR),
        piezas["terminales"].animate.set_color(AMBAR),
        piezas["mielina"].animate.set_stroke(color=AMBAR),
        FadeIn(rotulo_axon), Create(guia_axon),
        run_time=0.7,
    )
    scene.next_slide()

    # --- La señal recorre la célula: dendritas → soma → axón ---------------
    pulsos = [
        Dot(color=VERDE, radius=0.07).move_to(t.get_end())
        for t in piezas["troncos"]
    ]
    caminos = [t.copy().reverse_points() for t in piezas["troncos"]]
    scene.add(*pulsos)
    scene.play(
        *[MoveAlongPath(p, c) for p, c in zip(pulsos, caminos)], run_time=0.9,
    )
    scene.play(
        Indicate(piezas["soma"], color=PRIMARIO, scale_factor=1.12),
        Flash(piezas["nucleo"], color=PRIMARIO, line_length=0.28,
              num_lines=14, flash_radius=0.75),
        *[FadeOut(p, scale=0.1) for p in pulsos],
        run_time=0.6,
    )

    pulso_salida = Dot(color=AMBAR, radius=0.07)
    pulso_salida.move_to(piezas["linea_axon"].get_start())
    scene.play(
        MoveAlongPath(pulso_salida, piezas["linea_axon"]),
        run_time=1.0, rate_func=linear,
    )
    scene.play(
        FadeOut(pulso_salida, scale=0.1),
        *[Flash(b, color=AMBAR, line_length=0.18, num_lines=10,
                flash_radius=0.28) for b in piezas["puntas"]],
        run_time=0.6,
    )
    scene.next_slide()

    # --- Y no está sola: la cámara se aleja --------------------------------
    # Sin rótulos ni cifras: la célula se encoge hasta ser un punto más de un
    # campo entero que se enciende. Eso ya dice "miles de millones, en red".
    celulas, hilos, conexiones = _campo()
    semilla_campo = celulas[0].get_center()

    scene.play(FadeOut(rotulos), run_time=0.4)
    scene.play(
        neurona.animate.scale(0.09).move_to(semilla_campo),
        run_time=1.2,
    )
    scene.play(
        FadeOut(neurona, scale=0.6),
        LaggedStart(*[FadeIn(c, scale=0.4) for c in celulas], lag_ratio=0.025),
        run_time=1.8,
    )
    scene.play(
        LaggedStart(*[Create(h) for h in hilos], lag_ratio=0.012),
        run_time=1.6,
    )

    # La red entera se enciende: impulsos sueltos saltando de célula a célula.
    rng = np.random.default_rng(9)
    for _ in range(2):
        elegidas = rng.choice(len(conexiones), size=12, replace=False)
        impulsos = [
            Dot(color=CLARO, radius=0.06).move_to(conexiones[k].get_start())
            for k in elegidas
        ]
        scene.play(
            LaggedStart(*[
                MoveAlongPath(punto, conexiones[k], rate_func=linear)
                for punto, k in zip(impulsos, elegidas)
            ], lag_ratio=0.2),
            run_time=1.7,
        )
        scene.play(*[FadeOut(p, scale=0.1) for p in impulsos], run_time=0.3)
    scene.wait(0.4)

    scene.next_slide()
