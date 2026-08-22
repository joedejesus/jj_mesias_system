from __future__ import annotations

import asyncio
import gc
import unittest
import warnings
from dataclasses import dataclass
from unittest.mock import patch

import httpx

from src.interfaces.api_fastapi import app
from src.interfaces.ui_gradio import build_interface


@dataclass
class _FakeResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    messages: list[dict[str, str]]


class _FakeMesias:
    model_path = "fake-model"
    device = "cpu"
    web_client = object()

    def should_search_web(self, prompt: str, urls=None) -> bool:
        return "habitantes" in prompt.lower() and not urls

    def discover_web_urls(self, prompt: str, max_results: int = 3):
        return ["https://example.org/fuente"] if self.should_search_web(prompt) else []

    def generate(self, prompt: str, history=None, system_prompt=None, **kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return _FakeResponse(
            text="respuesta de prueba",
            prompt_tokens=4,
            completion_tokens=3,
            total_tokens=7,
            messages=messages,
        )

    def generate_with_web(self, prompt: str, urls, history=None, system_prompt=None, **kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return _FakeResponse(
            text=f"respuesta con web: {len(urls)}",
            prompt_tokens=5,
            completion_tokens=4,
            total_tokens=9,
            messages=messages,
        )


class InterfacesTestCase(unittest.TestCase):
    def test_api_app_title(self) -> None:
        self.assertEqual(app.title, "Mesias API")

    def test_api_root_endpoint_is_available(self) -> None:
        async def run_request() -> dict[str, object]:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get("/")
            self.assertEqual(response.status_code, 200)
            return response.json()

        payload = asyncio.run(run_request())
        self.assertEqual(payload["name"], "Mesias API")
        self.assertEqual(payload["docs"], "/docs")

    def test_api_favicon_endpoint_does_not_404(self) -> None:
        async def run_request() -> int:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get("/favicon.ico")
            return response.status_code

        status_code = asyncio.run(run_request())
        self.assertEqual(status_code, 204)

    def test_api_generate_endpoint_with_test_client(self) -> None:
        async def run_request() -> dict[str, object]:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/generate",
                    json={
                        "prompt": "hola",
                        "role": "general",
                        "history": [],
                        "urls": [],
                    },
                )
            self.assertEqual(response.status_code, 200)
            return response.json()

        with patch("src.interfaces.api_fastapi.get_mesias", return_value=_FakeMesias()):
            payload = asyncio.run(run_request())

        self.assertEqual(payload["text"], "respuesta de prueba")
        self.assertEqual(payload["messages"][-1]["content"], "hola")

    def test_api_generate_endpoint_uses_web_heuristic(self) -> None:
        async def run_request() -> dict[str, object]:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/generate",
                    json={
                        "prompt": "Necesito saber los habitantes de Asturias",
                        "role": "general",
                        "history": [],
                        "urls": [],
                    },
                )
            self.assertEqual(response.status_code, 200)
            return response.json()

        with patch("src.interfaces.api_fastapi.get_mesias", return_value=_FakeMesias()):
            payload = asyncio.run(run_request())

        self.assertEqual(payload["text"], "respuesta con web: 1")

    def test_api_chat_endpoint_uses_web_heuristic(self) -> None:
        async def run_request() -> dict[str, object]:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/chat",
                    json={
                        "prompt": "Necesito saber los habitantes de Asturias",
                        "role": "general",
                        "history": [
                            {"role": "assistant",
                                "content": "Dime la pregunta exacta."},
                        ],
                        "urls": [],
                    },
                )
            self.assertEqual(response.status_code, 200)
            return response.json()

        with patch("src.interfaces.api_fastapi.get_mesias", return_value=_FakeMesias()):
            payload = asyncio.run(run_request())

        self.assertEqual(payload["text"], "respuesta con web: 1")
        self.assertEqual(payload["messages"][1]
                         ["content"], "Dime la pregunta exacta.")
        self.assertEqual(payload["messages"][-1]["content"],
                         "Necesito saber los habitantes de Asturias")

    def test_gradio_interface_builds(self) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"unclosed event loop .*",
                category=ResourceWarning,
            )
            interface = build_interface()
            try:
                self.assertEqual(type(interface).__name__, "Blocks")
            finally:
                interface.close()
                del interface
                gc.collect()


if __name__ == "__main__":
    unittest.main()
