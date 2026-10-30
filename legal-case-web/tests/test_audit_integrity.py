"""Tests for audit log integrity (hash chain)."""

from app.audit_integrity import AuditChain


def test_append_and_verify():
    chain = AuditChain()
    chain.append("CASE_CREATED", metadata={"case_id": "1"})
    chain.append("GATE1_APPROVED", metadata={"user": "admin"})
    ok, reason = chain.verify()
    assert ok is True
    assert reason == ""


def test_tampered_entry_detected():
    chain = AuditChain()
    chain.append("CASE_CREATED")
    chain.append("GATE1_APPROVED")
    # Tamper with first entry
    chain.entries()[0].event = "TAMPERED"
    ok, reason = chain.verify()
    assert ok is False
    assert "hash mismatch" in reason


def test_broken_chain_detected():
    chain = AuditChain()
    chain.append("A")
    chain.append("B")
    # Break chain link
    chain.entries()[1].prev_hash = "WRONG"
    ok, reason = chain.verify()
    assert ok is False
    assert "chain broken" in reason or "hash mismatch" in reason


def test_empty_chain_valid():
    chain = AuditChain()
    ok, reason = chain.verify()
    assert ok is True


def test_roundtrip_serialization():
    chain = AuditChain()
    chain.append("EVENT1", metadata={"x": 1})
    chain.append("EVENT2")
    data = chain.to_list()
    chain2 = AuditChain.from_list(data)
    ok, reason = chain2.verify()
    assert ok is True
    assert chain2.length() == 2


def test_genesis_prev_hash():
    chain = AuditChain()
    entry = chain.append("FIRST")
    assert entry.prev_hash == "GENESIS"