"""Diapositiva 29 — Cierre.

La última imagen de la charla es la charla entera. Arriba el agradecimiento;
en el centro **la red completa** —ya no el perceptrón suelto de la portada,
sino las cuatro capas a las que se llegó— disparando de izquierda a derecha
hasta desembocar en el QR; abajo, en cuatro papeles, las cuatro gráficas que
la sostuvieron, dibujándose solas: la recta, el umbral, el error y el
descenso. Y en el bucle no se quedan quietas: la recta barre buscando su
ajuste, la rampa de ReLU se empina, el modelo se corrige y cierra el hueco del
error, y la bola cruza el valle de ladera a ladera.

Cierra el círculo sin una sola frase que lo explique: lo que en la portada
era una neurona con tres entradas, aquí es una red que se enciende sola.

Y se queda viva. El último tramo va en bucle (``next_slide(loop=True)``):
una oleada cian hacia adelante —la predicción, que acaba latiendo en la
tarjeta del QR— y otra morada hacia atrás, encendiendo un ``-∇w`` sobre cada
haz de aristas a medida que el gradiente lo alcanza. Una y otra vez mientras
la gente escanea y pregunta: la red no se congela, respira.

Las oleadas son ``ShowPassingFlash`` sobre copias de las aristas, no puntos
viajando: con 78 conexiones, 78 ``Dot`` con su updater se leerían como ruido
y costarían un mundo; la luz recorriendo el cable se lee de un vistazo.

Press Start 2P no trae acentos ni signos de apertura —lo mismo le pasa al
título de la portada, que dice «COMO» y no «CÓMO»—, así que el agradecimiento
va en mayúsculas y sin ellos. El resto del texto es JetBrains Mono y sí los
lleva.
"""

import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    AnimationGroup,
    Arrow,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Group,
    GrowFromCenter,
    DEGREES,
    LaggedStart,
    Line,
    MathTex,
    MoveAlongPath,
    RoundedRectangle,
    ShowPassingFlash,
    Succession,
    VGroup,
    VMobject,
    there_and_back,
)

from componentes import imagen, texto
from estilo import (
    AMBAR,
    BLANCO,
    CLARO,
    FONT_TITULO,
    MORADO,
    PRIMARIO,
    SECUNDARIO,
    VERDE,
)

RELLENO_NODO = "#04121a"     # el mismo de la portada

# --- Cabecera --------------------------------------------------------------
# Una sola línea, a plena anchura. Sin subtítulo debajo: las capas de 6 nodos
# llegan a y=2.15 y encima se posan los ``-∇w``, así que esa banda está
# ocupada. Y un cierre no necesita explicar que se dan las gracias.
Y_GRACIAS = 3.18
TAM_GRACIAS = 48
ANCHO_MAX_GRACIAS = 10.4

# --- La red: cuatro capas que desembocan en el QR --------------------------
# Las capas ocupan la mitad izquierda y el QR la derecha; la fila entera
# vive en ``Y_RED``, con la capa más alta (6 nodos) justo a la altura del
# borde superior de la tarjeta.
Y_RED = 0.55
TAM_CAPAS = (4, 6, 6, 3)
X_CAPAS = (-6.05, -4.35, -2.65, -0.95)
COLOR_CAPAS = (PRIMARIO, SECUNDARIO, SECUNDARIO, AMBAR)
RADIO_NODO = 0.15
PASO_NODO = 0.58
OPACIDAD_ARISTA = 0.26       # la malla es tejido de fondo, no protagonista

X_JUNTA = 0.55               # donde las tres salidas se hacen una

# --- El QR -----------------------------------------------------------------
X_QR = 4.25
LADO_TARJETA = 2.9
MARGEN_QR = 0.3          # zona de silencio: sin ella los lectores fallan
Y_PIE_QR = -1.35

# --- La tira de repaso -----------------------------------------------------
# Cuatro papeles, un color por papel: cada uno es la gráfica de una
# diapositiva de hoy, en el color con el que se contó allí.
#
# Van sin rótulo a propósito. Acaban de verse una por una durante la charla,
# así que ponerles el nombre debajo es repetir lo que la silueta ya dice, y
# cuatro textos seguidos convierten la tira en una fila de botones. Sin ellos
# se lee como lo que es: cuatro dibujos, uno por idea.
Y_TIRA = -2.55
ANCHO_PAPEL, ALTO_PAPEL = 2.6, 1.30
BUFF_PAPEL = 0.32
A_DIBUJO, H_DIBUJO = 0.92, 0.33      # semiejes del boceto dentro del papel
T_BOLA = 0.22                        # dónde arranca la bola sobre el valle
T_REBOTE = 0.74                      # y hasta dónde sube por la ladera de enfrente
MARGEN_HUECO = 0.05                  # aire entre cada punto y el hueco del error

# Cuánto se mueve cada gráfica en el bucle. Generoso a propósito: en una
# tarjeta de 2.6 x 1.3 un gesto discreto no se ve desde la última fila.
GIRO_RECTA = 14 * DEGREES            # barrido de la recta buscando su ajuste
ESTIRON_UMBRAL = 1.3                 # cuánto se empina la rampa de ReLU
GIRO_ERROR = 8 * DEGREES             # cuánto se corrige el modelo

# --- El gradiente, que solo sale en la vuelta ------------------------------
ALTURA_GRADIENTE = 0.16      # aire entre la arista más alta del tramo y su rótulo

Y_FIRMA = -3.62


# --------------------------------------------------------------------------
# La red
# --------------------------------------------------------------------------
def _red():
    """Los nodos agrupados por capa y las aristas agrupadas por tramo.

    Devolver las aristas por tramo (y no todas juntas) es lo que permite
    después encender la red capa a capa: cada tramo es un fotograma de la
    oleada.
    """
    capas = []
    for x, n, color in zip(X_CAPAS, TAM_CAPAS, COLOR_CAPAS):
        alto = (n - 1) * PASO_NODO
        capa = []
        for k in range(n):
            centro = np.array([x, Y_RED + alto / 2 - k * PASO_NODO, 0.0])
            nodo = Circle(radius=RADIO_NODO, color=color, stroke_width=2.6)
            capa.append(nodo.set_fill(RELLENO_NODO, opacity=1.0).move_to(centro))
        capas.append(capa)

    tramos = []
    for izquierda, derecha in zip(capas, capas[1:]):
        tramo = VGroup()
        for a in izquierda:
            for b in derecha:
                paso = b.get_center() - a.get_center()
                paso = paso / np.linalg.norm(paso)
                tramo.add(Line(
                    a.get_center() + paso * RADIO_NODO,
                    b.get_center() - paso * RADIO_NODO,
                    color=SECUNDARIO, stroke_width=1.1,
                ).set_stroke(opacity=OPACIDAD_ARISTA))
        tramos.append(tramo)
    return capas, tramos


def _desemboque(salidas):
    """Las tres salidas convergiendo en un punto, y de ahí al QR.

    La junta es lo que convierte la red en un mensaje: tres respuestas que se
    hacen una y entran en la tarjeta.
    """
    junta_centro = np.array([X_JUNTA, Y_RED, 0.0])
    junta = Dot(junta_centro, radius=0.08, color=PRIMARIO)

    convergencias = VGroup()
    for nodo in salidas:
        paso = junta_centro - nodo.get_center()
        paso = paso / np.linalg.norm(paso)
        convergencias.add(Line(
            nodo.get_center() + paso * RADIO_NODO,
            junta_centro - paso * 0.08,
            color=AMBAR, stroke_width=2.0,
        ).set_stroke(opacity=0.7))

    borde_qr = X_QR - LADO_TARJETA / 2
    tramo_final = (junta_centro + RIGHT * 0.1,
                   np.array([borde_qr - 0.12, Y_RED, 0.0]))
    salida = Arrow(
        *tramo_final, color=PRIMARIO, stroke_width=4, buff=0.0,
        max_tip_length_to_length_ratio=0.11,
    )
    # Riel invisible con el recorrido de la flecha: el destello va por aquí,
    # porque ``ShowPassingFlash`` sobre una ``Arrow`` arrastra la punta.
    riel = Line(*tramo_final)
    return junta, convergencias, salida, riel


def _oleada(tramo, nodos, color, reverso=False):
    """Luz recorriendo un tramo de aristas y los nodos acusándola después."""
    rieles = [
        arista.copy().reverse_points() if reverso else arista.copy()
        for arista in tramo
    ]
    return AnimationGroup(
        AnimationGroup(*[
            ShowPassingFlash(
                riel.set_stroke(color, 3.5, 1.0), time_width=0.55,
            )
            for riel in rieles
        ]),
        AnimationGroup(*[
            nodo.animate(rate_func=there_and_back).set_stroke(color, 5.5)
            for nodo in nodos
        ]),
        lag_ratio=0.6,
    )


def _hacia_adelante(capas, tramos, junta, convergencias, riel, tarjeta):
    """La predicción: entra por la izquierda y sale latiendo en el QR."""
    pasos = [
        _oleada(tramo, capas[i + 1], PRIMARIO)
        for i, tramo in enumerate(tramos)
    ]
    pasos.append(AnimationGroup(
        AnimationGroup(*[
            ShowPassingFlash(c.copy().set_stroke(AMBAR, 3.5, 1.0),
                             time_width=0.55)
            for c in convergencias
        ]),
        junta.animate(rate_func=there_and_back).scale(1.7),
        lag_ratio=0.6,
    ))
    pasos.append(AnimationGroup(
        ShowPassingFlash(riel.copy().set_stroke(PRIMARIO, 5.0, 1.0),
                         time_width=0.4),
        tarjeta.animate(rate_func=there_and_back).scale(1.045),
        lag_ratio=0.55,
    ))
    return LaggedStart(*pasos, lag_ratio=0.42)


def _hacia_atras(capas, tramos):
    """El aprendizaje: el error volviendo por donde vino, en morado."""
    return LaggedStart(*[
        _oleada(tramo, capas[i], MORADO, reverso=True)
        for i, tramo in reversed(list(enumerate(tramos)))
    ], lag_ratio=0.42)


def _gradientes(tramos):
    """Un ``-∇w`` sobre cada tramo de aristas, para la oleada de vuelta.

    Sobre las aristas y no sobre las capas: el gradiente que se resta es el de
    los **pesos**, y los pesos son las conexiones, no los nodos. Puesto encima
    de un nodo diría otra cosa.

    Mismo símbolo y mismo morado que en la diapositiva de backpropagation:
    quien estuvo atento reconoce el paso de gradiente, no un adorno nuevo.
    Cada rótulo se posa sobre la arista más alta de su tramo —de ahí el
    escalonado—, así que sigue la silueta de la malla en vez de flotar en una
    fila recta que la ignora.
    """
    rotulos = VGroup()
    for tramo in tramos:
        cumbre = max((arista.get_center() for arista in tramo),
                     key=lambda punto: punto[1])
        rotulos.add(
            MathTex(r"-\nabla w", color=MORADO).scale(0.58)
            .next_to(cumbre, UP, buff=ALTURA_GRADIENTE)
        )
    return rotulos


# --------------------------------------------------------------------------
# La tira de repaso: las cuatro gráficas de la charla, en miniatura
# --------------------------------------------------------------------------
# Cada boceto devuelve sus piezas **en el orden en que se cuentan**, porque de
# ese orden sale la animación: ``_dibujarse`` las va soltando una a una, así
# que la lista es a la vez el dibujo y su guion. Primero lo que había, después
# lo que el modelo hace con ello.
def _boceto_recta():
    """La recta que atraviesa los puntos (la suma ponderada)."""
    puntos = []
    for k, desvio in enumerate((0.10, -0.12, 0.08, -0.09, 0.11)):
        t = -1 + 2 * k / 4
        puntos.append(Dot([t * A_DIBUJO, t * H_DIBUJO + desvio, 0],
                          radius=0.045, color=SECUNDARIO))
    recta = Line([-A_DIBUJO, -H_DIBUJO, 0], [A_DIBUJO, H_DIBUJO, 0],
                 color=PRIMARIO, stroke_width=2.8)
    return VGroup(*puntos, recta)   # los datos primero; la recta, después


def _boceto_umbral():
    """El codo de ReLU sobre su eje (el umbral)."""
    eje = Line([-A_DIBUJO, -H_DIBUJO, 0], [A_DIBUJO, -H_DIBUJO, 0],
               color=SECUNDARIO, stroke_width=1.2).set_stroke(opacity=0.5)
    codo = VMobject(color=VERDE, stroke_width=2.8)
    codo.set_points_as_corners([
        [-A_DIBUJO, -H_DIBUJO, 0], [-0.04, -H_DIBUJO, 0],
        [A_DIBUJO * 0.88, H_DIBUJO, 0],
    ])
    return VGroup(eje, codo)


def _hueco(objetivo, prediccion):
    """Las rayas entre los dos puntos del error.

    Una sola fábrica porque el boceto la dibuja una vez y el updater de
    ``_vive_error`` la rehace en cada fotograma: si las dos versiones no
    coinciden al milímetro, el primer fotograma del bucle da un saltito.
    """
    return DashedLine(
        objetivo + DOWN * MARGEN_HUECO, prediccion + UP * MARGEN_HUECO,
        color=AMBAR, stroke_width=2.4, dash_length=0.05,
    )


def _boceto_error():
    """El hueco entre lo que se quería y lo que salió."""
    izq = np.array([-A_DIBUJO, -H_DIBUJO * 0.6, 0])
    der = np.array([A_DIBUJO, H_DIBUJO * 0.9, 0])
    modelo = Line(izq, der, color=SECUNDARIO,
                  stroke_width=1.6).set_stroke(opacity=0.5)

    prediccion = modelo.point_from_proportion(0.6)
    objetivo = prediccion + UP * H_DIBUJO * 1.15
    # El modelo, lo que sacó, lo que se quería, y solo al final el hueco:
    # el error se ve nacer entre los dos puntos.
    return VGroup(
        modelo,
        Dot(prediccion, radius=0.06, color=AMBAR),
        Dot(objetivo, radius=0.06, color=VERDE),
        _hueco(objetivo, prediccion),
    )


def _bajada(valle):
    """El trozo de valle que recorre la bola: de ``T_BOLA`` a ``T_REBOTE``.

    Ojo con la parametrización, que aquí muerde: ``pointwise_become_partial``
    corta por **parámetro de bézier** y ``point_from_proportion`` mide por
    **longitud de arco**, y en una curva no caen en el mismo punto. Si la bola
    se coloca con una y el camino se recorta con la otra, ``MoveAlongPath`` la
    teletransporta al arrancar y la deja movida al acabar: el bucle da un
    salto visible en cada vuelta. Por eso el camino se calcula aquí, una sola
    vez, y la bola se planta en su arranque.
    """
    return valle.copy().pointwise_become_partial(valle, T_BOLA, T_REBOTE)


def _boceto_descenso():
    """El valle, y la bolita a mitad de bajada."""
    xs = np.linspace(-A_DIBUJO, A_DIBUJO, 40)
    valle = VMobject(color=SECUNDARIO, stroke_width=1.8)
    valle.set_points_smoothly([
        [x, -H_DIBUJO + 2 * H_DIBUJO * (x / A_DIBUJO) ** 2, 0] for x in xs
    ])
    valle.set_stroke(opacity=0.55)

    # En el arranque del camino de bajada, no en una posición calculada
    # aparte: ver :func:`_bajada`.
    bola = Dot(_bajada(valle).get_start(), radius=0.075, color=MORADO)
    rumbo = Arrow(
        bola.get_center() + np.array([0.12, -0.02, 0]),
        bola.get_center() + np.array([0.42, -0.20, 0]),
        color=MORADO, stroke_width=2.4, buff=0.0,
        max_tip_length_to_length_ratio=0.4,
    ).set_stroke(opacity=0.8)
    return VGroup(valle, bola, rumbo)   # el terreno, la bola, y hacia dónde


# --------------------------------------------------------------------------
# Y las cuatro, vivas: lo que hace cada gráfica cuando la tira entra en bucle
# --------------------------------------------------------------------------
# Todas van con ``there_and_back``, sin excepción: el bucle solo se cierra sin
# costura si cada figura acaba exactamente donde empezó. Cualquier animación
# que deje una pieza movida se nota como un salto en cada vuelta.
def _vive_recta(boceto):
    """La recta barriendo en busca de su ajuste, y los datos acusándolo.

    El barrido es amplio a propósito —no un temblor—: a este tamaño un giro
    pequeño no se lee, y lo que tiene que verse es una recta *buscando*. Los
    puntos van pulsando en cascada por debajo, así que la tarjeta no se queda
    en un solo gesto.
    """
    *puntos, recta = boceto
    return AnimationGroup(
        recta.animate(rate_func=there_and_back).rotate(
            GIRO_RECTA, about_point=recta.get_center()),
        LaggedStart(*[
            punto.animate(rate_func=there_and_back).scale(2.0)
            for punto in puntos
        ], lag_ratio=0.18),
    )


def _vive_umbral(boceto):
    """La señal sube por el codo y la rampa se empina con ella.

    El estirón va anclado al arranque del codo, que está a la altura del
    tramo plano: así la parte apagada no se mueve ni un pelo y solo crece la
    rampa, que es justo lo que hace un umbral cuando pesa más.

    Y va en ``Succession``, no en paralelo: ``ShowPassingFlash`` recorre una
    **copia** del codo tomada al construir la animación, así que si el codo se
    estira a la vez, el destello viaja por la geometría vieja y se ve el codo
    partido en dos. Primero llega la señal, después responde la rampa.
    """
    _, codo = boceto
    return Succession(
        ShowPassingFlash(
            codo.copy().set_stroke(VERDE, 5.0, 1.0), time_width=0.45),
        codo.animate(rate_func=there_and_back).stretch(
            ESTIRON_UMBRAL, dim=1, about_point=codo.get_start()),
    )


def _vive_error(boceto):
    """El modelo corrigiéndose: la recta sube y el hueco se cierra.

    No basta con subir el punto ámbar —eso lo despegaría de su recta—: gira
    el **modelo entero** sobre su extremo izquierdo y la predicción con él,
    con el mismo ángulo y el mismo pivote, así que el punto sigue clavado en
    la recta mientras el error encoge. Que es lo que de verdad pasa al
    entrenar: no se mueve la predicción, se mueve el modelo.

    El hueco no se anima, se **recalcula**: un updater lo rehace entre los dos
    puntos en cada fotograma. Animar la ``DashedLine`` por separado la
    descuadraría de los puntos a mitad de camino.
    """
    modelo, prediccion, objetivo, hueco = boceto
    hueco.add_updater(lambda m: m.become(
        _hueco(objetivo.get_center(), prediccion.get_center()),
    ))
    pivote = modelo.get_start()
    return AnimationGroup(
        modelo.animate(rate_func=there_and_back).rotate(
            GIRO_ERROR, about_point=pivote),
        prediccion.animate(rate_func=there_and_back).rotate(
            GIRO_ERROR, about_point=pivote),
        objetivo.animate(rate_func=there_and_back).scale(1.4),
    )


def _vive_descenso(boceto):
    """La bola cayendo al fondo y subiendo por la ladera de enfrente.

    Se pasa de largo a propósito: quedarse clavada en el fondo es un gesto
    que muere ahí, y el rebote es además lo que hace de verdad un descenso
    con paso grande.
    """
    valle, bola, rumbo = boceto
    return AnimationGroup(
        MoveAlongPath(bola, _bajada(valle), rate_func=there_and_back),
        # La flecha del rumbo se apaga mientras rueda: apuntaba desde el sitio
        # que la bola acaba de dejar, y quedarse sola la delata.
        rumbo.animate(rate_func=there_and_back).set_opacity(0.0),
    )


# (cómo se dibuja, cómo vive en el bucle)
REPASO = (
    (_boceto_recta, _vive_recta),
    (_boceto_umbral, _vive_umbral),
    (_boceto_error, _vive_error),
    (_boceto_descenso, _vive_descenso),
)


def _dibujarse(boceto, lag=0.3):
    """El boceto haciéndose solo, pieza a pieza y en el orden en que llegó.

    Los puntos brotan y las líneas se trazan: ``Create`` sobre un ``Dot``
    dibuja la circunferencia, que a este tamaño parece un fallo.
    """
    return LaggedStart(*[
        GrowFromCenter(pieza) if isinstance(pieza, Dot) else Create(pieza)
        for pieza in boceto
    ], lag_ratio=lag)


def _papel(dibujar):
    """Un papel de la tira: el boceto solo, centrado y sin rótulo."""
    fondo = RoundedRectangle(
        width=ANCHO_PAPEL, height=ALTO_PAPEL, corner_radius=0.14,
        stroke_color=SECUNDARIO, stroke_width=1.6,
    ).set_fill(CLARO, opacity=0.03)
    fondo.set_stroke(opacity=0.3)
    return VGroup(fondo, dibujar().move_to(fondo.get_center()))


# --------------------------------------------------------------------------
def construir(scene):
    # --- Cabecera ----------------------------------------------------------
    gracias = VGroup(
        texto("MUCHAS", TAM_GRACIAS, color=CLARO, font=FONT_TITULO),
        texto("GRACIAS", TAM_GRACIAS, color=PRIMARIO, font=FONT_TITULO),
    ).arrange(RIGHT, buff=0.5)
    if gracias.width > ANCHO_MAX_GRACIAS:
        gracias.scale(ANCHO_MAX_GRACIAS / gracias.width)
    gracias.move_to([0, Y_GRACIAS, 0])

    # --- La red y su desemboque --------------------------------------------
    capas, tramos = _red()

    # --- El QR, que hace de salida -----------------------------------------
    papel_qr = RoundedRectangle(
        width=LADO_TARJETA, height=LADO_TARJETA, corner_radius=0.2,
        stroke_color=PRIMARIO, stroke_width=3,
    ).set_fill(BLANCO, opacity=1.0).move_to([X_QR, Y_RED, 0])
    codigo = imagen("qr_links.png")
    codigo.scale_to_fit_width(LADO_TARJETA - MARGEN_QR * 2)
    codigo.move_to(papel_qr.get_center())
    tarjeta = Group(papel_qr, codigo)

    junta, convergencias, salida, riel = _desemboque(capas[-1])

    pie_qr = VGroup(
        texto("escanea el código", 15, color=CLARO),
        texto("diapositivas y recursos", 14, color=SECUNDARIO),
    ).arrange(DOWN, buff=0.12).move_to([X_QR, Y_PIE_QR, 0])

    # --- La tira de repaso y la firma ---------------------------------------
    tira = VGroup(*[_papel(dibujar) for dibujar, _ in REPASO])
    tira.arrange(RIGHT, buff=BUFF_PAPEL).move_to([0, Y_TIRA, 0])

    gradientes = _gradientes(tramos)

    firma = texto("Semillero de Data Science e IA  ·  Aperture", 15,
                  color=SECUNDARIO).move_to([0, Y_FIRMA, 0])

    # ---------------------- Animación --------------------------------------
    # La malla decorativa del fondo se va con la primera animación: es la única
    # diapositiva que trae su propia red, y las dos juntas se pelean —las
    # aristas largas del fondo cruzan la tira de repaso y ensucian todo.
    entrada = [FadeIn(gracias[0], shift=UP * 0.18)]
    if getattr(scene, "_fondo", None) is not None:
        entrada.append(FadeOut(scene._fondo))
        scene._fondo = None
    scene.play(*entrada, run_time=0.5)
    scene.play(FadeIn(gracias[1], shift=UP * 0.18), run_time=0.5)

    # La red se arma capa a capa, de la entrada a la salida: es el mismo
    # gesto de la portada, pero ahora con la red entera.
    scene.play(
        LaggedStart(*[
            AnimationGroup(*[GrowFromCenter(n) for n in capa])
            for capa in capas
        ], lag_ratio=0.35),
        run_time=1.0,
    )
    scene.play(
        LaggedStart(*[Create(t) for t in tramos], lag_ratio=0.35),
        run_time=1.1,
    )

    # Y el primer disparo desemboca en el QR, que aparece al recibirlo.
    scene.play(
        LaggedStart(*[
            _oleada(tramo, capas[i + 1], PRIMARIO)
            for i, tramo in enumerate(tramos)
        ], lag_ratio=0.42),
        run_time=1.6,
    )
    scene.play(
        LaggedStart(*[Create(c) for c in convergencias], lag_ratio=0.15),
        GrowFromCenter(junta), run_time=0.6,
    )
    scene.play(Create(salida), run_time=0.45)
    # La tarjeta primero y el código encima: encadenados, no en dos golpes.
    scene.play(
        LaggedStart(GrowFromCenter(papel_qr), FadeIn(codigo, scale=0.85),
                    lag_ratio=0.55),
        run_time=0.95,
    )
    scene.play(FadeIn(pie_qr, shift=UP * 0.1), run_time=0.4)

    # --- Lo que vimos hoy, en cuatro dibujos --------------------------------
    # Sin pausa antes de la tira: partir aquí congelaría media pantalla vacía,
    # que es justo lo que esta diapositiva venía a arreglar. El cierre se monta
    # de un tirón mientras se da las gracias, y la única pausa es la del bucle.
    # Cada papel entra y se dibuja solo antes de que empiece el siguiente:
    # así la tira se lee como cuatro gráficas haciéndose, no como cuatro
    # estampas apareciendo de golpe.
    scene.play(
        LaggedStart(*[
            Succession(FadeIn(fondo, shift=UP * 0.18), _dibujarse(boceto))
            for fondo, boceto in tira
        ], lag_ratio=0.42),
        run_time=2.8,
    )
    scene.play(FadeIn(firma, shift=UP * 0.1), run_time=0.4)

    # --- Y se queda viva ----------------------------------------------------
    # Sin indicador en la última pausa: no queda nada que anunciar, y su
    # animación de entrada caería dentro del bucle, parpadeando en cada vuelta.
    # Los ``-∇w`` entran y salen dentro del bucle, así que el tramo empieza y
    # acaba con la pantalla igual y la vuelta no da un salto.
    # Un rótulo por tramo y una oleada por tramo: se encienden en el mismo
    # orden en que el gradiente los alcanza, de la salida hacia la entrada.
    al_reves = list(gradientes)[::-1]
    scene.next_slide(loop=True)
    # Las cuatro gráficas se mueven con la oleada de ida, escalonadas de
    # izquierda a derecha: viven en su propia banda, así que no compiten con
    # la red, y el ojo puede recorrerlas mientras la señal cruza arriba.
    scene.play(
        _hacia_adelante(capas, tramos, junta, convergencias, riel, tarjeta),
        LaggedStart(*[
            vivir(papel[1]) for (_, vivir), papel in zip(REPASO, tira)
        ], lag_ratio=0.22),
        run_time=2.4,
    )
    scene.play(
        _hacia_atras(capas, tramos),
        LaggedStart(*[FadeIn(g, shift=DOWN * 0.14) for g in al_reves],
                    lag_ratio=0.45),
        run_time=1.8,
    )
    scene.play(
        LaggedStart(*[FadeOut(g, shift=UP * 0.14) for g in al_reves],
                    lag_ratio=0.2),
        run_time=0.6,
    )
    scene.next_slide(indicador=False)
