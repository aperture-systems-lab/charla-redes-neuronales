# Cómo funcionan las redes neuronales

Charla hecha en manim sobre cómo funcionan las redes neuronales.

## Requisitos

- Python 
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias

## Uso

```bash
# --- La presentación ---
cd presentacion
uv sync                                                        # instalar su entorno

uv run python -m manim_slides render main.py presentation      # renderizar
uv run python -m manim_slides present presentation             # presentar

# --- La parte práctica ---
cd practica
uv sync                                                        # instalar su entorno
code .                                                         # abrir la carpeta en VS Code

# --- El playground ---
cd playground
uv sync                                                        # instalar su entorno
uv run python -m backend.descargar                             # bajar los modelos (una vez)
uv run python -m uvicorn backend.main:app                      # abrir http://127.0.0.1:8000
```

Dentro de VS Code se abre `00_inicio.ipynb` y se elige el kernel de `practica/.venv`.

## El playground

Una web para jugar en vivo con los conceptos de redes neuronales. Necesita una clave de Gemini en `playground/.env`. Revisar la informaciòn que está en [`playground/README.md`](playground/README.md).

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

### Otros

- Roller, S. _Desglose del cómputo (FLOPs) por componente en modelos de lenguaje (OPT)_. X (Twitter). https://x.com/stephenroller/status/1579993017234382849