"""Editor Agent — assembles all pipeline outputs into a polished AI news briefing."""

import logging
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from acp_sdk.models import Message
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

from shared import OllamaClient, error_response, markdown_response, parse_json_input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server()
ollama = OllamaClient()


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

    return await ollama.generate(prompt)


@server.agent()
async def editor(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Assembles analyzed articles into a polished daily AI news briefing report."""

    yield {"thought": "Parsing analyzed articles..."}
    articles, err = parse_json_input(input)
    if err:
        yield error_response(err)
        return

    yield {"thought": f"Composing briefing from {len(articles)} articles..."}
    briefing = await compose_briefing(articles)

    yield {"thought": "Briefing complete!"}
    yield markdown_response(briefing)


server.run(host="0.0.0.0", port=8000)
