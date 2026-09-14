"""Application configuration and settings management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment or .env file."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # LLM Settings
    llm_provider: str = "mock"  # 'openai', 'groq', 'ollama', or 'mock'
    llm_model: str = "gpt-4o-mini"
    
    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    
    # Groq Settings
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Ollama Settings
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"
    
    # Search API Settings (Bonus feature)
    tavily_api_key: Optional[str] = None
    serpapi_api_key: Optional[str] = None
    enable_external_linkedin_search: bool = True
    
    # Headless Browser & Crawler Settings
    headless: bool = True
    page_timeout_ms: int = 25000
    max_subpages_per_domain: int = 4
    wait_after_load_ms: int = 1500
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    
    # Context Preprocessing Settings
    max_text_tokens_per_page: int = 3000
    
    def resolve_provider(self) -> str:
        """Auto-detect provider if default is mock but API keys are present."""
        if self.llm_provider != "mock":
            return self.llm_provider.lower()
        if self.openai_api_key and self.openai_api_key.strip():
            return "openai"
        if self.groq_api_key and self.groq_api_key.strip():
            return "groq"
        return "mock"


# Singleton instance
settings = Settings()
