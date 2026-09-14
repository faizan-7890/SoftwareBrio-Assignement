"""External search engine integration for founder/leadership LinkedIn profile lookup."""

import logging
import re
from typing import Optional
import httpx

from agent.config import settings

logger = logging.getLogger("enrichment.search")

LINKEDIN_URL_PATTERN = re.compile(
    r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?",
    re.IGNORECASE
)


class ExternalSearchEnricher:
    """Enriches leadership contacts by finding external LinkedIn URLs via search engines."""

    def __init__(self):
        self.tavily_key = settings.tavily_api_key
        self.serpapi_key = settings.serpapi_api_key

    def find_linkedin_profile(self, company_name: str, person_name: str) -> Optional[str]:
        """
        Executes a targeted search query for the person's LinkedIn profile.
        Query format: '{company_name} {person_name} site:linkedin.com/in'
        """
        if not person_name or not person_name.strip():
            return None

        query = f'"{person_name}" "{company_name}" site:linkedin.com/in'

        # 1. Try Tavily if configured
        if self.tavily_key:
            url = self._search_tavily(query)
            if url:
                return url

        # 2. Try SerpAPI if configured
        if self.serpapi_key:
            url = self._search_serpapi(query)
            if url:
                return url

        # 3. DuckDuckGo search (Zero API key required)
        url = self._search_duckduckgo(query)
        if url:
            return url

        return None

    def _search_duckduckgo(self, query: str) -> Optional[str]:
        """Queries DuckDuckGo for LinkedIn profile URLs."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                for res in results:
                    href = res.get("href", "")
                    match = LINKEDIN_URL_PATTERN.search(href)
                    if match:
                        clean = match.group(0).rstrip("/")
                        logger.info(f"Found LinkedIn via DuckDuckGo: {clean}")
                        return clean
        except Exception as e:
            logger.debug(f"DuckDuckGo search failed for query '{query}': {e}")
        return None

    def _search_tavily(self, query: str) -> Optional[str]:
        """Queries Tavily API if configured."""
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 3,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    for r in data.get("results", []):
                        match = LINKEDIN_URL_PATTERN.search(r.get("url", ""))
                        if match:
                            return match.group(0).rstrip("/")
        except Exception as e:
            logger.debug(f"Tavily search error: {e}")
        return None

    def _search_serpapi(self, query: str) -> Optional[str]:
        """Queries SerpAPI if configured."""
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(
                    "https://serpapi.com/search",
                    params={
                        "api_key": self.serpapi_key,
                        "engine": "google",
                        "q": query,
                        "num": 3,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    for r in data.get("organic_results", []):
                        link = r.get("link", "")
                        match = LINKEDIN_URL_PATTERN.search(link)
                        if match:
                            return match.group(0).rstrip("/")
        except Exception as e:
            logger.debug(f"SerpAPI search error: {e}")
        return None
