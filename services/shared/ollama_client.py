"""Reusable async Ollama client for ACP agents."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL", "http://ollama-proxy:8080")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300"))


class OllamaClient:
    """Async client for generating text via Ollama (through the proxy)."""

    def __init__(
        self,
        proxy_url: str = OLLAMA_PROXY_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = OLLAMA_TIMEOUT,
    ):
        self.proxy_url = proxy_url
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str) -> str:
        """Send a prompt to Ollama and return the response text."""
        async with httpx.AsyncClient(base_url=self.proxy_url, timeout=self.timeout) as client:
            logger.info("Calling Ollama (model=%s)...", self.model)
            response = await client.post("/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            })
            response.raise_for_status()
            result = response.json()
            text = result.get("response", "")
            logger.info("Ollama response length: %d", len(text))
            return text
