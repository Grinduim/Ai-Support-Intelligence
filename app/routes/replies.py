from fastapi import APIRouter
from app.models import ReplySuggestionRequest, ReplySuggestionResponse
from app.services.reply_suggester import suggest_reply_with_llm

router = APIRouter()

@router.post(
    "/suggest-reply",
    response_model=ReplySuggestionResponse,
    summary="Suggest a customer support reply",
    description="Returns an AI-generated reply suggestion, confidence score, and metadata for a support ticket."
)
async def suggest_reply_endpoint(payload: ReplySuggestionRequest):
    """
    Suggest a customer support reply using LLM based on ticket details.

    Args:
        payload (ReplySuggestionRequest): Ticket details and preferences for reply.

    Returns:
        ReplySuggestionResponse: Suggested reply, confidence score, and additional metadata.

    Example Request:
        {
            "ticket_id": "TICKET-001",
            "customer": "Acme Corp",
            "channel": "email",
            "last_message": "Customer message...",
            "conversation_summary": "Summary...",
            "risk_label": "HIGH",
            "company_tone": "formal",
            "language": "en-US"
        }

    Example Response:
        {
            "ticket_id": "TICKET-001",
            "suggested_reply": "Thank you for your patience. We're escalating your issue.",
            "confidence": 92,
            "language": "en-US",
            "subject": "Escalation Notice",
            "next_steps": ["Assign to manager", "Follow up in 2 hours"],
            "do_not_say": ["We can't help", "Wait longer"]
        }
    """
    try:
        response = await suggest_reply_with_llm(payload)
        return response
    except Exception as e:
        # Fallback safe reply
        return ReplySuggestionResponse(
            ticket_id=payload.ticket_id,
            suggested_reply="Thank you for reaching out. We will get back to you shortly.",
            confidence=0
        )
