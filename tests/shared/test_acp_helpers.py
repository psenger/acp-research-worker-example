"""Tests for shared.acp_helpers."""

import json

import pytest
from acp_sdk.models import Message, MessagePart

from shared.acp_helpers import (
    error_response,
    extract_input_text,
    json_response,
    markdown_response,
    parse_json_input,
)


def _make_messages(*contents: str) -> list[Message]:
    """Helper to create ACP messages from string contents."""
    return [
        Message(role="user", parts=[MessagePart(content=c, content_type="text/plain")])
        for c in contents
    ]


class TestExtractInputText:
    def test_single_message(self):
        messages = _make_messages("hello")
        assert extract_input_text(messages) == "hello"

    def test_multiple_messages(self):
        messages = _make_messages("hello", " world")
        assert extract_input_text(messages) == "hello world"

    def test_empty_messages(self):
        assert extract_input_text([]) == ""


class TestParseJsonInput:
    def test_valid_json(self):
        messages = _make_messages('[{"title": "test"}]')
        data, err = parse_json_input(messages)
        assert err is None
        assert data == [{"title": "test"}]

    def test_invalid_json(self):
        messages = _make_messages("not json")
        data, err = parse_json_input(messages)
        assert data is None
        assert "Invalid JSON" in err

    def test_empty_array(self):
        messages = _make_messages("[]")
        data, err = parse_json_input(messages)
        assert err is None
        assert data == []


class TestJsonResponse:
    def test_dict_input(self):
        msg = json_response({"key": "value"})
        assert msg.parts[0].content_type == "application/json"
        assert json.loads(msg.parts[0].content) == {"key": "value"}

    def test_list_input(self):
        msg = json_response([1, 2, 3])
        assert json.loads(msg.parts[0].content) == [1, 2, 3]

    def test_string_input_passthrough(self):
        msg = json_response('{"raw": true}')
        assert msg.parts[0].content == '{"raw": true}'


class TestMarkdownResponse:
    def test_creates_markdown_message(self):
        msg = markdown_response("# Hello")
        assert msg.parts[0].content == "# Hello"
        assert msg.parts[0].content_type == "text/markdown"


class TestErrorResponse:
    def test_creates_error_message(self):
        msg = error_response("something broke")
        parsed = json.loads(msg.parts[0].content)
        assert parsed == {"error": "something broke"}
        assert msg.parts[0].content_type == "application/json"
