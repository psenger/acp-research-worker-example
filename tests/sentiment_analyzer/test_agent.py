"""Tests for the sentiment-analyzer agent's unique logic."""

import json
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_analyze_sentiment_parses_valid_json():
    """Test that analyze_sentiment returns parsed LLM response."""
    import sys
    sys.path.insert(0, "services/sentiment-analyzer")

    llm_response = json.dumps({
        "sentiment": "positive",
        "confidence": 0.9,
        "themes": ["breakthrough", "open source"],
    })

    with patch("agent.ollama") as mock_ollama:
        mock_ollama.generate = AsyncMock(return_value=llm_response)

        from agent import analyze_sentiment
        result = await analyze_sentiment("AI Breakthrough", "Major advancement in AI.")

    assert result["sentiment"] == "positive"
    assert result["confidence"] == 0.9
    assert "breakthrough" in result["themes"]


@pytest.mark.asyncio
async def test_analyze_sentiment_handles_invalid_json():
    """Test that analyze_sentiment returns defaults on bad LLM output."""
    import sys
    sys.path.insert(0, "services/sentiment-analyzer")

    with patch("agent.ollama") as mock_ollama:
        mock_ollama.generate = AsyncMock(return_value="not valid json")

        from agent import analyze_sentiment
        result = await analyze_sentiment("Test", "Test summary")

    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.5
    assert result["themes"] == []
