from fastapi import APIRouter
from app.models import ReplySuggestionRequest, ReplySuggestionResponse
from app.services.reply_suggester import suggest_reply_with_llm

router = APIRouter()

@router.post("/suggest-reply", response_model=ReplySuggestionResponse)
async def suggest_reply_endpoint(payload: ReplySuggestionRequest):
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
        