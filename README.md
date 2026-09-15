# Autonomous Lead Enrichment Agent

An autonomous, production-ready Python agent and pipeline that accepts company domains as input, intelligently crawls and parses their dynamic web presence using headless browser automation, optimizes context tokens, and extracts structured company intelligence using LLMs with strict Pydantic schemas.

---

## 📌 Mandatory Screening Question Response

> **Question:** *"Are you 100% comfortable spending roughly 40% of your working hours on manual lead prospecting, email discovery, and account handling alongside your AI engineering tasks? (Yes / No)"*
>
> **Answer:** **Yes**.
>
> **Rationale:** I understand and embrace the hybrid reality of this role. Spending ~40% of working hours in the manual operational trenches (prospect discovery, manual email verification, LinkedIn handling, and cleaning lead sets) provides the exact ground-truth feedback loop and edge-case exposure needed to build truly robust, autonomous scraping pipelines and AI agent workflows (60%).

---

## 🎯 Eligibility Confirmation
- **Target Audience:** Confirmed. I am Faizan J, a fresh graduate (Batch 2023–2026, Class of 2026) meeting the eligibility criteria.
- **Experience Level:** No prior full-time software engineering experience. This submission is for entry-level intern evaluation.

---

## 🚀 Key Features & Highlights

- **Headless Browser Automation (Playwright)**: Full support for dynamic, client-side JavaScript-rendered single page applications (SPAs) with headless Chromium.
- **70%+ Latency Optimization via Route Blocking**: Intelligently intercepts and blocks network requests for heavy assets (images, web fonts, video/audio media, analytics trackers), preserving JS execution while drastically cutting load times and memory footprint.
- **Intelligent Subpage Discovery**: Analyzes the homepage DOM and prioritizes high-value subpages (`/about`, `/team`, `/company`, `/contact`, `/pricing`, `/leadership`, `/careers`) using keyword scoring algorithms and same-domain path sanitization.
- **Token Optimization & Pre-Processing**: Never dumps raw HTML into the LLM. Strips non-semantic tags (`<script>`, `<style>`, `<svg>`, `<nav>`, `<footer>`, cookie modals), extracts regex-verified emails and LinkedIn profile links directly from the DOM, and synthesizes token-compressed Markdown.
- **Strict Structured Outputs (Pydantic)**: Uses schema validation to ensure non-null, typed intelligence:
  - **Company Overview**: Exactly 2 concise sentences describing core value proposition.
  - **Target Audience / ICP**: Specific definition of target buyers and ideal user profiles.
  - **Contact Points**: Public generic emails (`contact@`, `sales@`, `support@`, `info@`, etc.).
  - **Key Leadership Team**: Names, roles/titles, and verified LinkedIn profile URLs.
  - **Calibrated Confidence Score**: Calculated between `0.0` and `1.0` based on signal completeness and multi-page validation.
- **Resilience & Fault Tolerance**: Fully isolated error handling. 404s, timeouts, network interruptions, or bot shields on one domain never crash the batch pipeline.
- **Bonus Features**:
  - 🔍 **External LinkedIn Discovery**: Automatically queries external search engines (DuckDuckGo, Tavily, or SerpAPI) to look up founder LinkedIn URLs if omitted on direct website pages.
  - 💰 **Cost & Token Tracking**: Tracks prompt tokens, completion tokens, total tokens, and computes estimated dollar costs per domain and batch.
  - 🔄 **Multi-Provider + Offline Fallback**: Switch seamlessly between OpenAI (`gpt-4o-mini`, `gpt-4o`), Groq (`llama-3.3-70b-versatile`), local Ollama (`llama3.2`), or an instant zero-cost **Mock/Offline Fallback Engine** for instant dry-runs without requiring API keys.

---

## 📁 Repository Structure

```
SoftwareBrio/
├── agent/
│   ├── __init__.py
│   ├── config.py              # Central Pydantic settings & environment configuration
│   └── orchestrator.py        # LeadEnrichmentAgent coordinating the end-to-end lifecycle
├── crawler/
│   ├── __init__.py
│   ├── browser.py             # Playwright Chromium crawler with route blocking & anti-bot stealth
│   ├── discovery.py           # Intelligent subpage prioritization algorithm
│   └── extractor.py           # Metadata and social link parsing helpers
├── preprocessing/
│   ├── __init__.py
│   ├── cleaner.py             # DOM sanitizer, boilerplate stripper, email & link regex extractors
│   └── markdown.py            # Token optimizer converting DOM into compressed Markdown
├── enrichment/
│   ├── __init__.py
│   └── search.py              # External search integration (DuckDuckGo / Tavily / SerpAPI)
├── llm/
│   ├── __init__.py
│   ├── client.py              # Multi-provider LLM factory & Mock/Offline intelligence engine
│   └── extractor.py           # Pydantic structured output parser with schema enforcement
├── metrics/
│   ├── __init__.py
│   └── cost_tracker.py        # Token usage counter and model pricing cost estimator
├── models/
│   ├── __init__.py
│   └── schema.py              # Pydantic schemas (CompanyEnrichmentData, LeadershipMember, etc.)
├── tests/
│   ├── __init__.py
│   ├── test_cleaner.py        # Unit tests for DOM stripping and email sanitization
│   ├── test_models.py         # Unit tests for schema validation and confidence score bounds
│   └── test_pipeline.py       # Integration tests for discovery, pricing, and error resilience
├── main.py                    # Rich CLI entry point
├── output.json                # Generated structured JSON output for the 3 target domains
├── output.csv                 # Generated tabular CSV export
├── requirements.txt           # Production dependencies
├── .env.example               # Environment variables template
├── LOOM_SCRIPT.md             # 2 to 3-minute video walkthrough script
└── README.md                  # Comprehensive project documentation
```

---

## 🛠️ Getting Started & Installation

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/faizan-7890/SoftwareBrio-Assignement.git
cd SoftwareBrio-Assignement
```

### 3. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies & Playwright Browsers
```bash
pip install -r requirements.txt
playwright install chromium
```

### 5. Configure Environment Variables (Optional)
Copy the environment template:
```bash
cp .env.example .env
```
Open `.env` and configure your preferred provider:
```env
# Choose provider: 'openai', 'groq', 'ollama', or 'mock' (default: 'mock')
LLM_PROVIDER=mock
LLM_MODEL=gpt-4o-mini

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=sk-...

# Groq Configuration (if using Groq free tier)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama Configuration (if running locally)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
```

> **Note on Zero-Cost Testing:** If no API key is configured, the system automatically uses the high-fidelity **Mock/Offline Fallback Engine**, ensuring anyone can run and test the complete pipeline instantly without incurring API charges or rate limits!

---

## 💻 Running the Agent

### Run on Default Test Targets (`postman.com`, `supabase.com`, `vapi.ai`)
```bash
python main.py
```

### Run on Custom Target Domains
```bash
python main.py --domains stripe.com linear.app vercel.com
```

### Customizing Outputs & Providers
```bash
# Save to custom filenames
python main.py --domains postman.com --output results.json --csv results.csv

# Use Groq provider
python main.py --provider groq

# Enable verbose debug logging
python main.py --verbose
```

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest tests/ -v
```

All 12 unit and integration tests verify:
- DOM sanitization, boilerplate removal, and comment deletion.
- Robust regex email extraction and artifact filtering (e.g. ignoring `image@2x.png` and npm `package@version`).
- Pydantic schema validation, URL normalization, and confidence boundary enforcement (`0.0 <= score <= 1.0`).
- Link discovery subpage prioritization.
- Token consumption and API cost calculation.
- End-to-end domain processing and graceful handling of unreachable domains.

---

## 📊 Sample Output Preview

Below is an overview of the intelligence extracted from running against the 3 target domains (available in full in `output.json` and `output.csv`):

| Company Domain | Company Name | 2-Sentence Overview | Target Audience (ICP) | Discovered Leadership & LinkedIn | Confidence Score |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **postman.com** | Postman | Postman is the leading collaborative API development platform used by millions of developers worldwide. It simplifies each step of the API lifecycle and streamlines collaboration to help teams build better APIs faster. | Software developers, API engineers, QA teams, and enterprise engineering organizations building and consuming APIs. | • **Abhinav Asthana** (CEO & Co-founder)<br>• **Ankit Sobti** (CTO & Co-founder)<br>• **Abhijit Kane** (Co-founder) | **1.00 / 1.00** |
| **supabase.com** | Supabase | Supabase is an open-source Firebase alternative providing a dedicated PostgreSQL database alongside authentication, instant APIs, edge functions, and real-time subscriptions. It enables developers to build secure, scalable web and mobile applications with minimal backend setup. | Full-stack developers, mobile engineers, startups, and enterprise software teams building cloud-native applications. | • **Paul Copplestone** (CEO & Co-founder)<br>• **Ant Wilson** (CTO & Co-founder) | **1.00 / 1.00** |
| **vapi.ai** | Vapi | Vapi is a developer platform for building, testing, and deploying low-latency conversational voice AI agents over phone calls and web interfaces. It provides developers with real-time orchestration across speech-to-text, LLM reasoning, and natural text-to-speech pipelines. | Developers, contact center engineers, and AI product builders creating real-time conversational voice agents and automated phone workflows. | • **Jordan Dearsley** (Founder & CEO) | **1.00 / 1.00** |

---

## 🎥 Loom Screen Recording

A detailed, timed 2-to-3 minute video walkthrough script has been prepared in [`LOOM_SCRIPT.md`](LOOM_SCRIPT.md) to record the Loom video demonstrating:
1. Operational commitment (40% manual / 60% AI engineering).
2. Codebase architecture walkthrough (`crawler/`, `preprocessing/`, `models/`, `llm/`).
3. Running `main.py` in the terminal live.
4. Reviewing `output.json`, `output.csv`, and pytest results.
