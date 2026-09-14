"""LeadEnrichmentAgent orchestrator coordinating crawling, cleaning, LLM extraction, and enrichment."""

import logging
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

from agent.config import settings
from crawler.browser import BrowserCrawler
from crawler.discovery import LinkDiscovery
from crawler.extractor import HTMLExtractor
from enrichment.search import ExternalSearchEnricher
from llm.extractor import StructuredExtractor
from metrics.cost_tracker import CostTracker
from models.schema import (
    BatchEnrichmentReport,
    CompanyEnrichmentData,
    LeadershipMember,
)
from preprocessing.cleaner import DOMCleaner
from preprocessing.markdown import TokenOptimizer

logger = logging.getLogger("agent.orchestrator")


class LeadEnrichmentAgent:
    """Autonomous Agent for crawling company domains and extracting structured intelligence."""

    def __init__(self):
        self.crawler = BrowserCrawler(
            headless=settings.headless,
            timeout_ms=settings.page_timeout_ms
        )
        self.extractor = StructuredExtractor()
        self.search_enricher = ExternalSearchEnricher()
        self.cost_tracker = CostTracker()

    def process_domain(self, domain: str) -> CompanyEnrichmentData:
        """
        Executes end-to-end enrichment for a single target domain:
        1. Normalizes domain and fetches homepage.
        2. Discovers high-priority subpages (/about, /team, /contact, /pricing).
        3. Crawls subpages and strips DOM bloat to optimize tokens.
        4. Invokes LLM for structured intelligence extraction (Pydantic).
        5. (Bonus) Enriches missing founder/leadership LinkedIn profiles via external search.
        6. Computes final calibrated confidence score and logs token costs.
        """
        clean_domain = domain.strip().lower()
        if clean_domain.startswith("http://") or clean_domain.startswith("https://"):
            base_url = clean_domain
            clean_domain = urlparse(clean_domain).netloc
        else:
            base_url = f"https://{clean_domain}"

        logger.info(f"Starting enrichment pipeline for domain: {clean_domain} ({base_url})")

        sources_crawled: List[str] = []
        crawled_pages_text: Dict[str, str] = {}
        all_emails: Set[str] = set()
        all_linkedin: Set[str] = set()

        try:
            # 1. Fetch homepage
            logger.info(f"Fetching homepage: {base_url}")
            home_html, home_links = self.crawler.fetch_page(base_url)

            if not home_html:
                logger.warning(f"Could not retrieve homepage for {clean_domain}. Attempting HTTP protocol fallback.")
                fallback_url = f"http://{clean_domain}"
                home_html, home_links = self.crawler.fetch_page(fallback_url)
                if home_html:
                    base_url = fallback_url

            if not home_html:
                logger.error(f"Failed to fetch content for domain: {clean_domain}")
                return CompanyEnrichmentData(
                    domain=clean_domain,
                    company_name=clean_domain.split(".")[0].capitalize(),
                    company_overview="Unable to retrieve public web presence. Target server did not respond.",
                    target_audience_icp="Unknown",
                    contact_emails=[],
                    key_leadership=[],
                    data_confidence_score=0.0,
                    sources_crawled=[],
                    error="Connection timeout or server unreachable"
                )

            sources_crawled.append(base_url)

            # Clean and extract from homepage
            home_text, home_emails, home_li = DOMCleaner.clean_html(home_html)
            all_emails.update(home_emails)
            all_linkedin.update(home_li)
            crawled_pages_text[base_url] = home_text

            # 2. Discover relevant subpages (/about, /team, /company, /contact, /pricing)
            candidate_subpages = LinkDiscovery.get_candidate_subpages(
                base_url=base_url,
                found_links=home_links,
                max_subpages=settings.max_subpages_per_domain
            )
            logger.info(f"Discovered {len(candidate_subpages)} relevant subpages for {clean_domain}: {candidate_subpages}")

            # 3. Crawl discovered subpages
            for subpage_url in candidate_subpages:
                logger.info(f"Crawling subpage: {subpage_url}")
                sub_html, _ = self.crawler.fetch_page(subpage_url)
                if sub_html:
                    sources_crawled.append(subpage_url)
                    sub_text, sub_emails, sub_li = DOMCleaner.clean_html(sub_html)
                    all_emails.update(sub_emails)
                    all_linkedin.update(sub_li)
                    crawled_pages_text[subpage_url] = sub_text

            # 4. Preprocess and format token-optimized context
            token_optimized_context = TokenOptimizer.build_llm_context(
                domain=clean_domain,
                pages_content=crawled_pages_text,
                pre_extracted_emails=sorted(list(all_emails)),
                pre_extracted_linkedin=sorted(list(all_linkedin)),
                max_total_chars=settings.max_text_tokens_per_page * 4
            )

            # 5. Extract structured intelligence with LLM (or mock fallback)
            logger.info(f"Extracting structured intelligence via {self.extractor.provider} ({self.extractor.model})...")
            raw_intel, prompt_tokens, completion_tokens = self.extractor.extract(
                domain=clean_domain,
                optimized_context=token_optimized_context,
                pre_extracted_emails=sorted(list(all_emails)),
                pre_extracted_linkedin=sorted(list(all_linkedin))
            )

            # Record token and cost metrics
            self.cost_tracker.record_usage(
                domain=clean_domain,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model_name=self.extractor.model
            )

            # 6. Bonus: External LinkedIn search for leadership members missing URLs
            final_leadership: List[LeadershipMember] = []
            for leader in raw_intel.key_leadership:
                if not leader.linkedin_url and settings.enable_external_linkedin_search:
                    logger.info(f"Searching external LinkedIn for: {leader.name} ({raw_intel.company_name})")
                    found_url = self.search_enricher.find_linkedin_profile(
                        company_name=raw_intel.company_name,
                        person_name=leader.name
                    )
                    if found_url:
                        leader.linkedin_url = found_url
                        leader.source = "external_search"
                final_leadership.append(leader)

            # Merge any pre-extracted emails with LLM emails
            final_emails = sorted(list(set(raw_intel.contact_emails + list(all_emails))))

            # Calibrate confidence score
            confidence = self._calibrate_confidence(
                base_score=raw_intel.data_confidence_score,
                sources_count=len(sources_crawled),
                emails_count=len(final_emails),
                leaders_count=len(final_leadership)
            )

            return CompanyEnrichmentData(
                domain=clean_domain,
                company_name=raw_intel.company_name,
                company_overview=raw_intel.company_overview,
                target_audience_icp=raw_intel.target_audience_icp,
                contact_emails=final_emails,
                key_leadership=final_leadership,
                key_products_features=raw_intel.key_products_features,
                data_confidence_score=round(confidence, 2),
                sources_crawled=sources_crawled,
                error=None
            )

        except Exception as e:
            logger.error(f"Unexpected error enriching {clean_domain}: {e}", exc_info=True)
            return CompanyEnrichmentData(
                domain=clean_domain,
                company_name=clean_domain.split(".")[0].capitalize(),
                company_overview="Error encountered during enrichment pipeline execution.",
                target_audience_icp="Unknown",
                contact_emails=[],
                key_leadership=[],
                data_confidence_score=0.0,
                sources_crawled=sources_crawled,
                error=str(e)
            )

    def _calibrate_confidence(
        self,
        base_score: float,
        sources_count: int,
        emails_count: int,
        leaders_count: int
    ) -> float:
        """Calibrates confidence score based on completeness of discovered data points."""
        score = base_score
        # Bonus for comprehensive multi-page crawling
        if sources_count >= 2:
            score += 0.05
        # Bonus for finding verified contact emails
        if emails_count > 0:
            score += 0.05
        # Bonus for identifying key leadership
        if leaders_count > 0:
            score += 0.05
        return min(max(score, 0.1), 1.0)

    def run_batch(self, domains: List[str]) -> BatchEnrichmentReport:
        """Runs enrichment sequentially across an array of company domains with full fault tolerance."""
        start_time = time.time()
        self.crawler.start()

        results: List[CompanyEnrichmentData] = []
        successful = 0
        failed = 0

        try:
            for domain in domains:
                result = self.process_domain(domain)
                results.append(result)
                if result.error:
                    failed += 1
                else:
                    successful += 1
        finally:
            self.crawler.close()

        elapsed = time.time() - start_time
        summary = self.cost_tracker.get_summary()

        return BatchEnrichmentReport(
            results=results,
            total_domains=len(domains),
            successful_domains=successful,
            failed_domains=failed,
            total_prompt_tokens=summary["total_prompt_tokens"],
            total_completion_tokens=summary["total_completion_tokens"],
            total_tokens=summary["total_tokens"],
            estimated_cost_usd=summary["total_estimated_cost_usd"],
            execution_time_seconds=round(elapsed, 2)
        )
