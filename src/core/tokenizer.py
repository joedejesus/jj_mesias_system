from __future__ import annotations

"""Tokenizer local y helpers de chat para Mesias."""

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .model_loader import build_chat_inputs, resolve_model_path


def _lazy_import_transformers() -> Any:
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise ImportError(
            "Transformers no esta instalado. Instala 'transformers' para usar el tokenizer de Qwen2.5-3B-Instruct."
        ) from exc
    return AutoTokenizer


@dataclass
class TokenizerArtifacts:
    """Tokenizer y ruta de modelo resuelta."""
    tokenizer: Any
    model_path: Any


def load_qwen25_tokenizer(
        model_path: Optional[Union[str, Any]] = None,
        *,
        use_fast: bool = False,
        padding_side: str = "left",
        truncation_side: str = "left",
        extra_kwargs: Optional[Mapping[str, Any]] = None,
) -> TokenizerArtifacts:
    """Carga el tokenizer local."""
    auto_tokenizer_cls = _lazy_import_transformers()
    resolved_model_path = resolve_model_path(model_path)

    tokenizer_options: Dict[str, Any] = {
        "use_fast": use_fast,
        "padding_side": padding_side,
        "truncation_side": truncation_side,
    }
    if extra_kwargs:
        tokenizer_options.update(dict(extra_kwargs))

    tokenizer = auto_tokenizer_cls.from_pretrained(
        str(resolved_model_path),
        local_files_only=True,
        **tokenizer_options,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return TokenizerArtifacts(tokenizer=tokenizer, model_path=resolved_model_path)


class Qwen25Tokenizer:
    """Adaptador ligero del tokenizer local."""

    def __init__(
            self,
            model_path: Optional[Union[str, Any]] = None,
            *,
            use_fast: bool = False,
            padding_side: str = "left",
            truncation_side: str = "left",
            extra_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        artifacts = load_qwen25_tokenizer(
            model_path=model_path,
            use_fast=use_fast,
            padding_side=padding_side,
            truncation_side=truncation_side,
            extra_kwargs=extra_kwargs,
        )
        self.tokenizer = artifacts.tokenizer
        self.model_path = artifacts.model_path

    def encode(
            self,
            text: str,
            *,
            return_tensors: Optional[str] = None,
            add_special_tokens: bool = True,
            **kwargs: Any,
    ) -> Any:
        """Tokeniza texto plano."""
        return self.tokenizer(
            text,
            return_tensors=return_tensors,
            add_special_tokens=add_special_tokens,
            **kwargs,
        )

    def decode(
            self,
            token_ids: Sequence[int],
            *,
            skip_special_tokens: bool = True,
            **kwargs: Any,
    ) -> str:
        """Decodifica ids de token."""
        return self.tokenizer.decode(
            token_ids,
            skip_special_tokens=skip_special_tokens,
            **kwargs,
        )

    def batch_decode(
            self,
            sequences: Sequence[Sequence[int]],
            *,
            skip_special_tokens: bool = True,
            **kwargs: Any,
    ) -> List[str]:
        """Decodifica varios lotes."""
        return self.tokenizer.batch_decode(
            sequences,
            skip_special_tokens=skip_special_tokens,
            **kwargs,
        )

    def format_chat(
            self,
            messages: List[Dict[str, str]],
            *,
            add_generation_prompt: bool = True,
            return_tensors: Optional[str] = None,
    ) -> Any:
        """Formatea una conversacion."""
        if return_tensors is None:
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=add_generation_prompt,
            )

        return build_chat_inputs(
            self.tokenizer,
            messages,
            add_generation_prompt=add_generation_prompt,
            return_tensors=return_tensors,
        )

    def tokenize_chat(
            self,
            messages: List[Dict[str, str]],
            *,
            add_generation_prompt: bool = True,
            return_tensors: str = "pt",
    ) -> Any:
        """Convierte chat en tensores listos para inferencia."""
        return build_chat_inputs(
            self.tokenizer,
            messages,
            add_generation_prompt=add_generation_prompt,
            return_tensors=return_tensors,
        )

    def get_vocab_size(self) -> int:
        """Devuelve el tamano del vocabulario."""
        return int(self.tokenizer.vocab_size)


__all__ = [
    "Qwen25Tokenizer",
    "TokenizerArtifacts",
    "load_qwen25_tokenizer",
]
