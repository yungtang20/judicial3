"""Tests for confession corroboration checklist."""

from app.confession_checklist import ConfessionChecklist


def test_initial_state_incomplete():
    cl = ConfessionChecklist(case_id="case-1")
    assert cl.is_complete() is False
    assert len(cl.missing_labels()) == 6


def test_mark_items_satisfied():
    cl = ConfessionChecklist(case_id="case-1")
    cl.mark_satisfied("suspect_identity", evidence_refs=["ev1"])
    cl.mark_satisfied("act_confirmed", evidence_refs=["ev2"])
    assert cl.completion_ratio() == 2 / 6
    assert "犯罪人" not in cl.missing_labels()
    assert "行為" not in cl.missing_labels()


def test_complete_checklist():
    cl = ConfessionChecklist(case_id="case-1")
    for item_id, _, _ in [
        ("suspect_identity", "", ""),
        ("act_confirmed", "", ""),
        ("time_confirmed", "", ""),
        ("location_confirmed", "", ""),
        ("objects_confirmed", "", ""),
        ("corroborating_evidence", "", ""),
    ]:
        cl.mark_satisfied(item_id, evidence_refs=["ev"])
    assert cl.is_complete() is True
    assert cl.missing_labels() == []


def test_roundtrip_serialization():
    cl = ConfessionChecklist(case_id="case-1")
    cl.mark_satisfied("suspect_identity", evidence_refs=["ev1"], notes="confirmed")
    data = cl.to_dict()
    cl2 = ConfessionChecklist.from_dict(data)
    assert cl2.is_complete() is False
    assert cl2.items[0].satisfied is True
    assert cl2.items[0].evidence_refs == ["ev1"]