"""Structured LLM extraction engine using Pydantic schemas and tool-calling / JSON parsing."""

import json
import logging
import re
from typing import List, Optional, Tuple
from openai import OpenAI

from agent.config import settings
from llm.client import LLMClientFactory, MockLLMClient
from models.schema import RawExtractedIntelligence, LeadershipMember

logger = logging.getLogger("llm.extractor")

SYSTEM_PROMPT = """You are an expert Autonomous Lead Enrichment Agent.
Your task is to analyze crawled company website text, DOM metadata, and signals to extract structured intelligence.

Follow these strict rules:
1. Company Overview: Provide a concise, highly accurate, EXACTLY 2-sentence summary of what the company does.
2. Target Audience / ICP (Ideal Customer Profile): Describe who their product is built for (e.g. 'Developers building backend applications', 'Enterprise sales leaders').
3. Contact Points: Extract any generic or public emails found (e.g. contact@, sales@, support@, info@). Combine discovered emails with any found in the text.
4. Key Leadership: Extract known executives, founders, C-suite officers, or key leaders with their full name, exact title/role, and LinkedIn profile URL if mentioned or discoverable.
5. Data Confidence Score: Calculate an estimated score between 0.0 and 1.0 reflecting how complete, authoritative, and clean the extracted data is.
6. Do NOT hallucinate false emails or names. If not confident, return empty lists or lower the confidence score.
"""


class StructuredExtractor:
    """Extracts schema-validated intelligence from pre-processed web text using an LLM."""

    def __init__(self):
        self.provider, self.client, self.model = LLMClientFactory.get_client()
        self.mock_client = MockLLMClient()

    def extract(
        self,
        domain: str,
        optimized_context: str,
        pre_extracted_emails: List[str],
        pre_extracted_linkedin: List[str]
    ) -> Tuple[RawExtractedIntelligence, int, int]:
        """
        Executes structured extraction via LLM or fallback mock.
        Returns: (RawExtractedIntelligence, prompt_tokens, completion_tokens)
        """
        if self.provider == "mock" or not self.client:
            logger.info(f"Using Mock/Offline LLM engine for {domain}")
            return self.mock_client.extract_mock_intelligence(
                domain=domain,
                crawled_text=optimized_context,
                found_emails=pre_extracted_emails,
                found_linkedin=pre_extracted_linkedin
            )

        try:
            return self._extract_with_llm(
                domain=domain,
                optimized_context=optimized_context,
                pre_extracted_emails=pre_extracted_emails,
                pre_extracted_linkedin=pre_extracted_linkedin
            )
        except Exception as e:
            logger.warning(f"Live LLM extraction failed ({e}). Falling back to Mock/Offline engine.")
            return self.mock_client.extract_mock_intelligence(
                domain=domain,
                crawled_text=optimized_context,
                found_emails=pre_extracted_emails,
                found_linkedin=pre_extracted_linkedin
            )

    def _extract_with_llm(
        self,
        domain: str,
        optimized_context: str,
        pre_extracted_emails: List[str],
        pre_extracted_linkedin: List[str]
    ) -> Tuple[RawExtractedIntelligence, int, int]:
        """Calls OpenAI / Groq / Ollama using structured parse or json_object format."""
        user_prompt = (
            f"Analyze this company's web intelligence and extract structured company data:\n\n"
            f"{optimized_context}\n\n"
            f"Pre-extracted candidate emails from DOM: {pre_extracted_emails}\n"
            f"Pre-extracted candidate LinkedIn links from DOM: {pre_extracted_linkedin}\n"
        )

        try:
            # First attempt: OpenAI structured outputs via beta.chat.completions.parse
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=RawExtractedIntelligence,
                temperature=0.1
            )
            parsed = completion.choices[0].message.parsed
            usage = completion.usage
            prompt_tokens = usage.prompt_tokens if usage else len(optimized_context) // 4
            completion_tokens = usage.completion_tokens if usage else 250
            if parsed:
                return parsed, prompt_tokens, completion_tokens
        except Exception as pe:
            logger.debug(f"Pydantic parse endpoint not supported ({pe}), attempting JSON mode...")

        # Fallback: standard json_object mode
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\nYou must output pure valid JSON conforming to the schema."},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content or "{}"
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else len(optimized_context) // 4
        completion_tokens = usage.completion_tokens if usage else 250

        # Parse JSON and validate against Pydantic
        data = json.loads(content)
        intelligence = RawExtractedIntelligence.model_validate(data)
        return intelligence, prompt_tokens, completion_tokens
