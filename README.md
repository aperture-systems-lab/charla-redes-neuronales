# Cómo funcionan las redes neuronales

Charla del **Semillero de Data Science e IA — Aperture**: una introducción visual
al aprendizaje profundo.

La presentación es una animación de [Manim](https://www.manim.community/) servida
como diapositivas con [Manim Slides](https://manim-slides.eertmans.be/): cada
diapositiva es una escena animada y se avanza con las flechas del teclado.

Este repositorio contiene **solo esta charla**.

## Requisitos

- Python ≥ 3.13 (ver [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias
- **FFmpeg** en el `PATH` (Manim lo usa para componer los vídeos)
- Una distribución de **TeX** (MiKTeX / TeX Live) para las fórmulas `MathTex`

## Puesta en marcha

```bash
uv sync
```

## Uso

```bash
# Renderizar la presentación (calidad por defecto)
uv run python -m manim_slides render main.py presentation

# Iteración rápida mientras diseñas (baja calidad)
uv run python -m manim_slides render -ql main.py presentation

# Presentar en pantalla completa (flechas para avanzar)
uv run python -m manim_slides present presentation

# Exportar a PowerPoint o a vídeo
uv run python -m manim_slides convert presentation salida.pptx
uv run python -m manim_slides convert presentation salida.mp4
```

Ejecuta los comandos desde la raíz del repositorio: las rutas de `assets/` se
resuelven respecto al proyecto, y Manim escribe su salida en `media/` y
`slides/` (ambas ignoradas por git).

> **Por qué `python -m manim_slides` y no `manim-slides` a secas:** Windows
> Smart App Control bloquea los lanzadores `.exe` sin firmar que uv genera en
> `.venv\Scripts\`, y el comando corto falla con
> `Failed to spawn: manim-slides ... An Application Control policy has blocked
> this file (os error 4551)`. Invocar el módulo evita ese lanzador y acepta
> exactamente las mismas opciones. Si trabajas en una máquina sin esa política,
> `uv run manim-slides ...` también funciona.

## Estructura

| Ruta               | Qué contiene                                                              |
| ------------------ | ------------------------------------------------------------------------- |
| `main.py`          | Orquestador delgado: la clase `presentation` y el orden de las diapositivas |
| `estilo.py`        | Paleta, tipografía y constantes de marca — único sitio con valores mágicos |
| `fuentes.py`       | Registra las fuentes de `assets/fonts/` en el proceso (sin instalarlas)   |
| `componentes.py`   | Fábricas de mobjects reutilizables (texto, tarjetas, marco, viñetas…)     |
| `animaciones.py`   | Helpers de animación compartidos entre diapositivas                       |
| `diapositivas/`    | Una diapositiva por archivo, agrupadas en mixins temáticos                |
| `assets/`          | Imágenes de marca y fuentes `.ttf`                                        |

### Diapositivas

Cada diapositiva es un archivo en `diapositivas/` que expone `construir(scene)`.
`diapositivas/__init__.py` las agrupa en mixins (`SlidesInicio`, `SlidesCuerpo`,
`SlidesFinal`) que aportan los métodos `slide_*` que `main.py` invoca.

Para añadir una:

1. Copia `diapositivas/_plantilla.py` a `diapositivas/<nombre>.py`.
2. En `diapositivas/__init__.py`, impórtalo y añade
   `slide_<nombre> = _slide(<nombre>.construir)` al mixin que corresponda.
3. Llama `self.slide_<nombre>()` desde `construct` en `main.py`.

Reglas: no limpies la pantalla al entrar (lo hace `SlideBase.iniciar_slide`),
nunca hardcodees colores (úsalos desde `estilo`) y termina siempre con
`scene.next_slide()`.

### Indicador de avance

`SlideBase.next_slide` envuelve al de manim-slides: antes de cada pausa hace
aparecer el logo del semillero en la esquina inferior derecha
(`componentes.logo_esquina`) y lo retira al avanzar. Así el fotograma congelado
avisa de que la charla sigue. Las diapositivas no tienen que hacer nada: basta
con llamar a `scene.next_slide()` como siempre.

La portada y el cierre pintan ese mismo logo con la misma fábrica, así que allí
el indicador cae justo encima del que ya estaba y no se nota. Por eso conviene
dejar libre esa esquina en las diapositivas nuevas.

## Bibliografía

### Libros

- Bishop, C. M., & Bishop, H. (2024). _Deep Learning: Foundations and Concepts_. Springer.
- Amidi, A., & Amidi, S. _Super Study Guide: Transformers and Large Language Models_.
- Kinsley, H., & Kukieła, D. _Neural Networks from Scratch in Python_. https://nnfs.io

### Vídeos

- _La ecuación central de la neurociencia_. YouTube. https://www.youtube.com/watch?v=zOmhHE2xctw
- _Neural Networks Explained: From 1943 Origins to Deep Learning Revolution_. YouTube. https://www.youtube.com/watch?v=AA2ettRM6_Q
- _Understanding Backpropagation: The Core Algorithm of Machine Learning_. YouTube. https://www.youtube.com/watch?v=SmZmBKc7Lrs
