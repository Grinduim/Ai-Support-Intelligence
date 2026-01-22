from app.models import Ticket, TicketResult, TicketResult

ESCALATION_KEYWORDS = ["procon", "reclame aqui", "processo", "advogado"]
CHURN_KEYWORDS = ["cancelar", "não renovo", "nao renovo", "vou sair", "encerrar", "cancelamento"]
NEGATIVE_WORDS = ["péssimo", "horrível", "ridículo", "absurdo", "irritado", "raiva", "insatisfeito"]

def _contains_any(text: str, keywords: list[str]) -> list[str]:
    hits = []
    for k in keywords:
        if k in text:
            hits.append(k)
    return hits


def analyze_ticket(ticket: Ticket) -> TicketResult:

    debug_signals: list[str] = []
    breakdown = {"escalation": 0, "churn": 0, "sla": 0, "sentiment": 0}

    text = f"{ticket.last_message.lower()} {ticket.conversation_summary.lower()}"

    escalation_hits = _contains_any(text, ESCALATION_KEYWORDS)
    if escalation_hits:
        breakdown["escalation"] = 40
        debug_signals.append(f"escalation: {', '.join(escalation_hits)}")

    # 2) Churn intent
    churn_hits = _contains_any(text, CHURN_KEYWORDS)
    if churn_hits:
        breakdown["churn"] = 35
        debug_signals.append(f"churn: {', '.join(churn_hits)}")

    # 3) Sentiment (heuristic)
    negative_hits = _contains_any(text, NEGATIVE_WORDS)
    if negative_hits:
        breakdown["sentiment"] = 15
        debug_signals.append(f"sentiment: {', '.join(negative_hits)}")

    # 4) SLA
    if ticket.sla_hours_open >= 48:
        breakdown["sla"] = 35
        debug_signals.append("sla: >=48h")
    elif ticket.sla_hours_open >= 24:
        breakdown["sla"] = 25
        debug_signals.append("sla: >=24h")
    elif ticket.sla_hours_open >= 12:
        breakdown["sla"] = 15
        debug_signals.append("sla: >=12h")

    risk_score = min(sum(breakdown.values()), 100)

    override_high = (breakdown["escalation"] > 0 and breakdown["sla"] >= 25)

    # Label
    if risk_score >= 70 or override_high:
        risk_label = "HIGH"
        suggested_action = "Escalate to senior support and respond within 30 minutes with a clear plan."
    elif risk_score >= 35:
        risk_label = "MEDIUM"
        suggested_action = "Reply today with a concrete next step and monitor for escalation or churn."
    else:
        risk_label = "LOW"
        suggested_action = "Standard response flow."
        
    reason_parts = []
    if breakdown["escalation"] > 0:
        reason_parts.append("customer threatened escalation")
    if breakdown["churn"] > 0:
        reason_parts.append("customer signaled cancellation intent")
    if breakdown["sla"] >= 25:
        reason_parts.append(f"ticket open for {ticket.sla_hours_open}h")
    elif breakdown["sla"] > 0:
        reason_parts.append("ticket aging")
    if breakdown["sentiment"] > 0:
        reason_parts.append("negative tone")

    reason = " and ".join(reason_parts).capitalize() + "." if reason_parts else "No critical risk detected."

    results = TicketResult(
            id=ticket.id,
            risk_score=risk_score,
            risk_label=risk_label,
            reason=reason,
            suggested_action=suggested_action,
            risk_breakdown=breakdown,
            debug_signals=debug_signals,
        )

    return results
