# Cómo funcionan las redes neuronales

Charla hecha en manim

## Requisitos

- Python 
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
practica/       práctica que acompaña a la charla 
  xx_notebook.ipynb          notebooks con las explicaciones prácticas
  utils.py                   funciones auxiliares para la parte práctica
  datos/                     lo que generan los cuadernos (pesos guardados)
  assets/                    los banners de los cuadernos
```

Están separados a propósito: la presentación contiene Manim, y la
práctica contiene PyTorch. 

Los comandos se corren **desde dentro de cada carpeta**, no desde la raíz.

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

Después de la charla viene una parte práctica iniciando por [`practica/00_inicio.ipynb`](practica/00_inicio.ipynb) y se siguen en orden.

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