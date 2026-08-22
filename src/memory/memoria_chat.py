from __future__ import annotations

"""Historial conversacional persistente y utilidades de memoria para Mesias."""

import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence

try:
    from ..core.paths import DEFAULT_CHAT_MEMORY_PATH
    from ..interfaces.roles import DEFAULT_ROLE, get_system_prompt
    from .memoria import Memoria, _pack_text_for_storage, _unpack_text_from_storage
except ImportError:
    from core.paths import DEFAULT_CHAT_MEMORY_PATH
    from interfaces.roles import DEFAULT_ROLE, get_system_prompt
    from memory.memoria import Memoria, _pack_text_for_storage, _unpack_text_from_storage

if TYPE_CHECKING:
    try:
        from ..mesias import Mesias, MesiasResponse
    except ImportError:
        from mesias import Mesias, MesiasResponse
else:
    Mesias = Any
    MesiasResponse = Any


@dataclass
class ChatTurn:
    """Turno de conversacion persistido por la memoria de chat de Mesias."""
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoriaChat:
    """Gestiona historial conversacional y memoria persistente para Mesias."""

    def __init__(
            self,
            memoria: Optional[Memoria] = None,
            *,
            role: str = DEFAULT_ROLE,
            system_prompt: Optional[str] = None,
            storage_path: Optional[Path] = None,
            speaker_id: Optional[str] = None,
    ) -> None:
        self.memoria = memoria or Memoria()
        self.role = role
        self.system_prompt = system_prompt or get_system_prompt(role)
        self.speaker_id = speaker_id
        self._history: List[ChatTurn] = []
        self.storage_path = Path(
            storage_path) if storage_path else DEFAULT_CHAT_MEMORY_PATH
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatTurn:
        """Agrega un turno arbitrario al historial persistente de Mesias."""
        normalized_metadata = dict(metadata or {})
        if self.speaker_id and "speaker_id" not in normalized_metadata:
            normalized_metadata["speaker_id"] = self.speaker_id
        message = ChatTurn(
            role=role,
            content=content.strip(),
            metadata=normalized_metadata,
        )
        if not message.content:
            raise ValueError("El mensaje no puede estar vacio.")
        self._history.append(message)
        self.save()
        return message

    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatTurn:
        """Agrega un turno de usuario al historial de Mesias."""
        return self.add_message("user", content, metadata)

    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatTurn:
        """Agrega un turno del asistente Mesias al historial."""
        return self.add_message("assistant", content, metadata)

    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatTurn:
        """Agrega un turno de sistema al historial de Mesias."""
        return self.add_message("system", content, metadata)

    def history(self) -> List[ChatTurn]:
        """Devuelve una copia del historial de chat almacenado por Mesias."""
        return list(self._history_for_current_speaker())

    def clear(self) -> None:
        """Borra el historial conversacional persistido de Mesias."""
        if not self.speaker_id:
            self._history = []
        else:
            self._history = [
                turn for turn in self._history
                if str(turn.metadata.get("speaker_id", "")).strip() != self.speaker_id
            ]
        self.save()

    def load(self) -> List[ChatTurn]:
        """Carga desde disco el historial conversacional de Mesias."""
        if not self.storage_path.exists():
            self._history = []
            self.save()
            return []
        raw_data = self.storage_path.read_text(encoding="utf-8-sig").strip()
        if not raw_data:
            self._history = []
            return []
        try:
            payload = json.loads(raw_data)
        except json.JSONDecodeError:
            self._quarantine_corrupt_storage()
            self._history = []
            self.save()
            return []
        self._history = [self._deserialize_turn(item) for item in payload]
        return self.history()

    def save(self) -> None:
        """Guarda en disco el historial conversacional actual de Mesias."""
        payload = [self._serialize_turn(turn) for turn in self._history]
        self.storage_path.write_text(json.dumps(
            payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def to_messages(self, include_memory: bool = True, memory_limit: int = 5) -> List[Dict[str, str]]:
        """Convierte memoria e historial al formato de mensajes que consume Mesias."""
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if include_memory:
            messages.extend(self.memoria.to_messages(
                limit=memory_limit,
                speaker_id=self.speaker_id,
            ))
        messages.extend({"role": turn.role, "content": turn.content}
                        for turn in self._history_for_current_speaker())
        return messages

    def remember(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Guarda un recuerdo nuevo en la memoria persistente asociada a Mesias."""
        normalized_metadata = dict(metadata or {})
        if self.speaker_id and "speaker_id" not in normalized_metadata:
            normalized_metadata["speaker_id"] = self.speaker_id
        self.memoria.add(content, metadata=normalized_metadata)

    def generate_reply(
            self,
            mesias: Mesias,
            prompt: str,
            *,
            remember_user_message: bool = False,
            remember_reply: bool = False,
            remember_profile: bool = False,
            memory_limit: int = 5,
            web_urls: Optional[Sequence[str]] = None,
            **generate_kwargs: Any,
    ) -> MesiasResponse:
        """Genera una respuesta con Mesias, persiste el turno y opcionalmente memoriza."""
        self.add_user_message(
            prompt,
            metadata=_build_memory_metadata(
                "chat_user", self.role, speaker_id=self.speaker_id),
        )
        messages = self.to_messages(
            include_memory=True, memory_limit=memory_limit)
        resolved_web_urls = list(web_urls or [])
        if not resolved_web_urls and hasattr(mesias, "should_search_web") and mesias.should_search_web(prompt):
            resolved_web_urls = list(
                getattr(mesias, "discover_web_urls", lambda _prompt: [])(prompt) or [])
        if resolved_web_urls:
            try:
                web_context = mesias.fetch_web_context(
                    resolved_web_urls, include_errors=False)
            except Exception:
                web_context = None
            if web_context is not None and web_context.documents:
                messages[-1] = {
                    "role": "user",
                    "content": mesias._build_web_augmented_prompt(prompt, web_context.context),
                }

        response = mesias.chat(messages, **generate_kwargs)
        self.add_assistant_message(
            response.text,
            metadata=_build_memory_metadata(
                "chat_assistant", self.role, speaker_id=self.speaker_id),
        )

        if remember_user_message:
            self.remember(
                prompt,
                metadata=_build_memory_metadata(
                    "user", self.role, speaker_id=self.speaker_id),
            )
        if remember_reply:
            self.remember(
                response.text,
                metadata=_build_memory_metadata(
                    "assistant", self.role, speaker_id=self.speaker_id),
            )
        if remember_profile:
            self._remember_speaker_facts(prompt)

        return response

    def bootstrap(
            self,
            messages: Sequence[Mapping[str, str]],
            *,
            replace: bool = True,
    ) -> None:
        """Inicializa el historial de Mesias a partir de mensajes ya existentes."""
        new_history: List[ChatTurn] = []
        if not replace:
            new_history.extend(self._history)
        elif self.speaker_id:
            new_history.extend(
                turn for turn in self._history
                if str(turn.metadata.get("speaker_id", "")).strip() != self.speaker_id
            )
        for message in messages:
            role = str(message.get("role", "user"))
            content = str(message.get("content", "")).strip()
            if role == "system":
                self.system_prompt = content or self.system_prompt
                continue
            if content:
                metadata = {}
                if self.speaker_id:
                    metadata["speaker_id"] = self.speaker_id
                new_history.append(
                    ChatTurn(role=role, content=content, metadata=metadata))
        self._history = new_history
        self.save()

    def _history_for_current_speaker(self) -> List[ChatTurn]:
        if not self.speaker_id:
            return list(self._history)
        return [
            turn for turn in self._history
            if str(turn.metadata.get("speaker_id", "")).strip() == self.speaker_id
        ]

    def _remember_speaker_facts(self, prompt: str) -> None:
        existing_contents = {
            entry.content for entry in self.memoria.recent_for_speaker(self.speaker_id, limit=50)
        }
        for fact in _extract_speaker_facts(prompt):
            if fact in existing_contents:
                continue
            self.remember(
                fact,
                metadata=_build_memory_metadata(
                    "speaker_profile", self.role, speaker_id=self.speaker_id),
            )
            existing_contents.add(fact)

    def _quarantine_corrupt_storage(self) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup_path = self.storage_path.with_name(
            f"{self.storage_path.name}.corrupt.{timestamp}"
        )
        self.storage_path.replace(backup_path)

    @staticmethod
    def _turn_to_dict(turn: ChatTurn) -> Dict[str, Any]:
        return {
            "role": turn.role,
            "content": turn.content,
            "metadata": dict(turn.metadata),
        }

    @staticmethod
    def _deserialize_turn(item: Mapping[str, Any]) -> ChatTurn:
        return ChatTurn(
            role=str(item.get("role", item.get("r", "user"))),
            content=_unpack_text_from_storage(
                item.get("content", item.get("c", ""))),
            metadata=dict(item.get("metadata", item.get("m", {})) or {}),
        )

    @staticmethod
    def _serialize_turn(turn: ChatTurn) -> Dict[str, Any]:
        return {
            "r": turn.role,
            "c": _pack_text_for_storage(turn.content),
            "m": dict(turn.metadata),
        }


def _build_memory_metadata(kind: str, role: str, *, speaker_id: Optional[str] = None) -> Dict[str, Any]:
    metadata = {"kind": kind, "role": role}
    if speaker_id:
        metadata["speaker_id"] = speaker_id
    return metadata


def _extract_speaker_facts(prompt: str) -> List[str]:
    facts: List[str] = []
    short_value = r"([^.,;:\n]{2,60}?)(?=\s+y\s+|\s+pero\s+|[.,;:\n]|$)"
    patterns = [
        (rf"\bme llamo\s+{short_value}", "El usuario se llama {value}."),
        (rf"\bmi nombre es\s+{short_value}", "El usuario se llama {value}."),
        (rf"\bsoy de\s+{short_value}", "El usuario es de {value}."),
        (rf"\bvivo en\s+{short_value}", "El usuario vive en {value}."),
        (rf"\btrabajo como\s+{short_value}",
         "El usuario trabaja como {value}."),
        (rf"\bmi trabajo es\s+{short_value}",
         "El trabajo del usuario es {value}."),
        (rf"\bme gusta\s+{short_value}", "Al usuario le gusta {value}."),
        (rf"\bprefiero\s+{short_value}", "El usuario prefiere {value}."),
    ]
    for pattern, template in patterns:
        match = re.search(pattern, prompt, flags=re.IGNORECASE)
        if not match:
            continue
        value = re.sub(r"\s+", " ", match.group(1)).strip(" .,!?")
        if value:
            facts.append(template.format(value=value))
    return facts


__all__ = ["ChatTurn", "DEFAULT_CHAT_MEMORY_PATH", "MemoriaChat"]
