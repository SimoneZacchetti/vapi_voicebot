# AI Tools Used in Development

## Overview

This document discloses all AI tools leveraged during development of the Voicebot prototype, their purposes, and scope of usage.

## Tools & Usage

### 1. GitHub Copilot (GitHub, via VS Code)

**Scope:** Code generation, scaffolding, debugging

**Specific uses:**
- FastAPI endpoint boilerplate (main.py routes)
- Python class stubs (appointments.py, services_data.py, vapi_client.py)
- HTML/CSS styling for frontend UI (index.html)
- Docker/docker-compose setup
- Requirements.txt dependency list


### 2. GitHub Copilot Chat (Iterative conversation)

**Scope:** Debugging, refinement, optimization

**Specific uses:**
- Troubleshooting Docker cache issues (suggested `--no-cache`, `--force-recreate`)
- Environment variable propagation (VAPI_KEY vs VAPI_PUBLIC_KEY fallback logic)
- Browser caching problems (hard refresh, cache busting strategies)
- Vapi Web SDK integration (CDN script loader pattern, message event types)
- HTML/CSS circular button styling (border-radius: 50%, flex centering)

### 3. Manual Iteration & Testing (No AI)

**Scope:** Configuration, validation, decision-making

**Specific uses (AI-independent):**
- Vapi dashboard setup (manual agent configuration, tool URL registration)
- System prompt refinement (tested via Vapi voice testing, iterated based on agent responses)
- ngrok tunnel setup & troubleshooting
- Appointment slot design (hardcoded hours: 09:30, 10:00, 11:00, 14:00, 15:00 — designed from municipal office patterns)
- Service retrieval strategy decision (keyword matching vs embeddings — evaluated trade-offs, chose keyword for MVP simplicity)
- Error handling design (edge case scenarios listed in DESIGN_CHOICES.md — authored manually)

## Not Used (Intentionally)

- **ChatGPT / Claude directly:** Only via Copilot Chat in IDE (not web interface)
- **Code generation for business logic:** Appointment booking, RAG search implemented manually for transparency
- **API integration (external LLM calls):** All LLM calls via Vapi platform (not custom endpoints)
- **Auto-documentation tools:** This document + DESIGN_CHOICES.md written manually

## AI vs. Manual Breakdown

| Component | AI Contribution | Manual Contribution |
|-----------|----------------|--------------------|
| Backend scaffolding | ~70% (boilerplate) | ~30% (logic, validation) |
| Frontend UI/styling | ~60% (CSS patterns) | ~40% (layout decisions, voice flow) |
| System prompt | 0% | 100% (Italian domain-specific design) |
| Tool design | 10% (parameter names) | 90% (semantic choices, validation rules) |
| Docker setup | ~50% (config template) | ~50% (env wiring, layer optimization) |
| Debugging/troubleshooting | ~30% (suggestions) | ~70% (testing, validation, iteration) |
| **Total project** | ~35% | ~65% |

## Rationale for Disclosure

**Transparency:** Evaluators should know what was AI-assisted vs. human-designed. AI Copilot accelerated boilerplate (FastAPI routes, HTML stubs), but critical decisions (prompt engineering, tool design, RAG strategy, edge case handling) were manual, tested, and intentional.

**Limitations of AI contribution:** Copilot generated code patterns without understanding municipality domain context. Manual review + refinement essential for correctness.

**Best practices followed:**
- All Copilot suggestions validated (no blind acceptance)
- Business logic reviewed for correctness
- System prompt tested in production (Vapi dashboard) before deployment
- Edge cases designed manually based on real appointment-booking scenarios

## Future Improvements

When expanding this project:
- Keep manual control on system prompt (domain-specific tuning beats auto-generation)
- Use AI for documentation generation (README, changelog) — low-risk
- Consider AI for test case generation (edge case fuzzing) — moderate risk, high ROI
- Avoid AI for security decisions (auth, validation rules) — manual required

---

**Disclosure date:** 2026-05-12
**Tools inventory last updated:** At each AI tool addition
