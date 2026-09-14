"""CLI Entry point for the Autonomous Lead Enrichment Agent."""

import argparse
import csv
import json
import logging
import sys
from typing import List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.config import settings
from agent.orchestrator import LeadEnrichmentAgent
from models.schema import BatchEnrichmentReport

console = Console(highlight=False)

DEFAULT_DOMAINS = [
    "postman.com",
    "supabase.com",
    "vapi.ai"
]


def setup_logging(verbose: bool = False):
    """Configures application logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )


def save_json(report: BatchEnrichmentReport, output_path: str):
    """Saves enriched results to a formatted JSON file."""
    data = report.model_dump()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    console.print(f"[bold green][OK][/bold green] Saved structured JSON output to [cyan]{output_path}[/cyan]")


def save_csv(report: BatchEnrichmentReport, output_path: str):
    """Saves high-level enriched company intelligence to CSV."""
    fieldnames = [
        "domain",
        "company_name",
        "company_overview",
        "target_audience_icp",
        "contact_emails",
        "key_leadership",
        "data_confidence_score",
        "sources_crawled",
        "enrichment_timestamp"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in report.results:
            # Format leadership as readable string
            leaders_str = "; ".join(
                f"{l.name} ({l.title}) - {l.linkedin_url or 'N/A'}"
                for l in item.key_leadership
            )
            writer.writerow({
                "domain": item.domain,
                "company_name": item.company_name,
                "company_overview": item.company_overview,
                "target_audience_icp": item.target_audience_icp,
                "contact_emails": ", ".join(item.contact_emails),
                "key_leadership": leaders_str,
                "data_confidence_score": item.data_confidence_score,
                "sources_crawled": ", ".join(item.sources_crawled),
                "enrichment_timestamp": item.enrichment_timestamp
            })
    console.print(f"[bold green][OK][/bold green] Saved CSV export to [cyan]{output_path}[/cyan]")


def display_results_in_terminal(report: BatchEnrichmentReport):
    """Renders a Rich terminal dashboard displaying the enriched intelligence."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]AUTONOMOUS LEAD ENRICHMENT AGENT[/bold cyan]\n"
        "[dim]Dynamic Web Crawling • Token-Optimized DOM Preprocessing • LLM Intelligence Extraction[/dim]",
        border_style="cyan"
    ))

    for company in report.results:
        table = Table(title=f"Extracted Intelligence: [bold green]{company.company_name}[/bold green] ({company.domain})", show_header=True)
        table.add_column("Attribute", style="bold cyan", width=24)
        table.add_column("Enriched Value", style="white")

        table.add_row("Overview", company.company_overview)
        table.add_row("Target Audience (ICP)", company.target_audience_icp)
        table.add_row("Contact Emails", ", ".join(company.contact_emails) if company.contact_emails else "[italic dim]None found[/italic dim]")

        # Format leadership
        if company.key_leadership:
            lead_rows = []
            for l in company.key_leadership:
                lead_rows.append(f"- [bold]{l.name}[/bold] -- {l.title}\n  LinkedIn: [blue underline]{l.linkedin_url or 'N/A'}[/blue underline]")
            table.add_row("Key Leadership", "\n".join(lead_rows))
        else:
            table.add_row("Key Leadership", "[italic dim]None detected[/italic dim]")

        table.add_row("Confidence Score", f"[bold yellow]{company.data_confidence_score:.2f}[/bold yellow] / 1.00")
        table.add_row("Sources Crawled", f"{len(company.sources_crawled)} pages:\n" + "\n".join(f"  - {s}" for s in company.sources_crawled))
        
        console.print(table)
        console.print("\n")

    # Metrics table
    metrics_table = Table(title="Execution & Cost Metrics", show_header=True)
    metrics_table.add_column("Metric", style="bold magenta")
    metrics_table.add_column("Value", style="bold white")
    metrics_table.add_row("Total Domains Evaluated", str(report.total_domains))
    metrics_table.add_row("Successful Enrichments", f"[green]{report.successful_domains}[/green]")
    metrics_table.add_row("Failed Enrichments", f"[red]{report.failed_domains}[/red]")
    metrics_table.add_row("Total Prompt Tokens", str(report.total_prompt_tokens))
    metrics_table.add_row("Total Completion Tokens", str(report.total_completion_tokens))
    metrics_table.add_row("Total Tokens Processed", str(report.total_tokens))
    metrics_table.add_row("Estimated API Cost (USD)", f"${report.estimated_cost_usd:.6f}")
    metrics_table.add_row("Total Pipeline Runtime", f"{report.execution_time_seconds:.2f} seconds")
    console.print(metrics_table)
    console.print("\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Autonomous Lead Enrichment Agent — Crawls domains and outputs structured intelligence."
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=DEFAULT_DOMAINS,
        help="List of company domains to crawl and enrich (default: postman.com supabase.com vapi.ai)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output.json",
        help="Path to save output JSON results (default: output.json)"
    )
    parser.add_argument(
        "--csv",
        default="output.csv",
        help="Path to save CSV export (default: output.csv)"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "groq", "ollama", "mock"],
        default=None,
        help="Override LLM provider (default: auto-detected or 'mock')"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override LLM model name"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose debug logging"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging(args.verbose)

    if args.provider:
        settings.llm_provider = args.provider
    if args.model:
        settings.llm_model = args.model

    console.print(f"[bold green]Starting Autonomous Lead Enrichment Agent...[/bold green]")
    console.print(f"Target Domains: [cyan]{', '.join(args.domains)}[/cyan]")
    console.print(f"Active LLM Provider: [yellow]{settings.resolve_provider()}[/yellow]\n")

    agent = LeadEnrichmentAgent()
    report = agent.run_batch(args.domains)

    # Render dashboard
    display_results_in_terminal(report)

    # Save outputs
    save_json(report, args.output)
    if args.csv:
        save_csv(report, args.csv)

    console.print("[bold green][OK] Pipeline completed successfully![/bold green]\n")


if __name__ == "__main__":
    main()
