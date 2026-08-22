from __future__ import annotations

"""Preparacion de datasets conversacionales compatibles con Mesias."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

from ..core.tokenizer import Qwen25Tokenizer, load_qwen25_tokenizer
from ..interfaces.roles import get_system_prompt
from ..security.seguridad import sanitize_training_examples


@dataclass
class ChatExample:
    """Ejemplo de conversacion ya normalizado al formato de Mesias."""
    messages: List[Dict[str, str]]


@dataclass
class TokenizedChatExample:
    """Ejemplo conversacional tokenizado para entrenamiento supervisado en Mesias."""
    input_ids: List[int]
    attention_mask: List[int]
    labels: List[int]
    text: str
    messages: List[Dict[str, str]]


def load_jsonl_examples(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Carga ejemplos JSONL desde disco para entrenamiento o pruebas de Mesias."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el dataset: {path}")
    rows: List[Dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def normalize_example(
        example: Mapping[str, Any],
        *,
        default_role: str = "general",
) -> ChatExample:
    """Normaliza un ejemplo heterogeneo al formato conversacional interno de Mesias."""
    if "messages" in example:
        normalized_messages = [
            {
                "role": str(message.get("role", "user")),
                "content": str(message.get("content", "")).strip(),
            }
            for message in example.get("messages", [])
            if str(message.get("content", "")).strip()
        ]
        return ChatExample(messages=normalized_messages)

    prompt = str(example.get("prompt", "")).strip()
    response = str(example.get(
        "response", example.get("completion", ""))).strip()
    system_prompt = str(example.get(
        "system_prompt", get_system_prompt(default_role))).strip()

    if not prompt or not response:
        raise ValueError(
            "Cada ejemplo debe incluir 'messages' o bien 'prompt' y 'response'.")

    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    messages.append({"role": "assistant", "content": response})
    return ChatExample(messages=messages)


def format_chat_example(
        example: Mapping[str, Any],
        *,
        tokenizer: Optional[Any] = None,
        model_path: Optional[Union[str, Path]] = None,
        default_role: str = "general",
) -> str:
    """Renderiza un ejemplo al chat template textual que usa Mesias."""
    chat_example = normalize_example(example, default_role=default_role)
    resolved_tokenizer = tokenizer or load_qwen25_tokenizer(
        model_path=model_path).tokenizer
    return resolved_tokenizer.apply_chat_template(
        chat_example.messages,
        tokenize=False,
        add_generation_prompt=False,
    )


def tokenize_chat_example(
        example: Mapping[str, Any],
        *,
        tokenizer: Optional[Any] = None,
        model_path: Optional[Union[str, Path]] = None,
        max_length: int = 2048,
        default_role: str = "general",
) -> TokenizedChatExample:
    """Tokeniza un ejemplo de entrenamiento usando el tokenizer activo de Mesias."""
    resolved_tokenizer = tokenizer or load_qwen25_tokenizer(
        model_path=model_path).tokenizer
    chat_example = normalize_example(example, default_role=default_role)
    rendered_text = resolved_tokenizer.apply_chat_template(
        chat_example.messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    encoded = resolved_tokenizer(
        rendered_text,
        truncation=True,
        max_length=max_length,
        padding=False,
    )
    input_ids = list(encoded["input_ids"])
    attention_mask = list(encoded["attention_mask"])
    return TokenizedChatExample(
        input_ids=input_ids,
        attention_mask=attention_mask,
        labels=list(input_ids),
        text=rendered_text,
        messages=chat_example.messages,
    )


def prepare_sft_dataset(
        examples: Iterable[Mapping[str, Any]],
        *,
        tokenizer: Optional[Any] = None,
        model_path: Optional[Union[str, Path]] = None,
        max_length: int = 2048,
        default_role: str = "general",
        sanitize: bool = True,
) -> List[Dict[str, Any]]:
    """Prepara un dataset SFT listo para entrenamiento LoRA dentro de Mesias."""
    raw_examples = list(examples)
    prepared_examples: List[Mapping[str, Any]]
    if sanitize:
        prompt_response_examples = []
        passthrough_examples = []
        for example in raw_examples:
            if "messages" in example:
                passthrough_examples.append(example)
            else:
                prompt_response_examples.append(example)
        sanitized_prompt_response = sanitize_training_examples(
            prompt_response_examples)
        prepared_examples = [*passthrough_examples, *sanitized_prompt_response]
    else:
        prepared_examples = raw_examples

    resolved_tokenizer = tokenizer or load_qwen25_tokenizer(
        model_path=model_path).tokenizer
    return [
        tokenize_chat_example(
            example,
            tokenizer=resolved_tokenizer,
            max_length=max_length,
            default_role=default_role,
        ).__dict__
        for example in prepared_examples
    ]


def build_chat_dataset_from_pairs(
        pairs: Sequence[Mapping[str, str]],
        *,
        role: str = "general",
) -> List[Dict[str, Any]]:
    """Convierte pares prompt/response simples en ejemplos compatibles con Mesias."""
    system_prompt = get_system_prompt(role)
    dataset: List[Dict[str, Any]] = []
    for pair in pairs:
        prompt = str(pair.get("prompt", "")).strip()
        response = str(pair.get("response", "")).strip()
        if not prompt or not response:
            continue
        dataset.append(
            {
                "system_prompt": system_prompt,
                "prompt": prompt,
                "response": response,
            }
        )
    return dataset


__all__ = [
    "ChatExample",
    "Qwen25Tokenizer",
    "TokenizedChatExample",
    "build_chat_dataset_from_pairs",
    "format_chat_example",
    "load_jsonl_examples",
    "normalize_example",
    "prepare_sft_dataset",
    "tokenize_chat_example",
]
