# Cómo funcionan las redes neuronales

Charla hecha en manim

## Requisitos

- Python ≥ 3.13 (ver [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias
- [VS Code](https://code.visualstudio.com/) con la extensión de Python, para abrir los cuadernos

## Estructura

Dos proyectos independientes, cada uno con su `pyproject.toml` y su `.venv`:

```
presentacion/   la charla animada (manim-slides)
  main.py           orquestador: llama a cada slide_* en orden
  estilo.py         paleta, tipografía y rutas
  componentes.py    fábricas de mobjects reutilizables
  animaciones.py    helpers de animación
  fuentes.py        registro de las fuentes de marca
  diapositivas/     una diapositiva por archivo
  assets/           imágenes, logos y .ttf
practica/       el taller que acompaña a la charla (cuadernos .ipynb)
  00_inicio.ipynb            el entorno: uv, el lock, el .venv, y la comprobación de que todo quedó instalado
  01_una_neurona.ipynb       una neurona en PyTorch, y por qué hace falta la activación
  02_elementos_pytorch.ipynb tensores de cerca, cada cosa comparada con su equivalente en NumPy
  03_red_mas_grande.ipynb    clasificación con varias capas: lotes, prueba, softmax y la frontera de decisión
  utils.py                   las gráficas del taller, con la paleta del semillero
  datos/                     lo que generan los cuadernos (pesos guardados)
  assets/                    los banners de los cuadernos
```

Están separados a propósito: la presentación arrastra Manim y Qt, y la
práctica arrastra PyTorch. Nada de eso tiene por qué convivir en el mismo
entorno.

Los comandos se corren **desde dentro de cada carpeta**, no desde la raíz:
`uv` resuelve el proyecto por el directorio actual, y `manim-slides` busca
`.manim-slides.toml` y `slides/` ahí mismo.

## Uso

```bash
# --- La presentación ---
cd presentacion
uv sync                                                        # instalar su entorno

uv run python -m manim_slides render main.py presentation      # renderizar
uv run python -m manim_slides render -ql main.py presentation  # ... en baja calidad
uv run python -m manim_slides present presentation             # presentar

# --- La parte práctica ---
cd practica
uv sync                                                        # instalar su entorno
code .                                                         # abrir la carpeta en VS Code
```

Dentro de VS Code se abre `00_inicio.ipynb` y se elige el kernel de `practica/.venv`.

## La práctica

Después de la charla viene el taller: cuatro cuadernos donde se entrena una red neuronal
de verdad, línea por línea. Se empieza en
[`practica/00_inicio.ipynb`](practica/00_inicio.ipynb) y se siguen en orden.

1. **`00_inicio`** — el entorno y la comprobación de que todo quedó instalado.
2. **`01_una_neurona`** — `y = w·x + b`, el bucle de entrenamiento, y por qué sin activación
   una red no pasa de ser una recta.
3. **`02_elementos_pytorch`** — el tensor por dentro: formas, tipos, reshape, indexado y
   broadcasting, cada uno al lado de su equivalente en NumPy.
4. **`03_red_mas_grande`** — una red de varias capas que clasifica en tres clases, con
   minilotes, conjunto de prueba, matriz de confusión y frontera de decisión.

## Bibliografía

### Libros

- Bishop, C. M., & Bishop, H. (2024). _Deep Learning: Foundations and Concepts_. Springer.
- Kinsley, H., & Kukieła, D. _Neural Networks from Scratch in Python_. https://nnfs.io

### Vídeos

- _La ecuación central de la neurociencia_. YouTube. https://www.youtube.com/watch?v=zOmhHE2xctw
- _Neural Networks Explained: From 1943 Origins to Deep Learning Revolution_. YouTube. https://www.youtube.com/watch?v=AA2ettRM6_Q
- _Understanding Backpropagation: The Core Algorithm of Machine Learning_. YouTube. https://www.youtube.com/watch?v=SmZmBKc7Lrs
- _🧠 TODO sobre el FUNCIONAMIENTO de la NEURONA 👩🏼‍🏫_. Youtube. https://www.youtube.com/watch?v=VBvOVhEqHks
- _Teorema de aproximación universal: el componente fundamental del aprendizaje profundo_. Youtube. https://www.youtube.com/watch?v=wen3221_3gU
- _Cómo funcionan las redes neuronales - Inteligencia Artificial_. Youtube. https://www.youtube.com/watch?v=CU24iC3grq8&t=6s

### Cursos

La parte práctica sigue estos dos:

- _PyTorch for Deep Learning Professional Certificate_. DeepLearning.AI. https://www.deeplearning.ai/specializations/pytorch-for-deep-learning-professional-certificate
- _Deep Learning Specialization_. DeepLearning.AI. https://www.deeplearning.ai/specializations/deep-learning

### Otros

- Roller, S. _Desglose del cómputo (FLOPs) por componente en modelos de lenguaje (OPT)_. X (Twitter). https://x.com/stephenroller/status/1579993017234382849