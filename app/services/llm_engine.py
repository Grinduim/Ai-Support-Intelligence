import json
from app.models import Ticket, AIAnalysis, RiskLabel
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
- Respond ONLY in the specified language. No other languages.
"""

def _build_user_prompt(ticket: Ticket) -> str:
    return f"""
    Analyze this support context (respond in {ticket.language} only):

    last_message: "{ticket.last_message}"
    conversation_summary: "{ticket.conversation_summary}"
    sla_hours_open: {ticket.sla_hours_open}
    channel: "{ticket.channel}"
    language: {ticket.language}

    Return JSON with:
    - risk_score
    - risk_label
    - reason (short, business-friendly, in {ticket.language})
    - suggested_action (clear and operational, in {ticket.language})
    - confidence
    - signals (array of short strings, in {ticket.language})
    """
    
async def analyze_with_llm(ticket: Ticket) -> AIAnalysis:
    raw = await openai_chat(
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
    
    # Validate and convert risk_label to enum if needed
    if isinstance(analysis.risk_label, str):
        try:
            analysis.risk_label = RiskLabel(analysis.risk_label)
        except ValueError:
            raise ValueError(f"Invalid risk_label: {analysis.risk_label}. Must be one of: LOW, MEDIUM, HIGH")

    return analysis