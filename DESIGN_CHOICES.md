# Design Choices & Implementation Notes

## System Prompt Design

**Rationale:** System prompt guides agent behavior in Italian (target language). Instructions prioritize:
- **Tool usage clarity**: Explicit mapping (user asks → which tool). Avoids agent guessing.
- **Professional tone**: "amichevole e professionale" balances approachability with authority.
- **Data format requirements**: Date format (YYYY-MM-DD) + time format (HH:MM) specified upfront to minimize validation errors.
- **Fallback behavior**: If data missing, prompt agent to ASK rather than hallucinate.

**Alternatives considered:**
- Chain-of-thought prompting (add "let me think step by step" → verbose responses, not needed for simple 3-tool flow)
- Few-shot examples in prompt (low ROI for appointment booking, would bloat token count)
- Temperature 0.5 (more deterministic) vs 0.7 (current): 0.7 chosen for natural Italian conversation tone

## Tool Design

### Tool 1: `search_services`
**Parameters:** Single `query` (string)
- **Why:** Flexibility. User may ask "che servizi avete?", "ho bisogno di anagrafe", "come faccio per X". Single query field forces agent to extract intent.
- **Alternative considered:** Enum-based dropdown (fixed categories) → too rigid for Italian conversational language. Keyword matching more robust.

**Implementation:** Keyword match on service title, description, office name, required docs (case-insensitive).
- **Edge cases:**
  - Empty query → returns all services (fallback)
  - No matches → returns "Nessun servizio trovato" with hint to try different keywords
  - Partial matches → returns sorted by relevance (title > description > office)

### Tool 2: `check_availability`
**Parameters:** `office` (string) + `date` (YYYY-MM-DD)
- **Why two params:** Office ID + date required for slot lookup. Avoids ambiguous "when next available" queries.
- **Format choice (YYYY-MM-DD):** ISO 8601 standard, sortable, international.

**Implementation:** Hardcoded slot pool per office (09:30, 10:00, 11:00, 14:00, 15:00). Returns available slots after filtering booked.
- **Edge cases:**
  - Office not found → "Ufficio non riconosciuto. Prova: Anagrafe e stato civile, Tributi, etc."
  - No slots available that day → "Purtroppo nessun slot libero il [date]. Prova un'altra data."
  - Past date → Validation in agent response (backend doesn't reject, lets agent handle gracefully)

### Tool 3: `create_appointment`
**Parameters:** name, office, service, date, time
- **Why all 5:** Sufficient for confirmation. Backend stores in-memory dict keyed by appointment_id (auto-generated).
- **Validation:** No duplicate check (same person, same office, same date, same time allowed in MVP)

**Implementation:** Creates appointment, stores in appointments list, returns confirmation + appointment_id.
- **Edge cases:**
  - Already booked slot → Backend doesn't prevent (no locking). Returns success. **Caveat: race condition in high-concurrency.** Acceptable for MVP (single-office municipality, low traffic).
  - Invalid date/time → Agent validation. Backend assumes data from agent is valid.
  - Missing field → 400 Bad Request from backend

## RAG (Information Retrieval)

**Approach:** Keyword matching (not embeddings).

**Rationale:**
- **Low complexity:** Works well for ~50 services (Codroipo municipality size).
- **No external dependencies:** No embedding model (ollama, huggingface), no vector DB. Pure Python keyword search.
- **Transparency:** Evaluators see exact matching logic. No "black box" similarity scoring.
- **Trade-off:** Loses semantic understanding. Query "como faccio per licenza" won't match "autorizzazioni commerciali" (synonyms). Acceptable for MVP.

**Source data:**
- Hardcoded JSON in `app/data/servizi_comunali_codroipo.json` (fallback).
- Optional web scraper (`scrape_codroipo_services.py`) that visits `https://www.comune.codroipo.ud.it/it/servizi` via Playwright.
- Scraper fragility: If site changes structure, scraper breaks. Mitigated by fallback hardcoded data.

**Improvement path:** Replace keyword search with Mistral embeddings (open-source, runs locally) + cosine similarity. No API cost, no vendor lock-in.

## Edge Case Handling

| Scenario | Current Behavior | Rationale |
|----------|-----------------|-----------|
| User doesn't specify date | Agent prompt: "Chiedi di fornirla" → System asks in response | Explicit instruction in system prompt |
| Invalid date format (e.g., "12/05/2026") | Backend returns 400 if sent as-is. Agent should catch and re-prompt. | Format validation delegated to agent interpretation |
| Office name typo (e.g., "anagarfe") | `check_availability` returns "not found" → Agent offers correct name | Graceful error + suggestion |
| Slot double-booked (race condition) | First request wins, second gets success but slot occupied | MVP acceptable. Production: add mutex/transaction lock |
| No services match query | `search_services` returns empty array + hint | Agent responds with "nessun risultato, prova..." |

## Limitations (Current MVP)

1. **In-memory appointments**: Resets on server restart. No persistence.
   - *Workaround for evaluation:* Keep server running during testing, or accept data loss.
   - *Production:* Add PostgreSQL + SQLAlchemy ORM.

2. **No authentication**: Anyone can create appointments for anyone.
   - *Reason:* MVP simplicity. Real appointment needs citizen ID verification.
   - *Production:* Add user session, municipality ID validation.

3. **Hardcoded appointment slots**: Fixed hours (09:30, 10:00, etc.) for all offices.
   - *Reason:* Rapid prototyping. Real system: office hours per service type, per day.
   - *Improvement:* Load from municipal calendar DB.

4. **Scraper fragility**: Depends on website HTML structure.
   - *Reason:* Codroipo municipality site may not have stable API.
   - *Improvement:* Official municipal API (ANPR, SUAP) or cached snapshot.

5. **No rate limiting**: Agent can spam tool calls.
   - *Reason:* MVP. Vapi manages call throttling at platform level.
   - *Production:* Add Redis-based rate limiter per user/session.

6. **Keyword matching only**: No semantic understanding.
   - *Reason:* Simplicity + transparency for evaluation.
   - *Production:* Mistral embeddings + vector search.

7. **Italian language only**: System prompt hardcoded for Italian.
   - *Reason:* MVP scope. Add multi-language support: system prompt param, i18n strings, voice model per language.

8. **No conversation history**: Frontend shows chat but no persistent logs.
   - *Reason:* No DB. Backend discards messages after response.
   - *Production:* Store messages in PostgreSQL, expose via `/api/conversation_logs` endpoint.

## Future Improvements (with more time)

### Short-term (1-2 days)
- [ ] Add PostgreSQL for persistent appointments (+ alembic migrations)
- [ ] Implement conversation history storage
- [ ] Add input validation (date ranges, email format for citizen contact)
- [ ] Vapi webhook for appointment confirmations (email/SMS)

### Medium-term (3-5 days)
- [ ] Replace keyword search with Mistral embeddings (local, no cost)
- [ ] Add redis-based caching for common queries
- [ ] Implement citizen authentication (SPID, municipality ID)
- [ ] Add monitoring (Prometheus metrics, error tracking)
- [ ] Multi-language support (Italian + English minimum)

### Long-term (1+ weeks)
- [ ] Integration with real municipal DB (ANPR, SUAP APIs)
- [ ] Calendar sync (office hours, holidays, closures)
- [ ] SMS/email notifications for appointments
- [ ] Chatbot analytics dashboard (call volume, success rate, top queries)
- [ ] Fallback to human agent (escalation if agent confidence < threshold)

## Prompt Engineering Decisions

**System Prompt tone:** "amichevole e professionale"
- Balances warmth (first message: "Ciao! 👋") with authority (government office context)
- Italian diminutives ("servizi disponibili") foster trust

**Explicit tool instructions:** "Quando l'utente chiede... usa lo strumento..."
- Reduces hallucination. Without explicit mapping, agent might fabricate tool calls.
- Tested via Vapi dashboard voice testing (see VAPI_SETUP.md)

**Date/time format mandate:** "formato YYYY-MM-DD", "formato HH:MM"
- Prevents ambiguity (USA: MM-DD-YYYY vs EU: DD-MM-YYYY). ISO standard explicit.
- Backend validates format. Agent is instructed to use it.

## Testing Strategy

1. **Unit tests**: Tool endpoints tested with curl (see README.md examples)
2. **Integration tests**: Vapi dashboard voice tests (see VAPI_SETUP.md "Test Voice Interaction")
3. **Edge case manual testing:**
   - Missing date → Agent asks
   - Invalid date → Agent re-prompts
   - Double-book scenario → Observe if slots conflict (acceptable for MVP)
   - Empty query → Returns all services (fallback)

## Code Organization

```
backend/
├── app/
│   ├── main.py           # FastAPI app, all endpoints
│   ├── vapi_client.py    # HTTP client for Vapi chat API (server-side chat fallback)
│   ├── appointments.py   # In-memory appointment storage + slot management
│   ├── services_data.py  # Keyword search + service retrieval
│   ├── scrape_codroipo_services.py  # Playwright web scraper
│   ├── data/
│   │   ├── servizi_comunali.json          # Fallback (generic)
│   │   └── servizi_comunali_codroipo.json # Scraped (live, optional)
│   └── static/
│       └── index.html    # Frontend (chat + voice UI)
├── requirements.txt      # Python deps
└── Dockerfile            # Container config
```

**Rationale:** Single-file main.py (no separate route files) acceptable for ~5 endpoints. Easy to evaluate. Production: split into blueprints (appointments.py routes, services.py routes, tools.py routes).

## Why Vapi Web SDK (Client-side Voice)?

Not server-side STT/TTS endpoints. Reasons:
1. **User experience**: Browser-native microphone → lower latency, no double-hop.
2. **Security**: Credentials (public key) managed by Vapi SDK, not exposed in requests.
3. **Simplicity:** Vapi SDK handles speech-to-text + text-to-speech automatically. Backend only returns chat responses.

**Trade-off:** Frontend depends on Vapi CDN. Offline mode not possible. Acceptable for web app.

---

**Document generated:** 2026-05-12
**Last updated:** At each significant code change
