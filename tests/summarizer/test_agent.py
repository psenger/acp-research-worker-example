"""Tests for the summarizer agent's unique logic."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_summarize_article_calls_ollama():
    """Test that summarize_article sends correct prompt to Ollama."""
    import sys
    sys.path.insert(0, "services/summarizer")

    with patch("agent.ollama") as mock_ollama:
        mock_ollama.generate = AsyncMock(return_value="This is a summary.")

        from agent import summarize_article
        result = await summarize_article("Test Title", "Test content about AI.")

    assert result == "This is a summary."
    mock_ollama.generate.assert_called_once()
    call_args = mock_ollama.generate.call_args[0][0]
    assert "Test Title" in call_args
    assert "Test content about AI." in call_args
