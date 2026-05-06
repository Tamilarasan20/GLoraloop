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
- Celery
- Redis
- SQLAlchemy
- PostgreSQL-ready persistence
- Cloudflare R2-compatible storage
- OpenAI/Gemini provider adapters
- Next.js
- React Konva

The current brand intelligence layer uses deterministic heuristics when AI keys are absent. Set `LARALOOP_AI_PROVIDER=openai` or `LARALOOP_AI_PROVIDER=gemini` and provide the matching key to use the structured LLM extraction adapters.

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

Run a Celery worker:

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
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

Generate an enriched strategy document with PDF:

```bash
curl -X POST http://127.0.0.1:8000/v1/documents/strategy \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

The strategy document response includes:

- business profile
- social media strategy
- market research
- brand guidelines
- extracted website assets
- `strategy_pdf_url`

Create an async job:

```bash
curl -X POST http://127.0.0.1:8000/v1/brand-kits/jobs \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

Poll a job:

```bash
curl http://127.0.0.1:8000/v1/jobs/{job_id}
```

Watch status over WebSocket:

```text
ws://127.0.0.1:8000/v1/jobs/{job_id}/ws
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:3000`.

The frontend includes:

- URL ingestion screen
- async job polling
- extracted Brand Kit panel
- campaign variation selector
- React Konva template canvas
- PNG export
- saved project request using development bearer auth
- strategy document summary
- strategy PDF link

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

- Replace placeholder Fal.ai, Photoroom, remove.bg, Meta, LinkedIn, and TikTok adapters with account-specific API calls.
- Add migrations with Alembic before production deploys.
- Replace development bearer auth with Clerk, Supabase Auth, Auth0, or first-party JWT verification.
- Add fallback flows for blocked pages: screenshot upload, manual brand form, and partial extraction.
