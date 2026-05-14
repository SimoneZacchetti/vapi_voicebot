# 🤖 Voicebot Servizi Municipali - Setup Guide

## Prerequisiti

- Python 3.12+
- Docker e Docker Compose (opzionale, per deploy)
- Chiave API Vapi valida

## Quick Start

### 1. Ambiente Locale

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurazione Vapi

Copia `.env.example` in `.env` e inserisci la tua chiave Vapi:

```bash
cp .env.example .env
# Edita .env con:
# VAPI_KEY=sk-your-actual-vapi-key
# VAPI_PUBLIC_KEY=pk-your-public-key
# VAPI_ASSISTANT_ID=your-assistant-id
```

### 3. Avvia il Backend

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Accedi a: http://localhost:8000

## Architettura

### Backend (FastAPI + Python)

**Endpoints Disponibili:**

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/tools/search_services` | Ricerca servizi |
| POST | `/tools/check_availability` | Verifica disponibilità slot |
| POST | `/tools/create_appointment` | Crea appuntamento |
| GET | `/appointments` | Lista appuntamenti |
| GET | `/api/appointments` | Lista appuntamenti (UI) |
| GET | `/` | Serve UI HTML |
| POST | `/api/chat` | Endpoint Vapi chat |

### Componenti

**app/main.py** - FastAPI application con tutti gli endpoint

**app/vapi_client.py** - Client HTTP per Vapi API (usa httpx)

**app/appointments.py** - In-memory appointment storage con slot management

**app/services_data.py** - Ricerca servizi basata su keyword matching

**app/scrape_codroipo_services.py** - Web scraper Playwright per servizi comunali

**frontend/index.html** - UI web moderna con chat interface (proxy verso API in `docker compose`)

## Test Endpoint

### Ricerca Servizi

```bash
curl -X POST http://localhost:8000/tools/search_services \
  -H "Content-Type: application/json" \
  -d '{"query":"anagrafe"}'
```

Risposta:
```json
{
  "answer": "Ho trovato questi servizi comunali...",
  "sources": [
    {"title": "Anagrafe e stato civile", "office": "Anagrafe e stato civile"}
  ]
}
```

### Check Disponibilità

```bash
curl -X POST http://localhost:8000/tools/check_availability \
  -H "Content-Type: application/json" \
  -d '{
    "office":"Anagrafe e stato civile",
    "date":"2026-05-20"
  }'
```

### Crea Appuntamento

```bash
curl -X POST http://localhost:8000/tools/create_appointment \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Mario Rossi",
    "office":"Anagrafe e stato civile",
    "service":"Certificato di nascita",
    "date":"2026-05-20",
    "time":"09:30"
  }'
```

## Docker Compose

```bash
# Build e avvia
docker compose up --build

# Backend su http://localhost:8000
```

## Configurazione Vapi Agent

L'agente Vapi dovrebbe essere configurato così:

**System Prompt:**
```
You are a helpful Italian municipal services assistant. Your role is to help citizens:
1. Find municipal services by keyword
2. Check appointment availability
3. Book appointments

Always respond in Italian. Use the available tools to search for services and manage appointments.
Be friendly and professional.
```

**Tools:**
1. `search_services` - POST /tools/search_services
   - Parameter: `query` (string)
   
2. `check_availability` - POST /tools/check_availability
   - Parameters: `office` (string), `date` (date)
   
3. `create_appointment` - POST /tools/create_appointment
   - Parameters: `name`, `office`, `service`, `date`, `time`

## Limitazioni Attuali

- **Storage:** In-memory (reset on server restart)
- **Slots:** Hardcoded (09:30, 10:30, 11:30)
- **Search:** Keyword-based (no embeddings)
- **Scraped Data:** 17 servizi dal Comune di Codroipo

## Prossimi Step

1. Integrazione Vapi web widget per chat voice
2. Database persistente (PostgreSQL)
3. Real API availability da Google Calendar / ICS
4. Vector embeddings per RAG migliorato
5. Multi-language support (ITA/ENG/FRI)
6. SMS/Email notifications

## Troubleshooting

**"VAPI_KEY not configured"**
- Crea `.env` file con `VAPI_KEY=your-key`

**"ModuleNotFoundError: No module named 'dotenv'"**
- `pip install python-dotenv`

**Appuntamenti non visualizzati**
- Controlla che `/api/appointments` sia raggiungibile
- Verifica CORS headers

**Servizi non trovati**
- Esegui scraper: `python app/scrape_codroipo_services.py`
- Verifica `app/data/servizi_comunali_codroipo.json` esiste

