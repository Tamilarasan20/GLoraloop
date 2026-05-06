# GLoraloop Brand DNA Extractor

Initial backend for Laraloop's Pomelli-like Brand DNA pipeline.

## MVP 1

Input:

- Business website URL

Output:

- Normalized Brand Kit JSON
- Three campaign concepts
- Template-ready canvas layer data
- Raw scrape context for debugging and later LLM enrichment

## Stack

- Python
- FastAPI
- Playwright
- Pydantic

The current brand intelligence layer uses deterministic heuristics so the app runs without AI API keys. It is isolated behind `BrandIntelligenceService`, which is where OpenAI/Gemini structured extraction should be wired next.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Analyze a URL:

```bash
curl -X POST http://127.0.0.1:8000/v1/brand-kits/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## API Shape

```json
{
  "brand_kit": {
    "brand_name": "Example",
    "summary": "What the business sells",
    "audience": "Who it appears to target",
    "tone": ["modern", "clear", "warm"],
    "colors": ["#111827", "#ffffff", "#2563eb"],
    "font_style": "modern sans-serif",
    "logo_url": null,
    "images": [],
    "positioning": "Example presents itself as modern, clear, warm and focused on clear customer value.",
    "campaign_angles": [
      "Promote a seasonal or limited-time offer",
      "Highlight the most visible product or service benefit",
      "Build trust with proof points, reviews, or guarantees"
    ]
  },
  "campaign_concepts": [],
  "template_ready_data": [],
  "scraped_data": {}
}
```

## Next Backend Milestones

- Add Celery and Redis so `/analyze` returns a `job_id` immediately.
- Store brand kits and scrape artifacts in PostgreSQL.
- Upload screenshots and selected assets to Cloudflare R2.
- Replace heuristic extraction with strict OpenAI/Gemini structured outputs.
- Add fallback flows for blocked pages: screenshot upload, manual brand form, and partial extraction.
