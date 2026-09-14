"""Pydantic schemas for autonomous lead enrichment agent."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LeadershipMember(BaseModel):
    """Information about a key executive, founder, or team member."""
    name: str = Field(description="Full name of the executive or team member")
    title: str = Field(description="Role, title, or position within the company")
    linkedin_url: Optional[str] = Field(
        default=None,
        description="Direct LinkedIn profile URL if discoverable"
    )
    source: Optional[str] = Field(
        default="website",
        description="Source where profile was identified (e.g. website, external_search)"
    )

    @field_validator("linkedin_url")
    @classmethod
    def clean_linkedin_url(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        if not v or v.lower() == "none" or v.lower() == "null":
            return None
        if not (v.startswith("http://") or v.startswith("https://")):
            v = f"https://{v}"
        return v


class ContactPoints(BaseModel):
    """Public contact channels identified for the company."""
    emails: List[str] = Field(
        default_factory=list,
        description="Generic or public emails (e.g., contact@, sales@, support@)"
    )
    phone_numbers: List[str] = Field(
        default_factory=list,
        description="Public contact phone numbers"
    )
    social_profiles: Dict[str, str] = Field(
        default_factory=dict,
        description="Social links (Twitter/X, GitHub, YouTube, etc.)"
    )


class RawExtractedIntelligence(BaseModel):
    """Structured intelligence schema extracted directly by the LLM."""
    company_name: str = Field(
        description="Official brand or company name"
    )
    company_overview: str = Field(
        description="A concise 2-sentence summary of what the company does."
    )
    target_audience_icp: str = Field(
        description="Who their product is built for (Ideal Customer Profile, e.g., 'Developers building backend applications')."
    )
    contact_emails: List[str] = Field(
        default_factory=list,
        description="Generic or public emails found on the site (e.g., contact@, sales@, support@)"
    )
    key_leadership: List[LeadershipMember] = Field(
        default_factory=list,
        description="Names, roles/titles, and LinkedIn profile URLs of key leadership/team members"
    )
    key_products_features: List[str] = Field(
        default_factory=list,
        description="Key features, products, or value propositions"
    )
    data_confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated score between 0.0 and 1.0 indicating the quality/completeness of the extracted data."
    )


class CompanyEnrichmentData(BaseModel):
    """Final enriched data payload for a single company domain."""
    domain: str = Field(description="Target domain analyzed")
    company_name: str = Field(description="Official company name")
    company_overview: str = Field(
        description="A concise 2-sentence summary of what they do"
    )
    target_audience_icp: str = Field(
        description="Who their product is built for (e.g. 'Developers building backend applications')"
    )
    contact_emails: List[str] = Field(
        default_factory=list,
        description="Public generic contact emails"
    )
    key_leadership: List[LeadershipMember] = Field(
        default_factory=list,
        description="Leadership and key team members with LinkedIn URLs"
    )
    key_products_features: List[str] = Field(
        default_factory=list,
        description="High-level products or features"
    )
    data_confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Data confidence score between 0.0 and 1.0"
    )
    sources_crawled: List[str] = Field(
        default_factory=list,
        description="List of URLs successfully crawled and parsed"
    )
    enrichment_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of when enrichment was performed"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if crawling or extraction encountered issues"
    )


class BatchEnrichmentReport(BaseModel):
    """Summary report across all processed domains including cost & performance metrics."""
    results: List[CompanyEnrichmentData] = Field(default_factory=list)
    total_domains: int = 0
    successful_domains: int = 0
    failed_domains: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    execution_time_seconds: float = 0.0
