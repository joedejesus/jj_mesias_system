from __future__ import annotations

"""Fachada principal de Mesias para inferencia, diagnostico y contexto web."""

import argparse
import importlib.util
import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

try:
    from .core.lazy_imports import lazy_import_torch
    from .core.model_loader import DEFAULT_MODEL_DIR, ModelArtifacts, load_qwen25_3b_instruct, resolve_model_path
    from .core.paths import DEFAULT_LOG_PATH
    from .interfaces.roles import DEFAULT_ROLE, get_system_prompt
    from .internet.web import DEFAULT_CONNECTIVITY_TEST_URL, WebClient, WebConnectivityStatus, WebDocument, WebFetchError
    from .memory.memoria_chat import MemoriaChat
    from .security.seguridad import GuardiaSeguridad
except ImportError:
    from core.lazy_imports import lazy_import_torch
    from core.model_loader import DEFAULT_MODEL_DIR, ModelArtifacts, load_qwen25_3b_instruct, resolve_model_path
    from core.paths import DEFAULT_LOG_PATH
    from interfaces.roles import DEFAULT_ROLE, get_system_prompt
    from internet.web import DEFAULT_CONNECTIVITY_TEST_URL, WebClient, WebConnectivityStatus, WebDocument, WebFetchError
    from memory.memoria_chat import MemoriaChat
    from security.seguridad import GuardiaSeguridad


DEFAULT_SYSTEM_PROMPT = "Eres Mesias, un asistente util, claro y preciso."
CONSOLE_SPEAKER_ID = "console_local_user"
FACTUAL_QUERY_MARKERS = (
    "hoy",
    "actual",
    "actualmente",
    "internet",
    "web",
    "fecha",
    "hora",
    "habitantes",
    "poblacion",
    "población",
    "precio",
    "cotizacion",
    "cotización",
    "noticia",
    "noticias",
    "clima",
    "temperatura",
    "cuantos",
    "cuántos",
    "cuantas",
    "cuántas",
    "capital",
)
FACTUAL_QUERY_PATTERNS = (
    r"\bque dia es\b",
    r"\bqué dia es\b",
    r"\bque fecha es\b",
    r"\bqué fecha es\b",
    r"\ben que fecha\b",
    r"\ben qué fecha\b",
    r"\bcu[aá]l es la capital\b",
    r"\bcu[aá]ntos habitantes\b",
    r"\bnumero de habitantes\b",
    r"\bn[uú]mero de habitantes\b",
    r"\bprecio de\b",
    r"\bcotizaci[oó]n de\b",
    r"\bclima en\b",
    r"\btemperatura en\b",
)


@dataclass
class MesiasResponse:
    """Respuesta normalizada de Mesias tras una generacion o una llamada de chat."""
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    messages: List[Dict[str, str]]


@dataclass
class WebContextResult:
    """Resultado del enriquecimiento web opcional usado por Mesias."""
    documents: List[WebDocument]
    errors: List[WebFetchError]
    context: str


@dataclass
class RuntimeDiagnostics:
    """Diagnostico operativo resumido de dependencias, modelo y red para Mesias."""
    model_path: str
    model_files_ok: bool
    dependency_status: Dict[str, bool]
    web_connectivity: Optional[WebConnectivityStatus]
    issues: List[str]


def diagnose_runtime(
        model_path: Optional[Union[str, Path]] = None,
        *,
    test_url: str = DEFAULT_CONNECTIVITY_TEST_URL,
        enable_web: bool = True,
        web_timeout: int = 15,
) -> RuntimeDiagnostics:
    """Evalua si Mesias tiene modelo, dependencias y salida web listos para ejecutarse."""
    try:
        resolved_model_path = resolve_model_path(model_path)
        model_files_ok = True
    except (FileNotFoundError, NotADirectoryError):
        resolved_model_path = Path(
            model_path) if model_path else DEFAULT_MODEL_DIR
        model_files_ok = False

    dependency_status = {
        name: importlib.util.find_spec(name) is not None
        for name in ["torch", "transformers", "fastapi", "pydantic", "uvicorn", "gradio", "peft"]
    }
    issues: List[str] = []
    if not model_files_ok:
        issues.append("Faltan artefactos obligatorios del modelo local.")
    missing_dependencies = [
        name for name, is_available in dependency_status.items() if not is_available]
    if missing_dependencies:
        issues.append("Dependencias ausentes: " +
                      ", ".join(missing_dependencies))

    web_connectivity = None
    if enable_web:
        web_connectivity = WebClient(
            timeout=web_timeout).diagnose_connectivity(test_url=test_url)
        if not web_connectivity.dns_ok:
            issues.append("No hay resolucion DNS para acceso web.")
        elif not web_connectivity.http_ok:
            issues.append(
                "La resolucion DNS funciona, pero la salida HTTP/HTTPS fallo.")

    return RuntimeDiagnostics(
        model_path=str(resolved_model_path),
        model_files_ok=model_files_ok,
        dependency_status=dependency_status,
        web_connectivity=web_connectivity,
        issues=issues,
    )


class Mesias:
    """Fachada principal de Mesias para conversar, generar y enriquecer con web."""

    def __init__(
            self,
            model_path: Optional[Union[str, Any]] = None,
            *,
            device: Optional[str] = None,
            torch_dtype: Optional[Any] = None,
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            use_fast_tokenizer: bool = False,
            lora_adapter_path: Optional[Union[str, Any]] = None,
            merge_lora: bool = False,
            tokenizer_kwargs: Optional[Mapping[str, Any]] = None,
            model_kwargs: Optional[Mapping[str, Any]] = None,
            enable_security: bool = True,
            enable_logging: bool = True,
            log_path: Optional[Union[str, Path]] = None,
            enable_web: bool = True,
            web_timeout: int = 15,
    ) -> None:
        """Inicializa Mesias cargando modelo, tokenizer, seguridad, logs y web opcional."""
        artifacts = load_qwen25_3b_instruct(
            model_path=model_path,
            device=device,
            torch_dtype=torch_dtype,
            use_fast_tokenizer=use_fast_tokenizer,
            lora_adapter_path=lora_adapter_path,
            merge_lora=merge_lora,
            tokenizer_kwargs=tokenizer_kwargs,
            model_kwargs=model_kwargs,
        )
        self.artifacts = artifacts
        self.model = artifacts.model
        self.tokenizer = artifacts.tokenizer
        self.model_path = artifacts.model_path
        self.device = artifacts.device
        self.system_prompt = system_prompt
        self.security = GuardiaSeguridad() if enable_security else None
        self.enable_logging = enable_logging
        self.log_path = Path(log_path) if log_path else DEFAULT_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.web_client = WebClient(
            timeout=web_timeout) if enable_web else None

    def build_messages(
            self,
            prompt: str,
            *,
            history: Optional[Sequence[Mapping[str, str]]] = None,
            system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Construye la secuencia de mensajes que Mesias enviara al modelo."""
        messages: List[Dict[str, str]] = []
        resolved_system_prompt = self._sanitize_text(
            system_prompt or self.system_prompt)
        if resolved_system_prompt:
            messages.append(
                {"role": "system", "content": resolved_system_prompt})
        if history:
            for message in history:
                role = str(message.get("role", "user"))
                content = self._sanitize_text(str(message.get("content", "")))
                messages.append({"role": role, "content": content})
        messages.append(
            {"role": "user", "content": self._sanitize_text(prompt)})
        return messages

    def should_search_web(self, prompt: str, urls: Optional[Sequence[str]] = None) -> bool:
        """Decide si conviene buscar apoyo web para una consulta potencialmente factual."""
        if urls:
            return False
        normalized_prompt = prompt.strip().lower()
        if not normalized_prompt:
            return False
        if any(marker in normalized_prompt for marker in FACTUAL_QUERY_MARKERS):
            return True
        return any(
            re.search(pattern, normalized_prompt, flags=re.IGNORECASE)
            for pattern in FACTUAL_QUERY_PATTERNS
        )

    def discover_web_urls(self, prompt: str, max_results: int = 3) -> List[str]:
        """Intenta descubrir fuentes web HTTPS para una consulta cuando la instancia lo permite."""
        if self.web_client is None:
            return []
        try:
            return self.web_client.search(prompt, max_results=max_results)
        except Exception:
            return []

    def chat(
            self,
            messages: Sequence[Mapping[str, str]],
            *,
            max_new_tokens: int = 256,
            do_sample: bool = True,
            temperature: float = 0.7,
            top_p: float = 0.8,
            top_k: int = 20,
            repetition_penalty: float = 1.05,
            add_generation_prompt: bool = True,
            skip_special_tokens: bool = True,
            **generate_kwargs: Any,
    ) -> MesiasResponse:
        """Ejecuta una llamada de chat completa sobre el motor local de Mesias."""
        torch = lazy_import_torch()
        normalized_messages = [
            {"role": str(message.get("role", "user")),
             "content": self._sanitize_text(str(message.get("content", "")))}
            for message in messages
        ]
        try:
            model_inputs = self.tokenizer.apply_chat_template(
                normalized_messages,
                tokenize=True,
                add_generation_prompt=add_generation_prompt,
                return_dict=True,
                return_tensors="pt",
            )
        except TypeError:
            model_inputs = self.tokenizer.apply_chat_template(
                normalized_messages,
                tokenize=True,
                add_generation_prompt=add_generation_prompt,
                return_tensors="pt",
            )
        model_inputs = model_inputs.to(self._get_input_device())

        generation_options: Dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        generation_options.update(generate_kwargs)

        if isinstance(model_inputs, Mapping):
            model_inputs_dict = dict(model_inputs)
            prompt_ids = model_inputs_dict["input_ids"]
            with torch.no_grad():
                output_ids = self.model.generate(
                    **model_inputs_dict,
                    **generation_options,
                )
        else:
            prompt_ids = model_inputs
            with torch.no_grad():
                output_ids = self.model.generate(
                    model_inputs,
                    **generation_options,
                )

        prompt_length = int(prompt_ids.shape[-1])
        generated_ids = output_ids[0][prompt_length:]
        text = self._sanitize_output(self.tokenizer.decode(
            generated_ids, skip_special_tokens=skip_special_tokens).strip()
        )

        if self.enable_logging:
            self._append_log(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "device": self.device,
                    "model_path": str(self.model_path),
                    "messages": normalized_messages,
                    "response": text,
                    "prompt_tokens": prompt_length,
                    "completion_tokens": int(generated_ids.shape[-1]),
                }
            )

        completion_tokens = int(generated_ids.shape[-1])
        return MesiasResponse(
            text=text,
            prompt_tokens=prompt_length,
            completion_tokens=completion_tokens,
            total_tokens=prompt_length + completion_tokens,
            messages=normalized_messages,
        )

    def generate(
            self,
            prompt: str,
            *,
            history: Optional[Sequence[Mapping[str, str]]] = None,
            system_prompt: Optional[str] = None,
            **generate_kwargs: Any,
    ) -> MesiasResponse:
        """Atajo de Mesias para generar a partir de un prompt y un historial opcional."""
        messages = self.build_messages(
            prompt,
            history=history,
            system_prompt=system_prompt,
        )
        return self.chat(messages, **generate_kwargs)

    def fetch_web_context(
            self,
            urls: Sequence[str],
            *,
            max_chars_per_source: int = 1800,
            include_errors: bool = True,
    ) -> WebContextResult:
        """Recupera y resume fuentes web sin romper Mesias si alguna falla."""
        if self.web_client is None:
            raise RuntimeError(
                "El acceso web esta deshabilitado en esta instancia de Mesias.")

        cleaned_urls = [url.strip() for url in urls if url and url.strip()]
        documents, errors = self.web_client.fetch_many_safe(
            cleaned_urls,
            max_chars=max_chars_per_source,
        )
        blocks: List[str] = []
        for document in documents:
            blocks.append(
                f"Fuente: {document.title} ({document.url})\nContenido: {self._sanitize_output(document.content)}"
            )
        if include_errors:
            for error in errors:
                blocks.append(
                    f"Fuente no disponible: {error.url}\nMotivo: {error.error}")
        return WebContextResult(
            documents=documents,
            errors=errors,
            context="\n\n".join(blocks),
        )

    def diagnose_runtime(self, test_url: str = DEFAULT_CONNECTIVITY_TEST_URL) -> RuntimeDiagnostics:
        """Ejecuta el mismo diagnostico global pero desde una instancia concreta de Mesias."""
        return diagnose_runtime(
            model_path=self.model_path,
            test_url=test_url,
            enable_web=self.web_client is not None,
            web_timeout=self.web_client.timeout if self.web_client is not None else 15,
        )

    def generate_with_web(
            self,
            prompt: str,
            *,
            urls: Sequence[str],
            history: Optional[Sequence[Mapping[str, str]]] = None,
            system_prompt: Optional[str] = None,
            max_chars_per_source: int = 1800,
            require_web_success: bool = False,
            **generate_kwargs: Any,
    ) -> MesiasResponse:
        """Genera con Mesias usando contexto web opcional y degradacion segura."""
        web_context = self.fetch_web_context(
            urls,
            max_chars_per_source=max_chars_per_source,
            include_errors=not require_web_success,
        )
        if require_web_success and not web_context.documents:
            raise RuntimeError(
                "No se pudo recuperar ninguna fuente web valida para responder.")

        if not web_context.documents:
            return self.generate(
                prompt,
                history=history,
                system_prompt=system_prompt,
                **generate_kwargs,
            )

        augmented_prompt = self._build_web_augmented_prompt(
            prompt, web_context.context)
        response = self.generate(
            augmented_prompt,
            history=history,
            system_prompt=system_prompt,
            **generate_kwargs,
        )
        return response

    def tokenize_chat(
            self,
            messages: Sequence[Mapping[str, str]],
            *,
            add_generation_prompt: bool = True,
            return_tensors: str = "pt",
    ) -> Any:
        """Tokeniza una conversacion con el chat template activo de Mesias."""
        normalized_messages = [
            {"role": str(message.get("role", "user")),
             "content": str(message.get("content", ""))}
            for message in messages
        ]
        return self.tokenizer.apply_chat_template(
            normalized_messages,
            tokenize=True,
            add_generation_prompt=add_generation_prompt,
            return_tensors=return_tensors,
        )

    def format_chat(
            self,
            messages: Sequence[Mapping[str, str]],
            *,
            add_generation_prompt: bool = True,
    ) -> str:
        """Renderiza una conversacion al formato textual de chat que usa Mesias."""
        normalized_messages = [
            {"role": str(message.get("role", "user")),
             "content": str(message.get("content", ""))}
            for message in messages
        ]
        return self.tokenizer.apply_chat_template(
            normalized_messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )

    def _get_input_device(self) -> Any:
        torch = lazy_import_torch()
        hf_device_map = getattr(self.model, "hf_device_map", None)
        if isinstance(hf_device_map, dict) and hf_device_map:
            first_device = next(iter(hf_device_map.values()))
            if isinstance(first_device, str) and first_device not in {"cpu", "disk"}:
                return torch.device(first_device)
        try:
            return next(self.model.parameters()).device
        except StopIteration:
            return torch.device(self.device)

    def _sanitize_text(self, text: str) -> str:
        if self.security is None:
            return text
        return self.security.ensure_safe(text)

    def _sanitize_output(self, text: str) -> str:
        if self.security is None:
            return text
        return self.security.sanitize_text(text).sanitized_text

    def _append_log(self, record: Mapping[str, Any]) -> None:
        existing_logs: List[Dict[str, Any]] = []
        if self.log_path.exists():
            try:
                raw_logs = self.log_path.read_text(encoding="utf-8").strip()
                if raw_logs:
                    existing_logs = json.loads(raw_logs)
            except (json.JSONDecodeError, OSError):
                existing_logs = []
        existing_logs.append(dict(record))
        self.log_path.write_text(
            json.dumps(existing_logs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _build_web_augmented_prompt(prompt: str, web_context: str) -> str:
        if not web_context.strip():
            return prompt
        return (
            "Usa el siguiente contexto web como apoyo factual si es relevante. "
            "Si alguna fuente fallo, indicalo solo si afecta a la respuesta.\n\n"
            f"Contexto web:\n{web_context}\n\n"
            f"Consulta del usuario:\n{prompt}"
        )


def load_mesias(
        model_path: Optional[Union[str, Any]] = None,
        **kwargs: Any,
) -> Mesias:
    """Crea una instancia de Mesias desde codigo consumidor externo."""
    return Mesias(model_path=model_path, **kwargs)


def run_console(
        prompt: Optional[str] = None,
        *,
        role: str = DEFAULT_ROLE,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.8,
        model_path: Optional[Union[str, Any]] = None,
        urls: Optional[Sequence[str]] = None,
        doctor: bool = False,
) -> int:
    """Ejecuta Mesias en modo consola unica o interactiva, con diagnostico opcional."""
    if doctor:
        diagnostics = diagnose_runtime(model_path=model_path)
        print(json.dumps(
            {
                "model_path": diagnostics.model_path,
                "model_files_ok": diagnostics.model_files_ok,
                "dependency_status": diagnostics.dependency_status,
                "web_connectivity": None if diagnostics.web_connectivity is None else diagnostics.web_connectivity.__dict__,
                "issues": diagnostics.issues,
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0 if not diagnostics.issues else 1

    mesias = Mesias(
        model_path=model_path,
        system_prompt=get_system_prompt(role),
    )

    if prompt:
        resolved_urls = list(urls or [])
        if not resolved_urls and mesias.should_search_web(prompt):
            resolved_urls = mesias.discover_web_urls(prompt)
        if resolved_urls:
            response = mesias.generate_with_web(
                prompt,
                urls=resolved_urls,
                system_prompt=get_system_prompt(role),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
            )
        else:
            response = mesias.generate(
                prompt,
                system_prompt=get_system_prompt(role),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
            )
        print(response.text)
        return 0

    print("Mesias consola interactiva. Escribe 'salir' para terminar.")
    memoria_chat = MemoriaChat(
        role=role,
        system_prompt=get_system_prompt(role),
        speaker_id=CONSOLE_SPEAKER_ID,
    )
    memoria_chat.clear()
    while True:
        user_prompt = input("Tu: ").strip()
        if user_prompt.lower() in {"salir", "exit", "quit"}:
            return 0
        if not user_prompt:
            continue
        resolved_urls = list(urls or [])
        if not resolved_urls and mesias.should_search_web(user_prompt):
            resolved_urls = mesias.discover_web_urls(user_prompt)
        response = memoria_chat.generate_reply(
            mesias,
            user_prompt,
            remember_profile=True,
            web_urls=resolved_urls,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        print(f"Mesias: {response.text}")


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser CLI de la consola nativa de Mesias."""
    parser = argparse.ArgumentParser(
        description="Consola de Mesias sobre Qwen2.5-3B-Instruct.")
    parser.add_argument("prompt", nargs="?", default=None,
                        help="Prompt opcional para una sola respuesta.")
    parser.add_argument("--role", default=DEFAULT_ROLE,
                        help="Rol de sistema a usar.")
    parser.add_argument("--max-new-tokens", type=int,
                        default=256, help="Numero maximo de tokens a generar.")
    parser.add_argument("--temperature", type=float,
                        default=0.7, help="Temperatura de generacion.")
    parser.add_argument("--top-p", type=float, default=0.8,
                        help="Parametro top-p de generacion.")
    parser.add_argument("--model-path", default=None,
                        help="Ruta opcional del modelo local.")
    parser.add_argument("--url", action="append", dest="urls", default=None,
                        help="URL web opcional para aportar contexto factual. Repite la bandera para multiples URLs.")
    parser.add_argument("--doctor", action="store_true",
                        help="Ejecuta diagnostico de dependencias, modelo y conectividad web.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Punto de entrada CLI del modulo principal de Mesias."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_console(
        prompt=args.prompt,
        role=args.role,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        model_path=args.model_path,
        urls=args.urls,
        doctor=args.doctor,
    )


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_SYSTEM_PROMPT",
    "Mesias",
    "MesiasResponse",
    "RuntimeDiagnostics",
    "WebContextResult",
    "DEFAULT_LOG_PATH",
    "build_parser",
    "diagnose_runtime",
    "main",
    "run_console",
]
