from pydantic import BaseModel, Field
from typing import Dict, List
from enum import Enum


class RiskLabel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Ticket(BaseModel):
    id: str
    customer: str
    channel: str
    last_message: str = Field(..., max_length=255)
    conversation_summary: str = Field(..., max_length=255)
    sla_hours_open: int
    language: str = "en-US"  # pt-BR | en-US
    
class TicketAnalyzeRequest(BaseModel):
    tickets: List[Ticket]

    class Config:
        json_schema_extra = {
            "example": {
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
        }

class TicketResult(BaseModel):
    id: str
    risk_score: int
    risk_label: RiskLabel
    reason: str
    suggested_action: str
    debug_signals: List[str]
    risk_breakdown: Dict[str, int]
    language: str = "en-US"  # pt-BR | en-US

class TicketAnalyzeResponse(BaseModel):
    results: List[TicketResult]

    class Config:
        json_schema_extra = {
            "example": {
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
        }
    

class AIAnalysis(BaseModel):
    risk_score: int
    risk_label: RiskLabel
    reason: str
    suggested_action: str
    confidence: int = Field(..., ge=0, le=100)  # 0..100
    signals: List[str] = []
    
    
class ReplySuggestionRequest(BaseModel):
    ticket_id: str
    customer: str
    channel: str
    last_message: str = Field(..., max_length=255)
    conversation_summary: str = Field(..., max_length=255)
    risk_label: RiskLabel
    company_tone: str  # formal | friendly | technical
    language: str  # pt-BR | en-US

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TICKET-001",
                "customer": "Acme Corp",
                "channel": "email",
                "last_message": "Customer message...",
                "conversation_summary": "Summary...",
                "risk_label": "HIGH",
                "company_tone": "formal",
                "language": "en-US"
            }
        }

class ReplySuggestionResponse(BaseModel):
    ticket_id: str
    suggested_reply: str
    confidence: int = Field(..., ge=0, le=100)  # 0..100
    language: str = "en-US"  # pt-BR | en-US
    subject: str = ""
    next_steps: List[str] = []
    do_not_say: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TICKET-001",
                "suggested_reply": "Thank you for your patience. We're escalating your issue.",
                "confidence": 92,
                "language": "en-US",
                "subject": "Escalation Notice",
                "next_steps": ["Assign to manager", "Follow up in 2 hours"],
                "do_not_say": ["We can't help", "Wait longer"]
            }
        }
