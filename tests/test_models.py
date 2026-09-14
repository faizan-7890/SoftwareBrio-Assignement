"""Unit tests for Pydantic models and schemas."""

import pytest
from pydantic import ValidationError
from models.schema import (
    LeadershipMember,
    ContactPoints,
    RawExtractedIntelligence,
    CompanyEnrichmentData,
    BatchEnrichmentReport
)


def test_leadership_member_url_normalization():
    member = LeadershipMember(
        name="Alex Smith",
        title="CEO",
        linkedin_url="www.linkedin.com/in/alexsmith"
    )
    assert member.linkedin_url == "https://www.linkedin.com/in/alexsmith"

    member_none = LeadershipMember(
        name="Alex Smith",
        title="CEO",
        linkedin_url="none"
    )
    assert member_none.linkedin_url is None


def test_raw_extracted_intelligence_validation():
    intel = RawExtractedIntelligence(
        company_name="TestCorp",
        company_overview="TestCorp builds developer tools. They empower software teams globally.",
        target_audience_icp="Software developers",
        contact_emails=["team@testcorp.com"],
        key_leadership=[
            LeadershipMember(name="Alice", title="Founder", linkedin_url="https://linkedin.com/in/alice")
        ],
        key_products_features=["Cloud IDE", "CLI"],
        data_confidence_score=0.92
    )
    assert intel.company_name == "TestCorp"
    assert intel.data_confidence_score == 0.92
    assert len(intel.contact_emails) == 1


def test_data_confidence_score_boundaries():
    # Confidence score must be between 0.0 and 1.0
    with pytest.raises(ValidationError):
        RawExtractedIntelligence(
            company_name="Test",
            company_overview="Sentence 1. Sentence 2.",
            target_audience_icp="Developers",
            data_confidence_score=1.5  # Invalid: > 1.0
        )

    with pytest.raises(ValidationError):
        RawExtractedIntelligence(
            company_name="Test",
            company_overview="Sentence 1. Sentence 2.",
            target_audience_icp="Developers",
            data_confidence_score=-0.1  # Invalid: < 0.0
        )


def test_batch_enrichment_report_serialization():
    company = CompanyEnrichmentData(
        domain="testcorp.com",
        company_name="TestCorp",
        company_overview="Sentence one. Sentence two.",
        target_audience_icp="Enterprise engineers",
        contact_emails=["support@testcorp.com"],
        key_leadership=[],
        data_confidence_score=0.85,
        sources_crawled=["https://testcorp.com"]
    )
    report = BatchEnrichmentReport(
        results=[company],
        total_domains=1,
        successful_domains=1,
        failed_domains=0,
        total_tokens=500,
        estimated_cost_usd=0.0001
    )
    serialized = report.model_dump()
    assert serialized["total_domains"] == 1
    assert serialized["results"][0]["domain"] == "testcorp.com"
