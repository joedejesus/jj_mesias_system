from __future__ import annotations

"""Carga y validacion de artefactos locales de modelo para Mesias."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from .lazy_imports import lazy_import_peft, lazy_import_torch, lazy_import_transformers_for_inference


DEFAULT_MODEL_DIR = Path(__file__).resolve().parent.parent / "modelo"

REQUIRED_CONFIG_FILES = ("config.json",)
TOKENIZER_FILE_CANDIDATES = (
    "tokenizer_config.json",
    "tokenizer.json",
)
WEIGHT_FILE_CANDIDATES = (
    "model.safetensors.index.json",
    "model.safetensors",
    "pytorch_model.bin",
)


@dataclass
class ModelArtifacts:
    """Contenedor con el modelo, tokenizer y metadatos resueltos por Mesias."""
    model: Any
    tokenizer: Any
    model_path: Path
    device: str


def resolve_model_path(model_path: Optional[Union[str, Path]] = None) -> Path:
    """Resuelve y valida la carpeta de artefactos locales que Mesias usara como motor."""
    candidate = Path(model_path).expanduser().resolve(
    ) if model_path else DEFAULT_MODEL_DIR.resolve()
    if not candidate.exists():
        raise FileNotFoundError(
            f"No se encontro la carpeta del modelo: {candidate}")
    if not candidate.is_dir():
        raise NotADirectoryError(
            f"La ruta del modelo no es una carpeta: {candidate}")

    missing = [filename for filename in REQUIRED_CONFIG_FILES if not (
        candidate / filename).exists()]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            f"Faltan artefactos del modelo en {candidate}: {joined}")
    if not any((candidate / filename).exists() for filename in TOKENIZER_FILE_CANDIDATES):
        raise FileNotFoundError(
            "No se encontro un tokenizer compatible. Se esperaba alguno de: "
            + ", ".join(TOKENIZER_FILE_CANDIDATES)
        )
    if not any((candidate / filename).exists() for filename in WEIGHT_FILE_CANDIDATES):
        raise FileNotFoundError(
            "No se encontro un archivo de pesos compatible. Se esperaba alguno de: "
            + ", ".join(WEIGHT_FILE_CANDIDATES)
        )
    return candidate


def infer_device() -> str:
    """Infiere el dispositivo de ejecucion mas razonable para Mesias."""
    torch = lazy_import_torch()
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def infer_torch_dtype(device: Optional[str] = None) -> Any:
    """Devuelve el dtype recomendado para Mesias segun el dispositivo objetivo."""
    torch = lazy_import_torch()
    resolved_device = device or infer_device()

    if resolved_device == "cuda":
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    if resolved_device == "mps":
        return torch.float16
    return torch.float32


def load_qwen25_3b_instruct(
        model_path: Optional[Union[str, Path]] = None,
        *,
        device: Optional[str] = None,
        torch_dtype: Optional[Any] = None,
        use_fast_tokenizer: bool = False,
        lora_adapter_path: Optional[Union[str, Path]] = None,
        merge_lora: bool = False,
        tokenizer_kwargs: Optional[Mapping[str, Any]] = None,
        model_kwargs: Optional[Mapping[str, Any]] = None,
) -> ModelArtifacts:
    """Carga en Mesias un modelo causal local y su tokenizer compatible.

    El loader esta validado sobre Qwen2.5-3B-Instruct, pero tambien acepta
    otros motores locales compatibles con Hugging Face si exponen artefactos
    de tokenizer y pesos reconocibles por Mesias.
    """
    torch = lazy_import_torch()
    auto_model_cls, auto_tokenizer_cls = lazy_import_transformers_for_inference()

    resolved_model_path = resolve_model_path(model_path)
    resolved_device = device or infer_device()
    resolved_dtype = torch_dtype or infer_torch_dtype(resolved_device)

    tokenizer_options: Dict[str, Any] = {
        "use_fast": use_fast_tokenizer,
        "padding_side": "left",
    }
    if tokenizer_kwargs:
        tokenizer_options.update(dict(tokenizer_kwargs))

    tokenizer = auto_tokenizer_cls.from_pretrained(
        str(resolved_model_path),
        local_files_only=True,
        **tokenizer_options,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    resolved_model_kwargs: Dict[str, Any] = {
        "local_files_only": True,
        "low_cpu_mem_usage": True,
        "dtype": resolved_dtype,
    }
    if resolved_device == "cuda":
        resolved_model_kwargs["device_map"] = "auto"
    if model_kwargs:
        resolved_model_kwargs.update(dict(model_kwargs))

    model = auto_model_cls.from_pretrained(
        str(resolved_model_path), **resolved_model_kwargs)

    if resolved_device != "cuda":
        model = model.to(resolved_device)

    if lora_adapter_path:
        model = _load_lora_adapter(
            model=model,
            adapter_path=lora_adapter_path,
            merge_lora=merge_lora,
        )

    model.eval()
    return ModelArtifacts(
        model=model,
        tokenizer=tokenizer,
        model_path=resolved_model_path,
        device=resolved_device,
    )


def _load_lora_adapter(model: Any, adapter_path: Union[str, Path], merge_lora: bool) -> Any:
    """Carga un adaptador LoRA sobre el motor local de Mesias."""
    adapter_dir = Path(adapter_path).expanduser().resolve()
    if not adapter_dir.exists():
        raise FileNotFoundError(
            f"No se encontro el adaptador LoRA: {adapter_dir}")

    adapted_model = lazy_import_peft()["PeftModel"].from_pretrained(
        model, str(adapter_dir))
    if merge_lora:
        return adapted_model.merge_and_unload()
    return adapted_model


def build_chat_inputs(
        tokenizer: Any,
        messages: List[Dict[str, str]],
        *,
        add_generation_prompt: bool = True,
        return_tensors: str = "pt",
) -> Any:
    """Aplica el chat template del tokenizer para producir la entrada de Mesias."""
    return tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=add_generation_prompt,
        return_tensors=return_tensors,
    )


__all__ = [
    "DEFAULT_MODEL_DIR",
    "ModelArtifacts",
    "build_chat_inputs",
    "infer_device",
    "infer_torch_dtype",
    "load_qwen25_3b_instruct",
    "resolve_model_path",
]
