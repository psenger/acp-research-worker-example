"""Tests for the topic-scout agent's unique logic."""

from unittest.mock import MagicMock, patch

import pytest


def test_fetch_rss_articles_handles_empty_feeds():
    """Test that fetch_rss_articles returns empty list when feeds fail."""
    import sys
    sys.path.insert(0, "services/topic-scout")

    with patch("feedparser.parse") as mock_parse:
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_feed.bozo = False
        mock_feed.get.return_value = "unknown"
        mock_feed.feed.get.return_value = "Test Feed"
        mock_parse.return_value = mock_feed

        from agent import fetch_rss_articles
        articles = fetch_rss_articles()

    assert articles == []


def test_fetch_rss_articles_extracts_fields():
    """Test that articles are extracted with correct fields."""
    import sys
    sys.path.insert(0, "services/topic-scout")

    with patch("feedparser.parse") as mock_parse:
        mock_entry = {
            "title": "AI Breakthrough",
            "link": "https://example.com/article",
            "summary": "A major advancement in AI.",
        }
        mock_feed = MagicMock()
        mock_feed.entries = [MagicMock(**{"get.side_effect": lambda k, d="": mock_entry.get(k, d)})]
        mock_feed.bozo = False
        mock_feed.get.return_value = 200
        mock_feed.feed.get.return_value = "Test Source"
        mock_parse.return_value = mock_feed

        from agent import fetch_rss_articles
        articles = fetch_rss_articles()

    assert len(articles) >= 1
    assert articles[0]["title"] == "AI Breakthrough"
    assert articles[0]["source"] == "Test Source"
