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


class ReplySuggestionResponse(BaseModel):
    ticket_id: str
    suggested_reply: str
    confidence: int = Field(..., ge=0, le=100)  # 0..100
    language: str = "en-US"  # pt-BR | en-US
    subject: str = ""
    next_steps: List[str] = []
    do_not_say: List[str] = []
