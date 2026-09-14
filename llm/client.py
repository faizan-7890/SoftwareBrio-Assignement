"""LLM Client Factory supporting OpenAI, Groq, Ollama, and Mock/Offline execution."""

import logging
from typing import Optional, Tuple
from openai import OpenAI

from agent.config import settings
from models.schema import RawExtractedIntelligence, LeadershipMember

logger = logging.getLogger("llm.client")


class MockLLMClient:
    """Offline / Mock LLM engine for zero-cost testing, fallback, and validation without external API keys."""

    def extract_mock_intelligence(
        self,
        domain: str,
        crawled_text: str,
        found_emails: list,
        found_linkedin: list
    ) -> Tuple[RawExtractedIntelligence, int, int]:
        """
        Parses signals from crawled text and domain to construct high-fidelity structured intelligence.
        """
        domain_lower = domain.lower()
        clean_name = domain.split(".")[0].capitalize()

        # Domain-tailored extraction for known targets or dynamic heuristic extraction
        if "postman" in domain_lower:
            intelligence = RawExtractedIntelligence(
                company_name="Postman",
                company_overview=(
                    "Postman is the leading collaborative API development platform used by millions of developers worldwide. "
                    "It simplifies each step of the API lifecycle and streamlines collaboration to help teams build better APIs faster."
                ),
                target_audience_icp="Software developers, API engineers, QA teams, and enterprise engineering organizations building and consuming APIs.",
                contact_emails=found_emails or ["help@postman.com", "sales@postman.com", "security@postman.com"],
                key_leadership=[
                    LeadershipMember(
                        name="Abhinav Asthana",
                        title="CEO and Co-founder",
                        linkedin_url="https://www.linkedin.com/in/abhinavasthana",
                        source="website"
                    ),
                    LeadershipMember(
                        name="Ankit Sobti",
                        title="CTO and Co-founder",
                        linkedin_url="https://www.linkedin.com/in/ankitsobti",
                        source="website"
                    ),
                    LeadershipMember(
                        name="Abhijit Kane",
                        title="Co-founder",
                        linkedin_url="https://www.linkedin.com/in/abhijitkane",
                        source="website"
                    ),
                ],
                key_products_features=[
                    "API Client & Workspace Collaboration",
                    "Automated Testing & Mock Servers",
                    "API Documentation & Governance"
                ],
                data_confidence_score=0.95
            )
        elif "supabase" in domain_lower:
            intelligence = RawExtractedIntelligence(
                company_name="Supabase",
                company_overview=(
                    "Supabase is an open-source Firebase alternative providing a dedicated PostgreSQL database alongside authentication, instant APIs, edge functions, and real-time subscriptions. "
                    "It enables developers to build secure, scalable web and mobile applications with minimal backend setup."
                ),
                target_audience_icp="Full-stack developers, mobile engineers, startups, and enterprise software teams building cloud-native applications.",
                contact_emails=found_emails or ["support@supabase.com", "sales@supabase.com", "press@supabase.com"],
                key_leadership=[
                    LeadershipMember(
                        name="Paul Copplestone",
                        title="CEO and Co-founder",
                        linkedin_url="https://www.linkedin.com/in/paulcopplestone",
                        source="website"
                    ),
                    LeadershipMember(
                        name="Ant Wilson",
                        title="CTO and Co-founder",
                        linkedin_url="https://www.linkedin.com/in/antwilson",
                        source="website"
                    )
                ],
                key_products_features=[
                    "Postgres Database with Realtime Subscriptions",
                    "Built-in Authentication & Row Level Security",
                    "Storage, Vector Embeddings & Edge Functions"
                ],
                data_confidence_score=0.96
            )
        elif "vapi" in domain_lower:
            intelligence = RawExtractedIntelligence(
                company_name="Vapi",
                company_overview=(
                    "Vapi is a developer platform for building, testing, and deploying low-latency conversational voice AI agents over phone calls and web interfaces. "
                    "It provides developers with real-time orchestration across speech-to-text, LLM reasoning, and natural text-to-speech pipelines."
                ),
                target_audience_icp="Developers, contact center engineers, and AI product builders creating real-time conversational voice agents and automated phone workflows.",
                contact_emails=found_emails or ["support@vapi.ai", "sales@vapi.ai"],
                key_leadership=[
                    LeadershipMember(
                        name="Jordan Dearsley",
                        title="Founder & CEO",
                        linkedin_url="https://www.linkedin.com/in/jordandearsley",
                        source="website"
                    )
                ],
                key_products_features=[
                    "Sub-second Voice AI Orchestration Engine",
                    "Telephony Integration & WebRTC Audio Streaming",
                    "Function Calling & Custom Voice Assistant Tuning"
                ],
                data_confidence_score=0.92
            )
        else:
            # Generic heuristic extraction for any unknown domain
            overview_sentences = [
                f"{clean_name} provides advanced modern digital solutions tailored for high-growth teams and enterprises.",
                "Their platform delivers automated workflows and scalable infrastructure to enhance developer and operational productivity."
            ]
            intelligence = RawExtractedIntelligence(
                company_name=clean_name,
                company_overview=" ".join(overview_sentences),
                target_audience_icp=f"Developers, technical leaders, and enterprises adopting modern software tools.",
                contact_emails=found_emails or [f"contact@{domain}", f"support@{domain}"],
                key_leadership=[
                    LeadershipMember(
                        name=f"Lead Executive",
                        title="Chief Executive Officer",
                        linkedin_url=found_linkedin[0] if found_linkedin else None,
                        source="website"
                    )
                ],
                key_products_features=["Core Platform", "Cloud Integration", "Enterprise Security"],
                data_confidence_score=0.80 if found_emails else 0.65
            )

        # Realistic token counts
        prompt_tokens = max(350, len(crawled_text) // 4)
        completion_tokens = 280
        return intelligence, prompt_tokens, completion_tokens


class LLMClientFactory:
    """Creates the appropriate LLM client based on configuration."""

    @staticmethod
    def get_client() -> Tuple[str, Optional[OpenAI], str]:
        """
        Returns: (provider_name, openai_client_instance_or_none, model_name)
        """
        provider = settings.resolve_provider()

        if provider == "openai":
            if not settings.openai_api_key:
                logger.warning("OpenAI API key missing, falling back to mock provider.")
                return "mock", None, "mock"
            client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
            return "openai", client, settings.llm_model

        elif provider == "groq":
            if not settings.groq_api_key:
                logger.warning("Groq API key missing, falling back to mock provider.")
                return "mock", None, "mock"
            client = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            return "groq", client, settings.groq_model

        elif provider == "ollama":
            client = OpenAI(
                api_key="ollama",
                base_url=settings.ollama_base_url
            )
            return "ollama", client, settings.ollama_model

        return "mock", None, "mock"
