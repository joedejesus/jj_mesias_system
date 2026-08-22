from __future__ import annotations

"""Rutas compartidas del proyecto Mesias."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_LOG_PATH = DATA_DIR / "logs_mesias.json"
DEFAULT_MEMORY_PATH = DATA_DIR / "mesias_memory.json"
DEFAULT_CHAT_MEMORY_PATH = DATA_DIR / "memoria_chat.json"


__all__ = [
    "DATA_DIR",
    "DEFAULT_CHAT_MEMORY_PATH",
    "DEFAULT_LOG_PATH",
    "DEFAULT_MEMORY_PATH",
    "PROJECT_ROOT",
]
