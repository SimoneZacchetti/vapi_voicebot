# Vapi Agent Configuration

## Setup Instructions

### 1. Access Vapi Dashboard
- Go to https://dashboard.vapi.ai
- Create a new Assistant

### 2. Base Configuration
- **Name:** "Municipio Codroipo Bot"
- **Language:** Italian (IT)
- **Model:** GPT-4 (or gpt-4-turbo)
- **First Message:** "Ciao! 👋 Sono l'assistente IA per i servizi del Comune di Codroipo. Come posso aiutarti oggi?"

### 2b. Voice Configuration
- **Provider:** OpenAI
- **Voice ID:** nova

### 3. System Prompt

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
- Se l'utente non specifica una data, chiedi di fornirla nel formato YYYY-MM-DD
- Per gli orari disponibili, utilizza sempre il formato HH:MM (es. 09:30)

Cerca sempre di fornire risposte complete usando i tool disponibili.
```

### 4. Add Tools

#### Tool 1: Search Services
```
Name: search_services
Type: Server URL
URL: <your-backend-url>/tools/search_services
Method: POST
Description: Search municipal services by keyword (optional: if empty, returns all services)
Function name: search_services

Request parameters:
{
  "query": {
    "type": "string",
    "description": "Keyword to search services (e.g., 'anagrafe', 'tasse'). Optional: if omitted returns all services"
  }
}
```

#### Tool 2: Check Availability
```
Name: check_availability
Type: Server URL
URL: <your-backend-url>/tools/check_availability
Method: POST
Description: Check appointment availability for a specific date (both office and date required)

Request parameters:
{
  "office": {
    "type": "string",
    "description": "Office/service name (required)"
  },
  "date": {
    "type": "string",
    "description": "Date in YYYY-MM-DD format (e.g., 2026-05-20) (required)"
  }
}
```

### 5. Expose Backend Locally

**Option A: ngrok (Fast)**
```bash
# Install ngrok from https://ngrok.com (free account)
ngrok http 8000
# Copy the public URL (e.g., https://your-unique-id.ngrok-free.dev)
# Use this URL as <your-backend-url> in Vapi tools (without /tools/search_services)
```

**Option B: Azure/AWS VM**
- Deploy backend to a VM with public IP
- Use the IP/domain in tools

### 6. Test Voice Interaction

In the Vapi dashboard, test the chatbot by saying:

**Test 1: Service Search**
> "Voglio informazioni sulla anagrafe"

**Test 2: Availability**
> "Che ore sono libere per l'anagrafe il 20 maggio?"

## Web Widget Integration

The project uses the **official Vapi Web SDK** (`frontend/index.html`):

1. Fetches config from backend (`GET /api/config`)
2. Initializes Vapi Web SDK with `publicKey` and `assistantId`
3. Dynamically loads Vapi script
4. Enables voice interaction via browser

No additional setup needed: the frontend already uses the Vapi integration.

## Troubleshooting

**"Tool error: Connection refused"**
- Verify backend server is online
- If using ngrok, ensure tunnel is active
- Check tool URLs in Vapi

**"401 Unauthorized"**
- Ensure `VAPI_PRIVATE_KEY` in .env is correct
- Regenerate the key from dashboard

**Agent not responding**
- Verify tools are configured correctly
- Check backend logs
- Test endpoints manually with curl

