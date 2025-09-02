# Daily Gig Agent Workflow (Example)

This example shows how to run a day‑long opportunity search and generate end‑of‑day outreach drafts.

## Inputs
- Skills/offerings: <fill>
- Target roles/industries: <fill>
- Filters: min rate, contract type, keywords include/exclude
- Sources: Remotive, Remote OK, curated lists, select career pages

## Files
- `data/sources.json` — API endpoints, params, headers; rate‑limit notes
- `tools/fetch_gigs.(py|js)` — fetch, normalize, dedupe; write `data/gigs_raw.json` and `data/gigs_clean.json`
- `out/gigs_ranked.md` — ranked shortlist with rationale
- `examples/OutreachEmailTemplates.md` — email skeletons
- `out/outreach_drafts/<YYYY‑MM‑DD>/emails.md` — generated emails
- `out/outreach_log.md` — sent log & outcomes

## Step‑by‑step
1) Configure sources
- Create `data/sources.json` with entries like:
```json
{
  "remotive": {
    "url": "https://remotive.com/api/remote-jobs",
    "params": {"search": "<keywords>"},
    "notes": "Respect API terms; cache results."
  },
  "remoteok": {
    "url": "https://remoteok.com/api",
    "params": {},
    "notes": "Rate limits may apply."
  }
}
```

2) Implement fetch & normalize
- Write `tools/fetch_gigs.py` (or `.js`) to:
  - call APIs with retries/backoff
  - map fields to a standard schema (title, company, url, date, comp, tags)
  - dedupe by `url` and `(company,title)`
  - save raw and clean JSON

3) Rank and shortlist
- Implement a rule‑based score: skills match, rate, recency, company quality.
- Write a markdown table to `out/gigs_ranked.md` with top N including:
  - Title | Company | Source | Fit Score | Link | Notes

4) Generate outreach drafts
- For each top item, pick a template from `examples/OutreachEmailTemplates.md` and fill variables.
- Save to `out/outreach_drafts/<date>/emails.md` grouped by opportunity.

5) Review and send
- Manually proofread and personalize.
- Send via your email client or CRM.
- Append result to `out/outreach_log.md` (date, target, link, outcome).

## Scheduling (Windows)
- Open Task Scheduler → Create Basic Task.
- Trigger: Daily at 9:00 → Action: Start a program → `python.exe` with argument path to `tools/fetch_gigs.py`.
- Create another task at 17:30 to run a script that reads `data/gigs_clean.json` and writes `out/outreach_drafts/<date>/emails.md`.
- Ensure scripts are non‑interactive and log to files.

## Tips
- Keep API calls polite; cache results.
- Track duplicate companies to avoid spamming.
- Rotate subject lines; A/B test openers.
- Log outcomes to improve ranking heuristics.
