from app.models import ReplySuggestionRequest, ReplySuggestionResponse
from app.services.openai_client import openai_chat
import json
from pydantic import ValidationError

SYSTEM_PROMPT = """You are a customer support assistant that suggests replies to support tickets. 
Your responses must be in JSON format only, following this schema:
{
    "reply_text": "string",               // The full text of the suggested reply (in the specified language)
    "subject": "string (optional)",       // Suggested email subject, if applicable
    "next_steps": ["string"],             // List of recommended next steps for the support agent
    "do_not_say": ["string"],             // List of phrases or topics to avoid in the reply
    "confidence": integer (0 to 100)      // Confidence level in the suggested reply
}
Adhere to the following guardrails:
1) ALWAYS respond ONLY in the specified language. No other languages.
2) If the ticket's risk_label is "HIGH", ensure the reply:
    - Acknowledges the customer's issue empathetically.
    - Provides a clear action plan to resolve the issue.
    - Gives a short timeline for resolution.
    - Offers an escalation path if needed.      
3) Never promise refunds unless the customer explicitly requests one.
4) Avoid blaming the customer under any circumstances.
"""

async def suggest_reply_with_llm(request: ReplySuggestionRequest) -> ReplySuggestionResponse:
    """
    Generate a customer support reply suggestion using LLM.
    
    Args:
        request (ReplySuggestionRequest): The ticket details and preferences.
        
    Returns:
        ReplySuggestionResponse: Suggested reply in the specified language with confidence score.
        
    Raises:
        Exception: If LLM response cannot be parsed as valid JSON.
    """
    user_prompt = f"""
    Generate a customer support reply based on the following ticket details.
    RESPOND ONLY IN {request.language}:

    Ticket ID: {request.ticket_id}
    Customer: {request.customer}
    Channel: {request.channel}
    Last Message: {request.last_message}
    Conversation Summary: {request.conversation_summary}
    Risk Label: {request.risk_label}
    Company Tone: {request.company_tone}
    Language: {request.language}
    
    Provide the response strictly in the specified JSON format and in {request.language} only.
    """
    
    response_text = await openai_chat(
        system=SYSTEM_PROMPT,
        user=user_prompt,
    )
    
    try:
        response_json = json.loads(response_text)
        confidence = max(0, min(response_json.get("confidence", 0), 100))
        reply_text = response_json.get("reply_text", "Thank you for reaching out. We will get back to you shortly.")
        return ReplySuggestionResponse(
            ticket_id=request.ticket_id,
            suggested_reply=reply_text,
            confidence=confidence,
            language=request.language,
            subject=response_json.get("subject", ""),
            next_steps=response_json.get("next_steps", []),
            do_not_say=response_json.get("do_not_say", []),
        )
    except (json.JSONDecodeError, ValidationError, KeyError) as e:
        raise Exception(f"Failed to parse LLM response: {str(e)}")