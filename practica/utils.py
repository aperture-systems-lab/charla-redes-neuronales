"""Gráficas de apoyo para los cuadernos, con la paleta del semillero."""

import matplotlib.pyplot as plt
import torch
from matplotlib import font_manager

FONDO = "#010409"
PRIMARIO = "#29c4d9"
SECUNDARIO = "#8dbccd"
CLARO = "#eaf6fc"
AMBAR = "#caa655"
MORADO = "#ac94f1"
VERDE = "#48d0a5"
ROJO = "#e06c75"

CICLO = [PRIMARIO, AMBAR, MORADO, VERDE, ROJO]


def _familia():
    instaladas = {f.name for f in font_manager.fontManager.ttflist}
    for nombre in ("JetBrains Mono", "DejaVu Sans Mono"):
        if nombre in instaladas:
            return nombre
    return "monospace"


def _lienzo(titulo, x_etiqueta, y_etiqueta, tam=(9, 5)):
    fig, ax = plt.subplots(figsize=tam)
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(FONDO)
    ax.tick_params(colors=SECUNDARIO, labelsize=9)
    for lado, visible in (("bottom", True), ("left", True), ("top", False), ("right", False)):
        ax.spines[lado].set_visible(visible)
        ax.spines[lado].set_color(SECUNDARIO)
    ax.grid(True, color=SECUNDARIO, alpha=0.15, linewidth=0.8)
    familia = _familia()
    ax.set_xlabel(x_etiqueta, color=SECUNDARIO, fontsize=10, fontfamily=familia)
    ax.set_ylabel(y_etiqueta, color=SECUNDARIO, fontsize=10, fontfamily=familia)
    if titulo:
        ax.set_title(titulo, color=CLARO, fontsize=13, pad=14, fontfamily=familia)
    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily(familia)
    return fig, ax


def _leyenda(ax):
    leyenda = ax.legend(facecolor=FONDO, edgecolor=SECUNDARIO, labelcolor=CLARO, fontsize=9)
    leyenda.get_frame().set_alpha(0.9)
    for texto in leyenda.get_texts():
        texto.set_fontfamily(_familia())


def _plano(t):
    return t.detach().reshape(-1).numpy()


@torch.no_grad()
def _curva(predecir, x, puntos=300):
    malla = torch.linspace(float(x.min()), float(x.max()), puntos).reshape(-1, 1)
    return _plano(malla), _plano(predecir(malla))


def dibujar_datos(x, y, titulo="Los datos", x_etiqueta="minutos sin responder",
                  y_etiqueta="mensajes enviados"):
    """Nada más los puntos."""
    fig, ax = _lienzo(titulo, x_etiqueta, y_etiqueta)
    ax.scatter(_plano(x), _plano(y), s=45, color=PRIMARIO, edgecolor=FONDO, linewidth=0.8,
               zorder=3, label="datos reales")
    _leyenda(ax)
    plt.show()


def dibujar_ajuste(x, y, predecir, etiqueta="lo que aprendió el modelo",
                   titulo="Los datos y el modelo", x_etiqueta="minutos sin responder",
                   y_etiqueta="mensajes enviados"):
    """Los puntos y encima la curva del modelo. `predecir` recibe (n, 1) y devuelve (n, 1)."""
    fig, ax = _lienzo(titulo, x_etiqueta, y_etiqueta)
    ax.scatter(_plano(x), _plano(y), s=45, color=SECUNDARIO, edgecolor=FONDO, linewidth=0.8,
               zorder=3, label="datos reales")
    malla, curva = _curva(predecir, x)
    ax.plot(malla, curva, color=PRIMARIO, linewidth=2.5, zorder=2, label=etiqueta)
    _leyenda(ax)
    plt.show()


def comparar_ajustes(x, y, modelos, titulo="Comparación", x_etiqueta="minutos sin responder",
                     y_etiqueta="mensajes enviados"):
    """Los mismos puntos con varias curvas encima. `modelos` es {etiqueta: predecir}."""
    fig, ax = _lienzo(titulo, x_etiqueta, y_etiqueta)
    ax.scatter(_plano(x), _plano(y), s=45, color=SECUNDARIO, edgecolor=FONDO, linewidth=0.8,
               zorder=3, label="datos reales")
    for i, (etiqueta, predecir) in enumerate(modelos.items()):
        malla, curva = _curva(predecir, x)
        ax.plot(malla, curva, color=CICLO[i % len(CICLO)], linewidth=2.5, zorder=2, label=etiqueta)
    _leyenda(ax)
    plt.show()


def dibujar_perdida(historial, titulo="La pérdida época a época", escala_log=False):
    """La curva de entrenamiento."""
    fig, ax = _lienzo(titulo, "época", "pérdida (MSE)")
    ax.plot(range(1, len(historial) + 1), historial, color=PRIMARIO, linewidth=2)
    if escala_log:
        ax.set_yscale("log")
    plt.show()


def _colores(cantidad):
    return [CICLO[i % len(CICLO)] for i in range(cantidad)]


def dibujar_clases(x, etiquetas, nombres, titulo="Los datos",
                   x_etiqueta="característica 1", y_etiqueta="característica 2"):
    """Una nube de puntos coloreada por clase. `x` es (n, 2) y `etiquetas` es (n,)."""
    fig, ax = _lienzo(titulo, x_etiqueta, y_etiqueta, tam=(7, 6))
    puntos = x.detach().numpy()
    clases = etiquetas.detach().reshape(-1).numpy()
    for i, nombre in enumerate(nombres):
        dentro = clases == i
        ax.scatter(puntos[dentro, 0], puntos[dentro, 1], s=26, color=CICLO[i % len(CICLO)],
                   edgecolor=FONDO, linewidth=0.5, zorder=3, label=nombre)
    _leyenda(ax)
    plt.show()


@torch.no_grad()
def dibujar_frontera(predecir, x, etiquetas, nombres, titulo="La frontera de decisión",
                     x_etiqueta="característica 1", y_etiqueta="característica 2", puntos=300):
    """El fondo pintado con la clase que elige el modelo, y encima los datos reales."""
    from matplotlib.colors import ListedColormap

    datos = x.detach().numpy()
    margen = 0.4
    eje_x = torch.linspace(float(datos[:, 0].min()) - margen, float(datos[:, 0].max()) + margen, puntos)
    eje_y = torch.linspace(float(datos[:, 1].min()) - margen, float(datos[:, 1].max()) + margen, puntos)
    malla_x, malla_y = torch.meshgrid(eje_x, eje_y, indexing="xy")
    malla = torch.stack([malla_x.reshape(-1), malla_y.reshape(-1)], dim=1)
    elegida = predecir(malla).argmax(dim=1).reshape(malla_x.shape).numpy()

    fig, ax = _lienzo(titulo, x_etiqueta, y_etiqueta, tam=(7, 6))
    niveles = [i - 0.5 for i in range(len(nombres) + 1)]
    ax.contourf(malla_x.numpy(), malla_y.numpy(), elegida, levels=niveles,
                colors=_colores(len(nombres)), alpha=0.22, zorder=1)
    clases = etiquetas.detach().reshape(-1).numpy()
    for i, nombre in enumerate(nombres):
        dentro = clases == i
        ax.scatter(datos[dentro, 0], datos[dentro, 1], s=26, color=CICLO[i % len(CICLO)],
                   edgecolor=FONDO, linewidth=0.5, zorder=3, label=nombre)
    _leyenda(ax)
    plt.show()


def dibujar_metricas(series, titulo="Entrenamiento", y_etiqueta="pérdida", escala_log=False):
    """Varias curvas época a época. `series` es {etiqueta: lista de valores}."""
    fig, ax = _lienzo(titulo, "época", y_etiqueta)
    for i, (etiqueta, valores) in enumerate(series.items()):
        ax.plot(range(1, len(valores) + 1), valores, color=CICLO[i % len(CICLO)],
                linewidth=2, label=etiqueta)
    if escala_log:
        ax.set_yscale("log")
    _leyenda(ax)
    plt.show()
