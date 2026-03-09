"""Summarizer Agent — condenses articles into concise summaries."""

import logging
from collections.abc import AsyncGenerator

from acp_sdk.models import Message
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from shared import OllamaClient, error_response, json_response, parse_json_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server()
ollama = OllamaClient()


async def summarize_article(title: str, text: str) -> str:
    """Use Ollama to generate a concise summary of an article."""
    prompt = f"""Summarize the following AI news article in 2-3 sentences. Be concise and factual.

Title: {title}
Content: {text}

Summary:"""

    return await ollama.generate(prompt)


@server.agent()
async def summarizer(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Takes article data and produces concise summaries for each article."""

    yield {"thought": "Parsing articles..."}
    articles, err = parse_json_input(input)
    if err:
        yield error_response(err)
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

    yield json_response(summaries)


server.run(host="0.0.0.0", port=8000)
