"""Tests for legal source verification against MCP (fail-closed)."""

from __future__ import annotations

from app.legal_source_verification import verify_candidate_sources
from app.mcp_adapter import TaiwanLawMcpAdapter
from app.mcp_verification import VerificationStatus


class _FakeAdapter(TaiwanLawMcpAdapter):
    """Injectable fake: returns one hit with source_url for a known article."""

    def search_laws(self, query: str, **kwargs: object):  # type: ignore[override]
        hits = [{"source_url": "https://law.moj.gov.tw/Law/LawSearchResult.aspx?kw=x",
                 "title": "中華民國刑法第320條", "text": "竊盜罪..."}]
        ver = self._record("search_taiwan_laws", VerificationStatus.VERIFIED, query, hits[0]["source_url"], len(hits))
        return type("R", (), {"records": hits, "verification": ver, "available": True})()

    def _record(self, tool: str, status: VerificationStatus, query: str,
                source_url: str, hit_count: int):
        from app.mcp_verification import build_record
        return build_record(tool=tool, status=status, query=query,
                            source_url=source_url, case_revision=None, hit_count=hit_count)


def test_verify_records_appended_on_case() -> None:
    case: dict = {}
    candidates = [{"source": {"law_name": "中華民國刑法", "article_no": "第320條"}}]
    adapter = _FakeAdapter()
    records = verify_candidate_sources(candidates, adapter=adapter, case=case)
    assert len(records) == 1
    assert records[0].status == VerificationStatus.VERIFIED.value
    assert case["mcp_verification_log"][0]["status"] == VerificationStatus.VERIFIED.value
    lv = candidates[0]["law_verification"][0]
    assert lv["law_name"] == "中華民國刑法"
    assert lv["article_no"] == "第320條"
    assert lv["status"] == VerificationStatus.VERIFIED.value
    assert lv["source_url"] == "https://law.moj.gov.tw/Law/LawSearchResult.aspx?kw=x"


def test_verify_fail_closed_when_no_adapter() -> None:
    case: dict = {}
    candidates = [{"source": {"law_name": "中華民國刑法", "article_no": "第320條"}}]
    records = verify_candidate_sources(candidates, adapter=None, case=case)
    assert len(records) == 1
    assert records[0].status == VerificationStatus.MCP_UNAVAILABLE.value
    assert records[0].source_url == ""
    assert candidates[0]["law_verification"][0]["status"] == VerificationStatus.MCP_UNAVAILABLE.value
    assert case["mcp_verification_log"][0]["status"] == VerificationStatus.MCP_UNAVAILABLE.value


def test_verify_skips_candidates_without_source() -> None:
    case: dict = {}
    candidates = [{}, {"name": "no source"}]
    adapter = _FakeAdapter()
    records = verify_candidate_sources(candidates, adapter=adapter, case=case)
    assert records == []
    assert case.get("mcp_verification_log") is None
