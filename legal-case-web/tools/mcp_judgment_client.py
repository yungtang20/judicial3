# -*- coding: utf-8 -*-
"""MCP client for the remote Taiwan legal server (legaltech.org.tw/mcp).

Why this exists
---------------
Earlier attempts to read MCP output through PowerShell pipes produced what
looked like Big5 mojibake. Investigation showed that was a console/pipe
transcoding artifact, not bad data: the server returns valid UTF-8, but
cmd/PowerShell re-encodes text as it passes through pipes. Re-running the
same call, writing the raw bytes to a UTF-8 file, and reading that file back
returned clean text (e.g. 中華民國刑法 / 現行法規, article 305 text intact).

Rule for MCP work in this repo:
    never judge MCP text by what the terminal shows.
    write the raw response to a UTF-8 file, then read that file.

This module speaks the minimal HTTP JSON-RPC dialect the server accepts
(one POST per call, JSON body) and wraps the tools used to cross-check local
rules against real 地院 / 地檢 decisions:

    search_taiwan_laws(...)      -> statute text
    search_taiwan_judgments(...) -> real decisions (metadata + JID)
    get_taiwan_judgment(jid)     -> full text of one decision

Script usage (writes UTF-8 JSON to a file, never to stdout pipes):

    py -3 tools/mcp_judgment_client.py search_laws 跟蹤騷擾防治法
    py -3 tools/mcp_judgment_client.py judgments 跟蹤 "臺灣臺北地方法院" out.json
    py -3 tools/mcp_judgment_client.py judgment <jid> out.json
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request

BASE_URL = "https://legaltech.org.tw/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


def rpc(method: str, params: dict, *, timeout: int = 60):
    """Send one JSON-RPC request and return the decoded result."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=HEADERS,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    # The server may answer a plain JSON object, a bare {"result": ...}
    # wrapper, or an SSE event stream (lines beginning with "data:").
    stripped = raw.lstrip()
    if stripped.startswith("{") and ("jsonrpc" in raw[:40] or '"result"' in raw[:40]):
        return json.loads(raw)
    for line in raw.splitlines():
        if line.startswith("data:"):
            body = line[len("data:"):].strip()
            if body:
                return json.loads(body)
    raise ValueError(f"unrecognized MCP response: {raw[:200]!r}")


def call_tool(name: str, arguments: dict, *, timeout: int = 60):
    """Invoke a tool and return the text of its first text content block."""
    result = rpc("tools/call", {"name": name, "arguments": arguments}, timeout=timeout)
    content = result.get("result", {}).get("content") or []
    for block in content:
        if block.get("type") == "text":
            text = block.get("text", "")
            try:
                return json.loads(text)
            except (ValueError, TypeError):
                return text
    return result


def list_tools() -> list:
    result = rpc("tools/list", {})
    return result.get("result", {}).get("tools", [])


def search_laws(query: str, article_number: str | None = None, limit: int = 3):
    args: dict = {"query": query, "limit": limit}
    if article_number:
        args["article_number"] = article_number
    return call_tool("search_taiwan_laws", args)


def _article_numbers(reference: str) -> list[str]:
    """Expand a citation like "第135條至第141條" or "第3條、第4條至第11條".

    Returns the individual article numbers covered, capped to keep a single
    offense from pulling dozens of requests. Sub-numbered articles such as
    "第185條之3" keep their suffix.
    """
    ref = str(reference or "")
    found: list[str] = []

    def add(number: str) -> None:
        if number not in found:
            found.append(number)

    pattern = re.compile(
        r"第\s*([0-9]+(?:-[0-9]+)?)\s*條(?:之([0-9]+))?(?:至第\s*([0-9]+)\s*條(?:之([0-9]+))?)?"
    )
    for match in pattern.finditer(ref):
        start, suffix_a, end, end_suffix = match.groups()
        add(f"{start}-{suffix_a}" if suffix_a else start)
        if end:
            try:
                lo, hi = int(start), int(end)
            except ValueError:
                continue
            # Expand the whole range (not capped) so element terms living in a
            # later article of the same chapter are not falsely reported as
            # missing. Per-offense total is bounded below.
            for n in range(lo, hi + 1):
                add(str(n))
            if end_suffix:
                add(f"{end}-{end_suffix}")
    if not found:
        m = re.search(r"([0-9]+(?:-[0-9]+)?)", ref)
        if m:
            add(m.group(1))
    return found[:25]


def fetch_article_remote(law_name: str, article_no: str):
    """Return the article text for one law + article reference via the MCP.

    Multi-article references (a chapter range such as 第135條至第141條) are
    expanded and their texts joined, so element terms that live in a later
    article of the same chapter are not reported as missing.
    """
    numbers = _article_numbers(article_no)
    if not numbers:
        return None
    texts = []
    for art in numbers:
        # Sub-article references must keep their form: the API's article_number
        # takes "247-1" to mean 第247條之1. Stripping the suffix to the base
        # number (e.g. "315" for 第315條之1) makes the server fuzzy-match a
        # neighbouring article and silently return the wrong statute text.
        data = search_laws(law_name, article_number=art, limit=1)
        results = data.get("results", []) if isinstance(data, dict) else []
        for res in results:
            for article in res.get("articles", []):
                body = article.get("text")
                if body and body not in texts:
                    texts.append(body)
                break
    return "\n".join(texts) if texts else None


def search_judgments(
    query: str = "",
    court: str = "",
    case_type: str = "刑事",
    year_from: int | None = None,
    year_to: int | None = None,
    limit: int = 10,
    case_word: str = "",
    case_number: str = "",
    year: int | None = None,
):
    args: dict = {"limit": limit}
    if query:
        args["query"] = query
    if court:
        args["court"] = court
    if case_type:
        args["case_type"] = case_type
    if year_from is not None:
        args["year_from"] = year_from
    if year_to is not None:
        args["year_to"] = year_to
    if case_word:
        args["case_word"] = case_word
    if case_number:
        args["case_number"] = case_number
    if year is not None:
        args["year"] = year
    return call_tool("search_taiwan_judgments", args)


def get_judgment(jid: str, fresh: bool = False):
    return call_tool("get_taiwan_judgment", {"jid": jid, "fresh": fresh})


def _write(path: str, data) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        if isinstance(data, str):
            fh.write(data)
        else:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return path


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    mode = argv[1]
    if mode == "tools":
        out = argv[2]
        print(_write(out, list_tools()))
        return 0
    if mode == "search_laws":
        out = argv[3] if len(argv) > 3 else None
        data = search_laws(argv[2])
        print(_write(out, data) if out else json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if mode == "judgments":
        court = argv[3] if len(argv) > 3 else ""
        out = argv[4] if len(argv) > 4 else None
        data = search_judgments(query=argv[2], court=court, limit=10)
        if not out:
            raise SystemExit("must provide an output path so CJK is not lost to the pipe")
        print(_write(out, data))
        return 0
    if mode == "judgment":
        out = argv[3] if len(argv) > 3 else None
        if not out:
            raise SystemExit("must provide an output path so CJK is not lost to the pipe")
        print(_write(out, get_judgment(argv[2])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
