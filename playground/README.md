<h1 align="center">Playground</h1>

<p align="center">
  <b><a href="http://127.0.0.1:8000">http://127.0.0.1:8000</a></b>
</p>


## Pestañas

| | |
| --- | --- |
| **01 · fronteras de decisión** | A la izquierda eliges los datos (espiral, xor, círculo…) y el modelo; a la derecha, un plano grande donde se ve cómo lo parte. Regresión logística, árbol de decisión y red neuronal entrenan a la vez; las teclas 1, 2 y 3 cambian cuál se dibuja. |
| **02 · visión en vivo** | La cámara pasa por redes convolucionales que se pueden combinar: manos, malla de la cara, segmentación (pelo, piel, ropa) y clasificación. Todo corre en el navegador. |
| **03 · gemini dibuja** | Le pides un dibujo a Gemini: tu mensaje aparece partido en tokens y en el lienzo se ve el código HTML escribiéndose hasta convertirse en el dibujo. |

## .env

En la carpeta `playground/`. Está en `.gitignore`.

```ini
GEMINI_API_KEY=tu-clave-aqui
```

## Arrancar

```bash
cd playground
uv sync
uv run python -m backend.descargar          # una vez y con internet: ~85 MB de modelos
uv run python -m uvicorn backend.main:app
```


