# Configurazione Vapi Agent

## Istruzioni Setup

### 1. Accedi a Vapi Dashboard
- Vai su https://dashboard.vapi.ai
- Crea un nuovo Assistant

### 2. Configurazione Base
- **Nome:** "Municipio Codroipo Bot"
- **Lingua:** Italian (IT)
- **Modello:** GPT-4 (o gpt-4-turbo)

### 3. System Prompt (Italiano)

```
Tu sei un assistente IA amichevole e professionale per i servizi comunali del Comune di Codroipo.

Il tuo ruolo è aiutare i cittadini a:
1. Trovare servizi comunali cercando per parola chiave
2. Verificare la disponibilità di appuntamenti

Istruzioni importanti:
- Rispondi sempre in italiano
- Quando l'utente chiede info su servizi, usa lo strumento "search_services"
- Quando serve controllare disponibilità, usa "check_availability"
- I tool leggono i dati dal JSON hardcoded del backend
- Sii cortese, efficiente e professionale
- Se l'utente non specifica una data, chiedi di fornirla
- Per gli orari disponibili, utilizza sempre il formato HH:MM (es. 09:30)

Cerca sempre di fornire risposte complete usando i tool disponibili.
```

### 4. Aggiungi Tools

#### Tool 1: Search Services
```
Name: search_services
Type: Server URL
URL: https://book-nuclei-deafening.ngrok-free.dev/tools/search_services
Method: POST
Description: Cerca servizi comunali per parola chiave
Function name: search_services

Request parameters:
{
  "query": {
    "type": "string",
    "description": "Parola chiave per cercare servizi (es. 'anagrafe', 'tasse')"
  }
}
```

#### Tool 2: Check Availability
```
Name: check_availability
Type: Server URL
URL: https://book-nuclei-deafening.ngrok-free.dev/tools/check_availability
Method: POST
Description: Controlla disponibilità appuntamenti

Request parameters:
{
  "office": {
    "type": "string",
    "description": "Nome dell'ufficio/servizio"
  },
  "date": {
    "type": "string",
    "description": "Data in formato YYYY-MM-DD (es. 2026-05-20)"
  }
}
```

### 5. Esponi il Backend Locale

**Opzione A: ngrok (Veloce)**
```bash
ngrok http 8000
# Copia l'URL pubblico (es. https://book-nuclei-deafening.ngrok-free.dev)
# Usa questo URL nei tool Vapi
```

**Opzione B: Azure/AWS VM**
- Deploya il backend su una VM con IP pubblico
- Usa l'IP/dominio nei tool

### 6. Test Voice Interaction

Nel Vapi dashboard, prova il chatbot dicendo:

**Test 1: Ricerca Servizi**
> "Voglio informazioni sulla anagrafe"

**Test 2: Disponibilità**
> "Che ore sono libere per l'anagrafe il 20 maggio?"

## Integrazione Web Widget

Per aggiungere il chatbot al sito web:

```html
<script>
  window.voiceflow={config:{apiEndpoint:"https://general-runtime.voiceflow.com",projectID:"your-vapi-assistant-id"}};
  // O usa il widget Vapi ufficiale dal dashboard
</script>
```

## Troubleshooting

**"Tool error: Connection refused"**
- Verifica che il server backend sia online
- Se usi ngrok, assicurati che il tunnel sia attivo
- Controlla le URL dei tool in Vapi

**"401 Unauthorized"**
- Assicurati che VAPI_PRIVATE_KEY in .env sia corretta
- Rigenera la chiave dal dashboard

**Agente non risponde**
- Verifica che i tool siano configurati correttamente
- Controlla i log del backend
- Testa manualmente gli endpoint con curl

