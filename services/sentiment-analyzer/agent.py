"""Sentiment Analyzer Agent — evaluates tone and extracts themes from AI news."""

import json
import os
from collections.abc import AsyncGenerator

import httpx
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()

OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL", "http://ollama-proxy:8080")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


async def analyze_sentiment(title: str, summary: str) -> dict:
    """Use Ollama to classify sentiment and extract themes."""
    prompt = f"""Analyze the sentiment and themes of this AI news article.

Title: {title}
Summary: {summary}

Return a JSON object with:
- "sentiment": one of "positive", "negative", or "neutral"
- "confidence": a number between 0 and 1
- "themes": an array of 2-3 keyword themes (e.g. ["open source", "regulation", "breakthrough"])

Return ONLY valid JSON, no other text."""

    async with httpx.AsyncClient(base_url=OLLAMA_PROXY_URL, timeout=300) as client:
        response = await client.post("/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        })
        result = response.json()
        try:
            return json.loads(result.get("response", "{}"))
        except json.JSONDecodeError:
            return {"sentiment": "neutral", "confidence": 0.5, "themes": []}


@server.agent()
async def sentiment_analyzer(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Analyzes sentiment and extracts themes from article summaries."""

    articles_json = ""
    for message in input:
        for part in message.parts:
            articles_json += part.content

    yield {"thought": "Parsing summaries for sentiment analysis..."}

    try:
        articles = json.loads(articles_json)
    except json.JSONDecodeError:
        yield Message(
            role="agent",
            parts=[MessagePart(content=json.dumps({"error": "Invalid JSON input"}), content_type="application/json")],
        )
        return

    yield {"thought": f"Analyzing sentiment for {len(articles)} articles..."}

    results = []
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        sentiment = await analyze_sentiment(title, summary)
        results.append({
            **article,
            "sentiment": sentiment.get("sentiment", "neutral"),
            "confidence": sentiment.get("confidence", 0.5),
            "themes": sentiment.get("themes", []),
        })
        yield {"thought": f"Analyzed: {title[:50]}..."}

    yield Message(
        role="agent",
        parts=[MessagePart(content=json.dumps(results, indent=2), content_type="application/json")],
    )


server.run(host="0.0.0.0", port=8000)
