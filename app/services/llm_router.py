from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import httpx


@dataclass
class LLMResponse:
    text: str
    model: str


class LLMRouter:
    def __init__(self, api_key: str, base_url: str, models: list[str], timeout: float = 25.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.models = models
        self.timeout = timeout

    async def chat(self, messages: list[dict[str, str]], state: dict[str, Any] | None = None) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required.")

        errors: list[str] = []
        payload = {
            "messages": messages,
            "temperature": 0.2,
        }
        if state:
            payload["metadata"] = {"checkpoint": state}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for model in self.models:
                try:
                    res = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={**payload, "model": model},
                    )
                    res.raise_for_status()
                    body = res.json()
                    text = body["choices"][0]["message"]["content"]
                    return LLMResponse(text=text, model=model)
                except Exception as exc:  # move to next failover model
                    errors.append(f"{model}: {exc}")
                    continue
        raise RuntimeError(f"All model calls failed: {' | '.join(errors)}")
