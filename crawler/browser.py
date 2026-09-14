"""Headless browser crawler using Playwright with anti-bot resilience and resource optimization."""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from bs4 import BeautifulSoup
import httpx
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Error as PlaywrightError

from agent.config import settings

logger = logging.getLogger("crawler.browser")


class BrowserCrawler:
    """Headless browser automation engine for dynamic JS-rendered company websites."""

    def __init__(self, headless: bool = True, timeout_ms: int = 25000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    def start(self):
        """Initializes Playwright and launches the headless Chromium instance."""
        if self._browser is None:
            try:
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                    ]
                )
                self._context = self._browser.new_context(
                    user_agent=settings.user_agent,
                    viewport={"width": 1280, "height": 800},
                    locale="en-US",
                    timezone_id="America/New_York",
                )
                # Block heavy media and fonts to reduce latency by ~70%
                self._context.route(
                    re.compile(r"\.(png|jpg|jpeg|gif|webp|svg|woff|woff2|ttf|eot|mp4|webm|avi)(\?.*)?$", re.IGNORECASE),
                    lambda route: route.abort()
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Playwright browser: {e}. Will fallback to HTTP client.")
                self._browser = None

    def close(self):
        """Cleanly tears down the browser context and Playwright instance."""
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
            self._context = None
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    def fetch_page(self, url: str) -> Tuple[Optional[str], List[str]]:
        """
        Navigates to URL, waits for dynamic content to render, and extracts raw HTML and discovered links.
        Returns: (html_content, list_of_links)
        """
        # Try Playwright first
        if self._browser and self._context:
            try:
                return self._fetch_with_playwright(url)
            except Exception as e:
                logger.warning(f"Playwright navigation failed for {url} ({e}). Falling back to HTTP request.")

        # Fallback to httpx
        return self._fetch_with_httpx(url)

    def _fetch_with_playwright(self, url: str) -> Tuple[Optional[str], List[str]]:
        page: Optional[Page] = None
        try:
            page = self._context.new_page()
            # Set default navigation timeout
            page.set_default_navigation_timeout(self.timeout_ms)
            page.set_default_timeout(self.timeout_ms)

            # Navigate
            response = page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            if response and response.status >= 400:
                logger.warning(f"HTTP status {response.status} for {url}")
                if response.status == 404:
                    return None, []

            # Wait a brief moment for dynamic client-side JS / hydration
            page.wait_for_timeout(settings.wait_after_load_ms)

            # Quick scroll to trigger lazy loaded content
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
                page.wait_for_timeout(500)
            except Exception:
                pass

            html = page.content()

            # Extract links from DOM
            links = []
            try:
                links = page.evaluate("""() => {
                    const anchors = Array.from(document.querySelectorAll('a[href]'));
                    return anchors.map(a => a.getAttribute('href')).filter(Boolean);
                }""")
            except Exception:
                # Fallback link extraction via BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")
                links = [a["href"] for a in soup.find_all("a", href=True)]

            return html, links

        except PlaywrightError as pe:
            logger.warning(f"Playwright error loading {url}: {pe}")
            return None, []
        finally:
            if page:
                try:
                    page.close()
                except Exception:
                    pass

    def _fetch_with_httpx(self, url: str) -> Tuple[Optional[str], List[str]]:
        """HTTP client fallback for resilience against browser issues or bot shields."""
        headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            with httpx.Client(follow_redirects=True, timeout=15.0, headers=headers) as client:
                resp = client.get(url)
                if resp.status_code >= 400:
                    logger.warning(f"HTTP fallback returned status {resp.status_code} for {url}")
                    return None, []
                html = resp.text
                soup = BeautifulSoup(html, "html.parser")
                links = [a["href"] for a in soup.find_all("a", href=True)]
                return html, links
        except Exception as e:
            logger.error(f"HTTP fallback request failed for {url}: {e}")
            return None, []
