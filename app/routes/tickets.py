from fastapi import APIRouter
from app.models import TicketAnalyzeRequest, TicketAnalyzeResponse
from app.services.risk_orchestrator import analyze_one_ticket

router = APIRouter()

@router.post(
    "/analyze",
    response_model=TicketAnalyzeResponse,
    summary="Analyze support tickets for risk classification.",
    description="Returns risk label, score, reason, and suggested action for each ticket."
)
async def analyze_ticket_endpoint(payload: TicketAnalyzeRequest):
    """
    Analyze support tickets for risk classification.

    Args:
        payload (TicketAnalyzeRequest): List of tickets to analyze.

    Returns:
        TicketAnalyzeResponse: List of results with risk label, score, reason, and suggested action.

    Example Request:
        {
            "tickets": [
                {
                    "id": "TICKET-001",
                    "customer": "Acme Corp",
                    "channel": "email",
                    "last_message": "Customer message...",
                    "conversation_summary": "Summary...",
                    "sla_hours_open": 12,
                    "language": "en-US"
                }
            ]
        }

    Example Response:
        {
            "results": [
                {
                    "id": "TICKET-001",
                    "risk_score": 85,
                    "risk_label": "HIGH",
                    "reason": "Customer threatened to escalate.",
                    "suggested_action": "Prioritize and escalate to manager.",
                    "debug_signals": ["escalation", "negative_sentiment"],
                    "risk_breakdown": {"escalation": 50, "sentiment": 35},
                    "language": "en-US"
                }
            ]
        }
    """
    results = []
    for t in payload.tickets:
        results.append(await analyze_one_ticket(t))
    return TicketAnalyzeResponse(results=results)
