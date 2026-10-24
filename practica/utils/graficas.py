"""Todas las gráficas de los cuadernos, con la paleta del semillero."""

import matplotlib.pyplot as plt
import torch
from matplotlib.colors import LinearSegmentedColormap

from .configuracion import BACKGROUND, GREEN, LIGHT, PRIMARY, RED, SECONDARY, canvas, color


# --- Puntos y curvas (cuadernos 00 y 01) ---

X_LABEL = "minutos sin responder"
Y_LABEL = "mensajes enviados"


def _points(ax, x, y, point_color=PRIMARY):
    """La nube con los datos reales."""
    ax.scatter(x.detach().reshape(-1), y.detach().reshape(-1), s=45, color=point_color,
               edgecolor=BACKGROUND, linewidth=0.8, zorder=3, label="datos reales")


def plot_data(x, y, title="Los datos"):
    """Nada más los puntos."""
    ax = canvas(title, X_LABEL, Y_LABEL)
    _points(ax, x, y)
    ax.legend()
    plt.show()


@torch.no_grad()
def plot_fit(x, y, predict, label="lo que aprendió el modelo", title="Los datos y el modelo"):
    """Los puntos y encima la curva del modelo. `predict` recibe (n, 1) y devuelve (n, 1)."""
    ax = canvas(title, X_LABEL, Y_LABEL)
    _points(ax, x, y, SECONDARY)
    grid = torch.linspace(float(x.min()), float(x.max()), 300).reshape(-1, 1)
    ax.plot(grid.reshape(-1), predict(grid).reshape(-1), color=PRIMARY, linewidth=2.5,
            zorder=2, label=label)
    ax.legend()
    plt.show()


# --- La pérdida y las demás métricas, época a época ---

def plot_loss(history, title="La pérdida época a época"):
    """La curva de entrenamiento."""
    ax = canvas(title, "época", "pérdida (MSE)")
    ax.plot(range(1, len(history) + 1), history, color=PRIMARY, linewidth=2)
    plt.show()


def plot_metrics(series, title="Entrenamiento", y_label="pérdida"):
    """Varias curvas época a época. `series` es {nombre: lista de valores}."""
    ax = canvas(title, "época", y_label)
    for i, (name, values) in enumerate(series.items()):
        ax.plot(range(1, len(values) + 1), values, color=color(i), linewidth=2, label=name)
    ax.legend()
    plt.show()


# --- Cómo le fue a un clasificador (cuadernos 02 y 03) ---

# El orden en que se leen: primero la global, después las del positivo.
ORDER = [("accuracy", "accuracy"), ("precision", "precision"),
         ("recall", "recall"), ("f1", "f1 score")]

# Rampa de un solo tono, del fondo al primario: oscuro = pocos casos, claro = muchos.
RAMP = LinearSegmentedColormap.from_list("semillero", [BACKGROUND, PRIMARY])


def _bars(ax, results):
    """Las métricas de 0 a 1, con el valor escrito al lado de cada barra."""
    ax.set_title("Las métricas")
    values = [float(results[key]) for key, _ in ORDER]
    positions = list(range(len(ORDER)))

    ax.barh(positions, values, height=0.42, color=PRIMARY, zorder=3)
    for y, value in zip(positions, values):
        ax.text(value + 0.025, y, f"{value:.3f}", color=LIGHT, va="center", fontsize=10, zorder=4)

    ax.set_yticks(positions, [name for _, name in ORDER])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.18)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)


MEANINGS = [["VN", "FP"],
            ["FN", "VP"]]


def _cell_labels(ax, counts, largest):
    """Cada casilla con su cuenta y, debajo, lo que significa (VN, FP, FN o VP)."""
    for r, row in enumerate(counts):
        for c, count in enumerate(row):
            # Sobre una casilla clara el texto oscuro se lee mejor.
            ink = BACKGROUND if count > 0.6 * largest else LIGHT
            ax.text(c, r - 0.1, count, color=ink, ha="center", va="center", fontsize=18)
            ax.text(c, r + 0.22, MEANINGS[r][c], color=ink, ha="center", va="center",
                    fontsize=11, alpha=0.75)


def _matrix(ax, matrix):
    """La matriz de confusión: filas lo que pasó, columnas lo que dijo el modelo."""
    ax.set_title("Matriz de confusión")
    counts = [[int(value) for value in row] for row in matrix]
    largest = max(max(row) for row in counts) or 1

    ax.imshow(counts, cmap=RAMP, vmin=0, vmax=largest)
    _cell_labels(ax, counts, largest)
    _frame(ax)

    # Una ranura del color del fondo entre casilla y casilla.
    ax.set_xticks([0.5], minor=True)
    ax.set_yticks([0.5], minor=True)
    ax.grid(which="minor", color=BACKGROUND, linewidth=2, alpha=1)
    ax.tick_params(which="minor", length=0)


def plot_results(results, title="Cómo le fue al modelo"):
    """Las métricas y la matriz de confusión de un modelo, de un vistazo."""
    figure, (left, right) = plt.subplots(1, 2, figsize=(12, 4.6),
                                         gridspec_kw={"width_ratios": [1.2, 1]})
    figure.suptitle(title, color=LIGHT, fontsize=14)

    _bars(left, results)
    _matrix(right, results["matrix"])

    figure.tight_layout()
    plt.show()


def plot_comparison(models, title="Modelo contra modelo"):
    """Las mismas métricas de varios modelos, lado a lado. `models` es {nombre: resultados}."""
    names = list(models)
    height = 0.8 / len(names)
    figure, ax = plt.subplots(figsize=(9, 1.1 * len(ORDER) + 1.4))
    figure.suptitle(title, color=LIGHT, fontsize=14)

    for i, name in enumerate(names):
        values = [float(models[name][key]) for key, _ in ORDER]
        # De arriba hacia abajo dentro de cada grupo de barras.
        positions = [row + (i - (len(names) - 1) / 2) * height for row in range(len(ORDER))]
        ax.barh(positions, values, height=height * 0.86, color=color(i), zorder=3, label=name)
        for y, value in zip(positions, values):
            ax.text(value + 0.02, y, f"{value:.3f}", color=LIGHT, va="center", fontsize=9, zorder=4)

    ax.set_yticks(range(len(ORDER)), [name for _, name in ORDER])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.18)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    # Arriba y por fuera, para no taparle el valor a ninguna barra.
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.01), ncol=min(len(names), 2), framealpha=0)

    figure.tight_layout()
    plt.show()


# --- Las fotos y su veredicto (cuaderno 03) ---

# Con estas cuentas se normalizaron las fotos que entran a la red (las de ImageNet).
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)


def _to_image(tensor):
    """Deshace la normalización: de tensor (C, alto, ancho) a algo que se pueda mirar."""
    return (tensor.detach().cpu() * STD + MEAN).clamp(0, 1).permute(1, 2, 0).numpy()


def _frame(ax, frame_color=None):
    """Sin ejes, y con un borde de color alrededor de la foto si se pide."""
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(visible=False)
    for spine in ax.spines.values():
        spine.set_visible(frame_color is not None)
        spine.set_color(frame_color or SECONDARY)
        spine.set_linewidth(2.5)


def _grid(count, title, columns=6):
    """La figura y sus ejes, ya con el título puesto y los sobrantes escondidos."""
    columns = min(columns, count)
    rows = (count + columns - 1) // columns
    # "constrained" y no tight_layout: con fotos cuadradas, tight_layout monta los títulos sobre la fila de arriba.
    figure, _ = plt.subplots(rows, columns, figsize=(2.0 * columns, 2.3 * rows), squeeze=False,
                             layout="constrained")
    figure.suptitle(title, color=LIGHT, fontsize=14)
    for extra in figure.axes[count:]:
        extra.set_visible(False)
    return figure, figure.axes[:count]


def plot_sample(images, labels, title="Unas fotos"):
    """Una cuadrícula con las fotos y su etiqueta."""
    _, axes = _grid(len(images), title)
    for image, label, ax in zip(images, labels, axes):
        ax.imshow(_to_image(image))
        ax.set_title(label, color=SECONDARY, fontsize=9, pad=6)
        _frame(ax)
    plt.show()


def plot_predictions(images, probabilities, title="Lo que dijo el modelo"):
    """Cada foto con su veredicto en el borde: verde si dijo la clase positiva, rojo si no.

    `probabilities` es la probabilidad que le dio el modelo a la clase positiva.
    """
    _, axes = _grid(len(images), title)
    for image, probability, ax in zip(images, probabilities.flatten(), axes):
        ax.imshow(_to_image(image))
        _frame(ax, GREEN if float(probability) >= 0.5 else RED)
    plt.show()
