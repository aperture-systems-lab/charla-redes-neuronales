import numpy as np
from manim import (
    RIGHT,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    MoveAlongPath,
    linear,
)

from estilo import CLARO


def limpiar_pantalla(scene):
    resto = [m for m in scene.mobjects if m is not getattr(scene, "marco", None)]
    for m in resto:
        m.clear_updaters()
    if resto:
        scene.play(*[FadeOut(m) for m in resto])


def aparecer_uno_a_uno(scene, grupo, run_time=0.4, shift=RIGHT * 0.2):
    for elemento in grupo:
        scene.play(FadeIn(elemento, shift=shift), run_time=run_time)


def impulsos_al_azar(scene, conexiones, semilla, cantidad, lag_ratio, run_time):
    rng = np.random.default_rng(semilla)
    for _ in range(2):
        elegidas = rng.choice(len(conexiones), size=cantidad, replace=False)
        impulsos = [
            Dot(color=CLARO, radius=0.06).move_to(conexiones[k].get_start())
            for k in elegidas
        ]
        scene.play(
            LaggedStart(*[
                MoveAlongPath(punto, conexiones[k], rate_func=linear)
                for punto, k in zip(impulsos, elegidas)
            ], lag_ratio=lag_ratio),
            run_time=run_time,
        )
        scene.play(*[FadeOut(p, scale=0.1) for p in impulsos], run_time=0.3)
