"""Puntos de entrada minimos de interfaces.

Estos wrappers se mantienen como atajos de compatibilidad.
La via canónica de arranque de usuario final sigue siendo `python -m src ...`.
"""

from .roles import DEFAULT_ROLE, get_system_prompt, list_role_names


def get_api_app():
    """Devuelve la aplicacion FastAPI de Mesias sin importar la API antes de tiempo."""
    from .api_fastapi import app
    return app


def get_mesias(*args, **kwargs):
    """Construye o reutiliza la instancia de Mesias usada por las interfaces."""
    from .api_fastapi import get_mesias as _get_mesias
    return _get_mesias(*args, **kwargs)


def run_api(*args, **kwargs):
    """Arranca la API HTTP de Mesias con import perezoso."""
    from .api_fastapi import run_api as _run_api
    return _run_api(*args, **kwargs)


def build_interface(*args, **kwargs):
    """Construye la interfaz Gradio de Mesias con import perezoso."""
    from .ui_gradio import build_interface as _build_interface
    return _build_interface(*args, **kwargs)


def launch(*args, **kwargs):
    """Lanza la interfaz Gradio de Mesias."""
    from .ui_gradio import launch as _launch
    return _launch(*args, **kwargs)


def respond(*args, **kwargs):
    """Ejecuta la funcion de respuesta usada por la UI Gradio de Mesias."""
    from .ui_gradio import respond as _respond
    return _respond(*args, **kwargs)


__all__ = [
    "DEFAULT_ROLE",
    "build_interface",
    "get_api_app",
    "get_mesias",
    "get_system_prompt",
    "launch",
    "list_role_names",
    "respond",
    "run_api",
]
