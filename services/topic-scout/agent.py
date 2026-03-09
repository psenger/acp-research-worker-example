"""Topic Scout Agent — discovers trending AI news from RSS feeds."""

import json
import os
from collections.abc import AsyncGenerator

import feedparser
import httpx
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()

OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL", "http://ollama-proxy:8080")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

RSS_FEEDS = [
    "https://hnrss.org/newest?q=AI+OR+LLM+OR+%22artificial+intelligence%22&count=20",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://feeds.feedburner.com/venturebeat/SZYF",
]


def fetch_rss_articles() -> list[dict]:
    """Fetch articles from configured RSS feeds."""
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "source": feed.feed.get("title", feed_url),
                })
        except Exception:
            continue
    return articles


async def rank_articles(articles: list[dict]) -> str:
    """Use Ollama to rank and filter the most relevant AI trending topics."""
    articles_text = "\n".join(
        f"- {a['title']} ({a['source']}): {a['summary'][:200]}"
        for a in articles[:30]
    )

    prompt = f"""You are an AI news curator. From the following articles, select the top 5 most interesting
and trending AI/ML topics. Return a JSON array of objects with keys: "title", "link", "summary", "source".

Articles:
{articles_text}

Return ONLY valid JSON, no other text."""

    async with httpx.AsyncClient(base_url=OLLAMA_PROXY_URL, timeout=120) as client:
        response = await client.post("/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        })
        result = response.json()
        return result.get("response", "[]")


@server.agent()
async def topic_scout(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Discovers trending AI news topics from RSS feeds and ranks them using an LLM."""

    yield {"thought": "Fetching AI news from RSS feeds..."}

    articles = fetch_rss_articles()

    yield {"thought": f"Found {len(articles)} articles. Ranking with LLM..."}

    ranked = await rank_articles(articles)

    yield Message(
        role="agent",
        parts=[MessagePart(content=ranked, content_type="application/json")],
    )


server.run(port=8000)
