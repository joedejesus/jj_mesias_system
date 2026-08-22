from __future__ import annotations

"""Memoria persistente en JSON para recuerdos simples de Mesias."""

import base64
import json
import zlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4

from ..core.paths import DEFAULT_MEMORY_PATH


@dataclass
class MemoryEntry:
    """Entrada de memoria persistente almacenada por Mesias."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat())


_PACKED_TEXT_ENCODING = "zb64"


def _pack_text_for_storage(text: str) -> Any:
    normalized_text = text.strip()
    raw_bytes = normalized_text.encode("utf-8")
    packed_bytes = zlib.compress(raw_bytes, level=9)
    payload = {
        "e": _PACKED_TEXT_ENCODING,
        "d": base64.b64encode(packed_bytes).decode("ascii"),
    }
    packed_size = len(json.dumps(
        payload, separators=(",", ":"), ensure_ascii=True))
    plain_size = len(json.dumps(normalized_text, ensure_ascii=False))
    return payload if packed_size < plain_size else normalized_text


def _unpack_text_from_storage(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, Mapping):
        return str(value or "")
    if value.get("e") != _PACKED_TEXT_ENCODING:
        return str(value.get("d", "") or "")

    packed_data = str(value.get("d", ""))
    if not packed_data:
        return ""
    raw_bytes = base64.b64decode(packed_data.encode("ascii"))
    return zlib.decompress(raw_bytes).decode("utf-8")


class Memoria:
    """Almacen simple en JSON para recuerdos persistentes de Mesias."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = Path(
            storage_path) if storage_path else DEFAULT_MEMORY_PATH
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: List[MemoryEntry] = []
        self.load()

    def load(self) -> List[MemoryEntry]:
        """Carga las entradas persistidas de Mesias desde disco."""
        if not self.storage_path.exists():
            self._entries = []
            self.save()
            return self._entries

        raw_data = self.storage_path.read_text(encoding="utf-8-sig").strip()
        if not raw_data:
            self._entries = []
            return self._entries

        try:
            payload = json.loads(raw_data)
        except json.JSONDecodeError:
            self._quarantine_corrupt_storage()
            self._entries = []
            self.save()
            return self._entries
        self._entries = [self._deserialize_entry(item) for item in payload]
        return list(self._entries)

    def save(self) -> None:
        """Guarda en disco el estado actual de la memoria de Mesias."""
        payload = [self._serialize_entry(entry) for entry in self._entries]
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> MemoryEntry:
        """Crea y persiste un nuevo recuerdo utilizable por Mesias."""
        normalized_content = content.strip()
        if not normalized_content:
            raise ValueError("El contenido de memoria no puede estar vacio.")

        entry = MemoryEntry(
            id=str(uuid4()),
            content=normalized_content,
            metadata=dict(metadata or {}),
        )
        self._entries.append(entry)
        self.save()
        return entry

    def list_all(self) -> List[MemoryEntry]:
        """Devuelve todas las entradas guardadas en la memoria de Mesias."""
        return list(self._entries)

    def list_for_speaker(self, speaker_id: Optional[str], limit: Optional[int] = None) -> List[MemoryEntry]:
        """Devuelve recuerdos generales y del hablante indicado."""
        visible_entries = [
            entry for entry in self._entries
            if self._matches_speaker(entry, speaker_id)
        ]
        if limit is None:
            return visible_entries
        return visible_entries[-limit:]

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Busca una entrada concreta de memoria por identificador."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Busca recuerdos relevantes en la memoria persistente de Mesias."""
        normalized_query = query.strip().lower()
        if not normalized_query:
            return self.list_all()[:limit]

        results = [
            entry for entry in self._entries
            if normalized_query in entry.content.lower()
            or any(normalized_query in str(value).lower() for value in entry.metadata.values())
        ]
        return results[:limit]

    def recent(self, limit: int = 10) -> List[MemoryEntry]:
        """Devuelve los recuerdos mas recientes guardados por Mesias."""
        return list(self._entries[-limit:])

    def recent_for_speaker(self, speaker_id: Optional[str], limit: int = 10) -> List[MemoryEntry]:
        """Devuelve recuerdos recientes aplicables al hablante actual."""
        return self.list_for_speaker(speaker_id, limit=limit)

    def delete(self, entry_id: str) -> bool:
        """Elimina una entrada de memoria y devuelve si hubo cambios."""
        original_size = len(self._entries)
        self._entries = [
            entry for entry in self._entries if entry.id != entry_id]
        changed = len(self._entries) != original_size
        if changed:
            self.save()
        return changed

    def clear(self) -> None:
        """Vacia por completo la memoria persistente de Mesias."""
        self._entries = []
        self.save()

    def clear_for_speaker(self, speaker_id: Optional[str]) -> None:
        """Elimina solo la memoria asociada a un hablante concreto."""
        if not speaker_id:
            self.clear()
            return
        self._entries = [
            entry for entry in self._entries
            if str(entry.metadata.get("speaker_id", "")).strip() != speaker_id
        ]
        self.save()

    def stats(self) -> Dict[str, int]:
        """Resume el volumen actual de memoria persistente para inspeccion rapida."""
        scoped_entries = sum(
            1 for entry in self._entries if str(entry.metadata.get("speaker_id", "")).strip()
        )
        return {
            "entries": len(self._entries),
            "speaker_scoped_entries": scoped_entries,
            "global_entries": len(self._entries) - scoped_entries,
        }

    def to_messages(self, limit: int = 10, speaker_id: Optional[str] = None) -> List[Dict[str, str]]:
        """Convierte recuerdos recientes a mensajes de sistema inyectables en Mesias."""
        messages: List[Dict[str, str]] = []
        for entry in self.recent_for_speaker(speaker_id, limit=limit):
            messages.append(
                {
                    "role": "system",
                    "content": f"Memoria relevante: {entry.content}",
                }
            )
        return messages

    @staticmethod
    def _matches_speaker(entry: MemoryEntry, speaker_id: Optional[str]) -> bool:
        if not speaker_id:
            return True
        entry_speaker = str(entry.metadata.get("speaker_id", "")).strip()
        return not entry_speaker or entry_speaker == speaker_id

    @staticmethod
    def _deserialize_entry(item: Mapping[str, Any]) -> MemoryEntry:
        metadata = item.get("metadata", item.get("m", {})) or {}
        return MemoryEntry(
            id=str(item.get("id", "")),
            content=_unpack_text_from_storage(
                item.get("content", item.get("c", ""))),
            metadata=dict(metadata),
            created_at=str(item.get("created_at", item.get(
                "t", datetime.now(timezone.utc).isoformat()))),
        )

    @staticmethod
    def _serialize_entry(entry: MemoryEntry) -> Dict[str, Any]:
        payload = asdict(entry)
        return {
            "id": payload["id"],
            "c": _pack_text_for_storage(payload["content"]),
            "m": payload["metadata"],
            "t": payload["created_at"],
        }

    def _quarantine_corrupt_storage(self) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup_path = self.storage_path.with_name(
            f"{self.storage_path.name}.corrupt.{timestamp}"
        )
        self.storage_path.replace(backup_path)


__all__ = ["DEFAULT_MEMORY_PATH", "Memoria", "MemoryEntry"]
