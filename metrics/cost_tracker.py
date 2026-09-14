"""Token counting and cost estimation metrics tracker."""

from typing import Dict, Optional


# Pricing per 1,000,000 tokens (USD) as of standard rates
MODEL_PRICING_PER_1M: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
    "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79},
    "llama3-8b-8192": {"prompt": 0.05, "completion": 0.08},
    "mock": {"prompt": 0.0, "completion": 0.0},
    "ollama": {"prompt": 0.0, "completion": 0.0},
}


class CostTracker:
    """Tracks token consumption and computes estimated API costs per scraped domain."""

    def __init__(self):
        self.domain_records: Dict[str, Dict] = {}
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cost_usd: float = 0.0

    def record_usage(
        self,
        domain: str,
        prompt_tokens: int,
        completion_tokens: int,
        model_name: str
    ) -> Dict:
        """Records token metrics for a specific domain and updates cumulative totals."""
        total_tokens = prompt_tokens + completion_tokens

        # Resolve pricing
        pricing = MODEL_PRICING_PER_1M.get(
            model_name.lower(),
            {"prompt": 0.15, "completion": 0.60}  # default to gpt-4o-mini rates
        )

        cost = (
            (prompt_tokens / 1_000_000.0) * pricing["prompt"] +
            (completion_tokens / 1_000_000.0) * pricing["completion"]
        )

        record = {
            "domain": domain,
            "model": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 6),
        }

        self.domain_records[domain] = record
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost_usd += cost

        return record

    def get_domain_record(self, domain: str) -> Optional[Dict]:
        return self.domain_records.get(domain)

    def get_summary(self) -> Dict:
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_estimated_cost_usd": round(self.total_cost_usd, 6),
        }
