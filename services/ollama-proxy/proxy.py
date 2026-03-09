"""Ollama Queue/Proxy — serializes concurrent requests to Ollama."""

import asyncio
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI(title="Ollama Queue Proxy")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "120"))

# Semaphore ensures only one request hits Ollama at a time
_semaphore = asyncio.Semaphore(1)


async def _forward_request(method: str, path: str, body: bytes, headers: dict) -> httpx.Response:
    """Forward a single request to Ollama, holding the semaphore."""
    async with _semaphore:
        async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=REQUEST_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=path,
                content=body,
                headers={k: v for k, v in headers.items() if k.lower() not in ("host", "content-length")},
            )
            return response


async def _stream_forward(method: str, path: str, body: bytes, headers: dict):
    """Forward a request and stream the response back."""
    async with _semaphore:
        async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=REQUEST_TIMEOUT) as client:
            async with client.stream(
                method=method,
                url=path,
                content=body,
                headers={k: v for k, v in headers.items() if k.lower() not in ("host", "content-length")},
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk


@app.get("/health")
async def health():
    """Health check — also verifies Ollama connectivity."""
    try:
        async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=5) as client:
            resp = await client.get("/")
            return {"status": "ok", "ollama": resp.status_code == 200}
    except httpx.ConnectError:
        return {"status": "ok", "ollama": False}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    """Proxy all requests to Ollama, serialized through a semaphore."""
    body = await request.body()
    headers = dict(request.headers)
    full_path = f"/{path}"

    # For generate/chat endpoints, stream the response
    if request.method == "POST" and path in ("api/generate", "api/chat"):
        return StreamingResponse(
            _stream_forward(request.method, full_path, body, headers),
            media_type="application/x-ndjson",
        )

    # For all other requests, forward and return
    response = await _forward_request(request.method, full_path, body, headers)
    return httpx.Response(
        status_code=response.status_code,
        content=response.content,
        headers=dict(response.headers),
    )
