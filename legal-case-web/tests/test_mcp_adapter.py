"""Tests for MCP adapter fail-closed default."""

from __future__ import annotations

from app.mcp_adapter import TaiwanLawMcpAdapter
from app.mcp_verification import VerificationStatus


def test_default_unavailable():
    ad = TaiwanLawMcpAdapter()
    r = ad.search_laws("刑法 320")
    assert r.available is False
    assert r.verification is not None
    assert r.verification.status == VerificationStatus.MCP_UNAVAILABLE.value
    assert r.records == []


def test_injected_hits_version_unverified():
    def fake(**kwargs):
        return [{"source_url": "https://example.law/a", "title": "x"}]

    ad = TaiwanLawMcpAdapter(search_laws=fake)
    r = ad.search_laws("刑法 320", version_checked_for_event_date=False)
    assert r.available is True
    assert r.verification is not None
    assert r.verification.status == VerificationStatus.VERSION_UNVERIFIED.value
