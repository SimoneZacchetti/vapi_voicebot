![Vapi](https://img.shields.io/badge/Vapi-Voice%20AI-111111?style=for-the-badge&logo=audio-technica&logoColor=white)

# Voicebot Servizi Municipali

Prototipo voicebot per servizi comunali (Comune di Codroipo) con integrazione Vapi + backend FastAPI.

## Struttura repository

| Percorso | Contenuto |
|----------|-----------|
| `backend/app/` | FastAPI: `main.py`, `schemas.py`, `routers/`, `data/` |
| `frontend/` | UI statica (`index.html`) + immagine Nginx in Compose |
| `backend/scripts/` | Scraper Playwright (non inclusi nell'immagine Docker) |
| `docs/` | Setup, Vapi, design notes, `VAPI_AGENT_CONFIG.json` di esempio |
| `docker-compose.yml` | Servizi `backend` (:8000) e `frontend` (:8080, Nginx + proxy verso API) |

## Funzionalita

- Chat in italiano con assistente Vapi
- Interazione vocale (STT/TTS) via Vapi Web SDK
- Tool backend per:
  - ricerca servizi comunali
  - verifica disponibilita appuntamenti
  - creazione appuntamenti (in-memory)

## Avvio rapido

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Apri: `http://localhost:8000` (stessa UI: file servito da `frontend/index.html`)

## Docker Compose

```bash
docker compose up --build
```

- **UI:** http://localhost:8080 (Nginx; chiamate `/api/*`, `/health`, ecc. proxate al backend)
- **API diretta** (es. ngrok / tool URL Vapi): http://localhost:8000

Variabili Vapi: stesso `.env` nella root del progetto o `export` prima di `docker compose`.

Il PDF menziona anche DB separato come plus: qui non c’è (appuntamenti in-memory).

## Configurazione

Imposta variabili in `.env`:

- `VAPI_PRIVATE_KEY`
- `VAPI_PUBLIC_KEY`
- `VAPI_ASSISTANT_ID`

Per setup completo Vapi e tool: vedi `docs/SETUP.md` e `docs/VAPI_SETUP.md`.
