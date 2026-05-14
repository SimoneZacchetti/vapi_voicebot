# Setup — Municipal services voicebot

## Prerequisites

- Python 3.11+ (3.12 is fine)
- A Vapi account: **private** server key, **public** key, and `assistant id` for the voice UI
- Docker (optional, for Compose)

## Environment variables

Create a **`.env`** file (do not commit it):

| Variable | Purpose |
|----------|---------|
| `VAPI_PRIVATE_KEY` | Backend: server-side chat, sessions, dashboard tools |
| `VAPI_PUBLIC_KEY` | Browser: Vapi Web SDK (voice) |
| `VAPI_ASSISTANT_ID` | Browser: which assistant to start |

- **`docker compose`** from the **repo root**: Compose reads `.env` from that directory.
- **Uvicorn only** from `backend/`: put `.env` in `backend/` (that is the working directory) or export variables in your shell.

## Local run (backend only)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** — the UI is `frontend/index.html` served by FastAPI.

## Docker Compose (backend + frontend)

From the repository root:

```bash
docker compose up --build
```

- **UI:** http://localhost:8080 (Nginx; proxies API calls to the `backend` service)
- **API** (health, Vapi/ngrok tool URLs): http://localhost:8000

Do not open `http://0.0.0.0:…` in the browser; use `localhost`.

## Useful layout

| Path | Role |
|------|------|
| `backend/app/` | FastAPI (`main.py`, `routers/`, `schemas.py`, `data/*.json`) |
| `frontend/index.html` | Chat + voice (Vapi client-side SDK) |
| `backend/scripts/` | Playwright scraper (optional, not in the API image) |

## Quick API check

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/tools/search_services \
  -H "Content-Type: application/json" \
  -d '{"query":"anagrafe"}'
```

More curl examples: `backend/README.md`.

## Service data scraper (optional)

From `backend/`:

```bash
pip install playwright && python -m playwright install chromium
python scripts/scrape_codroipo_services.py
```

Default output: `app/data/servizi_comunali_hardcoded.json`.

## Vapi (agent, tool URLs, ngrok)

Assistant setup, tools wired to the backend, voice testing: **`docs/VAPI_SETUP.md`**.

To expose the API locally: `ngrok http 8000` and use the HTTPS URL for server-side tools.

## Limitations

Appointments are **in-memory** (lost on restart). Service search is **keyword**-based, not embeddings.

## Troubleshooting

| Issue | What to do |
|-------|------------|
| `VAPI_PRIVATE_KEY not configured` | Set `VAPI_PRIVATE_KEY` in `.env` / the environment of the uvicorn process or containers. |
| Empty UI / 503 on `/` on the backend container | Expected if the backend image does not bundle `frontend/`; with Compose open the UI on **:8080**. |
| No services found | Check `backend/app/data/`; regenerate JSON with the scraper above. |
