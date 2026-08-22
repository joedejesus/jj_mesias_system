from __future__ import annotations

"""Helpers de razonamiento guiado construidos sobre la fachada Mesias."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence

from ..interfaces.roles import get_system_prompt
from ..memory.memoria_chat import MemoriaChat
from ..mesias import Mesias, MesiasResponse


DEFAULT_REASONING_ROLE = "analista"


@dataclass
class ReasoningRequest:
    """Peticion de razonamiento estructurado que puede resolver Mesias."""
    question: str
    context: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    role: str = DEFAULT_REASONING_ROLE
    max_steps: int = 5


@dataclass
class ReasoningResult:
    """Resultado de un flujo de razonamiento ejecutado por Mesias."""
    response: MesiasResponse
    prompt: str
    role: str


class Razonador:
    """Construye prompts de analisis estructurado sobre el modelo Mesias."""

    def __init__(
            self,
            mesias: Optional[Mesias] = None,
            *,
            role: str = DEFAULT_REASONING_ROLE,
            memoria_chat: Optional[MemoriaChat] = None,
    ) -> None:
        self.role = role
        self.mesias = mesias or Mesias(system_prompt=get_system_prompt(role))
        self.memoria_chat = memoria_chat

    def _system_prompt(self) -> str:
        return get_system_prompt(self.role)

    @staticmethod
    def _clean_constraints(constraints: Optional[Sequence[str]]) -> List[str]:
        if not constraints:
            return []
        return [item.strip() for item in constraints if item.strip()]

    def _run_prompt(self, prompt: str, remember: bool, **generate_kwargs: Any) -> MesiasResponse:
        if self.memoria_chat is not None:
            self.memoria_chat.role = self.role
            self.memoria_chat.system_prompt = self._system_prompt()
            return self.memoria_chat.generate_reply(
                self.mesias,
                prompt,
                remember_user_message=remember,
                remember_reply=remember,
                **generate_kwargs,
            )
        return self.mesias.generate(
            prompt,
            system_prompt=self._system_prompt(),
            **generate_kwargs,
        )

    def build_reasoning_prompt(
            self,
            question: str,
            *,
            context: Optional[str] = None,
            constraints: Optional[Sequence[str]] = None,
            max_steps: int = 5,
    ) -> str:
        """Crea el prompt estructurado que se enviara a Mesias para razonar."""
        parts = [
            "Analiza la siguiente consulta de forma estructurada.",
            f"Consulta: {question.strip()}",
            f"Numero maximo de pasos: {max(1, max_steps)}.",
            "Responde en dos secciones: Analisis y Respuesta final.",
        ]
        if context:
            parts.append(f"Contexto adicional: {context.strip()}")
        clean_constraints = self._clean_constraints(constraints)
        if clean_constraints:
            parts.append("Restricciones:")
            parts.extend(f"- {item}" for item in clean_constraints)
        return "\n".join(parts)

    def reason(
            self,
            question: str,
            *,
            context: Optional[str] = None,
            constraints: Optional[Sequence[str]] = None,
            max_steps: int = 5,
            remember: bool = False,
            **generate_kwargs: Any,
    ) -> ReasoningResult:
        """Pide a Mesias una respuesta razonada y la devuelve con metadatos utiles."""
        prompt = self.build_reasoning_prompt(
            question,
            context=context,
            constraints=constraints,
            max_steps=max_steps,
        )
        response = self._run_prompt(prompt, remember, **generate_kwargs)

        return ReasoningResult(response=response, prompt=prompt, role=self.role)

    def explain_messages(self, messages: Sequence[Mapping[str, str]], **generate_kwargs: Any) -> ReasoningResult:
        """Pide a Mesias que explique y resuma una conversacion ya existente."""
        prompt = (
            "Explica la conversacion dada, identifica el objetivo del usuario, resume el contexto y "
            "propone la siguiente accion mas razonable.\n\n"
            f"Mensajes: {list(messages)}"
        )
        response = self._run_prompt(prompt, False, **generate_kwargs)
        return ReasoningResult(response=response, prompt=prompt, role=self.role)


__all__ = [
    "DEFAULT_REASONING_ROLE",
    "Razonador",
    "ReasoningRequest",
    "ReasoningResult",
]
