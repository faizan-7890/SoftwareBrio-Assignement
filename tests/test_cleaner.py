"""Unit tests for DOMCleaner and token pre-processing."""

import pytest
from preprocessing.cleaner import DOMCleaner
from preprocessing.markdown import TokenOptimizer


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Acme Inc - API Platform</title>
    <style>body { font-size: 14px; }</style>
    <script>console.log("analytics tracking code");</script>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/pricing">Pricing</a>
    </nav>
    <div class="cookie-consent">Please accept our cookie policy.</div>
    <main>
        <h1>Build Better APIs Faster</h1>
        <p>Acme Inc is the world leading platform for engineering teams to design and test APIs.</p>
        <p>Contact our team directly at <a href="mailto:support@acme.com">support@acme.com</a> or sales@acme.com for enterprise inquiries.</p>
        <a href="https://www.linkedin.com/in/john-doe-ceo">Connect with CEO John Doe on LinkedIn</a>
    </main>
    <footer>
        <p>© 2026 Acme Inc. All rights reserved.</p>
    </footer>
    <svg><circle cx="50" cy="50" r="40" /></svg>
</body>
</html>
"""


def test_clean_html_strips_boilerplate():
    text, emails, linkedin = DOMCleaner.clean_html(SAMPLE_HTML)

    # Assert scripts and styles are gone
    assert "analytics tracking code" not in text
    assert "font-size" not in text
    # Assert boilerplate nav/footer is stripped
    assert "cookie policy" not in text
    # Assert content is preserved
    assert "Build Better APIs Faster" in text
    assert "Acme Inc is the world leading platform" in text

    # Assert emails extracted
    assert "support@acme.com" in emails
    assert "sales@acme.com" in emails

    # Assert LinkedIn profile extracted
    assert any("john-doe-ceo" in url for url in linkedin)


def test_email_validation_filters_images():
    assert not DOMCleaner._is_valid_email("banner@2x.png")
    assert not DOMCleaner._is_valid_email("avatar@3x.jpg")
    assert not DOMCleaner._is_valid_email("express@4.18.2")
    assert not DOMCleaner._is_valid_email("notanemail")
    assert DOMCleaner._is_valid_email("contact@supabase.com")
    assert DOMCleaner._is_valid_email("hello@postman.com")


def test_email_sanitization():
    assert DOMCleaner._sanitize_email("u003ehelp@postman.com") == "help@postman.com"
    assert DOMCleaner._sanitize_email("&gt;sales@postman.com") == "sales@postman.com"
    assert DOMCleaner._sanitize_email("'info@postman.com'") == "info@postman.com"


def test_markdown_formatting():
    md = TokenOptimizer.html_to_markdown(SAMPLE_HTML, max_chars=1000)
    assert "# Build Better APIs Faster" in md
    assert "Acme Inc is the world leading platform" in md
