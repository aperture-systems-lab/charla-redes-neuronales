"""El tic-tac-toe del cuaderno 04: las reglas y un tablero para jugarle a la red.

El tablero son 9 casillas y siempre se ve desde quien tiene el turno:
1 es suyo, -1 del rival y 0 está libre.
"""

import ipywidgets as widgets
import torch

from .configuracion import AMBER, LIGHT, PRIMARY, SECONDARY

EMPTY = (0,) * 9

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

IDENTITY = tuple(range(9))                # cada casilla en su sitio
ROTATION = (6, 3, 0, 7, 4, 1, 8, 5, 2)    # dónde cae cada casilla al girar el tablero
MIRROR = (2, 1, 0, 5, 4, 3, 8, 7, 6)      # y al reflejarlo


def free_cells(board):
    return [cell for cell, value in enumerate(board) if value == 0]


def has_winner(board):
    return any(board[a] != 0 and board[a] == board[b] == board[c] for a, b, c in LINES)


def step(board, cell):
    """Juega en `cell`. Devuelve el tablero visto por el rival, la recompensa y si se acabó."""
    next_board = list(board)
    next_board[cell] = 1
    won = has_winner(next_board)
    return tuple(-value for value in next_board), float(won), won or not free_cells(next_board)


def _reorder(board, order):
    """El tablero con las casillas en el orden de `order` (girado, reflejado o tal cual)."""
    return tuple(board[i] for i in order)


def _transform(move, order):
    """La misma jugada, con los dos tableros y la casilla elegida reordenados igual."""
    board, cell, reward, next_board, done = move
    return _reorder(board, order), order.index(cell), reward, _reorder(next_board, order), done


def symmetries(move):
    """La misma jugada girada y reflejada: 8 versiones del mismo juego."""
    versions = []
    for _ in range(4):
        versions += [_transform(move, IDENTITY), _transform(move, MIRROR)]
        move = _transform(move, ROTATION)
    return versions


def _cell_button():
    """Una casilla del tablero: un botón cuadrado con la ficha en grande."""
    button = widgets.Button(layout=widgets.Layout(width="80px", height="80px"))
    button.style.button_color = "#0b1622"
    button.style.font_family = "Consolas, monospace"
    button.style.font_size = "40px"
    button.style.font_weight = "bold"
    return button


class _Match:
    """La partida contra la red: el tablero, sus botones y el mensaje de abajo."""

    def __init__(self, model):
        self.model = model
        self.status = widgets.HTML()
        self.buttons = [_cell_button() for _ in range(9)]
        for cell, button in enumerate(self.buttons):
            button.on_click(lambda _, cell=cell: self.click(cell))
        self.new_game()

    def say(self, text, color=SECONDARY):
        self.status.value = f'<span style="font-family: Consolas, monospace; font-size: 16px; color: {color}">{text}</span>'

    def place(self, cell, value):
        """Pone la ficha y dice si se acabó la partida."""
        self.board[cell] = value
        self.buttons[cell].description = "X" if value == 1 else "O"
        self.buttons[cell].style.text_color = PRIMARY if value == 1 else AMBER
        if has_winner(self.board) and value == 1:
            self.say("¡Ganaste!", PRIMARY)
        elif has_winner(self.board):
            self.say("Gana la red", AMBER)
        elif not free_cells(self.board):
            self.say("Empate")
        else:
            return False
        return True

    @torch.no_grad()
    def model_move(self):
        q = self.model(torch.tensor([-value for value in self.board], dtype=torch.float32))
        self.place(max(free_cells(self.board), key=lambda cell: q[cell]), -1)

    def click(self, cell):
        if self.board[cell] == 0 and not has_winner(self.board) and not self.place(cell, 1):
            self.model_move()

    def new_game(self, _=None):
        self.board = [0] * 9                    # 1 es tuya, -1 de la red
        for button in self.buttons:
            button.description = ""
        self.say("Tu turno")


def play_against(model):
    """Tú eres X y empiezas. El tablero aparece debajo de la celda."""
    match = _Match(model)

    again = widgets.Button(description="otra partida", layout=widgets.Layout(width="252px"))
    again.style.button_color = "#10202d"
    again.style.text_color = LIGHT
    again.on_click(match.new_game)

    grid = widgets.GridBox(match.buttons, layout=widgets.Layout(
        grid_template_columns="repeat(3, 80px)", grid_gap="6px"))
    return widgets.VBox([grid, match.status, again], layout=widgets.Layout(padding="10px"))
