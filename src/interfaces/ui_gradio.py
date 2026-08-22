from __future__ import annotations

"""Interfaz Gradio de Mesias para chat local y pruebas manuales."""

import socket

if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from functools import lru_cache
from typing import Any, List, Optional

try:
    import gradio as gr
except ImportError as exc:
    raise ImportError(
        "Gradio no esta instalado. Instala 'gradio' para usar la interfaz web."
    ) from exc

try:
    from ..mesias import Mesias
    from ..memory.memoria_chat import MemoriaChat
    from .roles import DEFAULT_ROLE, get_system_prompt, list_role_names
except ImportError:
    from mesias import Mesias
    from memory.memoria_chat import MemoriaChat
    from roles import DEFAULT_ROLE, get_system_prompt, list_role_names


GRADIO_SPEAKER_ID = "gradio_local_user"


@lru_cache(maxsize=1)
def get_mesias() -> Mesias:
    """Reutiliza una instancia cacheada de Mesias para la UI."""
    return Mesias()


@lru_cache(maxsize=1)
def get_memoria_chat() -> MemoriaChat:
    """Reutiliza una memoria persistente asociada al usuario local de Gradio."""
    return MemoriaChat(speaker_id=GRADIO_SPEAKER_ID)


def _extract_text_content(content: Any) -> str:
    """Normaliza el contenido rico de Gradio a texto plano para Mesias."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, dict):
        for key in ("text", "content"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""
    if isinstance(content, list):
        parts = [_extract_text_content(item) for item in content]
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()


def _history_to_messages(history: List[dict[str, str]]) -> List[dict[str, str]]:
    """Convierte el historial del chatbot de Gradio al formato de mensajes de Mesias."""
    messages: List[dict[str, str]] = []
    for message in history:
        role = str(message.get("role", "assistant"))
        content = _extract_text_content(message.get("content", ""))
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    return messages


def _parse_urls(urls_text: str) -> List[str]:
    return [line.strip() for line in urls_text.splitlines() if line.strip()]


def _generate_reply(
    model: Mesias,
    message: str,
    history: List[dict[str, str]],
    role: str,
    urls_text: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> tuple[Any, str]:
    memoria_chat = get_memoria_chat()
    memoria_chat.role = role
    memoria_chat.system_prompt = get_system_prompt(role)
    memoria_chat.bootstrap(_history_to_messages(history), replace=True)

    generate_options = {
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    urls = _parse_urls(urls_text)
    if urls:
        response = memoria_chat.generate_reply(
            model,
            message,
            remember_profile=True,
            web_urls=urls,
            **generate_options,
        )
        return response, f"Web: {len(urls)} URL(s) manual(es)."
    if model.should_search_web(message, urls):
        found_urls = model.discover_web_urls(message, max_results=3)
        if found_urls:
            response = memoria_chat.generate_reply(
                model,
                message,
                remember_profile=True,
                web_urls=found_urls,
                **generate_options,
            )
            return response, f"Web: {len(found_urls)} resultado(s) encontrados automaticamente."
    return memoria_chat.generate_reply(
        model,
        message,
        remember_profile=True,
        **generate_options,
    ), "Memoria: activa."


def respond(
        message: str,
    history: List[dict[str, str]],
        role: str,
    urls_text: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
) -> tuple[str, List[dict[str, str]], str]:
    """Gestiona una interaccion de usuario en la UI Gradio de Mesias."""
    if not message.strip():
        return "", history, "Escribe un mensaje para continuar."

    try:
        response, extra_status = _generate_reply(
            get_mesias(),
            message,
            history,
            role,
            urls_text,
            max_new_tokens,
            temperature,
            top_p,
        )
    except Exception as exc:
        return message, history, f"Error: {exc}"

    updated_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response.text},
    ]
    stats = (
        f"Rol: {role} | Prompt tokens: {response.prompt_tokens} | "
        f"Completion tokens: {response.completion_tokens} | Total: {response.total_tokens}"
    )
    status_parts = [stats]
    if extra_status:
        status_parts.append(extra_status)
    return "", updated_history, " | ".join(status_parts)


def clear_chat() -> tuple[str, List[dict[str, str]], str]:
    """Reinicia el historial visible de la conversacion en la UI de Mesias."""
    return "", [], "Conversacion reiniciada."


def _find_available_port(preferred_port: int, max_attempts: int = 20) -> int:
    """Busca un puerto TCP libre cercano para lanzar Gradio sin abortar."""
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


def build_interface() -> gr.Blocks:
    """Construye el arbol de componentes Gradio que usa Mesias."""
    role_names = list_role_names()
    with gr.Blocks(title="Mesias") as demo:
        gr.Markdown("# Mesias\nInterfaz de chat para Qwen2.5-3B-Instruct.")

        with gr.Row():
            role = gr.Dropdown(
                choices=role_names,
                value=DEFAULT_ROLE,
                label="Rol",
            )
            max_new_tokens = gr.Slider(
                minimum=32,
                maximum=1024,
                value=256,
                step=32,
                label="Max new tokens",
            )
            temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.7,
                step=0.1,
                label="Temperature",
            )
            top_p = gr.Slider(
                minimum=0.1,
                maximum=1.0,
                value=0.8,
                step=0.05,
                label="Top p",
            )

        chatbot = gr.Chatbot(label="Conversacion", height=500)
        urls_text = gr.Textbox(
            label="URLs opcionales",
            placeholder="Una URL por linea para aportar contexto web...",
            lines=3,
        )
        prompt = gr.Textbox(
            label="Mensaje", placeholder="Escribe tu pregunta...")
        status = gr.Textbox(label="Estado", interactive=False)

        with gr.Row():
            send_button = gr.Button("Enviar", variant="primary")
            clear_button = gr.Button("Limpiar")

        send_button.click(
            fn=respond,
            inputs=[prompt, chatbot, role, urls_text,
                    max_new_tokens, temperature, top_p],
            outputs=[prompt, chatbot, status],
        )
        prompt.submit(
            fn=respond,
            inputs=[prompt, chatbot, role, urls_text,
                    max_new_tokens, temperature, top_p],
            outputs=[prompt, chatbot, status],
        )
        clear_button.click(
            fn=clear_chat,
            inputs=None,
            outputs=[prompt, chatbot, status],
        )

        gr.Markdown(
            "Usa los roles para cambiar el prompt de sistema: "
            + ", ".join(role_names)
            + "."
        )
    return demo


def launch(
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        share: bool = False,
) -> None:
    """Lanza la interfaz Gradio de Mesias en el host y puerto indicados."""
    demo = build_interface()
    resolved_port = _find_available_port(server_port)
    if resolved_port != server_port:
        print(
            f"Puerto {server_port} ocupado. Mesias Gradio usara {resolved_port}.",
            flush=True,
        )
    demo.launch(
        server_name=server_name,
        server_port=resolved_port,
        share=share,
        theme=gr.themes.Soft(),
    )


__all__ = ["build_interface", "get_mesias", "launch", "respond"]


def main(argv: Optional[List[str]] = None) -> int:
    """CLI minima para arrancar la interfaz Gradio de Mesias."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Arranca la UI Gradio de Mesias.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    args = parser.parse_args(argv)
    launch(server_name=args.host, server_port=args.port, share=args.share)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
