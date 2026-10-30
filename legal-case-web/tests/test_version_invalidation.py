"""Tests for version invalidation / STALE marking."""

from app.version_invalidation import DocumentStatus, VersionChain, VersionNode


def test_upstream_change_marks_downstream_stale():
    chain = VersionChain()
    case = VersionNode(node_id="case-1", node_type="case", version=1)
    analysis = VersionNode(node_id="analysis-1", node_type="analysis", version=1, upstream_deps=["case-1"], upstream_versions={"case-1": 1})
    doc = VersionNode(node_id="doc-1", node_type="document", version=1, upstream_deps=["analysis-1"], upstream_versions={"analysis-1": 1})
    chain.register(case)
    chain.register(analysis)
    chain.register(doc)

    invalidated = chain.update_upstream("case-1", 2)
    assert "analysis-1" in invalidated
    assert "doc-1" in invalidated
    assert chain.is_stale("analysis-1")
    assert chain.is_stale("doc-1")


def test_no_change_no_invalidation():
    chain = VersionChain()
    case = VersionNode(node_id="case-1", node_type="case", version=1)
    analysis = VersionNode(node_id="analysis-1", node_type="analysis", version=1, upstream_deps=["case-1"], upstream_versions={"case-1": 1})
    chain.register(case)
    chain.register(analysis)

    invalidated = chain.update_upstream("case-1", 1)  # same version
    assert invalidated == []
    assert not chain.is_stale("analysis-1")


def test_manual_mark_stale_propagates():
    chain = VersionChain()
    a = VersionNode(node_id="a", node_type="analysis", version=1)
    d = VersionNode(node_id="d", node_type="document", version=1, upstream_deps=["a"], upstream_versions={"a": 1})
    chain.register(a)
    chain.register(d)

    chain.mark_stale("a", "manual review required")
    assert chain.is_stale("a")
    assert chain.is_stale("d")


def test_stale_nodes_list():
    chain = VersionChain()
    n1 = VersionNode(node_id="n1", node_type="case", version=1, status="STALE")
    n2 = VersionNode(node_id="n2", node_type="case", version=1)
    chain.register(n1)
    chain.register(n2)
    assert len(chain.stale_nodes()) == 1