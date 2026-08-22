from __future__ import annotations

"""CLI compartido de Mesias para consola, API y Gradio."""

import argparse
from typing import Optional, Sequence


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser comun de Mesias para consola, API y Gradio."""
    parser = argparse.ArgumentParser(description="Lanzador principal de Mesias.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    console_parser = subparsers.add_parser("console", help="Lanza Mesias en consola.")
    console_parser.add_argument("prompt", nargs="?", default=None)
    console_parser.add_argument("--role", default="general")
    console_parser.add_argument("--max-new-tokens", type=int, default=256)
    console_parser.add_argument("--temperature", type=float, default=0.7)
    console_parser.add_argument("--top-p", type=float, default=0.8)
    console_parser.add_argument("--model-path", default=None)
    console_parser.add_argument("--url", action="append", dest="urls", default=None)
    console_parser.add_argument("--doctor", action="store_true")

    api_parser = subparsers.add_parser("api", help="Lanza la API FastAPI.")
    api_parser.add_argument("--host", default="127.0.0.1")
    api_parser.add_argument("--port", type=int, default=8000)
    api_parser.add_argument("--reload", action="store_true")

    gradio_parser = subparsers.add_parser("gradio", help="Lanza la UI Gradio.")
    gradio_parser.add_argument("--host", default="127.0.0.1")
    gradio_parser.add_argument("--port", type=int, default=7860)
    gradio_parser.add_argument("--share", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Despacha el modo CLI solicitado."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "console":
        from .mesias import run_console

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
    if args.mode == "api":
        from .interfaces.api_fastapi import run_api

        run_api(host=args.host, port=args.port, reload=args.reload)
        return 0
    if args.mode == "gradio":
        from .interfaces.ui_gradio import launch

        launch(server_name=args.host, server_port=args.port, share=args.share)
        return 0

    parser.error("Modo no soportado.")
    return 2


__all__ = ["build_parser", "main"]