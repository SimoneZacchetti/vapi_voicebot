# Municipality Voicebot Backend

Prototipo FastAPI per un voicebot Vapi dedicato ai servizi comunali.

## Requisiti

- Python 3.10+ consigliato
- `pip`
- `ngrok` per esporre il backend in locale
- `VAPI_KEY` per endpoint server-side chat
- `VAPI_PUBLIC_KEY` e `VAPI_ASSISTANT_ID` per voice web

## 1. Creare il virtual environment

Da `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Installare le dipendenze

```bash
pip install -r requirements.txt
```

## 3. Avviare FastAPI

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verifica rapida:

```bash
curl http://127.0.0.1:8000/health
```

Config voice:

```bash
curl http://127.0.0.1:8000/api/config
```

## 4. Testare gli endpoint con curl

### Ricerca servizi

```bash
curl -X POST http://127.0.0.1:8000/tools/search_services \
  -H "Content-Type: application/json" \
  -d '{"query":"Come posso richiedere la carta d identita?"}'
```

### Disponibilita appuntamenti

```bash
curl -X POST http://127.0.0.1:8000/tools/check_availability \
  -H "Content-Type: application/json" \
  -d '{"office":"Ufficio Anagrafe e Stato Civile","date":"2026-05-12"}'
```

### Creazione appuntamento

```bash
curl -X POST http://127.0.0.1:8000/tools/create_appointment \
  -H "Content-Type: application/json" \
  -d '{"name":"Mario Rossi","office":"Ufficio Anagrafe e Stato Civile","service":"Carta d identita elettronica CIE","date":"2026-05-12","time":"09:30"}'
```

### Lista appuntamenti

```bash
curl http://127.0.0.1:8000/appointments
```

## 5. Esporre il backend con ngrok

In un secondo terminale, con il server FastAPI attivo:

```bash
ngrok http 8000
```

Usa l'URL pubblico generato da ngrok per configurare i custom tools di Vapi.

## 6. Endpoint da collegare a Vapi

- `GET /health` per il controllo base dello stato del backend
- `POST /tools/search_services` per rispondere a domande sui servizi comunali
- `POST /tools/check_availability` per verificare gli slot disponibili
- `POST /tools/create_appointment` per confermare una prenotazione
- `GET /appointments` per ispezionare gli appuntamenti creati in memoria

## 6. Voice web con Vapi

La UI in `frontend/index.html` (servita in dev da FastAPI su `/`, in Docker dal servizio `frontend`) usa `@vapi-ai/web` lato browser.

Serve impostare:

```bash
export VAPI_PUBLIC_KEY="your_public_key"
export VAPI_ASSISTANT_ID="your_assistant_id"
```

Flusso:

- clic `🎙️ Avvia Voice`
- browser apre microfono
- Vapi gestisce speech-to-text e text-to-speech
- clic `⏹️ Ferma Voice` per chiudere sessione

Se vuoi creare assistant con `clientMessages` utili per caption:

```json
{
  "clientMessages": ["assistant.speechStarted", "transcript", "speech-update"]
}
```

## 7. Scraping dei servizi comunali

Per generare il JSON da usare nel RAG locale puoi eseguire lo scraper (da `backend/`):

```bash
python scripts/scrape_codroipo_services.py
```

Opzionale: `--output path/custom.json`. Default: `app/data/servizi_comunali_codroipo.json`.

Se è la prima volta, installa anche il browser usato da Playwright:

```bash
python -m playwright install chromium
```

## Note

- Gli appuntamenti sono salvati solo in memoria: si azzerano al riavvio del server.
- Gli slot disponibili sono hardcoded e vengono rimossi se gia prenotati.
- La ricerca servizi usa solo parole chiave su titolo, descrizione, ufficio e documenti richiesti.
- La voice UI richiede browser con permessi microfono.
