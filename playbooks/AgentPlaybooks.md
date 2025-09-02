# Agent Playbooks

Use these turnkey workflows with the Super Prompt. Reference files with backticks inside the Agent (e.g., `examples/DailyGigAgentWorkflow.md`).

---

## Daily Gig Hunter (Freelance/Consulting)

### Inputs
- Skills/offerings, target roles/industries, locations/timezones
- Filters: min rate, contract type, keywords include/exclude
- Sources: official APIs (e.g., Remotive, Remote OK), curated lists, career pages

### Steps
1) Source setup
- Create `data/sources.json` with endpoints, params, and headers (if required).
- Note rate limits and terms; use backoff and caching where possible.
2) Fetch & normalize
- Write `tools/fetch_gigs.(py|js)` to fetch, deduplicate, and normalize fields.
- Save raw to `data/gigs_raw.json` and clean to `data/gigs_clean.json`.
3) Rank & shortlist
- Implement a simple scoring function (skills match, rate, recency, company).
- Output `out/gigs_ranked.md` with table of top N opportunities.
4) Outreach drafts
- For top N, generate tailored emails using `examples/OutreachEmailTemplates.md`.
- Save drafts to `out/outreach_drafts/<YYYY‑MM‑DD>/emails.md`.
5) Review & send
- Manually review drafts, personalize as needed, then send.
- Log outcomes in `out/outreach_log.md`.

### Scheduling
- Provide OS‑level scheduling (Windows Task Scheduler / cron / launchd) for `fetch_gigs` and end‑of‑day draft generation.

---

## Content Pipeline (Blog/Newsletter/Presentation)

### Steps
1) Topic intake → add to `out/content_queue.md` (title, audience, goal).
2) Research brief in `out/research/<slug>.md` with sources and notes.
3) Outline in `out/content/<slug>/outline.md`.
4) Draft in `out/content/<slug>/draft.md`.
5) Edit pass: clarity, structure, examples, CTA.
6) Final export assets (markdown, PDF slides, images if any).

---

## Research Briefs (Market/Tech/Competitive)

### Steps
1) Define question and scope; list assumptions and exclusions.
2) Collect sources (official docs, reports, primary data); avoid paywalled/opaque sources when possible.
3) Synthesize: findings, implications, risks, open questions.
4) Deliver `out/research/<topic>.md` with citations and next actions.

---

## Data Analysis (CSV/JSON/Sheets)

### Steps
1) Ingest data into `data/` and document schema.
2) Build `tools/analyze.(py|ipynb)` for EDA and transformations.
3) Produce visuals and tables; save to `out/figures/` and `out/tables/`.
4) Write `out/report_<topic>.md` with methods, insights, and actions.

---

## PM Assistant (Projects/OKRs)

### Steps
1) Create/maintain `Roadmap.md`: goals, milestones, backlog.
2) Weekly planning and daily checklist sections.
3) Status updates: progress, blockers, next actions.
4) Generate stakeholder summaries on cadence.

---

## Learning Coach (Skills/Certs)

### Steps
1) Define learning outcomes and timeline.
2) Curate resources; tag by level and time to complete.
3) Create quizzes/flashcards; schedule reviews.
4) Track progress in `out/learning_plan.md`.
