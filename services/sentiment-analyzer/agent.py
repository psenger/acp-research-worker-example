"""Sentiment Analyzer Agent — evaluates tone and extracts themes from AI news."""

import json
import logging
from collections.abc import AsyncGenerator

from acp_sdk.models import Message
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from shared import OllamaClient, error_response, json_response, parse_json_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server()
ollama = OllamaClient()


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

    response = await ollama.generate(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"sentiment": "neutral", "confidence": 0.5, "themes": []}


@server.agent()
async def sentiment_analyzer(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Analyzes sentiment and extracts themes from article summaries."""

    yield {"thought": "Parsing summaries for sentiment analysis..."}
    articles, err = parse_json_input(input)
    if err:
        yield error_response(err)
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

    yield json_response(results)


server.run(host="0.0.0.0", port=8000)
