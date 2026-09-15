# Loom Video Recording Script (2 to 3 Minutes Max)

This script guides your video recording for the **SoftwareBrio AI Engineer Intern Take-Home Submission**. It is timed to fit **under 3 minutes** while covering all rubric-weighted evaluation criteria.

---

## 🎬 Pre-Recording Checklist
- [ ] Terminal open in the `SoftwareBrio/` project directory.
- [ ] IDE (VS Code) open showing the project folder tree expanded.
- [ ] `output.json` already open in an IDE tab (so you can switch to it instantly).
- [ ] Terminal font size increased for legibility (`Ctrl + +` twice).
- [ ] Screen resolution: 1080p or higher.
- [ ] **Pre-run the pipeline** before recording so crawled output is ready. You will show the live terminal command but can fast-forward the ~2 min crawl wait using Loom's speed-up feature.

---

## ⏱️ Scene-by-Scene Script

> **Pacing guide:** ~150 words per minute is comfortable. Each section below stays within its time budget at natural speaking pace.

---

### [0:00 – 0:25] Introduction & Operations Confirmation
**Visual:** Webcam on + IDE screen showing the project folder tree.

**Say:**
> "Hi, my name is **Faizan J** and this is my walkthrough for the SoftwareBrio AI Engineer Intern take-home assignment.
>
> To directly answer the mandatory screening question: **Yes** — I'm fully comfortable spending 40% of my time on manual lead prospecting, email discovery, and account handling. The manual work gives you the ground-truth understanding needed to build better autonomous agents."

---

### [0:25 – 1:10] Code Architecture Walkthrough
**Visual:** Click through the folder tree in IDE: `crawler/` → `preprocessing/` → `llm/` → `models/`.

**Say:**
> "Here's how the project is structured:
>
> First, the **crawler** — built on Playwright Chromium with headless stealth mode. It blocks images, fonts, and media at the network layer, cutting load times by 70% while keeping full JavaScript execution. The **discovery module** scores homepage links to find high-value subpages like `/about`, `/team`, `/contact`, and `/pricing`.
>
> Second, **preprocessing** — we never feed raw HTML into the LLM. We strip scripts, styles, SVGs, navbars, and cookie banners. Emails and LinkedIn URLs are pre-extracted with regex directly from the DOM.
>
> Third, the **LLM extraction layer** — it uses strict Pydantic schemas to output a 2-sentence company overview, target audience ICP, public contact emails, leadership with LinkedIn URLs, and a confidence score. It supports OpenAI, Groq, Ollama, or a zero-cost offline mock engine.
>
> And for **bonus features**: external DuckDuckGo search for missing founder LinkedIn profiles, and per-domain token cost tracking."

---

### [1:10 – 2:00] Live Terminal Execution
**Visual:** Switch to terminal. Run the command.

**Say:**
> "Let me run the pipeline on the three required targets."

**Type and execute:**
```bash
python main.py --domains postman.com supabase.com vapi.ai
```

> "The agent launches headless Chromium, fetches each homepage, discovers relevant subpages, and crawls them. For Postman it found 4 subpages, for Supabase 4, and for Vapi 1."

**While it runs (or after fast-forward), point at the Rich dashboard output:**
> "Here's the final output — clean intelligence tables for each company with leadership names, LinkedIn URLs, contact emails, and confidence scores. At the bottom you can see the execution metrics: total tokens consumed and estimated API cost."

---

### [2:00 – 2:40] Output Review & Closing
**Visual:** Switch to `output.json` tab in IDE.

**Say:**
> "Let me show the structured JSON output. For **Postman** — Abhinav Asthana as CEO, Ankit Sobti as CTO, and Abhijit Kane as Co-founder, all with verified LinkedIn profiles. Emails include `help@postman.com` and `info@postman.com`.
>
> **Supabase** — Paul Copplestone and Ant Wilson with their LinkedIn URLs and five contact channels.
>
> **Vapi** — Jordan Dearsley as Founder and CEO.
>
> We also have 12 automated tests covering DOM cleaning, schema validation, cost tracking, and graceful error handling for unreachable domains.
>
> Thank you for reviewing my submission — I'm excited about the opportunity to contribute to SoftwareBrio!"

---

## 💡 Recording Tips
- **Crawl wait time:** The pipeline takes ~2 minutes to crawl all 12 pages. Either pre-run so output exists, or use Loom's **speed-up / trim** feature to skip the wait.
- **Speak naturally** — don't rush. The script is sized for comfortable pacing.
- **Show, don't just tell** — click on files as you mention them so viewers see the code.
- Keep the terminal text legible — increase font size before recording.
