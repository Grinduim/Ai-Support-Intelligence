# AI Support Intelligence

Production-ready API that analyzes customer support tickets and classifies **risk level (LOW / MEDIUM / HIGH)** with clear, explainable signals.

Designed for support teams that need to **prioritize critical tickets before SLAs, churn or escalation happen**.

---

## Why this exists
Support teams usually discover risk **too late**:
- customers threatening churn
- public complaints
- legal or billing escalations

This API turns raw support conversations into **actionable risk signals in seconds**.

---

## What it does (MVP)
Input:
- conversation summary
- latest customer message

Output:
- `risk_label`: LOW | MEDIUM | HIGH
- `signals`: objective indicators that led to the decision
- `explanation`: short, human-readable justification

No dashboards. No databases.  
Just **fast, reliable decision support**.

---

## 15-second demo (Recruiter Test)

```bash
curl -X POST http://localhost:8000/tickets/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TCK-2026-0419",
    "customer": "Acme Corp",
    "channel": "email",
    "last_message": "If this is not fixed today, I will cancel and escalate publicly.",
    "conversation_summary": "Customer contacted support regarding a billing issue that was not resolved after multiple attempts.",
    "company_tone": "neutral",
    "language": "en"
  }'
```

Response:
```json
{
  "risk_label": "HIGH",
  "signals": [
    "explicit cancellation threat",
    "public escalation intent",
    "unresolved billing issue"
  ],
  "explanation": "The customer explicitly threatens churn and public escalation after repeated unresolved billing problems.",
  "model": "gpt-4o-mini",
  "request_id": "req_9f31c2"
}
```

---

## API Endpoints
- `GET /health` → service health check
- `POST /tickets/analyze` → risk classification
- `POST /replies/suggest-reply` → suggested response (optional)

Interactive docs available at:
```
/docs
```

---

## Run locally

### Environment
```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional)

### Local
```bash
uvicorn app.main:app --reload
```

### Docker
```bash
docker compose up --build
```

Service runs at:
```
http://localhost:8000
```

---

## Reliability
- Strict request/response schemas (Pydantic)
- Deterministic heuristics + LLM reasoning
- Guardrails to prevent unsafe downgrades
- Test suite covering contracts, heuristics and fallbacks
- CI running on every push

---

## Non-goals (by design)
- UI / dashboard
- CRM integrations
- Authentication
- Persistence

This project focuses on **decision quality and API reliability**.

---

## Status
- Dockerized
- Tested
- CI enabled
- Ready for public deployment (Render / Fly)
