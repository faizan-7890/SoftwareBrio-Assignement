"""Integration tests for the enrichment pipeline and LinkDiscovery."""

import pytest
from crawler.discovery import LinkDiscovery
from metrics.cost_tracker import CostTracker
from agent.orchestrator import LeadEnrichmentAgent
from agent.config import settings


def test_link_discovery_prioritization():
    base_url = "https://example.com"
    raw_links = [
        "/",
        "/about",
        "/team",
        "/contact-us",
        "/pricing",
        "/blog/2024/new-feature",
        "/docs/api",
        "/privacy",
        "https://external.com/page",
        "#hero-section",
        "mailto:info@example.com"
    ]

    candidates = LinkDiscovery.get_candidate_subpages(base_url, raw_links, max_subpages=4)
    # Check that high-value links are captured and blogs/external are skipped
    assert any("/about" in c for c in candidates)
    assert any("/team" in c for c in candidates)
    assert any("/contact" in c for c in candidates)
    assert not any("external.com" in c for c in candidates)
    assert not any("blog" in c for c in candidates)
    assert len(candidates) <= 4


def test_cost_tracker_calculation():
    tracker = CostTracker()
    rec = tracker.record_usage(
        domain="example.com",
        prompt_tokens=1000,
        completion_tokens=500,
        model_name="gpt-4o-mini"
    )
    assert rec["total_tokens"] == 1500
    # gpt-4o-mini: $0.15/1M prompt, $0.60/1M completion
    # 1000/1M * 0.15 = 0.00015
    # 500/1M * 0.60 = 0.00030
    # total = 0.00045
    assert rec["estimated_cost_usd"] == 0.00045

    summary = tracker.get_summary()
    assert summary["total_tokens"] == 1500
    assert summary["total_estimated_cost_usd"] == 0.00045


def test_agent_process_domain_mock_mode():
    settings.llm_provider = "mock"
    agent = LeadEnrichmentAgent()
    # Test on synthetic domain
    res = agent.process_domain("vapi.ai")
    assert res.domain == "vapi.ai"
    assert res.company_name == "Vapi"
    assert len(res.company_overview.split(".")) >= 2
    assert res.data_confidence_score > 0.0
    assert len(res.key_leadership) > 0


def test_agent_graceful_handling_invalid_domain():
    agent = LeadEnrichmentAgent()
    # Unreachable non-existent domain should not raise an unhandled exception
    res = agent.process_domain("this-domain-definitely-does-not-exist-xyz123.com")
    assert res.data_confidence_score == 0.0
    assert res.error is not None
