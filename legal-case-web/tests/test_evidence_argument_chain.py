"""Tests for evidence-argument chain."""

from app.evidence_argument_chain import (
    EvidenceArgumentChain,
    EvidenceLink,
    ProofAssessment,
)


def test_sufficient_proof():
    pa = ProofAssessment(element_id="e1", claim="竊盜")
    pa.evidence_links = [
        EvidenceLink("ev1", "physical", "監視器畫面"),
        EvidenceLink("ev2", "testimonial", "證人證詞"),
    ]
    assert pa.assess() == "SUFFICIENT"


def test_needs_corroboration():
    pa = ProofAssessment(element_id="e1", claim="竊盜")
    pa.evidence_links = [EvidenceLink("ev1", "testimonial", "自白")]
    assert pa.assess() == "NEEDS_CORROBORATION"


def test_insufficient_proof():
    pa = ProofAssessment(element_id="e1", claim="竊盜")
    assert pa.assess() == "INSUFFICIENT"


def test_chain_overall_strength():
    chain = EvidenceArgumentChain(candidate_id="theft")
    pa1 = ProofAssessment(element_id="e1", claim="竊盜")
    pa1.evidence_links = [EvidenceLink("ev1", "physical", "x"), EvidenceLink("ev2", "testimonial", "y")]
    chain.add_assessment(pa1)
    assert chain.overall_strength() == "STRONG"


def test_chain_gaps():
    chain = EvidenceArgumentChain(candidate_id="theft")
    pa1 = ProofAssessment(element_id="e1", claim="竊盜")
    chain.add_assessment(pa1)
    gaps = chain.gaps()
    assert len(gaps) > 0