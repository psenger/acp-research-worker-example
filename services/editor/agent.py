"""Editor Agent — assembles all pipeline outputs into a polished AI news briefing."""

import json
import os
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import httpx
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()

OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL", "http://ollama-proxy:8080")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


async def compose_briefing(articles: list[dict]) -> str:
    """Use Ollama to compose a polished daily AI news briefing."""
    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"""
Article {i}:
- Title: {a.get('title', '')}
- Source: {a.get('source', '')}
- Summary: {a.get('summary', '')}
- Sentiment: {a.get('sentiment', 'neutral')}
- Themes: {', '.join(a.get('themes', []))}
- Link: {a.get('link', '')}
"""

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    prompt = f"""You are an AI news editor. Compose a polished daily briefing report in Markdown format
for {today}. Use the following analyzed articles:

{articles_text}

Structure the report as:
1. A brief executive summary (2-3 sentences on today's AI landscape)
2. Each article as a section with a compelling headline, the summary, sentiment indicator, and source link
3. A "Themes to Watch" section listing recurring themes across articles
4. Keep it professional, concise, and engaging

Output the full Markdown report:"""

    async with httpx.AsyncClient(base_url=OLLAMA_PROXY_URL, timeout=300) as client:
        response = await client.post("/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        })
        result = response.json()
        return result.get("response", "")


@server.agent()
async def editor(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Assembles analyzed articles into a polished daily AI news briefing report."""

    articles_json = ""
    for message in input:
        for part in message.parts:
            articles_json += part.content

    yield {"thought": "Parsing analyzed articles..."}

    try:
        articles = json.loads(articles_json)
    except json.JSONDecodeError:
        yield Message(
            role="agent",
            parts=[MessagePart(content="Error: Invalid JSON input", content_type="text/plain")],
        )
        return

    yield {"thought": f"Composing briefing from {len(articles)} articles..."}

    briefing = await compose_briefing(articles)

    yield {"thought": "Briefing complete!"}

    yield Message(
        role="agent",
        parts=[MessagePart(content=briefing, content_type="text/markdown")],
    )


server.run(host="0.0.0.0", port=8000)
