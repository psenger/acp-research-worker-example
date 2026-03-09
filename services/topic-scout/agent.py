"""Topic Scout Agent — discovers trending AI news from RSS feeds."""

import logging
from collections.abc import AsyncGenerator

import feedparser
from acp_sdk.models import Message
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from shared import OllamaClient, json_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server()
ollama = OllamaClient()

RSS_FEEDS = [
    "https://hnrss.org/newest?q=AI+OR+LLM+OR+%22artificial+intelligence%22&count=20",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
]


def fetch_rss_articles() -> list[dict]:
    """Fetch articles from configured RSS feeds."""
    articles = []
    for feed_url in RSS_FEEDS:
        logger.info("Fetching feed: %s", feed_url)
        try:
            feed = feedparser.parse(feed_url)
            logger.info("  Feed status: %s, entries: %d", feed.get("status", "unknown"), len(feed.entries))
            if feed.bozo:
                logger.warning("  Feed parse error: %s", feed.bozo_exception)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "source": feed.feed.get("title", feed_url),
                })
        except Exception as e:
            logger.error("  Failed to fetch feed: %s", e)
            continue
    logger.info("Total articles fetched: %d", len(articles))
    return articles


async def rank_articles(articles: list[dict]) -> str:
    """Use Ollama to rank and filter the most relevant AI trending topics."""
    if not articles:
        logger.warning("No articles to rank")
        return "[]"

    articles_text = "\n".join(
        f"- {a['title']} ({a['source']}): {a['summary'][:200]}"
        for a in articles[:30]
    )

    prompt = f"""You are an AI news curator. From the following articles, select the top 5 most interesting
and trending AI/ML topics. Return a JSON array of objects with keys: "title", "link", "summary", "source".

Articles:
{articles_text}

Return ONLY valid JSON, no other text."""

    return await ollama.generate(prompt)


@server.agent()
async def topic_scout(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Discovers trending AI news topics from RSS feeds and ranks them using an LLM."""

    yield {"thought": "Fetching AI news from RSS feeds..."}
    articles = fetch_rss_articles()

    if not articles:
        yield {"thought": "No articles found from RSS feeds."}
        yield json_response([])
        return

    yield {"thought": f"Found {len(articles)} articles. Ranking with LLM..."}
    ranked = await rank_articles(articles)
    yield json_response(ranked)


server.run(host="0.0.0.0", port=8000)
