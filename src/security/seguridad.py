from __future__ import annotations

"""Filtros basicos de seguridad y saneamiento textual para Mesias."""

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


DEFAULT_BLOCK_PATTERNS: Dict[str, str] = {
    "prompt_injection": r"ignore\s+previous\s+instructions|system\s+prompt|developer\s+message",
    "credential_request": r"api[_\s-]?key|token|password|secret|credenciales",
    "malware_intent": r"keylogger|ransomware|steal\s+cookies|exfiltrat|payload",
}

DEFAULT_REDACTION_PATTERNS: Dict[str, str] = {
    "openai_key": r"sk-[A-Za-z0-9]{20,}",
    "hf_token": r"hf_[A-Za-z0-9]{20,}",
    "aws_key": r"AKIA[0-9A-Z]{16}",
}


@dataclass
class SecurityCheckResult:
    """Resultado de una validacion o sanitizacion de seguridad en Mesias."""
    allowed: bool
    sanitized_text: str
    matched_rules: List[str] = field(default_factory=list)
    redactions: List[str] = field(default_factory=list)


class GuardiaSeguridad:
    """Filtros ligeros para prompts, mensajes y texto de salida de Mesias."""

    def __init__(
            self,
            blocked_patterns: Optional[Mapping[str, str]] = None,
            redaction_patterns: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.blocked_patterns = dict(
            blocked_patterns or DEFAULT_BLOCK_PATTERNS)
        self.redaction_patterns = dict(
            redaction_patterns or DEFAULT_REDACTION_PATTERNS)

    def sanitize_text(self, text: str) -> SecurityCheckResult:
        """Redacta secretos y elimina caracteres de control del texto para Mesias."""
        sanitized = self._strip_control_chars(text)
        redactions: List[str] = []
        for name, pattern in self.redaction_patterns.items():
            updated = re.sub(pattern, "[REDACTED]",
                             sanitized, flags=re.IGNORECASE)
            if updated != sanitized:
                redactions.append(name)
                sanitized = updated
        return SecurityCheckResult(
            allowed=True,
            sanitized_text=sanitized,
            matched_rules=[],
            redactions=redactions,
        )

    def validate_text(self, text: str) -> SecurityCheckResult:
        """Valida un texto segun reglas de bloqueo y saneamiento de Mesias."""
        sanitized_result = self.sanitize_text(text)
        matched_rules = [
            name for name, pattern in self.blocked_patterns.items()
            if re.search(pattern, sanitized_result.sanitized_text, flags=re.IGNORECASE)
        ]
        return SecurityCheckResult(
            allowed=not matched_rules,
            sanitized_text=sanitized_result.sanitized_text,
            matched_rules=matched_rules,
            redactions=sanitized_result.redactions,
        )

    def validate_messages(self, messages: Sequence[Mapping[str, str]]) -> SecurityCheckResult:
        """Valida varios mensajes concatenados como una sola entrada de Mesias."""
        joined = "\n".join(str(message.get("content", ""))
                           for message in messages)
        return self.validate_text(joined)

    def filter_messages(self, messages: Sequence[Mapping[str, str]]) -> List[Dict[str, str]]:
        """Elimina mensajes bloqueados y sanea los permitidos antes de usarlos en Mesias."""
        filtered_messages: List[Dict[str, str]] = []
        for message in messages:
            result = self.validate_text(str(message.get("content", "")))
            if not result.allowed:
                continue
            filtered_messages.append(
                {
                    "role": str(message.get("role", "user")),
                    "content": result.sanitized_text,
                }
            )
        return filtered_messages

    def ensure_safe(self, text: str) -> str:
        """Garantiza que un texto es aceptable para Mesias o lanza una excepcion."""
        result = self.validate_text(text)
        if not result.allowed:
            blocked = ", ".join(result.matched_rules)
            raise ValueError(f"Contenido bloqueado por seguridad: {blocked}")
        return result.sanitized_text

    @staticmethod
    def _strip_control_chars(text: str) -> str:
        return "".join(character for character in text if character.isprintable() or character in "\n\t\r")


def sanitize_training_examples(examples: Iterable[Mapping[str, str]]) -> List[Dict[str, str]]:
    """Limpia ejemplos prompt/response antes de preparar datasets de Mesias."""
    guard = GuardiaSeguridad()
    sanitized_examples: List[Dict[str, str]] = []
    for example in examples:
        prompt_result = guard.validate_text(str(example.get("prompt", "")))
        response_result = guard.sanitize_text(str(example.get("response", "")))
        if not prompt_result.allowed:
            continue
        sanitized_examples.append(
            {
                "prompt": prompt_result.sanitized_text,
                "response": response_result.sanitized_text,
            }
        )
    return sanitized_examples


__all__ = [
    "DEFAULT_BLOCK_PATTERNS",
    "DEFAULT_REDACTION_PATTERNS",
    "GuardiaSeguridad",
    "SecurityCheckResult",
    "sanitize_training_examples",
]
