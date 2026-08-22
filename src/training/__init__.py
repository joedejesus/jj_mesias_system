"""Puntos de entrada minimos de entrenamiento."""

from .entrenamiento import EntrenamientoConfig, train_lora_from_jsonl
from .preparacion_datos import prepare_sft_dataset

__all__ = [
    "EntrenamientoConfig",
    "prepare_sft_dataset",
    "train_lora_from_jsonl",
]
