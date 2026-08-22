from __future__ import annotations

"""Imports perezosos compartidos por el runtime y el entrenamiento de Mesias."""

from importlib import import_module
from typing import Any, Dict, Tuple


def lazy_import_torch() -> Any:
    try:
        import torch
    except ImportError as exc:
        raise ImportError(
            "PyTorch no esta instalado. Instala 'torch' para usar Mesias."
        ) from exc
    return torch


def lazy_import_transformers_for_inference() -> Tuple[Any, Any]:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise ImportError(
            "Transformers no esta instalado. Instala 'transformers' para cargar el modelo local."
        ) from exc
    return AutoModelForCausalLM, AutoTokenizer


def lazy_import_transformers_for_training() -> Dict[str, Any]:
    try:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise ImportError(
            "Transformers no esta instalado. Instala 'transformers' para entrenar Mesias."
        ) from exc
    return {
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "DataCollatorForLanguageModeling": DataCollatorForLanguageModeling,
        "Trainer": Trainer,
        "TrainingArguments": TrainingArguments,
    }


def lazy_import_peft() -> Dict[str, Any]:
    try:
        peft_module = import_module("peft")
    except ImportError as exc:
        raise ImportError(
            "PEFT no esta instalado. Instala 'peft' para usar adaptadores LoRA."
        ) from exc
    return {
        "LoraConfig": peft_module.LoraConfig,
        "TaskType": peft_module.TaskType,
        "get_peft_model": peft_module.get_peft_model,
        "PeftModel": peft_module.PeftModel,
    }


__all__ = [
    "lazy_import_peft",
    "lazy_import_torch",
    "lazy_import_transformers_for_inference",
    "lazy_import_transformers_for_training",
]
