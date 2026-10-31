"""Tests for the MCP client boundary (hermetic: no real network/subprocess)."""

from __future__ import annotations

import json
from typing import Any
from unittest import mock

from app.mcp_client import _remote_text, remote_call_tool


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self._text = text

    def read(self) -> bytes:
        return self._text.encode("utf-8")

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: Any) -> None:
        return None


def test_remote_text_parses_plain_json() -> None:
    data = {"result": {"content": [{"type": "text", "text": '{"success": true}'}]}}
    fake = _FakeResponse(json.dumps(data))
    with mock.patch("app.mcp_client.urllib.request.urlopen", return_value=fake):
        out = _remote_text("search_taiwan_laws", {"query": "x"})
    assert out == {"success": True}


def test_remote_text_parses_sse() -> None:
    payload = {"result": {"content": [{"type": "text", "text": '{"ok": 1}'}]}}
    text = "data: " + json.dumps(payload) + "\n\n"
    fake = _FakeResponse(text)
    with mock.patch("app.mcp_client.urllib.request.urlopen", return_value=fake):
        out = _remote_text("search_taiwan_laws", {"query": "x"})
    assert out == {"ok": 1}


def test_remote_text_returns_raw_on_non_json() -> None:
    payload = {"result": {"content": [{"type": "text", "text": "plain text"}]}}
    text = "data: " + json.dumps(payload) + "\n\n"
    fake = _FakeResponse(text)
    with mock.patch("app.mcp_client.urllib.request.urlopen", return_value=fake):
        out = _remote_text("search_taiwan_laws", {"query": "x"})
    assert out == "plain text"


def test_remote_call_passes_query_arguments() -> None:
    captured: dict[str, Any] = {}

    class _FakeReq:
        def __init__(self, url: str, data: bytes, headers: dict[str, str]) -> None:
            captured["data"] = data
            captured["headers"] = headers

        def read(self) -> bytes:
            return json.dumps({
                "result": {"content": [{"type": "text", "text": '[]'}]}
            }).encode("utf-8")

        def __enter__(self) -> "_FakeReq":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

    with mock.patch("app.mcp_client.urllib.request.Request", _FakeReq):
        with mock.patch("app.mcp_client.urllib.request.urlopen", return_value=_FakeReq("", b"", {})):
            remote_call_tool("search_taiwan_laws", {"query": "x", "limit": 3})
    assert b'"query": "x"' in captured["data"]
    assert b'"limit": 3' in captured["data"]
    assert captured["headers"]["User-Agent"].startswith("Mozilla/5.0")
