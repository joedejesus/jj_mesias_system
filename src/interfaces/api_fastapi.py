from __future__ import annotations

"""Interfaz FastAPI para exponer Mesias por HTTP."""

import socket

if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from functools import lru_cache
from typing import Any, Dict, List, Literal, Optional

try:
    from fastapi import FastAPI, HTTPException, Response
    from pydantic import BaseModel, Field
except ImportError as exc:
    raise ImportError(
        "FastAPI y pydantic no estan instalados. Instala 'fastapi' y 'pydantic' para usar la API."
    ) from exc

try:
    from ..mesias import Mesias, diagnose_runtime
    from ..memory.memoria_chat import MemoriaChat
    from .roles import DEFAULT_ROLE, get_system_prompt, list_role_names
except ImportError:
    from mesias import Mesias, diagnose_runtime
    from memory.memoria_chat import MemoriaChat
    from roles import DEFAULT_ROLE, get_system_prompt, list_role_names


class ChatMessage(BaseModel):
    """Mensaje individual del historial que recibe o devuelve la API de Mesias."""
    role: Literal["system", "user", "assistant"] = "user"
    content: str = Field(..., min_length=1)


class GenerateRequest(BaseModel):
    """Payload de entrada para generacion simple o conversacional en Mesias."""
    prompt: str = Field(..., min_length=1)
    role: str = DEFAULT_ROLE
    speaker_id: Optional[str] = None
    history: List[ChatMessage] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    remember_profile: bool = True
    max_new_tokens: int = Field(default=256, ge=1, le=4096)
    do_sample: bool = True
    temperature: float = Field(default=0.7, ge=0.0, le=5.0)
    top_p: float = Field(default=0.8, ge=0.0, le=1.0)
    top_k: int = Field(default=20, ge=0)
    repetition_penalty: float = Field(default=1.05, ge=0.5, le=3.0)


class GenerateResponse(BaseModel):
    """Respuesta normalizada de Mesias para la API HTTP."""
    text: str
    role: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    messages: List[ChatMessage]


class HealthResponse(BaseModel):
    """Estado minimo de salud de la instancia Mesias cargada por la API."""
    status: str
    model_path: str
    device: str


class DiagnosticsResponse(BaseModel):
    """Resultado serializable del diagnostico operativo de Mesias."""
    model_path: str
    model_files_ok: bool
    dependency_status: Dict[str, bool]
    web_connectivity: Optional[Dict[str, Any]]
    issues: List[str]


def _model_to_dict(model: BaseModel) -> dict[str, Any]:
    """Compatibiliza modelos Pydantic v1 y v2 al hablar con Mesias."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _history_to_dicts(history: List[ChatMessage]) -> List[dict[str, Any]]:
    return [_model_to_dict(message) for message in history]


def _generate_options(request: GenerateRequest) -> dict[str, Any]:
    return {
        "max_new_tokens": request.max_new_tokens,
        "do_sample": request.do_sample,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "repetition_penalty": request.repetition_penalty,
    }


def _generate_from_request(model: Mesias, request: GenerateRequest) -> Any:
    history = _history_to_dicts(request.history)
    generate_options = _generate_options(request)
    system_prompt = get_system_prompt(request.role)
    resolved_urls = list(request.urls)
    if not resolved_urls and model.should_search_web(request.prompt):
        resolved_urls = model.discover_web_urls(request.prompt)
    if request.speaker_id:
        memoria_chat = MemoriaChat(
            role=request.role,
            system_prompt=system_prompt,
            speaker_id=request.speaker_id,
        )
        memoria_chat.bootstrap(history, replace=True)
        return memoria_chat.generate_reply(
            model,
            request.prompt,
            remember_profile=request.remember_profile,
            web_urls=resolved_urls,
            **generate_options,
        )
    if resolved_urls:
        return model.generate_with_web(
            prompt=request.prompt,
            urls=resolved_urls,
            history=history,
            system_prompt=system_prompt,
            **generate_options,
        )
    return model.generate(
        prompt=request.prompt,
        history=history,
        system_prompt=system_prompt,
        **generate_options,
    )


@lru_cache(maxsize=1)
def get_mesias() -> Mesias:
    """Crea una unica instancia cacheada de Mesias para la API."""
    return Mesias()


app = FastAPI(
    title="Mesias API",
    version="1.0.0",
    description="API de inferencia para Qwen2.5-3B-Instruct en el proyecto Mesias.",
)


@app.get("/")
def root() -> Dict[str, str]:
    """Punto de entrada amigable para quien abre la URL base de la API."""
    return {
        "name": "Mesias API",
        "docs": "/docs",
        "health": "/health",
        "roles": "/roles",
        "diagnostics": "/diagnostics",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Evita un 404 espurio cuando el navegador pide automaticamente el favicon."""
    return Response(status_code=204)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Endpoint de salud basico para confirmar que Mesias carga correctamente."""
    try:
        model = get_mesias()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return HealthResponse(
        status="ok",
        model_path=str(model.model_path),
        device=str(model.device),
    )


@app.get("/roles", response_model=List[str])
def roles() -> List[str]:
    """Endpoint que expone los roles soportados por Mesias."""
    return list_role_names()


@app.get("/diagnostics", response_model=DiagnosticsResponse)
def diagnostics() -> DiagnosticsResponse:
    """Endpoint que devuelve el diagnostico operativo completo de Mesias."""
    try:
        result = diagnose_runtime()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return DiagnosticsResponse(
        model_path=result.model_path,
        model_files_ok=result.model_files_ok,
        dependency_status=result.dependency_status,
        web_connectivity=None if result.web_connectivity is None else result.web_connectivity.__dict__,
        issues=result.issues,
    )


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    """Genera una respuesta de Mesias a partir de prompt, historial y URLs opcionales."""
    try:
        response = _generate_from_request(get_mesias(), request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return GenerateResponse(
        text=response.text,
        role=request.role,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        total_tokens=response.total_tokens,
        messages=[ChatMessage(**message) for message in response.messages],
    )


@app.post("/chat", response_model=GenerateResponse)
def chat(request: GenerateRequest) -> GenerateResponse:
    """Ejecuta una interaccion de chat de Mesias preservando el historial recibido."""
    try:
        response = _generate_from_request(get_mesias(), request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return GenerateResponse(
        text=response.text,
        role=request.role,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        total_tokens=response.total_tokens,
        messages=[ChatMessage(**message) for message in response.messages],
    )


__all__ = ["app", "get_mesias"]


def _browser_base_url(host: str, port: int) -> str:
    """Normaliza una URL util para navegador a partir del host configurado."""
    normalized_host = host.strip()
    if normalized_host in {"0.0.0.0", "::", "[::]"}:
        normalized_host = "127.0.0.1"
    return f"http://{normalized_host}:{port}"


def _find_available_port(preferred_port: int, max_attempts: int = 20) -> int:
    """Busca un puerto TCP libre cercano para arrancar la API sin abortar."""
    for port in range(preferred_port, preferred_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    raise OSError(
        f"No hay puertos libres entre {preferred_port} y {preferred_port + max_attempts - 1}."
    )


def run_api(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Arranca el servidor Uvicorn que expone la API de Mesias."""
    try:
        import uvicorn
    except ImportError as exc:
        raise ImportError(
            "Uvicorn no esta instalado. Instala 'uvicorn' para arrancar la API.") from exc
    resolved_port = _find_available_port(port)
    if resolved_port != port:
        print(
            f"Puerto {port} ocupado. Mesias API usara {resolved_port}.",
            flush=True,
        )
    browser_base_url = _browser_base_url(host, resolved_port)
    print(
        f"Abre {browser_base_url}/ o {browser_base_url}/docs en tu navegador.",
        flush=True,
    )
    uvicorn.run(app, host=host, port=resolved_port, reload=reload)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI minima para lanzar la API FastAPI de Mesias."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Arranca la API FastAPI de Mesias.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args(argv)
    run_api(host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
