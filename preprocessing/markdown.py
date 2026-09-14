"""Markdown formatter and token optimizer."""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class TokenOptimizer:
    """Formats and optimizes crawled content into concise, token-efficient Markdown for LLM extraction."""

    @staticmethod
    def html_to_markdown(html_content: str, max_chars: int = 12000) -> str:
        """
        Converts HTML into structured markdown with headings and lists,
        avoiding raw DOM boilerplate and respecting a character/token budget.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, "html.parser")
        
        # Build markdown lines
        lines: List[str] = []

        for element in soup.descendants:
            if element.name in ["h1", "h2", "h3"]:
                text = element.get_text(strip=True)
                if text:
                    prefix = "#" * int(element.name[1])
                    lines.append(f"\n{prefix} {text}\n")
            elif element.name == "p":
                text = element.get_text(strip=True)
                if text and len(text) > 10:
                    lines.append(f"{text}\n")
            elif element.name == "li":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"- {text}")

        full_md = "\n".join(lines).strip()
        if not full_md:
            # Fallback to plain text
            full_md = soup.get_text(separator="\n", strip=True)

        if len(full_md) > max_chars:
            full_md = full_md[:max_chars] + "\n\n...[Content truncated for token efficiency]..."

        return full_md

    @staticmethod
    def build_llm_context(
        domain: str,
        pages_content: Dict[str, str],
        pre_extracted_emails: List[str],
        pre_extracted_linkedin: List[str],
        max_total_chars: int = 24000
    ) -> str:
        """
        Synthesizes multi-page crawled content into a compact prompt payload.
        """
        parts = [
            f"# Company Domain: {domain}",
            "",
            "## Pre-Extracted Public Signals from DOM:",
            f"- Discovered Public Emails: {', '.join(pre_extracted_emails) if pre_extracted_emails else 'None directly detected'}",
            f"- Discovered LinkedIn Profiles: {', '.join(pre_extracted_linkedin) if pre_extracted_linkedin else 'None directly detected'}",
            "",
            "## Crawled Page Contents:"
        ]

        chars_used = sum(len(p) for p in parts)

        for url, content in pages_content.items():
            if chars_used >= max_total_chars:
                break
            
            remaining = max_total_chars - chars_used
            page_snippet = content[:remaining]
            
            page_section = f"\n### Page: {url}\n{page_snippet}\n"
            parts.append(page_section)
            chars_used += len(page_section)

        return "\n".join(parts)
