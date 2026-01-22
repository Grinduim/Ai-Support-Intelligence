import json
from app.models import Ticket, AIAnalysis
from app.services.openai_client import openai_chat

SYSTEM_PROMPT = """
You are a customer support risk triage engine.

Return ONLY valid JSON.
No markdown. No explanations outside JSON.

Rules:
- risk_label must be one of: LOW, MEDIUM, HIGH
- risk_score: integer 0..100
- confidence: integer 0..100
- Be conservative. HIGH = urgent escalation.
- Focus on escalation threats, cancellation intent, negative tone, and SLA aging.
"""

def _build_user_prompt(ticket: Ticket) -> str:
    return f"""
    Analyze this support context:

    last_message: "{ticket.last_message}"
    conversation_summary: "{ticket.conversation_summary}"
    sla_hours_open: {ticket.sla_hours_open}
    channel: "{ticket.channel}"

    Return JSON with:
    - risk_score
    - risk_label
    - reason (short, business-friendly)
    - suggested_action (clear and operational)
    - confidence
    - signals (array of short strings)
    """
    
async def analyze_with_llm(ticket: Ticket) -> AIAnalysis:
    raw = openai_chat(
        system=SYSTEM_PROMPT,
        user=_build_user_prompt(ticket),
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"Invalid JSON from LLM: {raw[:200]}")
        data = json.loads(raw[start:end+1])

    analysis = AIAnalysis(**data)

    # Safety clamps
    analysis.risk_score = max(0, min(analysis.risk_score, 100))
    analysis.confidence = max(0, min(analysis.confidence, 100))
    if analysis.risk_label not in ("LOW", "MEDIUM", "HIGH"):
        raise ValueError("Invalid risk_label")

    return analysis