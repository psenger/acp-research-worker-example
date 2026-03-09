"""Summarizer Agent — condenses articles into concise summaries."""

import json
import os
from collections.abc import AsyncGenerator

import httpx
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()

OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL", "http://ollama-proxy:8080")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


async def summarize_article(title: str, text: str) -> str:
    """Use Ollama to generate a concise summary of an article."""
    prompt = f"""Summarize the following AI news article in 2-3 sentences. Be concise and factual.

Title: {title}
Content: {text}

Summary:"""

    async with httpx.AsyncClient(base_url=OLLAMA_PROXY_URL, timeout=300) as client:
        response = await client.post("/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        })
        result = response.json()
        return result.get("response", "")


@server.agent()
async def summarizer(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Takes article data and produces concise summaries for each article."""

    # Extract articles from input
    articles_json = ""
    for message in input:
        for part in message.parts:
            articles_json += part.content

    yield {"thought": "Parsing articles..."}

    try:
        articles = json.loads(articles_json)
    except json.JSONDecodeError:
        yield Message(
            role="agent",
            parts=[MessagePart(content=json.dumps({"error": "Invalid JSON input"}), content_type="application/json")],
        )
        return

    yield {"thought": f"Summarizing {len(articles)} articles..."}

    summaries = []
    for article in articles:
        title = article.get("title", "")
        text = article.get("summary", "")
        summary = await summarize_article(title, text)
        summaries.append({
            "title": title,
            "link": article.get("link", ""),
            "source": article.get("source", ""),
            "summary": summary,
        })
        yield {"thought": f"Summarized: {title[:50]}..."}

    yield Message(
        role="agent",
        parts=[MessagePart(content=json.dumps(summaries, indent=2), content_type="application/json")],
    )


server.run(host="0.0.0.0", port=8000)
