from app.models import TicketAnalyzeRequest, TicketAnalyzeResponse, TicketResult

RISK_KEYWORDS = [
    "procon",
    "processo",
    "cancelar",
    "reclame aqui",
    "não renovo",
    "advogado"
]

def analyze_ticket(payload: TicketAnalyzeRequest) -> TicketAnalyzeResponse:
    results = []

    for ticket in payload.tickets:
        risk_score = 0
        reasons = []

        text = f"{ticket.last_message.lower()} {ticket.conversation_summary.lower()}"

        for keyword in RISK_KEYWORDS:
            if keyword in text:
                risk_score += 25
                reasons.append(f"Keyword detected: {keyword}")

        if ticket.sla_hours_open > 24:
            risk_score += 20
            reasons.append("SLA open for more than 24 hours")

        risk_score = min(risk_score, 100)

        if risk_score >= 70:
            label = "HIGH"
            action = "Escalate to senior support and respond immediately."
        elif risk_score >= 40:
            label = "MEDIUM"
            action = "Prioritize response and monitor closely."
        else:
            label = "LOW"
            action = "Standard response flow."

        results.append(
            TicketResult(
                id=ticket.id,
                risk_score=risk_score,
                risk_label=label,
                reason="; ".join(reasons) or "No critical risk detected.",
                suggested_action=action
            )
        )

    return TicketAnalyzeResponse(results=results)
