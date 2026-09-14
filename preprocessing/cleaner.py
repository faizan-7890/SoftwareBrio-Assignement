"""DOM cleaning and boilerplate removal for token optimization."""

import re
from typing import Dict, List, Set, Tuple
from bs4 import BeautifulSoup, Comment


# Regex for public contact emails (ignoring common image/font extensions or false positives)
EMAIL_REGEX = re.compile(
    r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b",
    re.IGNORECASE
)

# Regex for LinkedIn profile URLs
LINKEDIN_PROFILE_REGEX = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?",
    re.IGNORECASE
)

# Regex for LinkedIn company URLs
LINKEDIN_COMPANY_REGEX = re.compile(
    r"https?://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9_-]+/?",
    re.IGNORECASE
)

# Common noisy extensions that look like email addresses (e.g. name@2x.png)
IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".css", ".js", ".woff", ".woff2", ".ttf", ".eot"
}

# Tags that never contain useful semantic text for LLM intelligence
TAGS_TO_REMOVE = [
    "script", "style", "noscript", "svg", "canvas", "iframe",
    "video", "audio", "source", "track", "object", "embed",
    "applet", "frame", "frameset"
]

# Secondary structural tags that frequently contain boilerplate
BOILERPLATE_TAGS = ["nav", "footer", "aside"]


class DOMCleaner:
    """Pre-processes raw HTML to extract high-signal text, emails, and links while stripping DOM bloat."""

    @staticmethod
    def clean_html(html_content: str) -> Tuple[str, List[str], List[str]]:
        """
        Parses raw HTML, strips boilerplate, and extracts:
        1. Cleaned text content
        2. Extracted public email addresses
        3. Discovered LinkedIn URLs
        """
        if not html_content or not html_content.strip():
            return "", [], []

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 2. Extract emails and links BEFORE deleting tags
        raw_emails: Set[str] = set()
        linkedin_urls: Set[str] = set()

        # Check mailto: links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if href.lower().startswith("mailto:"):
                clean_mail = DOMCleaner._sanitize_email(href[7:].split("?")[0])
                if DOMCleaner._is_valid_email(clean_mail):
                    raw_emails.add(clean_mail)
            
            # Check LinkedIn URLs in href
            if "linkedin.com/in/" in href.lower() or "linkedin.com/company/" in href.lower():
                linkedin_urls.add(href)

        # Regex scan raw HTML for emails
        for match in EMAIL_REGEX.findall(html_content):
            clean_mail = DOMCleaner._sanitize_email(match)
            if DOMCleaner._is_valid_email(clean_mail):
                raw_emails.add(clean_mail)

        # Regex scan raw HTML for linkedin
        for match in LINKEDIN_PROFILE_REGEX.findall(html_content):
            linkedin_urls.add(match)

        # 3. Strip non-content and media tags
        for tag_name in TAGS_TO_REMOVE:
            for el in soup.find_all(tag_name):
                el.decompose()

        # 4. Strip boilerplate containers (nav, footer, aside) but keep a compressed copy if small
        for tag_name in BOILERPLATE_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        # Remove elements with common boilerplate classes/ids
        boilerplate_patterns = re.compile(
            r"(cookie-banner|cookie-consent|gdpr|popup|modal-backdrop|advertisement|ad-banner)",
            re.IGNORECASE
        )
        for el in soup.find_all(attrs={"class": boilerplate_patterns}):
            el.decompose()
        for el in soup.find_all(attrs={"id": boilerplate_patterns}):
            el.decompose()

        # 5. Extract structured text
        text = soup.get_text(separator="\n", strip=True)

        # Clean multiple blank lines
        cleaned_text = re.sub(r"\n{3,}", "\n\n", text)
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)

        return cleaned_text, sorted(list(raw_emails)), sorted(list(linkedin_urls))

    @staticmethod
    def _sanitize_email(raw_email: str) -> str:
        """Sanitizes raw email strings removing escaped HTML entity prefixes."""
        clean = raw_email.strip().lower()
        clean = re.sub(r"^(?:u003[ce]|u002[27]|gt;|lt;|&gt;|&lt;|>|<|\"|')+", "", clean)
        clean = re.sub(r"[>\"']+$", "", clean)
        return clean.strip()

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Filter out false-positive emails like image assets, placeholders, etc."""
        if not email or "@" not in email:
            return False
        email = email.strip().lower()
        if any(email.endswith(ext) for ext in IGNORED_EXTENSIONS):
            return False
        if email.startswith("example") or "yoursite.com" in email or "domain.com" in email:
            return False
        # Ensure domain has at least one dot and length > 4
        parts = email.split("@")
        if len(parts) != 2 or "." not in parts[1]:
            return False
        # Reject package@1.2.3 version strings (domain must contain alpha characters)
        domain_part = parts[1]
        if not re.search(r"[a-zA-Z]", domain_part):
            return False
        # TLD must be letters
        tld = domain_part.split(".")[-1]
        if not tld.isalpha() or len(tld) < 2:
            return False
        if len(parts[0]) < 1 or len(parts[1]) < 3:
            return False
        return True
