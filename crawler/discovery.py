"""Subpage discovery and link prioritizer for targeted company crawling."""

import re
from typing import List, Set
from urllib.parse import urljoin, urlparse


PRIORITY_KEYWORDS = [
    # Top priority: About / Leadership / Team
    ("leadership", 10),
    ("our-team", 10),
    ("team", 9),
    ("about", 8),
    ("company", 7),
    ("people", 7),
    ("story", 6),
    # Contact priority
    ("contact", 8),
    ("support", 5),
    # Business / Product priority
    ("pricing", 6),
    ("products", 5),
    ("solutions", 4),
]

EXCLUDED_EXTENSIONS = {
    ".pdf", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg",
    ".mp4", ".svg", ".xml", ".rss", ".css", ".js"
}

EXCLUDED_PATHS = [
    "/blog", "/news", "/press", "/docs", "/documentation",
    "/changelog", "/legal", "/privacy", "/terms", "/status",
    "/tags", "/categories", "/author", "/wp-content", "/login",
    "/signup", "/register", "/cart", "/checkout"
]


class LinkDiscovery:
    """Discovers and prioritizes high-value subpages from a company homepage."""

    @staticmethod
    def get_candidate_subpages(
        base_url: str,
        found_links: List[str],
        max_subpages: int = 4
    ) -> List[str]:
        """
        Filters and scores discovered links to return the top most relevant subpages
        (e.g., /about, /team, /company, /contact, /pricing).
        """
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc.lower()
        if base_domain.startswith("www."):
            base_domain = base_domain[4:]

        scored_links = []
        seen_urls: Set[str] = set()

        for link in found_links:
            if not link or link.startswith("#") or link.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, link).strip()
            parsed = urlparse(full_url)
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]

            # Must belong to the exact same domain
            if netloc != base_domain:
                continue

            # Strip query params and fragments for deduplication
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
            if clean_url in seen_urls or clean_url == base_url.rstrip("/"):
                continue

            path_lower = parsed.path.lower()

            # Skip file extensions
            if any(path_lower.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                continue

            # Skip excluded paths
            if any(path_lower.startswith(p) or f"/{p.strip('/')}/" in path_lower for p in EXCLUDED_PATHS):
                continue

            # Calculate priority score
            score = 0
            for keyword, weight in PRIORITY_KEYWORDS:
                if re.search(rf"\b{keyword}\b", path_lower) or f"/{keyword}" in path_lower or f"-{keyword}" in path_lower:
                    score += weight

            if score > 0:
                seen_urls.add(clean_url)
                scored_links.append((score, clean_url))

        # Sort by highest score first, then by shortest URL length
        scored_links.sort(key=lambda item: (-item[0], len(item[1])))

        return [url for _, url in scored_links[:max_subpages]]
