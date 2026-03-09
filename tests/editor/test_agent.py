"""Tests for the editor agent's unique logic."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_compose_briefing_calls_ollama_with_articles():
    """Test that compose_briefing formats articles and calls Ollama."""
    import sys
    sys.path.insert(0, "services/editor")

    articles = [
        {
            "title": "AI News",
            "source": "Test Source",
            "summary": "Summary of AI news.",
            "sentiment": "positive",
            "themes": ["AI", "research"],
            "link": "https://example.com",
        }
    ]

    with patch("agent.ollama") as mock_ollama:
        mock_ollama.generate = AsyncMock(return_value="# Daily Briefing\n\nContent here.")

        from agent import compose_briefing
        result = await compose_briefing(articles)

    assert result == "# Daily Briefing\n\nContent here."
    call_args = mock_ollama.generate.call_args[0][0]
    assert "AI News" in call_args
    assert "Test Source" in call_args
    assert "positive" in call_args
