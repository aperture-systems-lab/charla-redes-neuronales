# Cómo funcionan las redes neuronales

Charla hecha en manim

## Requisitos

- Python ≥ 3.13 (ver [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias

## Puesta en marcha

```bash
uv sync
```

## Uso

```bash
# Instalación de librerías 
uv sync

# Renderizar la presentación 
uv run python -m manim_slides render main.py presentation

#  Renderizar la presentación con baja calidad
uv run python -m manim_slides render -ql main.py presentation

# Presentar en presentación
uv run python -m manim_slides present presentation
```

## Bibliografía

### Libros

- Bishop, C. M., & Bishop, H. (2024). _Deep Learning: Foundations and Concepts_. Springer.
- Amidi, A., & Amidi, S. _Super Study Guide: Transformers and Large Language Models_.
- Kinsley, H., & Kukieła, D. _Neural Networks from Scratch in Python_. https://nnfs.io

### Vídeos

- _La ecuación central de la neurociencia_. YouTube. https://www.youtube.com/watch?v=zOmhHE2xctw
- _Neural Networks Explained: From 1943 Origins to Deep Learning Revolution_. YouTube. https://www.youtube.com/watch?v=AA2ettRM6_Q
- _Understanding Backpropagation: The Core Algorithm of Machine Learning_. YouTube. https://www.youtube.com/watch?v=SmZmBKc7Lrs
- _🧠 TODO sobre el FUNCIONAMIENTO de la NEURONA 👩🏼‍🏫_. Youtube. https://www.youtube.com/watch?v=VBvOVhEqHks
- _Teorema de aproximación universal: el componente fundamental del aprendizaje profundo_. Youtube. https://www.youtube.com/watch?v=wen3221_3gU
