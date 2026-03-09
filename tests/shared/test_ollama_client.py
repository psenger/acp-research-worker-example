"""Tests for shared.ollama_client."""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from shared.ollama_client import OllamaClient


@pytest.fixture
def client():
    return OllamaClient(proxy_url="http://test:8080", model="test-model", timeout=10)


@pytest.mark.asyncio
async def test_generate_returns_response_text(client):
    mock_response = httpx.Response(
        200,
        json={"response": "Hello from LLM"},
        request=httpx.Request("POST", "http://test:8080/api/generate"),
    )

    with patch("shared.ollama_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await client.generate("test prompt")

    assert result == "Hello from LLM"
    mock_client.post.assert_called_once_with("/api/generate", json={
        "model": "test-model",
        "prompt": "test prompt",
        "stream": False,
    })


@pytest.mark.asyncio
async def test_generate_returns_empty_on_missing_response(client):
    mock_response = httpx.Response(
        200,
        json={},
        request=httpx.Request("POST", "http://test:8080/api/generate"),
    )

    with patch("shared.ollama_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await client.generate("test prompt")

    assert result == ""


@pytest.mark.asyncio
async def test_generate_raises_on_http_error(client):
    mock_response = httpx.Response(
        500,
        text="Internal Server Error",
        request=httpx.Request("POST", "http://test:8080/api/generate"),
    )

    with patch("shared.ollama_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await client.generate("test prompt")
