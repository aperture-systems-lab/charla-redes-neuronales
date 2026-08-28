"""Paleta, tipografía y constantes compartidas por toda la animación.

Único sitio con valores "mágicos": cambia aquí los colores o la fuente y se
re-tematiza la presentación entera. Ninguna diapositiva debe hardcodear hex
ni rutas de assets.

Charla: "Cómo funcionan las redes neuronales".
Marca: Semillero de Data Science e IA — Aperture.
"""

import os

# Importar registra las fuentes de marca (Press Start 2P + JetBrains Mono).
import fuentes  # noqa: F401

# --- Paleta (marca Aperture) ---------------------------------------------
FONDO = "#010409"        # fondo oscuro azulado (tech / red neuronal)
PRIMARIO = "#29c4d9"     # cian: acento de marca (títulos, resaltados)
SECUNDARIO = "#8dbccd"   # azul acero: texto secundario, ejes, líneas
CLARO = "#eaf6fc"        # casi blanco: texto principal sobre el fondo oscuro
BLANCO = "#ffffff"       # blanco puro: solo para fondos de imagen (discos, recortes)

# Colores de apoyo de la paleta (categorías, diagramas, énfasis)
AMBAR = "#caa655"
MORADO = "#ac94f1"
VERDE = "#48d0a5"
ROJO = "#e06c75"         # lo que no sirve / lo que falla (el verde es su pareja)

# Alias cómodos (por si prefieres nombrarlos por su rol de color)
ACENTO = PRIMARIO
GRIS = SECUNDARIO

# --- Tipografía ----------------------------------------------------------
FONT = "JetBrains Mono"          # cuerpo, texto general
FONT_TITULO = "Press Start 2P"   # títulos / display (pixel, retro)

# --- Rutas ---------------------------------------------------------------
RAIZ = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(RAIZ, "assets")  # imágenes de marca (.png, logos, iconos)

# --- Constantes de layout ------------------------------------------------
TAM_TITULO = 30          # tamaño del título de diapositiva (en FONT_TITULO)
