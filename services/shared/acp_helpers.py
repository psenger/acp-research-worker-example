"""ACP message utilities for agent input/output handling."""

import json
import logging
from typing import Any

from acp_sdk.models import Message, MessagePart

logger = logging.getLogger(__name__)


def extract_input_text(messages: list[Message]) -> str:
    """Extract and concatenate all text content from ACP input messages."""
    parts = []
    for message in messages:
        for part in message.parts:
            parts.append(part.content)
    return "".join(parts)


def parse_json_input(messages: list[Message]) -> tuple[Any | None, str | None]:
    """Extract and JSON-parse input from ACP messages.

    Returns:
        (parsed_data, None) on success.
        (None, error_message) on failure.
    """
    text = extract_input_text(messages)
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON input: %s", e)
        return None, f"Invalid JSON input: {e}"


def json_response(data: Any) -> Message:
    """Create an ACP Message with JSON content."""
    content = json.dumps(data, indent=2) if not isinstance(data, str) else data
    return Message(
        role="agent",
        parts=[MessagePart(content=content, content_type="application/json")],
    )


def markdown_response(text: str) -> Message:
    """Create an ACP Message with Markdown content."""
    return Message(
        role="agent",
        parts=[MessagePart(content=text, content_type="text/markdown")],
    )


def error_response(message: str) -> Message:
    """Create a standardized error ACP Message."""
    return Message(
        role="agent",
        parts=[MessagePart(
            content=json.dumps({"error": message}),
            content_type="application/json",
        )],
    )
