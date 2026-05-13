![Vapi](https://img.shields.io/badge/Vapi-Voice%20AI-111111?style=for-the-badge&logo=audio-technica&logoColor=white)

# Voicebot Servizi Municipali

Prototipo voicebot per servizi comunali (Comune di Codroipo) con integrazione Vapi + backend FastAPI.

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

Apri: `http://localhost:8000`

## Configurazione

Imposta variabili in `.env`:

- `VAPI_PRIVATE_KEY` (o `VAPI_KEY`)
- `VAPI_PUBLIC_KEY`
- `VAPI_ASSISTANT_ID`

Per setup completo Vapi e tool: vedi `SETUP.md` e `VAPI_SETUP.md`.
