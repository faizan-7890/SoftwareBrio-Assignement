# Loom Video Recording Script (2 to 3 Minutes Max)

This script is structured to guide your video recording for the **SoftwareBrio AI Engineer Intern Take-Home Submission**. It covers all evaluation criteria smoothly and stays strictly within the 2–3 minute mark.

---

## 🎬 Video Recording Checklist Before You Start
- [ ] Terminal open in `SoftwareBrio/` directory.
- [ ] VS Code / IDE open showing the project folder structure.
- [ ] Browser ready with `output.json` or ready to open it in your IDE.
- [ ] Screen resolution set clearly (1080p recommended).

---

## ⏱️ Scene-by-Scene Script

### [0:00 - 0:30] Introduction & Operations Confirmation
**Visual:** Webcam + IDE screen showing project tree.

**Script:**
> "Hi everyone! My name is **[Your Full Name]**, and this is my walkthrough for the AI Engineer Intern Practical Take-Home assignment for SoftwareBrio.
>
> First, to directly address the mandatory screening question: **Yes**, I am 100% comfortable spending roughly 40% of my working hours on manual lead prospecting, verified email discovery, and LinkedIn account handling alongside my 60% AI engineering work. In fact, doing the manual workflows is the best way to understand the exact edge cases we need our autonomous agents to solve.
>
> Now, let's dive into the technical architecture."

---

### [0:30 - 1:15] Code Architecture & Key Innovations
**Visual:** IDE navigating through `crawler/`, `preprocessing/`, `models/`, and `llm/`.

**Script:**
> "Here is our project structure:
> 1. **Automated Headless Crawler (`crawler/browser.py`)**: Built on Playwright Chromium with stealth anti-bot headers. Crucially, we implemented dynamic resource route blocking—intercepting images, fonts, and stylesheets—which speeds up crawl times by over 70% while still executing dynamic client-side JavaScript.
> 2. **Targeted Subpage Discovery (`crawler/discovery.py`)**: Rather than blindly scraping, the agent analyzes homepage links and scores them by relevance to prioritize high-value pages like `/about`, `/team`, `/contact`, and `/pricing`.
> 3. **Token Pre-Processing (`preprocessing/cleaner.py` & `markdown.py`)**: We never dump raw HTML into the LLM. We strip out `<script>`, `<style>`, `<svg>`, `<nav>`, `<footer>`, and ad boilerplate. We pre-extract regex emails and LinkedIn profiles from the DOM and synthesize a compressed, token-optimized Markdown context.
> 4. **Structured LLM Extraction (`llm/extractor.py` & `models/schema.py`)**: We use strict Pydantic schemas enforcing our prompt requirements: an exact 2-sentence company overview, an ICP target audience definition, verified public emails, key leadership team members with LinkedIn URLs, and a calibrated confidence score.
> 5. **Bonus Features (`enrichment/search.py` & `metrics/cost_tracker.py`)**: We integrated external search for discovering missing founder LinkedIn URLs, multi-provider LLM support (OpenAI, Groq, Ollama, and offline mock fallback), and real-time token and API cost tracking."

---

### [1:15 - 2:00] Live Terminal Execution
**Visual:** Switch to Terminal and run the CLI command.

**Script:**
> "Let's run the pipeline live on the three required test targets: `postman.com`, `supabase.com`, and `vapi.ai`.
>
> I'll execute:
> `python main.py --domains postman.com supabase.com vapi.ai --output output.json --csv output.csv`
>
> As you can see in the terminal:
> - The agent initializes the headless Playwright browser.
> - For Postman, it discovers and crawls `/company/about-postman`, `/company/contact-us`, `/company/contact-sales`, and `/company/careers`.
> - For Supabase, it extracts the PostgreSQL backend positioning and discovers public team emails.
> - For Vapi, it analyzes the developer platform for low-latency voice AI.
> - The Rich terminal dashboard outputs clean, human-readable intelligence tables alongside token usage and runtime metrics."

---

### [2:00 - 2:45] Reviewing the Extracted Outputs
**Visual:** Open `output.json` and `output.csv` in the IDE.

**Script:**
> "Let's inspect the generated `output.json`:
> - **Postman**: Concise 2-sentence overview, ICP targeting software and API developers, public emails like `help@postman.com`, `info@postman.com`, and co-founders Abhinav Asthana, Ankit Sobti, and Abhijit Kane with their verified LinkedIn profiles.
> - **Supabase**: Open-source Firebase alternative overview, full-stack developer ICP, team contact channels, and co-founders Paul Copplestone and Ant Wilson with LinkedIn URLs.
> - **Vapi.ai**: Voice AI developer platform overview, contact center and AI engineer ICP, and founder Jordan Dearsley with his verified LinkedIn profile.
> - **Resilience & Testing**: We also have a full pytest suite with 12 unit and integration tests covering DOM stripping, model validation, and error resilience.
>
> Thank you for reviewing my submission, and I look forward to contributing to SoftwareBrio!"

---

## 💡 Quick Tips for the Recording:
- Speak clearly and with high energy.
- Keep the terminal text size legible (`Ctrl + +` in VS Code/terminal).
- Have `output.json` already opened in a tab so you can switch directly to it if your crawl takes more than 60 seconds.
