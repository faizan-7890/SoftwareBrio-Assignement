"""Extractor helpers for parsing social profiles and metadata from HTML."""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


SOCIAL_DOMAINS = {
    "twitter": ["twitter.com", "x.com"],
    "github": ["github.com"],
    "youtube": ["youtube.com"],
    "facebook": ["facebook.com"],
    "instagram": ["instagram.com"],
}


class HTMLExtractor:
    """Helper to extract metadata, social links, and titles from parsed HTML."""

    @staticmethod
    def extract_meta_info(html_content: str) -> Dict[str, str]:
        """Extracts title, meta description, and og:description."""
        meta_info: Dict[str, str] = {}
        if not html_content:
            return meta_info

        soup = BeautifulSoup(html_content, "html.parser")
        
        # Title
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            meta_info["title"] = title_tag.string.strip()

        # Meta description
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_info["description"] = desc_tag["content"].strip()

        # OpenGraph site name
        site_tag = soup.find("meta", attrs={"property": "og:site_name"})
        if site_tag and site_tag.get("content"):
            meta_info["site_name"] = site_tag["content"].strip()

        return meta_info

    @staticmethod
    def extract_social_links(links: List[str]) -> Dict[str, str]:
        """Classifies external links into social media channels."""
        social_map: Dict[str, str] = {}

        for link in links:
            lower = link.lower()
            for platform, domains in SOCIAL_DOMAINS.items():
                if any(domain in lower for domain in domains):
                    if platform not in social_map:
                        social_map[platform] = link

        return social_map
