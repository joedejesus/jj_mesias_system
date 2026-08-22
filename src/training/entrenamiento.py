from __future__ import annotations

"""Entrenamiento LoRA con defaults prudentes para el ecosistema Mesias."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

from ..core.lazy_imports import lazy_import_peft, lazy_import_torch, lazy_import_transformers_for_training
from ..core.model_loader import infer_torch_dtype, resolve_model_path
from .preparacion_datos import load_jsonl_examples, prepare_sft_dataset


DEFAULT_OUTPUT_DIR = Path(__file__).resolve(
).parent.parent.parent / "data" / "checkpoints" / "mesias-qwen25-lora"
DEFAULT_LORA_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


class _ListDataset:
    """Dataset minimo en memoria que adapta filas preparadas al Trainer de Mesias."""

    def __init__(self, rows: Sequence[Mapping[str, Any]]) -> None:
        self.rows = list(rows)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        row = dict(self.rows[index])
        row.pop("text", None)
        row.pop("messages", None)
        return row


@dataclass
class EntrenamientoConfig:
    """Configuracion de entrenamiento LoRA usada por Mesias."""
    output_dir: Path = DEFAULT_OUTPUT_DIR
    epochs: float = 1.0
    learning_rate: float = 2e-4
    train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    dataloader_num_workers: int = 0
    cpu_threads: int = 4
    warmup_ratio: float = 0.03
    weight_decay: float = 0.0
    logging_steps: int = 10
    save_steps: int = 100
    max_length: int = 2048
    max_grad_norm: float = 1.0
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(
        default_factory=lambda: list(DEFAULT_LORA_TARGET_MODULES))


def build_lora_config(config: EntrenamientoConfig) -> Any:
    """Construye la configuracion LoRA derivada de un EntrenamientoConfig de Mesias."""
    peft = lazy_import_peft()
    return peft["LoraConfig"](
        task_type=peft["TaskType"].CAUSAL_LM,
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        bias="none",
        target_modules=list(config.lora_target_modules),
    )


def create_trainer(
        dataset_rows: Sequence[Mapping[str, Any]],
        *,
        config: Optional[EntrenamientoConfig] = None,
        model_path: Optional[Union[str, Path]] = None,
) -> Any:
    """Crea un Trainer listo para entrenar un adaptador LoRA sobre Mesias."""
    resolved_config = config or EntrenamientoConfig()
    resolved_config.output_dir.mkdir(parents=True, exist_ok=True)
    resolved_model_path = resolve_model_path(model_path)

    torch = lazy_import_torch()
    transformers = lazy_import_transformers_for_training()
    peft = lazy_import_peft()

    max_cpu_threads = max(
        1, min(resolved_config.cpu_threads, os.cpu_count() or 1))
    if hasattr(torch, "set_num_threads"):
        torch.set_num_threads(max_cpu_threads)
    if hasattr(torch, "set_num_interop_threads"):
        torch.set_num_interop_threads(max_cpu_threads)

    tokenizer = transformers["AutoTokenizer"].from_pretrained(
        str(resolved_model_path),
        local_files_only=True,
        use_fast=False,
        padding_side="left",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = transformers["AutoModelForCausalLM"].from_pretrained(
        str(resolved_model_path),
        local_files_only=True,
        low_cpu_mem_usage=True,
        dtype=infer_torch_dtype("cpu"),
    )
    model = peft["get_peft_model"](model, build_lora_config(resolved_config))
    model.train()

    training_arguments = transformers["TrainingArguments"](
        output_dir=str(resolved_config.output_dir),
        num_train_epochs=resolved_config.epochs,
        per_device_train_batch_size=resolved_config.train_batch_size,
        gradient_accumulation_steps=resolved_config.gradient_accumulation_steps,
        dataloader_num_workers=resolved_config.dataloader_num_workers,
        learning_rate=resolved_config.learning_rate,
        warmup_ratio=resolved_config.warmup_ratio,
        weight_decay=resolved_config.weight_decay,
        logging_steps=resolved_config.logging_steps,
        save_steps=resolved_config.save_steps,
        max_grad_norm=resolved_config.max_grad_norm,
        report_to=[],
        remove_unused_columns=False,
        bf16=False,
        fp16=False,
    )

    data_collator = transformers["DataCollatorForLanguageModeling"](
        tokenizer=tokenizer,
        mlm=False,
    )
    trainer = transformers["Trainer"](
        model=model,
        args=training_arguments,
        train_dataset=_ListDataset(dataset_rows),
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    return trainer


def train_lora_from_examples(
        examples: Iterable[Mapping[str, Any]],
        *,
        config: Optional[EntrenamientoConfig] = None,
        model_path: Optional[Union[str, Path]] = None,
) -> Any:
    """Prepara datos, entrena un adaptador LoRA y guarda el resultado para Mesias."""
    resolved_config = config or EntrenamientoConfig()
    dataset_rows = prepare_sft_dataset(
        list(examples),
        model_path=model_path,
        max_length=resolved_config.max_length,
    )
    trainer = create_trainer(
        dataset_rows,
        config=resolved_config,
        model_path=model_path,
    )
    trainer.train()
    trainer.model.save_pretrained(str(resolved_config.output_dir))
    trainer.tokenizer.save_pretrained(str(resolved_config.output_dir))
    return trainer


def train_lora_from_jsonl(
        dataset_path: Union[str, Path],
        *,
        config: Optional[EntrenamientoConfig] = None,
        model_path: Optional[Union[str, Path]] = None,
) -> Any:
    """Carga un dataset JSONL y lanza el entrenamiento LoRA de Mesias."""
    examples = load_jsonl_examples(dataset_path)
    return train_lora_from_examples(
        examples,
        config=config,
        model_path=model_path,
    )


__all__ = [
    "DEFAULT_LORA_TARGET_MODULES",
    "DEFAULT_OUTPUT_DIR",
    "EntrenamientoConfig",
    "build_lora_config",
    "create_trainer",
    "train_lora_from_examples",
    "train_lora_from_jsonl",
]
